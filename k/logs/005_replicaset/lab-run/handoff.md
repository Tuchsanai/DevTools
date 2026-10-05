# Handoff — container ทดลองบท 005 ReplicaSet (เปิดค้างไว้สำหรับ screenshot)

> ผู้ประสานงานเป็นคนลบ container เอง: `docker rm -fv k8s-lab-rs005lab-abd71a`

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-rs005lab-abd71a` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22 (`root` / รหัส LAB ตามสกิล k8s-lab) — publish แค่ SSH ไม่มี NodePort/Jupyter |
| gateway (agent อยู่ใน container) | `172.18.0.1` (บน Docker host ใช้ `localhost`) |
| คลัสเตอร์ | kind `lab` (lab-control-plane / lab-worker / lab-worker2, K8s v1.37.0) |
| โฟลเดอร์ LAB ใน container | `/workspace/005_kubernetes_replicaset/02_LAB` (docker cp ไม่ bind mount) |
| image บน Node | `som-shop-web:1.1`, `som-shop-web:1.1-promo` (tag เดียวกัน ID `2f06fd68d105`), `postgres:17.11-alpine` |

## สภาพปัจจุบัน (05 ต.ค. 2569 ~08:26 เวลาไทย)

namespace `som-booths`, ReplicaSet `som-booth` `3 3 3` (template `som-shop-web:1.1`, eyebrow `⚓ บูธ <ชื่อ Pod>`)

| port ใน k8s-lab (127.0.0.1) | Pod | Node | ออเดอร์ทั้งหมด |
|---|---|---|---|
| 3001 | `som-booth-rmcck` | lab-worker | **1** (สินค้า id 1) |
| 3002 | `som-booth-gxx9d` | lab-worker2 | **2** (id 1, 2) |
| 3003 | `som-booth-tdxr6` | lab-worker2 | **3** (id 1, 2, 3) |

3 บูธบน worker 2 ลำ จึงคนละ Node ได้ไม่ครบ (preferred anti-affinity → 2+1)
port-forward เปิดด้วย `setsid nohup kubectl port-forward --address 127.0.0.1 -n som-booths pod/<ชื่อ> 300N:3000 > /root/pf-300N.log 2>&1 < /dev/null` (log อยู่ที่ `/root/pf-300N.log` ใน container ทดลอง)

## เปิด tunnel จากเครื่อง agent

```bash
# askpass ไว้ใน scratch (ลบทิ้งหลังใช้) — รหัส LAB ตามสกิล k8s-lab
S=/root/workspace/DevTools/k/logs/005_replicaset/scratch
printf '#!/bin/sh\necho <รหัส LAB>\n' > $S/askpass && chmod +x $S/askpass
SSH_ASKPASS=$S/askpass SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid nohup \
  ssh -N -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -L 3001:localhost:3001 -L 3002:localhost:3002 -L 3003:localhost:3003 \
  -p 2224 root@172.18.0.1 </dev/null > $S/ssh-L.log 2>&1 &
# ตรวจ
for p in 3001 3002 3003; do curl -s localhost:$p | grep -o 'บูธ som-booth-[a-z0-9]*' | head -1; done
```

ปิด tunnel: หา PID ด้วย `pgrep -a -x ssh` แล้ว `kill <PID>` — **อย่าใช้** `pkill -f "...ssh -N ... -p 2224..."` จาก shell เดียวกับที่มีข้อความนี้ใน command line (ทดสอบแล้ว pkill ฆ่า shell ตัวเองจน exit 144)

เปิด browser: `http://localhost:3001` / `3002` / `3003` → หัวเว็บ `⚓ บูธ som-booth-xxxxx`, ชื่อร้าน `ร้านอาหารแมวน้องส้ม (หลายบูธ)`, ออเดอร์ทั้งหมด 1/2/3, ท้ายหน้า `🐱 เสิร์ฟโดย Pod: som-booth-xxxxx` + `Next.js + PostgreSQL · Kubernetes LAB 005 · ReplicaSet som-booth`

## คำสั่งสำหรับฉาก screenshot เพิ่ม (รันใน container ทดลอง: `docker exec k8s-lab-rs005lab-abd71a bash -c '...'`)

**ฉาก A — ลบบูธ 3001 แล้ว RS สร้างใหม่ (ออเดอร์ 0, port-forward เดิมหลุด)**
```bash
kubectl delete pod -n som-booths som-booth-rmcck
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s   # จริง ~7 วิ
# ตอนนี้ http://localhost:3001 → ERR_CONNECTION_RESET (port-forward 3001 จบเองตอนมีคนเข้าครั้งแรก, log: "error: lost connection to pod")
NEW=$(kubectl get pods -n som-booths -l app=som-booth --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
setsid nohup kubectl port-forward --address 127.0.0.1 -n som-booths pod/$NEW 3001:3000 > /root/pf-3001.log 2>&1 < /dev/null &
# tunnel ssh -L เดิมใช้ต่อได้ ไม่ต้องเปิดใหม่ → 3001 แสดงบูธชื่อใหม่ ออเดอร์ 0
```

**ฉาก B — บูธโปร (template ใหม่) ข้างบูธเดิม**
```bash
cd /workspace/005_kubernetes_replicaset/02_LAB/som-booths
kubectl apply -f k8s/som-booth-promo.yaml          # replicas ในไฟล์ = 3 ถ้าตอนนี้มี 3 จะไม่มีบูธใหม่
kubectl delete pod -n som-booths <บูธที่จะแทน>      # เช่น ตัวที่ port 3003
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s
NEW=$(kubectl get pods -n som-booths -l app=som-booth --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
pkill -f "[k]ubectl port-forward --address 127.0.0.1 -n som-booths pod/<ชื่อเดิม>" ; \
setsid nohup kubectl port-forward --address 127.0.0.1 -n som-booths pod/$NEW 3003:3000 > /root/pf-3003.log 2>&1 < /dev/null &
# 3003 → "🎉 โปรบูธใหม่ · som-booth-xxxxx" (emoji แสดงถูกใน Chromium ของ Playwright) ส่วน 3002 ยัง "⚓ บูธ ..."
kubectl get pods -n som-booths -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName
```

**ฉาก C — ทำออเดอร์เพิ่ม** `curl -s -X POST localhost:300N/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'`

**กลับสู่สภาพเริ่ม** `kubectl apply -f k8s/som-booth.yaml` แล้วลบบูธ promo ทีละตัว หรือ `kubectl delete ns som-booths` แล้ว apply ใหม่ (ออเดอร์หายหมด ต้องสั่งใหม่ + port-forward ใหม่)
