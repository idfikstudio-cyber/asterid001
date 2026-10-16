const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path=require('path'),fs=require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--enable-unsafe-swiftshader'], proxy:{server:process.env.HTTPS_PROXY} });
  const p = await b.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 3 });
  await p.route('http://fik.local/**', r => { const f=path.join(process.env.ROOT, decodeURIComponent(new URL(r.request().url()).pathname)); r.fulfill({status:200,body:fs.readFileSync(f)}); });
  await p.goto('http://fik.local/index.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
  const d = await p.evaluate(()=>{window.__seek(15);window.__pano(-8,-6);return document.querySelector('#pano canvas').toDataURL('image/jpeg',.9)});
  fs.writeFileSync(process.argv[2], Buffer.from(d.split(',')[1],'base64'));
  await b.close();
})();
