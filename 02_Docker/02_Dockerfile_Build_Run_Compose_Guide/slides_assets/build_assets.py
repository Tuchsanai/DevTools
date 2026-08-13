#!/usr/bin/env python3
"""Rebuild the single window.ASSETS line inside the Week-11 slide decks.

- SVG figures are embedded as base64 data URIs (key -> slides_assets/*.svg)
- Screenshots are converted to JPEG quality 82 and embedded (key -> PNG path)

Targets every deck listed in DECKS that exists and contains the ASSETS line.

Run:  python3 slides_assets/build_assets.py
"""
import base64
import io
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECKS = [
    HERE.parent / "Docker_Week11_Slides.html",
    HERE.parent / "new_Docker_Week11_Slides.html",
]

SVGS = {
    "d01": "01-image-vs-container.svg",
    "d02": "02-dockerfile-anatomy.svg",
    "d03": "03-build-flow.svg",
    "d04": "04-layer-cache.svg",
    "d05": "05-cmd-entrypoint.svg",
    "d06": "06-registry-flow.svg",
    "d07": "07-image-naming.svg",
    "d08": "08-default-networks.svg",
    "d09": "09-embedded-dns.svg",
    "d10": "10-secret-mission.svg",
    "d11": "11-why-compose.svg",
    "d12": "12-compose-stack.svg",
    "d13": "13-healthcheck-timeline.svg",
    "d14": "14-compose-watch.svg",
    "d15": "15-multi-stage.svg",
    "d16": "16-week-map.svg",
    "d17": "17-vscode-port-forward.svg",
}

# screenshots: key -> path relative to the deck folder (PNG in, JPEG q82 out)
SHOTS = {
    "japp1": "001_LAB_Dockerfile_First_Image/images/app-v1.png",
    "japp2": "001_LAB_Dockerfile_First_Image/images/app-v2.png",
    "jcard": "003_LAB_Docker_Hub_Registry/images/card-page.png",
    "jvote": "005_LAB_Docker_Compose_Voting/images/vote-page.png",
    "jresult": "005_LAB_Docker_Compose_Voting/images/result-page.png",
    # real Docker Hub captures (Playwright, Aug 2026)
    "jhub1": "003_LAB_Docker_Hub_Registry/images/hub-home.png",
    "jhub2": "003_LAB_Docker_Hub_Registry/images/hub-signup.png",
    "jhub3": "003_LAB_Docker_Hub_Registry/images/hub-pat-page.png",
    "jhub4": "003_LAB_Docker_Hub_Registry/images/hub-pat-generate.png",
    "jhub5": "003_LAB_Docker_Hub_Registry/images/hub-repo-page.png",
    "jhub6": "003_LAB_Docker_Hub_Registry/images/hub-repo-tags.png",
}


def svg_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode()
    return "data:image/svg+xml;base64," + b64


def jpeg_uri(path: Path) -> str:
    from PIL import Image

    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> None:
    assets: dict[str, str] = {}
    for key, name in SVGS.items():
        assets[key] = svg_uri(HERE / name)
    for key, rel in SHOTS.items():
        p = HERE.parent / rel
        if p.exists():
            assets[key] = jpeg_uri(p)
        else:
            print(f"[warn] missing screenshot for {key}: {p}")

    for deck in DECKS:
        if not deck.exists():
            print(f"[skip] {deck.name} not found")
            continue
        html = deck.read_text(encoding="utf-8")
        used = set(re.findall(r'data-a="(\w+)"', html))
        subset = {k: v for k, v in assets.items() if k in used}
        missing = used - set(subset)
        if missing:
            print(f"[warn] {deck.name} references unknown keys: {sorted(missing)}")
        line = "<script>window.ASSETS=" + json.dumps(subset) + "</script>"
        new, n = re.subn(
            r"<script>window\.ASSETS=.*?</script>", lambda _m: line, html, count=1, flags=re.S
        )
        if n != 1:
            print(f"[warn] ASSETS line not found in {deck.name}")
            continue
        deck.write_text(new, encoding="utf-8")
        print(f"embedded {len(subset)} assets -> {deck.name} ({deck.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
