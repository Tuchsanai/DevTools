#!/usr/bin/env python3
"""d41-backlog-refinement : refinement funnel (wide raw ideas at the bottom → narrow "Ready" at the top),
DEEP properties, Definition of Ready checklist and the "continuous activity, not an event" note."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d41-backlog-refinement"


# ---- helpers local to this scene -------------------------------------------------------------------
def est_w(s, fs):
    """Rough helvetica width of one line (Thai combining marks take no width)."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o == 0x0E31 or 0x0E34 <= o <= 0x0E3A or 0x0E47 <= o <= 0x0E4E:
            continue
        if 0x0E00 <= o <= 0x0E7F:
            w += 0.55
        elif ch == " ":
            w += 0.28
        elif ch in "·:()—-,.\"'/":
            w += 0.33
        elif ch.isupper():
            w += 0.68
        elif ch.isdigit():
            w += 0.56
        else:
            w += 0.5
    return w * fs


def ctxt(cx, y, text, fs, color=INK):
    """Text horizontally centred on cx (lines centred relative to each other)."""
    longest = max(text.split("\n"), key=lambda l: est_w(l, fs))
    return txt(cx - est_w(longest, fs) / 2, y, text, fs, color)


def note(x, y, text, fs=13, color=MUTED):
    """Left-aligned multi-line text."""
    t = txt(x, y, text, fs, color)
    t["textAlign"] = "left"
    return t


def trap(x, y, w, h, top_inset, stroke, bg):
    """Closed trapezoid (narrow top, wide bottom) as a filled line polygon; bbox = (x, y, w, h)."""
    pts = [[top_inset, 0], [w - top_inset, 0], [w, h], [0, h], [top_inset, 0]]
    return {"type": "line", "x": x, "y": y, "width": w, "height": h, "points": pts,
            "strokeColor": stroke, "backgroundColor": bg, "fillStyle": "solid",
            "strokeWidth": 2, "roughness": 0}


def anchor(id, x, y, w, h):
    """Invisible rectangle over a polygon's bbox so arrows can bind to it (arrows cannot bind to lines)."""
    return {"id": id, "type": "rectangle", "x": x, "y": y, "width": w, "height": h, "opacity": 0,
            "strokeColor": "transparent", "backgroundColor": "transparent", "strokeWidth": 1, "roughness": 0}


