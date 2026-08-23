#!/usr/bin/env python3
"""Build the offline Jenkins slide deck by embedding every local asset.

The source uses data-asset="path" for raster/video files and
data-inline-svg="path" for editable SVG sources.  The output contains no
filesystem or network asset references and can be opened directly with file://.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import mimetypes
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "tools" / "slides_src.html"
DEFAULT_OUTPUT = ROOT / "Jenkins_CICD_Docker_Slides.html"
MANIFEST = ROOT / "slides_assets" / "motion" / "motion-manifest.json"


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def read_manifest() -> dict[str, dict]:
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    clips = {clip["file"]: clip for clip in raw["clips"]}
    if len(clips) != 6:
        raise ValueError(f"expected 6 manifest clips, found {len(clips)}")
    return clips


def resolve_asset(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents:
        raise ValueError(f"asset escapes repository: {relative}")
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


WEBP_QUALITY = 92


def raster_bytes(path: Path, max_width: int | None) -> tuple[bytes, str, str]:
    """Return the smallest faithful encoding of a screenshot for the deck.

    The deck carries ~90 UI screenshots as data URIs, so encoding matters: a
    re-saved PNG is routinely *larger* than the capture it came from, while
    WebP at q92 is visually identical at the size a slide shows it and several
    times smaller.  Whatever ends up smaller wins, so a file is never inflated.
    """
    raw = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with Image.open(io.BytesIO(raw)) as opened:
        image = opened
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            flat = Image.new("RGB", image.size, (255, 255, 255))
            flat.paste(image, mask=image.split()[-1])
            image = flat
        else:
            image = image.convert("RGB")
        note = "original size"
        if max_width and image.width > max_width:
            height = round(image.height * max_width / image.width)
            image = image.resize((max_width, height), Image.Resampling.LANCZOS)
            note = f"{max_width}x{height}"
        buf = io.BytesIO()
        image.save(buf, format="WEBP", quality=WEBP_QUALITY, method=6)
        candidate = buf.getvalue()
    if len(candidate) < len(raw):
        return candidate, "image/webp", f"webp q{WEBP_QUALITY} {note}"
    return raw, mime, "original kept (already smaller)"


def build(source: Path, output: Path) -> None:
    deck = source.read_text(encoding="utf-8")
    manifest = read_manifest()
    reports: list[tuple[str, int, int, str]] = []
    used_videos: set[str] = set()

    svg_pattern = re.compile(
        r'<div(?P<before>[^>]*?)\sdata-inline-svg="(?P<path>[^"]+)"(?P<after>[^>]*)></div>'
    )

    def embed_svg(match: re.Match[str]) -> str:
        relative = match.group("path")
        path = resolve_asset(relative)
        raw = path.read_bytes()
        svg = raw.decode("utf-8")
        if "<text" not in svg:
            raise ValueError(f"diagram lacks real SVG text: {relative}")
        # The deck stores each slide on one line in a text/plain data block.
        # Keep the editable source pretty, but inline a single-line SVG so its
        # internal formatting cannot be mistaken for additional slide records.
        svg = re.sub(r">\s+<", "><", svg).strip()
        attrs = (match.group("before") + match.group("after")).rstrip()
        reports.append((relative, len(raw), len(raw), "inline SVG"))
        return f"<div{attrs}>{svg}</div>"

    deck = svg_pattern.sub(embed_svg, deck)

    tag_pattern = re.compile(r'<(?P<tag>img|video)(?P<attrs>[^>]*?)\sdata-asset="(?P<path>[^"]+)"(?P<tail>[^>]*)>', re.I)

    def embed_binary(match: re.Match[str]) -> str:
        tag = match.group("tag").lower()
        relative = match.group("path")
        path = resolve_asset(relative)
        attrs = match.group("attrs") + match.group("tail")
        max_match = re.search(r'\sdata-max-width="(\d+)"', attrs)
        max_width = int(max_match.group(1)) if max_match else None
        attrs = re.sub(r'\sdata-max-width="\d+"', "", attrs)

        if tag == "video":
            if path.suffix.lower() != ".mp4":
                raise ValueError(f"video must be mp4: {relative}")
            clip = manifest.get(path.name)
            if not clip:
                raise ValueError(f"video absent from manifest: {path.name}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != clip["sha256"] or path.stat().st_size != clip["bytes"]:
                raise ValueError(f"manifest mismatch: {path.name}")
            composition_match = re.search(r'data-composition="([^"]+)"', attrs)
            if not composition_match or composition_match.group(1) != clip["compositionId"]:
                raise ValueError(f"compositionId mismatch for {path.name}")
            raw, mime, note = path.read_bytes(), "video/mp4", (
                f"manifest {clip['compositionId']} {clip['durationSec']}s"
            )
            used_videos.add(path.name)
        else:
            raw, mime, note = raster_bytes(path, max_width)

        encoded = base64.b64encode(raw).decode("ascii")
        reports.append((relative, path.stat().st_size, len(raw), note))
        safe_path = html.escape(relative, quote=True)
        return f'<{tag}{attrs} data-embedded-from="{safe_path}" src="data:{mime};base64,{encoded}">'

    deck = tag_pattern.sub(embed_binary, deck)
    # Every embedded video is already proven against the manifest above
    # (absent-from-manifest / sha / compositionId all raise).  The deck is
    # allowed to use a subset of the rendered clips — slides that explain a
    # concept better with a static diagram should not be forced to carry a
    # video just because one was rendered once.
    if not used_videos:
        raise ValueError("no manifest video was embedded")
    unused = sorted(set(manifest) - used_videos)
    if unused:
        print(f"note: manifest clips rendered but not used by this deck: {', '.join(unused)}")
    if re.search(r'\b(?:src|href)=["\'](?:https?:|//)', deck, re.I):
        raise ValueError("external URL found in src/href after build")
    if "data-asset=" in deck or "data-inline-svg=" in deck:
        raise ValueError("unresolved asset placeholder remains")

    output.write_text(deck, encoding="utf-8")
    print(f"source: {source.relative_to(ROOT)}")
    for relative, original, embedded, note in reports:
        print(f"asset: {relative:<48} {human_size(original):>10} -> {human_size(embedded):>10}  {note}")
    print(f"assets embedded: {len(reports)} ({len(used_videos)} videos)")
    print(f"output: {output.relative_to(ROOT)} = {human_size(output.stat().st_size)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
