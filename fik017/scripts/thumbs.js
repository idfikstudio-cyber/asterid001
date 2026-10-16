const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path=require('path'),fs=require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--enable-unsafe-swiftshader'], proxy:{server:process.env.HTTPS_PROXY} });
  const p = await b.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 3 });
  p.on('pageerror', e => console.log('pageerror', e.message));
  await p.route('http://fik.local/**', r => { const f=path.join(process.env.ROOT, decodeURIComponent(new URL(r.request().url()).pathname));
    if(!fs.existsSync(f)) return r.fulfill({status:404,body:''});
    r.fulfill({status:200,body:fs.readFileSync(f),contentType:f.endsWith('.html')?'text/html; charset=utf-8':undefined}); });
  await p.goto('http://fik.local/index.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
  await p.evaluate(()=>{document.getElementById('bigplay').hidden=true;document.getElementById('phone').style.borderRadius='0'});
  const el = await p.$('#phone');
  for (const id of ['A','B','C']) {
    await p.evaluate(id=>{window.__thumb(id);window.__seek(0);document.getElementById('hint').hidden=true},id);
    await p.waitForTimeout(500);
    await el.screenshot({ path: `${process.argv[2]}/raw_${id}.png` });
  }
  await b.close();
})();
