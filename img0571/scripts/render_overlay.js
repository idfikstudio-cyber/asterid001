// Render the preview's graphics + captions as transparent 1080x1920 PNG frames.
// usage: node render_overlay.js http://localhost:PORT/index.html outdir duration [from] [to]
const { chromium } = require('playwright');
(async()=>{
  const [url,out,dur,from,to]=process.argv.slice(2);const FPS=30000/1001;
  const n=Math.round(+dur*FPS),a=+(from||0),b=+(to||n);
  const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto(url+'#render');await p.waitForFunction(()=>window.renderAt&&document.fonts.status==='loaded');
  await p.evaluate(()=>document.fonts.ready);
  for(let i=a;i<b;i++){
    await p.evaluate(t=>window.renderAt(t),i/FPS);
    await p.screenshot({path:`${out}/o${String(i).padStart(5,'0')}.png`,omitBackground:true,clip:{x:0,y:0,width:1080,height:1920}});
  }
  await br.close();
})();
