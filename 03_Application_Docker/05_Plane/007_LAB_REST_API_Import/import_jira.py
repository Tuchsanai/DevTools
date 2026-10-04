#!/usr/bin/env python3
"""import_jira.py — นำเข้า Jira CSV export เข้า Plane ผ่าน REST API v1 แบบ idempotent

  python import_jira.py --init      สร้างโปรเจกต์ JRA + PATCH cycle_view/module_view + ให้แน่ใจว่ามี Estimate (Points/Fibonacci)
  python import_jira.py --dry-run   พิมพ์แผนการ map (ไม่เขียนอะไรเข้า Plane)
  python import_jira.py --apply     นำเข้าจริง — รันซ้ำได้ (409 → skip)

การ map (แก้ที่ mapping_jira.json):
  Epic          → Module        (external_source=jira, external_id=<Issue key>)
  Sprint        → Cycle         (วันที่จาก jira_sprints.csv — sprint ที่ปิดแล้วต้อง "ปิดทีหลัง" ด้วย PATCH end_date)
  Status        → state         Priority → priority          Issue Type → label type:<x>
  Story Points  → estimate_point (UUID ของ EstimatePoint ที่มี value ตรงกัน)
  Assignee      → assignees     (email ใน mapping → workspace member → ต้องเป็น project member ก่อน)
  Created       → created_at    (API v1 ยอมให้ override ตอน POST)
  Parent (Epic) → module-issues
"""
import argparse
import csv
import html
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta

from planeapi import Plane, C

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="jira_export.csv")
ap.add_argument("--sprints", default="jira_sprints.csv")
ap.add_argument("--mapping", default="mapping_jira.json")
mode = ap.add_mutually_exclusive_group(required=True)
mode.add_argument("--init", action="store_true")
mode.add_argument("--dry-run", action="store_true")
mode.add_argument("--apply", action="store_true")
a = ap.parse_args()

M = json.load(open(a.mapping, encoding="utf-8"))
P = M["project"]
# utf-8-sig = ตัด BOM (EF BB BF) ที่ Jira ใส่มาหน้าไฟล์ — ถ้าเปิดด้วย utf-8 ธรรมดา คอลัมน์แรกจะชื่อ '﻿Issue key'
rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
sprints = list(csv.DictReader(open(a.sprints, encoding="utf-8-sig")))
epics = [r for r in rows if r["Issue Type"] == "Epic"]
items = [r for r in rows if r["Issue Type"] != "Epic"]
api = Plane()
TODAY = date.today()
# SQL ใช้เฉพาะจุดที่ API v1 ของ v1.4.2 ยังไม่มี route (estimates) — รันผ่าน pc ของ LAB 1
PSQL = os.environ.get("PLANE_PSQL", "pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -At -v ON_ERROR_STOP=1")


def ok(msg):
    print(f"{C.G}✔{C.X} {msg}")


def info(msg):
    print(f"{C.B}·{C.X} {msg}")


def warn(msg):
    print(f"{C.Y}!{C.X} {msg}")


def die(r, what):
    sys.exit(f"{C.R}✘ {what} → HTTP {r.status_code}: {r.text[:300]}{C.X}")


def bar(i, n, msg):
    w = 26
    f = int(w * i / n)
    sys.stdout.write(f"\r{C.B}[{'█' * f}{'░' * (w - f)}]{C.X} {i:>3}/{n}  {msg:<58}")
    sys.stdout.flush()


def sql(text):
    out = subprocess.run(["bash", "-c", PSQL], input=text, text=True, capture_output=True)
    if out.returncode != 0:
        sys.exit(f"{C.R}SQL ล้มเหลว: {out.stderr.strip()[-300:]}{C.X}")
    return [line.split("|") for line in out.stdout.strip().splitlines() if line]


def created_iso(s):
    return datetime.strptime(s, M["created_format"]).strftime("%Y-%m-%dT%H:%M:%SZ")


