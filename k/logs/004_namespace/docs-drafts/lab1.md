# LAB บทที่ 4: Namespace — แบ่งโซนบนท่าเรือ สู่ร้านน้องส้มแยก environment

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Namespace — สำรวจ namespace ตั้งต้น, สร้าง/ลบ namespace, Pod ชื่อซ้ำ, context, namespaced/cluster-scoped, ข้ามโซนด้วย Pod IP และ NetworkPolicy, ResourceQuota, LimitRange, RBAC, Pod Security Admission, ลบโซนทั้งก้อน และร้านอาหารแมวน้องส้ม 3 environment ในคลัสเตอร์เดียว
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่ทาสีแบ่งโซนบนแผนผังท่าเรือ เริ่มจากสำรวจโซนที่มีอยู่แล้ว สร้างโซนของตัวเอง วางกล่องชื่อเดียวกันในหลายโซน สลับโซนเริ่มต้นของ kubectl แยกของประจำโซนกับของส่วนกลาง ทดลองว่าโซนไม่ได้กั้นเครือข่ายเองแล้วสร้างรั้วด้วย NetworkPolicy ตั้งงบ (ResourceQuota) กฎขนาดกล่อง (LimitRange) บัตรพนักงานเฉพาะโซน (RBAC) ด่านตรวจความปลอดภัย (Pod Security Admission) และลบโซนทั้งก้อน ปิดท้ายด้วยการเปิด **ร้านอาหารแมวน้องส้ม 3 environment (`som-dev`, `som-staging`, `som-prod`) จาก manifest ไฟล์เดียว** ที่หน้าร้านบอกเองว่าอยู่โซนไหน

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, kind v0.33.0, Kubernetes v1.37.0) เมื่อ 4 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, เลข port ของ API server และ Node ที่ scheduler เลือก (lab-worker หรือ lab-worker2) ในเครื่องนักศึกษาอาจต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker build` และ `docker save` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิดท่อ `ssh -L` ใน LAB 10 ที่ทำ 🖥️ บนเครื่องนักศึกษา

### กติกาของ LAB บทนี้

- ทุก LAB ทำในโฟลเดอร์ **`/workspace/004_kubernetes_namespace/02_LAB`** ภายใน k8s-lab (LAB 10 ย้ายเข้า `som-shop-envs/` ตามที่บอกในขั้นตอน)
- บทนี้ยังใช้ **Pod เดี่ยว ๆ เท่านั้น** การเข้าถึงแอปใช้ `kubectl exec`, `kubectl logs` และ `kubectl port-forward` + `ssh -L` เหมือนบทที่ 2–3
- **ทุก LAB ทำใน namespace ของตัวเอง ไม่ทิ้งของไว้ใน `default`** และจบด้วยบล็อก "เก็บกวาด" ที่ใช้ `kubectl delete ns ...` ซึ่งเป็นการฝึกหัวข้อของบทนี้ไปในตัว ถ้าต้องการทำ LAB ต่อเนื่องหลายข้อ ให้ทำตาม [ตารางเก็บกวาด](#ตารางเก็บกวาดและคืนสภาพ) (LAB 1–8 ใช้ namespace ต่อกันบางส่วน จะบอกไว้ในแต่ละ LAB)
- หลังเปลี่ยน namespace ของ context (LAB 2) **ต้องคืนค่าเป็น `default` เสมอ** และหลังสร้าง context ของ intern (LAB 7, LAB 10) ต้องลบออก
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง ส่วน token ของ ServiceAccount เป็นรหัสลับจริง **ห้ามแปะลงรายงานหรือแชท** (เอกสารนี้แสดงแบบตัด `eyJhbGciOi...`)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [สำรวจโซนเริ่มต้น](#lab-0-สำรวจโซนเริ่มต้น) | 15 นาที | ⭐ |
| 1 | [สร้าง/ลบ namespace และ Pod ชื่อซ้ำ](#lab-1-สร้างลบ-namespace-และ-pod-ชื่อซ้ำ) | 15 นาที | ⭐ |
| 2 | [เปลี่ยน namespace เริ่มต้นของ context](#lab-2-เปลี่ยน-namespace-เริ่มต้นของ-context) | 10 นาที | ⭐ |
| 3 | [ของประจำโซน vs ของส่วนกลาง](#lab-3-ของประจำโซน-vs-ของส่วนกลาง) | 10 นาที | ⭐⭐ |
| 4 | [ข้ามโซน: Pod IP, เรือเดียวกัน และ NetworkPolicy](#lab-4-ข้ามโซน-pod-ip-เรือเดียวกัน-และ-networkpolicy) | 20 นาที | ⭐⭐⭐ |
| 5 | [ResourceQuota: งบของโซน](#lab-5-resourcequota-งบของโซน) | 10 นาที | ⭐⭐ |
| 6 | [LimitRange: กฎขนาดกล่อง](#lab-6-limitrange-กฎขนาดกล่อง) | 10 นาที | ⭐⭐ |
| 7 | [RBAC: บัตรพนักงานเฉพาะโซน](#lab-7-rbac-บัตรพนักงานเฉพาะโซน) | 20 นาที | ⭐⭐⭐ |
| 8 | [Pod Security Admission: ด่านตรวจหน้าโซน](#lab-8-pod-security-admission-ด่านตรวจหน้าโซน) | 15 นาที | ⭐⭐⭐ |
| 9 | [ลบโซนทั้งก้อน](#lab-9-ลบโซนทั้งก้อน) | 10 นาที | ⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มแยก environment](#lab-10-lab-สุดท้าย-ร้านน้องส้มแยก-environment) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (LAB 10 มีช่วง build image ของแอป)

### สารบัญรูปภาพ

{{FIGTABLE}}

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ + screenshots/ ภาพหน้าจอจริงของร้าน 3 environment
├── labs/
│   ├── lab01-create-ns/{ns-blue,snack-pod,snack-green-pod}.yaml
│   ├── lab04-network/{zones,web-pod,client-pods,np-same-ns,np-allow-team-b}.yaml
│   ├── lab05-quota/{quota,no-request-pod,small-pods}.yaml
│   ├── lab06-limitrange/{limitrange,plain-pod,big-pod}.yaml
│   ├── lab07-rbac/{sa-role-binding,view-clusterrole-binding}.yaml
│   ├── lab08-psa/{root-nginx-pod,privileged-pod,restricted-ok-pod}.yaml
│   └── lab09-delete-ns/doomed.yaml
└── som-shop-envs/                     ← LAB 10 ร้านน้องส้ม 3 environment
    ├── app/                           ← แอป Next.js + Dockerfile (som-shop-web:1.1 อ่านข้อความหัว/ท้ายหน้าจาก env)
    └── k8s/{00-namespaces,prod-guardrails,som-shop,som-shop-v002,intern-rbac}.yaml
```

