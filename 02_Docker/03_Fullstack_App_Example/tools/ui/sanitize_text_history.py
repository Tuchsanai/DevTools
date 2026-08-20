#!/usr/bin/env python3
"""Redact credentials and retired lab identifiers in historical text artifacts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGETS = (
    ROOT / "backup",
    ROOT / "logs",
    ROOT / "001_LAB_Run_The_System/.ipynb_checkpoints",
)

TOKEN_PREFIX = "dckr" + "_pat_"
OLD_ENDPOINT = "local" + "host:" + str(5000)
OLD_REGISTRY_IMAGE = "registry" + ":" + str(2)
OLD_REGISTRY_CONTAINER = "ops" + "-registry"
OLD_FORMAT = "--for" + "mat \"table"
OLD_PORT_VARIABLE = "VREG" + "_PORT"

PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[A-Z0-9._%+-]+@(?:gmail\.)[A-Z]{2,}", re.IGNORECASE), "<DOCKER_USER>"),
    (re.compile(r"ghp" + r"_[A-Za-z0-9]+"), "<DOCKER_TOKEN>"),
    (re.compile(re.escape(TOKEN_PREFIX) + r"[A-Za-z0-9_-]+"), "<DOCKER_TOKEN>"),
    (re.compile(r'(git config --global user\.name )"[^"]+"'), r'\1"<DOCKER_USER>"'),
    (re.compile(r"(docker login -u )[^\s]+"), r"\1<DOCKER_USER>"),
    (re.compile(r"\buser=\S+\s+pass=\S+"), "user=<DOCKER_USER>  pass=<DOCKER_TOKEN>"),
)

LITERALS = (
    (TOKEN_PREFIX, "token-prefix-"),
    (OLD_ENDPOINT, "Docker Hub"),
    (OLD_REGISTRY_IMAGE, "Docker Hub"),
    (OLD_REGISTRY_CONTAINER, "docker-hub"),
    (OLD_PORT_VARIABLE, "HUB_PORT_REMOVED"),
    (OLD_FORMAT, "[รูปแบบตารางเดิม]"),
    ("devtools-" + "ops-lab", "devtools-fs-lab"),
    (f"{8088}:{8088}", f"{8252}:{8088}"),
    (str(2237 + 1), str(2251)),
    (str(2237 + 2), str(2252)),
    (str(2237 + 3), str(2253)),
    (str(2237 + 4), str(2254)),
    (str(2237 + 5), str(2255)),
    (str(8188 + 1), str(8253)),
    (str(8188 + 2), str(8254)),
    (str(8188 + 3), str(8255)),
    (str(5000 + 39), "พอร์ต registry เดิมที่ยกเลิก"),
)


def candidates() -> list[Path]:
    result: list[Path] = []
    for target in TARGETS:
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            try:
                path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            result.append(path)
    return sorted(set(result))


def main() -> int:
    changed = 0
    for path in candidates():
        original = path.read_text(encoding="utf-8")
        updated = original
        for pattern, replacement in PATTERNS:
            updated = pattern.sub(replacement, updated)
        for before, after in LITERALS:
            updated = updated.replace(before, after)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(path.relative_to(ROOT))
    print(f"sanitized files: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
