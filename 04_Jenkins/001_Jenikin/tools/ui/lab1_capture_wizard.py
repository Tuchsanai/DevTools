#!/usr/bin/env python3
"""Run U0's LAB 1 wizard while capturing the completed admin form for U1R."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import lab1_wizard
from common import log, require, run_main


def capture_viewport(page, target: Path, description: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({"width": 1440, "height": 900})
    page.screenshot(path=str(target), full_page=False)
    log(f"screenshot: {description} -> {target}")


def flow(args: argparse.Namespace) -> None:
    admin_screenshot = Path(args.admin_screenshot)

    def create_admin_with_evidence(page) -> None:
        frame = page.frame(name="setup-first-user")
        require(frame is not None, "Create First Admin User iframe is present")
        fields = {
            "username": "admin",
            "password1": "admin2569",
            "password2": "admin2569",
            "fullname": "Admin",
            "email": "student@example.com",
        }
        for name, value in fields.items():
            locator = frame.locator(f"input[name='{name}']")
            if locator.count():
                locator.fill(value)
        require(
            frame.locator("input[name='password1']").get_attribute("type") == "password",
            "admin password is masked by the password input",
        )
        capture_viewport(page, admin_screenshot, "completed Create First Admin User form")
        page.get_by_role("button", name="Save and Continue").click()
        log("created Jenkins admin/admin2569")

    lab1_wizard.create_admin = create_admin_with_evidence
    wizard_args = argparse.Namespace(
        base_url=args.base_url,
        canonical_url="http://localhost:8080/",
        devtools_name=args.devtools_name,
        jenkins_name="jenkins",
        plugins_output=Path(args.plugins_output),
        screenshot_dir=args.wizard_screenshot_dir,
        plugin_timeout=args.plugin_timeout,
        headed=args.headed,
    )
    lab1_wizard.flow(wizard_args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:11080"),
    )
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk1"))
    parser.add_argument(
        "--admin-screenshot",
        default="slides_assets/lab1_s01_admin_user.png",
    )
    parser.add_argument("--plugins-output", default="/tmp/u1r-plugins.txt")
    parser.add_argument("--wizard-screenshot-dir", default="/tmp/u1r-wizard")
    parser.add_argument("--plugin-timeout", type=int, default=1800)
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_main(lambda: flow(arguments))
