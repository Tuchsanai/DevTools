#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 5 (ยุบทุกอย่างเป็นไฟล์เดียว แล้วส่งมอบให้ลูกค้า) ทำได้ครบจริง
# รันจากในโฟลเดอร์ LAB บนกล่องเรียน :  bash verify.sh
#
# สคริปต์นี้สร้างของของตัวเองด้วย prefix "vops5-" / project "vops5" เท่านั้น และลบเฉพาะของตัวเองตอนจบ
# ไม่แตะ project "campusops" · container "ops-*" · volume ของผู้เรียนเด็ดขาด

set -u

cd "$(dirname "$0")" || exit 1

failures=0
tmp_dir=""

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

VP=vops5                      # ชื่อ compose project ของสคริปต์นี้
VWEB_PORT=13191               # พอร์ตของสคริปต์นี้ ไม่ชนกับ 3000 ที่ผู้เรียนใช้
VREG_PORT=15000               # พอร์ต registry ของสคริปต์นี้

dc() { docker compose -p "$VP" -f compose.yaml -f "$tmp_dir/verify-override.yaml" "$@"; }

cleanup() {
  if [ -n "$tmp_dir" ] && [ -f "$tmp_dir/verify-override.yaml" ]; then
    docker compose -p "$VP" -f compose.yaml -f "$tmp_dir/verify-override.yaml" down -v >/dev/null 2>&1
  fi
  docker rm -f vops5-registry >/dev/null 2>&1
  docker image rm -f localhost:$VREG_PORT/vops5-api:1.0 localhost:$VREG_PORT/vops5-web:1.0 >/dev/null 2>&1
  docker image rm -f vops5-api vops5-web >/dev/null 2>&1
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

echo "=============================================="
echo " LAB 5 — Compose And Ship : verify"
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

cat > "$tmp_dir/verify-override.yaml" <<EOF
services:
  web:
    ports: !override
      - "$VWEB_PORT:3000"
EOF

# ---------- 1) ไฟล์ของแล็บครบไหม ----------
missing=""
for f in compose.yaml api/Dockerfile api/main.py web/Dockerfile web/package.json \
         db/initdb/01-schema.sql db/initdb/02-seed.sql; do
  [ -f "$f" ] || missing="$missing $f"
done
if [ -z "$missing" ]; then
  pass "ไฟล์ของแล็บครบ (compose.yaml · api/ · web/ · db/initdb/)"
else
  fail "ไฟล์ของแล็บไม่ครบ:$missing"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

# ---------- 2) compose.yaml อ่านออกและมีครบ 3 service ----------
svc=$(docker compose -p "$VP" config --services 2>/dev/null | sort | tr '\n' ' ')
if [ "$svc" = "api db web " ]; then
  pass "compose.yaml ประกาศครบ 3 service : api db web"
else
  fail "compose.yaml ควรมี service api · db · web แต่ได้ '$svc'"
fi

# ---------- 3) ห้ามตั้ง container_name ----------
if grep -qE '^[[:space:]]*container_name:' compose.yaml; then
  fail "compose.yaml ตั้ง container_name ไว้ — จะรันหลาย project พร้อมกันไม่ได้"
else
  pass "ไม่มี container_name ในไฟล์ — ปล่อยให้ compose ตั้งชื่อเป็น <project>-<service>-<n>"
fi

# ---------- 4) healthcheck + depends_on: service_healthy ----------
if [ "$(grep -cE '^[[:space:]]*healthcheck:' compose.yaml)" = "3" ]; then
  pass "มี healthcheck ครบทั้ง 3 service"
else
  fail "ควรมี healthcheck ครบทั้ง 3 service"
fi

if [ "$(grep -cE '^[[:space:]]*condition: service_healthy' compose.yaml)" = "2" ]; then
  pass "depends_on ใช้ condition: service_healthy 2 จุด (api รอ db · web รอ api)"
else
  fail "ควรมี condition: service_healthy 2 จุด"
fi

# ---------- 5) NFR-3 : db ต้องไม่มี published port ----------
db_ports=$(awk '/^  db:/{f=1;next} /^  [a-z]/{f=0} f' compose.yaml | grep -cE '^[[:space:]]*ports:')
if [ "$db_ports" = "0" ]; then
  pass "NFR-3 : service db ไม่มี published port ในไฟล์"
else
  fail "NFR-3 : service db มี published port อยู่ในไฟล์"
fi

# ---------- 6) NFR-2 : named volume ----------
if docker compose -p "$VP" config --volumes 2>/dev/null | grep -q '^pgdata$'; then
  pass "NFR-2 : ประกาศ named volume ชื่อ pgdata ไว้แล้ว"
else
  fail "NFR-2 : ไม่พบ named volume ชื่อ pgdata"
fi

# ---------- 7) NFR-1 : คำสั่งเดียวขึ้นครบสามกล่อง ----------
dc down -v >/dev/null 2>&1
if dc up -d --build >"$tmp_dir/up.log" 2>&1; then
  pass "NFR-1 : docker compose up -d --build ขึ้นครบด้วยคำสั่งเดียว"
else
  fail "docker compose up -d --build ไม่สำเร็จ (ดู $tmp_dir/up.log)"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

healthy_all=0
for _ in $(seq 1 60); do
  n=$(docker inspect -f '{{.State.Health.Status}}' "${VP}-db-1" "${VP}-api-1" "${VP}-web-1" 2>/dev/null | grep -c '^healthy$')
  if [ "$n" = "3" ]; then healthy_all=1; break; fi
  sleep 2
done
[ "$healthy_all" = "1" ] && pass "ทั้ง 3 service ขึ้นสถานะ healthy" \
                         || fail "มี service ที่ไม่ถึงสถานะ healthy ภายใน 120 วินาที"

# ---------- 8) ลำดับการสตาร์ตต้องเป็น db -> api -> web ----------
t_db=$(docker inspect -f '{{.State.StartedAt}}' "${VP}-db-1" 2>/dev/null)
t_api=$(docker inspect -f '{{.State.StartedAt}}' "${VP}-api-1" 2>/dev/null)
t_web=$(docker inspect -f '{{.State.StartedAt}}' "${VP}-web-1" 2>/dev/null)
if [ -n "$t_db" ] && [ "$t_db" \< "$t_api" ] && [ "$t_api" \< "$t_web" ]; then
  pass "ลำดับการสตาร์ตเป็น db -> api -> web ตาม depends_on: service_healthy"
else
  fail "ลำดับการสตาร์ตไม่เป็น db -> api -> web (db=$t_db api=$t_api web=$t_web)"
fi

# ---------- 9) db ที่รันอยู่จริงต้องไม่มีพอร์ตทะลุออกมา ----------
if [ -z "$(docker port "${VP}-db-1" 2>/dev/null)" ]; then
  pass "NFR-3 : กล่อง db ที่รันอยู่ไม่มี port mapping ออกนอกเครื่อง"
else
  fail "NFR-3 : กล่อง db มี port mapping ออกนอกเครื่อง"
fi

# ---------- 10) หน้าเว็บตอบจริงทั้ง 4 หน้า ----------
web_ok=0
for _ in $(seq 1 30); do
  if curl -fsS -o "$tmp_dir/home.html" "http://localhost:$VWEB_PORT/" 2>/dev/null; then web_ok=1; break; fi
  sleep 2
done
if [ "$web_ok" = "1" ]; then
  pass "หน้าเว็บตอบ 200 ที่ http://localhost:$VWEB_PORT/"
  pages_ok=1
  for p in /tickets /loans /parts; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$VWEB_PORT$p")
    [ "$code" = "200" ] || { pages_ok=0; fail "หน้า $p ตอบ $code ไม่ใช่ 200"; }
  done
  [ "$pages_ok" = "1" ] && pass "หน้า /tickets · /loans · /parts ตอบ 200 ครบทั้ง 3 โมดูล"
else
  fail "หน้าเว็บไม่ตอบที่พอร์ต $VWEB_PORT"
fi

# ---------- 11) เรียกกันด้วยชื่อ service ข้ามกล่องได้ ----------
if dc exec -T web wget -qO- http://api:8000/health 2>/dev/null | grep -q '"db":"up"'; then
  pass "web เรียก http://api:8000/health ด้วยชื่อ service แล้วได้ db up"
else
  fail "web เรียก api ด้วยชื่อ service ไม่สำเร็จ"
fi

# ---------- 12) NFR-2 : down แล้ว up ข้อมูลต้องอยู่ ----------
dc exec -T db psql -U opsuser -d campusops -c \
  "INSERT INTO tickets (asset_id,title,detail,priority) VALUES (4,'verify-ticket','จากสคริปต์ตรวจงาน','HIGH');" >/dev/null 2>&1
before=$(dc exec -T db psql -U opsuser -d campusops -tAc 'SELECT count(*) FROM tickets;' 2>/dev/null | tr -d '\r')

dc down >/dev/null 2>&1
dc up -d --no-build >/dev/null 2>&1
for _ in $(seq 1 40); do
  dc exec -T db pg_isready -U opsuser -d campusops >/dev/null 2>&1 && break
  sleep 2
done
after=$(dc exec -T db psql -U opsuser -d campusops -tAc 'SELECT count(*) FROM tickets;' 2>/dev/null | tr -d '\r')
if [ -n "$before" ] && [ "$before" = "$after" ] && [ "$after" -gt 8 ]; then
  pass "NFR-2 : down แล้ว up ข้อมูลยังอยู่ครบ ($after ใบเท่าเดิม)"
else
  fail "NFR-2 : ข้อมูลไม่ตรงกันหลัง down/up (ก่อน=$before หลัง=$after)"
fi

# ---------- 13) down -v แล้ว up ต้องกลับไปเป็น seed ----------
dc down -v >/dev/null 2>&1
dc up -d --no-build >/dev/null 2>&1
for _ in $(seq 1 40); do
  dc logs db 2>&1 | grep -q 'init process complete' && break
  sleep 2
done
for _ in $(seq 1 20); do
  dc exec -T db pg_isready -U opsuser -d campusops >/dev/null 2>&1 && break
  sleep 2
done
seeded=$(dc exec -T db psql -U opsuser -d campusops -tAc 'SELECT count(*) FROM tickets;' 2>/dev/null | tr -d '\r')
if [ "$seeded" = "8" ]; then
  pass "down -v แล้ว up ข้อมูลกลับไปเป็น seed ตั้งต้น (8 ใบ)"
else
  fail "หลัง down -v แล้ว up ควรได้ 8 ใบตาม seed แต่ได้ '$seeded'"
fi

# ---------- 14) ส่งมอบ : tag -> push -> pull ผ่าน registry ในเครื่อง ----------
docker rm -f vops5-registry >/dev/null 2>&1
if docker run -d --name vops5-registry -p "$VREG_PORT:5000" registry:2 >/dev/null 2>&1; then
  reg_ok=0
  for _ in $(seq 1 20); do
    curl -fsS "http://localhost:$VREG_PORT/v2/" >/dev/null 2>&1 && { reg_ok=1; break; }
    sleep 1
  done
  [ "$reg_ok" = "1" ] && pass "ยก registry ในเครื่อง (registry:2) ขึ้นที่พอร์ต $VREG_PORT ได้" \
                      || fail "registry ไม่ตอบที่พอร์ต $VREG_PORT"
else
  fail "ยกกล่อง registry:2 ไม่ขึ้น"
fi

docker tag "${VP}-api" "localhost:$VREG_PORT/vops5-api:1.0" >/dev/null 2>&1
docker tag "${VP}-web" "localhost:$VREG_PORT/vops5-web:1.0" >/dev/null 2>&1
push_ok=1
docker push "localhost:$VREG_PORT/vops5-api:1.0" >/dev/null 2>&1 || push_ok=0
docker push "localhost:$VREG_PORT/vops5-web:1.0" >/dev/null 2>&1 || push_ok=0
if [ "$push_ok" = "1" ]; then
  pass "docker push image ทั้งสองก้อนขึ้น registry สำเร็จ"
else
  fail "docker push ไม่สำเร็จ"
fi

catalog=$(curl -fsS "http://localhost:$VREG_PORT/v2/_catalog" 2>/dev/null)
if printf '%s' "$catalog" | grep -q 'vops5-api' && printf '%s' "$catalog" | grep -q 'vops5-web'; then
  pass "registry มี repository ครบสองก้อน : $catalog"
else
  fail "registry ไม่มี repository ที่ push ไป (ได้ '$catalog')"
fi

docker image rm -f "localhost:$VREG_PORT/vops5-web:1.0" >/dev/null 2>&1
if docker pull -q "localhost:$VREG_PORT/vops5-web:1.0" >/dev/null 2>&1; then
  pass "ลบ image ในเครื่องแล้ว docker pull กลับมาจาก registry ได้"
else
  fail "docker pull กลับมาจาก registry ไม่สำเร็จ"
fi

if docker run --rm "localhost:$VREG_PORT/vops5-web:1.0" ls .next/static >/dev/null 2>&1; then
  pass "image ที่ pull กลับมารันได้จริง (เห็นไฟล์ผลลัพธ์ของหน้าเว็บใน image)"
else
  fail "image ที่ pull กลับมารันไม่ได้"
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
