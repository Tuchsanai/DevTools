#!/usr/bin/env python3
"""d26 — Agile iteration loop: 6-node cycle, increments stacking up, Waterfall-vs-Agile feedback inset."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *  # noqa: E402,F401


def free_arrow(x, y, dx, dy, color, width=3):
    """Arrow that is not attached to any element (explicit points)."""
    return {"type": "arrow", "x": x, "y": y, "width": abs(dx), "height": abs(dy), "points": [[0, 0], [dx, dy]],
            "strokeColor": color, "strokeWidth": width, "roughness": 0}


# ---- loop geometry: 6 nodes on an ellipse around (CX, CY)
CX, CY, RX, RY = 345, 300, 235, 158
W, H = 180, 56
DX, DY = 210, 80          # horizontal / vertical offset of the four diagonal nodes
nodes = [  # (id, centre, text, stroke, bg)
    ("n1", (CX - DX, CY - DY), "Backlog\n(จัดลำดับ)", BLUE, BLUEBG),
    ("n2", (CX, CY - RY), "วางแผนรอบ\n(plan)", PURPLE, PURPLEBG),
    ("n3", (CX + DX, CY - DY), "สร้าง\n(build)", ORANGE, ORANGEBG),
    ("n4", (CX + DX, CY + DY), "ทดสอบ\n(test)", ORANGE, ORANGEBG),
    ("n5", (CX, CY + RY), "review + feedback\n(ทบทวน)", GREEN, GREENBG),
    ("n6", (CX - DX, CY + DY), "ปรับ backlog\n(adapt)", BLUE, BLUEBG),
]

els = [title("Agile iteration : วนรอบสั้น ๆ ได้ของที่ใช้ได้จริง + feedback ทุกรอบ")]

# ---- left zone: the loop
els += [zone(30, 70, 625, 440, BLUE, SKYBG),
        txt(50, 80, "วงจร 1 iteration = 6 ขั้น วนซ้ำไปเรื่อย ๆ", 18, BLUE)]
for nid, (cx, cy), text, c, bg in nodes:
    w = 220 if nid == "n5" else W          # bottom node carries the longest label
    els.append(box(nid, cx - w // 2, cy - H // 2, w, H, text, c, bg, 15))
for a, b in [("n1", "n2"), ("n2", "n3"), ("n3", "n4"), ("n4", "n5"), ("n5", "n6")]:
    els.append(arrow(a, b, BLUE))
els.append(arrow("n6", "n1", ORANGE))
els.append(txt(150, 292, "รอบถัดไป", 13, ORANGE))
els.append(txt(290, 278, "1 รอบ =\n1–4 สัปดาห์", 17, MUTED))

# ---- right zone: increments stacking up
els += [zone(680, 70, 500, 440, GREEN, GREENBG),
        txt(700, 80, "Increment สะสมทุกรอบ — ใช้งานได้จริงทุกรอบ", 18, GREEN),
        zone(755, 118, 405, 245, GREEN, "#ffffff", id="stk"),
        box("inc4", 770, 128, 375, 48, "Increment 4 …  (รอบถัดไป)", MUTED, GREYBG, 14, dashed=True),
        box("inc3", 770, 186, 375, 48, "Increment 3 = A + B + C   (รอบ 3)", GREEN, GREENBG, 14),
        box("inc2", 770, 244, 375, 48, "Increment 2 = A + B   (รอบ 2)", GREEN, GREENBG, 14),
        box("inc1", 770, 302, 375, 48, "Increment 1 = ฟีเจอร์ A   (รอบ 1)", GREEN, GREENBG, 14),
        box("usr", 770, 400, 375, 60, "ผู้ใช้ / ลูกค้า ทดลองใช้ของจริง\nแล้วให้ feedback", ORANGE, ORANGEBG, 14),
        arrow("stk", "usr", GREEN),
        arrow("n4", "stk", GREEN),
        txt(684, 348, "ส่งมอบ\nincrement", 13, GREEN),
        arrow("usr", "n5", ORANGE, dashed=True),
        txt(560, 418, "feedback", 13, ORANGE),
        txt(700, 474, "ทุก increment ต้องใช้งานได้จริง (potentially shippable) ไม่ใช่แค่เอกสาร", 13, MUTED)]

# ---- bottom inset: one long Waterfall pass vs three short Agile loops
els += [zone(30, 522, 1150, 96, MUTED, GREYBG),
        txt(50, 530, "Waterfall : ทำยาวรวดเดียว — feedback ครั้งเดียวตอนจบ (หลายเดือน)", 15, RED),
        txt(60, 555, "requirements  →  design  →  build  →  test", 12, MUTED),
        free_arrow(55, 592, 400, 0, RED, 3),
        box("wfb", 465, 574, 100, 36, "feedback", RED, REDBG, 13),
        txt(600, 530, "Agile : รอบสั้น — feedback ทุก 1–4 สัปดาห์", 15, GREEN)]
for k in range(3):
    x0 = 600 + k * 190
    els.append(txt(x0 + 18, 555, f"รอบ {k + 1}", 12, MUTED))
    els.append(free_arrow(x0, 592, 72, 0, GREEN, 3))
    els.append(box(f"fb{k + 1}", x0 + 80, 574, 100, 36, "feedback", ORANGE, ORANGEBG, 12))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d26-agile-iteration.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(f"wrote {out} ({len(els)} elements)")
