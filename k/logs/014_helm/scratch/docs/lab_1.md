# LAB บทที่ 14: Helm — ชุดแฟรนไชส์ร้านน้องส้ม เปิดสาขาทั้งร้านด้วยคำสั่งเดียว

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Helm 4 (v4.3.0) — repository และ Artifact Hub, ติดตั้ง chart สำเร็จรูป (podinfo), values (`-f`, `--set`, `--reuse-values`) และกับดัก upgrade, history/rollback/`--rollback-on-failure`/`--keep-history`, `helm create`/lint/template/test, debug แม่พิมพ์พัง (`--dry-run=server` ที่ไม่จับ field ผิด), อ่านแม่พิมพ์ `som-shop` (range, if, include, toYaml, checksum), ใบสั่ง dev/prod + `values.schema.json` + `required`/`lookup`, hook seed + `helm test` + ถอด release Secret, ย้าย Traefik/metrics-server จาก static manifest เป็น chart, OCI registry (`helm package`/`push`/`install oci://`) และ LAB สุดท้าย: ติดตั้งสาขา dev ทั้งร้านด้วยคำสั่งเดียว รับร้านเดิมของบท 013 เข้า Helm (`--take-ownership --force-conflicts`) อัปเกรด 1.7 → 1.8 และย้อนรุ่นระหว่างลูกค้าเข้าร้านโดยไม่มี error
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ร้านน้องส้มท้ายบทที่ 13 รับวันลดราคาได้เองแล้ว แต่ทั้งร้านยังเป็นกองไฟล์ YAML ที่ต้อง apply ตามลำดับ และ Traefik กับ metrics-server ก็ติดตั้งด้วย static manifest ใน LAB นี้นักศึกษาจะใช้ **Helm** หรือ **หุ่นยนต์ผู้รับเหมาติดตั้งร้าน** เริ่มจากเปิดแคตตาล็อก (repository) ติดตั้ง chart สำเร็จรูป `podinfo` ฝึกใบสั่ง (values) สมุดบันทึก (revision) และการย้อนรุ่น สร้าง chart แรกด้วย `helm create` ทำแม่พิมพ์พังแล้วหาจุดผิด จากนั้นอ่าน **ชุดแฟรนไชส์ร้านน้องส้ม `charts/som-shop`** ที่เตรียมไว้ ทดลองใบสั่ง dev/prod ด่านตรวจ hook และผู้ตรวจรับร้าน ย้ายพนักงานต้อนรับ (Traefik) และเจ้าหน้าที่จดมิเตอร์ (metrics-server) ให้มาจาก chart ทางการ เก็บชุดแฟรนไชส์ในโกดัง OCI และปิดท้ายด้วย **LAB 12** ที่เปิดสาขา dev ทั้งร้านในคำสั่งเดียว รับร้านเดิมของบท 013 (namespace `som-shop` ที่มีออเดอร์อยู่แล้ว) เข้ามาอยู่ใต้ Helm อัปเกรดเป็น `som-shop-web:1.8` และย้อนรุ่น ขณะที่ลูกค้าจำลองยิงเข้าร้านตลอดเวลาโดยไม่เจอ error

### วัตถุประสงค์ของ LAB

เมื่อทำ LAB ครบ นักศึกษาควรสามารถ

1. ใช้ `helm repo`, `helm search repo --versions`, `helm search hub`, `helm show`, `helm pull` เลือก chart จากผู้เผยแพร่ที่ถูกต้องและ pin รุ่นได้ (LAB 1)
2. ติดตั้ง chart ด้วย `helm install ... --wait` แล้วอ่าน `helm list/status/get` และ release Secret ได้ (LAB 2)
3. ส่ง values ด้วย `-f`/`--set` อธิบายลำดับความสำคัญ และหลีกเลี่ยงกับดัก upgrade ที่ทำให้ค่ากลับเป็นค่าเริ่มต้นได้ (LAB 3)
4. ใช้ `helm history`, `helm rollback <rev>`, `--rollback-on-failure`, `--keep-history` และอธิบายว่าทำไมต้องใส่ `--wait` และระบุเลข revision เสมอ (LAB 4)
5. สร้าง chart ด้วย `helm create` ตรวจด้วย `lint`/`template` และใช้ `helm test` (LAB 5)
6. อ่าน error ของ Helm 4 แบบ (YAML, function, required, schema, apiVersion) และตรวจ manifest สองชั้นด้วย `helm template | kubectl apply --dry-run=server` (LAB 6)
7. อ่านแม่พิมพ์ `som-shop` และอธิบาย `range`, `if`, `include`, `toYaml | nindent`, checksum annotation, `fullnameOverride` จากผล render จริง (LAB 7)
8. ใช้ใบสั่งต่อ environment, `values.schema.json`, `required`, `lookup` และอธิบายความต่างของ `helm lint/template` กับการติดตั้งจริง (LAB 8)
9. ติดตั้งร้านทั้งร้านพร้อม hook seed ตรวจรับด้วย `helm test` และถอดรหัสจาก release Secret ได้ (LAB 9)
10. ย้ายของที่ติดตั้งด้วย `kubectl apply` ไปเป็น chart อธิบายว่าเมื่อไร adopt ได้และเมื่อไรต้องลบแล้วติดตั้งใหม่ (LAB 10, 12)
11. แพ็ก push และติดตั้ง chart จาก OCI registry (LAB 11)
12. ส่งร้านน้องส้มทั้งร้านเป็นชุดเดียว: เปิดสาขา dev รับร้านเดิมเป็นสาขา prod อัปเกรด/ย้อนรุ่นโดยลูกค้าไม่เจอ error และอธิบายผลของ PVC ที่ค้างหลัง uninstall (LAB 12)

### ผลลัพธ์ในเอกสารนี้มาจากไหน

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`: helm v4.3.0, kind 0.33.0, 3 Node, Kubernetes v1.37.0, kubectl v1.37.1) เมื่อ 6 ตุลาคม 2569 (เวลาไทย 05:39–06:13) **โดยจำกัด container ไว้ที่ 4 CPU / RAM 8 GB เพื่อจำลองเครื่องนักศึกษา 4 core** จุดเริ่มต้นคือสภาพร้าน **ท้ายบทที่ 13** ที่ไล่ทำตามเอกสารบทที่ 12–13 บนคลัสเตอร์ใหม่ (Traefik + metrics-server แบบ static, `som-web` 1.7 + HPA 2–6, ออเดอร์ 3 รายการ) ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`)

**เวลา, AGE, IP, ชื่อ Pod, ค่า hash/digest, จำนวนออเดอร์ และเลข revision ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** (เลข revision ขึ้นกับจำนวนครั้งที่สั่ง/ล้ม) ให้ยึดผลจากเครื่องตัวเอง ส่วน **ลำดับเหตุการณ์และข้อความ error ต้องตรง** ถ้าเลข revision ในเครื่องต่างจากเอกสาร ให้ดูจาก `helm history` แล้วใช้เลขของตัวเองในคำสั่ง rollback

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox/Safari บนเครื่องตัวเอง |

คำสั่ง `helm`, `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้น `docker cp` (🖥️) และการเปิดร้าน/dashboard ใน browser (🌐) LAB 10 และ LAB 12 ใช้ **2 หน้าต่าง SSH** (หน้าต่างหนึ่งยิงลูกค้าจำลองด้วย `hit.sh` อีกหน้าต่างสั่ง helm) ให้เปิดไว้ตั้งแต่แรก

ร้านเปิดผ่านประตู Traefik เหมือนบทที่ 12–13: 🌐 `http://shop.localhost:30080` (ถูกส่งต่อไป `https://shop.localhost:30081`) หลังร้าน `https://admin.localhost:30081` (บัตร `som` / `meow-admin-123`) สาขา dev ของบทนี้ `http://dev.shop.localhost:30080` และ dashboard ของ Traefik `http://localhost:30082/dashboard/` (Chrome/Edge แปลงชื่อ `*.localhost` เป็นเครื่องตัวเองได้เอง ถ้า browser อื่นเปิดไม่ได้ให้ใช้ทางสำรองในบทที่ 12 หรือใช้ `curl` ใน k8s-lab)

### กติกาของ LAB บทนี้

