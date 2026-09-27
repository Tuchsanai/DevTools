#!/usr/bin/env bash
# Fresh isolated LAB003 environment (test harness, not the student setup).
# Adaptation: local devtools:2569_1 has no /etc/devtools/ssh key support, so the
# LAB public key Devtool_SSH/devtoolSSH.pub is installed into root's
# authorized_keys of the isolated devtools container (same effect as start.sh
# of the key-enabled image). No host docker.sock is mounted anywhere.
set -euo pipefail
H=406430
P=devtools-l3e2e-$H
LAB=$(cd "$(dirname "$0")/.." && pwd)
SHOP_PORT=13000
JENKINS_PORT=18491
SSH_PORT=2223

docker network create "$P-net" >/dev/null
docker volume create "$P-jhome" >/dev/null

docker run -dit --name "$P-devtools" --hostname devtools --privileged --tmpfs /run \
  --network "$P-net" --network-alias devtools \
  -p 127.0.0.1:$SSH_PORT:22 -p 127.0.0.1:$SHOP_PORT:3000 devtools:2569_1 >/dev/null
docker exec "$P-devtools" bash -c 'mkdir -p /root/.ssh && chmod 700 /root/.ssh'
docker cp "$LAB/Devtool_SSH/devtoolSSH.pub" "$P-devtools:/root/.ssh/lab_key.pub"
docker exec "$P-devtools" bash -c 'head -n1 /root/.ssh/lab_key.pub | tr -d "\r" >> /root/.ssh/authorized_keys && rm /root/.ssh/lab_key.pub && chmod 600 /root/.ssh/authorized_keys'

docker run -d --name "$P-jenkins" --network "$P-net" --restart unless-stopped \
  -p 127.0.0.1:$JENKINS_PORT:8080 -v "$P-jhome:/var/jenkins_home" \
  -e JAVA_OPTS=-Djenkins.install.runSetupWizard=false jenkins/jenkins:lts-jdk21 >/dev/null

# admin/admin2569 like README step 2.4 (Setup Wizard skipped in this harness)
docker exec "$P-jenkins" bash -c 'mkdir -p /var/jenkins_home/init.groovy.d && cat > /var/jenkins_home/init.groovy.d/admin.groovy' <<'GROOVY'
import jenkins.model.*
import hudson.security.*
def j = Jenkins.get()
if (!(j.securityRealm instanceof HudsonPrivateSecurityRealm)) {
  def realm = new HudsonPrivateSecurityRealm(false)
  realm.createAccount('admin', 'admin2569')
  j.securityRealm = realm
  def s = new FullControlOnceLoggedInAuthorizationStrategy(); s.allowAnonymousRead = false
  j.authorizationStrategy = s
  j.save()
}
GROOVY
docker exec "$P-jenkins" jenkins-plugin-cli --plugin-download-directory /var/jenkins_home/plugins \
  --plugins workflow-aggregator git ssh-agent pipeline-graph-view credentials-binding
docker restart "$P-jenkins" >/dev/null
docker exec "$P-devtools" bash -c 'for i in $(seq 60); do docker info >/dev/null 2>&1 && exit 0; sleep 1; done; exit 1'
echo "up: $P-devtools $P-jenkins"