def row_plan(r):
    labels = [M["type_label_prefix"] + r["Issue Type"].lower()] + [x.strip() for x in r["Labels"].split() if x.strip()]
    return {
        "key": r["Issue key"], "name": r["Summary"], "type": r["Issue Type"],
        "state": M["status_to_state"][r["Status"]]["name"], "priority": M["priority"][r["Priority"]],
        "assignee": M["assignees"].get(r["Assignee"]) if r["Assignee"] else None, "assignee_raw": r["Assignee"],
        "points": r["Story Points"] or None, "sprint": r["Sprint"] or None, "labels": labels,
        "created": created_iso(r["Created"]), "desc": r["Description"], "parent": r["Parent"] or None,
    }


plan = [row_plan(r) for r in items]

# =====================================================================
if a.init:
    print(f"{C.W}== --init: โปรเจกต์ {P['identifier']} ({P['name']}){C.X}")
    r = api.post("projects/", {"name": P["name"], "identifier": P["identifier"],
                                            "description": P["description"], "network": 2})
    if r.status_code == 201:
        proj = r.json()
        ok(f"POST /projects/ → 201 created  id={proj['id']}")
    elif r.status_code == 409:
        warn(f"POST /projects/ → 409 {r.json()}  → มีอยู่แล้ว ใช้ของเดิม")
        proj = api.project(P["identifier"])
    else:
        die(r, "create project")
    pid = proj["id"]
    info(f"ก่อน PATCH: cycle_view={proj['cycle_view']} module_view={proj['module_view']} estimate={proj.get('estimate')}")
    r = api.patch(f"projects/{pid}/", P["features"])
    if r.status_code != 200:
        die(r, "PATCH features")
    ok(f"PATCH /projects/{{id}}/ {json.dumps(P['features'])} → 200  (Jira มี Sprint/Epic → ต้องเปิด Cycles + Modules)")

    # ---- Estimate: ลองทาง API ก่อน ----
    print(f"\n{C.W}== Estimate {M['estimate']['name']} ({M['estimate']['type']}) {'/'.join(M['estimate']['values'])}{C.X}")
    r = api.get(f"projects/{pid}/estimates/")
    info(f"GET /projects/{{id}}/estimates/ → {r.status_code} {r.text.strip()[:60]}")
    if r.status_code in (200, 404) and "Page not found" not in r.text:
        # Plane รุ่นใหม่กว่า v1.4.2 มี route นี้ (ไฟล์ plane/api/urls/estimate.py) — ใช้ API ตรง ๆ
        if r.status_code == 404:
            r = api.post(f"projects/{pid}/estimates/", {"name": M["estimate"]["name"], "type": M["estimate"]["type"]})
            eid = r.json()["id"]
            api.post(f"projects/{pid}/estimates/{eid}/estimate-points/",
                     [{"key": i, "value": v} for i, v in enumerate(M["estimate"]["values"])])
            ok("สร้าง estimate + points ผ่าน API")
        else:
            eid = r.json()["id"]
    else:
        warn("v1.4.2: ไฟล์ route estimate.py มีใน image แต่ไม่ถูก include ใน plane/api/urls/__init__.py → ใช้ SQL แทน")
        me = api.get("users/me/").json()["id"]
        wsid = proj["workspace"]
        values = ",".join(f"({i},'{v}')" for i, v in enumerate(M["estimate"]["values"]))
        out = sql(f"""
insert into estimates (id,created_at,updated_at,name,description,type,last_used,project_id,workspace_id,created_by_id,updated_by_id)
select gen_random_uuid(),now(),now(),'{M['estimate']['name']}','Fibonacci — สร้างโดย import_jira.py --init','{M['estimate']['type']}',true,'{pid}','{wsid}','{me}','{me}'
where not exists (select 1 from estimates where project_id='{pid}' and deleted_at is null);
insert into estimate_points (id,created_at,updated_at,key,description,value,estimate_id,project_id,workspace_id,created_by_id,updated_by_id)
select gen_random_uuid(),now(),now(),v.key,'',v.value,e.id,'{pid}','{wsid}','{me}','{me}'
from estimates e, (values {values}) as v(key,value)
where e.project_id='{pid}' and e.deleted_at is null
  and not exists (select 1 from estimate_points p where p.estimate_id=e.id and p.value=v.value and p.deleted_at is null);
select e.id, (select count(*) from estimate_points p where p.estimate_id=e.id and p.deleted_at is null)
from estimates e where e.project_id='{pid}' and e.deleted_at is null;""")
        eid, npts = out[-1]
        ok(f"SQL: estimates 1 แถว (id={eid[:8]}…) · estimate_points {npts} แถว (INSERT … WHERE NOT EXISTS = idempotent)")
    r = api.patch(f"projects/{pid}/", {"estimate": eid})
    if r.status_code != 200:
        die(r, "PATCH project.estimate")
    ok(f"PATCH /projects/{{id}}/ {{\"estimate\": …}} → 200  project.estimate={r.json().get('estimate', '')[:8]}… (= เปิดใช้ Estimates ในโปรเจกต์)")
    print(api.stats())
    sys.exit(0)

