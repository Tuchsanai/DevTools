# LAB บทที่ 3: Node กับ Pod — จัดวาง Pod บนกองเรือ สู่ร้านน้องส้มหลายสาขา

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Node และการจัดวาง Pod — สำรวจ Node, Pending/FailedScheduling, nodeName, Downward API, nodeSelector, node affinity, pod affinity/anti-affinity, topology spread, taints/tolerations, cordon/drain, Node ล่ม, static Pod และร้านอาหารแมวน้องส้ม 2 สาขาบนเรือคนละลำ
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่อยากขยายร้านเป็นหลายสาขา เริ่มจากสำรวจกองเรือ ดูว่าเจ้าหน้าที่จัดตู้ (kube-scheduler) ตัดสินใจอย่างไร ทดลองบอกทางด้วยธงเรือ แม่เหล็ก ป้ายห้ามขึ้นและบัตรผ่าน ซ่อมเรือด้วย cordon/drain จำลอง **เรือล่ม** ด้วย `docker stop` แล้วปิดท้ายด้วยการเปิด **ร้านอาหารแมวน้องส้ม 2 สาขาบนเรือคนละลำ** ที่ชื่อร้านบอกได้เองว่าอยู่บนเรือลำไหน

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, kind v0.33.0, Kubernetes v1.37.0) เมื่อ 4 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, CPU/RAM ของ Node และ Node ที่ scheduler เลือก (lab-worker หรือ lab-worker2) ในเครื่องนักศึกษาอาจต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจาก `kubectl get pod -o wide` ของเครื่องตัวเองเสมอ

> **ทดสอบซ้ำ 5 ตุลาคม 2569:** รันทุกคำสั่งในเอกสารนี้ใหม่บน container ใหม่จาก image เดียวกัน (kubectl **v1.37.1**, kind **0.33.0**, node image `kindest/node:v1.37.0`, containerd 2.3.4) ด้วยคลัสเตอร์ที่สร้างใหม่จาก `k8s-up` ทุกคำสั่งรันได้ตามที่เขียนไว้ ผลตรงกับตัวอย่าง ยกเว้นจุดที่มีหมายเหตุ **"ผลการทดสอบซ้ำ"** กำกับไว้ ตัวอย่างค่าที่ต่างกันได้ระหว่างเครื่อง: รอบนั้น IP ของ Node เป็น `lab-control-plane` 172.19.0.2, `lab-worker` 172.19.0.3, `lab-worker2` 172.19.0.4 (ตัวอย่างในเอกสารเป็น .3 / .4 / .2) และ Pod บน `lab-worker2` ได้ IP `10.244.3.x` (ตัวอย่างในเอกสารเป็น `10.244.2.x`)

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

> ⚠️ **สำคัญมากสำหรับบทนี้:** คำสั่ง `docker stop lab-worker2`, `docker start lab-worker2`, `docker exec lab-worker ...`, `docker exec lab-control-plane ...` และ `docker cp ... lab-worker:...` ต้องพิมพ์ **🐧 ใน SSH session ของ k8s-lab** เท่านั้น เพราะ Node `lab-*` เป็น container ที่อยู่ใน dockerd **ภายใน k8s-lab** ถ้าพิมพ์บนเครื่องตัวเองจะได้ `No such container` และ **ห้าม `docker stop lab-control-plane` เด็ดขาด** (หอบังคับการหยุด คลัสเตอร์ทั้งหมดใช้ไม่ได้) รวมถึงห้ามหยุด container `k8s-lab` เองระหว่างทำ LAB

### กติกาของ LAB บทนี้

