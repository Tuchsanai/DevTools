# Handoff — บท 010 ConfigMap (container ทดลองสำหรับ screenshot)

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-cm010-b35a42` (owner label `cm010-labrun`, image `tuchsanai/devtools-kind:2569_1` = `8108a1bc7901`) |
| SSH | host port **2224** → 22 (`root` / password ของ LAB ตาม skill k8s-lab หรือ key `devtoolSSH` ที่สร้างใน container) — ตรวจแล้ว PASS ทั้งสองแบบ |
| NodePort | host **30090** → 30080 (ร้าน som-web), 30091 → 30081, 30092 → 30082 (ว่าง) |
| gateway (จาก agent container) | **172.18.0.1** → เปิด browser ที่ `http://172.18.0.1:30090/` (ทดสอบ curl แล้ว HTTP 200, `/som.png` 200) |
| บนเครื่อง Docker host เอง | `http://localhost:30090/` |
| ไฟล์ใน container | `/workspace/010_kubernetes_configmap/02_LAB` (docker cp ทั้งโฟลเดอร์บท, ไม่มี bind mount) |

ผู้ประสานงานเป็นคนลบ container เอง: `docker rm -fv k8s-lab-cm010-b35a42` (ห้ามใช้ `--filter name=k8s-lab` แบบกว้าง)

## สภาพปัจจุบัน (สภาพสุดท้ายของ LAB 10 ก่อนเปลี่ยนป้าย)

- namespace `som-shop`: `som-db-0` (StatefulSet, PVC `data-som-db-0`), `som-web` 3 Pod image `som-shop-web:1.5` (`envFrom: som-web-config` + mount `som-announcement` ที่ `/etc/som`), Service NodePort 30080
- ConfigMap `som-web-config` = ค่าเดิมใน `k8s/15-config.yaml`: `ร้านอาหารแมวน้องส้ม`, ธีม `harbor`, ไม่มีโปรโมชัน, eyebrow `⚓ ท่าเรือ Kubernetes · ConfigMap`, footer `Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config`
- ConfigMap `som-announcement` = `วันนี้ปลาทูสดมาก 🐟` (หน้าเว็บมีแถบเหลือง 📢)
- `/api/stats` → `orders=4 products=6`
- มี SA/Role/RoleBinding `intern` (ขั้น F) ค้างไว้ ไม่มีผลกับหน้าเว็บ; ไม่มี `som-web-config-v2` (ลบแล้ว)
- namespace `default` ว่าง (LAB 1–9 เก็บกวาดแล้ว)

ตัวช่วยพิมพ์คำสั่ง (รันจาก host):

```bash
C=k8s-lab-cm010-b35a42
k() { docker exec $C bash -lc "cd /workspace/010_kubernetes_configmap/02_LAB/som-shop-v6 && $*"; }
k 'curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement; curl -s localhost:30080/api/stats'
```

## ฉาก screenshot เพิ่ม

### ฉาก 1 — แก้ป้ายร้านใน ConfigMap แล้วหน้าเว็บยังเหมือนเดิม (ขั้น C1, ภาพ L14)

```bash
k 'kubectl apply -f extra/15-config-promo.yaml'
# รอ 90 วินาทีแล้ว refresh browser → ยังเป็น ร้านอาหารแมวน้องส้ม / ธีม harbor (น้ำเงิน) / ไม่มีแถบโปรโมชัน
k 'curl -s localhost:30080/api/shop; echo; kubectl -n som-shop get pod -l app=som-web'
```

### ฉาก 2 — rollout restart แล้วป้ายเปลี่ยน (ขั้น C2, ภาพ L15)

```bash
k 'kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web'
# รอ ~8 วินาที (preStop 5 วิ) แล้ว refresh → title "ร้านน้องส้ม สาขาท่าเรือ", ธีม sunset (ส้ม), แถบ "🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%", orders=4 เท่าเดิม
```
rollout ทั้งหมดใช้ราว 25–35 วินาที (3 Pod, maxSurge 1, minReadySeconds 3)

### ฉาก 3 — แก้ประกาศแล้วหน้าเว็บเปลี่ยนเองโดย Pod ไม่ restart (ขั้น D, ภาพ L17–L18)

```bash
k 'kubectl -n som-shop get pod -l app=som-web'              # จด AGE / RESTARTS 0
k 'kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00'
k 'kubectl -n som-shop get pod -l app=som-web'              # ชื่อเดิม RESTARTS 0 AGE ต่อเนื่อง
```
เวลาจริงที่วัดได้ 3 รอบ: Pod แรกเห็นประกาศใหม่หลัง **37 / 63 / 59 วินาที**, ครบทุก Pod (12/12) หลัง **48 / 82 / 88 วินาที** → เผื่อรอ **ประมาณ 1–1.5 นาที** แล้ว refresh browser (แถบ 📢 เป็น `ปิดร้านเร็ว 18:00 น. ⛵`; ระหว่างนั้น refresh แต่ละครั้งอาจได้ Pod ที่ยังเป็นข้อความเก่า)

### ฉาก 4 (ถ้าต้องการ) — `$(POD_NAMESPACE)` ไม่ถูกแทนค่า (ภาพ L16)

```bash
k "kubectl -n som-shop patch cm som-web-config --type merge -p '{\"data\":{\"SHOP_FOOTER\":\"LAB 010 · namespace \$(POD_NAMESPACE)\"}}' && kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web"
# footer = "LAB 010 · namespace $(POD_NAMESPACE)"
k "kubectl -n som-shop set env deploy/som-web SHOP_FOOTER='LAB 010 · namespace \$(POD_NAMESPACE)' && kubectl -n som-shop rollout status deploy/som-web"
# footer = "LAB 010 · namespace som-shop"
k 'kubectl -n som-shop set env deploy/som-web SHOP_FOOTER-'   # เอา env ออก (ทำก่อนคืนสภาพ)
```

## คืนสภาพ (กลับเป็นสภาพปัจจุบัน)

```bash
k 'kubectl -n som-shop set env deploy/som-web SHOP_FOOTER- 2>/dev/null; kubectl apply -f k8s/ && kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web'
# som-web-config กลับเป็นชื่อร้าน/harbor/ไม่มีโปรโมชัน ทันทีหลัง rollout
# ประกาศกลับเป็น "วันนี้ปลาทูสดมาก 🐟" — Pod ใหม่เห็นทันที (ถ้าไม่ได้ restart ต้องรอ ~1 นาที)
k 'curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement; curl -s localhost:30080/api/stats'
```
ออเดอร์ไม่หาย (อยู่ใน PVC ของ som-db-0) — ถ้าต้องการเพิ่มเป็น 5: `k "curl -s -XPOST -H 'content-type: application/json' -d '{\"product_id\":3,\"qty\":1}' localhost:30080/api/orders"`
