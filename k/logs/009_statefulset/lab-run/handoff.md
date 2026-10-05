# Handoff: container ทดลองบท 009 StatefulSet (ยังเปิดอยู่ ผู้ประสานงานลบเอง)

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-sts009lab-19f6aa` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22 (`ssh -p 2224 root@<gateway หรือ localhost>` รหัส LAB `passwd`); ทดสอบแล้ว `hostname` = `k8s-lab` |
| NodePort | host **30090 / 30091 / 30092** → container 30080 / 30081 / 30082 → kind `lab-control-plane` (extraPortMappings) |
| gateway (agent อยู่ใน container) | `172.18.0.1` → เปิด **http://172.18.0.1:30090** (บน Docker host = `http://localhost:30090`; ในเอกสารนักศึกษา = `http://localhost:30080`) |
| โฟลเดอร์ LAB ใน container | `/workspace/009_kubernetes_statefulset/02_LAB` (ตรงกับ repo, md5 46 ไฟล์ใต้ `labs/` + `som-shop-v5/`) มีแค่บท 009 |
| ไม่ได้แตะ | `k8s-lab` ของผู้เรียน, `deep_vision_5090_vllm`; ไม่ได้ `docker system prune` |

ลบเมื่อเสร็จ: `docker rm -fv k8s-lab-sts009lab-19f6aa`

## สภาพปัจจุบัน (พร้อมถ่าย screenshot)

- ns `som-shop` (`kubectl apply -f k8s/` ใหม่หลังจบ LAB 10 ขั้น I แล้วรันฉาก 3–5 ด้านล่างไปแล้ว 1 รอบ กลับมาสภาพเดิม):
  - headless Service `som-db` (`CLUSTER-IP None`, 5432/TCP)
  - StatefulSet `som-db` **1/1** → Pod `som-db-0` บน lab-worker2
  - PVC `data-som-db-0` `Bound` `pvc-de97dba8-addf-43cc-8f6f-3c51311e4d2c` 1Gi RWO `standard` (PV Delete) — จาก volumeClaimTemplates
  - Deployment `som-web` 3/3 `som-shop-web:1.2` (RS `som-web-cbb884886`) `DATABASE_URL …@som-db-0.som-db:5432/catshop` + Service NodePort `som-web` `80:30080/TCP`
- **ออเดอร์รวม 4 รายการ** (`/api/stats` ทุก Pod `orders=4 products=6`)
- footer หน้าร้าน `Next.js + PostgreSQL · Kubernetes LAB 009 · namespace som-shop`
- PV มีใบเดียว (ของ data-som-db-0), ไม่มี ns/ทรัพยากรของ LAB 1–9 ค้าง, 3 Node Ready ไม่มี taint
- image `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บนทุก Node (nginx:1.27/1.28-alpine, busybox:1.36 ถูก Node ดึงไว้แล้ว)

รันคำสั่งด้วย `docker exec -it k8s-lab-sts009lab-19f6aa bash` (หรือ ssh -p 2224) แล้ว `cd /workspace/009_kubernetes_statefulset/02_LAB/som-shop-v5`

## ฉาก screenshot (ฉาก 3–5 ซ้อมแล้วใน `screenshot-scenes.log`)

1. **หน้าร้าน** (browser `http://172.18.0.1:30090`): ออเดอร์ 4, แถบ `เสิร์ฟโดย Pod: som-web-cbb884886-… · เวอร์ชัน 1.2`, footer LAB 009
2. **ภาพรวม**:
   ```bash
   kubectl -n som-shop get sts,deploy,pod,svc,pvc -o wide
   kubectl get pv
   ```