# ---- funnel geometry (centre x = 400) --------------------------------------------------------------
CX = 400
# sides: half-width 150 at y=142 → 340 at y=476   (slope 190/334)
els = [
    title("Backlog refinement : กลั่นไอเดียดิบให้เล็ก ชัด และประเมินแล้ว ก่อนเข้า Sprint Planning"),

    # Sprint Planning at the spout (top)
    box("sp", 210, 64, 380, 40, "Sprint Planning : หยิบเฉพาะใบ Ready", ORANGE, ORANGEBG, 14),

    # layer 3 (top, narrow) — Ready
    trap(202, 142, 396, 84, 48, GREEN, GREENBG),
    anchor("l3", 202, 142, 396, 84),
    ctxt(CX, 150, "Ready : เล็ก · ชัด · ประเมินแล้ว", 17, GREEN),
    ctxt(CX, 178, "ผ่าน Definition of Ready แล้ว\nพร้อมหยิบเข้า Sprint Planning ทันที", 14, INK),

    # layer 2 (middle) — refine
    trap(132, 266, 536, 84, 48, ORANGE, ORANGEBG),
    anchor("l2", 132, 266, 536, 84),
    ctxt(CX, 274, "Refine : แตกย่อย · ทำให้ชัด · ประเมิน", 17, ORANGE),
    ctxt(CX, 302, "แตก epic เป็น user story ที่ทำจบใน 1 sprint\nเขียน acceptance criteria · ประเมิน story point", 14, INK),

    # layer 1 (bottom, wide) — raw ideas
    trap(60, 390, 680, 86, 49, MUTED, GREYBG),
    anchor("l1", 60, 390, 680, 86),
    ctxt(CX, 398, "ไอเดียดิบ : ใหญ่ · คลุมเครือ (Epic / theme)", 17, MUTED),
    ctxt(CX, 426, "คำขอลูกค้า · bug report · ไอเดียทีม · \"อยากได้ระบบรายงาน\"\nยังไม่ต้องละเอียด — ใส่รายละเอียดเมื่อใกล้ถึงคิว", 14, INK),

    # upward flow
    arrow("l1", "l2", MUTED, x=CX, y=382, w=0, h=-24),
    arrow("l2", "l3", ORANGE, x=CX, y=258, w=0, h=-24),
    arrow("l3", "sp", GREEN, x=CX, y=134, w=0, h=-22),
    txt(415, 360, "หยิบใบบนสุดมาดูก่อน (prioritised)", 13, MUTED),
    txt(415, 236, "กลั่นทีละน้อย ทุกสัปดาห์", 13, MUTED),
    txt(415, 112, "ผ่าน DoR ✓", 13, GREEN),

    # ---- clock note under the funnel
    zone(60, 494, 680, 108, TEAL, TEALBG),
    {"type": "ellipse", "x": 80, "y": 520, "width": 56, "height": 56, "strokeColor": TEAL,
     "backgroundColor": "#ffffff", "fillStyle": "solid", "strokeWidth": 3, "roughness": 0},
    line(108, 548, [[0, 0], [0, -20]], TEAL, 3),
    line(108, 548, [[0, 0], [15, 0]], TEAL, 3),
    txt(156, 506, "กิจกรรมต่อเนื่อง ไม่ใช่อีเวนต์", 19, TEAL),
    note(156, 538, "Scrum Guide ไม่กำหนดเป็นพิธีการ — ทีมทำทีละน้อยทุกสัปดาห์ (~10% ของเวลาทีม)\n"
                   "ใน Plane : เขียน AC ในใบงาน · แตก sub-work items · ใส่ estimate · แก้ blocker", 14, INK),

    # ---- right column : DEEP
    zone(775, 66, 405, 270, PURPLE, PURPLEBG),
    txt(790, 76, "DEEP : คุณสมบัติของ backlog ที่ดี", 18, PURPLE),
    box("dp1", 790, 108, 375, 50, "D — Detailed appropriately\nใบบนสุดละเอียด ใบล่าง ๆ หยาบได้", PURPLE, "#ffffff", 13),
    box("dp2", 790, 166, 375, 50, "E — Estimated\nใบใกล้คิวมี story point แล้ว", PURPLE, "#ffffff", 13),
    box("dp3", 790, 224, 375, 50, "E — Emergent\nเพิ่ม / ลด / แก้ได้เมื่อรู้มากขึ้น", PURPLE, "#ffffff", 13),
    box("dp4", 790, 282, 375, 50, "P — Prioritised\nเรียงตามคุณค่า · ใบบนสุด = ทำก่อน", PURPLE, "#ffffff", 13),

    # ---- right column : Definition of Ready
    zone(775, 352, 405, 250, GREEN, GREENBG, id="dor"),
    txt(790, 362, "Definition of Ready — เช็กก่อนเข้า Sprint", 18, GREEN),
    box("dr1", 790, 394, 375, 38, "✓ INVEST ผ่าน (เล็ก · ทดสอบได้)", GREEN, "#ffffff", 13),
    box("dr2", 790, 440, 375, 38, "✓ AC ตรวจได้ (ผ่าน / ไม่ผ่าน ชัด)", GREEN, "#ffffff", 13),
    box("dr3", 790, 486, 375, 38, "✓ ประเมินแล้ว · ≤ 8 pt", GREEN, "#ffffff", 13),
    box("dr4", 790, 532, 375, 38, "✓ ไม่มี blocker / dependency ค้าง", GREEN, "#ffffff", 13),
    txt(790, 578, "ไม่ผ่านข้อใด → กลับไป refine ต่อ ไม่หยิบเข้า sprint", 12, MUTED),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
