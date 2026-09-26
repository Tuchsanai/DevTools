#!/bin/bash
# Phase: create isolated experiment + Jenkins (exact LAB001 launch) + labadmin + creds + job. Owner: yolo3.
set -uo pipefail
cd "$(dirname "$0")/.."
O=out3; mkdir -p $O
[ "$(docker ps -q --filter name=^devtools- | wc -l)" -lt 7 ] || { echo "too many devtools- containers"; exit 1; }
H=$(head -c 16 /dev/urandom | sha256sum | cut -c1-6); C=devtools-lab003-$H; echo $C > container_name3
docker run -dit --name $C --privileged --tmpfs /run --label owner=yolo3 \
  -p 127.0.0.1:2223:22 -p 127.0.0.1:18080:8080 -p 127.0.0.1:13000:3000 tuchsanai/devtools:2569_1 >/dev/null || exit 1
docker inspect -f '{{.Image}}' $C > $O/image_id
timeout 90 docker exec $C bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null && docker info >/dev/null 2>&1; do sleep 1; done' || exit 1
date '+%Y-%m-%d %H:%M %Z' > $O/date
docker exec -i $C bash < blocks/jenkins-launch.sh > $O/jenkins-launch.txt 2>&1
docker exec $C bash -c 'for i in $(seq 150); do docker logs jenkins 2>&1 | grep -q "fully up" && break; sleep 2; done'
docker exec $C docker exec jenkins sh -c 'unzip -p /usr/share/jenkins/jenkins.war META-INF/MANIFEST.MF | grep Jenkins-Version' > $O/jenkins_version 2>&1
# test-only emulation of "Install suggested plugins" in the setup wizard
docker exec $C bash -c 'docker exec jenkins jenkins-plugin-cli -d /var/jenkins_home/plugins --plugins cloudbees-folder antisamy-markup-formatter build-timeout credentials-binding timestamper ws-cleanup workflow-aggregator github-branch-source pipeline-github-lib pipeline-graph-view git ssh-slaves matrix-auth pam-auth ldap email-ext mailer dark-theme ssh-credentials > /tmp/plugins.log 2>&1; tail -2 /tmp/plugins.log; docker restart jenkins >/dev/null; for i in $(seq 150); do [ "$(curl -s -o /dev/null -w "%{http_code}" localhost:8080/login)" = 200 ] && break; sleep 2; done' > $O/plugins.txt 2>&1
for b in check-state exp1-no-docker exp2-dns exp3-gateway exp4-ssh-alias exp4-test exp5-key exp5-keytest; do docker exec -i $C bash < blocks/$b.sh > $O/$b.txt 2>&1; done
docker cp ../../003_LAB_Docker_Build_Push/Jenkinsfile $C:/tmp/Jenkinsfile; docker cp scripts/jenkins_api2.sh $C:/tmp/jenkins_api.sh
LAB_PASS=$(head -c 24 /dev/urandom | base64 | tr -dc A-Za-z0-9 | cut -c1-20)
docker exec -e LAB_PASS $C /tmp/jenkins_api.sh mkuser > $O/mkuser.txt
docker exec -e LAB_PASS $C bash -c 'umask 077; printf "labadmin:%s" "$LAB_PASS" > /root/.jauth'
(umask 077; printf '{"username":"labadmin","password":"%s"}\n' "$LAB_PASS" > browser-auth.json); chmod 600 browser-auth.json
docker exec $C /tmp/jenkins_api.sh whoami > $O/whoami.txt
( set -a; . /root/workspace/DGX_2024/.env >/dev/null 2>&1; set +a; REG_USER="$DOCKER_USER" REG_PASS="$DOCKER_TOKEN" docker exec -e REG_USER -e REG_PASS $C /tmp/jenkins_api.sh creds ) > $O/creds.txt
docker exec $C /tmp/jenkins_api.sh job > $O/job.txt
IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $C)
echo "$C $IP $(cat $O/image_id)"
