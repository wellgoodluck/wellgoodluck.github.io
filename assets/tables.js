// Article tables wider than the screen (Nov 5): the table fades at an edge with more to scroll to, a line above it
// says the table continues, and the scroll box takes keyboard focus so it can be scrolled without a pointer.
// Tables that fit get none of this. Loaded only on article pages that have a table.
(function () {
  'use strict';
  document.querySelectorAll('.table-scroll').forEach(w => {
    const hint = document.createElement('p');
    hint.className = 'table-hint'; hint.textContent = 'The table continues to the right →'; hint.hidden = true;
    w.parentNode.insertBefore(hint, w);
    function update() {
      const max = w.scrollWidth - w.clientWidth, wide = max > 2;
      hint.hidden = !wide;
      w.classList.toggle('fade-r', wide && w.scrollLeft < max - 2);
      w.classList.toggle('fade-l', wide && w.scrollLeft > 2);
      if (wide) { w.tabIndex = 0; w.setAttribute('role', 'region'); w.setAttribute('aria-label', 'Table, scrolls sideways'); }
      else { w.removeAttribute('tabindex'); w.removeAttribute('role'); w.removeAttribute('aria-label'); }
    }
    w.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });
})();
