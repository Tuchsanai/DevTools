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
SHIP_NS=localverify           # namespace ทดสอบเฉพาะใน Docker daemon ไม่ติดต่อ registry จริง

dc() { docker compose -p "$VP" -f compose.yaml -f "$tmp_dir/verify-override.yaml" "$@"; }

cleanup() {
  if [ -n "$tmp_dir" ] && [ -f "$tmp_dir/verify-override.yaml" ]; then
    docker compose -p "$VP" -f compose.yaml -f "$tmp_dir/verify-override.yaml" down -v >/dev/null 2>&1
  fi
  docker image rm -f "$SHIP_NS/campusops-api:1.0" "$SHIP_NS/campusops-web:1.0" >/dev/null 2>&1
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

# ---------- 14) ส่งมอบแบบออฟไลน์ : tag -> save -> remove -> load ----------
api_id=$(docker image inspect -f '{{.Id}}' "${VP}-api" 2>/dev/null)
web_id=$(docker image inspect -f '{{.Id}}' "${VP}-web" 2>/dev/null)
docker tag "${VP}-api" "$SHIP_NS/campusops-api:1.0" >/dev/null 2>&1
docker tag "${VP}-web" "$SHIP_NS/campusops-web:1.0" >/dev/null 2>&1

tagged_api_id=$(docker image inspect -f '{{.Id}}' "$SHIP_NS/campusops-api:1.0" 2>/dev/null)
tagged_web_id=$(docker image inspect -f '{{.Id}}' "$SHIP_NS/campusops-web:1.0" 2>/dev/null)
[ -n "$api_id" ] && [ "$api_id" = "$tagged_api_id" ] \
  && pass "tag repository ให้ api แล้ว IMAGE ID ยังเป็นก้อนเดิม" \
  || fail "tag api แล้ว IMAGE ID เปลี่ยนหรือหา image ไม่พบ"
[ -n "$web_id" ] && [ "$web_id" = "$tagged_web_id" ] \
  && pass "tag repository ให้ web แล้ว IMAGE ID ยังเป็นก้อนเดิม" \
  || fail "tag web แล้ว IMAGE ID เปลี่ยนหรือหา image ไม่พบ"

archive="$tmp_dir/campusops-images.tar"
if docker save -o "$archive" "$SHIP_NS/campusops-api:1.0" "$SHIP_NS/campusops-web:1.0" \
   && [ -s "$archive" ]; then
  pass "docker save รวม image ทั้งสองก้อนเป็นไฟล์ส่งมอบได้"
else
  fail "docker save สร้างไฟล์ส่งมอบไม่สำเร็จ"
fi

dc down >/dev/null 2>&1
docker image rm "${VP}-api" "${VP}-web" >/dev/null 2>&1
docker image rm "$SHIP_NS/campusops-api:1.0" "$SHIP_NS/campusops-web:1.0" >/dev/null 2>&1
if ! docker image inspect "${VP}-api" "${VP}-web" "$SHIP_NS/campusops-api:1.0" "$SHIP_NS/campusops-web:1.0" >/dev/null 2>&1; then
  pass "ลบ image ต้นทางและชื่อสำหรับส่งมอบออกจากเครื่องแล้ว"
else
  fail "ยังมี image ทดสอบเหลือก่อน docker load"
fi

if docker load -i "$archive" >/dev/null 2>&1; then
  pass "docker load คืน image ทั้งสองก้อนจากไฟล์ส่งมอบได้"
else
  fail "docker load ไฟล์ส่งมอบไม่สำเร็จ"
fi

docker tag "$SHIP_NS/campusops-api:1.0" "${VP}-api:latest" >/dev/null 2>&1
docker tag "$SHIP_NS/campusops-web:1.0" "${VP}-web:latest" >/dev/null 2>&1
if dc up -d --no-build >"$tmp_dir/no-build.log" 2>&1; then
  pass "docker compose up -d --no-build ขึ้นครบจาก image ที่ load กลับมา"
else
  fail "docker compose up -d --no-build ไม่สำเร็จ"
fi

healthy_loaded=0
for _ in $(seq 1 60); do
  n=$(docker inspect -f '{{.State.Health.Status}}' "${VP}-db-1" "${VP}-api-1" "${VP}-web-1" 2>/dev/null | grep -c '^healthy$')
  if [ "$n" = "3" ]; then healthy_loaded=1; break; fi
  sleep 2
done
[ "$healthy_loaded" = "1" ] \
  && pass "ระบบที่ load กลับมามีสถานะ healthy ครบ 3 service" \
  || fail "ระบบที่ load กลับมามี service ไม่ healthy ภายใน 120 วินาที"

if curl -fsS -o /dev/null "http://localhost:$VWEB_PORT/"; then
  pass "ระบบที่ส่งมอบแบบออฟไลน์ตอบ HTTP 200"
else
  fail "ระบบที่ส่งมอบแบบออฟไลน์ไม่ตอบ HTTP 200"
fi

if grep -q 'Building' "$tmp_dir/no-build.log"; then
  fail "log ของ --no-build มีบรรทัด Building"
else
  pass "log ของ --no-build ไม่มีบรรทัด Building"
fi

# ---------- 15) Docker Hub จริงเป็น opt-in และไม่มี push/delete ----------
if [ -z "${HUB_USER:-}" ]; then
  echo "[SKIP] ไม่ตรวจ Docker Hub จริง — ตั้ง HUB_USER แล้ว tag/push ตามการทดลองที่ 8 เพื่อเปิดการตรวจ"
elif [ ! -f /root/.docker/config.json ] \
     || ! grep -q 'https://index.docker.io/v1/' /root/.docker/config.json; then
  echo "[SKIP] ยังไม่ได้ docker login ในกล่องเรียน — login ด้วย Access Token แล้วรันใหม่"
else
  hub_local=0
  docker image inspect "$HUB_USER/campusops-api:1.0" "$HUB_USER/campusops-web:1.0" >/dev/null 2>&1 \
    && hub_local=1
  if [ "$hub_local" = "1" ]; then
    pass "ติดชื่อ repository ของ Docker Hub ให้ image ทั้งสองก้อนแล้ว"
  else
    echo "[SKIP] ไม่พบ $HUB_USER/campusops-api:1.0 และ campusops-web:1.0 ในเครื่อง — ทำการทดลองที่ 8 ก่อน"
  fi
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
