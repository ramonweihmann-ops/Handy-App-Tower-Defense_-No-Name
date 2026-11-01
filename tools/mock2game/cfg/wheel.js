// Glücksrad (Artboard-zqpq.dc.html): Felder an die echten Gewinne anpassen, Rad-Teile für das Spiel
// vorbereiten. Feld k liegt k × 45° im Uhrzeigersinn ab oben; Zuordnung zu MetaData.WHEEL steht in
// scripts/ui/screens/board_artboard-zqpq.gd (FIELD_TO_WHEEL).
window.m2g = (() => {
  // Seite durchsichtig, damit die Einzelbilder (Rad, Zeiger, Symbole) keinen weißen Rand haben
  document.documentElement.style.background = 'transparent';
  document.body.style.background = 'transparent';
  const field = (k) => document.querySelector(`#dc-root g[transform="rotate(${k * 45} 150 150)"]`);
  const BOLT = '<g transform="translate(-18.4 -19.2) scale(1.6)"><path d="M13 2 4 14h7l-1 8 9-12h-7z" fill="#7dff8a" stroke="#1d6b2a" stroke-width="1.5" stroke-linejoin="round"></path></g>';
  const wheelParts = () => [
    document.querySelector('#dc-root div[style*="width: 300px; height: 300px; transform"]'),
    document.querySelector('#dc-root svg[width="340"][style*="pointer-events"]'),
    document.querySelector('#dc-root svg[width="56"][height="70"]'),
  ];
  return {
    // Felder wie die echten Gewinne: 500 Gold · 10 Energie · 3 Heldenkarten · 100 Gold ·
    // 5 Edelsteine · 1 Talentstern · 250 Gold · 20 Edelsteine
    fields() {
      field(1).querySelector('g[transform="translate(150 58)"]').innerHTML = BOLT;
      field(2).querySelector('text').textContent = '×3';
      field(3).querySelector('text').textContent = '100';
      field(5).querySelector('text').textContent = '×1';
      const svg = document.querySelector('#dc-root svg[aria-label^="Glücksrad"]');
      svg.setAttribute('aria-label', 'Glücksrad mit 8 Feldern: 500 Gold, 10 Energie, 3 Heldenkarten, 100 Gold, 5 Edelsteine, 1 Talentstern, 250 Gold, 20 Edelsteine');
    },
    // Rad, Nabe und Zeiger zeichnet das Spiel selbst (Bilder aus dem Grundzustand)
    hideWheel() {
      for (const e of wheelParts()) e.style.visibility = 'hidden';
    },
    hidePanel() {
      const p = document.querySelector('#dc-root [role="status"]');
      if (p) p.style.visibility = 'hidden';
    },
    // Popup „Gewonnen“: nur das Feld mit Strahlen; Symbol für jede Gewinnart zum Austauschen
    win() {
      const done = document.querySelector('#dc-root a[href="Main.dc.html"]:not([aria-label])');
      done.parentElement.remove();
      const coin = document.querySelector('#dc-root [role="status"] svg[width="64"]');
      const box = document.createElement('div');
      box.style.cssText = 'position: relative; width: 64px; height: 54px';
      coin.replaceWith(box);
      const icon = (kind, inner) => {
        const s = coin.cloneNode(true);
        s.setAttribute('data-icon', kind);
        s.style.cssText = 'position: absolute; left: 0; top: 0';
        if (inner !== null) s.querySelector('g').innerHTML = inner;
        box.appendChild(s);
      };
      icon('gold', null);
      icon('gems', field(1).querySelector('g[transform="translate(150 58)"] > g').innerHTML);
      icon('energy', BOLT);
      icon('stars', field(5).querySelector('g[transform="translate(150 58)"] > g').innerHTML);
      const hero = document.querySelector('#dc-root div[style*="left: 225px; top: 127px"]').cloneNode(true);
      hero.setAttribute('data-icon', 'cards');
      hero.style.left = '15px'; hero.style.top = '2px'; hero.style.transform = 'none';
      box.appendChild(hero);
      return Promise.all(Array.from(document.images).map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
    },
  };
})();
