# LAB บทที่ 3: Node กับ Pod — จัดวาง Pod บนกองเรือ สู่ร้านน้องส้มหลายสาขา

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Node และการจัดวาง Pod — สำรวจ Node, Pending/FailedScheduling, nodeName, Downward API, nodeSelector, node affinity, pod affinity/anti-affinity, topology spread, taints/tolerations, cordon/drain, Node ล่ม, static Pod และร้านอาหารแมวน้องส้ม 2 สาขาบนเรือคนละลำ
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่อยากขยายร้านเป็นหลายสาขา เริ่มจากสำรวจกองเรือ ดูว่าเจ้าหน้าที่จัดตู้ (kube-scheduler) ตัดสินใจอย่างไร ทดลองบอกทางด้วยธงเรือ แม่เหล็ก ป้ายห้ามขึ้นและบัตรผ่าน ซ่อมเรือด้วย cordon/drain จำลอง **เรือล่ม** ด้วย `docker stop` แล้วปิดท้ายด้วยการเปิด **ร้านอาหารแมวน้องส้ม 2 สาขาบนเรือคนละลำ** ที่ชื่อร้านบอกได้เองว่าอยู่บนเรือลำไหน

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, kind v0.33.0, Kubernetes v1.37.0) เมื่อ 4 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, CPU/RAM ของ Node และ Node ที่ scheduler เลือก (lab-worker หรือ lab-worker2) ในเครื่องนักศึกษาอาจต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจาก `kubectl get pod -o wide` ของเครื่องตัวเองเสมอ

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
| 7 | [LAB 5 ตาชั่งกองเรือ](#fig-7) | 20 | [ภาพหน้าจอจริง: สาขา lab-worker](#fig-20) |
| 8 | [LAB 6 ป้ายห้ามขึ้นและบัตรผ่าน](#fig-8) | 21 | [ภาพหน้าจอจริง: สาขา lab-worker2](#fig-21) |
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
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `time k8s-up` (ประมาณ 1 นาที) |

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
cat labs/lab01-scheduler/huge-pod.yaml
```

```yaml
# LAB 1: Pod ที่ขอหน่วยความจำมากเกินกว่าเรือลำไหนจะมี → Pending + Event FailedScheduling
apiVersion: v1
kind: Pod
metadata:
  name: huge-pod
  labels:
    lab: "03"
spec:
  terminationGracePeriodSeconds: 1   # busybox sleep ไม่ตอบ SIGTERM → ให้ลบเร็ว
  containers:
    - name: app
      image: busybox:1.36
      command: ["sleep", "3600"]
      resources:
        requests:
          memory: 4000Gi      # 4000 GiB! ไม่มี node ไหนรับไหว (แก้เป็น 256Mi ภายหลัง)
```

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

> **รู้ไว้ (ทางเลือก):** Kubernetes 1.37 มี subresource `resize` สำหรับปรับ resources ของ Pod ที่มีอยู่แล้ว ในการทดลองใช้กับ Pod ที่ Pending ได้ และ scheduler วางให้ทันที
> ```bash
> kubectl patch pod huge-pod --subresource resize -p '{"spec":{"containers":[{"name":"app","resources":{"requests":{"memory":"256Mi"}}}]}}'
> ```
> ผลจริง `pod/huge-pod patched` แล้ว Pod เปลี่ยนเป็น `ContainerCreating` บน `lab-worker` ภายใน 3 วินาที อย่างไรก็ตามวิธีหลักของบทนี้ยังเป็น "ลบแล้วสร้างใหม่"

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

### ขั้นที่ 4: รอดูชะตากรรมของ ghost-node-pod (ภายใน 1 นาที)

รอประมาณ 1 นาทีหลัง apply แล้วตรวจอีกครั้ง

```bash
kubectl get pod ghost-node-pod
kubectl logs -n kube-system kube-controller-manager-lab-control-plane | grep -i ghost-node-pod
```

```text
Error from server (NotFound): pods "ghost-node-pod" not found
I1004 11:59:08.298093       1 gc_controller.go:348] "PodGC is force deleting Pod" pod="default/ghost-node-pod"
I1004 11:59:08.312539       1 gc_controller.go:264] "Forced deletion of orphaned Pod succeeded" pod="default/ghost-node-pod"
```

(ในการทดลอง ตรวจทุก 5 วินาที เห็น `Pending` จนอายุ 61 วินาที แล้วรอบถัดไปกลายเป็น `NotFound` ถ้าตรวจเร็วกว่านั้นจะยังเห็น `Pending`)

### สิ่งที่เห็น

- `pinned-pod` **Running บน `lab-control-plane` ทั้งที่ไม่มี toleration ของ control-plane** (Tolerations มีแค่ 2 ตัวที่ระบบเติมให้) และ Events **ไม่มี `Scheduled`** มีแต่ Event จาก `kubelet` แสดงว่า scheduler ไม่ได้ยุ่งเลย
- `ghost-node-pod` แสดง `NODE lab-worker9` แต่ค้าง Pending โดยไม่มี Event ใด ๆ แล้วถูก **PodGC** ใน kube-controller-manager ลบทิ้งเอง (orphaned Pod) ราว 1 นาที
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
selector-pod   1/1     Running   0          4s    10.244.2.4    lab-worker2   <none>           <none>
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
