#!/bin/bash
# Test harness v2 (runs inside isolated devtools-lab003-* container). Owner: yolo3.
# Auth is read from /root/.jauth (user:password, mode 600) — never echoed.
set -euo pipefail
J=http://localhost:8080; JAR=/tmp/jar; JOB=docker-build-push
AUTH=$(cat /root/.jauth 2>/dev/null || echo "admin:$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)")
cu() { curl -s -u "$AUTH" -c $JAR -b $JAR "$@"; }
crumb() { cu "$J/crumbIssuer/api/json" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["crumbRequestField"]+":"+d["crumb"])'; }
post() { local c; c=$(crumb); cu -o /tmp/resp -w '%{http_code}' -H "$c" "$@"; echo; }
esc() { python3 -c 'import sys,html;print(html.escape(sys.stdin.read()),end="")'; }
# parameter definitions mirror the Jenkinsfile so buildWithParameters works before the first run
pdef() { printf '<hudson.model.StringParameterDefinition><name>%s</name><defaultValue>%s</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition>' "$1" "$2"; }
jobxml() { S=$(esc < /tmp/Jenkinsfile); P="$(pdef GIT_URL https://github.com/Tuchsanai/DevTools.git)$(pdef GIT_REF main)$(pdef APP_SUBDIR 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop)$(pdef APP_VERSION 1.0.0)$(pdef TAG_PREFIX lab3)"
  printf '<flow-definition><description>LAB 3: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy</description><properties><hudson.model.ParametersDefinitionProperty><parameterDefinitions>%s</parameterDefinitions></hudson.model.ParametersDefinitionProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition"><script>%s</script><sandbox>true</sandbox></definition></flow-definition>' "$P" "$S" > /tmp/job.xml; }
case "$1" in
mkuser)   # env LAB_PASS; creates labadmin, finishes wizard
  G="import jenkins.model.*; import hudson.security.*; def j=Jenkins.get(); def r=j.getSecurityRealm(); if(!(r instanceof HudsonPrivateSecurityRealm)){r=new HudsonPrivateSecurityRealm(false); j.setSecurityRealm(r)}; r.createAccount('labadmin', '$LAB_PASS'); def s=new FullControlOnceLoggedInAuthorizationStrategy(); s.setAllowAnonymousRead(false); j.setAuthorizationStrategy(s); j.setInstallState(jenkins.install.InstallState.INITIAL_SETUP_COMPLETED); JenkinsLocationConfiguration.get().setUrl('http://localhost:8080/'); j.save(); println('ok')"
  (umask 077; printf '%s' "$G" > /tmp/g.groovy); c=$(crumb); cu -H "$c" --data-urlencode "script@/tmp/g.groovy" "$J/scriptText"; rm -f /tmp/g.groovy; echo ;;
creds)    # env REG_USER REG_PASS
  KEY=$(esc < /root/.ssh/jenkins_devtools)
  printf '<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey><scope>GLOBAL</scope><id>devtools-ssh</id><description>SSH key: Jenkins to devtools</description><username>root</username><privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource"><privateKey>%s</privateKey></privateKeySource></com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>' "$KEY" > /tmp/c1.xml
  printf '<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl><scope>GLOBAL</scope><id>dockerhub</id><description>Docker Hub access token</description><username>%s</username><password>%s</password></com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>' "$REG_USER" "$REG_PASS" > /tmp/c2.xml
  for f in /tmp/c1.xml /tmp/c2.xml; do post -X POST -H 'Content-Type: application/xml' --data-binary @$f "$J/credentials/store/system/domain/_/createCredentials"; done
  rm -f /tmp/c1.xml /tmp/c2.xml ;;
delcreds) for id in dockerhub devtools-ssh; do post -X POST "$J/credentials/store/system/domain/_/credential/$id/doDelete"; done ;;
job) jobxml; post -X POST -H 'Content-Type: application/xml; charset=UTF-8' --data-binary @/tmp/job.xml "$J/createItem?name=$JOB" ;;
updatejob) jobxml; post -X POST -H 'Content-Type: application/xml; charset=UTF-8' --data-binary @/tmp/job.xml "$J/job/$JOB/config.xml" ;;
build) # prints build number; fails unless POST=201 with queue Location and queue yields a build within 120 s
  shift; a=(); for kv in "$@"; do a+=(--data-urlencode "$kv"); done; c=$(crumb)
  code=$(cu -o /tmp/resp -D /tmp/hdr -w '%{http_code}' -H "$c" -X POST "${a[@]}" "$J/job/$JOB/buildWithParameters")
  Q=$(sed -n 's/^[Ll]ocation: *\(.*queue\/item\/[0-9]*\)\/*\r*$/\1/p' /tmp/hdr)
  [ "$code" = 201 ] && [ -n "$Q" ] || { echo "POST rejected: HTTP $code" >&2; head -c 300 /tmp/resp >&2; exit 1; }
  echo "queued: ${Q#$J}" >&2
  for i in $(seq 60); do n=$(cu "$Q/api/json" | python3 -c 'import json,sys;d=json.load(sys.stdin);e=d.get("executable");print(e["number"] if e else ("CANCELLED" if d.get("cancelled") else ""))' || true)
    [ "$n" = CANCELLED ] && { echo "queue item cancelled" >&2; exit 1; }
    [ -n "$n" ] && { echo "$n"; exit 0; }; sleep 2; done
  echo "queue item never started" >&2; exit 1 ;;
wait) for i in $(seq 300); do r=$(cu "$J/job/$JOB/$2/api/json?tree=result,building,duration" || true); echo "$r" | grep -q '"building":false' && { echo "$r"; exit 0; }; sleep 3; done; echo "timeout after 15 min" >&2; exit 1 ;;
params) cu -g "$J/job/$JOB/$2/api/json?tree=actions[parameters[name,value]]" ;;
console) cu "$J/job/$JOB/$2/consoleText" ;;
stages) docker exec jenkins cat /var/jenkins_home/jobs/$JOB/builds/$2/pipeline-graph-view-tree.v3.json | python3 -c 'import json,sys;d=json.load(sys.stdin);[print(s["name"],s["state"],s["totalDurationMillis"]) for s in d["stages"]]' ;;
whoami) cu "$J/whoAmI/api/json" ;;
esac