- ทุก LAB ทำในโฟลเดอร์ **`/workspace/003_kubernetes_node_pod/02_LAB`** ภายใน k8s-lab
- บทนี้ยังใช้ **Pod เดี่ยว ๆ เท่านั้น** (ไม่ใช้ controller ใด ๆ ที่สร้าง Pod แทนเรา และไม่ใช้ทรัพยากรเครือข่ายแบบอื่น) การเข้าถึงแอปใช้ `kubectl exec`, `kubectl logs` และ `kubectl port-forward` + `ssh -L` เหมือนบทที่ 2
- ทุก Pod ใน LAB 1–8 ติด label **`lab=03`** จึงเก็บกวาดได้ด้วย `kubectl delete pod -l lab=03 --now`
- **ทุก LAB จบด้วยบล็อก "เก็บกวาด"** ที่ลบ Pod, ลบ label/taint ที่ติดให้ Node, `uncordon` และคืนเรือที่หยุดไป ต้องทำทุกครั้ง ไม่งั้น LAB ถัดไปจะได้ผลเพี้ยน (ดู [ตารางคืนสภาพคลัสเตอร์](#ตารางคืนสภาพคลัสเตอร์))
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [สำรวจกองเรือ](#lab-0-สำรวจกองเรือ) | 15 นาที | ⭐ |
| 1 | [เจ้าหน้าที่จัดตู้กับ Pending](#lab-1-เจ้าหน้าที่จัดตู้กับ-pending) | 10 นาที | ⭐ |
| 2 | [nodeName และ Downward API](#lab-2-nodename-และ-downward-api) | 15 นาที | ⭐⭐ |
| 3 | [ธงเรือ: nodeSelector และ node affinity](#lab-3-ธงเรือ-nodeselector-และ-node-affinity) | 20 นาที | ⭐⭐ |
| 4 | [แม่เหล็กระหว่างกล่อง: pod affinity และ anti-affinity](#lab-4-แม่เหล็กระหว่างกล่อง-pod-affinity-และ-anti-affinity) | 15 นาที | ⭐⭐⭐ |
| 5 | [ตาชั่งกองเรือ: topologySpreadConstraints](#lab-5-ตาชั่งกองเรือ-topologyspreadconstraints) | 10 นาที | ⭐⭐⭐ |
| 6 | [ป้ายห้ามขึ้นและบัตรผ่าน: taints และ tolerations](#lab-6-ป้ายห้ามขึ้นและบัตรผ่าน-taints-และ-tolerations) | 20 นาที | ⭐⭐⭐ |
| 7 | [ซ่อมเรือ: cordon, drain และ uncordon](#lab-7-ซ่อมเรือ-cordon-drain-และ-uncordon) | 15 นาที | ⭐⭐⭐ |
| 8 | [เรือหายในหมอก: Node NotReady](#lab-8-เรือหายในหมอก-node-notready) | 20 นาที | ⭐⭐⭐⭐ |
| 9 | [ตู้ของต้นเรือ: static Pod](#lab-9-ตู้ของต้นเรือ-static-pod) | 15 นาที | ⭐⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มหลายสาขาบนกองเรือ](#lab-10-lab-สุดท้าย-ร้านน้องส้มหลายสาขาบนกองเรือ) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางคืนสภาพคลัสเตอร์](#ตารางคืนสภาพคลัสเตอร์) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 4–4.5 ชั่วโมง (LAB 8 และ LAB 10 มีช่วงรอเรือ NotReady และรอการไล่ Pod หลายนาที)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 สำรวจกองเรือ](#fig-1) | 14 | [LAB 10 ภาพเปิด: 2 สาขาบนเรือคนละลำ](#fig-14) |
| 2 | [LAB 0 Node คือ container](#fig-2) | 15 | [โครง manifest ของสาขา](#fig-15) |
| 3 | [LAB 1 Pending](#fig-3) | 16 | [เตรียม image ให้ทุก Node](#fig-16) |
| 4 | [LAB 2 nodeName และ Downward API](#fig-4) | 17 | [สาขาที่ 3 Pending](#fig-17) |
| 5 | [LAB 3 ธงเรือ](#fig-5) | 18 | [port-forward 2 ท่อ](#fig-18) |
| 6 | [LAB 4 แม่เหล็กระหว่างกล่อง](#fig-6) | 19 | [หน้าเว็บ 2 สาขา](#fig-19) |
| 7 | [LAB 5 ตาชั่งกองเรือ](#fig-7) | 20 | [ภาพหน้าจอจริง: สาขา a บน lab-worker2](#fig-20) |
| 8 | [LAB 6 ป้ายห้ามขึ้นและบัตรผ่าน](#fig-8) | 21 | [ภาพหน้าจอจริง: สาขา b บน lab-worker](#fig-21) |
| 9 | [LAB 6 NoExecute และนาฬิกาทราย](#fig-9) | 22 | [drain เรือของสาขา a](#fig-22) |
| 10 | [LAB 7 cordon และ drain](#fig-10) | 23 | [เรือของสาขา b หายในหมอก](#fig-23) |
| 11 | [LAB 8 docker stop เรือล่ม](#fig-11) | 24 | [ภาพหน้าจอจริง: สาขา a ยังขายได้](#fig-24) |
| 12 | [LAB 8 ไทม์ไลน์การไล่ Pod](#fig-12) | 25 | [ภาพหน้าจอจริง: สาขา b เปิดไม่ได้](#fig-25) |
| 13 | [LAB 9 static Pod](#fig-13) | 26 | [ปูทางบทหน้า](#fig-26) |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ + screenshots/ ภาพหน้าจอจริงของร้าน 2 สาขา
├── labs/
│   ├── lab01-scheduler/{fit-pod,huge-pod}.yaml
│   ├── lab02-nodename-downward/{pinned-pod,ghost-node-pod,whereami-pod}.yaml
│   ├── lab03-node-labels/{selector-pod,affinity-required-pod,affinity-preferred-pod,affinity-gt-pod}.yaml
│   ├── lab04-pod-affinity/{cache-pod,web-near-cache-pod,crew-anti-pods,crew-preferred-pods}.yaml
│   ├── lab05-topology-spread/{spread-ignore-pods,spread-honor-pods}.yaml
│   ├── lab06-taints/{plain-pod,vip-pod,control-plane-pod,noexecute-pods}.yaml
│   ├── lab07-drain/fleet-pods.yaml
│   ├── lab08-node-down/fog-pods.yaml
│   └── lab09-static-pod/static-snack.yaml
└── som-shop-branches/                 ← LAB 10 ร้านน้องส้มหลายสาขา
    ├── app/                           ← แอป Next.js + Dockerfile (สำเนาจากบทที่ 2 ไม่ได้แก้โค้ด)
    └── k8s/{som-shop-a,som-shop-b,som-shop-c}.yaml
```

---

## LAB 0: สำรวจกองเรือ

<p align="center" id="fig-1">
  <img src="images/01-lab0-fleet-survey.png" alt="รูปที่ 1 LAB0 สำรวจกองเรือ" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: สำรวจ Node ด้วย kubectl get nodes, --show-labels และ describe node ดู allocatable กับ taint ของ control-plane</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 2 หรือสร้างใหม่) แล้วอ่าน Node object: labels, taints, capacity/allocatable, conditions และเห็นด้วยตาว่า Node คือ container

**สิ่งที่ต้องมีก่อน:** ทำ [LAB บทที่ 1](../../001_kubernetes-introduction/02_LAB/readme.md) และ [LAB บทที่ 2](../../002_kubernetes_pod/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`) และมีโฟลเดอร์ `003_kubernetes_node_pod` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `003_kubernetes_node_pod` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 003_kubernetes_node_pod k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลัง ต้องสั่ง `docker cp` ซ้ำ โฟลเดอร์นี้มีทั้งไฟล์ YAML ของ LAB 1–9 (`02_LAB/labs/`) และแอปกับ manifest ของ LAB 10 (`02_LAB/som-shop-branches/`) จึงคัดลอกครั้งเดียวพอ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` หน้าต่างนี้คือ **SSH session หลัก** (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/003_kubernetes_node_pod/02_LAB
ls
kubectl get nodes
kubectl get pods
```

`ls` ต้องเห็น `README.md  images  labs  som-shop-branches` จากนั้นเลือกทางตามผลของ `kubectl get nodes`

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node (`lab-control-plane`, `lab-worker`, `lab-worker2`) เป็น `Ready` (คลัสเตอร์จากบทที่ 2 ยังอยู่) | **ใช้ต่อได้เลย** ถ้า `kubectl get pods` ยังมี Pod จากบทที่ 2 ค้าง (เช่น `som-shop`) ให้ลบก่อนด้วย `kubectl delete pod --all` แล้วข้ามไปขั้นที่ 4 |
| error `The connection to the server localhost:8080 was refused - did you specify the right host or port?` (ก่อนหน้ามีบรรทัด `memcache.go ... connection refused` หลายบรรทัด) = ไม่มีคลัสเตอร์ (container ใหม่, เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `time k8s-up` (ประมาณ 1 นาที) |

ผลจริงของ `kubectl get nodes` บน container ใหม่ที่ยังไม่มีคลัสเตอร์ (ผลการทดสอบซ้ำ 5 ต.ค. `kubectl get pods` ก็ได้ข้อความแบบเดียวกัน)

```text
E1005 17:00:47.632122     362 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E1005 17:00:47.632808     362 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E1005 17:00:47.634647     362 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E1005 17:00:47.635184     362 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E1005 17:00:47.636913     362 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

(ยังไม่มี kubeconfig kubectl จึงลองต่อ `localhost:8080` ซึ่งเป็นค่าเริ่มต้น บรรทัด `E1005 ...` คือ log ของ kubectl ที่ลองซ้ำ 5 ครั้ง ตัวเลขวันเวลาและเลข process จะต่างกันในแต่ละเครื่อง)

ผลจริงของ `time k8s-up` (ตัดบางส่วน)

```text
[k8s-up] dockerd ready
[k8s-up] kind create cluster --name lab --config /etc/devtools/kind/kind-lab.yaml
Creating cluster "lab" ...
 ✓ Ensuring node image (kindest/node:v1.37.0) 🖼️
 ✓ Preparing nodes 📦 📦 📦 
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-lab"
...
[k8s-up] waiting for all nodes Ready (timeout 180s)...
node/lab-control-plane condition met
node/lab-worker condition met
node/lab-worker2 condition met
...
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
...

real	0m51.293s
```

(ผลการทดสอบซ้ำ: ข้อความของ kind เหมือนเดิมทุกบรรทัด ได้ `real	0m52.926s` เวลานี้ขึ้นกับความเร็วเครื่อง)

> ข้อความท้าย `k8s-up` มีคำแนะนำตัวอย่างอื่น ๆ ของ image และ port 30080–30082 ซึ่ง **ยังไม่ใช้ในบทนี้** ให้ข้ามไป

### ขั้นที่ 4: อ่าน Node ด้วย kubectl

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl config current-context
kubectl get nodes -o wide
```

```text
kind-lab
NAME                STATUS   ROLES           AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   3m13s   v1.37.0   172.19.0.3    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker          Ready    <none>          2m58s   v1.37.0   172.19.0.4    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker2         Ready    <none>          2m58s   v1.37.0   172.19.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
```

> **INTERNAL-IP อาจต่างกันได้:** kind แจก IP ให้ Node ตามลำดับที่ container ได้ network จึงไม่ตายตัว ในการทดสอบซ้ำได้ `lab-control-plane` 172.19.0.2, `lab-worker` 172.19.0.3, `lab-worker2` 172.19.0.4 ให้จด IP ของเครื่องตัวเองไว้ใช้ใน LAB 8 และ LAB 10

ดู labels ทั้งหมด และดูบาง label เป็นคอลัมน์

```bash
kubectl get nodes --show-labels
kubectl get nodes -L kubernetes.io/arch,kubernetes.io/os
```

```text
NAME                STATUS   ROLES           AGE     VERSION   LABELS
lab-control-plane   Ready    control-plane   3m13s   v1.37.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=lab-control-plane,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=,node.kubernetes.io/exclude-from-external-load-balancers=
lab-worker          Ready    <none>          2m58s   v1.37.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=lab-worker,kubernetes.io/os=linux
lab-worker2         Ready    <none>          2m58s   v1.37.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=lab-worker2,kubernetes.io/os=linux

NAME                STATUS   ROLES           AGE     VERSION   ARCH    OS
lab-control-plane   Ready    control-plane   3m14s   v1.37.0   amd64   linux
lab-worker          Ready    <none>          2m59s   v1.37.0   amd64   linux
lab-worker2         Ready    <none>          2m59s   v1.37.0   amd64   linux
```

(เครื่อง Mac ชิป Apple หรือเครื่อง ARM จะเห็น `arm64`)

ดู capacity เทียบ allocatable และดู taint ของทุก Node

```bash
kubectl get node lab-worker -o jsonpath='{.status.capacity}{"\n"}{.status.allocatable}{"\n"}'
kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key,EFFECT:.spec.taints[*].effect
```

```text
{"cpu":"32","ephemeral-storage":"1081101176832","hugepages-1Gi":"0","hugepages-2Mi":"0","memory":"64489564Ki","pods":"110"}
{"cpu":"32","ephemeral-storage":"1081101176832","hugepages-1Gi":"0","hugepages-2Mi":"0","memory":"64489564Ki","pods":"110"}
NAME                TAINTS                                  EFFECT
lab-control-plane   node-role.kubernetes.io/control-plane   NoSchedule
lab-worker          <none>                                  <none>
lab-worker2         <none>                                  <none>
```

เปิดสมุดประจำเรือทั้งเล่ม

```bash
kubectl describe node lab-worker
```

```text
Name:               lab-worker
Roles:              <none>
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=lab-worker
                    kubernetes.io/os=linux
...
Taints:             <none>
Unschedulable:      false
Lease:
  HolderIdentity:  lab-worker
  AcquireTime:     <unset>
  RenewTime:       Sun, 04 Oct 2026 18:56:27 +0700
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:14 +0700   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:14 +0700   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:14 +0700   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:25 +0700   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:  172.19.0.4
  Hostname:    lab-worker
...
PodCIDR:                      10.244.1.0/24
PodCIDRs:                     10.244.1.0/24
ProviderID:                   kind://docker/lab/lab-worker
Non-terminated Pods:          (2 in total)
  Namespace                   Name                CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                ------------  ----------  ---------------  -------------  ---
  kube-system                 kindnet-dmj46       100m (0%)     0 (0%)      50Mi (0%)        0 (0%)         3m15s
  kube-system                 kube-proxy-7xjpl    0 (0%)        0 (0%)      0 (0%)           0 (0%)         3m15s
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests   Limits
  --------           --------   ------
  cpu                100m (0%)  0 (0%)
  memory             50Mi (0%)  0 (0%)
  ...
Events:
  Type    Reason          Age    From             Message
  ----    ------          ----   ----             -------
  Normal  RegisteredNode  3m11s  node-controller  Node lab-worker event: Registered Node lab-worker in Controller
  Normal  NodeReady       3m4s   kubelet          Node lab-worker status is now: NodeReady
```

### ขั้นที่ 5: เห็นด้วยตาว่า Node คือ container

<p align="center" id="fig-2">
  <img src="images/02-lab0-inside-node-crictl.png" alt="รูปที่ 2 LAB0 Node คือ container" width="900"><br>
  <em><b>รูปที่ 2</b> LAB0: ใน k8s-lab node คือ container ใช้ docker exec lab-worker crictl ps ดู container ระบบที่รันในเรือ</em>
</p>

🐧 **ใน SSH session ของ k8s-lab** (คำสั่ง docker ทั้งหมดนี้คุยกับ dockerd ภายใน k8s-lab)

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
docker exec lab-worker crictl ps
docker exec lab-control-plane crictl ps
```

```text
lab-worker	Up 3 minutes
lab-worker2	Up 3 minutes
lab-control-plane	Up 3 minutes

CONTAINER           IMAGE               CREATED             STATE               NAME                ATTEMPT             POD ID              POD                 NAMESPACE
3ca8b31c44e17       4626fe10df5b9       3 minutes ago       Running             kindnet-cni         0                   f674bc63f9edb       kindnet-dmj46       kube-system
b9af0b8b13988       d6a28daf3e6b0       3 minutes ago       Running             kube-proxy          0                   05719e65616d7       kube-proxy-7xjpl    kube-system

CONTAINER           IMAGE               CREATED             STATE               NAME                      ATTEMPT             POD ID              POD                                         NAMESPACE
59bcd236c4ddc       c82008e2cd018       3 minutes ago       Running             local-path-provisioner    0                   2d36818bffd99       local-path-provisioner-75f7fc7dc5-vt7wv     local-path-storage
92514c60a16f4       520212b8b0fcd       3 minutes ago       Running             coredns                   0                   64bfb45066ab7       coredns-559f6c778d-v4wmg                    kube-system
1c6f8e0bd3d72       520212b8b0fcd       3 minutes ago       Running             coredns                   0                   0e84e592edaf6       coredns-559f6c778d-s7ml2                    kube-system
b1c92e1a9544b       4626fe10df5b9       3 minutes ago       Running             kindnet-cni               0                   95024bff5c608       kindnet-wvgxp                               kube-system
2233927cac939       d6a28daf3e6b0       3 minutes ago       Running             kube-proxy                0                   f86c6da4d3089       kube-proxy-4cmxx                            kube-system
ca021c76b79b3       270fbeb697171       3 minutes ago       Running             etcd                      0                   26949463e5ed8       etcd-lab-control-plane                      kube-system
ab76de321c6e1       1fabf80a1273a       3 minutes ago       Running             kube-scheduler            0                   3f634132644fd       kube-scheduler-lab-control-plane            kube-system
570147fb3b6c3       bec5f0e1e2eeb       3 minutes ago       Running             kube-apiserver            0                   f05894df9c39e       kube-apiserver-lab-control-plane            kube-system
809ec0969fd02       364b3c3d9ec19       3 minutes ago       Running             kube-controller-manager   0                   9d7c2180acf8d       kube-controller-manager-lab-control-plane   kube-system
```

(ถ้าใช้คลัสเตอร์ต่อจากบทที่ 2 ค่า `Up ...` และ `CREATED` จะนานกว่านี้ และ `crictl ps` อาจไม่มี container ของ Pod อื่น เพราะลบไปแล้ว)

### ขั้นที่ 6: สัญญาณวิทยุ (Lease heartbeat)

```bash
kubectl get lease -n kube-node-lease
kubectl get lease lab-worker -n kube-node-lease -o jsonpath='{.spec.renewTime}{"  "}{.spec.leaseDurationSeconds}{"\n"}'; sleep 11; kubectl get lease lab-worker -n kube-node-lease -o jsonpath='{.spec.renewTime}{"\n"}'
```

```text
NAME                HOLDER              AGE
lab-control-plane   lab-control-plane   3m29s
lab-worker          lab-worker          3m6s
lab-worker2         lab-worker2         3m7s
2026-10-04T11:56:27.119121Z  40
2026-10-04T11:56:37.288385Z
```

### สิ่งที่เห็น

- Node ทั้ง 3 `Ready` เวอร์ชัน `v1.37.0` คอลัมน์ `ROLES` ของ worker เป็น `<none>` เพราะไม่มี label `node-role.kubernetes.io/...` มีแต่ control-plane ที่มี
- นอกจาก `kubernetes.io/*` ยังมี label รุ่นเก่า `beta.kubernetes.io/arch|os` และ control-plane มี `node.kubernetes.io/exclude-from-external-load-balancers`
- **allocatable เท่ากับ capacity ทุกค่า** (kind ไม่ได้สงวนทรัพยากรให้ระบบ) และทุก Node เห็น CPU/RAM เท่าเครื่องจริงทั้งเครื่อง (ในตัวอย่าง 32 CPU, ~61.5 GiB) **3 Node ไม่ได้มีทรัพยากร 3 เท่า**
- มี taint เฉพาะ `lab-control-plane` (`NoSchedule`) Pod ของเราจึงไปลงแค่ worker
- `Allocated resources` ของ `lab-worker` มี requests 100m/50Mi จาก `kindnet` อยู่แล้ว
- บนเรือ worker มี container ระบบแค่ `kindnet-cni` และ `kube-proxy` ส่วนหอบังคับการมี etcd, apiserver, scheduler, controller-manager ฯลฯ
- Lease ถูกต่ออายุทุก ~10 วินาที (`11:56:27` → `11:56:37`) และ `leaseDurationSeconds` คือ 40

> **🤔 คำถามชวนคิด:** ถ้า `kubectl get nodes` บอกว่าแต่ละ Node มี memory ~61.5 GiB สร้าง Pod ที่ขอ memory 40 GiB ได้กี่ตัวพร้อมกันตาม scheduler และในความเป็นจริงเครื่องจะรับไหวไหม

**เก็บกวาด:** LAB นี้ไม่ได้สร้างอะไร ไม่ต้องเก็บกวาด

---

## LAB 1: เจ้าหน้าที่จัดตู้กับ Pending

<p align="center" id="fig-3">
  <img src="images/03-lab1-pending.png" alt="รูปที่ 3 LAB1 Pending" width="900"><br>
  <em><b>รูปที่ 3</b> LAB1: Pod ที่ขอ memory เกิน allocatable ค้าง Pending อ่านเหตุผลจาก Events FailedScheduling แล้วลด requests ให้วางได้</em>
</p>

**เป้าหมาย:** เห็นการคัดกรอง (Filtering) จาก requests, อ่านข้อความ `FailedScheduling`, ดู `Allocated resources` เปลี่ยน และแก้ Pod ที่ขอเกิน

**ไฟล์:** `labs/lab01-scheduler/fit-pod.yaml` (nginx ขอ `cpu: 100m, memory: 64Mi`) และ `huge-pod.yaml` (busybox ขอ `memory: 4000Gi`)

```bash
cat labs/lab01-scheduler/fit-pod.yaml labs/lab01-scheduler/huge-pod.yaml
```

### อธิบาย YAML

`labs/lab01-scheduler/fit-pod.yaml`

```yaml
# LAB 1: Pod ขนาดพอดี — scheduler หาเรือที่ "ระวางเหลือพอ" ให้ได้
apiVersion: v1
kind: Pod
metadata:
  name: fit-pod
  labels:
    lab: "03"                 # ทุก Pod ของบทนี้ติดป้าย lab=03 → เก็บกวาดด้วย kubectl delete pod -l lab=03
spec:
  containers:
    - name: web
      image: nginx:1.27-alpine  # web server เล็ก รันค้างได้เองโดยไม่ต้องใส่ command
      resources:
        requests:             # scheduler ใช้ "requests" (ไม่ใช่การใช้งานจริง) เทียบกับ allocatable ของ node
          cpu: 100m           # 0.1 core → Allocated cpu ของเรือเพิ่มจาก 100m (kindnet) เป็น 200m
          memory: 64Mi        # → Allocated memory เพิ่มจาก 50Mi เป็น 114Mi
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `kind: Pod` | Pod เดี่ยว | บทนี้ใช้ Pod เดี่ยวเท่านั้น (ไม่มี controller) | ลบแล้วไม่มีใครสร้างใหม่ |
| `metadata.labels.lab` | `"03"` | ป้ายร่วมของ LAB 1–8 ต้องใส่เครื่องหมายคำพูดเพราะค่า label ต้องเป็นข้อความ (`03` เปล่า ๆ YAML จะอ่านเป็นตัวเลข) | เก็บกวาดด้วย `kubectl delete pod -l lab=03` |
| `containers[0].image` | `nginx:1.27-alpine` | web server ที่รันค้างได้เอง ไม่ต้องใส่ `command` | `fit-pod` เป็น `1/1 Running` |
| `resources.requests.cpu` | `100m` | ขอ 0.1 core ให้ scheduler "จอง" ไว้บนเรือ | ขั้นที่ 3 `Allocated resources` cpu เพิ่มจาก 100m เป็น `200m` |
| `resources.requests.memory` | `64Mi` | ขอ memory น้อย ๆ วางได้ทุก worker | memory เพิ่มจาก 50Mi เป็น `114Mi` |

`labs/lab01-scheduler/huge-pod.yaml`

```yaml
# LAB 1: Pod ที่ขอหน่วยความจำมากเกินกว่าเรือลำไหนจะมี → Pending + Event FailedScheduling
apiVersion: v1
kind: Pod
metadata:
  name: huge-pod
  labels:
    lab: "03"                 # ป้ายของบทนี้ ใช้เก็บกวาดด้วย -l lab=03
spec:
  terminationGracePeriodSeconds: 1   # busybox sleep ไม่ตอบ SIGTERM → ให้ลบเร็ว
  containers:
    - name: app
      image: busybox:1.36       # image เล็กมาก (บนคลัสเตอร์ใหม่ต้อง pull ครั้งแรก)
      command: ["sleep", "3600"]   # busybox ไม่มีโปรแกรมค้างเอง → sleep 1 ชั่วโมงให้ container อยู่ต่อ
      resources:
        requests:               # ขอแค่ memory (ไม่ขอ cpu) → scheduler กรองเรือด้วย memory
          memory: 4000Gi      # 4000 GiB! ไม่มี node ไหนรับไหว (แก้เป็น 256Mi ภายหลัง)
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `terminationGracePeriodSeconds` | `1` | `sleep` ใน busybox ไม่สนใจ SIGTERM ถ้าใช้ค่าเริ่มต้น 30 วินาที การลบจะค้างนาน | `kubectl delete pod huge-pod --now` เสร็จทันที |
| `image` + `command` | `busybox:1.36`, `["sleep", "3600"]` | busybox ไม่มีโปรแกรมที่รันค้าง จึงสั่ง sleep 1 ชั่วโมง | Running ได้หลังลด requests |
| `resources.requests.memory` | `4000Gi` | ขอเกิน allocatable ของทุก Node (ราว 61.5 GiB) ตั้งใจให้ไม่มีเรือไหนผ่านการคัดกรอง | ขั้นที่ 1–2 ค้าง `Pending` พร้อม `2 Insufficient memory` |
| ไม่มี `limits` / ไม่ขอ `cpu` | – | scheduler ดูแค่ requests จึงกรองด้วย memory อย่างเดียว | ขั้นที่ 4–5 ใช้ `sed "s/4000Gi/256Mi/"` เปลี่ยนเฉพาะบรรทัดนี้ |

### ขั้นที่ 1: apply ทั้งโฟลเดอร์

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/003_kubernetes_node_pod/02_LAB` เสมอ)

```bash
kubectl apply -f labs/lab01-scheduler/
kubectl wait --for=condition=Ready pod/fit-pod --timeout=120s; kubectl get pod -o wide
```

```text
pod/fit-pod created
pod/huge-pod created
pod/fit-pod condition met
NAME       READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
fit-pod    1/1     Running   0          7s    10.244.2.2   lab-worker2   <none>           <none>
huge-pod   0/1     Pending   0          7s    <none>       <none>        <none>           <none>
```

### ขั้นที่ 2: อ่านเหตุผลที่ Pending

```bash
kubectl describe pod huge-pod | sed -n '/^Events/,$p'
kubectl get events --field-selector reason=FailedScheduling
```

```text
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  10s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
LAST SEEN   TYPE      REASON             OBJECT         MESSAGE
10s         Warning   FailedScheduling   pod/huge-pod   0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

### ขั้นที่ 3: ดูผลรวม requests บนเรือที่ fit-pod อยู่

```bash
N=$(kubectl get pod fit-pod -o jsonpath={.spec.nodeName}); echo node=$N
kubectl describe node $N | sed -n '/Non-terminated/,/^Events/p'
```

```text
node=lab-worker2
Non-terminated Pods:          (3 in total)
  Namespace                   Name                CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                ------------  ----------  ---------------  -------------  ---
  default                     fit-pod             100m (0%)     0 (0%)      64Mi (0%)        0 (0%)         10s
  kube-system                 kindnet-68hkk       100m (0%)     0 (0%)      50Mi (0%)        0 (0%)         3m55s
  kube-system                 kube-proxy-7k6xk    0 (0%)        0 (0%)      0 (0%)           0 (0%)         3m55s
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                200m (0%)   0 (0%)
  memory             114Mi (0%)  0 (0%)
  ...
```

### ขั้นที่ 4: ลองแก้ requests ด้วย apply (จะไม่สำเร็จ)

ใช้ `sed` เปลี่ยน `4000Gi` เป็น `256Mi` ระหว่างทาง (ไม่แก้ไฟล์ต้นฉบับ) แล้ว apply

```bash
sed "s/4000Gi/256Mi/" labs/lab01-scheduler/huge-pod.yaml | kubectl apply -f -
```

```text
The Pod "huge-pod" is invalid: spec: Forbidden: pod updates may not change fields other than `spec.containers[*].image`,`spec.initContainers[*].image`,`spec.activeDeadlineSeconds`,`spec.tolerations` (only additions to existing tolerations),`spec.terminationGracePeriodSeconds` (allow it to be set to 1 if it was previously negative)
@@ -109,7 +109,7 @@
    "Resources": {
     "Limits": null,
     "Requests": {
-     "memory": "4000Gi"
+     "memory": "256Mi"
     },
...
```

### ขั้นที่ 5: ลบแล้วสร้างใหม่ด้วยค่าที่พอดี

```bash
kubectl delete pod huge-pod --now
sed "s/4000Gi/256Mi/" labs/lab01-scheduler/huge-pod.yaml | kubectl apply -f -; kubectl wait --for=condition=Ready pod/huge-pod --timeout=60s; kubectl get pod -o wide
kubectl describe pod huge-pod | sed -n '/^Events/,$p'
```

```text
pod "huge-pod" deleted from default namespace
pod/huge-pod created
pod/huge-pod condition met
NAME       READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
fit-pod    1/1     Running   0          49s   10.244.2.2   lab-worker2   <none>           <none>
huge-pod   1/1     Running   0          1s    10.244.1.3   lab-worker    <none>           <none>
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  1s    default-scheduler  Successfully assigned default/huge-pod to lab-worker
  Normal  Pulled     1s    kubelet            spec.containers{app}: Container image "busybox:1.36" already present on machine and can be accessed by the pod
  Normal  Created    1s    kubelet            spec.containers{app}: Container created
  Normal  Started    1s    kubelet            spec.containers{app}: Container started
```

> **คลัสเตอร์ที่เพิ่งสร้างใหม่ (ผลการทดสอบซ้ำ):** ผลข้างบนมาจากคลัสเตอร์ที่ใช้ต่อจากบทที่ 2 ซึ่งมี `busybox:1.36` อยู่บนเรือแล้ว (`already present on machine`) ถ้าสร้างคลัสเตอร์ใหม่ด้วย `k8s-up` ใน LAB 0 เรือยังไม่มี image นี้ kubelet จึงต้อง pull ก่อน Events จะเป็นแบบนี้ (เวลา pull ขึ้นกับอินเทอร์เน็ต และ Node/IP อาจต่างกัน)
>
> ```text
> NAME       READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
> fit-pod    1/1     Running   0          13s   10.244.3.2   lab-worker2   <none>           <none>
> huge-pod   1/1     Running   0          5s    10.244.1.2   lab-worker    <none>           <none>
> Events:
>   Type    Reason     Age   From               Message
>   ----    ------     ----  ----               -------
>   Normal  Scheduled  5s    default-scheduler  Successfully assigned default/huge-pod to lab-worker
>   Normal  Pulling    5s    kubelet            spec.containers{app}: Pulling image "busybox:1.36"
>   Normal  Pulled     0s    kubelet            spec.containers{app}: Successfully pulled image "busybox:1.36" in 4.808s (4.808s including waiting). Image size: 2217006 bytes.
>   Normal  Created    0s    kubelet            spec.containers{app}: Container created
>   Normal  Started    0s    kubelet            spec.containers{app}: Container started
> ```

> **รู้ไว้ (ทางเลือก):** Kubernetes 1.37 มี subresource `resize` สำหรับปรับ resources ของ Pod ที่มีอยู่แล้ว ในการทดลองใช้กับ Pod ที่ Pending ได้ และ scheduler วางให้ทันที
> ```bash
> kubectl patch pod huge-pod --subresource resize -p '{"spec":{"containers":[{"name":"app","resources":{"requests":{"memory":"256Mi"}}}]}}'
> ```
> ผลจริง `pod/huge-pod patched` แล้ว Pod เปลี่ยนเป็น `ContainerCreating` บน `lab-worker` ภายใน 3 วินาที (ผลการทดสอบซ้ำ: `sleep 3` แล้วดูอีกครั้ง ได้ `1/1 Running` บน `lab-worker` แล้ว) อย่างไรก็ตามวิธีหลักของบทนี้ยังเป็น "ลบแล้วสร้างใหม่"

### สิ่งที่เห็น

- `fit-pod` ถูกวางบน worker ลำใดลำหนึ่ง (ในตัวอย่าง `lab-worker2`) ไม่ใช่ control-plane
- `huge-pod` Pending เหตุผลนับครบ 3 Node: control-plane ตกเพราะ taint, worker 2 ลำตกเพราะ `Insufficient memory` และ preemption ไม่ช่วย
- `Allocated resources` เพิ่มจาก 100m/50Mi เป็น 200m/114Mi = requests ของ `fit-pod` ถูก "จอง" ไว้
- requests ของ Pod ที่สร้างแล้วแก้ด้วย apply ไม่ได้ (`Forbidden`) ลบแล้วสร้างใหม่จึง Running

> **🤔 คำถามชวนคิด:** ถ้าแก้ `huge-pod` ให้ขอ `cpu: 40` (40 core) แทน memory ข้อความ FailedScheduling จะเปลี่ยนเป็นอย่างไร (คำใบ้: allocatable cpu ของเครื่องตัวเองคือเท่าไร)

### เก็บกวาด LAB 1

```bash
kubectl delete pod -l lab=03 --now; kubectl get pod
```

```text
pod "fit-pod" deleted from default namespace
pod "huge-pod" deleted from default namespace
No resources found in default namespace.
```

---

## LAB 2: nodeName และ Downward API

<p align="center" id="fig-4">
  <img src="images/04-lab2-nodename-downward.png" alt="รูปที่ 4 LAB2 nodeName และ Downward API" width="900"><br>
  <em><b>รูปที่ 4</b> LAB2: nodeName วาง Pod ตรงไปยัง node โดยไม่ผ่าน scheduler และ Downward API ให้ Pod บอกได้ว่าอยู่เรือลำไหน</em>
</p>

**เป้าหมาย:** วาง Pod ตรงเรือโดยข้าม scheduler (ทั้งเรือที่มีจริงและไม่มีจริง) และให้ Pod รู้ว่าตัวเองอยู่บนเรือลำไหนด้วย Downward API

**ไฟล์:** `labs/lab02-nodename-downward/`

| ไฟล์ | สาระสำคัญ |
|---|---|
| `pinned-pod.yaml` | `nodeName: lab-control-plane` **ไม่มี toleration** |
| `ghost-node-pod.yaml` | `nodeName: lab-worker9` (ไม่มี Node นี้) |
| `whereami-pod.yaml` | busybox รับ env `NODE_NAME`, `POD_NAME`, `POD_IP`, `HOST_IP` จาก Downward API และ `GREETING="สวัสดีจาก $(POD_NAME) บนเรือ $(NODE_NAME)"` |

```bash
cat labs/lab02-nodename-downward/whereami-pod.yaml
```

### อธิบาย YAML

`pinned-pod.yaml` และ `ghost-node-pod.yaml` ต่างกันแค่ชื่อ ค่า `nodeName` และ comment ส่วน `spec` ของทั้งสองไฟล์ตามลำดับ

```yaml
spec:
  nodeName: lab-control-plane  # ระบุเรือเอง → scheduler ไม่ตรวจ taint ของ control-plane (ไม่มี toleration ก็ลงได้)
  containers:
    - name: web
      image: nginx:1.27-alpine   # pull บน control-plane ครั้งแรก → Events มีแค่ Pulling/Pulled/Created/Started จาก kubelet
```

```yaml
spec:
  nodeName: lab-worker9        # ไม่มี node ชื่อนี้ในคลัสเตอร์
  containers:
    - name: web
      image: nginx:1.27-alpine   # ไม่มีวันถูก pull เพราะไม่มี kubelet ไหนรับ Pod นี้
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `spec.nodeName` | `lab-control-plane` | ใส่ชื่อเรือเองตั้งแต่ตอนสร้าง scheduler จะข้าม Pod นี้ไป kubelet ของเรือลำนั้นรับไปสร้างเลย จึงไม่มีการตรวจ taint `NoSchedule` ของ control-plane | ขั้นที่ 1 `pinned-pod` Running บน `lab-control-plane` ทั้งที่ไม่มี toleration และขั้นที่ 2 ไม่มี Event `Scheduled` |
| `spec.nodeName` | `lab-worker9` | ชื่อเรือที่ไม่มีในคลัสเตอร์ ไม่มี kubelet ไหนรับ | `NODE lab-worker9` ค้าง `Pending` และ `Events: <none>` แล้วถูก PodGC ลบใน ~1 นาที |
| ไม่มี `tolerations` | – | ตั้งใจไม่ใส่ เพื่อให้เห็นว่า `nodeName` ข้ามด่าน taint ได้ | Tolerations มีแค่ 2 ตัว (`not-ready`, `unreachable` 300s) ที่ระบบเติมให้ |

`whereami-pod.yaml` (Downward API)

```yaml
spec:
  terminationGracePeriodSeconds: 1   # sh/sleep ไม่ตอบ SIGTERM → ให้ลบเสร็จใน 1 วิ
  containers:
    - name: app
      image: busybox:1.36
      env:
        - name: NODE_NAME            # ชื่อ node ที่ Pod ถูกวาง (ต้นเรือเติมให้ตอนสร้าง container)
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_NAME             # ชื่อ Pod เอง (metadata.name)
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP               # IP ของ Pod (10.244.x.x)
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: HOST_IP              # IP ของ node (เช่น 172.19.0.x ใน kind ขึ้นกับ Docker network ของเครื่อง)
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: GREETING             # $(ชื่อตัวแปร) อ้างตัวแปรที่ประกาศ "ก่อนหน้า" ในลิสต์นี้ได้
          value: "สวัสดีจาก $(POD_NAME) บนเรือ $(NODE_NAME)"
      # พิมพ์ข้อความ 1 บรรทัด (อ่านด้วย kubectl logs whereami) แล้ว sleep ให้ Pod อยู่ต่อ
      command: ["sh", "-c", "echo \"$GREETING (Pod IP $POD_IP, Node IP $HOST_IP)\"; sleep 3600"]
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `env[].valueFrom.fieldRef.fieldPath` | `spec.nodeName` | Downward API: kubelet เติมชื่อเรือที่ Pod ถูกวางให้เป็น env ตอนสร้าง container | `NODE_NAME=lab-worker2` |
| | `metadata.name` | ชื่อ Pod | `POD_NAME=whereami` |
| | `status.podIP` | IP ของ Pod (ช่วง Pod CIDR ของเรือ) | `POD_IP=10.244.x.x` ตรงกับ `kubectl get pod -o wide` |
| | `status.hostIP` | IP ของ Node (container ของ kind ใน network 172.19.0.x) | `HOST_IP=172.19.0.x` |
| `GREETING` | `"สวัสดีจาก $(POD_NAME) บนเรือ $(NODE_NAME)"` | `$(ชื่อ)` อ้าง env ที่ประกาศ **ก่อนหน้า** ในลิสต์ได้ kubelet แทนค่าให้ (ไม่ใช่ shell) | `GREETING=สวัสดีจาก whereami บนเรือ lab-worker2` |
| `command` | `sh -c "echo ...; sleep 3600"` | `$GREETING`, `$POD_IP` ในสตริงนี้ **shell** เป็นคนแทนค่า (เขียนแบบ `$ชื่อ` ไม่มีวงเล็บ) แล้ว sleep ให้ Pod อยู่ต่อ | `kubectl logs whereami` ได้ 1 บรรทัด |
| `terminationGracePeriodSeconds` | `1` | `sh`/`sleep` ไม่ตอบ SIGTERM ให้ลบได้เร็ว | ขั้นเก็บกวาดเสร็จทันที |

### ขั้นที่ 1: apply แล้วดูว่าแต่ละตัวไปอยู่ไหน

```bash
kubectl apply -f labs/lab02-nodename-downward/
kubectl wait --for=condition=Ready pod/pinned-pod pod/whereami --timeout=90s; kubectl get pod -o wide
```

```text
pod/ghost-node-pod created
pod/pinned-pod created
pod/whereami created
pod/pinned-pod condition met
pod/whereami condition met
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE                NOMINATED NODE   READINESS GATES
ghost-node-pod   0/1     Pending   0          7s    <none>       lab-worker9         <none>           <none>
pinned-pod       1/1     Running   0          7s    10.244.0.5   lab-control-plane   <none>           <none>
whereami         1/1     Running   0          7s    10.244.2.3   lab-worker2         <none>           <none>
```

### ขั้นที่ 2: Events ของ Pod ที่ไม่ผ่าน scheduler

```bash
kubectl describe pod pinned-pod | sed -n '/^Tolerations/,$p'
kubectl describe pod ghost-node-pod | sed -n '/^Status/p;/^Node:/p;/^Events/,$p'
```

```text
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason   Age   From     Message
  ----    ------   ----  ----     -------
  Normal  Pulling  6s    kubelet  spec.containers{web}: Pulling image "nginx:1.27-alpine"
  Normal  Pulled   0s    kubelet  spec.containers{web}: Successfully pulled image "nginx:1.27-alpine" in 6.086s (6.086s including waiting). Image size: 20984244 bytes.
  Normal  Created  0s    kubelet  spec.containers{web}: Container created
  Normal  Started  0s    kubelet  spec.containers{web}: Container started

Node:             lab-worker9/
Status:           Pending
Events:                      <none>
```

### ขั้นที่ 3: Pod บอกได้ว่าอยู่เรือไหน

```bash
kubectl logs whereami
kubectl exec whereami -- env | grep -E 'NODE|POD|HOST_IP|GREETING'
kubectl get pod whereami -o jsonpath='{.status.podIP} {.status.hostIP}{"\n"}'
```

```text
สวัสดีจาก whereami บนเรือ lab-worker2 (Pod IP 10.244.2.3, Node IP 172.19.0.2)
NODE_NAME=lab-worker2
POD_NAME=whereami
POD_IP=10.244.2.3
HOST_IP=172.19.0.2
GREETING=สวัสดีจาก whereami บนเรือ lab-worker2
10.244.2.3 172.19.0.2
```

(ผลการทดสอบซ้ำได้ `สวัสดีจาก whereami บนเรือ lab-worker2 (Pod IP 10.244.3.3, Node IP 172.19.0.4)` IP ทั้งสองค่าขึ้นกับเครื่อง และ scheduler อาจวาง `whereami` บน `lab-worker` ก็ได้ ขอแค่ค่าใน log ตรงกับ `kubectl get pod whereami -o wide` ของเครื่องตัวเอง)

### ขั้นที่ 4: รอดูชะตากรรมของ ghost-node-pod (ประมาณ 1-1.5 นาที)

รอประมาณ 1-1.5 นาทีหลัง apply แล้วตรวจอีกครั้ง

```bash
kubectl get pod ghost-node-pod
kubectl logs -n kube-system kube-controller-manager-lab-control-plane | grep -i ghost-node-pod
```

```text
Error from server (NotFound): pods "ghost-node-pod" not found
I1004 11:59:08.298093       1 gc_controller.go:348] "PodGC is force deleting Pod" pod="default/ghost-node-pod"
I1004 11:59:08.312539       1 gc_controller.go:264] "Forced deletion of orphaned Pod succeeded" pod="default/ghost-node-pod"
```

(ในการทดลอง ตรวจทุก 5 วินาที เห็น `Pending` จนอายุ 61 วินาที แล้วรอบถัดไปกลายเป็น `NotFound` ผลการทดสอบซ้ำเห็น `Pending` ถึงอายุ 53 วินาที แล้วรอบถัดไป (ราว 57 วินาที) เป็น `NotFound` อีกรอบเห็น Pending ถึงอายุ 74 วินาที (PodGC ลบที่ ~76 วินาที) ถ้ายังเห็น Pending ให้รออีก 30 วินาทีแล้วรันซ้ำ ถ้าตรวจเร็วกว่านั้นจะยังเห็น `Pending` เวลาใน log ของ controller-manager จะเป็นเวลาของเครื่องตัวเอง)

### สิ่งที่เห็น

- `pinned-pod` **Running บน `lab-control-plane` ทั้งที่ไม่มี toleration ของ control-plane** (Tolerations มีแค่ 2 ตัวที่ระบบเติมให้) และ Events **ไม่มี `Scheduled`** มีแต่ Event จาก `kubelet` แสดงว่า scheduler ไม่ได้ยุ่งเลย
- `ghost-node-pod` แสดง `NODE lab-worker9` แต่ค้าง Pending โดยไม่มี Event ใด ๆ แล้วถูก **PodGC** ใน kube-controller-manager ลบทิ้งเอง (orphaned Pod) ราว 1-1.5 นาที
- `whereami` อ่านชื่อเรือ ชื่อ Pod และ IP ของตัวเองได้ ค่า `POD_IP`/`HOST_IP` ตรงกับ `status` และ `$(POD_NAME)`, `$(NODE_NAME)` ใน `GREETING` ถูกแทนค่าแล้ว (เพราะประกาศก่อนหน้าในลิสต์)

> **🤔 คำถามชวนคิด:** ถ้าย้าย `GREETING` ขึ้นไปเป็น env ตัวแรก (ก่อน `NODE_NAME`) `kubectl logs whereami` จะแสดงอะไร

### เก็บกวาด LAB 2

```bash
kubectl delete pod -l lab=03 --now; kubectl get pod
```

```text
pod "pinned-pod" deleted from default namespace
pod "whereami" deleted from default namespace
No resources found in default namespace.
```

---

## LAB 3: ธงเรือ: nodeSelector และ node affinity

<p align="center" id="fig-5">
  <img src="images/05-lab3-flags-selector-affinity.png" alt="รูปที่ 5 LAB3 ธงเรือ" width="900"><br>
  <em><b>รูปที่ 5</b> LAB3: ติด label ให้ node แล้วใช้ nodeSelector และ node affinity (required/preferred/Gt) เลือกเรือ</em>
</p>

**เป้าหมาย:** ติด/แก้/ลบ label ของ Node, เห็น Pod ที่ Pending ถูกวางเองเมื่อติดธง, เห็นว่าลบธงแล้ว Pod เดิมไม่ถูกไล่ และเทียบ required กับ preferred

**ไฟล์:** `labs/lab03-node-labels/`

| ไฟล์ | กฎ |
|---|---|
| `selector-pod.yaml` | `nodeSelector: {fleet: fast}` |
| `affinity-required-pod.yaml` | required `fleet In [fast, eco]` |
| `affinity-preferred-pod.yaml` | 4 Pod `prefer-1..4` (label `group=prefer`) preferred weight 80 `fleet=fast` + weight 20 `cabin Exists` |
| `affinity-gt-pod.yaml` | required `deck Gt ["3"]` |

### อธิบาย YAML

ทุกไฟล์ใช้ container `web` (`nginx:1.27-alpine`) และ label `lab: "03"` เหมือนกัน ต่างกันแค่ส่วน `spec` ที่เลือกเรือ

`selector-pod.yaml`

```yaml
spec:
  nodeSelector:               # ทุก key ต้องตรง (AND) ถ้าไม่มี node ไหนตรง → Pending
    fleet: fast               # ตรงกับ label ที่ติดด้วย kubectl label node ... fleet=fast
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `nodeSelector` | `fleet: fast` | วิธีเลือกเรือที่ง่ายที่สุด: Node ต้องมี label ตรงทุกคู่ (AND) เป็นเงื่อนไขบังคับ | ขั้นที่ 1 Pending (`didn't match Pod's node affinity/selector`) ติดธงในขั้นที่ 2 แล้วถูกวางบน `lab-worker2` เอง และขั้นที่ 6 (ไม่มีเรือ fast) Pending อีก |

`affinity-required-pod.yaml`

```yaml
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:   # ต้องตรงตอนวาง / วางแล้วไม่ตรวจซ้ำ
        nodeSelectorTerms:          # หลาย term = OR
          - matchExpressions:       # หลาย expression ใน term เดียว = AND
              - key: fleet
                operator: In          # In = ค่า label ตรงกับค่าใดค่าหนึ่งในลิสต์
                values: ["fast", "eco"]
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `requiredDuringSchedulingIgnoredDuringExecution` | – | "ต้อง" ตรงตอนจัดวาง ส่วน "IgnoredDuringExecution" คือวางแล้วไม่ตรวจซ้ำ | ขั้นที่ 3 ลบธงแล้ว Pod เดิมไม่ถูกไล่ |
| `nodeSelectorTerms` / `matchExpressions` | 1 term, 1 expression | หลาย term = OR, หลาย expression ใน term เดียว = AND | – |
| `key/operator/values` | `fleet In ["fast", "eco"]` | เขียนเงื่อนไข "ค่าใดค่าหนึ่ง" ซึ่ง nodeSelector ทำไม่ได้ | ขั้นที่ 5 ได้ทั้งสองลำ (ตัวอย่างได้ `lab-worker` ที่เป็น eco) |

`affinity-preferred-pod.yaml` มี 4 Pod (`prefer-1..4`) หน้าตาเหมือนกัน ต่างแค่ `name` ตัวอย่างของ `prefer-1`

```yaml
# LAB 3: node affinity แบบ "อยากได้" (preferred) — 4 Pod หน้าตาเดียวกัน ดูว่าไปเรือไหนบ้าง
# weight สูง = scheduler ให้คะแนนเพิ่มมาก แต่ไม่ใช่คำสั่งบังคับ (ไม่มีเรือตรงก็ยังวางที่อื่นได้)
apiVersion: v1
kind: Pod
metadata:
  name: prefer-1
  labels:
    lab: "03"
    group: prefer             # ใช้เลือกทั้งกลุ่ม -l group=prefer
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 80              # 1–100: อยากได้เรือ fleet=fast มาก
          preference:
            matchExpressions:
              - key: fleet
                operator: In
                values: ["fast"]
        - weight: 20              # อยากได้เรือที่มีป้าย cabin (ค่าอะไรก็ได้) นิดหน่อย
          preference:
            matchExpressions:
              - key: cabin
                operator: Exists  # Exists = มี key นี้ก็พอ ไม่ต้องใส่ values
  containers:
    - name: web
      image: nginx:1.27-alpine
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `labels.group` | `prefer` | ป้ายของกลุ่ม ใช้ลบ/ดูทั้ง 4 ตัวพร้อมกัน | `kubectl delete pod -l group=prefer` ในขั้นที่ 6 |
| `preferredDuringSchedulingIgnoredDuringExecution` | – | "อยากได้" ไม่บังคับ: เรือที่ตรงได้คะแนนเพิ่มตาม `weight` ถ้าไม่มีเรือตรงก็ยังวางที่อื่นได้ | ขั้นที่ 6 ไม่มีเรือ fast ก็ยัง Running ครบ (2 + 2) |
| `weight: 80` + `fleet In ["fast"]` | 80 | ความชอบหลัก (1–100) | ขั้นที่ 5 ทั้ง 4 ตัวไป `lab-worker2` (fast) |
| `weight: 20` + `cabin Exists` | 20 | ความชอบรอง `Exists` ไม่ต้องใส่ `values` (ใช้ในคำถามชวนคิด) | ไม่มีเรือติด `cabin` จึงไม่มีผลในการทดลองหลัก |

`affinity-gt-pod.yaml`

```yaml
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: deck             # label deck=5 (lab-worker2) / deck=2 (lab-worker)
                operator: Gt          # Greater than: ผ่านเฉพาะเรือที่ deck > 3
                values: ["3"]         # ต้องใส่ค่าเดียว และเป็นตัวเลขในเครื่องหมายคำพูด
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `operator: Gt` | `values: ["3"]` | เปรียบเทียบค่า label เป็นจำนวนเต็ม (`Gt`/`Lt` ต้องมีค่าเดียว เขียนเป็นข้อความในเครื่องหมายคำพูด) | ขั้นที่ 5 ได้เฉพาะ `lab-worker2` (`deck=5`) เพราะ `lab-worker` มี `deck=2` |

### ขั้นที่ 1: nodeSelector ก่อนมีธง

```bash
kubectl apply -f labs/lab03-node-labels/selector-pod.yaml; sleep 3; kubectl get pod selector-pod -o wide
kubectl describe pod selector-pod | sed -n '/^Events/,$p'
```

```text
pod/selector-pod created
NAME           READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
selector-pod   0/1     Pending   0          3s    <none>   <none>   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  3s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

### ขั้นที่ 2: ติดธงให้เรือ แล้วดู Pod ถูกวางเอง

```bash
kubectl label node lab-worker2 fleet=fast deck=5
kubectl label node lab-worker fleet=eco deck=2
kubectl get nodes -L fleet,deck
kubectl wait --for=condition=Ready pod/selector-pod --timeout=60s; kubectl get pod selector-pod -o wide
kubectl describe pod selector-pod | sed -n '/^Events/,$p'
```

```text
node/lab-worker2 labeled
node/lab-worker labeled
NAME                STATUS   ROLES           AGE     VERSION   FLEET   DECK
lab-control-plane   Ready    control-plane   6m52s   v1.37.0           
lab-worker          Ready    <none>          6m37s   v1.37.0   eco     2
lab-worker2         Ready    <none>          6m37s   v1.37.0   fast    5
pod/selector-pod condition met
NAME           READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
selector-pod   1/1     Running   0          4s    10.244.2.4   lab-worker2   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  4s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
  Normal   Scheduled         1s    default-scheduler  Successfully assigned default/selector-pod to lab-worker2
  Normal   Pulled            0s    kubelet            spec.containers{web}: Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
  Normal   Created           0s    kubelet            spec.containers{web}: Container created
  Normal   Started           0s    kubelet            spec.containers{web}: Container started
```

สังเกต Events: `FailedScheduling` ตอน apply แล้ว `Scheduled` ตามมาเองหลังติด label (ห่างกันไม่กี่วินาที ในการทดลองถูกวางภายใน ~1 วินาทีหลังติด label) **ไม่ต้องลบแล้วสร้าง Pod ใหม่**

### ขั้นที่ 3: ลบธงหลัง Pod รันแล้ว

```bash
kubectl label node lab-worker2 fleet-; sleep 5; kubectl get nodes -L fleet,deck; kubectl get pod selector-pod -o wide
```

```text
node/lab-worker2 unlabeled
NAME                STATUS   ROLES           AGE     VERSION   FLEET   DECK
lab-control-plane   Ready    control-plane   7m15s   v1.37.0           
lab-worker          Ready    <none>          7m      v1.37.0   eco     2
lab-worker2         Ready    <none>          7m      v1.37.0           5
NAME           READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
selector-pod   1/1     Running   0          26s   10.244.2.4   lab-worker2   <none>           <none>
```

### ขั้นที่ 4: ติดธงคืน และลองเปลี่ยนค่าโดยไม่ใส่ --overwrite

```bash
kubectl label node lab-worker2 fleet=fast
kubectl label node lab-worker2 fleet=eco
kubectl label node lab-worker2 fleet=fast --overwrite; kubectl get nodes -L fleet,deck
```

```text
node/lab-worker2 labeled
error: 'fleet' already has a value (fast), and --overwrite is false
node/lab-worker2 not labeled
NAME                STATUS   ROLES           AGE     VERSION   FLEET   DECK
lab-control-plane   Ready    control-plane   7m15s   v1.37.0           
lab-worker          Ready    <none>          7m      v1.37.0   eco     2
lab-worker2         Ready    <none>          7m      v1.37.0   fast    5
```

(`not labeled` เพราะค่าใหม่เท่ากับค่าเดิม `fast` จึงไม่มีอะไรเปลี่ยน)

### ขั้นที่ 5: required, preferred และ Gt

```bash
kubectl apply -f labs/lab03-node-labels/affinity-required-pod.yaml -f labs/lab03-node-labels/affinity-preferred-pod.yaml -f labs/lab03-node-labels/affinity-gt-pod.yaml; sleep 8; kubectl get pod -o wide
```

```text
pod/affinity-required-pod created
pod/prefer-1 created
pod/prefer-2 created
pod/prefer-3 created
pod/prefer-4 created
pod/affinity-gt-pod created
NAME                    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
affinity-gt-pod         1/1     Running   0          8s    10.244.2.8   lab-worker2   <none>           <none>
affinity-required-pod   1/1     Running   0          8s    10.244.1.4   lab-worker    <none>           <none>
prefer-1                1/1     Running   0          8s    10.244.2.5   lab-worker2   <none>           <none>
prefer-2                1/1     Running   0          8s    10.244.2.6   lab-worker2   <none>           <none>
prefer-3                1/1     Running   0          8s    10.244.2.9   lab-worker2   <none>           <none>
prefer-4                1/1     Running   0          8s    10.244.2.7   lab-worker2   <none>           <none>
selector-pod            1/1     Running   0          35s   10.244.2.4   lab-worker2   <none>           <none>
```

### ขั้นที่ 6: เมื่อไม่มีเรือ fast เลย

ลบกลุ่ม `prefer` แล้วเปลี่ยน `lab-worker2` เป็น `fleet=eco` (ทั้งสองลำเป็น eco) แล้วสร้างใหม่

```bash
kubectl delete pod -l group=prefer --now; kubectl label node lab-worker2 fleet=eco --overwrite; kubectl get nodes -L fleet,deck
kubectl apply -f labs/lab03-node-labels/affinity-preferred-pod.yaml; sleep 6; kubectl get pod -l group=prefer -o wide
```

```text
pod "prefer-1" deleted from default namespace
pod "prefer-2" deleted from default namespace
pod "prefer-3" deleted from default namespace
pod "prefer-4" deleted from default namespace
node/lab-worker2 labeled
NAME                STATUS   ROLES           AGE     VERSION   FLEET   DECK
lab-control-plane   Ready    control-plane   7m45s   v1.37.0           
lab-worker          Ready    <none>          7m30s   v1.37.0   eco     2
lab-worker2         Ready    <none>          7m30s   v1.37.0   eco     5
pod/prefer-1 created
pod/prefer-2 created
pod/prefer-3 created
pod/prefer-4 created
NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
prefer-1   1/1     Running   0          6s    10.244.2.10   lab-worker2   <none>           <none>
prefer-2   1/1     Running   0          6s    10.244.2.11   lab-worker2   <none>           <none>
prefer-3   1/1     Running   0          6s    10.244.1.5    lab-worker    <none>           <none>
prefer-4   1/1     Running   0          6s    10.244.1.6    lab-worker    <none>           <none>
```

เทียบกับ nodeSelector ในสถานการณ์เดียวกัน: ลบ `selector-pod` แล้วสร้างใหม่

```bash
kubectl delete pod selector-pod --now; kubectl apply -f labs/lab03-node-labels/selector-pod.yaml; sleep 3; kubectl get pod selector-pod
kubectl get events --field-selector involvedObject.name=selector-pod,reason=FailedScheduling | tail -1
```

```text
pod "selector-pod" deleted from default namespace
pod/selector-pod created
NAME           READY   STATUS    RESTARTS   AGE
selector-pod   0/1     Pending   0          3s
4s          Warning   FailedScheduling   pod/selector-pod   0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

### สิ่งที่เห็น

- nodeSelector ไม่มีเรือตรง → Pending (`didn't match Pod's node affinity/selector`) ติด label แล้ว **scheduler วางให้เองทันที**
- ลบ label หลัง Pod รันแล้ว Pod **ไม่ถูกไล่** (ตรวจเฉพาะตอนจัดวาง)
- เปลี่ยนค่า label ต้องใส่ `--overwrite`
- required `fleet In [fast, eco]` ได้ทั้งสองลำ (ในตัวอย่างได้ `lab-worker`) ส่วน `Gt "3"` ได้เฉพาะ `lab-worker2` (`deck=5`)
- preferred `fleet=fast` weight 80: เมื่อมีเรือ fast **ทั้ง 4 ตัวไปอยู่ lab-worker2** เมื่อไม่มีเรือ fast เลย ยัง **Running ครบ** (กระจาย 2 + 2) ขณะที่ nodeSelector **Pending**

> **🤔 คำถามชวนคิด:** ถ้าติด label `cabin=yes` ให้ `lab-worker` (ซึ่งเป็น `fleet=eco`) ในตอนที่ `lab-worker2` เป็น `fleet=fast` Pod `prefer-*` ตัวใหม่น่าจะไปเรือไหน เพราะอะไร (คำใบ้: เทียบ weight 80 กับ 20)

### เก็บกวาด LAB 3

ลบ Pod และ **ลบ label `fleet`, `deck` ของทั้งสองลำ**

```bash
kubectl delete pod -l lab=03 --now; kubectl label node lab-worker lab-worker2 fleet- deck-; kubectl get nodes -L fleet,deck
```

```text
pod "affinity-gt-pod" deleted from default namespace
pod "affinity-required-pod" deleted from default namespace
pod "prefer-1" deleted from default namespace
pod "prefer-2" deleted from default namespace
pod "prefer-3" deleted from default namespace
pod "prefer-4" deleted from default namespace
pod "selector-pod" deleted from default namespace
node/lab-worker unlabeled
node/lab-worker2 unlabeled
NAME                STATUS   ROLES           AGE     VERSION   FLEET   DECK
lab-control-plane   Ready    control-plane   7m57s   v1.37.0           
lab-worker          Ready    <none>          7m42s   v1.37.0           
lab-worker2         Ready    <none>          7m42s   v1.37.0           
```

---

## LAB 4: แม่เหล็กระหว่างกล่อง: pod affinity และ anti-affinity

<p align="center" id="fig-6">
  <img src="images/06-lab4-pod-magnets.png" alt="รูปที่ 6 LAB4 แม่เหล็กระหว่างกล่อง" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4: podAffinity ดึง web ไปอยู่เรือเดียวกับ cache ส่วน podAntiAffinity ผลัก crew 3 กล่องให้แยกเรือ กล่องที่ 3 ไม่มีที่จึง Pending</em>
</p>

**เป้าหมาย:** วาง Pod ใกล้/ห่าง Pod อื่นด้วย `topologyKey: kubernetes.io/hostname` และเทียบ required กับ preferred anti-affinity

**ไฟล์:** `labs/lab04-pod-affinity/`

| ไฟล์ | กฎ |
|---|---|
| `cache-pod.yaml` | `cache` (label `app=cache`) ปักที่ `lab-worker` ด้วย nodeSelector `kubernetes.io/hostname: lab-worker` |
| `web-near-cache-pod.yaml` | required podAffinity กับ `app=cache` |
| `crew-anti-pods.yaml` | 3 Pod `crew-1..3` (label `team=crew`) required podAntiAffinity |
| `crew-preferred-pods.yaml` | 3 Pod `deckhand-1..3` (label `team=deckhand`) preferred podAntiAffinity weight 100 |

### อธิบาย YAML

`cache-pod.yaml` (ตู้เย็น = เป้าหมายของแม่เหล็ก)

```yaml
  labels:
    lab: "03"
    app: cache                # web-near-cache จะ "ดึงดูด" Pod ที่มีป้ายนี้
spec:
  nodeSelector:
    kubernetes.io/hostname: lab-worker   # label มาตรฐานที่ทุก node มีอยู่แล้ว = ชื่อ node
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `labels.app` | `cache` | ป้ายที่ `web-near-cache` ใช้ค้นหา | – |
| `nodeSelector` | `kubernetes.io/hostname: lab-worker` | label มาตรฐานที่ทุก Node มี (ค่า = ชื่อ Node) ใช้ปัก cache ไว้ที่เรือที่รู้แน่นอน | ขั้นที่ 2 `cache` อยู่ `lab-worker` |

`web-near-cache-pod.yaml`

```yaml
  labels:
    lab: "03"
    app: web                  # ป้ายของตัวเอง (ไม่ตรงกับ selector app=cache จึงไม่ดึงดูดตัวเอง)
spec:
  affinity:
    podAffinity:                # ดึงดูด: ต้องอยู่ใกล้ Pod เป้าหมาย
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:            # หา Pod อื่นที่มีป้ายนี้ (ใน namespace เดียวกัน)
            matchLabels:
              app: cache
          topologyKey: kubernetes.io/hostname   # "ที่เดียวกัน" = node เดียวกัน
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `podAffinity.required...` | – | ต้องวางบน "ที่เดียวกัน" กับ Pod เป้าหมาย ถ้าไม่มีเป้าหมายเลยก็วางไม่ได้ | ขั้นที่ 1 Pending `didn't match pod affinity rules` |
| `labelSelector.matchLabels` | `app: cache` | Pod เป้าหมาย (ค้นใน namespace เดียวกัน) ป้ายของตัวเองเป็น `app: web` จึงไม่ดึงดูดตัวเอง | ขั้นที่ 2 พอ `cache` เกิด web ถูกวางเองทันที |
| `topologyKey` | `kubernetes.io/hostname` | นิยาม "ที่เดียวกัน" = Node เดียวกัน | ทั้งคู่อยู่ `lab-worker` |

`crew-anti-pods.yaml` มี 3 Pod (`crew-1..3`) เหมือนกัน ต่างแค่ `name` ตัวอย่างของ `crew-1`

```yaml
  labels:
    lab: "03"
    team: crew
spec:
  affinity:
    podAntiAffinity:              # ผลักกัน: ห้ามอยู่เรือลำเดียวกับ Pod team=crew ตัวอื่น
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:          # Pod ที่ "ห้ามอยู่ด้วย" = team=crew (รวมพวกเดียวกันเอง)
            matchLabels:
              team: crew
          topologyKey: kubernetes.io/hostname   # "เรือเดียวกัน" = node เดียวกัน
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `labels.team` + `labelSelector` | `team: crew` ทั้งคู่ | Pod ผลัก Pod ที่มีป้ายเดียวกับตัวเอง = ห้ามลูกเรือสองคนอยู่เรือเดียวกัน | – |
| `podAntiAffinity.required...` | – | บังคับ ถ้าไม่มีเรือว่างก็ไม่วาง | ขั้นที่ 3 ได้ 1 ตัวต่อ worker ตัวที่ 3 Pending `didn't match pod anti-affinity rules` |
| `topologyKey` | `kubernetes.io/hostname` | 1 Node = 1 "ที่" มี worker 2 ลำจึงรับได้ 2 คน | ขั้นที่ 5 ลบ `crew-1` แล้ว `crew-3` ถูกวางเองในไม่กี่วินาที |

`crew-preferred-pods.yaml` มี 3 Pod (`deckhand-1..3`) ตัวอย่างของ `deckhand-1`

```yaml
  labels:
    lab: "03"
    team: deckhand
spec:
  affinity:
    podAntiAffinity:              # แบบ "อยากได้": พยายามแยกเรือ แต่ถ้าไม่มีเรือว่างก็ยอมอยู่ด้วยกัน
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100             # 1–100: คะแนนพิเศษสูงสุดเมื่อแยกเรือได้
          podAffinityTerm:        # แบบ preferred ต้องห่อเงื่อนไขไว้ใน podAffinityTerm
            labelSelector:
              matchLabels:
                team: deckhand
            topologyKey: kubernetes.io/hostname
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `podAntiAffinity.preferred...` | – | "อยากแยกเรือ" แต่ไม่บังคับ | ขั้นที่ 4 Running ครบ 3 ตัว กระจาย 2 + 1 |
| `weight` | `100` | ให้คะแนนสูงสุดกับเรือที่ยังไม่มี deckhand | ตัวแรก ๆ แยกเรือกันก่อน |
| `podAffinityTerm` | `labelSelector` + `topologyKey` | แบบ preferred ต้องห่อเงื่อนไขไว้ใน `podAffinityTerm` (ต่างจากแบบ required ที่เขียนตรง ๆ) | – |

### ขั้นที่ 1: web มาก่อน cache

```bash
kubectl apply -f labs/lab04-pod-affinity/web-near-cache-pod.yaml; sleep 3; kubectl get pod web-near-cache
kubectl get events --field-selector involvedObject.name=web-near-cache,reason=FailedScheduling | tail -1
```

```text
pod/web-near-cache created
NAME             READY   STATUS    RESTARTS   AGE
web-near-cache   0/1     Pending   0          3s
3s          Warning   FailedScheduling   pod/web-near-cache   0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod affinity rules. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

### ขั้นที่ 2: cache มาถึง

```bash
kubectl apply -f labs/lab04-pod-affinity/cache-pod.yaml; kubectl wait --for=condition=Ready pod/cache pod/web-near-cache --timeout=60s; kubectl get pod -o wide -L app
```

```text
pod/cache created
pod/cache condition met
pod/web-near-cache condition met
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES   APP
cache            1/1     Running   0          0s    10.244.1.7   lab-worker   <none>           <none>            cache
web-near-cache   1/1     Running   0          3s    10.244.1.8   lab-worker   <none>           <none>            web
```

### ขั้นที่ 3: ลูกเรือ 3 คน ห้ามอยู่เรือเดียวกัน (required)

```bash
kubectl apply -f labs/lab04-pod-affinity/crew-anti-pods.yaml; sleep 6; kubectl get pod -l team=crew -o wide -L team
kubectl describe pod crew-3 | sed -n '/^Events/,$p'
```

```text
pod/crew-1 created
pod/crew-2 created
pod/crew-3 created
NAME     READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES   TEAM
crew-1   1/1     Running   0          6s    10.244.2.12   lab-worker2   <none>           <none>            crew
crew-2   1/1     Running   0          6s    10.244.1.9    lab-worker    <none>           <none>            crew
crew-3   0/1     Pending   0          6s    <none>        <none>        <none>           <none>            crew
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  6s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

### ขั้นที่ 4: แบบ preferred

```bash
kubectl apply -f labs/lab04-pod-affinity/crew-preferred-pods.yaml; sleep 6; kubectl get pod -l team=deckhand -o wide -L team
```

```text
pod/deckhand-1 created
pod/deckhand-2 created
pod/deckhand-3 created
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES   TEAM
deckhand-1   1/1     Running   0          6s    10.244.2.13   lab-worker2   <none>           <none>            deckhand
deckhand-2   1/1     Running   0          6s    10.244.1.10   lab-worker    <none>           <none>            deckhand
deckhand-3   1/1     Running   0          6s    10.244.2.14   lab-worker2   <none>           <none>            deckhand
```

### ขั้นที่ 5: ลูกเรือคนหนึ่งลงจากเรือ

ลบ crew ตัวที่ Running ตัวหนึ่ง (ในตัวอย่าง `crew-1`) แล้วดู `crew-3`

```bash
kubectl delete pod crew-1 --now; sleep 3; kubectl get pod -l team=crew -o wide
```

```text
pod "crew-1" deleted from default namespace
NAME     READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
crew-2   1/1     Running   0          32s   10.244.1.9    lab-worker    <none>           <none>
crew-3   1/1     Running   0          32s   10.244.2.15   lab-worker2   <none>           <none>
```

### สิ่งที่เห็น

- podAffinity ที่หาเป้าหมายไม่เจอ → Pending (`didn't match pod affinity rules`) แล้ว **ถูกวางเองทันทีเมื่อ cache เกิด** บนเรือเดียวกัน
- required anti-affinity: ได้ 1 ตัวต่อเรือ ตัวที่ 3 Pending (`didn't match pod anti-affinity rules`) เมื่อมีที่ว่างขึ้น (ลบ `crew-1`) ตัวที่ค้างถูกวางเองภายในไม่กี่วินาที
- preferred anti-affinity: Running ครบ กระจาย 2 + 1
- ตัวไหนเป็นตัวที่ Pending ขึ้นกับลำดับที่ scheduler หยิบ (ในการทดลองคือ `crew-3`)

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `topologyKey` ของ `crew-*` เป็น `topology.kubernetes.io/zone` (ซึ่ง Node ใน kind ไม่มี label นี้) คาดว่าผลจะเป็นอย่างไร

### เก็บกวาด LAB 4

```bash
kubectl delete pod -l lab=03 --now; kubectl get pod
```

```text
pod "cache" deleted from default namespace
pod "crew-2" deleted from default namespace
pod "crew-3" deleted from default namespace
pod "deckhand-1" deleted from default namespace
pod "deckhand-2" deleted from default namespace
pod "deckhand-3" deleted from default namespace
pod "web-near-cache" deleted from default namespace
No resources found in default namespace.
```

---

## LAB 5: ตาชั่งกองเรือ: topologySpreadConstraints

<p align="center" id="fig-7">
  <img src="images/07-lab5-spread-scale.png" alt="รูปที่ 7 LAB5 ตาชั่งกองเรือ" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: topologySpreadConstraints กระจาย Pod ให้สมดุล และเห็นกับดัก nodeTaintsPolicy: Ignore ที่นับ control-plane จนเกิด Pending</em>
</p>

**เป้าหมาย:** กระจาย 4 Pod ด้วย `maxSkew: 1` และเห็นด้วยตาว่าค่าเริ่มต้น `nodeTaintsPolicy: Ignore` ทำให้ Pod ค้างใน kind แล้วแก้ด้วย `Honor`

**ไฟล์:** `labs/lab05-topology-spread/`

| ไฟล์ | Pod | label | ต่างกันที่ |
|---|---|---|---|
| `spread-ignore-pods.yaml` | `spread-1..4` | `group=spread` | ไม่ระบุ `nodeTaintsPolicy` (ค่าเริ่มต้น Ignore) |
| `spread-honor-pods.yaml` | `honor-1..4` | `group=honor` | `nodeTaintsPolicy: Honor` |

ทั้งสองไฟล์ใช้ `maxSkew: 1`, `topologyKey: kubernetes.io/hostname`, `whenUnsatisfiable: DoNotSchedule` และใช้ label คนละกลุ่ม จึง apply ต่อกันได้และไม่นับข้ามกลุ่ม

### อธิบาย YAML

แต่ละไฟล์มี 4 Pod หน้าตาเหมือนกัน ต่างแค่ `name` ตัวอย่างของ `spread-1` (`spread-ignore-pods.yaml`)

```yaml
# LAB 5: กระจาย 4 Pod ด้วย maxSkew 1 แบบค่าเริ่มต้น (nodeTaintsPolicy: Ignore)
# Ignore = นับ node ที่มี taint (lab-control-plane) เป็น domain ด้วย ทั้งที่ Pod ไปลงที่นั่นไม่ได้
apiVersion: v1
kind: Pod
metadata:
  name: spread-1
  labels:
    lab: "03"
    group: spread
spec:
  topologySpreadConstraints:
    - maxSkew: 1                         # จำนวน Pod ระหว่าง "เรือที่มากสุด" กับ "เรือที่น้อยสุด" ต่างกันได้ไม่เกิน 1
      topologyKey: kubernetes.io/hostname   # 1 domain = 1 node
      whenUnsatisfiable: DoNotSchedule   # ถ้าทำให้เอียงเกิน → ไม่วาง (Pending)
      labelSelector:                     # นับเฉพาะ Pod กลุ่ม group=spread ในแต่ละ domain
        matchLabels:
          group: spread
  containers:
    - name: web
      image: nginx:1.27-alpine
```

และส่วนที่ต่างใน `honor-1` (`spread-honor-pods.yaml`)

```yaml
  topologySpreadConstraints:
    - maxSkew: 1                         # จำนวน Pod ระหว่าง "เรือที่มากสุด" กับ "เรือที่น้อยสุด" ต่างกันได้ไม่เกิน 1
      topologyKey: kubernetes.io/hostname   # 1 domain = 1 node
      whenUnsatisfiable: DoNotSchedule   # ถ้าทำให้เอียงเกิน → ไม่วาง (Pending)
      labelSelector:                     # นับเฉพาะ Pod กลุ่ม group=honor ในแต่ละ domain
        matchLabels:
          group: honor
      nodeTaintsPolicy: Honor        # ค่าเริ่มต้นคือ Ignore
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `maxSkew` | `1` | จำนวน Pod ของกลุ่มในโดเมนที่มากที่สุดกับน้อยที่สุดต่างกันได้ไม่เกิน 1 | – |
| `topologyKey` | `kubernetes.io/hostname` | 1 โดเมน = 1 Node (มี 3 โดเมนรวม control-plane) | – |
| `whenUnsatisfiable` | `DoNotSchedule` | ถ้าวางแล้วเอียงเกิน ให้ค้าง Pending แทนที่จะวางไปก่อน | `spread-3`, `spread-4` Pending `didn't match pod topology spread constraints` |
| `labelSelector` | `group: spread` / `group: honor` | นับเฉพาะ Pod กลุ่มเดียวกัน สองไฟล์จึงไม่นับปนกัน | ขั้นที่ 3 ทั้งสองกลุ่มอยู่ด้วยกันได้ |
| ไม่มี `nodeTaintsPolicy` (ไฟล์ ignore) | ค่าเริ่มต้น `Ignore` | ยังนับ `lab-control-plane` (ที่ Pod ลงไม่ได้เพราะ taint) เป็นโดเมนที่มี 0 Pod | ได้ 1 + 1 แล้วตัวที่ 3 จะทำให้ skew = 2 − 0 เกิน 1 และ jsonpath ไม่มีฟิลด์นี้ |
| `nodeTaintsPolicy` (ไฟล์ honor) | `Honor` | ไม่นับ Node ที่ Pod ทน taint ไม่ได้ เหลือ 2 โดเมน | `honor-1..4` ได้ 2 : 2 และ jsonpath แสดง `"nodeTaintsPolicy":"Honor"` |

### ขั้นที่ 1: แบบค่าเริ่มต้น (Ignore)

ก่อนรัน ลองทายก่อนว่า 4 Pod จะ Running กี่ตัว

```bash
kubectl apply -f labs/lab05-topology-spread/spread-ignore-pods.yaml; sleep 8; kubectl get pod -l group=spread -o wide
kubectl describe pod spread-3 | sed -n '/^Events/,$p'
```

```text
pod/spread-1 created
pod/spread-2 created
pod/spread-3 created
pod/spread-4 created
NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
spread-1   1/1     Running   0          8s    10.244.2.16   lab-worker2   <none>           <none>
spread-2   1/1     Running   0          8s    10.244.1.11   lab-worker    <none>           <none>
spread-3   0/1     Pending   0          8s    <none>        <none>        <none>           <none>
spread-4   0/1     Pending   0          8s    <none>        <none>        <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  8s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod topology spread constraints. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

ดู spec ที่ระบบเก็บไว้

```bash
kubectl get pod spread-1 -o jsonpath='{.spec.topologySpreadConstraints}{"\n"}'
```

```text
[{"labelSelector":{"matchLabels":{"group":"spread"}},"maxSkew":1,"topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule"}]
```

### ขั้นที่ 2: แบบ Honor

```bash
kubectl apply -f labs/lab05-topology-spread/spread-honor-pods.yaml; sleep 8; kubectl get pod -l group=honor -o wide
kubectl get pod -l group=honor -o jsonpath='{.items[0].spec.topologySpreadConstraints}{"\n"}'
```

```text
pod/honor-1 created
pod/honor-2 created
pod/honor-3 created
pod/honor-4 created
NAME      READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
honor-1   1/1     Running   0          8s    10.244.2.17   lab-worker2   <none>           <none>
honor-2   1/1     Running   0          8s    10.244.1.12   lab-worker    <none>           <none>
honor-3   1/1     Running   0          8s    10.244.2.18   lab-worker2   <none>           <none>
honor-4   1/1     Running   0          8s    10.244.1.13   lab-worker    <none>           <none>
[{"labelSelector":{"matchLabels":{"group":"honor"}},"maxSkew":1,"nodeTaintsPolicy":"Honor","topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule"}]
```

### ขั้นที่ 3: เปรียบเทียบในตารางเดียว

```bash
kubectl get pod -l "group in (spread,honor)" -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,STATUS:.status.phase
```

```text
NAME       NODE          STATUS
honor-1    lab-worker2   Running
honor-2    lab-worker    Running
honor-3    lab-worker2   Running
honor-4    lab-worker    Running
spread-1   lab-worker2   Running
spread-2   lab-worker    Running
spread-3   <none>        Pending
spread-4   <none>        Pending
```

### สิ่งที่เห็น

- แบบค่าเริ่มต้น: 1 + 1 แล้ว **ตัวที่ 3–4 Pending** (`didn't match pod topology spread constraints`) ทั้งที่ worker ยังว่างมาก เพราะ `lab-control-plane` ถูกนับเป็นโดเมนที่มี 0 Pod ตัวที่ 3 จะทำให้ skew = 2 − 0 = 2 เกิน 1
- spec ของแบบค่าเริ่มต้นไม่มีฟิลด์ `nodeTaintsPolicy` เลย (ใช้ค่าเริ่มต้น `Ignore`)
- แบบ `Honor`: ไม่นับ Node ที่ Pod ทน taint ไม่ได้ จึงได้ **2 : 2** ครบ 4 ตัว
- spread ต่างจาก anti-affinity ตรงที่ Pod มากกว่าจำนวน Node ได้ ขอแค่สมดุล

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `whenUnsatisfiable` ของ `spread-*` เป็น `ScheduleAnyway` (ยังเป็น Ignore) คาดว่า `spread-3` และ `spread-4` จะเป็นอย่างไร เพราะอะไร

### เก็บกวาด LAB 5

```bash
kubectl delete pod -l lab=03 --now; kubectl get pod
```

```text
pod "honor-1" deleted from default namespace
...
pod "spread-4" deleted from default namespace
No resources found in default namespace.
```

---

## LAB 6: ป้ายห้ามขึ้นและบัตรผ่าน: taints และ tolerations

<p align="center" id="fig-8">
  <img src="images/08-lab6-taint-pass.png" alt="รูปที่ 8 LAB6 ป้ายห้ามขึ้นและบัตรผ่าน" width="900"><br>
  <em><b>รูปที่ 8</b> LAB6: ติด taint ให้ lab-worker2 แล้วให้เฉพาะ Pod ที่มี toleration ขึ้นได้ และทดลองวาง Pod บน control-plane ด้วย toleration</em>
</p>

**เป้าหมาย:** ใช้ taint `NoSchedule`, toleration, วาง Pod บน control-plane และเห็นผลของ `NoExecute` + `tolerationSeconds`

**ไฟล์:** `labs/lab06-taints/`

| ไฟล์ | Pod | บัตรผ่าน (toleration) | ใบสั่ง (nodeSelector) |
|---|---|---|---|
| `plain-pod.yaml` | `plain-pod` | ไม่มี | ไม่มี |
| `vip-pod.yaml` | `vip-pod` | `dedicated=vip:NoSchedule` | `lab-worker2` |
| `control-plane-pod.yaml` | `control-plane-pod` | `node-role.kubernetes.io/control-plane` `Exists` `NoSchedule` | `node-role.kubernetes.io/control-plane: ""` |
| `noexecute-pods.yaml` | `no-pass` | `dedicated=vip` เท่านั้น | `lab-worker2` |
| | `pass-30s` | `dedicated=vip` + `maintenance=true:NoExecute` 30 วินาที | `lab-worker2` |
| | `pass-forever` | `dedicated=vip` + `maintenance=true:NoExecute` ไม่ระบุเวลา | `lab-worker2` |

### อธิบาย YAML

ไฟล์ที่ใช้ในขั้นที่ 2 (`noexecute-pods.yaml` อธิบายในขั้นที่ 3)

`plain-pod.yaml`

```yaml
# LAB 6: Pod ธรรมดา ไม่มีบัตรผ่าน (toleration) → ขึ้นเรือที่ติดป้ายห้ามขึ้นไม่ได้
apiVersion: v1
kind: Pod
metadata:
  name: plain-pod
  labels:
    lab: "03"
spec:                         # ไม่มี tolerations และ nodeSelector → scheduler เลือกเรือเอง
  containers:
    - name: web
      image: nginx:1.27-alpine
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `spec` ไม่มี `tolerations`/`nodeSelector` | – | Pod "ธรรมดา" ที่ scheduler เลือกเรือได้อิสระ ใช้พิสูจน์ว่า taint กันได้จริง | ขั้นที่ 2 ลง `lab-worker` ทั้ง 5 รอบ |

`vip-pod.yaml`

```yaml
spec:
  tolerations:
    - key: dedicated
      operator: Equal          # key และ value ต้องตรงกับ taint
      value: vip
      effect: NoSchedule       # ทนได้เฉพาะผลแบบ NoSchedule (ไม่ครอบคลุม NoExecute)
  nodeSelector:                # ใบสั่ง: ต้องไปเรือ lab-worker2 เท่านั้น
    kubernetes.io/hostname: lab-worker2
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `tolerations[0]` | `dedicated` `Equal` `vip` `NoSchedule` | บัตรผ่านที่ตรงกับ taint `dedicated=vip:NoSchedule` ทั้ง key, value และ effect | `describe` แสดง `Tolerations: dedicated=vip:NoSchedule` ต่อด้วย 2 ตัวที่ระบบเติม |
| `nodeSelector` | `kubernetes.io/hostname: lab-worker2` | บัตรผ่าน "อนุญาต" ให้ขึ้นแต่ไม่ "ดึง" ไปเรือนั้น จึงต้องมีใบสั่งคู่กัน | ขั้นที่ 2 `vip-pod` อยู่ `lab-worker2` |
| `effect: NoSchedule` เท่านั้น | – | ไม่มีบัตรสำหรับ `maintenance` แบบ `NoExecute` | ขั้นที่ 4 `vip-pod` ถูกไล่ไปพร้อม `no-pass` |

`control-plane-pod.yaml`

```yaml
spec:
  tolerations:                 # บัตรผ่าน taint node-role.kubernetes.io/control-plane:NoSchedule
    - key: node-role.kubernetes.io/control-plane
      operator: Exists         # Exists = ไม่สนค่า value (taint นี้ไม่มี value)
      effect: NoSchedule
  nodeSelector:
    node-role.kubernetes.io/control-plane: ""   # label นี้มีเฉพาะบน control-plane (ค่าว่าง)
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `tolerations[0]` | `node-role.kubernetes.io/control-plane` `Exists` `NoSchedule` | taint ของ control-plane ไม่มี value จึงใช้ `Exists` | – |
| `nodeSelector` | `node-role.kubernetes.io/control-plane: ""` | label นี้มีเฉพาะ control-plane (ค่าว่างต้องเขียน `""`) | ขั้นที่ 2 `control-plane-pod` อยู่ `lab-control-plane` IP `10.244.0.x` |

### ขั้นที่ 1: ติดป้ายห้ามขึ้นที่ lab-worker2

```bash
kubectl taint node lab-worker2 dedicated=vip:NoSchedule
kubectl describe node lab-worker2 | grep -A1 Taints
```

```text
node/lab-worker2 tainted
Taints:             dedicated=vip:NoSchedule
Unschedulable:      false
```

### ขั้นที่ 2: Pod ธรรมดา, Pod VIP และ Pod บน control-plane

```bash
kubectl apply -f labs/lab06-taints/plain-pod.yaml -f labs/lab06-taints/vip-pod.yaml -f labs/lab06-taints/control-plane-pod.yaml
kubectl wait --for=condition=Ready pod -l lab=03 --timeout=60s; kubectl get pod -o wide
kubectl describe pod vip-pod | grep -A3 Tolerations
```

```text
pod/plain-pod created
pod/vip-pod created
pod/control-plane-pod created
pod/control-plane-pod condition met
pod/plain-pod condition met
pod/vip-pod condition met
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE                NOMINATED NODE   READINESS GATES
control-plane-pod   1/1     Running   0          1s    10.244.0.6    lab-control-plane   <none>           <none>
plain-pod           1/1     Running   0          1s    10.244.1.14   lab-worker          <none>           <none>
vip-pod             1/1     Running   0          1s    10.244.2.19   lab-worker2         <none>           <none>
Tolerations:                 dedicated=vip:NoSchedule
                             node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
```

พิสูจน์ว่า `plain-pod` ไม่ได้ลง `lab-worker` เพราะบังเอิญ: ลบแล้วสร้างใหม่ 5 รอบ

```bash
kubectl delete pod plain-pod --now
for i in 1 2 3 4 5; do kubectl apply -f labs/lab06-taints/plain-pod.yaml >/dev/null; kubectl wait --for=condition=PodScheduled pod/plain-pod --timeout=20s >/dev/null; echo "รอบ $i: $(kubectl get pod plain-pod -o jsonpath={.spec.nodeName})"; kubectl delete pod plain-pod --now >/dev/null; done
```

```text
pod "plain-pod" deleted from default namespace
รอบ 1: lab-worker
รอบ 2: lab-worker
รอบ 3: lab-worker
รอบ 4: lab-worker
รอบ 5: lab-worker
```

### ขั้นที่ 3: เตรียม 3 Pod บน lab-worker2 สำหรับป้ายไล่ลงเรือ

<p align="center" id="fig-9">
  <img src="images/09-lab6-noexecute-timer.png" alt="รูปที่ 9 LAB6 NoExecute และนาฬิกาทราย" width="900"><br>
  <em><b>รูปที่ 9</b> LAB6: taint แบบ NoExecute ไล่ no-pass ทันที, pass-30s ถูกไล่หลัง 30 วินาที, pass-forever อยู่ต่อ</em>
</p>

#### อธิบาย YAML: noexecute-pods.yaml

ทั้ง 3 Pod มี `nodeSelector` และบัตร `dedicated=vip` เหมือนกัน (เพื่อให้ขึ้น `lab-worker2` ที่ยังติดป้าย `NoSchedule` จากขั้นที่ 1 ได้) ต่างกันแค่บัตรสำหรับป้ายไล่ลงเรือ ส่วน `spec` ของ `no-pass`

```yaml
spec:
  nodeSelector:                    # ปักทั้ง 3 Pod ไว้ที่ lab-worker2
    kubernetes.io/hostname: lab-worker2
  tolerations:
    - key: dedicated               # บัตรผ่านป้ายเดิม (NoSchedule) เพื่อให้ขึ้นเรือ lab-worker2 ได้ก่อน
      operator: Equal
      value: vip
      effect: NoSchedule
```

ส่วน `tolerations` ของ `pass-30s` และ `pass-forever` ตามลำดับ

```yaml
  tolerations:
    - key: dedicated               # บัตรผ่านป้ายเดิม (NoSchedule) เพื่อให้ขึ้นเรือ lab-worker2 ได้ก่อน
      operator: Equal
      value: vip
      effect: NoSchedule
    - key: maintenance             # บัตรผ่านป้ายไล่ลงเรือ แต่ "มีเวลา" 30 วินาที
      operator: Equal
      value: "true"
      effect: NoExecute
      tolerationSeconds: 30        # นับจากตอนติด taint NoExecute ครบแล้วถูกไล่
```

```yaml
  tolerations:
    - key: dedicated               # บัตรผ่านป้ายเดิม (NoSchedule) เพื่อให้ขึ้นเรือ lab-worker2 ได้ก่อน
      operator: Equal
      value: vip
      effect: NoSchedule
    - key: maintenance             # บัตรผ่านไม่ระบุเวลา → อยู่ต่อได้ตลอด
      operator: Equal
      value: "true"
      effect: NoExecute
```

| Pod | บัตรสำหรับ `maintenance=true:NoExecute` | ทำไม | เห็นผลในการทดลอง (ขั้นที่ 4) |
|---|---|---|---|
| `no-pass` | ไม่มี | ทนป้าย NoExecute ไม่ได้ ถูกไล่ทันทีที่ติดป้าย | หายตั้งแต่ +2 วินาที Event `TaintManagerEviction` |
| `pass-30s` | `Equal "true"` + `tolerationSeconds: 30` | อยู่ต่อได้ 30 วินาทีนับจากตอนติดป้าย แล้วถูกไล่ (`"true"` ต้องมีเครื่องหมายคำพูด ไม่งั้น YAML อ่านเป็น boolean) | ยังอยู่ที่ +20 วินาที หายที่ ~+30–32 วินาที |
| `pass-forever` | `Equal "true"` ไม่มี `tolerationSeconds` | ทนได้ไม่จำกัดเวลา | อยู่ต่อจนเก็บกวาด |

```bash
kubectl apply -f labs/lab06-taints/plain-pod.yaml -f labs/lab06-taints/noexecute-pods.yaml
kubectl wait --for=condition=Ready pod -l group=noexecute --timeout=60s; kubectl get pod -o wide
```

```text
pod/plain-pod created
pod/no-pass created
pod/pass-30s created
pod/pass-forever created
pod/no-pass condition met
pod/pass-30s condition met
pod/pass-forever condition met
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE                NOMINATED NODE   READINESS GATES
control-plane-pod   1/1     Running   0          32s   10.244.0.6    lab-control-plane   <none>           <none>
no-pass             1/1     Running   0          0s    10.244.2.20   lab-worker2         <none>           <none>
pass-30s            1/1     Running   0          0s    10.244.2.21   lab-worker2         <none>           <none>
pass-forever        1/1     Running   0          0s    10.244.2.22   lab-worker2         <none>           <none>
plain-pod           1/1     Running   0          0s    10.244.1.16   lab-worker          <none>           <none>
vip-pod             1/1     Running   0          32s   10.244.2.19   lab-worker2         <none>           <none>
```

**ทายก่อน:** ตอนนี้บน `lab-worker2` มี 4 Pod (`vip-pod`, `no-pass`, `pass-30s`, `pass-forever`) ถ้าติด `maintenance=true:NoExecute` ตัวไหนจะถูกไล่ และเมื่อไร

### ขั้นที่ 4: ติดป้ายไล่ลงเรือ แล้วเฝ้าดู

🖥️ เปิดหน้าต่างใหม่บนเครื่องนักศึกษา `ssh -p 2223 root@localhost` (หน้าต่างเฝ้าดู) แล้ว 🐧 รัน

```bash
kubectl get pod -l lab=03 -w --output-watch-events -o wide
```

🐧 กลับมาที่ SSH session หลัก ติด taint แล้วดูซ้ำเป็นระยะ (เช่น ที่ 2, 20, 32, 45 วินาที)

```bash
kubectl taint node lab-worker2 maintenance=true:NoExecute
kubectl get pod -l lab=03 -o wide
```

ผลจริงที่ +2 และ +32 วินาทีหลังติด taint (ตอนทดสอบใช้ `--no-headers` และพิมพ์เวลาคั่นไว้ จึงไม่มีบรรทัดหัวตาราง)

```text
node/lab-worker2 tainted
--- +2s 19:03:32
control-plane-pod   1/1   Running   0     35s   10.244.0.6    lab-control-plane   <none>   <none>
pass-30s            1/1   Running   0     3s    10.244.2.21   lab-worker2         <none>   <none>
pass-forever        1/1   Running   0     3s    10.244.2.22   lab-worker2         <none>   <none>
plain-pod           1/1   Running   0     3s    10.244.1.16   lab-worker          <none>   <none>
...
--- +32s 19:04:02
control-plane-pod   1/1   Running   0     65s   10.244.0.6    lab-control-plane   <none>   <none>
pass-forever        1/1   Running   0     33s   10.244.2.22   lab-worker2         <none>   <none>
plain-pod           1/1   Running   0     33s   10.244.1.16   lab-worker          <none>   <none>
```

หน้าต่างเฝ้าดู (`--output-watch-events`) ผลจริง (ตัดบางคอลัมน์ท้ายออก)

```text
EVENT      NAME                READY   STATUS    RESTARTS   AGE   IP            NODE
ADDED      control-plane-pod   1/1     Running   0          33s   10.244.0.6    lab-control-plane
ADDED      no-pass             1/1     Running   0          1s    10.244.2.20   lab-worker2
ADDED      pass-30s            1/1     Running   0          1s    10.244.2.21   lab-worker2
ADDED      pass-forever        1/1     Running   0          1s    10.244.2.22   lab-worker2
ADDED      plain-pod           1/1     Running   0          1s    10.244.1.16   lab-worker
ADDED      vip-pod             1/1     Running   0          33s   10.244.2.19   lab-worker2
MODIFIED   vip-pod             1/1     Running   0          33s   10.244.2.19   lab-worker2
MODIFIED   no-pass             1/1     Running   0          1s    10.244.2.20   lab-worker2
MODIFIED   vip-pod             1/1     Terminating   0          33s   10.244.2.19   lab-worker2
MODIFIED   no-pass             1/1     Terminating   0          1s    10.244.2.20   lab-worker2
...
MODIFIED   vip-pod             0/1     Completed     0          33s   10.244.2.19   lab-worker2
DELETED    vip-pod             0/1     Completed     0          33s   10.244.2.19   lab-worker2
MODIFIED   no-pass             0/1     Completed     0          1s    10.244.2.20   lab-worker2
DELETED    no-pass             0/1     Completed     0          1s    10.244.2.20   lab-worker2
MODIFIED   pass-30s            1/1     Running       0          31s   10.244.2.21   lab-worker2
MODIFIED   pass-30s            1/1     Terminating   0          31s   10.244.2.21   lab-worker2
...
DELETED    pass-30s            0/1     Completed     0          31s   10.244.2.21   lab-worker2
```

กด Ctrl+C ในหน้าต่างเฝ้าดูแล้วดู Events

```bash
kubectl get events --field-selector reason=TaintManagerEviction
kubectl get events --sort-by=.lastTimestamp | grep -E "no-pass|pass-30s" | tail -8
```

```text
LAST SEEN   TYPE     REASON                 OBJECT         MESSAGE
61s         Normal   TaintManagerEviction   pod/no-pass    Marking for deletion Pod default/no-pass
31s         Normal   TaintManagerEviction   pod/pass-30s   Marking for deletion Pod default/pass-30s
61s         Normal   TaintManagerEviction   pod/vip-pod    Marking for deletion Pod default/vip-pod
...
61s         Normal    TaintManagerEviction      pod/no-pass                 Marking for deletion Pod default/no-pass
61s         Normal    Killing                   pod/no-pass                 Stopping container web
31s         Normal    Killing                   pod/pass-30s                Stopping container web
31s         Normal    TaintManagerEviction      pod/pass-30s                Marking for deletion Pod default/pass-30s
```

### สิ่งที่เห็น

- `NoSchedule` บน `lab-worker2`: `plain-pod` ไปอยู่ `lab-worker` ทุกรอบ ส่วน `vip-pod` (มีบัตร + ใบสั่ง) ลง `lab-worker2` ได้
- `control-plane-pod` Running บน `lab-control-plane` ได้เพราะมีทั้งบัตรผ่าน taint ของ control-plane และ nodeSelector
- `NoExecute`: `no-pass` ถูกไล่ **ทันที (< 1 วินาที)**, `pass-30s` ถูกไล่ที่ **~30–31 วินาที**, `pass-forever` อยู่ต่อ
- **`vip-pod` ถูกไล่ด้วย** เพราะมีบัตรแค่ `dedicated` ไม่มีบัตร `maintenance` (NoExecute ไล่ทุก Pod ที่ไม่มีบัตรตรง ไม่สนว่ามาก่อนหรือหลัง)
- Pod ที่ถูกไล่: `Terminating` → `Completed` → หายจากรายการภายใน ~1 วินาที (Node ปกติ kubelet ยืนยันได้ทันที) และ **ไม่มี Pod ใหม่เกิดแทน**
- Event ที่บอกว่าถูกไล่เพราะ taint คือ `TaintManagerEviction ... Marking for deletion Pod ...`

> **🤔 คำถามชวนคิด:** ถ้าลบ taint `maintenance=true:NoExecute` ออกตอนที่ `pass-30s` อยู่มาได้ 20 วินาที `pass-30s` จะยังถูกไล่ไหม

### เก็บกวาด LAB 6

ลบ **taint ทั้งสอง** ของ `lab-worker2` และลบ Pod แล้วตรวจว่าเหลือ taint เฉพาะ control-plane

```bash
kubectl taint node lab-worker2 maintenance=true:NoExecute- dedicated=vip:NoSchedule-
kubectl delete pod -l lab=03 --now
kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key; kubectl get pod
```

```text
node/lab-worker2 untainted
pod "control-plane-pod" deleted from default namespace
pod "pass-forever" deleted from default namespace
pod "plain-pod" deleted from default namespace
NAME                TAINTS
lab-control-plane   node-role.kubernetes.io/control-plane
lab-worker          <none>
lab-worker2         <none>
No resources found in default namespace.
```

---

## LAB 7: ซ่อมเรือ: cordon, drain และ uncordon

<p align="center" id="fig-10">
  <img src="images/10-lab7-cordon-drain.png" alt="รูปที่ 10 LAB7 cordon และ drain" width="900"><br>
  <em><b>รูปที่ 10</b> LAB7: cordon lab-worker แล้ว drain ด้วย --ignore-daemonsets --delete-emptydir-data --force Pod เดี่ยวบนเรือหายไปและไม่ถูกสร้างใหม่ ส่วน lab-worker2 ไม่ได้รับ Pod แทน</em>
</p>

**เป้าหมาย:** เห็นความต่างของ cordon กับ drain, อ่าน error ของ drain ทีละด่าน และเห็นชะตากรรมของ Pod เดี่ยว

**ไฟล์:** `labs/lab07-drain/fleet-pods.yaml` มี `cargo-1..4` (nginx กระจาย 2 worker ด้วย topology spread แบบ Honor) และ `pantry` (มี emptyDir ปักที่ `lab-worker`)

> ⚠️ ข้อความ drain ใน LAB นี้มีคำว่า "DaemonSet" ซึ่งหมายถึง Pod ระบบ `kindnet` และ `kube-proxy` ที่ **ระบบดูแลให้ทุกเรือมีหนึ่งตัว** เราไม่ได้สร้างเองและจะเรียนรายละเอียดภายหลัง

### อธิบาย YAML

`fleet-pods.yaml` มี 5 Pod: `cargo-1..4` หน้าตาเหมือนกัน (ต่างแค่ `name`) และ `pantry` ตัวอย่างของ `cargo-1`

```yaml
# LAB 7: กองตู้สินค้า 4 Pod (cargo-1..4 กระจาย 2 worker) + pantry ที่มี emptyDir บน lab-worker
# ทุกตัวเป็น "Pod เดี่ยว" ไม่มี controller ดูแล → ถูก drain แล้วหายไปเลย
apiVersion: v1
kind: Pod
metadata:
  name: cargo-1
  labels:
    lab: "03"
    group: cargo                   # ใช้ใน labelSelector ของ topologySpreadConstraints
spec:
  topologySpreadConstraints:       # กระจาย cargo ให้ 2 worker เท่า ๆ กัน (ทวน LAB 5)
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: DoNotSchedule
      nodeTaintsPolicy: Honor      # ไม่นับ control-plane → ได้ 2 : 2 บน worker
      labelSelector:
        matchLabels:
          group: cargo
  containers:
    - name: web
      image: nginx:1.27-alpine
```

และ `pantry`

```yaml
  name: pantry
  labels:
    lab: "03"
    group: pantry
spec:
  nodeSelector:
    kubernetes.io/hostname: lab-worker   # ครัวเก็บของอยู่บนเรือที่จะเข้าอู่
  volumes:
    - name: scratch
      emptyDir: {}                 # ข้อมูลอยู่บน node → drain ต้องยืนยันด้วย --delete-emptydir-data
  containers:
    - name: web
      image: nginx:1.27-alpine
      volumeMounts:
        - name: scratch
          mountPath: /scratch
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `kind: Pod` (ไม่มี controller) | – | Pod เดี่ยว ไม่มีใครดูแลให้เกิดใหม่ | drain ด่านแรกขอ `--force` (`declare no controller`) และหลัง drain Pod หายไปเลย |
| `topologySpreadConstraints` ของ cargo | `maxSkew: 1`, `nodeTaintsPolicy: Honor`, `group: cargo` | ทวน LAB 5: กระจาย 4 ตู้ให้ 2 worker เท่า ๆ กัน โดยไม่นับ control-plane | ขั้นที่ 1 ได้ cargo ลำละ 2 ตัว (`cargo-2`, `cargo-4` อยู่ `lab-worker` ในตัวอย่าง) |
| `pantry.nodeSelector` | `kubernetes.io/hostname: lab-worker` | ปักครัวไว้บนเรือที่จะ drain แน่นอน | – |
| `pantry.volumes[].emptyDir` + `volumeMounts` | `scratch` → `/scratch` | ข้อมูลอยู่บนดิสก์ของ Node และหายเมื่อ Pod ถูกลบ | drain ขอ `--delete-emptydir-data` (`Pods with local storage: default/pantry`) |

### ขั้นที่ 1: สร้างกองตู้สินค้า

```bash
kubectl apply -f labs/lab07-drain/fleet-pods.yaml; kubectl wait --for=condition=Ready pod -l lab=03 --timeout=60s >/dev/null; kubectl get pod -o wide
```

```text
pod/cargo-1 created
pod/cargo-2 created
pod/cargo-3 created
pod/cargo-4 created
pod/pantry created
NAME      READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1   1/1     Running   0          1s    10.244.2.23   lab-worker2   <none>           <none>
cargo-2   1/1     Running   0          1s    10.244.1.17   lab-worker    <none>           <none>
cargo-3   1/1     Running   0          1s    10.244.2.24   lab-worker2   <none>           <none>
cargo-4   1/1     Running   0          1s    10.244.1.18   lab-worker    <none>           <none>
pantry    1/1     Running   0          1s    10.244.1.19   lab-worker    <none>           <none>
```

### ขั้นที่ 2: cordon

```bash
kubectl cordon lab-worker; kubectl get nodes
kubectl get node lab-worker -o jsonpath='{.spec.unschedulable} {.spec.taints}{"\n"}'
kubectl run late-cargo --image=nginx:1.27-alpine -l lab=03; kubectl wait --for=condition=Ready pod/late-cargo --timeout=60s >/dev/null; kubectl get pod -o wide
```

```text
node/lab-worker cordoned
NAME                STATUS                     ROLES           AGE   VERSION
lab-control-plane   Ready                      control-plane   11m   v1.37.0
lab-worker          Ready,SchedulingDisabled   <none>          11m   v1.37.0
lab-worker2         Ready                      <none>          11m   v1.37.0
true [{"effect":"NoSchedule","key":"node.kubernetes.io/unschedulable","timeAdded":"2026-10-04T12:04:50Z"}]
pod/late-cargo created
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1      1/1     Running   0          2s    10.244.2.23   lab-worker2   <none>           <none>
cargo-2      1/1     Running   0          2s    10.244.1.17   lab-worker    <none>           <none>
cargo-3      1/1     Running   0          2s    10.244.2.24   lab-worker2   <none>           <none>
cargo-4      1/1     Running   0          2s    10.244.1.18   lab-worker    <none>           <none>
late-cargo   1/1     Running   0          1s    10.244.2.25   lab-worker2   <none>           <none>
pantry       1/1     Running   0          2s    10.244.1.19   lab-worker    <none>           <none>
```

### ขั้นที่ 3: drain ทีละด่าน

ด่านที่ 1: ใส่แค่ `--ignore-daemonsets`

```bash
kubectl drain lab-worker --ignore-daemonsets
```

```text
node/lab-worker already cordoned
error: unable to drain node "lab-worker" due to error: [cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4, cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry], continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4
cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry
```

(ลำดับเหตุผลในข้อความนี้ไม่ตายตัว ผลการทดสอบซ้ำขึ้นเหตุผลเรื่อง local storage ก่อน เนื้อหาเหมือนกันทุกอย่าง)

```text
node/lab-worker already cordoned
error: unable to drain node "lab-worker" due to error: [cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry, cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4], continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry
cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4
```

ด่านที่ 2 (เพื่อดูข้อความ): ใส่ `--force --delete-emptydir-data` แต่ไม่ใส่ `--ignore-daemonsets`

```bash
kubectl drain lab-worker --force --delete-emptydir-data 2>&1 | tail -4
```

```text
error: unable to drain node "lab-worker" due to error: cannot delete DaemonSet-managed Pods (use --ignore-daemonsets to ignore): kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl, continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete DaemonSet-managed Pods (use --ignore-daemonsets to ignore): kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl
```

ใส่ครบทั้งสาม

```bash
time kubectl drain lab-worker --ignore-daemonsets --delete-emptydir-data --force
```

```text
node/lab-worker already cordoned
Warning: deleting Pods that declare no controller: default/cargo-2, default/cargo-4, default/pantry; ignoring DaemonSet-managed Pods: kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl
evicting pod default/pantry
evicting pod default/cargo-2
evicting pod default/cargo-4
pod/pantry evicted
pod/cargo-4 evicted
pod/cargo-2 evicted
node/lab-worker drained

real	0m2.064s
```

(ลำดับบรรทัด `evicted` และชื่อ Pod `kindnet-xxxxx`/`kube-proxy-xxxxx` ต่างกันได้ ผลการทดสอบซ้ำได้ `node/lab-worker drained` ใน `real	0m2.067s`)

### ขั้นที่ 4: ดูผลหลัง drain

```bash
kubectl get pod -o wide; kubectl get pod -A -o wide --field-selector spec.nodeName=lab-worker
```

```text
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1      1/1     Running   0          21s   10.244.2.23   lab-worker2   <none>           <none>
cargo-3      1/1     Running   0          21s   10.244.2.24   lab-worker2   <none>           <none>
late-cargo   1/1     Running   0          20s   10.244.2.25   lab-worker2   <none>           <none>
NAMESPACE     NAME               READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
kube-system   kindnet-dmj46      1/1     Running   0          11m   172.19.0.4   lab-worker   <none>           <none>
kube-system   kube-proxy-7xjpl   1/1     Running   0          11m   172.19.0.4   lab-worker   <none>           <none>
```

### ขั้นที่ 5: uncordon

```bash
kubectl uncordon lab-worker; sleep 10; kubectl get nodes; kubectl get pod -o wide
kubectl get events --field-selector involvedObject.kind=Node,involvedObject.name=lab-worker | tail -5
```

```text
node/lab-worker uncordoned
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          12m   v1.37.0
lab-worker2         Ready    <none>          12m   v1.37.0
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1      1/1     Running   0          46s   10.244.2.23   lab-worker2   <none>           <none>
cargo-3      1/1     Running   0          46s   10.244.2.24   lab-worker2   <none>           <none>
late-cargo   1/1     Running   0          45s   10.244.2.25   lab-worker2   <none>           <none>
12m         Normal   Starting                  node/lab-worker   
12m         Normal   RegisteredNode            node/lab-worker   Node lab-worker event: Registered Node lab-worker in Controller
12m         Normal   NodeReady                 node/lab-worker   Node lab-worker status is now: NodeReady
37s         Normal   NodeNotSchedulable        node/lab-worker   Node lab-worker status is now: NodeNotSchedulable
7s          Normal   NodeSchedulable           node/lab-worker   Node lab-worker status is now: NodeSchedulable
```

### สิ่งที่เห็น

- cordon: `Ready,SchedulingDisabled`, `spec.unschedulable: true` + taint `node.kubernetes.io/unschedulable:NoSchedule` Pod เดิมอยู่ต่อ Pod ใหม่ (`late-cargo`) ไป `lab-worker2`
- drain มี 3 ด่าน: Pod เดี่ยว (`--force`), emptyDir (`--delete-emptydir-data`), Pod ระบบที่ทุกเรือต้องมี (`--ignore-daemonsets`) **ทุกครั้งที่ error drain ก็ cordon ไว้แล้ว**
- drain สำเร็จใน ~2 วินาที `cargo-2`, `cargo-4`, `pantry` **หายไปเลย** ไม่มี Pod ใหม่บน `lab-worker2` (ก่อน drain 6 ตัว หลัง drain 3 ตัว)
- บน `lab-worker` เหลือแค่ `kindnet` และ `kube-proxy`
- uncordon แล้ว Node รับ Pod ใหม่ได้ (Event `NodeSchedulable`) แต่ **Pod ที่หายไม่กลับมา** และ Pod บน `lab-worker2` ก็ไม่ย้ายกลับ (ถ้า cordon ถึง uncordon เร็วกว่า ~10 วินาที อาจไม่เห็น 2 Event นี้)

> **🤔 คำถามชวนคิด:** ถ้าในงานจริงเราต้อง drain Node ที่มีร้านน้องส้มอยู่ทุกสัปดาห์ ทำไมการใช้ Pod เดี่ยวจึงไม่เหมาะ และอยากได้อะไรมาช่วย

### เก็บกวาด LAB 7

ตรวจว่า **ไม่มี Node ใดเป็น SchedulingDisabled** (ถ้ามี ให้ `kubectl uncordon <ชื่อ>`)

```bash
kubectl delete pod -l lab=03 --now; kubectl get nodes; kubectl get pod
```

```text
pod "cargo-1" deleted from default namespace
pod "cargo-3" deleted from default namespace
pod "late-cargo" deleted from default namespace
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          12m   v1.37.0
lab-worker2         Ready    <none>          12m   v1.37.0
No resources found in default namespace.
```

---

## LAB 8: เรือหายในหมอก: Node NotReady

<p align="center" id="fig-11">
  <img src="images/11-lab8-docker-stop-fog.png" alt="รูปที่ 11 LAB8 docker stop เรือล่ม" width="900"><br>
  <em><b>รูปที่ 11</b> LAB8: docker stop lab-worker2 จำลองเรือล่ม node เป็น NotReady และถูกใส่ taint unreachable อัตโนมัติ</em>
</p>

**เป้าหมาย:** จำลอง Node ล่ม แล้วดู NotReady, taint อัตโนมัติ, บัตรผ่านเริ่มต้น 300 วินาที, การไล่ Pod (ค้าง Terminating) และการคืนเรือ

**ไฟล์:** `labs/lab08-node-down/fog-pods.yaml` มี 2 Pod ปักที่ `lab-worker2`: `fog-default` (ไม่ได้ใส่ tolerations เอง) และ `fog-fast` (toleration `unreachable`/`not-ready` แบบ `NoExecute` `tolerationSeconds: 30`)

> ⏱️ LAB นี้ใช้เวลารอรวม **ประมาณ 6–7 นาที** (NotReady ~45–55 วินาที + `fog-default` รออีก 300 วินาที) ระหว่างรอทำอย่างอื่นหรือตอบคำถามชวนคิดได้
>
> ⚠️ คำสั่ง `docker stop`/`docker start`/`docker inspect` ทั้งหมดใน LAB นี้ **🐧 รันใน SSH session ของ k8s-lab** และหยุดได้เฉพาะ **`lab-worker2`** ห้ามหยุด `lab-control-plane`

### อธิบาย YAML

`fog-pods.yaml` มี 2 Pod ปักที่ `lab-worker2` ทั้งคู่ ส่วน `spec` ของ `fog-default`

```yaml
spec:
  nodeSelector:
    kubernetes.io/hostname: lab-worker2   # เรือที่เราจะทำให้ "หายในหมอก"
  # ไม่ใส่ tolerations → ระบบ (DefaultTolerationSeconds) เติมให้ 300 วิ
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ส่วน `spec` ของ `fog-fast`

```yaml
spec:
  nodeSelector:
    kubernetes.io/hostname: lab-worker2   # เรือที่เราจะทำให้ "หายในหมอก"
  tolerations:                     # เขียนทับค่าเริ่มต้น 300 วิ ที่ระบบใส่ให้ → ยอมรอแค่ 30 วิ
    - key: node.kubernetes.io/unreachable    # node ขาดการติดต่อ (Ready=Unknown)
      operator: Exists             # taint ระบบไม่มี value จึงใช้ Exists
      effect: NoExecute
      tolerationSeconds: 30
    - key: node.kubernetes.io/not-ready      # node รายงานว่าไม่พร้อม (Ready=False)
      operator: Exists             # taint ระบบไม่มี value จึงใช้ Exists
      effect: NoExecute
      tolerationSeconds: 30
  containers:
    - name: web
      image: nginx:1.27-alpine
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `nodeSelector` | `kubernetes.io/hostname: lab-worker2` | ปักทั้งสองตัวไว้บนเรือที่เราจะ `docker stop` | ขั้นที่ 1 ทั้งคู่อยู่ `lab-worker2` |
| `fog-default` ไม่มี `tolerations` | – | ให้ระบบ (admission plugin DefaultTolerationSeconds) เติมบัตร `not-ready`/`unreachable` `NoExecute` 300 วินาทีให้เอง | ขั้นที่ 1 `-o yaml` เห็น `tolerationSeconds: 300` สองตัว และขั้นที่ 6 ถูกไล่ที่ NotReady + ~300 วินาที |
| `fog-fast.tolerations` `node.kubernetes.io/unreachable` | `Exists` `NoExecute` `30` | ใส่เองเพื่อเขียนทับค่าเริ่มต้น เรือขาดการติดต่อ (Ready=Unknown) แล้วรอแค่ 30 วินาที | ขั้นที่ 5 ถูกไล่ที่ NotReady + ~30 วินาที |
| `fog-fast.tolerations` `node.kubernetes.io/not-ready` | `Exists` `NoExecute` `30` | กรณีเรือรายงานว่าไม่พร้อม (Ready=False) ใส่คู่กันให้ครบเหมือนค่าเริ่มต้น | ใน LAB นี้เรือหายทั้งลำจึงเห็นแค่ taint `unreachable` |
| `operator: Exists` | – | taint ของระบบไม่มี value | – |

### ขั้นที่ 1: สร้าง Pod บนเรือที่จะล่ม และดูบัตรผ่านที่ระบบเติมให้

```bash
kubectl apply -f labs/lab08-node-down/fog-pods.yaml; kubectl wait --for=condition=Ready pod -l group=fog --timeout=60s >/dev/null; kubectl get pod -o wide
kubectl get pod fog-default -o yaml | grep -A10 "tolerations:"
kubectl get pod fog-fast -o jsonpath='{range .spec.tolerations[*]}{.key} {.effect} {.tolerationSeconds}{"\n"}{end}'
docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' lab-control-plane lab-worker lab-worker2
```

```text
pod/fog-default created
pod/fog-fast created
NAME          READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   0          1s    10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Running   0          1s    10.244.2.27   lab-worker2   <none>           <none>
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: kube-api-access-6v6m4
node.kubernetes.io/unreachable NoExecute 30
node.kubernetes.io/not-ready NoExecute 30
/lab-control-plane 172.19.0.3
/lab-worker 172.19.0.4
/lab-worker2 172.19.0.2
```

(**IP ของเรือขึ้นกับเครื่อง** ให้จด IP ของ `lab-worker2` ของตัวเองไว้ เพราะจะไปโผล่ในข้อความ error ของขั้นที่ 4 ผลการทดสอบซ้ำได้ `/lab-control-plane 172.19.0.2`, `/lab-worker 172.19.0.3`, `/lab-worker2 172.19.0.4` และ Pod บน `lab-worker2` ได้ IP `10.244.3.x` แทน `10.244.2.x`)

### ขั้นที่ 2: เปิดหน้าต่างเฝ้าดู

🖥️ เปิดหน้าต่างใหม่ `ssh -p 2223 root@localhost` แล้ว 🐧 รันลูปนี้ (แสดงเวลานับจากเริ่มลูป สถานะ Node และ Pod ทุก 2 วินาที) **เริ่มลูปก่อน แล้วค่อย docker stop ในขั้นถัดไปทันที**

```bash
T0=$(date +%s); while true; do echo "+$(( $(date +%s) - T0 ))s $(kubectl get node lab-worker2 --no-headers | awk '{print $2}') | $(kubectl get pod -l group=fog --no-headers 2>/dev/null | awk '{printf "%s=%s ", $1, $3}')"; sleep 2; done
```

### ขั้นที่ 3: ทำให้เรือหายในหมอก

🐧 **SSH session หลักของ k8s-lab**

```bash
date +%T; time docker stop lab-worker2; docker ps -a --format "{{.Names}}\t{{.Status}}"
```

```text
19:06:19
lab-worker2

real	0m0.821s
lab-worker	Up 13 minutes
lab-worker2	Exited (130) Less than a second ago
lab-control-plane	Up 13 minutes
```

ผลจริงจากสคริปต์เฝ้าดูที่ใช้ตอนทดสอบ (รูปแบบละเอียดกว่าลูปด้านบน ตัดบางบรรทัดและคอลัมน์ท้าย)

```text
19:06:19 +0s node=Ready Ready=True taints=[] pods: fog-default=Running fog-fast=Running
19:06:41 +21s node=Ready Ready=True taints=[] pods: fog-default=Running fog-fast=Running
19:07:03 +42s node=Ready Ready=True taints=[] pods: fog-default=Running fog-fast=Running
19:07:05 +45s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Running fog-fast=Running
19:07:31 +71s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Running fog-fast=Running
19:07:33 +73s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Running fog-fast=Terminating
...
19:12:05 +345s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Terminating fog-fast=Terminating
...
19:12:27 +366s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Terminating fog-fast=Terminating
```

ผลการทดสอบซ้ำ (ลูปแบบเดียวกับขั้นที่ 2 เพิ่มนาฬิกาและ taint ตัดบางบรรทัด) เรือเป็น `NotReady` ช้ากว่ารอบแรก คือ **52 วินาที** หลัง `docker stop` เวลานี้แกว่งได้ราว **45–55 วินาที** ขึ้นกับจังหวะ heartbeat ครั้งสุดท้ายก่อนเรือหยุด

```text
17:06:36 +0s Ready taints=[] | fog-default=Running fog-fast=Running 
17:07:27 +51s Ready taints=[] | fog-default=Running fog-fast=Running 
17:07:29 +53s NotReady taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] | fog-default=Running fog-fast=Running 
17:07:56 +80s NotReady taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] | fog-default=Running fog-fast=Running 
17:07:58 +82s NotReady taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] | fog-default=Running fog-fast=Terminating 
```

<p align="center" id="fig-12">
  <img src="images/12-lab8-eviction-timeline.png" alt="รูปที่ 12 LAB8 ไทม์ไลน์การไล่ Pod" width="900"><br>
  <em><b>รูปที่ 12</b> LAB8: ไทม์ไลน์หลังเรือหายในหมอก: NotReady ประมาณ 45-55 วินาทีหลัง docker stop, fog-fast ถูกไล่หลัง NotReady 30 วินาที, fog-default รอหลัง NotReady 300 วินาที แล้ว docker start คืนเรือ</em>
</p>

### ขั้นที่ 4: สำรวจระหว่างเรือ NotReady (ภายใน 30 วินาทีหลัง NotReady)

```bash
kubectl get nodes
kubectl describe node lab-worker2 | sed -n '/^Taints/,/^Addresses/p'
kubectl get pod -o wide
kubectl get pod fog-default -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}{"\n"}'
```

```text
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   14m   v1.37.0
lab-worker          Ready      <none>          14m   v1.37.0
lab-worker2         NotReady   <none>          14m   v1.37.0
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
  HolderIdentity:  lab-worker2
  AcquireTime:     <unset>
  RenewTime:       Sun, 04 Oct 2026 19:06:10 +0700
Conditions:
  Type             Status    LastHeartbeatTime                 LastTransitionTime                Reason              Message
  ----             ------    -----------------                 ------------------                ------              -------
  MemoryPressure   Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  DiskPressure     Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  PIDPressure      Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  Ready            Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
Addresses:
NAME          READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   0          83s   10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Running   0          83s   10.244.2.27   lab-worker2   <none>           <none>
PodReadyToStartContainers=True Initialized=True Ready=False ContainersReady=True PodScheduled=True 
```

ลองคุยกับ Pod บนเรือที่ล่ม

```bash
timeout 15 kubectl exec fog-default -- hostname; echo "exit=$?"
timeout 15 kubectl logs fog-default | tail -2
kubectl get events --field-selector reason=NodeNotReady | tail -5
```

```text
error: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host
exit=1
Error from server: Get "https://172.19.0.2:10250/containerLogs/default/fog-default/web": dial tcp 172.19.0.2:10250: connect: no route to host
LAST SEEN   TYPE      REASON         OBJECT             MESSAGE
42s         Warning   NodeNotReady   pod/fog-default    Node is not ready
42s         Warning   NodeNotReady   pod/fog-fast       Node is not ready
42s         Normal    NodeNotReady   node/lab-worker2   Node lab-worker2 status is now: NodeNotReady
```

> **IP ในข้อความ error เป็น IP ของ `lab-worker2` ในเครื่องตัวเอง** (ดูได้จาก `docker inspect` ในขั้นที่ 1) ในการทดสอบซ้ำ `lab-worker2` คือ `172.19.0.4` ข้อความจึงเป็น `dial tcp 172.19.0.4:10250: connect: no route to host`
>
> **`kubectl exec` ได้ผลได้ 2 แบบ**
>
> 1. ได้ error ทันที `error: unable to upgrade connection: ... no route to host` และ `exit=1` (ผลข้างบน)
> 2. **ค้างเงียบ ๆ จนครบ 15 วินาทีของ `timeout`** ไม่มีข้อความใด ๆ แล้วได้ `exit=124` (124 คือรหัสของ `timeout` ที่บอกว่าคำสั่งถูกตัดเพราะหมดเวลา) ผลการทดสอบซ้ำเป็นแบบนี้
>
> ```text
> exit=124
> Error from server: Get "https://172.19.0.4:10250/containerLogs/default/fog-default/web": dial tcp 172.19.0.4:10250: connect: no route to host
> LAST SEEN   TYPE      REASON         OBJECT             MESSAGE
> 18s         Warning   NodeNotReady   pod/fog-default    Node is not ready
> 18s         Warning   NodeNotReady   pod/fog-fast       Node is not ready
> 18s         Normal    NodeNotReady   node/lab-worker2   Node lab-worker2 status is now: NodeNotReady
> ```
>
> ทั้งสองแบบมีความหมายเดียวกัน คือ API server ต่อไปยัง kubelet (port 10250) ของเรือที่ล่มไม่ได้ จะได้แบบไหนขึ้นกับว่าการเชื่อมต่อถูกปฏิเสธทันที (`no route to host`) หรือรอจนหมดเวลา ถ้าไม่ใส่ `timeout 15` นำหน้า แบบที่ 2 จะค้างนาน ให้กด Ctrl+C ส่วน `kubectl logs` ทั้งสองรอบได้ `no route to host` เหมือนกัน

### ขั้นที่ 5: fog-fast ถูกไล่ และลอง apply ซ้ำ

ราว 30 วินาทีหลัง NotReady

```bash
kubectl get pod -o wide
kubectl apply -f labs/lab08-node-down/fog-pods.yaml
kubectl get pod fog-fast -o jsonpath='{.metadata.deletionTimestamp} grace={.metadata.deletionGracePeriodSeconds}{"\n"}'
```

```text
NAME          READY   STATUS        RESTARTS   AGE    IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running       0          2m7s   10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Terminating   0          2m7s   10.244.2.27   lab-worker2   <none>           <none>
pod/fog-default unchanged
Warning: Detected changes to resource fog-fast which is currently being deleted.
pod/fog-fast unchanged
2026-10-04T12:08:03Z grace=30
```

(ผลการทดสอบซ้ำ: `fog-fast` เป็น `Terminating` ที่ NotReady + 29 วินาที (+81 วินาทีจาก `docker stop`) apply ซ้ำได้ Warning เดียวกันและ `grace=30` เวลา `deletionTimestamp` เป็นเวลาของเครื่องตัวเอง)

### ขั้นที่ 6: รอ fog-default (ครบ 300 วินาทีหลัง NotReady)

ประมาณ 6 นาทีหลัง `docker stop`

```bash
kubectl get pod -o wide; kubectl get nodes
```

```text
NAME          READY   STATUS        RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Terminating   0          6m25s   10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Terminating   0          6m25s   10.244.2.27   lab-worker2   <none>           <none>
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   19m   v1.37.0
lab-worker          Ready      <none>          19m   v1.37.0
lab-worker2         NotReady   <none>          19m   v1.37.0
```

(ผลการทดสอบซ้ำ: `fog-default` เป็น `Terminating` ที่ NotReady + 299 วินาที (+351 วินาทีจาก `docker stop` เพราะรอบนั้น NotReady ช้ากว่า) จึงควรรอราว 6 นาทีหลัง `docker stop` ก่อนดู)

### ขั้นที่ 7: คืนเรือ

🐧 **SSH session หลักของ k8s-lab**

```bash
docker start lab-worker2; T0=$(date +%s); until kubectl get node lab-worker2 --no-headers | grep -q " Ready "; do sleep 1; done; echo "lab-worker2 กลับ Ready หลัง docker start $(( $(date +%s) - T0 )) วินาที"; kubectl get nodes -o wide
```

```text
lab-worker2
lab-worker2 กลับ Ready หลัง docker start 2 วินาที
NAME                STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   19m   v1.37.0   172.19.0.3    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker          Ready    <none>          19m   v1.37.0   172.19.0.4    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker2         Ready    <none>          19m   v1.37.0   172.19.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
```

รอประมาณ 10–30 วินาที แล้วตรวจ

```bash
kubectl get pod -o wide
kubectl get node lab-worker2 -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key
kubectl get pod -n kube-system -o wide --field-selector spec.nodeName=lab-worker2
```

```text
No resources found in default namespace.
NAME          TAINTS
lab-worker2   <none>
NAME               READY   STATUS    RESTARTS      AGE   IP           NODE          NOMINATED NODE   READINESS GATES
kindnet-68hkk      1/1     Running   1 (33s ago)   19m   172.19.0.2   lab-worker2   <none>           <none>
kube-proxy-7k6xk   1/1     Running   1 (33s ago)   19m   172.19.0.2   lab-worker2   <none>           <none>
```

สคริปต์เฝ้าดูหลัง `docker start` (ผลจริง)

```text
19:12:31 +3s node=Ready Ready=True taints=[node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Unknown fog-fast=Unknown
19:12:33 +5s node=Ready Ready=True taints=[node.kubernetes.io/unreachable:NoExecute ] pods:
19:12:35 +7s node=Ready Ready=True taints=[] pods:
```

(ผลการทดสอบซ้ำ: Ready หลัง `docker start` 2 วินาที Pod ที่ถูกไล่หายตามมาอีกราว 2 วินาที และ taint หายอีกราว 3 วินาทีถัดไป ลำดับเหมือนกัน ตัวเลขวินาทีแกว่งได้เล็กน้อย RESTARTS ของ `kindnet`/`kube-proxy` เป็น `1` เช่นกัน)

กด Ctrl+C หยุดลูปในหน้าต่างเฝ้าดู

### ขั้นที่ 8 (ทางเลือก): เรือกลับมาก่อนครบเวลา

ทำซ้ำ แต่คืนเรือ **10 วินาทีหลัง NotReady** (ก่อนครบ 30 วินาทีของ `fog-fast`)

```bash
kubectl apply -f labs/lab08-node-down/fog-pods.yaml; kubectl wait --for=condition=Ready pod -l group=fog --timeout=60s >/dev/null; kubectl get pod -o wide
T0=$(date +%s); docker stop lab-worker2 >/dev/null; until kubectl get node lab-worker2 --no-headers | grep -q NotReady; do sleep 1; done; echo "NotReady หลัง docker stop $(( $(date +%s) - T0 )) วินาที"; sleep 10; docker start lab-worker2 >/dev/null; T1=$(date +%s); until kubectl get node lab-worker2 --no-headers | grep -q " Ready "; do sleep 1; done; echo "Ready หลัง docker start $(( $(date +%s) - T1 )) วินาที"; sleep 15; kubectl get pod -o wide
```

```text
pod/fog-default created
pod/fog-fast created
NAME          READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   0          1s    10.244.2.2   lab-worker2   <none>           <none>
fog-fast      1/1     Running   0          1s    10.244.2.3   lab-worker2   <none>           <none>
NotReady หลัง docker stop 50 วินาที
Ready หลัง docker start 2 วินาที
NAME          READY   STATUS    RESTARTS      AGE   IP           NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   1 (17s ago)   79s   10.244.2.3   lab-worker2   <none>           <none>
fog-fast      1/1     Running   1 (17s ago)   79s   10.244.2.2   lab-worker2   <none>           <none>
```

(ผลการทดสอบซ้ำได้ `NotReady หลัง docker stop 52 วินาที`, `Ready หลัง docker start 2 วินาที`, RESTARTS `1 (17s ago)` และ IP สลับกันเหมือนเดิม แต่เป็น `10.244.3.2`/`10.244.3.3`)

### สิ่งที่เห็น

- `docker stop` ใช้เวลาไม่ถึง 1 วินาที แต่ Node ยังแสดง `Ready` อีก **~45–55 วินาที** (รอบแรกวัดได้ 44–50 วินาที ผลการทดสอบซ้ำ 52 วินาทีทั้งสองครั้ง และ 47 วินาทีใน LAB 10) ก่อนเป็น `NotReady` เพราะหอบังคับการรอ grace period ก่อนตัดสิน (heartbeat สุดท้าย 19:06:10 → NotReady 19:07:03)
- condition ทุกตัวเป็น `Unknown` (`Kubelet stopped posting node status.`) พร้อม taint `node.kubernetes.io/unreachable` ทั้ง `NoSchedule` และ `NoExecute`
- Pod บนเรือยังแสดง `1/1 Running` แต่ condition `Ready=False` และ exec/logs ใช้ไม่ได้ (`dial tcp <IP ของ lab-worker2>:10250: connect: no route to host` ในตัวอย่างคือ 172.19.0.2 ผลการทดสอบซ้ำคือ 172.19.0.4) โดย `kubectl exec` อาจได้ error ทันที (`exit=1`) หรือค้างจน `timeout` ตัด (`exit=124`)
- `fog-fast` ถูกไล่ที่ **NotReady + ~30 วินาที** (+73 วินาทีจาก stop, ผลการทดสอบซ้ำ +81) `fog-default` ถูกไล่ที่ **NotReady + ~300 วินาที** (+345 วินาทีจาก stop, ผลการทดสอบซ้ำ +351) **เวลานับจาก NotReady ไม่ใช่จาก docker stop**
- ถูกไล่แล้วค้าง `Terminating` จนเรือกลับ ไม่มี Pod ใหม่เกิดที่ `lab-worker` และ apply ซ้ำได้แค่ Warning `currently being deleted`
- `docker start` → Ready ใน 2 วินาที IP เดิม Pod ที่ถูกไล่หายจริงใน ~5 วินาที taint หายใน ~7 วินาที `kindnet`/`kube-proxy` RESTARTS +1
- ถ้าเรือกลับก่อนครบเวลา Pod ไม่ถูกไล่ แต่ RESTARTS เป็น 1 และ **Pod IP เปลี่ยน** (สลับ `.2` กับ `.3`)

> **🤔 คำถามชวนคิด:** ทำไมระบบจึงตั้งค่าเริ่มต้นให้รอถึง 300 วินาทีก่อนไล่ Pod แทนที่จะไล่ทันทีที่ NotReady ข้อดีและข้อเสียคืออะไร

### เก็บกวาด LAB 8

ตรวจว่า **`lab-worker2` กลับมาเป็น `Ready`** (ถ้ายังเป็น NotReady ให้ 🐧 `docker start lab-worker2` แล้วรอ) จากนั้นลบ Pod

```bash
kubectl delete pod -l lab=03 --now; kubectl get nodes; kubectl get pod
```

```text
pod "fog-default" deleted from default namespace
pod "fog-fast" deleted from default namespace
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   22m   v1.37.0
lab-worker          Ready    <none>          21m   v1.37.0
lab-worker2         Ready    <none>          21m   v1.37.0
No resources found in default namespace.
```

---

## LAB 9: ตู้ของต้นเรือ: static Pod

<p align="center" id="fig-13">
  <img src="images/13-lab9-static-pod.png" alt="รูปที่ 13 LAB9 static Pod" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9: วางไฟล์ manifest ลง /etc/kubernetes/manifests ใน lab-worker ด้วย docker cp kubelet สร้าง static Pod และ mirror pod static-snack-lab-worker</em>
</p>

**เป้าหมาย:** เห็นว่า kubelet สร้าง Pod จากไฟล์บนเรือเองโดยไม่ผ่าน scheduler, รู้จัก mirror pod และวิธีลบ static Pod ที่ถูกต้อง

**ไฟล์:** `labs/lab09-static-pod/static-snack.yaml` (nginx ชื่อ `static-snack`) — **ไม่ได้ติด label `lab=03`** โดยตั้งใจ เพื่อไม่ให้คำสั่งเก็บกวาดของ LAB อื่นไปลบ mirror pod แล้วค้าง

> ⚠️ คำสั่ง `docker exec lab-control-plane ...`, `docker exec lab-worker ...` และ `docker cp ... lab-worker:...` ใน LAB นี้ **🐧 รันใน SSH session ของ k8s-lab**

### ขั้นที่ 1: static Pod ของหอบังคับการ

```bash
docker exec lab-control-plane ls /etc/kubernetes/manifests
kubectl get pod -n kube-system -o wide | grep lab-control-plane
```

```text
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
coredns-559f6c778d-s7ml2                    1/1     Running   0             22m   10.244.0.4   lab-control-plane   <none>           <none>
coredns-559f6c778d-v4wmg                    1/1     Running   0             22m   10.244.0.3   lab-control-plane   <none>           <none>
etcd-lab-control-plane                      1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kindnet-wvgxp                               1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-apiserver-lab-control-plane            1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-controller-manager-lab-control-plane   1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-proxy-4cmxx                            1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-scheduler-lab-control-plane            1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
```

### ขั้นที่ 2: ตรวจแฟ้มบนเรือ lab-worker

```bash
docker exec lab-worker grep staticPodPath /var/lib/kubelet/config.yaml; docker exec lab-worker ls -la /etc/kubernetes/manifests
```

```text
staticPodPath: /etc/kubernetes/manifests
total 8
drwxr-xr-x 2 root root 4096 Aug 20 11:25 .
drwxr-xr-x 1 root root 4096 Oct  4 11:53 ..
```

### ขั้นที่ 3: วางแฟ้มลงบนเรือ

#### อธิบาย YAML: static-snack.yaml

```yaml
# LAB 9: static Pod — ไฟล์นี้ไม่ได้ kubectl apply แต่ copy ไปวางใน /etc/kubernetes/manifests บน node
# ต้นเรือ (kubelet) อ่านไฟล์แล้วสร้าง Pod เอง ไม่ผ่าน scheduler / API server
apiVersion: v1
kind: Pod
metadata:
  name: static-snack           # ชื่อที่ kubectl เห็นจะต่อท้ายด้วยชื่อ node เช่น static-snack-lab-worker
  labels:                      # ไม่ติด lab=03 โดยตั้งใจ กันคำสั่งเก็บกวาดของ LAB อื่นไปลบ mirror pod
    app: static-snack
spec:
  containers:
    - name: web
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80    # nginx ฟังที่ port 80 (ประกาศไว้เป็นข้อมูล)
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| (ทั้งไฟล์) | Pod ธรรมดา | **ไม่ได้ส่งผ่าน `kubectl apply`** แต่ `docker cp` ไปวางใน `staticPodPath` (`/etc/kubernetes/manifests`) ของเรือ kubelet อ่านไฟล์แล้วสร้าง Pod เอง ไม่ผ่าน scheduler | ขั้นที่ 4 Events ไม่มี `Scheduled` และ annotation `kubernetes.io/config.source: file` |
| `metadata.name` | `static-snack` | kubelet ต่อท้ายด้วยชื่อ Node ตอนสร้าง mirror pod ใน API server | ชื่อที่เห็นคือ `static-snack-lab-worker` |
| `metadata.labels` | `app: static-snack` (ไม่มี `lab: "03"`) | ตั้งใจไม่ติด `lab=03` เพื่อไม่ให้คำสั่งเก็บกวาดของ LAB อื่นไปลบ mirror pod แล้วค้าง | `kubectl delete pod -l lab=03` ไม่แตะ Pod นี้ |
| ไม่มี `namespace` | ค่าเริ่มต้น `default` | mirror pod จึงอยู่ใน `default` | เห็นด้วย `kubectl get pod` ธรรมดา |
| `ports[].containerPort` | `80` | ประกาศ port ของ nginx ไว้เป็นข้อมูล (ไม่ได้เปิดอะไรเพิ่ม) | – |

```bash
docker exec lab-worker mkdir -p /etc/kubernetes/manifests
docker cp labs/lab09-static-pod/static-snack.yaml lab-worker:/etc/kubernetes/manifests/
kubectl wait --for=condition=Ready pod/static-snack-lab-worker --timeout=60s; kubectl get pod -o wide
```

(`mkdir -p` ไม่จำเป็นเพราะโฟลเดอร์มีอยู่แล้ว แต่ใส่ไว้กันพลาดได้ ถ้า `kubectl wait` ขึ้น `NotFound` เพราะ mirror pod ยังไม่ทันโผล่ ให้รอ 2–3 วินาทีแล้วรันใหม่)

```text
pod/static-snack-lab-worker condition met
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
static-snack-lab-worker   1/1     Running   0          0s    10.244.1.20   lab-worker   <none>           <none>
```

### ขั้นที่ 4: ตรวจว่าเป็น mirror pod

```bash
kubectl get pod static-snack-lab-worker -o yaml | grep -E -A6 "^  annotations:|^  ownerReferences:"
kubectl describe pod static-snack-lab-worker | sed -n '/^Events/,$p'
```

```text
  annotations:
    kubernetes.io/config.hash: 2f1365a1083c561d7f460f6a6525964b
    kubernetes.io/config.mirror: 2f1365a1083c561d7f460f6a6525964b
    kubernetes.io/config.seen: "2026-10-04T12:15:43.509068771Z"
    kubernetes.io/config.source: file
  creationTimestamp: "2026-10-04T12:15:43Z"
  generation: 1
--
  ownerReferences:
  - apiVersion: v1
    controller: true
    kind: Node
    name: lab-worker
    uid: 15dc410e-40e0-4d3f-9d68-88b5ee898db2
  resourceVersion: "3625"
Events:
  Type    Reason   Age   From     Message
  ----    ------   ----  ----     -------
  Normal  Pulled   18s   kubelet  spec.containers{web}: Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
  Normal  Created  18s   kubelet  spec.containers{web}: Container created
  Normal  Started  18s   kubelet  spec.containers{web}: Container started
```

### ขั้นที่ 5: ลองลบด้วย kubectl

`kubectl delete` mirror pod จะค้างประมาณ 1 นาที จึงใส่ `--wait=false` แล้วดูด้วย `-w` (กด Ctrl+C เมื่อเห็น Pod กลับมา)

```bash
kubectl delete pod static-snack-lab-worker --wait=false
kubectl get pod -w -o wide --output-watch-events
```

```text
pod "static-snack-lab-worker" deleted from default namespace
19:19:13 EVENT      NAME                      READY   STATUS        RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
19:19:13 ADDED      static-snack-lab-worker   1/1     Terminating   0          5s    10.244.1.22   lab-worker   <none>           <none>
19:20:33 MODIFIED   static-snack-lab-worker   1/1     Terminating   0          85s   10.244.1.22   lab-worker   <none>           <none>
19:20:33 DELETED    static-snack-lab-worker   1/1     Terminating   0          85s   10.244.1.22   lab-worker   <none>           <none>
19:20:33 ADDED      static-snack-lab-worker   0/1     Pending       0          0s    <none>        lab-worker   <none>           <none>
```

(ผลจริงข้างบนมาจากรอบที่เติมเวลาไว้หน้าบรรทัด ผลการทดสอบซ้ำค้าง `Terminating` 70 วินาที (17:14:50 → 17:16:00, AGE 4s → 74s) แล้ว `DELETED` ตามด้วย `ADDED ... Pending` เหมือนกัน) ดู container จริงบนเรือ

```bash
docker exec lab-worker crictl ps --name web
```

```text
CONTAINER           IMAGE               CREATED              STATE               NAME                ATTEMPT             POD ID              POD                       NAMESPACE
23a0a2ec810e2       6769dc3a703c7       About a minute ago   Running             web                 0                   9b3ca85cc9e1c       static-snack-lab-worker   default
```

### ขั้นที่ 6: ลบให้หายจริง

```bash
docker exec lab-worker rm /etc/kubernetes/manifests/static-snack.yaml; sleep 4; kubectl get pod; docker exec lab-worker ls /etc/kubernetes/manifests
```

```text
No resources found in default namespace.
```

(`ls` ไม่แสดงอะไร = โฟลเดอร์ว่างแล้ว ในการทดลองวัดได้ว่า Pod หายภายใน 3 วินาทีหลังลบไฟล์)

### สิ่งที่เห็น

- องค์ประกอบหลักของหอบังคับการเป็น static Pod จาก 4 ไฟล์ใน `/etc/kubernetes/manifests` ชื่อลงท้าย `-lab-control-plane` และใช้ IP ของ Node
- `staticPodPath` ของ worker คือ `/etc/kubernetes/manifests` (มีอยู่แล้วและว่าง)
- วางไฟล์แล้ว mirror pod `static-snack-lab-worker` โผล่และ Ready เกือบทันที **Events ไม่มี `Scheduled`**
- mirror pod มี annotation `kubernetes.io/config.mirror`, `config.source: file` และ `ownerReferences` เป็น `kind: Node`
- `kubectl delete` ค้าง Terminating ราว 60–85 วินาที แล้ว **ถูกสร้างกลับมา** ส่วน container จริงไม่ถูกรีสตาร์ต (ATTEMPT 0)
- ลบไฟล์บนเรือ → Pod หายจริงในไม่กี่วินาที

> **🤔 คำถามชวนคิด:** ถ้า kube-scheduler ของคลัสเตอร์ล่ม Pod ใหม่ทั่วไปจะเป็นอย่างไร และ static Pod ที่วางไฟล์ใหม่จะยังเกิดได้ไหม เพราะอะไร

### เก็บกวาด LAB 9

ต้องมั่นใจว่า **ไม่มีไฟล์ static Pod ค้างบนเรือ** (ถ้าค้าง Pod จะกลับมาเองแม้รีสตาร์ตเรือ)

```bash
docker exec lab-worker rm -f /etc/kubernetes/manifests/static-snack.yaml
docker exec lab-worker ls /etc/kubernetes/manifests
kubectl get pod
```

---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มหลายสาขาบนกองเรือ

<p align="center" id="fig-14">
  <img src="images/14-lab10-opening-branches.png" alt="รูปที่ 14 LAB10 ภาพเปิด 2 สาขาบนเรือคนละลำ" width="900"><br>
  <em><b>รูปที่ 14</b> LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้ม 2 สาขา som-shop-a และ som-shop-b บนเรือคนละลำ</em>
</p>

**เป้าหมาย:** เปิดร้านอาหารแมวน้องส้ม (Next.js + PostgreSQL จากบทที่ 2) **2 สาขาเป็น Pod เดี่ยว 2 ตัวบนเรือคนละลำ** โดยรวมทุกอย่างที่เรียนในบทนี้

- **node label + required node affinity**: เปิดสาขาได้เฉพาะเรือที่ติดธง `shop=open`
- **required pod anti-affinity**: สาขาของร้านห้ามอยู่เรือลำเดียวกัน
- **Downward API + `$(NODE_NAME)`**: ชื่อร้านบอกเองว่าอยู่เรือลำไหน
- **toleration `tolerationSeconds: 60`**: ถ้าเรือหายในหมอกเกิน 60 วินาที ยอมให้ถูกไล่
- **drain** เรือของสาขาหนึ่ง และ **เรือล่ม** ของอีกสาขา แล้วดูว่าร้านเป็นอย่างไร

**ไฟล์:** `som-shop-branches/` (อยู่ใน k8s-lab ที่ `/workspace/003_kubernetes_node_pod/02_LAB/som-shop-branches/` ตั้งแต่ `docker cp` ใน LAB 0)

| path | เนื้อหา |
|---|---|
| `som-shop-branches/app/` | แอป Next.js + `Dockerfile` + `scripts/seed.mjs` **สำเนาจากบทที่ 2 ไม่ได้แก้โค้ด** |
| `som-shop-branches/k8s/som-shop-a.yaml` | Pod สาขา a |
| `som-shop-branches/k8s/som-shop-b.yaml` | Pod สาขา b (ต่างจาก a แค่ชื่อและ label `branch: b`) |
| `som-shop-branches/k8s/som-shop-c.yaml` | Pod สาขา c ไว้ทดลองว่า "เรือเต็ม" |

> **หมายเหตุเรื่องหน้าเว็บ:** เพราะใช้แอปเดิมจากบทที่ 2 ทั้งหมด footer ของหน้าเว็บจึงยังเขียน `Next.js + PostgreSQL · Kubernetes LAB 002` และข้อความบนหัวเว็บยังเป็น `⚓ ท่าเรือ Kubernetes · Pod เดียวครบทั้งร้าน` ไม่ใช่ข้อผิดพลาด ส่วนชื่อร้านมาจาก env `SHOP_NAME` ที่เราตั้งใหม่

### 10.1 สถาปัตยกรรมและโครง manifest

เป้าหมายที่ต้องการ (scheduler เป็นคนเลือกว่าสาขาไหนได้เรือลำไหน เรากำหนดแค่ "คนละลำ")

```text
lab-control-plane  (taint control-plane:NoSchedule, ไม่มีธง shop)  ← ไม่มีสาขา
lab-worker   [shop=open]  └─ Pod som-shop-a  "ร้านอาหารแมวน้องส้ม สาขา lab-worker"    ← port-forward 3001
lab-worker2  [shop=open]  └─ Pod som-shop-b  "ร้านอาหารแมวน้องส้ม สาขา lab-worker2"   ← port-forward 3002
(สาขา a อาจได้ lab-worker2 และ b ได้ lab-worker ก็ได้ ให้ดูของจริงจาก kubectl get pod -o wide)
```

แต่ละสาขาเป็น Pod all-in-one แบบเดียวกับ `som-shop` ในบทที่ 2: `db` (native sidecar) → `wait-for-db` → `db-seed` → `web` และ **มีฐานข้อมูลใน emptyDir ของตัวเอง** ออเดอร์ของสาขา a จึงไม่เห็นที่สาขา b (เป็นข้อจำกัดที่ตั้งใจให้เห็นในบทนี้ บทหน้าจะใช้ฐานข้อมูลกลาง)

<p align="center" id="fig-15">
  <img src="images/15-lab10-manifest-anatomy.png" alt="รูปที่ 15 โครง manifest ของสาขา" width="900"><br>
  <em><b>รูปที่ 15</b> โครง Pod สาขา: nodeAffinity เลือกเรือที่มีธง shop=open, podAntiAffinity ห้ามสาขาอยู่เรือเดียวกัน และ Downward API ใส่ NODE_NAME ในชื่อร้าน</em>
</p>

#### อธิบาย YAML

`som-shop-a.yaml`, `som-shop-b.yaml` และ `som-shop-c.yaml` **เหมือนกันทุกบรรทัด ยกเว้น** `metadata.name` (`som-shop-a|b|c`), label `branch` (`a|b|c`) และบรรทัด comment แรก ดูไฟล์เต็มด้วย `cat som-shop-branches/k8s/som-shop-a.yaml` ด้านล่างแบ่งไฟล์ `som-shop-a.yaml` เป็น 3 ช่วงติดกัน

**ช่วงที่ 1: ส่วนที่เพิ่มจากบทที่ 2 (labels, กฎจัดวาง, tolerations, volume)**

```yaml
# LAB 10: ร้านอาหารแมวน้องส้ม สาขา a — Pod เดี่ยว (web + db ใน Pod เดียวเหมือนบท 002) + กฎจัดวางบนกองเรือ
# som-shop-a / som-shop-b / som-shop-c ต่างกันแค่ชื่อและ label branch (ไม่มี Deployment จึงต้องก๊อปปี้ YAML เอง)
apiVersion: v1
kind: Pod
metadata:
  name: som-shop-a
  labels:
    app: som-shop                # ป้ายร้าน ใช้เลือกทุกสาขา -l app=som-shop
    part: branch                 # ใช้ในกฎ podAntiAffinity ด้านล่าง
    branch: a                    # ป้ายแยกสาขา (ดูด้วย -L branch)
spec:
  affinity:
    nodeAffinity:                # ต้องเปิดบนเรือที่ติดธง shop=open เท่านั้น
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: shop
                operator: In
                values: ["open"]
    podAntiAffinity:             # สาขาของ som-shop ห้ามอยู่เรือลำเดียวกัน (1 เรือ 1 สาขา)
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels:
              app: som-shop
              part: branch
          topologyKey: kubernetes.io/hostname
  tolerations:                   # เรือหายในหมอกเกิน 60 วิ → ยอมให้ถูกไล่ (ค่าเริ่มต้น 300 วิ นานไปสำหรับ LAB)
    - key: node.kubernetes.io/unreachable
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 60
    - key: node.kubernetes.io/not-ready
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 60

  volumes:
    - name: db-data              # ฐานข้อมูลของสาขานี้เท่านั้น (แต่ละสาขามี emptyDir ของตัวเอง) หายเมื่อ Pod ถูกลบ
      emptyDir: {}
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `labels.app` / `labels.part` / `labels.branch` | `som-shop` / `branch` / `a` | `app` ใช้เลือกทุกสาขา (`-l app=som-shop`), `app`+`part` เป็นเป้าของ anti-affinity, `branch` ไว้ดูด้วย `-L branch` | 10.3 คอลัมน์ `BRANCH` และ 10.11 ลบทุกสาขาด้วย `-l app=som-shop` |
| `nodeAffinity` required `shop In ["open"]` | – | สาขาเปิดได้เฉพาะเรือที่เราติดธง ถ้ายังไม่ติดธง → Pending | 10.3 ขั้นที่ 1 Pending `didn't match Pod's node affinity/selector` ติดธงแล้วถูกวางเอง |
| `podAntiAffinity` required, `labelSelector: app=som-shop, part=branch`, `topologyKey: kubernetes.io/hostname` | – | ทุกสาขา (ที่มี label ทั้งสอง) ห้ามอยู่เรือเดียวกัน เรือ `shop=open` มี 2 ลำ จึงเปิดได้สูงสุด 2 สาขา | 10.5 `som-shop-c` Pending `2 node(s) didn't match pod anti-affinity rules` และ 10.8 Pending ระหว่าง cordon |
| `tolerations` `unreachable`/`not-ready` `NoExecute` | `tolerationSeconds: 60` | เขียนทับค่าเริ่มต้น 300 วินาที (เหมือน `fog-fast` ใน LAB 8) ให้ LAB ไม่ต้องรอนาน | 10.9 `som-shop-b` ถูกไล่ที่ NotReady + ~60 วินาที |
| `volumes[].emptyDir` | `db-data` | ฐานข้อมูลของแต่ละสาขาอยู่ใน emptyDir ของ Pod ตัวเอง | ออเดอร์แยกกันต่อสาขา, 10.7 drain ต้องใส่ `--delete-emptydir-data` และสาขาที่เปิดใหม่ออเดอร์เริ่มที่ 0 |

**ช่วงที่ 2: initContainers (เหมือนบทที่ 2)**

```yaml

  initContainers:                # เหมือนบท 002 ทุกบรรทัด
    # 1) db: native sidecar (restartPolicy: Always) → เริ่มก่อนและรันตลอดอายุ Pod
    - name: db
      image: postgres:17.11-alpine
      restartPolicy: Always      # init container ที่มี restartPolicy: Always = native sidecar
      env:
        - name: POSTGRES_USER
          value: som
        - name: POSTGRES_PASSWORD
          value: meow1234        # เพื่อการเรียนเท่านั้น
        - name: POSTGRES_DB
          value: catshop
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata   # โฟลเดอร์ย่อยใน emptyDir ให้ initdb ทำงานได้
      ports:
        - containerPort: 5432
      volumeMounts:
        - name: db-data
          mountPath: /var/lib/postgresql/data
      startupProbe:              # รอ postgres พร้อม (สูงสุด 30 × 2 วิ) ก่อนเริ่ม init container ถัดไป
        exec:
          command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
        periodSeconds: 2
        failureThreshold: 30
      readinessProbe:
        exec:
          command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
        periodSeconds: 5
      livenessProbe:             # port 5432 ไม่ตอบ 3 ครั้งติด → รีสตาร์ต db
        tcpSocket:
          port: 5432
        periodSeconds: 10
        failureThreshold: 3
      resources:
        requests: { cpu: 100m, memory: 256Mi }   # requests ที่ scheduler นับ (db)
        limits:   { cpu: 500m, memory: 512Mi }

    # 2) wait-for-db: รอจนต่อ db ได้
    - name: wait-for-db
      image: postgres:17.11-alpine
      command:
        - sh
        - -c
        - until pg_isready -h localhost -p 5432 -U som -d catshop; do echo "รอฐานข้อมูล..."; sleep 2; done; echo "ฐานข้อมูลพร้อมแล้ว"
      resources:
        requests: { cpu: 10m, memory: 16Mi }
        limits:   { cpu: 100m, memory: 64Mi }

    # 3) db-seed: สร้างตาราง + สินค้าตั้งต้น
    - name: db-seed
      image: som-shop-web:1.0
      imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน node ไม่ไปดึงจาก registry
      command: ["node", "scripts/seed.mjs"]
      env:
        - name: DATABASE_URL
          value: postgres://som:meow1234@localhost:5432/catshop
      resources:
        requests: { cpu: 50m, memory: 64Mi }
        limits:   { cpu: 300m, memory: 256Mi }
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| `db` + `restartPolicy: Always` | `postgres:17.11-alpine` | init container ที่มี `restartPolicy: Always` คือ native sidecar เริ่มก่อนและรันคู่กับ `web` ตลอดอายุ Pod จึงนับเป็น 1 ใน `2/2` | 10.3 ลำดับ `Init:0/3` → `Init:1/3` และ `1/2` (db พร้อมแล้ว) |
| `db.env` `POSTGRES_*`, `PGDATA` | `som` / `meow1234` / `catshop`, `.../data/pgdata` | สร้างผู้ใช้และฐานข้อมูลตอนเริ่ม `PGDATA` เป็นโฟลเดอร์ย่อยใน volume ที่ mount | – |
| `db.startupProbe` / `readinessProbe` / `livenessProbe` | `pg_isready` ทุก 2/5 วินาที, TCP 5432 ทุก 10 วินาที | sidecar ต้องผ่าน startupProbe ก่อน init container ถัดไปจึงเริ่ม | – |
| `wait-for-db` | ลูป `pg_isready` | รอจนต่อฐานข้อมูลได้ | `Init:2/3` |
| `db-seed` | `node scripts/seed.mjs` | สร้างตารางและสินค้าตั้งต้น 6 รายการ (สินค้า id 1 มี 20 ชิ้น) | 10.6 สั่งซื้อแล้ว stock 19, 18 |
| `imagePullPolicy: IfNotPresent` | – | ใช้ `som-shop-web:1.0` ที่ `kind load` ไว้บน Node (ไม่มีใน registry) | ถ้าไม่ได้ทำ 10.2 จะค้าง `ErrImagePull` (ดู Troubleshooting) |
| `resources` | db 100m/256Mi | requests ของ sidecar ถูกนับรวมกับ `web` ตลอดอายุ Pod | 10.10 ทางเลือก |

**ช่วงที่ 3: container หลัก `web` (Downward API)**

```yaml

  containers:
    - name: web
      image: som-shop-web:1.0
      imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน node ไม่ไปดึงจาก registry
      env:
        - name: NODE_NAME          # Downward API: ชื่อเรือที่ Pod นี้ถูกวาง (ต้องประกาศก่อน SHOP_NAME)
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: SHOP_NAME          # $(NODE_NAME) ถูกแทนค่าตอนสร้าง container → "สาขา lab-worker" หรือ "สาขา lab-worker2"
          value: "ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"
        - name: DATABASE_URL
          value: postgres://som:meow1234@localhost:5432/catshop
        - name: PORT
          value: "3000"
        - name: HOSTNAME
          value: "0.0.0.0"
      ports:
        - containerPort: 3000
      readinessProbe:              # /api/health ตอบ 200 → Pod Ready (2/2)
        httpGet:
          path: /api/health
          port: 3000
        periodSeconds: 5
        failureThreshold: 2
      livenessProbe:
        httpGet:
          path: /api/health
          port: 3000
        initialDelaySeconds: 10
        periodSeconds: 10
        failureThreshold: 6
      resources:
        requests: { cpu: 100m, memory: 192Mi }   # web 100m/192Mi + db 100m/256Mi = 200m/448Mi ต่อสาขา
        limits:   { cpu: 500m, memory: 512Mi }
```

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | เห็นผลในการทดลอง |
|---|---|---|---|
| env `NODE_NAME` จาก `spec.nodeName` | Downward API | ชื่อเรือที่ Pod ถูกวาง ต้องประกาศก่อน `SHOP_NAME` | 10.4 `NODE_NAME=lab-worker` / `lab-worker2` |
| env `POD_IP` จาก `status.podIP` | Downward API | IP ของ Pod | 10.4 ตรงกับคอลัมน์ `IP` |
| env `SHOP_NAME` | `"ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"` | kubelet แทนค่า `$(NODE_NAME)` ตอนสร้าง container หน้าเว็บอ่าน `SHOP_NAME` ตอน runtime จึงแสดงชื่อสาขาตามเรือ (และชื่อแท็บของ browser ก็เปลี่ยนตามด้วย) | 10.6 `<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>` |
| env `DATABASE_URL`, `PORT`, `HOSTNAME` | `localhost:5432`, `3000`, `0.0.0.0` | web คุยกับ db ผ่าน localhost เพราะอยู่ Pod เดียวกัน และฟังทุก interface ให้ port-forward เข้าถึงได้ | 10.4 `/api/health` ได้ `{"ok":true,"db":"up"}` |
| `readinessProbe` / `livenessProbe` | `GET /api/health` | Ready เมื่อเว็บและ db พร้อม | ช่วงแรกมี Event `Unhealthy ... connection refused` ได้ (10.9) เป็นเรื่องปกติ |
| `resources.requests` | web 100m/192Mi | รวมกับ db = 200m/448Mi ต่อสาขา | 10.10 ทางเลือก `cpu 300m`, `memory 498Mi` (รวม `kindnet` 100m/50Mi) |
| ไฟล์ `som-shop-b.yaml`, `som-shop-c.yaml` | ก๊อปปี้ไฟล์เดิม | เปลี่ยนแค่ชื่อและ `branch` เพราะยังไม่มีตัวช่วยสร้าง Pod หลายตัวจากแม่แบบเดียว | 10.12 ปูทางสู่ Deployment |

### 10.2 เตรียม image ให้ทุก Node

<p align="center" id="fig-16">
  <img src="images/16-lab10-images-ready.png" alt="รูปที่ 16 เตรียม image ให้ทุก Node" width="900"><br>
  <em><b>รูปที่ 16</b> เตรียม image: build som-shop-web:1.0 จากบทที่ 2 แล้ว kind load ไปทุก node ส่วน postgres ใช้ docker save --platform แล้ว kind load image-archive</em>
</p>

**ตรวจก่อนว่าต้องทำไหม** ถ้าใช้คลัสเตอร์ต่อจากบทที่ 2 (ไม่ได้ `k8s-up` ใหม่) image อาจมีบนทั้งสอง worker แล้ว ข้ามขั้นนี้ได้

```bash
docker image ls som-shop-web
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

ถ้าทั้ง `lab-worker` และ `lab-worker2` มีทั้ง `som-shop-web 1.0` และ `postgres 17.11-alpine` ให้ข้ามไป 10.3 ถ้าไม่มี (เช่น สร้างคลัสเตอร์ใหม่ใน LAB 0) ทำต่อดังนี้

**ขั้นที่ 1: build image ของเว็บ** (ประมาณ 30 วินาที ถ้าเคย build ในบทที่ 2 จะเร็วขึ้นเพราะมี cache)

```bash
docker build -t som-shop-web:1.0 som-shop-branches/app 2>&1 | tail -5
```

```text
#16 exporting manifest list sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807 0.0s done
#16 naming to docker.io/library/som-shop-web:1.0 done
#16 unpacking to docker.io/library/som-shop-web:1.0
#16 unpacking to docker.io/library/som-shop-web:1.0 1.3s done
#16 DONE 2.4s
```

**ขั้นที่ 2: นำเข้าทุก Node**

```bash
time kind load docker-image som-shop-web:1.0 --name lab
```

```text
Image: "som-shop-web:1.0" with ID "sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.0" with ID "sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.0" with ID "sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807" not yet present on node "lab-control-plane", loading...

real	0m4.863s
```

**ขั้นที่ 3: postgres** ใช้วิธีเดียวกับบทที่ 2 (`docker save --platform` แล้ว `kind load image-archive` เลี่ยงปัญหา image หลาย platform) เครื่อง ARM (เช่น Mac ชิป Apple) ให้เปลี่ยนเป็น `--platform linux/arm64`

```bash
docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

```text
docker.io/library/postgres:17.11-alpine
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  b95826bfd89f2       76.6MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  b95826bfd89f2       76.6MB
```

(ผลการทดสอบซ้ำบนคลัสเตอร์ใหม่: ตอนตรวจก่อนทำ `docker image ls som-shop-web` มีแค่บรรทัดหัวตาราง และ `crictl images` ของทั้งสองเรือว่าง build ใช้ `real 0m31.014s`, `kind load` ใช้ `real 0m6.062s` image ID ของ `som-shop-web` (`sha256:...` และ `38832335a6026` ใน `crictl`) จะต่างจากตัวอย่างทุกครั้งที่ build ใหม่ และลำดับบรรทัด `not yet present on node ...` ของ 3 Node สลับกันได้)

> image ต้องอยู่บน **ทุก worker** เพราะเราไม่รู้ล่วงหน้าว่า scheduler จะวางสาขาไหนบนเรือลำไหน (`kind load` ใส่ให้ทุก Node อยู่แล้ว)

### 10.3 เปิดสาขาก่อนติดธง แล้วติดธง

**ขั้นที่ 1:** apply ทั้งสองสาขาตอนที่ยังไม่มีเรือลำไหนติดธง `shop=open`

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-a.yaml -f som-shop-branches/k8s/som-shop-b.yaml; sleep 3; kubectl get pod -l app=som-shop -o wide
kubectl describe pod som-shop-a | sed -n '/^Events/,$p'
```

```text
pod/som-shop-a created
pod/som-shop-b created
NAME         READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
som-shop-a   0/2     Pending   0          3s    <none>   <none>   <none>           <none>
som-shop-b   0/2     Pending   0          3s    <none>   <none>   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  3s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

**ขั้นที่ 2:** ติดธงให้ทั้งสองลำ แล้วเฝ้าดูลำดับการเริ่ม (กด Ctrl+C เมื่อทั้งคู่ `2/2 Running`)

```bash
kubectl label node lab-worker lab-worker2 shop=open; kubectl get nodes -L shop
kubectl get pod -l app=som-shop -w
```

```text
node/lab-worker labeled
node/lab-worker2 labeled
NAME                STATUS   ROLES           AGE   VERSION   SHOP
lab-control-plane   Ready    control-plane   29m   v1.37.0   
lab-worker          Ready    <none>          28m   v1.37.0   open
lab-worker2         Ready    <none>          28m   v1.37.0   open
NAME         READY   STATUS     RESTARTS   AGE
som-shop-a   0/2     Init:0/3   0          3s
som-shop-b   0/2     Init:0/3   0          3s
som-shop-a   0/2     Init:1/3   0          8s
som-shop-b   0/2     Init:1/3   0          8s
som-shop-a   1/2     Init:1/3   0          8s
som-shop-b   1/2     Init:1/3   0          8s
som-shop-a   1/2     Init:2/3   0          8s
som-shop-b   1/2     Init:2/3   0          9s
som-shop-a   1/2     PodInitializing   0          9s
som-shop-a   1/2     Running           0          10s
som-shop-b   1/2     PodInitializing   0          10s
som-shop-b   1/2     Running           0          10s
som-shop-a   2/2     Running           0          11s
som-shop-b   2/2     Running           0          11s
```

(ผลจริงจากการทดสอบซ้ำ ตัดบรรทัดที่สถานะซ้ำกับบรรทัดก่อนหน้าออก คอลัมน์ AGE นับจากตอน apply ในขั้นที่ 1) ทั้งคู่เป็น `2/2 Running` ภายใน **ราว 8–12 วินาทีหลังติดธง** (รอบแรกวัดได้ภายใน 8 วินาที ผลการทดสอบซ้ำได้ `2/2 Running` ที่ AGE 11 วินาที) เร็วเพราะ image อยู่บน Node แล้ว

```bash
kubectl get pod -l app=som-shop -o wide -L branch
```

```text
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES   BRANCH
som-shop-a   2/2     Running   0          11s   10.244.1.23   lab-worker    <none>           <none>            a
som-shop-b   2/2     Running   0          11s   10.244.2.4    lab-worker2   <none>           <none>            b
```

> **scheduler อาจวางสาขาสลับเรือ:** กฎของเราบอกแค่ "คนละลำ" ไม่ได้บอกว่าสาขาไหนต้องอยู่ลำไหน ในการทดสอบซ้ำรอบหลัก a อยู่ `lab-worker` (10.244.1.24) และ b อยู่ `lab-worker2` (10.244.3.4) เหมือนตัวอย่าง แต่ตอนเปิดร้านใหม่อีกรอบหลังเก็บกวาด scheduler วาง **a บน `lab-worker2` และ b บน `lab-worker`** ถ้าของตัวเองสลับ ให้อ่านชื่อเรือในเอกสารสลับกัน และใช้ `NODE_A`/`NODE_B` ตามที่ 10.7 และ 10.9 คำนวณให้

### 10.4 ตรวจ Downward API

```bash
kubectl exec som-shop-a -c web -- printenv NODE_NAME SHOP_NAME POD_IP; kubectl exec som-shop-b -c web -- printenv NODE_NAME SHOP_NAME POD_IP
kubectl get pod -l app=som-shop -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,IP:.status.podIP
kubectl exec som-shop-a -c web -- wget -qO- http://127.0.0.1:3000/api/health; echo
```

```text
lab-worker
ร้านอาหารแมวน้องส้ม สาขา lab-worker
10.244.1.23
lab-worker2
ร้านอาหารแมวน้องส้ม สาขา lab-worker2
10.244.2.4
NAME         NODE          IP
som-shop-a   lab-worker    10.244.1.23
som-shop-b   lab-worker2   10.244.2.4
{"ok":true,"db":"up"}
```

### 10.5 ทดลองสาขาที่ 3

<p align="center" id="fig-17">
  <img src="images/17-lab10-anti-affinity-pending.png" alt="รูปที่ 17 สาขาที่ 3 Pending" width="900"><br>
  <em><b>รูปที่ 17</b> ทดลองสาขาที่ 3 som-shop-c: มีเรือติดธง shop=open แค่ 2 ลำและทั้งสองลำมีสาขาแล้ว จึง Pending</em>
</p>

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-c.yaml; sleep 3; kubectl get pod -l app=som-shop -o wide
kubectl describe pod som-shop-c | sed -n '/^Events/,$p'
```

```text
pod/som-shop-c created
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          32s   10.244.1.23   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          32s   10.244.2.4    lab-worker2   <none>           <none>
som-shop-c   0/2     Pending   0          3s    <none>        <none>        <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  4s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

สังเกตว่า control-plane ถูกนับเป็น `untolerated taint(s)` (เหตุผลแรกที่ตก) ไม่ใช่ "ไม่มีธง shop" เพราะแต่ละ Node ถูกนับในเหตุผลเดียว ลบสาขา c ทิ้ง

```bash
kubectl delete -f som-shop-branches/k8s/som-shop-c.yaml; kubectl get pod -l app=som-shop
```

```text
pod "som-shop-c" deleted from default namespace
NAME         READY   STATUS    RESTARTS   AGE
som-shop-a   2/2     Running   0          33s
som-shop-b   2/2     Running   0          33s
```

### 10.6 เปิดหน้าร้าน 2 สาขาใน browser

<p align="center" id="fig-18">
  <img src="images/18-lab10-two-tunnels.png" alt="รูปที่ 18 port-forward 2 ท่อ" width="900"><br>
  <em><b>รูปที่ 18</b> เปิดหน้าร้าน 2 สาขาด้วย kubectl port-forward คนละ port (3001, 3002) และ ssh -L สองชั้นจากเครื่องนักศึกษา</em>
</p>

**ขั้นที่ 1:** 🐧 **SSH session หลักของ k8s-lab** เปิด port-forward ทั้งสองสาขาไว้เบื้องหลัง (เก็บข้อความไว้ในไฟล์ log เพื่อดูภายหลังว่าท่อหลุดเมื่อไร)

```bash
kubectl port-forward pod/som-shop-a 3001:3000 > /tmp/pf-a.log 2>&1 &
kubectl port-forward pod/som-shop-b 3002:3000 > /tmp/pf-b.log 2>&1 &
sleep 2; cat /tmp/pf-a.log /tmp/pf-b.log
curl -s localhost:3001 | grep -o "<h1>[^<]*</h1>"; curl -s localhost:3002 | grep -o "<h1>[^<]*</h1>"
```

```text
Forwarding from 127.0.0.1:3001 -> 3000
Forwarding from 127.0.0.1:3002 -> 3000
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker2</h1>
```

(ในเครื่องที่รองรับ IPv6 อาจมีบรรทัด `Forwarding from [::1]:...` เพิ่ม ใช้ได้เหมือนกัน)

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ ต่อท่อ SSH สองท่อพร้อมกัน (ถ้ามีหน้าต่าง `ssh -L` จากบทที่ 2 ค้างอยู่ ให้ `exit` ก่อน)

```bash
ssh -p 2223 -L 3001:localhost:3001 -L 3002:localhost:3002 root@localhost
```

**ขั้นที่ 3:** 🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:3001** และ **http://localhost:3002** คนละแท็บ กดสั่งซื้อที่สาขาแรก 2 ครั้ง แล้วรีเฟรชทั้งสองแท็บ

<p align="center" id="fig-19">
  <img src="images/19-lab10-browser-branch-names.png" alt="รูปที่ 19 หน้าเว็บ 2 สาขา" width="900"><br>
  <em><b>รูปที่ 19</b> หน้าเว็บสองสาขาแสดงชื่อร้านพร้อมชื่อเรือจาก Downward API และออเดอร์ของแต่ละสาขาแยกกันเพราะฐานข้อมูลอยู่ใน Pod ของตัวเอง</em>
</p>

<p align="center" id="fig-20">
  <img src="images/screenshots/20261005_1728_lab003_01-branch-a-lab-worker2.png" alt="รูปที่ 20 ภาพหน้าจอจริง สาขา a บน lab-worker2" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: สาขา a (เปิดที่ http://localhost:3001) รอบที่ถ่ายภาพ scheduler วางไว้บนเรือ lab-worker2 หัวเว็บจึงแสดง "ร้านอาหารแมวน้องส้ม สาขา lab-worker2" ออเดอร์ทั้งหมด 2 ชิ้นที่ขายแล้ว 2 และ footer เสิร์ฟโดย Pod som-shop-a</em>
</p>

<p align="center" id="fig-21">
  <img src="images/screenshots/20261005_1728_lab003_02-branch-b-lab-worker.png" alt="รูปที่ 21 ภาพหน้าจอจริง สาขา b บน lab-worker" width="700"><br>
  <em><b>รูปที่ 21</b> ภาพหน้าจอจริงจากการทดลอง: สาขา b (เปิดที่ http://localhost:3002) บนเรือ lab-worker หัวเว็บแสดง "ร้านอาหารแมวน้องส้ม สาขา lab-worker" ออเดอร์ทั้งหมด 0 แม้สาขา a จะขายไปแล้ว เพราะแต่ละสาขามีฐานข้อมูลของตัวเอง footer เสิร์ฟโดย Pod som-shop-b<br>
  (หมายเหตุ: ทั้งสองสาขาตั้ง anti-affinity ไว้ จึงอยู่คนละเรือเสมอ แต่ scheduler อาจวาง a/b สลับเรือกับผลตัวอย่างด้านบนได้ ภาพชุดนี้ถ่ายผ่าน NodePort Service ที่เพิ่มเฉพาะเพื่อการถ่ายภาพ นักศึกษาใช้ port-forward ตามขั้นตอนเดิม)</em>
</p>

**(ทางเลือก) สั่งซื้อด้วย curl** 🐧 ใน k8s-lab ผลจริง

```bash
curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo
curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
```

หลังสั่งซื้อ กล่องสถิติของสาขา a คือ `2 ออเดอร์ทั้งหมด · 2 ชิ้นที่ขายแล้ว · 6 สินค้าในร้าน` และสินค้า id 1 เหลือ 18 ชิ้น ส่วนสาขา b ยังเป็น `0 · 0 · 6` และสินค้า id 1 ยังเหลือ 20 ชิ้น

### 10.7 ซ่อมเรือของสาขา a (drain)

<p align="center" id="fig-22">
  <img src="images/20-lab10-drain-branch-closed.png" alt="รูปที่ 22 drain เรือของสาขา a" width="900"><br>
  <em><b>รูปที่ 22</b> drain เรือของสาขา a: สาขา a ปิดและหายไป สาขา b ยังขายได้ เปิด a ใหม่ระหว่าง cordon จะ Pending จนกว่า uncordon</em>
</p>

**หาเรือของสาขา a จากของจริงเสมอ** (อย่าจำตามภาพ เพราะ scheduler อาจวางสลับกัน)

```bash
NODE_A=$(kubectl get pod som-shop-a -o jsonpath={.spec.nodeName}); echo NODE_A=$NODE_A
kubectl drain $NODE_A --ignore-daemonsets
```

```text
NODE_A=lab-worker
node/lab-worker cordoned
error: unable to drain node "lab-worker" due to error: cannot delete Pods with local storage (use --delete-emptydir-data to override): default/som-shop-a, continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete Pods with local storage (use --delete-emptydir-data to override): default/som-shop-a
```

สาขามีฐานข้อมูลใน emptyDir drain จึงขอให้ยืนยันว่ายอมให้ข้อมูลหาย (และสังเกตว่า Node ถูก cordon ไปแล้วแม้ error) ใส่ให้ครบ

```bash
time kubectl drain $NODE_A --ignore-daemonsets --delete-emptydir-data --force
kubectl get pod -l app=som-shop -o wide; kubectl get nodes
```

```text
node/lab-worker already cordoned
Warning: ignoring DaemonSet-managed Pods: kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl; deleting Pods that declare no controller: default/som-shop-a
evicting pod default/som-shop-a
pod/som-shop-a evicted
node/lab-worker drained

real	0m1.059s
NAME         READY   STATUS    RESTARTS   AGE    IP           NODE          NOMINATED NODE   READINESS GATES
som-shop-b   2/2     Running   0          119s   10.244.2.4   lab-worker2   <none>           <none>
NAME                STATUS                     ROLES           AGE   VERSION
lab-control-plane   Ready                      control-plane   31m   v1.37.0
lab-worker          Ready,SchedulingDisabled   <none>          30m   v1.37.0
lab-worker2         Ready                      <none>          30m   v1.37.0
```

(ลำดับสองส่วนในบรรทัด `Warning:` สลับกันได้ ผลการทดสอบซ้ำได้ `Warning: deleting Pods that declare no controller: default/som-shop-a; ignoring DaemonSet-managed Pods: kube-system/kindnet-ncp6g, kube-system/kube-proxy-fbkvb` และ `real	0m1.119s` ชื่อ Pod `kindnet-*`/`kube-proxy-*` ต่างกันในแต่ละคลัสเตอร์)

ดูผลต่อหน้าร้าน

```bash
curl -s -m 5 localhost:3001 >/dev/null; echo "curl 3001 exit=$?"
curl -s localhost:3002 | grep -o "<h1>[^<]*</h1>"
tail -3 /tmp/pf-a.log
```

```text
curl 3001 exit=52
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker2</h1>
Handling connection for 3001
E1004 19:24:06.053551   56187 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod ec253c7d3678b25fd2e8d10064013265a7b3ff87384fee4101b22f22294a7289, uid : network namespace for sandbox \"ec253c7d3678b25fd2e8d10064013265a7b3ff87384fee4101b22f22294a7289\" is closed" localPort=3001 remotePort=3000
error: lost connection to pod
```

🌐 แท็บ `localhost:3001` เปิดไม่ได้แล้ว ส่วนแท็บ `localhost:3002` ยังขายได้ปกติ

### 10.8 เปิดสาขา a ใหม่ระหว่างเรือยังอยู่ในอู่

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-a.yaml; sleep 3; kubectl get pod -l app=som-shop -o wide
kubectl describe pod som-shop-a | sed -n '/^Events/,$p'
```

```text
pod/som-shop-a created
NAME         READY   STATUS    RESTARTS   AGE     IP           NODE          NOMINATED NODE   READINESS GATES
som-shop-a   0/2     Pending   0          3s      <none>       <none>        <none>           <none>
som-shop-b   2/2     Running   0          2m40s   10.244.2.4   lab-worker2   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  3s    default-scheduler  0/3 nodes are available: 1 node(s) didn't match pod anti-affinity rules, 1 node(s) had untolerated taint(s), 1 node(s) were unschedulable. preemption: 0/3 nodes are available: 1 No preemption victims found for incoming pod, 2 Preemption is not helpful for scheduling.
```

ซ่อมเสร็จ เอาเชือกออก แล้วเปิดท่อใหม่ (ท่อเก่าตายไปพร้อม Pod เดิม)

```bash
kubectl uncordon $NODE_A; kubectl wait --for=condition=Ready pod/som-shop-a --timeout=120s; kubectl get pod -l app=som-shop -o wide; kubectl get nodes
kubectl port-forward pod/som-shop-a 3001:3000 > /tmp/pf-a.log 2>&1 &
sleep 2; curl -s localhost:3001 | grep -oE "<h1>[^<]*</h1>|<span class=\"num\">[^<]*</span><span class=\"label\">ออเดอร์ทั้งหมด"
```

```text
node/lab-worker uncordoned
pod/som-shop-a condition met
NAME         READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          10s     10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          2m47s   10.244.2.4    lab-worker2   <none>           <none>
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   31m   v1.37.0
lab-worker          Ready    <none>          31m   v1.37.0
lab-worker2         Ready    <none>          31m   v1.37.0
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
<span class="num">0</span><span class="label">ออเดอร์ทั้งหมด
```

(ในการทดลอง `som-shop-a` Ready ภายใน 7 วินาทีหลัง uncordon ผลการทดสอบซ้ำราว 8 วินาที) 🌐 รีเฟรชแท็บ `localhost:3001` จะเห็นร้านกลับมา แต่ **ออเดอร์เป็น 0** และ IP ใหม่ เพราะเป็น Pod ใหม่ที่มี emptyDir ใหม่

### 10.9 เรือของสาขา b หายในหมอก

<p align="center" id="fig-23">
  <img src="images/21-lab10-fog-branch-lost.png" alt="รูปที่ 23 เรือของสาขา b หายในหมอก" width="900"><br>
  <em><b>รูปที่ 23</b> เรือ lab-worker2 หายในหมอก (docker stop): สาขา b ถูกไล่ออกหลัง NotReady 60 วินาที สาขา a ยังขายได้ แต่ไม่มีใครเปิดสาขาใหม่ให้</em>
</p>

> ⚠️ 🐧 รันใน **SSH session ของ k8s-lab** และตรวจให้แน่ใจว่า `NODE_B` เป็น `lab-worker` หรือ `lab-worker2` เท่านั้น (ห้ามเป็น `lab-control-plane`)

```bash
NODE_B=$(kubectl get pod som-shop-b -o jsonpath={.spec.nodeName}); echo NODE_B=$NODE_B; date +%T; docker stop $NODE_B
```

```text
NODE_B=lab-worker2
19:25:15
lab-worker2
```

ทันทีหลังหยุดเรือ

```bash
curl -s -m 5 localhost:3002 >/dev/null; echo "curl 3002 exit=$?"; tail -2 /tmp/pf-b.log
curl -s -m 5 localhost:3001 | grep -o "<h1>[^<]*</h1>"
```

```text
curl 3002 exit=7
Handling connection for 3002
error: lost connection to pod
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
```

รอ ~45–55 วินาที (จนเรือเป็น `NotReady` ผลการทดสอบซ้ำได้ 47 วินาที) แล้วดูสถานะ และลองสั่งซื้อที่สาขา a ระหว่างเรือ b ล่ม

```bash
kubectl get nodes; kubectl get pod -l app=som-shop -o wide
curl -s -X POST localhost:3001/api/orders -H "Content-Type: application/json" -d '{"product_id":2,"qty":2}'; echo
```

```text
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   33m   v1.37.0
lab-worker          Ready      <none>          33m   v1.37.0
lab-worker2         NotReady   <none>          33m   v1.37.0
NAME         READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          95s     10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          4m12s   10.244.2.4    lab-worker2   <none>           <none>
{"ok":true,"order_id":1,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":13}}
```

ภาพหน้าจอจริงช่วงนี้ (ถ่ายจากการทดลองอีกรอบหนึ่งซึ่งสาขา a มี 2 ออเดอร์อยู่ก่อน แล้ว `docker stop lab-worker2` ซึ่ง Node เป็น NotReady หลัง 51 วินาที)

<p align="center" id="fig-24">
  <img src="images/screenshots/20261004_1940_lab10_03-branch-a-still-selling-while-worker2-down.png" alt="รูปที่ 24 ภาพหน้าจอจริง สาขา a ยังขายได้" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: ระหว่างที่ lab-worker2 ถูก docker stop และเป็น NotReady สาขา a บน lab-worker ยังรับออเดอร์ได้ ออเดอร์ทั้งหมดเพิ่มเป็น 3</em>
</p>

<p align="center" id="fig-25">
  <img src="images/screenshots/20261004_1940_lab10_04-branch-b-unreachable.png" alt="รูปที่ 25 ภาพหน้าจอจริง สาขา b เปิดไม่ได้" width="700"><br>
  <em><b>รูปที่ 25</b> ภาพหน้าจอจริงจากการทดลอง: browser เปิด http://localhost:3002 (สาขา b) ไม่ได้ ขึ้น ERR_CONNECTION_RESET เพราะ port-forward ไปยัง Pod บนเรือที่ล่มหลุดไปแล้ว</em>
</p>

รอต่ออีกราว 60 วินาทีหลัง NotReady (บัตรผ่าน `tolerationSeconds: 60`) แล้วลองช่วยสาขา b

```bash
kubectl get pod -l app=som-shop -o wide
time timeout 40 kubectl port-forward pod/som-shop-b 3002:3000; echo "exit=$?"
kubectl apply -f som-shop-branches/k8s/som-shop-b.yaml
kubectl delete pod som-shop-b --wait=false; kubectl get pod som-shop-b
kubectl get events --field-selector involvedObject.name=som-shop-b | tail -4
```

```text
NAME         READY   STATUS        RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running       0          2m37s   10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Terminating   0          5m14s   10.244.2.4    lab-worker2   <none>           <none>
error: error upgrading connection: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host

real	0m6.174s
exit=1
pod/som-shop-b configured
Warning: Detected changes to resource som-shop-b which is currently being deleted.
pod "som-shop-b" deleted from default namespace
NAME         READY   STATUS        RESTARTS   AGE
som-shop-b   2/2     Terminating   0          5m20s
5m11s       Normal    Started                pod/som-shop-b   Container started
5m11s       Warning   Unhealthy              pod/som-shop-b   Readiness probe failed: Get "http://10.244.2.4:3000/api/health": dial tcp 10.244.2.4:3000: connect: connection refused
89s         Warning   NodeNotReady           pod/som-shop-b   Node is not ready
29s         Normal    TaintManagerEviction   pod/som-shop-b   Marking for deletion Pod default/som-shop-b
```

(Event `Unhealthy` ตอนอายุ 5m11s เป็นของช่วงเปิดร้านใหม่ ๆ ที่เว็บยังไม่พร้อม เป็นเรื่องปกติจากบทที่ 2)

> **IP ใน `dial tcp ...:10250` คือ IP ของเรือ `NODE_B` ในเครื่องตัวเอง** และ IP ของ Pod ขึ้นกับ Pod CIDR ของเรือลำนั้น ผลการทดสอบซ้ำ `lab-worker2` คือ `172.19.0.4` และ Pod บนเรือได้ `10.244.3.x` และบรรทัด `Warning: Detected changes ...` อาจขึ้น **ก่อน** `pod/som-shop-b configured` ก็ได้ (ข้อความ Warning ออกทาง stderr ลำดับบนจอจึงไม่ตายตัว) ผลการทดสอบซ้ำ (b ถูกไล่ที่ NotReady + 59 วินาที = +106 วินาทีจาก `docker stop`)
>
> ```text
> NAME         READY   STATUS        RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
> som-shop-a   2/2     Running       0          2m      10.244.1.25   lab-worker    <none>           <none>
> som-shop-b   2/2     Terminating   0          3m11s   10.244.3.4    lab-worker2   <none>           <none>
> error: error upgrading connection: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.4:10250: connect: no route to host
>
> real	0m6.194s
> exit=1
> Warning: Detected changes to resource som-shop-b which is currently being deleted.
> pod/som-shop-b configured
> pod "som-shop-b" deleted from default namespace
> NAME         READY   STATUS        RESTARTS   AGE
> som-shop-b   2/2     Terminating   0          3m18s
> 3m8s        Normal    Started                pod/som-shop-b   Container started
> 3m8s        Warning   Unhealthy              pod/som-shop-b   Readiness probe failed: Get "http://10.244.3.4:3000/api/health": dial tcp 10.244.3.4:3000: connect: connection refused
> 67s         Warning   NodeNotReady           pod/som-shop-b   Node is not ready
> 7s          Normal    TaintManagerEviction   pod/som-shop-b   Marking for deletion Pod default/som-shop-b
> ```

ไทม์ไลน์จริงจากสคริปต์เฝ้าดู (T0 = `docker stop` ตัดบางบรรทัดและคอลัมน์ท้าย)

```text
19:25:15 +0s node=Ready Ready=True taints=[] pods: som-shop-a=Running som-shop-b=Running
19:25:57 +40s node=Ready Ready=True taints=[] pods: som-shop-a=Running som-shop-b=Running
19:25:59 +43s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Running
19:26:58 +102s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Running
19:27:00 +104s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Terminating
...
19:27:48 +152s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Terminating
```

ไทม์ไลน์ของการทดสอบซ้ำ (ลูปตรวจทุก ~2 วินาที จึงช้ากว่าค่าที่วัดตรง ๆ ได้ 1–2 วินาที: NotReady วัดได้ 47 วินาที, b ถูกไล่ที่ +106 วินาที)

```text
17:19:21 +0s Ready taints=[] | som-shop-a=Running som-shop-b=Running 
17:20:08 +47s Ready taints=[] | som-shop-a=Running som-shop-b=Running 
17:20:10 +49s NotReady taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] | som-shop-a=Running som-shop-b=Running 
17:21:07 +106s NotReady taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] | som-shop-a=Running som-shop-b=Running 
17:21:09 +108s NotReady taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] | som-shop-a=Running som-shop-b=Terminating 
```

ตอนนี้ร้านน้องส้มเหลือสาขาเดียว และ **ไม่มีใครเปิดสาขา b ใหม่บนเรือที่ยังดีให้** (ถึงจะมีเรือ `lab-worker` ว่างอยู่ ก็ติดกฎ anti-affinity กับสาขา a และไม่มีใครสร้าง Pod ใหม่ให้อยู่ดี)

### 10.10 เรือกลับมา

```bash
docker start $NODE_B; T0=$(date +%s); until kubectl get node $NODE_B --no-headers | grep -q " Ready "; do sleep 1; done; echo "$NODE_B Ready หลัง docker start $(( $(date +%s) - T0 )) วินาที"; while kubectl get pod som-shop-b >/dev/null 2>&1; do sleep 1; done; echo "som-shop-b หายจริงหลัง docker start $(( $(date +%s) - T0 )) วินาที"; kubectl get nodes; kubectl get pod -l app=som-shop -o wide
```

```text
lab-worker2
lab-worker2 Ready หลัง docker start 2 วินาที
som-shop-b หายจริงหลัง docker start 5 วินาที
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   34m   v1.37.0
lab-worker          Ready    <none>          34m   v1.37.0
lab-worker2         Ready    <none>          34m   v1.37.0
NAME         READY   STATUS    RESTARTS   AGE    IP            NODE         NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          3m8s   10.244.1.24   lab-worker   <none>           <none>
```

(ผลการทดสอบซ้ำ: Ready หลัง `docker start` 2 วินาที และ `som-shop-b หายจริงหลัง docker start 4 วินาที` ตัวเลขนี้แกว่งได้ราว 4–5 วินาที)

ตรวจเรือที่กลับมา (taint หาย, Pod ระบบกลับมา, image ยังอยู่บนเรือ)

```bash
kubectl get node $NODE_B -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key
kubectl get pod -n kube-system -o wide --field-selector spec.nodeName=$NODE_B
docker exec $NODE_B crictl images | grep -E "som-shop|postgres"
```

```text
NAME          TAINTS
lab-worker2   <none>
NAME               READY   STATUS    RESTARTS      AGE   IP           NODE          NOMINATED NODE   READINESS GATES
kindnet-68hkk      1/1     Running   3 (30s ago)   35m   172.19.0.2   lab-worker2   <none>           <none>
kube-proxy-7k6xk   1/1     Running   3 (30s ago)   35m   172.19.0.2   lab-worker2   <none>           <none>
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  b95826bfd89f2       76.6MB
```

(RESTARTS ของ `kindnet`/`kube-proxy` สะสมทุกครั้งที่หยุด/เริ่มเรือ ในตัวอย่างเป็น 3 เพราะผ่าน LAB 8 มาแล้ว ผลการทดสอบซ้ำก็ได้ 3 เช่นกัน ส่วน IP ของเรือ (ผลการทดสอบซ้ำ `172.19.0.4`), ชื่อ Pod ระบบ และ image ID ของ `som-shop-web` จะเป็นค่าของเครื่องตัวเอง) เปิดสาขา b ใหม่เอง

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-b.yaml && kubectl wait --for=condition=Ready pod/som-shop-b --timeout=120s; kubectl get pod -l app=som-shop -o wide
kubectl port-forward pod/som-shop-b 3002:3000 > /tmp/pf-b.log 2>&1 &
sleep 2; for p in 3001 3002; do curl -s localhost:$p | grep -oE "<h1>[^<]*</h1>|<span class=\"num\">[^<]*</span><span class=\"label\">ออเดอร์ทั้งหมด"; done
```

```text
pod/som-shop-b created
pod/som-shop-b condition met
NAME         READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          3m41s   10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          7s      10.244.2.2    lab-worker2   <none>           <none>
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
<span class="num">1</span><span class="label">ออเดอร์ทั้งหมด
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker2</h1>
<span class="num">0</span><span class="label">ออเดอร์ทั้งหมด
```

🌐 รีเฟรชทั้งสองแท็บ ร้านกลับมาครบ 2 สาขา (สาขา a มี 1 ออเดอร์ที่สั่งระหว่างเรือ b ล่ม สาขา b เริ่มที่ 0 ใหม่)

**(ทางเลือก) ดูทรัพยากรที่สาขาหนึ่งจอง**

```bash
kubectl describe node lab-worker | sed -n '/Allocated resources/,/^Events/p' | head -6
docker stats --no-stream --format "{{.Name}} {{.MemUsage}}"
```

```text
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                300m (0%)   1 (3%)
  memory             498Mi (0%)  1Gi (1%)
lab-worker 391.4MiB / 61.5GiB
lab-worker2 206.1MiB / 61.5GiB
lab-control-plane 758.3MiB / 61.5GiB
```

(1 สาขาจอง 200m/448Mi บวกกับ `kindnet` 100m/50Mi = 300m/498Mi ตามที่คำนวณในทฤษฎีหัวข้อ 5)

### สิ่งที่เห็นใน LAB 10

| ขั้น | ผลจริง |
|---|---|
| ก่อนติดธง | ทั้งสองสาขา Pending `didn't match Pod's node affinity/selector` |
| ติดธง `shop=open` | ถูกวางเองทันที `2/2 Running` บนเรือคนละลำ ภายในราว 8–12 วินาที (scheduler อาจวาง a/b สลับเรือกับตัวอย่าง) |
| Downward API | `SHOP_NAME=ร้านอาหารแมวน้องส้ม สาขา lab-worker` / `... lab-worker2` หน้าเว็บและชื่อแท็บแสดงชื่อสาขา |
| สาขาที่ 3 | Pending `2 node(s) didn't match pod anti-affinity rules` |
| ออเดอร์ | แต่ละสาขานับแยกกัน (a = 2, b = 0) เพราะ emptyDir แยก |
| drain เรือของ a | ต้องใส่ `--delete-emptydir-data` และ `--force`, สาขา a หายใน ~1–2 วินาที, port-forward `lost connection to pod`, สาขา b ขายต่อ, ไม่มีใครเปิด a ใหม่ |
| เปิด a ใหม่ระหว่าง cordon | Pending มีเหตุผล `node(s) were unschedulable` ครบ → uncordon แล้ว Running ใน ~7–8 วินาที ออเดอร์เริ่มที่ 0 |
| เรือของ b ล่ม | port-forward หลุดทันที, NotReady ~43–55 วินาที (ผลการทดสอบซ้ำ 47), สาขา a ขายได้ตลอด, b ถูกไล่ที่ NotReady + ~60 วินาที (วัดได้ 59–61) แล้วค้าง Terminating, apply ซ้ำได้แค่ Warning |
| เรือกลับ | Ready ใน 2 วินาที, b หายจริงใน 4–5 วินาที, ต้อง apply b ใหม่เอง ข้อมูลเริ่มใหม่ |

### 10.11 เก็บกวาด LAB 10

1. 🖥️ หน้าต่าง `ssh -L 3001 ... 3002`: พิมพ์ `exit`
2. 🐧 SSH session หลักของ k8s-lab: หยุด port-forward ลบทุกสาขา และ **ลบธง `shop`** ตรวจว่าไม่มี Node ใดเป็น `SchedulingDisabled` หรือ `NotReady`

```bash
pkill -f "[k]ubectl port-forward pod/som-shop"
kubectl delete pod -l app=som-shop
kubectl label node lab-worker lab-worker2 shop-
kubectl get nodes -L shop; kubectl get pod
pgrep -af "[k]ubectl port-forward" || echo "(ไม่มี port-forward ค้าง)"
```

```text
pod "som-shop-a" deleted from default namespace
pod "som-shop-b" deleted from default namespace
node/lab-worker unlabeled
node/lab-worker2 unlabeled
NAME                STATUS   ROLES           AGE   VERSION   SHOP
lab-control-plane   Ready    control-plane   36m   v1.37.0   
lab-worker          Ready    <none>          36m   v1.37.0   
lab-worker2         Ready    <none>          36m   v1.37.0   
No resources found in default namespace.
```

(pattern `[k]ubectl` ใช้กัน `pkill`/`pgrep` ไปตรงกับ command line ของตัวเอง บรรทัดสุดท้ายควรได้ `(ไม่มี port-forward ค้าง)`)

### 10.12 ปูทางบทหน้า: ทำไมร้านจริงไม่ทำแบบนี้

<p align="center" id="fig-26">
  <img src="images/22-lab10-next-deployment-service.png" alt="รูปที่ 26 ปูทางบทหน้า" width="900"><br>
  <em><b>รูปที่ 26</b> ปิดท้าย: ถ้าอยากให้มีคนเปิดสาขาใหม่อัตโนมัติและมีที่อยู่เดียวสำหรับลูกค้า ต้องใช้ Deployment และ Service ในบทหน้า</em>
</p>

สิ่งที่น้องส้มเจอใน LAB นี้คือปัญหาจริงของ Pod เดี่ยว

| ปัญหาที่เห็นใน LAB 10 | สิ่งที่บทหน้าจะใช้แก้ |
|---|---|
| drain/เรือล่มแล้วสาขาหาย **ไม่มีใครเปิดใหม่** ต้อง `kubectl apply` เอง | **Deployment** กำหนด "ต้องการ 2 สาขา" แล้ว controller สร้าง Pod ใหม่ให้เองบนเรือที่ยังดี |
| ต้องก๊อปปี้ YAML เป็น a, b, c | Pod template เดียวใน Deployment ใส่ affinity/anti-affinity/toleration ที่เรียนในบทนี้ได้เหมือนเดิม |
| ลูกค้าต้องจำ 2 port (3001, 3002) และ port-forward หลุดทุกครั้งที่ Pod หาย | **Service** ที่อยู่เดียวคงที่ กระจายลูกค้าไปทุกสาขาที่พร้อม |
| ออเดอร์แต่ละสาขาแยกกันและหายเมื่อ Pod หาย | ฐานข้อมูลกลาง + ที่เก็บข้อมูลถาวร (PersistentVolumeClaim) |

### คำถามท้าย LAB 10

1. ทำไม `som-shop-c` จึง Pending และข้อความ FailedScheduling นับ control-plane เป็น "untolerated taint" แทน "ไม่มีธง shop"
2. ถ้าลบ `podAntiAffinity` ออกจากทั้ง 3 ไฟล์แล้ว apply ใหม่ทั้ง 3 สาขา ผลการจัดวางจะเป็นอย่างไร และร้านจะเสี่ยงอะไรเพิ่มขึ้น
3. ตอน drain เรือของสาขา a ทำไมต้องใส่ `--delete-emptydir-data` และข้อมูลออเดอร์ของสาขา a หายไปไหน
4. ทำไม `som-shop-a` ที่ apply ใหม่ระหว่าง cordon จึง Pending ทั้งที่ `lab-worker` ยัง `Ready` อยู่ อ่านเหตุผลจากข้อความ FailedScheduling ให้ครบทั้ง 3 Node
5. หลัง `docker stop` ทำไมหน้า 3002 เปิดไม่ได้ **ทันที** ทั้งที่ Node ยังแสดง `Ready` อีกราว 45–55 วินาที และทำไม `som-shop-b` ถูกไล่ที่ราว 100–110 วินาที (NotReady ~45–55 วินาที + 60) หลัง stop ไม่ใช่ 60 วินาที

> **🏆 ท้าทาย:** แก้ toleration ของ `som-shop-b.yaml` ให้ไม่มี `tolerationSeconds` (อยู่ต่อได้ตลอดเมื่อเรือล่ม) แล้วทำขั้น 10.9 ซ้ำ บันทึกว่าเกิดอะไรขึ้นกับสาขา b และอธิบายว่าในงานจริงตัวเลือกนี้ดีหรือไม่ดีอย่างไร

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-branches/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 003_kubernetes_node_pod k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/003_kubernetes_node_pod/02_LAB` (ตรวจด้วย `pwd`) |
| `docker stop lab-worker2` ได้ `Error response from daemon: No such container: lab-worker2` | พิมพ์บน **เครื่องตัวเอง** ไม่ใช่ใน k8s-lab | 🐧 พิมพ์ใน SSH session ของ k8s-lab (`ssh -p 2223 root@localhost`) |
| `kubectl get nodes` ได้ `The connection to the server localhost:8080 was refused - did you specify the right host or port?` (มีบรรทัด `memcache.go ... connection refused` นำหน้า) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ แล้วถ้าจะทำ LAB 10 ต้อง build/`kind load` image ใหม่ |
| Pod ค้าง `Pending` | กฎจัดวางไม่มี Node ใดผ่าน | อ่าน `kubectl describe pod <ชื่อ> \| sed -n '/^Events/,$p'` แล้วดูตาราง "ข้อความ FailedScheduling" ในทฤษฎีหัวข้อ 4.3 ตรวจ label (`kubectl get nodes -L ...`), taint (`custom-columns` แบบ LAB 0) และ cordon (`kubectl get nodes`) |
| LAB ถัดไปผลไม่ตรงเอกสาร (เช่น Pod ไปลงแต่ `lab-worker2` หรือ Pending แปลก ๆ) | ลืมเก็บกวาด label/taint/cordon จาก LAB ก่อน | ทำ [ตารางคืนสภาพคลัสเตอร์](#ตารางคืนสภาพคลัสเตอร์) |
| `error: 'fleet' already has a value (fast), and --overwrite is false` | เปลี่ยนค่า label ที่มีอยู่แล้ว | ใส่ `--overwrite` |
| drain ขึ้น `cannot delete Pods that declare no controller` / `with local storage` / `DaemonSet-managed Pods` | ด่านป้องกันของ drain | ใส่ `--force` / `--delete-emptydir-data` / `--ignore-daemonsets` ตามข้อความ แล้ว **อย่าลืม `kubectl uncordon`** |
| Node ค้าง `Ready,SchedulingDisabled` | drain (แม้ error) หรือ cordon แล้วลืม uncordon | `kubectl uncordon <ชื่อ node>` |
| `lab-worker2` ค้าง `NotReady` | ลืม `docker start lab-worker2` หลัง LAB 8/10 | 🐧 `docker ps -a` ดูสถานะ แล้ว `docker start lab-worker2` รอ `kubectl get nodes` (ปกติ Ready ใน 2 วินาที) ถ้าไม่กลับภายใน 2 นาที ใช้แผนสำรอง `k8s-down && k8s-up` แล้ว load image ใหม่ |
| Pod ค้าง `Terminating` นาน | Pod อยู่บนเรือที่ล่ม kubelet ยืนยันการลบไม่ได้ | ปกติ จะหายเองภายในไม่กี่วินาทีหลัง `docker start` |
| `kubectl exec/logs/port-forward` ได้ `dial tcp 172.19.0.x:10250: connect: no route to host` หรือ `timeout 15 kubectl exec ...` ค้างแล้วได้ `exit=124` โดยไม่มีข้อความ | Pod อยู่บนเรือที่ล่ม | ปกติระหว่าง LAB 8/10 รอเรือกลับ (IP `172.19.0.x` คือ IP ของเรือในเครื่องตัวเอง) |
| `kubectl delete pod static-snack-lab-worker` ค้างราว 1 นาที แล้ว Pod กลับมาอีก | เป็น mirror pod ของ static Pod | ใช้ `--wait=false` หรือ Ctrl+C และลบไฟล์บนเรือ `docker exec lab-worker rm /etc/kubernetes/manifests/static-snack.yaml` |
| `spread-3`/`spread-4` Pending ทั้งที่ worker ว่าง | `nodeTaintsPolicy` ค่าเริ่มต้นเป็น `Ignore` นับ control-plane | เป็นผลที่ตั้งใจใน LAB 5 ใช้ `nodeTaintsPolicy: Honor` |
| `som-shop-*` ค้าง `Init:ErrImagePull` / `ImagePullBackOff` | ไม่มี image บน Node (สร้างคลัสเตอร์ใหม่แต่ยังไม่ `kind load`) | ทำ 10.2 แล้ว `kubectl delete pod -l app=som-shop` และ apply ใหม่ |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` (ARM ใช้ `linux/arm64`) |
| `kubectl port-forward` แจ้ง `address already in use` | port-forward ตัวเก่ายังค้าง | `pgrep -af "[k]ubectl port-forward"` แล้ว `pkill -f "[k]ubectl port-forward pod/som-shop"` |
| browser เปิด `localhost:3001`/`3002` ไม่ได้ (`ERR_CONNECTION_RESET`/refused) | หน้าต่าง `ssh -L` ถูกปิด หรือ port-forward หลุดเพราะ Pod ถูกลบ/เรือล่ม | ดู `cat /tmp/pf-a.log` ถ้ามี `lost connection to pod` ให้เปิด port-forward ใหม่หลังมี Pod ใหม่ |
| `ssh -L` แจ้งว่า bind port ไม่ได้ | port 3001/3002 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ | เปลี่ยนเลขซ้ายของ `-L` เช่น `-L 13001:localhost:3001` แล้วเปิด `http://localhost:13001` |
| หน้าเว็บ footer เขียน `Kubernetes LAB 002` | ใช้แอปเดิมจากบทที่ 2 โดยไม่แก้โค้ด | ไม่ใช่ข้อผิดพลาด |
| scheduler วางสาขาสลับกับในเอกสาร (a อยู่ `lab-worker2`) | scheduler เลือกเอง เรากำหนดแค่ "คนละลำ" | ใช้ `NODE_A`/`NODE_B` จาก `kubectl get pod ... -o jsonpath={.spec.nodeName}` ทุกครั้ง |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes -o wide`, ผล capacity/allocatable และ `docker exec lab-worker crictl ps`
- [ ] **LAB 1** Events `FailedScheduling ... Insufficient memory` ของ `huge-pod` และ `Allocated resources` หลังวาง `fit-pod`
- [ ] **LAB 2** `kubectl get pod -o wide` ที่ `pinned-pod` อยู่บน `lab-control-plane` และ `kubectl logs whereami`
- [ ] **LAB 3** Events ของ `selector-pod` ที่มีทั้ง `FailedScheduling` และ `Scheduled` และผล `prefer-*` เมื่อไม่มีเรือ fast
- [ ] **LAB 4** `crew-3` Pending พร้อมข้อความ `didn't match pod anti-affinity rules`
- [ ] **LAB 5** ตารางเปรียบเทียบ `spread-*` (Pending 2 ตัว) กับ `honor-*` (2 : 2)
- [ ] **LAB 6** Events `TaintManagerEviction` ของ `no-pass` และ `pass-30s`
- [ ] **LAB 7** ผล drain ที่สำเร็จ (`node/lab-worker drained`) และ `kubectl get pod -o wide` หลัง drain
- [ ] **LAB 8** `describe node lab-worker2` ที่ condition เป็น `Unknown` พร้อม taint `unreachable` และ `fog-*` ค้าง `Terminating`
- [ ] **LAB 9** annotation `kubernetes.io/config.mirror` และ ownerReferences `kind: Node` ของ `static-snack-lab-worker`
- [ ] **LAB 10** (1) `kubectl get pod -l app=som-shop -o wide` 2 สาขาคนละ NODE (2) browser 2 แท็บแสดงชื่อสาขาต่างกันและออเดอร์แยก (3) FailedScheduling ของ `som-shop-c` (4) ผล drain และ `som-shop-a` Pending ระหว่าง cordon (5) `lab-worker2 NotReady` + `som-shop-b Terminating` ขณะสาขา a ยังรับออเดอร์ได้
- [ ] ท้ายสุด `kubectl get pods` ได้ `No resources found in default namespace.`, Node ทั้ง 3 `Ready` ไม่มี `SchedulingDisabled` และไม่มี label/taint ที่เราติดค้าง

---

## ตารางคืนสภาพคลัสเตอร์

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Pod ของ LAB | 1–8 | `kubectl get pod -l lab=03` | `kubectl delete pod -l lab=03 --now` |
| label `fleet`, `deck` | 3 | `kubectl get nodes -L fleet,deck` | `kubectl label node lab-worker lab-worker2 fleet- deck-` |
| taint `dedicated`, `maintenance` | 6 | `kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key` (ต้องเหลือแค่ของ control-plane) | `kubectl taint node lab-worker2 maintenance=true:NoExecute- dedicated=vip:NoSchedule-` |
| Node ถูก cordon | 7, 10 | `kubectl get nodes` (ไม่มี `SchedulingDisabled`) | `kubectl uncordon lab-worker` (หรือ `lab-worker2`) |
| เรือ `lab-worker2` หยุดอยู่ | 8, 10 | `docker ps -a --format '{{.Names}}\t{{.Status}}'` และ `kubectl get nodes` | `docker start lab-worker2` แล้วรอ `Ready` |
| ไฟล์ static Pod บนเรือ | 9 | `docker exec lab-worker ls /etc/kubernetes/manifests` (ต้องว่าง) | `docker exec lab-worker rm -f /etc/kubernetes/manifests/static-snack.yaml` |
| สาขาร้าน | 10 | `kubectl get pod -l app=som-shop` | `kubectl delete pod -l app=som-shop` |
| label `shop` | 10 | `kubectl get nodes -L shop` | `kubectl label node lab-worker lab-worker2 shop-` |
| port-forward ค้าง | 10 | `pgrep -af "[k]ubectl port-forward"` | `pkill -f "[k]ubectl port-forward pod/som-shop"` |

ตอนลบ label/taint ที่ไม่มีอยู่แล้ว kubectl อาจแจ้งว่า `not found` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get pods
kubectl get nodes -L fleet,deck,shop
kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key
docker exec lab-worker ls /etc/kubernetes/manifests
pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
```

ผลที่ถูกต้อง: ไม่มี Pod ใน default namespace, Node ทั้ง 3 `Ready` ไม่มีคอลัมน์ `FLEET/DECK/SHOP` ที่มีค่า, taint เหลือเฉพาะ `node-role.kubernetes.io/control-plane` บน `lab-control-plane`, โฟลเดอร์ manifests ของ `lab-worker` ว่าง และไม่มี port-forward ค้าง

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ `kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

> **บทถัดไป:** น้องส้มจะเลิกก๊อปปี้ YAML ทีละสาขา ให้ Deployment ดูแลจำนวนสาขาและเปิดสาขาใหม่เองเมื่อเรือล่ม ใช้ Service เป็นที่อยู่เดียวของร้าน และนำกฎ affinity/anti-affinity/toleration ที่เรียนในบทนี้ไปใส่ใน Pod template
