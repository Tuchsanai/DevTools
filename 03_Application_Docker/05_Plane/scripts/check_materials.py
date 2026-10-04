#!/usr/bin/env python3
"""Static, offline QA for the Plane teaching set (deck + labs). Run from anywhere:

    python3 scripts/check_materials.py

Checks: single-file deck without external resources, slide/asset integrity, lab folder structure,
required readme sections, placeholder-only credentials, pinned image tags, Python syntax, internal links.
"""
from __future__ import annotations

import ast
import glob
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "Plane_Agile_Slides.html"
TOP_README = ROOT / "readme.md"

REQUIRED_LAB_HEADINGS = (
    "สิ่งที่จะได้เรียนรู้",
    "ทฤษฎีที่เกี่ยวข้อง",
    "ภาพรวมของแล็บนี้",
    "ทดลองเพิ่มเติม",
    "แก้ปัญหาที่พบบ่อย",
    "เก็บกวาด (Cleanup)",
    "สรุปคำสั่งของแล็บนี้",
    "เช็กลิสต์ก่อนจบแล็บ",
)
# Header/footer lines every lab readme must carry (kept in sync with the lab table in the top readme).
DURATION_RE = re.compile(r"^> \(เวลาโดยประมาณ : (\d+) นาที\)", re.M)
QUESTION_RE = re.compile(r"^> \*\*คำถามก่อนเริ่ม:\*\*", re.M)
FOOTER_RE = re.compile(r"^\*ผลลัพธ์ทั้งหมดในเอกสารนี้.*เมื่อ \S+.*\*$", re.M)

# Real-credential leak patterns — student-facing files must use placeholders only.
LEAKS = [
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"dckr_pat_[A-Za-z0-9_\-]{10,}", "Docker Hub token"),
    (r"plane_api_[0-9a-f]{32}", "real Plane API token"),
    (r"plane_wh_[0-9a-f]{32}", "real Plane webhook secret"),
    (r"[A-Za-z0-9._%+-]+@gmail\.com", "real-looking e-mail (gmail)"),
    (r"hf_[A-Za-z0-9]{20,}", "HuggingFace token"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style key"),
]
# The public course repo and classroom image are the only allowed uses of the maintainer's account name.
ALLOWED_REAL = ["https://github.com/Tuchsanai/DevTools.git", "tuchsanai/devtools:2569_1", "tuchsanai/devtools"]
TEXT_EXT = {".md", ".yml", ".yaml", ".sh", ".py", ".json", ".html", ".txt", ".conf", ".env", ".csv", ""}

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))")
fails: list[str] = []
warns: list[str] = []


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slots = 0
        self.slides = 0
        self.asset_refs: list[str] = []
        self.external: list[str] = []
        self.ids: dict[str, int] = {}

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        classes = set(a.get("class", "").split())
        if i := a.get("id"):
            self.ids[i] = self.ids.get(i, 0) + 1
        if tag == "div" and "slot" in classes:
            self.slots += 1
        if tag == "section" and "slide" in classes:
            self.slides += 1
        if tag == "img" and a.get("data-a"):
            self.asset_refs.append(a["data-a"])
        for attr in ("src", "href"):
            v = a.get(attr, "")
            if v.startswith(("http://", "https://", "//")) and tag in ("script", "link", "img", "iframe", "video", "source"):
                self.external.append(f"<{tag} {attr}={v[:80]}>")


def check_deck() -> None:
    if not DECK.exists():
        fails.append("ไม่พบไฟล์สไลด์ Plane_Agile_Slides.html")
        return
    html = read(DECK)
    p = DeckParser()
    p.feed(html)
    if p.slots < 40:
        fails.append(f"สไลด์น้อยผิดปกติ: {p.slots} slot")
    if p.slots != p.slides:
        fails.append(f"จำนวน .slot ({p.slots}) ไม่เท่ากับ section.slide ({p.slides})")
    if p.external:
        fails.append(f"สไลด์โหลดทรัพยากรภายนอก/CDN: {p.external[:3]}")
    for i, n in p.ids.items():
        if n > 1:
            fails.append(f"id ซ้ำในสไลด์: {i} ×{n}")
    m = re.search(r'window\.ASSETS=(\{.*?\});</script>', html, re.S)
    if not m:
        fails.append("ไม่พบ window.ASSETS ในสไลด์")
    else:
        keys = set(re.findall(r'"([^"]+)":\s*"data:', m.group(1)))
        missing = sorted(set(p.asset_refs) - keys)
        if missing:
            fails.append(f"data-a ที่ไม่มี asset: {missing[:6]}")
        placeholders = m.group(1).count("MISSING SCREENSHOT")
        if placeholders:
            warns.append(f"สไลด์ยังมี placeholder 'MISSING SCREENSHOT' {placeholders} รูป")
    for must in ("id=\"ov\"", "id=\"help\"", "class=\"pg\"", "keydown"):
        if must not in html:
            fails.append(f"สไลด์ขาดส่วนสำคัญ: {must}")
    print(f"deck: {p.slots} slides · {len(set(p.asset_refs))} assets referenced · external refs: {len(p.external)}")


