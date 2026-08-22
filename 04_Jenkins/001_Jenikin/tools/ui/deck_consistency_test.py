#!/usr/bin/env python3
"""Cross-check the generated deck against the Phase 5 GitHub contracts."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Jenkins_CICD_Docker_Slides.html"
SOURCE = ROOT / "tools" / "slides_src.html"
PLAN = (ROOT / "docs" / "PLAN_P5_GITHUB.md").read_text(encoding="utf-8")
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

REQUIRED_CONTRACTS = (
    "https://github.com/<GITHUB_USER>/hello-ci.git",
    "https://github.com/<GITHUB_USER>/webapp.git",
    "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello",
    "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp",
    "https://smee.io/",
)
REQUIRED_NAMES = (
    "<GITHUB_USER>/hello-ci",
    "<GITHUB_USER>/webapp",
    "hello-ci-pipeline",
    "webapp-deploy",
    "cicd2569-hello",
    "cicd2569-webapp",
    "* * * * *",
    "refs/heads/main",
)
LOCKED_VERSIONS = ("2.568.2", "2.4.2", "29.7.2")
FORBIDDEN_DECK_TEXT = ("localhost:" + "3000",)


def check(condition: bool, message: str, *, emit: bool = True) -> None:
    if not condition:
        raise AssertionError(message)
    if emit:
        print(f"[consistency][PASS] {message}")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def visible_text(document: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", document))


def extract_code_blocks(deck: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for attrs, body in re.findall(r"<pre\b([^>]*)>(.*?)</pre>", deck, flags=re.I | re.S):
        key_match = re.search(r'data-canonical="([^"]+)"', attrs)
        key = key_match.group(1) if key_match else "uncategorized"
        body = re.sub(r"<[^>]+>", "", body)
        blocks.append((key, html.unescape(body)))
    return blocks


def validate_v3_contracts(
    deck_document: str,
    source_document: str,
    readmes: dict[int, str],
    plan: str,
    *,
    emit: bool = True,
) -> None:
    deck_text = visible_text(deck_document)
    source_text = visible_text(source_document)
    all_readmes = "\n".join(readmes.values())
    canonical_sources = "\n".join((all_readmes, source_text, plan))

    for contract in REQUIRED_CONTRACTS:
        check(contract in deck_text, f"deck contains Phase 5 contract: {contract}", emit=emit)
        check(
            contract in canonical_sources,
            f"Phase 5 contract is sourced by README/slide source/plan: {contract}",
            emit=emit,
        )

    for name in REQUIRED_NAMES:
        check(name in deck_text, f"deck contains canonical repo/job/token/cron/ref: {name}", emit=emit)
        check(name in all_readmes, f"README set contains canonical repo/job/token/cron/ref: {name}", emit=emit)

    for version in LOCKED_VERSIONS:
        check(version in deck_text, f"locked version appears in deck: {version}", emit=emit)

    for forbidden in FORBIDDEN_DECK_TEXT:
        check(forbidden not in deck_text, f"deck excludes retired URL token: {forbidden}", emit=emit)


def validate_full_deck(
    deck: str,
    source: str,
    readmes: dict[int, str],
    plan: str,
    *,
    emit: bool = True,
) -> None:
    blocks = extract_code_blocks(deck)
    code_text = "\n".join(text for _, text in blocks)
    deck_text = visible_text(deck)
    check(len(blocks) >= 10, f"extracted {len(blocks)} code blocks from final deck", emit=emit)

    outer = """docker run -dit --name devtools-jenkins --privileged \\
  --tmpfs /run -v jenkins-dind:/var/lib/docker \\
  -p 2222:22 -p 8080:8080 -p 8000:8000 \\
  tuchsanai/devtools:2569_1"""
    check(normalize(outer) in normalize(readmes[1]), "outer docker run matches LAB 1 README", emit=emit)
    check(normalize(outer) in normalize(code_text), "outer docker run appears exactly in deck code", emit=emit)

    recreate = "docker rm -f jenkins\ndocker run -d --name jenkins --restart unless-stopped --network cicd-net -p 8080:8080 -u root -e JAVA_OPTS=-Djenkins.install.runSetupWizard=false -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins-docker:2569"
    check(normalize(recreate) in normalize(readmes[3]), "Jenkins recreate commands match LAB 3 README", emit=emit)
    check(normalize(recreate) in normalize(code_text), "Jenkins recreate commands appear exactly in deck code", emit=emit)

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
        check(line in code_text and line in jenkinsfile3, f"push-block line matches LAB 3: {line[:54]}", emit=emit)

    validate_v3_contracts(deck, source, readmes, plan, emit=emit)

    by_key = {key: text for key, text in blocks}
    webhook_contract = by_key.get("webhook-urls", "")
    capstone_contract = by_key.get("capstone-contract", "")
    for label, contract in (("hello-ci", webhook_contract), ("webapp", capstone_contract)):
        check("Post content: ref=$.ref, after=$.after" in contract,
              f"{label} slide contract contains ref/after JSONPath", emit=emit)
        check("Cause: GitHub push $after" in contract,
              f"{label} slide contract contains exact SHA-bearing cause", emit=emit)

    folders = [
        "001_LAB_Jenkins_On_Docker",
        "002_LAB_Declarative_Pipeline",
        "003_LAB_Docker_Build_Push",
        "004_LAB_Pipeline_From_Git",
        "005_LAB_Webhook_Trigger",
        "006_LAB_CICD_Capstone",
    ]
    for folder in folders:
        check(folder in deck_text and (ROOT / folder).is_dir(), f"LAB landing folder is exact: {folder}", emit=emit)

    manifest = json.loads((ROOT / "slides_assets/motion/motion-manifest.json").read_text(encoding="utf-8"))
    # The deck may use a subset of the rendered clips, but every clip it *does*
    # use must be the exact bytes the manifest vouches for.
    used = {clip["compositionId"] for clip in manifest["clips"] if clip["compositionId"] in source}
    check(bool(used), f"deck consumes at least one manifest clip: {sorted(used)}", emit=emit)
    for clip in manifest["clips"]:
        if clip["compositionId"] not in used:
            continue
        path = ROOT / "slides_assets" / "motion" / clip["file"]
        check(
            hashlib.sha256(path.read_bytes()).hexdigest() == clip["sha256"],
            f"video sha256 matches manifest: {clip['file']}",
            emit=emit,
        )
    declared = set(re.findall(r'data-composition="([^"]+)"', source))
    check(
        declared <= {clip["compositionId"] for clip in manifest["clips"]},
        f"every deck video is declared by the motion manifest; extra={sorted(declared - used)}",
        emit=emit,
    )

    check("dckr_pat_" not in deck, "no real Docker Hub token material embedded", emit=emit)
    check("<DOCKER_TOKEN>" in deck_text, "Docker Hub token is shown only as the required placeholder", emit=emit)
    check("docker.io/tuchsanai/" not in deck_text, "deck text uses Docker Hub placeholder, not test account", emit=emit)
    check("data-asset=" not in deck and "data-inline-svg=" not in deck, "no unresolved asset placeholders", emit=emit)

    check(
        "`* * * * *`" in readmes[4] and "ห้ามใช้ `H/1`" in readmes[4],
        "LAB 4 README carries corrected every-minute cron and H/1 guard",
        emit=emit,
    )
    check("* * * * *" in code_text, "deck Poll SCM code follows corrected README", emit=emit)


def synthetic_fixture() -> tuple[str, str, dict[int, str], str]:
    contracts = "\n".join(REQUIRED_CONTRACTS)
    names = "\n".join(REQUIRED_NAMES)
    versions = "\n".join(LOCKED_VERSIONS)
    deck = f"<html><body>{html.escape(contracts)}\n{html.escape(names)}\n{versions}</body></html>"
    source = deck
    readmes = {number: f"{contracts}\n{names}\n{versions}" for number in range(1, 7)}
    return deck, source, readmes, f"{contracts}\n{names}\n{versions}"


def run_self_test() -> int:
    base_deck, base_source, base_readmes, base_plan = synthetic_fixture()
    cases = (
        ("remove GitHub hello-ci contract", REQUIRED_CONTRACTS[0], "Phase 5 contract"),
        ("remove Docker CLI version", LOCKED_VERSIONS[2], "locked version"),
        ("inject retired deck URL", None, "deck excludes retired URL token"),
    )
    caught = 0
    with tempfile.TemporaryDirectory(prefix="deck-consistency-self-test-") as temp_dir:
        fixture = Path(temp_dir) / "deck.html"
        for index, (label, removed, expected) in enumerate(cases, 1):
            fixture.write_text(base_deck, encoding="utf-8")
            shutil.copy2(fixture, Path(temp_dir) / f"case-{index}.html")
            mutated = fixture.read_text(encoding="utf-8")
            if removed is None:
                mutated = mutated.replace("</body>", f" {FORBIDDEN_DECK_TEXT[0]}</body>")
            else:
                mutated = mutated.replace(html.escape(removed), "")
            fixture.write_text(mutated, encoding="utf-8")
            try:
                validate_v3_contracts(mutated, base_source, base_readmes, base_plan, emit=False)
            except AssertionError as exc:
                check(expected in str(exc), f"self-test mutation {index} rejected for expected reason: {label}")
                caught += 1
            else:
                print(f"[consistency][FAIL] self-test mutation escaped detection: {label}", file=sys.stderr)
    check(caught == len(cases), f"self-test caught all {caught}/{len(cases)} bad fixtures")
    print("[consistency][SELF-TEST] RESULT: PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="prove mutations are rejected")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    validate_full_deck(
        DECK.read_text(encoding="utf-8"),
        SOURCE.read_text(encoding="utf-8"),
        READMES,
        PLAN,
    )
    print("[consistency] RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[consistency][FAIL] {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
