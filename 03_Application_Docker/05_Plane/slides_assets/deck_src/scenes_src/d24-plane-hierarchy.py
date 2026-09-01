#!/usr/bin/env python3
"""d24 — Plane object hierarchy as a tree: Instance → Workspace → Project → (Work item · features) → children.
Note: box labels render at the canvas default (20 px hand font) whatever fs is passed, so box text stays short and
details go into grey helvetica txt elements.
Project-level things are split into two dashed zones because only the first row is a toggle in Settings → Features
(project.cycle_view / module_view / issue_views_view / page_view / intake_view in Plane v1.4.2); States, Labels and
Members are always on, and Estimates is enabled from its own Settings → Estimates page."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d24-plane-hierarchy"


def stub(x, y, dy, target, color=MUTED):
    """Short vertical arrow from a bus line down into a box (end-bound)."""
    return {"type": "arrow", "x": x, "y": y, "width": 0, "height": dy, "points": [[0, 0], [0, dy]],
            "endElementId": target, "strokeColor": color, "strokeWidth": 2, "roughness": 0}


SPINE_CX = 420                      # centre x of the Instance / Workspace / Project spine
NOTE_X = 612

els = [
    title("ลำดับชั้นของ Plane : Instance → Workspace → Project → Work item"),
    # ---- spine
    box("ins", SPINE_CX - 130, 66, 260, 42, "Instance (god-mode)", RED, REDBG, 15),
    box("ws", SPINE_CX - 180, 130, 360, 58, "Workspace (devtools-lab)\nroles Admin · Member · Guest", ORANGE, ORANGEBG, 13),
    box("pr", SPINE_CX - 140, 210, 280, 42, "Project (identifier PLAB)", GREEN, GREENBG, 15),
    arrow("ins", "ws", MUTED, x=SPINE_CX, y=108, w=0, h=22),
    arrow("ws", "pr", MUTED, x=SPINE_CX, y=188, w=0, h=22),
    txt(SPINE_CX + 8, 110, "1 : N", 12, MUTED),
    txt(SPINE_CX + 8, 190, "1 : N", 12, MUTED),
    # ---- notes on the right of the spine
    txt(NOTE_X, 78, "ทั้งเซิร์ฟเวอร์ 1 ตัว · instance admin ตั้งค่าที่ /god-mode/", 13, MUTED),
    txt(NOTE_X, 142, "องค์กร/ทีม · เชิญ members และกำหนด role ที่ระดับนี้\nAdmin = ตั้งค่า/เชิญคน · Member = ทำงาน · Guest = ดู+comment", 13, MUTED),
    txt(NOTE_X, 222, "ผลิตภัณฑ์/ทีมย่อย · เปิด-ปิด features ได้รายโปรเจกต์ (Settings → Features)", 13, MUTED),
]

# ---- level 3 : Project → Work item  +  two zones of project-level things
#   zone A (teal)  : features that are toggles in Settings → Features
#   zone B (grey)  : project settings that are always on (Estimates is enabled on its own settings page)
FW, FGAP, FH = 160, 10, 40
ZONE_H = 82                          # caption + row of boxes + synonym line
ZGAP = 8
WI_X, WI_W, L3_Y = 40, 250, 292
L3_H = ZONE_H * 2 + ZGAP             # Work item box spans both zones
WI_CX = WI_X + WI_W / 2
FZ_X, FZ_W = 315, 860
FZ_CX = FZ_X + FZ_W / 2
BUS1_Y = 276
ZA_Y = L3_Y
ZB_Y = L3_Y + ZONE_H + ZGAP
els += [
    line(SPINE_CX, 252, [[0, 0], [0, BUS1_Y - 252]], MUTED, 2),
    line(WI_CX, BUS1_Y, [[0, 0], [FZ_CX - WI_CX, 0]], MUTED, 2),
    box("wi", WI_X, L3_Y, WI_W, L3_H,
        "Work item  PLAB-12\ntitle · description\nstate · priority\nassignee · estimate\nstart / target date", BLUE, BLUEBG, 13),
    stub(WI_CX, BUS1_Y, L3_Y - BUS1_Y, "wi", BLUE),
    zone(FZ_X, ZA_Y, FZ_W, ZONE_H, TEAL, TEALBG, id="fz"),
    stub(FZ_CX, BUS1_Y, ZA_Y - BUS1_Y, "fz", TEAL),
    txt(FZ_X + 15, ZA_Y + 5, "features ระดับโปรเจกต์ — เปิด/ปิดได้ทีละอย่างใน Settings → Features", 12, TEAL),
    zone(FZ_X, ZB_Y, FZ_W, ZONE_H, MUTED, GREYBG, id="sz"),
    txt(FZ_X + 15, ZB_Y + 5, "ตั้งค่าระดับโปรเจกต์ — ใช้ได้เสมอ ปิดไม่ได้ (Estimates เปิดใช้ที่หน้า Settings → Estimates)", 12, MUTED),
]
row1 = ["Cycles", "Modules", "Views", "Pages", "Intake"]
row2 = ["States", "Labels", "Estimates", "Members"]
syn = {"Cycles": "= Sprint (Scrum)", "Modules": "= Epic (Jira)", "Estimates": "= Story points", "States": "= board columns"}
for r, (zy, names, stroke) in enumerate(((ZA_Y, row1, TEAL), (ZB_Y, row2, MUTED))):
    y = zy + 22
    for i, name in enumerate(names):
        x = FZ_X + 15 + i * (FW + FGAP)
        els.append(box(f"f{r}{i}", x, y, FW, FH, name, stroke, "#ffffff", 12))
        if name in syn:
            els.append(txt(x + 4, y + FH + 3, syn[name], 12, MUTED))

# ---- level 4 : Work item → 5 children (bus + stubs)
children = [
    ("Sub-work items", "งานย่อย · parent / child"),
    ("Relations", "blocked by · duplicate · relates"),
    ("Comments", "คุยงานในใบ · @mention"),
    ("Attachments", "ไฟล์ · ลิงก์ PR / เอกสาร"),
    ("Activity log", "ใครแก้อะไร เมื่อไร (อัตโนมัติ)"),
]
L3_BOTTOM = L3_Y + L3_H
BUS2_Y = L3_BOTTOM + 28
CX0, CW, CGAP, CY, CH = 40, 200, 20, BUS2_Y + 20, 44
child_cx = [CX0 + i * (CW + CGAP) + CW / 2 for i in range(len(children))]
els += [
    line(WI_CX, L3_BOTTOM, [[0, 0], [0, BUS2_Y - L3_BOTTOM]], BLUE, 2),
    line(child_cx[0], BUS2_Y, [[0, 0], [child_cx[-1] - child_cx[0], 0]], BLUE, 2),
    txt(WI_CX + 10, L3_BOTTOM + 6, "= Issue (Jira) · Card (Trello)", 12, MUTED),
]
for i, (name, note) in enumerate(children):
    x = CX0 + i * (CW + CGAP)
    els.append(box(f"c{i}", x, CY, CW, CH, name, PURPLE, PURPLEBG, 13))
    els.append(stub(child_cx[i], BUS2_Y, CY - BUS2_Y, f"c{i}", BLUE))
    els.append(txt(x + 4, CY + CH + 4, note, 12, MUTED))

# ---- footer : the same hierarchy shows up in URL / API path
FOOT_Y = CY + CH + 30
els += [
    zone(40, FOOT_Y, 1130, 52, MUTED, GREYBG),
    txt(55, FOOT_Y + 7, "ลำดับชั้นเดียวกันโผล่ใน URL :  http://localhost:8080/devtools-lab/browse/PLAB-12/      →  <workspace slug> / <project identifier>-<ลำดับ>\n"
                        "และใน API path :  /api/v1/workspaces/<slug>/projects/<project id>/work-items/<id>/      (X-API-Key · ใช้ใน LAB 4–5)", 13, INK),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
