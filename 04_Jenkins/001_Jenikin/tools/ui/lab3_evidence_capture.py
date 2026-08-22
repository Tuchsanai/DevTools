#!/usr/bin/env python3
"""Recapture focused LAB 3 console and anonymous Hub evidence."""

from __future__ import annotations

import os
from pathlib import Path

import io
import re

from PIL import Image, ImageDraw

from common import browser_page, jenkins_login, log, require, run_main, wait_visible
from lab4_capture import _text_rectangles, draw_masks


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:13080").rstrip("/")
    docker_user = os.environ.get("DOCKER_USER", "")
    require(bool(docker_user), "Docker Hub public namespace environment is present")

    with browser_page() as (_, browser, context, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/docker-build-push/lastBuild/console", wait_until="domcontentloaded")
        console_pre = page.locator("pre").last
        page.set_viewport_size({"width": 1440, "height": 180})
        require("Login Succeeded" in console_pre.inner_text(), "console contains Login Succeeded")
        require("digest: sha256:" in console_pre.inner_text(), "console contains a push digest")

        for needle, filename, description in (
            ("Login Succeeded", "lab3_s06_console_login.png", "Login Succeeded line"),
            ("digest: sha256:", "lab3_s07_console_digest.png", "push digest line"),
        ):
            rect = console_pre.evaluate(
                """(el, needle) => {
                    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                    let node = null;
                    let match = null;
                    let index = -1;
                    while ((node = walker.nextNode())) {
                      const candidate = node.textContent.lastIndexOf(needle);
                      if (candidate >= 0) { match = node; index = candidate; }
                    }
                    if (!match) throw new Error(`text not found: ${needle}`);
                    const range = document.createRange();
                    range.setStart(match, index);
                    range.setEnd(match, index + needle.length);
                    const r = range.getBoundingClientRect();
                    return {top: r.top + window.scrollY};
                }""",
                needle,
            )
            page.evaluate("y => window.scrollTo(0, Math.max(0, y - 72))", rect["top"])
            page.screenshot(path=str(ASSETS / filename), full_page=False)
            log(f"screenshot: focused console evidence ({description})")

        build_number = page.evaluate(
            """async url => (await (await fetch(url, {credentials: 'same-origin'})).json()).number""",
            f"{base_url}/job/docker-build-push/lastBuild/api/json?tree=number",
        )
        hub_context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 820, "height": 1100},
            device_scale_factor=2,
        )
        hub_page = hub_context.new_page()
        response = hub_page.goto(
            f"https://hub.docker.com/r/{docker_user}/ci-demo/tags",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        require(response is not None and response.status == 200, "anonymous Docker Hub Tags page returns HTTP 200")
        hub_page.wait_for_timeout(5000)
        tags_tab = wait_visible(hub_page.get_by_text("Tags", exact=True).first, "public Tags tab", 120000)
        current_tag = wait_visible(hub_page.get_by_text(str(build_number), exact=True).first, "current build tag", 120000)

        # Hub shows the digest in short form, so close the BUILD_NUMBER -> digest loop
        # against the first 12 hex characters the build's console printed.
        short_digest = re.search(r"digest: sha256:([0-9a-f]{12})", console_pre.inner_text()).group(1)
        digest_cell = wait_visible(hub_page.get_by_text(short_digest, exact=False).first,
                                   f"public Tags card shows digest {short_digest}", 120000)

        tags_box = tags_tab.bounding_box()
        digest_box = digest_cell.bounding_box()
        require(tags_box is not None and digest_box is not None, "public Tags evidence has measurable bounds")
        crop_x = 0  # the tag number and Digest column sit left of the Tags tab
        crop_y = max(0, tags_box["y"] - 22)
        crop_h = digest_box["y"] + digest_box["height"] + 18 - crop_y

        # The public page repeats the account name; only the placeholder may reach disk.
        rects = _text_rectangles(hub_page, docker_user)
        raw = hub_page.screenshot(full_page=False)
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        ratio = image.width / 820
        draw_masks(image, rects, "<DOCKER_USER>", ratio)
        image.crop((int(crop_x * ratio), int(crop_y * ratio),
                    image.width, int((crop_y + crop_h) * ratio))).save(
            ASSETS / "lab3_s08_hub_public_tag.png", format="PNG", optimize=True)
        log(f"screenshot: anonymous Hub Tags tab, tag {build_number} and digest {short_digest} "
            f"({len(rects)} namespace mask(s))")
        hub_context.close()
        log("screenshot: anonymous Hub Tags tab and current build tag without account header")


if __name__ == "__main__":
    run_main(main)
