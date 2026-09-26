#!/bin/bash
# Reproduce param oddity after devtools restart. Owner: yolo3.
cd "$(dirname "$0")/.."; H=$(head -c 16 /dev/urandom | sha256sum | cut -c1-6); C=devtools-lab003p-$H
trap 'docker rm -fv $C >/dev/null 2>&1; echo removed $C' EXIT
docker run -dit --name $C --privileged --tmpfs /run tuchsanai/devtools:2569_1 >/dev/null
timeout 90 docker exec $C bash -c 'until docker info >/dev/null 2>&1; do sleep 1; done'
docker exec -i $C bash < blocks/jenkins-launch.sh >/dev/null 2>&1
docker exec $C bash -c 'for i in $(seq 120); do docker logs jenkins 2>&1 | grep -q "fully up" && break; sleep 2; done; docker exec jenkins jenkins-plugin-cli -d /var/jenkins_home/plugins --plugins workflow-aggregator credentials-binding ssh-credentials >/dev/null 2>&1; docker restart jenkins >/dev/null; for i in $(seq 120); do [ "$(curl -s -o /dev/null -w "%{http_code}" localhost:8080/login)" = 200 ] && break; sleep 2; done'
docker cp Jenkinsfile.test $C:/tmp/Jenkinsfile.test; docker cp scripts/jenkins_api.sh $C:/tmp/jenkins_api.sh
docker exec $C bash -c 'mkdir -p /root/.ssh; ssh-keygen -q -t ed25519 -N "" -f /root/.ssh/jenkins_devtools'
docker exec -e REG_USER=labuser -e REG_PASS=x $C /tmp/jenkins_api.sh setup
p() { docker exec $C /tmp/jenkins_api.sh params $1 | grep -o '"APP_VERSION","value":"[^"]*"'; }
docker exec $C /tmp/jenkins_api.sh build; sleep 8; docker exec $C /tmp/jenkins_api.sh wait 1 >/dev/null
docker exec $C /tmp/jenkins_api.sh build APP_VERSION=1.1.0; sleep 8; docker exec $C /tmp/jenkins_api.sh wait 2 >/dev/null; echo "b2 $(p 2)"
docker exec $C /tmp/jenkins_api.sh build APP_VERSION=1.1.1; sleep 8; docker exec $C /tmp/jenkins_api.sh wait 3 >/dev/null; echo "b3 (before restart) $(p 3)"
docker restart $C >/dev/null
timeout 150 docker exec $C bash -c 'until docker info >/dev/null 2>&1; do sleep 1; done; for i in $(seq 150); do [ "$(curl -s -o /dev/null -w "%{http_code}" localhost:8080/login)" = 200 ] && break; sleep 2; done'
docker exec $C /tmp/jenkins_api.sh build APP_VERSION=1.1.2; cat_resp=$(docker exec $C cat /tmp/resp | head -c 300); echo "resp: $cat_resp"; sleep 8; docker exec $C /tmp/jenkins_api.sh wait 4 >/dev/null; echo "b4 (after restart) $(p 4)"
docker exec $C bash -c 'curl -s -u admin:$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword) "localhost:8080/job/docker-build-push/api/json?tree=builds[number]"'
