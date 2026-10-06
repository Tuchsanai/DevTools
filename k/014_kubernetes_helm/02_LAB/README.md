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

คำสั่ง `helm`, `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้น `docker cp` (🖥️) และการเปิดร้าน/dashboard ใน browser (🌐) LAB 9 (ขั้นที่ 7), LAB 10 และ LAB 12 ใช้ **2 หน้าต่าง SSH** (หน้าต่างหนึ่งดู Pod หรือยิงลูกค้าจำลองด้วย `hit.sh` อีกหน้าต่างสั่ง helm) ให้เปิดไว้ตั้งแต่แรก

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

build + load ใช้ **6.5 วินาที** เพราะ docker ใช้ cache ของขั้นติดตั้ง package และ build Next.js จากการ build 1.7 ในบท 013 (โค้ดเหมือนกัน) ส่วน `APP_VERSION` ถูกตั้งเฉพาะใน stage สุดท้ายของ `Dockerfile` ถ้าไม่มี cache (คลัสเตอร์ใหม่) จะใช้ราว 40–45 วินาที

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

ใน **0.2 วินาที** Helm ตอบ `STATUS: deployed` และสมุดเขียน `Upgrade complete` ทั้งที่ Pod ใหม่ดึง image ไม่ได้ (`ErrImagePull`) ร้านยังเปิดได้เพราะ rolling update ยังเก็บ Pod เก่าไว้บางส่วน (2 จาก 3) — **Helm 4 ไม่ใส่ `--wait` = ไม่รอดูว่าร้านพร้อมจริง** (กลยุทธ์ `hookOnly`)

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

## LAB 5: ชุดแฟรนไชส์ชุดแรกของเรา (helm create)

<p align="center" id="fig-12">
  <img src="images/12-lab05-open.png" alt="รูปที่ 12 LAB 5 helm create" width="900"><br>
  <em><b>รูปที่ 12</b> LAB 5: helm create mychart → lint → template → install → helm test --logs</em>
</p>

**เป้าหมาย:** สร้าง chart ตัวอย่างด้วย `helm create` อ่านโครงสร้าง ตรวจ render ติดตั้ง และสั่งผู้ตรวจรับร้าน

**ไฟล์:** สร้างใน `labs/lab05-first/mychart/` (ไม่เข้า git)

### ขั้นที่ 1: สร้างและดูโครง

```bash
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab05-first
helm create mychart
find mychart -type f | sort
grep -vE "^\s*#|^$" mychart/Chart.yaml
grep -nE "^replicaCount|^image:|^  repository|^  tag|^service:|^  type|^  port" mychart/values.yaml
```

```text
Creating mychart
mychart/.helmignore
mychart/Chart.yaml
mychart/templates/NOTES.txt
mychart/templates/_helpers.tpl
mychart/templates/deployment.yaml
mychart/templates/hpa.yaml
mychart/templates/httproute.yaml
mychart/templates/ingress.yaml
mychart/templates/service.yaml
mychart/templates/serviceaccount.yaml
mychart/templates/tests/test-connection.yaml
mychart/values.yaml
apiVersion: v2
name: mychart
description: A Helm chart for Kubernetes
type: application
version: 0.1.0
appVersion: "1.16.0"
6:replicaCount: 1
9:image:
10:  repository: nginx
14:  tag: ""
53:service:
55:  type: ClusterIP
57:  port: 80
```

> image `k8s-lab` **ไม่มีคำสั่ง `tree`** (`tree: command not found`) จึงใช้ `find ... | sort` ดูโครงแทน

scaffold ของ Helm 4 ได้ chart `apiVersion: v2` ที่มีครบทุกส่วนของทฤษฎีหัวข้อ 4: `_helpers.tpl`, `NOTES.txt`, `tests/` และแม่พิมพ์ที่ปิดไว้ด้วย `if` (hpa, ingress และ **`httproute.yaml`** ของ Gateway API ที่เพิ่มมาใน Helm 4) ไม่มี `values.schema.json` image เริ่มต้นคือ `nginx` tag ว่าง (= `appVersion` `1.16.0`)

### ขั้นที่ 2: lint และ template

```bash
helm lint mychart
helm template web mychart | grep -E "^kind:|image:"
```

```text
==> Linting mychart
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
kind: ServiceAccount
kind: Service
kind: Deployment
          image: "nginx:1.16.0"
kind: Pod
      image: busybox
```

lint ผ่าน (`[INFO]` เป็นแค่คำแนะนำ) render ได้ 4 object: ServiceAccount, Service, Deployment (`nginx:1.16.0` จาก `default .Chart.AppVersion`) และ Pod ทดสอบ (`busybox`) ส่วน hpa/ingress/httproute ไม่ถูก render เพราะค่าเริ่มต้นปิดไว้

### ขั้นที่ 3: ติดตั้งและตรวจรับ

```bash
time helm install web mychart -n first --create-namespace --wait
kubectl -n first get deploy,svc,pod
helm test web -n first --logs
kubectl -n first get pod
```

```text
NAME: web
LAST DEPLOYED: Tue Oct  6 05:52:11 2026
NAMESPACE: first
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace first -l "app.kubernetes.io/name=mychart,app.kubernetes.io/instance=web" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace first $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace first port-forward $POD_NAME 8080:$CONTAINER_PORT

real	0m7.353s
NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-mychart   1/1     1            1           7s

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/web-mychart   ClusterIP   10.96.212.11   <none>        80/TCP    7s

NAME                               READY   STATUS    RESTARTS   AGE
pod/web-mychart-5fd4677f4c-5t8np   1/1     Running   0          7s
NAME: web
LAST DEPLOYED: Tue Oct  6 05:52:11 2026
NAMESPACE: first
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE:     web-mychart-test-connection
Last Started:   Tue Oct  6 05:52:19 2026
Last Completed: Tue Oct  6 05:52:26 2026
Phase:          Succeeded

POD LOGS: web-mychart-test-connection (wget)
Connecting to web-mychart:80 (10.96.212.11:80)
saving to 'index.html'
index.html           100% |********************************|   612  0:00:00 ETA
'index.html' saved

NAME                           READY   STATUS      RESTARTS   AGE
web-mychart-5fd4677f4c-5t8np   1/1     Running     0          15s
web-mychart-test-connection    0/1     Completed   0          7s
```

- ชื่อ object = `<release>-<chart>` (`web-mychart`) ตามตรายาง `mychart.fullname` ของ scaffold
- `helm test` สร้าง Pod `web-mychart-test-connection` ที่ `wget` ไปยัง Service ได้หน้า nginx (612 ไบต์) จบด้วย exit 0 = **`Phase: Succeeded`**
- Pod ทดสอบของ scaffold ค้างเป็น `Completed` เพราะไม่ได้ตั้ง `hook-delete-policy` ให้ลบเมื่อสำเร็จ (ชุดร้านใน LAB 9 ตั้งไว้)

### สิ่งที่เห็น

- `helm create` ได้ chart ที่ใช้งานได้ทันที (lint ผ่าน, install 7.4 วินาที, test `Succeeded`)
- อ่านแม่พิมพ์ของ scaffold เป็นตัวอย่างการใช้ `include`, `with`, `toYaml | nindent` จริง

**คำถามชวนคิด**

1. เปิด `mychart/templates/deployment.yaml` หาบรรทัด `image:` แล้วอธิบายว่า `nginx:1.16.0` มาจากไหนบ้าง
2. ถ้าแก้ `values.yaml` แล้วอยากให้คนอื่นรู้ว่า chart เปลี่ยน ต้องแก้อะไรใน `Chart.yaml`

**เก็บกวาด:** ยังไม่ลบ — LAB 6 คัดลอก `mychart` ไปทำแม่พิมพ์พัง และใช้ release `web` (namespace `first`) ต่อ

---

## LAB 6: แม่พิมพ์พัง: render และ debug

<p align="center" id="fig-13">
  <img src="images/13-lab06-open.png" alt="รูปที่ 13 LAB 6 แม่พิมพ์พัง" width="900"><br>
  <em><b>รูปที่ 13</b> LAB 6: ทำแม่พิมพ์พัง 4 แบบ แล้วหาจุดผิดด้วย helm lint / helm template --debug</em>
</p>

**เป้าหมาย:** อ่าน error ของ Helm 4 แต่ละแบบ หาบรรทัดที่ผิด และเห็นช่องโหว่ของ `--dry-run=server`

**ไฟล์:** `labs/lab06-debug/make-broken.sh` (คัดลอก `../lab05-first/mychart` เป็น `broken-indent`, `broken-func`, `broken-required`, `broken-v3` แล้วแก้ด้วย `sed` โฟลเดอร์ละ 1 จุด รันซ้ำได้)

### ขั้นที่ 1: สร้างแม่พิมพ์พัง

```bash
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab06-debug
bash make-broken.sh
```

```text
=== broken-indent (บรรทัดที่ต่างจาก mychart)
>         {{- toYaml . | indent 2 }}
> podLabels: {shop: som}
=== broken-func (บรรทัดที่ต่างจาก mychart)
>         {{- toYml . | nindent 8 }}
>         {{- toYml . | nindent 8 }}
>         {{- toYml . | nindent 8 }}
=== broken-required (บรรทัดที่ต่างจาก mychart)
>           image: "{{ required "ต้องใส่ image.repository" .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
=== broken-v3 (บรรทัดที่ต่างจาก mychart)
> apiVersion: v3
```

### ขั้นที่ 2: indent แทน nindent (YAML พัง)

```bash
helm lint broken-indent
helm template web broken-indent 2>&1 | tail -3
helm template web broken-indent --debug 2>&1 | grep -n -B2 -A3 "shop: som" | head -12
```

```text
Error: 1 chart(s) linted, 1 chart(s) failed
==> Linting broken-indent
[INFO] Chart.yaml: icon is recommended
[ERROR] templates/deployment.yaml: unable to parse YAML: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context

Error: YAML parse error on mychart/templates/deployment.yaml: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context