- ทุก LAB ทำในโฟลเดอร์ **`/workspace/014_kubernetes_helm/02_LAB`** (คำสั่งอ้างไฟล์แบบ `charts/som-shop`, `labs/lab03-values/podinfo-values.yaml`) ยกเว้นที่บอกให้ `cd` เข้าโฟลเดอร์ย่อย
- namespace ที่ใช้: `helm-demo` (LAB 2–4), `first` (LAB 5–6), `som-dev` (LAB 9 และ 12), `oci-demo` (LAB 11), `traefik` และ `kube-system` (LAB 10), **`som-shop` = ร้านจริงจากบท 013** (LAB 12 รับเข้า Helm) ทุก LAB มีบล็อก **"เก็บกวาด"** ทำทุกครั้ง
- **ใส่ `--wait` ทุกครั้งที่ install/upgrade/rollback** (Helm 4 ไม่ใส่ = ไม่รอ Pod พร้อม) และ **ระบุเลข revision ทุกครั้งที่ rollback** ยกเว้นขั้นที่ตั้งใจให้เห็นกับดัก
- **pin รุ่นของ chart ทุกคำสั่ง** (`--version 6.15.0`, `41.6.1`, `3.14.0`) เพื่อให้ผลตรงกับเอกสาร
- รหัสผ่านทุกตัวเป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง: SSH `passwd`, ฐานข้อมูล `meow1234` (บทที่ 11; ถ้าเปลี่ยนรหัสร้านใน LAB บทที่ 11 ให้ใช้รหัสของตัวเองแทนในขั้นที่ใส่ `--set db.password`), บัตรหลังร้าน `som` / `meow-admin-123` (บทที่ 12), บัญชีโกดัง OCI `som` / `meow-registry-123` (LAB 11) ไฟล์ `*.key`, `*.crt`, `*.tgz` และโฟลเดอร์ที่ LAB สร้าง (เช่น `labs/lab11-registry/auth/`) ห้าม commit ลง git (`.gitignore` กันไว้แล้ว)
- ค่าที่ลดความปลอดภัยใน LAB (`api.insecure: true` ของ Traefik dashboard, `--kubelet-insecure-tls`, `--plain-http` ของ registry, `--verify=false` ของ plugin) **ใช้เฉพาะ LAB**
- Helm ต้อง **ต่ออินเทอร์เน็ต** (ดึง index ของ repository, Artifact Hub, chart podinfo/traefik/metrics-server และ image `ghcr.io/stefanprodan/podinfo`, `nginx`, `busybox`, `curlimages/curl`, `registry:2`, `httpd:2.4-alpine`) ส่วน `som-shop-web:1.7/1.8` และ `postgres:17.11-alpine` ต้องอยู่ใน Node แล้ว (LAB 0)

### เครื่อง ARM (Mac Apple Silicon)

