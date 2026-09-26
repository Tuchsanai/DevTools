#!/bin/bash
# Test harness (runs inside the isolated devtools-lab003-* container). Emulates the Jenkins UI steps via REST.
# Usage: jenkins_api.sh setup | build [k=v ...] | console N | result N
set -euo pipefail
J=http://localhost:8080; JAR=/tmp/jar
PASS=$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
crumb() { curl -s -c $JAR -b $JAR -u "admin:$PASS" "$J/crumbIssuer/api/json" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["crumbRequestField"]+":"+d["crumb"])'; }
post() { local c; c=$(crumb); curl -s -o /tmp/resp -w '%{http_code}' -c $JAR -b $JAR -u "admin:$PASS" -H "$c" "$@"; echo; }
esc() { python3 -c 'import sys,html;print(html.escape(sys.stdin.read()),end="")'; }
case "$1" in
setup)
  KEY=$(esc < /root/.ssh/jenkins_devtools)
  printf '<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey><scope>GLOBAL</scope><id>devtools-ssh</id><description>SSH key: Jenkins to devtools</description><username>root</username><privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource"><privateKey>%s</privateKey></privateKeySource></com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>' "$KEY" > /tmp/c1.xml
  printf '<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl><scope>GLOBAL</scope><id>dockerhub</id><description>Docker Hub access token</description><username>%s</username><password>%s</password></com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>' "$REG_USER" "$REG_PASS" > /tmp/c2.xml
  for f in /tmp/c1.xml /tmp/c2.xml; do post -X POST -H 'Content-Type: application/xml' --data-binary @$f "$J/credentials/store/system/domain/_/createCredentials"; done
  rm -f /tmp/c1.xml /tmp/c2.xml
  S=$(esc < /tmp/Jenkinsfile.test)
  printf '<flow-definition><definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition"><script>%s</script><sandbox>true</sandbox></definition></flow-definition>' "$S" > /tmp/job.xml
  post -X POST -H 'Content-Type: application/xml' --data-binary @/tmp/job.xml "$J/createItem?name=docker-build-push" ;;
build)
  shift; if [ $# -eq 0 ]; then post -X POST "$J/job/docker-build-push/build"; else args=(); for kv in "$@"; do args+=(--data-urlencode "$kv"); done; post -X POST "${args[@]}" "$J/job/docker-build-push/buildWithParameters"; fi ;;
wait)
  for i in $(seq 300); do r=$(curl -s -u "admin:$PASS" "$J/job/docker-build-push/$2/api/json?tree=result,building,duration" || true); echo "$r" | grep -q '"building":false' && { echo "$r"; exit 0; }; sleep 3; done; echo timeout; exit 1 ;;
recreate)
  post -X POST "$J/job/docker-build-push/doDelete"
  S=$(esc < /tmp/Jenkinsfile.test)
  printf '<flow-definition><definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition"><script>%s</script><sandbox>true</sandbox></definition></flow-definition>' "$S" > /tmp/job.xml
  post -X POST -H 'Content-Type: application/xml' --data-binary @/tmp/job.xml "$J/createItem?name=docker-build-push" ;;
params) curl -gs -u "admin:$PASS" "$J/job/docker-build-push/$2/api/json?tree=actions[parameters[name,value]]" ;;
console) curl -s -u "admin:$PASS" "$J/job/docker-build-push/$2/consoleText" ;;
stages) curl -s -u "admin:$PASS" "$J/job/docker-build-push/$2/wfapi/describe" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["status"],d["durationMillis"]);[print(s["name"],s["status"],s["durationMillis"]) for s in d["stages"]]' ;;
esac
