#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const pw = require('/usr/local/lib/node_modules/@playwright/mcp/node_modules/playwright-core');
const input = path.resolve(process.argv[2]);
const output = path.resolve(process.argv[3]);
const files = fs.readdirSync(input).filter(f => /^s\d{3}\.png$/.test(f)).sort();
(async () => {
  fs.mkdirSync(output, {recursive:true});
  const browser = await pw.chromium.launch();
  const page = await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
  for (let start=0; start<files.length; start+=16) {
    const group = files.slice(start,start+16);
    const cells = group.map(f => `<figure><img src="file://${path.join(input,f)}"><b>${f.slice(1,4)}</b></figure>`).join('');
    const tempHtml = path.join(output, '.contact.html');
    fs.writeFileSync(tempHtml, `<style>*{box-sizing:border-box}body{margin:0;background:#0e0e11}.g{display:grid;grid-template-columns:repeat(4,320px);grid-auto-rows:180px}figure{position:relative;margin:0;border:2px solid #27272a;overflow:hidden;background:#18181b}img{width:100%;height:100%;object-fit:contain;display:block}b{position:absolute;left:6px;top:6px;padding:2px 6px;border-radius:4px;background:rgba(0,0,0,.78);color:white;font:12px monospace}</style><div class="g">${cells}</div>`);
    await page.goto('file://' + tempHtml,{waitUntil:'load'});
    await page.waitForTimeout(200);
    await page.screenshot({path:path.join(output,`contact-${String(start/16+1).padStart(2,'0')}.png`)});
  }
  fs.rmSync(path.join(output, '.contact.html'), {force:true});
  await browser.close();
})();
