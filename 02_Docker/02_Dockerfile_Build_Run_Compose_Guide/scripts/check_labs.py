#!/usr/bin/env python3
"""ตรวจสอบชุด LAB "Dockerfile → Build → Run → Compose" แบบ static (ไม่เปิด Docker)

รันจากโฟลเดอร์ไหนก็ได้::

    python3 scripts/check_labs.py

ผ่านครบทุกข้อจะขึ้น ALL CHECKS PASSED และ exit 0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- ข้อมูลชุด LAB

LABS: dict[str, dict] = {
    "001_LAB_Dockerfile_First_Image": {
        "container": "devtools-df-lab1",
        "ssh_port": "2231",
        "app_ports": ["8181"],
    },
    "002_LAB_Layer_Cache_Build_Options": {
        "container": "devtools-df-lab2",
        "ssh_port": "2232",
        "app_ports": ["8182"],
    },
    "003_LAB_RUN_CMD_ENTRYPOINT": {
        "container": "devtools-df-lab3",
        "ssh_port": "2233",
        "app_ports": [],
    },
    "004_LAB_ENV_ARG_Config": {
        "container": "devtools-df-lab4",
        "ssh_port": "2234",
        "app_ports": ["8184"],
    },
    "005_LAB_Registry_Tag_Push_Pull": {
        "container": "devtools-df-lab5",
        "ssh_port": "2235",
        "app_ports": ["5035", "8185"],
    },
    "006_LAB_Network_DNS": {
        "container": "devtools-df-lab6",
        "ssh_port": "2236",
        "app_ports": ["8186"],
    },
    "007_LAB_Compose_Multistage_Capstone": {
        "container": "devtools-df-lab7",
        "ssh_port": "2237",
        "app_ports": ["8087", "8187"],
    },
}

REQUIRED_HEADINGS = (
    "สิ่งที่จะได้เรียนรู้",
    "ภาพรวมของแล็บนี้",
    "ทดลองเพิ่มเติม",
    "แก้ปัญหาที่พบบ่อย",
    "เก็บกวาด (Cleanup)",
    "เช็กลิสต์ก่อนจบแล็บ",
)

# ค่าที่ห้ามหลุดเข้าเอกสาร (เทียบแบบ case-insensitive)
FORBIDDEN_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{10,}", "GitHub personal access token"),
    (r"dckr_pat_[A-Za-z0-9_\-]{10,}", "Docker Hub access token"),
    (r"[A-Za-z0-9._%+-]+@gmail\.com", "อีเมลจริง"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
]

# `tuchsanai` ใช้ได้เฉพาะเป็นชื่อ image ของเครื่องเรียนเท่านั้น
ALLOWED_TUCHSANAI = re.compile(r"tuchsanai/devtools:2569_1")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# ---------------------------------------------------------------- helpers


def code_blocks(text: str) -> list[tuple[str, str]]:
    """คืน [(ภาษา, เนื้อใน fence), ...] และตรวจว่า fence ปิดครบ"""
    out: list[tuple[str, str]] = []
    lang: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if lang is None:
                lang = stripped[3:].strip() or "plain"
                buf = []
            else:
                out.append((lang, "\n".join(buf)))
                lang = None
        elif lang is not None:
            buf.append(line)
    if lang is not None:
        out.append(("__UNCLOSED__", "\n".join(buf)))
    return out


def bash_lines(text: str) -> list[str]:
    lines: list[str] = []
    for lang, body in code_blocks(text):
        if lang in ("bash", "sh", "shell"):
            lines.extend(body.splitlines())
    return lines


LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")


# ---------------------------------------------------------------- checks


def check_layout() -> None:
    for name in LABS:
        d = ROOT / name
        if not d.is_dir():
            fail(f"{name}: ไม่พบโฟลเดอร์")
            continue
        if not (d / "readme.md").is_file():
            fail(f"{name}: ไม่มี readme.md")
        if not (d / "verify.sh").is_file():
            fail(f"{name}: ไม่มี verify.sh")
        logs = d / "test_logs"
        if not logs.is_dir():
            fail(f"{name}: ไม่มีโฟลเดอร์ test_logs/")
        elif not any(logs.iterdir()):
            fail(f"{name}: test_logs/ ว่างเปล่า — ต้องมี log การรันจริง")

    stray = sorted(
        p.name
        for p in ROOT.iterdir()
        if p.is_dir() and re.match(r"^\d{3}_LAB_", p.name) and p.name not in LABS
    )
    for name in stray:
        fail(f"{name}: โฟลเดอร์ LAB ที่ไม่อยู่ในแผน (ชื่อไม่ตรง SPEC)")


def check_verify_scripts() -> None:
    for name in LABS:
        f = ROOT / name / "verify.sh"
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("#!"):
            fail(f"{name}/verify.sh: ไม่มี shebang บรรทัดแรก")
        if "ALL CHECKS PASSED" not in text:
            fail(f"{name}/verify.sh: ไม่มีข้อความ ALL CHECKS PASSED")
        mode = f.stat().st_mode
        if not mode & 0o111:
            warn(f"{name}/verify.sh: ยังไม่ได้ตั้ง execute bit (chmod +x)")


def check_headings(name: str, text: str) -> None:
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            fail(f"{name}/readme.md: ขาดหัวข้อบังคับ '{heading}'")
    if not re.search(r"^# LAB \d", text, re.M):
        fail(f"{name}/readme.md: บรรทัดแรกต้องเป็น '# LAB <n> — ...'")
    if "✅ **Expected output**" not in text and "**Expected output**" not in text:
        fail(f"{name}/readme.md: ไม่มีบล็อก Expected output เลย")
    if text.count("📝 **คำอธิบาย:**") < 5:
        fail(f"{name}/readme.md: บล็อก '📝 คำอธิบาย' น้อยกว่า 5 จุด")
    if not re.search(r"- \[ \]", text):
        fail(f"{name}/readme.md: ไม่มี checkbox ในเช็กลิสต์")
    if "tuchsanai/devtools:2569_1" not in text:
        fail(f"{name}/readme.md: ไม่ได้อ้างอิง image เครื่องเรียน tuchsanai/devtools:2569_1")


def check_ports_and_names(name: str, text: str) -> None:
    meta = LABS[name]
    if meta["container"] not in text:
        fail(f"{name}/readme.md: ไม่พบชื่อ container ที่กำหนด ({meta['container']})")
    if f"-p {meta['ssh_port']}:22" not in text:
        fail(f"{name}/readme.md: ไม่พบการ map SSH port -p {meta['ssh_port']}:22")
    if f"-p {meta['ssh_port']}" not in text or f"ssh root@localhost -p {meta['ssh_port']}" not in text:
        fail(f"{name}/readme.md: ไม่พบคำสั่ง ssh root@localhost -p {meta['ssh_port']}")

    for other, ometa in LABS.items():
        if other == name:
            continue
        if ometa["container"] in text:
            fail(f"{name}/readme.md: อ้างถึง container ของ LAB อื่น ({ometa['container']})")
        if f"-p {ometa['ssh_port']}:22" in text:
            fail(f"{name}/readme.md: ใช้ SSH port ของ LAB อื่น ({ometa['ssh_port']})")


def check_secrets(name: str, path: Path, text: str) -> None:
    for pattern, label in FORBIDDEN_PATTERNS:
        for m in re.finditer(pattern, text):
            fail(f"{path.relative_to(ROOT)}: พบ {label} ในเอกสาร -> {m.group(0)[:24]}…")
    for m in re.finditer(r"tuchsanai", text):
        start = max(0, m.start() - 40)
        window = text[start : m.end() + 40]
        if not ALLOWED_TUCHSANAI.search(window):
            fail(
                f"{path.relative_to(ROOT)}: พบชื่อบัญชีจริง 'tuchsanai' นอกบริบท image เครื่องเรียน "
                f"(ให้ใช้ <DOCKER_USER>)"
            )
            break


def check_commands(name: str, text: str) -> None:
    lines = bash_lines(text)
    body = "\n".join(lines)

    for lang, _ in code_blocks(text):
        if lang == "__UNCLOSED__":
            fail(f"{name}/readme.md: มี code fence ``` ที่ไม่ได้ปิด")

    if re.search(r"(?<![\w.-])docker-compose\s", body):
        fail(f"{name}/readme.md: ใช้ `docker-compose` (ขีดกลาง) ในบล็อกคำสั่ง — ต้องใช้ `docker compose`")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # :latest ห้ามใช้เป็น "ที่มา" ของ image (run/pull/create)
        for m in re.finditer(r"docker\s+(?:run|pull|create)\b[^\n]*?\s([\w./:-]+):latest\b", stripped):
            fail(f"{name}/readme.md: ใช้ tag :latest ในคำสั่งสอน -> {m.group(0).strip()[:60]}")
        # docker build ติด :latest ได้เฉพาะเมื่อเป็น tag เสริมของ multi-tag (สอนตามคู่มือ ตอนที่ 4)
        if re.search(r"docker\s+build\b", stripped) and ":latest" in stripped:
            if stripped.count("-t ") < 2:
                fail(
                    f"{name}/readme.md: `docker build` ติดเฉพาะ :latest โดยไม่มี version tag คู่กัน "
                    f"-> {stripped[:60]}"
                )
        # image ที่ไม่ระบุ tag เลยในคำสั่ง pull
        m = re.search(r"docker\s+pull\s+([\w./-]+)\s*$", stripped)
        if m and ":" not in m.group(1):
            fail(f"{name}/readme.md: `docker pull {m.group(1)}` ไม่ได้ระบุ tag")

    if "docker rm -f" not in body:
        fail(f"{name}/readme.md: ส่วน Cleanup ไม่มีคำสั่ง docker rm -f")
    if 'docker ps -a --filter "name=^devtools-"' not in body:
        fail(
            f"{name}/readme.md: Cleanup ไม่มีคำสั่งตรวจ "
            'docker ps -a --filter "name=^devtools-"'
        )


def check_links(name: str, text: str) -> None:
    base = ROOT / name
    for m in LINK_RE.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        if not (base / target).exists():
            fail(f"{name}/readme.md: ลิงก์ชี้ไปไฟล์ที่ไม่มีอยู่ -> {target}")


def check_html_assets() -> None:
    """หน้าเว็บของ LAB ต้อง self-contained (ไม่โหลด asset จากภายนอก)"""
    ext_ref = re.compile(
        r"""(?:src|href)\s*=\s*["']https?://""", re.I
    )
    for name in LABS:
        for html in (ROOT / name).rglob("*.html"):
            if "test_logs" in html.parts:
                continue
            text = html.read_text(encoding="utf-8", errors="replace")
            if ext_ref.search(text):
                fail(f"{html.relative_to(ROOT)}: โหลด asset จากภายนอก (ต้อง inline ทั้งหมด)")
            for pattern, label in FORBIDDEN_PATTERNS:
                if re.search(pattern, text):
                    fail(f"{html.relative_to(ROOT)}: พบ {label}")


