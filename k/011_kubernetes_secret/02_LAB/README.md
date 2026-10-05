# LAB บทที่ 11: Secret — ซองปิดผนึกในกล่องกุญแจ สู่ร้านน้องส้มที่ซ่อนรหัสผ่าน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Secret — base64 ไม่ใช่การเข้ารหัส, สร้าง Secret หลายแบบและ `type` (`Opaque`, `basic-auth`, `tls`, `dockerconfigjson`), `data`/`stringData` และกับดัก `last-applied-configuration`, ใช้ใน Pod (env, envFrom, volume tmpfs, `defaultMode`) การอัปเดตและ `immutable`, TLS กับ nginx HTTPS, `imagePullSecrets` กับ registry ส่วนตัว, projected volume และ token ของ ServiceAccount, RBAC และการอ่าน Secret ทางอ้อม, ส่อง etcd และร้านอาหารแมวน้องส้มที่ย้ายรหัสผ่านฐานข้อมูลไปไว้ใน Secret เปลี่ยนรหัสจริง และเปิด HTTPS
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะช่วยน้องส้มเก็บความลับของร้านใส่ **ซองปิดผนึก (Secret)** ในกล่องกุญแจของโซน เริ่มจากพิสูจน์ว่า **base64 เป็นแค่ซองใส** สร้างซองหลายแบบและดูว่า `type` ตรวจอะไรให้ ส่งซองเข้า Pod เป็น env และไฟล์ (ถาดฟองน้ำความจำ tmpfs) จับเวลาการอัปเดต ทำ **ท่อแก้วปิดสนิท (TLS)** ให้ nginx เปิด **คลังตู้สินค้าส่วนตัว** ที่ต้องมีบัตรผ่าน (`imagePullSecrets`) รวมเอกสารในแฟ้มห่วง (projected volume) ทดสอบ **บัตรพนักงาน (RBAC)** ว่าใครเปิดกล่องได้และใครแอบอ่านทางอ้อมได้ แล้วส่องตู้เอกสาร etcd ว่ารหัสถูกเก็บอย่างไร ปิดท้ายด้วย **ร้านอาหารแมวน้องส้ม `som-shop-v7`** ที่ย้ายรหัสผ่านฐานข้อมูล `meow1234` ออกจาก YAML ไปไว้ใน Secret `som-db-secret` จน intern อ่านไม่ได้ เปลี่ยนรหัสจริงเป็น `purr5678` โดยออเดอร์ไม่หาย และเปิดร้านผ่าน HTTPS ที่ `https://localhost:30082` **โดยใช้ image `som-shop-web:1.5` ตัวเดิมจากบทที่ 10 ไม่แก้โค้ดเลย**

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, Kubernetes v1.37.0, kubectl v1.37.1, OpenSSL 3.0.13) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, ชื่อ Pod ของ Deployment ที่สุ่ม, IP, UID, ค่า sha256, ชื่อโฟลเดอร์ `..2026_10_05_…`, Node ที่ Pod ถูกวาง และจำนวนวินาทีที่ไฟล์อัปเดต ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ เวลาที่สคริปต์พิมพ์ (เช่น `18:32:25`) เป็นเวลาไทย ส่วนเวลาใน `ls -la` ภายใน Pod เป็น UTC (ช้ากว่า 7 ชั่วโมง)

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker`, `openssl` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container (🖥️) และการเปิด browser ที่ `http://localhost:30080`, `https://localhost:30081` (LAB 4) และ `https://localhost:30082` (LAB 9) (🌐)

### กติกาของ LAB บทนี้

