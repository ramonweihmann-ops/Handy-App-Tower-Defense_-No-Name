// Shop (Main-c4lv.dc.html): Zusatz-Zustände für die Reiter Truhen, Aufladen und Event.
// Das Mockup zeigt nur „Angebote“; die anderen Reiter werden hier aus den Bausteinen des Mockups
// zusammengesetzt (gleiche Karten, Kacheln, Überschriften, Knöpfe und Symbole).
window.m2g = (() => {
  const root = () => document.getElementById('dc-root');
  const area = () => Array.from(root().querySelectorAll('div')).find(d => d.style.top === '64px' && d.style.height === '668px');
  const grid = () => area().querySelector('div[style*="grid-template-columns"]');
  // Symbole aus dem Mockup (Edelstein, Münze, Heldenkarten, Stern, Blitz, Truhe)
  const icons = () => {
    const g = grid().children;
    return {
      gem: g[0].firstElementChild.outerHTML,
      coin: g[1].firstElementChild.outerHTML,
      cards: g[2].firstElementChild.outerHTML,
      star: g[3].firstElementChild.outerHTML,
      bolt: root().querySelector('svg path[d^="M13 2 4 14"]').closest('svg').outerHTML,
      chest: area().querySelector('div[style*="width: 160px; height: 116px"]').outerHTML,
    };
  };
  const sized = (svg, w, h) => svg.replace(/width="[\d.]+"/, `width="${w}"`).replace(/height="[\d.]+"/, `height="${h}"`);

  const header = (top, text) => `<div style="position: absolute; left: 70px; right: 70px; top: ${top}px; height: 34px; border-radius: 8px; background: linear-gradient(180deg, #8a6ae0, #6a4ac0); box-shadow: inset 0 0 0 2px rgba(255,255,255,0.18); display: grid; place-items: center; font: 700 17px Fredoka, sans-serif; letter-spacing: 0.06em; color: #e8e0ff">${text}</div>`;
  const card = (top, h, inner, look, extra = '') => `<div style="position: absolute; left: 12px; right: 12px; top: ${top}px; height: ${h}px; border-radius: 18px; background: rgba(30,20,80,0.55); padding: 8px; box-sizing: border-box"><div style="position: relative; height: 100%; border-radius: 14px; overflow: hidden; ${look}">${inner}</div>${extra}</div>`;
  const LOOK = {
    gold: 'border: 2px solid #ffd34d; background: radial-gradient(circle at 30% 45%, #ffc06b 0%, #e0801f 45%, #a8461a 100%); box-shadow: 0 0 18px rgba(255,200,90,0.55), inset 0 0 24px rgba(255,230,150,0.25)',
    green: 'border: 2px solid #b6ffcf; background: radial-gradient(circle at 30% 45%, #7ee09a 0%, #2f9d5b 50%, #16603a 100%); box-shadow: 0 0 18px rgba(120,255,160,0.4), inset 0 0 24px rgba(220,255,230,0.2)',
    blue: 'border: 2px solid #9bb4ff; background-color: #2e3aa8; background-image: radial-gradient(circle at 78% 18%, rgba(160,190,255,0.45) 0%, rgba(160,190,255,0) 50%), radial-gradient(rgba(255,255,255,0.07) 22%, rgba(255,255,255,0) 24%), linear-gradient(160deg, #4a63e6 0%, #2e3aa8 58%, #23267a 100%); background-size: auto, 20px 20px, auto',
    event: 'border: 2px solid #9fd0ff; background-color: #2a4fbf; background-image: radial-gradient(circle at 70% 30%, rgba(160,210,255,0.5) 0%, rgba(160,210,255,0) 55%), radial-gradient(rgba(255,255,255,0.07) 22%, rgba(255,255,255,0) 24%), linear-gradient(170deg, #3a7dff 0%, #2a4fbf 60%, #1d2f86 100%); background-size: auto, 20px 20px, auto',
  };
  const rays = '<div aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 200px; height: 150px; background: repeating-conic-gradient(from 0deg at 35% 55%, rgba(255,255,255,0.12) 0deg 10deg, rgba(255,255,255,0) 10deg 22deg)"></div>';
  const tile = (icon, text, w = 58, h = 62, size = 13) => `<div style="width: ${w}px; height: ${h}px; border-radius: 10px; background: rgba(60,0,40,0.35); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px">${icon}<span style="font: 700 ${size}px Fredoka, sans-serif">${text}</span></div>`;
  const footer = (label, price, href, priceLook) => `<div style="position: absolute; left: 0; right: 0; bottom: 0; height: 46px; display: flex; align-items: stretch"><div style="flex: 1; background: linear-gradient(180deg, #8a4dff, #5a2ad0); clip-path: polygon(0 0, 92% 0, 100% 100%, 0 100%); display: flex; align-items: center; padding-left: 12px; font: 700 15px Fredoka, sans-serif; color: #fff">${label}</div><a href="${href}" style="width: 118px; text-decoration: none; ${priceLook}; display: flex; align-items: center; justify-content: center; gap: 4px; font: 700 22px Fredoka, sans-serif">${price}</a></div>`;
  const WHITE = 'background: linear-gradient(180deg, #ffffff, #cfe6ff); color: #1b1745';
  const GREEN = 'background: linear-gradient(180deg, #b6ff8a 0%, #5fd83f 60%, #3fbf3a 100%); color: #0f3d12; box-shadow: inset 0 2px 0 rgba(255,255,255,0.6)';
  const greenBtn = (href, inner, w, h, size) => `<a href="${href}" style="width: ${w}px; height: ${h}px; border-radius: 12px; text-decoration: none; color: #0f3d12; background: linear-gradient(180deg, #b6ff8a 0%, #5fd83f 60%, #3fbf3a 100%); box-shadow: 0 4px 0 #23802a, inset 0 2px 0 rgba(255,255,255,0.6); display: flex; align-items: center; justify-content: center; gap: 4px; font: 700 ${size}px Fredoka, sans-serif; flex: none">${inner}</a>`;
  const note = (top, text) => `<div style="position: absolute; left: 34px; right: 34px; top: ${top}px; font: 800 12px/1.35 Nunito, sans-serif; color: #d9d0ff; text-align: center">${text}</div>`;

  const pages = {
    truhen(I) {
      const truhe = card(0 + 58, 176,
        rays + I.chest +
        `<div style="position: absolute; left: 160px; right: 8px; top: 14px; display: flex; flex-direction: column; align-items: center; gap: 6px">` +
        tile(I.cards, '×25', 128, 62, 15) +
        `<div style="font: 800 11px/1.25 Nunito, sans-serif; text-align: center; color: #fff4e0">Zufällige Heldenkarten,<br>mehr mit jedem Level</div></div>` +
        footer('HELDENTRUHE', sized(I.gem, 22, 22) + '100', '#truhe', WHITE), LOOK.gold);
      const geschenk = card(294, 128,
        `<div style="position: absolute; left: 14px; top: 10px; width: 58px; height: 58px; display: grid; place-items: center">${sized(I.coin, 46, 46)}</div>` +
        `<div style="position: absolute; left: 84px; right: 10px; top: 12px"><div style="font: 700 20px Fredoka, sans-serif; color: #ffe27a; text-shadow: 0 2px 0 #0d4a26">GRATIS-GOLD</div><div style="font: 800 11px/1.25 Nunito, sans-serif">Jeden Tag ein kleines Geschenk</div></div>` +
        `<div style="position: absolute; right: 12px; top: 12px">${tile(sized(I.coin, 20, 20), '×100', 64, 44, 13)}</div>` +
        footer('1× PRO TAG', 'ABHOLEN', '#geschenk', GREEN), LOOK.green);
      const angebot = `<div style="position: absolute; left: 22px; right: 22px; top: 446px; height: 74px; border-radius: 12px; background: linear-gradient(180deg,#8a4dff,#5a2ad0); box-shadow: 0 8px 18px rgba(0,0,0,0.45),inset 0 2px 0 rgba(255,255,255,0.3); display: flex; align-items: center; padding: 0 12px 0 16px; gap: 10px; box-sizing: border-box"><div style="flex:1;font:700 16px/1.15 Fredoka,sans-serif;color:#ffe27a;text-align:center;text-shadow:0 2px 0 #3a1580">KARTEN-ANGEBOT<br>DES TAGES</div><a href="Kartenpaket.dc.html" style="min-width:138px;height:52px;border-radius:14px;text-decoration:none;color:#0f3d12;background:linear-gradient(180deg,#b6ff8a 0%,#5fd83f 60%,#3fbf3a 100%);box-shadow:0 5px 0 #23802a,inset 0 2px 0 rgba(255,255,255,0.6);display:grid;place-items:center;font:700 24px Fredoka,sans-serif">4,99 €</a></div>`;
      return header(14, 'TRUHEN') + truhe + header(250, 'TAGESGESCHENK') + geschenk + angebot +
        note(540, 'Heldenkarten landen bei deinen freigeschalteten Helden. Wer genug Karten hat, steigt in der Sammlung auf.');
    },
    aufladen(I) {
      const energie = card(58, 132,
        `<div aria-hidden="true" style="position: absolute; left: -4px; top: -6px; width: 120px; height: 130px; border-radius: 50%; background: radial-gradient(circle, rgba(170,255,160,0.55) 0%, rgba(125,255,138,0.2) 45%, rgba(125,255,138,0) 70%)"></div>` +
        `<div style="position: absolute; left: 14px; top: 12px; width: 84px; height: 92px; display: grid; place-items: center; filter: drop-shadow(0 3px 3px rgba(0,0,0,0.5))">${sized(I.bolt, 76, 76)}</div>` +
        `<div style="position: absolute; left: 112px; right: 10px; top: 12px"><div style="font: 700 20px Fredoka, sans-serif; color: #ffe27a; text-shadow: 0 2px 0 #1b1f6a">ENERGIE</div><div style="font: 800 11px/1.25 Nunito, sans-serif">Sofort wieder voll: 30/30</div></div>` +
        `<div style="position: absolute; left: 112px; bottom: 14px">${greenBtn('#energie', sized(I.gem, 22, 22) + '20', 124, 44, 21)}</div>` +
        `<div style="position: absolute; right: 12px; bottom: 14px; width: 92px; height: 44px; border-radius: 10px; background: rgba(16,20,70,0.6); border: 1.5px solid rgba(160,190,255,0.5); box-sizing: border-box; display: flex; align-items: center; justify-content: center; gap: 4px">${sized(I.bolt, 18, 18)}<span style="font: 700 14px Fredoka, sans-serif">25/30</span></div>`,
        LOOK.blue);
      const pack = (k, left, gems, n, price) => `<div style="position: absolute; left: ${left}px; top: 262px; width: 116px; height: 186px; border-radius: 18px; background: rgba(30,20,80,0.55); padding: 6px; box-sizing: border-box"><div style="position: relative; height: 100%; border-radius: 14px; overflow: hidden; ${LOOK.blue}; display: flex; flex-direction: column; align-items: center; padding-top: 10px; box-sizing: border-box">` +
        `<div style="height: 64px; display: flex; align-items: center; justify-content: center">${gems}</div>` +
        `<span style="font: 700 20px Fredoka, sans-serif; text-shadow: 0 2px 0 #1b1f6a; margin-top: 4px">${n}</span>` +
        `<span style="font: 800 10px Nunito, sans-serif; color: #c9d4ff">Edelsteine</span>` +
        `<div style="position: absolute; left: 6px; right: 6px; bottom: 8px">${greenBtn('#paket' + k, price, 92, 38, 18)}</div></div></div>`;
      const g = (w) => sized(I.gem, w, w);
      return header(14, 'ENERGIE') + energie + header(214, 'EDELSTEINE') +
        pack(0, 12, g(40), '×80', '1,99 €') +
        pack(1, 137, `<div style="display:flex;align-items:flex-end">${g(34)}<span style="margin-left:-10px">${g(46)}</span></div>`, '×500', '9,99 €') +
        pack(2, 262, `<div style="display:flex;align-items:flex-end">${g(32)}<span style="margin:0 -12px">${g(52)}</span>${g(32)}</div>`, '×1.200', '19,99 €') +
        note(468, 'In der Testphase gibt es Edelsteine im Battle Pass, am Glücksrad und als tägliche Belohnung.');
    },
    event(I) {
      const dragon = root().querySelector('a[href="#event"] img').getAttribute('src');
      const ev = card(58, 300,
        `<div aria-hidden="true" style="position: absolute; left: 0; top: 0; right: 0; height: 220px; background: repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,255,255,0.1) 0deg 10deg, rgba(255,255,255,0) 10deg 22deg)"></div>` +
        `<img src="${dragon}" alt="Drache" style="position: absolute; left: 50%; top: 8px; height: 170px; transform: translateX(-50%); filter: drop-shadow(0 8px 10px rgba(0,0,0,0.45))">` +
        `<div style="position: absolute; left: 0; right: 0; bottom: 0; height: 104px; background: linear-gradient(180deg, #8a4dff, #5a2ad0); box-shadow: 0 -2px 0 rgba(255,255,255,0.2); text-align: center; padding-top: 12px; box-sizing: border-box">` +
        `<div style="font: 700 22px Fredoka, sans-serif; color: #ffe27a; text-shadow: 0 2px 0 #3a1580">BALD GEHT'S LOS!</div>` +
        `<div style="font: 800 12px/1.35 Nunito, sans-serif; margin: 6px 18px 0">Hier startet bald das erste Event mit eigenen Belohnungen. Halte die Augen offen, Kommandant!</div></div>`,
        LOOK.event);
      return header(14, 'EVENT') + ev;
    },
  };

  const TAB_ON = 'background: linear-gradient(180deg, #b36bff, #7a3fd0); box-shadow: 0 2px 0 #4a1f8a; color: #fff';
  const TAB_OFF = 'background: rgba(255,255,255,0.06); box-shadow: none; color: #d9d0ff';
  const tabs = (name) => {
    const bar = Array.from(root().querySelectorAll('div')).find(d => d.style.top === '730px');
    const keys = ['angebote', 'truhen', 'aufladen', 'event'];
    Array.from(bar.children).forEach((a, k) => {
      if (keys[k] === 'event') {
        if (name === 'event') a.style.boxShadow = 'inset 0 0 0 2px #ffe27a, 0 2px 0 #1d2f86';
        return;
      }
      const on = keys[k] === name;
      for (const part of (on ? TAB_ON : TAB_OFF).split('; ')) { const [p, v] = part.split(': '); a.style.setProperty(p, v); }
    });
  };

  const waitImages = () => Promise.all(Array.from(document.images).map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));

  return {
    // Überbleibsel aus dem Entwurf: rechts oben ragt ein halbes „Karten-Angebot“ ins Bild.
    // Nur unsichtbar machen: es bestimmt die Höhe der Kopfleiste mit.
    clean() {
      const extra = root().querySelector('div[style*="margin: auto -10px 0"]');
      if (extra) extra.style.visibility = 'hidden';
    },
    // Grundzustand: Sonderangebot und Talentstern-Angebot antippbar machen
    offers() {
      this.clean();
      const sonder = Array.from(area().children).find(d => d.style.top === '390px');
      sonder.setAttribute('data-on', 'sonder');
      const talent = Array.from(area().children).find(d => d.style.top === '624px');
      talent.setAttribute('data-on', 'talent');
    },
    page(name) {
      this.clean();
      const I = icons();
      area().innerHTML = pages[name](I);
      tabs(name);
      return waitImages();
    },
  };
})();
