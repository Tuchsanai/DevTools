# บทที่ 10: ConfigMap — กระดานประกาศของโซนที่ทุกบูธอ่านได้

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes ConfigMap — แยก config ออกจาก image ตามหลัก 12-factor, `data`/`binaryData` และขนาด 1 MiB, การสร้าง (`--from-literal`, `--from-file`, `--from-env-file`, YAML, `--dry-run=client -o yaml`), ใช้เป็น env (`configMapKeyRef`, `envFrom`, `prefix`, `$(VAR)`), ใช้เป็นไฟล์ (volume, `items`, `defaultMode`, `subPath`), `optional`, การอัปเดต (env vs volume, `..data`, reload, `rollout restart`, checksum), `immutable`, kustomize `configMapGenerator`, ConfigMap ของระบบ, การอ้างข้าม namespace และ RBAC
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-notice-board.png" alt="เปิดบท กระดานประกาศกลาง" width="900"><br>
  <em>เปิดบทที่ 10: ต่อจากบท 009 — ร้านมี db เป็น StatefulSet แล้ว แต่จะเปลี่ยนชื่อร้าน/โปรโมชันทีไรต้องแก้ YAML หรือ build image ใหม่ น้องส้มจึงติดกระดานประกาศกลางให้ทุกบูธอ่าน</em>
</p>

## บทนี้เรียนอะไร

บทที่ 9 ร้านอาหารแมวน้องส้มมีครัวกลางแบบโปรดักชันแล้ว (StatefulSet `som-db` + ตู้เซฟ `data-som-db-0`) แต่ทุกครั้งที่อยากเปลี่ยน **ชื่อร้าน ธีม หรือโปรโมชัน** ยังต้องแก้ `20-web.yaml` หรือ build image ใหม่ เพราะค่าพวกนี้เขียนตรงใน env หรือฝังใน image ด้วย `--build-arg` บทนี้แนะนำ **ConfigMap** หรือ **กระดานประกาศของโซน** ที่ติดการ์ด `key: value` ให้ทุกบูธใน namespace เดียวกันอ่าน ส่งค่าเข้า Pod ได้สองทาง คือ **ป้ายติดอกพนักงาน** (env/envFrom อ่านครั้งเดียวตอนเริ่ม เปลี่ยนแล้วต้อง rollout) และ **กระดานเล็กในบูธ** (volume ที่หุ่นยนต์ลูกเรือ kubelet อัปเดตให้เองราว 1 นาที) เราจะทดลองการสร้าง การอ้างของที่ไม่มี การจับเวลาอัปเดต แอปที่ต้อง reload เอง ConfigMap แบบ `immutable` และ kustomize `configMapGenerator` ปิดท้ายด้วย **ร้านน้องส้ม `som-shop-v6`** ที่เปลี่ยนชื่อร้าน ธีม โปรโมชัน และประกาศหน้าร้านได้ **โดยใช้ image `som-shop-web:1.5` ตัวเดียว ไม่ build ใหม่เลย** ออเดอร์ไม่หาย และจบด้วยปัญหาที่ยังเหลือ: คนที่อ่าน Deployment ได้ยังเห็นรหัสผ่านฐานข้อมูล

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ปัญหาค่าฝังใน image/YAML และหลัก 12-factor, config คืออะไร/ไม่ใช่อะไร, กายวิภาค ConfigMap (`data`, `binaryData`, 1 MiB, namespaced, ไม่ใช่ที่เก็บความลับ), วิธีสร้าง 4 แบบ, env/envFrom/prefix/`$(VAR)` และลำดับความสำคัญ, volume/items/defaultMode/subPath, ConfigMap ที่ไม่มีและ `optional`, การอัปเดต (`..data` symlink, เวลาจริง 37–88 วินาที, reload, `rollout restart`, checksum, ชื่อใหม่), `immutable`, `configMapGenerator`, ConfigMap ของระบบ, ข้าม namespace, RBAC, แนวปฏิบัติ และปัญหาที่ส่งต่อบทที่ 11 (40 ภาพประกอบ + คำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–10 จากง่ายไปยาก: เตรียมคลัสเตอร์และ image → ส่องและสร้าง ConfigMap → env ทีละ key และ `$(VAR)` → envFrom + prefix + ลำดับความสำคัญ → ConfigMap ที่ไม่มี/optional/ข้าม namespace → mount เป็นไฟล์ → จับเวลาการอัปเดต → nginx ต้อง reload / `rollout restart` / checksum → immutable → kustomize → **LAB สุดท้าย: ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่** (พร้อมภาพหน้าจอจริง 4 ภาพ) และ Troubleshooting, Checklist, ตารางเก็บกวาด | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีหัวข้อ 1–4 ก่อน** (ปัญหา, ConfigMap คืออะไร, วิธีสร้าง) แล้วเริ่ม LAB 0–1 ได้
2. ก่อน LAB 2–3 อ่านหัวข้อ 5 (env) ก่อน LAB 4 อ่านหัวข้อ 7 และ 11.2 ก่อน LAB 5 อ่านหัวข้อ 6 ก่อน LAB 6–7 อ่านหัวข้อ 8 ก่อน LAB 8 อ่านหัวข้อ 9 ก่อน LAB 9 อ่านหัวข้อ 10 และก่อน LAB 10 อ่านหัวข้อ 11.3 และ 12
3. ทำ LAB **ตามลำดับ** ConfigMap `shop-config` และ Pod `envpod` ที่สร้างใน LAB 2 ใช้ต่อถึง LAB 6 และ **ทำบล็อก "เก็บกวาด" ทุกครั้ง** ใช้เวลารวมประมาณ 3–3.5 ชั่วโมง (มีช่วงรอไฟล์อัปเดตราว 1 นาทีหลายครั้ง)
4. สังเกตสัญลักษณ์ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0, kubectl v1.37.1, Kustomize v5.8.1, 5 ตุลาคม 2569) แต่ **เวลา, AGE, ชื่อ Pod ที่สุ่ม, ชื่อโฟลเดอร์ `..2026_10_05_…` และจำนวนวินาทีที่ไฟล์อัปเดตอาจต่างจากเครื่องของนักศึกษา** ส่วนชื่อ ConfigMap ที่ kustomize สร้าง (`web-config-gh5tkgmddg`) จะเหมือนกันทุกเครื่องเมื่อไฟล์ตรงกันทุกไบต์
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ทุกอย่างของบทที่ 1–9 (Pod, Node, Namespace/RBAC/Pod Security, ReplicaSet, Service, Deployment, PV/PVC, StatefulSet) และ **ConfigMap, `kubectl apply -k` (kustomize ใน kubectl), checksum annotation** ส่วน **Secret ยังไม่ใช้** (รหัสผ่านฐานข้อมูลยังเขียนใน YAML โดยจงใจ เป็นค่าตัวอย่างเพื่อการเรียน) Ingress, HPA และ Helm เป็นบทหลัง (บทนี้ปูทางแค่แนวคิด checksum ที่ Helm ใช้)