LAB 0, 2 และ 3 ไม่มีไฟล์ ใช้คำสั่งล้วน

---

## LAB 0: สำรวจโซนเริ่มต้น

{{FIG:L01|LAB 0 สำรวจโซนเริ่มต้น}}

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 3 หรือสร้างใหม่) แล้วสำรวจ namespace ที่มีอยู่และของข้างใน

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md), [2](../../002_kubernetes_pod/02_LAB/README.md) และ [3](../../003_kubernetes_node_pod/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`) และมีโฟลเดอร์ `004_kubernetes_namespace` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `004_kubernetes_namespace` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 004_kubernetes_namespace k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลัง ต้องสั่ง `docker cp` ซ้ำ โฟลเดอร์นี้มีทั้งไฟล์ YAML ของ LAB 1–9 (`02_LAB/labs/`) และแอปกับ manifest ของ LAB 10 (`02_LAB/som-shop-envs/`) จึงคัดลอกครั้งเดียวพอ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` หน้าต่างนี้คือ **SSH session หลัก** (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/004_kubernetes_namespace/02_LAB
ls
kubectl get nodes
kubectl get pods
```

`ls` ต้องเห็น `README.md  images  labs  som-shop-envs` จากนั้นเลือกทางตามผลของ `kubectl get nodes`

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node (`lab-control-plane`, `lab-worker`, `lab-worker2`) เป็น `Ready` (คลัสเตอร์จากบทที่ 3 ยังอยู่) | **ใช้ต่อได้เลย** ถ้า `kubectl get pods` ยังมี Pod จากบทก่อนค้าง ให้ลบด้วย `kubectl delete pod --all` แล้วข้ามไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `time k8s-up` (ประมาณ 1 นาที) |

ตรวจด้วยว่าไม่มี label/taint หรือ Node ที่ถูก cordon ค้างจากบทที่ 3 (คอลัมน์ STATUS ต้องเป็น `Ready` เฉย ๆ ไม่มี `SchedulingDisabled`) ถ้ามี ให้ทำ "ตารางคืนสภาพคลัสเตอร์" ของบทที่ 3 ก่อน

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

real	0m50.878s
```

> ข้อความท้าย `k8s-up` มีคำแนะนำตัวอย่างอื่น ๆ ของ image และ port 30080–30082 ซึ่ง **ยังไม่ใช้ในบทนี้** ให้ข้ามไป

### ขั้นที่ 4: ดู namespace ทั้งหมด

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get ns
kubectl get ns --show-labels
```

```text
NAME                 STATUS   AGE
default              Active   101s
kube-node-lease      Active   101s
kube-public          Active   101s
kube-system          Active   101s
local-path-storage   Active   97s

NAME                 STATUS   AGE    LABELS
default              Active   101s   kubernetes.io/metadata.name=default
kube-node-lease      Active   101s   kubernetes.io/metadata.name=kube-node-lease
kube-public          Active   101s   kubernetes.io/metadata.name=kube-public
kube-system          Active   101s   kubernetes.io/metadata.name=kube-system
local-path-storage   Active   97s    kubernetes.io/metadata.name=local-path-storage
```

(ถ้าใช้คลัสเตอร์เดิมจากบทก่อน AGE จะเป็นชั่วโมงหรือวัน)

### ขั้นที่ 5: Pod ทั้งท่าเรือ และ Pod ของระบบ

```bash
kubectl get pods -A -o wide
kubectl get pods -n kube-system
kubectl get pods -n local-path-storage
```

ผลจริง (ตัดคอลัมน์ `NOMINATED NODE` และ `READINESS GATES` ที่เป็น `<none>` ออก)

```text
NAMESPACE            NAME                                        READY   STATUS    RESTARTS   AGE    IP           NODE
kube-system          coredns-559f6c778d-5hcpz                    1/1     Running   0          93s    10.244.0.3   lab-control-plane
kube-system          coredns-559f6c778d-6hfdw                    1/1     Running   0          93s    10.244.0.4   lab-control-plane
kube-system          etcd-lab-control-plane                      1/1     Running   0          99s    172.19.0.2   lab-control-plane
kube-system          kindnet-dq2ng                               1/1     Running   0          93s    172.19.0.2   lab-control-plane
kube-system          kindnet-mbmsr                               1/1     Running   0          92s    172.19.0.4   lab-worker2
kube-system          kindnet-vlb7z                               1/1     Running   0          92s    172.19.0.3   lab-worker
kube-system          kube-apiserver-lab-control-plane            1/1     Running   0          99s    172.19.0.2   lab-control-plane
kube-system          kube-controller-manager-lab-control-plane   1/1     Running   0          100s   172.19.0.2   lab-control-plane
kube-system          kube-proxy-6c5br                            1/1     Running   0          93s    172.19.0.2   lab-control-plane
kube-system          kube-proxy-htcvs                            1/1     Running   0          92s    172.19.0.4   lab-worker2
kube-system          kube-proxy-hzmtb                            1/1     Running   0          92s    172.19.0.3   lab-worker
kube-system          kube-scheduler-lab-control-plane            1/1     Running   0          99s    172.19.0.2   lab-control-plane
local-path-storage   local-path-provisioner-75f7fc7dc5-kn7sx     1/1     Running   0          93s    10.244.0.2   lab-control-plane
```

`-A` เพิ่มคอลัมน์ `NAMESPACE` ให้ ข้อสังเกต: `kube-system` มี 12 Pod (control plane 4 ตัว, coredns 2 ตัว, kindnet และ kube-proxy เรือละตัว) ส่วน `local-path-provisioner` อยู่ใน `local-path-storage` และ **ไม่มี Pod ของเราเลย** (`default` ว่าง) คำสั่ง `kubectl get pods -n kube-system` และ `-n local-path-storage` แสดงแถวชุดเดียวกันแยกตามโซน โดยไม่มีคอลัมน์ NAMESPACE

### ขั้นที่ 6: ส่องของใน kube-public, kube-node-lease และ default

{{FIG:L02|LAB 0 kube-public และ kube-node-lease}}

```bash
kubectl get pods -n kube-public
kubectl get cm -n kube-public
kubectl get lease -n kube-node-lease
kubectl get sa,cm -n default
kubectl describe ns default
kubectl get ns default -o yaml
```

```text
No resources found in kube-public namespace.

NAME               DATA   AGE
cluster-info       2      100s
kube-root-ca.crt   1      93s

NAME                HOLDER              AGE
lab-control-plane   lab-control-plane   99s
lab-worker          lab-worker          82s
lab-worker2         lab-worker2         82s

NAME                     AGE
serviceaccount/default   93s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      93s

Name:         default
Labels:       kubernetes.io/metadata.name=default
Annotations:  <none>
Status:       Active

No resource quota.

No LimitRange resource.

apiVersion: v1
kind: Namespace
metadata:
  creationTimestamp: "2026-10-04T13:27:44Z"
  labels:
    kubernetes.io/metadata.name: default
  name: default
  resourceVersion: "20"
  uid: 5d8f94f8-5d8a-400a-ab46-6d0cac45c5b2
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
```

### สิ่งที่เห็น

- kind มี namespace **5 ตัว** (4 ตัวมาตรฐาน + `local-path-storage` ของ kind) ทุกตัวมี label อัตโนมัติ `kubernetes.io/metadata.name=<ชื่อ>` เพียง label เดียว
- `kube-system` เป็นโซนพนักงานของท่าเรือ มี Pod ของ control plane (ชื่อลงท้าย `-lab-control-plane` เพราะเป็น static Pod จากบทที่ 3), DNS และ network
- `kube-public` ไม่มี Pod มีแต่ ConfigMap `cluster-info` (ประกาศสาธารณะ) ส่วน `kube-node-lease` มี Lease 3 ใบ เท่าจำนวนเรือ
- `default` มีของ 2 ชิ้นที่ระบบใส่ให้ทุก namespace คือ ServiceAccount `default` และ ConfigMap `kube-root-ca.crt` และ **ไม่มีงบ (quota) และไม่มีกฎขนาดกล่อง (LimitRange)**
- Namespace object มี `spec.finalizers: [kubernetes]` และ `status.phase: Active` แต่ไม่มี `metadata.namespace` (เป็น cluster-scoped)

> **🤔 คำถามชวนคิด:** ถ้าจะหาว่า Pod `coredns` อยู่ namespace ไหน โดยไม่รู้มาก่อน ใช้คำสั่งอะไร และทำไม `kubectl get pods` เฉย ๆ จึงไม่เห็น Pod ระบบเหล่านี้เลย

**เก็บกวาด:** LAB นี้ไม่ได้สร้างอะไร ไม่ต้องเก็บกวาด

---

## LAB 1: สร้าง/ลบ namespace และ Pod ชื่อซ้ำ

{{FIG:L03|LAB 1 Pod ชื่อซ้ำในหลายโซน}}

**เป้าหมาย:** สร้าง namespace 2 วิธี วาง Pod ชื่อเดียวกันใน 3 namespace จากไฟล์เดียว เข้าใจ `metadata.namespace` เทียบกับ `-n` และเห็นข้อความ error จริงของชื่อซ้ำ ชื่อผิดกฎ และการเรียกชื่อข้ามทุก namespace

**ไฟล์:** `labs/lab01-create-ns/`

```bash
ls labs/lab01-create-ns
cat labs/lab01-create-ns/ns-blue.yaml labs/lab01-create-ns/snack-pod.yaml
```

```yaml
# LAB 1: สร้าง namespace แบบเขียน YAML (เทียบกับ kubectl create namespace green)
apiVersion: v1
kind: Namespace
metadata:
  name: blue                     # ชื่อโซน: a-z 0-9 และ - ยาวไม่เกิน 63 ตัว ห้ามขึ้นต้นด้วย kube-
  labels:
    lab: "04"                    # label ของ namespace เอง (ไว้ค้นด้วย -l)
---
# LAB 1: Pod ขนมแมว "snack" — ไม่มี metadata.namespace
# จะไปอยู่โซนไหนขึ้นกับ -n ตอนสั่ง (ไม่ใส่ -n → namespace ของ context ปกติคือ default)
apiVersion: v1
kind: Pod
metadata:
  name: snack
  labels:
    app: snack
spec:
  terminationGracePeriodSeconds: 1   # busybox sh เป็น PID 1 ไม่ตอบ SIGTERM → ให้ลบเร็ว
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "echo snack พร้อมเสิร์ฟ; sleep 3600"]
```

(`---` ในบล็อกข้างบนแสดงรอยต่อของ 2 ไฟล์ ส่วน `snack-green-pod.yaml` เหมือน `snack-pod.yaml` แต่ชื่อ `snack-green` และมี `namespace: green` ในไฟล์)

### ขั้นที่ 1: สร้าง namespace 2 วิธี

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/004_kubernetes_namespace/02_LAB`)

