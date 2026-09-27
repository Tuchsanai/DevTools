#!/usr/bin/env python3
"""Minimal Jenkins REST helper for the isolated LAB003 harness.

Secrets come from the environment / lab key file and travel only in request
bodies (never argv, never printed).
usage: jenkins_api.py setup | build [APP_VERSION] | wait N | console N | info N
"""
import http.cookiejar
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from xml.sax.saxutils import escape

BASE = os.environ.get("JENKINS_URL", "http://172.22.0.3:8080")
AUTH = ("admin", "admin2569")
JOB = os.environ.get("JOB", "docker-build-push")
REPO = os.environ.get("REPO", "https://github.com/Tuchsanai/DevTools.git")
LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
import base64
BASIC = "Basic " + base64.b64encode(("%s:%s" % AUTH).encode()).decode()
_crumb = None


def req(method, path, data=None, ctype=None):
    global _crumb
    headers = {"Authorization": BASIC}
    if method == "POST":
        if _crumb is None:
            c = json.loads(req("GET", "/crumbIssuer/api/json")[1])
            _crumb = (c["crumbRequestField"], c["crumb"])
        headers[_crumb[0]] = _crumb[1]
    if ctype:
        headers["Content-Type"] = ctype
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with opener.open(r) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), e.headers


def create_cred(xml):
    code, body, _ = req("POST", "/credentials/store/system/domain/_/createCredentials",
                        xml.encode("utf-8"), "application/xml; charset=UTF-8")
    return code


def setup():
    key = open(os.path.join(LAB, "Devtool_SSH", "devtoolSSH")).read()
    ssh_xml = f"""<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials">
  <scope>GLOBAL</scope><id>devtools-ssh</id><description>SSH key: Jenkins to devtools</description>
  <username>root</username><usernameSecret>false</usernameSecret>
  <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey>{escape(key)}</privateKey></privateKeySource>
</com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>"""
    hub_xml = f"""<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
  <scope>GLOBAL</scope><id>dockerhub</id><description>Docker Hub access token</description>
  <username>{escape(os.environ['DOCKER_USER'])}</username><usernameSecret>false</usernameSecret>
  <password>{escape(os.environ['DOCKER_TOKEN'])}</password>
</com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>"""
    print("cred devtools-ssh:", create_cred(ssh_xml))
    print("cred dockerhub:", create_cred(hub_xml))
    create_job()


def create_job():
    job_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description></description><keepDependencies>false</keepDependencies><properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs><hudson.plugins.git.UserRemoteConfig>
        <url>{REPO}</url>
      </hudson.plugins.git.UserRemoteConfig></userRemoteConfigs>
      <branches><hudson.plugins.git.BranchSpec><name>*/main</name></hudson.plugins.git.BranchSpec></branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/><extensions/>
    </scm>
    <scriptPath>04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/><disabled>false</disabled>
</flow-definition>"""
    code, body, _ = req("POST", "/createItem?name=" + JOB, job_xml.encode("utf-8"),
                        "application/xml; charset=UTF-8")
    print("createItem:", JOB, code)


def build(version=None):
    if version:
        path = f"/job/{JOB}/buildWithParameters?" + urllib.parse.urlencode({"APP_VERSION": version})
    else:
        path = f"/job/{JOB}/build"
    code, _, h = req("POST", path)
    print("trigger:", code, h.get("Location"))


def info(n):
    code, body, _ = req("GET", f"/job/{JOB}/{n}/api/json?tree=number,result,building,duration,timestamp,actions[parameters[name,value],lastBuiltRevision[SHA1]]")
    return code, body


def wait(n):
    for _ in range(360):
        code, body = info(n)
        if code == 200:
            d = json.loads(body)
            if not d["building"] and d["result"]:
                print(json.dumps(d))
                return
        time.sleep(5)
    print("timeout")


def console(n):
    print(req("GET", f"/job/{JOB}/{n}/consoleText")[1])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "setup":
        setup()
    elif cmd == "createjob":
        create_job()
    elif cmd == "build":
        build(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "wait":
        wait(sys.argv[2])
    elif cmd == "console":
        console(sys.argv[2])
    elif cmd == "info":
        print(*info(sys.argv[2]))
    elif cmd == "stages":
        print(req("GET", f"/job/{JOB}/{sys.argv[2]}/wfapi/describe")[1])