## สิ่งที่ต้องผ่านก่อน

**ต้องผ่านบทที่ 1–9 ก่อน** โดยแบ่งเป็นพื้นฐาน (บทที่ 1–4) และชุดเรื่องต่อเนื่องของร้านน้องส้ม (บทที่ 5 → 6 → 7 → 8 → 9) บทนี้ต่อจาก **บทที่ 9 StatefulSet** โดยตรง

- **พื้นฐาน (ต้องผ่านบทที่ 1–4 ก่อน)**
  - [บทที่ 1: Kubernetes และสถาปัตยกรรม](../001_kubernetes-introduction/01_Theory/README.md) และ [LAB บทที่ 1](../001_kubernetes-introduction/02_LAB/readme.md): มี container **`k8s-lab`** ที่ publish พอร์ต `2223`, `8889` และ **`30080–30082`** ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น)
  - [บทที่ 2: Kubernetes Pod](../002_kubernetes_pod/01_Theory/README.md) และ [LAB บทที่ 2](../002_kubernetes_pod/02_LAB/README.md): เขียน Pod YAML ได้ เข้าใจ `command`/`args`, env, volume (emptyDir) และ init container
  - [บทที่ 3: Node กับ Pod](../003_kubernetes_node_pod/01_Theory/README.md) และ [LAB บทที่ 3](../003_kubernetes_node_pod/02_LAB/README.md): เข้าใจบทบาทของ kubelet และ **Downward API** (`fieldRef: metadata.namespace` ที่ร้านใช้ใน footer)
  - [บทที่ 4: Namespace](../004_kubernetes_namespace/01_Theory/README.md) และ [LAB บทที่ 4](../004_kubernetes_namespace/02_LAB/README.md): เข้าใจ namespaced object, **RBAC** (ServiceAccount, Role, RoleBinding, `kubectl auth can-i --as`) และ Pod Security Admission (`warn: restricted`)