```bash
kubectl create namespace green
kubectl create namespace green --dry-run=client -o yaml
kubectl apply -f labs/lab01-create-ns/ns-blue.yaml
kubectl get ns blue green --show-labels
```

```text
namespace/green created
apiVersion: v1
kind: Namespace
metadata:
  name: green
spec: {}
status: {}
namespace/blue created
NAME    STATUS   AGE   LABELS
blue    Active   0s    kubernetes.io/metadata.name=blue,lab=04
green   Active   0s    kubernetes.io/metadata.name=green
```

`--dry-run=client -o yaml` แค่พิมพ์ YAML ที่ "จะ" ถูกส่ง ไม่ได้สร้างซ้ำ จึงไม่ error ว่ามีอยู่แล้ว ใช้เป็นจุดเริ่มเขียนไฟล์ได้

### ขั้นที่ 2: Pod ชื่อเดียวกันใน 3 โซนจากไฟล์เดียว

```bash
kubectl apply -f labs/lab01-create-ns/snack-pod.yaml -n blue
kubectl apply -f labs/lab01-create-ns/snack-pod.yaml -n green
kubectl apply -f labs/lab01-create-ns/snack-pod.yaml
kubectl wait --for=condition=Ready pod/snack -n blue --timeout=90s
kubectl wait --for=condition=Ready pod/snack -n green --timeout=90s
kubectl wait --for=condition=Ready pod/snack --timeout=90s
kubectl get pods -A -l app=snack -o wide
```

