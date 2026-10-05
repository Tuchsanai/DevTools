# LAB บทที่ 7: Deployment — ผู้จัดการร้านที่เปลี่ยนรุ่นทีละบูธและย้อนรุ่นได้ สู่ร้านน้องส้มแบบโปรดักชันจริง

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Deployment — Deployment → ReplicaSet → Pod, pod-template-hash, rolling update ผ่าน Service, rollout history/change-cause/undo/pause/resume/restart, maxSurge/maxUnavailable และ Recreate, readinessProbe/minReadySeconds, rollout พังกับ progressDeadlineSeconds, zero-downtime ผ่าน NodePort, การย้ายจาก ReplicaSet เป็น Deployment, blue/green และ canary และร้านอาหารแมวน้องส้มที่เปลี่ยนรุ่นระหว่างขายโดยลูกค้าไม่เจอ error
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่จ้าง **ผู้จัดการร้าน (Deployment)** มาดูแลร้าน เริ่มจากสร้าง Deployment แรกแล้วดูลำดับชั้น Deployment → ReplicaSet → Pod เปลี่ยนรุ่นแบบ rolling ระหว่างที่ลูกค้ายิงคำขอวน ใช้สมุดบันทึกรุ่น (`rollout history`/`undo`) เทียบกลยุทธ์เปลี่ยนรุ่น 3 แบบ ทำให้ readiness ล้มและ image ผิดเพื่อดูว่า rollout ค้างแต่ร้านยังขาย นับ error ผ่าน NodePort 30080 เทียบก่อน/หลังใส่ `preStop` ย้ายร้านจาก ReplicaSet มาเป็น Deployment และลอง blue/green กับ canary ปิดท้ายด้วย **ร้านอาหารแมวน้องส้มแบบโปรดักชันจริง** ที่แปลงร้านของบทที่ 6 เป็น Deployment แล้วเปลี่ยนรุ่น 1.2 → 1.3 ย้อนรุ่น เจอรุ่นพัง 1.4 scale และ restart โดยร้านไม่สะดุด แต่จะเห็นว่าข้อมูลฐานข้อมูลยังหายเมื่อ Pod db ถูกสร้างใหม่ ซึ่งเป็นโจทย์ของบทถัดไป

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, Kubernetes v1.37.0, kubectl v1.37.1) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ค่า hash ในชื่อ ReplicaSet/Pod (เช่น `web-779cb4fbb8`), ชื่อ Pod ที่สุ่ม, จำนวน error และจำนวนครั้งที่สุ่มได้ ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ และเมื่อคำสั่งมีชื่อ ReplicaSet/Pod ให้ **แทนด้วยค่าที่เห็นในเครื่องตัวเอง** (หรือใช้ตัวแปรตามที่เอกสารแสดง) เครื่องที่ใช้ทดสอบค่อนข้างเร็ว เครื่องที่ช้ากว่าจะใช้เวลา rollout นานกว่าและอาจเห็น error ในรอบที่ไม่มี preStop มากกว่านี้

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิด browser ที่ `http://localhost:30080` หลาย LAB ใช้ **2–3 หน้าต่าง** (terminal 1, 2, 3) เพื่อดูการเปลี่ยนแปลงไปพร้อมกัน ให้เปิด SSH session เพิ่มด้วยคำสั่งเดียวกัน แล้ว `cd` ไปโฟลเดอร์เดียวกันทุกหน้าต่าง

### กติกาของ LAB บทนี้

