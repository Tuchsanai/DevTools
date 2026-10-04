#!/usr/bin/env python3
"""import_trello.py — นำเข้า Trello board (ไฟล์ JSON export) เข้า Plane ผ่าน REST API v1 แบบ idempotent

  python import_trello.py --init      สร้างโปรเจกต์ TRL (409 = มีแล้ว) + PATCH เปิด features ที่ต้องใช้
  python import_trello.py --dry-run   อ่าน board แล้วพิมพ์ "แผน" การ map — ไม่เขียนอะไรเข้า Plane
  python import_trello.py --apply     นำเข้าจริง พร้อม progress bar — รันซ้ำได้ ของเดิมถูก skip ด้วย 409

การ map (แก้ที่ mapping_trello.json):
  list           → state          POST /states/  (ชื่อซ้ำ → 409 → ใช้ของเดิม เช่น Done ที่ Plane สร้างให้)
  label          → label          POST /labels/  (409 → ใช้ของเดิม)
  card           → work item      external_source=trello, external_id=<card id>  (ซ้ำ → 409 → skip)
  checklist item → sub-work item  parent = work item ของ card นั้น
"""
import argparse
import html
import json
import sys
import time

from planeapi import Plane, C

ap = argparse.ArgumentParser()
ap.add_argument("--board", default="trello_board.json")
ap.add_argument("--mapping", default="mapping_trello.json")
mode = ap.add_mutually_exclusive_group(required=True)
mode.add_argument("--init", action="store_true")
mode.add_argument("--dry-run", action="store_true")
mode.add_argument("--apply", action="store_true")
a = ap.parse_args()

M = json.load(open(a.mapping, encoding="utf-8"))
B = json.load(open(a.board, encoding="utf-8"))
api = Plane()
P = M["project"]


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


def desc_html(text):
    return "".join(f"<p>{html.escape(line)}</p>" for line in (text or "").split("\n") if line.strip())


# ---------- อ่าน board ให้อยู่ในรูปที่ map ง่าย ----------
lists = {l["id"]: l["name"] for l in B["lists"] if not l["closed"]}
checklists = {}
for cl in B["checklists"]:
    checklists.setdefault(cl["idCard"], []).extend(cl["checkItems"])
cards = sorted((c for c in B["cards"] if not c["closed"]), key=lambda c: c["idShort"])
n_items = sum(len(v) for v in checklists.values())


def card_plan(c):
    labels = [l["name"] for l in c["labels"]]
    # ไล่ตามลำดับใน mapping (urgent ก่อน bug) → card ที่มีทั้ง bug และ urgent ต้องได้ urgent ไม่ใช่ตัวแรกที่เจอ
    prio = next((v for k, v in M["priority_from_labels"].items() if k in labels), "none")
    return {
        "idShort": c["idShort"], "id": c["id"], "name": c["name"], "list": lists[c["idList"]],
        "state": M["lists_to_states"][lists[c["idList"]]]["name"], "labels": labels, "priority": prio,
        "due": (c.get("due") or "")[:10] or None, "desc": c.get("desc", ""), "items": checklists.get(c["id"], []),
    }


plan = [card_plan(c) for c in cards]

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
    info(f"features ก่อน PATCH: cycle_view={proj['cycle_view']} module_view={proj['module_view']} "
         f"issue_views_view={proj['issue_views_view']} page_view={proj['page_view']}")
    r = api.patch(f"projects/{proj['id']}/", P["features"])
    if r.status_code != 200:
        die(r, "PATCH features")
    d = r.json()
    ok(f"PATCH /projects/{{id}}/ {json.dumps(P['features'])} → 200")
    info(f"features หลัง PATCH: cycle_view={d['cycle_view']} module_view={d['module_view']} "
         f"issue_views_view={d['issue_views_view']} page_view={d['page_view']}  (บอร์ด Trello ไม่มี sprint → ไม่เปิด Cycles)")
    print(api.stats())
    sys.exit(0)

# =====================================================================
if a.dry_run:
    print(f"{C.W}== --dry-run: แผนการนำเข้า board \"{B['name']}\" → โปรเจกต์ {P['identifier']}{C.X}  (ไม่เขียนอะไรเข้า Plane)\n")
    print(f"{C.W}lists → states{C.X}")
    for name, s in M["lists_to_states"].items():
        n = sum(1 for c in plan if c["list"] == name)
        print(f"  {name:<8} → {s['name']:<8} group={s['group']:<10} {n:>2} cards")
    print(f"  ลบ state ว่างที่ Plane สร้างให้: {', '.join(M['delete_empty_default_states'])}")
    print(f"\n{C.W}labels{C.X}")
    for l in B["labels"]:
        n = sum(1 for c in plan if l["name"] in c["labels"])
        print(f"  {l['name']:<8} {l['color']:<7} → {M['label_colors'][l['color']]}  {n:>2} cards")
    print(f"\n{C.W}cards → work items{C.X}")
    print(f"  {'#':>2}  {'name':<40} {'list':<7} {'priority':<8} {'due':<10} labels / checklist")
    for c in plan:
        extra = f"{','.join(c['labels'])}" + (f"  +{len(c['items'])} sub-items" if c["items"] else "")
        print(f"  {c['idShort']:>2}  {c['name'][:38]:<40} {c['list']:<7} {c['priority']:<8} {c['due'] or '-':<10} {extra}")
    print(f"\n{C.W}สรุป{C.X}: {len(plan)} cards + {n_items} checklist items = {C.G}{len(plan) + n_items} work items{C.X}"
          f" · external_source=trello · external_id=<Trello id 24 hex>")
    sys.exit(0)

