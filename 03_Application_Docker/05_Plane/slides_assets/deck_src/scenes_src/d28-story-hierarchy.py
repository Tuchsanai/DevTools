#!/usr/bin/env python3
"""d28 — Work-item hierarchy: Epic → User Story → Task → Subtask (+ Bug) and the Plane CE mapping."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

els = [
    title("ลำดับชั้นของงาน : Epic → User Story → Task → Subtask (+ Bug) และชื่อเรียกใน Plane"),

    # ---------------- left: the hierarchy tree
    zone(30, 70, 740, 540, BLUE, SKYBG),
    txt(45, 82, "ขนาด ≈", 15, MUTED),
    txt(175, 80, "ลำดับชั้นของงาน (แนวคิด Agile)", 18, BLUE),

    # size hints (left strip)
    txt(45, 128, "สัปดาห์–เดือน", 14, MUTED),
    txt(45, 240, "หลายวัน", 14, MUTED),
    txt(45, 352, "ชั่วโมง–1 วัน", 14, MUTED),

    # Epic
    box("epic", 325, 105, 280, 66, "Epic\nงานใหญ่ กินเวลาหลาย sprint", PURPLE, PURPLEBG, 16),

    # User stories
    box("st1", 175, 205, 180, 88, "User Story 1\nAs a … I want …\nso that …", BLUE, BLUEBG, 14),
    box("st2", 375, 205, 180, 88, "User Story 2\nAs a … I want …\nso that …", BLUE, BLUEBG, 14),
    box("st3", 575, 205, 180, 88, "User Story 3\nAs a … I want …\nso that …", BLUE, BLUEBG, 14),
    arrow("epic", "st1", PURPLE, x=405, y=171, w=-140, h=34),
    arrow("epic", "st2", PURPLE, x=465, y=171, w=0, h=34),
    arrow("epic", "st3", PURPLE, x=525, y=171, w=140, h=34),

    # Tasks under story 2
    box("tk1", 305, 330, 150, 62, "Task 1\nงานเชิงเทคนิค", ORANGE, ORANGEBG, 14),
    box("tk2", 475, 330, 150, 62, "Task 2\nงานเชิงเทคนิค", ORANGE, ORANGEBG, 14),
    arrow("st2", "tk1", BLUE, x=430, y=293, w=-50, h=37),
    arrow("st2", "tk2", BLUE, x=500, y=293, w=50, h=37),

    # Subtask under task 2
    box("sub", 475, 430, 190, 56, "Subtask\nงานย่อยของ Task", TEAL, TEALBG, 14),
    arrow("tk2", "sub", ORANGE, x=570, y=392, w=0, h=38),

    # Bug — a type that can sit at story or task level (dashed links)
    box("bug", 175, 515, 200, 70, "Bug\nข้อบกพร่อง\nexpected ≠ actual", RED, REDBG, 14),
    arrow("bug", "st1", RED, dashed=True, x=265, y=515, w=0, h=-222),
    arrow("bug", "tk1", RED, dashed=True, x=345, y=515, w=35, h=-123),
    txt(395, 588, "เส้นประ = Bug อยู่ได้ทั้งระดับ story และระดับ task", 13, MUTED),

    # ---------------- right: Plane CE mapping
    zone(800, 70, 380, 540, GREEN, GREENBG),
    txt(820, 80, "ใน Plane (Community Edition)", 18, GREEN),
    box("m1", 830, 105, 320, 66, "Module\n(lead · members · progress)", GREEN, "#ffffff", 14),
    box("m2", 830, 205, 320, 187, "Work item\n\nStory และ Task ใช้ชนิดเดียวกัน\nต่างกันที่ขนาดและรายละเอียด\n(PLAB-12, PLAB-13, …)", GREEN, "#ffffff", 14),
    box("m3", 830, 430, 320, 56, "Sub-work item\n(ตั้ง parent = work item แม่)", GREEN, "#ffffff", 14),
    box("m4", 830, 515, 320, 70, "Label \"bug\"\nCE ไม่มี work item type\n→ ใช้ label แทน", RED, "#ffffff", 14),
    arrow("epic", "m1", PURPLE, x=610, y=138, w=215, h=0),
    arrow("st3", "m2", BLUE, x=760, y=249, w=65, h=0),
    arrow("tk2", "m2", ORANGE, x=630, y=361, w=195, h=0),
    arrow("sub", "m3", TEAL, x=670, y=458, w=155, h=0),
    arrow("bug", "m4", RED, x=380, y=550, w=445, h=0),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d28-story-hierarchy.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
