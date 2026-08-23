#!/usr/bin/env node
"use strict";
const path = require("node:path");
const {createRequire} = require("node:module");
const {pathToFileURL} = require("node:url");
const root = path.resolve(__dirname, "../..");
const {chromium} = createRequire(path.join(root, "tools/motion/package.json"))("playwright");
const deck = process.argv[2] || path.join(root, "Jenkins_CICD_Docker_Slides.html");
(async () => {
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage();
  const response = await page.goto(pathToFileURL(deck).href, {waitUntil: "domcontentloaded"});
  if (!response || !response.ok()) throw new Error("deck did not open successfully");
  process.stdout.write((await page.locator("body").textContent()) || "");
  await browser.close();
})().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
