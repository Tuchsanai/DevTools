# บทที่ 11: Secret — ซองปิดผนึกในกล่องกุญแจของโซน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Secret — ความต่างจาก ConfigMap, base64 ไม่ใช่การเข้ารหัส, `type` ของ Secret (`Opaque`, `basic-auth`, `dockerconfigjson`, `tls`, `service-account-token`), การสร้างและกับดัก `stringData` + `last-applied-configuration`, ใช้ใน Pod (`secretKeyRef`, `envFrom.secretRef`, volume แบบ tmpfs, `defaultMode`), การอัปเดตและ `immutable`, `imagePullSecrets` กับ registry ส่วนตัว, TLS Secret กับ nginx HTTPS, projected volume, RBAC และการอ่าน Secret ทางอ้อม, etcd กับ encryption at rest, การเปลี่ยนรหัสผ่านสองฝั่ง และแนวทางภายนอก (Sealed Secrets, External Secrets, Vault)
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-sealed-envelope.png" alt="เปิดบท ซองปิดผนึกในกล่องกุญแจ" width="900"><br>
  <em>เปิดบทที่ 11: ต่อจากบท 010 — ป้ายร้านอยู่ใน ConfigMap แล้ว แต่รหัส DB ยังอยู่ใน YAML ที่ใครก็อ่านได้ น้องส้มจึงย้ายรหัสใส่ซองปิดผนึกในกล่องกุญแจ</em>
</p>

## บทนี้เรียนอะไร

