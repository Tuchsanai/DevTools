#!/usr/bin/env python3
"""Unit tests for privacy-mask rendering in annotate_steps.py."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageFont

from tools.ui.annotate_steps import ROSE, annotate_image


FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


class AnnotateMaskTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.image_path = self.repo / "synthetic.png"
        Image.new("RGB", (400, 240), "white").save(self.image_path)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "synthetic.png"], cwd=self.repo, check=True)
        font = ImageFont.truetype(FONT_PATH, size=28)
        self.fonts = (font, font)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_mask_is_drawn_before_marker_in_same_image(self) -> None:
        spec = {
            "path": "synthetic.png",
            "shapes": [
                {
                    "type": "round_rect",
                    "box": [80, 80, 320, 160],
                    "label": "① marker",
                    "label_at": [10, 10],
                },
                {
                    "type": "mask",
                    "box": [50, 50, 350, 190],
                    "text": "<GITHUB_USER>",
                },
            ],
        }

        annotate_image(self.repo, spec, self.fonts)

        with Image.open(self.image_path) as result:
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(result.size, (400, 240))
            self.assertEqual(result.getpixel((200, 80)), (225, 29, 72))
            self.assertEqual(result.getpixel((340, 180)), (13, 17, 23))
        self.assertEqual(ROSE.lower(), "#e11d48")

    def test_mask_out_of_bounds_raises(self) -> None:
        spec = {
            "path": "synthetic.png",
            "shapes": [
                {
                    "type": "mask",
                    "box": [0, 0, 401, 240],
                    "text": "<GITHUB_USER>",
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "outside 400x240"):
            annotate_image(self.repo, spec, self.fonts)

    def test_rerun_has_identical_sha256(self) -> None:
        spec = {
            "path": "synthetic.png",
            "shapes": [
                {
                    "type": "mask",
                    "box": [40, 90, 360, 150],
                    "text": "a-very-long-github-user-name-for-font-fitting",
                    "fill": "#0d1117",
                }
            ],
        }

        annotate_image(self.repo, spec, self.fonts)
        first = self.sha256(self.image_path)
        annotate_image(self.repo, spec, self.fonts)
        second = self.sha256(self.image_path)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