def check_index_readme() -> None:
    f = ROOT / "readme.md"
    if not f.is_file():
        fail("readme.md ระดับบนสุด: ไม่พบไฟล์")
        return
    text = f.read_text(encoding="utf-8", errors="replace")
    for name in LABS:
        if name not in text:
            fail(f"readme.md ระดับบนสุด: ไม่ได้อ้างถึง {name}")
    for m in LINK_RE.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if target and not (ROOT / target).exists():
            fail(f"readme.md ระดับบนสุด: ลิงก์ชี้ไปไฟล์ที่ไม่มีอยู่ -> {target}")
    check_secrets("readme.md", f, text)


def main() -> int:
    check_layout()
    check_verify_scripts()

    for name in LABS:
        f = ROOT / name / "readme.md"
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        check_headings(name, text)
        check_ports_and_names(name, text)
        check_secrets(name, f, text)
        check_commands(name, text)
        check_links(name, text)

        n_lines = len(text.splitlines())
        if n_lines < 300:
            warn(f"{name}/readme.md: สั้นเพียง {n_lines} บรรทัด (SPEC ตั้งไว้ 400–700)")

    check_html_assets()
    check_index_readme()

    for w in warnings:
        print(f"[WARN] {w}")
    for e in errors:
        print(f"[FAIL] {e}")

    if errors:
        print(f"\n{len(errors)} CHECK(S) FAILED")
        return 1
    print(f"\nALL CHECKS PASSED ({len(LABS)} labs, {len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
