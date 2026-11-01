// Mockup -> Spiel: zerlegt einen Mockup-Bildschirm in Hintergrund, Knöpfe und Texte.
// node export.js <config.json>
// Config: {board, out, states:[{name, set:{...}, eval|eval_file}], live:[{sel, id, img, pad}], scale}
//  - live: Elemente, die das Spiel selbst darstellt (z. B. 3D-Helden); sie fehlen im Hintergrund,
//    ihr Rechteck steht in der JSON-Datei.
const fs = require('fs'); const path = require('path');
const { open } = require('./shoot.js');

const PREP = `(() => {
  // 1) Texte in Spans packen, damit sie messbar und ausblendbar sind
  const root = document.getElementById('dc-root');
  // Text mit <br> direkt in einem Grid/Flex: im Browser ein gemeinsames Element; damit das nach dem
  // Einpacken in Spans so bleibt, alles in einen Span fassen (z. B. „JETZT<br>BEITRETEN“)
  root.querySelectorAll('br').forEach(br => { const p = br.parentElement; const d = getComputedStyle(p).display;
    if (!/grid|flex/.test(d) || p.dataset.m2gWrap) return; const kids = Array.from(p.childNodes);
    if (!kids.every(k => k.nodeType === 3 || k.localName === 'br')) return;
    const s = document.createElement('span'); kids.forEach(k => s.appendChild(k)); p.appendChild(s); p.dataset.m2gWrap = '1'; });
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = []; let n;
  while ((n = walker.nextNode())) {
    if (!n.nodeValue.trim()) continue;
    const p = n.parentElement; if (!p || p.closest('svg')) continue;
    nodes.push(n);
  }
  // In Flex-/Grid-Behältern bilden Text und <br> zusammen ein Element; die Spans dürfen das nicht aufbrechen
  for (const t of nodes) { const s = document.createElement('span'); s.className = 'm2g-t'; const pd = getComputedStyle(t.parentElement).display;
    if (/flex|grid/.test(pd) && t.parentElement.querySelector(':scope > br')) s.style.display = 'contents'; t.replaceWith(s); s.appendChild(t); }
  // 2) Animationen anhalten (fester Zeitpunkt)
  for (const sv of document.querySelectorAll('svg')) { try { sv.pauseAnimations(); sv.setCurrentTime(0.35); } catch (e) {} }
  for (const a of document.getAnimations()) { try { a.pause(); a.currentTime = 350; } catch (e) {} }
  // SVG-Texte ebenfalls als Text behandeln (Zahlen in Anzeigen)
  document.querySelectorAll('#dc-root svg text').forEach(t => { if (t.textContent.trim()) t.classList.add('m2g-svgt'); });
  return nodes.length;
})()`;

// Signatur je Element; Texte zählen gleich, ob schon in m2g-t-Spans verpackt oder nicht
const SIGS = `(() => { const out = []; document.querySelectorAll('#dc-root *').forEach(e => { if (e.classList.contains('m2g-t')) return; out.push(e.localName + '|' + (e.getAttribute('style') || '') + '|' + (e.getAttribute('src') || '') + '|' + (e.getAttribute('d') || '') + '|' + Array.from(e.childNodes).map(n => n.nodeType === 3 ? n.nodeValue.trim() : (n.classList && n.classList.contains('m2g-t') ? n.textContent.trim() : '')).join('')); }); return out; })()`;
const MARK_OVERLAY = `((base) => { const cnt = {}; base.forEach(k => cnt[k] = (cnt[k] || 0) + 1); let n = 0;
  document.querySelectorAll('#dc-root *').forEach(e => { if (e.classList.contains('m2g-t')) return; const k = e.localName + '|' + (e.getAttribute('style') || '') + '|' + (e.getAttribute('src') || '') + '|' + (e.getAttribute('d') || '') + '|' + Array.from(e.childNodes).map(n => n.nodeType === 3 ? n.nodeValue.trim() : (n.classList && n.classList.contains('m2g-t') ? n.textContent.trim() : '')).join('');
    if (e.parentElement && e.parentElement.closest('[data-m2g-ov]')) return; if (cnt[k]) { cnt[k]--; return; } e.setAttribute('data-m2g-ov', '1'); n++; });
  return n; })`;
