// Render thumb.html -> PNG 1080x1920 + versi 4:5 (grid IG).  node thumb.mjs <outDir>
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import path from 'path';
const OUT=process.argv[2];
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve('thumb.html')); await p.evaluate(()=>window.READY);
await p.screenshot({path:path.join(OUT,'Thumbnail_9x16.png')});
await p.screenshot({path:path.join(OUT,'Thumbnail_4x5.png'),clip:{x:0,y:285,width:1080,height:1350}});
await b.close();
