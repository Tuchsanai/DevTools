#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 4 (ต่อสามกล่องด้วยชื่อ + ปิดฐานข้อมูลจากภายนอก) ทำได้ครบจริง
# รันจากในโฟลเดอร์ LAB บนกล่องเรียน :  bash verify.sh
#
# สคริปต์นี้สร้างของของตัวเองด้วย prefix "vops4-" เท่านั้น และลบเฉพาะของตัวเองตอนจบ
# ไม่แตะ container / network / volume ที่ผู้เรียนสร้างไว้ (prefix "ops-") เด็ดขาด

set -u

cd "$(dirname "$0")" || exit 1

failures=0
tmp_dir=""

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  docker rm -f vops4-web vops4-api vops4-db vops4-probe >/dev/null 2>&1
  docker network rm vops4-net >/dev/null 2>&1
  docker volume rm vops4-pgdata >/dev/null 2>&1
  docker image rm vops4-web:verify vops4-api:verify >/dev/null 2>&1
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

# IP ของกล่องบน network ที่ระบุ
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
  fail "สั่ง docker info ไม่ผ่าน — ยังไม่ได้อยู่ในกล่องเรียนหรือ daemon ไม่ทำงาน"
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
docker rm -f vops4-web vops4-api vops4-db vops4-probe >/dev/null 2>&1
docker network rm vops4-net >/dev/null 2>&1
docker volume rm vops4-pgdata >/dev/null 2>&1

if docker network create vops4-net >/dev/null 2>&1; then
  drv=$(docker network inspect vops4-net --format '{{.Driver}}' 2>/dev/null)
  if [ "$drv" = "bridge" ]; then
    pass "docker network create ได้ network ชนิด bridge (vops4-net)"
  else
    fail "network ที่สร้างได้เป็นชนิด '$drv' ไม่ใช่ bridge"
  fi
else
  fail "สร้าง network vops4-net ไม่สำเร็จ"
fi

# ---------- 3) ยกฐานข้อมูลขึ้นบน network นั้น โดยไม่ publish พอร์ต (NFR-3) ----------
if docker run -d --name vops4-db --network vops4-net \
     -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
     -v vops4-pgdata:/var/lib/postgresql/data \
     -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
     postgres:17-alpine >/dev/null 2>&1; then
  pass "ยกกล่องฐานข้อมูล vops4-db ขึ้นบน vops4-net ได้ (ไม่ใส่ -p)"
else
  fail "ยกกล่องฐานข้อมูล vops4-db ไม่ขึ้น"
fi

if wait_db vops4-db; then
  pass "ฐานข้อมูลรัน init script เสร็จและพร้อมรับ connection แล้ว"
else
  fail "ฐานข้อมูลไม่พร้อมภายใน 90 วินาที"
fi

# ---------- 4) NFR-3 : ต้องไม่มีพอร์ตของ db โผล่ออกมาที่เครื่องเลย ----------
port_out=$(docker port vops4-db 2>/dev/null)
if [ -z "$port_out" ]; then
  pass "docker port vops4-db ไม่คืนบรรทัดใดเลย — ไม่มีพอร์ตถูก publish (NFR-3)"
else
  fail "ฐานข้อมูลถูก publish พอร์ตออกมา : $port_out"
fi

bindings=$(docker inspect -f '{{json .NetworkSettings.Ports}}' vops4-db 2>/dev/null)
case "$bindings" in
  *'"HostPort"'*) fail "NetworkSettings.Ports ของ vops4-db มี HostPort ผูกอยู่ : $bindings" ;;
  *)              pass "NetworkSettings.Ports ของ vops4-db ไม่มี HostPort ผูกไว้เลย" ;;
esac

if curl -s -m 5 -o /dev/null "http://localhost:5432" 2>/dev/null; then
  fail "พอร์ต 5432 บนกล่องเรียนมีคนตอบ — ฐานข้อมูลถูกเปิดออกมาแล้ว"
else
  pass "ยิง curl http://localhost:5432 จากกล่องเรียนแล้วต่อไม่ติด (ตามที่ NFR-3 ต้องการ)"
fi

# ---------- 5) api ต่อ db ด้วย "ชื่อ" ไม่ใช่ IP ----------
docker build -t vops4-api:verify ./api >"$tmp_dir/api.log" 2>&1
if docker run -d --name vops4-api --network vops4-net \
     -e DATABASE_URL="postgresql://opsuser:labpass@vops4-db:5432/campusops" \
     vops4-api:verify >/dev/null 2>&1; then
  pass "ยกกล่อง vops4-api ขึ้นบน vops4-net โดยใส่ชื่อกล่อง vops4-db ใน DATABASE_URL"
else
  fail "ยกกล่อง vops4-api ไม่ขึ้น (ดู $tmp_dir/api.log)"
fi

API_IP=""
api_ok=0
for _ in $(seq 1 40); do
  API_IP=$(ip_on vops4-api vops4-net)
  if [ -n "$API_IP" ] && curl -fsS "http://$API_IP:8000/health" 2>/dev/null | grep -q '"db":"up"'; then
    api_ok=1; break
  fi
  sleep 1
