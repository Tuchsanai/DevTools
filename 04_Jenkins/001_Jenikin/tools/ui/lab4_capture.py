#!/usr/bin/env python3
"""Capture LAB 4 GitHub/Jenkins evidence with privacy masks applied before saving."""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import browser_page, jenkins_login, log, require, run_main


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"
JOB = "hello-ci-pipeline"
VIEWPORT = {"width": 1440, "height": 1000}
MASK_FILL = "#0d1117"


def _text_rectangles(page, needle: str) -> list[dict[str, float]]:
    if not needle:
        return []
    return page.evaluate(
        """
        needle => {
          const out = [];
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          let node;
          while ((node = walker.nextNode())) {
            let start = 0;
            while (true) {
              const index = node.nodeValue.toLowerCase().indexOf(needle.toLowerCase(), start);
              if (index < 0) break;
              const range = document.createRange();
              range.setStart(node, index);
              range.setEnd(node, index + needle.length);
              for (const r of range.getClientRects()) {
                if (r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight)
                  out.push({x:r.x, y:r.y, width:r.width, height:r.height});
              }
              start = index + needle.length;
            }
          }
          return out;
        }
        """,
        needle,
    )


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def _fitted_font(draw: ImageDraw.ImageDraw, text: str, width: int, height: int):
    """Largest font that keeps the placeholder inside its mask.

    The mask may only cover the account name it replaces — growing the box would
    swallow the repository name next to it — so the label shrinks to fit instead
    of being cut off mid-word.
    """
    for size in range(min(16, max(7, height - 3)), 5, -1):
        font = _font(size)
        if draw.textlength(text, font=font) <= width - 4:
            return font
    return _font(6)


def draw_masks(image: Image.Image, rectangles, label: str, scale: float = 1.0) -> None:
    """Cover each rectangle and stamp the placeholder that replaces it."""
    draw = ImageDraw.Draw(image)
    for rect in rectangles:
        box = [
            max(0, int(rect["x"] * scale) - 3),
            max(0, int(rect["y"] * scale) - 2),
            min(image.width, int((rect["x"] + rect["width"]) * scale) + 3),
            min(image.height, int((rect["y"] + rect["height"]) * scale) + 2),
        ]
        draw.rectangle(box, fill=MASK_FILL)
        font = _fitted_font(draw, label, box[2] - box[0], box[3] - box[1])
        draw.text((box[0] + 2, box[1] + 1), label, fill="white", font=font)


def masked_screenshot(
    page,
    target: Path,
    description: str,
    *,
    mask_texts: tuple[str, ...] = (),
    mask_locators: tuple = (),
    crop: tuple[int, int] | None = None,
) -> None:
    """Take an in-memory screenshot, mask rectangles, then write the first on-disk PNG."""
    rectangles: list[tuple[float, float, float, float, str]] = []
    for value in mask_texts:
        for rect in _text_rectangles(page, value):
            rectangles.append((rect["x"], rect["y"], rect["width"], rect["height"], "<GITHUB_USER>"))
    for locator, label in mask_locators:
        if locator.count() and locator.first.is_visible():
            rect = locator.first.bounding_box()
            if rect:
                rectangles.append((rect["x"], rect["y"], rect["width"], rect["height"], label))

    raw = page.screenshot(full_page=False)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    for x, y, width, height, label in rectangles:
        draw_masks(image, [{"x": x, "y": y, "width": width, "height": height}], label)
    if crop is not None:
        image = image.crop((0, max(0, crop[0]), image.width, min(image.height, crop[1])))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG", optimize=True)
    log(f"masked screenshot: {description} -> {target} ({len(rectangles)} mask(s))")


