// Shop · Event (Shop-Event-Neu.dc.html): eine Fassung je Wochenthema (MetaData.EVENT_THEMES). Banner-Farben,
// Boss-Porträt, Titel, Beschreibung, Punktezeile und „Nächste Woche“ werden hier umgestellt; Restzeit, Punkte,
// Balken und die zehn Belohnungskarten zeichnet das Spiel selbst (live).
window.m2gEvent = (() => {
  const T = {
    schleimflut: {title: 'Schleimflut', boss: 'd2d681b6db97f4b0845e41067fb7d0ea', bg: '#4fd17a 0%, #1f8a5a 45%, #18406a 100%',
      border: 'rgba(180,255,190,0.5)', glow: 'rgba(170,255,120,0.6) 55%, rgba(120,220,60,0) 72%', ring: 'rgba(140,255,120,0.8)', shadow: '#0f4a2a',
      desc: 'Besiege Schleim-Gegner, fülle die Leiste und hol dir die Event-Truhe!', foes: 'Schleim-Gegner besiegt',
      chip: '#7dff8a, #2f9a3f'},
    frostwoche: {title: 'Frostwoche', boss: 'c146c9df73de27321e258986fdf6b043', bg: '#8fd8ff 0%, #2a7ab0 45%, #18306a 100%',
      border: 'rgba(190,235,255,0.55)', glow: 'rgba(150,220,255,0.6) 55%, rgba(90,170,255,0) 72%', ring: 'rgba(150,220,255,0.85)', shadow: '#0f2a4a',
      desc: 'Besiege verlangsamte Gegner, fülle die Leiste und hol dir die Event-Truhe!', foes: 'Verlangsamte Gegner besiegt',
      chip: '#6fd0ff, #3a7dff'},
    zombienacht: {title: 'Zombienacht', boss: '089a0bc38b2df302db6022f0846007ca', bg: '#9ad94a 0%, #3f7a2a 45%, #1f2a4a 100%',
      border: 'rgba(210,255,150,0.5)', glow: 'rgba(190,255,120,0.55) 55%, rgba(140,220,60,0) 72%', ring: 'rgba(190,255,120,0.8)', shadow: '#1f3a10',
      desc: 'Besiege Zombie-Gegner, fülle die Leiste und hol dir die Event-Truhe!', foes: 'Zombie-Gegner besiegt',
      chip: '#b6ff6a, #4f9a2a'},
    lavawoche: {title: 'Lavawoche', boss: '15743b7c4950ddde62df4f72ddb0dbbe', bg: '#ffb04a 0%, #c2451a 45%, #4a1630 100%',
      border: 'rgba(255,210,160,0.55)', glow: 'rgba(255,190,110,0.6) 55%, rgba(255,120,40,0) 72%', ring: 'rgba(255,180,90,0.85)', shadow: '#5a1a08',
      desc: 'Besiege starke Gegner, fülle die Leiste und hol dir die Event-Truhe!', foes: 'Starke Gegner besiegt',
      chip: '#ffc46a, #e0601a'},
  };
  const ORDER = ['schleimflut', 'frostwoche', 'zombienacht', 'lavawoche'];
  const root = () => document.getElementById('dc-root');
  const waitImages = () => Promise.all(Array.from(document.images).map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  return {
    theme(id) {
      const t = T[id];
      const next = T[ORDER[(ORDER.indexOf(id) + 1) % ORDER.length]];
      const banner = Array.from(root().querySelectorAll('div')).find(d => d.style.top === '8px' && d.style.height === '156px');
      banner.style.background = `radial-gradient(90% 120% at 15% 50%, ${t.bg})`;
      banner.style.borderColor = t.border;
      const portrait = banner.querySelector('img');
      portrait.src = '/_blob/' + t.boss;
      portrait.alt = t.title;
      portrait.style.boxShadow = `0 0 0 3px #fff, 0 0 14px 4px ${t.ring}`;
      portrait.parentElement.style.background = `radial-gradient(circle, ${t.glow})`;
      const title = Array.from(banner.querySelectorAll('div')).find(d => d.textContent.trim() === 'Schleimflut');
      title.textContent = t.title;
      title.style.textShadow = `0 2px 0 ${t.shadow}`;
      const desc = Array.from(banner.querySelectorAll('div')).find(d => d.textContent.startsWith('Besiege'));
      desc.textContent = t.desc;
      const foes = Array.from(root().querySelectorAll('span')).find(s => s.textContent.trim() === 'Schleim-Gegner besiegt');
      foes.textContent = t.foes;
      const chip = Array.from(root().querySelectorAll('span')).find(s => s.textContent.trim() === 'Frostwoche');
      chip.textContent = next.title;
      chip.style.background = `linear-gradient(180deg, ${next.chip})`;
      return waitImages();
    },
  };
})();
