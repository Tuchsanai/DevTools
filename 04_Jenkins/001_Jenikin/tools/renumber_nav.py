#!/usr/bin/env python3
"""Rewrite the two navigation tables from where the slides actually are.

Slide 2 lists the chapters, the LAB Sequence slide lists the six labs; both carry
`data-goto="N"` and a visible "หน้า N".  Any insertion earlier in the deck moves
those targets, so they are derived from the current deck rather than kept by hand.

Usage: python3 tools/renumber_nav.py [--check]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "slides_src.html"
US = "␟"


def slides(text: str) -> list[str]:
    block = text.split('<script id="slideData" type="text/plain">')[1].split("</script>")[0].strip()
    return block.split("\n")


def targets(lines: list[str]) -> dict[str, int]:
    found: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        p = line.split(US)
        if p[1] == "labopen":
            found[f"LAB{p[2]}"] = i
        elif p[1] == "section":
            found.setdefault(f"section:{p[2]}", i)
    return found


def renumber(line: str, order: list[int]) -> str:
    """Replace the Nth data-goto/หน้า pair with the Nth page in `order`."""
    it = iter(order)
    line = re.sub(r'data-goto="\d+"', lambda m: f'data-goto="{next(it)}"', line)
    it = iter(order)
    return re.sub(r'class="pg">หน้า \d+<', lambda m: f'class="pg">หน้า {next(it)}<', line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ตรวจอย่างเดียว ไม่แก้ไฟล์")
    args = ap.parse_args()

    text = SRC.read_text(encoding="utf-8")
    lines = slides(text)
    t = targets(lines)

    chapters = ["section:1", "section:2", "LAB1", "section:4", "section:5", "section:6", "section:สรุป"]
    missing = [k for k in chapters + [f"LAB{n}" for n in range(1, 7)] if k not in t]
    if missing:
        print(f"[FAIL] ไม่พบหน้าเป้าหมาย: {', '.join(missing)}")
        return 1

    plan = {
        "โครงสร้างบทเรียน": [t[k] for k in chapters],
        "ภาคปฏิบัติ": [t[f"LAB{n}"] for n in range(1, 7)],
    }

    changed = 0
    for i, line in enumerate(lines):
        eyebrow = line.split(US)[2] if len(line.split(US)) > 2 else ""
        if eyebrow in plan and "data-goto=" in line:
            updated = renumber(line, plan[eyebrow])
            if updated != line:
                lines[i] = updated
                changed += 1
                print(f"อัปเดตตารางนำทางหน้า {i + 1} ({eyebrow}) -> {plan[eyebrow]}")
            else:
                print(f"หน้า {i + 1} ({eyebrow}) ตรงอยู่แล้ว -> {plan[eyebrow]}")

    if args.check:
        print("ตรวจอย่างเดียว: " + ("ต้องแก้" if changed else "ตรงทั้งหมด"))
        return 1 if changed else 0
    if changed:
        block = text.split('<script id="slideData" type="text/plain">')[1].split("</script>")[0].strip()
        SRC.write_text(text.replace(block, "\n".join(lines), 1), encoding="utf-8")
    print(f"แก้ตารางนำทาง {changed} หน้า")
    return 0


if __name__ == "__main__":
    sys.exit(main())
