#!/bin/bash
# verify.sh — LAB 4 : รันหลังจบข้อ 6 (ก่อนล้างกระดาน)
# หมายเหตุ: ข้อ spy จะเชื่อม/ถอด lab_net ให้อัตโนมัติ แล้วคืนสภาพเดิมเสมอ
# exit 0 = ผ่านทุกข้อ
PASS=0; FAIL=0
ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# 1) lab_net มีอยู่และ subnet ถูกต้อง
SUB=$(docker network inspect -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}' lab_net 2>/dev/null)
[ "$SUB" = "172.30.0.0/24" ] && ok "lab_net มีอยู่ subnet 172.30.0.0/24" || bad "lab_net ไม่มีหรือ subnet ผิด: ${SUB:-ไม่พบ} (ข้อ 3)"

# 2) default bridge: ชื่อใช้ไม่ได้ (ต้องล้มเหลว)
if docker exec box1 ping -c 1 -W 2 box2 >/dev/null 2>&1; then
  bad "box1 ping ชื่อ box2 สำเร็จ — ไม่ควรเกิดบน default bridge (ข้อ 2)"
else ok "default bridge แปลชื่อไม่ได้ (bad address) — ตามบทเรียน"; fi

# 3) lab_net: ชื่อใช้ได้
docker exec box3 ping -c 2 -W 3 box4 >/dev/null 2>&1 && ok "box3 ping ชื่อ box4 สำเร็จ — Embedded DNS ทำงาน" || bad "box3 ping box4 ล้มเหลว (ข้อ 3)"

# 4) Embedded DNS ตัวเป็น ๆ ใน resolv.conf
docker exec box3 cat /etc/resolv.conf 2>/dev/null | grep -q '127.0.0.11' && ok "resolv.conf ชี้ nameserver 127.0.0.11" || bad "ไม่พบ 127.0.0.11 ใน resolv.conf ของ box3 (ข้อ 3)"

# 5) IP ตายตัวของ box5
IP5=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' box5 2>/dev/null)
[ "$IP5" = "172.30.0.50" ] && ok "box5 ได้ IP ตายตัว 172.30.0.50" || bad "IP ของ box5 คือ ${IP5:-ไม่พบ} ไม่ใช่ 172.30.0.50 (ข้อ 4)"

# 6) secret-server ไม่เปิด port สู่โลกภายนอก
PORTS=$(docker inspect -f '{{json .HostConfig.PortBindings}}' secret-server 2>/dev/null)
if [ -z "$PORTS" ]; then bad "ไม่พบ container secret-server (ข้อ 5)"
elif [ "$PORTS" = "{}" ] || [ "$PORTS" = "null" ]; then ok "secret-server ไม่มี -p — เห็นเฉพาะสมาชิก lab_net"
else bad "secret-server ถูก publish port ออกมา: $PORTS (ข้อ 5)"; fi

# 7) ภารกิจ spy ครบสามจังหวะ: มืดบอด → connect เห็น → disconnect มืดบอด
if docker inspect spy >/dev/null 2>&1; then
  docker network disconnect lab_net spy 2>/dev/null   # เริ่มจากสภาพ "อยู่นอกวง" เสมอ
  if docker exec spy wget -qO- -T 3 http://secret-server >/dev/null 2>&1; then
    bad "spy เห็น secret-server ทั้งที่อยู่นอก lab_net (ข้อ 5)"
  else ok "spy นอกวง → มองไม่เห็น secret-server"; fi
  docker network connect lab_net spy
  MSG=$(docker exec spy wget -qO- -T 5 http://secret-server 2>/dev/null)
  echo "$MSG" | grep -q 'กู้ข้อความลับสำเร็จ' && ok "หลัง network connect → spy กู้ข้อความลับได้" || bad "connect แล้วยังอ่านข้อความลับไม่ได้ (ข้อ 5): $MSG"
  docker network disconnect lab_net spy 2>/dev/null   # คืนสภาพ
else
  bad "ไม่พบ container spy (ข้อ 5)"
fi

# 8) โหมด host: nginx ตอบบน port 80 ตรง ๆ โดยไม่มี -p
curl -s --max-time 5 localhost:80 | grep -q '<title>Welcome to nginx!</title>' && ok "hostnginx ตอบทาง localhost:80 (network host)" || bad "localhost:80 ไม่ตอบ — hostnginx รันอยู่ไหม? (ข้อ 6)"

# 9) โหมด none: มีแค่ loopback
NIF=$(docker run --rm --network none alpine ip -o link 2>/dev/null | wc -l)
[ "$NIF" -eq 1 ] && ok "network none เหลือ interface เดียว (lo)" || bad "network none มี interface เกินคาด: $NIF (ข้อ 6)"

echo "-----------------------------"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))"; exit 0
else echo "FAILED $FAIL CHECK(S)"; exit 1; fi
