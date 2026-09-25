#!/usr/bin/env bash
# ตรวจสถานะจบ LAB 3 — รันใน devtools: DOCKER_USER=<id> bash check.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
JOB='docker-build-push'
REPO='catfood-shop'
failures=0
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
unset DOCKER_TOKEN

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }
info() { printf '[INFO] %s\n' "$1"; }

if [ -z "${DOCKER_USER:-}" ]; then
  fail 'กรุณารันด้วย DOCKER_USER=<id> bash check.sh'
  printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
  exit 1
fi

# 1) Jenkins ใช้ image ที่มี Docker CLI + mount socket + mount source
image="$(docker inspect -f '{{.Config.Image}}' jenkins 2>/dev/null || true)"
[ "$image" = 'jenkins-docker:2569' ] && pass 'jenkins ใช้ image jenkins-docker:2569' \
  || fail "jenkins ใช้ image ไม่ตรง (พบ: ${image:-ไม่พบ container})"

mounts="$(docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' jenkins 2>/dev/null || true)"
case " $mounts " in *' /var/run/docker.sock '*) pass 'jenkins mount Docker socket แล้ว' ;; *) fail 'jenkins ยังไม่ได้ mount /var/run/docker.sock' ;; esac
case " $mounts " in *' /lab/catfood-shop '*) pass 'jenkins mount source ร้านอาหารแมวที่ /lab/catfood-shop' ;; *) fail 'jenkins ยังไม่ได้ mount /lab/catfood-shop' ;; esac

# 2) Credential dockerhub
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/credentials/store/system/domain/_/api/json?tree=credentials[id]" 2>/dev/null \
    | grep -q '"id":"dockerhub"'; then
  pass 'Jenkins Credentials API พบ id dockerhub'
else
  fail 'Jenkins Credentials API ไม่พบ id dockerhub'
fi

# 3) build ล่าสุดสำเร็จ
read -r build_number build_result < <(curl -gfsS -u "$JENKINS_AUTH" \
  "$JENKINS_URL/job/$JOB/lastBuild/api/json?tree=number,result" 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("number",""), d.get("result",""))' 2>/dev/null || echo '')
if [ -n "${build_number:-}" ] && [ "${build_result:-}" = 'SUCCESS' ]; then
  pass "$JOB build #$build_number = SUCCESS"
else
  fail "$JOB ยังไม่มี build ล่าสุดที่ SUCCESS"
fi

# 4) digest จาก console ตรงกับ Docker Hub (tag BUILD_NUMBER และ latest)
console="$tmp_dir/console.txt"
curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/${build_number:-0}/consoleText" -o "$console" 2>/dev/null
jenkins_digest="$(sed -n "s/^${build_number:-x}: digest: \(sha256:[0-9a-f]\{64\}\).*/\1/p" "$console" | tail -1)"
[ -n "$jenkins_digest" ] && pass "console มี push digest ${jenkins_digest:0:19}..." \
  || fail 'ไม่พบ push digest ใน console ของ build ล่าสุด'

hub_digest() {
  curl -fsS "https://hub.docker.com/v2/namespaces/$DOCKER_USER/repositories/$REPO/tags/$1" 2>/dev/null \
    | python3 -c 'import json,sys; print(json.load(sys.stdin).get("digest",""))' 2>/dev/null
}
tag_digest="$(hub_digest "${build_number:-0}")"
latest_digest="$(hub_digest latest)"
if [ -n "$jenkins_digest" ] && [ "$tag_digest" = "$jenkins_digest" ]; then
  pass "Docker Hub tag ${build_number} มี digest ตรงกับ console"
else
  fail "Docker Hub tag ${build_number:-?} ไม่พบหรือ digest ไม่ตรง"
fi
if [ -n "$jenkins_digest" ] && [ "$latest_digest" = "$jenkins_digest" ]; then
  pass 'tag latest ชี้ไปที่ build ล่าสุด'
else
  fail 'tag latest ยังไม่ชี้ไปที่ build ล่าสุด'
fi

# 5) ใครก็ pull ได้ (anonymous) = repository เป็น Public
if DOCKER_CONFIG="$tmp_dir/anon" docker manifest inspect "docker.io/$DOCKER_USER/$REPO:latest" >/dev/null 2>&1; then
  pass 'anonymous client อ่าน manifest ได้ (repository เป็น Public)'
else
  fail 'anonymous client อ่าน manifest ไม่ได้ — ตรวจว่า repository เป็น Public'
fi

# 6) เว็บที่ deploy แล้วเป็น build ล่าสุด
web_image="$(docker inspect -f '{{.Config.Image}}' catfood-web 2>/dev/null || true)"
health="$(curl -fsS http://localhost:3000/api/health 2>/dev/null || true)"
info "catfood-web image: ${web_image:-ไม่พบ}"
info "health: ${health:-ไม่มีการตอบกลับ}"
case "$web_image" in
  *"$DOCKER_USER/$REPO:"*) pass 'catfood-web รันจาก image ที่ pull มาจาก Docker Hub' ;;
  *) fail 'catfood-web ไม่ได้รันจาก image บน Docker Hub' ;;
esac
if printf '%s' "$health" | grep -q "\"build\":\"${build_number:-x}\""; then
  pass "http://localhost:3000 ตอบ build #$build_number"
else
  fail "http://localhost:3000 ยังไม่ใช่ build #${build_number:-?}"
fi

# 7) ไม่มี token รั่ว และไม่มี docker auth ค้าง
pattern_count="$( { cat "$console"; find "$SCRIPT_DIR" -type f -not -path '*/node_modules/*' -exec cat {} + 2>/dev/null; } \
  | python3 -c 'import sys; print(sys.stdin.buffer.read().count(b"dckr_" + b"pat_"))')"
info "Docker token pattern count: $pattern_count"
[ "$pattern_count" = '0' ] && pass 'ไม่พบรูปแบบ Docker Hub token ในไฟล์แล็บหรือ console' \
  || fail 'พบรูปแบบ Docker Hub token; ต้อง revoke token และล้างก่อนส่งงาน'

retained="$(docker exec jenkins sh -c \
  'find /root /var/jenkins_home /tmp -type f -name config.json -exec grep -hc "\"auth\"" {} \; 2>/dev/null | awk "{s+=\$1} END {print s+0}"' \
  2>/dev/null || printf '0')"
info "retained Docker auth entry count: $retained"
[ "$retained" = '0' ] && pass 'ไม่พบ Docker auth entry ค้างใน jenkins container' \
  || fail 'พบ Docker auth entry ค้างใน jenkins container'

if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
