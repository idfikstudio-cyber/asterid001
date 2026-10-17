const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const k of ['A','B','C']){await p.goto('file://'+process.argv[2]+`/cover_${k}.html`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
const f=await p.evaluate(()=>document.fonts.check('900 40px Lexend'));console.log(k,'font',f);
await p.screenshot({path:process.argv[2]+`/YU001_cover_${k}.jpg`,type:'jpeg',quality:93})}
await b.close()})();
