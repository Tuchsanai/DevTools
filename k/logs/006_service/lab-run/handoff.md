# Handoff — container ทดลองบท 006 Service (ยังเปิดอยู่ ผู้ประสานงานลบเอง)

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-svc006lab-06b9a8` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22 (`ssh -p 2224 root@<gateway หรือ localhost>` รหัส LAB `passwd`) — ทดสอบแล้ว `hostname` = `k8s-lab` |
| NodePort | host **30090 / 30091 / 30092** → container 30080 / 30081 / 30082 → kind `lab-control-plane` (extraPortMappings) |
| gateway (agent อยู่ใน container) | `172.18.0.1` → เปิด **http://172.18.0.1:30090** (บน Docker host ใช้ `http://localhost:30090`) |
| โฟลเดอร์ LAB ใน container | `/workspace/006_kubernetes_service/02_LAB` (ไฟล์ตรงกับ repo ทุกไฟล์ — ตรวจ md5 44 ไฟล์แล้ว) |
| ไม่ได้แตะ | `k8s-lab` ของผู้เรียน, `deep_vision_5090_vllm` |

ลบเมื่อเสร็จ: `docker rm -fv k8s-lab-svc006lab-06b9a8`

## สภาพปัจจุบัน (พร้อมถ่าย screenshot)

- ns `som-shop`: `som-db` RS 1/1 + Service ClusterIP `som-db` (5432), `som-web` RS 3/3 (`som-shop-web:1.2` ธีม harbor) + Service NodePort `som-web` `80:30080/TCP`
- **ออเดอร์รวม 4 รายการ** (ปลาทูน่า, ปลาซาบะ, ขนมเลียรสไก่, แซลมอน อย่างละ 1) — `/api/stats` ทุก Pod ตอบ `orders=4 products=6`
- Pod: `som-db-zcwt6`, `som-web-74wwq`, `som-web-bx7tz`, `som-web-tmxnr` (ชื่อจะเปลี่ยนถ้าลบ Pod)
- image `som-shop-web:1.3` (ธีม sunset) โหลดไว้บนทุก Node แล้ว
- (ทางเลือก ฉาก LAB 8) ns `shop`: RS `web` nginx 3 ตัว + `client` + Service `web-nodeport` ที่ **nodePort 30081** (ไม่ใช่ 30080 เพราะร้านใช้อยู่) → **http://172.18.0.1:30091** แสดง `web v1 from web-xxxxx` — ลบได้ด้วย `kubectl delete ns shop`

รันคำสั่งด้านล่างด้วย `docker exec -it k8s-lab-svc006lab-06b9a8 bash` (หรือ ssh -p 2224) แล้ว `cd /workspace/006_kubernetes_service/02_LAB/som-shop-v2`
(ในเอกสารนักศึกษา URL คือ `http://localhost:30080` / `:30081` แทน 30090 / 30091)

## ฉาก screenshot

1. **หน้าร้าน 1.2** — browser `http://172.18.0.1:30090`: ป้าย `เวอร์ชัน 1.2`, แถบ `🐱 เสิร์ฟโดย Pod: som-web-… · เวอร์ชัน 1.2`, ออเดอร์ทั้งหมด 4, footer `Next.js + PostgreSQL · Kubernetes LAB 006 · namespace som-shop`
2. **keep-alive** — กด reload หลายครั้ง: ชื่อ Pod **ไม่เปลี่ยน** (ทดสอบ Chromium 10/10 Pod เดียว); เปิดหน้าต่าง Incognito/ปิดเปิด browser ใหม่ → อาจเปลี่ยน (ทดสอบ 5 context: 2 ชื่อ) — ถ้าอยากเห็นเปลี่ยนแน่ ๆ ให้รอ ~5 วินาทีขึ้นไปแล้ว Incognito ใหม่
3. **terminal: curl กระจาย** — `./hit.sh` (ตาราง 3 Pod + `ok=60 err=0`) และ `for i in $(seq 9); do curl -s localhost:30080/api/stats; done | sort | uniq -c` (ทุก Pod `orders=4`)
4. **terminal: ภาพรวม** — `kubectl -n som-shop get rs,pods,svc,endpointslice -o wide`
5. **EndpointSlice ก่อน/หลังลบ db** —
   ```bash
   kubectl -n som-shop get pod -l app=som-db -o wide
   kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
   kubectl -n som-shop delete pod -l app=som-db            # ~4.5 วิได้ Pod ใหม่ IP ใหม่
   kubectl -n som-shop get svc som-db                      # ClusterIP เดิม
   kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db   # IP ใหม่
   ```
6. **หน้า 503** — หลังข้อ 5 reload browser → `ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱` (HTTP 503, หน้า refresh เองทุก 5 วิ, บอกชื่อ Pod/เวอร์ชัน) ; terminal: `curl -s -o /dev/null -w '%{http_code}\n' localhost:30080` → `503`, `curl -s localhost:30080/api/health` → `{"ok":true,"db":"up"}`
7. **ร้านกลับมา (ออเดอร์ 0)** — `kubectl -n som-shop delete pod $(kubectl -n som-shop get pod -l app=som-web -o name | head -1 | cut -d/ -f2)` แล้วรอ ~4 วิ → browser กลับมา ออเดอร์ 0 (หน้า 503 refresh เอง) ; ถ้าต้องการออเดอร์คืน: `for p in 1 4 5 6; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done`
8. **set image แล้ว Pod เดิมไม่เปลี่ยน** —
   ```bash
   kubectl -n som-shop set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
   kubectl -n som-shop get rs som-web -o wide
   kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
   ./hit.sh                                                 # ยัง 1.2 ทุกตัว
   ```
9. **1.2/1.3 ปน** — terminal 1 `./hit.sh http://localhost:30080/api/whoami 200`; terminal 2 ลบ Pod 1 ตัว → ตาราง hit.sh มีทั้ง 1.2 และ 1.3 (ทดสอบ: err 0–1)
10. **ลบทีเดียว ร้านสะดุด** — terminal 1 `./hit.sh -q http://localhost:30080/api/whoami 200`; terminal 2 `kubectl -n som-shop delete pod -l app=som-web` → แถว `x` ต่อกัน 4–7 ตัว (`Connection reset by peer` / `Operation timed out`) แล้ว browser เป็นธีม sunset `เวอร์ชัน 1.3` + แบนเนอร์ `🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟`
11. **LAB 8 (ทางเลือก)** — browser `http://172.18.0.1:30091` → `web v1 from web-…` ; `kubectl -n shop get svc web-nodeport`

## คืนสภาพเริ่มต้น (1.2 + ออเดอร์ 4)

```bash
cd /workspace/006_kubernetes_service/02_LAB/som-shop-v2
kubectl delete ns som-shop && kubectl apply -f k8s/ && kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=120s
for p in 1 4 5 6; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done
```
(ทดสอบแล้ว: apply ทั้งโฟลเดอร์พร้อมกัน web รอ db ด้วย wait-for-db แล้ว seed พร้อมกัน 3 ตัว ได้ `new: 6/0/0` init restart 0 — Ready ใน 9 วิ)

log ของการตั้งสภาพนี้: `handoff-commands.log`
