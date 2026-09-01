#!/usr/bin/env python3
"""d21-issue-lifecycle : Report → Triage (accept / decline / duplicate / snooze) → Prioritise → Plan → In progress
→ Review → Done (+ Reopen back to In progress), with the matching Plane state group in a strip beneath each stage.

Note: bound-label text is always rendered at 20 px Excalifont by the canvas (fs on box() is not propagated),
so every label here was width-checked at 20 px: box inner width = w - 10."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

W, GAP, H = 136, 26, 64                      # stage / strip boxes
XS = [50 + i * (W + GAP) for i in range(7)]  # 50 212 374 536 698 860 1022  (last box ends at 1158)
CX = [x + W // 2 for x in XS]
SY = 185                                     # stage row top
BY, BW, BH = 335, 100, 64                    # triage-branch row
PY = 474                                     # Plane strip top

# colour = the Plane state group the stage lives in
stages = [
    ("s1", "แจ้ง / สร้าง\nReport", TEAL, TEALBG),
    ("s2", "คัดกรอง\nTriage", TEAL, TEALBG),
    ("s3", "จัดลำดับ\nPrioritise", PURPLE, PURPLEBG),
    ("s4", "วางแผน\nPlan · Cycle", BLUE, BLUEBG),
    ("s5", "กำลังทำ\nIn progress", ORANGE, ORANGEBG),
    ("s6", "ตรวจ\nReview", ORANGE, ORANGEBG),
    ("s7", "เสร็จ\nDone", GREEN, GREENBG),
]

els = [
    title("วงจรชีวิตของ Issue : รายงาน → คัดกรอง → จัดลำดับ → วางแผน → ทำ → ตรวจ → เสร็จ"),
    zone(30, 60, 1150, 360, BLUE, SKYBG),
    txt(45, 66, "วงจรชีวิตของ issue — แบบแผนเดียวกันใน Jira · GitHub Issues · Plane", 16, BLUE),
]
for i, (sid, label, c, bg) in enumerate(stages):
    els.append(box(sid, XS[i], SY, W, H, label, c, bg, 15))
for i in range(6):
    els.append(arrow(f"s{i+1}", f"s{i+2}", MUTED, x=XS[i] + W + 4, y=SY + H // 2, w=GAP - 8, h=0))

# Reopen : Done → dashed waypoint above the row → In progress (two straight bound arrows, nothing crossed)
RX = (CX[4] + CX[6]) // 2 - 70
els += [
    box("reopen", RX, 78, 140, H, "Reopen\nยังไม่ผ่านจริง", RED, REDBG, 15, dashed=True),
    arrow("s7", "reopen", RED, dashed=True, x=CX[6] - 49, y=SY, w=-64, h=-43),
    arrow("reopen", "s5", RED, dashed=True, x=RX + 91, y=142, w=-64, h=43),
]

# Triage outcomes as small branches hanging under the Triage box
bx0 = CX[1] - (4 * BW + 3 * 12) // 2
branches = [
    ("b1", "accept\nรับเข้า", GREEN, GREENBG),
    ("b2", "decline\nไม่ทำ", RED, REDBG),
    ("b3", "duplicate\nซ้ำใบเดิม", RED, REDBG),
    ("b4", "snooze\nพักไว้ก่อน", MUTED, GREYBG),
]
for i, (bid, label, c, bg) in enumerate(branches):
    x = bx0 + i * (BW + 12)
    els.append(box(bid, x, BY, BW, BH, label, c, bg, 15))
    els.append(arrow("s2", bid, c, dashed=(bid == "b4"), x=CX[1], y=SY + H, w=x + BW // 2 - CX[1], h=BY - SY - H))
els.append(txt(540, 338, "ผลการคัดกรอง — ตัดสินใจก่อนเข้า backlog\n"
                         "accept = ไปต่อที่จัดลำดับ  ·  decline / duplicate = ทีมย้าย state เองตาม policy  ·  snooze = พักไว้", 14, MUTED))

# Plane state-group strip : one box under each stage column
els += [
    zone(30, 436, 1150, 122, TEAL, TEALBG),
    txt(XS[2], 442, "Plane : state group ที่ใบงานอยู่ในแต่ละช่วง — ตั้งชื่อ state เองได้ แต่ group เป็นตัวกำหนดพฤติกรรม", 16, TEAL),
    box("p1", XS[0], PY, W, H, "Intake\ntriage state", TEAL, "#ffffff", 15),
    box("p2", XS[1], PY, W, H, "ยังอยู่ triage\nทีมย้ายเองตาม policy", TEAL, "#ffffff", 15, dashed=True),
    box("p3", XS[2], PY, W, H, "backlog", PURPLE, "#ffffff", 15),
    box("p4", XS[3], PY, W, H, "unstarted\n(Todo)", BLUE, "#ffffff", 15),
    box("p5", XS[4], PY, W, H, "started\nIn Progress", ORANGE, "#ffffff", 15),
    box("p6", XS[5], PY, W, H, "started\nIn Review", ORANGE, "#ffffff", 15),
    box("p7", XS[6], PY, W, H, "completed\n(Done)", GREEN, "#ffffff", 15),
]

# footnote
els.append(txt(40, 574, "Reopen = ย้าย state กลับไปกลุ่ม started บนใบเดิม ไม่สร้างใบใหม่ (ประวัติครบใน activity log)  ·  "
                        "เข้า completed เมื่อผ่าน Definition of Done → Plane ตั้ง completed_at ให้\n"
                        "decline / duplicate เปลี่ยนสถานะ Intake แต่ไม่ย้าย state — ทีมย้ายเองตาม policy  ·  Intake เปิดได้ที่ Project settings → Features", 14, MUTED))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d21-issue-lifecycle.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
