"""Build tool สำหรับ render หน้า DevOps Board เป็น static artifact ไฟล์เดียว"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


# ข้อความนี้ถูกฝังลงใน artifact เพื่ออธิบายหน้าที่ของ multi-stage build
STAGE_NOTE = (
    "สร้าง static artifact ใน Python build stage แล้วคัดเฉพาะ index.html "
    "ไปยัง nginx runtime stage"
)


def current_utc_time():
    """คืนเวลา UTC ปัจจุบันในรูปแบบที่อ่านง่ายและคงที่"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def main():
    """อ่าน template, render ด้วย Jinja2 และเขียนผลลัพธ์ไปยัง path ที่รับมา"""
    # บังคับให้ระบุ output path เพื่อลดโอกาสเขียน artifact ผิดตำแหน่ง
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} OUTPUT_PATH", file=sys.stderr)
        raise SystemExit(2)

    # อ้าง template จากโฟลเดอร์เดียวกับสคริปต์ จึงเรียกได้จาก working directory ใดก็ได้
    source_dir = Path(__file__).resolve().parent
    output_path = Path(sys.argv[1]).expanduser()
    # ถ้าไม่ได้ส่ง --build-arg BUILD_TIME เข้ามา (ค่าเริ่มต้นคือ unknown) ให้ใช้เวลา UTC ตอน build แทน
    build_time = os.environ.get("BUILD_TIME", "")
    if build_time in ("", "unknown"):
        build_time = current_utc_time()

    # เปิด autoescape สำหรับ HTML และใช้ loader ของ Jinja2 render template จริง
    environment = Environment(
        loader=FileSystemLoader(source_dir),
        autoescape=select_autoescape(("html", "htm", "xml")),
        keep_trailing_newline=True,
    )
    template = environment.get_template("template.html")
    rendered = template.render(BUILD_TIME=build_time, STAGE_NOTE=STAGE_NOTE)

    # สร้างโฟลเดอร์ปลายทางให้อัตโนมัติก่อนเขียน artifact เพียงไฟล์เดียว
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    size = output_path.stat().st_size

    # สรุปผลใน build log เพื่อยืนยัน path, ขนาด artifact และเวลาที่ถูกฝัง
    print(f"[build] rendered {output_path} ({size} bytes) at {build_time}")


# เรียก main เฉพาะเมื่อรันไฟล์นี้เป็นโปรแกรม build tool โดยตรง
if __name__ == "__main__":
    main()
