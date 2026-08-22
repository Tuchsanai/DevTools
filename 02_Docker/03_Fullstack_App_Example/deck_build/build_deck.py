#!/usr/bin/env python3
"""ประกอบไฟล์ part ใน deck_build/ กลับเป็น Fullstack_App_Example.html

แก้เนื้อหาที่ไฟล์ part เท่านั้น — ห้ามแก้ไฟล์เด็คตรง ๆ เพราะจะถูกเขียนทับ
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DECK = ROOT / "Fullstack_App_Example.html"

PARTS = [
    "s0_open.html", "s1_customer.html", "s2_require.html", "s3_design.html",
    "s4_lab1.html", "s5_lab2.html", "s6_lab3.html", "s7_lab4.html",
    "s8_lab5.html", "s9_summary.html",
]
MARK = re.compile(r"<!-- ===== \d+ :([^\n]*?===== -->)")


def renumber(html: str) -> str:
    n = 0
    def rep(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        return f"<!-- ===== {n} :{m.group(1)}"
    return MARK.sub(rep, html)


def main() -> int:
    argv = sys.argv[1:]
    target = DECK
    if "--output" in argv:
        target = Path(argv[argv.index("--output") + 1]).resolve()
    missing = [p for p in ["_head.html", "_tail.html", *PARTS] if not (HERE / p).exists()]
    if missing:
        print(f"[FAIL] ไม่พบไฟล์ part: {missing}")
        return 1
    out = (HERE / "_head.html").read_text(encoding="utf-8")
    for p in PARTS:
        out += (HERE / p).read_text(encoding="utf-8")
    out += (HERE / "_tail.html").read_text(encoding="utf-8")
    out = renumber(out)

    slots = out.count('<div class="slot"')
    marks = len(MARK.findall(out))
    secs = out.count('<section class="slide')
    if not (slots == marks == secs):
        print(f"[FAIL] นับไม่ตรง: slot={slots} marker={marks} section={secs}")
        return 1

    old = target.read_text(encoding="utf-8") if target.exists() else ""
    target.write_text(out, encoding="utf-8")
    status = "ไม่เปลี่ยน" if out == old else f"เปลี่ยน ({len(old)} -> {len(out)} bytes)"
    print(f"[OK] ประกอบเด็ค {slots} สไลด์ -> {target.name} · {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
