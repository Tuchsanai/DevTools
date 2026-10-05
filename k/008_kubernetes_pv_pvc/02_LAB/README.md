# LAB บทที่ 8: PersistentVolume และ PVC — ตู้เซฟบนเรือ สู่ร้านน้องส้มที่จำออเดอร์ได้

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Volume และ Persistent Storage — emptyDir และ hostPath, PVC แรกจาก StorageClass (WaitForFirstConsumer), static PV และ `storageClassName: ""`, accessModes กับ local-path, วงจรชีวิต (finalizer, Delete, Retain, กู้ PV), StorageClass ของเราเอง (Retain/Immediate/expand), Node ล่มกับ local storage, ResourceQuota ของ storage, ephemeral volume, subPath/readOnly/fsGroup และร้านอาหารแมวน้องส้มที่ฐานข้อมูลจำออเดอร์ได้แม้ Pod ถูกสร้างใหม่
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะช่วยน้องส้มหา **ตู้เซฟ** ให้สมุดออเดอร์ของร้าน เริ่มจากที่เก็บแบบชั่วคราวที่รู้จักแล้ว (`emptyDir`) และช่องเปิดบนเรือ (`hostPath`) ต่อด้วยการเขียน **ใบเบิก (PVC)** ใบแรกให้ **โรงทำตู้อัตโนมัติ (StorageClass)** สร้างตู้ (PV) ให้ แล้วเปิดดูถึงโฟลเดอร์จริงบน Node สร้างตู้เองด้วยมือ ทดสอบว่าตู้แบบ local-path ทำอะไรได้และไม่ได้ ดูวงจรชีวิตของตู้ตั้งแต่ผูกจนถูกบดทิ้งหรือเก็บไว้ ลองหยุด Node ที่ตู้อยู่ และคุมงบพื้นที่ด้วย ResourceQuota ปิดท้ายด้วย **ร้านอาหารแมวน้องส้มที่จำได้แล้ว** (`som-shop-v4`) ซึ่งเปลี่ยน volume ของฐานข้อมูลจาก `emptyDir` เป็น PVC จุดเดียว แล้วพิสูจน์ว่าลบ Pod db, rollout restart db และลบ Deployment db ออเดอร์ก็ไม่หาย พร้อมทดลองสิ่งที่ **ห้ามทำ** กับฐานข้อมูล (scale เป็น 2) เพื่อเห็นความเสียหายจริง และกู้ข้อมูลจากตู้ที่เก็บไว้ (Retain)

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, Kubernetes v1.37.0, kubectl v1.37.1) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, ชื่อ PV (`pvc-<uid>`), Node ที่ Pod ถูกวาง, ขนาดดิสก์ และจำนวนวินาทีที่รอ ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ คำสั่งในเอกสารจึงดึงชื่อ PV/Node ใส่ตัวแปร (`PV=$(...)`, `N=$(...)`) แทนการพิมพ์ชื่อตายตัว

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิด browser ที่ `http://localhost:30080` ใน LAB 10 Node ของคลัสเตอร์ kind (`lab-control-plane`, `lab-worker`, `lab-worker2`) เป็น container ที่รันอยู่ **ข้างใน k8s-lab** คำสั่ง `docker exec lab-worker ...` (ดูโฟลเดอร์บน Node) และ `docker stop`/`docker start` ใน LAB 8 จึงรันใน SSH session ของ k8s-lab ไม่ใช่บนเครื่องนักศึกษา

### กติกาของ LAB บทนี้

