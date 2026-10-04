#!/usr/bin/env python3
"""lint_work_items.py — ตรวจความครบถ้วน (hygiene) ของ work item ทั้งโปรเจกต์ผ่าน REST API

    python lint_work_items.py --project PLAB [--include-sub]

แต่ละ work item ให้คะแนน 5 ข้อ: มีเกณฑ์การยอมรับ (checkbox/หัวข้อ AC) · มี assignee · priority ไม่ใช่ none ·
มี due date · มี label — พิมพ์ตารางสีและคะแนนรวมของทีม (sub-work item ถูกข้ามโดยปริยาย เพราะรับบริบทจาก parent)
"""
import argparse
import re

from planeapi import Plane

G, R, Y, B, D, N = "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[2m", "\033[0m"
OK, NO = f"{G}✓{N}", f"{R}✗{N}"
AC_RE = re.compile(r'data-type="taskItem"|เกณฑ์การยอมรับ|Acceptance Criteria|\[[ x]\]', re.I)


def check(item: dict) -> dict:
    html = item.get("description_html") or ""
    return {
        "AC": bool(AC_RE.search(html)),
        "Assignee": bool(item.get("assignees")),
        "Priority": (item.get("priority") or "none") != "none",
        "Due": bool(item.get("target_date")),
        "Labels": bool(item.get("labels")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="PLAB")
    ap.add_argument("--include-sub", action="store_true", help="ตรวจ sub-work item ด้วย")
    a = ap.parse_args()

    p = Plane()
    proj = p.project(a.project)
    items = sorted(p.work_items(proj["id"]), key=lambda i: i["sequence_id"])
    skipped = [i for i in items if i.get("parent")]
    if not a.include_sub:
        items = [i for i in items if not i.get("parent")]

    cols = ["AC", "Assignee", "Priority", "Due", "Labels"]
    print(f"\n{B}Work-item hygiene — {proj['name']} ({proj['identifier']}){N}   token remaining: {p.remaining}\n")
    print(B + f"{'ID':9}" + "".join(f"{c:>9}" for c in cols) + "   คะแนน  ชื่อ" + N)
    total = 0
    for it in items:
        res = check(it)
        score = sum(res.values())
        total += score
        colour = G if score == 5 else (Y if score >= 3 else R)
        key = f"{proj['identifier']}-{it['sequence_id']}"
        cells = "".join(" " * 8 + (OK if v else NO) for v in res.values())
        print(f"{key:9}{cells}   {colour}{score}/5{N}    {it['name']}")
    n = len(items)
    pct = (100 * total // (5 * n)) if n else 0
    colour = G if pct >= 80 else (Y if pct >= 50 else R)
    print(f"\n{B}Team hygiene score: {colour}{total}/{5 * n} ({pct}%){N}" + (f"  {D}(ข้าม sub-work item {len(skipped)} รายการ){N}" if skipped and not a.include_sub else ""))
    print(f"{D}เกณฑ์: AC = มี checkbox หรือหัวข้อ 'เกณฑ์การยอมรับ' ใน description · Priority ≠ none · Due = target_date · Labels ≥ 1{N}\n")


if __name__ == "__main__":
    main()