```text
pod/snack created
pod/snack created
pod/snack created
pod/snack condition met
pod/snack condition met
pod/snack condition met
NAMESPACE   NAME    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
blue        snack   1/1     Running   0          7s    10.244.2.2   lab-worker    <none>           <none>
default     snack   1/1     Running   0          6s    10.244.2.3   lab-worker    <none>           <none>
green       snack   1/1     Running   0          6s    10.244.1.2   lab-worker2   <none>           <none>
```

ดูทีละโซน และอ่าน namespace จาก object

```bash
kubectl get pods
kubectl get pods -n blue
kubectl get pod snack -n blue -o jsonpath="{.metadata.namespace}{\"\n\"}"
kubectl logs snack -n green
```

```text
NAME    READY   STATUS    RESTARTS   AGE
snack   1/1     Running   0          6s
NAME    READY   STATUS    RESTARTS   AGE
snack   1/1     Running   0          8s
blue
snack พร้อมเสิร์ฟ
```

### ขั้นที่ 3: ป้ายในไฟล์ไม่ตรงกับ -n

{{FIG:L04|LAB 1 namespace ในไฟล์ไม่ตรงกับ -n}}

```bash
kubectl apply -f labs/lab01-create-ns/snack-green-pod.yaml -n blue
kubectl apply -f labs/lab01-create-ns/snack-green-pod.yaml
kubectl get pods -n green
```

