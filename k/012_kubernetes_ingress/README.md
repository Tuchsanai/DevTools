# บทที่ 12: Ingress — ประตูหน้าท่าเรือบานเดียวที่มีป้ายบอกทาง

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Ingress — NodePort/LoadBalancer กับ Ingress, L4 กับ L7, Ingress resource กับ Ingress controller, สถานะ ingress-nginx (archive 24 มี.ค. 2026) และ Traefik v3.7.13, IngressClass และ default class, host-based และ path fan-out, `pathType`, `defaultBackend` และรหัส 404/503/502, TLS termination + SNI ด้วย Secret `kubernetes.io/tls`, redirect HTTP → HTTPS, Middleware เฉพาะ controller (redirectScheme, basicAuth, stripPrefix), การ debug, rolling update ผ่าน Ingress, canary และ Gateway API
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-front-gate.png" alt="เปิดบท ประตูหน้าท่าเรือบานเดียว" width="900"><br>
  <em>เปิดบทที่ 12: ต่อจากบท 011 ร้านน้องส้มมีทั้งประตู HTTP และ HTTPS คนละเลข น้องส้มจึงสร้างประตูหน้าท่าเรือบานเดียวที่มีป้ายบอกทาง</em>
</p>

## บทนี้เรียนอะไร

บทที่ 11 ร้านอาหารแมวน้องส้มซ่อนรหัสผ่านฐานข้อมูลไว้ใน Secret และเปิด HTTPS ได้แล้ว แต่ลูกค้ายังต้อง **จำเลขประตู** เอง: หน้าร้าน HTTP อยู่ที่ NodePort `30080` HTTPS อยู่ที่ `30082` ผ่าน nginx ที่เราดูแลใบรับรองเอง และถ้าจะเพิ่มหน้าหลังร้านก็ต้องเปิดเลขประตูเพิ่มอีก บทนี้แนะนำ **Ingress** หรือ **ป้ายบอกทางที่ประตูหน้าท่าเรือบานเดียว** ที่มี **พนักงานต้อนรับ (Ingress controller)** อ่านป้ายแล้วพาลูกค้าไปเคาน์เตอร์ (Service) ที่ถูกต้องตาม **ชื่อ** และ **ทางเดิน (path)** พร้อมถอดรหัส HTTPS ที่ประตู (TLS termination) ด้วย Secret จากบทที่ 11 เนื่องจาก **ingress-nginx หยุดดูแลแล้ว (repo archive 24 มี.ค. 2026)** บทนี้จึงใช้ **Traefik v3.7.13** ติดตั้งด้วยไฟล์ YAML ที่ pin เวอร์ชัน (ไม่ใช้ Helm) และแยกให้เห็นชัดว่าอะไรเป็นมาตรฐานของ Kubernetes อะไรเป็นความสามารถเฉพาะ Traefik ปิดท้ายด้วย **ร้านน้องส้ม `som-shop-v8`** ที่ลูกค้าเข้าด้วย `http://shop.localhost:30080` แล้วถูกส่งต่อไป `https://shop.localhost:30081` อัตโนมัติ พนักงานเข้าหลังร้าน `https://admin.localhost:30081` ด้วยบัตร Service ของร้านเป็น ClusterIP ทั้งหมด และเปลี่ยนรุ่น 1.5 → 1.6 ผ่าน Ingress โดยลูกค้าไม่เจอ error

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ปัญหาของ NodePort/LoadBalancer, L4 กับ L7 และกายวิภาคคำขอ HTTP, Ingress resource กับ controller, ไทม์ไลน์การหยุดดูแลของ ingress-nginx และเกณฑ์เลือก Traefik, IngressClass/default class/class ผิด, โครงสร้าง YAML และ `backend.service.port`, name-based virtual hosting และ `*.localhost`, path fan-out และลำดับความสำคัญ, `pathType` สามแบบกับ `strictPrefixMatching` ของ Traefik, `defaultBackend` และรหัส 404/503/502, TLS termination, SNI, SAN, redirect HTTP → HTTPS และกับดักพอร์ตบน kind, มาตรฐานเทียบความสามารถเฉพาะ controller (Middleware), Traefik บน kind, การ debug, rolling update ผ่าน Ingress, canary, ข้อจำกัดของ Ingress และ Gateway API (53 ภาพประกอบ + คำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–10 จากง่ายไปยาก: เตรียมคลัสเตอร์และคืน NodePort ของร้านเดิม → ติดตั้ง Traefik + IngressClass → Ingress แผ่นแรก → path fan-out → host-based และ default class → `pathType` → ทำให้พังแล้ว debug → TLS ที่ Ingress → Middleware (redirect, basicAuth, stripPrefix) → rolling update ผ่าน Ingress → **LAB สุดท้าย: ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน** (พร้อมภาพหน้าจอจริง 6 ภาพ) + **LAB เสริม: ลองชิม Gateway API** และ Troubleshooting, Checklist, ตารางเก็บกวาด | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีหัวข้อ 1–6 ก่อน** (ปัญหา, L4/L7, resource กับ controller, ingress-nginx และ Traefik, IngressClass) แล้วเริ่ม LAB 0–1 ได้
2. ก่อน LAB 2–4 อ่านหัวข้อ 7–9 ก่อน LAB 5 อ่านหัวข้อ 10 ก่อน LAB 6 อ่านหัวข้อ 11 และ 16 ก่อน LAB 7 อ่านหัวข้อ 12 ก่อน LAB 8 อ่านหัวข้อ 13–14 ก่อน LAB 9 อ่านหัวข้อ 17 ก่อน LAB 10 อ่านหัวข้อ 15 และ 20 และก่อน LAB เสริมอ่านหัวข้อ 18–19
3. ทำ LAB **ตามลำดับ** Traefik ที่ติดตั้งใน LAB 1 ใช้ต่อจนจบบท ป้าย `shop` ถูกแก้ทับต่อกันตั้งแต่ LAB 2 ถึง LAB 8 และ **ต้องลบ namespace `ingress-demo` (ท้าย LAB 9) ก่อนเริ่ม LAB 10** ทำบล็อก "เก็บกวาด" ทุกครั้ง (โดยเฉพาะ `lab06-debug/lost.yaml` และการคืน args ของ Traefik หลัง LAB 5, 7) ใช้เวลารวมประมาณ 3.5–4 ชั่วโมง
4. สังเกตสัญลักษณ์ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0, kubectl v1.37.1, Traefik v3.7.13, 5 ตุลาคม 2569) แต่ **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, จำนวน error ของการทดลองแบบเปราะ และจำนวนออเดอร์อาจต่างจากเครื่องของนักศึกษา**
6. ชื่อ `shop.localhost`/`admin.localhost` ใช้ได้โดยไม่แก้ไฟล์ hosts กับ curl และ Chromium (ทดสอบแล้วบน Linux) **browser อื่นยังไม่ได้ทดสอบ** ถ้าเปิดไม่ได้ให้ใช้ทางสำรองใน LAB (`curl --resolve` หรือแก้ไฟล์ hosts)
7. รหัสผ่านทุกตัวในบทนี้ (`passwd`, `meow1234`, `meow-admin-123`) เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** และห้าม commit ไฟล์ `tls.key`
8. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ทุกอย่างของบทที่ 1–11 (Pod, Node, Namespace/RBAC/Pod Security, ReplicaSet, Service, Deployment, PV/PVC, StatefulSet, ConfigMap, Secret) และ **Ingress `networking.k8s.io/v1` + IngressClass กับ Traefik v3.7.13 (Middleware `traefik.io/v1alpha1`)** ส่วน **HPA และ Helm** เป็นบทถัดไป (บทนี้ปูทางไว้เท่านั้น) และ **Gateway API** ลองได้ใน LAB เสริม cert-manager, IngressRoute/TraefikService และ controller อื่นเรียนเป็นแนวคิด