def check_lab(lab: Path) -> None:
    name = lab.name
    files = [Path(f) for f in glob.glob(f"{lab}/**/*", recursive=True) if os.path.isfile(f)]
    readme = lab / "readme.md"
    if not readme.exists():
        readme = lab / "README.md"
    if not readme.exists():
        fails.append(f"{name}: ไม่มี readme.md")
        return
    rm = read(readme)
    for h in REQUIRED_LAB_HEADINGS:
        if h not in rm:
            fails.append(f"{name}: readme ขาดหัวข้อ '{h}'")
    if "Expected output" not in rm:
        fails.append(f"{name}: readme ไม่มี Expected output")
    if not QUESTION_RE.search(rm):
        fails.append(f"{name}: readme ไม่มี blockquote '> **คำถามก่อนเริ่ม:**'")
    if not FOOTER_RE.search(rm):
        fails.append(f"{name}: readme ไม่มีบรรทัดท้าย '*ผลลัพธ์ทั้งหมดในเอกสารนี้…เมื่อ <วันที่>*'")
    dm = DURATION_RE.search(rm)
    if not dm:
        fails.append(f"{name}: readme ไม่มีบรรทัด '> (เวลาโดยประมาณ : NN นาที)' ใต้ชื่อแล็บ")
    else:
        top = read(TOP_README)
        tm = re.search(rf"\|\s*\*\*(\d)\*\*\s*\|\s*(\d+) นาที\s*\|\s*\[`{re.escape(name)}`\]", top)
        if tm and tm.group(2) != dm.group(1):
            fails.append(f"{name}: เวลาโดยประมาณ {dm.group(1)} นาที ไม่ตรงกับตารางใน readme บนสุด ({tm.group(2)} นาที)")
        elif not tm:
            warns.append(f"{name}: หาแถวเวลาในตาราง LAB ของ readme บนสุดไม่พบ")
    if "📝" not in rm:
        warns.append(f"{name}: readme ไม่มี 📝 คำอธิบาย")
    # images referenced must exist; images present should be referenced
    for m in MARKDOWN_LINK_RE.finditer(rm):
        target = (m.group(1) or m.group(2) or "").split("#")[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (lab / target).exists() and not (ROOT / target).exists():
            fails.append(f"{name}: ลิงก์/รูปหาย → {target}")
    imgs = [f for f in files if f.suffix.lower() == ".png" and f.parent.name == "images"]
    if not imgs:
        warns.append(f"{name}: ไม่มีภาพหน้าจอจริงใน images/")
    for img in imgs:
        rel = f"images/{img.name}"
        if rel not in rm:
            warns.append(f"{name}: รูป {rel} ไม่ถูกอ้างถึงใน readme")
    # leaks
    for f in files:
        if f.suffix.lower() not in TEXT_EXT or f.suffix.lower() == ".png":
            continue
        body = read(f)
        for pat, what in LEAKS:
            if re.search(pat, body):
                fails.append(f"{name}: พบ {what} ใน {f.relative_to(ROOT)}")
        scrubbed = body
        for allowed in ALLOWED_REAL:
            scrubbed = scrubbed.replace(allowed, "")
        stray = re.findall(r"[Tt]uchsanai[^\s\)\"'`]*", scrubbed)
        if stray:
            fails.append(f"{name}: พบชื่อบัญชีจริงนอก clone URL/ชื่อ image ใน {f.relative_to(ROOT)} → {stray[:3]}")
        if f.suffix == ".py":
            try:
                ast.parse(body)
            except SyntaxError as e:
                fails.append(f"{name}: Python syntax error ใน {f.name}: {e}")
        if re.search(r"^\s*version:\s*['\"]?\d", body, re.M) and "compose" in f.name:
            warns.append(f"{name}: compose file มี 'version:' ที่เลิกใช้แล้ว ({f.name})")
        if re.search(r"image:\s*\S+:latest\b", body):
            warns.append(f"{name}: ใช้ image tag :latest ใน {f.name}")


def check_top_readme(labs: list[Path]) -> None:
    if not TOP_README.exists():
        fails.append("ไม่มี readme.md ระดับบนสุด")
        return
    rm = read(TOP_README)
    for lab in labs:
        if lab.name not in rm:
            fails.append(f"readme บนสุดไม่ได้ลิงก์ไป {lab.name}")
    if "Plane_Agile_Slides.html" not in rm:
        fails.append("readme บนสุดไม่ได้ลิงก์ไปสไลด์")


def main() -> int:
    labs = sorted(p for p in ROOT.glob("0*_LAB_*") if p.is_dir())
    print(f"labs: {[l.name for l in labs]}")
    check_deck()
    check_top_readme(labs)
    for lab in labs:
        check_lab(lab)
    for w in warns:
        print("WARN ", w)
    for f in fails:
        print("FAIL ", f)
    print(f"\n{len(fails)} fail · {len(warns)} warn")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