```text
error: the namespace from the provided object "green" does not match the namespace "blue". You must pass '--namespace=green' to perform this operation.
pod/snack-green created
NAME          READY   STATUS              RESTARTS   AGE
snack         1/1     Running             0          7s
snack-green   0/1     ContainerCreating   0          0s
```

ครั้งแรก kubectl ปฏิเสธและไม่สร้างอะไร ครั้งที่สองไม่ใส่ `-n` Pod จึงไปตามป้ายในไฟล์ (`green`)

### ขั้นที่ 4: ชื่อซ้ำในโซนเดียว, เรียกชื่อข้ามทุกโซน, ชื่อผิดกฎ

```bash
kubectl create -f labs/lab01-create-ns/snack-pod.yaml -n blue
kubectl apply -f labs/lab01-create-ns/snack-pod.yaml -n blue
kubectl get pod snack -A
kubectl get pods -A --field-selector metadata.name=snack
kubectl create namespace Blue_Zone
```

```text
Error from server (AlreadyExists): error when creating "labs/lab01-create-ns/snack-pod.yaml": pods "snack" already exists
pod/snack unchanged
error: a resource cannot be retrieved by name across all namespaces
NAMESPACE   NAME    READY   STATUS    RESTARTS   AGE
blue        snack   1/1     Running   0          9s
default     snack   1/1     Running   0          8s
green       snack   1/1     Running   0          8s
The Namespace "Blue_Zone" is invalid: metadata.name: Invalid value: "Blue_Zone": a lowercase RFC 1123 label must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character (e.g. 'my-name',  or '123-abc', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?')
```

