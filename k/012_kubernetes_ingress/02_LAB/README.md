# LAB บทที่ 12: Ingress — ประตูหน้าท่าเรือบานเดียว สู่ร้านน้องส้มที่เข้าด้วยชื่อ

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Ingress — คืน NodePort ของร้านเดิม, ติดตั้ง Traefik v3.7.13 + IngressClass (CRD ก่อน controller), Ingress แรก, path fan-out, host-based และ default class, `pathType` และ `strictPrefixMatching`, debug (class ผิด, Service/port ผิด, ไม่มี Pod Ready, defaultBackend), TLS ที่ Ingress และ SNI, Middleware ของ Traefik (redirect HTTP → HTTPS, basicAuth, stripPrefix), rolling update ผ่าน Ingress และร้านอาหารแมวน้องส้มที่มีหน้าร้านเดียวด้วยชื่อ `shop.localhost` + หลังร้าน `admin.localhost` พร้อม LAB เสริม Gateway API
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะช่วยน้องส้มสร้าง **ประตูหน้าท่าเรือบานเดียว** ให้ร้านอาหารแมวน้องส้ม เริ่มจากคืนเลขประตู NodePort ที่ร้านของบทที่ 11 จองไว้ ติดตั้ง **พนักงานต้อนรับ (Ingress controller) Traefik** แขวน **ป้ายบอกทาง (Ingress)** แผ่นแรก แยกทางเดินตาม path และตามชื่อ ทดลองกฎ `pathType` ทำให้พังทีละแบบเพื่อฝึกอ่านรหัส 404/503 ติด **ประตูกระจกนิรภัย (TLS)** ด้วย Secret จากบทที่ 11 เพิ่ม **ด่านในทางเดิน (Middleware)** ส่งต่อ HTTP → HTTPS และตรวจบัตรหน้าหลังร้าน แล้ววัดว่าเปลี่ยนรุ่นผ่านประตูนี้โดยลูกค้าไม่เจอ error ได้จริงไหม ปิดท้ายด้วย **ร้านน้องส้ม `som-shop-v8`** ที่ลูกค้าเข้าด้วย `http://shop.localhost:30080` แล้วถูกส่งต่อไป `https://shop.localhost:30081` อัตโนมัติ พนักงานเข้าหลังร้านที่ `https://admin.localhost:30081` ด้วยบัตร และ Service ของร้านเป็น ClusterIP ทั้งหมด **ใช้ image `som-shop-web:1.5` เดิมและ `1.6` (build จากโค้ดชุดเดียวกัน ต่างแค่เลขเวอร์ชัน)** และ LAB เสริมให้ลองชิม **Gateway API**

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, kind 3 Node, Kubernetes v1.37.0, kubectl v1.37.1, Traefik v3.7.13, curl 8.5.0) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, ค่า sha256, จำนวนครั้งที่แต่ละ Pod ตอบ, จำนวน error ในการทดลองแบบเปราะ และจำนวนออเดอร์ ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** ให้ยึดผลจากเครื่องตัวเองเสมอ เวลาใน log ของ Traefik เป็น UTC (ช้ากว่าเวลาไทย 7 ชั่วโมง)

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox/Safari บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker`, `openssl` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container (🖥️) และการเปิด browser (🌐) ที่ `http://shop.localhost:30080`, `https://shop.localhost:30081`, `https://admin.localhost:30081` และ dashboard `http://localhost:30082/dashboard/`

### กติกาของ LAB บทนี้

- LAB 0–9 และ LAB เสริมทำในโฟลเดอร์ **`/workspace/012_kubernetes_ingress/02_LAB`** (คำสั่งอ้างไฟล์แบบ `lab02-first/10-apps.yaml`) LAB 7 เข้า `lab07-tls` ชั่วคราวแล้วกลับ และ LAB 10 ทำใน **`02_LAB/som-shop-v8`**
- **Traefik ที่ติดตั้งใน LAB 1 ใช้ต่อจนจบบท** (namespace `traefik`) LAB 2–9 ใช้ namespace **`ingress-demo`** ซึ่งต้อง **ลบทิ้งท้าย LAB 9 ก่อนเริ่ม LAB 10** เพราะป้าย `shop` ของ `ingress-demo` ใช้ชื่อ `shop.localhost` ซ้ำกับร้าน
- ทำ LAB **ตามลำดับ** ป้าย `shop` ถูกแก้ทับต่อกันตั้งแต่ LAB 2 ถึง LAB 8 และ Secret ของ LAB 7–8 ใช้ต่อกัน
- **NodePort 30080–30082 เป็นของ Traefik ตลอดบท** (30080 = HTTP, 30081 = HTTPS, 30082 = dashboard) Service อื่นจองพอร์ตเหล่านี้ไม่ได้
- รหัสผ่านทุกตัวในบทนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง: รหัส SSH `passwd`, รหัสฐานข้อมูลของบทที่ 11 `meow1234` (หรือ `purr5678` ถ้าเปลี่ยนรหัสในบทที่ 11 แล้ว — บทนี้ไม่แตะ Secret `som-db-secret`), บัตรหลังร้าน `som` / `meow-admin-123`
- ไฟล์ `tls.key`/`tls.crt` ที่สร้างใน LAB 7 และ LAB 10 **ห้าม commit ลง git** (`.gitignore` ของบทกัน `*.key`, `*.crt` ไว้แล้ว) dashboard ของ Traefik เปิดแบบไม่มีรหัส (`--api.insecure=true`) **ใช้เฉพาะใน LAB**
- image `traefik:v3.7.13`, `traefik/whoami:v1.11.0` และ `nginxinc/nginx-unprivileged:1.27-alpine` **Node ดึงจาก Docker Hub เองตอนใช้** ส่วน `som-shop-web:1.5`/`1.6` และ `postgres:17.11-alpine` ต้องโหลดเข้า Node ใน LAB 0 ไฟล์ CRD ของ Traefik มีสำเนาในโฟลเดอร์บทแล้ว แต่ LAB เสริมต้องดาวน์โหลด CRD ของ Gateway API จาก GitHub (ต้องมีอินเทอร์เน็ต)
- หลัง `scale`, `rollout` หรือ `apply` ป้ายใหม่ **ให้รอ 2–3 วินาที** ก่อนยิงทดสอบ (คำสั่งในเอกสารใส่ `sleep` ไว้แล้ว) Traefik ต้องเห็น EndpointSlice/ป้ายใหม่ก่อน

### Traefik แทน ingress-nginx และชื่อ `*.localhost`

