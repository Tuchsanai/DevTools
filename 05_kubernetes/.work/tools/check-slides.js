#!/usr/bin/env node
// check-slides.js <file.html> [--shots outdir]  — opens the slide deck offline with Playwright and verifies:
// slide count, every <img> loaded (naturalWidth>0), no external http(s) src/href/@import, keyboard nav (ArrowRight/Left, Space, Home, End, O, F, ?, Esc), hash sync
const pw = require('/usr/local/lib/node_modules/@playwright/mcp/node_modules/playwright-core');
const fs = require('fs'), path = require('path');
const file = process.argv[2]; if (!file) { console.error('usage: node check-slides.js <file.html> [--shots dir]'); process.exit(2); }
const si = process.argv.indexOf('--shots'); const shots = si > -1 ? process.argv[si + 1] : null;
(async () => {
  const html = fs.readFileSync(file, 'utf8');
  const ext = (html.match(/(src|href)=["']https?:\/\/[^"']+/g) || []).filter(m => !/href=["']https?:\/\/(github\.com|kubernetes\.io|hub\.docker\.com|www\.)/.test(m));
  const imports = html.match(/@import\s+url\(\s*["']?https?:/g) || [];
  const b = await pw.chromium.launch({ args: ['--allow-file-access-from-files'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, offline: true });
  const p = await ctx.newPage();
  const errors = []; p.on('pageerror', e => errors.push(e.message)); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await p.goto('file://' + path.resolve(file), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const total = await p.evaluate(() => document.querySelectorAll('section.slide').length);
  const imgs = await p.evaluate(() => [...document.images].map(i => ({ a: i.getAttribute('data-a') || i.getAttribute('src')?.slice(0, 40), ok: i.complete && i.naturalWidth > 0, alt: i.alt })));
  const broken = imgs.filter(i => !i.ok), noAlt = imgs.filter(i => !i.alt);
  const cur = async () => p.evaluate(() => (document.querySelector('.slide.active, .slide.current, .slot.active .slide, section.slide.on') || {}).id || location.hash || document.querySelector('.pg, #pg, .counter')?.textContent?.trim());
  const nav = {};
  const h0 = await cur(); await p.keyboard.press('ArrowRight'); await p.waitForTimeout(250); nav.right = (await cur()) !== h0;
  const h1 = await cur(); await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(250); nav.left = (await cur()) !== h1;
  const h2 = await cur(); await p.keyboard.press('Space'); await p.waitForTimeout(250); nav.space = (await cur()) !== h2;
  await p.keyboard.press('End'); await p.waitForTimeout(250); nav.end = await cur();
  await p.keyboard.press('Home'); await p.waitForTimeout(250); nav.home = await cur();
  await p.keyboard.press('o'); await p.waitForTimeout(400); nav.overviewVisible = await p.evaluate(() => { const o = document.querySelector('#ov, #overview, .overview, [data-overview]'); return !!o && getComputedStyle(o).display !== 'none' && getComputedStyle(o).visibility !== 'hidden'; });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  await p.keyboard.press('?'); await p.waitForTimeout(400); nav.helpVisible = await p.evaluate(() => { const o = document.querySelector('#help, .help, [data-help], .shortcuts'); return !!o && getComputedStyle(o).display !== 'none' && getComputedStyle(o).visibility !== 'hidden'; });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  nav.hash = await p.evaluate(() => location.hash);
  nav.hasProgressBar = await p.evaluate(() => !!document.querySelector('#bar, .progress, .bar'));
  nav.hasCounter = await p.evaluate(() => !!document.querySelector('#counter, #cur, .counter'));
  nav.hasControls = await p.evaluate(() => !!document.querySelector('#ctl, .ctl, .controls'));
  const labRefs = [...new Set((html.match(/\b0\d\d-[a-z0-9-]+(\/README\.md)?/g) || []).map(s => s.split('/')[0]))];
  if (shots) { fs.mkdirSync(shots, { recursive: true }); await p.keyboard.press('Home'); for (let i = 0; i < total; i++) { await p.screenshot({ path: path.join(shots, `s${String(i + 1).padStart(3, '0')}.png`) }); await p.keyboard.press('ArrowRight'); await p.waitForTimeout(150); } }
  console.log(JSON.stringify({ file: path.basename(file), sizeMB: +(fs.statSync(file).size / 1048576).toFixed(1), slides: total, images: imgs.length, brokenImages: broken.slice(0, 10), imagesWithoutAlt: noAlt.length, externalRefs: ext.slice(0, 10), externalImports: imports.length, nav, labFoldersReferenced: labRefs, pageErrors: errors.slice(0, 5) }, null, 1));
  await b.close();
})().catch(e => { console.error('check FAILED:', e.message); process.exit(1); });
