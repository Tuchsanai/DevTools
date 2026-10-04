#!/usr/bin/env python3
"""d38-theory-plane-lab-map : Theory concept → Plane feature → LAB, five aligned rows in three columns."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

# column geometry (x, width)
TX, TW = 30, 430      # ทฤษฎี
PX, PW = 520, 420     # ฟีเจอร์ของ Plane
LX, LW = 1000, 180    # LAB
Y0, STEP, H = 122, 96, 82

# (id, colour, bg, theory lines, theory caption, plane lines, plane caption, lab label, lab caption)
rows = [
    ("1", BLUE, BLUEBG,
     ["SDLC · Issue tracking · Workflow"], "วงจรชีวิตซอฟต์แวร์ · ใบงานที่ดี · สถานะของงาน",
     ["Work items · States · Activity"], "Project → Work items · Settings → States",
     "LAB 1–3", "Setup · Architecture\nWork items"),
    ("2", ORANGE, ORANGEBG,
     ["Scrum · Sprint · Backlogs", "Story points · Velocity · Burndown"], "กรอบงาน Scrum · การประมาณ · วัดความคืบหน้า",
     ["Cycles · Estimates · Progress panel"], "Project → Cycles · Settings → Estimates",
     "LAB 4", "Scrum Cycles"),
    ("3", TEAL, TEALBG,
     ["Kanban · WIP", "Lead / Cycle time · CFD"], "ระบบดึงงาน · จำกัดงานค้าง · วัด flow",
     ["Board · States · Views · Intake"], "Layout: Board · Views · Intake (triage)",
     "LAB 5", "Kanban Flow"),
    ("4", PURPLE, PURPLEBG,
     ["Epic · Roadmap · Analytics"], "งานก้อนใหญ่ · แผนระยะยาว · ภาพรวมของทีม",
     ["Modules · Pages · Analytics · Exports"], "Project → Modules · Pages · Workspace → Analytics",
     "LAB 6", "Modules · Pages\nAnalytics"),
    ("5", GREEN, GREENBG,
     ["Integration · Automation", "Tracking dashboard"], "เชื่อมระบบอื่น · ทำงานอัตโนมัติ · dashboard ของทีม",
     ["REST API · Webhooks"], "Settings → API tokens · Webhooks",
     "LAB 7–9", "REST API · Webhooks\nDashboard"),
]

parts = ["ตอนที่ 2", "ตอนที่ 3", "ตอนที่ 3", "ตอนที่ 3–4", "ตอนที่ 4"]

els = [title("แผนที่การเรียน : ทฤษฎี → ฟีเจอร์ของ Plane → LAB ที่ได้ลงมือทำ")]

# column headers
els += [
    box("ht", TX, 72, TW, 38, "ทฤษฎี", INK, GREYBG, 19),
    box("hp", PX, 72, PW, 38, "ฟีเจอร์ของ Plane", INK, GREYBG, 19),
    box("hl", LX, 72, LW, 38, "LAB", INK, GREYBG, 19),
]

for i, (rid, c, bg, tlines, tcap, plines, pcap, lab, lcap) in enumerate(rows):
    y = Y0 + i * STEP
    cy = y + H // 2
    # ทฤษฎี
    els.append(box(f"t{rid}", TX, y, TW, H, "", c, bg, 16))
    ty = y + 9 if len(tlines) == 2 else y + 20
    for k, ln in enumerate(tlines):
        els.append(txt(TX + 16, ty + k * 23, ln, 17, INK))
    els.append(txt(TX + 16, y + 58, tcap, 13, MUTED))
    els.append(box(f"b{rid}", TX + TW - 134, y + 8, 122, 24, parts[i], c, "#ffffff", 12))
    # Plane
    els.append(box(f"p{rid}", PX, y, PW, H, "", c, bg, 16))
    els.append(txt(PX + 16, y + 20, plines[0], 17, INK))
    els.append(txt(PX + 16, y + 58, pcap, 13, MUTED))
    # LAB
    els.append(box(f"l{rid}", LX, y, LW, H, "", c, bg, 16))
    els.append(txt(LX + 16, y + 10, lab, 20, c))
    els.append(txt(LX + 16, y + 42, lcap, 13, MUTED))
    # arrows
    els.append(arrow(f"t{rid}", f"p{rid}", c, x=TX + TW + 5, y=cy, w=PX - TX - TW - 10, h=0))
    els.append(arrow(f"p{rid}", f"l{rid}", c, x=PX + PW + 5, y=cy, w=LX - PX - PW - 10, h=0))

els.append(txt(30, 598, "อ่านจากซ้ายไปขวา : แนวคิดที่เรียน → ฟีเจอร์ที่ใช้แทนใน Plane → LAB ที่ได้ลงมือทำจริง (ตอนที่ 1–4 ของวิชา)", 14, MUTED))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d38-theory-plane-lab-map.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
