#!/usr/bin/env python3
"""Crop annotated UI screenshots and embed them into the deck ASSETS map."""

from __future__ import annotations

import base64
import io
import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Fullstack_App_Example.html"
SOURCES = {
    "ui_github_code": (
        ROOT / "001_LAB_Run_The_System/images/ui-github-03-code.png",
        (580, 165, 1320, 510),
    ),
    "ui_swagger_created": (
        ROOT / "002_LAB_Build_The_API/images/ui-swagger-09-created.png",
        (180, 65, 1260, 610),
    ),
    "ui_web_new_card": (
        ROOT / "003_LAB_Build_The_Web/images/ui-web-07-new-card.png",
        (330, 205, 920, 875),
    ),
    "ui_hub_api_tags": (
        ROOT / "005_LAB_Compose_And_Ship/images/ui-hub-push-03-api-tags.png",
        (280, 95, 1425, 700),
    ),
}


def data_uri(path: Path, crop: tuple[int, int, int, int]) -> str:
    with Image.open(path) as source:
        if source.size != (1440, 900):
            raise ValueError(f"source must be 1440x900: {path}")
        image = source.convert("RGB").crop(crop)
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return "data:image/png;base64," + encoded


def renumber_comments(html: str) -> str:
    index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal index
        index += 1
        return f"<!-- ===== {index} :{match.group(1)}"

    return re.sub(r"<!-- ===== \d+ :([^\n]*?===== -->)", replace, html)


def main() -> int:
    assets = {key: data_uri(path, crop) for key, (path, crop) in SOURCES.items()}
    tag = (
        '<script id="ui-assets">Object.assign(window.ASSETS,'
        + json.dumps(assets, ensure_ascii=True, separators=(",", ":"))
        + ");</script>"
    )
    html = DECK.read_text(encoding="utf-8")
    existing = re.compile(r'<script id="ui-assets">.*?</script>', re.DOTALL)
    if existing.search(html):
        html = existing.sub(tag, html, count=1)
    else:
        anchor = re.compile(r'(<script id="assets">.*?</script>)', re.DOTALL)
        if not anchor.search(html):
            raise RuntimeError("ASSETS script not found")
        html = anchor.sub(r"\1\n" + tag, html, count=1)
    html = renumber_comments(html)
    DECK.write_text(html, encoding="utf-8")
    print(f"embedded {len(assets)} cropped UI assets")
    print(f"slides: {html.count('<div class=\"slot\"')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
