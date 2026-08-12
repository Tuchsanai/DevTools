#!/usr/bin/env python3
"""Static and artifact validation for the Docker Practical Stacks bundle."""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
LABS = [
    "001_LAB_Nginx_Operations",
    "002_LAB_Flask_ENV",
    "003_LAB_MySQL_Network_Volume",
    "004_LAB_CMD_ENTRYPOINT",
    "005_LAB_Bulletin_Registry",
    "006_LAB_Compose_MySQL",
    "007_LAB_FastAPI_OpenCV_Streamlit",
    "008_LAB_Fullstack_Todo",
    "009_LAB_Capstone",
]
DECKS = [
    "Docker_Part1_Easy",
    "Docker_Part2_Intermediate",
    "Docker_Part3_Advanced",
]
TEXT_SUFFIXES = {".md", ".txt", ".html", ".yaml", ".yml", ".json", ".py", ".js", ".css", ".env", ".example", ""}
SECRET_PATTERNS = {
    "GitHub classic PAT": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "Docker Hub PAT": re.compile(r"dckr_pat_[A-Za-z0-9_-]{20,}"),
    "Embedded bearer token": re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{20,}"),
    "Real-looking Gmail address": re.compile(r"(?i)\b(?!your_|student|example)[A-Za-z0-9._%+-]+@gmail\.com\b"),
}


def command_output(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.returncode, result.stdout.strip()


def pdf_pages(path: Path) -> int | None:
    code, output = command_output(["pdfinfo", str(path)])
    if code:
        return None
    match = re.search(r"^Pages:\s+(\d+)$", output, re.MULTILINE)
    return int(match.group(1)) if match else None


def pptx_pages(path: Path) -> int | None:
    try:
        with zipfile.ZipFile(path) as archive:
            return len([
                name for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ])
    except (OSError, zipfile.BadZipFile):
        return None


def scan_secrets() -> list[str]:
    findings: list[str] = []
    excluded = {".git", ".export", "__pycache__"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in excluded for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Dockerfile", ".dockerignore", ".gitignore"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {path.relative_to(ROOT)}")
    return findings


def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    for lab in LABS:
        folder = ROOT / lab
        checks.append((f"LAB folder {lab}", folder.is_dir(), str(folder.relative_to(ROOT))))
        readme = folder / "readme.md"
        checks.append((f"LAB README {lab}", readme.exists(), "readme.md"))
        validation = folder / "validation.md"
        checks.append((f"LAB validation {lab}", validation.exists(), "validation.md"))

    for stem in DECKS:
        html_path = ROOT / f"{stem}.html"
        count = 0
        if html_path.exists():
            count = len(re.findall(r'<div class="slot">', html_path.read_text(encoding="utf-8")))
        checks.append((f"HTML {stem}", count >= 20, f"{count} slides"))

        pdf_path = ROOT / f"{stem}.pdf"
        pages = pdf_pages(pdf_path) if pdf_path.exists() else None
        checks.append((f"PDF {stem}", pages == count and count > 0, f"{pages} pages"))

        pptx_path = ROOT / f"{stem}.pptx"
        slides = pptx_pages(pptx_path) if pptx_path.exists() else None
        checks.append((f"PPTX {stem}", slides == count and count > 0, f"{slides} slides"))

    images = list(ROOT.glob("0??_*/*/*.png")) + list(ROOT.glob("0??_*/images/*.png"))
    bad_images: list[str] = []
    for path in sorted(set(images)):
        try:
            with Image.open(path) as image:
                image.verify()
        except Exception as exc:  # validation should report every bad file
            bad_images.append(f"{path.relative_to(ROOT)} ({exc})")
    checks.append(("PNG evidence decodes", not bad_images, f"{len(set(images))} images; bad={bad_images}"))

    secret_findings = scan_secrets()
    checks.append(("No real credentials in deliverables", not secret_findings, json.dumps(secret_findings, ensure_ascii=False)))

    code, cleanup_output = command_output([
        "docker", "ps", "-a", "--filter", "name=^devtools-", "--format", "{{.Names}}",
    ])
    names = [line for line in cleanup_output.splitlines() if line.strip()]
    checks.append(("No devtools-* outer container remains", code == 0 and not names, ", ".join(names) or "none"))

    passed = sum(ok for _, ok, _ in checks)
    lines = [
        "# Validation Report",
        "",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"Result: **{passed}/{len(checks)} checks passed**",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for name, ok, detail in checks:
        safe_detail = detail.replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {safe_detail} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "A PASS verifies artifact shape, render/export parity, evidence file integrity, credential hygiene, and final outer-container cleanup. Runtime behavior for each LAB is recorded separately in that LAB's `validation.md`.",
        "",
    ])
    (ROOT / "VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{passed}/{len(checks)} checks passed")
    if passed != len(checks):
        for name, ok, detail in checks:
            if not ok:
                print(f"FAIL: {name}: {detail}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

