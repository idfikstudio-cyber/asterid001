// Frame-exact render: drives the preview page's render(t) and pipes 1080x1920 PNG frames into ffmpeg.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path=require('path'),fs=require('fs'),{spawn}=require('child_process');
(async () => {
  const [root,out,fps,from,to]=[process.env.ROOT,process.argv[2],+(process.argv[3]||30),+(process.argv[4]||0),process.argv[5]];
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--use-gl=swiftshader','--enable-unsafe-swiftshader'], proxy:{server:process.env.HTTPS_PROXY} });
  const p = await b.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 3 });
  p.on('pageerror', e => console.log('pageerror', e.message));
  await p.route('http://fik.local/**', r => { const f=path.join(root, decodeURIComponent(new URL(r.request().url()).pathname));
    if(!fs.existsSync(f)) return r.fulfill({status:404,body:''});
    r.fulfill({status:200,body:fs.readFileSync(f),contentType:f.endsWith('.html')?'text/html; charset=utf-8':undefined}); });
  await p.goto('http://fik.local/index.html', { waitUntil: 'networkidle' });
  await p.addStyleTag({content:`#phone{position:fixed!important;left:0!important;top:0!important;z-index:999;width:360px!important;height:640px!important;aspect-ratio:auto!important;max-width:none!important;border-radius:0!important;box-shadow:none!important}.player{max-width:none!important;position:static!important}#hint,#bigplay{display:none!important}.caps span{transition:none!important}`});
  await p.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
  await p.waitForTimeout(1500);
  const P=JSON.parse(fs.readFileSync(path.join(root,'plan.json')));
  const end=to?+to:P.dur, n=Math.round((end-from)*fps);
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-r',String(fps),out],{stdio:['pipe','inherit','inherit']});
  const el=await p.$('#phone'); const t0=Date.now();
  for(let i=0;i<n;i++){ const t=from+i/fps;
    await p.evaluate(t=>window.__renderFrame(t),t);
    const buf=await p.screenshot({type:"png",clip:{x:0,y:0,width:360,height:640}});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%150===0) console.log(`frame ${i}/${n} t=${t.toFixed(2)} ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');
})();
