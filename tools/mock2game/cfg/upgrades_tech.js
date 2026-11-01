// Tech-Baum (Artboard-wpji): vor dem Zerlegen vorbereiten.
// - Reiterleiste zeigt auf die Reiter im Spiel (#shop, #helden …) wie im Hauptbildschirm
// - Knoten sind im Spiel keine festen Knöpfe (der Baum scrollt): aus <button> wird <div>
// - Symbole für alle Knoten des Spiels (MetaData.TECH, Reihenfolge gleich), je farbig und grau
(() => {
  const root = document.getElementById('dc-root');
  const NAV = { Shop: '#shop', Helden: '#helden', Kampf: '#kampf', Upgrades: '#upgrades', Basis: '#basis' };
  root.querySelectorAll('nav a').forEach(a => { const t = a.textContent.trim(); if (NAV[t]) a.setAttribute('href', NAV[t]); });

  const nodes = Array.from(root.querySelectorAll('button[aria-label$="Beschreibung und Preis"]'));
  const divs = nodes.map(b => {
    const d = document.createElement('div');
    for (const a of Array.from(b.attributes)) if (a.name !== 'data-on' && a.name !== 'onclick') d.setAttribute(a.name, a.value);
    d.classList.add('m2g-node');
    while (b.firstChild) d.appendChild(b.firstChild);
    b.replaceWith(d);
    return d;
  });
  divs.forEach(d => d.firstElementChild.classList.add('m2g-nic'));

  const NS = 'http://www.w3.org/2000/svg';
  const svgOf = k => divs[k].firstElementChild.querySelector('svg');
  // Stufenzeichen wie beim Schildgenerator („I“, „II“) an ein Symbol hängen
  const mark = (k, txt, x) => {
    const c = svgOf(k).cloneNode(true);
    let t = c.querySelector('text');
    if (!t) {
      t = document.createElementNS(NS, 'text');
      for (const [a, v] of Object.entries({ y: '21', 'font-family': 'Fredoka, sans-serif', 'font-weight': '700', 'font-size': '7', fill: '#fff', stroke: '#1d4aa8', 'stroke-width': '1.5', 'paint-order': 'stroke' })) t.setAttribute(a, v);
      c.appendChild(t);
    }
    t.setAttribute('x', String(x));
    t.textContent = txt;
    return c;
  };
  // Waffenkammer: zwei gekreuzte Klingen im Stil der übrigen Symbole
  const swords = () => {
    const c = svgOf(0).cloneNode(false);
    c.innerHTML = '<path d="M5 3l11 11" stroke="#1d4aa8" stroke-width="4" stroke-linecap="round"/><path d="M19 3L8 14" stroke="#1d4aa8" stroke-width="4" stroke-linecap="round"/>'
      + '<path d="M5 3l11 11" stroke="#e6ecff" stroke-width="2.2" stroke-linecap="round"/><path d="M19 3L8 14" stroke="#e6ecff" stroke-width="2.2" stroke-linecap="round"/>'
      + '<path d="M12.5 16.5l5-5M6.5 11.5l5 5" stroke="#ffd34d" stroke-width="2.4" stroke-linecap="round"/>'
      + '<path d="M16 16l3.5 3.5M8 16l-3.5 3.5" stroke="#a8641a" stroke-width="2.6" stroke-linecap="round"/>'
      + '<circle cx="20" cy="20" r="1.6" fill="#ffd34d" stroke="#a86a00" stroke-width="0.8"/><circle cx="4" cy="20" r="1.6" fill="#ffd34d" stroke="#a86a00" stroke-width="0.8"/>';
    return c;
  };
  const icons = [svgOf(0), svgOf(1), svgOf(2), svgOf(3), svgOf(4), svgOf(5), mark(2, 'III', 17), mark(1, 'II', 18), swords(), mark(3, 'II', 18)];
  const box = divs[0].parentElement;
  icons.forEach((s, k) => {
    for (const gray of [false, true]) {
      const d = document.createElement('div');
      d.className = gray ? 'm2g-gic' : 'm2g-ic';
      d.style.cssText = 'position: absolute; width: 54px; height: 54px; display: grid; place-items: center; left: ' + (8 + (k % 5) * 76) + 'px; top: ' + (300 + Math.floor(k / 5) * 70 + (gray ? 150 : 0)) + 'px;'
        + (gray ? ' filter: grayscale(0.85) brightness(0.8);' : '');
      d.appendChild(s.cloneNode(true));
      box.appendChild(d);
    }
  });
})()