- **ชุดเรื่องต่อเนื่องของร้านน้องส้ม: บทที่ 5 → 6 → 7 เป็นเรื่องต่อเนื่องกัน แล้วต่อด้วยบทที่ 8 → 9**
  - [บทที่ 5: ReplicaSet](../005_kubernetes_replicaset/01_Theory/README.md), [บทที่ 6: Service](../006_kubernetes_service/01_Theory/README.md) และ [บทที่ 7: Deployment](../007_kubernetes_deployment/01_Theory/README.md) พร้อม LAB ([5](../005_kubernetes_replicaset/02_LAB/README.md), [6](../006_kubernetes_service/02_LAB/README.md), [7](../007_kubernetes_deployment/02_LAB/README.md)): Service NodePort 30080, Deployment, rolling update, `rollout history/undo/restart`, `preStop`
  - [บทที่ 8: PersistentVolume และ PVC](../008_kubernetes_pv_pvc/01_Theory/README.md) และ [LAB บทที่ 8](../008_kubernetes_pv_pvc/02_LAB/README.md): ข้อมูลฐานข้อมูลอยู่ใน PVC ที่อายุยืนกว่า Pod
  - [บทที่ 9: StatefulSet](../009_kubernetes_statefulset/01_Theory/README.md) และ [LAB บทที่ 9](../009_kubernetes_statefulset/02_LAB/README.md) **(ต้องผ่านก่อน)**: db เป็น StatefulSet `som-db` พร้อม headless Service และ PVC `data-som-db-0` ซึ่งบทนี้ใช้ต่อแบบไม่เปลี่ยน
- คลัสเตอร์ kind `lab` จากบทก่อน **ใช้ต่อได้** ถ้ายังไม่มีคลัสเตอร์ LAB 0 จะสร้างใหม่ด้วย `k8s-up` ส่วน image `som-shop-web:1.5` เป็นรุ่นใหม่ของบทนี้ **ต้อง build จากแอปในบทนี้ทุกกรณี** และร้านของบทที่ 9 **ไม่จำเป็นต้องค้างไว้** (LAB 10 เริ่มร้านใหม่จาก `som-shop-v6/k8s-start/`)
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image `busybox`, `nginx`, `postgres`, `node`)

## บทที่ 5 → 6 → 7 → 8 → 9 → 10 เป็นเรื่องต่อเนื่องกัน

บทที่ 5–10 ใช้ร้านน้องส้มเรื่องเดียวกันต่อเนื่อง บทนี้รับร้านจาก **ท้ายบทที่ 9** (web Deployment 3 บูธ + db StatefulSet + NodePort 30080) มาย้ายป้ายร้านไปไว้บนกระดานประกาศ

| บท | ตัวละครใหม่ | ปัญหาที่แก้ |
|---|---|---|
| [5 ReplicaSet](../005_kubernetes_replicaset/) | หัวหน้ากะ | บูธหายแล้วไม่มีใครสร้างแทน → มีบูธครบจำนวนเสมอ |
| [6 Service](../006_kubernetes_service/) | ประภาคาร, คลิปบอร์ดรายชื่อบูธ, ประตู 30080 | ชื่อ/IP ของบูธเปลี่ยนทุกครั้ง → ที่อยู่คงที่ของร้าน |
| [7 Deployment](../007_kubernetes_deployment/) | ผู้จัดการร้าน, สมุดบันทึกรุ่น | เปลี่ยนรุ่นต้องลบบูธเองจนร้านสะดุด → เปลี่ยนรุ่นทีละบูธ ย้อนรุ่นได้ |
| [8 PV/PVC](../008_kubernetes_pv_pvc/) | ตู้เซฟบนเรือ, ใบเบิก | ข้อมูล db หายเมื่อ Pod db เกิดใหม่ → ข้อมูลอยู่ในตู้ที่อายุยืนกว่า Pod |
| [9 StatefulSet](../009_kubernetes_statefulset/) | หัวหน้ากะถือเครื่องจ่ายบัตรคิว, สมุดรายชื่อ | db มีได้ตัวเดียวและชื่อสุ่ม → ชื่อคงที่ `som-db-0`, DNS รายตัว, ตู้เซฟประจำตัว |
| **10 ConfigMap** (บทนี้) | กระดานประกาศของโซน, ป้ายติดอก, กระดานเล็กในบูธ, หุ่นยนต์ลูกเรือ kubelet, กระดานเคลือบ, เครื่องพิมพ์ป้าย | เปลี่ยนชื่อร้าน/ธีม/ประกาศต้องแก้ YAML หรือ build image → ค่าอยู่ใน ConfigMap ใช้ image เดียวทุกค่า |
| [11 Secret](../011_kubernetes_secret/) (บทถัดไป) | ซองปิดผนึก | รหัสผ่านฐานข้อมูล `som:meow1234` ยังอยู่ใน YAML ของ Deployment/StatefulSet ใครอ่าน Deployment/ConfigMap ได้ก็เห็นรหัส |