**บทนี้ทดสอบบนเครื่อง amd64 เท่านั้น ยังไม่ได้ลองบนเครื่อง ARM จริง** image ภายนอกที่ใช้ (`ghcr.io/stefanprodan/podinfo`, `nginx:1.16.0` ของ `helm create`, `registry:2`, `httpd:2.4-alpine`, `curlimages/curl:8.22.0`, `traefik:v3.7.13`, `metrics-server:v0.9.0`) คาดว่าเป็น multi-arch และ `som-shop-web` ที่ build ในเครื่องตัวเองได้สถาปัตยกรรมตรงกับ Node อยู่แล้ว จุดที่ต้องแก้มีจุดเดียว: ถ้าต้องสร้างคลัสเตอร์ใหม่ (LAB 0 ทางสำรอง) ให้ `docker save --platform linux/arm64` แทน `linux/amd64` สำหรับ postgres ถ้าเจอปัญหาบนเครื่อง ARM ให้แจ้งผู้สอน

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมท่าเรือและแอป 1.8](#lab-0-เตรียมท่าเรือและแอป-18) | 10 นาที | ⭐ |
| 1 | [แคตตาล็อกแฟรนไชส์](#lab-1-แคตตาล็อกแฟรนไชส์) | 10 นาที | ⭐ |
| 2 | [เปิดสาขาแรกจากแคตตาล็อก (podinfo)](#lab-2-เปิดสาขาแรกจากแคตตาล็อก-podinfo) | 10 นาที | ⭐⭐ |
| 3 | [ใบสั่งปรับแต่งร้าน (values)](#lab-3-ใบสั่งปรับแต่งร้าน-values) | 15 นาที | ⭐⭐ |
| 4 | [สมุดบันทึกการปรับปรุงร้าน (history/rollback)](#lab-4-สมุดบันทึกการปรับปรุงร้าน-historyrollback) | 20 นาที | ⭐⭐⭐ |
| 5 | [ชุดแฟรนไชส์ชุดแรกของเรา (helm create)](#lab-5-ชุดแฟรนไชส์ชุดแรกของเรา-helm-create) | 10 นาที | ⭐⭐ |
| 6 | [แม่พิมพ์พัง: render และ debug](#lab-6-แม่พิมพ์พัง-render-และ-debug) | 15 นาที | ⭐⭐⭐ |
| 7 | [แม่พิมพ์ร้านน้องส้ม (template functions)](#lab-7-แม่พิมพ์ร้านน้องส้ม-template-functions) | 15 นาที | ⭐⭐⭐ |
| 8 | [ใบสั่งต่อสาขาและด่านตรวจ](#lab-8-ใบสั่งต่อสาขาและด่านตรวจ) | 15 นาที | ⭐⭐⭐ |
| 9 | [เติมสินค้าหลังเปิดร้านและผู้ตรวจรับ (hook + test)](#lab-9-เติมสินค้าหลังเปิดร้านและผู้ตรวจรับ-hook--test) | 15 นาที | ⭐⭐⭐ |
| 10 | [Traefik และ metrics-server จากแคตตาล็อก](#lab-10-traefik-และ-metrics-server-จากแคตตาล็อก) | 20 นาที | ⭐⭐⭐⭐ |
| 11 | [โกดังเก็บชุดแฟรนไชส์ (OCI registry)](#lab-11-โกดังเก็บชุดแฟรนไชส์-oci-registry) | 15 นาที | ⭐⭐⭐ |
| 12 | [LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง](#lab-12-lab-สุดท้าย-ร้านน้องส้มพร้อมส่ง) | 45–60 นาที | ⭐⭐⭐⭐⭐ |
| เสริม | [helm-diff และ umbrella chart (ไม่บังคับ)](#lab-เสริม-helm-diff-และ-umbrella-chart-ไม่บังคับ) | 10 นาที | ⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3.5–4 ชั่วโมง ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านทฤษฎี: LAB 1–2 → หัวข้อ 3 และ 13, LAB 3 → หัวข้อ 6, LAB 4 → หัวข้อ 8 และ 10, LAB 5–6 → หัวข้อ 4 และ 7, LAB 7 → หัวข้อ 5, LAB 8 → หัวข้อ 5.7 และ 6, LAB 9 → หัวข้อ 10–11, LAB 10 → หัวข้อ 9 และ 14, LAB 11 → หัวข้อ 13, LAB 12 → หัวข้อ 8–11

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมท่าเรือ](#fig-1) | 21 | [LAB 10 ติดตั้งทับของเดิม](#fig-21) |
| 2 | [1.8 = build-arg](#fig-2) | 22 | [LAB 10 ย้ายจริง ประตูปิดชั่วคราว](#fig-22) |
| 3 | [LAB 1 แคตตาล็อก](#fig-3) | 23 | [LAB 11 โกดัง OCI](#fig-23) |
| 4 | [LAB 1 ชื่อซ้ำใน Artifact Hub](#fig-4) | 24 | [LAB 11 login push install](#fig-24) |
| 5 | [LAB 2 สาขาแรก](#fig-5) | 25 | [LAB 12 ภาพรวม](#fig-25) |
| 6 | [LAB 2 helm get](#fig-6) | 26 | [LAB 12 โครงชุด som-shop](#fig-26) |
| 7 | [LAB 3 values](#fig-7) | 27 | [LAB 12 สาขา dev](#fig-27) |
| 8 | [LAB 3 กับดัก upgrade](#fig-8) | 28 | [ภาพหน้าจอจริง สาขา dev](#fig-28) |
| 9 | [LAB 4 สมุดบันทึก](#fig-9) | 29 | [LAB 12 รับร้านเดิมเป็น prod](#fig-29) |
| 10 | [LAB 4 rollback-on-failure](#fig-10) | 30 | [ภาพหน้าจอจริง Traefik routers](#fig-30) |
| 11 | [LAB 4 keep-history](#fig-11) | 31 | [LAB 12 อัปเกรด 1.8 err=0](#fig-31) |
| 12 | [LAB 5 helm create](#fig-12) | 32 | [LAB 12 rollback ระบุเลข](#fig-32) |
| 13 | [LAB 6 แม่พิมพ์พัง](#fig-13) | 33 | [ภาพหน้าจอจริง หลัง rollback เป็น 1.7](#fig-33) |
| 14 | [LAB 6 ช่องโหว่ของ dry-run=server](#fig-14) | 34 | [ภาพหน้าจอจริง หลัง upgrade กลับ 1.8](#fig-34) |
| 15 | [LAB 7 อ่านแม่พิมพ์](#fig-15) | 35 | [LAB 12 uninstall สาขา dev](#fig-35) |
| 16 | [LAB 8 ใบสั่งต่อสาขา](#fig-16) | 36 | [LAB 12 กับดักรหัสใหม่](#fig-36) |
| 17 | [LAB 8 ด่านตรวจปฏิเสธ](#fig-17) | 37 | [ภาพหน้าจอจริง หน้าร้าน prod 1.8](#fig-37) |
| 18 | [LAB 9 hook และ test](#fig-18) | 38 | [LAB 12 ตรวจรับร้าน](#fig-38) |
| 19 | [LAB 9 ถอด release Secret](#fig-19) | 39 | [ปิดบท](#fig-39) |
| 20 | [LAB 10 add-on จาก chart](#fig-20) |  | |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── .gitignore                         ← กัน *.key, *.crt, *.tgz, *.log และโฟลเดอร์ที่ LAB สร้าง
├── images/                            ← ภาพประกอบ LAB (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของ LAB 12 จำนวน 5 ภาพ
├── hit.sh                             ← ยิง HTTPS ผ่าน Ingress แล้วนับ ok/err (สำเนาจากบทที่ 13) ใช้ใน LAB 10 และ 12
├── som-shop-v10/app/                  ← แอป Next.js โค้ดเดียวกับ 1.7 (build เป็น som-shop-web:1.8 ด้วย --build-arg APP_VERSION=1.8)
├── charts/                            ← ชุดแฟรนไชส์ร้านน้องส้ม (LAB 7–9, 11, 12)
│   ├── som-shop/
│   │   ├── Chart.yaml                 (apiVersion v2, version 0.1.0, appVersion "1.7", kubeVersion >=1.30.0-0)
│   │   ├── values.yaml                (ใบสั่งค่าเริ่มต้น: shop.*, announcement, web.*, hpa.*, db.*, ingress.*, seed, tests)
│   │   ├── values.schema.json         (ด่านตรวจ: replicas 1–6, tag ห้าม 1.4, host/storage pattern)
│   │   ├── .helmignore
│   │   └── templates/
│   │       ├── _helpers.tpl           (ตรายาง: fullname, labels, webImage, dbPassword = --set > lookup > required)
│   │       ├── configmap.yaml         (som-web-config จาก range + som-announcement)
│   │       ├── secret.yaml            (som-db-secret: POSTGRES_PASSWORD + DATABASE_URL)
│   │       ├── db.yaml                (headless Service + StatefulSet som-db)
│   │       ├── web.yaml               (Deployment som-web + Service; checksum/config, ไม่มี replicas เมื่อเปิด HPA)
│   │       ├── hpa.yaml               (เมื่อ hpa.enabled)
│   │       ├── ingress.yaml           (Ingress som-web; tls → Secret som-tls จาก lookup/genSelfSignedCert + Middleware redirect)
│   │       ├── seed-job.yaml          (hook post-install,post-upgrade เติมสินค้าเข้าชั้น)
│   │       ├── tests/test-health.yaml (helm test: curl /api/health, /api/whoami, /api/products)
│   │       └── NOTES.txt              (การ์ดต้อนรับภาษาไทย)
│   ├── values-dev.yaml                (สาขา dev: ชื่อ "(dev)", ธีม sunset, 1 บูธ, ไม่มี HPA, http dev.shop.localhost)
│   └── values-prod.yaml               (สาขา prod: HPA 2–6, https shop.localhost, แถบ "เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว")
└── labs/
    ├── lab01-catalog/                 ← ที่แตก chart traefik ด้วย helm pull --untar (README.txt)
    ├── lab03-values/podinfo-values.yaml
    ├── lab05-first/                   ← ที่สร้าง mychart ด้วย helm create (README.txt)
    ├── lab06-debug/make-broken.sh     ← คัดลอก mychart แล้วทำแม่พิมพ์พัง 4 แบบ
    ├── lab10-addons/
    │   ├── traefik-values.yaml        (chart traefik/traefik 41.6.1 ให้ได้ผลเหมือน static บท 012/013)
    │   ├── metrics-server-values.yaml (chart metrics-server 3.14.0 + --kubelet-insecure-tls)
    │   └── static-old/                (สำเนา 00-traefik.yaml, traefik-crds-v3.7.13.yml, 00-metrics-server.yaml จากบท 012/013)
    ├── lab11-registry/                ← ที่ทำงานของ LAB 11 (README.txt; auth/ และ pulled/ สร้างระหว่าง LAB)
    └── labx-extra/harbor-addons/      ← LAB เสริม: umbrella chart (metrics-server + podinfo)
```

บทนี้มีแอป chart และ manifest เก่าที่ต้องใช้ครบในโฟลเดอร์ของตัวเอง **ไม่ต้องมีโฟลเดอร์ของบทก่อนใน container**

---

## LAB 0: เตรียมท่าเรือและแอป 1.8

<p align="center" id="fig-1">
  <img src="images/01-lab00-open.png" alt="รูปที่ 1 LAB 0 เตรียมท่าเรือ" width="900"><br>
  <em><b>รูปที่ 1</b> LAB 0: ตรวจ helm v4.3.0 และร้านจากบท 013 แล้ว build som-shop-web:1.8 (โค้ดเดิม เปลี่ยนแค่ APP_VERSION)</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` ตรวจรุ่น helm และสภาพร้านท้ายบทที่ 13 แล้ว build `som-shop-web:1.8` ไว้ใช้ใน LAB 12

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md)–[13](../../013_kubernetes_hpa/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `014_kubernetes_helm` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (ถ้า `Exited` ให้ `docker start k8s-lab`) แล้ว `cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `014_kubernetes_helm` อยู่ข้างใน**

```bash
docker ps -a --filter name=k8s-lab
docker cp 014_kubernetes_helm k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ถ้าแก้ไฟล์บนเครื่องภายหลังต้องสั่งซ้ำ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** (เปิด 2 หน้าต่างไว้เลย)

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (ค่าตัวอย่างของ LAB) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab`

### ขั้นที่ 3: ตรวจ helm คลัสเตอร์ และร้านท้ายบทที่ 13

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/014_kubernetes_helm/02_LAB
ls
helm version
helm env | grep -E "HELM_(CACHE|CONFIG|DATA)_HOME|MAX_HISTORY|HELM_DRIVER"
kubectl get nodes
kubectl get node -o jsonpath='{range .items[*]}{.metadata.name} {.status.nodeInfo.architecture}{"\n"}{end}'
```

```text
charts
hit.sh
labs
som-shop-v10
version.BuildInfo{Version:"v4.3.0", GitCommit:"bec5b06ed841fe5269972d864d5177944fd5970f", GitTreeState:"clean", GoVersion:"go1.27.1", KubeClientVersion:"v1.37"}
HELM_CACHE_HOME="/root/.cache/helm"
HELM_CONFIG_HOME="/root/.config/helm"
HELM_DATA_HOME="/root/.local/share/helm"
HELM_MAX_HISTORY="10"
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   6m49s   v1.37.0
lab-worker          Ready    <none>          6m34s   v1.37.0
lab-worker2         Ready    <none>          6m34s   v1.37.0
lab-control-plane amd64
lab-worker amd64
lab-worker2 amd64
```

(ในเครื่องนักศึกษา `ls` จะเห็น `README.md` และ `images` เพิ่มด้วย) helm เป็น **v4.3.0** และเก็บ revision ล่าสุด **10 รุ่น** (`HELM_MAX_HISTORY`) helm เก็บ cache ของ repository และ config (รวม login ของ OCI registry) ไว้ใน home ของ root ภายใน k8s-lab

ดูสภาพร้านท้ายบทที่ 13 (ร้านนี้ LAB 12 จะรับเข้า Helm)

```bash
kubectl get ns som-shop traefik
kubectl -n som-shop get deploy,sts,hpa
helm list -A
curl -sk https://shop.localhost:30081/api/stats; echo
```

```text
NAME       STATUS   AGE
som-shop   Active   4m33s
traefik    Active   4m42s
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/customers   0/0     0            0           103s
deployment.apps/som-admin   1/1     1            1           4m18s
deployment.apps/som-web     6/6     6            6           4m33s

NAME                      READY   AGE
statefulset.apps/som-db   1/1     4m33s

NAME                                          REFERENCE            TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 32%/50%   2         6         6          2m57s
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
som-web-774d99d8df-r72bt 1.7 orders=3 products=6
```

ร้านท้ายบท 013 ครบ: หน้าร้าน 1.7 + HPA 2–6 (ตอนตรวจยังมี 6 บูธเพราะเพิ่งจบวันลดราคา ไม่กี่นาทีต่อมาลดเหลือ 2 เอง), ลูกค้าจำลอง `customers 0/0`, ออเดอร์ 3 รายการ และ **`helm list -A` ว่าง** (ยังไม่มีอะไรติดตั้งด้วย Helm)

| ผล | ทำอย่างไร |
|---|---|
| มี `som-shop`, `traefik` และ `curl` ตอบ `... 1.7 orders=...` | ทำต่อขั้นที่ 4 (ทางหลัก) |
| 3 Node `Ready` แต่ไม่มี namespace `som-shop`/`traefik` | ทำ [ทางสำรอง: คลัสเตอร์ใหม่](#ทางสำรอง-คลัสเตอร์ใหม่-ไม่มีร้านบท-013) ก่อน แล้วทำขั้นที่ 4 |
| error / ไม่มีคลัสเตอร์ | `k8s-up` (ราว 55 วินาที) แล้วทำทางสำรอง |
| Node เป็น `arm64` | ทำตามปกติ (ดู [เครื่อง ARM](#เครื่อง-arm-mac-apple-silicon)) |

### ขั้นที่ 4: build som-shop-web:1.8

1.8 คือ **โค้ดเดิมของ 1.7 ทุกบรรทัด** ต่างแค่ค่า `APP_VERSION` ที่ฝังตอน build (เห็นที่ `/api/whoami` และป้ายเวอร์ชันบนหน้าร้าน) ใช้ทดสอบ upgrade/rollback ใน LAB 12

```bash
cd som-shop-v10
time (docker build -q -t som-shop-web:1.8 --build-arg APP_VERSION=1.8 app && kind load docker-image som-shop-web:1.8 --name lab)
docker run --rm som-shop-web:1.8 node -e 'console.log(process.env.APP_VERSION)'
cd ..
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

```text
sha256:cd33ee239bebe029d6b55d92be8340302975e87d2754e6ff659337afdc03e265
Image: "som-shop-web:1.8" with ID "sha256:cd33ee23..." not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.8" with ID "sha256:cd33ee23..." not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.8" with ID "sha256:cd33ee23..." not yet present on node "lab-worker", loading...

real	0m6.458s
1.8
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  ee3adb619ba03       76.7MB
docker.io/library/som-shop-web                  1.6                  771081d0c6186       76.7MB
docker.io/library/som-shop-web                  1.7                  baadc43777d7e       76.7MB
docker.io/library/som-shop-web                  1.8                  0c61f97b3ddbc       76.7MB
== lab-worker2
...
```

<p align="center" id="fig-2">
  <img src="images/02-lab00-build-arg.png" alt="รูปที่ 2 1.8 = build-arg" width="900"><br>
  <em><b>รูปที่ 2</b> 1.8 = โค้ดเดิม build ใหม่ด้วย --build-arg APP_VERSION=1.8 แล้ว kind load docker-image เข้า Node</em>
</p>

build + load ใช้ **6.5 วินาที** เพราะ docker ใช้ cache ของ layer จากการ build 1.7 ในบท 013 (ต่างแค่ layer สุดท้ายที่ตั้ง `APP_VERSION`) ถ้าไม่มี cache (คลัสเตอร์ใหม่) จะใช้ราว 40–45 วินาที

> **ห้าม tag เป็น `som-shop-web:1.4`** (รุ่นพังของบทที่ 7 — `values.schema.json` ของชุดร้านก็กันไว้) และอย่า build ทับ 1.5–1.7

### ทางสำรอง: คลัสเตอร์ใหม่ (ไม่มีร้านบท 013)

ถ้าไม่มีร้านจากบท 013 ให้เตรียมท่าเรือให้เหมือนท้ายบท 013 **ยกเว้นร้าน** (Traefik + metrics-server แบบ static จากสำเนาในโฟลเดอร์ LAB 10 ของบทนี้ ซึ่งเป็นไฟล์เดียวกับบท 012/013) แล้ว build ทั้ง 1.7 และ 1.8

```bash
cd /workspace/014_kubernetes_helm/02_LAB
# postgres (ใช้ --platform linux/arm64 บนเครื่อง ARM)
docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab; rm -f /root/postgres.tar
# หน้าร้าน 1.7 (ครั้งแรกไม่มี cache ราว 40–45 วินาที) แล้ว 1.8
cd som-shop-v10
docker build -q -t som-shop-web:1.7 --build-arg APP_VERSION=1.7 app && kind load docker-image som-shop-web:1.7 --name lab
docker build -q -t som-shop-web:1.8 --build-arg APP_VERSION=1.8 app && kind load docker-image som-shop-web:1.8 --name lab
cd ..
# Traefik (CRD + static) และ metrics-server (static) เหมือนบท 012/013
kubectl apply -f labs/lab10-addons/static-old/traefik-crds-v3.7.13.yml
kubectl apply -f labs/lab10-addons/static-old/00-traefik.yaml
kubectl apply -f labs/lab10-addons/static-old/00-metrics-server.yaml
kubectl -n traefik rollout status deploy/traefik --timeout=180s
kubectl -n kube-system rollout status deploy/metrics-server --timeout=180s
```

ทางนี้ทำ LAB 1–11 ได้เหมือนทางหลักทุกขั้น (LAB 10 ยังลบ static แล้วติดตั้ง chart ได้ตามปกติ แต่ไม่มีร้านให้ hit.sh ยิง ให้ข้ามการยิงลูกค้า) ส่วน LAB 12 ไม่มีร้านเดิมให้รับ ให้ใช้ขั้น [12.4 ทางสำรอง](#124-รับร้านเดิมเข้า-helm-สาขา-prod) แทน

### สิ่งที่เห็น

- helm v4.3.0, `HELM_MAX_HISTORY="10"`, คลัสเตอร์ 3 Node `Ready`
- ร้านท้ายบท 013 ใน `som-shop` (1.7 + HPA, ออเดอร์เดิม) และ `helm list -A` ว่าง
- `som-shop-web:1.8` อยู่บนทุก Node คู่กับ 1.5–1.7 และ postgres

**คำถามชวนคิด**

1. build 1.8 ทำไมเร็วกว่า build 1.7 ในบท 013 มาก ทั้งที่ build จากโค้ดชุดเดียวกัน
2. `helm list -A` ว่าง แปลว่าคลัสเตอร์ไม่มีแอปเลยใช่ไหม Helm รู้จักเฉพาะอะไร

**เก็บกวาด:** ไม่มี — image 1.8 ใช้ใน LAB 12 ร้านใน `som-shop` ห้ามลบ

---

## LAB 1: แคตตาล็อกแฟรนไชส์

<p align="center" id="fig-3">
  <img src="images/03-lab01-open.png" alt="รูปที่ 3 LAB 1 แคตตาล็อก" width="900"><br>
  <em><b>รูปที่ 3</b> LAB 1: helm repo add / update / search repo --versions / show — เลือก chart และ pin เวอร์ชัน</em>
</p>

**เป้าหมาย:** เพิ่มแคตตาล็อก (HTTP repository) 3 แห่ง ค้นรุ่นของ chart เลือกรุ่นที่จะ pin และอ่าน chart ก่อนติดตั้ง

**ไฟล์:** `labs/lab01-catalog/` (ที่แตก chart traefik)

### ขั้นที่ 1: เพิ่มแคตตาล็อก

```bash
cd /workspace/014_kubernetes_helm/02_LAB
helm repo list
helm repo add podinfo https://stefanprodan.github.io/podinfo
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm repo list
```

```text
no repositories to show
"podinfo" has been added to your repositories
"traefik" has been added to your repositories
"metrics-server" has been added to your repositories
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "metrics-server" chart repository
...Successfully got an update from the "podinfo" chart repository
...Successfully got an update from the "traefik" chart repository
Update Complete. ⎈Happy Helming!⎈
NAME          	URL
podinfo       	https://stefanprodan.github.io/podinfo
traefik       	https://traefik.github.io/charts
metrics-server	https://kubernetes-sigs.github.io/metrics-server/
```

`helm repo add` แค่จดชื่อกับ URL ไว้ `helm repo update` จึงดาวน์โหลด `index.yaml` (รายการทุก chart ทุกรุ่น) มาเก็บใน cache — `helm search repo` ค้นจาก cache นี้ ถ้าไม่ update จะไม่เห็นรุ่นใหม่

### ขั้นที่ 2: ค้นรุ่นและเลือก pin

```bash
helm search repo traefik/traefik --versions | head -5
helm search repo metrics-server --versions | head -3
helm search repo podinfo/podinfo --versions | head -3
```

```text
NAME                	CHART VERSION	APP VERSION	DESCRIPTION
traefik/traefik     	41.6.1       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.6.0       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.5.0       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.4.0       	v3.7.12    	A Traefik based Kubernetes ingress controller
NAME                         	CHART VERSION	APP VERSION	DESCRIPTION
metrics-server/metrics-server	3.14.0       	0.9.0      	Metrics Server is a scalable, efficient source ...
metrics-server/metrics-server	3.13.1       	0.8.1      	Metrics Server is a scalable, efficient source ...
NAME           	CHART VERSION	APP VERSION	DESCRIPTION
podinfo/podinfo	6.15.0       	6.15.0     	Podinfo Helm chart for Kubernetes
podinfo/podinfo	6.14.1       	6.14.1     	Podinfo Helm chart for Kubernetes
```

**รุ่นที่บทนี้ pin** (ข้อมูล ณ วันทำ LAB)

| chart | CHART VERSION | APP VERSION | เหตุผล |
|---|---|---|---|
| `traefik/traefik` | **41.6.1** | v3.7.13 | รุ่นล่าสุดที่ app = v3.7.13 ตรงกับ Traefik ที่ใช้ในบท 012–013 |
| `metrics-server/metrics-server` | **3.14.0** | 0.9.0 | ตรงกับ metrics-server v0.9.0 ของบท 013 |
| `podinfo/podinfo` | **6.15.0** | 6.15.0 | แอปตัวอย่างขนาดเล็กสำหรับ LAB 2–4 |

สังเกตว่า chart 41.6.1, 41.6.0, 41.5.0 ใช้ Traefik รุ่นเดียวกัน — **รุ่นของ chart กับรุ่นของแอปเป็นคนละเลข** (ทฤษฎีหัวข้อ 4.2) ถ้าวันที่ทำ LAB มีรุ่นใหม่กว่านี้ ให้ยังใช้รุ่นที่ pin ไว้

### ขั้นที่ 3: ชื่อเดียวกันใน Artifact Hub

```bash
helm search hub traefik --max-col-width 50 | head -8
```

```text
URL                                               	CHART VERSION              	APP VERSION	DESCRIPTION
https://artifacthub.io/packages/helm/traefik/tr...	41.6.1                     	v3.7.13    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/quench-tra...	0.0.21                     	3.7.13     	Cloud-native reverse proxy and load balancer wi...
https://artifacthub.io/packages/helm/aigisuk/tr...	0.1.1                      	2.7.0-rc2  	Latest release candidate of the Traefik based K...
https://artifacthub.io/packages/helm/kubeblocks...	41.6.0                     	v3.7.13    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/k3s/traefik  	41.4.2+up41.4.0            	v3.7.12    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/cloudnativ...	1.68.4                     	1.7.9      	A Traefik based Kubernetes ingress controller w...
https://artifacthub.io/packages/helm/gpg-dev/tr...	39.0.8                     	v3.6.13    	A Traefik based Kubernetes ingress controller
```

<p align="center" id="fig-4">
  <img src="images/04-lab01-hub-names.png" alt="รูปที่ 4 LAB 1 ชื่อซ้ำใน Artifact Hub" width="900"><br>
  <em><b>รูปที่ 4</b> helm search hub traefik เจอหลายผู้เผยแพร่ชื่อเดียวกัน เลือกของทางการ (traefik/traefik)</em>
</p>

มี chart ชื่อ traefik จากหลายผู้เผยแพร่ (`quench-traefik`, `aigisuk` รุ่น `2.7.0-rc2`, สำเนาของ `kubeblocks`, `k3s` ...) 🌐 เปิด `https://artifacthub.io/packages/helm/traefik/traefik` ดูป้าย Verified Publisher/Official, repository URL `https://traefik.github.io/charts` และหน้า security report ก่อนเลือก

### ขั้นที่ 4: อ่าน chart ก่อนติดตั้ง และแตกดูข้างใน

```bash
helm show chart podinfo/podinfo --version 6.15.0
helm show values podinfo/podinfo --version 6.15.0 | grep -nE "^replicaCount|^ui:|^  color|^  message|^service:|^  type:|^ingress:" | head
cd labs/lab01-catalog
helm pull traefik/traefik --version 41.6.1 --untar
ls traefik | head -20
grep -E "^(version|appVersion)" traefik/Chart.yaml
ls traefik/crds | wc -l
cd ../..
```

```text
apiVersion: v1
appVersion: 6.15.0
description: Podinfo Helm chart for Kubernetes
home: https://github.com/stefanprodan/podinfo
kubeVersion: '>=1.23.0-0'
maintainers:
- email: stefanprodan@users.noreply.github.com
  name: stefanprodan
name: podinfo
sources:
- https://github.com/stefanprodan/podinfo
version: 6.15.0

3:replicaCount: 1
17:ui:
18:  color: "#34577c"
19:  message: ""
32:service:
36:  type: ClusterIP
195:ingress:
Changelog.md
Chart.yaml
EXAMPLES.md
Guidelines.md
LICENSE
README.md
VALUES.md
crds
templates
values.schema.json
values.yaml
appVersion: v3.7.13
version: 41.6.1
25
```

- podinfo ยังใช้ `apiVersion: v1` (รูปแบบ chart ยุค Helm 2) Helm 4 ยังติดตั้งได้
- `helm show values` คือ "ใบสั่งค่าเริ่มต้น" ทั้งหมด — LAB 2–3 จะทับ `replicaCount`, `ui.message`, `ui.color` และ `ingress`
- chart traefik มี `values.schema.json` (ด่านตรวจ — LAB 8) และโฟลเดอร์ `crds/` 25 ไฟล์ (CRD ของ Traefik ที่บท 012 apply ไปแล้ว)

### สิ่งที่เห็น

- `helm repo list` มี 3 แคตตาล็อก และรู้รุ่นที่จะ pin: traefik 41.6.1, metrics-server 3.14.0, podinfo 6.15.0
- ชื่อ chart ซ้ำได้ใน Artifact Hub ต้องดูผู้เผยแพร่
- อ่าน chart ได้ 3 ทาง: `helm show chart/values/readme`, `helm pull --untar`

**คำถามชวนคิด**

1. ถ้าไม่ใส่ `--version` ในคำสั่ง install วันนี้กับเดือนหน้าจะได้ผลเหมือนกันไหม เพราะอะไร
2. ทำไม chart ที่มีชื่อ `traefik` บน Artifact Hub บางตัวมี APP VERSION `2.7.0-rc2` ทั้งที่ Traefik ล่าสุดเป็น v3.7.13 แปลว่าอะไรกับผู้ใช้

**เก็บกวาด:** โฟลเดอร์ `labs/lab01-catalog/traefik/` ไม่ใช้ต่อ ลบได้ด้วย `rm -rf labs/lab01-catalog/traefik` (ไม่เข้า git อยู่แล้ว) แคตตาล็อก 3 แห่ง **เก็บไว้** ใช้ต่อทั้งบท

---

## LAB 2: เปิดสาขาแรกจากแคตตาล็อก (podinfo)

<p align="center" id="fig-5">
  <img src="images/05-lab02-open.png" alt="รูปที่ 5 LAB 2 สาขาแรก" width="900"><br>
  <em><b>รูปที่ 5</b> LAB 2: helm install hello podinfo/podinfo ด้วย --set ข้อความภาษาไทย แล้วดู list/status/get</em>
</p>

**เป้าหมาย:** ติดตั้ง chart สำเร็จรูปเป็น release `hello` ใน namespace `helm-demo` แล้วดูว่า Helm จดอะไรไว้บ้าง

### ขั้นที่ 1: ติดตั้ง

```bash
time helm install hello podinfo/podinfo --version 6.15.0 -n helm-demo --create-namespace \
  --set replicaCount=2 --set ui.message="สวัสดีจากร้านน้องส้ม" --wait
```

```text
NAME: hello
LAST DEPLOYED: Tue Oct  6 05:48:59 2026
NAMESPACE: helm-demo
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
1. Get the application URL by running these commands:
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl -n helm-demo port-forward deploy/hello-podinfo 8080:9898

real	0m12.221s
```

คำสั่งเดียว: สร้าง namespace (`--create-namespace`), render chart ด้วยค่าที่ `--set`, ส่ง object เข้า API server, รอจนพร้อม (`--wait`) แล้วพิมพ์ **NOTES** (การ์ดต้อนรับจาก `templates/NOTES.txt` ของ chart) ใช้ 12.2 วินาที (รอบแรกที่ต้องดึง image อาจนานกว่านี้)

### ขั้นที่ 2: ดูสาขาที่เปิด

```bash
helm list -n helm-demo
helm status hello -n helm-demo | head -6
helm get values hello -n helm-demo
helm get manifest hello -n helm-demo | grep -E "^kind:|^# Source"
helm get metadata hello -n helm-demo
kubectl -n helm-demo get deploy,svc,pod
```

```text
NAME 	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART         	APP VERSION
hello	helm-demo	1       	2026-10-06 05:48:59.584834553 +0700 +07	deployed	podinfo-6.15.0	6.15.0
NAME: hello
LAST DEPLOYED: Tue Oct  6 05:48:59 2026
NAMESPACE: helm-demo
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
USER-SUPPLIED VALUES:
replicaCount: 2
ui:
  message: สวัสดีจากร้านน้องส้ม
# Source: podinfo/templates/service.yaml
kind: Service
# Source: podinfo/templates/deployment.yaml
kind: Deployment
NAME: hello
CHART: podinfo
VERSION: 6.15.0
APP_VERSION: 6.15.0
ANNOTATIONS:
LABELS: modifiedAt=1791240551,name=hello,owner=helm,status=deployed,version=1
DEPENDENCIES:
NAMESPACE: helm-demo
REVISION: 1
STATUS: deployed
DEPLOYED_AT: 2026-10-06T05:48:59+07:00
APPLY_METHOD: server-side apply
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-podinfo   2/2     2            2           12s

NAME                    TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)             AGE
service/hello-podinfo   ClusterIP   10.96.95.36   <none>        9898/TCP,9999/TCP   12s

NAME                                 READY   STATUS    RESTARTS   AGE
pod/hello-podinfo-5d74774f48-287kt   1/1     Running   0          12s
pod/hello-podinfo-5d74774f48-nblp6   1/1     Running   0          12s
```

<p align="center" id="fig-6">
  <img src="images/06-lab02-get.png" alt="รูปที่ 6 LAB 2 helm get" width="900"><br>
  <em><b>รูปที่ 6</b> helm get values/manifest/metadata ดูใบสั่ง พิมพ์เขียว และวิธี apply (server-side apply) ส่วนสมุดถูกเก็บเป็น Secret sh.helm.release.v1.hello.v1</em>
</p>

| คำสั่ง | ได้อะไร |
|---|---|
| `helm get values` | **ใบสั่ง** ที่เราส่ง (`USER-SUPPLIED VALUES`) — ไม่รวมค่าเริ่มต้น (ใส่ `--all` จะได้ทั้งหมด) |
| `helm get manifest` | **พิมพ์เขียว** = YAML ทุก object ที่ render แล้ว (`# Source:` บอกแม่พิมพ์ต้นทาง) |
| `helm get metadata` | ข้อมูลของ revision รวม **`APPLY_METHOD: server-side apply`** (Helm 4) |
| `helm get notes` | การ์ดต้อนรับ |

### ขั้นที่ 3: สมุดอยู่ที่ไหน และใครเป็นเจ้าของ field

```bash
kubectl -n helm-demo get secret -l owner=helm
kubectl get ns helm-demo --show-labels
kubectl -n helm-demo get deploy hello-podinfo -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
```

```text
NAME                          TYPE                 DATA   AGE
sh.helm.release.v1.hello.v1   helm.sh/release.v1   1      13s
NAME        STATUS   AGE   LABELS
helm-demo   Active   13s   kubernetes.io/metadata.name=helm-demo,name=helm-demo
helm Apply
kube-controller-manager Update
```

- สมุดหน้าแรก (revision 1) อยู่ใน **Secret** type `helm.sh/release.v1` ใน namespace ของ release เอง (LAB 4 และ 9 จะถอดดู)
- namespace ที่ `--create-namespace` สร้างมีแค่ label พื้นฐาน **ไม่มี label Pod Security** (ต่างจาก `som-shop` ที่ตั้งเองในบทที่ 4/12) ถ้าต้องการให้เตือนแบบ `restricted` ต้อง label เอง
- field ของ Deployment มีเจ้าของ 2 ราย: **`helm` (Apply = server-side apply)** และ `kube-controller-manager` (อัปเดต status) — ทฤษฎีหัวข้อ 9

### ขั้นที่ 4: เปิดร้าน podinfo

```bash
kubectl -n helm-demo port-forward svc/hello-podinfo 9898:9898 >/dev/null 2>&1 &
sleep 3
curl -s localhost:9898 | grep -E '"(hostname|version|message|color)"'
kill %1
```

```text
  "hostname": "hello-podinfo-5d74774f48-287kt",
  "version": "6.15.0",
  "color": "#34577c",
  "message": "สวัสดีจากร้านน้องส้ม",
```

ข้อความภาษาไทยที่ `--set` ไปอยู่ในแอปแล้ว สียังเป็นค่าเริ่มต้นของ chart (`#34577c`)

### สิ่งที่เห็น

- `helm install ... --wait` ครั้งเดียวได้ Deployment + Service พร้อมใช้ (12.2 วินาที) และ `REVISION: 1`
- Helm จด release เป็น Secret `sh.helm.release.v1.hello.v1` และใช้ server-side apply (field manager `helm`)

**คำถามชวนคิด**

1. ถ้าลบ Secret `sh.helm.release.v1.hello.v1` ทิ้ง Pod ของ podinfo จะหายไหม แล้ว `helm list` จะเห็นอะไร
2. ทำไม `helm get values` ไม่แสดง `ui.color` ทั้งที่แอปใช้สี `#34577c`

**เก็บกวาด:** ไม่มี — release `hello` ใช้ต่อใน LAB 3–4

---

## LAB 3: ใบสั่งปรับแต่งร้าน (values)

<p align="center" id="fig-7">
  <img src="images/07-lab03-open.png" alt="รูปที่ 7 LAB 3 values" width="900"><br>
  <em><b>รูปที่ 7</b> LAB 3: ไฟล์ -f + --set (--set ชนะ) + Ingress podinfo.localhost ผ่าน Traefik</em>
</p>

**เป้าหมาย:** ใช้ใบสั่งเป็นไฟล์ (`-f`) ร่วมกับ `--set` ดูว่าใครชนะ เปิด Ingress ผ่านประตู Traefik เดิม แล้วเจอกับดักของ upgrade ที่ส่งค่ามาไม่ครบ

**ไฟล์:** `labs/lab03-values/podinfo-values.yaml`

### ขั้นที่ 1: ใบสั่งเป็นไฟล์ + --set

```bash
cat labs/lab03-values/podinfo-values.yaml
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo \
  -f labs/lab03-values/podinfo-values.yaml --set ui.message="--set ชนะ" --wait | grep -E "REVISION|STATUS"
kubectl -n helm-demo get deploy,ing
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
```

```text
# LAB 3: ใบสั่งปรับแต่งสาขา podinfo (ใช้กับ helm upgrade -f) — ค่าที่ส่งด้วย --set บนบรรทัดคำสั่งชนะค่าในไฟล์นี้
replicaCount: 3
ui:
  color: "#ff8c00"
  message: "ร้านน้องส้มสาขา values file"
ingress:
  enabled: true
  className: traefik
  hosts:
    - host: podinfo.localhost
      paths:
        - path: /
          pathType: Prefix
STATUS: deployed
REVISION: 2

real	0m24.518s
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-podinfo   3/3     3            3           40s

NAME                                      CLASS     HOSTS               ADDRESS     PORTS   AGE
ingress.networking.k8s.io/hello-podinfo   traefik   podinfo.localhost   localhost   80      24s
  "color": "#ff8c00",
  "message": "--set ชนะ",
```

- `message` ในไฟล์คือ `"ร้านน้องส้มสาขา values file"` แต่ `--set` ชนะ ได้ `--set ชนะ`
- `color` ไม่มีใน `--set` จึงมาจากไฟล์ (`#ff8c00` ส้มน้องส้ม)
- chart podinfo สร้าง Ingress `podinfo.localhost` ให้ Traefik ตัวเดิมของบท 012 (ยังเป็น static) — ลูกค้าเข้า `http://podinfo.localhost:30080` ได้เลย (`curl` ใน k8s-lab แปลงชื่อ `*.localhost` เป็น 127.0.0.1 เอง)

```bash
helm get values hello -n helm-demo
helm get values hello -n helm-demo --all | grep -E "^replicaCount|^  color|^  message"
```

```text
USER-SUPPLIED VALUES:
ingress:
  className: traefik
  enabled: true
  hosts:
  - host: podinfo.localhost
    paths:
    - path: /
      pathType: Prefix
replicaCount: 3
ui:
  color: '#ff8c00'
  message: --set ชนะ
replicaCount: 3
  color: '#ff8c00'
  message: --set ชนะ
```

`helm get values` แสดงใบสั่งที่ **merge ไฟล์ + `--set` แล้ว** (ไม่รู้ว่าค่าไหนมาจากไฟล์หรือจาก `--set`) ส่วน `--all` รวมค่าเริ่มต้นของ chart ทั้งหมดด้วย

### ขั้นที่ 2: ลองผิด — ส่งแค่ --set ค่าเดียว

```bash
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --set replicaCount=1 --wait | grep -E "REVISION|STATUS"
helm get values hello -n helm-demo
kubectl -n helm-demo get deploy,ing
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
```

```text
STATUS: deployed
REVISION: 3
USER-SUPPLIED VALUES:
replicaCount: 1
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-podinfo   1/1     1            1           43s
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
404
```

<p align="center" id="fig-8">
  <img src="images/08-lab03-reset-trap.png" alt="รูปที่ 8 LAB 3 กับดัก upgrade" width="900"><br>
  <em><b>รูปที่ 8</b> LAB 3: helm upgrade ... --set replicaCount=1 อย่างเดียว (ไม่ส่ง -f) = เหลือแค่ค่าที่ส่งครั้งนี้ ค่าอื่นกลับค่าเริ่มต้น (Ingress หาย ได้ 404) — ถ้า upgrade โดยไม่ส่งค่าเลยจะใช้ค่าเดิมต่อ; ใช้ --reuse-values หรือส่ง -f ทุกครั้ง</em>
</p>

ตั้งใจจะลดเหลือ 1 บูธ แต่ **ใบสั่งทั้งใบถูกแทน** ด้วย `replicaCount: 1` อย่างเดียว: สี ข้อความ และ Ingress กลับเป็นค่าเริ่มต้นของ chart (`ingress.enabled: false`) Ingress จึงถูกลบ ลูกค้าได้ `404 page not found` จาก Traefik — Helm คำนวณ values ของ upgrade จาก **ค่าเริ่มต้นของ chart + สิ่งที่ส่งมาในคำสั่งนี้** (ทฤษฎีหัวข้อ 6.4)

> ในรอบสำรวจก่อนเขียนเอกสาร ลอง `helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --wait` **โดยไม่ส่งค่าอะไรเลย** ผลคือ values ยังครบเหมือนเดิม (Helm 4.3 ใช้ค่าของ revision ก่อนเมื่อไม่ได้ส่งค่าใหม่) กับดักจึงเกิดเมื่อ "ส่งมาบางส่วน"

### ขั้นที่ 3: แก้ — ส่งไฟล์ทุกครั้ง หรือ --reuse-values

```bash
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f labs/lab03-values/podinfo-values.yaml --wait | grep -E "REVISION"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set ui.message="reuse-values จำค่าเดิม" --wait | grep -E "REVISION"
helm get values hello -n helm-demo | grep -E "replicaCount|message|color"
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
helm history hello -n helm-demo
```

```text
REVISION: 4
REVISION: 5
replicaCount: 3
  color: '#ff8c00'
  message: reuse-values จำค่าเดิม
  "color": "#ff8c00",
  "message": "reuse-values จำค่าเดิม",
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 05:48:59 2026	superseded	podinfo-6.15.0	6.15.0     	Install complete
2       	Tue Oct  6 05:49:15 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
3       	Tue Oct  6 05:49:40 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
4       	Tue Oct  6 05:49:43 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
5       	Tue Oct  6 05:49:58 2026	deployed  	podinfo-6.15.0	6.15.0     	Upgrade complete
```

- rev 4 ส่งไฟล์กลับไป ทุกอย่างกลับมา (Ingress ด้วย)
- rev 5 `--reuse-values` = **ใช้ใบสั่งของ revision ก่อน** แล้วทับด้วย `--set` ใหม่ `replicaCount: 3`, สี และ Ingress อยู่ครบ message เปลี่ยน
- สมุดมี 5 หน้า หน้าที่ "พัง" (rev 3) ยังอยู่ในประวัติ (`Upgrade complete` — Helm ไม่รู้ว่าเราไม่ได้ตั้งใจ)

### สิ่งที่เห็น

- ลำดับความสำคัญ: ค่าเริ่มต้นของ chart < `-f` < `--set`
- upgrade ที่ส่งค่ามาแค่บางตัว = ค่าอื่นกลับเป็นค่าเริ่มต้น (`404`) แก้ด้วยส่ง `-f` ทุกครั้งหรือ `--reuse-values`

**คำถามชวนคิด**

1. ถ้ามี 2 ไฟล์ `-f base.yaml -f override.yaml` ที่ตั้ง `ui.color` คนละค่า ใครชนะ และถ้ามี `--set ui.color=...` อีกล่ะ
2. ทำไมทีมส่วนใหญ่เลือก "ส่ง `-f` ทุกครั้ง" มากกว่า `--reuse-values` (คิดถึงการเก็บใบสั่งใน git และการอัปเกรดรุ่น chart)

**เก็บกวาด:** ไม่มี — release `hello` (rev 5) ใช้ต่อใน LAB 4

---

## LAB 4: สมุดบันทึกการปรับปรุงร้าน (history/rollback)

<p align="center" id="fig-9">
  <img src="images/09-lab04-open.png" alt="รูปที่ 9 LAB 4 สมุดบันทึก" width="900"><br>
  <em><b>รูปที่ 9</b> LAB 4: upgrade / history / rollback / rollback-on-failure / uninstall --keep-history</em>
</p>

**เป้าหมาย:** ทำให้ร้านพังด้วย image ที่ไม่มีอยู่จริง ดูว่า `--wait` สำคัญแค่ไหน ย้อนรุ่นทั้งแบบระบุเลขและไม่ระบุ ใช้ `--rollback-on-failure` ถอดสมุดใน Secret และใช้ `--keep-history`

> เลข revision ในขั้นนี้ต่อจาก LAB 3 (rev 5) ถ้าเครื่องของนักศึกษาเลขต่างไป ให้ดู `helm history hello -n helm-demo` แล้วแทนเลขในคำสั่ง rollback ด้วยเลขของตัวเอง

### ขั้นที่ 1: image ผิด โดยไม่ใส่ --wait

```bash
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope | grep -E "REVISION|STATUS"
sleep 15; kubectl -n helm-demo get pod
helm history hello -n helm-demo | tail -2
```

```text
STATUS: deployed
REVISION: 6

real	0m0.197s
NAME                             READY   STATUS         RESTARTS   AGE
hello-podinfo-56c6766d59-tl2gs   0/1     ErrImagePull   0          15s
hello-podinfo-56c6766d59-w2xz5   0/1     ErrImagePull   0          15s
hello-podinfo-74df4fff9c-cxnf6   1/1     Running        0          50s
hello-podinfo-74df4fff9c-dsvtd   1/1     Running        0          50s
5       	Tue Oct  6 05:49:58 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
6       	Tue Oct  6 05:50:32 2026	deployed  	podinfo-6.15.0	6.15.0     	Upgrade complete
```

ใน **0.2 วินาที** Helm ตอบ `STATUS: deployed` และสมุดเขียน `Upgrade complete` ทั้งที่ Pod ใหม่ดึง image ไม่ได้ (`ErrImagePull`) ร้านยังเปิดได้เพราะ rolling update เก็บ Pod เก่าไว้ (`maxUnavailable` ของ chart) — **Helm 4 ไม่ใส่ `--wait` = ไม่รอดูว่าร้านพร้อมจริง** (กลยุทธ์ `hookOnly`)

### ขั้นที่ 2: rollback ระบุเลข

```bash
time helm rollback hello 5 -n helm-demo --wait
kubectl -n helm-demo get pod
helm history hello -n helm-demo | tail -2
```

```text
Rollback was a success! Happy Helming!

real	0m11.862s
NAME                             READY   STATUS    RESTARTS   AGE
hello-podinfo-74df4fff9c-cj86k   1/1     Running   0          12s
hello-podinfo-74df4fff9c-cxnf6   1/1     Running   0          62s
hello-podinfo-74df4fff9c-dsvtd   1/1     Running   0          62s
6       	Tue Oct  6 05:50:32 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
7       	Tue Oct  6 05:50:48 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 5
```

rollback ไป rev 5 ได้ **หน้าใหม่ rev 7** (`Rollback to 5`) เลข revision ไม่ถอยหลัง Pod ที่พังหายไป เหลือ Pod ของ ReplicaSet เดิม `74df4fff9c` 3 ตัว

### ขั้นที่ 3: --atomic (เก่า) และ --rollback-on-failure

```bash
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --atomic --dry-run=client 2>&1 | head -1
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope \
  --rollback-on-failure --timeout 40s 2>&1 | cut -c1-400
helm history hello -n helm-demo
kubectl -n helm-demo get pod
```

```text
Flag --atomic has been deprecated, use --rollback-on-failure instead
level=WARN msg="upgrade failed" name=hello error="resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3\ncontext deadline exceeded"
Error: UPGRADE FAILED: release hello failed, and has been rolled back due to rollback-on-failure being set: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3
context deadline exceeded

real	0m42.959s
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 05:48:59 2026	superseded	podinfo-6.15.0	6.15.0     	Install complete
2       	Tue Oct  6 05:49:15 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
3       	Tue Oct  6 05:49:40 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
4       	Tue Oct  6 05:49:43 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
5       	Tue Oct  6 05:49:58 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
6       	Tue Oct  6 05:50:32 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
7       	Tue Oct  6 05:50:48 2026	superseded	podinfo-6.15.0	6.15.0     	Rollback to 5
8       	Tue Oct  6 05:51:00 2026	failed    	podinfo-6.15.0	6.15.0     	Upgrade "hello" failed: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: ...
9       	Tue Oct  6 05:51:40 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 7
NAME                             READY   STATUS    RESTARTS   AGE
hello-podinfo-74df4fff9c-5kt75   1/1     Running   0          3s
hello-podinfo-74df4fff9c-cxnf6   1/1     Running   0          105s
hello-podinfo-74df4fff9c-dsvtd   1/1     Running   0          105s
```

<p align="center" id="fig-10">
  <img src="images/10-lab04-rollback-on-failure.png" alt="รูปที่ 10 LAB 4 rollback-on-failure" width="900"><br>
  <em><b>รูปที่ 10</b> LAB 4: image ผิด + --rollback-on-failure --timeout 40s: รอ ~43 วินาที ล้ม (rev 8 failed) แล้วถอยกลับเอง (rev 9 Rollback to 7); ระวัง helm rollback ไม่ใส่เลขจะถอยไปรุ่นก่อนหน้าแม้รุ่นนั้นล้ม</em>
</p>

- `--atomic` ยังใช้ได้แต่ขึ้นคำเตือน ให้ใช้ชื่อใหม่ `--rollback-on-failure`
- `--rollback-on-failure` รอเหมือน `--wait` พอครบ 40 วินาที Deployment ยังไม่พร้อม (`Updated: 2/3`) จึงบันทึก **rev 8 `failed`** แล้ว **ถอยเองเป็น rev 9 `Rollback to 7`** (rev 7 คือรุ่นที่ใช้อยู่ก่อน upgrade) ร้านกลับมาเป็น 3/3 ใช้เวลารวม ~43 วินาที

### ขั้นที่ 4: กับดัก — rollback ไม่ใส่เลข

```bash
helm rollback hello -n helm-demo
sleep 10; kubectl -n helm-demo get pod
helm history hello -n helm-demo | tail -3
```

```text
Rollback was a success! Happy Helming!
NAME                             READY   STATUS         RESTARTS   AGE
hello-podinfo-56c6766d59-6fkzj   0/1     ErrImagePull   0          10s
hello-podinfo-56c6766d59-cgrwx   0/1     ErrImagePull   0          10s
hello-podinfo-74df4fff9c-cxnf6   1/1     Running        0          115s
hello-podinfo-74df4fff9c-dsvtd   1/1     Running        0          115s
8       	Tue Oct  6 05:51:00 2026	failed    	podinfo-6.15.0	6.15.0     	Upgrade "hello" failed: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: ...
9       	Tue Oct  6 05:51:40 2026	superseded	podinfo-6.15.0	6.15.0     	Rollback to 7
10      	Tue Oct  6 05:51:43 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 8
```

"ย้อนกลับ" แต่ร้านกลับไปพัง: rollback ไม่ใส่เลข = ไป **revision ก่อนหน้า** (rev 8) **แม้ rev 8 เป็นรุ่นที่ `failed`** ได้ rev 10 `Rollback to 8` และ `ErrImagePull` อีกครั้ง (ไม่มี `--wait` ด้วย Helm จึงบอก success) แก้ด้วยการระบุเลข

```bash
time helm rollback hello 9 -n helm-demo --wait
helm history hello -n helm-demo | tail -2
curl -s http://podinfo.localhost:30080 | grep -E '"(message|version)"'
```

```text
Rollback was a success! Happy Helming!

real	0m2.602s
10      	Tue Oct  6 05:51:43 2026	superseded	podinfo-6.15.0	6.15.0     	Rollback to 8
11      	Tue Oct  6 05:51:53 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 9
  "version": "6.15.0",
  "message": "reuse-values จำค่าเดิม",
```

> **กติกา: `helm history` ก่อน แล้ว `helm rollback <ชื่อ> <เลข> --wait` เสมอ**

### ขั้นที่ 5: ถอดสมุดใน Secret

```bash
kubectl -n helm-demo get secret -l owner=helm,name=hello
kubectl -n helm-demo get secret sh.helm.release.v1.hello.v5 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d \
  | python3 -c 'import json,sys; r=json.load(sys.stdin); print(sorted(r.keys())); print(r["info"]["status"], r["info"]["description"], r["version"]); print(json.dumps(r["config"], ensure_ascii=False))'
```

```text
NAME                           TYPE                 DATA   AGE
sh.helm.release.v1.hello.v10   helm.sh/release.v1   1      13s
sh.helm.release.v1.hello.v11   helm.sh/release.v1   1      3s
sh.helm.release.v1.hello.v2    helm.sh/release.v1   1      2m41s
sh.helm.release.v1.hello.v3    helm.sh/release.v1   1      2m16s
sh.helm.release.v1.hello.v4    helm.sh/release.v1   1      2m13s
sh.helm.release.v1.hello.v5    helm.sh/release.v1   1      118s
sh.helm.release.v1.hello.v6    helm.sh/release.v1   1      84s
sh.helm.release.v1.hello.v7    helm.sh/release.v1   1      68s
sh.helm.release.v1.hello.v8    helm.sh/release.v1   1      56s
sh.helm.release.v1.hello.v9    helm.sh/release.v1   1      16s
['apply_method', 'chart', 'config', 'hooks', 'info', 'manifest', 'name', 'namespace', 'version']
superseded Upgrade complete 5
{"ingress": {"className": "traefik", "enabled": true, "hosts": [{"host": "podinfo.localhost", "paths": [{"path": "/", "pathType": "Prefix"}]}]}, "replicaCount": 3, "ui": {"color": "#ff8c00", "message": "reuse-values จำค่าเดิม"}}
```

- มี 10 ซอง (v2–v11) **v1 หายไป** เพราะ Helm เก็บแค่ 10 revision ล่าสุด (`HELM_MAX_HISTORY="10"`)
- 1 ซอง = 1 หน้าในสมุด ถอดด้วย `base64 -d` (ชั้นของ Secret) → `base64 -d` (ชั้นของ Helm) → `gzip -d` ได้ JSON ที่มี `config` (ใบสั่ง) และ `manifest` (พิมพ์เขียว) — rollback ใช้ข้อมูลจากซองเหล่านี้ (ทฤษฎีหัวข้อ 10)

### ขั้นที่ 6: uninstall --keep-history แล้วเปิดร้านกลับ

```bash
helm uninstall hello -n helm-demo --keep-history
helm list -n helm-demo
helm list -n helm-demo --uninstalled
kubectl -n helm-demo get all
helm history hello -n helm-demo | tail -2
helm install hello podinfo/podinfo --version 6.15.0 -n helm-demo 2>&1 | tail -1
time helm rollback hello 11 -n helm-demo --wait
helm list -n helm-demo
kubectl -n helm-demo get deploy
```

```text
release "hello" uninstalled
NAME 	NAMESPACE	REVISION	UPDATED                                	STATUS     	CHART         	APP VERSION
hello	helm-demo	11      	2026-10-06 05:51:53.579882785 +0700 +07	uninstalled	podinfo-6.15.0	6.15.0
NAME 	NAMESPACE	REVISION	UPDATED                                	STATUS     	CHART         	APP VERSION
hello	helm-demo	11      	2026-10-06 05:51:53.579882785 +0700 +07	uninstalled	podinfo-6.15.0	6.15.0
NAME                                 READY   STATUS        RESTARTS   AGE
pod/hello-podinfo-74df4fff9c-cxnf6   1/1     Terminating   0          118s
pod/hello-podinfo-74df4fff9c-dsvtd   1/1     Terminating   0          118s
pod/hello-podinfo-74df4fff9c-z2bl8   1/1     Terminating   0          3s
10      	Tue Oct  6 05:51:43 2026	superseded 	podinfo-6.15.0	6.15.0     	Rollback to 8
11      	Tue Oct  6 05:51:53 2026	uninstalled	podinfo-6.15.0	6.15.0     	Uninstallation complete
Error: INSTALLATION FAILED: release name check failed: cannot reuse a name that is still in use
Rollback was a success! Happy Helming!

real	0m2.574s
NAME 	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART         	APP VERSION
hello	helm-demo	12      	2026-10-06 05:51:56.697674683 +0700 +07	deployed	podinfo-6.15.0	6.15.0
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
hello-podinfo   3/3     3            3           3s
```

<p align="center" id="fig-11">
  <img src="images/11-lab04-keep-history.png" alt="รูปที่ 11 LAB 4 keep-history" width="900"><br>
  <em><b>รูปที่ 11</b> uninstall --keep-history: ร้านถูกรื้อแต่สมุดยังอยู่ (uninstalled) → helm rollback เปิดร้านกลับมาได้</em>
</p>

- Helm 4 **ไม่มี `helm list -a` แล้ว** และ `helm list` เฉย ๆ ก็แสดง release สถานะ `uninstalled` (เหมือน `--uninstalled`)
- ระหว่างที่สมุดยังอยู่ ติดตั้งชื่อเดิมไม่ได้ (`cannot reuse a name that is still in use`) ต้อง rollback หรือ `upgrade --install`
- `helm rollback hello 11` เปิดร้านกลับมาเป็น rev 12 ใน 2.6 วินาที

### ขั้นที่ 7: uninstall จริง

```bash
helm uninstall hello -n helm-demo --wait
helm history hello -n helm-demo
kubectl -n helm-demo get secret -l owner=helm
kubectl delete ns helm-demo
```

```text
release "hello" uninstalled
Error: release: not found
No resources found in helm-demo namespace.
namespace "helm-demo" deleted
```

uninstall ปกติลบสมุดทั้งเล่ม (`release: not found`) namespace ที่ `--create-namespace` สร้างไม่ใช่ส่วนของ release ต้องลบเอง

### สิ่งที่เห็น

- ไม่ใส่ `--wait` = `deployed` ใน 0.2 วินาทีทั้งที่ Pod พัง
- rollback เขียนหน้าใหม่ (`Rollback to N`) และ rollback ไม่ใส่เลขถอยไปรุ่นที่ `failed` ได้
- `--rollback-on-failure --timeout 40s` ≈ 43 วินาที: rev 8 `failed` → rev 9 `Rollback to 7`
- สมุดเก็บ 10 หน้าเป็น Secret ถอดอ่านได้, `--keep-history` เปิดร้านกลับได้

**คำถามชวนคิด**

1. ทำไม `helm rollback hello 9` (rev 11) ใช้แค่ 2.6 วินาที แต่ `helm rollback hello 5` (rev 7) ใช้ 11.9 วินาที
2. ใน CI ที่ deploy อัตโนมัติ ควรใช้ `--wait` อย่างเดียว หรือ `--rollback-on-failure` และการถอยอัตโนมัติมีข้อเสียอะไร
3. ถ้า revision ที่ต้องการย้อนไปเก่ากว่า 10 รุ่นล่าสุดจะทำอย่างไร

**เก็บกวาด:** ลบแล้วในขั้นที่ 7 (`helm-demo` ไม่มีแล้ว)

---

