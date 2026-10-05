# LAB บทที่ 9: StatefulSet — บูธเลขคงที่และตู้เซฟประจำตัว สู่ครัวกลางแบบโปรดักชันของร้านน้องส้ม

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ StatefulSet — เทียบ Deployment กับ StatefulSet, headless Service และ DNS ต่อ Pod (Pod ที่ไม่ Ready หายจาก DNS), volumeClaimTemplates, OrderedReady/Parallel, scale และ PVC retention, RollingUpdate + partition + rollout undo, OnDelete + minReadySeconds, ลบ StatefulSet (รวม `--cascade=orphan`) แล้ว apply ใหม่, Node ล่มกับ at-most-one และ taint `out-of-service` และร้านอาหารแมวน้องส้มที่ย้ายฐานข้อมูลจาก Deployment ของบทที่ 8 มาเป็น StatefulSet พร้อม read replica ด้วย postgres streaming replication
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะช่วยน้องส้มเปลี่ยน "หัวหน้ากะ" ของครัวกลาง จากผู้จัดการร้านที่ถือใบเบิกใบเดียว (Deployment) มาเป็น **หัวหน้ากะที่ถือเครื่องจ่ายบัตรคิว (StatefulSet)** เริ่มจากเทียบชื่อ Pod ของ Deployment กับ StatefulSet ดู **สมุดรายชื่อ (headless Service)** ที่บอกที่อยู่ของแต่ละบูธ ให้แต่ละบูธได้ **ตู้เซฟประจำตัว (volumeClaimTemplates)** ดูลำดับการเปิด/ปิดบูธ ทดลองว่าตู้หายหรือไม่เมื่อ scale ลงหรือลบ StatefulSet เปลี่ยนรุ่นทีละบูธด้วย **เชือกกั้นแถว (partition)**, OnDelete และ minReadySeconds แล้วหยุดเรือ (Node) ให้ติดหมอกเพื่อดูว่าทำไม StatefulSet ไม่ยอมสร้างบูธแทน ปิดท้ายด้วย **ร้านอาหารแมวน้องส้มแบบโปรดักชัน** (`som-shop-v5`) ที่ **ย้ายตู้เซฟเดิมของบทที่ 8** มาเป็น PVC `data-som-db-0` ของ StatefulSet `som-db` แล้วพิสูจน์ว่าลบ Pod ลบ StatefulSet หรือ rolling update ออเดอร์ก็ไม่หาย เห็นด้วยตาว่า scale เป็น 3 ได้ฐานข้อมูลเปล่า และทำ read replica จริงใน LAB เสริม

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, Kubernetes v1.37.0, kubectl v1.37.1) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, UID, ชื่อ Pod ของ Deployment ที่สุ่ม, ชื่อ PV (`pvc-<uid>`), revision hash, Node ที่ Pod ถูกวาง และจำนวนวินาทีที่รอ ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ แต่ **ชื่อ Pod ของ StatefulSet (`web-0`, `som-db-0`) และชื่อ PVC (`www-web-1`, `data-som-db-0`) จะเหมือนกันทุกเครื่อง** ให้ยึดผลจากเครื่องตัวเองเสมอ คำสั่งในเอกสารจึงดึงชื่อ PV/Node ใส่ตัวแปร (`PV=$(...)`, `N=$(...)`) แทนการพิมพ์ชื่อตายตัว

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิด browser ที่ `http://localhost:30080` ใน LAB 10 Node ของคลัสเตอร์ kind (`lab-control-plane`, `lab-worker`, `lab-worker2`) เป็น container ที่รันอยู่ **ข้างใน k8s-lab** คำสั่ง `docker stop`/`docker start` Node ใน LAB 9 และ `docker exec <node> crictl images` จึงรันใน SSH session ของ k8s-lab ไม่ใช่บนเครื่องนักศึกษา

### กติกาของ LAB บทนี้

