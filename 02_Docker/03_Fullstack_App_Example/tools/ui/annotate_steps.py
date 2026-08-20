#!/usr/bin/env python3
"""ใส่ marker (กรอบแดง + เลขลำดับ + ป้ายไทย) ลงภาพหน้าจอ UI ตาม annotation spec

รองรับทั้ง schema กลาง ``markers``/``masks`` และ schema ``shapes`` เดิม
เพื่อให้สเปกจากชุดก่อนยังใช้งานได้
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROSE = "#e11d48"
SLATE = "#1e293b"
WHITE = "#ffffff"
MASK_FILL = "#0d1117"
LINE_WIDTH = 5
FONT_SIZE = 28
MASK_PADDING = 4
LABEL_PADDING_X = 14
LABEL_PADDING_Y = 8
LABEL_RADIUS = 10


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, check=check, text=True, capture_output=True
    )


def repo_root() -> Path:
    # This teaching project is nested inside a larger Git worktree.  Specs and
    # image paths are deliberately relative to the project, not the outer root.
    project = Path(__file__).resolve().parents[2]
    git(project, "rev-parse", "--show-toplevel")
    return project


def safe_repo_path(repo: Path, relative: str) -> Path:
    path = (repo / relative).resolve()
    if repo not in path.parents:
        raise ValueError(f"path escapes repository: {relative}")
    if path.suffix.lower() != ".png":
        raise ValueError(f"target must be a PNG: {relative}")
    return path


def restore_pristine(repo: Path, image_spec: dict[str, Any]) -> str:
    relative = image_spec["path"]
    target = safe_repo_path(repo, relative)
    source_relative = image_spec.get("source")
    tracked = git(repo, "ls-files", "--error-unmatch", "--", relative, check=False)
    if tracked.returncode == 0 and not source_relative:
        git(repo, "checkout", "--", relative)
        return "git checkout"

    if not source_relative:
        raise ValueError(
            f"untracked target {relative!r} needs a pristine 'source' until it is committed"
        )
    source = safe_repo_path(repo, source_relative)
    if not source.is_file():
        raise ValueError(f"pristine source is missing: {source_relative}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return f"copy pristine {source_relative}"


def load_fonts(repo: Path, size: int) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
    font_path = repo / "tools/fonts/NotoSansThai-Variable.ttf"
    if not font_path.is_file():
        raise FileNotFoundError(f"Thai font not found: {font_path}")
    # DejaVu Sans has ①-⑩ but not ⑪-⑳. WenQuanYi Zen Hei covers the
    # complete Unicode circled-number range needed by longer walkthroughs.
    symbol_candidates = (
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    symbol_path = next((path for path in symbol_candidates if path.is_file()), None)
    if symbol_path is None:
        raise FileNotFoundError("circled-number fallback font not found")
    return (
        ImageFont.truetype(str(font_path), size=size),
        ImageFont.truetype(str(symbol_path), size=size - 1),
    )


def check_box(box: list[int], width: int, height: int, label: str) -> None:
    if len(box) != 4:
        raise ValueError(f"{label} must contain four coordinates")
    x1, y1, x2, y2 = box
    if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
        raise ValueError(f"{label} {box} is outside {width}x{height}")


def label_box(
    draw: ImageDraw.ImageDraw,
    fonts: tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont],
    text: str,
    at: list[int],
) -> tuple[int, int, int, int]:
    if len(at) != 2:
        raise ValueError("label_at must contain x and y")
    left, top = at
    parts = label_parts(text, fonts)
    boxes = [draw.textbbox((0, 0), part, font=font, anchor="lt") for part, font in parts]
    text_width = sum(box[2] - box[0] for box in boxes)
    text_height = max(box[3] - box[1] for box in boxes)
    return (
        left,
        top,
        left + text_width + LABEL_PADDING_X * 2,
        top + text_height + LABEL_PADDING_Y * 2,
    )


def label_parts(
    text: str, fonts: tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]
) -> list[tuple[str, ImageFont.FreeTypeFont]]:
    thai_font, symbol_font = fonts
    if text and text[0] in "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳":
        return [(text[0], symbol_font), (text[1:], thai_font)]
    return [(text, thai_font)]


def draw_label_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    fonts: tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont],
) -> None:
    x, y = position
    for part, font in label_parts(text, fonts):
        draw.text((x, y), part, font=font, fill=WHITE, anchor="lt")
        bbox = draw.textbbox((0, 0), part, font=font, anchor="lt")
        x += bbox[2] - bbox[0]


def fit_mask_font(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
    text: str,
    box: list[int],
) -> ImageFont.FreeTypeFont:
    available_width = box[2] - box[0] - MASK_PADDING * 2
    available_height = box[3] - box[1] - MASK_PADDING * 2
    if available_width <= 0 or available_height <= 0:
        raise ValueError(f"mask box {box} is too small for text")
    for size in range(font.size, 0, -1):
        candidate = font.font_variant(size=size)
        bounds = draw.textbbox((0, 0), text, font=candidate)
        if (
            bounds[2] - bounds[0] <= available_width
            and bounds[3] - bounds[1] <= available_height
        ):
            return candidate
    raise ValueError(f"mask text does not fit inside box {box}: {text!r}")


def draw_mask(
    draw: ImageDraw.ImageDraw,
    shape: dict[str, Any],
    font: ImageFont.FreeTypeFont,
) -> None:
    box = shape["box"]
    draw.rectangle(box, fill=shape.get("fill", MASK_FILL))
    text = shape.get("text")
    if not text:
        return
    fitted = fit_mask_font(draw, font, text, box)
    bounds = draw.textbbox((0, 0), text, font=fitted)
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    x = box[0] + (box[2] - box[0] - text_width) / 2 - bounds[0]
    y = box[1] + (box[3] - box[1] - text_height) / 2 - bounds[1]
    draw.text((x, y), text, font=fitted, fill=WHITE)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float]) -> None:
    draw.line((start, end), fill=ROSE, width=4)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 15
    spread = math.pi / 7
    points = [end]
    for delta in (spread, -spread):
        points.append(
            (
                end[0] - length * math.cos(angle + delta),
                end[1] - length * math.sin(angle + delta),
            )
        )
    draw.polygon(points, fill=ROSE)


def annotate_image(
    repo: Path,
    spec: dict[str, Any],
    fonts: tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont],
) -> str:
    restore_mode = restore_pristine(repo, spec)
    path = safe_repo_path(repo, spec["path"])
    shapes = list(spec.get("shapes", []))
    # PLAN_UI_HUB.md กำหนด schema กลางเป็น markers + masks
    # โดยยังรับ shapes ของสคริปต์ต้นฉบับเพื่อคงความสามารถเดิมให้ครบ
    for marker in spec.get("markers", []):
        shape = dict(marker)
        shape.setdefault("type", "round_rect")
        shapes.append(shape)
    for mask_spec in spec.get("masks", []):
        if isinstance(mask_spec, list):
            shapes.append({"type": "mask", "box": mask_spec})
        else:
            shape = dict(mask_spec)
            shape["type"] = "mask"
            shapes.append(shape)
    if not shapes:
        return f"SKIP ({spec.get('reason', 'no interactive target')}); restored by {restore_mode}"

    with Image.open(path) as source:
        original_mode = source.mode
        image = source.convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size

    masks: list[dict[str, Any]] = []
    prepared: list[tuple[dict[str, Any], tuple[int, int, int, int]]] = []
    for index, shape in enumerate(shapes, start=1):
        kind = shape.get("type", "round_rect")
        if kind not in {"mask", "ellipse", "round_rect"}:
            raise ValueError(f"unsupported shape type: {kind}")
        check_box(shape["box"], width, height, f"shape {index} box")
        if kind == "mask":
            text = shape.get("text")
            if text is not None and (not isinstance(text, str) or not text):
                raise ValueError(f"shape {index} mask text must be a non-empty string")
            if text:
                fit_mask_font(draw, fonts[0], text, shape["box"])
            masks.append(shape)
            continue
        text = shape["label"]
        box = label_box(draw, fonts, text, shape["label_at"])
        check_box(list(box), width, height, f"shape {index} label")
        prepared.append((shape, box))

    # Privacy masks always precede every leader, outline, and label, regardless
    # of their order in the annotation schema.
    for shape in masks:
        draw_mask(draw, shape, fonts[0])

    # Leaders remain behind both target outlines and labels.
    for shape, box in prepared:
        target_box = shape["box"]
        target = tuple(
            shape.get(
                "target",
                [(target_box[0] + target_box[2]) / 2, (target_box[1] + target_box[3]) / 2],
            )
        )
        start = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
        arrow(draw, start, target)

    for shape, _ in prepared:
        kind = shape.get("type", "round_rect")
        box = shape["box"]
        if kind == "ellipse":
            draw.ellipse(box, outline=ROSE, width=LINE_WIDTH)
        elif kind == "round_rect":
            draw.rounded_rectangle(box, radius=shape.get("radius", 12), outline=ROSE, width=LINE_WIDTH)

    for shape, box in prepared:
        draw.rounded_rectangle(box, radius=LABEL_RADIUS, fill=SLATE)
        draw_label_text(
            draw,
            (box[0] + LABEL_PADDING_X, box[1] + LABEL_PADDING_Y),
            shape["label"],
            fonts,
        )

    temporary = path.with_name(f".{path.name}.annotating")
    rendered = image if original_mode == "RGBA" else image.convert(original_mode)
    rendered.save(temporary, format="PNG", optimize=True)
    temporary.replace(path)
    return (
        f"OK; {len(masks)} mask(s); {len(prepared)} marker(s); "
        f"restored by {restore_mode}"
    )


def append_log(repo: Path, command: str, results: list[tuple[str, str]]) -> None:
    log = repo / "tools/ui/annotate.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with log.open("a", encoding="utf-8") as handle:
        handle.write(f"\n[{timestamp}] DRAW {command}\n")
        for path, result in results:
            handle.write(f"- {path}: {result}\n")


def spec_paths(repo: Path, selection: str | None, explicit: str | None) -> list[Path]:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = repo / path
        path = path.resolve()
        if repo not in path.parents or path.suffix.lower() != ".json":
            raise ValueError(f"invalid spec path: {explicit}")
        if not path.is_file():
            raise FileNotFoundError(f"annotation spec not found: {path}")
        return [path]
    directory = repo / "tools/ui/annotations"
    if selection == "--all":
        paths = sorted(directory.glob("lab*.json"))
        if not paths:
            raise FileNotFoundError(f"no annotation specs in {directory}")
        return paths
    if not selection.startswith("lab") or not selection[3:].isdigit():
        raise ValueError("selection must be labN or --all")
    path = directory / f"{selection}.json"
    if not path.is_file():
        raise FileNotFoundError(f"annotation spec not found: {path}")
    return [path]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("selection", nargs="?", help="labN (for example, lab1)")
    group.add_argument("--all", action="store_true", help="render every lab*.json spec")
    group.add_argument("--spec", help="spec path relative to the project root")
    args = parser.parse_args()
    selection = "--all" if args.all else args.selection
    try:
        repo = repo_root()
        fonts = load_fonts(repo, FONT_SIZE)
        results: list[tuple[str, str]] = []
        for path in spec_paths(repo, selection, args.spec):
            data = json.loads(path.read_text(encoding="utf-8"))
            for image_spec in data["images"]:
                result = annotate_image(repo, image_spec, fonts)
                results.append((image_spec["path"], result))
                print(f"{image_spec['path']}: {result}")
        command = f"annotate_steps.py --spec {args.spec}" if args.spec else f"annotate_steps.py {selection}"
        append_log(repo, command, results)
        return 0
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
