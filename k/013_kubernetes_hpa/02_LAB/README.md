# LAB บทที่ 13: HorizontalPodAutoscaler (HPA) — หุ่นยนต์ผู้ช่วยเปิด/ปิดบูธตามจำนวนลูกค้า

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ HPA — ติดตั้ง metrics-server v0.9.0 ด้วย static manifest (ลองผิด x509 ก่อน), `kubectl top`, HPA ตัวแรกด้วย `kubectl autoscale` และ YAML `autoscaling/v2`, ยิงโหลดแล้วดู scale up, scale down และ `stabilizationWindowSeconds`, ลืม `requests`, สูตร `desiredReplicas`, `behavior` policies, หลาย metric (CPU + memory), ชนเพดาน ResourceQuota และ Pending, กับดัก `replicas` ใน YAML (`edit-last-applied` / `set-last-applied`) และร้านอาหารแมวน้องส้มวันลดราคาที่หน้าร้านเพิ่ม/ลดบูธเองผ่านประตู Ingress
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ร้านน้องส้มจากบทที่ 12 มีประตูหน้าท่าเรือ (Traefik + Ingress) แล้ว แต่หน้าร้าน `som-web` ยังมี **3 บูธตายตัว** (`replicas: 3`) วันลดราคาลูกค้าล้น บูธไม่พอ วันปกติบูธว่างเปลืองที่ ใน LAB นี้นักศึกษาจะติดตั้ง **เจ้าหน้าที่จดมิเตอร์ (metrics-server)** ให้คลัสเตอร์รู้ว่าแต่ละ Pod เหนื่อยแค่ไหน แล้วเปิดสวิตช์ **หุ่นยนต์ผู้ช่วยผู้จัดการ (HPA)** ที่ดูมิเตอร์ทุก 15 วินาทีและสั่งเพิ่ม/ลดจำนวนบูธเอง เริ่มจากแอปตัวอย่าง `php-apache` ของเอกสารทางการ (LAB 1–10) ฝึกอ่านค่า ทำให้พังทีละแบบ แล้วปิดท้ายด้วย **ร้านน้องส้ม `som-shop-v9`** (image `som-shop-web:1.7`) ที่ลูกค้าจำลองยิงผ่าน `https://shop.localhost:30081` แล้วหน้าร้านขยาย 2 → 6 บูธและกลับเป็น 2 เองโดยลูกค้าไม่เจอ error

### วัตถุประสงค์ของ LAB

เมื่อทำ LAB ครบ นักศึกษาควรสามารถ

1. ติดตั้ง metrics-server v0.9.0 ด้วย static manifest อ่านอาการ x509 บน kind และใช้ `kubectl top` ได้ (LAB 1)
2. สร้าง HPA ด้วย `kubectl autoscale --cpu=50%` และด้วย YAML `autoscaling/v2` แล้วอ่าน TARGETS, Conditions และ Events ได้ (LAB 2)
3. ยิงโหลด ดู scale up/down จับเวลา และอธิบายนาฬิกาทราย (`stabilizationWindowSeconds`) กับ `behavior` policies ได้ (LAB 3, 4, 7)
4. วินิจฉัย `<unknown>` จากการไม่มี requests และคิดสูตร `desiredReplicas` เทียบกับที่ HPA สั่งจริงได้ (LAB 5, 6)
5. อธิบายผลของหลาย metric (memory) และสถานการณ์ที่ HPA สั่งได้แต่ Pod เกิดไม่ได้ (ResourceQuota, Pending) (LAB 8, 9)
6. ย้าย Deployment ที่มี `replicas` ให้ HPA ดูแลโดยบูธไม่ลดเหลือ 1 (`edit-last-applied` / `set-last-applied`) (LAB 10)
7. นำทุกอย่างที่เรียนมาถึงบทที่ 12 + HPA ไปให้ร้านน้องส้มรับวันลดราคาได้เองโดยลูกค้าไม่เจอ error (LAB 11)

### ผลลัพธ์ในเอกสารนี้มาจากไหน

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, kind 3 Node, Kubernetes v1.37.0, kubectl v1.37.1, metrics-server v0.9.0, Traefik v3.7.13) เมื่อ 5 ตุลาคม 2569 **โดยจำกัด container ไว้ที่ 4 CPU / RAM 8 GB (`--cpus=4 --memory=8g`) เพื่อจำลองเครื่องนักศึกษา 4 core** ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod, % CPU, จำนวนขั้นที่ HPA เพิ่ม และจำนวนครั้งที่แต่ละ Pod ตอบ ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** ให้ยึดผลจากเครื่องตัวเอง ส่วน **ลำดับเหตุการณ์และข้อความ (reason, condition, error) ต้องตรง**

**ตัวเลขเวลาและ % CPU ทั้งหมดวัดบนเครื่องที่จำกัด 4 core** ค่าที่แนะนำตามจำนวน core ของเครื่องนักศึกษา

| ค่า | เครื่อง 4 core (ทดสอบจริง) | เครื่อง 8 core ขึ้นไป |
|---|---|---|
| ตัวยิง `load` ใน LAB 3–10 | `1` (ใช้ CPU รวม < 0.6 core) | `1` (เพิ่มเป็น 2 ได้ แต่จำนวนบูธไม่เปลี่ยนเพราะชน `maxReplicas` 6) |
| ลูกค้าจำลอง `customers` ใน LAB 11 | **`1`** (เครื่องใช้ CPU สูงสุดราว 2.6 core จาก 4 หน้าร้านยังขึ้นถึง 6 บูธ) | **`2`** (ทดสอบบนเครื่อง 4 CPU แล้วยัง `err=0` แต่ใช้ CPU ราว 3.3 core จาก 4 บนเครื่อง 8 core จึงเหลือที่) |
| requests หน้าร้าน / `maxReplicas` | `100m` / `6` (ไม่ต้องเปลี่ยน) | `100m` / `6` |
| memory target ใน LAB 8 | `6Mi` | `6Mi` |
| requests ใน LAB 9 ข | สคริปต์คิดให้เอง (4 core → `2400m`) | สคริปต์คิดให้เอง (8 core → `4800m`) |

> **ข้อจำกัดของการจำลองด้วย `--cpus=4`:** การจำกัด CPU ของ container **ไม่ได้ทำให้ Node ของ kind เห็นว่ามี 4 core** Node ยังรายงาน allocatable เป็นจำนวน core จริงของเครื่องทดลอง (`cpu: 32`) ผลที่เห็นในเอกสารจึงต่างจากเครื่องนักศึกษา 2 จุด: (1) คอลัมน์ `CPU(%)` ของ `kubectl top nodes` เป็นแค่ `0%–2%` (เครื่อง 4 core จริงจะสูงกว่านี้) และ (2) LAB 9 ข สคริปต์คำนวณ requests ได้ `19200m` (60% ของ 32 core) ขณะที่เครื่อง 4 core จริงจะได้ `2400m` ส่วน **% ของ HPA (เทียบกับ requests ของ Pod) ไม่ได้รับผลกระทบ**

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox/Safari บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้น `docker cp` (🖥️) และการเปิดร้าน/dashboard ใน browser (🌐) หลาย LAB ใช้ **2 หน้าต่าง** (หน้าต่างหนึ่งดูค่าด้วย `watch-hpa.sh` อีกหน้าต่างสั่งยิงโหลด) ให้เปิด SSH session ที่สองไว้เลย

ร้านน้องส้มยังเปิดผ่านประตู Traefik เหมือนบทที่ 12: 🌐 `http://shop.localhost:30080` (NodePort 30080 ถูกส่งต่อไป HTTPS อัตโนมัติ) → `https://shop.localhost:30081` หลังร้าน `https://admin.localhost:30081` และ dashboard ของ Traefik `http://localhost:30082/dashboard/` (`http://localhost:30080` ที่ไม่มีชื่อร้านจะได้ `404 page not found` ของ Traefik เหมือนบทที่ 12)

### กติกาของ LAB บทนี้

- LAB 0–10 ทำในโฟลเดอร์ **`/workspace/013_kubernetes_hpa/02_LAB`** (คำสั่งอ้างไฟล์แบบ `lab02-first/10-php-apache.yaml`) และ LAB 11 ทำใน **`02_LAB/som-shop-v9`**
- **metrics-server ที่ติดตั้งใน LAB 1 ใช้ต่อจนจบบท** (namespace `kube-system`) LAB 2–10 ใช้ namespace **`hpa-demo`** (แอป + HPA) และ **`hpa-load`** (ตัวยิงโหลด แยก namespace เพื่อไม่ถูกนับใน HPA/ResourceQuota ของแอป) ลบทั้งสองทิ้งท้าย LAB 10
- ทำ LAB **ตามลำดับ** HPA `php-apache` ถูก apply ทับต่อกันตั้งแต่ LAB 2 ถึง LAB 10 และทำบล็อก **"เก็บกวาด"** ท้ายแต่ละ LAB ทุกครั้ง
- **ไม่ใช้ Helm** ทุกอย่างติดตั้งด้วยไฟล์ YAML ในโฟลเดอร์บท (Helm เป็นบทถัดไป ส่วน VPA, Cluster Autoscaler และ KEDA เรียนเป็นทฤษฎี)
- รหัสผ่านทุกตัวเป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง: SSH `passwd`, ฐานข้อมูล `meow1234` (บทที่ 11 หรือ `purr5678` ถ้าเปลี่ยนรหัสใน LAB บทที่ 11), บัตรหลังร้าน `som` / `meow-admin-123` (บทที่ 12) บทนี้ไม่สร้างหรือแก้ Secret ของร้าน (ยกเว้นทางคลัสเตอร์ใหม่ใน LAB 11) และไฟล์ `tls.key`/`tls.crt` ห้าม commit ลง git (`.gitignore` กันไว้แล้ว)
- **`--kubelet-insecure-tls` ใน `00-metrics-server.yaml` ใช้เฉพาะ LAB** (kind ออกใบรับรอง kubelet แบบ self-signed) ระบบจริงต้องใช้ใบที่ CA ของคลัสเตอร์เซ็น
- **behavior ของ HPA ใน LAB ย่อเวลารอให้สั้น** (ลดบูธหลัง 30–60 วินาที) ค่าเริ่มต้นจริงคือ 300 วินาที (LAB 4 วัดให้ดู)
- image `registry.k8s.io/metrics-server/metrics-server:v0.9.0`, `registry.k8s.io/hpa-example`, `busybox:1.36`, `curlimages/curl:8.22.0` **Node ดึงเองตอนใช้** (ต้องมีอินเทอร์เน็ต) ส่วน `som-shop-web:1.7` ต้อง build + `kind load` ใน LAB 0
- **อย่าเปิดตัวยิงโหลดค้างไว้** เลิกทำ LAB เมื่อไรให้ `--replicas=0` (ตัวยิง `load` และ `customers`) เครื่องจะได้ไม่ร้อน/หน่วง

### เครื่อง ARM (Mac Apple Silicon) — ทางสำรอง

`registry.k8s.io/hpa-example` มี tag เดียว (`latest`) และเป็น **amd64 อย่างเดียว** บน Node ARM จึงดึงไม่ได้ (คาดว่าจะเห็น `ErrImagePull` หรือข้อความทำนอง `no match for platform in manifest`) ตรวจสถาปัตยกรรมใน LAB 0 ขั้นที่ 3 ถ้าได้ `arm64` ให้ใช้ไฟล์ชุด **`-arm`** ซึ่งใช้ `som-shop-web:1.7` ที่ build เองใน LAB 0 (build บนเครื่องตัวเองจึงได้สถาปัตยกรรมตรงกับ Node; endpoint `/api/work?ms=20` หมุน CPU 20 ms ต่อ request ไม่ต้องมีฐานข้อมูล, readiness ใช้ `/api/live`) ชื่อ Deployment/Service/container ยังเป็น `php-apache` **คำสั่งอื่นทุกบรรทัดเหมือนเดิม**

| LAB | ไฟล์หลัก (amd64) | ไฟล์แทน (ARM) |
|---|---|---|
| 2 | `lab02-first/10-php-apache.yaml` | `lab02-first/10-php-apache-arm.yaml` |
| 3–10 (ตัวยิง) | `lab03-load/30-load.yaml` | `lab03-load/30-load-arm.yaml` |
| 5 | `lab05-norequests/50-no-requests.yaml` | `lab05-norequests/50-no-requests-arm.yaml` |
| 10 | `lab02-first/10-php-apache.yaml` และ `lab10-replicas/10-php-apache-hpa.yaml` | `lab02-first/10-php-apache-arm.yaml` และไฟล์ที่สร้างเองด้วย `sed '/^  replicas:/d' lab02-first/10-php-apache-arm.yaml > lab10-replicas/10-php-apache-hpa-arm.yaml` |

