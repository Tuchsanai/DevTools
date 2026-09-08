// keeps a headless browser tab open on the Excalidraw canvas so export/screenshot work without a human browser
const pw = require('/usr/local/lib/node_modules/@playwright/mcp/node_modules/playwright-core');
(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1800, height: 1100 } });
  await p.goto(process.env.EXPRESS_SERVER_URL || 'http://127.0.0.1:8893', { waitUntil: 'networkidle' });
  console.log('excalidraw tab open on', p.url());
  setInterval(() => {}, 1e6);
})().catch(e => { console.error(e); process.exit(1); });