- LAB 1–9 ทำในโฟลเดอร์ **`/workspace/009_kubernetes_statefulset/02_LAB/labs/labNN-...`** ของแต่ละ LAB ภายใน k8s-lab ส่วน LAB 10 ทำใน **`/workspace/009_kubernetes_statefulset/02_LAB/som-shop-v5`** ทุก LAB เริ่มด้วย `cd` ไปโฟลเดอร์ของตัวเอง
- LAB 1–9 ใช้ namespace `default` และ LAB 10 ใช้ `som-shop` **StatefulSet `web` ที่สร้างใน LAB 3 ใช้ต่อเนื่องถึง LAB 9** (ไม่ลบระหว่างทาง) ทำ LAB 3–9 ต่อกันในรอบเดียวจะง่ายที่สุด ถ้าหยุดกลางทางให้กลับมาเริ่มที่ LAB 3 ใหม่ได้เสมอ
- **PVC ของ StatefulSet ไม่หายเองเมื่อลบ StatefulSet** (ค่า default) บล็อกเก็บกวาดจึงมี `kubectl delete pvc -l app=...` ด้วย ทำทุกครั้ง ไม่อย่างนั้น LAB ถัดไปจะได้ข้อมูลเก่าคืนมา
- image สาธารณะ `nginx:1.27-alpine`, `nginx:1.28-alpine` และ `busybox:1.36` **ให้ Node ดึงจาก Docker Hub เองตอนใช้** ไม่ต้อง `kind load` ส่วน `som-shop-web:1.2` ต้อง build เองและ `kind load` และ `postgres:17.11-alpine` ต้อง `docker save --platform` + `kind load image-archive` (LAB 0) ทั้งสองใช้เฉพาะ LAB 10
- Pod busybox ทุกตัวตั้ง `terminationGracePeriodSeconds: 1` (`sleep` ไม่รับ SIGTERM) ตอนลบจึงอาจเห็นสถานะ `Error` ชั่วครู่ ซึ่งปกติ
- `date` ใน Pod (nginx, busybox, postgres) เป็นเวลา **UTC** ช้ากว่าเวลาไทย 7 ชั่วโมง เช่น `first-born web-1 06:51:47` คือ 13:51:47 เวลาไทย ส่วน `date` ใน shell ของ k8s-lab เป็นเวลาไทย
- `nslookup` ของ busybox พิมพ์บรรทัด `** server can't find ...: NXDOMAIN` ของ search domain อื่นปนกับคำตอบจริง ให้ดูเฉพาะบรรทัด `Name:`/`Address:` และเวลาตรวจว่า Pod อยู่ใน DNS หรือไม่ **ให้ใช้ชื่อเต็ม** `web-1.web.default.svc.cluster.local` (LAB 2 อธิบายเหตุผล)
- **NodePort 30080 จองได้ทีละ Service ทั้งคลัสเตอร์** บทนี้ใช้ใน LAB 10 เท่านั้น
- **LAB 9 หยุด Node จริง** ต้อง `docker start` Node และเอา taint `out-of-service` ออกให้ครบ 3 Node `Ready` ก่อนทำ LAB 10 และ **ห้าม `kind load` ระหว่างที่ Node หยุด**
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง (ของจริงเก็บใน Secret ซึ่งเป็นเนื้อหาบทหลัง)
- **ขอบเขตของบทนี้:** ใช้ทุกอย่างของบทที่ 1–8 (Pod, ReplicaSet, Deployment, Service, PV, PVC, StorageClass) และ **StatefulSet, headless Service, volumeClaimTemplates, partition/OnDelete, taint `out-of-service`** ส่วน ConfigMap/Secret, Ingress, HPA, PodDisruptionBudget และ Operator เป็นแนวคิด/บทหลัง (LAB เสริมแก้ `pg_hba.conf` ด้วย `kubectl exec` แทน ConfigMap)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์และ image](#lab-0-เตรียมคลัสเตอร์และ-image) | 15–20 นาที | ⭐ |
| 1 | [Deployment เทียบ StatefulSet](#lab-1-deployment-เทียบ-statefulset) | 10 นาที | ⭐ |
| 2 | [headless Service และ DNS ต่อ Pod](#lab-2-headless-service-และ-dns-ต่อ-pod) | 15 นาที | ⭐⭐ |
| 3 | [volumeClaimTemplates: ตู้เซฟประจำบูธ](#lab-3-volumeclaimtemplates-ตู้เซฟประจำบูธ) | 10 นาที | ⭐⭐ |
| 4 | [ลำดับ: OrderedReady และ Parallel](#lab-4-ลำดับ-orderedready-และ-parallel) | 10 นาที | ⭐⭐ |
| 5 | [scale และ PVC retention](#lab-5-scale-และ-pvc-retention) | 10 นาที | ⭐⭐⭐ |
| 6 | [RollingUpdate, partition และ rollout undo](#lab-6-rollingupdate-partition-และ-rollout-undo) | 15 นาที | ⭐⭐⭐ |
| 7 | [minReadySeconds และ OnDelete](#lab-7-minreadyseconds-และ-ondelete) | 10 นาที | ⭐⭐⭐ |
| 8 | [ลบ StatefulSet แล้ว apply ใหม่](#lab-8-ลบ-statefulset-แล้ว-apply-ใหม่) | 10 นาที | ⭐⭐⭐ |
| 9 | [Node ล่ม: at most one และ out-of-service](#lab-9-node-ล่ม-at-most-one-และ-out-of-service) | 15 นาที | ⭐⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชัน db เป็น StatefulSet](#lab-10-lab-สุดท้าย-ร้านน้องส้มแบบโปรดักชัน-db-เป็น-statefulset) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (ถ้าต้อง build image ของร้านใน LAB 0 เพิ่มอีกราว 5–10 นาที) ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านหัวข้อทฤษฎีที่เกี่ยวข้อง: LAB 1 → หัวข้อ 2–3, LAB 2 → หัวข้อ 4, LAB 3 → หัวข้อ 5.1–5.2, LAB 4 → หัวข้อ 6, LAB 5 → หัวข้อ 5.3–5.4, LAB 6–7 → หัวข้อ 7, LAB 8 → หัวข้อ 5.3, LAB 9 → หัวข้อ 9, LAB 10 → หัวข้อ 8 และ 10

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมคลัสเตอร์และ image](#fig-1) | 15 | [LAB 10 ขั้น B ย้ายตู้เซฟ](#fig-15) |
| 2 | [LAB 1 Deployment เทียบ StatefulSet](#fig-2) | 16 | [LAB 10 ขั้น B2 web ชี้ som-db-0.som-db](#fig-16) |
| 3 | [LAB 2 headless Service และ DNS](#fig-3) | 17 | [LAB 10 ขั้น C ลบ som-db-0](#fig-17) |
| 4 | [LAB 3 volumeClaimTemplates](#fig-4) | 18 | [LAB 10 ขั้น D rolling update db](#fig-18) |
| 5 | [LAB 4 OrderedReady](#fig-5) | 19 | [ภาพหน้าจอจริง ร้านที่ db เป็น StatefulSet](#fig-19) |
| 6 | [LAB 4 Parallel และ scale down](#fig-6) | 20 | [LAB 10 ขั้น E ลบ StatefulSet](#fig-20) |
| 7 | [LAB 5 scale และ retention](#fig-7) | 21 | [ภาพหน้าจอจริง หลังลบ StatefulSet แล้ว apply ใหม่](#fig-21) |
| 8 | [LAB 6 partition](#fig-8) | 22 | [LAB 10 ขั้น F scale db เป็น 3](#fig-22) |
| 9 | [LAB 7 OnDelete](#fig-9) | 23 | [LAB 10 ขั้น G scale กลับ 1](#fig-23) |
| 10 | [LAB 8 ลบ StatefulSet แล้ว apply ใหม่](#fig-10) | 24 | [ภาพหน้าจอจริง สั่งซื้อหลัง scale](#fig-24) |
| 11 | [LAB 9 Node ล่ม](#fig-11) | 25 | [LAB 10 เสริม read replica](#fig-25) |
| 12 | [LAB 9 out-of-service](#fig-12) | 26 | [LAB 10 เสริม replica อ่านอย่างเดียว](#fig-26) |
| 13 | [LAB 10 ภาพรวม som-shop-v5](#fig-13) | 27 | [สรุป LAB สุดท้าย](#fig-27) |
| 14 | [LAB 10 ขั้น A เริ่มจากร้านบท 008](#fig-14) | | |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ 01–24 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
├── labs/                              ← YAML ของ LAB 1–9
│   ├── lab01-compare/{web-deploy,web-sts}.yaml          (Deployment web-d กับ StatefulSet web — nginx 3 ตัว)
│   ├── lab02-headless/{svc-headless,sts,dns-pod}.yaml   (headless Service web + StatefulSet web + Pod busybox dns)
│   ├── lab03-vct/sts.yaml                               (headless Service + StatefulSet web + vct www 10Mi — ใช้ต่อ LAB 4–8)
│   ├── lab04-order/{bad,par}.yaml                       (readiness ไม่ผ่าน / Parallel)
│   ├── lab05-retention/par.yaml                         (Parallel + whenScaled/whenDeleted: Delete + vct)
│   ├── lab06-update/{partition-2,partition-0}.yaml + show.sh   (ไฟล์ patch + สคริปต์ดู image/revision)
│   ├── lab07-ondelete/{min-ready,ondelete}.yaml         (ไฟล์ patch minReadySeconds / OnDelete)
│   └── lab09-node-down/sts-tol.yaml                     (web ของ LAB 3 + tolerationSeconds 30)
└── som-shop-v5/                       ← LAB 10 ร้านน้องส้มแบบโปรดักชัน
    ├── app/                           ← สำเนาแอป Next.js + Dockerfile จากบทที่ 8 (build เป็น som-shop-web:1.2)
    ├── k8s-008/{00-namespace,10-db,20-web}.yaml     ← สภาพท้ายบท 008: db Deployment + PVC som-db-data + Service ClusterIP
    ├── k8s/{00-namespace,10-db,20-web}.yaml         ← บทนี้: headless Service som-db + StatefulSet som-db (vct data) + web ชี้ som-db-0.som-db
    ├── migrate/data-som-db-0-pvc.yaml               ← ใบเบิก data-som-db-0 ที่ชี้ PV เดิม (volumeName: PVNAME)
    ├── extra/replica.yaml                           ← LAB เสริม: StatefulSet som-db-replica (pg_basebackup -R)
    └── hit.sh                         ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err
```

แอปร้านใน `som-shop-v5/app` เป็น **สำเนาเดียวกับบทที่ 8 โดยไม่แก้โค้ด** (ไม่ต้องสร้างรุ่นใหม่ ใช้ `som-shop-web:1.2` เดิม) หัวหน้าเว็บจึงยังเขียน "⚓ ท่าเรือ Kubernetes · ReplicaSet + Service" (ข้อความตั้งต้นของแอปตั้งแต่บทที่ 6) ส่วน footer ถูกตั้งจาก env ใน `k8s-008/20-web.yaml` และ `k8s/20-web.yaml` เป็น `Kubernetes LAB 009 · namespace som-shop`

---

## LAB 0: เตรียมคลัสเตอร์และ image

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมคลัสเตอร์และ image" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: 3 Node Ready, StorageClass standard, ไม่มี PV/PVC ค้างจากบท 008 (kubectl get pv ว่าง), image postgres:17.11-alpine และ som-shop-web:1.2 อยู่บนทุก Node (nginx/busybox ให้ Node ดึงเองตอนใช้)</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 8 หรือสร้างใหม่) ตรวจว่ามี StorageClass `standard` ไม่มี PV/PVC หรือ NodePort 30080 ค้าง และมี image `som-shop-web:1.2` กับ `postgres:17.11-alpine` อยู่บน Node สำหรับ LAB 10

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md)–[8](../../008_kubernetes_pv_pvc/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `009_kubernetes_statefulset` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `009_kubernetes_statefulset` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 009_kubernetes_statefulset k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ บทนี้มีสำเนาแอปร้านน้องส้มของตัวเอง (`02_LAB/som-shop-v5/app`) และสภาพร้านท้ายบทที่ 8 (`som-shop-v5/k8s-008/`) จึง **ไม่ต้องมีโฟลเดอร์ของบทที่ 8 ใน container** ก็ทำได้ครบ (การทดลองจริงคัดลอกเฉพาะโฟลเดอร์ของบทนี้)

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (ค่าตัวอย่างเพื่อการเรียน พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB
ls labs som-shop-v5
kubectl version | head -2; kubectl get nodes -o wide
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 8 ยังอยู่) | **ใช้ต่อได้เลย** ไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `k8s-up` image ที่เคย `kind load` ในบทก่อนจะหายไป ต้อง build/load ใหม่ในขั้นที่ 6 |

ผลจริงช่วงท้ายของ `k8s-up` บนคลัสเตอร์ใหม่

```text
[k8s-up] waiting for all nodes Ready (timeout 180s)...
node/lab-control-plane condition met
node/lab-worker condition met
node/lab-worker2 condition met
...
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
  ...
  k8s-down                                  # ลบคลัสเตอร์
  NodePort ที่ map ออก host: 30080 30081 30082
```

ผลจริงของ `kubectl version` และ `kubectl get nodes -o wide` (คอลัมน์ OS-IMAGE และ KERNEL-VERSION ขึ้นกับเครื่อง)

```text
Client Version: v1.37.1
Kustomize Version: v5.8.1
NAME                STATUS   ROLES           AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   5m53s   v1.37.0   172.19.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker          Ready    <none>          5m43s   v1.37.0   172.19.0.4    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker2         Ready    <none>          5m43s   v1.37.0   172.19.0.3    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
```

### ขั้นที่ 4: ตรวจของที่ค้างจากบทก่อน

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get ns
kubectl get sc
kubectl get pv,pvc -A
```

ผลจริงบนคลัสเตอร์ใหม่

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  5m49s
No resources found
```

ที่ถูกต้องคือ StorageClass `standard (default)` (local-path, `Delete`, `WaitForFirstConsumer` แบบบทที่ 8) และ **ไม่มี PV/PVC** ถ้ายังเห็นของค้างจากบทที่ 8 ให้จัดการดังนี้

| เห็นอะไร | ทำอย่างไร |
|---|---|
| namespace `som-shop` ของบทที่ 8 (จอง NodePort 30080) | แนะนำให้ลบ `kubectl delete ns som-shop` แล้วใช้สภาพท้ายบทที่ 8 จากไฟล์ `som-shop-v5/k8s-008/` ใน LAB 10 (เส้นทางที่ทดสอบแล้ว) |
| PV ที่ `Released` (Retain) หรือ StorageClass `standard-retain` จากบทที่ 8 | `kubectl delete pv <ชื่อ>` และ `kubectl delete sc standard-retain` แล้วลบโฟลเดอร์ของตู้บน Node เองตามตารางเก็บกวาดของบทที่ 8 (`docker exec <node> rm -rf /var/local-path-provisioner/<โฟลเดอร์>`) |

### ขั้นที่ 5: ตรวจ image ของร้านบน Node

LAB 10 ใช้ `som-shop-web:1.2` ที่ build เอง (ไม่มีใน Docker Hub) และ `postgres:17.11-alpine` ถ้าใช้คลัสเตอร์เดิมจากบทที่ 8 image เหล่านี้น่าจะยังอยู่ ตรวจด้วย `crictl` ภายใน Node

🐧 **ใน SSH session ของ k8s-lab**

```bash
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "postgres|som-shop-web"; done
```

ถ้าเห็นทั้ง `postgres 17.11-alpine` และ `som-shop-web 1.2` บนทั้งสอง worker **ข้ามไปขั้นที่ 7 ได้เลย** ถ้าไม่เห็น (คลัสเตอร์ใหม่) ให้ทำขั้นที่ 6

### ขั้นที่ 6: build และ load image (เฉพาะคลัสเตอร์ใหม่)

🐧 **ใน SSH session ของ k8s-lab** ทำในโฟลเดอร์แอปของบทนี้

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/som-shop-v5/app
```

**postgres** เป็น image หลาย platform จึงใช้ `docker save --platform` + `kind load image-archive` (ไฟล์ `pg.tar` ชั่วคราวถูกลบทิ้งท้ายบรรทัด ก่อน build จะได้ไม่ติดไปใน build context)

```bash
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o pg.tar && kind load image-archive pg.tar --name lab) 2>&1 | tail -6; rm -f pg.tar
```

```text
docker.io/library/postgres:17.11-alpine

real	0m17.217s
user	0m0.232s
sys	0m0.924s
```

**som-shop-web:1.2** build จาก **สำเนาแอปในบทนี้** แล้ว `kind load` ให้ทุก Node

```bash
time docker build -q --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 . 2>&1 | tail -3
time kind load docker-image som-shop-web:1.2 --name lab 2>&1 | tail -3
```

```text
sha256:6fea602559ffd167a32ba5234f4682c2f4e1c32b6965027e9369d8ddda2a57fc

real	0m29.128s
user	0m0.094s
sys	0m0.156s
Image: "som-shop-web:1.2" with ID "sha256:6fea602559ffd167a32ba5234f4682c2f4e1c32b6965027e9369d8ddda2a57fc" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.2" with ID "sha256:6fea602559ffd167a32ba5234f4682c2f4e1c32b6965027e9369d8ddda2a57fc" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.2" with ID "sha256:6fea602559ffd167a32ba5234f4682c2f4e1c32b6965027e9369d8ddda2a57fc" not yet present on node "lab-control-plane", loading...

real	0m5.012s
user	0m0.248s
sys	0m0.677s
```

ตรวจซ้ำด้วยคำสั่ง `crictl` ของขั้นที่ 5 ผลจริงหลัง load

```text
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  b781b4088880d       76.6MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  b781b4088880d       76.6MB
```

build ใช้ราว 30 วินาที (ดาวน์โหลด dependency และคอมไพล์ เครื่องนักศึกษาอาจนานกว่านี้หลายเท่า) ค่า sha256 และ IMAGE ID ในเครื่องนักศึกษาจะต่างจากตัวอย่าง

> **ข้อควรระวัง:** ทำขั้นนี้ **ตอนที่ Node ครบ 3 ตัวและ Ready** เท่านั้น อย่า `kind load` ระหว่างที่ Node ถูก `docker stop` ใน LAB 9 (บทที่ 8 พบ error `failed to detect containerd snapshotter`)

### ขั้นที่ 7: กลับโฟลเดอร์ LAB

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB
pwd
```

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node พร้อม StorageClass `standard (default)` = `rancher.io/local-path`, `Delete`, `WaitForFirstConsumer` และไม่มี PV/PVC ค้าง
- `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บนทั้งสอง worker ส่วน nginx และ busybox ยังไม่ต้องมี (Node ดึงเองครั้งแรกที่ใช้ LAB 1 จึงช้ากว่า LAB ถัดไปเล็กน้อย)

**คำถามชวนคิด**

1. ทำไม `nginx:1.27-alpine` จึงไม่ต้อง `kind load` แต่ `som-shop-web:1.2` ต้อง load (ดู `imagePullPolicy: IfNotPresent` ใน `k8s/20-web.yaml`)
2. StatefulSet ในบทนี้ส่วนใหญ่ไม่ใส่ `storageClassName` ใน `volumeClaimTemplates` จะได้ตู้จาก class ไหน และถ้าคลัสเตอร์ไม่มี default class จะเกิดอะไรกับ Pod `web-0` (ทวนบทที่ 8)

---

## LAB 1: Deployment เทียบ StatefulSet

<p align="center" id="fig-2">
  <img src="images/02-lab1-deploy-vs-sts.png" alt="รูปที่ 2 LAB 1 Deployment เทียบ StatefulSet" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: nginx 3 ตัวแบบ Deployment ได้ชื่อสุ่ม ลบแล้วชื่อใหม่; แบบ StatefulSet ได้ web-0/1/2 ลบ web-1 แล้วได้ web-1 คืน</em>
</p>

**เป้าหมาย:** รัน nginx 3 ตัวสองแบบพร้อมกัน เห็นความต่างของชื่อ ลำดับการเกิด hostname label อัตโนมัติ และผลของการลบ Pod

**ไฟล์:** `lab01-compare/web-deploy.yaml` — Deployment `web-d` (label `app: web-d`) 3 ตัว / `lab01-compare/web-sts.yaml` — StatefulSet `web` (label `app: web`) 3 ตัว มี `serviceName: web` (ยังไม่สร้าง Service — มาใน LAB 2) และ readinessProbe `httpGet /` ทุก 2 วินาที ทั้งสองใช้ `nginx:1.27-alpine` และ `terminationGracePeriodSeconds: 5`

```yaml
# LAB 1: แบบใหม่ — StatefulSet 3 ตัว (หัวหน้ากะแจกบัตรคิว -0 -1 -2: ชื่อคงที่)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  # ชื่อ headless Service ที่ใช้ทำ DNS รายตัว (สร้างจริงใน LAB 2 — LAB นี้ยังไม่มีก็สร้าง Pod ได้)
  serviceName: web
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      terminationGracePeriodSeconds: 5
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
          # Ready เมื่อเปิดหน้าเว็บได้ → StatefulSet รอตัวก่อนหน้า Ready ก่อนสร้างตัวถัดไป
          readinessProbe:
            httpGet:
              path: /
              port: 80
            periodSeconds: 2
```

เทียบกับ `web-deploy.yaml` ต่างกันที่ `kind: Deployment`, ชื่อ/label `web-d`, ไม่มี `serviceName` และไม่มี readinessProbe

### ขั้นที่ 1: apply ทั้งสองแบบแล้วดูลำดับการเกิด

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab01-compare
kubectl apply -f web-deploy.yaml -f web-sts.yaml
for i in $(seq 1 12); do echo "$(date +%T) $(kubectl get pod -l 'app in (web,web-d)' --no-headers | awk '{print $1":"$2}' | tr '\n' ' ')"; sleep 2; done
```

```text
deployment.apps/web-d created
statefulset.apps/web created
13:48:07 web-0:0/1 web-d-d8cf7b4b8-lgww5:0/1 web-d-d8cf7b4b8-pgrgg:0/1 web-d-d8cf7b4b8-vn6cv:0/1 
13:48:09 web-0:0/1 web-d-d8cf7b4b8-lgww5:0/1 web-d-d8cf7b4b8-pgrgg:0/1 web-d-d8cf7b4b8-vn6cv:0/1 
...
13:48:15 web-0:0/1 web-d-d8cf7b4b8-lgww5:1/1 web-d-d8cf7b4b8-pgrgg:1/1 web-d-d8cf7b4b8-vn6cv:0/1 
13:48:17 web-0:0/1 web-d-d8cf7b4b8-lgww5:1/1 web-d-d8cf7b4b8-pgrgg:1/1 web-d-d8cf7b4b8-vn6cv:1/1 
13:48:19 web-0:1/1 web-1:1/1 web-2:0/1 web-d-d8cf7b4b8-lgww5:1/1 web-d-d8cf7b4b8-pgrgg:1/1 web-d-d8cf7b4b8-vn6cv:1/1 
13:48:21 web-0:1/1 web-1:1/1 web-2:1/1 web-d-d8cf7b4b8-lgww5:1/1 web-d-d8cf7b4b8-pgrgg:1/1 web-d-d8cf7b4b8-vn6cv:1/1 
...
```

- Deployment สร้าง Pod **ทั้ง 3 ตัวพร้อมกัน** ชื่อ `web-d-d8cf7b4b8-<สุ่ม>` (`d8cf7b4b8` คือ pod-template-hash)
- StatefulSet สร้าง **`web-0` ตัวเดียวก่อน** รอจน Ready (ราว 12 วินาทีเพราะ Node ดึง image nginx ครั้งแรก) แล้ว `web-1` และ `web-2` จึงตามมาทีละตัว (เร็วเพราะ image อยู่แล้ว)

### ขั้นที่ 2: ดูชื่อ hostname และ label

```bash
kubectl rollout status sts/web --timeout=120s; kubectl rollout status deploy/web-d
kubectl get deploy,sts,pod -o wide
for p in $(kubectl get pod -l app=web-d -o name) web-0 web-1 web-2; do echo "$p hostname=$(kubectl exec ${p#pod/} -- hostname)"; done
kubectl get pod web-1 --show-labels
```

```text
partitioned roll out complete: 3 new pods have been updated...
deployment "web-d" successfully rolled out
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES              SELECTOR
deployment.apps/web-d   3/3     3            3           25s   nginx        nginx:1.27-alpine   app=web-d

NAME                   READY   AGE   CONTAINERS   IMAGES
statefulset.apps/web   3/3     25s   nginx        nginx:1.27-alpine

NAME                        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
pod/web-0                   1/1     Running   0          25s   10.244.2.4   lab-worker2   <none>           <none>
pod/web-1                   1/1     Running   0          15s   10.244.1.3   lab-worker    <none>           <none>
pod/web-2                   1/1     Running   0          14s   10.244.2.5   lab-worker2   <none>           <none>
pod/web-d-d8cf7b4b8-lgww5   1/1     Running   0          25s   10.244.2.2   lab-worker2   <none>           <none>
pod/web-d-d8cf7b4b8-pgrgg   1/1     Running   0          25s   10.244.1.2   lab-worker    <none>           <none>
pod/web-d-d8cf7b4b8-vn6cv   1/1     Running   0          25s   10.244.2.3   lab-worker2   <none>           <none>
pod/web-d-d8cf7b4b8-lgww5 hostname=web-d-d8cf7b4b8-lgww5
pod/web-d-d8cf7b4b8-pgrgg hostname=web-d-d8cf7b4b8-pgrgg
pod/web-d-d8cf7b4b8-vn6cv hostname=web-d-d8cf7b4b8-vn6cv
web-0 hostname=web-0
web-1 hostname=web-1
web-2 hostname=web-2
NAME    READY   STATUS    RESTARTS   AGE   LABELS
web-1   1/1     Running   0          15s   app=web,apps.kubernetes.io/pod-index=1,controller-revision-hash=web-8776b8748,statefulset.kubernetes.io/pod-name=web-1
```

- `kubectl rollout status sts/web` ของ StatefulSet ตอบ `partitioned roll out complete: 3 new pods have been updated...` (ข้อความแบบนี้ใช้กับ StatefulSet เสมอแม้ไม่ได้ตั้ง partition — partition default คือ 0)
- `kubectl get sts` มีแค่ `READY` และ `AGE` (ไม่มี `UP-TO-DATE`/`AVAILABLE` แบบ Deployment)
- hostname = ชื่อ Pod ทั้งสองแบบ แต่ของ StatefulSet **คาดเดาได้ล่วงหน้า**
- StatefulSet ใส่ label `apps.kubernetes.io/pod-index=1`, `controller-revision-hash=web-8776b8748` และ `statefulset.kubernetes.io/pod-name=web-1` ให้เอง

### ขั้นที่ 3: ลบ Pod หนึ่งตัวของแต่ละแบบ

```bash
kubectl get pod web-1 -o jsonpath='{.metadata.uid} {.status.podIP}{"\n"}'
D=$(kubectl get pod -l app=web-d -o jsonpath='{.items[0].metadata.name}'); echo "delete $D"; kubectl delete pod $D web-1
sleep 4; kubectl get pod -l 'app in (web,web-d)' -o wide
kubectl get pod web-1 -o jsonpath='{.metadata.uid} {.status.podIP}{"\n"}'
```

```text
3091ecf4-1c61-4db1-8920-d3f481758f13 10.244.1.3
delete web-d-d8cf7b4b8-lgww5
pod "web-d-d8cf7b4b8-lgww5" deleted from default namespace
pod "web-1" deleted from default namespace
NAME                    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
web-0                   1/1     Running   0          53s   10.244.2.4   lab-worker2   <none>           <none>
web-1                   1/1     Running   0          5s    10.244.1.5   lab-worker    <none>           <none>
web-2                   1/1     Running   0          42s   10.244.2.5   lab-worker2   <none>           <none>
web-d-d8cf7b4b8-d7zkr   1/1     Running   0          6s    10.244.1.4    lab-worker    <none>           <none>
web-d-d8cf7b4b8-pgrgg   1/1     Running   0          53s   10.244.1.2   lab-worker    <none>           <none>
web-d-d8cf7b4b8-vn6cv   1/1     Running   0          53s   10.244.2.3   lab-worker2   <none>           <none>
1e1cfe64-6d44-4508-b8cf-74949b801ef2 10.244.1.5
```

- Deployment: `web-d-d8cf7b4b8-lgww5` หายไป ได้ **ชื่อใหม่** `web-d-d8cf7b4b8-d7zkr` มาแทน
- StatefulSet: ได้ **`web-1` ชื่อเดิม** (AGE 5s) แต่ UID ใหม่ (`3091ecf4…` → `1e1cfe64…`) และ IP ใหม่ (`10.244.1.3` → `10.244.1.5`)

### ขั้นที่ 4: เก็บกวาด

```bash
kubectl delete -f web-deploy.yaml -f web-sts.yaml
```

```text
deployment.apps "web-d" deleted from default namespace
statefulset.apps "web" deleted from default namespace
```

### สิ่งที่เห็น

- Deployment: สร้างพร้อมกัน ชื่อสุ่ม ลบแล้วได้ชื่อใหม่
- StatefulSet: สร้างทีละตัวตามลำดับ `web-0 → web-1 → web-2` ชื่อคงที่ ลบแล้วได้ชื่อเดิม (UID/IP ใหม่) มี label อัตโนมัติ 3 ตัว
- StatefulSet ที่มี `serviceName` ชี้ Service ที่ยังไม่มีก็สร้าง Pod ได้

**คำถามชวนคิด**

1. ถ้าเอา readinessProbe ออกจาก `web-sts.yaml` คาดว่าเวลาห่างระหว่าง `web-0` กับ `web-1` จะเปลี่ยนไปอย่างไร (StatefulSet ใช้อะไรตัดสินว่า "พร้อม")
2. ถ้าแอปอื่นจำ IP `10.244.1.3` ของ `web-1` ไว้ หลังขั้นที่ 3 จะเกิดอะไร และ LAB 2 จะแก้ปัญหานี้อย่างไร

---

## LAB 2: headless Service และ DNS ต่อ Pod

<p align="center" id="fig-3">
  <img src="images/03-lab2-headless-dns.png" alt="รูปที่ 3 LAB 2 headless Service และ DNS" width="900"><br>
  <em><b>รูปที่ 3</b> LAB2: Service web clusterIP: None → nslookup web ได้ 3 Address, nslookup web-0.web.default.svc.cluster.local ได้ IP เดียว, wget web-1.web ได้หน้าของ web-1</em>
</p>

**เป้าหมาย:** สร้าง headless Service ให้ StatefulSet ถาม DNS จาก Pod เครื่องมือ (busybox) เห็นชื่อรายตัว และพิสูจน์ว่า **Pod ที่ไม่ Ready หายจาก DNS**

**ไฟล์:** `lab02-headless/svc-headless.yaml` — Service `web` `clusterIP: None` / `lab02-headless/sts.yaml` — StatefulSet `web` 3 ตัวที่เขียนหน้าเว็บ `first-born <hostname> <เวลา>` ใหม่ทุกครั้งที่เริ่ม (ไม่มี PVC) และมี readinessProbe / `lab02-headless/dns-pod.yaml` — Pod `dns` (busybox `sleep 3600`) สำหรับ `kubectl exec dns -- nslookup ...`

### ขั้นที่ 1: สร้าง headless Service และ StatefulSet

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab02-headless
kubectl apply -f svc-headless.yaml -f sts.yaml
kubectl rollout status sts/web --timeout=120s
kubectl get svc web; kubectl get pod -l app=web -o wide
kubectl get endpointslice -l kubernetes.io/service-name=web
```

```text
service/web created
statefulset.apps/web created
Waiting for 3 pods to be ready...
Waiting for 2 pods to be ready...
Waiting for 2 pods to be ready...
Waiting for 1 pods to be ready...
Waiting for 1 pods to be ready...
partitioned roll out complete: 3 new pods have been updated...
NAME   TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
web    ClusterIP   None         <none>        80/TCP    2s
NAME    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
web-0   1/1     Running   0          2s    10.244.2.6   lab-worker2   <none>           <none>
web-1   1/1     Running   0          1s    10.244.1.6   lab-worker    <none>           <none>
web-2   1/1     Running   0          1s    10.244.2.7   lab-worker2   <none>           <none>
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-jjj67   IPv4          80      10.244.2.6,10.244.1.6,10.244.2.7   2s
```

`CLUSTER-IP` เป็น **`None`** (headless) แต่ EndpointSlice ยังมี IP ของทั้ง 3 Pod รอบนี้ Pod เกิดเร็ว (1–2 วินาที) เพราะ image อยู่บน Node แล้ว

### ขั้นที่ 2: ถาม DNS จาก Pod busybox แบบโต้ตอบ

```bash
kubectl run dns --image=busybox:1.36 --rm -it --restart=Never -- sh
```

ถ้าไม่เห็น prompt `/ #` ให้กด Enter หนึ่งครั้ง (มีข้อความ `If you don't see a command prompt, try pressing enter.`) แล้วพิมพ์ทีละบรรทัดใน prompt ของ busybox

```bash
nslookup web
nslookup web-0.web.default.svc.cluster.local
wget -qO- web-1.web
exit
```

ผลจริง

```text
All commands and output from this session will be recorded in container logs, including credentials and sensitive information passed through the command prompt.
If you don't see a command prompt, try pressing enter.
/ # nslookup web
Server:		10.96.0.10
Address:	10.96.0.10:53


** server can't find web.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN

Name:	web.default.svc.cluster.local
Address: 10.244.1.6
Name:	web.default.svc.cluster.local
Address: 10.244.2.7
Name:	web.default.svc.cluster.local
Address: 10.244.2.6

** server can't find web.cluster.local: NXDOMAIN

/ # nslookup web-0.web.default.svc.cluster.local
Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web-0.web.default.svc.cluster.local
Address: 10.244.2.6

/ # wget -qO- web-1.web
first-born web-1 06:49:20
/ # exit
Session ended, resume using 'kubectl attach dns -c dns -n default -i -t' command
pod "dns" deleted from default namespace
```

- `nslookup web` ได้ **3 Address** = IP ของ Pod ทั้งสามตัว (ไม่ใช่ ClusterIP) ส่วนบรรทัด `** server can't find web.cluster.local: NXDOMAIN` คือ busybox ลองต่อท้ายชื่อด้วย search domain อื่นแล้วพิมพ์ผลที่ไม่เจอปนมา **ไม่ใช่ error** ให้ดูเฉพาะบรรทัด `Name: web.default.svc.cluster.local` และ `Address:`
- ชื่อรายตัว `web-0.web.default.svc.cluster.local` ได้ IP เดียวตรงกับ `web-0` (`10.244.2.6`)
- `wget -qO- web-1.web` (ชื่อย่อในตอนที่ Pod Ready) ได้หน้าของ `web-1` เท่านั้น
- `exit` แล้วมีข้อความ `Session ended, resume using 'kubectl attach …'` ตามด้วย `pod "dns" deleted` เพราะ `--rm` (ไม่ต้อง attach ต่อ)

> **ทางเลือก (ถ้า terminal ไม่รองรับโหมดโต้ตอบ):** ใช้ Pod `dns` จาก `dns-pod.yaml` แล้วสั่งผ่าน `kubectl exec` ทีละคำสั่งแบบขั้นที่ 3 และกรองบรรทัด NXDOMAIN ออกด้วย `grep -A1 "^Name"`

### ขั้นที่ 3: ทำให้ web-1 ไม่ Ready แล้วดู DNS

```bash
kubectl apply -f dns-pod.yaml; kubectl wait --for=condition=Ready pod/dns --timeout=60s
kubectl exec dns -- nslookup web 2>&1 | grep -A1 "^Name"
```

```text
pod/dns created
pod/dns condition met
Name:	web.default.svc.cluster.local
Address: 10.244.2.6
Name:	web.default.svc.cluster.local
Address: 10.244.2.7
Name:	web.default.svc.cluster.local
Address: 10.244.1.6
```

ลบหน้าเว็บของ `web-1` → nginx ตอบ 403 → readinessProbe ไม่ผ่าน

```bash
kubectl exec web-1 -- rm /usr/share/nginx/html/index.html
sleep 8; kubectl get pod -l app=web
kubectl get endpointslice -l kubernetes.io/service-name=web
kubectl exec dns -- nslookup web 2>&1 | grep -A1 "^Name"
kubectl exec dns -- nslookup web-1.web.default.svc.cluster.local; echo "exit=$?"
kubectl exec dns -- wget -qO- -T 3 web-1.web; echo "exit=$?"
kubectl describe pod web-1 | grep -E "Readiness probe failed" | tail -1
```

```text
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          76s
web-1   0/1     Running   0          75s
web-2   1/1     Running   0          75s
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-jjj67   IPv4          80      10.244.2.6,10.244.1.6,10.244.2.7   76s
Name:	web.default.svc.cluster.local
Address: 10.244.2.6
Name:	web.default.svc.cluster.local
Address: 10.244.2.7
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find web-1.web.default.svc.cluster.local: NXDOMAIN

** server can't find web-1.web.default.svc.cluster.local: NXDOMAIN

command terminated with exit code 1
exit=1
wget: can't connect to remote host (127.0.53.53): Connection refused
command terminated with exit code 1
exit=1
  Warning  Unhealthy  1s (x5 over 7s)  kubelet            spec.containers{nginx}: Readiness probe failed: HTTP probe failed with statuscode: 403
```

- `web-1` ยัง `Running` แต่ `0/1` (ไม่ Ready) เพราะ probe ได้ 403
- `nslookup web` เหลือ **2 Address** (ไม่มี `10.244.1.6`) และชื่อเต็ม `web-1.web.default.svc.cluster.local` เป็น **`NXDOMAIN`** (exit 1)
- คอลัมน์ ENDPOINTS ของ EndpointSlice ยังแสดง IP ครบ 3 ตัว เพราะ EndpointSlice เก็บทุก Pod แต่ระบุ `conditions.ready` แยก (ขั้นที่ 4 จะเห็น)

> **ข้อควรระวัง: ชื่อสั้นหลุดไป DNS ภายนอก** `wget -qO- -T 3 web-1.web` ได้ `can't connect to remote host (127.0.53.53): Connection refused` แทนที่จะบอกว่า "ไม่พบชื่อ" เพราะเมื่อชื่อในคลัสเตอร์ไม่มีคำตอบ resolver ลองชื่อ `web-1.web` ตรง ๆ ซึ่งออกไปถาม DNS บนอินเทอร์เน็ต และ **`.web` เป็นโดเมนระดับบนสุด (TLD) ที่มีอยู่จริง** ผลจึงขึ้นกับ DNS ภายนอก (เครื่องอื่นอาจได้ข้อความต่างไป) **เวลาตรวจว่า Pod อยู่ใน DNS ให้ใช้ชื่อเต็ม `<pod>.<svc>.<ns>.svc.cluster.local` เสมอ**

เขียนหน้าเว็บคืน → Ready → กลับเข้า DNS

```bash
kubectl exec web-1 -- sh -c 'echo "first-born web-1 (กลับมาแล้ว)" > /usr/share/nginx/html/index.html'
sleep 6; kubectl get pod web-1
kubectl exec dns -- nslookup web-1.web.default.svc.cluster.local 2>&1 | tail -3
kubectl exec dns -- wget -qO- web-1.web
```

```text
NAME    READY   STATUS    RESTARTS   AGE
web-1   1/1     Running   0          81s
Name:	web-1.web.default.svc.cluster.local
Address: 10.244.1.6

first-born web-1 (กลับมาแล้ว)
```

### ขั้นที่ 4: ดู conditions.ready ใน EndpointSlice

ทำซ้ำกับ `web-2` แล้วดู EndpointSlice แบบละเอียด และลองชื่อเต็มของ Pod ที่ไม่ Ready

```bash
kubectl exec web-2 -- rm /usr/share/nginx/html/index.html; sleep 6
kubectl get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[*].endpoints[*]}{.targetRef.name} {.addresses[0]} ready={.conditions.ready}{"\n"}{end}'
kubectl exec dns -- wget -qO- -T 3 web-2.web.default.svc.cluster.local; echo "exit=$?"
kubectl delete pod web-2; kubectl wait --for=condition=Ready pod/web-2 --timeout=60s
kubectl exec dns -- wget -qO- web-2.web
```

```text
web-0 10.244.2.6 ready=true
web-1 10.244.1.6 ready=true
web-2 10.244.2.7 ready=false
wget: bad address 'web-2.web.default.svc.cluster.local'
command terminated with exit code 1
exit=1
pod "web-2" deleted from default namespace
pod/web-2 condition met
first-born web-2 06:51:13
```

- EndpointSlice ระบุ `web-2 … ready=false` DNS ของ headless Service จึงไม่ใส่ `web-2`
- ชื่อเต็มของ Pod ที่ไม่ Ready ได้ `bad address` (ไม่พบชื่อ) ตามที่ควรเป็น
- ลบ `web-2` แล้ว Pod ใหม่เขียนหน้าเว็บใหม่ (`first-born web-2 06:51:13` เวลาใหม่) เพราะ StatefulSet ของ LAB นี้ **ยังไม่มี PVC** หน้าเว็บอยู่ในระบบไฟล์ของ container จึงหายไปกับ Pod เดิม LAB 3 จะแก้เรื่องนี้

### ขั้นที่ 5: เก็บกวาด

```bash
kubectl delete -f dns-pod.yaml -f sts.yaml -f svc-headless.yaml
```

```text
pod "dns" deleted from default namespace
statefulset.apps "web" deleted from default namespace
service "web" deleted from default namespace
```

### สิ่งที่เห็น

- headless Service `CLUSTER-IP None` → `nslookup web` ได้ IP ของทุก Pod ที่ Ready, `web-0.web.default.svc.cluster.local` ได้ IP เดียว
- Pod ที่ไม่ Ready (`0/1 Running`) หายจาก DNS ทั้งชื่อ Service และชื่อรายตัว แต่ยังอยู่ใน EndpointSlice ด้วย `ready=false`
- busybox พิมพ์ NXDOMAIN ของ search domain ปน และชื่อสั้น `web-1.web` ของ Pod ที่ไม่ Ready หลุดไปถาม DNS ภายนอก — ตรวจด้วยชื่อเต็ม
- StatefulSet ที่ไม่มี PVC: ชื่อคงที่ แต่ข้อมูลในตัว Pod หายเมื่อ Pod เกิดใหม่

**คำถามชวนคิด**

1. ถ้าแอปของน้องส้มต่อฐานข้อมูลด้วย `web` (ชื่อ Service) แทน `web-0.web` จะได้ Pod ไหน และต่างจาก Service ClusterIP ของบทที่ 6 อย่างไร
2. ระบบที่สมาชิกต้องคุยกันก่อนจะ Ready (เช่น cluster ที่เลือกผู้นำ) จะมีปัญหาอะไรกับพฤติกรรมของขั้นที่ 3 และ Service มีฟิลด์ใดช่วยได้ (ทฤษฎีหัวข้อ 4.3)

---

## LAB 3: volumeClaimTemplates: ตู้เซฟประจำบูธ

<p align="center" id="fig-4">
  <img src="images/04-lab3-volume-claim-templates.png" alt="รูปที่ 4 LAB 3 volumeClaimTemplates" width="900"><br>
  <em><b>รูปที่ 4</b> LAB3: PVC www-web-0/1/2 เกิดตามลำดับ แต่ละ Pod เขียน first-born &lt;ชื่อ&gt; ครั้งแรก — ลบ Pod แล้วไฟล์เดิมยังอยู่</em>
</p>

**เป้าหมาย:** ให้แต่ละ Pod มี PVC ของตัวเองจาก `volumeClaimTemplates` เห็นชื่อ PVC, ลำดับการเกิด, label และพิสูจน์ว่าลบ Pod แล้วได้ตู้ใบเดิม

**ไฟล์:** `lab03-vct/sts.yaml` — headless Service `web` + StatefulSet `web` 3 ตัว (nginx) mount PVC จากแม่แบบ `www` (10Mi, RWO, class default) ที่ `/usr/share/nginx/html` และเขียน `first-born $(hostname) $(date +%T)` **เฉพาะครั้งแรก** (ถ้ามีไฟล์ใน PVC แล้วไม่เขียนทับ) **StatefulSet นี้ใช้ต่อใน LAB 4–8 อย่าลบจนกว่าจะบอก**

```yaml
spec:
  template:
    spec:
      containers:
        - name: nginx
          volumeMounts:
            - name: www                    # ต้องตรงกับชื่อใน volumeClaimTemplates
              mountPath: /usr/share/nginx/html
  # สมุดใบเบิกตู้เซฟ: ฉีก 1 ใบต่อ 1 Pod (ไม่มี storageClassName = ใช้ default "standard")
  volumeClaimTemplates:
    - metadata:
        name: www
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 10Mi
```

(เฉพาะส่วนที่เกี่ยวกับตู้เซฟใน `spec` ของ StatefulSet — ดูไฟล์เต็มในทฤษฎีหัวข้อ 3.2)

### ขั้นที่ 1: apply แล้วดู Pod กับ PVC เกิดตามกัน

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab03-vct
kubectl apply -f sts.yaml
for i in $(seq 1 10); do echo "$(date +%T) pod: $(kubectl get pod -l app=web --no-headers | awk '{print $1":"$3}' | tr '\n' ' ') pvc: $(kubectl get pvc --no-headers 2>/dev/null | awk '{print $1":"$2}' | tr '\n' ' ')"; sleep 2; done
```

```text
service/web created
statefulset.apps/web created
13:51:38 pod: web-0:Pending  pvc: www-web-0:Pending 
13:51:40 pod: web-0:Pending  pvc: www-web-0:Pending 
13:51:42 pod: web-0:ContainerCreating  pvc: www-web-0:Bound 
13:51:44 pod: web-0:Running web-1:Pending  pvc: www-web-0:Bound www-web-1:Pending 
13:51:47 pod: web-0:Running web-1:Pending  pvc: www-web-0:Bound www-web-1:Bound 
13:51:49 pod: web-0:Running web-1:Running web-2:Pending  pvc: www-web-0:Bound www-web-1:Bound www-web-2:Pending 
13:51:51 pod: web-0:Running web-1:Running web-2:Pending  pvc: www-web-0:Bound www-web-1:Bound www-web-2:Bound 
13:51:53 pod: web-0:Running web-1:Running web-2:Running  pvc: www-web-0:Bound www-web-1:Bound www-web-2:Bound 
...
```

StatefulSet สร้าง PVC `www-web-0` พร้อม `web-0` PVC เป็น `Pending` (WaitForFirstConsumer แบบบทที่ 8) จนกว่า Pod ของตัวเองถูก schedule แล้วจึง `Bound` จากนั้นจึงถึงคิว `web-1` + `www-web-1` และ `web-2` + `www-web-2` ห่างกันราว 5 วินาที (เวลาสร้างตู้ + เวลา Ready)

### ขั้นที่ 2: ดูชื่อ ขนาด และ label ของ PVC

```bash
kubectl rollout status sts/web --timeout=120s
kubectl get pod -l app=web -o wide; kubectl get pvc
kubectl get pvc --show-labels
```

```text
partitioned roll out complete: 3 new pods have been updated...
NAME    READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
web-0   1/1     Running   0          21s   10.244.2.12   lab-worker2   <none>           <none>
web-1   1/1     Running   0          16s   10.244.1.8    lab-worker    <none>           <none>
web-2   1/1     Running   0          11s   10.244.2.14   lab-worker2   <none>           <none>
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 21s
www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 16s
www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 12s
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   LABELS
www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 21s   app=web
www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 16s   app=web
www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 12s   app=web
```

- ชื่อ PVC = `<ชื่อแม่แบบ>-<ชื่อ Pod>` = `www-web-0`, `www-web-1`, `www-web-2` (เหมือนกันทุกเครื่อง ต่างกันแค่ชื่อ PV)
- ทุกใบ `10Mi RWO standard` ตามแม่แบบ และได้ label **`app=web`** ตาม selector ของ StatefulSet
- AGE ของ PVC เท่ากับ AGE ของ Pod คู่กัน (21s/16s/12s)

### ขั้นที่ 3: อ่านไฟล์ในตู้ของแต่ละบูธ แล้วลบ Pod

```bash
for i in 0 1 2; do kubectl exec web-$i -- cat /usr/share/nginx/html/index.html; done
kubectl get pod web-1 -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}{"\n"}'
kubectl delete pod web-1; kubectl wait --for=condition=Ready pod/web-1 --timeout=60s
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
kubectl get pod web-1 -o wide
```

```text
first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
www-web-1
pod "web-1" deleted from default namespace
pod/web-1 condition met
first-born web-1 06:51:47
NAME    READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
web-1   1/1     Running   0          1s    10.244.1.9   lab-worker   <none>           <none>
```

- แต่ละบูธเขียนชื่อตัวเองลงตู้ของตัวเอง (เวลาเป็น UTC)
- StatefulSet ใส่ volume ที่อ้าง `claimName: www-web-1` ให้ Pod `web-1` เอง (ไม่ได้เขียน `volumes:` ใน template)
- ลบ `web-1` แล้ว Pod ใหม่ (IP ใหม่ `10.244.1.9`) อ่านได้ **`first-born web-1 06:51:47` เวลาเดิม** = ตู้ใบเดิม และกลับมาที่ Node เดิม (`lab-worker`) เพราะ PV ของ local-path ผูก Node (บทที่ 8)

**เก็บกวาด:** **ยังไม่ลบ** StatefulSet `web` และ PVC `www-web-*` เพราะใช้ต่อใน LAB 4–8 (ข้อความ `first-born …` ชุดนี้จะเป็นหลักฐานไปจนถึง LAB 9)

### สิ่งที่เห็น

- `volumeClaimTemplates` สร้าง PVC 1 ใบต่อ Pod ชื่อ `www-web-N` ตามลำดับเดียวกับ Pod และใส่ label ตาม selector
- ลบ Pod แล้ว Pod ชื่อเดิมกลับไปใช้ PVC เดิม ข้อมูลไม่หาย (ต่างจาก LAB 2 ที่ไม่มี PVC)

**คำถามชวนคิด**

1. ถ้าเปลี่ยนแม่แบบเป็น `storage: 20Mi` แล้ว apply ใหม่ คาดว่าจะเกิดอะไร (ทฤษฎีหัวข้อ 3.2: `volumeClaimTemplates` แก้ภายหลังได้หรือไม่) และ PVC ที่มีอยู่แล้วจะเปลี่ยนขนาดเองหรือไม่
2. ทำไม Pod `web-1` ตัวใหม่จึงต้องกลับไปลง `lab-worker` และถ้า `lab-worker` ล่มจะเกิดอะไร (จะได้ทดลองใน LAB 9)

---

## LAB 4: ลำดับ: OrderedReady และ Parallel

<p align="center" id="fig-5">
  <img src="images/05-lab4-ordered-ready.png" alt="รูปที่ 5 LAB 4 OrderedReady" width="900"><br>
  <em><b>รูปที่ 5</b> LAB4: StatefulSet bad ที่ readiness ไม่ผ่าน → ค้างที่ bad-0 ไม่สร้าง bad-1 จน touch /tmp/ready → bad-1 ตามมา</em>
</p>

**เป้าหมาย:** เห็นว่า OrderedReady รอ Pod ก่อนหน้า Ready จริง เทียบกับ Parallel ที่สร้าง/ลบพร้อมกัน และดูลำดับการ scale down ของ `web`

**ไฟล์:** `lab04-order/bad.yaml` — StatefulSet `bad` 3 ตัว (busybox `sleep 3600`) readinessProbe `cat /tmp/ready` (ไม่มีไฟล์ = ไม่ Ready) / `lab04-order/par.yaml` — StatefulSet `par` 3 ตัว `podManagementPolicy: Parallel` (ไม่มี PVC) ทั้งสองไม่มี headless Service ของตัวเอง (`serviceName: web` เพื่อเป็นตัวอย่างเท่านั้น และ selector `app: bad`/`app: par` ไม่ตรงกับ Service `web` จึงไม่ปนใน DNS)

### ขั้นที่ 1: OrderedReady ค้างที่ตัวแรก

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab04-order
kubectl apply -f bad.yaml
for i in $(seq 1 8); do echo "$(date +%T) $(kubectl get pod -l app=bad --no-headers | awk '{print $1":"$2":"$3}' | tr '\n' ' ')"; sleep 2; done
kubectl get sts bad
```

```text
statefulset.apps/bad created
13:52:25 bad-0:0/1:ContainerCreating 
13:52:27 bad-0:0/1:Running 
13:52:29 bad-0:0/1:Running 
...
13:52:39 bad-0:0/1:Running 
NAME   READY   AGE
bad    0/3     16s
```

`bad-0` เป็น `Running` แต่ `0/1` และ **ไม่มี `bad-1` เกิดขึ้นเลย** ตลอด 16 วินาที เพราะ OrderedReady รอให้ `bad-0` Ready ก่อน

### ขั้นที่ 2: ทำให้ bad-0 Ready แล้วดูตัวถัดไป

```bash
kubectl exec bad-0 -- touch /tmp/ready
for i in $(seq 1 8); do echo "$(date +%T) $(kubectl get pod -l app=bad --no-headers | awk '{print $1":"$2":"$3}' | tr '\n' ' ')"; sleep 2; done
kubectl exec bad-1 -- touch /tmp/ready
for i in $(seq 1 5); do echo "$(date +%T) $(kubectl get pod -l app=bad --no-headers | awk '{print $1":"$2":"$3}' | tr '\n' ' ')"; sleep 2; done
kubectl delete -f bad.yaml
```

```text
13:52:41 bad-0:0/1:Running 
13:52:43 bad-0:1/1:Running bad-1:0/1:ContainerCreating 
13:52:45 bad-0:1/1:Running bad-1:0/1:ContainerCreating 
13:52:47 bad-0:1/1:Running bad-1:0/1:ContainerCreating 
13:52:49 bad-0:1/1:Running bad-1:0/1:Running 
...
13:52:57 bad-0:1/1:Running bad-1:0/1:Running 
13:52:59 bad-0:1/1:Running bad-1:1/1:Running bad-2:0/1:Running 
...
statefulset.apps "bad" deleted from default namespace
```

ภายใน 2 วินาทีหลัง `touch` `bad-0` เป็น `1/1` และ `bad-1` ถูกสร้างทันที (`ContainerCreating` ครั้งแรกเพราะ Node ดึง busybox) `bad-1` ก็ค้าง `0/1` แบบเดียวกันจนกว่าจะ `touch` ในตัวมันแล้ว `bad-2` จึงเกิด (`bad-2` ไม่ได้ `touch` จึงยัง `0/1` ตอนลบ)

<p align="center" id="fig-6">
  <img src="images/06-lab4-parallel.png" alt="รูปที่ 6 LAB 4 Parallel และ scale down" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4 (ต่อ): podManagementPolicy: Parallel → par-0/1/2 เกิดพร้อมกัน; scale down OrderedReady ลบ web-2 ก่อน web-1</em>
</p>

### ขั้นที่ 3: Parallel สร้างและลบพร้อมกัน

```bash
kubectl apply -f par.yaml
for i in $(seq 1 5); do echo "$(date +%T) $(kubectl get pod -l app=par --no-headers | awk '{print $1":"$2":"$3}' | tr '\n' ' ')"; sleep 1; done
kubectl scale sts par --replicas=0
for i in $(seq 1 4); do echo "$(date +%T) $(kubectl get pod -l app=par --no-headers 2>&1 | awk '{print $1":"$3}' | tr '\n' ' ')"; sleep 1; done
kubectl delete -f par.yaml
```

```text
statefulset.apps/par created
13:53:28 par-0:0/1:Pending par-1:0/1:Pending par-2:0/1:Pending 
13:53:29 par-0:1/1:Running par-1:1/1:Running par-2:1/1:Running 
...
statefulset.apps/par scaled
13:53:34 par-0:Terminating par-1:Terminating par-2:Terminating 
13:53:35 par-0:Terminating par-1:Terminating par-2:Terminating 
13:53:36 par-0:Terminating par-1:Terminating par-2:Terminating 
13:53:37 par-1:Error par-2:Error 
statefulset.apps "par" deleted from default namespace
```

ทั้ง 3 ตัว `Pending` **ในวินาทีเดียวกัน** และ `Running` ใน 1 วินาที เมื่อ scale เป็น 0 ทั้งหมด `Terminating` พร้อมกัน (สถานะ `Error` ตอนท้ายคือ `sleep` ถูก kill เมื่อครบ `terminationGracePeriodSeconds: 1` ซึ่งปกติ)

### ขั้นที่ 4: scale down ของ web ไล่จากเลขมาก

ใช้ StatefulSet `web` จาก LAB 3 (OrderedReady)

```bash
kubectl scale sts web --replicas=1
for i in $(seq 1 10); do echo "$(date +%T) $(kubectl get pod -l app=web --no-headers | awk '{print $1":"$3}' | tr '\n' ' ')"; sleep 2; done
kubectl get pvc
```

```text
statefulset.apps/web scaled
13:53:38 web-0:Running web-1:Running web-2:Terminating 
13:53:40 web-0:Running web-1:Completed 
13:53:42 web-0:Running 
...
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 2m20s
www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 2m15s
www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 2m11s
```

- `web-2` ถูกปิดก่อนขณะที่ `web-1` ยัง Running จากนั้นจึงถึง `web-1` (เห็น `Completed` ชั่วครู่เพราะ nginx ปิดตัวเองเรียบร้อย) เหลือ `web-0` ภายในราว 4 วินาที
- **PVC ทั้ง 3 ใบยัง `Bound`** แม้ Pod เหลือตัวเดียว (LAB 5 ต่อจากตรงนี้)

**เก็บกวาด:** `bad` และ `par` ถูกลบในขั้นที่ 2–3 แล้ว (ไม่มี PVC) ส่วน `web` (replicas 1) เก็บไว้ใช้ใน LAB 5

### สิ่งที่เห็น

- OrderedReady: Pod ถัดไปเกิดเมื่อ Pod ก่อนหน้า **Ready** เท่านั้น probe ที่ไม่ผ่านทำให้ทั้งชุดค้าง
- Parallel: สร้างและลบพร้อมกันทั้งหมด ชื่อยังเป็น `par-0/1/2`
- scale down แบบ OrderedReady ไล่จาก ordinal มากไปน้อย และ PVC ไม่หายตาม

**คำถามชวนคิด**

1. ถ้าร้านน้องส้มมี StatefulSet ฐานข้อมูลที่ readinessProbe ผิด (เช่นต่อพอร์ตผิด) แล้ว scale จาก 1 เป็น 3 จะเห็นอะไร
2. งานแบบไหนเหมาะกับ Parallel และทำไมฐานข้อมูลแบบ primary/replica จึงควรใช้ OrderedReady

---

## LAB 5: scale และ PVC retention

<p align="center" id="fig-7">
  <img src="images/07-lab5-scale-retention.png" alt="รูปที่ 7 LAB 5 scale และ retention" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: scale 3→1 แล้ว PVC www-web-1/2 ยังอยู่ → scale กลับ web-2 อ่าน first-born web-2 เดิม; StatefulSet par ตั้ง whenScaled/whenDeleted: Delete → PVC หายตาม</em>
</p>

**เป้าหมาย:** ยืนยันว่าค่า default เก็บ PVC ไว้เมื่อ scale down และ scale กลับได้ข้อมูลเดิม แล้วเทียบกับ StatefulSet ที่ตั้ง `persistentVolumeClaimRetentionPolicy` เป็น `Delete`

**ไฟล์:** `lab05-retention/par.yaml` — StatefulSet `par` 3 ตัว Parallel + `whenScaled: Delete`, `whenDeleted: Delete` + vct `www` 10Mi (busybox เขียน `first-born …` ลง `/data/born.txt` ครั้งแรก)

### ขั้นที่ 1: ค่า default ของ web และ scale กลับเป็น 3

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab05-retention
kubectl get sts web -o jsonpath='{.spec.persistentVolumeClaimRetentionPolicy}{"\n"}'
kubectl get pod,pvc -l app=web
kubectl scale sts web --replicas=3; kubectl rollout status sts/web --timeout=120s
for i in 0 1 2; do kubectl exec web-$i -- cat /usr/share/nginx/html/index.html; done
```

```text
{"whenDeleted":"Retain","whenScaled":"Retain"}
NAME        READY   STATUS    RESTARTS   AGE
pod/web-0   1/1     Running   0          2m44s

NAME                              STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 2m44s
persistentvolumeclaim/www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 2m39s
persistentvolumeclaim/www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 2m35s
statefulset.apps/web scaled
Waiting for 2 pods to be ready...
Waiting for 1 pods to be ready...
Waiting for 1 pods to be ready...
partitioned roll out complete: 3 new pods have been updated...
first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
```

- ค่า default คือ `{"whenDeleted":"Retain","whenScaled":"Retain"}` (ไม่ได้เขียนในไฟล์ แต่ API server เติมให้)
- ตอนมี Pod ตัวเดียว PVC ยังอยู่ครบ 3 ใบ เมื่อ scale กลับ `web-1`, `web-2` ตัวใหม่ **อ่านไฟล์เวลาเดิม** (`06:51:47`, `06:51:52`)

### ขั้นที่ 2: StatefulSet ที่ตั้งให้ลบ PVC ตาม

```bash
kubectl apply -f par.yaml; kubectl rollout status sts/par --timeout=120s
kubectl get pvc
kubectl get pvc www-par-0 -o jsonpath='{.metadata.ownerReferences}{"\n"}'
kubectl get pvc www-web-0 -o jsonpath='ownerReferences ของ www-web-0 = [{.metadata.ownerReferences}]{"\n"}'
```

```text
statefulset.apps/par created
Waiting for statefulset spec update to be observed...
Waiting for 3 pods to be ready...
...
partitioned roll out complete: 3 new pods have been updated...
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
www-par-0   Bound    pvc-e6407d1f-a856-4a0f-9333-a1474cf64d28   10Mi       RWO            standard       <unset>                 8s
www-par-1   Bound    pvc-3f8085d3-eef7-42c4-ba03-6f23f15f2d39   10Mi       RWO            standard       <unset>                 8s
www-par-2   Bound    pvc-ebcbc35c-c5c4-4d2a-a65c-508b77a8b250   10Mi       RWO            standard       <unset>                 8s
www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 2m53s
www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 2m48s
www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 2m44s
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"StatefulSet","name":"par","uid":"cd299542-9199-436e-80aa-ed99d44b9a01"}]
ownerReferences ของ www-web-0 = []
```

- PVC ของ `par` เกิดพร้อมกันทั้ง 3 ใบ (AGE 8s เท่ากัน เพราะ Parallel)
- `www-par-0` มี **`ownerReferences` ชี้ไปที่ StatefulSet `par`** (`controller: true`) ส่วน `www-web-0` ว่าง (`[]`) นี่คือกลไกที่ทำให้ PVC ของ `par` ถูกลบตาม (garbage collection)

### ขั้นที่ 3: scale ลงและลบ StatefulSet par

```bash
kubectl scale sts par --replicas=1
sleep 8; kubectl get pod -l app=par; kubectl get pvc -l app=par
kubectl delete sts par
sleep 8; kubectl get pvc -l app=par; kubectl get pv | grep -c par
```

```text
statefulset.apps/par scaled
NAME    READY   STATUS    RESTARTS   AGE
par-0   1/1     Running   0          16s
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
www-par-0   Bound    pvc-e6407d1f-a856-4a0f-9333-a1474cf64d28   10Mi       RWO            standard       <unset>                 16s
statefulset.apps "par" deleted from default namespace
No resources found in default namespace.
0
```

- scale 3 → 1: PVC เหลือ `www-par-0` ใบเดียว (`whenScaled: Delete`)
- ลบ StatefulSet: PVC ของ `par` หมด (`whenDeleted: Delete`) และ **PV ที่เป็นของ `par` เหลือ 0** เพราะ class `standard` เป็น `Delete` (สองชั้นของ policy — ทฤษฎีหัวข้อ 5.4)

**เก็บกวาด:** `par` ถูกลบแล้วพร้อม PVC/PV ส่วน `web` (replicas 3) ใช้ต่อใน LAB 6

### สิ่งที่เห็น

- ค่า default `Retain/Retain`: scale ลงแล้ว PVC ยังอยู่ scale กลับได้ข้อมูลเดิม
- `whenScaled/whenDeleted: Delete`: PVC มี ownerReferences ถึง StatefulSet และถูกลบตาม PV (Delete) หายตามอีกชั้น

**คำถามชวนคิด**

1. ถ้าฐานข้อมูลของร้านตั้ง `whenScaled: Delete` แล้วมีคนเผลอ scale จาก 3 เป็น 1 แล้วกลับเป็น 3 ข้อมูลของ `som-db-1/2` จะเป็นอย่างไร
2. ถ้าต้องการให้ PVC ถูกลบตาม StatefulSet แต่ข้อมูลยังกู้ได้ ต้องตั้งค่าอะไรเพิ่มที่ชั้น PV/StorageClass (ทวนบทที่ 8)

---

## LAB 6: RollingUpdate, partition และ rollout undo

<p align="center" id="fig-8">
  <img src="images/08-lab6-partition.png" alt="รูปที่ 8 LAB 6 partition" width="900"><br>
  <em><b>รูปที่ 8</b> LAB6: partition 2 + nginx:1.28-alpine → เฉพาะ web-2 (updated=1) → partition 0 → web-1 แล้ว web-0 — rollout history มี 2 revision → rollout undo กลับ 1.27 (history เป็น 2, 3)</em>
</p>

**เป้าหมาย:** ทำ canary ด้วย partition เปลี่ยน `web` จาก `nginx:1.27-alpine` เป็น `nginx:1.28-alpine` เฉพาะ `web-2` ก่อน แล้วปล่อยครบ ดูลำดับ 2 → 1 → 0, ค่า `currentRevision`/`updateRevision`, `rollout history` และย้อนรุ่นด้วย `rollout undo`

**ไฟล์:** ใช้ StatefulSet `web` จาก LAB 3 และไฟล์ใน `lab06-update/`

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `partition-2.yaml` | patch `updateStrategy` เป็น RollingUpdate `partition: 2` (ใช้ `kubectl patch sts web --patch-file partition-2.yaml` เลี่ยงการพิมพ์ JSON ยาวในบรรทัดคำสั่ง) |
| `partition-0.yaml` | patch `partition: 0` เอาเชือกออก |
| `show.sh` | แสดง image, revision (`controller-revision-hash`), ready และเวลาสร้าง (`CREATED`) ของแต่ละ Pod + `currentRevision`/`updateRevision`/`updated` ของ StatefulSet ใช้ `./show.sh` ครั้งเดียว หรือ `watch -n2 ./show.sh` ดูต่อเนื่อง (Ctrl+C ออก) |

> ผลของ `show.sh` บางบล็อกด้านล่างมาจากรอบทดลองที่หัวคอลัมน์สุดท้ายยังชื่อ `AGE` (สคริปต์ถูกแก้ชื่อเป็น `CREATED` หลังรันครั้งแรก เพราะค่าที่แสดงคือเวลาสร้าง ไม่ใช่อายุ) ค่าข้างในเหมือนกัน

### ขั้นที่ 1: ดูค่าเริ่มต้นและตั้ง partition 2

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab06-update
kubectl get sts web -o jsonpath='{.spec.updateStrategy}{"\n"}'
./show.sh
```

```text
{"rollingUpdate":{"maxUnavailable":1,"partition":0},"type":"RollingUpdate"}
NAME    IMAGE               REVISION         READY   AGE
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:51:38Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
web-2   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
currentRevision=web-67f445dc6c  updateRevision=web-67f445dc6c  updated=3/3
```

ค่า default คือ RollingUpdate, `maxUnavailable: 1`, `partition: 0` ทุก Pod เป็น revision เดียวกัน (`web-0` สร้างตั้งแต่ LAB 3 ส่วน `web-1/2` สร้างใหม่ตอน scale กลับใน LAB 5)

### ขั้นที่ 2: เปลี่ยน image แล้วดู canary

```bash
kubectl patch sts web --patch-file partition-2.yaml
kubectl set image sts/web nginx=nginx:1.28-alpine
for i in $(seq 1 8); do echo "--- $(date +%T)"; ./show.sh | tail -4; sleep 3; done
kubectl rollout status sts/web --timeout=10s; echo "exit=$?"
```

```text
statefulset.apps/web patched
statefulset.apps/web image updated
--- 13:55:13
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:51:38Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
web-2   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
currentRevision=web-67f445dc6c  updateRevision=web-5888c97b8  updated=/3
--- 13:55:16
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:51:38Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
web-2   nginx:1.28-alpine   web-5888c97b8    false   2026-10-05T06:55:14Z
currentRevision=web-67f445dc6c  updateRevision=web-5888c97b8  updated=1/3
--- 13:55:22
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:51:38Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
web-2   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:55:14Z
currentRevision=web-67f445dc6c  updateRevision=web-5888c97b8  updated=1/3
...
--- 13:55:35
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:51:38Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
web-2   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:55:14Z
currentRevision=web-67f445dc6c  updateRevision=web-5888c97b8  updated=1/3
partitioned roll out complete: 1 new pods have been updated...
exit=0
```

- ทันทีหลัง `set image` เกิด revision ใหม่ `updateRevision=web-5888c97b8` แต่ยังไม่มี Pod ไหนเปลี่ยน (`updated=/3` = ยังไม่มีค่า)
- เฉพาะ **`web-2`** (ordinal ≥ 2) ถูกลบและสร้างใหม่เป็น `nginx:1.28-alpine` (Ready ใน ~8 วินาทีเพราะ Node ต้องดึง image 1.28) แล้ว **หยุดที่เชือก** `web-0`, `web-1` ยังเป็น 1.27 นานเท่าไรก็ได้
- **`kubectl rollout status` จบทันทีด้วย `partitioned roll out complete: 1 new pods have been updated...` (exit 0)** ทั้งที่อัปเดตไปตัวเดียว เพราะสำหรับ partition "ถึงเชือกแล้ว = เสร็จ" อย่าเข้าใจผิดว่าอัปเดตครบ

### ขั้นที่ 3: เอาเชือกออก ปล่อยที่เหลือ

```bash
kubectl patch sts web --patch-file partition-0.yaml
for i in $(seq 1 10); do echo "--- $(date +%T) $(kubectl get pod -l app=web --no-headers -o custom-columns=N:.metadata.name,I:.spec.containers[0].image,R:.status.containerStatuses[0].ready | tr -s ' ' | tr '\n' ' ')"; sleep 2; done
kubectl rollout status sts/web --timeout=60s
./show.sh
kubectl rollout history sts/web
for i in 0 1 2; do kubectl exec web-$i -- cat /usr/share/nginx/html/index.html; done
```

```text
statefulset.apps/web patched
--- 13:55:38 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.28-alpine true 
--- 13:55:40 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine false web-2 nginx:1.28-alpine true 
--- 13:55:42 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine false web-2 nginx:1.28-alpine true 
--- 13:55:44 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine false web-2 nginx:1.28-alpine true 
--- 13:55:46 web-0 nginx:1.27-alpine false web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true 
--- 13:55:48 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true 
...
partitioned roll out complete: 3 new pods have been updated...
NAME    IMAGE               REVISION        READY   AGE
web-0   nginx:1.28-alpine   web-5888c97b8   true    2026-10-05T06:55:46Z
web-1   nginx:1.28-alpine   web-5888c97b8   true    2026-10-05T06:55:38Z
web-2   nginx:1.28-alpine   web-5888c97b8   true    2026-10-05T06:55:14Z
currentRevision=web-5888c97b8  updateRevision=web-5888c97b8  updated=3/3
statefulset.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
```

- ลำดับ **`web-1` แล้ว `web-0`** (ordinal มากไปน้อย) ทีละตัว ตัวถัดไปเริ่มเมื่อตัวก่อนหน้า Ready (`web-0 … false` ที่ 13:55:46 คือ Pod ใหม่ของ `web-0` ที่เพิ่งถูกสร้าง)
- เวลาสร้าง (คอลัมน์สุดท้าย) เรียง `web-2` 06:55:14 → `web-1` 06:55:38 → `web-0` 06:55:46 และ `currentRevision` = `updateRevision` = `web-5888c97b8`
- `rollout history` มี REVISION 1, 2 และไฟล์ใน PVC เป็น `first-born` เวลาเดิมทุกตัว (เปลี่ยน image ไม่แตะตู้เซฟ)

### ขั้นที่ 4: rollout undo

```bash
kubectl rollout undo sts/web
for i in $(seq 1 8); do echo "--- $(date +%T) $(kubectl get pod -l app=web --no-headers -o custom-columns=N:.metadata.name,I:.spec.containers[0].image,R:.status.containerStatuses[0].ready | tr -s ' ' | tr '\n' ' ')"; sleep 2; done
kubectl rollout status sts/web --timeout=60s
./show.sh
kubectl rollout history sts/web
kubectl get controllerrevision -l app=web
for i in 0 1 2; do kubectl exec web-$i -- cat /usr/share/nginx/html/index.html; done
```

```text
Warning: resource statefulsets/web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
statefulset.apps/web rolled back
--- 13:56:41 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true 
--- 13:56:43 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine false web-2 nginx:1.27-alpine true 
--- 13:56:45 web-0 nginx:1.27-alpine false web-1 nginx:1.27-alpine true web-2 nginx:1.27-alpine true 
--- 13:56:47 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.27-alpine true 
...
partitioned roll out complete: 3 new pods have been updated...
NAME    IMAGE               REVISION         READY   CREATED
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:56:45Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:56:44Z
web-2   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:56:42Z
currentRevision=web-67f445dc6c  updateRevision=web-67f445dc6c  updated=3/3
statefulset.apps/web 
REVISION  CHANGE-CAUSE
2         <none>
3         <none>

NAME             CONTROLLER             REVISION   AGE
web-5888c97b8    statefulset.apps/web   2          105s
web-67f445dc6c   statefulset.apps/web   3          5m20s
first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
```

- undo ไล่ 2 → 1 → 0 เหมือน rolling update ปกติ ใช้ราว 6 วินาที (image 1.27 อยู่บน Node แล้ว)
- revision hash เดิม `web-67f445dc6c` (รุ่น 1) ถูกนำกลับมาใช้และ **เลื่อนเป็น REVISION 3** history จึงเหลือ `2, 3` และ ControllerRevision มี 2 ตัว
- **Warning** เตือนว่าค่าในคลัสเตอร์ไม่ตรงกับไฟล์ที่ apply ล่าสุดแล้ว (ถ้า apply `lab03-vct/sts.yaml` ใหม่จะกลับไปตามไฟล์ — LAB 8 ทำแบบนั้น) แนวปฏิบัติจริงคือแก้ไฟล์แล้ว apply
- partition ที่ patch ไว้ยังเป็น 0 (จากขั้นที่ 3)

**เก็บกวาด:** ไม่ต้อง `web` ใช้ต่อใน LAB 7 (ตอนนี้เป็น `nginx:1.27-alpine` ทุกตัว)

### สิ่งที่เห็น

- partition 2: เฉพาะ `web-2` เป็นรุ่นใหม่ (`updated=1/3`) `rollout status` จบที่เชือก
- partition 0: ปล่อยต่อ `web-1` → `web-0` ทีละตัว ลบก่อนสร้าง
- รุ่นเก็บเป็น ControllerRevision `rollout history/undo` ใช้ได้ undo แล้วรุ่นเดิมเลื่อนเลข และมี Warning last-applied

**คำถามชวนคิด**

1. ถ้าขณะ partition 2 มีคนลบ Pod `web-0` คาดว่า `web-0` ตัวใหม่จะเป็น image รุ่นไหน เพราะอะไร (ทฤษฎีหัวข้อ 7.2)
2. ถ้า `nginx:1.28-alpine` เป็น image ที่พัง (Pod ไม่เคย Ready) partition 2 ช่วยร้านได้อย่างไร และถ้าตั้ง partition 0 ตั้งแต่แรกจะเกิดอะไร (หัวข้อ 7.6)

---

## LAB 7: minReadySeconds และ OnDelete

<p align="center" id="fig-9">
  <img src="images/09-lab7-ondelete.png" alt="รูปที่ 9 LAB 7 OnDelete" width="900"><br>
  <em><b>รูปที่ 9</b> LAB7: OnDelete + set image กลับ 1.27 → ไม่มี Pod เปลี่ยน → ลบ web-1 → web-1 เป็น 1.27 คนเดียว; minReadySeconds ชะลอการเปลี่ยนแต่ละตัว</em>
</p>

**เป้าหมาย:** เห็นผลของ `minReadySeconds` ต่อจังหวะ rolling update แล้วเปลี่ยนเป็น OnDelete ที่ Pod ได้รุ่นใหม่เฉพาะเมื่อเราลบเอง

**ไฟล์:** `lab07-ondelete/min-ready.yaml` — patch `minReadySeconds: 10` / `lab07-ondelete/ondelete.yaml` — patch `minReadySeconds: 0` + `updateStrategy.type: OnDelete` + `rollingUpdate: null` (ลบค่า partition ทิ้ง เพราะใช้ได้เฉพาะ RollingUpdate) ใช้ `../lab06-update/show.sh` ดูผล

### ขั้นที่ 1: minReadySeconds 10 แล้ว rolling update

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab07-ondelete
kubectl patch sts web --patch-file min-ready.yaml
kubectl get sts web -o jsonpath='minReadySeconds={.spec.minReadySeconds}{"\n"}'
../lab06-update/show.sh | tail -1
kubectl set image sts/web nginx=nginx:1.28-alpine
for i in $(seq 1 25); do echo "--- $(date +%T) $(kubectl get pod -l app=web --no-headers -o custom-columns=N:.metadata.name,I:.spec.containers[0].image,R:.status.containerStatuses[0].ready | tr -s ' ' | tr '\n' ' ') | sts ready=$(kubectl get sts web -o jsonpath='{.status.readyReplicas} available={.status.availableReplicas}')"; sleep 2; done
kubectl rollout status sts/web --timeout=60s
```

```text
statefulset.apps/web patched
minReadySeconds=10
currentRevision=web-67f445dc6c  updateRevision=web-67f445dc6c  updated=3/3
statefulset.apps/web image updated
--- 13:57:20 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.27-alpine true  | sts ready=3 available=3
--- 13:57:22 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
...
--- 13:57:30 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
--- 13:57:32 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
...
--- 13:57:40 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
--- 13:57:42 web-0 nginx:1.28-alpine false web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=2 available=2
--- 13:57:45 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
...
--- 13:57:51 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
--- 13:57:53 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=3
...
partitioned roll out complete: 3 new pods have been updated...
```

- patch `minReadySeconds` อย่างเดียว **ไม่เกิด rollout** (`updated=3/3` เท่าเดิม) เพราะไม่ได้แก้ template
- หลัง `set image` Pod เปลี่ยน **ห่างกันราว 10–11 วินาที** (`web-2` 13:57:21, `web-1` 13:57:32, `web-0` 13:57:42) เทียบกับราว 2 วินาทีตอน `rollout undo` ใน LAB 6
- `ready=3` แต่ `available=2` ค้างราว 10 วินาทีหลังแต่ละตัว Ready = ช่วงที่ Pod ใหม่ยัง "Ready ไม่ครบ 10 วินาที"

### ขั้นที่ 2: เปลี่ยนเป็น OnDelete แล้วเปลี่ยน image

```bash
kubectl patch sts web --patch-file ondelete.yaml
kubectl get sts web -o jsonpath='{.spec.updateStrategy} minReadySeconds={.spec.minReadySeconds}{"\n"}'
kubectl set image sts/web nginx=nginx:1.27-alpine
sleep 10; ../lab06-update/show.sh
kubectl rollout status sts/web --timeout=10s; echo "exit=$?"
```

```text
statefulset.apps/web patched
{"type":"OnDelete"} minReadySeconds=
statefulset.apps/web image updated
NAME    IMAGE               REVISION        READY   CREATED
web-0   nginx:1.28-alpine   web-5888c97b8   true    2026-10-05T06:57:42Z
web-1   nginx:1.28-alpine   web-5888c97b8   true    2026-10-05T06:57:31Z
web-2   nginx:1.28-alpine   web-5888c97b8   true    2026-10-05T06:57:20Z
currentRevision=web-5888c97b8  updateRevision=web-67f445dc6c  updated=/3
error: rollout status is only available for RollingUpdate strategy type
exit=1
```

- `updateStrategy` เป็น `{"type":"OnDelete"}` (ไม่มี rollingUpdate แล้ว) และ `minReadySeconds=` ว่าง (= 0)
- ผ่านไป 10 วินาที **ไม่มี Pod ไหนเปลี่ยน** ทุกตัวยังเป็น 1.28 แม้ `updateRevision` จะเป็นรุ่น 1.27 แล้ว (`updated=/3`)
- **`kubectl rollout status` ใช้กับ OnDelete ไม่ได้** (`error: rollout status is only available for RollingUpdate strategy type` exit 1) ต้องดูด้วย `show.sh` แทน

### ขั้นที่ 3: ลบ Pod เองทีละตัว

```bash
kubectl delete pod web-1; kubectl wait --for=condition=Ready pod/web-1 --timeout=60s
../lab06-update/show.sh
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
kubectl delete pod web-0 web-2; sleep 3; kubectl wait --for=condition=Ready pod -l app=web --timeout=60s
../lab06-update/show.sh
```

```text
pod "web-1" deleted from default namespace
pod/web-1 condition met
NAME    IMAGE               REVISION         READY   CREATED
web-0   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:57:42Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:58:46Z
web-2   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:57:20Z
currentRevision=web-5888c97b8  updateRevision=web-67f445dc6c  updated=1/3
first-born web-1 06:51:47
pod "web-0" deleted from default namespace
pod "web-2" deleted from default namespace
pod/web-0 condition met
pod/web-1 condition met
pod/web-2 condition met
NAME    IMAGE               REVISION         READY   CREATED
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:58:48Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:58:46Z
web-2   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:58:48Z
currentRevision=web-67f445dc6c  updateRevision=web-67f445dc6c  updated=3/3
```

- ลบ `web-1` → **เฉพาะ `web-1`** ได้ 1.27 (`updated=1/3`) ไฟล์ในตู้ยังเป็น `first-born web-1 06:51:47`
- ลบ `web-0` และ `web-2` พร้อมกัน → ครบ 3/3 (OnDelete ไม่สนลำดับ เราเป็นคนเลือกเอง) และ `currentRevision` = `updateRevision` = `web-67f445dc6c` เมื่อทุก Pod เป็นรุ่นใหม่แล้ว

**เก็บกวาด:** ไม่ต้อง LAB 8 จะลบ StatefulSet แล้ว apply `lab03-vct/sts.yaml` ใหม่ ซึ่งคืนค่าทุกอย่างตามไฟล์ (RollingUpdate default, ไม่มี minReadySeconds)

### สิ่งที่เห็น

- `minReadySeconds: 10` ทำให้ rolling update หน่วงราว 10 วินาทีต่อ Pod และ `available` น้อยกว่า `ready` ระหว่างนั้น
- OnDelete: แก้ template แล้วไม่มีอะไรเปลี่ยน Pod ที่เราลบเท่านั้นได้รุ่นใหม่ `rollout status` ใช้ไม่ได้

**คำถามชวนคิด**

1. ฐานข้อมูลที่มี primary (`-0`) และ replica (`-1`, `-2`) ต้องอัปเกรด replica ก่อนแล้วจึง primary ควรใช้ RollingUpdate ธรรมดา, partition หรือ OnDelete ทำไม
2. `minReadySeconds` ช่วยอะไรได้ ถ้าแอปรุ่นใหม่ Ready แล้วพังหลังเปิดได้ 5 วินาที

---

## LAB 8: ลบ StatefulSet แล้ว apply ใหม่

<p align="center" id="fig-10">
  <img src="images/10-lab8-delete-reapply.png" alt="รูปที่ 10 LAB 8 ลบ StatefulSet แล้ว apply ใหม่" width="900"><br>
  <em><b>รูปที่ 10</b> LAB8: kubectl delete sts web → Pod หายหมด PVC 3 ใบยังอยู่ → apply ใหม่ → web-0/1/2 อ่าน first-born เดิมทุกตัว</em>
</p>

**เป้าหมาย:** ลบ StatefulSet ทั้งตัวแล้วพิสูจน์ว่าตู้เซฟยังรอเจ้าของ apply ใหม่แล้วได้ข้อมูลเดิม และลองลบแบบ `--cascade=orphan` (ลบหัวหน้ากะแต่ปล่อยบูธไว้)

**ไฟล์:** `lab03-vct/sts.yaml` (ไฟล์เดียวกับ LAB 3)

### ขั้นที่ 1: ลบ StatefulSet

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab03-vct
time kubectl delete sts web
for i in $(seq 1 6); do echo "$(date +%T) $(kubectl get pod -l app=web --no-headers 2>&1 | awk '{print $1":"$3}' | tr '\n' ' ')"; sleep 2; done
kubectl get pod,pvc
```

```text
statefulset.apps "web" deleted from default namespace

real	0m0.042s
user	0m0.032s
sys	0m0.022s
13:59:14 web-0:Terminating web-1:Terminating web-2:Terminating 
13:59:16 No:found 
13:59:18 No:found 
...
NAME                              STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 7m48s
persistentvolumeclaim/www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 7m43s
persistentvolumeclaim/www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 7m39s
```

- คำสั่งลบตอบกลับทันที (0.04 วินาที) Pod ทั้ง 3 ตัว `Terminating` **พร้อมกัน** (ลบทั้ง StatefulSet ไม่รับประกันลำดับ) และหายภายใน 2 วินาที (`No:found` คือ `No resources found` ที่ถูก awk ตัด)
- **PVC 3 ใบยัง `Bound`** (`whenDeleted: Retain`)

### ขั้นที่ 2: apply ใหม่ ได้ตู้เดิม

```bash
kubectl apply -f sts.yaml; kubectl rollout status sts/web --timeout=120s
for i in 0 1 2; do kubectl exec web-$i -- cat /usr/share/nginx/html/index.html; done
kubectl get pod -l app=web
```

```text
service/web unchanged
statefulset.apps/web created
Waiting for 3 pods to be ready...
...
partitioned roll out complete: 3 new pods have been updated...
first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          2s
web-1   1/1     Running   0          1s
web-2   1/1     Running   0          0s
```

`service/web unchanged` (Service ไม่ได้ถูกลบ) + `statefulset.apps/web created` (StatefulSet ใหม่) Pod ใหม่ทั้ง 3 ตัวรับ PVC ชื่อตรงกันไปใช้ ข้อความ `first-born` **เวลาเดิมครบทุกตัว**

### ขั้นที่ 3: ลบแบบ --cascade=orphan

```bash
kubectl delete sts web --cascade=orphan
sleep 3; kubectl get sts; kubectl get pod -l app=web
kubectl get pod web-0 -o jsonpath='ownerReferences=[{.metadata.ownerReferences}]{"\n"}'
kubectl delete pod web-2; sleep 5; kubectl get pod -l app=web
```

```text
statefulset.apps "web" deleted from default namespace
No resources found in default namespace.
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          6s
web-1   1/1     Running   0          5s
web-2   1/1     Running   0          4s
ownerReferences=[]
pod "web-2" deleted from default namespace
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          12s
web-1   1/1     Running   0          11s
```

- `kubectl get sts` ว่าง แต่ Pod 3 ตัวยัง Running = Pod **กำพร้า** (`ownerReferences=[]`)
- ลบ `web-2` ที่กำพร้าแล้ว **ไม่มีใครสร้างคืน** เหลือ `web-0`, `web-1`

### ขั้นที่ 4: apply ใหม่ รับ Pod เดิมกลับมาดูแล

```bash
kubectl apply -f sts.yaml; kubectl rollout status sts/web --timeout=120s
kubectl get pod -l app=web
kubectl get pod web-0 -o jsonpath='{.metadata.ownerReferences[0].kind}/{.metadata.ownerReferences[0].name}{"\n"}'
for i in 0 1 2; do kubectl exec web-$i -- cat /usr/share/nginx/html/index.html; done
```

```text
service/web unchanged
statefulset.apps/web created
Waiting for 1 pods to be ready...
Waiting for 1 pods to be ready...
partitioned roll out complete: 3 new pods have been updated...
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          12s
web-1   1/1     Running   0          11s
web-2   1/1     Running   0          0s
StatefulSet/web
first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
```

StatefulSet ใหม่ **รับ `web-0`, `web-1` เดิมกลับมา** (AGE ต่อเนื่อง 12s/11s ไม่ได้สร้างใหม่ และ ownerReferences เป็น `StatefulSet/web`) และสร้าง `web-2` ที่ขาด (AGE 0s) ซึ่งกลับไปใช้ `www-web-2` เดิม

**เก็บกวาด:** ไม่ต้อง `web` ใช้ต่อใน LAB 9

### สิ่งที่เห็น

- `kubectl delete sts`: Pod หายหมด (พร้อมกัน ไม่เรียงลำดับ) PVC อยู่ครบ apply ใหม่ได้ข้อมูลเดิม
- `--cascade=orphan`: เหลือ Pod กำพร้าที่ไม่มีใครดูแล apply ใหม่แล้ว StatefulSet รับกลับ (adopt) ตาม selector

**คำถามชวนคิด**

1. `--cascade=orphan` มีประโยชน์ตอนไหน (ใบ้: ต้องการแก้ฟิลด์ของ StatefulSet ที่แก้ทับไม่ได้ เช่น `volumeClaimTemplates` โดยไม่หยุด Pod)
2. ถ้าต้องการให้ Pod ปิดตามลำดับ 2 → 1 → 0 ก่อนลบ StatefulSet ควรสั่งอะไรก่อน

---

## LAB 9: Node ล่ม: at most one และ out-of-service

<p align="center" id="fig-11">
  <img src="images/11-lab9-node-down.png" alt="รูปที่ 11 LAB 9 Node ล่ม" width="900"><br>
  <em><b>รูปที่ 11</b> LAB9: docker stop Node ที่มี web-1 ($N ดูจาก kubectl get pod -o wide, tolerationSeconds 30) → NotReady 40–50 วิ → web-1 Terminating ~80 วิ แล้วค้าง ไม่มี web-1 ใหม่ (รอ 3 นาที ยังค้าง)</em>
</p>

**เป้าหมาย:** หยุด Node ที่ `web-1` อยู่จริง แล้วเห็นว่า StatefulSet **ไม่สร้าง `web-1` ตัวใหม่** (at most one) จนกว่าผู้ดูแลจะยืนยันว่า Node ดับด้วย taint `out-of-service` และเห็นว่าตู้ local-path ยังผูกกับ Node เดิม

**ไฟล์:** `lab09-node-down/sts-tol.yaml` — headless Service + StatefulSet `web` แบบเดียวกับ LAB 3 แต่เพิ่ม tolerations `node.kubernetes.io/unreachable` และ `node.kubernetes.io/not-ready` แบบ `NoExecute` `tolerationSeconds: 30` (ค่า default 300 วินาที) จะได้ไม่ต้องรอนาน

```yaml
      # Node NotReady/unreachable นานเกิน 30 วิ → ถูกสั่งไล่ (แต่ StatefulSet ยังไม่สร้างแทน จนกว่าจะยืนยันว่า Pod เก่าตายแล้ว)
      tolerations:
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
```

> **ข้อควรระวังก่อนเริ่ม:** LAB นี้หยุด Node จริง ระหว่างที่ Node หยุด **ห้าม `kind load`** และ **ห้าม `kubectl delete pod --force`** ทำขั้นที่ 5 (เอา taint ออก + `docker start`) ให้ครบเสมอก่อนไป LAB 10 ถ้าเปิด shell ใหม่ระหว่าง LAB ตัวแปร `$N` จะหายไป ให้ตั้งใหม่เป็นชื่อ Node ที่หยุด (`N=lab-worker` หรือ `N=lab-worker2` ตามที่เห็นในขั้นที่ 1)

### ขั้นที่ 1: apply tolerations ทับ web เดิม แล้วหา Node ของ web-1

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/labs/lab09-node-down
kubectl apply -f sts-tol.yaml; kubectl rollout status sts/web --timeout=120s
kubectl get pod -l app=web -o wide
kubectl get pod web-1 -o jsonpath='{.spec.tolerations}{"\n"}'
```

```text
service/web unchanged
statefulset.apps/web configured
Waiting for partitioned roll out to finish: 0 out of 3 new pods have been updated...
Waiting for 1 pods to be ready...
...
Waiting for partitioned roll out to finish: 2 out of 3 new pods have been updated...
...
partitioned roll out complete: 3 new pods have been updated...
NAME    READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
web-0   1/1     Running   0          0s    10.244.2.38   lab-worker2   <none>           <none>
web-1   1/1     Running   0          1s    10.244.1.21   lab-worker    <none>           <none>
web-2   1/1     Running   0          3s    10.244.2.37   lab-worker2   <none>           <none>
[{"effect":"NoExecute","key":"node.kubernetes.io/unreachable","operator":"Exists","tolerationSeconds":30},{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":30}]
```

`statefulset.apps/web configured` = tolerations อยู่ใน template จึงเกิด rolling update ทั้ง 3 ตัว (PVC เดิม) ดูคอลัมน์ NODE ว่า `web-1` อยู่ Node ไหน **รอบทดลองนี้คือ `lab-worker`** ของนักศึกษาอาจเป็น `lab-worker2` ขั้นถัดไปจึงดึงชื่อ Node ใส่ตัวแปร `N` แทนการพิมพ์เอง

### ขั้นที่ 2: หยุด Node แล้วเฝ้าดู 3 นาที

```bash
N=$(kubectl get pod web-1 -o jsonpath='{.spec.nodeName}'); echo "N=$N"; date +%T; docker stop $N; echo "stopped $(date +%T)"
for i in $(seq 1 20); do sleep 10; echo "--- $(date +%T) $N=$(kubectl get node $N --no-headers | awk '{print $2}')"; kubectl get pod -l app=web -o wide --no-headers | awk '{print $1,$2,$3,$7}'; done
```

```text
N=lab-worker
14:00:25
lab-worker
stopped 14:00:26
--- 14:00:36 lab-worker=Ready
web-0 1/1 Running lab-worker2
web-1 1/1 Running lab-worker
web-2 1/1 Running lab-worker2
...
--- 14:01:06 lab-worker=Ready
...
--- 14:01:16 lab-worker=NotReady
web-0 1/1 Running lab-worker2
web-1 1/1 Running lab-worker
web-2 1/1 Running lab-worker2
...
--- 14:01:46 lab-worker=NotReady
web-0 1/1 Running lab-worker2
web-1 1/1 Terminating lab-worker
web-2 1/1 Running lab-worker2
...
--- 14:03:47 lab-worker=NotReady
web-0 1/1 Running lab-worker2
web-1 1/1 Terminating lab-worker
web-2 1/1 Running lab-worker2
```

| เวลาหลัง `docker stop` | เหตุการณ์ (รอบทดลอง) |
|---|---|
| 0–40 วินาที | Node ยัง `Ready` (Node controller ยังรอ heartbeat) Pod ทุกตัวแสดง Running |
| ~40–50 วินาที | Node เป็น `NotReady` |
| ~80 วินาที | `web-1` เป็น `Terminating` (ครบ `tolerationSeconds: 30` หลัง taint unreachable + grace 5 วินาที) |
| 80 วินาที – 3 นาที 21 วินาที (จบการเฝ้าดู) | **`web-1` ค้าง `Terminating` ไม่มี `web-1` ตัวใหม่** |

ตัวเลขในเครื่องนักศึกษาอาจคลาดได้ราว ±10–20 วินาที ช่อง READY ของ `web-1` ยังแสดง `1/1` เพราะเป็นค่าล่าสุดที่ kubelet รายงานก่อนหายไป ตรวจสถานะจริง

```bash
kubectl get pod web-1 -o jsonpath='deletionTimestamp={.metadata.deletionTimestamp} Ready={.status.conditions[?(@.type=="Ready")].status}{"\n"}'
kubectl describe node $N | grep -A3 Taints
kubectl get sts web
```

```text
deletionTimestamp=2026-10-05T07:01:50Z Ready=False
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
NAME   READY   AGE
web    2/3     4m9s
```

- `web-1` มี `deletionTimestamp` (ถูกสั่งลบแล้ว) และ `Ready=False` แต่ยังไม่หาย เพราะ kubelet บน Node ที่หยุดไม่สามารถยืนยันว่า container ตายแล้ว
- StatefulSet `2/3` และ **ไม่สร้าง `web-1` ใหม่** (at most one: ห้ามมี `web-1` สองตัว) ต่างจาก Deployment ในบทที่ 8 LAB 8 ที่สร้าง Pod ชื่อใหม่ทันที
- Node มี taint `node.kubernetes.io/unreachable` ทั้ง `NoExecute` และ `NoSchedule`

<p align="center" id="fig-12">
  <img src="images/12-lab9-out-of-service.png" alt="รูปที่ 12 LAB 9 out-of-service" width="900"><br>
  <em><b>รูปที่ 12</b> LAB9 (ต่อ): taint out-of-service → web-1 ถูกลบและสร้างใหม่แต่ Pending (PV node affinity) → เอา taint ออก + docker start → web-1 Running อ่าน first-born web-1 เดิม</em>
</p>

### ขั้นที่ 3: ยืนยันว่า Node ดับด้วย taint out-of-service

สมมติว่าผู้ดูแลตรวจแล้วว่า "เรือลำนี้ดับจริง ไม่ได้แค่หลุดสัญญาณ" (ในห้องแล็บเรารู้เพราะเรา `docker stop` เอง)

```bash
echo "taint $(date +%T)"; kubectl taint node $N node.kubernetes.io/out-of-service=nodeshutdown:NoExecute
for i in $(seq 1 6); do sleep 5; echo "--- $(date +%T)"; kubectl get pod -l app=web -o wide --no-headers | awk '{print $1,$2,$3,$5,$7}'; done
```

```text
taint 14:04:11
node/lab-worker tainted
--- 14:04:16
web-0 1/1 Running 4m12s lab-worker2
web-1 1/1 Terminating 4m13s lab-worker
web-2 1/1 Running 4m15s lab-worker2
--- 14:04:21
web-0 1/1 Running 4m17s lab-worker2
web-1 1/1 Terminating 4m18s lab-worker
web-2 1/1 Running 4m20s lab-worker2
--- 14:04:26
web-0 1/1 Running 4m23s lab-worker2
web-1 0/1 Pending 2s <none>
web-2 1/1 Running 4m26s lab-worker2
...
--- 14:04:42
web-0 1/1 Running 4m38s lab-worker2
web-1 0/1 Pending 17s <none>
web-2 1/1 Running 4m41s lab-worker2
```

ภายในราว 15 วินาทีหลังใส่ taint `web-1` ตัวเก่าถูกลบจริง และ StatefulSet สร้าง `web-1` ตัวใหม่ทันที (AGE 2s) **แต่ค้าง `Pending`** ไม่มี Node (`<none>`) ดูเหตุผล

```bash
kubectl describe pod web-1 | grep -A3 "^Events" ; kubectl describe pod web-1 | grep FailedScheduling | tail -1
kubectl get pvc www-web-1; kubectl get pv $(kubectl get pvc www-web-1 -o jsonpath='{.spec.volumeName}') -o jsonpath='{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values}{"\n"}'
```

```text
Events:
  Type     Reason            Age                From               Message
  ----     ------            ----               ----               -------
  Warning  FailedScheduling  17s (x2 over 17s)  default-scheduler  0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
  Warning  FailedScheduling  17s (x2 over 17s)  default-scheduler  0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 12m
["lab-worker"]
```

- `1 node(s) didn't match PersistentVolume's node affinity` = `lab-worker2` ใช้ไม่ได้เพราะตู้ `www-web-1` อยู่บน `lab-worker` (PV `nodeAffinity` = `["lab-worker"]`)
- `2 node(s) had untolerated taint(s)` = `lab-worker` (taint unreachable/out-of-service) และ `lab-control-plane` (taint ของ control-plane)
- out-of-service แก้ปัญหา "StatefulSet ไม่กล้าสร้างแทน" ได้ แต่ **แก้ปัญหา "ตู้ติดเรือ" ไม่ได้** ถ้าใช้ storage เครือข่าย Pod ใหม่จะไปลง Node อื่นได้ทันที

### ขั้นที่ 4: เอา taint ออกและเปิด Node กลับมา

```bash
kubectl taint node $N node.kubernetes.io/out-of-service-; echo "start $(date +%T)"; docker start $N
kubectl wait --for=condition=Ready node/$N --timeout=180s; echo "node Ready $(date +%T)"
kubectl wait --for=condition=Ready pod/web-1 --timeout=180s; echo "web-1 Ready $(date +%T)"
kubectl get pod -l app=web -o wide
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
```

```text
node/lab-worker untainted
start 14:05:03
lab-worker
node/lab-worker condition met
node Ready 14:05:05
pod/web-1 condition met
web-1 Ready 14:05:07
NAME    READY   STATUS    RESTARTS   AGE    IP            NODE          NOMINATED NODE   READINESS GATES
web-0   1/1     Running   0          5m3s   10.244.2.38   lab-worker2   <none>           <none>
web-1   1/1     Running   0          42s    10.244.1.2    lab-worker    <none>           <none>
web-2   1/1     Running   0          5m6s   10.244.2.37   lab-worker2   <none>           <none>
first-born web-1 06:51:47
```

Node `Ready` ใน 2 วินาที `web-1` Ready บน `lab-worker` อีก 2 วินาที และอ่านได้ **`first-born web-1 06:51:47`** ข้อความเดิมตั้งแต่ LAB 3 (ข้อมูลรอดเพราะอยู่บนดิสก์ของ Node ที่แค่หยุด ไม่ได้เสีย)

### ขั้นที่ 5: ตรวจ Node และ image แล้วเก็บกวาด

```bash
kubectl get nodes
kubectl describe node $N | grep -A2 Taints
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "postgres|som-shop-web"; done
```

```text
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   24m   v1.37.0
lab-worker          Ready    <none>          24m   v1.37.0
lab-worker2         Ready    <none>          24m   v1.37.0
Taints:             <none>
Unschedulable:      false
Lease:
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  b781b4088880d       76.6MB
== lab-worker2
docker.io/library/som-shop-web                  1.2                  b781b4088880d       76.6MB
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
```

ต้องได้ 3 Node `Ready`, `Taints: <none>` และ image ของร้านยังอยู่ทั้งสอง worker (การหยุด/เปิด Node ไม่ลบ image) จากนั้นลบ StatefulSet `web` ที่ใช้มาตั้งแต่ LAB 3 พร้อมตู้ทั้งชุด

```bash
kubectl delete -f sts-tol.yaml
kubectl delete pvc -l app=web
sleep 5; kubectl get all,pvc; kubectl get pv
```

```text
service "web" deleted from default namespace
statefulset.apps "web" deleted from default namespace
persistentvolumeclaim "www-web-0" deleted from default namespace
persistentvolumeclaim "www-web-1" deleted from default namespace
persistentvolumeclaim "www-web-2" deleted from default namespace
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   25m
No resources found
```

`kubectl delete -f sts-tol.yaml` ลบ Service + StatefulSet แต่ **ไม่ลบ PVC** (default Retain) จึงต้อง `kubectl delete pvc -l app=web` (ใช้ label ที่ StatefulSet ใส่ให้ PVC) เมื่อ PVC หาย PV (class `standard` = Delete) หายตาม `kubectl get pv` จึงว่าง

### สิ่งที่เห็น

- Node หยุด → `NotReady` ~40–50 วินาที → `web-1` `Terminating` ~80 วินาที แล้วค้าง StatefulSet ไม่สร้างแทน (at most one) `sts web 2/3`
- taint `out-of-service` = ยืนยันว่า Node ดับ → Pod เดิมถูกลบ `web-1` ใหม่ถูกสร้าง แต่ `Pending` เพราะ PV ของ local-path ผูก Node
- Node กลับ → `web-1` กลับมาบน Node เดิมพร้อมข้อมูลเดิม

**คำถามชวนคิด**

1. ทำไม StatefulSet จึงเลือก "รอ" แทน "สร้าง `web-1` ใหม่บน `lab-worker2`" เหมือน Deployment ถ้าเป็นฐานข้อมูลและ Node แค่หลุดเครือข่าย การสร้างใหม่ทันทีจะเสี่ยงอะไร
2. ถ้าคลัสเตอร์ใช้ storage เครือข่าย (CSI) แทน local-path ผลของขั้นที่ 3 จะต่างไปอย่างไร และทำไมการใส่ taint `out-of-service` กับ Node ที่ยังทำงานอยู่จึงอันตราย

---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชัน db เป็น StatefulSet

**เป้าหมาย:** รับร้านน้องส้มต่อจากท้ายบทที่ 8 (db เป็น Deployment + PVC `som-db-data`) แล้ว **ย้ายตู้เซฟเดิม** ไปเป็น PVC `data-som-db-0` ของ StatefulSet `som-db` ที่มี headless Service ให้ web ต่อด้วยชื่อรายตัว `som-db-0.som-db` จากนั้นพิสูจน์ด้วย `/api/stats`, `psql` และหน้าร้านจริงใน browser ว่า **ลบ Pod db, rolling update db และลบ StatefulSet ทั้งตัวแล้ว apply ใหม่ ออเดอร์ไม่หาย** ดูความจริงว่า **scale db เป็น 3 ไม่ใช่การทำสำเนา** และ (เสริม) ทำ read replica จริงด้วย postgres streaming replication

**ต้องมีก่อน:** LAB 0 (image `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บน Node, NodePort 30080 ว่าง) และ **3 Node `Ready` ไม่มี taint** (ถ้าเพิ่งทำ LAB 9 ตรวจว่าเอา taint ออกและ `docker start` แล้ว)

### 10.1 สถาปัตยกรรมและไฟล์

<p align="center" id="fig-13">
  <img src="images/13-lab10-architecture.png" alt="รูปที่ 13 LAB 10 ภาพรวม som-shop-v5" width="900"><br>
  <em><b>รูปที่ 13</b> LAB10 ภาพรวม som-shop-v5: web Deployment 3 บูธ (NodePort 30080) → DATABASE_URL som-db-0.som-db → headless Service som-db → StatefulSet som-db → PVC data-som-db-0</em>
</p>

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)
   ▼                     ▼                     ▼
Pod som-web-<hash>-a  Pod som-web-<hash>-b  Pod som-web-<hash>-c   (Deployment som-web 3 บูธ — เหมือนบทที่ 8)
   │
   └──── DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop
                                   ▼  (DNS รายตัวของ headless Service)
                    Service som-db (clusterIP: None, port postgres 5432)
                                   ▼
                    Pod som-db-0 (StatefulSet som-db, replicas 1, serviceName som-db)
                                   │ volumeClaimTemplates "data" → /var/lib/postgresql/data (PGDATA …/pgdata)
                                   ▼
                    PVC data-som-db-0 (standard, RWO, 1Gi) ══ PV เดิมจากบทที่ 8 (ย้ายในขั้น B)
```

**ตารางที่ 10.1** ไฟล์ใน `som-shop-v5/`

| ไฟล์ | เนื้อหา |
|---|---|
| `k8s-008/00-namespace.yaml` | namespace `som-shop` (label `pod-security.kubernetes.io/warn: restricted`) |
| `k8s-008/10-db.yaml` | **สภาพท้ายบท 008:** PVC `som-db-data` (standard, RWO, 1Gi) + Deployment `som-db` (replicas 1, `Recreate`) + Service `som-db` แบบ **ClusterIP** |
| `k8s-008/20-web.yaml` | **สภาพท้ายบท 008:** Deployment `som-web` 3 บูธ ต่อ db ด้วย `som-db` + Service NodePort `som-web` 30080 (change-cause `1.2 ร้านจำได้ (db ใช้ PVC)`) |
| `k8s/00-namespace.yaml` | เหมือน `k8s-008/00-namespace.yaml` (ทำให้ `kubectl apply -f k8s/` สร้างร้านใหม่ทั้งร้านได้) |
| `k8s/10-db.yaml` | **บทนี้:** headless Service `som-db` (`clusterIP: None`, port `postgres` 5432) + StatefulSet `som-db` (`serviceName: som-db`, replicas 1, template postgres เดิม, `volumeClaimTemplates: data` standard RWO 1Gi) |
| `k8s/20-web.yaml` | **บทนี้:** เหมือน `k8s-008/20-web.yaml` แต่ `wait-for-db`, `db-seed`, `web` ต่อ **`som-db-0.som-db`** (change-cause `1.2 db เป็น StatefulSet (som-db-0.som-db)`) |
| `migrate/data-som-db-0-pvc.yaml` | PVC `data-som-db-0` (label `app: som-db`, `volumeName: PVNAME`) — ขั้น B แทนชื่อ PV ด้วย `sed` |
| `extra/replica.yaml` | LAB เสริม: StatefulSet `som-db-replica` (init `clone-from-primary` ใช้ `pg_basebackup -R`) |
| `hit.sh` | ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err |

> **ข้อควรระวัง:** **ห้าม `kubectl apply -f migrate/`** ตรง ๆ เพราะไฟล์ยังมีคำว่า `PVNAME` ใช้คำสั่ง `sed` ของขั้น B เท่านั้น และ **ห้าม apply `k8s-008/` กับ `k8s/` ปนกัน** (Service `som-db` คนละแบบ)

ต่างจากบทที่ 8 ตรงไหน (`k8s/10-db.yaml`)

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: som-db
  namespace: som-shop
  labels:
    app: som-db
spec:
  serviceName: som-db              # ต้องตรงกับชื่อ headless Service ด้านบน → ได้ DNS som-db-0.som-db
  # replicas 1 = postgres ตัวเดียวที่รับเขียน (scale 3 = db 3 ตัว "ข้อมูลแยกกัน" ไม่ใช่ replication — ดูขั้น F)
  replicas: 1
  # ...template เดิมของบทที่ 8 แต่ไม่มี volumes: (ได้ PVC จาก volumeClaimTemplates)...
  selector:
    matchLabels:
      app: som-db
  template:
    metadata:
      labels:
        app: som-db
    spec:
      containers:
        - name: postgres
          image: postgres:17.11-alpine
          volumeMounts:
            - name: data             # = ชื่อใน volumeClaimTemplates
              mountPath: /var/lib/postgresql/data
  # สมุดใบเบิกตู้เซฟ: Pod som-db-N ได้ PVC data-som-db-N (ลบ Pod/ลบ StatefulSet แล้ว PVC ยังอยู่)
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        storageClassName: standard
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 1Gi
```

(ตัดให้สั้น — ไฟล์จริงมี securityContext, env `POSTGRES_*`/`PGDATA`, probes และ resources ครบเหมือนบทที่ 8) ข้อสังเกต: **ไม่มี `strategy: Recreate`** แล้ว เพราะ StatefulSet ใช้ `updateStrategy` (default RollingUpdate ที่ลบตัวเก่าก่อนสร้างตัวใหม่ชื่อเดิม จึงไม่มี postgres สองตัวบนตู้เดียว)

**มีร้านของบทที่ 8 ค้างอยู่หรือไม่**

| สภาพคลัสเตอร์ | เริ่มที่ |
|---|---|
| ไม่มี namespace `som-shop` (ทำเก็บกวาดบทที่ 8 แล้ว หรือคลัสเตอร์ใหม่) — **เส้นทางที่ทดสอบแล้ว** | ขั้น A ด้วย `k8s-008/` (สร้างสภาพท้ายบทที่ 8 ขึ้นมาใหม่) |
| ยังมีร้านของบทที่ 8 ที่ใช้ `som-shop-v4/k8s/` (PVC `som-db-data` class `standard` RWO) | ลบแล้วเริ่มขั้น A ใหม่จะได้ผลตรงเอกสารที่สุด ถ้าจะใช้ร้านเดิมต่อ ข้ามไปขั้น B ได้ (ขั้นตอนเหมือนกัน — PVC ชื่อและ class เดียวกัน) |
| ร้านของบทที่ 8 ใช้ `k8s-retain/` (class `standard-retain`, `ReadWriteOncePod`) | **ลบ namespace และ PV/StorageClass ที่ค้างก่อน** (`migrate/data-som-db-0-pvc.yaml` ใช้ `standard` + RWO จึงจับคู่ PV แบบนั้นไม่ได้) แล้วเริ่มขั้น A |
| ไม่ต้องการทำขั้นย้ายข้อมูล | ทางเลือก: `kubectl apply -f k8s/` สร้างร้านใหม่ที่ db เป็น StatefulSet ทันที (PVC มาจาก vct — ทดสอบแล้วในรอบถ่ายภาพหน้าจอ) แล้วเริ่มที่ขั้น C (ตัวเลขออเดอร์จะเริ่มจาก 0) |

### 10.2 ขั้น A: เริ่มจากร้านท้ายบท 008

<p align="center" id="fig-14">
  <img src="images/14-lab10-start-008.png" alt="รูปที่ 14 LAB 10 ขั้น A เริ่มจากร้านบท 008" width="900"><br>
  <em><b>รูปที่ 14</b> LAB10 ขั้น A: เริ่มจากสภาพท้ายบท 008 (db Deployment + PVC som-db-data) สั่งซื้อ 3 ครั้ง → orders=3</em>
</p>

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/009_kubernetes_statefulset/02_LAB/som-shop-v5
kubectl apply -f k8s-008/
time kubectl -n som-shop rollout status deploy/som-db --timeout=180s
time kubectl -n som-shop rollout status deploy/som-web --timeout=180s
```

```text
namespace/som-shop created
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db created
deployment.apps/som-web created
service/som-web created
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out

real	0m6.922s
...
Waiting for deployment "som-web" rollout to finish: 0 of 3 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m10.240s
```

สั่งซื้อ 3 ครั้งด้วย API (`/api/orders`) แล้วดูสถิติ (`/api/stats` ตอบ `<ชื่อ Pod web> <รุ่น> orders=<จำนวน> products=<จำนวน>`)

```bash
for p in 1 2 3; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done
for i in 1 2 3; do curl -s localhost:30080/api/stats; done
kubectl -n som-shop get deploy,pod,svc,pvc -o wide
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":14}}
{"ok":true,"order_id":3,"product":{"id":3,"name_th":"อาหารเม็ดแมวสูงวัย 1.2 กก.","stock":9}}
som-web-64fdf9cf64-hkd98 1.2 orders=3 products=6
som-web-64fdf9cf64-cx84w 1.2 orders=3 products=6
som-web-64fdf9cf64-cx84w 1.2 orders=3 products=6
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                  SELECTOR
deployment.apps/som-db    1/1     1            1           18s   postgres     postgres:17.11-alpine   app=som-db
deployment.apps/som-web   3/3     3            3           18s   web          som-shop-web:1.2        app=som-web

NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-7b786655f5-bdsgq    1/1     Running   0          18s   10.244.2.44   lab-worker2   <none>           <none>
pod/som-web-64fdf9cf64-5xhqn   1/1     Running   0          18s   10.244.1.4    lab-worker    <none>           <none>
pod/som-web-64fdf9cf64-cx84w   1/1     Running   0          18s   10.244.2.42   lab-worker2   <none>           <none>
pod/som-web-64fdf9cf64-hkd98   1/1     Running   0          18s   10.244.2.43   lab-worker2   <none>           <none>

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/som-db    ClusterIP   10.96.99.37    <none>        5432/TCP       18s   app=som-db
service/som-web   NodePort    10.96.119.79   <none>        80:30080/TCP   18s   app=som-web

NAME                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   VOLUMEMODE
persistentvolumeclaim/som-db-data   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 18s   Filesystem
```

นี่คือร้านแบบเดียวกับท้ายบทที่ 8: Pod db ชื่อสุ่ม `som-db-7b786655f5-bdsgq`, Service `som-db` แบบ **ClusterIP** (`10.96.99.37`) และ PVC `som-db-data` ที่มีออเดอร์ 3 รายการ 🌐 เปิด `http://localhost:30080` บน browser จะเห็นการ์ด "ออเดอร์ทั้งหมด" เป็น 3

### 10.3 ขั้น B: ย้ายตู้เซฟไปเป็น data-som-db-0

<p align="center" id="fig-15">
  <img src="images/15-lab10-migrate.png" alt="รูปที่ 15 LAB 10 ขั้น B ย้ายตู้เซฟ" width="900"><br>
  <em><b>รูปที่ 15</b> LAB10 ขั้น B: PV → Retain, ลบ Deployment/Service/PVC เดิม, ลบ claimRef, สร้าง PVC data-som-db-0 (volumeName) แล้ว apply StatefulSet → som-db-0 ผูก PV เดิม</em>
</p>

**B-1 ดู error ก่อน (ไม่เปลี่ยนอะไรในคลัสเตอร์)** ถ้า apply `k8s/10-db.yaml` ทั้งที่ Service ClusterIP เดิมยังอยู่จะเกิดอะไร ใช้ `--dry-run=server` ให้ API server ตรวจจริงแต่ไม่บันทึก

```bash
kubectl apply -f k8s/10-db.yaml --dry-run=server; echo "exit=$?"
kubectl -n som-shop get svc som-db -o jsonpath='clusterIP={.spec.clusterIP}{"\n"}'
```

```text
statefulset.apps/som-db created (server dry run)
The Service "som-db" is invalid: spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set
exit=1
clusterIP=10.96.99.37
```

- Service ล้มด้วย **`spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set`** เพราะ ClusterIP ของ Service เดิม (`10.96.99.37`) แก้ไขหลังสร้างไม่ได้ ต้องลบ Service เดิมก่อน
- แต่ส่วน StatefulSet **ผ่าน** (`created (server dry run)`) ถ้าสั่ง apply จริงตอนนี้ StatefulSet จะถูกสร้างและสร้าง PVC `data-som-db-0` **เปล่า** จากแม่แบบแย่งชื่อไปก่อน ทำให้ย้ายข้อมูลเดิมเข้าไปไม่ได้ (ถ้าเผลอทำ ดู Troubleshooting) **จึงห้าม apply จริงในขั้นนี้**

**B-2 กันตู้ไม่ให้ถูกบดทิ้ง** PV จาก class `standard` เป็น `Delete` ถ้าลบ PVC ตอนนี้ข้อมูลจะหาย เปลี่ยนเป็น `Retain` ก่อน (บทที่ 8 LAB 6)

```bash
PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}'); echo "PV=$PV"
kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

```text
PV=pvc-6c88d7af-5c52-48b1-aa08-044104105355
persistentvolume/pvc-6c88d7af-5c52-48b1-aa08-044104105355 patched
```

**B-3 ปิดครัวเดิมและคืนใบเบิกเดิม** ลบ Deployment db, Service ClusterIP และ PVC เดิม (web ยังรันอยู่ จะตอบ 503 ช่วงสั้น ๆ ระหว่างที่ไม่มี db)

```bash
kubectl -n som-shop delete deploy som-db
kubectl -n som-shop delete svc som-db
kubectl -n som-shop delete pvc som-db-data
kubectl get pv $PV
```

```text
deployment.apps "som-db" deleted from som-shop namespace
service "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            Retain           Released   som-shop/som-db-data   standard       <unset>                          87s
```

PV เป็น `Retain` + `Released` และ CLAIM ยังจำ `som-shop/som-db-data` ไว้ (ข้อมูลยังอยู่บน Node)

**B-4 ปลดกุญแจเดิมแล้วเขียนใบเบิกชื่อใหม่** ลบ `claimRef` ให้ PV เป็น `Available` แล้วสร้าง PVC **`data-som-db-0`** ที่ชี้ PV นี้โดยตรง (`sed` แทน `PVNAME` ด้วยชื่อ PV จริง)

```bash
kubectl patch pv $PV --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'
kubectl get pv $PV
sed "s/PVNAME/$PV/" migrate/data-som-db-0-pvc.yaml | kubectl apply -f -
```

```text
persistentvolume/pvc-6c88d7af-5c52-48b1-aa08-044104105355 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            Retain           Available           standard       <unset>                          87s
persistentvolumeclaim/data-som-db-0 created
```

ชื่อ `data-som-db-0` = `<ชื่อแม่แบบ data>-<ชื่อ Pod som-db-0>` คือชื่อที่ StatefulSet จะมองหา ถ้ามีอยู่แล้วมันจะ **ใช้ใบนี้** แทนการสร้างใหม่

**B-5 เปิดครัวแบบใหม่**

```bash
kubectl apply -f k8s/10-db.yaml
time kubectl -n som-shop rollout status sts/som-db --timeout=120s
kubectl -n som-shop get sts,pod,svc,pvc -o wide
kubectl get pv $PV
curl -s -w ' [%{http_code}]\n' localhost:30080/api/stats
```

```text
service/som-db created
statefulset.apps/som-db created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...

real	0m1.479s
...
NAME                      READY   AGE   CONTAINERS   IMAGES
statefulset.apps/som-db   1/1     1s    postgres     postgres:17.11-alpine

NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-0                   1/1     Running   0          1s    10.244.2.45   lab-worker2   <none>           <none>
pod/som-web-64fdf9cf64-5xhqn   1/1     Running   0          90s   10.244.1.4    lab-worker    <none>           <none>
pod/som-web-64fdf9cf64-cx84w   1/1     Running   0          90s   10.244.2.42   lab-worker2   <none>           <none>
pod/som-web-64fdf9cf64-hkd98   1/1     Running   0          90s   10.244.2.43   lab-worker2   <none>           <none>

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/som-db    ClusterIP   None           <none>        5432/TCP       1s    app=som-db
service/som-web   NodePort    10.96.119.79   <none>        80:30080/TCP   90s   app=som-web

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   VOLUMEMODE
persistentvolumeclaim/data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 1s    Filesystem
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                    STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            Retain           Bound    som-shop/data-som-db-0   standard       <unset>                          89s
som-web-64fdf9cf64-5xhqn 1.2 orders=3 products=6
 [200]
```

- `som-db-0 1/1 Running` ภายใน **1.5 วินาที** (postgres เจอข้อมูลเดิมใน `pgdata` จึงไม่ต้อง init ใหม่) บน Node เดียวกับ PV (`lab-worker2`)
- Service `som-db` เป็น **`CLUSTER-IP None`** (headless) และ PV เดิมเป็น `Bound som-shop/data-som-db-0`
- **web รุ่นเก่าที่ยังต่อ `som-db` ตอบ `orders=3` ได้ทันที** เพราะชื่อ headless `som-db` ตอนนี้ชี้ IP ของ `som-db-0` ตัวเดียว ข้อมูลย้ายมาครบ

### 10.4 ขั้น B2: ให้ web ต่อ som-db-0.som-db

<p align="center" id="fig-16">
  <img src="images/16-lab10-web-points-sts.png" alt="รูปที่ 16 LAB 10 ขั้น B2 web ชี้ som-db-0.som-db" width="900"><br>
  <em><b>รูปที่ 16</b> LAB10 ขั้น B (ต่อ): web ใช้ DATABASE_URL ...@som-db-0.som-db:5432 → rollout → /api/stats orders=3 ข้อมูลย้ายมาครบ</em>
</p>

```bash
kubectl apply -f k8s/20-web.yaml
time kubectl -n som-shop rollout status deploy/som-web --timeout=180s
for i in 1 2 3; do curl -s localhost:30080/api/stats; done
kubectl -n som-shop rollout history deploy/som-web
```

```text
deployment.apps/som-web configured
service/som-web unchanged
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out

real	0m18.855s
...
som-web-cbb884886-x5cs9 1.2 orders=3 products=6
som-web-64fdf9cf64-cx84w 1.2 orders=3 products=6
som-web-64fdf9cf64-cx84w 1.2 orders=3 products=6
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.2 ร้านจำได้ (db ใช้ PVC)
2         1.2 db เป็น StatefulSet (som-db-0.som-db)
```

web ทำ rolling update แบบบทที่ 7 (ลูกค้าไม่เจอร้านว่าง) ไม่กี่วินาทีแรกหลัง rollout ยังได้คำตอบจาก Pod เก่า (`som-web-64fdf9cf64-…`) เพราะ preStop 5 วินาที ซึ่งปกติ รอสักครู่แล้วตรวจอีกครั้ง

```bash
sleep 8; for i in 1 2 3 4; do curl -s localhost:30080/api/stats; done
kubectl -n som-shop get pod -l app=som-web
kubectl -n som-shop logs $(kubectl -n som-shop get pod -l app=som-web -o jsonpath='{.items[0].metadata.name}') -c wait-for-db
```

```text
som-web-cbb884886-sgb58 1.2 orders=3 products=6
som-web-cbb884886-sgb58 1.2 orders=3 products=6
som-web-cbb884886-xfrmq 1.2 orders=3 products=6
som-web-cbb884886-x5cs9 1.2 orders=3 products=6
NAME                      READY   STATUS    RESTARTS   AGE
som-web-cbb884886-sgb58   1/1     Running   0          45s
som-web-cbb884886-x5cs9   1/1     Running   0          52s
som-web-cbb884886-xfrmq   1/1     Running   0          39s
som-db-0.som-db:5432 - accepting connections
ฐานข้อมูลพร้อมแล้ว
```

ทุกคำตอบมาจาก Pod รุ่นใหม่ `som-web-cbb884886-…` และ init container `wait-for-db` ต่อ **`som-db-0.som-db:5432`** สำเร็จ

**คืน reclaimPolicy** ตอนนี้ PV อยู่กับใบเบิกใหม่เรียบร้อยแล้ว เอกสารนี้เลือกคืนเป็น `Delete` ตาม class `standard` เพื่อให้ตอนเก็บกวาด (`kubectl delete ns som-shop`) ไม่มี PV ค้าง (ระบบจริงที่ข้อมูลสำคัญควรคงเป็น `Retain`)

```bash
PV=$(kubectl -n som-shop get pvc data-som-db-0 -o jsonpath='{.spec.volumeName}'); kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'; kubectl get pv $PV --no-headers
kubectl -n som-shop get pvc data-som-db-0 --show-labels
```

```text
persistentvolume/pvc-6c88d7af-5c52-48b1-aa08-044104105355 patched
pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi   RWO   Delete   Bound   som-shop/data-som-db-0   standard   <unset>         2m10s
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   LABELS
data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 43s   app=som-db
```

PVC ที่เราสร้างเองมี label `app=som-db` เหมือน PVC ที่ StatefulSet สร้างให้ จึงเลือกด้วย `-l app=som-db` ได้ในขั้นถัดไป

### 10.5 ขั้น C: ลบ Pod som-db-0

<p align="center" id="fig-17">
  <img src="images/17-lab10-delete-pod.png" alt="รูปที่ 17 LAB 10 ขั้น C ลบ som-db-0" width="900"><br>
  <em><b>รูปที่ 17</b> LAB10 ขั้น C: ลบ som-db-0 → กลับมาชื่อเดิม UID/IP ใหม่ PVC data-som-db-0 เดิม → orders=3</em>
</p>

```bash
kubectl -n som-shop get pod som-db-0 -o jsonpath='{.metadata.uid} {.status.podIP} {.spec.nodeName}{"\n"}'
kubectl -n som-shop delete pod som-db-0
kubectl -n som-shop wait --for=condition=Ready pod/som-db-0 --timeout=120s
kubectl -n som-shop get pod som-db-0 -o jsonpath='{.metadata.uid} {.status.podIP} {.spec.nodeName} claimName={.spec.volumes[0].persistentVolumeClaim.claimName}{"\n"}'
for i in 1 2 3 4; do curl -s -w ' [%{http_code}]\n' localhost:30080/api/stats; sleep 1; done
```

```text
ea0d5d48-b079-4995-8241-096236c5d94a 10.244.2.45 lab-worker2
pod "som-db-0" deleted from som-shop namespace
pod/som-db-0 condition met
acfc1cf3-faf0-43fc-ae01-83de4303be62 10.244.2.48 lab-worker2 claimName=data-som-db-0
som-web-cbb884886-xfrmq 1.2 orders=3 products=6
 [200]
som-web-cbb884886-x5cs9 1.2 orders=3 products=6
 [200]
som-web-cbb884886-xfrmq 1.2 orders=3 products=6
 [200]
som-web-cbb884886-sgb58 1.2 orders=3 products=6
 [200]
```

ได้ **`som-db-0` ชื่อเดิม** แต่ UID ใหม่ (`ea0d5d48…` → `acfc1cf3…`) และ IP ใหม่ (`10.244.2.45` → `10.244.2.48`) บน Node เดิม (PV ผูก Node) ใช้ `data-som-db-0` เดิม ร้านตอบ `orders=3` และ HTTP 200 ทุกครั้ง web ไม่ต้องรู้ IP ใหม่ เพราะต่อด้วยชื่อ `som-db-0.som-db` (ถ้าเจอ `db-not-ready [503]` ครั้งแรกหนึ่งครั้งก็ไม่ผิด connection เดิมใน pool หลุด ครั้งถัดไปจะเป็น 200)

### 10.6 ขั้น D: rolling update ของ db

<p align="center" id="fig-18">
  <img src="images/18-lab10-rolling-db.png" alt="รูปที่ 18 LAB 10 ขั้น D rolling update db" width="900"><br>
  <em><b>รูปที่ 18</b> LAB10 ขั้น D: patch memory limit 512Mi → 768Mi → rolling update som-db (revision 2) → สั่งซื้อเพิ่ม orders=4</em>
</p>

เปลี่ยน template ของ db ด้วยการเพิ่ม memory limit (ไม่เปลี่ยน tag ของ postgres เพราะ `17.11-alpine` เป็นรุ่นล่าสุดของสาย 17 ตอนทดลอง) ใช้ JSON patch ระบุ path ตรง ๆ

```bash
kubectl -n som-shop patch sts som-db --type json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"768Mi"}]'
time kubectl -n som-shop rollout status sts/som-db --timeout=120s
kubectl -n som-shop rollout history sts/som-db
kubectl -n som-shop get pod som-db-0 -o jsonpath='{.spec.containers[0].resources.limits.memory} {.metadata.labels.controller-revision-hash}{"\n"}'
sleep 2; curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":4,"qty":1}'; echo
for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
statefulset.apps/som-db patched
Waiting for partitioned roll out to finish: 0 out of 1 new pods have been updated...
Waiting for 1 pods to be ready...
Waiting for 1 pods to be ready...
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...

real	0m1.974s
...
statefulset.apps/som-db 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

768Mi som-db-84b948b59f
{"ok":true,"order_id":4,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":59}}
som-web-cbb884886-xfrmq 1.2 orders=4 products=6
som-web-cbb884886-sgb58 1.2 orders=4 products=6
som-web-cbb884886-xfrmq 1.2 orders=4 products=6
```

rolling update ของ StatefulSet ที่มีตัวเดียว = ลบ `som-db-0` แล้วสร้างใหม่ด้วย template รุ่น 2 (ไม่มีสองตัวพร้อมกัน — ทำหน้าที่แทน `Recreate` ของบทที่ 8) ใช้ 2 วินาที Pod ใหม่มี limit `768Mi` และ revision `som-db-84b948b59f` สั่งซื้อเพิ่มเป็น **`orders=4`**

<p align="center" id="fig-19">
  <img src="images/screenshots/20261005_1420_lab10sts_01-shop-statefulset-4-orders.png" alt="รูปที่ 19 ภาพหน้าจอจริง ร้านที่ db เป็น StatefulSet" width="700"><br>
  <em><b>รูปที่ 19</b> ภาพหน้าจอจริงจากการทดลอง: ร้าน som-shop-v5 ที่ db เป็น StatefulSet som-db-0 + headless Service + PVC data-som-db-0 — การ์ดออเดอร์ทั้งหมด 4, แถบ "เสิร์ฟโดย Pod: som-web-cbb884886-… · เวอร์ชัน 1.2" (หัวเว็บยังเขียน "ReplicaSet + Service" เพราะใช้แอปเดิม)</em>
</p>

🌐 เปิด `http://localhost:30080` บน browser ตอนนี้จะเห็นการ์ด "ออเดอร์ทั้งหมด" เป็น 4 เหมือนรูปที่ 19 (ภาพถ่ายในรอบทดลองซ้ำเพื่อถ่ายภาพ ซึ่งสร้างร้านใหม่จาก `k8s/` แล้วสั่งซื้อ 4 รายการ ชื่อ Pod จึงต่างจากผลคำสั่งด้านบน)

### 10.7 ขั้น E: ลบ StatefulSet ทั้งตัวแล้ว apply ใหม่

<p align="center" id="fig-20">
  <img src="images/19-lab10-delete-sts.png" alt="รูปที่ 20 LAB 10 ขั้น E ลบ StatefulSet" width="900"><br>
  <em><b>รูปที่ 20</b> LAB10 ขั้น E: delete sts som-db → PVC data-som-db-0 ยัง Bound → apply 10-db.yaml → orders=4</em>
</p>

```bash
kubectl -n som-shop delete sts som-db
sleep 3; kubectl -n som-shop get pod -l app=som-db; kubectl -n som-shop get pvc
curl -s -w ' [%{http_code}]\n' localhost:30080/api/stats
kubectl apply -f k8s/10-db.yaml
kubectl -n som-shop rollout status sts/som-db --timeout=120s
sleep 2; for i in 1 2 3; do curl -s -w ' [%{http_code}]\n' localhost:30080/api/stats; done
kubectl -n som-shop get sts,pod,pvc -l app=som-db
```

```text
statefulset.apps "som-db" deleted from som-shop namespace
No resources found in som-shop namespace.
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 2m10s
som-web-cbb884886-sgb58 1.2 db-not-ready
 [503]
service/som-db unchanged
statefulset.apps/som-db created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...
som-web-cbb884886-sgb58 1.2 orders=4 products=6
 [200]
som-web-cbb884886-sgb58 1.2 orders=4 products=6
 [200]
som-web-cbb884886-sgb58 1.2 orders=4 products=6
 [200]
NAME                      READY   AGE
statefulset.apps/som-db   1/1     4s

NAME           READY   STATUS    RESTARTS   AGE
pod/som-db-0   1/1     Running   0          4s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 2m14s
```

- ระหว่างที่ไม่มี StatefulSet ร้านตอบ `db-not-ready [503]` (ไม่มี db) แต่ **PVC `data-som-db-0` ยัง `Bound`** (`whenDeleted: Retain`)
- apply ใหม่: `service/som-db unchanged` + `statefulset.apps/som-db created` `som-db-0` ตัวใหม่รับ PVC เดิม ร้านกลับมา **`orders=4`** โดยไม่ต้อง restart web
- memory limit กลับเป็น `512Mi` ตามไฟล์ (ค่า `768Mi` จากขั้น D เป็น patch ที่ไม่ได้อยู่ในไฟล์ — ตัวอย่างของ Warning last-applied ใน LAB 6)

<p align="center" id="fig-21">
  <img src="images/screenshots/20261005_1422_lab10sts_02-after-sts-deleted-reapplied-still-4.png" alt="รูปที่ 21 ภาพหน้าจอจริง หลังลบ StatefulSet แล้ว apply ใหม่" width="700"><br>
  <em><b>รูปที่ 21</b> ภาพหน้าจอจริงจากการทดลอง: หลังลบ Pod som-db-0 (กลับมาชื่อเดิม UID/IP ใหม่ PVC data-som-db-0 เดิม) แล้วลบ StatefulSet ทั้งตัว (เหลือ PVC Bound) และ apply ใหม่ "statefulset.apps/som-db created" — refresh หน้าร้านออเดอร์ยังเป็น 4</em>
</p>

ผลคำสั่งของรอบถ่ายภาพ (ร้านใหม่จาก `k8s/`) ที่ตรงกับรูปที่ 21

```text
NAME       UID                                    IP            PVC
som-db-0   8af73dc5-2f64-4103-856e-6c88cb19175c   10.244.2.65   data-som-db-0
pod "som-db-0" deleted from som-shop namespace
NAME       UID                                    IP            PVC
som-db-0   2697b49c-88b6-4382-a63d-74c5227df551   10.244.2.69   data-som-db-0
som-web-cbb884886-6nlsp 1.2 orders=4 products=6
statefulset.apps "som-db" deleted from som-shop namespace
NAME           READY   STATUS        RESTARTS   AGE
pod/som-db-0   1/1     Terminating   0          3s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-de97dba8-addf-43cc-8f6f-3c51311e4d2c   1Gi        RWO            standard       <unset>                 7m17s
service/som-db unchanged
statefulset.apps/som-db created
som-web-cbb884886-b442v 1.2 orders=4 products=6
```

(คำสั่งที่ใช้ดู UID/IP/PVC ในรอบนี้คือ `kubectl -n som-shop get pod som-db-0 -o custom-columns=NAME:.metadata.name,UID:.metadata.uid,IP:.status.podIP,PVC:.spec.volumes[0].persistentVolumeClaim.claimName`)

### 10.8 ขั้น F: scale db เป็น 3 (ข้อมูลไม่ได้ถูกคัดลอก)

<p align="center" id="fig-22">
  <img src="images/20-lab10-scale-three.png" alt="รูปที่ 22 LAB 10 ขั้น F scale db เป็น 3" width="900"><br>
  <em><b>รูปที่ 22</b> LAB10 ขั้น F: scale som-db 3 → PVC data-som-db-1/2 ใหม่ (ต่าง Node ได้), som-db-1/2 ไม่มีตาราง orders, nslookup som-db ได้ 3 IP แต่ร้านยังปกติเพราะ web ชี้ som-db-0</em>
</p>

บทที่ 8 scale db เป็น 2 แล้วข้อมูลเสีย บทนี้ StatefulSet ให้ตู้คนละใบ จึงไม่เสีย แต่ลองดูว่าได้อะไร

```bash
kubectl -n som-shop scale sts som-db --replicas=3
time kubectl -n som-shop rollout status sts/som-db --timeout=180s
kubectl -n som-shop get pod,pvc -l app=som-db -o wide
for i in 0 1 2; do echo "som-db-$i: $(kubectl -n som-shop exec som-db-$i -- psql -U som -d catshop -tAc 'select count(*) from orders' 2>&1 | head -1)"; done
```

```text
statefulset.apps/som-db scaled
Waiting for 2 pods to be ready...
Waiting for 1 pods to be ready...
Waiting for 1 pods to be ready...
partitioned roll out complete: 3 new pods have been updated...

real	0m17.057s
...
NAME           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-0   1/1     Running   0          45s   10.244.2.50   lab-worker2   <none>           <none>
pod/som-db-1   1/1     Running   0          17s   10.244.1.7    lab-worker    <none>           <none>
pod/som-db-2   1/1     Running   0          9s    10.244.2.52   lab-worker2   <none>           <none>

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE     VOLUMEMODE
persistentvolumeclaim/data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 2m55s   Filesystem
persistentvolumeclaim/data-som-db-1   Bound    pvc-c6e96a1b-b00f-4682-afd5-337771842007   1Gi        RWO            standard       <unset>                 17s     Filesystem
persistentvolumeclaim/data-som-db-2   Bound    pvc-1198dfe4-2201-4215-b09d-51eccf132f10   1Gi        RWO            standard       <unset>                 9s      Filesystem
som-db-0: 4
som-db-1: ERROR:  relation "orders" does not exist
som-db-2: ERROR:  relation "orders" does not exist
```

- ได้ `som-db-1`, `som-db-2` ทีละตัว (OrderedReady, รวม 17 วินาทีเพราะ postgres ต้อง init ฐานใหม่) พร้อม PVC ใหม่ `data-som-db-1/2` และ **ลงต่าง Node ได้** (`som-db-1` บน `lab-worker`) เพราะตู้ใหม่ถูกสร้างบน Node ที่ Pod ลง
- **`som-db-0` มี 4 ออเดอร์ ส่วน `som-db-1/2` ไม่มีตาราง `orders` เลย** = postgres เปล่า 2 ตัว StatefulSet ไม่คัดลอกข้อมูลให้ (ทฤษฎีหัวข้อ 8)

ดู DNS และร้าน (ใน namespace `som-shop` จะมี Warning PodSecurity เพราะ namespace ตั้ง `warn: restricted` และ busybox ไม่ได้ตั้ง securityContext — เป็นแค่คำเตือน Pod ยังถูกสร้าง)

```bash
kubectl -n som-shop run dns --image=busybox:1.36 --rm -it --restart=Never -- sh
```

ใน prompt `/ #` พิมพ์

```bash
nslookup som-db
nslookup som-db-1.som-db.som-shop.svc.cluster.local
exit
```

```text
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "dns" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "dns" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "dns" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "dns" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
...
/ # nslookup som-db
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find som-db.cluster.local: NXDOMAIN


Name:	som-db.som-shop.svc.cluster.local
Address: 10.244.2.50
Name:	som-db.som-shop.svc.cluster.local
Address: 10.244.2.52
Name:	som-db.som-shop.svc.cluster.local
Address: 10.244.1.7
...
/ # nslookup som-db-1.som-db.som-shop.svc.cluster.local
Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	som-db-1.som-db.som-shop.svc.cluster.local
Address: 10.244.1.7

/ # exit
Session ended, resume using 'kubectl attach dns -c dns -n som-shop -i -t' command
pod "dns" deleted from som-shop namespace
```

```bash
for i in 1 2 3 4 5 6; do curl -s localhost:30080/api/stats; done
```

```text
som-web-cbb884886-sgb58 1.2 orders=4 products=6
som-web-cbb884886-xfrmq 1.2 orders=4 products=6
som-web-cbb884886-sgb58 1.2 orders=4 products=6
som-web-cbb884886-xfrmq 1.2 orders=4 products=6
som-web-cbb884886-sgb58 1.2 orders=4 products=6
som-web-cbb884886-x5cs9 1.2 orders=4 products=6
```

`nslookup som-db` ได้ **3 Address** ถ้า web ยังต่อ `som-db` เหมือนบทที่ 8 จะสุ่มไปเจอฐานเปล่า แต่ร้านตอบ **`orders=4` ทุกครั้ง** เพราะ `k8s/20-web.yaml` ต่อ `som-db-0.som-db` ตรง ๆ (ทฤษฎีหัวข้อ 10.2)

### 10.9 ขั้น G: scale กลับเป็น 1 และลบตู้ที่ค้าง

<p align="center" id="fig-23">
  <img src="images/21-lab10-scale-back.png" alt="รูปที่ 23 LAB 10 ขั้น G scale กลับ 1" width="900"><br>
  <em><b>รูปที่ 23</b> LAB10 ขั้น G: scale กลับ 1 → som-db-1/2 ถูกลบ (2 ก่อน 1) แต่ PVC data-som-db-1/2 ยังอยู่ ต้องลบเอง</em>
</p>

```bash
kubectl -n som-shop scale sts som-db --replicas=1
for i in $(seq 1 6); do echo "$(date +%T) $(kubectl -n som-shop get pod -l app=som-db --no-headers | awk '{print $1":"$3}' | tr '\n' ' ')"; sleep 2; done
kubectl -n som-shop get pod,pvc -l app=som-db
```

```text
statefulset.apps/som-db scaled
14:11:01 som-db-0:Running som-db-1:Running som-db-2:Terminating 
14:11:03 som-db-0:Running 
...
NAME           READY   STATUS    RESTARTS   AGE
pod/som-db-0   1/1     Running   0          95s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 3m45s
persistentvolumeclaim/data-som-db-1   Bound    pvc-c6e96a1b-b00f-4682-afd5-337771842007   1Gi        RWO            standard       <unset>                 67s
persistentvolumeclaim/data-som-db-2   Bound    pvc-1198dfe4-2201-4215-b09d-51eccf132f10   1Gi        RWO            standard       <unset>                 59s
```

`som-db-2` ถูกปิดก่อน (`som-db-1` ยัง Running) แล้วจึง `som-db-1` เหลือ `som-db-0` ในราว 2 วินาที แต่ **PVC `data-som-db-1/2` ยัง `Bound`** ตาม retention เริ่มต้น ถ้าไม่ลบ ครั้งหน้าที่ scale ขึ้น `som-db-1` จะได้ฐานเปล่าเดิมคืน ลบเองให้เรียบร้อย

```bash
kubectl -n som-shop delete pvc data-som-db-1 data-som-db-2
sleep 3; kubectl -n som-shop get pvc; kubectl get pv
curl -s localhost:30080/api/stats
```

```text
persistentvolumeclaim "data-som-db-1" deleted from som-shop namespace
persistentvolumeclaim "data-som-db-2" deleted from som-shop namespace
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 3m49s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                    STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            Delete           Bound    som-shop/data-som-db-0   standard       <unset>                          5m16s
som-web-cbb884886-sgb58 1.2 orders=4 products=6
```

เหลือ PVC และ PV ใบเดียวของ `som-db-0` (PV ของ `-1/-2` ถูกลบตามเพราะ class `standard` เป็น `Delete`) ร้านยัง `orders=4`

<p align="center" id="fig-24">
  <img src="images/screenshots/20261005_1423_lab10sts_03-order-after-scale-5-orders.png" alt="รูปที่ 24 ภาพหน้าจอจริง สั่งซื้อหลัง scale" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: หลัง scale เป็น 3 (ได้ data-som-db-0/1/2 แยกกัน som-db-1/2 ไม่มีตาราง orders เพราะไม่ replicate) แล้ว scale กลับ 1 (PVC 1/2 ยังค้างตาม retention เริ่มต้น) — กดสั่งซื้อผ่าน browser ได้ "สั่งซื้อแล้ว! ออเดอร์ #5" การ์ดออเดอร์ทั้งหมดเป็น 5</em>
</p>

🌐 ลองกดปุ่ม **สั่งซื้อ** บนหน้าร้านหนึ่งครั้ง ร้านยังเขียนลง `som-db-0` ได้ปกติ (รูปที่ 24 ถ่ายในรอบทดลองซ้ำ ซึ่งมี 4 ออเดอร์ก่อนกด จึงได้ออเดอร์ #5 ถ้ากดในรอบหลักของเอกสารนี้ก็จะได้ #5 เช่นกัน แต่ขั้น H ด้านล่างใช้ตัวเลขจากการสั่งซื้อด้วย `curl` — ถ้ากดใน browser แล้ว ตัวเลขในขั้น H ของนักศึกษาจะมากกว่าเอกสาร 1)

ผลคำสั่งของรอบถ่ายภาพที่ตรงกับรูปที่ 24 (ก่อนกดสั่งซื้อ)

```text
NAME           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-0   1/1     Running   0          33s   10.244.2.70   lab-worker2   <none>           <none>
pod/som-db-1   1/1     Running   0          17s   10.244.1.15   lab-worker    <none>           <none>
pod/som-db-2   1/1     Running   0          9s    10.244.2.72   lab-worker2   <none>           <none>
...
som-db-0: 4
som-db-1: ERROR:  relation "orders" does not exist
som-db-2: ERROR:  relation "orders" does not exist
som-web-cbb884886-wvwmc 1.2 orders=4 products=6
statefulset.apps/som-db scaled
NAME           READY   STATUS    RESTARTS   AGE
pod/som-db-0   1/1     Running   0          41s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-de97dba8-addf-43cc-8f6f-3c51311e4d2c   1Gi        RWO            standard       <unset>                 7m59s
persistentvolumeclaim/data-som-db-1   Bound    pvc-1cd6b5a8-7096-4d55-be03-20e1e520e86b   1Gi        RWO            standard       <unset>                 25s
persistentvolumeclaim/data-som-db-2   Bound    pvc-0f4c1463-e1ce-49eb-abab-ebee7f7c9935   1Gi        RWO            standard       <unset>                 17s
```

### 10.10 ขั้น H (เสริม): read replica ด้วย streaming replication

<p align="center" id="fig-25">
  <img src="images/22-lab10-extra-replica.png" alt="รูปที่ 25 LAB 10 เสริม read replica" width="900"><br>
  <em><b>รูปที่ 25</b> LAB10 เสริม: เพิ่มบรรทัด host replication ใน pg_hba.conf ของ som-db-0 → StatefulSet som-db-replica (init pg_basebackup -R) → pg_is_in_recovery = t, pg_stat_replication streaming async</em>
</p>

ขั้นนี้แสดงว่าสำเนาข้อมูลจริงต้องทำด้วยความสามารถของ postgres (ทฤษฎีหัวข้อ 8.2) ใช้ StatefulSet ตัวที่สอง `som-db-replica` (`extra/replica.yaml`) ที่ใช้ `serviceName: som-db` เดียวกัน (label `app: som-db-replica` จึงไม่ปนใน `nslookup som-db`) init container `clone-from-primary` โคลนจาก `som-db-0.som-db` **เฉพาะครั้งแรก** (มี `PG_VERSION` แล้ว = ข้าม)

**H-1 อนุญาต replication บน primary** ปกติแก้ด้วย ConfigMap (บทหลัง) LAB นี้ใช้ `kubectl exec` เพิ่มบรรทัดลง `pg_hba.conf` ซึ่งอยู่ใน `PGDATA` บน PVC จึงคงอยู่ข้าม restart

```bash
kubectl -n som-shop exec som-db-0 -- sh -c 'echo "host replication all all scram-sha-256" >> $PGDATA/pg_hba.conf; psql -U som -d catshop -c "select pg_reload_conf()"'
```

```text
 pg_reload_conf 
----------------
 t
(1 row)
```

**H-2 สร้าง replica**

```bash
kubectl apply -f extra/replica.yaml
time kubectl -n som-shop rollout status sts/som-db-replica --timeout=180s
kubectl -n som-shop logs som-db-replica-0 -c clone-from-primary
kubectl -n som-shop get pod,pvc -o wide | grep -E "NAME|som-db"
```

```text
statefulset.apps/som-db-replica created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...

real	0m5.989s
...
waiting for checkpoint
30955/30955 kB (100%), 0/1 tablespace
30955/30955 kB (100%), 1/1 tablespace
cloned
NAME                          READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-0                  1/1     Running   0          2m9s    10.244.2.50   lab-worker2   <none>           <none>
pod/som-db-replica-0          1/1     Running   0          6s      10.244.2.55   lab-worker2   <none>           <none>
NAME                                          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE     VOLUMEMODE
persistentvolumeclaim/data-som-db-0           Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 4m19s   Filesystem
persistentvolumeclaim/data-som-db-replica-0   Bound    pvc-807bdbb6-2cc6-4620-a612-c0428cba4f90   1Gi        RWO            standard       <unset>                 6s      Filesystem
```

`pg_basebackup` ดึงข้อมูลทั้งก้อน (30955 kB) จาก `som-db-0` ลงตู้ `data-som-db-replica-0` ของ replica แล้ว postgres เปิดเป็น standby ภายในราว 6 วินาที

**H-3 ตรวจว่าเป็นสำเนาจริง**

```bash
kubectl -n som-shop exec som-db-replica-0 -- psql -U som -d catshop -tAc "select pg_is_in_recovery(), count(*) from orders"
kubectl -n som-shop exec som-db-replica-0 -c postgres -- psql -U som -d catshop -tAc "select pg_is_in_recovery(), count(*) from orders"
curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":5,"qty":1}'; echo; sleep 1
echo "primary: $(kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders')  replica: $(kubectl -n som-shop exec som-db-replica-0 -c postgres -- psql -U som -d catshop -tAc 'select count(*) from orders')"
kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc "select client_addr, state, sync_state from pg_stat_replication"
```

```text
Defaulted container "postgres" out of: postgres, clone-from-primary (init)
t|4
t|4
{"ok":true,"order_id":5,"product":{"id":5,"name_th":"ขนมแมวเลียรสไก่ (แพ็ก 4)","stock":39}}
primary: 5  replica: 5
10.244.2.55|streaming|async
```

- `exec` เข้า replica โดยไม่ใส่ `-c` ได้ข้อความ `Defaulted container "postgres" out of: postgres, clone-from-primary (init)` (Pod มี init container) ใส่ `-c postgres` แล้วข้อความหายไป
- `t|4` = `pg_is_in_recovery()` เป็นจริง (เป็น standby) และเห็น 4 ออเดอร์เท่า primary
- สั่งซื้อผ่านร้านเป็นออเดอร์ที่ 5 แล้ว **replica เห็นตามทันที** (`primary: 5  replica: 5`) และ primary เห็นการเชื่อมต่อจาก IP ของ replica (`10.244.2.55`) สถานะ `streaming` แบบ `async`

<p align="center" id="fig-26">
  <img src="images/23-lab10-extra-readonly.png" alt="รูปที่ 26 LAB 10 เสริม replica อ่านอย่างเดียว" width="900"><br>
  <em><b>รูปที่ 26</b> LAB10 เสริม (ต่อ): สั่งซื้อแล้ว replica เห็นตาม (orders เท่ากัน), INSERT บน replica → cannot execute INSERT in a read-only transaction, ลบ som-db-0 แล้ว replica ต่อกลับเอง</em>
</p>

**H-4 replica เขียนไม่ได้ และอยู่รอดเมื่อ Pod ถูกลบ**

```bash
kubectl -n som-shop exec som-db-replica-0 -c postgres -- psql -U som -d catshop -c "insert into orders(product_id,qty) values (1,1)"
kubectl -n som-shop delete pod som-db-replica-0; kubectl -n som-shop wait --for=condition=Ready pod/som-db-replica-0 --timeout=120s
kubectl -n som-shop logs som-db-replica-0 -c clone-from-primary
kubectl -n som-shop exec som-db-replica-0 -c postgres -- psql -U som -d catshop -tAc "select pg_is_in_recovery(), count(*) from orders"
```

```text
ERROR:  cannot execute INSERT in a read-only transaction
command terminated with exit code 1
pod "som-db-replica-0" deleted from som-shop namespace
pod/som-db-replica-0 condition met
already-cloned
t|5
```

INSERT บน replica ถูกปฏิเสธ (อ่านอย่างเดียว) และเมื่อลบ Pod replica ตัวใหม่ได้ **ตู้เดิม** (`data-som-db-replica-0`) init จึงพิมพ์ `already-cloned` แล้ว stream ต่อจากจุดเดิม (`t|5`)

**H-5 ลบ primary แล้ว replica ต่อกลับเอง**

```bash
kubectl -n som-shop delete pod som-db-0; kubectl -n som-shop wait --for=condition=Ready pod/som-db-0 --timeout=120s
sleep 3; curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":6,"qty":1}'; echo
for i in $(seq 1 10); do R=$(kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc "select count(*) from pg_stat_replication"); [ "$R" = 1 ] && break; sleep 2; done; echo "repl=$R"
echo "primary: $(kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders')  replica: $(kubectl -n som-shop exec som-db-replica-0 -c postgres -- psql -U som -d catshop -tAc 'select count(*) from orders')"
kubectl -n som-shop logs som-db-replica-0 -c postgres --tail=6
```

```text
pod "som-db-0" deleted from som-shop namespace
pod/som-db-0 condition met
{"ok":true,"order_id":6,"product":{"id":6,"name_th":"ขนมฟรีซดรายแซลมอน 40 ก.","stock":24}}
repl=1
primary: 6  replica: 6
...
2026-10-05 07:12:13.625 UTC [26] LOG:  invalid record length at 0/3000AB8: expected at least 24, got 0
2026-10-05 07:12:13.644 UTC [43] FATAL:  could not connect to the primary server: could not translate host name "som-db-0.som-db" to address: Name does not resolve
2026-10-05 07:12:13.644 UTC [26] LOG:  waiting for WAL to become available at 0/3000AD0
2026-10-05 07:12:18.636 UTC [51] LOG:  started streaming WAL from primary at 0/3000000 on timeline 1
```

- ระหว่างที่ `som-db-0` ถูกสร้างใหม่ ชื่อ `som-db-0.som-db` **ไม่อยู่ใน DNS** (Pod ยังไม่ Ready — LAB 2) replica จึงต่อไม่ได้ (`Name does not resolve`) แล้วลองใหม่เอง 5 วินาทีต่อมา `started streaming WAL from primary`
- บรรทัด `host replication …` ใน `pg_hba.conf` รอดการ restart เพราะอยู่ใน PVC ของ `som-db-0` สั่งซื้อครั้งที่ 6 แล้วทั้งสองฝั่งเห็น `6`
- **นี่ไม่ใช่ failover** ระหว่างที่ `som-db-0` หายไป replica ไม่ได้ขึ้นมาเป็นตัวหลัก ร้านเขียนไม่ได้จนกว่า `som-db-0` จะกลับ งานนี้คือหน้าที่ของ Operator (ทฤษฎีหัวข้อ 8.3)

**ถ้าต้องการเก็บร้านไว้แต่เอา replica ออก** (ไม่บังคับ) ลบ StatefulSet และตู้ของ replica (บรรทัดใน `pg_hba.conf` ค้างอยู่ใน PVC ไม่เป็นไร)

```bash
kubectl -n som-shop delete sts som-db-replica && kubectl -n som-shop delete pvc data-som-db-replica-0
```

### 10.11 ขั้น I: เก็บกวาด LAB 10

```bash
time kubectl delete ns som-shop
kubectl get pv; kubectl get ns
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n ls /var/local-path-provisioner; done
```

```text
namespace "som-shop" deleted

real	0m32.243s
...
No resources found
NAME                 STATUS   AGE
default              Active   32m
kube-node-lease      Active   32m
kube-public          Active   32m
kube-system          Active   32m
local-path-storage   Active   32m
== lab-worker
== lab-worker2
```

ลบ namespace ใช้ราว 32 วินาที (Pod web มี preStop และ grace period) PVC ทุกใบใน namespace หายตาม และเพราะขั้น B2 คืน PV เป็น `Delete` แล้ว **PV หายหมด** และโฟลเดอร์ใต้ `/var/local-path-provisioner` บนทั้งสอง worker ว่าง ถ้าเลือกคง `Retain` ไว้ ต้อง `kubectl delete pv <ชื่อ>` และลบโฟลเดอร์บน Node เองแบบบทที่ 8

> **อยากเปิดร้านไว้ดูต่อ:** `kubectl apply -f k8s/` สร้างร้านใหม่ที่ db เป็น StatefulSet ตั้งแต่แรก (PVC `data-som-db-0` มาจาก `volumeClaimTemplates` ไม่ต้องย้าย) ผลจริงของรอบทดลอง

```bash
kubectl apply -f k8s/
kubectl -n som-shop rollout status sts/som-db --timeout=180s
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
```

```text
namespace/som-shop created
service/som-db created
statefulset.apps/som-db created
deployment.apps/som-web created
service/som-web created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...
...
deployment "som-web" successfully rolled out
```

(การทดลองยิง 30 request ผ่าน NodePort ด้วย `hit.sh` ไปที่ร้านใหม่นี้ได้ `ok=30 err=0` กระจายไปทั้ง 3 Pod ของ web) เมื่อดูเสร็จให้ `kubectl delete ns som-shop` อีกครั้ง

### 10.12 สรุป LAB 10 และปัญหาที่ส่งต่อ

<p align="center" id="fig-27">
  <img src="images/24-lab10-wrap-up.png" alt="รูปที่ 27 สรุป LAB สุดท้าย" width="900"><br>
  <em><b>รูปที่ 27</b> LAB10 สรุปและบทถัดไป: db มีชื่อคงที่และตู้เซฟประจำตัวแล้ว แต่รหัสผ่านยังอยู่ใน YAML (→ Secret), เปิดร้านผ่าน NodePort (→ Ingress), web ยังต้อง scale เอง (→ HPA)</em>
</p>

**ตารางสรุป** ออเดอร์ตลอด LAB 10 (จาก `/api/stats`)

| ขั้น | ทำอะไร | ผล | orders |
|---|---|---|:---:|
| A | `apply -f k8s-008/` + สั่งซื้อ 3 | Deployment `som-db-7b786655f5-bdsgq` + PVC `som-db-data` | 3 |
| B | Retain → ลบ deploy/svc/pvc → ลบ claimRef → PVC `data-som-db-0` → `apply k8s/10-db.yaml` | `som-db-0` ใช้ PV เดิม Service headless (error `may not change once set` ถ้าไม่ลบ Service เดิม) | 3 |
| B2 | `apply k8s/20-web.yaml` + คืน PV เป็น Delete | web ต่อ `som-db-0.som-db` | 3 |
| C | `delete pod som-db-0` | ชื่อเดิม UID/IP ใหม่ PVC เดิม | 3 |
| D | patch memory 768Mi + สั่งซื้อ | rolling update REVISION 2 (2 วินาที) | 4 |
| E | `delete sts` → `apply k8s/10-db.yaml` | ระหว่างนั้น 503 / PVC Bound ตลอด | 4 |
| F | `scale --replicas=3` | `som-db-1/2` ฐานเปล่า (`relation "orders" does not exist`) ร้านปกติ | 4 |
| G | `scale --replicas=1` + ลบ `data-som-db-1/2` | ตู้ไม่หายเอง ต้องลบ | 4 |
| H | `pg_hba.conf` + `apply extra/replica.yaml` + สั่งซื้อ 2 | replica `t`, `streaming async`, read-only, ต่อกลับเองเมื่อ primary เกิดใหม่ | 5 → 6 |
| I | `delete ns som-shop` | PV หมด | – |

**สิ่งที่ StatefulSet แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม**

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| db มีชื่อคงที่ให้แอปและ replica อ้างถึง | `som-db-0` / `som-db-0.som-db` ลบกี่ครั้งก็ชื่อเดิม | ✅ StatefulSet + headless Service (บทนี้) |
| db หลายตัวมีตู้ของตัวเอง ไม่เขียนทับกัน | scale 3 ได้ `data-som-db-0/1/2` คนละใบ ข้อมูลไม่เสียแบบบทที่ 8 | ✅ volumeClaimTemplates |
| อัปเดต db โดยไม่มีสองตัวพร้อมกัน | rolling update ลบก่อนสร้าง (แทน `Recreate`) | ✅ updateStrategy ของ StatefulSet |
| ลบ StatefulSet พลาด | PVC `data-som-db-0` Bound ตลอด apply ใหม่ได้ข้อมูลเดิม | ✅ retention default Retain |
| สำเนาข้อมูลจริง | scale ไม่ได้คัดลอก ต้อง streaming replication เอง | ⚠️ ทำได้ระดับแอป (LAB เสริม) |
| สลับตัวหลักอัตโนมัติเมื่อ `som-db-0` ตาย | replica ได้แค่รอ ร้านเขียนไม่ได้ | ❌ → Operator |
| Node ที่ db อยู่ล่ม | LAB 9: StatefulSet รอ (at most one) + local-path ผูก Node | ❌ → storage เครือข่าย / replication ข้าม Node |
| รหัสผ่านไม่อยู่ใน YAML | `meow1234` ใน `k8s/10-db.yaml`, `k8s/20-web.yaml`, `extra/replica.yaml` | ❌ → ConfigMap/Secret (บทถัดไป) |
| เปิดร้านด้วยชื่อโดเมน | ยังใช้ `http://localhost:30080` (NodePort) | ❌ → Ingress |
| web ปรับจำนวนเอง | `som-web` `replicas: 3` ตายตัว | ❌ → HPA |

### สิ่งที่เห็นใน LAB 10

- ย้าย PV เดิมของบทที่ 8 เป็น PVC `data-som-db-0` ได้โดยไม่เสียออเดอร์ (Retain → ลบ claimRef → PVC ที่มี `volumeName` → StatefulSet ใช้ PVC ชื่อตรง) และต้องลบ Service ClusterIP ก่อนเปลี่ยนเป็น headless
- ลบ Pod, rolling update, ลบ StatefulSet → ออเดอร์อยู่ครบ web ไม่ต้อง restart เพราะต่อ `som-db-0.som-db`
- scale เป็น 3 = ฐานเปล่า 2 ตัว + PVC ที่ต้องลบเอง ไม่ใช่การทำสำเนา
- สำเนาจริงทำได้ด้วย streaming replication (อ่านอย่างเดียว ไม่ใช่ failover)

### คำถามท้าย LAB 10

1. ขั้น B ถ้าลืม `kubectl -n som-shop delete svc som-db` แล้ว apply `k8s/10-db.yaml` จริง (ไม่ใช่ dry-run) จะเกิดอะไรกับ Service, StatefulSet และ PVC `data-som-db-0` และต้องแก้อย่างไรก่อนย้ายข้อมูลต่อ
2. ทำไมต้องสร้าง PVC `data-som-db-0` **ก่อน** apply StatefulSet และทำไมชื่อต้องเป็น `data-som-db-0` พอดี (อ้าง `volumeClaimTemplates` ใน `k8s/10-db.yaml`)
3. ขั้น B5 web รุ่นเก่าที่ยังต่อ `som-db` ตอบ `orders=3` ได้ทันที แต่ทำไมเราจึงยังต้องเปลี่ยน web ให้ต่อ `som-db-0.som-db` (อ้างผลของขั้น F)
4. เทียบการ rolling update db ในขั้น D กับ `strategy: Recreate` ของบทที่ 8 เหมือนหรือต่างกันอย่างไรในแง่ "ช่วงที่ไม่มี db" และ "postgres สองตัวบนตู้เดียว"
5. ถ้าน้องส้มต้องการให้ร้าน **อ่าน** สถิติจาก replica แต่ **เขียน** ออเดอร์ลง primary ควรตั้ง `DATABASE_URL` สองตัวชี้ชื่อ DNS อะไร และถ้า `som-db-0` ตาย ระบบนี้ยังขาดอะไร

> **🏆 ท้าทาย:** หลังขั้น H ลอง scale `som-db-replica` เป็น 2 แล้วตรวจว่า `som-db-replica-1` โคลนได้เองหรือไม่ (`kubectl -n som-shop logs som-db-replica-1 -c clone-from-primary`) และ `pg_stat_replication` บน primary มีกี่แถว (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเองและอย่าลืมลบ PVC ของ replica ทุกใบ)

> **ปูทางบทหน้า:** ครัวกลางมีชื่อคงที่และตู้เซฟประจำตัวแล้ว แต่รหัสผ่าน `meow1234` ยังกระจายอยู่ในไฟล์ YAML ทุกไฟล์ และการแก้ `pg_hba.conf` ยังต้อง `kubectl exec` เข้าไปพิมพ์เอง บทถัดไปจะใช้ **ConfigMap และ Secret** แยกค่าตั้งและความลับออกจาก manifest

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v5/`, kubectl แจ้ง `the path "sts.yaml" does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 009_kubernetes_statefulset k8s-lab:/workspace/` แล้ว 🐧 `cd` ไปโฟลเดอร์ของ LAB นั้น ตรวจด้วย `pwd` |
| `./show.sh: Permission denied` | สิทธิ์ execute หายระหว่างคัดลอก | `bash ../lab06-update/show.sh` หรือ `chmod +x show.sh` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 6 (build/load image ใหม่) |
| StatefulSet ค้างที่ `<ชื่อ>-0 0/1` ไม่มีตัวถัดไป | OrderedReady รอ Pod แรก Ready (readinessProbe ไม่ผ่าน — LAB 4 ตั้งใจ) | `kubectl describe pod <ชื่อ>-0` ดู `Readiness probe failed` แก้ probe/แอป หรือ `kubectl exec bad-0 -- touch /tmp/ready` ใน LAB 4 |
| `nslookup web` มีบรรทัด `** server can't find web.cluster.local: NXDOMAIN` | busybox ลองทุก search domain แล้วพิมพ์ที่ไม่เจอปนมา | ปกติ ดูเฉพาะ `Name:`/`Address:` หรือ `kubectl exec dns -- nslookup web 2>&1 \| grep -A1 "^Name"` |
| `wget web-1.web` ได้ `can't connect to remote host (127.0.53.53): Connection refused` | `web-1` ไม่ Ready ชื่อในคลัสเตอร์จึงไม่มี resolver ลองชื่อสั้นตรง ๆ และหลุดไปถาม DNS ภายนอก (`.web` เป็น TLD จริง) | ใช้ชื่อเต็ม `web-1.web.default.svc.cluster.local` (ได้ `bad address`/`NXDOMAIN` ตามจริง) แล้วแก้ให้ Pod Ready |
| ชื่อ `<pod>.<svc>` resolve ไม่ได้ทั้งที่ Pod Running | Pod ไม่ Ready, Service ไม่ใช่ headless, ชื่อ Service ไม่ตรง `serviceName` หรือ selector ไม่ตรง | `kubectl get svc <svc>` (ต้อง `CLUSTER-IP None`), `kubectl get sts <ชื่อ> -o jsonpath='{.spec.serviceName}'`, `kubectl get endpointslice -l kubernetes.io/service-name=<svc> -o yaml` ดู `ready` |
| `kubectl run dns ... -it` ไม่ขึ้น prompt | prompt ถูกพิมพ์ก่อน attach | กด Enter หนึ่งครั้ง หรือใช้ `dns-pod.yaml` + `kubectl exec dns -- nslookup ...` |
| `Session ended, resume using 'kubectl attach dns …'` หลัง `exit` | ข้อความปกติของ `kubectl run -it --rm` | ไม่ต้องทำอะไร Pod ถูกลบตาม `--rm` |
| `Warning: would violate PodSecurity "restricted:latest" …` ตอน `kubectl -n som-shop run dns` | namespace `som-shop` ตั้ง `warn: restricted` | ปกติ เป็นแค่คำเตือน Pod ยังถูกสร้าง |
| scale กลับแล้วได้ข้อมูลเก่า / ฐานเปล่าเดิม | PVC ไม่หายเมื่อ scale down หรือลบ StatefulSet (default `Retain`) | ลบ PVC เองเมื่อไม่ใช้ `kubectl delete pvc -l app=<label>` หรือ `kubectl -n som-shop delete pvc data-som-db-1 data-som-db-2` |
| `kubectl get pv` ยังเห็น PV หลังลบ StatefulSet | PVC ยังอยู่ (Bound) | ลบ PVC ก่อน PV จาก class `standard` จะหายตาม |
| `kubectl rollout status` ตอบ `partitioned roll out complete: 1 new pods have been updated...` ทั้งที่ยังมี Pod รุ่นเก่า | มี `partition` อยู่ rollout ถือว่าจบที่เชือก | ปกติ ใช้ `show.sh` ดู `updated=` และลด partition (`partition-0.yaml`) เมื่อพร้อม |
| `error: rollout status is only available for RollingUpdate strategy type` | StatefulSet เป็น `OnDelete` | ดูด้วย `../lab06-update/show.sh` หรือ `kubectl get sts web -o jsonpath='{.status.updatedReplicas}'` |
| `set image` แล้วไม่มี Pod ไหนเปลี่ยน | `OnDelete` (LAB 7) หรือ `partition` สูงกว่า ordinal ทุกตัว | ลบ Pod เอง (OnDelete) หรือลด partition |
| `Warning: resource statefulsets/web was previously managed with 'kubectl apply' …` ตอน `rollout undo` | undo ไม่แก้ annotation last-applied | ปกติ ถ้า apply ไฟล์เดิมจะกลับไปตามไฟล์ แก้ไฟล์แล้ว apply เป็นแนวปฏิบัติ |
| LAB 9: `web-1` ค้าง `Terminating` นาน ไม่มีตัวใหม่ | at most one — StatefulSet ไม่สร้างแทนจนกว่า Pod เดิมถูกลบจริง (ตั้งใจให้เห็น) | รอดูตามขั้นที่ 2 แล้วทำขั้นที่ 3 (taint `out-of-service`) **อย่า force delete** |
| LAB 9: `$N` ว่าง / `docker stop` ผิดตัว / `kubectl taint node` ไม่เจอ Node | เปิด shell ใหม่ ตัวแปรหาย | ดู Node จาก `kubectl get pod -l app=web -o wide` หรือ `kubectl get nodes` (ตัวที่ `NotReady`) แล้วตั้ง `N=<ชื่อ>` ใหม่ |
| LAB 9: `web-1` ใหม่ `Pending` + `didn't match PersistentVolume's node affinity` | PV local-path ผูก Node ที่หยุด | ปกติ เอา taint ออก + `docker start $N` |
| หลัง LAB 9 Node ยัง `NotReady` / มี taint `out-of-service` ค้าง / Pod ใน LAB 10 `Pending` | ลืมขั้นที่ 4 | 🐧 `kubectl taint node $N node.kubernetes.io/out-of-service-` แล้ว `docker start $N` ตรวจ `kubectl get nodes` และ `kubectl describe node $N \| grep Taints` |
| `kind load` ล้มเหลว `failed to detect containerd snapshotter` | สั่งระหว่างที่ Node ถูกหยุด | `docker start` Node ให้ครบก่อนแล้ว load ใหม่ |
| `The Service "som-db" is invalid: spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set` | apply headless Service ทับ Service ClusterIP เดิม | `kubectl -n som-shop delete svc som-db` แล้ว apply ใหม่ (ตรวจล่วงหน้าด้วย `--dry-run=server`) |
| เผลอ apply `k8s/10-db.yaml` จริงก่อนย้ายข้อมูล: `som-db-0` ขึ้นมาแต่ร้าน `orders` ไม่ใช่ 3 / PVC `data-som-db-0` ชี้ PV ใหม่ | StatefulSet สร้าง PVC `data-som-db-0` เปล่าจากแม่แบบไปก่อน | **อย่าลบ PV เดิม** `kubectl -n som-shop delete sts som-db` → `kubectl -n som-shop delete pvc data-som-db-0` (PV เปล่าหายตาม) → ทำขั้น B ต่อจาก B-2 (ตรวจว่า PV เดิมยังเป็น `Retain`) |
| PVC `data-som-db-0` ค้าง `Pending` หลัง `sed … \| kubectl apply -f -` | PV ยังมี `claimRef` เดิม (ยัง `Released`), ชื่อ PV ใน `$PV` ว่าง หรือ class/ขนาด/accessMode ไม่ตรง | `kubectl get pv $PV` ต้องเป็น `Available` ก่อน (B-4) และ `echo $PV` ต้องไม่ว่าง ถ้า PV มาจาก `k8s-retain/` ของบทที่ 8 (RWOP) ให้เริ่มจาก `k8s-008/` |
| apply `migrate/` ทั้งโฟลเดอร์แล้ว error เกี่ยวกับ `PVNAME` | ไฟล์เป็นแม่แบบที่ยังไม่แทนชื่อ PV | ใช้ `sed "s/PVNAME/$PV/" migrate/data-som-db-0-pvc.yaml \| kubectl apply -f -` เท่านั้น |
| `/api/stats` ได้ `db-not-ready [503]` | ช่วงที่ไม่มี db (ขั้น B-3 ถึง B-5, ขั้น E) หรือ connection เดิมหลุดหลังลบ Pod db | ปกติ รอ db Ready แล้วลองใหม่ ถ้าค้างนาน ดู `kubectl -n som-shop get pod -l app=som-db` |
| หลัง apply `k8s/20-web.yaml` ยังเห็นชื่อ Pod web รุ่นเก่า | preStop 5 วินาทีของ Pod เก่า | ปกติ รอ ~8 วินาทีแล้วตรวจใหม่ |
| `som-db-1: ERROR:  relation "orders" does not exist` | StatefulSet ไม่คัดลอกข้อมูล (ขั้น F ตั้งใจให้เห็น) | ปกติ scale กลับ 1 และลบ `data-som-db-1/2` |
| `Defaulted container "postgres" out of: postgres, clone-from-primary (init)` | `kubectl exec` เข้า Pod ที่มี init container โดยไม่ระบุ `-c` | ใส่ `-c postgres` |
| replica `som-db-replica-0` ค้างที่ `Init` หรือ init container จบด้วย error (ดู `kubectl -n som-shop logs som-db-replica-0 -c clone-from-primary`) | ยังไม่ได้ทำ H-1 (primary ยังไม่อนุญาตการเชื่อมต่อแบบ replication ใน `pg_hba.conf`) | ทำ H-1 แล้ว `kubectl -n som-shop delete sts som-db-replica && kubectl -n som-shop delete pvc data-som-db-replica-0` แล้ว apply `extra/replica.yaml` ใหม่ |
| replica log `could not translate host name "som-db-0.som-db" to address` | `som-db-0` กำลังถูกสร้างใหม่ (ไม่ Ready = ไม่อยู่ใน DNS) | ปกติ replica ต่อใหม่เองเมื่อ `som-db-0` Ready |
| `ImagePullBackOff` ของ `som-shop-web:1.2` หรือ `postgres:17.11-alpine` | ยังไม่ได้ load image เข้า Node (คลัสเตอร์ใหม่) | LAB 0 ขั้นที่ 6 |
| `provided port is already allocated` ตอน apply `20-web.yaml` | Service อื่นจอง 30080 (เช่น `som-shop` ของบทก่อนค้าง) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace ที่ค้าง |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080/api/stats` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| เวลาใน `first-born …` หรือ log postgres ช้ากว่านาฬิกา 7 ชั่วโมง | container ใช้ UTC | ปกติ |
| ลบ namespace `som-shop` ใช้เวลา ~30 วินาที | Pod web มี preStop 5 วินาทีและ grace period | ปกติ รอให้จบ |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `kubectl get sc` (`standard (default)`), `kubectl get pv,pvc -A` (`No resources found`) และ `crictl images` ที่เห็น `som-shop-web 1.2` + `postgres 17.11-alpine` บนทั้งสอง worker
- [ ] **LAB 1** ผลวนดูที่ Deployment เกิดพร้อมกันแต่ `web-0` เกิดก่อน `web-1/2`, `hostname`, `--show-labels` ของ `web-1` และผลหลังลบ Pod (ชื่อใหม่ของ Deployment, `web-1` ชื่อเดิม UID/IP ใหม่)
- [ ] **LAB 2** `CLUSTER-IP None`, `nslookup web` 3 Address และชื่อรายตัว 1 Address, หลังทำ `web-1` ไม่ Ready: 2 Address + `NXDOMAIN` ของชื่อเต็ม + `ready=false` ใน EndpointSlice
- [ ] **LAB 3** ผลวนดู Pod/PVC เกิดตามลำดับ, `kubectl get pvc --show-labels` (`www-web-0/1/2` `app=web`) และ `first-born web-1` เวลาเดิมหลังลบ Pod
- [ ] **LAB 4** `bad 0/3` + `bad-0 0/1` ไม่มี `bad-1` → หลัง `touch` มี `bad-1`, `par-0/1/2 Pending` วินาทีเดียวกัน และ scale web 3→1 ที่ `web-2 Terminating` ก่อน
- [ ] **LAB 5** `{"whenDeleted":"Retain","whenScaled":"Retain"}`, `first-born web-2` เดิมหลัง scale กลับ, `ownerReferences` ของ `www-par-0` เทียบ `www-web-0` และ PVC ของ `par` หายหลังลบ
- [ ] **LAB 6** `show.sh` ตอน partition 2 (`web-2` 1.28, `updated=1/3`) + `partitioned roll out complete: 1 new pods…`, ลำดับ `web-1` → `web-0` หลัง partition 0, `rollout history` (1, 2) และหลัง undo (2, 3)
- [ ] **LAB 7** ผลวนดูที่ Pod เปลี่ยนห่าง ~10 วินาที (`available=2`), `{"type":"OnDelete"}` + `error: rollout status is only available for RollingUpdate strategy type` และ `show.sh` ที่ `web-1` เป็น 1.27 ตัวเดียว
- [ ] **LAB 8** PVC 3 ใบ Bound หลัง `delete sts`, `first-born` เวลาเดิมหลัง apply ใหม่, `ownerReferences=[]` ของ Pod กำพร้า และ `StatefulSet/web` หลัง apply
- [ ] **LAB 9** ตารางเวลาของตัวเอง (NotReady, Terminating, ค้างนานเท่าไร), `deletionTimestamp … Ready=False`, `sts web 2/3`, `FailedScheduling … didn't match PersistentVolume's node affinity` หลังใส่ taint และ `first-born web-1` เดิมหลัง `docker start`
- [ ] **LAB 10** (1) ขั้น A `orders=3` + Service ClusterIP (2) error `may not change once set` จาก `--dry-run=server` (3) PV `Released` → `Available` → `Bound som-shop/data-som-db-0` และ Service `CLUSTER-IP None` (4) `orders=3` หลัง B2 + `wait-for-db` ที่ `som-db-0.som-db` (5) ขั้น C UID/IP ก่อน-หลัง + `claimName=data-som-db-0` (6) ขั้น D `768Mi` + REVISION 2 + `orders=4` (7) browser หน้าร้าน 4 ออเดอร์ (8) ขั้น E `503` ระหว่างไม่มี sts และ `orders=4` หลัง apply (9) ขั้น F `som-db-1/2: relation "orders" does not exist` + `nslookup som-db` 3 Address (10) ขั้น G PVC ค้างแล้วลบ (11) (เสริม) `t|4`, `primary: 5 replica: 5`, `streaming|async`, `read-only transaction`
- [ ] ท้ายสุด `kubectl get pv,pvc -A` ว่าง, `kubectl get ns` เหลือ 5 ตัวตั้งต้น และ `kubectl get nodes` 3 Ready ไม่มี taint

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Deployment `web-d`, StatefulSet `web` ของ LAB 1 | 1 | `kubectl get deploy,sts` | `cd …/labs/lab01-compare && kubectl delete -f web-deploy.yaml -f web-sts.yaml` |
| Pod `dns`, Service/StatefulSet `web` ของ LAB 2 | 2 | `kubectl get pod dns; kubectl get svc web` | `cd …/labs/lab02-headless && kubectl delete -f dns-pod.yaml -f sts.yaml -f svc-headless.yaml` |
| StatefulSet `bad`, `par` | 4, 5 | `kubectl get sts` | `kubectl delete sts bad par` (`par` ของ LAB 5 ลบ PVC ให้เอง) |
| StatefulSet/Service `web` + PVC `www-web-0/1/2` (ใช้ LAB 3–9) | 3–9 | `kubectl get sts,svc,pvc -l app=web; kubectl get svc web` | `cd …/labs/lab09-node-down && kubectl delete -f sts-tol.yaml` แล้ว `kubectl delete pvc -l app=web` |
| PVC `www-par-*` (ถ้าหยุดกลาง LAB 5) | 5 | `kubectl get pvc -l app=par` | `kubectl delete sts par` (whenDeleted: Delete) หรือ `kubectl delete pvc -l app=par` |
| Node ที่ถูก `docker stop` / taint `out-of-service` | 9 | `kubectl get nodes`; `kubectl describe node <node> \| grep -A2 Taints` | `kubectl taint node <node> node.kubernetes.io/out-of-service-` แล้ว `docker start <node>` รอ `Ready` |
| namespace `som-shop` (**จอง NodePort 30080**) + PVC `data-som-db-*`, `data-som-db-replica-0` | 10 | `kubectl get ns som-shop`; `kubectl -n som-shop get pvc` | `kubectl delete ns som-shop` |
| PV ที่ `Retain`/`Released` (ถ้าไม่ได้คืนเป็น Delete ในขั้น B2) และโฟลเดอร์ `pvc-…` บน Node | 10 | `kubectl get pv`; `docker exec <node> ls /var/local-path-provisioner/` | `kubectl delete pv <ชื่อ>`; `docker exec <node> rm -rf /var/local-path-provisioner/<โฟลเดอร์>` |
| image `som-shop-web:1.2`, postgres, nginx, busybox บน Node | 0–10 | `docker exec lab-worker crictl images` | **เก็บไว้ได้** (ใช้ซ้ำในบทถัดไป ถ้า `k8s-down` จะหายไปด้วย) |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl describe nodes | grep -E "^Name:|^Taints:"
kubectl get ns
kubectl get sts,pvc -A
kubectl get pv
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n ls /var/local-path-provisioner; done
```

ผลที่ถูกต้อง: 3 Node `Ready` และ worker ทั้งสองมี `Taints: <none>`, namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), ไม่มี StatefulSet/PVC/PV (`No resources found`) และโฟลเดอร์ `/var/local-path-provisioner` บน Node ว่าง

คลัสเตอร์ `lab` และ image ของร้านเก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ Pod, จำนวนออเดอร์ และเวลา) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริง 3 ภาพถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ (สร้างร้านใหม่ด้วย `kubectl apply -f k8s/` แล้วสั่งซื้อ 4 รายการ จากนั้นลบ Pod `som-db-0`, ลบ StatefulSet แล้ว apply ใหม่, scale เป็น 3 และกลับเป็น 1 แล้วสั่งซื้อผ่าน browser) ชื่อ Pod และลำดับออเดอร์ในภาพจึงต่างจากผลคำสั่งในขั้นหลักของเอกสาร