> **สถานะการทดสอบ:** ไฟล์ชุด `-arm` ทดสอบจริงแล้วกับ LAB 2, 3 และ 5 **บนเครื่อง amd64** (ใช้ไฟล์ `-arm` แทนไฟล์หลัก) **ยังไม่ได้ลองบนเครื่อง ARM จริง** ผลใกล้เคียงไฟล์หลัก: `/api/work` ตอบ `php-apache-5d4955d4ff-sk2xt 1.7 work=20ms`, ยิงโหลดแล้ว **1 → 4 → 6** (Ready 6 ราว 60 วินาที) ที่ 6 Pod เฉลี่ย ~92% และ LAB 5 ได้ `missing request for cpu in container php-apache` เหมือนกัน ข้อต่าง: แอป Node.js ใช้หน่วยความจำ ~45–52Mi ต่อ Pod (php-apache ~8–11Mi) ใน LAB 8 memory จึงชนะ CPU ชัดกว่าเดิม ถ้าเจอปัญหาบนเครื่อง ARM ให้แจ้งผู้สอน

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์และ image 1.7](#lab-0-เตรียมคลัสเตอร์และ-image-17) | 10–15 นาที | ⭐ |
| 1 | [ติดตั้ง metrics-server](#lab-1-ติดตั้ง-metrics-server) | 10 นาที | ⭐⭐ |
| 2 | [HPA ตัวแรก](#lab-2-hpa-ตัวแรก) | 10 นาที | ⭐⭐ |
| 3 | [ยิงโหลด แล้วดู scale up](#lab-3-ยิงโหลด-แล้วดู-scale-up) | 10 นาที | ⭐⭐ |
| 4 | [scale down และนาฬิกาทราย](#lab-4-scale-down-และนาฬิกาทราย) | 15 นาที | ⭐⭐⭐ |
| 5 | [ลืม requests](#lab-5-ลืม-requests) | 5 นาที | ⭐⭐ |
| 6 | [คิดตามสูตร desiredReplicas](#lab-6-คิดตามสูตร-desiredreplicas) | 10 นาที | ⭐⭐⭐ |
| 7 | [behavior: เพิ่มทีละ 1 บูธ](#lab-7-behavior-เพิ่มทีละ-1-บูธ) | 10 นาที | ⭐⭐⭐ |
| 8 | [หลาย metric: CPU + memory](#lab-8-หลาย-metric-cpu--memory) | 10 นาที | ⭐⭐⭐ |
| 9 | [ชนเพดาน: ResourceQuota และ Pending](#lab-9-ชนเพดาน-resourcequota-และ-pending) | 15 นาที | ⭐⭐⭐⭐ |
| 10 | [กับดัก replicas ใน YAML](#lab-10-กับดัก-replicas-ใน-yaml) | 15 นาที | ⭐⭐⭐⭐ |
| 11 | [LAB สุดท้าย: ร้านน้องส้มวันลดราคา](#lab-11-lab-สุดท้าย-ร้านน้องส้มวันลดราคา) | 40–50 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (ส่วนใหญ่เป็นเวลารอ HPA) ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านทฤษฎี: LAB 1 → หัวข้อ 4, LAB 2 → หัวข้อ 5, LAB 3–4 → หัวข้อ 5 และ 8, LAB 5 → หัวข้อ 6, LAB 6 → หัวข้อ 7, LAB 7 → หัวข้อ 8, LAB 8–10 → หัวข้อ 9, LAB 11 → หัวข้อ 9–10

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 1 ติดตั้ง metrics-server](#fig-1) | 18 | [ขั้น A แอป 1.7](#fig-18) |
| 2 | [LAB 1 ลองผิด x509](#fig-2) | 19 | [ขั้น B HPA และย้าย replicas](#fig-19) |
| 3 | [ผล LAB 1 kubectl top](#fig-3) | 20 | [ภาพหน้าจอจริง หน้าร้าน 1.7 ก่อนวันลดราคา 2 บูธ](#fig-20) |
| 4 | [LAB 2 HPA ตัวแรก](#fig-4) | 21 | [ขั้น C ลูกค้าจำลอง](#fig-21) |
| 5 | [ผล LAB 2](#fig-5) | 22 | [ขั้น D scale up](#fig-22) |
| 6 | [LAB 3 ยิงโหลด](#fig-6) | 23 | [ขั้น E ชื่อ Pod บนหน้าเว็บ](#fig-23) |
| 7 | [ผล LAB 3 scale up](#fig-7) | 24 | [ภาพหน้าจอจริง หน้าร้านระหว่างวันลดราคา 6 บูธ](#fig-24) |
| 8 | [LAB 4 scale down](#fig-8) | 25 | [ขั้น F Traefik dashboard](#fig-25) |
| 9 | [ผล LAB 4](#fig-9) | 26 | [ภาพหน้าจอจริง Traefik dashboard 2 servers](#fig-26) |
| 10 | [LAB 5 ลืม requests](#fig-10) | 27 | [ภาพหน้าจอจริง Traefik dashboard 6 servers](#fig-27) |
| 11 | [LAB 6 สูตร](#fig-11) | 28 | [ขั้น G ไม่มี error](#fig-28) |
| 12 | [LAB 7 behavior](#fig-12) | 29 | [ขั้น H scale down](#fig-29) |
| 13 | [LAB 8 หลาย metric](#fig-13) | 30 | [ภาพหน้าจอจริง Traefik dashboard กลับเป็น 2 servers](#fig-30) |
| 14 | [LAB 9 ก ResourceQuota](#fig-14) | 31 | [ขั้น I ครัวคงเดิม](#fig-31) |
| 15 | [LAB 9 ข Pending](#fig-15) | 32 | [ตรวจรับวันลดราคา](#fig-32) |
| 16 | [LAB 10 กับดัก replicas](#fig-16) | 33 | [ปิดบท](#fig-33) |
| 17 | [LAB 11 ภาพรวมวันลดราคา](#fig-17) |  | |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── .gitignore                         ← กัน *.key, *.crt
├── images/                            ← ภาพประกอบ 01–28 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของ LAB 11 จำนวน 5 ภาพ
├── watch-hpa.sh                       ← พิมพ์ "วินาที  TARGETS  replicas=(ที่ HPA สั่ง)  ready=(Pod พร้อมจริง)" ทุก 5 วินาที
├── metrics-server/
│   ├── components-v0.9.0.yaml         (ต้นฉบับจาก release v0.9.0 ไม่แก้ — LAB 1 ลองผิด)
│   └── 00-metrics-server.yaml         (ต้นฉบับ + --kubelet-insecure-tls 1 บรรทัด)
├── ingress-controller/                ← Traefik v3.7.13 สำเนาจากบทที่ 12 (ใช้เฉพาะคลัสเตอร์ใหม่ใน LAB 11)
├── lab02-first/{10-php-apache.yaml,10-php-apache-arm.yaml,20-hpa-php.yaml}   (แอป + HPA แบบ YAML)
├── lab03-load/{30-load.yaml,30-load-arm.yaml}                                 (ตัวยิงโหลด busybox wget -T 2)
├── lab04-scaledown/40-hpa-fast-down.yaml                                      (scaleDown window 30 วินาที)
├── lab05-norequests/{50-no-requests.yaml,50-no-requests-arm.yaml}             (Deployment ไม่มี requests + HPA)
├── lab06-formula/formula.sh                                                   (คิดสูตรเทียบกับ HPA)
├── lab07-behavior/70-hpa-slow-up.yaml                                         (scaleUp Pods 1 ต่อ 15 วินาที)
├── lab08-multi/80-hpa-multi.yaml                                              (cpu 50% + memory 6Mi)
├── lab09-limits/{90-quota.yaml,big-requests.sh}                               (ResourceQuota + requests 60% ของ Node)
├── lab10-replicas/10-php-apache-hpa.yaml                                      (php-apache ที่ลบ replicas แล้ว)
└── som-shop-v9/                       ← LAB 11 ร้านน้องส้มวันลดราคา
    ├── app/                           ← แอป Next.js 1.7 = 1.6 + app/api/work/route.ts (build เป็น som-shop-web:1.7)
    ├── k8s/
    │   ├── 00-namespace.yaml, 10-db.yaml, 40-admin.yaml, 50-ingress.yaml   (เหมือนบทที่ 12)
    │   ├── 15-config.yaml             (ป้ายร้านบทที่ 13: "⚓ ท่าเรือ Kubernetes · HPA" + แถบโปรโมชันวันลดราคา)
    │   ├── 20-web.yaml                (image 1.7, ไม่มี replicas แล้ว)
    │   ├── 60-hpa.yaml                (HPA som-web min 2 max 6 cpu 50% + behavior)
    │   └── 70-customers.yaml          (ลูกค้าจำลอง curlimages/curl ยิงผ่าน Traefik HTTPS เริ่ม replicas 0)
    ├── .gitignore                     ← กัน secret.yaml, *.key, *.crt
    └── hit.sh                         ← ยิง HTTPS ผ่าน Ingress แล้วนับ ok/err (เหมือนบทที่ 12)
```

---

## LAB 0: เตรียมคลัสเตอร์และ image 1.7

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` ตรวจคลัสเตอร์และสถาปัตยกรรมของ Node ดูสภาพร้านท้ายบทที่ 12 และ build `som-shop-web:1.7` ไว้ใช้ใน LAB 11 (และทางสำรอง ARM)

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md)–[12](../../012_kubernetes_ingress/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `013_kubernetes_hpa` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (ถ้า `Exited` ให้ `docker start k8s-lab`) แล้ว `cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `013_kubernetes_hpa` อยู่ข้างใน**

```bash
docker ps -a --filter name=k8s-lab
docker cp 013_kubernetes_hpa k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ถ้าแก้ไฟล์บนเครื่องภายหลังต้องสั่งซ้ำ บทนี้มีแอปร้านและ manifest ทุกไฟล์ของตัวเอง **ไม่ต้องมีโฟลเดอร์ของบทก่อนใน container**

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** (เปิด 2 หน้าต่างไว้เลย)

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` เมื่อสำเร็จจะเห็น prompt `root@k8s-lab`

### ขั้นที่ 3: ตรวจคลัสเตอร์ สถาปัตยกรรม และร้านท้ายบทที่ 12

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/013_kubernetes_hpa/02_LAB
ls
kubectl get nodes
kubectl get node -o jsonpath='{range .items[*]}{.metadata.name} {.status.nodeInfo.architecture}{"\n"}{end}'
```

```text
images
ingress-controller
lab02-first
lab03-load
lab04-scaledown
lab05-norequests
lab06-formula
lab07-behavior
lab08-multi
lab09-limits
lab10-replicas
metrics-server
som-shop-v9
watch-hpa.sh
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   7m57s   v1.37.0
lab-worker          Ready    <none>          7m43s   v1.37.0
lab-worker2         Ready    <none>          7m43s   v1.37.0
lab-control-plane amd64
lab-worker amd64
lab-worker2 amd64
```

| ผล | ทำอย่างไร |
|---|---|
| 3 Node `Ready` และ `amd64` | ใช้ไฟล์หลักทุก LAB |
| 3 Node `Ready` และ `arm64` | ใช้ไฟล์ชุด `-arm` ตาม [ตารางทางสำรอง](#เครื่อง-arm-mac-apple-silicon--ทางสำรอง) |
| error / ไม่มีคลัสเตอร์ | `k8s-up` (ราว 55 วินาที) แล้วทำต่อ — ร้านจะไม่มี ให้ใช้ทาง "คลัสเตอร์ใหม่" ใน LAB 11 ขั้น 0 |

ดูสภาพร้านท้ายบทที่ 12 (ร้านใช้ต่อใน LAB 11)

```bash
kubectl -n som-shop get deploy,sts,hpa
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.replicas} {.spec.template.spec.containers[0].image}{"\n"}'
kubectl top nodes
```

```text
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-admin   1/1     1            1           5m30s
deployment.apps/som-web     3/3     3            3           5m30s

NAME                      READY   AGE
statefulset.apps/som-db   1/1     5m30s
3 som-shop-web:1.6
error: Metrics API not available
```

หน้าร้าน 3 บูธ รุ่น 1.6 (จากขั้น E บทที่ 12) ยังไม่มี HPA และ `kubectl top` ยังใช้ไม่ได้ (คลัสเตอร์ยังไม่มีเจ้าหน้าที่จดมิเตอร์ — LAB 1)

### ขั้นที่ 4: build som-shop-web:1.7

1.7 คือโค้ดชุดเดียวกับ 1.6 + endpoint ใหม่ `GET /api/work?ms=N` (หมุน CPU `N` มิลลิวินาทีต่อ request จำกัด 0–200 ไม่แตะฐานข้อมูล) ใช้สร้างโหลดให้ HPA เห็นใน LAB 11

```bash
cat som-shop-v9/app/app/api/work/route.ts | sed -n '5,10p'
cd som-shop-v9
time (docker build -q -t som-shop-web:1.7 --build-arg APP_VERSION=1.7 app && kind load docker-image som-shop-web:1.7 --name lab)
cd ..
```

```text
sha256:773ddb3f0d8a754697fcaac23dd9e0f41c0db3ba8a3034a647ef88c0f5336575
Image: "som-shop-web:1.7" with ID "sha256:773ddb3f..." not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.7" with ID "sha256:773ddb3f..." not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.7" with ID "sha256:773ddb3f..." not yet present on node "lab-control-plane", loading...

real	0m31.215s
```

build บนเครื่องทดลอง (4 CPU, มี cache ของ node_modules จากบทที่ 12 บางส่วน) ใช้ราว 31 วินาที เครื่องนักศึกษาอาจนานกว่านี้ (build ครั้งแรกไม่มี cache ราว 40 วินาทีบน 4 CPU) ตรวจผล

```bash
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
docker run --rm som-shop-web:1.7 node -e 'console.log(process.env.APP_VERSION)'
```

```text
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  b2db208b1d65b       76.7MB
docker.io/library/som-shop-web                  1.6                  bb578956a889f       76.7MB
docker.io/library/som-shop-web                  1.7                  99bcf0004b378       76.7MB
== lab-worker2
...
1.7
```

> **ห้าม tag เป็น `som-shop-web:1.4` หรือ build ทับ 1.5/1.6** ให้ใช้ tag `1.7` ตามเอกสาร (Pod เดิมของร้านยังใช้ 1.6 จนถึง LAB 11 ขั้น B)

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node `Ready` รู้สถาปัตยกรรมของ Node แล้ว (`amd64` หรือ `arm64`)
- ร้านท้ายบทที่ 12: `som-web` 3/3 รุ่น 1.6, `som-db` 1/1
- `som-shop-web:1.7` อยู่บนทุก Node

**คำถามชวนคิด**

1. ทำไมต้องตรวจสถาปัตยกรรมของ Node ก่อนเริ่ม LAB ที่ใช้ image จาก registry ภายนอก
2. image `som-shop-web:1.7` ที่ build ในเครื่อง k8s-lab ไปอยู่ใน Node ได้อย่างไร ทำไม Node ไม่ไปดึงจากอินเทอร์เน็ต

**เก็บกวาด:** ไม่มี — image `som-shop-web:1.7` ใช้ต่อใน LAB 11 (และทางสำรอง ARM) ร้านท้ายบทที่ 12 ห้ามลบ

---

## LAB 1: ติดตั้ง metrics-server

<p align="center" id="fig-1">
  <img src="images/01-lab1-open.png" alt="รูปที่ 1 LAB 1 ติดตั้ง metrics-server" width="900"><br>
  <em><b>รูปที่ 1</b> LAB 1 เปิด: ก่อนติดตั้ง kubectl top ได้ error: Metrics API not available → apply 00-metrics-server.yaml (v0.9.0 + --kubelet-insecure-tls) แล้วดูกระดานความเหนื่อย</em>
</p>

**เป้าหมาย:** ติดตั้ง **เจ้าหน้าที่จดมิเตอร์ (metrics-server v0.9.0)** ด้วย static manifest ลองไฟล์ต้นฉบับก่อนเพื่อเห็นอาการ x509 บน kind แล้วแก้ด้วยไฟล์ของบท จากนั้นใช้ `kubectl top`

**ไฟล์:** `metrics-server/components-v0.9.0.yaml` (ต้นฉบับจาก [release v0.9.0](https://github.com/kubernetes-sigs/metrics-server/releases/tag/v0.9.0)), `metrics-server/00-metrics-server.yaml`

**ทำไมเป็น metrics-server v0.9.0 และ `--kubelet-insecure-tls`** (ข้อมูล ณ วันทำ LAB)

| เรื่อง | ข้อมูล | แหล่งอ้างอิง |
|---|---|---|
| รุ่น | **v0.9.0** ออก 13 ก.ค. 2026 (รุ่นล่าสุด) image `registry.k8s.io/metrics-server/metrics-server:v0.9.0` | [GitHub releases](https://github.com/kubernetes-sigs/metrics-server/releases) |
| รองรับ Kubernetes | ตาราง compatibility: `0.9.x` ↔ `metrics.k8s.io/v1beta1` ↔ Kubernetes `1.34+` (คลัสเตอร์ของเรา v1.37.0) | [README ของ metrics-server](https://github.com/kubernetes-sigs/metrics-server) |
| ไฟล์ติดตั้ง | `components.yaml` ของ release v0.9.0 (args เดิม: `--cert-dir=/tmp`, `--secure-port=10250`, `--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname`, `--kubelet-use-node-status-port`, `--metric-resolution=15s`) | [components.yaml v0.9.0](https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.9.0/components.yaml) |
| ใบรับรอง kubelet | README กำหนดว่า *"Kubelet certificate needs to be signed by cluster Certificate Authority (or disable certificate validation by passing `--kubelet-insecure-tls` to Metrics Server)"* — kind ออกใบ kubelet แบบ self-signed ที่ไม่มี IP ใน SAN จึงต้องใช้ทางในวงเล็บ | [README ของ metrics-server](https://github.com/kubernetes-sigs/metrics-server) |
| ขอบเขต | **`--kubelet-insecure-tls` ใช้เฉพาะ LAB ห้ามใช้ production** (ปิดการตรวจว่าคุยกับ kubelet ตัวจริง) ระบบจริงให้ kubelet ใช้ใบที่ CA ของคลัสเตอร์เซ็น | [ทฤษฎีหัวข้อ 4.4](../01_Theory/README.md#44-metrics-server-บน-kind-และ---kubelet-insecure-tls) |

ไม่ใช้ Helm chart ของ metrics-server (Helm เป็นบทถัดไป) และไม่ต้องแก้ `--kubelet-preferred-address-types` (InternalIP ใช้ได้บน kind)

### ขั้นที่ 1: ก่อนติดตั้ง

```bash
kubectl top nodes; kubectl get --raw /apis/metrics.k8s.io; kubectl get apiservice | grep metrics || echo "ไม่มี APIService metrics"
```

```text
error: Metrics API not available
Error from server (NotFound): the server could not find the requested resource
ไม่มี APIService metrics
```

Kubernetes ไม่ได้มี metrics-server มาให้ `kubectl top` และ HPA แบบ CPU/memory ถามค่าจาก API กลุ่ม `metrics.k8s.io` ซึ่งยังไม่มีใครให้บริการ

### ขั้นที่ 2: ลองผิด — ไฟล์ต้นฉบับบน kind

<p align="center" id="fig-2">
  <img src="images/02-lab1-x509-trap.png" alt="รูปที่ 2 LAB 1 ลองผิด x509" width="900"><br>
  <em><b>รูปที่ 2</b> LAB 1 ลองผิด: ใช้ components.yaml ต้นฉบับ → Pod 0/1 Running, readiness 500, log: x509: cannot validate certificate ... doesn't contain any IP SANs, APIService False (MissingEndpoints)</em>
</p>

ดูความต่างของสองไฟล์ก่อน

```bash
diff metrics-server/components-v0.9.0.yaml metrics-server/00-metrics-server.yaml
```

```text
0a1,3
> # metrics-server v0.9.0 (registry.k8s.io/metrics-server/metrics-server:v0.9.0) = components.yaml ทางการ
> # https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.9.0/components.yaml
> # แก้ 1 บรรทัด: เพิ่ม --kubelet-insecure-tls (kind ออกใบรับรอง kubelet แบบ self-signed ไม่มี IP SAN)
140a144
>         - --kubelet-insecure-tls              # kind: ใบรับรอง kubelet ไม่มี IP SAN (เฉพาะ LAB ห้ามใช้ production)
```

ติดตั้งต้นฉบับ รอ 1 นาที แล้วดูอาการ

```bash
kubectl apply -f metrics-server/components-v0.9.0.yaml
sleep 60; kubectl -n kube-system get pod -l k8s-app=metrics-server; kubectl get apiservice v1beta1.metrics.k8s.io; kubectl top nodes
kubectl -n kube-system logs deploy/metrics-server --tail=4
kubectl -n kube-system describe pod -l k8s-app=metrics-server | grep -E "Readiness probe failed|Successfully pulled"
```

```text
serviceaccount/metrics-server created
...
deployment.apps/metrics-server created
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io created
NAME                              READY   STATUS    RESTARTS   AGE
metrics-server-6bcd67b6cf-rcvm8   0/1     Running   0          61s
NAME                     SERVICE                      AVAILABLE                  AGE
v1beta1.metrics.k8s.io   kube-system/metrics-server   False (MissingEndpoints)   61s
error: Metrics API not available
E1005 15:40:39.286511       1 scraper.go:149] "Failed to scrape node" err="Get \"https://172.19.0.4:10250/metrics/resource\": tls: failed to verify certificate: x509: cannot validate certificate for 172.19.0.4 because it doesn't contain any IP SANs" node="lab-worker2"
E1005 15:40:39.293135       1 scraper.go:149] "Failed to scrape node" err="Get \"https://172.19.0.3:10250/metrics/resource\": ... doesn't contain any IP SANs" node="lab-control-plane"
E1005 15:40:39.294594       1 scraper.go:149] "Failed to scrape node" err="Get \"https://172.19.0.2:10250/metrics/resource\": ... doesn't contain any IP SANs" node="lab-worker"
I1005 15:40:44.816814       1 server.go:192] "Failed probe" probe="metric-storage-ready" err="no metrics to serve"
  Normal   Pulled     57s               kubelet            spec.containers{metrics-server}: Successfully pulled image "registry.k8s.io/metrics-server/metrics-server:v0.9.0" in 3.484s (3.484s including waiting). Image size: 23258428 bytes.
  Warning  Unhealthy  6s (x4 over 36s)  kubelet            spec.containers{metrics-server}: Readiness probe failed: HTTP probe failed with statuscode: 500
```

อ่านอาการ: metrics-server ไปขอค่าจาก kubelet ทุก Node ทาง HTTPS ที่ IP ของ Node (`InternalIP`) แต่ใบรับรองของ kubelet ใน kind เป็น self-signed **ไม่มี IP อยู่ใน SAN** จึงตรวจใบไม่ผ่าน → ไม่มีค่าเลย (`no metrics to serve`) → readiness 500 → Pod `0/1` → Service ไม่มี endpoint → APIService `False (MissingEndpoints)` → `kubectl top` ยังพัง (image ดึงตรงจาก `registry.k8s.io` ได้ใน ~3.5 วินาที **ไม่ต้อง `kind load`**)

### ขั้นที่ 3: แก้ด้วยไฟล์ของบท

apply ไฟล์ของบท **ทับได้เลย** (ชื่อ object เดียวกัน) แล้วจับเวลา

```bash
kubectl apply -f metrics-server/00-metrics-server.yaml
t0=$(date +%s); kubectl -n kube-system rollout status deploy/metrics-server --timeout=120s; echo "rollout $(( $(date +%s)-t0 )) วิ"
until kubectl top nodes >/dev/null 2>&1; do sleep 2; done; echo "kubectl top ใช้ได้หลัง apply $(( $(date +%s)-t0 )) วิ"
kubectl get apiservice v1beta1.metrics.k8s.io
```

```text
serviceaccount/metrics-server unchanged
...
deployment.apps/metrics-server configured
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io unchanged
Waiting for deployment "metrics-server" rollout to finish: 1 old replicas are pending termination...
deployment "metrics-server" successfully rolled out
rollout 24 วิ
kubectl top ใช้ได้หลัง apply 30 วิ
NAME                     SERVICE                      AVAILABLE   AGE
v1beta1.metrics.k8s.io   kube-system/metrics-server   True        115s
```

มีแค่ Deployment ที่ `configured` (เพิ่ม arg 1 บรรทัด) rollout ราว 24 วินาที (readiness `initialDelaySeconds: 20`) และ `kubectl top` ใช้ได้ราว 30 วินาทีหลัง apply

### ขั้นที่ 4: กระดานความเหนื่อย

<p align="center" id="fig-3">
  <img src="images/03-lab1-top-result.png" alt="รูปที่ 3 ผล LAB 1 kubectl top" width="900"><br>
  <em><b>รูปที่ 3</b> ผล LAB 1: image ดึงจาก registry.k8s.io ตรง (3 วิ) ไม่ต้อง kind load, rollout ~25 วิ, kubectl top ใช้ได้ ~30 วิหลัง apply, APIService AVAILABLE True</em>
</p>

```bash
kubectl top nodes
kubectl top pods -A --sort-by=cpu | head -12
kubectl api-resources --api-group=metrics.k8s.io
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes/lab-worker | head -c 400; echo
```

```text
NAME                CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
lab-control-plane   121m         0%       990Mi           1%
lab-worker          48m          0%       441Mi           0%
lab-worker2         38m          0%       522Mi           0%
NAMESPACE            NAME                                        CPU(cores)   MEMORY(bytes)
kube-system          kube-apiserver-lab-control-plane            39m          304Mi
kube-system          etcd-lab-control-plane                      22m          56Mi
kube-system          kube-controller-manager-lab-control-plane   15m          63Mi
som-shop             som-db-0                                    7m           45Mi
kube-system          kube-scheduler-lab-control-plane            6m           29Mi
kube-system          metrics-server-84c99cb944-t9m4p             2m           17Mi
kube-system          coredns-559f6c778d-wr4b4                    2m           15Mi
som-shop             som-web-796c88558c-xmg2b                    2m           43Mi
som-shop             som-web-796c88558c-mrv6h                    2m           43Mi
som-shop             som-web-796c88558c-lk9rt                    2m           42Mi
...
NAME    SHORTNAMES   APIVERSION               NAMESPACED   KIND
nodes                metrics.k8s.io/v1beta1   false        NodeMetrics
pods                 metrics.k8s.io/v1beta1   true         PodMetrics
{"kind":"NodeMetrics","apiVersion":"metrics.k8s.io/v1beta1","metadata":{"name":"lab-worker",...},"timestamp":"2026-10-05T15:41:27Z","window":"10.016s","usage":{"cpu":"47397663n","memory":"45...
```

- หน่วย `m` = millicore (1000m = 1 core), `Mi` = mebibyte ค่าที่เห็นคือ **ค่าล่าสุดเท่านั้น** (metrics-server จดทุก 15 วินาที ไม่เก็บย้อนหลัง — ต้องการกราฟย้อนหลังใช้ Prometheus)
- หน้าร้าน 3 บูธใช้ CPU แค่ ~2m ต่อบูธ (ไม่มีลูกค้า) — วันปกติ 3 บูธจึงเกินความจำเป็น
- `CPU(%)` ของ Node เทียบกับ allocatable ของ Node (ดูหมายเหตุในบทนำเรื่องเครื่องทดลอง)

### สิ่งที่เห็น

- ต้นฉบับบน kind: `0/1 Running`, `x509 ... doesn't contain any IP SANs`, `False (MissingEndpoints)`
- ไฟล์ของบท: `AVAILABLE True`, `kubectl top nodes/pods` ใช้ได้ใน ~30 วินาที

**คำถามชวนคิด**

1. ทำไมการแก้ที่ถูกต้องในระบบจริงไม่ใช่ `--kubelet-insecure-tls` และควรแก้ที่ใคร
2. ถ้า metrics-server ล่ม HPA ที่มีอยู่จะทำอะไร (ดูคำตอบได้จาก LAB 2 ตอนที่ TARGETS เป็น `<unknown>`)

**เก็บกวาด:** **ไม่ลบ metrics-server** ใช้ต่อทุก LAB จนจบบท (ถ้าอยากลองต้นฉบับซ้ำ ให้ `kubectl apply -f metrics-server/00-metrics-server.yaml` กลับทุกครั้ง)

---

## LAB 2: HPA ตัวแรก

<p align="center" id="fig-4">
  <img src="images/04-lab2-open.png" alt="รูปที่ 4 LAB 2 HPA ตัวแรก" width="900"><br>
  <em><b>รูปที่ 4</b> LAB 2 เปิด: แอปตัวอย่าง php-apache (registry.k8s.io/hpa-example, requests cpu 100m) + kubectl autoscale --cpu=50% --min=1 --max=6</em>
</p>

**เป้าหมาย:** สร้างแอป `php-apache` (ทุก request วนคิด `sqrt` 1 ล้านรอบ) แล้วเปิด HPA ตัวแรกด้วยคำสั่ง `kubectl autoscale` อ่านผลและเทียบกับ YAML `autoscaling/v2`

**ไฟล์:** `lab02-first/10-php-apache.yaml` (namespace `hpa-demo` + Deployment `replicas: 1` requests cpu `100m` limits `300m` + Service), `lab02-first/20-hpa-php.yaml` (ARM: `10-php-apache-arm.yaml`)

### ขั้นที่ 1: แอป

```bash
kubectl apply -f lab02-first/10-php-apache.yaml
t0=$(date +%s); kubectl -n hpa-demo rollout status deploy/php-apache --timeout=180s; echo "พร้อมใน $(( $(date +%s)-t0 )) วิ"
kubectl -n hpa-demo describe pod -l app=php-apache | grep "Successfully pulled"
```

```text
namespace/hpa-demo created
deployment.apps/php-apache created
service/php-apache created
Waiting for deployment "php-apache" rollout to finish: 0 of 1 updated replicas are available...
deployment "php-apache" successfully rolled out
พร้อมใน 11 วิ
  Normal  Pulled     0s    kubelet            spec.containers{php-apache}: Successfully pulled image "registry.k8s.io/hpa-example" in 10.357s (10.357s including waiting). Image size: 164030864 bytes.
```

image 164 MB Node ดึงเอง (เครื่องทดลอง ~10 วินาที เครื่องที่เน็ตช้าอาจ 20–60 วินาที)

### ขั้นที่ 2: kubectl autoscale

```bash
kubectl -n hpa-demo autoscale deployment php-apache --cpu=50% --min=1 --max=6
kubectl -n hpa-demo get hpa
sleep 20; kubectl -n hpa-demo get hpa
kubectl -n hpa-demo describe hpa php-apache | grep -A3 -E "^Events|FailedGet" | head -8
```

```text
horizontalpodautoscaler.autoscaling/php-apache autoscaled
NAME         REFERENCE               TARGETS              MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: <unknown>/50%   1         6         1          0s
NAME         REFERENCE               TARGETS              MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: <unknown>/50%   1         6         1          20s
  ScalingActive  False   FailedGetResourceMetric  the HPA was unable to compute the replica count: failed to get cpu utilization: did not receive metrics for targeted pods (pods might be unready)
Events:
  Type     Reason                        Age   From                       Message
  ----     ------                        ----  ----                       -------
  Warning  FailedGetResourceMetric       21s   horizontal-pod-autoscaler  failed to get cpu utilization: unable to get metrics for resource cpu: no metrics returned from resource metrics API
```

- kubectl 1.37 ใช้ `--cpu=50%` (ไม่มี `--cpu-percent` แล้ว) ผลคือ HPA ชื่อเดียวกับ Deployment
- **`<unknown>` ช่วงแรกเป็นเรื่องปกติ** Pod เพิ่งเกิด metrics-server ยังไม่มีค่าของ Pod นี้ (จดทุก 15 วินาที) Event `FailedGetResourceMetric` ช่วงแรกไม่ต้องตกใจ ในการทดลองได้ตัวเลขหลังสร้าง HPA ~30 วินาที (Pod อายุ ~40 วินาที)

```bash
until kubectl -n hpa-demo get hpa php-apache --no-headers | grep -q "cpu: [0-9]"; do sleep 3; done
kubectl -n hpa-demo get hpa; kubectl top pod -n hpa-demo
```

```text
NAME         REFERENCE               TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: 1%/50%   1         6         1          32s
NAME                          CPU(cores)   MEMORY(bytes)
php-apache-7cccb789ff-9f2gb   1m           9Mi
```

### ขั้นที่ 3: อ่าน HPA และเทียบกับ YAML

<p align="center" id="fig-5">
  <img src="images/05-lab2-result.png" alt="รูปที่ 5 ผล LAB 2" width="900"><br>
  <em><b>รูปที่ 5</b> ผล LAB 2: kubectl get hpa → TARGETS cpu: 1%/50%, MINPODS 1, MAXPODS 6, REPLICAS 1; YAML ที่ได้เป็น autoscaling/v2 type Utilization</em>
</p>

```bash
kubectl -n hpa-demo get hpa php-apache -o yaml | sed -n '/^spec:/,/^status:/p'
kubectl -n hpa-demo describe hpa php-apache | sed -n '/^Conditions/,/^Events/p'
cat lab02-first/20-hpa-php.yaml
```

```text
spec:
  maxReplicas: 6
  metrics:
  - resource:
      name: cpu
      target:
        averageUtilization: 50
        type: Utilization
    type: Resource
  minReplicas: 1
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
status:
Conditions:
  Type            Status  Reason              Message
  ----            ------  ------              -------
  AbleToScale     True    ReadyForNewScale    recommended size matches current size
  ScalingActive   True    ValidMetricFound    the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
  ScalingLimited  False   DesiredWithinRange  the desired count is within the acceptable range
Events:
```

- `kubectl autoscale` สร้าง `autoscaling/v2` แบบ `type: Resource` → `cpu` → `Utilization 50` = **เฉลี่ย 50% ของ `requests.cpu` (100m) = 50m ต่อ Pod**
- Conditions 3 ตัว: `AbleToScale` (แก้ `/scale` ของ Deployment ได้), `ScalingActive` (อ่าน metric ได้), `ScalingLimited` (ชน min/max หรือไม่)

ไฟล์ `20-hpa-php.yaml` คือ HPA เดียวกันแบบ YAML ตรวจว่า spec เท่ากัน แล้ว apply ทับ (ต่อจากนี้ดูแล HPA ด้วยไฟล์)

```bash
diff <(kubectl -n hpa-demo get hpa php-apache -o jsonpath='{.spec}') <(kubectl apply --dry-run=server -f lab02-first/20-hpa-php.yaml -o jsonpath='{.spec}') && echo "spec เท่ากัน"
kubectl apply -f lab02-first/20-hpa-php.yaml
```

```text
Warning: resource horizontalpodautoscalers/php-apache is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. ...
spec เท่ากัน
Warning: resource horizontalpodautoscalers/php-apache is missing the kubectl.kubernetes.io/last-applied-configuration annotation ... The missing annotation will be patched automatically.
horizontalpodautoscaler.autoscaling/php-apache configured
```

Warning เรื่อง `last-applied-configuration` เป็นเรื่องปกติ (HPA สร้างด้วยคำสั่ง ไม่ใช่ apply) kubectl เติมให้เอง — annotation นี้จะสำคัญมากใน LAB 10

### สิ่งที่เห็น

- HPA `php-apache` `cpu: 1%/50%` min 1 max 6 replicas 1
- ช่วงแรก `<unknown>` + `FailedGetResourceMetric` แล้วหายเองเมื่อ metrics-server มีค่า

**คำถามชวนคิด**

1. ถ้า requests เป็น 200m แต่ใช้จริง 50m TARGETS จะแสดงกี่ % และ HPA จะทำอะไร
2. ทำไม HPA ต้องอ้าง Deployment (`scaleTargetRef`) ไม่อ้าง Pod ตรง ๆ

**เก็บกวาด:** ไม่ลบ — namespace `hpa-demo` (แอป `php-apache` + HPA จาก `20-hpa-php.yaml`) ใช้ต่อใน LAB 3

---

## LAB 3: ยิงโหลด แล้วดู scale up

<p align="center" id="fig-6">
  <img src="images/06-lab3-open.png" alt="รูปที่ 6 LAB 3 ยิงโหลด" width="900"><br>
  <em><b>รูปที่ 6</b> LAB 3 เปิด: 30-load.yaml = busybox วน wget ไป php-apache (namespace hpa-load) แล้ว watch-hpa.sh ดูทุก 5 วิ</em>
</p>

**เป้าหมาย:** ปล่อยลูกค้าจำลองแล้วดูหุ่นยนต์เพิ่มบูธเองจนชนเพดาน `maxReplicas`

**ไฟล์:** `lab03-load/30-load.yaml` (namespace `hpa-load` + Deployment `load` busybox วน `wget -q -T 2` ไป `http://php-apache.hpa-demo`), `watch-hpa.sh` (ARM: `30-load-arm.yaml`)

> `-T 2` สำคัญ: ถ้าไม่ใส่ wget จะรอไม่มีกำหนดเมื่อ Pod ปลายทางถูกปิดกลางคัน (เช่น LAB 10) โหลดจะหายไปเงียบ ๆ

### ขั้นที่ 1: เปิดหน้าต่างดูค่า

🐧 **หน้าต่างที่ 1** (โฟลเดอร์ `02_LAB`) — `watch-hpa.sh` พิมพ์ทุก 5 วินาที: วินาทีที่ผ่านไป, TARGETS, `replicas=` (ที่ HPA สั่งตาม status ของ HPA) และ `ready=` (Pod ที่พร้อมจริงของ Deployment)

```bash
./watch-hpa.sh hpa-demo php-apache 150
```

### ขั้นที่ 2: ปล่อยลูกค้า

🐧 **หน้าต่างที่ 2**

```bash
kubectl apply -f lab03-load/30-load.yaml
```

ผลจริงของหน้าต่างที่ 1 (เริ่มยิงที่วินาทีที่ ~1)

```text
   0s  1%/50% replicas=1 ready=1
   5s  1%/50% replicas=1 ready=1
...
  20s  1%/50% replicas=1 ready=1
  25s  19%/50% replicas=1 ready=1
  30s  19%/50% replicas=1 ready=1
  35s  19%/50% replicas=1 ready=1
  40s  301%/50% replicas=1 ready=2
  45s  301%/50% replicas=1 ready=2
  50s  301%/50% replicas=1 ready=4
  56s  299%/50% replicas=4 ready=6
  61s  299%/50% replicas=4 ready=6
  66s  299%/50% replicas=4 ready=6
  71s  224%/50% replicas=6 ready=6
  76s  224%/50% replicas=6 ready=6
  81s  224%/50% replicas=6 ready=6
  86s  66%/50% replicas=6 ready=6
...
 132s  72%/50% replicas=6 ready=6
 147s  75%/50% replicas=6 ready=6
```

- ~25 วินาทีแรกยังเห็น `1%` เพราะ busybox ต้องดึง image + metrics-server จดค่ารอบถัดไป (มิเตอร์ช้ากว่าความจริงได้ 15–30 วินาที)
- CPU ขึ้นถึง **301%** (ใช้ ~300m = ชน limits 300m) — **% เกิน 100 ได้** เพราะเทียบกับ requests ไม่ใช่ limits
- HPA สั่ง **1 → 4 → 6** (เครื่องอื่นอาจเป็น 1 → 5 → 6) **Ready 6 ราว 55 วินาทีหลังเริ่มยิง** คอลัมน์ `replicas=` (status ของ HPA) ช้ากว่า `ready=` ได้ 5–15 วินาที
- ที่ 6 Pod CPU เฉลี่ยยัง **~66–78%** (> 50%) แต่เพิ่มไม่ได้แล้ว

### ขั้นที่ 3: ดูว่าใครเหนื่อยแค่ไหน และทำไมหยุดที่ 6

<p align="center" id="fig-7">
  <img src="images/07-lab3-scale-up-result.png" alt="รูปที่ 7 ผล LAB 3 scale up" width="900"><br>
  <em><b>รูปที่ 7</b> ผล LAB 3: ~30 วิหลังเริ่มโหลด CPU ขึ้น ~300% → HPA สั่ง 1 → 4 หรือ 5 แล้วเป็น 6 ใน 15 วิถัดไป (Ready ครบ 6 ~55–65 วิ บนเครื่อง 4 core); ที่ 6 Pod ยังเฉลี่ย ~70% → ScalingLimited TooManyReplicas</em>
</p>

```bash
kubectl -n hpa-demo get hpa; kubectl top pod -n hpa-demo; kubectl top pod -n hpa-load
kubectl -n hpa-demo get pod -o wide
kubectl -n hpa-demo describe hpa php-apache | sed -n '/^Conditions/,$p'
```

```text
NAME         REFERENCE               TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: 71%/50%   1         6         6          3m16s
NAME                          CPU(cores)   MEMORY(bytes)
php-apache-7cccb789ff-9f2gb   85m          12Mi
php-apache-7cccb789ff-g7r9w   64m          11Mi
php-apache-7cccb789ff-qdlc4   75m          11Mi
php-apache-7cccb789ff-tjb2b   61m          11Mi
php-apache-7cccb789ff-tqkcp   71m          11Mi
php-apache-7cccb789ff-w4kwc   70m          11Mi
NAME                    CPU(cores)   MEMORY(bytes)
load-6dc955d56d-qr99n   23m          1Mi
NAME                          READY   STATUS    RESTARTS   AGE     IP            NODE
php-apache-7cccb789ff-9f2gb   1/1     Running   0          3m27s   10.244.2.11   lab-worker2
php-apache-7cccb789ff-g7r9w   1/1     Running   0          105s    10.244.1.10   lab-worker
php-apache-7cccb789ff-qdlc4   1/1     Running   0          2m      10.244.1.9    lab-worker
php-apache-7cccb789ff-tjb2b   1/1     Running   0          105s    10.244.2.14   lab-worker2
php-apache-7cccb789ff-tqkcp   1/1     Running   0          2m      10.244.1.8    lab-worker
php-apache-7cccb789ff-w4kwc   1/1     Running   0          2m      10.244.2.13   lab-worker2
Conditions:
  Type            Status  Reason               Message
  ----            ------  ------               -------
  AbleToScale     True    ScaleDownStabilized  recent recommendations were higher than current one, applying the highest recent recommendation
  ScalingActive   True    ValidMetricFound     the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
  ScalingLimited  True    TooManyReplicas      the desired replica count is more than the maximum replica count
  ScaledToZero    False   NotScaledToZero      the HPA controller did not scale the workload to zero
Events:
  Type     Reason                        Age    From                       Message
  ----     ------                        ----   ----                       -------
  Warning  FailedGetResourceMetric       3m16s  horizontal-pod-autoscaler  failed to get cpu utilization: unable to get metrics for resource cpu: no metrics returned from resource metrics API
...
  Normal   SuccessfulRescale             2m1s   horizontal-pod-autoscaler  New size: 4; reason: cpu resource utilization (percentage of request) above target
  Normal   SuccessfulRescale             105s   horizontal-pod-autoscaler  New size: 6; reason: cpu resource utilization (percentage of request) above target
```

- โหลดเท่าเดิม (ลูกค้า 1 คน ~0.43 core รวม) แต่แบ่ง 6 บูธ → เฉลี่ย ~71m ต่อบูธ Pod กระจาย 2 worker (control-plane มี taint จึงไม่รับ)
- `ScalingLimited True TooManyReplicas` = อยากได้มากกว่า 6 แต่ติดเพดาน
- `ScaledToZero False NotScaledToZero` เป็น condition ใหม่ของ v1.37 (feature `HPAScaleToZero` ยังไม่เปิดให้ใช้ทั่วไป — HPA ปกติ `minReplicas` ต่ำสุดคือ 1)
- เครื่องทดลอง 4 CPU รับไหวสบาย (โหลดรวมของ LAB นี้ < 0.6 core)

**ไม่ต้องหยุดตัวยิง** LAB 4 จะหยุดเองพร้อมจับเวลา

### สิ่งที่เห็น

- 1 → 4 → 6 บูธเอง ภายใน ~1 นาที ด้วย reason `cpu resource utilization (percentage of request) above target`
- ชนเพดาน `TooManyReplicas` ทั้งที่ CPU ยังเกินเป้า

**คำถามชวนคิด**

1. ถ้าเพิ่มลูกค้าเป็น 2 คน (`kubectl -n hpa-load scale deploy/load --replicas=2`) จำนวนบูธจะเปลี่ยนไหม แล้ว CPU เฉลี่ยจะเป็นอย่างไร
2. ทำไมตัวยิงโหลดจึงอยู่คนละ namespace กับแอป

**เก็บกวาด:** ปล่อยตัวยิง (`load` 1 Pod) และ 6 บูธไว้ LAB 4 เริ่มจากสภาพนี้ (ถ้าจะพักนาน ให้ `kubectl -n hpa-load scale deploy/load --replicas=0`)

---

## LAB 4: scale down และนาฬิกาทราย

<p align="center" id="fig-8">
  <img src="images/08-lab4-open.png" alt="รูปที่ 8 LAB 4 scale down" width="900"><br>
  <em><b>รูปที่ 8</b> LAB 4 เปิด: หยุดลูกค้า (scale load 0) แล้วเทียบเวลาปิดบูธ: ค่าเริ่มต้น 300 วิ กับ 40-hpa-fast-down.yaml ที่ stabilizationWindowSeconds: 30</em>
</p>

**เป้าหมาย:** หยุดลูกค้าแล้วจับเวลาที่หุ่นยนต์ปิดบูธ เทียบค่าเริ่มต้น (**นาฬิกาทราย 300 วินาที**) กับ `stabilizationWindowSeconds: 30`

**ไฟล์:** `lab04-scaledown/40-hpa-fast-down.yaml`

### ขั้นที่ 1: ค่าเริ่มต้น (รอ ~5.5 นาที — ข้ามได้)

> **ข้ามได้ถ้าเวลาไม่พอ** ดูผลจริงในบล็อกข้างล่างแล้วไปขั้นที่ 2

🐧 หน้าต่างที่ 1: `./watch-hpa.sh hpa-demo php-apache 400`  🐧 หน้าต่างที่ 2:

```bash
kubectl -n hpa-load scale deploy/load --replicas=0
sleep 60; kubectl -n hpa-demo describe hpa php-apache | grep -A1 AbleToScale
```

```text
deployment.apps/load scaled
  AbleToScale     True    ScaleDownStabilized  recent recommendations were higher than current one, applying the highest recent recommendation
```

ผลจริงของหน้าต่างที่ 1 (แสดงทุก ~10 วินาที)

```text
   0s  71%/50% replicas=6 ready=6
  10s  79%/50% replicas=6 ready=6
  20s  79%/50% replicas=6 ready=6
  31s  22%/50% replicas=6 ready=6
  41s  1%/50% replicas=6 ready=6
  51s  1%/50% replicas=6 ready=6
...
 295s  1%/50% replicas=6 ready=6
 305s  1%/50% replicas=6 ready=6
 315s  1%/50% replicas=6 ready=3
 325s  1%/50% replicas=3 ready=1
 335s  1%/50% replicas=3 ready=1
 345s  1%/50% replicas=1 ready=1
```

```bash
kubectl -n hpa-demo get events --field-selector involvedObject.kind=HorizontalPodAutoscaler --sort-by=.lastTimestamp | tail -2
```

```text
94s         Normal    SuccessfulRescale              horizontalpodautoscaler/php-apache   New size: 3; reason: All metrics below target
79s         Normal    SuccessfulRescale              horizontalpodautoscaler/php-apache   New size: 1; reason: All metrics below target
```

- CPU ตกเหลือ 1% ภายใน ~40 วินาที (มิเตอร์ช้ากว่าความจริง) แต่บูธยังเปิด 6 ไปอีก **~4.5 นาที** — condition `ScaleDownStabilized` = นาฬิกาทราย: ตอนลด HPA เลือกค่าแนะนำ **สูงสุด** ในช่วง 300 วินาทีล่าสุด
- **6 → 3 ที่ ~310 วินาที แล้ว → 1 ที่ ~325–345 วินาที (≈ 5 นาที 25 วินาทีหลังหยุด)** ลด 2 ขั้นเพราะในหน้าต่าง 300 วินาทียังจำคำแนะนำ "3" ตอน CPU 22% (เครื่องอื่นอาจเห็น 6 → 2 → 1)

### ขั้นที่ 2: ย่อนาฬิกาทรายเหลือ 30 วินาที

<p align="center" id="fig-9">
  <img src="images/09-lab4-result.png" alt="รูปที่ 9 ผล LAB 4" width="900"><br>
  <em><b>รูปที่ 9</b> ผล LAB 4: ค่าเริ่มต้นใช้ ~5 นาที 25 วิหลังหยุดโหลด (6 → 3 → 1) ส่วน window 30 วิ ใช้ ~60–75 วิ — แต่ CPU ต้องลดลงก่อน (~25–45 วิ เพราะรอบจดมิเตอร์)</em>
</p>

```bash
kubectl apply -f lab04-scaledown/40-hpa-fast-down.yaml
kubectl -n hpa-demo get hpa php-apache -o jsonpath='{.spec.behavior}'; echo
kubectl -n hpa-load scale deploy/load --replicas=1
until [ "$(kubectl -n hpa-demo get deploy php-apache -o jsonpath={.status.readyReplicas})" = 6 ]; do sleep 3; done; echo "ready 6"
```

```text
horizontalpodautoscaler.autoscaling/php-apache configured
{"scaleDown":{"policies":[{"periodSeconds":15,"type":"Percent","value":100}],"selectPolicy":"Max","stabilizationWindowSeconds":30},"scaleUp":{"policies":[{"periodSeconds":15,"type":"Pods","value":4},{"periodSeconds":15,"type":"Percent","value":100}],"selectPolicy":"Max","stabilizationWindowSeconds":0}}
deployment.apps/load scaled
ready 6
```

ไฟล์ใส่แค่ `scaleDown.stabilizationWindowSeconds: 30` ที่เหลือ API server เติมค่าเริ่มต้นให้ — **scaleUp: window 0, เพิ่มได้ max(4 Pod, 100%) ต่อ 15 วินาที; scaleDown: ลดได้ 100% ต่อ 15 วินาที** (ready 6 หลังเริ่มยิงราว 64 วินาที) รอ ~30 วินาทีให้นิ่ง แล้วหยุดลูกค้าพร้อมดูหน้าต่างที่ 1 (`./watch-hpa.sh hpa-demo php-apache 150`)

```bash
kubectl -n hpa-load scale deploy/load --replicas=0
```

```text
   0s  69%/50% replicas=6 ready=6
...
  26s  71%/50% replicas=6 ready=6
  31s  27%/50% replicas=6 ready=6
  41s  27%/50% replicas=6 ready=6
  46s  1%/50% replicas=6 ready=4
  56s  1%/50% replicas=6 ready=4
  61s  1%/50% replicas=4 ready=1
  71s  1%/50% replicas=4 ready=1
  76s  1%/50% replicas=1 ready=1
```

**6 → 4 ที่ ~45 วินาที แล้ว → 1 ที่ ~60 วินาที** (ready 1 ราว 60 วินาทีหลังหยุด, status ของ HPA ตามมา ~75 วินาที) เร็วกว่าค่าเริ่มต้นราว 4 นาที

### สิ่งที่เห็น

| | ค่าเริ่มต้น (300 วินาที) | `stabilizationWindowSeconds: 30` |
|---|---|---|
| CPU ตกให้เห็น | ~30–40 วินาที | ~30–45 วินาที |
| บูธลดถึง 1 | **~5 นาที 25 วินาที** (6 → 3 → 1) | **~60–75 วินาที** (6 → 4 → 1) |
| reason | `All metrics below target` | `All metrics below target` |

**คำถามชวนคิด**

1. ทำไมค่าเริ่มต้นจึงตั้งใจให้ลดช้า (5 นาที) แต่เพิ่มทันที (0 วินาที) ถ้าลดเร็วเกินไปกับร้านที่ลูกค้ามาเป็นระลอกจะเกิดอะไร (flapping)
2. ระบบจริงควรใช้ window 30 วินาทีแบบ LAB ไหม

**เก็บกวาด:** ตัวยิงเป็น 0 แล้ว และ HPA เป็นแบบ `40-hpa-fast-down.yaml` (window 30) ซึ่ง LAB 5–6 ใช้ต่อ — ตรวจด้วย `kubectl -n hpa-demo get hpa,deploy` ว่าเหลือ `php-apache` 1 Pod

---

## LAB 5: ลืม requests

<p align="center" id="fig-10">
  <img src="images/10-lab5-open-result.png" alt="รูปที่ 10 LAB 5 ลืม requests" width="900"><br>
  <em><b>รูปที่ 10</b> LAB 5: 50-no-requests.yaml ไม่มี requests → cpu: &lt;unknown&gt;/50%, FailedGetResourceMetric: missing request for cpu; แก้ด้วย kubectl set resources --requests=cpu=100m แล้วได้ % ใน ~30 วิ</em>
</p>

**เป้าหมาย:** เห็นว่า HPA แบบ `Utilization` คิด % ไม่ได้ถ้า container ไม่มี `requests.cpu` แล้วแก้

**ไฟล์:** `lab05-norequests/50-no-requests.yaml` (Deployment `nores` ไม่มี `resources:` + HPA `nores` max 4) (ARM: `50-no-requests-arm.yaml`)

```bash
kubectl apply -f lab05-norequests/50-no-requests.yaml
kubectl -n hpa-demo rollout status deploy/nores --timeout=120s
sleep 45; kubectl -n hpa-demo get hpa nores
kubectl -n hpa-demo describe hpa nores | sed -n '/^Conditions/,$p'
```

```text
deployment.apps/nores created
horizontalpodautoscaler.autoscaling/nores created
deployment "nores" successfully rolled out
NAME    REFERENCE          TARGETS              MINPODS   MAXPODS   REPLICAS   AGE
nores   Deployment/nores   cpu: <unknown>/50%   1         4         1          47s
Conditions:
  Type           Status  Reason                   Message
  ----           ------  ------                   -------
  AbleToScale    True    SucceededGetScale        the HPA controller was able to get the target's current scale
  ScalingActive  False   FailedGetResourceMetric  the HPA was unable to compute the replica count: failed to get cpu utilization: missing request for cpu in container php-apache of Pod nores-c8675d8cb-pjmmz
Events:
  Type     Reason                        Age                From                       Message
  ----     ------                        ----               ----                       -------
  Warning  FailedGetResourceMetric       47s                horizontal-pod-autoscaler  failed to get cpu utilization: unable to get metrics for resource cpu: no metrics returned from resource metrics API
...
  Warning  FailedGetResourceMetric       2s                 horizontal-pod-autoscaler  failed to get cpu utilization: missing request for cpu in container php-apache of Pod nores-c8675d8cb-pjmmz
```

ต่างจาก LAB 2: **รอนานเท่าไรก็ `<unknown>`** ข้อความเปลี่ยนจาก `no metrics returned` (ยังไม่มีค่า) เป็น **`missing request for cpu in container php-apache`** (มีค่าแล้วแต่ไม่มีตัวหาร) HPA จะไม่ทำอะไรเลยแม้ลูกค้าล้น แก้โดยใส่ requests

```bash
kubectl -n hpa-demo set resources deploy nores --requests=cpu=100m
t0=$(date +%s); kubectl -n hpa-demo rollout status deploy/nores --timeout=120s
until kubectl -n hpa-demo get hpa nores --no-headers | grep -q "cpu: [0-9]"; do sleep 3; done; echo "ได้ % หลัง set resources $(( $(date +%s)-t0 )) วิ"
kubectl -n hpa-demo get hpa nores
kubectl delete -f lab05-norequests/50-no-requests.yaml
```

```text
deployment.apps/nores resource requirements updated
deployment "nores" successfully rolled out
ได้ % หลัง set resources 29 วิ
NAME    REFERENCE          TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
nores   Deployment/nores   cpu: 1%/50%   1         4         1          76s
deployment.apps "nores" deleted from hpa-demo namespace
horizontalpodautoscaler.autoscaling "nores" deleted from hpa-demo namespace
```

`set resources` แก้ template → Pod ใหม่ → ได้ % ใน ~30 วินาที (ไฟล์ YAML ยังไม่มี requests — ระบบจริงต้องแก้ไฟล์ด้วย)

### สิ่งที่เห็น

- ไม่มี requests → `cpu: <unknown>/50%` + `ScalingActive False` + `missing request for cpu`
- ใส่ requests แล้วได้ `cpu: 1%/50%`

**คำถามชวนคิด:** Pod ที่มี 2 container (เช่น web + sidecar) แต่ใส่ requests แค่ container เดียว จะเป็นอย่างไร (ดูทฤษฎีหัวข้อ 6)

**เก็บกวาด:** ลบ `nores` แล้วในขั้นสุดท้าย (`kubectl delete -f lab05-norequests/50-no-requests.yaml`) ตรวจว่า `kubectl -n hpa-demo get hpa` เหลือแค่ `php-apache`

---

## LAB 6: คิดตามสูตร desiredReplicas

<p align="center" id="fig-11">
  <img src="images/11-lab6-formula.png" alt="รูปที่ 11 LAB 6 สูตร" width="900"><br>
  <em><b>รูปที่ 11</b> LAB 6: formula.sh อ่าน status แล้วคิด ceil(current × utilization ÷ target) ตรงกับ HPA ทุกครั้ง เช่น 1 × 200 ÷ 50 → 4 และ 4 × 299 ÷ 50 = 23.92 → 24 แต่ max 6</em>
</p>

**เป้าหมาย:** ยืนยันสูตร `desiredReplicas = ceil(currentReplicas × currentUtilization ÷ targetUtilization)` กับค่าที่ HPA สั่งจริง

**ไฟล์:** `lab06-formula/formula.sh` (อ่าน `status.currentReplicas`, `status.currentMetrics[0]...averageUtilization`, `status.desiredReplicas` จาก HPA แล้วคิดให้ดู)

```bash
kubectl -n hpa-load scale deploy/load --replicas=1
for i in $(seq 8); do sleep 15; echo "--- $((i*15)) วิ"; ./lab06-formula/formula.sh; done
```

```text
deployment.apps/load scaled
--- 15 วิ
currentReplicas=1  currentUtilization=1%  target=50%
สูตร: ceil(1 × 1 / 50) = ceil(0.02) = 1
HPA สั่งจริง desiredReplicas=1
--- 30 วิ
currentReplicas=1  currentUtilization=200%  target=50%
สูตร: ceil(1 × 200 / 50) = ceil(4.00) = 4
HPA สั่งจริง desiredReplicas=4
--- 45 วิ
currentReplicas=4  currentUtilization=299%  target=50%
สูตร: ceil(4 × 299 / 50) = ceil(23.92) = 24  → เกิน maxReplicas 6 จึงได้ 6
HPA สั่งจริง desiredReplicas=6
--- 60 วิ
currentReplicas=6  currentUtilization=106%  target=50%
สูตร: ceil(6 × 106 / 50) = ceil(12.72) = 13  → เกิน maxReplicas 6 จึงได้ 6
HPA สั่งจริง desiredReplicas=6
--- 75 วิ
currentReplicas=6  currentUtilization=74%  target=50%
สูตร: ceil(6 × 74 / 50) = ceil(8.88) = 9  → เกิน maxReplicas 6 จึงได้ 6
HPA สั่งจริง desiredReplicas=6
...
--- 120 วิ
currentReplicas=6  currentUtilization=65%  target=50%
สูตร: ceil(6 × 65 / 50) = ceil(7.80) = 8  → เกิน maxReplicas 6 จึงได้ 6
HPA สั่งจริง desiredReplicas=6
```

- ทุกรอบสูตรตรงกับ `desiredReplicas` (ตัวเลข % ของเครื่องนักศึกษาจะต่าง แต่สูตรต้องตรง)
- รอบ 45 วินาที: 4 Pod ที่ 299% อยากได้ 24 แต่ `maxReplicas` 6 ชนะ (นโยบายค่าเริ่มต้นเพิ่มได้ max(4 Pod, 100%) ต่อ 15 วินาที = 8 ก็ไม่เกิน)
- `currentUtilization` คือค่าเฉลี่ยของ Pod ที่ "นับได้" (Pod ไม่พร้อม/ขาด metric HPA คิดแบบระวังตัว — ทฤษฎีหัวข้อ 7) สคริปต์จะพิมพ์ "อยู่ใน tolerance 10%" เมื่อ `utilization ÷ target` อยู่ระหว่าง 0.9–1.1 (HPA ไม่เปลี่ยน)
- tolerance 10% เป็นค่าทั้งคลัสเตอร์ (`--horizontal-pod-autoscaler-tolerance` ของ kube-controller-manager) **ตั้งแต่ Kubernetes v1.37 ฟีเจอร์ `HPAConfigurableTolerance` เป็น stable (GA)** ตั้งแยกต่อ HPA ได้ที่ `behavior.scaleUp.tolerance` / `behavior.scaleDown.tolerance` (เช่น `tolerance: "0.05"` ระบบเก็บเป็น `50m`) ดู `kubectl explain hpa.spec.behavior.scaleUp.tolerance` — ไฟล์ของบทไม่ได้ตั้ง จึงใช้ค่า 10%

หยุดลูกค้า แล้วรอให้กลับเป็น 1 (ใช้ window 30 จาก LAB 4)

```bash
kubectl -n hpa-load scale deploy/load --replicas=0
until [ "$(kubectl -n hpa-demo get deploy php-apache -o jsonpath={.spec.replicas})" = 1 ]; do sleep 5; done; kubectl -n hpa-demo get deploy php-apache
```

**คำถามชวนคิด:** ถ้า 6 Pod เฉลี่ย 54% HPA จะสั่งเท่าไร (คิดสูตร แล้วนึกถึง tolerance)

**เก็บกวาด:** หยุดตัวยิงแล้ว (`--replicas=0`) และรอให้ `php-apache` กลับเป็น 1 ก่อนเริ่ม LAB 7

---

## LAB 7: behavior: เพิ่มทีละ 1 บูธ

<p align="center" id="fig-12">
  <img src="images/12-lab7-policies.png" alt="รูปที่ 12 LAB 7 behavior" width="900"><br>
  <em><b>รูปที่ 12</b> LAB 7: 70-hpa-slow-up.yaml (Pods 1 ต่อ 15 วิ) → 1 → 2 → 3 → 4 → 5 → 6 (Ready ครบ ~85 วิ) เทียบค่าเริ่มต้นที่เพิ่ม 2 ขั้นถึง 6 (Ready ~55 วิ)</em>
</p>

**เป้าหมาย:** คุมความเร็วการเพิ่ม/ลดด้วย `behavior.scaleUp/scaleDown.policies`

**ไฟล์:** `lab07-behavior/70-hpa-slow-up.yaml` (scaleUp `Pods 1 / 15 วินาที`, scaleDown window 30 + `Percent 50 / 15 วินาที`)

```bash
kubectl apply -f lab07-behavior/70-hpa-slow-up.yaml
```

🐧 หน้าต่างที่ 1: `./watch-hpa.sh hpa-demo php-apache 150`  🐧 หน้าต่างที่ 2: `kubectl -n hpa-load scale deploy/load --replicas=1`

```text
   0s  1%/50% replicas=1 ready=1
...
  15s  1%/50% replicas=1 ready=1
  20s  87%/50% replicas=1 ready=1
  25s  87%/50% replicas=1 ready=2
  36s  292%/50% replicas=2 ready=2
  41s  292%/50% replicas=2 ready=3
  51s  158%/50% replicas=3 ready=3
  56s  158%/50% replicas=3 ready=4
  66s  148%/50% replicas=4 ready=4
  71s  148%/50% replicas=4 ready=5
  81s  116%/50% replicas=5 ready=5
  86s  116%/50% replicas=5 ready=6
  97s  75%/50% replicas=6 ready=6
```

```bash
kubectl -n hpa-demo get events --field-selector involvedObject.kind=HorizontalPodAutoscaler,reason=SuccessfulRescale --sort-by=.lastTimestamp | tail -5
```

```text
2m13s       Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 2; reason: cpu resource utilization (percentage of request) above target
118s        Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 3; reason: cpu resource utilization (percentage of request) above target
103s        Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 4; reason: cpu resource utilization (percentage of request) above target
88s         Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 5; reason: cpu resource utilization (percentage of request) above target
73s         Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 6; reason: cpu resource utilization (percentage of request) above target
```

Event ห่างกัน **15 วินาทีพอดี** ทีละ 1 Pod (1 → 6 ใช้ 5 ขั้น = 60 วินาที, Ready 6 ราว 85 วินาทีหลังเริ่มยิง) ทั้งที่สูตรอยากได้ 6 ทันที ต่อด้วยขาลง (หน้าต่างที่ 1 `./watch-hpa.sh hpa-demo php-apache 110`, หน้าต่างที่ 2 `kubectl -n hpa-load scale deploy/load --replicas=0`)

```text
   0s  68%/50% replicas=6 ready=6
  31s  35%/50% replicas=6 ready=6
  51s  1%/50% replicas=6 ready=5
  61s  1%/50% replicas=5 ready=2
  81s  1%/50% replicas=2 ready=1
  92s  1%/50% replicas=1 ready=1
```

ขาลง: 6 → 5 (ตอน CPU 35% สูตรได้ `ceil(6 × 35 ÷ 50) = 5`) → 2 → 1 event ห่างกัน 15 วินาที เพราะ `Percent 50` จำกัดจำนวนที่ลดได้ในแต่ละช่วง 15 วินาที (ค่าเริ่มต้น `Percent 100` ลดรวดเดียวได้) ถึง 1 ราว 80–90 วินาทีหลังหยุด

### สิ่งที่เห็น

| | ค่าเริ่มต้น (LAB 3–4) | `70-hpa-slow-up.yaml` |
|---|---|---|
| ขาขึ้น | 1 → 4 → 6 (2 ขั้น) Ready 6 ~55–65 วินาที | 1 → 2 → 3 → 4 → 5 → 6 ทุก 15 วินาที Ready 6 ~85 วินาที |
| ขาลง (window 30) | 6 → 4 → 1 (`Percent 100`) | 6 → 5 → 2 → 1 (`Percent 50` ต่อ 15 วินาที) |

**คำถามชวนคิด:** ถ้าใส่ `selectPolicy: Disabled` ใน scaleDown จะเกิดอะไร และเหมาะกับงานแบบไหน

**เก็บกวาด:** ตัวยิงเป็น 0 และ `php-apache` กลับเป็น 1 แล้ว HPA ยังเป็นแบบ `70-hpa-slow-up.yaml` ไม่ต้องคืน (LAB 8 apply ทับ)

---

## LAB 8: หลาย metric: CPU + memory

<p align="center" id="fig-13">
  <img src="images/13-lab8-multi.png" alt="รูปที่ 13 LAB 8 หลาย metric" width="900"><br>
  <em><b>รูปที่ 13</b> LAB 8: 80-hpa-multi.yaml (cpu 50% + memory averageValue 6Mi) ไม่มีโหลดแต่ memory ชนะ → scale ถึง 6 และไม่ลด; TARGETS แสดง memory เป็นหน่วย m (มิลลิไบต์) เช่น 9859754666m/6Mi (ค่า 6Mi ปรับจาก 8Mi เพราะเครื่องอื่นอาจใช้ memory ต่ำกว่า)</em>
</p>

**เป้าหมาย:** HPA ที่มีหลาย metric เลือกจำนวน **มากที่สุด** ของทุก metric และเห็นข้อควรระวังของ memory

**ไฟล์:** `lab08-multi/80-hpa-multi.yaml` (cpu Utilization 50 + memory `AverageValue 6Mi` ตั้งต่ำกว่าที่ php-apache ใช้จริงโดยตั้งใจ, scaleDown window 30)

ไม่มีลูกค้า (ตัวยิง = 0) php-apache 1 Pod ใช้ memory ~11Mi

```bash
kubectl top pod -n hpa-demo
kubectl apply -f lab08-multi/80-hpa-multi.yaml
```

🐧 หน้าต่างที่ 1: `./watch-hpa.sh hpa-demo php-apache 120`

```text
NAME                          CPU(cores)   MEMORY(bytes)
php-apache-7cccb789ff-tjb2b   1m           11Mi
horizontalpodautoscaler.autoscaling/php-apache configured
   1s  1%/50%, memory: 12104Ki/6Mi replicas=1 ready=1
   6s  1%/50%, memory: 12104Ki/6Mi replicas=1 ready=2
  11s  1%/50%, memory: 12104Ki/6Mi replicas=2 ready=2
  21s  1%/50%, memory: 10592Ki/6Mi replicas=2 ready=2
  26s  1%/50%, memory: 10592Ki/6Mi replicas=2 ready=4
  36s  1%/50%, memory: 10592Ki/6Mi replicas=4 ready=4
  51s  1%/50%, memory: 9875Ki/6Mi replicas=4 ready=4
  56s  1%/50%, memory: 9875Ki/6Mi replicas=4 ready=6
  67s  1%/50%, memory: 9875Ki/6Mi replicas=6 ready=6
  82s  1%/50%, memory: 9859754666m/6Mi replicas=6 ready=6
 117s  1%/50%, memory: 9859754666m/6Mi replicas=6 ready=6
```

```bash
sleep 60; kubectl -n hpa-demo get hpa; kubectl top pod -n hpa-demo
kubectl -n hpa-demo get events --field-selector involvedObject.kind=HorizontalPodAutoscaler,reason=SuccessfulRescale --sort-by=.lastTimestamp | tail -3
```

```text
NAME         REFERENCE               TARGETS                                MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: 1%/50%, memory: 9859754666m/6Mi   1         6         6          31m
NAME                          CPU(cores)   MEMORY(bytes)
php-apache-7cccb789ff-55gqf   1m           8Mi
php-apache-7cccb789ff-h9rdl   1m           8Mi
php-apache-7cccb789ff-hp97z   1m           8Mi
php-apache-7cccb789ff-jnsbk   1m           8Mi
php-apache-7cccb789ff-tjb2b   1m           11Mi
php-apache-7cccb789ff-trwfd   1m           8Mi
3m7s        Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 2; reason: memory resource above target
2m46s       Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   (combined from similar events): New size: 4; reason: memory resource above target
2m16s       Normal   SuccessfulRescale   horizontalpodautoscaler/php-apache   New size: 6; reason: memory resource above target
```

- CPU บอก "1 พอ" แต่ memory บอก "มากกว่า 6" → HPA เลือกค่ามากสุด reason **`memory resource above target`** ถึง 6 ภายใน ~55 วินาทีทั้งที่ไม่มีลูกค้า
- **ไม่ลดเลย** (รอเพิ่ม 1 นาทีก็ยัง 6) เพราะ memory ของแต่ละ Pod ไม่ลดตามจำนวน Pod (Pod ใหม่ก็ใช้ ~8Mi อยู่ดี) — แอปที่ไม่คืน memory (cache, heap ของ runtime) กับ HPA memory = บูธเปิดค้างเต็มเพดาน
- **หน่วยแปลก** `12104Ki` และ `9859754666m` = ค่าเฉลี่ยของ memory ที่หารไม่ลงตัว Kubernetes แสดงเป็น milli-byte (9859754666m ≈ 9.4Mi) ไม่ใช่ millicore
- ถ้าตั้ง `8Mi` (ใกล้ค่าจริงของ Pod ใหม่) HPA จะค่อย ๆ เพิ่มทีละ 1 และใช้ ~2.5 นาทีกว่าจะถึง 6 (ทดลองแล้ว) ไฟล์บทจึงใช้ 6Mi ให้เห็นผลชัด

คืน HPA เป็นแบบ CPU อย่างเดียว (window 30) แล้วรอให้กลับเป็น 1

```bash
kubectl apply -f lab04-scaledown/40-hpa-fast-down.yaml
until [ "$(kubectl -n hpa-demo get deploy php-apache -o jsonpath={.status.readyReplicas})" = 1 ]; do sleep 5; done; kubectl -n hpa-demo get hpa
```

```text
horizontalpodautoscaler.autoscaling/php-apache configured
NAME         REFERENCE               TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: 1%/50%   1         6         6          31m
```

(คอลัมน์ REPLICAS ของ HPA ตามมาอีกไม่กี่วินาที)

**คำถามชวนคิด:** ถ้าจะใช้ memory กับ HPA จริง ควรตั้ง target อย่างไร และควรระวังเรื่อง `limits.memory` (OOMKilled) อย่างไร

**เก็บกวาด:** คืน HPA เป็น `40-hpa-fast-down.yaml` แล้วในขั้นสุดท้าย และ `php-apache` เหลือ 1 Pod (ถ้าข้ามขั้นนี้ LAB 9 จะเริ่มที่ 6 Pod เพราะ memory ยังชนะ)

---

## LAB 9: ชนเพดาน: ResourceQuota และ Pending

**เป้าหมาย:** เห็นว่า HPA "สั่ง" ได้ แต่ Pod อาจ "เกิด" ไม่ได้ — ติดงบของโซน (ResourceQuota บทที่ 4) หรือ Node ไม่มีที่ (Pending บทที่ 3) และ HPA ไม่รู้เรื่องนี้

**ไฟล์:** `lab09-limits/90-quota.yaml` (ResourceQuota `booth-budget` requests.cpu `300m` pods `10`), `lab09-limits/big-requests.sh`

### ก. ResourceQuota

<p align="center" id="fig-14">
  <img src="images/14-lab9-quota.png" alt="รูปที่ 14 LAB 9 ก ResourceQuota" width="900"><br>
  <em><b>รูปที่ 14</b> LAB 9 ก: ResourceQuota requests.cpu 300m → HPA สั่ง 6 แต่ได้ 3/6, ReplicaSet: exceeded quota: booth-budget</em>
</p>

```bash
kubectl apply -f lab09-limits/90-quota.yaml
kubectl -n hpa-demo describe resourcequota booth-budget
kubectl -n hpa-load scale deploy/load --replicas=1
sleep 90; kubectl -n hpa-demo get hpa,deploy; kubectl -n hpa-demo describe resourcequota booth-budget | tail -3
kubectl -n hpa-demo get events --field-selector reason=FailedCreate --sort-by=.lastTimestamp | tail -2
kubectl -n hpa-demo describe hpa php-apache | grep -A5 ^Conditions
```

```text
resourcequota/booth-budget created
Name:         booth-budget
Namespace:    hpa-demo
Resource      Used  Hard
--------      ----  ----
pods          1     10
requests.cpu  100m  300m
deployment.apps/load scaled
NAME                                             REFERENCE               TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/php-apache   Deployment/php-apache   cpu: 131%/50%   1         6         6          33m

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/php-apache   3/6     3            3           33m
--------      ----  ----
pods          3     10
requests.cpu  300m  300m
52s         Warning   FailedCreate   replicaset/php-apache-7cccb789ff   Error creating: pods "php-apache-7cccb789ff-jrdmf" is forbidden: exceeded quota: booth-budget, requested: requests.cpu=100m, used: requests.cpu=300m, limited: requests.cpu=300m
38s         Warning   FailedCreate   replicaset/php-apache-7cccb789ff   (combined from similar events): Error creating: pods "php-apache-7cccb789ff-z24c2" is forbidden: exceeded quota: booth-budget, requested: requests.cpu=100m, used: requests.cpu=300m, limited: requests.cpu=300m
Conditions:
  Type            Status  Reason            Message
  ----            ------  ------            -------
  AbleToScale     True    ReadyForNewScale  recommended size matches current size
  ScalingActive   True    ValidMetricFound  the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
  ScalingLimited  True    TooManyReplicas   the desired replica count is more than the maximum replica count
```

HPA บอก `REPLICAS 6` และ Conditions ดูปกติ แต่ Deployment ได้แค่ **3/6** ต้องไปดู Event ของ **ReplicaSet** จึงเห็น `exceeded quota: booth-budget` (CPU เฉลี่ยค้าง 131% เพราะ 3 บูธรับโหลดทั้งหมด) คืนค่า

```bash
kubectl -n hpa-load scale deploy/load --replicas=0
kubectl delete -f lab09-limits/90-quota.yaml
until [ "$(kubectl -n hpa-demo get deploy php-apache -o jsonpath={.spec.replicas})" = 1 ]; do sleep 5; done; kubectl -n hpa-demo rollout status deploy/php-apache
```

### ข. Node ไม่มีที่ (Pending)

<p align="center" id="fig-15">
  <img src="images/15-lab9-pending.png" alt="รูปที่ 15 LAB 9 ข Pending" width="900"><br>
  <em><b>รูปที่ 15</b> LAB 9 ข: requests ใหญ่ 60% ของ Node + minReplicas 4 → Running 2 (worker ละ 1) Pending 2: 0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu</em>
</p>

ตั้ง requests ของ php-apache เป็น 60% ของ CPU ที่ Node worker รับจองได้ (1 Node วางได้ 1 Pod) **รอ rollout เสร็จก่อน** แล้วค่อยบังคับให้ต้องมีอย่างน้อย 4 บูธ (ถ้าทำพร้อมกัน Pod รุ่นเก่าจาก rolling update จะค้างปนอยู่ ภาพสับสน)

```bash
kubectl describe node lab-worker | grep -A2 -E "^Allocatable"; kubectl describe node lab-control-plane | grep Taints
./lab09-limits/big-requests.sh
kubectl -n hpa-demo rollout status deploy/php-apache --timeout=120s
kubectl -n hpa-demo patch hpa php-apache -p '{"spec":{"minReplicas":4}}'
sleep 30; kubectl -n hpa-demo get pod -o wide; kubectl -n hpa-demo get hpa,deploy
```

```text
Allocatable:
  cpu:                32
  ephemeral-storage:  1081101176832
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
allocatable ของ lab-worker = 32 → requests = 60% = 19200m
deployment.apps/php-apache resource requirements updated
Waiting for deployment "php-apache" rollout to finish: 1 old replicas are pending termination...
deployment "php-apache" successfully rolled out
horizontalpodautoscaler.autoscaling/php-apache patched
NAME                          READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE
php-apache-68b7d68975-f5x69   0/1     Pending   0          30s   <none>        <none>        <none>
php-apache-68b7d68975-fhp9k   1/1     Running   0          30s   10.244.1.30   lab-worker    <none>
php-apache-68b7d68975-k6v6g   0/1     Pending   0          30s   <none>        <none>        <none>
php-apache-68b7d68975-r7gnt   1/1     Running   0          32s   10.244.2.32   lab-worker2   <none>
NAME                                             REFERENCE               TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/php-apache   Deployment/php-apache   cpu: 0%/50%   4         6         4          34m

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/php-apache   2/4     4            2           35m
```

allocatable ของเครื่องทดลองเป็น `32` (เครื่องนักศึกษา 4 core จะเห็น `4` → requests `2400m`, 8 core → `4800m` สคริปต์รองรับทั้งเลข core และหน่วย `m` เช่น `7800m`) ดูเหตุผลที่ Pending

```bash
P=$(kubectl -n hpa-demo get pod --field-selector=status.phase=Pending -o name | head -1); kubectl -n hpa-demo describe $P | sed -n '/^Events/,$p'
```

```text
Events:
  Type     Reason            Age                From               Message
  ----     ------            ----               ----               -------
  Warning  FailedScheduling  30s (x2 over 30s)  default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

- **Running 2 (worker ละ 1) Pending 2**: control-plane มี taint (`untolerated taint`), worker 2 ลำ CPU ไม่พอ (`Insufficient cpu`)
- HPA แสดง `REPLICAS 4` เหมือนทุกอย่างเรียบร้อย — HPA ไม่รู้ว่า Pod Pending บนคลาวด์ **Cluster Autoscaler** คือผู้ที่เห็น Pod Pending แล้วเรียกเรือ (Node) เพิ่ม (ทฤษฎีหัวข้อ 3)

คืนค่า (min 1 และ requests เดิม)

```bash
kubectl apply -f lab04-scaledown/40-hpa-fast-down.yaml
kubectl -n hpa-demo set resources deploy php-apache --requests=cpu=100m --limits=cpu=300m
kubectl -n hpa-demo rollout status deploy/php-apache --timeout=120s
sleep 40; kubectl -n hpa-demo get hpa,pod
```

```text
horizontalpodautoscaler.autoscaling/php-apache configured
deployment.apps/php-apache resource requirements updated
...
deployment "php-apache" successfully rolled out
NAME                                             REFERENCE               TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/php-apache   Deployment/php-apache   cpu: 1%/50%   1         6         1          35m

NAME                              READY   STATUS    RESTARTS   AGE
pod/php-apache-7cccb789ff-dz42n   1/1     Running   0          41s
```

### สิ่งที่เห็น

- ก: HPA 6 แต่ Deployment `3/6` เหตุผลอยู่ที่ Event ของ ReplicaSet (`exceeded quota`)
- ข: HPA 4 แต่ Running 2 Pending 2 เหตุผลอยู่ที่ Event ของ Pod (`Insufficient cpu`)

**คำถามชวนคิด:** ตั้ง `maxReplicas` ให้สัมพันธ์กับ ResourceQuota และความจุของ Node อย่างไร

**เก็บกวาด:** ลบ ResourceQuota แล้ว (ก), คืน `minReplicas: 1` และ requests `100m`/limits `300m` แล้ว (ข) ตรวจด้วย `kubectl -n hpa-demo get resourcequota,hpa,pod` ว่าไม่มี quota และเหลือ Pod `Running` 1 ตัว ไม่มี `Pending`

---

## LAB 10: กับดัก replicas ใน YAML

<p align="center" id="fig-16">
  <img src="images/16-lab10-trap.png" alt="รูปที่ 16 LAB 10 กับดัก replicas" width="900"><br>
  <em><b>รูปที่ 16</b> LAB 10: ระหว่าง HPA ถือ 6 Pod สั่ง kubectl apply -f 10-php-apache.yaml (replicas: 1) → เหลือ 1 ทันที แล้ว HPA ค่อย ๆ ดึงกลับ 3 → 4 → 6 ใน ~45–50 วิ; แก้ด้วยลบ replicas และ kubectl apply edit-last-applied / set-last-applied</em>
</p>

**เป้าหมาย:** เห็นว่า `replicas` ในไฟล์ YAML ทับจำนวนที่ HPA ตั้ง และย้ายให้ HPA ดูแลโดยบูธไม่หาย

**ไฟล์:** `lab02-first/10-php-apache.yaml` (มี `replicas: 1`), `lab10-replicas/10-php-apache-hpa.yaml` (ลบ replicas แล้ว)

### ขั้นที่ 1: ทำให้ HPA ถือ 6 บูธ แล้ว apply ไฟล์เดิม

```bash
kubectl -n hpa-load scale deploy/load --replicas=1
until [ "$(kubectl -n hpa-demo get deploy php-apache -o jsonpath={.status.readyReplicas})" = 6 ]; do sleep 3; done; sleep 15
kubectl -n hpa-demo get hpa,deploy; grep -n replicas lab02-first/10-php-apache.yaml
(for i in $(seq 16); do echo "$((i*3))s $(kubectl -n hpa-demo get deploy php-apache --no-headers)"; sleep 3; done &); kubectl apply -f lab02-first/10-php-apache.yaml; sleep 50
```

```text
NAME                                             REFERENCE               TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/php-apache   Deployment/php-apache   cpu: 194%/50%   1         6         6          36m

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/php-apache   6/6     6            6           37m
4:# มี replicas: 1 โดยตั้งใจ — LAB 10 จะใช้ไฟล์นี้สาธิตกับดัก "replicas ใน YAML ทับ HPA"
16:  replicas: 1
namespace/hpa-demo unchanged
deployment.apps/php-apache configured
service/php-apache unchanged
3s php-apache   6/6   6     6     37m
6s php-apache   1/1   1     1     37m
9s php-apache   1/1   1     1     37m
12s php-apache   1/1   1     1     37m
15s php-apache   1/3   3     1     37m
18s php-apache   3/3   3     3     37m
...
30s php-apache   3/4   4     3     37m
33s php-apache   4/4   4     4     37m
...
45s php-apache   4/6   6     4     37m
48s php-apache   6/6   6     6     37m
```

**6 → 1 ทันที** (`deployment.apps/php-apache configured`) 5 บูธปิดพร้อมกัน ลูกค้าที่อยู่ในบูธเหล่านั้นสะดุด แล้ว HPA ค่อย ๆ ดึงกลับ 3 → 4 → 6 (Ready 6 ราว 45 วินาที) ตัวยิงมี `wget -T 2` จึงกลับมายิงต่อได้ (ถ้าไม่มี timeout โหลดจะหายแล้ว HPA ไม่ดึงกลับ — เห็นจริงในการทดลองก่อนเขียนเอกสาร)

### ขั้นที่ 2: ย้ายให้ HPA ดูแล — ลบ replicas จาก last-applied ก่อน

ลบบรรทัด `replicas` ออกจากไฟล์ **อย่างเดียวไม่พอ** `kubectl apply` เทียบ 3 ทาง (ไฟล์ใหม่ / `last-applied-configuration` / ของจริง) ถ้าไฟล์ครั้งก่อนมี `replicas: 1` แต่ไฟล์ใหม่ไม่มี kubectl ถือว่า "ผู้ใช้ลบ field นี้" แล้วลบออกจาก Deployment → กลับเป็นค่าเริ่มต้น **1** ทางที่ถูกคือแก้ last-applied ก่อน

```bash
kubectl -n hpa-demo apply view-last-applied deploy/php-apache | grep -n replicas
kubectl -n hpa-demo apply edit-last-applied deploy/php-apache
```

`edit-last-applied` เปิด vi ให้แก้ annotation (ไม่แตะของจริง) **ลบบรรทัด `  replicas: 1`** (เลื่อนไปที่บรรทัดแล้วกด `dd`) แล้วพิมพ์ `:wq`

```text
8:  replicas: 1
deployment.apps/php-apache edited
```

ตรวจแล้ว apply ไฟล์ที่ลบ replicas

```bash
kubectl -n hpa-demo apply view-last-applied deploy/php-apache | grep -c replicas
kubectl -n hpa-demo get deploy php-apache
diff lab02-first/10-php-apache.yaml lab10-replicas/10-php-apache-hpa.yaml
kubectl apply -f lab10-replicas/10-php-apache-hpa.yaml; sleep 15; kubectl -n hpa-demo get deploy php-apache
```

```text
0
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
php-apache   6/6     6            6           38m
1,4c1,3
< # LAB 2: แอปตัวอย่างจากเอกสาร HPA ทางการ (php-apache): ...
...
16c15
<   replicas: 1
---
>   # ไม่มี replicas: แล้ว — HPA php-apache เป็นคนกำหนดจำนวน Pod (kubectl apply ไฟล์นี้จะไม่แตะจำนวน)
namespace/hpa-demo unchanged
deployment.apps/php-apache unchanged
service/php-apache unchanged
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
php-apache   6/6     6            6           38m
```

`deployment.apps/php-apache unchanged` และยัง **6/6** ตลอด — ย้ายสำเร็จโดยบูธไม่หาย ต่อจากนี้ apply ไฟล์นี้กี่ครั้งก็ไม่แตะจำนวน

> **ไม่ถนัด vi:** ใช้ `kubectl apply set-last-applied -f lab10-replicas/10-php-apache-hpa.yaml` แทน (เขียน last-applied เป็นเนื้อหาของไฟล์ใหม่ทั้งไฟล์ โดยไม่แตะของจริง) ทดสอบแล้วได้ผลเหมือนกัน (`deployment.apps/php-apache configured` แล้ว apply ไฟล์ใหม่ยัง 6/6) — LAB 11 ใช้วิธีนี้กับร้าน
> **ทาง Server-Side Apply** (โอนความเป็นเจ้าของ field `spec.replicas`) อ่านในทฤษฎีหัวข้อ 9

### ลองผิด: apply ไฟล์ที่ลบ replicas "ตรง ๆ" (ผลจริง ไม่ต้องทำตาม)

ทำให้ last-applied กลับมามี `replicas` (apply `lab02-first/10-php-apache.yaml` อีกครั้ง รอ HPA ดึงกลับ 6) แล้ว apply `lab10-replicas/10-php-apache-hpa.yaml` เลยโดยไม่แก้ last-applied

```text
namespace/hpa-demo unchanged
deployment.apps/php-apache configured
service/php-apache unchanged
3s php-apache   6/6   6     6     39m
6s php-apache   1/3   3     1     39m
9s php-apache   3/3   3     3     39m
```

ไฟล์ไม่มี `replicas` แล้ว แต่ **ครั้งแรกที่ apply ยังลดเหลือ 1** (`configured`) เพราะ kubectl ลบ field ตาม last-applied แล้ว HPA ดึงกลับ (เอกสาร HPA ทางการเตือนเรื่องนี้ในหัวข้อ "Migrating Deployments and StatefulSets to horizontal autoscaling")

### ขั้นที่ 3: เก็บกวาด LAB 1–10 (บังคับก่อน LAB 11)

```bash
kubectl delete ns hpa-demo hpa-load
kubectl get ns | grep hpa || echo "ไม่มี ns hpa-* แล้ว"
```

```text
namespace "hpa-demo" deleted
namespace "hpa-load" deleted
ไม่มี ns hpa-* แล้ว
```

metrics-server **เก็บไว้** ใช้ใน LAB 11

### สิ่งที่เห็น

- `replicas` ในไฟล์ + `kubectl apply` = ทับ HPA ทันที (6 → 1)
- ลบ replicas ทั้งจากไฟล์และ last-applied (`edit-last-applied` หรือ `set-last-applied`) แล้ว apply = `unchanged` ไม่มีบูธหาย

**คำถามชวนคิด:** GitOps (เช่น Argo CD) ที่ sync ไฟล์ทุกนาทีจะทะเลาะกับ HPA อย่างไรถ้าไฟล์มี `replicas`

---

## LAB 11: LAB สุดท้าย: ร้านน้องส้มวันลดราคา

<p align="center" id="fig-17">
  <img src="images/17-final-open.png" alt="รูปที่ 17 LAB 11 ภาพรวมวันลดราคา" width="900"><br>
  <em><b>รูปที่ 17</b> LAB สุดท้าย: ร้านจากบท 012 (Traefik + Ingress + TLS) จัดวันลดราคา — หน้าร้าน som-web ให้ HPA ดูแล min 2 max 6 ส่วนครัว som-db-0 คงเดิม</em>
</p>

**เป้าหมาย:** เปลี่ยนหน้าร้านจาก **3 บูธตายตัว รุ่น 1.6** (ท้ายบทที่ 12) เป็น **รุ่น 1.7 ที่ HPA ดูแล min 2 max 6** โดยลูกค้าไม่เจอ error แล้วจัดวันลดราคา: ปล่อยลูกค้าจำลองยิง `https://shop.localhost:30081/api/work` ผ่านประตู Traefik ดูบูธเพิ่มเป็น 6 เห็นชื่อ Pod ต่าง ๆ บนหน้าเว็บและจำนวน server ใน Traefik dashboard แล้วปิดโปรให้บูธลดกลับเป็น 2 ใช้ทุกอย่างที่เรียนมา: Deployment + rolling update + readiness/preStop (บทที่ 7), StatefulSet (บทที่ 8–9), ConfigMap (บทที่ 10), Secret (บทที่ 11), Ingress + Middleware (บทที่ 12), metrics-server + HPA + behavior (บทนี้)

**ไฟล์:** `som-shop-v9/` ทำงานใน `/workspace/013_kubernetes_hpa/02_LAB/som-shop-v9`

**สิ่งที่ต้องมีก่อน:** LAB 0 (image 1.7), LAB 1 (metrics-server) และ LAB 10 ขั้นที่ 3 (ลบ `hpa-demo`, `hpa-load` แล้ว)

| | บทที่ 12 (`som-shop-v8`) | บทที่ 13 (`som-shop-v9`) |
|---|---|---|
| image หน้าร้าน | `som-shop-web:1.6` (`set image` ในขั้น E) | **`som-shop-web:1.7`** (+ `/api/work?ms=N`) |
| จำนวนบูธ | `replicas: 3` ในไฟล์ | **ไม่มี replicas** — HPA `som-web` min 2 max 6 cpu 50% |
| ป้ายร้าน | `⚓ ท่าเรือ Kubernetes · Ingress` | `⚓ ท่าเรือ Kubernetes · HPA` + แถบ `🎉 วันลดราคา! ...` + footer `... LAB 013 · บูธเพิ่ม-ลดเองด้วย HPA ...` |
| ลูกค้าจำลอง | ไม่มี | Deployment `customers` (`curlimages/curl:8.22.0`) เริ่ม `replicas: 0` |
| ครัว / ประตู / หลังร้าน | `som-db`, Traefik, Ingress, `som-admin` | **เหมือนเดิม ไม่แตะ** (ไม่มี HPA กับ db) |

| ไฟล์ใน `som-shop-v9/` | หน้าที่ |
|---|---|
| `k8s/15-config.yaml` | ป้ายร้านบทที่ 13 |
| `k8s/20-web.yaml` | image 1.7 (db-seed + web), **ไม่มี `replicas`**, change-cause `1.7 เพิ่ม /api/work + HPA`, requests cpu 100m / limits 500m, readiness `/api/health`, preStop sleep 5, `maxUnavailable: 0` เดิม |
| `k8s/60-hpa.yaml` | HPA `som-web` min 2 max 6 cpu 50%; scaleUp window 0 + `Pods 2 / 15 วินาที`; scaleDown window **60** + `Pods 1 / 15 วินาที` |
| `k8s/70-customers.yaml` | ลูกค้าจำลอง: วน `curl -sk -m 5 --connect-to shop.localhost:30081:traefik.traefik.svc.cluster.local:443 "https://shop.localhost:30081/api/work?ms=20"` พิมพ์รหัส HTTP ทุกครั้ง (runAsUser 100 ผ่าน restricted) |
| `k8s/00`, `10`, `40`, `50` | เหมือนบทที่ 12 |

### 11.1 ขั้น 0: จุดเริ่มต้น

🐧 **ใน SSH session ของ k8s-lab** (ทั้งสองหน้าต่าง)

```bash
cd /workspace/013_kubernetes_hpa/02_LAB/som-shop-v9
kubectl -n som-shop get deploy,sts,hpa
kubectl -n som-shop apply view-last-applied deploy/som-web | grep -E "replicas|image:|change-cause"
kubectl top pod -n som-shop
curl -sk https://shop.localhost:30081/api/stats
```

```text
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-admin   1/1     1            1           54m
deployment.apps/som-web     3/3     3            3           54m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     54m
    kubernetes.io/change-cause: 1.5 หน้าร้านผ่าน Ingress
  replicas: 3
        image: som-shop-web:1.5
        image: postgres:17.11-alpine
        image: som-shop-web:1.5
NAME                         CPU(cores)   MEMORY(bytes)
som-admin-5f75ddc94b-rrpls   1m           23Mi
som-db-0                     8m           45Mi
som-web-796c88558c-lk9rt     2m           46Mi
som-web-796c88558c-mrv6h     2m           46Mi
som-web-796c88558c-xmg2b     1m           46Mi
som-web-796c88558c-mrv6h 1.6 orders=3 products=6
```

สังเกต: ของจริงเป็น 1.6 แต่ **last-applied ยังจำไฟล์บทที่ 12 (`replicas: 3`, image 1.5)** เพราะ 1.6 มาจาก `kubectl set image` (ไม่ผ่าน apply) และ `replicas: 3` ใน last-applied คือกับดักของ LAB 10 ที่ต้องจัดการในขั้น B ออเดอร์เดิมของนักศึกษาอาจไม่ใช่ 3

> **ถ้าไม่มีร้านจากบทที่ 12** (คลัสเตอร์ใหม่หรือลบ `som-shop` ไปแล้ว) ทำตามนี้แทนขั้น B (ข้าม `set-last-applied`) — ทดสอบจริงแล้วบนคลัสเตอร์ใหม่ (4 CPU)
>
> ```bash
> # postgres (image หลาย platform ใช้ save --platform + image-archive) และ Traefik ของบทที่ 12 (สำเนาใน 02_LAB/ingress-controller)
> docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab; rm -f /root/postgres.tar
> kubectl apply -f ../ingress-controller/traefik-crds-v3.7.13.yml && kubectl apply -f ../ingress-controller/00-traefik.yaml && kubectl -n traefik rollout status deploy/traefik --timeout=180s
> # ซองรหัส 3 ซอง (ค่าตัวอย่างของบทที่ 11–12) + ใบรับรอง self-signed
> kubectl apply -f k8s/00-namespace.yaml
> kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop
> openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.localhost' -addext 'subjectAltName=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost'
> kubectl -n som-shop create secret tls som-tls --cert=tls.crt --key=tls.key
> kubectl -n som-shop create secret generic som-admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow-admin-123
> kubectl apply -f k8s/
> kubectl -n som-shop rollout status sts/som-db --timeout=240s && kubectl -n som-shop rollout status deploy/som-web --timeout=300s
> ```
>
> บนเครื่อง ARM ใช้ `--platform linux/arm64` ร้านใหม่เริ่มที่ `orders=0` และ HPA ทำงานทันที (2 บูธ) แล้วไปขั้น C ได้เลย (`70-customers.yaml` ถูก apply แล้วพร้อม `k8s/`)
>
> ผลจริงบนคลัสเตอร์ใหม่ (4 CPU): โหลด postgres ~20 วินาที, `kubectl apply -f k8s/` ครั้งเดียวได้ทุก object (รวม `horizontalpodautoscaler.autoscaling/som-web created` และ `deployment.apps/customers created`) แล้ว
>
> ```text
> NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
> deployment.apps/customers   0/0     0            0           17s
> deployment.apps/som-admin   1/1     1            1           17s
> deployment.apps/som-web     2/2     2            2           17s
>
> NAME                      READY   AGE
> statefulset.apps/som-db   1/1     17s
>
> NAME                                          REFERENCE            TARGETS              MINPODS   MAXPODS   REPLICAS   AGE
> horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: <unknown>/50%   2         6         2          17s
> som-web-54cf88dbdb-zw9tm 1.7 orders=0 products=6
> ```
>
> (`cpu: <unknown>` ช่วงแรกเป็นเรื่องปกติ หลัง ~1 นาทีได้ `cpu: 3%/50%`) และ customers=1 ก็ดันหน้าร้าน 2 → 4 → 6 ได้ใน ~55 วินาทีเช่นกัน

### 11.2 ขั้น A: แอป 1.7

<p align="center" id="fig-18">
  <img src="images/18-final-app-1-7.png" alt="รูปที่ 18 ขั้น A แอป 1.7" width="900"><br>
  <em><b>รูปที่ 18</b> ขั้น A: build som-shop-web:1.7 (เพิ่ม /api/work?ms=20 = หมุน CPU 20 ms ต่อ request ไม่แตะ db) + kind load docker-image</em>
</p>

image `som-shop-web:1.7` build และ `kind load` แล้วใน LAB 0 ขั้นที่ 4 ตรวจซ้ำได้ด้วย `docker exec lab-worker crictl images | grep som-shop` ดูโค้ด endpoint ใหม่

```bash
sed -n '5,17p' app/app/api/work/route.ts
```

```text
// 1.7: GET /api/work?ms=20 → "som-web-xxxxx 1.7 work=20ms"
// จำลอง "งานหนักของวันลดราคา" (เช่น คิดส่วนลด) = หมุน CPU ms มิลลิวินาทีต่อ 1 request ไม่แตะฐานข้อมูล
// ใช้สร้างโหลด CPU ให้ HPA เห็น (จำกัด 0–200 ms กันพิมพ์ผิดแล้ว Pod ค้าง)
export async function GET(req: Request) {
  const raw = Number(new URL(req.url).searchParams.get('ms') ?? '20');
  const ms = Math.min(Math.max(Number.isFinite(raw) ? Math.round(raw) : 20, 0), 200);
  const start = Date.now();
  let x = 0;
  while (Date.now() - start < ms) x += Math.sqrt(x + 1); // วนคิดเลขเปล่า ๆ = ใช้ CPU จริง
  return new Response(`${os.hostname()} ${process.env.APP_VERSION ?? 'dev'} work=${ms}ms\n`, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}
```

### 11.3 ขั้น B: HPA ก่อน แล้วเปลี่ยนเป็น 1.7 โดยไม่มี replicas

<p align="center" id="fig-19">
  <img src="images/19-final-hpa-yaml.png" alt="รูปที่ 19 ขั้น B HPA และย้าย replicas" width="900"><br>
  <em><b>รูปที่ 19</b> ขั้น B: 60-hpa.yaml min 2 max 6 cpu 50% + behavior (scaleUp Pods 2/15 วิ, scaleDown window 60 วิ ลดทีละ 1/15 วิ) แล้วใช้ kubectl apply set-last-applied ก่อน apply 20-web.yaml ที่ไม่มี replicas → บูธคงที่ 2 ไม่ลดเหลือ 1</em>
</p>

ดูความต่างของ `20-web.yaml` กับบทที่ 12 (ถ้ายังมีโฟลเดอร์ `012_kubernetes_ingress` ใน container) และไฟล์ HPA

```bash
diff ../../../012_kubernetes_ingress/02_LAB/som-shop-v8/k8s/20-web.yaml k8s/20-web.yaml 2>/dev/null | grep -E "^[<>]" | grep -vE "^[<>] *#"
grep -vE "^ *#" k8s/60-hpa.yaml
```

```text
<     kubernetes.io/change-cause: "1.5 หน้าร้านผ่าน Ingress"
>     kubernetes.io/change-cause: "1.7 เพิ่ม /api/work + HPA"
<   replicas: 3
<           image: som-shop-web:1.5
>           image: som-shop-web:1.7
<           image: som-shop-web:1.5    # image เดิมทุกขั้น — เปลี่ยนป้ายร้านโดยไม่ build ใหม่
>           image: som-shop-web:1.7    # 1.7 = 1.6 + /api/work (build ใน LAB 0)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: som-web
  namespace: som-shop
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: som-web
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
  behavior:
    scaleUp:                         # เปิดบูธเพิ่มทันที (ค่าเริ่มต้น window 0)
      stabilizationWindowSeconds: 0
      policies:
        - type: Pods
          value: 2                   # เพิ่มได้ครั้งละไม่เกิน 2 บูธ ต่อ 15 วิ
          periodSeconds: 15
    scaleDown:                       # เฉพาะ LAB: รอ 60 วิ (ค่าเริ่มต้น 300 วิ) แล้วปิดทีละ 1 บูธ ต่อ 15 วิ
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 1
          periodSeconds: 15
```

**1) เปิด HPA ก่อน** (ร้านยังเป็น 1.6) — HPA รับช่วงดูแลจำนวนบูธทันที วันนี้ไม่มีลูกค้า 3 บูธจึงเกินจำเป็น

```bash
kubectl apply -f k8s/60-hpa.yaml
kubectl -n som-shop get hpa
until [ "$(kubectl -n som-shop get deploy som-web -o jsonpath={.spec.replicas})" = 2 ]; do sleep 3; done
kubectl -n som-shop get events --field-selector involvedObject.kind=HorizontalPodAutoscaler,reason=SuccessfulRescale | tail -1
```

```text
horizontalpodautoscaler.autoscaling/som-web created
NAME      REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 1%/50%   2         6         3          0s
1s          Normal   SuccessfulRescale   horizontalpodautoscaler/som-web   New size: 2; reason: All metrics below target
```

ได้ % ทันที (Pod เดิมมี metric อยู่แล้ว) แล้วลด **3 → 2 ราว 61 วินาทีหลัง apply** (window 60 วินาที) หยุดที่ `minReplicas: 2`

**2) ลบ replicas ออกจาก last-applied** (บทเรียนจาก LAB 10) ด้วย `set-last-applied` จากไฟล์ใหม่ — แก้แค่ annotation ยังไม่เปลี่ยนของจริง

```bash
kubectl apply set-last-applied -f k8s/20-web.yaml
kubectl -n som-shop apply view-last-applied deploy/som-web | grep -cE "^  replicas:"
kubectl -n som-shop get deploy som-web
```

```text
deployment.apps/som-web configured
service/som-web configured
0
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
som-web   2/2     2            2           55m
```

**3) apply ป้ายร้านบทที่ 13 + หน้าร้าน 1.7 ระหว่างที่ `hit.sh` ยิงผ่าน Ingress** (`-q` พิมพ์ `.` สำเร็จ / `x` ล้ม)

```bash
(sleep 2; kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml) & ./hit.sh -q https://shop.localhost:30081/api/whoami 400 0.05; wait
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
kubectl -n som-shop get hpa; kubectl -n som-shop rollout history deploy/som-web
```

```text
...................................configmap/som-web-config configured
configmap/som-announcement unchanged
.deployment.apps/som-web configured
.service/som-web configured
.........................................................................................................
จำนวน  Pod  เวอร์ชัน
    172 1.6 (เวอร์ชัน)
    228 1.7 (เวอร์ชัน)
ok=400 err=0 (ใช้เวลา 24.7 วินาที)
deployment "som-web" successfully rolled out
NAME      REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          101s
deployment.apps/som-web
REVISION  CHANGE-CAUSE
1         1.5 หน้าร้านผ่าน Ingress
2         1.5 หน้าร้านผ่าน Ingress
3         1.6 ผ่าน Ingress
4         1.7 เพิ่ม /api/work + HPA
```

ระหว่าง rollout ดู `kubectl -n som-shop get deploy som-web` ทุก 2 วินาทีได้ `2/2 → 3/2 (บูธใหม่ surge 1) → 2/2` **ไม่เคยต่ำกว่า 2** `ok=400 err=0` ตรวจป้ายใหม่และ endpoint ใหม่

```bash
curl -sk https://shop.localhost:30081/ | grep -o "Kubernetes LAB 01[0-9][^<]*" | head -1
curl -sk https://shop.localhost:30081/ | grep -o "🎉 วันลดราคา[^<]*" | head -1
curl -sk "https://shop.localhost:30081/api/work?ms=20"; curl -sk "https://shop.localhost:30081/api/work?ms=5000"
```

```text
Kubernetes LAB 013 · บูธเพิ่ม-ลดเองด้วย HPA https://shop.localhost
🎉 วันลดราคา! ลูกค้าเยอะแค่ไหน HPA ก็เปิดบูธเพิ่มให้
som-web-869b965df4-98b8r 1.7 work=20ms
som-web-869b965df4-5hpm6 1.7 work=200ms
```

`ms=5000` ถูกจำกัดเหลือ 200 (กันพิมพ์ผิดแล้ว Pod ค้าง) ป้ายใหม่มีผลทันทีเพราะ image เปลี่ยน = Pod ใหม่ทุกตัว (ไม่ต้อง `rollout restart` แยก)

🌐 **ตรวจใน browser:** เปิด `http://shop.localhost:30080` (ถูกส่งต่อไป `https://shop.localhost:30081`) จะเห็นแถบโปรโมชันใหม่และเวอร์ชัน 1.7 กด refresh หลายครั้ง แถบ `เสิร์ฟโดย Pod:` สลับไปมาระหว่าง **2 ชื่อ** (HPA ถือ 2 บูธ) ภาพหน้าจอจริงข้างล่าง (และทุกภาพในโฟลเดอร์ `images/screenshots/`) ถ่ายด้วย Chromium ที่เปิด URL เดียวกับนักศึกษาบนเครื่องทดลองที่จำกัด 4 CPU

<p align="center" id="fig-20">
  <img src="images/screenshots/20261005_2357_lab11hpa_01-shop-before-sale-2-booths.png" alt="รูปที่ 20 ภาพหน้าจอจริง หน้าร้าน 1.7 ก่อนวันลดราคา 2 บูธ" width="800"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: ก่อนวันลดราคา หน้าร้านเวอร์ชัน 1.7 มีแถบ &quot;🎉 วันลดราคา! ลูกค้าเยอะแค่ไหน HPA ก็เปิดบูธเพิ่มให้&quot; หัวเว็บ &quot;⚓ ท่าเรือ Kubernetes · HPA&quot; และ &quot;เสิร์ฟโดย Pod: som-web-869b965df4-98b8r · เวอร์ชัน 1.7&quot; — refresh 12 ครั้งเห็นชื่อ Pod 2 ชื่อ (HPA ถือ 2 บูธ)</em>
</p>

> **ถ้าข้าม `set-last-applied`** (apply `20-web.yaml` ตรง ๆ) kubectl จะลบ `replicas` ตาม last-applied → หน้าร้านลดเหลือ **1** ชั่วครู่ แล้ว HPA ดึงกลับเป็น 2 (`Current number of replicas below Spec.MinReplicas`) ในการทดลองก่อนเขียนเอกสารยังได้ `err=0` เพราะ `maxUnavailable: 0` + preStop แต่ร้านเหลือบูธเดียวช่วงสั้น ๆ — ไม่ควรทำกับร้านจริง

### 11.4 ขั้น C: ลูกค้าจำลอง

<p align="center" id="fig-21">
  <img src="images/20-final-customers.png" alt="รูปที่ 21 ขั้น C ลูกค้าจำลอง" width="900"><br>
  <em><b>รูปที่ 21</b> ขั้น C: 70-customers.yaml (curlimages/curl) ยิง https://shop.localhost:30081/api/work ผ่าน Traefik ด้วย --connect-to; ถ้าลืม :30081 ได้ 301 ทุกครั้ง (redirect-https)</em>
</p>

```bash
grep -A4 'while true' k8s/70-customers.yaml
kubectl apply -f k8s/70-customers.yaml; kubectl -n som-shop get deploy customers
```

```text
              while true; do
                curl -sk -o /dev/null -m 5 -w '%{http_code}\n' \
                  --connect-to shop.localhost:30081:traefik.traefik.svc.cluster.local:443 \
                  "https://shop.localhost:30081/api/work?ms=20" || echo fail
              done
deployment.apps/customers created
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
customers   0/0     0            0           0s
```

`--connect-to` = ต่อ TCP ไปที่ Service `traefik:443` ในคลัสเตอร์ แต่ URL, SNI และ `Host` ยังเป็น `shop.localhost:30081` **เหมือนลูกค้าเปิดจาก browser** จึงผ่านป้าย Ingress, TLS และ Middleware เดียวกับลูกค้าจริง

**ลองผิด: ลืม `:30081`** (ทดสอบจากเครื่อง k8s-lab ด้วยหลักการเดียวกัน)

```bash
curl -sk -o /dev/null -w "%{http_code} %{redirect_url}\n" --connect-to shop.localhost:443:127.0.0.1:30081 "https://shop.localhost/api/work?ms=20"
curl -sk -w "  %{http_code}\n" "https://shop.localhost:30081/api/work?ms=20"
```

```text
301 https://shop.localhost:30081/api/work?ms=20
som-web-869b965df4-5hpm6 1.7 work=20ms
  200
```

ไม่มี `:30081` = `Host: shop.localhost` (พอร์ต 443) Middleware `redirect-https` ของบทที่ 12 จึงส่งต่อไป `:30081` ทุกครั้ง (`301`) ลูกค้าแบบนั้นจะไม่ทำให้ CPU ขึ้นเลย (การทดลองก่อนเขียนเอกสาร: 2000/2000 ครั้งได้ 301, CPU 12%, HPA ไม่ scale)

### 11.5 ขั้น D: วันลดราคา — scale up

<p align="center" id="fig-22">
  <img src="images/21-final-scale-up.png" alt="รูปที่ 22 ขั้น D scale up" width="900"><br>
  <em><b>รูปที่ 22</b> ขั้น D: kubectl scale deploy/customers --replicas=1 (เครื่อง 4 core; เครื่อง 8 core ใช้ 2 ได้) → CPU 206–370% → HPA 2 → 4 → 6 ใน ~45 วิ (เพิ่มทีละ 2 ตาม policy) แล้วนิ่งที่ 6 (~125%)</em>
</p>

> **จำนวนลูกค้า:** 1 Pod `customers` = ลูกค้า 1 คนกดไม่หยุด (~30 ครั้ง/วินาที) **เครื่อง 4 core ใช้ `--replicas=1`** (ทดสอบแล้วถึง 6 บูธ, เครื่องทั้งหมดใช้ CPU ราว 1.7–2.6 core จาก 4) **เครื่อง 8 core ขึ้นไปใช้ `--replicas=2` ได้** (ทดสอบบน 4 CPU แล้วก็ยังได้ `err=0` แต่ใช้ CPU ถึง ~3.3 core จาก 4 เครื่องจะหน่วง)

🐧 **หน้าต่างที่ 1** (โฟลเดอร์ `som-shop-v9`)

```bash
../watch-hpa.sh som-shop som-web 420
```

🐧 **หน้าต่างที่ 2** — ยิงหน้าร้านผ่าน Ingress ทิ้งไว้เบื้องหลัง (1200 ครั้ง ห่าง 0.1 วินาที ≈ 2 นาที) แล้วปล่อยลูกค้า

```bash
./hit.sh -q https://shop.localhost:30081/api/whoami 1200 0.1 > hit-up.log 2>&1 &
kubectl -n som-shop scale deploy/customers --replicas=1
```

ผลจริงของหน้าต่างที่ 1 (เริ่มปล่อยลูกค้าที่วินาทีที่ ~3)

```text
   0s  14%/50% replicas=2 ready=2
...
  31s  10%/50% replicas=2 ready=2
  36s  206%/50% replicas=2 ready=4
  41s  206%/50% replicas=2 ready=4
  46s  206%/50% replicas=2 ready=4
  51s  370%/50% replicas=4 ready=6
  56s  370%/50% replicas=4 ready=6
  61s  370%/50% replicas=4 ready=6
  66s  219%/50% replicas=6 ready=6
...
 117s  127%/50% replicas=6 ready=6
 142s  122%/50% replicas=6 ready=6
```

Event ของ HPA: `New size: 4` ราว 29 วินาทีหลังปล่อยลูกค้า และ `New size: 6` ราว 44 วินาที (**เพิ่มทีละ 2** ตาม policy แม้สูตรอยากได้มากกว่า) **Ready 6 ราว 48–50 วินาที** คอลัมน์ `replicas=` ช้ากว่า `ready=` (status ของ HPA อัปเดตรอบถัดไป) ดูรายละเอียดระหว่างนั้น (ราว 2 นาทีหลังปล่อยลูกค้า)

```bash
kubectl -n som-shop get hpa som-web; kubectl top pod -n som-shop -l app=som-web; kubectl top pod -n som-shop -l app=customers
kubectl -n som-shop get pod -l app=som-web -o wide
```

```text
NAME      REFERENCE            TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 127%/50%   2         6         6          4m16s
NAME                       CPU(cores)   MEMORY(bytes)
som-web-869b965df4-5hpm6   129m         57Mi
som-web-869b965df4-6c5tl   123m         47Mi
som-web-869b965df4-98b8r   124m         56Mi
som-web-869b965df4-h8rtv   124m         47Mi
som-web-869b965df4-kcrtl   133m         47Mi
som-web-869b965df4-vsj9p   129m         48Mi
NAME                         CPU(cores)   MEMORY(bytes)
customers-5d84b48bbd-75542   246m         4Mi
NAME                       READY   STATUS    RESTARTS   AGE     IP            NODE
som-web-869b965df4-5hpm6   1/1     Running   0          2m57s   10.244.2.48   lab-worker2
som-web-869b965df4-6c5tl   1/1     Running   0          91s     10.244.1.48   lab-worker
som-web-869b965df4-98b8r   1/1     Running   0          2m51s   10.244.1.47   lab-worker
som-web-869b965df4-h8rtv   1/1     Running   0          76s     10.244.1.49   lab-worker
som-web-869b965df4-kcrtl   1/1     Running   0          76s     10.244.2.51   lab-worker2
som-web-869b965df4-vsj9p   1/1     Running   0          91s     10.244.2.50   lab-worker2
```

- ลูกค้า 1 คนดันหน้าร้าน 2 บูธไปถึง **370%** → HPA 2 → 4 → 6 แล้วนิ่ง **~125m ต่อบูธ (≈125%)** ยังเกินเป้า 50% → `TooManyReplicas` (เพดาน 6)
- บูธกระจาย 2 worker ลำละ 3 — **2 บูธเดิม (AGE 2m5x) + 4 บูธใหม่ (AGE 76–91s)**
- ถ้าใช้ `--replicas=2` (แนะนำสำหรับเครื่อง 8 core) ผลจริงบนเครื่องทดลอง 4 CPU: CPU ขึ้นถึง ~494% → 2 → 4 → 6 เหมือนกัน แล้วนิ่ง ~240% (~240m ต่อบูธ) ยัง `err=0` แต่เครื่องใช้ CPU ราว 3.3 core จาก 4
- Event `Readiness probe failed: ... connect: connection refused` ของบูธใหม่ตอนเพิ่งเกิด (แอปยังไม่เปิดพอร์ต 3000) เป็นเรื่องปกติ readinessProbe กันไม่ให้ลูกค้าถูกส่งไปบูธที่ยังไม่พร้อม

ต้องการดูแบบ HPA เองก็ได้ (พิมพ์เมื่อค่าเปลี่ยน ไม่มีเวลา): `kubectl -n som-shop get hpa som-web -w` (Ctrl+C เพื่อออก)

```text
NAME      REFERENCE            TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 10%/50%   2         6         2          2m30s
som-web   Deployment/som-web   cpu: 206%/50%   2         6         2          2m45s
som-web   Deployment/som-web   cpu: 370%/50%   2         6         4          3m
som-web   Deployment/som-web   cpu: 219%/50%   2         6         6          3m15s
som-web   Deployment/som-web   cpu: 150%/50%   2         6         6          3m30s
som-web   Deployment/som-web   cpu: 131%/50%   2         6         6          3m45s
som-web   Deployment/som-web   cpu: 127%/50%   2         6         6          4m
```

### 11.6 ขั้น E: หน้าเว็บเห็นบูธใหม่

<p align="center" id="fig-23">
  <img src="images/22-final-pod-names.png" alt="รูปที่ 23 ขั้น E ชื่อ Pod บนหน้าเว็บ" width="900"><br>
  <em><b>รูปที่ 23</b> ขั้น E: เปิดหน้าร้านซ้ำ ๆ เห็น 'เสิร์ฟโดย Pod: som-web-…' เปลี่ยนไป 5–6 ชื่อ — ลูกค้าถูกกระจายไปบูธใหม่ทันทีที่ไฟเขียว</em>
</p>

ขณะที่ยังมีลูกค้า (ภายใน 2 นาทีหลังปล่อย)

```bash
for i in $(seq 12); do curl -sk https://shop.localhost:30081/ | grep -o 'เสิร์ฟโดย Pod: <!-- -->[^<]*\|เสิร์ฟโดย Pod: [^<·]*' | head -1; done | sort | uniq -c
```

```text
      6 เสิร์ฟโดย Pod: som-web-869b965df4-5hpm6
      1 เสิร์ฟโดย Pod: som-web-869b965df4-6c5tl
      1 เสิร์ฟโดย Pod: som-web-869b965df4-98b8r
      3 เสิร์ฟโดย Pod: som-web-869b965df4-kcrtl
      1 เสิร์ฟโดย Pod: som-web-869b965df4-vsj9p
```

12 ครั้งตกไป 5 บูธ (อีกรอบที่ใช้ customers=2 เห็นครบ 6 ชื่อ) — Traefik สลับบูธ **ทุก request** (round-robin) แต่ลูกค้าจำลองแทรกคิวอยู่ตลอด ตัวเลขจึงไม่เท่ากันพอดี 🌐 **browser:** เปิด `https://shop.localhost:30081/` แล้วกด refresh หลายครั้ง แถบ `🐱 เสิร์ฟโดย Pod: ...` ใต้ชื่อร้านจะเปลี่ยนไปเรื่อย ๆ (ทดสอบด้วย curl แล้ว: แม้ใช้ connection เดิมซ้ำ `Re-using existing connection` ก็ได้ Pod สลับกันทุกครั้ง)

**รอบถ่ายภาพหน้าจอ** (ทำซ้ำอีกรอบด้วย `customers=1` บนเครื่องเดิม เพื่อถ่ายภาพ browser) ผลของ `kubectl -n som-shop get hpa som-web` ทุก 10 วินาทีหลังปล่อยลูกค้า

```text
$ kubectl -n som-shop scale deploy/customers --replicas=1
deployment.apps/customers scaled
--- +10s
som-web   Deployment/som-web   cpu: 2%/50%   2     6     2     30m
--- +20s
som-web   Deployment/som-web   cpu: 16%/50%   2     6     2     30m
--- +30s
som-web   Deployment/som-web   cpu: 235%/50%   2     6     2     30m
--- +40s
som-web   Deployment/som-web   cpu: 235%/50%   2     6     2     31m
--- +50s
som-web   Deployment/som-web   cpu: 353%/50%   2     6     4     31m
--- +60s
som-web   Deployment/som-web   cpu: 202%/50%   2     6     6     31m
...
--- +80s
som-web   Deployment/som-web   cpu: 139%/50%   2     6     6     31m
$ kubectl -n som-shop get pods -l app=som-web
NAME                       READY   STATUS    RESTARTS   AGE
som-web-869b965df4-5hpm6   1/1     Running   0          30m
som-web-869b965df4-98b8r   1/1     Running   0          30m
som-web-869b965df4-dggqb   1/1     Running   0          39s
som-web-869b965df4-mqrdv   1/1     Running   0          54s
som-web-869b965df4-vrht4   1/1     Running   0          39s
som-web-869b965df4-wh5s2   1/1     Running   0          54s
```

HPA เห็น CPU 235% → 353% แล้วสั่ง 2 → 4 → 6 ภายใน ~50–60 วินาที (บูธใหม่ 2 ชุด AGE 54s และ 39s ห่างกัน 15 วินาทีตาม policy `Pods 2 / 15 วินาที`) จากนั้น refresh หน้าร้านใน browser 12 ครั้งเห็นชื่อ Pod **ครบ 6 ชื่อ**

<p align="center" id="fig-24">
  <img src="images/screenshots/20261005_2357_lab11hpa_03-shop-during-sale-6-booths.png" alt="รูปที่ 24 ภาพหน้าจอจริง หน้าร้านระหว่างวันลดราคา 6 บูธ" width="800"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: ระหว่างวันลดราคา (customers=1, HPA สั่ง 2 → 4 → 6) หน้าเว็บเหมือนเดิมทุกอย่าง ต่างแค่ชื่อในแถบ &quot;เสิร์ฟโดย Pod&quot; ที่เปลี่ยนไปตามบูธที่ตอบ — refresh 12 ครั้งในรอบถ่ายภาพเห็นชื่อ Pod ครบ 6 ชื่อ (ภาพนี้เป็นหนึ่งในนั้น) ลูกค้าไม่รู้เลยว่าร้านเพิ่มบูธ</em>
</p>

### 11.7 ขั้น F: Traefik dashboard

<p align="center" id="fig-25">
  <img src="images/23-final-traefik-dashboard.png" alt="รูปที่ 25 ขั้น F Traefik dashboard" width="900"><br>
  <em><b>รูปที่ 25</b> ขั้น F: Traefik dashboard (http://localhost:30082) หน้า HTTP Services: som-shop-som-web-80@kubernetes มี server เพิ่มเป็น 6 แล้วกลับเป็น 2</em>
</p>

```bash
curl -s localhost:30082/api/http/services | python3 -c "import json,sys; [print(s['name'], len(s.get('loadBalancer',{}).get('servers',[])), 'servers') for s in json.load(sys.stdin) if 'som-web' in s['name']]"
```

```text
som-shop-som-web-80@kubernetes 6 servers
```

🌐 เปิด `http://localhost:30082/dashboard/` → **HTTP** → **Services** → `som-shop-som-web-80@kubernetes` ช่อง Servers แสดง IP:3000 ของทุกบูธที่ Ready Traefik อ่าน EndpointSlice เอง บูธใหม่จึงถูกเพิ่มเข้าประตูโดยไม่ต้องแก้ป้าย Ingress หลังปิดโปร (ขั้น H) จะเหลือ `2 servers`

เทียบภาพหน้าจอจริงของหน้าเดียวกันก่อนและระหว่างวันลดราคา (ตัวเลข `6` ที่เมนู **HTTP Services** ด้านซ้ายคือจำนวน Service ทั้งหมดใน Traefik ไม่ใช่จำนวนบูธ — จำนวนบูธดูที่ตาราง **Servers**)

<p align="center" id="fig-26">
  <img src="images/screenshots/20261005_2357_lab11hpa_02-traefik-2-servers.png" alt="รูปที่ 26 ภาพหน้าจอจริง Traefik dashboard 2 servers" width="800"><br>
  <em><b>รูปที่ 26</b> ภาพหน้าจอจริงจากการทดลอง: Traefik dashboard (http://localhost:30082/dashboard/) → HTTP Services → som-shop-som-web-80@kubernetes ก่อนวันลดราคา ตาราง Servers มี 2 แถว (IP:3000 ของ 2 บูธ) สถานะ UP ทั้งคู่</em>
</p>

<p align="center" id="fig-27">
  <img src="images/screenshots/20261005_2357_lab11hpa_04-traefik-6-servers.png" alt="รูปที่ 27 ภาพหน้าจอจริง Traefik dashboard 6 servers" width="800"><br>
  <em><b>รูปที่ 27</b> ภาพหน้าจอจริงจากการทดลอง: ระหว่างวันลดราคา som-shop-som-web-80@kubernetes มี 6 servers — dashboard แสดงทีละ 5 แถวพร้อม &quot;Page 1 of 2&quot; (แถวที่ 6 อยู่หน้า 2) บูธใหม่ถูกเพิ่มเข้าประตูเองโดยไม่ต้องแก้ป้าย Ingress</em>
</p>

### 11.8 ขั้น G: ลูกค้าไม่เจอ error

<p align="center" id="fig-28">
  <img src="images/24-final-no-errors.png" alt="รูปที่ 28 ขั้น G ไม่มี error" width="900"><br>
  <em><b>รูปที่ 28</b> ขั้น G: hit.sh -q ยิงหน้าร้านผ่าน Ingress ตลอดช่วงเพิ่มบูธ ok=1200 err=0 และช่วงลดบูธ ok=1500 err=0 (readiness + preStop sleep 5) — customers เองก็ได้ 200 ทั้งหมด</em>
</p>

รหัส HTTP ที่ลูกค้าจำลองได้ทั้งหมด และสุขภาพของบูธ

```bash
for p in $(kubectl -n som-shop get pod -l app=customers -o name); do kubectl -n som-shop logs $p --tail=100000; done | sort | uniq -c
kubectl -n som-shop get pod -l app=som-web -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount,READY:.status.containerStatuses[0].ready
```

```text
   3784 200
NAME                       RESTARTS   READY
som-web-869b965df4-5hpm6   0          true
som-web-869b965df4-6c5tl   0          true
som-web-869b965df4-98b8r   0          true
som-web-869b965df4-h8rtv   0          true
som-web-869b965df4-kcrtl   0          true
som-web-869b965df4-vsj9p   0          true
```

ลูกค้าจำลองได้ `200` ทั้งหมด (ไม่มี `fail`, `000` หรือ 5xx) บูธไม่ restart เลย (เครื่อง 4 CPU ไม่หน่วงจน probe ล้ม) ผลของ `hit.sh` ช่วงขาขึ้น (`hit-up.log`) ดูหลังขั้น H

### 11.9 ขั้น H: ปิดโปร — scale down

<p align="center" id="fig-29">
  <img src="images/25-final-scale-down.png" alt="รูปที่ 29 ขั้น H scale down" width="900"><br>
  <em><b>รูปที่ 29</b> ขั้น H: scale customers 0 → CPU ลดใน ~45–60 วิ → นาฬิกาทราย 60 วิ → ปิดทีละ 1 บูธทุก 15 วิ 6 → 5 → 4 → 3 → 2 รวม ~2–3 นาที (วัดได้ 2 นาที และ 2 นาที 45 วิ) แล้วหยุดที่ minReplicas 2 (TooFewReplicas)</em>
</p>

🐧 หน้าต่างที่ 2 (หน้าต่างที่ 1 ยังรัน `watch-hpa.sh`)

```bash
kubectl -n som-shop scale deploy/customers --replicas=0
wait; cat hit-up.log | tail -3
./hit.sh -q https://shop.localhost:30081/api/whoami 1500 0.1 | tail -3
```

```text
deployment.apps/customers scaled
จำนวน  Pod  เวอร์ชัน
   1200 1.7 (เวอร์ชัน)
ok=1200 err=0 (ใช้เวลา 133.5 วินาที)
จำนวน  Pod  เวอร์ชัน
   1500 1.7 (เวอร์ชัน)
ok=1500 err=0 (ใช้เวลา 166.9 วินาที)
```

ผลจริงของหน้าต่างที่ 1 (หยุดลูกค้าที่วินาทีที่ ~125)

```text
 122s  127%/50% replicas=6 ready=6
 153s  122%/50% replicas=6 ready=6
 158s  12%/50% replicas=6 ready=6
 168s  7%/50% replicas=6 ready=6
 193s  6%/50% replicas=6 ready=6
 198s  6%/50% replicas=6 ready=5
 213s  6%/50% replicas=5 ready=4
 229s  6%/50% replicas=4 ready=3
 244s  8%/50% replicas=3 ready=2
 259s  9%/50% replicas=2 ready=2
 300s  14%/50% replicas=2 ready=2
```

```bash
kubectl -n som-shop get hpa som-web
kubectl -n som-shop describe hpa som-web | sed -n '/Conditions/,$p'
curl -s localhost:30082/api/http/services | python3 -c "import json,sys; [print(s['name'], len(s.get('loadBalancer',{}).get('servers',[])), 'servers') for s in json.load(sys.stdin) if 'som-web' in s['name']]"
```

```text
NAME      REFERENCE            TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 12%/50%   2         6         2          7m17s
Conditions:
  Type            Status  Reason            Message
  ----            ------  ------            -------
  AbleToScale     True    ReadyForNewScale  recommended size matches current size
  ScalingActive   True    ValidMetricFound  the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
  ScalingLimited  True    TooFewReplicas    the desired replica count is less than the minimum replica count
  ScaledToZero    False   NotScaledToZero   the HPA controller did not scale the workload to zero
Events:
  Type     Reason                        Age                  From                       Message
  ----     ------                        ----                 ----                       -------
...
  Normal   SuccessfulRescale             4m32s                horizontal-pod-autoscaler  New size: 4; reason: cpu resource utilization (percentage of request) above target
  Normal   SuccessfulRescale             4m17s                horizontal-pod-autoscaler  New size: 6; reason: cpu resource utilization (percentage of request) above target
  Normal   SuccessfulRescale             106s                 horizontal-pod-autoscaler  New size: 5; reason: All metrics below target
  Normal   SuccessfulRescale             91s                  horizontal-pod-autoscaler  New size: 4; reason: All metrics below target
  Normal   SuccessfulRescale             76s                  horizontal-pod-autoscaler  New size: 3; reason: All metrics below target
  Normal   SuccessfulRescale             61s (x2 over 6m17s)  horizontal-pod-autoscaler  New size: 2; reason: All metrics below target
som-shop-som-web-80@kubernetes 2 servers
```

- CPU ตกให้เห็นราว **33 วินาที** หลังหยุด → นาฬิกาทราย 60 วินาที → **6 → 5 → 4 → 3 → 2 ห่างกัน 15 วินาที** ถึง 2 ราว **2 นาที** หลังหยุดลูกค้า (Event `New size: 5` ~73 วินาที, `New size: 2` ~118 วินาที)
- หยุดที่ `minReplicas` → `ScalingLimited True TooFewReplicas` (CPU 12% อยากได้ 1 แต่ร้านต้องมีอย่างน้อย 2 บูธ)
- ตลอดการลด `hit.sh` ได้ **`ok=1500 err=0`** บูธที่ถูกปิดผ่าน preStop 5 วินาทีก่อน (Traefik ลบออกจากรายชื่อทัน) ขาขึ้นก็ **`ok=1200 err=0`**
- Traefik เหลือ `2 servers`

**รอบถ่ายภาพหน้าจอ** (ขาลงของรอบที่สอง) ผลของ `kubectl -n som-shop get hpa som-web` ทุก 15 วินาทีหลังหยุดลูกค้า

```text
$ kubectl -n som-shop scale deploy/customers --replicas=0
deployment.apps/customers scaled
--- +15s som-web   Deployment/som-web   cpu: 125%/50%   2     6     6     32m
--- +30s som-web   Deployment/som-web   cpu: 119%/50%   2     6     6     32m
--- +45s som-web   Deployment/som-web   cpu: 61%/50%   2     6     6     32m
--- +61s som-web   Deployment/som-web   cpu: 3%/50%   2     6     6     32m
--- +76s som-web   Deployment/som-web   cpu: 2%/50%   2     6     6     33m
--- +91s som-web   Deployment/som-web   cpu: 2%/50%   2     6     6     33m
--- +106s som-web   Deployment/som-web   cpu: 2%/50%   2     6     6     33m
--- +121s som-web   Deployment/som-web   cpu: 1%/50%   2     6     5     33m
--- +136s som-web   Deployment/som-web   cpu: 2%/50%   2     6     4     34m
--- +151s som-web   Deployment/som-web   cpu: 2%/50%   2     6     3     34m
--- +166s som-web   Deployment/som-web   cpu: 3%/50%   2     6     2     34m
```

รอบนี้มิเตอร์เห็น CPU ตกช้ากว่า (~45–60 วินาที) จึงถึง 2 บูธราว **2 นาที 45 วินาที** หลังหยุด (รอบแรก ~2 นาที) — **เวลาขาลงของร้านอยู่ในช่วงราว 2–3 นาที** ขึ้นกับจังหวะรอบจดมิเตอร์ ลำดับเหมือนกันทุกรอบ: มิเตอร์ตก → นาฬิกาทราย 60 วินาที → ปิดทีละ 1 บูธทุก 15 วินาที

<p align="center" id="fig-30">
  <img src="images/screenshots/20261005_2357_lab11hpa_05-traefik-back-to-2-servers.png" alt="รูปที่ 30 ภาพหน้าจอจริง Traefik dashboard กลับเป็น 2 servers" width="800"><br>
  <em><b>รูปที่ 30</b> ภาพหน้าจอจริงจากการทดลอง: หลังหยุดลูกค้า (customers=0) HPA ปิดบูธ 6 → 5 → 4 → 3 → 2 ทีละ 15 วิ รวม ~2 นาที 45 วิ แล้ว som-shop-som-web-80@kubernetes กลับเป็น 2 servers — IP เดียวกับก่อนวันลดราคา เพราะบูธที่ถูกปิดก่อนคือบูธใหม่ล่าสุด 2 บูธเดิมยังอยู่</em>
</p>

### 11.10 ขั้น I: ครัวไม่ถูก scale และออเดอร์ยังอยู่

<p align="center" id="fig-31">
  <img src="images/26-final-db-stays.png" alt="รูปที่ 31 ขั้น I ครัวคงเดิม" width="900"><br>
  <em><b>รูปที่ 31</b> ขั้น I: ตลอดวันลดราคา som-db 1/1 ไม่เปลี่ยน — HPA เพิ่มเฉพาะหน้าร้าน stateless ส่วน postgres ตัวเดียวรับเขียน (scale db ต้องใช้ replication ไม่ใช่ HPA)</em>
</p>

```bash
kubectl -n som-shop get sts som-db; kubectl -n som-shop get hpa
curl -sk -XPOST -H "content-type: application/json" -d '{"product_id":4,"qty":1}' https://shop.localhost:30081/api/orders; echo
curl -sk https://shop.localhost:30081/api/stats; curl -sk -u som:meow-admin-123 https://admin.localhost:30081/stats
curl -sk -o /dev/null -w "%{http_code}\n" https://admin.localhost:30081/stats
```

```text
NAME     READY   AGE
som-db   1/1     78m
NAME      REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          23m
{"ok":true,"order_id":4,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":56}}
som-web-869b965df4-5hpm6 1.7 orders=4 products=6
som-web-869b965df4-98b8r 1.7 orders=4 products=6
401
```

`som-db 1/1` ตลอด มี HPA แค่ `som-web` ออเดอร์เดิม (3 รายการของการทดลอง) อยู่ครบและสั่งเพิ่มได้ `order_id 4` หลังร้านยังต้องใช้บัตร (ไม่มีบัตร `401`) — ใช้ `-k` เพราะ `tls.crt` อยู่ในโฟลเดอร์ `som-shop-v8` ของบทที่ 12 (ตรวจใบจริงได้ด้วย `--cacert ../../../012_kubernetes_ingress/02_LAB/som-shop-v8/tls.crt`)

### 11.11 ตรวจรับร้านและปิดบท

<p align="center" id="fig-32">
  <img src="images/27-final-checklist.png" alt="รูปที่ 32 ตรวจรับวันลดราคา" width="900"><br>
  <em><b>รูปที่ 32</b> ตรวจรับวันลดราคา: HPA min 2 max 6, scale up ถึง 6, หน้าเว็บเห็นหลาย Pod, Traefik เห็น server เพิ่ม, err=0, ลดกลับ 2, db ไม่ถูก scale</em>
</p>

| ข้อตรวจรับ | ผลจริง (4 CPU, customers=1) |
|---|---|
| HPA min 2 max 6 | `som-web 2 6`, ไม่มี HPA กับ `som-db`/`som-admin` |
| ย้าย 1.6 → 1.7 + ลบ replicas | `set-last-applied` → apply: บูธไม่ต่ำกว่า 2, `ok=400 err=0`, revision 4 `1.7 เพิ่ม /api/work + HPA` |
| scale up ถึง 6 | 2 → 4 → 6 ใน ~45 วินาที (Ready 6 ~50 วินาที) peak 370% นิ่ง ~125% |
| หน้าเว็บเห็นหลาย Pod | 5 ชื่อใน 12 ครั้ง (curl รอบแรก) / ครบ 6 ชื่อ (browser รอบถ่ายภาพหน้าจอ) |
| Traefik เห็น server เพิ่ม | `som-shop-som-web-80@kubernetes 6 servers` → `2 servers` |
| ลูกค้าไม่เจอ error | ขาขึ้น `ok=1200 err=0`, ขาลง `ok=1500 err=0`, customers `200` ทั้งหมด, RESTARTS 0 |
| ลดกลับ 2 | ~2–3 นาทีหลังหยุด (วัดได้ ~2 นาที และ ~2 นาที 45 วินาที) ทีละ 1 บูธ / 15 วินาที, `TooFewReplicas` |
| db ไม่ถูก scale | `som-db 1/1`, ออเดอร์ครบ |

<p align="center" id="fig-33">
  <img src="images/28-wrap-up-next.png" alt="รูปที่ 33 ปิดบท" width="900"><br>
  <em><b>รูปที่ 33</b> ปิดบท: ติดตั้ง metrics-server/Traefik/ร้านเป็นแพ็กเกจเดียว (Helm), ขยายขนาดบูธอัตโนมัติ (VPA), เรียกเรือเพิ่ม (Cluster Autoscaler), ปลุกบูธตามคิวออเดอร์ (KEDA)</em>
</p>

ร้านน้องส้มเพิ่ม/ลดบูธเองแล้ว แต่ยังเหลือโจทย์

- **ติดตั้งหลายไฟล์ตามลำดับเอง** — metrics-server, CRD + Traefik, Secret 3 ซอง, `k8s/00`–`70` (บทถัดไป: **Helm** ติดตั้งเป็นแพ็กเกจ + values)
- **ขนาดบูธยังต้องเดา** — requests 100m มาจากการลองเอง (**VPA** แนะนำ/ปรับ requests ให้)
- **เรือ (Node) มีแค่ 2 ลำ** — LAB 9 ข เห็น Pending แล้วไม่มีใครเพิ่มเรือ (**Cluster Autoscaler / Karpenter** บนคลาวด์)
- **ลูกค้าเป็นคิวงาน ไม่ใช่ CPU** — เช่นออเดอร์ค้างในคิว หรือปิดบูธเหลือ 0 ตอนกลางคืน (**KEDA**)

**คำถามท้าย LAB 11**

1. ทำไมขั้น B จึง apply HPA **ก่อน** ลบ replicas และถ้าสลับลำดับ (apply `20-web.yaml` ก่อนมี HPA) Deployment จะเหลือกี่บูธ
2. ทำไมลูกค้าจำลองต้องยิง `https://shop.localhost:30081` ผ่าน Traefik แทนการยิง Service `som-web` ตรง ๆ (คิดถึงสิ่งที่อยากพิสูจน์ใน ขั้น F–G)
3. ขาลงไม่มี error เพราะกลไกอะไรของบทที่ 7 ถ้าลบ `preStop` ออกจะเกิดอะไร
4. ถ้าวันจริงลูกค้ามา 3 เท่า แต่ `maxReplicas: 6` ร้านจะเป็นอย่างไร ควรแก้ที่ HPA อย่างเดียวหรือต้องดูอะไรอีก (ResourceQuota, ความจุ Node)
5. ทำไมไม่ใส่ HPA ให้ `som-db`
6. ถ้าต้องตั้งร้านนี้ใหม่บนคลัสเตอร์อื่นพรุ่งนี้ ต้อง apply อะไรบ้างตามลำดับ (นับจำนวนไฟล์/คำสั่ง) และส่วนไหนที่อยากรวมเป็นก้อนเดียว (ปูทางบทถัดไป)

**เก็บกวาด LAB 11:** ตรวจว่าลูกค้าจำลองหยุดแล้ว (`kubectl -n som-shop get deploy customers` ต้องเป็น `0/0`) และลบไฟล์ผลชั่วคราว `rm -f hit-up.log` ร้าน, HPA `som-web` และ metrics-server **เก็บไว้** (ดูตารางท้ายเอกสาร)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `error: Metrics API not available` | ยังไม่ติดตั้ง metrics-server หรือติดตั้งต้นฉบับ (x509) | LAB 1 ขั้นที่ 3 `kubectl apply -f metrics-server/00-metrics-server.yaml` รอ ~30 วินาที |
| APIService `False (MissingEndpoints)` / Pod `0/1` | metrics-server ตรวจใบรับรอง kubelet ไม่ผ่าน | ดู log `x509 ... IP SANs` → ใช้ไฟล์ของบท (`--kubelet-insecure-tls`) |
| `cpu: <unknown>/50%` ไม่หายเกิน 1 นาที | ไม่มี `requests.cpu` (`missing request for cpu`) หรือ Pod ไม่ Ready | `kubectl describe hpa` ดู Conditions/Events แล้วใส่ requests (LAB 5) |
| `ErrImagePull` ... `no match for platform in manifest` (hpa-example) | Node เป็น arm64 | ใช้ไฟล์ชุด `-arm` (ดูบทนำ) |
| HPA ไม่เพิ่มบูธทั้งที่ตัวยิงรันอยู่ | ตัวยิงค้าง (ไม่มี `-T`), ยิงผิดที่ หรือ customers ได้ 301 | `kubectl -n hpa-load logs deploy/load`, `kubectl -n som-shop logs deploy/customers --tail=5` ต้องเป็น `200` (ไม่ใช่ `301` — ต้องมี `:30081`) |
| HPA บอก 6 แต่ Deployment ได้น้อยกว่า | ResourceQuota หรือ Node เต็ม | Event ของ ReplicaSet (`exceeded quota`) / Pod (`Insufficient cpu`) — LAB 9 |
| บูธลดเหลือ 1 ทันทีหลัง `kubectl apply` | ไฟล์หรือ last-applied มี `replicas` | ลบ replicas จากไฟล์ + `kubectl apply edit-last-applied`/`set-last-applied` (LAB 10) |
| ปิดลูกค้าแล้วบูธยังไม่ลด | นาฬิกาทราย (`ScaleDownStabilized`) ค่าเริ่มต้น 300 วินาที | รอ หรือใช้ behavior window สั้นใน LAB |
| LAB 8 ไม่ scale ด้วย memory | Pod ของเครื่องนั้นใช้ memory ต่ำกว่า target | ดู `kubectl top pod -n hpa-demo` แล้วลด `averageValue` ใน `80-hpa-multi.yaml` ให้ต่ำกว่าค่าที่เห็น |
| `./watch-hpa.sh: Permission denied` | สิทธิ์ execute หายตอนคัดลอก | `bash watch-hpa.sh ...` หรือ `chmod +x watch-hpa.sh lab*/*.sh som-shop-v9/*.sh` |
| เครื่องหน่วงมากตอน LAB 11 | customers มากเกินสำหรับเครื่อง | `kubectl -n som-shop scale deploy/customers --replicas=1` (4 core) หรือ 0 |
| เปิด `https://shop.localhost:30081` ไม่ได้ใน browser | browser ไม่แปลง `*.localhost` | ดูทางสำรองในบทที่ 12 (`curl` ใน k8s-lab หรือแก้ไฟล์ hosts) |

## Checklist ส่งงาน

- [ ] ภาพ `kubectl top nodes` และ `kubectl get apiservice v1beta1.metrics.k8s.io` (`True`) หลัง LAB 1
- [ ] ภาพ `watch-hpa.sh` ของ LAB 3 ที่เห็น replicas เพิ่มถึง 6 และ `describe hpa` ที่มี `TooManyReplicas`
- [ ] ตารางเวลา scale down ของเครื่องตัวเองใน LAB 4 (ค่าเริ่มต้น หรืออ้างผลในเอกสาร + window 30)
- [ ] ผล `formula.sh` อย่างน้อย 3 รอบ (LAB 6)
- [ ] ภาพ LAB 9 ก (`3/6` + `exceeded quota`) และ ข (`Pending` + `Insufficient cpu`)
- [ ] ภาพ LAB 10 ที่เห็น `6/6 → 1/1` และหลังแก้ `unchanged` + `6/6`
- [ ] LAB 11: `watch-hpa.sh` ขาขึ้นถึง 6 และขาลงถึง 2, `hit.sh` `err=0` ทั้งสองช่วง, Traefik `6 servers` → `2 servers`, หน้าเว็บที่ชื่อ Pod ต่างกัน, `som-db 1/1`
- [ ] ภาพหน้าจอ browser ของตัวเอง: หน้าร้านที่มีแถบวันลดราคา (ชื่อ Pod อย่างน้อย 2 ชื่อจากการ refresh) และ Traefik dashboard ที่ `som-shop-som-web-80@kubernetes` มี server มากกว่า 2
- [ ] ตอบคำถามท้าย LAB 11

## เก็บกวาดหลังจบบท

| สิ่งที่สร้างในบทนี้ | เก็บไว้บทถัดไป? | ลบด้วย |
|---|---|---|
| namespace `hpa-demo`, `hpa-load` | ไม่ (ลบแล้วใน LAB 10) | `kubectl delete ns hpa-demo hpa-load` |
| metrics-server (`kube-system`) | **เก็บ** (บทต่อไปใช้ `kubectl top`) | `kubectl delete -f metrics-server/00-metrics-server.yaml` (สั่งในโฟลเดอร์ `02_LAB`) |
| HPA `som-web`, Deployment `customers` | เก็บได้ (customers = 0) | `kubectl -n som-shop delete hpa som-web deploy customers` (ถ้าลบ HPA ร้านจะค้างจำนวนบูธล่าสุด) |
| image `som-shop-web:1.7` | เก็บ | — |
| ไฟล์ `hit-up.log` ใน `som-shop-v9` | ไม่ | `rm -f hit-up.log` |

ปิด container เมื่อเลิกใช้ 🖥️ `docker stop k8s-lab` (คลัสเตอร์และร้านรอด restart)

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ Pod, % CPU และจำนวนวินาที) เป็นค่าตัวอย่าง ผู้เรียนควรใช้ผลลัพธ์จากเครื่องตัวเองและเนื้อหาในเอกสารนี้เป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริงบนเครื่องที่จำกัด 4 CPU (Kubernetes v1.37.0, kubectl v1.37.1, metrics-server v0.9.0, Traefik v3.7.13)