# =====================================================================
if a.dry_run:
    print(f"{C.W}== --dry-run: {a.csv} ({len(rows)} rows) → โปรเจกต์ {P['identifier']}{C.X}  (ไม่เขียนอะไรเข้า Plane)\n")
    print(f"{C.W}Epics → Modules{C.X}")
    for e in epics:
        n = sum(1 for p in plan if p["parent"] == e["Issue key"])
        print(f"  {e['Issue key']:<6} {e['Summary'][:40]:<42} status={M['epic_module_status'][e['Status']]:<12} {n} work items")
    print(f"\n{C.W}Sprints → Cycles{C.X}")
    for s in sprints:
        n = sum(1 for p in plan if p["sprint"] == s["Sprint"])
        end = date.fromisoformat(s["End date"])
        note = "end_date ผ่านมาแล้ว → สร้างเป็น active ก่อน ใส่ work items แล้วค่อย PATCH end_date ให้ Completed" if end < TODAY else "ครอบวันนี้ → Active cycle"
        print(f"  {s['Sprint']:<9} {s['Start date']} → {s['End date']}  {s['State']:<7} {n} work items  · {note}")
    print(f"\n{C.W}rows → work items{C.X}")
    print(f"  {'key':<7}{'type':<6}{'state':<12}{'prio':<8}{'pts':<4}{'sprint':<9}{'assignee':<20}{'created_at':<21}labels")
    for p in plan:
        print(f"  {p['key']:<7}{p['type']:<6}{p['state']:<12}{p['priority']:<8}{p['points'] or '-':<4}{p['sprint'] or '-':<9}"
              f"{p['assignee'] or '(unassigned)':<20}{p['created']:<21}{','.join(p['labels'])}")
    print(f"\n{C.W}สรุป{C.X}: {len(epics)} Epics → Modules · {len(sprints)} Sprints → Cycles · "
          f"{C.G}{len(plan)} work items{C.X} (external_source=jira, external_id=<Issue key>) · "
          f"Story Points → estimate_point · Created → created_at")
    sys.exit(0)

# =====================================================================
t0 = time.time()
proj = api.project(P["identifier"], required=False)
if not proj:
    sys.exit(f"{C.R}ยังไม่มีโปรเจกต์ {P['identifier']} — รัน python import_jira.py --init ก่อน{C.X}")
pid = proj["id"]
base = f"projects/{pid}/"
print(f"{C.W}== --apply: {a.csv} → {P['identifier']} ({pid}){C.X}")

# 1) states
print(f"\n{C.W}1) states{C.X}")
state_id = {}
for status, spec in M["status_to_state"].items():
    r = api.post(base + "states/", spec)
    if r.status_code == 200:
        state_id[spec["name"]] = r.json()["id"]
        ok(f"{status:<12} → POST /states/ → 200 created '{spec['name']}'")
    elif r.status_code == 409:
        state_id[spec["name"]] = r.json()["id"]
        warn(f"{status:<12} → POST /states/ → 409 already exists → reuse '{spec['name']}'")
    else:
        die(r, f"create state {status}")

# 2) labels
print(f"\n{C.W}2) labels{C.X}")
label_id = {}
for name in sorted({l for p in plan for l in p["labels"]}):
    r = api.post(base + "labels/", {"name": name, "color": M["label_colors"].get(name, "#64748b")})
    if r.status_code == 201:
        label_id[name] = r.json()["id"]
        ok(f"{name:<12} → 201 created")
    elif r.status_code == 409:
        label_id[name] = r.json().get("id") or api.labels(pid)[name]["id"]
        warn(f"{name:<12} → 409 already exists → reuse")
    else:
        die(r, f"create label {name}")

