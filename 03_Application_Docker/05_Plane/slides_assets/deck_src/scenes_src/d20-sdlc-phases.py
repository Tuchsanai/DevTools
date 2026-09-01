#!/usr/bin/env python3
"""d20-sdlc-phases : SDLC loop (Requirements → … → Maintenance) with feedback arrows back to Requirements."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

PINK, PINKBG = "#a61e4d", "#ffdeeb"
W, H = 310, 100
TOP, BOT = 90, 360
XS = [50, 435, 820]

# (id, x, y, phase name, thai activity line, artifact line, colour, bg)
phases = [
    ("req", XS[0], TOP, "1  Requirements  ความต้องการ", "คุยกับผู้ใช้ · เขียนสิ่งที่ระบบต้องทำ", "user story · product backlog", BLUE, BLUEBG),
    ("des", XS[1], TOP, "2  Design  ออกแบบ", "ออกแบบข้อมูล หน้าจอ สถาปัตยกรรม", "ERD · wireframe · API spec", PURPLE, PURPLEBG),
    ("imp", XS[2], TOP, "3  Implementation  พัฒนา", "เขียนโค้ด · review กันในทีม", "code · commit · pull request", ORANGE, ORANGEBG),
    ("tst", XS[2], BOT, "4  Testing  ทดสอบ", "ตรวจว่าตรง acceptance criteria", "unit · integration · e2e test", TEAL, TEALBG),
    ("dep", XS[1], BOT, "5  Deployment  ส่งมอบ", "build image · ปล่อยให้ผู้ใช้จริง", "image · release · changelog", GREEN, GREENBG),
    ("mnt", XS[0], BOT, "6  Maintenance  บำรุงรักษา", "เฝ้าดูระบบ · แก้ bug · ปรับปรุง", "monitor · fix · new request", PINK, PINKBG),
]

els = [title("SDLC : วงจรชีวิตการพัฒนาซอฟต์แวร์ 6 ขั้น — วนซ้ำจนกว่าระบบจะเลิกใช้")]
for pid, x, y, name, act, art, c, bg in phases:
    els.append(box(pid, x, y, W, H, "", c, bg, 16))
    els.append(txt(x + 14, y + 10, name, 19, c))
    els.append(txt(x + 14, y + 42, act, 14, INK))
    els.append(txt(x + 14, y + 66, art, 14, MUTED))

# main cycle (clockwise)
els += [
    arrow("req", "des", MUTED, x=365, y=140, w=65, h=0),
    arrow("des", "imp", MUTED, x=750, y=140, w=65, h=0),
    arrow("imp", "tst", MUTED, x=975, y=195, w=0, h=160),
    arrow("tst", "dep", MUTED, x=815, y=410, w=-65, h=0),
    arrow("dep", "mnt", MUTED, x=430, y=410, w=-65, h=0),
    arrow("mnt", "req", BLUE, x=205, y=355, w=0, h=-160),
    txt(215, 262, "รอบถัดไป\nความต้องการใหม่", 14, BLUE),
    # feedback arrows back to Requirements
    arrow("tst", "req", RED, dashed=True, x=900, y=355, w=-600, h=-160),
    txt(640, 250, "พบ bug / เข้าใจโจทย์ผิด → ทบทวนความต้องการ", 14, RED),
    arrow("dep", "req", RED, dashed=True, x=520, y=355, w=-230, h=-160),
    txt(256, 332, "feedback จากผู้ใช้จริง", 14, RED),
]

# footnote strip
els += [
    txt(50, 478, "เดินวงจรแบบไหน = โมเดลไหน", 15, MUTED),
    box("wf", 50, 502, 520, 56, "ผ่านครั้งเดียว ตั้งแต่ต้นจนจบ  =  Waterfall", RED, REDBG, 16),
    box("ag", 600, 502, 530, 56, "ผ่านรอบสั้น ๆ ซ้ำหลายรอบ  =  Iterative / Agile", GREEN, GREENBG, 16),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d20-sdlc-phases.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
