#!/bin/bash
# End-to-end test of LAB 3 in a fresh isolated devtools-lab003-<hash> container. Owner: yolo3.
set -uo pipefail
cd "$(dirname "$0")/.."
H=$(head -c 16 /dev/urandom | sha256sum | cut -c1-6); C=devtools-lab003-$H; echo $C > container_name
O=out2; rm -rf $O; mkdir -p $O
cleanup() { docker rm -fv "$C" >/dev/null 2>&1; rm -f .regpass; echo "cleanup: removed $C"; }
trap cleanup EXIT
[ "$(docker ps -q --filter name=^devtools- | wc -l)" -lt 7 ] || { echo "too many devtools- containers"; exit 1; }
docker run -dit --name $C --privileged --tmpfs /run -p 127.0.0.1:2223:22 -p 127.0.0.1:18080:8080 -p 127.0.0.1:13000:3000 tuchsanai/devtools:2569_1 >/dev/null || exit 1
docker inspect -f '{{.Image}}' $C > $O/image_id
timeout 90 docker exec $C bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null && docker info >/dev/null 2>&1; do sleep 1; done' || exit 1
date '+%Y-%m-%d %H:%M %Z' > $O/date
# exact Jenkins launch (extracted from built README by caller into blocks/jenkins-launch.sh)
docker exec -i $C bash < blocks/jenkins-launch.sh > $O/jenkins-launch.txt 2>&1
docker exec $C bash -c 'for i in $(seq 120); do docker logs jenkins 2>&1 | grep -q "fully up" && break; sleep 2; done; docker logs jenkins 2>&1 | grep -c "fully up"' > $O/jenkins-up.txt
docker exec $C docker exec jenkins cat /var/jenkins_home/war/META-INF/MANIFEST.MF 2>/dev/null | grep -i '^Jenkins-Version' > $O/jenkins_version
# test-only emulation of setup wizard plugin install
docker exec $C bash -c 'docker exec jenkins jenkins-plugin-cli -d /var/jenkins_home/plugins --plugins workflow-aggregator credentials-binding ssh-credentials pipeline-graph-view >/dev/null 2>&1; docker restart jenkins >/dev/null; for i in $(seq 120); do [ "$(curl -s -o /dev/null -w "%{http_code}" localhost:8080/login)" = 200 ] && break; sleep 2; done'
for b in check-state exp1-no-docker exp2-dns exp3-gateway exp4-ssh-alias exp4-test exp5-key exp5-keytest; do docker exec -i $C bash < blocks/$b.sh > $O/$b.txt 2>&1; done
REGPASS=$(head -c 18 /dev/urandom | base64 | tr -dc A-Za-z0-9); echo -n "$REGPASS" > .regpass
docker exec -e REGPASS="$REGPASS" $C bash -c 'mkdir -p /root/reg-auth && docker run --rm --entrypoint htpasswd httpd:2 -Bbn labuser "$REGPASS" > /root/reg-auth/htpasswd 2>/dev/null && docker run -d --name lab3-registry --restart unless-stopped -p 127.0.0.1:5000:5000 -v /root/reg-auth:/auth -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=lab -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2 >/dev/null 2>&1; sleep 2'
sed "s|REGISTRY    = 'docker.io'|REGISTRY    = 'localhost:5000'|" ../../003_LAB_Docker_Build_Push/Jenkinsfile > Jenkinsfile.test
docker cp Jenkinsfile.test $C:/tmp/Jenkinsfile.test; docker cp scripts/jenkins_api.sh $C:/tmp/jenkins_api.sh
docker exec -e REG_USER=labuser -e REG_PASS="$REGPASS" $C /tmp/jenkins_api.sh setup > $O/setup.txt
run() { local n=$1; shift; docker exec $C /tmp/jenkins_api.sh build "$@" >/dev/null; sleep 5; docker exec $C /tmp/jenkins_api.sh wait $n > $O/b$n.json; docker exec $C /tmp/jenkins_api.sh console $n > $O/b$n.txt; docker exec $C /tmp/jenkins_api.sh params $n > $O/b$n.params; cat $O/b$n.json; }
run 1
docker exec -i $C bash < blocks/verify-web.sh > $O/verify-web-b1.txt 2>&1
run 2 APP_VERSION=1.1.0
docker exec -i $C bash < blocks/verify-web.sh > $O/verify-web-b2.txt 2>&1
run 3 'APP_VERSION=1.2.0; id'
run 4 'APP_SUBDIR=../../etc'
run 5 GIT_REF=no-such-branch
docker exec -i $C bash < blocks/verify-web.sh > $O/verify-web-b5.txt 2>&1
# restart devtools (continuation scenario), then build again
docker restart $C >/dev/null
timeout 120 docker exec $C bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null && docker info >/dev/null 2>&1; do sleep 1; done; for i in $(seq 150); do [ "$(curl -s -o /dev/null -w "%{http_code}" localhost:8080/login)" = 200 ] && break; sleep 2; done'
docker exec $C bash -c 'docker ps --format "{{.Names}} {{.Status}}"; docker network inspect cicd-net --format "{{range .IPAM.Config}}{{.Gateway}}{{end}}"; docker exec jenkins ssh -G devtools-gw | grep ^hostname' > $O/after-restart.txt 2>&1
run 6 APP_VERSION=1.1.1
docker exec -i $C bash < blocks/verify-web.sh > $O/verify-web-b6.txt 2>&1
docker exec -i $C bash < blocks/cleanup.sh > $O/cleanup.txt 2>&1
docker exec $C bash -c 'docker ps -a --format "{{.Names}}"; docker image ls --format "{{.Repository}}:{{.Tag}}" | grep catfood; ls /root/lab3-work /tmp/jenkins-docker-* 2>&1' > $O/after-cleanup.txt
grep -l "$REGPASS" $O/* && echo "SECRET LEAK" || echo "no secret in outputs"
