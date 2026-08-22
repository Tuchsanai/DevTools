#!/usr/bin/env python3
"""แยก Fullstack_App_Example.html ออกเป็นไฟล์ part ใน deck_build/ (รันครั้งเดียวตอนตั้งระบบ)."""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "Fullstack_App_Example.html"
OUT = ROOT / "deck_build"

# ชื่อไฟล์ part ต่อค่า data-sec ("" = ก่อนตอนที่ 1)
PART_BY_SEC = {
    "":  "s0_open.html",
    "1": "s1_customer.html",
    "2": "s2_require.html",
    "3": "s3_design.html",
    "4": "s4_lab1.html",
    "5": "s5_lab2.html",
    "6": "s6_lab3.html",
    "7": "s7_lab4.html",
    "8": "s8_lab5.html",
    "9": "s9_summary.html",
}
MARK = re.compile(r"<!-- ===== \d+ : [^\n]*? ===== -->")
TAIL_ANCHOR = '</div><!-- /stage -->'


def main() -> int:
    html = DECK.read_text(encoding="utf-8")
    marks = list(MARK.finditer(html))
    if len(marks) != html.count('<div class="slot"'):
        print(f"[FAIL] marker {len(marks)} != slot {html.count(chr(60)+'div class=' + chr(34) + 'slot' + chr(34))}")
        return 1
    tail_at = html.index(TAIL_ANCHOR)

    head = html[: marks[0].start()]
    tail = html[tail_at:]

    blocks = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else tail_at
        blocks.append(html[m.start(): end])

    groups: dict[str, list[str]] = {k: [] for k in PART_BY_SEC}
    cur = ""
    for b in blocks:
        sec = re.search(r'<div class="slot"\s+data-sec="(\d+)"', b)
        if sec:
            cur = sec.group(1)
        groups[cur].append(b)

    OUT.mkdir(exist_ok=True)
    (OUT / "_head.html").write_text(head, encoding="utf-8")
    (OUT / "_tail.html").write_text(tail, encoding="utf-8")
    for sec, name in PART_BY_SEC.items():
        (OUT / name).write_text("".join(groups[sec]), encoding="utf-8")
        print(f"{name:22s} {len(groups[sec]):>3} สไลด์")
    print(f"_head.html / _tail.html  เขียนแล้ว")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
