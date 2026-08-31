#!/usr/bin/env python3
"""flow_metrics.py — วัด flow ของบอร์ด Kanban จาก activity log ของ Plane (สิ่งที่ Analytics ใน CE ไม่มีให้)

  lead time   = completed_at − created_at                  (ลูกค้ารับรู้: ตั้งแต่ขอจนได้)
  cycle time  = completed_at − เวลาที่เข้า state กลุ่ม started ครั้งแรก (ทีมควบคุมได้: ตั้งแต่ลงมือจนเสร็จ)
  throughput  = จำนวนใบที่ Done ในช่วง N วัน · WIP = ใบที่อยู่ในกลุ่ม started ตอนนี้
  Little's Law: WIP ≈ throughput/วัน × cycle time เฉลี่ย (วัน)

ใช้: python flow_metrics.py [--days 7] [--project PLAB]   → ตาราง + p50/p85 + flow_metrics.csv + ASCII CFD
request ที่ใช้: projects 1 + states 1 + work items 1 + activities 1 ต่อใบงาน (พิมพ์ยอดใช้/คงเหลือท้ายรายงาน)
"""
import argparse
import csv
import datetime as dt
import statistics
from collections import Counter

from planeapi import Plane

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
ap.add_argument("--days", type=int, default=7)
ap.add_argument("--csv", default="flow_metrics.csv")
a = ap.parse_args()

P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
now = dt.datetime.now(dt.timezone.utc)
since = now - dt.timedelta(days=a.days)
pct = lambda xs, q: (sorted(xs)[max(0, int(round(q * (len(xs) - 1))))] if xs else 0)

p = Plane()
pid = p.project(a.project)["id"]
states = p.states(pid)
group_of = {v["id"]: v["group"] for v in states.values()}
name_group = {k: v["group"] for k, v in states.items()}
items = p.work_items(pid, per_page=100)

rows, remaining = [], "?"
for it in items:
    r = p.get(f"projects/{pid}/work-items/{it['id']}/activities/", per_page=100)
    remaining = r.headers.get("X-RateLimit-Remaining", remaining)
    acts = [x for x in r.json().get("results", []) if x.get("field") == "state"]
    acts.sort(key=lambda x: x["created_at"])
    it["_acts"] = acts
    started = next((P(x["created_at"]) for x in acts if name_group.get(x["new_value"]) == "started"), None)
    it["_started"] = started
    if it.get("completed_at") and P(it["completed_at"]) >= since:
        done = P(it["completed_at"]); created = P(it["created_at"])
        rows.append({"item": f"{a.project}-{it['sequence_id']}", "name": it["name"][:40],
                     "created": created.strftime("%m-%d %H:%M"), "started": started.strftime("%m-%d %H:%M") if started else "-",
                     "done": done.strftime("%m-%d %H:%M"), "lead_h": round((done - created).total_seconds() / 3600, 1),
                     "cycle_h": round((done - started).total_seconds() / 3600, 1) if started else None})

rows.sort(key=lambda r: r["done"])
print(f"\nงานที่ Done ใน {a.days} วันที่ผ่านมา ({a.project}) — {len(rows)} ใบ")
print(f"{'item':<9}{'created':<13}{'started':<13}{'done':<13}{'lead(h)':>8}{'cycle(h)':>9}  name")
for r in rows:
    print(f"{r['item']:<9}{r['created']:<13}{r['started']:<13}{r['done']:<13}{r['lead_h']:>8}{str(r['cycle_h'] or '-'):>9}  {r['name']}")
with open(a.csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["item"]); w.writeheader(); w.writerows(rows)

leads = [r["lead_h"] for r in rows]; cycles = [r["cycle_h"] for r in rows if r["cycle_h"] is not None]
wip_now = [it for it in items if group_of.get(it["state"]) == "started"]
thr_day = len(rows) / a.days
avg_cycle_d = (statistics.mean(cycles) / 24) if cycles else 0
print(f"\nlead time   p50 = {pct(leads, .5):.1f} h   p85 = {pct(leads, .85):.1f} h   (avg {statistics.mean(leads) if leads else 0:.1f} h)")
print(f"cycle time  p50 = {pct(cycles, .5):.1f} h   p85 = {pct(cycles, .85):.1f} h   (avg {statistics.mean(cycles) if cycles else 0:.1f} h)")
print(f"throughput  {len(rows)} ใบ / {a.days} วัน = {thr_day:.2f} ใบ/วัน")
print(f"WIP ตอนนี้  {len(wip_now)} ใบ ({', '.join(a.project + '-' + str(i['sequence_id']) for i in wip_now)})")
print(f"Little's Law: throughput × cycle = {thr_day:.2f} ใบ/วัน × {avg_cycle_d:.2f} วัน = {thr_day * avg_cycle_d:.2f} ใบ  เทียบ WIP จริง {len(wip_now)} ใบ"
      f"  → {'ใกล้เคียง (ระบบค่อนข้างนิ่ง)' if abs(thr_day * avg_cycle_d - len(wip_now)) <= max(1, 0.5 * len(wip_now)) else 'ต่างกันมาก — WIP โตกว่าที่ throughput รับไหว หรือช่วงเวลาสั้นเกิน'}")
print(f"บอกนัย: ถ้าคง WIP {len(wip_now)} ใบ งานใบใหม่จะรอเฉลี่ย ≈ WIP ÷ throughput = {len(wip_now) / thr_day if thr_day else 0:.1f} วัน")

# ---- ASCII CFD: นับใบงานตามกลุ่ม ณ สิ้นวัน ย้อนหลัง N วัน จาก activity log ----
def group_at(it, t):
    if P(it["created_at"]) > t:
        return None
    g = None
    acts = it["_acts"]
    if acts:
        g = name_group.get(acts[0]["old_value"], "backlog")
        for x in acts:
            if P(x["created_at"]) <= t:
                g = name_group.get(x["new_value"], g)
    else:
        g = group_of.get(it["state"])
    return g
order = ["completed", "started", "unstarted", "backlog"]; glyph = {"completed": "█", "started": "▓", "unstarted": "▒", "backlog": "░"}
print(f"\nCumulative Flow (สิ้นวัน, {a.days} วันล่าสุด)   █ Done  ▓ Started(WIP)  ▒ Ready/Todo  ░ Backlog")
for d in range(a.days, -1, -1):
    t = (now - dt.timedelta(days=d)).replace(hour=23, minute=59, second=59)
    c = Counter(g for g in (group_at(it, t) for it in items) if g)
    bar = "".join(glyph[g] * c.get(g, 0) for g in order)
    print(f"{t:%b %d} | {bar:<24} done={c.get('completed', 0):<2} wip={c.get('started', 0):<2} ready={c.get('unstarted', 0):<2} backlog={c.get('backlog', 0)}")
print(f"\nrequests used: {p.calls} · X-RateLimit-Remaining: {remaining} · เขียน {a.csv} แล้ว")
