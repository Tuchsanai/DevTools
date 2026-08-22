#!/usr/bin/env python3
"""Produce deck-only crops of LAB screenshots.

The LAB READMEs need the full page (context for the click sequence), but a full
page shrunk into a slide panel makes the console text unreadable.  These crops
keep the region a learner actually has to read; the originals stay untouched for
the READMEs.  Re-run after re-capturing any source screenshot.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "slides_assets"

# source -> (output, crop box left/top/right/bottom, what the crop must keep)
CROPS = {
    "lab1_s06_console_output.png": (
        "deck_lab1_console.png",
        (0, 48, 1440, 424),
        "left menu with Console Output selected + the whole console panel",
    ),
    "lab4_s03_github_repo_files.png": (
        "deck_lab4_repo_files.png",
        (100, 190, 1030, 560),
        "branch bar, the boxed four-file list and the marker label",
    ),
    "lab4_s05_jenkins_scm_config.png": (
        "deck_lab4_scm_config.png",
        (388, 55, 1322, 825),
        "Definition, SCM, Repository URL, Credentials and Branch Specifier",
    ),
    "lab6_s12_hub_public_tags.png": (
        "deck_lab6_hub_tags.png",
        (24, 330, 1428, 948),
        "Tags tab plus both tag cards with their digests",
    ),
}


def main() -> None:
    for source, (target, box, note) in CROPS.items():
        src = ASSETS / source
        with Image.open(src) as image:
            if box[2] > image.width or box[3] > image.height:
                raise ValueError(f"crop box escapes {source} ({image.width}x{image.height})")
            cropped = image.crop(box)
            cropped.save(ASSETS / target, optimize=True)
        print(f"crop: {source} {image.width}x{image.height} -> {target} "
              f"{cropped.width}x{cropped.height}  ({note})")


if __name__ == "__main__":
    main()
