#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

echo "[1/4] ตรวจ service ที่กำลังรัน"
docker compose ps --status running --services | sort | diff -u <(printf 'api\nui\n') -

echo "[2/4] ตรวจ health และ Docker DNS จาก container ui"
docker compose exec -T ui python - <<'PY'
import requests

r = requests.get("http://api:8000/health", timeout=5)
r.raise_for_status()
assert r.json()["status"] == "ok", r.text
print(r.json())
PY

echo "[3/4] ตรวจภาพ PNG ที่ OpenCV สร้าง"
docker compose exec -T ui python - <<'PY'
from io import BytesIO
import requests
from PIL import Image

r = requests.get("http://api:8000/demo/edges", timeout=10)
r.raise_for_status()
assert r.headers["content-type"].startswith("image/png")
image = Image.open(BytesIO(r.content))
assert image.size == (720, 420), image.size
assert r.headers["x-process-mode"] == "edges"
print({"content_type": r.headers["content-type"], "size": image.size, "bytes": len(r.content)})
PY

echo "[4/4] ตรวจหน้า Streamlit"
curl --fail --silent --show-error http://localhost:8501/_stcore/health
echo
echo "PASS: LAB 7 acceptance ครบทุกข้อ"
