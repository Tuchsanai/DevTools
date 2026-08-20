#!/usr/bin/env python3
"""Exercise the complete LAB 2 flow through the Jenkins classic UI."""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


INITIAL_SCRIPT = """pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        echo 'Checkout (simulated)'
        sleep 1
      }
    }
    stage('Build') {
      steps {
        echo 'Build'
        sleep 1
      }
    }
    stage('Test') {
      steps {
        echo 'Tests passed'
        sleep 1
      }
    }
  }
}
"""

ENVIRONMENT_SCRIPT = """pipeline {
  agent any

  environment {
    LAB_NAME = 'Declarative Pipeline'
  }

  stages {
    stage('Checkout') {
      steps {
        echo 'Checkout (simulated)'
        sleep 1
      }
    }
    stage('Build') {
      steps {
        echo "Building ${env.LAB_NAME}: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        sleep 1
      }
    }
    stage('Test') {
      steps {
        echo 'Tests passed'
        sleep 1
      }
    }
  }
}
"""

PARAMETERS_SCRIPT = """pipeline {
  agent any

  parameters {
    string(name: 'APP_ENV', defaultValue: 'dev', description: 'Environment to deploy')
  }

  environment {
    LAB_NAME = 'Declarative Pipeline'
  }

  stages {
    stage('Checkout') {
      steps {
        echo 'Checkout (simulated)'
        sleep 1
      }
    }
    stage('Build') {
      steps {
        echo "Building ${env.LAB_NAME}: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        echo "APP_ENV=${params.APP_ENV}"
        sleep 1
      }
    }
    stage('Test') {
      steps {
        echo 'Tests passed'
        sleep 1
      }
    }
  }
}
"""

POST_SCRIPT = PARAMETERS_SCRIPT[:-2] + """

  post {
    always {
      echo "Finished ${env.JOB_NAME} #${env.BUILD_NUMBER}"
    }
    success {
      echo 'Pipeline succeeded'
    }
  }
}
"""


def api_json(page, url: str) -> dict:
    response = page.request.get(url)
    require(response.ok, f"API {url} returned HTTP {response.status}")
    return response.json()


def last_build_number(page, base_url: str) -> int:
    data = api_json(page, f"{base_url}/job/first-pipeline/api/json?tree=lastBuild[number]")
    build = data.get("lastBuild")
    return 0 if build is None else int(build["number"])


def wait_for_build(page, base_url: str, baseline: int, timeout_seconds: int = 120) -> tuple[int, str]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        data = api_json(
            page,
            f"{base_url}/job/first-pipeline/api/json?tree=lastBuild[number,building,result]",
        )
        build = data.get("lastBuild") or {}
        number = int(build.get("number", 0))
        if number > baseline and not build.get("building", True):
            result = str(build.get("result"))
            require(result == "SUCCESS", f"first-pipeline #{number} finished SUCCESS")
            log(f"build #{number}: SUCCESS")
            return number, result
        page.wait_for_timeout(500)
    raise AssertionError(f"timed out waiting for build after #{baseline}")


def console_text(page, base_url: str, number: int) -> str:
    response = page.request.get(f"{base_url}/job/first-pipeline/{number}/consoleText")
    require(response.ok, f"console for build #{number} is readable")
    return response.text()


def set_pipeline_script(page, script: str) -> None:
    named_textarea = page.locator("textarea[name='_.script']")
    require(named_textarea.count() == 1, "Pipeline script field exists")
    ace_editor = page.locator(".ace_editor")
    code_mirror = page.locator(".CodeMirror")
    if ace_editor.count():
        page.wait_for_function("document.querySelector('.ace_editor')?.env?.editor")
        ace_editor.first.evaluate("(node, value) => node.env.editor.setValue(value, -1)", script)
        actual = ace_editor.first.evaluate("node => node.env.editor.getValue()")
    elif code_mirror.count():
        code_mirror.first.evaluate("(node, value) => node.CodeMirror.setValue(value)", script)
        actual = code_mirror.first.evaluate("node => node.CodeMirror.getValue()")
    else:
        named_textarea.fill(script, force=True)
        actual = named_textarea.input_value()
    require(
        actual == script,
        f"Pipeline editor contains the requested script exactly "
        f"(expected={len(script)} bytes, actual={len(actual)} bytes)",
    )


