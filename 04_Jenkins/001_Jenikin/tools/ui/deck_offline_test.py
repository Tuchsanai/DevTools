#!/usr/bin/env python3
"""Compatibility entrypoint for the package-local Node Playwright deck gate."""
from __future__ import annotations
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    raise SystemExit(subprocess.run(["node", str(ROOT / "tools/ui/deck_offline_gate.cjs")], cwd=ROOT).returncode)
