#!/usr/bin/env bash
set -u

PROJ=devopsboard
COMPOSE="docker compose -p $PROJ"
FAILURES=0

pass() {
    printf '[PASS] %s\n' "$1"
}

fail() {
    printf '[FAIL] %s\n' "$1"
    FAILURES=$((FAILURES + 1))
}

TMP_DIR=$(mktemp -d)
trap 'rm -rf -- "$TMP_DIR"' EXIT

# 1. Required files
required_files=(
    compose.yaml
    .env.app
    .dockerignore
    api/Dockerfile
    api/app.py
    api/requirements.txt
    web/Dockerfile
    web/build_site.py
    web/template.html
    web/nginx.conf
    db/initdb/01-schema.sql
)
missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done
if ((${#missing_files[@]} == 0)); then
    pass "ไฟล์ที่กำหนดครบถ้วน"
else
    fail "ไฟล์ไม่ครบ: ${missing_files[*]}"
fi

# 2. No tab characters in compose.yaml
if [[ -f compose.yaml ]] && ! grep -Pq '\t' compose.yaml 2>/dev/null; then
    pass "compose.yaml ไม่มีอักขระแท็บ"
else
    fail "compose.yaml มีอักขระแท็บหรืออ่านไม่ได้"
fi

# 3. Valid Compose configuration
if $COMPOSE config --quiet >/dev/null 2>&1; then
    pass "Compose YAML ถูกต้อง"
else
    fail "Compose YAML ไม่ถูกต้อง"
fi

# 4. Password comes only from .env.app
if [[ -f compose.yaml && -f .env.app ]] \
    && ! grep -q 'POSTGRES_PASSWORD' compose.yaml \
    && grep -Eq '^[[:space:]]*POSTGRES_PASSWORD=' .env.app; then
    pass "รหัสผ่าน PostgreSQL มาจาก .env.app"
else
    fail "การกำหนด POSTGRES_PASSWORD ไม่ถูกต้อง"
fi

# 5. .dockerignore excludes .env.app
if [[ -f .dockerignore ]] && grep -Eq '^[[:space:]]*\.env\.app[[:space:]]*$' .dockerignore; then
    pass ".dockerignore กันไฟล์ .env.app"
else
    fail ".dockerignore ไม่มีบรรทัด .env.app"
fi

# 6. Backend network is internal
if $COMPOSE config 2>/dev/null | grep -A3 'backend:' | grep -q 'internal: true'; then
    pass "เครือข่าย backend เป็น internal"
else
    fail "เครือข่าย backend ไม่ได้เป็น internal"
fi

# 7. Four expected containers are running
containers_ok=1
for service in web api redis db; do
    container="${PROJ}-${service}-1"
    state=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || true)
    if [[ "$state" != "running" ]]; then
        containers_ok=0
    fi
done
if ((containers_ok)); then
    pass "คอนเทนเนอร์ทั้ง 4 ตัวกำลังทำงาน"
else
    fail "คอนเทนเนอร์ไม่ครบหรือไม่ได้ running"
fi

# 8. DB, Redis, and API are healthy
health_ok=1
for service in db redis api; do
    container="${PROJ}-${service}-1"
    health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$container" 2>/dev/null || true)
    if [[ "$health" != "healthy" ]]; then
        health_ok=0
    fi
done
if ((health_ok)); then
    pass "db, redis และ api มีสถานะ healthy"
else
    fail "db, redis หรือ api ยังไม่ healthy"
fi

# 9. Expected networks exist
if docker network inspect "${PROJ}_frontend" >/dev/null 2>&1 \
    && docker network inspect "${PROJ}_backend" >/dev/null 2>&1; then
    pass "เครือข่าย frontend และ backend มีครบ"
else
    fail "เครือข่าย frontend หรือ backend ไม่พบ"
fi

# 10. Expected volumes exist
if docker volume inspect "${PROJ}_pgdata" >/dev/null 2>&1 \
    && docker volume inspect "${PROJ}_redisdata" >/dev/null 2>&1; then
    pass "volume pgdata และ redisdata มีครบ"
else
    fail "volume pgdata หรือ redisdata ไม่พบ"
fi

# 11. DB and Redis have no host-published ports
ports_ok=1
for service in db redis; do
    ports=$(docker inspect -f '{{json .NetworkSettings.Ports}}' "${PROJ}-${service}-1" 2>/dev/null || true)
    if [[ -z "$ports" || "$ports" == *'"HostPort"'* ]]; then
        ports_ok=0
    fi
done
if ((ports_ok)); then
    pass "db และ redis ไม่เปิดพอร์ตสู่ host"
else
    fail "db หรือ redis เปิดพอร์ตสู่ host"
fi

# 12. Nginx serves the home page
home_file="$TMP_DIR/home.html"
home_code=$(curl -sS -o "$home_file" -w '%{http_code}' http://localhost:8187/ 2>/dev/null || true)
if [[ "$home_code" == "200" ]] && grep -q 'DevOps Board' "$home_file"; then
    pass "หน้าเว็บตอบ 200 และมี DevOps Board"
else
    fail "หน้าเว็บไม่ตอบ 200 หรือไม่มี DevOps Board"
fi

# 13. Served HTML contains no external HTTP(S) URL
if [[ "$home_code" == "200" ]] && ! grep -Eq 'https?://' "$home_file"; then
    pass "HTML ไม่มีลิงก์ http:// หรือ https://"
else
    fail "HTML มีลิงก์ภายนอกหรือโหลดหน้าเว็บไม่ได้"
fi

# 14. Stats endpoint and required JSON keys
stats_file="$TMP_DIR/stats.json"
stats_code=$(curl -sS -o "$stats_file" -w '%{http_code}' http://localhost:8187/api/stats 2>/dev/null || true)
if [[ "$stats_code" == "200" ]] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); required={"visits","hostname","app_env","env_file_only","api_build_time","services","items","item_count"}; assert required <= set(d)' "$stats_file" >/dev/null 2>&1; then
    pass "API stats ตอบ 200 และมี key ครบ"
else
    fail "API stats ไม่ถูกต้องหรือมี key ไม่ครบ"
fi

# 15. Redis and DB service statuses are up
if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); s={x["name"]:x["status"] for x in d["services"]}; assert s.get("redis")=="up" and s.get("db")=="up"' "$stats_file" >/dev/null 2>&1; then
    pass "สถานะ redis และ db เป็น up"
else
    fail "สถานะ redis หรือ db ไม่เป็น up"
fi

# 16. Redis INCR makes visits increase
visit_file_1="$TMP_DIR/visits-1.json"
visit_file_2="$TMP_DIR/visits-2.json"
visit_code_1=$(curl -sS -o "$visit_file_1" -w '%{http_code}' http://localhost:8187/api/stats 2>/dev/null || true)
visit_code_2=$(curl -sS -o "$visit_file_2" -w '%{http_code}' http://localhost:8187/api/stats 2>/dev/null || true)
if [[ "$visit_code_1" == "200" && "$visit_code_2" == "200" ]] \
    && python3 -c 'import json,sys; a=json.load(open(sys.argv[1]))["visits"]; b=json.load(open(sys.argv[2]))["visits"]; assert isinstance(a,int) and not isinstance(a,bool) and isinstance(b,int) and not isinstance(b,bool) and b>a' "$visit_file_1" "$visit_file_2" >/dev/null 2>&1; then
    pass "ค่า visits เพิ่มขึ้นจาก Redis INCR"
else
    fail "ค่า visits ไม่เพิ่มขึ้นตามคาด"
fi

# 17. environment overrides env_file
if python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["app_env"] == "production"' "$stats_file" >/dev/null 2>&1; then
    pass "app_env เป็น production"
else
    fail "app_env ไม่เป็น production"
fi

# 18. env_file_only is populated
if python3 -c 'import json,sys; v=json.load(open(sys.argv[1]))["env_file_only"]; assert v is not None and str(v).strip()' "$stats_file" >/dev/null 2>&1; then
    pass "env_file_only มีค่าจาก .env.app"
else
    fail "env_file_only ไม่มีค่า"
fi

# 19. Seed rows exist
base_count=$(python3 -c 'import json,sys; v=json.load(open(sys.argv[1]))["item_count"]; assert isinstance(v,int) and not isinstance(v,bool); print(v)' "$stats_file" 2>/dev/null || true)
if [[ "$base_count" =~ ^[0-9]+$ ]] && ((base_count >= 4)); then
    pass "ฐานข้อมูลมี seed อย่างน้อย 4 รายการ"
else
    fail "จำนวน seed ในฐานข้อมูลน้อยกว่า 4"
fi

# 20. Create one item, then verify item_count increases by exactly one
post_file="$TMP_DIR/post.json"
after_file="$TMP_DIR/after-post.json"
post_body=$(printf '{"name":"verify-item-%s","owner":"verify-script"}' "$$")
post_code=$(curl -sS -o "$post_file" -w '%{http_code}' -X POST \
    -H 'Content-Type: application/json' -d "$post_body" \
    http://localhost:8187/api/items 2>/dev/null || true)
after_code=$(curl -sS -o "$after_file" -w '%{http_code}' http://localhost:8187/api/stats 2>/dev/null || true)
if [[ "$post_code" == "201" && "$after_code" == "200" && "$base_count" =~ ^[0-9]+$ ]] \
    && python3 -c 'import json,sys; after=json.load(open(sys.argv[1]))["item_count"]; before=int(sys.argv[2]); assert isinstance(after,int) and not isinstance(after,bool) and after == before+1' "$after_file" "$base_count" >/dev/null 2>&1; then
    pass "POST สร้าง item และจำนวนเพิ่มขึ้น 1"
else
    fail "POST item ไม่สำเร็จหรือจำนวนไม่เพิ่มขึ้น 1"
fi

# 21. Direct API health endpoint
health_file="$TMP_DIR/api-health.json"
health_code=$(curl -sS -o "$health_file" -w '%{http_code}' http://localhost:8087/health 2>/dev/null || true)
if [[ "$health_code" == "200" ]] \
    && python3 -c 'import json,sys; assert json.load(open(sys.argv[1])) == {"status":"ok"}' "$health_file" >/dev/null 2>&1; then
    pass "API health โดยตรงตอบ status ok"
else
    fail "API health โดยตรงไม่ตอบ status ok"
fi

# 22. Web image is a Python-free Nginx runtime image
if docker run --rm devopsboard-web:1.0 python --version >/dev/null 2>&1; then
    web_python_absent=0
else
    web_python_absent=1
fi
if docker run --rm devopsboard-web:1.0 nginx -v >/dev/null 2>&1; then
    web_nginx_present=1
else
    web_nginx_present=0
fi
if ((web_python_absent && web_nginx_present)); then
    pass "web runtime ไม่มี Python และมี Nginx"
else
    fail "web runtime stage ไม่ตรงตามกำหนด"
fi

# 23. Web image is smaller than API image
web_size=$(docker image inspect -f '{{.Size}}' devopsboard-web:1.0 2>/dev/null || true)
api_size=$(docker image inspect -f '{{.Size}}' devopsboard-api:1.0 2>/dev/null || true)
if [[ "$web_size" =~ ^[0-9]+$ && "$api_size" =~ ^[0-9]+$ ]] && ((web_size < api_size)); then
    pass "image web เล็กกว่า image api"
else
    fail "image web ไม่เล็กกว่า image api"
fi

# 24. Compose DNS resolves DB and Redis from API
if $COMPOSE exec -T api getent hosts db >/dev/null 2>&1 \
    && $COMPOSE exec -T api getent hosts redis >/dev/null 2>&1; then
    pass "Compose DNS หา db และ redis ได้"
else
    fail "Compose DNS หา db หรือ redis ไม่ได้"
fi

# 25. Frontend cannot reach DB, while backend can
if ! docker image inspect busybox:1.36 >/dev/null 2>&1; then
    docker pull busybox:1.36 >/dev/null 2>&1 || true
fi
if docker run --rm --network "${PROJ}_frontend" busybox:1.36 nc -z -w 3 db 5432 >/dev/null 2>&1; then
    frontend_blocked=0
else
    frontend_blocked=1
fi
if docker run --rm --network "${PROJ}_backend" busybox:1.36 nc -z -w 3 db 5432 >/dev/null 2>&1; then
    backend_connected=1
else
    backend_connected=0
fi
if ((frontend_blocked && backend_connected)); then
    pass "แยกชั้น network ถูกต้อง"
else
    fail "การแยกชั้น network ไม่ถูกต้อง"
fi

if ((FAILURES == 0)); then
    printf 'ALL CHECKS PASSED\n'
    exit 0
else
    printf 'CHECKS FAILED: %d\n' "$FAILURES"
    exit 1
fi