def capture_github(page, user: str, require_files: bool) -> None:
    page.set_viewport_size(VIEWPORT)
    response = page.goto(f"https://github.com/{user}/hello-ci", wait_until="domcontentloaded")
    require(response is not None and response.status == 200, "public GitHub repository page returned HTTP 200")
    body = page.locator("body").inner_text()
    if require_files:
        page.wait_for_timeout(4000)
        body = page.locator("body").inner_text()
        for name in (".course-cicd2569", "Jenkinsfile", "hello.sh", "expected.txt"):
            require(name in body, f"public repository page lists {name}")
        target = ASSETS / "lab4_s03_github_repo_files.png"
        description = "public GitHub repository after the first push"
    else:
        require(
            "This repository is empty" in body
            or "Quick setup" in body
            or "create a new repository" in body,
            "public repository page is empty",
        )
        target = ASSETS / "lab4_s02_github_empty_repo.png"
        description = "empty public GitHub repository"
    masked_screenshot(page, target, description, mask_texts=(user,))


def capture_jenkins(page, base_url: str, action: str, user: str) -> None:
    page.set_viewport_size(VIEWPORT)
    jenkins_login(page, base_url)
    if action == "manual-console":
        page.goto(f"{base_url}/job/{JOB}/lastBuild/console", wait_until="domcontentloaded")
        body = page.locator("body").inner_text()
        # The lab reads three things off this one screen: which revision was checked
        # out, that hello.sh really ran, and the final result — so frame from the
        # checkout line rather than from the greeting halfway down the log.
        require("Checking out Revision" in body, "manual console contains Checking out Revision")
        require("refs/remotes/origin/main" in body, "checkout is against refs/remotes/origin/main")
        require("Hello from GitHub" in body, "manual console contains Hello from GitHub")
        require("Finished: SUCCESS" in body, "manual console contains Finished: SUCCESS")
        # All three proofs have to sit in one frame.  Rather than fight the page's
        # scrolling, open a window tall enough to hold the whole console, then keep
        # only the band from the checkout line to the final result.
        doc_height = page.evaluate("() => document.documentElement.scrollHeight")
        page.set_viewport_size({"width": VIEWPORT["width"], "height": min(3000, doc_height + 40)})
        page.wait_for_timeout(500)

        def band(needle: str) -> tuple[float, float]:
            return page.evaluate(
                """needle => {
                     const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                     let node, last = null;
                     while ((node = walker.nextNode()))
                       if (node.nodeValue.includes(needle)) last = node;
                     if (!last) throw new Error(needle);
                     const range = document.createRange();
                     range.selectNodeContents(last);
                     const r = range.getBoundingClientRect();
                     return [r.top + window.scrollY, r.bottom + window.scrollY];
                   }""",
                needle,
            )

        crop_top = max(0, int(band("Checking out Revision")[0]) - 96)
        crop_bottom = int(band("Finished: SUCCESS")[1]) + 56
        require(crop_bottom > crop_top, "console band has a positive height")

        target = ASSETS / "lab4_s06_manual_build_console.png"
        description = "manual SCM build console"
        masked_screenshot(page, target, description, mask_texts=(user,),
                          crop=(crop_top, crop_bottom))
        return
    elif action == "poll-log":
        page.goto(f"{base_url}/job/{JOB}/scmPollLog/", wait_until="domcontentloaded")
        require("Changes found" in page.locator("body").inner_text(), "Git Polling Log contains Changes found")
        target = ASSETS / "lab4_s08_git_polling_log.png"
        description = "Git Polling Log with Changes found"
    else:
        page.goto(f"{base_url}/job/{JOB}/lastBuild/", wait_until="domcontentloaded")
        require("Started by an SCM change" in page.locator("body").inner_text(), "build page shows SCM change cause")
        target = ASSETS / "lab4_s09_scm_build_cause.png"
        description = "successful build caused by an SCM change"
    masked_screenshot(page, target, description, mask_texts=(user,))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("github-empty", "github-files", "manual-console", "poll-log", "scm-build"), required=True)
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    args = parser.parse_args()
    user = os.environ.get("GITHUB_USER", "")
    require(bool(user), "GITHUB_USER is set")
    with browser_page() as (_, _, _, page):
        if args.action.startswith("github-"):
            capture_github(page, user, require_files=args.action == "github-files")
        else:
            capture_jenkins(page, args.base_url.rstrip("/"), args.action, user)


if __name__ == "__main__":
    run_main(main)
