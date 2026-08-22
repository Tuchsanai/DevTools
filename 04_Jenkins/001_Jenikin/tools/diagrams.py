#!/usr/bin/env python3
"""Generate the slide-deck diagram set from one shared visual kit.

Every diagram in the deck is emitted from the primitives below, so stroke
widths, corner radii, role colours, arrow heads, type scale and spacing are
identical across the whole lesson.  Run this script to rewrite
``slides_assets/d*.svg``; ``tools/embed_assets.py`` then inlines them.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "slides_assets"

FONT = '"Leelawadee UI","Noto Sans Thai","Segoe UI",sans-serif'
MONO = '"Cascadia Code",Consolas,monospace'

# fill, stroke, title colour
ROLES: dict[str, tuple[str, str, str]] = {
    "src": ("#eaf4ff", "#4b95cc", "#12547f"),
    "jk": ("#dff1f5", "#147d92", "#0b5a6b"),
    "ci": ("#e6fbf4", "#169b72", "#07795a"),
    "cd": ("#fff5d9", "#d99013", "#95600b"),
    "ext": ("#eef3f6", "#7d97a3", "#3d5865"),
    "warn": ("#ffece9", "#cf4b45", "#a2312c"),
    "plain": ("#ffffff", "#bcd5de", "#173d52"),
}

ARROW = "#6f97a6"
MUTED = "#57737f"
INK = "#173d52"
CANVAS = "#f7fbfd"
EDGE = "#dcebf0"

R_NODE = 18
SW_NODE = 3
SW_ARROW = 3.5


def esc(value: str) -> str:
    return escape(str(value))


# ----------------------------------------------------------------- primitives


# The whole deck inlines every diagram into ONE html document, so element ids
# must be unique per diagram.  Sharing id="ah" made all 31 marker-end
# references resolve to d1's marker, which lives in a display:none slot on
# every page except d1's — that is why arrow heads vanished everywhere else.
_KEY = "d0"


def marker_id(name: str) -> str:
    return f"{name}-{_KEY}"


def head(key: str, width: int, height: int, title: str, desc: str) -> list[str]:
    global _KEY
    _KEY = key
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-labelledby="dt-{key} dd-{key}">',
        f'<title id="dt-{key}">{esc(title)}</title>'
        f'<desc id="dd-{key}">{esc(desc)}</desc>',
        "<defs>"
        + "".join(
            f'<marker id="{mid}-{key}" markerUnits="userSpaceOnUse" markerWidth="15" markerHeight="12" '
            f'refX="13.5" refY="6" orient="auto">'
            f'<path d="M0 0.5L15 6L0 11.5z" fill="{colour}"/></marker>'
            for mid, colour in (
                ("ah", ARROW),
                ("ahw", "#d99013"),
                ("ahr", "#cf4b45"),
                ("ahg", "#169b72"),
                ("ahb", "#4b95cc"),
            )
        )
        + "</defs>",
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="26" '
        f'fill="{CANVAS}" stroke="{EDGE}" stroke-width="2"/>',
        f'<g font-family={FONT!r}>'.replace("'", '"'),
    ]


def tail() -> list[str]:
    return ["</g>", "</svg>"]


def txt(x, y, s, size=18, fill=INK, weight=400, anchor="middle", mono=False, opacity=None):
    extra = f' font-family="{MONO}"' if mono else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}"{extra}{op}>{esc(s)}</text>'
    )


def fit(text: str, size: float, avail: float, factor: float, floor: float) -> float:
    """Shrink a font size until the string is expected to fit the given width."""
    est = len(text) * size * factor
    if est <= avail:
        return round(size, 1)
    return round(max(floor, size * avail / est), 1)


def node(x, y, w, h, role, title, sub=None, sub2=None, size=23, subsize=16, mono_sub=False):
    """A standard rounded node: one bold title, up to two muted sub-lines."""
    fill, stroke, ink = ROLES[role]
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{R_NODE}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{SW_NODE}"/>'
    ]
    cx = x + w / 2
    avail = w - 24
    lines = [t for t in (sub, sub2) if t]
    size = fit(title, size, avail, 0.62, 14)
    subsize = min(subsize, min((fit(t, subsize, avail, 0.58, 11) for t in lines), default=subsize))
    if not lines:
        base = y + h / 2 + size * 0.35
    else:
        block = size + len(lines) * (subsize + 6)
        base = y + (h - block) / 2 + size * 0.82
    parts.append(txt(cx, round(base, 1), title, size=size, fill=ink, weight=700))
    for i, line in enumerate(lines):
        parts.append(
            txt(
                cx,
                round(base + size * 0.32 + (i + 1) * (subsize + 6), 1),
                line,
                size=subsize,
                fill=MUTED,
                mono=mono_sub,
            )
        )
    return parts


def badge(cx, cy, label, fill="#10364a"):
    return [
        f'<circle cx="{cx}" cy="{cy}" r="15" fill="{fill}"/>',
        txt(cx, cy + 5.6, label, size=16, fill="#ffffff", weight=800),
    ]


def chevron(x, cy, colour=ARROW, w=14, h=17):
    """A standalone arrow head — used where the gap is too small for a shaft."""
    return [
        f'<path d="M{x} {cy - h / 2}L{x + w} {cy}L{x} {cy + h / 2}z" fill="{colour}"/>'
    ]


def arrow(x1, y1, x2, y2, colour=ARROW, marker="ah", dash=None, width=SW_ARROW):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return [
        f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{colour}" '
        f'stroke-width="{width}" stroke-linecap="round"{d} marker-end="url(#{marker_id(marker)})"/>'
    ]


def curve(path, colour=ARROW, marker="ah", dash=None, width=SW_ARROW):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return [
        f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="{width}" '
        f'stroke-linecap="round"{d} marker-end="url(#{marker_id(marker)})"/>'
    ]


def band(x, y, w, h, label, stroke, label_fill=None, dash="9 7", label_at="left", label_pos="top"):
    """Dashed zone with a solid pill label sitting on its top or bottom edge."""
    label_fill = label_fill or stroke
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="none" '
        f'stroke="{stroke}" stroke-width="2.5" stroke-dasharray="{dash}"/>'
    ]
    pw = 15 + len(label) * 9.4
    px = x + 26 if label_at == "left" else x + w - pw - 26 if label_at == "right" else x + w / 2 - pw / 2
    py = y if label_pos == "top" else y + h
    parts += [
        f'<rect x="{round(px, 1)}" y="{py - 15}" width="{round(pw, 1)}" height="30" rx="15" fill="{label_fill}"/>',
        txt(round(px + pw / 2, 1), py + 5.5, label, size=15, fill="#ffffff", weight=800),
    ]
    return parts


def bar(x, y, w, h, label, fill, ink="#ffffff", size=19):
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}"/>',
        txt(x + w / 2, y + h / 2 + size * 0.35, label, size=size, fill=ink, weight=700),
    ]


def footnote(width, y, s, size=19):
    return [txt(width / 2, y, s, size=size, fill=INK, weight=700)]


def row(x0, y, w, h, gap, specs):
    """Lay out equally sized nodes left to right and connect them with arrows."""
    parts: list[str] = []
    xs = []
    for i, spec in enumerate(specs):
        x = x0 + i * (w + gap)
        xs.append(x)
        parts += node(x, y, w, h, *spec)
    for i in range(len(specs) - 1):
        if gap < 34:
            parts += chevron(xs[i] + w + (gap - 14) / 2, y + h / 2)
        else:
            parts += arrow(xs[i] + w + 8, y + h / 2, xs[i + 1] - 6, y + h / 2)
    return parts, xs


def write(name: str, lines: list[str]) -> None:
    path = OUT / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"diagram: {name:<34} {path.stat().st_size:>6} B")


# ------------------------------------------------------------------ diagrams


def d1_cicd_pipeline() -> None:
    """Seven pipeline steps on two roomy rows: every hop is source → shaft → head."""
    W, H = 1200, 512
    s = head(
        "d1",
        W,
        H,
        "สายพาน CI/CD เจ็ดขั้น",
        "Code Commit Trigger Build Test Push Deploy เรียงต่อกัน โดยผลของทุกขั้นย้อนกลับถึงผู้พัฒนา",
    )

    legend = [
        ("#4b95cc", "#eaf4ff", "#12547f", "คนทำเอง"),
        ("#147d92", "#dff1f5", "#0b5a6b", "Jenkins เริ่มทำงาน"),
        ("#169b72", "#e6fbf4", "#07795a", "CI — ยืนยันว่าโค้ดยังใช้ได้"),
        ("#d99013", "#fff5d9", "#95600b", "CD — ส่งของถึงผู้ใช้"),
    ]
    widths = [42 + len(label) * 8.6 for *_, label in legend]
    lx = (W - (sum(widths) + 18 * (len(legend) - 1))) / 2
    for (stroke, fill, ink, label), lw in zip(legend, widths):
        s += [
            f'<rect x="{round(lx, 1)}" y="30" width="{round(lw, 1)}" height="34" rx="17" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
            f'<circle cx="{round(lx + 19, 1)}" cy="47" r="7" fill="{stroke}"/>',
            txt(round(lx + 32, 1), 53, label, size=15, fill=ink, weight=700, anchor="start"),
        ]
        lx += lw + 18

    w, h = 210, 112
    gap = 72
    top_y, bot_y = 106, 302
    top_x0 = (W - (4 * w + 3 * gap)) / 2
    bot_x0 = (W - (3 * w + 2 * gap)) / 2
    top = [
        ("src", "Code", "เขียน / แก้โค้ด"),
        ("src", "Commit", "push ขึ้น Git"),
        ("jk", "Trigger", "webhook หรือ poll"),
        ("ci", "Build", "สร้าง artifact"),
    ]
    bottom = [
        ("ci", "Test", "ต้องผ่านก่อนไปต่อ"),
        ("cd", "Push", "เก็บขึ้น registry"),
        ("cd", "Deploy", "รันของจริง แล้ว verify"),
    ]

    xs_top, xs_bot = [], []
    for i, spec in enumerate(top):
        x = top_x0 + i * (w + gap)
        xs_top.append(x)
        s += node(x, top_y, w, h, *spec)
    for i, spec in enumerate(bottom):
        x = bot_x0 + i * (w + gap)
        xs_bot.append(x)
        s += node(x, bot_y, w, h, *spec)

    for i in range(3):
        s += arrow(xs_top[i] + w + 10, top_y + h / 2, xs_top[i + 1] - 8, top_y + h / 2)
    for i in range(2):
        s += arrow(xs_bot[i] + w + 10, bot_y + h / 2, xs_bot[i + 1] - 8, bot_y + h / 2)

    # 4 → 5 wraps to the next row with a full orthogonal elbow.
    turn = (top_y + h + bot_y) / 2
    s += curve(
        f"M{xs_top[3] + w / 2} {top_y + h + 10}"
        f"L{xs_top[3] + w / 2} {turn}"
        f"L{xs_bot[0] + w / 2} {turn}"
        f"L{xs_bot[0] + w / 2} {bot_y - 8}"
    )

    for i, x in enumerate(xs_top + xs_bot, 1):
        y = top_y if i <= 4 else bot_y
        s += badge(x + 24, y, str(i))

    # Feedback closes the loop from Deploy back to Code, well clear of both rows.
    fb_y = bot_y + h + 42
    s += curve(
        f"M{xs_bot[2] + w / 2} {bot_y + h + 10}"
        f"L{xs_bot[2] + w / 2} {fb_y}"
        f"L{xs_top[0] + w / 2 - 6} {fb_y}"
        f"L{xs_top[0] + w / 2 - 6} {top_y + h + 8}",
        colour="#d99013",
        marker="ahw",
        dash="9 8",
    )
    s += [
        txt(
            W / 2,
            fb_y + 32,
            "Feedback — ผลของทุกขั้นกลับถึงผู้พัฒนาในไม่กี่นาที ไม่ใช่ตอนผู้ใช้เจอปัญหา",
            size=19,
            fill="#95600b",
            weight=700,
        )
    ]
    s += tail()
    write("d1_cicd_pipeline.svg", s)

def d2_jenkins_position() -> None:
    """Hub-and-spoke: people own two steps, Jenkins drives the four that follow."""
    W, H = 1200, 488
    s = head(
        "d2",
        W,
        H,
        "Jenkins อยู่ตรงไหนของกระบวนการ",
        "คนเขียนโค้ดแล้ว push ขึ้น Git จากนั้น Jenkins รับเหตุการณ์และสั่งงาน Test Build Registry Deploy ตามลำดับ",
    )

    s += band(20, 150, 470, 190, "คนทำเอง — สองขั้นนี้เท่านั้น", "#4b95cc")
    s += band(512, 14, 664, 416, "Jenkins ทำให้อัตโนมัติ ทุกครั้งที่ push", "#147d92")

    s += node(44, 188, 186, 114, "src", "Developer", "เขียน / แก้โค้ด")
    s += node(290, 188, 186, 114, "ext", "Git repository", "เก็บ commit และ Jenkinsfile")
    s += arrow(236, 245, 282, 245)
    s += [txt(259, 228, "push", size=14, fill=MUTED, weight=700)]

    jx, jy, jw, jh = 536, 168, 208, 154
    s += node(jx, jy, jw, jh, "jk", "Jenkins", "รับเหตุการณ์", "แล้วสั่งงานตามสูตร")
    s += arrow(482, 245, jx - 8, 245)
    s += [txt(509, 228, "event", size=14, fill=MUTED, weight=700)]

    tasks = [
        ("ci", "Test", "เรียก pytest แล้วอ่านผล"),
        ("ci", "Build", "สั่ง docker build เป็น image"),
        ("cd", "Registry", "docker push ขึ้น Docker Hub"),
        ("cd", "Deploy + Verify", "รัน container แล้ว curl ตรวจ"),
    ]
    tx, tw, th = 824, 336, 82
    for i, spec in enumerate(tasks):
        ty = 44 + i * 98
        s += node(tx, ty, tw, th, *spec, size=21, subsize=15)
        s += arrow(jx + jw + 10, jy + jh / 2, tx - 10, ty + th / 2)
    # Badges go on each node's top-left corner, never on the fan-out arrows:
    # a badge sitting mid-arrow made the near-horizontal hop to Registry unreadable.
    for i in range(len(tasks)):
        s += badge(tx + 26, 44 + i * 98, str(i + 1))

    s += footnote(W, 466, "Jenkins ไม่ได้ลงมือเอง — มันสั่ง Git, test runner และ Docker ให้ทำตามลำดับ 1 → 4 แล้วเก็บผลเป็นหลักฐาน", size=18)
    s += tail()
    write("d2_jenkins_position.svg", s)

def d3_jenkins_architecture() -> None:
    """Three parts, three labelled relationships — nothing else."""
    W, H = 1200, 486
    s = head(
        "d3",
        W,
        H,
        "สามส่วนหลักภายใน Jenkins",
        "Controller คือสมองที่จัดคิว Executor คือแรงงานที่รัน build และ jenkins_home คือความจำที่เก็บทุกอย่างไว้",
    )

    w, h, y = 268, 176, 172
    xs = [45, 466, 887]
    s += node(xs[0], y, w, h, "jk", "Controller", "สมอง", "เก็บ config • จัดคิว")
    s += node(xs[1], y, w, h, "ci", "Executor", "แรงงาน", "รัน build ใน workspace")
    s += node(xs[2], y, w, h, "cd", "jenkins_home", "ความจำ", "users • jobs • history")

    mid = y + h / 2
    s += arrow(xs[0] + w + 10, mid, xs[1] - 8, mid)
    s += [txt((xs[0] + w + xs[1]) / 2, mid - 16, "ส่ง build เข้าคิว", size=16, fill=MUTED, weight=700)]
    s += arrow(xs[1] + w + 10, mid, xs[2] - 8, mid)
    s += [txt((xs[1] + w + xs[2]) / 2, mid - 16, "เขียน log และผล", size=16, fill=MUTED, weight=700)]

    ex, ey, ew, eh = xs[0], 66, w, 54
    s += [
        f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" rx="27" fill="#ffffff" '
        f'stroke="#4b95cc" stroke-width="{SW_NODE}"/>',
        txt(ex + ew / 2, ey + 34, "เหตุการณ์: กดปุ่ม • poll • webhook", size=17, fill="#12547f", weight=700),
    ]
    s += arrow(ex + ew / 2, ey + eh + 8, ex + ew / 2, y - 8)

    back_y = y + h + 62
    s += curve(
        f"M{xs[2] + w / 2} {y + h + 10}"
        f"L{xs[2] + w / 2} {back_y}"
        f"L{xs[0] + w / 2} {back_y}"
        f"L{xs[0] + w / 2} {y + h + 8}",
        dash="9 8",
    )
    s += [txt(W / 2, back_y - 14, "อ่าน config กลับมาเมื่อ Jenkins สตาร์ตใหม่", size=17, fill=MUTED, weight=700)]
    s += footnote(W, 462, "ในแล็บนี้ทั้งสามส่วนอยู่ในคอนเทนเนอร์เดียว — แต่หน้าที่แยกกันชัดเจน")
    s += tail()
    write("d3_jenkins_architecture.svg", s)

def d4_docker_layers() -> None:
    W, H = 1200, 470
    s = head("d4", W, H, "สองชั้นของ Docker ในแล็บ", "เครื่องหลักรัน devtools ซึ่งมี dockerd ของตัวเองและรัน jenkins smee-client และ webapp บนเครือข่าย cicd-net")
    s += [
        f'<rect x="36" y="34" width="1128" height="330" rx="24" fill="#ffffff" stroke="#9fbcc8" stroke-width="3"/>',
        txt(64, 68, "เครื่องของคุณ • Host Docker", size=20, fill="#3d5865", weight=800, anchor="start"),
    ]
    s += [
        f'<rect x="330" y="92" width="806" height="248" rx="20" fill="#f3f9fb" stroke="#147d92" stroke-width="3"/>',
        txt(354, 126, "devtools-jenkins  ·  --privileged  ·  dockerd ของตัวเอง", size=19, fill="#0b5a6b", weight=800, anchor="start"),
    ]
    s += [
        f'<rect x="352" y="148" width="762" height="172" rx="16" fill="#ffffff" stroke="#6cc0a4" stroke-width="2.5" stroke-dasharray="8 6"/>',
        txt(374, 176, "network: cicd-net", size=16, fill="#07795a", weight=800, anchor="start"),
    ]
    s += node(376, 192, 226, 108, "jk", "jenkins", "controller ของแล็บ")
    s += node(622, 192, 226, 108, "ext", "smee-client", "relay webhook")
    s += node(868, 192, 226, 108, "cd", "webapp", "ผลลัพธ์ที่ deploy")

    s += node(64, 118, 236, 96, "src", "Browser", "localhost:8080 / :8000")
    s += node(64, 236, 236, 96, "src", "SSH", "root@localhost -p 2222")
    s += arrow(304, 166, 326, 166)
    s += arrow(304, 284, 326, 284)

    s += band(36, 396, 1128, 56, "พอร์ตที่ map ออกมา", "#4b95cc")
    s += [
        txt(230, 432, "8080 → Jenkins", size=19, fill=INK, weight=700),
        txt(560, 432, "8000 → webapp", size=19, fill=INK, weight=700),
        txt(890, 432, "2222 → SSH devtools", size=19, fill=INK, weight=700),
    ]
    s += tail()
    write("d4_docker_layers.svg", s)


def d5_volume_state() -> None:
    W, H = 1200, 490
    s = head("d5", W, H, "container หายได้ แต่ state ต้องอยู่", "ลบและสร้าง container ใหม่โดย mount named volume jenkins_home เดิม งานและประวัติ build จึงยังอยู่")
    y, h, w, gap = 96, 140, 340, 50
    xs = [40 + i * (w + gap) for i in range(3)]
    s += node(xs[0], y, w, h, "warn", "1 · ลบ container", "docker rm -f jenkins", "writable layer หายไปด้วย")
    s += node(xs[1], y, w, h, "plain", "2 · ไม่มีอะไรรันอยู่", "ไม่มี process ของ Jenkins", "แต่ข้อมูลยังไม่ถูกลบ")
    s += node(xs[2], y, w, h, "ci", "3 · สร้างใหม่", "docker run … -v jenkins_home:…", "job และ build history กลับมาครบ")
    s += arrow(xs[0] + w + 6, y + h / 2, xs[1] - 8, y + h / 2)
    s += arrow(xs[1] + w + 6, y + h / 2, xs[2] - 8, y + h / 2)

    vy = y + h + 66
    s += [
        f'<rect x="40" y="{vy}" width="1120" height="104" rx="{R_NODE}" fill="#fff5d9" '
        f'stroke="#d99013" stroke-width="{SW_NODE}"/>',
        txt(600, vy + 44, "named volume  jenkins_home  →  /var/jenkins_home", size=24, fill="#95600b", weight=700),
        txt(600, vy + 76, "users • jobs • build history • workspaces — อยู่ต่อไปทั้งสามขั้น", size=17, fill=MUTED),
    ]
    for x in xs:
        s += curve(f"M{x + w / 2} {y + h + 6}L{x + w / 2} {vy - 6}", dash="8 7", width=3)
    s += footnote(W, vy + 148, "สิ่งที่ต้องรอด restart อยู่ใน volume ไม่ใช่ใน container — จึงไม่ต้องทำ Setup Wizard ซ้ำ")
    s += tail()
    write("d5_volume_state.svg", s)


def d6_jenkinsfile_anatomy() -> None:
    W, H = 1200, 470
    s = head("d6", W, H, "กายวิภาคของ Jenkinsfile", "โครง Declarative Pipeline ตั้งแต่ pipeline agent parameters environment stages steps when และ post")
    s += [
        f'<rect x="44" y="40" width="560" height="392" rx="20" fill="#122536" stroke="#2c4a5f" stroke-width="2"/>'
    ]
    code = [
        ("pipeline {", 0, "#7ee0ad"),
        ("agent any", 1, "#dcecf3"),
        ("parameters { string(name: 'APP_ENV', …) }", 1, "#dcecf3"),
        ("environment { LAB_NAME = '…' }", 1, "#dcecf3"),
        ("stages {", 1, "#7ee0ad"),
        ("stage('Test') {", 2, "#dcecf3"),
        ("steps { echo 'Tests passed' }", 3, "#ffd479"),
        ("}", 2, "#dcecf3"),
        ("stage('Deploy') {", 2, "#dcecf3"),
        ("when { expression { … == 'prod' } }", 3, "#91cfff"),
        ("steps { echo 'Deploying' }", 3, "#ffd479"),
        ("}", 2, "#dcecf3"),
        ("}", 1, "#7ee0ad"),
        ("post { always { … }  success { … } }", 1, "#91cfff"),
        ("}", 0, "#7ee0ad"),
    ]
    ly = 76
    for line, depth, colour in code:
        s.append(
            f'<text x="{68 + depth * 20}" y="{ly}" font-size="16.5" font-family="{MONO}" fill="{colour}">{esc(line)}</text>'
        )
        ly += 24
    labels = [
        (76, "pipeline", "บล็อกนอกสุด — ต้องมีเสมอ", "jk"),
        (152, "agent", "จะรันที่ node ไหน", "src"),
        (228, "parameters / environment", "ค่าจากผู้กด Build • ค่าที่ใช้ร่วม", "src"),
        (304, "stages → stage → steps", "ชื่อ stage เล่า flow • steps ลงมือ", "ci"),
        (380, "when / post", "เงื่อนไขข้าม stage • งานปิดท้าย", "cd"),
    ]
    for y, title, sub, role in labels:
        s += node(672, y - 30, 484, 62, role, title, sub, size=21, subsize=15)
        s += arrow(610, y + 2, 664, y + 2, dash="7 6", width=3)
    s += tail()
    write("d6_jenkinsfile_anatomy.svg", s)


def d7_dood_socket() -> None:
    W, H = 1200, 440
    s = head("d7", W, H, "Docker outside of Docker", "Jenkins มีเฉพาะ Docker CLI แล้วส่งคำสั่งผ่าน socket ไปยัง dockerd ของ devtools คอนเทนเนอร์ที่ได้จึงเป็น sibling")
    s += band(36, 62, 1128, 236, "dockerd ของ devtools — daemon ตัวเดียวที่ทำงานจริง", "#147d92")

    s += node(72, 106, 292, 148, "jk", "jenkins", "มีแค่ Docker CLI 29.7.2", "image: jenkins-docker:2569")
    s += node(788, 106, 340, 148, "ci", "container ที่ build ออกมา", "อยู่ระดับเดียวกับ jenkins", "ไม่ได้ซ้อนอยู่ข้างใน")
    s += [
        f'<rect x="440" y="128" width="272" height="104" rx="{R_NODE}" fill="#ffffff" '
        f'stroke="#7d97a3" stroke-width="{SW_NODE}"/>',
        txt(576, 168, "/var/run/docker.sock", size=19, fill="#3d5865", weight=700, mono=True),
        txt(576, 196, "bind mount เข้า jenkins", size=16, fill=MUTED),
    ]
    s += arrow(368, 180, 434, 180)
    s += arrow(716, 180, 782, 180)
    s += [
        txt(400, 158, "สั่ง", size=15, fill=MUTED, weight=700),
        txt(750, 158, "สร้าง", size=15, fill=MUTED, weight=700),
    ]
    s += node(72, 322, 520, 80, "warn", "socket ≈ สิทธิ์ root ของ inner host", "ใช้เฉพาะแล็บที่ทิ้งได้ — production ต้องแยก agent")
    s += node(624, 322, 504, 80, "ci", "แลกมาด้วยความเร็ว", "ใช้ image cache • network • lifecycle ชุดเดียวกัน")
    s += tail()
    write("d7_dood_socket.svg", s)


def d8_credentials_flow() -> None:
    W, H = 1200, 440
    s = head("d8", W, H, "เส้นทางของ credential", "Jenkinsfile อ้างเฉพาะ ID ส่วนค่าจริงอยู่ใน credentials store และถูกฉีดเฉพาะช่วง withCredentials")
    y, h = 116, 146
    s += node(40, y, 250, h, "src", "Jenkinsfile", "อ้างแค่ id: 'dockerhub'", "อยู่ใน Git ได้ปลอดภัย")
    s += node(330, y, 250, h, "jk", "Credentials store", "Username with password", "อยู่ใน jenkins_home")
    s += node(620, y, 250, h, "ci", "withCredentials { }", "ฉีดเป็น env เฉพาะบล็อกนี้", "$DOCKER_USER / $DOCKER_TOKEN")
    s += node(910, y, 250, h, "cd", "Console output", "แสดงเป็น ****", "Masking = ลดความเสี่ยง")
    for x in (290, 580, 870):
        s += arrow(x + 4, y + h / 2, x + 36, y + h / 2)

    s += node(40, 316, 540, 84, "warn", "ห้าม", "echo token • printenv • archive Docker config", size=21, subsize=16)
    s += node(620, 316, 540, 84, "ci", "ท่ามาตรฐาน", "set +x • --password-stdin • DOCKER_CONFIG ชั่วคราว + trap", size=21, subsize=16)
    s += tail()
    write("d8_credentials_flow.svg", s)


def d9_polling_webhook() -> None:
    W, H = 1200, 480
    s = head("d9", W, H, "Poll SCM กับ Webhook", "แบบ pull Jenkins ถาม GitHub ทุกนาที ส่วนแบบ push GitHub ส่ง event ผ่าน smee.io เข้า Jenkins หลัง NAT")

    s += band(36, 54, 1128, 150, "PULL — LAB 4 · Poll SCM  * * * * *", "#4b95cc")
    s += node(80, 84, 260, 96, "jk", "Jenkins", "ตื่นทุกนาที")
    s += node(470, 84, 260, 96, "ext", "GitHub", "ตอบว่ามี/ไม่มี commit")
    s += node(860, 84, 260, 96, "cd", "Build", "เมื่อ revision เปลี่ยน")
    s += curve("M344 118L466 118", dash="7 6")
    s += curve("M466 150L344 150", dash="7 6")
    s += [txt(405, 106, "ถาม", size=15, fill=MUTED, weight=700), txt(405, 176, "ตอบ", size=15, fill=MUTED, weight=700)]
    s += arrow(734, 132, 856, 132)
    s += [txt(795, 118, "หน่วงถึงรอบถัดไป", size=15, fill=MUTED, weight=700)]

    s += band(36, 260, 1128, 156, "PUSH — LAB 5 · webhook + smee relay", "#169b72")
    w, h, gap, y = 246, 96, 42, 292
    hops = [
        ("ext", "GitHub", "ส่งเมื่อ push"),
        ("ext", "smee.io", "channel สาธารณะ"),
        ("jk", "smee-client", "อยู่ใน cicd-net"),
        ("ci", "Jenkins GWT", "token + ref filter"),
    ]
    nodes, xs = row(66, y, w, h, gap, hops)
    s += nodes
    for i, x in enumerate(xs, 1):
        s += badge(x + 20, y - 2, str(i))
    s += [txt(600, 452, "ไม่มี polling delay — แต่ GitHub ต้องส่งถึง receiver ได้ จึงต้องมี relay", size=19, fill=INK, weight=700)]
    s += tail()
    write("d9_polling_webhook.svg", s)


def d10_capstone_topology() -> None:
    W, H = 1200, 545
    s = head("d10", W, H, "Topology ของ capstone", "GitHub smee.io และ Docker Hub อยู่บนอินเทอร์เน็ต ส่วน jenkins relay และ webapp อยู่ใน cicd-net ภายใน devtools")
    s += band(36, 54, 1128, 136, "internet", "#7d97a3")
    s += node(78, 82, 300, 92, "ext", "GitHub", "<GITHUB_USER>/webapp")
    s += node(430, 82, 300, 92, "ext", "smee.io", "<SMEE_WEBAPP_URL>")
    s += node(822, 82, 300, 92, "cd", "Docker Hub", "<DOCKER_USER>/cicd-webapp")
    s += arrow(384, 128, 424, 128)
    s += badge(404, 100, "1")

    s += band(36, 292, 1128, 172, "devtools-jenkins  →  network cicd-net", "#147d92", label_pos="bottom")
    s += node(78, 322, 300, 116, "jk", "smee-webapp", "relay → GWT", "token cicd2569-webapp")
    s += node(430, 322, 300, 116, "ci", "jenkins", "job webapp-deploy", "build → pytest → push")
    s += node(822, 322, 300, 116, "cd", "webapp", "http://webapp:8000", "browser: localhost:8000")
    s += arrow(384, 380, 424, 380)
    s += arrow(736, 380, 816, 380)
    s += badge(404, 352, "3")
    s += badge(776, 352, "5")

    s += curve("M580 178L580 240L228 240L228 316", dash="9 7")
    s += badge(300, 240, "2")
    s += curve("M972 316L972 262L1080 262L1080 180", dash="9 7")
    s += badge(1030, 262, "4")

    s += footnote(W, 518, "1 push → 2 relay → 3 build+test → 4 push image → 5 deploy แล้ว verify — SHA เดียวไล่ได้ตลอดสาย")
    s += tail()
    write("d10_capstone_topology.svg", s)



def d0_cicd_loop() -> None:
    """Cover art: the standard CI/CD lifecycle loop, drawn as one closed ring.

    Reference shape — the six-stage continuous delivery lifecycle used by every
    mainstream CI/CD reference (code → build → test → release → deploy →
    monitor → back to code).  Nothing here is Jenkins-specific on purpose: the
    cover has to read as CI/CD to somebody who has never opened Jenkins.
    """
    import math

    W, H = 620, 476
    s = head(
        "d0",
        W,
        H,
        "วงจร CI/CD",
        "หกขั้นของวงจรส่งมอบซอฟต์แวร์ Code Build Test Release Deploy Monitor แล้ววนกลับมาที่ Code",
    )

    cx, cy, r = 310, 224, 143
    stations = [
        ("Code", -90, "src"),
        ("Build", -30, "ci"),
        ("Test", 30, "ci"),
        ("Release", 90, "cd"),
        ("Deploy", 150, "cd"),
        ("Monitor", 210, "src"),
    ]
    arcs = [
        ("#169b72", "ahg", None),
        ("#169b72", "ahg", None),
        ("#7d97a3", "ah", None),
        ("#d99013", "ahw", None),
        ("#d99013", "ahw", None),
        ("#4b95cc", "ahb", "8 8"),
    ]

    def point(angle: float, radius: float) -> tuple[float, float]:
        rad = math.radians(angle)
        return cx + math.cos(rad) * radius, cy + math.sin(rad) * radius

    pad = 15
    for i, (colour, marker, dash) in enumerate(arcs):
        a1 = stations[i][1] + pad
        a2 = stations[(i + 1) % len(stations)][1] - pad
        x1, y1 = point(a1, r)
        x2, y2 = point(a2, r)
        arc = curve(
            f"M{round(x1, 1)} {round(y1, 1)}A{r} {r} 0 0 1 {round(x2, 1)} {round(y2, 1)}",
            colour=colour,
            marker=marker,
            dash=dash,
            width=4,
        )
        if not dash:
            arc = [a.replace("<path ", f'<path class="d0-arc" style="animation-delay:{i * 1.5}s" ', 1) for a in arc]
        s += arc

    for label, angle, role in stations:
        fill, stroke, ink = ROLES[role]
        px, py = point(angle, r)
        pw, ph = 118, 44
        delay = stations.index((label, angle, role)) * 1.5
        s += [
            f'<rect class="d0-pill" style="animation-delay:{delay}s" '
            f'x="{round(px - pw / 2, 1)}" y="{round(py - ph / 2, 1)}" width="{pw}" height="{ph}" '
            f'rx="22" fill="{fill}" stroke="{stroke}" stroke-width="3"/>',
            txt(round(px, 1), round(py + 7, 1), label, size=20, fill=ink, weight=800),
        ]

    s += [
        f'<circle class="d0-core" cx="{cx}" cy="{cy}" r="80" fill="#ffffff" stroke="#147d92" stroke-width="3"/>',
        txt(cx, cy + 2, "CI/CD", size=40, fill="#0b5a6b", weight=800),
        txt(cx, cy + 30, "ด้วย Jenkins", size=16, fill=MUTED, weight=700),
    ]

    # A single commit travelling the loop: the motion carries the idea that the
    # cycle never stops, without adding anything the reader has to decode.
    s += [
        f'<g><circle cx="{cx}" cy="{cy - r}" r="13" fill="#169b72" fill-opacity="0.22"/>'
        f'<circle cx="{cx}" cy="{cy - r}" r="7.5" fill="#169b72" stroke="#ffffff" stroke-width="3"/>'
        f'<animateTransform attributeName="transform" attributeType="XML" type="rotate" '
        f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="9s" repeatCount="indefinite"/></g>'
    ]

    s.insert(
        3,
        "<style>"
        ".d0-pill{animation:d0-pulse 9s linear infinite}"
        "@keyframes d0-pulse{0%,14%,100%{stroke-width:3}5%{stroke-width:6.5}}"
        ".d0-core{animation:d0-breathe 4.5s ease-in-out infinite}"
        "@keyframes d0-breathe{0%,100%{r:80}50%{r:83.5}}"
        ".d0-arc{stroke-dasharray:420;animation:d0-draw 9s linear infinite}"
        "@keyframes d0-draw{0%,100%{stroke-dashoffset:0;opacity:.55}"
        "6%{stroke-dashoffset:0;opacity:1}20%{opacity:.55}}"
        "@media (prefers-reduced-motion:reduce){.d0-pill,.d0-core,.d0-arc{animation:none}}"
        "</style>",
    )

    chips = [("#169b72", "#e6fbf4", "#07795a", "CI — build + test ทุก commit"),
             ("#d99013", "#fff5d9", "#95600b", "CD — ส่งถึงผู้ใช้อัตโนมัติ")]
    widths = [40 + len(label) * 7.4 for *_, label in chips]
    lx = (W - (sum(widths) + 16)) / 2
    for (stroke, fill, ink, label), cw in zip(chips, widths):
        s += [
            f'<rect x="{round(lx, 1)}" y="418" width="{round(cw, 1)}" height="32" rx="16" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
            f'<circle cx="{round(lx + 18, 1)}" cy="434" r="6" fill="{stroke}"/>',
            txt(round(lx + 30, 1), 440, label, size=13.5, fill=ink, weight=700, anchor="start"),
        ]
        lx += cw + 16
    s += tail()
    write("d0_cicd_loop.svg", s)


def d11_manual_vs_auto() -> None:
    """Same job, two lanes: who remembers the steps, and what evidence is left."""
    W, H = 1200, 486
    s = head(
        "d11",
        W,
        H,
        "ปล่อยของด้วยมือ เทียบกับ CI/CD",
        "งานเท่ากันสี่ขั้น แต่แบบทำมือขั้นตอนอยู่ในหัวคนและไม่มีหลักฐาน ส่วน CI/CD ขั้นตอนอยู่ในไฟล์และเก็บหลักฐานทุกครั้ง",
    )

    w, h, gap = 214, 94, 68
    x0 = (W - (4 * w + 3 * gap)) / 2

    lanes = [
        (
            52,
            "ทำเอง — ขั้นตอนอยู่ในหัวคน",
            "#cf4b45",
            "ahr",
            [
                ("warn", "แก้โค้ด", "บนเครื่องตัวเอง"),
                ("warn", "build เอง", "ต้องจำคำสั่งให้ครบ"),
                ("warn", "คัดลอกขึ้น server", "ลากไฟล์ / scp"),
                ("warn", "ssh restart", "แล้วเปิดดูเอง"),
            ],
            "ผลต่างกันตามคนและเครื่อง • ไม่มี log ย้อนหลัง • รู้ว่าพังตอนผู้ใช้เจอ",
            "#a2312c",
        ),
        (
            268,
            "CI/CD — ขั้นตอนอยู่ในไฟล์ที่ review ได้",
            "#169b72",
            "ahg",
            [
                ("src", "git push", "จุดเริ่มเดียว"),
                ("jk", "Jenkins รับ event", "ทุกครั้ง ไม่มีข้อยกเว้น"),
                ("ci", "Build → Test → Push", "สูตรเดียวกันทุกครั้ง"),
                ("cd", "Deploy + Verify", "ตรวจว่าใช้ได้จริง"),
            ],
            "ผลเหมือนเดิมทุกครั้ง • มี build number + console เป็นหลักฐาน • รู้ผลในไม่กี่นาที",
            "#07795a",
        ),
    ]

    for top, label, stroke, marker, specs, outcome, ink in lanes:
        s += band(36, top, 1128, 166, label, stroke)
        y = top + 32
        for i, spec in enumerate(specs):
            x = x0 + i * (w + gap)
            s += node(x, y, w, h, *spec, size=21, subsize=15)
            if i:
                s += arrow(x - gap + 10, y + h / 2, x - 8, y + h / 2, colour=stroke, marker=marker)
        s += [txt(W / 2, top + 148, outcome, size=17.5, fill=ink, weight=700)]

    s += footnote(W, 466, "งานเหมือนกันทุกขั้น — ต่างกันที่ “ใครเป็นคนจำ” และ “เหลืออะไรไว้ให้ตรวจย้อนหลัง”")
    s += tail()
    write("d11_manual_vs_auto.svg", s)


def d12_integration_hell() -> None:
    """Why CI exists: batch size decides how painful integration is."""
    W, H = 1200, 486
    s = head(
        "d12",
        W,
        H,
        "Integration Hell กับ Continuous Integration",
        "แยกสาขานานแล้วรวมทีเดียวทำให้ conflict ก้อนใหญ่ ส่วนการรวมเข้า main ทุกวันทำให้แต่ละครั้งเล็กและตรวจได้ทันที",
    )

    s += band(36, 44, 1128, 196, "ไม่ทำ CI — ต่างคนต่างแยกสาขานานเป็นสัปดาห์", "#cf4b45")
    branches = [(104, "dev A"), (146, "dev B"), (188, "dev C")]
    for by, name in branches:
        s += [
            f'<path d="M150 {by}L770 {by}" stroke="#b9ccd5" stroke-width="3" stroke-linecap="round"/>',
            txt(138, by + 6, name, size=14, fill=MUTED, weight=700, anchor="end"),
        ]
        for i in range(7):
            s += [f'<circle cx="{176 + i * 96}" cy="{by}" r="7" fill="#8fb2c2"/>']
        s += arrow(778, by, 812, 146, colour="#cf4b45", marker="ahr", width=3)
    s += node(820, 96, 322, 100, "warn", "merge ครั้งเดียว", "conflict ก้อนใหญ่", "หาสาเหตุยาก • เสียเวลาเป็นวัน", size=22, subsize=15)

    s += band(36, 268, 1128, 168, "ทำ CI — รวมเข้า main อย่างน้อยวันละครั้ง", "#169b72")
    main_y = 358
    s += [f'<path d="M150 {main_y}L770 {main_y}" stroke="#169b72" stroke-width="4" stroke-linecap="round"/>',
          txt(138, main_y + 6, "main", size=14, fill="#07795a", weight=800, anchor="end")]
    for i in range(7):
        mx = 176 + i * 96
        s += [f'<circle cx="{mx}" cy="{main_y}" r="10" fill="#169b72" stroke="#ffffff" stroke-width="3"/>']
        above = i % 2 == 0
        sy = main_y - 44 if above else main_y + 44
        s += arrow(mx - 34, sy, mx - 5, main_y - 11 if above else main_y + 11, colour="#6cc0a4", marker="ahg", width=3)
    s += arrow(778, main_y, 812, main_y - 4, colour="#169b72", marker="ahg", width=3)
    s += node(820, 308, 322, 100, "ci", "รวมเล็ก ๆ บ่อย ๆ", "conflict เล็ก แก้ได้ทันที", "ทุก commit ถูก build + test", size=22, subsize=15)

    s += footnote(W, 466, "CI คือวินัยของทีม — “รวมโค้ดบ่อย แล้วให้ระบบ build + test ทุกครั้ง” ไม่ใช่แค่การติดตั้งเครื่องมือ")
    s += tail()
    write("d12_integration_hell.svg", s)



def d13_integration_conflict() -> None:
    """Scenario 1 — two developers, three weeks apart, one painful merge."""
    W, H = 1200, 448
    s = head(
        "d13",
        W,
        H,
        "สถานการณ์ที่ 1 — Integration Conflict",
        "Programmer A และ Programmer B แยกกันทำงานสามสัปดาห์โดยไม่รวมโค้ด เมื่อ merge วันสุดท้ายจึงเกิด conflict จำนวนมากและ build ล้ม",
    )

    lanes = [("Programmer A", 86, "แก้ 12 ไฟล์"), ("Programmer B", 250, "แก้ 9 ไฟล์")]
    for name, y, note in lanes:
        s += node(48, y, 226, 96, "src", name, note)
        s += [f'<path d="M282 {y + 48}L700 {y + 48}" stroke="#b9ccd5" stroke-width="3" stroke-linecap="round"/>']
        for i in range(5):
            s += [f'<circle cx="{318 + i * 92}" cy="{y + 48}" r="8" fill="#8fb2c2"/>']
        s += arrow(710, y + 48, 782, 226, colour="#cf4b45", marker="ahr")

    s += [
        f'<rect x="300" y="24" width="400" height="30" rx="15" fill="#eef3f6" stroke="#b9ccd5" stroke-width="2"/>',
        txt(500, 44, "สามสัปดาห์ที่ไม่ได้รวมโค้ดกันเลย", size=15, fill=MUTED, weight=700),
    ]

    s += node(
        790, 146, 356, 162, "warn", "merge วันสุดท้าย",
        "conflict 42 จุดในไฟล์เดียวกัน",
        "build ล้ม • หาสาเหตุไม่เจอ • เลื่อน release",
        size=24, subsize=16,
    )
    s += footnote(W, 412, "ยิ่งปล่อยให้โค้ดสองสายห่างกันนาน ต้นทุนของการรวมกลับยิ่งสูงแบบไม่เป็นเชิงเส้น")
    s += tail()
    write("d13_integration_conflict.svg", s)


def d14_late_feedback() -> None:
    """Scenario 2 — the same defect, found at two very different moments."""
    W, H = 1200, 486
    s = head(
        "d14",
        W,
        H,
        "สถานการณ์ที่ 2 — ตรวจพบข้อผิดพลาดช้าเกินไป",
        "ข้อผิดพลาดเดียวกันถ้าไม่มีการทดสอบอัตโนมัติจะถูกพบหลังผู้ใช้ได้รับผลกระทบ แต่ถ้าทดสอบทุก commit จะถูกพบภายในไม่กี่นาที",
    )

    w, h, gap = 226, 92, 62
    x0 = (W - (4 * w + 3 * gap)) / 2
    lanes = [
        (
            52, "ไม่มีการทดสอบอัตโนมัติ", "#cf4b45", "ahr",
            [
                ("plain", "commit", "งานเสร็จตามกำหนด"),
                ("warn", "deploy ขึ้น production", "ไม่มีใครตรวจก่อน"),
                ("warn", "ผู้ใช้แจ้งปัญหา", "หลายชั่วโมงถึงหลายวัน"),
                ("warn", "ไล่หาสาเหตุย้อนหลัง", "ไม่รู้ว่ามาจาก commit ไหน"),
            ],
            "พบช้า → ผู้ใช้ได้รับผลกระทบแล้ว • ต้องดึงคนทั้งทีมมาช่วย • แก้แบบเร่งด่วน",
            "#a2312c",
        ),
        (
            268, "ทดสอบอัตโนมัติทุก commit", "#169b72", "ahg",
            [
                ("plain", "commit", "งานเสร็จตามกำหนด"),
                ("ci", "build + test อัตโนมัติ", "ทำงานทันทีที่ push"),
                ("ci", "ผลแดงภายในไม่กี่นาที", "ระบุ commit ที่ทำให้พัง"),
                ("cd", "แก้ก่อนถึงผู้ใช้", "คนที่ commit แก้เอง"),
            ],
            "พบเร็ว → ยังไม่ถึงผู้ใช้ • ขอบเขตความผิดพลาดแคบ • แก้ด้วยคนเดียว",
            "#07795a",
        ),
    ]

    for top, label, stroke, marker, specs, outcome, ink in lanes:
        s += band(36, top, 1128, 166, label, stroke)
        y = top + 32
        for i, spec in enumerate(specs):
            x = x0 + i * (w + gap)
            s += node(x, y, w, h, *spec, size=20, subsize=14)
            if i:
                s += arrow(x - gap + 10, y + h / 2, x - 8, y + h / 2, colour=stroke, marker=marker)
        s += [txt(W / 2, top + 148, outcome, size=17, fill=ink, weight=700)]

    s += footnote(W, 466, "หลักการ shift-left — ย้ายการตรวจสอบให้เกิดใกล้เวลาที่เขียนโค้ดมากที่สุด")
    s += tail()
    write("d14_late_feedback.svg", s)


def d15_dev_ops_wall() -> None:
    """Scenario 3 — release slows down at the hand-off, not at the keyboard."""
    W, H = 1200, 470
    s = head(
        "d15",
        W,
        H,
        "สถานการณ์ที่ 3 — การส่งมอบระหว่างทีม Dev และทีม Ops",
        "ทีม Dev ส่งงานเป็นไฟล์และเอกสาร ทีม Ops ต้องตีความขั้นตอนเองบนสภาพแวดล้อมที่ไม่เหมือนกัน การปล่อยของจึงช้าและทำซ้ำไม่ได้",
    )

    s += node(48, 92, 380, 210, "src", "ทีม Dev", "เขียนโค้ดเสร็จ • ทดสอบบนเครื่องตัวเอง", "ส่งมอบเป็นไฟล์ + เอกสารหนึ่งหน้า", size=26, subsize=17)
    s += node(772, 92, 380, 210, "warn", "ทีม Ops", "ต้องเดาขั้นตอนที่เอกสารไม่ได้เขียน", "สภาพแวดล้อมจริงไม่เหมือนเครื่อง Dev", size=26, subsize=17)

    wx = 546
    s += [
        f'<rect x="{wx}" y="70" width="108" height="254" rx="14" fill="#f4f7f9" stroke="#7d97a3" '
        'stroke-width="3" stroke-dasharray="10 8"/>',
        txt(wx + 54, 52, "กำแพงส่งมอบ", size=17, fill="#3d5865", weight=800),
    ]
    for i in range(5):
        yy = 88 + i * 50
        s += [f'<path d="M{wx + 12} {yy}L{wx + 96} {yy + 32}" stroke="#dbe6ec" stroke-width="6" stroke-linecap="round"/>']

    s += arrow(436, 197, wx - 8, 197)
    s += [txt(490, 180, "โยนข้าม", size=15, fill=MUTED, weight=700)]
    s += arrow(wx + 116, 197, 764, 197)
    s += [txt(710, 180, "รับไปทำต่อ", size=15, fill=MUTED, weight=700)]

    s += band(48, 346, 1104, 76, "ผลที่เกิดขึ้นกับการปล่อยของ", "#cf4b45", label_at="center")
    s += [
        txt(266, 392, "release เลื่อนออกไป", size=19, fill="#a2312c", weight=700),
        txt(600, 392, "ทำซ้ำให้เหมือนเดิมไม่ได้", size=19, fill="#a2312c", weight=700),
        txt(934, 392, "พังแล้วตอบไม่ได้ว่าใครแก้อะไร", size=19, fill="#a2312c", weight=700),
    ]
    s += tail()
    write("d15_dev_ops_wall.svg", s)


def d16_ci_workflow() -> None:
    """What one CI round actually does, and where its answer goes back to."""
    W, H = 1200, 476
    s = head(
        "d16",
        W,
        H,
        "Workflow ของ Continuous Integration",
        "นักพัฒนา commit เข้า mainline แล้ว CI server สร้าง build ทดสอบอัตโนมัติ และส่งผลเขียวหรือแดงกลับถึงผู้ commit ทันที",
    )

    s += node(44, 150, 216, 128, "src", "นักพัฒนา", "commit งานเล็ก ๆ", "อย่างน้อยวันละครั้ง")
    s += node(320, 150, 216, 128, "ext", "mainline", "สาขาหลักที่ทุกคนใช้ร่วมกัน")
    s += arrow(270, 214, 312, 214)
    s += [txt(291, 196, "push", size=14, fill=MUTED, weight=700)]

    bx, by, bw, bh = 610, 62, 546, 304
    s += [
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="22" fill="#f2fafb" stroke="#147d92" stroke-width="3"/>',
        txt(bx + bw / 2, by + 34, "CI server — ทำงานเองทุกครั้งที่ mainline เปลี่ยน", size=18, fill="#0b5a6b", weight=800),
    ]
    s += arrow(546, 214, bx - 8, 214)
    s += [txt(578, 196, "trigger", size=14, fill=MUTED, weight=700)]

    steps = [("1 · Checkout", "ดึงโค้ดของ commit นั้น"), ("2 · Build", "สร้าง artifact จากศูนย์"), ("3 · Test", "รันชุดทดสอบอัตโนมัติ")]
    for i, (title, sub) in enumerate(steps):
        sy = by + 54 + i * 62
        s += [
            f'<rect x="{bx + 26}" y="{sy}" width="{bw - 52}" height="52" rx="14" fill="#ffffff" stroke="#6cc0a4" stroke-width="2.5"/>',
            txt(bx + 52, sy + 33, title, size=19, fill="#07795a", weight=800, anchor="start"),
            txt(bx + bw - 42, sy + 32, sub, size=15, fill=MUTED, anchor="end"),
        ]

    s += bar(bx + 26, by + bh - 66, bw - 52, 46, "ผลลัพธ์: เขียว = รวมได้  •  แดง = หยุดแล้วแก้ก่อน", "#147d92", size=18)

    fy = 424
    s += curve(f"M{bx + bw / 2} {by + bh + 8}L{bx + bw / 2} {fy}L152 {fy}L152 {286}", colour="#d99013", marker="ahw", dash="9 8")
    s += [txt(430, fy + 26, "ผลกลับถึงผู้ commit ภายในไม่กี่นาที", size=18, fill="#95600b", weight=700)]
    s += tail()
    write("d16_ci_workflow.svg", s)



def d17_lab1_workflow() -> None:
    """LAB 1 at a glance: six steps and the artefact each one leaves behind."""
    W, H = 1200, 490
    s = head(
        "d17",
        W,
        H,
        "ลำดับการทำงานของ LAB 1",
        "หกขั้นตอนตั้งแต่สร้างคอนเทนเนอร์ ตรวจสถานะ เข้าใช้งาน ตั้งค่า สร้างงานแรก จนถึงการยืนยันสถานะปิดท้าย",
    )

    w, h, gap = 320, 128, 78
    top_y, bot_y = 96, 292
    top_x0 = (W - (3 * w + 2 * gap)) / 2
    steps = [
        ("src", "1 · Start", "สร้าง network และคอนเทนเนอร์", "→ jenkins ทำงานบน cicd-net"),
        ("src", "2 · Verify", "ตรวจสถานะและ log ของคอนเทนเนอร์", "→ Up และเริ่มระบบเสร็จแล้ว"),
        ("jk", "3 · Access", "อ่านรหัสปลดล็อกแล้วเปิดหน้าเว็บ", "→ เข้าหน้า Unlock ที่พอร์ต 8080"),
        ("ci", "4 · Configure", "ติดตั้ง plugin และสร้างผู้ดูแล", "→ เข้าใช้งานด้วย admin ได้"),
        ("ci", "5 · Test", "สร้างและรัน job แรก", "→ build #1 = SUCCESS"),
        ("cd", "6 · Verify state", "restart แล้วรันสคริปต์ตรวจผล", "→ LAB 1 CHECK: PASS"),
    ]

    xs = []
    for i, spec in enumerate(steps):
        row, col = divmod(i, 3)
        x = top_x0 + col * (w + gap)
        y = top_y if row == 0 else bot_y
        xs.append((x, y))
        s += node(x, y, w, h, *spec, size=23, subsize=16)
        if col:
            s += arrow(x - gap + 10, y + h / 2, x - 8, y + h / 2)

    turn = (top_y + h + bot_y) / 2
    s += curve(
        f"M{xs[2][0] + w / 2} {top_y + h + 10}"
        f"L{xs[2][0] + w / 2} {turn}"
        f"L{xs[3][0] + w / 2} {turn}"
        f"L{xs[3][0] + w / 2} {bot_y - 8}"
    )
    s += [txt(W / 2, turn - 22, "ติดตั้งเสร็จแล้วจึงตั้งค่าและพิสูจน์ว่าใช้งานได้จริง", size=16, fill=MUTED, weight=700)]
    s += footnote(W, 470, "ทุกขั้นตอนมีผลลัพธ์ที่ตรวจสอบได้ — หากขั้นใดไม่ได้ผลตามนี้ ห้ามข้ามไปขั้นถัดไป")
    s += tail()
    write("d17_lab1_workflow.svg", s)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    d0_cicd_loop()
    d1_cicd_pipeline()
    d2_jenkins_position()
    d3_jenkins_architecture()
    d4_docker_layers()
    d5_volume_state()
    d6_jenkinsfile_anatomy()
    d7_dood_socket()
    d8_credentials_flow()
    d9_polling_webhook()
    d10_capstone_topology()
    d11_manual_vs_auto()
    d12_integration_hell()
    d13_integration_conflict()
    d14_late_feedback()
    d15_dev_ops_wall()
    d16_ci_workflow()
    d17_lab1_workflow()


if __name__ == "__main__":
    main()
