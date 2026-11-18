// Renders index.html frame-by-frame to JPEGs: node render.js <outDir> [fps] [duration_s] [only_times_csv]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const out = process.argv[2] || 'frames';
  const fps = +(process.argv[3] || 30);
  const dur = +(process.argv[4] || 20);
  const only = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const times = only || Array.from({ length: Math.round(fps * dur) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(ms => window.seek(ms), times[i] * 1000);
    const name = only ? `t_${times[i]}.jpg` : `f_${String(i).padStart(4, '0')}.jpg`;
    await page.screenshot({ path: path.join(out, name), type: 'jpeg', quality: 93 });
    if (!only && i % 60 === 0) console.log(`frame ${i}/${times.length}`);
  }
  await browser.close();
})();
