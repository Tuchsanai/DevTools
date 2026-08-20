#!/usr/bin/env python3
"""ตรวจ regression ของเอกสารและภาพ UI ทั้งชุด CampusOps."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[2]
LAB_READMES = sorted(ROOT.glob("00?_LAB_*/readme.md"))
READMES = [ROOT / "readme.md", *LAB_READMES]
ANNOTATIONS = sorted((ROOT / "tools/ui/annotations").glob("lab*.json"))
ROSE = (225, 29, 72)
SLATE = (30, 41, 59)
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
QUESTION_ENDINGS = ("ไหม", "อะไร", "อย่างไร")

# ประกอบค่าขณะรันเพื่อไม่ให้ข้อความที่ต้องกำจัดตกค้างใน source ของตัวตรวจเอง
FORBIDDEN = (
    "local" + "host:" + str(5000),
    "registry" + ":" + str(2),
    "ops" + "-registry",
    "VREG" + "_PORT",
    "--for" + "mat \"table",
    "devtools-" + "ops-lab",
    *tuple(str(2237 + offset) for offset in range(1, 6)),
    f"{8088}:{8088}",
    *tuple(str(8188 + offset) for offset in range(1, 4)),
    str(5000 + 39),
)


class Checks:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes = 0

    def check(self, condition: bool, message: str) -> None:
        if condition:
            self.passes += 1
            print(f"[PASS] {message}")
        else:
            self.failures.append(message)
            print(f"[FAIL] {message}")


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append(path)
    return files


def forbidden_scan(checks: Checks) -> None:
    hits: list[str] = []
    for path in text_files():
        text = path.read_text(encoding="utf-8")
        for index, value in enumerate(FORBIDDEN, start=1):
            for line_no, line in enumerate(text.splitlines(), start=1):
                if value in line:
                    hits.append(f"{path.relative_to(ROOT)}:{line_no} [กลุ่ม {index}]")
    checks.check(not hits, "ไม่พบชื่อกล่อง พอร์ต รูปแบบคำสั่ง และ endpoint ชุดเดิม")
    for hit in hits:
        print(f"       {hit}")


def markdown_links(checks: Checks) -> None:
    missing: list[str] = []
    image_count = 0
    pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    for readme in READMES:
        for match in pattern.finditer(readme.read_text(encoding="utf-8")):
            target = match.group(1).split(" ", 1)[0]
            if target.startswith(("http://", "https://", "data:")):
                continue
            image_count += 1
            resolved = (readme.parent / unquote(target)).resolve()
            if not resolved.is_file():
                missing.append(f"{readme.relative_to(ROOT)} -> {target}")
    checks.check(not missing, f"ลิงก์ภาพ Markdown {image_count} รายการชี้ไฟล์ที่มีอยู่จริง")
    for item in missing:
        print(f"       {item}")


def experiment_headings(checks: Checks) -> None:
    heading_re = re.compile(r"^## การทดลองที่ (\d+) — (.+)$", re.MULTILINE)
    problems: list[str] = []
    for readme in LAB_READMES:
        headings = [(int(number), title) for number, title in heading_re.findall(readme.read_text(encoding="utf-8"))]
        numbers = [number for number, _ in headings]
        if numbers != list(range(1, len(numbers) + 1)):
            problems.append(f"{readme.parent.name}: ลำดับ {numbers}")
        for number, title in headings:
            if title.endswith(("?", "？")) or not title.endswith(QUESTION_ENDINGS):
                problems.append(f"{readme.parent.name}: การทดลองที่ {number} ลงท้ายไม่ตรงรูปแบบ")
    checks.check(not problems, "หัวข้อการทดลองเรียงต่อเนื่องและลงท้ายด้วยคำถามภาษาไทยโดยไม่มีเครื่องหมายคำถาม")
    for problem in problems:
        print(f"       {problem}")


def ui_document_format(checks: Checks) -> None:
    problems: list[str] = []
    refs = 0
    image_re = re.compile(r"!\[[^\]]*\]\((?:\./)?images/(ui-[^)]+\.png)\)")
    step_re = re.compile(r"^#### ขั้นที่ [①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳](?:[–-][①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳])? — ")
    for readme in LAB_READMES:
        lines = readme.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not image_re.search(line):
                continue
            refs += 1
            prior = lines[max(0, index - 20):index]
            if not any(step_re.match(item) for item in prior):
                problems.append(f"{readme.relative_to(ROOT)}:{index + 1} ไม่มีหัวข้อขั้นที่ก่อนภาพ")
            after = lines[index + 1:index + 4]
            if not any(re.fullmatch(r"\*ภาพที่ .+\*", item) for item in after):
                problems.append(f"{readme.relative_to(ROOT)}:{index + 1} ไม่มี caption ตัวเอียง")
    checks.check(not problems, f"ภาพ UI ในเอกสาร {refs} ใบมีหัวข้อขั้นและ caption รูปแบบเดียวกัน")
    for problem in problems:
        print(f"       {problem}")


def color_count(image: Image.Image, color: tuple[int, int, int]) -> int:
    return sum(1 for pixel in image.convert("RGB").get_flattened_data() if pixel == color)


def annotation_checks(checks: Checks) -> None:
    problems: list[str] = []
    targets: set[Path] = set()
    total = 0
    for spec_path in ANNOTATIONS:
        try:
            data = json.loads(spec_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            problems.append(f"{spec_path.relative_to(ROOT)} parse ไม่ได้: {error}")
            continue
        sequence: list[int] = []
        for image_spec in data.get("images", []):
            total += 1
            if "markers" in image_spec or "masks" in image_spec or "shapes" not in image_spec:
                problems.append(f"{spec_path.name}: {image_spec.get('path')} ไม่ใช้ schema shapes")
                continue
            target = ROOT / image_spec["path"]
            source = ROOT / image_spec.get("source", "")
            targets.add(target.resolve())
            if not target.is_file() or not source.is_file():
                problems.append(f"{spec_path.name}: source/target หายสำหรับ {image_spec['path']}")
                continue
            with Image.open(target) as marked, Image.open(source) as raw:
                if marked.size != (1440, 900) or raw.size != (1440, 900):
                    problems.append(f"{image_spec['path']}: ขนาด marked/raw ไม่ใช่ 1440x900")
                if ImageChops.difference(marked.convert("RGB"), raw.convert("RGB")).getbbox() is None:
                    problems.append(f"{image_spec['path']}: ภาพ marker เหมือนภาพดิบ")
                if color_count(marked, ROSE) < 100 or color_count(marked, SLATE) < 100:
                    problems.append(f"{image_spec['path']}: ไม่พบสีกรอบหรือป้าย marker เพียงพอ")
            for shape in image_spec["shapes"]:
                if shape.get("type", "round_rect") == "mask":
                    continue
                label = shape.get("label", "")
                if not label or label[0] not in CIRCLED:
                    problems.append(f"{spec_path.name}: marker ไม่มีเลขลำดับใน {image_spec['path']}")
                else:
                    sequence.append(CIRCLED.index(label[0]) + 1)
        expected = list(range(1, len(sequence) + 1))
        if sequence != expected:
            problems.append(f"{spec_path.name}: ลำดับ marker {sequence} ไม่ตรง {expected}")

    referenced: set[Path] = set()
    image_re = re.compile(r"!\[[^\]]*\]\((?:\./)?images/(ui-[^)]+\.png)\)")
    for readme in LAB_READMES:
        for name in image_re.findall(readme.read_text(encoding="utf-8")):
            referenced.add((readme.parent / "images" / name).resolve())
    for path in sorted(referenced - targets):
        problems.append(f"ภาพ UI ไม่มี annotation spec: {path.relative_to(ROOT)}")
    for path in sorted(targets - referenced):
        problems.append(f"ภาพใน annotation spec ไม่ถูกอ้างใน readme: {path.relative_to(ROOT)}")

    checks.check(not problems, f"annotation {len(ANNOTATIONS)} spec / {total} ภาพใช้ schema จริง มี marker และลำดับต่อเนื่อง")
    for problem in problems:
        print(f"       {problem}")


def secret_text_scan(checks: Checks) -> None:
    patterns = (
        re.compile(r"dckr" + r"_pat_", re.IGNORECASE),
        re.compile(r"ghp" + r"_[A-Za-z0-9]+"),
        re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    )
    hits: list[str] = []
    for path in text_files():
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                hits.append(f"{path.relative_to(ROOT)}:{line_no}")
    checks.check(not hits, "ไม่พบ prefix ของ token หรืออีเมลจริงในไฟล์ข้อความ")
    for hit in hits:
        print(f"       {hit}")


def root_table(checks: Checks) -> None:
    text = (ROOT / "readme.md").read_text(encoding="utf-8")
    expected = (
        "| 1 | `devtools-fs-lab1` | 2251 | —",
        "| 2 | `devtools-fs-lab2` | 2252 | `8252:8088`",
        "| 3 | `devtools-fs-lab3` | 2253 | `8253:3000`",
        "| 4 | `devtools-fs-lab4` | 2254 | `8254:3000`",
        "| 5 | `devtools-fs-lab5` | 2255 | `8255:3000`",
    )
    checks.check(all(row in text for row in expected), "ตารางกล่องเรียนหลักตรงกับชื่อและพอร์ตจริงของ LAB 1–5")


def main() -> int:
    checks = Checks()
    forbidden_scan(checks)
    markdown_links(checks)
    experiment_headings(checks)
    ui_document_format(checks)
    annotation_checks(checks)
    secret_text_scan(checks)
    root_table(checks)
    print(f"\nสรุป: PASS {checks.passes} กลุ่ม · FAIL {len(checks.failures)} กลุ่ม")
    return 1 if checks.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
