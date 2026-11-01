// Mockup lokal rendern: node shoot.js Board.dc.html out.png [scale] [js-to-run-before]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
// MOCKUP_DIR: Ordner mit den heruntergeladenen Mockups (project/*.dc.html) und ihren Bildern (<id>.webp)
const P=(process.env.MOCKUP_DIR||'')+'/';
const M=__dirname+'/';
const FONTS=path.join(__dirname,'../../game/fonts')+'/';
module.exports.open=async function(board,scale){
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:scale||1});
  await p.route('**/*',r=>{const u=new URL(r.request().url());
    if(u.pathname.startsWith('/_blob/')){const id=u.pathname.split('/').pop();const f=fs.readdirSync(P).find(x=>x.startsWith(id));return f?r.fulfill({body:fs.readFileSync(P+f),contentType:f.endsWith('webp')?'image/webp':'image/png'}):r.fulfill({status:404,body:''});}
    if(u.pathname.endsWith('support.js'))return r.fulfill({body:fs.readFileSync(M+'dcrt.js'),contentType:'text/javascript'});
    if(u.pathname.endsWith('.woff2'))return r.fulfill({body:fs.readFileSync(FONTS+path.basename(u.pathname)),contentType:'font/woff2'});
    if(u.pathname.endsWith('fonts.css'))return r.fulfill({body:fs.readFileSync(M+'fonts.css'),contentType:'text/css'});
    if(u.hostname==='mock.local'){let h=fs.readFileSync(P+'project/'+path.basename(u.pathname),'utf8');h=h.replace('<head>','<head><link rel="stylesheet" href="/fonts.css">');return r.fulfill({body:h,contentType:'text/html'});}
    return r.fulfill({status:404,body:''});});
  await p.goto('http://mock.local/'+board);await p.waitForFunction(()=>window.__dcReady);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
  return {b,p};
};
if(require.main===module){(async()=>{const [board,out,scale]=process.argv.slice(2);const {b,p}=await module.exports.open(board,+scale||1);await p.screenshot({path:out});await b.close();})();}