บทที่ 10 ร้านอาหารแมวน้องส้มย้ายชื่อร้าน ธีม โปรโมชัน และประกาศหน้าร้านไปไว้บนกระดานประกาศของโซน (ConfigMap) ได้แล้ว แต่ **รหัสผ่านฐานข้อมูล `som:meow1234` ยังเขียนตรงอยู่ใน YAML** ของ Deployment และ StatefulSet ServiceAccount `intern` ที่มีสิทธิ์แค่ "ดู" ก็อ่านรหัสได้ 4 ที่ บทนี้แนะนำ **Secret** หรือ **ซองปิดผนึกในกล่องกุญแจของโซน** ที่ใช้งานแบบเดียวกับ ConfigMap แต่แยกสิทธิ์อ่านได้ และชี้ให้เห็นความจริงสำคัญว่า **base64 เป็นแค่ซองใส ไม่ใช่การเข้ารหัส** ความปลอดภัยจริงมาจาก RBAC, encryption at rest, tmpfs บน Node และวินัยของทีม เราจะทดลองสร้างซองหลายแบบ ส่งเข้า Pod ทำ HTTPS เปิด registry ส่วนตัวที่ต้องมีบัตรผ่าน ดูว่าใครแอบอ่านซองได้ทางอ้อม และส่องว่ารหัสถูกเก็บใน etcd อย่างไร ปิดท้ายด้วย **ร้านน้องส้ม `som-shop-v7`** ที่ย้ายรหัสไปไว้ใน Secret จน intern อ่านไม่ได้ **เปลี่ยนรหัสฐานข้อมูลจริงโดยออเดอร์ไม่หาย** (พร้อมเห็นว่าถ้าทำไม่ครบสองฝั่ง ร้านจะล่มเป็นช่วง ๆ) และเปิดร้านผ่าน HTTPS ที่ `https://localhost:30082` โดยใช้ image `som-shop-web:1.5` ตัวเดิมไม่แก้โค้ด

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ปัญหารหัสใน YAML, Secret เทียบ ConfigMap, base64 ไม่ใช่การเข้ารหัสและกับดัก `echo`, ชั้นป้องกันจริง, `type` 5 แบบและการตรวจ key, `--from-literal`/`--from-file`/`data`/`stringData` และกับดัก `last-applied-configuration`, `secretKeyRef`/`envFrom`/volume tmpfs/`defaultMode`, env รั่วง่าย, การอัปเดต (ราว 1 นาที) และ `immutable`, `imagePullSecrets` และการตรวจบัตรซ้ำของ kubelet v1.37, TLS self-signed กับ nginx, RBAC และการอ่านทางอ้อม (`create pods`, `pods/exec`), etcd และ EncryptionConfiguration, การไม่ commit ลง git, ทางรั่ว, การเปลี่ยนรหัสสองฝั่ง, Sealed Secrets / External Secrets / Vault, projected volume และปัญหาที่ส่งต่อบทถัดไป (39 ภาพประกอบ + คำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–9 จากง่ายไปยาก: เตรียมคลัสเตอร์และ image → base64 ไม่ใช่การเข้ารหัส → สร้าง Secret หลายแบบและ type → ใช้ใน Pod การอัปเดต และ immutable → TLS + nginx HTTPS → `imagePullSecrets` กับ registry ส่วนตัว → projected volume และ token → RBAC และการอ่านทางอ้อม → ส่อง etcd → **LAB สุดท้าย: ร้านน้องส้มซ่อนรหัสผ่าน** (พร้อมภาพหน้าจอจริง 5 ภาพ) และ Troubleshooting, Checklist, ตารางเก็บกวาด | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีหัวข้อ 1–2 ก่อน** (ปัญหาและ Secret คืออะไร) แล้วเริ่ม LAB 0–1 ได้
2. ก่อน LAB 2 อ่านหัวข้อ 3–4 ก่อน LAB 3 อ่านหัวข้อ 5 ก่อน LAB 4 อ่านหัวข้อ 7 ก่อน LAB 5 อ่านหัวข้อ 6 ก่อน LAB 6 อ่านหัวข้อ 3.4 และ 12 ก่อน LAB 7 อ่านหัวข้อ 8 ก่อน LAB 8 อ่านหัวข้อ 9 และก่อน LAB 9 อ่านหัวข้อ 10.3 และ 13.4
3. ทำ LAB **ตามลำดับ** Secret `demo`, `sd` และ Pod `spod` ที่สร้างใน LAB 1–3 ใช้ต่อถึง LAB 8 และไฟล์ใบรับรองของ LAB 4 ใช้ต่อใน LAB 9 **ทำบล็อก "เก็บกวาด" ทุกครั้ง** (โดยเฉพาะ `./cleanup-registry.sh` ของ LAB 5) ใช้เวลารวมประมาณ 3–3.5 ชั่วโมง
4. สังเกตสัญลักษณ์ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0, kubectl v1.37.1, OpenSSL 3.0.13, 5 ตุลาคม 2569) แต่ **เวลา, AGE, ชื่อ Pod ที่สุ่ม, IP, ค่า sha256 และจำนวนวินาทีที่ไฟล์อัปเดตอาจต่างจากเครื่องของนักศึกษา**
6. รหัสผ่านทุกตัวในบทนี้ (`passwd`, `meow1234`, `purr5678`, `hiss9012`, `newpass-01`, `example-pass` ฯลฯ) เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** และ **ห้ามแปะ token ของ ServiceAccount ลงรายงาน** (เอกสารตัดเหลือ `eyJhbGciOi...`)
7. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ทุกอย่างของบทที่ 1–10 (Pod, Node, Namespace/RBAC/Pod Security, ReplicaSet, Service, Deployment, PV/PVC, StatefulSet, ConfigMap) และ **Secret ทุก type, `imagePullSecrets` กับ registry ภายใน (`registry:2` + htpasswd บน network `kind`), TLS กับ nginx, projected volume และ `etcdctl` แบบอ่านอย่างเดียว** ส่วน **Ingress, HPA และ Helm** เป็นบทหลัง ส่วน **EncryptionConfiguration, Sealed Secrets, External Secrets และ Vault** เรียนเป็นแนวคิด (ไม่ติดตั้งและไม่แก้ kube-apiserver ใน LAB)

## สิ่งที่ต้องผ่านก่อน

