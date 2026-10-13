// Render thumb.html variants to PNG/JPG. usage: node render.js dir/thumb.html outdir
const { chromium } = require('playwright');
(async()=>{const [f,out]=process.argv.slice(2);const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:1080,height:1920}});await p.goto('file://'+f);await p.evaluate(()=>document.fonts.ready);
 for(const v of [1,2,3]){await p.evaluate(v=>document.body.dataset.v=v,v);await p.waitForTimeout(300);
   await p.screenshot({path:`${out}/thumb_v${v}.png`});}
 await b.close();})();
