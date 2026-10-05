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

{{FIGTOC}}

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

{{FIG:L01|LAB 0 เตรียมคลัสเตอร์ พอร์ต และ image}}

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

{{FIG:L02|LAB 1 Deployment แรก}}

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

{{FIG:L03|LAB 1 scale RS ตรงถูกปรับกลับ}}

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

{{FIG:L04|LAB 2 RS ใหม่เพิ่ม RS เก่าลด}}

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

{{FIG:L05|LAB 2 client เห็น v1 และ v2 ปนกัน}}

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

{{FIG:L06|LAB 3 history และ undo}}

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

{{FIG:L07|LAB 3 pause/resume และ restart}}

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

{{FIG:L08|LAB 4 เทียบ 3 กลยุทธ์}}

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

{{FIG:L09|LAB 5 readiness และ minReadySeconds}}

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

{{FIG:L10|LAB 6 rollout พังแล้ว undo}}

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
