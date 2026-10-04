#!/usr/bin/env python3
"""velocity.py — velocity ต่อ sprint จาก cycle ที่จบแล้ว (?cycle_view=completed) + พยากรณ์จำนวน sprint ที่เหลือ

velocity(sprint) = Σ points ของงานที่ Done ใน sprint นั้น (งานทำครึ่งเดียว = 0)
committed        = points ทั้งหมดตอนเริ่ม sprint — หลัง Transfer งานที่ไม่เสร็จจะย้ายออกไปแล้ว จึงอ่านจาก progress_snapshot
                   (Plane แช่แข็งสถิติของ cycle เก่าไว้ตอนกด Transfer) ถ้าไม่มี snapshot ใช้ total_estimates ปัจจุบัน
forecast         = points ที่ยังไม่ Done ทั้งโปรเจกต์ ÷ velocity เฉลี่ย
"""
import argparse

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
a = ap.parse_args()

p = Plane()
pid = p.project(a.project)["id"]
def pts(it):                      # ?expand=estimate_point → estimate_point เป็น object ที่มี value (string)
    ep = it.get("estimate_point")
    return float(ep["value"]) if isinstance(ep, dict) else 0.0

completed = p.cycles(pid, "completed")     # envelope แบบมีหน้า (ต่างจาก current)
print(f"{'cycle':10} {'period':23} {'committed':>9} {'done':>5} {'velocity':>9}  {'snapshot':8}")
vel = []
for c in sorted(completed, key=lambda c: c["start_date"]):
    items = list(p.paginate(f"projects/{pid}/cycles/{c['id']}/cycle-issues/", expand="estimate_point"))
    done_pts = sum(pts(it) for it in items if it.get("completed_at"))
    snap = c.get("progress_snapshot") or {}
    est = (snap.get("estimate_distribution") or {}).get("completion_chart") or {}
    committed = max(est.values()) if est and any(v is not None for v in est.values()) else (c.get("total_estimates") or 0)
    committed = committed or 0
    vel.append(done_pts)
    print(f"{c['name']:10} {c['start_date'][:10]} → {c['end_date'][:10]} {committed:9g} {done_pts:5g} {done_pts:9g}  {'yes' if snap else 'no':8}")

if not vel:
    raise SystemExit("ยังไม่มี cycle ที่ Completed — ปิด Sprint 1 ก่อน (ข้อ 9)")
avg = sum(vel[-3:]) / len(vel[-3:])
remaining = sum(pts(it) for it in p.work_items(pid, expand="estimate_point") if not it.get("completed_at"))
print(f"\nvelocity เฉลี่ย (≤3 sprint ล่าสุด) = {avg:g} points/sprint")
print(f"งานที่ยังไม่ Done ทั้งโปรเจกต์ = {remaining:g} points")
if avg > 0:
    import math
    print(f"forecast: เหลืออีก ≈ {remaining / avg:.1f} sprint → ปัดขึ้น {math.ceil(remaining / avg)} sprint (sprint ละ 2 สัปดาห์ ≈ {2 * math.ceil(remaining / avg)} สัปดาห์)")
print(f"API calls: {p.calls}")
