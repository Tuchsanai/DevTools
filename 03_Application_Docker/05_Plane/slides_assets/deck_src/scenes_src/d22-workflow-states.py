#!/usr/bin/env python3
"""d22-workflow-states : Workflow = states + transitions + policies; Plane's 5 state groups as five column zones."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d22-workflow-states"


def note(x, y, text, fs=13, color=MUTED):
    """Left-aligned multi-line text."""
    t = txt(x, y, text, fs, color)
    t["textAlign"] = "left"
    return t


# ---- five column zones (x, w, stroke, bg, group, thai meaning)
cols = [
    (30, 170, MUTED, GREYBG, "backlog", "ยังไม่วางแผน"),
    (225, 170, BLUE, SKYBG, "unstarted", "วางแผนแล้ว ยังไม่เริ่ม"),
    (420, 200, ORANGE, "#fff4e6", "started", "กำลังทำ = WIP"),
    (645, 320, GREEN, GREENBG, "completed", "เสร็จแล้ว → นับใน burndown / velocity"),
    (990, 190, RED, "#fff5f5", "cancelled", "ปิดโดยไม่ทำ ไม่นับว่าเสร็จ"),
]
ZY, ZH = 90, 320

els = [
    title("Workflow = states + transitions + policies : Plane จัด state เป็น 5 group"),
    note(30, 58, "states = กล่อง · transitions = ลูกศร (ทึบ = เส้นทางปกติ, ประ = ย้อนกลับ / ยกเลิก) · policies = ข้อตกลงที่เครื่องมือไม่บังคับ", 15),
]
for x, w, c, bg, g, th in cols:
    els.append(zone(x, ZY, w, ZH, c, bg, id="z-" + g))
    els.append(txt(x + 15, ZY + 8, "group: " + g, 18, c))
    els.append(txt(x + 15, ZY + 34, th, 13, MUTED))

R1, R2, R3, BH = 160, 266, 336, 50
els += [
    # example custom states
    box("bl", 40, R1, 150, BH, "Backlog", MUTED, "#ffffff", 15),
    box("todo", 235, R1, 150, BH, "Todo", BLUE, BLUEBG, 15),
    box("inp", 430, R1, 180, BH, "In Progress", ORANGE, ORANGEBG, 15),
    box("rev", 430, R2, 180, BH, "In Review", ORANGE, ORANGEBG, 15),
    box("custom", 430, R3, 180, BH, "+ Testing …\n(เพิ่มเองได้)", MUTED, "#ffffff", 12, dashed=True),
    box("done", 720, R2, 170, BH, "Done", GREEN, GREENBG, 15),
    box("anysrc", 1010, R1, 150, BH, "จาก state ใดก็ได้", MUTED, "#ffffff", 13, dashed=True),
    box("can", 1010, R2, 150, BH, "Cancelled", RED, REDBG, 15),
    # callouts on the completed group
    # co1 is narrowed from the left + lifted so the dashed reopen arrow (Done → In Progress, auto-routed
    # centre-to-centre) passes below its bottom-left corner instead of cutting through it
    box("co1", 710, R1 - 10, 245, 62, "เข้า group นี้\n→ ตั้ง completed_at\n(ใช้คำนวณ burndown)", GREEN, "#ffffff", 13, dashed=True),
    box("co2", 655, R3, 300, 62, "ออกจาก completed →\ncompleted_at กลับเป็นค่าว่าง\n(ไม่นับว่าเสร็จอีก)", GREEN, "#ffffff", 13, dashed=True),
    # typical transitions
    arrow("bl", "todo", BLUE),
    arrow("todo", "inp", ORANGE),
    dict(arrow("inp", "rev", ORANGE), startArrowhead="arrow"),
    arrow("rev", "done", GREEN),
    arrow("done", "inp", ORANGE, dashed=True),
    arrow("anysrc", "can", RED, dashed=True),
    # arrow labels (14px: the .fig is scaled to ~0.7x on the slide, 12px became unreadable)
    note(538, 226, "ส่ง review\nส่งกลับแก้", 14, ORANGE),
    txt(620, 261, "ผ่าน review", 14, GREEN),
    txt(653, 207, "reopen", 14, ORANGE),   # in the pocket left of co1, just above the dashed arrow
    # bottom: policies + comparison + CE note
    box("pol", 30, 430, 590, 100,
        "Policies = ข้อตกลงของทีม (Plane ไม่บังคับ → เขียนไว้ใน Page)\n"
        "• เข้า In Review ต้องมี PR link\n"
        "• เข้า Done ต้องผ่าน acceptance criteria ครบทุกข้อ\n"
        "• WIP ใน In Progress ≤ 3 ใบ/คน", PURPLE, PURPLEBG, 14),
    box("cmp", 645, 430, 535, 100,
        "เทียบกับ Jira\nJira: ตั้ง transition + condition / validator ได้\n"
        "Plane: มีแค่ state + group → เรียบง่าย แต่ทีมต้องมีวินัย", TEAL, TEALBG, 14),
    box("ce", 30, 548, 1150, 48,
        "Plane CE: ลากไป state ใดก็ได้ — ไม่มี transition rule / WIP limit → ทีมเขียน policy เอง", RED, REDBG, 15),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