# 3) estimate points (value → UUID)  — v1.4.2 อ่านผ่าน API ไม่ได้ จึงอ่านจาก DB
print(f"\n{C.W}3) estimate points{C.X}")
r = api.get(base + "estimates/")
if r.status_code == 200:
    eid = r.json()["id"]
    point_id = {p["value"]: p["id"] for p in api.get(base + f"estimates/{eid}/estimate-points/").json()}
    info("อ่าน estimate points ผ่าน API")
else:
    point_id = {v: i for v, i in sql(f"select value,id from estimate_points where project_id='{pid}' and deleted_at is null order by key")}
    info(f"GET /estimates/ → {r.status_code} → อ่านจาก SQL แทน")
if not point_id:
    sys.exit(f"{C.R}ไม่พบ estimate points — รัน python import_jira.py --init ก่อน{C.X}")
ok("value → UUID: " + "  ".join(f"{v}={i[:8]}…" for v, i in point_id.items()))

# 4) members (assignee ต้องเป็น project member role ≥ 15 ไม่งั้น API จะ "เงียบ ๆ ตัดทิ้ง")
print(f"\n{C.W}4) members{C.X}")
ws_members = {m.get("email"): m["id"] for m in api.members() if m.get("email")}
user_id = {}
for email in sorted({p["assignee"] for p in plan if p["assignee"]}):
    uid = ws_members.get(email)
    if not uid:
        warn(f"{email:<20} ไม่อยู่ใน workspace → จะไม่ assign")
        continue
    user_id[email] = uid
    r = api.post(base + "members/", {"member": uid, "role": 15})
    if r.status_code == 201:
        ok(f"{email:<20} → POST /members/ role=15 → 201 added")
    else:
        warn(f"{email:<20} → POST /members/ → {r.status_code} {r.text[:60]} (เป็นสมาชิกอยู่แล้ว)")

# 5) Epics → Modules
print(f"\n{C.W}5) Epics → Modules{C.X}")
module_id = {}
for e in epics:
    r = api.post(base + "modules/", {"name": e["Summary"], "description": f"Jira Epic {e['Issue key']}: {e['Description']}",
                                     "status": M["epic_module_status"][e["Status"]],
                                     "external_source": "jira", "external_id": e["Issue key"]})
    if r.status_code == 201:
        module_id[e["Issue key"]] = r.json()["id"]
        ok(f"{e['Issue key']:<6} → POST /modules/ → 201 created '{e['Summary'][:30]}'")
    elif r.status_code == 409:
        module_id[e["Issue key"]] = r.json()["id"]
        warn(f"{e['Issue key']:<6} → POST /modules/ → 409 already exists → reuse")
    else:
        die(r, f"create module {e['Issue key']}")

# 6) Sprints → Cycles
print(f"\n{C.W}6) Sprints → Cycles{C.X}")
cycle_id, close_later, cycle_done = {}, {}, set()
existing = {c["name"]: c for c in api.paginate(base + "cycles/")}
for s in sprints:
    end = date.fromisoformat(s["End date"])
    if s["Sprint"] in existing:
        c = existing[s["Sprint"]]
        cycle_id[s["Sprint"]] = c["id"]
        if c["end_date"] and c["end_date"][:10] < TODAY.isoformat():
            cycle_done.add(s["Sprint"])
        warn(f"{s['Sprint']:<9} มีอยู่แล้ว ({c['start_date'][:10]} → {c['end_date'][:10]}) → reuse"
             + (" · Completed แล้ว (เพิ่ม work items ไม่ได้อีก)" if s["Sprint"] in cycle_done else ""))
        continue
    body = {"name": s["Sprint"], "description": s["Goal"], "start_date": s["Start date"], "end_date": s["End date"],
            "external_source": "jira", "external_id": s["Sprint"]}
    if end < TODAY:
        # cycle ที่ end_date ผ่านไปแล้ว = Completed → POST cycle-issues จะได้ 400 CYCLE_COMPLETED
        # จึงสร้างให้ "ยังไม่จบ" ก่อน แล้วค่อย PATCH end_date หลังใส่ work items
        body["end_date"] = (TODAY + timedelta(days=1)).isoformat()
        close_later[s["Sprint"]] = s["End date"]
    r = api.post(base + "cycles/", body)
    if r.status_code == 201:
        cycle_id[s["Sprint"]] = r.json()["id"]
        ok(f"{s['Sprint']:<9} → POST /cycles/ {body['start_date']} → {body['end_date']} → 201 created"
           + (f"  (ของจริงจบ {s['End date']} — จะ PATCH ทีหลัง)" if s["Sprint"] in close_later else ""))
    else:
        die(r, f"create cycle {s['Sprint']}")