**ทำไมใช้ Traefik:** ingress-nginx (`kubernetes/ingress-nginx`) ซึ่งเป็น controller ที่ตำราส่วนใหญ่ใช้ **ประกาศหยุดดูแลเมื่อ 11 พ.ย. 2025** ([Kubernetes blog](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)) Steering Committee ย้ำให้ย้ายทันที ([29 ม.ค. 2026](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/)) และ **repo ถูก archive เมื่อ 24 มี.ค. 2026** ([GitHub](https://github.com/kubernetes/ingress-nginx)) ไม่มี release หรือแพตช์ความปลอดภัยอีก เวอร์ชันสุดท้าย v1.15.1 รองรับถึง Kubernetes 1.35 ขณะที่คลัสเตอร์ของเราเป็น v1.37 คำแนะนำทางการคือย้ายไป Gateway API หรือ controller ตัวอื่น ([Before You Migrate](https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/), [Ingress2Gateway 1.0](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/)) บทนี้เลือก **Traefik v3.7.13** ([releases](https://github.com/traefik/traefik/releases), ออก 4 ก.ย. 2026) เพราะยังดูแลอยู่ ติดตั้งด้วย YAML ไฟล์เดียวโดยไม่ต้องใช้ Helm image ทางการดึงได้ตรง ใช้ป้าย Ingress มาตรฐาน ([Kubernetes Ingress provider](https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-ingress/)) อ่าน Secret `kubernetes.io/basic-auth` ได้ตรงและรองรับ Gateway API ([Gateway API provider](https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-gateway/)) รายละเอียดดูทฤษฎีหัวข้อ 5 **ส่วนมาตรฐานที่ฝึกใน LAB 2–7 ใช้กับ controller ใดก็ได้** ส่วนเฉพาะ Traefik (flag ของ controller และ Middleware ใน LAB 5, 7, 8) จะติดป้ายไว้

**ชื่อ `*.localhost`:** บทนี้เปิดร้านด้วยชื่อ `shop.localhost`, `admin.localhost` (และ `paths.localhost`, `other.localhost` ใน LAB ย่อย) โดย **ไม่แก้ไฟล์ hosts** เพราะ curl และ Chromium แปลงชื่อที่ลงท้ายด้วย `.localhost` เป็น loopback เอง

| ทดสอบแล้ว | ผล |
|---|---|
| curl 8.5.0 ใน k8s-lab | แปลงเอง (`Connected to shop.localhost (127.0.0.1) port 30080`) |
| Chromium 153 **บน Linux** | แปลงเอง เปิดร้านได้ครบทุกฉากของ LAB 10 |
| `getent hosts` (resolver ของระบบ) | หาไม่เจอ (`getent rc=2`) |
| **Chrome/Edge บน Windows/macOS, Firefox, Safari** | **ยังไม่ได้ทดสอบ** — ให้นักศึกษาลองเอง |

ถ้า browser หรือโปรแกรมของนักศึกษาเปิด `http://shop.localhost:30080` ไม่ได้ (เช่น `DNS_PROBE_FINISHED_NXDOMAIN` หรือ "server not found") ใช้ทางสำรอง

1. **curl ใน k8s-lab** ใช้ได้เสมอ (ทุก LAB ทดสอบด้วย curl ได้ครบ) ถ้าโปรแกรมไม่แปลงชื่อเอง ใช้ `curl --resolve shop.localhost:30081:127.0.0.1 https://shop.localhost:30081/` (HTTP ใช้ `-H 'Host: shop.localhost'` ได้ด้วย)
2. **แก้ไฟล์ hosts** บนเครื่องนักศึกษา เพิ่มบรรทัด `127.0.0.1 shop.localhost admin.localhost` ใน `C:\Windows\System32\drivers\etc\hosts` (Windows เปิด Notepad แบบ Run as administrator) หรือ `/etc/hosts` (macOS/Linux ใช้ `sudo`) แล้วลบออกเมื่อจบบท

> **http://localhost:30080 (ไม่มีชื่อ) ได้ 404 เป็นเรื่องปกติของบทนี้** ประตู 30080 เป็นของ Traefik ซึ่งเลือกปลายทางตามชื่อ ไม่มีป้ายใดรับชื่อ `localhost` บนพอร์ต HTTP จึงตอบ `404 page not found` ต้องเปิดด้วย `http://shop.localhost:30080` ส่วนหน้า dashboard เปิดที่ `http://localhost:30082/dashboard/` ได้ตรง

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์ คืนพอร์ต และ image](#lab-0-เตรียมคลัสเตอร์-คืนพอร์ต-และ-image) | 15–20 นาที | ⭐ |
| 1 | [ติดตั้ง Traefik และ IngressClass](#lab-1-ติดตั้ง-traefik-และ-ingressclass) | 15 นาที | ⭐⭐ |
| 2 | [Ingress แผ่นแรก](#lab-2-ingress-แผ่นแรก) | 15 นาที | ⭐⭐ |
| 3 | [ชื่อเดียว หลายทางเดิน (path fan-out)](#lab-3-ชื่อเดียว-หลายทางเดิน-path-fan-out) | 10 นาที | ⭐⭐ |
| 4 | [หลายชื่อ ประตูเดียว (host-based)](#lab-4-หลายชื่อ-ประตูเดียว-host-based) | 10 นาที | ⭐⭐ |
| 5 | [pathType และ strictPrefixMatching](#lab-5-pathtype-และ-strictprefixmatching) | 15 นาที | ⭐⭐⭐ |
| 6 | [ทำให้พังแล้ว debug](#lab-6-ทำให้พังแล้ว-debug) | 20 นาที | ⭐⭐⭐ |
| 7 | [TLS ที่ Ingress](#lab-7-tls-ที่-ingress) | 20 นาที | ⭐⭐⭐ |
| 8 | [Middleware: redirect, basicAuth, stripPrefix](#lab-8-middleware-redirect-basicauth-stripprefix) | 20 นาที | ⭐⭐⭐⭐ |
| 9 | [Rolling update ผ่าน Ingress](#lab-9-rolling-update-ผ่าน-ingress) | 15 นาที | ⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน](#lab-10-lab-สุดท้าย-ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน) | 45–60 นาที | ⭐⭐⭐⭐⭐ |
| เสริม | [ลองชิม Gateway API](#lab-เสริม-ลองชิม-gateway-api) | 15 นาที | ⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3.5–4 ชั่วโมง (รวมช่วง build image ใน LAB 0) ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านหัวข้อทฤษฎีที่เกี่ยวข้อง: LAB 0 → หัวข้อ 1, 2 และ 15.2, LAB 1 → หัวข้อ 4–6 และ 15, LAB 2 → หัวข้อ 3, 7 และ 8.2–8.3, LAB 3 → หัวข้อ 9, LAB 4 → หัวข้อ 6.2 และ 8.1, LAB 5 → หัวข้อ 10, LAB 6 → หัวข้อ 6.3, 7.2, 11 และ 16, LAB 7 → หัวข้อ 12, LAB 8 → หัวข้อ 13–14, LAB 9 → หัวข้อ 17, LAB 10 → หัวข้อ 7.3, 12–14 และ 20, LAB เสริม → หัวข้อ 18–19

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมและคืนพอร์ต](#fig-1) | 20 | [LAB 9 เปรียบเทียบแบบเปราะ](#fig-20) |
| 2 | [LAB 1 ติดตั้ง Traefik](#fig-2) | 21 | [LAB 10 ภาพรวม som-shop-v8](#fig-21) |
| 3 | [ผล LAB 1](#fig-3) | 22 | [ก่อนและหลังย้ายประตู](#fig-22) |
| 4 | [LAB 1 ลองผิด พอร์ตชน](#fig-4) | 23 | [ขั้น A ย้ายประตู](#fig-23) |
| 5 | [LAB 2 Ingress แผ่นแรก](#fig-5) | 24 | [ขั้น B ใบรับรองใหม่](#fig-24) |
| 6 | [ผล LAB 2](#fig-6) | 25 | [ขั้น C หลังร้านและป้าย](#fig-25) |
| 7 | [LAB 3 path fan-out](#fig-7) | 26 | [ขั้น D redirect และ browser](#fig-26) |
| 8 | [ผล LAB 3](#fig-8) | 27 | [ภาพหน้าจอจริง หน้าเตือนใบรับรอง self-signed](#fig-27) |
| 9 | [LAB 4 host-based](#fig-9) | 28 | [ภาพหน้าจอจริง หน้าร้านผ่าน Ingress HTTPS](#fig-28) |
| 10 | [LAB 5 pathType](#fig-10) | 29 | [ภาพหน้าจอจริง หลังร้าน 401 เมื่อไม่ login](#fig-29) |
| 11 | [ผล LAB 5 ตาราง pathType](#fig-11) | 30 | [ภาพหน้าจอจริง หลังร้านหลัง login](#fig-30) |
| 12 | [LAB 6 ทำให้พังทีละแบบ](#fig-12) | 31 | [ภาพหน้าจอจริง ชื่อที่ไม่มีป้าย 404](#fig-31) |
| 13 | [ผล LAB 6 อาการพัง](#fig-13) | 32 | [ภาพหน้าจอจริง Traefik dashboard](#fig-32) |
| 14 | [ผล LAB 6 defaultBackend](#fig-14) | 33 | [ขั้น E rolling update ผ่าน Ingress](#fig-33) |
| 15 | [LAB 7 TLS](#fig-15) | 34 | [ตรวจรับร้าน](#fig-34) |
| 16 | [ผล LAB 7](#fig-16) | 35 | [ปิดบท ปัญหาที่ยังเหลือ](#fig-35) |
| 17 | [LAB 8 Middleware](#fig-17) | 36 | [LAB เสริม Gateway API](#fig-36) |
| 18 | [ผล LAB 8](#fig-18) | 37 | [ผล LAB เสริม](#fig-37) |
| 19 | [LAB 9 rolling update](#fig-19) |  |  |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── .gitignore                         ← กัน *.key, *.crt ที่สร้างใน LAB 7 ไม่ให้เข้า git
├── images/                            ← ภาพประกอบ 01–31 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของ LAB 10 จำนวน 6 ภาพ
├── ingress-controller/                ← LAB 1 พนักงานต้อนรับ Traefik v3.7.13
│   ├── traefik-crds-v3.7.13.yml       (CRD ทางการ 10 ตัว สำเนาจาก tag v3.7.13 ไม่แก้ — apply ก่อนเสมอ)
│   └── 00-traefik.yaml                (Namespace, ServiceAccount, ClusterRole/Binding, Deployment, Service NodePort 30080/30081/30082, IngressClass default)
├── lab02-first/{10-apps.yaml,20-ingress.yaml}      (แอป menu/api/admin = whoami ใน ns ingress-demo + ป้ายแผ่นแรก)
├── lab03-fanout/ingress.yaml                        (ป้าย shop แยก / /api /admin)
├── lab04-hosts/ingress.yaml                         (ป้าย backoffice admin.localhost ไม่ใส่ class)
├── lab05-pathtype/{ingress.yaml,try-paths.sh}       (ป้าย paths.localhost + สคริปต์ยิง 15 path)
├── lab06-debug/{wrongclass.yaml,typo.yaml,lost.yaml} (class ผิด, Service/port ผิด, defaultBackend)
├── lab07-tls/ingress-tls.yaml                       (ป้าย shop + backoffice พร้อม spec.tls)
├── lab08-middleware/{redirect.yaml,redirect-noport.yaml,admin-auth.yaml,strip.yaml}  (Middleware ของ Traefik)
├── lab09-rolling/{loop.sh,menu-v2.yaml,menu-fragile.yaml}  (ยิง HTTPS วน + menu รุ่นใหม่ + แบบเปราะ)
├── labx-gateway/{gateway-rbac.yml,60-gateway.yaml}  (LAB เสริม Gateway API)
└── som-shop-v8/                       ← LAB 10 ร้านน้องส้มหน้าร้านเดียวด้วยชื่อโดเมน
    ├── app/                           ← แอป Next.js + Dockerfile (สำเนาจากบทที่ 11 ไม่แก้โค้ด, build เป็น som-shop-web:1.5 และ 1.6)
    ├── k8s/
    │   ├── 00-namespace.yaml, 10-db.yaml   (เหมือนบทที่ 11)
    │   ├── 15-config.yaml             (ป้ายร้านบทที่ 12: "⚓ ท่าเรือ Kubernetes · Ingress")
    │   ├── 20-web.yaml                (Service som-web เป็น ClusterIP แล้ว)
    │   ├── 40-admin.yaml              (หลังร้าน som-admin: nginx-unprivileged + /stats)
    │   └── 50-ingress.yaml            (Middleware redirect-https, admin-auth + Ingress som-shop, som-admin)
    ├── .gitignore                     ← กัน secret.yaml, *.secret.yaml, *.key, *.crt
    └── hit.sh                         ← ยิง HTTPS ผ่าน Ingress แล้วนับว่าไปตก Pod/เวอร์ชันไหน
```

> **ไม่มี `30-https.yaml` ใน `som-shop-v8/k8s/` โดยตั้งใจ** — TLS ย้ายจาก nginx ของบทที่ 11 มาที่ประตู Ingress แล้ว ห้าม `kubectl apply -f` โฟลเดอร์ `k8s/` ของบทที่ 11 ทับ เพราะ `30-https.yaml` จะกลับมาจอง NodePort 30082 ซึ่งชนกับ dashboard ของ Traefik

### แอปร้านใช้โค้ดเดิม

`som-shop-v8/app/` เป็นสำเนาแอปจากบทที่ 11 **ไม่แก้โค้ดแม้แต่บรรทัดเดียว** เพราะแอปไม่ต้องรู้เรื่อง TLS หรือชื่อโดเมนเลย (TLS ถูกถอดที่ประตู) สิ่งที่เปลี่ยนบนหน้าเว็บมาจาก ConfigMap `k8s/15-config.yaml` (หัวเว็บ `⚓ ท่าเรือ Kubernetes · Ingress` และ footer `Next.js + PostgreSQL · Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost`) ส่วน `som-shop-web:1.6` คือโค้ดชุดเดียวกัน build ด้วย `--build-arg APP_VERSION=1.6` ใช้ทดสอบการเปลี่ยนรุ่นผ่าน Ingress ใน LAB 10

---

## LAB 0: เตรียมคลัสเตอร์ คืนพอร์ต และ image

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมและคืนพอร์ต" width="900"><br>
  <em><b>รูปที่ 1</b> LAB 0: ตรวจ 3 Node Ready, ดูว่าใครถือ NodePort 30080–30082 (ร้านบท 011) แล้วลบ Service som-web/som-https ชั่วคราว, โหลด postgres + build som-shop-web:1.5/1.6 ไว้ใช้ LAB 10</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` ตรวจคลัสเตอร์ (ใช้ต่อจากบทที่ 11 หรือสร้างใหม่) **คืน NodePort 30080–30082 ที่ร้านของบทที่ 11 จองไว้** โดยเก็บฐานข้อมูลและออเดอร์ไว้ และเตรียม image `postgres:17.11-alpine`, `som-shop-web:1.5` และ `som-shop-web:1.6` ให้ทุก Node สำหรับ LAB 10

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md)–[11](../../011_kubernetes_secret/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `012_kubernetes_ingress` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `012_kubernetes_ingress` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 012_kubernetes_ingress k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ บทนี้มีแอปร้าน (`02_LAB/som-shop-v8/app`) และ manifest ทุกไฟล์ของตัวเอง จึง **ไม่ต้องมีโฟลเดอร์ของบทก่อนใน container**

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (ค่าตัวอย่างเพื่อการเรียน พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และตรวจคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/012_kubernetes_ingress/02_LAB
ls; ls som-shop-v8 ingress-controller
kubectl get nodes
```

```text
images
ingress-controller
lab02-first
lab03-fanout
lab04-hosts
lab05-pathtype
lab06-debug
lab07-tls
lab08-middleware
lab09-rolling
labx-gateway
som-shop-v8
ingress-controller:
00-traefik.yaml
traefik-crds-v3.7.13.yml

som-shop-v8:
app
hit.sh
k8s
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   5m27s   v1.37.0
lab-worker          Ready    <none>          5m17s   v1.37.0
lab-worker2         Ready    <none>          5m17s   v1.37.0
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 11 ยังอยู่) | **ใช้ต่อได้เลย** ไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `k8s-up` (การทดลองใช้เวลาราว 50 วินาที) แล้วข้ามขั้นที่ 4–5 ไปขั้นที่ 6 (คลัสเตอร์ใหม่ไม่มีร้านเดิม image ต้องโหลดใหม่ทั้งหมด) |

### ขั้นที่ 4: ดูว่าใครถือ NodePort 30080–30082

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
kubectl get ns som-shop; kubectl get svc -A | grep 3008 || echo "ไม่มี NodePort 3008x ค้าง"
```

ผลจริงบนคลัสเตอร์ที่มีร้านจากท้ายบทที่ 11

```text
NAME       STATUS   AGE
som-shop   Active   36s
som-shop      som-https    NodePort    10.96.194.61    <none>        443:30082/TCP            35s
som-shop      som-web      NodePort    10.96.223.183   <none>        80:30080/TCP             35s
```

ร้านของบทที่ 11 จอง `30080` (หน้าร้าน) และ `30082` (HTTPS ผ่าน nginx) อยู่ ถ้าติดตั้ง Traefik ทับตอนนี้จะได้ `provided port is already allocated` (ดู LAB 1 ลองผิด) **คลัสเตอร์ใหม่จะเห็นแค่** `Error from server (NotFound): namespaces "som-shop" not found` และ `ไม่มี NodePort 3008x ค้าง` ถ้าเห็น Service อื่นที่ถือ `3008x` (เช่น `ngx-tls` NodePort 30081 จาก LAB 4 บทที่ 11 ที่ลืมลบ) ให้ลบด้วย `kubectl delete svc <ชื่อ>` ใน namespace ของมัน

**ลองดู (ไม่จำเป็น):** ตรวจล่วงหน้าด้วย dry-run ฝั่ง server ได้ไหม

```bash
kubectl apply --dry-run=server -f ingress-controller/00-traefik.yaml
```

```text
namespace/traefik created (server dry run)
clusterrole.rbac.authorization.k8s.io/traefik created (server dry run)
clusterrolebinding.rbac.authorization.k8s.io/traefik created (server dry run)
ingressclass.networking.k8s.io/traefik created (server dry run)
Error from server (NotFound): error when creating "ingress-controller/00-traefik.yaml": namespaces "traefik" not found
Error from server (NotFound): error when creating "ingress-controller/00-traefik.yaml": namespaces "traefik" not found
Error from server (NotFound): error when creating "ingress-controller/00-traefik.yaml": namespaces "traefik" not found
```

dry-run ไม่ได้สร้าง namespace `traefik` จริง object ที่อยู่ใน namespace นั้น (ServiceAccount, Deployment, Service) จึงตรวจไม่ได้ และ **ไม่เห็นปัญหาพอร์ตชน** วิธีที่ใช้ได้คือดู `kubectl get svc -A | grep 3008` ตามข้างบน

### ขั้นที่ 5: คืนพอร์ต — ลบเฉพาะ Service ของร้านบทที่ 11

🐧 **ใน SSH session ของ k8s-lab** (ข้ามได้ถ้าไม่มี namespace `som-shop`)

```bash
kubectl -n som-shop delete svc som-web som-https
kubectl get svc -A | grep 3008 || echo "ไม่มี NodePort 3008x ค้าง"
kubectl -n som-shop get deploy,sts,pvc
```

```text
service "som-web" deleted from som-shop namespace
service "som-https" deleted from som-shop namespace
ไม่มี NodePort 3008x ค้าง
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-https   1/1     1            1           35s
deployment.apps/som-web     3/3     3            3           35s

NAME                      READY   AGE
statefulset.apps/som-db   1/1     35s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-025e80a5-8f0a-47c6-8b9e-d82e1c94ada8   1Gi        RWO            standard       <unset>                 35s
```

ลบแค่ **Service** (ประตู) ส่วน Deployment `som-web`, StatefulSet `som-db`, PVC `data-som-db-0` และ Secret ทั้งหมดยังอยู่ ออเดอร์จึงไม่หาย ช่วงนี้ร้านเปิดจากภายนอกไม่ได้ชั่วคราว จนกว่า LAB 10 จะติดป้าย Ingress ให้ (`som-https` จะถูกลบใน LAB 10 ขั้น A)

### ขั้นที่ 6: เตรียม image ให้ทุก Node

ตรวจก่อนว่า Node มี image อะไรอยู่แล้ว

```bash
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

ผลจริงบนคลัสเตอร์ที่ใช้ต่อจากบทที่ 11 (มี postgres และ 1.5 อยู่แล้ว)

```text
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  22187f5886568       76.7MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  22187f5886568       76.7MB
```

**postgres** (เฉพาะคลัสเตอร์ใหม่ หรือถ้าไม่เห็น `postgres 17.11-alpine` บนทั้งสอง worker) เป็น image หลาย platform จึงใช้ `docker save --platform` + `kind load image-archive`

```bash
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab)
```

```text
docker.io/library/postgres:17.11-alpine

real	0m16.640s
user	0m0.235s
sys	0m0.900s
```

**som-shop-web:1.6** (ทุกคนต้อง build) จากแอปในโฟลเดอร์ `som-shop-v8/app` แล้ว `kind load` ให้ทุก Node

```bash
cd som-shop-v8
time (docker build -q -t som-shop-web:1.6 --build-arg APP_VERSION=1.6 app && kind load docker-image som-shop-web:1.6 --name lab)
```

```text
sha256:66e3c558d56212219b08c2efa3e9b390615bf79bb395d9bb09fd474b6752b042
Image: "som-shop-web:1.6" with ID "sha256:66e3c558d56212219b08c2efa3e9b390615bf79bb395d9bb09fd474b6752b042" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.6" with ID "sha256:66e3c558d56212219b08c2efa3e9b390615bf79bb395d9bb09fd474b6752b042" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.6" with ID "sha256:66e3c558d56212219b08c2efa3e9b390615bf79bb395d9bb09fd474b6752b042" not yet present on node "lab-control-plane", loading...

real	0m4.642s
user	0m0.342s
sys	0m0.795s
```

**som-shop-web:1.5** (เฉพาะคลัสเตอร์ใหม่ที่ไม่มี 1.5) build จากโค้ดชุดเดียวกัน

```bash
time (docker build -q -t som-shop-web:1.5 --build-arg APP_VERSION=1.5 app && kind load docker-image som-shop-web:1.5 --name lab)
```

ผลจริงของการ build ครั้งแรก (ไม่มี cache) ใช้ราว 34 วินาทีในเครื่องทดลอง (`real 0m33.705s`) เครื่องนักศึกษาอาจนานกว่านี้หลายเท่า การทดลองนี้ build 1.6 ต่อจาก 1.5 จึงใช้ cache และเร็วมาก (4.6 วินาที) ค่า sha256 จะต่างจากตัวอย่าง

> **คลัสเตอร์ที่ใช้ต่อจากบทที่ 11 ไม่ต้อง build 1.5 ซ้ำ** ถ้า build ซ้ำจะได้ image ID ใหม่ (Pod เดิมไม่กระทบ แต่สับสนได้) ไฟล์ `/root/postgres.tar` ลบได้หลัง load เสร็จ (`rm -f /root/postgres.tar`)

ตรวจผลและยืนยันว่า image 1.6 จำเลขเวอร์ชันถูก แล้วกลับไปโฟลเดอร์ `02_LAB`

```bash
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
docker run --rm som-shop-web:1.6 node -e 'console.log(process.env.APP_VERSION)'
cd ..
```

```text
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  22187f5886568       76.7MB
docker.io/library/som-shop-web                  1.6                  f75f3713df65e       76.7MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  22187f5886568       76.7MB
docker.io/library/som-shop-web                  1.6                  f75f3713df65e       76.7MB
1.6
```

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node `Ready` (v1.37.0) และ **ไม่มี Service ใดถือ NodePort 30080–30082** แล้ว
- ร้านบทที่ 11 ยังมี Deployment, StatefulSet และ PVC ครบ (เปิดจากภายนอกไม่ได้ชั่วคราว)
- `postgres:17.11-alpine`, `som-shop-web:1.5` และ `som-shop-web:1.6` อยู่บนทั้งสอง worker

**คำถามชวนคิด**

1. ทำไมขั้นที่ 5 ลบแค่ Service ไม่ลบ namespace `som-shop` ทั้งก้อน ถ้าลบ namespace จะเสียอะไร
2. `kubectl apply --dry-run=server` ตรวจปัญหาพอร์ตชนไม่ได้เพราะอะไร มีวิธีอื่นที่ตรวจก่อนติดตั้งได้ไหม

---

## LAB 1: ติดตั้ง Traefik และ IngressClass

<p align="center" id="fig-2">
  <img src="images/02-lab1-open.png" alt="รูปที่ 2 LAB 1 ติดตั้ง Traefik" width="900"><br>
  <em><b>รูปที่ 2</b> LAB 1 เปิด: ติดตั้งพนักงานต้อนรับ — CRD (v3.7.13) → 00-traefik.yaml (RBAC, Deployment, Service NodePort, IngressClass default)</em>
</p>

**เป้าหมาย:** ติดตั้ง Ingress controller Traefik v3.7.13 ตามลำดับที่ถูก (CRD ก่อน controller) ตรวจว่า Pod พร้อม IngressClass เป็น default และประตู 30080/30081/30082 ตอบแล้วแม้ยังไม่มีป้าย

**ไฟล์:** `ingress-controller/traefik-crds-v3.7.13.yml`, `ingress-controller/00-traefik.yaml` ทำในโฟลเดอร์ `02_LAB`

### ขั้นที่ 1: ดูไฟล์ที่จะติดตั้ง

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/012_kubernetes_ingress/02_LAB
ls -la ingress-controller; grep -c '^kind: CustomResourceDefinition' ingress-controller/traefik-crds-v3.7.13.yml
```

```text
total 260
drwxr-xr-x  2 root root   4096 Oct  5 20:06 .
drwxr-xr-x 14 root root   4096 Oct  5 20:08 ..
-rw-r--r--  1 root root   7177 Oct  5 20:06 00-traefik.yaml
-rw-r--r--  1 root root 248801 Oct  5 20:05 traefik-crds-v3.7.13.yml
10
```

`traefik-crds-v3.7.13.yml` คือสำเนาไฟล์ CRD ทางการจาก tag `v3.7.13` (`https://raw.githubusercontent.com/traefik/traefik/v3.7.13/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml`) ไม่ได้แก้ไข มี CRD 10 ตัว ให้เปิดอ่าน `00-traefik.yaml` ด้วย `less ingress-controller/00-traefik.yaml` จุดสำคัญคือ args ของ Deployment

| arg | ทำอะไร | ไม่ตั้งแล้วเป็นอย่างไร (ผลจริงในบทนี้) |
|---|---|---|
| `--entryPoints.web.address=:8000`, `websecure` `:8443`, `traefik` `:8080` | ประตูภายใน container (รันเป็น uid 65532 จึงใช้พอร์ตสูง) | – |
| `--entryPoints.websecure.http.tls=true` | router บนประตู HTTPS เป็น TLS | HTTPS ได้ `HTTP/2 404` ทั้งที่ใบรับรองถูก (LAB 7) |
| `--providers.kubernetesingress=true` | อ่านป้าย Ingress มาตรฐาน | – |
| `--providers.kubernetesingress.strictPrefixMatching=true` | Prefix ตรงทีละท่อนตามมาตรฐาน | `/apix` ไป api, `/docs` ได้ 404 (LAB 5) |
| `--providers.kubernetesingress.allowEmptyServices=true` | Service ไม่มี Pod Ready → 503 | router หายไป ได้ 404 แทน (ทฤษฎีหัวข้อ 11.2) |
| `--providers.kubernetesingress.ingressendpoint.hostname=localhost` | ค่าในคอลัมน์ ADDRESS | ADDRESS ว่าง แยกไม่ออกว่า controller รับป้ายไหม |
| `--providers.kubernetescrd=true` | อ่าน Middleware (CRD `traefik.io`) | Middleware ใช้ไม่ได้ |
| `--api.dashboard=true`, `--api.insecure=true` | dashboard ที่ 30082 แบบไม่มีรหัส | **เฉพาะ LAB** |
| `--ping=true`, `--accesslog=true` | `/ping` สำหรับ readinessProbe, สมุดเยี่ยมใน `kubectl logs` | – |

### ขั้นที่ 2: ติดตั้ง CRD ก่อน

```bash
time kubectl apply -f ingress-controller/traefik-crds-v3.7.13.yml
kubectl get crd | grep traefik.io
```

```text
customresourcedefinition.apiextensions.k8s.io/ingressroutes.traefik.io created
customresourcedefinition.apiextensions.k8s.io/ingressroutetcps.traefik.io created
customresourcedefinition.apiextensions.k8s.io/ingressrouteudps.traefik.io created
customresourcedefinition.apiextensions.k8s.io/middlewares.traefik.io created
customresourcedefinition.apiextensions.k8s.io/middlewaretcps.traefik.io created
customresourcedefinition.apiextensions.k8s.io/serverstransports.traefik.io created
customresourcedefinition.apiextensions.k8s.io/serverstransporttcps.traefik.io created
customresourcedefinition.apiextensions.k8s.io/tlsoptions.traefik.io created
customresourcedefinition.apiextensions.k8s.io/tlsstores.traefik.io created
customresourcedefinition.apiextensions.k8s.io/traefikservices.traefik.io created

real	0m0.179s
...
ingressroutes.traefik.io          Namespaced   v1alpha1(storage)   2026-10-05T13:12:44Z
...
middlewares.traefik.io            Namespaced   v1alpha1(storage)   2026-10-05T13:12:44Z
...
traefikservices.traefik.io        Namespaced   v1alpha1(storage)   2026-10-05T13:12:44Z
```

ไฟล์ CRD ขนาด 248 KB apply แบบธรรมดาผ่าน (ไม่ต้อง `--server-side`) บทนี้ใช้แค่ `middlewares.traefik.io` (LAB 8, 10) ที่เหลือมีไว้เพราะ Traefik watch ทุกตัว

### ขั้นที่ 3: ติดตั้ง controller

```bash
kubectl apply -f ingress-controller/00-traefik.yaml
time kubectl -n traefik rollout status deploy/traefik --timeout=180s
kubectl -n traefik get deploy,pod,svc -o wide
kubectl get ingressclass
```

```text
namespace/traefik created
serviceaccount/traefik created
clusterrole.rbac.authorization.k8s.io/traefik created
clusterrolebinding.rbac.authorization.k8s.io/traefik created
deployment.apps/traefik created
service/traefik created
ingressclass.networking.k8s.io/traefik created
Waiting for deployment "traefik" rollout to finish: 0 of 1 updated replicas are available...
deployment "traefik" successfully rolled out

real	0m3.743s
...
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES            SELECTOR
deployment.apps/traefik   1/1     1            1           4s    traefik      traefik:v3.7.13   app=traefik

NAME                           READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
pod/traefik-79d6dbf9fb-r6xs5   1/1     Running   0          4s    10.244.2.8   lab-worker2   <none>           <none>

NAME              TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                                     AGE   SELECTOR
service/traefik   NodePort   10.96.154.128   <none>        80:30080/TCP,443:30081/TCP,8080:30082/TCP   4s    app=traefik
NAME                CONTROLLER                      PARAMETERS   AGE
traefik (default)   traefik.io/ingress-controller   <none>       3s
```

<p align="center" id="fig-3">
  <img src="images/03-lab1-result.png" alt="รูปที่ 3 ผล LAB 1" width="900"><br>
  <em><b>รูปที่ 3</b> ผล LAB 1: traefik Running (ดึง image จาก Docker Hub ได้ตรง ~7 วิ), IngressClass traefik (default), curl localhost:30080 → 404 page not found เพราะยังไม่มีป้าย, dashboard ที่ 30082</em>
</p>

ดูว่า Node ดึง image เองได้และ log ไม่มี error

```bash
kubectl -n traefik describe pod -l app=traefik | grep -E 'Pulled|Image:'
kubectl -n traefik logs deploy/traefik | head -20
kubectl -n traefik logs deploy/traefik | grep -cE 'ERR|Failed to watch'
```

```text
    Image:         traefik:v3.7.13
  Normal   Pulled     3s    kubelet            spec.containers{traefik}: Container image "traefik:v3.7.13" already present on machine and can be accessed by the pod
...
2026-10-05T13:12:45Z WRN Traefik can reject some encoded characters in the request path. ...
2026-10-05T13:12:45Z INF Traefik version 3.7.13 built on 2026-09-04T12:31:42Z version=3.7.13
...
2026-10-05T13:12:45Z WRN aliasHeadersStrategy is not configured: ... entryPointName=web
...
2026-10-05T13:12:45Z INF Starting provider *ingress.Provider
...
0
```

- รอบนี้ image อยู่บน Node แล้วจากการทดลองก่อนหน้า (`already present on machine`) **ครั้งแรกบนเครื่องนักศึกษาจะเห็น `Successfully pulled image "traefik:v3.7.13"`** (pre-check ใช้ 7.42 วินาที ขนาด 55 MB) **ไม่ต้อง `kind load`**
- `WRN ... encoded characters`, `WRN aliasHeadersStrategy is not configured` เป็นคำเตือนเชิงแนะนำของ Traefik v3.7 ไม่ใช่ error (log จริงมีสี ANSI)
- นับ `ERR`/`Failed to watch` ได้ `0` = ลำดับติดตั้งถูก

### ขั้นที่ 4: ประตูเปิดแล้ว แต่ยังไม่มีป้าย

```bash
curl -i localhost:30080
curl -sk -o /dev/null -w '%{http_code}\n' https://localhost:30081/
curl -s -o /dev/null -w '%{http_code}\n' localhost:30082/dashboard/; curl -s localhost:30082/api/version; echo
curl -s localhost:30082/api/entrypoints | python3 -c 'import json,sys; [print(e["name"], e["address"]) for e in json.load(sys.stdin)]'
```

```text
HTTP/1.1 404 Not Found
Content-Type: text/plain; charset=utf-8
X-Content-Type-Options: nosniff
Date: Mon, 05 Oct 2026 13:12:48 GMT
Content-Length: 19

404 page not found
404
200
{"Version":"3.7.13","Codename":"langres","startDate":"2026-10-05T13:12:45.562281383Z"}
traefik :8080
web :8000
websecure :8443
```

`404 page not found` มาจาก **Traefik** (ยังไม่มีป้ายใดรับคำขอ) ไม่ใช่จากร้าน ประตู HTTPS ก็ตอบ 404 เช่นกัน dashboard ตอบ 200 และ entrypoint ตรงกับ args (web :8000 = NodePort 30080, websecure :8443 = 30081, traefik :8080 = 30082)

🌐 **browser บนเครื่องนักศึกษา** เปิด `http://localhost:30082/dashboard/` จะเห็นหน้า Dashboard ของ Traefik Proxy 3.7.13 (ภาพหน้าจอจริงของ dashboard หลังมีร้านแล้วอยู่ใน LAB 10 ขั้น D)

### ขั้นที่ 5: ลองผิด — Service อื่นขอพอร์ตที่ Traefik ถือ

```bash
kubectl create service nodeport probe --tcp=80:80 --node-port=30080
kubectl get svc -A | grep 3008
```

```text
error: failed to create NodePort service: Service "probe" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated
traefik       traefik      NodePort    10.96.154.128   <none>        80:30080/TCP,443:30081/TCP,8080:30082/TCP   5s
```

Service `probe` ไม่ถูกสร้าง (ไม่ต้องลบ) ข้อความเดียวกันนี้คือสิ่งที่เกิดเมื่อติดตั้ง Traefik ทับร้านบทที่ 11 ที่ยังถือพอร์ต

<p align="center" id="fig-4">
  <img src="images/04-lab1-port-conflict.png" alt="รูปที่ 4 LAB 1 ลองผิด พอร์ตชน" width="900"><br>
  <em><b>รูปที่ 4</b> LAB 1 ลองผิด: ถ้าข้าม LAB 0 แล้ว Service ร้านเดิมยังถือ 30080 → The Service &quot;traefik&quot; is invalid: ... provided port is already allocated</em>
</p>

### ถ้าพลาด: ข้าม LAB 0 หรือลืม CRD (ผลจริงจากการทดลองแยก ไม่ต้องทำตาม)

**ข้าม LAB 0** (ร้านบทที่ 11 ยังถือ 30080/30082) แล้ว `kubectl apply -f ingress-controller/00-traefik.yaml`

```text
namespace/traefik created
serviceaccount/traefik created
clusterrole.rbac.authorization.k8s.io/traefik created
clusterrolebinding.rbac.authorization.k8s.io/traefik created
deployment.apps/traefik created
ingressclass.networking.k8s.io/traefik created
The Service "traefik" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated
```

ทุกอย่างถูกสร้างยกเว้น Service Deployment รันได้แต่ไม่มีประตู แก้ด้วย `kubectl -n som-shop delete svc som-web som-https` แล้ว apply ไฟล์เดิมซ้ำ จะได้ `service/traefik created` ส่วนอื่น `unchanged`

**ลืม CRD** (apply `00-traefik.yaml` ก่อน CRD) log ของ Traefik มี error ซ้ำ ๆ (ผลจริง 40 บรรทัดใน 15 วินาที)

```text
E1005 13:11:32.584200       1 reflector.go:227] "Failed to watch" err="failed to list *v1alpha1.MiddlewareTCP: the server could not find the requested resource (get middlewaretcps.traefik.io)" logger="UnhandledError" ...
E1005 13:11:32.584298       1 reflector.go:227] "Failed to watch" err="failed to list *v1alpha1.Middleware: the server could not find the requested resource (get middlewares.traefik.io)" logger="UnhandledError" ...
```

แก้ด้วยการ apply CRD แล้ว restart controller

```bash
kubectl apply -f ingress-controller/traefik-crds-v3.7.13.yml
kubectl -n traefik rollout restart deploy/traefik && kubectl -n traefik rollout status deploy/traefik --timeout=90s
```

ผลจริง: หลัง apply CRD บรรทัดใหม่หยุดเพิ่ม (`Failed to watch ก่อน=41 หลัง 30 วิ=41`) และหลัง `rollout restart` นับ `Failed to watch|ERR` ได้ `0`

### สิ่งที่เห็น

- CRD 10 ตัวของ `traefik.io` → Traefik 1/1 Running (rollout ราว 4 วินาที) → IngressClass `traefik (default)` controller `traefik.io/ingress-controller`
- Service `traefik` NodePort `80:30080`, `443:30081`, `8080:30082` เป็นประตูเดียวของทั้งคลัสเตอร์ พอร์ตเหล่านี้ Service อื่นขอไม่ได้อีก
- ยังไม่มีป้าย: `localhost:30080` → `404 page not found` ของ Traefik, dashboard 200

**คำถามชวนคิด**

1. Traefik เป็น "Deployment + Service" ธรรมดา ถ้า Pod Traefik ตาย (เช่น Node ล่ม) ลูกค้าของทุกร้านจะเป็นอย่างไร งานจริงควรตั้ง `replicas` เท่าไร
2. ClusterRole ของ Traefik ให้สิทธิ์ `get/list/watch secrets` ทั้งคลัสเตอร์ เชื่อมโยงกับเหตุผลที่ไม่ควรใช้ controller ที่หยุดดูแลแล้วอย่างไร

---

## LAB 2: Ingress แผ่นแรก

<p align="center" id="fig-5">
  <img src="images/05-lab2-open.png" alt="รูปที่ 5 LAB 2 Ingress แผ่นแรก" width="900"><br>
  <em><b>รูปที่ 5</b> LAB 2 เปิด: Ingress แรก shop.localhost → Service menu (whoami) เปิดทั้ง curl และ browser http://shop.localhost:30080</em>
</p>

**เป้าหมาย:** สร้างแอปทดลอง 3 ตัว (menu/api/admin) ที่มีแค่ Service ClusterIP แล้วแขวนป้ายแผ่นแรก `shop.localhost → menu` ทดสอบด้วย `Host` header, ชื่อ `*.localhost`, `--resolve` และ browser ดู ADDRESS, describe และ access log

**ไฟล์:** `lab02-first/10-apps.yaml` (namespace `ingress-demo` + Deployment/Service `menu`, `api`, `admin` ทุกตัวเป็น `traefik/whoami:v1.11.0` 2 replicas มี readinessProbe + preStop), `lab02-first/20-ingress.yaml`

### ขั้นที่ 1: แอปทดลอง 3 ตัว

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
kubectl apply -f lab02-first/10-apps.yaml
time (for d in menu api admin; do kubectl -n ingress-demo rollout status deploy/$d --timeout=120s; done)
kubectl -n ingress-demo get deploy,svc
```

```text
namespace/ingress-demo created
deployment.apps/menu created
service/menu created
deployment.apps/api created
service/api created
deployment.apps/admin created
service/admin created
...
deployment "admin" successfully rolled out

real	0m8.958s
...
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/admin   2/2     2            2           9s
deployment.apps/api     2/2     2            2           9s
deployment.apps/menu    2/2     2            2           9s

NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/admin   ClusterIP   10.96.1.171     <none>        80/TCP    9s
service/api     ClusterIP   10.96.128.199   <none>        80/TCP    9s
service/menu    ClusterIP   10.96.228.179   <none>        80/TCP    9s
```

`traefik/whoami` (3 MB) ตอบกลับชื่อที่ตั้งด้วย `--name` (`Name: menu`) พร้อมบรรทัด `GET /path` และ header ทุกตัวที่ได้รับ จึงเห็นชัดว่าคำขอไปถึงใครและถูกแก้อะไรระหว่างทาง Service ทั้งสามเป็น **ClusterIP** (`port: 80` ชื่อ `http` → container 8080)

### ขั้นที่ 2: ก่อนมีป้าย และหลังแขวนป้าย

```bash
curl -s -H 'Host: shop.localhost' localhost:30080/
kubectl apply -f lab02-first/20-ingress.yaml
kubectl -n ingress-demo get ingress
sleep 2; curl -s -H 'Host: shop.localhost' localhost:30080/
```

```text
404 page not found
ingress.networking.k8s.io/shop created
NAME   CLASS     HOSTS            ADDRESS     PORTS   AGE
shop   traefik   shop.localhost   localhost   80      0s
Name: menu
Hostname: menu-5f588ffbdd-hmskt
IP: 127.0.0.1
IP: ::1
IP: 10.244.2.9
IP: fe80::b409:cdff:fedc:c207
RemoteAddr: 10.244.2.8:34654
GET / HTTP/1.1
Host: shop.localhost
User-Agent: curl/8.5.0
Accept: */*
Accept-Encoding: gzip
X-Forwarded-For: 172.19.0.2
X-Forwarded-Host: shop.localhost
X-Forwarded-Port: 80
X-Forwarded-Proto: http
X-Forwarded-Server: traefik-79d6dbf9fb-r6xs5
X-Real-Ip: 172.19.0.2
```

- ก่อนแขวนป้ายได้ 404 หลังแขวน **Traefik เห็นป้ายเองภายในวินาที** (ไม่ต้อง restart) แล้วพาไป menu
- `RemoteAddr: 10.244.2.8` คือ IP ของ Pod Traefik (LAB 1) — คำขอเดินทาง Traefik → Pod menu ตรง ๆ
- `X-Forwarded-Server` บอกชื่อ Pod Traefik ที่ส่งมา `X-Forwarded-For` คือที่อยู่ของลูกค้าตามที่ Traefik เห็น (บน kind เป็น IP ภายในของ Node)
- `X-Forwarded-Port: 80` เพราะ `Host` ไม่มีพอร์ต Traefik จึงถือว่าเป็นพอร์ตมาตรฐาน (ข้อนี้สำคัญใน LAB 10)

### ขั้นที่ 3: เรียกด้วยชื่อ `shop.localhost`

```bash
curl -s http://shop.localhost:30080/hello | grep -E 'Name|^GET|Host:|X-Forwarded'
curl -sv http://shop.localhost:30080/ 2>&1 | grep -E 'Trying|Connected|^> Host|^< HTTP'
curl -s localhost:30080/; curl -s -H 'Host: other.localhost' localhost:30080/
```

```text
Name: menu
GET /hello HTTP/1.1
Host: shop.localhost:30080
X-Forwarded-For: 172.19.0.2
X-Forwarded-Host: shop.localhost:30080
X-Forwarded-Port: 30080
X-Forwarded-Proto: http
X-Forwarded-Server: traefik-79d6dbf9fb-r6xs5
*   Trying [::1]:30080...
*   Trying 127.0.0.1:30080...
* Connected to shop.localhost (127.0.0.1) port 30080
> Host: shop.localhost:30080
< HTTP/1.1 200 OK
404 page not found
404 page not found
```

curl แปลง `shop.localhost` เป็น loopback เอง (ลอง `::1` ก่อนแล้วต่อ `127.0.0.1` สำเร็จ) และส่ง `Host: shop.localhost:30080` **มีพอร์ตต่อท้าย** Traefik ตัดพอร์ตออกก่อนเทียบกับ `host: shop.localhost` จึงตรง ไม่มี `Host` (เรียก `localhost`) หรือชื่ออื่นได้ 404

### ขั้นที่ 4: resolver ของระบบ และทางสำรอง

```bash
getent hosts shop.localhost; echo "getent rc=$?"
curl -s --resolve shop.localhost:30080:127.0.0.1 http://shop.localhost:30080/ | head -1
```

```text
getent rc=2
Name: menu
```

`getent` (resolver ของระบบ) หาชื่อไม่เจอ โปรแกรมที่ไม่แปลง `*.localhost` เองจึงต้องใช้ `--resolve` หรือแก้ไฟล์ hosts (ดู [Traefik แทน ingress-nginx และชื่อ `*.localhost`](#traefik-แทน-ingress-nginx-และชื่อ-localhost))

### ขั้นที่ 5: ADDRESS, describe และการกระจายโหลด

```bash
kubectl -n ingress-demo get ing shop -o jsonpath='{.status.loadBalancer.ingress}'; echo
kubectl -n ingress-demo describe ing shop
for i in 1 2 3 4 5 6; do curl -s http://shop.localhost:30080/ | grep Hostname; done | sort | uniq -c
kubectl -n traefik logs deploy/traefik --tail=3
```

```text
[{"hostname":"localhost"}]
Name:             shop
Labels:           <none>
Namespace:        ingress-demo
Address:          localhost
Ingress Class:    traefik
Default backend:  <default>
Rules:
  Host            Path  Backends
  ----            ----  --------
  shop.localhost
                  /   menu:80 (10.244.2.9:8080,10.244.1.4:8080)
Annotations:      <none>
Events:           <none>
      3 Hostname: menu-5f588ffbdd-hmskt
      3 Hostname: menu-5f588ffbdd-sbwk5
172.19.0.2 - - [05/Oct/2026:13:13:13 +0000] "GET / HTTP/1.1" 200 433 "-" "-" 15 "ingress-demo-shop-shop-localhost@kubernetes" "http://10.244.1.4:8080" 0ms
172.19.0.2 - - [05/Oct/2026:13:13:13 +0000] "GET / HTTP/1.1" 200 433 "-" "-" 16 "ingress-demo-shop-shop-localhost@kubernetes" "http://10.244.2.9:8080" 0ms
172.19.0.2 - - [05/Oct/2026:13:13:13 +0000] "GET / HTTP/1.1" 200 433 "-" "-" 17 "ingress-demo-shop-shop-localhost@kubernetes" "http://10.244.1.4:8080" 0ms
```

<p align="center" id="fig-6">
  <img src="images/06-lab2-host-header.png" alt="รูปที่ 6 ผล LAB 2" width="900"><br>
  <em><b>รูปที่ 6</b> ผล LAB 2: curl -H 'Host: shop.localhost' ได้ Name: menu, ไม่ใส่ Host → 404, ADDRESS แสดง localhost; whoami แสดง Host: shop.localhost:30080</em>
</p>

- ADDRESS `localhost` มาจาก flag `ingressendpoint.hostname=localhost` (Traefik เขียน status ของป้าย) ใช้บอกว่า **controller รับป้ายนี้แล้ว**
- Backends แสดง IP:พอร์ตของ Pod menu ทั้งสองตัว (จาก EndpointSlice) Events เป็น `<none>` (Ingress แทบไม่มี Event)
- Traefik กระจายคำขอสลับกันสองบูธ (3/3) และ access log บอก status, ชื่อ router (`ingress-demo-shop-shop-localhost@kubernetes`) และ **IP ของ Pod ที่ตอบ**

### ขั้นที่ 6: เปิดจาก browser

🌐 **browser บนเครื่องนักศึกษา** เปิด `http://shop.localhost:30080/` ถ้า browser แปลง `*.localhost` เองจะเห็นข้อความของ whoami ขึ้นต้นด้วย `Name: menu` และบรรทัด `Host: shop.localhost:30080` เหมือนผลของ curl ถ้าเปิดไม่ได้ (เช่น ขึ้นว่าหาเซิร์ฟเวอร์ไม่เจอ) ให้ใช้ทางสำรองแก้ไฟล์ hosts แล้วจดไว้ว่า browser/ระบบปฏิบัติการของตัวเองเป็นแบบไหน (บทนี้ทดสอบแล้วเฉพาะ Chromium บน Linux)

### สิ่งที่เห็น

- ป้ายแผ่นเดียวทำให้ `shop.localhost` เข้าถึง Service ClusterIP `menu` ได้ผ่านประตู 30080 โดยไม่ต้องมี NodePort ของแอป
- `Host` เป็นตัวตัดสิน: มีชื่อตรง → menu, ไม่มีหรือชื่ออื่น → 404 ของ Traefik
- curl ใส่พอร์ตใน `Host` และแปลง `*.localhost` เอง ส่วน `getent` แปลงไม่ได้

**คำถามชวนคิด**

1. `X-Forwarded-Port` เป็น `80` เมื่อใช้ `-H 'Host: shop.localhost'` แต่เป็น `30080` เมื่อใช้ชื่อใน URL ทำไม และแอปที่สร้างลิงก์จาก header นี้จะได้ผลต่างกันอย่างไร
2. ถ้าลบ Pod menu ทีละตัว Traefik รู้ได้อย่างไรว่าต้องส่งไป Pod ใหม่ (ดูว่า Traefik watch อะไร)

---

## LAB 3: ชื่อเดียว หลายทางเดิน (path fan-out)

<p align="center" id="fig-7">
  <img src="images/07-lab3-open.png" alt="รูปที่ 7 LAB 3 path fan-out" width="900"><br>
  <em><b>รูปที่ 7</b> LAB 3 เปิด: ชื่อเดียว shop.localhost แยก path / → menu, /api → api, /admin → admin (3 Service)</em>
</p>

**เป้าหมาย:** แก้ป้าย `shop` ให้แยก `/` → menu, `/api` → api, `/admin` → admin ดูว่า path ที่ยาวกว่าชนะ path ไม่ถูกตัด และ backend อ้าง port ได้ทั้ง number และ name

**ไฟล์:** `lab03-fanout/ingress.yaml` (ป้าย `shop` เดิม apply ทับ LAB 2)

### ขั้นที่ 1: แก้ป้าย

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
kubectl apply -f lab03-fanout/ingress.yaml
kubectl -n ingress-demo describe ing shop | sed -n '/Rules/,/Annotations/p'
```

```text
ingress.networking.k8s.io/shop configured
Rules:
  Host            Path  Backends
  ----            ----  --------
  shop.localhost
                  /        menu:80 (10.244.2.9:8080,10.244.1.4:8080)
                  /api     api:http (10.244.1.5:8080,10.244.2.10:8080)
                  /admin   admin:80 (10.244.2.11:8080,10.244.1.6:8080)
Annotations:      <none>
```

กฎ `/api` อ้าง `port: {name: http}` (describe แสดง `api:http`) ส่วนอีกสองกฎอ้าง `number: 80` ทั้งสองแบบชี้ไปพอร์ตเดียวกันของ Service และ Backends มี IP ครบทุกกฎ

### ขั้นที่ 2: ยิงหลาย path

```bash
sleep 2; for p in / /order /api /api/ /api/stats /admin /admin/x /apix; do printf '%-11s -> ' $p; curl -s http://shop.localhost:30080$p | grep -E '^Name|^GET' | tr '\n' ' '; echo; done
```

```text
/           -> Name: menu GET / HTTP/1.1
/order      -> Name: menu GET /order HTTP/1.1
/api        ->
/api/       -> Name: api GET /api/ HTTP/1.1
/api/stats  -> Name: api GET /api/stats HTTP/1.1
/admin      -> Name: admin GET /admin HTTP/1.1
/admin/x    -> Name: admin GET /admin/x HTTP/1.1
/apix       -> Name: menu GET /apix HTTP/1.1
```

<p align="center" id="fig-8">
  <img src="images/08-lab3-result.png" alt="รูปที่ 8 ผล LAB 3" width="900"><br>
  <em><b>รูปที่ 8</b> ผล LAB 3: /api/stats ไป api และ path ไม่ถูกตัด (GET /api/stats) ส่วน /order ไป menu; backend อ้าง port ได้ทั้ง number: 80 และ name: http</em>
</p>

- `/api/stats` ตรงทั้ง `/` และ `/api` → **path ที่ยาวกว่าชนะ** ไป api และแอปได้รับ `GET /api/stats` เต็ม (**path ไม่ถูกตัด**)
- `/order` และ `/apix` ไม่ตรง `/api` (Prefix เทียบทีละท่อน) จึงตกไปที่ `/` → menu
- **`/api` ว่าง ไม่ใช่ error** — ดูขั้นที่ 3

### ขั้นที่ 3: `/api` ของ whoami ตอบเป็น JSON

```bash
for i in 1 2 3; do curl -s -o /dev/null -w '%{http_code} ' http://shop.localhost:30080/api; done; echo
curl -s http://shop.localhost:30080/api | python3 -c 'import json,sys; d=json.load(sys.stdin); print("name =", d["name"], "| url =", d["url"])'
kubectl -n traefik logs deploy/traefik --since=2m | grep -E '"GET /api ' | head -3
```

```text
200 200 200
name = api | url = /api
172.19.0.2 - - [05/Oct/2026:13:13:16 +0000] "GET /api HTTP/1.1" 200 502 "-" "-" 20 "ingress-demo-shop-shop-localhost-api@kubernetes" "http://10.244.2.10:8080" 0ms
...
```

path `/api` (ตรงตัว) ของ image `traefik/whoami` เป็น endpoint พิเศษที่ตอบ JSON (`{"hostname":"api-84cf8dd6b8-kmx8c",...,"name":"api",...}`) จึงไม่มีบรรทัด `Name:` ให้ grep แต่ได้ 200 และ access log ยืนยันว่า router `...-api@kubernetes` เป็นคนตอบ (เลข `502` ในบรรทัดนี้คือ **ขนาด body 502 ไบต์** ไม่ใช่รหัส 502 รหัสคือ `200` ที่อยู่หน้า)

### ขั้นที่ 4: router ที่ Traefik สร้าง

```bash
curl -s localhost:30082/api/http/routers | python3 -c 'import json,sys; [print(r["name"], "|", r["rule"], "|", r.get("priority")) for r in json.load(sys.stdin) if "ingress-demo" in r["name"]]'
```

```text
ingress-demo-shop-shop-localhost-admin@kubernetes | Host("shop.localhost") && (Path("/admin") || PathPrefix("/admin/")) | 67
ingress-demo-shop-shop-localhost-api@kubernetes | Host("shop.localhost") && (Path("/api") || PathPrefix("/api/")) | 63
ingress-demo-shop-shop-localhost@kubernetes | Host("shop.localhost") && PathPrefix("/") | 41
websecure-ingress-demo-shop-shop-localhost-admin@kubernetes | Host("shop.localhost") && (Path("/admin") || PathPrefix("/admin/")) | 67
websecure-ingress-demo-shop-shop-localhost-api@kubernetes | Host("shop.localhost") && (Path("/api") || PathPrefix("/api/")) | 63
websecure-ingress-demo-shop-shop-localhost@kubernetes | Host("shop.localhost") && PathPrefix("/") | 41
```

หนึ่ง path = หนึ่ง router priority คือความยาวของ rule (67 > 63 > 41) จึงได้ผล "ยาวกว่าชนะ" และมีชุด `websecure-...` ซ้ำเพราะป้ายที่ไม่ระบุ entrypoint ใช้ทั้งประตู HTTP และ HTTPS (ทดลองใน LAB 7)

### สิ่งที่เห็น

- ชื่อเดียวแยกได้ 3 Service ตาม path, path ที่ยาวกว่าชนะ และ path ถูกส่งต่อเต็ม ๆ
- `/apix` ไม่ถูกนับเป็น `/api` (ทีละท่อน) — ผลนี้ได้เพราะเปิด `strictPrefixMatching` (LAB 5)

**คำถามชวนคิด**

1. ถ้าแอป api ถูกเขียนให้ตอบที่ `/stats` (ไม่มี `/api` นำหน้า) ป้ายนี้จะใช้ได้ไหม ต้องเพิ่มอะไร (ดู LAB 8 ขั้นที่ 3)
2. ถ้าเพิ่มกฎ `path: /api/stats` แบบ `Exact` ไปที่ admin คำขอ `/api/stats` จะไปที่ไหน เพราะอะไร

---

## LAB 4: หลายชื่อ ประตูเดียว (host-based)

<p align="center" id="fig-9">
  <img src="images/09-lab4-open.png" alt="รูปที่ 9 LAB 4 host-based" width="900"><br>
  <em><b>รูปที่ 9</b> LAB 4: เพิ่มกฎ admin.localhost → admin, ชื่ออื่นเช่น other.localhost → 404; Ingress ที่ไม่ใส่ class ถูกเติม ingressClassName: traefik</em>
</p>

**เป้าหมาย:** แขวนป้ายแผ่นที่สอง `admin.localhost → admin` **โดยไม่ใส่ `ingressClassName`** ดูว่า default class ถูกเติมให้ และทดสอบชื่อที่ไม่มีป้ายรับ

**ไฟล์:** `lab04-hosts/ingress.yaml` (Ingress `backoffice`)

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
grep -n ingressClassName lab04-hosts/ingress.yaml || echo "ไม่มี ingressClassName ในไฟล์"
kubectl apply -f lab04-hosts/ingress.yaml
kubectl -n ingress-demo get ing
kubectl -n ingress-demo get ing backoffice -o jsonpath='{.spec.ingressClassName}'; echo
```

```text
3:# ตั้งใจ "ไม่ใส่ ingressClassName" — IngressClass traefik เป็น default จึงถูกเติมให้ตอนสร้าง
ingress.networking.k8s.io/backoffice created
NAME         CLASS     HOSTS             ADDRESS     PORTS   AGE
backoffice   traefik   admin.localhost   localhost   80      0s
shop         traefik   shop.localhost    localhost   80      31s
traefik
```

`grep` เจอแค่บรรทัดคอมเมนต์ (ไฟล์ไม่มีฟิลด์นี้) แต่หลังสร้าง `spec.ingressClassName` เป็น `traefik` เพราะ IngressClass `traefik` มี annotation `is-default-class: "true"`

```bash
sleep 2; curl -s http://admin.localhost:30080/ | grep -E '^Name|^GET|^Host'
curl -s http://admin.localhost:30080/api/stats | grep -E '^Name|^GET'
curl -s http://shop.localhost:30080/ | grep -E '^Name'
curl -s -i http://other.localhost:30080/ | grep -E '^HTTP|404'
curl -s -H 'Host: ADMIN.localhost' localhost:30080/ | grep -E '^Name' || echo "(ไม่พบ)"
curl -s localhost:30080/; curl -s http://127.0.0.1:30080/
```

```text
Name: admin
Hostname: admin-86c89bffbb-5v554
GET / HTTP/1.1
Host: admin.localhost:30080
Name: admin
GET /api/stats HTTP/1.1
Name: menu
HTTP/1.1 404 Not Found
404 page not found
Name: admin
404 page not found
404 page not found
```

### สิ่งที่เห็น

- ประตูเดียว (30080) สองชื่อ ได้คนละ Service: `admin.localhost` → admin **ทุก path** (`/api/stats` ก็ไป admin เพราะกฎผูกกับชื่อก่อน) `shop.localhost` → menu
- ชื่อที่ไม่มีป้ายรับ (`other.localhost`), `localhost` และ `127.0.0.1` ได้ 404 ของ Traefik
- ชื่อโฮสต์ไม่สนตัวพิมพ์ (`ADMIN.localhost` → admin) ต่างจาก path ที่สนตัวพิมพ์ (LAB 5)
- ป้ายที่ไม่ใส่ class ถูกเติม `traefik` ให้ตอนสร้าง

**คำถามชวนคิด**

1. ถ้าวันหนึ่งติดตั้ง controller ตัวที่สองและตั้ง class ของมันเป็น default ด้วย ป้ายแบบ `lab04-hosts/ingress.yaml` จะเป็นอย่างไร ควรเขียนป้ายอย่างไรให้ปลอดภัย
2. ถ้าต้องการให้ `www.shop.localhost` และ `shop.localhost` ไปที่เดียวกัน เขียนกฎได้กี่แบบ (ลองคิดถึง wildcard `*.shop.localhost` ว่าครอบคลุมชื่อไหน)

---
## LAB 5: pathType และ strictPrefixMatching

<p align="center" id="fig-10">
  <img src="images/10-lab5-open.png" alt="รูปที่ 10 LAB 5 pathType" width="900"><br>
  <em><b>รูปที่ 10</b> LAB 5 เปิด: Ingress paths.localhost มี Prefix /api, Prefix /docs/, Exact /menu, ImplementationSpecific /impl แล้วยิง path ทดสอบ 15 แบบ</em>
</p>

**เป้าหมาย:** ทดลอง `pathType` ทั้งสามแบบบนชื่อ `paths.localhost` ด้วยการยิง 15 path แล้วเทียบผลเมื่อเปิด/ปิด flag `strictPrefixMatching` ของ Traefik (ส่วนเฉพาะ Traefik)

**ไฟล์:** `lab05-pathtype/ingress.yaml` (Prefix `/api`, Prefix `/docs/`, Exact `/menu`, ImplementationSpecific `/impl` ไม่มีกฎ `/`), `lab05-pathtype/try-paths.sh` (ยิง path ผ่าน `Host: paths.localhost` แล้วพิมพ์ตาราง path → status → ใครตอบ; path `/api` ที่ตอบ JSON จะแสดงเป็น `Name: api (JSON)`)

### ขั้นที่ 1: ป้ายและ flag ปัจจุบัน

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
kubectl apply -f lab05-pathtype/ingress.yaml
kubectl -n ingress-demo get ing paths
kubectl -n traefik get deploy traefik -o jsonpath='{.spec.template.spec.containers[0].args}' | tr ',' '\n' | grep -n -E 'strict|allowEmpty'
```

```text
ingress.networking.k8s.io/paths created
NAME    CLASS     HOSTS             ADDRESS     PORTS   AGE
paths   traefik   paths.localhost   localhost   80      0s
6:"--providers.kubernetesingress.strictPrefixMatching=true"
7:"--providers.kubernetesingress.allowEmptyServices=true"
```

`strictPrefixMatching` อยู่บรรทัดที่ 6 ของ args (ตำแหน่ง index `5` เมื่อนับจาก 0) ซึ่งจะใช้ในคำสั่ง patch ขั้นที่ 3

### ขั้นที่ 2: ยิง 15 path (strict = true)

```bash
sleep 2; ./lab05-pathtype/try-paths.sh
```

```text
PATH       STATUS ใครตอบ
/api       200    Name: api (JSON)
/api/      200    Name: api
/api/x     200    Name: api
/apix      404    404 page not found
/API       404    404 page not found
/docs      200    Name: admin
/docs/     200    Name: admin
/docs/a    200    Name: admin
/docsx     404    404 page not found
/menu      200    Name: menu
/menu/     404    404 page not found
/menux     404    404 page not found
/impl      200    Name: admin
/impl/x    200    Name: admin
/implx     404    404 page not found
```

```bash
curl -s localhost:30082/api/http/routers | python3 -c 'import json,sys; [print(r["name"].split("@")[0], "|", r["rule"]) for r in json.load(sys.stdin) if r["name"].startswith("ingress-demo-paths")]'
```

```text
ingress-demo-paths-paths-localhost-api | Host("paths.localhost") && (Path("/api") || PathPrefix("/api/"))
ingress-demo-paths-paths-localhost-docs | Host("paths.localhost") && (Path("/docs") || PathPrefix("/docs/"))
ingress-demo-paths-paths-localhost-impl | Host("paths.localhost") && (Path("/impl") || PathPrefix("/impl/"))
ingress-demo-paths-paths-localhost-menu | Host("paths.localhost") && Path("/menu")
```

| กฎ | ผลที่ได้ | ตรงมาตรฐานเพราะ |
|---|---|---|
| Prefix `/api` | `/api`, `/api/`, `/api/x` → 200; `/apix` → 404 | เทียบทีละท่อน `apix` ≠ `api` |
| (ไม่มีกฎ `/`) | `/API` → 404 | path สนตัวพิมพ์ และ `paths.localhost` ไม่มีกฎ `/` ให้ตก |
| Prefix `/docs/` | `/docs`, `/docs/`, `/docs/a` → 200; `/docsx` → 404 | Prefix ไม่สน `/` ท้าย |
| Exact `/menu` | `/menu` → 200; `/menu/`, `/menux` → 404 | ต้องตรงทั้งเส้น |
| ImplementationSpecific `/impl` | `/impl`, `/impl/x` → 200; `/implx` → 404 | Traefik (strict) ทำเหมือน Prefix |

rule ที่ Traefik สร้างแปลง Prefix เป็น `Path("/api") || PathPrefix("/api/")` = "ตรงตัว หรือขึ้นต้นด้วย `/api/`"

### ขั้นที่ 3: ปิด strict (ค่าเริ่มต้นของ Traefik) แล้วเทียบ

```bash
kubectl -n traefik patch deploy traefik --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/args/5","value":"--providers.kubernetesingress.strictPrefixMatching=false"}]'
kubectl -n traefik rollout status deploy/traefik --timeout=120s
sleep 3; ./lab05-pathtype/try-paths.sh
curl -s localhost:30082/api/http/routers | python3 -c 'import json,sys; [print(r["name"].split("@")[0], "|", r["rule"]) for r in json.load(sys.stdin) if r["name"].startswith("ingress-demo-paths")]'
```

```text
deployment.apps/traefik patched
Waiting for deployment "traefik" rollout to finish: 1 old replicas are pending termination...
...
deployment "traefik" successfully rolled out
PATH       STATUS ใครตอบ
/api       200    Name: api (JSON)
/api/      200    Name: api
/api/x     200    Name: api
/apix      200    Name: api
/API       404    404 page not found
/docs      404    404 page not found
/docs/     200    Name: admin
/docs/a    200    Name: admin
/docsx     404    404 page not found
/menu      200    Name: menu
/menu/     404    404 page not found
/menux     404    404 page not found
/impl      200    Name: admin
/impl/x    200    Name: admin
/implx     200    Name: admin
ingress-demo-paths-paths-localhost-api | Host("paths.localhost") && PathPrefix("/api")
ingress-demo-paths-paths-localhost-docs | Host("paths.localhost") && PathPrefix("/docs/")
ingress-demo-paths-paths-localhost-impl | Host("paths.localhost") && PathPrefix("/impl")
ingress-demo-paths-paths-localhost-menu | Host("paths.localhost") && Path("/menu")
```

<p align="center" id="fig-11">
  <img src="images/11-lab5-table.png" alt="รูปที่ 11 ผล LAB 5 ตาราง pathType" width="900"><br>
  <em><b>รูปที่ 11</b> ผล LAB 5 (strictPrefixMatching=true): /apix → 404, /docs → 200, /menu/ → 404, /implx → 404; ถ้าปิด strict /apix ไป api และ /docs กลายเป็น 404</em>
</p>

ค่าเริ่มต้นของ Traefik เทียบ Prefix **แบบตัวอักษร** (`PathPrefix("/api")` จับ `/apix` ด้วย) และกฎ `/docs/` ไม่รับ `/docs` — **ผิดมาตรฐานสามจุด** (`/apix`, `/docs`, `/implx`) ผลนี้เป็นตัวอย่างว่าทำไมต้องทดสอบกับ controller จริง

### ขั้นที่ 4: คืนค่าด้วยไฟล์ของบท

```bash
kubectl apply -f ingress-controller/00-traefik.yaml
kubectl -n traefik rollout status deploy/traefik --timeout=120s
sleep 3; ./lab05-pathtype/try-paths.sh paths.localhost /apix /docs /docs/
```

```text
namespace/traefik unchanged
serviceaccount/traefik unchanged
clusterrole.rbac.authorization.k8s.io/traefik unchanged
clusterrolebinding.rbac.authorization.k8s.io/traefik unchanged
deployment.apps/traefik configured
service/traefik unchanged
ingressclass.networking.k8s.io/traefik unchanged
...
deployment "traefik" successfully rolled out
PATH       STATUS ใครตอบ
/apix      404    404 page not found
/docs      200    Name: admin
/docs/     200    Name: admin
```

`kubectl apply` ไฟล์เดิมคืน args ทั้งชุด (`deployment.apps/traefik configured`) **ใช้วิธีนี้คืนค่าทุกครั้งที่ patch Traefik ในบทนี้** (LAB 7, LAB เสริม)

### สิ่งที่เห็น

- Prefix เทียบทีละท่อน ไม่สน `/` ท้าย แต่สนตัวพิมพ์, Exact ต้องตรงทั้งเส้น, ImplementationSpecific แล้วแต่ controller
- ค่าเริ่มต้นของ Traefik ไม่ตรงมาตรฐาน ต้องเปิด `strictPrefixMatching=true` (ไฟล์ของบทเปิดไว้แล้ว)

**คำถามชวนคิด**

1. ถ้าร้านจริงย้าย controller จาก Traefik (ค่าเริ่มต้น) ไป controller ที่ตรงมาตรฐาน URL แบบไหนของลูกค้าที่เคยใช้ได้จะกลายเป็น 404
2. ทำไมการเขียน `/docs/` (มี `/` ท้าย) ในป้ายจึงเสี่ยงกว่า `/docs`

---

## LAB 6: ทำให้พังแล้ว debug

<p align="center" id="fig-12">
  <img src="images/12-lab6-open.png" alt="รูปที่ 12 LAB 6 ทำให้พังทีละแบบ" width="900"><br>
  <em><b>รูปที่ 12</b> LAB 6 เปิด: ทำพังทีละแบบแล้วดูผลจริง — ingressClassName ผิด ได้ 404, ชื่อ Service ผิด ได้ 404 (describe เห็น services &quot;menuu&quot; not found), port ผิด ได้ 404 (log: service port not found), scale เป็น 0 ได้ 503 no available server; แล้วลอง defaultBackend</em>
</p>

**เป้าหมาย:** ทำป้ายพังทีละแบบ (class ผิด, ชื่อ Service ผิด, port ผิด, ไม่มี Pod Ready) แล้วฝึกอ่านอาการจาก `kubectl get/describe ing`, log `ERR` และ access log ของ Traefik ปิดท้ายด้วย `defaultBackend` และเห็นว่าทำไมต้องลบทิ้ง

**ไฟล์:** `lab06-debug/wrongclass.yaml` (`ingressClassName: nginx`), `lab06-debug/typo.yaml` (Service `menuu` และ `port: 8080`), `lab06-debug/lost.yaml` (มีแค่ `spec.defaultBackend` → admin)

### ขั้นที่ 1: class ผิด

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
kubectl apply -f lab06-debug/wrongclass.yaml
sleep 3; kubectl -n ingress-demo get ing
curl -s -H 'Host: wrong.localhost' localhost:30080/
kubectl get ingressclass
```

```text
ingress.networking.k8s.io/wrongclass created
NAME         CLASS     HOSTS             ADDRESS     PORTS   AGE
backoffice   traefik   admin.localhost   localhost   80      30s
paths        traefik   paths.localhost   localhost   80      28s
shop         traefik   shop.localhost    localhost   80      61s
wrongclass   nginx     wrong.localhost               80      3s
404 page not found
NAME                CONTROLLER                      PARAMETERS   AGE
traefik (default)   traefik.io/ingress-controller   <none>       87s
```

ป้าย `wrongclass` ติดตรา `nginx` ซึ่งไม่มี IngressClass/controller ในคลัสเตอร์ **ADDRESS ว่าง** = ไม่มีใครรับป้าย Traefik ไม่สร้าง router ให้ `wrong.localhost` จึงได้ 404

### ขั้นที่ 2: ชื่อ Service ผิด และ port ผิด

```bash
kubectl apply -f lab06-debug/typo.yaml
sleep 3; kubectl -n ingress-demo get ing typo
kubectl -n ingress-demo describe ing typo | sed -n '/Rules/,$p'
curl -s -i -H 'Host: typo.localhost' localhost:30080/ | grep -E '^HTTP|page'; curl -s -i -H 'Host: typo.localhost' localhost:30080/port | grep -E '^HTTP|page'
kubectl -n traefik logs deploy/traefik --since=30s | grep ERR | sed 's/\x1b\[[0-9;]*m//g' | sort -u -t'"' -k2,2 | head -4
```

```text
ingress.networking.k8s.io/typo created
NAME   CLASS     HOSTS            ADDRESS     PORTS   AGE
typo   traefik   typo.localhost   localhost   80      3s
Rules:
  Host            Path  Backends
  ----            ----  --------
  typo.localhost
                  /       menuu:80 (<error: services "menuu" not found>)
                  /port   menu:8080 ()
Annotations:      <none>
Events:           <none>
HTTP/1.1 404 Not Found
404 page not found
HTTP/1.1 404 Not Found
404 page not found
2026-10-05T13:14:12Z ERR Cannot create service error="service not found" ingress=typo namespace=ingress-demo providerName=kubernetes serviceName=menuu servicePort=&ServiceBackendPort{Name:,Number:80,}
2026-10-05T13:14:12Z ERR Cannot create service error="service port not found" ingress=typo namespace=ingress-demo providerName=kubernetes serviceName=menu servicePort=&ServiceBackendPort{Name:,Number:8080,}
```

- `kubectl apply` ผ่านและ ADDRESS มีค่า (Traefik รับป้ายแล้ว) แต่ **API server ไม่ตรวจว่า backend มีจริง** และ Events เป็น `<none>`
- `describe` บอกใบ้: `<error: services "menuu" not found>` และ `menu:8080 ()` (วงเล็บว่าง = หา endpoint ของพอร์ตนั้นไม่เจอ)
- log ของ Traefik บอกสาเหตุตรงที่สุด: `service not found` และ `service port not found` (`sed` ล้างรหัสสี ANSI ส่วน `sort -u` ตัดบรรทัดซ้ำ)
- ทั้งสองกรณีลูกค้าได้ **404** (router ของกฎนั้นไม่ถูกสร้าง)

### ขั้นที่ 3: Service ไม่มี Pod Ready → 503

```bash
kubectl -n ingress-demo scale deploy menu --replicas=0
kubectl -n ingress-demo get endpointslice -l kubernetes.io/service-name=menu
sleep 3; curl -s -i http://shop.localhost:30080/ | grep -E '^HTTP|no available'
kubectl -n ingress-demo describe ing shop | grep -E '^\s+/ '
kubectl -n traefik logs deploy/traefik --tail=1
```

```text
deployment.apps/menu scaled
NAME         ADDRESSTYPE   PORTS   ENDPOINTS               AGE
menu-wxspn   IPv4          8080    10.244.2.9,10.244.1.4   73s
HTTP/1.1 503 Service Unavailable
no available server
                  /        menu:80 ()
172.19.0.2 - - [05/Oct/2026:13:14:18 +0000] "GET / HTTP/1.1" 503 20 "-" "-" 7 "ingress-demo-shop-shop-localhost@kubernetes" "-" 0ms
```

- EndpointSlice ที่ดูทันทีหลัง `scale` ยังแสดง IP เดิม (Pod กำลังปิดช่วง preStop 5 วินาที) หลังรอ 3 วินาที Pod ไม่ Ready แล้ว describe แสดง `menu:80 ()`
- กฎตรงแต่ไม่มีปลายทาง → **`503 Service Unavailable` `no available server`** และ access log มีชื่อ router แต่ปลายทางเป็น `"-"`
- ได้ 503 (แทน 404) เพราะ flag `--providers.kubernetesingress.allowEmptyServices=true` ของบท (ค่าเริ่มต้นของ Traefik จะตัด router ทิ้ง ได้ 404 ซึ่งแยกไม่ออกกับกรณีไม่มีกฎ)

คืนจำนวน menu

```bash
kubectl -n ingress-demo scale deploy menu --replicas=2 && kubectl -n ingress-demo rollout status deploy/menu --timeout=60s
sleep 2; curl -s http://shop.localhost:30080/ | grep '^Name'
```

```text
deployment.apps/menu scaled
...
deployment "menu" successfully rolled out
Name: menu
```

<p align="center" id="fig-13">
  <img src="images/13-lab6-errors.png" alt="รูปที่ 13 ผล LAB 6 อาการพัง" width="900"><br>
  <em><b>รูปที่ 13</b> ผล LAB 6: describe แสดง &lt;error: services &quot;menuu&quot; not found&gt;, log ERR service port not found, class nginx → ADDRESS ว่าง, scale 0 → 503 no available server</em>
</p>

### ขั้นที่ 4: defaultBackend = catch-all ของทั้ง controller

```bash
kubectl apply -f lab06-debug/lost.yaml
sleep 3; kubectl -n ingress-demo get ing lost
for h in other.localhost typo.localhost wrong.localhost ''; do printf '%-16s -> ' "${h:-(ไม่มี Host)}"; curl -s -H "Host: $h" localhost:30080/ | grep -m1 '^Name' || echo 404; done
curl -s localhost:30080/ | grep -m1 '^Name'
```

```text
ingress.networking.k8s.io/lost created
NAME   CLASS     HOSTS   ADDRESS     PORTS   AGE
lost   traefik   *       localhost   80      3s
other.localhost  -> Name: admin
typo.localhost   -> Name: admin
wrong.localhost  -> Name: admin
(ไม่มี Host) -> Name: admin
Name: admin
```

ป้าย `lost` ไม่มี `ingressClassName` (ได้ default) ไม่มี rules มีแค่ `defaultBackend` (HOSTS `*`) ใน Traefik ป้ายนี้รับ **ทุกคำขอที่ไม่มีป้ายอื่นรับ ทั้งคลัสเตอร์** — ชื่อที่ไม่มีป้าย, ป้ายที่ backend พัง (`typo`), ป้าย class ผิด (`wrong`) และคำขอที่ไม่มี `Host` ไหลไปที่ admin หมด

แล้วกฎที่ตรงแต่ไม่มี Pod Ready ล่ะ

```bash
kubectl -n ingress-demo scale deploy menu --replicas=0; sleep 4; printf 'shop.localhost (menu=0) -> '; curl -s -o /dev/null -w '%{http_code}\n' http://shop.localhost:30080/; kubectl -n ingress-demo scale deploy menu --replicas=2; kubectl -n ingress-demo rollout status deploy/menu --timeout=60s
```

```text
deployment.apps/menu scaled
shop.localhost (menu=0) -> 503
deployment.apps/menu scaled
...
deployment "menu" successfully rolled out
```

ยังได้ **503** ไม่ไหลไป admin เพราะกฎ `shop.localhost` ยังอยู่ (`allowEmptyServices=true`)

<p align="center" id="fig-14">
  <img src="images/14-lab6-default-backend.png" alt="รูปที่ 14 ผล LAB 6 defaultBackend" width="900"><br>
  <em><b>รูปที่ 14</b> ผล LAB 6 (defaultBackend): ชื่อที่ไม่ตรงกฎไหนเลยไหลไปโต๊ะของหาย (admin) ใน Traefik เป็น catch-all ของทั้งคลัสเตอร์ จึงลบทิ้งหลังทดลอง (ส่วนกฎที่ Service ไม่มี endpoint ยังได้ 503 ไม่ไหลไป defaultBackend)</em>
</p>

### ขั้นที่ 5: เก็บกวาด LAB 6 (สำคัญ)

```bash
kubectl delete -f lab06-debug/
kubectl -n ingress-demo get ing
sleep 2; curl -s http://other.localhost:30080/; for i in 1 2 3 4 5; do curl -s -o /dev/null -w '%{http_code} ' http://shop.localhost:30080/; done; echo
```

```text
ingress.networking.k8s.io "lost" deleted from ingress-demo namespace
ingress.networking.k8s.io "typo" deleted from ingress-demo namespace
ingress.networking.k8s.io "wrongclass" deleted from ingress-demo namespace
NAME         CLASS     HOSTS             ADDRESS     PORTS   AGE
backoffice   traefik   admin.localhost   localhost   80      47s
paths        traefik   paths.localhost   localhost   80      45s
shop         traefik   shop.localhost    localhost   80      78s
404 page not found
200 200 200 200 200
```

**ต้องลบ `lost.yaml` ทุกครั้ง** ไม่งั้นทุกชื่อที่ผิดใน LAB ถัดไป (และ LAB 10) จะเข้า admin แทน 404 ทำให้อ่านผลผิด หลังลบ `other.localhost` กลับเป็น 404 (ถ้ายิง `shop.localhost` ทันทีหลัง menu กลับมาแล้วได้ผลว่าง ให้รอ 2–3 วินาทีแล้วลองใหม่ ผลจริงรอบตรวจซ้ำได้ 200 ทั้ง 5 ครั้ง)

### สิ่งที่เห็น

| ทำพังแบบ | สิ่งที่เห็น | ลูกค้าได้ |
|---|---|---|
| `ingressClassName: nginx` | CLASS `nginx`, **ADDRESS ว่าง** | 404 |
| Service ชื่อผิด `menuu` | describe `<error: services "menuu" not found>`, log `ERR ... service not found` | 404 |
| port ผิด `8080` | describe `menu:8080 ()`, log `ERR ... service port not found` | 404 |
| scale เป็น 0 | describe `menu:80 ()`, access log ปลายทาง `"-"` | **503 no available server** |
| defaultBackend อย่างเดียว | HOSTS `*` | ทุกชื่อที่ไม่มีป้าย → admin |

**คำถามชวนคิด**

1. ทั้ง class ผิด, ชื่อ Service ผิด และ port ผิด ลูกค้าได้ 404 เหมือนกัน นักศึกษาจะแยกสามกรณีนี้ออกจากกันด้วยคำสั่งอะไรบ้าง
2. ถ้าร้านจริงตั้ง defaultBackend ไปที่หน้าแอดมินแบบใน `lost.yaml` จะเกิดความเสี่ยงอะไร ควรชี้ defaultBackend ไปที่ไหนแทน

---

## LAB 7: TLS ที่ Ingress

<p align="center" id="fig-15">
  <img src="images/15-lab7-open.png" alt="รูปที่ 15 LAB 7 TLS" width="900"><br>
  <em><b>รูปที่ 15</b> LAB 7 เปิด: openssl สร้างใบรับรองหลายชื่อ (shop.localhost, admin.localhost, localhost) → Secret som-tls → spec.tls</em>
</p>

**เป้าหมาย:** ออกใบรับรอง self-signed หลายชื่อ (SAN) เก็บเป็น Secret `kubernetes.io/tls` แล้วติดที่ประตูด้วย `spec.tls` ทดสอบ HTTPS ด้วย `-k`, `--cacert`, `--resolve` ดู SNI ด้วย `openssl s_client` และดูว่าเกิดอะไรถ้า Traefik ไม่ได้เปิด TLS บน entrypoint

**ไฟล์:** `lab07-tls/ingress-tls.yaml` (ป้าย `shop` และ `backoffice` + `tls` ที่ใช้ Secret `som-tls`) ทำในโฟลเดอร์ `02_LAB/lab07-tls` แล้วกลับ `02_LAB`

### ขั้นที่ 1: ใบรับรองหลายชื่อ และ Secret

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd lab07-tls
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.localhost' -addext 'subjectAltName=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost' 2>&1 | tail -1
openssl x509 -in tls.crt -noout -subject -ext subjectAltName -enddate
kubectl -n ingress-demo create secret tls som-tls --cert=tls.crt --key=tls.key
kubectl -n ingress-demo get secret
```

```text
-----
subject=CN = shop.localhost
X509v3 Subject Alternative Name:
    DNS:shop.localhost, DNS:admin.localhost, DNS:localhost
notAfter=Oct  5 13:14:56 2027 GMT
secret/som-tls created
NAME      TYPE                DATA   AGE
som-tls   kubernetes.io/tls   2      0s
```

ใบเดียวใช้ได้สามชื่อ (SAN) Secret ชื่อ `som-tls` ชนิด `kubernetes.io/tls` แบบเดียวกับบทที่ 11 และต้องอยู่ namespace เดียวกับป้าย (`ingress-demo`) ไฟล์ `tls.key` เป็นกุญแจส่วนตัว **ห้าม commit** (`.gitignore` ของบทกันไว้แล้ว)

### ขั้นที่ 2: ติด TLS ที่ป้าย

```bash
kubectl apply -f ingress-tls.yaml
kubectl -n ingress-demo get ing
sleep 3; curl -sk https://shop.localhost:30081/ | grep -E '^Name|^Host|X-Forwarded-(Proto|Port)'
```

```text
ingress.networking.k8s.io/shop configured
ingress.networking.k8s.io/backoffice configured
NAME         CLASS     HOSTS             ADDRESS     PORTS     AGE
backoffice   traefik   admin.localhost   localhost   80, 443   74s
paths        traefik   paths.localhost   localhost   80        72s
shop         traefik   shop.localhost    localhost   80, 443   105s
Name: menu
Hostname: menu-5f588ffbdd-nwkqf
Host: shop.localhost:30081
X-Forwarded-Port: 30081
X-Forwarded-Proto: https
```

PORTS กลายเป็น `80, 443` (มี `spec.tls`) ลูกค้าเข้าทาง HTTPS (30081) แต่ menu ได้รับ HTTP ธรรมดาพร้อม `X-Forwarded-Proto: https` = **TLS termination ที่ประตู**

### ขั้นที่ 3: ตรวจใบรับรองแบบต่าง ๆ

```bash
curl -sS https://shop.localhost:30081/ >/dev/null; echo "rc=$?"
curl -s --cacert tls.crt https://shop.localhost:30081/ | grep -E '^Name'; echo "rc=$?"
curl -s --cacert tls.crt https://admin.localhost:30081/ | grep -E '^Name'
curl -s --cacert tls.crt https://localhost:30081/ -o /dev/null -w '%{http_code}\n'
curl -sS --cacert tls.crt https://127.0.0.1:30081/ >/dev/null; echo "rc=$?"
curl -s --cacert tls.crt --resolve shop.localhost:30081:127.0.0.1 https://shop.localhost:30081/api/x | grep '^Name'
```

```text
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html
...
rc=60
Name: menu
rc=0
Name: admin
404
curl: (60) SSL certificate problem: self-signed certificate
...
rc=60
Name: api
```

- ไม่มี `-k` → `curl: (60)` เพราะใบเป็น self-signed, `--cacert tls.crt` → ตรวจจริงผ่านทั้ง shop และ admin
- `https://localhost:30081/` ผ่านการตรวจใบ (มี `localhost` ใน SAN) แต่ได้ **404** เพราะไม่มีป้ายรับชื่อ `localhost`
- `https://127.0.0.1:30081/` ได้ `rc=60` เพราะ IP ไม่อยู่ใน SAN
- `--resolve` ใช้ชื่อร้านใน URL (เป็นทั้ง SNI และ `Host`) แต่บังคับให้ต่อไปที่ `127.0.0.1` — วิธีที่ถูกต้องสำหรับโปรแกรมที่แปลง `*.localhost` ไม่ได้

### ขั้นที่ 4: SNI และใบสำรอง

```bash
echo | openssl s_client -connect localhost:30081 -servername shop.localhost 2>/dev/null | grep -E '^subject|^issuer'
echo | openssl s_client -connect localhost:30081 -servername other.localhost 2>/dev/null | grep -E '^subject|^issuer'
curl -sS --cacert tls.crt https://paths.localhost:30081/menu >/dev/null; echo "rc=$?"
curl -sk https://paths.localhost:30081/menu | grep '^Name'
curl -sk -o /dev/null -w '%{http_code}\n' https://other.localhost:30081/
```

```text
subject=CN = shop.localhost
issuer=CN = shop.localhost
subject=CN = TRAEFIK DEFAULT CERT
issuer=CN = TRAEFIK DEFAULT CERT
curl: (60) SSL certificate problem: self-signed certificate
...
rc=60
Name: menu
404
```

ประตู HTTPS เดียวเลือกใบตามชื่อที่ลูกค้าบอกใน SNI (`-servername`) ชื่อที่ไม่มีใน `spec.tls` ได้ `TRAEFIK DEFAULT CERT` ป้าย `paths` ที่ไม่มี `spec.tls` ก็ยังตอบบน HTTPS (เพราะป้ายไม่ระบุ entrypoint จึงอยู่ทั้ง `web` และ `websecure`) แต่ด้วยใบสำรอง จึงตรวจด้วย `--cacert` ไม่ผ่าน

### ขั้นที่ 5: HTTP บนพอร์ต HTTPS และป้ายเดียวทั้งสองประตู

```bash
curl -si http://localhost:30081/ | head -1
curl -s http://shop.localhost:30080/ | grep -E '^Name|X-Forwarded-Proto'
kubectl -n ingress-demo describe ing shop | grep -A2 TLS
```

```text
HTTP/1.1 404 Not Found
Name: menu
X-Forwarded-Proto: http
TLS:
  som-tls terminates shop.localhost
Rules:
```

ส่ง HTTP ไปที่ 30081 ได้ 404 ของ Traefik (ต่างจาก nginx ในบทที่ 11 ที่ตอบ `400 The plain HTTP request was sent to HTTPS port`) และป้ายแผ่นเดียวยังตอบ HTTP ที่ 30080 ได้ (`X-Forwarded-Proto: http`) ยังไม่มีการบังคับ HTTPS — LAB 8 จะเพิ่ม redirect

### ขั้นที่ 6: ลองผิด — Traefik ไม่ได้เปิด TLS บน websecure (เฉพาะ Traefik)

```bash
kubectl -n traefik get deploy traefik -o jsonpath='{.spec.template.spec.containers[0].args[3]}'; echo
kubectl -n traefik patch deploy traefik --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/args/3","value":"--entryPoints.websecure.http.tls=false"}]'
kubectl -n traefik rollout status deploy/traefik --timeout=120s
sleep 3; curl -sk -i https://shop.localhost:30081/ | head -1; curl -sk https://shop.localhost:30081/ ; echo | openssl s_client -connect localhost:30081 -servername shop.localhost 2>/dev/null | grep -E '^subject'
```

```text
--entryPoints.websecure.http.tls=true
deployment.apps/traefik patched
...
deployment "traefik" successfully rolled out
HTTP/2 404
404 page not found
subject=CN = shop.localhost
```

Traefik ยังส่งใบของร้าน (`subject=CN = shop.localhost`) แต่ router ของป้ายไม่ได้เป็น TLS router คำขอ HTTPS จึงได้ **`HTTP/2 404`** ทั้งที่ใบรับรองถูก ผลนี้หาสาเหตุยากมากถ้าไม่รู้ว่าต้องมี flag `--entryPoints.websecure.http.tls=true` คืนค่าด้วยไฟล์ของบท

```bash
cd ..; kubectl apply -f ingress-controller/00-traefik.yaml | grep configured; kubectl -n traefik rollout status deploy/traefik --timeout=120s
sleep 3; curl -sk https://shop.localhost:30081/ | grep '^Name'
```

```text
deployment.apps/traefik configured
...
deployment "traefik" successfully rolled out
Name: menu
```

<p align="center" id="fig-16">
  <img src="images/16-lab7-results.png" alt="รูปที่ 16 ผล LAB 7" width="900"><br>
  <em><b>รูปที่ 16</b> ผล LAB 7: ไม่มี -k → curl: (60), --cacert tls.crt ผ่าน, ชื่ออื่นได้ TRAEFIK DEFAULT CERT, browser เตือนใบรับรอง self-signed (ต้องเปิด --entryPoints.websecure.http.tls=true)</em>
</p>

🌐 **browser บนเครื่องนักศึกษา** (ไม่บังคับ) เปิด `https://shop.localhost:30081/` จะเจอหน้าเตือนใบรับรอง `NET::ERR_CERT_AUTHORITY_INVALID` เพราะใบเป็น self-signed (ตัวอย่างหน้าจอจริงอยู่ใน LAB 10 ขั้น D) กด Advanced → Proceed (เฉพาะทดสอบ) แล้วจะเห็น `Name: menu` และ `X-Forwarded-Proto: https`

### สิ่งที่เห็น

- `spec.tls` + Secret `kubernetes.io/tls` → ป้ายตอบ HTTPS ที่ 30081 แอปได้ HTTP พร้อม `X-Forwarded-Proto: https`
- ตรวจจริงด้วย `--cacert` ชื่อต้องอยู่ใน SAN (`127.0.0.1` ไม่ผ่าน) ชื่อที่ไม่มีใบได้ `TRAEFIK DEFAULT CERT`
- Traefik ต้องเปิด `--entryPoints.websecure.http.tls=true` ไม่งั้น HTTPS ได้ `HTTP/2 404`
- ไฟล์ `lab07-tls/tls.crt`, `tls.key` เก็บไว้ได้จนจบบท (LAB 10 ออกใบใหม่ของตัวเอง)

**คำถามชวนคิด**

1. เทียบกับบทที่ 11 ที่ nginx ใน Pod ถือใบรับรอง: การย้าย TLS มาที่ประตูมีข้อดีอะไร และการรับส่งระหว่าง Traefik กับ Pod ยังเป็น HTTP ธรรมดา มีความเสี่ยงอะไรในงานจริง
2. ถ้าป้ายสองแผ่นใน namespace ต่างกันใช้ชื่อเดียวกันแต่ Secret ต่างกัน ประตูจะเลือกใบไหน (คิดจาก SNI ว่าเลือกได้ด้วยข้อมูลอะไรบ้าง)

---

## LAB 8: Middleware: redirect, basicAuth, stripPrefix

<p align="center" id="fig-17">
  <img src="images/17-lab8-open.png" alt="รูปที่ 17 LAB 8 Middleware" width="900"><br>
  <em><b>รูปที่ 17</b> LAB 8 เปิด: Middleware ของ Traefik (ไม่ใช่มาตรฐาน) redirectScheme, basicAuth (Secret basic-auth จากบท 011), stripPrefix ผูกด้วย annotation router.middlewares</em>
</p>

**เป้าหมาย:** ใช้ Middleware ของ Traefik (**ส่วนเฉพาะ Traefik ไม่ใช่มาตรฐาน**) ทำ (1) redirect HTTP → HTTPS พร้อมลองผิดแบบไม่ใส่ port (2) ด่านตรวจบัตรด้วย basicAuth ที่อ่าน Secret `kubernetes.io/basic-auth` จากบทที่ 11 (3) ตัด `/admin` ออกด้วย stripPrefix และดูว่าลำดับใน annotation คือลำดับด่าน

**ไฟล์:** `lab08-middleware/redirect.yaml` (Middleware `redirect-https` port `"30081"` + ป้าย `shop`), `redirect-noport.yaml` (Middleware เดิมไม่มี port), `admin-auth.yaml` (Middleware `admin-auth` + ป้าย `backoffice`), `strip.yaml` (Middleware `strip-admin` + ป้าย `shop` เหลือ `/` `/api` + ป้ายใหม่ `shop-admin`)

### ขั้นที่ 1: redirect HTTP → HTTPS

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
kubectl apply -f lab08-middleware/redirect.yaml
kubectl -n ingress-demo get middleware
sleep 3; curl -si 'http://shop.localhost:30080/menu?x=1' | grep -iE '^HTTP|^location'
curl -sk -o /dev/null -w '%{http_code}\n' 'https://shop.localhost:30081/menu?x=1'
curl -skL 'http://shop.localhost:30080/hello?x=1' | grep -E '^Name|^GET'
curl -si http://admin.localhost:30080/ | grep -iE '^HTTP' ; curl -si http://paths.localhost:30080/menu | grep -iE '^HTTP'
```

```text
middleware.traefik.io/redirect-https created
ingress.networking.k8s.io/shop configured
NAME             AGE
redirect-https   0s
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/menu?x=1
200
Name: menu
GET /hello?x=1 HTTP/1.1
HTTP/1.1 200 OK
HTTP/1.1 200 OK
```

- ป้าย `shop` มี annotation `traefik.ingress.kubernetes.io/router.middlewares: ingress-demo-redirect-https@kubernetescrd` (ชื่อ = `<namespace>-<ชื่อ Middleware>@kubernetescrd`)
- HTTP ได้ **301** ไป `https://shop.localhost:30081/...` เก็บ path + query เดิม `curl -L` ตามไปจนได้ menu บน HTTPS ได้ 200 ไม่ redirect ซ้ำ
- ป้ายอื่นที่ไม่ได้ผูก Middleware (`admin.localhost`, `paths.localhost`) ยังเป็น HTTP 200 ตามปกติ

### ขั้นที่ 2: ลองผิด — redirect ไม่ใส่ port

```bash
kubectl apply -f lab08-middleware/redirect-noport.yaml
sleep 3; curl -si 'http://shop.localhost:30080/menu?x=1' | grep -iE '^HTTP|^location'
curl -skL -o /dev/null -w '%{http_code} %{url_effective}\n' 'http://shop.localhost:30080/menu?x=1'; echo "rc=$?"
curl -si -H 'Host: shop.localhost' 'http://localhost:30080/menu' | grep -iE '^location'
```

```text
middleware.traefik.io/redirect-https configured
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost/menu?x=1
301 https://shop.localhost/menu?x=1
rc=7
Location: https://shop.localhost/menu
```

`Location` ไม่มีพอร์ต = พอร์ต 443 ซึ่งไม่มีใครฟังใน `k8s-lab` `curl -L` ต่อไม่ได้ (`rc=7` = couldn't connect) browser ก็จะขึ้นว่าเชื่อมต่อไม่ได้ เพราะ Traefik ไม่รู้ว่าลูกค้าเห็นประตู HTTPS เป็น NodePort 30081 คืนค่า

```bash
kubectl apply -f lab08-middleware/redirect.yaml
sleep 3; curl -si 'http://shop.localhost:30080/menu?x=1' | grep -iE '^location'
```

```text
middleware.traefik.io/redirect-https configured
ingress.networking.k8s.io/shop unchanged
Location: https://shop.localhost:30081/menu?x=1
```

### ขั้นที่ 3: basicAuth จาก Secret

สร้างบัตรเป็น Secret ชนิด `kubernetes.io/basic-auth` (บทที่ 11) **รหัส `meow-admin-123` เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น**

```bash
kubectl -n ingress-demo create secret generic admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow-admin-123
kubectl -n ingress-demo get secret
kubectl apply -f lab08-middleware/admin-auth.yaml
sleep 3; curl -si http://admin.localhost:30080/ | grep -iE '^HTTP|^location'
curl -ski https://admin.localhost:30081/ | grep -iE '^HTTP|^www-auth|401'
curl -sk -o /dev/null -w '%{http_code}\n' -u som:wrong https://admin.localhost:30081/
curl -sk -u som:meow-admin-123 https://admin.localhost:30081/ | grep -E '^HTTP|^Name|^Authorization' ; curl -sk -o /dev/null -w '%{http_code}\n' -u som:meow-admin-123 https://admin.localhost:30081/
curl -sk -u som:meow-admin-123 https://admin.localhost:30081/ | grep -c '^Authorization'
```

```text
secret/admin-auth created
NAME         TYPE                       DATA   AGE
admin-auth   kubernetes.io/basic-auth   2      0s
som-tls      kubernetes.io/tls          2      42s
middleware.traefik.io/admin-auth created
ingress.networking.k8s.io/backoffice configured
HTTP/1.1 301 Moved Permanently
Location: https://admin.localhost:30081/
HTTP/2 401
www-authenticate: Basic realm="traefik"
401 Unauthorized
401
Name: admin
200
0
```

- ป้าย `backoffice` ผูกสองด่าน `ingress-demo-redirect-https@kubernetescrd,ingress-demo-admin-auth@kubernetescrd` → HTTP ได้ **301 ก่อน** (รหัสจึงไม่ถูกส่งบน HTTP)
- บน HTTPS: ไม่มีบัตร **401** + `www-authenticate: Basic realm="traefik"` (ทำให้ browser ขึ้นกล่อง login), บัตรผิด 401, บัตรถูก 200
- `removeHeader: true` ทำให้แอปไม่เห็น header `Authorization` (นับได้ `0`)

### ขั้นที่ 4: stripPrefix และด่านสามชั้น

```bash
kubectl apply -f lab08-middleware/strip.yaml
kubectl -n ingress-demo get ing
sleep 3; curl -sk -o /dev/null -w '%{http_code}\n' https://shop.localhost:30081/admin/orders
curl -sk -u som:meow-admin-123 https://shop.localhost:30081/admin/orders | grep -E '^Name|^GET|X-Forwarded-Prefix'
curl -sk -u som:meow-admin-123 https://shop.localhost:30081/admin | grep -E '^Name|^GET'
curl -sk https://shop.localhost:30081/adminx | grep -E '^Name|^GET'
curl -sk https://shop.localhost:30081/api/x | grep -E '^Name|^GET'
curl -si http://shop.localhost:30080/admin/orders | grep -iE '^HTTP|^location'
```

```text
middleware.traefik.io/strip-admin created
ingress.networking.k8s.io/shop configured
ingress.networking.k8s.io/shop-admin created
NAME         CLASS     HOSTS             ADDRESS     PORTS     AGE
backoffice   traefik   admin.localhost   localhost   80, 443   119s
paths        traefik   paths.localhost   localhost   80        117s
shop         traefik   shop.localhost    localhost   80, 443   2m30s
shop-admin   traefik   shop.localhost    localhost   80, 443   0s
401
Name: admin
GET /orders HTTP/1.1
X-Forwarded-Prefix: /admin
Name: admin
GET / HTTP/1.1
Name: menu
GET /adminx HTTP/1.1
Name: api
GET /api/x HTTP/1.1
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/admin/orders
```

- ป้าย `shop-admin` (ชื่อ host เดียวกับ `shop`) มีสามด่าน: redirect → ตรวจบัตร → ตัด `/admin` แอปจึงเห็น `GET /orders` และรู้คำนำหน้าเดิมจาก `X-Forwarded-Prefix: /admin` ส่วน `/admin` เฉย ๆ กลายเป็น `GET /`
- `/adminx` ไม่เข้ากฎ `/admin` (ทีละท่อน) จึงไป menu ไม่ต้องใช้บัตร ส่วน `/api/x` ยังไป api ตามป้าย `shop`
- แยก `/admin` ไปป้ายอีกแผ่นเพราะ annotation ผูกกับ **ทั้งป้าย** ถ้าใส่ basicAuth ที่ป้าย `shop` หน้าร้านทั้งหมดจะต้องใช้บัตร

ดูลำดับด่านของแต่ละ router จาก dashboard API

```bash
curl -s localhost:30082/api/http/routers | python3 -c 'import json,sys; [print(r["name"].split("@")[0], "|", r.get("middlewares")) for r in json.load(sys.stdin) if r["name"].startswith("websecure-ingress-demo-shop")]'
```

```text
websecure-ingress-demo-shop-admin-shop-localhost-admin | ['ingress-demo-redirect-https@kubernetescrd', 'ingress-demo-admin-auth@kubernetescrd', 'ingress-demo-strip-admin@kubernetescrd']
websecure-ingress-demo-shop-shop-localhost-api | ['ingress-demo-redirect-https@kubernetescrd']
websecure-ingress-demo-shop-shop-localhost | ['ingress-demo-redirect-https@kubernetescrd']
```

<p align="center" id="fig-18">
  <img src="images/18-lab8-results.png" alt="รูปที่ 18 ผล LAB 8" width="900"><br>
  <em><b>รูปที่ 18</b> ผล LAB 8: http → 301 Location https://shop.localhost:30081/..., /admin ไม่มีบัตร 401, บัตรผิด 401, บัตรถูก 200 และแอปเห็น /orders</em>
</p>

### สิ่งที่เห็น

- redirect, basicAuth, stripPrefix ทำได้ด้วย Middleware ของ Traefik (CRD `traefik.io/v1alpha1`) ผูกกับป้ายด้วย annotation `router.middlewares` — **ย้าย controller ต้องเขียนส่วนนี้ใหม่**
- redirect บน kind ต้องใส่ `port: "30081"` (ไม่ใส่ → `Location` ไป 443 `rc=7`)
- ลำดับใน annotation = ลำดับด่าน redirect ต้องมาก่อนตรวจบัตร
- basicAuth อ่าน Secret `kubernetes.io/basic-auth` ได้ตรง ไม่มีบัตร/บัตรผิด 401 บัตรถูก 200

**คำถามชวนคิด**

1. ถ้าใช้ controller อื่น (ไม่ใช่ Traefik) ไฟล์ใน `lab08-middleware/` ส่วนไหนใช้ต่อได้ ส่วนไหนต้องเขียนใหม่
2. basic auth ส่งรหัสเป็น base64 ในทุกคำขอ ทำไมการมี redirect ไป HTTPS ก่อนจึงสำคัญ และงานจริงควรใช้อะไรแทน basic auth สำหรับหน้าแอดมิน

---

## LAB 9: Rolling update ผ่าน Ingress

<p align="center" id="fig-19">
  <img src="images/19-lab9-open.png" alt="รูปที่ 19 LAB 9 rolling update" width="900"><br>
  <em><b>รูปที่ 19</b> LAB 9: วน curl https ผ่าน Ingress ระหว่างเปลี่ยน menu → menu-v2 (readiness + preStop + maxUnavailable: 0) ได้ err=0</em>
</p>

**เป้าหมาย:** วัดว่าเปลี่ยนรุ่น menu ระหว่างที่ลูกค้ายิง HTTPS ผ่าน Ingress ไม่มี error เมื่อมี readinessProbe + preStop + `maxUnavailable: 0` และเทียบกับแบบเปราะที่ไม่มี

**ไฟล์:** `lab09-rolling/loop.sh` (curl HTTPS วน N ครั้ง ค่าเริ่มต้น `https://shop.localhost:30081/` 300 ครั้ง เว้น 0.05 วินาที แล้วนับว่าใครตอบ/error รหัสอะไร ค่าเริ่ม `CURL_OPTS=-k`), `menu-v2.yaml` (เหมือนเดิมแต่ตอบชื่อ `menu-v2`), `menu-fragile.yaml` (ไม่มี readiness/preStop, `maxUnavailable: 1`, ชื่อ `menu-fragile`)

### ขั้นที่ 1: ทดสอบ loop และเปลี่ยนรุ่นระหว่างยิง

🐧 **ใน SSH session ของ k8s-lab** (โฟลเดอร์ `02_LAB`)

```bash
./lab09-rolling/loop.sh https://shop.localhost:30081/ 20
(sleep 2; kubectl apply -f lab09-rolling/menu-v2.yaml) & ./lab09-rolling/loop.sh; wait
kubectl -n ingress-demo rollout status deploy/menu --timeout=60s
```

```text
  menu 20
ok=20 err=0 (ใช้เวลา 1.2 วินาที)
deployment.apps/menu configured
  menu 67
  menu-v2 233
ok=300 err=0 (ใช้เวลา 18.3 วินาที)
deployment "menu" successfully rolled out
```

`( ... ) &` สั่ง apply ไฟล์ใหม่ในพื้นหลังหลัง 2 วินาที ขณะที่ `loop.sh` ยิงอยู่ ผลคือคำตอบเปลี่ยนจาก `menu` เป็น `menu-v2` กลางทาง **โดยไม่มี error สักครั้ง** (`ok=300 err=0`)

### ขั้นที่ 2: rollout restart ระหว่างยิง

```bash
(sleep 2; kubectl -n ingress-demo rollout restart deploy/menu) & ./lab09-rolling/loop.sh; wait
```

```text
deployment.apps/menu restarted
  menu-v2 300
ok=300 err=0 (ใช้เวลา 18.3 วินาที)
```

### ขั้นที่ 3: ลองผิด — menu แบบเปราะ

```bash
kubectl apply -f lab09-rolling/menu-fragile.yaml && kubectl -n ingress-demo rollout status deploy/menu --timeout=90s
sleep 5; (sleep 2; kubectl -n ingress-demo rollout restart deploy/menu) & ./lab09-rolling/loop.sh; wait
```

```text
deployment.apps/menu configured
...
deployment "menu" successfully rolled out
deployment.apps/menu restarted
  menu-fragile 297
  error 000 × 1
  error 502 × 2
ok=297 err=3 (ใช้เวลา 20.3 วินาที)
```

ทำซ้ำอีกสองรอบ (รอ rollout เสร็จและเว้น 5 วินาทีก่อนแต่ละรอบ)

```bash
kubectl -n ingress-demo rollout status deploy/menu --timeout=90s; sleep 5
(sleep 2; kubectl -n ingress-demo rollout restart deploy/menu) & ./lab09-rolling/loop.sh; wait
```

ผลจริงรอบที่สองและสาม

```text
deployment.apps/menu restarted
  menu-fragile 295
  error 000 × 1
  error 502 × 4
ok=295 err=5 (ใช้เวลา 20.2 วินาที)
...
deployment.apps/menu restarted
  menu-fragile 297
  error 000 × 1
  error 502 × 2
ok=297 err=3 (ใช้เวลา 20.3 วินาที)
```

ดู 502 ใน access log ของ Traefik

```bash
kubectl -n traefik logs deploy/traefik --since=60s | grep -E '" 50[0-9] ' | tail -3
```

```text
172.19.0.2 - - [05/Oct/2026:13:17:07 +0000] "GET / HTTP/2.0" 502 11 "-" "-" 992 "websecure-ingress-demo-shop-shop-localhost@kubernetes" "http://10.244.1.12:8080" 0ms
172.19.0.2 - - [05/Oct/2026:13:17:32 +0000] "GET / HTTP/2.0" 502 11 "-" "-" 1288 "websecure-ingress-demo-shop-shop-localhost@kubernetes" "http://10.244.1.13:8080" 1ms
172.19.0.2 - - [05/Oct/2026:13:17:32 +0000] "GET / HTTP/2.0" 502 11 "-" "-" 1289 "websecure-ingress-demo-shop-shop-localhost@kubernetes" "http://10.244.1.13:8080" 0ms
```

<p align="center" id="fig-20">
  <img src="images/20-lab9-contrast.png" alt="รูปที่ 20 LAB 9 เปรียบเทียบแบบเปราะ" width="900"><br>
  <em><b>รูปที่ 20</b> LAB 9 เปรียบเทียบ: เอา readiness/preStop ออก → rollout restart สามรอบได้ 502 Bad Gateway บางครั้งทุกรอบ (err 3–5 ครั้งจาก 300); ใส่กลับ → err=0</em>
</p>

- แบบเปราะได้ error **ทุกรอบ** (3–5 ครั้งจาก 300 ในเครื่องทดลอง): **502** = Traefik ส่งไปที่ IP ของ Pod ที่ปิดไปแล้ว (access log ระบุ IP ปลายทาง) และ **000** = curl ต่อไม่สำเร็จภายใน 2 วินาที
- จำนวน error ขึ้นกับความเร็วเครื่อง **บางรอบอาจเป็น 0** แต่ไม่มีอะไรรับประกัน ส่วนแบบมี readiness + preStop ได้ `err=0` ทุกรอบ
- เหตุผล: Pod เก่าปิดทันทีขณะที่ Traefik ยังไม่ทันลบออกจากรายชื่อ (ไม่มี preStop) และ Pod ใหม่ถูกนับว่า Ready ทันทีที่ process เริ่ม (ไม่มี readinessProbe) บวกกับ `maxUnavailable: 1` ที่ยอมให้บูธพร้อมลดลง

### ขั้นที่ 4: คืนค่า menu

```bash
kubectl apply -f lab02-first/10-apps.yaml | grep menu; kubectl -n ingress-demo rollout status deploy/menu --timeout=90s
sleep 3; ./lab09-rolling/loop.sh https://shop.localhost:30081/ 20
```

```text
deployment.apps/menu configured
service/menu unchanged
...
deployment "menu" successfully rolled out
  menu 20
ok=20 err=0 (ใช้เวลา 1.2 วินาที)
```

### ขั้นที่ 5: เก็บกวาด LAB 1–9 ก่อน LAB 10 (บังคับ)

ป้าย `shop` และ `shop-admin` ของ `ingress-demo` ใช้ชื่อ `shop.localhost` ซ้ำกับร้านใน LAB 10 **ต้องลบ namespace `ingress-demo` ก่อน** (Traefik เก็บไว้)

```bash
time kubectl delete ns ingress-demo
kubectl get ing -A; kubectl get svc -A | grep 3008
ls lab07-tls
```

```text
namespace "ingress-demo" deleted

real	0m27.110s
...
No resources found
traefik       traefik      NodePort    10.96.154.128   <none>        80:30080/TCP,443:30081/TCP,8080:30082/TCP   5m46s
ingress-tls.yaml
tls.crt
tls.key
```

ลบทั้ง namespace ใช้ราว 27 วินาที (Pod รอ preStop 5 วินาที) Ingress, Middleware และ Secret (`som-tls`, `admin-auth`) ของ LAB 2–9 หายไปพร้อมกัน เหลือแค่ Traefik ถือ NodePort ไฟล์ `lab07-tls/tls.crt`, `tls.key` บนดิสก์ยังอยู่ (ลบได้ตามตารางเก็บกวาด)

### สิ่งที่เห็น

- rolling update ผ่าน Ingress ได้ `err=0` เมื่อมี readinessProbe + preStop sleep 5 + `maxUnavailable: 0` (ทั้ง apply รุ่นใหม่และ `rollout restart`)
- แบบเปราะได้ 502/000 บางครั้งทุกรอบ
- `kubectl delete ns ingress-demo` คืนชื่อ `shop.localhost` ให้ร้านใน LAB 10

**คำถามชวนคิด**

1. ทำไม preStop ต้อง "รอ" ทั้งที่ Pod ถูกสั่งปิดแล้ว ใครบ้างที่ต้องรู้ว่า Pod นี้กำลังจะหายไป และรู้ช้ากว่ากันเพราะอะไร
2. ถ้ามี Traefik แค่ 1 replica แล้วเราอัปเกรด Traefik เอง (เช่น patch args ใน LAB 5/7) ลูกค้าจะเจออะไร ต้องตั้งค่าอย่างไรให้ controller เปลี่ยนรุ่นได้โดยไม่สะดุด

---
## LAB 10: LAB สุดท้าย: ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน

<p align="center" id="fig-21">
  <img src="images/21-lab10-open.png" alt="รูปที่ 21 LAB 10 ภาพรวม som-shop-v8" width="900"><br>
  <em><b>รูปที่ 21</b> LAB 10 เปิด: ร้าน som-shop-v8 (คัดลอกจากบท 011) เข้าทาง https://shop.localhost และหลังร้าน admin.localhost ผ่าน Ingress</em>
</p>

**เป้าหมาย:** ย้ายร้านน้องส้มจากบทที่ 11 (NodePort 30080 + nginx HTTPS 30082) มาเข้าทาง **ประตู Ingress เดียว** ด้วยชื่อ `shop.localhost` (หน้าร้าน) และ `admin.localhost` (หลังร้านที่ต้องมีบัตร) ย้าย TLS จาก nginx มาที่ `spec.tls` ของ Ingress บังคับ HTTP → HTTPS เปลี่ยนป้ายร้านเป็นบทที่ 12 และเปลี่ยนรุ่น 1.5 → 1.6 ผ่าน Ingress โดยลูกค้าไม่เจอ error **ข้อมูลในฐานข้อมูลและออเดอร์เดิมต้องอยู่ครบ** ใช้ทุกอย่างที่เรียนมาถึงบทนี้: Deployment + rolling update (บทที่ 7), StatefulSet + PVC (บทที่ 8–9), ConfigMap (บทที่ 10), Secret `tls` และ `basic-auth` (บทที่ 11), Pod Security restricted (บทที่ 4) และ Ingress + Middleware ของ Traefik (บทนี้)

**ไฟล์:** โฟลเดอร์ `som-shop-v8/` ทำงานใน `/workspace/012_kubernetes_ingress/02_LAB/som-shop-v8`

**สิ่งที่ต้องมีก่อน:** LAB 0 (คืนพอร์ต + image 1.5/1.6), LAB 1 (Traefik ติดตั้งแล้ว) และ **LAB 9 ขั้นที่ 5 (ลบ namespace `ingress-demo` แล้ว)**

### 10.1 ภาพรวมและไฟล์

<p align="center" id="fig-22">
  <img src="images/22-lab10-before-after.png" alt="รูปที่ 22 ก่อนและหลังย้ายประตู" width="900"><br>
  <em><b>รูปที่ 22</b> ก่อน/หลัง: บท 011 ใช้ NodePort 30080 + nginx HTTPS 30082; บท 012 ใช้ Ingress เดียว Service som-web เป็น ClusterIP</em>
</p>

| | บทที่ 11 (`som-shop-v7`) | บทที่ 12 (`som-shop-v8`) |
|---|---|---|
| หน้าร้าน HTTP | Service `som-web` NodePort `30080` | Service `som-web` **ClusterIP** + Ingress `som-shop` (`http://shop.localhost:30080` → 301) |
| HTTPS | Deployment `som-https` (nginx) + NodePort `30082` ใบ `CN=shop.som.local` | **`spec.tls` ของ Ingress** (`https://shop.localhost:30081`) ใบใหม่ SAN `shop.localhost`, `admin.localhost`, `localhost` |
| หลังร้าน | ไม่มี | `som-admin` (nginx-unprivileged) ClusterIP + Ingress `som-admin` (`https://admin.localhost:30081`) + basicAuth |
| ป้ายร้าน | `⚓ ท่าเรือ Kubernetes · Secret`, footer `... LAB 011 ...` | `⚓ ท่าเรือ Kubernetes · Ingress`, footer `Next.js + PostgreSQL · Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost` |
| ฐานข้อมูล | `som-db` StatefulSet + PVC `data-som-db-0` + Secret `som-db-secret` | **เหมือนเดิม ไม่แตะ** |

| ไฟล์ใน `som-shop-v8/` | หน้าที่ |
|---|---|
| `k8s/00-namespace.yaml`, `k8s/10-db.yaml` | เหมือนบทที่ 11 ทุกบรรทัด (namespace `som-shop` + `warn: restricted`, ครัว `som-db`) |
| `k8s/15-config.yaml` | ConfigMap `som-web-config` ป้ายร้านบทที่ 12 + `som-announcement` |
| `k8s/20-web.yaml` | Deployment `som-web` 3 บูธ (readinessProbe, preStop 5 วินาที, `maxUnavailable: 0`) + Service **ClusterIP** change-cause `1.5 หน้าร้านผ่าน Ingress` |
| `k8s/40-admin.yaml` | ConfigMap `som-admin-conf` (nginx `listen 8080`, `location = /stats` ส่งต่อไป `som-web.som-shop.svc.cluster.local/api/stats`, หน้า `หลังร้านน้องส้ม (admin)`) + Deployment `som-admin` (`nginxinc/nginx-unprivileged:1.27-alpine` uid 101) + Service ClusterIP `som-admin` port ชื่อ `http` |
| `k8s/50-ingress.yaml` | Middleware `redirect-https` (port `"30081"`), `admin-auth` (Secret `som-admin-auth`, `removeHeader: true`) + Ingress `som-shop` (shop.localhost → `som-web:80`) + Ingress `som-admin` (admin.localhost → `som-admin:http` ผ่าน redirect + ตรวจบัตร) ทั้งสองแผ่นมี `tls` ใช้ Secret `som-tls` |
| `hit.sh` | ยิง HTTPS ผ่าน Ingress ทีละครั้ง ค่าเริ่ม `https://shop.localhost:30081/api/whoami` 60 ครั้ง `-q` = โหมดเงียบสรุปตามเวอร์ชัน ตัวแปร `CURL_OPTS` ค่าเริ่ม `-k` (เช่น `CURL_OPTS="--cacert tls.crt"`) |

### 10.2 จุดเริ่มต้น: ร้านเดิมที่ยังไม่มีประตู

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/012_kubernetes_ingress/02_LAB/som-shop-v8
pwd; ls; ls k8s
kubectl -n som-shop get deploy,sts,svc,secret,ing
curl -s localhost:30080/api/stats; curl -sk https://localhost:30081/api/stats
```

ผลจริง (ร้านจากบทที่ 11 ที่ LAB 0 ลบ Service ไปแล้ว)

```text
/workspace/012_kubernetes_ingress/02_LAB/som-shop-v8
app
hit.sh
k8s
00-namespace.yaml
10-db.yaml
15-config.yaml
20-web.yaml
40-admin.yaml
50-ingress.yaml
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-https   1/1     1            1           8m40s
deployment.apps/som-web     3/3     3            3           8m40s

NAME                      READY   AGE
statefulset.apps/som-db   1/1     8m40s

NAME             TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
service/som-db   ClusterIP   None         <none>        5432/TCP   8m40s

NAME                   TYPE                DATA   AGE
secret/som-db-secret   Opaque              2      8m41s
secret/som-tls         kubernetes.io/tls   2      8m41s
404 page not found
404 page not found
```

ร้านยังมีบูธ ครัว และซองครบ แต่ไม่มี Service ของหน้าร้าน ประตู 30080/30081 เป็นของ Traefik ซึ่งยังไม่มีป้ายของร้าน จึงตอบ 404

> **ถ้าไม่มีร้านจากบทที่ 11** (คลัสเตอร์ใหม่จาก `k8s-up` ใน LAB 0 หรือลบ `som-shop` ไปแล้ว) ให้สร้าง namespace และซองรหัสฐานข้อมูลก่อน (รหัส `meow1234` เป็นค่าตัวอย่างของบทที่ 11) แล้วทำขั้น A ตามปกติ และรอ db/web พร้อมหลังขั้น A
>
> ```bash
> kubectl apply -f k8s/00-namespace.yaml
> kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop
> ```
>
> หลังขั้น A ใช้ `kubectl -n som-shop rollout status sts/som-db --timeout=180s && kubectl -n som-shop rollout status deploy/som-web --timeout=240s` ร้านใหม่จะเริ่มที่ `orders=0` ผลของ `apply` จะเป็น `created` แทน `configured` และคำสั่งลบ `som-https` ในขั้น A จะได้ `NotFound` ซึ่งไม่เป็นไร

### 10.3 ขั้น A: ย้ายประตู — web เป็น ClusterIP และลบ nginx HTTPS

<p align="center" id="fig-23">
  <img src="images/23-lab10-ports-cleanup.png" alt="รูปที่ 23 ขั้น A ย้ายประตู" width="900"><br>
  <em><b>รูปที่ 23</b> ขั้น A: apply 00/10/15/20 ใน k8s/ ของ v8 (som-web → ClusterIP, ConfigMap ป้ายบท 012) และลบ som-https (nginx TLS ของบท 011) — ข้อมูล db และออเดอร์เดิมยังอยู่</em>
</p>

ดูความต่างของ Service ระหว่างบทที่ 11 กับบทนี้ (ถ้ายังมีโฟลเดอร์ `011_kubernetes_secret` ใน container)

```bash
diff <(sed -n '/^kind: Service/,$p' ../../../011_kubernetes_secret/02_LAB/som-shop-v7/k8s/20-web.yaml 2>/dev/null) <(sed -n '/^kind: Service/,$p' k8s/20-web.yaml) || true
```

```text
6c6
<   type: NodePort
---
>   type: ClusterIP
12d11
<       nodePort: 30080
```

apply ไฟล์ 00/10/15/20 **(ห้าม apply ทั้งโฟลเดอร์ `k8s/` ตอนนี้ เพราะ 50-ingress.yaml ต้องมี Secret ของขั้น B–C ก่อน)** แล้วลบ nginx HTTPS ของบทที่ 11

```bash
kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml -f k8s/15-config.yaml -f k8s/20-web.yaml
kubectl -n som-shop delete deploy som-https; kubectl -n som-shop delete cm som-https-conf; kubectl -n som-shop delete svc som-https 2>&1 | tail -1
kubectl -n som-shop get svc; kubectl get svc -A | grep 3008
kubectl -n som-shop get pod
```

```text
namespace/som-shop unchanged
service/som-db unchanged
statefulset.apps/som-db configured
configmap/som-web-config configured
configmap/som-announcement unchanged
deployment.apps/som-web configured
service/som-web created
deployment.apps "som-https" deleted from som-shop namespace
configmap "som-https-conf" deleted from som-shop namespace
Error from server (NotFound): services "som-https" not found
NAME      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
som-db    ClusterIP   None           <none>        5432/TCP   8m40s
som-web   ClusterIP   10.96.198.30   <none>        80/TCP     0s
traefik       traefik      NodePort    10.96.154.128   <none>        80:30080/TCP,443:30081/TCP,8080:30082/TCP   6m11s
NAME                         READY   STATUS        RESTARTS   AGE
som-db-0                     1/1     Running       0          8m40s
som-https-6fdbf5b749-dhcml   1/1     Terminating   0          8m40s
som-web-7948ccf586-7xtk9     1/1     Running       0          8m40s
som-web-7948ccf586-g779k     1/1     Running       0          8m40s
som-web-7948ccf586-rsxk8     1/1     Running       0          8m40s
```

- `service/som-web created` (LAB 0 ลบไปแล้ว ถ้ายังไม่ได้ลบจะเป็น `configured` เปลี่ยน NodePort → ClusterIP ได้เลย) NodePort เหลือแค่ของ Traefik
- Service `som-https` ถูกลบตั้งแต่ LAB 0 จึง `NotFound` ส่วน Deployment และ ConfigMap ของ nginx ถูกลบตอนนี้ (Pod `Terminating`)
- `deployment.apps/som-web configured` เปลี่ยนแค่ annotation change-cause **template ไม่เปลี่ยน Pod เดิมจึงไม่ถูกสร้างใหม่** (AGE เดิม) ป้ายร้านใหม่ใน ConfigMap จึงยังไม่มีผล (จะ `rollout restart` ในขั้น E) `statefulset.apps/som-db configured` เป็นเรื่องปกติ (kubectl เทียบกับค่าตั้งต้นที่ API server เติม) `som-db-0` ไม่ restart

### 10.4 ขั้น B: ใบรับรองใหม่ให้ชื่อตรง

<p align="center" id="fig-24">
  <img src="images/24-lab10-tls-move.png" alt="รูปที่ 24 ขั้น B ใบรับรองใหม่" width="900"><br>
  <em><b>รูปที่ 24</b> ขั้น B: ทำ som-tls ใบใหม่ให้ชื่อตรง (CN เดิม shop.som.local ใช้กับ shop.localhost ไม่ได้) แล้วย้าย TLS จาก nginx มาที่ spec.tls ของ Ingress</em>
</p>

ใบเดิมของบทที่ 11 ออกให้ `shop.som.local`

```bash
kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -subject -ext subjectAltName
```

```text
subject=CN = shop.som.local
X509v3 Subject Alternative Name:
    DNS:shop.som.local, DNS:localhost
```

ชื่อ `shop.localhost` และ `admin.localhost` ไม่อยู่ในใบ ถ้าใช้ใบนี้ curl ที่ตรวจจริงจะล้ม จึงออกใบใหม่ใน `som-shop-v8/` แล้ว **อัปเดต Secret เดิม** ด้วย `--dry-run=client -o yaml | kubectl apply -f -` (บทที่ 11)

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.localhost' -addext 'subjectAltName=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost' 2>&1 | tail -1
kubectl -n som-shop create secret tls som-tls --cert=tls.crt --key=tls.key --dry-run=client -o yaml | kubectl apply -f -
kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -subject -ext subjectAltName
```

```text
-----
Warning: resource secrets/som-tls is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
secret/som-tls configured
subject=CN = shop.localhost
X509v3 Subject Alternative Name:
    DNS:shop.localhost, DNS:admin.localhost, DNS:localhost
```

Warning `missing the kubectl.kubernetes.io/last-applied-configuration` เป็นเรื่องปกติ (Secret เดิมสร้างด้วย `kubectl create`) kubectl เติม annotation ให้เอง ไฟล์ `tls.key`/`tls.crt` ใน `som-shop-v8/` ใช้ต่อกับ `--cacert` ในขั้น D และ **ห้าม commit** (`som-shop-v8/.gitignore` กันไว้แล้ว)

### 10.5 ขั้น C: หลังร้าน และป้าย Ingress

<p align="center" id="fig-25">
  <img src="images/25-lab10-admin.png" alt="รูปที่ 25 ขั้น C หลังร้านและป้าย" width="900"><br>
  <em><b>รูปที่ 25</b> ขั้น C: หลังร้าน som-admin (nginx-unprivileged + ConfigMap หน้า HTML + /stats) ที่ admin.localhost ป้องกันด้วย basicAuth จาก Secret som-admin-auth (รหัสตัวอย่าง)</em>
</p>

สร้างบัตรหลังร้าน (Secret `kubernetes.io/basic-auth`) **รหัส `meow-admin-123` เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น** แล้ว apply หลังร้านและป้าย

```bash
kubectl -n som-shop create secret generic som-admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow-admin-123
kubectl apply -f k8s/40-admin.yaml -f k8s/50-ingress.yaml
kubectl -n som-shop rollout status deploy/som-admin --timeout=120s
kubectl -n som-shop get ing,middleware
kubectl -n som-shop describe ing som-shop | sed -n '/TLS/,$p'
```

```text
secret/som-admin-auth created
configmap/som-admin-conf created
deployment.apps/som-admin created
service/som-admin created
middleware.traefik.io/redirect-https created
middleware.traefik.io/admin-auth created
ingress.networking.k8s.io/som-shop created
ingress.networking.k8s.io/som-admin created
Waiting for deployment "som-admin" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-admin" successfully rolled out
NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   8s
ingress.networking.k8s.io/som-shop    traefik   shop.localhost    localhost   80, 443   8s

NAME                                   AGE
middleware.traefik.io/admin-auth       8s
middleware.traefik.io/redirect-https   8s
TLS:
  som-tls terminates shop.localhost
Rules:
  Host            Path  Backends
  ----            ----  --------
  shop.localhost
                  /   som-web:80 (10.244.2.3:3000,10.244.2.2:3000,10.244.1.2:3000)
Annotations:      traefik.ingress.kubernetes.io/router.middlewares: som-shop-redirect-https@kubernetescrd
Events:           <none>
```

- `som-admin` ใช้ `nginxinc/nginx-unprivileged:1.27-alpine` (uid 101, ฟัง 8080) จึงผ่าน Pod Security restricted **ไม่มี Warning** (ต่างจาก nginx `som-https` ของบทที่ 11) และไม่มีรหัสผ่านอยู่ในแอปเลย ด่านตรวจบัตรอยู่ที่ประตู
- ป้ายสองแผ่น CLASS `traefik` ADDRESS `localhost` PORTS `80, 443` Backends ของ `som-shop` เห็น 3 บูธที่พอร์ต 3000

### 10.6 ขั้น D: ตรวจร้านด้วย curl และ browser

<p align="center" id="fig-26">
  <img src="images/26-lab10-redirect-browser.png" alt="รูปที่ 26 ขั้น D redirect และ browser" width="900"><br>
  <em><b>รูปที่ 26</b> ขั้น D: browser เปิด http://shop.localhost:30080 → 301 → https://shop.localhost:30081 เตือน self-signed → หน้าร้านแสดง footer บท 012 (ทดสอบด้วย Chromium แล้ว)</em>
</p>

**หน้าร้าน:** HTTP ต้องถูกส่งต่อ HTTPS ต้องขายได้และออเดอร์เดิมอยู่ครบ (ทดสอบแบบตรวจใบรับรองจริงด้วย `--cacert tls.crt`)

```bash
sleep 3; curl -si http://shop.localhost:30080/ | grep -iE '^HTTP|^location'
curl -s --cacert tls.crt https://shop.localhost:30081/api/stats
curl -s --cacert tls.crt https://shop.localhost:30081/ | grep -o '<title>[^<]*</title>'
curl -s --cacert tls.crt -XPOST -H "content-type: application/json" -d '{"product_id":4,"qty":1}' https://shop.localhost:30081/api/orders; echo
curl -s --cacert tls.crt https://shop.localhost:30081/api/stats
curl -s --cacert tls.crt -XPOST -H "content-type: application/json" -d '{"productId":4,"qty":1}' https://shop.localhost:30081/api/orders; echo
```

```text
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/
som-web-7948ccf586-7xtk9 1.5 orders=3 products=6
<title>ร้านอาหารแมวน้องส้ม</title>
{"ok":true,"order_id":4,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":59}}
som-web-7948ccf586-rsxk8 1.5 orders=4 products=6
{"ok":false,"error":"ข้อมูลไม่ถูกต้อง"}
```

ออเดอร์เดิม 3 รายการยังอยู่ (ร้านของนักศึกษาที่ทำบทที่ 11 ครบอาจมีจำนวนต่างไป) สั่งผ่าน HTTPS ได้ `order_id` ถัดไป body ต้องใช้ `product_id` (ถ้าพิมพ์ `productId` ได้ `ข้อมูลไม่ถูกต้อง`)

**หลังร้าน:** redirect → ตรวจบัตร → หน้าหลังร้าน และ `/stats` ที่ nginx ส่งต่อไปถามหน้าร้านภายในคลัสเตอร์

```bash
curl -si http://admin.localhost:30080/ | grep -iE '^HTTP|^location'
curl -s --cacert tls.crt -o /dev/null -w '%{http_code}\n' https://admin.localhost:30081/
curl -s --cacert tls.crt -u som:meow-admin-123 https://admin.localhost:30081/ | grep -o '<h1>.*</h1>'
curl -s --cacert tls.crt -u som:meow-admin-123 https://admin.localhost:30081/stats; echo
curl -s --cacert tls.crt -o /dev/null -w '%{http_code}\n' -u som:wrong https://admin.localhost:30081/stats
```

```text
HTTP/1.1 301 Moved Permanently
Location: https://admin.localhost:30081/
401
<h1>หลังร้านน้องส้ม (admin)</h1>
som-web-7948ccf586-g779k 1.5 orders=4 products=6

401
```

**ประตูเดิมของร้านไม่มีแล้ว และชื่ออื่นได้ 404**

```bash
curl -s localhost:30080/api/stats; curl -s -o /dev/null -w '%{http_code}\n' http://other.localhost:30080/; curl -sk -o /dev/null -w '%{http_code}\n' https://other.localhost:30081/
```

```text
404 page not found
404
404
```

**HTTPS กับ `--resolve` และ `Host` header:** ทางสำรองสำหรับโปรแกรมที่แปลง `*.localhost` ไม่ได้

```bash
curl -s --cacert tls.crt --resolve shop.localhost:30081:127.0.0.1 https://shop.localhost:30081/api/whoami; echo
curl -ski -H 'Host: shop.localhost' https://localhost:30081/api/whoami | grep -iE '^HTTP|^location'
curl -sk -H 'Host: shop.localhost:30081' https://localhost:30081/api/whoami; echo
```

```text
som-web-7948ccf586-7xtk9 1.5

HTTP/2 301
location: https://shop.localhost:30081/api/whoami
som-web-7948ccf586-rsxk8 1.5

```

`--resolve` ได้ผลถูกต้องทันที ส่วน `-H 'Host: shop.localhost'` (ไม่มีพอร์ต) บน HTTPS ได้ **301 วนกลับไป `:30081`** เพราะ Middleware `redirectScheme` เทียบพอร์ตใน `Host` (ไม่มีพอร์ต = 443 ≠ 30081) ต้องใส่ `Host: shop.localhost:30081` ให้ตรงพอร์ตจึงได้หน้าร้าน ด้วยเหตุเดียวกัน **ถ้าเปิดร้านผ่าน tunnel ที่ใช้พอร์ตอื่น (เช่น `ssh -L 8443:localhost:30081`) จะถูกส่งกลับไป 30081 ทุกครั้ง** ให้เปิดด้วยพอร์ต 30080/30081 ตรงเสมอ

**hit.sh แบบ HTTPS:** ยิงผ่าน Ingress แล้วนับว่าไปตกบูธไหน

```bash
./hit.sh
CURL_OPTS="--cacert tls.crt" ./hit.sh https://shop.localhost:30081/api/whoami 12
CURL_OPTS="-k --resolve shop.localhost:30081:127.0.0.1" ./hit.sh https://shop.localhost:30081/api/whoami 6
CURL_OPTS=" " ./hit.sh https://shop.localhost:30081/api/whoami 2
kubectl -n traefik logs deploy/traefik --tail=2
```

```text
จำนวน  Pod  เวอร์ชัน
     20 som-web-7948ccf586-7xtk9 1.5
     20 som-web-7948ccf586-g779k 1.5
     20 som-web-7948ccf586-rsxk8 1.5
ok=60 err=0 (ใช้เวลา 6.7 วินาที)
จำนวน  Pod  เวอร์ชัน
      4 som-web-7948ccf586-7xtk9 1.5
      4 som-web-7948ccf586-g779k 1.5
      4 som-web-7948ccf586-rsxk8 1.5
ok=12 err=0 (ใช้เวลา 1.3 วินาที)
จำนวน  Pod  เวอร์ชัน
      2 som-web-7948ccf586-7xtk9 1.5
      2 som-web-7948ccf586-g779k 1.5
      2 som-web-7948ccf586-rsxk8 1.5
ok=6 err=0 (ใช้เวลา 0.7 วินาที)
ข้อความ error:
      2
      2 More details here: https://curl.se/docs/sslcerts.html
      2 curl failed to verify the legitimacy of the server and therefore could not
      2 curl: (60) SSL certificate problem: self-signed certificate
      2 establish a secure connection to it. To learn more about this situation and
      2 how to fix it, please visit the web page mentioned above.
ช่วงที่มี err: 0.1 วินาที
ok=0 err=2 (ใช้เวลา 0.2 วินาที)
172.19.0.2 - - [05/Oct/2026:13:19:16 +0000] "GET /api/whoami HTTP/2.0" 200 29 "-" "-" 1658 "websecure-som-shop-som-shop-shop-localhost@kubernetes" "http://10.244.1.2:3000" 2ms
172.19.0.2 - - [05/Oct/2026:13:19:16 +0000] "GET /api/whoami HTTP/2.0" 200 29 "-" "-" 1659 "websecure-som-shop-som-shop-shop-localhost@kubernetes" "http://10.244.2.2:3000" 2ms
```

Traefik กระจายให้ 3 บูธเท่า ๆ กัน `CURL_OPTS=" "` (ไม่ใส่ `-k` และไม่ใส่ `--cacert`) ได้ `curl: (60)` ทุกครั้ง access log บอกว่าคำขอมาทาง router `websecure-som-shop-...` (HTTP/2 บนประตู HTTPS) ไปที่ IP ของ Pod พอร์ต 3000

**เปิดร้านจาก browser** 🌐 **บนเครื่องนักศึกษา**

1. เปิด `http://shop.localhost:30080` → browser ถูกส่งต่อไป `https://shop.localhost:30081/` และเจอหน้าเตือนใบรับรอง กด Advanced → Proceed (เฉพาะใน LAB)
2. เห็นหน้าร้าน หัวเว็บ `⚓ ท่าเรือ Kubernetes · Ingress` (หลังขั้น E) และ footer บทที่ 12
3. เปิด `https://admin.localhost:30081/` → กล่อง login กด Cancel จะได้ `401 Unauthorized` แล้วเปิดใหม่ใส่ `som` / `meow-admin-123` → หน้า `หลังร้านน้องส้ม (admin)` คลิก "ดูยอดออเดอร์" (`/stats`)
4. เปิด `http://other.localhost:30080/` → `404 page not found`
5. เปิด `http://localhost:30082/dashboard/` → dashboard ของ Traefik

ภาพหน้าจอจริงจากการทดลองด้านล่างถ่ายด้วย Chromium บน Linux โดยใช้ URL เดียวกับที่นักศึกษาพิมพ์ (`shop.localhost:30080/30081`, `admin.localhost:30081`, `other.localhost:30080`, `localhost:30082`) ถ่ายหลังจบขั้น E (ร้านเป็นรุ่น 1.6 และมีออเดอร์ 4 รายการ) ผลตรวจอัตโนมัติของ Chromium รอบเดียวกัน

```text
shop: final url=https://shop.localhost:30081/ status=200 title=ร้านอาหารแมวน้องส้ม chain=['https://shop.localhost:30081/']
shop redirect chain (ล่าสุดก่อน): ['https://shop.localhost:30081/', 'http://shop.localhost:30080/']
footer: 🐱 เสิร์ฟโดย Pod: som-web-bd5bb7d66-4cm5b | Next.js + PostgreSQL · Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost
admin no auth: 401
admin with auth: https://admin.localhost:30081/ 200 h1=หลังร้านน้องส้ม (admin)
admin /stats: 200 som-web-bd5bb7d66-4cm5b 1.6 orders=4 products=6
other: 404 404 page not found
dashboard: 200 title=Dashboard - Traefik Proxy
```

<p align="center" id="fig-27">
  <img src="images/screenshots/20261005_2035_lab10ing_01-https-selfsigned-warning.png" alt="รูปที่ 27 ภาพหน้าจอจริง หน้าเตือนใบรับรอง self-signed" width="700"><br>
  <em><b>รูปที่ 27</b> ภาพหน้าจอจริงจากการทดลอง: เปิด https://shop.localhost:30081 ครั้งแรก browser เตือน &quot;Your connection is not private&quot; NET::ERR_CERT_AUTHORITY_INVALID เพราะใบรับรองเป็น self-signed (ข้อความในภาพแสดงที่อยู่ของเครื่องทดลอง บนเครื่องนักศึกษาจะเห็นเป็น shop.localhost) — กด Advanced → Proceed เฉพาะใน LAB</em>
</p>

<p align="center" id="fig-28">
  <img src="images/screenshots/20261005_2035_lab10ing_02-shop-via-ingress-https.png" alt="รูปที่ 28 ภาพหน้าจอจริง หน้าร้านผ่าน Ingress HTTPS" width="700"><br>
  <em><b>รูปที่ 28</b> ภาพหน้าจอจริงจากการทดลอง: http://shop.localhost:30080 ถูกส่งต่อ (301) ไป https://shop.localhost:30081 หน้าร้านเวอร์ชัน 1.6 หัวเว็บ &quot;⚓ ท่าเรือ Kubernetes · Ingress&quot; ออเดอร์ทั้งหมด 4 เสิร์ฟโดย Pod som-web-bd5bb7d66-jxpr7 — ออเดอร์เดิมจากบทที่ 11 อยู่ครบ</em>
</p>

<p align="center" id="fig-29">
  <img src="images/screenshots/20261005_2035_lab10ing_03-admin-401-no-login.png" alt="รูปที่ 29 ภาพหน้าจอจริง หลังร้าน 401 เมื่อไม่ login" width="700"><br>
  <em><b>รูปที่ 29</b> ภาพหน้าจอจริงจากการทดลอง: https://admin.localhost:30081 โดยไม่ใส่บัตร ได้ 401 Unauthorized จาก Middleware basicAuth ของ Traefik (แอปหลังร้านไม่ได้รับคำขอนี้เลย)</em>
</p>

<p align="center" id="fig-30">
  <img src="images/screenshots/20261005_2035_lab10ing_04-admin-200-after-login.png" alt="รูปที่ 30 ภาพหน้าจอจริง หลังร้านหลัง login" width="700"><br>
  <em><b>รูปที่ 30</b> ภาพหน้าจอจริงจากการทดลอง: login ด้วยบัตรตัวอย่าง som / meow-admin-123 แล้วได้หน้า &quot;หลังร้านน้องส้ม (admin)&quot; พร้อมลิงก์ &quot;ดูยอดออเดอร์&quot; (/stats)</em>
</p>

<p align="center" id="fig-31">
  <img src="images/screenshots/20261005_2035_lab10ing_05-unknown-host-404.png" alt="รูปที่ 31 ภาพหน้าจอจริง ชื่อที่ไม่มีป้าย 404" width="700"><br>
  <em><b>รูปที่ 31</b> ภาพหน้าจอจริงจากการทดลอง: http://other.localhost:30080 ไม่มีป้ายใดรับชื่อนี้ Traefik ตอบ 404 page not found</em>
</p>

<p align="center" id="fig-32">
  <img src="images/screenshots/20261005_2035_lab10ing_06-traefik-dashboard.png" alt="รูปที่ 32 ภาพหน้าจอจริง Traefik dashboard" width="700"><br>
  <em><b>รูปที่ 32</b> ภาพหน้าจอจริงจากการทดลอง: Traefik dashboard ที่ http://localhost:30082/dashboard/ (Traefik 3.7.13) เห็น entrypoints traefik :8080, web :8000, websecure :8443 และ HTTP Routers 7, Services 6, Middlewares 4 ไม่มี Warning/Error</em>
</p>

dashboard นับ router ได้ 7 ตัว ตรวจจาก API ได้ว่าเป็นของร้าน 4 ตัว (ป้ายละ 2 ตัวสำหรับ `web` และ `websecure`) และของ Traefik เอง 3 ตัว

```bash
curl -s localhost:30082/api/http/routers | python3 -c 'import json,sys; [print(r["name"], r.get("middlewares","")) for r in json.load(sys.stdin)]'
```

```text
api@internal
dashboard@internal ['dashboard_redirect@internal', 'dashboard_stripprefix@internal']
ping@internal
som-shop-som-admin-admin-localhost@kubernetes ['som-shop-redirect-https@kubernetescrd', 'som-shop-admin-auth@kubernetescrd']
som-shop-som-shop-shop-localhost@kubernetes ['som-shop-redirect-https@kubernetescrd']
websecure-som-shop-som-admin-admin-localhost@kubernetes ['som-shop-redirect-https@kubernetescrd', 'som-shop-admin-auth@kubernetescrd']
websecure-som-shop-som-shop-shop-localhost@kubernetes ['som-shop-redirect-https@kubernetescrd']
```

Middlewares 4 ตัวบน dashboard คือ `som-shop-redirect-https`, `som-shop-admin-auth` และสองตัวภายในของ dashboard

### 10.7 ขั้น E: ป้ายบทที่ 12 และ rolling update ผ่าน Ingress

<p align="center" id="fig-33">
  <img src="images/27-lab10-rolling.png" alt="รูปที่ 33 ขั้น E rolling update ผ่าน Ingress" width="900"><br>
  <em><b>รูปที่ 33</b> ขั้น E: hit.sh ยิง https ผ่าน Ingress ระหว่าง rollout restart และ set image 1.5 → 1.6 ได้ err=0 ทั้งสองรอบ, rollout history มี change-cause</em>
</p>

ป้ายร้านใน ConfigMap ใหม่ยังไม่มีผล เพราะ env จาก `envFrom` อ่านครั้งเดียวตอน container เริ่ม (บทที่ 10)

```bash
curl -sk https://shop.localhost:30081/ | grep -o 'Kubernetes LAB 01[0-9][^<]*' | head -1
```

```text
Kubernetes LAB 011 · รหัส DB อยู่ใน Secret som-db-secret
```

บันทึกเหตุผลลงสมุดรุ่น แล้ว `rollout restart` **ระหว่างที่ `hit.sh` ยิง HTTPS ผ่าน Ingress** (`-q` พิมพ์ `.` เมื่อสำเร็จ `x` เมื่อล้ม)

```bash
kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.5 หน้าร้านผ่าน Ingress" --overwrite
(sleep 2; kubectl -n som-shop rollout restart deploy/som-web) & ./hit.sh -q https://shop.localhost:30081/api/whoami 250 0.05; wait
kubectl -n som-shop rollout status deploy/som-web --timeout=120s
curl -sk https://shop.localhost:30081/ | grep -o 'Kubernetes LAB 01[0-9][^<]*' | head -1
```

```text
deployment.apps/som-web annotated
..................................deployment.apps/som-web restarted
........................................................................................................................................................................................................................
จำนวน  Pod  เวอร์ชัน
    250 1.5 (เวอร์ชัน)
ok=250 err=0 (ใช้เวลา 15.4 วินาที)
...
deployment "som-web" successfully rolled out
Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost
```

ไม่มี `x` เลย (`ok=250 err=0`) และ footer เป็นบทที่ 12 แล้ว (ถ้ายังเห็น `LAB 011` อาจเป็น Pod เก่าที่ยังตอบช่วง preStop รอ 10 วินาทีแล้วลองใหม่) จากนั้นเปลี่ยนรุ่นเป็น 1.6

```bash
(sleep 2; kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.6 && kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.6 ผ่าน Ingress" --overwrite) & ./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.05; wait
kubectl -n som-shop rollout status deploy/som-web --timeout=120s
./hit.sh https://shop.localhost:30081/api/whoami 30
kubectl -n som-shop rollout history deploy/som-web
curl -sk https://shop.localhost:30081/api/stats; curl -sk -u som:meow-admin-123 https://admin.localhost:30081/stats; echo
```

```text
.................................deployment.apps/som-web image updated
.deployment.apps/som-web annotated
..........................................................................................................................................................................................................................................................................
จำนวน  Pod  เวอร์ชัน
    213 1.5 (เวอร์ชัน)
     87 1.6 (เวอร์ชัน)
ok=300 err=0 (ใช้เวลา 18.5 วินาที)
...
deployment "som-web" successfully rolled out
จำนวน  Pod  เวอร์ชัน
      4 som-web-7754cd544c-dxnnb 1.5
      9 som-web-bd5bb7d66-4cm5b 1.6
      8 som-web-bd5bb7d66-h85nl 1.6
      9 som-web-bd5bb7d66-jxpr7 1.6
ok=30 err=0 (ใช้เวลา 3.4 วินาที)
deployment.apps/som-web
REVISION  CHANGE-CAUSE
1         1.5 หน้าร้านผ่าน Ingress
2         1.5 หน้าร้านผ่าน Ingress
3         1.6 ผ่าน Ingress

som-web-bd5bb7d66-h85nl 1.6 orders=4 products=6
som-web-bd5bb7d66-h85nl 1.6 orders=4 products=6
```

- เปลี่ยนรุ่น 1.5 → 1.6 ผ่าน Ingress ได้ `ok=300 err=0` (สัดส่วน 1.5/1.6 ขึ้นกับจังหวะ) เพราะ `som-web` มี readinessProbe + preStop 5 วินาที + `maxUnavailable: 0` ตั้งแต่บทที่ 7
- `./hit.sh` ทันทีหลัง rollout เสร็จยังเห็น Pod 1.5 ตอบ 4 ครั้ง คือ Pod เก่าที่กำลังปิดอย่างสุภาพในช่วง preStop (ไม่ใช่ error)
- history 3 แถว: revision 1–2 คือรุ่นก่อน/หลัง restart (change-cause เดิม) revision 3 คือ 1.6
- ออเดอร์ยังเป็น 4 ทั้งหน้าร้านและหลังร้าน

### 10.8 ขั้น F: ตรวจรับร้านและปิดบท

<p align="center" id="fig-34">
  <img src="images/28-lab10-checklist.png" alt="รูปที่ 34 ตรวจรับร้าน" width="900"><br>
  <em><b>รูปที่ 34</b> ตรวจรับร้าน: http → https, shop.localhost ขายได้, admin.localhost ต้องมีบัตร, NodePort เดิมของร้านไม่มีแล้ว, rolling update err=0</em>
</p>

ตรวจสภาพสุดท้าย

```bash
kubectl get svc -A | grep -E 'NodePort|som-'
kubectl -n som-shop get deploy,sts,pod,svc,ing,middleware,secret,pvc
```

```text
som-shop      som-admin    ClusterIP   10.96.126.248   <none>        80/TCP                                      3m20s
som-shop      som-db       ClusterIP   None            <none>        5432/TCP                                    12m
som-shop      som-web      ClusterIP   10.96.198.30    <none>        80/TCP                                      3m21s
traefik       traefik      NodePort    10.96.154.128   <none>        80:30080/TCP,443:30081/TCP,8080:30082/TCP   9m32s
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-admin   1/1     1            1           3m20s
deployment.apps/som-web     3/3     3            3           12m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     12m

NAME                             READY   STATUS    RESTARTS   AGE
pod/som-admin-5f75ddc94b-zlmjn   1/1     Running   0          3m20s
pod/som-db-0                     1/1     Running   0          12m
pod/som-web-bd5bb7d66-4cm5b      1/1     Running   0          2m14s
pod/som-web-bd5bb7d66-h85nl      1/1     Running   0          2m8s
pod/som-web-bd5bb7d66-jxpr7      1/1     Running   0          2m2s

NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/som-admin   ClusterIP   10.96.126.248   <none>        80/TCP     3m20s
service/som-db      ClusterIP   None            <none>        5432/TCP   12m
service/som-web     ClusterIP   10.96.198.30    <none>        80/TCP     3m21s

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   3m20s
ingress.networking.k8s.io/som-shop    traefik   shop.localhost    localhost   80, 443   3m20s

NAME                                   AGE
middleware.traefik.io/admin-auth       3m20s
middleware.traefik.io/redirect-https   3m20s

NAME                    TYPE                       DATA   AGE
secret/som-admin-auth   kubernetes.io/basic-auth   2      3m21s
secret/som-db-secret    Opaque                     2      12m
secret/som-tls          kubernetes.io/tls          2      12m

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-025e80a5-8f0a-47c6-8b9e-d82e1c94ada8   1Gi        RWO            standard       <unset>                 12m
```

| ข้อตรวจรับ | ผลจริง |
|---|---|
| HTTP → HTTPS | `http://shop.localhost:30080/` → `301` `Location: https://shop.localhost:30081/` |
| หน้าร้านขายได้ผ่าน HTTPS (ตรวจใบจริง) | `--cacert tls.crt` สั่งได้ `order_id 4`, `orders=4` |
| หลังร้านต้องมีบัตร | ไม่มีบัตร/บัตรผิด `401`, บัตรถูก `200` `หลังร้านน้องส้ม (admin)` + `/stats` |
| ไม่มี NodePort ของร้านแล้ว | `som-web`, `som-admin` ClusterIP NodePort มีแค่ `traefik`; `localhost:30080/api/stats` → `404` |
| ข้อมูลไม่หาย | `som-db-0` + PVC `data-som-db-0` เดิม ออเดอร์เดิมอยู่ครบ |
| rolling update ผ่าน Ingress | restart `ok=250 err=0`, set image 1.6 `ok=300 err=0` |
| ป้ายบทที่ 12 | footer `Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost` |

<p align="center" id="fig-35">
  <img src="images/29-lab10-wrap-up.png" alt="รูปที่ 35 ปิดบท ปัญหาที่ยังเหลือ" width="900"><br>
  <em><b>รูปที่ 35</b> ปิดบท: ร้านคนเยอะขึ้นต้องเพิ่มบูธอัตโนมัติ (HPA), ติดตั้ง controller/ร้านเป็นแพ็กเกจ (Helm), และอาคารผู้โดยสารรุ่นใหม่ (Gateway API)</em>
</p>

ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อแล้ว แต่ยังเหลือโจทย์ให้บทถัดไป

- **ร้านคนแน่นต้องเพิ่มบูธอัตโนมัติ** — `replicas: 3` ตายตัว (บทถัดไป: **HPA** เพิ่ม/ลดบูธตามโหลด และ Ingress จะส่งลูกค้าให้บูธใหม่ที่ Ready เอง)
- **ติดตั้ง controller และร้านหลายไฟล์ต้องทำตามลำดับเอง** — CRD → `00-traefik.yaml` → Secret 3 ซอง → `k8s/00`–`50` และพอร์ต `30081` เขียนซ้ำหลายไฟล์ (บทถัดไป: **Helm** ติดตั้ง Traefik จาก chart และแพ็กร้านเป็นแพ็กเกจเดียว)
- **ข้อจำกัดของ Ingress** — redirect/auth ผูกกับ Middleware ของ Traefik และทำ canary แบบแบ่งน้ำหนักไม่ได้ (**Gateway API** — ลองได้เลยใน [LAB เสริม](#lab-เสริม-ลองชิม-gateway-api))

**คำถามท้าย LAB 10**

1. ทำไมขั้น A จึง apply แค่ไฟล์ 00/10/15/20 ไม่ apply ทั้งโฟลเดอร์ `k8s/` และถ้า apply `k8s/` ของบทที่ 11 ทับจะเกิดอะไรกับ dashboard ของ Traefik
2. ทำไมต้องออกใบรับรองใหม่ทั้งที่ Secret `som-tls` มีอยู่แล้ว ถ้าใช้ใบเดิม `CN=shop.som.local` ต่อ curl แบบ `--cacert` และ browser จะเป็นอย่างไร
3. หลังร้าน `som-admin` ไม่มีรหัสผ่านอยู่ในแอปเลย ใครเป็นคนตรวจบัตร และ `removeHeader: true` ช่วยอะไร
4. `-H 'Host: shop.localhost'` บน HTTPS ได้ 301 แต่บน HTTP (LAB 2) ใช้ได้ปกติ ทำไมต่างกัน
5. ทำไม `apply` ConfigMap ป้ายใหม่ในขั้น A แล้วหน้าเว็บยังเป็นบทที่ 11 จนกว่าจะ `rollout restart` และทำไมการ restart นั้นจึงไม่ทำให้ลูกค้าเจอ error
6. ถ้าร้านนี้ขึ้นระบบจริงบนคลาวด์ ต้องเปลี่ยนอะไรบ้างใน `50-ingress.yaml` และ Service ของ Traefik (คิดถึงพอร์ต 80/443, ใบรับรองจาก CA จริง และ dashboard)

---

## LAB เสริม: ลองชิม Gateway API

<p align="center" id="fig-36">
  <img src="images/30-labx-gateway-open.png" alt="รูปที่ 36 LAB เสริม Gateway API" width="900"><br>
  <em><b>รูปที่ 36</b> LAB เสริม: ติดตั้ง Gateway API CRD v1.6.2 + เปิด --providers.kubernetesgateway แล้วสร้าง GatewayClass/Gateway/HTTPRoute แบ่งน้ำหนัก 90/10</em>
</p>

**เป้าหมาย:** ติดตั้ง CRD ของ Gateway API v1.6.2 เปิด provider Gateway API ของ Traefik แล้วสร้าง GatewayClass → Gateway → HTTPRoute ที่แบ่งน้ำหนัก 90/10 ระหว่าง `som-web` และ `som-admin` (สิ่งที่ Ingress มาตรฐานทำไม่ได้) แล้วคืนสภาพให้เหมือนท้าย LAB 10

**ไฟล์:** `labx-gateway/gateway-rbac.yml` (ClusterRole/Binding อ่าน Gateway API ให้ ServiceAccount `traefik/traefik` ต้นแบบจาก Traefik v3.7.13), `labx-gateway/60-gateway.yaml` (GatewayClass `traefik`, Gateway `harbor` listener HTTP `port: 8000` hostname `gw.localhost`, HTTPRoute `canary` weight 90/10) ทำในโฟลเดอร์ `02_LAB` ต่อจาก LAB 10 (ร้านต้องเปิดอยู่) **ต้องมีอินเทอร์เน็ต** (ดาวน์โหลด CRD จาก GitHub)

### ขั้นที่ 1: CRD, RBAC และเปิด provider

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/012_kubernetes_ingress/02_LAB
time kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.2/standard-install.yaml
kubectl get crd | grep gateway.networking.k8s.io
kubectl apply -f labx-gateway/gateway-rbac.yml
kubectl -n traefik patch deploy traefik --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--providers.kubernetesgateway=true"}]'
kubectl -n traefik rollout status deploy/traefik --timeout=120s
```

```text
customresourcedefinition.apiextensions.k8s.io/backendtlspolicies.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/gatewayclasses.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/gateways.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/grpcroutes.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/httproutes.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/listenersets.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/referencegrants.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/tcproutes.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/tlsroutes.gateway.networking.k8s.io serverside-applied
customresourcedefinition.apiextensions.k8s.io/udproutes.gateway.networking.k8s.io serverside-applied
validatingadmissionpolicy.admissionregistration.k8s.io/safe-upgrades.gateway.networking.k8s.io serverside-applied
validatingadmissionpolicybinding.admissionregistration.k8s.io/safe-upgrades.gateway.networking.k8s.io serverside-applied

real	0m0.971s
...
gatewayclasses.gateway.networking.k8s.io       Cluster      v1(storage),v1beta1   2026-10-05T13:20:48Z
gateways.gateway.networking.k8s.io             Namespaced   v1(storage),v1beta1   2026-10-05T13:20:48Z
httproutes.gateway.networking.k8s.io           Namespaced   v1(storage),v1beta1   2026-10-05T13:20:48Z
...
clusterrole.rbac.authorization.k8s.io/gateway-role created
clusterrolebinding.rbac.authorization.k8s.io/gateway-controller created
deployment.apps/traefik patched
...
deployment "traefik" successfully rolled out
```

Gateway API ไม่ได้ติดมากับ Kubernetes ต้องติดตั้ง CRD ชุด standard (10 CRD + ValidatingAdmissionPolicy `safe-upgrades`) ใช้ `--server-side` ตามคำแนะนำของโครงการ `GatewayClass` เป็น cluster-scoped ส่วน `Gateway`/`HTTPRoute` เป็น namespaced

### ขั้นที่ 2: GatewayClass, Gateway และ HTTPRoute

```bash
kubectl apply -f labx-gateway/60-gateway.yaml
sleep 5; kubectl get gatewayclass; kubectl -n som-shop get gateway,httproute
kubectl -n som-shop get gateway harbor -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}'; echo
```

```text
gatewayclass.gateway.networking.k8s.io/traefik created
gateway.gateway.networking.k8s.io/harbor created
httproute.gateway.networking.k8s.io/canary created
NAME      CONTROLLER                      ACCEPTED   AGE
traefik   traefik.io/gateway-controller   True       5s
NAME                                       CLASS     ADDRESS   PROGRAMMED   AGE
gateway.gateway.networking.k8s.io/harbor   traefik             True         5s

NAME                                         HOSTNAMES          AGE
httproute.gateway.networking.k8s.io/canary   ["gw.localhost"]   5s
Accepted=True Programmed=True
```

GatewayClass `ACCEPTED True` (Traefik รับเป็นเจ้าของ) Gateway `PROGRAMMED True` (ประตูพร้อม listener `port: 8000` คือ entrypoint `web` = NodePort 30080)

### ขั้นที่ 3: แบ่งน้ำหนัก 90/10

```bash
for i in $(seq 40); do curl -s http://gw.localhost:30080/stats -o /dev/null -w '%{http_code} '; done; echo
for i in $(seq 40); do curl -s http://gw.localhost:30080/api/whoami | grep -q som-web && echo som-web || echo som-admin; done | sort | uniq -c
for i in $(seq 40); do curl -s http://gw.localhost:30080/api/whoami | grep -q som-web && echo som-web || echo som-admin; done | sort | uniq -c
curl -sk https://shop.localhost:30081/api/stats
```

```text
404 404 404 404 404 404 404 404 200 404 404 404 404 404 404 404 404 404 404 200 404 404 404 404 404 404 404 404 404 200 404 404 404 404 404 404 404 404 200 404
      4 som-admin
     36 som-web
      4 som-admin
     36 som-web
som-web-bd5bb7d66-4cm5b 1.6 orders=4 products=6
```

<p align="center" id="fig-37">
  <img src="images/31-labx-gateway-result.png" alt="รูปที่ 37 ผล LAB เสริม" width="900"><br>
  <em><b>รูปที่ 37</b> ผล LAB เสริม: GatewayClass ACCEPTED True, Gateway PROGRAMMED True, ยิง 40 ครั้งได้ร้าน 36 / หลังร้าน 4 (ใกล้ 90/10)</em>
</p>

- `/stats` มีเฉพาะที่ `som-admin` (หน้าร้านตอบ 404) จึงเห็น 200 แค่ 4 จาก 40 ครั้ง = คำขอที่ถูกส่งไปหลังร้าน
- `/api/whoami` นับได้ `som-web` 36 : `som-admin` 4 ทั้งสองรอบ ใกล้ 90/10 **การแบ่งเป็นการสุ่ม เครื่องนักศึกษาอาจได้ตัวเลขต่างจากนี้เล็กน้อย**
- ทั้งหมดนี้ทำผ่าน `HTTPRoute` มาตรฐาน ไม่ต้องใช้ annotation ของ controller และ Ingress ของร้าน (`shop.localhost`) ยังทำงานต่อคู่กันได้

ระหว่าง Traefik restart อาจเห็น log ชั่วครู่ (หายเองภายในวินาที ไม่กระทบร้าน)

```text
2026-10-05T13:20:49Z ERR error="middleware \"som-shop-admin-auth@kubernetescrd\" does not exist" entryPointName=web routerName=som-shop-som-admin-admin-localhost@kubernetes
2026-10-05T13:20:49Z ERR error="middleware \"som-shop-redirect-https@kubernetescrd\" does not exist" entryPointName=web routerName=som-shop-som-shop-shop-localhost@kubernetes
```

### ขั้นที่ 4: คืนสภาพให้เหมือนท้าย LAB 10

```bash
kubectl delete -f labx-gateway/60-gateway.yaml
kubectl apply -f ingress-controller/00-traefik.yaml | grep configured; kubectl -n traefik rollout status deploy/traefik --timeout=120s
kubectl delete -f labx-gateway/gateway-rbac.yml
kubectl delete -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.2/standard-install.yaml | tail -3
kubectl get crd | grep -c gateway.networking.k8s.io
sleep 20; kubectl -n traefik logs deploy/traefik --since=15s | grep -cE 'ERR'
curl -si http://shop.localhost:30080/ | grep -iE '^HTTP|^location'; curl -s --cacert som-shop-v8/tls.crt -o /dev/null -w '%{http_code}\n' https://admin.localhost:30081/; curl -s --cacert som-shop-v8/tls.crt -o /dev/null -w '%{http_code}\n' -u som:meow-admin-123 https://admin.localhost:30081/
curl -s -o /dev/null -w '%{http_code}\n' http://gw.localhost:30080/
```

```text
gatewayclass.gateway.networking.k8s.io "traefik" deleted
gateway.gateway.networking.k8s.io "harbor" deleted from som-shop namespace
httproute.gateway.networking.k8s.io "canary" deleted from som-shop namespace
deployment.apps/traefik configured
...
deployment "traefik" successfully rolled out
clusterrole.rbac.authorization.k8s.io "gateway-role" deleted
clusterrolebinding.rbac.authorization.k8s.io "gateway-controller" deleted
customresourcedefinition.apiextensions.k8s.io "udproutes.gateway.networking.k8s.io" deleted
validatingadmissionpolicy.admissionregistration.k8s.io "safe-upgrades.gateway.networking.k8s.io" deleted
validatingadmissionpolicybinding.admissionregistration.k8s.io "safe-upgrades.gateway.networking.k8s.io" deleted
0
0
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/
401
200
404
```

`kubectl apply -f ingress-controller/00-traefik.yaml` เอา arg `--providers.kubernetesgateway=true` ออก CRD ของ Gateway API เหลือ 0 ร้านยังมี redirect/auth ครบ และ `gw.localhost` กลับเป็น 404 (ถ้าอยากเก็บ Gateway API ไว้ศึกษาต่อจะข้ามขั้นนี้ก็ได้ แต่ต้องจำว่า Traefik มี arg เพิ่ม)

**คำถามชวนคิด**

1. ใน Gateway API ใครควรเป็นเจ้าของ `Gateway harbor` และใครเป็นเจ้าของ `HTTPRoute canary` ถ้าทีมร้านต้องการเปลี่ยนน้ำหนักเป็น 50/50 ต้องแก้ไฟล์ไหน และไม่ต้องแตะอะไร
2. ป้าย Ingress `som-shop` ของ LAB 10 จะเขียนเป็น Gateway API ได้อย่างไร (redirect HTTP → HTTPS และ TLS ไปอยู่ที่ resource ใด)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `ingress-controller/` หรือ `som-shop-v8/`, kubectl แจ้ง `the path "..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 012_kubernetes_ingress k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/012_kubernetes_ingress/02_LAB` ตรวจด้วย `pwd` |
| `./lab05-pathtype/try-paths.sh: Permission denied` (หรือ `loop.sh`, `hit.sh`) | สิทธิ์ execute หายระหว่างคัดลอก | รันด้วย `bash <ชื่อสคริปต์> ...` หรือ `chmod +x lab05-pathtype/*.sh lab09-rolling/*.sh som-shop-v8/*.sh` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 6 (postgres + build 1.5/1.6) และ LAB 10 ตามกล่อง "ถ้าไม่มีร้านจากบทที่ 11" |
| `The Service "traefik" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated` | Service ของร้านบทที่ 11 (หรือ `ngx-tls` ของ LAB 4 บทที่ 11) ยังถือ 30080–30082 | `kubectl get svc -A \| grep 3008` ลบ Service ที่ถือพอร์ต (ร้าน: `kubectl -n som-shop delete svc som-web som-https`) แล้ว `kubectl apply -f ingress-controller/00-traefik.yaml` ซ้ำ |
| log Traefik มี `"Failed to watch" ... could not find the requested resource (get middlewaretcps.traefik.io)` ซ้ำ ๆ | apply controller ก่อน CRD | `kubectl apply -f ingress-controller/traefik-crds-v3.7.13.yml` แล้ว `kubectl -n traefik rollout restart deploy/traefik` |
| `error: resource mapping not found for name: "redirect-https" ... no matches for kind "Middleware" in version "traefik.io/v1alpha1"` | ยังไม่มี CRD ของ Traefik | apply ไฟล์ CRD ก่อน (LAB 1 ขั้นที่ 2) |
| Pod Traefik `ErrImagePull`/`ImagePullBackOff` | Node ดึง `traefik:v3.7.13` จาก Docker Hub ไม่ได้ (เน็ตช้า/ถูกจำกัด) | รอแล้วดู `kubectl -n traefik describe pod -l app=traefik` หรือ 🐧 `docker pull traefik:v3.7.13 && kind load docker-image traefik:v3.7.13 --name lab` |
| `curl localhost:30080` ได้ `404 page not found` | ปกติ: ไม่มีป้ายรับชื่อ `localhost` | ใช้ชื่อ `http://shop.localhost:30080` หรือ `-H 'Host: shop.localhost'` |
| `curl: (7) Failed to connect to localhost port 30080` | ยังไม่มี Service `traefik` (ติดตั้งไม่ครบ/พอร์ตชน) หรือ Pod Traefik ยังไม่ Ready | `kubectl -n traefik get pod,svc` แก้ตามแถวพอร์ตชนด้านบน |
| browser: `DNS_PROBE_FINISHED_NXDOMAIN` / "Hmm. We're having trouble finding that site" เมื่อเปิด `shop.localhost` | browser/ระบบนั้นไม่แปลง `*.localhost` เอง (ทดสอบแล้วเฉพาะ Chromium บน Linux) | แก้ไฟล์ hosts: `127.0.0.1 shop.localhost admin.localhost` หรือทดสอบด้วย curl ใน k8s-lab |
| `curl: (6) Could not resolve host: shop.localhost` / โปรแกรมอื่น `getaddrinfo ENOTFOUND` | โปรแกรมใช้ resolver ของระบบ (`getent rc=2`) | `curl --resolve shop.localhost:30081:127.0.0.1 ...` หรือแก้ไฟล์ hosts |
| `kubectl get ing` คอลัมน์ ADDRESS ว่าง | `ingressClassName` ไม่ตรงกับ class ที่มี (เช่น `nginx`) | `kubectl get ingressclass` แล้วแก้เป็น `traefik` |
| `describe ing` แสดง `<error: services "..." not found>` หรือ `svc:8080 ()` ได้ 404 | ชื่อ Service ผิด หรือใช้ containerPort แทน port ของ Service | `kubectl get svc -n <ns>` แก้ชื่อ/พอร์ต ดู `kubectl -n traefik logs deploy/traefik \| grep ERR` |
| `503 Service Unavailable` `no available server` | กฎตรงแต่ไม่มี Pod Ready (scale 0, readiness ไม่ผ่าน, Pod ยังไม่เริ่ม) | `kubectl get endpointslice -l kubernetes.io/service-name=<svc> -n <ns>`, `kubectl get pod` รอ 2–3 วินาทีหลัง rollout |
| ชื่อที่ไม่มีป้าย (`other.localhost`) กลับได้หน้า admin แทน 404 | `lab06-debug/lost.yaml` (defaultBackend) ยังค้าง | `kubectl delete -f lab06-debug/lost.yaml` |
| `/api` ไม่มีบรรทัด `Name:` ให้ grep | path `/api` ของ `traefik/whoami` ตอบ JSON | ปกติ ดู `"name":"api"` ใน JSON หรือใช้ `/api/` `/api/stats` |
| `/apix` ไป api หรือ `/docs` ได้ 404 | `strictPrefixMatching` ถูกปิด (patch ใน LAB 5 แล้วลืมคืน) | `kubectl apply -f ingress-controller/00-traefik.yaml` |
| `https://...:30081` ได้ `HTTP/2 404` ทั้งที่ `openssl s_client` เห็นใบของร้าน | `--entryPoints.websecure.http.tls` ไม่เป็น `true` (patch ใน LAB 7 แล้วลืมคืน) | `kubectl apply -f ingress-controller/00-traefik.yaml` |
| `curl: (60) SSL certificate problem: self-signed certificate` | ใบ self-signed | ทดสอบด้วย `-k` หรือ `--cacert tls.crt` (ตรวจจริง) |
| `--cacert tls.crt` ยังได้ `curl: (60)` | เรียกด้วยชื่อที่ไม่อยู่ใน SAN (`127.0.0.1`) หรือชื่อที่ไม่มี `spec.tls` (ได้ `TRAEFIK DEFAULT CERT`) หรือใช้ `tls.crt` คนละไฟล์กับใน Secret | ใช้ชื่อในใบ (`shop.localhost`, `admin.localhost`) + `--resolve` ตรวจ `openssl s_client -servername ...` และใช้ `tls.crt` ของโฟลเดอร์ที่สร้าง Secret |
| browser ขึ้น `NET::ERR_CERT_AUTHORITY_INVALID` | ใบ self-signed | ปกติใน LAB กด Advanced → Proceed (เฉพาะทดสอบ) |
| `Location: https://shop.localhost/...` (ไม่มีพอร์ต) / `curl -L` ได้ `rc=7` / browser เชื่อมต่อไม่ได้หลัง redirect | Middleware `redirectScheme` ไม่มี `port: "30081"` (ไฟล์ `redirect-noport.yaml` ค้าง) | `kubectl apply -f lab08-middleware/redirect.yaml` (LAB 10 ตรวจ `k8s/50-ingress.yaml`) |
| HTTPS ได้ `Moved Permanently` / 301 วนกลับ `:30081` | ส่ง `Host` ไม่มีพอร์ตหรือพอร์ตอื่น (`-H 'Host: shop.localhost'`, tunnel พอร์ตอื่น) | ใช้ `--resolve shop.localhost:30081:127.0.0.1` หรือ `-H 'Host: shop.localhost:30081'` และเปิดด้วยพอร์ต 30080/30081 ตรง |
| `401` ทั้งที่ใส่ `-u som:meow-admin-123` | Secret ของบัตรไม่อยู่ namespace เดียวกับ Middleware, ชื่อ Secret ไม่ตรง (`admin-auth` / `som-admin-auth`) หรือพิมพ์รหัสผิด | `kubectl -n <ns> get secret` ตรวจ `type: kubernetes.io/basic-auth` และ key `username`/`password` |
| log `ERR ... middleware "...@kubernetescrd" does not exist` | (1) ชื่อใน annotation ผิด ต้องเป็น `<namespace>-<ชื่อ>@kubernetescrd` หรือ (2) เกิดชั่วครู่ตอน Traefik restart | (1) แก้ชื่อ (2) ปกติ หายเองภายในวินาที |
| ป้าย `shop.localhost` ของร้าน (LAB 10) ตอบเป็น whoami `Name: menu` | ยังไม่ได้ลบ namespace `ingress-demo` ป้ายชื่อซ้ำกัน | `kubectl delete ns ingress-demo` (LAB 9 ขั้นที่ 5) |
| LAB 10 footer ยังเป็น `LAB 011` | ConfigMap ใหม่มีผลหลัง `rollout restart` เท่านั้น หรือเพิ่งเห็น Pod เก่าช่วง preStop | ทำขั้น E แล้วรอ 10 วินาที |
| LAB 10 `{"ok":false,"error":"ข้อมูลไม่ถูกต้อง"}` | body ใช้ `productId` | ใช้ `{"product_id":4,"qty":1}` |
| LAB 10 Pod `som-web` ใหม่ค้าง `Init:Error` | รหัสใน `som-db-secret` ไม่ตรงกับฐานข้อมูล (จากบทที่ 11) | ดู `kubectl -n som-shop logs <pod> -c db-seed` แก้ Secret ตามบทที่ 11 LAB 9 |
| `Warning: resource secrets/som-tls is missing the kubectl.kubernetes.io/last-applied-configuration annotation` | apply ทับ Secret ที่สร้างด้วย `create` | ปกติ kubectl เติมให้เอง |
| LAB 9 แบบเปราะได้ `err=0` | เครื่องเร็ว จังหวะไม่ชน | ปกติ ลองซ้ำอีก 1–2 รอบ (ผลจริงเจอ 3–5 ครั้งต่อรอบ) |
| `kubectl delete ns ingress-demo` นานเกิน 30 วินาที | Pod รอ preStop + grace | รอได้ถึง 1–2 นาที ตรวจ `kubectl get ns ingress-demo` |
| LAB เสริม `kubectl apply --server-side -f https://github.com/...` ค้าง/ล้ม | ไม่มีอินเทอร์เน็ตหรือ GitHub ถูกบล็อก | ลองใหม่ภายหลัง (LAB เสริมไม่บังคับ) |
| browser เปิด `http://shop.localhost:30080` ไม่ได้ทั้งที่ใน k8s-lab curl ได้ | container `k8s-lab` ไม่ได้ publish พอร์ต หรือโปรแกรมอื่นใช้พอร์ต | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp`–`30082/tcp` |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 6 ข้อ **บังรหัสผ่านจริงทุกครั้ง** (รหัสตัวอย่างของ LAB แสดงได้)

- [ ] **LAB 0** `kubectl get svc -A | grep 3008` ก่อนและหลังคืนพอร์ต (หลังต้องเป็น `ไม่มี NodePort 3008x ค้าง`), `kubectl -n som-shop get deploy,sts,pvc` และ `crictl images` ที่เห็น `som-shop-web 1.5`, `1.6`, `postgres 17.11-alpine` บนทั้งสอง worker
- [ ] **LAB 1** `kubectl -n traefik get deploy,pod,svc -o wide`, `kubectl get ingressclass` (`traefik (default)`), `curl -i localhost:30080` (`404 page not found`), `/api/version`, entrypoints 3 ตัว, error `provided port is already allocated` ของ `probe` และ dashboard ใน browser
- [ ] **LAB 2** curl ก่อน/หลังแขวนป้าย, `Host: shop.localhost:30080` + `X-Forwarded-*`, `Trying [::1]` → `Connected to shop.localhost (127.0.0.1)`, `getent rc=2`, `--resolve`, `describe ing shop`, access log และผลเปิด `http://shop.localhost:30080` ใน browser ของตัวเอง (ระบุ browser/OS)
- [ ] **LAB 3** describe Rules 3 กฎ, ผลยิง 8 path, JSON ของ `/api` และ router + priority
- [ ] **LAB 4** jsonpath `ingressClassName` = `traefik`, `admin.localhost` → admin, `other.localhost` → 404, `ADMIN.localhost` → admin
- [ ] **LAB 5** ตาราง `try-paths.sh` ทั้งแบบ strict=true และ strict=false พร้อม rule จาก dashboard API และผลหลังคืนค่า
- [ ] **LAB 6** ADDRESS ว่างของ `wrongclass`, describe ของ `typo`, log `ERR` สองบรรทัด, `503 no available server`, ผล `lost` ที่ทุกชื่อเป็น admin, `menu=0 -> 503` และผลหลังเก็บกวาด
- [ ] **LAB 7** SAN ของใบ, `get ing` PORTS `80, 443`, `X-Forwarded-Proto: https`, `rc=60` / `--cacert` / `127.0.0.1` rc=60, `subject=CN = TRAEFIK DEFAULT CERT` และ `HTTP/2 404` เมื่อปิด `websecure.http.tls`
- [ ] **LAB 8** `301` + `Location` ที่มีและไม่มีพอร์ต (`rc=7`), `401` + `www-authenticate`, บัตรผิด 401, บัตรถูก 200, `GET /orders` + `X-Forwarded-Prefix: /admin` และรายการ middleware ของ router
- [ ] **LAB 9** `ok=300 err=0` ทั้ง menu-v2 และ restart, ผลแบบเปราะอย่างน้อย 2 รอบพร้อมจำนวน 502/000 ของเครื่องตัวเอง, access log 502 และ `kubectl delete ns ingress-demo`
- [ ] **LAB 10** (1) จุดเริ่ม: `get deploy,sts,svc,secret,ing` + 404 (2) ขั้น A `service/som-web` ClusterIP และ NodePort เหลือแค่ traefik (3) ขั้น B subject/SAN ก่อนและหลัง (4) ขั้น C `get ing,middleware` (5) ขั้น D 301, `orders` ก่อน/หลังสั่ง, admin 401/200/`/stats`, `localhost:30080/api/stats` 404, `--resolve` vs `-H 'Host: shop.localhost'` (6) `hit.sh` แบบ `--cacert` (7) ขั้น E `ok=… err=0` ทั้งสองรอบ + footer LAB 012 + `rollout history` (8) ขั้น F `get svc -A` + `get ... -n som-shop` (9) browser 6 ฉากของเครื่องตัวเอง: หน้าเตือนใบรับรอง, หน้าร้านหลัง redirect, admin 401, admin หลัง login, `other.localhost` 404, dashboard
- [ ] **LAB เสริม** (ถ้าทำ) `ACCEPTED True`, `Accepted=True Programmed=True`, ผลนับ 40 ครั้ง และ CRD gateway เหลือ 0 หลังคืนสภาพ

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab (path ในตารางนับจาก `/workspace/012_kubernetes_ingress/02_LAB`)

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Service `som-web`/`som-https` ของบทที่ 11 (**จอง 30080/30082**) | ก่อน LAB 0 | `kubectl get svc -A \| grep 3008` | `kubectl -n som-shop delete svc som-web som-https` (LAB 0 ขั้นที่ 5) |
| Traefik: namespace `traefik` (**จอง 30080–30082**), ClusterRole/Binding `traefik`, IngressClass `traefik`, CRD `*.traefik.io` 10 ตัว | 1 | `kubectl -n traefik get all`; `kubectl get ingressclass`; `kubectl get crd \| grep -c traefik.io` | **เก็บไว้ใช้ต่อ** ถ้าจะลบดู [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) |
| args ของ Traefik ที่ patch (`strictPrefixMatching=false`, `websecure.http.tls=false`, `kubernetesgateway=true`) | 5, 7, เสริม | `kubectl -n traefik get deploy traefik -o jsonpath='{.spec.template.spec.containers[0].args}'` | `kubectl apply -f ingress-controller/00-traefik.yaml` |
| namespace `ingress-demo` (menu/api/admin, ป้าย `shop`, `shop-admin`, `backoffice`, `paths`, Middleware, Secret `som-tls`, `admin-auth`) | 2–9 | `kubectl get ns ingress-demo`; `kubectl get ing -A` | `kubectl delete ns ingress-demo` (**ก่อน LAB 10**) |
| ป้าย `lost` (defaultBackend), `typo`, `wrongclass` | 6 | `kubectl -n ingress-demo get ing` | `kubectl delete -f lab06-debug/` |
| Middleware `redirect-https` แบบไม่มี port | 8 | `curl -si http://shop.localhost:30080/ \| grep -i location` | `kubectl apply -f lab08-middleware/redirect.yaml` |
| ไฟล์ `lab07-tls/tls.crt`, `tls.key` | 7 | `ls lab07-tls` | `rm -f lab07-tls/tls.crt lab07-tls/tls.key` |
| ไฟล์ `som-shop-v8/tls.crt`, `tls.key` (ใบที่อยู่ใน Secret `som-tls`) | 10 | `ls som-shop-v8` | เก็บไว้ได้ระหว่างใช้ร้าน (ใช้กับ `--cacert`) ลบได้ `rm -f som-shop-v8/tls.crt som-shop-v8/tls.key` **ห้าม commit** |
| namespace `som-shop` (ร้าน + `som-admin`, Ingress 2 แผ่น, Middleware 2 ตัว, Secret `som-db-secret`, `som-tls`, `som-admin-auth`, PVC `data-som-db-0`) | 10 | `kubectl -n som-shop get all,ing,middleware,secret,pvc` | **เก็บไว้ใช้ต่อบทถัดไป** หรือ `kubectl delete ns som-shop` |
| CRD Gateway API, ClusterRole/Binding `gateway-role`/`gateway-controller`, GatewayClass/Gateway/HTTPRoute | เสริม | `kubectl get crd \| grep -c gateway.networking.k8s.io` | LAB เสริม ขั้นที่ 4 |
| บรรทัด `127.0.0.1 shop.localhost admin.localhost` ในไฟล์ hosts ของเครื่องนักศึกษา (ถ้าเพิ่ม) | 2, 10 | 🖥️ เปิดไฟล์ hosts | 🖥️ ลบบรรทัดนั้นเมื่อจบบท |
| image `som-shop-web:1.5`/`1.6`, `postgres`, `traefik`, `whoami`, `nginx-unprivileged` บน Node และ `/root/postgres.tar` | 0–10 | `docker exec lab-worker crictl images` | **เก็บ image ไว้ได้** (หายไปเมื่อ `k8s-down`) ไฟล์ tar ลบได้ `rm -f /root/postgres.tar` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl get ns
kubectl get svc -A | grep -E 'NodePort|som-'
kubectl get ingressclass; kubectl get crd | grep -c traefik.io; kubectl get crd | grep -c gateway.networking || true
```

ผลจริงท้าย LAB 10 (หลังคืนสภาพ LAB เสริมแล้ว)

```text
NAME                 STATUS   AGE
default              Active   16m
kube-node-lease      Active   16m
kube-public          Active   16m
kube-system          Active   16m
local-path-storage   Active   16m
som-shop             Active   12m
traefik              Active   9m31s
som-shop      som-admin    ClusterIP   10.96.126.248   <none>        80/TCP                                      3m20s
som-shop      som-db       ClusterIP   None            <none>        5432/TCP                                    12m
som-shop      som-web      ClusterIP   10.96.198.30    <none>        80/TCP                                      3m21s
traefik       traefik      NodePort    10.96.154.128   <none>        80:30080/TCP,443:30081/TCP,8080:30082/TCP   9m32s
NAME                CONTROLLER                      PARAMETERS   AGE
traefik (default)   traefik.io/ingress-controller   <none>       9m31s
10
0
```

ผลที่ถูกต้อง: ไม่มี namespace `ingress-demo`, NodePort มีแค่ของ `traefik`, IngressClass `traefik (default)`, CRD `traefik.io` 10 ตัว และไม่มี CRD ของ Gateway API **แนะนำให้เก็บ Traefik และร้าน `som-shop` ไว้** เพื่อใช้ต่อในบทถัดไป

ถ้าต้องการลบ Traefik ออกทั้งหมด (เช่น จะกลับไปทำ LAB ของบทก่อนที่ใช้ NodePort 30080–30082) ให้ลบป้ายของร้านหรือทั้งร้านก่อน แล้วลบ controller และ CRD ตามลำดับ

```bash
kubectl delete ns som-shop
kubectl delete -f ingress-controller/00-traefik.yaml; kubectl delete -f ingress-controller/traefik-crds-v3.7.13.yml | tail -2
kubectl get ns traefik; kubectl get crd | grep -c traefik; kubectl get svc -A | grep 3008 || echo "ไม่มี NodePort 3008x ค้าง"
```

ผลจริงของการลบ controller และ CRD (จากการทดลองลำดับติดตั้งใน LAB 1)

```text
namespace "traefik" deleted
serviceaccount "traefik" deleted from traefik namespace
clusterrole.rbac.authorization.k8s.io "traefik" deleted
clusterrolebinding.rbac.authorization.k8s.io "traefik" deleted
deployment.apps "traefik" deleted from traefik namespace
service "traefik" deleted from traefik namespace
ingressclass.networking.k8s.io "traefik" deleted
customresourcedefinition.apiextensions.k8s.io "tlsstores.traefik.io" deleted
customresourcedefinition.apiextensions.k8s.io "traefikservices.traefik.io" deleted
Error from server (NotFound): namespaces "traefik" not found
0
ไม่มี NodePort 3008x ค้าง
```

คลัสเตอร์ `lab` และ image เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit` และอย่าลืมลบบรรทัดที่เพิ่มในไฟล์ hosts ของเครื่องตัวเอง (ถ้าเพิ่ม)

บทถัดไปจะแก้ปัญหาที่ยังเหลือจากบทนี้: เพิ่ม/ลดบูธอัตโนมัติตามโหลด (**HPA**) และแพ็กการติดตั้ง Traefik กับทั้งร้านเป็นชุดเดียว (**Helm**) ส่วนข้อจำกัดของ Ingress และ **Gateway API** ดูทฤษฎีหัวข้อ 19 และ LAB เสริม

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ Pod, จำนวนครั้งและจำนวนวินาที) เป็นค่าตัวอย่าง รหัสผ่านในภาพเป็นค่าตัวอย่าง ผู้เรียนควรใช้ผลลัพธ์จากเครื่องตัวเองและเนื้อหาในเอกสารนี้เป็นหลัก
