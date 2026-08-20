#!/usr/bin/env python3
"""Cross-check deck code blocks and contracts against the frozen lab sources."""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Jenkins_CICD_Docker_Slides.html"
SOURCE = ROOT / "tools" / "slides_src.html"
PLAN = (ROOT / "docs" / "PLAN.md").read_text(encoding="utf-8")
READMES = {
    number: (ROOT / f"00{number}_LAB_{name}" / "README.md").read_text(encoding="utf-8")
    for number, name in {
        1: "Jenkins_On_Docker",
        2: "Declarative_Pipeline",
        3: "Docker_Build_Push",
        4: "Pipeline_From_Git",
        5: "Webhook_Trigger",
        6: "CICD_Capstone",
    }.items()
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[consistency][PASS] {message}")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def extract_code_blocks(deck: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for attrs, body in re.findall(r"<pre\b([^>]*)>(.*?)</pre>", deck, flags=re.I | re.S):
        key_match = re.search(r'data-canonical="([^"]+)"', attrs)
        key = key_match.group(1) if key_match else "uncategorized"
        body = re.sub(r"<[^>]+>", "", body)
        blocks.append((key, html.unescape(body)))
    return blocks


def main() -> int:
    deck = DECK.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    blocks = extract_code_blocks(deck)
    code_text = "\n".join(text for _, text in blocks)
    deck_text = html.unescape(re.sub(r"<[^>]+>", " ", deck))
    check(len(blocks) >= 10, f"extracted {len(blocks)} code blocks from final deck")

    outer = """docker run -dit --name devtools-jenkins --privileged \\
  --tmpfs /run -v jenkins-dind:/var/lib/docker \\
  -p 2222:22 -p 8080:8080 -p 3000:3000 -p 8000:8000 \\
  tuchsanai/devtools:2569_1"""
    check(normalize(outer) in normalize(READMES[1]), "outer docker run matches LAB 1 README")
    check(normalize(outer) in normalize(code_text), "outer docker run appears exactly in deck code")

    recreate = "docker rm -f jenkins && docker run -d --name jenkins --restart unless-stopped --network cicd-net -p 8080:8080 -u root -e JAVA_OPTS=-Djenkins.install.runSetupWizard=false -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins-docker:2569"
    check(normalize(recreate) in normalize(READMES[3]), "Jenkins recreate command matches LAB 3 README")
    check(normalize(recreate) in normalize(code_text), "Jenkins recreate command appears exactly in deck code")

    push_lines = [
        "withCredentials([usernamePassword(credentialsId: 'dockerhub'",
        "usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN'",
        "export DOCKER_CONFIG=$(mktemp -d)",
        "trap 'docker logout >/dev/null 2>&1; rm -rf \"$DOCKER_CONFIG\"' EXIT",
        'echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin',
        "docker build -t docker.io/$DOCKER_USER/ci-demo:$BUILD_NUMBER .",
        "docker push docker.io/$DOCKER_USER/ci-demo:$BUILD_NUMBER",
    ]
    jenkinsfile3 = (ROOT / "003_LAB_Docker_Build_Push" / "Jenkinsfile").read_text(encoding="utf-8")
    for line in push_lines:
        check(line in code_text and line in jenkinsfile3, f"push-block line matches LAB 3: {line[:54]}")

    required_contracts = [
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://gitea:3000/student/hello-ci.git",
        "http://gitea:3000/student/webapp.git",
        "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello",
        "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp",
        "http://webapp:8000",
        "docker.io/<DOCKER_USER>/cicd-webapp:BUILD_NUMBER",
        "docker.io/<DOCKER_USER>/cicd-webapp:latest",
    ]
    all_readmes = "\n".join(READMES.values())
    for contract in required_contracts:
        check(contract in deck_text, f"deck contains canonical URL/image: {contract}")
        source_ok = contract in all_readmes or contract in PLAN
        if contract.endswith("cicd-webapp:latest"):
            source_ok = "<DOCKER_USER>/cicd-webapp" in all_readmes and "latest" in all_readmes
        check(source_ok, f"canonical URL/image sourced by README/PLAN: {contract}")

    names = [
        "first-freestyle",
        "first-pipeline",
        "docker-build-push",
        "hello-ci-pipeline",
        "webapp-deploy",
        "student/hello-ci",
        "student/webapp",
        "dockerhub",
        "cicd2569-hello",
        "cicd2569-webapp",
        "* * * * *",
    ]
    for name in names:
        check(name in deck_text and name in all_readmes, f"job/repo/token/cron matches README: {name}")

    versions = ["2.568.2", "1.27.2", "2.4.2"]
    for version in versions:
        check(version in deck_text, f"locked version appears: {version}")

    folders = [
        "001_LAB_Jenkins_On_Docker",
        "002_LAB_Declarative_Pipeline",
        "003_LAB_Docker_Build_Push",
        "004_LAB_Pipeline_From_Git",
        "005_LAB_Webhook_Trigger",
        "006_LAB_CICD_Capstone",
    ]
    for folder in folders:
        check(folder in deck_text and (ROOT / folder).is_dir(), f"LAB landing folder is exact: {folder}")

    manifest = json.loads((ROOT / "slides_assets/motion/motion-manifest.json").read_text(encoding="utf-8"))
    for clip in manifest["clips"]:
        path = ROOT / "slides_assets" / "motion" / clip["file"]
        check(clip["compositionId"] in source, f"compositionId consumed from manifest: {clip['compositionId']}")
        check(hashlib.sha256(path.read_bytes()).hexdigest() == clip["sha256"], f"video sha256 matches manifest: {clip['file']}")

    check("dckr_pat_" not in deck, "no real Docker Hub token material embedded")
    check("<DOCKER_TOKEN>" in deck_text, "Docker Hub token is shown only as the required placeholder")
    check("docker.io/tuchsanai/" not in deck_text, "deck text uses Docker Hub placeholder, not test account")
    check("data-asset=" not in deck and "data-inline-svg=" not in deck, "no unresolved asset placeholders")

    # Explicitly protect the accepted H/1 correction from regressing.
    check("`* * * * *`" in READMES[4] and "ห้ามใช้ `H/1`" in READMES[4], "LAB 4 README carries corrected every-minute cron")
    check("* * * * *" in code_text, "deck Poll SCM code follows corrected README")

    print("[consistency] RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[consistency][FAIL] {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