done
[ "$api_ok" -eq 1 ] && pass "/health ตอบ db up ทั้งที่ DATABASE_URL ไม่มีเลข IP อยู่เลย" \
                    || fail "/health ไม่ตอบว่า db up ภายใน 40 วินาที"

# ---------- 6) DNS ของ user-defined network ต้องแปลชื่อเป็น IP ได้ ----------
resolved=$(docker exec vops4-api getent hosts vops4-db 2>/dev/null | awk '{print $1}')
db_ip=$(ip_on vops4-db vops4-net)
if [ -n "$resolved" ] && [ "$resolved" = "$db_ip" ]; then
  pass "getent hosts vops4-db ในกล่อง api ได้ $resolved ตรงกับ IP จริงของ vops4-db"
else
  fail "แปลชื่อ vops4-db ไม่ได้หรือได้คนละเลข (getent='$resolved' · inspect='$db_ip')"
fi

# ---------- 7) default bridge ต้องแปลชื่อไม่ได้ (ของเทียบ) ----------
docker run -d --name vops4-probe postgres:17-alpine sleep 300 >/dev/null 2>&1
if docker exec vops4-probe getent hosts vops4-db >/dev/null 2>&1; then
  fail "กล่องบน default bridge แปลชื่อ vops4-db ได้ — ผิดจากที่เอกสารอธิบายไว้"
else
  pass "กล่องบน default bridge แปลชื่อ vops4-db ไม่ได้ (ยืนยันว่า default bridge ไม่มี DNS)"
fi

# ---------- 8) docker network connect ให้กล่องที่รันอยู่แล้ว ----------
if docker network connect vops4-net vops4-probe >/dev/null 2>&1 &&
   docker exec vops4-probe getent hosts vops4-db >/dev/null 2>&1; then
  pass "docker network connect กับกล่องที่รันอยู่แล้ว ทำให้แปลชื่อ vops4-db ได้ทันที"
else
  fail "หลัง docker network connect แล้วยังแปลชื่อ vops4-db ไม่ได้"
fi

# ---------- 9) สร้าง db ใหม่แล้วชื่อยังใช้ได้ แม้ IP เปลี่ยน ----------
docker rm -f vops4-db >/dev/null 2>&1
docker run -d --name vops4-db --network vops4-net \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v vops4-pgdata:/var/lib/postgresql/data \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
  postgres:17-alpine >/dev/null 2>&1
db_ok=0
wait_db vops4-db && db_ok=1
new_ip=$(ip_on vops4-db vops4-net)
new_resolved=$(docker exec vops4-api getent hosts vops4-db 2>/dev/null | awk '{print $1}')
if [ "$db_ok" -eq 1 ] && [ -n "$new_resolved" ] && [ "$new_resolved" = "$new_ip" ]; then
  pass "สร้าง vops4-db ใหม่แล้ว ชื่อเดิมยังชี้ไปที่กล่องใหม่ได้ถูกต้อง ($new_resolved)"
else
  fail "สร้าง vops4-db ใหม่แล้วชื่อชี้ไม่ถูก (getent='$new_resolved' · inspect='$new_ip')"
fi

health_after=0
for _ in $(seq 1 40); do
  curl -fsS "http://$API_IP:8000/health" 2>/dev/null | grep -q '"db":"up"' && { health_after=1; break; }
  sleep 1
done
[ "$health_after" -eq 1 ] && pass "api กล่องเดิม (ไม่ได้สร้างใหม่ ไม่ได้แก้ค่าใด ๆ) ต่อ db ตัวใหม่ได้เอง" \
                          || fail "api ต่อ db ตัวใหม่ไม่ได้ภายใน 40 วินาที"

# ---------- 10) web ต่อ api ด้วยชื่อ แล้วหน้าเว็บต้องมีเนื้อหาจริง ----------
docker build -t vops4-web:verify ./web >"$tmp_dir/web.log" 2>&1
docker run -d --name vops4-web --network vops4-net \
  -e API_BASE_URL="http://vops4-api:8000" vops4-web:verify >/dev/null 2>&1
WEB_IP=""
web_ok=0
for _ in $(seq 1 40); do
  WEB_IP=$(ip_on vops4-web vops4-net)
  if [ -n "$WEB_IP" ] && curl -fsS -o "$tmp_dir/home.html" "http://$WEB_IP:3000/" 2>/dev/null; then
    web_ok=1; break
  fi
  sleep 1
done
[ "$web_ok" -eq 1 ] && pass "หน้าเว็บตอบ 200 โดยตั้ง API_BASE_URL=http://vops4-api:8000 (ชื่อล้วน ๆ)" \
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

# ---------- 11) สมาชิกของ network ต้องครบสามกล่องของระบบ ----------
members=$(docker network inspect vops4-net --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null)
ok_members=1
for n in vops4-db vops4-api vops4-web; do
  case " $members " in *" $n "*) ;; *) ok_members=0 ;; esac
done
if [ "$ok_members" -eq 1 ]; then
  pass "docker network inspect เห็นครบทั้ง vops4-db · vops4-api · vops4-web"
else
  fail "สมาชิกของ vops4-net ไม่ครบ : $members"
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
