const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require(process.argv[2] || 'sharp');
(async()=>{
 const root=__dirname;
 await fs.mkdir(path.join(root,'ui_png'),{recursive:true});
 const files=(await fs.readdir(path.join(root,'ui'))).filter(x=>x.endsWith('.svg'));
 for(const name of files){await sharp(path.join(root,'ui',name)).withIccProfile('srgb').png().toFile(path.join(root,'ui_png',name.replace('.svg','.png')));}
 if(process.argv[3])await sharp(process.argv[3]).withIccProfile('srgb').png().toFile(path.join(root,'helden_modular_vorschau.png'));
 process.stdout.write(JSON.stringify({gerasterte_bauteile:files.length,vorschau:!!process.argv[3]}));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1});
