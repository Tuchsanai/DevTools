#!/usr/bin/env python3
"""make_cycle.py — สร้างหรือแก้ Cycle (= Sprint) ผ่าน API ด้วยวันที่แบบสัมพัทธ์กับวันนี้

ตัวอย่าง:
  python make_cycle.py --name "Sprint 1" --start -4 --end +9 --description "Sprint Goal: ..."   # เริ่มเมื่อ 4 วันก่อน จบอีก 9 วัน
  python make_cycle.py --name "Sprint 2" --start +1 --end +14
  python make_cycle.py --name "Sprint 1" --end -1        # ย้ายวันจบไปเมื่อวาน → cycle กลายเป็น Completed

ทำไมต้องใช้ API: date picker ในหน้า Create cycle ของ UI ปิดวันที่ผ่านมาแล้ว (past days disabled) จึงสร้าง sprint
ที่ "เริ่มไปแล้วเมื่อ 4 วันก่อน" ไม่ได้ — แต่ API รับวันที่ใดก็ได้ ตราบใดที่ start ≤ end และ cycle ยังไม่ Completed
Plane เก็บ start_date เป็น 00:00:01 และ end_date เป็น 23:59:00 ตาม timezone ของโปรเจกต์ แล้วแปลงเป็น UTC
"""
import argparse
import datetime as dt
import json

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
ap.add_argument("--name", required=True)
ap.add_argument("--start", type=int, help="จำนวนวันจากวันนี้ (ลบ = อดีต)")
ap.add_argument("--end", type=int, help="จำนวนวันจากวันนี้")
ap.add_argument("--description", default=None)
a = ap.parse_args()

today = dt.date.today()
rel = lambda n: (today + dt.timedelta(days=n)).isoformat()

p = Plane()
pid = p.project(a.project)["id"]
body = {}
if a.start is not None:
    body["start_date"] = rel(a.start)
if a.end is not None:
    body["end_date"] = rel(a.end)
if a.description is not None:
    body["description"] = a.description

cyc = p.cycle_by_name(pid, a.name)
if cyc:
    # PATCH: ถ้าส่งแค่ end_date ต้องแนบ start_date เดิมไปด้วย เพราะ validator ต้องเห็นทั้งคู่จึงจะแปลง timezone
    if "end_date" in body and "start_date" not in body:
        body["start_date"] = cyc["start_date"][:10]
    if "start_date" in body and "end_date" not in body:
        body["end_date"] = cyc["end_date"][:10]
    r = p.patch(f"projects/{pid}/cycles/{cyc['id']}/", body)
    verb = "updated"
else:
    if a.start is None or a.end is None:
        raise SystemExit("สร้างใหม่ต้องระบุทั้ง --start และ --end")
    body["name"] = a.name
    r = p.post(f"projects/{pid}/cycles/", body)
    verb = "created"

if r.status_code not in (200, 201):
    raise SystemExit(f"{verb} FAILED {r.status_code}: {r.text[:300]}")
c = r.json()
status = "Completed" if c["end_date"] < dt.datetime.now(dt.timezone.utc).isoformat() else (
    "Yet to start" if c["start_date"][:10] > today.isoformat() else "In progress")
print(f"{verb} cycle '{c['name']}' id={c['id']}")
print(f"  start_date={c['start_date']}  end_date={c['end_date']}  → status now: {status}")
print(f"  sent: {json.dumps(body, ensure_ascii=False)}")