LAB สุดท้ายของบทนี้จบด้วยการให้ ServiceAccount `intern` ที่มีสิทธิ์แค่ "ดู" Pod/ConfigMap/Deployment/StatefulSet อ่าน YAML ของร้าน แล้วพบว่า **ยังเห็นรหัสผ่านฐานข้อมูล** (`som:meow1234@` 4 ที่ใน Deployment และ `POSTGRES_PASSWORD` ใน StatefulSet) และการย้ายรหัสไปไว้ใน ConfigMap ก็ไม่ช่วย นี่คือโจทย์ของ **บทที่ 11 Secret**

## โครงสร้างโฟลเดอร์

```text
010_kubernetes_configmap/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ 00–40 (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–10
    ├── images/                       ← ภาพประกอบ LAB 01–21 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน 4 ภาพ
    ├── labs/                         ← ไฟล์ของ LAB 1–9
    │   ├── lab01-create/             ← shop.env, announcement.txt, default.conf
    │   ├── lab02-env/                ← ConfigMap shop-config (ใช้ต่อ LAB 3–6) + Pod envpod
    │   ├── lab03-envfrom/            ← Pod envfrom (envFrom + prefix CFG_)
    │   ├── lab04-missing/            ← nocm, nokey, novol, optpod, other-ns
    │   ├── lab05-volume/             ← Pod volpod (ทั้งก้อน, items + defaultMode, subPath)
    │   ├── lab06-update/             ← watch.sh จับเวลาการอัปเดต
    │   ├── lab07-reload/             ← nginx-conf (v1/v2/v3), Pod ngx, Deployment plain
    │   ├── lab08-immutable/          ← frozen.yaml
    │   └── lab09-kustomize/kz/       ← kustomization.yaml, announcement.txt, deploy.yaml
    └── som-shop-v6/                  ← LAB 10 ร้านน้องส้มที่ป้ายร้านมาจาก ConfigMap
        ├── app/                      ← แอป Next.js + Dockerfile รุ่น 1.5 (SHOP_PROMO, อ่าน /etc/som/announcement.txt, /api/shop, /api/announcement)
        ├── k8s-start/                ← จุดเริ่ม: แบบท้ายบท 009 (ค่าร้านยังเขียนใน env)
        ├── k8s/                      ← 00-namespace, 10-db, 15-config (ConfigMap 2 แผ่น), 20-web (envFrom + volume)
        ├── extra/                    ← 15-config-promo, 16-announcement-1800, 17-config-v2 (immutable)
        ├── rbac/intern.yaml          ← ServiceAccount intern ดูได้อย่างเดียว
        ├── hit.sh                    ← ยิง request แล้วนับว่าไปตก Pod ไหน
        └── wait-announcement.sh      ← จับเวลาว่าประกาศใหม่ถึงทุก Pod เมื่อไร
```

ใน LAB 0 จะคัดลอกโฟลเดอร์ทั้งหมดนี้เข้า container ด้วย 🖥️ `docker cp 010_kubernetes_configmap k8s-lab:/workspace/` แล้วทำงานที่ `/workspace/010_kubernetes_configmap/02_LAB` ภายใน k8s-lab และเปิดร้านใน 🌐 browser ที่ `http://localhost:30080`

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md) → บทถัดไป: [บทที่ 11 Secret](../011_kubernetes_secret/)
