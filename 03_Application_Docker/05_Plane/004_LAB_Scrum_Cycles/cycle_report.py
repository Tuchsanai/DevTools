#!/usr/bin/env python3
"""cycle_report.py — คำนวณ burndown ของ cycle เอง ด้วยสูตรเดียวกับ Plane แล้วพิมพ์เป็นตาราง

สูตรของ Plane (apps/api/plane/utils/analytics_plot.py → burndown_plot):
  remaining(day) = total − Σ งานที่ completed_at::date ≤ day        (วันในอนาคต = ยังไม่รู้)
  ideal(i)       = total × (1 − i/(n−1))     i = ลำดับวันใน cycle (0..n−1), n = จำนวนวันทั้งหมด
โหมด Work items นับ 1 ต่อใบ · โหมด Estimates ใช้ผลรวม estimate_point.value (แปลงเป็น float)
ใช้:  python cycle_report.py [--cycle "Sprint 1"]     (ไม่ระบุ = cycle ที่กำลังดำเนินอยู่ ?cycle_view=current)
"""
import argparse
import datetime as dt

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
ap.add_argument("--cycle", default=None)
a = ap.parse_args()

p = Plane()
pid = p.project(a.project)["id"]
if a.cycle:
    cyc = p.cycle_by_name(pid, a.cycle)
    if not cyc:
        raise SystemExit(f"ไม่พบ cycle ชื่อ {a.cycle}")
else:
    current = p.cycles(pid, "current")   # ตอบเป็น list เปล่า ๆ ไม่ใช่ envelope (ดูทดลองเพิ่มเติม ง)
    if not current:
        raise SystemExit("ไม่มี cycle ที่กำลังดำเนินอยู่ — ระบุ --cycle <ชื่อ>")
    cyc = current[0]

# ?expand=estimate_point ทำให้ API แนบ object ของ EstimatePoint (มี value เป็น string) มากับแต่ละใบ
items = list(p.paginate(f"projects/{pid}/cycles/{cyc['id']}/cycle-issues/", expand="estimate_point"))

start = dt.date.fromisoformat(cyc["start_date"][:10])
end = dt.date.fromisoformat(cyc["end_date"][:10])
today = dt.datetime.now(dt.timezone.utc).date()
n = (end - start).days + 1

def points(it):
    ep = it.get("estimate_point")
    return float(ep["value"]) if isinstance(ep, dict) else 0.0

total_items = len(items)
total_pts = sum(points(it) for it in items)
done_days = {}
for it in items:
    if it.get("completed_at"):
        d = dt.datetime.fromisoformat(it["completed_at"].replace("Z", "+00:00")).date()
        done_days.setdefault(d, []).append(it)

print(f"Cycle: {cyc['name']}  {start} → {end}  ({n} วัน)   items={total_items}  points={total_pts:g}")
print(f"{'day':>3}  {'date':10}  {'ideal':>6}  {'done':>5}  {'remain':>6}  {'ideal':>6}  {'remain':>6}   {'':8}")
print(f"{'':3}  {'':10}  {'items':>6}  {'items':>5}  {'items':>6}  {'points':>6}  {'points':>6}")
cum_items = cum_pts = 0.0
for i in range(n):
    day = start + dt.timedelta(days=i)
    ideal_i = total_items * (1 - i / (n - 1)) if n > 1 else 0
    ideal_p = total_pts * (1 - i / (n - 1)) if n > 1 else 0
    for it in done_days.get(day, []):
        cum_items += 1
        cum_pts += points(it)
    if day > today:
        print(f"{i:>3}  {day}  {ideal_i:6.1f}  {'-':>5}  {'-':>6}  {ideal_p:6.1f}  {'-':>6}   (future)")
        continue
    mark = "◀ today" if day == today else ""
    done_names = ",".join(f"{a.project}-{it['sequence_id']}" for it in done_days.get(day, []))
    print(f"{i:>3}  {day}  {ideal_i:6.1f}  {int(cum_items):>5}  {total_items - cum_items:6.0f}  {ideal_p:6.1f}  {total_pts - cum_pts:6.1f}   {mark} {done_names}")
print(f"\nวันนี้เหลือ {total_items - cum_items:.0f} items / {total_pts - cum_pts:g} points  → ต้องตรงกับจุดสุดท้ายของเส้น Current ในแผง Progress")
print(f"API calls: {p.calls}")