- LAB 1 ทำในโฟลเดอร์ **`/workspace/011_kubernetes_secret/02_LAB`** LAB 2–8 ทำใน **`02_LAB/labs/labNN-...`** ของแต่ละ LAB และ LAB 9 ทำใน **`02_LAB/som-shop-v7`** ทุก LAB เริ่มด้วย `cd` ไปโฟลเดอร์ของตัวเอง
- LAB 1–8 ใช้ namespace `default` (LAB 5 สร้าง `reg`/`reg2` ชั่วคราว) และ LAB 9 ใช้ `som-shop` **Secret `demo` (LAB 1) และ `sd` (LAB 2) กับ Pod `spod` (LAB 3) ใช้ต่อถึง LAB 8** ทำ LAB 1–8 ต่อกันในรอบเดียวจะง่ายที่สุด เก็บกวาดรวมไว้ท้าย LAB 8 ส่วนไฟล์ `tls.crt`/`tls.key` ที่สร้างใน LAB 4 ใช้ต่อใน LAB 9 ขั้น E (อย่าลบ)
- รหัสผ่านทุกตัวในบทนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง: รหัส SSH `passwd`, รหัสฐานข้อมูล `meow1234` → `purr5678` (→ `hiss9012` ในรอบถ่ายภาพหน้าจอ), รหัสทดลอง `newpass-00`/`newpass-01`, registry `som`/`example-pass` และค่าอื่น ๆ ที่ขึ้นต้นด้วย `example-`
- token ของ ServiceAccount เป็น **รหัสลับจริงของคลัสเตอร์** ห้ามแปะลงรายงาน แชท หรือภาพหน้าจอ เอกสารนี้ตัดเหลือ `eyJhbGciOi...` เสมอ ในภาพหน้าจอที่ส่งงานให้บังรหัสผ่านและ token ทุกครั้ง
- image สาธารณะ `busybox:1.36`, `nginx:1.27-alpine`, `nginxinc/nginx-unprivileged:1.27-alpine`, `httpd:2.4-alpine` และ `registry:2` **ดึงจาก Docker Hub เองตอนใช้** ส่วน `som-shop-web:1.5` และ `postgres:17.11-alpine` ต้องโหลดเข้า Node ใน LAB 0 (ใช้เฉพาะ LAB 9)
- **ห้ามใช้ `kubectl edit`** ใน terminal ที่ไม่ใช่แบบโต้ตอบ ทุก LAB แก้ Secret ด้วย `kubectl patch`, `kubectl apply` หรือ `kubectl create ... --dry-run=client -o yaml | kubectl apply -f -`
- **ไฟล์ใน volume อัปเดตเองราว 1 นาที บางครั้งเกือบ 1.5 นาที** (LAB 3) อย่าเพิ่งสรุปว่าไม่ทำงานก่อนรอครบ 2 นาที
- **NodePort 30080–30082 จองได้ทีละ Service ทั้งคลัสเตอร์** บทนี้ใช้ 30081 ใน LAB 4 และ 30080/30082 ใน LAB 9
- LAB 5 **ห้ามนำ image ของร้าน (`som-shop-web`) ขึ้น registry ส่วนตัว และห้าม `crictl rmi` บน Node** (เหตุผลใน LAB 5) และต้องรัน `./cleanup-registry.sh` ทุกครั้งที่จบ

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์และ image](#lab-0-เตรียมคลัสเตอร์และ-image) | 15–20 นาที | ⭐ |
| 1 | [base64 ไม่ใช่การเข้ารหัส](#lab-1-base64-ไม่ใช่การเข้ารหัส) | 10 นาที | ⭐ |
| 2 | [สร้าง Secret หลายแบบและ type](#lab-2-สร้าง-secret-หลายแบบและ-type) | 15 นาที | ⭐⭐ |
| 3 | [ใช้ Secret ใน Pod การอัปเดต และ immutable](#lab-3-ใช้-secret-ใน-pod-การอัปเดต-และ-immutable) | 15–20 นาที | ⭐⭐ |
| 4 | [TLS Secret และ nginx HTTPS](#lab-4-tls-secret-และ-nginx-https) | 15 นาที | ⭐⭐⭐ |
| 5 | [imagePullSecrets กับ registry ส่วนตัว](#lab-5-imagepullsecrets-กับ-registry-ส่วนตัว) | 20 นาที | ⭐⭐⭐ |
| 6 | [projected volume และ token ของ ServiceAccount](#lab-6-projected-volume-และ-token-ของ-serviceaccount) | 10 นาที | ⭐⭐ |
| 7 | [RBAC: ใครเปิดซองได้ และการอ่านทางอ้อม](#lab-7-rbac-ใครเปิดซองได้-และการอ่านทางอ้อม) | 15 นาที | ⭐⭐⭐ |
| 8 | [ส่อง etcd: รหัสถูกเก็บอย่างไร](#lab-8-ส่อง-etcd-รหัสถูกเก็บอย่างไร) | 10 นาที | ⭐⭐⭐ |
| 9 | [LAB สุดท้าย: ร้านน้องส้มซ่อนรหัสผ่าน](#lab-9-lab-สุดท้าย-ร้านน้องส้มซ่อนรหัสผ่าน) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (รวมช่วง build image ใน LAB 0 และรอไฟล์อัปเดตใน LAB 3) ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านหัวข้อทฤษฎีที่เกี่ยวข้อง: LAB 1 → หัวข้อ 2, LAB 2 → หัวข้อ 3–4, LAB 3 → หัวข้อ 5, LAB 4 → หัวข้อ 7, LAB 5 → หัวข้อ 6, LAB 6 → หัวข้อ 3.4 และ 12, LAB 7 → หัวข้อ 8, LAB 8 → หัวข้อ 9, LAB 9 → หัวข้อ 1, 5, 8, 10.3 และ 13.4

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมคลัสเตอร์และ image](#fig-1) | 15 | [LAB 9 ขั้น B สร้างซอง](#fig-15) |
| 2 | [LAB 1 base64 ไม่ใช่การเข้ารหัส](#fig-2) | 16 | [LAB 9 ขั้น C1 db ใช้ซอง](#fig-16) |
| 3 | [LAB 2 สร้าง Secret หลายแบบและ type](#fig-3) | 17 | [LAB 9 ขั้น C2 web ใช้ซอง](#fig-17) |
| 4 | [LAB 3 ใช้ Secret ใน Pod](#fig-4) | 18 | [LAB 9 ขั้น D1 ALTER USER](#fig-18) |
| 5 | [LAB 3 อัปเดตและ immutable](#fig-5) | 19 | [LAB 9 ขั้น D2 ลืมแก้ซอง](#fig-19) |
| 6 | [LAB 4 TLS และ nginx HTTPS](#fig-6) | 20 | [LAB 9 ขั้น D3 แก้ซองแล้ว restart](#fig-20) |
| 7 | [LAB 5 registry ส่วนตัว](#fig-7) | 21 | [LAB 9 ขั้น E HTTPS](#fig-21) |
| 8 | [LAB 5 kubelet ตรวจบัตรซ้ำ](#fig-8) | 22 | [ภาพหน้าจอจริง ร้านที่รหัส DB มาจาก Secret](#fig-22) |
| 9 | [LAB 6 projected และ token](#fig-9) | 23 | [ภาพหน้าจอจริง browser เตือนใบรับรอง self-signed](#fig-23) |
| 10 | [LAB 7 intern อ่านซองไม่ได้](#fig-10) | 24 | [ภาพหน้าจอจริง ร้านผ่าน HTTPS 30082](#fig-24) |
| 11 | [LAB 7 maker อ่านทางอ้อม](#fig-11) | 25 | [ภาพหน้าจอจริง Pod เดิมตอบ 503 ระหว่างรหัสไม่ตรง](#fig-25) |
| 12 | [LAB 8 ส่อง etcd](#fig-12) | 26 | [ภาพหน้าจอจริง รหัสใหม่ ร้านกลับมา ออเดอร์ครบ](#fig-26) |
| 13 | [LAB 9 ภาพรวม som-shop-v7](#fig-13) | 27 | [สรุป LAB 9](#fig-27) |
| 14 | [LAB 9 ขั้น A intern เห็นรหัส](#fig-14) | | |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ 01–22 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน 5 ภาพ
├── labs/                              ← ไฟล์ของ LAB 2–8 (LAB 1 ใช้คำสั่งล้วน)
│   ├── lab02-types/{pw.txt,sd.yaml}                         (ไฟล์รหัสไม่มี newline + Secret แบบ data/stringData)
│   ├── lab03-use/{spod.yaml,frozen.yaml,wait-secret.sh}     (Pod ใช้ Secret 3 แบบ, immutable, จับเวลาอัปเดต)
│   ├── lab04-tls/tls.yaml                                   (ConfigMap nginx + Pod ngx-tls + Service NodePort 30081)
│   ├── lab05-registry/                                      (registry ส่วนตัว + Pod 5 แบบ)
│   │   ├── setup-registry.sh, cleanup-registry.sh, Dockerfile, menu.txt
│   │   └── 00-ns.yaml, 1-nopull.yaml, 2-withpull.yaml, 3-wrong.yaml, 4-viasa.yaml, 5-cached.yaml
│   ├── lab06-projected/{proj.yaml,builder-token.yaml}       (projected volume + service-account-token)
│   ├── lab07-rbac/{intern.yaml,maker.yaml,peek.yaml}        (บัตรแถบเทา + ผู้สร้าง Pod + Pod แอบอ่าน)
│   └── lab08-etcd/etcdget.sh                                (อ่าน etcd แบบอ่านอย่างเดียว)
└── som-shop-v7/                       ← LAB 9 ร้านน้องส้มที่รหัสผ่านอยู่ใน Secret
    ├── app/                           ← แอป Next.js + Dockerfile รุ่น 1.5 (สำเนาจากบทที่ 10 ไม่แก้โค้ด)
    ├── k8s-010/{00-namespace,10-db,15-config,20-web}.yaml   ← จุดเริ่ม: สภาพท้ายบท 010 (รหัสยังเขียนใน YAML)
    ├── k8s/{00-namespace,10-db,15-config,20-web,30-https}.yaml ← บทนี้: รหัสจาก Secret som-db-secret + ทางเข้า HTTPS 30082
    ├── examples/05-secret.example.yaml ← ไฟล์ Secret ตัวอย่าง (ค่าปลอม commit ได้) — ไม่ได้อยู่ใน k8s/ โดยตั้งใจ
    ├── extra/30-https-restricted.yaml ← ทางเลือก HTTPS ที่ผ่าน Pod Security restricted (nginx-unprivileged)
    ├── rbac/intern.yaml               ← ServiceAccount intern ดูได้อย่างเดียว (Pod, log, ConfigMap, Deployment, StatefulSet)
    ├── rbac/intern-context.sh         ← สร้าง context "intern" ใน kubeconfig ด้วย token อายุ 24 ชั่วโมง
    ├── .gitignore                     ← กันไฟล์ secret.yaml, *.secret.yaml, *.key, *.crt ไม่ให้เข้า git
    ├── hit.sh                         ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน
    └── wait-announcement.sh           ← (จากบทที่ 10) จับเวลาประกาศหน้าร้าน
```

> **ทำไม `05-secret.example.yaml` อยู่ใน `examples/` ไม่ใช่ `k8s/`:** ถ้าอยู่ใน `k8s/` คำสั่ง `kubectl apply -f k8s/` (ใช้คืนสภาพร้าน) จะเขียนรหัสตัวอย่าง `meow1234` ทับรหัสที่เปลี่ยนแล้วใน Secret ทำให้ร้านต่อฐานข้อมูลไม่ได้ ไฟล์ตัวอย่างจึงแยกไว้ และวิธีหลักของบทนี้คือ `kubectl create secret generic` (ขั้น B)

### แอปร้านใช้รุ่น 1.5 เดิม

`som-shop-v7/app/` เป็นสำเนาแอปรุ่น **1.5 จากบทที่ 10 โดยไม่แก้โค้ดแม้แต่บรรทัดเดียว** เพราะแอปอ่านรหัสผ่านจาก env `DATABASE_URL` (`lib/db.ts` ใช้ `process.env.DATABASE_URL`) อยู่แล้ว ไม่สนว่าค่ามาจาก `value:` ใน YAML หรือจาก `secretKeyRef` บทนี้จึงเปลี่ยนแค่ manifest สิ่งที่ต่างให้เห็นบนหน้าเว็บมาจาก ConfigMap `k8s/15-config.yaml` (หัวเว็บ `⚓ ท่าเรือ Kubernetes · Secret` และ footer `... Kubernetes LAB 011 · รหัส DB อยู่ใน Secret som-db-secret`)

---

## LAB 0: เตรียมคลัสเตอร์และ image

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมคลัสเตอร์และ image" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: 3 Node Ready, โหลด postgres:17.11-alpine (image-archive) และ som-shop-web:1.5 (สำเนาแอปจากบท 010 ไม่แก้โค้ด) ให้ทุก Node</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 10 หรือสร้างใหม่) ตรวจของค้าง และเตรียม image `postgres:17.11-alpine` กับ `som-shop-web:1.5` ให้ทุก Node สำหรับ LAB 9

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md)–[10](../../010_kubernetes_configmap/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `011_kubernetes_secret` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `011_kubernetes_secret` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 011_kubernetes_secret k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ บทนี้มีแอปร้านรุ่น 1.5 (`02_LAB/som-shop-v7/app`) และไฟล์สภาพท้ายบท 010 (`som-shop-v7/k8s-010/`) ของตัวเอง จึง **ไม่ต้องมีโฟลเดอร์ของบทก่อนใน container** ก็ทำได้ครบ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (ค่าตัวอย่างเพื่อการเรียน พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และตรวจคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB
ls labs som-shop-v7
kubectl get nodes
kubectl version
```

```text
labs:
lab02-types
lab03-use
lab04-tls
lab05-registry
lab06-projected
lab07-rbac
lab08-etcd

som-shop-v7:
app
examples
extra
hit.sh
k8s
k8s-010
rbac
wait-announcement.sh
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   51s   v1.37.0
lab-worker          Ready    <none>          41s   v1.37.0
lab-worker2         Ready    <none>          41s   v1.37.0
Client Version: v1.37.1
Kustomize Version: v5.8.1
Server Version: v1.37.0
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 10 ยังอยู่) | **ใช้ต่อได้เลย** ไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `k8s-up` (การทดลองใช้เวลาราว 50 วินาที) image ที่เคย `kind load` ในบทก่อนจะหายไป ต้องโหลดใหม่ในขั้นที่ 5 |

### ขั้นที่ 4: ตรวจของที่ค้างจากบทก่อน

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get sc; kubectl get pv,pvc -A; kubectl get secret -A; kubectl get svc -A | grep 3008 || echo "ไม่มี NodePort 3008x ค้าง"
```

ผลจริงบนคลัสเตอร์ใหม่

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  47s
No resources found
NAMESPACE     NAME                     TYPE                            DATA   AGE
kube-system   bootstrap-token-abcdef   bootstrap.kubernetes.io/token   6      49s
ไม่มี NodePort 3008x ค้าง
```

คลัสเตอร์ใหม่มี Secret ของระบบตัวเดียวคือ `bootstrap-token-abcdef` ใน `kube-system` (ใช้ตอน Node เข้าร่วมคลัสเตอร์) ถ้ายังเห็นร้านของบทที่ 10 (namespace `som-shop` จอง NodePort 30080 และมี PVC `data-som-db-0`) แนะนำให้ลบด้วย `kubectl delete ns som-shop` (ราว 30 วินาที) เพื่อให้ LAB 9 เริ่มจากร้านใหม่และตัวเลขออเดอร์ตรงกับเอกสาร

### ขั้นที่ 5: โหลด postgres และ build som-shop-web:1.5

ตรวจก่อนว่า Node มี image อะไรอยู่แล้ว (ถ้าใช้คลัสเตอร์เดิมจากบทที่ 10 น่าจะมีครบแล้ว)

```bash
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

**postgres** (ข้ามได้ถ้าเห็น `postgres 17.11-alpine` บนทั้งสอง worker แล้ว) เป็น image หลาย platform จึงใช้ `docker save --platform` + `kind load image-archive` 🐧 ในโฟลเดอร์ `02_LAB`

```bash
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab)
```

```text
docker.io/library/postgres:17.11-alpine

real	0m15.745s
user	0m0.329s
sys	0m1.060s
```

**som-shop-web:1.5** (ข้ามได้ถ้าใช้คลัสเตอร์เดิมของบทที่ 10 และเห็น `som-shop-web 1.5` บนทั้งสอง worker แล้ว เพราะเป็นโค้ดชุดเดียวกัน) **คลัสเตอร์ใหม่ต้อง build** จากแอปในโฟลเดอร์ `som-shop-v7/app` แล้ว `kind load` ให้ทุก Node

```bash
cd som-shop-v7
time (docker build -q -t som-shop-web:1.5 --build-arg APP_VERSION=1.5 app && kind load docker-image som-shop-web:1.5 --name lab)
```

```text
sha256:d56246b6c5cafd030b7d093acd3294817c13e9ed6370764a6ded6d692cff6cf7
Image: "som-shop-web:1.5" with ID "sha256:d56246b6c5cafd030b7d093acd3294817c13e9ed6370764a6ded6d692cff6cf7" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.5" with ID "sha256:d56246b6c5cafd030b7d093acd3294817c13e9ed6370764a6ded6d692cff6cf7" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.5" with ID "sha256:d56246b6c5cafd030b7d093acd3294817c13e9ed6370764a6ded6d692cff6cf7" not yet present on node "lab-worker2", loading...

real	0m36.840s
user	0m0.414s
sys	0m1.000s
```

build ครั้งแรกใช้ราว 35 วินาทีในเครื่องทดลอง (`npm ci` แล้วคอมไพล์ Next.js) เครื่องนักศึกษาอาจนานกว่านี้หลายเท่า ค่า sha256 จะต่างจากตัวอย่าง ไฟล์ `/root/postgres.tar` ลบได้หลัง load เสร็จ (`rm -f /root/postgres.tar`) ตรวจซ้ำด้วยคำสั่ง `crictl` ข้างบน ผลจริงหลัง load

```text
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  b0b30ef64ac6d       76.7MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  b0b30ef64ac6d       76.7MB
```

### ขั้นที่ 6: ตรวจเครื่องมือที่มีใน k8s-lab

```bash
cd /workspace/011_kubernetes_secret/02_LAB
which openssl; openssl version; which htpasswd strings xxd hexdump || true
```

```text
/usr/bin/openssl
OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
```

k8s-lab มี `openssl` (ใช้ใน LAB 4) แต่ **ไม่มี** `htpasswd`, `strings`, `xxd`, `hexdump` (บรรทัดว่าง = หาไม่เจอ) บทนี้จึงสร้างไฟล์รหัสของ registry ด้วย `htpasswd` ใน image `httpd:2.4-alpine` (LAB 5) และอ่านข้อมูลไบนารีจาก etcd ด้วย `grep -a` / `cat -v` (LAB 8)

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node `Ready` (v1.37.0) พร้อม kubectl v1.37.1 ไม่มี PV/PVC หรือ NodePort 3008x ค้าง และมี Secret ของระบบแค่ `bootstrap-token-abcdef`
- `postgres:17.11-alpine` และ `som-shop-web:1.5` อยู่บนทั้งสอง worker (ผลจริง LAB 0 ทั้งหมดใช้เวลาราว 54 วินาที ไม่นับ `k8s-up`)

**คำถามชวนคิด**

1. ทำไมบทนี้ใช้ image `som-shop-web:1.5` ตัวเดิมได้ ทั้งที่ย้ายรหัสผ่านไปไว้ที่อื่น (ดู `lib/db.ts` ของแอป)
2. Secret `bootstrap-token-abcdef` อยู่ใน namespace `kube-system` ถ้าผู้ใช้ทั่วไปมีสิทธิ์ `list secrets` ใน `kube-system` จะเกิดความเสี่ยงอะไร

---

## LAB 1: base64 ไม่ใช่การเข้ารหัส

<p align="center" id="fig-2">
  <img src="images/02-lab1-base64.png" alt="รูปที่ 2 LAB 1 base64 ไม่ใช่การเข้ารหัส" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: create secret generic demo → get -o yaml เห็น password: bWVvdzEyMzQ= → base64 -d ได้ meow1234; describe แสดง 8 bytes; echo vs echo -n</em>
</p>

**เป้าหมาย:** สร้าง Secret แรก ดูว่าค่าถูกเก็บเป็น base64 แปลงกลับเป็นรหัสได้ทันที เห็นกับดัก newline ของ `echo` และความต่างระหว่าง `describe` กับ `get -o yaml`

**ไฟล์:** ไม่มี (คำสั่งล้วน) ทำในโฟลเดอร์ `02_LAB`

### ขั้นที่ 1: Secret เป็น resource แบบไหน

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB
kubectl api-resources | grep -E "^NAME|^secrets"
kubectl get secret -A
```

```text
NAME                                SHORTNAMES   APIVERSION                        NAMESPACED   KIND
secrets                                          v1                                true         Secret
NAMESPACE     NAME                     TYPE                            DATA   AGE
kube-system   bootstrap-token-abcdef   bootstrap.kubernetes.io/token   6      113s
```

Secret เป็น namespaced object ใน `v1` และ **ไม่มีชื่อย่อ** (ต่างจาก ConfigMap ที่มี `cm`)

### ขั้นที่ 2: สร้างซองแรก

```bash
kubectl create secret generic demo --from-literal=username=som --from-literal=password=meow1234
kubectl get secret demo
kubectl get secret demo -o yaml
```

```text
secret/demo created
NAME   TYPE     DATA   AGE
demo   Opaque   2      0s
apiVersion: v1
data:
  password: bWVvdzEyMzQ=
  username: c29t
kind: Secret
metadata:
  creationTimestamp: "2026-10-05T11:31:58Z"
  name: demo
  namespace: default
  resourceVersion: "742"
  uid: 9129defa-e305-4359-b188-df70f9e70f61
type: Opaque
```

`generic` ได้ type `Opaque` ค่าใน `data` ไม่ใช่ `meow1234` ตรง ๆ แต่เป็นข้อความที่ดูอ่านไม่ออก

### ขั้นที่ 3: เปิดซองใส

```bash
kubectl get secret demo -o jsonpath='{.data.password}'; echo
kubectl get secret demo -o jsonpath='{.data.password}' | base64 -d; echo
echo bWVvdzEyMzQ= | base64 -d; echo
```

```text
bWVvdzEyMzQ=
meow1234
meow1234
```

ไม่ต้องใช้กุญแจหรือสิทธิ์พิเศษใด ๆ แค่คำสั่ง `base64 -d` ก็ได้รหัสคืน นี่คือเหตุผลที่เรียก base64 ว่า **ซองใส**

### ขั้นที่ 4: กับดัก newline ของ echo

```bash
echo meow1234 | base64
echo -n meow1234 | base64
echo bWVvdzEyMzQK | base64 -d | od -c | head -2
```

```text
bWVvdzEyMzQK
bWVvdzEyMzQ=
0000000   m   e   o   w   1   2   3   4  \n
0000011
```

`echo` ธรรมดาเติม `\n` ท้ายข้อความ ได้ base64 ที่ลงท้ายด้วย `K` และถอดกลับได้ 9 ไบต์ (`0000011` เป็นเลขฐานแปด = 9) ถ้านำค่านี้ไปใส่ `data` ของ Secret แอปจะได้รหัส `meow1234\n` ซึ่ง login ไม่ผ่าน ต้องใช้ `echo -n` (ได้ `bWVvdzEyMzQ=`)

### ขั้นที่ 5: describe ไม่แสดงค่า แต่ get แสดง

```bash
kubectl describe secret demo
kubectl get secret demo -o go-template='{{range $k,$v := .data}}{{$k}}={{$v | base64decode}}{{"\n"}}{{end}}'
```

```text
Name:         demo
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
password:  8 bytes
username:  3 bytes
password=meow1234
username=som
```

`describe` บอกแค่ขนาด (`8 bytes`) ส่วน go-template ที่มีฟังก์ชัน `base64decode` ถอดทุก key ในคำสั่งเดียว ทั้งสองคำสั่งใช้สิทธิ์ `get secrets` เหมือนกัน

### ขั้นที่ 6: สร้างซ้ำ และให้ kubectl เขียน YAML

```bash
kubectl create secret generic demo --from-literal=password=again
kubectl create secret generic demo2 --from-literal=password=meow1234 --dry-run=client -o yaml
```

```text
error: failed to create secret secrets "demo" already exists
apiVersion: v1
data:
  password: bWVvdzEyMzQ=
kind: Secret
metadata:
  name: demo2
```

`--dry-run=client -o yaml` ไม่ได้สร้าง `demo2` จริง แค่พิมพ์ YAML ที่แปลง base64 ให้แล้ว (ใช้ต่อใน LAB 2 และ LAB 9 สำหรับอัปเดต Secret)

### สิ่งที่เห็น

- Secret `demo` (type `Opaque`) เก็บ `password: bWVvdzEyMzQ=`, `username: c29t` ซึ่งถอดกลับเป็น `meow1234` และ `som` ได้ทันที
- `echo` → `bWVvdzEyMzQK` (มี `\n`) / `echo -n` → `bWVvdzEyMzQ=`
- `describe` แสดง `password:  8 bytes` แต่ `get -o jsonpath`/go-template แสดงค่าจริง

> **เก็บไว้:** Secret `demo` ใช้ต่อใน LAB 3, 6, 7 และ 8 อย่าเพิ่งลบ

**คำถามชวนคิด**

1. ถ้ามีคนแปะผล `kubectl get secret demo -o yaml` ลงแชทกลุ่ม ถือว่ารหัสรั่วหรือไม่ เพราะอะไร
2. `c29t` ถอดได้ว่าอะไร ลองคิดด้วยตัวเองก่อนรัน `echo c29t | base64 -d`

---

## LAB 2: สร้าง Secret หลายแบบและ type

<p align="center" id="fig-3">
  <img src="images/03-lab2-create-types.png" alt="รูปที่ 3 LAB 2 สร้าง Secret หลายแบบและ type" width="900"><br>
  <em><b>รูปที่ 3</b> LAB2: --from-file, data + stringData (stringData ชนะ), basic-auth/tls/docker-registry และ error ของ type; ดู last-applied-configuration ที่เก็บ stringData เป็นข้อความ</em>
</p>

**เป้าหมาย:** สร้าง Secret จากไฟล์ (มี/ไม่มี newline), เขียน YAML ที่มีทั้ง `data` และ `stringData` แล้วเห็นกับดัก `last-applied-configuration` เปรียบเทียบ 3 วิธีที่เลี่ยงได้ ลอง `type` ที่ตรวจ key ให้ (`basic-auth`, `tls`) สร้างบัตรผ่าน registry (`docker-registry`) และชนเพดาน 1 MiB

**ไฟล์:** `labs/lab02-types/pw.txt`, `sd.yaml`

### ขั้นที่ 1: ไฟล์รหัสที่ไม่มี newline

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab02-types
ls -la; od -c pw.txt
```

```text
total 16
drwxr-xr-x 2 root root 4096 Oct  5 18:00 .
drwxr-xr-x 9 root root 4096 Oct  5 18:00 ..
-rw-r--r-- 1 root root    8 Oct  5 18:00 pw.txt
-rw-r--r-- 1 root root  980 Oct  5 18:00 sd.yaml
0000000   m   e   o   w   1   2   3   4
0000010
```

`pw.txt` มี 8 ไบต์พอดี ไม่มี `\n` ท้ายไฟล์ (ไฟล์นี้สร้างด้วย `printf` ถ้าแก้ไฟล์ด้วย editor อาจถูกเติม newline ให้)

### ขั้นที่ 2: --from-file กับไฟล์ที่มีและไม่มี newline

```bash
kubectl create secret generic fromfile --from-file=db-password=pw.txt
kubectl get secret fromfile -o jsonpath='{.data}'; echo
echo meow1234 > pw-nl.txt; kubectl create secret generic fromfile-nl --from-file=db-password=pw-nl.txt; kubectl get secret fromfile-nl -o jsonpath='{.data}'; echo; kubectl get secret fromfile-nl -o jsonpath='{.data.db-password}' | base64 -d | od -c | head -2
```

```text
secret/fromfile created
{"db-password":"bWVvdzEyMzQ="}
secret/fromfile-nl created
{"db-password":"bWVvdzEyMzQK"}
0000000   m   e   o   w   1   2   3   4  \n
0000011
```

`--from-file=db-password=pw.txt` ตั้งชื่อ key เป็น `db-password` ค่าคือเนื้อไฟล์ทั้งไฟล์ ไฟล์ `pw-nl.txt` ที่สร้างด้วย `echo` มี `\n` ติดเข้าไปในรหัสด้วย

### ขั้นที่ 3: data กับ stringData ในไฟล์เดียว

```bash
cat sd.yaml | grep -v "^#"
kubectl apply -f sd.yaml
kubectl get secret sd -o yaml
kubectl get secret sd -o jsonpath='{.data.PASSWORD}' | base64 -d; echo
```

```text
apiVersion: v1
kind: Secret
metadata:
  name: sd
type: Opaque
data:
  PASSWORD: bWVvdzEyMzQ=            # = base64 ของ meow1234 (แค่เปลี่ยนตัวอักษร ไม่ใช่การเข้ารหัส)
stringData:
  PASSWORD: override-by-stringData   # ทับ data.PASSWORD
  USERNAME: som                      # ระบบแปลงเป็น base64 เก็บใน data ให้เอง
secret/sd created
apiVersion: v1
data:
  PASSWORD: b3ZlcnJpZGUtYnktc3RyaW5nRGF0YQ==
  USERNAME: c29t
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"PASSWORD":"bWVvdzEyMzQ="},"kind":"Secret","metadata":{"annotations":{},"name":"sd","namespace":"default"},"stringData":{"PASSWORD":"override-by-stringData","USERNAME":"som"},"type":"Opaque"}
  creationTimestamp: "2026-10-05T11:32:06Z"
  name: sd
  namespace: default
  resourceVersion: "759"
  uid: 77a04079-2324-451f-9319-e7dfbabfe290
type: Opaque
override-by-stringData
```

สังเกต 3 อย่าง

1. `PASSWORD` เป็นค่าจาก `stringData` (**stringData ชนะ** เมื่อ key ซ้ำ)
2. object ที่เก็บจริงมีแค่ `data` (`USERNAME` ถูกแปลงเป็น `c29t` ให้)
3. **annotation `last-applied-configuration` เก็บ `"stringData":{"PASSWORD":"override-by-stringData","USERNAME":"som"}` เป็นข้อความ** ไม่ต้อง decode ก็อ่านได้ ถ้าเป็นรหัสจริง นี่คือการรั่วอีกที่หนึ่ง

### ขั้นที่ 4: 3 วิธีที่ไม่ทิ้งรหัสเป็นข้อความ

```bash
kubectl get secret sd -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}'
kubectl create secret generic viapipe --from-literal=PASSWORD=pipe-pass-01 --dry-run=client -o yaml | kubectl apply -f -
kubectl get secret viapipe -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}'
kubectl create secret generic viass --from-literal=PASSWORD=ss-pass-01 --dry-run=client -o yaml | kubectl apply --server-side -f -; kubectl get secret viass -o jsonpath='{.metadata.annotations}'; echo '(ไม่มี annotation last-applied)'
```

```text
{"apiVersion":"v1","data":{"PASSWORD":"bWVvdzEyMzQ="},"kind":"Secret","metadata":{"annotations":{},"name":"sd","namespace":"default"},"stringData":{"PASSWORD":"override-by-stringData","USERNAME":"som"},"type":"Opaque"}
secret/viapipe created
{"apiVersion":"v1","data":{"PASSWORD":"cGlwZS1wYXNzLTAx"},"kind":"Secret","metadata":{"annotations":{},"name":"viapipe","namespace":"default"}}
secret/viass serverside-applied
(ไม่มี annotation last-applied)
```

| วิธีสร้าง | annotation last-applied |
|---|---|
| `kubectl create secret generic demo ...` (LAB 1) | ไม่มี |
| `create ... --dry-run=client -o yaml \| kubectl apply -f -` | มี แต่เก็บเป็น base64 ใน `data` (`cGlwZS1wYXNzLTAx`) |
| `create ... --dry-run=client -o yaml \| kubectl apply --server-side -f -` | ไม่มี (`serverside-applied`) |
| `kubectl apply -f sd.yaml` (มี stringData) | มี และเป็นข้อความ ❌ |

### ขั้นที่ 5: type ที่ตรวจ key ให้

```bash
kubectl create secret generic onlypw --type=kubernetes.io/basic-auth --from-literal=password=meow1234; kubectl get secret onlypw
kubectl create secret generic emptyba --type=kubernetes.io/basic-auth
kubectl create secret generic ba --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow1234; kubectl get secret ba
kubectl create secret generic badtls --type=kubernetes.io/tls --from-file=tls.crt=pw.txt
kubectl create secret tls badtls2 --cert=pw.txt --key=pw.txt
```

```text
secret/onlypw created
NAME     TYPE                       DATA   AGE
onlypw   kubernetes.io/basic-auth   1      0s
error: failed to create secret Secret "emptyba" is invalid: [data[username]: Required value, data[password]: Required value]
secret/ba created
NAME   TYPE                       DATA   AGE
ba     kubernetes.io/basic-auth   2      0s
error: failed to create secret Secret "badtls" is invalid: data[tls.key]: Required value
error: tls: failed to find any PEM data in certificate input
```

- `basic-auth` ใส่แค่ `password` ได้ (DATA `1`) แต่ว่างทั้งคู่ถูกปฏิเสธ
- `kubernetes.io/tls` ที่ไม่มี `tls.key` ถูก API server ปฏิเสธ (`Required value`)
- `kubectl create secret tls` ตรวจว่าไฟล์เป็น PEM ก่อนส่ง เพราะ `pw.txt` ไม่ใช่ใบรับรองจึงได้ `... PEM data in certificate input` (ข้อความแบบ `... in key input` จะเห็นใน LAB 4 เมื่อ cert ถูกแต่ key ผิด)

### ขั้นที่ 6: บัตรผ่าน registry ก็ถอดได้

```bash
kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=som --docker-password=example-pass --docker-email=som@example.com; kubectl get secret regcred
kubectl get secret regcred -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d; echo
echo c29tOmV4YW1wbGUtcGFzcw== | base64 -d; echo
```

```text
secret/regcred created
NAME      TYPE                             DATA   AGE
regcred   kubernetes.io/dockerconfigjson   1      0s
{"auths":{"registry.example.com":{"username":"som","password":"example-pass","email":"som@example.com","auth":"c29tOmV4YW1wbGUtcGFzcw=="}}}
som:example-pass
```

รหัสของ registry (ค่าสมมติ `example-pass`) อยู่ทั้งใน `password` และใน `auth` (base64 ของ `som:example-pass`) jsonpath ต้องใส่ `\.` หน้า `dockerconfigjson` เพราะชื่อ key ขึ้นต้นด้วยจุด ใน LAB 2 นี้ `registry.example.com` เป็นชื่อสมมติ ยังไม่ได้ใช้ดึง image จริง (LAB 5 จะใช้กับ registry จริง)

### ขั้นที่ 7: เพดาน 1 MiB และสรุปซองทั้งหมด

```bash
head -c 1100000 /dev/zero > big.bin; kubectl create secret generic huge --from-file=big.bin; rm -f big.bin
kubectl get secret
```

```text
error: failed to create secret Secret "huge" is invalid: data: Too long: may not be more than 1048576 bytes
NAME          TYPE                             DATA   AGE
ba            kubernetes.io/basic-auth         2      1s
demo          Opaque                           2      11s
fromfile      Opaque                           1      4s
fromfile-nl   Opaque                           1      3s
onlypw        kubernetes.io/basic-auth         1      1s
regcred       kubernetes.io/dockerconfigjson   1      0s
sd            Opaque                           2      3s
viapipe       Opaque                           1      2s
viass         Opaque                           1      2s
```

### สิ่งที่เห็น

- ไฟล์ไม่มี newline → `bWVvdzEyMzQ=` / มี newline → `bWVvdzEyMzQK`
- stringData ชนะ data (`override-by-stringData`) แต่ `kubectl apply` เก็บ stringData เป็นข้อความใน `last-applied-configuration` ส่วนวิธี pipe เก็บเป็น base64 และ `--server-side` ไม่มี annotation
- error ของ type: `[data[username]: Required value, data[password]: Required value]`, `data[tls.key]: Required value`, `tls: failed to find any PEM data in certificate input`
- `.dockerconfigjson` ถอดได้ `"password":"example-pass"`, ขนาดเกิน → `Too long: may not be more than 1048576 bytes`

> **เก็บไว้:** Secret `sd` ใช้ต่อใน LAB 3 ไฟล์ `pw-nl.txt` ลบได้ (`rm -f pw-nl.txt`) Secret อื่น ๆ จะลบรวมท้าย LAB 8

**คำถามชวนคิด**

1. ทำไม kubectl จึงตรวจ PEM ของ `tls` ฝั่ง client ได้ แต่ `Required value` มาจาก API server (ดูรูปแบบข้อความ error ที่ต่างกัน)
2. ถ้าทีมต้องเก็บ Secret YAML ไว้ในไฟล์เพื่อ apply ซ้ำได้ ควรใช้ `data` หรือ `stringData` และจะเลี่ยงปัญหา last-applied อย่างไร

---

## LAB 3: ใช้ Secret ใน Pod การอัปเดต และ immutable

<p align="center" id="fig-4">
  <img src="images/04-lab3-use-in-pod.png" alt="รูปที่ 4 LAB 3 ใช้ Secret ใน Pod" width="900"><br>
  <em><b>รูปที่ 4</b> LAB3: spod ใช้ secretKeyRef/envFrom prefix SD_/volume → mount เป็น tmpfs ro, ไฟล์ -r-------- เมื่อ defaultMode 0400, /proc/1/environ เห็น DB_PASSWORD</em>
</p>

**เป้าหมาย:** ส่ง Secret เข้า Pod 3 แบบ (`secretKeyRef`, `envFrom` + `prefix`, volume) เห็นว่า volume เป็น tmpfs อ่านอย่างเดียว ตั้ง `defaultMode: 0400` เห็นทางรั่วของ env ผ่าน `/proc/1/environ` จับเวลาว่าไฟล์อัปเดตเองเมื่อไรแต่ env ไม่เปลี่ยน และลองซองเคลือบ `immutable`

**ไฟล์:** `labs/lab03-use/spod.yaml`, `frozen.yaml`, `wait-secret.sh` (ต้องมี Secret `demo` จาก LAB 1 และ `sd` จาก LAB 2)

### ขั้นที่ 1: Pod ที่ใช้ Secret 3 แบบ

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab03-use
grep -v '^#' spod.yaml
kubectl apply -f spod.yaml && kubectl wait --for=condition=Ready pod/spod --timeout=120s
```

ส่วนสำคัญของ `spod.yaml`

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: demo               # ชื่อ Secret
        key: password            # key ในซอง
envFrom:
  - prefix: SD_
    secretRef:
      name: sd
```

```yaml
volumes:
  - name: s
    secret:
      secretName: demo               # ทุก key = 1 ไฟล์ (/etc/secret/username, /etc/secret/password)
  - name: s400
    secret:
      secretName: demo
      defaultMode: 0400              # เลขฐานแปด → ไฟล์ -r--------
```

```text
pod/spod created
pod/spod condition met
```

### ขั้นที่ 2: env ที่ได้

```bash
kubectl exec spod -- env | grep -E 'DB_|SD_'
```

```text
SD_USERNAME=som
SD_PASSWORD=override-by-stringData
DB_PASSWORD=meow1234
```

`DB_PASSWORD` มาจาก `secretKeyRef` (Secret `demo` key `password`) ส่วน `SD_*` มาจาก `envFrom` ที่ถ่ายทุก key ของ `sd` พร้อมเติม prefix `SD_`

### ขั้นที่ 3: ไฟล์ใน volume และ tmpfs

```bash
kubectl exec spod -- ls -la /etc/secret /etc/secret400/..data/
kubectl exec spod -- ls -laL /etc/secret400
kubectl exec spod -- mount | grep -E "secret|serviceaccount"
kubectl exec spod -- cat /etc/secret/password; echo
```

```text
/etc/secret:
total 4
drwxrwxrwt    3 root     root           120 Oct  5 11:32 .
drwxr-xr-x    1 root     root          4096 Oct  5 11:32 ..
drwxr-xr-x    2 root     root            80 Oct  5 11:32 ..2026_10_05_11_32_18.406880621
lrwxrwxrwx    1 root     root            31 Oct  5 11:32 ..data -> ..2026_10_05_11_32_18.406880621
lrwxrwxrwx    1 root     root            15 Oct  5 11:32 password -> ..data/password
lrwxrwxrwx    1 root     root            15 Oct  5 11:32 username -> ..data/username

/etc/secret400/..data/:
total 8
drwxr-xr-x    2 root     root            80 Oct  5 11:32 .
drwxrwxrwt    3 root     root           120 Oct  5 11:32 ..
-r--------    1 root     root             8 Oct  5 11:32 password
-r--------    1 root     root             3 Oct  5 11:32 username
total 12
drwxrwxrwt    3 root     root           120 Oct  5 11:32 .
drwxr-xr-x    1 root     root          4096 Oct  5 11:32 ..
drwxr-xr-x    2 root     root            80 Oct  5 11:32 ..2026_10_05_11_32_18.1947603794
drwxr-xr-x    2 root     root            80 Oct  5 11:32 ..data
-r--------    1 root     root             8 Oct  5 11:32 password
-r--------    1 root     root             3 Oct  5 11:32 username
tmpfs on /etc/secret type tmpfs (ro,relatime,size=64489564k,noswap)
tmpfs on /etc/secret400 type tmpfs (ro,relatime,size=64489564k,noswap)
tmpfs on /var/run/secrets/kubernetes.io/serviceaccount type tmpfs (ro,relatime,size=64489564k,noswap)
meow1234
```

- แต่ละ key เป็นไฟล์ (symlink ผ่าน `..data` เหมือน ConfigMap ในบทที่ 10) เนื้อไฟล์เป็นค่าที่ **ถอด base64 แล้ว**
- `defaultMode: 0400` → `-r--------` (`ls -laL` ตาม symlink ให้เห็นสิทธิ์ของไฟล์จริง)
- ทุก mount ของ Secret เป็น **tmpfs (ro, noswap)** รวมถึง token ของ ServiceAccount ที่ Pod ได้อัตโนมัติ — ถาดฟองน้ำความจำที่ไม่เขียนลงดิสก์ของ Node

### ขั้นที่ 4: env รั่วผ่าน /proc และไฟล์แก้ไม่ได้

```bash
kubectl exec spod -- cat /proc/1/environ | tr '\0' '\n' | grep DB_
kubectl exec spod -- sh -c "echo hack > /etc/secret/password"
```

```text
DB_PASSWORD=meow1234
sh: can't create /etc/secret/password: Read-only file system
command terminated with exit code 1
```

env ของ process หลัก (PID 1) อ่านได้จาก `/proc/1/environ` ใครที่ `exec` เข้า container ได้ก็เห็นรหัสทั้งหมด ส่วนไฟล์ใน volume เขียนทับไม่ได้ (`Read-only file system`)

<p align="center" id="fig-5">
  <img src="images/05-lab3-update.png" alt="รูปที่ 5 LAB 3 อัปเดตและ immutable" width="900"><br>
  <em><b>รูปที่ 5</b> LAB3 (ต่อ): patch Secret demo → ไฟล์ /etc/secret/password เปลี่ยนในราว 1 นาที (71–81 วินาที) ส่วน env DB_PASSWORD ยังเป็นค่าเดิม; immutable frozen แก้ไม่ได้</em>
</p>

### ขั้นที่ 5: แก้ Secret แล้วจับเวลา

สคริปต์ `wait-secret.sh` สั่ง `kubectl patch secret demo` เปลี่ยน `password` แล้ววนอ่าน `/etc/secret/password` ทุก 1 วินาทีจนกว่าจะเป็นค่าใหม่ (ไม่เกิน 180 วินาที) จากนั้นพิมพ์ค่าในไฟล์ `0400` และ env

```bash
./wait-secret.sh newpass-00
./wait-secret.sh newpass-01
```

```text
secret/demo patched
18:32:25 patch secret demo → password=newpass-00
  ไฟล์ /etc/secret/password เปลี่ยนหลัง 71 วินาที: newpass-00
  ไฟล์ /etc/secret400/password       : newpass-00
  env DB_PASSWORD (ไม่เปลี่ยน)        : meow1234
secret/demo patched
18:33:37 patch secret demo → password=newpass-01
  ไฟล์ /etc/secret/password เปลี่ยนหลัง 81 วินาที: newpass-01
  ไฟล์ /etc/secret400/password       : newpass-01
  env DB_PASSWORD (ไม่เปลี่ยน)        : meow1234
```

ไฟล์ใน volume เปลี่ยนเองภายใน **ราว 1 นาที** (เครื่องทดลองได้ 71 และ 81 วินาที เครื่องนักศึกษาอาจเร็วหรือช้ากว่านี้ แต่ปกติไม่เกินราว 1.5 นาที) เพราะ kubelet sync เป็นรอบ ส่วน env ยังเป็น `meow1234` เพราะถูกคัดลอกครั้งเดียวตอน container เริ่ม ถ้าได้ `Permission denied` ให้รันด้วย `bash wait-secret.sh newpass-00`

### ขั้นที่ 6: Pod ใหม่ได้ค่าใหม่

```bash
kubectl delete pod spod --wait=true; kubectl apply -f spod.yaml && kubectl wait --for=condition=Ready pod/spod --timeout=120s && kubectl exec spod -- printenv DB_PASSWORD
```

```text
pod "spod" deleted from default namespace
pod/spod created
pod/spod condition met
newpass-01
```

### ขั้นที่ 7: ซองเคลือบ immutable

```bash
kubectl apply -f frozen.yaml; kubectl get secret frozen
kubectl patch secret frozen --type merge -p '{"stringData":{"API_KEY":"example-key-v2"}}'
kubectl patch secret frozen --type merge -p '{"immutable":false}'
kubectl delete secret frozen && sed "s/example-key-v1/example-key-v2/" frozen.yaml | kubectl apply -f - && kubectl get secret frozen -o jsonpath="{.data.API_KEY}" | base64 -d; echo
```

```text
secret/frozen created
NAME     TYPE     DATA   AGE
frozen   Opaque   1      0s
The Secret "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
The Secret "frozen" is invalid: immutable: Forbidden: field is immutable when `immutable` is set
secret "frozen" deleted from default namespace
secret/frozen created
example-key-v2
```

แก้ค่าไม่ได้ และปิด `immutable` ก็ไม่ได้ ทางเดียวคือลบแล้วสร้างใหม่ (คำสั่งสุดท้ายใช้ `sed` แก้ค่าระหว่างทางแล้วส่งเข้า `kubectl apply -f -` โดยไม่แก้ไฟล์ต้นฉบับ)

### สิ่งที่เห็น

- env `DB_PASSWORD=meow1234`, `SD_PASSWORD=override-by-stringData`, `SD_USERNAME=som`
- `tmpfs on /etc/secret type tmpfs (ro,relatime,...,noswap)`, `defaultMode: 0400` → `-r--------`, เขียนไฟล์ได้ `Read-only file system`
- แก้ Secret → ไฟล์เปลี่ยนในราว 1 นาที (71/81 วินาที) env ค่าเดิม → Pod ใหม่ได้ `newpass-01`
- `immutable` → `Forbidden: field is immutable when \`immutable\` is set` ต้องลบสร้างใหม่

> **เก็บไว้:** Pod `spod` ใช้ต่อใน LAB 7 และ Secret `demo` ตอนนี้มี `password=newpass-01` (LAB 6, 7, 8 จะเห็นค่านี้)

**คำถามชวนคิด**

1. ทำไมผลของ `wait-secret.sh` สองรอบจึงได้เวลาไม่เท่ากัน (71 กับ 81 วินาที) และควรออกแบบแอปอย่างไรถ้าต้องการให้รหัสใหม่มีผลทันที
2. ถ้าเปลี่ยน `defaultMode` เป็น `0400` แต่ container รันเป็นผู้ใช้ uid 1000 จะเกิดอะไรขึ้นเมื่อแอปอ่านไฟล์

---

## LAB 4: TLS Secret และ nginx HTTPS

<p align="center" id="fig-6">
  <img src="images/06-lab4-tls-nginx.png" alt="รูปที่ 6 LAB 4 TLS และ nginx HTTPS" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4: openssl สร้าง cert CN=shop.som.local → secret tls shop-tls → nginx 443 ssl + NodePort 30081: curl ได้ (60) self-signed, curl -k ได้ HTTPS ร้านน้องส้ม, --cacert ผ่าน</em>
</p>

**เป้าหมาย:** สร้างใบรับรอง self-signed ด้วย openssl เก็บเป็น Secret ชนิด `kubernetes.io/tls` ให้ nginx ใช้เปิด HTTPS ผ่าน NodePort 30081 แล้วทดสอบด้วย curl ทั้งแบบข้ามการตรวจ (`-k`) และแบบตรวจจริง (`--cacert`)

**ไฟล์:** `labs/lab04-tls/tls.yaml` (ConfigMap `ngx-tls-conf` + Pod `ngx-tls` + Service NodePort 30081)

### ขั้นที่ 1: ออกใบรับรองให้ตัวเอง

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab04-tls
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.som.local' -addext 'subjectAltName=DNS:shop.som.local,DNS:localhost'; ls -la tls.*
openssl x509 -in tls.crt -noout -subject -issuer -enddate -ext subjectAltName
```

```text
...........+......+++++++++++++++++++++++++++++++++++++++...
-----
-rw-r--r-- 1 root root 1180 Oct  5 18:35 tls.crt
-rw------- 1 root root 1704 Oct  5 18:35 tls.key
-rw-r--r-- 1 root root 1697 Oct  5 18:00 tls.yaml
subject=CN = shop.som.local
issuer=CN = shop.som.local
notAfter=Oct  5 11:35:09 2027 GMT
X509v3 Subject Alternative Name: 
    DNS:shop.som.local, DNS:localhost
```

| ตัวเลือก | ความหมาย |
|---|---|
| `req -x509` | สร้างใบรับรองที่เซ็นเอง (ไม่ใช่คำขอส่ง CA) |
| `-nodes` | ไม่ตั้งรหัสผ่านให้ไฟล์กุญแจ (nginx เปิดเองได้) |
| `-newkey rsa:2048` | สร้างกุญแจ RSA 2048 บิตใหม่ → `tls.key` |
| `-days 365` | ใช้ได้ 1 ปี (`notAfter=... 2027`) |
| `-subj '/CN=shop.som.local'` | ชื่อในใบรับรอง |
| `-addext 'subjectAltName=...'` | ชื่อที่ browser/curl ใช้ตรวจจริง ใส่ทั้ง `shop.som.local` และ `localhost` |

จุดและ `+` หลายบรรทัดคือ progress ตอนสร้างกุญแจ เป็นเรื่องปกติ สังเกตว่า openssl สร้าง `tls.key` ด้วยสิทธิ์ `-rw-------` ให้เอง และ `subject` = `issuer` คือลักษณะของ self-signed

### ขั้นที่ 2: สร้าง Secret ชนิด TLS

```bash
kubectl create secret tls shop-tls --cert=tls.crt --key=tls.key; kubectl get secret shop-tls; kubectl describe secret shop-tls | tail -4
kubectl create secret tls badtls --cert=tls.crt --key=../lab02-types/pw.txt
```

```text
secret/shop-tls created
NAME       TYPE                DATA   AGE
shop-tls   kubernetes.io/tls   2      0s
Data
====
tls.crt:  1180 bytes
tls.key:  1704 bytes
error: tls: failed to find any PEM data in key input
```

ถ้า key ไม่ใช่ไฟล์ PEM จะได้ `... in key input` (ต่างจาก LAB 2 ที่ cert ผิดก่อน)

### ขั้นที่ 3: เปิด nginx HTTPS แล้ว curl

ส่วนสำคัญของ `tls.yaml`: ConfigMap ให้ nginx `listen 443 ssl` และชี้ไฟล์ใบรับรองไปที่ `/etc/nginx/tls/` ซึ่ง mount จาก Secret `shop-tls` ด้วย `defaultMode: 0400` และ Service `ngx-tls` เปิด NodePort `30081`

```bash
kubectl apply -f tls.yaml && kubectl wait --for=condition=Ready pod/ngx-tls --timeout=120s; curl -sS https://localhost:30081/; echo "rc=$?"
```

```text
configmap/ngx-tls-conf created
pod/ngx-tls created
service/ngx-tls created
pod/ngx-tls condition met
curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to localhost:30081 
rc=35
```

`rc=35` เกิดเพราะ curl ทันทีหลัง Pod Ready เส้นทางของ NodePort ยังไม่พร้อม **รอราว 5 วินาทีแล้วลองใหม่**

```bash
sleep 5; curl -sS https://localhost:30081/; echo "rc=$?"
```

```text
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
rc=60
```

ตอนนี้ HTTPS ทำงานแล้ว แต่ curl ไม่เชื่อใบรับรองที่เซ็นเอง (`rc=60`)

### ขั้นที่ 4: ข้ามการตรวจ กับ ตรวจจริง

```bash
curl -sk https://localhost:30081/
curl -s --cacert tls.crt https://localhost:30081/
curl -s --cacert tls.crt --resolve shop.som.local:30081:127.0.0.1 https://shop.som.local:30081/
curl -sS --cacert tls.crt https://127.0.0.1:30081/; echo "rc=$?"
curl -sS http://localhost:30081/ | head -3
```

```text
HTTPS ร้านน้องส้ม
HTTPS ร้านน้องส้ม
HTTPS ร้านน้องส้ม
curl: (60) SSL: no alternative certificate subject name matches target host name '127.0.0.1'
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
rc=60
<html>
<head><title>400 The plain HTTP request was sent to HTTPS port</title></head>
<body>
```

| คำสั่ง | ผล | ตรวจใบรับรองไหม |
|---|---|---|
| `curl -sk` | ผ่าน | ❌ ข้ามทั้งหมด (ใช้ทดสอบเท่านั้น) |
| `curl --cacert tls.crt https://localhost:30081/` | ผ่าน | ✅ เชื่อใบรับรองนี้และชื่อ `localhost` อยู่ใน SAN |
| `--resolve shop.som.local:30081:127.0.0.1` | ผ่าน | ✅ เรียกด้วยชื่อในใบรับรองโดยไม่แก้ DNS |
| `https://127.0.0.1:30081/` + `--cacert` | `(60)` ชื่อไม่ตรง | ✅ ตรวจแล้วไม่ผ่าน เพราะ `127.0.0.1` ไม่อยู่ใน SAN |
| `http://localhost:30081/` | `400 The plain HTTP request was sent to HTTPS port` | – ส่ง http ไปพอร์ต https |

### ขั้นที่ 5: ส่องใบรับรองที่เซิร์ฟเวอร์ส่งมาและไฟล์ใน Pod

```bash
curl -skv https://localhost:30081/ 2>&1 | grep -E "subject:|issuer:|SSL connection|expire date"
openssl s_client -connect localhost:30081 -servername shop.som.local </dev/null 2>/dev/null | openssl x509 -noout -subject -enddate
kubectl exec ngx-tls -- ls -laL /etc/nginx/tls; kubectl exec ngx-tls -- mount | grep nginx/tls
```

```text
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519 / RSASSA-PSS
*  subject: CN=shop.som.local
*  expire date: Oct  5 11:35:09 2027 GMT
*  issuer: CN=shop.som.local
subject=CN = shop.som.local
notAfter=Oct  5 11:35:09 2027 GMT
total 12
drwxrwxrwt    3 root     root           120 Oct  5 11:35 .
drwxr-xr-x    1 root     root          4096 Oct  5 11:35 ..
drwxr-xr-x    2 root     root            80 Oct  5 11:35 ..2026_10_05_11_35_10.594231088
drwxr-xr-x    2 root     root            80 Oct  5 11:35 ..data
-r--------    1 root     root          1180 Oct  5 11:35 tls.crt
-r--------    1 root     root          1704 Oct  5 11:35 tls.key
tmpfs on /etc/nginx/tls type tmpfs (ro,relatime,size=64489564k,noswap)
```

การเชื่อมต่อใช้ TLSv1.3 ใบรับรองที่ได้คือของเราเอง กุญแจ `tls.key` ใน Pod เป็น `-r--------` บน tmpfs (nginx master รันเป็น root จึงอ่านได้)

### ขั้นที่ 6: เปิดจาก browser

🌐 **browser บนเครื่องนักศึกษา** เปิด `https://localhost:30081` browser จะเตือนว่าการเชื่อมต่อไม่เป็นส่วนตัว (`NET::ERR_CERT_AUTHORITY_INVALID`) เพราะใบรับรองไม่ได้ออกโดย CA ที่ browser รู้จัก กด **Advanced → Proceed to localhost (unsafe)** จะเห็นข้อความ `HTTPS ร้านน้องส้ม` (การทดลองยืนยันจากนอก container แล้วว่า `-k` ได้ข้อความนี้ และแบบไม่ `-k` ได้ `(60) SSL certificate problem: self-signed certificate` เหมือนกัน) หน้าจอเตือนแบบเดียวกันมีภาพหน้าจอจริงใน LAB 9

### สิ่งที่เห็น

- ใบรับรอง `subject=CN = shop.som.local`, `notAfter=Oct  5 11:35:09 2027 GMT` (วันที่ในเครื่องนักศึกษาจะเป็น 1 ปีนับจากวันที่สร้าง)
- curl ทันทีหลัง Ready → `rc=35` รอ 5 วินาที → `(60) self-signed certificate` → `-k`/`--cacert`/`--resolve` ได้ `HTTPS ร้านน้องส้ม`
- `127.0.0.1` ไม่ผ่านเพราะไม่อยู่ใน subjectAltName, http ไปพอร์ต https ได้ `400`
- ไฟล์ใน Pod `-r--------` บน tmpfs

> **เก็บไว้:** ไฟล์ `tls.crt` และ `tls.key` ในโฟลเดอร์นี้ใช้ต่อใน LAB 9 ขั้น E (`.gitignore` ของร้านกัน `*.key`/`*.crt` ไม่ให้เข้า git) Pod/Service `ngx-tls` จะลบรวมท้าย LAB 8 (คืน NodePort 30081)

**คำถามชวนคิด**

1. ถ้าลืมใส่ `DNS:localhost` ใน `-addext` คำสั่ง `curl --cacert tls.crt https://localhost:30081/` จะได้ผลอะไร
2. ทำไม `tls.crt` แจกให้ใครก็ได้ แต่ `tls.key` ต้องเก็บใน Secret และตั้ง `defaultMode: 0400`

---

## LAB 5: imagePullSecrets กับ registry ส่วนตัว

<p align="center" id="fig-7">
  <img src="images/07-lab5-private-registry.png" alt="รูปที่ 7 LAB 5 registry ส่วนตัว" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: registry:2 + htpasswd บน network kind (kind-registry:5000) → push som-menu:1.0 → Pod ไม่มีบัตร ErrImagePull, regcred ถูก Running, wrongcred 401 Unauthorized; ผูก regcred ที่ ServiceAccount default ได้</em>
</p>

**เป้าหมาย:** เปิด registry ส่วนตัวที่ต้อง login (`registry:2` + htpasswd) บน network `kind` ฝาก image `som-menu:1.0` แล้วดูว่า Pod ที่ไม่มีบัตร / มีบัตรถูก / บัตรผิด / ได้บัตรจาก ServiceAccount เป็นอย่างไร และทดสอบว่า image ที่ค้างบน Node ถูก Pod ที่ไม่มีบัตรยืมใช้ได้หรือไม่

**ไฟล์:** `labs/lab05-registry/` (`setup-registry.sh`, `cleanup-registry.sh`, `Dockerfile`, `menu.txt`, `00-ns.yaml`, `1-nopull.yaml` … `5-cached.yaml`)

> ⚠️ **ทำไมใช้ image แยกชื่อ `som-menu:1.0`:** kubelet v1.37 จำว่า image ใดถูกดึงมาด้วยบัตรใด ถ้านำ image ของร้าน (`som-shop-web:1.5` ตัวเดียวกันทุกไบต์กับที่ `kind load` ไว้) ขึ้น registry แล้วดึงด้วยบัตร Pod ร้านที่ไม่มีบัตรบน Node นั้นอาจดึง image ไม่ได้อีก (เกิดจริงตอนเตรียม LAB) **ห้ามใช้ image ของร้านใน LAB นี้ และห้าม `crictl rmi`** บน Node

### ขั้นที่ 1: เปิดคลังตู้สินค้าส่วนตัว

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab05-registry
docker network ls | grep kind
./setup-registry.sh
```

สคริปต์ทำ 4 อย่าง (ผลจริง ตัดบรรทัดดาวน์โหลด image ออก)

```text
26e2abb77664   kind      bridge    local
== 1) สร้างไฟล์รหัสผ่าน auth/htpasswd (bcrypt) ด้วยคำสั่ง htpasswd ใน image httpd
...
Status: Downloaded newer image for httpd:2.4-alpine
som:$2y$05$2

   (ตัดให้เห็นแค่ต้นบรรทัด)
== 2) เปิด registry ชื่อ kind-registry บน network kind (Node ของ kind มองเห็นด้วยชื่อนี้)
...
Status: Downloaded newer image for registry:2
d241ce17ae3b9bd5a455ed2816ec6fafee49a10e51973dda51f5a7a2c500471b
   ไม่ใส่รหัส: HTTP 401  (401 = ต้องมีบัตร)
== 3) docker login แล้ว build + push som-menu:1.0
Login Succeeded

WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

sha256:f2364f78a94e4d6a9cbd34c1e8b8b8bc547789f8b5a63815e224bf3ecb78ac56
localhost:5001/som-menu:1.0
== 4) บอก containerd ทุก Node ว่า kind-registry:5000 เป็น http (ไม่มี TLS) — ไม่ต้อง restart containerd
   lab-worker: /etc/containerd/certs.d/kind-registry:5000/hosts.toml
   lab-control-plane: /etc/containerd/certs.d/kind-registry:5000/hosts.toml
   lab-worker2: /etc/containerd/certs.d/kind-registry:5000/hosts.toml
เสร็จ: image ในคลัสเตอร์ = kind-registry:5000/som-menu:1.0
```

| ขั้นในสคริปต์ | ทำอะไร |
|---|---|
| 1 | k8s-lab ไม่มีคำสั่ง `htpasswd` จึงรันใน image `httpd:2.4-alpine` สร้างไฟล์ `auth/htpasswd` (user `som` รหัสตัวอย่าง `example-pass` แบบ bcrypt) |
| 2 | `docker run ... --name kind-registry --network kind -p 127.0.0.1:5001:5000 ... registry:2` เปิด registry ที่ Node ของ kind เรียกด้วยชื่อ `kind-registry:5000` ส่วนใน k8s-lab เรียก `localhost:5001` ไม่ใส่รหัสได้ HTTP 401 |
| 3 | `docker login` แล้ว build + push `som-menu:1.0` (busybox + `menu.txt`) สังเกตคำเตือน **docker เก็บรหัสไว้ใน `~/.docker/config.json` แบบไม่เข้ารหัส** (base64 เหมือน Secret) |
| 4 | เขียน `hosts.toml` ให้ containerd ทุก Node รู้ว่า `kind-registry:5000` เป็น http (registry ใน LAB ไม่มี TLS) มีผลทันทีไม่ต้อง restart containerd |

ตรวจว่าคลังมี image และ Node ได้การตั้งค่าแล้ว

```bash
curl -s -u som:example-pass http://localhost:5001/v2/_catalog; curl -s -u som:example-pass http://localhost:5001/v2/som-menu/tags/list
docker exec lab-worker cat /etc/containerd/certs.d/kind-registry:5000/hosts.toml
```

```text
{"repositories":["som-menu"]}
{"name":"som-menu","tags":["1.0"]}
[host."http://kind-registry:5000"]
  capabilities = ["pull", "resolve"]
```

### ขั้นที่ 2: ไม่มีบัตร

```bash
kubectl apply -f 00-ns.yaml -f 1-nopull.yaml; sleep 20; kubectl -n reg get pod nopull
kubectl -n reg describe pod nopull | grep -E 'Failed|BackOff' | tail -3
```

```text
namespace/reg created
namespace/reg2 created
pod/nopull created
NAME     READY   STATUS             RESTARTS   AGE
nopull   0/1     ImagePullBackOff   0          20s
  Warning  Failed     19s               kubelet            spec.containers{menu}: Error: ImagePullBackOff
  Warning  Failed     6s (x2 over 20s)  kubelet            spec.containers{menu}: Failed to pull image "kind-registry:5000/som-menu:1.0": failed to pull and unpack image "kind-registry:5000/som-menu:1.0": failed to resolve reference "kind-registry:5000/som-menu:1.0": pull access denied, repository does not exist or may require authorization: authorization failed: no basic auth credentials
  Warning  Failed     6s (x2 over 20s)  kubelet            spec.containers{menu}: Error: ErrImagePull
```

STATUS สลับระหว่าง `ErrImagePull` (เพิ่งลองดึงแล้วพลาด) และ `ImagePullBackOff` (รอก่อนลองใหม่) ข้อความที่บอกสาเหตุคือ `no basic auth credentials`

### ขั้นที่ 3: มีบัตรถูก

```bash
kubectl -n reg create secret docker-registry regcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=example-pass; kubectl -n reg get secret regcred
kubectl apply -f 2-withpull.yaml; kubectl -n reg wait --for=condition=Ready pod/withpull --timeout=90s; kubectl -n reg get pod withpull -o wide
kubectl -n reg describe pod withpull | grep -E 'Pulling|Pulled' ; kubectl -n reg logs withpull
```

```text
secret/regcred created
NAME      TYPE                             DATA   AGE
regcred   kubernetes.io/dockerconfigjson   1      0s
pod/withpull created
pod/withpull condition met
NAME       READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
withpull   1/1     Running   0          1s    10.244.2.3   lab-worker   <none>           <none>
  Normal  Pulling  0s    kubelet  spec.containers{menu}: Pulling image "kind-registry:5000/som-menu:1.0"
  Normal  Pulled   0s    kubelet  spec.containers{menu}: Successfully pulled image "kind-registry:5000/som-menu:1.0" in 311ms (311ms including waiting). Image size: 2208941 bytes.
เมนูลับของน้องส้ม: ปลาทูย่างซีอิ๊ว 🐟
```

`--docker-server` ต้องตรงกับชื่อ registry ที่อยู่ในชื่อ image (`kind-registry:5000`) Secret `regcred` ต้องอยู่ namespace เดียวกับ Pod (`reg`) และ `2-withpull.yaml` ตรึง Pod ไว้ที่ `lab-worker` ด้วย `nodeName` เพื่อใช้ในขั้นที่ 6

### ขั้นที่ 4: บัตรผิด

```bash
kubectl -n reg create secret docker-registry wrongcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=wrong-pass; kubectl apply -f 3-wrong.yaml; sleep 20; kubectl -n reg get pod wrong
kubectl -n reg describe pod wrong | grep -E 'Failed' | tail -3
```

```text
secret/wrongcred created
pod/wrong created
NAME    READY   STATUS             RESTARTS   AGE
wrong   0/1     ImagePullBackOff   0          20s
  Warning  Failed     19s               kubelet            spec.containers{menu}: Error: ImagePullBackOff
  Warning  Failed     9s (x2 over 20s)  kubelet            spec.containers{menu}: Failed to pull image "kind-registry:5000/som-menu:1.0": failed to pull and unpack image "kind-registry:5000/som-menu:1.0": failed to resolve reference "kind-registry:5000/som-menu:1.0": unexpected status from HEAD request to http://kind-registry:5000/v2/som-menu/manifests/1.0: 401 Unauthorized
  Warning  Failed     9s (x2 over 20s)  kubelet            spec.containers{menu}: Error: ErrImagePull
```

บัตรผิดได้ `401 Unauthorized` (ต่างจากไม่มีบัตรที่ได้ `no basic auth credentials`) `3-wrong.yaml` ตั้ง `imagePullPolicy: Always` ให้ถามคลังทุกครั้ง

### ขั้นที่ 5: ผูกบัตรกับ ServiceAccount

```bash
kubectl -n reg patch sa default -p '{"imagePullSecrets":[{"name":"regcred"}]}'; kubectl -n reg get sa default -o yaml | grep -A1 imagePullSecrets
kubectl apply -f 4-viasa.yaml; kubectl -n reg wait --for=condition=Ready pod/viasa --timeout=90s; kubectl -n reg get pod viasa -o jsonpath='{.spec.imagePullSecrets}{"  "}{.status.phase}{"  "}{.spec.nodeName}'; echo
```

```text
serviceaccount/default patched
imagePullSecrets:
- name: regcred
pod/viasa created
pod/viasa condition met
[{"name":"regcred"}]  Running  lab-worker2
```

`4-viasa.yaml` ไม่ได้เขียน `imagePullSecrets` เลย แต่ Pod ที่ใช้ ServiceAccount `default` ของ `reg` ได้บัตร `regcred` เติมให้ตอนสร้าง ทุก Pod ใหม่ใน namespace นี้จึงดึง image ส่วนตัวได้โดยไม่ต้องแก้ YAML

<p align="center" id="fig-8">
  <img src="images/08-lab5-cached-recheck.png" alt="รูปที่ 8 LAB 5 kubelet ตรวจบัตรซ้ำ" width="900"><br>
  <em><b>รูปที่ 8</b> LAB5 (ต่อ): Pod ใน namespace อื่นที่ไม่มีบัตร ตรึงลง Node ที่มี image แล้ว → ยัง ErrImagePull (kubelet v1.37 ตรวจบัตรซ้ำ) — เพราะฉะนั้น LAB นี้ใช้ image แยก som-menu ไม่ใช้ som-shop-web</em>
</p>

### ขั้นที่ 6: Pod ที่ไม่มีบัตรยืม image ที่ค้างบน Node ได้ไหม

`5-cached.yaml` สร้าง Pod `cached` ใน namespace `reg2` (ไม่มีบัตร) ตรึงลง `lab-worker` ที่ `withpull` ดึง image มาแล้ว และตั้ง `imagePullPolicy: IfNotPresent`

```bash
kubectl apply -f 5-cached.yaml; sleep 20; kubectl -n reg2 get pod cached -o wide
kubectl -n reg2 describe pod cached | grep -E 'Failed|Pulled|already|Pulling' | tail -4
docker exec lab-worker crictl images | grep -E "som-menu|som-shop|IMAGE"
```

```text
pod/cached created
NAME     READY   STATUS             RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
cached   0/1     ImagePullBackOff   0          20s   10.244.2.4   lab-worker   <none>           <none>
  Warning  Failed   19s               kubelet  spec.containers{menu}: Error: ImagePullBackOff
  Normal   Pulling  5s (x2 over 20s)  kubelet  spec.containers{menu}: Pulling image "kind-registry:5000/som-menu:1.0"
  Warning  Failed   5s (x2 over 20s)  kubelet  spec.containers{menu}: Failed to pull image "kind-registry:5000/som-menu:1.0": failed to pull and unpack image "kind-registry:5000/som-menu:1.0": failed to resolve reference "kind-registry:5000/som-menu:1.0": pull access denied, repository does not exist or may require authorization: authorization failed: no basic auth credentials
  Warning  Failed   5s (x2 over 20s)  kubelet  spec.containers{menu}: Error: ErrImagePull
IMAGE                                           TAG                  IMAGE ID            SIZE
docker.io/library/som-shop-web                  1.5                  b0b30ef64ac6d       76.7MB
kind-registry:5000/som-menu                     1.0                  bcf5797065c37       2.21MB
```

แม้ image อยู่บน `lab-worker` แล้ว kubelet ยังไปขอสิทธิ์จาก registry ใหม่ (`Pulling` อีกครั้ง) และล้มเหลวเพราะ Pod นี้ไม่มีบัตร นี่คือการตรวจสิทธิ์ซ้ำของ kubelet ใน v1.37 ที่กันไม่ให้ Pod ใน namespace อื่นแอบใช้ image ส่วนตัว ส่วน image ของร้านที่ `kind load` ไว้ยังใช้ได้ตามปกติ

```bash
kubectl -n reg2 run shopcheck --image=som-shop-web:1.5 --image-pull-policy=IfNotPresent --restart=Never --overrides='{"spec":{"nodeName":"lab-worker"}}' --command -- node -e "console.log(\"som-shop-web:1.5 ok\")"; sleep 10; kubectl -n reg2 get pod shopcheck; kubectl -n reg2 logs shopcheck
```

```text
pod/shopcheck created
NAME        READY   STATUS      RESTARTS   AGE
shopcheck   0/1     Completed   0          10s
som-shop-web:1.5 ok
```

### ขั้นที่ 7: ภาพรวมและเก็บกวาด

```bash
kubectl get pod -A -o wide | grep -E "reg|NAME"
./cleanup-registry.sh
docker ps -a | grep kind-registry || echo "ไม่มี kind-registry แล้ว"
```

```text
NAMESPACE            NAME                                        READY   STATUS             RESTARTS   AGE     IP           NODE                NOMINATED NODE   READINESS GATES
reg                  nopull                                      0/1     ImagePullBackOff   0          75s     10.244.1.4   lab-worker2         <none>           <none>
reg                  viasa                                       1/1     Running            0          32s     10.244.1.6   lab-worker2         <none>           <none>
reg                  withpull                                    1/1     Running            0          55s     10.244.2.3   lab-worker          <none>           <none>
reg                  wrong                                       0/1     ErrImagePull       0          53s     10.244.1.5   lab-worker2         <none>           <none>
reg2                 cached                                      0/1     ErrImagePull       0          31s     10.244.2.4   lab-worker          <none>           <none>
reg2                 shopcheck                                   0/1     Completed          0          11s     10.244.2.5   lab-worker          <none>           <none>
namespace "reg" deleted
namespace "reg2" deleted
kind-registry
Removing login credentials for localhost:5001
ไม่มี kind-registry แล้ว
```

`cleanup-registry.sh` ลบ namespace `reg`/`reg2` (รวม Secret `regcred`, `wrongcred`) ปิด container `kind-registry`, `docker logout localhost:5001` (ลบรหัสออกจาก `~/.docker/config.json`), ลบ image `localhost:5001/som-menu:1.0` ใน k8s-lab และลบโฟลเดอร์ `auth/` **รันทุกครั้งที่จบ LAB นี้** ถ้าได้ `Permission denied` ให้ใช้ `bash setup-registry.sh` / `bash cleanup-registry.sh`

### สิ่งที่เห็น

- `registry:2` + htpasswd ไม่ใส่รหัสได้ HTTP 401
- ไม่มีบัตร → `ErrImagePull`/`ImagePullBackOff` + `no basic auth credentials`; บัตรถูก → `Running` (`Successfully pulled ... in 311ms`); บัตรผิด → `401 Unauthorized`
- ผูกบัตรกับ ServiceAccount `default` → Pod ได้ `[{"name":"regcred"}]` อัตโนมัติ
- Pod ใน `reg2` ที่ไม่มีบัตรยืม image ที่ค้างบน Node ไม่ได้ แต่ `som-shop-web:1.5` ที่ `kind load` ไว้ใช้ได้ (`som-shop-web:1.5 ok`)

**คำถามชวนคิด**

1. ทำไม `docker login` จึงเตือนว่าเก็บรหัส "unencrypted" ทั้งที่ไฟล์ `config.json` เก็บ `auth` เป็น base64 (เชื่อมกับ LAB 1)
2. ถ้าทุก namespace ต้องดึง image จาก registry ส่วนตัวเดียวกัน จะต้องสร้าง Secret `regcred` กี่ชุด และผูกกับอะไร

---

## LAB 6: projected volume และ token ของ ServiceAccount

<p align="center" id="fig-9">
  <img src="images/09-lab6-projected-token.png" alt="รูปที่ 9 LAB 6 projected และ token" width="900"><br>
  <em><b>รูปที่ 9</b> LAB6: Pod proj รวม announcement.txt + db/password + pod-name ใน /etc/som (โหมด 0440); Secret service-account-token ของ builder ถูกเติม token/ca.crt/namespace และ describe แสดง token เต็ม</em>
</p>

**เป้าหมาย:** รวมไฟล์จาก ConfigMap, Secret และ Downward API ไว้ในโฟลเดอร์เดียวด้วย projected volume ส่องโฟลเดอร์ token ที่ Pod ได้อัตโนมัติ และเทียบ token ถาวร (Secret ชนิด `service-account-token`) กับ token ที่มีอายุ (`kubectl create token`)

**ไฟล์:** `labs/lab06-projected/proj.yaml` (ConfigMap `shop-board` + Pod `proj`), `builder-token.yaml` (ServiceAccount `builder` + Secret `builder-token`)

### ขั้นที่ 1: แฟ้มห่วงรวมเอกสาร

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab06-projected
kubectl apply -f proj.yaml && kubectl wait --for=condition=Ready pod/proj --timeout=120s
kubectl exec proj -- ls -laLR /etc/som
```

ส่วน volume ของ `proj.yaml` รวม 3 แหล่ง: `configMap` (`shop-board` → `announcement.txt`), `secret` (`demo` key `password` → `db/password`) และ `downwardAPI` (`metadata.name` → `pod-name`) ตั้ง `defaultMode: 0440` ร่วมกัน ผลจริง (ตัดโฟลเดอร์ `..2026_…` และ `..data` ที่ซ้ำกันออก)

```text
configmap/shop-board created
pod/proj created
pod/proj condition met
/etc/som:
total 12
drwxrwxrwt    3 root     root           140 Oct  5 11:37 .
drwxr-xr-x    1 root     root          4096 Oct  5 11:37 ..
drwxr-xr-x    3 root     root           100 Oct  5 11:37 ..2026_10_05_11_37_24.2616867840
drwxr-xr-x    3 root     root           100 Oct  5 11:37 ..data
-r--r-----    1 root     root            54 Oct  5 11:37 announcement.txt
drwxr-xr-x    2 root     root            60 Oct  5 11:37 db
-r--r-----    1 root     root             4 Oct  5 11:37 pod-name
...
/etc/som/db:
total 4
drwxr-xr-x    2 root     root            60 Oct  5 11:37 .
drwxr-xr-x    3 root     root           100 Oct  5 11:37 ..
-r--r-----    1 root     root            10 Oct  5 11:37 password
```

```bash
kubectl exec proj -- sh -c "cat /etc/som/pod-name; echo; cat /etc/som/db/password; echo; cat /etc/som/announcement.txt"
kubectl exec proj -- mount | grep /etc/som
```

```text
proj
newpass-01
วันนี้ปลาทูสดมาก 🐟
tmpfs on /etc/som type tmpfs (ro,relatime,size=64489564k,noswap)
```

ทุกไฟล์เป็น `-r--r-----` (0440) `db/password` ได้ค่าปัจจุบันของ Secret `demo` (`newpass-01` จาก LAB 3) และเพราะมี Secret รวมอยู่ ทั้งโฟลเดอร์จึงเป็น tmpfs

### ขั้นที่ 2: token ที่ Pod ได้อัตโนมัติ

```bash
kubectl exec proj -- ls -la /var/run/secrets/kubernetes.io/serviceaccount/
```

```text
total 4
drwxrwxrwt    3 root     root           140 Oct  5 11:37 .
drwxr-xr-x    3 root     root          4096 Oct  5 11:37 ..
drwxr-xr-x    2 root     root           100 Oct  5 11:37 ..2026_10_05_11_37_24.3420944231
lrwxrwxrwx    1 root     root            32 Oct  5 11:37 ..data -> ..2026_10_05_11_37_24.3420944231
lrwxrwxrwx    1 root     root            13 Oct  5 11:37 ca.crt -> ..data/ca.crt
lrwxrwxrwx    1 root     root            16 Oct  5 11:37 namespace -> ..data/namespace
lrwxrwxrwx    1 root     root            12 Oct  5 11:37 token -> ..data/token
```

ทุก Pod มีโฟลเดอร์นี้ (projected volume ที่ระบบเติมให้) ประกอบด้วย `ca.crt` ของคลัสเตอร์, ชื่อ `namespace` และ `token` อายุสั้นที่ kubelet ต่ออายุให้เอง แอปใช้ไฟล์เหล่านี้คุยกับ API server

### ขั้นที่ 3: token ถาวรแบบเก่า

```bash
kubectl apply -f builder-token.yaml; sleep 3; kubectl get secret builder-token
kubectl describe secret builder-token
kubectl get sa builder -o yaml
```

```text
serviceaccount/builder created
secret/builder-token created
NAME            TYPE                                  DATA   AGE
builder-token   kubernetes.io/service-account-token   3      3s
Name:         builder-token
Namespace:    default
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: builder
              kubernetes.io/service-account.uid: b3f1b5c9-628c-4420-9e3a-a1a24f1a794e

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1107 bytes
namespace:  7 bytes
token:      eyJhbGciOi...
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"name":"builder","namespace":"default"}}
  creationTimestamp: "2026-10-05T11:37:26Z"
  name: builder
  namespace: default
  resourceVersion: "1524"
  uid: b3f1b5c9-628c-4420-9e3a-a1a24f1a794e
```

- ไฟล์ YAML ของ Secret มีแค่ annotation `kubernetes.io/service-account.name: builder` ระบบเติม 3 key (`ca.crt`, `namespace`, `token`) และ annotation `uid` ให้เอง
- ⚠️ **`describe` แสดง token เต็มทั้งเส้น** (เอกสารนี้ตัดเหลือ `eyJhbGciOi...`) ต่างจาก Secret ชนิดอื่นที่แสดงแค่จำนวนไบต์ **ห้ามแปะ token จริงลงรายงาน** ในภาพหน้าจอให้บังบรรทัด `token:`
- `get sa builder -o yaml` **ไม่มีฟิลด์ `secrets:`** ระบบไม่สร้าง token ถาวรให้ ServiceAccount อัตโนมัติแล้ว token แบบนี้มีเฉพาะเมื่อเราสร้าง Secret เอง และไม่มีวันหมดอายุจนกว่าจะลบ

### ขั้นที่ 4: token ที่มีอายุ

```bash
kubectl create token builder --duration=10m | cut -c1-10; echo ...
kubectl create token builder --duration=10m | cut -d. -f2 | base64 -d 2>/dev/null | head -c 400; echo
kubectl get secret
```

```text
eyJhbGciOi
...
{"aud":["https://kubernetes.default.svc.cluster.local"],"exp":1791200849,"iat":1791200249,"iss":"https://kubernetes.default.svc.cluster.local","jti":"016bfa55-e5c5-450e-bc07-1ba3ed989451","kubernetes.io":{"namespace":"default","serviceaccount":{"name":"builder","uid":"b3f1b5c9-628c-4420-9e3a-a1a24f1a794e"}},"nbf":1791200249,"sub":"system:serviceaccount:default:builder"}
NAME            TYPE                                  DATA   AGE
ba              kubernetes.io/basic-auth              2      5m22s
builder-token   kubernetes.io/service-account-token   3      4s
demo            Opaque                                2      5m32s
fromfile        Opaque                                1      5m25s
fromfile-nl     Opaque                                1      5m24s
frozen          Opaque                                1      2m27s
onlypw          kubernetes.io/basic-auth              1      5m22s
regcred         kubernetes.io/dockerconfigjson        1      5m21s
sd              Opaque                                2      5m24s
shop-tls        kubernetes.io/tls                     2      2m21s
viapipe         Opaque                                1      5m23s
viass           Opaque                                1      5m23s
```

token เป็น JWT สามท่อนคั่นด้วยจุด ท่อนกลางถอดด้วย base64 ได้ข้อมูลว่าเป็นของ `system:serviceaccount:default:builder` และหมดอายุใน `exp − iat = 600` วินาที (10 นาที) token แบบนี้ **ไม่ถูกเก็บเป็น Secret** (รายการ Secret ไม่มีอะไรเพิ่ม) จึงไม่ค้างใน etcd และหมดอายุเอง (คำสั่งแรกตัดแสดงแค่ 10 ตัวอักษรแรกโดยตั้งใจ) ถ้า `base64 -d` พิมพ์ท้าย JSON ไม่ครบ เป็นเพราะ JWT ตัด `=` ท้ายออก ไม่มีผลกับการอ่าน

### สิ่งที่เห็น

- projected รวม `announcement.txt` + `db/password` + `pod-name` ใน `/etc/som` โหมด `-r--r-----` บน tmpfs ค่า `proj` / `newpass-01` / `วันนี้ปลาทูสดมาก 🐟`
- `builder-token kubernetes.io/service-account-token 3`, describe แสดง token เต็ม, `get sa builder -o yaml` ไม่มี `secrets:`
- `kubectl create token builder --duration=10m` ได้ JWT `sub: system:serviceaccount:default:builder` อายุ 600 วินาที

**คำถามชวนคิด**

1. ถ้าต้องให้ระบบ CI ภายนอกเรียก API ของคลัสเตอร์ ควรใช้ `builder-token` หรือ `kubectl create token` เพราะอะไร
2. ทำไมการที่ทั้งโฟลเดอร์ `/etc/som` เป็น tmpfs จึงสมเหตุสมผล ทั้งที่ `announcement.txt` มาจาก ConfigMap ซึ่งไม่ลับ

---

## LAB 7: RBAC: ใครเปิดซองได้ และการอ่านทางอ้อม

<p align="center" id="fig-10">
  <img src="images/10-lab7-rbac-intern.png" alt="รูปที่ 10 LAB 7 intern อ่านซองไม่ได้" width="900"><br>
  <em><b>รูปที่ 10</b> LAB7: intern (Role get/list/watch pods, pods/log, configmaps) → can-i get secrets = no, get secret demo → Forbidden; ยังดู Pod -o yaml เห็นแค่ชื่อ secretKeyRef ไม่เห็นค่า</em>
</p>

**เป้าหมาย:** ให้ ServiceAccount `intern` ดู Pod/log/ConfigMap ได้แต่แตะ Secret ไม่ได้ เห็นว่า intern เห็นแค่ชื่อซองใน YAML ของ Pod แล้วพิสูจน์ว่า ServiceAccount `maker` ที่ไม่มีสิทธิ์ `get secrets` แต่ **สร้าง Pod ได้** อ่านรหัสทางอ้อมได้

**ไฟล์:** `labs/lab07-rbac/intern.yaml`, `maker.yaml`, `peek.yaml` (ต้องมี Secret `demo` และ Pod `spod`)

### ขั้นที่ 1: บัตรแถบเทาของ intern

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab07-rbac
kubectl apply -f intern.yaml
for r in pods configmaps secrets; do echo "get $r: $(kubectl auth can-i get $r --as=system:serviceaccount:default:intern)"; done; echo "list secrets: $(kubectl auth can-i list secrets --as=system:serviceaccount:default:intern)"
```

```text
serviceaccount/intern created
role.rbac.authorization.k8s.io/intern-view created
rolebinding.rbac.authorization.k8s.io/intern-view created
get pods: yes
get configmaps: yes
get secrets: no
list secrets: no
```

Role `intern-view` ให้ `get, list, watch` กับ `pods`, `pods/log`, `configmaps` เท่านั้น (`--as=system:serviceaccount:default:intern` = ให้ kubectl สวมรอยเป็น intern ตอนตรวจ ต่อจากบทที่ 4)

### ขั้นที่ 2: intern ลองเปิดซอง

```bash
kubectl get pods --as=system:serviceaccount:default:intern
kubectl get secret demo --as=system:serviceaccount:default:intern
kubectl get secrets --as=system:serviceaccount:default:intern
kubectl describe secret demo --as=system:serviceaccount:default:intern
```

```text
NAME      READY   STATUS    RESTARTS   AGE
ngx-tls   1/1     Running   0          2m20s
proj      1/1     Running   0          6s
spod      1/1     Running   0          2m28s
Error from server (Forbidden): secrets "demo" is forbidden: User "system:serviceaccount:default:intern" cannot get resource "secrets" in API group "" in the namespace "default"
Error from server (Forbidden): secrets is forbidden: User "system:serviceaccount:default:intern" cannot list resource "secrets" in API group "" in the namespace "default"
Error from server (Forbidden): secrets "demo" is forbidden: User "system:serviceaccount:default:intern" cannot get resource "secrets" in API group "" in the namespace "default"
```

ดู Pod ได้ แต่ `get`, `list` และ `describe` Secret ถูกปฏิเสธทั้งหมด (describe ใช้สิทธิ์ `get` เหมือนกัน)

### ขั้นที่ 3: intern เห็นอะไรใน YAML ของ Pod

```bash
kubectl get pod spod -o yaml --as=system:serviceaccount:default:intern | grep -B2 -A3 secretKeyRef
kubectl exec spod --as=system:serviceaccount:default:intern -- printenv DB_PASSWORD
```

```text
...
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          key: password
          name: demo
    envFrom:
error: unable to upgrade connection: pods "spod" is forbidden: User "system:serviceaccount:default:intern" cannot create resource "pods/exec" in API group "" in the namespace "default"
```

intern เห็นแค่ **ชื่อซอง (`demo`) และชื่อ key (`password`)** ไม่เห็นค่า (annotation `last-applied-configuration` ของ Pod ก็มีแค่ `secretKeyRef` เช่นกัน) และ `exec` เข้า Pod เพื่ออ่าน env ไม่ได้เพราะไม่มีสิทธิ์ `pods/exec` ดูสิทธิ์ทั้งหมดของ intern

```bash
kubectl auth can-i --list --as=system:serviceaccount:default:intern
```

```text
Resources                                       Non-Resource URLs                      Resource Names   Verbs
selfsubjectreviews.authentication.k8s.io        []                                     []               [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []               [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []               [create]
configmaps                                      []                                     []               [get list watch]
pods/log                                        []                                     []               [get list watch]
pods                                            []                                     []               [get list watch]
clustertrustbundles.certificates.k8s.io         []                                     []               [get list watch]
                                                [/.well-known/openid-configuration/]   []               [get]
...
```

ไม่มีแถว `secrets` เลย (แถว `selfsubject…`, `clustertrustbundles` และ URL อย่าง `/healthz` เป็นสิทธิ์พื้นฐานที่ทุกคนได้)

<p align="center" id="fig-11">
  <img src="images/11-lab7-pod-maker.png" alt="รูปที่ 11 LAB 7 maker อ่านทางอ้อม" width="900"><br>
  <em><b>รูปที่ 11</b> LAB7 (ต่อ): maker ไม่มีสิทธิ์ get secrets แต่ create pods ได้ → kubectl run peek ที่ใช้ secretKeyRef แล้ว logs ได้ stolen=<รหัส> — สิทธิ์สร้าง Pod ต้องให้อย่างระวัง</em>
</p>

### ขั้นที่ 4: maker ไม่มีสิทธิ์อ่านซอง แต่สร้าง Pod ได้

```bash
kubectl apply -f maker.yaml
kubectl auth can-i get secrets --as=system:serviceaccount:default:maker; kubectl auth can-i create pods --as=system:serviceaccount:default:maker
kubectl get secret demo --as=system:serviceaccount:default:maker
```

```text
serviceaccount/maker created
role.rbac.authorization.k8s.io/pod-maker created
rolebinding.rbac.authorization.k8s.io/pod-maker created
no
yes
Error from server (Forbidden): secrets "demo" is forbidden: User "system:serviceaccount:default:maker" cannot get resource "secrets" in API group "" in the namespace "default"
```

### ขั้นที่ 5: แอบอ่านผ่าน Pod

`peek.yaml` เป็น Pod ที่ขอ Secret `demo` key `password` มาเป็น env `P` แล้วพิมพ์ `stolen=$P` ลง log

```bash
kubectl apply -f peek.yaml --as=system:serviceaccount:default:maker; sleep 12; kubectl get pod peek --as=system:serviceaccount:default:maker
kubectl logs peek --as=system:serviceaccount:default:maker
kubectl delete pod peek --as=system:serviceaccount:default:maker
```

```text
pod/peek created
NAME   READY   STATUS      RESTARTS   AGE
peek   0/1     Completed   0          12s
stolen=newpass-01
pod "peek" deleted from default namespace
```

maker ได้รหัสปัจจุบัน `newpass-01` ทั้งที่ `get secrets` = `no` เพราะ **kubelet เป็นคนเปิดซองให้ Pod** โดยไม่ตรวจว่าคนสร้าง Pod มีสิทธิ์อ่าน Secret หรือไม่ สิทธิ์ `create pods` (รวมถึง Deployment/Job ที่สร้าง Pod) ใน namespace ที่มีความลับจึงต้องให้อย่างระวังเท่ากับสิทธิ์อ่าน Secret

### สิ่งที่เห็น

- intern: get pods/configmaps = `yes`, get/list secrets = `no`; get/list/describe secret → `Forbidden`; YAML ของ Pod เห็นแค่ `secretKeyRef: key: password, name: demo`; exec → `cannot create resource "pods/exec"`
- maker: get secrets = `no`, create pods = `yes` → `stolen=newpass-01`

**คำถามชวนคิด**

1. intern มีสิทธิ์ `pods/log` ถ้าแอปในร้านพิมพ์ `DATABASE_URL` ลง log ตอนเริ่ม intern จะเห็นอะไร และควรแก้ที่ใคร
2. ถ้าให้ maker มีสิทธิ์ `create pods` แต่ต้องการกันไม่ให้อ่าน Secret ได้ ควรแยก namespace อย่างไร

---

## LAB 8: ส่อง etcd: รหัสถูกเก็บอย่างไร

<p align="center" id="fig-12">
  <img src="images/12-lab8-etcd-peek.png" alt="รูปที่ 12 LAB 8 ส่อง etcd" width="900"><br>
  <em><b>รูปที่ 12</b> LAB8: kubectl -n kube-system exec etcd-lab-control-plane -- etcdctl ... get /registry/secrets/default/demo | grep -a → เห็นรหัสเป็นข้อความ (ไม่มี encryption at rest); EncryptionConfiguration เป็นทฤษฎี</em>
</p>

**เป้าหมาย:** อ่านข้อมูลดิบของ Secret ใน etcd (อ่านอย่างเดียว) เห็นว่า kind ไม่ได้เปิด encryption at rest รหัสจึงอยู่ในฐานข้อมูลของคลัสเตอร์เป็นข้อความ แล้วเก็บกวาด LAB 1–8

**ไฟล์:** `labs/lab08-etcd/etcdget.sh` (เรียก `etcdctl ... get` ใน Pod `etcd-lab-control-plane` ด้วยใบรับรองของ etcd)

> ⚠️ ใช้เฉพาะคำสั่ง **อ่าน** (`get`) เท่านั้น ห้ามใช้ `etcdctl put`/`del` กับคลัสเตอร์ เพราะเป็นการแก้ฐานข้อมูลของคลัสเตอร์โดยตรงข้าม API server

### ขั้นที่ 1: ตู้เอกสาร etcd และรายชื่อซอง

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/011_kubernetes_secret/02_LAB/labs/lab08-etcd
kubectl -n kube-system get pod -l component=etcd
./etcdget.sh --keys /registry/secrets/default/
```

```text
NAME                     READY   STATUS    RESTARTS   AGE
etcd-lab-control-plane   1/1     Running   0          7m44s
/registry/secrets/default/ba

/registry/secrets/default/builder-token

/registry/secrets/default/demo
...
/registry/secrets/default/viass

```

Secret ทุกตัวอยู่ใต้ key `/registry/secrets/<namespace>/<ชื่อ>` (ผลจริงมี 12 key ตรงกับ `kubectl get secret` ท้าย LAB 6)

### ขั้นที่ 2: อ่านซอง demo จาก etcd

```bash
./etcdget.sh /registry/secrets/default/demo | grep -a -o 'newpass-01'
./etcdget.sh /registry/secrets/default/demo | head -c 400 | cat -v; echo
```

```text
newpass-01
/registry/secrets/default/demo
k8s^@
^L
^Bv1^R^FSecret^RM-7^B
...
^Hpassword^R
newpass-01^R^O
^Husername^R^Csom^Z^FOpaque^Z^@"^@
```

ข้อมูลเป็น protobuf (อักขระไบนารีแสดงเป็น `^X`/`M-` ด้วย `cat -v`) แต่รหัส `newpass-01` อยู่ในนั้น **เป็นข้อความตรง ๆ ไม่ใช่แม้แต่ base64** k8s-lab ไม่มี `strings`/`xxd` จึงใช้ `grep -a` (มองไฟล์ไบนารีเป็นข้อความ) และ `cat -v` แทน

### ขั้นที่ 3: ConfigMap ก็เหมือนกัน และไม่มี encryption

```bash
./etcdget.sh /registry/configmaps/default/shop-board | grep -a -o 'วันนี้ปลาทูสดมาก'
docker exec lab-control-plane grep -n encryption /etc/kubernetes/manifests/kube-apiserver.yaml; echo "rc=$?"
docker exec lab-control-plane grep -n -E "etcd-servers|secure-port" /etc/kubernetes/manifests/kube-apiserver.yaml
```

```text
วันนี้ปลาทูสดมาก
วันนี้ปลาทูสดมาก
rc=1
24:    - --etcd-servers=https://127.0.0.1:2379
35:    - --secure-port=6443
```

ConfigMap `shop-board` เจอข้อความ 2 ครั้ง (ใน `data` และใน annotation last-applied) ส่วน `grep encryption` ใน manifest ของ kube-apiserver ไม่เจออะไรเลย (`rc=1`) แปลว่าไม่มี `--encryption-provider-config` ขณะที่ flag อื่น เช่น `--etcd-servers` มีอยู่จริง ใครที่เข้าถึง etcd, ดิสก์ของ control plane หรือไฟล์ backup ของ etcd ได้ จะอ่าน Secret ทุกตัวได้โดยไม่ผ่าน RBAC การเปิด EncryptionConfiguration เป็นเนื้อหาทฤษฎี (หัวข้อ 9.2) ไม่ทำใน LAB เพราะต้องแก้ kube-apiserver

### ขั้นที่ 4: เก็บกวาด LAB 1–8

กลับไปโฟลเดอร์ `02_LAB` แล้วลบของที่สร้างใน LAB 1–8 (ใน namespace `default`) ทั้งหมด (คืน NodePort 30081 ด้วย)

```bash
cd /workspace/011_kubernetes_secret/02_LAB
kubectl delete pod spod proj ngx-tls --wait=true; kubectl delete svc ngx-tls; kubectl delete cm ngx-tls-conf shop-board; kubectl delete secret demo demo2 sd fromfile fromfile-nl viapipe viass onlypw ba regcred shop-tls frozen builder-token --ignore-not-found; kubectl delete -f labs/lab07-rbac/intern.yaml -f labs/lab07-rbac/maker.yaml -f labs/lab06-projected/builder-token.yaml --ignore-not-found; kubectl get all,secret,cm,sa,role,rolebinding
rm -f labs/lab02-types/pw-nl.txt
```

```text
pod "spod" deleted from default namespace
pod "proj" deleted from default namespace
pod "ngx-tls" deleted from default namespace
service "ngx-tls" deleted from default namespace
configmap "ngx-tls-conf" deleted from default namespace
configmap "shop-board" deleted from default namespace
secret "demo" deleted from default namespace
...
secret "builder-token" deleted from default namespace
serviceaccount "intern" deleted from default namespace
role.rbac.authorization.k8s.io "intern-view" deleted from default namespace
rolebinding.rbac.authorization.k8s.io "intern-view" deleted from default namespace
serviceaccount "maker" deleted from default namespace
role.rbac.authorization.k8s.io "pod-maker" deleted from default namespace
rolebinding.rbac.authorization.k8s.io "pod-maker" deleted from default namespace
serviceaccount "builder" deleted from default namespace
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   7m52s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      7m45s

NAME                     AGE
serviceaccount/default   7m45s
```

`demo2` ไม่เคยถูกสร้างจริง (LAB 1 เป็นแค่ dry-run) `--ignore-not-found` จึงข้ามไปเงียบ ๆ namespace `default` เหลือแค่ของที่ระบบสร้าง **อย่าลบ** `labs/lab04-tls/tls.crt` และ `tls.key` (ใช้ใน LAB 9)

### สิ่งที่เห็น

- `./etcdget.sh --keys /registry/secrets/default/` แสดง 12 key, `grep -a -o newpass-01` เจอ, `cat -v` เห็น `password^R` ตามด้วย `newpass-01` ในข้อมูล protobuf
- ConfigMap ก็เก็บเป็นข้อความ (`วันนี้ปลาทูสดมาก`), `grep encryption` ใน kube-apiserver.yaml → `rc=1`

**คำถามชวนคิด**

1. intern ใน LAB 7 อ่าน Secret ผ่าน API ไม่ได้ ถ้า intern ได้ไฟล์ backup ของ etcd ไป จะอ่าน `newpass-01` ได้หรือไม่ และ encryption at rest ช่วยตรงนี้อย่างไร
2. ทำไมใน etcd ค่ารหัสจึงไม่เป็น base64 เหมือนที่เห็นใน `kubectl get secret -o yaml`

---

## LAB 9: LAB สุดท้าย: ร้านน้องส้มซ่อนรหัสผ่าน

**เป้าหมาย:** รับร้านน้องส้มจากท้ายบทที่ 10 (`k8s-010/`) ที่รหัสฐานข้อมูล `meow1234` ยังเขียนอยู่ใน YAML ให้ intern ยืนยันว่าเห็นรหัส ย้ายรหัสไปไว้ใน Secret `som-db-secret` ทั้งฝั่ง db (StatefulSet) และ web (Deployment) จน intern อ่านไม่ได้ **เปลี่ยนรหัสจริงเป็น `purr5678`** โดยลองทำผิดลำดับให้เห็นผลก่อน เปิดทางเข้า HTTPS ด้วย Secret ชนิด TLS ที่ `https://localhost:30082` ส่อง etcd ว่ารหัสยังเป็นข้อความ และดูผลทั้งหมดใน browser **ใช้ image `som-shop-web:1.5` ตัวเดิม ไม่ build ใหม่ และออเดอร์ไม่หายตลอด LAB**

**ใช้ทุกอย่างที่เรียนมา:** Namespace + Pod Security `warn: restricted` (บทที่ 4), Deployment 3 บูธ + rolling update + `rollout restart`/`history` (บทที่ 5–7), Service NodePort 30080 (บทที่ 6), PVC (บทที่ 8), StatefulSet + headless Service `som-db-0.som-db` (บทที่ 9), ConfigMap ป้ายร้าน + ประกาศ (บทที่ 10), RBAC + ServiceAccount (บทที่ 4) และ Secret ทุกแบบที่ใช้ในงานจริงของบทนี้ (`Opaque` + `secretKeyRef`, `kubernetes.io/tls` + volume)

### 9.1 ภาพรวมและไฟล์

<p align="center" id="fig-13">
  <img src="images/13-lab9-architecture.png" alt="รูปที่ 13 LAB 9 ภาพรวม som-shop-v7" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9 ภาพรวม: Secret som-db-secret (POSTGRES_PASSWORD, DATABASE_URL) ให้ som-db-0 และ web ผ่าน secretKeyRef; ConfigMap ป้ายร้านจากบท 010; Secret som-tls ให้ nginx HTTPS NodePort 30082; intern อ่านได้แค่ Pod/ConfigMap/Deployment/StatefulSet อ่าน Secret ไม่ได้</em>
</p>

| ไฟล์ใน `som-shop-v7/` | บทบาท | ต่างจากบทที่ 10 อย่างไร |
|---|---|---|
| `k8s-010/00-namespace.yaml`, `10-db.yaml`, `15-config.yaml`, `20-web.yaml` | จุดเริ่ม = สภาพท้ายบท 010 | สำเนาไม่แก้ (รหัส `meow1234` ยังอยู่ใน `POSTGRES_PASSWORD` และ `DATABASE_URL` 2 ที่) |
| `k8s/00-namespace.yaml` | namespace `som-shop` + `pod-security.kubernetes.io/warn: restricted` | เหมือนเดิม |
| `k8s/10-db.yaml` | headless Service + StatefulSet `som-db` | `POSTGRES_PASSWORD` ← `secretKeyRef som-db-secret/POSTGRES_PASSWORD` |
| `k8s/15-config.yaml` | ConfigMap `som-web-config`, `som-announcement` | หัวเว็บ `⚓ ท่าเรือ Kubernetes · Secret` และ footer บอกว่ารหัสอยู่ใน Secret (ไม่มีรหัสบนกระดาน) |
| `k8s/20-web.yaml` | Deployment `som-web` 3 บูธ + Service NodePort 30080 | `DATABASE_URL` ของ `db-seed` และ `web` ← `secretKeyRef som-db-secret/DATABASE_URL`, change-cause `1.5 รหัส DB จาก Secret` |
| `k8s/30-https.yaml` | ConfigMap `som-https-conf` (nginx `listen 8443 ssl` → `proxy_pass http://som-web.som-shop.svc.cluster.local:80`) + Deployment `som-https` (nginx:1.27-alpine, mount Secret `som-tls` `defaultMode: 0400`) + Service NodePort **30082** → 443 | ใหม่ |
| `extra/30-https-restricted.yaml` | ทางเลือกของ `30-https.yaml` ที่ผ่าน Pod Security restricted (`nginxinc/nginx-unprivileged`, `fsGroup: 101`, `defaultMode: 0440`) | ใหม่ |
| `examples/05-secret.example.yaml` | ไฟล์ Secret ตัวอย่าง (stringData ค่าปลอม) | ใหม่ — ไม่ได้ใช้เป็นวิธีหลัก |
| `rbac/intern.yaml`, `rbac/intern-context.sh` | intern ดูได้อย่างเดียว + context ใน kubeconfig | สคริปต์ใหม่ (ใช้ `kubectl create token` อายุ 24h) |

Secret ที่ร้านใช้มี 2 ซอง

| Secret | type | key | ใครใช้ |
|---|---|---|---|
| `som-db-secret` | `Opaque` | `POSTGRES_PASSWORD`, `DATABASE_URL` | `som-db-0` (initdb), `db-seed` และ `web` ของ `som-web` |
| `som-tls` | `kubernetes.io/tls` | `tls.crt`, `tls.key` (จาก LAB 4) | nginx ของ `som-https` |

ส่วนที่เปลี่ยนใน `k8s/20-web.yaml` (เทียบกับ `k8s-010/20-web.yaml`) มีแค่นี้ ทั้งใน `db-seed` และ `web`

```yaml
- name: DATABASE_URL     # postgres://som:<รหัส>@som-db-0.som-db:5432/catshop — ทั้งก้อนอยู่ในซอง
  valueFrom:
    secretKeyRef:
      name: som-db-secret
      key: DATABASE_URL
```

ลำดับขั้น: **เริ่ม** (สั่ง 3 ออเดอร์) → **A** intern เห็นรหัส → **B** สร้างซอง → **C1** db ใช้ซอง → **C2** web ใช้ซอง → **D1** เปลี่ยนรหัสใน DB → **D2** ลองผิด: restart โดยไม่แก้ซอง → **D3** แก้ซองแล้ว restart → **D4** db เกิดใหม่ออเดอร์ยังอยู่ → **E** HTTPS → **F** ส่อง etcd → **เปิดร้านใน browser (ภาพหน้าจอจริง)**

### 9.2 เริ่มร้านจากสภาพท้ายบท 010 และขั้น A: intern ยังเห็นรหัส

<p align="center" id="fig-14">
  <img src="images/14-lab9-start-visible.png" alt="รูปที่ 14 LAB 9 ขั้น A intern เห็นรหัส" width="900"><br>
  <em><b>รูปที่ 14</b> ขั้น A: เริ่มจากสภาพท้ายบท 010 (k8s-010/) แล้วสั่ง 3 ออเดอร์ → orders=3; intern ใช้ get deploy/sts -o yaml ยังเห็น meow1234</em>
</p>

🐧 **ใน SSH session ของ k8s-lab** ตรวจว่าไม่มีร้านค้าง แล้วเปิดร้านจาก `k8s-010/`

```bash
cd /workspace/011_kubernetes_secret/02_LAB/som-shop-v7
kubectl get ns som-shop 2>&1; kubectl get pv
kubectl apply -f k8s-010/
time (kubectl -n som-shop rollout status sts/som-db --timeout=180s && kubectl -n som-shop rollout status deploy/som-web --timeout=240s)
```

```text
Error from server (NotFound): namespaces "som-shop" not found
No resources found
namespace/som-shop created
service/som-db created
statefulset.apps/som-db created
configmap/som-web-config created
configmap/som-announcement created
deployment.apps/som-web created
service/som-web created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...
Waiting for deployment "som-web" rollout to finish: 0 of 3 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m14.107s
```

ถ้า `kubectl get ns som-shop` ยังเจอร้านของบทที่ 10 ให้ `kubectl delete ns som-shop` ก่อน (LAB 0 ขั้นที่ 4)

**สั่ง 3 ออเดอร์ก่อน** ร้านที่เพิ่งเปิดบนฐานข้อมูลใหม่มี `orders=0` สั่งด้วย curl (หรือ 🌐 เปิด `http://localhost:30080` แล้วกด "สั่งซื้อ" 3 ครั้ง) เพื่อให้ตัวเลขตรงกับเอกสาร

```bash
sleep 8; curl -s localhost:30080/api/stats; for p in 1 2 3; do curl -s -XPOST -H "content-type: application/json" -d "{\"product_id\":$p,\"qty\":1}" localhost:30080/api/orders; echo; done; curl -s localhost:30080/api/stats
curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement
kubectl -n som-shop rollout history deploy/som-web
```

```text
som-web-8655557674-t4l7l 1.5 orders=0 products=6
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":14}}
{"ok":true,"order_id":3,"product":{"id":3,"name_th":"อาหารเม็ดแมวสูงวัย 1.2 กก.","stock":9}}
som-web-8655557674-t4l7l 1.5 orders=3 products=6
{"pod":"som-web-8655557674-t4l7l","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-8655557674-t4l7l 1.5 วันนี้ปลาทูสดมาก 🐟
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 ป้ายร้านจาก ConfigMap
```

ร้านเป็นสภาพท้ายบท 010 ทุกอย่าง (หัวเว็บ `· ConfigMap`, footer `LAB 010`, ประกาศ `วันนี้ปลาทูสดมาก 🐟`) และมี `orders=3`

**ขั้น A: ให้ intern ลองอ่านร้าน** สร้าง ServiceAccount `intern` (ดูได้อย่างเดียว) และ context `intern` ใน kubeconfig ด้วยสคริปต์ที่ขอ token อายุ 24 ชั่วโมงจาก `kubectl create token` (ไม่ใช้ Secret แบบ service-account-token ที่ไม่มีวันหมดอายุ)

```bash
kubectl apply -f rbac/intern.yaml
./rbac/intern-context.sh
kubectl config get-contexts; kubectl --context intern get pods
```

```text
serviceaccount/intern created
role.rbac.authorization.k8s.io/intern-read created
rolebinding.rbac.authorization.k8s.io/intern-read created
Context "intern" created.
ใช้: kubectl --context intern get pods   (token อายุ 24h — ห้ามแชร์ token)
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
          intern     kind-lab   intern     som-shop
*         kind-lab   kind-lab   kind-lab   
NAME                       READY   STATUS    RESTARTS   AGE
som-db-0                   1/1     Running   0          24s
som-web-8655557674-8rrdf   1/1     Running   0          24s
som-web-8655557674-qh776   1/1     Running   0          24s
som-web-8655557674-t4l7l   1/1     Running   0          24s
```

`kubectl --context intern ...` = สั่งในฐานะ intern จริง ๆ (ใช้ token ของ intern และ namespace `som-shop` เป็นค่าเริ่ม) ส่วน context ปัจจุบัน (`*`) ยังเป็น `kind-lab` ของเรา

```bash
kubectl --context intern get deploy som-web -o yaml | grep -o 'som:[a-z0-9]*@'
kubectl --context intern get sts som-db -o yaml | grep -A1 POSTGRES_PASSWORD
kubectl --context intern get pod som-db-0 -o yaml | grep -A1 POSTGRES_PASSWORD
kubectl --context intern get secrets
```

```text
som:meow1234@
som:meow1234@
som:meow1234@
som:meow1234@
      {"apiVersion":"apps/v1","kind":"StatefulSet",...{"name":"POSTGRES_PASSWORD","value":"meow1234"},...
--
        - name: POSTGRES_PASSWORD
          value: meow1234
    - name: POSTGRES_PASSWORD
      value: meow1234
Error from server (Forbidden): secrets is forbidden: User "system:serviceaccount:som-shop:intern" cannot list resource "secrets" in API group "" in the namespace "som-shop"
```

intern ไม่มีสิทธิ์กับ Secret เลย แต่ **เห็นรหัส 4 ที่ใน Deployment** (`db-seed` + `web` ใน spec และอีก 2 ที่ใน annotation `last-applied-configuration`) และเห็น `POSTGRES_PASSWORD` ทั้งใน StatefulSet (spec + annotation) และ Pod นี่คือโจทย์ของ LAB นี้

### 9.3 ขั้น B: สร้างซอง som-db-secret

<p align="center" id="fig-15">
  <img src="images/15-lab9-create-secret.png" alt="รูปที่ 15 LAB 9 ขั้น B สร้างซอง" width="900"><br>
  <em><b>รูปที่ 15</b> ขั้น B: kubectl create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=... --from-literal=DATABASE_URL=... (หรือไฟล์ 05-secret.example.yaml ที่ไม่ commit ค่าจริง)</em>
</p>

วิธีหลักคือ `kubectl create secret generic --from-literal` (ไม่ทิ้ง annotation last-applied และไม่ต้องมีไฟล์ที่มีรหัส)

```bash
kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop
kubectl -n som-shop get secret; kubectl -n som-shop describe secret som-db-secret
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.metadata.annotations}'; echo '(ไม่มี last-applied)'
```

```text
secret/som-db-secret created
NAME            TYPE     DATA   AGE
som-db-secret   Opaque   2      0s
Name:         som-db-secret
Namespace:    som-shop
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
DATABASE_URL:       52 bytes
POSTGRES_PASSWORD:  8 bytes
(ไม่มี last-applied)
```

รหัสในซองยังเป็น `meow1234` เท่าเดิมโดยตั้งใจ ขั้นนี้แค่ "ย้ายที่เก็บ" ยังไม่เปลี่ยนรหัส (จะเปลี่ยนในขั้น D)

**ทางเลือก: ไฟล์ตัวอย่าง** ดูไฟล์ตัวอย่างและ `.gitignore` ของร้าน

```bash
grep -v '^#' examples/05-secret.example.yaml; cat .gitignore
kubectl apply --dry-run=server -f examples/05-secret.example.yaml
```

```text
apiVersion: v1
kind: Secret
metadata:
  name: som-db-secret
  namespace: som-shop
type: Opaque
stringData:
  POSTGRES_PASSWORD: meow1234
  DATABASE_URL: postgres://som:meow1234@som-db-0.som-db:5432/catshop
# ไฟล์ Secret ที่มีค่าจริง ห้ามเข้า git (ไฟล์ตัวอย่าง *.example.yaml commit ได้)
secret.yaml
*.secret.yaml
*.key
*.crt
Warning: resource secrets/som-db-secret is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
secret/som-db-secret configured (server dry run)
```

`--dry-run=server` ให้ API server ตรวจไฟล์โดยไม่บันทึกจริง ถ้าจะใช้ไฟล์จริง ให้คัดลอกเป็นชื่อที่ `.gitignore` กันไว้ (เช่น `som-db.secret.yaml`) แล้วแก้ค่า แต่จำไว้ว่า `kubectl apply` + `stringData` จะเก็บรหัสเป็นข้อความใน annotation (LAB 2) Warning `missing the ... last-applied-configuration annotation` ขึ้นเพราะ Secret ถูกสร้างด้วย `create` เป็นเรื่องปกติ

### 9.4 ขั้น C1: db ใช้รหัสจากซอง

<p align="center" id="fig-16">
  <img src="images/16-lab9-db-secret-ref.png" alt="รูปที่ 16 LAB 9 ขั้น C1 db ใช้ซอง" width="900"><br>
  <em><b>รูปที่ 16</b> ขั้น C1: apply k8s/10-db.yaml (POSTGRES_PASSWORD จาก secretKeyRef) → som-db-0 rolling update ~2 วินาที PVC เดิม ออเดอร์ยัง 3</em>
</p>

```bash
kubectl -n som-shop get pvc; kubectl -n som-shop get pod som-db-0 -o jsonpath='{.metadata.uid}'; echo
kubectl apply -f k8s/10-db.yaml && time kubectl -n som-shop rollout status sts/som-db --timeout=180s
kubectl -n som-shop get pod som-db-0; kubectl -n som-shop get pvc; sleep 5; curl -s localhost:30080/api/stats
kubectl --context intern get sts som-db -o yaml | grep -A4 'name: POSTGRES_PASSWORD'
```

```text
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
data-som-db-0   Bound    pvc-5a9c2812-baf2-42ec-b11f-e3ddbb385214   1Gi        RWO            standard       <unset>                 26s
7ec5121b-b471-41ba-b86f-884d8c97264c
service/som-db unchanged
statefulset.apps/som-db configured
Waiting for partitioned roll out to finish: 0 out of 1 new pods have been updated...
Waiting for 1 pods to be ready...
...
partitioned roll out complete: 1 new pods have been updated...

real	0m1.697s
NAME       READY   STATUS    RESTARTS   AGE
som-db-0   1/1     Running   0          1s
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
data-som-db-0   Bound    pvc-5a9c2812-baf2-42ec-b11f-e3ddbb385214   1Gi        RWO            standard       <unset>                 28s
som-web-8655557674-qh776 1.5 orders=3 products=6
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              key: POSTGRES_PASSWORD
              name: som-db-secret
```

StatefulSet เปลี่ยน template จึงสร้าง `som-db-0` ใหม่ (AGE `1s`, rollout ราว 2 วินาที) แต่ยังผูก PVC `data-som-db-0` ตัวเดิม (VOLUME เดิม) ออเดอร์จึงยังเป็น 3 และ `POSTGRES_PASSWORD` ไม่ได้ใช้เลยในรอบนี้ เพราะฐานข้อมูลมีอยู่แล้ว (ใช้แค่ตอน initdb) intern เห็นแค่ `secretKeyRef` ไม่เห็นค่า

### 9.5 ขั้น C2: web ใช้รหัสจากซอง

<p align="center" id="fig-17">
  <img src="images/17-lab9-web-secret-ref.png" alt="รูปที่ 17 LAB 9 ขั้น C2 web ใช้ซอง" width="900"><br>
  <em><b>รูปที่ 17</b> ขั้น C2: apply k8s/20-web.yaml (web และ db-seed ใช้ DATABASE_URL จาก Secret) → orders=3; intern grep meow1234 ใน Deployment ได้ 0 บรรทัด, get secret → Forbidden, exec → Forbidden</em>
</p>

```bash
kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml && time kubectl -n som-shop rollout status deploy/som-web --timeout=240s
sleep 8; curl -s localhost:30080/api/stats; ./hit.sh http://localhost:30080/api/stats 12 0.1
curl -s localhost:30080/api/shop; echo
kubectl -n som-shop rollout history deploy/som-web
```

```text
configmap/som-web-config configured
configmap/som-announcement unchanged
deployment.apps/som-web configured
service/som-web unchanged
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
deployment "som-web" successfully rolled out

real	0m17.591s
som-web-7948ccf586-hxqdd 1.5 orders=3 products=6
จำนวน  Pod  เวอร์ชัน
      3 som-web-7948ccf586-hxqdd 1.5 orders=3 products=6
      6 som-web-7948ccf586-v8t4l 1.5 orders=3 products=6
      3 som-web-7948ccf586-xnpsd 1.5 orders=3 products=6
ok=12 err=0 (ใช้เวลา 1.3 วินาที)
{"pod":"som-web-7948ccf586-hxqdd","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · Secret","footer":"Next.js + PostgreSQL · Kubernetes LAB 011 · รหัส DB อยู่ใน Secret som-db-secret"}
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 ป้ายร้านจาก ConfigMap
2         1.5 รหัส DB จาก Secret
```

rolling update 3 บูธ (ราว 18 วินาที) ทุก Pod ต่อฐานข้อมูลด้วยรหัสจากซองได้ ออเดอร์ยัง 3 ป้ายร้านเปลี่ยนเป็น `· Secret` / `LAB 011` เพราะ apply `15-config.yaml` ชุดใหม่พร้อมกัน (env จาก ConfigMap อ่านตอน Pod ใหม่เริ่ม) ทีนี้ให้ intern ลองอีกครั้ง

```bash
kubectl --context intern get deploy som-web -o yaml | grep -c meow1234
kubectl --context intern get deploy som-web -o yaml | grep -A3 secretKeyRef
kubectl --context intern get secret som-db-secret
kubectl --context intern describe secret som-db-secret
kubectl --context intern auth can-i get secrets; kubectl --context intern auth can-i create pods/exec; kubectl --context intern auth can-i get pods/log
kubectl --context intern exec deploy/som-web -c web -- printenv DATABASE_URL
kubectl --context intern logs deploy/som-web -c db-seed | tail -3
```

```text
0
            secretKeyRef:
              key: DATABASE_URL
              name: som-db-secret
...
Error from server (Forbidden): secrets "som-db-secret" is forbidden: User "system:serviceaccount:som-shop:intern" cannot get resource "secrets" in API group "" in the namespace "som-shop"
Error from server (Forbidden): secrets "som-db-secret" is forbidden: User "system:serviceaccount:som-shop:intern" cannot get resource "secrets" in API group "" in the namespace "som-shop"
no
no
yes
error: unable to upgrade connection: pods "som-web-7948ccf586-xnpsd" is forbidden: User "system:serviceaccount:som-shop:intern" cannot create resource "pods/exec" in API group "" in the namespace "som-shop"
Found 3 pods, using pod/som-web-7948ccf586-xnpsd
got seed lock 5005
tables ready: products, orders
seeded 6 products (new: 0)
```

| intern ลองทำ | ผลก่อนย้าย (ขั้น A) | ผลหลังย้าย (ขั้น C2) |
|---|---|---|
| `grep` รหัสใน Deployment | `som:meow1234@` 4 บรรทัด | `0` เห็นแค่ `secretKeyRef {key: DATABASE_URL, name: som-db-secret}` |
| `get`/`describe secret` | – | `Forbidden` |
| `exec` อ่าน env | – | `cannot create resource "pods/exec"` |
| อ่าน log | ได้ | ได้ (`pods/log` = yes) log ของ db-seed ไม่มีรหัส |

แม้ annotation `last-applied-configuration` ของ Deployment ก็ไม่มีรหัสแล้ว เพราะไฟล์ `k8s/20-web.yaml` ไม่มีรหัส (บรรทัด annotation ถูกตัดเป็น `...` ข้างบน) ถ้าเห็น `grep -c` พิมพ์ `0` แล้ว shell บอก exit code 1 เป็นเรื่องปกติของ `grep` ที่ไม่เจอ

### 9.6 ขั้น D1: เปลี่ยนรหัสในฐานข้อมูล

<p align="center" id="fig-18">
  <img src="images/18-lab9-alter-user.png" alt="รูปที่ 18 LAB 9 ขั้น D1 ALTER USER" width="900"><br>
  <em><b>รูปที่ 18</b> ขั้น D1: psql ALTER USER som PASSWORD 'purr5678' → Pod web เดิมยังตอบได้เฉพาะ connection ที่ค้างอยู่ใน pool พอต้องต่อใหม่ก็ auth ไม่ผ่าน หน้าเว็บขึ้น 503 "ร้านกำลังเตรียมสินค้า" เป็นช่วง ๆ (password authentication failed for user "som")</em>
</p>

ร้านจะเปลี่ยนรหัสจาก `meow1234` เป็น `purr5678` (ค่าตัวอย่าง) ขั้นแรกเปลี่ยนในฐานข้อมูล

```bash
kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -c "ALTER USER som PASSWORD 'purr5678';"
sleep 10; for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " localhost:30080/api/stats; done; echo; curl -s localhost:30080/api/stats
kubectl -n som-shop get pod -l app=som-web
```

```text
ALTER ROLE
200 200 200 200 200 200 
som-web-7948ccf586-v8t4l 1.5 orders=3 products=6
NAME                       READY   STATUS    RESTARTS   AGE
som-web-7948ccf586-hxqdd   1/1     Running   0          38s
som-web-7948ccf586-v8t4l   1/1     Running   0          32s
som-web-7948ccf586-xnpsd   1/1     Running   0          44s
```

> ⚠️ **อย่าหลงดีใจกับ `200` ชุดนี้** ทุก Pod ยังใช้รหัสเก่า `meow1234` จาก Secret ที่ได้ 200 เพราะ request เหล่านี้ใช้ **connection ที่เปิดค้างอยู่ใน pool** ตั้งแต่ก่อนเปลี่ยนรหัส (PostgreSQL ตรวจรหัสเฉพาะตอนเปิด connection ใหม่) เมื่อ connection เก่าถูกปิดและแอปต้องเปิดใหม่ การยืนยันตัวตนจะไม่ผ่าน หน้าเว็บได้ **503 "ร้านกำลังเตรียมสินค้า" เป็นช่วง ๆ** (ภาพหน้าจอจริงใน 9.13 ฉาก 4) ร้านจึง **ล่มเป็นช่วง ไม่ได้ขายได้ปกติ** สถานะนี้ต้องรีบแก้ซองให้ตรงกับรหัสใหม่ (ขั้น D3)

ทดสอบว่ารหัสไหนใช้ได้จริง **ต้องทดสอบผ่านเครือข่ายด้วย `-h som-db-0.som-db`** แบบเดียวกับที่ web เชื่อมต่อ

```bash
kubectl -n som-shop exec som-db-0 -- sh -c 'PGPASSWORD=meow1234 psql -h som-db-0.som-db -U som -d catshop -tAc "select 1"'
kubectl -n som-shop exec som-db-0 -- sh -c 'PGPASSWORD=purr5678 psql -h som-db-0.som-db -U som -d catshop -tAc "select 1"'
kubectl -n som-shop exec som-db-0 -- sh -c 'PGPASSWORD=wrong-anything psql -h 127.0.0.1 -U som -d catshop -tAc "select 1"'
kubectl -n som-shop exec som-db-0 -- grep -v -E '^#|^$' /var/lib/postgresql/data/pgdata/pg_hba.conf
```

```text
psql: error: connection to server at "som-db-0.som-db" (10.244.1.13), port 5432 failed: FATAL:  password authentication failed for user "som"
command terminated with exit code 2
1
1
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
host all all all scram-sha-256
```

รหัสเก่าถูกปฏิเสธ รหัสใหม่ได้ `1` แต่รหัสมั่ว ๆ ผ่าน `127.0.0.1` ก็ได้ `1` เพราะ `pg_hba.conf` ให้ `127.0.0.1/32 trust` (ไม่ตรวจรหัส) ส่วนการเชื่อมต่อจากเครือข่ายเข้ากฎ `host all all all scram-sha-256` **การทดสอบด้วย 127.0.0.1 จึงหลอกให้เข้าใจผิดได้**

### 9.7 ขั้น D2 (ลองผิด): restart โดยยังไม่แก้ซอง

<p align="center" id="fig-19">
  <img src="images/19-lab9-forgot-secret.png" alt="รูปที่ 19 LAB 9 ขั้น D2 ลืมแก้ซอง" width="900"><br>
  <em><b>รูปที่ 19</b> ขั้น D2 (ลองผิด): rollout restart โดยยังไม่แก้ Secret → Pod ใหม่ค้าง Init:Error (db-seed: auth_failed) และ maxUnavailable: 0 ทำให้ Pod เดิมไม่ถูกลบ แต่ Pod เดิมก็ล่มเป็นช่วง ๆ (503) เพราะต่อ DB ใหม่ไม่ได้ → ต้องแก้ Secret ให้ตรงกับรหัสใหม่</em>
</p>

สมมติว่าลืมแก้ Secret แล้วสั่งให้ Pod เกิดใหม่

```bash
kubectl -n som-shop rollout restart deploy/som-web
sleep 40; kubectl -n som-shop get pod -l app=som-web
```

```text
deployment.apps/som-web restarted
NAME                       READY   STATUS       RESTARTS      AGE
som-web-7948ccf586-hxqdd   1/1     Running      0             80s
som-web-7948ccf586-v8t4l   1/1     Running      0             74s
som-web-7948ccf586-xnpsd   1/1     Running      0             86s
som-web-7d598bc5cd-rvqjd   0/1     Init:Error   2 (37s ago)   40s
```

Pod ใหม่ค้าง `Init:Error` และ restart วนไปเรื่อย ๆ ดู log ของ init container `db-seed` (ผลจริงเต็ม)

```bash
P=$(kubectl -n som-shop get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print $1}' | head -1); echo "Pod ใหม่: $P"; kubectl -n som-shop logs $P -c db-seed
```

```text
Pod ใหม่: som-web-7d598bc5cd-rvqjd
/app/node_modules/pg-protocol/dist/parser.js:306
        : new messages_1.DatabaseError(messageValue, LATEINIT_LENGTH, name);
          ^

error: password authentication failed for user "som"
    at parseErrorMessage (/app/node_modules/pg-protocol/dist/parser.js:306:11)
    at Parser.handlePacket (/app/node_modules/pg-protocol/dist/parser.js:143:27)
    at Parser.parse (/app/node_modules/pg-protocol/dist/parser.js:37:38)
    at Socket.<anonymous> (/app/node_modules/pg-protocol/dist/index.js:12:42)
    at Socket.emit (node:events:519:28)
    at addChunk (node:internal/streams/readable:561:12)
    at readableAddChunkPushByteMode (node:internal/streams/readable:512:3)
    at Readable.push (node:internal/streams/readable:392:5)
    at TCP.onStreamRead (node:internal/stream_base_commons:189:23) {
  length: 99,
  severity: 'FATAL',
  code: '28P01',
  detail: undefined,
  hint: undefined,
  position: undefined,
  internalPosition: undefined,
  internalQuery: undefined,
  where: undefined,
  schema: undefined,
  table: undefined,
  column: undefined,
  dataType: undefined,
  constraint: undefined,
  file: 'auth.c',
  line: '329',
  routine: 'auth_failed'
}

Node.js v22.23.3
```

อ่าน log จากบนลงล่าง: บรรทัด `parser.js:306` คือจุดที่ driver โยน error, **บรรทัดสำคัญคือ `error: password authentication failed for user "som"`** ตามด้วย stack trace และ object ของ error จาก PostgreSQL (`severity: 'FATAL'`, `code: '28P01'` = invalid password, `routine: 'auth_failed'`) สาเหตุคือ Pod ใหม่อ่าน `DATABASE_URL` จาก Secret ซึ่งยังเป็น `meow1234` ดูสถานะของ init container และ rollout

```bash
P=$(kubectl -n som-shop get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print $1}' | head -1); kubectl -n som-shop describe pod $P | sed -n '/Init Containers:/,/Containers:/p' | grep -E 'db-seed:|State|Reason|Exit Code|Restart Count'
for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " localhost:30080/api/stats; done; echo; curl -s localhost:30080/api/stats
kubectl -n som-shop rollout status deploy/som-web --timeout=60s
kubectl -n som-shop get deploy som-web; kubectl -n som-shop describe deploy som-web | grep -A4 Conditions
```

```text
    State:          Terminated
      Reason:       Completed
      Exit Code:    0
    Restart Count:  0
  db-seed:
    State:          Running
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
    Restart Count:  3
200 200 200 200 200 200 
som-web-7948ccf586-v8t4l 1.5 orders=3 products=6
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
error: deployment "som-web" exceeded its progress deadline
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
som-web   3/3     1            3           2m21s
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    False   ProgressDeadlineExceeded
```

- init container แรก (`wait-for-db`) ผ่าน (`Completed`) เพราะ `pg_isready` ไม่ต้องใช้รหัส ส่วน `db-seed` จบด้วย `Exit Code: 1` และ restart ซ้ำ
- `maxUnavailable: 0` ทำให้ Deployment ไม่ลบ Pod เดิมทั้ง 3 ตัวจนกว่า Pod ใหม่จะพร้อม (`READY 3/3`, `UP-TO-DATE 1`) และเมื่อไม่คืบหน้าเกิน `progressDeadlineSeconds: 60` ก็ขึ้น `ProgressDeadlineExceeded`
- curl 6 ครั้งรอบนี้ได้ 200 จาก Pod เดิมอีก (ยังใช้ connection ที่ค้างใน pool) แต่เป็นสถานะเดียวกับฉาก 4 ใน 9.13 ที่ Pod เดิมตัวเดียวกันตอบหน้า 503 ให้ browser **Pod เดิมไม่ได้ทำให้ร้านปกติ แค่ทำให้ไม่ดับสนิท**

### 9.8 ขั้น D3: แก้ซองให้ตรงรหัสใหม่ แล้ว restart

<p align="center" id="fig-20">
  <img src="images/20-lab9-update-restart.png" alt="รูปที่ 20 LAB 9 ขั้น D3 แก้ซองแล้ว restart" width="900"><br>
  <em><b>รูปที่ 20</b> ขั้น D3: create secret ... --dry-run=client -o yaml | kubectl apply -f - ด้วยรหัสใหม่ → rollout restart → Pod ใหม่ครบ 3 ตัว POST ได้ ออเดอร์เพิ่มเป็น 4 ข้อมูลเดิมไม่หาย</em>
</p>

อัปเดต Secret ทั้ง 2 key ด้วยวิธี `create ... --dry-run=client -o yaml | kubectl apply -f -` (เพราะ `create` อย่างเดียวได้ `already exists`)

```bash
kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=purr5678 --from-literal=DATABASE_URL=postgres://som:purr5678@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -
kubectl -n som-shop rollout restart deploy/som-web && time kubectl -n som-shop rollout status deploy/som-web --timeout=240s
sleep 8; kubectl -n som-shop get pod
```

```text
Warning: resource secrets/som-db-secret is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
secret/som-db-secret configured
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 0 out of 3 new replicas have been updated...
...
deployment "som-web" successfully rolled out

real	0m18.115s
NAME                       READY   STATUS    RESTARTS   AGE
som-db-0                   1/1     Running   0          2m21s
som-web-69bc85d7f7-7p5bz   1/1     Running   0          14s
som-web-69bc85d7f7-l5nrp   1/1     Running   0          27s
som-web-69bc85d7f7-ldt6z   1/1     Running   0          20s
```

`rollout restart` ครั้งใหม่สร้าง ReplicaSet ใหม่แทนตัวที่ค้าง `Init:Error` (ตัวนั้นถูกทิ้งไปเอง) ทั้ง 3 Pod ใหม่ใช้รหัส `purr5678` ทดลองสั่งออเดอร์ที่ 4

```bash
curl -s localhost:30080/api/stats; curl -s -XPOST -H "content-type: application/json" -d "{\"product_id\":4,\"qty\":2}" localhost:30080/api/orders; echo; ./hit.sh http://localhost:30080/api/stats 12 0.1
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}'; echo; kubectl -n som-shop get secret som-db-secret -o yaml | grep -c purr5678
kubectl -n som-shop rollout history deploy/som-web
```

```text
som-web-69bc85d7f7-l5nrp 1.5 orders=3 products=6
{"ok":true,"order_id":4,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":58}}
จำนวน  Pod  เวอร์ชัน
      7 som-web-69bc85d7f7-7p5bz 1.5 orders=4 products=6
      4 som-web-69bc85d7f7-l5nrp 1.5 orders=4 products=6
      1 som-web-69bc85d7f7-ldt6z 1.5 orders=4 products=6
ok=12 err=0 (ใช้เวลา 1.3 วินาที)
purr5678
{"apiVersion":"v1","data":{"DATABASE_URL":"cG9zdGdyZXM6Ly9zb206cHVycjU2NzhAc29tLWRiLTAuc29tLWRiOjU0MzIvY2F0c2hvcA==","POSTGRES_PASSWORD":"cHVycjU2Nzg="},"kind":"Secret","metadata":{"annotations":{},"name":"som-db-secret","namespace":"som-shop"}}

0
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 ป้ายร้านจาก ConfigMap
2         1.5 รหัส DB จาก Secret
3         1.5 รหัส DB จาก Secret
4         1.5 รหัส DB จาก Secret
```

- ทุก Pod เห็น `orders=4` ร้านกลับมาปกติด้วยรหัสใหม่
- annotation last-applied ที่วิธี pipe สร้างเก็บค่าเป็น **base64** (`grep -c purr5678` = `0`) ไม่ใช่ข้อความ
- `rollout restart` ไม่เปลี่ยน annotation `kubernetes.io/change-cause` revision 3 (ที่ค้าง) และ 4 จึงมีข้อความซ้ำ `1.5 รหัส DB จาก Secret` ถ้าต้องการบันทึกเหตุผลให้ถูก ให้สั่ง `kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.5 เปลี่ยนรหัส DB" --overwrite` ก่อน `rollout restart`

### 9.9 ขั้น D4: db เกิดใหม่ ออเดอร์และรหัสยังอยู่

```bash
kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders'; kubectl -n som-shop delete pod som-db-0 && kubectl -n som-shop wait --for=condition=Ready pod/som-db-0 --timeout=120s
sleep 5; kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders'; curl -s localhost:30080/api/stats; kubectl -n som-shop exec som-db-0 -- sh -c 'PGPASSWORD=purr5678 psql -h som-db-0.som-db -U som -d catshop -tAc "select 1"'
```

```text
4
pod "som-db-0" deleted from som-shop namespace
pod/som-db-0 condition met
4
som-web-69bc85d7f7-ldt6z 1.5 orders=4 products=6
1
```

`som-db-0` ตัวใหม่อ่าน `POSTGRES_PASSWORD=purr5678` จากซอง แต่ไม่ได้ใช้ (ฐานข้อมูลใน PVC มีอยู่แล้ว) รหัส `purr5678` ใช้ได้เพราะเราตั้งด้วย `ALTER USER` ในขั้น D1 ไม่ใช่เพราะแก้ Secret ออเดอร์ยัง 4 และ web ต่อใหม่ได้เอง

### 9.10 ขั้น E: ทางเข้า HTTPS ด้วย Secret ชนิด TLS

<p align="center" id="fig-21">
  <img src="images/21-lab9-https.png" alt="รูปที่ 21 LAB 9 ขั้น E HTTPS" width="900"><br>
  <em><b>รูปที่ 21</b> ขั้น E: secret tls som-tls + 30-https.yaml (nginx proxy → som-web) NodePort 30082 → curl -k https://localhost:30082/api/stats ได้ร้านเดิม; ไม่มี -k ได้ (60); มี Warning PodSecurity เพราะ nginx รันเป็น root</em>
</p>

ใช้ใบรับรองจาก LAB 4 (`CN=shop.som.local`, SAN `localhost`) สร้าง Secret `som-tls` แล้วเปิด nginx ที่ส่งต่อให้ Service `som-web`

```bash
kubectl -n som-shop create secret tls som-tls --cert=../labs/lab04-tls/tls.crt --key=../labs/lab04-tls/tls.key; kubectl -n som-shop get secret
kubectl apply -f k8s/30-https.yaml && kubectl -n som-shop rollout status deploy/som-https --timeout=120s
```

```text
secret/som-tls created
NAME            TYPE                DATA   AGE
som-db-secret   Opaque              2      2m41s
som-tls         kubernetes.io/tls   2      0s
configmap/som-https-conf created
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
deployment.apps/som-https created
service/som-https created
Waiting for deployment "som-https" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-https" successfully rolled out
```

Warning มาจาก label `pod-security.kubernetes.io/warn: restricted` ของ namespace (บทที่ 4) เพราะ `nginx:1.27-alpine` รันเป็น root เป็นแค่คำเตือน Pod ยังสร้างได้ (แบบที่ไม่มี Warning ดูด้านล่าง) ทดสอบ (รอ 5 วินาทีกัน `rc=35` แบบ LAB 4)

```bash
sleep 5; curl -sk https://localhost:30082/api/stats
curl -s --cacert ../labs/lab04-tls/tls.crt https://localhost:30082/api/shop; echo
curl -sS https://localhost:30082/api/stats; echo "rc=$?"
curl -sk -XPOST -H "content-type: application/json" -d "{\"product_id\":5,\"qty\":1}" https://localhost:30082/api/orders; echo; curl -sk https://localhost:30082/api/stats
curl -sk -o /dev/null -w "%{http_code} %{content_type}\n" https://localhost:30082/
kubectl -n som-shop exec deploy/som-https -- ls -laL /etc/nginx/tls
```

```text
som-web-69bc85d7f7-l5nrp 1.5 orders=4 products=6
{"pod":"som-web-69bc85d7f7-7p5bz","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · Secret","footer":"Next.js + PostgreSQL · Kubernetes LAB 011 · รหัส DB อยู่ใน Secret som-db-secret"}
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html
...
rc=60
{"ok":true,"order_id":5,"product":{"id":5,"name_th":"ขนมแมวเลียรสไก่ (แพ็ก 4)","stock":39}}
som-web-69bc85d7f7-ldt6z 1.5 orders=5 products=6
200 text/html; charset=utf-8
total 12
drwxrwxrwt    3 root     root           120 Oct  5 11:41 .
drwxr-xr-x    1 root     root          4096 Oct  5 11:41 ..
drwxr-xr-x    2 root     root            80 Oct  5 11:41 ..2026_10_05_11_41_11.4141799291
drwxr-xr-x    2 root     root            80 Oct  5 11:41 ..data
-r--------    1 root     root          1180 Oct  5 11:41 tls.crt
-r--------    1 root     root          1704 Oct  5 11:41 tls.key
```

เส้นทางของ request: ลูกค้า → `https://localhost:30082` (NodePort) → nginx `:8443` (ถอด TLS ด้วยกุญแจจาก Secret) → `http://som-web.som-shop.svc.cluster.local:80` → Pod web ร้านเดียวกันตอบได้ทั้งทาง HTTP 30080 และ HTTPS 30082 สั่งออเดอร์ที่ 5 ผ่าน HTTPS ได้

**ทางเลือกที่ผ่าน Pod Security restricted** `extra/30-https-restricted.yaml` ใช้ `nginxinc/nginx-unprivileged:1.27-alpine` (uid 101) พร้อม securityContext ครบ และเพราะไฟล์ใน Secret volume เป็นของ root จึงตั้ง `fsGroup: 101` + `defaultMode: 0440` ให้กลุ่ม nginx อ่านกุญแจได้

```bash
kubectl apply -f extra/30-https-restricted.yaml && kubectl -n som-shop rollout status deploy/som-https --timeout=120s
sleep 5; curl -sk https://localhost:30082/api/stats; kubectl -n som-shop exec deploy/som-https -- sh -c 'id; ls -laL /etc/nginx/tls'
```

```text
configmap/som-https-conf unchanged
deployment.apps/som-https configured
...
deployment "som-https" successfully rolled out
som-web-69bc85d7f7-ldt6z 1.5 orders=5 products=6
uid=101(nginx) gid=101(nginx) groups=101(nginx)
total 12
drwxrwsrwt    3 root     nginx          120 Oct  5 11:41 .
drwxrwxr-x    1 nginx    root          4096 Oct  5 11:41 ..
drwxr-sr-x    2 root     nginx           80 Oct  5 11:41 ..2026_10_05_11_41_18.4024641824
drwxr-sr-x    2 root     nginx           80 Oct  5 11:41 ..data
-r--r-----    1 root     nginx         1180 Oct  5 11:41 tls.crt
-r--r-----    1 root     nginx         1704 Oct  5 11:41 tls.key
```

ไม่มี Warning ของ PodSecurity และไฟล์เป็น `-r--r----- root nginx` แล้วสลับกลับเป็นไฟล์หลักเพื่อให้ตรงกับ `k8s/` (ใช้ต่อแบบ restricted ก็ได้)

```bash
kubectl apply -f k8s/30-https.yaml && kubectl -n som-shop rollout status deploy/som-https --timeout=120s; sleep 5; curl -sk https://localhost:30082/api/stats
```

```text
configmap/som-https-conf unchanged
Warning: would violate PodSecurity "restricted:latest": ...
deployment.apps/som-https configured
service/som-https unchanged
...
deployment "som-https" successfully rolled out
som-web-69bc85d7f7-l5nrp 1.5 orders=5 products=6
```

### 9.11 ขั้น F: ส่อง etcd อีกครั้ง

```bash
../labs/lab08-etcd/etcdget.sh /registry/secrets/som-shop/som-db-secret | grep -a -o 'postgres://[^@]*@'
```

```text
postgres://som:purr5678@
```

intern อ่านซองผ่าน API ไม่ได้ แต่ในตู้เอกสาร etcd รหัสใหม่ยังเป็นข้อความ ใครได้ข้อมูล etcd หรือ backup ไปก็อ่านได้ นี่คือปัญหาที่ต้องแก้ด้วย encryption at rest หรือระบบภายนอก (ทฤษฎีหัวข้อ 9 และ 13.4)

### 9.12 สภาพสุดท้ายของร้าน

```bash
kubectl apply -f k8s/ 2>&1; kubectl -n som-shop get all,secret,cm,pvc
kubectl --context intern get secrets; kubectl --context intern get deploy som-web -o yaml | grep -c -E 'meow1234|purr5678'
curl -s localhost:30080/api/stats; curl -sk https://localhost:30082/api/stats
```

```text
namespace/som-shop unchanged
service/som-db unchanged
statefulset.apps/som-db configured
configmap/som-web-config unchanged
configmap/som-announcement unchanged
deployment.apps/som-web unchanged
service/som-web unchanged
configmap/som-https-conf unchanged
deployment.apps/som-https unchanged
service/som-https unchanged
NAME                             READY   STATUS    RESTARTS   AGE
pod/som-db-0                     1/1     Running   0          43s
pod/som-https-6fdbf5b749-7wmr5   1/1     Running   0          7s
pod/som-web-69bc85d7f7-7p5bz     1/1     Running   0          60s
pod/som-web-69bc85d7f7-l5nrp     1/1     Running   0          73s
pod/som-web-69bc85d7f7-ldt6z     1/1     Running   0          66s

NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
service/som-db      ClusterIP   None            <none>        5432/TCP        3m34s
service/som-https   NodePort    10.96.25.39     <none>        443:30082/TCP   28s
service/som-web     NodePort    10.96.121.215   <none>        80:30080/TCP    3m34s
...
NAME                   TYPE                DATA   AGE
secret/som-db-secret   Opaque              2      3m9s
secret/som-tls         kubernetes.io/tls   2      28s
...
NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-5a9c2812-baf2-42ec-b11f-e3ddbb385214   1Gi        RWO            standard       <unset>                 3m34s
Error from server (Forbidden): secrets is forbidden: User "system:serviceaccount:som-shop:intern" cannot list resource "secrets" in API group "" in the namespace "som-shop"
0
som-web-69bc85d7f7-ldt6z 1.5 orders=5 products=6
som-web-69bc85d7f7-ldt6z 1.5 orders=5 products=6
```

`kubectl apply -f k8s/` ใช้ "คืนสภาพร้าน" ได้อย่างปลอดภัย เพราะไม่มีไฟล์ Secret อยู่ใน `k8s/` (รหัสที่เปลี่ยนแล้วไม่ถูกเขียนทับ) `statefulset.apps/som-db configured` ขึ้นทั้งที่ไม่ได้แก้ไฟล์ เพราะ kubectl เทียบกับค่าตั้งต้นที่ API server เติม เป็นเรื่องปกติ ไม่มี Pod ใดถูกสร้างใหม่ ทั้ง HTTP และ HTTPS ตอบ `orders=5`

### 9.13 เปิดร้านใน browser: HTTPS และเปลี่ยนรหัสอีกรอบ (ภาพหน้าจอจริง)

ดูผลใน 🌐 browser บนเครื่องนักศึกษา ภาพหน้าจอ 5 ภาพในหัวข้อนี้เป็น **ภาพหน้าจอจริงจากการทดลอง** (browser เปิด NodePort โดยตรง บนเครื่องนักศึกษาคือ `http://localhost:30080` และ `https://localhost:30082`) ถ่ายต่อจากสภาพใน 9.12 ออเดอร์จึงเป็น 5 ชื่อ Pod ในภาพต่างจากผลข้างบนเพราะถ่ายหลังผ่านการ `rollout restart` เพิ่มเติม

**ฉาก 1 — ร้านที่รหัสฐานข้อมูลมาจาก Secret** เปิด `http://localhost:30080`

<p align="center" id="fig-22">
  <img src="images/screenshots/20261005_1847_lab9sec_01-shop-password-from-secret.png" alt="รูปที่ 22 ภาพหน้าจอจริง ร้านที่รหัส DB มาจาก Secret" width="700"><br>
  <em><b>รูปที่ 22</b> ภาพหน้าจอจริงจากการทดลอง: ร้าน som-shop-v7 (som-shop-web:1.5) ที่ http://localhost:30080 หัวเว็บ "⚓ ท่าเรือ Kubernetes · Secret" ออเดอร์ทั้งหมด 5 — รหัสฐานข้อมูลมาจาก Secret som-db-secret ไม่ได้เขียนใน YAML แล้ว หน้าตาร้านเหมือนเดิมทุกอย่าง</em>
</p>

หน้าร้านเหมือนบทที่ 10 ทุกอย่าง (ธีม harbor, ประกาศ `📢 วันนี้ปลาทูสดมาก 🐟`) ต่างแค่หัวเว็บ `· Secret` ลูกค้าไม่รู้เลยว่ารหัสย้ายที่ไปแล้ว ซึ่งเป็นสิ่งที่ต้องการ

**ฉาก 2 — HTTPS กับใบรับรอง self-signed** เปิด `https://localhost:30082`

<p align="center" id="fig-23">
  <img src="images/screenshots/20261005_1848_lab9sec_02-https-selfsigned-warning.png" alt="รูปที่ 23 ภาพหน้าจอจริง browser เตือนใบรับรอง self-signed" width="700"><br>
  <em><b>รูปที่ 23</b> ภาพหน้าจอจริงจากการทดลอง: เปิด https://…:30082 แล้ว browser เตือน "Your connection is not private" NET::ERR_CERT_AUTHORITY_INVALID เพราะใบรับรองใน Secret som-tls เป็น self-signed (ที่อยู่ในภาพเป็นของเครื่องทดลอง บนเครื่องนักศึกษาจะเป็น localhost:30082)</em>
</p>

`NET::ERR_CERT_AUTHORITY_INVALID` = ใบรับรองไม่ได้ออกโดย CA ที่ browser เชื่อถือ (เหมือน `curl: (60) SSL certificate problem: self-signed certificate`) การเชื่อมต่อยังถูกเข้ารหัส แต่ browser ยืนยันไม่ได้ว่าปลายทางเป็นใคร

**ฉาก 3 — ยอมรับใบรับรองเพื่อทดสอบ** กด **Advanced → Proceed to localhost (unsafe)**

<p align="center" id="fig-24">
  <img src="images/screenshots/20261005_1848_lab9sec_03-shop-over-https-30082.png" alt="รูปที่ 24 ภาพหน้าจอจริง ร้านผ่าน HTTPS 30082" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: หลังกดยอมรับใบรับรอง ร้านเปิดผ่าน HTTPS ที่พอร์ต 30082 ได้ — nginx ถือใบรับรองและกุญแจจาก Secret som-tls แล้วส่งต่อให้ Service som-web ร้านเดียวกับพอร์ต 30080</em>
</p>

> การกดข้ามคำเตือนทำเพื่อทดสอบใน LAB เท่านั้น ในงานจริงต้องใช้ใบรับรองจาก CA จริง (เช่น Let's Encrypt ผ่าน cert-manager ร่วมกับ Ingress ในบทถัดไป)

**ฉาก 4 — เปลี่ยนรหัสใน DB แต่ยังไม่แก้ซอง (ลองผิดอีกรอบ)** ทำขั้น D1 + D2 ซ้ำด้วยรหัสตัวอย่างรอบที่ 3 `hiss9012` (ลำดับคำสั่งนี้ทดสอบแล้ว ในบันทึกรอบถ่ายภาพปิดรหัสเป็น `●●●●`)

```bash
kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -c "ALTER USER som PASSWORD 'hiss9012';"
kubectl -n som-shop rollout restart deploy/som-web
kubectl -n som-shop get pod -l app=som-web
curl -s localhost:30080/api/stats
P=$(kubectl -n som-shop get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print $1}' | head -1); kubectl -n som-shop logs $P -c db-seed | grep -E "error:|routine"
```

ผลจริงจากรอบถ่ายภาพ (รหัสปิดเป็น `●●●●`)

```text
$ kubectl exec som-db-0 -- psql ... ALTER USER som PASSWORD ●●●●
ALTER ROLE
$ kubectl rollout restart deploy/som-web
deployment.apps/som-web restarted
$ kubectl get pod -l app=som-web
NAME                       READY   STATUS       RESTARTS      AGE
som-web-58bb7ccfc6-2q5bx   1/1     Running      0             4m28s
som-web-58bb7ccfc6-jdtqs   1/1     Running      0             4m15s
som-web-58bb7ccfc6-phfth   1/1     Running      0             4m21s
som-web-695665d5b4-8xhr9   0/1     Init:Error   2 (32s ago)   35s
$ curl -s localhost:30080/api/stats
som-web-58bb7ccfc6-phfth 1.5 orders=5 products=6

$ kubectl logs som-web-695665d5b4-8xhr9 -c db-seed | grep -E "error:|routine"
error: password authentication failed for user "som"
  routine: 'auth_failed'
```

แล้ว refresh browser ที่ `http://localhost:30080` สองสามครั้ง

<p align="center" id="fig-25">
  <img src="images/screenshots/20261005_1850_lab9sec_04-old-pod-503-new-pod-init-error.png" alt="รูปที่ 25 ภาพหน้าจอจริง Pod เดิมตอบ 503 ระหว่างรหัสไม่ตรง" width="700"><br>
  <em><b>รูปที่ 25</b> ภาพหน้าจอจริงจากการทดลอง: หลัง ALTER USER โดยยังไม่แก้ Secret + rollout restart — Pod ใหม่ค้าง Init:Error (db-seed: password authentication failed for user "som") ส่วน Pod เดิม som-web-58bb7ccfc6-phfth ยังอยู่ แต่ browser ได้หน้า 503 "ร้านกำลังเตรียมสินค้า กรุณารอสักครู่" เพราะ connection ใหม่ยืนยันตัวตนไม่ผ่าน ร้านล่มเป็นช่วง ๆ ไม่ใช่ขายได้ปกติ</em>
</p>

ภาพนี้ยืนยันข้อเท็จจริงที่สำคัญที่สุดของขั้น D: **curl เมื่อครู่ได้ `orders=5` จาก Pod `som-web-58bb7ccfc6-phfth` แต่ไม่กี่วินาทีต่อมา Pod ตัวเดียวกันตอบหน้า 503 ให้ browser** เพราะทำงานได้เฉพาะ request ที่ใช้ connection ที่ค้างอยู่ใน pool เมื่อต้องเปิด connection ใหม่ (หน้าเว็บตรวจตารางในฐานข้อมูลทุกครั้ง) การยืนยันตัวตนไม่ผ่าน ร้านจึงล่มเป็นช่วง ๆ และ Pod ใหม่ก็ขึ้นไม่ได้ ห้ามปล่อยสถานะนี้ไว้

**ฉาก 5 — แก้ซองให้ตรงรหัสใหม่ + rollout restart** (ขั้น D3 ด้วยรหัส `hiss9012`)

```bash
kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=hiss9012 --from-literal=DATABASE_URL=postgres://som:hiss9012@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -
kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s
kubectl -n som-shop get pod
curl -s localhost:30080/api/stats
```

ผลจริงจากรอบถ่ายภาพ

```text
$ kubectl create secret generic som-db-secret ... --dry-run=client -o yaml | kubectl apply -f -
secret/som-db-secret configured
$ kubectl rollout restart deploy/som-web && kubectl rollout status deploy/som-web
deployment.apps/som-web restarted
deployment "som-web" successfully rolled out
$ kubectl get pod
NAME                         READY   STATUS        RESTARTS   AGE
som-db-0                     1/1     Running       0          7m45s
som-https-6fdbf5b749-7wmr5   1/1     Running       0          7m9s
som-web-5588c58f7f-k2chg     1/1     Running       0          17s
som-web-5588c58f7f-r7hhg     1/1     Running       0          6s
som-web-5588c58f7f-s29jc     1/1     Running       0          11s
som-web-58bb7ccfc6-phfth     1/1     Terminating   0          4m48s
$ curl -s localhost:30080/api/stats
som-web-5588c58f7f-k2chg 1.5 orders=5 products=6
```

<p align="center" id="fig-26">
  <img src="images/screenshots/20261005_1851_lab9sec_05-new-password-shop-back-orders-kept.png" alt="รูปที่ 26 ภาพหน้าจอจริง รหัสใหม่ ร้านกลับมา ออเดอร์ครบ" width="700"><br>
  <em><b>รูปที่ 26</b> ภาพหน้าจอจริงจากการทดลอง: แก้ Secret som-db-secret ให้ตรงรหัสใหม่แล้ว rollout restart — Pod ใหม่ som-web-5588c58f7f-… ทั้ง 3 ตัว Running ร้านกลับมาเปิดปกติ ออเดอร์ทั้งหมดยังเป็น 5 เท่าเดิม (ข้อมูลอยู่ใน PVC ไม่ได้หายไปกับการเปลี่ยนรหัส)</em>
</p>

Pod เดิมที่ล่มเป็นช่วง ๆ ถูกแทนที่ด้วย Pod ใหม่ที่ใช้รหัสถูก ออเดอร์ยังครบ 5 สรุปบทเรียน: **เปลี่ยนรหัส = `ALTER USER` + แก้ซองทั้ง 2 key + `rollout restart` ทำต่อเนื่องกันทันที**

### 9.14 สรุป LAB 9

<p align="center" id="fig-27">
  <img src="images/22-lab9-wrap-up.png" alt="รูปที่ 27 สรุป LAB 9" width="900"><br>
  <em><b>รูปที่ 27</b> สรุป LAB9: รหัสออกจาก YAML แล้ว (Secret + secretKeyRef), เปลี่ยนรหัสจริงสำเร็จ ออเดอร์ยังอยู่, intern อ่านซองไม่ได้ — แต่ etcd ยังเก็บเป็นข้อความ และต่อไปจะใช้ Ingress/HPA/Helm</em>
</p>

| ขั้น | ทำอะไร | ผลจริง | ออเดอร์ |
|---|---|---|:---:|
| เริ่ม | `apply -f k8s-010/` + สั่ง 3 ออเดอร์ | rollout 14 วินาที, `orders=0` → `orders=3` | 3 |
| A | intern อ่าน Deployment/StatefulSet | `som:meow1234@` 4 บรรทัด, `POSTGRES_PASSWORD value: meow1234` | 3 |
| B | `create secret generic som-db-secret` | `DATABASE_URL: 52 bytes`, `POSTGRES_PASSWORD: 8 bytes`, ไม่มี annotation | 3 |
| C1 | db ใช้ `secretKeyRef` | rollout ราว 2 วินาที PVC เดิม | 3 |
| C2 | web + db-seed ใช้ `secretKeyRef` | intern `grep -c meow1234` = `0`, get secret/exec → `Forbidden` | 3 |
| D1 | `ALTER USER ... 'purr5678'` | curl ได้ 200 จาก connection ค้าง แต่ connection ใหม่ไม่ผ่าน → ล่มเป็นช่วง ๆ (503) | 3 |
| D2 | `rollout restart` โดยไม่แก้ซอง | Pod ใหม่ `Init:Error` (`password authentication failed`), `ProgressDeadlineExceeded` | 3 |
| D3 | แก้ซอง + `rollout restart` | 3 Pod ใหม่ ราว 18 วินาที, ออเดอร์ที่ 4 | 4 |
| D4 | ลบ `som-db-0` | `count(*)` 4 เท่าเดิม รหัส `purr5678` ใช้ได้ | 4 |
| E | `secret tls som-tls` + `30-https.yaml` | `https://localhost:30082` ใช้ได้, ไม่มี `-k` → `rc=60`, ออเดอร์ที่ 5 ผ่าน HTTPS | 5 |
| F | etcdctl | `postgres://som:purr5678@` เป็นข้อความ | 5 |
| ภาพหน้าจอ | เปลี่ยนรหัสอีกรอบ | 503 เป็นช่วง ๆ → แก้ซอง → ร้านกลับมา | 5 |

**คำถามท้าย LAB 9**

1. ทำไมขั้น B สร้าง Secret ด้วย `kubectl create secret generic` แทน `kubectl apply -f examples/05-secret.example.yaml` และทำไมไฟล์ตัวอย่างจึงไม่อยู่ใน `k8s/`
2. ขั้น C1 ทำให้ `som-db-0` เกิดใหม่ แต่ทำไม `POSTGRES_PASSWORD` จากซองจึงไม่มีผลกับฐานข้อมูลเลย และถ้าลบ PVC ด้วยจะเกิดอะไรกับรหัสและออเดอร์
3. หลังขั้น D1 curl ได้ `200` ทุกครั้ง แต่ browser ได้ 503 เป็นช่วง ๆ อธิบายความต่างนี้ด้วยเรื่อง connection pool และบอกว่าทำไมการทดสอบด้วย curl ไม่กี่ครั้งจึงไม่พอ
4. ในขั้น D2 ทำไม Deployment จึงไม่ลบ Pod เดิมทั้ง 3 ตัว และถ้าตั้ง `maxUnavailable: 1` ร้านจะเป็นอย่างไร
5. intern ทำอะไรได้บ้างและทำอะไรไม่ได้ในร้านตอนจบ LAB ถ้าเพิ่มสิทธิ์ `create pods` ให้ intern จะเกิดความเสี่ยงอะไร (เชื่อมกับ LAB 7)
6. ขั้น F แสดงว่า etcd ยังเก็บ `purr5678` เป็นข้อความ เสนอวิธีแก้อย่างน้อย 2 วิธี พร้อมข้อดีข้อเสีย

### 9.15 เก็บกวาด LAB 9

ถ้าจะเรียนบทถัดไปต่อทันทีเก็บร้านไว้ได้ ถ้าต้องการคืนทรัพยากรหรือก่อนทำ LAB นี้ซ้ำ ให้ลบทั้ง namespace (ลบ Deployment, StatefulSet, ConfigMap, Secret `som-db-secret`/`som-tls`, ServiceAccount `intern` และ PVC `data-som-db-0` พร้อมออเดอร์ทั้งหมด และคืน NodePort 30080/30082) แล้วลบ context/user `intern` ออกจาก kubeconfig (token ข้างในใช้ไม่ได้แล้วเมื่อ ServiceAccount ถูกลบ)

```bash
kubectl delete ns som-shop
kubectl config delete-context intern
kubectl config delete-user intern
```

ใช้เวลาราว 30 วินาที (Pod web มี preStop 5 วินาที) ถ้า token ของ context `intern` หมดอายุ (24 ชั่วโมง) ระหว่างทำ LAB ให้รัน `./rbac/intern-context.sh` ใหม่ในโฟลเดอร์ `som-shop-v7`

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v7/`, kubectl แจ้ง `the path "..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 011_kubernetes_secret k8s-lab:/workspace/` แล้ว 🐧 `cd` ไปโฟลเดอร์ของ LAB นั้น ตรวจด้วย `pwd` |
| `./wait-secret.sh: Permission denied` (หรือ `setup-registry.sh`, `cleanup-registry.sh`, `etcdget.sh`, `intern-context.sh`, `hit.sh`) | สิทธิ์ execute หายระหว่างคัดลอก | รันด้วย `bash <ชื่อสคริปต์> ...` หรือ `chmod +x *.sh` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 5 (โหลด postgres และ build/load `som-shop-web:1.5`) |
| `error: failed to create secret secrets "demo" already exists` | `kubectl create` ใช้สร้างใหม่เท่านั้น | ลบก่อน หรือ `kubectl create secret ... --dry-run=client -o yaml \| kubectl apply -f -` |
| ค่าที่ถอดได้มี `\n` ติดท้าย / base64 ลงท้ายด้วย `K` / แอป login ไม่ผ่านทั้งที่รหัส "ถูก" | ใช้ `echo` (ไม่มี `-n`) หรือไฟล์ `--from-file` มี newline ท้าย | `echo -n`, `printf '%s'` หรือ `--from-literal`/`stringData` ตรวจด้วย `... \| base64 -d \| od -c` |
| เห็นรหัสเป็นข้อความใน annotation `last-applied-configuration` ของ Secret | `kubectl apply -f` ไฟล์ที่มี `stringData` | สร้างใหม่ด้วย `kubectl create secret` หรือ pipe ผ่าน `--dry-run=client -o yaml` / `apply --server-side` แล้วเปลี่ยนรหัสถ้าเป็นรหัสจริง |
| `[data[username]: Required value, data[password]: Required value]` / `data[tls.key]: Required value` | type ตรวจ key ไม่ครบ | ใส่ key ตามที่ type ต้องการ (ทฤษฎีหัวข้อ 3.1) |
| `tls: failed to find any PEM data in certificate input` / `... in key input` | ไฟล์ cert/key ไม่ใช่ PEM หรือสลับกัน | ตรวจด้วย `openssl x509 -in tls.crt -noout -subject` และใช้ `--cert=tls.crt --key=tls.key` |
| `Too long: may not be more than 1048576 bytes` | Secret รวมทุก key เกิน 1 MiB | เก็บไฟล์ใหญ่ที่อื่น Secret ใช้กับความลับขนาดเล็ก |
| Pod ค้าง `CreateContainerConfigError` + `secret "..." not found` / `couldn't find key ...` | Secret/key ที่อ้างไม่มีใน namespace ของ Pod (สะกดผิด, ข้าม LAB 1–2, อยู่คนละ namespace) | `kubectl get secret -n <ns>` สร้าง/แก้ชื่อให้ตรง หรือใส่ `optional: true` ถ้าไม่จำเป็นจริง |
| `pods "spod" not found` / `secrets "demo" not found` ใน LAB 3–8 | ลบไปแล้ว หรือข้าม LAB 1–3 | ทำ LAB 1 (`demo`), LAB 2 (`sd`) และ LAB 3 (`spod`) ใหม่ |
| แก้ Secret แล้วไฟล์ใน volume ยังไม่เปลี่ยนหลัง 30–60 วินาที | kubelet sync เป็นรอบ (วัดได้ 71–81 วินาที) | รอได้ถึง 2 นาที ถ้าเกินตรวจว่าไม่ได้ใช้ `subPath` และแก้ Secret ชื่อ/namespace ถูก |
| env ไม่เปลี่ยนหลังแก้ Secret | พฤติกรรมปกติ env อ่านครั้งเดียวตอนเริ่ม | ลบแล้วสร้าง Pod ใหม่ หรือ `kubectl rollout restart` (Deployment) |
| ``The Secret "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set`` | Secret เป็น `immutable: true` | ลบแล้วสร้างใหม่ หรือใช้ชื่อใหม่ |
| `curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL` ทันทีหลัง Pod Ready | เส้นทาง NodePort ยังไม่พร้อม | รอราว 5 วินาทีแล้วลองใหม่ |
| `curl: (60) SSL certificate problem: self-signed certificate` | ใบรับรอง self-signed | ทดสอบด้วย `curl -k` หรือ `--cacert tls.crt` (ตรวจจริง) |
| `curl: (60) SSL: no alternative certificate subject name matches target host name '127.0.0.1'` | เรียกด้วยชื่อที่ไม่อยู่ใน subjectAltName | ใช้ `https://localhost:...` หรือ `--resolve shop.som.local:30081:127.0.0.1` |
| `400 The plain HTTP request was sent to HTTPS port` | ใช้ `http://` กับพอร์ต HTTPS | ใช้ `https://` |
| browser ขึ้น `NET::ERR_CERT_AUTHORITY_INVALID` | ใบรับรอง self-signed | ปกติใน LAB กด Advanced → Proceed (เฉพาะทดสอบ) |
| `provided port is already allocated` ตอน apply `tls.yaml`, `20-web.yaml` หรือ `30-https.yaml` | Service อื่นจอง 30081/30080/30082 อยู่ (เช่น ร้านบทที่ 10 ค้าง หรือ `ngx-tls` ยังไม่ลบ) | `kubectl get svc -A \| grep 3008` แล้วลบของที่ค้าง |
| LAB 5 `docker: Error response from daemon: Conflict. The container name "/kind-registry" is already in use` หรือพอร์ต 5001 ถูกใช้ | registry จากรอบก่อนค้าง | `./cleanup-registry.sh` แล้วรัน `./setup-registry.sh` ใหม่ |
| LAB 5 Pod `withpull`/`viasa` ก็ `ErrImagePull` | ยังไม่ได้สร้าง `regcred` ใน namespace `reg`, `--docker-server` ไม่ตรงกับชื่อใน image หรือ `hosts.toml` ยังไม่ถูกเขียน | ตรวจ `kubectl -n reg get secret`, `docker exec lab-worker cat /etc/containerd/certs.d/kind-registry:5000/hosts.toml` แล้วรัน `setup-registry.sh` ใหม่ |
| `no basic auth credentials` / `401 Unauthorized` | ไม่มีบัตร / บัตรผิด (ตั้งใจใน LAB 5) | ใส่ `imagePullSecrets` ที่ถูกต้องใน namespace เดียวกับ Pod หรือผูกกับ ServiceAccount |
| Pod ร้าน `som-shop-web:1.5` ติด `ErrImagePull` ... `insufficient_scope` หลังทำ LAB 5 | นำ image ของร้านขึ้น registry ส่วนตัวแล้วดึงด้วยบัตร (ผิดกติกา LAB 5) kubelet ผูก image กับบัตร | ห้ามทำตั้งแต่แรก ถ้าเกิดแล้ววิธีที่ง่ายที่สุดคือ `k8s-down` → `k8s-up` แล้วทำ LAB 0 ขั้นที่ 5 ใหม่ |
| describe ของ `builder-token` แสดง token ยาวเต็มจอ | พฤติกรรมของ Secret ชนิด service-account-token | ห้ามแปะ/ส่ง token บังในภาพหน้าจอ ลบ Secret ทิ้งหลัง LAB |
| `Error from server (Forbidden): ... cannot get resource "secrets"` | ตั้งใจใน LAB 7/9 (intern/maker) | ถ้าเกิดกับตัวเอง ตรวจว่าไม่ได้ใส่ `--as=...` หรือ `--context intern` ค้างไว้ |
| `error: You must be logged in to the server (Unauthorized)` ตอนใช้ `--context intern` | token อายุ 24 ชั่วโมงหมดอายุ หรือ namespace `som-shop` ถูกลบแล้วสร้างใหม่ | 🐧 `./rbac/intern-context.sh` ใหม่ใน `som-shop-v7` (หลัง `kubectl apply -f rbac/intern.yaml`) |
| `grep -c ...` พิมพ์ `0` แล้ว exit code 1 | `grep` คืน 1 เมื่อไม่เจอ | ปกติ (ใน LAB 9 คือผลที่ต้องการ) |
| LAB 8 `etcdget.sh` ได้ `error: unable to upgrade connection` หรือหา Pod etcd ไม่เจอ | ชื่อคลัสเตอร์ไม่ใช่ `lab` หรือ etcd ยังไม่พร้อม | `kubectl -n kube-system get pod -l component=etcd` ต้องเห็น `etcd-lab-control-plane` |
| `cat -v` แสดงตัวอักษรแปลก ๆ | ข้อมูล etcd เป็น protobuf (ไบนารี) | ปกติ ใช้ `grep -a -o '<คำ>'` หาเฉพาะค่าที่ต้องการ |
| LAB 9 `orders=0` ตอนเริ่ม | ร้านเพิ่งเปิดบนฐานข้อมูลใหม่ | สั่ง 3 ออเดอร์ตามขั้น 9.2 |
| LAB 9 Pod ใหม่ `Init:Error` และ log db-seed `password authentication failed for user "som"` | รหัสใน Secret ไม่ตรงกับรหัสในฐานข้อมูล (ขั้น D2 ตั้งใจ) | แก้ Secret ทั้ง `POSTGRES_PASSWORD` และ `DATABASE_URL` ให้ตรงกับ `ALTER USER` แล้ว `rollout restart` |
| LAB 9 browser ได้หน้า 503 "ร้านกำลังเตรียมสินค้า" เป็นช่วง ๆ แต่ curl บางครั้งได้ 200 | เปลี่ยนรหัสใน DB แล้วแต่ Pod ยังใช้รหัสเก่า: ได้เฉพาะ connection ที่ค้างใน pool | ทำขั้น D3 ทันที |
| `error: deployment "som-web" exceeded its progress deadline` | Pod ใหม่ไม่พร้อมภายใน 60 วินาที (`progressDeadlineSeconds`) | ดูสาเหตุจาก `kubectl -n som-shop logs <pod> -c db-seed` แก้แล้ว `rollout restart` |
| ทดสอบรหัสด้วย `psql -h 127.0.0.1` ผ่านทุกรหัส | `pg_hba.conf` ให้ `127.0.0.1/32 trust` | ทดสอบด้วย `-h som-db-0.som-db` |
| แก้ `POSTGRES_PASSWORD` ใน Secret แล้วรหัส DB ไม่เปลี่ยน | ใช้แค่ตอน initdb ครั้งแรก | เปลี่ยนด้วย `ALTER USER` (ขั้น D1) |
| `Warning: resource secrets/som-db-secret is missing the kubectl.kubernetes.io/last-applied-configuration annotation` | apply ทับ Secret ที่สร้างด้วย `create` | ปกติ kubectl เติมให้เอง |
| `Warning: would violate PodSecurity "restricted:latest"` ตอน apply `30-https.yaml` | nginx รันเป็น root ใน namespace ที่ตั้ง `warn: restricted` | เป็นแค่คำเตือน หรือใช้ `extra/30-https-restricted.yaml` |
| `rollout history` CHANGE-CAUSE ซ้ำ `1.5 รหัส DB จาก Secret` หลายบรรทัด | `rollout restart` ไม่เปลี่ยน annotation `change-cause` | ปกติ หรือ `kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="..." --overwrite` ก่อน restart |
| `statefulset.apps/som-db configured` ตอน `kubectl apply -f k8s/` ทั้งที่ไม่ได้แก้ไฟล์ | kubectl เทียบกับค่าตั้งต้นที่ API server เติม | ปกติ `som-db-0` ไม่ restart |
| browser เปิด `http://localhost:30080` หรือ `https://localhost:30082` ไม่ได้ ทั้งที่ใน k8s-lab curl ได้ | container `k8s-lab` ไม่ได้ publish พอร์ตนั้น หรือโปรแกรมอื่นใช้พอร์ต | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp`–`30082/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30082:localhost:30082 root@localhost` แล้วเปิดใหม่ |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 9 ทั้ง 6 ข้อ **ทุกภาพต้องบังรหัสผ่านจริงและ token** (รหัสตัวอย่างของ LAB แสดงได้)

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `kubectl get secret -A` (มีแค่ `bootstrap-token-abcdef`) และ `crictl images` ที่เห็น `som-shop-web 1.5` + `postgres 17.11-alpine` บนทั้งสอง worker
- [ ] **LAB 1** `get secret demo -o yaml` (`bWVvdzEyMzQ=`), `base64 -d` ได้ `meow1234`, `echo` vs `echo -n` และ `describe` (`password:  8 bytes`)
- [ ] **LAB 2** `bWVvdzEyMzQ=` vs `bWVvdzEyMzQK` ของ `--from-file`, `get secret sd -o yaml` ที่เห็น `stringData` ใน `last-applied-configuration`, ตารางเทียบ 3 วิธี (viapipe/viass), error ของ type ทั้ง 3 แบบ, `.dockerconfigjson` ที่ถอดแล้ว และ `Too long`
- [ ] **LAB 3** env `DB_`/`SD_`, `mount` (tmpfs ro), `-r--------`, `Read-only file system`, ผล `./wait-secret.sh` ทั้ง 2 รอบพร้อมเวลาของเครื่องตัวเอง, `newpass-01` หลังสร้าง Pod ใหม่ และ error ของ `frozen` ทั้ง 2 แบบ
- [ ] **LAB 4** `openssl x509 ... -subject -enddate`, `rc=35` → `(60)` → `-k`/`--cacert` ได้ `HTTPS ร้านน้องส้ม`, error ของ `127.0.0.1`, ไฟล์ใน Pod `-r--------` และ browser ที่ `https://localhost:30081` (หน้าเตือน + หลัง Proceed)
- [ ] **LAB 5** `HTTP 401` ของ setup, Events `no basic auth credentials` (nopull), `Successfully pulled` + log เมนูลับ (withpull), `401 Unauthorized` (wrong), `[{"name":"regcred"}]  Running` (viasa), `cached` ยัง `ImagePullBackOff` + `shopcheck` ได้ `som-shop-web:1.5 ok` และผล `./cleanup-registry.sh`
- [ ] **LAB 6** `ls -laLR /etc/som` (`-r--r-----`), ค่า 3 ไฟล์, `describe secret builder-token` (**บังบรรทัด token**), `get sa builder -o yaml` ไม่มี `secrets:` และ payload ของ `kubectl create token`
- [ ] **LAB 7** can-i ของ intern (yes/yes/no/no), `Forbidden` 3 แบบ, `secretKeyRef` ใน YAML ของ `spod`, `pods/exec` ถูกปฏิเสธ, maker `no`/`yes` และ `stolen=newpass-01`
- [ ] **LAB 8** `./etcdget.sh --keys ...`, `grep -a -o newpass-01`, `cat -v` ที่เห็น `password^R` + `newpass-01`, `rc=1` ของ grep encryption และผลเก็บกวาด LAB 1–8
- [ ] **LAB 9** (1) `orders=0` → `orders=3` และ intern เห็น `som:meow1234@` 4 บรรทัด (2) `describe secret som-db-secret` (3) C1 `som-db-0` AGE ใหม่ + PVC เดิม + `orders=3` (4) C2 intern `grep -c meow1234` = `0` + `Forbidden` + `pods/exec` ถูกปฏิเสธ (5) D1 ผล `-h som-db-0.som-db` รหัสเก่า/ใหม่ และ `-h 127.0.0.1` (6) D2 `Init:Error` + บรรทัด `error: password authentication failed for user "som"` + `ProgressDeadlineExceeded` (7) D3 `orders=4` + `grep -c purr5678` = `0` (8) D4 `count(*)` เท่าเดิม (9) E `curl -sk https://localhost:30082/api/stats` + `rc=60` + Warning PodSecurity (10) F `postgres://som:purr5678@` (11) browser 5 ฉากของ 9.13 ของเครื่องตัวเอง (`http://localhost:30080`, หน้าเตือน cert, `https://localhost:30082`, หน้า 503 + `Init:Error`, ร้านกลับมา `orders` เท่าเดิม)
- [ ] ท้ายสุด `kubectl get secret` ใน `default` ว่าง, `docker ps -a | grep kind-registry` ไม่มี และ `kubectl config get-contexts` ไม่มี `intern` (ถ้าลบร้านแล้ว)

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab (path ในตารางนับจาก `/workspace/011_kubernetes_secret/02_LAB`)

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Secret `demo`, `sd`, `fromfile`, `fromfile-nl`, `viapipe`, `viass`, `onlypw`, `ba`, `regcred`, `frozen`, `shop-tls`, `builder-token` (namespace `default`) | 1–6 | `kubectl get secret` | คำสั่งเก็บกวาดใน LAB 8 ขั้นที่ 4 |
| Pod `spod`, `proj`, `ngx-tls` + Service `ngx-tls` (**จอง NodePort 30081**) + ConfigMap `ngx-tls-conf`, `shop-board` | 3, 4, 6 | `kubectl get pod,svc,cm` | คำสั่งเก็บกวาดใน LAB 8 ขั้นที่ 4 |
| ServiceAccount `intern`, `maker`, `builder` + Role/RoleBinding `intern-view`, `pod-maker` | 6, 7 | `kubectl get sa,role,rolebinding` | `kubectl delete -f labs/lab07-rbac/intern.yaml -f labs/lab07-rbac/maker.yaml -f labs/lab06-projected/builder-token.yaml --ignore-not-found` |
| Pod `peek` | 7 | `kubectl get pod peek` | `kubectl delete pod peek` |
| ไฟล์ `labs/lab02-types/pw-nl.txt` | 2 | `ls labs/lab02-types` | `rm -f labs/lab02-types/pw-nl.txt` |
| ไฟล์ `labs/lab04-tls/tls.crt`, `tls.key` | 4 | `ls labs/lab04-tls` | **เก็บไว้จนจบ LAB 9** แล้วลบได้ `rm -f labs/lab04-tls/tls.crt labs/lab04-tls/tls.key` |
| container `kind-registry`, namespace `reg`/`reg2`, รหัสใน `~/.docker/config.json`, image `localhost:5001/som-menu:1.0`, โฟลเดอร์ `labs/lab05-registry/auth/` | 5 | `docker ps -a \| grep kind-registry`; `kubectl get ns reg reg2`; `ls labs/lab05-registry` | `cd labs/lab05-registry && ./cleanup-registry.sh` |
| `hosts.toml` ของ `kind-registry:5000` และ image `kind-registry:5000/som-menu:1.0` บน Node | 5 | `docker exec lab-worker crictl images \| grep som-menu` | ไม่มีผลกับ LAB อื่น ปล่อยไว้ได้ (หายไปเมื่อ `k8s-down`) **ห้าม `crictl rmi`** |
| namespace `som-shop` (**จอง NodePort 30080, 30082**) + Secret `som-db-secret`, `som-tls`, ServiceAccount `intern`, PVC `data-som-db-0` | 9 | `kubectl get ns som-shop`; `kubectl -n som-shop get all,secret,cm,pvc,sa` | `kubectl delete ns som-shop` |
| context/user `intern` ใน kubeconfig | 9 | `kubectl config get-contexts` | `kubectl config delete-context intern; kubectl config delete-user intern` |
| image `som-shop-web:1.5`, postgres, nginx, busybox บน Node และ `/root/postgres.tar` | 0–9 | `docker exec lab-worker crictl images`; `ls /root/postgres.tar` | **เก็บ image ไว้ได้** (ถ้า `k8s-down` จะหายไปด้วย) ไฟล์ tar ลบได้ `rm -f /root/postgres.tar` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl get ns
kubectl get pod,secret,cm,sa
kubectl get pv,pvc -A
docker ps -a | grep kind-registry || echo "ไม่มี kind-registry แล้ว"
kubectl config get-contexts
```

ผลที่ถูกต้อง: 3 Node `Ready`, ใน namespace `default` ไม่มี Pod และไม่มี Secret, มี ConfigMap แค่ `kube-root-ca.crt` และ ServiceAccount แค่ `default` (ผลจริงท้าย LAB 8: `configmap/kube-root-ca.crt   1      7m45s`, `serviceaccount/default   7m45s`) ถ้าลบ `som-shop` แล้ว namespace จะเหลือ 5 ตัวตั้งต้น (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`) ไม่มี PV/PVC และ context เหลือแค่ `kind-lab`

คลัสเตอร์ `lab` และ image ของร้านเก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

บทถัดไปจะแก้ปัญหาที่ยังเหลือจากบทนี้: เปิดร้านด้วยชื่อโดเมนและ TLS ที่ทางเข้าเดียว (**Ingress**), เพิ่ม/ลดบูธอัตโนมัติตามโหลด (**HPA**) และแพ็กทั้งร้านรวม ConfigMap/Secret เป็นชุดเดียว (**Helm**) ส่วนการเข้ารหัส etcd (EncryptionConfiguration/KMS) และตู้นิรภัยภายนอก (External Secrets/Vault) ดูทฤษฎีหัวข้อ 9 และ 11

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ Pod และจำนวนวินาที) เป็นค่าตัวอย่าง รหัสผ่านในภาพเป็นค่าตัวอย่างหรือปิดเป็น `●●●●` ผู้เรียนควรใช้ผลลัพธ์จากเครื่องตัวเองและเนื้อหาในเอกสารนี้เป็นหลัก
