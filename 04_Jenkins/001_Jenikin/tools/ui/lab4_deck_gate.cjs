#!/usr/bin/env node
"use strict";

const path = require("node:path");
const {createRequire} = require("node:module");
const {pathToFileURL} = require("node:url");

const root = path.resolve(__dirname, "../..");
const motionRequire = createRequire(path.join(root, "tools/motion/package.json"));
const {chromium} = motionRequire("playwright");
const deck = path.join(root, "Jenkins_CICD_Docker_Slides.html");
const logs = path.join(root, "logs");
const captureReview = process.env.CAPTURE_DECK_REVIEW === "1";

const check = (condition, label) => {
  if (!condition) throw new Error(label);
  process.stdout.write(`[PASS] ${label}\n`);
};

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--autoplay-policy=no-user-gesture-required"],
  });
  const context = await browser.newContext({viewport: {width: 1280, height: 720}});
  const external = [];
  const consoleErrors = [];
  await context.route("**/*", async (route) => {
    const url = route.request().url();
    if (/^https?:/i.test(url)) {
      external.push(url);
      await route.abort();
    } else {
      await route.continue();
    }
  });
  const page = await context.newPage();
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  const uri = pathToFileURL(deck).href;
  await page.goto(`${uri}#page-103`, {waitUntil: "load"});
  check(await page.locator(".slot").count() === 198, "single-file deck has 198 pages");
  check((await page.locator("#counter").innerText()) === "103/198", "LAB 4 overview page number is 103/198");
  check(await page.locator(".diagram svg").count() === 19, "19 inline SVG diagrams are embedded");
  check(await page.locator("video").count() === 4, "4 Remotion videos are embedded as data URIs");
  check(await page.locator('video[src^="data:video/mp4;base64,"]').count() === 4, "every video uses a data URI");
  check(await page.locator('img[data-embedded-from="slides_assets/lab4_s10_dockerhub_sha_tags.png"]').count() === 1, "Docker Hub evidence is embedded once");
  check(await page.locator('img[data-embedded-from="slides_assets/lab4_s06_manual_build_console.png"]').count() === 1, "Jenkins console evidence is embedded once");
  await page.goto(`${uri}#page-104`, {waitUntil: "load"});
  check(await page.locator(".slot.active .diagram svg text").count() >= 10, "LAB 4 architecture is editable inline SVG text");
  if (captureReview) await page.screenshot({path: path.join(logs, "lab4_slide_architecture.png")});
  await page.goto(`${uri}#page-105`, {waitUntil: "load"});
  const active = page.locator('video[data-composition="mo-lab4-sha-digest"]');
  await page.waitForFunction(() => {
    const video = document.querySelector('video[data-composition="mo-lab4-sha-digest"]');
    return video && !video.paused && video.currentTime > 0.15;
  });
  check(await active.evaluate((video) => !video.paused && video.muted), "LAB 4 video autoplays muted on its active slide");
  check(await page.locator("video").evaluateAll((videos) => videos.filter((video) => !video.paused).length === 1), "only the active slide video is playing");
  if (captureReview) await page.screenshot({path: path.join(logs, "lab4_slide_video.png")});
  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(200);
  check(await active.evaluate((video) => video.paused), "LAB 4 video pauses after leaving its slide");
  await page.goto(`${uri}#page-114`, {waitUntil: "load"});
  if (captureReview) await page.screenshot({path: path.join(logs, "lab4_slide_console.png")});
  check(external.length === 0, "offline deck makes zero external HTTP requests");
  check(consoleErrors.length === 0, "deck emits zero browser console errors");
  await browser.close();
  process.stdout.write("LAB4_DECK_GATE: PASS\n");
})().catch((error) => {
  process.stderr.write(`LAB4_DECK_GATE: FAIL: ${error.stack || error}\n`);
  process.exitCode = 1;
});
