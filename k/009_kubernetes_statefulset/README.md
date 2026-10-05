# บทที่ 9: StatefulSet — หัวหน้ากะที่ตั้งเลขบูธและแจกตู้เซฟประจำตัว

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes StatefulSet — stateless กับ stateful, การรับประกัน 3 ข้อ (ชื่อ `<sts>-<ordinal>`, DNS ต่อ Pod, storage ประจำตัว), headless Service (`clusterIP: None`) และ `serviceName`, `volumeClaimTemplates` และ `persistentVolumeClaimRetentionPolicy`, `podManagementPolicy` (OrderedReady/Parallel), `updateStrategy` (RollingUpdate, partition, OnDelete), ControllerRevision และ `rollout history/undo`, `minReadySeconds`, replicas ≠ replication (postgres streaming replication, Operator), Node ล่มกับ at-most-one และ taint `out-of-service`, การย้ายข้อมูลจาก Deployment + PVC มาเป็น StatefulSet และแนวปฏิบัติสำหรับฐานข้อมูล
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-three-kitchens.png" alt="น้องส้มอยากมีครัวหลายครัวที่แต่ละครัวมีชื่อและตู้เซฟของตัวเอง" width="900"><br>
  <em>เปิดบทที่ 9: ต่อจากบท 008 — ร้านจำออเดอร์ได้แล้ว แต่ db มีได้ตัวเดียว น้องส้มอยากมีครัวหลายครัวที่แต่ละครัวมีชื่อและตู้เซฟของตัวเอง</em>
</p>

## บทนี้เรียนอะไร

