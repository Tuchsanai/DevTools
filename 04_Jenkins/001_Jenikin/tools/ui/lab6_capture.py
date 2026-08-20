#!/usr/bin/env python3
"""Capture LAB 6 public GitHub and live smee evidence, masking before save."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import browser_page, log, require, run_main


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"
MASK_FILL = "#0d1117"


def text_rectangles(page, needle: str) -> list[dict[str, float]]:
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
            const text = node.nodeValue.toLowerCase();
            while (true) {
              const index = text.indexOf(needle.toLowerCase(), start);
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


def _font(size: int):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def masked_screenshot(
    page,
    target: Path,
    description: str,
    *,
    masks: tuple[tuple[str, str], ...],
    mask_locators: tuple[tuple[object, str], ...] = (),
) -> None:
    rectangles: list[tuple[float, float, float, float, str]] = []
    for needle, replacement in masks:
        for rect in text_rectangles(page, needle):
            rectangles.append((rect["x"], rect["y"], rect["width"], rect["height"], replacement))
    for locator, replacement in mask_locators:
        if locator.count() and locator.first.is_visible():
            rect = locator.first.bounding_box()
            if rect:
                rectangles.append((rect["x"], rect["y"], rect["width"], rect["height"], replacement))
    raw = page.screenshot(full_page=False)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    draw = ImageDraw.Draw(image)
    for x, y, width, height, replacement in rectangles:
        box = [max(0, int(x) - 4), max(0, int(y) - 2), min(image.width, int(x + width) + 4), min(image.height, int(y + height) + 2)]
        draw.rectangle(box, fill=MASK_FILL)
        size = max(9, min(17, box[3] - box[1] - 2))
        draw.text((box[0] + 3, box[1] + 1), replacement, fill="white", font=_font(size))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG", optimize=True)
    log(f"masked screenshot: {description} -> {target} ({len(rectangles)} mask(s))")


def relay_channel(devtools_name: str) -> str:
    raw = subprocess.check_output(
        ["docker", "exec", devtools_name, "docker", "inspect", "smee-webapp"], text=True
    )
    args = json.loads(raw)[0]["Config"]["Cmd"]
    channel = args[args.index("--url") + 1]
    require(bool(re.fullmatch(r"https://smee\.io/[^/?#]+", channel)), "smee-webapp stores a valid channel")
    return channel


def capture_github(page, user: str) -> None:
    response = page.goto(f"https://github.com/{user}/webapp", wait_until="domcontentloaded")
    require(response is not None and response.status == 200, "public GitHub webapp page returned HTTP 200")
    page.wait_for_timeout(3000)
    body = page.locator("body").inner_text()
    for name in ("app", "Dockerfile", "Jenkinsfile", ".course-cicd2569"):
        require(name in body, f"public repository page lists {name}")
    masked_screenshot(
        page,
        ASSETS / "lab6_s02_github_repo_after_push.png",
        "public GitHub webapp repository",
        masks=((user, "<GITHUB_USER>"),),
    )


def capture_smee(page, channel: str, user: str, ready_file: str, timeout: int, initial_only: bool) -> None:
    # Mask the complete URL once so each CLI/Node example receives one box that
    # covers the whole value instead of overlapping channel-id placeholders.
    masks = ((channel, "<SMEE_WEBAPP_URL>"), (user, "<GITHUB_USER>"))
    response = page.goto(channel, wait_until="domcontentloaded")
    require(response is not None and response.status == 200, "smee channel page returned HTTP 200")
    page.wait_for_timeout(1500)
    url_input = page.locator("#url")
    masked_screenshot(
        page,
        ASSETS / "lab6_s03_smee_channel.png",
        "webapp smee channel before hook",
        masks=masks,
        mask_locators=((url_input, "<SMEE_WEBAPP_URL>"),),
    )
    if initial_only:
        log("assert: initial channel capture completed without waiting for a delivery")
        return
    if ready_file:
        Path(ready_file).write_text("ready\n", encoding="utf-8")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if "ping" in page.locator("body").inner_text().casefold():
            break
        page.wait_for_timeout(500)
    require("ping" in page.locator("body").inner_text().casefold(), "live GitHub ping appeared in the open smee tab")
    for index in range(page.get_by_text("ping", exact=True).count() - 1, -1, -1):
        item = page.get_by_text("ping", exact=True).nth(index)
        if item.is_visible():
            item.click()
            page.wait_for_timeout(500)
            break
    masked_screenshot(
        page,
        ASSETS / "lab6_s07_smee_ping.png",
        "live GitHub ping on webapp smee channel",
        masks=masks,
        mask_locators=((url_input, "<SMEE_WEBAPP_URL>"),),
    )


def annotate_all() -> None:
    import annotate_steps as ann

    spec_path = ROOT / "tools/ui/annotations/lab6.json"
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    fonts = ann.load_fonts(ROOT, ann.FONT_SIZE)
    for spec in data["images"]:
        target = ROOT / spec["path"]
        if source_name := spec.get("source"):
            with Image.open(ROOT / source_name) as source:
                source.convert("RGBA").save(target, format="PNG", optimize=True)
        require(target.is_file(), f"annotation target exists: {target.name}")
        with Image.open(target) as source:
            original_mode = source.mode
            image = source.convert("RGBA")
        draw = ImageDraw.Draw(image)
        prepared = []
        for shape in spec.get("shapes", []):
            ann.check_box(shape["box"], image.width, image.height, f"{target.name} marker")
            label = ann.label_box(draw, fonts, shape["label"], shape["label_at"])
            ann.check_box(list(label), image.width, image.height, f"{target.name} label")
            prepared.append((shape, label))
        for shape, label in prepared:
            target_box = shape["box"]
            endpoint = tuple(shape.get("target", [(target_box[0] + target_box[2]) / 2, (target_box[1] + target_box[3]) / 2]))
            start = ((label[0] + label[2]) / 2, (label[1] + label[3]) / 2)
            ann.arrow(draw, start, endpoint)
        for shape, _ in prepared:
            if shape.get("type", "round_rect") == "ellipse":
                draw.ellipse(shape["box"], outline=ann.ROSE, width=ann.LINE_WIDTH)
            else:
                draw.rounded_rectangle(shape["box"], radius=12, outline=ann.ROSE, width=ann.LINE_WIDTH)
        for shape, label in prepared:
            draw.rounded_rectangle(label, radius=ann.LABEL_RADIUS, fill=ann.SLATE)
            ann.draw_label_text(draw, (label[0] + ann.LABEL_PADDING_X, label[1] + ann.LABEL_PADDING_Y), shape["label"], fonts)
        rendered = image if original_mode == "RGBA" else image.convert(original_mode)
        rendered.save(target, format="PNG", optimize=True)
        log(f"annotated screenshot -> {target} ({len(prepared)} marker(s))")
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("github", "smee", "annotate"), required=True)
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk-lab"))
    parser.add_argument("--ready-file", default="")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--initial-only", action="store_true")
    args = parser.parse_args()
    if args.action == "annotate":
        annotate_all()
        return
    user = os.environ.get("GITHUB_USER", "")
    require(bool(user), "GITHUB_USER is set")
    with browser_page() as (_, _, _, page):
        if args.action == "github":
            capture_github(page, user)
        else:
            channel = os.environ.get("SMEE_WEBAPP_URL", "") or relay_channel(args.devtools_name)
            require(bool(re.fullmatch(r"https://smee\.io/[^/?#]+", channel)), "SMEE_WEBAPP_URL is one smee channel")
            capture_smee(page, channel, user, args.ready_file, args.timeout, args.initial_only)


if __name__ == "__main__":
    run_main(main)
