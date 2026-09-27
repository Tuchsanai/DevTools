#!/usr/bin/env bash
# Minimal isolated Jenkins for LAB 3 step-3 navigation screenshots only.
# Resources: devtools-l3nav-<hash>-{net,jhome,jenkins}. KEPT after the task (user order) — no cleanup here.
set -euo pipefail
W=$(cd "$(dirname "$0")/.." && pwd)
H=$(cat "$W/hash"); P=devtools-l3nav-$H
NET=$P-net; VOL=$P-jhome; JC=$P-jenkins
JPORT=${JPORT:-18490}; IMG=jenkins/jenkins:lts-jdk21
LOG=$W/evidence/setup-env.log
log(){ echo "[$(date +%T)] $*" | tee -a "$LOG"; }

N=$(docker ps -q --filter "name=^devtools-" --filter status=running | wc -l)
log "running devtools- containers before: $N"; [ "$N" -lt 7 ] || { log "limit 7 reached"; exit 1; }
docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET" >/dev/null
docker volume inspect "$VOL" >/dev/null 2>&1 || docker volume create "$VOL" >/dev/null
log "network $NET, volume $VOL"

if ! docker run --rm -v "$VOL":/var/jenkins_home $IMG test -d /var/jenkins_home/plugins/credentials 2>/dev/null; then
  log "installing credentials plugin (+deps)"
  docker run --rm --name $P-plugins -v "$VOL":/var/jenkins_home $IMG \
    jenkins-plugin-cli -d /var/jenkins_home/plugins --plugins credentials >>"$LOG" 2>&1
fi

if ! docker container inspect "$JC" >/dev/null 2>&1; then
  docker create --name "$JC" --network "$NET" --restart unless-stopped -p 127.0.0.1:$JPORT:8080 \
    -v "$VOL":/var/jenkins_home -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" $IMG >/dev/null
  TMP=$(mktemp -d "$W/tmp/init.XXXX"); mkdir -p "$TMP/init.groovy.d"
  # disposable training account documented in README step 2 (admin / admin2569)
  cat > "$TMP/init.groovy.d/01-admin.groovy" <<'G'
import jenkins.model.*
import hudson.security.*
def j = Jenkins.get()
if (!(j.securityRealm instanceof HudsonPrivateSecurityRealm)) {
  def realm = new HudsonPrivateSecurityRealm(false)
  realm.createAccount('admin', 'admin2569').setFullName('Admin')
  j.securityRealm = realm
  def st = new FullControlOnceLoggedInAuthorizationStrategy(); st.allowAnonymousRead = false
  j.authorizationStrategy = st
}
def loc = JenkinsLocationConfiguration.get(); loc.url = 'http://localhost:8080/'; loc.save()
j.save()
G
  docker cp "$TMP/." "$JC":/var/jenkins_home/ >/dev/null; rm -rf "$TMP"
  docker start "$JC" >/dev/null
fi
log "jenkins image: $(docker inspect -f '{{.Image}}' "$JC") ip: $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$JC")"
for i in $(seq 1 150); do
  C=$(curl -s -o /dev/null -w '%{http_code}' http://host.docker.internal:$JPORT/login || true)
  [ "$C" = 200 ] && break; sleep 2
done
log "jenkins /login via host.docker.internal:$JPORT -> $C"
