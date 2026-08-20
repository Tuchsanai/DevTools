#!/usr/bin/env python3
"""Cross-check LAB, deck, stack, links, and the Phase 5 active-tree guard."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
LABS = [
    "001_LAB_Jenkins_On_Docker",
    "002_LAB_Declarative_Pipeline",
    "003_LAB_Docker_Build_Push",
    "004_LAB_Pipeline_From_Git",
    "005_LAB_Webhook_Trigger",
    "006_LAB_CICD_Capstone",
]
RELAY_DIGEST = "sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33"
REQUIRED = {
    LABS[0]: (
        "--name devtools-jenkins",
        "--tmpfs /run",
        "-v jenkins-dind:/var/lib/docker",
        "-p 2222:22",
        "-p 8080:8080",
        "-p 8000:8000",
        "--name jenkins",
        "--network cicd-net",
        "-v jenkins_home:/var/jenkins_home",
    ),
    LABS[1]: ("devtools-jenkins", "http://localhost:8080", "admin2569"),
    LABS[2]: (
        "jenkins-docker:2569",
        "-v jenkins_home:/var/jenkins_home",
        "-v /var/run/docker.sock:/var/run/docker.sock",
        "dockerhub",
        "docker.io/<DOCKER_USER>/ci-demo",
        "<DOCKER_TOKEN>",
    ),
    LABS[3]: (
        "https://github.com/<GITHUB_USER>/hello-ci.git",
        "* * * * *",
        "<GITHUB_TOKEN>",
        "github_preflight.sh",
    ),
    LABS[4]: (
        "Generic Webhook Trigger 2.4.2",
        "cicd2569-hello",
        "refs/heads/main",
        "smee-hello",
        RELAY_DIGEST,
        "<SMEE_HELLO_URL>",
    ),
    LABS[5]: (
        "dockerhub",
        "cicd2569-webapp",
        "https://github.com/<GITHUB_USER>/webapp.git",
        "smee-webapp",
        "<SMEE_WEBAPP_URL>",
        "http://webapp:8000",
        "<DOCKER_USER>/cicd-webapp",
    ),
}
LOCKED_VERSIONS = ("2.568.2", "29.7.2", "2.4.2")
FORBIDDEN_TERMS = (
    "gi" + "tea",
    "localhost:" + "3000",
    "gi" + "tea_data",
    "student/" + "hello-ci",
    "student/" + "webapp",
)
MAX_TEXT_BYTES = 5 * 1024 * 1024
GATE_FILES = {
    "int_consistency.py",
    "deck_consistency_test.py",
    "deck_offline_test.py",
}
GENERATED_DIRS = {".git", ".ipynb_checkpoints", ".npm-cache", "__pycache__", "node_modules"}
SURFACE_DIRS = (
    *(Path(name) for name in LABS),
    Path("tools/bootstrap"),
    Path("tools/motion"),
    Path("tools/ui"),
)
SURFACE_FILES = (
    Path("readme.md"),
    Path("tools/slides_src.html"),
    Path("Jenkins_CICD_Docker_Slides.html"),
    Path("docs/LAB_TEMPLATE.md"),
)
# Internal/history trees (docs except the live template, prompt, logs, and backup)
# are intentionally out of scope for this student-facing surface guard.


def report(ok: bool, message: str) -> bool:
    print(f"[{'PASS' if ok else 'FINDING'}] {message}")
    return ok


def read_readmes(root: Path = ROOT) -> dict[str, str]:
    return {name: (root / name / "README.md").read_text(encoding="utf-8") for name in LABS}


def missing_contracts(readmes: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for lab, needles in REQUIRED.items():
        missing.extend(f"{lab}: {needle}" for needle in needles if needle not in readmes[lab])
    return missing


def version_drift(stack: str, deck_text: str) -> list[str]:
    return [version for version in LOCKED_VERSIONS if version not in stack or version not in deck_text]


def scan_forbidden(root: Path) -> tuple[list[str], str | None]:
    """Scan only learner-visible surfaces without relying on a host binary."""
    pattern = re.compile("|".join(re.escape(term) for term in FORBIDDEN_TERMS), re.I)
    candidates: dict[Path, tuple[bool, bool]] = {}
    errors: list[str] = []

    def add_file(path: Path, *, scan_name: bool = False, svg_only: bool = False) -> None:
        if path.is_file():
            candidates[path] = (scan_name, not svg_only or path.suffix.lower() == ".svg")

    for relative in SURFACE_FILES:
        add_file(root / relative)

    for relative in SURFACE_DIRS:
        base = root / relative
        if not base.is_dir():
            continue

        def on_walk_error(error: OSError) -> None:
            errors.append(str(error))

        for directory, subdirs, filenames in os.walk(base, onerror=on_walk_error):
            subdirs[:] = sorted(name for name in subdirs if name not in GENERATED_DIRS)
            for filename in sorted(filenames):
                if relative == Path("tools/ui") and filename in GATE_FILES:
                    continue
                add_file(Path(directory) / filename)

    assets = root / "slides_assets"
    if assets.is_dir():
        for directory, subdirs, filenames in os.walk(assets, onerror=lambda error: errors.append(str(error))):
            subdirs[:] = sorted(name for name in subdirs if name not in GENERATED_DIRS)
            for filename in sorted(filenames):
                add_file(Path(directory) / filename, scan_name=True, svg_only=True)

    findings: list[str] = []
    for path in sorted(candidates):
        scan_name, scan_content = candidates[path]
        relative = path.relative_to(root).as_posix()
        if scan_name and pattern.search(relative):
            findings.append(f"{relative}:0:{path.name}")
        if not scan_content:
            continue
        try:
            if path.stat().st_size > MAX_TEXT_BYTES:
                continue
            raw = path.read_bytes()
        except OSError as error:
            errors.append(f"{relative}: {error}")
            continue
        if b"\0" in raw[:8192]:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(
            f"{relative}:{line_number}:{line}"
            for line_number, line in enumerate(text.splitlines(), 1)
            if pattern.search(line)
        )
    return findings, "; ".join(errors) or None


def relative_link_findings(readmes: dict[str, str], root: Path = ROOT) -> tuple[list[str], int]:
    broken: list[str] = []
    link_count = 0
    link_re = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for lab, text in readmes.items():
        targets = link_re.findall(text)
        link_count += len(targets)
        for target in targets:
            clean = target.strip().split("#", 1)[0]
            if not clean or re.match(r"^(?:https?://|mailto:)", clean):
                continue
            resolved = (root / lab / clean).resolve()
            if not resolved.exists():
                broken.append(f"{lab}/README.md -> {target}")
    return broken, link_count


def deck_body_text(deck_path: Path) -> tuple[str, str, bool]:
    deck_html = deck_path.read_text(encoding="utf-8")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.goto(deck_path.as_uri(), wait_until="domcontentloaded")
        deck_text = page.locator("body").text_content() or ""
        browser.close()
    return deck_html, deck_text, response is not None and response.ok


def run_self_test() -> int:
    readmes = read_readmes()
    stack = (ROOT / "docs" / "STACK_RESOLVED.md").read_text(encoding="utf-8")
    deck_text = html.unescape((ROOT / "tools" / "slides_src.html").read_text(encoding="utf-8"))
    caught = 0

    with tempfile.TemporaryDirectory(prefix="int-consistency-self-test-") as temp_dir:
        fixture_root = Path(temp_dir)

        lab4_copy = fixture_root / "lab4.README.md"
        lab4_copy.write_text(readmes[LABS[3]], encoding="utf-8")
        mutated_readmes = dict(readmes)
        mutated_readmes[LABS[3]] = lab4_copy.read_text(encoding="utf-8").replace(REQUIRED[LABS[3]][0], "")
        if any(REQUIRED[LABS[3]][0] in finding for finding in missing_contracts(mutated_readmes)):
            report(True, "self-test mutation 1 rejected: removed LAB 4 GitHub URL")
            caught += 1
        else:
            report(False, "self-test mutation 1 escaped: removed LAB 4 GitHub URL")

        lab5_copy = fixture_root / "lab5.README.md"
        lab5_copy.write_text(readmes[LABS[4]], encoding="utf-8")
        mutated_readmes = dict(readmes)
        mutated_readmes[LABS[4]] = lab5_copy.read_text(encoding="utf-8").replace(RELAY_DIGEST, "")
        if any(RELAY_DIGEST in finding for finding in missing_contracts(mutated_readmes)):
            report(True, "self-test mutation 2 rejected: removed relay digest")
            caught += 1
        else:
            report(False, "self-test mutation 2 escaped: removed relay digest")

        stack_copy = fixture_root / "STACK_RESOLVED.md"
        shutil.copy2(ROOT / "docs" / "STACK_RESOLVED.md", stack_copy)
        stack_copy.write_text(stack_copy.read_text(encoding="utf-8").replace(LOCKED_VERSIONS[1], ""), encoding="utf-8")
        if LOCKED_VERSIONS[1] in version_drift(stack_copy.read_text(encoding="utf-8"), deck_text):
            report(True, "self-test mutation 3 rejected: removed Docker CLI version")
            caught += 1
        else:
            report(False, "self-test mutation 3 escaped: removed Docker CLI version")

        active = fixture_root / "readme.md"
        active.write_text(f"bad={FORBIDDEN_TERMS[0]}\n", encoding="utf-8")
        findings, error = scan_forbidden(fixture_root)
        if not error and any("readme.md:1" in finding for finding in findings):
            report(True, "self-test mutation 4 rejected: injected active-tree forbidden term")
            caught += 1
        else:
            report(False, f"self-test mutation 4 escaped: findings={findings}, error={error}")

    ok = caught == 4
    report(ok, f"mutation self-test caught {caught}/4 bad fixtures")
    print(f"CONSISTENCY SELF-TEST: {'PASS' if ok else 'FINDING'}")
    return 0 if ok else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="prove contract and guard mutations are rejected")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    readmes = read_readmes()
    checks: list[bool] = []

    missing = missing_contracts(readmes)
    checks.append(report(not missing, "LAB 1-6 canonical Phase 5 contracts are present" + ("" if not missing else f"; missing={missing}")))

    code = "\n".join(
        block for text in readmes.values() for block in re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
    )
    obsolete_runtime = [
        token for token in ("host.docker.internal", "registry:2.8.3", "localhost:5000", "devtools-jk8")
        if token in code
    ]
    checks.append(report(not obsolete_runtime, "README code blocks contain no agent-only/obsolete runtime values"
                         + ("" if not obsolete_runtime else f"; found={obsolete_runtime}")))

    broken, link_count = relative_link_findings(readmes)
    checks.append(report(not broken, f"relative README links resolve ({link_count} links)"
                         + ("" if not broken else f"; broken={broken}")))

    deck_path = ROOT / "Jenkins_CICD_Docker_Slides.html"
    deck_html, deck_text, deck_ok = deck_body_text(deck_path)
    checks.append(report(deck_ok, "deck opened headlessly and body text was extracted"))

    missing_labs = []
    for number, folder in enumerate(LABS, 1):
        if f"LAB {number}" not in deck_text or folder not in deck_html:
            missing_labs.append(f"LAB {number}/{folder}")
    checks.append(report(not missing_labs, "deck LAB numbers and folder links match all six real folders"
                         + ("" if not missing_labs else f"; missing={missing_labs}")))

    stack = (ROOT / "docs" / "STACK_RESOLVED.md").read_text(encoding="utf-8")
    drift = version_drift(stack, deck_text)
    checks.append(report(not drift, "deck versions match STACK_RESOLVED (Jenkins/Docker CLI/GWT)"
                         + ("" if not drift else f"; missing={drift}")))

    secret_pattern_count = 0
    scoped_files = [ROOT / "readme.md", ROOT / "docs" / "INTEGRATION.md"]
    scoped_files.extend(ROOT / lab / "README.md" for lab in LABS)
    for path in scoped_files:
        if path.exists():
            secret_pattern_count += path.read_bytes().count(b"dckr_" + b"pat_")
    checks.append(report(secret_pattern_count == 0, f"README/integration secret-pattern count={secret_pattern_count}"))

    forbidden_findings, scan_error = scan_forbidden(ROOT)
    for finding in forbidden_findings:
        print(f"[SURFACE-ZERO][FINDING] {finding}")
    checks.append(report(scan_error is None and not forbidden_findings,
                         "student-facing surfaces contain no legacy SCM/URL/volume/repo terms"
                         + (f"; error={scan_error}" if scan_error else f"; matches={len(forbidden_findings)}")))

    passed = sum(checks)
    print(f"CONSISTENCY SUMMARY: {'PASS' if passed == len(checks) else 'FINDING'} ({passed}/{len(checks)})")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
