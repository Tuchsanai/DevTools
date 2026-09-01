#!/usr/bin/env python3
"""d35-wip-limit-effect : effect of a WIP limit (Little's Law) — before/after panels.

Terminology follows d39: WIP here = cards in the In Progress column only, so WIP ÷ throughput is the
time spent *in that column* = Cycle time (team view). Lead time (customer view) would also include the
waiting time of the To Do cards.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d35-wip-limit-effect"
CARD_W, CARD_H, GAP = 88, 46, 8


def cards(prefix, x0, y0, n, text, stroke, bg):
    out = []
    for i in range(n):
        col, row = i % 3, i // 3
        out.append(box(f"{prefix}{i}", x0 + col * (CARD_W + 10), y0 + row * (CARD_H + GAP),
                       CARD_W, CARD_H, text, stroke, bg, 12))
    return out


els = [title("ผลของ WIP limit (Little's Law) : ลด WIP → งานออกเร็วขึ้น โดยไม่ต้องเพิ่มคน")]

# ---------------------------------------------------------------- Panel A : no WIP limit
els += [
    zone(30, 72, 560, 340, RED, "#fff5f5"),
    txt(50, 82, "A · ไม่มี WIP limit — ใครว่างก็เริ่มงานใหม่ได้เรื่อย ๆ", 18, RED),
    box("col_a", 50, 115, 300, 257, "", ORANGE, "#ffffff", 14),
    txt(62, 123, "In Progress · 12 ใบ  (ล้น!)", 16, RED),
]
els += cards("a", 58, 150, 12, "80 %\nเสร็จ", RED, REDBG)
els += [
    box("tp_a", 385, 115, 185, 60, "Throughput\n3 ใบ/วัน", BLUE, BLUEBG, 15),
    box("lt_a", 385, 210, 185, 80, "Cycle time ≈\n12 ÷ 3 = 4 วัน", RED, REDBG, 17),
    box("na", 385, 315, 185, 70, "ทุกใบ 80 % เสร็จ\nส่งมอบไม่ได้เลย", MUTED, GREYBG, 13),
    arrow("col_a", "lt_a", RED, x=352, y=250, w=31, h=0),
    arrow("tp_a", "lt_a", BLUE, x=477, y=180, w=0, h=30),
]

# ---------------------------------------------------------------- Panel B : WIP limit 6
els += [
    zone(610, 72, 570, 340, GREEN, GREENBG),
    txt(630, 82, "B · WIP limit 6 — คอลัมน์เต็มแล้ว ห้ามดึงงานใหม่", 18, GREEN),
    box("col_b", 630, 115, 300, 257, "", ORANGE, "#ffffff", 14),
    txt(642, 123, "In Progress (WIP ≤ 6) · 6/6 เต็ม", 16, GREEN),
]
els += cards("b", 638, 150, 6, "ทำจนจบ", BLUE, BLUEBG)
els += [
    box("wait_b", 640, 264, 280, 92, "อีก 6 ใบรออยู่ใน To Do\n(ยังไม่เริ่ม = ไม่นับเป็น WIP)\nเวลารอนี้นับใน lead time\nไม่ใช่ cycle time", MUTED, GREYBG, 13, dashed=True),
    box("tp_b", 965, 115, 195, 60, "Throughput\n3 ใบ/วัน (เท่าเดิม)", BLUE, BLUEBG, 15),
    box("lt_b", 965, 210, 195, 80, "Cycle time ≈\n6 ÷ 3 = 2 วัน", GREEN, GREENBG, 17),
    box("nb", 965, 315, 195, 70, "ทำน้อยใบแต่จบจริง\nส่งมอบได้ทุกวัน", MUTED, GREYBG, 13),
    arrow("col_b", "lt_b", GREEN, x=932, y=250, w=31, h=0),
    arrow("tp_b", "lt_b", BLUE, x=1062, y=180, w=0, h=30),
]

# ---------------------------------------------------------------- Formula + rule strip
els += [
    box("formula", 30, 435, 520, 80, "Cycle time  ≈  WIP  ÷  Throughput", PURPLE, PURPLEBG, 24),
    txt(30, 525, "Little's Law : throughput เท่าเดิม ลด WIP ลงครึ่งหนึ่ง → cycle time สั้นลงครึ่งหนึ่ง\n(WIP ที่นับ = ใบใน In Progress เท่านั้น · ใบที่รอใน To Do ไม่นับ)", 14, PURPLE),
    box("rule", 580, 435, 600, 80, "คอลัมน์เต็ม = หยุดดึงงานใหม่ ไปช่วยปิดงานที่ค้าง\n(stop starting · start finishing)", ORANGE, ORANGEBG, 17),
    txt(580, 525, "งาน 12 ใบเท่ากัน คนเท่ากัน ต่างกันแค่ “เริ่มพร้อมกันกี่ใบ”", 14, MUTED),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(out, len(els), "elements")
