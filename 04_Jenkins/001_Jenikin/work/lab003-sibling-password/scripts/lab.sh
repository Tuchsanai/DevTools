#!/bin/bash
# LAB 3 sibling-topology / SSH-password end-to-end harness. Owner: yolo3 (this session).
# Resources owned by a run (all named from one short random hash H, recorded in state.env):
#   containers devtools-lab003-H (alias devtools) and jenkins-lab003-H (alias jenkins),
#   network cicd-net-lab003-H, volume jenkins-lab003-H-home, host ports bound to 127.0.0.1 only.
# Never touches the learner's devtools / jenkins / cicd-net / jenkins_home and never prunes.
# Secrets: DOCKER_USER/DOCKER_TOKEN come from the process env and reach Jenkins only through the
# env of `docker exec` + stdin of curl. The test admin password lives in private/ (mode 600, git-ignored).
set -euo pipefail
W=$(cd "$(dirname "$0")/.." && pwd)
LAB=$(cd "$W/../../003_LAB_Docker_Build_Push" && pwd)
O=$W/out P=$W/private STATE=$W/state.env
mkdir -p "$O" "$W/run"
[ -f "$STATE" ] && . "$STATE"
J=http://localhost:8080

need_state() { [ -n "${H:-}" ] || { echo "no state.env: run '$0 up' first" >&2; exit 1; }; }
mapped() { # run a README host block verbatim with learner names/ports mapped onto this run
  ( cd "$W/run" && export DC JC NET VOL P_SSH P_JENKINS P_APP && bash --norc -c ". '$W/scripts/docker-map.sh'; . '$W/blocks/$1.sh'" )
}
jauth() { export JPASS; JPASS=$(cat "$P/jpass" 2>/dev/null || docker exec "$JC" cat /var/jenkins_home/secrets/initialAdminPassword); }
jc() { # curl inside the jenkins container; the admin password is fed with -K from env, never argv
  docker exec -i -e JPASS "$JC" bash -c 'exec curl -sS -K <(printf "user = \"admin:%s\"\n" "$JPASS") -c /tmp/h.jar -b /tmp/h.jar "$@"' _ "$@"
}
crumb() { jc "$J/crumbIssuer/api/json" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["crumbRequestField"]+":"+d["crumb"])'; }
jpost() { local c; c=$(crumb); jc -o /dev/null -w '%{http_code}\n' -H "$c" -X POST "$@"; }
wait_jenkins() { for i in $(seq 150); do [ "$(docker exec "$JC" curl -s -o /dev/null -w '%{http_code}' $J/login 2>/dev/null)" = 200 ] && return 0; sleep 2; done; echo "jenkins not ready" >&2; return 1; }
xml_esc() { python3 -c 'import sys,html;print(html.escape(sys.stdin.read(),quote=False),end="")'; }
pdef() { printf '<hudson.model.StringParameterDefinition><name>%s</name><defaultValue>%s</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition>' "$1" "$2"; }
jobxml() { # parameter definitions mirror the Jenkinsfile so buildWithParameters works before the first run
  local s p; s=$(xml_esc < "$LAB/Jenkinsfile")
  p="$(pdef GIT_URL https://github.com/Tuchsanai/DevTools.git)$(pdef GIT_REF main)$(pdef APP_SUBDIR 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop)$(pdef APP_VERSION 1.0.0)$(pdef TAG_PREFIX lab3)"
  printf '<flow-definition><description>LAB 3: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy</description><properties><hudson.model.ParametersDefinitionProperty><parameterDefinitions>%s</parameterDefinitions></hudson.model.ParametersDefinitionProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition"><script>%s</script><sandbox>true</sandbox></definition></flow-definition>' "$p" "$s"
}
sshcred() { # XML for devtools-ssh; password from env SSHCRED_PASS inside the container
  docker exec -i -e JPASS -e SSHCRED_PASS "$JC" bash -c 'c=$1; shift
    printf "<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl><scope>GLOBAL</scope><id>devtools-ssh</id><description>SSH password: Jenkins to devtools</description><username>root</username><usernameSecret>false</usernameSecret><password>%s</password></com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>" "$SSHCRED_PASS" |
    curl -sS -K <(printf "user = \"admin:%s\"\n" "$JPASS") -c /tmp/h.jar -b /tmp/h.jar -o /dev/null -w "%{http_code}\n" -H "$c" -H "Content-Type: application/xml" -X POST --data-binary @- "$@"' _ "$(crumb)" "$@"
}