- LAB 1–9 ทำในโฟลเดอร์ **`/workspace/007_kubernetes_deployment/02_LAB/labs`** ภายใน k8s-lab ส่วน LAB 10 ทำใน **`/workspace/007_kubernetes_deployment/02_LAB/som-shop-v3`**
- **แต่ละ LAB มี namespace ของตัวเองและจบด้วย `kubectl delete ns ...`** ยกเว้น LAB 1–3 ที่ใช้ `deploy-lab` ต่อเนื่องกันแล้วลบตอนจบ LAB 3 ถ้าหยุดกลางทางหรือผลเพี้ยน ลบ namespace ของ LAB นั้นแล้วเริ่ม LAB ใหม่ได้ (ดู [ตารางเก็บกวาด](#ตารางเก็บกวาดและคืนสภาพ))
- **NodePort 30080 จองได้ทีละ Service ทั้งคลัสเตอร์** ใช้ใน LAB 7 และ LAB 10 เท่านั้น ต้องลบ namespace `zdt-lab` ของ LAB 7 ก่อนเริ่ม LAB 10
- `kubectl apply -f <โฟลเดอร์>/` อ่านทุกไฟล์ `.yaml` ในโฟลเดอร์นั้น (ไม่ลงโฟลเดอร์ย่อย) ไฟล์ patch จึงแยกไว้ในโฟลเดอร์ `patches/` และไฟล์แบบฝึกที่ตั้งใจให้ error (`zero-zero.yaml`) อยู่ใน `exercise/` ไม่เช่นนั้นจะได้ `error validating ... [apiVersion not set, kind not set]` หรือ `The Deployment "zero" is invalid` ปนกับผลปกติ
- image สาธารณะ (`nginx:1.27-alpine`, `nginx:1.28-alpine`, `busybox:1.36`) ให้ Node ดึงเอง ไม่ต้อง `kind load` ส่วน `som-shop-web:1.2`/`1.3` ต้อง build และ `kind load` (LAB 0) และ `nginx:9.99-nope`, `som-shop-web:1.4` **ไม่มีจริง** (ตั้งใจให้พัง)
- Pod busybox ใน LAB ตั้ง `terminationGracePeriodSeconds: 1` ให้ลบแล้วหายเร็ว
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง (ของจริงเก็บใน Secret ซึ่งเป็นเนื้อหาบทหลัง)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์ พอร์ต และ image](#lab-0-เตรียมคลัสเตอร์-พอร์ต-และ-image) | 15–20 นาที | ⭐ |
| 1 | [Deployment แรก: deploy → rs → pod](#lab-1-deployment-แรก-deploy--rs--pod) | 15 นาที | ⭐ |
| 2 | [rolling update ผ่าน Service ClusterIP](#lab-2-rolling-update-ผ่าน-service-clusterip) | 10 นาที | ⭐⭐ |
| 3 | [history, change-cause, undo, pause/resume และ restart](#lab-3-history-change-cause-undo-pauseresume-และ-restart) | 15 นาที | ⭐⭐ |
| 4 | [เทียบ maxSurge/maxUnavailable และ Recreate](#lab-4-เทียบ-maxsurgemaxunavailable-และ-recreate) | 15 นาที | ⭐⭐ |
| 5 | [readiness และ minReadySeconds ตัดสิน rollout](#lab-5-readiness-และ-minreadyseconds-ตัดสิน-rollout) | 10 นาที | ⭐⭐⭐ |
| 6 | [image ผิด + progressDeadlineSeconds แล้ว undo](#lab-6-image-ผิด--progressdeadlineseconds-แล้ว-undo) | 15 นาที | ⭐⭐⭐ |
| 7 | [zero-downtime ผ่าน NodePort 30080](#lab-7-zero-downtime-ผ่าน-nodeport-30080) | 15 นาที | ⭐⭐⭐ |
| 8 | [ย้าย ReplicaSet เป็น Deployment](#lab-8-ย้าย-replicaset-เป็น-deployment) | 15 นาที | ⭐⭐⭐⭐ |
| 9 | [blue/green และ canary](#lab-9-bluegreen-และ-canary) | 10 นาที | ⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริง](#lab-10-lab-สุดท้าย-ร้านน้องส้มแบบโปรดักชันจริง) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (ถ้าต้อง build image ของร้านใน LAB 0 เพิ่มอีกราว 5–10 นาที)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมคลัสเตอร์ พอร์ต และ image](#fig-1) | 14 | [LAB 10 สถาปัตยกรรมเป้าหมาย](#fig-14) |
| 2 | [LAB 1 Deployment แรก](#fig-2) | 15 | [LAB 10 เริ่มจากสภาพบทที่ 6](#fig-15) |
| 3 | [LAB 1 scale RS ตรงถูกปรับกลับ](#fig-3) | 16 | [LAB 10 แปลงร้านเป็น Deployment](#fig-16) |
| 4 | [LAB 2 RS ใหม่เพิ่ม RS เก่าลด](#fig-4) | 17 | [ภาพหน้าจอจริง ร้าน 1.2 หลังแปลงเป็น Deployment](#fig-17) |
| 5 | [LAB 2 client เห็น v1 และ v2 ปนกัน](#fig-5) | 18 | [LAB 10 rolling 1.2 → 1.3 ไม่มี error](#fig-18) |
| 6 | [LAB 3 history และ undo](#fig-6) | 19 | [LAB 10 หน้าร้าน 1.3](#fig-19) |
| 7 | [LAB 3 pause/resume และ restart](#fig-7) | 20 | [ภาพหน้าจอจริง ร้าน 1.3 หลัง rolling err 0](#fig-20) |
| 8 | [LAB 4 เทียบ 3 กลยุทธ์](#fig-8) | 21 | [LAB 10 history และ undo](#fig-21) |
| 9 | [LAB 5 readiness และ minReadySeconds](#fig-9) | 22 | [LAB 10 รุ่นพัง 1.4 แต่ร้านยังขาย](#fig-22) |
| 10 | [LAB 6 rollout พังแล้ว undo](#fig-10) | 23 | [ภาพหน้าจอจริง รุ่นพัง 1.4 ร้านยังขาย](#fig-23) |
| 11 | [LAB 7 นับ error ก่อน/หลังใส่ preStop](#fig-11) | 24 | [LAB 10 scale 3 → 5](#fig-24) |
| 12 | [LAB 8 Deployment รับเลี้ยง RS เดิม](#fig-12) | 25 | [LAB 10 ลบ Pod db แล้ว rollout restart](#fig-25) |
| 13 | [LAB 9 blue/green และ canary](#fig-13) | 26 | [สรุป LAB สุดท้าย](#fig-26) |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ 01–23 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
├── labs/                              ← YAML ของ LAB 1–9 (แต่ละ LAB มี namespace ของตัวเอง)
│   ├── lab01-deployment/{00-ns,web}.yaml                       (namespace deploy-lab — ใช้ต่อถึง LAB 3)
│   ├── lab02-rolling/{web-v2,web-svc,client-pod}.yaml
│   ├── lab04-strategy/{00-ns,rolling,nosurge,recreate}.yaml + exercise/zero-zero.yaml
│   ├── lab05-readiness/{00-ns,web-minready,client-pod}.yaml + patches/readiness-broken-patch.yaml
│   ├── lab06-broken/{00-ns,web,web-svc,client-pod}.yaml + patches/crash-patch.yaml
│   ├── lab07-zero-downtime/{00-ns,web,web-nodeport}.yaml + patches/graceful-patch.yaml
│   ├── lab08-migrate/{00-ns,web-rs,web-svc,client-pod,web-deploy}.yaml
│   └── lab09-release/{00-ns,web-blue,web-green,web-svc,web-svc-all,web-stable,web-canary,client-pod}.yaml
└── som-shop-v3/                       ← LAB 10 ร้านน้องส้ม
    ├── app/                           ← สำเนาแอป Next.js + Dockerfile จากบทที่ 6 (build เป็น som-shop-web:1.2 และ 1.3 จากโค้ดเดียว)
    ├── k8s-rs/{00-namespace,10-db,20-web}.yaml   ← จุดเริ่ม = สภาพท้ายบทที่ 6 (ReplicaSet + Service)
    ├── k8s/{10-db,20-web}.yaml                    ← Deployment som-db (Recreate) + som-web (zero-downtime) ชื่อ/selector เดิม
    └── hit.sh                         ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err
```

แอปตัวอย่างของ LAB 1–9 คือ nginx ที่ `command` เขียนหน้า `index.html` เป็น `web <VERSION> from <ชื่อ Pod>` แล้วเปิด nginx จึงเห็นรุ่นและชื่อ Pod ทุกครั้งที่เรียก (ไม่ต้อง build อะไร) LAB 3 ไม่มีไฟล์ของตัวเอง ใช้ Deployment ต่อจาก LAB 1–2

---

## LAB 0: เตรียมคลัสเตอร์ พอร์ต และ image

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมคลัสเตอร์ พอร์ต และ image" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: เช็กคลัสเตอร์ 3 Node, NodePort 30080 ว่าง (ไม่มี Service ค้างจากบท 006) และ image som-shop-web:1.2 / 1.3 ของบท 006 ยังอยู่บน Node (ถ้าไม่มี build ใหม่ + kind load)</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 6 หรือสร้างใหม่) ตรวจว่า NodePort 30080–30082 ว่าง และมี image `som-shop-web:1.2`/`1.3` กับ `postgres:17.11-alpine` อยู่บน Node สำหรับ LAB 10

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md), [2](../../002_kubernetes_pod/02_LAB/README.md), [3](../../003_kubernetes_node_pod/02_LAB/README.md), [4](../../004_kubernetes_namespace/02_LAB/README.md), [5](../../005_kubernetes_replicaset/02_LAB/README.md) และ [6](../../006_kubernetes_service/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`) และมีโฟลเดอร์ `007_kubernetes_deployment` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `007_kubernetes_deployment` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 007_kubernetes_deployment k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ บทนี้มีสำเนาแอปร้านน้องส้มของตัวเอง (`02_LAB/som-shop-v3/app`) จึง **ไม่ต้องมีโฟลเดอร์ของบทที่ 6** ใน container ก็ทำได้ครบ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` หน้าต่างนี้คือ **terminal 1** (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/007_kubernetes_deployment/02_LAB
ls labs som-shop-v3
kubectl get nodes
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 6 ยังอยู่) | **ใช้ต่อได้เลย** ไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `time k8s-up` (ประมาณ 1 นาที) image ที่เคย `kind load` ในบทก่อนจะหายไป ต้อง build/load ใหม่ในขั้นที่ 5 |

ผลจริงของ `time k8s-up` บนคลัสเตอร์ใหม่ (ตัดบางส่วน)

```text
[k8s-up] dockerd ready
[k8s-up] kind create cluster --name lab --config /etc/devtools/kind/kind-lab.yaml
Creating cluster "lab" ...
 ✓ Ensuring node image (kindest/node:v1.37.0) 🖼️
 ✓ Preparing nodes 📦 📦 📦 
 ...
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-lab"
...
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
...
  NodePort ที่ map ออก host: 30080 30081 30082

real	0m53.715s
```

```text
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   34s   v1.37.0
lab-worker          Ready    <none>          20s   v1.37.0
lab-worker2         Ready    <none>          20s   v1.37.0
```

### ขั้นที่ 4: ตรวจพอร์ต 30080–30082 และ namespace ที่ค้าง

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get svc -A | grep -E '3008[0-2]' || echo '(ไม่มี Service ใช้ 30080-30082)'
kubectl get ns
```

```text
(ไม่มี Service ใช้ 30080-30082)
NAME                 STATUS   AGE
default              Active   34s
kube-node-lease      Active   34s
kube-public          Active   34s
kube-system          Active   34s
local-path-storage   Active   30s
```

ถ้ายังเห็น Service ใช้ 30080 หรือ namespace `som-shop` ค้างจากบทที่ 6 ให้ลบก่อน (`kubectl delete ns som-shop`) ถ้าเป็นตัวอย่างของบทที่ 1 ให้ `kubectl delete -f /workspace/examples/web-deployment.yaml`

### ขั้นที่ 5: ตรวจ image ของร้านบน Node (ถ้าไม่มีให้ build และ load)

LAB 10 ใช้ `som-shop-web:1.2`/`1.3` ที่ build เอง (ไม่มีใน Docker Hub) และ `postgres:17.11-alpine` ถ้าใช้คลัสเตอร์เดิมจากบทที่ 6 image เหล่านี้น่าจะยังอยู่ ตรวจด้วย `crictl` ภายใน Node

🐧 **ใน SSH session ของ k8s-lab**

```bash
docker exec lab-worker crictl images | grep -E "som-shop-web|postgres"
docker exec lab-worker2 crictl images | grep -E "som-shop-web|postgres"
```

ถ้าเห็นครบ 3 บรรทัดบนทั้งสอง worker (ตัวอย่างผลด้านล่าง) **ข้ามไปขั้นที่ 6 ได้เลย**

```text
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  2c6639fdf3a05       76.6MB
docker.io/library/som-shop-web                  1.3                  3e4974056955d       76.6MB
```

ถ้าไม่เห็น (เช่น คลัสเตอร์ใหม่) ให้ build รุ่น 1.2 และ 1.3 จาก **สำเนาแอปในบทนี้** โค้ดเดียวกัน ต่างกันแค่ build-arg แล้ว `kind load` ให้ทุก Node และเตรียม postgres

```bash
cd /workspace/007_kubernetes_deployment/02_LAB/som-shop-v3/app
time docker build -q --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 .
time docker build -q --build-arg APP_VERSION=1.3 --build-arg APP_THEME=sunset -t som-shop-web:1.3 .
time kind load docker-image som-shop-web:1.2 som-shop-web:1.3 --name lab
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o ../pg.tar && kind load image-archive ../pg.tar --name lab && rm ../pg.tar)
docker exec lab-worker crictl images | grep -E "som-shop-web|postgres"
```

ผลจริง (ตัดบางส่วน)

```text
sha256:b42e2cbaa90d7ff2edfce2542830e9f3843c39d3f5696cf2fed2e280d5d66623

real	0m28.967s
...
sha256:6087441e8e95f791ff3618709aeec33857f2f5abf7fb090c418b516ab11b5a44

real	0m0.886s
...
Image: "som-shop-web:1.2" with ID "sha256:b42e2cbaa90d7ff2edfce2542830e9f3843c39d3f5696cf2fed2e280d5d66623" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.2" with ID "sha256:b42e2cbaa90d7ff2edfce2542830e9f3843c39d3f5696cf2fed2e280d5d66623" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.2" with ID "sha256:b42e2cbaa90d7ff2edfce2542830e9f3843c39d3f5696cf2fed2e280d5d66623" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.3" with ID "sha256:6087441e8e95f791ff3618709aeec33857f2f5abf7fb090c418b516ab11b5a44" not yet present on node "lab-worker", loading...
...
real	0m5.991s
docker.io/library/postgres:17.11-alpine

real	0m16.297s
...
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  2c6639fdf3a05       76.6MB
docker.io/library/som-shop-web                  1.3                  3e4974056955d       76.6MB
```

- build รุ่น 1.2 ราว 29 วินาที (ดาวน์โหลด dependency และคอมไพล์) รุ่น 1.3 ไม่ถึง 1 วินาทีเพราะใช้ cache เดิม (เครื่องนักศึกษาอาจนานกว่านี้หลายเท่า)
- postgres เป็น image หลาย platform จึงใช้ `docker save --platform linux/amd64` + `kind load image-archive` (ไฟล์ `pg.tar` ชั่วคราวอยู่ใน `som-shop-v3/` แล้วถูกลบทันที)

> **ข้อสังเกต:** อีกวิธีที่ใช้ดู image บน Node คือ `kubectl get node lab-worker -o jsonpath='{.status.images[*].names}'` แต่ข้อมูลนี้ **อัปเดตช้า** ในการทดลองจริง ทันทีหลัง `kind load` ยังว่าง และราว 30–60 วินาทีต่อมาจึงเห็น `["docker.io/library/import-2026-10-05@sha256:…","docker.io/library/som-shop-web:1.2"]` (ชื่อมี prefix `docker.io/library/`) จึงแนะนำ `crictl images` ซึ่งเห็นทันที

### ขั้นที่ 6: เข้าโฟลเดอร์ของ LAB 1–9

```bash
cd /workspace/007_kubernetes_deployment/02_LAB/labs
pwd
```

LAB 1–9 รันจากโฟลเดอร์นี้ (เส้นทางไฟล์ในคำสั่งทั้งหมดเป็นแบบสัมพัทธ์ เช่น `lab01-deployment/`)

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node พร้อม NodePort 30080–30082 ว่าง และไม่มี namespace ของบทก่อนค้าง
- `som-shop-web:1.2`/`1.3` และ `postgres:17.11-alpine` อยู่บน Node (ตรวจด้วย `crictl images`)

**คำถามชวนคิด**

1. ทำไม `nginx` และ `busybox` จึงไม่ต้อง `kind load` แต่ `som-shop-web` ต้อง load
2. ถ้าลืม load `som-shop-web:1.3` แล้วไปสั่ง `set image ... som-shop-web:1.3` ใน LAB 10 จะเห็นอาการแบบไหน (เทียบกับรุ่น 1.4 ใน LAB 10 ขั้น 10.8)

---

## LAB 1: Deployment แรก: deploy → rs → pod

<p align="center" id="fig-2">
  <img src="images/02-lab1-first-deployment.png" alt="รูปที่ 2 LAB 1 Deployment แรก" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: Deployment web (nginx หน้าเว็บบอกเวอร์ชันและชื่อ Pod) → เห็น deploy → rs → pod, pod-template-hash, strategy default 25%/25% แล้ว scale 3→5→2 (rollout history ยังเป็น revision 1)</em>
</p>

**เป้าหมาย:** สร้าง Deployment แรก เห็นสายเจ้าของ Deployment → ReplicaSet → Pod, `pod-template-hash`, ค่า default ของ strategy และพิสูจน์ว่า scale ไม่สร้าง revision และแก้ ReplicaSet ที่มีเจ้าของตรง ๆ ไม่ได้

**ไฟล์:** `lab01-deployment/00-ns.yaml` (namespace `deploy-lab` ใช้ต่อถึง LAB 3), `lab01-deployment/web.yaml` (Deployment `web` nginx:1.27-alpine, `VERSION=v1`, 3 replicas, readinessProbe ทุก 2 วินาที)

### ขั้นที่ 1: ดูโครง YAML จาก --dry-run

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl create deployment web --image=nginx:1.27-alpine --replicas=3 --dry-run=client -o yaml
```

```text
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: web
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  strategy: {}
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - image: nginx:1.27-alpine
        name: nginx
        resources: {}
status: {}
```

คำสั่งนี้ไม่สร้างอะไรในคลัสเตอร์ ไฟล์ `lab01-deployment/web.yaml` เริ่มจากโครงนี้ แล้วเติม namespace, ชื่อ container `web`, `env VERSION`, `command`, `ports`, `readinessProbe` และ `resources` เปิดดูไฟล์จริงด้วย `cat lab01-deployment/web.yaml`

### ขั้นที่ 2: สร้าง Deployment แล้วรอ rollout

```bash
kubectl apply -f lab01-deployment/
time kubectl -n deploy-lab rollout status deploy/web
kubectl -n deploy-lab get deploy,rs,pods --show-labels
```

```text
namespace/deploy-lab created
deployment.apps/web created
Waiting for deployment "web" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 2 of 3 updated replicas are available...
deployment "web" successfully rolled out

real	0m9.266s
...
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/web   3/3     3            3           10s   app=web

NAME                             DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web-779cb4fbb8   3         3         3       10s   app=web,pod-template-hash=779cb4fbb8

NAME                       READY   STATUS    RESTARTS   AGE   LABELS
pod/web-779cb4fbb8-4jwkw   1/1     Running   0          10s   app=web,pod-template-hash=779cb4fbb8
pod/web-779cb4fbb8-6xw2m   1/1     Running   0          10s   app=web,pod-template-hash=779cb4fbb8
pod/web-779cb4fbb8-9nkmg   1/1     Running   0          10s   app=web,pod-template-hash=779cb4fbb8
```

- Deployment `web` สร้าง ReplicaSet `web-779cb4fbb8` (ชื่อ = `<deploy>-<hash>`) และ Pod ชื่อ `web-779cb4fbb8-<สุ่ม 5 ตัว>`
- label `pod-template-hash=779cb4fbb8` ติดทั้ง ReplicaSet และ Pod ส่วน Deployment มีแค่ `app=web`
- `READY 3/3 UP-TO-DATE 3 AVAILABLE 3` = ครบ เป็นรุ่นล่าสุดทั้งหมด และใช้งานได้ (ค่า hash ในเครื่องนักศึกษาอาจต่างจากนี้)

### ขั้นที่ 3: ค่า default, ownerReferences และ annotation

```bash
kubectl -n deploy-lab get deploy web -o jsonpath='{.spec.strategy}{"\n"}{.spec.revisionHistoryLimit}{"\n"}{.spec.progressDeadlineSeconds}{"\n"}{.spec.minReadySeconds}{"\n"}'
kubectl -n deploy-lab get rs -o jsonpath='{.items[0].metadata.ownerReferences}{"\n"}'
kubectl -n deploy-lab get pod -o jsonpath='{.items[0].metadata.ownerReferences}{"\n"}'
kubectl -n deploy-lab get rs -o jsonpath='{.items[0].metadata.annotations}{"\n"}'
```

```text
{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"}
10
600

[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"web","uid":"df93403a-b04f-4633-a0bc-f94d32833573"}]
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"ReplicaSet","name":"web-779cb4fbb8","uid":"c2f94260-85e8-45c5-86a7-cac80342ce47"}]
{"deployment.kubernetes.io/desired-replicas":"3","deployment.kubernetes.io/max-replicas":"4","deployment.kubernetes.io/revision":"1"}
```

- ไฟล์ไม่ได้เขียน strategy จึงได้ default: RollingUpdate `maxSurge 25%` / `maxUnavailable 25%`, `revisionHistoryLimit 10`, `progressDeadlineSeconds 600` และ `minReadySeconds` ว่าง (= 0)
- สายเจ้าของ: ReplicaSet → **Deployment `web`**, Pod → **ReplicaSet `web-779cb4fbb8`**
- annotation `revision: 1` คือเลขหน้าในสมุดบันทึกรุ่น และ `max-replicas: 4` คือเพดานระหว่าง rollout (3 + maxSurge 1)

### ขั้นที่ 4: scale ไม่ทำให้เกิด revision ใหม่

```bash
kubectl -n deploy-lab scale deploy web --replicas=5 && sleep 3 && kubectl -n deploy-lab get deploy,rs
kubectl -n deploy-lab scale deploy web --replicas=2 && sleep 3 && kubectl -n deploy-lab get deploy,rs,pods
kubectl -n deploy-lab scale deploy web --replicas=3 && kubectl -n deploy-lab rollout status deploy/web && kubectl -n deploy-lab rollout history deploy/web
```

```text
deployment.apps/web scaled
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   5/5     5            5           21s

NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/web-779cb4fbb8   5         5         5       21s
deployment.apps/web scaled
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   2/2     2            2           24s

NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/web-779cb4fbb8   2         2         2       24s
...
deployment.apps/web scaled
Waiting for deployment "web" rollout to finish: 2 of 3 updated replicas are available...
deployment "web" successfully rolled out
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
```

ReplicaSet ตัวเดิมแค่ปรับ DESIRED เป็น 5, 2, 3 ไม่มี ReplicaSet ใหม่ และ `rollout history` ยังมี **revision 1 แถวเดียว** เพราะ `replicas` อยู่นอก template (ทฤษฎีหัวข้อ 3)

<p align="center" id="fig-3">
  <img src="images/03-lab1-rs-scale-reverted.png" alt="รูปที่ 3 LAB 1 scale RS ตรงถูกปรับกลับ" width="900"><br>
  <em><b>รูปที่ 3</b> LAB1 (ต่อ): ลอง scale RS ที่ Deployment เป็นเจ้าของตรง ๆ → ถูกปรับกลับ; ลบ Pod หนึ่งตัว → หัวหน้ากะสร้างแทน (ชื่อใหม่ hash เดิม)</em>
</p>

### ขั้นที่ 5: ลอง scale ReplicaSet ที่มีเจ้าของตรง ๆ

เปิด **terminal 2** (SSH อีกหน้าต่าง `cd` ไป `02_LAB/labs`) เฝ้าดู Pod พร้อมชนิดของ event

```bash
kubectl -n deploy-lab get pods -w --output-watch-events
```

กลับมาที่ **terminal 1** เก็บชื่อ ReplicaSet ใส่ตัวแปรแล้ว scale เป็น 6

```bash
RS=$(kubectl -n deploy-lab get rs -l app=web -o jsonpath="{.items[0].metadata.name}"); echo RS=$RS
kubectl -n deploy-lab scale rs $RS --replicas=6
sleep 6; kubectl -n deploy-lab get rs,pods
kubectl -n deploy-lab get events --sort-by=.lastTimestamp | tail -12
```

ผลจริงใน terminal 2 (ตัดบางส่วน)

```text
EVENT      NAME                   READY   STATUS    RESTARTS   AGE
ADDED      web-779cb4fbb8-6xw2m   1/1     Running   0          32s
ADDED      web-779cb4fbb8-rtl76   1/1     Running   0          14s
ADDED      web-779cb4fbb8-tcw8z   1/1     Running   0          7s
ADDED      web-779cb4fbb8-nfzp7   0/1     Pending   0          0s
ADDED      web-779cb4fbb8-dp4d2   0/1     Pending   0          0s
ADDED      web-779cb4fbb8-j8d8z   0/1     Pending   0          0s
...
MODIFIED   web-779cb4fbb8-nfzp7   0/1     ContainerCreating   0          0s
MODIFIED   web-779cb4fbb8-j8d8z   0/1     Terminating         0          0s
...
DELETED    web-779cb4fbb8-dp4d2   0/1     ContainerStatusUnknown   0          1s
DELETED    web-779cb4fbb8-nfzp7   0/1     ContainerStatusUnknown   0          1s
DELETED    web-779cb4fbb8-j8d8z   0/1     ContainerStatusUnknown   0          1s
```

ผลจริงใน terminal 1

```text
RS=web-779cb4fbb8
replicaset.apps/web-779cb4fbb8 scaled
NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/web-779cb4fbb8   3         3         3       39s

NAME                       READY   STATUS    RESTARTS   AGE
pod/web-779cb4fbb8-6xw2m   1/1     Running   0          39s
pod/web-779cb4fbb8-rtl76   1/1     Running   0          21s
pod/web-779cb4fbb8-tcw8z   1/1     Running   0          14s
...
7s          Normal    SuccessfulDelete    replicaset/web-779cb4fbb8   Deleted pod: web-779cb4fbb8-dp4d2
7s          Normal    SuccessfulCreate    replicaset/web-779cb4fbb8   Created pod: web-779cb4fbb8-j8d8z
7s          Normal    SuccessfulCreate    replicaset/web-779cb4fbb8   Created pod: web-779cb4fbb8-nfzp7
...
7s          Normal    ScalingReplicaSet   deployment/web              Scaled down replica set web-779cb4fbb8 from 6 to 3
```

ReplicaSet ทำตามคำสั่งจริง (สร้าง Pod เพิ่ม 3 ตัว) แต่ Deployment controller ปรับกลับเป็น 3 **ภายในราว 1 วินาที** Pod ส่วนเกินถูกลบตั้งแต่ยังสร้างไม่เสร็จ (สถานะ `ContainerStatusUnknown` ชั่วครู่) กด Ctrl+C ใน terminal 2 เพื่อหยุดดู

### ขั้นที่ 6: ลบ Pod หนึ่งตัว

```bash
P=$(kubectl -n deploy-lab get pod -l app=web -o name | head -1); kubectl -n deploy-lab delete $P; kubectl -n deploy-lab get pods --show-labels
```

```text
pod "web-779cb4fbb8-6xw2m" deleted from deploy-lab namespace
NAME                   READY   STATUS    RESTARTS   AGE   LABELS
web-779cb4fbb8-rtl76   1/1     Running   0          27s   app=web,pod-template-hash=779cb4fbb8
web-779cb4fbb8-tcw8z   1/1     Running   0          20s   app=web,pod-template-hash=779cb4fbb8
web-779cb4fbb8-zjddz   1/1     Running   0          1s    app=web,pod-template-hash=779cb4fbb8
```

ReplicaSet สร้างตัวแทนทันที (ชื่อใหม่ `-zjddz` แต่ hash เดิม เพราะยังเป็นรุ่นเดิม) kubectl 1.37 พิมพ์ข้อความลบเป็น `pod "..." deleted from deploy-lab namespace`

### สิ่งที่เห็น

- Deployment → ReplicaSet `web-<hash>` → Pod `web-<hash>-<สุ่ม>` พร้อม ownerReferences ต่อกันเป็นสายโซ่
- ค่า default: RollingUpdate 25%/25%, `revisionHistoryLimit 10`, `progressDeadlineSeconds 600`
- scale 5 → 2 → 3 ไม่เกิด revision ใหม่ และ scale ReplicaSet ตรง ๆ ถูกปรับกลับในราว 1 วินาที
- ลบ Pod แล้วได้ตัวใหม่ hash เดิม

**คำถามชวนคิด**

1. ทำไม Deployment จึงต้องติด `pod-template-hash` ให้ ReplicaSet ทั้งที่ selector ของ Deployment มีแค่ `app=web`
2. ถ้าอยากได้ 6 บูธจริง ๆ ควรสั่งคำสั่งใด และถ้าไฟล์ `web.yaml` ยังเขียน `replicas: 3` อะไรจะเกิดขึ้นเมื่อ apply ไฟล์นี้อีกครั้ง

> **ยังไม่ต้องลบ namespace** LAB 2 และ 3 ใช้ Deployment `web` ใน `deploy-lab` ต่อ

---

## LAB 2: rolling update ผ่าน Service ClusterIP

<p align="center" id="fig-4">
  <img src="images/04-lab2-rolling-rs.png" alt="รูปที่ 4 LAB 2 RS ใหม่เพิ่ม RS เก่าลด" width="900"><br>
  <em><b>รูปที่ 4</b> LAB2: apply web-v2.yaml (nginx 1.28 + VERSION v2) แล้ว watch RS ใหม่เพิ่มทีละ 1 RS เก่าลดทีละ 1 จนเก่าเหลือ 0 (RS เก่ายังอยู่ไว้ undo)</em>
</p>

**เป้าหมาย:** ดู ReplicaSet รุ่นเก่า/ใหม่ระหว่าง rolling update และผลต่อลูกค้าที่เรียกผ่าน Service

**ต้องมีจาก LAB 1:** Deployment `web` (v1) ใน `deploy-lab`
**ไฟล์:** `lab02-rolling/web-svc.yaml` (Service ClusterIP `web` 80 → `http`), `lab02-rolling/client-pod.yaml` (busybox `client`), `lab02-rolling/web-v2.yaml` (Deployment `web` เดิมแต่ nginx 1.28 + `VERSION=v2` — template เปลี่ยน 2 จุดใน revision เดียว)

### ขั้นที่ 1: สร้าง Service และลูกค้า

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab02-rolling/web-svc.yaml -f lab02-rolling/client-pod.yaml && kubectl -n deploy-lab wait --for=condition=Ready pod/client --timeout=60s
kubectl -n deploy-lab exec client -- sh -c 'for i in 1 2 3 4 5 6; do wget -qO- -T 2 http://web; done'
```

```text
service/web created
pod/client created
pod/client condition met
web v1 from web-779cb4fbb8-tcw8z
web v1 from web-779cb4fbb8-rtl76
web v1 from web-779cb4fbb8-tcw8z
web v1 from web-779cb4fbb8-zjddz
web v1 from web-779cb4fbb8-zjddz
web v1 from web-779cb4fbb8-tcw8z
```

### ขั้นที่ 2: เปลี่ยนรุ่นระหว่างที่ลูกค้ายิงวน

เปิด 3 หน้าต่างพร้อมกัน

**terminal 2** — เฝ้าดู ReplicaSet

```bash
kubectl -n deploy-lab get rs -w
```

**terminal 3** — ลูกค้ายิงวนทุก 0.2 วินาที (พิมพ์ `ERR` ถ้าเรียกไม่ได้)

```bash
kubectl -n deploy-lab exec client -- sh -c "while true; do wget -qO- -T 2 http://web || echo ERR; sleep 0.2; done"
```

**terminal 1** — apply รุ่นใหม่แล้วจับเวลา

```bash
kubectl apply -f lab02-rolling/web-v2.yaml && time kubectl -n deploy-lab rollout status deploy/web
```

ผลจริงใน terminal 1

```text
deployment.apps/web configured
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "web" rollout to finish: 2 out of 3 new replicas have been updated...
...
Waiting for deployment "web" rollout to finish: 1 old replicas are pending termination...
deployment "web" successfully rolled out

real	0m17.521s
```

ผลจริงใน terminal 2 (ตัดบรรทัดซ้ำบางส่วน)

```text
NAME             DESIRED   CURRENT   READY   AGE
web-779cb4fbb8   3         3         3       60s
web-7c974c65c6   1         0         0       0s
web-7c974c65c6   1         1         0       0s
web-7c974c65c6   1         1         1       7s
web-779cb4fbb8   2         3         3       70s
web-779cb4fbb8   2         2         2       70s
web-7c974c65c6   2         2         1       7s
web-7c974c65c6   2         2         2       15s
web-779cb4fbb8   1         2         2       78s
web-7c974c65c6   3         2         2       15s
web-779cb4fbb8   1         1         1       78s
web-7c974c65c6   3         3         3       17s
web-779cb4fbb8   0         1         1       80s
web-779cb4fbb8   0         0         0       80s
```

ใน terminal 3 จะเห็นคำตอบ `web v1 from web-779cb4fbb8-...` ปนกับ `web v2 from web-7c974c65c6-...` ช่วงสั้น ๆ แล้วเหลือ v2 ล้วน ผลจริงเมื่อสรุปคำตอบทั้งหมด (ยิงราว 35 วินาที)

```text
     81 web v1 from web-779cb4fbb8-xxxxx
     87 web v2 from web-7c974c65c6-xxxxx
```

ทั้งหมด 168 ครั้ง **ไม่มี `ERR` เลย** กด Ctrl+C ใน terminal 2 และ 3

<p align="center" id="fig-5">
  <img src="images/05-lab2-client-sees-mix.png" alt="รูปที่ 5 LAB 2 client เห็น v1 และ v2 ปนกัน" width="900"><br>
  <em><b>รูปที่ 5</b> LAB2 (ต่อ): Pod client ยิง wget http://web วนทุก 0.2 วิ ระหว่าง rollout เห็นคำตอบ v1 และ v2 ปนกันช่วงสั้น ๆ แล้วเหลือ v2 ล้วน — ชื่อ Service web คงเดิมตลอด</em>
</p>

### ขั้นที่ 3: ดู Events และ ReplicaSet หลัง rollout

🐧 **terminal 1**

```bash
kubectl -n deploy-lab describe deploy web | sed -n "/^Events/,\$p"
kubectl -n deploy-lab get rs -o wide
```

```text
Events:
  Type    Reason             Age                From                   Message
  ----    ------             ----               ----                   -------
  Normal  ScalingReplicaSet  115s               deployment-controller  Scaled up replica set web-779cb4fbb8 from 0 to 3
  Normal  ScalingReplicaSet  97s                deployment-controller  Scaled up replica set web-779cb4fbb8 from 3 to 5
  Normal  ScalingReplicaSet  94s                deployment-controller  Scaled down replica set web-779cb4fbb8 from 5 to 2
  Normal  ScalingReplicaSet  90s                deployment-controller  Scaled up replica set web-779cb4fbb8 from 2 to 3
  Normal  ScalingReplicaSet  82s                deployment-controller  Scaled down replica set web-779cb4fbb8 from 6 to 3
  Normal  ScalingReplicaSet  52s                deployment-controller  Scaled up replica set web-7c974c65c6 from 0 to 1
  Normal  ScalingReplicaSet  45s                deployment-controller  Scaled down replica set web-779cb4fbb8 from 3 to 2
  Normal  ScalingReplicaSet  45s                deployment-controller  Scaled up replica set web-7c974c65c6 from 1 to 2
  Normal  ScalingReplicaSet  37s                deployment-controller  Scaled down replica set web-779cb4fbb8 from 2 to 1
  Normal  ScalingReplicaSet  35s (x2 over 37s)  deployment-controller  (combined from similar events): Scaled down replica set web-779cb4fbb8 from 1 to 0
NAME             DESIRED   CURRENT   READY   AGE    CONTAINERS   IMAGES              SELECTOR
web-779cb4fbb8   0         0         0       116s   web          nginx:1.27-alpine   app=web,pod-template-hash=779cb4fbb8
web-7c974c65c6   3         3         3       53s    web          nginx:1.28-alpine   app=web,pod-template-hash=7c974c65c6
```

- 5 บรรทัดแรกคือสิ่งที่ทำใน LAB 1 (scale และ scale RS ตรงที่ถูกปรับกลับ)
- rolling ของ replicas 3 (+1/−0) สลับกัน: ใหม่ 0→1, เก่า 3→2, ใหม่ 1→2, เก่า 2→1, (ใหม่ 2→3), เก่า 1→0 บรรทัด "ใหม่ 2→3" ถูก **รวม** เข้ากับบรรทัดท้ายเป็น `(combined from similar events)` ระบบจำกัดจำนวน event จึงอาจเห็นไม่ครบทุกบรรทัด ให้ยึดผลของ `get rs -w` เป็นหลัก
- ReplicaSet เก่า `web-779cb4fbb8` เหลือ `0 0 0` **ไม่ถูกลบ** (เก็บไว้ย้อนรุ่น) selector ของสองรุ่นต่างกันที่ `pod-template-hash`
- rollout ใช้ 17.5 วินาที รวมเวลาที่ Node ดึง `nginx:1.28-alpine` ครั้งแรกราว 7 วินาที

### สิ่งที่เห็น

- RS ใหม่เพิ่มทีละ 1 RS เก่าลดทีละ 1 เพราะ replicas 3 คำนวณได้ maxSurge 1 / maxUnavailable 0
- ลูกค้าที่เรียกชื่อ Service `web` เห็น v1/v2 ปนกันช่วงสั้น ๆ แล้วเหลือ v2 รอบนี้ไม่มี error (รอบที่นับละเอียดผ่าน NodePort ใน LAB 7 จะเห็นว่าไม่มี preStop ก็อาจมี error ได้)

**คำถามชวนคิด**

1. ทำไม Service `web` (selector `app=web`) ส่งลูกค้าได้ทั้ง Pod รุ่นเก่าและใหม่ ในขณะที่ ReplicaSet สองรุ่นไม่นับ Pod ปนกัน
2. ถ้า `replicas: 4` แทน 3 ลำดับใน `get rs -w` จะต่างไปอย่างไร (คำนวณ maxSurge/maxUnavailable ก่อน แล้วไปพิสูจน์ใน LAB 4)

---

## LAB 3: history, change-cause, undo, pause/resume และ restart

<p align="center" id="fig-6">
  <img src="images/06-lab3-history-undo.png" alt="รูปที่ 6 LAB 3 history และ undo" width="900"><br>
  <em><b>รูปที่ 6</b> LAB3: ใส่ change-cause ด้วย kubectl annotate ทุกครั้ง ดู rollout history / --revision แล้ว undo --to-revision=2 — revision 2 หายจากรายการกลายเป็นเลขใหม่ (ลืม annotate = ข้อความเดิมถูกสืบทอด)</em>
</p>

**เป้าหมาย:** ใช้สมุดบันทึกรุ่นให้เป็น เห็นกับดักของ change-cause และเลข revision หลัง undo ลอง pause/resume และ restart

**ต้องมีจาก LAB 2:** Deployment `web` (revision 2, v2) + Service `web` + Pod `client` ใน `deploy-lab` LAB นี้ไม่มีไฟล์ของตัวเอง

### ขั้นที่ 1: ใส่ change-cause และดูกับดักการสืบทอด

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl -n deploy-lab rollout history deploy/web
kubectl -n deploy-lab annotate deploy web kubernetes.io/change-cause="v2 nginx 1.28 (apply web-v2.yaml)" && kubectl -n deploy-lab rollout history deploy/web
```

```text
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

deployment.apps/web annotated
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         v2 nginx 1.28 (apply web-v2.yaml)
```

เปลี่ยนรุ่นอีกสองครั้งด้วย `set env` ครั้งแรก annotate ครั้งที่สอง **ตั้งใจลืม** annotate

```bash
kubectl -n deploy-lab set env deploy/web VERSION=v3 && kubectl -n deploy-lab annotate deploy web kubernetes.io/change-cause="v3 set env" && kubectl -n deploy-lab rollout status deploy/web
kubectl -n deploy-lab set env deploy/web VERSION=v4 && kubectl -n deploy-lab rollout status deploy/web && kubectl -n deploy-lab rollout history deploy/web
```

```text
deployment.apps/web env updated
deployment.apps/web annotated
...
deployment "web" successfully rolled out
deployment.apps/web env updated
...
deployment "web" successfully rolled out
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         v2 nginx 1.28 (apply web-v2.yaml)
3         v3 set env
4         v3 set env
```

**กับดัก:** revision 4 (`VERSION=v4`) สืบทอดข้อความ `v3 set env` เพราะ annotation เดิมยังค้างอยู่บน Deployment ดู template ของ revision ใดก็ได้ด้วย `--revision`

```bash
kubectl -n deploy-lab rollout history deploy/web --revision=3
```

```text
deployment.apps/web with revision #3
Pod Template:
  Labels:	app=web
	pod-template-hash=5488545dcf
  Annotations:	kubernetes.io/change-cause: v3 set env
  Containers:
   web:
    Image:	nginx:1.28-alpine
    Port:	80/TCP (http)
    ...
    Readiness:	http-get http://:http/ delay=0s timeout=1s period=2s successThreshold=1 failureThreshold=3
    Environment:
      VERSION:	v3
    ...
```

### ขั้นที่ 2: undo ไป revision 2

```bash
kubectl -n deploy-lab rollout undo deploy/web --to-revision=2 && kubectl -n deploy-lab rollout status deploy/web >/dev/null && kubectl -n deploy-lab rollout history deploy/web
kubectl -n deploy-lab exec client -- sh -c 'for i in 1 2 3 4 5 6; do wget -qO- -T 2 http://web; done'
kubectl -n deploy-lab get rs -o wide
```

```text
Warning: resource deployments/web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
deployment.apps/web rolled back
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
3         v3 set env
4         v3 set env
5         v2 nginx 1.28 (apply web-v2.yaml)

web v2 from web-7c974c65c6-5rxvd
web v2 from web-7c974c65c6-4ghvx
...
NAME             DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES              SELECTOR
web-5488545dcf   0         0         0       16s     web          nginx:1.28-alpine   app=web,pod-template-hash=5488545dcf
web-6f86b7df6b   0         0         0       12s     web          nginx:1.28-alpine   app=web,pod-template-hash=6f86b7df6b
web-779cb4fbb8   0         0         0       2m18s   web          nginx:1.27-alpine   app=web,pod-template-hash=779cb4fbb8
web-7c974c65c6   3         3         3       75s     web          nginx:1.28-alpine   app=web,pod-template-hash=7c974c65c6
```

- revision 2 **หายจากรายการ** กลายเป็น revision 5 และได้ข้อความ change-cause ของรุ่นเป้าหมายกลับมา
- Deployment ขยาย ReplicaSet เดิม `web-7c974c65c6` (hash เดิม) ไม่สร้างตัวใหม่ ลูกค้าเห็น `web v2` ทันที
- **Warning** เตือนว่าของจริงในคลัสเตอร์ไม่ตรงกับไฟล์ที่ apply ล่าสุดแล้ว (undo = แก้ฉุกเฉิน ต้องไปแก้ไฟล์ใน git ให้ตรง)
- ReplicaSet รุ่นเก่า 4 ตัว `0 0 0` คือข้อมูลสำหรับ undo (สูงสุด `revisionHistoryLimit` 10 ตัว)

<p align="center" id="fig-7">
  <img src="images/07-lab3-pause-restart.png" alt="รูปที่ 7 LAB 3 pause/resume และ restart" width="900"><br>
  <em><b>รูปที่ 7</b> LAB3 (ต่อ): pause → set image + set env → resume ได้ revision เดียว; rollout restart = เปลี่ยนแค่ annotation restartedAt ใน template แต่ Pod ใหม่ทุกตัว</em>
</p>

### ขั้นที่ 3: pause แล้วแก้หลายอย่าง

```bash
kubectl -n deploy-lab rollout pause deploy/web && kubectl -n deploy-lab set image deploy/web web=nginx:1.27-alpine && kubectl -n deploy-lab set env deploy/web VERSION=v6 && sleep 3 && kubectl -n deploy-lab get rs && kubectl -n deploy-lab get deploy web
```

```text
deployment.apps/web paused
deployment.apps/web image updated
deployment.apps/web env updated
NAME             DESIRED   CURRENT   READY   AGE
web-5488545dcf   0         0         0       26s
web-6f86b7df6b   0         0         0       22s
web-779cb4fbb8   0         0         0       2m28s
web-7c974c65c6   3         3         3       85s
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
web    3/3     0            3           2m28s
```

แก้ template ไปสองอย่างแต่ **ไม่มี ReplicaSet ใหม่** และ `UP-TO-DATE 0` (Pod ทั้ง 3 ยังเป็นรุ่นก่อน pause) ลองสองคำสั่งระหว่าง pause

```bash
kubectl -n deploy-lab rollout undo deploy/web; echo "exit=$?"
kubectl -n deploy-lab rollout status deploy/web --timeout=5s; echo "exit=$?"
```

```text
Warning: resource deployments/web was previously managed with 'kubectl apply'. ...
error: you cannot rollback a paused deployment; resume it first with 'kubectl rollout resume' and try again
exit=1
Waiting for deployment "web" rollout to finish: 0 out of 3 new replicas have been updated...
error: timed out waiting for the condition
exit=1
```

undo ระหว่าง pause ทำไม่ได้ และ `rollout status` รอไปเรื่อย ๆ (จึงใส่ `--timeout=5s`)

### ขั้นที่ 4: resume ได้ revision เดียว

```bash
kubectl -n deploy-lab annotate deploy web kubernetes.io/change-cause="v6 nginx 1.27 (pause/resume)" --overwrite && kubectl -n deploy-lab rollout resume deploy/web && kubectl -n deploy-lab rollout status deploy/web && kubectl -n deploy-lab get rs && kubectl -n deploy-lab rollout history deploy/web
kubectl -n deploy-lab exec client -- wget -qO- -T 2 http://web
```

```text
deployment.apps/web annotated
deployment.apps/web resumed
...
deployment "web" successfully rolled out
NAME             DESIRED   CURRENT   READY   AGE
web-5488545dcf   0         0         0       35s
web-6f86b7df6b   0         0         0       31s
web-779cb4fbb8   0         0         0       2m37s
web-7c974c65c6   0         0         0       94s
web-8494ccfb97   3         3         3       3s
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
3         v3 set env
4         v3 set env
5         v2 nginx 1.28 (apply web-v2.yaml)
6         v6 nginx 1.27 (pause/resume)

web v6 from web-8494ccfb97-6vdgp
```

การเปลี่ยน image และ env ระหว่าง pause รวมเป็น rollout **ครั้งเดียว** (revision 6, RS `web-8494ccfb97`)

### ขั้นที่ 5: rollout restart

```bash
kubectl -n deploy-lab get pods -l app=web; kubectl -n deploy-lab rollout restart deploy/web && kubectl -n deploy-lab rollout status deploy/web >/dev/null && kubectl -n deploy-lab get deploy web -o jsonpath="{.spec.template.metadata.annotations}{\"\n\"}" && kubectl -n deploy-lab get pods -l app=web && kubectl -n deploy-lab rollout history deploy/web
```

```text
NAME                   READY   STATUS    RESTARTS   AGE
web-8494ccfb97-6vdgp   1/1     Running   0          7s
web-8494ccfb97-gtsfn   1/1     Running   0          6s
web-8494ccfb97-z44fq   1/1     Running   0          5s
deployment.apps/web restarted
{"kubectl.kubernetes.io/restartedAt":"2026-10-05T10:09:39+07:00"}
NAME                   READY   STATUS        RESTARTS   AGE
web-5c488bd646-bc7fz   1/1     Running       0          1s
web-5c488bd646-gwcd8   1/1     Running       0          3s
web-5c488bd646-sqqcl   1/1     Running       0          4s
web-8494ccfb97-6vdgp   1/1     Terminating   0          11s
web-8494ccfb97-gtsfn   0/1     Completed     0          10s
deployment.apps/web 
REVISION  CHANGE-CAUSE
...
6         v6 nginx 1.27 (pause/resume)
7         v6 nginx 1.27 (pause/resume)
```

- `rollout restart` เติม annotation `kubectl.kubernetes.io/restartedAt` ใน **template** จึงได้ hash ใหม่ (`5c488bd646`) Pod ใหม่ทุกตัว image เดิม
- revision 7 **สืบทอด** change-cause ของ revision 6 (กับดักเดียวกับขั้นที่ 1)
- Pod nginx ที่กำลังปิดขึ้น `0/1 Completed` ชั่วครู่ (ปิดสะอาด) ไม่ใช่ความผิดปกติ

### ขั้นที่ 6: เก็บกวาด LAB 1–3

```bash
time kubectl delete ns deploy-lab
```

```text
namespace "deploy-lab" deleted

real	0m11.070s
```

### สิ่งที่เห็น

- CHANGE-CAUSE มาจาก annotation `kubernetes.io/change-cause` ลืม annotate = สืบทอดข้อความเดิม (รวมถึง `rollout restart`)
- `undo --to-revision=2` → history `1, 3, 4, 5` ใช้ RS เดิม และมี Warning เรื่อง last-applied
- pause → แก้หลายอย่าง → resume = revision เดียว undo ระหว่าง pause ไม่ได้
- `rollout restart` = template ใหม่ (annotation `restartedAt`) Pod ใหม่ทุกตัว

**คำถามชวนคิด**

1. ถ้าทีมของคุณใช้ git เก็บ YAML ควรบันทึก change-cause ด้วยวิธีใด จึงไม่เจอกับดักการสืบทอดข้อความ
2. หลัง `rollout undo` ถ้ามีคน `kubectl apply -f lab02-rolling/web-v2.yaml` อีกครั้ง Deployment จะเป็นรุ่นอะไร และ Warning ในขั้นที่ 2 เตือนเรื่องนี้อย่างไร

---

## LAB 4: เทียบ maxSurge/maxUnavailable และ Recreate

<p align="center" id="fig-8">
  <img src="images/08-lab4-strategies.png" alt="รูปที่ 8 LAB 4 เทียบ 3 กลยุทธ์" width="900"><br>
  <em><b>รูปที่ 8</b> LAB4: Deployment 4 replicas 3 แบบ (rolling.yaml default 25%/25% = +1/−1, nosurge.yaml maxSurge 0/maxUnavailable 1, recreate.yaml) set env แล้ว watch จำนวน Pod สูงสุด/Ready ต่ำสุด</em>
</p>

**เป้าหมาย:** เห็นผลของ strategy ต่อจำนวน Pod ระหว่างเปลี่ยนรุ่น และพิสูจน์การคำนวณของ replicas 10

**ไฟล์:** `lab04-strategy/00-ns.yaml` (namespace `strategy-lab`), Deployment 4 replicas 3 ตัวที่มี label `lab=strategy`: `rolling.yaml` (default 25%/25% = +1/−1), `nosurge.yaml` (`maxSurge: 0`, `maxUnavailable: 1`), `recreate.yaml` (`Recreate`) และ `exercise/zero-zero.yaml` (`maxSurge: 0` + `maxUnavailable: 0` ตั้งใจให้ error)

### ขั้นที่ 1: สร้างทั้ง 3 Deployment

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab04-strategy/ && kubectl -n strategy-lab rollout status deploy/rolling && kubectl -n strategy-lab rollout status deploy/nosurge && kubectl -n strategy-lab rollout status deploy/recreate
kubectl -n strategy-lab get deploy -l lab=strategy
```

```text
namespace/strategy-lab created
deployment.apps/nosurge created
deployment.apps/recreate created
deployment.apps/rolling created
...
deployment "rolling" successfully rolled out
deployment "nosurge" successfully rolled out
deployment "recreate" successfully rolled out
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
nosurge    4/4     4            4           20s
recreate   4/4     4            4           20s
rolling    4/4     4            4           20s
```

> ถ้า `zero-zero.yaml` อยู่ในโฟลเดอร์เดียวกัน `apply -f lab04-strategy/` จะพิมพ์ `The Deployment "zero" is invalid: ...` ปนมาด้วย (เกิดจริงตอนทดสอบ) จึงย้ายไฟล์นั้นไว้ใน `exercise/`

### ขั้นที่ 2: เปลี่ยนรุ่นทีละตัวแล้วนับ Pod

ทำซ้ำ 3 รอบ แทน `<name>` ด้วย `rolling`, `nosurge` และ `recreate` ตามลำดับ

**terminal 2** — เฝ้าดู Pod ของ Deployment นั้น

```bash
kubectl -n strategy-lab get pods -l app=rolling -w
```

**terminal 1** — เปลี่ยน env (ไม่ต้องดึง image ใหม่ เร็วและเห็นจังหวะชัด)

```bash
kubectl -n strategy-lab set env deploy/rolling VERSION=v2 && time kubectl -n strategy-lab rollout status deploy/rolling >/dev/null
```

ผลจริงใน terminal 2 ของ `rolling` (ตัดบรรทัดซ้ำ)

```text
NAME                       READY   STATUS    RESTARTS   AGE
rolling-6f877d46b9-9rjxr   1/1     Running   0          25s
rolling-6f877d46b9-pzbl6   1/1     Running   0          25s
rolling-6f877d46b9-rt9wg   1/1     Running   0          25s
rolling-6f877d46b9-xp7xg   1/1     Running   0          25s
rolling-6648b669d8-hdm45   0/1     Pending   0          0s
rolling-6f877d46b9-pzbl6   1/1     Terminating   0          26s
rolling-6648b669d8-hdm45   0/1     ContainerCreating   0          0s
rolling-6648b669d8-fmzss   0/1     Pending             0          0s
...
rolling-6648b669d8-fmzss   1/1     Running             0          1s
rolling-6648b669d8-hdm45   1/1     Running             0          1s
rolling-6f877d46b9-xp7xg   1/1     Terminating         0          27s
rolling-6f877d46b9-9rjxr   1/1     Terminating         0          27s
rolling-6f877d46b9-pzbl6   0/1     Completed           0          27s
rolling-6648b669d8-nlljv   0/1     Pending             0          0s
rolling-6648b669d8-xf9b6   0/1     Pending             0          0s
...
rolling-6f877d46b9-rt9wg   1/1     Terminating         0          28s
...
rolling-6648b669d8-xf9b6   1/1     Running             0          2s
rolling-6f877d46b9-rt9wg   0/1     Completed           0          29s
```

ผลจริงของ `recreate` (ตัดบรรทัดซ้ำ) — Pod เก่าทั้ง 4 ถูกสั่งปิดพร้อมกันก่อน แล้ว Pod ใหม่ทั้ง 4 จึงเกิด

```text
recreate-74448759d4-x7nzs   1/1     Terminating   0          92s
recreate-74448759d4-7mndq   1/1     Terminating   0          92s
recreate-74448759d4-kmfv6   1/1     Terminating   0          92s
recreate-74448759d4-pknqq   1/1     Terminating   0          92s
recreate-74448759d4-7mndq   0/1     Completed     0          93s
recreate-74448759d4-pknqq   0/1     Completed     0          93s
recreate-74448759d4-x7nzs   0/1     Completed     0          93s
recreate-74448759d4-kmfv6   0/1     Completed     0          93s
recreate-755d569859-5s2rs   0/1     Pending       0          0s
recreate-755d569859-kpxkr   0/1     Pending       0          0s
recreate-755d569859-tt5hj   0/1     Pending       0          0s
recreate-755d569859-pxsbv   0/1     Pending       0          0s
...
recreate-755d569859-5s2rs   1/1     Running             0          1s
...
recreate-755d569859-tt5hj   1/1     Running             0          4s
```

> **กับดักการนับ Pod จาก `get pods -w`:** Pod nginx ที่กำลังปิดแสดงเป็น `Terminating` แล้วเป็น `0/1 Completed` ซ้ำหลายบรรทัด ถ้านับทุกชื่อที่เห็นจะได้ตัวเลขเกินจริง (รอบแรกที่ผู้ทดสอบนับรวมตัวที่กำลังปิดได้ rolling 7–8, recreate 8) ให้ **นับเฉพาะ Pod ที่ยังไม่ถูกสั่งปิด** (ไม่นับบรรทัด `Terminating`/`Completed` ของ Pod รุ่นเก่า) และ Recreate สร้าง Pod ใหม่ทันทีที่ Pod เก่าเป็น `Completed` แม้ชื่อยังโผล่ในรายการ

ผู้ทดสอบทำขั้นนี้ 2 รอบ (`VERSION=v2` แล้ว `VERSION=v3`) รอบที่สองนับเฉพาะ Pod ที่ยังไม่ถูกสั่งปิด (ตัวนับของผู้ทดสอบดูจาก `deletionTimestamp`) ได้ผลจริง

**ตาราง LAB 4** Pod สูงสุด/พร้อมต่ำสุดระหว่างเปลี่ยนรุ่น (4 replicas)

| Deployment | strategy | Pod สูงสุด (คาด) | Pod สูงสุด (จริง) | พร้อมต่ำสุด (คาด) | พร้อมต่ำสุด (จริง) | rollout |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `rolling` | 25%/25% → +1/−1 | 5 | **5** | 3 | **3** | 4.9 วินาที |
| `nosurge` | maxSurge 0 / maxUnavailable 1 | 4 | **4** | 3 | **3** | 4.9 วินาที |
| `recreate` | Recreate | 4 | **4** | 0 | **0** (ราว 2 วินาที) | 2.8 วินาที |

ตัวอย่างบันทึกของ `recreate` (เวลา ณ เครื่องทดสอบ)

```text
10:12:59.7 active=4 ready=4 closing=0
10:13:00.9 active=0 ready=0 closing=4
10:13:01.7 active=0 ready=0 closing=3
10:13:01.9 active=4 ready=0 closing=3
10:13:02.6 active=4 ready=0 closing=0
10:13:02.9 active=4 ready=1 closing=0
10:13:03.6 active=4 ready=4 closing=0
```

ช่วง 10:13:00.9 → 10:13:02.9 **ไม่มี Pod พร้อมเลย** ถ้ามีลูกค้าเรียกผ่าน Service ช่วงนี้จะเรียกไม่ได้

อีกวิธีที่ไม่ต้องนับเองคือดูเพดานที่ Deployment controller คำนวณไว้ใน annotation ของ ReplicaSet (ขั้นที่ 3)

### ขั้นที่ 3: replicas 10 → คำนวณแล้วพิสูจน์

คำนวณก่อน: 25% ของ 10 = 2.5 → maxSurge ปัดขึ้น = 3, maxUnavailable ปัดลง = 2 → **สูงสุด 13 พร้อมอย่างน้อย 8**

```bash
kubectl -n strategy-lab patch deploy rolling -p '{"spec":{"replicas":10}}' && kubectl -n strategy-lab rollout status deploy/rolling >/dev/null && kubectl -n strategy-lab get deploy rolling && kubectl -n strategy-lab get rs -l app=rolling -o jsonpath='{range .items[*]}{.metadata.name} {.spec.replicas} {.metadata.annotations.deployment\.kubernetes\.io/max-replicas}{"\n"}{end}'
kubectl -n strategy-lab set env deploy/rolling VERSION=v4 && time kubectl -n strategy-lab rollout status deploy/rolling >/dev/null
```

```text
deployment.apps/rolling patched
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
rolling   10/10   10           10          3m28s
rolling-5dbcbdc455 10 13
rolling-6648b669d8 0 5
rolling-6f877d46b9 0 5
deployment.apps/rolling env updated

real	0m3.140s
```

ReplicaSet ปัจจุบันมี `max-replicas: 13` (RS รุ่นเก่ายังเป็นค่าตอนที่ replicas 4 คือ 5) การ patch `replicas` ไม่สร้าง RS ใหม่ ส่วน `set env VERSION=v4` ทำให้ rollout ผลจริงจากตัวนับ

```text
rolling: Pod active สูงสุด=13 (รวมตัวที่กำลังปิด สูงสุด=18)  Ready ต่ำสุด=8
10:13:33.8 active=10 ready=10 closing=0
10:13:35.1 active=13 ready=8 closing=2
...
10:13:39.7 active=10 ready=10 closing=0
```

ตรงกับที่คำนวณทุกตัว: สูงสุด 13 พร้อมต่ำสุด 8

### ขั้นที่ 4: แบบฝึก maxSurge 0 + maxUnavailable 0

```bash
kubectl apply --dry-run=server -f lab04-strategy/exercise/zero-zero.yaml; echo "exit=$?"
```

```text
The Deployment "zero" is invalid: spec.strategy.rollingUpdate.maxUnavailable: Invalid value: 0: may not be 0 when `maxSurge` is 0
exit=1
```

`--dry-run=server` ให้ API server ตรวจจริงแต่ไม่บันทึก ห้ามเกินและห้ามขาดพร้อมกัน = เปลี่ยนรุ่นไม่ได้ API server จึงปฏิเสธ

### ขั้นที่ 5: เก็บกวาด

```bash
time kubectl delete ns strategy-lab
```

```text
namespace "strategy-lab" deleted

real	0m11.789s
```

### สิ่งที่เห็น

- `rolling` (+1/−1): สูงสุด 5 พร้อมต่ำสุด 3, `nosurge` (+0/−1): สูงสุด 4 พร้อมต่ำสุด 3, `recreate`: พร้อมต่ำสุด 0 ราว 2 วินาที
- replicas 10 → สูงสุด 13 พร้อมต่ำสุด 8 ตรงสูตร (ปัดขึ้น/ปัดลง) และเห็นใน annotation `max-replicas: 13`
- `maxSurge: 0` + `maxUnavailable: 0` ใช้ไม่ได้

**คำถามชวนคิด**

1. Node มีทรัพยากรเหลือพอสำหรับ Pod อีกแค่ 0 ตัว ควรเลือก `rolling` หรือ `nosurge` เพราะอะไร
2. ถ้าแอปของคุณมี 2 replicas และตั้ง `maxUnavailable: 50%` ระหว่างเปลี่ยนรุ่นจะพร้อมอย่างน้อยกี่ตัว ปลอดภัยหรือไม่

---

## LAB 5: readiness และ minReadySeconds ตัดสิน rollout

<p align="center" id="fig-9">
  <img src="images/09-lab5-readiness-minready.png" alt="รูปที่ 9 LAB 5 readiness และ minReadySeconds" width="900"><br>
  <em><b>รูปที่ 9</b> LAB5: minReadySeconds 10 ทำให้ AVAILABLE ตาม READY ช้ากว่า 10 วิ; แพตช์ readiness path ผิด → Pod ใหม่ 0/1 Running rollout ค้าง Pod เก่ายังรับลูกค้า → undo</em>
</p>

**เป้าหมาย:** เห็นว่า "พร้อม" คือสิ่งที่ rollout รอ ทั้งจาก `minReadySeconds` และเมื่อ readiness ล้ม

**ไฟล์:** `lab05-readiness/00-ns.yaml` (namespace `ready-lab`), `lab05-readiness/web-minready.yaml` (Deployment `web` 3 replicas `minReadySeconds: 10` + Service `web` ในไฟล์เดียวกัน), `lab05-readiness/client-pod.yaml`, `lab05-readiness/patches/readiness-broken-patch.yaml` (เปลี่ยน readiness ไป `/nope`)

### ขั้นที่ 1: สร้างและเปลี่ยนรุ่นแบบมี minReadySeconds

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab05-readiness/ && kubectl -n ready-lab wait --for=condition=Ready pod/client --timeout=60s && time kubectl -n ready-lab rollout status deploy/web && kubectl -n ready-lab get deploy web
```

```text
namespace/ready-lab created
pod/client created
deployment.apps/web created
service/web created
pod/client condition met
deployment "web" successfully rolled out
...
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
web    3/3     3            3           12s
```

> ไฟล์ patch อยู่ใน `patches/` จึงไม่ถูกหยิบไปตอน `apply -f lab05-readiness/` ตอนทดสอบครั้งแรกที่ไฟล์ยังอยู่ในโฟลเดอร์เดียวกัน ได้ `error: error validating "lab05-readiness/readiness-broken-patch.yaml": error validating data: [apiVersion not set, kind not set]`

**terminal 2** — เฝ้าดู Deployment

```bash
kubectl -n ready-lab get deploy web -w
```

**terminal 1** — เปลี่ยนรุ่น

```bash
kubectl -n ready-lab set env deploy/web VERSION=v2 && time kubectl -n ready-lab rollout status deploy/web
```

ผลจริงใน terminal 2 (เติมเวลาไว้หน้าบรรทัดเพื่อให้เห็นจังหวะ)

```text
10:14:32 NAME   READY   UP-TO-DATE   AVAILABLE   AGE
10:14:32 web    3/3     3            3           17s
10:14:33 web    3/3     0            3           18s
10:14:33 web    3/3     1            3           18s
10:14:34 web    4/3     1            3           19s
10:14:44 web    4/3     1            4           29s
10:14:44 web    3/3     1            3           29s
10:14:44 web    3/3     2            3           29s
10:14:45 web    4/3     2            3           30s
10:14:55 web    4/3     2            4           40s
10:14:55 web    3/3     2            3           40s
10:14:55 web    3/3     3            3           40s
10:14:56 web    4/3     3            3           41s
10:15:06 web    4/3     3            4           51s
10:15:06 web    3/3     3            3           51s
```

ผลจริงใน terminal 1: `real 0m32.820s`

- ทุกรอบ `READY` ขึ้นเป็น `4/3` ก่อน แล้ว `AVAILABLE` ตามมาเป็น 4 **หลังจากนั้น 10–11 วินาทีพอดี** (= `minReadySeconds: 10`) จากนั้นจึงลด Pod เก่า 1 ตัว
- rollout 3 replicas จึงใช้ 32.8 วินาที (3 รอบ × ~11 วินาที) เทียบกับ LAB 2 ที่ไม่มี minReadySeconds
- `READY 4/3` = มี Pod ที่ ready เกิน replicas ได้ชั่วคราวตาม maxSurge 1

### ขั้นที่ 2: readiness พังระหว่าง rollout

**terminal 2** — เปลี่ยนเป็นลูกค้ายิงวน (Ctrl+C ตัวเดิมก่อน)

```bash
kubectl -n ready-lab exec client -- sh -c "while true; do wget -qO- -T 2 http://web || echo ERR; sleep 0.2; done"
```

**terminal 1** — patch readiness ให้ไปที่ path ที่ไม่มี

```bash
cat lab05-readiness/patches/readiness-broken-patch.yaml
kubectl -n ready-lab patch deploy web --patch-file lab05-readiness/patches/readiness-broken-patch.yaml && sleep 12 && kubectl -n ready-lab get pods && kubectl -n ready-lab get deploy,rs
```

```text
deployment.apps/web patched
NAME                   READY   STATUS    RESTARTS   AGE
client                 1/1     Running   0          76s
web-545bffc4f7-cmx98   0/1     Running   0          12s
web-7b6cd79469-4cs6x   1/1     Running   0          47s
web-7b6cd79469-5q45x   1/1     Running   0          58s
web-7b6cd79469-cftkh   1/1     Running   0          36s
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   3/3     1            3           76s

NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/web-545bffc4f7   1         1         0       12s
replicaset.apps/web-779cb4fbb8   0         0         0       76s
replicaset.apps/web-7b6cd79469   3         3         3       58s
```

Pod ใหม่ `0/1 Running` (container ทำงานแต่ไม่พร้อม) RS ใหม่ค้าง `1 1 0` Pod เก่า 3 ตัวไม่ถูกปิด ดูสาเหตุ

```bash
P=$(kubectl -n ready-lab get pods -l app=web --no-headers | awk "\$2==\"0/1\"{print \$1}" | head -1); kubectl -n ready-lab describe pod $P | sed -n "/^Events/,\$p"
kubectl -n ready-lab get endpointslice -l kubernetes.io/service-name=web; kubectl -n ready-lab get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
kubectl -n ready-lab rollout status deploy/web --timeout=10s; echo "exit=$?"
```

```text
Events:
  Type     Reason     Age               From               Message
  ----     ------     ----              ----               -------
  Normal   Scheduled  12s               default-scheduler  Successfully assigned ready-lab/web-545bffc4f7-cmx98 to lab-worker
  ...
  Warning  Unhealthy  11s               kubelet            spec.containers{web}: Readiness probe failed: Get "http://10.244.2.51:80/nope": dial tcp 10.244.2.51:80: connect: connection refused
  Warning  Unhealthy  1s (x6 over 11s)  kubelet            spec.containers{web}: Readiness probe failed: HTTP probe failed with statuscode: 404
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                         AGE
web-2x4qd   IPv4          80      10.244.2.49,10.244.1.37,10.244.2.50 + 1 more...   76s
10.244.2.49 web-7b6cd79469-5q45x ready=true
10.244.1.37 web-7b6cd79469-4cs6x ready=true
10.244.2.50 web-7b6cd79469-cftkh ready=true
10.244.2.51 web-545bffc4f7-cmx98 ready=false
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
error: timed out waiting for the condition
exit=1
```

- Event แรก `connection refused` (nginx ยังเปิดพอร์ตไม่ทัน) แล้วตามด้วย `statuscode: 404` ซ้ำ ๆ เพราะ `/nope` ไม่มีจริง
- endpoint ของ Pod ใหม่อยู่ใน EndpointSlice แต่ `ready=false` (คอลัมน์ ENDPOINTS แสดงแค่ 3 IP แล้วตัดเป็น `+ 1 more...`)
- ลูกค้าใน terminal 2 ได้ `web v2 from web-7b6cd79469-...` ทุกครั้ง ผลจริงยิง 149 ครั้งได้ v2 ทั้งหมด **ไม่มี ERR**

### ขั้นที่ 3: undo และเก็บกวาด

```bash
kubectl -n ready-lab rollout undo deploy/web && kubectl -n ready-lab rollout status deploy/web && kubectl -n ready-lab get deploy,rs,pods
time kubectl delete ns ready-lab
```

```text
Warning: resource deployments/web was previously managed with 'kubectl apply'. ...
deployment.apps/web rolled back
Waiting for deployment "web" rollout to finish: 1 old replicas are pending termination...
deployment "web" successfully rolled out
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   3/3     3            3           95s
...
NAME                       READY   STATUS        RESTARTS   AGE
pod/client                 1/1     Running       0          95s
pod/web-545bffc4f7-cmx98   0/1     Terminating   0          31s
...
namespace "ready-lab" deleted

real	0m10.527s
```

undo กลับรุ่นก่อนหน้าได้ทันที เพราะ RS `web-7b6cd79469` ยังพร้อมครบ แค่ลบ Pod ที่พังทิ้ง

### สิ่งที่เห็น

- `minReadySeconds: 10` ทำให้ AVAILABLE ตาม READY ช้า 10–11 วินาที และ rollout ช้าลงตาม
- readiness พัง → Pod ใหม่ `0/1 Running` + `Readiness probe failed: HTTP probe failed with statuscode: 404`, rollout ค้าง แต่ Pod เก่ายังรับลูกค้าครบ

**คำถามชวนคิด**

1. ถ้าลบ readinessProbe ออกจาก template ของ LAB นี้ แล้ว patch ให้แอปพังแบบตอบ 404 ทุก path rollout จะค้างหรือเดินหน้า ลูกค้าจะเห็นอะไร
2. `minReadySeconds` ช่วยป้องกันปัญหาแบบไหนที่ readinessProbe อย่างเดียวป้องกันไม่ได้

---

## LAB 6: image ผิด + progressDeadlineSeconds แล้ว undo

<p align="center" id="fig-10">
  <img src="images/10-lab6-broken-rollout.png" alt="รูปที่ 10 LAB 6 rollout พังแล้ว undo" width="900"><br>
  <em><b>รูปที่ 10</b> LAB6: set image เป็น tag ที่ไม่มี → ErrImagePull/ImagePullBackOff, rollout status ล้มเมื่อเกิน progressDeadlineSeconds 30 แต่ Service ยังส่งลูกค้าไป Pod เก่า 3 ตัว แล้ว rollout undo</em>
</p>

**เป้าหมาย:** เห็นว่า rollout ที่ค้างถูกตัดสินด้วย `progressDeadlineSeconds` Service ยังส่งลูกค้าไป Pod เก่า และ Kubernetes ไม่ย้อนรุ่นให้เอง

**ไฟล์:** `lab06-broken/00-ns.yaml` (namespace `broken-lab`), `lab06-broken/web.yaml` (`progressDeadlineSeconds: 30`), `lab06-broken/web-svc.yaml`, `lab06-broken/client-pod.yaml`, `lab06-broken/patches/crash-patch.yaml` (command `exit 1` — เสริม)

### ขั้นที่ 1: สร้างแล้วตั้ง image ที่ไม่มีจริง

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab06-broken/ && kubectl -n broken-lab rollout status deploy/web && kubectl -n broken-lab wait --for=condition=Ready pod/client --timeout=60s
```

```text
namespace/broken-lab created
pod/client created
service/web created
deployment.apps/web created
...
deployment "web" successfully rolled out
pod/client condition met
```

**terminal 2** — ลูกค้ายิงวน

```bash
kubectl -n broken-lab exec client -- sh -c "while true; do wget -qO- -T 2 http://web || echo ERR; sleep 0.2; done"
```

**terminal 1** — ตั้ง tag ที่ไม่มีจริง

```bash
kubectl -n broken-lab set image deploy/web web=nginx:9.99-nope && sleep 4 && kubectl -n broken-lab get pods,rs
```

```text
deployment.apps/web image updated
NAME                       READY   STATUS         RESTARTS   AGE
pod/client                 1/1     Running        0          6s
pod/web-779cb4fbb8-44w5b   1/1     Running        0          6s
pod/web-779cb4fbb8-rvzfz   1/1     Running        0          6s
pod/web-779cb4fbb8-x6vbw   1/1     Running        0          6s
pod/web-b6c6fccd4-9k8nv    0/1     ErrImagePull   0          4s

NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/web-779cb4fbb8   3         3         3       6s
replicaset.apps/web-b6c6fccd4    1         1         0       4s
```

### ขั้นที่ 2: รอจนเกิน deadline

```bash
time kubectl -n broken-lab rollout status deploy/web; echo "exit=$?"
kubectl -n broken-lab get deploy web; kubectl -n broken-lab get pods,rs
```

```text
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
error: deployment "web" exceeded its progress deadline

real	0m26.601s
...
exit=1
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
web    3/3     1            3           37s
...
pod/web-b6c6fccd4-9k8nv    0/1     ErrImagePull   0          35s
...
replicaset.apps/web-779cb4fbb8   3         3         3       37s
replicaset.apps/web-b6c6fccd4    1         1         0       35s
```

ราว 30 วินาทีหลัง `set image` (`progressDeadlineSeconds: 30`) `rollout status` จบด้วย `exceeded its progress deadline` และ **exit 1** ส่วน `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` บอกว่าร้านยังขายได้ครบ ดูเหตุผลใน Conditions และ Events

```bash
kubectl -n broken-lab describe deploy web | sed -n "/^Conditions/,/^Events/p"
kubectl -n broken-lab get deploy web -o jsonpath='{range .status.conditions[*]}{.type}={.status} {.reason}: {.message}{"\n"}{end}'
P=$(kubectl -n broken-lab get pods -l app=web --no-headers | awk "\$2==\"0/1\"{print \$1}"); kubectl -n broken-lab describe pod $P | sed -n "/^Events/,\$p"
```

```text
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    False   ProgressDeadlineExceeded
OldReplicaSets:  web-779cb4fbb8 (3/3 replicas created)
NewReplicaSet:   web-b6c6fccd4 (1/1 replicas created)
Events:
Available=True MinimumReplicasAvailable: Deployment has minimum availability.
Progressing=False ProgressDeadlineExceeded: ReplicaSet "web-b6c6fccd4" has timed out progressing.
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  36s                default-scheduler  Successfully assigned broken-lab/web-b6c6fccd4-9k8nv to lab-worker
  Normal   Pulling    19s (x2 over 36s)  kubelet            spec.containers{web}: Pulling image "nginx:9.99-nope"
  Warning  Failed     17s (x2 over 34s)  kubelet            spec.containers{web}: Failed to pull image "nginx:9.99-nope": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:9.99-nope": failed to resolve reference "docker.io/library/nginx:9.99-nope": docker.io/library/nginx:9.99-nope: not found
  Warning  Failed     17s (x2 over 34s)  kubelet            spec.containers{web}: Error: ErrImagePull
  Normal   BackOff    4s (x2 over 34s)   kubelet            spec.containers{web}: Back-off pulling image "nginx:9.99-nope"
  Warning  Failed     4s (x2 over 34s)   kubelet            spec.containers{web}: Error: ImagePullBackOff
```

สถานะ Pod สลับไปมาระหว่าง `ErrImagePull` (เพิ่งดึงไม่สำเร็จ) กับ `ImagePullBackOff` (รอก่อนลองใหม่) ลูกค้าใน terminal 2 ได้ `web v1` ตลอด ผลจริงตลอด 60 วินาทีได้ 297 ครั้ง **เป็น v1 ทั้งหมด ไม่มี ERR**

### ขั้นที่ 3: undo เอง

Deployment ไม่ย้อนรุ่นให้ ต้องสั่งเอง

```bash
kubectl -n broken-lab rollout undo deploy/web 2>&1 | grep -v ^Warning; kubectl -n broken-lab rollout status deploy/web && kubectl -n broken-lab get deploy,rs,pods && kubectl -n broken-lab rollout history deploy/web
```

```text
deployment.apps/web rolled back
Waiting for deployment "web" rollout to finish: 1 old replicas are pending termination...
deployment "web" successfully rolled out
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   3/3     3            3           64s

NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/web-779cb4fbb8   3         3         3       64s
replicaset.apps/web-b6c6fccd4    0         0         0       62s
...
pod/web-b6c6fccd4-9k8nv    0/1     Terminating   0          62s
deployment.apps/web 
REVISION  CHANGE-CAUSE
2         <none>
3         <none>
```

(`2>&1 | grep -v ^Warning` แค่ซ่อนข้อความ Warning เรื่อง last-applied ที่เห็นแล้วใน LAB 3) revision 1 กลายเป็น revision 3

### ขั้นที่ 4 (เสริม): แอปล้มทันที → CrashLoopBackOff

```bash
kubectl -n broken-lab patch deploy web --patch-file lab06-broken/patches/crash-patch.yaml && sleep 25 && kubectl -n broken-lab get pods
P=$(kubectl -n broken-lab get pods -l app=web --no-headers | awk "\$2==\"0/1\"{print \$1}"); kubectl -n broken-lab logs $P; kubectl -n broken-lab logs $P --previous; kubectl -n broken-lab get pod $P -o jsonpath="{.status.containerStatuses[0].lastState.terminated}{\"\n\"}"
```

```text
deployment.apps/web patched
NAME                   READY   STATUS             RESTARTS      AGE
client                 1/1     Running            0             89s
web-779cb4fbb8-44w5b   1/1     Running            0             89s
web-779cb4fbb8-rvzfz   1/1     Running            0             89s
web-779cb4fbb8-x6vbw   1/1     Running            0             89s
web-86d8598d79-85drj   0/1     CrashLoopBackOff   2 (10s ago)   25s
แอปรุ่นนี้พัง: ไม่เจอไฟล์ตั้งค่า
แอปรุ่นนี้พัง: ไม่เจอไฟล์ตั้งค่า
{"containerID":"containerd://269971b9...","exitCode":1,"finishedAt":"2026-10-05T03:17:25Z","reason":"Error","startedAt":"2026-10-05T03:17:25Z"}
```

`CrashLoopBackOff` RESTARTS 2 ใน 25 วินาที log บอกสาเหตุ (`--previous` = log ของรอบที่ล้มไปแล้ว) และ `lastState.terminated` บอก `exitCode 1 reason Error` จากนั้นรอ deadline แล้ว undo

```bash
kubectl -n broken-lab rollout status deploy/web; echo "exit=$?"; kubectl -n broken-lab rollout undo deploy/web 2>&1 | grep -v ^Warning; kubectl -n broken-lab rollout status deploy/web; kubectl -n broken-lab get pods
```

```text
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
error: deployment "web" exceeded its progress deadline
exit=1
deployment.apps/web rolled back
Waiting for deployment "web" rollout to finish: 1 old replicas are pending termination...
deployment "web" successfully rolled out
...
web-86d8598d79-85drj   0/1     Terminating   2 (16s ago)   31s
```

### ขั้นที่ 5: เก็บกวาด

```bash
time kubectl delete ns broken-lab
```

```text
namespace "broken-lab" deleted

real	0m10.455s
```

### สิ่งที่เห็น

- image ผิด → `ErrImagePull`/`ImagePullBackOff`, RS ใหม่ `1 1 0`, `rollout status` exit 1 `exceeded its progress deadline`, condition `ProgressDeadlineExceeded`
- `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` — ลูกค้ายังได้ v1 ครบ 297/297 Kubernetes ไม่ rollback ให้ ต้อง `rollout undo` เอง
- แอปล้ม → `CrashLoopBackOff` อ่านสาเหตุด้วย `logs --previous`

**คำถามชวนคิด**

1. ถ้าเขียน pipeline CI/CD ให้ deploy รุ่นใหม่อัตโนมัติ จะใช้ผลลัพธ์อะไรของ `kubectl rollout status` ตัดสินว่าต้อง undo
2. ถ้า Deployment ตั้ง `maxUnavailable: 1` (ไม่ใช่ default ของ replicas 3) แล้ว image ผิด ร้านจะเหลือ Pod พร้อมกี่ตัวระหว่างรอ deadline

---

## LAB 7: zero-downtime ผ่าน NodePort 30080

<p align="center" id="fig-11">
  <img src="images/11-lab7-zero-downtime.png" alt="รูปที่ 11 LAB 7 นับ error ก่อน/หลังใส่ preStop" width="900"><br>
  <em><b>รูปที่ 11</b> LAB7: hit.sh ยิง 300 ครั้งผ่าน NodePort 30080 ระหว่าง rollout เทียบ 2 แบบ: ไม่มี preStop ได้ error 1–4 ครั้ง กับ preStop sleep 5 + maxUnavailable 0 ได้ 0/300 ทั้ง 3 รอบ</em>
</p>

**เป้าหมาย:** นับ error ที่ลูกค้าเห็นระหว่าง rollout ผ่าน NodePort 30080 เทียบแบบไม่มี preStop กับแบบ `preStop` + `maxSurge 1 / maxUnavailable 0`

**ไฟล์:** `lab07-zero-downtime/00-ns.yaml` (namespace `zdt-lab`), `lab07-zero-downtime/web.yaml` (3 replicas strategy default ไม่มี preStop), `lab07-zero-downtime/web-nodeport.yaml` (Service NodePort `30080`), `lab07-zero-downtime/patches/graceful-patch.yaml` (`maxSurge: 1`, `maxUnavailable: 0`, `terminationGracePeriodSeconds: 30`, `preStop.sleep.seconds: 5`) และสคริปต์ `../som-shop-v3/hit.sh`

**hit.sh** (สำเนาจากบทที่ 6) ยิงคำขอด้วย `curl` ใหม่ทุกครั้ง (connection ใหม่ → Service สุ่ม Pod ใหม่ทุกครั้ง) รูปแบบ `./hit.sh [-q] [URL] [N] [DELAY]` ค่าเริ่มต้น URL `http://localhost:30080/api/whoami`, N 60, DELAY 0.1 วินาที โหมด `-q` พิมพ์ `.` (สำเร็จ) / `x` (ล้มเหลว) แล้วสรุป `ok=… err=…` ใน LAB นี้ส่ง URL เป็นหน้าแรกของ nginx `http://localhost:30080/`

### ขั้นที่ 1: เปิด NodePort 30080

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab07-zero-downtime/ && kubectl -n zdt-lab rollout status deploy/web && sleep 2 && curl -s localhost:30080
../som-shop-v3/hit.sh http://localhost:30080/ 30
```

```text
namespace/zdt-lab created
service/web created
deployment.apps/web created
...
deployment "web" successfully rolled out
web v1 from web-779cb4fbb8-4zk8b
จำนวน  Pod  เวอร์ชัน
      9 web v1 from web-779cb4fbb8-4zk8b
     14 web v1 from web-779cb4fbb8-ql6cc
      7 web v1 from web-779cb4fbb8-zzkgv
ok=30 err=0 (ใช้เวลา 3.2 วินาที)
```

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:30080** จะเห็นข้อความ `web v1 from web-...` (refresh แล้วมักได้ Pod เดิมเพราะ keep-alive ของ browser — บทที่ 6) หัวตารางของ hit.sh เขียน `จำนวน  Pod  เวอร์ชัน` เพราะออกแบบไว้สำหรับร้านน้องส้ม แต่ใช้นับหน้า nginx ได้ถูกต้อง

### ขั้นที่ 2: รอบที่ 1 — ไม่มี preStop

**terminal 1** — ยิง 300 ครั้ง (ราว 33 วินาที)

```bash
../som-shop-v3/hit.sh -q http://localhost:30080/ 300
```

**terminal 2** — ภายในไม่กี่วินาทีหลังเริ่มยิง ให้เปลี่ยนรุ่น

```bash
kubectl -n zdt-lab set env deploy/web VERSION=v2 && time kubectl -n zdt-lab rollout status deploy/web >/dev/null
```

ผลจริงใน terminal 1 (rollout ใช้ราว 3.6 วินาที)

```text
.........................................x..xx.x....(ตัดจุด)
ข้อความ error:
      1 curl: (28) Operation timed out
      3 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 2.6 วินาที
ok=296 err=4 (ใช้เวลา 33.9 วินาที)
```

ทำซ้ำอีก 2 รอบ (`VERSION=v3`, `VERSION=v4`) ได้ผลจริง

```text
ข้อความ error:
      1 curl: (28) Operation timed out
      1 curl: (52) Empty reply from server
      2 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 3.4 วินาที
ok=296 err=4 (ใช้เวลา 34.1 วินาที)
...
ข้อความ error:
      1 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 0.0 วินาที
ok=299 err=1 (ใช้เวลา 32.8 วินาที)
```

รวม 3 รอบได้ error **4, 4, 1** จาก 300 ครั้ง ทั้งหมดเกิดช่วงที่ Pod เก่าถูกปิด (ทฤษฎีหัวข้อ 6.1) จำนวนเป็นการสุ่ม เครื่องนักศึกษาอาจได้มากหรือน้อยกว่านี้ (บางรอบอาจเป็น 0)

### ขั้นที่ 3: ใส่ graceful-patch

```bash
cat lab07-zero-downtime/patches/graceful-patch.yaml
kubectl -n zdt-lab patch deploy web --patch-file lab07-zero-downtime/patches/graceful-patch.yaml && time kubectl -n zdt-lab rollout status deploy/web >/dev/null && kubectl -n zdt-lab get deploy web -o jsonpath="{.spec.strategy}{\"\n\"}{.spec.template.spec.containers[0].lifecycle}{\"\n\"}"
```

```text
deployment.apps/web patched

real	0m3.803s
...
{"rollingUpdate":{"maxSurge":1,"maxUnavailable":0},"type":"RollingUpdate"}
{"preStop":{"sleep":{"seconds":5}}}
```

patch นี้แก้ template ด้วย (เพิ่ม `lifecycle` และ grace period) จึงเกิด rollout 1 ครั้ง **รอให้จบก่อน** เริ่มนับรอบที่ 2

### ขั้นที่ 4: รอบที่ 2 — preStop 5 วินาที + maxUnavailable 0

ทำแบบเดียวกับขั้นที่ 2 (terminal 1 `../som-shop-v3/hit.sh -q http://localhost:30080/ 300`, terminal 2 `kubectl -n zdt-lab set env deploy/web VERSION=v5 && time kubectl -n zdt-lab rollout status deploy/web >/dev/null`) ผลจริง 3 รอบ (v5, v6, v7)

```text
rollout status ใช้เวลา 3.9 วินาที
............................................................................................................................................................................................................................................................................................................
ok=300 err=0 (ใช้เวลา 32.0 วินาที)
...
rollout status ใช้เวลา 3.9 วินาที
ok=300 err=0 (ใช้เวลา 31.9 วินาที)
...
rollout status ใช้เวลา 5.7 วินาที
ok=300 err=0 (ใช้เวลา 31.9 วินาที)
```

ทั้ง 3 รอบ **err 0 จาก 300** ถ้ารัน `hit.sh` แบบไม่มี `-q` ระหว่างเปลี่ยนรุ่น จะเห็นทั้งรุ่นเก่าและใหม่ปนกัน ผลจริงเมื่อยิง 200 ครั้งจากเครื่องฝั่งนักศึกษาผ่าน NodePort ระหว่าง `set env VERSION=v8`

```text
จำนวน  Pod  เวอร์ชัน
     35 web v7 from web-7547dd7659-nsmbn
     14 web v7 from web-7547dd7659-wx4n7
     23 web v7 from web-7547dd7659-zqrz9
     41 web v8 from web-5d8fddbb74-dw24d
     47 web v8 from web-5d8fddbb74-kbvmc
     40 web v8 from web-5d8fddbb74-pzzqg
ok=200 err=0 (ใช้เวลา 21.4 วินาที)
```

### ขั้นที่ 5: เก็บกวาด (ต้องทำก่อน LAB 10)

```bash
time kubectl delete ns zdt-lab; kubectl get svc -A | grep -E "3008[0-2]" || echo "(30080 ว่าง)"
```

```text
namespace "zdt-lab" deleted

real	0m27.034s
(30080 ว่าง)
```

ลบ namespace ครั้งนี้ใช้ราว 27 วินาที (นานกว่า LAB อื่น) เพราะ Pod มี `preStop` 5 วินาทีและ grace period 30 วินาที

### สิ่งที่เห็น

- ไม่มี preStop: err 4, 4, 1 จาก 300 (`Connection reset by peer`, `Operation timed out`, `Empty reply from server`)
- preStop 5 + maxSurge 1 / maxUnavailable 0: err 0, 0, 0 จาก 300

**คำถามชวนคิด**

1. ถ้าตั้ง `preStop.sleep.seconds: 40` แต่ `terminationGracePeriodSeconds: 30` จะเกิดอะไรขึ้นกับ Pod ที่กำลังปิด
2. ทำไมรอบแรกบางครั้งได้ error เพียง 1 แต่บางครั้งได้ 4 ทั้งที่คำสั่งเหมือนกัน

---

## LAB 8: ย้าย ReplicaSet เป็น Deployment

<p align="center" id="fig-12">
  <img src="images/12-lab8-migrate-rs.png" alt="รูปที่ 12 LAB 8 Deployment รับเลี้ยง RS เดิม" width="900"><br>
  <em><b>รูปที่ 12</b> LAB8: มี ReplicaSet web (แบบบท 006) อยู่แล้ว → apply Deployment ที่ selector ตรง → ดู ownerReferences ของ RS เดิมชี้ Deployment แล้ว RS เดิมถูก scale 3→0 ระหว่าง rolling (Service ยังตอบตลอด)</em>
</p>

**เป้าหมาย:** ร้านที่ใช้ ReplicaSet แบบบทที่ 6 อยู่แล้ว ย้ายมาเป็น Deployment ชื่อเดิม selector เดิม โดยลูกค้าไม่สะดุด และเห็นการ "รับเลี้ยง" ReplicaSet เดิม

**ไฟล์:** `lab08-migrate/00-ns.yaml` (namespace `migrate-lab`), `lab08-migrate/web-rs.yaml` (ReplicaSet `web` 3 replicas `app=web` VERSION v1), `lab08-migrate/web-svc.yaml`, `lab08-migrate/client-pod.yaml`, `lab08-migrate/web-deploy.yaml` (Deployment `web` selector `app=web` VERSION v2)

### ขั้นที่ 1: สร้างร้านแบบบทที่ 6

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab08-migrate/00-ns.yaml -f lab08-migrate/web-rs.yaml -f lab08-migrate/web-svc.yaml -f lab08-migrate/client-pod.yaml && kubectl -n migrate-lab wait --for=condition=Ready pod -l app=web --timeout=90s && kubectl -n migrate-lab wait --for=condition=Ready pod/client --timeout=60s && kubectl -n migrate-lab get rs,pods --show-labels
```

```text
namespace/migrate-lab created
replicaset.apps/web created
service/web created
pod/client created
...
NAME                  DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web   3         3         3       2s    app=web

NAME            READY   STATUS    RESTARTS   AGE   LABELS
pod/client      1/1     Running   0          2s    role=client
pod/web-nw85z   1/1     Running   0          2s    app=web
pod/web-phg2q   1/1     Running   0          2s    app=web
pod/web-r58mb   1/1     Running   0          2s    app=web
```

ReplicaSet ที่เขียนเองไม่มี `pod-template-hash` ชื่อ Pod จึงเป็น `web-<สุ่ม 5 ตัว>`

### ขั้นที่ 2: apply Deployment ระหว่างที่ลูกค้ายิงวน

**terminal 2** — `kubectl -n migrate-lab get rs -w`

**terminal 3** — `kubectl -n migrate-lab exec client -- sh -c "while true; do wget -qO- -T 2 http://web || echo ERR; sleep 0.2; done"`

**terminal 1**

```bash
kubectl apply -f lab08-migrate/web-deploy.yaml && time kubectl -n migrate-lab rollout status deploy/web
```

```text
deployment.apps/web created
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
...
deployment "web" successfully rolled out

real	0m3.785s
```

ผลจริงใน terminal 2 (ตัดบรรทัดซ้ำ)

```text
NAME   DESIRED   CURRENT   READY   AGE
web    3         3         3       6s
web-7b6cd79469   1         0         0       0s
web-7b6cd79469   1         1         1       2s
web              2         3         3       11s
web              2         2         2       11s
web-7b6cd79469   2         2         2       3s
web              1         2         2       12s
web              1         1         1       12s
web-7b6cd79469   3         3         3       4s
web              0         1         1       13s
web              0         0         0       13s
```

ผลจริงของลูกค้าใน terminal 3 (สรุป)

```text
     30 web v1 from web-xxxxx (Pod ของ RS เดิม)
    143 web v2 from web-7b6cd79469-xxxxx
```

RS `web` เดิมถูก scale 3→2→1→0 สลับกับ RS ใหม่ `web-7b6cd79469` 0→1→2→3 แบบ rolling ปกติ ลูกค้า 173 ครั้ง **ไม่มี ERR**

### ขั้นที่ 3: ตรวจการรับเลี้ยง

```bash
kubectl -n migrate-lab get rs web -o jsonpath='{.metadata.ownerReferences}{"\n"}{.metadata.annotations}{"\n"}{.spec.selector}{"\n"}{.metadata.labels}{"\n"}'
kubectl -n migrate-lab get deploy,rs,pods --show-labels; kubectl -n migrate-lab rollout history deploy/web
kubectl -n migrate-lab describe deploy web | sed -n "/^OldReplicaSets/,\$p"
```

```text
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"web","uid":"0d405a82-4d4c-4556-a59d-c6cbf64d4639"}]
{"deployment.kubernetes.io/desired-replicas":"3","deployment.kubernetes.io/max-replicas":"4","kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"apps/v1\",\"kind\":\"ReplicaSet\",...
{"matchLabels":{"app":"web"}}
{"app":"web"}
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/web   3/3     3            3           42s   app=web

NAME                             DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web              0         0         0       51s   app=web
replicaset.apps/web-7b6cd79469   3         3         3       42s   app=web,pod-template-hash=7b6cd79469

NAME                       READY   STATUS    RESTARTS   AGE   LABELS
pod/client                 1/1     Running   0          51s   role=client
pod/web-7b6cd79469-5c5n8   1/1     Running   0          39s   app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-kr5l2   1/1     Running   0          40s   app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-kwhzj   1/1     Running   0          42s   app=web,pod-template-hash=7b6cd79469
deployment.apps/web 
REVISION  CHANGE-CAUSE
0         <none>
1         <none>

OldReplicaSets:  web (0/0 replicas created)
NewReplicaSet:   web-7b6cd79469 (3/3 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  42s   deployment-controller  Scaled up replica set web-7b6cd79469 from 0 to 1
  Normal  ScalingReplicaSet  40s   deployment-controller  Scaled down replica set web from 3 to 2
  Normal  ScalingReplicaSet  40s   deployment-controller  Scaled up replica set web-7b6cd79469 from 1 to 2
  Normal  ScalingReplicaSet  39s   deployment-controller  Scaled down replica set web from 2 to 1
  Normal  ScalingReplicaSet  39s   deployment-controller  Scaled up replica set web-7b6cd79469 from 2 to 3
  Normal  ScalingReplicaSet  38s   deployment-controller  Scaled down replica set web from 1 to 0
```

- RS `web` เดิมได้ **ownerReferences ชี้ Deployment `web`** และ annotation `desired-replicas`/`max-replicas` แต่ **ไม่มี** annotation `revision` และไม่ได้ label `pod-template-hash`
- `rollout history` มี **REVISION 0** (= RS เดิม) และ 1 (= รุ่นใหม่) `describe` แสดง RS เดิมเป็น `OldReplicaSets`

ลอง undo (เสริม)

```bash
kubectl -n migrate-lab rollout undo deploy/web; echo "exit=$?"; sleep 6; kubectl -n migrate-lab get rs --show-labels; kubectl -n migrate-lab get pods --show-labels; kubectl -n migrate-lab rollout history deploy/web
```

```text
Warning: resource deployments/web was previously managed with 'kubectl apply'. ...
deployment.apps/web rolled back
exit=0
NAME             DESIRED   CURRENT   READY   AGE   LABELS
web              3         3         3       64s   app=web
web-7b6cd79469   0         0         0       55s   app=web,pod-template-hash=7b6cd79469
NAME        READY   STATUS    RESTARTS   AGE   LABELS
client      1/1     Running   0          64s   role=client
web-7897n   1/1     Running   0          6s    app=web
web-bss8k   1/1     Running   0          5s    app=web
web-zkcks   1/1     Running   0          4s    app=web
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

undo กลับไปขยาย RS `web` เดิมได้จริง (Pod ไม่มี hash) และ RS เดิมกลายเป็น revision 2

### ขั้นที่ 4 (เสริม): template เหมือนกันทุกตัวอักษร

เริ่ม namespace ใหม่ที่มีแค่ ReplicaSet แล้ว apply Deployment ที่ใช้ `VERSION v1` เท่ากับ RS (ใช้ `sed` แก้ค่าในไฟล์ระหว่างส่งให้ kubectl โดยไม่แก้ไฟล์จริง)

```bash
kubectl delete ns migrate-lab >/dev/null; kubectl apply -f lab08-migrate/00-ns.yaml -f lab08-migrate/web-rs.yaml >/dev/null && kubectl -n migrate-lab wait --for=condition=Ready pod -l app=web --timeout=90s >/dev/null && kubectl -n migrate-lab get pods
sed "s/value: v2 .*/value: v1/" lab08-migrate/web-deploy.yaml | kubectl apply -f - && sleep 8 && kubectl -n migrate-lab get deploy,rs,pods --show-labels && kubectl -n migrate-lab rollout history deploy/web
```

```text
NAME        READY   STATUS    RESTARTS   AGE
web-drr68   1/1     Running   0          2s
web-rfv4z   1/1     Running   0          2s
web-wgv7n   1/1     Running   0          2s
deployment.apps/web created
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/web   3/3     3            3           8s    app=web

NAME                  DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web   3         3         3       10s   app=web

NAME            READY   STATUS    RESTARTS   AGE   LABELS
pod/web-drr68   1/1     Running   0          10s   app=web
pod/web-rfv4z   1/1     Running   0          10s   app=web
pod/web-wgv7n   1/1     Running   0          10s   app=web
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
```

ไม่มี ReplicaSet ใหม่ ไม่มี Pod ใหม่ RS `web` เดิมกลายเป็น **รุ่นปัจจุบัน (revision 1)** ทันที ผลนี้สำคัญกับ LAB 10 (ฐานข้อมูล `som-db`)

### ขั้นที่ 5 (เสริม): ทางสำรอง --cascade=orphan

```bash
kubectl delete ns migrate-lab >/dev/null; kubectl apply -f lab08-migrate/00-ns.yaml -f lab08-migrate/web-rs.yaml -f lab08-migrate/web-svc.yaml -f lab08-migrate/client-pod.yaml >/dev/null && kubectl -n migrate-lab wait --for=condition=Ready pod -l app=web --timeout=90s >/dev/null && kubectl -n migrate-lab wait --for=condition=Ready pod/client --timeout=60s >/dev/null
kubectl -n migrate-lab delete rs web --cascade=orphan && kubectl -n migrate-lab get rs,pods --show-labels
```

```text
replicaset.apps "web" deleted from migrate-lab namespace
NAME            READY   STATUS    RESTARTS   AGE   LABELS
pod/client      1/1     Running   0          2s    role=client
pod/web-nb7dg   1/1     Running   0          2s    app=web
pod/web-nglsz   1/1     Running   0          2s    app=web
pod/web-vrtjs   1/1     Running   0          2s    app=web
```

เปิดลูกค้ายิงวนใน terminal 3 อีกครั้ง แล้ว apply Deployment และลบ Pod เดิมที่ไม่มี `pod-template-hash`

```bash
kubectl apply -f lab08-migrate/web-deploy.yaml && kubectl -n migrate-lab rollout status deploy/web && kubectl -n migrate-lab get rs,pods --show-labels
kubectl -n migrate-lab delete pod -l "app=web,!pod-template-hash"; kubectl -n migrate-lab get pods --show-labels
```

```text
deployment.apps/web created
...
deployment "web" successfully rolled out
NAME                             DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web-7b6cd79469   3         3         3       1s    app=web,pod-template-hash=7b6cd79469

NAME                       READY   STATUS    RESTARTS   AGE   LABELS
pod/client                 1/1     Running   0          5s    role=client
pod/web-7b6cd79469-9s6jr   1/1     Running   0          1s    app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-dps2l   1/1     Running   0          1s    app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-kj7xw   1/1     Running   0          1s    app=web,pod-template-hash=7b6cd79469
pod/web-nb7dg              1/1     Running   0          5s    app=web
pod/web-nglsz              1/1     Running   0          5s    app=web
pod/web-vrtjs              1/1     Running   0          5s    app=web
pod "web-nb7dg" deleted from migrate-lab namespace
pod "web-nglsz" deleted from migrate-lab namespace
pod "web-vrtjs" deleted from migrate-lab namespace
...
```

ผลจริงของลูกค้าในรอบนี้

```text
      1 ERR
     28 web v1 from web-xxxxx (Pod เดิมที่ไม่มีเจ้าของ)
    119 web v2 from web-7b6cd79469-xxxxx
      1 wget: can't connect to remote host (10.96.60.208): Connection refused
```

Deployment ไม่รับเลี้ยง Pod หลง (selector ของ RS ใหม่มี hash) จึงสร้าง Pod ใหม่ครบ 3 ตัว ช่วงหนึ่งมี 6 Pod หลัง Service และตอนลบ Pod เดิมพร้อมกันลูกค้าเจอ error 1 ครั้ง ทางหลัก (รับเลี้ยง) จึงนุ่มนวลกว่า

### ขั้นที่ 6: เก็บกวาด

```bash
time kubectl delete ns migrate-lab
```

```text
namespace "migrate-lab" deleted

real	0m10.437s
```

### สิ่งที่เห็น

- Deployment รับเลี้ยง RS ที่ไม่มีเจ้าของซึ่ง label ตรง selector: ติด ownerReferences, scale ลงแบบ rolling, โผล่ใน history เป็น REVISION 0, undo กลับไปได้
- template เหมือนกันทุกตัวอักษร → RS เดิมเป็นรุ่นปัจจุบัน ไม่มีอะไรถูกสร้างใหม่
- ทางสำรอง orphan ใช้ได้แต่ต้องลบ Pod เก่าเอง (เจอ error 1 ครั้ง)

**คำถามชวนคิด**

1. ถ้า Deployment ใช้ selector `app: web, tier: front` (ไม่ตรงกับ RS เดิม) จะเกิดอะไรขึ้นกับ RS `web` และ Service `web` ช่วงนั้น
2. ทำไม Pod ใหม่ของ Deployment (มี `app=web`) จึงไม่ถูก RS `web` เดิมนับรวม ทั้งที่ selector ของ RS เดิมคือ `app=web`

---

## LAB 9: blue/green และ canary

<p align="center" id="fig-13">
  <img src="images/13-lab9-blue-green-canary.png" alt="รูปที่ 13 LAB 9 blue/green และ canary" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9: blue/green — Deployment web-blue/web-green + kubectl patch svc เปลี่ยน selector version ทีเดียว; canary — stable 4 + canary 1 ใช้ app=web ร่วมกัน client ยิง 50 ครั้งเห็นรุ่นใหม่ราว 1 ใน 5 (สุ่ม แต่ละรอบไม่เท่ากัน)</em>
</p>

**เป้าหมาย:** สลับรุ่นทั้งร้านด้วย selector ของ Service (blue/green) และแบ่งลูกค้าตามจำนวน Pod (canary)

**ไฟล์:** `lab09-release/00-ns.yaml` (namespace `release-lab`), `web-blue.yaml`/`web-green.yaml` (2 replicas label `version`), `web-svc.yaml` (selector `app=web,version=blue`), `web-stable.yaml` (4 replicas `track=stable`), `web-canary.yaml` (1 replica `track=canary`), `web-svc-all.yaml` (selector `app=web` อย่างเดียว), `client-pod.yaml`

### ขั้นที่ 1: blue/green

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab09-release/00-ns.yaml -f lab09-release/web-blue.yaml -f lab09-release/web-green.yaml -f lab09-release/web-svc.yaml -f lab09-release/client-pod.yaml && kubectl -n release-lab rollout status deploy/web-blue && kubectl -n release-lab rollout status deploy/web-green && kubectl -n release-lab wait --for=condition=Ready pod/client --timeout=60s && kubectl -n release-lab get deploy,pods --show-labels
kubectl -n release-lab exec client -- sh -c 'for i in $(seq 20); do wget -qO- -T 2 http://web; done' | sort | uniq -c
```

```text
...
NAME                             READY   STATUS    RESTARTS   AGE   LABELS
pod/client                       1/1     Running   0          2s    role=client
pod/web-blue-65757d87bc-9dkgq    1/1     Running   0          2s    app=web,pod-template-hash=65757d87bc,version=blue
pod/web-blue-65757d87bc-hd8xl    1/1     Running   0          2s    app=web,pod-template-hash=65757d87bc,version=blue
pod/web-green-7547c8b9d9-94r9t   1/1     Running   0          2s    app=web,pod-template-hash=7547c8b9d9,version=green
pod/web-green-7547c8b9d9-kpwvl   1/1     Running   0          2s    app=web,pod-template-hash=7547c8b9d9,version=green
     10 web blue from web-blue-65757d87bc-9dkgq
     10 web blue from web-blue-65757d87bc-hd8xl
```

ทั้งสองชุดเปิดพร้อมกัน แต่ลูกค้าไปชุด blue ทั้งหมด สลับเป็น green ด้วยคำสั่งเดียว แล้ว **รอ 2 วินาที** ก่อนยิงทดสอบ

```bash
kubectl -n release-lab patch svc web -p '{"spec":{"selector":{"version":"green"}}}'
sleep 2; kubectl -n release-lab exec client -- sh -c 'for i in $(seq 20); do wget -qO- -T 2 http://web; done' | sort | uniq -c
```

```text
service/web patched
     13 web green from web-green-7547c8b9d9-94r9t
      7 web green from web-green-7547c8b9d9-kpwvl
```

> **ข้อควรระวัง (เจอจริงตอนทดสอบ):** ถ้ายิง 20 ครั้งต่อจาก `patch` ทันที (คำขอทั้ง 20 จบในไม่ถึง 1 วินาที) ยังได้ blue ทั้ง 20 ครั้ง และเมื่อ patch กลับเป็น blue แล้วยิงทันทีกลับได้ green ทั้ง 20 ครั้ง เพราะ EndpointSlice และ kube-proxy ยังอัปเดตไม่ทัน เมื่อวัดละเอียดด้วยการยิงทุก 0.1 วินาทีพร้อมเวลา คำขอในวินาทีเดียวกับคำสั่ง patch เริ่มเป็น green แล้ว คือสลับเสร็จภายในไม่ถึง 1 วินาที

ย้อนกลับก็ใช้คำสั่งเดียวกันโดยเปลี่ยนเป็น `"version":"blue"` (ทั้งสองชุดยังรันอยู่ จึงย้อนได้ทันที แลกกับการใช้ทรัพยากร 2 เท่า)

### ขั้นที่ 2: canary

ลบชุด blue/green ถอด `version` ออกจาก selector ของ Service แล้วสร้าง stable 4 + canary 1

```bash
kubectl -n release-lab delete deploy web-blue web-green && kubectl -n release-lab patch svc web --type=json -p '[{"op":"remove","path":"/spec/selector/version"}]' && kubectl -n release-lab get svc web -o jsonpath='{.spec.selector}{"\n"}' && kubectl apply -f lab09-release/web-stable.yaml -f lab09-release/web-canary.yaml && kubectl -n release-lab rollout status deploy/web-stable && kubectl -n release-lab rollout status deploy/web-canary && kubectl -n release-lab get pods -L track
```

```text
deployment.apps "web-blue" deleted from release-lab namespace
deployment.apps "web-green" deleted from release-lab namespace
service/web patched
{"app":"web"}
deployment.apps/web-stable created
deployment.apps/web-canary created
...
NAME                          READY   STATUS      RESTARTS   AGE   TRACK
client                        1/1     Running     0          27s   
web-canary-9f8b957d4-jdlck    1/1     Running     0          2s    canary
web-green-7547c8b9d9-94r9t    0/1     Completed   0          27s   
web-stable-5ff56dccfd-52vzh   1/1     Running     0          2s    stable
web-stable-5ff56dccfd-7ckzs   1/1     Running     0          2s    stable
web-stable-5ff56dccfd-fdmjp   1/1     Running     0          2s    stable
web-stable-5ff56dccfd-h2hgl   1/1     Running     0          2s    stable
```

(`web-green-...` ที่ `0/1 Completed` คือ Pod ของ Deployment ที่เพิ่งลบ กำลังหายไป) ยิง 50 ครั้งแล้วนับตาม track — ทำซ้ำหลายรอบ

```bash
kubectl -n release-lab exec client -- sh -c 'for i in $(seq 50); do wget -qO- -T 2 http://web; done' | awk '{print $2}' | sort | uniq -c
```

```text
      5 canary
     45 stable
```

ผลจริง 7 รอบ (50 ครั้ง/รอบ) ได้ canary **5, 6, 7, 9, 12, 11, 3** ครั้ง แกว่งมากเพราะ kube-proxy เลือกแบบสุ่มต่อ connection เมื่อยิง 500 ครั้งได้ canary **101 ครั้ง (20.2%)** และ stable 4 ตัวได้ 81–108 ครั้งต่อตัว ใกล้สัดส่วน 1 ใน 5 ที่คาด

ทางเลือกแทน `patch --type=json` คือ apply Service ที่ไม่มี `version` ตั้งแต่แรก

```bash
kubectl apply -f lab09-release/web-svc-all.yaml && kubectl -n release-lab get svc web -o jsonpath='{.spec.selector}{"\n"}'
```

```text
service/web configured
{"app":"web"}
```

### ขั้นที่ 3: เก็บกวาด

```bash
time kubectl delete ns release-lab
```

```text
namespace "release-lab" deleted

real	0m10.562s
```

### สิ่งที่เห็น

- blue/green: สลับ selector ของ Service ทีเดียว ลูกค้าย้ายทั้งหมดภายในไม่ถึง 1 วินาที (รอ 1–2 วินาทีก่อนทดสอบ) ย้อนได้ทันที
- canary: แบ่งตามจำนวน Pod 50 ครั้งแกว่ง 3–12 ครั้ง 500 ครั้งได้ 20.2%

**คำถามชวนคิด**

1. ถ้าอยากให้ canary ได้ลูกค้าราว 10% ด้วยวิธีนี้ ต้องตั้ง replicas ของ stable และ canary อย่างไร และมีข้อจำกัดอะไร
2. blue/green ในบทนี้ใช้ Deployment สองตัว ถ้าใช้ Deployment ตัวเดียวแบบ RollingUpdate จะได้ข้อดีข้อใดของ blue/green และเสียข้อใด

---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริง

**เป้าหมาย:** แปลงร้านของบทที่ 6 (ReplicaSet + Service) เป็น Deployment **โดยไม่เปลี่ยนชื่อ Service** แล้วเปลี่ยนรุ่น 1.2 → 1.3, ย้อนรุ่น, เจอรุ่นพัง 1.4, scale และ restart โดยร้านไม่สะดุด พิสูจน์ด้วยตัวเลขจาก `hit.sh` และหน้าร้านจริงใน browser แล้วปิดท้ายด้วยปัญหาข้อมูลหายที่ยังเหลือ

**ต้องมีก่อน:** LAB 0 (image `som-shop-web:1.2`/`1.3` และ postgres อยู่บน Node) และ **ลบ namespace `zdt-lab` ของ LAB 7 แล้ว** (30080 ว่าง)

### 10.1 สถาปัตยกรรมและไฟล์

<p align="center" id="fig-14">
  <img src="images/14-lab10-architecture.png" alt="รูปที่ 14 LAB 10 สถาปัตยกรรมเป้าหมาย" width="900"><br>
  <em><b>รูปที่ 14</b> LAB10: สถาปัตยกรรมเป้าหมาย — Deployment som-web 3 บูธ (RollingUpdate maxSurge 1 / maxUnavailable 0, preStop 5 วิ) + Service NodePort 30080 และ Deployment som-db 1 ตัว (Recreate, emptyDir) + Service ClusterIP som-db ใน namespace som-shop</em>
</p>

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-<hash>-a  Pod som-web-<hash>-b  Pod som-web-<hash>-c   (Deployment som-web, replicas 3→5,
   │                                                                RollingUpdate maxSurge 1 / maxUnavailable 0,
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop    preStop sleep 5, minReadySeconds 3)
                                   ▼
                    Service som-db (ClusterIP, 5432)
                                   ▼
                    Pod som-db-... (Deployment som-db, replicas 1, Recreate, emptyDir)
```

**ตาราง LAB 10** ไฟล์ใน `som-shop-v3/`

| ไฟล์ | เนื้อหา |
|---|---|
| `k8s-rs/00-namespace.yaml` | namespace `som-shop` (Pod Security `warn: restricted`) — สำเนาจากบทที่ 6 |
| `k8s-rs/10-db.yaml` | **ReplicaSet** `som-db` 1 ตัว (postgres:17.11-alpine, `emptyDir`, readiness `pg_isready`) + Service ClusterIP `som-db:5432` — สำเนาจากบทที่ 6 (แก้แค่คอมเมนต์) |
| `k8s-rs/20-web.yaml` | **ReplicaSet** `som-web` 3 ตัว `som-shop-web:1.2` (initContainers `wait-for-db` + `db-seed`, readiness `/api/health`, liveness `/api/live`, footer `LAB 006`, ไม่มี preStop) + Service NodePort `som-web` 30080 |
| `k8s/10-db.yaml` | **Deployment** `som-db` ชื่อ/selector เดิม `replicas: 1`, `strategy: Recreate` Pod spec เหมือน ReplicaSet เดิมทุกตัวอักษร + Service `som-db` เดิม |
| `k8s/20-web.yaml` | **Deployment** `som-web` ชื่อ/selector เดิม `replicas: 3`, `revisionHistoryLimit: 5`, `progressDeadlineSeconds: 60`, `minReadySeconds: 3`, `maxSurge: 1`/`maxUnavailable: 0`, annotation `kubernetes.io/change-cause: "1.2 แปลงเป็น Deployment"`, footer `LAB 007` และ **เพิ่ม** `lifecycle.preStop.sleep.seconds: 5` + Service `som-web` เดิม |
| `hit.sh` | สำเนาจากบทที่ 6 (ดู LAB 7) |
| `app/` | สำเนาแอป Next.js จากบทที่ 6 (โค้ดไม่แก้) |

ส่วนที่เปลี่ยนใน `k8s/20-web.yaml` เทียบกับ `k8s-rs/20-web.yaml` (ไฟล์จริง ตัดบางส่วน)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: som-web
  namespace: som-shop
  labels:
    app: som-web
  annotations:
    kubernetes.io/change-cause: "1.2 แปลงเป็น Deployment"
spec:
  replicas: 3
  revisionHistoryLimit: 5          # เก็บ ReplicaSet รุ่นเก่าไว้ย้อนได้ 5 รุ่น
  progressDeadlineSeconds: 60      # rollout ไม่คืบหน้าเกิน 60 วิ = ล้มเหลว (เห็นในขั้นรุ่นพัง 1.4)
  minReadySeconds: 3               # Pod ใหม่ต้องพร้อมต่อเนื่อง 3 วิ ถึงนับว่าใช้ได้
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                  # เปิดบูธใหม่เกินได้ 1 ตัว
      maxUnavailable: 0            # ห้ามบูธที่พร้อมลดลงเลย → ลูกค้าไม่เจอร้านว่าง
  selector:
    matchLabels:
      app: som-web
  template:
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: web
          image: som-shop-web:1.2
          lifecycle:
            preStop:                 # ถูกสั่งปิดแล้วยังเสิร์ฟต่อ 5 วิ ระหว่างที่ทุก Node ลบบูธนี้ออกจากรายชื่อ
              sleep:
                seconds: 5
```

> ไฟล์จริงมี initContainers, securityContext, env และ probe ครบเหมือนบทที่ 6 ดูทั้งไฟล์ด้วย `cat k8s/20-web.yaml` หรือเทียบความต่างด้วย `diff k8s-rs/20-web.yaml k8s/20-web.yaml`

ใช้ **3 หน้าต่าง** ใน LAB นี้ ทุกหน้าต่าง `cd` ไปที่โฟลเดอร์ร้าน

```bash
cd /workspace/007_kubernetes_deployment/02_LAB/som-shop-v3
```

- **terminal 1:** `hit.sh` นับ ok/err
- **terminal 2:** คำสั่งเปลี่ยนรุ่น
- **terminal 3:** เฝ้าดู (`get rs -w` / `get pods -w`) ตามที่บอกในแต่ละขั้น

### 10.2 เริ่มจากสภาพบทที่ 6

<p align="center" id="fig-15">
  <img src="images/15-lab10-start-from-rs.png" alt="รูปที่ 15 LAB 10 เริ่มจากสภาพบทที่ 6" width="900"><br>
  <em><b>รูปที่ 15</b> LAB10 ขั้น 1: เริ่มจากสภาพบท 006 (apply k8s-rs/) — ร้านเปิดด้วย ReplicaSet + Service แต่ยังไม่มีผู้จัดการร้าน เปลี่ยนรุ่นต้องลบ Pod เอง</em>
</p>

🐧 **terminal 2**

```bash
kubectl apply -f k8s-rs/ && time kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=120s && kubectl -n som-shop get rs,pods,svc
```

```text
namespace/som-shop created
replicaset.apps/som-db created
service/som-db created
replicaset.apps/som-web created
service/som-web created
pod/som-web-gw6mc condition met
pod/som-web-kw4z6 condition met
pod/som-web-x4jkt condition met

real	0m8.235s
...
NAME                      DESIRED   CURRENT   READY   AGE
replicaset.apps/som-db    1         1         1       8s
replicaset.apps/som-web   3         3         3       8s

NAME                READY   STATUS    RESTARTS   AGE
pod/som-db-sdznc    1/1     Running   0          8s
pod/som-web-gw6mc   1/1     Running   0          8s
pod/som-web-kw4z6   1/1     Running   0          8s
pod/som-web-x4jkt   1/1     Running   0          8s

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/som-db    ClusterIP   10.96.177.9    <none>        5432/TCP       8s
service/som-web   NodePort    10.96.194.40   <none>        80:30080/TCP   8s
```

🌐 **browser** เปิด **http://localhost:30080** จะเห็นร้านธีม harbor ป้าย "เวอร์ชัน 1.2" แถบ "เสิร์ฟโดย Pod: som-web-gw6mc · เวอร์ชัน 1.2" (ชื่อ Pod ของ ReplicaSet ไม่มี hash) และท้ายหน้า `Kubernetes LAB 006`

สั่งซื้อ 2 ออเดอร์ (กดปุ่ม "สั่งซื้อ" บนหน้าเว็บก็ได้ หรือใช้ API) แล้วดูการกระจายและยอดออเดอร์

```bash
for p in 1 4; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":2}"; echo; done
./hit.sh && for i in $(seq 6); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":2,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":58}}
จำนวน  Pod  เวอร์ชัน
     22 som-web-gw6mc 1.2
     19 som-web-kw4z6 1.2
     19 som-web-x4jkt 1.2
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
      2 som-web-gw6mc 1.2 orders=2 products=6
      2 som-web-kw4z6 1.2 orders=2 products=6
      2 som-web-x4jkt 1.2 orders=2 products=6
```

นี่คือร้านเดียวกับท้ายบทที่ 6 ถ้าจะเปลี่ยนเป็น 1.3 ตอนนี้ต้องลบ Pod เอง ขั้นต่อไปจะให้ผู้จัดการร้านมาดูแลแทน

### 10.3 แปลง db เป็น Deployment: รับเลี้ยงทันที ไม่สร้างใหม่

**terminal 1** — ยิง `/api/whoami` (ไม่แตะ db) วนไว้ระหว่างแปลง

```bash
./hit.sh -q http://localhost:30080/api/whoami 400
```

**terminal 2**

```bash
kubectl apply -f k8s/10-db.yaml && time kubectl -n som-shop rollout status deploy/som-db
kubectl -n som-shop get deploy,rs,pods -l app=som-db --show-labels; kubectl -n som-shop get rs som-db -o jsonpath="{.metadata.ownerReferences}{\"\n\"}"; kubectl -n som-shop rollout history deploy/som-db
for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
deployment.apps/som-db created
service/som-db unchanged
deployment "som-db" successfully rolled out

real	0m0.040s
...
NAME                     READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/som-db   1/1     1            1           48s   app=som-db

NAME                     DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/som-db   1         1         1       80s   app=som-db

NAME               READY   STATUS    RESTARTS   AGE   LABELS
pod/som-db-sdznc   1/1     Running   0          80s   app=som-db
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"som-db","uid":"e30639ab-de6f-45ce-bcce-f0478aa5e658"}]
deployment.apps/som-db 
REVISION  CHANGE-CAUSE
1         <none>

som-web-x4jkt 1.2 orders=2 products=6
som-web-gw6mc 1.2 orders=2 products=6
som-web-x4jkt 1.2 orders=2 products=6
```

ผลจริงใน terminal 1: `ok=400 err=0`

- template ของ `k8s/10-db.yaml` **เหมือน ReplicaSet เดิมทุกตัวอักษร** (`strategy: Recreate` อยู่นอก template) Deployment จึงรับเลี้ยง RS `som-db` เป็น **รุ่นปัจจุบัน** ทันที (`rollout status` 0.04 วินาที) แบบเดียวกับ LAB 8 ขั้นที่ 4
- Pod `som-db-sdznc` **ตัวเดิม ไม่ถูกสร้างใหม่** ข้อมูลใน `emptyDir` จึงยังอยู่ (`orders=2`) ไม่มีช่วงร้านล่ม และไม่มีหน้า 503
- `Recreate` จะมีผลเมื่อเกิด rollout ครั้งถัดไปของ `som-db` (สาธิตใน [10.11](#1011-เสริม-recreate-ของ-som-db-ของจริง))

### 10.4 แปลง web เป็น Deployment ระหว่างขาย

<p align="center" id="fig-16">
  <img src="images/16-lab10-convert-to-deployment.png" alt="รูปที่ 16 LAB 10 แปลงร้านเป็น Deployment" width="900"><br>
  <em><b>รูปที่ 16</b> LAB10 ขั้น 2: apply k8s/ (Deployment ชื่อ/selector เดิม) — som-db template เหมือน RS เดิมจึงถูกรับเลี้ยงทันที ไม่รีสตาร์ต ข้อมูลยังอยู่ ส่วน som-web รับเลี้ยง RS เดิมแล้วแทนบูธทีละตัว (error 1–2/300 เพราะ Pod เก่ายังไม่มี preStop)</em>
</p>

**terminal 1**

```bash
./hit.sh -q http://localhost:30080/api/whoami 300
```

**terminal 3**

```bash
kubectl -n som-shop get rs -w
```

**terminal 2**

```bash
kubectl apply -f k8s/20-web.yaml && time kubectl -n som-shop rollout status deploy/som-web
```

```text
deployment.apps/som-web created
service/som-web unchanged
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out

real	0m17.724s
```

ผลจริงใน terminal 3 (เติมเวลาหน้าบรรทัด ตัดบรรทัดซ้ำ)

```text
10:29:53 som-web   3         3         3       91s
10:29:56 som-web-7955fccc94   1         0         0       0s
10:29:59 som-web-7955fccc94   1         1         1       3s
10:30:02 som-web              2         3         3       100s
10:30:02 som-web-7955fccc94   2         1         1       6s
10:30:02 som-web              2         2         2       100s
10:30:05 som-web-7955fccc94   2         2         2       9s
10:30:08 som-web              1         2         2       106s
10:30:08 som-web-7955fccc94   3         2         2       12s
10:30:08 som-web              1         1         1       106s
10:30:11 som-web-7955fccc94   3         3         3       15s
10:30:14 som-web              0         1         1       112s
10:30:14 som-web              0         0         0       112s
```

ผลจริงใน terminal 1

```text
..................................................................................x.......................................................x.................................................................................................................................................................
ข้อความ error:
      2 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 6.1 วินาที
ok=298 err=2 (ใช้เวลา 32.5 วินาที)
```

- RS `som-web` เดิมถูกรับเลี้ยงแล้ว scale 3→2→1→0 สลับกับ `som-web-7955fccc94` 0→1→2→3 ห่างกันขั้นละราว 6 วินาที (Pod ใหม่ ready ~3 วินาที + `minReadySeconds: 3`)
- **อาจเห็น error 1–2 ครั้ง** (ผลจริง 2/300 และในรอบทดสอบซ้ำ 1/300) เพราะบูธที่ถูกปิดในขั้นนี้คือ **Pod เดิมของ ReplicaSet บทที่ 6 ซึ่งยังไม่มี preStop** หลังจากนี้ทุกบูธเป็นของ Deployment ที่มี preStop แล้ว การเปลี่ยนรุ่นครั้งต่อ ๆ ไปจะได้ err 0
- ถ้ายิงหน้าแรก `/` พร้อมกัน (`./hit.sh -q http://localhost:30080/ 150 0.2` ใน terminal เพิ่ม) ผลจริงได้ 1/150 และ 0/150 ในสองรอบ

ตรวจผล

```bash
kubectl -n som-shop get deploy,rs,pods -o wide; kubectl -n som-shop get rs som-web -o jsonpath="{.metadata.ownerReferences}{\"\n\"}"; kubectl -n som-shop rollout history deploy/som-web
```

```text
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE    CONTAINERS   IMAGES                  SELECTOR
deployment.apps/som-db    1/1     1            1           115s   postgres     postgres:17.11-alpine   app=som-db
deployment.apps/som-web   3/3     3            3           52s    web          som-shop-web:1.2        app=som-web

NAME                                 DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                  SELECTOR
replicaset.apps/som-db               1         1         1       2m26s   postgres     postgres:17.11-alpine   app=som-db
replicaset.apps/som-web              0         0         0       2m26s   web          som-shop-web:1.2        app=som-web
replicaset.apps/som-web-7955fccc94   3         3         3       52s     web          som-shop-web:1.2        app=som-web,pod-template-hash=7955fccc94

NAME                           READY   STATUS    RESTARTS   AGE     IP             NODE          NOMINATED NODE   READINESS GATES
pod/som-db-sdznc               1/1     Running   0          2m26s   10.244.2.98    lab-worker    <none>           <none>
pod/som-web-7955fccc94-cgjqm   1/1     Running   0          46s     10.244.1.62    lab-worker2   <none>           <none>
pod/som-web-7955fccc94-m4f6r   1/1     Running   0          52s     10.244.2.101   lab-worker    <none>           <none>
pod/som-web-7955fccc94-vs9kw   1/1     Running   0          40s     10.244.2.102   lab-worker    <none>           <none>
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"som-web","uid":"f55bf804-9b63-48d8-9f57-5f2ab2ff3637"}]
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
1         1.2 แปลงเป็น Deployment
```

- Deployment `som-db 1/1`, `som-web 3/3` RS `som-web` เดิม `0 0 0` มีเจ้าของเป็น Deployment และโผล่ใน history เป็น **REVISION 0** ส่วน revision 1 ได้ CHANGE-CAUSE จาก annotation ในไฟล์ YAML
- **ไม่ต้องใช้ทางสำรอง `--cascade=orphan`** เพราะการรับเลี้ยงทำงานได้ (ถ้าวันหนึ่ง selector ไม่ตรง ใช้วิธีใน LAB 8 ขั้นที่ 5)
- Pod `som-db-sdznc` ตัวเดิมยังอยู่

### 10.5 สั่งซื้อเพิ่ม (ใช้พิสูจน์ในขั้นต่อไป)

```bash
for p in 5 6; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done; curl -s localhost:30080/api/stats
```

```text
{"ok":true,"order_id":3,"product":{"id":5,"name_th":"ขนมแมวเลียรสไก่ (แพ็ก 4)","stock":39}}
{"ok":true,"order_id":4,"product":{"id":6,"name_th":"ขนมฟรีซดรายแซลมอน 40 ก.","stock":24}}
som-web-7955fccc94-m4f6r 1.2 orders=4 products=6
```

ออเดอร์รวม **4** (2 ก่อนแปลง + 2 ตอนนี้) เพราะ db ไม่ถูกสร้างใหม่ตอนแปลง

🌐 refresh **http://localhost:30080** (Ctrl+F5) ชื่อ Pod ในแถบ "เสิร์ฟโดย Pod" มี hash แล้ว และท้ายหน้าเป็น `Kubernetes LAB 007 · namespace som-shop`

<p align="center" id="fig-17">
  <img src="images/screenshots/20261005_1044_lab10deploy_01-shop-1.2-deployment.png" alt="รูปที่ 17 ภาพหน้าจอจริง ร้าน 1.2 หลังแปลงเป็น Deployment" width="700"><br>
  <em><b>รูปที่ 17</b> ภาพหน้าจอจริงจากการทดลอง: เปิด http://localhost:30080 (NodePort โดยตรง) หลังแปลงร้านเป็น Deployment — ป้าย "เวอร์ชัน 1.2" แถบ "🐱 เสิร์ฟโดย Pod: som-web-7955fccc94-fjsv6 · เวอร์ชัน 1.2" ชื่อ Pod มี pod-template-hash แล้ว และออเดอร์ทั้งหมด 4 (ข้อมูลเดิมไม่หายเพราะ som-db ถูกรับเลี้ยงโดยไม่สร้าง Pod ใหม่)</em>
</p>

> **หมายเหตุ:** หัวเว็บยังเขียน `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service` เพราะบทนี้ใช้แอปเดิมจากบทที่ 6 (ข้อความนี้ฝังอยู่ในโค้ดของแอป) แต่ร้านตอนนี้ดูแลด้วย Deployment แล้ว ดูได้จากชื่อ Pod ที่มี hash และ `kubectl -n som-shop get deploy`

### 10.6 rolling update 1.2 → 1.3 ระหว่างขาย

<p align="center" id="fig-18">
  <img src="images/17-lab10-rollout-1-3.png" alt="รูปที่ 18 LAB 10 rolling 1.2 → 1.3 ไม่มี error" width="900"><br>
  <em><b>รูปที่ 18</b> LAB10 ขั้น 3: rolling update 1.2 → 1.3 (set image web และ db-seed + annotate change-cause) ระหว่าง hit.sh -q 300 ครั้ง — นับแล้วไม่มี error</em>
</p>

**terminal 1**

```bash
./hit.sh -q http://localhost:30080/api/whoami 300
```

**terminal 3** (ดู Pod ที่กำลังปิด)

```bash
kubectl -n som-shop get pods -w
```

**terminal 2** — เปลี่ยน image ของทั้ง container `web` และ initContainer `db-seed` บันทึกเหตุผล แล้วจับเวลา

```bash
kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.3 ธีม sunset" --overwrite
time kubectl -n som-shop rollout status deploy/som-web
```

```text
deployment.apps/som-web image updated
deployment.apps/som-web annotated
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
```

ผลจริง: rollout ใช้ **18.1 วินาที** (รอบถ่ายภาพหน้าจอ 16.9 วินาที) และ terminal 1

```text
............................................................................................................................................................................................................................................................................................................
ok=300 err=0 (ใช้เวลา 32.5 วินาที)
```

**err = 0 จาก 300** (หน้าแรก `/` 150 ครั้งก็ err 0) ใน terminal 3 จะเห็น Pod เก่าขึ้น `Error` ราว 5 วินาทีหลัง `Terminating`

```text
10:31:11 som-web-7955fccc94-vs9kw   1/1     Terminating       0          63s
10:31:16 som-web-7955fccc94-vs9kw   0/1     Error             0          68s
10:31:17 som-web-7955fccc94-m4f6r   1/1     Terminating       0          81s
10:31:22 som-web-7955fccc94-m4f6r   0/1     Error             0          86s
```

นี่คือ preStop 5 วินาที แล้ว Next.js รับ SIGTERM และออกด้วย exit code ไม่เป็น 0 **ไม่ใช่ rollout พัง** ตรวจผล

```bash
kubectl -n som-shop rollout history deploy/som-web; kubectl -n som-shop get rs -o wide; kubectl -n som-shop get pods
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.initContainers[*].image}{" | "}{.spec.template.spec.containers[*].image}{"\n"}'
```

```text
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
1         1.2 แปลงเป็น Deployment
2         1.3 ธีม sunset

NAME                 DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                  SELECTOR
som-db               1         1         1       3m20s   postgres     postgres:17.11-alpine   app=som-db
som-web              0         0         0       3m20s   web          som-shop-web:1.2        app=som-web
som-web-7955fccc94   0         0         0       106s    web          som-shop-web:1.2        app=som-web,pod-template-hash=7955fccc94
som-web-ffc7b9f94    3         3         3       38s     web          som-shop-web:1.3        app=som-web,pod-template-hash=ffc7b9f94
NAME                      READY   STATUS    RESTARTS   AGE
som-db-sdznc              1/1     Running   0          3m20s
som-web-ffc7b9f94-dl8cm   1/1     Running   0          31s
som-web-ffc7b9f94-g88n9   1/1     Running   0          38s
som-web-ffc7b9f94-v5rnr   1/1     Running   0          25s
postgres:17.11-alpine som-shop-web:1.3 | som-shop-web:1.3
```

`set image` ใช้กับ initContainer ได้ (`db-seed` เป็น 1.3) ส่วน `wait-for-db` ยังเป็น postgres

<p align="center" id="fig-19">
  <img src="images/18-lab10-shop-1-3-page.png" alt="รูปที่ 19 LAB 10 หน้าร้าน 1.3" width="900"><br>
  <em><b>รูปที่ 19</b> LAB10: เปิด http://localhost:30080 บนเครื่องนักศึกษา (Ctrl+F5) เห็นธีม sunset ป้ายเวอร์ชัน 1.3 แบนเนอร์เมนูใหม่ และชื่อ Pod ที่เสิร์ฟ</em>
</p>

🌐 **browser** กด **Ctrl+F5** ที่ http://localhost:30080 จะเห็นธีม sunset (ส้ม–ชมพู) แบนเนอร์ด้านบน `🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟` และแถบ `🐱 เสิร์ฟโดย Pod: som-web-ffc7b9f94-… · เวอร์ชัน 1.3` (ผลจริงจาก curl: `เสิร์ฟโดย Pod: som-web-ffc7b9f94-g88n9 · เวอร์ชัน 1.3` และ footer `Kubernetes LAB 007 · namespace som-shop`) ออเดอร์ยังเป็น 4 เพราะเปลี่ยนแค่ web

<p align="center" id="fig-20">
  <img src="images/screenshots/20261005_1046_lab10deploy_02-shop-1.3-after-rolling-err0.png" alt="รูปที่ 20 ภาพหน้าจอจริง ร้าน 1.3 หลัง rolling err 0" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: หลัง set image 1.3 (rollout 16.9 วินาที ระหว่างนั้น hit.sh ok=300 err=0) หน้าร้านเป็นธีม sunset ป้าย "เวอร์ชัน 1.3" แบนเนอร์ "🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟" แถบ "เสิร์ฟโดย Pod: som-web-ffc7b9f94-scnkp · เวอร์ชัน 1.3" และออเดอร์ยังเป็น 4</em>
</p>

### 10.7 rollout history และ undo สองครั้ง

<p align="center" id="fig-21">
  <img src="images/19-lab10-history-undo.png" alt="รูปที่ 21 LAB 10 history และ undo" width="900"><br>
  <em><b>รูปที่ 21</b> LAB10 ขั้น 4: rollout history เห็น change-cause → rollout undo กลับ 1.2 (ออเดอร์ 4 ยังอยู่ เพราะ db ไม่ถูกแตะ) → undo อีกครั้งกลับ 1.3</em>
</p>

ทำเหมือนขั้นก่อน (terminal 1 ยิง `./hit.sh -q http://localhost:30080/api/whoami 300`) แล้วใน **terminal 2**

```bash
kubectl -n som-shop rollout undo deploy/som-web && kubectl -n som-shop rollout status deploy/som-web
kubectl -n som-shop rollout history deploy/som-web; for i in $(seq 6); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
Warning: resource deployments/som-web was previously managed with 'kubectl apply'. ...
deployment.apps/som-web rolled back
...
deployment "som-web" successfully rolled out
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
2         1.3 ธีม sunset
3         1.2 แปลงเป็น Deployment

      2 som-web-7955fccc94-5hkh9 1.2 orders=4 products=6
      2 som-web-7955fccc94-kbwrx 1.2 orders=4 products=6
      2 som-web-7955fccc94-q2nrb 1.2 orders=4 products=6
```

กลับเป็น 1.2 (RS `som-web-7955fccc94` เดิม) ใน 17.5 วินาที hit.sh `ok=300 err=0` ออเดอร์ **ยังเป็น 4** เพราะ undo เปลี่ยนแค่ web ไม่แตะ db และ schema ของสองรุ่นเข้ากันได้ undo อีกครั้ง (ไม่ระบุ revision = กลับไปรุ่นก่อนหน้า)

```bash
kubectl -n som-shop rollout undo deploy/som-web 2>&1 | grep -v ^Warning; kubectl -n som-shop rollout status deploy/som-web
kubectl -n som-shop rollout history deploy/som-web; for i in $(seq 6); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
deployment.apps/som-web rolled back
...
deployment "som-web" successfully rolled out
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
4         1.3 ธีม sunset

      6 som-web-ffc7b9f94-qtmdt 1.3 orders=4 products=6
```

กลับเป็น 1.3 ใน 18.2 วินาที err 0 อีกครั้ง เลข revision เลื่อนไปเรื่อย ๆ (`0, 2, 3` → `0, 3, 4`) และแต่ละ revision ได้ CHANGE-CAUSE ของรุ่นเป้าหมาย

### 10.8 รุ่นพัง 1.4: rollout ค้างแต่ร้านยังขาย

<p align="center" id="fig-22">
  <img src="images/20-lab10-broken-1-4.png" alt="รูปที่ 22 LAB 10 รุ่นพัง 1.4 แต่ร้านยังขาย" width="900"><br>
  <em><b>รูปที่ 22</b> LAB10 ขั้น 5: set image web=som-shop-web:1.4 (tag ไม่มี) → Pod ใหม่ 1 ตัว ImagePullBackOff (maxUnavailable 0 จึงไม่มีบูธเก่าถูกปิด) → ProgressDeadlineExceeded หลัง 60 วิ แต่ hit.sh ยัง ok ทั้งหมด → undo</em>
</p>

`som-shop-web:1.4` **ไม่มีจริง** (ตั้งใจให้พัง) เปลี่ยนเฉพาะ container `web` (`db-seed` ยังเป็น 1.3)

**terminal 1** — ยิงนานขึ้นให้ครอบช่วง deadline 60 วินาที

```bash
./hit.sh -q http://localhost:30080/api/whoami 700
```

**terminal 2**

```bash
kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.4 && kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.4 (ทดสอบรุ่นพัง)" --overwrite && sleep 8 && kubectl -n som-shop get pods && kubectl -n som-shop get deploy som-web
time kubectl -n som-shop rollout status deploy/som-web; echo "exit=$?"
```

```text
deployment.apps/som-web image updated
deployment.apps/som-web annotated
NAME                       READY   STATUS            RESTARTS   AGE
som-db-sdznc               1/1     Running           0          4m54s
som-web-6cd4d5d687-dqh9r   0/1     PodInitializing   0          8s
som-web-ffc7b9f94-k896q    1/1     Running           0          35s
som-web-ffc7b9f94-qtmdt    1/1     Running           0          41s
som-web-ffc7b9f94-vdmf6    1/1     Running           0          48s
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
som-web   3/3     1            3           3m20s
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
error: deployment "som-web" exceeded its progress deadline
exit=1
```

- 8 วินาทีแรก Pod ใหม่เป็น **`PodInitializing`** (initContainer `wait-for-db` และ `db-seed` 1.3 รันผ่าน) แล้วค่อยเป็น `ErrImagePull`/`ImagePullBackOff` ตอนดึง image ของ container หลัก
- `rollout status` จบด้วย `exceeded its progress deadline` และ **exit 1** ราว 60 วินาทีหลัง `set image` (`progressDeadlineSeconds: 60`)
- terminal 1 ผลจริง `ok=700 err=0 (ใช้เวลา 75.7 วินาที)` (หน้าแรก `/` 350 ครั้งก็ err 0)

ดูอาการและสั่งซื้อระหว่างรุ่นพัง

```bash
kubectl -n som-shop get deploy som-web; kubectl -n som-shop get pods; kubectl -n som-shop get rs
kubectl -n som-shop get deploy som-web -o jsonpath='{range .status.conditions[*]}{.type}={.status} {.reason}: {.message}{"\n"}{end}'
P=$(kubectl -n som-shop get pods -l app=som-web --no-headers | awk "\$2==\"0/1\"{print \$1}"); kubectl -n som-shop describe pod $P | sed -n "/^Events/,\$p"
curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":2,"qty":1}'; echo; kubectl -n som-shop rollout history deploy/som-web
```

```text
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
som-web   3/3     1            3           4m33s
NAME                       READY   STATUS             RESTARTS   AGE
som-db-sdznc               1/1     Running            0          6m7s
som-web-6cd4d5d687-dqh9r   0/1     ImagePullBackOff   0          81s
som-web-ffc7b9f94-k896q    1/1     Running            0          108s
som-web-ffc7b9f94-qtmdt    1/1     Running            0          114s
som-web-ffc7b9f94-vdmf6    1/1     Running            0          2m1s
NAME                 DESIRED   CURRENT   READY   AGE
som-db               1         1         1       6m7s
som-web              0         0         0       6m7s
som-web-6cd4d5d687   1         1         0       81s
som-web-7955fccc94   0         0         0       4m33s
som-web-ffc7b9f94    3         3         3       3m25s
Available=True MinimumReplicasAvailable: Deployment has minimum availability.
Progressing=False ProgressDeadlineExceeded: ReplicaSet "som-web-6cd4d5d687" has timed out progressing.
Events:
  ...
  Normal   Started    79s                kubelet            spec.initContainers{db-seed}: Container started
  Normal   Pulling    35s (x3 over 78s)  kubelet            spec.containers{web}: Pulling image "som-shop-web:1.4"
  Warning  Failed     33s (x3 over 76s)  kubelet            spec.containers{web}: Failed to pull image "som-shop-web:1.4": failed to pull and unpack image "docker.io/library/som-shop-web:1.4": failed to resolve reference "docker.io/library/som-shop-web:1.4": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Warning  Failed     33s (x3 over 76s)  kubelet            spec.containers{web}: Error: ErrImagePull
  Normal   BackOff    8s (x3 over 50s)   kubelet            spec.containers{web}: Back-off pulling image "som-shop-web:1.4"
  Warning  Failed     8s (x3 over 50s)   kubelet            spec.containers{web}: Error: ImagePullBackOff
{"ok":true,"order_id":5,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":14}}
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
4         1.3 ธีม sunset
5         1.4 (ทดสอบรุ่นพัง)
```

`READY 3/3 UP-TO-DATE 1 AVAILABLE 3`: `maxUnavailable: 0` ไม่ยอมปิดบูธ 1.3 จนกว่าบูธ 1.4 จะพร้อม (ซึ่งไม่มีวัน) ร้านจึงยังเป็น 1.3 และ **สั่งซื้อได้** (`order_id 5`) Kubernetes ตั้ง `ProgressDeadlineExceeded` แต่ไม่ย้อนรุ่นให้ ต้องสั่งเอง

<p align="center" id="fig-23">
  <img src="images/screenshots/20261005_1047_lab10deploy_03-broken-1.4-shop-still-selling.png" alt="รูปที่ 23 ภาพหน้าจอจริง รุ่นพัง 1.4 ร้านยังขาย" width="700"><br>
  <em><b>รูปที่ 23</b> ภาพหน้าจอจริงจากการทดลอง: ระหว่างที่ set image เป็น 1.4 (ไม่มี image จริง) Pod ใหม่ค้าง ErrImagePull และ Deployment เป็น READY 3/3 UP-TO-DATE 1 AVAILABLE 3 — หน้าร้านยังเป็นเวอร์ชัน 1.3 (เสิร์ฟโดย Pod: som-web-ffc7b9f94-7m6wn) และยังสั่งซื้อได้ ออเดอร์เพิ่มเป็น 5 จากนั้น rollout status แจ้ง exceeded its progress deadline (exit 1) แล้วจึงสั่ง rollout undo</em>
</p>

**terminal 2** — undo (terminal 1 ยิง `./hit.sh -q http://localhost:30080/api/whoami 300` อีกรอบ)

```bash
kubectl -n som-shop rollout undo deploy/som-web 2>&1 | grep -v ^Warning; kubectl -n som-shop rollout status deploy/som-web
kubectl -n som-shop get pods; kubectl -n som-shop rollout history deploy/som-web
```

```text
deployment.apps/som-web rolled back
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
NAME                      READY   STATUS    RESTARTS   AGE
som-db-sdznc              1/1     Running   0          6m47s
som-web-ffc7b9f94-k896q   1/1     Running   0          2m28s
som-web-ffc7b9f94-qtmdt   1/1     Running   0          2m34s
som-web-ffc7b9f94-vdmf6   1/1     Running   0          2m41s
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
5         1.4 (ทดสอบรุ่นพัง)
6         1.3 ธีม sunset
```

undo จาก 1.4 กลับ 1.3 ใช้แค่ **0.1 วินาที** (RS 1.3 ยังพร้อมครบ แค่ลบ Pod 1.4 ที่พัง) และ hit.sh ระหว่าง undo ได้ `ok=300 err=0` ส่วนรอบถ่ายภาพหน้าจอซึ่งไม่ได้ทำขั้น 10.7 ได้ history หลังขั้นนี้เป็น `0, 1, 3, 4` (เลข revision ขึ้นกับลำดับคำสั่งที่ทำมา)

### 10.9 scale 3 → 5

<p align="center" id="fig-24">
  <img src="images/21-lab10-scale-3-to-5.png" alt="รูปที่ 24 LAB 10 scale 3 → 5" width="900"><br>
  <em><b>รูปที่ 24</b> LAB10 ขั้น 6: kubectl scale deploy/som-web --replicas=5 → บูธเพิ่มเป็น 5 EndpointSlice เพิ่มเอง และ rollout history ไม่มี revision ใหม่</em>
</p>

```bash
kubectl -n som-shop scale deploy/som-web --replicas=5 && time kubectl -n som-shop rollout status deploy/som-web && kubectl -n som-shop get pods -o wide
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web; kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'; kubectl -n som-shop rollout history deploy/som-web
./hit.sh
```

```text
deployment.apps/som-web scaled
Waiting for deployment "som-web" rollout to finish: 3 out of 5 new replicas have been updated...
Waiting for deployment "som-web" rollout to finish: 3 of 5 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m5.405s
NAME                      READY   STATUS    RESTARTS   AGE     IP             NODE          NOMINATED NODE   READINESS GATES
som-db-sdznc              1/1     Running   0          6m58s   10.244.2.98    lab-worker    <none>           <none>
som-web-ffc7b9f94-7784v   1/1     Running   0          6s      10.244.1.66    lab-worker2   <none>           <none>
som-web-ffc7b9f94-9p8n7   1/1     Running   0          6s      10.244.2.110   lab-worker    <none>           <none>
som-web-ffc7b9f94-k896q   1/1     Running   0          2m39s   10.244.2.108   lab-worker    <none>           <none>
som-web-ffc7b9f94-qtmdt   1/1     Running   0          2m45s   10.244.1.65    lab-worker2   <none>           <none>
som-web-ffc7b9f94-vdmf6   1/1     Running   0          2m52s   10.244.2.107   lab-worker    <none>           <none>
NAME            ADDRESSTYPE   PORTS   ENDPOINTS                                           AGE
som-web-9sxgw   IPv4          3000    10.244.2.107,10.244.1.65,10.244.2.108 + 2 more...   6m58s
10.244.2.107 som-web-ffc7b9f94-vdmf6 ready=true
10.244.1.65 som-web-ffc7b9f94-qtmdt ready=true
10.244.2.108 som-web-ffc7b9f94-k896q ready=true
10.244.2.110 som-web-ffc7b9f94-9p8n7 ready=true
10.244.1.66 som-web-ffc7b9f94-7784v ready=true
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
5         1.4 (ทดสอบรุ่นพัง)
6         1.3 ธีม sunset
จำนวน  Pod  เวอร์ชัน
     15 som-web-ffc7b9f94-7784v 1.3
      9 som-web-ffc7b9f94-9p8n7 1.3
     11 som-web-ffc7b9f94-k896q 1.3
     12 som-web-ffc7b9f94-qtmdt 1.3
     13 som-web-ffc7b9f94-vdmf6 1.3
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
```

- 5 บูธพร้อมใน 5.4 วินาที EndpointSlice มี 5 endpoint `ready=true` เอง (คอลัมน์ ENDPOINTS แสดงแค่ 3 IP แล้ว `+ 2 more...` จึงดูด้วย jsonpath)
- `rollout history` **ไม่มี revision ใหม่** (scale ไม่แตะ template) และ hit.sh เห็นครบ 5 บูธ
- ทรัพยากรพอ ไม่มี Pod `Pending` (5 web + 1 surge ระหว่าง rollout + 1 db)

### 10.10 ลบ Pod db แล้วเติมสินค้าด้วย rollout restart

<p align="center" id="fig-25">
  <img src="images/22-lab10-db-lost-restart.png" alt="รูปที่ 25 LAB 10 ลบ Pod db แล้ว rollout restart" width="900"><br>
  <em><b>รูปที่ 25</b> LAB10 ขั้น 7: ลบ Pod db → Deployment สร้างใหม่ แต่ emptyDir ว่าง ช่วงแรกเปิดหน้าไม่ได้ 2–5 วิ แล้วขึ้น "ร้านกำลังเตรียมสินค้า" (503) → rollout restart deploy/som-web เติมสินค้าใหม่ ออเดอร์จาก 4 เป็น 0 → บทหน้า PVC</em>
</p>

Deployment สร้าง Pod db แทนให้ได้ แต่ข้อมูลอยู่ใน `emptyDir` ของ Pod เดิม

```bash
kubectl -n som-shop get pod -l app=som-db -o wide; kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=60s; kubectl -n som-shop get pod -l app=som-db -o wide; kubectl -n som-shop get rs -l app=som-db
```

```text
NAME           READY   STATUS    RESTARTS   AGE     IP            NODE         NOMINATED NODE   READINESS GATES
som-db-sdznc   1/1     Running   0          7m12s   10.244.2.98   lab-worker   <none>           <none>
pod "som-db-sdznc" deleted from som-shop namespace
pod/som-db-66sc7 condition met
NAME           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-db-66sc7   1/1     Running   0          4s    10.244.1.67   lab-worker2   <none>           <none>
NAME     DESIRED   CURRENT   READY   AGE
som-db   1         1         1       7m16s
```

Pod db ใหม่ (`som-db-66sc7`) พร้อมใน 4.4 วินาที คนละ Node คนละ IP แต่ Service `som-db` ชื่อเดิม (ReplicaSet `som-db` ที่ถูกรับเลี้ยงเป็นผู้สร้าง) ดูหน้าร้านและฐานข้อมูล

```bash
sleep 2; curl -s -o /dev/null -w '%{http_code}\n' localhost:30080; curl -s localhost:30080/api/health; echo; curl -s localhost:30080/api/stats; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c 'select count(*) from orders'
for i in 1 2 3 4 5 6; do echo "$(date +%T) code=$(curl -s -m 2 -o /dev/null -w '%{http_code}' localhost:30080) health=$(curl -s -m 2 localhost:30080/api/health)"; sleep 1; done; kubectl -n som-shop get pods -l app=som-web; curl -s localhost:30080/api/stats; kubectl -n som-shop get events --sort-by=.lastTimestamp | grep -i -E 'unhealthy|readiness' | tail -5
```

```text
000

ERROR:  relation "orders" does not exist
LINE 1: select count(*) from orders
                             ^
command terminated with exit code 1
10:35:46 code=503 health={"ok":true,"db":"up"}
10:35:47 code=503 health={"ok":true,"db":"up"}
...
10:35:51 code=503 health={"ok":true,"db":"up"}
NAME                      READY   STATUS    RESTARTS   AGE
som-web-ffc7b9f94-7784v   1/1     Running   0          38s
...
som-web-ffc7b9f94-k896q 1.3 db-not-ready
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-vdmf6     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-qtmdt     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-9p8n7     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-k896q     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-7784v     Readiness probe failed: HTTP probe failed with statuscode: 503
```

- ช่วงแรก **2–5 วินาที เปิดหน้าเว็บไม่ได้เลย** (`curl` ได้ code `000`) เพราะ readiness ของ web ทุกตัวล้มพร้อมกันตอน db หาย (Event `statuscode: 503` ทั้ง 5 Pod) endpoint จึงว่างชั่วครู่ browser อาจขึ้นหน้า error ก่อน
- จากนั้น db ใหม่ตอบแล้ว (`/api/health` = `{"ok":true,"db":"up"}`) web กลับมา ready แต่หน้าแรกได้ **503** "ร้านกำลังเตรียมสินค้า" เพราะ db ใหม่ **ว่างเปล่า** ไม่มีตาราง `orders` (`relation "orders" does not exist`) web ไม่มีตัวไหนถูก restart (liveness ไม่พึ่ง db)

initContainer `db-seed` (สร้างตาราง + สินค้า) รันเฉพาะตอน Pod เกิด บทที่ 6 ต้องลบ Pod web เอง บทนี้ใช้ **`rollout restart`** ให้ผู้จัดการร้านทยอยสร้างบูธใหม่ตามกติกา zero-downtime (terminal 1 ยิง `./hit.sh -q http://localhost:30080/api/whoami 300`)

```bash
kubectl -n som-shop rollout restart deploy/som-web && time kubectl -n som-shop rollout status deploy/som-web
for i in $(seq 10); do curl -s localhost:30080/api/stats; done | sort | uniq -c; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c "select count(*) from orders"; kubectl -n som-shop rollout history deploy/som-web; P=$(kubectl -n som-shop get pods -l app=som-web -o name | head -1); kubectl -n som-shop logs $P -c db-seed
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 1 out of 5 new replicas have been updated...
...
deployment "som-web" successfully rolled out
      4 som-web-7cbbcddf4-559c2 1.3 orders=0 products=6
      1 som-web-7cbbcddf4-5z79n 1.3 orders=0 products=6
      1 som-web-7cbbcddf4-6cgfv 1.3 orders=0 products=6
      2 som-web-7cbbcddf4-hg9gh 1.3 orders=0 products=6
      2 som-web-7cbbcddf4-rtplg 1.3 orders=0 products=6
 count 
-------
     0
(1 row)

deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
5         1.4 (ทดสอบรุ่นพัง)
6         1.3 ธีม sunset
7         1.3 ธีม sunset

connected to database
got seed lock 5005
tables ready: products, orders
seeded 6 products (new: 6)
```

- rollout restart 5 replicas ใช้ **32.9 วินาที** `/api/whoami` ได้ `ok=300 err=0`
- ถ้ายิงหน้าแรก `/` พร้อมกัน ผลจริง `ok=125 err=25` (`The requested URL returned error: 503` ในช่วง 5.1 วินาทีแรก) — ร้าน 503 อยู่แล้วก่อน restart และหายทันทีที่บูธใหม่ตัวแรก seed ตารางเสร็จ (ไม่ใช่ error จากการ rollout)
- ร้านกลับมาขายได้ แต่ **ออเดอร์ = 0** (เดิม 5) revision 7 สืบทอด change-cause `1.3 ธีม sunset` (ลืม annotate)

### 10.11 (เสริม) Recreate ของ som-db ของจริง

ตอนแปลง db (ขั้น 10.3) ไม่เกิด Recreate เพราะ template เหมือนเดิม ถ้าอยากเห็นลำดับ "ปิดก่อนเปิด" ของจริง ใช้ `rollout restart` กับ `som-db`

**terminal 3** — `kubectl -n som-shop get pods -w`

**terminal 2**

```bash
curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":1}'; echo
kubectl -n som-shop rollout restart deploy/som-db && time kubectl -n som-shop rollout status deploy/som-db
kubectl -n som-shop get rs -l app=som-db; kubectl -n som-shop rollout history deploy/som-db
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
deployment.apps/som-db restarted
Waiting for deployment "som-db" rollout to finish: 0 out of 1 new replicas have been updated...
...
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
NAME                DESIRED   CURRENT   READY   AGE
som-db              0         0         0       9m2s
som-db-786556dc4f   1         1         1       32s
deployment.apps/som-db 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

ผลจริงใน terminal 3 (เติมเวลาหน้าบรรทัด)

```text
10:36:51 som-db-66sc7   1/1     Terminating   0          77s
10:36:52 som-db-66sc7   0/1     Completed     0          78s
10:36:52 som-db-786556dc4f-ljl5d   0/1     Pending       0          0s
10:36:52 som-db-786556dc4f-ljl5d   0/1     ContainerCreating   0          0s
10:36:52 som-db-786556dc4f-ljl5d   0/1     Running             0          0s
10:36:56 som-db-786556dc4f-ljl5d   1/1     Running             0          4s
10:36:54 som-web-7cbbcddf4-559c2   0/1     Running           0          51s
...
10:36:58 som-web-7cbbcddf4-559c2   1/1     Running           0          54s
```

- Pod db เก่า `Completed` **ก่อน** แล้ว Pod db ใหม่จึงเกิด (rollout 4.3 วินาที) ไม่มีช่วงที่มี db 2 ตัว = Recreate ทำงานตามที่ออกแบบ RS `som-db` เดิมเหลือ 0 และได้ RS ใหม่ `som-db-786556dc4f` (revision 2)
- web 4 ใน 5 ตัว `0/1` ชั่วครู่ระหว่างไม่มี db `/api/whoami` ยัง 300/300 แต่หน้าแรกเป็น 503 (ผลจริง `ok=14 err=136` จาก 150) จนกว่าจะเติมสินค้าใหม่ และออเดอร์ที่เพิ่งสั่ง (`order_id 1`) หายไปพร้อม Pod db เก่า

```bash
kubectl -n som-shop rollout restart deploy/som-web >/dev/null && kubectl -n som-shop rollout status deploy/som-web >/dev/null && curl -s -o /dev/null -w "%{http_code}\n" localhost:30080 && curl -s localhost:30080/api/stats
```

```text
200
som-web-7cbbcddf4-559c2 1.3 orders=0 products=6
```

### 10.12 สรุป LAB 10 และปัญหาที่ส่งต่อ

<p align="center" id="fig-26">
  <img src="images/23-lab10-wrap-up.png" alt="รูปที่ 26 สรุป LAB สุดท้าย" width="900"><br>
  <em><b>รูปที่ 26</b> สรุป LAB สุดท้าย: Deployment ดูแลจำนวนและรุ่น, rolling + preStop ไม่สะดุด, rollout undo ย้อนได้, progress deadline บอกรุ่นพังโดยร้านยังขาย, Recreate สำหรับ db — แต่ db ยังลืมข้อมูล</em>
</p>

**ตารางสรุป** สิ่งที่ Deployment แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| ย้ายจาก ReplicaSet โดยไม่เปลี่ยนชื่อ Service | db ถูกรับเลี้ยงทันที (ไม่สร้างใหม่ ข้อมูลอยู่), web รับเลี้ยงแล้วแทนทีละบูธ err 1–2/300 (บูธเดิมไม่มี preStop) | ✅ Deployment (บทนี้) |
| เปลี่ยนรุ่นระหว่างขายโดยลูกค้าไม่เจอ error | rolling 1.2→1.3 18.1 วินาที err 0/300 | ✅ RollingUpdate + readiness + maxUnavailable 0 + preStop |
| สมุดประวัติและย้อนรุ่น | `rollout history` มี CHANGE-CAUSE, undo สองครั้ง err 0 ออเดอร์อยู่ครบ | ✅ `rollout history/undo` |
| รุ่นพังแต่ร้านยังขาย | 1.4 `ImagePullBackOff` + `ProgressDeadlineExceeded` แต่ hit.sh 700/700 และสั่งซื้อได้ | ✅ maxUnavailable 0 + progressDeadlineSeconds (คนต้อง undo เอง) |
| ปรับจำนวนบูธ | scale 3→5 ใน 5.4 วินาที ไม่มี revision ใหม่ | ✅ (สั่งเอง) → ปรับอัตโนมัติด้วย HPA (บทหลัง) |
| ห้ามมี db สองตัว | `rollout restart deploy/som-db` ปิดก่อนเปิด | ✅ Recreate |
| ข้อมูล db คงอยู่เมื่อ Pod db เกิดใหม่ | ลบ Pod db / Recreate แล้ว `relation "orders" does not exist` ออเดอร์ 0 | ❌ → **PersistentVolume/PVC/StatefulSet (บทถัดไป)** |
| รหัสผ่านไม่อยู่ใน YAML | `meow1234` ยังเขียนตรง ๆ ใน `k8s/*.yaml` | ❌ → ConfigMap/Secret (บทหลัง) |

### สิ่งที่เห็นใน LAB 10

- แปลงร้านด้วยไฟล์ชื่อ/selector เดิม: `som-db` template เดิม → รับเลี้ยงเป็นรุ่นปัจจุบัน ไม่มี Recreate ข้อมูลไม่หาย, `som-web` → RS เดิมเป็น REVISION 0 แล้วถูกแทนแบบ rolling (err 1–2/300 เพราะบูธเดิมไม่มี preStop)
- rolling 1.2 → 1.3, undo สองครั้ง, undo จาก 1.4 และ rollout restart: `/api/whoami` err 0/300 ทุกครั้ง Pod เก่าขึ้น `Error` ชั่วครู่ (ปกติ)
- รุ่นพัง 1.4: `PodInitializing` → `ImagePullBackOff`, `exceeded its progress deadline` (exit 1) ~60 วินาที, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` ร้านยังขาย undo 0.1 วินาที
- scale 5: EndpointSlice 5 endpoint ไม่มี revision ใหม่
- ลบ Pod db: เปิดไม่ได้ 2–5 วินาที → 503 → `rollout restart deploy/som-web` เติมสินค้า ออเดอร์ 5 → 0 และ Recreate ของ `som-db` ปิดก่อนเปิดจริง

### 10.13 เก็บกวาด LAB 10

🐧 **ใน SSH session ของ k8s-lab** (หยุด `hit.sh` และ `-w` ในหน้าต่างอื่นด้วย Ctrl+C ก่อน)

```bash
time kubectl delete ns som-shop; kubectl get svc -A | grep -E "3008[0-2]" || echo "(30080 ว่าง)"
```

```text
namespace "som-shop" deleted

real	0m27.898s
(30080 ว่าง)
```

ลบ namespace ราว 28 วินาที (Pod web มี preStop และ grace period) พอร์ต 30080 ว่างอีกครั้ง image `som-shop-web:1.2`/`1.3` และ postgres ยังอยู่บน Node

### คำถามท้าย LAB 10

1. ทำไมตอน `kubectl apply -f k8s/10-db.yaml` (ขั้น 10.3) Pod db เดิมจึงไม่ถูกปิดทั้งที่ไฟล์เขียน `strategy: Recreate` ถ้าแก้ env ใดก็ได้ของ postgres ในไฟล์ก่อน apply จะเกิดอะไรกับออเดอร์
2. ทำไมการแปลง web (ขั้น 10.4) จึงมี error 1–2 ครั้ง แต่ rolling 1.2 → 1.3 (ขั้น 10.6) ได้ 0 ทั้งที่ใช้ Deployment ตัวเดียวกัน
3. อธิบายค่า `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` ระหว่างรุ่น 1.4 และบอกว่าถ้า `maxUnavailable` เป็น 1 ลูกค้าจะเห็นอะไรต่างไป
4. หลังลบ Pod db ทำไมช่วงแรกเปิดหน้าเว็บไม่ได้เลย แล้วค่อยเป็น 503 และทำไม `rollout restart deploy/som-web` จึงทำให้ร้านกลับมา (เทียบกับวิธีของบทที่ 6)
5. ถ้าน้องส้มอยากให้ออเดอร์ไม่หายเมื่อ Pod db ถูกสร้างใหม่ ต้องเปลี่ยนส่วนใดของ `k8s/10-db.yaml` และ Deployment ช่วยเรื่องนี้ได้หรือไม่ เพราะอะไร

> **🏆 ท้าทาย:** แก้ `k8s/20-web.yaml` ให้ใช้ `som-shop-web:1.3` และเปลี่ยน annotation `kubernetes.io/change-cause` เป็นข้อความใหม่ แล้ว `kubectl apply -f k8s/20-web.yaml` แทนการใช้ `set image` บันทึกว่า `rollout history` และ Warning เรื่อง last-applied เปลี่ยนไปอย่างไรเมื่อเทียบกับการใช้ `set image` + `undo` (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเอง)

> **ปูทางบทหน้า:** ผู้จัดการร้านดูแล "จำนวนและรุ่น" ได้ดีแล้ว แต่ครัวกลางยังลืมทุกอย่างทุกครั้งที่ Pod db เกิดใหม่ บทถัดไปจะให้ db มีที่เก็บข้อมูลถาวร (PersistentVolume/PersistentVolumeClaim) และรู้จัก StatefulSet

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v3/`, kubectl แจ้ง `the path "lab01-deployment/" does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 007_kubernetes_deployment k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/007_kubernetes_deployment/02_LAB/labs` (LAB 10 ใช้ `../som-shop-v3`) ตรวจด้วย `pwd` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 5 (build/load image ใหม่) |
| `error validating "...-patch.yaml": error validating data: [apiVersion not set, kind not set]` | apply ทั้งโฟลเดอร์ที่มีไฟล์ patch ปน (ไฟล์ patch ไม่มี apiVersion/kind) | ไฟล์ patch ต้องอยู่ใน `patches/` และใช้กับ `kubectl patch ... --patch-file` เท่านั้น |
| `The Deployment "zero" is invalid: ... may not be 0 when maxSurge is 0` ตอน apply LAB 4 | ไฟล์แบบฝึกอยู่ในโฟลเดอร์เดียวกับ `apply -f` | `zero-zero.yaml` อยู่ใน `exercise/` ใช้กับ `--dry-run=server` เท่านั้น |
| นับ Pod จาก `get pods -w` ได้มากกว่าที่คำนวณ | นับรวมบรรทัด `Terminating`/`Completed` ของ Pod ที่กำลังปิด | นับเฉพาะ Pod ที่ยังไม่ถูกสั่งปิด หรือดู annotation `deployment.kubernetes.io/max-replicas` ของ RS (LAB 4 ขั้นที่ 3) |
| Pod ขึ้น `0/1 Completed` (nginx/postgres) หรือ `0/1 Error` (Next.js) ระหว่าง rollout | Pod รุ่นเก่ากำลังปิด (ออกสะอาด / ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM) | ปกติ ไม่ใช่ rollout พัง รอสักครู่จะหายไป |
| `describe deploy` เห็น Events ไม่ครบ มี `(combined from similar events)` | ระบบรวม event ที่คล้ายกัน | ใช้ `kubectl get rs -w` หรือ `get rs` ดูจำนวนจริง |
| CHANGE-CAUSE ของ revision ใหม่ซ้ำกับของเก่า | ลืม `annotate` (รวมถึงหลัง `rollout restart`) | `kubectl -n <ns> annotate deploy <ชื่อ> kubernetes.io/change-cause="..." --overwrite` ทุกครั้ง หรือใส่ใน YAML |
| `error: you cannot rollback a paused deployment` | สั่ง undo ระหว่าง pause | `kubectl -n <ns> rollout resume deploy/<ชื่อ>` ก่อน |
| `rollout status` รอไม่จบ | Deployment ถูก pause อยู่ หรือรุ่นใหม่พังแต่ deadline ยังไม่หมด (default 600 วินาที) | ใส่ `--timeout=10s`, ตรวจ `kubectl get deploy` (UP-TO-DATE) และ `kubectl describe deploy` |
| `rollout status` จบด้วย `exceeded its progress deadline` (exit 1) | รุ่นใหม่ไม่พร้อมภายใน `progressDeadlineSeconds` | ดูสาเหตุด้วย `get pods`, `describe pod`, `logs --previous` แล้ว `kubectl rollout undo` |
| Pod ใหม่ `ErrImagePull`/`ImagePullBackOff` | tag ไม่มีจริง (ตั้งใจใน LAB 6/10) หรือลืม `kind load` image ที่ build เอง | LAB 6/10: `rollout undo`; ถ้าเป็น `som-shop-web:1.2`/`1.3` ทำ LAB 0 ขั้นที่ 5 |
| Pod ใหม่ค้าง `PodInitializing` ราว 8 วินาทีก่อน `ErrImagePull` (LAB 10 รุ่น 1.4) | initContainer รันก่อน แล้วจึงดึง image ของ container หลัก | ปกติ รอดูต่อ |
| `kubectl get node ... -o jsonpath='{.status.images...}'` ไม่เห็น image ทั้งที่เพิ่ง `kind load` | ข้อมูลใน `.status.images` อัปเดตช้า (30–60 วินาที) | ใช้ `docker exec lab-worker crictl images` |
| `provided port is already allocated` ตอน apply NodePort 30080 | Service อื่นจอง 30080 (LAB 7 ยังไม่ลบ, ร้านบทที่ 6, ตัวอย่างของบทที่ 1) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace/ตัวอย่างที่ค้าง |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นบนเครื่องใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| browser refresh แล้วเห็นรุ่น/ชื่อ Pod เดิม | keep-alive และ cache ของ browser | กด Ctrl+F5 และนับการกระจายด้วย `hit.sh` |
| หลัง `kubectl patch svc` เปลี่ยน selector ยังได้รุ่นเดิม | EndpointSlice/kube-proxy ยังอัปเดตไม่ทัน | รอ 1–2 วินาทีก่อนยิงทดสอบ |
| canary 50 ครั้งได้รุ่นใหม่ไม่ถึง/เกิน 10 ครั้ง | การสุ่มต่อ connection | ปกติ ยิงหลายร้อยครั้งจึงใกล้ 20% |
| ENDPOINTS แสดง `... + 2 more...` | kubectl ตัดการแสดงผลเกิน 3 IP | ใช้ jsonpath `{range .items[0].endpoints[*]}...` |
| หลังลบ Pod db หน้าเว็บเปิดไม่ได้ 2–5 วินาที แล้วเป็น 503 "ร้านกำลังเตรียมสินค้า" ค้าง | web ทุกตัว not ready ชั่วครู่ แล้ว db ใหม่ว่างเปล่า (ตั้งใจให้เห็น) | `kubectl -n som-shop rollout restart deploy/som-web` (ขั้น 10.10) |
| err ของ `hit.sh` มากกว่าในเอกสาร | เครื่องช้ากว่า หรือรอบที่บูธเดิมยังไม่มี preStop | ปกติ บันทึกตัวเลขของตัวเอง ถ้ามี error หลังใส่ preStop แล้ว ตรวจว่า patch/rollout จบก่อนเริ่มนับ |
| `./hit.sh: Permission denied` | สิทธิ์ execute หายระหว่างคัดลอก | `chmod +x ../som-shop-v3/hit.sh` หรือรันด้วย `bash` |
| ลบ namespace ใช้เวลานาน ~27 วินาที | Pod มี preStop 5 วินาทีและ grace period | ปกติ รอให้จบ |
| `hit.sh` หรือ `kubectl ... -w` ค้างอยู่ในอีกหน้าต่าง | ยังไม่ได้หยุด | กด Ctrl+C ในหน้าต่างนั้น ถ้าหาไม่เจอใช้ `pkill -f "[h]it.sh"` (ใส่วงเล็บเหลี่ยมเพื่อไม่ให้จับคำสั่ง pkill เอง) |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), ผล `grep -E '3008[0-2]'` ที่ว่าง และ `crictl images` ที่เห็น `som-shop-web` 1.2/1.3 + postgres
- [ ] **LAB 1** `get deploy,rs,pods --show-labels` (เห็น `pod-template-hash`), ownerReferences ของ RS และ Pod, history หลัง scale (revision 1 แถวเดียว) และ Event `Scaled down replica set ... from 6 to 3`
- [ ] **LAB 2** ผล `get rs -w` ที่ RS ใหม่เพิ่ม/เก่าลด และผลรวมคำตอบของ client (v1/v2 ปน ไม่มี ERR)
- [ ] **LAB 3** history ที่มี revision สืบทอด change-cause, history หลัง undo (`1, 3, 4, 5`), error ของ undo ระหว่าง pause และ annotation `restartedAt`
- [ ] **LAB 4** ตาราง Pod สูงสุด/พร้อมต่ำสุดของ 3 กลยุทธ์ (ตัวเลขของตัวเอง), `max-replicas 13` และ error ของ `zero-zero.yaml`
- [ ] **LAB 5** `get deploy -w` ที่ AVAILABLE ตาม READY ~10 วินาที และ Pod `0/1 Running` + Event `statuscode: 404`
- [ ] **LAB 6** `exceeded its progress deadline` + `exit=1`, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` และ condition `ProgressDeadlineExceeded`
- [ ] **LAB 7** ผล `hit.sh -q` รอบไม่มี preStop และรอบ graceful-patch (ตัวเลข err ของตัวเอง)
- [ ] **LAB 8** ownerReferences ของ RS `web` ที่ชี้ Deployment และ history `0`/`1`
- [ ] **LAB 9** ผล blue → green และสัดส่วน canary อย่างน้อย 3 รอบ
- [ ] **LAB 10** (1) history `0 <none>` / `1 1.2 แปลงเป็น Deployment` และ RS เดิม `0 0 0` (2) browser หน้าร้าน 1.2 ที่ชื่อ Pod มี hash (3) `hit.sh -q` ระหว่าง rolling 1.3 (`err=0`) (4) browser หน้าร้าน 1.3 (5) history หลัง undo สองครั้ง (6) 1.4: `ImagePullBackOff` + `exceeded its progress deadline` + `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` + สั่งซื้อได้ (7) EndpointSlice 5 endpoint (8) `relation "orders" does not exist` และร้านกลับมา `orders=0`
- [ ] ท้ายสุด `kubectl get ns` เหลือ namespace ตั้งต้น 5 ตัว และ `kubectl get svc -A | grep 3008` ว่าง

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| namespace `deploy-lab` (Deployment `web`, Service `web`, `client`) | 1–3 | `kubectl get all -n deploy-lab` | `kubectl delete ns deploy-lab` |
| Deployment ที่ถูก pause | 3 | `kubectl -n deploy-lab get deploy web -o jsonpath='{.spec.paused}'` | `kubectl -n deploy-lab rollout resume deploy/web` |
| namespace `strategy-lab` | 4 | `kubectl get ns strategy-lab` | `kubectl delete ns strategy-lab` |
| namespace `ready-lab` | 5 | `kubectl get ns ready-lab` | `kubectl delete ns ready-lab` |
| namespace `broken-lab` (Pod `ImagePullBackOff`/`CrashLoopBackOff`) | 6 | `kubectl get pods -n broken-lab` | `kubectl delete ns broken-lab` |
| namespace `zdt-lab` (**จอง NodePort 30080**) | 7 | `kubectl get svc -A \| grep 30080` | `kubectl delete ns zdt-lab` |
| namespace `migrate-lab` | 8 | `kubectl get ns migrate-lab` | `kubectl delete ns migrate-lab` |
| namespace `release-lab` | 9 | `kubectl get ns release-lab` | `kubectl delete ns release-lab` |
| namespace `som-shop` (**จอง NodePort 30080**) | 10 | `kubectl get ns som-shop` | `kubectl delete ns som-shop` |
| `hit.sh` หรือ `kubectl ... -w` ที่ยังรันอยู่ | 2–10 | `pgrep -af "[h]it.sh"` | Ctrl+C หรือ `pkill -f "[h]it.sh"` |
| image `som-shop-web:1.2`/`1.3`, postgres บน Node | 0, 10 | `docker exec lab-worker crictl images \| grep -E "som-shop\|postgres"` | **เก็บไว้ได้** (ใช้ซ้ำได้ ถ้า `k8s-down` จะหายไปด้วย) |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get ns
kubectl get svc -A
pgrep -af "[h]it.sh" || echo "ไม่มี hit.sh ค้าง"
```

ผลที่ถูกต้อง: เหลือ namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), Service มีแค่ `kubernetes` และ `kube-dns` และไม่มี `hit.sh` ค้าง

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ค่า hash, จำนวน error และจำนวนออเดอร์) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ ชื่อ Pod, เวลา rollout และเลข revision ในรอบนั้นจึงอาจต่างจากผลคำสั่งในเอกสาร