**ต้องผ่านบทที่ 1–10 ก่อน** โดยแบ่งเป็นพื้นฐาน (บทที่ 1–4) และชุดเรื่องต่อเนื่องของร้านน้องส้ม (บทที่ 5 → 6 → 7 แล้วต่อด้วย 8 → 9 → 10) บทนี้ต่อจาก **บทที่ 10 ConfigMap** โดยตรง

- **พื้นฐาน (ต้องผ่านบทที่ 1–4 ก่อน)**
  - [บทที่ 1: Kubernetes และสถาปัตยกรรม](../001_kubernetes-introduction/01_Theory/README.md) และ [LAB บทที่ 1](../001_kubernetes-introduction/02_LAB/readme.md): มี container **`k8s-lab`** ที่ publish พอร์ต `2223`, `8889` และ **`30080–30082`** ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น) และรู้จัก etcd ใน control plane
  - [บทที่ 2: Kubernetes Pod](../002_kubernetes_pod/01_Theory/README.md) และ [LAB บทที่ 2](../002_kubernetes_pod/02_LAB/README.md): เขียน Pod YAML ได้ เข้าใจ env, volume และ init container
  - [บทที่ 3: Node กับ Pod](../003_kubernetes_node_pod/01_Theory/README.md) และ [LAB บทที่ 3](../003_kubernetes_node_pod/02_LAB/README.md): เข้าใจบทบาทของ kubelet (คนเปิดซองให้ Pod) และ Downward API
  - [บทที่ 4: Namespace](../004_kubernetes_namespace/01_Theory/README.md) และ [LAB บทที่ 4](../004_kubernetes_namespace/02_LAB/README.md): เข้าใจ **RBAC** (ServiceAccount, Role, RoleBinding, `kubectl auth can-i --as`, context ของ intern) และ Pod Security Admission (`warn: restricted`)
- **ชุดเรื่องต่อเนื่องของร้านน้องส้ม: บทที่ 5 → 6 → 7 เป็นเรื่องต่อเนื่องกัน แล้วต่อด้วยบทที่ 8 → 9 → 10**
  - [บทที่ 5: ReplicaSet](../005_kubernetes_replicaset/01_Theory/README.md), [บทที่ 6: Service](../006_kubernetes_service/01_Theory/README.md) และ [บทที่ 7: Deployment](../007_kubernetes_deployment/01_Theory/README.md) พร้อม LAB ([5](../005_kubernetes_replicaset/02_LAB/README.md), [6](../006_kubernetes_service/02_LAB/README.md), [7](../007_kubernetes_deployment/02_LAB/README.md)): Service NodePort 30080, Deployment, rolling update (`maxUnavailable: 0`), `progressDeadlineSeconds`, `rollout history/restart`
  - [บทที่ 8: PersistentVolume และ PVC](../008_kubernetes_pv_pvc/01_Theory/README.md) และ [LAB บทที่ 8](../008_kubernetes_pv_pvc/02_LAB/README.md): ข้อมูลฐานข้อมูลอยู่ใน PVC ที่อายุยืนกว่า Pod
  - [บทที่ 9: StatefulSet](../009_kubernetes_statefulset/01_Theory/README.md) และ [LAB บทที่ 9](../009_kubernetes_statefulset/02_LAB/README.md): db เป็น StatefulSet `som-db` + headless Service (`som-db-0.som-db`) + PVC `data-som-db-0`
  - [บทที่ 10: ConfigMap](../010_kubernetes_configmap/01_Theory/README.md) และ [LAB บทที่ 10](../010_kubernetes_configmap/02_LAB/README.md) **(ต้องผ่านก่อน)**: env/envFrom/volume, การอัปเดตราว 1 นาที, `immutable` และ ConfigMap ป้ายร้านที่บทนี้ใช้ต่อ
