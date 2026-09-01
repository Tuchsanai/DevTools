#!/usr/bin/env python3
"""d40 — Prioritisation: three methods (value×effort, MoSCoW, WSJF) converge into ONE ordered backlog; Plane mapping."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d40-prioritization"
YEL = "#e67700"


def dot(id, cx, cy, c):
    """Small filled port on a panel edge: arrows bound here leave the panel exactly at mid-right
    (the canvas routes bound arrows centre-to-centre, so binding to the wide zone itself would
    exit through its top/bottom edge)."""
    return {"id": id, "type": "ellipse", "x": cx - 7, "y": cy - 7, "width": 14, "height": 14,
            "backgroundColor": c, "strokeColor": c, "fillStyle": "solid", "strokeWidth": 2, "roughness": 0}

els = [title("จัดลำดับความสำคัญ : หลายวิธีคิด → Backlog ที่เรียงลำดับเดียว")]

# ---------------------------------------------------------------- panel 1 : Value × Effort 2×2
P1Y, P1H = 65, 205
els += [
    zone(30, P1Y, 600, P1H, BLUE, SKYBG, id="m1"),
    txt(45, P1Y + 10, "1  Value × Effort matrix", 17, BLUE),
    txt(48, P1Y + 48, "Value\nสูง", 14, MUTED),
    txt(48, P1Y + 116, "Value\nต่ำ", 14, MUTED),
    box("q1", 120, P1Y + 35, 235, 62, "ทำก่อน\n(quick win)", GREEN, GREENBG),
    box("q2", 365, P1Y + 35, 235, 62, "วางแผน\n(big project)", BLUE, BLUEBG),
    box("q3", 120, P1Y + 103, 235, 62, "เติมเมื่อว่าง\n(fill-in)", YEL, YELBG),
    box("q4", 365, P1Y + 103, 235, 62, "ตัดทิ้ง\n(avoid)", RED, REDBG),
    txt(190, P1Y + 172, "Effort น้อย", 14, MUTED),
    txt(440, P1Y + 172, "Effort มาก", 14, MUTED),
]

# ---------------------------------------------------------------- panel 2 : MoSCoW
P2Y, P2H = 285, 115
els += [
    zone(30, P2Y, 600, P2H, ORANGE, "#fff4e6", id="m2"),
    txt(45, P2Y + 10, "2  MoSCoW", 17, ORANGE),
]
mos = [("Must\nต้องมี", RED, REDBG), ("Should\nควรมี", ORANGE, ORANGEBG),
       ("Could\nมีก็ดี", BLUE, BLUEBG), ("Won't\nไม่ทำรอบนี้", MUTED, GREYBG)]
for i, (t, c, bg) in enumerate(mos):
    els.append(box(f"mo{i}", 45 + i * 145, P2Y + 40, 135, 60, t, c, bg))

# ---------------------------------------------------------------- panel 3 : WSJF
P3Y, P3H = 415, 125
els += [
    zone(30, P3Y, 600, P3H, TEAL, TEALBG, id="m3"),
    txt(45, P3Y + 10, "3  WSJF (Weighted Shortest Job First)", 17, TEAL),
    box("wf", 45, P3Y + 37, 300, 60, "WSJF =\nCost of Delay ÷ Duration", TEAL, "#ffffff"),
    box("wx", 355, P3Y + 37, 260, 60, "เช่น CoD 8 ÷ 3 = 2.7\nค่ามาก → ทำก่อน", TEAL, "#ffffff"),
    txt(45, P3Y + 102, "Cost of Delay = มูลค่า/ความเสี่ยงที่เสียไปทุกสัปดาห์ที่ยังไม่ทำ  ·  Duration = เวลาที่ใช้ทำ", 13, MUTED),
]

# ---------------------------------------------------------------- right : ONE ordered backlog
LX, LY, LW, LH = 830, 65, 350, 475
els += [
    zone(LX, LY, LW, LH, PURPLE, PURPLEBG, id="bl"),
    txt(LX + 15, LY + 10, "Backlog เรียงลำดับเดียว (PO ตัดสิน)", 18, PURPLE),
    txt(LX + 20, LY + 38, "ลำดับ · work item", 13, MUTED),
    txt(LX + 245, LY + 38, "priority", 13, MUTED),
]
items = [
    ("1  รีเซ็ตรหัสผ่าน", "urgent", RED, REDBG),
    ("2  แจ้งเตือนอีเมล", "high", ORANGE, ORANGEBG),
    ("3  export CSV", "medium", YEL, YELBG),
    ("4  ค้นหาขั้นสูง", "medium", YEL, YELBG),
    ("5  dark mode", "low", BLUE, BLUEBG),
    ("6  รองรับหลายภาษา", "none", MUTED, GREYBG),
]
for i, (t, pr, c, bg) in enumerate(items):
    y = LY + 55 + i * 60
    els.append(box(f"it{i}", LX + 15, y, 215, 50, t, PURPLE, "#ffffff"))
    els.append(box(f"pr{i}", LX + 240, y, 95, 50, pr, c, bg))
els.append(txt(LX + 15, LY + 418, "เลขลำดับ = ตำแหน่งบน backlog (sort_order) ไม่ใช่ priority\nลำดับเดียว ไม่มีเสมอกัน — เสมอกัน = ยังไม่ได้ตัดสินใจ", 13, MUTED))

# converging arrows : port dot on each panel's right edge → the single list
els += [
    dot("d1", 630, P1Y + P1H // 2, BLUE),
    dot("d2", 630, P2Y + P2H // 2, ORANGE),
    dot("d3", 630, P3Y + P3H // 2, TEAL),
    arrow("d1", "bl", BLUE, x=637, y=P1Y + P1H // 2, w=189, h=(LY + 175) - (P1Y + P1H // 2)),
    arrow("d2", "bl", ORANGE, x=637, y=P2Y + P2H // 2, w=189, h=(LY + 255) - (P2Y + P2H // 2)),
    arrow("d3", "bl", TEAL, x=637, y=P3Y + P3H // 2, w=189, h=(LY + 320) - (P3Y + P3H // 2)),
    txt(655, 250, "รวมเป็น\nลำดับเดียว", 13, MUTED),
]

# ---------------------------------------------------------------- footer : mapping to Plane
FY = 548
els += [
    zone(30, FY, 1150, 72, GREEN, GREENBG),
    txt(45, FY + 6, "ใน Plane", 15, GREEN),
    box("f1", 45, FY + 26, 470, 40, "priority: urgent · high · medium · low · none", GREEN, "#ffffff"),
    txt(522, FY + 34, "+", 22, GREEN),
    box("f2", 545, FY + 26, 280, 40, "ลากจัดลำดับ (sort_order)", GREEN, "#ffffff"),
    txt(832, FY + 34, "·", 22, GREEN),
    box("f3", 850, FY + 26, 315, 40, "urgent = Expedite ตาม policy", RED, REDBG),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