const COLLECT = `((liveSel) => {
  const out = { texts: [], buttons: [], live: [] };
  const rot = (el) => { let a = 0; for (let e = el; e && e.id !== 'dc-root'; e = e.parentElement) { const t = getComputedStyle(e).transform; if (t && t !== 'none') { const m = new DOMMatrix(t); a += Math.atan2(m.b, m.a) * 180 / Math.PI; } } return Math.round(a * 10) / 10; };
  const op = (el) => { let o = 1; for (let e = el; e && e.id !== 'dc-root'; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const visible = (el) => { for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return false; } return true; };
  const ovm = !!document.querySelector('[data-m2g-ov]'); const inOv = (e) => !ovm || !!e.closest('[data-m2g-ov]');
  const btns = Array.from(document.querySelectorAll('#dc-root button, #dc-root a, #dc-root [data-on]')).filter(b => !b.parentElement.closest('button, a, [data-on]') && visible(b) && inOv(b));
  btns.forEach((b, i) => { b.setAttribute('data-m2g-btn', i); const r = b.getBoundingClientRect();
    out.buttons.push({ i, rect: [r.left, r.top, r.width, r.height], href: b.getAttribute('href') || '', on: b.getAttribute('data-on') || '', label: b.getAttribute('aria-label') || '', rot: rot(b) }); });
  // rote Hinweis-Punkte: zeichnet das Spiel nur, wenn etwas wartet
  Array.from(document.querySelectorAll('#dc-root span[style*="background: #ff3b30"]')).filter(e => visible(e) && inOv(e)).forEach((el, k) => {
    const r = el.getBoundingClientRect(); if (r.width > 20) return; const owner = el.closest('[data-m2g-btn]');
    el.setAttribute('data-m2g-live', 'badge' + k); out.live.push({ id: 'badge' + k, rect: [r.left, r.top, r.width, r.height], rot: 0, badge: true, button: owner ? +owner.getAttribute('data-m2g-btn') : -1 }); });
  (liveSel || []).forEach(l => { document.querySelectorAll(l.sel).forEach((el, k) => { if (!visible(el) || !inOv(el)) return; el.setAttribute('data-m2g-live', l.id + (k ? '_' + k : '')); const r = el.getBoundingClientRect(); out.live.push({ id: l.id + (k ? '_' + k : ''), rect: [r.left, r.top, r.width, r.height], rot: rot(el), img: !!l.img, pad: l.pad || 8 }); }); });
  document.querySelectorAll('.m2g-svgt').forEach((t, k) => {
    if (!visible(t) || t.closest('[data-m2g-live]') || !inOv(t)) return;
    const cs = getComputedStyle(t); const r = t.getBoundingClientRect(); if (r.width < 0.5) return;
    const anchor = t.getAttribute('text-anchor') || cs.textAnchor || 'start';
    const owner = t.closest('[data-m2g-btn]');
    out.texts.push({ i: 10000 + k, text: t.textContent.trim(), lines: [{ rect: [r.left, r.top, r.width, r.height], text: t.textContent.trim() }],
      family: (t.getAttribute('font-family') || cs.fontFamily).split(',')[0].replace(/["']/g, '').trim(), weight: +(t.getAttribute('font-weight') || cs.fontWeight), size: parseFloat(cs.fontSize) * (t.getScreenCTM() ? Math.hypot(t.getScreenCTM().a, t.getScreenCTM().b) : 1),
      color: cs.fill && cs.fill.startsWith('rgb') ? cs.fill : cs.color, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) || 0, shadow: 'none',
      align: anchor === 'middle' ? 'center' : (anchor === 'end' ? 'right' : 'left'), rot: rot(t), opacity: op(t), button: owner ? +owner.getAttribute('data-m2g-btn') : -1, svg: true });
  });
  document.querySelectorAll('.m2g-t').forEach((s, i) => {
    if (!visible(s) || s.closest('[data-m2g-live]') || !inOv(s)) return;
    const cs = getComputedStyle(s); const range = document.createRange(); range.selectNodeContents(s);
    const lines = Array.from(range.getClientRects()).filter(r => r.width > 0.5 && r.height > 0.5);
    if (!lines.length) return;
    let txt = s.textContent.replace(/\\s+/g, ' ').trim();
    if (cs.textTransform === 'uppercase') txt = txt.toUpperCase();
    // Text pro Zeile aufteilen: Wörter den Zeilen zuordnen
    const words = []; const tn = s.firstChild; const raw = tn.nodeValue; const re = /[^\\s-]+-+|[^\\s-]+|-+/g; let m;
    while ((m = re.exec(raw))) { const rr = document.createRange(); rr.setStart(tn, m.index); rr.setEnd(tn, m.index + m[0].length); const b = rr.getBoundingClientRect(); words.push({ w: cs.textTransform === 'uppercase' ? m[0].toUpperCase() : m[0], y: b.top + b.height / 2, start: m.index, end: m.index + m[0].length }); }
    const ln = lines.map(r => ({ rect: [r.left, r.top, r.width, r.height], text: '' }));
    words.forEach((w, wi) => { w.gap = wi > 0 && /\\s/.test(raw.slice(words[wi-1].end, w.start)); });
    for (const w of words) { let best = 0, bd = 1e9; ln.forEach((l, k) => { const d = Math.abs(l.rect[1] + l.rect[3] / 2 - w.y); if (d < bd) { bd = d; best = k; } }); ln[best].text += (ln[best].text && w.gap ? ' ' : '') + w.w; }
    const owner = s.closest('[data-m2g-btn]');
    // Ausrichtung: nächster Block-Vorfahr
    let blk = s.parentElement; while (blk && getComputedStyle(blk).display === 'inline') blk = blk.parentElement;
    out.texts.push({ i, text: txt, lines: ln.filter(l => l.text), family: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), weight: +cs.fontWeight, size: parseFloat(cs.fontSize),
      color: cs.color, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing), shadow: cs.textShadow, align: blk ? getComputedStyle(blk).textAlign : 'left',
      rot: rot(s), opacity: op(s), button: owner ? +owner.getAttribute('data-m2g-btn') : -1 });
  });
  return out;
})`;

