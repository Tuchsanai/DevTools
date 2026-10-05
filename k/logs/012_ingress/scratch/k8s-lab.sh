#!/usr/bin/env bash
# k8s-lab.sh — run Kubernetes LAB experiments in throwaway, isolated containers.
# Self-contained: needs only bash, docker CLI and coreutils (curl/ssh/flock optional).
# Every container is named k8s-lab-<experiment>-<hashid> and labelled so that
# concurrent agents never touch each other's containers or ports.
set -uo pipefail

IMAGE=${K8S_LAB_IMAGE:-tuchsanai/devtools-kind:2569_1}
MAX=${K8S_LAB_MAX:-5}
OWNER=${K8S_LAB_OWNER:-$(hostname)}
LOCK=${K8S_LAB_LOCK:-${TMPDIR:-/tmp}/k8s-lab.ports.lock}
# Host ports that belong to the student's own k8s-lab/devtools containers.
RESERVED="2222 2223 8888 8889 30080 30081 30082"
PREFIX=k8s-lab-

die()  { echo "ERROR: $*" >&2; exit 1; }
log()  { echo "[k8s-lab] $*" >&2; }
pass() { echo "PASS  $*"; }
fail() { echo "FAIL  $*"; FAILED=$((FAILED+1)); }
FAILED=0

usage() {
  cat <<'EOF'
usage: k8s-lab.sh <command> [args]

  up <experiment> [--ssh] [--jupyter] [--nodeport] [--auto-create] [--wait-slot]
                  [--ssh-port N] [--jupyter-port N] [--nodeport-base N] [-- extra docker run args]
        create k8s-lab-<experiment>-<hashid>, print its name on stdout
  wait <C> [secs]          wait for sshd + inner dockerd (default 90s)
  cluster <C> [secs]       run k8s-up and wait for 3 nodes Ready (default 400s)
  check <C> [what...]      what = tools cluster examples host ssh jupyter all (default all)
  expect <C> <regex> [secs] -- <cmd...>
                           retry <cmd> inside C until output matches regex
  expect-host <C> <container-port> <regex> [secs] [path]
                           curl the mapped host port until body matches regex
  cp <C> <local-path> [dest]   copy LAB files into C (default dest /workspace/lab/)
  info <C>                 name, owner, hashid, image ID, host ports
  ls                       list all k8s-lab-* containers (all owners)
  down <C>...              remove container(s) + DinD volume, verify gone
  run <experiment> [up opts]   up -> wait -> cluster -> check all -> down (always)

env: K8S_LAB_IMAGE K8S_LAB_MAX(5) K8S_LAB_OWNER(hostname) K8S_LAB_HOST K8S_LAB_LOCK
EOF
}

# ---------- helpers ----------
hashid() { # random, never derived from any secret
  od -An -N3 -tx1 /dev/urandom | tr -d ' \n'
}

sanitize() { # docker-safe experiment slug
  local s
  s=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9-' '-' | tr -s '-' | sed 's/^-*//; s/-*$//')
  s=${s:0:40}
  [ -n "$s" ] || die "invalid experiment name: '$1'"
  printf '%s' "$s"
}

probe_host() { # where published host ports are reachable from here
  if [ -n "${K8S_LAB_HOST:-}" ]; then echo "$K8S_LAB_HOST"
  elif [ -f /.dockerenv ]; then ip route 2>/dev/null | awk '/^default/ {print $3; exit}'
  else echo 127.0.0.1; fi
}
HOST=$(probe_host); HOST=${HOST:-127.0.0.1}

used_ports() { # all host ports bound by any container (running or stopped) + reserved
  echo $RESERVED | tr ' ' '\n'
  local ids; ids=$(docker ps -aq)
  [ -n "$ids" ] && docker inspect --format \
    '{{range $p,$b := .HostConfig.PortBindings}}{{range $b}}{{.HostPort}}{{"\n"}}{{end}}{{end}}' $ids 2>/dev/null
  # ranges like "30080-30082" may appear when bound as ranges
  true
}

