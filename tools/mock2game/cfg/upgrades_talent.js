// Talente (Upgrades-Talente): vor dem Zerlegen vorbereiten.
// - Reiterleiste zeigt auf die Reiter im Spiel (#shop, #helden …) wie im Hauptbildschirm
// - Symbole für alle Talente des Spiels (MetaData.TALENTS, Reihenfolge gleich). Schnelllader und
//   Sanitätskoffer stammen aus dem Mockup, die übrigen sind im selben Stil gezeichnet.
(() => {
  const root = document.getElementById('dc-root');
  const NAV = { Shop: '#shop', Helden: '#helden', Kampf: '#kampf', Upgrades: '#upgrades', Basis: '#basis' };
  root.querySelectorAll('nav a').forEach(a => { const t = a.textContent.trim(); if (NAV[t]) a.setAttribute('href', NAV[t]); });

  const cards = Array.from(root.querySelectorAll('div[style*="#5fe07a, #2fa84a"]'));
  cards.forEach(c => c.children[1].classList.add('m2g-tslot'));
  const area = cards[0].parentElement.parentElement;
  const SPARK = '<path d="M20 2.5v3.4M18.3 4.2h3.4" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity="0.6"/>';
  const NEW = {
    kopfgeld: '<defs><radialGradient id="tkc" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#fffbd0"/><stop offset="0.45" stop-color="#ffd23a"/><stop offset="1" stop-color="#b87400"/></radialGradient></defs>'
      + '<ellipse cx="8" cy="20.2" rx="6" ry="2.6" fill="#b87400" stroke="#7a4a00" stroke-width="0.8"/><ellipse cx="8" cy="19" rx="6" ry="2.6" fill="#ffd23a" stroke="#a86a00" stroke-width="0.8"/>'
      + '<ellipse cx="8" cy="16.8" rx="6" ry="2.6" fill="#b87400" stroke="#7a4a00" stroke-width="0.8"/><ellipse cx="8" cy="15.6" rx="6" ry="2.6" fill="#ffe27a" stroke="#a86a00" stroke-width="0.8"/>'
      + '<ellipse cx="8" cy="13.4" rx="6" ry="2.6" fill="#b87400" stroke="#7a4a00" stroke-width="0.8"/><ellipse cx="8" cy="12.2" rx="6" ry="2.6" fill="#ffd23a" stroke="#a86a00" stroke-width="0.8"/>'
      + '<circle cx="15.5" cy="14" r="6.8" fill="url(#tkc)" stroke="#a86a00" stroke-width="1"/><circle cx="15.5" cy="14" r="4.2" fill="none" stroke="#fff3b0" stroke-width="1"/>'
      + '<path d="M11.6 11.2a4.6 4.6 0 0 1 2.6-2" stroke="#fff" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.9"/>' + SPARK,
    scharfschuetze: '<circle cx="12" cy="13" r="8.2" fill="#2a2450" stroke="#ff6a5a" stroke-width="2"/><circle cx="12" cy="13" r="3.8" fill="none" stroke="#ff6a5a" stroke-width="1.8"/>'
      + '<path d="M12 2.8v5M12 18.2v5M1.8 13h5M17.2 13h5" stroke="#ffe9c2" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="13" r="1.5" fill="#ffd34d"/>'
      + '<path d="M6.6 9.6a6.6 6.6 0 0 1 2.6-2.4" stroke="#fff" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.8"/>' + SPARK,
    munitionslager: '<defs><linearGradient id="tmb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9a0"/><stop offset="1" stop-color="#c8820c"/></linearGradient></defs>'
      + [7.5, 12, 16.5].map(x => '<rect x="' + (x - 1.8) + '" y="5" width="3.6" height="9" rx="0.6" fill="url(#tmb)" stroke="#7a4a00" stroke-width="0.7"/><path d="M' + (x - 1.8) + ' 5.4Q' + x + ' 0.8 ' + (x + 1.8) + ' 5.4z" fill="#e07a3a" stroke="#7a2a00" stroke-width="0.7"/>').join('')
      + '<rect x="3" y="12" width="18" height="11" rx="2" fill="#4a5a88"/><rect x="3" y="11" width="18" height="11" rx="2" fill="#2f8d3e" stroke="#123d18" stroke-width="1"/>'
      + '<rect x="3.5" y="14" width="17" height="2" fill="#1d6b2a"/><rect x="9" y="16.6" width="6" height="3.4" rx="0.8" fill="#ffd34d" stroke="#7a4a00" stroke-width="0.6"/>'
      + '<path d="M5 12.8h5" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity="0.6"/>' + SPARK,
    feuerkraft: '<defs><linearGradient id="tff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe27a"/><stop offset="0.5" stop-color="#ff7a3d"/><stop offset="1" stop-color="#d0281a"/></linearGradient></defs>'
      + '<path d="M12 1.8c3.2 4.2 7 6.5 7 12a7 7 0 0 1-14 0c0-3.4 2.2-5.6 3.4-7.8 1.1 2.2 2.2 3.3 3.4 3.3 0-2.3-1-4.6.2-7.5z" fill="url(#tff)" stroke="#8a1a0a" stroke-width="1"/>'
      + '<path d="M12 11.4c1.6 2 3.2 3.2 3.2 5.6a3.2 3.2 0 0 1-6.4 0c0-1.6 1-2.6 1.6-3.6.5 1 1 1.4 1.6 1.4 0-1.1-.4-2.1 0-3.4z" fill="#fff3b0"/>'
      + '<path d="M7.4 13.4a5.2 5.2 0 0 1 1.5-3.6" stroke="#fff" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.7"/>' + SPARK,
    glueckspilz: '<defs><radialGradient id="tgc" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#ffb0a0"/><stop offset="0.5" stop-color="#ff3b4a"/><stop offset="1" stop-color="#8a0a1a"/></radialGradient></defs>'
      + '<path d="M9 13.5h6l1 7.4a1.5 1.5 0 0 1-1.5 1.6h-5A1.5 1.5 0 0 1 8 20.9z" fill="#fff3e0" stroke="#a8805a" stroke-width="1"/>'
      + '<path d="M2.5 13.8C2.5 7.3 7 3.2 12 3.2s9.5 4.1 9.5 10.6c0 .8-.6 1.3-1.4 1.3H3.9c-.8 0-1.4-.5-1.4-1.3z" fill="url(#tgc)" stroke="#8a0a1a" stroke-width="1"/>'
      + '<circle cx="8" cy="9.4" r="1.8" fill="#fff"/><circle cx="13.6" cy="6.8" r="1.4" fill="#fff"/><circle cx="16.8" cy="11.2" r="1.6" fill="#fff"/><circle cx="11.4" cy="12.4" r="1" fill="#fff"/>'
      + '<path d="M5 10a7 7 0 0 1 2.6-3.8" stroke="#fff" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.7"/>' + SPARK,
    lernfreude: '<defs><linearGradient id="tlf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8fa8ff"/><stop offset="0.5" stop-color="#3a4fd0"/><stop offset="1" stop-color="#1a2268"/></linearGradient></defs>'
      + '<path d="M1.8 8l10.2 2 10.2-2v13.4L12 23.4 1.8 21.4z" fill="url(#tlf)" stroke="#0a1450" stroke-width="1"/>'
      + '<path d="M3.4 6.8c3-.6 6 0 8.6 1.7v12.8c-2.6-1.5-5.6-2-8.6-1.5z" fill="#fff" stroke="#5a6a90" stroke-width="0.8"/>'
      + '<path d="M20.6 6.8c-3-.6-6 0-8.6 1.7v12.8c2.6-1.5 5.6-2 8.6-1.5z" fill="#dbe7ff" stroke="#5a6a90" stroke-width="0.8"/>'
      + '<path d="M5.4 11c1.8-.2 3.5.1 5 .8M5.4 14c1.8-.2 3.5.1 5 .8M5.4 17c1.8-.2 3.5.1 5 .8" stroke="#8fa8c8" stroke-width="0.9" stroke-linecap="round" fill="none"/>'
      + '<path d="M16.2 10l1 2.1 2.3.3-1.7 1.6.4 2.3-2-1.1-2 1.1.4-2.3-1.7-1.6 2.3-.3z" fill="#ffd23a" stroke="#a86a00" stroke-width="0.7"/>' + SPARK,
  };
  const make = inner => {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    for (const [a, v] of Object.entries({ width: '52', height: '52', viewBox: '0 0 24 24', 'aria-hidden': 'true' })) s.setAttribute(a, v);
    s.setAttribute('style', 'overflow: visible; filter: drop-shadow(0 3px 3px rgba(0,0,0,0.5))');
    s.innerHTML = inner;
    return s;
  };
  const svgs = [cards[0].children[1].querySelector('svg').cloneNode(true), cards[1].children[1].querySelector('svg').cloneNode(true)]
    .concat(['kopfgeld', 'scharfschuetze', 'munitionslager', 'feuerkraft', 'glueckspilz', 'lernfreude'].map(k => make(NEW[k])));
  svgs.forEach((s, k) => {
    const d = document.createElement('div');
    d.className = 'm2g-tic';
    d.style.cssText = 'position: absolute; width: 52px; height: 52px; left: ' + (14 + (k % 4) * 90) + 'px; top: ' + (150 + Math.floor(k / 4) * 90) + 'px';
    d.appendChild(s);
    area.appendChild(d);
  });
})()