async function shootLive(p, data, pre) {
  for (const l of data.live) {
    if (!l.img) continue;
    await p.evaluate((id) => { const r = document.getElementById('dc-root'); r.dataset.vis = r.style.visibility; r.style.setProperty('visibility', 'hidden', 'important');
      document.querySelectorAll('#dc-root *').forEach(e => { if (e.style.visibility === 'visible') e.style.removeProperty('visibility'); });
      document.querySelectorAll('[data-m2g-ov]').forEach(e => e.style.setProperty('visibility', 'hidden', 'important'));
      document.querySelectorAll('[data-m2g-btn]').forEach(e => e.style.setProperty('visibility', 'hidden', 'important'));
      const el = document.querySelector('[data-m2g-live="' + id + '"]'); el.style.setProperty('visibility', 'visible', 'important');
      // Kinder des Elements (z. B. Pfade eines SVG in einem Popup) nicht einzeln verstecken, Knöpfe schon
      el.querySelectorAll('*').forEach(c => { if (!c.hasAttribute('data-m2g-btn')) c.style.removeProperty('visibility'); }); }, l.id);
    const [x, y, w, h] = l.rect; const pad = l.pad || 8;  // pad: Rand für Leuchten/Schatten (Konfiguration)
    const clip = { x: Math.max(0, x - pad), y: Math.max(0, y - pad), width: Math.min(390, x + w + pad) - Math.max(0, x - pad), height: Math.min(844, y + h + pad) - Math.max(0, y - pad) };
    l.img_rect = [clip.x, clip.y, clip.width, clip.height];
    await p.screenshot({ path: `${pre}_live_${l.id}.png`, clip, omitBackground: true });
    await p.evaluate((id) => { document.querySelector('[data-m2g-live="' + id + '"]').style.removeProperty('visibility'); }, l.id);
  }
}

