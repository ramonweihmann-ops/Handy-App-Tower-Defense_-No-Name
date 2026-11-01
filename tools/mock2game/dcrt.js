// Kleine Nachbildung der Mockup-Laufzeit (x-dc): {{ }}-Lücken, sc-if, sc-for, onClick, setState.
(function(){
  class DCLogic { constructor(){ this.state = null; } setState(o){ this.state = Object.assign({}, this.state || {}, o); window.__dcRender(); } }
  window.DCLogic = DCLogic;
  const ev = (expr, scope) => { const k = Object.keys(scope); try { return Function(...k, 'return (' + expr + ');')(...k.map(x => scope[x])); } catch (e) { return undefined; } };
  const interp = (s, scope) => s.replace(/\{\{\s*([^}]+?)\s*\}\}/g, (_, e) => { const v = ev(e, scope); return v === undefined || v === null ? '' : String(v); });
  function build(node, scope, out) {
    for (const ch of Array.from(node.childNodes)) {
      if (ch.nodeType === 3) { out.appendChild(document.createTextNode(interp(ch.nodeValue, scope))); continue; }
      if (ch.nodeType !== 1) continue;
      const tag = ch.tagName.toLowerCase();
      if (tag === 'sc-if') { const m = /\{\{\s*(.+?)\s*\}\}/.exec(ch.getAttribute('value') || ''); if (m && ev(m[1], scope)) build(ch.content || ch, scope, out); continue; }
      if (tag === 'sc-for') { const m = /\{\{\s*(.+?)\s*\}\}/.exec(ch.getAttribute('list') || ''); const as = ch.getAttribute('as') || 'it'; const list = m ? ev(m[1], scope) || [] : [];
        list.forEach((it, i) => { const sc = Object.assign({}, scope); sc[as] = it; sc.index = i; build(ch, sc, out); }); continue; }
      const el = document.createElementNS(ch.namespaceURI, ch.localName);
      for (const a of Array.from(ch.attributes)) {
        if (a.name.startsWith('hint-')) continue;
        const m = /^\{\{\s*(.+?)\s*\}\}$/.exec(a.value);
        if (a.name.toLowerCase().startsWith('on') && m) { const f = ev(m[1], scope); if (typeof f === 'function') el.addEventListener(a.name.slice(2).toLowerCase(), f); el.setAttribute('data-on', m[1]); continue; }
        el.setAttribute(a.name, interp(a.value, scope));
      }
      build(ch, scope, el); out.appendChild(el);
    }
  }
  window.addEventListener('DOMContentLoaded', () => {
    const x = document.querySelector('x-dc'); const tpl = document.createElement('div'); tpl.innerHTML = x.innerHTML;
    const helmet = tpl.querySelector('helmet'); if (helmet) { for (const c of Array.from(helmet.children)) if (c.tagName !== 'LINK') document.head.appendChild(c.cloneNode(true)); helmet.remove(); }
    const sn = document.querySelector('script[data-dc-script]'); const src = sn ? sn.textContent : 'class Component extends DCLogic { renderVals(){ return {}; } }';
    const Comp = Function('DCLogic', src + '\nreturn Component;')(DCLogic);
    const comp = new Comp(); window.__dcComp = comp;
    const host = document.createElement('div'); host.id = 'dc-root'; x.replaceWith(host);
    window.__dcRender = () => { const vals = comp.renderVals() || {}; host.innerHTML = ''; build(tpl, vals, host); };
    window.__dcRender(); window.__dcReady = true;
  });
})();
