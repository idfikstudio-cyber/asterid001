// Export the preview overlay layer (captions, motion, logo, end card) as transparent PNG frames.
// Serve preview/ over HTTP and open index.html#render. Opaque frames (end card) come out RGB: convert all to RGBA before ffmpeg.
// usage: node capture.js URL fonts.css outdir fps_num fps_den duration [t1,t2,...]
const { chromium } = require('playwright');const fs=require('fs');
(async()=>{const [url,fonts,out,num,den,dur,list]=process.argv.slice(2);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
p.on('pageerror',e=>console.log('pageerror',e.message));
await p.goto(url,{waitUntil:'domcontentloaded'});await p.addStyleTag({content:fs.readFileSync(fonts,'utf8')});
await p.waitForFunction(()=>window.__ready===true);await p.evaluate(()=>document.fonts.ready);
await p.evaluate(()=>Promise.all([...document.querySelectorAll('#phone img')].map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r}))));
const el=p.locator('#phone');
const times=list?list.split(',').map(Number):Array.from({length:Math.ceil(+dur*num/den)},(_, k)=>k*den/num);
for(let k=0;k<times.length;k++){await p.evaluate(t=>window.__frame(t),times[k]);
  await el.screenshot({path:`${out}/${list?'t_'+times[k]:String(k).padStart(5,'0')}.png`,omitBackground:true});
  if(!list&&k%100===0)console.log('frame',k,'/',times.length);}
await b.close();})();
