#!/opt/venv/bin/python
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ASSET_DIR = (PROJECT_DIR / "../../slides_assets/motion").resolve()
FFPROBE = Path("/opt/ffmpeg-safe/bin/ffprobe")

SPECS = [
    ("mo_intro.mp4", "mo-intro"),
    ("mo_manual_vs_ci.mp4", "mo-manual-vs-ci"),
    ("mo_pipeline_flow.mp4", "mo-pipeline-flow"),
    ("mo_polling_vs_webhook.mp4", "mo-polling-vs-webhook"),
    ("mo_dood_socket.mp4", "mo-dood-socket"),
]


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def make_entry(filename: str, composition_id: str) -> dict:
    path = ASSET_DIR / filename
    metadata = probe(path)
    video_streams = [stream for stream in metadata["streams"] if stream["codec_type"] == "video"]
    audio_streams = [stream for stream in metadata["streams"] if stream["codec_type"] == "audio"]
    if len(video_streams) != 1:
        raise RuntimeError(f"{filename}: expected exactly one video stream")
    video = video_streams[0]
    numerator, denominator = (int(value) for value in video["r_frame_rate"].split("/"))
    return {
        "file": filename,
        "compositionId": composition_id,
        "durationSec": round(float(metadata["format"]["duration"]), 3),
        "fps": numerator / denominator,
        "width": int(video["width"]),
        "height": int(video["height"]),
        "codec": video["codec_name"],
        "hasAudio": bool(audio_streams),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main() -> None:
    payload = {"schemaVersion": 1, "clips": [make_entry(*spec) for spec in SPECS]}
    destination = ASSET_DIR / "motion-manifest.json"
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
