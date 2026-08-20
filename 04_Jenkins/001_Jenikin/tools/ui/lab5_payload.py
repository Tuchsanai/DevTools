#!/usr/bin/env python3
"""Create/inspect the GitHub hook and correlate its delivery payload with Git."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

from common import log, require, run_main


JOB = "hello-ci-pipeline"


def api(method: str, path: str, payload: dict | None = None) -> tuple[int, object]:
    token = os.environ.get("GITHUB_TOKEN", "")
    require(bool(token), "GITHUB_TOKEN is set in the current shell")
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        raise AssertionError(f"GitHub API {method} {path} returned HTTP {exc.code}") from exc


def channel_from_relay(devtools_name: str) -> str:
    raw = subprocess.check_output(
        ["docker", "exec", devtools_name, "docker", "inspect", "smee-hello"], text=True
    )
    args = json.loads(raw)[0]["Config"]["Cmd"]
    channel = args[args.index("--url") + 1]
    require(bool(re.fullmatch(r"https://smee\.io/[^/?#]+", channel)), "relay stores one valid smee channel URL")
    return channel


def jenkins(base_url: str, path: str) -> dict:
    auth = base64.b64encode(b"admin:admin2569").decode()
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}", headers={"Authorization": f"Basic {auth}"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def last_build(base_url: str) -> int:
    item = jenkins(base_url, f"/job/{JOB}/api/json?tree=lastBuild[number]").get("lastBuild")
    return 0 if item is None else int(item["number"])


def settled_build_baseline(base_url: str, timeout_seconds: int) -> int:
    """Wait for an earlier local probe to leave the queue and finish."""
    deadline = time.monotonic() + timeout_seconds
    stable_number = None
    stable_since = None
    while time.monotonic() < deadline:
        queue = jenkins(base_url, "/queue/api/json?tree=items[task[name],cancelled]")
        queued = any(
            not item.get("cancelled", False) and (item.get("task") or {}).get("name") == JOB
            for item in queue.get("items", [])
        )
        build = jenkins(
            base_url, f"/job/{JOB}/api/json?tree=lastBuild[number,building]"
        ).get("lastBuild") or {}
        number = int(build.get("number", 0))
        idle = not queued and not build.get("building", False)
        if idle and number == stable_number:
            if stable_since is not None and time.monotonic() - stable_since >= 2:
                log(f"settled pre-ping baseline: build #{number}; queue empty")
                return number
        elif idle:
            stable_number = number
            stable_since = time.monotonic()
        else:
            stable_number = None
            stable_since = None
        time.sleep(1)
    raise AssertionError("timed out waiting for the local main probe to settle before ping baseline")


def find_hook(user: str, channel: str) -> dict | None:
    status, hooks = api("GET", f"/repos/{user}/hello-ci/hooks?per_page=100")
    require(status == 200 and isinstance(hooks, list), "GitHub hook list is readable")
    for hook in hooks:
        if (hook.get("config") or {}).get("url") == channel:
            return hook
    return None


def add_hook(args: argparse.Namespace, user: str, channel: str) -> None:
    require(find_hook(user, channel) is None, "fresh smee channel is not already registered")
    baseline = settled_build_baseline(args.jenkins_base_url, args.timeout)
    status, hook = api(
        "POST",
        f"/repos/{user}/hello-ci/hooks",
        {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": {"url": channel, "content_type": "json", "insecure_ssl": "0"},
        },
    )
    require(status == 201 and isinstance(hook, dict), "GitHub API created the push-only webhook")
    hook_id = int(hook["id"])
    log(f"GitHub API replacement for Settings -> Webhooks -> Add webhook: hook_id={hook_id}")

    deadline = time.monotonic() + args.timeout
    ping = None
    while time.monotonic() < deadline:
        status, deliveries = api(
            "GET", f"/repos/{user}/hello-ci/hooks/{hook_id}/deliveries?per_page=10"
        )
        require(status == 200 and isinstance(deliveries, list), "GitHub deliveries are readable")
        ping = next((item for item in deliveries if item.get("event") == "ping"), None)
        if ping and 200 <= int(ping.get("status_code") or 0) < 300:
            break
        time.sleep(1)
    require(ping is not None, "GitHub sent the automatic ping delivery")
    require(200 <= int(ping.get("status_code") or 0) < 300, "automatic ping delivery returned 2xx")
    time.sleep(5)
    require(last_build(args.jenkins_base_url) == baseline, "ping did not increase the Jenkins build number")
    log(f"ping acceptance: delivery 2xx; build remained #{baseline}")


def origin_sha(user: str) -> str:
    output = subprocess.check_output(
        ["git", "ls-remote", f"https://github.com/{user}/hello-ci.git", "refs/heads/main"],
        text=True,
        timeout=60,
    )
    sha = output.split()[0] if output.split() else ""
    require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "origin/main resolves to a full SHA")
    return sha


def verify_push(args: argparse.Namespace, user: str, channel: str) -> None:
    hook = find_hook(user, channel)
    require(hook is not None, "GitHub hook points to the running smee channel")
    assert hook is not None
    status, deliveries = api(
        "GET", f"/repos/{user}/hello-ci/hooks/{hook['id']}/deliveries?per_page=10"
    )
    require(status == 200 and isinstance(deliveries, list), "GitHub deliveries are readable")
    item = next((entry for entry in deliveries if entry.get("event") == "push"), None)
    require(item is not None, "latest delivery set contains a push")
    assert item is not None
    status, delivery = api(
        "GET", f"/repos/{user}/hello-ci/hooks/{hook['id']}/deliveries/{item['id']}"
    )
    require(status == 200 and isinstance(delivery, dict), "full push delivery is readable")
    payload = (delivery.get("request") or {}).get("payload") or {}
    sha = origin_sha(user)
    require(200 <= int(delivery.get("status_code") or 0) < 300, "push delivery returned 2xx")
    require(payload.get("ref") == "refs/heads/main", "payload ref is refs/heads/main")
    require(payload.get("after") == sha, "payload after equals origin/main")
    require((payload.get("head_commit") or {}).get("id") == sha, "head_commit.id equals origin/main")
    commits = payload.get("commits") or []
    require(any("hello.sh" in (item.get("modified") or []) for item in commits), "commits[].modified contains hello.sh")
    require(any(any(name.startswith("webhook-proof") for name in (item.get("added") or [])) for item in commits), "commits[].added contains a webhook proof file")
    log(f"correlation: delivery.after=head_commit.id=origin/main={sha[:12]}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("add-hook", "verify-push"), required=True)
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk-lab"))
    parser.add_argument("--jenkins-base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    user = os.environ.get("GITHUB_USER", "")
    require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", user)), "GITHUB_USER has a valid login form")
    channel = channel_from_relay(args.devtools_name)
    if args.action == "add-hook":
        add_hook(args, user, channel)
    else:
        verify_push(args, user, channel)


if __name__ == "__main__":
    run_main(main)
