const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:1200,height:1000}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(1500);
 await p.evaluate(()=>document.querySelector('#bigplay').hidden=true);
 const T=process.argv.slice(2).map(Number);
 for(const t of T){
   await p.evaluate(t=>{const s=document.querySelector('#scrub');s.value=t;s.dispatchEvent(new Event('input'))},t);
   await p.waitForTimeout(700);
   await p.locator('#phone').screenshot({path:`/tmp/claude-0/-home-user-asterid001/0b042463-1b52-5621-b3f6-ae06b3007c09/scratchpad/shots/t${t}.png`});
 }
 await p.screenshot({path:'/tmp/claude-0/-home-user-asterid001/0b042463-1b52-5621-b3f6-ae06b3007c09/scratchpad/shots/page.png'});
 console.log('errors:',errs);await b.close();
})();
