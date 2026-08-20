#!/usr/bin/env python3
"""Converge LAB 6 job contract, assert it, and capture the real Jenkins UI."""

from __future__ import annotations

import base64
import http.cookiejar
import html
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from common import browser_page, jenkins_login, log, require, run_main, wait_visible
from lab6_capture import masked_screenshot


JOB = "webapp-deploy"
TOKEN = "cicd2569-webapp"
ROOT = Path(__file__).resolve().parents[2]


def auth_headers() -> dict[str, str]:
    encoded = base64.b64encode(b"admin:admin2569").decode("ascii")
    return {"Authorization": f"Basic {encoded}"}


def request(base_url: str, path: str, *, method: str = "GET", body: bytes | None = None, headers: dict[str, str] | None = None, opener=None) -> tuple[int, bytes]:
    merged = auth_headers()
    merged.update(headers or {})
    req = urllib.request.Request(f"{base_url}{path}", data=body, method=method, headers=merged)
    try:
        response_context = (
            opener.open(req, timeout=60)
            if opener is not None
            else urllib.request.urlopen(req, timeout=60)
        )
        with response_context as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def config_xml(user: str) -> bytes:
    url = html.escape(f"https://github.com/{user}/webapp.git")
    return f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <actions/>
  <description>LAB 6 GitHub to Docker Hub deployment pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
      <triggers>
        <org.jenkinsci.plugins.gwt.GenericTrigger plugin="generic-webhook-trigger@2.4.2">
          <spec></spec>
          <genericVariables>
            <org.jenkinsci.plugins.gwt.GenericVariable>
              <expressionType>JSONPath</expressionType><key>ref</key><value>$.ref</value>
              <regexpFilter></regexpFilter><defaultValue></defaultValue>
            </org.jenkinsci.plugins.gwt.GenericVariable>
            <org.jenkinsci.plugins.gwt.GenericVariable>
              <expressionType>JSONPath</expressionType><key>after</key><value>$.after</value>
              <regexpFilter></regexpFilter><defaultValue></defaultValue>
            </org.jenkinsci.plugins.gwt.GenericVariable>
          </genericVariables>
          <regexpFilterText>$ref</regexpFilterText>
          <regexpFilterExpression>^refs/heads/main$</regexpFilterExpression>
          <printPostContent>false</printPostContent>
          <printContributedVariables>false</printContributedVariables>
          <causeString>GitHub push $after</causeString>
          <token>{TOKEN}</token>
          <tokenCredentialId></tokenCredentialId>
          <silentResponse>false</silentResponse>
          <overrideQuietPeriod>false</overrideQuietPeriod>
          <shouldNotFlattern>false</shouldNotFlattern>
          <allowSeveralTriggersPerBuild>false</allowSeveralTriggersPerBuild>
        </org.jenkinsci.plugins.gwt.GenericTrigger>
      </triggers>
    </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>{url}</url></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs>
      <branches><hudson.plugins.git.BranchSpec><name>*/main</name></hudson.plugins.git.BranchSpec></branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/><extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath><lightweight>true</lightweight>
  </definition>
  <triggers/><disabled>false</disabled>
