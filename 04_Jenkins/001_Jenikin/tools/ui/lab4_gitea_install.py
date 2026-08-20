#!/usr/bin/env python3
"""Prove the canonical Gitea web-installer path used by students."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from common import browser_page, log, require, run_main, screenshot, wait_visible


def fill_if_present(page, name: str, value: str) -> None:
    field = page.locator(f"[name='{name}']")
    if field.count() and field.first.is_visible():
        field.first.fill(value)
        log(f"filled {name}")


def app_ini(devtools_name: str, gitea_name: str) -> str:
    return subprocess.check_output(
        ["docker", "exec", devtools_name, "docker", "exec", gitea_name, "cat", "/data/gitea/conf/app.ini"],
        text=True,
    )


def flow(args: argparse.Namespace) -> None:
    shot_dir = Path(args.screenshot_dir)
    with browser_page(headless=not args.headed) as (_, _, _, page):
        page.goto(f"{args.base_url.rstrip('/')}/", wait_until="domcontentloaded", timeout=60_000)
        wait_visible(page.locator("form"), "Gitea initial configuration form", 60_000)

        db_select = page.locator("select[name='db_type']")
        if db_select.count():
            db_select.select_option("SQLite3")
        fill_if_present(page, "db_path", "/data/gitea/gitea.db")
        fill_if_present(page, "app_name", "Gitea")
        fill_if_present(page, "repo_root_path", "/data/git/repositories")
        fill_if_present(page, "domain", "localhost")
        fill_if_present(page, "ssh_port", "22")
        fill_if_present(page, "http_port", "3000")
        fill_if_present(page, "app_url", "http://localhost:3000/")
        fill_if_present(page, "log_root_path", "/data/gitea/log")
        disable_ssh = page.locator("input[name='disable_ssh']")
        if disable_ssh.count() and disable_ssh.first.is_visible() and not disable_ssh.first.is_checked():
            disable_ssh.first.check()
            log("checked disable_ssh")
        admin_settings = page.get_by_text("Administrator Account Settings", exact=False)
        if admin_settings.count() and admin_settings.first.is_visible():
            admin_settings.first.click()
            log("opened Administrator Account Settings")
        fill_if_present(page, "admin_name", "student")
        fill_if_present(page, "admin_passwd", "student2569")
        fill_if_present(page, "admin_confirm_passwd", "student2569")
        fill_if_present(page, "admin_email", "student@example.com")
        screenshot(page, shot_dir / "lab4_gitea_installer.png", "canonical Gitea installer values")

        page.get_by_role("button", name="Install Gitea").click()
        page.wait_for_url(lambda url: "/install" not in url, timeout=args.install_timeout * 1000)
        wait_visible(page.locator("body"), "Gitea page after installation", 120_000)
        screenshot(page, shot_dir / "lab4_gitea_installed.png", "Gitea after installation")

    config = app_ini(args.devtools_name, args.gitea_name)
    require("ROOT_URL = http://localhost:3000/" in config, "web installer wrote canonical ROOT_URL")
    require("DOMAIN = localhost" in config, "web installer wrote canonical DOMAIN")
    require("DISABLE_SSH = true" in config, "web installer disabled SSH")
    users = subprocess.check_output(
        [
            "docker", "exec", args.devtools_name, "docker", "exec", "-u", "git", args.gitea_name,
            "gitea", "admin", "user", "list", "--config", "/data/gitea/conf/app.ini",
        ],
        text=True,
    )
    require("student" in users and "student@example.com" in users, "student fixture exists after web install")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("GITEA_BASE_URL", "http://host.docker.internal:10300"))
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk0"))
    parser.add_argument("--gitea-name", default="gitea")
    parser.add_argument("--screenshot-dir", default="/tmp/u0-lab4-gitea")
    parser.add_argument("--install-timeout", type=int, default=600)
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_main(lambda: flow(arguments))
