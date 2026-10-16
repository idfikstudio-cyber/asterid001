// Capture the preview's overlay layer (captions, motion, b-roll, cards) as transparent 1080x1920 PNGs, one per frame.
// usage: PW=<playwright module> node at001_overlay.js http://localhost:8765/index.html#render outdir fps total_seconds
const {chromium}=require(process.env.PW);
const [url,out,fps,total]=process.argv.slice(2);
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(url);await p.waitForFunction(()=>window.renderAt&&window.renderReady);await p.evaluate(()=>window.renderReady);
  const n=Math.round(+total*+fps);
  for(let i=0;i<n;i++){
    await p.evaluate(t=>window.renderAt(t),i/ +fps);
    await p.screenshot({path:`${out}/o${String(i).padStart(5,'0')}.png`,omitBackground:true});
    if(i%100===0)console.log('frame',i,'/',n);
  }
  console.log('done',n,'errors',JSON.stringify(errs));await b.close();
})();