- คลัสเตอร์ kind `lab` จากบทก่อน **ใช้ต่อได้** ถ้ายังไม่มีคลัสเตอร์ LAB 0 จะสร้างใหม่ด้วย `k8s-up` แล้ว build/load `som-shop-web:1.5` จากแอปในบทนี้ (`02_LAB/som-shop-v7/app`) และโหลด `postgres:17.11-alpine` ด้วย `docker save --platform` + `kind load image-archive` ร้านของบทที่ 10 **ไม่จำเป็นต้องค้างไว้** (LAB 9 เริ่มร้านใหม่จาก `som-shop-v7/k8s-010/`)
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image `busybox`, `nginx`, `nginx-unprivileged`, `httpd`, `registry`, `postgres`, `node`)

## บทที่ 5 → 6 → 7 → 8 → 9 → 10 → 11 เป็นเรื่องต่อเนื่องกัน

บทที่ 5–11 ใช้ร้านน้องส้มเรื่องเดียวกันต่อเนื่อง บทนี้รับร้านจาก **ท้ายบทที่ 10** (web Deployment 3 บูธ + db StatefulSet + ConfigMap ป้ายร้าน + NodePort 30080) มาย้ายรหัสผ่านใส่ซองปิดผนึก

| บท | ตัวละครใหม่ | ปัญหาที่แก้ |
|---|---|---|
| [5 ReplicaSet](../005_kubernetes_replicaset/) | หัวหน้ากะ | บูธหายแล้วไม่มีใครสร้างแทน → มีบูธครบจำนวนเสมอ |
| [6 Service](../006_kubernetes_service/) | ประภาคาร, คลิปบอร์ดรายชื่อบูธ, ประตู 30080 | ชื่อ/IP ของบูธเปลี่ยนทุกครั้ง → ที่อยู่คงที่ของร้าน |
| [7 Deployment](../007_kubernetes_deployment/) | ผู้จัดการร้าน, สมุดบันทึกรุ่น | เปลี่ยนรุ่นต้องลบบูธเองจนร้านสะดุด → เปลี่ยนรุ่นทีละบูธ ย้อนรุ่นได้ |
| [8 PV/PVC](../008_kubernetes_pv_pvc/) | ตู้เซฟบนเรือ, ใบเบิก | ข้อมูล db หายเมื่อ Pod db เกิดใหม่ → ข้อมูลอยู่ในตู้ที่อายุยืนกว่า Pod |
| [9 StatefulSet](../009_kubernetes_statefulset/) | หัวหน้ากะถือเครื่องจ่ายบัตรคิว, สมุดรายชื่อ | db มีได้ตัวเดียวและชื่อสุ่ม → ชื่อคงที่ `som-db-0`, DNS รายตัว, ตู้เซฟประจำตัว |
| [10 ConfigMap](../010_kubernetes_configmap/) | กระดานประกาศของโซน, ป้ายติดอก, กระดานเล็กในบูธ | เปลี่ยนชื่อร้าน/ธีม/ประกาศต้องแก้ YAML หรือ build image → ค่าอยู่ใน ConfigMap |
| **11 Secret** (บทนี้) | ซองปิดผนึกในกล่องกุญแจ, ซองใส (base64), บัตรพนักงานแถบเขียว/เทา, ตู้นิรภัยในหอบังคับการ, ถาดฟองน้ำความจำ, ท่อแก้วปิดสนิท, บัตรผ่านคลังตู้สินค้า | รหัสผ่าน `som:meow1234` อยู่ใน YAML ใครอ่าน Deployment ได้ก็เห็น → รหัสอยู่ใน Secret ที่ intern อ่านไม่ได้ เปลี่ยนรหัสได้โดยออเดอร์ไม่หาย และเปิด HTTPS |

LAB สุดท้ายของบทนี้จบด้วยร้านที่ซ่อนรหัสผ่านได้แล้ว แต่ยังเหลือโจทย์ให้บทถัดไป: ลูกค้าต้องจำพอร์ต 30080/30082 และเราดูแล TLS เอง (→ **Ingress**), จำนวนบูธตายตัว 3 ตัว (→ **HPA**), manifest หลายไฟล์และคำสั่ง `create secret` ต้องทำตามลำดับเอง (→ **Helm**) และ etcd ยังเก็บรหัสเป็นข้อความ (→ **EncryptionConfiguration / External Secrets**)