expand_used() {
  used_ports | while read -r p; do
    [ -z "$p" ] && continue
    if [[ $p == *-* ]]; then seq "${p%-*}" "${p#*-}"; else echo "$p"; fi
  done | sort -un
}

port_open() { timeout 2 bash -c "echo > /dev/tcp/$HOST/$1" 2>/dev/null; }

port_free() { # $1 port, $2 = newline list of used ports
  grep -qx "$1" <<<"$2" && return 1
  port_open "$1" && return 1
  return 0
}

pick_port() { # $1 start, $2 used list
  local p=$1
  while ! port_free "$p" "$2"; do p=$((p+1)); [ $p -gt 65000 ] && die "no free port from $1"; done
  echo "$p"
}

pick_np_base() { # 3 consecutive ports, start 30090, step 10
  local b=$1 used=$2
  while :; do
    if port_free "$b" "$used" && port_free $((b+1)) "$used" && port_free $((b+2)) "$used"; then echo "$b"; return; fi
    b=$((b+10)); [ $b -gt 32760 ] && die "no free NodePort block"
  done
}

running_count() { docker ps -q --filter "name=^${PREFIX}" | wc -l; }

hostport() { # $1 C, $2 container port -> host port (empty if not published)
  docker port "$1" "$2/tcp" 2>/dev/null | head -1 | awk -F: '{print $NF}'
}

need_c() {
  [ -n "${1:-}" ] || die "container name required"
  [[ $1 == ${PREFIX}* ]] || die "refusing: '$1' is not a ${PREFIX}* container"
  docker inspect "$1" >/dev/null 2>&1 || die "no such container: $1"
}

# ---------- commands ----------
cmd_up() {
  local exp="" ssh=0 jup=0 np=0 auto=0 waitslot=0 sshp="" jupp="" npb="" extra=()
  while [ $# -gt 0 ]; do
    case $1 in
      --ssh) ssh=1;; --jupyter) jup=1;; --nodeport) np=1;; --auto-create) auto=1;;
      --wait-slot) waitslot=1;;
      --ssh-port) sshp=$2; ssh=1; shift;; --jupyter-port) jupp=$2; jup=1; shift;;
      --nodeport-base) npb=$2; np=1; shift;;
      --) shift; extra=("$@"); break;;
      -*) die "unknown option $1";;
      *) [ -z "$exp" ] && exp=$1 || die "unexpected arg $1";;
    esac; shift
  done
  [ -n "$exp" ] || die "usage: up <experiment> [opts]"
  exp=$(sanitize "$exp")

  docker image inspect "$IMAGE" >/dev/null 2>&1 || { log "pulling $IMAGE"; docker pull -q "$IMAGE" >&2 || die "pull failed"; }

  # concurrency quota (counts every agent's k8s-lab-* containers, touches none);
  # checked under the lock so simultaneous `up` calls cannot overshoot MAX
  local t0=$SECONDS attempt name hid args used s j b out
  { exec 9>"$LOCK"; } 2>/dev/null
  while :; do
    command -v flock >/dev/null && flock -w 120 9 2>/dev/null
    [ "$(running_count)" -lt "$MAX" ] && break
    flock -u 9 2>/dev/null
    [ $waitslot = 1 ] || die "quota reached: $(running_count)/$MAX k8s-lab-* containers running (use --wait-slot or K8S_LAB_MAX)"
    [ $((SECONDS-t0)) -gt 1800 ] && die "waited 30 min for a free slot"
    log "quota $MAX reached, waiting for a slot..."; sleep 10
  done
  for attempt in 1 2 3 4 5; do
    hid=$(hashid); name="${PREFIX}${exp}-${hid}"
    docker inspect "$name" >/dev/null 2>&1 && continue
    used=$(expand_used)
    args=(-dit --name "$name" --hostname k8s-lab --privileged
          --label k8s-lab.owner="$OWNER" --label k8s-lab.hashid="$hid"
          --label k8s-lab.experiment="$exp" --label k8s-lab.created="$(date -u +%FT%TZ)")
    if [ $ssh = 1 ]; then
      if [ -n "$sshp" ]; then port_free "$sshp" "$used" || die "requested SSH port $sshp is busy"; s=$sshp
      else s=$(pick_port 2224 "$used"); fi
      args+=(-p "$s:22"); used+=$'\n'$s
    fi
    if [ $jup = 1 ]; then
      if [ -n "$jupp" ]; then port_free "$jupp" "$used" || die "requested Jupyter port $jupp is busy"; j=$jupp
      else j=$(pick_port 8890 "$used"); fi
      args+=(-p "$j:8888"); used+=$'\n'$j
    fi
    if [ $np = 1 ]; then
      if [ -n "$npb" ]; then
        for k in 0 1 2; do port_free $((npb+k)) "$used" || die "requested NodePort port $((npb+k)) is busy"; done; b=$npb
      else b=$(pick_np_base 30090 "$used"); fi
      args+=(-p "$b-$((b+2)):30080-30082")
    fi
    [ $auto = 1 ] && args+=(-e KIND_AUTO_CREATE=1)
    if out=$(docker run "${args[@]}" "${extra[@]}" "$IMAGE" 2>&1); then
      flock -u 9 2>/dev/null; exec 9>&-
      log "created $name (owner=$OWNER image=$(docker inspect -f '{{.Image}}' "$name" | cut -c8-19))"
      echo "$name"; return 0
    fi
    docker rm -fv "$name" >/dev/null 2>&1
    if grep -qiE 'already allocated|address already in use|bind' <<<"$out" && [ -z "$sshp$jupp$npb" ]; then
      log "port race on attempt $attempt, retrying"; continue
    fi
    flock -u 9 2>/dev/null; exec 9>&-
    die "docker run failed: $out"
  done
  die "could not create container after 5 attempts"
}