## สิ่งที่ต้องผ่านก่อน

**ต้องผ่านบทที่ 1–11 ก่อน** โดยแบ่งเป็นพื้นฐาน (บทที่ 1–4) และชุดเรื่องต่อเนื่องของร้านน้องส้ม (บทที่ 5 → 6 → 7 แล้วต่อด้วย 8 → 9 → 10 → 11) บทนี้ต่อจาก **บทที่ 11 Secret** โดยตรง

- **พื้นฐาน (ต้องผ่านบทที่ 1–4 ก่อน)**
  - [บทที่ 1: Kubernetes และสถาปัตยกรรม](../001_kubernetes-introduction/01_Theory/README.md) และ [LAB บทที่ 1](../001_kubernetes-introduction/02_LAB/readme.md): มี container **`k8s-lab`** ที่ publish พอร์ต `2223`, `8889` และ **`30080–30082`** ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น)
  - [บทที่ 2: Kubernetes Pod](../002_kubernetes_pod/01_Theory/README.md) และ [LAB บทที่ 2](../002_kubernetes_pod/02_LAB/README.md): เขียน Pod YAML ได้ เข้าใจ readinessProbe และ lifecycle hook
  - [บทที่ 3: Node กับ Pod](../003_kubernetes_node_pod/01_Theory/README.md) และ [LAB บทที่ 3](../003_kubernetes_node_pod/02_LAB/README.md): เข้าใจ Node และ kubelet
  - [บทที่ 4: Namespace](../004_kubernetes_namespace/01_Theory/README.md) และ [LAB บทที่ 4](../004_kubernetes_namespace/02_LAB/README.md): เข้าใจ namespace, ClusterRole/ServiceAccount (ใช้กับสิทธิ์ของ Traefik) และ Pod Security Admission (`restricted`)
