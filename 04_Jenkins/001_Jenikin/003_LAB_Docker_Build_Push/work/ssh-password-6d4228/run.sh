#!/usr/bin/env bash
# Temporary SSH password-auth test. Scratch lives only in this dir.
set -u
D=$(cd "$(dirname "$0")" && pwd); H=$(cat "$D/hash")
C=devtools-ssh-password-$H; CLI=$C-client; IMG=tuchsanai/devtools:2569_1
LOG=$D/run.log; : > "$LOG"
log(){ echo "[$(date +%T)] $*" | tee -a "$LOG"; }
cleanup(){
  log "cleanup: removing $CLI and $C (with anonymous volumes)"
  docker rm -fv "$CLI" >/dev/null 2>&1
  VOLS=$(docker inspect -f '{{range .Mounts}}{{if eq .Type "volume"}}{{.Name}} {{end}}{{end}}' "$C" 2>/dev/null)
  echo "$VOLS" > "$D/anon_volumes.txt"
  docker rm -fv "$C" >/dev/null 2>&1
  log "post-cleanup containers matching ^$C: [$(docker ps -a -q --filter "name=^$C")]"
  for v in $VOLS; do docker volume inspect "$v" >/dev/null 2>&1 && log "volume LEFT: $v" || log "volume removed: $v"; done
  log "devtools- containers now: [$(docker ps -a --format '{{.Names}}' --filter 'name=^devtools-' | tr '\n' ' ')]"
}
trap cleanup EXIT INT TERM

N=$(docker ps -q --filter "name=^devtools-" --filter status=running | wc -l)
log "running devtools- containers before: $N"; [ "$N" -le 5 ] || { log "quota exceeded"; exit 1; }
PW=$(grep -m1 -E '^\| Password \| `' "$D/../../README.md" | sed -E 's/^\| Password \| `([^`]+)`.*/\1/')
[ -n "$PW" ] || { log "README password not found"; exit 1; }
log "README password extracted (length ${#PW}, not printed)"

P=2223; STARTED=0
while [ $P -le 2299 ]; do
  [ $P -eq 2222 ] && { P=$((P+1)); continue; }
  if docker run -dit --name "$C" --privileged -p 127.0.0.1:$P:22 "$IMG" >/dev/null 2>>"$LOG"; then STARTED=1; break; fi
  log "port $P unavailable, trying next"; docker rm -fv "$C" >/dev/null 2>&1; P=$((P+1))
done
[ $STARTED -eq 1 ] || { log "could not start"; exit 1; }
log "container $C started; mapping: $(docker port "$C" 22)"
log "image ID: $(docker inspect -f '{{.Image}}' "$C")"
timeout 60 docker exec "$C" bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null; do sleep 1; done' && log "sshd ready" || { log "sshd not ready in 60s"; exit 1; }

KEY=$(docker exec "$C" cat /etc/ssh/ssh_host_ed25519_key.pub | awk '{print $1" "$2}')
echo "[127.0.0.1]:$P $KEY" > "$D/known_hosts"
log "pinned host key: $(ssh-keygen -lf "$D/known_hosts")"

# Client runs in host netns (only way to reach a 127.0.0.1-bound host port from this agent container).
# Entrypoint overridden so no sshd/jupyter start on the host network. Password + known_hosts go via stdin only.
log "client tools in image: $(docker run --rm --entrypoint bash "$IMG" -c 'command -v sshpass || echo no-sshpass; python3 -c "import paramiko" 2>/dev/null && echo paramiko || echo no-paramiko' | tr '\n' ' ')"
{ printf '%s\n' "$PW"; cat "$D/known_hosts"; } | timeout 90 docker run --rm -i --name "$CLI" --network host --entrypoint bash "$IMG" -c '
  read -r SSHPASS; export SSHPASS; cat > /tmp/kh
  if ! command -v sshpass >/dev/null; then
    (apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends sshpass) >/dev/null 2>&1 || { echo "CLIENT: sshpass install failed"; exit 97; }
    echo "CLIENT: sshpass installed in throwaway client"
  fi
  timeout 20 sshpass -e ssh -F /dev/null -p '"$P"' \
    -o UserKnownHostsFile=/tmp/kh -o StrictHostKeyChecking=yes -o GlobalKnownHostsFile=/dev/null \
    -o PreferredAuthentications=password -o PubkeyAuthentication=no -o KbdInteractiveAuthentication=no \
    -o PasswordAuthentication=yes -o NumberOfPasswordPrompts=1 -o IdentitiesOnly=yes -o IdentityAgent=none \
    -o ConnectTimeout=10 -o BatchMode=no -v \
    root@127.0.0.1 "hostname; whoami" 2> /tmp/err
  RC=$?; echo "CLIENT: ssh exit=$RC"
  grep -E "Authentications that can continue|Authenticated to|Host .* found|Permission denied|Server host key" /tmp/err | sed "s/^/CLIENT-DBG: /"
  exit $RC' 2>&1 | tee -a "$LOG"
RC=${PIPESTATUS[1]}
log "ssh result rc=$RC; container hostname (for comparison): $(docker exec "$C" hostname)"
exit $RC
