#!/opt/venv/bin/python
from __future__ import annotations

import hashlib
import io
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import Page, sync_playwright

PROJECT_DIR = Path(__file__).resolve().parent
ASSET_DIR = (PROJECT_DIR / "../../slides_assets/motion").resolve()
MANIFEST_PATH = ASSET_DIR / "motion-manifest.json"
FFPROBE = Path("/opt/ffmpeg-safe/bin/ffprobe")
HARD_CAP_BYTES = 2_500_000
TARGET_BYTES = 1_500_000
LOOP_MAE_LIMIT_PERCENT = 0.75
EXPECTED_FILES = {
    "mo_intro.mp4": ("mo-intro", 8.0),
    "mo_manual_vs_ci.mp4": ("mo-manual-vs-ci", 12.0),
    "mo_pipeline_flow.mp4": ("mo-pipeline-flow", 12.0),
    "mo_polling_vs_webhook.mp4": ("mo-polling-vs-webhook", 12.0),
    "mo_dood_socket.mp4": ("mo-dood-socket", 12.0),
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def ffprobe(path: Path) -> dict:
    result = subprocess.run(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_name,codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def validate_metadata(entry: dict) -> float:
    filename = entry["file"]
    check(filename in EXPECTED_FILES, f"unexpected manifest file: {filename}")
    path = ASSET_DIR / filename
    check(path.is_file(), f"missing file: {path}")
    composition_id, expected_duration = EXPECTED_FILES[filename]
    required = {"file", "compositionId", "durationSec", "fps", "width", "height", "codec", "hasAudio", "bytes", "sha256"}
    check(required.issubset(entry), f"{filename}: missing manifest field(s): {sorted(required - set(entry))}")

    metadata = ffprobe(path)
    video_streams = [stream for stream in metadata["streams"] if stream["codec_type"] == "video"]
    audio_streams = [stream for stream in metadata["streams"] if stream["codec_type"] == "audio"]
    check(len(video_streams) == 1, f"{filename}: expected one video stream")
    check(not audio_streams, f"{filename}: audio stream must be absent")
    video = video_streams[0]
    duration = float(metadata["format"]["duration"])
    fps = float(Fraction(video["r_frame_rate"]))
    size = path.stat().st_size
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    check(video["codec_name"] == "h264", f"{filename}: codec={video['codec_name']}, expected h264")
    check((int(video["width"]), int(video["height"])) == (1280, 720), f"{filename}: expected 1280x720")
    check(math.isclose(fps, 30.0, abs_tol=0.001), f"{filename}: fps={fps}")
    check(6.0 <= duration <= 14.0, f"{filename}: duration outside 6-14s: {duration}")
    check(math.isclose(duration, expected_duration, abs_tol=0.05), f"{filename}: expected duration {expected_duration}, got {duration}")
    check(size <= HARD_CAP_BYTES, f"{filename}: {size} bytes exceeds hard cap {HARD_CAP_BYTES}")

    check(entry["compositionId"] == composition_id, f"{filename}: compositionId mismatch")
    check(entry["codec"] == video["codec_name"], f"{filename}: manifest codec mismatch")
    check(entry["hasAudio"] is False, f"{filename}: manifest hasAudio must be false")
    check(int(entry["width"]) == int(video["width"]) and int(entry["height"]) == int(video["height"]), f"{filename}: manifest dimensions mismatch")
    check(math.isclose(float(entry["fps"]), fps, abs_tol=0.001), f"{filename}: manifest fps mismatch")
    check(math.isclose(float(entry["durationSec"]), duration, abs_tol=0.01), f"{filename}: manifest duration mismatch")
    check(int(entry["bytes"]) == size, f"{filename}: manifest byte count mismatch")
    check(entry["sha256"] == digest, f"{filename}: manifest sha256 mismatch")

    target = "TARGET_OK" if size <= TARGET_BYTES else "TARGET_WARN"
    print(f"METADATA PASS {filename}: codec=h264 audio=none duration={duration:.3f}s fps={fps:.3f} dim=1280x720 bytes={size} {target} sha256={digest}")
    return duration


def seek(page: Page, time_sec: float) -> None:
    page.evaluate(
        """async (timeSec) => {
          const video = document.querySelector('video');
          await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error('seek timeout')), 8000);
            const done = () => { clearTimeout(timeout); resolve(); };
            video.addEventListener('seeked', done, {once: true});
            video.currentTime = timeSec;
            if (Math.abs(video.currentTime - timeSec) < 0.002 && video.readyState >= 2) done();
          });
          video.pause();
          await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        }""",
        time_sec,
    )


def image_diff_percent(first_png: bytes, last_png: bytes) -> float:
    first = Image.open(io.BytesIO(first_png)).convert("RGB")
    last = Image.open(io.BytesIO(last_png)).convert("RGB")
    check(first.size == (1280, 720) and last.size == first.size, f"unexpected screenshot dimensions: {first.size}, {last.size}")
    difference = ImageChops.difference(first, last)
    mean = ImageStat.Stat(difference).mean
    return sum(mean) / (3 * 255) * 100


def validate_playback(page: Page, html_path: Path, entry: dict, duration: float) -> None:
    filename = entry["file"]
    source = (ASSET_DIR / filename).as_uri()
    html_path.write_text(
        f"""<!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;width:1280px;height:720px;background:#f8fafc;overflow:hidden}}
        video{{display:block;width:1280px;height:720px;object-fit:contain}}
        </style></head><body><video id="video" src="{source}" autoplay muted loop playsinline></video></body></html>""",
        encoding="utf-8",
    )
    page.goto(html_path.as_uri(), wait_until="load")
    page.wait_for_function("document.querySelector('video').readyState >= 2")
    page.evaluate("document.querySelector('video').play()")
    start_time = float(page.locator("video").evaluate("video => video.currentTime"))
    page.wait_for_timeout(650)
    end_time = float(page.locator("video").evaluate("video => video.currentTime"))
    paused = bool(page.locator("video").evaluate("video => video.paused"))
    check(not paused, f"{filename}: autoplay video is paused")
    check(end_time - start_time >= 0.25, f"{filename}: currentTime did not advance ({start_time:.3f}->{end_time:.3f})")

    seek(page, 0.001)
    first_png = page.locator("video").screenshot(type="png")
    seek(page, max(0.001, duration - 0.05))
    last_png = page.locator("video").screenshot(type="png")
    mae_percent = image_diff_percent(first_png, last_png)
    check(mae_percent <= LOOP_MAE_LIMIT_PERCENT, f"{filename}: loop MAE {mae_percent:.4f}% exceeds {LOOP_MAE_LIMIT_PERCENT:.2f}%")
    print(f"PLAYBACK PASS {filename}: autoplay currentTime={start_time:.3f}->{end_time:.3f}s; loop t=0.001 vs t={duration - 0.05:.3f} MAE={mae_percent:.4f}% <= {LOOP_MAE_LIMIT_PERCENT:.2f}%")


def main() -> None:
    check(FFPROBE.is_file(), f"ffprobe missing: {FFPROBE}")
    check(MANIFEST_PATH.is_file(), f"manifest missing: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    check(manifest.get("schemaVersion") == 1, "manifest schemaVersion must be 1")
    entries = manifest.get("clips")
    check(isinstance(entries, list) and len(entries) == 5, "manifest must contain exactly 5 clips")
    check({entry.get("file") for entry in entries} == set(EXPECTED_FILES), "manifest clip set mismatch")

    durations = {entry["file"]: validate_metadata(entry) for entry in entries}
    temp_dir = PROJECT_DIR / ".validate-tmp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    html_path = temp_dir / "probe.html"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--allow-file-access-from-files", "--autoplay-policy=no-user-gesture-required"],
            )
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            for entry in entries:
                validate_playback(page, html_path, entry, durations[entry["file"]])
            browser.close()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("VALIDATION PASS: 5/5 metadata + autoplay + currentTime + loop-frame checks")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"VALIDATION FAIL: {type(error).__name__}: {error}")
        raise SystemExit(1)
