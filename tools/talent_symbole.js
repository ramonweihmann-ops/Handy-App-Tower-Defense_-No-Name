// Vorläufige Talent-Symbole für Funkenherz, Werkzeugkiste, Bollwerk, Schwerefeld (bis ChatGPT liefert): Formen wie im
// Mockup „Held aufleveln“, mit dunklem Umriss und Glanz. Aufruf: node tools/talent_symbole.js <ordner> → tal_<id>.png
const { chromium } = require('playwright');
const ICONS = {
  funkenherz: ['<path d="M11 3l2 6.5 6.5 2.5-6.5 2.5-2 6.5-2-6.5-6.5-2.5 6.5-2.5z" fill="#ff9ae0"/>', '<path d="M19 2.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" fill="#ffd34d"/>', '#7a1f6a'],
  werkzeugkiste: ['<path d="M15 3a5 5 0 0 0-4.8 6.4l-6.4 6.4a2.1 2.1 0 0 0 3 3l6.4-6.4A5 5 0 0 0 19.6 7l-3 3-2.5-.6-.6-2.5 3-3A5 5 0 0 0 15 3z" fill="#8fe8e8"/>', '', '#0f5560'],
  bollwerk: ['<path d="M12 3l7 2.8V11c0 4.8-3.2 8.3-7 10-3.8-1.7-7-5.2-7-10V5.8z" fill="#ffc070"/>', '<path d="M12 6v12M7.5 11h9" stroke="#d8661a" stroke-width="1.6"/>', '#7a3408'],
  schwerefeld: ['<path d="M12 12a1.5 1.5 0 0 1 3 0a3 3 0 0 1-6 0a4.5 4.5 0 0 1 9 0a6 6 0 0 1-12 0" fill="none" stroke="#d0a8ff" stroke-width="2.4" stroke-linecap="round"/>', '', '#3a1670'],
};
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 176, height: 176 } });
  for (const [id, [shape, extra, dark]] of Object.entries(ICONS)) {
    // Umriss: dieselbe Form dick und dunkel dahinter; Glanz: helle Kopie oben links, auf die Form beschnitten
    const outline = shape.replace(/fill="#[0-9a-f]+"/, `fill="${dark}"`).replace('/>', ` stroke="${dark}" stroke-width="3.2" stroke-linejoin="round"/>`)
      .replace(/stroke="#d0a8ff" stroke-width="2.4"/, `stroke="${dark}" stroke-width="5.4"`);
    const extraOutline = extra && !extra.includes('stroke=') ? extra.replace(/fill="#[0-9a-f]+"/, `fill="${dark}"`).replace('/>', ` stroke="${dark}" stroke-width="2.6" stroke-linejoin="round"/>`) : '';
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="176" height="176" viewBox="0 0 24 24">
      <defs><clipPath id="c">${shape.replace(/stroke="[^"]*"|stroke-width="[^"]*"|stroke-linecap="[^"]*"|fill="none"/g, '')}</clipPath>
      <linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
      ${outline}${extraOutline}${shape}<rect x="0" y="0" width="24" height="13" fill="url(#g)" clip-path="url(#c)"/>${extra}</svg>`;
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.screenshot({ path: `${process.argv[2]}/tal_${id}.png`, omitBackground: true, clip: { x: 0, y: 0, width: 176, height: 176 } });
  }
  await b.close();
})();