### ขั้นที่ 5: คำนำหน้า kube- เป็นข้อตกลง ไม่ใช่กฎของ API

```bash
kubectl create namespace kube-mine
kubectl delete ns kube-mine
```

```text
namespace/kube-mine created
namespace "kube-mine" deleted
```

ทฤษฎีบอกว่า "ห้ามขึ้นต้นด้วย `kube-`" (และคอมเมนต์ใน `ns-blue.yaml` ก็เขียนแบบนั้น) แต่ผลจริงคือ **API ยอมให้สร้าง** เพราะเป็นธรรมเนียมที่สงวนชื่อไว้ให้ระบบ ไม่ใช่กฎ validation เราจึงลบทิ้งทันทีและไม่ควรตั้งชื่อแบบนี้ในงานจริง

### ขั้นที่ 6: ดู Namespace object และเก็บ snack ของ default

```bash
kubectl get ns blue -o yaml
kubectl delete pod snack
kubectl get pods
```

```text
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Namespace","metadata":{"annotations":{},"labels":{"lab":"04"},"name":"blue"}}
  creationTimestamp: "2026-10-04T13:29:35Z"
  labels:
    kubernetes.io/metadata.name: blue
    lab: "04"
  name: blue
  ...
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
pod "snack" deleted from default namespace
No resources found in default namespace.
```

`blue` มี annotation `last-applied-configuration` เพราะสร้างด้วย `apply` ส่วน `green` (สร้างด้วย `create`) ไม่มี และ kubectl รุ่นนี้บอกชัดว่าลบ Pod จาก namespace ไหน (`deleted from default namespace`)

### สิ่งที่เห็น

- ไฟล์ `snack-pod.yaml` ไฟล์เดียวสร้าง `blue/snack`, `green/snack`, `default/snack` ได้โดยไม่ชนกัน และ Pod ของต่างโซนอยู่บนเรือลำเดียวกันหรือคนละลำก็ได้
- `metadata.namespace` ในไฟล์ไม่ตรงกับ `-n` = error ไม่สร้างอะไร
- `create` ซ้ำได้ `AlreadyExists` ส่วน `apply` ซ้ำได้ `unchanged`
- `kubectl get pod <ชื่อ> -A` ใช้ไม่ได้ ต้องใช้ `--field-selector metadata.name=<ชื่อ>`
- ชื่อ namespace ต้องเป็นตัวพิมพ์เล็ก ตัวเลข และ `-` เท่านั้น ส่วนคำนำหน้า `kube-` API ยอมแต่ห้ามใช้ตามธรรมเนียม

> **🤔 คำถามชวนคิด:** ถ้าทีม dev และทีม prod ใช้ไฟล์ `snack-green-pod.yaml` (ที่มี `namespace: green` ในไฟล์) ร่วมกัน จะเกิดปัญหาอะไร และควรแก้ไฟล์อย่างไร

**เก็บกวาด:** เก็บ `blue` และ `green` ไว้ใช้ต่อใน LAB 2–4 ถ้าจะหยุดทำที่ LAB นี้ ให้ลบด้วย `kubectl delete ns blue green`

---

## LAB 2: เปลี่ยน namespace เริ่มต้นของ context

{{FIG:L05|LAB 2 สลับโซนเริ่มต้นของ context}}

**เป้าหมาย:** อ่าน kubeconfig และ context, สลับ namespace เริ่มต้นเป็น `blue` แล้วเห็นว่าคำสั่งที่ไม่มี `-n` ไปที่ blue ทั้งหมด จากนั้นคืนค่า

**ต้องมีจาก LAB 1:** namespace `blue` และ Pod `blue/snack`

### ขั้นที่ 1: อ่าน context และ kubeconfig

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl config get-contexts
kubectl config current-context
kubectl config view --minify
echo "[$(kubectl config view --minify -o jsonpath={..namespace})]"
```

```text
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   
kind-lab
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://127.0.0.1:41301
  name: kind-lab
contexts:
- context:
    cluster: kind-lab
    user: kind-lab
  name: kind-lab
current-context: kind-lab
kind: Config
users:
- name: kind-lab
  user:
    client-certificate-data: DATA+OMITTED
    client-key-data: DATA+OMITTED