3. **ลบ som-db-0 แล้วกลับมาชื่อเดิม PVC เดิม ออเดอร์เดิม**:
   ```bash
   kubectl -n som-shop get pod som-db-0 -o custom-columns=NAME:.metadata.name,UID:.metadata.uid,IP:.status.podIP,PVC:.spec.volumes[0].persistentVolumeClaim.claimName
   kubectl -n som-shop delete pod som-db-0
   kubectl -n som-shop wait --for=condition=Ready pod/som-db-0 --timeout=120s
   kubectl -n som-shop get pod som-db-0 -o custom-columns=NAME:.metadata.name,UID:.metadata.uid,IP:.status.podIP,PVC:.spec.volumes[0].persistentVolumeClaim.claimName
   sleep 2; curl -s localhost:30080/api/stats          # orders=4
   ```
   (ซ้อมแล้ว: UID `1d055972…` → `53da1ec1…`, IP `10.244.2.63` → `10.244.2.64`, PVC `data-som-db-0` เท่าเดิม) แล้ว refresh browser ออเดอร์ 4
4. **ลบ StatefulSet แล้ว apply ใหม่ ออเดอร์ยังอยู่**:
   ```bash
   kubectl -n som-shop delete sts som-db
   kubectl -n som-shop get sts,pod,pvc -l app=som-db     # เหลือแค่ PVC data-som-db-0 Bound
   curl -s -w ' [%{http_code}]\n' localhost:30080/api/stats   # ระหว่างนี้ db-not-ready [503]
   kubectl apply -f k8s/10-db.yaml                       # service/som-db unchanged, statefulset.apps/som-db created
   kubectl -n som-shop rollout status sts/som-db
   sleep 2; curl -s localhost:30080/api/stats            # orders=4
   ```
5. **scale db เป็น 3 เห็น PVC แยกต่อ Pod (และข้อมูลแยก)**:
   ```bash
   kubectl -n som-shop scale sts som-db --replicas=3
   kubectl -n som-shop rollout status sts/som-db         # ~17 วิ
   kubectl -n som-shop get pod,pvc -l app=som-db -o wide # data-som-db-0/1/2, som-db-1 ลง lab-worker
   for i in 0 1 2; do echo "som-db-$i: $(kubectl -n som-shop exec som-db-$i -- psql -U som -d catshop -tAc 'select count(*) from orders' 2>&1 | head -1)"; done
   #   som-db-0: 4 / som-db-1, som-db-2: ERROR:  relation "orders" does not exist
   curl -s localhost:30080/api/stats                     # ยัง orders=4 (web ชี้ som-db-0.som-db)
   ```
   **คืนสภาพหลังฉากนี้ (ต้องทำ):**
   ```bash
   kubectl -n som-shop scale sts som-db --replicas=1; sleep 5
   kubectl -n som-shop delete pvc data-som-db-1 data-som-db-2
   ```
6. (เสริม) **DNS headless**:
   ```bash
   kubectl -n som-shop run dns --image=busybox:1.36 --rm -it --restart=Never -- sh
   / # nslookup som-db                  # 1 Address (หรือ 3 ระหว่างฉาก 5)
   / # nslookup som-db-0.som-db
   / # exit
   ```
   (มี Warning PodSecurity ของ ns som-shop ขึ้นก่อน — เป็นแค่ warn)
7. (เสริม) **read replica**: ดูขั้น H ใน `lab10.log` (`exec som-db-0 … pg_hba.conf` → `kubectl apply -f extra/replica.yaml`) จบแล้วลบด้วย `kubectl -n som-shop delete sts som-db-replica && kubectl -n som-shop delete pvc data-som-db-replica-0` (บรรทัด replication ใน pg_hba.conf ค้างอยู่ใน PVC ไม่เป็นไร)

ถ้าออเดอร์ไม่ใช่ 4 (เช่นทำฉากเพิ่ม) คืนสภาพทั้งร้าน:
```bash
kubectl delete ns som-shop        # ~32 วิ (PVC/PV หายตาม เพราะ PV Delete)
kubectl apply -f k8s/
kubectl -n som-shop rollout status sts/som-db; kubectl -n som-shop rollout status deploy/som-web
for p in 1 2 3 1; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done
```
