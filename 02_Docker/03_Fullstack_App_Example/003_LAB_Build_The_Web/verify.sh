#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 3 (สร้าง image ของหน้าเว็บด้วย multi-stage) ทำได้ครบจริง
# รันจากในโฟลเดอร์ LAB บนกล่องเรียน :  bash verify.sh
#
# สคริปต์นี้สร้างของของตัวเองด้วย prefix "vops3-" เท่านั้น และลบเฉพาะของตัวเองตอนจบ
# ไม่แตะ container / image / volume ที่ผู้เรียนสร้างไว้ (prefix "ops-") เด็ดขาด

set -u

cd "$(dirname "$0")" || exit 1

failures=0
tmp_dir=""

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  docker rm -f -v vops3-web vops3-api vops3-db >/dev/null 2>&1
  docker volume rm vops3-pgdata >/dev/null 2>&1
  docker image rm vops3-web:verify vops3-web:single vops3-api:verify >/dev/null 2>&1
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

ip_of() { docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' "$1" 2>/dev/null; }

echo "=============================================="
echo " LAB 3 — Build The Web (multi-stage) : verify"
echo "=============================================="

# ---------- preflight ----------
if docker info >/dev/null 2>&1; then
  pass "ต่อกับ Docker daemon ได้"
else
  fail "สั่ง docker info ไม่ผ่าน — ยังไม่ได้อยู่ในกล่องเรียนหรือ daemon ไม่ทำงาน"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

tmp_dir=$(mktemp -d)

# ---------- 1) ไฟล์ของแล็บครบไหม ----------
missing=""
for f in web/Dockerfile web/Dockerfile.single web/Dockerfile.shellform web/package.json web/next.config.ts \
         api/Dockerfile api/main.py db/initdb/01-schema.sql db/initdb/02-seed.sql; do
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

# ---------- 2) web/Dockerfile ต้องเป็น multi-stage 3 ชั้นจริง ----------
stages=$(grep -c '^FROM ' web/Dockerfile)
if [ "$stages" -eq 3 ]; then
  pass "web/Dockerfile มี FROM 3 ครั้ง = 3 stage (deps · builder · runner)"
else
  fail "web/Dockerfile ควรมี FROM 3 ครั้ง แต่พบ $stages ครั้ง"
fi

if grep -q '^COPY --from=builder .*\.next/standalone' web/Dockerfile &&
   grep -qE '^COPY --from=builder .*/\.next/static \./\.next/static' web/Dockerfile; then
  pass "stage runner หยิบเฉพาะ .next/standalone และ .next/static ทั้งก้อน"
else
  fail "stage runner ต้อง COPY --from=builder ทั้ง .next/standalone และ .next/static (ทั้งโฟลเดอร์)"
fi

if grep -qE '^COPY --from=builder .*\.next/static/(css|chunks)[ /]' web/Dockerfile; then
  fail "web/Dockerfile เจาะ COPY โฟลเดอร์ย่อยของ .next/static — หน้าเว็บจะไม่มี CSS"
else
  pass "ไม่มีบรรทัดที่เจาะ COPY เฉพาะโฟลเดอร์ย่อยของ .next/static"
fi

# ---------- 3) build ทั้งสองแบบ ----------
if docker build -t vops3-web:verify ./web >"$tmp_dir/multi.log" 2>&1; then
  pass "build image multi-stage (vops3-web:verify) สำเร็จ"
else
  fail "build image multi-stage ไม่สำเร็จ (ดู $tmp_dir/multi.log)"
fi

if docker build -f web/Dockerfile.single -t vops3-web:single ./web >"$tmp_dir/single.log" 2>&1; then
  pass "build image stage เดียว (vops3-web:single) สำเร็จ"
else
  fail "build image stage เดียวไม่สำเร็จ (ดู $tmp_dir/single.log)"
fi

# ---------- 4) ขนาดต้องต่างกันอย่างมีนัย ----------
size_multi=$(docker image inspect vops3-web:verify  --format '{{.Size}}' 2>/dev/null)
size_single=$(docker image inspect vops3-web:single --format '{{.Size}}' 2>/dev/null)
if [ -n "$size_multi" ] && [ -n "$size_single" ] && [ "$size_multi" -gt 0 ]; then
  ratio=$((size_single * 10 / size_multi))
  human_multi=$((size_multi / 1000000))
  human_single=$((size_single / 1000000))
  if [ "$ratio" -ge 20 ]; then
    pass "multi-stage เล็กกว่า stage เดียวอย่างน้อย 2 เท่า (content size ${human_multi}MB vs ${human_single}MB)"
  else
    fail "ขนาดต่างกันน้อยเกินไป (${human_multi}MB vs ${human_single}MB)"
  fi
else
  fail "อ่านขนาด image ไม่ได้"
fi

# ---------- 5) toolchain ต้องไม่ติดไปกับ image ที่ส่งมอบ ----------
if docker history --no-trunc --format '{{.CreatedBy}}' vops3-web:verify 2>/dev/null | grep -q 'npm run build'; then
  fail "docker history ของ image สุดท้ายยังมีขั้น npm run build ติดมา"
else
  pass "docker history ของ image สุดท้ายไม่มีขั้น npm ci / npm run build เลย"
fi

if docker run --rm vops3-web:verify sh -c 'ls node_modules/typescript' >/dev/null 2>&1; then
  fail "image สุดท้ายยังมี node_modules/typescript (แบก devDependencies ไปด้วย)"
else
  pass "image สุดท้ายไม่มี node_modules/typescript — ไม่ได้แบก toolchain ไปด้วย"
fi

# ---------- 6) CMD ต้องเป็น exec form และไม่รันด้วย root ----------
cmd_json=$(docker image inspect vops3-web:verify --format '{{json .Config.Cmd}}' 2>/dev/null)
if [ "$cmd_json" = '["node","server.js"]' ]; then
  pass "CMD เป็น exec form : $cmd_json"
else
  fail "CMD ควรเป็น [\"node\",\"server.js\"] แต่ได้ $cmd_json"
fi

img_user=$(docker image inspect vops3-web:verify --format '{{.Config.User}}' 2>/dev/null)
if [ -n "$img_user" ] && [ "$img_user" != "root" ] && [ "$img_user" != "0" ]; then
  pass "image ตั้ง USER เป็น $img_user (ไม่ใช่ root)"
else
  fail "image ยังรันด้วย root (USER='$img_user')"
fi

# ---------- 7) ยกสามกล่องขึ้นจริง แล้วต่อกันด้วย IP ----------
docker rm -f -v vops3-db vops3-api vops3-web >/dev/null 2>&1
docker volume rm vops3-pgdata >/dev/null 2>&1

if docker run -d --name vops3-db \
     -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
     -v vops3-pgdata:/var/lib/postgresql/data \
     -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
     postgres:17-alpine >/dev/null 2>&1; then
  pass "ยกกล่องฐานข้อมูล vops3-db ขึ้นได้"
else
  fail "ยกกล่องฐานข้อมูล vops3-db ไม่ขึ้น"
fi

db_ok=0
for _ in $(seq 1 30); do
  if docker exec vops3-db pg_isready -U opsuser -d campusops >/dev/null 2>&1; then db_ok=1; break; fi
  sleep 1
done
[ "$db_ok" -eq 1 ] && pass "ฐานข้อมูลพร้อมรับ connection แล้ว" || fail "ฐานข้อมูลไม่พร้อมภายใน 30 วินาที"

docker build -t vops3-api:verify ./api >"$tmp_dir/api.log" 2>&1
DB_IP=$(ip_of vops3-db)
docker run -d --name vops3-api \
  -e DATABASE_URL="postgresql://opsuser:labpass@${DB_IP}:5432/campusops" \
  vops3-api:verify >/dev/null 2>&1
API_IP=""
api_ok=0
for _ in $(seq 1 30); do
  API_IP=$(ip_of vops3-api)
  if [ -n "$API_IP" ] && curl -fsS "http://$API_IP:8000/health" 2>/dev/null | grep -q '"db":"up"'; then
    api_ok=1; break
  fi
  sleep 1
done
[ "$api_ok" -eq 1 ] && pass "บริการเบื้องหลังตอบ /health ว่า db up (ต่อ db ด้วย IP $DB_IP)" \
                    || fail "บริการเบื้องหลังไม่ตอบ /health"

docker run -d --name vops3-web -e API_BASE_URL="http://${API_IP}:8000" vops3-web:verify >/dev/null 2>&1
WEB_IP=""
web_ok=0
for _ in $(seq 1 30); do
  WEB_IP=$(ip_of vops3-web)
  if [ -n "$WEB_IP" ] && curl -fsS -o "$tmp_dir/home.html" "http://$WEB_IP:3000/" 2>/dev/null; then
    web_ok=1; break
  fi
  sleep 1
done
[ "$web_ok" -eq 1 ] && pass "หน้าเว็บตอบ 200 ที่ http://$WEB_IP:3000/ (ต่อ api ด้วย IP $API_IP)" \
                    || fail "หน้าเว็บไม่ตอบที่พอร์ต 3000"

if [ "$web_ok" -eq 1 ]; then
  pages_ok=1
  for p in /tickets /loans /parts; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://$WEB_IP:3000$p")
    [ "$code" = "200" ] || { pages_ok=0; fail "หน้า $p ตอบ $code ไม่ใช่ 200"; }
  done
  [ "$pages_ok" -eq 1 ] && pass "หน้า /tickets · /loans · /parts ตอบ 200 ครบ"

  if grep -q 'งานค้างเกินกำหนด' "$tmp_dir/home.html"; then
    pass "หน้าแรกมีเนื้อหาจริงจากฐานข้อมูล (บล็อก 'งานค้างเกินกำหนด')"
  else
    fail "หน้าแรกไม่มีเนื้อหาที่เรนเดอร์จากฝั่ง server"
  fi
fi

# ---------- 8) CSS ต้องมาถึงเบราว์เซอร์จริง (กับดักของ Next.js 16) ----------
if [ "$web_ok" -eq 1 ]; then
  css=$(grep -o '<link rel="stylesheet" href="[^"]*"' "$tmp_dir/home.html" | head -1 | sed 's/.*href="//; s/"$//')
  case "$css" in
    /_next/static/chunks/*.css)
      pass "HTML ชี้ไฟล์ CSS ไปที่ $css (อยู่ใต้ chunks/ ตามที่ Next.js 16 วางจริง)" ;;
    "")
      fail "ไม่พบ <link rel=\"stylesheet\"> ใน HTML เลย" ;;
    *)
      fail "เส้นทางไฟล์ CSS ผิดจากที่คาด : $css" ;;
  esac

  if [ -n "$css" ]; then
    csscode=$(curl -s -o "$tmp_dir/app.css" -w '%{http_code}' "http://$WEB_IP:3000$css")
    csssize=$(wc -c < "$tmp_dir/app.css")
    if [ "$csscode" = "200" ] && [ "$csssize" -gt 5000 ]; then
      pass "โหลดไฟล์ CSS ได้ HTTP 200 ขนาด $csssize ไบต์"
    else
      fail "โหลดไฟล์ CSS ไม่สำเร็จ (HTTP $csscode · $csssize ไบต์)"
    fi
  fi

  if docker exec vops3-web sh -c 'ls .next/static/chunks/*.css' >/dev/null 2>&1; then
    pass "ไฟล์ CSS อยู่จริงใน image ที่ .next/static/chunks/"
  else
    fail "ไม่พบไฟล์ .css ใต้ .next/static/chunks/ ใน image"
  fi

  if docker exec vops3-web sh -c 'ls .next/static/css' >/dev/null 2>&1; then
    fail "พบโฟลเดอร์ .next/static/css — ผิดจากที่เอกสารอธิบายไว้ ต้องทบทวนเอกสาร"
  else
    pass "ไม่มีโฟลเดอร์ .next/static/css จริง — ยืนยันว่าห้าม COPY เจาะ subfolder"
  fi
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