## ตัวละครของบทนี้

<p align="center">
  <img src="01_Theory/images/00-character-som.png" alt="น้องส้ม ตัวละครหลักของบทเรียน" width="600"><br>
  <em>น้องส้ม — ผู้ช่วยกัปตัน Kubernetes แมวส้มสวมหมวกกัปตันพวงมาลัยเรือและผ้าพันคอสีเขียวอมฟ้า (ภาพอ้างอิงตัวละครที่ใช้ในภาพประกอบทุกภาพ) บทนี้น้องส้มดูแลซองปิดผนึกครั่งรูปอุ้งเท้าในกล่องกุญแจของโซน</em>
</p>

## โครงสร้างโฟลเดอร์

```text
011_kubernetes_secret/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพตัวละคร 00 + ภาพประกอบ 01–39 (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–9
    ├── images/                       ← ภาพประกอบ LAB 01–22 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน 5 ภาพ
    ├── labs/                         ← ไฟล์ของ LAB 2–8 (LAB 1 ใช้คำสั่งล้วน)
    │   ├── lab02-types/              ← pw.txt (ไม่มี newline), sd.yaml (data + stringData)
    │   ├── lab03-use/                ← spod.yaml (env/envFrom/volume), frozen.yaml (immutable), wait-secret.sh
    │   ├── lab04-tls/                ← tls.yaml (nginx HTTPS + NodePort 30081)
    │   ├── lab05-registry/           ← setup-registry.sh, cleanup-registry.sh, Dockerfile + menu.txt (som-menu:1.0), 00-ns + Pod 5 แบบ
    │   ├── lab06-projected/          ← proj.yaml (projected volume), builder-token.yaml (service-account-token)
    │   ├── lab07-rbac/               ← intern.yaml, maker.yaml, peek.yaml
    │   └── lab08-etcd/               ← etcdget.sh (etcdctl แบบอ่านอย่างเดียว)
    └── som-shop-v7/                  ← LAB 9 ร้านน้องส้มที่รหัสผ่านอยู่ใน Secret
        ├── app/                      ← แอป Next.js + Dockerfile รุ่น 1.5 (สำเนาบทที่ 10 ไม่แก้โค้ด)
        ├── k8s-010/                  ← จุดเริ่ม: สภาพท้ายบท 010 (รหัสยังเขียนใน YAML)
        ├── k8s/                      ← 00-namespace, 10-db, 15-config, 20-web (secretKeyRef), 30-https (NodePort 30082)
        ├── examples/                 ← 05-secret.example.yaml (ไฟล์ Secret ตัวอย่างค่าปลอม)
        ├── extra/                    ← 30-https-restricted.yaml (HTTPS แบบผ่าน Pod Security restricted)
        ├── rbac/                     ← intern.yaml (ดูได้อย่างเดียว), intern-context.sh (context ด้วย token อายุ 24h)
        ├── .gitignore                ← กัน secret.yaml, *.secret.yaml, *.key, *.crt
        ├── hit.sh                    ← ยิง request แล้วนับว่าไปตก Pod ไหน
        └── wait-announcement.sh      ← (จากบทที่ 10) จับเวลาประกาศหน้าร้าน
```

ใน LAB 0 จะคัดลอกโฟลเดอร์ทั้งหมดนี้เข้า container ด้วย 🖥️ `docker cp 011_kubernetes_secret k8s-lab:/workspace/` แล้วทำงานที่ `/workspace/011_kubernetes_secret/02_LAB` ภายใน k8s-lab และเปิดร้านใน 🌐 browser ที่ `http://localhost:30080` (HTTP) และ `https://localhost:30082` (HTTPS ใบรับรอง self-signed)

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md) → บทก่อนหน้า: [บทที่ 10 ConfigMap](../010_kubernetes_configmap/)
