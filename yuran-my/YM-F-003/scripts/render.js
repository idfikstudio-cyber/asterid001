// Render overlay.html -> PNG berturutan (lutsinar). node render.js <plan.json> <outdir> <scale> [fps] [from] [to]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [planF, out, scale, fps = 30, from = 0, to] = process.argv.slice(2);
  const plan = JSON.parse(fs.readFileSync(planF));
  const sc = +scale, W = Math.round(1080 * sc), H = Math.round(1920 * sc);
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: W, height: H } });
  await pg.addInitScript(p => { window.PLAN = p; }, plan);
  await pg.goto('file://' + path.resolve(__dirname, '../overlay.html') + '?scale=' + sc);
  await pg.evaluate(() => window.ready);
  const N = Math.round(plan.duration * fps), a = +from, z = to ? +to : N;
  for (let i = a; i < z; i++) {
    await pg.evaluate(t => window.render(t), (i + .5) / fps);
    await pg.screenshot({ path: `${out}/${String(i).padStart(5, '0')}.png`, omitBackground: true });
  }
  await b.close();
})();
