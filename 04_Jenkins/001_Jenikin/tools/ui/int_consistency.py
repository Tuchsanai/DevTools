#!/usr/bin/env python3
"""Cross-check LAB READMEs, the slide deck, and the resolved stack for U8."""

from __future__ import annotations

import re
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


def report(ok: bool, message: str) -> bool:
    print(f"[{'PASS' if ok else 'FINDING'}] {message}")
    return ok


def main() -> int:
    readmes = {name: (ROOT / name / "README.md").read_text(encoding="utf-8") for name in LABS}
    checks: list[bool] = []

    required = {
        LABS[0]: (
            "--name devtools-jenkins", "--tmpfs /run", "-v jenkins-dind:/var/lib/docker",
            "-p 2222:22", "-p 8080:8080", "-p 3000:3000", "-p 8000:8000",
            "--name jenkins", "--network cicd-net", "-v jenkins_home:/var/jenkins_home",
        ),
        LABS[1]: ("devtools-jenkins", "http://localhost:8080", "admin2569"),
        LABS[2]: (
            "jenkins-docker:2569", "-v jenkins_home:/var/jenkins_home",
            "-v /var/run/docker.sock:/var/run/docker.sock", "dockerhub",
            "docker.io/<DOCKER_USER>/ci-demo", "<DOCKER_TOKEN>",
        ),
        LABS[3]: (
            "--name gitea", "--network cicd-net", "-v gitea_data:/data",
            "GITEA__webhook__ALLOWED_HOST_LIST=private", "GITEA__server__DISABLE_SSH=true",
            "http://localhost:3000/student/hello-ci.git",
            "http://gitea:3000/student/hello-ci.git", "* * * * *",
        ),
        LABS[4]: (
            "Generic Webhook Trigger 2.4.2", "cicd2569-hello",
            "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello",
        ),
        LABS[5]: (
            "dockerhub", "cicd2569-webapp", "http://gitea:3000/student/webapp.git",
            "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp",
            "http://webapp:8000", "<DOCKER_USER>/cicd-webapp",
        ),
    }
    for lab, needles in required.items():
        missing = [needle for needle in needles if needle not in readmes[lab]]
        checks.append(report(not missing, f"{lab}: canonical names/network/volumes/credentials/tokens/URLs"
                             + ("" if not missing else f"; missing={missing}")))

    code = "\n".join(
        block for text in readmes.values() for block in re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
    )
    forbidden = [
        token for token in ("host.docker.internal", "registry:2.8.3", "localhost:5000", "devtools-jk8")
        if token in code
    ]
    checks.append(report(not forbidden, "README code blocks contain no agent-only/obsolete runtime values"
                         + ("" if not forbidden else f"; found={forbidden}")))

    broken: list[str] = []
    link_re = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for lab, text in readmes.items():
        for target in link_re.findall(text):
            clean = target.strip().split("#", 1)[0]
            if not clean or re.match(r"^(?:https?://|mailto:)", clean):
                continue
            resolved = (ROOT / lab / clean).resolve()
            if not resolved.exists():
                broken.append(f"{lab}/README.md -> {target}")
    checks.append(report(not broken, f"relative README links resolve ({sum(len(link_re.findall(t)) for t in readmes.values())} links)"
                         + ("" if not broken else f"; broken={broken}")))

    deck_path = ROOT / "Jenkins_CICD_Docker_Slides.html"
    deck_html = deck_path.read_text(encoding="utf-8")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.goto(deck_path.as_uri(), wait_until="domcontentloaded")
        # Slides outside the active page are intentionally hidden. text_content()
        # extracts every slide's DOM text while still proving the deck opened in Chromium.
        deck_text = page.locator("body").text_content() or ""
        browser.close()
    checks.append(report(response is not None and response.ok, "deck opened headlessly and body text was extracted"))

    missing_labs = []
    for number, folder in enumerate(LABS, 1):
        if f"LAB {number}" not in deck_text or folder not in deck_html:
            missing_labs.append(f"LAB {number}/{folder}")
    checks.append(report(not missing_labs, "deck LAB numbers and folder links match all six real folders"
                         + ("" if not missing_labs else f"; missing={missing_labs}")))

    stack = (ROOT / "docs" / "STACK_RESOLVED.md").read_text(encoding="utf-8")
    versions = ("2.568.2", "1.27.2", "26.1.5", "2.4.2")
    version_drift = [v for v in versions if v not in stack or v not in deck_text]
    checks.append(report(not version_drift, "deck versions match STACK_RESOLVED (Jenkins/Gitea/Docker CLI/GWT)"
                         + ("" if not version_drift else f"; missing={version_drift}")))

    secret_pattern_count = 0
    scoped_files = [ROOT / "readme.md", ROOT / "docs" / "INTEGRATION.md", ROOT / "logs" / "U8.log"]
    scoped_files.extend(ROOT / lab / "README.md" for lab in LABS)
    for path in scoped_files:
        if path.exists():
            secret_pattern_count += path.read_bytes().count(b"dckr_" + b"pat_")
    checks.append(report(secret_pattern_count == 0, f"U8/report/README secret-pattern count={secret_pattern_count}"))

    passed = sum(checks)
    print(f"CONSISTENCY SUMMARY: {'PASS' if passed == len(checks) else 'FINDING'} ({passed}/{len(checks)})")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
