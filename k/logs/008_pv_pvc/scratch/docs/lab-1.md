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
