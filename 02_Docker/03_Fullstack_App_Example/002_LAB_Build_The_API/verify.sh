#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 2 (สร้าง image ของ api) ทำได้ครบจริง
# รันจากในโฟลเดอร์ LAB บนกล่องเรียน :  bash verify.sh
#
# สคริปต์นี้สร้างของของตัวเองด้วย prefix  vops-  เท่านั้น และลบเฉพาะของตัวเองตอนจบ
# ของผู้เรียน (ops-db · ops-api · ops-api:1.0 · ops-pgdata) ไม่ถูกแตะเลย

set -u
cd "$(dirname "$0")" || exit 1

failures=0
tmp_dir=""
VPORT=18088          # พอร์ตของ verify เอง — ไม่ชนกับ 8088 ที่ผู้เรียนใช้อยู่

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  docker rm -f vops-api vops-api-p vops-db >/dev/null 2>&1
  docker volume rm vops-pgdata >/dev/null 2>&1
  docker image rm -f vops-api:verify vops-api-bad:verify >/dev/null 2>&1
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

# อ่านสถานะของ build step หนึ่ง ๆ จาก log ของ --progress=plain → CACHED / REBUILT / NOSTEP
step_status() {
  local log="$1" needle="$2" num
  num=$(grep -E '^#[0-9]+ \[[0-9]+/[0-9]+\] ' "$log" | grep -F "$needle" | head -1 | sed -E 's/^#([0-9]+) .*/\1/')
  if [ -z "$num" ]; then printf 'NOSTEP\n'; return; fi
  if grep -qE "^#${num} CACHED" "$log"; then printf 'CACHED\n'; else printf 'REBUILT\n'; fi
}

echo "=============================================="
echo " LAB 2 — สร้าง image ของบริการเบื้องหลัง : verify"
echo "=============================================="

# ---------- 0) preflight ----------
if docker info >/dev/null 2>&1; then
  pass "docker daemon ตอบสนอง"
else
  fail "docker daemon ไม่ตอบสนอง — เปิดกล่องเรียนแล้วหรือยัง"
  echo "----------------------------------------------"
  echo "1 CHECK(S) FAILED"
  exit 1
fi

# ---------- 1) ไฟล์ครบไหม ----------
missing=""
for f in api/Dockerfile api/Dockerfile.bad api/main.py api/requirements.txt api/.dockerignore \
         db/initdb/01-schema.sql db/initdb/02-seed.sql .env.db; do
  [ -f "$f" ] || missing="$missing $f"
done
if [ -z "$missing" ]; then
  pass "ไฟล์ของแล็บครบ (api/ · db/initdb/ · .env.db)"
else
  fail "ไฟล์ของแล็บไม่ครบ:$missing"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

# ---------- 2) ลำดับใน Dockerfile ต้องถูก ----------
req_line=$(grep -n '^COPY requirements.txt' api/Dockerfile | head -1 | cut -d: -f1)
pip_line=$(grep -n '^RUN pip install' api/Dockerfile | head -1 | cut -d: -f1)
code_line=$(grep -n '^COPY main.py' api/Dockerfile | head -1 | cut -d: -f1)
if [ -n "$req_line" ] && [ -n "$pip_line" ] && [ -n "$code_line" ] \
   && [ "$req_line" -lt "$pip_line" ] && [ "$pip_line" -lt "$code_line" ]; then
  pass "api/Dockerfile เรียงถูก : COPY requirements.txt -> RUN pip install -> COPY main.py"
else
  fail "api/Dockerfile เรียงลำดับไม่ถูกต้อง (ต้อง COPY requirements.txt ก่อน RUN pip install ก่อน COPY main.py)"
fi

# ---------- 3) build image ของ api ----------
tmp_dir=$(mktemp -d)
if docker build --progress=plain -t vops-api:verify api >"$tmp_dir/build1.log" 2>&1; then
  pass "build image vops-api:verify จาก api/Dockerfile สำเร็จ"
else
  fail "build image vops-api:verify ไม่สำเร็จ (ดู $tmp_dir/build1.log)"
fi

# ---------- 4) EXPOSE 8000 ต้องอยู่ใน image ----------
if docker image inspect vops-api:verify --format '{{json .Config.ExposedPorts}}' 2>/dev/null | grep -q '8000/tcp'; then
  pass "image ประกาศ EXPOSE 8000 ไว้ใน metadata"
else
  fail "image ไม่มี EXPOSE 8000 ใน metadata"
fi

