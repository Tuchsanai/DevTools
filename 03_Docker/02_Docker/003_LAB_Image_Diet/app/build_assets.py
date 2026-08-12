"""ขั้นตอน build ของฝั่ง frontend (จำลองแบบง่าย ๆ)

อ่าน style.css แล้วบีบ (minify) ให้เหลือ static/style.min.css
พร้อมบันทึกข้อมูลการ build ลง static/build_info.json

สคริปต์นี้ถูกเรียก "เฉพาะใน builder stage" ของ v3/Dockerfile เท่านั้น
image สุดท้ายจึงได้แค่ผลลัพธ์ ไม่ต้องแบกเครื่องมือ build ไปด้วย
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"


def minify(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)      # ตัด comment
    css = re.sub(r"\s+", " ", css)                        # ยุบช่องว่าง
    css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)          # ตัดช่องว่างรอบสัญลักษณ์
    css = css.replace(";}", "}")
    return css.strip()


def main() -> None:
    raw = (APP_DIR / "style.css").read_text(encoding="utf-8")
    small = minify(raw)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "style.min.css").write_text(small, encoding="utf-8")
    info = {
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "raw_bytes": len(raw.encode("utf-8")),
        "min_bytes": len(small.encode("utf-8")),
    }
    (STATIC_DIR / "build_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(f"[build_assets] style.css {info['raw_bytes']} B -> style.min.css {info['min_bytes']} B")


if __name__ == "__main__":
    main()