Use --debug flag to render out invalid YAML
50-        app.kubernetes.io/instance: web
51-        app.kubernetes.io/version: "1.16.0"
52:        app.kubernetes.io/managed-by: Helm  shop: som
53-    spec:
54-      serviceAccountName: web-mychart
55-      containers:
```

`line 24` คือบรรทัดของ **ผล render** ของไฟล์นั้น ไม่ใช่บรรทัดใน template `--debug` พิมพ์ YAML ที่พังออกมาให้เห็น: `indent 2` ไม่ขึ้นบรรทัดใหม่ และ `{{-` ตัดบรรทัดก่อนหน้า label `shop: som` จึงไปต่อท้าย `managed-by: Helm` ในบรรทัดเดียวกัน (ทฤษฎีหัวข้อ 5.4)

### ขั้นที่ 3: ชื่อฟังก์ชันผิด

```bash
helm lint broken-func 2>&1 | tail -4
```

```text
[INFO] Chart.yaml: icon is recommended
[ERROR] templates/: parse error at (mychart/templates/deployment.yaml:18): function "toYml" not defined

Error: 1 chart(s) linted, 1 chart(s) failed
```

error นี้เกิดตอน **parse template** (ก่อน render) บอกไฟล์และบรรทัดของ template ตรง ๆ (`deployment.yaml:18`)

### ขั้นที่ 4: required

```bash
helm template web broken-required --set image.repository= 2>&1 | head -3
helm template web broken-required | grep "image:" | head -1
```

```text
Error: execution error at (mychart/templates/deployment.yaml:41:21): ต้องใส่ image.repository

Use --debug flag to render out invalid YAML
          image: "nginx:1.16.0"
```

`required` หยุด render พร้อมข้อความที่เราเขียนเองและตำแหน่ง `บรรทัด:คอลัมน์` ถ้ามีค่า (`nginx` จากค่าเริ่มต้น) ก็ผ่านตามปกติ

### ขั้นที่ 5: chart apiVersion v3

```bash
helm lint broken-v3 2>&1 | tail -4
HELM_EXPERIMENTAL_CHART_V3=1 helm lint broken-v3 2>&1 | tail -3
sed -i '/^type:/d' broken-v3/Chart.yaml
helm lint broken-v3 2>&1
helm template web broken-v3 2>&1 | head -3
```

```text
[INFO] Chart.yaml: icon is recommended
[ERROR] Chart.yaml: chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'

Error: 1 chart(s) linted, 1 chart(s) failed
[ERROR] Chart.yaml: chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'

Error: 1 chart(s) linted, 1 chart(s) failed
==> Linting broken-v3
[ERROR] Chart.yaml: apiVersion 'v3' is not valid. The value must be either "v1" or "v2"
[INFO] Chart.yaml: icon is recommended

Error: 1 chart(s) linted, 1 chart(s) failed
Error: invalid chart apiVersion
```

chart API v3 ของ Helm 4 **ยังเป็นงานทดลอง** แม้ตั้ง `HELM_EXPERIMENTAL_CHART_V3=1` ก็ยังใช้ไม่ได้ ข้อความแรกบ่นเรื่องบรรทัด `type:` ลบออกแล้วจึงเห็นข้อความหลัก `apiVersion 'v3' is not valid` — chart ที่เขียนวันนี้ใช้ `apiVersion: v2`

### ขั้นที่ 6: ช่องโหว่ของ --dry-run=server

ใช้ `mychart` ที่ดี แต่พิมพ์ค่าผิด `service.type=NodePortt`

```bash
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | head -8
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | grep -n "type:"
helm template web2 ../lab05-first/mychart --set service.type=NodePortt | kubectl apply --dry-run=server -n first -f - 2>&1 | tail -3
```

```text
NAME: web2
LAST DEPLOYED: Tue Oct  6 05:52:33 2026
NAMESPACE: first
STATUS: pending-install
REVISION: 1
DESCRIPTION: Dry run complete
HOOKS:
---
58:  type: NodePortt
deployment.apps/web2-mychart created (server dry run)
pod/web2-mychart-test-connection created (server dry run)
The Service "web2-mychart" is invalid: spec.type: Unsupported value: "NodePortt": supported values: "ClusterIP", "ExternalName", "LoadBalancer", "NodePort"
```

<p align="center" id="fig-14">
  <img src="images/14-lab06-dryrun-gap.png" alt="รูปที่ 14 LAB 6 ช่องโหว่ของ dry-run=server" width="900"><br>
  <em><b>รูปที่ 14</b> helm install --dry-run=server ผ่าน (Dry run complete) แต่ kubectl apply --dry-run=server จับ spec.type ผิดได้ — ตรวจสองชั้น</em>
</p>

`helm install --dry-run=server` ของ Helm 4.3.0 ตอบ `Dry run complete` ทั้งที่ manifest มี `type: NodePortt` (Helm ใช้ "server" เพื่อให้ `lookup` เห็นคลัสเตอร์ แต่ไม่ได้ส่ง object ให้ API server ตรวจ) ส่วน `kubectl apply --dry-run=server` ส่งให้ API server validate จริงจึงจับได้ ถ้าติดตั้งจริงล่ะ

```bash
helm install web2 ../lab05-first/mychart -n first --set service.type=NodePortt 2>&1 | tail -2
helm list -n first
helm uninstall web2 -n first
helm list -n first
```

```text
Error: INSTALLATION FAILED: server-side apply failed for object first/web2-mychart /v1, Kind=Service: Service "web2-mychart" is invalid: spec.type: Unsupported value: "NodePortt": supported values: "ClusterIP", "ExternalName", "LoadBalancer", "NodePort"
NAME	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART        	APP VERSION
web 	first    	1       	2026-10-06 05:52:11.552625655 +0700 +07	deployed	mychart-0.1.0	1.16.0
web2	first    	1       	2026-10-06 05:52:34.197006681 +0700 +07	failed  	mychart-0.1.0	1.16.0
release "web2" uninstalled
NAME	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART        	APP VERSION
web 	first    	1       	2026-10-06 05:52:11.552625655 +0700 +07	deployed	mychart-0.1.0	1.16.0
```

install จริงล้มที่ API server **และทิ้ง release `web2` สถานะ `failed` ไว้** (object ที่สร้างไปแล้วบางตัวอาจค้างด้วย) ต้อง `helm uninstall web2` เอง ไม่งั้น install ชื่อเดิมซ้ำไม่ได้

> **ตรวจสองชั้นก่อนติดตั้งของสำคัญ:** `helm lint` + `helm template` (รูปแบบ chart) แล้ว `helm template ... | kubectl apply --dry-run=server -f -` (ความถูกต้องของ object)

### สิ่งที่เห็น

| แบบ | ข้อความหลัก | ชี้ไปที่ |
|---|---|---|
| ย่อหน้าผิด | `yaml: line 24: mapping values are not allowed in this context` | บรรทัดของผล render (ใช้ `--debug`) |
| ฟังก์ชันผิด | `function "toYml" not defined` | `deployment.yaml:18` ของ template |
| ลืมค่า | `execution error at (...deployment.yaml:41:21): ต้องใส่ image.repository` | บรรทัด:คอลัมน์ของ template |
| chart v3 | `apiVersion 'v3' is not valid` / `invalid chart apiVersion` | `Chart.yaml` |
| field ผิด | `Dry run complete` (helm) vs `spec.type: Unsupported value` (kubectl) | ต้องตรวจด้วย API server |

**คำถามชวนคิด**

1. ทำไม error ของ `toYml` บอกบรรทัดของไฟล์ template ได้ตรง ๆ แต่ error ของ indent บอกบรรทัดของผล render
2. ถ้าจะใส่ขั้นตรวจ chart ลงใน CI จะเรียงคำสั่งอะไรบ้าง

**เก็บกวาด LAB 5–6:**

```bash
helm uninstall web -n first; kubectl delete ns first
```

```text
release "web" uninstalled
namespace "first" deleted
```

โฟลเดอร์ `labs/lab05-first/mychart` และ `labs/lab06-debug/broken-*` เก็บไว้ดูได้ (ไม่เข้า git) หรือลบด้วย `rm -rf labs/lab05-first/mychart labs/lab06-debug/broken-*` (สั่งในโฟลเดอร์ `02_LAB`)

---

## LAB 7: แม่พิมพ์ร้านน้องส้ม (template functions)

<p align="center" id="fig-15">
  <img src="images/15-lab07-open.png" alt="รูปที่ 15 LAB 7 อ่านแม่พิมพ์" width="900"><br>
  <em><b>รูปที่ 15</b> LAB 7: อ่านแม่พิมพ์ som-shop — range การ์ดกระดาน, if hpa ไม่ใส่ replicas, include ตรายาง, toYaml resources</em>
</p>

**เป้าหมาย:** อ่านชุดแฟรนไชส์ `charts/som-shop` และพิสูจน์ด้วย `helm template` ว่าแต่ละฟังก์ชันให้ผลอะไร (ไม่ติดตั้งอะไร ไม่ต่อคลัสเตอร์)

**ไฟล์:** `charts/som-shop/` (ใส่ `--set db.password=x` ทุกครั้งเพราะ `helm template` ไม่ต่อคลัสเตอร์ — LAB 8 อธิบาย)

### ขั้นที่ 1: โครงชุดและตรายาง

```bash
cd /workspace/014_kubernetes_helm/02_LAB
find charts -type f | sort
cat charts/som-shop/Chart.yaml
grep -n "define" charts/som-shop/templates/_helpers.tpl
```

```text
charts/som-shop/.helmignore
charts/som-shop/Chart.yaml
charts/som-shop/templates/NOTES.txt
charts/som-shop/templates/_helpers.tpl
charts/som-shop/templates/configmap.yaml
charts/som-shop/templates/db.yaml
charts/som-shop/templates/hpa.yaml
charts/som-shop/templates/ingress.yaml
charts/som-shop/templates/secret.yaml
charts/som-shop/templates/seed-job.yaml
charts/som-shop/templates/tests/test-health.yaml
charts/som-shop/templates/web.yaml
charts/som-shop/values.schema.json
charts/som-shop/values.yaml
charts/values-dev.yaml
charts/values-prod.yaml
# ชุดแฟรนไชส์ร้านอาหารแมวน้องส้ม (บท 014) — chart API v2 (Helm 3 และ Helm 4 ใช้ได้)
apiVersion: v2
name: som-shop
description: ร้านอาหารแมวน้องส้ม — หน้าร้าน Next.js + ครัว PostgreSQL + Ingress + HPA
type: application
version: 0.1.0          # เวอร์ชันของ chart (ชุดแฟรนไชส์) — แก้ทุกครั้งที่แก้ templates
appVersion: "1.7"       # เวอร์ชันแอปเริ่มต้น = tag ของ som-shop-web ถ้าไม่ได้ตั้ง web.image.tag
kubeVersion: ">=1.30.0-0"
keywords: [som-shop, kubernetes-lab]
4:{{- define "som-shop.fullname" -}}
9:{{- define "som-shop.labels" -}}
18:{{- define "som-shop.webImage" -}}
23:{{- define "som-shop.dbPassword" -}}
```

เทียบแม่พิมพ์กับไฟล์ YAML ของบท 013

| แม่พิมพ์ | object ที่ได้ (release `som`) | แทนไฟล์บท 013 |
|---|---|---|
| `configmap.yaml` | ConfigMap `som-web-config`, `som-announcement` | `15-config.yaml` |
| `secret.yaml` | Secret `som-db-secret` | สร้างเองด้วย `kubectl create secret` (บท 011) |
| `db.yaml` | Service `som-db` + StatefulSet `som-db` | `10-db.yaml` |
| `web.yaml` | Deployment + Service `som-web` | `20-web.yaml` |
| `hpa.yaml` | HPA `som-web` | `60-hpa.yaml` |
| `ingress.yaml` | Ingress `som-web` (+ Secret `som-tls`, Middleware `som-redirect-https` เมื่อ tls) | `50-ingress.yaml` + `kubectl create secret tls` |
| `seed-job.yaml` | Job `som-seed` (hook) | initContainer `db-seed` ใน `20-web.yaml` |
| `tests/test-health.yaml` | Pod `som-test-health` (test) | — (ใหม่) |

ชุดนี้ **ไม่มี** หลังร้าน `som-admin` และลูกค้าจำลอง `customers` (LAB 12 จัดการของสองอย่างนี้)

### ขั้นที่ 2: range — การ์ดบนกระดานประกาศ

```bash
helm template som charts/som-shop --set db.password=x --show-only templates/configmap.yaml
```

```text
---
# Source: som-shop/templates/configmap.yaml
# กระดานประกาศ 2 แผ่น: ป้ายร้าน (envFrom) + ประกาศหน้าร้าน (mount เป็นไฟล์)
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.7"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
data:
  APP_THEME: "harbor"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · Helm"
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 014 · ติดตั้งทั้งร้านด้วย Helm"
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  SHOP_PROMO: ""


---
# Source: som-shop/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-announcement
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.7"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
data:
  announcement.txt: "วันนี้ปลาทูสดมาก 🐟\n"
```

- `range $key, $value := .Values.shop` สร้างการ์ด 5 ใบ **เรียงตามตัวอักษรของ key** (APP_THEME มาก่อน SHOP_*) ไม่ใช่ตามลำดับใน `values.yaml`
- ทุกค่าครอบ `quote` (`SHOP_PROMO: ""` ยังเป็นข้อความว่าง ไม่ใช่ `null`)
- label 5 บรรทัดมาจากตรายาง `som-shop.labels` ตัวเดียว
- ป้ายหัวร้านเปลี่ยนเป็น `⚓ ท่าเรือ Kubernetes · Helm` (บท 013 เป็น `· HPA`)

### ขั้นที่ 3: if — replicas หายเมื่อเปิด HPA

```bash
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep -nE "^kind:|replicas:|image:|checksum"
helm template som charts/som-shop --set db.password=x --set hpa.enabled=true --show-only templates/web.yaml | grep -nE "^kind:|replicas:|image:"
```

```text
4:kind: Service
25:kind: Deployment
35:  replicas: 2
49:        # แก้กระดานประกาศ/ซอง → ค่า checksum เปลี่ยน → ได้ Pod ใหม่เอง (ไม่ต้อง rollout restart)
50:        checksum/config: 26b21079c94c41e739e54c86e0e6bc3b645c05616ab6adc55adccc304e8ec8fd
51:        checksum/secret: 2548f708d02bc8233b43c88f4e535af3aafba6687be9427412f7330e9871ec36
59:          image: postgres:17.11-alpine
75:          image: som-shop-web:1.7
4:kind: Service
25:kind: Deployment
58:          image: postgres:17.11-alpine
74:          image: som-shop-web:1.7
```

`hpa.enabled=false` (ค่าเริ่มต้น) มี `replicas: 2` แต่ `hpa.enabled=true` บรรทัด `replicas:` **หายไป** — แม่พิมพ์แก้กับดัก "replicas ใน YAML ทับ HPA" ของบท 013 LAB 10 ไว้ในตัว (image `postgres:17.11-alpine` คือ initContainer `wait-for-db`)

### ขั้นที่ 4: toYaml | nindent และ checksum

```bash
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep -A6 "^          resources:"
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep "checksum/config"
helm template som charts/som-shop --set db.password=x --set shop.SHOP_PROMO="ลด 50%" --show-only templates/web.yaml | grep "checksum/config"
```

```text
          resources:
            requests: {cpu: 10m, memory: 16Mi}
            limits: {cpu: 100m, memory: 64Mi}
      volumes:
        - name: announcement
          configMap:
            name: som-announcement
--
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 192Mi
        checksum/config: 26b21079c94c41e739e54c86e0e6bc3b645c05616ab6adc55adccc304e8ec8fd
        checksum/config: 25db4af18147f3bcf17521bf2bf231118fabf17c112d4dc934b5b08c0ab74532
```

- ก้อนแรกเป็น resources ของ initContainer ที่เขียนตรงในแม่พิมพ์ ก้อนที่สองคือหน้าร้านที่มาจาก `toYaml .Values.web.resources | nindent 12` (ย่อหน้า 12 ช่องพอดีใต้ `resources:`)
- แก้แค่ `SHOP_PROMO` ลายนิ้วมือ `checksum/config` เปลี่ยนจาก `26b21079…` เป็น `25db4af1…` → upgrade จริงจะได้ Pod ใหม่เอง (LAB 9 พิสูจน์)

### ขั้นที่ 5: fullnameOverride และ label ตาม tag

```bash
helm template som charts/som-shop --set db.password=x --set fullnameOverride=shop2 | grep -E "^  name:" | sort | uniq
helm template som charts/som-shop --set db.password=x | grep -E "^  name:" | sort | uniq
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.8 --show-only templates/secret.yaml
```

```text
  name: shop2-announcement
  name: shop2-db
  name: shop2-db-secret
  name: shop2-seed
  name: shop2-test-health
  name: shop2-web
  name: shop2-web-config
  name: som-announcement
  name: som-db
  name: som-db-secret
  name: som-seed
  name: som-test-health
  name: som-web
  name: som-web-config
---
# Source: som-shop/templates/secret.yaml
# ซองปิดผนึก: รหัสฐานข้อมูล + DATABASE_URL (Helm เก็บค่านี้ใน release Secret ด้วย — ถอดได้!)
apiVersion: v1
kind: Secret
metadata:
  name: som-db-secret
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.8"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
type: Opaque
stringData:
  POSTGRES_PASSWORD: "x"
  DATABASE_URL: "postgres://som:x@som-db-0.som-db:5432/catshop"
```

- release `som` → ชื่อ `som-*` **ตรงกับร้านบท 009–013 ทุกตัว** (LAB 12 จึงรับร้านเดิมได้) `fullnameOverride=shop2` เปลี่ยนคำนำหน้าทุกชิ้นพร้อมกัน
- `DATABASE_URL` ประกอบด้วย `printf` จากค่า user/รหัส/ชื่อ จึงไม่ต้องพิมพ์รหัสซ้ำ 2 ที่แบบบท 011
- label `app.kubernetes.io/version` ตาม tag ที่ส่ง (`"1.8"`) แต่ `helm.sh/chart` ยังเป็น `som-shop-0.1.0`

### สิ่งที่เห็น

- `range` วน key ตามตัวอักษร, `if` ทำให้ `replicas` หายเมื่อมี HPA, `include` ตรายางเดียวใช้ทุกไฟล์, `toYaml | nindent 12` ย่อหน้าตรง
- checksum เปลี่ยนเมื่อป้ายเปลี่ยน และชื่อ object ตามชื่อ release/`fullnameOverride`

**คำถามชวนคิด**

1. ถ้าเพิ่ม key ใหม่ `SHOP_HOURS: "9-18"` ใน `values-prod.yaml` ใต้ `shop:` ต้องแก้แม่พิมพ์ไหม แอปจะเห็นค่านี้อย่างไร
2. ทำไม label `app.kubernetes.io/version` ไม่ควรใส่ไว้ใน `spec.selector` ของ Deployment (คิดถึง selector ที่แก้ไม่ได้ ในบทที่ 7)

**เก็บกวาด:** ไม่มี (ไม่ได้ติดตั้งอะไร)

---

## LAB 8: ใบสั่งต่อสาขาและด่านตรวจ

<p align="center" id="fig-16">
  <img src="images/16-lab08-open.png" alt="รูปที่ 16 LAB 8 ใบสั่งต่อสาขา" width="900"><br>
  <em><b>รูปที่ 16</b> LAB 8: values-dev.yaml / values-prod.yaml + values.schema.json + required/lookup</em>
</p>

**เป้าหมาย:** เทียบผล render ของสาขา dev กับ prod ให้ด่านตรวจปฏิเสธใบสั่งผิด และเห็นความต่างของ `helm lint`/`template` (ไม่ต่อคลัสเตอร์) กับการติดตั้งจริง

**ไฟล์:** `charts/values-dev.yaml`, `charts/values-prod.yaml`, `charts/som-shop/values.schema.json`

### ขั้นที่ 1: ใบสั่ง 2 สาขา

```bash
cd /workspace/014_kubernetes_helm/02_LAB
cat charts/values-dev.yaml charts/values-prod.yaml
helm template som charts/som-shop -f charts/values-dev.yaml --set db.password=x | grep -E "^kind:" | sort | uniq -c
helm template som charts/som-shop -f charts/values-dev.yaml --set db.password=x | grep -E "^kind:" | wc -l
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x | grep -E "^kind:" | sort | uniq -c
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x | grep -E "^kind:" | wc -l
```

```text
# สาขาทดลอง (dev): บูธเดียว ไม่มี HPA ประตู http ธรรมดา ธีมส้ม
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม (dev)"
  APP_THEME: "sunset"
  SHOP_PROMO: "🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost"
web:
  replicas: 1
hpa:
  enabled: false
ingress:
  enabled: true
  host: dev.shop.localhost
  tls: false
# สาขาจริง (prod): HPA 2–6 บูธ ประตู HTTPS shop.localhost
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  APP_THEME: "harbor"
  SHOP_PROMO: "🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
ingress:
  enabled: true
  host: shop.localhost
  tls: true
      2 kind: ConfigMap
      1 kind: Deployment
      1 kind: Ingress
      1 kind: Job
      1 kind: Pod
      1 kind: Secret
      2 kind: Service
      1 kind: StatefulSet
10
      2 kind: ConfigMap
      1 kind: Deployment
      1 kind: HorizontalPodAutoscaler
      1 kind: Ingress
      1 kind: Job
      1 kind: Middleware
      1 kind: Pod
      2 kind: Secret
      2 kind: Service
      1 kind: StatefulSet
13
```

| | dev (10) | prod (13) |
|---|---|---|
| หน้าร้าน | 1 บูธ (`replicas: 1`) | HPA 2–6 (ไม่มี `replicas`) |
| ประตู | `http://dev.shop.localhost:30080` | `https://shop.localhost:30081` + Secret `som-tls` + Middleware redirect |
| ป้าย | `(dev)` ธีม `sunset` แถบ 🧪 | ธีม `harbor` แถบ 🎉 |
| ส่วนที่เหมือนกัน | db, ConfigMap, Secret, Job seed (hook), Pod test — มาจากแม่พิมพ์ชุดเดียวกัน | |

ใบสั่งแต่ละใบมีแค่ "ส่วนที่ต่าง" ไม่กี่บรรทัด ค่าอื่นมาจาก `values.yaml` ของชุด (จำนวน 10/13 นับ Job hook และ Pod test ด้วย)

### ขั้นที่ 2: ด่านตรวจปฏิเสธใบสั่ง

```bash
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.4 2>&1 | head -4
helm template som charts/som-shop --set db.password=x --set web.replicas=9 2>&1 | head -4
helm template som charts/som-shop --set db.password=x --set ingress.host=Shop_Localhost 2>&1 | head -3
```

```text
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/image/tag': 'not' failed

Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/replicas': maximum: got 9, want 6

Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/ingress/host': 'Shop_Localhost' does not match pattern '^[a-z0-9.-]+$'
```

<p align="center" id="fig-17">
  <img src="images/17-lab08-schema-reject.png" alt="รูปที่ 17 LAB 8 ด่านตรวจปฏิเสธ" width="900"><br>
  <em><b>รูปที่ 17</b> ด่านตรวจปฏิเสธใบสั่ง: --set web.replicas=9 → maximum: got 9, want 6</em>
</p>

`values.schema.json` ตรวจ **ก่อน render** ข้อความบอกตำแหน่งของค่า (`/web/replicas`) และกติกาที่ผิด (`maximum`, `not`, `pattern`) — tag `1.4` คือรุ่นพังของบทที่ 7, 9 บูธเกินเพดาน 6 ของร้าน, host ตัวใหญ่/ขีดล่างใช้เป็นชื่อโดเมนไม่ได้

chart ภายนอกก็มีด่านตรวจ ลองใส่ key ผิดให้ Traefik chart (ใช้แคตตาล็อกจาก LAB 1)

```bash
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml --set logs.access.enabled=true 2>&1 | head -3
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml --set accesslog.enabled=true 2>&1 | head -3
```

```text
Error: values don't meet the specifications of the schema(s) in the following chart(s):
traefik:
- at '': additional properties 'logs' not allowed
Error: values don't meet the specifications of the schema(s) in the following chart(s):
traefik:
- at '': additional properties 'accesslog' not allowed
```

key ที่ถูกของ chart 41.6.1 คือ `accessLog.enabled` (ตัว L ใหญ่ — ดูใน `labs/lab10-addons/traefik-values.yaml`) ถ้าไม่มี schema ค่าที่สะกดผิดจะถูกเพิกเฉยเงียบ ๆ

### ขั้นที่ 3: required — lint เตือน template หยุด

```bash
helm lint charts/som-shop
helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x
helm template som charts/som-shop 2>&1 | head -1
```

```text
level=WARN msg="missing required values" message="ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>"
level=WARN msg="missing required values" message="ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>"
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
Error: execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>
```

ไม่ใส่รหัส: `helm lint` แค่ **WARN** (lint ไม่รู้ว่าในคลัสเตอร์มี Secret เดิมหรือไม่) แต่ `helm template` **หยุด** ที่ `required` (บรรทัด 29 ของ `web.yaml` คือ checksum/secret ที่ render `secret.yaml` → เรียกตรายาง `dbPassword`)

### ขั้นที่ 4: lookup มองไม่เห็นคลัสเตอร์ตอน template

```bash
for i in 1 2; do helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | awk '{print $2}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-45; done
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | awk '{print $2}' | base64 -d | openssl x509 -noout -subject -ext subjectAltName
```

```text
sha256 Fingerprint=95:82:4B:CC:A2:6E:6E:D1:E8
sha256 Fingerprint=46:94:7E:2E:C2:BA:33:71:83
subject=CN = shop.localhost
X509v3 Subject Alternative Name:
    DNS:shop.localhost
```

render 2 ครั้งได้ใบรับรอง **คนละใบ** เพราะ `helm template` ไม่ต่อคลัสเตอร์ `lookup` จึงไม่เจอ `som-tls` เดิม และ `genSelfSignedCert` สุ่มใบใหม่ทุกครั้ง ตอน install/upgrade จริง `lookup` เห็นใบเดิมจึงใช้ใบเดิมต่อ (LAB 12 พิสูจน์ด้วย fingerprint ก่อน/หลัง) — ทฤษฎีหัวข้อ 5.7

### สิ่งที่เห็น

- chart เดียว + ใบสั่ง 2 ใบ = dev 10 object / prod 13 object
- schema ปฏิเสธ tag 1.4, replicas 9, host ผิดรูป ตั้งแต่ก่อน render (ทั้งชุดเราและชุด Traefik)
- `required`: lint = WARN, template = error; `lookup` ว่างตอน template

**คำถามชวนคิด**

1. ถ้าอยากห้ามไม่ให้ใบสั่ง prod ปิด HPA (`hpa.enabled: false`) จะใช้ schema ได้ไหม หรือควรตรวจที่อื่น
2. ทำไม chart นี้จึงไม่ใช้ `randAlphaNum` สร้างรหัสฐานข้อมูลให้อัตโนมัติ

**เก็บกวาด:** ไม่มี (ไม่ได้ติดตั้งอะไร)

---

## LAB 9: เติมสินค้าหลังเปิดร้านและผู้ตรวจรับ (hook + test)

<p align="center" id="fig-18">
  <img src="images/18-lab09-open.png" alt="รูปที่ 18 LAB 9 hook และ test" width="900"><br>
  <em><b>รูปที่ 18</b> LAB 9: install สาขา dev → hook post-install (seed) เติมสินค้า → helm test --logs → ถอด release Secret</em>
</p>

**เป้าหมาย:** ติดตั้งร้านน้องส้มทั้งร้านเป็นสาขา dev ด้วยคำสั่งเดียว ดู hook seed ทำงาน สั่งผู้ตรวจรับร้าน และถอดดูว่า release Secret เก็บอะไรไว้

**ไฟล์:** `charts/som-shop`, `charts/values-dev.yaml` (namespace `som-dev` ใหม่ ไม่แตะร้านจริง `som-shop`)

### ขั้นที่ 1: hook ในแม่พิมพ์

```bash
cd /workspace/014_kubernetes_helm/02_LAB
grep -A3 "annotations:" charts/som-shop/templates/seed-job.yaml
```

```text
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

Job `som-seed` (คำสั่ง `node scripts/seed.mjs` ใน image หน้าร้าน) รัน **หลัง install และหลังทุก upgrade** สำเร็จแล้วถูกลบ (`hook-succeeded`) แทน initContainer `db-seed` ของบท 009–013 ที่รันในทุกบูธ

### ขั้นที่ 2: เปิดสาขา dev ทั้งร้านด้วยคำสั่งเดียว

```bash
time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait
```

```text
NAME: som
LAST DEPLOYED: Tue Oct  6 05:53:27 2026
NAMESPACE: som-dev
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (dev) (release som, revision 1) ใน namespace som-dev แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: 1 (ไม่มี HPA)
   เปิดร้าน: curl http://dev.shop.localhost:30080/api/whoami
   ตรวจรับร้าน: helm test som -n som-dev --logs

real	0m17.892s
```

**17.9 วินาที** ได้ร้านครบ: db + ซอง + ป้าย + หน้าร้าน + ประตู + เติมสินค้า การ์ดต้อนรับ (NOTES) เป็นภาษาไทยจาก `templates/NOTES.txt` ที่ render ชื่อร้าน revision image และคำสั่งเปิดร้านให้ (`meow1234` เป็นรหัสตัวอย่างของ LAB)

```bash
kubectl get ns som-dev --show-labels
kubectl -n som-dev get all,pvc,cm,secret,ing
kubectl -n som-dev get job
```

```text
NAME      STATUS   AGE   LABELS
som-dev   Active   18s   kubernetes.io/metadata.name=som-dev,name=som-dev
NAME                           READY   STATUS    RESTARTS   AGE
pod/som-db-0                   1/1     Running   0          18s
pod/som-web-64c9f5cd95-t5pj7   1/1     Running   0          18s

NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/som-db    ClusterIP   None            <none>        5432/TCP   18s
service/som-web   ClusterIP   10.96.216.214   <none>        80/TCP     18s

NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-web   1/1     1            1           18s

NAME                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/som-web-64c9f5cd95   1         1         1       18s

NAME                      READY   AGE
statefulset.apps/som-db   1/1     18s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-8347bc95-a507-4042-9bcb-af75570ea79c   1Gi        RWO            standard       <unset>                 18s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      18s
configmap/som-announcement   1      18s
configmap/som-web-config     5      18s

NAME                               TYPE                 DATA   AGE
secret/sh.helm.release.v1.som.v1   helm.sh/release.v1   1      18s
secret/som-db-secret               Opaque               2      18s

NAME                                CLASS     HOSTS                ADDRESS     PORTS   AGE
ingress.networking.k8s.io/som-web   traefik   dev.shop.localhost   localhost   80      18s
No resources found in som-dev namespace.
```

- Job `som-seed` **ไม่อยู่แล้ว** (`No resources found`) เพราะสำเร็จแล้วถูกลบตาม `hook-succeeded`
- namespace จาก `--create-namespace` ไม่มี label Pod Security (ดูขั้นที่ 4)
- สมุดหน้าแรกคือ `sh.helm.release.v1.som.v1`

```bash
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
curl -s http://dev.shop.localhost:30080/ | grep -o "ร้านอาหารแมวน้องส้ม (dev)" | head -1
curl -s http://dev.shop.localhost:30080/ | grep -o "🧪 สาขาทดลอง[^<]*" | head -1
```

```text
som-web-64c9f5cd95-t5pj7 1.7
som-web-64c9f5cd95-t5pj7 1.7 orders=0 products=6
ร้านอาหารแมวน้องส้ม (dev)
🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost
```

สาขาใหม่ ออเดอร์ 0 สินค้า 6 รายการ (มาจาก hook seed) ชื่อร้านและแถบโปรโมชันมาจากใบสั่ง dev — 🌐 เปิด `http://dev.shop.localhost:30080` ใน browser ได้

### ขั้นที่ 3: ผู้ตรวจรับร้าน

```bash
helm test som -n som-dev --logs | sed -n '/TEST SUITE/,$p'
kubectl -n som-dev get pod
```

```text
TEST SUITE:     som-test-health
Last Started:   Tue Oct  6 05:53:45 2026
Last Completed: Tue Oct  6 05:53:53 2026
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-64c9f5cd95-t5pj7 1.7
products: ok

NAME                       READY   STATUS    RESTARTS   AGE
som-db-0                   1/1     Running   0          26s
som-web-64c9f5cd95-t5pj7   1/1     Running   0          26s
```

Pod `som-test-health` (curl) เรียก `/api/health` (ร้านต่อ db ได้), `/api/whoami` และ `/api/products` ผ่าน Service ภายใน ผ่านทั้ง 3 = `Phase: Succeeded` และ Pod ทดสอบถูกลบทันที (delete policy `hook-succeeded`) แต่ `--logs` ยังแสดงผลตรวจให้

### ขั้นที่ 4: Pod Security ของ namespace ใหม่

```bash
kubectl label --dry-run=server --overwrite ns som-dev pod-security.kubernetes.io/enforce=restricted
```

```text
namespace/som-dev labeled (server dry run)
```

ลอง (แบบ dry run) ว่าถ้าบังคับระดับ `restricted` Pod ที่มีอยู่จะผิดกติกาไหม ผลไม่มี warning = Pod ของชุดร้าน (และ Job/test) ผ่าน `restricted` (แม่พิมพ์ตั้ง `runAsNonRoot`, `seccompProfile`, `drop: ["ALL"]` ไว้ทุก container) ถ้าต้องการให้ namespace ใหม่เตือนเหมือน `som-shop` ให้ label เอง เช่น `kubectl label ns som-dev pod-security.kubernetes.io/warn=restricted` (ไม่บังคับใน LAB นี้)

### ขั้นที่ 5: ซองในสมุด — ถอด release Secret

```bash
kubectl -n som-dev get secret -l owner=helm
kubectl -n som-dev get secret sh.helm.release.v1.som.v1 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d \
  | python3 -c 'import json,sys,re; r=json.load(sys.stdin); print(json.dumps(r["config"],ensure_ascii=False)); print(re.findall(r"DATABASE_URL: .*", r["manifest"])); print([h["name"]+":"+",".join(h["events"]) for h in r["hooks"]])'
helm get values som -n som-dev
```

```text
NAME                        TYPE                 DATA   AGE
sh.helm.release.v1.som.v1   helm.sh/release.v1   1      26s
{"db": {"password": "meow1234"}, "hpa": {"enabled": false}, "ingress": {"enabled": true, "host": "dev.shop.localhost", "tls": false}, …}
['DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"']
['som-test-health:test', 'som-seed:post-install,post-upgrade']
USER-SUPPLIED VALUES:
db:
  password: meow1234
hpa:
  enabled: false
...
```

(ผลตัดให้สั้น)

<p align="center" id="fig-19">
  <img src="images/19-lab09-release-secret.png" alt="รูปที่ 19 LAB 9 ถอด release Secret" width="900"><br>
  <em><b>รูปที่ 19</b> ถอดสมุดใน Secret ด้วย base64 -d | base64 -d | gzip -d เห็นรหัสฐานข้อมูลในใบสั่ง → ใครอ่าน Secret ได้ = อ่านรหัสได้</em>
</p>

รหัสฐานข้อมูลอยู่ใน release Secret **สองที่**: ใบสั่ง (`config.db.password`) และพิมพ์เขียว (`DATABASE_URL` ใน manifest ของ Secret ร้าน) และ `helm get values` ก็แสดงตรง ๆ — ใครมีสิทธิ์ `get secrets` ใน `som-dev` หรือรัน `helm` กับ namespace นี้ได้ = อ่านรหัสได้ (ทฤษฎีหัวข้อ 10) ข้อมูล hook ก็อยู่ในซองด้วย (`som-seed:post-install,post-upgrade`, `som-test-health:test`)

### ขั้นที่ 6: upgrade โดยไม่ส่งรหัส + เปลี่ยนประกาศ

```bash
kubectl -n som-dev get pod -l app=som-web -o name
time helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set announcement="ปลาแซลมอนมาแล้ว 🍣" --wait | grep -E "REVISION|STATUS"
kubectl -n som-dev get pod -l app=som-web -o name
kubectl -n som-dev get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
curl -s http://dev.shop.localhost:30080/api/announcement; echo
helm history som -n som-dev
```

```text
pod/som-web-64c9f5cd95-t5pj7
STATUS: deployed
REVISION: 2

real	0m9.685s
pod/som-web-574cd55f96-g94jv
pod/som-web-64c9f5cd95-t5pj7
meow1234
som-web-574cd55f96-g94jv 1.7 ปลาแซลมอนมาแล้ว 🍣
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 05:53:27 2026	superseded	som-shop-0.1.0	1.7        	Install complete
2       	Tue Oct  6 05:53:53 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

- ไม่ได้ส่ง `--set db.password` แต่ Secret ยังเป็นรหัสเดิม (`meow1234` ค่าตัวอย่าง) เพราะตรายาง `dbPassword` ใช้ **`lookup`** อ่านจาก Secret เดิม
- เปลี่ยนแค่ประกาศ → `checksum/config` เปลี่ยน → ได้ Pod ใหม่ `som-web-574cd55f96-…` เอง (ไม่ต้อง `rollout restart` แบบบทที่ 10) Pod เก่ากำลังปิด (ยังเห็นคู่กันชั่วครู่)

### ขั้นที่ 7: ดู hook เกิดแล้วหายระหว่าง upgrade (2 หน้าต่าง)

**หน้าต่างที่ 2** ดู Pod แบบ watch (`kubectl get -w` ดูได้ทีละชนิด ถ้าสั่ง `get job,pod -w` จะได้ `error: you may only specify a single resource type`)

```bash
timeout 25 kubectl -n som-dev get pod -w
```

**หน้าต่างที่ 1** (ภายใน 25 วินาที)

```bash
cd /workspace/014_kubernetes_helm/02_LAB
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set announcement="วันนี้ปลาทูสดมาก 🐟" --wait | grep -E "REVISION|STATUS"
kubectl -n som-dev get job
kubectl -n som-dev get events --field-selector involvedObject.kind=Job | tail -3
```

หน้าต่างที่ 2 (ตัดบรรทัดซ้ำ)

```text
NAME                       READY   STATUS    RESTARTS   AGE
som-db-0                   1/1     Running   0          43s
som-web-574cd55f96-g94jv   1/1     Running   0          16s
som-web-65b7dd9845-j9rm7   0/1     Pending   0          0s
som-web-65b7dd9845-j9rm7   0/1     Init:0/1   0          0s
som-web-65b7dd9845-j9rm7   0/1     PodInitializing   0          2s
som-web-65b7dd9845-j9rm7   0/1     Running           0          2s
som-web-65b7dd9845-j9rm7   1/1     Running           0          3s
som-web-574cd55f96-g94jv   1/1     Terminating       0          22s
som-seed-qk2k5             0/1     Pending           0          0s
som-seed-qk2k5             0/1     Init:0/1          0          0s
som-seed-qk2k5             0/1     PodInitializing   0          1s
som-seed-qk2k5             1/1     Running           0          1s
som-seed-qk2k5             0/1     Completed         0          2s
som-web-574cd55f96-g94jv   0/1     Error             0          27s
```

หน้าต่างที่ 1

```text
STATUS: deployed
REVISION: 3
No resources found in som-dev namespace.
32s         Normal   Completed          job/som-seed   Job completed
19s         Normal   SuccessfulCreate   job/som-seed   Created pod: som-seed-qk2k5
15s         Normal   Completed          job/som-seed   Job completed
```

ลำดับที่เห็นตรงกับทฤษฎีหัวข้อ 11: **Pod หน้าร้านใหม่พร้อม (1/1) ก่อน** (เพราะ `--wait`) → Pod เก่าเริ่มปิด → **จึงเกิด Job seed** (`post-upgrade`) → `Completed` → Job ถูกลบ (`No resources found`) Events ของ Job เห็น `Job completed` 2 ครั้งในช่วงไม่ถึงนาที (จาก upgrade rev 2 และ rev 3) — seed รันใหม่ทุก upgrade

> Pod เก่าของหน้าร้านแสดง `Error` ชั่วครู่ตอนถูกปิด เป็นแค่ exit code ของ process หลังได้สัญญาณหยุด (SIGTERM) ระหว่าง rolling update ไม่ใช่ปัญหา (Pod ใหม่รับลูกค้าแล้ว)

### สิ่งที่เห็น

- `helm install ... --wait` ครั้งเดียวได้ร้านทั้งร้าน 17.9 วินาที + NOTES ภาษาไทย + hook seed (`orders=0 products=6`)
- `helm test` ผ่าน 3 บรรทัด, release Secret มีรหัสทั้งใน config และ manifest
- upgrade ไม่ส่งรหัส = `lookup` รหัสเดิม, เปลี่ยนประกาศ = Pod ใหม่เอง, hook รันหลังหน้าร้านพร้อม

**คำถามชวนคิด**

1. ถ้าสินค้าตั้งต้นต้องมีก่อนหน้าร้านรับลูกค้าคนแรก hook แบบ `post-install` เพียงพอไหม ควรใช้ hook ชนิดไหนแทน และมีข้อจำกัดอะไร (คิดถึง db ที่ต้องพร้อมก่อน)
2. ทำไม seed ต้อง "ทำซ้ำได้" (idempotent) เมื่อเปลี่ยนจาก initContainer มาเป็น hook `post-upgrade`

**เก็บกวาด LAB 9:** LAB 12 จะเปิดสาขา dev ใหม่ทั้งร้าน ให้ลบสาขานี้

```bash
helm uninstall som -n som-dev
kubectl -n som-dev get pvc
kubectl delete ns som-dev
helm list -A
```

```text
release "som" uninstalled
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
data-som-db-0   Bound    pvc-8347bc95-a507-4042-9bcb-af75570ea79c   1Gi        RWO            standard       <unset>                 81s
namespace "som-dev" deleted
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
```

หลัง `helm uninstall` ตู้เซฟ `data-som-db-0` **ยังอยู่** (PVC จาก `volumeClaimTemplates` ไม่ใช่ส่วนของ release — LAB 12 ใช้เรื่องนี้) การลบ namespace ลบ PVC ไปด้วย ตอนนี้ `helm list -A` ว่างอีกครั้ง

---

## LAB 10: Traefik และ metrics-server จากแคตตาล็อก

<p align="center" id="fig-20">
  <img src="images/20-lab10-open.png" alt="รูปที่ 20 LAB 10 add-on จาก chart" width="900"><br>
  <em><b>รูปที่ 20</b> LAB 10: แทน static manifest ด้วย chart traefik 41.6.1 (v3.7.13) และ metrics-server 3.14.0 (0.9.0)</em>
</p>

**เป้าหมาย:** เปลี่ยนพนักงานต้อนรับ (Traefik) และเจ้าหน้าที่จดมิเตอร์ (metrics-server) ที่ติดตั้งด้วย static manifest ในบท 012–013 ให้มาจาก chart ทางการ เทียบผล render กับของเดิม เห็นว่าทำไม "รับของเดิม" ไม่ได้ แล้วย้ายจริงระหว่างที่ลูกค้าเข้าร้าน

**ไฟล์:** `labs/lab10-addons/traefik-values.yaml`, `labs/lab10-addons/metrics-server-values.yaml`, `labs/lab10-addons/static-old/` (สำเนาไฟล์ static ของบท 012/013)

ใบสั่งของ Traefik ตั้งให้ได้ผลเหมือนประตูเดิม (ไฟล์จริง ตัดคอมเมนต์บางส่วน)

```yaml
service:
  spec:
    type: NodePort            # kind map ออกมาแค่ 30080-30082 (ไม่มี LoadBalancer)
ports:
  web:
    nodePort: 30080
  websecure:
    nodePort: 30081
  traefik:
    expose:
      default: true           # เปิด dashboard ออก Service (เฉพาะ LAB)
    nodePort: 30082
providers:
  kubernetesIngress:
    strictPrefixMatching: true
    allowEmptyServices: true
    publishedService:
      enabled: false
    ingressEndpoint:
      hostname: localhost     # คอลัมน์ ADDRESS = localhost เหมือนบท 012
ingressClass:
  enabled: true
  isDefaultClass: true
api:
  dashboard: true
  insecure: true              # dashboard ไม่มีรหัส — เฉพาะ LAB
accessLog:
  enabled: true
global:
  checkNewVersion: false
  sendAnonymousUsage: false
```

ส่วน `metrics-server-values.yaml` มีแค่ `args: [--kubelet-insecure-tls]` (เฉพาะ LAB เหมือนบท 013)

### ขั้นที่ 1: render chart เทียบกับ static

```bash
cd /workspace/014_kubernetes_helm/02_LAB
ls labs/lab10-addons labs/lab10-addons/static-old
helm list -A
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml > /root/traefik-rendered.yaml
grep "^kind:" /root/traefik-rendered.yaml | sort | uniq -c
grep -nE -- "--(entryPoints.websecure.http.tls|providers.kubernetesingress.strictPrefixMatching|providers.kubernetesingress.ingressendpoint.hostname|api.insecure|accesslog)" /root/traefik-rendered.yaml
grep -nE "nodePort:|image:" /root/traefik-rendered.yaml
grep -A3 "matchLabels" /root/traefik-rendered.yaml | head -4
grep -A2 "matchLabels" labs/lab10-addons/static-old/00-traefik.yaml | head -3
```

```text
labs/lab10-addons:
metrics-server-values.yaml
static-old
traefik-values.yaml

labs/lab10-addons/static-old:
00-metrics-server.yaml
00-traefik.yaml
traefik-crds-v3.7.13.yml
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
      1 kind: ClusterRole
      1 kind: ClusterRoleBinding
      1 kind: Deployment
      1 kind: IngressClass
      1 kind: Service
      1 kind: ServiceAccount
200:        - --api.insecure=true
208:        - --providers.kubernetesingress.ingressendpoint.hostname=localhost
209:        - --providers.kubernetesingress.strictPrefixMatching=true
210:        - --entryPoints.websecure.http.tls=true
212:        - --accesslog=true
213:        - --accesslog.fields.defaultmode=keep
214:        - --accesslog.fields.headers.defaultmode=drop
142:    nodePort: 30082
147:    nodePort: 30080
152:    nodePort: 30081
226:        image: docker.io/traefik:v3.7.13
    matchLabels:
      app.kubernetes.io/name: traefik
      app.kubernetes.io/instance: traefik-traefik
  strategy:
    matchLabels: {app: traefik}
  template:
    metadata:
      labels:
        app: traefik
```

ผล render ได้ flag สำคัญของบท 012 ครบ (HTTPS ที่ websecure, `strictPrefixMatching`, ADDRESS `localhost`, dashboard, access log), NodePort 30080/30081/30082 และ image `traefik:v3.7.13` เดิม **แต่ selector ต่างกัน**: chart ใช้ `app.kubernetes.io/name: traefik` + `app.kubernetes.io/instance: traefik-traefik` ส่วน static ใช้ `app: traefik` ซึ่งเป็นตัวกำหนดว่ารับของเดิมได้หรือไม่ (ขั้นที่ 2) สังเกตด้วยว่า chart ไม่สร้าง Namespace (มาจาก `--create-namespace`) และไม่มี CRD ใน render (CRD อยู่ใน `crds/` ติดตั้งแยก)

### ขั้นที่ 2: ลองผิด — ติดตั้งทับของเดิม

```bash
helm install traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml 2>&1 | cut -c1-420
helm list -A
```

```text
Error: INSTALLATION FAILED: unable to continue with install: ServiceAccount "traefik" in namespace "traefik" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annotation validation error: missing key "meta.helm.sh/release-name": must be set to "traefik"; annotation validation error: missing key
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
```

<p align="center" id="fig-21">
  <img src="images/21-lab10-adopt-fail.png" alt="รูปที่ 21 LAB 10 ติดตั้งทับของเดิม" width="900"><br>
  <em><b>รูปที่ 21</b> ติดตั้งทับของเดิม: invalid ownership metadata → --take-ownership เจอ conflict → --force-conflicts ติด selector field is immutable ⇒ ลบของเดิมก่อน (เก็บ CRD)</em>
</p>

Helm ไม่ยอมแตะ ServiceAccount ที่ไม่มีป้าย `managed-by: Helm` และ annotation `meta.helm.sh/release-name` (**invalid ownership metadata**) ข้อดีคือหยุดก่อนสร้างอะไร **ไม่มี release ค้าง** (`helm list -A` ว่าง) ประตูเดิมยังทำงานปกติ

**ผลจริงจากการทดลองแยก (ไม่ต้องทำตาม)** — ทดลองบนสำเนาของ Traefik static ใน namespace ทดลอง `traefik-test` (ไม่มี NodePort/IngressClass) เพื่อดูว่าถ้าฝืน "รับของเดิม" จะเกิดอะไร

1. `helm install ... --take-ownership` → SSA **conflict** กับ `kubectl-client-side-apply` และเกิด release `failed` rev 1

   ```text
   Error: INSTALLATION FAILED: conflict occurred while applying object traefik-test/traefik /v1, Kind=Service: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using v1: .spec.selector && conflict occurred while applying object traefik-test/traefik apps/v1, Kind=Deployment: Apply failed with 11 conflicts: conflicts with "kubectl-client-side-apply" using apps/v1:
   - .spec.selector
   - .spec.strategy.rollingUpdate.maxSurge
   ...
   - .spec.template.spec.containers[name="traefik"].readinessProbe.httpGet.port
   ```

2. `helm upgrade --install ... --take-ownership --force-conflicts` → ยึด conflict ได้ แต่ติด **selector แก้ไม่ได้** rev 2 `failed`

   ```text
   Error: UPGRADE FAILED: server-side apply failed for object traefik-test/traefik apps/v1, Kind=Deployment: Deployment.apps "traefik" is invalid: spec.selector: Invalid value: {"matchLabels":{"app.kubernetes.io/instance":"traefik-traefik-test","app.kubernetes.io/name":"traefik"}}: field is immutable
   ```

3. ระหว่างนั้น ServiceAccount และ Service **ถูกติดป้าย Helm ไปแล้ว** (Deployment ยังไม่ถูกยึด) แล้วถ้า `helm uninstall` release ที่ล้มนี้

   ```text
   level=WARN msg="skipping delete of resource not owned by this release" kind=Deployment name=traefik namespace=traefik-test release=traefik
   1 resource(s) were not deleted because they are not owned by this release:
   [Deployment] traefik

   release "traefik" uninstalled
   ```

   ServiceAccount และ Service **ถูกลบทิ้ง** เหลือแต่ Deployment ถ้าเป็น Traefik ตัวจริงใน namespace `traefik` ประตูของทุกร้านปิดทันที

> ⚠️ **ห้าม `helm uninstall` release ที่ adopt ล้ม** และอย่าทำข้อ 1–3 กับ Traefik ตัวจริง (ทฤษฎีหัวข้อ 9.3) ทางที่ถูกสำหรับ add-on ที่ selector ต่างกันคือ **ลบของเดิม (เก็บ CRD) แล้วติดตั้ง chart** ซึ่งประตูจะปิดชั่วครู่ (ขั้นที่ 3)

### ขั้นที่ 3: ย้าย Traefik จริงระหว่างลูกค้าเข้าร้าน (2 หน้าต่าง)

ก่อนเริ่ม ตรวจว่ามี CRD ของ Traefik (Middleware ของร้านอยู่บน CRD เหล่านี้ **ห้ามลบไฟล์ `traefik-crds-v3.7.13.yml`**)

```bash
kubectl get crd | grep -c traefik.io
```

```text
25
```

**หน้าต่างที่ 2** ยิงลูกค้าจำลองผ่านประตู HTTPS 600 ครั้ง (ราว 78 วินาที)

```bash
cd /workspace/014_kubernetes_helm/02_LAB
./hit.sh -q https://shop.localhost:30081/api/whoami 600 0.1
```

**หน้าต่างที่ 1** (เริ่มภายในไม่กี่วินาทีหลังหน้าต่างที่ 2)

```bash
t0=$(date +%s)
kubectl delete -f labs/lab10-addons/static-old/00-traefik.yaml --wait=true
helm install traefik traefik/traefik --version 41.6.1 -n traefik --create-namespace -f labs/lab10-addons/traefik-values.yaml --wait --timeout 5m
echo "ย้าย Traefik: $(( $(date +%s)-t0 )) วินาที"
```

หน้าต่างที่ 1

```text
namespace "traefik" deleted
serviceaccount "traefik" deleted from traefik namespace
clusterrole.rbac.authorization.k8s.io "traefik" deleted
clusterrolebinding.rbac.authorization.k8s.io "traefik" deleted
deployment.apps "traefik" deleted from traefik namespace
service "traefik" deleted from traefik namespace
ingressclass.networking.k8s.io "traefik" deleted
NAME: traefik
LAST DEPLOYED: Tue Oct  6 05:58:43 2026
NAMESPACE: traefik
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
traefik with docker.io/traefik:v3.7.13 has been deployed successfully on traefik namespace!
ย้าย Traefik: 19 วินาที
```

หน้าต่างที่ 2

```text
............................xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx......................................
จำนวน  Pod  เวอร์ชัน
    528 1.7 (เวอร์ชัน)
ข้อความ error:
     61 curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to shop.localhost:30081
     11 curl: (35) Recv failure: Connection reset by peer
ช่วงที่มี err: 18.8 วินาที
ok=528 err=72 (ใช้เวลา 77.9 วินาที)
```

<p align="center" id="fig-22">
  <img src="images/22-lab10-migrate-downtime.png" alt="รูปที่ 22 LAB 10 ย้ายจริง ประตูปิดชั่วคราว" width="900"><br>
  <em><b>รูปที่ 22</b> ย้ายจริง: ระหว่างลบของเดิมและติดตั้ง chart ประตูปิดชั่วคราว (~19 วินาที) แล้วกลับมาเป็น 404 page not found ตามเดิม</em>
</p>

ย้ายทั้งหมด **19 วินาที** ลูกค้าเจอ error 72 จาก 600 ครั้งต่อเนื่อง **18.8 วินาที** (ประตูไม่มีคนเฝ้าระหว่างลบตัวเก่าถึงตัวใหม่พร้อม) ระบบจริงต้องประกาศช่วงปิดปรับปรุง หรือทำแบบ blue/green (ติดตั้งตัวใหม่คู่ขนานบนพอร์ต/IP อื่นแล้วสลับ) — นี่คือเหตุผลที่ควรเลือกวิธีติดตั้ง add-on ให้ดีตั้งแต่แรก

ตรวจประตูใหม่

```bash
kubectl get crd | grep -c traefik.io
kubectl -n traefik get deploy,svc,pod
kubectl get ingressclass
kubectl get ns traefik --show-labels
curl -s localhost:30080; echo
curl -s -o /dev/null -w "dashboard %{http_code}\n" localhost:30082/dashboard/
curl -si http://shop.localhost:30080/ | grep -iE "^HTTP|^location"
curl -sk https://shop.localhost:30081/api/stats; echo
curl -sk -o /dev/null -w "admin no-auth %{http_code}\n" https://admin.localhost:30081/
curl -sk -u som:meow-admin-123 https://admin.localhost:30081/stats; echo
```

```text
25
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/traefik   1/1     1            1           69s

NAME              TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                                     AGE
service/traefik   NodePort   10.96.201.218   <none>        8080:30082/TCP,80:30080/TCP,443:30081/TCP   69s

NAME                          READY   STATUS    RESTARTS   AGE
pod/traefik-8b84c796d-s5ngq   1/1     Running   0          69s
NAME                CONTROLLER                      PARAMETERS   AGE
traefik (default)   traefik.io/ingress-controller   <none>       70s
NAME      STATUS   AGE   LABELS
traefik   Active   70s   kubernetes.io/metadata.name=traefik,name=traefik
404 page not found
dashboard 200
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/
som-web-774d99d8df-g67ln 1.7 orders=3 products=6
admin no-auth 401
som-web-774d99d8df-g67ln 1.7 orders=3 products=6
```

ทุกอย่างกลับมาเหมือนบท 012–013: CRD 25 ตัวยังอยู่, NodePort 3 พอร์ต, IngressClass `traefik (default)` (ดาวทอง), `404 page not found` ที่ประตูเปล่า, dashboard 200, redirect 301 ไป 30081, ร้านตอบ (ออเดอร์เดิม 3), หลังร้านยังถามบัตร (401) และเข้าได้ด้วยบัตรตัวอย่าง

### ขั้นที่ 4: ย้าย metrics-server

```bash
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f labs/lab10-addons/metrics-server-values.yaml 2>&1 | cut -c1-300
t0=$(date +%s)
kubectl delete -f labs/lab10-addons/static-old/00-metrics-server.yaml --wait=true | tail -3
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f labs/lab10-addons/metrics-server-values.yaml --wait --timeout 5m | grep -E "STATUS|REVISION"
echo "ย้าย metrics-server: $(( $(date +%s)-t0 )) วินาที"
kubectl get apiservice v1beta1.metrics.k8s.io
```

```text
Error: INSTALLATION FAILED: unable to continue with install: ServiceAccount "metrics-server" in namespace "kube-system" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annot
service "metrics-server" deleted from kube-system namespace
deployment.apps "metrics-server" deleted from kube-system namespace
apiservice.apiregistration.k8s.io "v1beta1.metrics.k8s.io" deleted
STATUS: deployed
REVISION: 1
ย้าย metrics-server: 21 วินาที
NAME                     SERVICE                      AVAILABLE                      AGE
v1beta1.metrics.k8s.io   kube-system/metrics-server   False (FailedDiscoveryCheck)   21s
```

ติดตั้งทับได้ error เดียวกับ Traefik (ไม่มี release ค้าง) ย้ายจริงใช้ **21 วินาที** แต่ **APIService ยังเป็น `False (FailedDiscoveryCheck)` ทันทีหลัง `--wait`** — Pod พร้อมแล้ว แต่ kube-apiserver ยังต้องตรวจเส้นทางไปหา metrics-server และ metrics-server ต้องจดมิเตอร์รอบแรกก่อน รอสัก 20–45 วินาที

```bash
sleep 20; kubectl top nodes
kubectl -n som-shop get hpa
kubectl get apiservice v1beta1.metrics.k8s.io
helm list -A
```

```text
NAME                CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
lab-control-plane   140m         0%       1234Mi          1%
lab-worker          47m          0%       522Mi           0%
lab-worker2         42m          0%       643Mi           1%
NAME      REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 3%/50%   2         6         2          17m
NAME                     SERVICE                      AVAILABLE   AGE
v1beta1.metrics.k8s.io   kube-system/metrics-server   True        47s
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
```

`kubectl top` ใช้ได้ HPA ของร้านอ่าน CPU ได้ต่อ (`cpu: 3%/50%`) APIService `True` ใน ~47 วินาที และ `helm list -A` เห็นอุปกรณ์ท่าเรือ 2 ชิ้นเป็น release — ต่อไปอัปเกรด Traefik/metrics-server ด้วย `helm upgrade ... --version <ใหม่>` และย้อนด้วย `helm rollback` ได้เหมือนแอปทั่วไป (ส่วน CRD ต้องดูแลตามทฤษฎีหัวข้อ 4.3)

### สิ่งที่เห็น

- ผล render ของ chart ทางการ ≈ static ของบท 012/013 แต่ selector ต่าง จึงรับของเดิมไม่ได้
- ติดตั้งทับ = `invalid ownership metadata` (ปลอดภัย) / ฝืนด้วย take-ownership + force-conflicts = `field is immutable` และ uninstall แล้วลบของจริง
- ย้ายจริง: Traefik 19 วินาที (err 18.8 วินาที), metrics-server 21 วินาที (+ รอ APIService)

**คำถามชวนคิด**

1. ทำไมต้องเก็บ CRD ของ Traefik ไว้ตอนลบ static และถ้าเผลอลบไปจะเกิดอะไรกับ Middleware `redirect-https`, `admin-auth` ของร้าน
2. ถ้าเป็นระบบจริงที่ห้ามประตูปิดแม้ 19 วินาที จะวางแผนย้ายอย่างไร (คิดถึงการติดตั้งตัวใหม่คู่ขนานด้วยชื่อ release/พอร์ตอื่น)
3. ทำไม metrics-server ขึ้น `deployed` แล้วแต่ `kubectl top` ยังใช้ไม่ได้ทันที `--wait` รอถึงไหน

**เก็บกวาด:** ไม่มี — Traefik และ metrics-server ที่มาจาก chart **ใช้ต่อ** (LAB 12 และบทถัดไป) ลบไฟล์ชั่วคราว `rm -f /root/traefik-rendered.yaml` ได้

---

## LAB 11: โกดังเก็บชุดแฟรนไชส์ (OCI registry)

<p align="center" id="fig-23">
  <img src="images/23-lab11-open.png" alt="รูปที่ 23 LAB 11 โกดัง OCI" width="900"><br>
  <em><b>รูปที่ 23</b> LAB 11: registry:2 ใน k8s-lab → helm package → helm push → helm install oci://</em>
</p>

**เป้าหมาย:** ตั้งโกดัง OCI registry ขนาดเล็ก (มีรหัส) ใน k8s-lab แพ็กชุดร้านเป็น `.tgz` push เข้าโกดัง แล้วติดตั้งสาขาจาก `oci://` แทนโฟลเดอร์

**ไฟล์:** ทำงานใน `labs/lab11-registry/` (โฟลเดอร์ `auth/` และ `pulled/` สร้างระหว่าง LAB ไม่เข้า git) บัญชีโกดัง `som` / `meow-registry-123` **เป็นค่าตัวอย่าง**

### ขั้นที่ 1: ตั้งโกดัง

```bash
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab11-registry
mkdir -p auth
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn som meow-registry-123 > auth/htpasswd
cut -c1-8 auth/htpasswd
docker run -d --name som-registry -p 5000:5000 -v $PWD/auth:/auth -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=som -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2 | cut -c1-12
sleep 3; docker ps --filter name=som-registry --format '{{.Names}} {{.Image}} {{.Status}} {{.Ports}}'
curl -s -o /dev/null -w "%{http_code}\n" localhost:5000/v2/
```

```text
Unable to find image 'httpd:2.4-alpine' locally
...
Status: Downloaded newer image for httpd:2.4-alpine
som:$2y$
Unable to find image 'registry:2' locally
...
Status: Downloaded newer image for registry:2
42045de1f2c8
som-registry registry:2 Up 3 seconds 0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
401
```

- `htpasswd` (ยืมจาก image `httpd`) สร้างไฟล์บัญชีที่รหัสถูก hash ด้วย bcrypt (`$2y$`)
- `registry:2` รันใน docker ของ k8s-lab ที่พอร์ต 5000 (ไม่ชน 30080–30082 และไม่ต้องเปิดออกเครื่องนักศึกษา) ไม่มีบัตรได้ `401`

### ขั้นที่ 2: แพ็กชุดแฟรนไชส์

```bash
helm package ../../charts/som-shop
ls -l som-shop-0.1.0.tgz; tar tzf som-shop-0.1.0.tgz | head -20
```

```text
Successfully packaged chart and saved it to: /workspace/014_kubernetes_helm/02_LAB/labs/lab11-registry/som-shop-0.1.0.tgz
-rw-r--r-- 1 root root 5987 Oct  6 06:01 som-shop-0.1.0.tgz
som-shop/Chart.yaml
som-shop/values.yaml
som-shop/values.schema.json
som-shop/templates/NOTES.txt
som-shop/templates/_helpers.tpl
som-shop/templates/configmap.yaml
som-shop/templates/db.yaml
som-shop/templates/hpa.yaml
som-shop/templates/ingress.yaml
som-shop/templates/secret.yaml
som-shop/templates/seed-job.yaml
som-shop/templates/tests/test-health.yaml
som-shop/templates/web.yaml
som-shop/.helmignore
```

ชื่อไฟล์ = `<name>-<version>.tgz` จาก `Chart.yaml` ทั้งร้านแพ็กได้ไม่ถึง 6 KB (ไม่มีรหัสอยู่ข้างใน — รหัสส่งตอนติดตั้ง)

### ขั้นที่ 3: login (ลองผิด 2 แบบ) แล้ว push

```bash
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http 2>&1 | tail -1
echo meow-registry-123 | helm registry login http://localhost:5000 -u som --password-stdin --plain-http 2>&1 | tail -1
echo meow-registry-123 | helm registry login localhost:5000 -u som --password-stdin --plain-http
python3 -c 'import json; d=json.load(open("/root/.config/helm/registry/config.json")); print({k:{kk:(vv[:6]+"...") for kk,vv in v.items()} for k,v in d["auths"].items()})'
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http
```

```text
Error: failed to perform "Exists" on destination: HEAD "http://localhost:5000/v2/charts/som-shop/manifests/sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22": basic credential not found
Error: invalid reference: invalid registry "http://localhost:5000"
Login Succeeded
{'localhost:5000': {'auth': 'c29tOm...'}}
Pushed: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
```

<p align="center" id="fig-24">
  <img src="images/24-lab11-push-install.png" alt="รูปที่ 24 LAB 11 login push install" width="900"><br>
  <em><b>รูปที่ 24</b> ต้อง helm registry login localhost:5000 (ใส่แค่ชื่อโฮสต์) ก่อน push ได้ digest แล้วติดตั้งจาก oci:// เป็นสาขา oci-demo</em>
</p>

- push ก่อน login = `basic credential not found`
- Helm 4 ให้ login ด้วย **ชื่อโฮสต์เท่านั้น** (`localhost:5000`) ใส่ `http://` ได้ `invalid registry`
- `--password-stdin` กันรหัสไปค้างในประวัติคำสั่ง (`ps`/history) ส่วน `--plain-http` ใช้เพราะโกดัง LAB ไม่มี TLS
- credential เก็บใน `~/.config/helm/registry/config.json` เป็น base64 ของ `som:...` (`c29tOm` = `som:`) **ไม่ได้เข้ารหัส**
- push แล้วได้ **digest** (ลายนิ้วมือของเนื้อหา) ใช้อ้างอิงแบบเปลี่ยนไม่ได้

### ขั้นที่ 4: ดู ดึง และติดตั้งจากโกดัง

```bash
helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | grep -E "^(name|version|appVersion|Pulled|Digest)"
mkdir -p pulled && helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d pulled --untar 2>&1 | tail -2; ls pulled/som-shop
time helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -n oci-demo --create-namespace \
  --set fullnameOverride=som --set db.password=meow1234 --set ingress.enabled=true --set ingress.host=oci.shop.localhost --set web.replicas=1 \
  --wait 2>&1 | grep -vE "^\s*$" | head -12
curl -s http://oci.shop.localhost:30080/api/whoami; echo
helm list -n oci-demo
```

```text
Pulled: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
appVersion: "1.7"
name: som-shop
version: 0.1.0
Pulled: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
Chart.yaml
templates
values.schema.json
values.yaml
Pulled: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
NAME: oci-som
LAST DEPLOYED: Tue Oct  6 06:01:08 2026
NAMESPACE: oci-demo
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (release oci-som, revision 1) ใน namespace oci-demo แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: 1 (ไม่มี HPA)

real	0m17.003s
som-web-59495f6db6-qrvkm 1.7
NAME   	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART         	APP VERSION
oci-som	oci-demo 	1       	2026-10-06 06:01:08.356324343 +0700 +07	deployed	som-shop-0.1.0	1.7
```

- `helm pull -d pulled` ต้องมีโฟลเดอร์ `pulled` อยู่ก่อน (จึง `mkdir -p` ไว้)
- ติดตั้งจาก `oci://` **ไม่ต้อง `helm repo add`** ใช้เวลา 17.0 วินาที เปิดได้ที่ `http://oci.shop.localhost:30080`
- release ชื่อ `oci-som` แต่ `--set fullnameOverride=som` ทำให้ object ยังชื่อ `som-*` (ไม่งั้นจะเป็น `oci-som-web`, `oci-som-db`)

### ขั้นที่ 5: ล็อกด้วย digest และ logout

```bash
DIG=$(helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | grep -oE "sha256:[0-9a-f]+" | head -1); echo "digest=${DIG:0:19}..."
helm template x oci://localhost:5000/charts/som-shop@$DIG --plain-http --set db.password=x 2>&1 | grep -E "^kind:|Pulled|Digest" | head -4
helm registry logout localhost:5000
helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d /root 2>&1 | tail -1
```

```text
digest=sha256:ef59e9e33853...
Pulled: localhost:5000/charts/som-shop@sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
kind: Secret
kind: ConfigMap
Removing login credentials for localhost:5000
Error: failed to perform "FetchReference" on source: GET "http://localhost:5000/v2/charts/som-shop/manifests/0.1.0": basic credential not found
```

อ้างอิงด้วย `@sha256:...` ได้ chart ชุดเดิมเป๊ะ แม้วันหลังจะมีคน push `0.1.0` ทับ (ทฤษฎีหัวข้อ 14) หลัง logout ดึงไม่ได้อีก (`basic credential not found`)

> **chart กับ image คนละคนดึง:** chart ข้างบนถูกดึงโดย helm ที่รันใน k8s-lab (มองเห็น `localhost:5000`) แต่ image `som-shop-web` ถูกดึงโดย containerd บน Node ของ kind ซึ่ง `localhost` คือตัว Node เอง จึงไม่เห็นโกดังนี้ LAB จึงไม่ push image เข้าโกดัง (ระบบจริงใช้ registry ที่ Node มองเห็น + `imagePullSecrets` ของบทที่ 11)

### สิ่งที่เห็น

- `helm package` ได้ `som-shop-0.1.0.tgz` 5987 ไบต์, push ได้ digest `sha256:ef59e9e3…`
- login ต้องใช้ชื่อโฮสต์, credential เป็น base64
- ติดตั้งจาก `oci://` ได้ทั้งด้วย `--version` และ `@sha256:` (17.0 วินาที)

**คำถามชวนคิด**

1. ถ้าแก้ template แล้ว `helm package` + `helm push` โดยไม่เปลี่ยน `version: 0.1.0` จะเกิดอะไรกับคนที่ติดตั้งด้วย `--version 0.1.0` และคนที่ติดตั้งด้วย digest
2. องค์กรควรเก็บอะไรบ้างในโกดังของตัวเอง (chart อย่างเดียวพอไหม)

**เก็บกวาด LAB 11:**

```bash
helm uninstall oci-som -n oci-demo; kubectl delete ns oci-demo
docker rm -f som-registry
rm -rf som-shop-0.1.0.tgz auth pulled
cd ../..
```

```text
release "oci-som" uninstalled
namespace "oci-demo" deleted
som-registry
```

---

## LAB 12: LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง

<p align="center" id="fig-25">
  <img src="images/25-lab12-open.png" alt="รูปที่ 25 LAB 12 ภาพรวม" width="900"><br>
  <em><b>รูปที่ 25</b> LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง — ติดตั้งทั้งร้านด้วยคำสั่งเดียว สาขา dev และรับร้านเดิมเป็นสาขา prod</em>
</p>

**เป้าหมาย:** ใช้ทุกอย่างของบทนี้กับร้านจริง

1. เปิด **สาขา dev** ทั้งร้านใน namespace ใหม่ด้วยคำสั่งเดียว และตรวจรับด้วย `helm test`
2. **รับร้านเดิมของบท 013** (`som-shop` ที่ติดตั้งด้วย `kubectl apply` และมีออเดอร์อยู่แล้ว) เข้ามาอยู่ใต้ Helm เป็นสาขา prod โดยออเดอร์และใบรับรองเดิมไม่หาย
3. อัปเกรดหน้าร้าน 1.7 → **1.8** และย้อนรุ่น **ขณะที่ลูกค้าจำลองยิงเข้าร้านตลอดเวลา** โดยไม่มีลูกค้าเจอ error
4. ปิดสาขา dev และเข้าใจผลของตู้เซฟ (PVC) ที่ค้างอยู่

**ไฟล์:** `charts/som-shop`, `charts/values-dev.yaml`, `charts/values-prod.yaml`, `hit.sh` (ทำในโฟลเดอร์ `02_LAB` ทั้งหมด ใช้ **2 หน้าต่าง SSH**)

**สิ่งที่ต้องมีก่อน:** LAB 0 (image 1.8), LAB 10 (Traefik และ metrics-server จาก chart) และสาขา dev ของ LAB 9 ถูกลบแล้ว

เลข revision ของสาขา prod ที่จะเกิดในเครื่องทดลอง (ของนักศึกษาอาจต่างถ้าสั่งซ้ำหรือล้มเพิ่ม — ดู `helm history` ก่อน rollback ทุกครั้ง)

| rev | มาจาก | สถานะ |
|:---:|---|---|
| 1 | 12.4 (ข) `--take-ownership` ชน conflict | `failed` (ภายหลังเป็น `superseded`) |
| 2 | 12.4 (ค) `--take-ownership --force-conflicts` รับร้าน 1.7 | `deployed` → `superseded` |
| 3 | 12.6 upgrade 1.8 ไม่ใส่ `--force-conflicts` | `failed` |
| 4 | 12.6 upgrade 1.8 + `--force-conflicts` | `superseded` |
| 5 | 12.7 `helm rollback som 2` | `Rollback to 2` (1.7) |
| 6 | 12.7 upgrade 1.8 อีกครั้ง (ไม่ต้อง force แล้ว) | `deployed` |

### 12.1 จุดเริ่ม

```bash
cd /workspace/014_kubernetes_helm/02_LAB
helm list -A
kubectl -n som-shop get deploy,sts,hpa,ing
curl -sk https://shop.localhost:30081/api/stats; echo
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
fp() { kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-40; }
echo "cert ก่อน: $(fp)"
```

```text
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/customers   0/0     0            0           18m
deployment.apps/som-admin   1/1     1            1           20m
deployment.apps/som-web     2/2     2            2           20m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     20m

NAME                                          REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          19m

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   20m
ingress.networking.k8s.io/som-shop    traefik   shop.localhost    localhost   80, 443   20m
som-web-774d99d8df-r72bt 1.7 orders=3 products=6
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update
kube-controller-manager Update
cert ก่อน: sha256 Fingerprint=DF:E2:AD:87:27:0E:8B:
```

- Helm รู้จักแค่ add-on 2 ตัว (LAB 10) ส่วนร้าน `som-shop` ยังเป็นของ `kubectl` ล้วน: เจ้าของ field ของ `som-web` มี `kubectl-client-side-apply` (apply ไฟล์), `kubectl` (`set image`), `kubectl-rollout` (`rollout restart`) และ `kube-controller-manager` (ทฤษฎีหัวข้อ 9.1)
- จดออเดอร์ (`orders=3` ในเครื่องทดลอง ของนักศึกษาอาจต่าง) และ fingerprint ของใบรับรอง `som-tls` ไว้เทียบหลังรับร้าน (ฟังก์ชัน `fp` ใช้ได้ตลอด session นี้)

### 12.2 อ่านชุดแฟรนไชส์

<p align="center" id="fig-26">
  <img src="images/26-lab12-chart-tree.png" alt="รูปที่ 26 LAB 12 โครงชุด som-shop" width="900"><br>
  <em><b>รูปที่ 26</b> โครงชุด charts/som-shop: แม่พิมพ์ web, db, config, secret, ingress, hpa, seed hook, test + ใบสั่ง dev/prod</em>
</p>

โครงชุดดูได้จาก LAB 7 ขั้นที่ 1 (`find charts -type f | sort`) ตรวจชุดด้วยใบสั่งทั้งสองก่อนใช้จริง

```bash
helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x
helm lint charts/som-shop -f charts/values-dev.yaml --set db.password=x | tail -1
```

```text
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
1 chart(s) linted, 0 chart(s) failed
```

### 12.3 สาขา dev ด้วยคำสั่งเดียว

```bash
time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait
helm test som -n som-dev --logs | sed -n '/Phase/,$p'
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/ | grep -oE "ร้านอาหารแมวน้องส้ม \(dev\)|theme-[a-z]+|data-theme=\"[a-z]+\"" | sort -u
```

```text
NAME: som
LAST DEPLOYED: Tue Oct  6 06:02:08 2026
NAMESPACE: som-dev
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (dev) (release som, revision 1) ใน namespace som-dev แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: 1 (ไม่มี HPA)
   เปิดร้าน: curl http://dev.shop.localhost:30080/api/whoami
   ตรวจรับร้าน: helm test som -n som-dev --logs

real	0m18.037s
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-64c9f5cd95-lvbr9 1.7
products: ok

som-web-64c9f5cd95-lvbr9 1.7
theme-sunset
ร้านอาหารแมวน้องส้ม (dev)
```

<p align="center" id="fig-27">
  <img src="images/27-lab12-dev-branch.png" alt="รูปที่ 27 LAB 12 สาขา dev" width="900"><br>
  <em><b>รูปที่ 27</b> สาขา dev: helm install ... --wait ครั้งเดียวได้ทั้งร้าน (~18 วินาที) ป้ายร้านมีคำว่า (dev) ธีมส้ม</em>
</p>

ทั้งร้าน **18.0 วินาที** ตรวจรับผ่าน ธีม `sunset` และชื่อร้าน `(dev)` มาจากใบสั่ง 🌐 เปิด `http://dev.shop.localhost:30080`

<p align="center" id="fig-28">
  <img src="images/screenshots/20261006_0629_lab12helm_02-dev-branch.png" alt="รูปที่ 28 ภาพหน้าจอจริง สาขา dev" width="800"><br>
  <em><b>รูปที่ 28</b> ภาพหน้าจอจริงจากการทดลอง: สาขา dev ที่ http://dev.shop.localhost:30080 (release som ใน namespace som-dev) ธีมส้ม-ชมพู ชื่อร้าน &quot;ร้านอาหารแมวน้องส้ม (dev)&quot; ป้ายเวอร์ชัน 1.7 แถบ &quot;🧪 สาขาทดลอง&quot; ออเดอร์ 0 — เปิดจาก chart เดียวกับสาขาจริง ต่างแค่ใบสั่ง</em>
</p>

### 12.4 รับร้านเดิมเข้า Helm (สาขา prod)

<p align="center" id="fig-29">
  <img src="images/28-lab12-adopt-prod.png" alt="รูปที่ 29 LAB 12 รับร้านเดิมเป็น prod" width="900"><br>
  <em><b>รูปที่ 29</b> รับร้านเดิมของบท 013 (som-shop) เข้า Helm ด้วย --take-ownership --force-conflicts ออเดอร์เดิมยังอยู่ (rev 1 failed เพราะ conflict → rev 2 deployed)</em>
</p>

ร้านบท 013 มี object ชื่อ `som-web`, `som-db`, `som-db-secret`, `som-web-config`, `som-announcement`, `som-tls` ซึ่ง **ชื่อและ selector ตรงกับที่ chart สร้างจาก release `som`** (LAB 7) จึงรับได้ทีละชั้น (ทฤษฎีหัวข้อ 9.3) — ไม่ต้อง `--set db.password` เพราะ `lookup` อ่านรหัสจาก Secret เดิม

**(ก) install ทับ**

```bash
helm install som charts/som-shop -n som-shop -f charts/values-prod.yaml 2>&1 | cut -c1-300
helm list -n som-shop
```

```text
Error: INSTALLATION FAILED: unable to continue with install: Secret "som-tls" in namespace "som-shop" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annotation validation e
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
```

หยุดตั้งแต่ object แรกที่ไม่มีป้าย Helm ไม่มี release เกิดขึ้น

**(ข) --take-ownership**

```bash
helm upgrade --install som charts/som-shop -n som-shop -f charts/values-prod.yaml --take-ownership 2>&1 | cut -c1-2000
helm history som -n som-shop | cut -c1-120
```

```text
Release "som" does not exist. Installing it now.
Error: conflict occurred while applying object som-shop/som-web-config /v1, Kind=ConfigMap: Apply failed with 3 conflicts: conflicts with "kubectl-client-side-apply" using v1:
- .data.SHOP_EYEBROW
- .data.SHOP_FOOTER
- .data.SHOP_PROMO && conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 2 conflicts: conflicts with "kubectl-client-side-apply" using apps/v1:
- .spec.template.spec.containers[name="web"].env[name="POD_NAMESPACE"].valueFrom.fieldRef
- .spec.template.spec.initContainers[name="wait-for-db"].command && conflict occurred while applying object som-shop/som-db apps/v1, Kind=StatefulSet: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using apps/v1: .spec.volumeClaimTemplates
REVISION	UPDATED                 	STATUS	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	failed	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while applyi
        	                        	      	              	           	- .data.SHOP_EYEBROW
        	                        	      	              	           	- .data.SHOP_FOOTER
        	                        	      	              	           	- .data.SHOP_PROMO && conflict o...
```

`--take-ownership` ข้ามการตรวจป้ายได้ แต่ server-side apply พบ field ที่ `kubectl-client-side-apply` ถือไว้ด้วยค่าที่ **ต่างจาก chart**: ป้ายร้าน 3 ใบ (ข้อความของบท 013 vs บท 014), `POD_NAMESPACE` และคำสั่ง `wait-for-db` (เขียนต่างรูปแบบ) และ `volumeClaimTemplates` ของ db ได้ rev 1 `failed` (ร้านยังทำงานตามเดิม) รายการ conflict ในเครื่องนักศึกษาอาจต่างเล็กน้อยตามประวัติร้านของตัวเอง

> ⚠️ **ห้าม `helm uninstall som -n som-shop` ตอนนี้** — release ที่ล้มได้ติดป้าย Helm ให้บาง object ไปแล้ว uninstall จะลบของจริงของร้าน (ดู LAB 10 ขั้นที่ 2) ให้ทำ (ค) ต่อเลย

**(ค) --take-ownership --force-conflicts**

```bash
time helm upgrade --install som charts/som-shop -n som-shop -f charts/values-prod.yaml --take-ownership --force-conflicts --wait --timeout 5m 2>&1 | cut -c1-300
helm history som -n som-shop | cut -c1-120
kubectl -n som-shop get deploy,sts,hpa,ing,pvc
curl -sk https://shop.localhost:30081/api/stats; echo
echo "cert หลัง: $(fp)"
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d | sed 's/./*/g'; echo " (รหัสเดิมจาก lookup ซ่อนเป็น *)"
```

```text
Release "som" has been upgraded. Happy Helming!
NAME: som
LAST DEPLOYED: Tue Oct  6 06:02:29 2026
NAMESPACE: som-shop
STATUS: deployed
REVISION: 2
DESCRIPTION: Upgrade complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (release som, revision 2) ใน namespace som-shop แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: HPA 2–6 (cpu 50%)
   เปิดร้าน: curl -k https://shop.localhost:30081/api/whoami
   ตรวจรับร้าน: helm test som -n som-shop --logs

real	0m16.428s
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	superseded	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while ap
        	                        	          	              	           	- .data.SHOP_EYEBROW
        	                        	          	              	           	- .data.SHOP_FOOTER
        	                        	          	              	           	- .data.SHOP_PROMO && conflict o...
2       	Tue Oct  6 06:02:29 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/customers   0/0     0            0           18m
deployment.apps/som-admin   1/1     1            1           21m
deployment.apps/som-web     2/2     2            2           21m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     21m

NAME                                          REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          19m

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   21m
ingress.networking.k8s.io/som-shop    traefik   shop.localhost    localhost   80, 443   21m
ingress.networking.k8s.io/som-web     traefik   shop.localhost    localhost   80, 443   17s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-df0cbf66-e96a-4b84-a06b-bd9e3511b621   1Gi        RWO            standard       <unset>                 21m
som-web-5d8b4f958-662lc 1.7 orders=3 products=6
cert หลัง: sha256 Fingerprint=DF:E2:AD:87:27:0E:8B:
******** (รหัสเดิมจาก lookup ซ่อนเป็น *)
```

รับร้านสำเร็จเป็น **rev 2 ใน 16.4 วินาที**

- **ออเดอร์เดิมอยู่ครบ** (`orders=3`) และ PVC เดิม (AGE 21m) — Helm ไม่ได้สร้างร้านใหม่ แค่ยึดของเดิมมาดูแล
- **ใบรับรองเดิม** (fingerprint `DF:E2:AD:87:…` ก่อน = หลัง) เพราะแม่พิมพ์ ingress `lookup` เจอ `som-tls` จึงไม่สร้างใบใหม่ หลังร้าน `admin.localhost` ที่ใช้ใบเดียวกันจึงไม่พัง
- **รหัสเดิม** (8 ตัวอักษร ซ่อนไว้) มาจาก `lookup` ไม่ต้องส่งรหัสในคำสั่ง
- HPA เดิมถูก chart รับไปดูแล หน้าร้านยัง 2/2 (ไม่มี `replicas` ใน chart จึงไม่ทับ HPA)
- rev 1 เปลี่ยนเป็น `superseded` แต่ DESCRIPTION ยังเป็นข้อความ failed เดิม (สมุดไม่ลบประวัติ)
- ตอนนี้มี Ingress 2 ตัวที่ host `shop.localhost` (`som-shop` ของบท 013 กับ `som-web` ของ chart) และ `customers` ที่ chart ไม่รู้จัก → 12.5 เก็บของเก่า

ดู field ที่ chart ไม่ได้ตั้งแต่ยังอยู่

```bash
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
kubectl -n som-shop get deploy som-web -o jsonpath='{.metadata.annotations.kubernetes\.io/change-cause}{"\n"}{.metadata.annotations.meta\.helm\.sh/release-name}{"\n"}{.spec.template.spec.initContainers[*].name}{"\n"}'
kubectl -n som-shop get hpa som-web -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}{"\n"}'
```

```text
helm Apply
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update
kube-controller-manager Update
1.7 เพิ่ม /api/work + HPA
som
wait-for-db db-seed
60
```

- มี field manager `helm Apply` เพิ่มเข้ามา และ annotation `meta.helm.sh/release-name: som` (ป้ายสาขา) แต่เจ้าของเดิมยังอยู่
- change-cause ของบท 013 และ HPA behavior (window 60 วินาที) **ยังอยู่** เพราะ chart ไม่ได้ตั้ง field เหล่านี้ (server-side apply ไม่ลบ field ของคนอื่น)
- **initContainer มี 2 ตัว: `wait-for-db` และ `db-seed`** — `db-seed` ของบท 013 ค้างอยู่ทั้งที่ chart ใช้ hook seed แทน (12.5 ขั้น ค แก้)

> **ทางสำรอง (ไม่มีร้านบท 013 — คลัสเตอร์ใหม่ของ LAB 0):** ไม่มีอะไรให้รับ ติดตั้งสาขา prod ใหม่ด้วย
> ```bash
> helm install som charts/som-shop -n som-shop --create-namespace -f charts/values-prod.yaml --set db.password=meow1234 --wait
> ```
> ผลจากรอบ pre-check ของบทนี้ (namespace ทดลอง): ติดตั้ง 16 วินาที, `http` ได้ `301`, `https` ตอบ 1.7, `curl --cacert` ด้วยใบจาก `som-tls` ผ่าน, HPA ทำงาน ทางนี้ **ไม่มีหลังร้าน `som-admin`** และไม่มี conflict ให้ข้าม 12.5 ทั้งหมด ใน 12.6 ไม่ต้องใส่ `--force-conflicts` และเลข revision จะเป็น 1 (install) → 2 (1.8) → 3 (`Rollback to 1`) ให้ใช้เลขของตัวเองใน 12.7–12.8

### 12.5 เก็บของเก่า

**ขั้น ก: Ingress เดิมและลูกค้าจำลอง** — Ingress `som-shop` (บท 012) ซ้ำ host กับ `som-web` ของ chart และ `customers` (บท 013) ไม่ได้อยู่ในชุด **ไม่ลบ** Middleware `redirect-https` เพราะ Ingress `som-admin` ยังใช้อยู่ (ลบแล้วหลังร้านได้ 404)

```bash
kubectl -n som-shop delete ingress som-shop
kubectl -n som-shop delete deploy customers
kubectl -n som-shop get ing,middleware
curl -si http://shop.localhost:30080/ | grep -iE "^HTTP|^location"
curl -sk https://shop.localhost:30081/api/whoami; echo
curl -sk -u som:meow-admin-123 -o /dev/null -w "admin %{http_code}\n" https://admin.localhost:30081/
curl -sk https://shop.localhost:30081/ | grep -oE "⚓ ท่าเรือ Kubernetes · [A-Za-z]+|🎉 เปิดสาขาใหม่[^<]*" | sort -u | head -2
```

```text
ingress.networking.k8s.io "som-shop" deleted from som-shop namespace
deployment.apps "customers" deleted from som-shop namespace
NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   21m
ingress.networking.k8s.io/som-web     traefik   shop.localhost    localhost   80, 443   17s

NAME                                       AGE
middleware.traefik.io/admin-auth           21m
middleware.traefik.io/redirect-https       21m
middleware.traefik.io/som-redirect-https   17s
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/
som-web-5d8b4f958-662lc 1.7

admin 200
⚓ ท่าเรือ Kubernetes · Helm
🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว
```

ประตูหน้าร้านตอนนี้เป็นของ chart ทั้งหมด (Ingress `som-web` + Middleware `som-redirect-https`) redirect 301 ยังทำงาน หลังร้านยังเข้าได้ และหน้าร้านแสดงป้ายของบท 014 (`⚓ ท่าเรือ Kubernetes · Helm` + แถบ `🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว` จากใบสั่ง prod)

🌐 ดู dashboard ของ Traefik ที่ `http://localhost:30082/dashboard/#/http/routers`

<p align="center" id="fig-30">
  <img src="images/screenshots/20261006_0629_lab12helm_03-traefik-routers.png" alt="รูปที่ 30 ภาพหน้าจอจริง Traefik routers" width="800"><br>
  <em><b>รูปที่ 30</b> ภาพหน้าจอจริงจากการทดลอง: dashboard ของ Traefik v3.7.13 ที่ติดตั้งจาก chart (LAB 10) หน้า HTTP Routers เห็น router ของ dev.shop.localhost (สาขา dev), admin.localhost และ shop.localhost (สาขา prod ที่ chart สร้าง) ครบทั้งทางเข้า web และ websecure (มีโล่ TLS) — ถ่ายตอนที่สาขา dev ถูกเปิดอีกครั้งเพื่อถ่ายภาพ</em>
</p>

สังเกตว่า router แบบไม่มี TLS ของแต่ละ Ingress ผูกกับ entrypoint `metrics` ด้วย (นอกจาก `web`) เพราะ chart ของ Traefik เพิ่ม entrypoint `metrics` (พอร์ต 9100 สำหรับ Prometheus) ที่ static ของบท 012 ไม่มี และ Ingress ที่ไม่ระบุ entrypoint จะถูกผูกกับ entrypoint ที่มีอยู่ ส่วน `websecure` แยกเป็น router ที่มี TLS — เป็นตัวอย่างว่า chart ทางการ "ไม่เหมือนเดิม 100%" ควรอ่านผล render ก่อน

**ขั้น ข: หา field ที่เหลือจากบท 013**

```bash
kubectl -n som-shop get deploy som-web -o json | python3 -c '
import json,sys; d=json.load(sys.stdin); s=d["spec"]["template"]["spec"]
print("initContainers:", [c["name"] for c in s.get("initContainers",[])])
print("pod annotations:", sorted(d["spec"]["template"]["metadata"].get("annotations",{}).keys()))'
helm get manifest som -n som-shop | python3 -c '
import sys,re; m=sys.stdin.read(); dep=[x for x in m.split("\n---") if "kind: Deployment" in x][0]
print("chart initContainers:", re.findall(r"- name: (wait-for-db|db-seed)", dep))'
kubectl -n som-shop get deploy som-web --show-managed-fields -o json | python3 -c '
import json,sys; d=json.load(sys.stdin)
for m in d["metadata"]["managedFields"]:
    f=json.dumps(m.get("fieldsV1",{}))
    print(m["manager"], m["operation"], "owns db-seed" if "db-seed" in f else "")'
```

```text
initContainers: ['wait-for-db', 'db-seed']
pod annotations: ['checksum/config', 'checksum/secret', 'kubectl.kubernetes.io/restartedAt']
chart initContainers: ['wait-for-db']
helm Apply
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update owns db-seed
kube-controller-manager Update
```

Deployment จริงมี initContainer 2 ตัว แต่ manifest ของ release (`helm get manifest`) มีแค่ `wait-for-db` และ **ผู้ถือ `db-seed` คือ `kubectl-client-side-apply`** Helm จึงไม่ลบให้ (ไม่ใช่ field ของ `helm`) — ไม่เสียหาย แต่ทุกบูธใหม่จะ seed ซ้ำโดยไม่จำเป็น และร้านไม่ตรงกับชุดแฟรนไชส์ annotation `restartedAt` ของ `kubectl-rollout` ก็ค้างเช่นกัน (ไม่มีผล)

> `kubectl get -o json` ซ่อน `managedFields` เป็นค่าเริ่มต้น ต้องใส่ `--show-managed-fields` (ในเครื่องทดลองรอบแรกที่ไม่ใส่ python ได้ `KeyError: 'managedFields'`)

**ขั้น ค: ถอด initContainer `db-seed` ระหว่างลูกค้าเข้าร้าน**

ใช้ JSON patch ที่มีคำสั่ง `test` ยืนยันก่อนว่าตำแหน่ง `initContainers/1` คือ `db-seed` จริง (ถ้าไม่ใช่ patch จะไม่ทำอะไรเลย กันลบผิดตัว) สั่ง patch ฉากหลังแล้วยิงลูกค้า 250 ครั้งพร้อมกัน

```bash
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.initContainers[1].name}{"\n"}'
(sleep 2; kubectl -n som-shop patch deploy som-web --type=json -p='[{"op":"test","path":"/spec/template/spec/initContainers/1/name","value":"db-seed"},{"op":"remove","path":"/spec/template/spec/initContainers/1"}]') & ./hit.sh -q https://shop.localhost:30081/api/whoami 250 0.1; wait
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
kubectl -n som-shop get pod -l app=som-web -o jsonpath='{range .items[*]}{.metadata.name}{" init="}{.spec.initContainers[*].name}{"\n"}{end}'
```

```text
db-seed
...................deployment.apps/som-web patched
...........................................................................................................
จำนวน  Pod  เวอร์ชัน
    250 1.7 (เวอร์ชัน)
ok=250 err=0 (ใช้เวลา 28.0 วินาที)
deployment "som-web" successfully rolled out
som-web-d776d4768-cqnvq init=wait-for-db
som-web-d776d4768-gbc7j init=wait-for-db
```

rolling update เปลี่ยนบูธทั้งสองเป็นแบบที่มีแค่ `wait-for-db` ลูกค้า **`ok=250 err=0`** ตอนนี้ร้านตรงกับชุดแฟรนไชส์แล้ว (ระบบจริงควรทำความสะอาดแบบนี้ทุกครั้งหลังรับของเดิมเข้า Helm)

### 12.6 อัปเกรดเป็น 1.8 ระหว่างลูกค้าเข้าร้าน

**ลองก่อนโดยไม่ force**

```bash
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | cut -c1-600
helm history som -n som-shop --max 2 | cut -c1-140
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

```text
level=WARN msg="upgrade failed" name=som error="conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with \"kubectl-client-side-apply\" using apps/v1: .spec.template.spec.containers[name=\"web\"].image"
Error: UPGRADE FAILED: conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using apps/v1: .spec.template.spec.containers[name="web"].image
REVISION	UPDATED                 	STATUS  	CHART         	APP VERSION	DESCRIPTION
2       	Tue Oct  6 06:02:29 2026	deployed	som-shop-0.1.0	1.7        	Upgrade complete
3       	Tue Oct  6 06:03:50 2026	failed  	som-shop-0.1.0	1.7        	Upgrade "som" failed: conflict occurred while applying object som-shop
som-shop-web:1.7
```

**conflict อีกครั้ง** ที่ field image: ตอนรับร้าน (rev 2) chart ตั้ง image เป็น `1.7` ซึ่ง **เท่ากับ** ค่าที่ `kubectl-client-side-apply` ถือไว้ จึงไม่ชน (ถือร่วมกัน) พอจะเปลี่ยนเป็น `1.8` ค่าไม่ตรงกับเจ้าของเดิมจึงชน (ทฤษฎีหัวข้อ 9.2) rev 3 `failed` ร้านยังเป็น 1.7 ไม่มีอะไรเสียหาย

**อัปเกรดจริงด้วย --force-conflicts (2 หน้าต่าง)**

**หน้าต่างที่ 2**

```bash
cd /workspace/014_kubernetes_helm/02_LAB
./hit.sh -q https://shop.localhost:30081/api/whoami 400 0.1
```

**หน้าต่างที่ 1** (ภายในไม่กี่วินาที)

```bash
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --force-conflicts --wait 2>&1 | grep -E "REVISION|STATUS|image|Error"
echo "upgrade: $(( $(date +%s)-t0 )) วินาที"
curl -sk https://shop.localhost:30081/api/whoami; echo
helm history som -n som-shop | cut -c1-120
```

หน้าต่างที่ 1

```text
STATUS: deployed
REVISION: 4
   image หน้าร้าน: som-shop-web:1.8
upgrade: 15 วินาที
som-web-56875c6cb5-6dwms 1.8

REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	superseded	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while ap
        	                        	          	              	           	- .data.SHOP_EYEBROW
        	                        	          	              	           	- .data.SHOP_FOOTER
        	                        	          	              	           	- .data.SHOP_PROMO && conflict o...
2       	Tue Oct  6 06:02:29 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
3       	Tue Oct  6 06:03:50 2026	failed    	som-shop-0.1.0	1.7        	Upgrade "som" failed: conflict occurred while ap
4       	Tue Oct  6 06:03:54 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

หน้าต่างที่ 2

```text
................................................................................................................
จำนวน  Pod  เวอร์ชัน
     84 1.7 (เวอร์ชัน)
    316 1.8 (เวอร์ชัน)
ok=400 err=0 (ใช้เวลา 44.7 วินาที)
```

<p align="center" id="fig-31">
  <img src="images/29-lab12-upgrade-err0.png" alt="รูปที่ 31 LAB 12 อัปเกรด 1.8 err=0" width="900"><br>
  <em><b>รูปที่ 31</b> อัปเกรด prod 1.7 → 1.8 ระหว่างลูกค้าเข้าร้าน (hit.sh) ไม่มีลูกค้าเจอ error แม้ upgrade แรกหลังรับร้านต้อง --force-conflicts อีกครั้ง</em>
</p>

rev 4 ใช้ **15 วินาที** ลูกค้า **`ok=400 err=0`** (84 ครั้งเจอ 1.7 ก่อนสลับ 316 ครั้งเจอ 1.8) — rolling update `maxUnavailable: 0` + readinessProbe + preStop ของบทที่ 7 ทำงานเหมือนเดิม Helm แค่เป็นคนสั่ง สังเกตคอลัมน์ **APP VERSION ยังเป็น 1.7** เพราะมาจาก `appVersion` ใน `Chart.yaml` ไม่ใช่ image ที่ใช้จริง (ทฤษฎีหัวข้อ 4.2)

### 12.7 ประวัติและย้อนรุ่น

```bash
helm history som -n som-shop -o table --max 10 | cut -c1-120
for r in 2 4; do echo "rev $r: $(helm get values som -n som-shop --revision $r -o json)"; done
```

```text
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	superseded	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while ap
...
2       	Tue Oct  6 06:02:29 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
3       	Tue Oct  6 06:03:50 2026	failed    	som-shop-0.1.0	1.7        	Upgrade "som" failed: conflict occurred while ap
4       	Tue Oct  6 06:03:54 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
rev 2: {"hpa":{"enabled":true,"maxReplicas":6,"minReplicas":2},"ingress":{"enabled":true,"host":"shop.localhost","tls":true},"shop":{"APP_THEME":"harbor","SHOP_NAME":"ร้านอาหารแมวน้องส้ม","SHOP_PROMO":"🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"}}
rev 4: {"hpa":{"enabled":true,"maxReplicas":6,"minReplicas":2},"ingress":{"enabled":true,"host":"shop.localhost","tls":true},"shop":{"APP_THEME":"harbor","SHOP_NAME":"ร้านอาหารแมวน้องส้ม","SHOP_PROMO":"🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"},"web":{"image":{"tag":"1.8"}}}
```

ตาราง history บอกไม่ได้ว่ารุ่นไหนเป็น image อะไร (APP VERSION 1.7 ทุกแถว) ต้องดูใบสั่งของแต่ละ revision: rev 2 ไม่มี `web.image.tag` (= 1.7 จาก appVersion) rev 4 มี `tag: "1.8"` → **รุ่นที่ดีของ 1.7 คือ rev 2** (rev 3 ก็ "เป็น 1.7" แต่สถานะ `failed` — ห้ามเลือก และห้าม `helm rollback som` แบบไม่ใส่เลข เพราะจะไป rev 3)

**ย้อนเป็น 1.7 ระหว่างลูกค้าเข้าร้าน** — หน้าต่างที่ 2: `./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1` หน้าต่างที่ 1:

```bash
t0=$(date +%s)
helm rollback som 2 -n som-shop --wait 2>&1 | tail -1
echo "rollback: $(( $(date +%s)-t0 )) วินาที"
helm history som -n som-shop --max 2 | cut -c1-120
curl -sk https://shop.localhost:30081/api/whoami; echo
```

หน้าต่างที่ 1

```text
Rollback was a success! Happy Helming!
rollback: 11 วินาที
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
4       	Tue Oct  6 06:03:54 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
5       	Tue Oct  6 06:04:49 2026	deployed  	som-shop-0.1.0	1.7        	Rollback to 2
som-web-d776d4768-twh2d 1.7

```

หน้าต่างที่ 2

```text
.......................................................................................................
จำนวน  Pod  เวอร์ชัน
    215 1.7 (เวอร์ชัน)
     85 1.8 (เวอร์ชัน)
ok=300 err=0 (ใช้เวลา 33.6 วินาที)
```

<p align="center" id="fig-32">
  <img src="images/30-lab12-rollback.png" alt="รูปที่ 32 LAB 12 rollback ระบุเลข" width="900"><br>
  <em><b>รูปที่ 32</b> helm history แล้ว rollback ไป revision ที่เป็น 1.7 (ระบุเลข) ได้หน้าใหม่ในสมุด ลูกค้าไม่เจอ error</em>
</p>

rollback **11 วินาที** ได้ **rev 5 `Rollback to 2`** ลูกค้า **`ok=300 err=0`** — ทั้งร้าน (ป้าย, ซอง, Deployment, HPA, Ingress) กลับไปตามใบสั่งของ rev 2 ไม่ใช่แค่ Deployment แบบ `kubectl rollout undo` สังเกตว่า Pod ที่ได้ (`som-web-d776d4768-…`) คือ ReplicaSet เดียวกับหลัง 12.5 ขั้น ค เพราะ Pod template เหมือนกันทุกตัวอักษร Deployment จึงนำ ReplicaSet เดิมกลับมาใช้

**upgrade กลับเป็น 1.8 — คราวนี้ไม่ต้อง force** (หน้าต่างที่ 2 ยิง 300 ครั้งเหมือนเดิม)

```bash
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | grep -E "REVISION|STATUS|Error"
echo "upgrade: $(( $(date +%s)-t0 )) วินาที"
helm history som -n som-shop --max 3 | cut -c1-120
```

```text
STATUS: deployed
REVISION: 6
upgrade: 15 วินาที
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
4       	Tue Oct  6 06:03:54 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
5       	Tue Oct  6 06:04:49 2026	superseded	som-shop-0.1.0	1.7        	Rollback to 2
6       	Tue Oct  6 06:05:23 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

หน้าต่างที่ 2 ได้ `ok=300 err=0` (1.7 = 87, 1.8 = 213) — `--force-conflicts` ครั้งเดียวใน rev 4 โอน field image ให้ `helm` แล้ว ต่อจากนี้ upgrade/rollback เป็นงานปกติของ Helm

**รอบถ่ายภาพหน้าจอ** (ทำซ้ำบนคลัสเตอร์เดิมหลังจบขั้น 12.10 โดยเปิดสาขา dev อีกครั้งและมีออเดอร์ทดสอบเพิ่ม ร้าน prod จึงมี 5 ออเดอร์) ผลคำสั่งจริงของรอบนั้น

```text
$ time helm rollback som 2 -n som-shop --wait
Rollback was a success! Happy Helming!

real	0m10.338s
--- hit.sh ระหว่าง rollback
ok=250 err=0 (ใช้เวลา 28.0 วินาที)
$ time helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait
Release "som" has been upgraded. Happy Helming!
NAME: som
LAST DEPLOYED: Tue Oct  6 06:29:41 2026
NAMESPACE: som-shop
STATUS: deployed
REVISION: 8

real	0m13.834s
--- hit.sh ระหว่าง upgrade
ok=250 err=0 (ใช้เวลา 28.0 วินาที)
$ helm history som -n som-shop --max 3
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
6       	Tue Oct  6 06:05:23 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
7       	Tue Oct  6 06:29:13 2026	superseded	som-shop-0.1.0	1.7        	Rollback to 2
8       	Tue Oct  6 06:29:41 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

<p align="center" id="fig-33">
  <img src="images/screenshots/20261006_0629_lab12helm_04-after-rollback-1.7.png" alt="รูปที่ 33 ภาพหน้าจอจริง หลัง rollback เป็น 1.7" width="800"><br>
  <em><b>รูปที่ 33</b> ภาพหน้าจอจริงจากการทดลอง: หลัง helm rollback som 2 --wait (10.3 วินาที ได้ revision 7 &quot;Rollback to 2&quot;) หน้าร้าน https://shop.localhost:30081 กลับเป็นป้ายเวอร์ชัน 1.7 ออเดอร์ 5 รายการยังอยู่ ระหว่างนั้น hit.sh ได้ ok=250 err=0</em>
</p>

<p align="center" id="fig-34">
  <img src="images/screenshots/20261006_0629_lab12helm_05-after-upgrade-1.8.png" alt="รูปที่ 34 ภาพหน้าจอจริง หลัง upgrade กลับ 1.8" width="800"><br>
  <em><b>รูปที่ 34</b> ภาพหน้าจอจริงจากการทดลอง: helm upgrade ... --set web.image.tag=1.8 --wait (13.8 วินาที ได้ revision 8 ไม่ต้อง --force-conflicts แล้ว) หน้าร้านกลับเป็นเวอร์ชัน 1.8 ระหว่างนั้น hit.sh ได้ ok=250 err=0</em>
</p>

### 12.8 ซองในสมุดของสาขา prod

```bash
kubectl -n som-shop get secret -l owner=helm,name=som
kubectl -n som-shop get secret sh.helm.release.v1.som.v2 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d \
  | python3 -c 'import json,sys,re; r=json.load(sys.stdin); print("config:", json.dumps(r["config"],ensure_ascii=False)); print(re.findall(r"DATABASE_URL: .*", r["manifest"])); print(re.findall(r"POSTGRES_PASSWORD: .*", r["manifest"])); print("tls.key อยู่ใน manifest:", "tls.key:" in r["manifest"])'
```

```text
NAME                        TYPE                 DATA   AGE
sh.helm.release.v1.som.v1   helm.sh/release.v1   1      3m39s
sh.helm.release.v1.som.v2   helm.sh/release.v1   1      3m38s
sh.helm.release.v1.som.v3   helm.sh/release.v1   1      2m17s
sh.helm.release.v1.som.v4   helm.sh/release.v1   1      2m13s
sh.helm.release.v1.som.v5   helm.sh/release.v1   1      78s
sh.helm.release.v1.som.v6   helm.sh/release.v1   1      44s
config: {"hpa": {"enabled": true, "maxReplicas": 6, "minReplicas": 2}, "ingress": {"enabled": true, "host": "shop.localhost", "tls": true}, "shop": {…}}
['DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"']
['POSTGRES_PASSWORD: "meow1234"']
tls.key อยู่ใน manifest: True
```

(ผล config ตัดให้สั้น) rev 2 **ไม่ได้ส่งรหัสในคำสั่งเลย** (`config` ไม่มี `db.password`) แต่ **manifest** เก็บผล render ของ Secret ทั้งก้อน จึงมีรหัสฐานข้อมูล (ที่ `lookup` อ่านมา) **และกุญแจลับของใบรับรอง (`tls.key`)** ด้วย — การปกป้องร้านจึงต้องคุมสิทธิ์อ่าน Secret ใน namespace (RBAC บทที่ 11) ไม่ใช่แค่ไม่ใส่รหัสในใบสั่ง (ทฤษฎีหัวข้อ 10) **ห้ามคัดลอกหรือแชร์ผลถอดของ `tls.key`**

### 12.9 ปิดสาขา dev

**ขั้น ก: uninstall แล้วตู้เซฟค้าง**

```bash
curl -s -XPOST -H "content-type: application/json" -d '{"product_id":1,"qty":2}' http://dev.shop.localhost:30080/api/orders; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev
sleep 8; kubectl -n som-dev get all,pvc,secret
helm list -A
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
som-web-64c9f5cd95-lvbr9 1.7 orders=1 products=6

release "som" uninstalled
NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-634d0a60-bd70-46ad-b23d-605ccc52a76b   1Gi        RWO            standard       <unset>                 4m7s
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
som           	som-shop   	6       	2026-10-06 06:05:23.632314816 +0700 +07	deployed	som-shop-0.1.0       	1.7
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
```

(ออเดอร์ใช้ key `product_id` และ `qty` — ถ้าส่ง `productId` แอปตอบ `ข้อมูลไม่ถูกต้อง`) หลัง uninstall ทุก object ของสาขาหาย **เหลือแต่ตู้เซฟ `data-som-db-0` สถานะ `Bound`** (PVC จาก `volumeClaimTemplates` ไม่ใช่ส่วนของ release — บทที่ 9)

**ขั้น ข: ติดตั้งใหม่ด้วยรหัสเดิม → ข้อมูลเดิมกลับมา**

```bash
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait | grep -E "STATUS|REVISION"
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev; sleep 8
```

```text
STATUS: deployed
REVISION: 1

real	0m11.904s
som-web-64c9f5cd95-869r5 1.7 orders=1 products=6

release "som" uninstalled
```

<p align="center" id="fig-35">
  <img src="images/31-lab12-uninstall-dev.png" alt="รูปที่ 35 LAB 12 uninstall สาขา dev" width="900"><br>
  <em><b>รูปที่ 35</b> helm uninstall สาขา dev: ร้านถูกรื้อ แต่ตู้เซฟ (PVC data-som-db-0) ยังอยู่ ติดตั้งใหม่รหัสเดิมได้ออเดอร์เดิม</em>
</p>

สาขาใหม่ REVISION 1 (สมุดเล่มใหม่) แต่ **`orders=1` กลับมา** เพราะ StatefulSet ใช้ PVC ชื่อเดิม ติดตั้งเร็วขึ้น (11.9 วินาที) ส่วนหนึ่งน่าจะเพราะ db ไม่ต้องสร้างฐานข้อมูลใหม่ จากนั้น uninstall อีกครั้ง (PVC ยังค้างอยู่) เพื่อลองกับดักถัดไป

**ขั้น ค: กับดัก — ติดตั้งใหม่ด้วยรหัสใหม่ (ไม่ใส่ --wait)**

`purr5678` เป็นรหัสตัวอย่างอีกตัว

```bash
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=purr5678 --timeout 90s 2>&1 | tail -2
helm list -n som-dev
kubectl -n som-dev get pod,job
kubectl -n som-dev logs job/som-seed -c seed --tail=3 2>&1 | tail -3
```

```text
Error: INSTALLATION FAILED: failed post-install: resource Job/som-dev/som-seed not ready. status: Failed, message: Job Failed. failed: 1/1

real	0m45.711s
NAME	NAMESPACE	REVISION	UPDATED                                	STATUS	CHART         	APP VERSION
som 	som-dev  	1       	2026-10-06 06:09:08.509818895 +0700 +07	failed	som-shop-0.1.0	1.7
NAME                          READY   STATUS    RESTARTS      AGE
pod/som-db-0                  1/1     Running   0             46s
pod/som-seed-9sjtp            0/1     Error     3 (29s ago)   46s
pod/som-web-f45d5f58d-zqjwz   0/1     Running   0             46s

NAME                 STATUS   COMPLETIONS   DURATION   AGE
job.batch/som-seed   Failed   0/1           46s        46s
}

Node.js v22.23.3
```

<p align="center" id="fig-36">
  <img src="images/32-lab12-wrong-password.png" alt="รูปที่ 36 LAB 12 กับดักรหัสใหม่" width="900"><br>
  <em><b>รูปที่ 36</b> กับดัก: ติดตั้ง dev ใหม่ (ไม่ใส่ --wait) ด้วยรหัสใหม่ แต่ตู้เซฟเดิมใช้รหัสเก่า → hook เติมสินค้าล้ม failed post-install (ถ้าใส่ --wait จะล้มที่ som-web not ready ก่อนถึง hook)</em>
</p>

PostgreSQL ตั้งรหัสเฉพาะตอนสร้าง data directory ครั้งแรก ตู้เซฟเดิมจึงยังล็อกด้วย `meow1234` ขณะที่ Secret ใหม่ของ chart เป็น `purr5678` ผล:

- หน้าร้าน `0/1` (readinessProbe `/api/health` ต่อ db ไม่ได้)
- Job seed (`post-install`) login ไม่ได้ ล้มครบ `backoffLimit: 3` → **`failed post-install ... Job Failed`** ใน 45.7 วินาที release เป็น `failed`
- Job/Pod ที่ล้ม **ยังอยู่ให้ดู log** เพราะ delete policy ไม่มี `hook-failed` (ท้าย log เป็น stack trace ของ Node.js ดูเต็มด้วย `kubectl -n som-dev logs job/som-seed -c seed`)

ผลจริงอีกแบบ (ไม่ต้องทำตาม ใช้เวลา 90 วินาที): ถ้าสั่งแบบเดียวกันแต่ **ใส่ `--wait --timeout 90s`** Helm รอหน้าร้านพร้อมก่อนถึง hook จึงล้มที่หน้าร้านแทน

```text
Error: INSTALLATION FAILED: resource Deployment/som-dev/som-web not ready. status: InProgress, message: Available: 0/1
context deadline exceeded

real	1m30.215s
```

**แก้:** upgrade release ที่ `failed` ด้วยรหัสเดิม (upgrade ได้เลย ไม่ต้อง uninstall ก่อน)

```bash
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait 2>&1 | grep -E "STATUS|REVISION|Error"
curl -s http://dev.shop.localhost:30080/api/stats; echo
```

```text
STATUS: deployed
REVISION: 2
som-web-64c9f5cd95-b4q8j 1.7 orders=1 products=6

```

(ผลนี้มาจากการแก้หลังกรณี `--wait` ในเครื่องทดลอง สภาพเริ่มต้นเหมือนกัน คือ release `failed` + ตู้เซฟเดิม) ร้านกลับมาพร้อมออเดอร์เดิม ถ้าต้องการเริ่มสาขาใหม่จริง ๆ ด้วยรหัสใหม่ ต้องลบตู้เซฟเดิมก่อน (ข้อมูลหาย)

**ลบสาขา dev จริงทั้งหมด (รวมตู้เซฟ)**

```bash
helm uninstall som -n som-dev
kubectl delete ns som-dev
```

```text
release "som" uninstalled
namespace "som-dev" deleted
```

### 12.10 ตรวจรับร้านและปิดบท

```bash
helm test som -n som-shop --logs | sed -n '/Phase/,$p'
kubectl -n som-shop get deploy,sts,hpa,ing
kubectl top pod -n som-shop
curl -sk https://shop.localhost:30081/api/stats; echo
curl -s --cacert <(kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d) https://shop.localhost:30081/api/whoami; echo " (cacert ok)"
helm list -A
```

```text
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-56875c6cb5-9r2rg 1.8
products: ok

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-admin   1/1     1            1           27m
deployment.apps/som-web     2/2     2            2           27m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     27m

NAME                                          REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          25m

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   27m
ingress.networking.k8s.io/som-web     traefik   shop.localhost    localhost   80, 443   6m6s
NAME                         CPU(cores)   MEMORY(bytes)
som-admin-5f75ddc94b-lqswj   1m           23Mi
som-db-0                     8m           39Mi
som-web-56875c6cb5-5c54d     2m           42Mi
som-web-56875c6cb5-9r2rg     2m           41Mi
som-web-56875c6cb5-9r2rg 1.8 orders=3 products=6

som-web-56875c6cb5-5c54d 1.8
 (cacert ok)
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
som           	som-shop   	6       	2026-10-06 06:05:23.632314816 +0700 +07	deployed	som-shop-0.1.0       	1.7
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
```

ผู้ตรวจรับร้านผ่าน (หน้าร้าน 1.8 ต่อ db ได้) HPA 2–6 ทำงานด้วย metrics-server จาก chart, `curl --cacert` ด้วยใบจาก `som-tls` ผ่านโดยไม่ต้อง `-k` (ใบเดิมของบท 012 ใช้ต่อได้จริง) ออเดอร์เดิม 3 รายการอยู่ครบ และ **`helm list -A` เห็นทั้งท่าเรือ 3 release** — ร้าน ประตู และเจ้าหน้าที่จดมิเตอร์ ติดตั้ง/อัปเกรด/ย้อนได้ด้วยคำสั่งเดียวทั้งหมด 🌐 เปิด `http://shop.localhost:30080`

<p align="center" id="fig-37">
  <img src="images/screenshots/20261006_0629_lab12helm_01-prod-1.8.png" alt="รูปที่ 37 ภาพหน้าจอจริง หน้าร้าน prod 1.8" width="800"><br>
  <em><b>รูปที่ 37</b> ภาพหน้าจอจริงจากการทดลอง: สาขาจริง (release som ใน namespace som-shop) รุ่น 1.8 ที่ https://shop.localhost:30081 หัวร้าน &quot;⚓ ท่าเรือ Kubernetes · Helm&quot; แถบ &quot;🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว&quot; จากใบสั่ง prod และออเดอร์ 5 รายการ (ออเดอร์เดิมของบท 013 + ออเดอร์ทดสอบรอบถ่ายภาพ) ไม่หายระหว่างรับร้าน อัปเกรด และย้อนรุ่น</em>
</p>

<p align="center" id="fig-38">
  <img src="images/33-lab12-checklist.png" alt="รูปที่ 38 LAB 12 ตรวจรับร้าน" width="900"><br>
  <em><b>รูปที่ 38</b> ตรวจรับร้าน: dev helm test ผ่าน, prod HTTPS + HPA, upgrade 1.8 err=0, rollback ระบุเลข, เข้าใจ PVC ค้าง</em>
</p>

| ข้อตรวจรับ | ผลจริง (เครื่อง 4 CPU) |
|---|---|
| สาขา dev คำสั่งเดียว | 18.0 วินาที, `helm test` Succeeded, ธีม `sunset`, ชื่อ `(dev)` |
| รับร้านเดิมเป็น prod | rev 1 `failed` (conflict) → rev 2 `deployed` 16.4 วินาที, `orders=3`, ใบรับรองและรหัสเดิม |
| ร้านตรงกับชุด | ลบ Ingress `som-shop`, `customers`, initContainer `db-seed` (`ok=250 err=0`) |
| อัปเกรด 1.8 | rev 3 `failed` (conflict image) → rev 4 + `--force-conflicts` 15 วินาที `ok=400 err=0` |
| ย้อนรุ่นระบุเลข | `helm rollback som 2` → rev 5 `Rollback to 2` 11 วินาที `ok=300 err=0` |
| upgrade ครั้งต่อไปไม่ต้อง force | rev 6 15 วินาที `ok=300 err=0` |
| ความลับใน release Secret | rev 2 มีรหัส db และ `tls.key` แม้ไม่ได้ส่งรหัส |
| PVC ค้าง | uninstall dev เหลือ `data-som-db-0`, รหัสเดิมได้ `orders=1`, รหัสใหม่ `failed post-install` |
| ปิดท้าย | prod test Succeeded (1.8), `--cacert` ผ่าน, `helm list -A` 3 release |

<p align="center" id="fig-39">
  <img src="images/34-lab12-wrap-up.png" alt="รูปที่ 39 ปิดบท" width="900"><br>
  <em><b>รูปที่ 39</b> ปิดบท: เก็บ chart + ใบสั่งใน Git ให้หุ่นยนต์ GitOps ดูแล (Argo CD/Flux), แผ่นใสซ้อน (Kustomize), หุ่นยนต์ดูแลร้าน (operator)</em>
</p>

ร้านน้องส้มเป็น "ชุดแฟรนไชส์" แล้ว แต่ยังเหลือโจทย์ที่ Helm ไม่ได้ตอบ

- **ใครเป็นคนสั่ง `helm upgrade`?** ตอนนี้คือเราพิมพ์เอง ถ้ามีคนแก้ร้านด้วย `kubectl edit` ก็ไม่มีใครรู้ → **GitOps** (Argo CD/Flux): เก็บ `charts/som-shop` + `values-prod.yaml` ใน Git ให้ controller ทำให้ร้านตรงกับ Git เสมอ (ทฤษฎีหัวข้อ 16)
- **ปรับ chart ของคนอื่นเล็กน้อยโดยไม่ fork** → Kustomize/post-renderer (ทฤษฎีหัวข้อ 15)
- **ใครดูแลครัวหลังเปิดร้าน?** Helm ติดตั้งจบแล้วไม่สำรองข้อมูล ไม่ซ่อม db ไม่อัปเกรด PostgreSQL ให้ → **operator** (บทถัดไป)
- **รหัสยังอยู่ใน release Secret** → External Secrets / Sealed Secrets / SOPS

**คำถามท้าย LAB 12**

1. ทำไมรับร้านน้องส้มเข้า Helm ได้ แต่รับ Traefik static ไม่ได้ (เทียบ selector) และถ้าเผลอ `helm uninstall som -n som-shop` หลัง 12.4 (ข) จะเกิดอะไร
2. ทำไม upgrade แรกหลังรับร้านยัง conflict ที่ image ทั้งที่ตอนรับร้านใส่ `--force-conflicts` แล้ว และทำไม upgrade ครั้งที่สอง (rev 6) ไม่ต้อง force
3. ถ้าต้องย้อนเป็น 1.7 ควร rollback เลขอะไร ทำไมไม่ใช่ rev 3 และทำไมเลข revision ไม่ถอยหลัง
4. ทำไม PVC `data-som-db-0` ค้างหลัง `helm uninstall` เป็นข้อดีหรือข้อเสีย และทำไมติดตั้งใหม่ด้วยรหัสใหม่จึงล้ม
5. ใครอ่านรหัสฐานข้อมูลและ `tls.key` ของร้าน prod ได้บ้าง (ทั้งจาก Secret ของร้านและจาก release Secret) จะลดความเสี่ยงอย่างไร
6. ถ้าจะใช้ GitOps ดูแลร้านนี้ จะเก็บอะไรใน Git บ้าง และอะไรห้ามเก็บ

**เก็บกวาด LAB 12:** สาขา dev ถูกลบแล้วใน 12.9 สาขา prod (`som` ใน `som-shop`), Traefik และ metrics-server **เก็บไว้** (ดูตารางท้ายเอกสาร)

---

## LAB เสริม: helm-diff และ umbrella chart (ไม่บังคับ)

ทำหลัง LAB 12 (ใช้ release `som` ใน `som-shop`) ต้องต่ออินเทอร์เน็ต (GitHub และ `ghcr.io`)

### ก. helm-diff: ดูความต่างก่อน upgrade

plugin `helm-diff` แสดงว่า upgrade จะเปลี่ยนอะไร (คล้าย `git diff`) ก่อนสั่งจริง Helm 4 ตรวจที่มาของ plugin และ helm-diff ต้องเป็น **v3.15.15 ขึ้นไป** จึงใช้กับ Helm 4 ได้

```bash
cd /workspace/014_kubernetes_helm/02_LAB
timeout 180 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 2>&1 | tail -1
timeout 180 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 --verify=false 2>&1 | tail -1
helm plugin list
helm diff upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.7 2>&1 | grep -E "^[+-] |has changed|Error" | head -12
helm plugin uninstall diff
```

```text
Error: plugin source does not support verification. Use --verify=false to skip verification
Installed plugin: diff
NAME	VERSION	TYPE  	APIVERSION	PROVENANCE	SOURCE
diff	3.15.15	cli/v1	legacy    	unknown   	unknown
som-shop, som-announcement, ConfigMap (v1) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
som-shop, som-db, Service (v1) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
som-shop, som-db, StatefulSet (apps) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
som-shop, som-db-secret, Secret (v1) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
Uninstalled plugin: diff
```

- แหล่งที่ไม่ได้เซ็นต้องใส่ `--verify=false` เอง (`PROVENANCE unknown`) — ใช้เฉพาะ plugin ที่เชื่อถือได้และ pin `--version`
- diff ถ้าย้อน tag เป็น 1.7 จะเปลี่ยน label `app.kubernetes.io/version` ของ **ทุก** object (ไม่ใช่แค่ Deployment) เพราะตรายาง labels ใช้ค่า tag — ข้อมูลแบบนี้ช่วยตัดสินใจก่อน upgrade

### ข. umbrella chart: กล่องใหญ่ที่มีกล่องย่อย

```bash
cd labs/labx-extra
helm dependency list harbor-addons
helm dependency update harbor-addons 2>&1 | tail -3
ls harbor-addons harbor-addons/charts
helm dependency list harbor-addons
helm template ha harbor-addons -n kube-system | grep -E "^kind:" | sort | uniq -c
helm template ha harbor-addons -n kube-system --set podinfo.enabled=true | grep -E "^# Source: [a-z-]+/charts/[a-z-]+" -o | sort | uniq -c
helm template ha harbor-addons -n kube-system | grep -- "--kubelet-insecure-tls"
rm -rf harbor-addons/charts harbor-addons/Chart.lock
cd ../..
```

```text
NAME          	VERSION	REPOSITORY                                       	STATUS
metrics-server	3.14.0 	https://kubernetes-sigs.github.io/metrics-server/	missing
podinfo       	6.15.0 	oci://ghcr.io/stefanprodan/charts                	missing

Pulled: ghcr.io/stefanprodan/charts/podinfo:6.15.0
Digest: sha256:ff3d3e14728f75476ed4d43c14f80d52d81d36bc16906843463d464c6146f0d8
Deleting outdated charts
harbor-addons:
Chart.lock
Chart.yaml
charts
values.yaml

harbor-addons/charts:
metrics-server-3.14.0.tgz
podinfo-6.15.0.tgz
NAME          	VERSION	REPOSITORY                                       	STATUS
metrics-server	3.14.0 	https://kubernetes-sigs.github.io/metrics-server/	ok
podinfo       	6.15.0 	oci://ghcr.io/stefanprodan/charts                	ok

      1 kind: APIService
      2 kind: ClusterRole
      2 kind: ClusterRoleBinding
      1 kind: Deployment
      1 kind: RoleBinding
      1 kind: Service
      1 kind: ServiceAccount
      9 # Source: harbor-addons/charts/metrics-server
      5 # Source: harbor-addons/charts/podinfo
            - --kubelet-insecure-tls
```

- `helm dependency update` ดึง subchart จากทั้ง HTTP repo และ OCI (`oci://ghcr.io/...`) มาไว้ใน `charts/` และเขียน `Chart.lock`
- ค่าเริ่มต้น `podinfo.enabled: false` → render ได้เฉพาะ metrics-server 9 object (`condition` ทำงาน) เปิดด้วย `--set podinfo.enabled=true` ได้ object ของ podinfo เพิ่ม 5 ตัว
- ค่าใต้ key `metrics-server:` ใน `values.yaml` ของกล่องใหญ่ไปถึง subchart (`--kubelet-insecure-tls`)
- LAB นี้ render อย่างเดียว **ไม่ติดตั้ง** (metrics-server ตัวจริงจาก LAB 10 ทำงานอยู่แล้ว ติดตั้งซ้ำจะชน)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Error: INSTALLATION FAILED: ... cannot reuse a name that is still in use` | มี release ชื่อนั้นอยู่แล้ว (รวม `failed` หรือ `uninstalled` ที่ keep-history) | `helm list -n <ns>` แล้ว `helm uninstall`, `helm rollback` หรือใช้ `helm upgrade --install` |
| `... exists and cannot be imported into the current release: invalid ownership metadata` | object ชื่อเดียวกันถูกสร้างด้วย `kubectl` (ไม่มีป้าย Helm) | ถ้า selector ตรง: `--take-ownership --force-conflicts` (LAB 12) ถ้าไม่ตรง: ลบของเดิมแล้วติดตั้ง (LAB 10) |
| `conflict occurred while applying object ... conflicts with "kubectl-client-side-apply"` | field มีเจ้าของอื่นถือด้วยค่าต่างกัน (server-side apply) | ตรวจว่าค่าใน chart ถูกแล้วใส่ `--force-conflicts` (ครั้งเดียวพอ) และเลิกแก้ object นั้นด้วย kubectl |
| `spec.selector: Invalid value: ...: field is immutable` | selector ของ chart ต่างจากของเดิม | ลบ Deployment เดิมแล้วติดตั้งใหม่ (มี downtime) — **อย่า uninstall release ที่ adopt ล้ม** |
| `STATUS: deployed` แต่ Pod `ErrImagePull`/`CrashLoopBackOff` | ไม่ได้ใส่ `--wait` (Helm 4 = `hookOnly`) | ใส่ `--wait` (หรือ `--rollback-on-failure`) ทุกครั้ง แล้ว `helm rollback <rel> <rev> --wait` |
| upgrade แล้ว Ingress/ค่าอื่นหาย ได้ 404 | upgrade ส่งแค่ `--set` บางค่า ค่าอื่นกลับค่าเริ่มต้น | ส่ง `-f <ใบสั่ง>` ทุกครั้ง หรือ `--reuse-values` (LAB 3) |
| rollback แล้วร้านกลับไปพัง | `helm rollback <rel>` ไม่ใส่เลข ไปรุ่นก่อนหน้าที่ `failed` | `helm history` แล้ว rollback ระบุเลขรุ่นที่ดี (LAB 4) |
| `--dry-run=server` ผ่านแต่ install จริงล้ม | Helm 4.3 dry-run ไม่ส่ง object ให้ API server validate | `helm template ... \| kubectl apply --dry-run=server -f -` (LAB 6) |
| `yaml: line N: mapping values are not allowed in this context` | ย่อหน้า/`indent`/`{{-` ผิด (N = บรรทัดของผล render) | `helm template --debug` ดู YAML ที่พัง (LAB 6) |
| `function "xxx" not defined` | สะกดฟังก์ชันผิด | ดูรายชื่อฟังก์ชันในเอกสาร Helm/Sprig |
| `execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล` | `helm template` หรือ install ครั้งแรกโดยไม่ใส่รหัส (`lookup` ว่าง) | ใส่ `--set db.password=<รหัส>` (template ใส่ค่าอะไรก็ได้ เช่น `x`) |
| `values don't meet the specifications of the schema(s)` | ใบสั่งผิด schema (เช่น tag 1.4, replicas > 6, key ผิดของ Traefik) | แก้ค่าตามตำแหน่งที่ข้อความบอก (LAB 8) |
| `Error: invalid registry "http://localhost:5000"` | Helm 4 รับแค่ชื่อโฮสต์ | `helm registry login localhost:5000 ...` |
| `basic credential not found` | ยังไม่ login หรือ logout แล้ว | `helm registry login` (LAB 11) |
| `helm pull ... -d pulled`: no such file or directory | โฟลเดอร์ปลายทางยังไม่มี | `mkdir -p pulled` ก่อน |
| `plugin source does not support verification` | Helm 4 ตรวจที่มาของ plugin | ใส่ `--verify=false` เฉพาะ plugin ที่เชื่อถือได้ และ pin `--version` |
| `tree: command not found` | image ไม่มี `tree` | `find <dir> -type f \| sort` |
| `error: you may only specify a single resource type` | `kubectl get job,pod -w` | watch ทีละชนิด เช่น `kubectl get pod -w` |
| `KeyError: 'managedFields'` | `kubectl get -o json` ซ่อน managedFields | เพิ่ม `--show-managed-fields` |
| `kubectl top` ใช้ไม่ได้หลังติดตั้ง metrics-server ด้วย chart | APIService ยัง `False (FailedDiscoveryCheck)` ช่วงแรก | รอ 20–45 วินาที แล้วดู `kubectl get apiservice v1beta1.metrics.k8s.io` |
| สาขา dev ติดตั้งใหม่แล้ว `failed post-install ... som-seed` หรือ `som-web not ready ... Available: 0/1` | ตู้เซฟ (PVC) เดิมใช้รหัสเก่า | `helm upgrade` ด้วยรหัสเดิม หรือ `kubectl delete ns som-dev` แล้วเริ่มใหม่ (ข้อมูลหาย) |
| หลังร้าน `admin.localhost` ได้ 404 | เผลอลบ Middleware `redirect-https` ที่ `som-admin` ใช้ | `kubectl apply` ไฟล์ ingress ของบท 012/013 ที่มี Middleware นี้กลับ หรือย้อนจากสำเนาที่ backup ไว้ |
| เปิด `http://dev.shop.localhost:30080` ใน browser ไม่ได้ | browser ไม่แปลง `*.localhost` | ใช้ Chrome/Edge หรือทางสำรองของบทที่ 12 (แก้ไฟล์ hosts / `curl` ใน k8s-lab) |
| `./hit.sh: Permission denied` | สิทธิ์ execute หายตอนคัดลอก | `bash hit.sh ...` หรือ `chmod +x hit.sh labs/lab06-debug/make-broken.sh` |

## Checklist ส่งงาน

- [ ] ภาพ `helm version` (v4.3.0) และ `helm repo list` 3 แคตตาล็อก (LAB 0–1)
- [ ] ภาพ `helm get metadata` ที่มี `APPLY_METHOD: server-side apply` (LAB 2)
- [ ] ภาพกับดัก upgrade ของ LAB 3 (`replicaCount: 1` อย่างเดียว + `404`) และหลังแก้ด้วย `--reuse-values`
- [ ] ภาพ `helm history hello` ที่เห็น `failed` + `Rollback to N` จาก `--rollback-on-failure` และ `Rollback to 8` จาก rollback ไม่ใส่เลข (LAB 4)
- [ ] ภาพ error 4 แบบของ LAB 6 และผลต่างของ `--dry-run=server` กับ `kubectl apply --dry-run=server`
- [ ] ภาพ schema ปฏิเสธ `web.replicas=9` (LAB 8)
- [ ] ภาพ `helm test som -n som-dev --logs` (Succeeded) และผลถอด release Secret (ตัดรหัสให้สั้น) (LAB 9)
- [ ] ภาพ `helm list -A` ที่มี traefik 41.6.1 และ metrics-server 3.14.0 + ผล `hit.sh` ช่วงย้าย Traefik (LAB 10)
- [ ] ภาพ `Pushed: ... Digest: sha256:...` และ install จาก `oci://` (LAB 11)
- [ ] LAB 12: dev 1 คำสั่ง + test, adopt rev 1 failed → rev 2 deployed + ออเดอร์เดิม, upgrade 1.8 `err=0`, `helm rollback som <เลข>` `err=0`, `helm history`, PVC ค้างหลัง uninstall
- [ ] ภาพหน้าจอ browser ของตัวเอง: สาขา dev (`http://dev.shop.localhost:30080`) และสาขา prod 1.8 (`https://shop.localhost:30081`)
- [ ] ตอบคำถามท้าย LAB 12

## เก็บกวาดหลังจบบท

| สิ่งที่สร้างในบทนี้ | เก็บไว้บทถัดไป? | ลบด้วย |
|---|---|---|
| namespace `helm-demo`, `first`, `som-dev`, `oci-demo` | ไม่ (ลบแล้วใน LAB 4, 6, 12, 11) | `kubectl delete ns <ชื่อ>` |
| release `traefik` (ns `traefik`), `metrics-server` (ns `kube-system`) | **เก็บ** (ประตูและมิเตอร์ของท่าเรือ) | `helm uninstall traefik -n traefik` / `helm uninstall metrics-server -n kube-system` (ร้านจะไม่มีประตู/HPA) |
| release `som` (ns `som-shop`) = ร้านจริง | **เก็บ** | `helm uninstall som -n som-shop` (เหลือ PVC, `som-admin`, Middleware ของบท 012 — ห้ามทำถ้ายังเรียนบทถัดไป) |
| แคตตาล็อก podinfo, traefik, metrics-server | เก็บได้ | `helm repo remove podinfo traefik metrics-server` |
| image `som-shop-web:1.8` | เก็บ | — |
| container `som-registry`, ไฟล์ `.tgz`, `auth/`, `pulled/` | ไม่ (ลบแล้วใน LAB 11) | `docker rm -f som-registry` |
| โฟลเดอร์ที่ LAB สร้าง (`labs/lab01-catalog/traefik`, `labs/lab05-first/mychart`, `labs/lab06-debug/broken-*`) | ไม่ | `rm -rf` (ไม่เข้า git อยู่แล้ว) |
| plugin `diff`, `Chart.lock`/`charts/` ของ harbor-addons (LAB เสริม) | ไม่ (ลบแล้ว) | `helm plugin uninstall diff` |

ปิด container เมื่อเลิกใช้ 🖥️ `docker stop k8s-lab` (คลัสเตอร์ release และร้านรอด restart)

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น เลข revision ชื่อ Pod และจำนวนวินาที) เป็นค่าตัวอย่าง ผู้เรียนควรใช้ผลลัพธ์จากเครื่องตัวเองและเนื้อหาในเอกสารนี้เป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด URL เดียวกับที่นักศึกษาใช้ บนเครื่องทดลองที่จำกัด 4 CPU ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (helm v4.3.0, Kubernetes v1.37.0, kubectl v1.37.1, Traefik chart 41.6.1, metrics-server chart 3.14.0) รหัสผ่านทุกตัว (`passwd`, `meow1234`, `purr5678`, `meow-admin-123`, `meow-registry-123`) เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น
