#!/usr/bin/env python3
"""ตรวจว่าตัวเลขของชุดตรงกันทุกไฟล์ — เด็ค · root readme · readme ของแต่ละแล็บ

source of truth
  จำนวนการทดลอง = นับหัวข้อ "การทดลองที่ N" ในไฟล์แล็บ
  จำนวน [PASS]  = logs/verify_counts/labN.json (ได้จากการรัน verify.sh จริง)
  เวลาต่อแล็บ    = ค่าที่เขียนในไฟล์แล็บนั้น
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Fullstack_App_Example.html"
COUNTS = ROOT / "logs/verify_counts"

LABS = sorted(ROOT.glob("00?_LAB_*"))


def strip_deck(html: str) -> str:
    html = re.sub(r'data:image/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+', '', html)
    return re.sub(r"<[^>]+>", " ", html)


def main() -> int:
    fail: list[str] = []
    truth: dict[int, dict] = {}

    for lab in LABS:
        n = int(lab.name[:3])
        body = (lab / "readme.md").read_text(encoding="utf-8")
        heads = {int(m) for m in re.findall(r"^#+ .*?การทดลองที่ (\d+)", body, flags=re.M)}
        exp = len(heads)
        if heads and heads != set(range(1, exp + 1)):
            fail.append(f"LAB {n}: เลขการทดลองไม่ต่อเนื่อง {sorted(heads)}")
        tm = re.search(r"\*\*เวลา\*\*\s*\|\s*~?\s*(\d+)\s*นาที", body)
        claim = re.search(r"การทดลอง\s*\*\*(\d+)\s*อัน\*\*", body)
        truth[n] = {
            "exp": exp,
            "time": int(tm.group(1)) if tm else None,
            "claim_exp": int(claim.group(1)) if claim else None,
            "pass": None, "skip": None,
        }
        if truth[n]["claim_exp"] is not None and truth[n]["claim_exp"] != exp:
            fail.append(f"LAB {n}: readme เขียนว่า {truth[n]['claim_exp']} การทดลอง แต่มีหัวข้อจริง {exp}")
        cf = COUNTS / f"lab{n}.json"
        if cf.exists():
            d = json.loads(cf.read_text(encoding="utf-8"))
            truth[n]["pass"], truth[n]["skip"] = d.get("pass"), d.get("skip")
            if not d.get("all_checks_passed"):
                fail.append(f"LAB {n}: verify.sh ไม่ผ่าน (ledger บอก all_checks_passed=false)")
        else:
            fail.append(f"LAB {n}: ยังไม่มี logs/verify_counts/lab{n}.json — ต้องได้จากการรัน verify.sh จริง")

    exp_total = sum(t["exp"] for t in truth.values())
    times = [t["time"] for t in truth.values() if t["time"]]
    time_total = sum(times) if len(times) == len(truth) else None
    passes = [t["pass"] for t in truth.values() if t["pass"] is not None]
    pass_total = sum(passes) if len(passes) == len(truth) else None

    # ---- root readme ----
    root_md = (ROOT / "readme.md").read_text(encoding="utf-8")
    for n, t in truth.items():
        row = re.search(rf"^\|\s*\*\*{n}\*\*\s*\|\s*(\d+)\s*อัน\s*\|\s*(\d+)\s*นาที", root_md, flags=re.M)
        if not row:
            fail.append(f"root readme: ไม่พบแถวของ LAB {n} ในตารางเส้นทางแล็บ")
            continue
        if int(row.group(1)) != t["exp"]:
            fail.append(f"root readme: LAB {n} เขียน {row.group(1)} การทดลอง ควรเป็น {t['exp']}")
        if t["time"] and int(row.group(2)) != t["time"]:
            fail.append(f"root readme: LAB {n} เขียน {row.group(2)} นาที แต่ไฟล์แล็บเขียน {t['time']}")
    m = re.search(r"การทดลองทั้งหมด\s*(\d+)\s*อัน", root_md)
    if not m:
        fail.append("root readme: ไม่พบบรรทัดยอดรวมการทดลอง")
    elif int(m.group(1)) != exp_total:
        fail.append(f"root readme: ยอดรวมการทดลอง {m.group(1)} ควรเป็น {exp_total}")
    if time_total:
        m = re.search(r"~\s*(\d+)\s*ชั่วโมง\s*(\d+)\s*นาที", root_md)
        if m and int(m.group(1)) * 60 + int(m.group(2)) != time_total:
            fail.append(f"root readme: เวลารวม {m.group(1)}:{m.group(2)} ควรเป็น {time_total//60}:{time_total%60:02d}")
    for n, t in truth.items():
        if t["pass"] is None:
            continue
        row = re.search(rf"^\|\s*{n}\s*\|\s*(\d+)\s*(?:`?\[PASS\]`?)?", root_md, flags=re.M)
        if row and int(row.group(1)) != t["pass"]:
            fail.append(f"root readme: ตาราง [PASS] ของ LAB {n} เขียน {row.group(1)} ควรเป็น {t['pass']}")

    # ---- deck ----
    deck = strip_deck(DECK.read_text(encoding="utf-8"))
    deck = re.sub(r"\s+", " ", deck)
    valid_exp = {exp_total} | {t["exp"] for t in truth.values()}
    for m in re.finditer(r"(\d+)\s*การทดลอง(?!ที่)|การทดลอง(?:ทั้งหมด)?\s*(\d+)\s*อัน", deck):
        got = int(m.group(1) or m.group(2))
        if got not in valid_exp:
            ctx = deck[max(0, m.start() - 40):m.end() + 40].strip()
            fail.append(f"เด็ค: พบตัวเลขการทดลอง {got} ที่ไม่ตรงกับความจริง (รวม {exp_total}) — \"{ctx}\"")
    if "แล็บละ 9 อัน" in deck:
        fail.append("เด็ค: ยังมีข้อความ 'แล็บละ 9 อัน' ซึ่งไม่จริง (" +
                    " · ".join(str(truth[n]["exp"]) for n in sorted(truth)) + ")")
    if pass_total:
        for m in re.finditer(r"(\d+)\s*บรรทัด\s*\[PASS\]", deck):
            if int(m.group(1)) != pass_total:
                fail.append(f"เด็ค: `[PASS]` รวมเขียน {m.group(1)} ควรเป็น {pass_total}")
    if time_total:
        for m in re.finditer(r"~?\s*(\d+)\s*ชั่วโมง\s*(\d+)\s*นาที", deck):
            if int(m.group(1)) * 60 + int(m.group(2)) != time_total:
                fail.append(f"เด็ค: เวลารวม {m.group(1)}:{m.group(2)} ควรเป็น {time_total//60}:{time_total%60:02d}")
        hh = f"{time_total//60}:{time_total%60:02d}"
        for m in re.finditer(r"\b([2-6]):(\d{2})\b\s*(?=ชั่วโมง|·|$)", deck):
            if m.group(0).strip() != hh:
                ctx = deck[max(0, m.start() - 40):m.end() + 50].strip()
                fail.append(f"เด็ค: พบเวลา {m.group(0).strip()} ควรเป็น {hh} — \"{ctx}\"")

    print("ความจริงที่ใช้ตรวจ:")
    for n in sorted(truth):
        t = truth[n]
        print(f"  LAB {n}: การทดลอง {t['exp']} · เวลา {t['time']} นาที · [PASS] {t['pass']} · [SKIP] {t['skip']}")
    print(f"  รวม: การทดลอง {exp_total} · เวลา {time_total} นาที · [PASS] {pass_total}")
    if fail:
        print(f"\n[FAIL] {len(fail)} รายการ")
        for f in fail:
            print(f"  {f}")
        return 1
    print("\n[PASS] ตัวเลขตรงกันทุกไฟล์")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
