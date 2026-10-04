#!/usr/bin/env python3
"""seed_modules.py — สร้าง Roadmap ของ CampusEats เป็น Modules ใน PLAB จาก roadmap.csv แบบ idempotent

- module ที่ "ชื่อซ้ำกับที่มีอยู่แล้ว" จะไม่ถูกสร้างซ้ำ (Plane บังคับ unique (name, project) อยู่แล้ว เราเช็กก่อนยิงเพื่อไม่ให้เจอ 400)
- วันที่ในไฟล์เป็น offset (จำนวนวันจากวันนี้) → Timeline ของทุกคนจะมีแท่งอยู่รอบ ๆ วันนี้เสมอ ไม่ว่าจะรันวันไหน
- lead ระบุเป็นอีเมล → แปลงเป็น UUID ผ่าน GET workspaces/<ws>/members/
- ผูก work item เข้า module ด้วย "คำสำคัญ" (คอลัมน์ keywords คั่นด้วย |) ที่ปรากฏในชื่อใบงาน
  โดยดูก่อนว่าใบไหนอยู่ใน module แล้ว (GET module-issues) → ยิง POST เฉพาะใบใหม่ → รันซ้ำได้ linked 0
ใช้: python seed_modules.py [--project PLAB] [--csv roadmap.csv]
"""
import argparse
import csv
from datetime import date, timedelta

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
ap.add_argument("--csv", default="roadmap.csv")
a = ap.parse_args()

p = Plane()
proj = p.project(a.project)
pid = proj["id"]
if not proj.get("module_view"):
    raise SystemExit("โปรเจกต์ยังไม่เปิด Modules — เปิดที่ Settings › Projects › Plane Lab › Features ก่อน")

members = {m["email"]: m["id"] for m in p.paginate("members/")}
modules = {m["name"]: m for m in p.paginate(f"projects/{pid}/modules/")}
items = p.work_items(pid)          # ใบงานทั้งหมดของโปรเจกต์ (เดินทุกหน้าให้แล้ว)
today = date.today()

created = existing = linked = 0
with open(a.csv, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        name = row["name"]
        if name in modules:
            existing += 1
            mod = modules[name]
            print(f"  exists   {name:<14} status={mod['status']}")
        else:
            body = {
                "name": name,
                "description": row["description"],
                "status": row["status"],
                "start_date": (today + timedelta(days=int(row["start_offset"]))).isoformat(),
                "target_date": (today + timedelta(days=int(row["end_offset"]))).isoformat(),
            }
            if row["lead"] in members:
                body["lead"] = members[row["lead"]]
                body["members"] = [members[row["lead"]]]
            r = p.post(f"projects/{pid}/modules/", body)
            if r.status_code != 201:
                print(f"  ERROR    {name} → {r.status_code} {r.text[:120]}")
                continue
            mod = r.json()
            modules[name] = mod
            created += 1
            print(f"  created  {name:<14} {body['start_date']} → {body['target_date']}  status={body['status']}  lead={row['lead']}")

        # ---- ผูกใบงานตามคำสำคัญ ----
        keys = [k.strip().lower() for k in row["keywords"].split("|") if k.strip()]
        # GET module-issues ตอบเป็น work item เต็ม ๆ (id = issue id) ไม่ใช่แถว ModuleIssue
        already = {mi["id"] for mi in p.paginate(f"projects/{pid}/modules/{mod['id']}/module-issues/")}
        wanted = [it["id"] for it in items if any(k in it["name"].lower() for k in keys)]
        new = [i for i in wanted if i not in already]
        if new:
            r = p.post(f"projects/{pid}/modules/{mod['id']}/module-issues/", {"issues": new})
            if r.status_code == 200:
                linked += len(new)
                seqs = sorted(it["sequence_id"] for it in items if it["id"] in new)
                print(f"           + linked {len(new)} work items: " + ", ".join(f"{a.project}-{s}" for s in seqs))
            else:
                print(f"           link ERROR → {r.status_code} {r.text[:120]}")
        else:
            print(f"           linked 0 (มีอยู่แล้ว {len(already)} ใบ)")

print(f"created {created} / existing {existing} / linked {linked} / API calls {p.calls}")
