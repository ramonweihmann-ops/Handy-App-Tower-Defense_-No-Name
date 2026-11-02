// Tägliche Belohnung: Tageskarten in einheitliche Bausteine verwandeln, damit das Spiel jede Karte
// in jedem Zustand (erledigt, heute, gesperrt) einzeln zeichnen kann.
window.tbPrep = function (mode) {
  document.querySelectorAll('[style*="animation"]').forEach(e => { e.style.animation = 'none'; });
  const grid = [...document.querySelectorAll('#dc-root div')].find(d => d.style.gridTemplateColumns && d.style.gridTemplateColumns.includes('repeat(3'));
  if (!grid) return;
  let kids = [...grid.children];
  // „Heute“-Karte steckt in einem Knopf: Knopf auflösen
  kids.forEach((k, i) => { if (k.tagName === 'BUTTON') { const inner = k.firstElementChild; grid.replaceChild(inner, k); kids[i] = inner; } });
  const amount = (el) => el.querySelector('span[style*="background: #6a4320"]');
  const iconOf = (el) => el.querySelector('div[style*="width: 50px; height: 44px"]');
  const lockedT = kids.find(k => k.textContent.includes('TAG 4'));
  const todayT = kids.find(k => k.textContent.includes('HEUTE'));
  if (mode !== 'main' && lockedT && todayT) {
    const srcIcon = [kids[4], kids[5], todayT, kids[3], kids[4], kids[5]].map(iconOf);
    const amounts = ['×150', '×5', '×10', '×5', '×300', '×10'];
    for (let i = 0; i < 6; i++) {
      const tpl = (mode === 'locked' ? lockedT : todayT).cloneNode(true);
      const ic = iconOf(tpl); if (ic && srcIcon[i]) ic.replaceWith(srcIcon[i].cloneNode(true));
      const a = amount(tpl); if (a) a.textContent = amounts[i];
      const head = tpl.firstElementChild; if (head) head.textContent = mode === 'locked' ? 'TAG ' + (i + 1) : 'HEUTE';
      grid.replaceChild(tpl, grid.children[i]);
    }
    kids = [...grid.children];
  }
  kids.forEach((k, i) => k.setAttribute('data-tb-day', String(i + 1)));
  const t7 = [...document.querySelectorAll('#dc-root div')].find(d => d.style.borderRadius === '14px' && d.textContent.trim().startsWith('TAG 7'));
  if (t7) {
    t7.setAttribute('data-tb-t7', '1');
    if (mode === 'today') {
      t7.style.boxShadow = '0 3px 0 #23802a, 0 0 18px rgba(140,240,106,0.9)';
      t7.style.outline = '2.5px solid #8cf06a';
      const head = t7.firstElementChild; if (head) { head.style.background = 'linear-gradient(180deg, #8cf06a, #3fbf3a)'; head.textContent = 'HEUTE · GROSSE BELOHNUNG'; }
      const lock = t7.querySelector('span[style*="position: absolute; right: 6px"]'); if (lock) lock.remove();
    }
  }
};