cmd_wait() {
  need_c "$1"; local secs=${2:-90}
  timeout "$secs" docker exec "$1" bash -c \
    'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null; do sleep 1; done; until docker info >/dev/null 2>&1; do sleep 1; done' \
    || die "$1 not ready after ${secs}s"
  log "$1 ready (sshd + dockerd)"
}

cmd_cluster() {
  need_c "$1"; local secs=${2:-400}
  timeout "$secs" docker exec "$1" k8s-up >&2 || die "k8s-up failed/timeout in $1"
  local n; n=$(docker exec "$1" kubectl get nodes --no-headers 2>/dev/null | awk '$2=="Ready"' | wc -l)
  [ "$n" -eq 3 ] || die "expected 3 Ready nodes, got $n"
  log "$1 cluster lab: 3 nodes Ready"
}

# retry a command inside C until regex matches
cmd_expect() {
  local c=$1 re=$2 secs=60; shift 2
  [ "${1:-}" != "--" ] && { secs=$1; shift; }
  [ "${1:-}" = "--" ] && shift
  need_c "$c"; local out="" t0=$SECONDS
  while :; do
    out=$(docker exec "$c" bash -lc "$*" 2>&1)
    if grep -qE "$re" <<<"$out"; then pass "$* =~ /$re/ -> $(grep -oE "$re" <<<"$out" | head -1)"; return 0; fi
    [ $((SECONDS-t0)) -ge "$secs" ] && { fail "$* !~ /$re/ (last: $(tail -c 200 <<<"$out" | tr '\n' ' '))"; return 1; }
    sleep 2
  done
}

cmd_expect_host() {
  local c=$1 cport=$2 re=$3 secs=${4:-60} path=${5:-/}
  need_c "$c"; local hp; hp=$(hostport "$c" "$cport")
  [ -n "$hp" ] || { fail "port $cport not published on $c"; return 1; }
  local out="" t0=$SECONDS
  while :; do
    out=$(curl -s --max-time 5 "http://$HOST:$hp$path")
    if grep -qE "$re" <<<"$out"; then pass "host :$hp -> $cport =~ /$re/ (localhost:$hp$path)"; return 0; fi
    [ $((SECONDS-t0)) -ge "$secs" ] && { fail "host :$hp$path !~ /$re/"; return 1; }
    sleep 2
  done
}

