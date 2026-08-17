#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 1 (ยกฐานข้อมูล CampusOps ขึ้นและทำให้ข้อมูลไม่หาย) ทำได้ครบจริง
# รันจากในโฟลเดอร์ LAB บนเครื่องเรียน :  bash verify.sh
# สคริปต์นี้สร้าง/ลบเฉพาะของตัวเอง : container ชื่อขึ้นต้น vops- และ volume ชื่อ vops-*
# ของผู้เรียน (ops-db, ops-pgdata) จะไม่ถูกแตะต้องเลย

set -u

cd "$(dirname "$0")" || exit 1

failures=0
pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  docker rm -f vops-db1 vops-db2 vops-db3 vops-db4 vops-db5 vops-nopass >/dev/null 2>&1
  docker volume rm vops1-pgdata >/dev/null 2>&1
  return 0
}
trap cleanup EXIT INT TERM

# ---------- helper ----------
# รอจน postgres ในกล่องพร้อมใช้งานจริง
# สองจังหวะ เพราะระหว่าง init postgres เปิดเซิร์ฟเวอร์ "ชั่วคราว" ไว้ก่อน
# ถ้าเช็กแค่ pg_isready จะผ่านตั้งแต่ seed ยังไม่ถูกรัน แล้วนับแถวได้ค่าว่าง
wait_pg() {
  local name="$1" i
  for i in $(seq 1 60); do   # จังหวะที่ 1 : init จบแล้วหรือถูกข้ามไปแล้ว
    if docker logs "$name" 2>&1 | grep -qE 'PostgreSQL init process complete|Skipping initialization'; then
      break
    fi
    sleep 1
  done
  for i in $(seq 1 40); do   # จังหวะที่ 2 : เซิร์ฟเวอร์ตัวจริงตอบคำถามได้
    if [ "$(docker exec "$name" psql -U opsuser -d campusops -tAc 'SELECT 1' 2>/dev/null | tr -d '[:space:]')" = "1" ]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

# นับแถวของตารางเดียว คืนตัวเลขล้วน (ว่าง = ถามไม่สำเร็จ)
count_of() {
  docker exec "$1" psql -U opsuser -d campusops -tAc "SELECT count(*) FROM $2;" 2>/dev/null | tr -d '[:space:]'
}

run_db() {  # run_db <ชื่อกล่อง> <อาร์กิวเมนต์เพิ่มเติม...>
  local name="$1"; shift
  docker run -d --name "$name" \
    -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
    "$@" \
    -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
    postgres:17-alpine >/dev/null 2>&1
}

echo "=============================================="
echo " LAB 1 — Run The System (CampusOps db) : verify"
echo "=============================================="

# ---------- 0) preflight ----------
if docker info >/dev/null 2>&1; then
  pass "ต่อ Docker daemon ได้"
else
  fail "ต่อ Docker daemon ไม่ได้ — ต้องรันในกล่องเรียนที่ dockerd ทำงานอยู่"
  echo "1 CHECK(S) FAILED"
  exit 1
fi

# ---------- 1) ไฟล์ของแล็บครบไหม ----------
missing=""
for f in db/initdb/01-schema.sql db/initdb/02-seed.sql .env.db readme.md; do
  [ -f "$f" ] || missing="$missing $f"
done
if [ -z "$missing" ]; then
  pass "ไฟล์ของแล็บครบ (db/initdb/01-schema.sql, db/initdb/02-seed.sql, .env.db, readme.md)"
else
  fail "ไฟล์ของแล็บไม่ครบ:$missing"
  echo "$failures CHECK(S) FAILED"
  exit 1
fi

cleanup   # เผื่อรอบก่อนค้าง

# ---------- 2) ไม่ใส่ POSTGRES_PASSWORD ต้องขึ้นไม่ได้ ----------
docker run -d --name vops-nopass postgres:17-alpine >/dev/null 2>&1
sleep 3
nopass_state=$(docker inspect -f '{{.State.Status}}:{{.State.ExitCode}}' vops-nopass 2>/dev/null)
if docker logs vops-nopass 2>&1 | grep -q 'You must specify POSTGRES_PASSWORD'; then
  pass "ไม่ใส่ POSTGRES_PASSWORD แล้วกล่องหยุดพร้อมข้อความเตือน (state=$nopass_state)"
else
  fail "คาดว่าไม่ใส่ POSTGRES_PASSWORD แล้วต้องมีข้อความ 'You must specify POSTGRES_PASSWORD' แต่ไม่พบ (state=$nopass_state)"
fi
docker rm -f vops-nopass >/dev/null 2>&1

# ---------- 3) initdb สร้างตารางครบ 5 ตาราง ----------
run_db vops-db1
if wait_pg vops-db1; then
  pass "กล่อง vops-db1 ขึ้นและรับ connection ได้"
else
  fail "กล่อง vops-db1 ไม่พร้อมรับ connection ภายใน 40 วินาที"
  echo "$failures CHECK(S) FAILED"
  exit 1
fi

tables=$(docker exec vops-db1 psql -U opsuser -d campusops -tAc \
  "SELECT string_agg(tablename, ',' ORDER BY tablename) FROM pg_tables WHERE schemaname='public';" 2>/dev/null | tr -d '[:space:]')
if [ "$tables" = "assets,loans,parts,stock_moves,tickets" ]; then
  pass "initdb สร้างตารางครบ 5 ตาราง : $tables"
else
  fail "ตารางไม่ครบตามสัญญา — ต้องได้ assets,loans,parts,stock_moves,tickets แต่ได้ '$tables'"
fi

if docker logs vops-db1 2>&1 | grep -q 'running /docker-entrypoint-initdb.d/01-schema.sql'; then
  pass "log บอกว่ารันไฟล์ /docker-entrypoint-initdb.d/01-schema.sql จริง"
else
  fail "ไม่พบบรรทัด 'running /docker-entrypoint-initdb.d/01-schema.sql' ใน log ของ vops-db1"
fi

# ---------- 4) จำนวน seed ตรงกับ requirements ----------
seed_ok=1
for pair in "assets:12" "tickets:8" "loans:3" "parts:6" "stock_moves:6"; do
  t=${pair%%:*}; want=${pair##*:}
  got=$(count_of vops-db1 "$t")
  if [ "$got" != "$want" ]; then
    fail "จำนวนแถวของตาราง $t ต้องเป็น $want แต่ได้ '$got'"
    seed_ok=0
  fi
done
[ "$seed_ok" -eq 1 ] && pass "จำนวน seed ตรงตามข้อกำหนด (assets 12 · tickets 8 · loans 3 · parts 6 · stock_moves 6)"

low=$(docker exec vops-db1 psql -U opsuser -d campusops -tAc \
  "SELECT count(*) FROM parts WHERE qty_on_hand < reorder_point;" 2>/dev/null | tr -d '[:space:]')
if [ "$low" = "2" ]; then
  pass "อะไหล่ต่ำกว่าจุดสั่งซื้อ 2 รายการตามที่ contract ระบุ (REQ-12)"
else
  fail "อะไหล่ต่ำกว่าจุดสั่งซื้อต้องเป็น 2 รายการ แต่ได้ '$low'"
fi

# ---------- 5) ไม่มี volume → ข้อมูลที่เพิ่มเองหาย ----------
docker exec vops-db1 psql -U opsuser -d campusops -c \
  "INSERT INTO tickets (asset_id, title, detail, priority) VALUES (4, 'ตรวจงานอัตโนมัติ', 'แถวที่ verify.sh เพิ่มเอง', 'HIGH');" >/dev/null 2>&1
after_insert=$(count_of vops-db1 tickets)
if [ "$after_insert" = "9" ]; then
  pass "เพิ่มใบแจ้งซ่อม 1 ใบแล้วนับได้ 9 ใบ"
else
  fail "หลังเพิ่ม 1 ใบ ต้องนับได้ 9 แต่ได้ '$after_insert'"
fi

docker rm -f vops-db1 >/dev/null 2>&1
run_db vops-db2
if wait_pg vops-db2; then
  lost=$(count_of vops-db2 tickets)
  if [ "$lost" = "8" ]; then
    pass "ไม่มี volume : ลบกล่องแล้วสร้างใหม่ ข้อมูลที่เพิ่มเองหายจริง (กลับเป็น $lost ใบตาม seed)"
  else
    fail "ไม่มี volume แล้วควรกลับเป็น 8 ใบ แต่ได้ '$lost'"
  fi
else
  fail "กล่อง vops-db2 ไม่พร้อมรับ connection"
fi
docker rm -f vops-db2 >/dev/null 2>&1

# ---------- 6) มี named volume → ข้อมูลอยู่ ----------
docker volume rm vops1-pgdata >/dev/null 2>&1
run_db vops-db3 -v vops1-pgdata:/var/lib/postgresql/data
if wait_pg vops-db3; then
  docker exec vops-db3 psql -U opsuser -d campusops -c \
    "INSERT INTO tickets (asset_id, title, detail, priority) VALUES (4, 'ตรวจงานอัตโนมัติ', 'แถวที่ verify.sh เพิ่มเอง', 'HIGH');" >/dev/null 2>&1
  kept_before=$(count_of vops-db3 tickets)
  if [ "$kept_before" = "9" ]; then
    pass "กล่องที่ผูก volume vops1-pgdata เพิ่มข้อมูลแล้วนับได้ 9 ใบ"
  else
    fail "กล่องที่ผูก volume ควรนับได้ 9 ใบหลังเพิ่ม แต่ได้ '$kept_before'"
  fi
else
  fail "กล่อง vops-db3 ไม่พร้อมรับ connection"
fi
docker rm -f vops-db3 >/dev/null 2>&1

if docker volume ls --format '{{.Name}}' | grep -qx 'vops1-pgdata'; then
  pass "ลบกล่องแล้ว volume vops1-pgdata ยังอยู่ (อายุ volume ไม่ผูกกับอายุกล่อง)"
else
  fail "volume vops1-pgdata หายไปหลังลบกล่อง ซึ่งไม่ควรเกิด"
fi

run_db vops-db4 -v vops1-pgdata:/var/lib/postgresql/data
if wait_pg vops-db4; then
  kept_after=$(count_of vops-db4 tickets)
  if [ "$kept_after" = "9" ]; then
    pass "มี volume : สร้างกล่องใหม่แล้วข้อมูลยังอยู่ครบ $kept_after ใบ (NFR-2 ผ่าน)"
  else
    fail "มี volume แล้วข้อมูลต้องอยู่ครบ 9 ใบ แต่ได้ '$kept_after'"
  fi
else
  fail "กล่อง vops-db4 ไม่พร้อมรับ connection"
fi

# ---------- 7) init script ต้องไม่รันซ้ำเมื่อ volume ไม่ว่าง ----------
if docker logs vops-db4 2>&1 | grep -q 'Skipping initialization'; then
  pass "volume ไม่ว่าง : log ขึ้น 'Skipping initialization' — init script ถูกข้าม"
else
  fail "คาดว่า log ของ vops-db4 ต้องมี 'Skipping initialization' แต่ไม่พบ"
fi

if docker logs vops-db4 2>&1 | grep -q 'running /docker-entrypoint-initdb.d/02-seed.sql'; then
  fail "vops-db4 รัน 02-seed.sql ซ้ำ ซึ่งไม่ควรเกิดเมื่อ volume ไม่ว่าง"
else
  pass "vops-db4 ไม่ได้รัน 02-seed.sql ซ้ำ ข้อมูลจึงไม่ถูกเติมซ้ำซ้อน"
fi
docker rm -f vops-db4 >/dev/null 2>&1

# ---------- 8) --env-file ให้ผลเท่ากับ -e หลายตัว ----------
docker run -d --name vops-db5 \
  --env-file .env.db \
  -v vops1-pgdata:/var/lib/postgresql/data \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
  postgres:17-alpine >/dev/null 2>&1
if wait_pg vops-db5; then
  envs=$(docker exec vops-db5 env 2>/dev/null | grep -c -E '^POSTGRES_(DB|USER|PASSWORD)=')
  envfile_count=$(count_of vops-db5 tickets)
  if [ "$envs" = "3" ] && [ "$envfile_count" = "9" ]; then
    pass "--env-file .env.db ส่งค่าเข้ากล่องครบ 3 ตัว และเข้าฐานข้อมูลเดิมได้ ($envfile_count ใบ)"
  else
    fail "--env-file ไม่ได้ผลตามคาด (พบตัวแปร POSTGRES_* = $envs ตัว · นับ tickets ได้ '$envfile_count')"
  fi
else
  fail "กล่อง vops-db5 ที่ใช้ --env-file ไม่พร้อมรับ connection"
fi
docker rm -f vops-db5 >/dev/null 2>&1

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
