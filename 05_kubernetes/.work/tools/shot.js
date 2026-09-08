#!/usr/bin/env node
// shot.js — capture a real screenshot of a running web page (host-side Playwright)
// usage: node shot.js <url> <out.png> [--w 1280] [--h 800] [--full] [--wait 1500] [--selector "css"] [--reload N]
//   --reload N : reload the page N times before capturing (useful to land on a different Pod)
const pw = require('/usr/local/lib/node_modules/@playwright/mcp/node_modules/playwright-core');
const a = process.argv.slice(2);
const url = a[0], out = a[1];
if (!url || !out) { console.error('usage: node shot.js <url> <out.png> [--w 1280] [--h 800] [--full] [--wait ms] [--selector css] [--reload N]'); process.exit(2); }
const opt = (k, d) => { const i = a.indexOf(k); return i > -1 ? a[i + 1] : d; };
const W = +opt('--w', 1280), H = +opt('--h', 800), wait = +opt('--wait', 1500), sel = opt('--selector', null), reload = +opt('--reload', 0);
const full = a.includes('--full');
(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  try { await p.goto(url, { waitUntil: 'networkidle', timeout: 30000 }); }
  catch (e) { await p.goto(url, { waitUntil: 'load', timeout: 30000 }); }
  for (let i = 0; i < reload; i++) { await p.reload({ waitUntil: 'load' }); await p.waitForTimeout(300); }
  await p.waitForTimeout(wait);
  if (sel) { const el = await p.waitForSelector(sel, { timeout: 15000 }); await el.screenshot({ path: out }); }
  else await p.screenshot({ path: out, fullPage: full });
  console.log(JSON.stringify({ ok: true, out, title: await p.title(), url: p.url() }));
  await b.close();
})().catch(e => { console.error('shot FAILED:', e.message); process.exit(1); });
