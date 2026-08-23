#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const {createRequire} = require("node:module");
const {pathToFileURL} = require("node:url");
const root = path.resolve(__dirname, "../..");
const {chromium} = createRequire(path.join(root, "tools/motion/package.json"))("playwright");
const deck = path.join(root, "Jenkins_CICD_Docker_Slides.html");
const source = fs.readFileSync(path.join(root, "tools/slides_src.html"), "utf8");
const expectedAssets = [...source.matchAll(/data-asset="([^"]+)"/g)].map((match) => match[1]);
const compositions = new Set(["mo-dood-socket", "mo-lab4-sha-digest", "mo-polling-vs-webhook", "mo-pipeline-flow"]);
const requiredLab4 = ["lab4_s03_github_repo_files.png", "lab4_s05_jenkins_scm_config.png", "lab4_s06_manual_build_console.png", "lab4_s07_poll_scm_trigger.png", "lab4_s09_scm_build_cause.png", "lab4_s10_dockerhub_sha_tags.png"].map((name) => `slides_assets/${name}`);
const check = (condition, label) => { if (!condition) throw new Error(label); process.stdout.write(`[deck][PASS] ${label}\n`); };
(async () => {
  check(expectedAssets.length === 71, "source declares 71 embedded assets (67 screenshots + 4 videos)");
  check(requiredLab4.every((asset) => expectedAssets.includes(asset)), "source declares the current LAB 4 evidence set");
  check(!expectedAssets.some((asset) => /deck_lab4_/i.test(asset)), "source has no legacy LAB 4 deck captures");
  const browser = await chromium.launch({headless: true, args: ["--autoplay-policy=no-user-gesture-required"]});
  const context = await browser.newContext({viewport: {width: 1280, height: 720}});
  const external = [], consoleErrors = [], pageErrors = [];
  await context.route("**/*", async (route) => { if (/^https?:/i.test(route.request().url())) { external.push(route.request().url()); await route.abort(); } else await route.continue(); });
  const page = await context.newPage();
  page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => pageErrors.push(String(error)));
  const uri = pathToFileURL(deck).href;
  await page.goto(uri, {waitUntil: "load"});
  check(await page.locator(".slot").count() === 198, "page count = 198");
  check(await page.locator("#counter").innerText() === "1/198", "initial counter is 1/198");
  check(await page.locator(".diagram svg").count() === 19, "19 inline SVG diagrams");
  check(await page.locator("img[data-embedded-from]").count() === 67, "67 embedded screenshots");
  check(await page.locator("video").count() === 4, "4 embedded Remotion videos");
  check(await page.locator('video[src^="data:video/mp4;base64,"]').count() === 4, "all videos use data URIs");
  const actualAssets = await page.locator("[data-embedded-from]").evaluateAll((elements) => elements.map((element) => element.dataset.embeddedFrom));
  check(JSON.stringify(actualAssets) === JSON.stringify(expectedAssets), "built asset order exactly matches source");
  const actualCompositions = new Set(await page.locator("video").evaluateAll((videos) => videos.map((video) => video.dataset.composition)));
  check([...compositions].every((id) => actualCompositions.has(id)) && actualCompositions.size === 4, "composition IDs match the motion manifest contract");
  const duplicateIds = await page.evaluate(() => { const seen = new Set(), duplicate = new Set(); document.querySelectorAll("[id]").forEach((el) => seen.has(el.id) ? duplicate.add(el.id) : seen.add(el.id)); return [...duplicate]; });
  check(duplicateIds.length === 0, "0 duplicate element IDs");
  const unresolved = await page.evaluate(() => [...document.querySelectorAll("[marker-end]")].map((el) => el.getAttribute("marker-end").slice(5, -1)).filter((id) => !document.getElementById(id)));
  check(unresolved.length === 0, "every SVG marker-end resolves");
  for (let number = 2; number <= 198; number += 1) { await page.keyboard.press("ArrowRight"); if (await page.locator("#counter").innerText() !== `${number}/198` || !page.url().endsWith(`#page-${number}`)) throw new Error(`navigation failed at page ${number}`); }
  check(true, "ArrowRight counter/hash walk covers all 198 pages");
  await page.keyboard.press("Home"); check(await page.locator("#counter").innerText() === "1/198", "Home returns to cover");
  await page.keyboard.press("End"); check(await page.locator("#counter").innerText() === "198/198", "End jumps to last page");
  for (const id of compositions) {
    const video = page.locator(`video[data-composition="${id}"]`);
    const number = await video.evaluate((element) => [...document.querySelectorAll(".slot")].indexOf(element.closest(".slot")) + 1);
    await page.goto(`${uri}#page-${number}`, {waitUntil: "load"});
    await page.waitForFunction((composition) => { const element = document.querySelector(`video[data-composition="${composition}"]`); return element && !element.paused && element.muted && element.currentTime > 0.12; }, id);
    await page.keyboard.press("ArrowRight"); await page.waitForTimeout(180);
    check(await video.evaluate((element) => element.paused), `${id} pauses after leaving its slide`);
  }
  check(external.length === 0, "0 external HTTP(S) requests"); check(consoleErrors.length === 0, "0 console errors"); check(pageErrors.length === 0, "0 uncaught page errors");
  await browser.close(); process.stdout.write("[deck] RESULT: PASS\n");
})().catch((error) => { process.stderr.write(`[deck][FAIL] ${error.stack || error}\n`); process.exitCode = 1; });