case "${1:-}" in
up)
  [ -z "${H:-}" ] || { echo "state.env already exists for $H" >&2; exit 1; }
  running=$(docker ps -q --filter "name=^devtools-" | wc -l); echo "running devtools-* containers: $running"
  [ "$running" -lt 7 ] || { echo "7-container limit reached" >&2; exit 1; }
  H=$(head -c 16 /dev/urandom | sha256sum | cut -c1-6)
  used=$(docker ps -a --format '{{.Ports}}')
  free() { local p=$1; while grep -q ":$p->" <<<"$used"; do p=$((p+1)); [ "$p" = 2222 ] && p=2223; done; echo $p; }
  cat > "$STATE" <<EOF
H=$H
DC=devtools-lab003-$H
JC=jenkins-lab003-$H
NET=cicd-net-lab003-$H
VOL=jenkins-lab003-$H-home
P_SSH=$(free 2223)
P_JENKINS=$(free 18080)
P_APP=$(free 13000)
TAG_PREFIX=${TAG_PREFIX:-lab3-sibling-20260926}
EOF
  . "$STATE"; cat "$STATE"
  [ -z "$(docker ps -aq --filter "name=^($DC|$JC)\$")" ] || { echo "name clash" >&2; exit 1; }
  mapped host-setup > "$O/host-setup.txt" 2>&1 || true; cat "$O/host-setup.txt"
  docker inspect -f '{{.Name}} {{.Image}} {{.State.Status}}' "$DC" "$JC" > "$O/containers.txt"
  timeout 120 docker exec "$DC" bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null && docker info >/dev/null 2>&1; do sleep 1; done'
  for i in $(seq 90); do docker logs "$JC" 2>&1 | grep -q 'fully up' && break; sleep 2; done
  mapped host-check > "$O/host-check.txt" 2>&1; cat "$O/host-check.txt"
  date '+%Y-%m-%d %H:%M %Z' > "$O/date"
  docker exec "$JC" sh -c 'unzip -p /usr/share/jenkins/jenkins.war META-INF/MANIFEST.MF | grep ^Jenkins-Version' > "$O/jenkins_version" 2>/dev/null || true
  docker image inspect -f '{{index .RepoDigests 0}} {{.Id}}' tuchsanai/devtools:2569_1 jenkins/jenkins:lts-jdk21 > "$O/image_ids"
  ;;
wizard) # test-only stand-in for "Install suggested plugins" + "Create First Admin User" in the browser
  need_state
  mapped unlock | sed -E 's/^(.{16}).*/\1••••••••••••••••/' > "$O/unlock.txt"
  # same mechanism as the wizard's "Install suggested plugins": the controller's UpdateCenter (jenkins-plugin-cli
  # stalled on the huge plugin-versions.json in this sandbox), authenticated with the initial admin password
  jauth; c=$(crumb)
  printf '%s' 'def uc = jenkins.model.Jenkins.get().getUpdateCenter(); uc.updateAllSites()
