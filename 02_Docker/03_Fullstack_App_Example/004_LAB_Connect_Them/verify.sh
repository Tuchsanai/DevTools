#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 4 เชื่อม Container ทั้งสามด้วยชื่อและปิด Database จากภายนอกได้
# รันจากในโฟลเดอร์ LAB บน Container สำหรับเรียน: bash verify.sh
#
# สคริปต์นี้สร้างของของตัวเองด้วย prefix "devtools-lab004-check-" เท่านั้น และลบเฉพาะของตัวเองตอนจบ
# ไม่แตะ Container, Network หรือ Volume ที่ผู้เรียนสร้างไว้ (prefix "devtools-connect-")

set -u

cd "$(dirname "$0")" || exit 1

failures=0
tmp_dir=""

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  docker rm -f -v devtools-lab004-check-web devtools-lab004-check-api devtools-lab004-check-db devtools-lab004-check-probe >/dev/null 2>&1
  docker network rm devtools-lab004-check-net >/dev/null 2>&1
  docker volume rm devtools-lab004-check-pgdata >/dev/null 2>&1
  docker image rm devtools-lab004-check-web:verify devtools-lab004-check-api:verify >/dev/null 2>&1
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

# IP address ของ Container บน Network ที่ระบุ
ip_on() { docker inspect -f "{{index .NetworkSettings.Networks \"$2\" \"IPAddress\"}}" "$1" 2>/dev/null; }

# รอจน postgres พร้อมรับ connection ของจริง แล้วค่อยยอมให้ query
# (pg_isready ผ่านตั้งแต่เซิร์ฟเวอร์ชั่วคราวของ initdb ยังทำงานอยู่ จึงเชื่อตัวเดียวไม่ได้
#  ต้องเห็น log ว่า init เสร็จ "init process complete" หรือ volume ไม่ว่างจน initdb ถูกข้าม
#  "Skipping initialization" เสียก่อน — postgres เขียน log ลง stderr จึงต้อง 2>&1 ทุกครั้ง)
wait_db() {
  local name="$1" i
  for i in $(seq 1 90); do
    if docker logs "$name" 2>&1 | grep -qE 'init process complete|Skipping initialization'; then
      if docker exec "$name" pg_isready -U opsuser -d campusops >/dev/null 2>&1; then return 0; fi
    fi
    sleep 1
  done
  return 1
}

echo "=============================================="
echo " LAB 4 — Connect Them (network + ชื่อ) : verify"
echo "=============================================="

# ---------- preflight ----------
if docker info >/dev/null 2>&1; then
  pass "ต่อกับ Docker daemon ได้"
else
  fail "สั่ง docker info ไม่ผ่าน — ยังไม่ได้อยู่ใน Container สำหรับเรียน หรือ Docker daemon ไม่ทำงาน"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

tmp_dir=$(mktemp -d)

# ---------- 1) ไฟล์ของแล็บครบไหม ----------
missing=""
for f in api/Dockerfile api/main.py web/Dockerfile web/package.json \
         db/initdb/01-schema.sql db/initdb/02-seed.sql; do
  [ -f "$f" ] || missing="$missing $f"
done
if [ -z "$missing" ]; then
  pass "ไฟล์ของแล็บครบ (api/ · web/ · db/initdb/)"
else
  fail "ไฟล์ของแล็บไม่ครบ:$missing"
  echo "----------------------------------------------"
  printf '%s CHECK(S) FAILED\n' "$failures"
  exit 1
fi

# ---------- 2) สร้าง network ของตัวเอง ----------
docker rm -f -v devtools-lab004-check-web devtools-lab004-check-api devtools-lab004-check-db devtools-lab004-check-probe >/dev/null 2>&1
docker network rm devtools-lab004-check-net >/dev/null 2>&1
docker volume rm devtools-lab004-check-pgdata >/dev/null 2>&1

if docker network create devtools-lab004-check-net >/dev/null 2>&1; then
  drv=$(docker network inspect devtools-lab004-check-net --format '{{.Driver}}' 2>/dev/null)
  if [ "$drv" = "bridge" ]; then
    pass "docker network create ได้ network ชนิด bridge (devtools-lab004-check-net)"
  else
    fail "network ที่สร้างได้เป็นชนิด '$drv' ไม่ใช่ bridge"
  fi
else
  fail "สร้าง network devtools-lab004-check-net ไม่สำเร็จ"
fi

# NFR ย่อมาจาก Non-Functional Requirement; NFR-3 กำหนดให้ Database ไม่มี Published Port
# ---------- 3) เริ่ม Database บน Network โดยไม่ Publish Port (NFR-3) ----------
if docker run -d --name devtools-lab004-check-db --network devtools-lab004-check-net \
     -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
     -v devtools-lab004-check-pgdata:/var/lib/postgresql/data \
     -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
     postgres:17-alpine >/dev/null 2>&1; then
  pass "เริ่ม Database Container devtools-lab004-check-db บน devtools-lab004-check-net ได้ (ไม่ใส่ -p)"
