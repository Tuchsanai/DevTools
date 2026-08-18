#!/usr/bin/env python3
"""Embed slide SVGs and optional screenshots into the single-file deck.

SVG files are stored as base64 data URIs. Optional PNG/JPEG screenshots are
converted to RGB JPEG quality 82 before embedding. Missing screenshots leave
the current deck markup unchanged.
"""

from __future__ import annotations

import base64
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "slides_assets"
DECK = ROOT / "Fullstack_Gateway_Broker_Slides.html"

SVGS = {f"d{i:02d}": ASSET_DIR / f"d{i:02d}.svg" for i in range(1, 11)}
SVGS.update(
    {
        "t_front": ROOT / "001_LAB_Gateway_Front_Door/images/theory-front-door.svg",
        "t_route": ROOT / "001_LAB_Gateway_Front_Door/images/theory-routing-priority.svg",
        "t_scale": ROOT / "002_LAB_Scale_Rush_Hour/images/theory-scale-health.svg",
        "t_middle": ROOT / "002_LAB_Scale_Rush_Hour/images/theory-middleware-chain.svg",
        "t_order": ROOT / "003_LAB_Order_Queue_RabbitMQ/images/theory-order-path.svg",
        "t_rabbit": ROOT / "003_LAB_Order_Queue_RabbitMQ/images/theory-rabbit-controls.svg",
        "t_event": ROOT / "004_LAB_Sales_Analytics_Kafka/images/theory-event-pipeline.svg",
        "t_key": ROOT / "004_LAB_Sales_Analytics_Kafka/images/theory-key-partition.svg",
        "t_canary": ROOT / "005_LAB_Canary_Release_Capstone/images/theory-canary-weights.svg",
        "t_full": ROOT / "005_LAB_Canary_Release_Capstone/images/theory-full-stack.svg",
    }
)
SHOTS = {
    "jweb1": "screenshots/jweb1.jpg",
    "jweb2": "screenshots/jweb2.jpg",
    "jweb3": "screenshots/jweb3.jpg",
    "jweb4": "screenshots/jweb4.jpg",
    "jdash": "screenshots/jdash.jpg",
    "jrabbit": "screenshots/jrabbit.jpg",
    "jkafka": "screenshots/jkafka.jpg",
    "jcanary": "screenshots/jcanary.jpg",
}


def svg_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return "data:image/svg+xml;base64," + encoded


def jpeg_uri(path: Path) -> str:
    from PIL import Image

    with Image.open(path) as image:
        rgb = image.convert("RGB")
        buffer = io.BytesIO()
        rgb.save(buffer, "JPEG", quality=82, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return "data:image/jpeg;base64," + encoded


def main() -> int:
    assets: dict[str, str] = {}
    missing_required: list[str] = []

    for key, path in SVGS.items():
        if not path.is_file():
            missing_required.append(str(path))
            continue
        assets[key] = svg_uri(path)

    if missing_required:
        for path in missing_required:
            print(f"[error] missing required SVG: {path}")
        return 1

    for key, relative in SHOTS.items():
        path = ASSET_DIR / relative
        if path.is_file():
            assets[key] = jpeg_uri(path)
        else:
            print(f"[warn] screenshot not embedded for {key}: {path}")

    html = DECK.read_text(encoding="utf-8")
    # A real screenshot is supplied through window.ASSETS; remove the inline
    # SVG fallback so the finished deck contains no placeholder artwork.
    for key in SHOTS:
        if key in assets:
            html = re.sub(
                rf'(<img\s+data-a="{re.escape(key)}")\s+src="data:image/svg\+xml,[^"]*"',
                r'\1',
                html,
                count=1,
            )
    html = re.sub(r'alt="placeholder\s+([^"]+)"', r'alt="\1"', html)
    used = set(re.findall(r'data-a="([A-Za-z0-9_-]+)"', html))
    # Deck v3 builds image elements from slide data at runtime. Embed the full
    # manifest so every declared visual remains available to that renderer.
    subset = assets
    unknown = sorted(used - set(SVGS) - set(SHOTS))
    if unknown:
        print(f"[error] unknown data-a keys: {unknown}")
        return 1

    line = "<script>window.ASSETS=" + json.dumps(
        subset, ensure_ascii=False, separators=(",", ":")
    ) + "</script>"
    updated, count = re.subn(
        r"<script>window\.ASSETS=.*?</script>",
        lambda _match: line,
        html,
        count=1,
        flags=re.S,
    )
    if count != 1:
        print("[error] expected exactly one window.ASSETS script")
        return 1

    DECK.write_text(updated, encoding="utf-8")
    print(
        f"embedded {len(subset)} assets "
        f"({len(SVGS)} diagrams, {len(subset) - len(SVGS)} screenshots) "
        f"-> {DECK.name} ({DECK.stat().st_size / 1_000_000:.2f} MB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