บทที่ 8 ร้านอาหารแมวน้องส้ม **จำออเดอร์ได้แล้ว** ด้วยตู้เซฟ (PV) และใบเบิก (PVC) แต่ครัวกลางยังเป็น Deployment ที่มีได้แค่ตัวเดียว เพราะ Deployment ใช้ Pod template เดียว ทุก Pod จึงถือใบเบิกใบเดียวกัน scale เป็น 2 แล้ว postgres สองตัวเขียนโฟลเดอร์เดียวจนออเดอร์หาย ชื่อ Pod ก็สุ่มใหม่ทุกครั้ง บทนี้แนะนำ **StatefulSet** หรือ **หัวหน้ากะที่ถือเครื่องจ่ายบัตรคิว** ที่เปิดบูธทีละบูธตามเลข `-0`, `-1`, `-2` แจก **ตู้เซฟประจำตัวเลขเดียวกับบูธ** (`volumeClaimTemplates`) และมี **สมุดรายชื่อ (headless Service)** บอกที่อยู่ของแต่ละบูธตรง ๆ (`som-db-0.som-db`) เราจะทดลองลำดับการเปิด/ปิด การเก็บตู้เมื่อ scale ลงหรือลบ StatefulSet การเปลี่ยนรุ่นทีละบูธด้วย partition/OnDelete และหยุด Node จริงเพื่อดูว่าทำไม StatefulSet ไม่ยอมสร้างบูธแทน ปิดท้ายด้วย **ร้านน้องส้มแบบโปรดักชัน** (`som-shop-v5`) ที่ **ย้ายข้อมูลเดิมของบทที่ 8** มาเป็น PVC `data-som-db-0` ของ StatefulSet `som-db` พิสูจน์ว่าลบ Pod, rolling update หรือลบ StatefulSet ออเดอร์ก็ไม่หาย เห็นว่า scale เป็น 3 **ไม่ใช่การทำสำเนา** และทำ read replica จริงด้วย postgres streaming replication

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ทำไม Deployment ไม่พอสำหรับระบบ stateful, การรับประกัน 3 ข้อและกายวิภาค manifest, ชื่อ/hostname/label อัตโนมัติ, headless Service และ DNS ต่อ Pod (Pod ที่ไม่ Ready ไม่อยู่ใน DNS, เปลี่ยน ClusterIP เป็น headless ไม่ได้), volumeClaimTemplates และ retention policy (เทียบ reclaimPolicy ของ PV), OrderedReady/Parallel, RollingUpdate/partition/OnDelete/minReadySeconds/ControllerRevision, replicas ≠ replication และ Operator, Node ล่ม (at most one, force delete, out-of-service), web ต่อ db ด้วยชื่อไหน, การย้ายข้อมูลจาก Deployment, แนวปฏิบัติ และปัญหาที่ส่งต่อบทถัดไป (38 ภาพประกอบ + คำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–10 จากง่ายไปยาก: เตรียมคลัสเตอร์และ image → Deployment เทียบ StatefulSet → headless Service และ DNS → volumeClaimTemplates → OrderedReady/Parallel → scale และ PVC retention → RollingUpdate + partition + rollout undo → minReadySeconds + OnDelete → ลบ StatefulSet แล้ว apply ใหม่ (รวม `--cascade=orphan`) → Node ล่มกับ out-of-service → **LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชัน db เป็น StatefulSet** (ย้าย PVC + LAB เสริม read replica พร้อมภาพหน้าจอจริง) และ Troubleshooting, Checklist, ตารางเก็บกวาด | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีหัวข้อ 1–3 ก่อน** (ปัญหาของ Deployment กับ db, คุณสมบัติของ StatefulSet) แล้วเริ่ม LAB 0–1 ได้
2. ก่อน LAB 2 อ่านหัวข้อ 4 (headless Service, DNS) ก่อน LAB 3 อ่านหัวข้อ 5.1–5.2 ก่อน LAB 4 อ่านหัวข้อ 6 ก่อน LAB 5 และ 8 อ่านหัวข้อ 5.3–5.4 ก่อน LAB 6–7 อ่านหัวข้อ 7 ก่อน LAB 9 อ่านหัวข้อ 9 และก่อน LAB 10 อ่านหัวข้อ 8 และ 10
3. ทำ LAB **ตามลำดับ** StatefulSet `web` ที่สร้างใน LAB 3 ใช้ต่อเนื่องถึง LAB 9 และ **ทำบล็อก "เก็บกวาด" ทุกครั้ง** โดยเฉพาะการลบ PVC ของ StatefulSet ซึ่งไม่หายเอง และ **ต้องเอา taint `out-of-service` ออกและ `docker start` Node ที่หยุดใน LAB 9 ก่อนทำ LAB 10** ใช้เวลารวมประมาณ 3–3.5 ชั่วโมง
4. สังเกตสัญลักษณ์ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0, kubectl v1.37.1, 5 ตุลาคม 2569) แต่ **เวลา, IP, UID, ชื่อ PV (`pvc-<uid>`), revision hash และ Node ที่ Pod ถูกวางอาจต่างจากเครื่องของนักศึกษา** ส่วนชื่อ Pod ของ StatefulSet (`web-0`, `som-db-0`) และชื่อ PVC (`www-web-1`, `data-som-db-0`) จะเหมือนกันทุกเครื่อง
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ทุกอย่างของบทที่ 1–8 (Pod, ReplicaSet, Deployment, Service, PV, PVC, StorageClass) และ StatefulSet, headless Service, volumeClaimTemplates, partition/OnDelete, taint `out-of-service` รหัสผ่านฐานข้อมูลยังเขียนใน YAML ตรง ๆ (ค่าตัวอย่างเพื่อการเรียน) ส่วน ConfigMap/Secret, Ingress, HPA, PodDisruptionBudget และ Operator เป็นแนวคิด/บทหลัง

## สิ่งที่ต้องผ่านก่อน

**ต้องผ่านบทที่ 1–8 ก่อน** โดยแบ่งเป็นพื้นฐาน (บทที่ 1–4) และชุดเรื่องต่อเนื่องของร้านน้องส้ม (บทที่ 5 → 6 → 7 → 8) บทนี้ต่อจาก **บทที่ 8 PersistentVolume/PVC** โดยตรง