- **ชุดเรื่องต่อเนื่องของร้านน้องส้ม: บทที่ 5 → 6 → 7 เป็นเรื่องต่อเนื่องกัน แล้วต่อด้วยบทที่ 8 → 9 → 10 → 11**
  - [บทที่ 5: ReplicaSet](../005_kubernetes_replicaset/01_Theory/README.md), [บทที่ 6: Service](../006_kubernetes_service/01_Theory/README.md) และ [บทที่ 7: Deployment](../007_kubernetes_deployment/01_Theory/README.md) พร้อม LAB ([5](../005_kubernetes_replicaset/02_LAB/README.md), [6](../006_kubernetes_service/02_LAB/README.md), [7](../007_kubernetes_deployment/02_LAB/README.md)): Service ClusterIP/NodePort และ EndpointSlice, Deployment, rolling update (`maxUnavailable: 0`, preStop), `rollout history/restart`
  - [บทที่ 8: PersistentVolume และ PVC](../008_kubernetes_pv_pvc/01_Theory/README.md) และ [LAB บทที่ 8](../008_kubernetes_pv_pvc/02_LAB/README.md): ข้อมูลฐานข้อมูลอยู่ใน PVC ที่อายุยืนกว่า Pod
  - [บทที่ 9: StatefulSet](../009_kubernetes_statefulset/01_Theory/README.md) และ [LAB บทที่ 9](../009_kubernetes_statefulset/02_LAB/README.md): db เป็น StatefulSet `som-db` + headless Service + PVC `data-som-db-0`
  - [บทที่ 10: ConfigMap](../010_kubernetes_configmap/01_Theory/README.md) และ [LAB บทที่ 10](../010_kubernetes_configmap/02_LAB/README.md): ป้ายร้านจาก ConfigMap และการ `rollout restart` ให้ env ใหม่มีผล
  - [บทที่ 11: Secret](../011_kubernetes_secret/01_Theory/README.md) และ [LAB บทที่ 11](../011_kubernetes_secret/02_LAB/README.md) **(ต้องผ่านก่อน)**: Secret ชนิด `kubernetes.io/tls` และ `kubernetes.io/basic-auth`, ใบรับรอง self-signed ด้วย `openssl`, `curl -k`/`--cacert` และร้าน `som-shop-v7` ที่บทนี้รับมาทำต่อ
- คลัสเตอร์ kind `lab` และร้านของบทที่ 11 **ใช้ต่อได้** (LAB 0 จะคืน NodePort ของร้านเดิมโดยเก็บฐานข้อมูลไว้) ถ้ายังไม่มีคลัสเตอร์ LAB 0 จะสร้างใหม่ด้วย `k8s-up` แล้ว build/load `som-shop-web:1.5` และ `1.6` จากแอปในบทนี้ (`02_LAB/som-shop-v8/app`) และโหลด `postgres:17.11-alpine` ด้วย `docker save --platform` + `kind load image-archive` (LAB 10 มีขั้นสำหรับเริ่มร้านใหม่)
- เครื่องต่ออินเทอร์เน็ตได้ (Node ดึง image `traefik:v3.7.13`, `traefik/whoami:v1.11.0`, `nginxinc/nginx-unprivileged:1.27-alpine` จาก Docker Hub และ LAB เสริมดาวน์โหลด CRD ของ Gateway API จาก GitHub)

