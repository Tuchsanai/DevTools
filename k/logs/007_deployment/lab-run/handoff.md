# Handoff — container ทดลองบท 007 Deployment (ยังเปิดอยู่ ผู้ประสานงานลบเอง)

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-deploy007lab-06e5cc` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22 (`ssh -p 2224 root@<gateway หรือ localhost>` รหัส LAB `passwd`) — ทดสอบแล้ว `hostname` = `k8s-lab` |
| NodePort | host **30090 / 30091 / 30092** → container 30080 / 30081 / 30082 → kind `lab-control-plane` (extraPortMappings) |
| gateway (agent อยู่ใน container) | `172.18.0.1` → เปิด **http://172.18.0.1:30090** (บน Docker host = `http://localhost:30090`; ในเอกสารนักศึกษา = `http://localhost:30080`) |
| โฟลเดอร์ LAB ใน container | `/workspace/007_kubernetes_deployment/02_LAB` (ตรงกับ repo ทุกไฟล์ — md5 64 ไฟล์) มีแค่บท 007 (ไม่ได้ copy บท 006 เข้าไป) |
| ไม่ได้แตะ | `k8s-lab` ของผู้เรียน, `deep_vision_5090_vllm` |

ลบเมื่อเสร็จ: `docker rm -fv k8s-lab-deploy007lab-06e5cc`

## สภาพปัจจุบัน (พร้อมถ่าย screenshot) — ทำตามขั้น LAB 10 จริง (apply `k8s-rs/` → `k8s/10-db.yaml` → `k8s/20-web.yaml`)

- ns `som-shop`: Deployment `som-db` 1/1 (Recreate, รับเลี้ยง RS `som-db` เดิม — Pod `som-db-9zrzs` ไม่เคยถูกสร้างใหม่) + Service ClusterIP `som-db`; Deployment `som-web` 3/3 `som-shop-web:1.2` (RS `som-web-7955fccc94` 3, RS เดิม `som-web` 0) + Service NodePort `som-web` `80:30080/TCP`
- **ออเดอร์รวม 4 รายการ** (`/api/stats` ทุก Pod `orders=4 products=6`)
- `kubectl -n som-shop rollout history deploy/som-web`:
  ```
  REVISION  CHANGE-CAUSE
  0         <none>                       ← RS som-web เดิมจากบท 006 (ไม่มี annotation revision)
  1         1.2 แปลงเป็น Deployment
  ```
- image `som-shop-web:1.2` / `1.3` และ `postgres:17.11-alpine` อยู่บนทุก Node; `som-shop-web:1.4` ไม่มี (ตั้งใจ)
- ไม่มี ns ของ LAB 1–9 ค้าง

รันคำสั่งด้วย `docker exec -it k8s-lab-deploy007lab-06e5cc bash` (หรือ ssh -p 2224) แล้ว `cd /workspace/007_kubernetes_deployment/02_LAB/som-shop-v3`
(ฉาก "terminal 1 / terminal 2" ให้เปิด 2 หน้าต่าง)

## ฉาก screenshot

1. **หน้าร้าน 1.2 (Deployment แล้ว)** — browser `http://172.18.0.1:30090`: แถบ `🐱 เสิร์ฟโดย Pod: som-web-7955fccc94-… · เวอร์ชัน 1.2`, ออเดอร์ 4, footer `Next.js + PostgreSQL · Kubernetes LAB 007 · namespace som-shop`
2. **ภาพรวมหลังแปลง** — `kubectl -n som-shop get deploy,rs,pods` (RS `som-web` `0 0 0` + `som-web-7955fccc94` `3 3 3`, RS `som-db` ไม่มี hash) และ
   `kubectl -n som-shop get rs som-web -o jsonpath='{.metadata.ownerReferences}{"\n"}'` (→ `"kind":"Deployment","name":"som-web"`) และ `kubectl -n som-shop rollout history deploy/som-web`
3. **rolling 1.2 → 1.3 ระหว่าง hit.sh (err=0)** —
   terminal 1: `./hit.sh -q http://localhost:30080/api/whoami 300`
   terminal 2:
   ```bash
   kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
   kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.3 ธีม sunset" --overwrite
   kubectl -n som-shop rollout status deploy/som-web          # ~18 วิ
   ```
   ผลที่ทดสอบ: `ok=300 err=0` (ทุกครั้ง 6/6 รอบ), rollout 17.5–18.6 วิ; ถ้าอยากเห็น 1.2/1.3 ปน ใช้ `./hit.sh http://localhost:30080/api/whoami 200` (ไม่ -q) ใน terminal 1 แทน
   ระหว่างนั้น terminal 3 `kubectl -n som-shop get pods -w` เห็น Pod เก่า `Terminating` → `0/1 Error` (5 วิหลัง Terminating = preStop แล้ว SIGTERM)
