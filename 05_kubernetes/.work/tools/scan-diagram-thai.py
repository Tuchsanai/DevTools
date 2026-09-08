#!/usr/bin/env python3
"""Extract and audit Thai text in paired SVG and Excalidraw diagrams."""

from __future__ import annotations

import argparse
import collections
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


THAI_RE = re.compile(r"[\u0E00-\u0E7F]")
COLLOQUIAL_PATTERNS = {
    "แล็บ": re.compile(r"แล็บ"),
    "ทดลองให้พัง/ทำให้พัง": re.compile(r"ทดลองให้พัง|ทำให้พัง"),
    "พัง": re.compile(r"พัง"),
    "ทาย/ทายผล": re.compile(r"ทาย(?:ผล)?"),
    "ลอง": re.compile(r"(?<!ทด)(?<!จำ)ลอง"),
    "ดู": re.compile(r"(?<!ผู้)ดู(?!แล)"),
    "เจอ/หาไม่เจอ": re.compile(r"หาให้เจอ|หาไม่เจอ|เจอ"),
    "งง": re.compile(r"งง"),
    "สั่ง": re.compile(r"(?<!คำ)สั่ง"),
    "รัน": re.compile(r"รัน"),
    "เก็บกวาด": re.compile(r"เก็บกวาด"),
    "เช็กลิสต์": re.compile(r"เช็กลิสต์"),
    "สรรพนามบุรุษ": re.compile(r"คุณ(?!สมบัติ)|เรา|ผม"),
    "คำลงท้าย/คำไม่เป็นทางการ": re.compile(r"(?<![\u0E00-\u0E7F])(นะ|ล่ะ|แหละ|ซะ|เลย|ก็|แค่)(?![\u0E00-\u0E7F])"),
    "คำถามไม่เป็นทางการ": re.compile(r"ทำไม|อะไร|ไหม|ยังไง|ใครจะ"),
    "จะได้": re.compile(r"จะได้"),
    "คำบอกเวลาไม่เป็นทางการ": re.compile(r"ตอนนี้|ทีนี้|เดี๋ยว|ตีสาม|กลางดึก"),
    "ลักษณนาม ตัว": re.compile(r"(?<![\u0E00-\u0E7F])ตัว(?![\u0E00-\u0E7F])"),
    "แอบดู": re.compile(r"แอบดู"),
    "คุยกัน": re.compile(r"คุยกัน"),
    "เก็บของ": re.compile(r"เก็บของ"),
    "คำกริยาไม่เป็นทางการ": re.compile(r"(?<![\u0E00-\u0E7F])ขึ้น(?![\u0E00-\u0E7F])|ตาย|(?<!สูญ)(?<!ขาด)หาย|โดน|เอา|มัน"),
    "คำขยายไม่เป็นทางการ": re.compile(r"จริง ๆ|จริงๆ|นิดหน่อย|เยอะ|โอเค|ชัวร์"),
    "ภาษาพูดเพิ่มเติม": re.compile(
        r"เครื่องดับ|คุยกับ|คนนั่งเฝ้า|สมองของ cluster|ประตูของ API|“ซอง”|"
        r"มองแยก|แชร์ IP|บอกปลายทาง|วนตรวจ|กาวของ Kubernetes|selector จับ|"
        r"ของเก่าก่อนเปิดของใหม่|ค่อย ๆ|เครื่องเรียน|ทุกอย่างคือ object|แบ่ง “ห้อง”|"
        r"ในห้องนี้|สร้างห้องแล้ว|ตรง ๆ|สมาชิกหาย|ประตูเดิม|อย่าผูก|"
        r"ทางที่เปราะบาง|ทางที่ทนทาน|ต่างกันที่ใคร|cloud จัดให้|การแปลงรูป ไม่ใช่|"
        r"จะเห็นค่าจริง|ถอดกลับได้|อยู่รอดแค่ไหน|รอด:|ใส่กลับเอง|process ค้าง|"
        r"ฆ่าและเริ่ม|อย่าเช็ก|วนครบหนึ่งรอบ|เพราะอะไร|ตาม Pod ให้เอง|"
        r"ไม่เปิดออกนอก cluster|ไม่ได้แปลว่า|db ล่ม|แอปจริงคือ|ถามก่อน scale|"
        r"Stateless ทิ้ง|ไม่สะดุด|เก็บตัวเก่า|เพิ่มตัวใหม่|Ready แล้ว|"
        r"เหลือพอ|Pod ลง worker|ไล่จากอาการ|ทุกเคส|เสียงของแอป|จุดที่ควรสงสัย|"
        r"Response เดินย้อน|แบบลงมือจริง|หลักฐาน 3 มุม|ทุก object มาจาก|"
        r"เพื่อซ่อม|ครบ 3 ชั้น|ยังอยู่ครบ|ประตูหน้าบ้าน|ไม่เห็น FAIL|"
        r"บอก Kubernetes ว่า|ที่จองไม่พอ|ขอเกินทั้งหมด|เห็นอาการ|ฟังแอป|"
        r"มองตามเวลา|ภาพใหญ่ของระบบ|แก้กลับ"
    ),
}


