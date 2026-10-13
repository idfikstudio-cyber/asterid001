// usage: node render_overlay.js BASEURL OUTDIR FROM TO   -> composited frames OUTDIR/%05d.png (30 fps)
const { chromium } = require('playwright');
(async()=>{
  const [base,out,from,to]=process.argv.slice(2);const FPS=30;
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'}).catch(()=>chromium.launch());
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('pageerror',e=>console.error('pageerror',e.message));
  await p.goto(base+'/index.html?render');await p.waitForFunction(()=>window.__frame&&window.__ready);await p.evaluate(()=>window.__ready);
  for(let i=+from;i<+to;i++){
    const n=String(i).padStart(5,'0');
    await p.evaluate(([t,src])=>window.__frame(t,src),[i/FPS,`_frames/${n}.jpg`]);
    await p.screenshot({path:`${out}/${n}.png`,clip:{x:0,y:0,width:1080,height:1920}});
  }
  await b.close();
})();
