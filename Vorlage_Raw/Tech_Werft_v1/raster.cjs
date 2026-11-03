const fs=require('node:fs/promises'),path=require('node:path');
const sharp=require(process.argv[2]||'sharp');
(async()=>{const out=path.join(__dirname,'ui_png');await fs.mkdir(out,{recursive:true});const names=(await fs.readdir(path.join(__dirname,'ui'))).filter(x=>x.endsWith('.svg'));for(const name of names)await sharp(path.join(__dirname,'ui',name)).withIccProfile('srgb').png().toFile(path.join(out,name.replace('.svg','.png')));process.stdout.write(JSON.stringify({bauteile:names.length}));})().catch(e=>{process.stderr.write(String(e));process.exitCode=1});
