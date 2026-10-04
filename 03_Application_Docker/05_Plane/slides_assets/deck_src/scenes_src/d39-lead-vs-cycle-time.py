#!/usr/bin/env python3
"""d39-lead-vs-cycle-time : one work item on a time axis — Lead time (customer view) vs Cycle time (team view)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d39-lead-vs-cycle-time"

# time axis: 03/08 00:00 → 08/08 00:00 (120 h) mapped onto x 110 → 1140
X0, PXH = 110, 1030 / 120


def X(h):
    return round(X0 + h * PXH)


H_CREATED, H_STARTED, H_DONE = 9, 58, 112          # 03/08 09:00 · 05/08 10:00 · 07/08 16:00
XC, XS, XD = X(H_CREATED), X(H_STARTED), X(H_DONE)  # 187 · 608 · 1071
AXIS_Y = 306

els = [title("Lead time vs Cycle time : work item ใบเดียวกัน แต่เริ่มนับคนละจุด")]

# ---------------------------------------------------------------- timeline zone
els += [
    zone(30, 72, 1150, 336, TEAL, TEALBG),
    txt(50, 82, "เส้นเวลาของ work item PLAB-12", 16, TEAL),
]

# lead-time bracket (above) : created → done
LW = XD - XC
els += [
    line(XC, 146, [[0, 12], [0, 0], [LW, 0], [LW, 12]], BLUE, 3),
    box("lt_lab", (XC + XD) // 2 - 280, 104, 560, 36,
        "Lead time = เสร็จ − สร้าง = 4 วัน 7 ชม.   (มุมมองลูกค้า)", BLUE, "#ffffff", 17),
]

# milestone boxes on the axis
W1, W2, W3 = 200, 280, 200
els += [
    box("m1", XC - W1 // 2, 164, W1, 76, "สร้าง\ncreated_at\n03/08 09:00", BLUE, BLUEBG, 14),
    box("m2", XS - W2 // 2, 164, W2, 76, "เริ่มทำ\nstate → started ครั้งแรก\n05/08 10:00", ORANGE, ORANGEBG, 14),
    box("m3", XD - W3 // 2, 164, W3, 76, "เสร็จ\ncompleted_at\n07/08 16:00", GREEN, GREENBG, 14),
    arrow("m1", "m2", MUTED, x=XC + W1 // 2 + 5, y=202, w=(XS - W2 // 2) - (XC + W1 // 2 + 10), h=0),
    arrow("m2", "m3", MUTED, x=XS + W2 // 2 + 5, y=202, w=(XD - W3 // 2) - (XS + W2 // 2 + 10), h=0),
]

# waiting / working segments
els += [
    box("wait", XC, 268, XS - XC, 32, "รอ (waiting) · 2 วัน 1 ชม.", MUTED, GREYBG, 14),
    box("work", XS, 268, XD - XS, 32, "ทำจริง (working) · 2 วัน 6 ชม.", ORANGE, ORANGEBG, 14),
    line(XC, 240, [[0, 0], [0, AXIS_Y - 240]], BLUE, 2, dashed=True),
    line(XS, 240, [[0, 0], [0, AXIS_Y - 240]], ORANGE, 2, dashed=True),
    line(XD, 240, [[0, 0], [0, AXIS_Y - 240]], GREEN, 2, dashed=True),
]

# axis with daily ticks
els.append(line(X0, AXIS_Y, [[0, 0], [1030, 0]], INK, 2))
for d in range(6):
    xd = X(d * 24)
    els.append(line(xd, AXIS_Y, [[0, 0], [0, 6]], INK, 1))
    els.append(txt(xd - 19, AXIS_Y + 8, f"0{3 + d}/08", 13, MUTED))

# cycle-time bracket (below) : started → done
CW = XD - XS
els += [
    line(XS, 352, [[0, -12], [0, 0], [CW, 0], [CW, -12]], ORANGE, 3),
    box("ct_lab", (XS + XD) // 2 - 270, 360, 540, 36,
        "Cycle time = เสร็จ − เริ่มทำ = 2 วัน 6 ชม.   (มุมมองทีม)", ORANGE, "#ffffff", 17),
]

# ---------------------------------------------------------------- bottom strip : two views + P85 note
els += [
    box("v_cust", 30, 428, 365, 100, "มุมมองลูกค้า = Lead time\nนับตั้งแต่ขอ จนได้ของ\n(รวมเวลารอคิวทั้งหมด)", BLUE, BLUEBG, 15),
    box("v_team", 415, 428, 365, 100, "มุมมองทีม = Cycle time\nนับตั้งแต่ลงมือ จนเสร็จ\n(ไม่รวมเวลารอก่อนเริ่ม)", ORANGE, ORANGEBG, 15),
    box("p85", 800, 428, 380, 100, "รายงานด้วย P85 ไม่ใช่ค่าเฉลี่ย\n(85 % ของใบเสร็จภายในค่านี้)\nเพราะ outlier ดึงค่าเฉลี่ยให้เพี้ยน", PURPLE, PURPLEBG, 15),
    txt(30, 544, "Lead time ≥ Cycle time เสมอ · ส่วนต่าง = เวลารอคิว → ลด WIP และจัดลำดับ backlog ช่วยลดส่วนนี้ได้", 14, INK),
    txt(30, 570, "ข้อมูลใน Plane : created_at · IssueActivity (field = state) ครั้งแรกที่เข้า group started · completed_at  →  LAB 5 flow_metrics.py", 14, MUTED),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