def capture_viewport(page, target: Path, description: str) -> None:
    """Capture the current real UI viewport at the frozen 1440 px width."""
    target.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(target), full_page=False)
    log(f"screenshot: {description} -> {target}")


def open_stages(page, base_url: str, number: int) -> None:
    page.goto(f"{base_url}/job/first-pipeline/{number}/stages/", wait_until="networkidle")
    wait_visible(page.locator("#console-pipeline-root"), "Pipeline Graph build-level Stages view")


def save_configuration(page, base_url: str, script: str) -> None:
    page.goto(f"{base_url}/job/first-pipeline/configure", wait_until="domcontentloaded")
    wait_visible(page.locator("form[name='config']"), "first-pipeline configuration form")
    set_pipeline_script(page, script)
    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(r"/job/first-pipeline/?$"))
    require(page.url.rstrip("/").endswith("/job/first-pipeline"), "configuration saved through UI")


def click_build_now(page, base_url: str) -> int:
    page.goto(f"{base_url}/job/first-pipeline/", wait_until="domcontentloaded")
    baseline = last_build_number(page, base_url)
    page.get_by_role("link", name=re.compile(r"Build Now", re.I)).click()
    number, _ = wait_for_build(page, base_url, baseline)
    return number


def parameter_page(page, base_url: str):
    page.goto(f"{base_url}/job/first-pipeline/", wait_until="domcontentloaded")
    link = page.get_by_role("link", name=re.compile(r"Build with Parameters", re.I))
    wait_visible(link, "Build with Parameters link")
    link.click()
    wait_visible(page.locator("form"), "parameter form")
    field = page.locator("input[name='value']")
    require(field.count() == 1, "APP_ENV has one string input")
    return field


def build_with_parameter(page, base_url: str, value: str) -> int:
    baseline = last_build_number(page, base_url)
    field = parameter_page(page, base_url)
    field.fill(value)
    page.get_by_role("button", name=re.compile(r"Build", re.I)).click()
    number, _ = wait_for_build(page, base_url, baseline)
    return number


def stage_statuses(page, base_url: str, number: int) -> dict[str, str]:
    # pipeline-graph-view is in the frozen suggested-plugin set. Its real stage
    # API backs the Stages UI; no extra stage API plugin is installed.
    data = api_json(page, f"{base_url}/job/first-pipeline/{number}/stages/tree")
    return {
        stage["name"]: str(stage["state"]).upper()
        for stage in data.get("data", {}).get("stages", [])
        if not stage.get("synthetic", False)
    }


def assert_saved_pipeline_script(page, base_url: str, expected: str) -> None:
    page.goto(f"{base_url}/job/first-pipeline/configure", wait_until="domcontentloaded")
    wait_visible(page.locator("form[name='config']"), "first-pipeline configuration form")
    textarea = page.locator("textarea[name='_.script']")
    require(textarea.count() == 1, "saved Pipeline script field exists")
    ace_editor = page.locator(".ace_editor")
    if ace_editor.count():
        page.wait_for_function("document.querySelector('.ace_editor')?.env?.editor")
        actual = ace_editor.first.evaluate("node => node.env.editor.getValue()")
    else:
        actual = textarea.input_value()
    require(actual == expected, "Jenkinsfile on disk matches the script saved in Jenkins exactly")