</flow-definition>
""".encode("utf-8")


def converge(base_url: str, user: str) -> None:
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )
    status, crumb_raw = request(base_url, "/crumbIssuer/api/json", opener=opener)
    require(status == 200, "Jenkins crumb issuer is available")
    crumb = json.loads(crumb_raw)
    headers = {crumb["crumbRequestField"]: crumb["crumb"], "Content-Type": "application/xml"}
    status, _ = request(base_url, f"/job/{JOB}/config.xml")
    if status == 200:
        path = f"/job/{JOB}/config.xml"
        action = "updated"
    else:
        require(status == 404, "webapp-deploy is either present or absent")
        path = f"/createItem?name={urllib.parse.quote(JOB)}"
        action = "created"
    status, _ = request(
        base_url,
        path,
        method="POST",
        body=config_xml(user),
        headers=headers,
        opener=opener,
    )
    require(status in {200, 302}, f"Jenkins {action} webapp-deploy from the canonical contract (HTTP {status})")


def assert_xml(base_url: str, user: str) -> None:
    status, raw = request(base_url, f"/job/{JOB}/config.xml")
    require(status == 200, "saved webapp-deploy config.xml is readable")
    root = ET.fromstring(raw)
    definition = root.find("definition")
    scm = None if definition is None else definition.find("scm")
    trigger = root.find(".//org.jenkinsci.plugins.gwt.GenericTrigger")
    require(definition is not None and scm is not None and trigger is not None, "Pipeline SCM and one GWT trigger exist")
    assert definition is not None and scm is not None and trigger is not None
    require(scm.findtext("./userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url") == f"https://github.com/{user}/webapp.git", "SCM uses the canonical public GitHub URL")
    require(scm.findtext("./branches/hudson.plugins.git.BranchSpec/name") == "*/main", "SCM branch is */main")
    require(definition.findtext("scriptPath") == "Jenkinsfile", "SCM script path is Jenkinsfile")
    require(not root.findall(".//credentialsId") and not root.findall(".//hudson.triggers.SCMTrigger"), "SCM has no credentials and Poll SCM is off")
    variables = {item.findtext("key"): item.findtext("value") for item in trigger.findall("./genericVariables/*")}
    require(variables == {"ref": "$.ref", "after": "$.after"}, "GWT reads ref and after with JSONPath")
    require(trigger.findtext("token") == TOKEN, "GWT token is cicd2569-webapp")
    require(trigger.findtext("causeString") == "GitHub push $after", "GWT cause is GitHub push $after")
    require(trigger.findtext("regexpFilterText") == "$ref" and trigger.findtext("regexpFilterExpression") == "^refs/heads/main$", "GWT filter accepts only refs/heads/main")


def capture(page, user: str) -> None:
    masks = ((user, "<GITHUB_USER>"),)
    page.set_viewport_size({"width": 1440, "height": 1000})
    first_key = wait_visible(page.locator("input[name='_.key']").first, "first GWT JSONPath key")
    first_key.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -120)")
    masked_screenshot(
        page,
        ROOT / "slides_assets/lab6_s04a_gwt_parameters.png",
        "GWT ref and after JSONPath parameters",
        masks=masks,
    )

    token = wait_visible(page.locator("input[name='_.token']"), "GWT token field")
    token.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -150)")
    masked_screenshot(
        page,
        ROOT / "slides_assets/lab6_s04b_gwt_token_cause.png",
        "GWT token and GitHub SHA cause",
        masks=masks,
    )

    expression = wait_visible(page.locator("input[name='_.regexpFilterExpression']"), "GWT main-only expression")
    expression.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -180)")
    masked_screenshot(
        page,
        ROOT / "slides_assets/lab6_s04c_gwt_filter.png",
        "GWT main-only optional filter",
        masks=masks,
    )

    url = wait_visible(page.locator("input[name='_.url']").last, "SCM repository URL")
    url.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -260)")
    masked_screenshot(
        page,
        ROOT / "slides_assets/lab6_s05_job_scm.png",
        "canonical GitHub Pipeline from SCM",
        masks=masks,
        mask_locators=((url, "https://github.com/<GITHUB_USER>/webapp.git"),),
    )

    script_path = wait_visible(page.locator("input[name='_.scriptPath']"), "Jenkinsfile script path")
    script_path.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -260)")
    masked_screenshot(
        page,
        ROOT / "slides_assets/lab6_s05b_job_script_path.png",
        "main branch and Jenkinsfile script path",
        masks=masks,
    )


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080").rstrip("/")
    user = os.environ.get("GITHUB_USER", "")
    require(bool(user), "GITHUB_USER is set")
    converge(base_url, user)
    assert_xml(base_url, user)
    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")
        capture(page, user)


if __name__ == "__main__":
    run_main(main)
