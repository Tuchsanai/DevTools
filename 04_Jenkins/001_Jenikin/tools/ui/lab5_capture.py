#!/usr/bin/env python3
"""Capture masked LAB 5 smee/Jenkins evidence; raw pixels never touch disk."""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import time
import json
import urllib.request

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
            const haystack = node.nodeValue.toLowerCase();
            while (true) {
              const index = haystack.indexOf(needle.toLowerCase(), start);
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


def font(size: int):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def masked_screenshot(page, target: Path, description: str, *, masks: tuple[tuple[str, str], ...], mask_locators: tuple[tuple[object, str], ...] = ()) -> None:
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
        draw.text((box[0] + 3, box[1] + 1), replacement, fill="white", font=font(size))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG", optimize=True)
    log(f"masked screenshot: {description} -> {target} ({len(rectangles)} mask(s))")


def wait_for_text(page, predicate, description: str, timeout_seconds: int) -> str:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        body = page.locator("body").inner_text()
        if predicate(body.casefold()):
            log(f"assert: {description}")
            return body
        page.wait_for_timeout(500)
    raise TimeoutError(f"timed out waiting for {description}")


def click_event(page, name: str) -> None:
    candidates = page.get_by_text(name, exact=True)
    for index in range(candidates.count() - 1, -1, -1):
        item = candidates.nth(index)
        if item.is_visible():
            expander = item.locator("xpath=ancestor::li[1]").locator("button.ellipsis-expander")
            if expander.count():
                expander.click()
            else:
                item.click()
            page.wait_for_timeout(500)
            return


def expand_payload_key(page, key: str) -> None:
    clicked = page.evaluate(
        """
        key => {
          const expected = `"${key}"`;
          for (const element of document.querySelectorAll('.object-key')) {
            if (element.textContent.trim() !== expected) continue;
            const rect = element.getBoundingClientRect();
            if (rect.width && rect.height && rect.bottom > 0) {
              let target = element;
              while (target && getComputedStyle(target).cursor !== 'pointer')
                target = target.parentElement;
              if (target) { target.click(); return true; }
            }
          }
          return false;
        }
        """,
        key,
    )
    require(bool(clicked), f"payload tree contains expandable {key}")
    page.wait_for_timeout(500)


def expand_first_child(page, key: str) -> None:
    clicked = page.evaluate(
        """
        key => {
          const expected = `"${key}"`;
          for (const element of document.querySelectorAll('.object-key')) {
            if (element.textContent.trim() !== expected) continue;
            const row = element.closest('.object-key-val');
            if (!row) continue;
            const icons = [...row.querySelectorAll('.collapsed-icon')];
            for (const icon of icons) {
              let target = icon;
              while (target && getComputedStyle(target).cursor !== 'pointer')
                target = target.parentElement;
              if (target) { target.click(); return true; }
            }
          }
          return false;
        }
        """,
        key,
    )
    require(bool(clicked), f"expanded first item below {key}")
    page.wait_for_timeout(500)


def redeliver_latest_ping(user: str) -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    require(bool(token), "GITHUB_TOKEN is set for the capture-only ping redelivery")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    def api(method: str, path: str):
        request = urllib.request.Request(
            f"https://api.github.com{path}", method=method, headers=headers
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
            return None if not data else json.loads(data)
    hooks = api("GET", f"/repos/{user}/hello-ci/hooks?per_page=100")
    require(bool(hooks), "GitHub hook exists for ping redelivery")
    hook = hooks[0]
    deliveries = api("GET", f"/repos/{user}/hello-ci/hooks/{hook['id']}/deliveries?per_page=10")
    ping = next(item for item in deliveries if item.get("event") == "ping")
    api("POST", f"/repos/{user}/hello-ci/hooks/{hook['id']}/deliveries/{ping['id']}/attempts")
    log("capture helper requested a ping redelivery after the tab was connected")


def listen(args: argparse.Namespace) -> None:
    channel = os.environ.get("SMEE_HELLO_URL", "")
    user = os.environ.get("GITHUB_USER", "")
    require(channel.startswith("https://smee.io/") and channel.count("/") == 3, "SMEE_HELLO_URL is one smee channel")
    require(bool(user), "GITHUB_USER is set")
    # Mask the complete URL once. Masking the nested channel id separately would
    # paint overlapping placeholders and leave an unreadable command example.
    masks = ((channel, "<SMEE_HELLO_URL>"), (user, "<GITHUB_USER>"))
    with browser_page() as (_, _, _, page):
        page.goto(channel, wait_until="domcontentloaded")
        wait_for_text(page, lambda text: "webhook" in text or "smee" in text, "smee channel page loaded", 30)
        url_input = page.locator("#url")
        masked_screenshot(page, ASSETS / "lab5_s03_smee_channel.png", "new smee channel kept open", masks=masks, mask_locators=((url_input, "<SMEE_HELLO_URL>"),))
        if args.initial_only:
            log("assert: initial channel capture completed without waiting for a delivery")
            return
        if args.ready_file:
            Path(args.ready_file).write_text("ready\n", encoding="utf-8")
        if args.redeliver_ping:
            redeliver_latest_ping(user)
        wait_for_text(page, lambda text: "ping" in text, "live GitHub ping event appeared", args.timeout)
        click_event(page, "ping")
        wait_for_text(page, lambda text: "event id:" in text, "expanded ping delivery details", 30)
        masked_screenshot(page, ASSETS / "lab5_s07_smee_ping.png", "GitHub ping visible in live smee tab", masks=masks, mask_locators=((url_input, "<SMEE_HELLO_URL>"),))
        wait_for_text(page, lambda text: "push" in text, "live GitHub push event appeared", args.timeout)
        click_event(page, "push")
        wait_for_text(page, lambda text: "refs/heads/main" in text and "head_commit" in text, "expanded push payload has ref and head_commit", 30)
        masked_screenshot(page, ASSETS / "lab5_s08_smee_push.png", "GitHub push payload in live smee tab", masks=masks, mask_locators=((url_input, "<SMEE_HELLO_URL>"),))
        expand_payload_key(page, "commits")
        expand_first_child(page, "commits")
        expand_payload_key(page, "added")
        wait_for_text(page, lambda text: '"added"' in text and "webhook-proof" in text, "commits[].added contains a webhook proof file", 30)
        page.get_by_text("webhook-proof", exact=False).first.scroll_into_view_if_needed()
        masked_screenshot(page, ASSETS / "lab5_s08a_smee_commit_files.png", "commits added and modified files", masks=masks, mask_locators=((url_input, "<SMEE_HELLO_URL>"),))
        expand_payload_key(page, "head_commit")
        wait_for_text(page, lambda text: '"message"' in text and "verify immediate github webhook build" in text, "head_commit message is expanded", 30)
        page.get_by_text("Verify immediate GitHub webhook build", exact=False).first.scroll_into_view_if_needed()
        masked_screenshot(page, ASSETS / "lab5_s08b_smee_head_commit.png", "expanded head_commit evidence", masks=masks, mask_locators=((url_input, "<SMEE_HELLO_URL>"),))


def annotate_all() -> None:
    import annotate_steps as ann

    spec_path = ROOT / "tools/ui/annotations/lab5.json"
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    fonts = ann.load_fonts(ROOT, ann.FONT_SIZE)
    for spec in data["images"]:
        target = ROOT / spec["path"]
        if source_name := spec.get("source"):
            with Image.open(ROOT / source_name) as source:
                source.convert("RGBA").save(target, format="PNG", optimize=True)
        with Image.open(target) as source:
            original_mode = source.mode
            image = source.convert("RGBA")
        draw = ImageDraw.Draw(image)
        prepared = []
        for shape in spec.get("shapes", []):
            box = shape["box"]
            ann.check_box(box, image.width, image.height, f"{target.name} marker")
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
    parser.add_argument("--action", choices=("listen", "annotate"), default="listen")
    parser.add_argument("--ready-file")
    parser.add_argument("--redeliver-ping", action="store_true")
    parser.add_argument("--initial-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.action == "annotate":
        annotate_all()
    else:
        listen(args)


if __name__ == "__main__":
    run_main(main)
