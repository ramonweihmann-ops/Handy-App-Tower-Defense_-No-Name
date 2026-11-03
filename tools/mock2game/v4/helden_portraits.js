// Findet Heldenbilder in kleinen Boxen (Karte, Kreis): Bild ragt über die abschneidende Box hinaus.
// Ausgabe je Board: Nummer des <img> im Quelltext, Box-Größe und Lage der Box im offsetParent.
const {open}=require('../shoot.js');
const HEROES=JSON.parse(process.argv[3]);
(async()=>{
  const boards=JSON.parse(process.argv[2]); const out={};
  for(const b of boards){
    const {b:br,p}=await open(b,1);
    out[b]=await p.evaluate((H)=>{
      const res=[]; const imgs=[...document.querySelectorAll('#dc-root img')];
      imgs.forEach((im,i)=>{
        const m=(im.getAttribute('src')||'').match(/_blob\/([0-9a-f]+)/); if(!m||!H[m[1]])return;
        let c=im.parentElement; while(c&&c.id!=='dc-root'&&getComputedStyle(c).overflow==='visible')c=c.parentElement;
        if(!c||c.id==='dc-root')return;
        const cr=c.getBoundingClientRect(), ir=im.getBoundingClientRect();
        if(cr.width>200||cr.height>260)return;
        if(!(ir.height>cr.height*1.08||ir.bottom>cr.bottom+3))return;
        const op=im.offsetParent.getBoundingClientRect();
        const cs=getComputedStyle(c);
        res.push({i,hero:H[m[1]],box:[cr.left-op.left-im.offsetParent.clientLeft,cr.top-op.top-im.offsetParent.clientTop,cr.width,cr.height],
          bw:[parseFloat(cs.borderLeftWidth)||0,parseFloat(cs.borderTopWidth)||0], round:cs.borderRadius.includes('50%')||parseFloat(cs.borderTopLeftRadius)>=cr.width*0.45});
      });
      const all=[...document.querySelectorAll('img')].length;
      return {res,count:imgs.length,all};
    },HEROES);
    await br.close();
  }
  console.log(JSON.stringify(out));
})();