def names = ["cloudbees-folder","antisamy-markup-formatter","build-timeout","credentials-binding","timestamper","ws-cleanup","workflow-aggregator","pipeline-graph-view","git","matrix-auth","mailer"]
def jobs = names.collect { uc.getPlugin(it).deploy(true) }
jobs.each { it.get() }
println("installed: " + names.join(" "))
println("failed: " + uc.getJobs().findAll { it instanceof hudson.model.UpdateCenter.DownloadJob && it.status instanceof hudson.model.UpdateCenter.DownloadJob.Failure }.collect { it.name })' |
    jc -H "$c" --data-urlencode script@- "$J/scriptText" > "$O/plugins.txt" 2>&1; cat "$O/plugins.txt"
  grep -q '^failed: \[\]$' "$O/plugins.txt" || exit 1
  docker restart "$JC" >/dev/null; wait_jenkins
  jauth
  umask 077; NEWPASS=$(head -c 24 /dev/urandom | base64 | tr -dc A-Za-z0-9 | cut -c1-20); export NEWPASS
  c=$(crumb)
  docker exec -i -e JPASS -e NEWPASS -e URL="http://localhost:$P_JENKINS/" "$JC" bash -c 'printf "%s" "import jenkins.model.*; import hudson.security.*; def j=Jenkins.get(); def r=j.getSecurityRealm(); if(!(r instanceof HudsonPrivateSecurityRealm)){r=new HudsonPrivateSecurityRealm(false); j.setSecurityRealm(r)}; r.createAccount(\"admin\", \"$NEWPASS\"); def u=hudson.model.User.getById(\"admin\", false); u.setFullName(\"Admin\"); def s=new FullControlOnceLoggedInAuthorizationStrategy(); s.setAllowAnonymousRead(false); j.setAuthorizationStrategy(s); j.setInstallState(jenkins.install.InstallState.INITIAL_SETUP_COMPLETED); JenkinsLocationConfiguration.get().setUrl(\"$URL\"); j.save(); println(\"security: \" + j.getSecurityRealm().getClass().getSimpleName() + \" / \" + j.getAuthorizationStrategy().getClass().getSimpleName())" |
    curl -sS -K <(printf "user = \"admin:%s\"\n" "$JPASS") -c /tmp/h.jar -b /tmp/h.jar -H "$1" --data-urlencode script@- '"$J"'/scriptText' _ "$c" | tee "$O/wizard.txt"
  printf '%s' "$NEWPASS" > "$P/jpass"
  python3 - "$P/browser-auth.json" <<PY
import json, os, sys
json.dump({"jenkins_url": "http://localhost:$P_JENKINS/", "username": "admin", "password": os.environ["NEWPASS"],
           "note": "test-only admin of jenkins-lab003-$H; deleted at cleanup"}, open(sys.argv[1], "w"), indent=2)
PY
  chmod 600 "$P/jpass" "$P/browser-auth.json"
  unset NEWPASS
  jauth; [ "$(jc -o /dev/null -w '%{http_code}' $J/whoAmI/api/json)" = 200 ] && echo "admin login OK"
  [ "$(docker exec "$JC" curl -s -o /dev/null -w '%{http_code}' $J/api/json)" = 403 ] && echo "anonymous denied (403)"
  ;;
hostblocks) # README steps 3–5 (sshpass, host-key pin, interactive SSH password test) run verbatim
  need_state
  mapped sshpass > "$O/sshpass.txt" 2>&1; cat "$O/sshpass.txt" | tail -5
  mapped pin-hostkey > "$O/pin-hostkey.txt" 2>&1; cat "$O/pin-hostkey.txt"
  docker exec "$JC" ls -ln /var/jenkins_home/.ssh > "$O/ssh-dir.txt"
  # negative control: without the pinned key, strict checking refuses before any password is sent
  docker exec "$JC" ssh -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/dev/null -o BatchMode=yes root@devtools true > "$O/unpinned.txt" 2>&1 || echo "exit=$?" >> "$O/unpinned.txt"
  LAB_SSH_PASS=passwd python3 "$W/scripts/pty_ssh.py" "$W/blocks/ssh-test.sh" "$JC" > "$O/ssh-test.txt"; cat "$O/ssh-test.txt"
  ;;
creds)
  need_state; jauth
  : "${DOCKER_USER:?}" "${DOCKER_TOKEN:?}"
  SSHCRED_PASS=passwd sshcred "$J/credentials/store/system/domain/_/createCredentials"
  c=$(crumb)
  docker exec -i -e JPASS -e DOCKER_USER -e DOCKER_TOKEN "$JC" bash -c '
    printf "<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl><scope>GLOBAL</scope><id>dockerhub</id><description>Docker Hub access token</description><username>%s</username><usernameSecret>false</usernameSecret><password>%s</password></com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>" "$DOCKER_USER" "$DOCKER_TOKEN" |
    curl -sS -K <(printf "user = \"admin:%s\"\n" "$JPASS") -c /tmp/h.jar -b /tmp/h.jar -o /dev/null -w "%{http_code}\n" -H "$1" -H "Content-Type: application/xml" -X POST --data-binary @- '"$J"'/credentials/store/system/domain/_/createCredentials' _ "$c"
  ;;