[]
```

คอลัมน์ `NAMESPACE` **ว่าง** และ jsonpath ได้ค่าว่าง (`[]`) แปลว่า context ไม่ได้ตั้ง namespace ไว้ kubectl จึงใช้ `default` (เลข port ใน `server` ของแต่ละเครื่องต่างกัน)

### ขั้นที่ 2: สลับโซนเริ่มต้นเป็น blue

```bash
kubectl config set-context --current --namespace=blue
kubectl config get-contexts
kubectl get pods
kubectl run peek --image=busybox:1.36 -- sleep 3600
kubectl wait --for=condition=Ready pod/peek --timeout=60s
kubectl get pods
kubectl get pods -n default
kubectl get pod peek -o jsonpath="{.metadata.namespace}{\"\n\"}"
```

```text
Context "kind-lab" modified.
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   blue
NAME    READY   STATUS    RESTARTS   AGE
snack   1/1     Running   0          26s
pod/peek created
pod/peek condition met
NAME    READY   STATUS    RESTARTS   AGE
peek    1/1     Running   0          1s
snack   1/1     Running   0          27s
No resources found in default namespace.
blue
```

`kubectl get pods` ที่ไม่มี `-n` เห็น `snack` ของ blue และ Pod `peek` ที่สร้างด้วย `kubectl run` โดยไม่ระบุ namespace ก็ไปอยู่ที่ `blue`

### ขั้นที่ 3: คืนค่าเป็น default (ห้ามลืม)

```bash
kubectl config set-context --current --namespace=default
kubectl config get-contexts
kubectl get pods
kubectl get pods -n blue
```

```text
Context "kind-lab" modified.
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
No resources found in default namespace.
NAME    READY   STATUS    RESTARTS   AGE
peek    1/1     Running   0          2s
snack   1/1     Running   0          28s
```

หลังคืนค่า คอลัมน์ NAMESPACE แสดง `default` (ไม่กลับเป็นช่องว่าง แต่ความหมายเท่ากัน)

### ขั้นที่ 4: kubeconfig ของ kind ใช้อะไรยืนยันตัวตน

```bash
grep -E "^\s+(client-certificate-data|client-key-data|token):" ~/.kube/config | cut -c1-40
```

```text
    client-certificate-data: LS0tLS1CRUd
    client-key-data: LS0tLS1CRUdJTiBSU0E
```

(`cut -c1-40` ตัดให้เห็นแค่ต้นบรรทัด ไม่ต้องพิมพ์ค่าเต็มซึ่งเป็นกุญแจลับของผู้ดูแลคลัสเตอร์) user ของ kind ใช้ **client certificate** ไม่มี token จำข้อนี้ไว้ใช้ใน LAB 7

### สิ่งที่เห็น

- kubeconfig มี clusters, users, contexts และ current-context โดย context `kind-lab` เริ่มแรกไม่ได้ตั้ง namespace (= default)
- `set-context --current --namespace=blue` ทำให้ทุกคำสั่งที่ไม่มี `-n` (ทั้งดูและสร้าง) ไปที่ blue ทันที และค่านี้ถูกเขียนลงไฟล์ จึงอยู่ข้าม terminal
- คืนค่าด้วย `--namespace=default` แล้วตรวจด้วย `kubectl config get-contexts`

> **🤔 คำถามชวนคิด:** ถ้าเพื่อนเปิด JupyterLab Terminal อีกหน้าต่างหนึ่งของ k8s-lab เดียวกันระหว่างที่คุณตั้ง namespace เป็น blue อยู่ แล้วเขาสั่ง `kubectl delete pod snack` จะเกิดอะไรขึ้น

**เก็บกวาด:** ยืนยันว่า `kubectl config get-contexts` แสดง NAMESPACE เป็น `default` แล้ว ส่วน `blue/peek` ปล่อยไว้ได้ (จะถูกลบพร้อม `blue` ใน LAB 9)

---

## LAB 3: ของประจำโซน vs ของส่วนกลาง

{{FIG:L06|LAB 3 แยก namespaced กับ cluster-scoped}}

**เป้าหมาย:** แยกชนิด resource ที่เป็น namespaced กับ cluster-scoped ด้วย `kubectl api-resources` และเห็นว่า `-n` ไม่มีผลกับของส่วนกลาง

### ขั้นที่ 1: นับและดูตัวอย่างแต่ละกลุ่ม

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl api-resources --namespaced=true -o name | wc -l
kubectl api-resources --namespaced=false -o name | wc -l
kubectl api-resources --namespaced=true | head -13
```

