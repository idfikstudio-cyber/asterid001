// Captures the preview's live graphics as transparent 1080x1920 PNG frames,
// plus zoom.json (face punch-in per frame) for final.py.
// usage: node render_overlay.js <preview url> <outdir> [fps=30] [workers=3]
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs'), path = require('path');
const [url, out, fpsArg, wArg] = process.argv.slice(2);
const FPS = +(fpsArg || 30), WORKERS = +(wArg || 3);
const CSS = `
  html,body{background:transparent!important}
  body *{visibility:hidden}
  .phone,.phone .ov,.phone .ov *{visibility:visible}
  .phone .ov [style*="opacity: 0"],.phone .ov .g[style*="opacity: 0"] *{visibility:hidden}
  .phone{position:fixed!important;left:0;top:0;width:1080px!important;max-width:none!important;height:1920px;border-radius:0!important;background:transparent!important;box-shadow:none!important}
  .stage,.bigplay,.safe,.wipe{display:none!important}
  *{transition:none!important;animation:none!important}`;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const open = async () => {
    const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto(url); await p.waitForFunction(() => window.asterFrame);
    await p.addStyleTag({ content: CSS }); await p.evaluate(() => document.fonts.ready);
    return p;
  };
  const pages = await Promise.all(Array.from({ length: WORKERS }, open));
  const dur = await pages[0].evaluate(() => +document.getElementById('scrub').max);
  const n = Math.round(dur * FPS), zoom = new Array(n);
  let next = 0, done = 0;
  await Promise.all(pages.map(async p => {
    while (next < n) {
      const i = next++;
      zoom[i] = await p.evaluate(t => window.asterFrame(t), i / FPS);
      await p.screenshot({ path: path.join(out, `o_${String(i).padStart(5, '0')}.png`), omitBackground: true, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
      if (++done % 150 === 0) console.log(`${done}/${n}`);
    }
  }));
  fs.writeFileSync(path.join(out, 'zoom.json'), JSON.stringify(zoom));
  console.log('done', n); await browser.close();
})();