- [บทที่ 1: Kubernetes และสถาปัตยกรรม](../001_kubernetes-introduction/01_Theory/README.md) และ [LAB บทที่ 1](../001_kubernetes-introduction/02_LAB/readme.md): เข้าใจบทบาทของ Control Plane, Worker Node และมี container **`k8s-lab`** ที่สร้างตามบทที่ 1 (publish พอร์ต `2223`, `8889` และ **`30080–30082`**) ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น)
- [บทที่ 2: Kubernetes Pod](../002_kubernetes_pod/01_Theory/README.md) และ [LAB บทที่ 2](../002_kubernetes_pod/02_LAB/README.md): เขียน Pod YAML ได้ เข้าใจ labels, **readinessProbe** (StatefulSet ใช้ตัดสินลำดับและ DNS) และ init container
- [บทที่ 3: Node กับ Pod](../003_kubernetes_node_pod/01_Theory/README.md) และ [LAB บทที่ 3](../003_kubernetes_node_pod/02_LAB/README.md): เข้าใจ kube-scheduler, **taint/toleration** และเหตุการณ์ **Node ล่ม**
- [บทที่ 4: Namespace](../004_kubernetes_namespace/01_Theory/README.md) และ [LAB บทที่ 4](../004_kubernetes_namespace/02_LAB/README.md): เข้าใจ namespaced/cluster-scoped, **DNS search domain** และ Pod Security Admission (`warn: restricted`)
- **[บทที่ 5: ReplicaSet](../005_kubernetes_replicaset/01_Theory/README.md), [บทที่ 6: Service](../006_kubernetes_service/01_Theory/README.md) และ [บทที่ 7: Deployment](../007_kubernetes_deployment/01_Theory/README.md) พร้อม LAB ([5](../005_kubernetes_replicaset/02_LAB/README.md), [6](../006_kubernetes_service/02_LAB/README.md), [7](../007_kubernetes_deployment/02_LAB/README.md)):** บทที่ 5 → 6 → 7 เป็นเรื่องต่อเนื่องกัน เข้าใจ ReplicaSet, Service ClusterIP/EndpointSlice/NodePort 30080, Deployment, RollingUpdate/Recreate, `rollout history/undo` และ `minReadySeconds`
- **[บทที่ 8: PersistentVolume และ PVC](../008_kubernetes_pv_pvc/01_Theory/README.md) และ [LAB บทที่ 8](../008_kubernetes_pv_pvc/02_LAB/README.md) (ต้องผ่านก่อน):** เข้าใจ PV/PVC/StorageClass, `standard` (local-path, WaitForFirstConsumer), **Retain และการกู้ PV (`claimRef`/`volumeName`)**, ข้อมูลผูก Node และเคยเห็นผลเสียหายเมื่อ scale db บน Deployment เป็น 2 (ร้าน `som-shop-v4`)
- คลัสเตอร์ kind `lab` จากบทก่อน **ใช้ต่อได้** (ถ้ายังมี image `som-shop-web:1.2` และ `postgres:17.11-alpine` ก็ไม่ต้อง build ใหม่) ถ้ายังไม่มีคลัสเตอร์ LAB 0 จะสร้างใหม่ด้วย `k8s-up` และ build image ร้านจากสำเนาแอปในบทนี้ ร้านของบทที่ 8 **ไม่จำเป็นต้องค้างไว้** LAB 10 สร้างสภาพท้ายบทที่ 8 ใหม่จาก `som-shop-v5/k8s-008/` ได้
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image `nginx`, `busybox`, `postgres`, `node`)

## บทที่ 5 → 6 → 7 → 8 → 9 เป็นเรื่องต่อเนื่องกัน

บทที่ 5–9 ใช้ร้านน้องส้มเรื่องเดียวกันต่อเนื่อง บทนี้รับร้านจาก **ท้ายบทที่ 8** (db เป็น Deployment + PVC) มาเปลี่ยนครัวกลางเป็น StatefulSet

| บท | ตัวละครใหม่ | ปัญหาที่แก้ |
|---|---|---|
| [5 ReplicaSet](../005_kubernetes_replicaset/) | หัวหน้ากะ | บูธหายแล้วไม่มีใครสร้างแทน → มีบูธครบจำนวนเสมอ |
| [6 Service](../006_kubernetes_service/) | ประภาคาร, คลิปบอร์ดรายชื่อบูธ, ประตู 30080 | ชื่อ/IP ของบูธเปลี่ยนทุกครั้ง → ที่อยู่คงที่ของร้าน เปิดร้านจาก browser และแยก db กลาง |
| [7 Deployment](../007_kubernetes_deployment/) | ผู้จัดการร้าน, สมุดบันทึกรุ่น | เปลี่ยนรุ่นต้องลบบูธเองจนร้านสะดุด → เปลี่ยนรุ่นทีละบูธ ย้อนรุ่นได้ |
| [8 PV/PVC](../008_kubernetes_pv_pvc/) | ตู้เซฟบนเรือ, ใบเบิก, โรงทำตู้อัตโนมัติ | ข้อมูล db หายเมื่อ Pod db เกิดใหม่ → ข้อมูลอยู่ในตู้ที่อายุยืนกว่า Pod |
| **9 StatefulSet** (บทนี้) | หัวหน้ากะถือเครื่องจ่ายบัตรคิว, สมุดใบเบิกฉีกได้, สมุดรายชื่อบนแท่นอ่าน, เชือกกั้นแถว | db มีได้ตัวเดียวและชื่อสุ่ม → ชื่อคงที่ (`som-db-0`), DNS รายตัว (`som-db-0.som-db`) และตู้เซฟประจำตัวทุก Pod (`data-som-db-0`) |