else
  fail "เริ่ม Database Container devtools-lab004-check-db ไม่สำเร็จ"
fi

if wait_db devtools-lab004-check-db; then
  pass "ฐานข้อมูลรัน init script เสร็จและพร้อมรับ connection แล้ว"
else
  fail "ฐานข้อมูลไม่พร้อมภายใน 90 วินาที"
fi

# ---------- 4) NFR-3 : ต้องไม่มีพอร์ตของ db โผล่ออกมาที่เครื่องเลย ----------
port_out=$(docker port devtools-lab004-check-db 2>/dev/null)
if [ -z "$port_out" ]; then
  pass "docker port devtools-lab004-check-db ไม่คืนบรรทัดใดเลย — ไม่มีพอร์ตถูก publish (NFR-3)"
else
  fail "ฐานข้อมูลถูก publish พอร์ตออกมา : $port_out"
fi

bindings=$(docker inspect -f '{{json .NetworkSettings.Ports}}' devtools-lab004-check-db 2>/dev/null)
case "$bindings" in
  *'"HostPort"'*) fail "NetworkSettings.Ports ของ devtools-lab004-check-db มี HostPort ผูกอยู่ : $bindings" ;;
  *)              pass "NetworkSettings.Ports ของ devtools-lab004-check-db ไม่มี HostPort ผูกไว้เลย" ;;
esac

if curl -s -m 5 -o /dev/null "http://localhost:5432" 2>/dev/null; then
  fail "พอร์ต 5432 บน Container สำหรับเรียนมีการตอบกลับ — Database ถูกเปิดออกมาแล้ว"
else
  pass "curl http://localhost:5432 จาก Container สำหรับเรียนเชื่อมต่อไม่ได้ (ตรงตาม NFR-3)"
fi

# ---------- 5) api ต่อ db ด้วย "ชื่อ" ไม่ใช่ IP ----------
docker build -t devtools-lab004-check-api:verify ./api >"$tmp_dir/api.log" 2>&1
if docker run -d --name devtools-lab004-check-api --network devtools-lab004-check-net \
     -e DATABASE_URL="postgresql://opsuser:labpass@devtools-lab004-check-db:5432/campusops" \
     devtools-lab004-check-api:verify >/dev/null 2>&1; then
  pass "เริ่ม API Container devtools-lab004-check-api บน devtools-lab004-check-net โดยใช้ชื่อ Container devtools-lab004-check-db ใน DATABASE_URL"
else
  fail "เริ่ม API Container devtools-lab004-check-api ไม่สำเร็จ (ดู $tmp_dir/api.log)"
fi

API_IP=""
api_ok=0
for _ in $(seq 1 40); do
  API_IP=$(ip_on devtools-lab004-check-api devtools-lab004-check-net)
  if [ -n "$API_IP" ] && curl -fsS "http://$API_IP:8000/health" 2>/dev/null | grep -q '"db":"up"'; then
    api_ok=1; break
  fi
  sleep 1
done
[ "$api_ok" -eq 1 ] && pass "/health ตอบ db up ทั้งที่ DATABASE_URL ไม่มีเลข IP อยู่เลย" \
                    || fail "/health ไม่ตอบว่า db up ภายใน 40 วินาที"

# ---------- 6) DNS ของ user-defined network ต้องแปลชื่อเป็น IP ได้ ----------
resolved=$(docker exec devtools-lab004-check-api getent hosts devtools-lab004-check-db 2>/dev/null | awk '{print $1}')
db_ip=$(ip_on devtools-lab004-check-db devtools-lab004-check-net)
if [ -n "$resolved" ] && [ "$resolved" = "$db_ip" ]; then
  pass "getent hosts devtools-lab004-check-db ใน API Container ได้ $resolved ตรงกับ IP address จริงของ devtools-lab004-check-db"
else
  fail "แปลชื่อ devtools-lab004-check-db ไม่ได้หรือได้คนละเลข (getent='$resolved' · inspect='$db_ip')"
fi

# ---------- 7) default bridge ต้องแปลชื่อไม่ได้ (ของเทียบ) ----------
docker run -d --name devtools-lab004-check-probe postgres:17-alpine sleep 300 >/dev/null 2>&1
if docker exec devtools-lab004-check-probe getent hosts devtools-lab004-check-db >/dev/null 2>&1; then
  fail "Container บน Default bridge แปลชื่อ devtools-lab004-check-db ได้ — ไม่ตรงกับแบบจำลองในเอกสาร"
else
  pass "Container บน Default bridge แปลชื่อ devtools-lab004-check-db ไม่ได้"
fi

