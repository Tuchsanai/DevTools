#!/usr/bin/env python3
"""d42 — Product Backlog → Sprint Backlog → Increment : the 3 Scrum artifacts, their commitments, and the Plane mapping.

Box labels are drawn by the canvas at 20 px (≈10 px per character, 25 px per line, wrap width = box width − 20),
so every box below is sized for its exact number of lines.
Small grey notes are 14 px (same as d37/d41) and are placed at column x + 15 like the header lines; keep every
text inside its column and the title under ~1100 px wide so the exported canvas stays 1170 px like the other diagrams."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

# three tall columns left → right (gap 105 px for the arrow labels)
C1, W1 = 30, 310      # Product Backlog   (label width 290)
C2, W2 = 455, 300     # Sprint Backlog    (label width 280)
C3, W3 = 860, 320     # Increment         (label width 300)
ZY, ZH = 64, 488      # zone top / height  → bottom 552
CY, CH = 484, 60      # commitment box (2 lines), aligned in all 3 columns
PY, PH = 560, 60      # grey Plane mapping box (2 lines) → bottom 620
L1, L2, L3, L4 = 35, 60, 85, 110   # box heights for 1–4 lines of label

els = [
    title("3 artifacts ของ Scrum : Product Backlog → Sprint Backlog → Increment + commitment"),

    # ================= column 1 : Product Backlog
    zone(C1, ZY, W1, ZH, BLUE, SKYBG, id="pb"),
    txt(C1 + 15, 72, "Product Backlog", 18, BLUE),
    txt(C1 + 15, 98, "งานทั้งหมด · เรียงลำดับโดย PO (ผู้ดูแลคนเดียว)", 13, MUTED),
]

# 8 ordered rows: top = refined + ready (selected 1–4), bottom = still rough
pb_rows = [
    ("1 · ล็อกอินด้วยอีเมล · 5 pts\nAC ครบ · พร้อมทำ", L2, BLUE, BLUEBG),
    ("2 · รีเซ็ตรหัสผ่าน · 3 pts", L1, BLUE, BLUEBG),
    ("3 · ค้นหาเมนูอาหาร · 8 pts", L1, BLUE, BLUEBG),
    ("4 · ตะกร้าสั่งซื้อ · 3 pts", L1, BLUE, BLUEBG),
    ("5 · จ่ายเงิน · 13 pts?", L1, MUTED, "#ffffff"),
    ("6 · รีวิวร้าน", L1, MUTED, "#ffffff"),
    ("7 · คูปองส่วนลด", L1, MUTED, "#ffffff"),
    ("8 · แชร์ไปโซเชียล …", L1, MUTED, "#ffffff"),
]
y = 122
for i, (t, h, c, bg) in enumerate(pb_rows):
    els.append(box(f"r{i+1}", C1 + 20, y, W1 - 40, h, t, c, bg, 14))
    y += h + 4
els += [
    txt(C1 + 15, y + 2, "บน = ละเอียด พร้อมเข้า Sprint · ล่าง = ยังหยาบ", 14, MUTED),
    box("cm1", C1 + 20, CY, W1 - 40, CH, "commitment: Product Goal\n“สั่งอาหารในแคมปัสได้”", BLUE, "#ffffff", 14, dashed=True),
    box("pl1", C1, PY, W1, PH, "Plane: work items ของโปรเจกต์\n(state group backlog)", MUTED, GREYBG, 14),

    # ================= column 2 : Sprint Backlog
    zone(C2, ZY, W2, ZH, ORANGE, "#fff4e6", id="sb"),
    txt(C2 + 15, 72, "Sprint Backlog", 18, ORANGE),
    txt(C2 + 15, 98, "งานที่เลือก + แผนการทำ · เจ้าของ = Developers", 13, MUTED),
]

# 4 selected items, each with sub-tasks = the Developers' plan
sb_rows = [
    ("1 · ล็อกอินด้วยอีเมล · 5 pts", ["API login", "UI + test"]),
    ("2 · รีเซ็ตรหัสผ่าน · 3 pts", ["อีเมล token", "UI + test"]),
    ("3 · ค้นหาเมนูอาหาร · 8 pts", ["index DB", "API + UI"]),
    ("4 · ตะกร้าสั่งซื้อ · 3 pts", ["API /cart", "UI ตะกร้า"]),
]
y = 122
for i, (t, subs) in enumerate(sb_rows):
    els.append(box(f"s{i+1}", C2 + 20, y, W2 - 40, L1, t, ORANGE, ORANGEBG, 14))
    for j, st in enumerate(subs):
        els.append(box(f"s{i+1}{j+1}", C2 + 28 + j * 138, y + L1 + 4, 134, L1, st, ORANGE, "#ffffff", 14))
    y += 2 * L1 + 4 + 6      # gap 6 between groups leaves room for the 2-line 14 px note above the commitment box
els += [
    txt(C2 + 15, y + 1, "Σ 19 pts  ≤  velocity ≈ 20 pts\nปรับ sub-tasks ได้ทุกวัน (Daily Scrum)", 14, MUTED),
    box("cm2", C2 + 20, CY, W2 - 40, CH, "commitment: Sprint Goal\n“ล็อกอินและหาเมนูได้”", ORANGE, "#ffffff", 14, dashed=True),
    box("pl2", C2, PY, W2, PH, "Plane: work items ใน Cycle\n(Add existing work items)", MUTED, GREYBG, 14),

    # ================= column 3 : Increment
    zone(C3, ZY, W3, ZH, GREEN, GREENBG, id="inc"),
    txt(C3 + 15, 72, "Increment", 18, GREEN),
    txt(C3 + 15, 98, "งานที่ Done สะสมทุก Sprint · ใช้งานได้จริง", 13, MUTED),
    box("i0", C3 + 20, 122, W3 - 40, L3, "จาก Sprint 1 (ก่อนหน้า)\n✓ สมัครสมาชิก\n✓ หน้าแรก + รายชื่อร้าน", GREEN, "#ffffff", 14),
    box("i1", C3 + 20, 215, W3 - 40, L4, "+ Sprint 2 (ผ่าน DoD แล้ว)\n✓ 1 ล็อกอินด้วยอีเมล\n✓ 2 รีเซ็ตรหัสผ่าน\n✓ 3 ค้นหาเมนูอาหาร", GREEN, GREENBG, 14),
    box("nd", C3 + 20, 333, W3 - 40, L3, "4 · ตะกร้า ยังไม่ผ่าน DoD\n→ ไม่นับใน Increment\n→ กลับไป Product Backlog", RED, REDBG, 14, dashed=True),
    txt(C3 + 15, 432, "Increment = ของที่ release ได้ทันที\nไม่ใช่ “เกือบเสร็จ”", 14, MUTED),
    box("cm3", C3 + 20, CY, W3 - 40, CH, "commitment:\nDefinition of Done", GREEN, "#ffffff", 14, dashed=True),
    box("pl3", C3, PY, W3, PH, "Plane: state group\ncompleted · Progress panel", MUTED, GREYBG, 14),

    # ================= arrows between the three artifacts
    arrow("pb", "sb", BLUE, x=C1 + W1, y=300, w=C2 - (C1 + W1), h=0),
    txt(C1 + W1 + 6, 244, "Sprint Planning\nเลือก 1–4\n(≤ velocity)", 13, BLUE),
    arrow("sb", "inc", ORANGE, x=C2 + W2, y=300, w=C3 - (C2 + W2), h=0),
    txt(C2 + W2 + 6, 244, "ทำจน Done\n(ผ่าน DoD)\nตลอด Sprint", 13, ORANGE),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d42-product-vs-sprint-backlog.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
