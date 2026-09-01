#!/usr/bin/env python3
"""d27-scrum-workflow — Scrum framework flow (artifacts · events · accountabilities) with Plane names."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

els = [
    title("Scrum framework : 3 artifacts · 5 events · 3 accountabilities ในหนึ่งรอบ Sprint"),

    # ---- row A : Product Backlog → Sprint Planning → Sprint Backlog
    box("pb", 70, 85, 220, 80, "Product Backlog\n+ Product Goal", BLUE, BLUEBG, 16),
    box("sp", 340, 85, 220, 80, "Sprint Planning\nทำไม · ทำอะไร · ทำอย่างไร", PURPLE, PURPLEBG, 14),
    box("sb", 625, 85, 220, 80, "Sprint Backlog\n+ Sprint Goal", ORANGE, ORANGEBG, 16),
    arrow("pb", "sp", BLUE, x=295, y=125, w=45, h=0),
    arrow("sp", "sb", PURPLE, x=565, y=125, w=60, h=0),
    txt(75, 170, "Plane: work items ของโปรเจกต์", 13, MUTED),
    txt(755, 172, "Plane: work items ใน Cycle", 13, MUTED),
    box("po", 70, 194, 220, 48, "Product Owner\nจัดลำดับ backlog", RED, REDBG, 14),
    box("sm", 340, 194, 220, 48, "Scrum Master\nโค้ชทีม · ขจัดอุปสรรค", TEAL, TEALBG, 14),
    txt(885, 96, "ม่วง + กรอบส้ม = 5 events\nฟ้า · ส้ม · เขียว = 3 artifacts\nป้าย PO · SM · Dev = 3 accountabilities", 13, MUTED),
    arrow("sb", "sprint", ORANGE, x=735, y=170, w=0, h=80),

    # ---- row B : the Sprint (timebox) with the Daily Scrum loop
    zone(300, 255, 870, 175, ORANGE, "#fff4e6", id="sprint"),
    txt(315, 263, "Sprint  1–4 สัปดาห์ · timebox คงที่ ไม่ขยายเวลา", 17, ORANGE),
    txt(1075, 267, "Plane: Cycle", 13, MUTED),
    box("ds", 320, 300, 270, 70, "Daily Scrum · 15 นาที ทุกวัน\nตรวจความคืบหน้า · ปรับแผน", PURPLE, PURPLEBG, 14),
    box("wk", 640, 300, 290, 70, "ทำงานตาม Sprint Backlog\nปิดงานทีละใบให้ผ่าน DoD", ORANGE, "#ffffff", 14),
    arrow("ds", "wk", PURPLE, x=595, y=335, w=45, h=0),
    {"type": "arrow", "x": 785, "y": 378, "width": 330, "height": 24,
     "points": [[0, 0], [0, 24], [-330, 24], [-330, 2]],
     "strokeColor": PURPLE, "strokeWidth": 2, "roughness": 0},
    txt(560, 406, "วันถัดไป · ทำซ้ำทุกวันจนจบ Sprint", 13, PURPLE),
    box("dev", 965, 300, 190, 70, "Developers\nวางแผนวิธีทำเอง\nส่ง Increment", GREEN, GREENBG, 14),

    # ---- row C : Increment → Sprint Review → Sprint Retrospective (+ Definition of Done)
    arrow("sprint", "inc", ORANGE, x=735, y=435, w=0, h=45),
    box("inc", 645, 480, 180, 80, "Increment\nงานที่ Done แล้ว\nใช้ได้จริง", GREEN, GREENBG, 15),
    box("dod", 880, 480, 290, 80, "Definition of Done\nเกณฑ์คุณภาพที่งานต้องผ่าน\nจึงนับเป็น Increment", MUTED, GREYBG, 13, dashed=True),
    arrow("dod", "inc", MUTED, dashed=True, x=875, y=520, w=-50, h=0),
    box("rev", 320, 480, 280, 80, "Sprint Review\nstakeholders ดู Increment\nแล้วให้ feedback", PURPLE, PURPLEBG, 13),
    box("retro", 70, 480, 220, 80, "Sprint Retrospective\nทีมปรับวิธีทำงาน\nรอบหน้าดีกว่าเดิม", PURPLE, PURPLEBG, 13),
    arrow("inc", "rev", GREEN, x=640, y=520, w=-40, h=0),
    arrow("rev", "retro", PURPLE, x=315, y=520, w=-25, h=0),
    txt(630, 565, "Plane: state group completed", 13, MUTED),
    txt(885, 565, "Plane: Page", 13, MUTED),
    txt(75, 565, "Plane: Page (บันทึก retro)", 13, MUTED),

    # ---- loop back : Retrospective → next Sprint → Product Backlog
    {"type": "arrow", "x": 65, "y": 520, "width": 27, "height": 395,
     "points": [[0, 0], [-27, 0], [-27, -395], [0, -395]],
     "strokeColor": PURPLE, "strokeWidth": 2, "roughness": 0},
    txt(48, 320, "Sprint\nถัดไป", 13, PURPLE),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d27-scrum-workflow.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