## บทที่ 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 เป็นเรื่องต่อเนื่องกัน

บทที่ 5–12 ใช้ร้านน้องส้มเรื่องเดียวกันต่อเนื่อง บทนี้รับร้านจาก **ท้ายบทที่ 11** (web Deployment 3 บูธ + db StatefulSet + ConfigMap ป้ายร้าน + Secret รหัส DB และ TLS + NodePort 30080/30082) มาย้ายทางเข้าไปไว้ที่ประตู Ingress เดียว

| บท | ตัวละครใหม่ | ปัญหาที่แก้ |
|---|---|---|
| [5 ReplicaSet](../005_kubernetes_replicaset/) | หัวหน้ากะ | บูธหายแล้วไม่มีใครสร้างแทน → มีบูธครบจำนวนเสมอ |
| [6 Service](../006_kubernetes_service/) | ประภาคาร, คลิปบอร์ดรายชื่อบูธ, ประตู 30080 | ชื่อ/IP ของบูธเปลี่ยนทุกครั้ง → ที่อยู่คงที่ของร้าน |
| [7 Deployment](../007_kubernetes_deployment/) | ผู้จัดการร้าน, สมุดบันทึกรุ่น | เปลี่ยนรุ่นต้องลบบูธเองจนร้านสะดุด → เปลี่ยนรุ่นทีละบูธ ย้อนรุ่นได้ |
| [8 PV/PVC](../008_kubernetes_pv_pvc/) | ตู้เซฟบนเรือ, ใบเบิก | ข้อมูล db หายเมื่อ Pod db เกิดใหม่ → ข้อมูลอยู่ในตู้ที่อายุยืนกว่า Pod |
| [9 StatefulSet](../009_kubernetes_statefulset/) | หัวหน้ากะถือเครื่องจ่ายบัตรคิว, สมุดรายชื่อ | db มีได้ตัวเดียวและชื่อสุ่ม → ชื่อคงที่ `som-db-0`, DNS รายตัว, ตู้เซฟประจำตัว |
| [10 ConfigMap](../010_kubernetes_configmap/) | กระดานประกาศของโซน, ป้ายติดอก, กระดานเล็กในบูธ | เปลี่ยนชื่อร้าน/ธีม/ประกาศต้องแก้ YAML หรือ build image → ค่าอยู่ใน ConfigMap |
| [11 Secret](../011_kubernetes_secret/) | ซองปิดผนึกในกล่องกุญแจ, ท่อแก้วปิดสนิท (TLS) | รหัสผ่านอยู่ใน YAML → รหัสอยู่ใน Secret และเปิด HTTPS ด้วย nginx |
| **12 Ingress** (บทนี้) | ป้ายบอกทางที่ประตูหน้าท่าเรือ, หุ่นยนต์พนักงานต้อนรับ (controller), ยูนิฟอร์มดาวทอง (IngressClass), ประตูกระจกนิรภัย (TLS), โต๊ะของหาย (defaultBackend), ด่านในทางเดิน (Middleware), กระดานแก้ว (dashboard), อาคารผู้โดยสารรุ่นใหม่ (Gateway API) | ลูกค้าต้องจำเลขประตู 30080/30082 และเราดูแล nginx HTTPS เอง → ประตูเดียวด้วยชื่อ `shop.localhost`/`admin.localhost`, TLS ที่ประตู, HTTP → HTTPS อัตโนมัติ และหลังร้านที่ต้องมีบัตร |

LAB สุดท้ายของบทนี้จบด้วยร้านที่มีหน้าร้านเดียวด้วยชื่อแล้ว แต่ยังเหลือโจทย์ให้บทถัดไป: ร้านคนแน่นแต่จำนวนบูธตายตัว 3 ตัว (→ **HPA** เพิ่มบูธอัตโนมัติ), ติดตั้ง Traefik และร้านหลายไฟล์ต้องทำตามลำดับเอง (→ **Helm** แพ็กเป็นแพ็กเกจ) และข้อจำกัดของ Ingress ที่ฟีเจอร์เสริมผูกกับ controller และทำ canary แบบแบ่งน้ำหนักไม่ได้ (→ **Gateway API** ซึ่งมี LAB เสริมให้ลองแล้ว)

## ตัวละครของบทนี้