```text
34
37
NAME                        SHORTNAMES   APIVERSION                     NAMESPACED   KIND
bindings                                 v1                             true         Binding
configmaps                  cm           v1                             true         ConfigMap
endpoints                   ep           v1                             true         Endpoints
events                      ev           v1                             true         Event
limitranges                 limits       v1                             true         LimitRange
persistentvolumeclaims      pvc          v1                             true         PersistentVolumeClaim
pods                        po           v1                             true         Pod
podtemplates                             v1                             true         PodTemplate
replicationcontrollers      rc           v1                             true         ReplicationController
resourcequotas              quota        v1                             true         ResourceQuota
secrets                                  v1                             true         Secret
serviceaccounts             sa           v1                             true         ServiceAccount
```

ลองดูรายการของส่วนกลางทั้งหมดด้วยตัวเอง (`kubectl api-resources --namespaced=false`) จะเห็น `namespaces`, `nodes`, `persistentvolumes`, `storageclasses`, `priorityclasses`, `clusterroles`, `clusterrolebindings`, `csidrivers`, `runtimeclasses` และอื่น ๆ (ตัวเลข 34/37 อาจต่างได้ถ้าคลัสเตอร์มีส่วนขยายติดตั้งเพิ่ม)

### ขั้นที่ 2: เทียบชนิดที่ใช้ในบทนี้

```bash
kubectl api-resources | grep -E "^(pods|nodes|namespaces|resourcequotas|limitranges|networkpolicies|roles|clusterroles) "
```

```text
limitranges                         limits       v1                                true         LimitRange
namespaces                          ns           v1                                false        Namespace
nodes                               no           v1                                false        Node
pods                                po           v1                                true         Pod
resourcequotas                      quota        v1                                true         ResourceQuota
networkpolicies                     netpol       networking.k8s.io/v1              true         NetworkPolicy
clusterroles                                     rbac.authorization.k8s.io/v1      false        ClusterRole
roles                                            rbac.authorization.k8s.io/v1      true         Role
```

### ขั้นที่ 3: -n กับของส่วนกลาง

```bash
kubectl get nodes -n blue
kubectl get sc
kubectl get sc -n green
kubectl get pv
kubectl get priorityclass
kubectl get ns blue -n green
```

```text
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   2m25s   v1.37.0
lab-worker          Ready    <none>          2m15s   v1.37.0
lab-worker2         Ready    <none>          2m15s   v1.37.0
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  2m21s
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  2m21s
No resources found
NAME                      VALUE        GLOBAL-DEFAULT   AGE     PREEMPTIONPOLICY
system-cluster-critical   2000000000   false            2m24s   PreemptLowerPriority
system-node-critical      2000001000   false            2m24s   PreemptLowerPriority
NAME   STATUS   AGE
blue   Active   35s
```

สังเกต `kubectl get pv` ตอบ `No resources found` เฉย ๆ **ไม่มี** คำว่า `in default namespace` ต่อท้าย เพราะ PersistentVolume ไม่อยู่ใน namespace ใด

### ขั้นที่ 4: ClusterRole สำเร็จรูป (ปูทาง LAB 7)

```bash
kubectl get clusterroles | wc -l
kubectl get clusterroles view edit admin cluster-admin
```

```text
78
NAME            CREATED AT
view            2026-10-04T13:27:45Z
edit            2026-10-04T13:27:45Z
admin           2026-10-04T13:27:45Z
cluster-admin   2026-10-04T13:27:45Z
```

(78 บรรทัด = หัวตาราง 1 + ClusterRole 77 ตัว)

### สิ่งที่เห็น

- Kubernetes v1.37 มี resource แบบ namespaced 34 ชนิด และ cluster-scoped 37 ชนิด
- Node, Namespace, StorageClass, PersistentVolume, PriorityClass, ClusterRole เป็นของส่วนกลาง ใส่ `-n` ก็ได้ผลเหมือนเดิม (ไม่ error แต่ไม่กรอง)
- ข้อความ `No resources found` ของ resource แบบ cluster-scoped ไม่มีชื่อ namespace ต่อท้าย

> **🤔 คำถามชวนคิด:** ถ้าทีม `blue` อยากได้ StorageClass ชื่อ `fast` และทีม `green` ก็อยากได้ชื่อ `fast` แต่ตั้งค่าคนละแบบ ทำได้ไหม เพราะอะไร

**เก็บกวาด:** LAB นี้ไม่ได้สร้างอะไร

---