chk_tools() {
  local c=$1 v
  v=$(docker exec "$c" kubectl version --client 2>&1 | tr '\n' ' '); [[ $v == *v1.* ]] && pass "kubectl: $v" || fail "kubectl: $v"
  v=$(docker exec "$c" kind --version 2>&1); [[ $v == kind* ]] && pass "$v" || fail "kind: $v"
  v=$(docker exec "$c" helm version --short 2>&1); [[ $v == v* ]] && pass "helm $v" || fail "helm: $v"
  v=$(docker exec "$c" k9s version --short 2>&1 | tr -s ' \n' ' '); [[ $v == *Version* ]] && pass "k9s $v" || fail "k9s: $v"
  v=$(docker logs "$c" 2>&1 | grep -o 'cgroup v2 controllers:.*' | head -1)
  [[ $v == *memory* && $v == *io* ]] && pass "$v" || fail "cgroup nesting: '${v:-missing}'"
}

chk_cluster() {
  local c=$1
  docker exec "$c" kind get clusters 2>/dev/null | grep -qx lab || cmd_cluster "$c"
  local n; n=$(docker exec "$c" kubectl get nodes --no-headers 2>/dev/null | awk '$2=="Ready"' | wc -l)
  [ "$n" -eq 3 ] && pass "3 nodes Ready ($(docker exec "$c" kubectl config current-context))" || fail "Ready nodes = $n"
}

chk_examples() {
  local c=$1
  docker exec "$c" bash -c 'cd /workspace/examples && kubectl apply -f hello-pod.yaml -f web-deployment.yaml' >/dev/null 2>&1
  cmd_expect "$c" 'Hello from Kubernetes pod hello' 180 -- 'kubectl logs hello'
  docker exec "$c" kubectl rollout status deploy/web --timeout=180s >/dev/null 2>&1
  cmd_expect "$c" '<title>Welcome to nginx!</title>' 120 -- 'curl -s localhost:30080'
  docker exec "$c" bash -c 'cd /workspace/examples && docker build -q -t myapp:1.0 myapp && kind load docker-image myapp:1.0 --name lab && kubectl apply -f myapp/myapp.yaml' >/dev/null 2>&1 \
    || fail "build/kind load myapp"
  docker exec "$c" kubectl rollout status deploy/myapp --timeout=180s >/dev/null 2>&1
  cmd_expect "$c" '<h1>Hello from myapp:1.0</h1>' 120 -- 'curl -s localhost:30081'
}

chk_host() {
  local c=$1
  [ -n "$(hostport "$c" 30080)" ] || { echo "SKIP  host NodePort (not published, use --nodeport)"; return; }
  cmd_expect_host "$c" 30080 '<title>Welcome to nginx!</title>' 90
  cmd_expect_host "$c" 30081 '<h1>Hello from myapp:1.0</h1>' 90
}

chk_ssh() {
  local c=$1 hp; hp=$(hostport "$c" 22)
  [ -n "$hp" ] || { echo "SKIP  ssh (not published, use --ssh)"; return; }
  command -v ssh >/dev/null || { echo "SKIP  ssh (no ssh client)"; return; }
  local d; d=$(mktemp -d); local o=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -p "$hp")
  printf '#!/bin/sh\necho passwd\n' >"$d/askpass"; chmod +x "$d/askpass"
  local out
  out=$(SSH_ASKPASS="$d/askpass" SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid ssh "${o[@]}" \
        -o PubkeyAuthentication=no root@"$HOST" 'hostname; kubectl config current-context 2>/dev/null || true' </dev/null 2>&1)
  [[ $out == *k8s-lab* ]] && pass "ssh password root@localhost:$hp -> $(tr '\n' ' ' <<<"$out")" || fail "ssh password: $out"
  if docker cp "$c:/etc/devtools/ssh/devtoolSSH" "$d/key" >/dev/null 2>&1; then
    chmod 600 "$d/key"
    out=$(ssh -i "$d/key" -o BatchMode=yes -o IdentitiesOnly=yes "${o[@]}" root@"$HOST" hostname </dev/null 2>&1)
    [[ $out == *k8s-lab* ]] && pass "ssh key devtoolSSH localhost:$hp" || fail "ssh key: $out"
  else
    echo "SKIP  ssh key (no generated key in container; mounted .pub only)"
  fi
  rm -rf "$d"
}

