#!/usr/bin/env python3
"""Create/assert the LAB 6 public repo and webhook through GitHub's API."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.request

from common import log, require, run_main


API = "https://api.github.com"
REPO = "webapp"
REQUIRED_FILES = {".course-cicd2569", "Dockerfile", "Jenkinsfile", "app"}
MARKER = "course fixture — safe to delete"


def api(method: str, path: str, token: str, payload: dict | None = None) -> tuple[int, object]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{API}{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "cicd2569-lab6-helper",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raw = error.read()
        try:
            data: object = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {}
        return error.code, data


def assert_repo(data: object, user: str) -> None:
    require(isinstance(data, dict), "GitHub API returned a repository object")
    assert isinstance(data, dict)
    owner = str((data.get("owner") or {}).get("login", ""))
    require(owner.casefold() == user.casefold(), "repository owner matches GITHUB_USER")
    require(data.get("name") == REPO, "repository name is webapp")
    require(data.get("private") is False, "webapp is public")


def assert_files(user: str, token: str) -> None:
    status, listing = api("GET", f"/repos/{user}/{REPO}/contents?ref=main", token)
    require(status == 200 and isinstance(listing, list), "GitHub contents API returned branch main")
    assert isinstance(listing, list)
    names = {str(item.get("name")) for item in listing if isinstance(item, dict)}
    require(REQUIRED_FILES <= names, "main lists marker, app, Dockerfile, and Jenkinsfile")
    status, marker = api(
        "GET", f"/repos/{user}/{REPO}/contents/.course-cicd2569?ref=main", token
    )
    require(status == 200 and isinstance(marker, dict), "ownership marker is readable")
    assert isinstance(marker, dict)
    import base64

    content = base64.b64decode(str(marker.get("content", ""))).decode("utf-8")
    require(content == MARKER, "ownership marker has the canonical safe-to-delete value")


def relay_channel(devtools_name: str) -> str:
    raw = subprocess.check_output(
        ["docker", "exec", devtools_name, "docker", "inspect", "smee-webapp"],
        text=True,
    )
    args = json.loads(raw)[0]["Config"]["Cmd"]
    channel = args[args.index("--url") + 1]
    require(
        bool(re.fullmatch(r"https://smee\.io/[^/?#]+", channel)),
        "smee-webapp stores one valid channel URL",
    )
    return channel


def assert_hook(user: str, token: str, channel: str) -> None:
    status, hooks = api("GET", f"/repos/{user}/{REPO}/hooks?per_page=100", token)
    require(status == 200 and isinstance(hooks, list), "GitHub hook list is readable")
    assert isinstance(hooks, list)
    matches = [hook for hook in hooks if (hook.get("config") or {}).get("url") == channel]
    require(len(matches) == 1, "exactly one webapp hook points to smee-webapp")
    hook = matches[0]
    config = hook.get("config") or {}
    valid = hook.get("active") is True and hook.get("events") == ["push"]
    valid = valid and config.get("content_type") == "json"
    valid = valid and str(config.get("insecure_ssl")) == "0"
    require(valid, "hook is active, push-only, JSON, and SSL-verifying")
    status, deliveries = api(
        "GET", f"/repos/{user}/{REPO}/hooks/{hook['id']}/deliveries?per_page=20", token
    )
    require(status == 200 and isinstance(deliveries, list), "GitHub deliveries are readable")
    assert isinstance(deliveries, list)
    ping = next((item for item in deliveries if item.get("event") == "ping"), None)
    require(ping is not None, "automatic GitHub ping delivery exists")
    assert ping is not None
    require(200 <= int(ping.get("status_code") or 0) < 300, "automatic ping returned 2xx")
    status, delivery = api(
        "GET", f"/repos/{user}/{REPO}/hooks/{hook['id']}/deliveries/{ping['id']}", token
    )
    require(status == 200 and isinstance(delivery, dict), "full ping delivery is readable")
    assert isinstance(delivery, dict)
    headers = ((delivery.get("request") or {}).get("headers") or {})
    unsigned = not any(str(key).casefold() == "x-hub-signature-256" for key in headers)
    require(unsigned, "delivery request headers contain no X-Hub-Signature-256")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("create", "files", "hook"), required=True)
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk-lab"))
    args = parser.parse_args()
    user = os.environ.get("GITHUB_USER", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", user)), "GITHUB_USER has a valid login form")
    require(bool(token), "GITHUB_TOKEN is set without printing it")

    status, data = api("GET", f"/repos/{user}/{REPO}", token)
    if args.action == "create" and status == 404:
        status, data = api(
            "POST", "/user/repos", token, {"name": REPO, "private": False, "auto_init": False}
        )
        require(status == 201, "GitHub API created webapp")
        log("GitHub API replacement for + -> New repository completed")
    else:
        require(status == 200, "GitHub API found webapp")
        if args.action == "create":
            log("webapp already exists; preserving it")
    assert_repo(data, user)

    if args.action == "create":
        status, contents = api("GET", f"/repos/{user}/{REPO}/contents?ref=main", token)
        if status == 200:
            require(isinstance(contents, list), "existing main returns a file listing")
            assert_files(user, token)
            log("existing course-owned repository is already initialized")
        else:
            require(status in {404, 409}, "new repository has no initialized main branch")
    elif args.action == "files":
        assert_files(user, token)
    else:
        assert_files(user, token)
        assert_hook(user, token, relay_channel(args.devtools_name))


if __name__ == "__main__":
    run_main(main)