# =====================================================================
t0 = time.time()
proj = api.project(P["identifier"], required=False)
if not proj:
    sys.exit(f"{C.R}ยังไม่มีโปรเจกต์ {P['identifier']} — รัน python import_trello.py --init ก่อน{C.X}")
pid = proj["id"]
base = f"projects/{pid}/"
print(f"{C.W}== --apply: {B['name']} → {P['identifier']} ({pid}){C.X}")

# 1) lists → states
print(f"\n{C.W}1) states{C.X}")
state_id = {}
for list_name, spec in M["lists_to_states"].items():
    r = api.post(base + "states/", spec)
    if r.status_code == 200:                      # Plane ตอบ 200 (ไม่ใช่ 201) เมื่อสร้าง state สำเร็จ
        state_id[spec["name"]] = r.json()["id"]
        ok(f"{list_name:<8} → POST /states/ → 200 created")
    elif r.status_code == 409:                    # ชื่อซ้ำ (เช่น Done) → ใช้ของเดิม
        state_id[spec["name"]] = r.json()["id"]
        warn(f"{list_name:<8} → POST /states/ → 409 already exists → reuse id={r.json()['id'][:8]}…")
    else:
        die(r, f"create state {list_name}")
current = api.states(pid)
for name in M["delete_empty_default_states"]:
    if name not in current:
        info(f"state '{name}' ไม่มีแล้ว (ลบไปในรอบก่อน)")
        continue
    r = api.delete(base + f"states/{current[name]['id']}/")
    if r.status_code == 204:
        ok(f"DELETE state '{name}' (ว่างและไม่ใช่ default) → 204")
    else:
        warn(f"DELETE state '{name}' → {r.status_code} {r.text[:80]} (เก็บไว้)")

# 2) labels
print(f"\n{C.W}2) labels{C.X}")
label_id = {}
for l in B["labels"]:
    r = api.post(base + "labels/", {"name": l["name"], "color": M["label_colors"].get(l["color"], "#64748b")})
    if r.status_code == 201:
        label_id[l["name"]] = r.json()["id"]
        ok(f"{l['name']:<8} → 201 created")
    elif r.status_code == 409:
        label_id[l["name"]] = r.json().get("id") or api.labels(pid)[l["name"]]["id"]
        warn(f"{l['name']:<8} → 409 already exists → reuse")
    else:
        die(r, f"create label {l['name']}")

# 3) cards → work items
print(f"\n{C.W}3) cards → work items{C.X}")
created = skipped = 0
issue_of_card = {}
for i, c in enumerate(plan, 1):
    body = {
        "name": c["name"], "state": state_id[c["state"]],
        "priority": c["priority"], "labels": [label_id[x] for x in c["labels"]],
        "external_source": "trello", "external_id": c["id"],
    }
    if c["desc"].strip():                    # ส่ง description_html ว่าง "" → 400 "Invalid HTML passed" — ต้องไม่ส่ง key เลย
        body["description_html"] = desc_html(c["desc"])
    if c["due"]:
        body["target_date"] = c["due"]
    r = api.post(base + "work-items/", body)
    if r.status_code == 201:
        created += 1
        issue_of_card[c["id"]] = r.json()["id"]
        tag = f"{C.G}created{C.X} {P['identifier']}-{r.json()['sequence_id']}"
    elif r.status_code == 409:
        skipped += 1
        issue_of_card[c["id"]] = r.json()["id"]
        tag = f"{C.Y}skipped{C.X} (409 duplicate external_id)"
    else:
        print()
        die(r, f"create card #{c['idShort']}")
    bar(i, len(plan), f"card #{c['idShort']:<2} {tag}  {c['name'][:24]}")
    time.sleep(0.05)
print()

# 4) checklist items → sub-work items
print(f"\n{C.W}4) checklist items → sub-work items{C.X}")
k = 0
for c in plan:
    for it in sorted(c["items"], key=lambda x: x["pos"]):
        k += 1
        st = M["checklist"]["complete_state" if it["state"] == "complete" else "incomplete_state"]
        r = api.post(base + "work-items/", {
            "name": it["name"], "parent": issue_of_card[c["id"]], "state": state_id[st],
            "external_source": "trello", "external_id": it["id"],
        })
        if r.status_code == 201:
            created += 1
            tag = f"{C.G}created{C.X} {P['identifier']}-{r.json()['sequence_id']}"
        elif r.status_code == 409:
            skipped += 1
            tag = f"{C.Y}skipped{C.X} (409)"
        else:
            print()
            die(r, f"create checklist item {it['name']}")
        bar(k, n_items, f"#{c['idShort']:<2} ↳ {tag}  {it['name'][:22]}")
        time.sleep(0.05)
print()

print(f"\n{C.W}== สรุป{C.X}: created {C.G}{created}{C.X} · skipped {C.Y}{skipped}{C.X} · "
      f"total {created + skipped} work items ({len(plan)} cards + {n_items} checklist items) · {time.time() - t0:.1f}s")
print(api.stats())
