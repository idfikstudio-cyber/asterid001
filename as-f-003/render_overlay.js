// Render lapisan grafik sebagai PNG lutsinar, satu fail setiap bingkai.
// usage: node render_overlay.js timeline.json face.png outdir width [fps | t1,t2,...]
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
(async () => {
  const [tlPath, face, out, width, arg = "30"] = process.argv.slice(2);
  const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
  const W = +width, Hh = Math.round(W * 16 / 9), s = W / 1080;
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: Hh } });
  await page.goto("file://" + path.resolve(__dirname, "overlay.html"));
  const faceUrl = "data:image/png;base64," + fs.readFileSync(face).toString("base64");
  await page.evaluate(([t, f, sc]) => { setScale(sc); return init(t, f); }, [tl, faceUrl, s]);
  await page.waitForTimeout(500);
  const times = arg.includes(",") || arg.includes(".") ? arg.split(",").map(Number) : null;
  const fps = times ? 0 : +arg, n = times ? times.length : Math.round(tl.dur * fps);
  for (let i = 0; i < n; i++) {
    const t = times ? times[i] : i / fps;
    await page.evaluate(t => renderAt(t), t);
    await page.screenshot({ path: path.join(out, times ? `t${t.toFixed(2)}.png` : `${String(i).padStart(5, "0")}.png`), omitBackground: true });
    if (!times && i % 300 === 0) console.log("frame", i, "/", n);
  }
  await browser.close();
})();
