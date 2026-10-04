#!/usr/bin/env python3
"""verify_import.py — ตรวจผลการนำเข้า TRL / JRA ผ่าน API v1 แล้วเทียบกับตัวเลขที่ fixtures บอกไว้

ทุกตัวเลข "expected" คำนวณจากไฟล์ fixtures (ไม่ hard-code) → ถ้าแก้ fixtures ตัวตรวจก็ปรับตาม
"""
import csv
import json
import sys
from datetime import date

from planeapi import Plane, C

api = Plane()
B = json.load(open("trello_board.json", encoding="utf-8"))
MT = json.load(open("mapping_trello.json", encoding="utf-8"))
MJ = json.load(open("mapping_jira.json", encoding="utf-8"))
rows = list(csv.DictReader(open("jira_export.csv", encoding="utf-8-sig")))
sprints = list(csv.DictReader(open("jira_sprints.csv", encoding="utf-8-sig")))
TODAY = date.today().isoformat()
fails = 0


def check(label, got, exp):
    global fails
    good = got == exp
    fails += 0 if good else 1
    mark = f"{C.G}PASS{C.X}" if good else f"{C.R}FAIL{C.X}"
    print(f"  {mark}  {label:<46} got={got!r:<28} expected={exp!r}")


def project_report(ident):
    p = api.project(ident, required=False)
    if not p:
        print(f"{C.R}ไม่พบโปรเจกต์ {ident}{C.X}")
        sys.exit(1)
    pid = p["id"]
    items = list(api.work_items(pid, expand="state"))
    states = list(api.states(pid).values())
    labels = list(api.labels(pid).values())
    return p, pid, items, states, labels


# ---------------- TRL ----------------
print(f"{C.W}== TRL (Trello){C.X}")
p, pid, items, states, labels = project_report("TRL")
cards = [c for c in B["cards"] if not c["closed"]]
n_check = sum(len(cl["checkItems"]) for cl in B["checklists"])
check("work items ทั้งหมด", len(items), len(cards) + n_check)
check("external_source = trello ทุกตัว", sum(1 for i in items if i["external_source"] == "trello"), len(items))
check("sub-work items (parent ไม่ว่าง)", sum(1 for i in items if i["parent"]), n_check)
check("states (ไม่รวม triage)", sorted(s["name"] for s in states if not s["is_triage"]),
      sorted(v["name"] for v in MT["lists_to_states"].values()))
check("labels", sorted(l["name"] for l in labels), sorted(l["name"] for l in B["labels"]))
by_state = {}
for i in items:
    if not i["parent"]:
        by_state[i["state"]["name"]] = by_state.get(i["state"]["name"], 0) + 1
lists = {l["id"]: l["name"] for l in B["lists"]}
exp_state = {}
for c in cards:
    n = MT["lists_to_states"][lists[c["idList"]]]["name"]
    exp_state[n] = exp_state.get(n, 0) + 1
check("cards ต่อ column (state)", by_state, exp_state)
check("priority urgent (label urgent)", sum(1 for i in items if i["priority"] == "urgent"),
      sum(1 for c in cards if any(l["name"] == "urgent" for l in c["labels"])))

# ---------------- JRA ----------------
print(f"\n{C.W}== JRA (Jira){C.X}")
p, pid, items, states, labels = project_report("JRA")
epics = [r for r in rows if r["Issue Type"] == "Epic"]
issues = [r for r in rows if r["Issue Type"] != "Epic"]
modules = list(api.paginate(f"projects/{pid}/modules/"))
cycles = list(api.paginate(f"projects/{pid}/cycles/"))
check("work items ทั้งหมด", len(items), len(issues))
check("external_source = jira ทุกตัว", sum(1 for i in items if i["external_source"] == "jira"), len(items))
check("มี estimate_point (Story Points)", sum(1 for i in items if i["estimate_point"]),
      sum(1 for r in issues if r["Story Points"]))
check("modules (จาก Epic)", sorted(m["name"] for m in modules), sorted(e["Summary"] for e in epics))
check("cycles (จาก Sprint)", sorted(c["name"] for c in cycles), sorted(s["Sprint"] for s in sprints))
cyc_status = {c["name"]: ("completed" if c["end_date"][:10] < TODAY else "current" if c["start_date"][:10] <= TODAY else "upcoming")
              for c in cycles}
exp_status = {s["Sprint"]: ("completed" if s["End date"] < TODAY else "current" if s["Start date"] <= TODAY else "upcoming")
              for s in sprints}
check("สถานะ cycle ตามวันที่", cyc_status, exp_status)
check("work items ใน cycle", {c["name"]: c["total_issues"] for c in cycles},
      {s["Sprint"]: sum(1 for r in issues if r["Sprint"] == s["Sprint"]) for s in sprints})
check("work items ที่ Done ใน Sprint ที่ปิด", {c["name"]: c["completed_issues"] for c in cycles if cyc_status[c["name"]] == "completed"},
      {s["Sprint"]: sum(1 for r in issues if r["Sprint"] == s["Sprint"] and r["Status"] == "Done") for s in sprints if s["State"] == "closed"})
check("label type:* (Issue Type)", sorted(l["name"] for l in labels if l["name"].startswith("type:")),
      sorted({"type:" + r["Issue Type"].lower() for r in issues}))
check("created_at ถูก override (< วันนี้)", sum(1 for i in items if i["created_at"][:10] < TODAY), len(issues))
check("มี assignee", sum(1 for i in items if i["assignees"]),
      sum(1 for r in issues if r["Assignee"] in MJ["assignees"]))

# ---------------- ตัวอย่าง payload ----------------
first = next(i for i in items if i["sequence_id"] == 1)
print(f"\n{C.W}== ตัวอย่าง JRA-1 (?expand=state){C.X}: name={first['name'][:30]!r} state={first['state']['name']} "
      f"priority={first['priority']} estimate_point={str(first['estimate_point'])[:8]}… created_at={first['created_at'][:16]} "
      f"external={first['external_source']}/{first['external_id']}")

print(f"\n{api.stats()}")
if fails:
    print(f"{C.R}FAIL: {fails} ข้อไม่ตรง{C.X}")
    sys.exit(1)
print(f"{C.G}PASS: การนำเข้า TRL และ JRA ตรงกับ fixtures ทุกข้อ{C.X}")
