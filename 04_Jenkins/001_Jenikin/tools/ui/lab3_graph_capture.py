#!/usr/bin/env python3
"""Capture the Pipeline Graph of the LAB 3 build that the console/Hub evidence came from.

Runs against the same build number the console screenshots were taken from, so the
BUILD_NUMBER -> digest -> Hub tag chain the lab has to prove holds across all four
LAB 3 evidence images.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import io

from PIL import Image, ImageDraw

from common import browser_page, jenkins_login, log, require, run_main, wait_visible
from lab4_capture import _text_rectangles, draw_masks

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "slides_assets" / "lab3_pipeline_docker.png"
JOB = "docker-build-push"


def main() -> None:
    base_url = os.environ["JENKINS_BASE_URL"].rstrip("/")
    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/{JOB}/lastBuild/api/json?tree=number,result,building",
                  wait_until="domcontentloaded")
        build = json.loads(page.locator("body").inner_text())
        require(build["result"] == "SUCCESS" and not build["building"],
                f"{JOB} last build finished SUCCESS")
        number = build["number"]

        page.goto(f"{base_url}/job/{JOB}/{number}/console", wait_until="domcontentloaded")
        console = page.locator("body").inner_text()
        require("Login Succeeded" in console, "same build logged in to Docker Hub")
        require(f"{number}: digest: sha256:" in console,
                f"same build pushed tag {number} and printed its digest")

        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(f"{base_url}/job/{JOB}/{number}/stages/", wait_until="networkidle")
        wait_visible(page.locator("#console-pipeline-root"), "Pipeline Graph build-level Stages view")
        body = page.locator("body").inner_text()
        for stage in ("Prepare app", "Build & Push", "Smoke test"):
            require(stage in body, f"Pipeline Graph shows stage {stage}")
        require(f"#{number}" in body, f"Pipeline Graph shows build #{number}")
        # The Stages page prints the real Docker Hub namespace in the stage log,
        # so mask it to the placeholder before anything reaches disk, then keep
        # only the band the lab asks the reader to look at (header + graph + stages).
        docker_user = os.environ["DOCKER_USER"]
        rects = _text_rectangles(page, docker_user)
        raw = page.screenshot(full_page=False)
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        draw_masks(image, rects, "<DOCKER_USER>", 1.0)
        image.crop((0, 0, image.width, 500)).save(TARGET, format="PNG", optimize=True)
        log(f"screenshot: LAB 3 Pipeline Graph of build #{number} "
            f"({len(rects)} namespace mask(s)) -> {TARGET}")
        print(f"CAPTURED_BUILD={number}")


if __name__ == "__main__":
    run_main(main)
