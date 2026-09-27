#!/usr/bin/env bash
# Serve the LOCAL (unpublished) Jenkinsfile from a throwaway git repo inside the
# isolated devtools container (git daemon :9418 on the lab network only).
set -euo pipefail
C=devtools-l3e2e-406430-devtools
LAB=$(cd "$(dirname "$0")/.." && pwd)
SP=04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push
docker exec $C bash -c "rm -rf /srv/fixture /srv/fixture.git && mkdir -p /srv/fixture/$SP"
docker cp "$LAB/Jenkinsfile" $C:/srv/fixture/$SP/Jenkinsfile
docker exec $C bash -ec "cd /srv/fixture && git init -q -b main && git add . && \
  git -c user.name=fixture -c user.email=fixture@example.invalid commit -qm 'local Jenkinsfile fixture' && \
  git clone -q --bare /srv/fixture /srv/fixture.git && touch /srv/fixture.git/git-daemon-export-ok && \
  git -C /srv/fixture log -1 --format='fixture commit %H'; sha256sum /srv/fixture/$SP/Jenkinsfile"
docker exec $C bash -c "pkill -f 'git daemon' || true"
docker exec -d $C sh -c 'git daemon --reuseaddr --base-path=/srv --export-all --verbose /srv > /var/log/git-daemon.log 2>&1'
sleep 2
