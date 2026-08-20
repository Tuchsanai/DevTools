#!/usr/bin/env bash
set -u

fails=0

pass() {
  printf '[PASS] %s\n' "$1"
}

fail() {
  printf '[FAIL] %s\n' "$1"
  fails=$((fails + 1))
}

cleanup() {
  docker rm -f vfy-web vfy-web2 vfy-agent vfy-vault vfy-hostmode >/dev/null 2>&1 || true
  docker network rm vfy-net vfy-vault-net >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM
cleanup

# c1: Docker ต้องมี network driver มาตรฐานครบทั้งสามแบบ
network_list=$(timeout 10 docker network ls --format '{{.Name}}' 2>/dev/null || true)
if grep -qx bridge <<<"$network_list" && grep -qx host <<<"$network_list" && grep -qx none <<<"$network_list"; then
  pass 'c1 default networks bridge, host, none exist'
else
  fail 'c1 default networks bridge, host, none exist'
fi

# c2: build image ของ LAB จากโฟลเดอร์ปัจจุบัน
if timeout 180 docker build -t netlab-web:1.0 . >/dev/null 2>&1; then
  pass 'c2 build netlab-web:1.0'
else
  fail 'c2 build netlab-web:1.0'
fi

# เตรียม user-defined network และ web container สำหรับ c3-c4 และ c10
timeout 15 docker network create vfy-net >/dev/null 2>&1 || true
timeout 15 docker run -d --name vfy-web --network vfy-net netlab-web:1.0 >/dev/null 2>&1 || true

# c3: user-defined bridge ต้อง resolve ชื่อและใช้ embedded DNS
c3_output=$(timeout 20 docker run --rm --network vfy-net busybox:1.36 sh -c 'cat /etc/resolv.conf; nslookup vfy-web' 2>/dev/null || true)
if grep -q '127\.0\.0\.11' <<<"$c3_output" && grep -Eq 'Address[^:]*: [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' <<<"$c3_output"; then
  pass 'c3 embedded DNS resolves vfy-web'
else
  fail 'c3 embedded DNS resolves vfy-web'
fi

# c4: client บน network เดียวกันต้องอ่านหน้าเว็บผ่านชื่อ container ได้
c4_output=$(timeout 20 docker run --rm --network vfy-net busybox:1.36 wget -qO- http://vfy-web 2>/dev/null || true)
if grep -q 'Container Network Console' <<<"$c4_output"; then
  pass 'c4 HTTP by container name on vfy-net'
else
  fail 'c4 HTTP by container name on vfy-net'
fi

# c5: default bridge ไม่มี DNS สำหรับชื่อ container ที่ไม่ได้ link กัน
timeout 15 docker run -d --name vfy-web2 netlab-web:1.0 >/dev/null 2>&1 || true
if timeout 20 docker run --rm busybox:1.36 wget -qO- http://vfy-web2 >/dev/null 2>&1; then
  fail 'c5 default bridge rejects lookup by container name'
else
  pass 'c5 default bridge rejects lookup by container name'
fi

# c6: default bridge ยังติดต่อกันด้วย IP ได้
web2_ip=$(timeout 10 docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' vfy-web2 2>/dev/null || true)
if [[ -n "$web2_ip" ]] && timeout 20 docker run --rm busybox:1.36 wget -qO- "http://$web2_ip" 2>/dev/null | grep -q 'Container Network Console'; then
  pass 'c6 default bridge HTTP by container IP'
else
  fail 'c6 default bridge HTTP by container IP'
fi

# c7: inspect ต้องรายงาน subnet และ gateway ของ vfy-net
c7_output=$(timeout 10 docker network inspect -f '{{range .IPAM.Config}}subnet={{.Subnet}} gateway={{.Gateway}}{{end}}' vfy-net 2>/dev/null || true)
if [[ "$c7_output" == subnet=* ]] && grep -q 'gateway=' <<<"$c7_output" && grep -Eq 'gateway=[^[:space:]]+' <<<"$c7_output"; then
  pass 'c7 network inspect reports subnet and gateway'
else
  fail 'c7 network inspect reports subnet and gateway'
fi

# c8: ทดสอบ connect และ disconnect network แบบ runtime
timeout 15 docker run -d --name vfy-agent --network vfy-net busybox:1.36 sleep 300 >/dev/null 2>&1 || true
timeout 15 docker network create vfy-vault-net >/dev/null 2>&1 || true
timeout 15 docker run -d --name vfy-vault --network vfy-vault-net \
  -v "$PWD/secret/flag.txt:/usr/share/nginx/html/flag.txt:ro" netlab-web:1.0 >/dev/null 2>&1 || true

c8_before=0
c8_connected=0
c8_after=0
timeout 15 docker exec vfy-agent wget -qO- http://vfy-vault/flag.txt >/dev/null 2>&1 || c8_before=1
if timeout 15 docker network connect vfy-vault-net vfy-agent >/dev/null 2>&1; then
  if timeout 20 docker exec vfy-agent wget -qO- http://vfy-vault/flag.txt 2>/dev/null | grep -q 'DOCKER-NET-FLAG'; then
    c8_connected=1
  fi
fi
if timeout 15 docker network disconnect vfy-vault-net vfy-agent >/dev/null 2>&1; then
  timeout 15 docker exec vfy-agent wget -qO- http://vfy-vault/flag.txt >/dev/null 2>&1 || c8_after=1
fi
if (( c8_before == 1 && c8_connected == 1 && c8_after == 1 )); then
  pass 'c8 runtime network connect and disconnect'
else
  fail 'c8 runtime network connect and disconnect'
fi

# c9: none network ต้องมีเพียง loopback และไม่มี eth0
c9_output=$(timeout 20 docker run --rm --network none busybox:1.36 ip -o addr 2>/dev/null || true)
if [[ -n "$c9_output" ]] && ! grep -q 'eth0' <<<"$c9_output" && awk '{print $2}' <<<"$c9_output" | grep -qv '^lo$'; then
  fail 'c9 none network exposes loopback only'
elif [[ -n "$c9_output" ]] && grep -q ' lo ' <<<"$c9_output"; then
  pass 'c9 none network exposes loopback only'
else
  fail 'c9 none network exposes loopback only'
fi

# c10: Docker ต้องไม่ยอมลบ network ที่ยังมี active endpoint
c10_output=$(timeout 15 docker network rm vfy-net 2>&1)
c10_status=$?
if (( c10_status != 0 )) && grep -qi 'active endpoints' <<<"$c10_output"; then
  pass 'c10 cannot remove network with active endpoints'
else
  fail 'c10 cannot remove network with active endpoints'
fi

# c11: หน้าเว็บที่ render ตอน start ต้องรายงาน embedded DNS 127.0.0.11 เมื่ออยู่บน user-defined network
c11_output=$(timeout 15 docker exec vfy-web cat /usr/share/nginx/html/index.html 2>/dev/null || true)
if grep -q '127\.0\.0\.11' <<<"$c11_output" && grep -q 'Container Network Console' <<<"$c11_output"; then
  pass 'c11 rendered console shows embedded DNS 127.0.0.11'
else
  fail 'c11 rendered console shows embedded DNS 127.0.0.11'
fi

# c12: --network host ต้องไม่มี network namespace เป็นของตัวเอง (NetworkMode = host)
timeout 15 docker rm -f vfy-hostmode >/dev/null 2>&1
timeout 20 docker run -d --name vfy-hostmode --network host busybox:1.36 sleep 30 >/dev/null 2>&1
c12_mode=$(timeout 10 docker inspect -f '{{.HostConfig.NetworkMode}}' vfy-hostmode 2>/dev/null || true)
c12_ports=$(timeout 10 docker port vfy-hostmode 2>/dev/null || true)
if [[ "$c12_mode" == host && -z "$c12_ports" ]]; then
  pass 'c12 host mode shares the host network stack (no port mapping)'
else
  fail 'c12 host mode shares the host network stack (no port mapping)'
fi

if (( fails == 0 )); then
  printf 'ALL CHECKS PASSED\n'
  exit 0
fi

printf '%d CHECK(S) FAILED\n' "$fails"
exit 1
