#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const {pathToFileURL} = require("node:url");
const {chromium} = require("playwright");

const [manifestPath, assetDir, tempDir] = process.argv.slice(2);
if (!manifestPath || !assetDir || !tempDir) {
  throw new Error("usage: validate_playback.cjs <manifest> <asset-dir> <temp-dir>");
}

const seek = async (page, timeSec) => {
  await page.evaluate(async (target) => {
    const video = document.querySelector("video");
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error("seek timeout")), 8000);
      const done = () => { clearTimeout(timeout); resolve(); };
      video.addEventListener("seeked", done, {once: true});
      video.currentTime = target;
      if (Math.abs(video.currentTime - target) < 0.002 && video.readyState >= 2) done();
    });
    video.pause();
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  }, timeSec);
};

(async () => {
  const entries = JSON.parse(fs.readFileSync(manifestPath, "utf8")).clips;
  const browser = await chromium.launch({
    headless: true,
    args: ["--allow-file-access-from-files", "--autoplay-policy=no-user-gesture-required"],
  });
  const page = await browser.newPage({viewport: {width: 1280, height: 720}});
  const probe = path.join(tempDir, "probe.html");
  for (const entry of entries) {
    const source = pathToFileURL(path.join(assetDir, entry.file)).href;
    fs.writeFileSync(probe, `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:1280px;height:720px;background:#f8fafc;overflow:hidden}video{display:block;width:1280px;height:720px;object-fit:contain}</style><video src="${source}" autoplay muted loop playsinline></video>`);
    await page.goto(pathToFileURL(probe).href, {waitUntil: "load"});
    await page.waitForFunction(() => document.querySelector("video").readyState >= 2);
    await page.locator("video").evaluate((video) => video.play());
    const start = await page.locator("video").evaluate((video) => video.currentTime);
    await page.waitForTimeout(650);
    const state = await page.locator("video").evaluate((video) => ({time: video.currentTime, paused: video.paused}));
    if (state.paused || state.time - start < 0.25) {
      throw new Error(`${entry.file}: autoplay/currentTime failed (${start.toFixed(3)}->${state.time.toFixed(3)})`);
    }
    await seek(page, 0.001);
    await page.locator("video").screenshot({path: path.join(tempDir, `${entry.file}.first.png`)});
    await seek(page, Math.max(0.001, entry.durationSec - 0.05));
    await page.locator("video").screenshot({path: path.join(tempDir, `${entry.file}.last.png`)});
    process.stdout.write(`PLAYBACK PASS ${entry.file}: autoplay currentTime=${start.toFixed(3)}->${state.time.toFixed(3)}s\n`);
  }
  await browser.close();
})().catch((error) => {
  process.stderr.write(`PLAYBACK FAIL: ${error.stack || error}\n`);
  process.exitCode = 1;
});
