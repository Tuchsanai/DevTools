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

PROJECT_DIR = Path(__file__).resolve().parent
ASSET_DIR = (PROJECT_DIR / "../../slides_assets/motion").resolve()
MANIFEST_PATH = ASSET_DIR / "motion-manifest.json"
FFPROBE = Path("/opt/ffmpeg-safe/bin/ffprobe")
PLAYBACK_SCRIPT = PROJECT_DIR / "validate_playback.cjs"
HARD_CAP_BYTES = 2_500_000
TARGET_BYTES = 1_500_000
LOOP_MAE_LIMIT_PERCENT = 0.75
EXPECTED_FILES = {
    "mo_intro.mp4": ("mo-intro", 8.0),
    "mo_manual_vs_ci.mp4": ("mo-manual-vs-ci", 12.0),
    "mo_pipeline_flow.mp4": ("mo-pipeline-flow", 12.0),
    "mo_polling_vs_webhook.mp4": ("mo-polling-vs-webhook", 12.0),
    "mo_dood_socket.mp4": ("mo-dood-socket", 12.0),
    "mo_lab4_sha_digest.mp4": ("mo-lab4-sha-digest", 8.0),
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


def image_diff_percent(first_png: bytes, last_png: bytes) -> float:
    first = Image.open(io.BytesIO(first_png)).convert("RGB")
    last = Image.open(io.BytesIO(last_png)).convert("RGB")
    check(first.size == (1280, 720) and last.size == first.size, f"unexpected screenshot dimensions: {first.size}, {last.size}")
    difference = ImageChops.difference(first, last)
    mean = ImageStat.Stat(difference).mean
    return sum(mean) / (3 * 255) * 100


def main() -> None:
    check(FFPROBE.is_file(), f"ffprobe missing: {FFPROBE}")
    check(MANIFEST_PATH.is_file(), f"manifest missing: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    check(manifest.get("schemaVersion") == 1, "manifest schemaVersion must be 1")
    entries = manifest.get("clips")
    check(isinstance(entries, list) and len(entries) == 6, "manifest must contain exactly 6 clips")
    check({entry.get("file") for entry in entries} == set(EXPECTED_FILES), "manifest clip set mismatch")

    durations = {entry["file"]: validate_metadata(entry) for entry in entries}
    temp_dir = PROJECT_DIR / ".validate-tmp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    try:
        check(PLAYBACK_SCRIPT.is_file(), f"playback validator missing: {PLAYBACK_SCRIPT}")
        subprocess.run(
            ["node", str(PLAYBACK_SCRIPT), str(MANIFEST_PATH), str(ASSET_DIR), str(temp_dir)],
            cwd=PROJECT_DIR,
            check=True,
        )
        for entry in entries:
            filename = entry["file"]
            first_png = (temp_dir / f"{filename}.first.png").read_bytes()
            last_png = (temp_dir / f"{filename}.last.png").read_bytes()
            mae_percent = image_diff_percent(first_png, last_png)
            check(mae_percent <= LOOP_MAE_LIMIT_PERCENT, f"{filename}: loop MAE {mae_percent:.4f}% exceeds {LOOP_MAE_LIMIT_PERCENT:.2f}%")
            duration = durations[filename]
            print(f"LOOP PASS {filename}: t=0.001 vs t={duration - 0.05:.3f} MAE={mae_percent:.4f}% <= {LOOP_MAE_LIMIT_PERCENT:.2f}%")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("VALIDATION PASS: 6/6 metadata + local-Playwright autoplay + currentTime + loop-frame checks")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"VALIDATION FAIL: {type(error).__name__}: {error}")
        raise SystemExit(1)