(async () => {
  const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  // script: Hilfs-Skript (Pfad relativ zur Konfiguration), läuft vor jedem eval, z. B. für Zusatz-Zustände
  const helper = cfg.script ? fs.readFileSync(path.resolve(path.dirname(process.argv[2]), cfg.script), 'utf8') : '';
  // eval_file: JavaScript aus einer Datei neben der Konfiguration (statt eval als Zeichenkette)
  for (const st of [...(cfg.states || []), ...(cfg.overlays || [])]) if (st.eval_file) st.eval = fs.readFileSync(path.join(path.dirname(process.argv[2]), st.eval_file), 'utf8');
  const scale = cfg.scale || 3;
  fs.mkdirSync(cfg.out, { recursive: true });
  const result = { board: cfg.board, size: [390, 844], scale, states: {}, transparent: !!cfg.only };
  for (const st of cfg.states || [{ name: 'main' }]) {
    const { b, p } = await open(cfg.board, scale);
    if (st.set) { await p.evaluate((o) => window.__dcComp.setState(o), st.set); await p.waitForTimeout(200); }
    if (st.eval) { if (helper) await p.evaluate(helper); await p.evaluate(st.eval); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); }
    await p.evaluate(PREP);
    if (cfg.only) await p.evaluate((sels) => { const keep = new Set(); sels.forEach(q => document.querySelectorAll(q).forEach(e => keep.add(e)));
      document.querySelectorAll('#dc-root *').forEach(e => { let k = false; for (let a = e; a; a = a.parentElement) if (keep.has(a)) { k = true; break; } if (!k) { let d = false; keep.forEach(x => { if (e.contains(x)) d = true; }); if (!d) e.style.setProperty('display', 'none', 'important'); } });
      const r = document.querySelector('#dc-root > div'); r.style.setProperty('background', 'transparent', 'important'); }, cfg.only);
    const data = await p.evaluate(COLLECT + '(' + JSON.stringify(cfg.live || []) + ')');
    // Texte ausblenden
    await p.addStyleTag({ content: 'html,body{background:transparent!important} .m2g-t{color:transparent!important;text-shadow:none!important;-webkit-text-stroke:0!important} .m2g-svgt{fill:transparent!important;stroke:transparent!important} [data-m2g-live]{visibility:hidden!important}' });
    // Hintergrund ohne Knöpfe
    await p.addStyleTag({ content: '[data-m2g-btn]{visibility:hidden!important}' });
    const pre = path.join(cfg.out, st.name);
    await p.screenshot({ path: pre + '_bg.png', omitBackground: !!cfg.only });
    await p.addStyleTag({ content: '[data-m2g-btn]{visibility:visible!important}' });
    // Knöpfe einzeln, mit Rand für Schatten
    for (const btn of data.buttons) {
      await p.evaluate((i) => { document.getElementById('dc-root').style.visibility = 'hidden'; document.querySelectorAll('[data-m2g-btn]').forEach(e => e.style.setProperty('visibility', e.getAttribute('data-m2g-btn') == i ? 'visible' : 'hidden', 'important')); }, btn.i);
      const pad = 12; const [x, y, w, h] = await p.evaluate((i) => { const el = document.querySelector('[data-m2g-btn="' + i + '"]'); let r = el.getBoundingClientRect(); let a = [r.left, r.top, r.right, r.bottom];
        el.querySelectorAll('*').forEach(c => { const q = c.getBoundingClientRect(); if (q.width > 0 && q.height > 0) a = [Math.min(a[0], q.left), Math.min(a[1], q.top), Math.max(a[2], q.right), Math.max(a[3], q.bottom)]; });
        return [a[0], a[1], a[2] - a[0], a[3] - a[1]]; }, btn.i);
      const clip = { x: Math.max(0, x - pad), y: Math.max(0, y - pad), width: Math.min(390, x + w + pad) - Math.max(0, x - pad), height: Math.min(844, y + h + pad) - Math.max(0, y - pad) };
      if (clip.width < 1 || clip.height < 1) continue;
      btn.img_rect = [clip.x, clip.y, clip.width, clip.height];
      await p.screenshot({ path: `${pre}_btn${btn.i}.png`, clip, omitBackground: true });
    }
    await p.evaluate(() => { document.querySelectorAll('[data-m2g-btn]').forEach(e => e.style.removeProperty('visibility')); document.getElementById('dc-root').style.visibility = ''; });
    await shootLive(p, data, pre);
    result.states[st.name] = data;
    await b.close();
  }
  // Popups: nur die Elemente, die gegenüber dem Grundzustand neu sind
  result.overlays = {};
  for (const ov of cfg.overlays || []) {
    const { b, p } = await open(cfg.board, scale);
    if (ov.base) await p.evaluate((o) => window.__dcComp.setState(o), ov.base);
    const base = await p.evaluate(SIGS);
    await p.evaluate((o) => window.__dcComp.setState(o), ov.set || {});
    if (ov.eval) { if (helper) await p.evaluate(helper); await p.evaluate(ov.eval); }
    await p.waitForTimeout(250);
    // erst vergleichen, dann Texte einpacken (sonst gilt jedes Element mit Text als neu)
    const n = await p.evaluate(MARK_OVERLAY + '(' + JSON.stringify(base) + ')');
    await p.evaluate(PREP);
    const data = await p.evaluate(COLLECT + '(' + JSON.stringify(cfg.live || []) + ')');
    await p.addStyleTag({ content: 'html,body{background:transparent!important} .m2g-t{color:transparent!important;text-shadow:none!important} .m2g-svgt{fill:transparent!important;stroke:transparent!important} [data-m2g-live]{visibility:hidden!important} #dc-root{visibility:hidden!important} [data-m2g-ov]{visibility:visible!important} [data-m2g-btn]{visibility:hidden!important}' });
    const box = await p.evaluate(() => { let a = null; document.querySelectorAll('[data-m2g-ov], [data-m2g-ov] *').forEach(e => { const q = e.getBoundingClientRect(); if (q.width < 0.5 || q.height < 0.5) return; const cs = getComputedStyle(e);
      const shadow = parseFloat((cs.boxShadow.match(/(\d+)px\)?\s*$/) || [0, 0])[1]) || 0; const g = Math.min(40, 6 + (cs.boxShadow !== 'none' ? 24 : 0));
      const r = [q.left - g, q.top - g, q.right + g, q.bottom + g]; a = a ? [Math.min(a[0], r[0]), Math.min(a[1], r[1]), Math.max(a[2], r[2]), Math.max(a[3], r[3])] : r; });
      if (!a) return [0, 0, 1, 1]; a = [Math.max(0, a[0]), Math.max(0, a[1]), Math.min(390, a[2]), Math.min(844, a[3])]; return [a[0], a[1], a[2] - a[0], a[3] - a[1]]; });
    const pre = path.join(cfg.out, 'ov_' + ov.name);
    await p.screenshot({ path: pre + '_bg.png', clip: { x: box[0], y: box[1], width: box[2], height: box[3] }, omitBackground: true });
    data.rect = box;
    await p.addStyleTag({ content: '[data-m2g-btn]{visibility:visible!important}' });
    for (const btn of data.buttons) {
      await p.evaluate((i) => { document.querySelectorAll('[data-m2g-ov]').forEach(e => e.style.setProperty('visibility', 'hidden', 'important')); document.querySelectorAll('[data-m2g-btn]').forEach(e => e.style.setProperty('visibility', e.getAttribute('data-m2g-btn') == i ? 'visible' : 'hidden', 'important')); }, btn.i);
      const [x, y, w, h] = await p.evaluate((i) => { const el = document.querySelector('[data-m2g-btn="' + i + '"]'); let r = el.getBoundingClientRect(); let a = [r.left, r.top, r.right, r.bottom];
        el.querySelectorAll('*').forEach(c => { const q = c.getBoundingClientRect(); if (q.width > 0 && q.height > 0) a = [Math.min(a[0], q.left), Math.min(a[1], q.top), Math.max(a[2], q.right), Math.max(a[3], q.bottom)]; }); return [a[0], a[1], a[2] - a[0], a[3] - a[1]]; }, btn.i);
      const pad = 12; const clip = { x: Math.max(0, x - pad), y: Math.max(0, y - pad), width: Math.min(390, x + w + pad) - Math.max(0, x - pad), height: Math.min(844, y + h + pad) - Math.max(0, y - pad) };
      if (clip.width < 1 || clip.height < 1) continue;
      btn.img_rect = [clip.x, clip.y, clip.width, clip.height];
      await p.screenshot({ path: `${pre}_btn${btn.i}.png`, clip, omitBackground: true });
    }
    await p.evaluate(() => { document.querySelectorAll('[data-m2g-ov], [data-m2g-btn]').forEach(e => e.style.removeProperty('visibility')); });
    await shootLive(p, data, pre);
    result.overlays[ov.name] = data;
    console.log('Popup', ov.name, n, 'Elemente,', data.texts.length, 'Texte,', data.buttons.length, 'Knöpfe');
    await b.close();
  }
  fs.writeFileSync(path.join(cfg.out, 'layout.json'), JSON.stringify(result, null, 1));
  console.log('fertig', cfg.board, Object.keys(result.states).map(k => k + ':' + result.states[k].texts.length + 't/' + result.states[k].buttons.length + 'b').join(' '));
})();
