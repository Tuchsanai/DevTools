#!/usr/bin/env python3
"""compare_export_api.py — เทียบ 1 แถวจากไฟล์ JSON export กับ GET /work-items/?expand=state,assignees ของ API v1
ใช้: python compare_export_api.py out-json.zip [--key PLAB-9]
จุดที่อยากให้เห็น: export ให้ "ชื่อ" (state_name, assignees เป็นชื่อคน, estimate เป็นค่า) ส่วน API ให้ "UUID" (ต้อง expand ถึงจะได้ชื่อ)
"""
import argparse
import json
import zipfile

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("zip")
ap.add_argument("--key", default="PLAB-9")
ap.add_argument("--project", default="PLAB")
a = ap.parse_args()

z = zipfile.ZipFile(a.zip)
exp = json.loads(z.read([n for n in z.namelist() if n.endswith(".json")][0]))
p = Plane()
pid = p.project(a.project)["id"]
api = {f"{a.project}-{i['sequence_id']}": i for i in p.work_items(pid, expand="state,assignees")}
print(f"export {len(exp)} rows · API {len(api)} rows")

row = next(r for r in exp if r["identifier"] == a.key)
it = api[a.key]
print(f"\n== {a.key} จาก export (JSON)")
for k in ("state_name", "priority", "assignees", "estimate", "labels", "modules", "cycles", "completed_at"):
    print(f"   {k:13}: {row.get(k)!r}")
print(f"\n== {a.key} จาก API v1 (?expand=state,assignees)")
print(f"   state        : {it['state']['name']!r}  (group={it['state']['group']!r}, id={it['state']['id'][:8]}…)")
print(f"   assignees    : {[u.get('display_name') or u.get('email') for u in it['assignees']]!r}")
print(f"   estimate_point: {it['estimate_point']!r}  ← ยังเป็น UUID (ไม่มี expand สำหรับ estimate)")
print(f"   labels       : {it['labels']!r}  ← UUID เช่นกัน")
print(f"   completed_at : {it['completed_at']!r}")
print(f"\nAPI calls ที่ใช้: {p.calls}")
