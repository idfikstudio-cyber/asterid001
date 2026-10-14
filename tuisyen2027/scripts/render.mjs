// Render compose.html frame demi frame -> JPEG.  node render.mjs <framesDir> <outDir> [t1,t2,...]
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';
const [,,FR,OUT,TS]=process.argv; fs.mkdirSync(OUT,{recursive:true});
const NF=fs.readdirSync(FR).filter(f=>f.endsWith('.jpg')).length;
const FPS=30000/1001, DUR=14.4;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--allow-file-access-from-files']}).catch(()=>chromium.launch({args:['--allow-file-access-from-files']}));
const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
p.on('console',m=>console.log('page:',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+path.resolve('compose.html')+'?frames=file://'+path.resolve(FR)+'&nf='+NF);
await p.evaluate(()=>window.READY);
const times=TS?TS.split(',').map(Number):[...Array(Math.round(DUR*FPS)).keys()].map(i=>i/FPS);
for(let i=0;i<times.length;i++){
  await p.evaluate(t=>render(t),times[i]);
  await p.screenshot({path:path.join(OUT,(TS?'t'+times[i].toFixed(2):String(i+1).padStart(4,'0'))+'.jpg'),type:'jpeg',quality:93});
  if(!TS&&i%60==0)console.log(i,'/',times.length);
}
await b.close();