def create_job(page, base_url: str, screenshot_dir: Path) -> None:
    page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
    page.locator("input[name='name']").fill("first-pipeline")
    pipeline_choice = page.locator("label:has-text('Pipeline')").first
    wait_visible(pipeline_choice, "Pipeline job type")
    pipeline_choice.click()
    require(page.locator("input[name='name']").input_value() == "first-pipeline",
            "New Item contains the canonical job name")
    capture_viewport(
        page,
        screenshot_dir / "lab2_s01_new_item.png",
        "New Item with first-pipeline and Pipeline selected",
    )
    page.get_by_role("button", name="OK").click()
    page.wait_for_url(re.compile(r"/job/first-pipeline/configure"))
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)
    set_pipeline_script(page, INITIAL_SCRIPT)
    visible_editor = page.locator(".ace_editor:visible, .CodeMirror:visible")
    editor = visible_editor.first if visible_editor.count() else page.locator("textarea[name='_.script']")
    if page.locator(".ace_editor:visible").count():
        page.locator(".ace_editor:visible").first.evaluate(
            "node => { node.style.height = '520px'; node.env.editor.resize(); }"
        )
    editor.scroll_into_view_if_needed()
    capture_viewport(
        page,
        screenshot_dir / "lab2_s02_initial_script.png",
        "Pipeline script editor containing the initial three-stage script",
    )
    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(r"/job/first-pipeline/?$"))
    require(last_build_number(page, base_url) == 0, "new Pipeline job exists and has no build yet")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://host.docker.internal:12080")
    parser.add_argument(
        "--jenkinsfile",
        default=str(Path(__file__).resolve().parents[2] / "002_LAB_Declarative_Pipeline" / "Jenkinsfile"),
    )
    parser.add_argument(
        "--screenshot-dir",
        default=str(Path(__file__).resolve().parents[2] / "slides_assets"),
    )
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    final_script = Path(args.jenkinsfile).read_text(encoding="utf-8")
    screenshot_dir = Path(args.screenshot_dir)

    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        create_job(page, base_url, screenshot_dir)

        first = click_build_now(page, base_url)
        first_stages = stage_statuses(page, base_url, first)
        require(first_stages == {"Checkout": "SUCCESS", "Build": "SUCCESS", "Test": "SUCCESS"},
                "initial pipeline has three green stages")
        open_stages(page, base_url, first)
        first_graph_text = page.locator("body").inner_text()
        require("Deploy" not in first_graph_text, "initial Pipeline Graph contains only three stages")
        capture_viewport(page, screenshot_dir / "lab2_s03_first_graph.png",
                         "first build Pipeline Graph with three green stages")

        save_configuration(page, base_url, ENVIRONMENT_SCRIPT)
        env_build = click_build_now(page, base_url)
        env_console = console_text(page, base_url, env_build)
        require("Building Declarative Pipeline: first-pipeline #" in env_console,
                "environment and Jenkins BUILD_NUMBER/JOB_NAME appear in console")
        page.goto(f"{base_url}/job/first-pipeline/{env_build}/console", wait_until="domcontentloaded")
        environment_line = page.get_by_text(
            re.compile(r"Building Declarative Pipeline: first-pipeline #2"), exact=False
        ).first
        wait_visible(environment_line, "environment values in Console Output")
        environment_line.scroll_into_view_if_needed()
        capture_viewport(page, screenshot_dir / "lab2_s04_environment_console.png",
                         "Console Output showing LAB_NAME, JOB_NAME, and BUILD_NUMBER")

        save_configuration(page, base_url, PARAMETERS_SCRIPT)
        parameter_seed = click_build_now(page, base_url)
        require("APP_ENV=dev" in console_text(page, base_url, parameter_seed),
                "first build registers APP_ENV with default dev")
        page.goto(f"{base_url}/job/first-pipeline/configure", wait_until="domcontentloaded")
        parameter_config = page.get_by_text("This project is parameterized", exact=False).first
        wait_visible(parameter_config, "This project is parameterized configuration")
        require("APP_ENV" in page.locator("form[name='config']").inner_text(),
                "job configuration shows APP_ENV")
        parameter_config.scroll_into_view_if_needed()
        capture_viewport(page, screenshot_dir / "lab2_s05_parameters_config.png",
                         "job configuration showing This project is parameterized and APP_ENV")

        parameter_baseline = last_build_number(page, base_url)
        parameter_field = parameter_page(page, base_url)
        parameter_field.fill("staging")
        capture_viewport(page, screenshot_dir / "lab2_s06_build_parameters.png",
                         "Build with Parameters page with APP_ENV staging")
        page.get_by_role("button", name=re.compile(r"Build", re.I)).click()
        parameter_build, _ = wait_for_build(page, base_url, parameter_baseline)
        require("APP_ENV=staging" in console_text(page, base_url, parameter_build),
                "Build with Parameters passes APP_ENV=staging")

        save_configuration(page, base_url, POST_SCRIPT)
        post_build = build_with_parameter(page, base_url, "dev")
        post_console = console_text(page, base_url, post_build)
        require("Pipeline succeeded" in post_console and "Finished first-pipeline #" in post_console,
                "post always and success both ran")
        page.goto(f"{base_url}/job/first-pipeline/{post_build}/console", wait_until="domcontentloaded")
        post_line = page.get_by_text("Pipeline succeeded", exact=True).last
        wait_visible(post_line, "post success output in Console Output")
        post_line.scroll_into_view_if_needed()
        capture_viewport(page, screenshot_dir / "lab2_s07_post_console.png",
                         "Console Output showing post always and success messages")

        save_configuration(page, base_url, final_script)
        dev_build = build_with_parameter(page, base_url, "dev")
        dev_stages = stage_statuses(page, base_url, dev_build)
        require(dev_stages.get("Deploy") == "SKIPPED", "Deploy is skipped when APP_ENV=dev")
        open_stages(page, base_url, dev_build)
        dev_graph_text = page.locator("body").inner_text()
        require("Deploy" in dev_graph_text, "dev Pipeline Graph includes the skipped Deploy stage")
        capture_viewport(page, screenshot_dir / "lab2_s08_dev_graph.png",
                         "APP_ENV=dev Pipeline Graph with Deploy skipped")

        field = parameter_page(page, base_url)
        require(field.input_value() == "dev", "APP_ENV default value is dev")
        require("Environment to deploy" in page.locator("body").inner_text(), "APP_ENV description is visible")
        baseline = last_build_number(page, base_url)
        field.fill("prod")
        page.get_by_role("button", name=re.compile(r"Build", re.I)).click()
        prod_build, _ = wait_for_build(page, base_url, baseline)
        prod_stages = stage_statuses(page, base_url, prod_build)
        require(prod_stages == {
            "Checkout": "SUCCESS", "Build": "SUCCESS", "Test": "SUCCESS", "Deploy": "SUCCESS"
        }, "APP_ENV=prod runs all four stages successfully")
        require("Deploying to prod" in console_text(page, base_url, prod_build),
                "Deploy console confirms APP_ENV=prod")

        assert_saved_pipeline_script(page, base_url, final_script)

        # The build-level Stages page is the clearest pipeline-graph-view screen:
        # it focuses on one run and shows the complete connected four-stage graph.
        open_stages(page, base_url, prod_build)
        body = page.locator("body").inner_text()
        for stage in ("Checkout", "Build", "Test", "Deploy"):
            require(stage in body, f"Pipeline Graph shows {stage}")
        require(f"#{prod_build}" in body, f"Pipeline Graph shows successful build #{prod_build}")
        capture_viewport(page, screenshot_dir / "lab2_s09_prod_graph.png",
                         "APP_ENV=prod Pipeline Graph with four green stages")

        log(f"final build #{prod_build}; final UI script length={len(final_script)} bytes")


if __name__ == "__main__":
    run_main(main)