def compact(value: str) -> str:
    value = html.unescape(value).replace("\u00a0", " ")
    return " ".join(value.split())


def svg_text(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    result: list[str] = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "text":
            continue
        value = compact("".join(node.itertext()))
        if value and THAI_RE.search(value):
            result.append(value)
    return result


def svg_text_blocks(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    result: list[str] = []
    for node in root.iter():
        children = list(node)
        text_children = [child for child in children if child.tag.rsplit("}", 1)[-1] == "text"]
        if not text_children:
            continue
        value = compact(" ".join("".join(child.itertext()) for child in text_children))
        if value:
            result.append(value)
    return result


def excalidraw_text(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result: list[str] = []
    for element in data.get("elements", []):
        if element.get("type") != "text" or element.get("isDeleted"):
            continue
        text = element.get("text", "")
        original = element.get("originalText", text)
        for field, value in (("text", text), ("originalText", original)):
            if not isinstance(value, str):
                continue
            for line in value.splitlines() or [value]:
                line = compact(line)
                if line and THAI_RE.search(line):
                    result.append((field, line))
    return result


def excalidraw_text_blocks(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        compact(element.get("text", ""))
        for element in data.get("elements", [])
        if element.get("type") == "text"
        and not element.get("isDeleted")
        and isinstance(element.get("text"), str)
        and element.get("text")
    ]


def files(root: Path) -> tuple[list[Path], list[Path]]:
    svgs = sorted(root.glob("0*_Session*/slides_assets/*.svg"))
    scenes = sorted(root.glob("0*_Session*/slides_assets/scenes/*.excalidraw"))
    return svgs, scenes


def pair_key(path: Path) -> tuple[str, str]:
    session = next(part for part in path.parts if re.match(r"0\d+_Session", part))
    return session, path.stem


def scan(root: Path) -> dict:
    svgs, scenes = files(root)
    records = []
    pair_text: dict[tuple[str, str], dict[str, list[str]]] = collections.defaultdict(dict)

    for path in svgs:
        texts = svg_text(path)
        pair_text[pair_key(path)]["svg"] = svg_text_blocks(path)
        for value in texts:
            hits = [name for name, pattern in COLLOQUIAL_PATTERNS.items() if pattern.search(value)]
            records.append({"file": str(path.relative_to(root)), "format": "svg", "field": "text", "text": value, "flags": hits})

    for path in scenes:
        values = excalidraw_text(path)
        pair_text[pair_key(path)]["excalidraw"] = excalidraw_text_blocks(path)
        for field, value in values:
            hits = [name for name, pattern in COLLOQUIAL_PATTERNS.items() if pattern.search(value)]
            records.append({"file": str(path.relative_to(root)), "format": "excalidraw", "field": field, "text": value, "flags": hits})

    comparisons = []
    for key, values in sorted(pair_text.items()):
        svg_counter = collections.Counter(values.get("svg", []))
        exc_counter = collections.Counter(values.get("excalidraw", []))
        comparisons.append({
            "session": key[0],
            "name": key[1],
            "match": svg_counter == exc_counter,
            "svg_only": list((svg_counter - exc_counter).elements()),
            "excalidraw_only": list((exc_counter - svg_counter).elements()),
        })

    return {
        "counts": {"svg": len(svgs), "excalidraw": len(scenes), "records": len(records)},
        "records": records,
        "comparisons": comparisons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--mode", choices=("all", "suspects", "compare", "json"), default="suspects")
    args = parser.parse_args()
    report = scan(args.root.resolve())

    if args.mode == "json":
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0
    if args.mode == "compare":
        for item in report["comparisons"]:
            if not item["match"]:
                print(f'{item["session"]}/{item["name"]}\tSVG_ONLY={item["svg_only"]}\tEXCALIDRAW_ONLY={item["excalidraw_only"]}')
        return 1 if any(not item["match"] for item in report["comparisons"]) else 0

    for item in report["records"]:
        if args.mode == "suspects" and not item["flags"]:
            continue
        flags = ",".join(item["flags"]) if item["flags"] else "-"
        print(f'{item["file"]}\t{item["field"]}\t{flags}\t{item["text"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