<p align="center">
  <img src="01_Theory/images/00-character-som.png" alt="น้องส้ม ตัวละครหลักของบทเรียน" width="600"><br>
  <em>น้องส้ม — ผู้ช่วยกัปตัน Kubernetes แมวส้มสวมหมวกกัปตันพวงมาลัยเรือและผ้าพันคอสีเขียวอมฟ้า (ภาพอ้างอิงตัวละครที่ใช้ในภาพประกอบทุกภาพ) บทนี้น้องส้มสร้างประตูหน้าท่าเรือที่มีป้ายบอกทางและหุ่นยนต์พนักงานต้อนรับ</em>
</p>

## โครงสร้างโฟลเดอร์

```text
012_kubernetes_ingress/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพตัวละคร 00 + ภาพประกอบ 01–53 (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–10 + LAB เสริม
    ├── .gitignore                    ← กัน *.key, *.crt
    ├── images/                       ← ภาพประกอบ LAB 01–31 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของ LAB 10 จำนวน 6 ภาพ
    ├── ingress-controller/           ← LAB 1: traefik-crds-v3.7.13.yml (CRD ทางการ) + 00-traefik.yaml (Traefik v3.7.13, Service NodePort 30080/30081/30082, IngressClass default)
    ├── lab02-first/                  ← 10-apps.yaml (menu/api/admin = whoami ใน ns ingress-demo), 20-ingress.yaml (ป้ายแผ่นแรก)
    ├── lab03-fanout/                 ← ingress.yaml (/ /api /admin)
    ├── lab04-hosts/                  ← ingress.yaml (admin.localhost ไม่ใส่ class)
    ├── lab05-pathtype/               ← ingress.yaml (Prefix/Exact/ImplementationSpecific), try-paths.sh
    ├── lab06-debug/                  ← wrongclass.yaml, typo.yaml, lost.yaml (defaultBackend)
    ├── lab07-tls/                    ← ingress-tls.yaml (spec.tls + Secret som-tls)
    ├── lab08-middleware/             ← redirect.yaml, redirect-noport.yaml, admin-auth.yaml, strip.yaml (Middleware ของ Traefik)
    ├── lab09-rolling/                ← loop.sh, menu-v2.yaml, menu-fragile.yaml
    ├── labx-gateway/                 ← LAB เสริม: gateway-rbac.yml, 60-gateway.yaml (GatewayClass/Gateway/HTTPRoute 90/10)
    └── som-shop-v8/                  ← LAB 10 ร้านน้องส้มหน้าร้านเดียวด้วยชื่อโดเมน
        ├── app/                      ← แอป Next.js + Dockerfile (สำเนาจากบทที่ 11 ไม่แก้โค้ด, build เป็น som-shop-web:1.5 และ 1.6)
        ├── k8s/                      ← 00-namespace, 10-db, 15-config (ป้ายบท 012), 20-web (ClusterIP), 40-admin (หลังร้าน), 50-ingress (Middleware + Ingress 2 แผ่น)
        ├── .gitignore                ← กัน secret.yaml, *.secret.yaml, *.key, *.crt
        └── hit.sh                    ← ยิง HTTPS ผ่าน Ingress แล้วนับว่าไปตก Pod/เวอร์ชันไหน (CURL_OPTS)
```

ใน LAB 0 จะคัดลอกโฟลเดอร์ทั้งหมดนี้เข้า container ด้วย 🖥️ `docker cp 012_kubernetes_ingress k8s-lab:/workspace/` แล้วทำงานที่ `/workspace/012_kubernetes_ingress/02_LAB` ภายใน k8s-lab (ร้านของ LAB 10 อยู่ที่ `/workspace/012_kubernetes_ingress/02_LAB/som-shop-v8/`) เปิดร้านใน 🌐 browser ที่ `http://shop.localhost:30080` (ถูกส่งต่อไป `https://shop.localhost:30081`) หลังร้านที่ `https://admin.localhost:30081` และ dashboard ของ Traefik ที่ `http://localhost:30082/dashboard/` (ในบทนี้ `http://localhost:30080` ที่ไม่มีชื่อร้านจะได้ `404 page not found` ของ Traefik ซึ่งเป็นเรื่องปกติ)

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md) → บทก่อนหน้า: [บทที่ 11 Secret](../011_kubernetes_secret/)
