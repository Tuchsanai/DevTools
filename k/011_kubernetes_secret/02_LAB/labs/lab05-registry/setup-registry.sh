#!/usr/bin/env bash
# LAB 5: เปิดคลังตู้สินค้าส่วนตัว (registry:2 + รหัสผ่าน htpasswd) บน network "kind" แล้วฝาก som-menu:1.0
#   - ในคลัสเตอร์ (Node ของ kind) เรียกคลังนี้ว่า kind-registry:5000
#   - ใน k8s-lab (docker push) เรียกว่า localhost:5001
# ผู้ใช้/รหัสของคลังเป็นค่าตัวอย่างเพื่อการเรียน: som / example-pass
set -e
cd "$(dirname "$0")"
REG_USER=som
REG_PASS=example-pass

echo "== 1) สร้างไฟล์รหัสผ่าน auth/htpasswd (bcrypt) ด้วยคำสั่ง htpasswd ใน image httpd"
mkdir -p auth
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn "$REG_USER" "$REG_PASS" > auth/htpasswd
cut -c1-12 auth/htpasswd; echo "   (ตัดให้เห็นแค่ต้นบรรทัด)"

echo "== 2) เปิด registry ชื่อ kind-registry บน network kind (Node ของ kind มองเห็นด้วยชื่อนี้)"
docker rm -f kind-registry >/dev/null 2>&1 || true
docker run -d --restart=always --name kind-registry --network kind \
  -p 127.0.0.1:5001:5000 \
  -v "$PWD/auth:/auth" \
  -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=som-registry \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  registry:2
until curl -s -o /dev/null http://localhost:5001/v2/; do sleep 1; done
echo "   ไม่ใส่รหัส: HTTP $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/v2/)  (401 = ต้องมีบัตร)"

echo "== 3) docker login แล้ว build + push som-menu:1.0"
echo "$REG_PASS" | docker login localhost:5001 -u "$REG_USER" --password-stdin
docker build -q -t localhost:5001/som-menu:1.0 .
docker push -q localhost:5001/som-menu:1.0

echo "== 4) บอก containerd ทุก Node ว่า kind-registry:5000 เป็น http (ไม่มี TLS) — ไม่ต้อง restart containerd"
for n in $(kind get nodes --name lab); do
  docker exec "$n" mkdir -p /etc/containerd/certs.d/kind-registry:5000
  printf '[host."http://kind-registry:5000"]\n  capabilities = ["pull", "resolve"]\n' \
    | docker exec -i "$n" tee /etc/containerd/certs.d/kind-registry:5000/hosts.toml >/dev/null
  echo "   $n: /etc/containerd/certs.d/kind-registry:5000/hosts.toml"
done
echo "เสร็จ: image ในคลัสเตอร์ = kind-registry:5000/som-menu:1.0"
