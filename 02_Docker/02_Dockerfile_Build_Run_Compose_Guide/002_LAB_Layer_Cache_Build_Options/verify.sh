#!/usr/bin/env bash
# verify.sh — ตรวจว่า LAB 2 (Layer cache + options ของ docker build) ทำได้ครบจริง
# รันจากในโฟลเดอร์ LAB บนเครื่องเรียน :  ./verify.sh
# สคริปต์นี้ "ไม่ลบ image ของผู้เรียน" ลบเฉพาะ container ชั่วคราวที่ตัวเองสร้าง

set -u

failures=0
app_backup=""
container_started=0
tmp_dir=""
made_notes=0

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  # คืน app.py กลับเป็นของเดิมเสมอ แม้สคริปต์ถูกขัดจังหวะ
  if [ -n "$app_backup" ] && [ -f "$app_backup" ]; then
    cp "$app_backup" app.py
  fi
  [ "$made_notes" -eq 1 ] && rm -f notes.md
  if [ "$container_started" -eq 1 ]; then
    docker rm -f cachelab-web >/dev/null 2>&1
  fi
  [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
  return 0
}
trap cleanup EXIT INT TERM

tmp_dir=$(mktemp -d)

# อ่านสถานะของ build step หนึ่ง ๆ จาก log ของ --progress=plain
# คืนค่า CACHED / REBUILT / NOSTEP
step_status() {
  local log="$1" needle="$2" num
  num=$(grep -E '^#[0-9]+ \[[0-9]+/[0-9]+\] ' "$log" | grep -F "$needle" | head -1 | sed -E 's/^#([0-9]+) .*/\1/')
  if [ -z "$num" ]; then printf 'NOSTEP\n'; return; fi
  if grep -qE "^#${num} CACHED" "$log"; then printf 'CACHED\n'; else printf 'REBUILT\n'; fi
}

echo "=============================================="
echo " LAB 2 — Layer Cache & Build Options : verify"
echo "=============================================="

# ---------- 1) ไฟล์ครบไหม ----------
missing=""
for f in app.py requirements.txt Dockerfile.good Dockerfile.bad .dockerignore; do
  [ -f "$f" ] || missing="$missing $f"
done
if [ -z "$missing" ]; then
  pass "ไฟล์ของแล็บครบ (app.py, requirements.txt, Dockerfile.good, Dockerfile.bad, .dockerignore)"
else
  fail "ไฟล์ของแล็บไม่ครบ:$missing"
  echo "$failures CHECK(S) FAILED"
  exit 1
fi

# ---------- 2) build ทั้งสองลำดับ ----------
if docker build --progress=plain -f Dockerfile.good -t cachelab-good:1.0 . >"$tmp_dir/good.log" 2>&1; then
  pass "build image cachelab-good:1.0 จาก Dockerfile.good สำเร็จ"
else
  fail "build image cachelab-good:1.0 ไม่สำเร็จ (ดู $tmp_dir/good.log)"
fi

if docker build --progress=plain -f Dockerfile.bad -t cachelab-bad:1.0 . >"$tmp_dir/bad.log" 2>&1; then
  pass "build image cachelab-bad:1.0 จาก Dockerfile.bad สำเร็จ"
else
  fail "build image cachelab-bad:1.0 ไม่สำเร็จ (ดู $tmp_dir/bad.log)"
fi

# ---------- 3) เห็น image ทั้งสองใน docker image ls ----------
tags=$(docker image ls --format '{{.Repository}}:{{.Tag}}')
if printf '%s\n' "$tags" | grep -Fxq 'cachelab-good:1.0' && printf '%s\n' "$tags" | grep -Fxq 'cachelab-bad:1.0'; then
  pass "docker image ls เห็น cachelab-good:1.0 และ cachelab-bad:1.0"
else
  fail "docker image ls ไม่เห็น image ครบทั้งสองตัว"
fi

# ---------- 4) หัวใจของแล็บ : แก้ app.py 1 บรรทัดแล้วดู cache ----------
app_backup="$tmp_dir/app.py.orig"
cp app.py "$app_backup"
# ใช้ค่าที่ไม่ซ้ำกับรอบก่อน ๆ ไม่งั้น build cache เก่าอาจ hit แล้วผลเพี้ยน
# รับค่าเดิมได้ทุกค่า (ผู้เรียนอาจหยุดกลางแล็บตอน APP_VERSION เป็น 2 หรือ 3 อยู่)
old_version=$(grep -m1 -E '^# APP_VERSION = ' app.py | sed -E 's/^# APP_VERSION = //')
new_version="2-$(date +%s)"
sed -i -E "s|^# APP_VERSION = .*$|# APP_VERSION = ${new_version}|" app.py

if grep -q "^# APP_VERSION = ${new_version}$" app.py; then
  pass "แก้ app.py 1 บรรทัด (APP_VERSION ${old_version:-?} -> ${new_version}) เรียบร้อย"