4. **หน้าร้าน 1.3** — browser Ctrl+F5: ธีมส้ม-ชมพู, แบนเนอร์ `🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟`, `เวอร์ชัน 1.3`, ออเดอร์ยัง 4
5. **history / undo** — `kubectl -n som-shop rollout history deploy/som-web` (0, 1 `1.2 แปลงเป็น Deployment`, 2 `1.3 ธีม sunset`) → `kubectl -n som-shop rollout undo deploy/som-web` (มี `Warning: ... last-applied-configuration ...`) → history (0, 2, 3 `1.2 แปลงเป็น Deployment`) → browser 1.2 ออเดอร์ 4 เท่าเดิม → `rollout undo` อีกครั้ง → history (0, 3, 4 `1.3 ธีม sunset`)
6. **รุ่นพัง 1.4 ร้านยังขาย** —
   terminal 1: `./hit.sh -q http://localhost:30080/api/whoami 700` (≈76 วิ ครอบช่วง deadline)
   terminal 2:
   ```bash
   kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.4
   kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.4 (ทดสอบรุ่นพัง)" --overwrite
   kubectl -n som-shop get pods                                # ~8 วิแรกเป็น PodInitializing แล้ว ErrImagePull / ImagePullBackOff
   kubectl -n som-shop rollout status deploy/som-web; echo $?  # ~60 วิหลัง set image → error: deployment "som-web" exceeded its progress deadline / 1
   kubectl -n som-shop get deploy som-web                      # READY 3/3  UP-TO-DATE 1  AVAILABLE 3
   kubectl -n som-shop describe pod <Pod ที่ 0/1> | tail -6    # pull access denied, repository does not exist ...
   ```
   browser ยังขายได้ (ทดสอบสั่งซื้อระหว่างนั้นได้ order ใหม่) ; hit.sh `ok=700 err=0` → `kubectl -n som-shop rollout undo deploy/som-web` (rollout status จบทันที 0.1 วิ เพราะ RS 1.3 ยังพร้อมครบ)
7. **scale 3→5** — `kubectl -n som-shop scale deploy/som-web --replicas=5` (~5 วิ) → `kubectl -n som-shop get pods -o wide`, `kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'` (5 บรรทัด — คอลัมน์ ENDPOINTS ปกติตัดที่ 3 `+ 2 more...`), `rollout history` ไม่มี revision ใหม่, `./hit.sh` เห็น 5 Pod
8. **ลบ db → 503 → rollout restart → ออเดอร์ 0** —
   ```bash
   kubectl -n som-shop delete pod -l app=som-db       # Pod ใหม่ Ready ~4.4 วิ
   # browser: 2–5 วิแรกอาจเปิดไม่ได้เลย (web ทุกตัว readiness ล้มชั่วครู่) แล้วเป็นหน้า "ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱" (503)
   curl -s -o /dev/null -w '%{http_code}\n' localhost:30080        # 503
   kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c 'select count(*) from orders'   # ERROR: relation "orders" does not exist
   kubectl -n som-shop rollout restart deploy/som-web  # 5 replicas ~33 วิ; หน้า 503 refresh เองแล้วกลับมา ออเดอร์ 0
   ```
9. **(ทางเลือก) Recreate ของ db** — terminal 1 `kubectl -n som-shop get pods -l app=som-db -w`; terminal 2 `kubectl -n som-shop rollout restart deploy/som-db` → Pod เก่า `Terminating` → `Completed` แล้ว **จึง** มี Pod ใหม่ `Pending` (ไม่มี 2 ตัวพร้อมกัน) Ready ใน ~4 วิ → ข้อมูลหาย ต้อง `rollout restart deploy/som-web` เติมสินค้าใหม่เหมือนข้อ 8

## คืนสภาพเริ่มต้น (1.2 + ออเดอร์ 4 + history 0/1)

```bash
cd /workspace/007_kubernetes_deployment/02_LAB/som-shop-v3
kubectl delete ns som-shop                                   # ~28 วิ (preStop + grace)
kubectl apply -f k8s-rs/ && kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=120s
kubectl apply -f k8s/10-db.yaml && kubectl apply -f k8s/20-web.yaml && kubectl -n som-shop rollout status deploy/som-web
for p in 1 4 5 6; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done
```
(ถ้าไม่ต้องการแถว REVISION 0 ให้ข้าม `k8s-rs/` แล้ว `kubectl apply -f k8s/` ตรง ๆ → history มีแค่ 1 — ทางนี้ยังไม่ได้ทดสอบ)
