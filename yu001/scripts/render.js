const {chromium}=require('playwright');
(async()=>{
 const [from,to,dir]=[+process.argv[2],+process.argv[3],process.argv[4]];
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('http://127.0.0.1:8767/index.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1500);
 const ph=p.locator('#phone');
 for(let i=from;i<to;i++){
   await p.evaluate(t=>window.renderAt(t),i/30);
   await ph.screenshot({path:`${dir}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:95});
   if(i%100==0)console.log(i,new Date().toISOString());
 }
 await b.close();
})();
