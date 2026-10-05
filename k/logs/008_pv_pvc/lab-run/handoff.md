# Handoff: container ทดลองบท 008 PV/PVC (ยังเปิดอยู่ ผู้ประสานงานลบเอง)

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-pv008lab-ff12a9` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22 (`ssh -p 2224 root@<gateway หรือ localhost>` รหัส LAB `passwd`); ทดสอบแล้ว `hostname` = `k8s-lab` |
| NodePort | host **30090 / 30091 / 30092** → container 30080 / 30081 / 30082 → kind `lab-control-plane` (extraPortMappings) |
| gateway (agent อยู่ใน container) | `172.18.0.1` → เปิด **http://172.18.0.1:30090** (บน Docker host = `http://localhost:30090`; ในเอกสารนักศึกษา = `http://localhost:30080`) |
| โฟลเดอร์ LAB ใน container | `/workspace/008_kubernetes_pv_pvc/02_LAB` (ตรงกับ repo md5 62 ไฟล์) มีแค่บท 008 |
| ไม่ได้แตะ | `k8s-lab` ของผู้เรียน, `deep_vision_5090_vllm` |

ลบเมื่อเสร็จ: `docker rm -fv k8s-lab-pv008lab-ff12a9`

## สภาพปัจจุบัน (พร้อมถ่าย screenshot)

- ns `som-shop` (apply `k8s/` ใหม่หลังจบ LAB 10):
  - Deployment `som-db` 1/1 **Recreate** (Pod `som-db-7b786655f5-…` บน lab-worker) + Service ClusterIP `som-db`
  - PVC `som-db-data` `Bound` `pvc-12c65838-6304-45a3-8367-43944c66298c` 1Gi RWO `standard` (PV Delete)
  - Deployment `som-web` 3/3 `som-shop-web:1.2` (RS `som-web-7d79d9779f`) + Service NodePort `som-web` `80:30080/TCP`
- **ออเดอร์รวม 4 รายการ** (`/api/stats` ทุก Pod `orders=4 products=6`)
- footer หน้าร้าน `Next.js + PostgreSQL · Kubernetes LAB 008 · namespace som-shop`
- ไม่มี StorageClass อื่นนอกจาก `standard`, ไม่มี PV ค้าง, ไม่มี ns ของ LAB 1–9; 3 Node Ready
- image `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บนทุก Node

รันคำสั่งด้วย `docker exec -it k8s-lab-pv008lab-ff12a9 bash` (หรือ ssh -p 2224) แล้ว `cd /workspace/008_kubernetes_pv_pvc/02_LAB/som-shop-v4`

## ฉาก screenshot

1. **หน้าร้านจำได้** (browser `http://172.18.0.1:30090`): ออเดอร์ 4, แถบ `เสิร์ฟโดย Pod: som-web-7d79d9779f-… · เวอร์ชัน 1.2`
2. **ภาพรวม**:
   ```bash
   kubectl -n som-shop get deploy,pod,svc,pvc
   kubectl get sc,pv
   ```
3. **ลบ Pod db แล้วออเดอร์ยังอยู่** (ไม่ต้อง restart web):
   ```bash
   kubectl -n som-shop delete pod -l app=som-db
   kubectl -n som-shop rollout status deploy/som-db
   sleep 3; for i in 1 2 3; do curl -s localhost:30080/api/stats; done   # orders=4 (request แรกอาจได้ db-not-ready 1 ครั้ง)
   ```
   แล้ว refresh browser เห็นออเดอร์ 4 เท่าเดิม
4. **ลบ Deployment db แล้ว apply ใหม่ ออเดอร์ยังอยู่**:
   ```bash
   kubectl -n som-shop delete deploy som-db
   kubectl -n som-shop get pvc                      # som-db-data ยัง Bound
   kubectl apply -f k8s/10-db.yaml                  # persistentvolumeclaim/som-db-data unchanged
   kubectl -n som-shop rollout status deploy/som-db
   curl -s localhost:30080/api/stats                # orders=4
   ```
5. **ดูไฟล์ postgres บน Node**:
   ```bash
   N=$(kubectl -n som-shop get pod -l app=som-db -o jsonpath='{.items[0].spec.nodeName}')
   PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}')
   docker exec $N ls -ln /var/local-path-provisioner/${PV}_som-shop_som-db-data/pgdata
   ```
6. **ลบ PVC แล้วข้อมูลหายจริง** (ทำเป็นฉากสุดท้าย เพราะออเดอร์หาย):
   ```bash
   kubectl -n som-shop delete deploy som-db
   kubectl -n som-shop delete pvc som-db-data
   kubectl get pv                                   # Released ชั่วครู่ แล้วหาย
   kubectl apply -f k8s/10-db.yaml
   kubectl -n som-shop rollout status deploy/som-db
   curl -s -w ' [%{http_code}]\n' localhost:30080/api/stats   # db-not-ready [503] → browser หน้าร้าน 503
   kubectl -n som-shop rollout restart deploy/som-web
   kubectl -n som-shop rollout status deploy/som-web          # ~18 วิ
   curl -s localhost:30080/api/stats                          # orders=0 → browser ออเดอร์ 0
   ```
   ถ้าจะคืนสภาพ 4 ออเดอร์หลังฉากนี้:
   ```bash
   for p in 1 2 3 1; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done
   ```
7. (เสริม) **RWOP กันตัวที่ 2**: ดูคำสั่งขั้น H ใน `lab10.log` (ต้องลบ db+PVC เดิมก่อน) และเมื่อจบให้ลบ PV ที่ Retain + `kubectl delete sc standard-retain`