# ---------- 5) หัวใจของแล็บ : แก้โค้ด 1 บรรทัดแล้ว pip install ต้อง CACHED ----------
# ทำสำเนา context ไปแก้ในที่ชั่วคราว — ไฟล์ api/main.py ของผู้เรียนไม่ถูกแตะ
ctx="$tmp_dir/ctx"
mkdir -p "$ctx"
cp api/Dockerfile api/Dockerfile.bad api/requirements.txt api/main.py api/.dockerignore "$ctx/"
printf '\n# verify build marker %s\n' "$(date +%s)" >>"$ctx/main.py"

docker build --progress=plain -t vops-api-bad:verify -f "$ctx/Dockerfile.bad" "$ctx" >"$tmp_dir/bad1.log" 2>&1
printf '\n# verify build marker %s-second\n' "$(date +%s)" >>"$ctx/main.py"

docker build --progress=plain -t vops-api:verify     -f "$ctx/Dockerfile"     "$ctx" >"$tmp_dir/good2.log" 2>&1
docker build --progress=plain -t vops-api-bad:verify -f "$ctx/Dockerfile.bad" "$ctx" >"$tmp_dir/bad2.log"  2>&1

good_pip=$(step_status "$tmp_dir/good2.log" 'RUN pip install')
bad_pip=$(step_status "$tmp_dir/bad2.log" 'RUN pip install')

if [ "$good_pip" = "CACHED" ]; then
  pass "api/Dockerfile : แก้ main.py แล้วขั้น RUN pip install ยังเป็น CACHED"
else
  fail "api/Dockerfile : ขั้น RUN pip install ควรเป็น CACHED แต่ได้ $good_pip"
fi

if [ "$bad_pip" = "REBUILT" ]; then
  pass "api/Dockerfile.bad : ขั้น RUN pip install ถูกทำใหม่ (cache แตกจริงเพราะเรียงผิดลำดับ)"
else
  fail "api/Dockerfile.bad : คาดว่า RUN pip install ต้องทำใหม่ แต่ได้ $bad_pip"
fi

# ---------- 6) .dockerignore ต้องกันไฟล์ออกจาก build context ----------
if grep -qx '\*.log' api/.dockerignore && grep -qx 'smoke.sh' api/.dockerignore; then
  pass ".dockerignore ระบุ *.log และ smoke.sh ไว้"
else
  fail ".dockerignore ต้องมีบรรทัด *.log และ smoke.sh"
fi

head -c 3000000 /dev/urandom >"$ctx/api-debug.log"
docker build --progress=plain -t vops-api:verify -f "$ctx/Dockerfile" "$ctx" >"$tmp_dir/ctx.log" 2>&1
# หาเลข step ของ "[internal] load build context" ก่อน แล้วค่อยอ่านบรรทัด transferring ของ step นั้น
# (ขั้น load .dockerignore ก็พิมพ์คำว่า context เหมือนกัน — เลือกด้วย tail -1 เฉย ๆ ไม่ปลอดภัย)
ctx_step=$(grep -E '^#[0-9]+ \[internal\] load build context' "$tmp_dir/ctx.log" | head -1 | sed -E 's/^#([0-9]+) .*/\1/')
if [ -n "$ctx_step" ]; then
  ctx_line=$(grep -E "^#${ctx_step} transferring context: " "$tmp_dir/ctx.log" | tail -1)
else
  ctx_line=""
fi
if printf '%s' "$ctx_line" | grep -qE 'transferring context: [0-9.]+(B|kB) '; then
  pass "ไฟล์ 3MB ที่ตรงกับ *.log ไม่ถูกส่งเข้า build context ($(printf '%s' "$ctx_line" | sed -E 's/^#[0-9]+ //'))"
else
  fail "build context ใหญ่ผิดปกติ — .dockerignore ไม่ได้กันไฟล์ .log ออก ($ctx_line)"
fi
rm -f "$ctx/api-debug.log"

# ---------- 7) ยกฐานข้อมูลของ verify เอง ----------
docker rm -f vops-db >/dev/null 2>&1
docker volume rm vops-pgdata >/dev/null 2>&1
if docker run -d --name vops-db --env-file .env.db \
     -v vops-pgdata:/var/lib/postgresql/data \
     -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
     postgres:17-alpine >/dev/null 2>&1; then
  db_ready=0
  for _ in $(seq 1 30); do
    if docker exec vops-db pg_isready -U opsuser -d campusops >/dev/null 2>&1; then db_ready=1; break; fi
    sleep 2
  done
  if [ "$db_ready" -eq 1 ]; then
    pass "ฐานข้อมูล vops-db พร้อมรับ connection"
  else
    fail "ฐานข้อมูล vops-db ไม่พร้อมภายในเวลาที่รอ"
  fi
else
  fail "สร้าง container vops-db ไม่สำเร็จ"
fi

db_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' vops-db 2>/dev/null)
if printf '%s' "$db_ip" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
  pass "docker inspect อ่าน IP ของ vops-db ได้ : $db_ip"