# ---------- 8) docker network connect ให้ Container ที่ทำงานอยู่แล้ว ----------
if docker network connect devtools-lab004-check-net devtools-lab004-check-probe >/dev/null 2>&1 &&
   docker exec devtools-lab004-check-probe getent hosts devtools-lab004-check-db >/dev/null 2>&1; then
  pass "docker network connect เชื่อม Container ที่ทำงานอยู่แล้วและทำให้แปลชื่อ devtools-lab004-check-db ได้ทันที"
else
  fail "หลัง docker network connect แล้วยังแปลชื่อ devtools-lab004-check-db ไม่ได้"
fi

# ---------- 9) สร้าง db ใหม่แล้วชื่อยังใช้ได้ แม้ IP เปลี่ยน ----------
docker rm -f -v devtools-lab004-check-db >/dev/null 2>&1
docker run -d --name devtools-lab004-check-db --network devtools-lab004-check-net \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v devtools-lab004-check-pgdata:/var/lib/postgresql/data \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
  postgres:17-alpine >/dev/null 2>&1
db_ok=0
wait_db devtools-lab004-check-db && db_ok=1
new_ip=$(ip_on devtools-lab004-check-db devtools-lab004-check-net)
new_resolved=$(docker exec devtools-lab004-check-api getent hosts devtools-lab004-check-db 2>/dev/null | awk '{print $1}')
if [ "$db_ok" -eq 1 ] && [ -n "$new_resolved" ] && [ "$new_resolved" = "$new_ip" ]; then
  pass "สร้าง devtools-lab004-check-db ใหม่แล้ว ชื่อเดิมยังชี้ไปที่ Container ใหม่ได้ถูกต้อง ($new_resolved)"
else
  fail "สร้าง devtools-lab004-check-db ใหม่แล้วชื่อชี้ไม่ถูก (getent='$new_resolved' · inspect='$new_ip')"
fi

health_after=0
for _ in $(seq 1 40); do
  curl -fsS "http://$API_IP:8000/health" 2>/dev/null | grep -q '"db":"up"' && { health_after=1; break; }
  sleep 1
done
[ "$health_after" -eq 1 ] && pass "API Container เดิม (ไม่ได้สร้างใหม่ ไม่ได้แก้ค่าใด ๆ) ต่อ Database Container ใหม่ได้เอง" \
                          || fail "api ต่อ db ตัวใหม่ไม่ได้ภายใน 40 วินาที"

# ---------- 10) web ต่อ api ด้วยชื่อ แล้วหน้าเว็บต้องมีเนื้อหาจริง ----------
docker build -t devtools-lab004-check-web:verify ./web >"$tmp_dir/web.log" 2>&1
docker run -d --name devtools-lab004-check-web --network devtools-lab004-check-net \
  -e API_BASE_URL="http://devtools-lab004-check-api:8000" devtools-lab004-check-web:verify >/dev/null 2>&1
WEB_IP=""
web_ok=0
for _ in $(seq 1 40); do
  WEB_IP=$(ip_on devtools-lab004-check-web devtools-lab004-check-net)
  if [ -n "$WEB_IP" ] && curl -fsS -o "$tmp_dir/home.html" "http://$WEB_IP:3000/" 2>/dev/null; then
    web_ok=1; break
  fi
  sleep 1
done
[ "$web_ok" -eq 1 ] && pass "หน้าเว็บตอบ 200 โดยตั้ง API_BASE_URL=http://devtools-lab004-check-api:8000 (ชื่อล้วน ๆ)" \
                    || fail "หน้าเว็บไม่ตอบ (ดู $tmp_dir/web.log)"

if [ "$web_ok" -eq 1 ]; then
  if grep -q 'งานค้างเกินกำหนด' "$tmp_dir/home.html"; then
    pass "หน้าแรกมีเนื้อหาที่วิ่งครบสายจริง : เบราว์เซอร์ → web → api → db"
  else
    fail "หน้าแรกไม่มีเนื้อหาที่มาจากฐานข้อมูล"
  fi

  pages_ok=1
  for p in /tickets /loans /parts; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://$WEB_IP:3000$p")
    [ "$code" = "200" ] || { pages_ok=0; fail "หน้า $p ตอบ $code ไม่ใช่ 200"; }
  done
  [ "$pages_ok" -eq 1 ] && pass "หน้า /tickets · /loans · /parts ตอบ 200 ครบ"
fi

# ---------- 11) สมาชิกของ Network ต้องครบ Container ทั้งสามของระบบ ----------
members=$(docker network inspect devtools-lab004-check-net --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null)
ok_members=1
for n in devtools-lab004-check-db devtools-lab004-check-api devtools-lab004-check-web; do
  case " $members " in *" $n "*) ;; *) ok_members=0 ;; esac
done
if [ "$ok_members" -eq 1 ]; then
  pass "docker network inspect เห็นครบทั้ง devtools-lab004-check-db · devtools-lab004-check-api · devtools-lab004-check-web"
else
  fail "สมาชิกของ devtools-lab004-check-net ไม่ครบ : $members"
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
