#!/usr/bin/env python3
"""Create or assert the public hello-ci repository through the GitHub API."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request

from common import log, require, run_main


API = "https://api.github.com"
FILES = {"Jenkinsfile", "hello.sh", "expected.txt"}


def github_request(method: str, path: str, token: str, payload: dict | None = None) -> tuple[int, object]:
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
            "User-Agent": "cicd2569-lab4-helper",
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
    require(data.get("name") == "hello-ci", "repository name is hello-ci")
    require(data.get("private") is False, "hello-ci is public")


def assert_files(user: str, token: str, expected_empty: bool) -> None:
    status, data = github_request("GET", f"/repos/{user}/hello-ci/contents?ref=main", token)
    if expected_empty:
        require(status in {404, 409}, "new repository has no initialized main branch")
        return
    require(status == 200 and isinstance(data, list), "GitHub contents API returned branch main")
    assert isinstance(data, list)
    names = {str(item.get("name")) for item in data if isinstance(item, dict)}
    require(FILES <= names, "main lists Jenkinsfile, hello.sh, and expected.txt")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("create", "empty", "files", "verify"), required=True)
    args = parser.parse_args()
    user = os.environ.get("GITHUB_USER", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    require(bool(user), "GITHUB_USER is set")
    require(bool(token), "GITHUB_TOKEN is set without printing it")

    status, data = github_request("GET", f"/repos/{user}/hello-ci", token)
    if args.action == "create" and status == 404:
        status, data = github_request(
            "POST", "/user/repos", token, {"name": "hello-ci", "private": False, "auto_init": False}
        )
        require(status == 201, "GitHub API created hello-ci")
    else:
        require(status == 200, "GitHub API found hello-ci")
        if args.action == "create":
            log("hello-ci already exists; preserving it")

    assert_repo(data, user)
    if args.action in {"create", "empty"}:
        assert_files(user, token, expected_empty=True)
    elif args.action in {"files", "verify"}:
        assert_files(user, token, expected_empty=False)


if __name__ == "__main__":
    run_main(main)
