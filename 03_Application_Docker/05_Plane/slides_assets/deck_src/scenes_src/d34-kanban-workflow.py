#!/usr/bin/env python3
"""d34 — Kanban board with pull arrows, WIP limits and explicit policies (Thai deck).

Note: bound labels created via box() always render at 20 px Excalifont on the canvas, so boxes are sized for that;
dense policy text uses txt() overlays (helvetica) inside empty boxes, like the card in d06.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

# ---- geometry -------------------------------------------------------------
X0, CW, GAP = 30, 140, 40              # column origin, column width, gap for pull arrows
HY, HH = 68, 56                         # header row
ZY, ZH = 132, 284                       # column body (zone)
CARD_W, CARD_GAP = 122, 8
CARD_Y0 = ZY + 34
PY, PH = 448, 76                        # policy strip

cols = [
    # key, header, stroke, bg, count label, count colour, cards [(text, height)], policy lines
    ("bl", "Backlog", MUTED, GREYBG, "5 ใบ · ไม่จำกัด", MUTED,
     [("PLAB-40", 36), ("PLAB-41", 36), ("PLAB-42", 36), ("PLAB-43", 36), ("PLAB-44", 36)],
     "ทุกไอเดีย / คำขอ\nยังไม่ต้องละเอียด\nPO จัดลำดับ"),
    ("rd", "Ready", BLUE, BLUEBG, "3 ใบ", BLUE,
     [("PLAB-33\n5 pt", 56), ("PLAB-35\n3 pt", 56), ("PLAB-36\n8 pt", 56)],
     "มี acceptance\ncriteria + estimate\nขนาด ≤ 8 pt"),
    ("ip", "In Progress\n(WIP ≤ 3)", ORANGE, ORANGEBG, "3/3  เต็ม!", RED,
     [("PLAB-24\nAnn", 56), ("PLAB-27\nBee", 56), ("PLAB-30\nChai", 56)],
     "≤ 3 ใบ\nทุกใบมีเจ้าของ\nอัปเดตทุกวัน"),
    ("rv", "Review\n(WIP ≤ 2)", PURPLE, PURPLEBG, "1/2", PURPLE,
     [("PLAB-19\nPR #42", 56)],
     "≤ 2 ใบ\nมี PR + test ผ่าน\nรีวิวโดยคนอื่น"),
    ("dn", "Done", GREEN, GREENBG, "5 ใบ / สัปดาห์", GREEN,
     [("✓ PLAB-11", 36), ("✓ PLAB-12", 36), ("✓ PLAB-15", 36), ("✓ PLAB-17", 36), ("✓ PLAB-18", 36)],
     "ผ่าน DoD\nขึ้น staging แล้ว\nปิดใบใน Plane"),
]

els = [title("Kanban board : ดึงงาน (pull) ทีละใบ · จำกัด WIP · นโยบายชัดเจนใต้ทุกคอลัมน์")]

for i, (key, head, c, bg, cnt, cntc, cards, policy) in enumerate(cols):
    x = X0 + i * (CW + GAP)
    els.append(box(f"h_{key}", x, HY, CW, HH, head, c, bg, 16))
    els.append(zone(x, ZY, CW, ZH, c, "#ffffff", id=f"z_{key}"))
    els.append(txt(x + 10, ZY + 8, cnt, 14, cntc))
    y = CARD_Y0
    for j, (card, ch) in enumerate(cards):
        els.append(box(f"c_{key}{j}", x + 9, y, CARD_W, ch, card, c, bg, 16))
        y += ch + CARD_GAP
    els.append(box(f"p_{key}", x, PY, CW, PH, "", c, "#ffffff", 13, dashed=True))
    els.append(txt(x + 8, PY + 9, policy, 14, INK))

# full-column warning inside In Progress
ipx = X0 + 2 * (CW + GAP)
els.append(txt(ipx + 10, ZY + 232, "เต็ม! ห้ามดึงใบใหม่\nไปช่วย review /\nปิดงานที่ค้างก่อน", 12, RED))

# pull arrows between column bodies
mid = ZY + ZH // 2
for i in range(4):
    a, b = cols[i][0], cols[i + 1][0]
    gx = X0 + i * (CW + GAP) + CW
    blocked = (i == 1)                       # Ready → In Progress is blocked (3/3)
    els.append(arrow(f"z_{a}", f"z_{b}", RED if blocked else MUTED, dashed=blocked,
                     x=gx, y=mid, w=GAP, h=0))
    if blocked:
        els.append(txt(gx + 5, mid - 38, "หยุด\nดึง", 13, RED))
    else:
        els.append(txt(gx + 3, mid - 38, "ดึง\n(pull)", 13, MUTED))

# policy strip label + footer
els.append(txt(X0, 424, "นโยบายชัดเจน (explicit policies) : การ์ดจะเข้าคอลัมน์นี้ได้เมื่อ …   (เขียนไว้ใน Page ของโปรเจกต์)", 14, MUTED))
els.append(txt(X0, 542, "Pull = คอลัมน์ถัดไปดึงงานเมื่อมีที่ว่าง ไม่ใช่ถูกยัดเข้ามา\nIn Progress เต็ม 3/3 → หยุดเริ่มงานใหม่ ไปช่วยปิดงานที่ค้าง (stop starting, start finishing)", 14, INK))

# side note: 6 Kanban practices
SX, SW = 920, 260
els.append(zone(SX, HY, SW, PY + PH - HY, TEAL, TEALBG))
els.append(txt(SX + 15, HY + 10, "6 แนวปฏิบัติของ Kanban", 17, TEAL))
practices = [
    "Visualise\nเห็นงานทุกใบบนบอร์ด",
    "Limit WIP\nจำกัดงานค้าง",
    "Manage flow\nดูแลการไหลของงาน",
    "Explicit policies\nนโยบายเขียนชัด",
    "Feedback loops\nรอบ feedback สั้น ๆ",
    "Improve\nปรับปรุงต่อเนื่อง",
]
for i, p in enumerate(practices):
    els.append(box(f"k{i}", SX + 15, HY + 42 + i * 66, SW - 30, 58, p, TEAL, "#ffffff", 16))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d34-kanban-workflow.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