else
  fail "docker inspect อ่าน IP ของ vops-db ไม่ได้"
fi

# ---------- 8) EXPOSE ไม่ได้เปิดพอร์ต ----------
docker rm -f vops-api >/dev/null 2>&1
docker run -d --name vops-api \
  -e DATABASE_URL="postgresql://opsuser:labpass@${db_ip}:5432/campusops" \
  vops-api:verify >/dev/null 2>&1
sleep 1
if [ -z "$(docker port vops-api 2>/dev/null)" ]; then
  pass "รันโดยไม่ใส่ -p แล้ว docker port ไม่มีรายการ — EXPOSE ไม่ได้เปิดพอร์ตให้"
else
  fail "รันโดยไม่ใส่ -p แต่ docker port กลับมีรายการ"
fi
docker rm -f vops-api >/dev/null 2>&1

# ---------- 9) รันจริงพร้อม -p แล้ว /health ต้องเขียว ----------
if docker run -d --name vops-api-p -p "${VPORT}:8000" \
     -e DATABASE_URL="postgresql://opsuser:labpass@${db_ip}:5432/campusops" \
     vops-api:verify >/dev/null 2>&1; then
  health_ok=0
  for _ in $(seq 1 20); do
    if curl -fsS "http://localhost:${VPORT}/health" 2>/dev/null | grep -q '"db":"up"'; then health_ok=1; break; fi
    sleep 1
  done
  if [ "$health_ok" -eq 1 ]; then
    pass "GET /health ตอบ {\"status\":\"ok\",\"db\":\"up\"} ผ่านพอร์ต ${VPORT}"
  else
    fail "GET /health ไม่ตอบว่า db up ผ่านพอร์ต ${VPORT}"
  fi
else
  fail "รัน container vops-api-p พร้อม -p ${VPORT}:8000 ไม่สำเร็จ"
fi

if curl -fsS -o /dev/null "http://localhost:${VPORT}/docs" 2>/dev/null; then
  pass "หน้า /docs ของ FastAPI เปิดได้ผ่านพอร์ต ${VPORT}"
else
  fail "หน้า /docs เปิดไม่ได้ผ่านพอร์ต ${VPORT}"
fi

# ---------- 10) REQ-01 : สร้างใบแจ้งซ่อมได้ 201 ----------
create_body=$(curl -s -o "$tmp_dir/create.json" -w '%{http_code}' \
  -X POST "http://localhost:${VPORT}/api/tickets" \
  -H 'Content-Type: application/json' \
  -d '{"asset_id":1,"title":"verify ticket","detail":"สร้างโดย verify.sh","priority":"HIGH"}')
if [ "$create_body" = "201" ] && grep -q '"status":"NEW"' "$tmp_dir/create.json"; then
  pass "REQ-01 : POST /api/tickets ได้ 201 และใบใหม่มีสถานะ NEW"
else
  fail "REQ-01 : POST /api/tickets ได้ $create_body (เนื้อหา: $(head -c 200 "$tmp_dir/create.json" 2>/dev/null))"
fi

new_id=$(sed -E 's/^\{"id":([0-9]+).*/\1/' "$tmp_dir/create.json" 2>/dev/null)

# ---------- 11) REQ-02 : ข้ามสถานะไม่ได้ 409 INVALID_TRANSITION ----------
if printf '%s' "$new_id" | grep -qE '^[0-9]+$'; then
  patch_code=$(curl -s -o "$tmp_dir/patch.json" -w '%{http_code}' \
    -X PATCH "http://localhost:${VPORT}/api/tickets/${new_id}/status" \
    -H 'Content-Type: application/json' -d '{"status":"DONE"}')
  if [ "$patch_code" = "409" ] && grep -q 'INVALID_TRANSITION' "$tmp_dir/patch.json"; then
    pass "REQ-02 : สั่ง NEW -> DONE ได้ 409 INVALID_TRANSITION"
  else
    fail "REQ-02 : สั่ง NEW -> DONE ได้ $patch_code (เนื้อหา: $(head -c 200 "$tmp_dir/patch.json" 2>/dev/null))"
  fi

  still_new=$(curl -s "http://localhost:${VPORT}/api/tickets?status=NEW" | grep -c "\"id\":${new_id},")
  if [ "$still_new" -ge 1 ]; then
    pass "REQ-02 : ใบหมายเลข ${new_id} ยังอยู่ในสถานะ NEW เหมือนเดิม"
  else
    fail "REQ-02 : ใบหมายเลข ${new_id} ไม่ได้อยู่ในสถานะ NEW แล้ว"
  fi
else
  fail "อ่านหมายเลขใบแจ้งซ่อมที่เพิ่งสร้างไม่ได้ จึงตรวจ REQ-02 ต่อไม่ได้"
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
