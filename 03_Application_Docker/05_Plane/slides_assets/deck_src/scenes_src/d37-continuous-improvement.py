#!/usr/bin/env python3
"""d37 — Continuous improvement loop (Kaizen / PDCA): Measure → Retrospective → Decide → Do → Measure …
Each node is a card (coloured header box + grey "ใน Plane:" line); arrows bind to the cards so they never cross text."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *  # noqa: E402,F401

# ---- geometry: 4 cards on the corners of a ring, hub in the middle, footer below
CW, CH = 330, 140                     # card size
HX, HY = 12, 12                       # header inset inside the card
HH = 78                               # header box height
LX, RX = 60, 790                      # left / right card x
TY, BY = 80, 360                      # top / bottom card y

nodes = [  # id, x, y, header text, stroke, bg, "ใน Plane" line
    ("m", LX, TY, "1  วัดผล (Measure)\nburndown · cycle time\nCFD · activity log", BLUE, BLUEBG,
     "ใน Plane: Analytics · Cycle progress chart"),
    ("r", RX, TY, "2  ทบทวน (Retrospective)\nทีมตรวจสอบสิ่งที่เกิดขึ้น\nจากข้อมูลจริง", PURPLE, PURPLEBG,
     "ใน Plane: Page (บันทึก retro)"),
    ("d", RX, BY, "3  ตัดสินใจ (Decide)\nเลือก action items\nแค่ 1–2 ข้อ", ORANGE, ORANGEBG,
     "ใน Plane: work items ติด label improvement"),
    ("o", LX, BY, "4  ลงมือทำ (Do)\nใน sprint / cycle ถัดไป", GREEN, GREENBG,
     "ใน Plane: Cycle ถัดไป (ใส่ action items เข้าไป)"),
]

els = [title("Continuous improvement : วัดผล → ทบทวน → ตัดสินใจ → ลงมือ แล้ววนใหม่ทุก sprint")]

for nid, x, y, head, c, bg, plane in nodes:
    els.append(box(f"c{nid}", x, y, CW, CH, "", c, "#ffffff"))                 # card (arrow target)
    els.append(box(f"h{nid}", x + HX, y + HY, CW - 2 * HX, HH, head, c, bg, 15))
    els.append(txt(x + HX + 2, y + HY + HH + 11, plane, 14, MUTED))

# ---- hub
els.append(box("hub", 440, 242, 300, 96, "วงจร Kaizen / PDCA\nPlan → Do → Check → Act\n1 sprint = 1 รอบ", INK, YELBG, 15))

# ---- ring arrows (clockwise) + what flows along each edge
els += [
    arrow("cm", "cr", BLUE, x=LX + CW, y=TY + CH // 2, w=RX - LX - CW, h=0),
    txt(510, 120, "ข้อมูลจริง / หลักฐาน (evidence)", 14, BLUE),
    arrow("cr", "cd", PURPLE, x=RX + CW // 2, y=TY + CH, w=0, h=BY - TY - CH),
    txt(975, 262, "ข้อสังเกต\n(insight)", 14, PURPLE),
    arrow("cd", "co", ORANGE, x=RX, y=BY + CH // 2, w=-(RX - LX - CW), h=0),
    txt(505, 442, "action items 1–2 ข้อ → work items", 14, ORANGE),
    arrow("co", "cm", GREEN, x=LX + CW // 2, y=BY, w=0, h=-(BY - TY - CH)),
    txt(95, 262, "sprint ถัดไป\n→ วัดซ้ำ", 14, GREEN),
]

# ---- footer
els.append(box("foot", 290, 540, 600, 48, "เปลี่ยนทีละน้อย  ·  มีหลักฐาน  ·  ทุกรอบ", PURPLE, PURPLEBG, 19))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d37-continuous-improvement.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(f"wrote {out} ({len(els)} elements)")
