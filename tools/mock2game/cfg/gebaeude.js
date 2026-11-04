// Gebäudefenster (Basislager-Gebaeude): Rahmen, Knöpfe, Kopf- und Reiterleiste bleiben, alles was je
// Gebäude wechselt (Bild, Untertitel, Wertezeile, Füllung des Lagers, Text, Inhalt des großen Knopfs)
// zeichnet das Spiel selbst. lager=false: ohne Lager-Zeile (Verstärker, Bauplätze).
window.m2gStrip = function (lager) {
  const q = (s) => document.querySelector('#dc-root ' + s);
  const panel = q('div[style*="top: 120px; bottom: 120px"]');
  panel.querySelector('div[style*="width: 210px; height: 170px"]').innerHTML = '';
  panel.querySelector('div[style*="top: 48px"]').remove();
  panel.querySelector('div[style*="top: 266px; height: 40px"]').innerHTML = '';
  panel.querySelector('div[style*="top: 388px"]').remove();
  const bar = panel.querySelector('div[style*="right: 132px; top: 338px"]');
  bar.innerHTML = '';
  const collect = [...panel.querySelectorAll('a')].find(a => a.textContent.trim() == 'ABHOLEN');
  collect.setAttribute('data-on', 'collect'); collect.removeAttribute('href');
  const big = q('a[style*="top: 636px"]');
  big.innerHTML = ''; big.setAttribute('data-on', 'main'); big.removeAttribute('href');
  if (!lager) { bar.remove(); collect.remove(); panel.querySelector('div[style*="top: 318px"]').remove(); }
};
