#!/usr/bin/env bash
# Owned, isolated LAB 3 environment for README reorder screenshots/validation.
# Every resource is named devtools-l3reorder-<hash>-*. Nothing else is touched.
set -euo pipefail
W=$(cd "$(dirname "$0")/.." && pwd)
H=$(cat "$W/hash")
P=devtools-l3reorder-$H
NET=$P-net; JC=$P-jenkins; DT=$P-dt; VOL=$P-jhome
BIND=127.0.0.1         # host-side loopback bind only
HX=host.docker.internal # how this agent container reaches host loopback-published ports
JPORT=${JPORT:-18480}  # host port -> jenkins:8080 (host loopback only)
APORT=${APORT:-13080}  # host port -> dt:3000 (shop, host loopback only)
LOG=$W/evidence/setup-env.log
log(){ echo "[$(date +%T)] $*" | tee -a "$LOG"; }

N=$(docker ps -q --filter "name=^devtools-" --filter status=running | wc -l)
log "running devtools- containers before: $N"; [ "$N" -le 4 ] || { log "quota would be exceeded"; exit 1; }

# admin password: random, file only (0600), never printed
PWF=$W/secrets/jenkins-admin-password
[ -s "$PWF" ] || { umask 077; head -c 18 /dev/urandom | base64 | tr -d '/+=' > "$PWF"; }
chmod 600 "$PWF"

docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET" >/dev/null
docker volume inspect "$VOL" >/dev/null 2>&1 || docker volume create "$VOL" >/dev/null
log "network $NET, volume $VOL ready"

if ! docker container inspect "$DT" >/dev/null 2>&1; then
  docker run -dit --name "$DT" --network "$NET" --network-alias devtools --privileged --tmpfs /run \
    -p $BIND:$APORT:3000 tuchsanai/devtools:2569_1 >/dev/null
fi
log "dt image: $(docker inspect -f '{{.Image}}' "$DT")"

# plugins = Jenkins "Install suggested plugins" set (+ deps), installed into the owned volume
if ! docker run --rm -v "$VOL":/var/jenkins_home jenkins/jenkins:lts-jdk21 test -d /var/jenkins_home/plugins/workflow-aggregator 2>/dev/null; then
  log "installing suggested plugins"
  docker run --rm --name $P-plugins -v "$VOL":/var/jenkins_home jenkins/jenkins:lts-jdk21 \
    jenkins-plugin-cli -d /var/jenkins_home/plugins --plugins \
    cloudbees-folder antisamy-markup-formatter build-timeout credentials-binding timestamper ws-cleanup \
    ant gradle workflow-aggregator github-branch-source pipeline-github-lib pipeline-graph-view git \
    ssh-slaves matrix-auth pam-auth ldap email-ext mailer dark-theme >>"$LOG" 2>&1
fi

if ! docker container inspect "$JC" >/dev/null 2>&1; then
  docker create --name "$JC" --network "$NET" -p $BIND:$JPORT:8080 -v "$VOL":/var/jenkins_home \
    -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true" \
    jenkins/jenkins:lts-jdk21 >/dev/null
  TMP=$(mktemp -d "$W/tmp/init.XXXX")
  mkdir -p "$TMP/init.groovy.d"
  cp "$PWF" "$TMP/admin-pass"
  cat > "$TMP/init.groovy.d/01-admin.groovy" <<'G'
import jenkins.model.*
import hudson.security.*
def j = Jenkins.get()
def f = new File(j.rootDir, 'admin-pass')
if (f.exists()) {
  def realm = new HudsonPrivateSecurityRealm(false)
  realm.createAccount('admin', f.text.trim()).setFullName('Admin')
  j.securityRealm = realm
  def st = new FullControlOnceLoggedInAuthorizationStrategy(); st.allowAnonymousRead = false
  j.authorizationStrategy = st
  f.delete()
}
def loc = JenkinsLocationConfiguration.get(); loc.url = 'http://localhost:8080/'; loc.save()
j.save()
G
  docker cp "$TMP/." "$JC":/var/jenkins_home/ >/dev/null
  rm -rf "$TMP"
  docker start "$JC" >/dev/null
fi
log "jenkins image: $(docker inspect -f '{{.Image}}' "$JC")"

# README step: install sshpass in jenkins (as root) — same command as the lab, container name adapted
docker exec -u root -e DEBIAN_FRONTEND=noninteractive "$JC" sh -c "command -v sshpass >/dev/null || (apt-get update -qq && apt-get install -y -qq --no-install-recommends sshpass)" >>"$LOG" 2>&1
log "sshpass in jenkins: $(docker exec "$JC" sh -c 'command -v sshpass; command -v docker || echo docker: none' | tr '\n' ' ')"

# README step: pin host key of devtools into jenkins known_hosts
timeout 60 docker exec "$DT" bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null; do sleep 1; done'
docker exec "$DT" sh -c "sed 's/^/devtools /' /etc/ssh/ssh_host_ed25519_key.pub > /tmp/devtools.known_hosts"
docker cp "$DT":/tmp/devtools.known_hosts "$W/tmp/devtools.known_hosts" >/dev/null
docker cp "$W/tmp/devtools.known_hosts" "$JC":/tmp/devtools.known_hosts >/dev/null
docker exec "$JC" sh -c "mkdir -p -m 700 /var/jenkins_home/.ssh && cp /tmp/devtools.known_hosts /var/jenkins_home/.ssh/known_hosts"
log "fingerprint dt:      $(docker exec "$DT" ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub)"
log "fingerprint jenkins: $(docker exec "$JC" ssh-keygen -lF devtools | tail -1)"
timeout 120 docker exec "$DT" bash -c 'until docker info >/dev/null 2>&1; do sleep 1; done' && log "dockerd in dt ready"

for i in $(seq 1 120); do
  C=$(curl -s -o /dev/null -w '%{http_code}' http://$HX:$JPORT/login || true)
  [ "$C" = 200 ] && break; sleep 2
done
log "jenkins /login via $HX:$JPORT -> $C"
