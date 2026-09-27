#!/usr/bin/env node
// Opens LAB003 GitHub page + Docker Hub in a headed Chrome through a SOCKS5 proxy.
// Runs on the macOS host with NODE_PATH pointing at a bundled playwright.
// No screenshots, no login, no persistent user profile. Ctrl+C (SIGINT) to exit.
'use strict';

const { chromium } = require('playwright');

const URLS = [
  'https://github.com/Tuchsanai/DevTools/tree/main/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push',
  'https://hub.docker.com/',
];

let browser = null;
let closing = false;

async function shutdown(code) {
  if (closing) return;
  closing = true;
  try {
    if (browser) await browser.close();
  } catch (err) {
    console.error('[close] error:', err && err.message ? err.message : err);
  }
  process.exit(code);
}

process.on('SIGINT', () => {
  console.log('[signal] SIGINT received, closing browser');
  shutdown(0);
});

async function openTab(context, url, idx) {
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const title = await page.title();
    console.log(`[tab ${idx}] title=${JSON.stringify(title)} url=${page.url()}`);
  } catch (err) {
    console.error(`[tab ${idx}] error url=${url}:`, err && err.message ? err.message : err);
  }
  return page;
}

(async () => {
  try {
    browser = await chromium.launch({
      channel: 'chrome',
      headless: false,
      proxy: { server: 'socks5://127.0.0.1:18999' },
    });
    browser.on('disconnected', () => {
      if (!closing) {
        console.log('[browser] disconnected');
        closing = true;
        process.exit(0);
      }
    });

    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

    for (let i = 0; i < URLS.length; i++) {
      await openTab(context, URLS[i], i + 1);
    }

    console.log('[ready] browser open; press Ctrl+C to exit');
    // Keep the process alive until SIGINT.
    setInterval(() => {}, 1 << 30);
  } catch (err) {
    console.error('[launch] error:', err && err.message ? err.message : err);
    await shutdown(1);
  }
})();
