const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const [out, ...ts] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-certificate-errors'], proxy: {server:process.env.HTTPS_PROXY,bypass:'<-loopback>'} });
  const p = await b.newPage({ viewport: { width: 1200, height: 900 }, ignoreHTTPSErrors:true });
  const path=require('path'),fs=require('fs');
  await p.route('http://fik.local/**', r => { const u=new URL(r.request().url()); const f=path.join(process.env.ROOT, decodeURIComponent(u.pathname));
    const ext=path.extname(f).slice(1); const ct={html:'text/html; charset=utf-8',json:'application/json',jpg:'image/jpeg',png:'image/png',mp4:'video/mp4',mp3:'audio/mpeg'}[ext]||'application/octet-stream';
    r.fulfill({status:200,body:fs.readFileSync(f),contentType:ct}); });
  p.on('console', m => console.log('console', m.type(), m.text()));
  p.on('response', r => { if (r.status()>=400) console.log('bad', r.status(), r.url()) });
  p.on('pageerror', e => console.log('pageerror', e.message));
  await p.goto('http://fik.local/index.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  await p.evaluate(()=>{document.getElementById('bigplay').hidden=true});
  const el = await p.$('#phone');
  for (const t of ts) {
    await p.evaluate(t => window.__seek(+t), t);
    await p.waitForTimeout(700);
    await el.screenshot({ path: `${out}/t${t}.png` });
  }
  await p.screenshot({ path: `${out}/page.png`, fullPage: false });
  await b.close();
})();
