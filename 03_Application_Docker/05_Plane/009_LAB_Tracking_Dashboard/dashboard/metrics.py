"""metrics.py — สูตรของ dashboard ทั้งหมดเป็น pure function (ไม่แตะ network) เพื่อทดสอบด้วย pytest ก่อนต่อข้อมูลจริง

โครงสร้างข้อมูลที่รับ (เหมือน REST API v1 ของ Plane หลังดึงมาแล้ว):
  items      : list ของ work item dict — id, sequence_id, name, state (uuid), priority, created_at, completed_at, estimate_point (uuid|None), assignees, labels
  states     : dict state_id → {"name", "group"}   (group: backlog|unstarted|started|completed|cancelled)
  points     : dict estimate_point_id → float      (ค่า story points)
  cycles     : list ของ cycle dict — id, name, start_date, end_date, issue_ids (list), status ('completed'|'current'|'upcoming')
  activities : list ของ dict — issue_id, field, old_value, new_value, created_at  (เฉพาะ field='state' ที่ใช้)
  relations  : list ของ dict — issue_id, related_issue_id, relation_type ('blocked_by')
"""
from __future__ import annotations

import datetime as dt
from collections import Counter, defaultdict

ISO = "%Y-%m-%d"


def _ts(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    d = dt.datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def _day(s):
    return dt.date.fromisoformat(s[:10])


def burndown(items, start, end, points=None, today=None):
    """remaining ต่อวัน (สูตรเดียวกับ analytics_plot ของ Plane): total − Σ ที่ completed_at ≤ วันนั้น; วันอนาคต = None
    คืน {"dates": [...], "actual": [...], "ideal": [...], "unit": "items"|"points", "total": total}"""
    start, end = _day(start), _day(end)
    today = today or dt.date.today()
    n = (end - start).days + 1
    dates = [start + dt.timedelta(days=i) for i in range(n)]
    weight = (lambda it: points.get(it.get("estimate_point")) or 0) if points else (lambda it: 1)
    total = sum(weight(it) for it in items)
    actual = []
    for d in dates:
        if d > today:
            actual.append(None)
            continue
        done = sum(weight(it) for it in items if it.get("completed_at") and _ts(it["completed_at"]).date() <= d)
        actual.append(round(total - done, 2))
    ideal = [round(total * (1 - i / (n - 1)), 2) if n > 1 else 0 for i in range(n)]
    return {"dates": [d.isoformat() for d in dates], "actual": actual, "ideal": ideal, "unit": "points" if points else "items", "total": total}


def velocity(cycles, items_by_id, points=None):
    """ต่อ cycle ที่ completed: committed = Σ weight ของงานใน cycle, done = Σ weight ของงานที่ completed_at ≤ end_date"""
    weight = (lambda it: points.get(it.get("estimate_point")) or 0) if points else (lambda it: 1)
    rows = []
    for c in cycles:
        if c.get("status") != "completed":
            continue
        its = [items_by_id[i] for i in c.get("issue_ids", []) if i in items_by_id]
        end = _day(c["end_date"]) if c.get("end_date") else None
        committed = sum(weight(it) for it in its)
        done = sum(weight(it) for it in its if it.get("completed_at") and (end is None or _ts(it["completed_at"]).date() <= end))
        rows.append({"cycle": c["name"], "committed": committed, "done": done, "end_date": c.get("end_date")})
    vals = [r["done"] for r in rows]
    avg = round(sum(vals) / len(vals), 2) if vals else 0
    return {"rows": rows, "average": avg, "unit": "points" if points else "items"}


def cfd(items, states, activities, days=14, today=None):
    """จำนวนงานต่อ state group ณ สิ้นวัน ย้อนหลัง N วัน — สร้างจาก activity field='state' (เล่นย้อนกลับจากสถานะปัจจุบัน)
    คืน {"dates": [...], "series": {group: [...]}} โดยผลรวมทุก group ในวันหนึ่ง = จำนวนงานที่มีอยู่แล้ว ณ วันนั้น"""
    today = today or dt.date.today()
    groups = ["backlog", "unstarted", "started", "completed", "cancelled"]
    name_to_group = {v["name"]: v["group"] for v in states.values()}
    id_to_group = {k: v["group"] for k, v in states.items()}
    # เหตุการณ์เปลี่ยน state ต่อ issue เรียงตามเวลา
    ev = defaultdict(list)
    for a in activities:
        if a.get("field") != "state":
            continue
        g_new = name_to_group.get(a.get("new_value")) or id_to_group.get(a.get("new_value"))
        g_old = name_to_group.get(a.get("old_value")) or id_to_group.get(a.get("old_value"))
        ev[a["issue_id"]].append((_ts(a["created_at"]), g_old, g_new))
    for k in ev:
        ev[k].sort(key=lambda x: x[0])
    dates = [today - dt.timedelta(days=i) for i in range(days - 1, -1, -1)]
    series = {g: [0] * len(dates) for g in groups}
    for it in items:
        created = _ts(it["created_at"]).date()
        current = id_to_group.get(it.get("state"), "backlog")
        for di, d in enumerate(dates):
            if d < created:
                continue
            g = current
            cutoff = dt.datetime.combine(d, dt.time.max, tzinfo=dt.timezone.utc)
            # ย้อนกลับ: ทุก transition ที่เกิดหลังสิ้นวัน d ยังไม่เกิด → state ณ วันนั้นคือ old ของ transition แรกที่อยู่หลัง cutoff
            later = [e for e in ev.get(it["id"], []) if e[0] > cutoff]
            if later:
                g = later[0][1] or "backlog"
            if g in series:
                series[g][di] += 1
    return {"dates": [d.isoformat() for d in dates], "series": series}


def lead_cycle(items, states, activities):
    """lead = completed − created · cycle = completed − first transition into a 'started' state  (ชั่วโมง)"""
    started_names = {v["name"] for v in states.values() if v["group"] == "started"}
    started_ids = {k for k, v in states.items() if v["group"] == "started"}
    first_start = {}
    for a in sorted((a for a in activities if a.get("field") == "state"), key=lambda a: a["created_at"]):
        if (a.get("new_value") in started_names or a.get("new_value") in started_ids) and a["issue_id"] not in first_start:
            first_start[a["issue_id"]] = _ts(a["created_at"])
    rows = []
    for it in items:
        if not it.get("completed_at"):
            continue
        done = _ts(it["completed_at"]); created = _ts(it["created_at"])
        lead_h = round((done - created).total_seconds() / 3600, 1)
        st = first_start.get(it["id"])
        cyc_h = round((done - st).total_seconds() / 3600, 1) if st else None
        rows.append({"key": it.get("sequence_id"), "name": it.get("name"), "lead_h": lead_h, "cycle_h": cyc_h})
    leads = sorted(r["lead_h"] for r in rows)
    cycs = sorted(r["cycle_h"] for r in rows if r["cycle_h"] is not None)
    pct = lambda xs, q: (xs[max(0, int(round(q * (len(xs) - 1))))] if xs else None)
    return {"rows": rows, "lead_p50": pct(leads, .5), "lead_p85": pct(leads, .85), "cycle_p50": pct(cycs, .5), "cycle_p85": pct(cycs, .85),
            "histogram": Counter(int(l // 24) for l in leads)}


def wip(items, states, policy):
    """จำนวนงานต่อ state ที่อยู่ในกลุ่ม started เทียบ limit ใน policy"""
    by_state = Counter(states[it["state"]]["name"] for it in items if it.get("state") in states and states[it["state"]]["group"] == "started")
    rows = []
    for name, limit in policy.items():
        n = by_state.get(name, 0)
        rows.append({"state": name, "wip": n, "limit": limit, "ok": n <= limit})
    for name, n in by_state.items():
        if name not in policy:
            rows.append({"state": name, "wip": n, "limit": None, "ok": True})
    return {"rows": rows, "total_wip": sum(by_state.values()), "violations": [r["state"] for r in rows if not r["ok"]]}


def blockers(items_by_id, relations, states):
    """งานที่ยังไม่เสร็จและถูก block โดยงานที่ยังไม่เสร็จ"""
    out = []
    for r in relations:
        if r.get("relation_type") != "blocked_by":
            continue
        a, b = items_by_id.get(r["issue_id"]), items_by_id.get(r["related_issue_id"])
        if not a or not b:
            continue
        if a.get("completed_at") or b.get("completed_at"):
            continue
        out.append({"blocked": a.get("sequence_id"), "by": b.get("sequence_id"), "by_state": states.get(b.get("state"), {}).get("name")})
    return out


def aging(items, states, activities, now=None):
    """อายุ (วัน) ของงานที่กำลังทำ นับจากที่เข้า started ครั้งแรก (หรือ created ถ้าไม่มี activity)"""
    now = now or dt.datetime.now(dt.timezone.utc)
    started_names = {v["name"] for v in states.values() if v["group"] == "started"}
    first = {}
    for a in sorted((a for a in activities if a.get("field") == "state"), key=lambda a: a["created_at"]):
        if a.get("new_value") in started_names and a["issue_id"] not in first:
            first[a["issue_id"]] = _ts(a["created_at"])
    rows = []
    for it in items:
        if states.get(it.get("state"), {}).get("group") != "started":
            continue
        since = first.get(it["id"]) or _ts(it["created_at"])
        rows.append({"key": it.get("sequence_id"), "name": it.get("name"), "age_d": round((now - since).total_seconds() / 86400, 1), "state": states[it["state"]]["name"]})
    return sorted(rows, key=lambda r: -r["age_d"])
