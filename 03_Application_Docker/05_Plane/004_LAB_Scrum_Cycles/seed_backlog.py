#!/usr/bin/env python3
"""seed_backlog.py — ป้อน Product Backlog ของ CampusEats (backlog.csv) เข้าโปรเจกต์ PLAB แบบ idempotent

- ทุกแถวมี external_source="lab" + external_id="PBI-xx" → รันซ้ำกี่ครั้ง Plane ก็ตอบ 409 และเราข้ามให้ (ไม่มีใบซ้ำ)
- ใส่ estimate_point ตามคอลัมน์ points โดยแปลงค่า (เช่น "5") → UUID ของ EstimatePoint ในโปรเจกต์
- label ที่ยังไม่มีจะถูกสร้างให้ (bug/feature/docs/tech-debt สร้างไว้แล้วใน LAB 3)
ใช้: python seed_backlog.py [--project PLAB] [--csv backlog.csv]
     python seed_backlog.py --map      # ไม่สร้างอะไร แค่พิมพ์ตาราง PBI-xx → PLAB-n ของเครื่องนี้ (เลข PLAB-n ต่างกันได้ทุกเครื่อง)
"""
import argparse
import csv

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
ap.add_argument("--csv", default="backlog.csv")
ap.add_argument("--map", action="store_true", help="พิมพ์ตาราง PBI-xx → PLAB-n ที่มีอยู่แล้ว (ไม่สร้างอะไร)")
a = ap.parse_args()

p = Plane()
proj = p.project(a.project)
pid = proj["id"]
by_value, by_id = p.estimate_points(pid)

if a.map:                                   # เลข PLAB-n ขึ้นกับว่าเครื่องนั้นสร้าง work item มาแล้วกี่ใบ → ให้ยึด PBI-xx แล้วดูตารางนี้
    items = [i for i in p.work_items(pid) if i.get("external_source") == "lab"]
    print(f"{'PBI':<7} {'work item':<9} {'pt':>2}  name")
    for it in sorted(items, key=lambda i: i["external_id"]):
        pt = by_id.get(it.get("estimate_point"))
        print(f"{it['external_id']:<7} {a.project}-{it['sequence_id']:<4} {int(pt) if pt else '-':>2}  {it['name']}")
    print(f"{len(items)} PBI / API calls {p.calls}")
    raise SystemExit

states = p.states(pid)
labels = p.labels(pid)
if not by_value:
    print("⚠️  โปรเจกต์ยังไม่มี Estimates แบบ points — work item จะถูกสร้างโดยไม่มี point (เปิดที่ Settings › Projects › Estimates ก่อน)")

created = skipped = 0
with open(a.csv, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        label_ids = []
        for name in filter(None, row["labels"].split("|")):
            if name not in labels:
                r = p.post(f"projects/{pid}/labels/", {"name": name})
                if r.status_code == 201:
                    labels[name] = r.json()
                else:                       # 409 = มีอยู่แล้ว → โหลดใหม่
                    labels = p.labels(pid)
            label_ids.append(labels[name]["id"])
        body = {
            "name": row["name"],
            "description_html": row["description_html"],
            "priority": row["priority"],
            "state": states["Backlog"]["id"],
            "labels": label_ids,
            "external_source": "lab",
            "external_id": row["external_id"],
        }
        if by_value.get(row["points"]):
            body["estimate_point"] = by_value[row["points"]]
        r = p.post(f"projects/{pid}/work-items/", body)
        if r.status_code == 201:
            d = r.json()
            created += 1
            print(f"  created  {a.project}-{d['sequence_id']:<3} {row['external_id']}  {row['points']:>2} pt  {row['name']}")
        elif r.status_code == 409:
            skipped += 1
            print(f"  skipped  {row['external_id']} (409 มีอยู่แล้ว id={r.json().get('id','')[:8]}…)")
        else:
            print(f"  ERROR    {row['external_id']} → {r.status_code} {r.text[:120]}")

print(f"created {created} / skipped {skipped} / API calls {p.calls}")