# 7) rows → work items
print(f"\n{C.W}7) rows → work items{C.X}")
created = skipped = 0
to_module, to_cycle = {}, {}
for i, p in enumerate(plan, 1):
    body = {
        "name": p["name"], "state": state_id[p["state"]], "priority": p["priority"], "labels": [label_id[l] for l in p["labels"]],
        "created_at": p["created"], "external_source": "jira", "external_id": p["key"],
    }
    if p["desc"].strip():                    # description_html ว่าง → 400 "Invalid HTML passed" — ส่งเฉพาะเมื่อมีข้อความ
        body["description_html"] = f"<p>{html.escape(p['desc'])}</p>"
    if p["points"]:
        body["estimate_point"] = point_id[p["points"]]
    if p["assignee"] and p["assignee"] in user_id:
        body["assignees"] = [user_id[p["assignee"]]]
    r = api.post(base + "work-items/", body)
    if r.status_code == 201:
        created += 1
        iid = r.json()["id"]
        tag = f"{C.G}created{C.X} {P['identifier']}-{r.json()['sequence_id']}"
        if p["parent"] in module_id:
            to_module.setdefault(p["parent"], []).append(iid)
        if p["sprint"] in cycle_id:
            to_cycle.setdefault(p["sprint"], []).append(iid)
    elif r.status_code == 409:
        skipped += 1
        tag = f"{C.Y}skipped{C.X} (409 duplicate external_id)"
    else:
        print()
        die(r, f"create {p['key']}")
    bar(i, len(plan), f"{p['key']:<7}{tag}  {p['name'][:22]}")
    time.sleep(0.05)
print()

# 8) link → modules / cycles, then close finished sprints
print(f"\n{C.W}8) link module-issues / cycle-issues{C.X}")
for epic, ids in to_module.items():
    r = api.post(base + f"modules/{module_id[epic]}/module-issues/", {"issues": ids})
    ok(f"{epic:<9} ← {len(ids)} work items → POST /module-issues/ → {r.status_code}") if r.status_code == 200 else die(r, "module-issues")
for sp, ids in to_cycle.items():
    if sp in cycle_done:
        warn(f"{sp:<9} Completed แล้ว → ข้าม {len(ids)} work items")
        continue
    r = api.post(base + f"cycles/{cycle_id[sp]}/cycle-issues/", {"issues": ids})
    ok(f"{sp:<9} ← {len(ids)} work items → POST /cycle-issues/ → {r.status_code}") if r.status_code == 200 else die(r, "cycle-issues")
for sp, real_end in close_later.items():
    r = api.patch(base + f"cycles/{cycle_id[sp]}/", {"end_date": real_end})
    ok(f"{sp:<9} PATCH end_date={real_end} → {r.status_code} → cycle กลายเป็น Completed") if r.status_code == 200 else die(r, "close cycle")
if not (to_module or to_cycle or close_later):
    info("ไม่มี work item ใหม่ → ไม่ต้อง link อะไรเพิ่ม")

print(f"\n{C.W}== สรุป{C.X}: created {C.G}{created}{C.X} · skipped {C.Y}{skipped}{C.X} · total {created + skipped} work items · "
      f"{len(module_id)} modules · {len(cycle_id)} cycles · {time.time() - t0:.1f}s")
print(api.stats())
