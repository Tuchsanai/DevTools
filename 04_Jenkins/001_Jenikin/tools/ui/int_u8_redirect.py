#!/usr/bin/env python3
"""Run a LAB UI helper while redirecting its fixed screenshot paths for U8."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


REDIRECT_ATTRS = {
    "lab3_job": ("PIPELINE_SHOT", "LOG_SHOT"),
    "lab3_hub_tags": ("TARGET",),
    "lab4_scm_repo": ("REPO_SHOT",),
    "lab4_scm_job": ("SCM_SHOT",),
    "lab4_scm_poll": ("POLL_SHOT",),
    "lab6_pipeline": ("TARGET",),
    "lab6_auto_refresh": ("TARGET",),
    "lab6_hub_tags": ("TARGET",),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=sorted(REDIRECT_ATTRS))
    parser.add_argument("--evidence-dir", default="logs/u8_evidence")
    args, forwarded = parser.parse_known_args()

    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    module = importlib.import_module(args.module)
    for attr in REDIRECT_ATTRS[args.module]:
        original = Path(getattr(module, attr))
        setattr(module, attr, evidence_dir / original.name)

    sys.argv = [args.module, *forwarded]
    module.main()
    print(f"[int] PASS: {args.module}; evidence={evidence_dir}")


if __name__ == "__main__":
    main()
