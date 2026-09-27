#!/usr/bin/env bash
# Remove ONLY resources owned by this task (run on coordinator's later instruction).
set -u
W=$(cd "$(dirname "$0")/.." && pwd); H=$(cat "$W/hash"); P=devtools-l3reorder-$H
for f in forward-8080 forward-3000 receiver; do
  pid=$(cat "$W/run/$f.pid" 2>/dev/null) && ps -p "$pid" -o args= | grep -q -E 'forward.py|receiver.py' && kill "$pid" && echo "stopped $f ($pid)"
done
docker rm -fv "$P-jenkins" "$P-dt" 2>/dev/null
docker volume rm "$P-jhome" 2>/dev/null
docker network rm "$P-net" 2>/dev/null
rm -rf "$W/tmp/localrepo" "$W/tmp/localrepo.git" "$W/tmp/devtools.known_hosts"
echo "left (must be empty):"; docker ps -a --filter "name=^$P-" --format '{{.Names}}'; docker volume ls -q --filter "name=^$P-"; docker network ls -q --filter "name=^$P-"