sshpw) # sshpw right|wrong — update devtools-ssh (wrong = random value, never stored)
  need_state; jauth
  if [ "$2" = right ]; then SSHCRED_PASS=passwd; else SSHCRED_PASS=$(head -c 12 /dev/urandom | base64 | tr -dc a-z0-9); fi
  export SSHCRED_PASS; sshcred "$J/credentials/store/system/domain/_/credential/devtools-ssh/config.xml"; unset SSHCRED_PASS
  ;;
job)
  need_state; jauth; c=$(crumb)
  jobxml | jc -o /dev/null -w '%{http_code}\n' -H "$c" -H 'Content-Type: application/xml; charset=UTF-8' -X POST --data-binary @- "$J/createItem?name=docker-build-push"
  ;;
build) # build LABEL [k=v ...] — prints build number, saves json/console/params/stages to out/
  need_state; jauth; L=$2; shift 2
  a=(); for kv in "$@"; do a+=(--data-urlencode "$kv"); done; c=$(crumb)
  hdr=$(jc -o /dev/null -D - -H "$c" -X POST "${a[@]}" "$J/job/docker-build-push/buildWithParameters")
  code=$(sed -n '1s/^HTTP[^ ]* \([0-9]*\).*/\1/p' <<<"$hdr"); Q=$(sed -n 's/^[Ll]ocation: *\(.*queue\/item\/[0-9]*\)\/*\r*$/\1/p' <<<"$hdr")
  [ "$code" = 201 ] && [ -n "$Q" ] || { echo "POST rejected: HTTP $code" >&2; exit 1; }
  n=""; for i in $(seq 60); do n=$(jc "$Q/api/json" | python3 -c 'import json,sys;d=json.load(sys.stdin);e=d.get("executable");print(e["number"] if e else ("CANCELLED" if d.get("cancelled") else ""))' || true)
    [ "$n" = CANCELLED ] && { echo "queue item cancelled" >&2; exit 1; }; [ -n "$n" ] && break; sleep 2; done
  [ -n "$n" ] || { echo "queue item never started" >&2; exit 1; }
  echo "$L → build #$n"; echo "$n" > "$O/$L.number"
  for i in $(seq 300); do r=$(jc "$J/job/docker-build-push/$n/api/json?tree=result,building,duration,timestamp" || true)
    grep -q '"building":false' <<<"$r" && break; sleep 3; done
  echo "$r" > "$O/b$n.json"; echo "$r"
  jc "$J/job/docker-build-push/$n/consoleText" > "$O/b$n.txt"
  jc -g "$J/job/docker-build-push/$n/api/json?tree=actions[parameters[name,value]]" > "$O/b$n.params"
  docker exec "$JC" cat "/var/jenkins_home/jobs/docker-build-push/builds/$n/pipeline-graph-view-tree.v3.json" |
    python3 -c 'import json,sys;d=json.load(sys.stdin);[print(s["name"],s["state"],s["totalDurationMillis"]) for s in d["stages"]]' | tee "$O/b$n.stages"
  ;;
web) # web LABEL — README check-web block + host-side reachability of the published app port
  need_state; mapped check-web > "$O/web-$2.txt" 2>&1; cat "$O/web-$2.txt"
  ;;
shell) need_state; shift; "$@" ;;   # run a command with state loaded (e.g. shell docker exec "$DC" ...)
cleanup)
  need_state
  mapped cleanup > "$O/cleanup-block.txt" 2>&1 || true
  docker rm -fv "$DC" "$JC" || true
  docker network rm "$NET" || true
  docker volume rm "$VOL" || true
  for f in "$P/jpass" "$P/browser-auth.json"; do [ -f "$f" ] && shred -u "$f"; done
  rm -rf "$W/run"
  echo "left over:"; docker ps -a --filter "name=lab003-$H" --format '{{.Names}}'; docker network ls -q --filter "name=$NET"; docker volume ls -q --filter "name=$VOL"
  python3 -c 'import json,sys; print(json.dumps(dict(l.split("=",1) for l in open(sys.argv[1]).read().split() if "=" in l), indent=2))' "$STATE" > "$W/run-state.json"
  mv "$STATE" "$W/state.$H.done.env"
  ;;
*) echo "usage: $0 up|wizard|hostblocks|creds|sshpw|job|build|web|cleanup" >&2; exit 2 ;;
esac
