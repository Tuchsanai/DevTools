#!/usr/bin/env python3
"""Generate Thai speech with qwen-audio-3.0-tts-plus via DashScope.

Tries, in order:
  1. OpenAI-compatible endpoint  POST {base}/compatible-mode/v1/audio/speech
  2. Native DashScope endpoint   POST {base}/api/v1/services/aigc/multimodal-generation/generation
across CN and INTL regions. Never prints the API key.
"""
import json
import os
import sys
import urllib.error
import urllib.request

API_KEY = os.environ.get("BAILIAN_TOKEN_PLAN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
if not API_KEY:
    print("ERROR: no API key found (BAILIAN_TOKEN_PLAN_API_KEY / DASHSCOPE_API_KEY)")
    sys.exit(2)

MODEL = os.environ.get("TTS_MODEL", "qwen-audio-3.0-tts-plus")
TEXT = os.environ.get(
    "TTS_TEXT",
    "สวัสดีครับ ยินดีต้อนรับสู่การทดลองสังเคราะห์เสียงภาษาไทย ด้วยโมเดลคิวเวน ทีทีเอส",
)
OUT = sys.argv[1] if len(sys.argv) > 1 else "thai_speech.mp3"
VOICES = ["Cherry", None]
REGIONS = [
    "https://dashscope.aliyuncs.com",
    "https://dashscope-intl.aliyuncs.com",
]


def post(url, payload, timeout=180):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # network-level errors
        return -1, str(e).encode("utf-8")


def looks_binary(body):
    return len(body) > 1024 and not body.lstrip()[:1] in (b"{", b"[")


def save(body, how):
    with open(OUT, "wb") as f:
        f.write(body)
    print(f"OK: {len(body)} bytes written to {OUT} via {how}")
    sys.exit(0)


for base in REGIONS:
    # 1) OpenAI-compatible /v1/audio/speech
    for voice in VOICES:
        payload = {"model": MODEL, "input": TEXT, "response_format": "mp3"}
        if voice:
            payload["voice"] = voice
        status, body = post(f"{base}/compatible-mode/v1/audio/speech", payload)
        if status == 200 and looks_binary(body):
            save(body, f"compatible-mode {base} voice={voice}")
        print(f"[compatible {base} voice={voice}] HTTP {status}: {body[:250]!r}")

    # 2) Native multimodal-generation API (returns JSON with an audio URL)
    for voice in VOICES:
        inp = {"text": TEXT}
        if voice:
            inp["voice"] = voice
        payload = {"model": MODEL, "input": inp}
        status, body = post(
            f"{base}/api/v1/services/aigc/multimodal-generation/generation", payload
        )
        if status == 200:
            try:
                data = json.loads(body)
                audio = data.get("output", {}).get("audio", {})
                audio_url = audio.get("url")
                if audio_url:
                    with urllib.request.urlopen(audio_url, timeout=120) as r:
                        save(r.read(), f"native {base} voice={voice}")
            except Exception:
                pass
        print(f"[native {base} voice={voice}] HTTP {status}: {body[:250]!r}")

print("FAILED: all endpoints rejected the request", file=sys.stderr)
sys.exit(1)