LAB สุดท้ายของบทนี้เริ่มจากร้านแบบเดียวกับ **ท้ายบทที่ 8** (web Deployment 3 บูธ + db Deployment `Recreate` + PVC `som-db-data` + Service NodePort 30080) แล้วย้ายตู้เซฟเดิมเข้า StatefulSet โดยไม่เสียออเดอร์ และจบด้วยปัญหาที่ส่งต่อบทถัดไป: รหัสผ่านฐานข้อมูลยังอยู่ใน YAML (→ ConfigMap/Secret), เปิดร้านด้วยเลขพอร์ตแทนชื่อโดเมน (→ Ingress), web ยังต้อง scale เอง (→ HPA) และการ replicate ฐานข้อมูลจริงจังพร้อม failover (→ Operator)

## โครงสร้างโฟลเดอร์

```text
009_kubernetes_statefulset/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ 00–38 (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–10
    ├── images/                       ← ภาพประกอบ LAB 01–24 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
    ├── labs/                         ← YAML และสคริปต์ของ LAB 1–9
    │   ├── lab01-compare/            ← Deployment web-d กับ StatefulSet web
    │   ├── lab02-headless/           ← headless Service, StatefulSet, Pod dns (busybox)
    │   ├── lab03-vct/                ← StatefulSet web + volumeClaimTemplates (ใช้ต่อ LAB 4–8)
    │   ├── lab04-order/              ← bad.yaml (readiness ไม่ผ่าน), par.yaml (Parallel)
    │   ├── lab05-retention/          ← par.yaml (whenScaled/whenDeleted: Delete)
    │   ├── lab06-update/             ← partition-2.yaml, partition-0.yaml, show.sh
    │   ├── lab07-ondelete/           ← min-ready.yaml, ondelete.yaml
    │   └── lab09-node-down/          ← sts-tol.yaml (tolerationSeconds 30)
    └── som-shop-v5/                  ← LAB 10 ร้านน้องส้มแบบโปรดักชัน
        ├── app/                      ← สำเนาแอป Next.js + Dockerfile จากบทที่ 8 (som-shop-web:1.2)
        ├── k8s-008/                  ← สภาพท้ายบทที่ 8: 00-namespace.yaml, 10-db.yaml (PVC + Deployment + Service ClusterIP), 20-web.yaml
        ├── k8s/                      ← บทนี้: 00-namespace.yaml, 10-db.yaml (headless Service + StatefulSet), 20-web.yaml (ต่อ som-db-0.som-db)
        ├── migrate/                  ← data-som-db-0-pvc.yaml (ใบเบิกที่ชี้ PV เดิม)
        ├── extra/                    ← replica.yaml (LAB เสริม read replica)
        └── hit.sh                    ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err
```

ใน LAB 0 จะคัดลอกโฟลเดอร์ทั้งหมดนี้เข้า container ด้วย 🖥️ `docker cp 009_kubernetes_statefulset k8s-lab:/workspace/` แล้วทำงานที่ `/workspace/009_kubernetes_statefulset/02_LAB` ภายใน k8s-lab (LAB 1–9 ที่ `labs/labNN-…`, LAB 10 ที่ `som-shop-v5/`) บทนี้มีสำเนาแอปร้านและสภาพร้านท้ายบทที่ 8 ของตัวเอง จึงไม่ต้องมีโฟลเดอร์ของบทที่ 8 ใน container พอร์ต 30080–30082 ของ kind ถูก map ออกมาที่ `localhost` ของเครื่องนักศึกษาไว้แล้วตั้งแต่บทที่ 1 จึงเปิดร้านที่ `http://localhost:30080` ได้โดยไม่ต้อง port-forward

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)
