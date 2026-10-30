// Render lapisan grafik ke PNG lutsinar setiap frame. usage: node render_overlay.js plan.json outdir width fps [t0 t1]
const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const [plan,out,W,FPS,T0,T1]=[process.argv[2],process.argv[3],+process.argv[4],+process.argv[5],process.argv[6],process.argv[7]];
  const P=JSON.parse(fs.readFileSync(plan));fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch();const pg=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:W/540});
  await pg.goto('file://'+path.resolve(__dirname,'overlay.html'));await pg.evaluate(p=>setPlan(p),P);
  await pg.evaluate(()=>document.fonts.ready);await pg.evaluate(()=>{draw(0.5);draw(90)});
  await pg.waitForTimeout(300);
  const n0=T0?Math.round(+T0*FPS):0,n1=T1?Math.round(+T1*FPS):Math.round(P.duration*FPS);
  for(let n=n0;n<n1;n++){await pg.evaluate(t=>draw(t),n/FPS);
    await pg.screenshot({path:path.join(out,String(n).padStart(5,'0')+'.png'),omitBackground:true});}
  await b.close();
})();
