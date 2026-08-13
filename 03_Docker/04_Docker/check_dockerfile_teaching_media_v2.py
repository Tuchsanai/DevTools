#!/opt/venv/bin/python3
"""ตรวจความสมบูรณ์พื้นฐานของ dockerfile_teaching_media_v2.html"""

from pathlib import Path
import sys

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / "dockerfile_teaching_media_v2.html"


def fail(message: str) -> None:
    print(f"ไม่ผ่าน: {message}")
    raise SystemExit(1)


def main() -> None:
    if not HTML_FILE.is_file():
        fail(f"ไม่พบไฟล์ {HTML_FILE.name}")

    try:
        soup = BeautifulSoup(HTML_FILE.read_text(encoding="utf-8"), "html.parser")
    except Exception as error:
        fail(f"BeautifulSoup parse HTML ไม่สำเร็จ: {error}")

    if not all((soup.html, soup.head, soup.body, soup.main)):
        fail("โครงสร้างหลัก html/head/body/main ไม่ครบ")
    print("ผ่าน (1) BeautifulSoup parse HTML และพบโครงสร้างหลักครบ")

    missing_images: list[str] = []
    invalid_image_paths: list[str] = []
    for image in soup.find_all("img"):
        src = image.get("src")
        if not src:
            invalid_image_paths.append("<ไม่มี src>")
            continue
        image_path = Path(src)
        if image_path.is_absolute() or image_path.parts[:1] != ("slides_assets",):
            invalid_image_paths.append(src)
        elif not (ROOT / image_path).is_file():
            missing_images.append(src)
        if not image.get("alt", "").strip():
            fail(f"รูป {src} ไม่มี alt ภาษาไทย")

    if invalid_image_paths:
        fail(f"img src ต้องเป็นไฟล์ใน slides_assets เท่านั้น: {invalid_image_paths}")
    if missing_images:
        fail(f"ไม่พบไฟล์รูป: {missing_images}")
    print(f"ผ่าน (2) img ทั้ง {len(soup.find_all('img'))} รูปมีไฟล์จริงใน slides_assets และมี alt")

    ids = {tag["id"] for tag in soup.find_all(attrs={"id": True})}
    nav_links = soup.select("nav a[href]")
    broken_anchors: list[str] = []
    for link in nav_links:
        href = link.get("href", "")
        if not href.startswith("#") or href[1:] not in ids:
            broken_anchors.append(href)
    if broken_anchors:
        fail(f"nav มี anchor ที่ไม่มี id ปลายทาง: {broken_anchors}")
    if len(nav_links) != 11:
        fail(f"nav ต้องมี 11 ลิงก์ แต่พบ {len(nav_links)}")
    print("ผ่าน (3) nav ทั้ง 11 ลิงก์มี id ปลายทางครบ")

    sections = soup.select("main > section")
    if len(sections) != 11:
        fail(f"ต้องมี section ระดับบนสุด 11 ตอน แต่พบ {len(sections)}")
    if any(not section.get("id") for section in sections):
        fail("มี section ที่ไม่มี id")
    if any(not section.select_one(".badge") for section in sections):
        fail("มี section ที่ไม่มี badge ระดับความยาก")
    if any(not section.select_one(".learning") for section in sections):
        fail("มี section ที่ไม่มีข้อความ 'จะได้อะไรจากตอนนี้'")
    print("ผ่าน (4) มี section ครบ 11 ตอน พร้อม id, badge และผลลัพธ์การเรียนรู้")

    print(f"ตรวจสำเร็จ: {HTML_FILE.name}")


if __name__ == "__main__":
    main()