- LAB 1–9 ทำในโฟลเดอร์ **`/workspace/008_kubernetes_pv_pvc/02_LAB/labs/labNN-...`** ของแต่ละ LAB ภายใน k8s-lab ส่วน LAB 10 ทำใน **`/workspace/008_kubernetes_pv_pvc/02_LAB/som-shop-v4`** ทุก LAB เริ่มด้วย `cd` ไปโฟลเดอร์ของตัวเอง
- LAB ส่วนใหญ่ใช้ namespace `default` ยกเว้น LAB 2 (`hostpath-lab`), LAB 9 ส่วนแรก (`quota-lab`) และ LAB 10 (`som-shop`) **ทุก LAB จบด้วยบล็อก "เก็บกวาด"** ที่ทำให้ `kubectl get pv,pvc -A` กลับมาว่าง ทำทุกครั้ง เพราะ PV ที่ค้างจะทำให้ผลของ LAB ถัดไปเพี้ยน
- **PV และ StorageClass ไม่มี namespace** ลบ namespace แล้วไม่หายตาม และ **โฟลเดอร์บน Node ของ hostPath, static PV และ PV ที่ Retain ไม่มีใครลบให้** บล็อกเก็บกวาดจึงมี `docker exec <node> rm -rf ...` ด้วย
- ชื่อ PV จาก StorageClass คือ `pvc-<uid>` ซึ่งสุ่มใหม่ทุกครั้ง คำสั่งจึงดึงชื่อด้วย `kubectl get pvc <ชื่อ> -o jsonpath='{.spec.volumeName}'` และหา Node ด้วย `.spec.nodeName` ของ Pod หรือ `nodeAffinity` ของ PV
- image สาธารณะ `busybox:1.36` ให้ Node ดึงเอง ไม่ต้อง `kind load` ส่วน `som-shop-web:1.2` ต้อง build เองและ `kind load` และ `postgres:17.11-alpine` ต้อง `docker save --platform` + `kind load image-archive` (LAB 0) ทั้งสองใช้เฉพาะ LAB 10
- Pod busybox ทุกตัวตั้ง `terminationGracePeriodSeconds: 1` ให้ลบแล้วหายเร็ว (`sh`/`sleep` ไม่รับ SIGTERM ถ้าไม่ใส่ต้องรอ 30 วินาที)
- `date` ใน Pod busybox และ log ของ postgres เป็นเวลา **UTC** (ช้ากว่าเวลาไทย 7 ชั่วโมง) ส่วน `date` ใน shell ของ k8s-lab เป็นเวลาไทย
- `kubectl logs` ทันทีหลัง `kubectl wait --for=condition=Ready` อาจยังได้ไม่ครบทุกบรรทัด ถ้าเห็นไม่ครบให้รอ 1–2 วินาทีแล้วสั่งใหม่
- **NodePort 30080 จองได้ทีละ Service ทั้งคลัสเตอร์** บทนี้ใช้ใน LAB 10 เท่านั้น ถ้ายังมี namespace `som-shop` ของบทที่ 7 ค้างอยู่ต้องลบก่อน (LAB 0 ขั้นที่ 4)
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง (ของจริงเก็บใน Secret ซึ่งเป็นเนื้อหาบทหลัง)
- **ขอบเขตของบทนี้:** ใช้ Pod, ReplicaSet, Deployment, Service, PV, PVC และ StorageClass ได้ทั้งหมด **ยังไม่ใช้ StatefulSet** (เนื้อหาบทที่ 9)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์ StorageClass และ image](#lab-0-เตรียมคลัสเตอร์-storageclass-และ-image) | 15–20 นาที | ⭐ |
| 1 | [emptyDir: อยู่เท่า Pod](#lab-1-emptydir-อยู่เท่า-pod) | 10 นาที | ⭐ |
| 2 | [hostPath: ข้อมูลอยู่บนเรือลำเดียว](#lab-2-hostpath-ข้อมูลอยู่บนเรือลำเดียว) | 10 นาที | ⭐ |
| 3 | [PVC แรกจาก StorageClass](#lab-3-pvc-แรกจาก-storageclass) | 15 นาที | ⭐⭐ |
| 4 | [Static PV และ storageClassName ""](#lab-4-static-pv-และ-storageclassname-) | 10 นาที | ⭐⭐ |
| 5 | [accessModes กับ local-path](#lab-5-accessmodes-กับ-local-path) | 15 นาที | ⭐⭐⭐ |
| 6 | [วงจรชีวิต: finalizer, Delete, Retain และกู้ PV](#lab-6-วงจรชีวิต-finalizer-delete-retain-และกู้-pv) | 15 นาที | ⭐⭐⭐ |
| 7 | [StorageClass ของเราเอง](#lab-7-storageclass-ของเราเอง) | 10 นาที | ⭐⭐⭐ |
| 8 | [Node ล่ม: ตู้เซฟติดเรือ](#lab-8-node-ล่ม-ตู้เซฟติดเรือ) | 10 นาที | ⭐⭐⭐⭐ |
| 9 | [งบพื้นที่, ephemeral, subPath/readOnly/fsGroup](#lab-9-งบพื้นที่-ephemeral-subpathreadonlyfsgroup) | 15 นาที | ⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มจำได้แล้ว](#lab-10-lab-สุดท้าย-ร้านน้องส้มจำได้แล้ว) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (ถ้าต้อง build image ของร้านใน LAB 0 เพิ่มอีกราว 5–10 นาที) ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านหัวข้อทฤษฎีที่เกี่ยวข้อง: LAB 1–2 → หัวข้อ 2, LAB 3 → หัวข้อ 3, 5, 7, LAB 4 → หัวข้อ 4, LAB 5 → หัวข้อ 6, LAB 6 → หัวข้อ 8, LAB 7 → หัวข้อ 5.2, 7.2, 9, LAB 8 → หัวข้อ 11, LAB 9 → หัวข้อ 10, 12, LAB 10 → หัวข้อ 13–14

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมคลัสเตอร์และ image](#fig-1) | 15 | [LAB 10 ขั้น A สั่งซื้อแรก](#fig-15) |
| 2 | [LAB 1 emptyDir อยู่เท่า Pod](#fig-2) | 16 | [ภาพหน้าจอจริง ร้านที่ db ใช้ PVC](#fig-16) |
| 3 | [LAB 2 hostPath อยู่บนเรือลำเดียว](#fig-3) | 17 | [LAB 10 ขั้น B–C ลบ Pod db และ restart](#fig-17) |
| 4 | [LAB 3 PVC แรก](#fig-4) | 18 | [LAB 10 ขั้น D ลบ Deployment db](#fig-18) |
| 5 | [LAB 3 ดูตู้บน Node](#fig-5) | 19 | [ภาพหน้าจอจริง หลังลบ Deployment db ออเดอร์ยังอยู่](#fig-19) |
| 6 | [LAB 4 Static PV](#fig-6) | 20 | [LAB 10 ขั้น E ดูไฟล์ postgres บน Node](#fig-20) |
| 7 | [LAB 5 accessModes](#fig-7) | 21 | [LAB 10 ขั้น F scale db เป็น 2](#fig-21) |
| 8 | [LAB 5 ขนาดไม่ถูกบังคับ](#fig-8) | 22 | [LAB 10 ขั้น F ผล: ข้อมูลเสีย](#fig-22) |
| 9 | [LAB 6 finalizer และ Delete](#fig-9) | 23 | [LAB 10 ขั้น G ลบ PVC](#fig-23) |
| 10 | [LAB 6 Retain และกู้ตู้](#fig-10) | 24 | [ภาพหน้าจอจริง ลบ PVC แล้ว 503](#fig-24) |
| 11 | [LAB 7 StorageClass ของเราเอง](#fig-11) | 25 | [ภาพหน้าจอจริง PVC ใหม่ ออเดอร์ 0](#fig-25) |
| 12 | [LAB 8 Node ล่ม](#fig-12) | 26 | [LAB 10 ขั้น H Retain + RWOP](#fig-26) |
| 13 | [LAB 9 quota, ephemeral, mount](#fig-13) | 27 | [LAB 10 ขั้น H2 กู้ตู้ที่ Retain](#fig-27) |
| 14 | [LAB 10 ภาพรวม som-shop-v4](#fig-14) | 28 | [สรุป LAB สุดท้าย](#fig-28) |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ 01–24 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
├── labs/                              ← YAML ของ LAB 1–9
│   ├── lab01-emptydir/pod.yaml                                   (Pod cache-demo: emptyDir ดิสก์ + Memory)
│   ├── lab02-hostpath/{00-ns,pod-worker,pod-worker2}.yaml        (namespace hostpath-lab, warn restricted)
│   ├── lab03-first-pvc/{pvc,pod}.yaml                            (PVC notes + Pod writer)
│   ├── lab04-static/{pv,pvc,pvc-too-big,pod}.yaml                (PV pv-manual 100Mi บน lab-worker2)
│   ├── lab05-access/{rwo,rwo-second,rwop,rwop-second,rwx,blk}.yaml
│   ├── lab06-lifecycle/{pvc,pod,pvc-reuse}.yaml                  (PVC ledger + Pod ledger-pod)
│   ├── lab07-storageclass/{sc-retain,sc-immediate,sc-expand}.yaml + {pvc-retain,pvc-standard,pvc-expand,pvc-immediate}.yaml
│   ├── lab08-node-down/nd.yaml                                   (PVC + Deployment Recreate + tolerationSeconds 30)
│   └── lab09-misc/{00-ns-quota,pvc-400,pvc-200,pvc-100,pvc-10,pod-mounts}.yaml
└── som-shop-v4/                       ← LAB 10 ร้านน้องส้มจำได้แล้ว
    ├── app/                           ← สำเนาแอป Next.js + Dockerfile จากบทที่ 7 (build เป็น som-shop-web:1.2)
    ├── k8s/{00-namespace,10-db,20-web}.yaml          ← db ใช้ PVC som-db-data (standard, RWO, 1Gi)
    ├── k8s-retain/{sc-retain,10-db,pvc-rescue}.yaml  ← ขั้น H: class standard-retain + PVC ReadWriteOncePod + ใบเบิกกู้ตู้
    └── hit.sh                         ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err
```

แอปร้านใน `som-shop-v4/app` เป็น **สำเนาเดียวกับบทที่ 7 โดยไม่แก้โค้ด** หัวหน้าเว็บจึงยังเขียน "⚓ ท่าเรือ Kubernetes · ReplicaSet + Service" (ข้อความตั้งต้นของแอปตั้งแต่บทที่ 6) ส่วน footer ถูกตั้งจาก env ใน `k8s/20-web.yaml` เป็น `Kubernetes LAB 008 · namespace som-shop`

---

## LAB 0: เตรียมคลัสเตอร์ StorageClass และ image

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมคลัสเตอร์และ image" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: เช็ก 3 Node Ready, StorageClass standard (default) และ local-path-provisioner Running, โหลด postgres:17.11-alpine ด้วย image-archive และ build som-shop-web:1.2 แล้ว kind load</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 7 หรือสร้างใหม่) ตรวจว่ามี StorageClass `standard` และ local-path-provisioner พร้อม ไม่มี PV/PVC หรือ NodePort 30080 ค้าง และมี image `som-shop-web:1.2` กับ `postgres:17.11-alpine` อยู่บน Node สำหรับ LAB 10

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md), [2](../../002_kubernetes_pod/02_LAB/README.md), [3](../../003_kubernetes_node_pod/02_LAB/README.md), [4](../../004_kubernetes_namespace/02_LAB/README.md), [5](../../005_kubernetes_replicaset/02_LAB/README.md), [6](../../006_kubernetes_service/02_LAB/README.md) และ [7](../../007_kubernetes_deployment/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `008_kubernetes_pv_pvc` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `008_kubernetes_pv_pvc` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 008_kubernetes_pv_pvc k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ บทนี้มีสำเนาแอปร้านน้องส้มของตัวเอง (`02_LAB/som-shop-v4/app`) จึง **ไม่ต้องมีโฟลเดอร์ของบทที่ 7** ใน container ก็ทำได้ครบ (การทดลองจริงคัดลอกเฉพาะโฟลเดอร์ของบทนี้)

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (ค่าตัวอย่างเพื่อการเรียน พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB
ls labs som-shop-v4
kubectl get nodes
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 7 ยังอยู่) | **ใช้ต่อได้เลย** ไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `k8s-up` (การทดลองใช้ราว 53 วินาที) image ที่เคย `kind load` ในบทก่อนจะหายไป ต้อง build/load ใหม่ในขั้นที่ 6 |

ผลจริงช่วงท้ายของ `k8s-up` บนคลัสเตอร์ใหม่

```text
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
  kubectl get pods -A                       # ดู pod ทั้งหมด (alias: k get pods -A)
  ...
  k8s-down                                  # ลบคลัสเตอร์
  NodePort ที่ map ออก host: 30080 30081 30082
```

```text
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   3m10s   v1.37.0
lab-worker          Ready    <none>          2m55s   v1.37.0
lab-worker2         Ready    <none>          2m55s   v1.37.0
```

### ขั้นที่ 4: ตรวจของที่ค้างจากบทก่อน

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get ns
kubectl get svc -A | grep -E '3008[0-2]' || echo '(ไม่มี Service ใช้ 30080-30082)'
kubectl get pv,pvc -A
```

ผลจริงบนคลัสเตอร์ใหม่ของ `kubectl get pv,pvc -A`

```text
No resources found
```

ที่ถูกต้องคือ namespace มีแค่ 5 ตัวตั้งต้น (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), ไม่มี Service ใช้ 30080–30082 และไม่มี PV/PVC ถ้ายังเห็น namespace `som-shop` จากบทที่ 7 ให้ลบก่อน (`kubectl delete ns som-shop`) เพราะจองพอร์ต 30080 ไว้

### ขั้นที่ 5: ตรวจ StorageClass และ local-path-provisioner

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get sc
kubectl get sc standard -o yaml | grep -E "is-default|provisioner|reclaimPolicy|volumeBindingMode|allowVolume"
```

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  3m6s
```

```text
      {"apiVersion":"storage.k8s.io/v1","kind":"StorageClass","metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"},"name":"standard"},"provisioner":"rancher.io/local-path","reclaimPolicy":"Delete","volumeBindingMode":"WaitForFirstConsumer"}
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

บรรทัดแรกคือ annotation `last-applied-configuration` ที่ kind ใช้สร้าง class นี้ ส่วนบรรทัดถัดมาคือค่าจริง ไม่มีบรรทัด `allowVolumeExpansion` เพราะไม่ได้ตั้ง (= `false`) ต่อด้วยตัว provisioner และที่เก็บโฟลเดอร์ของตู้

```bash
kubectl -n local-path-storage get pod -o wide; kubectl -n local-path-storage get deploy -o jsonpath="{..image}{\"\n\"}"
kubectl -n local-path-storage get cm local-path-config -o jsonpath="{.data.config\.json}"; echo
docker exec lab-worker ls -la /var/local-path-provisioner 2>&1
```

```text
NAME                                      READY   STATUS    RESTARTS   AGE    IP           NODE                NOMINATED NODE   READINESS GATES
local-path-provisioner-75f7fc7dc5-5dkx2   1/1     Running   0          3m1s   10.244.0.4   lab-control-plane   <none>           <none>
docker.io/kindest/local-path-provisioner:v20260820-69b56db7
{
        "nodePathMap":[
        {
                "node":"DEFAULT_PATH_FOR_NON_LISTED_NODES",
                "paths":["/var/local-path-provisioner"]
        }
        ]
}
ls: cannot access '/var/local-path-provisioner': No such file or directory
```

- provisioner 1 Pod รันบน `lab-control-plane` ทุก Node ใช้ path เดียวกัน `/var/local-path-provisioner`
- โฟลเดอร์นี้ **ยังไม่มีบน Node** เพราะยังไม่เคยมี PV (จะถูกสร้างเมื่อมีตู้แรกใน LAB 3) ถ้าใช้คลัสเตอร์เดิมที่เคยมี PV มาก่อนอาจเห็นโฟลเดอร์ว่างแทน

### ขั้นที่ 6: ตรวจ image ของร้านบน Node (ถ้าไม่มีให้ build และ load)

LAB 10 ใช้ `som-shop-web:1.2` ที่ build เอง (ไม่มีใน Docker Hub) และ `postgres:17.11-alpine` ถ้าใช้คลัสเตอร์เดิมจากบทที่ 7 image เหล่านี้น่าจะยังอยู่ ตรวจด้วย `crictl` ภายใน Node

🐧 **ใน SSH session ของ k8s-lab**

```bash
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "postgres|som-shop-web"; done
```

ถ้าเห็นทั้ง `postgres 17.11-alpine` และ `som-shop-web 1.2` บนทั้งสอง worker **ข้ามไปขั้นที่ 7 ได้เลย** (บทนี้ไม่ใช้ `som-shop-web:1.3` ถ้ามีอยู่ก็ไม่เป็นไร) ถ้าไม่เห็น (คลัสเตอร์ใหม่) ให้เตรียมดังนี้

**postgres** เป็น image หลาย platform จึงใช้ `docker save --platform` + `kind load image-archive` (ไฟล์ `pg.tar` ชั่วคราวอยู่ใน `02_LAB/` แล้วลบทิ้ง)

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o pg.tar && kind load image-archive pg.tar --name lab) 2>&1 | tail -6; rm -f pg.tar
```

```text
docker.io/library/postgres:17.11-alpine

real	0m17.276s
user	0m0.278s
sys	0m0.786s
```

**som-shop-web:1.2** build จาก **สำเนาแอปในบทนี้** แล้ว `kind load` ให้ทุก Node

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/som-shop-v4/app
time docker build -q --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 . 2>&1 | tail -3
time kind load docker-image som-shop-web:1.2 --name lab 2>&1 | tail -3
```

```text
sha256:b2d17517eacf809dad53606e209c7f44d702787e5b516769d40e491701f1386a

real	0m30.033s
...
Image: "som-shop-web:1.2" with ID "sha256:b2d17517eacf809dad53606e209c7f44d702787e5b516769d40e491701f1386a" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.2" with ID "sha256:b2d17517eacf809dad53606e209c7f44d702787e5b516769d40e491701f1386a" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.2" with ID "sha256:b2d17517eacf809dad53606e209c7f44d702787e5b516769d40e491701f1386a" not yet present on node "lab-worker", loading...

real	0m5.347s
```

ตรวจซ้ำด้วยคำสั่ง `crictl` ด้านบน ผลจริงหลัง load

```text
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  fc97d28600ddf       76.6MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  fc97d28600ddf       76.6MB
```

build ใช้ราว 30 วินาที (ดาวน์โหลด dependency และคอมไพล์ เครื่องนักศึกษาอาจนานกว่านี้หลายเท่า) ค่า sha256 และ IMAGE ID ในเครื่องนักศึกษาจะต่างจากตัวอย่าง

> **ข้อควรระวัง:** ทำขั้นนี้ **ตอนที่ Node ครบ 3 ตัวและ Ready** เท่านั้น อย่า `kind load` ระหว่างที่ Node ถูก `docker stop` ใน LAB 8 (pre-check พบ error `failed to detect containerd snapshotter`)

### ขั้นที่ 7: กลับโฟลเดอร์ LAB

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB
pwd
```

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node พร้อม มี StorageClass เดียวคือ `standard (default)` = `rancher.io/local-path`, `Delete`, `WaitForFirstConsumer`, ขยายไม่ได้ (`false`)
- provisioner รันใน namespace `local-path-storage` และยังไม่มี PV/PVC หรือโฟลเดอร์ `/var/local-path-provisioner` บน Node
- `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บน Node (ตรวจด้วย `crictl images`)

**คำถามชวนคิด**

1. ทำไม `busybox:1.36` จึงไม่ต้อง `kind load` แต่ `som-shop-web:1.2` ต้อง load
2. ถ้าคลัสเตอร์ไม่มี default StorageClass เลย PVC ที่ไม่ใส่ `storageClassName` จะเป็นอย่างไร (เทียบกับ PVC `too-big` ใน LAB 4)

---

## LAB 1: emptyDir: อยู่เท่า Pod

<p align="center" id="fig-2">
  <img src="images/02-lab1-emptydir.png" alt="รูปที่ 2 LAB 1 emptyDir อยู่เท่า Pod" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: เขียนไฟล์ลง emptyDir → kubectl exec ... touch /tmp/stop ให้ container restart (RESTARTS 1) ไฟล์ใน emptyDir ยังอยู่ แต่ไฟล์ใน /tmp หาย → ลบ Pod แล้วสร้างใหม่ ไฟล์หาย</em>
</p>

**เป้าหมาย:** เห็นอายุของข้อมูล 3 แบบในการทดลองเดียว ไฟล์ใน container (`/tmp`), `emptyDir` บนดิสก์ (`/cache`) และ `emptyDir` ใน RAM (`/ram`) เมื่อ container restart และเมื่อ Pod ถูกสร้างใหม่

**ไฟล์:** `lab01-emptydir/pod.yaml` — Pod `cache-demo` (busybox) บันทึกเวลาเริ่มลง `/cache/boot.log` แล้ววนรอจนมีไฟล์ `/tmp/stop` จึง `exit 1` มี volume `cache` (`emptyDir: {}`) และ `ram` (`medium: Memory`, `sizeLimit: 16Mi`)

### ขั้นที่ 1: สร้าง Pod และเขียนไฟล์ 3 ที่

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab01-emptydir
kubectl apply -f pod.yaml && kubectl wait --for=condition=Ready pod/cache-demo --timeout=90s && kubectl get pod cache-demo -o wide
```

```text
pod/cache-demo created
pod/cache-demo condition met
NAME         READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
cache-demo   1/1     Running   0          6s    10.244.2.2   lab-worker   <none>           <none>
```

```bash
kubectl exec cache-demo -- sh -c "echo hi-from-emptydir > /cache/x.txt; echo hi-from-container > /tmp/y.txt; echo ram > /ram/r.txt; ls /cache /tmp /ram; cat /cache/boot.log"
kubectl exec cache-demo -- df -h /cache /ram
```

```text
/cache:
boot.log
x.txt

/ram:
r.txt

/tmp:
y.txt
start 05:38:03
Filesystem                Size      Used Available Use% Mounted on
/dev/sdd               1006.9G    224.5G    731.1G  23% /cache
tmpfs                    16.0M      4.0K     16.0M   0% /ram
```

`/cache` อยู่บนดิสก์ของ Node (ขนาดคือดิสก์ทั้งก้อนของเครื่องทดสอบ ของนักศึกษาจะต่างกัน) ส่วน `/ram` เป็น `tmpfs` ขนาด 16.0M ตาม `sizeLimit` เวลาใน `boot.log` เป็น UTC

### ขั้นที่ 2: ลอง kill 1 (ไม่ได้ผล)

```bash
kubectl exec cache-demo -- kill 1; sleep 3; kubectl get pod cache-demo
kubectl exec cache-demo -- kill -9 1; sleep 3; kubectl get pod cache-demo
```

```text
NAME         READY   STATUS    RESTARTS   AGE
cache-demo   1/1     Running   0          9s
NAME         READY   STATUS    RESTARTS   AGE
cache-demo   1/1     Running   0          13s
```

`RESTARTS` ยังเป็น 0 ทั้งสองครั้ง `sh` ที่เป็น PID 1 ใน container ไม่ถูกปิดด้วยสัญญาณที่ไม่มี handler (แม้ `-9`) จึงใช้วิธีของขั้นถัดไปแทน

### ขั้นที่ 3: ทำให้ container จบเองด้วย touch /tmp/stop

```bash
kubectl exec cache-demo -- touch /tmp/stop; sleep 4; kubectl get pod cache-demo
kubectl exec cache-demo -- sh -c "ls /cache /tmp /ram; cat /cache/x.txt /cache/boot.log"
```

```text
NAME         READY   STATUS    RESTARTS     AGE
cache-demo   1/1     Running   1 (3s ago)   21s
/cache:
boot.log
x.txt

/ram:
r.txt

/tmp:
hi-from-emptydir
start 05:38:03
start 05:38:16
```

- `RESTARTS 1 (3s ago)` — loop เจอ `/tmp/stop` แล้ว `exit 1` kubelet จึงเริ่ม container ใหม่ (Pod เดิม ชื่อเดิม IP เดิม)
- `/tmp` **ว่าง** (`y.txt` และ `stop` หายไปกับ container เดิม จึงไม่วน restart ซ้ำ) แต่ `/cache/x.txt` และ `/ram/r.txt` **ยังอยู่** และ `boot.log` มี 2 บรรทัด

ดูเหตุผลที่ container เดิมจบ

```bash
kubectl logs cache-demo --previous; kubectl get pod cache-demo -o jsonpath="{.status.containerStatuses[0].lastState}{\"\n\"}"
```

```text
เจอ /tmp/stop → จบ process (kubelet จะเริ่ม container ใหม่)
{"terminated":{"containerID":"containerd://e936df6bcb73f21707e5bd92096be9667e27a3d410cbf7ac54758ddb417e72bb","exitCode":1,"finishedAt":"2026-10-05T05:38:15Z","reason":"Error","startedAt":"2026-10-05T05:38:03Z"}}
```

### ขั้นที่ 4: ลบ Pod แล้วสร้างใหม่

```bash
kubectl delete pod cache-demo && kubectl apply -f pod.yaml && kubectl wait --for=condition=Ready pod/cache-demo --timeout=90s && kubectl exec cache-demo -- sh -c "ls -la /cache; cat /cache/boot.log"; kubectl get pod cache-demo -o wide
```

```text
pod "cache-demo" deleted from default namespace
pod/cache-demo created
pod/cache-demo condition met
total 12
drwxrwxrwx    2 root     root          4096 Oct  5 05:38 .
drwxr-xr-x    1 root     root          4096 Oct  5 05:38 ..
-rw-r--r--    1 root     root            15 Oct  5 05:38 boot.log
start 05:38:23
NAME         READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
cache-demo   1/1     Running   0          2s    10.244.2.3   lab-worker   <none>           <none>
```

Pod ใหม่ได้ `emptyDir` ใหม่ที่ว่าง `x.txt` หายไป `boot.log` เหลือบรรทัดเดียว (แม้จะลง Node เดิมก็ตาม เพราะ emptyDir ผูกกับ Pod ไม่ใช่ Node)

### ขั้นที่ 5: เก็บกวาด

```bash
kubectl delete -f pod.yaml
```

```text
pod "cache-demo" deleted from default namespace
```

### สิ่งที่เห็น

- container restart: ไฟล์ใน container หาย, `emptyDir` (ดิสก์และ RAM) อยู่
- ลบ Pod แล้วสร้างใหม่: `emptyDir` หายทั้งหมด → ฐานข้อมูลของบทที่ 7 จึงหายทุกครั้งที่ Pod db เกิดใหม่
- `kill 1`/`kill -9 1` ใน busybox ไม่ทำให้ container ตาย

**คำถามชวนคิด**

1. ถ้าเขียนไฟล์ 20Mi ลง `/ram` (ซึ่ง `sizeLimit: 16Mi`) คาดว่าจะเกิดอะไรกับ Pod และข้อมูลใน RAM ถูกนับเป็นทรัพยากรอะไรของ container
2. initContainer `db-seed` ของร้านน้องส้มกับ container `web` อยู่ใน Pod เดียวกัน ถ้าต้องส่งไฟล์ให้กัน ควรใช้ volume ชนิดใด เพราะอะไร

---

## LAB 2: hostPath: ข้อมูลอยู่บนเรือลำเดียว

<p align="center" id="fig-3">
  <img src="images/03-lab2-hostpath.png" alt="รูปที่ 3 LAB 2 hostPath อยู่บนเรือลำเดียว" width="900"><br>
  <em><b>รูปที่ 3</b> LAB2: Pod hostPath ปักไว้ lab-worker เขียนไฟล์ → docker exec lab-worker เห็นไฟล์ → ย้าย Pod ไป lab-worker2 ไม่เห็นไฟล์; namespace ที่ warn restricted เตือน hostPath</em>
</p>

**เป้าหมาย:** เห็นว่า `hostPath` เก็บข้อมูลบน Node ลำเดียว อยู่รอดเมื่อ Pod/namespace ถูกลบ (ไม่มีใครเก็บกวาด) และถูก Pod Security ระดับ restricted เตือน

**ไฟล์:** `lab02-hostpath/00-ns.yaml` (namespace `hostpath-lab` ติดป้าย `pod-security.kubernetes.io/warn: restricted`), `pod-worker.yaml` (Pod `hp-worker` ปักที่ `lab-worker`), `pod-worker2.yaml` (Pod `hp-worker2` ปักที่ `lab-worker2`) ทั้งสองเขียนต่อท้าย `/host/notes.txt` (= `/srv/som-hostpath` บน Node) แล้วแสดงทั้งไฟล์ใน log

### ขั้นที่ 1: Pod บน lab-worker เขียนไฟล์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab02-hostpath
kubectl apply -f 00-ns.yaml -f pod-worker.yaml
```

```text
namespace/hostpath-lab created
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "app" must set securityContext.capabilities.drop=["ALL"]), restricted volume types (volume "host" uses restricted volume type "hostPath"), runAsNonRoot != true (pod or container "app" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "app" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/hp-worker created
```

Warning ระบุ `restricted volume types (volume "host" uses restricted volume type "hostPath")` (ข้ออื่นเป็นเรื่อง securityContext แบบบทที่ 4) แต่ Pod ยังถูกสร้างเพราะ namespace ตั้งแค่ `warn` ถ้าเป็น `enforce` จะถูกปฏิเสธ

```bash
kubectl -n hostpath-lab wait --for=condition=Ready pod/hp-worker --timeout=90s; kubectl -n hostpath-lab get pod -o wide; kubectl -n hostpath-lab logs hp-worker
docker exec lab-worker ls -la /srv/som-hostpath; docker exec lab-worker cat /srv/som-hostpath/notes.txt
```

```text
pod/hp-worker condition met
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
hp-worker   1/1     Running   0          1s    10.244.2.4   lab-worker   <none>           <none>
05:38:36 from hp-worker on lab-worker
total 12
drwxr-xr-x 2 root root 4096 Oct  5 05:38 .
drwxr-xr-x 1 root root 4096 Oct  5 05:38 ..
-rw-r--r-- 1 root root   38 Oct  5 05:38 notes.txt
05:38:36 from hp-worker on lab-worker
```

ไฟล์ที่ Pod เขียนอยู่บน Node จริง (`docker exec lab-worker` คือเข้าไปใน container ของ Node) โฟลเดอร์ที่ `DirectoryOrCreate` สร้างเป็น `drwxr-xr-x root`

### ขั้นที่ 2: Pod บน lab-worker2 ใช้ path เดียวกัน

```bash
kubectl apply -f pod-worker2.yaml; kubectl -n hostpath-lab wait --for=condition=Ready pod/hp-worker2 --timeout=90s; kubectl -n hostpath-lab get pod -o wide; kubectl -n hostpath-lab logs hp-worker2
docker exec lab-worker2 cat /srv/som-hostpath/notes.txt; docker exec lab-worker cat /srv/som-hostpath/notes.txt
```

```text
Warning: would violate PodSecurity "restricted:latest": ... restricted volume types (volume "host" uses restricted volume type "hostPath"), ...
pod/hp-worker2 created
pod/hp-worker2 condition met
NAME         READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
hp-worker    1/1     Running   0          7s    10.244.2.4   lab-worker    <none>           <none>
hp-worker2   1/1     Running   0          6s    10.244.1.2   lab-worker2   <none>           <none>
05:38:42 from hp-worker2 on lab-worker2
05:38:42 from hp-worker2 on lab-worker2
05:38:36 from hp-worker on lab-worker
```

`hp-worker2` เห็นเฉพาะบรรทัดของตัวเอง **ไม่เห็นไฟล์ที่ `hp-worker` เขียน** เพราะ `/srv/som-hostpath` ของ `lab-worker2` เป็นคนละโฟลเดอร์กับของ `lab-worker` (คนละเรือ)

### ขั้นที่ 3: ลบ Pod แล้วสร้างใหม่บน Node เดิม

```bash
kubectl -n hostpath-lab delete pod hp-worker; kubectl apply -f pod-worker.yaml; kubectl -n hostpath-lab wait --for=condition=Ready pod/hp-worker --timeout=90s; kubectl -n hostpath-lab logs hp-worker
```

```text
pod "hp-worker" deleted from hostpath-lab namespace
Warning: would violate PodSecurity "restricted:latest": ...
pod/hp-worker created
pod/hp-worker condition met
05:38:36 from hp-worker on lab-worker
05:38:46 from hp-worker on lab-worker
```

ต่างจาก `emptyDir` ใน LAB 1 Pod ใหม่บน Node เดิมเห็นบรรทัดเก่าด้วย เพราะข้อมูลอยู่บน Node ไม่ได้อยู่กับ Pod

### ขั้นที่ 4: ลบ namespace แล้วไฟล์บน Node ยังอยู่ (เก็บกวาด)

```bash
time kubectl delete ns hostpath-lab; docker exec lab-worker cat /srv/som-hostpath/notes.txt
```

```text
namespace "hostpath-lab" deleted

real	0m10.508s
...
05:38:36 from hp-worker on lab-worker
05:38:46 from hp-worker on lab-worker
```

ลบ namespace แล้วไฟล์ยังอยู่บน Node ไม่มีใครลบให้ ต้องลบเองบนทุก Node ที่เคยใช้

```bash
for n in lab-worker lab-worker2; do docker exec $n rm -rf /srv/som-hostpath; done; docker exec lab-worker ls /srv
```

คำสั่งสุดท้ายไม่แสดงอะไร (ใน `/srv` ไม่เหลืออะไร) แปลว่าเก็บกวาดเรียบร้อย

### สิ่งที่เห็น

- `hostPath` เขียนลงโฟลเดอร์ของ Node ตรง ๆ เห็นได้ด้วย `docker exec <node>`
- ข้อมูลผูกกับ Node: Pod บน Node อื่นไม่เห็น, Pod ใหม่บน Node เดิมเห็น
- ลบ Pod/namespace แล้วไฟล์ยังอยู่ และ Pod Security restricted เตือน `restricted volume type "hostPath"`

**คำถามชวนคิด**

1. ถ้าลบ `nodeSelector` ออกจาก `pod-worker.yaml` แล้วสร้าง Pod ใหม่หลายครั้ง ผลใน `notes.txt` ที่ Pod เห็นจะคงที่หรือไม่ เพราะอะไร
2. ถ้า namespace ตั้ง `pod-security.kubernetes.io/enforce: restricted` คำสั่ง apply ในขั้นที่ 1 จะให้ผลต่างไปอย่างไร

---

## LAB 3: PVC แรกจาก StorageClass

<p align="center" id="fig-4">
  <img src="images/04-lab3-first-pvc.png" alt="รูปที่ 4 LAB 3 PVC แรก" width="900"><br>
  <em><b>รูปที่ 4</b> LAB3: สร้าง PVC notes → Pending (WaitForFirstConsumer) → สร้าง Pod writer → Bound กับ PV pvc-&lt;uid&gt; บน Node ที่ Pod ลง; ลบ Pod สร้างใหม่ ข้อมูลยังอยู่</em>
</p>

**เป้าหมาย:** เขียนใบเบิกใบแรก เห็น dynamic provisioning และ `WaitForFirstConsumer` ตั้งแต่ `Pending` จน `Bound` อ่าน Events, annotation และ PV ที่ provisioner สร้าง แล้วเปิดดูตู้จริงบน Node และพิสูจน์ว่าข้อมูลอยู่รอดเมื่อ Pod ถูกสร้างใหม่

**ไฟล์:** `lab03-first-pvc/pvc.yaml` (PVC `notes` 10Mi RWO ไม่ระบุ class), `lab03-first-pvc/pod.yaml` (Pod `writer` เขียนต่อท้าย `/data/log.txt` ทุกครั้งที่เริ่ม แล้วแสดงไฟล์และสิทธิ์ของ `/data`)

### ขั้นที่ 1: สร้าง PVC ก่อน (ยังไม่มี Pod)

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab03-first-pvc
kubectl apply -f pvc.yaml; sleep 3; kubectl get pvc; kubectl get pv
kubectl describe pvc notes | sed -n "1,40p"
```

```text
persistentvolumeclaim/notes created
NAME    STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
notes   Pending                                      standard       <unset>                 3s
No resources found
Name:          notes
Namespace:     default
StorageClass:  standard
Status:        Pending
Volume:        
Labels:        <none>
Annotations:   <none>
Finalizers:    [kubernetes.io/pvc-protection]
Capacity:      
Access Modes:  
VolumeMode:    Filesystem
Used By:       <none>
Events:
  Type    Reason                Age   From                         Message
  ----    ------                ----  ----                         -------
  Normal  WaitForFirstConsumer  3s    persistentvolume-controller  waiting for first consumer to be created before binding
```

- ไฟล์ไม่ได้เขียน `storageClassName` แต่คอลัมน์ `STORAGECLASS` เป็น `standard` เพราะ default class ถูกใส่ให้ตอนสร้าง
- `Pending` **ไม่ใช่ error** Event `WaitForFirstConsumer` บอกว่ารอ Pod ตัวแรก และยังไม่มี PV เลย
- PVC มี finalizer `kubernetes.io/pvc-protection` ตั้งแต่เกิด (ใช้ใน LAB 6)

### ขั้นที่ 2: สร้าง Pod ที่ใช้ใบเบิก

```bash
kubectl apply -f pod.yaml; kubectl wait --for=condition=Ready pod/writer --timeout=90s; kubectl get pvc,pv -o wide; kubectl get pod writer -o wide
```

```text
pod/writer created
pod/writer condition met
NAME                          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   VOLUMEMODE
persistentvolumeclaim/notes   Bound    pvc-b4fb1995-3929-4c26-930e-08074d960afb   10Mi       RWO            standard       <unset>                 8s    Filesystem

NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM           STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE   VOLUMEMODE
persistentvolume/pvc-b4fb1995-3929-4c26-930e-08074d960afb   10Mi       RWO            Delete           Bound    default/notes   standard       <unset>                          2s    Filesystem
NAME     READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
writer   1/1     Running   0          5s    10.244.2.7   lab-worker   <none>           <none>
```

```bash
kubectl logs writer; kubectl describe pvc notes | tail -8
```

```text
05:39:14 hello from writer
drwxrwxrwx    2 root     root          4096 Oct  5 05:39 /data
  Unused   False   Mon, 01 Jan 0001 00:00:00 +0000   Mon, 05 Oct 2026 12:39:12 +0700   PodUsingPVC   A pod is currently referencing this PVC
Events:
  Type    Reason                 Age   From                                                                                                Message
  ----    ------                 ----  ----                                                                                                -------
  Normal  WaitForFirstConsumer   8s    persistentvolume-controller                                                                         waiting for first consumer to be created before binding
  Normal  ExternalProvisioning   5s    persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
  Normal  Provisioning           5s    rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  External provisioner is provisioning volume for claim "default/notes"
  Normal  ProvisioningSucceeded  2s    rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  Successfully provisioned volume pvc-b4fb1995-3929-4c26-930e-08074d960afb
```

- PV `pvc-b4fb1995-…` เกิด **หลัง** Pod ถูกสร้าง (AGE ของ PV 2s, ของ PVC 8s) ใช้เวลาสร้างราว 3 วินาที Pod Ready ราว 5 วินาที
- reclaimPolicy ของ PV เป็น `Delete` ตาม class ชื่อ PV คือ `pvc-` + uid ของ PVC ของนักศึกษาจะเป็นค่าอื่น
- `/data` ใน Pod เป็น `drwxrwxrwx root` (โฟลเดอร์ที่ local-path สร้าง) และ PVC มี Condition `Unused False … PodUsingPVC` (ใหม่ใน v1.37)

### ขั้นที่ 3: อ่าน annotation และ PV ที่ได้

```bash
kubectl describe pvc notes | sed -n "1,20p"
PV=$(kubectl get pvc notes -o jsonpath="{.spec.volumeName}"); echo PV=$PV; kubectl get pv $PV -o yaml | sed -n "/^spec:/,\$p"; kubectl get pv $PV -o jsonpath="{.metadata.finalizers}{\"\n\"}"
```

```text
Name:          notes
Namespace:     default
StorageClass:  standard
Status:        Bound
Volume:        pvc-b4fb1995-3929-4c26-930e-08074d960afb
Labels:        <none>
Annotations:   pv.kubernetes.io/bind-completed: yes
               pv.kubernetes.io/bound-by-controller: yes
               volume.beta.kubernetes.io/storage-provisioner: rancher.io/local-path
               volume.kubernetes.io/selected-node: lab-worker
               volume.kubernetes.io/storage-provisioner: rancher.io/local-path
Finalizers:    [kubernetes.io/pvc-protection]
Capacity:      10Mi
Access Modes:  RWO
VolumeMode:    Filesystem
Used By:       writer
...
PV=pvc-b4fb1995-3929-4c26-930e-08074d960afb
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 10Mi
  claimRef:
    apiVersion: v1
    kind: PersistentVolumeClaim
    name: notes
    namespace: default
    resourceVersion: "1203"
    uid: b4fb1995-3929-4c26-930e-08074d960afb
  hostPath:
    path: /var/local-path-provisioner/pvc-b4fb1995-3929-4c26-930e-08074d960afb_default_notes
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - lab-worker
  persistentVolumeReclaimPolicy: Delete
  storageClassName: standard
  volumeMode: Filesystem
status:
  lastPhaseTransitionTime: "2026-10-05T05:39:12Z"
  phase: Bound
["kubernetes.io/pv-protection"]
```

| สิ่งที่เห็น | ความหมาย |
|---|---|
| `volume.kubernetes.io/selected-node: lab-worker` | scheduler เลือก Node ให้ Pod แล้วบอก provisioner ให้สร้างตู้บน Node นี้ |
| `claimRef.uid` = ส่วนท้ายของชื่อ PV | PV ชื่อ `pvc-<uid ของ PVC>` |
| `hostPath.path: /var/local-path-provisioner/pvc-…_default_notes` | ตู้จริงคือโฟลเดอร์ `pvc-<uid>_<namespace>_<pvc>` บน Node |
| `nodeAffinity … values: [lab-worker]` | Pod ที่ใช้ตู้นี้ต้องลง `lab-worker` เสมอ |
| finalizer `kubernetes.io/pv-protection` | กัน PV ถูกลบระหว่างที่ยังผูกอยู่ |

### ขั้นที่ 4: เปิดดูตู้บน Node

<p align="center" id="fig-5">
  <img src="images/05-lab3-peek-node.png" alt="รูปที่ 5 LAB 3 ดูตู้บน Node" width="900"><br>
  <em><b>รูปที่ 5</b> LAB3 (ต่อ): ดู PV ด้วย kubectl get pv -o yaml (hostPath + nodeAffinity) แล้ว docker exec lab-worker ls /var/local-path-provisioner เห็นโฟลเดอร์ pvc-&lt;uid&gt;_default_notes</em>
</p>

ใช้ Node ที่ Pod อยู่จริง (ของนักศึกษาอาจเป็น `lab-worker2`)

```bash
N=$(kubectl get pod writer -o jsonpath="{.spec.nodeName}"); echo N=$N; docker exec $N ls -la /var/local-path-provisioner/; docker exec $N sh -c "cat /var/local-path-provisioner/*_default_notes/log.txt"
```

```text
N=lab-worker
total 12
drwxr-xr-x  3 root root 4096 Oct  5 05:39 .
drwxr-xr-x 12 root root 4096 Oct  5 05:39 ..
drwxrwxrwx  2 root root 4096 Oct  5 05:39 pvc-b4fb1995-3929-4c26-930e-08074d960afb_default_notes
05:39:14 hello from writer
```

โฟลเดอร์ `/var/local-path-provisioner` เพิ่งถูกสร้างพร้อมตู้แรก และไฟล์ที่ Pod เขียนอยู่ในโฟลเดอร์ของตู้จริง

### ขั้นที่ 5: ลบ Pod แล้วสร้างใหม่ ข้อมูลยังอยู่

```bash
kubectl delete pod writer; kubectl get pvc notes; kubectl apply -f pod.yaml; kubectl wait --for=condition=Ready pod/writer --timeout=90s; kubectl get pod writer -o wide; kubectl logs writer
```

```text
pod "writer" deleted from default namespace
NAME    STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
notes   Bound    pvc-b4fb1995-3929-4c26-930e-08074d960afb   10Mi       RWO            standard       <unset>                 18s
pod/writer created
pod/writer condition met
NAME     READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
writer   1/1     Running   0          1s    10.244.2.8   lab-worker   <none>           <none>
05:39:14 hello from writer
05:39:24 hello from writer
drwxrwxrwx    2 root     root          4096 Oct  5 05:39 /data
```

ลบ Pod แล้ว PVC ยัง `Bound` Pod ใหม่ (IP ใหม่) ลง **Node เดิม** ตาม nodeAffinity ของ PV และเห็นบรรทัดเก่าต่อด้วยบรรทัดใหม่ ต่างจาก `emptyDir` ใน LAB 1

### ขั้นที่ 6: เก็บกวาด

```bash
kubectl delete -f pod.yaml -f pvc.yaml; sleep 5; kubectl get pvc,pv; docker exec lab-worker ls -la /var/local-path-provisioner/
```

```text
pod "writer" deleted from default namespace
persistentvolumeclaim "notes" deleted from default namespace
No resources found
total 8
drwxr-xr-x  2 root root 4096 Oct  5 05:39 .
drwxr-xr-x 12 root root 4096 Oct  5 05:39 ..
```

ลบ PVC แล้ว PV (Delete) และโฟลเดอร์ของตู้ถูกลบอัตโนมัติ (ถ้า Pod ของนักศึกษาอยู่ `lab-worker2` ให้เปลี่ยนชื่อ Node ในคำสั่ง `ls` หรือใช้ `$N`)

### สิ่งที่เห็น

- PVC `Pending` (WaitForFirstConsumer) → มี Pod → `ExternalProvisioning` → `ProvisioningSucceeded` → `Bound`
- PV ชื่อ `pvc-<uid>` เป็น hostPath ที่ `/var/local-path-provisioner/pvc-<uid>_default_notes` + nodeAffinity ของ Node ที่ Pod ลง
- ลบ Pod แล้วข้อมูลยังอยู่ Pod ใหม่ลง Node เดิม ลบ PVC แล้ว PV และโฟลเดอร์หาย

**คำถามชวนคิด**

1. ถ้าสร้าง Pod `writer` ก่อนแล้วค่อยสร้าง PVC `notes` จะเห็นสถานะของ Pod เป็นอย่างไรในช่วงแรก
2. ทำไม local-path ต้องรอ Pod ก่อนจึงสร้างตู้ได้ (ใช้ข้อมูลจาก annotation `volume.kubernetes.io/selected-node` ตอบ)

---

## LAB 4: Static PV และ storageClassName ""

<p align="center" id="fig-6">
  <img src="images/06-lab4-static-pv.png" alt="รูปที่ 6 LAB 4 Static PV" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4: สร้าง PV pv-manual 100Mi (Retain, nodeAffinity lab-worker2) + PVC manual-claim 50Mi storageClassName "" → Bound ทันที CAPACITY 100Mi; PVC too-big 1Gi ค้าง Pending</em>
</p>

**เป้าหมาย:** สร้างตู้เองแบบผู้ดูแลคลัสเตอร์ (static PV) ผูกกับใบเบิกที่ `storageClassName: ""` เห็นกติกาการจับคู่ (ได้ตู้ใหญ่กว่า, ขอเกินแล้วค้าง) และเห็นว่า Pod ถูกส่งไป Node ของตู้เอง

**ไฟล์:** `lab04-static/pv.yaml` (PV `pv-manual` 100Mi RWO Retain hostPath `/srv/som-manual` nodeAffinity `lab-worker2`), `pvc.yaml` (PVC `manual-claim` 50Mi `""`), `pvc-too-big.yaml` (PVC `too-big` 1Gi `""`), `pod.yaml` (Pod `manual-user` ไม่ปัก Node)

### ขั้นที่ 1: ผู้ดูแลสร้างตู้

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab04-static
kubectl apply -f pv.yaml; kubectl get pv
```

```text
persistentvolume/pv-manual created
NAME        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pv-manual   100Mi      RWO            Retain           Available                          <unset>                          0s
```

PV ไม่มี namespace สถานะ `Available` และ `STORAGECLASS` ว่าง

### ขั้นที่ 2: เขียนใบเบิกที่ไม่ใช้ class

```bash
kubectl apply -f pvc.yaml; sleep 2; kubectl get pv; kubectl get pvc
```

```text
persistentvolumeclaim/manual-claim created
NAME        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pv-manual   100Mi      RWO            Retain           Bound    default/manual-claim                  <unset>                          2s
NAME           STATUS   VOLUME      CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
manual-claim   Bound    pv-manual   100Mi      RWO                           <unset>                 2s
```

- ผูกกันภายใน 2 วินาที **โดยยังไม่มี Pod** (PV ที่ไม่มี class ไม่ผ่าน WaitForFirstConsumer)
- ขอ 50Mi แต่ `CAPACITY` เป็น **100Mi** — ได้ตู้ทั้งใบ

### ขั้นที่ 3: ใบเบิกที่ขอเกินทุกตู้

```bash
kubectl apply -f pvc-too-big.yaml; sleep 3; kubectl get pvc; kubectl describe pvc too-big | tail -4
```

```text
persistentvolumeclaim/too-big created
NAME           STATUS    VOLUME      CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
manual-claim   Bound     pv-manual   100Mi      RWO                           <unset>                 6s
too-big        Pending                                                        <unset>                 3s
Events:
  Type    Reason         Age   From                         Message
  ----    ------         ----  ----                         -------
  Normal  FailedBinding  3s    persistentvolume-controller  no persistent volumes available for this claim and no storage class is set
```

ไม่มี PV ขนาด ≥ 1Gi และ `storageClassName: ""` ไม่ให้ default class สร้างตู้ให้ จึงค้าง `Pending` ไปเรื่อย ๆ

### ขั้นที่ 4: Pod ที่ใช้ตู้ทำมือ

```bash
kubectl apply -f pod.yaml; kubectl wait --for=condition=Ready pod/manual-user --timeout=90s; kubectl get pod manual-user -o wide; kubectl logs manual-user; docker exec lab-worker2 ls -la /srv/som-manual; docker exec lab-worker2 cat /srv/som-manual/manual.txt
```

```text
pod/manual-user created
pod/manual-user condition met
NAME          READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
manual-user   1/1     Running   0          1s    10.244.1.3   lab-worker2   <none>           <none>
05:39:48 from manual-user
total 12
drwxr-xr-x 2 root root 4096 Oct  5 05:39 .
drwxr-xr-x 1 root root 4096 Oct  5 05:39 ..
-rw-r--r-- 1 root root   26 Oct  5 05:39 manual.txt
05:39:48 from manual-user
```

`pod.yaml` ไม่มี `nodeSelector` แต่ Pod ลง `lab-worker2` เสมอ เพราะ scheduler อ่าน `nodeAffinity` ของ PV ที่ PVC ผูกอยู่ (ผลนี้จะเหมือนกันทุกเครื่อง)

### ขั้นที่ 5: ลบใบเบิก ตู้ Retain เหลือ Released (เก็บกวาด)

```bash
kubectl delete -f pod.yaml -f pvc.yaml -f pvc-too-big.yaml; sleep 2; kubectl get pv
```

```text
pod "manual-user" deleted from default namespace
persistentvolumeclaim "manual-claim" deleted from default namespace
persistentvolumeclaim "too-big" deleted from default namespace
NAME        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pv-manual   100Mi      RWO            Retain           Released   default/manual-claim                  <unset>                          16s
```

```bash
kubectl delete -f pv.yaml; kubectl get pv; docker exec lab-worker2 cat /srv/som-manual/manual.txt; docker exec lab-worker2 rm -rf /srv/som-manual
```

```text
persistentvolume "pv-manual" deleted
No resources found
05:39:48 from manual-user
```

PV `Retain` เหลือ `Released` (ยังจำ `CLAIM` เดิม) และแม้ลบ PV แล้ว **ไฟล์บน Node ยังอยู่** คำสั่ง `rm -rf` ท้ายสุดจึงจำเป็น

### สิ่งที่เห็น

- static PV `Available` → PVC `storageClassName: ""` → `Bound` ทันทีไม่รอ Pod ขอ 50Mi ได้ 100Mi
- ขอเกินทุกตู้ → `FailedBinding … no storage class is set` ค้าง Pending
- Pod ถูกวางบน Node ของ PV เอง ลบ PVC → `Released` ลบ PV → ไฟล์บน Node ยังอยู่

**คำถามชวนคิด**

1. ถ้าลบบรรทัด `storageClassName: ""` ออกจาก `pvc.yaml` แล้ว apply ใหม่ PVC จะผูกกับ `pv-manual` หรือไม่ จะเห็นอะไรแทน
2. ถ้ามี PV ขนาด 100Mi และ 1Gi อย่างละใบ และ PVC ขอ 80Mi ควรได้ใบไหน เพราะอะไร

---
## LAB 5: accessModes กับ local-path

<p align="center" id="fig-7">
  <img src="images/07-lab5-access-modes.png" alt="รูปที่ 7 LAB 5 accessModes" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: PVC RWX → ProvisioningFailed, Block → does not support block, RWOP Pod ที่ 2 Pending, RWO Pod 2 ตัวบน Node เดียวใช้ได้</em>
</p>

**เป้าหมาย:** ทดสอบว่า local-path รองรับ accessModes/volumeMode แบบไหน เห็นว่า RWO ไม่ได้แปลว่า Pod เดียว RWOP กัน Pod ที่ 2 ได้จริง และขนาดใน PVC ไม่ถูกบังคับ

**ไฟล์ (`lab05-access/`):**

| ไฟล์ | เนื้อหา |
|---|---|
| `rwo.yaml` | PVC `rwo-data` (RWO) + Pod `rwo-a` เขียน `/data/shared.txt` |
| `rwo-second.yaml` | Pod `rwo-b` ใช้ `rwo-data` เดียวกัน เขียนต่อแล้วแสดงไฟล์ |
| `rwop.yaml` | PVC `single` (ReadWriteOncePod) + Pod `rwop-a` |
| `rwop-second.yaml` | Pod `rwop-b` ขอใช้ `single` |
| `rwx.yaml` | PVC `shared` (ReadWriteMany) + Pod `use-rwx` |
| `blk.yaml` | PVC `blk` (`volumeMode: Block`) + Pod `use-blk` ที่ใช้ `volumeDevices` |

### ขั้นที่ 1: RWO — Pod 2 ตัวบน Node เดียวกัน

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab05-access
kubectl apply -f rwo.yaml; kubectl wait --for=condition=Ready pod/rwo-a --timeout=90s; kubectl apply -f rwo-second.yaml; kubectl wait --for=condition=Ready pod/rwo-b --timeout=90s; kubectl get pod rwo-a rwo-b -o wide; kubectl logs rwo-b
```

```text
persistentvolumeclaim/rwo-data created
pod/rwo-a created
pod/rwo-a condition met
pod/rwo-b created
pod/rwo-b condition met
NAME    READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
rwo-a   1/1     Running   0          5s    10.244.2.11   lab-worker   <none>           <none>
rwo-b   1/1     Running   0          1s    10.244.2.12   lab-worker   <none>           <none>
05:40:06 from rwo-a
05:40:07 from rwo-b
```

ทั้งคู่ Running บน **Node เดียวกัน** และ `rwo-b` อ่านบรรทัดที่ `rwo-a` เขียนได้ RWO = เมานต์ได้จาก Node เดียว ไม่ใช่ Pod เดียว

### ขั้นที่ 2: ขนาดไม่ถูกบังคับ

<p align="center" id="fig-8">
  <img src="images/08-lab5-size-not-enforced.png" alt="รูปที่ 8 LAB 5 ขนาดไม่ถูกบังคับ" width="900"><br>
  <em><b>รูปที่ 8</b> LAB5 (ต่อ): dd เขียน 50MB ลง PVC 10Mi สำเร็จ, df -h เห็นขนาดดิสก์ทั้งก้อนของ Node — requests.storage ใน local-path เป็นแค่ตัวเลข</em>
</p>

```bash
kubectl exec rwo-a -- sh -c "dd if=/dev/zero of=/data/big bs=1M count=50 && ls -lh /data/big && df -h /data"; kubectl get pvc rwo-data
```

```text
50+0 records in
50+0 records out
52428800 bytes (50.0MB) copied, 0.378015 seconds, 132.3MB/s
-rw-r--r--    1 root     root       50.0M Oct  5 05:40 /data/big
Filesystem                Size      Used Available Use% Mounted on
/dev/sdd               1006.9G    224.6G    731.1G  23% /data
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
rwo-data   Bound    pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            standard       <unset>                 5s
```

เขียน 50MB ลงตู้ที่ป้ายบอก 10Mi ได้ และ `df` เห็นดิสก์ทั้งก้อนของ Node (ตัวเลขเป็นของเครื่องทดสอบ ของนักศึกษาจะต่างกัน) เพราะตู้ของ local-path เป็นแค่โฟลเดอร์บนดิสก์ของ Node

### ขั้นที่ 3: RWOP — Pod ที่ 2 เข้าไม่ได้

```bash
kubectl apply -f rwop.yaml; kubectl wait --for=condition=Ready pod/rwop-a --timeout=90s; kubectl apply -f rwop-second.yaml; sleep 8; kubectl get pod rwop-a rwop-b -o wide; kubectl describe pod rwop-b | tail -4
```

```text
persistentvolumeclaim/single created
pod/rwop-a created
pod/rwop-a condition met
pod/rwop-b created
NAME     READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
rwop-a   1/1     Running   0          14s   10.244.2.14   lab-worker   <none>           <none>
rwop-b   0/1     Pending   0          8s    <none>        <none>       <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  8s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

`rwop-b` ค้าง `Pending` เพราะตู้ RWOP มีเจ้าของแล้ว (worker ทั้ง 2 ตัวถูกตัด ส่วน control-plane ติด taint) เราจะใช้คุณสมบัตินี้ป้องกันฐานข้อมูลใน LAB 10 ขั้น H

### ขั้นที่ 4: RWX และ Block — provisioner ปฏิเสธ

```bash
kubectl apply -f rwx.yaml -f blk.yaml; sleep 8; kubectl get pvc; kubectl get pod use-rwx use-blk
```

```text
persistentvolumeclaim/shared created
pod/use-rwx created
persistentvolumeclaim/blk created
pod/use-blk created
NAME       STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
blk        Pending                                                                        standard       <unset>                 8s
rwo-data   Bound     pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            standard       <unset>                 30s
shared     Pending                                                                        standard       <unset>                 8s
single     Bound     pvc-024e3dd8-93b7-4c2a-91d5-23b055943fe5   10Mi       RWOP           standard       <unset>                 25s
NAME      READY   STATUS    RESTARTS   AGE
use-rwx   0/1     Pending   0          8s
use-blk   0/1     Pending   0          8s
```

ดูสาเหตุที่ PVC (ไม่ใช่ที่ Pod)

```bash
kubectl describe pvc shared | sed -n "/Events:/,\$p"
kubectl describe pvc blk | sed -n "/Events:/,\$p"
```

```text
Events:
  Type     Reason                Age              From                                                                                                Message
  ----     ------                ----             ----                                                                                                -------
  Normal   WaitForFirstConsumer  8s               persistentvolume-controller                                                                         waiting for first consumer to be created before binding
  Normal   Provisioning          8s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  External provisioner is provisioning volume for claim "default/shared"
  Warning  ProvisioningFailed    8s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  failed to provision volume with StorageClass "standard": NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes
  Normal   ExternalProvisioning  0s (x2 over 8s)  persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
Events:
  Type     Reason                Age              From                                                                                                Message
  ----     ------                ----             ----                                                                                                -------
  Normal   WaitForFirstConsumer  9s               persistentvolume-controller                                                                         waiting for first consumer to be created before binding
  Warning  ProvisioningFailed    9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  rancher.io/local-path does not support block volume provisioning
  Normal   ExternalProvisioning  1s (x2 over 9s)  persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
```

ส่วน Pod ที่รออยู่ **ไม่มี Event เลย**

```bash
kubectl describe pod use-rwx | tail -3
kubectl get events --field-selector involvedObject.name=shared -o custom-columns=REASON:.reason,COUNT:.count
```

```text
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:                      <none>
REASON                 COUNT
WaitForFirstConsumer   1
ExternalProvisioning   3
Provisioning           2
ProvisioningFailed     2
```

provisioner ลองซ้ำเรื่อย ๆ (COUNT เพิ่มขึ้นตามเวลา) แต่จะไม่สำเร็จ เพราะโฟลเดอร์บน Node เดียวให้หลาย Node เขียนพร้อมกันไม่ได้ และไม่ใช่ดิสก์ดิบ

### ขั้นที่ 5: เก็บกวาด

```bash
time kubectl delete -f .; kubectl get pvc,pv
```

```text
persistentvolumeclaim "blk" deleted from default namespace
pod "use-blk" deleted from default namespace
pod "rwo-b" deleted from default namespace
persistentvolumeclaim "rwo-data" deleted from default namespace
pod "rwo-a" deleted from default namespace
pod "rwop-b" deleted from default namespace
persistentvolumeclaim "single" deleted from default namespace
pod "rwop-a" deleted from default namespace
persistentvolumeclaim "shared" deleted from default namespace
pod "use-rwx" deleted from default namespace

real	0m3.456s
...
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM              STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-024e3dd8-93b7-4c2a-91d5-23b055943fe5   10Mi       RWOP           Delete           Released   default/single     standard       <unset>                          50s
persistentvolume/pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            Delete           Released   default/rwo-data   standard       <unset>                          57s
```

`kubectl delete -f .` ลบทุกไฟล์ในโฟลเดอร์ PV ที่เห็น `Released` เป็นช่วงสั้น ๆ ก่อน provisioner ลบทิ้ง (Delete) รอสักครู่แล้วตรวจซ้ำ

```bash
kubectl get pv; docker exec lab-worker ls /var/local-path-provisioner/
```

```text
No resources found
```

### สิ่งที่เห็น

- RWO: Pod 2 ตัวบน Node เดียวใช้ร่วมได้ — RWOP: Pod ที่ 2 `Pending … ReadWriteOncePod access mode already in-use`
- RWX: `NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes`, Block: `does not support block volume provisioning` — Pod ไม่มี Event ต้องดูที่ PVC
- ขนาดใน PVC ของ local-path ไม่ถูกบังคับ

**คำถามชวนคิด**

1. ถ้า `rwo-a` อยู่ `lab-worker` แล้วสร้าง Pod ที่ใช้ `rwo-data` โดยปัก `nodeSelector` ไว้ที่ `lab-worker2` คาดว่าจะเกิดอะไร
2. ร้านที่มีหลาย Pod ต้องอ่านเขียนโฟลเดอร์รูปสินค้าเดียวกันจากหลาย Node ต้องใช้ storage แบบไหน

---

## LAB 6: วงจรชีวิต: finalizer, Delete, Retain และกู้ PV

<p align="center" id="fig-9">
  <img src="images/09-lab6-finalizer-delete.png" alt="รูปที่ 9 LAB 6 finalizer และ Delete" width="900"><br>
  <em><b>รูปที่ 9</b> LAB6: ลบ PVC ที่ Pod ใช้อยู่ → Terminating (pvc-protection) → ลบ Pod → PVC หาย PV หาย โฟลเดอร์บน Node หาย (Delete)</em>
</p>

**เป้าหมาย:** ดูวงจรชีวิตของตู้ทั้งหมด: finalizer กันลบ, reclaimPolicy Delete, เปลี่ยนเป็น Retain, PVC ชื่อเดิมไม่ได้ตู้เดิม และกู้ตู้ที่ `Released` กลับมาด้วย `claimRef` + `volumeName`

**ไฟล์:** `lab06-lifecycle/pvc.yaml` (PVC `ledger` 10Mi class `standard`), `pod.yaml` (Pod `ledger-pod` เขียน `keepme.txt` ครั้งแรกครั้งเดียว ถ้ามีอยู่แล้วไม่เขียนทับ แล้วแสดงไฟล์), `pvc-reuse.yaml` (PVC `ledger` ที่มี `volumeName: PV_NAME`)

### ขั้นที่ 1: finalizer กันลบใบเบิกที่ยังใช้อยู่

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab06-lifecycle
kubectl apply -f pvc.yaml -f pod.yaml; kubectl wait --for=condition=Ready pod/ledger-pod --timeout=90s; kubectl logs ledger-pod; kubectl get pvc ledger
kubectl delete pvc ledger --wait=false; sleep 2; kubectl get pvc ledger; kubectl describe pvc ledger | grep -E "^Status|Finalizers|Used By"
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
pod/ledger-pod condition met
keepme เขียนเมื่อ 05:41:19
NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Bound    pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            standard       <unset>                 5s
persistentvolumeclaim "ledger" deleted from default namespace
NAME     STATUS        VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Terminating   pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            standard       <unset>                 7s
Status:        Terminating (lasts 2s)
Finalizers:    [kubernetes.io/pvc-protection]
Used By:       ledger-pod
```

`--wait=false` ให้ kubectl ไม่รอ (ไม่อย่างนั้นจะค้างรอจนกว่าจะลบได้) PVC ค้าง `Terminating` เพราะ finalizer `kubernetes.io/pvc-protection` และ `Used By: ledger-pod`

### ขั้นที่ 2: ลบ Pod → PVC, PV และโฟลเดอร์หาย (Delete)

```bash
PV=$(kubectl get pvc ledger -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pod ledger-pod -o jsonpath="{.spec.nodeName}"); echo "PV=$PV N=$N"; kubectl delete pod ledger-pod; kubectl get pvc,pv; sleep 1; kubectl get pv; sleep 4; kubectl get pv; docker exec $N ls /var/local-path-provisioner/
```

```text
PV=pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d N=lab-worker
pod "ledger-pod" deleted from default namespace
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            Delete           Released   default/ledger   standard       <unset>                          8s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            Delete           Released   default/ledger   standard       <unset>                          9s
No resources found
```

เมื่อ Pod หายไป PVC ถูกลบจริง PV เป็น `Released` 1–2 วินาที แล้วถูกลบพร้อมโฟลเดอร์ (คำสั่ง `ls` สุดท้ายไม่แสดงอะไร) ข้อมูล `keepme.txt` หายถาวร

### ขั้นที่ 3: เปลี่ยนตู้เป็น Retain แล้วลบใบเบิก

<p align="center" id="fig-10">
  <img src="images/10-lab6-retain-rescue.png" alt="รูปที่ 10 LAB 6 Retain และกู้ตู้" width="900"><br>
  <em><b>รูปที่ 10</b> LAB6 (ต่อ): patch PV เป็น Retain → ลบ PVC → Released ไฟล์ keepme.txt ยังอยู่ → ลบ claimRef → Available → PVC ใหม่ใส่ volumeName → Bound อ่าน keepme ได้</em>
</p>

```bash
kubectl apply -f pvc.yaml -f pod.yaml; kubectl wait --for=condition=Ready pod/ledger-pod --timeout=90s; kubectl logs ledger-pod
PV=$(kubectl get pvc ledger -o jsonpath="{.spec.volumeName}"); echo PV=$PV; kubectl patch pv $PV -p "{\"spec\":{\"persistentVolumeReclaimPolicy\":\"Retain\"}}"; kubectl get pv $PV
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
pod/ledger-pod condition met
keepme เขียนเมื่อ 05:41:40
PV=pvc-4c821b49-b44e-4818-a63e-c65943143e39
persistentvolume/pvc-4c821b49-b44e-4818-a63e-c65943143e39 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Bound    default/ledger   standard       <unset>                          2s
```

จำเวลาใน `keepme เขียนเมื่อ ...` ของตัวเองไว้ (ตัวอย่าง `05:41:40`) ใช้พิสูจน์ในขั้นที่ 5 ต่อไปลบ Pod และ PVC

```bash
kubectl delete -f pod.yaml -f pvc.yaml; sleep 3; kubectl get pv; PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); echo "N=$N"; docker exec $N ls /var/local-path-provisioner/; docker exec $N sh -c "cat /var/local-path-provisioner/${PV}_default_ledger/keepme.txt"
```

```text
pod "ledger-pod" deleted from default namespace
persistentvolumeclaim "ledger" deleted from default namespace
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          10s
N=lab-worker
pvc-4c821b49-b44e-4818-a63e-c65943143e39_default_ledger
keepme เขียนเมื่อ 05:41:40
```

ตู้ `Released` ค้างอยู่ (ไม่ถูกบด) และไฟล์ยังอยู่บน Node (หา Node จาก `nodeAffinity` ของ PV เพราะไม่มี Pod แล้ว)

### ขั้นที่ 4: ใบเบิกชื่อเดิมไม่ได้ตู้เดิม

```bash
kubectl apply -f pvc.yaml -f pod.yaml; sleep 5; kubectl get pvc ledger; kubectl get pv; kubectl logs ledger-pod
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Bound    pvc-9b832bb3-1026-4f3b-a81e-1810820588b9   10Mi       RWO            standard       <unset>                 5s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          15s
pvc-9b832bb3-1026-4f3b-a81e-1810820588b9   10Mi       RWO            Delete           Bound      default/ledger   standard       <unset>                          2s
keepme เขียนเมื่อ 05:41:53
```

PVC ใหม่ชื่อ `ledger` เหมือนเดิม แต่ได้ **ตู้ใหม่** (`pvc-9b83…`, Delete) และ `keepme.txt` เป็นไฟล์ใหม่ (เวลาใหม่) ตู้เดิมยัง `Released` เพราะยังจำ `claimRef` ของ PVC ตัวเก่า (uid เก่า) ลบชุดนี้ทิ้งก่อน (ตู้ใหม่เป็น Delete จึงหายไปเอง เหลือแต่ตู้ Retain)

```bash
kubectl delete -f pod.yaml -f pvc.yaml; sleep 6; kubectl get pv
```

```text
pod "ledger-pod" deleted from default namespace
persistentvolumeclaim "ledger" deleted from default namespace
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          30s
```

### ขั้นที่ 5: กู้ตู้เดิม

ลบ `claimRef` ให้ตู้กลับเป็น `Available` แล้วสร้างใบเบิกที่ระบุชื่อตู้ (`pvc-reuse.yaml` ผ่าน `sed` แทน `PV_NAME`)

```bash
PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); echo PV=$PV; kubectl patch pv $PV --type json -p "[{\"op\":\"remove\",\"path\":\"/spec/claimRef\"}]"; kubectl get pv $PV
```

```text
PV=pvc-4c821b49-b44e-4818-a63e-c65943143e39
persistentvolume/pvc-4c821b49-b44e-4818-a63e-c65943143e39 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Available           standard       <unset>                          30s
```

```bash
PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); sed "s/PV_NAME/$PV/" pvc-reuse.yaml | kubectl apply -f -; kubectl apply -f pod.yaml; kubectl wait --for=condition=Ready pod/ledger-pod --timeout=90s; kubectl get pvc ledger; kubectl get pv; kubectl logs ledger-pod
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
pod/ledger-pod condition met
NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Bound    pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            standard       <unset>                 1s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Bound    default/ledger   standard       <unset>                          31s
keepme เขียนเมื่อ 05:41:40
```

ได้ **ตู้เดิม** (`pvc-4c82…`) และ `keepme เขียนเมื่อ 05:41:40` ตรงกับเวลาที่จดไว้ในขั้นที่ 3 ข้อมูลกลับมาครบ (คำสั่ง `items[0]` ใช้ได้เพราะตอนนี้มี PV ตัวเดียว ถ้ามีหลายตัวให้ระบุชื่อเอง)

### ขั้นที่ 6: ลบตู้ Retain แล้วโฟลเดอร์ยังอยู่ (เก็บกวาด)

```bash
PV=$(kubectl get pvc ledger -o jsonpath="{.spec.volumeName}"); kubectl get pv $PV -o jsonpath="{.metadata.finalizers}{\"\n\"}"; kubectl delete pod ledger-pod; kubectl delete pvc ledger; kubectl delete pv $PV; kubectl get pv; docker exec lab-worker ls -la /var/local-path-provisioner/
```

```text
["kubernetes.io/pv-protection"]
pod "ledger-pod" deleted from default namespace
persistentvolumeclaim "ledger" deleted from default namespace
persistentvolume "pvc-4c821b49-b44e-4818-a63e-c65943143e39" deleted
No resources found
total 12
drwxr-xr-x  3 root root 4096 Oct  5 05:42 .
drwxr-xr-x 12 root root 4096 Oct  5 05:39 ..
drwxrwxrwx  2 root root 4096 Oct  5 05:41 pvc-4c821b49-b44e-4818-a63e-c65943143e39_default_ledger
```

PV ถูกลบแล้ว แต่โฟลเดอร์ `…_default_ledger` ยังอยู่บน Node (provisioner ไม่ลบข้อมูลของตู้ Retain) ลบเอง (ถ้าตู้ของนักศึกษาอยู่ `lab-worker2` ให้เปลี่ยนชื่อ Node)

```bash
docker exec lab-worker sh -c "rm -rf /var/local-path-provisioner/pvc-*_default_ledger"; docker exec lab-worker ls /var/local-path-provisioner/
```

### สิ่งที่เห็น

- ลบ PVC ที่ใช้อยู่ → `Terminating` (`pvc-protection`, `Used By`) จนกว่า Pod จะหาย
- Delete: PV `Released` ชั่วครู่แล้วหายพร้อมโฟลเดอร์ — Retain (`kubectl patch pv`): `Released` ข้อมูลอยู่
- PVC ชื่อเดิมได้ตู้ใหม่ กู้ตู้เดิมด้วยการลบ `claimRef` + PVC ที่มี `volumeName`
- ลบ PV ที่ Retain แล้วโฟลเดอร์บน Node ยังอยู่

**คำถามชวนคิด**

1. ถ้าลืม `--wait=false` ในขั้นที่ 1 terminal จะเป็นอย่างไร และจะออกจากสถานการณ์นั้นได้อย่างไร
2. ถ้าใช้ `pvc-reuse.yaml` ตอนที่ PV ยัง `Released` (ยังไม่ได้ลบ `claimRef`) คาดว่า PVC จะเป็นสถานะใด

---

## LAB 7: StorageClass ของเราเอง

<p align="center" id="fig-11">
  <img src="images/11-lab7-storageclass.png" alt="รูปที่ 11 LAB 7 StorageClass ของเราเอง" width="900"><br>
  <em><b>รูปที่ 11</b> LAB7: สร้าง standard-retain (Retain), local-immediate (Immediate → no node was specified), local-expand (allowVolumeExpansion: true → spec 20Mi แต่ capacity ยัง 10Mi ไม่มีใครขยายให้)</em>
</p>

**เป้าหมาย:** สร้าง StorageClass 3 แบบด้วย provisioner ตัวเดิม (`rancher.io/local-path`) เพื่อเห็นผลของ `reclaimPolicy`, `volumeBindingMode` และ `allowVolumeExpansion`

**ไฟล์ (`lab07-storageclass/`):** class `sc-retain.yaml` (`standard-retain` Retain), `sc-immediate.yaml` (`local-immediate` Immediate), `sc-expand.yaml` (`local-expand` `allowVolumeExpansion: true`) และใบเบิก `pvc-retain.yaml` (`kept` + Pod `kept-user`), `pvc-standard.yaml` (`std` + Pod `std-user`), `pvc-expand.yaml` (`ex` + Pod `ex-user`), `pvc-immediate.yaml` (`imm` ไม่มี Pod)

### ขั้นที่ 1: สร้าง class และใบเบิก

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab07-storageclass
kubectl apply -f sc-retain.yaml -f sc-immediate.yaml -f sc-expand.yaml; kubectl get sc
```

```text
storageclass.storage.k8s.io/standard-retain created
storageclass.storage.k8s.io/local-immediate created
storageclass.storage.k8s.io/local-expand created
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
local-expand         rancher.io/local-path   Delete          WaitForFirstConsumer   true                   0s
local-immediate      rancher.io/local-path   Delete          Immediate              false                  0s
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  8m39s
standard-retain      rancher.io/local-path   Retain          WaitForFirstConsumer   false                  0s
```

```bash
kubectl apply -f pvc-retain.yaml -f pvc-standard.yaml -f pvc-expand.yaml -f pvc-immediate.yaml; kubectl wait --for=condition=Ready pod/kept-user pod/std-user pod/ex-user --timeout=90s; sleep 3; kubectl get pvc; kubectl get pv
```

```text
persistentvolumeclaim/kept created
pod/kept-user created
persistentvolumeclaim/std created
pod/std-user created
persistentvolumeclaim/ex created
pod/ex-user created
persistentvolumeclaim/imm created
pod/kept-user condition met
pod/std-user condition met
pod/ex-user condition met
NAME   STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
ex     Bound     pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f   10Mi       RWO            local-expand      <unset>                 9s
imm    Pending                                                                        local-immediate   <unset>                 9s
kept   Bound     pvc-29503d87-cb90-4f0e-a081-439f3235d48b   10Mi       RWO            standard-retain   <unset>                 9s
std    Bound     pvc-a47bd8d7-34ef-44eb-ac9f-8ba88b7d068c   10Mi       RWO            standard          <unset>                 9s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM          STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f   10Mi       RWO            Delete           Bound    default/ex     local-expand      <unset>                          5s
pvc-29503d87-cb90-4f0e-a081-439f3235d48b   10Mi       RWO            Retain           Bound    default/kept   standard-retain   <unset>                          6s
pvc-a47bd8d7-34ef-44eb-ac9f-8ba88b7d068c   10Mi       RWO            Delete           Bound    default/std    standard          <unset>                          7s
```

PV ของ `kept` ได้ `Retain` ตาม class ส่วน `imm` ค้าง `Pending`

### ขั้นที่ 2: Immediate ใช้กับ local-path ไม่ได้

```bash
kubectl describe pvc imm | sed -n "/Events:/,\$p"
```

```text
Events:
  Type     Reason                Age              From                                                                                                Message
  ----     ------                ----             ----                                                                                                -------
  Normal   ExternalProvisioning  9s (x2 over 9s)  persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
  Normal   Provisioning          9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  External provisioner is provisioning volume for claim "default/imm"
  Warning  ProvisioningFailed    9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  failed to provision volume with StorageClass "local-immediate": configuration error, no node was specified
```

`Immediate` เริ่มสร้างทันทีโดยไม่มี Pod จึงไม่มี `selected-node` provisioner ไม่รู้ว่าจะสร้างโฟลเดอร์บน Node ไหน (`no node was specified`)

### ขั้นที่ 3: ขยาย PVC

```bash
kubectl patch pvc std -p "{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"20Mi\"}}}}"; echo "exit=$?"
```

```text
Error from server (Forbidden): persistentvolumeclaims "std" is forbidden: only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize
exit=1
```

class `standard` ไม่อนุญาตให้ขยาย ลองกับ `ex` (class `local-expand`) แล้วรอ 20 วินาที

```bash
kubectl patch pvc ex -p "{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"20Mi\"}}}}"; sleep 20; kubectl get pvc ex; kubectl get pvc ex -o jsonpath="spec={.spec.resources.requests.storage} status={.status.capacity.storage} conditions={.status.conditions}{\"\n\"}"; kubectl get pv $(kubectl get pvc ex -o jsonpath="{.spec.volumeName}") -o jsonpath="pv={.spec.capacity.storage}{\"\n\"}"; kubectl describe pvc ex | sed -n "/Events:/,\$p"
```

```text
persistentvolumeclaim/ex patched
NAME   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ex     Bound    pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f   10Mi       RWO            local-expand   <unset>                 33s
spec=20Mi status=10Mi conditions=[{"lastProbeTime":null,"lastTransitionTime":"2026-10-05T05:42:26Z","message":"A pod is currently referencing this PVC","reason":"PodUsingPVC","status":"False","type":"Unused"}]
pv=10Mi
Events:
  ...
  Normal  ProvisioningSucceeded  30s   rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  Successfully provisioned volume pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f
  Normal  ExternalExpanding      21s   volume_expand                                                                                       waiting for an external controller to expand this PVC
```

API ยอมรับ (`patched`, `spec=20Mi`) แต่ `status`/PV ยัง `10Mi` และ Event `ExternalExpanding` บอกว่ารอ controller ภายนอก ซึ่ง local-path ไม่มี จึงค้างแบบนี้ไปเรื่อย ๆ สุดท้ายลองลดขนาด

```bash
kubectl patch pvc ex -p "{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"5Mi\"}}}}"; echo "exit=$?"
```

```text
The PersistentVolumeClaim "ex" is invalid: spec.resources.requests.storage: Forbidden: field can not be less than status.capacity
exit=1
```

### ขั้นที่ 4: ลบ class แล้ว PV ยังอยู่ (เก็บกวาด)

```bash
PV=$(kubectl get pvc kept -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pod kept-user -o jsonpath="{.spec.nodeName}"); kubectl delete -f .; sleep 4; kubectl get pvc,pv; docker exec $N ls /var/local-path-provisioner/
```

```text
persistentvolumeclaim "ex" deleted from default namespace
pod "ex-user" deleted from default namespace
persistentvolumeclaim "imm" deleted from default namespace
persistentvolumeclaim "kept" deleted from default namespace
pod "kept-user" deleted from default namespace
persistentvolumeclaim "std" deleted from default namespace
pod "std-user" deleted from default namespace
storageclass.storage.k8s.io "local-expand" deleted
storageclass.storage.k8s.io "local-immediate" deleted
storageclass.storage.k8s.io "standard-retain" deleted
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM          STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-29503d87-cb90-4f0e-a081-439f3235d48b   10Mi       RWO            Retain           Released   default/kept   standard-retain   <unset>                          44s
pvc-29503d87-cb90-4f0e-a081-439f3235d48b_default_kept
```

class ถูกลบแล้ว แต่ PV ของ `kept` ยังอยู่ (`Released`, class `standard-retain` ที่ไม่มีแล้ว) พร้อมโฟลเดอร์ ลบเอง

```bash
kubectl get sc; PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); kubectl delete pv $PV; docker exec $N sh -c "rm -rf /var/local-path-provisioner/${PV}_default_kept; ls /var/local-path-provisioner/"; kubectl get pv
```

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  9m27s
persistentvolume "pvc-29503d87-cb90-4f0e-a081-439f3235d48b" deleted
No resources found
```

### สิ่งที่เห็น

- class ใหม่ใช้ provisioner เดิมได้ reclaimPolicy ของ class ถูกใส่ให้ PV ที่สร้าง (`kept` → Retain)
- `Immediate` + local-path → `configuration error, no node was specified`
- `standard` ขยายไม่ได้ (Forbidden) `allowVolumeExpansion: true` ผ่าน API แต่ไม่มีใครขยายจริง (`ExternalExpanding`) ลดขนาดไม่ได้
- ลบ class ไม่กระทบ PV ที่สร้างไปแล้ว

**คำถามชวนคิด**

1. ถ้าตั้ง `standard-retain` เป็น default class แทน `standard` PVC ใน LAB 3 จะต่างไปอย่างไรตอนเก็บกวาด
2. ถ้าย้ายร้านไปคลาวด์ที่ CSI driver ขยายดิสก์ได้ ขั้นตอนขยาย PVC ของ db ควรเป็นอย่างไร และต้องตรวจอะไรใน StorageClass ก่อน

---

## LAB 8: Node ล่ม: ตู้เซฟติดเรือ

<p align="center" id="fig-12">
  <img src="images/12-lab8-node-down.png" alt="รูปที่ 12 LAB 8 Node ล่ม" width="900"><br>
  <em><b>รูปที่ 12</b> LAB8: Deployment + PVC (tolerationSeconds 30) → docker stop Node ที่ Pod อยู่ → NotReady ~40–50 วิ → Pod ใหม่ Pending ~65–70 วิ (PersistentVolume's node affinity) → docker start แล้ว Pod กลับมาพร้อมข้อมูลเดิม</em>
</p>

**เป้าหมาย:** ต่อจากบทที่ 3 (Node ล่ม) เห็นว่าเมื่อ Pod ใช้ local storage Deployment สร้าง Pod ใหม่ได้ แต่ Pod ใหม่ **ไปลง Node อื่นไม่ได้** จนกว่า Node เดิมจะกลับมา

**ไฟล์:** `lab08-node-down/nd.yaml` — PVC `nd-data` (10Mi) + Deployment `nd` (replicas 1, `Recreate`, tolerations `unreachable`/`not-ready` แบบ `tolerationSeconds: 30` แทน default 300) Pod เขียนบรรทัดใหม่ลง `/data/boot.txt` ทุกครั้งที่เริ่ม พร้อมชื่อ Node (Downward API)

> **ข้อควรระวัง:** LAB นี้หยุด container ของ Node **ภายใน k8s-lab** ด้วย `docker stop` **ต้อง `docker start` ให้ Node กลับมาก่อนไป LAB ถัดไปเสมอ** และ **ห้าม `kind load` ระหว่าง Node หยุด** (pre-check พบ `failed to detect containerd snapshotter`) ใช้ Node ที่ Pod อยู่จริง (`$N`) ซึ่งอาจเป็น `lab-worker` หรือ `lab-worker2`

### ขั้นที่ 1: สร้าง Deployment ที่ใช้ PVC

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab08-node-down
kubectl apply -f nd.yaml; kubectl rollout status deploy/nd --timeout=90s; kubectl get pod -l app=nd -o wide; kubectl logs deploy/nd; kubectl get pvc nd-data
```

```text
persistentvolumeclaim/nd-data created
deployment.apps/nd created
Waiting for deployment "nd" rollout to finish: 0 of 1 updated replicas are available...
deployment "nd" successfully rolled out
NAME                 READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
nd-d49d6fd9f-hj8fp   1/1     Running   0          5s    10.244.2.35   lab-worker   <none>           <none>
05:43:21 start nd-d49d6fd9f-hj8fp on lab-worker
NAME      STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
nd-data   Bound    pvc-c20aba41-55db-4d7a-8003-770cdd1daa40   10Mi       RWO            standard       <unset>                 5s
```

### ขั้นที่ 2: หยุด Node ที่ Pod อยู่ แล้วเฝ้าดู

คำสั่งนี้หา Node ใส่ `$N` แล้ว `docker stop` และพิมพ์สถานะทุก 5 วินาที 24 รอบ (ราว 2 นาที)

```bash
N=$(kubectl get pod -l app=nd -o jsonpath="{.items[0].spec.nodeName}"); echo "N=$N"; date +%T; docker stop $N; echo "stopped $(date +%T)"; for i in $(seq 1 24); do sleep 5; echo "--- $(date +%T)"; kubectl get node $N --no-headers; kubectl get pod -l app=nd -o wide --no-headers; done
```

```text
N=lab-worker
12:43:21
lab-worker
stopped 12:43:31
--- 12:43:36
lab-worker   Ready   <none>   9m43s   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     20s   10.244.2.35   lab-worker   <none>   <none>
...
--- 12:44:07
lab-worker   Ready   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     51s   10.244.2.35   lab-worker   <none>   <none>
--- 12:44:12
lab-worker   NotReady   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     56s   10.244.2.35   lab-worker   <none>   <none>
...
--- 12:44:32
lab-worker   NotReady   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     76s   10.244.2.35   lab-worker   <none>   <none>
--- 12:44:37
lab-worker   NotReady   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Terminating   0     81s   10.244.2.35   lab-worker   <none>   <none>
nd-d49d6fd9f-xdg9j   0/1   Pending       0     0s    <none>        <none>       <none>   <none>
...
--- 12:45:33
lab-worker   NotReady   <none>   11m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Terminating   0     2m17s   10.244.2.35   lab-worker   <none>   <none>
nd-d49d6fd9f-xdg9j   0/1   Pending       0     56s     <none>        <none>       <none>   <none>
```

| เวลา (ในการทดลอง) | เหตุการณ์ |
|---|---|
| 12:43:21 → 12:43:31 | `docker stop` ใช้ 10 วินาที |
| +41 วินาที (12:44:12) | Node เป็น `NotReady` (control plane ไม่ได้ heartbeat) Pod เดิมยังแสดง `Running` |
| +66 วินาที (12:44:37) | ครบ `tolerationSeconds: 30` → Pod เดิม `Terminating`, ReplicaSet สร้าง Pod ใหม่ `nd-…-xdg9j` ที่ค้าง `Pending` |
| ต่อจากนั้น | Pod ใหม่ `Pending` ตลอด ไม่ไป `lab-worker2` แม้จะว่าง |

เวลา (`date` ใน shell ของ k8s-lab เป็นเวลาไทย) และจำนวนวินาทีในเครื่องนักศึกษาอาจต่างกัน

### ขั้นที่ 3: ทำไม Pod ใหม่ไปไหนไม่ได้

```bash
kubectl get node; kubectl get pod -l app=nd -o wide
kubectl get pv -o custom-columns=NAME:.metadata.name,CLAIM:.spec.claimRef.name,NODE:.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]; kubectl describe node $N | grep -A3 Taints
```

```text
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   12m   v1.37.0
lab-worker          NotReady   <none>          11m   v1.37.0
lab-worker2         Ready      <none>          11m   v1.37.0
NAME                 READY   STATUS        RESTARTS   AGE     IP            NODE         NOMINATED NODE   READINESS GATES
nd-d49d6fd9f-hj8fp   1/1     Terminating   0          2m23s   10.244.2.35   lab-worker   <none>           <none>
nd-d49d6fd9f-xdg9j   0/1     Pending       0          62s     <none>        <none>       <none>           <none>
NAME                                       CLAIM     NODE
pvc-c20aba41-55db-4d7a-8003-770cdd1daa40   nd-data   lab-worker
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
```

ตู้ (PV) ผูกกับ Node ที่หยุด และ Node นั้นติด taint `unreachable` สาเหตุที่ scheduler เขียนไว้อยู่ใน Event ของ Pod ใหม่ ในการทดลองนี้ `kubectl describe pod -l app=nd | grep FailedScheduling` **ไม่เจอ** บรรทัดนั้น ให้ใช้ `kubectl get events` แทน (ทำในขั้นที่ 4 ด้วยชื่อ Pod จริงของตัวเอง หรือสั่งตอนนี้ก็ได้)

```bash
kubectl get events --sort-by=.lastTimestamp | grep FailedScheduling | tail -3
```

### ขั้นที่ 4: เปิด Node กลับมา

```bash
date +%T; docker start $N; echo "started $(date +%T)"; for i in $(seq 1 30); do sleep 3; echo "--- $(date +%T)"; kubectl get node $N --no-headers; kubectl get pod -l app=nd -o wide --no-headers; kubectl get pod -l app=nd --no-headers | grep -q "1/1.*Running" && break; done
```

```text
12:45:39
lab-worker
started 12:45:39
--- 12:45:42
lab-worker   Ready   <none>   11m   v1.37.0
nd-d49d6fd9f-hj8fp   0/1   Unknown             0     2m26s   <none>   lab-worker   <none>   <none>
nd-d49d6fd9f-xdg9j   0/1   ContainerCreating   0     65s     <none>   lab-worker   <none>   <none>
--- 12:45:46
lab-worker   Ready   <none>   11m   v1.37.0
nd-d49d6fd9f-xdg9j   1/1   Running   0     69s   10.244.2.2   lab-worker   <none>   <none>
```

```bash
kubectl logs deploy/nd; kubectl get events --sort-by=.lastTimestamp | grep -E "$(kubectl get pod -l app=nd -o jsonpath='{.items[0].metadata.name}')" | tail -8
```

```text
05:43:21 start nd-d49d6fd9f-hj8fp on lab-worker
05:45:43 start nd-d49d6fd9f-xdg9j on lab-worker
75s         Normal    SuccessfulCreate          replicaset/nd-d49d6fd9f          Created pod: nd-d49d6fd9f-xdg9j
75s         Warning   FailedScheduling          pod/nd-d49d6fd9f-xdg9j           0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
11s         Normal    Scheduled                 pod/nd-d49d6fd9f-xdg9j           Successfully assigned default/nd-d49d6fd9f-xdg9j to lab-worker
10s         Normal    TaintManagerEviction      pod/nd-d49d6fd9f-xdg9j           Cancelling deletion of Pod default/nd-d49d6fd9f-xdg9j
9s          Normal    Pulled                    pod/nd-d49d6fd9f-xdg9j           Container image "busybox:1.36" already present on machine and can be accessed by the pod
9s          Normal    Created                   pod/nd-d49d6fd9f-xdg9j           Container created
9s          Normal    Started                   pod/nd-d49d6fd9f-xdg9j           Container started
```

- Node `Ready` ใน 3 วินาที Pod ใหม่ `Running` บน **Node เดิม** ใน ~7 วินาที Pod เก่า `Unknown` แล้วหายไป
- `boot.txt` มี 2 บรรทัด ข้อมูลเดิมอยู่ครบ (เวลาใน log เป็น UTC)
- `FailedScheduling … 1 node(s) didn't match PersistentVolume's node affinity` = `lab-worker2` ที่ไม่มีตู้, `2 node(s) had untolerated taint(s)` = control-plane และ Node ที่หยุด

### ขั้นที่ 5: เก็บกวาดและตรวจ Node

```bash
kubectl delete -f nd.yaml; sleep 4; kubectl get node; kubectl get pv,pvc; docker exec lab-worker crictl images | grep -E "postgres|som-shop"
```

```text
persistentvolumeclaim "nd-data" deleted from default namespace
deployment.apps "nd" deleted from default namespace
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          12m   v1.37.0
lab-worker2         Ready    <none>          12m   v1.37.0
No resources found
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  fc97d28600ddf       76.6MB
```

ต้องเห็น 3 Node `Ready` และ image ของร้านยังอยู่บน Node (การ stop/start ไม่ทำให้ image หาย) ถ้าไม่เห็นให้ทำ LAB 0 ขั้นที่ 6 ใหม่หลัง Node ครบ

### สิ่งที่เห็น

- `docker stop` Node → `NotReady` ~40–50 วินาที → ครบ tolerationSeconds → Pod ใหม่ `Pending`
- `didn't match PersistentVolume's node affinity` — ตู้ไม่ลอยข้ามเรือ Pod ใหม่รอจน Node เดิมกลับ
- `docker start` → Pod กลับมาบน Node เดิมพร้อมข้อมูลเดิม

**คำถามชวนคิด**

1. ถ้าไม่ได้ตั้ง `tolerationSeconds: 30` (ใช้ default 300) Pod ใหม่จะถูกสร้างเมื่อไรหลัง Node NotReady
2. ร้านน้องส้มใน LAB 10 ใช้ local-path เหมือนกัน ถ้า Node ที่ db อยู่ล่ม ลูกค้าจะเจออะไร และ Deployment ช่วยได้หรือไม่

---

## LAB 9: งบพื้นที่, ephemeral, subPath/readOnly/fsGroup

<p align="center" id="fig-13">
  <img src="images/13-lab9-quota-ephemeral.png" alt="รูปที่ 13 LAB 9 quota, ephemeral, mount" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9: ResourceQuota storage ปฏิเสธ PVC เกินงบ (exceeded quota), ephemeral volume ได้ PVC fsg-e ที่หายพร้อม Pod, subPath/readOnly ทำงาน, fsGroup 70 ไม่เปลี่ยนเจ้าของโฟลเดอร์ local-path</em>
</p>

**เป้าหมาย:** คุมพื้นที่ต่อ namespace ด้วย ResourceQuota (ต่อจากบทที่ 4) และลองวิธีเมานต์หลายแบบในตู้เดียว (`subPath`, `readOnly`) พร้อม generic ephemeral volume และดูผลของ `fsGroup` กับ local-path

**ไฟล์ (`lab09-misc/`):** `00-ns-quota.yaml` (namespace `quota-lab` + ResourceQuota `storage`: PVC ไม่เกิน 2 ใบ, รวม 1Gi, class standard 500Mi), `pvc-400.yaml`, `pvc-200.yaml`, `pvc-100.yaml`, `pvc-10.yaml` (PVC `p400` … `p10` ใน `quota-lab`), `pod-mounts.yaml` (PVC `fsg-data` + Pod `fsg` ใน `default` รันเป็น uid/gid 70, `fsGroup: 70`, เมานต์ตู้เดียวกันที่ `/data`, `/site` (`subPath: site`), `/ro` (`readOnly`) และ ephemeral volume `e` 5Mi ที่ `/eph`)

### ขั้นที่ 1: งบพื้นที่ต่อ namespace

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab09-misc
kubectl apply -f 00-ns-quota.yaml; kubectl apply -f pvc-400.yaml
kubectl apply -f pvc-200.yaml; echo "exit=$?"
```

```text
namespace/quota-lab created
resourcequota/storage created
persistentvolumeclaim/p400 created
Error from server (Forbidden): error when creating "pvc-200.yaml": persistentvolumeclaims "p200" is forbidden: exceeded quota: storage, requested: standard.storageclass.storage.k8s.io/requests.storage=200Mi, used: standard.storageclass.storage.k8s.io/requests.storage=400Mi, limited: standard.storageclass.storage.k8s.io/requests.storage=500Mi
exit=1
```

`p200` ถูกปฏิเสธเพราะ 400Mi + 200Mi เกินงบของ class standard (500Mi) แม้งบรวม (1Gi) ยังพอ ถัดไปขอ 100Mi และดูงบ

```bash
kubectl apply -f pvc-100.yaml; kubectl -n quota-lab get pvc; kubectl describe quota -n quota-lab
```

```text
persistentvolumeclaim/p100 created
NAME   STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
p100   Pending                                      standard       <unset>                 0s
p400   Pending                                      standard       <unset>                 1s
Name:                                                  storage
Namespace:                                             quota-lab
Resource                                               Used   Hard
--------                                               ----   ----
persistentvolumeclaims                                 2      2
requests.storage                                       500Mi  1Gi
standard.storageclass.storage.k8s.io/requests.storage  500Mi  500Mi
```

PVC ยัง `Pending` (ไม่มี Pod) แต่ถูกนับในงบแล้ว และไฟล์ไม่ได้ใส่ class แต่ถูกนับเป็น `standard` สุดท้ายขอ 10Mi

```bash
kubectl apply -f pvc-10.yaml; echo "exit=$?"
```

```text
Error from server (Forbidden): error when creating "pvc-10.yaml": persistentvolumeclaims "p10" is forbidden: exceeded quota: storage, requested: persistentvolumeclaims=1,standard.storageclass.storage.k8s.io/requests.storage=10Mi, used: persistentvolumeclaims=2,standard.storageclass.storage.k8s.io/requests.storage=500Mi, limited: persistentvolumeclaims=2,standard.storageclass.storage.k8s.io/requests.storage=500Mi
exit=1
```

ติดทั้งจำนวนใบเบิก (2/2) และงบของ class (500Mi/500Mi) ข้อความบอกครบทุกข้อที่เกิน ลบ namespace (PVC ที่ยัง Pending ไม่มี PV จึงไม่มีอะไรต้องลบบน Node)

```bash
time kubectl delete ns quota-lab
```

```text
namespace "quota-lab" deleted

real	0m10.261s
```

### ขั้นที่ 2: subPath, readOnly, fsGroup และ ephemeral ใน Pod เดียว

```bash
kubectl apply -f pod-mounts.yaml; kubectl wait --for=condition=Ready pod/fsg --timeout=90s; sleep 2; kubectl logs fsg; kubectl get pvc
```

```text
persistentvolumeclaim/fsg-data created
pod/fsg created
pod/fsg condition met
uid=70 gid=70 groups=70
drwxrwxrwx    3 0        0             4096 Oct  5 05:46 /data
drwxrwxrwx    2 0        0             4096 Oct  5 05:46 /eph
ls /data/site → page.txt
touch: /ro/x: Read-only file system
readOnly ทำงาน: เขียน /ro ไม่ได้
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
fsg-data   Bound    pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            standard       <unset>                 6s
fsg-e      Bound    pvc-1421697e-9a36-4079-9e2c-846adec65f72   5Mi        RWO            standard       <unset>                 6s
```

| บรรทัด | ความหมาย |
|---|---|
| `uid=70 gid=70 groups=70` | รันเป็น uid/gid 70 ตาม `runAsUser`/`runAsGroup` |
| `drwxrwxrwx 0 0 /data` และ `/eph` | โฟลเดอร์ของตู้ยังเป็นของ root **`fsGroup: 70` ไม่มีผลกับ local-path** แต่ 0777 ทำให้ uid 70 เขียนได้ |
| `ls /data/site → page.txt` | ไฟล์ที่เขียนผ่าน `/site` (`subPath: site`) ไปอยู่ในโฟลเดอร์ย่อย `site` ของตู้ |
| `touch: /ro/x: Read-only file system` | เมานต์ `readOnly: true` เขียนไม่ได้ |
| PVC `fsg-e` 5Mi | ephemeral volume ได้ PVC ชื่อ `<pod>-<volume>` อัตโนมัติ |

> **ข้อสังเกต:** ถ้าสั่ง `kubectl logs fsg` ทันทีหลัง `wait` (ไม่มี `sleep 2`) การทดลองได้แค่บรรทัดแรก `uid=70 gid=70 groups=70` เพราะสคริปต์ยังรันไม่ถึงบรรทัดถัดไป รอ 1–2 วินาทีแล้วสั่งใหม่

ดูเจ้าของของ `fsg-e` และไฟล์บน Node (ผลด้านล่างมาจากรอบทดลองก่อนหน้าของ LAB เดียวกัน ชื่อ PV จึงต่างจากขั้นด้านบน)

```bash
kubectl get pvc fsg-e -o jsonpath="{.metadata.ownerReferences}{\"\n\"}"; N=$(kubectl get pod fsg -o jsonpath="{.spec.nodeName}"); docker exec $N sh -c "ls -lan /var/local-path-provisioner/; ls -lan /var/local-path-provisioner/*_default_fsg-data/ /var/local-path-provisioner/*_default_fsg-data/site"
```

```text
[{"apiVersion":"v1","blockOwnerDeletion":true,"controller":true,"kind":"Pod","name":"fsg","uid":"dbd236f5-6739-4039-b67c-d238aac04b97"}]
total 16
drwxr-xr-x  4 0 0 4096 Oct  5 05:46 .
drwxr-xr-x 12 0 0 4096 Oct  5 05:39 ..
drwxrwxrwx  3 0 0 4096 Oct  5 05:46 pvc-1508f6e3-bb64-4f1e-aa89-1d39a561837f_default_fsg-data
drwxrwxrwx  2 0 0 4096 Oct  5 05:46 pvc-e6b1aff0-f67c-4375-b8fc-aa2b9dc7059f_default_fsg-e
/var/local-path-provisioner/pvc-1508f6e3-bb64-4f1e-aa89-1d39a561837f_default_fsg-data/:
total 12
drwxrwxrwx 3 0 0 4096 Oct  5 05:46 .
drwxr-xr-x 4 0 0 4096 Oct  5 05:46 ..
drwxrwxrwx 2 0 0 4096 Oct  5 05:46 site

/var/local-path-provisioner/pvc-1508f6e3-bb64-4f1e-aa89-1d39a561837f_default_fsg-data/site:
total 12
drwxrwxrwx 2  0  0 4096 Oct  5 05:46 .
drwxrwxrwx 3  0  0 4096 Oct  5 05:46 ..
-rw-r--r-- 1 70 70   36 Oct  5 05:46 page.txt
```

- `fsg-e` มี ownerReferences เป็น Pod `fsg` (`controller: true`) — garbage collector จะลบตาม Pod
- โฟลเดอร์ `site` (จาก subPath) ถูกสร้างให้อัตโนมัติ ไฟล์ `page.txt` เป็นของ `70 70` แต่โฟลเดอร์เป็นของ root ทั้งหมด

### ขั้นที่ 3: ลบ Pod → ephemeral PVC หายตาม

```bash
kubectl delete pod fsg; sleep 4; kubectl get pvc; kubectl get pv
```

```text
pod "fsg" deleted from default namespace
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
fsg-data   Bound    pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            standard       <unset>                 13s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM              STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            Delete           Bound    default/fsg-data   standard       <unset>                          11s
```

`fsg-e` และ PV ของมันหายไปพร้อม Pod ส่วน `fsg-data` (PVC ปกติ) ยังอยู่

### ขั้นที่ 4: เก็บกวาด

```bash
kubectl delete -f pod-mounts.yaml; sleep 4; kubectl get pvc,pv
```

```text
persistentvolumeclaim "fsg-data" deleted from default namespace
Error from server (NotFound): error when deleting "pod-mounts.yaml": pods "fsg" not found
No resources found
```

`NotFound` ของ Pod `fsg` เป็นเรื่องปกติ (ลบไปแล้วในขั้นที่ 3)

### สิ่งที่เห็น

- ResourceQuota ปฏิเสธ PVC ที่เกินจำนวนหรือเกินงบรวม/งบต่อ class (`exceeded quota: storage, …`) นับตั้งแต่ PVC ยัง Pending
- `subPath` เมานต์โฟลเดอร์ย่อย, `readOnly` → `Read-only file system`, `fsGroup` ไม่เปลี่ยนเจ้าของโฟลเดอร์ของ local-path
- ephemeral volume ได้ PVC `fsg-e` ที่มี ownerReferences ถึง Pod และหายตาม Pod

**คำถามชวนคิด**

1. ถ้า Pod `fsg` อยู่ใน `quota-lab` (ที่ใช้ PVC ครบ 2 ใบแล้ว) Pod จะถูกสร้างได้หรือไม่ เพราะ ephemeral volume สร้างอะไรขึ้นมา
2. ถ้าย้ายไปใช้ CSI driver ที่รองรับ `fsGroup` คาดว่า `ls -ldn /data` จะเปลี่ยนเป็นอย่างไร

---
## LAB 10: LAB สุดท้าย: ร้านน้องส้มจำได้แล้ว

**เป้าหมาย:** เปลี่ยน volume ของฐานข้อมูลร้านน้องส้มจาก `emptyDir` (บทที่ 7) เป็น PVC แล้วพิสูจน์ด้วยตัวเลขจาก `/api/stats`, `psql` และหน้าร้านจริงใน browser ว่า **ลบ Pod db, rollout restart db และลบ Deployment db แล้ว apply ใหม่ ออเดอร์ไม่หายและไม่ต้อง restart web** เปิดดูไฟล์ของ postgres บน Node ทดลองสิ่งที่ห้ามทำ (scale db เป็น 2) เพื่อเห็นข้อมูลเสียจริง แล้วใช้ StorageClass แบบ Retain + `ReadWriteOncePod` ป้องกันและกู้ข้อมูล

**ต้องมีก่อน:** LAB 0 (image `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บน Node, NodePort 30080 ว่าง, ไม่มี namespace `som-shop` ค้างจากบทที่ 7) และ 3 Node `Ready` (ถ้าเพิ่งทำ LAB 8 ตรวจว่า `docker start` แล้ว)

### 10.1 สถาปัตยกรรมและไฟล์

<p align="center" id="fig-14">
  <img src="images/14-lab10-architecture.png" alt="รูปที่ 14 LAB 10 ภาพรวม som-shop-v4" width="900"><br>
  <em><b>รูปที่ 14</b> LAB10 ภาพรวม som-shop-v4: web Deployment 3 บูธ (NodePort 30080) → Service som-db → db Deployment replicas 1 Recreate → PVC som-db-data (standard 1Gi RWO) → PV บน Node</em>
</p>

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)
   ▼                     ▼                     ▼
Pod som-web-<hash>-a  Pod som-web-<hash>-b  Pod som-web-<hash>-c   (Deployment som-web 3 บูธ แบบบทที่ 7)
   │
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop
                                   ▼
                    Service som-db (ClusterIP, 5432)
                                   ▼
                    Pod som-db-<hash>-x (Deployment som-db, replicas 1, Recreate)
                                   │ volume db-data → persistentVolumeClaim som-db-data
                                   ▼
                    PVC som-db-data (standard, RWO, 1Gi) ══ PV pvc-<uid> (Delete)
                                   ▼
                    โฟลเดอร์ /var/local-path-provisioner/pvc-<uid>_som-shop_som-db-data/pgdata บน Node ที่ db ลง
```

**ตาราง LAB 10** ไฟล์ใน `som-shop-v4/`

| ไฟล์ | เนื้อหา |
|---|---|
| `k8s/00-namespace.yaml` | namespace `som-shop` (Pod Security `warn: restricted`) เหมือนบทที่ 6–7 |
| `k8s/10-db.yaml` | **PVC `som-db-data`** (`standard`, RWO, 1Gi) + Deployment `som-db` (replicas 1, `Recreate`, volume `db-data` → `claimName: som-db-data`, `PGDATA=/var/lib/postgresql/data/pgdata`, uid/gid 70, `fsGroup: 70` ซึ่งไม่มีผลกับ local-path) + Service ClusterIP `som-db` |
| `k8s/20-web.yaml` | Deployment `som-web` 3 บูธ (initContainer `wait-for-db` + `db-seed`, RollingUpdate maxSurge 1/maxUnavailable 0, preStop 5 วินาที) + Service NodePort `som-web` 30080 — เหมือนบทที่ 7 เปลี่ยนแค่ footer `LAB 008` และ change-cause |
| `k8s-retain/sc-retain.yaml` | StorageClass `standard-retain` (local-path, **Retain**, WaitForFirstConsumer) — ขั้น H |
| `k8s-retain/10-db.yaml` | เหมือน `k8s/10-db.yaml` แต่ PVC ใช้ `standard-retain` และ **`ReadWriteOncePod`** — ขั้น H |
| `k8s-retain/pvc-rescue.yaml` | PVC `som-db-data` ที่มี `volumeName: PV_NAME` ใช้กู้ตู้เดิม (แทนค่าด้วย `sed`) — ขั้น H2 |
| `hit.sh` | ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err |

> **ข้อควรระวัง:** **ห้าม `kubectl apply -f k8s-retain/`** ทั้งโฟลเดอร์ เพราะ `pvc-rescue.yaml` ยังมีคำว่า `PV_NAME` อยู่ ใช้ทีละไฟล์ตามขั้นที่บอกเท่านั้น ส่วน `k8s/` apply ทั้งโฟลเดอร์ได้

ต่างจากบทที่ 7 จุดเดียวคือ volume `db-data` ของ `som-db`

```yaml
      volumes:
        # ตู้เซฟของร้าน: อ้างใบเบิก (PVC) ด้วยชื่อ — Pod ไม่ต้องรู้ว่าตู้อยู่ที่ไหน
        - name: db-data
          persistentVolumeClaim:
            claimName: som-db-data
```

(บทที่ 7 เป็น `emptyDir: {}`) ส่วน web ไม่เก็บข้อมูลเองจึงไม่ต้องมี volume

### 10.2 ขั้น A: เปิดร้านและสั่งซื้อแรก

<p align="center" id="fig-15">
  <img src="images/15-lab10-first-orders.png" alt="รูปที่ 15 LAB 10 ขั้น A สั่งซื้อแรก" width="900"><br>
  <em><b>รูปที่ 15</b> LAB10 ขั้น A: apply → PVC Bound หลัง Pod db ลงเรือ → สั่งซื้อ 3 ครั้ง → /api/stats orders=3</em>
</p>

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/som-shop-v4
kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml; kubectl -n som-shop get pvc
```

```text
namespace/som-shop created
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db created
NAME          STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Pending                                      standard       <unset>                 0s
```

PVC `Pending` ทันทีหลังสร้าง (WaitForFirstConsumer แบบ LAB 3) รอ db พร้อม

```bash
time kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pvc,pv; kubectl -n som-shop get pod -o wide
```

```text
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out

real	0m8.205s
...
NAME                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/som-db-data   Bound    pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            standard       <unset>                 8s

NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            Delete           Bound    som-shop/som-db-data   standard       <unset>                          5s
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-7b786655f5-tk2bn   1/1     Running   0          8s    10.244.2.15   lab-worker   <none>           <none>
```

db พร้อมใน ~8 วินาที (รวมสร้างตู้) PV เป็น `Delete` ตาม class `standard` เปิดหน้าร้าน

```bash
kubectl apply -f k8s/20-web.yaml; time kubectl -n som-shop rollout status deploy/som-web --timeout=180s; kubectl -n som-shop get deploy,svc,pod -o wide
```

```text
deployment.apps/som-web created
service/som-web created
Waiting for deployment "som-web" rollout to finish: 0 of 3 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m6.044s
...
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                  SELECTOR
deployment.apps/som-db    1/1     1            1           15s   postgres     postgres:17.11-alpine   app=som-db
deployment.apps/som-web   3/3     3            3           7s    web          som-shop-web:1.2        app=som-web

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/som-db    ClusterIP   10.96.185.22   <none>        5432/TCP       15s   app=som-db
service/som-web   NodePort    10.96.94.32    <none>        80:30080/TCP   7s    app=som-web

NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-7b786655f5-tk2bn    1/1     Running   0          15s   10.244.2.15   lab-worker    <none>           <none>
pod/som-web-7d79d9779f-8c8tt   1/1     Running   0          7s    10.244.2.17   lab-worker    <none>           <none>
pod/som-web-7d79d9779f-dcvkb   1/1     Running   0          7s    10.244.1.4    lab-worker2   <none>           <none>
pod/som-web-7d79d9779f-rthbz   1/1     Running   0          7s    10.244.2.16   lab-worker    <none>           <none>
```

สั่งซื้อ 3 ครั้งด้วย API แล้วดูสถิติ (`/api/stats` ตอบ `<ชื่อ Pod web> <รุ่น> orders=<จำนวน> products=<จำนวน>`)

```bash
curl -s localhost:30080/api/stats; for i in 1 2 3; do curl -s -X POST localhost:30080/api/orders -H "content-type: application/json" -d "{\"product_id\":1,\"qty\":1}"; echo; done; for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
som-web-7d79d9779f-8c8tt 1.2 orders=0 products=6
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":3,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":17}}
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
```

🌐 **browser บนเครื่องนักศึกษา** เปิด `http://localhost:30080` จะเห็นร้านรุ่น 1.2 footer `Next.js + PostgreSQL · Kubernetes LAB 008 · namespace som-shop` และลองกดปุ่ม "สั่งซื้อ" เพิ่มเองได้ (ตัวเลขออเดอร์ของนักศึกษาจะต่างจากเอกสารตามจำนวนที่กด)

<p align="center" id="fig-16">
  <img src="images/screenshots/20261005_1302_lab10pv_01-shop-4-orders.png" alt="รูปที่ 16 ภาพหน้าจอจริง ร้านที่ db ใช้ PVC" width="700"><br>
  <em><b>รูปที่ 16</b> ภาพหน้าจอจริงจากการทดลอง: ร้าน som-shop-v4 ที่ db เก็บข้อมูลใน PVC som-db-data — ออเดอร์ทั้งหมด 4 รายการ (รอบถ่ายภาพสั่งซื้อ 4 ครั้ง) เสิร์ฟโดย Pod som-web-7d79d9779f-55j9n เวอร์ชัน 1.2 หัวเว็บยังเขียน "ReplicaSet + Service" เพราะใช้แอปเดิม</em>
</p>

> **หมายเหตุ:** ภาพหน้าจอจริงในหัวข้อนี้ถ่ายจากรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ ซึ่งสั่งซื้อ 4 รายการ (สินค้า 1, 2, 3, 1) ตัวเลขในภาพจึงเป็น 4 ส่วนผลคำสั่งในเอกสารมาจากรอบหลักที่สั่งซื้อ 3 รายการ

### 10.3 ขั้น B–C: ลบ Pod db และ rollout restart db

<p align="center" id="fig-17">
  <img src="images/16-lab10-delete-pod-db.png" alt="รูปที่ 17 LAB 10 ขั้น B–C ลบ Pod db และ restart" width="900"><br>
  <em><b>รูปที่ 17</b> LAB10 ขั้น B–C: ลบ Pod db และ rollout restart db → Pod ใหม่ใช้ PVC เดิม orders=3 (request แรกหลังลบ Pod อาจได้ 503 หนึ่งครั้ง) ไม่ต้อง rollout restart web แบบบท 007</em>
</p>

**ขั้น B** ทำสิ่งเดียวกับที่ทำให้ร้านบทที่ 7 ลืมทุกอย่าง

```bash
date +%T; kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; date +%T; kubectl -n som-shop get pod -l app=som-db -o wide; for i in 1 2 3 4 5 6; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; sleep 1; done
```

```text
12:47:36
pod "som-db-7b786655f5-tk2bn" deleted from som-shop namespace
deployment "som-db" successfully rolled out
12:47:37
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-7b786655f5-zdw4m   1/1     Running   0          1s    10.244.2.18   lab-worker   <none>           <none>
som-web-7d79d9779f-dcvkb 1.2 db-not-ready
 [503]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
```

- Pod db ใหม่ (`zdw4m`) พร้อมใน ~1 วินาที บน **Node เดิม** (ตาม nodeAffinity ของ PV) และเห็น **`orders=3` เท่าเดิม**
- request แรกได้ `db-not-ready [503]` เพราะ connection เดิมใน pool ของ web ตัวนั้นหลุดไปกับ db ตัวเก่า หลังจากนั้น 200 ทั้งหมด **ไม่ต้อง rollout restart web** (ต่างจากบทที่ 7 ที่ db ใหม่ว่างเปล่าจนต้อง seed ใหม่)

**ขั้น C** rollout restart db (Recreate: ปิดตัวเก่าก่อนเปิดตัวใหม่)

```bash
kubectl -n som-shop rollout restart deploy/som-db; time kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pod -l app=som-db -o wide; sleep 3; for i in 1 2 3 4; do curl -s -m 2 localhost:30080/api/stats; done
```

```text
deployment.apps/som-db restarted
Waiting for deployment "som-db" rollout to finish: 0 out of 1 new replicas have been updated...
...
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out

real	0m1.247s
...
NAME                     READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-bb9948676-hgt7s   1/1     Running   0          1s    10.244.2.19   lab-worker   <none>           <none>
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
```

ReplicaSet ใหม่ (`bb9948676`) Pod ใหม่ แต่ใบเบิกเดิม ออเดอร์ยัง 3

### 10.4 ขั้น D: ลบ Deployment db ทั้งตัวแล้ว apply ใหม่

<p align="center" id="fig-18">
  <img src="images/17-lab10-delete-deploy.png" alt="รูปที่ 18 LAB 10 ขั้น D ลบ Deployment db" width="900"><br>
  <em><b>รูปที่ 18</b> LAB10 ขั้น D: ลบ Deployment som-db ทั้งตัว → PVC ยัง Bound → apply ใหม่ → ต่อตู้เดิม orders=3</em>
</p>

```bash
kubectl -n som-shop delete deploy som-db; kubectl -n som-shop get deploy,pvc; curl -s -m 3 -w " [%{http_code}]\n" localhost:30080/api/stats
```

```text
deployment.apps "som-db" deleted from som-shop namespace
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-web   3/3     3            3           39s

NAME                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/som-db-data   Bound    pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            standard       <unset>                 47s
som-web-7d79d9779f-dcvkb 1.2 db-not-ready
 [503]
```

ไม่มี db แล้ว (ร้าน 503) แต่ **ใบเบิกยัง `Bound` กับตู้เดิม** เพราะ PVC เป็น object แยก ไม่ได้เป็นของ Deployment apply ไฟล์เดิมอีกครั้ง

```bash
kubectl apply -f k8s/10-db.yaml; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; sleep 3; for i in 1 2 3 4; do curl -s -m 2 localhost:30080/api/stats; done
```

```text
persistentvolumeclaim/som-db-data unchanged
deployment.apps/som-db created
service/som-db unchanged
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
```

`persistentvolumeclaim/som-db-data unchanged` — Deployment ใหม่ใช้ใบเบิกเดิม ออเดอร์ 3 กลับมาโดยไม่ต้องทำอะไรกับ web

🌐 refresh browser ที่ `http://localhost:30080` ตัวเลขออเดอร์เท่าเดิม

<p align="center" id="fig-19">
  <img src="images/screenshots/20261005_1303_lab10pv_02-after-db-deploy-deleted-still-4.png" alt="รูปที่ 19 ภาพหน้าจอจริง หลังลบ Deployment db ออเดอร์ยังอยู่" width="700"><br>
  <em><b>รูปที่ 19</b> ภาพหน้าจอจริงจากการทดลอง: ลบ Pod db แล้วต่อด้วยลบ Deployment som-db และ apply k8s/10-db.yaml ใหม่ (PVC som-db-data ยัง Bound — persistentvolumeclaim/som-db-data unchanged) ออเดอร์ยังเป็น 4 โดยไม่ต้อง restart web</em>
</p>

### 10.5 ขั้น E: ดูไฟล์ postgres บน Node

<p align="center" id="fig-20">
  <img src="images/18-lab10-peek-pgdata.png" alt="รูปที่ 20 LAB 10 ขั้น E ดูไฟล์ postgres บน Node" width="900"><br>
  <em><b>รูปที่ 20</b> LAB10 ขั้น E: docker exec &lt;node&gt; ls -ln /var/local-path-provisioner/pvc-…_som-shop_som-db-data/pgdata → ไฟล์ของ postgres uid 70 (PG_VERSION, base)</em>
</p>

```bash
N=$(kubectl -n som-shop get pod -l app=som-db -o jsonpath="{.items[0].spec.nodeName}"); PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath="{.spec.volumeName}"); echo "N=$N PV=$PV"; docker exec $N ls -ln /var/local-path-provisioner/${PV}_som-shop_som-db-data/; docker exec $N ls -ln /var/local-path-provisioner/${PV}_som-shop_som-db-data/pgdata | head -12
```

```text
N=lab-worker PV=pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d
total 4
drwx------ 19 70 70 4096 Oct  5 05:48 pgdata
total 128
-rw------- 1 70 70     3 Oct  5 05:47 PG_VERSION
drwx------ 6 70 70  4096 Oct  5 05:47 base
drwx------ 2 70 70  4096 Oct  5 05:48 global
drwx------ 2 70 70  4096 Oct  5 05:47 pg_commit_ts
drwx------ 2 70 70  4096 Oct  5 05:47 pg_dynshmem
-rw------- 1 70 70  5743 Oct  5 05:47 pg_hba.conf
-rw------- 1 70 70  2640 Oct  5 05:47 pg_ident.conf
drwx------ 4 70 70  4096 Oct  5 05:47 pg_logical
drwx------ 4 70 70  4096 Oct  5 05:47 pg_multixact
drwx------ 2 70 70  4096 Oct  5 05:47 pg_notify
drwx------ 2 70 70  4096 Oct  5 05:47 pg_replslot
```

```bash
kubectl -n som-shop exec deploy/som-db -- id; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c "select count(*) from orders"
```

```text
uid=70(postgres) gid=70(postgres) groups=70(postgres)
 count 
-------
     3
(1 row)
```

ในโฟลเดอร์ของตู้มีแค่ `pgdata` (ตาม `PGDATA`) ซึ่ง postgres (uid 70) สร้างเองเป็น `drwx------ 70 70` ไฟล์ทุกไฟล์เป็นของ uid 70 นี่คือ "สมุดออเดอร์" ตัวจริงที่อยู่บน Node และอยู่รอดทุกครั้งที่ Pod เปลี่ยน

### 10.6 ขั้น F (ทดลองอันตราย): scale db เป็น 2

<p align="center" id="fig-21">
  <img src="images/19-lab10-scale-two.png" alt="รูปที่ 21 LAB 10 ขั้น F scale db เป็น 2" width="900"><br>
  <em><b>รูปที่ 21</b> LAB10 ขั้น F: scale db เป็น 2 → ทั้งคู่ลง Node เดียว (RWO) Running/Ready ทั้งคู่ → postgres ตัวที่ 2 recovery บนโฟลเดอร์เดียวกัน → psql ผ่าน Service ได้ orders 3 กับ 6 สลับกัน</em>
</p>

> **⚠️ คำเตือน:** ขั้นนี้ **ตั้งใจทำให้ข้อมูลเสียจริง** เพื่อให้เห็นว่าทำไม db บน Deployment ต้องเป็น 1 ตัว ทำหลังขั้น E เท่านั้น และ **ต้องทำขั้น G ต่อทันทีหลังจบ** เพื่อเริ่มฐานข้อมูลใหม่ ห้ามทำแบบนี้กับระบบจริง

ผลของขั้นนี้ **ไม่แน่นอนในแต่ละเครื่อง แต่เสียหายทุกครั้ง** การทดลองจริงพบได้สามแบบ

| แบบ | อาการหลัง scale กลับเป็น 1 | พบเมื่อ |
|---|---|---|
| 1 | ราว 1 นาทีต่อมา postgres ตัวที่เหลือหยุดเอง (`lock file is invalid`) แล้ว restart **ออเดอร์หาย 6 → 3** | รอบหลักของ LAB |
| 2 | เหมือนแบบ 1 แต่ Pod ขึ้น `Completed` → **`CrashLoopBackOff` ชั่วครู่** (~10–24 วินาที) แล้ว `Running` เอง ออเดอร์ 6 → 3 | รอบทดลองซ้ำ 2 รอบ |
| 3 | postgres เริ่มไม่ได้อีกเลย log มี **`PANIC: could not locate a valid checkpoint record`** และค้าง `CrashLoopBackOff` ร้านขึ้น `db-not-ready` | การตรวจสอบก่อนเขียนบท (pre-check) |

**ขั้นที่ F1** scale เป็น 2 แล้วดูว่า Pod ลงที่ไหน

```bash
kubectl -n som-shop scale deploy/som-db --replicas=2; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pod -l app=som-db -o wide
```

```text
deployment.apps/som-db scaled
Waiting for deployment "som-db" rollout to finish: 1 of 2 updated replicas are available...
deployment "som-db" successfully rolled out
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-7b786655f5-mkhsg   1/1     Running   0          4s    10.244.2.21   lab-worker   <none>           <none>
som-db-7b786655f5-phtbj   1/1     Running   0          14s   10.244.2.20   lab-worker   <none>           <none>
```

ไม่มีอะไรห้าม ทั้งคู่ `Running 1/1` บน **Node เดียวกัน** (PVC เป็น RWO ซึ่งกันแค่ต่าง Node) ดู log ของทั้งสองตัว

```bash
for p in $(kubectl -n som-shop get pod -l app=som-db -o name); do echo "== $p"; kubectl -n som-shop logs $p --tail=6; done
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db -o jsonpath="{range .items[*].endpoints[*]}{.addresses[0]} ready={.conditions.ready} {.targetRef.name}{\"\n\"}{end}"
```

```text
== pod/som-db-7b786655f5-mkhsg
2026-10-05 05:48:11.148 UTC [26] LOG:  database system was not properly shut down; automatic recovery in progress
2026-10-05 05:48:11.153 UTC [26] LOG:  invalid record length at 0/1960848: expected at least 24, got 0
2026-10-05 05:48:11.153 UTC [26] LOG:  redo is not required
2026-10-05 05:48:11.163 UTC [24] LOG:  checkpoint starting: end-of-recovery immediate wait
2026-10-05 05:48:11.187 UTC [24] LOG:  checkpoint complete: wrote 3 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.008 s, sync=0.004 s, total=0.027 s; sync files=2, longest=0.003 s, average=0.002 s; distance=0 kB, estimate=0 kB; lsn=0/1960848, redo lsn=0/1960848
2026-10-05 05:48:11.192 UTC [1] LOG:  database system is ready to accept connections
== pod/som-db-7b786655f5-phtbj
2026-10-05 05:48:00.265 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-10-05 05:48:00.265 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-10-05 05:48:00.272 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-10-05 05:48:00.314 UTC [26] LOG:  database system was shut down at 2026-10-05 05:47:59 UTC
2026-10-05 05:48:00.314 UTC [27] FATAL:  the database system is starting up
2026-10-05 05:48:00.320 UTC [1] LOG:  database system is ready to accept connections
10.244.2.20 ready=true som-db-7b786655f5-phtbj
10.244.2.21 ready=true som-db-7b786655f5-mkhsg
```

ตัวที่ 2 (`mkhsg`) เปิดโฟลเดอร์ที่ตัวแรกยังใช้อยู่ คิดว่าเครื่องดับกะทันหัน (`not properly shut down; automatic recovery in progress`) แล้วทำ checkpoint ของตัวเอง ทั้งคู่ ready และอยู่ใน EndpointSlice ของ Service `som-db` (postgres กันการเปิดซ้ำด้วยไฟล์ล็อก `postmaster.pid` และการตรวจ process แต่สอง container อยู่คนละ PID/IPC namespace จึงมองไม่เห็นกัน)

**ขั้นที่ F2** สั่งซื้อแล้วถามฐานข้อมูลทั้งสองตัว

```bash
for i in 1 2 3; do curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H "content-type: application/json" -d "{\"product_id\":2,\"qty\":1}"; done; echo; for i in 1 2 3 4 5 6; do curl -s localhost:30080/api/stats; done
for p in $(kubectl -n som-shop get pod -l app=som-db -o name); do echo "$p orders=$(kubectl -n som-shop exec $p -- psql -U som -d catshop -tAc "select count(*) from orders")"; done
```

```text
201 201 201 
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-rthbz 1.2 orders=6 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-rthbz 1.2 orders=6 products=6
pod/som-db-7b786655f5-mkhsg orders=3
pod/som-db-7b786655f5-phtbj orders=6
```

หน้าเว็บเห็น `orders=6` (connection pool ของ web ยังต่อกับตัวแรก) แต่ถามตรงที่ Pod ได้ **6 กับ 3** — ฐานข้อมูลสองตัวบนโฟลเดอร์เดียวกันเห็นข้อมูลไม่ตรงกัน ถามผ่าน Service (connection ใหม่ทุกครั้ง)

```bash
P=$(kubectl -n som-shop get pod -l app=som-db -o name | head -1); for i in 1 2 3 4 5 6 7 8; do kubectl -n som-shop exec $P -- env PGPASSWORD=meow1234 psql -h som-db -U som -d catshop -tAc "select inet_server_addr(), count(*) from orders"; done
```

```text
10.244.2.20|6
10.244.2.20|6
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
```

Service สุ่มส่งไปทั้งสองตัว ลูกค้าคนใหม่ (หรือ web ที่ต่อใหม่) อาจได้ข้อมูลชุดไหนก็ได้

<p align="center" id="fig-22">
  <img src="images/20-lab10-corruption.png" alt="รูปที่ 22 LAB 10 ขั้น F ผล: ข้อมูลเสีย" width="900"><br>
  <em><b>รูปที่ 22</b> LAB10 ขั้น F (ผล): scale กลับ 1 → ราว 1 นาทีต่อมา postgres ตัวที่เหลือหยุดเอง ("lock file is invalid") แล้ว restart ออเดอร์หาย 6 → 3 มี CrashLoopBackOff ชั่วครู่ (บางเครื่องอาจพังเป็น PANIC)</em>
</p>

**ขั้นที่ F3** scale กลับเป็น 1 แล้ว **รอดูอย่างน้อย 1 นาที** (คำสั่งเฝ้าดู 15 รอบ × 6 วินาที)

```bash
kubectl -n som-shop scale deploy/som-db --replicas=1; for i in $(seq 1 15); do sleep 6; echo "--- $(date +%T) $(kubectl -n som-shop get pod -l app=som-db --no-headers | tr -s " " | tr "\n" ";")"; done
```

```text
deployment.apps/som-db scaled
--- 12:48:31 som-db-7b786655f5-phtbj 1/1 Running 0 33s;
--- 12:48:38 som-db-7b786655f5-phtbj 1/1 Running 0 39s;
--- 12:48:44 som-db-7b786655f5-phtbj 1/1 Running 0 45s;
--- 12:48:50 som-db-7b786655f5-phtbj 1/1 Running 0 51s;
--- 12:48:56 som-db-7b786655f5-phtbj 1/1 Running 0 57s;
--- 12:49:02 som-db-7b786655f5-phtbj 1/1 Running 1 (2s ago) 63s;
--- 12:49:08 som-db-7b786655f5-phtbj 1/1 Running 1 (8s ago) 69s;
...
--- 12:49:56 som-db-7b786655f5-phtbj 1/1 Running 1 (56s ago) 117s;
```

ReplicaSet ลบตัวใหม่กว่า (`mkhsg`) เหลือ `phtbj` ซึ่งดูปกติอยู่ราว 35 วินาที แล้ว `RESTARTS` กลายเป็น 1 ดู log ของ container ก่อน restart และหลัง restart

```bash
P=$(kubectl -n som-shop get pod -l app=som-db -o name); kubectl -n som-shop logs $P --previous --tail=8; echo ---; kubectl -n som-shop logs $P --tail=8; kubectl -n som-shop get $P -o jsonpath="{.status.containerStatuses[0].lastState}{\"\n\"}"
```

```text
2026-10-05 05:48:00.314 UTC [26] LOG:  database system was shut down at 2026-10-05 05:47:59 UTC
2026-10-05 05:48:00.314 UTC [27] FATAL:  the database system is starting up
2026-10-05 05:48:00.320 UTC [1] LOG:  database system is ready to accept connections
2026-10-05 05:49:00.010 UTC [1] LOG:  could not open file "postmaster.pid": No such file or directory
2026-10-05 05:49:00.010 UTC [1] LOG:  performing immediate shutdown because data directory lock file is invalid
2026-10-05 05:49:00.010 UTC [1] LOG:  received immediate shutdown request
2026-10-05 05:49:00.010 UTC [1] LOG:  could not open file "postmaster.pid": No such file or directory
2026-10-05 05:49:00.013 UTC [1] LOG:  database system is shut down
---

2026-10-05 05:49:01.022 UTC [1] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
2026-10-05 05:49:01.022 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-10-05 05:49:01.022 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-10-05 05:49:01.028 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-10-05 05:49:01.037 UTC [26] LOG:  database system was shut down at 2026-10-05 05:48:26 UTC
2026-10-05 05:49:01.037 UTC [27] FATAL:  the database system is starting up
2026-10-05 05:49:01.043 UTC [1] LOG:  database system is ready to accept connections
{"terminated":{"containerID":"containerd://3e73bfeab6f490cca285b1dd901a3ef80e6eb5812dbd46ceebcf4fa395e394aa","exitCode":0,"finishedAt":"2026-10-05T05:49:00Z","reason":"Completed","startedAt":"2026-10-05T05:48:00Z"}}
```

- ตอน scale ลง postgres ตัวที่ 2 ถูกปิดอย่างสุภาพและลบไฟล์ล็อก `postmaster.pid` ซึ่งเป็นไฟล์เดียวกับของตัวแรก ตัวแรกตรวจไฟล์นี้ทุกนาที (ที่วินาที `:00` ของนาทีถัดไป) จึงพบว่าหายไป แล้ว **หยุดตัวเองทันที** (`performing immediate shutdown because data directory lock file is invalid`, `exitCode 0 reason Completed`)
- kubelet เริ่ม container ใหม่ (`restartPolicy: Always`) postgres อ่านสภาพจากดิสก์ที่ตัวที่ 2 ปิดไว้ตอน `05:48:26` (`database system was shut down at 2026-10-05 05:48:26 UTC`) — สภาพที่ไม่มีออเดอร์ 3 รายการหลัง

```bash
kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -tAc "select count(*) from orders"; for i in 1 2 3 4; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; sleep 1; done
```

```text
3
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
 [200]
```

**ออเดอร์ 3 รายการที่ลูกค้าได้คำตอบ `201` ไปแล้วหายไป (6 → 3)** โดยไม่มี error ใดเตือนลูกค้าเลย

**ถ้าเห็นแบบ 2 (CrashLoopBackOff ชั่วครู่)** — ผลจริงจากรอบทดลองซ้ำ (Pod เดิม restart มาแล้วจึงมี back-off สะสม)

```text
--- 12:50:58 som-db-7b786655f5-phtbj 1/1 Running 1 (118s ago) 2m59s;
--- 12:51:04 som-db-7b786655f5-phtbj 0/1 Completed 1 (2m4s ago) 3m5s;
--- 12:51:10 som-db-7b786655f5-phtbj 0/1 CrashLoopBackOff 1 (9s ago) 3m11s;
--- 12:51:16 som-db-7b786655f5-phtbj 1/1 Running 2 (15s ago) 3m17s;
```

ไม่ต้องทำอะไร รอให้ `Running` เอง (ช่วงนั้นร้านขึ้น `db-not-ready`) แล้วตรวจจำนวนออเดอร์ด้วยคำสั่ง `psql` ด้านบน รอบทดลองซ้ำได้ `3` เช่นกัน

**ถ้าเห็นแบบ 3 (PANIC)** — `kubectl -n som-shop logs deploy/som-db` มี `PANIC: could not locate a valid checkpoint record` และ Pod ค้าง `CrashLoopBackOff` เกิน 2–3 นาที ฐานข้อมูลในตู้นี้เสียจนเปิดไม่ได้ **ไปขั้น G ทันที** (ขั้น G ลบใบเบิกและเริ่มฐานข้อมูลใหม่ จึงใช้กู้ได้ทุกแบบ)

### 10.7 ขั้น G: ลบใบเบิก = ข้อมูลหายจริง

<p align="center" id="fig-23">
  <img src="images/21-lab10-delete-pvc.png" alt="รูปที่ 23 LAB 10 ขั้น G ลบ PVC" width="900"><br>
  <em><b>รูปที่ 23</b> LAB10 ขั้น G: ลบ Deployment db + PVC → PV (Delete) ถูกลบพร้อมโฟลเดอร์ → apply ใหม่ได้ db ว่าง → rollout restart web เพื่อ seed → orders=0</em>
</p>

เริ่มฐานข้อมูลใหม่หลังขั้น F และดูว่าการลบ PVC ที่ reclaimPolicy เป็น `Delete` ทำอะไร

```bash
PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); echo "PV=$PV N=$N"; kubectl -n som-shop delete deploy som-db; time kubectl -n som-shop delete pvc som-db-data; kubectl get pv; sleep 4; kubectl get pv; docker exec $N ls /var/local-path-provisioner/
```

```text
PV=pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d N=lab-worker
deployment.apps "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace

real	0m0.949s
...
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            Delete           Released   som-shop/som-db-data   standard       <unset>                          6m49s
No resources found
```

ต้องลบ Deployment ก่อน (ไม่อย่างนั้น PVC ค้าง `Terminating` เพราะ Pod db ยังใช้อยู่) PV `Released` ชั่วครู่แล้วหายภายใน 4 วินาที คำสั่ง `ls` สุดท้ายไม่แสดงอะไร **โฟลเดอร์ `pgdata` บน Node ถูกลบแล้ว** apply db ใหม่

```bash
kubectl apply -f k8s/10-db.yaml; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; sleep 5; for i in 1 2 3; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; done; curl -s -o /dev/null -w "หน้าแรก %{http_code}\n" localhost:30080/
```

```text
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db unchanged
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
som-web-7d79d9779f-rthbz 1.2 db-not-ready
 [503]
som-web-7d79d9779f-rthbz 1.2 db-not-ready
 [503]
som-web-7d79d9779f-8c8tt 1.2 db-not-ready
 [503]
หน้าแรก 503
```

`persistentvolumeclaim/som-db-data created` (ไม่ใช่ `unchanged`) = ใบเบิกใหม่ ตู้ใหม่ว่างเปล่า ไม่มีตาราง ร้านเป็น 503 แบบเดียวกับบทที่ 7

🌐 browser จะเห็นหน้า "ร้านกำลังเตรียมสินค้า"

<p align="center" id="fig-24">
  <img src="images/screenshots/20261005_1304_lab10pv_03-pvc-deleted-503.png" alt="รูปที่ 24 ภาพหน้าจอจริง ลบ PVC แล้ว 503" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: ลบ PVC som-db-data → PV เป็น Released แล้วถูกลบเพราะ reclaimPolicy Delete → apply ใหม่ได้ PVC/PV ใหม่ที่ว่างเปล่า หน้าร้านขึ้น "ร้านกำลังเตรียมสินค้า" (HTTP 503, db-not-ready)</em>
</p>

เติมตารางและสินค้าด้วย initContainer `db-seed` ของ web (วิธีเดียวกับบทที่ 7)

```bash
kubectl -n som-shop rollout restart deploy/som-web; time kubectl -n som-shop rollout status deploy/som-web --timeout=180s; for i in 1 2 3; do curl -s localhost:30080/api/stats; done; kubectl -n som-shop get pvc
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out

real	0m18.351s
...
som-web-7fdc4fd7cb-psq5x 1.2 orders=0 products=6
som-web-7fdc4fd7cb-tn9mg 1.2 orders=0 products=6
som-web-7fdc4fd7cb-psq5x 1.2 orders=0 products=6
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Bound    pvc-70baae7e-16d6-473f-a19f-d993a143a34b   1Gi        RWO            standard       <unset>                 33s
```

ร้านกลับมาขายได้ แต่ **`orders=0`** และ PV เป็นชื่อใหม่ (`pvc-70ba…`) **ลบใบเบิกที่เป็น Delete = ทิ้งข้อมูลจริง**

<p align="center" id="fig-25">
  <img src="images/screenshots/20261005_1305_lab10pv_04-new-pvc-0-orders.png" alt="รูปที่ 25 ภาพหน้าจอจริง PVC ใหม่ ออเดอร์ 0" width="700"><br>
  <em><b>รูปที่ 25</b> ภาพหน้าจอจริงจากการทดลอง: หลัง rollout restart deploy/som-web ให้ db-seed เติมสินค้าใหม่ ร้านกลับมาขายได้ด้วย Pod web ชุดใหม่ (som-web-5564dcc7dd-…) แต่ออเดอร์เป็น 0 เพราะเป็นตู้ใหม่</em>
</p>

### 10.8 ขั้น H: Retain + ReadWriteOncePod

<p align="center" id="fig-26">
  <img src="images/22-lab10-retain-rwop.png" alt="รูปที่ 26 LAB 10 ขั้น H Retain + RWOP" width="900"><br>
  <em><b>รูปที่ 26</b> LAB10 ขั้น H: StorageClass standard-retain + PVC ReadWriteOncePod → orders=2 → scale db 2 → Pod ที่ 2 Pending (ReadWriteOncePod already in-use) ปลอดภัย</em>
</p>

ทำ db ให้ปลอดภัยขึ้นสองเรื่อง: ตู้ไม่ถูกบดเมื่อลบใบเบิก (`Retain`) และระบบไม่ยอมให้ Pod ที่ 2 ใช้ตู้ (`ReadWriteOncePod`) spec ของ PVC ที่มีอยู่แก้ class/โหมดไม่ได้ จึงลบชุดเดิมแล้วสร้างใหม่

```bash
kubectl -n som-shop delete deploy som-db; kubectl -n som-shop delete pvc som-db-data; kubectl apply -f k8s-retain/sc-retain.yaml -f k8s-retain/10-db.yaml; kubectl get sc; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pvc; kubectl get pv
```

```text
deployment.apps "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace
storageclass.storage.k8s.io/standard-retain created
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db unchanged
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  21m
standard-retain      rancher.io/local-path   Retain          WaitForFirstConsumer   false                  0s
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Bound    pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           standard-retain   <unset>                 8s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Bound    som-shop/som-db-data   standard-retain   <unset>                          5s
```

PVC `RWOP` class `standard-retain` PV เป็น `Retain` (ในรอบนี้ db ลง `lab-worker2` Node ของนักศึกษาอาจต่าง) db ใหม่ว่าง จึง seed ด้วย rollout restart web แล้วสั่งซื้อ 2 รายการ

```bash
kubectl -n som-shop rollout restart deploy/som-web; kubectl -n som-shop rollout status deploy/som-web --timeout=180s >/dev/null; for i in 1 2; do curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H "content-type: application/json" -d "{\"product_id\":5,\"qty\":1}"; done; echo; for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
deployment.apps/som-web restarted
201 201 
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
som-web-69c6c4b4c6-w7fh2 1.2 orders=2 products=6
```

ลองความผิดพลาดเดิมของขั้น F

```bash
kubectl -n som-shop scale deploy/som-db --replicas=2; sleep 10; kubectl -n som-shop get pod -l app=som-db -o wide; P=$(kubectl -n som-shop get pod -l app=som-db --field-selector=status.phase=Pending -o name); kubectl -n som-shop describe $P | sed -n "/Events:/,\$p"; kubectl -n som-shop get deploy som-db
```

```text
deployment.apps/som-db scaled
NAME                      READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
som-db-7b786655f5-cmcz8   0/1     Pending   0          10s   <none>       <none>        <none>           <none>
som-db-7b786655f5-n6bzl   1/1     Running   0          37s   10.244.1.7   lab-worker2   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  10s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
NAME     READY   UP-TO-DATE   AVAILABLE   AGE
som-db   1/2     2            1           37s
```

Pod ที่ 2 ค้าง `Pending` (`ReadWriteOncePod access mode already in-use`) postgres ตัวที่ 2 ไม่เคยได้เปิดโฟลเดอร์ scale กลับ

```bash
kubectl -n som-shop scale deploy/som-db --replicas=1; sleep 3; kubectl -n som-shop get pod -l app=som-db; for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
deployment.apps/som-db scaled
NAME                      READY   STATUS    RESTARTS   AGE
som-db-7b786655f5-n6bzl   1/1     Running   0          40s
som-web-69c6c4b4c6-w7fh2 1.2 orders=2 products=6
som-web-69c6c4b4c6-c86ph 1.2 orders=2 products=6
som-web-69c6c4b4c6-w7fh2 1.2 orders=2 products=6
```

ReplicaSet ลบ Pod ที่ Pending ทิ้ง ร้านปกติ `orders=2` ไม่มีอะไรเสียหาย (`k8s-retain/10-db.yaml` ยังเป็น `Recreate` เพราะ RWOP + RollingUpdate จะทำให้ rollout ค้าง — ทฤษฎีหัวข้อ 14.2)

### 10.9 ขั้น H2: ลบใบเบิกแล้วกู้ตู้ที่ Retain

<p align="center" id="fig-27">
  <img src="images/23-lab10-rescue-retained.png" alt="รูปที่ 27 LAB 10 ขั้น H2 กู้ตู้ที่ Retain" width="900"><br>
  <em><b>รูปที่ 27</b> LAB10 ขั้น H (ต่อ): ลบ PVC → PV Released ข้อมูลยังอยู่ → ลบ claimRef → PVC ใหม่ volumeName → Bound → orders=2 กลับมา</em>
</p>

จำลองการ "ลบใบเบิกพลาด" แล้วกู้ด้วยขั้นตอนเดียวกับ LAB 6

```bash
curl -s localhost:30080/api/stats; kubectl -n som-shop delete deploy som-db; kubectl -n som-shop delete pvc som-db-data; sleep 3; PV=$(kubectl get pv -o jsonpath="{.items[?(@.status.phase==\"Released\")].metadata.name}"); echo PV=$PV; kubectl get pv $PV; kubectl patch pv $PV --type json -p "[{\"op\":\"remove\",\"path\":\"/spec/claimRef\"}]"; kubectl get pv $PV
```

```text
som-web-69c6c4b4c6-c86ph 1.2 orders=2 products=6
deployment.apps "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace
PV=pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Released   som-shop/som-db-data   standard-retain   <unset>                          78s
persistentvolume/pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Available           standard-retain   <unset>                          78s
```

ตู้ `Retain` เหลือ `Released` (ช่วงนี้ร้านเป็น `db-not-ready [503]`) ลบ `claimRef` แล้วเป็น `Available` ต่อไปสร้างใบเบิกที่ชี้ตู้นี้ และเปิด db **เฉพาะ Deployment** ด้วย `-l app=som-db`

```bash
PV=$(kubectl get pv -o jsonpath="{.items[?(@.status.phase==\"Available\")].metadata.name}"); sed "s/PV_NAME/$PV/" k8s-retain/pvc-rescue.yaml | kubectl apply -f -; kubectl apply -f k8s-retain/10-db.yaml -l app=som-db; echo "exit=$?"; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pvc; kubectl get pv; sleep 3; for i in 1 2 3 4; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; sleep 1; done
```

```text
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
exit=0
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Bound    pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           standard-retain   <unset>                 1s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Bound    som-shop/som-db-data   standard-retain   <unset>                          80s
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
 [200]
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
 [200]
som-web-69c6c4b4c6-c86ph 1.2 orders=2 products=6
 [200]
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
 [200]
```

ได้ **ตู้เดิม** (`pvc-80ce…`) และ **`orders=2` กลับมาทันที โดยไม่ต้อง restart web** (ตารางและออเดอร์อยู่ในตู้)

> **ทำไมต้อง `-l app=som-db`:** ถ้า apply `k8s-retain/10-db.yaml` ทั้งไฟล์หลัง `pvc-rescue.yaml` kubectl จะพยายามแก้ PVC `som-db-data` ให้ตรงกับไฟล์ (ซึ่งไม่มี `volumeName`) ผลจริงในการทดลองคือ
>
> ```text
> The PersistentVolumeClaim "som-db-data" is invalid: spec: Forbidden: spec is immutable after creation except resources.requests and volumeAttributesClassName for bound claims
> @@ -9,7 +9,7 @@
> ...
> - "VolumeName": "pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38",
> + "VolumeName": "",
> ...
> exit=1
> ```
>
> (Deployment ถูกสร้างได้แต่คำสั่งจบด้วย exit 1) `-l app=som-db` เลือกเฉพาะ object ที่มี label นี้ซึ่งคือ Deployment `som-db` จึงไม่แตะ PVC (วิธีนี้เขียนไว้ในคอมเมนต์ของ `pvc-rescue.yaml` ด้วย)

### 10.10 ขั้น I: เก็บกวาด LAB 10

```bash
PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); echo "PV=$PV N=$N"; time kubectl delete ns som-shop; kubectl get pv; docker exec $N ls /var/local-path-provisioner/
```

```text
PV=pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38 N=lab-worker2
namespace "som-shop" deleted

real	0m32.585s
...
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Released   som-shop/som-db-data   standard-retain   <unset>                          2m6s
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38_som-shop_som-db-data
```

ลบ namespace ราว 30 วินาที (Pod web มี preStop และ grace period) แต่ **PV ที่ Retain ไม่อยู่ใน namespace จึงยังอยู่** พร้อมโฟลเดอร์ ลบ PV, โฟลเดอร์ และ StorageClass เอง

```bash
PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); kubectl delete pv $PV; docker exec $N rm -rf /var/local-path-provisioner/${PV}_som-shop_som-db-data; docker exec $N ls /var/local-path-provisioner/; kubectl delete sc standard-retain; kubectl get sc,pv; kubectl get ns
```

```text
persistentvolume "pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38" deleted
storageclass.storage.k8s.io "standard-retain" deleted
NAME                                             PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
storageclass.storage.k8s.io/standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  23m
NAME                 STATUS   AGE
default              Active   23m
kube-node-lease      Active   23m
kube-public          Active   23m
kube-system          Active   23m
local-path-storage   Active   23m
```

ไม่มี PV เหลือ (`kubectl get sc,pv` แสดงแค่ class `standard`) namespace กลับเป็น 5 ตัวตั้งต้น image ของร้านยังอยู่บน Node

### 10.11 สรุป LAB 10 และปัญหาที่ส่งต่อ

<p align="center" id="fig-28">
  <img src="images/24-lab10-wrap-up.png" alt="รูปที่ 28 สรุป LAB สุดท้าย" width="900"><br>
  <em><b>รูปที่ 28</b> LAB10 สรุป: PVC ทำให้ db จำได้ แต่ยังได้แค่ 1 ตัว, ข้อมูลผูก Node และ Deployment ให้ทุก Pod ใช้ใบเบิกเดียวกัน → บท 009 StatefulSet</em>
</p>

**ตารางสรุป** สิ่งที่ PVC แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| ลบ Pod db / rollout restart db แล้วข้อมูลอยู่ | `orders=3` เท่าเดิม (request แรกอาจ 503 ครั้งเดียว) ไม่ต้อง restart web | ✅ PVC (บทนี้) |
| ลบ Deployment db แล้ว apply ใหม่ | `persistentvolumeclaim/som-db-data unchanged` → `orders=3` | ✅ PVC เป็น object แยกจาก Deployment |
| ลบ PVC พลาด | class `standard` (Delete): PV + โฟลเดอร์หาย `orders=0` / class `standard-retain` (Retain): `Released` → ลบ `claimRef` + `volumeName` → `orders=2` กลับมา | ✅ Retain + ขั้นตอนกู้ (ผู้ดูแลต้องลบตู้เองเมื่อเลิกใช้) |
| เผลอ scale db เป็น 2 | RWO: postgres สองตัวบนโฟลเดอร์เดียว ออเดอร์ 6 → 3 / CrashLoopBackOff / PANIC — RWOP: Pod ที่ 2 `Pending` ปลอดภัย | ✅ `replicas: 1` + Recreate + RWOP (กันได้ แต่ยังมีได้ตัวเดียว) |
| **db หลายตัว แต่ละตัวมีข้อมูลของตัวเอง** | Deployment มี template เดียว ทุก Pod อ้าง `claimName: som-db-data` เดียวกัน | ❌ → **StatefulSet** (`volumeClaimTemplates` ให้ PVC ประจำตัวทุก Pod, บทที่ 9) |
| **ชื่อ db คงที่** | ชื่อ Pod สุ่มทุกครั้ง (`tk2bn` → `zdw4m` → `hgt7s` …) | ❌ → **StatefulSet** (ชื่อเลขลำดับ `<ชื่อ>-0`, `<ชื่อ>-1`) |
| Node ที่ db อยู่ล่ม | local-path ผูก Node (LAB 8) db หยุดจน Node กลับ | ❌ → storage เครือข่าย (CSI) หรือ replication ระดับแอป |
| รหัสผ่านไม่อยู่ใน YAML | `meow1234` ยังเขียนตรง ๆ | ❌ → ConfigMap/Secret (บทหลัง) |

### สิ่งที่เห็นใน LAB 10

- เปลี่ยน `emptyDir` เป็น `persistentVolumeClaim` จุดเดียว: ลบ Pod db, rollout restart db, ลบ Deployment db → ออเดอร์อยู่ครบ ไม่ต้อง restart web
- ข้อมูลจริงคือโฟลเดอร์ `pgdata` (uid 70) ใน `/var/local-path-provisioner/pvc-<uid>_som-shop_som-db-data/` บน Node ที่ db ลง
- scale db เป็น 2 กับ RWO: ทั้งสองตัว Running บนโฟลเดอร์เดียวกัน ข้อมูลแยก (6/3) แล้วหาย (6 → 3) ภายในราว 1 นาทีหลัง scale กลับ
- ลบ PVC (Delete) = ข้อมูลหายจริง `orders=0`, Retain + RWOP: Pod ที่ 2 Pending และกู้ตู้เดิมได้ `orders=2`
- ลบ namespace แล้ว PV ที่ Retain และ StorageClass ยังอยู่ ต้องลบเอง

### คำถามท้าย LAB 10

1. ทำไมขั้น B (ลบ Pod db) ในบทนี้จึงไม่ต้อง `rollout restart deploy/som-web` แต่ในบทที่ 7 ต้องทำ และทำไม request แรกจึงอาจได้ 503
2. ขั้น D แสดง `persistentvolumeclaim/som-db-data unchanged` หมายความว่าอะไร ถ้าต้องการให้การลบ Deployment ลบข้อมูลไปด้วยต้องทำอย่างไร และควรทำหรือไม่
3. อธิบายลำดับเหตุการณ์ในขั้น F ตั้งแต่ scale เป็น 2 จนออเดอร์เหลือ 3 โดยอ้างข้อความ log อย่างน้อย 2 บรรทัด และบอกว่าทำไม RWO จึงไม่กันเหตุการณ์นี้
4. ถ้าขั้น H ใช้ RWOP แต่เปลี่ยน strategy เป็น RollingUpdate แล้วสั่ง `rollout restart deploy/som-db` คาดว่าจะเห็นอะไร (ตอบจากทฤษฎีหัวข้อ 14.2)
5. ถ้าน้องส้มอยากมี db 2 ตัว (ตัวหลัก + ตัวสำรอง) แต่ละตัวต้องมีอะไรที่ Deployment ให้ไม่ได้ และบทที่ 9 จะให้อะไร

> **🏆 ท้าทาย:** ก่อนขั้น G ลองใช้ `kubectl patch pv` เปลี่ยน PV ของ `som-db-data` (class `standard`) เป็น `Retain` แล้วลบ Deployment + PVC แล้วกู้ตู้กลับมาด้วยขั้นตอนของ LAB 6 (ใบเบิกใหม่ต้องใช้ class `standard` และ RWO ให้ตรงกับ PV) บันทึกว่าออเดอร์กลับมากี่รายการ (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเองและอย่าลืมเก็บกวาดตู้ที่ Retain)

> **ปูทางบทหน้า:** ร้านจำได้แล้ว แต่ครัวกลางยังมีได้แค่ตัวเดียว เพราะ Deployment ให้ทุก Pod ใช้ใบเบิกใบเดียวกันและชื่อ Pod สุ่มทุกครั้ง บทที่ 9 จะใช้ **StatefulSet** ให้ Pod ฐานข้อมูลมี **ชื่อคงที่และตู้เซฟประจำตัวทุก Pod**

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v4/`, kubectl แจ้ง `the path "pod.yaml" does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 008_kubernetes_pv_pvc k8s-lab:/workspace/` แล้ว 🐧 `cd` ไปโฟลเดอร์ของ LAB นั้น ตรวจด้วย `pwd` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 6 (build/load image ใหม่) |
| PVC `Pending` + Event `WaitForFirstConsumer` | class `standard` รอ Pod ตัวแรก | ปกติ สร้าง Pod ที่ใช้ PVC แล้วจะ Bound เอง |
| PVC `Pending` + `ProvisioningFailed … NodePath only supports ReadWriteOnce and ReadWriteOncePod` / `does not support block volume provisioning` | local-path ไม่รองรับ RWX/Block (LAB 5 ตั้งใจ) | ใช้ RWO/RWOP และ `Filesystem` หรือใช้ storage ที่รองรับ |
| PVC `Pending` + `configuration error, no node was specified` | class `Immediate` กับ local-path (LAB 7 ตั้งใจ) | ใช้ `WaitForFirstConsumer` |
| PVC `Pending` + `FailedBinding … no storage class is set` | `storageClassName: ""` แต่ไม่มี static PV ที่ตรง (ขนาด/โหมด) | สร้าง PV ที่ตรง หรือเอา `""` ออกเพื่อใช้ default class |
| Pod `Pending` แต่ `describe pod` ไม่มี Event | Pod รอ PVC ที่ยังไม่มีตู้ | `kubectl describe pvc <ชื่อ>` ดู Events ของ PVC |
| Pod `Pending` + `didn't match PersistentVolume's node affinity` | ตู้อยู่บน Node ที่หยุด/มี taint (LAB 8) | `docker start <node>` แล้วรอ Node `Ready` |
| `kubectl delete pvc` แล้วค้าง `Terminating` | finalizer `pvc-protection` + มี Pod ใช้อยู่ (`Used By`) | ลบ Pod หรือ Deployment ที่ใช้ PVC ก่อน (อย่าลบ finalizer เอง) |
| PV ค้าง `Released` ไม่หาย | reclaimPolicy `Retain` | กู้ (ลบ `claimRef` + PVC `volumeName`) หรือ `kubectl delete pv` แล้วลบโฟลเดอร์บน Node เอง |
| apply PVC ชื่อเดิมแล้วได้ PV ใหม่ ข้อมูลเก่าไม่มา | PV เก่ายังมี `claimRef` ของ PVC ตัวเก่า | ลบ `claimRef` แล้วใช้ `pvc-reuse.yaml`/`pvc-rescue.yaml` ที่มี `volumeName` |
| `The PersistentVolumeClaim "som-db-data" is invalid: spec: Forbidden: spec is immutable after creation …` | apply ไฟล์ที่มี PVC ชื่อเดียวกันแต่ spec ต่างจากที่ Bound อยู่ (เช่น ไม่มี `volumeName`) | `kubectl apply -f k8s-retain/10-db.yaml -l app=som-db` (เฉพาะ Deployment) |
| apply `k8s-retain/` ทั้งโฟลเดอร์แล้ว PVC ค้างหรือ error เกี่ยวกับ `PV_NAME` | `pvc-rescue.yaml` เป็นแม่แบบที่ยังไม่แทนชื่อ PV | apply ทีละไฟล์ตามขั้น H/H2 เท่านั้น ลบ PVC ที่ผิดแล้วทำใหม่ |
| `Error from server (Forbidden): … only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize` | class ไม่มี `allowVolumeExpansion: true` | ปกติของ `standard` ใน kind (LAB 7) |
| PVC ขยายแล้ว CAPACITY ไม่เปลี่ยน + `ExternalExpanding` | driver ไม่มีตัวขยาย (local-path) | ปกติใน kind ระบบจริงต้องใช้ CSI ที่รองรับ resize |
| `kubectl exec … -- kill 1` แล้ว RESTARTS ไม่เพิ่ม | PID 1 ใน container ไม่ถูกปิดด้วยสัญญาณที่ไม่มี handler | `kubectl exec cache-demo -- touch /tmp/stop` (LAB 1) |
| `Warning: would violate PodSecurity "restricted:latest": … hostPath …` | namespace ตั้ง `warn: restricted` (LAB 2 และ `som-shop`) | ปกติ เป็นแค่คำเตือน Pod ยังถูกสร้าง |
| `docker exec lab-worker ls /var/local-path-provisioner` ได้ `No such file or directory` หรือไม่เห็นโฟลเดอร์ที่คาด | ยังไม่เคยมี PV บน Node นั้น หรือ Pod/ตู้อยู่อีก Node | ใช้ `N=$(kubectl get pod <ชื่อ> -o jsonpath='{.spec.nodeName}')` หรือ `nodeAffinity` ของ PV แล้ว `docker exec $N …` |
| `kubectl logs` ได้ไม่ครบทันทีหลัง Ready | สคริปต์ใน container ยังรันไม่ถึง | รอ 1–2 วินาทีแล้วสั่งใหม่ |
| เวลาใน log ของ Pod ช้ากว่านาฬิกา 7 ชั่วโมง | busybox/postgres ใช้ UTC | ปกติ (`date` ใน shell ของ k8s-lab เป็นเวลาไทย) |
| `kubectl describe pod -l app=nd \| grep FailedScheduling` ไม่เจอ (LAB 8) | Event ไม่แสดงในรอบนั้น | `kubectl get events --sort-by=.lastTimestamp \| grep FailedScheduling` |
| หลัง LAB 8 Node ยัง `NotReady` / Pod ใหม่ไม่ขึ้น | ลืม `docker start` | 🐧 `docker start lab-worker` (หรือ Node ที่หยุด) แล้วตรวจ `kubectl get nodes` |
| `kind load` ล้มเหลว `failed to detect containerd snapshotter` | สั่งระหว่างที่ Node ถูกหยุด | `docker start` Node ให้ครบก่อนแล้ว load ใหม่ |
| request แรกหลังลบ Pod db ได้ `db-not-ready [503]` | connection เดิมใน pool ของ web หลุด | ปกติ request ถัดไปเป็น 200 |
| หลังขั้น G ร้าน 503 ค้าง (`db-not-ready`) | db ใหม่ว่างเปล่า ไม่มีตาราง | `kubectl -n som-shop rollout restart deploy/som-web` |
| ขั้น F: Pod db `Completed` → `CrashLoopBackOff` | postgres หยุดเพราะ `lock file is invalid` (ตั้งใจให้เห็น) | รอ ~1 นาทีให้ Running เอง ถ้า log มี `PANIC` และค้างเกิน 2–3 นาที ไปขั้น G |
| `ImagePullBackOff` ของ `som-shop-web:1.2` หรือ `postgres:17.11-alpine` | ยังไม่ได้ load image เข้า Node (คลัสเตอร์ใหม่) | LAB 0 ขั้นที่ 6 |
| `provided port is already allocated` ตอน apply `k8s/20-web.yaml` | Service อื่นจอง 30080 (เช่น `som-shop` ของบทที่ 7 ค้าง) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace ที่ค้าง |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080/api/stats` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| ลบ namespace `som-shop` ใช้เวลา ~30 วินาที | Pod web มี preStop 5 วินาทีและ grace period | ปกติ รอให้จบ |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `kubectl get sc` (`standard (default)` … `WaitForFirstConsumer false`), Pod `local-path-provisioner` Running และ `crictl images` ที่เห็น `som-shop-web 1.2` + `postgres 17.11-alpine`
- [ ] **LAB 1** `RESTARTS 1` หลัง `touch /tmp/stop` + `ls` ที่ `/tmp` ว่างแต่ `/cache/x.txt` อยู่ และผลหลังลบ Pod (`boot.log` บรรทัดเดียว)
- [ ] **LAB 2** Warning `restricted volume type "hostPath"`, `cat notes.txt` บนสอง Node ที่ต่างกัน และไฟล์ที่ยังอยู่หลังลบ namespace
- [ ] **LAB 3** PVC `Pending` + Event `WaitForFirstConsumer`, PVC/PV `Bound` + annotation `selected-node`, `hostPath`/`nodeAffinity` ของ PV และ `ls /var/local-path-provisioner/` บน Node
- [ ] **LAB 4** `pv-manual` `Available` → `Bound` (`CAPACITY 100Mi`), `too-big` `FailedBinding` และ Pod `manual-user` บน `lab-worker2`
- [ ] **LAB 5** `rwo-a`/`rwo-b` บน Node เดียว, `dd` 50MB ลง PVC 10Mi, `rwop-b` Pending และ `ProvisioningFailed` ของ RWX กับ Block
- [ ] **LAB 6** `Terminating` + `pvc-protection` + `Used By`, PV `Retain`/`Released` + `keepme.txt` บน Node, PVC ชื่อเดิมได้ PV ใหม่ และหลังกู้ได้ `keepme` เวลาเดิม
- [ ] **LAB 7** `kubectl get sc` 4 class, `no node was specified`, Forbidden ของ `std`, `spec=20Mi status=10Mi` + `ExternalExpanding` ของ `ex`
- [ ] **LAB 8** ตารางเวลาของตัวเอง (NotReady, Pending), `FailedScheduling … didn't match PersistentVolume's node affinity` และ `boot.txt` 2 บรรทัดหลัง `docker start`
- [ ] **LAB 9** `exceeded quota` ของ `p200` และ `p10`, `describe quota`, log ของ Pod `fsg` (`drwxrwxrwx 0 0`, `Read-only file system`) และ `fsg-e` ที่หายหลังลบ Pod
- [ ] **LAB 10** (1) PVC `Bound` + `orders=3` (2) browser หน้าร้าน (3) ลบ Pod db / rollout restart db / ลบ Deployment db (`unchanged`) แล้วยัง `orders=3` (4) `ls -ln …/pgdata` บน Node (5) ขั้น F: Pod 2 ตัวบน Node เดียว, psql ได้ 6 กับ 3, log `lock file is invalid` (หรือ `PANIC`) และ `orders` หลัง scale กลับ (6) ขั้น G: `orders=0` + browser หน้า 503 (7) ขั้น H: `RWOP standard-retain` + Pod ที่ 2 `Pending` (8) ขั้น H2: `Bound` PV เดิม + `orders=2`
- [ ] ท้ายสุด `kubectl get pv,pvc -A` ว่าง, `kubectl get sc` เหลือ `standard` ตัวเดียว และ `kubectl get ns` เหลือ 5 ตัวตั้งต้น

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Pod `cache-demo` | 1 | `kubectl get pod cache-demo` | `kubectl delete pod cache-demo` |
| namespace `hostpath-lab` และโฟลเดอร์ `/srv/som-hostpath` บน Node | 2 | `kubectl get ns hostpath-lab`; `docker exec lab-worker ls /srv` | `kubectl delete ns hostpath-lab`; `for n in lab-worker lab-worker2; do docker exec $n rm -rf /srv/som-hostpath; done` |
| PVC/PV ใน `default` (`notes`, `rwo-data`, `single`, `shared`, `blk`, `ledger`, `kept`, `std`, `ex`, `imm`, `nd-data`, `fsg-data`) | 3, 5–9 | `kubectl get pv,pvc -A` | `kubectl delete -f .` ในโฟลเดอร์ของ LAB นั้น (ลบ Pod/Deployment ก่อน PVC) |
| PV `pv-manual` และ `/srv/som-manual` บน `lab-worker2` | 4 | `kubectl get pv pv-manual`; `docker exec lab-worker2 ls /srv` | `kubectl delete pv pv-manual`; `docker exec lab-worker2 rm -rf /srv/som-manual` |
| PV ที่ `Released` (Retain) และโฟลเดอร์ `pvc-…` | 6, 7, 10 | `kubectl get pv`; `docker exec <node> ls /var/local-path-provisioner/` | `kubectl delete pv <ชื่อ>`; `docker exec <node> rm -rf /var/local-path-provisioner/<โฟลเดอร์>` |
| StorageClass `standard-retain`, `local-immediate`, `local-expand` | 7, 10 | `kubectl get sc` | `kubectl delete sc <ชื่อ>` (ต้องเหลือ `standard` ตัวเดียว) |
| Node ที่ถูก `docker stop` | 8 | `kubectl get nodes`; `docker ps -a --filter name=lab-` | `docker start <node>` แล้วรอ `Ready` |
| namespace `quota-lab` | 9 | `kubectl get ns quota-lab` | `kubectl delete ns quota-lab` |
| namespace `som-shop` (**จอง NodePort 30080**) | 10 | `kubectl get ns som-shop` | `kubectl delete ns som-shop` แล้วลบ PV ที่ Retain + StorageClass ตามขั้น I |
| image `som-shop-web:1.2`, postgres บน Node | 0, 10 | `docker exec lab-worker crictl images \| grep -E "som-shop\|postgres"` | **เก็บไว้ได้** (ใช้ซ้ำในบทถัดไป ถ้า `k8s-down` จะหายไปด้วย) |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl get ns
kubectl get pv,pvc -A
kubectl get sc
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n ls /var/local-path-provisioner/ /srv 2>&1; done
```

ผลที่ถูกต้อง: 3 Node `Ready`, namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), `No resources found` สำหรับ PV/PVC, StorageClass เหลือ `standard (default)` ตัวเดียว และไม่มีโฟลเดอร์ `pvc-…`, `som-hostpath` หรือ `som-manual` ค้างบน Node

คลัสเตอร์ `lab` และ image ของร้านเก็บไว้ใช้ต่อในบทที่ 9 ได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ PV, จำนวนออเดอร์ และเวลา) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ (สั่งซื้อ 4 รายการ) ชื่อ Pod และจำนวนออเดอร์ในภาพจึงต่างจากผลคำสั่งในเอกสาร