else
  fail "แก้ app.py ไม่สำเร็จ — ต้องมีบรรทัดขึ้นต้นด้วย '# APP_VERSION = ' ในไฟล์"
fi

docker build --progress=plain -f Dockerfile.good -t cachelab-good:1.0 . >"$tmp_dir/good2.log" 2>&1
docker build --progress=plain -f Dockerfile.bad  -t cachelab-bad:1.0  . >"$tmp_dir/bad2.log"  2>&1

good_pip=$(step_status "$tmp_dir/good2.log" 'RUN pip install')
bad_pip=$(step_status "$tmp_dir/bad2.log" 'RUN pip install')

if [ "$good_pip" = "CACHED" ]; then
  pass "Dockerfile.good : ขั้น RUN pip install เป็น CACHED หลังแก้ app.py"
else
  fail "Dockerfile.good : ขั้น RUN pip install ไม่ได้ CACHED (ได้ $good_pip)"
fi

if [ "$bad_pip" = "REBUILT" ]; then
  pass "Dockerfile.bad : ขั้น RUN pip install ถูก build ใหม่ (cache แตก) — ลำดับคำสั่งมีผลจริง"
else
  fail "Dockerfile.bad : คาดว่า RUN pip install ต้อง build ใหม่ แต่ได้ $bad_pip"
fi

# คืน app.py กลับ (เทียบกับไฟล์สำรอง ไม่ผูกกับค่า APP_VERSION ค่าใดค่าหนึ่ง)
cp "$app_backup" app.py
if cmp -s "$app_backup" app.py; then
  pass "คืนไฟล์ app.py กลับเป็นของเดิมแล้ว"
else
  fail "คืนไฟล์ app.py กลับไม่สำเร็จ"
fi

# ---------- 5) .dockerignore ต้องกัน cache ไม่ให้แตก ----------
if grep -qx 'notes.md' .dockerignore; then
  pass ".dockerignore มีบรรทัด notes.md"
else
  fail ".dockerignore ไม่มีบรรทัด notes.md"
fi

made_notes=1
echo "note v1" > notes.md
docker build --progress=plain -f Dockerfile.good -t cachelab-good:1.0 . >/dev/null 2>&1
echo "note v2 — แก้แล้ว" > notes.md
docker build --progress=plain -f Dockerfile.good -t cachelab-good:1.0 . >"$tmp_dir/ignore.log" 2>&1
copy_all=$(step_status "$tmp_dir/ignore.log" 'COPY . .')
if [ "$copy_all" = "CACHED" ]; then
  pass "แก้ไฟล์ที่ถูก .dockerignore แล้ว ขั้น COPY . . ยังเป็น CACHED"
else
  fail "แก้ไฟล์ที่ถูก .dockerignore แล้ว cache ไม่ควรแตก แต่ได้ $copy_all"
fi
rm -f notes.md
made_notes=0

# ---------- 6) docker history ต้องเห็น layer ของ pip ----------
if docker history --no-trunc --format '{{.CreatedBy}}' cachelab-good:1.0 2>/dev/null | grep -q 'pip install'; then
  pass "docker history cachelab-good:1.0 เห็น layer ของ RUN pip install"
else
  fail "docker history cachelab-good:1.0 ไม่เห็น layer ของ RUN pip install"
fi

# ---------- 7) รัน container แล้วต้องตอบจริง ----------
docker rm -f cachelab-web >/dev/null 2>&1
if docker run -d --name cachelab-web -p 8182:8182 cachelab-good:1.0 >/dev/null 2>&1; then
  container_started=1
  health_ok=0
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    if curl -fsS http://localhost:8182/health 2>/dev/null | grep -q '"status":"ok"'; then
      health_ok=1; break
    fi
    sleep 1
  done
  if [ "$health_ok" -eq 1 ]; then
    pass "container cachelab-web ตอบ /health ว่า status ok บนพอร์ต 8182"
  else
    fail "container cachelab-web ไม่ตอบ /health บนพอร์ต 8182"
  fi

  if curl -fsS http://localhost:8182/ 2>/dev/null | grep -q 'Layer Cache Lab'; then
    pass "หน้าเว็บ / แสดงหัวข้อ Layer Cache Lab"
  else
    fail "หน้าเว็บ / ไม่แสดงหัวข้อ Layer Cache Lab"
  fi

  if docker rm -f cachelab-web >/dev/null 2>&1; then
    container_started=0
    pass "ลบ container ชั่วคราว cachelab-web แล้ว"
  else
    fail "ลบ container cachelab-web ไม่สำเร็จ"
  fi
else
  fail "run container cachelab-web พอร์ต 8182 ไม่สำเร็จ (พอร์ตอาจถูกใช้อยู่)"
fi

echo "----------------------------------------------"
if [ "$failures" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
fi
printf '%s CHECK(S) FAILED\n' "$failures"
exit 1
