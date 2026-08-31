#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 3 สร้างและรัน Next.js จาก Dockerfile แบบพื้นฐานได้จริง
# รันจากโฟลเดอร์ LAB ภายใน Container สำหรับการทดลอง :  bash verify.sh
#
# สคริปต์สร้างทรัพยากรด้วย prefix "vops3-" เท่านั้น และลบเมื่อจบตามค่าเริ่มต้น
# กำหนด KEEP_STACK=1 เพื่อคงระบบไว้ตรวจ UI; ไม่แตะ Container/image/volume prefix "ops-"

set -u

cd "$(dirname "$0")" || exit 1

failures=0
tmp_dir=""
keep_stack="${KEEP_STACK:-0}"
web_port="${WEB_PORT:-}"

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  if [ "$keep_stack" != "1" ]; then
    docker rm -f -v vops3-web vops3-api vops3-db >/dev/null 2>&1
    docker volume rm vops3-pgdata >/dev/null 2>&1
    docker image rm vops3-web:verify vops3-api:verify >/dev/null 2>&1
  fi
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

ip_of() { docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' "$1" 2>/dev/null; }

echo "=============================================="
echo " LAB 3 — Build The Web (single-stage) : verify"
echo "=============================================="

# ---------- preflight ----------
if docker info >/dev/null 2>&1; then
  pass "ต่อกับ Docker daemon ได้"
else
  fail "สั่ง docker info ไม่ผ่าน — Docker daemon ไม่ทำงานหรือไม่ได้รันภายใน Container สำหรับการทดลอง"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

tmp_dir=$(mktemp -d)

# ---------- 1) ไฟล์ของแล็บครบไหม ----------
missing=""
for f in web/Dockerfile web/package.json web/next.config.ts \
         web/tests/capture-walkthrough.spec.js \
         api/Dockerfile api/main.py db/initdb/01-schema.sql db/initdb/02-seed.sql \
         images/ui-web-01-overview.png images/ui-web-02-tickets.png \
         images/ui-web-03-asset.png images/ui-web-04-details.png \
         images/ui-web-05-priority.png images/ui-web-06-submit.png \
         images/ui-web-07-new-card.png images/ui-web-08-assignee.png \
         images/ui-web-09-assign.png images/ui-web-10-assigned.png; do
  [ -f "$f" ] || missing="$missing $f"
done
if [ -z "$missing" ]; then
  pass "ไฟล์ของแล็บครบ (web/ · api/ · db/initdb/)"
else
  fail "ไฟล์ของแล็บไม่ครบ:$missing"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

# ---------- 2) web/Dockerfile ต้องเป็น stage เดียวและอ่านตรงไปตรงมา ----------
stages=$(grep -c '^FROM ' web/Dockerfile)
if [ "$stages" -eq 1 ]; then
  pass "web/Dockerfile มี FROM 1 ครั้ง = stage เดียว"
else
  fail "web/Dockerfile ควรมี FROM 1 ครั้ง แต่พบ $stages ครั้ง"
fi

if grep -q '^COPY package.json package-lock.json ./$' web/Dockerfile; then
  pass "คัดลอก package files ก่อนติดตั้ง dependency"
else
  fail "ไม่พบบรรทัด COPY package.json package-lock.json ./"
fi

if grep -q '^RUN npm ci$' web/Dockerfile && grep -q '^RUN npm run build$' web/Dockerfile; then
  pass "Dockerfile ติดตั้ง dependency และ build Next.js ตามลำดับ"
else
  fail "Dockerfile ต้องมี RUN npm ci และ RUN npm run build"
fi

# ---------- 3) build image แบบพื้นฐาน ----------
if docker build -t vops3-web:verify ./web >"$tmp_dir/web.log" 2>&1; then
  pass "build image Next.js (vops3-web:verify) สำเร็จ"
else
  fail "build image Next.js ไม่สำเร็จ (ดู $tmp_dir/web.log)"
fi

# ---------- 4) CMD ต้องเริ่ม Next.js แบบ exec form ----------
cmd_json=$(docker image inspect vops3-web:verify --format '{{json .Config.Cmd}}' 2>/dev/null)
if [ "$cmd_json" = '["npm","start"]' ]; then
  pass "CMD เป็น exec form : $cmd_json"
else
  fail "CMD ควรเป็น [\"npm\",\"start\"] แต่ได้ $cmd_json"
fi

# ---------- 5) เริ่มสาม Container จริง แล้วเชื่อมต่อกันด้วย IP ----------
docker rm -f -v vops3-db vops3-api vops3-web >/dev/null 2>&1
docker volume rm vops3-pgdata >/dev/null 2>&1

if docker run -d --name vops3-db \
     -e POSTGRES_DB=skillspace -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
     -v vops3-pgdata:/var/lib/postgresql/data \
     -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
     postgres:17-alpine >/dev/null 2>&1; then
  pass "เริ่ม Container ฐานข้อมูล vops3-db ได้"
else
  fail "เริ่ม Container ฐานข้อมูล vops3-db ไม่สำเร็จ"
fi

db_ok=0
for _ in $(seq 1 30); do
  if docker exec vops3-db pg_isready -U opsuser -d skillspace >/dev/null 2>&1; then db_ok=1; break; fi
  sleep 1
done
[ "$db_ok" -eq 1 ] && pass "ฐานข้อมูลพร้อมรับ connection แล้ว" || fail "ฐานข้อมูลไม่พร้อมภายใน 30 วินาที"

docker build -t vops3-api:verify ./api >"$tmp_dir/api.log" 2>&1
DB_IP=$(ip_of vops3-db)
docker run -d --name vops3-api \
  -e DATABASE_URL="postgresql://opsuser:labpass@${DB_IP}:5432/skillspace" \
  vops3-api:verify >/dev/null 2>&1
API_IP=""
api_ok=0
for _ in $(seq 1 30); do
  API_IP=$(ip_of vops3-api)
  if [ -n "$API_IP" ] && curl --noproxy '*' --max-time 2 -fsS "http://$API_IP:8000/health" 2>/dev/null | grep -q '"db":"up"'; then
    api_ok=1; break
  fi
  sleep 1
done
[ "$api_ok" -eq 1 ] && pass "บริการเบื้องหลังตอบ /health ว่า db up (ต่อ db ด้วย IP $DB_IP)" \
                    || fail "บริการเบื้องหลังไม่ตอบ /health"

if [ -n "$web_port" ]; then
  docker run -d --name vops3-web -p "${web_port}:3000" \
    -e API_BASE_URL="http://${API_IP}:8000" vops3-web:verify >/dev/null 2>&1
else
  docker run -d --name vops3-web \
    -e API_BASE_URL="http://${API_IP}:8000" vops3-web:verify >/dev/null 2>&1
fi
WEB_IP=""
web_ok=0
for _ in $(seq 1 30); do
  WEB_IP=$(ip_of vops3-web)
  if [ -n "$WEB_IP" ] && curl --noproxy '*' --max-time 2 -fsS -o "$tmp_dir/home.html" "http://$WEB_IP:3000/" 2>/dev/null; then
    web_ok=1; break
  fi
  sleep 1
done
[ "$web_ok" -eq 1 ] && pass "หน้าเว็บตอบ 200 ที่ http://$WEB_IP:3000/ (ต่อ api ด้วย IP $API_IP)" \
                    || fail "หน้าเว็บไม่ตอบที่พอร์ต 3000"

if [ "$web_ok" -eq 1 ]; then
  pages_ok=1
  for p in /tickets /loans /parts; do
    code=$(curl --noproxy '*' --max-time 3 -s -o /dev/null -w '%{http_code}' "http://$WEB_IP:3000$p")
    [ "$code" = "200" ] || { pages_ok=0; fail "หน้า $p ตอบ $code ไม่ใช่ 200"; }
  done
  [ "$pages_ok" -eq 1 ] && pass "หน้า /tickets · /loans · /parts ตอบ 200 ครบ"

  if grep -q 'งานค้างเกินกำหนด' "$tmp_dir/home.html"; then
    pass "หน้าแรกมีเนื้อหาจริงจากฐานข้อมูล (บล็อก 'งานค้างเกินกำหนด')"
  else
    fail "หน้าแรกไม่มีเนื้อหาที่เรนเดอร์จากฝั่ง server"
  fi
fi

# ---------- 6) CSS ต้องมาถึงเบราว์เซอร์จริง ----------
if [ "$web_ok" -eq 1 ]; then
  css=$(grep -o '<link rel="stylesheet" href="[^"]*"' "$tmp_dir/home.html" | head -1 | sed 's/.*href="//; s/"$//')
  if [ -n "$css" ]; then
    csscode=$(curl --noproxy '*' --max-time 3 -s -o "$tmp_dir/app.css" -w '%{http_code}' "http://$WEB_IP:3000$css")
    csssize=$(wc -c < "$tmp_dir/app.css")
    if [ "$csscode" = "200" ] && [ "$csssize" -gt 5000 ]; then
      pass "โหลดไฟล์ CSS ได้ HTTP 200 ขนาด $csssize ไบต์"
    else
      fail "โหลดไฟล์ CSS ไม่สำเร็จ (HTTP $csscode · $csssize ไบต์)"
    fi
  else
    fail "ไม่พบ stylesheet ใน HTML"
  fi
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  if [ "$keep_stack" = "1" ]; then
    if [ -n "$web_port" ]; then
      echo "STACK KEPT: เปิดหน้าเว็บผ่านพอร์ต $web_port และลบด้วยคำสั่งในหัวข้อเก็บกวาด"
    else
      echo "STACK KEPT: ทรัพยากร vops3-* ยังคงทำงานเพื่อการตรวจเพิ่มเติม"
    fi
  fi
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
