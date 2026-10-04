#!/usr/bin/env python3
"""d29 — Relative estimation: compare every story to a reference story (2 pt), not to a clock."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

els = [
    title("Relative estimation : เทียบขนาดกับเรื่องอ้างอิง ไม่ใช่นับชั่วโมง"),

    # ---------------------------------------------------------------- left inset : absolute hours
    zone(30, 75, 260, 508, RED, "#fff5f5"),
    txt(45, 85, "แบบเดิม : ประเมินเป็นชั่วโมง", 17, RED),
    txt(45, 112, "เรื่องเดียวกัน ถามคนละคน", 14, MUTED),
    box("h1", 55, 145, 210, 50, "คนที่ 1  →  8h ?", MUTED, "#ffffff", 16),
    box("h2", 55, 210, 210, 50, "คนที่ 2  →  12h ?", MUTED, "#ffffff", 16),
    box("h3", 55, 275, 210, 50, "คนที่ 3  →  30h ?", MUTED, "#ffffff", 16),
    dict(line(45, 135, [[0, 0], [230, 200]], RED, 4), opacity=45),
    dict(line(275, 135, [[0, 0], [-230, 200]], RED, 4), opacity=45),
    txt(45, 365, "คนต่างกัน เวลาต่างกัน", 18, RED),
    txt(45, 395, "8h ของใคร? เร็วหรือช้า?\nตัวเลขชั่วโมงกลายเป็น\n\"คำสัญญา\" ที่ถูกทวง", 14, MUTED),
    txt(45, 480, "→ เลิกถาม \"กี่ชั่วโมง\"\n   ถาม \"ใหญ่กว่าเรื่องอ้างอิงกี่เท่า\"", 14, INK),

    # ---------------------------------------------------------------- centre : reference story + comparisons
    txt(320, 85, "เทียบกับเรื่องอ้างอิง (reference story)", 17, GREEN),
    txt(320, 118, "1) เลือกเรื่องกลาง ๆ ที่ทุกคนเข้าใจดี → 2 pt\n2) เรื่องอื่นเทียบกับเรื่องนี้\n3) เลือกตัวเลขที่ใกล้สุดจาก 1 2 3 5 8 13", 14, INK),
    box("ref", 320, 255, 200, 100, "เรื่องอ้างอิง\nเข้าสู่ระบบด้วยอีเมล\n= 2 pt", GREEN, GREENBG, 16),
    txt(320, 380, "ทุกเรื่องถามคำถามเดียว :\n\"เล็กหรือใหญ่กว่าเรื่องนี้กี่เท่า\"", 14, MUTED),

    box("s1", 645, 113, 170, 60, "ปุ่มลืมรหัสผ่าน\n= 1 pt", BLUE, BLUEBG, 14),
    box("s5", 645, 255, 230, 90, "รีเซ็ตรหัสผ่านทางอีเมล\n= 5 pt", ORANGE, ORANGEBG, 15),
    box("s13", 645, 425, 245, 115, "ล็อกอินด้วย Google/OAuth\n= 13 pt\nใหญ่เกินไป → ควรแตก", RED, REDBG, 13, dashed=True),

    arrow("ref", "s1", BLUE, x=525, y=290, w=115, h=-145),
    txt(536, 178, "ครึ่งหนึ่ง", 15, BLUE),
    arrow("ref", "s5", ORANGE, x=525, y=305, w=115, h=-5),
    txt(522, 279, "ประมาณสองเท่า", 14, ORANGE),
    arrow("ref", "s13", RED, x=525, y=335, w=115, h=145),
    txt(600, 383, "ใหญ่กว่ามาก", 15, RED),

    txt(320, 560, "ใน Plane : Project settings → Estimates (Points) แล้วเลือก estimate บน work item", 14, MUTED),

    # ---------------------------------------------------------------- right inset : what a point is
    zone(920, 75, 260, 508, TEAL, TEALBG),
    txt(935, 85, "1 point คืออะไร", 17, TEAL),
    box("ef", 940, 112, 220, 64, "ความพยายาม\n(effort)", TEAL, "#ffffff", 14),
    txt(1042, 181, "+", 22, TEAL),
    box("cx", 940, 210, 220, 64, "ความซับซ้อน\n(complexity)", TEAL, "#ffffff", 14),
    txt(1042, 279, "+", 22, TEAL),
    box("un", 940, 308, 220, 64, "ความไม่แน่นอน\n(uncertainty)", TEAL, "#ffffff", 14),
    txt(1042, 377, "=", 22, TEAL),
    box("pt", 940, 405, 220, 48, "story point", GREEN, GREENBG, 17),
    box("scale", 940, 462, 220, 112, "มาตรวัดของทีมนี้เท่านั้น\n2 pt ของทีม A\n≠ 2 pt ของทีม B\nห้ามเทียบข้ามทีม", ORANGE, ORANGEBG, 13),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d29-relative-estimation.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(out)
