#!/usr/bin/env python3
"""d31 — Planning Poker: 6 steps left→right, two-round example, rules strip."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d31-planning-poker"

# ---------------------------------------------------------------- row 1 : 6 steps
steps = [
    ("1. PO อ่าน\nstory และ\nตอบคำถาม", BLUE, BLUEBG),
    ("2. ทุกคนเลือกไพ่\nแบบลับ ๆ", ORANGE, ORANGEBG),
    ("3. เปิดไพ่\nพร้อมกัน", TEAL, TEALBG),
    ("4. สูงสุด/ต่ำสุด\nอธิบายเหตุผล", PURPLE, PURPLEBG),
    ("5. โหวตรอบใหม่", ORANGE, ORANGEBG),
    ("6. ตกลงค่าเดียว\nและบันทึก", GREEN, GREENBG),
]
SX, SY, SW, SH, SGAP = 30, 105, 165, 100, 32
els = [title("Planning Poker : ประเมินร่วมกันด้วยไพ่ 6 ขั้นตอน")]
for i, (t, c, bg) in enumerate(steps):
    x = SX + i * (SW + SGAP)
    els.append(box(f"s{i+1}", x, SY, SW, SH, t, c, bg, 14))
for i in range(1, 6):
    x = SX + i * (SW + SGAP) - SGAP
    els.append(arrow(f"s{i}", f"s{i+1}", MUTED, x=x + 4, y=SY + SH // 2, w=SGAP - 8, h=0))

# loop-back : step 5 → step 2 (unbound multi-point arrow drawn above the row)
cx5 = SX + 4 * (SW + SGAP) + SW / 2
cx2 = SX + 1 * (SW + SGAP) + SW / 2
loop = arrow(None, None, ORANGE, dashed=True, x=cx5, y=SY - 8, w=cx5 - cx2, h=24)
loop.pop("startElementId"); loop.pop("endElementId")
loop["points"] = [[0, 0], [0, -26], [-(cx5 - cx2), -26], [-(cx5 - cx2), 0]]
els.append(loop)
els.append(txt(490, 80, "ยังต่างกันมาก → วนซ้ำข้อ 2–5 (ไม่เกิน 3 รอบ)", 13, ORANGE))

# ---------------------------------------------------------------- row 2 : two-round example
ZY = 235
els += [
    zone(30, ZY, 1150, 215, TEAL, TEALBG),
    txt(50, ZY + 12, "ตัวอย่าง : story เดียว โหวต 2 รอบ  (Dev A · B · C · D)", 18, TEAL),
]
CY, CW, CH, CSTEP = ZY + 55, 56, 80, 64          # card row
def cards(prefix, x0, vals, cols):
    out = []
    for k, (v, (c, bg)) in enumerate(zip(vals, cols)):
        x = x0 + k * CSTEP
        out.append(box(f"{prefix}{k}", x, CY, CW, CH, v, c, bg, 22))
        out.append(txt(x + 23, CY + CH + 6, "ABCD"[k], 12, MUTED))
    return out

els.append(box("r1", 50, CY, 70, CH, "รอบ 1", MUTED, "#ffffff", 15))
els += cards("c1", 132, ["3", "5", "5", "13"],
             [(RED, REDBG), (BLUE, BLUEBG), (BLUE, BLUEBG), (RED, REDBG)])
els.append(box("disc", 410, CY, 200, CH, "3 vs 13 ต่างกันมาก\nA และ D อธิบาย\n→ พบงานแฝง", PURPLE, PURPLEBG, 13))
els.append(box("r2", 640, CY, 70, CH, "รอบ 2", MUTED, "#ffffff", 15))
els += cards("c2", 722, ["5", "5", "8", "5"],
             [(GREEN, GREENBG), (GREEN, GREENBG), (ORANGE, ORANGEBG), (GREEN, GREENBG)])
els.append(box("sum", 1000, CY, 165, CH, "สรุป = 5\nบันทึก Estimate\n+ comment", GREEN, GREENBG, 13))
els += [
    arrow("c13", "disc", MUTED, x=385, y=CY + CH // 2, w=25, h=0),
    arrow("disc", "r2", MUTED, x=615, y=CY + CH // 2, w=25, h=0),
    arrow("c23", "sum", MUTED, x=975, y=CY + CH // 2, w=25, h=0),
    txt(50, ZY + 172, "รอบ 1 ห่างกันมาก = ยังเข้าใจ story ไม่ตรงกัน  ·  รอบ 2 ใกล้กันแล้ว → เลือกค่าที่คนส่วนใหญ่ให้ ไม่ใช่ค่าเฉลี่ย", 14, MUTED),
]

# ---------------------------------------------------------------- row 3 : rules strip
RY = 470
rules = [
    "PO ไม่โหวต\n(ถาม-ตอบได้ แต่ไม่ชี้นำ)",
    "Timebox ต่อ story\n(เช่น 5 นาที)",
    "ไม่เกิน 3 รอบ\nยังไม่ตรง → พักไว้ก่อน",
    "ค้นพบงานแฝง = กำไร\nของการคุยกัน",
]
els += [zone(30, RY, 1150, 125, ORANGE, "#fff4e6"), txt(50, RY + 10, "กติกา", 18, ORANGE)]
for i, r in enumerate(rules):
    els.append(box(f"rule{i}", 50 + i * 280, RY + 45, 262, 65, r, ORANGE, "#ffffff", 14))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
