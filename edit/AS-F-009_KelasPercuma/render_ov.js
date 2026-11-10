// usage: node render_ov.js <html> <W> <fps> <dur> <outdir> [t1,t2,...]  -> writes PNG frames (or stills)
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [html,W,fps,dur,out,stills]=process.argv.slice(2);const w=+W,h=Math.round(w*16/9),s=w/1080;
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:w,height:h}});
 await p.goto('file://'+html);await p.evaluate(s=>scaleStage(s),s);await p.evaluate(()=>document.fonts.ready);
 await p.waitForTimeout(300);
 const ts=stills?stills.split(',').map(Number):[...Array(Math.round(+dur*+fps)).keys()].map(i=>i/+fps);
 fs.mkdirSync(out,{recursive:true});
 for(let i=0;i<ts.length;i++){await p.evaluate(t=>render(t),ts[i]);
   await p.screenshot({path:`${out}/${stills?'s_'+ts[i]:String(i).padStart(5,'0')}.png`,omitBackground:true});}
 await b.close();})();