chk_jupyter() {
  local c=$1 hp; hp=$(hostport "$c" 8888)
  [ -n "$hp" ] || { echo "SKIP  jupyter (not published, use --jupyter)"; return; }
  local code="" t0=$SECONDS
  while [ $((SECONDS-t0)) -lt 60 ]; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://$HOST:$hp/lab"); [ "$code" = 200 ] && break; sleep 2
  done
  [ "$code" = 200 ] && pass "jupyter http://localhost:$hp/lab -> 200" || fail "jupyter /lab -> $code"
}

cmd_check() {
  local c=$1; shift; need_c "$c"
  local what=("$@"); [ ${#what[@]} -eq 0 ] && what=(all)
  [ "${what[0]}" = all ] && what=(tools cluster examples host ssh jupyter)
  echo "== check $c (image $(docker inspect -f '{{.Image}}' "$c" | cut -c8-19))"
  for w in "${what[@]}"; do
    case $w in
      tools|cluster|examples|host|ssh|jupyter) chk_$w "$c";;
      *) die "unknown check $w";;
    esac
  done
  echo "== $c: $FAILED failed"
  [ $FAILED -eq 0 ]
}

cmd_cp() {
  need_c "$1"; local dest=${3:-/workspace/lab/}
  docker exec "$1" mkdir -p "$dest" && docker cp "$2" "$1:$dest" >/dev/null && log "copied $2 -> $1:$dest"
}

cmd_info() {
  need_c "$1"
  docker inspect -f 'name={{.Name}} owner={{index .Config.Labels "k8s-lab.owner"}} hashid={{index .Config.Labels "k8s-lab.hashid"}} image={{.Image}} status={{.State.Status}}' "$1" | sed 's#name=/#name=#'
  docker port "$1" | sed 's/^/  /'
}

cmd_ls() {
  docker ps -a --filter "name=^${PREFIX}" \
    --format 'table {{.Names}}\t{{.Label "k8s-lab.owner"}}\t{{.Status}}\t{{.Ports}}'
}

cmd_down() {
  [ $# -gt 0 ] || die "usage: down <C>..."
  local c rc=0
  for c in "$@"; do
    [[ $c == ${PREFIX}* ]] || { log "refusing to remove '$c' (not ${PREFIX}*)"; rc=1; continue; }
    docker rm -fv "$c" >/dev/null 2>&1
    if docker inspect "$c" >/dev/null 2>&1; then log "STILL PRESENT: $c"; rc=1; else log "removed $c"; fi
  done
  return $rc
}

cmd_run() {
  local exp=${1:?experiment}; shift
  RUN_C=$(cmd_up "$exp" "$@") || exit 1
  trap 'rc=$?; cmd_down "$RUN_C"; exit $rc' EXIT
  trap 'exit 130' INT TERM
  cmd_info "$RUN_C"
  cmd_wait "$RUN_C" && cmd_cluster "$RUN_C" && cmd_check "$RUN_C" all
}

case ${1:-} in
  up) shift; cmd_up "$@";;
  wait) shift; cmd_wait "$@";;
  cluster) shift; cmd_cluster "$@";;
  check) shift; cmd_check "$@";;
  expect) shift; cmd_expect "$@";;
  expect-host) shift; cmd_expect_host "$@";;
  cp) shift; cmd_cp "$@";;
  info) shift; cmd_info "$@";;
  ls) cmd_ls;;
  down) shift; cmd_down "$@";;
  run) shift; cmd_run "$@";;
  ""|-h|--help|help) usage;;
  *) usage; exit 2;;
esac
