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

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 สำรวจโซนเริ่มต้น](#fig-1) | 15 | [LAB 10 ภาพเปิด ร้านน้องส้ม 3 environment](#fig-15) |
| 2 | [LAB 0 kube-public และ kube-node-lease](#fig-2) | 16 | [Downward API ส่งชื่อ namespace เข้าหน้าร้าน](#fig-16) |
| 3 | [LAB 1 Pod ชื่อซ้ำในหลายโซน](#fig-3) | 17 | [ชุดป้องกันของ som-prod](#fig-17) |
| 4 | [LAB 1 namespace ในไฟล์ไม่ตรงกับ -n](#fig-4) | 18 | [ร้านฉบับเก่าถูกด่าน restricted ปฏิเสธ](#fig-18) |
| 5 | [LAB 2 สลับโซนเริ่มต้นของ context](#fig-5) | 19 | [สาขาที่ 3 ชนงบของ som-prod](#fig-19) |
| 6 | [LAB 3 แยก namespaced กับ cluster-scoped](#fig-6) | 20 | [intern ดูได้อย่างเดียวเฉพาะ som-dev](#fig-20) |
| 7 | [LAB 4 ต่างโซนอยู่เรือเดียวกันและคุยกันได้](#fig-7) | 21 | [port-forward 3 โซนผ่าน ssh -L](#fig-21) |
| 8 | [LAB 4 NetworkPolicy กั้นแล้วเปิดประตู](#fig-8) | 22 | [ภาพหน้าจอจริง โซน som-dev](#fig-22) |
| 9 | [LAB 5 ใบงบของโซน budget](#fig-9) | 23 | [ภาพหน้าจอจริง โซน som-staging](#fig-23) |
| 10 | [LAB 6 LimitRange เติมค่าและกันกล่องใหญ่](#fig-10) | 24 | [ภาพหน้าจอจริง โซน som-prod](#fig-24) |
| 11 | [LAB 7 บัตร intern ของ team-a](#fig-11) | 25 | [ลบ som-dev แล้ว staging และ prod ยังเปิดอยู่](#fig-25) |
| 12 | [LAB 7 --token กับ context ใหม่](#fig-12) | 26 | [ภาพหน้าจอจริง โซน som-dev หายแล้ว](#fig-26) |
| 13 | [LAB 8 ด่านตรวจ restricted](#fig-13) | 27 | [ภาพหน้าจอจริง som-prod ยังเปิดอยู่](#fig-27) |
| 14 | [LAB 9 ลบโซน doomed](#fig-14) | 28 | [สรุป LAB บทที่ 4](#fig-28) |

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

<p align="center" id="fig-1">
  <img src="images/01-lab0-survey-zones.png" alt="รูปที่ 1 LAB 0 สำรวจโซนเริ่มต้น" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: kubectl get ns --show-labels เห็น 5 โซนตั้งต้นของ kind และ kubectl get pods -A เห็นว่า Pod ระบบอยู่ใน kube-system</em>
</p>

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

<p align="center" id="fig-2">
  <img src="images/02-lab0-peek-public-lease.png" alt="รูปที่ 2 LAB 0 kube-public และ kube-node-lease" width="900"><br>
  <em><b>รูปที่ 2</b> LAB0: ดูของใน kube-public (ConfigMap cluster-info) และ kube-node-lease (Lease 3 ใบ ของเรือ 3 ลำ)</em>
</p>

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

<p align="center" id="fig-3">
  <img src="images/03-lab1-same-name-pods.png" alt="รูปที่ 3 LAB 1 Pod ชื่อซ้ำในหลายโซน" width="900"><br>
  <em><b>รูปที่ 3</b> LAB1: สร้าง namespace blue และ green แล้ววาง Pod ชื่อ snack ในแต่ละโซนจากไฟล์เดียวกัน ไม่ชนกัน</em>
</p>

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

<p align="center" id="fig-4">
  <img src="images/04-lab1-namespace-mismatch.png" alt="รูปที่ 4 LAB 1 namespace ในไฟล์ไม่ตรงกับ -n" width="900"><br>
  <em><b>รูปที่ 4</b> LAB1: ไฟล์ที่เขียน metadata.namespace: green แต่สั่ง -n blue จะถูก kubectl ปฏิเสธ</em>
</p>

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

ชื่อที่ขึ้นต้นด้วย `kube-` ถูกสงวนไว้ให้ระบบตามธรรมเนียม (คอมเมนต์ใน `ns-blue.yaml` เขียนว่า "ไม่ควร") แต่ผลจริงคือ **API ยอมให้สร้าง** เพราะไม่ใช่กฎ validation เราจึงลบทิ้งทันทีและไม่ควรตั้งชื่อแบบนี้ในงานจริง

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

<p align="center" id="fig-5">
  <img src="images/05-lab2-switch-context-ns.png" alt="รูปที่ 5 LAB 2 สลับโซนเริ่มต้นของ context" width="900"><br>
  <em><b>รูปที่ 5</b> LAB2: set-context --current --namespace=blue แล้ว kubectl get pods เห็นของในโซน blue ทันที อย่าลืมคืนค่าเป็น default</em>
</p>

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

<p align="center" id="fig-6">
  <img src="images/06-lab3-sort-scope.png" alt="รูปที่ 6 LAB 3 แยก namespaced กับ cluster-scoped" width="900"><br>
  <em><b>รูปที่ 6</b> LAB3: api-resources --namespaced=true/false และทดลองว่า kubectl get nodes -n blue ได้ผลเหมือนไม่ใส่ -n</em>
</p>

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

## LAB 4: ข้ามโซน: Pod IP, เรือเดียวกัน และ NetworkPolicy

<p align="center" id="fig-7">
  <img src="images/07-lab4-cross-zone-ip.png" alt="รูปที่ 7 LAB 4 ต่างโซนอยู่เรือเดียวกันและคุยกันได้" width="900"><br>
  <em><b>รูปที่ 7</b> LAB4: Pod web ใน team-a และ client ใน team-b อยู่บนเรือ lab-worker ลำเดียวกัน และ wget ถึงกันด้วย Pod IP ได้</em>
</p>

**เป้าหมาย:** เห็นด้วยตาว่า namespace ไม่ได้แยก Node และไม่ได้กั้นเครือข่าย ดู search domain ของ DNS แล้วสร้างรั้วด้วย NetworkPolicy และเปิดประตูให้เฉพาะโซนที่ต้องการ

**ไฟล์:** `labs/lab04-network/`

| ไฟล์ | เนื้อหา |
|---|---|
| `zones.yaml` | namespace `team-a` (label `team: a`) และ `team-b` (label `team: b`) |
| `web-pod.yaml` | nginx ชื่อ `web` ใน `team-a` ปักไว้ที่ `lab-worker` ด้วย `nodeSelector` |
| `client-pods.yaml` | busybox ชื่อ `client` ใน `team-a` และ `team-b` (ชื่อเดียวกัน) บน `lab-worker` ทั้งคู่ |
| `np-same-ns.yaml` | รั้ว: ทุก Pod ใน `team-a` รับเฉพาะจาก Pod ใน `team-a` |
| `np-allow-team-b.yaml` | ประตู: Pod `app=web` รับจาก namespace `team-b` ได้ด้วย |

ทุก Pod ติด label `lab: net` ไว้ดูรวมกันได้

### ขั้นที่ 1: สร้างโซนและ Pod

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab04-network/zones.yaml
kubectl apply -f labs/lab04-network/web-pod.yaml -f labs/lab04-network/client-pods.yaml
kubectl wait --for=condition=Ready pod -l lab=net -A --timeout=120s
kubectl get pods -A -o wide -l lab=net
```

```text
namespace/team-a created
namespace/team-b created
pod/web created
pod/client created
pod/client created
pod/client condition met
pod/web condition met
pod/client condition met
NAMESPACE   NAME     READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
team-a      client   1/1     Running   0          8s    10.244.2.7   lab-worker   <none>           <none>
team-a      web      1/1     Running   0          8s    10.244.2.6   lab-worker   <none>           <none>
team-b      client   1/1     Running   0          8s    10.244.2.8   lab-worker   <none>           <none>
```

Pod ของ 2 โซนอยู่บน **เรือลำเดียวกัน** (`lab-worker`)

### ขั้นที่ 2: ก่อนมีรั้ว ข้ามโซนได้

เก็บ IP ของ `web` ไว้ในตัวแปร (IP ในเครื่องนักศึกษาต่างจากเอกสาร ใช้ `$WEB_IP` แทนการพิมพ์เลขเอง)

```bash
WEB_IP=$(kubectl get pod web -n team-a -o jsonpath='{.status.podIP}'); echo $WEB_IP
kubectl -n team-b exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
kubectl -n team-a exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
```

```text
10.244.2.6
<title>Welcome to nginx!</title>
<title>Welcome to nginx!</title>
```

ทั้ง `team-b` และ `team-a` เข้าเว็บได้เหมือนกัน (`-T 3` = รอไม่เกิน 3 วินาที)

### ขั้นที่ 3: search domain ของแต่ละโซน

```bash
kubectl -n team-b exec client -- cat /etc/resolv.conf
kubectl -n team-a exec client -- cat /etc/resolv.conf
```

```text
search team-b.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
search team-a.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

เครือข่ายไม่ได้แยก แต่ **ชื่อ DNS แยกตามโซน** บรรทัด `search` ขึ้นต้นด้วยชื่อ namespace ของ Pod เอง (ทฤษฎีหัวข้อ 9.2)

### ขั้นที่ 4: สร้างรั้วรอบ team-a

<p align="center" id="fig-8">
  <img src="images/08-lab4-networkpolicy-blocks.png" alt="รูปที่ 8 LAB 4 NetworkPolicy กั้นแล้วเปิดประตู" width="900"><br>
  <em><b>รูปที่ 8</b> LAB4: ใส่ NetworkPolicy ให้ team-a รับเฉพาะ Pod ในโซนตัวเอง team-b ได้ download timed out จากนั้นเปิดประตูให้ team-b ด้วย namespaceSelector</em>
</p>

```bash
cat labs/lab04-network/np-same-ns.yaml
kubectl apply -f labs/lab04-network/np-same-ns.yaml
kubectl get netpol -n team-a
time kubectl -n team-b exec client -- wget -qO- -T 3 http://$WEB_IP
kubectl -n team-a exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
kubectl -n blue exec snack -- wget -qO- -T 3 http://$WEB_IP
```

```yaml
# LAB 4 (รั้วที่ 1): ทุก Pod ใน team-a รับการเชื่อมต่อเข้าเฉพาะจาก Pod ในโซน team-a เอง
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: team-a
spec:
  podSelector: {}                # {} = เลือกทุก Pod ในโซนนี้ → Pod เหล่านี้เปลี่ยนเป็น "ปฏิเสธ ยกเว้นที่อนุญาต"
  policyTypes: ["Ingress"]       # คุมเฉพาะขาเข้า
  ingress:
    - from:
        - podSelector: {}        # podSelector อย่างเดียว (ไม่มี namespaceSelector) = Pod ในโซนเดียวกันเท่านั้น
```

```text
networkpolicy.networking.k8s.io/allow-same-namespace created
NAME                   POD-SELECTOR   AGE
allow-same-namespace   <none>         0s
wget: download timed out
command terminated with exit code 1

real	0m3.060s
user	0m0.029s
sys	0m0.025s
<title>Welcome to nginx!</title>
wget: download timed out
command terminated with exit code 1
```

- รั้วมีผล **ทันที** (คำสั่งแรกหลัง apply ก็ถูกกั้นแล้ว) kindnet ของ kind บังคับใช้ NetworkPolicy จริง
- `team-b` รอครบ 3 วินาทีแล้ว `download timed out` เพราะ packet ถูกทิ้งเงียบ ๆ (ไม่มีข้อความปฏิเสธกลับมา)
- `team-a/client` ยังเข้าได้ และ `blue/snack` จากโซนอื่นก็ถูกกั้นเช่นกัน
- คอลัมน์ `POD-SELECTOR` แสดง `<none>` สำหรับ `podSelector: {}` (หมายถึงทุก Pod ไม่ใช่ไม่มี Pod)

### ขั้นที่ 5: เปิดประตูให้ team-b เข้า web

```bash
cat labs/lab04-network/np-allow-team-b.yaml
kubectl apply -f labs/lab04-network/np-allow-team-b.yaml
for i in 1 2 3 4 5 6 7 8 9 10; do if kubectl -n team-b exec client -- wget -qO- -T 2 http://$WEB_IP >/dev/null 2>&1; then echo "team-b เข้าได้ในรอบที่ $i"; break; fi; sleep 1; done
kubectl -n team-b exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
kubectl -n blue exec snack -- wget -qO- -T 3 http://$WEB_IP
kubectl -n team-b exec client -- wget -qO- -T 3 http://$(kubectl get pod client -n team-a -o jsonpath='{.status.podIP}'):80
```

```yaml
# LAB 4 (ประตูที่ 2): เปิดให้ทุก Pod จากโซนที่มี label kubernetes.io/metadata.name=team-b เข้า web ได้
# policy รวมกันแบบ OR: ผ่านข้อใดข้อหนึ่งก็เข้าได้
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-team-b
  namespace: team-a
spec:
  podSelector:
    matchLabels:
      app: web                   # ใช้กับ Pod web เท่านั้น
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: team-b   # label ที่ระบบใส่ให้ทุก namespace อัตโนมัติ
```

```text
networkpolicy.networking.k8s.io/allow-from-team-b created
team-b เข้าได้ในรอบที่ 1
<title>Welcome to nginx!</title>
wget: download timed out
command terminated with exit code 1
wget: download timed out
command terminated with exit code 1
```

`team-b` กลับมาเข้า `web` ได้ทันที แต่ `blue` ยังถูกกั้น และ `team-b` ยังเข้า `client` ของ `team-a` ไม่ได้ เพราะประตูที่ 2 เลือกเฉพาะ Pod `app=web`

### ขั้นที่ 6: อ่าน policy ทั้งสอง

```bash
kubectl get netpol -n team-a
kubectl describe netpol -n team-a
```

```text
NAME                   POD-SELECTOR   AGE
allow-from-team-b      app=web        7s
allow-same-namespace   <none>         13s
Name:         allow-from-team-b
Namespace:    team-a
Created on:   2026-10-04 20:30:34 +0700 +07
Labels:       <none>
Annotations:  <none>
Spec:
  PodSelector:     app=web
  Allowing ingress traffic:
    To Port: <any> (traffic allowed to all ports)
    From:
      NamespaceSelector: kubernetes.io/metadata.name=team-b
  Not affecting egress traffic
  Policy Types: Ingress


Name:         allow-same-namespace
Namespace:    team-a
...
Spec:
  PodSelector:     <none> (Allowing the specific traffic to all pods in this namespace)
  Allowing ingress traffic:
    To Port: <any> (traffic allowed to all ports)
    From:
      PodSelector: <none>
  Not affecting egress traffic
  Policy Types: Ingress
```

### สิ่งที่เห็น

- Pod ต่าง namespace อยู่บนเรือลำเดียวกันได้ และคุยกันด้วย Pod IP ได้ทันทีถ้าไม่มี NetworkPolicy
- `/etc/resolv.conf` ของแต่ละ Pod มี search domain ตาม namespace ของตัวเอง
- `allow-same-namespace` เปลี่ยน Pod ทุกตัวใน `team-a` เป็น "ปฏิเสธยกเว้นที่อนุญาต" ผู้ถูกกั้นได้ `download timed out`
- policy รวมกันแบบ OR: `web` รับจาก team-a (policy 1) หรือ team-b (policy 2) ส่วน `client` ของ team-a รับแค่ team-a

| ผู้เรียก → ปลายทาง | ก่อน policy | หลัง `allow-same-namespace` | หลัง `allow-from-team-b` |
|---|:---:|:---:|:---:|
| `team-a/client` → `team-a/web` | ✅ | ✅ | ✅ |
| `team-b/client` → `team-a/web` | ✅ | ❌ timed out | ✅ |
| `blue/snack` → `team-a/web` | (ไม่ได้ทดสอบ) | ❌ timed out | ❌ timed out |
| `team-b/client` → `team-a/client` | (ไม่ได้ทดสอบ) | (ไม่ได้ทดสอบ) | ❌ timed out |

> **🤔 คำถามชวนคิด:** ถ้าลบ `allow-same-namespace` ออกแต่เก็บ `allow-from-team-b` ไว้ `team-a/client` จะยังเข้า `web` ได้ไหม และ `blue/snack` จะเข้า `team-a/client` ได้ไหม (ลองทำนายก่อนทดลอง)

**เก็บกวาด:** เก็บ `team-a` และ `team-b` (รวม Pod และ policy) ไว้ใช้ใน LAB 7 ถ้าจะหยุดที่ LAB นี้ ให้ `kubectl delete ns team-a team-b`

---

## LAB 5: ResourceQuota: งบของโซน

<p align="center" id="fig-9">
  <img src="images/09-lab5-quota-rejects.png" alt="รูปที่ 9 LAB 5 ใบงบของโซน budget" width="900"><br>
  <em><b>รูปที่ 9</b> LAB5: ใบงบของโซน budget กำหนด pods: 3 Pod ที่ไม่ระบุ resources ถูกปฏิเสธ และ Pod ตัวที่ 4 ชนเพดาน exceeded quota</em>
</p>

**เป้าหมาย:** ตั้งงบให้โซน `budget` แล้วเห็นการปฏิเสธ 2 แบบ คือ Pod ที่ไม่ระบุขนาด (`must specify`) และ Pod ที่ทำให้เกินงบ (`exceeded quota`)

**ไฟล์:** `labs/lab05-quota/quota.yaml` (namespace `budget` + ResourceQuota `budget-quota`), `no-request-pod.yaml` (busybox ไม่มี resources), `small-pods.yaml` (busybox 4 ตัว ตัวละ requests 100m/64Mi, limits 200m/128Mi)

```yaml
# LAB 5: โซน budget + ใบงบประมาณ (ResourceQuota) ของโซน
apiVersion: v1
kind: Namespace
metadata:
  name: budget
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: budget-quota
  namespace: budget
spec:
  hard:
    pods: "3"                    # Pod ได้ไม่เกิน 3 ตัว
    requests.cpu: 500m           # ผลรวม requests ของทุก Pod ในโซน
    requests.memory: 256Mi
    limits.cpu: "1"              # ผลรวม limits ของทุก Pod ในโซน
    limits.memory: 512Mi
```

> คำนวณก่อนลงมือ: Pod เล็ก 4 ตัวรวมกันขอ requests 400m/256Mi และ limits 800m/512Mi ซึ่ง **ยังไม่เกินงบ CPU/หน่วยความจำ** ตัวที่ 4 จึงควรชนแค่ `pods: 3`

### ขั้นที่ 1: สร้างโซนและใบงบ

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab05-quota/quota.yaml
kubectl describe quota -n budget
kubectl get quota -n budget
```

```text
namespace/budget created
resourcequota/budget-quota created
Name:            budget-quota
Namespace:       budget
Resource         Used  Hard
--------         ----  ----
limits.cpu       0     1
limits.memory    0     512Mi
pods             0     3
requests.cpu     0     500m
requests.memory  0     256Mi
NAME           REQUEST                                                     LIMIT                                     AGE
budget-quota   pods: 0/3, requests.cpu: 0/500m, requests.memory: 0/256Mi   limits.cpu: 0/1, limits.memory: 0/512Mi   0s
```

### ขั้นที่ 2: Pod ที่ไม่ระบุขนาด

```bash
kubectl apply -f labs/lab05-quota/no-request-pod.yaml
```

```text
Error from server (Forbidden): error when creating "labs/lab05-quota/no-request-pod.yaml": pods "no-request" is forbidden: failed quota: budget-quota: must specify limits.cpu for: app; limits.memory for: app; requests.cpu for: app; requests.memory for: app
```

### ขั้นที่ 3: Pod เล็ก 4 ตัว

```bash
kubectl apply -f labs/lab05-quota/small-pods.yaml
kubectl get pods -n budget
kubectl describe quota -n budget
```

```text
pod/small-1 created
pod/small-2 created
pod/small-3 created
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-4" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
NAME      READY   STATUS              RESTARTS   AGE
small-1   0/1     ContainerCreating   0          0s
small-2   0/1     ContainerCreating   0          0s
small-3   0/1     ContainerCreating   0          0s
Name:            budget-quota
Namespace:       budget
Resource         Used   Hard
--------         ----   ----
limits.cpu       600m   1
limits.memory    384Mi  512Mi
pods             3      3
requests.cpu     300m   500m
requests.memory  192Mi  256Mi
```

### ขั้นที่ 4: ภาพรวมของโซน

```bash
kubectl describe ns budget
```

```text
Name:         budget
Labels:       kubernetes.io/metadata.name=budget
Annotations:  <none>
Status:       Active

Resource Quotas
  Name:            budget-quota
  Resource         Used   Hard
  --------         ---    ---
  limits.cpu       600m   1
  limits.memory    384Mi  512Mi
  pods             3      3
  requests.cpu     300m   500m
  requests.memory  192Mi  256Mi

No LimitRange resource.
```

### สิ่งที่เห็น

- quota ตรวจ **ตอนสร้าง** Pod ที่ไม่ผ่านถูกปฏิเสธทันที ไม่ได้ค้าง Pending (`small-4` ไม่มีใน `kubectl get pods` เลย)
- Pod ที่ไม่ระบุ resources ถูกปฏิเสธพร้อมรายชื่อค่าที่ขาดครบ 4 ค่าและชื่อ container (`app`)
- `small-4` ชนแค่ `pods` ตามที่คำนวณไว้ ข้อความ `exceeded quota` บอก requested / used / limited
- Used ของ CPU/หน่วยความจำ = ผลรวมของ 3 Pod (300m/192Mi และ 600m/384Mi)

> **🤔 คำถามชวนคิด:** ถ้าแก้ quota เป็น `pods: "10"` แต่คงค่าอื่นไว้ Pod เล็กจะสร้างได้สูงสุดกี่ตัว ค่าไหนจะชนก่อน

**เก็บกวาด:** เก็บ `budget` ไว้ใช้ต่อใน LAB 6 ทันที (ถ้าจะหยุดที่นี่ `kubectl delete ns budget`)

---

## LAB 6: LimitRange: กฎขนาดกล่อง

<p align="center" id="fig-10">
  <img src="images/10-lab6-limitrange-stickers.png" alt="รูปที่ 10 LAB 6 LimitRange เติมค่าและกันกล่องใหญ่" width="900"><br>
  <em><b>รูปที่ 10</b> LAB6: เพิ่ม LimitRange ให้โซน budget Pod ที่ไม่ระบุ resources ได้ค่า default อัตโนมัติ ส่วน Pod ที่ขอ cpu เกิน max ถูกปฏิเสธ</em>
</p>

**เป้าหมาย:** เพิ่ม LimitRange ให้โซน `budget` แล้วเห็นว่า Pod ที่ไม่ระบุ resources ได้ค่าตั้งต้นและผ่าน quota ได้ ส่วน Pod ที่ขอเกิน `max` ถูกปฏิเสธ

**ต้องมีจาก LAB 5:** namespace `budget` ที่มี `small-1`, `small-2`, `small-3`

**ไฟล์:** `labs/lab06-limitrange/limitrange.yaml`, `plain-pod.yaml` (Pod ไม่ระบุ resources ชื่อ `plain`), `big-pod.yaml` (ขอ `limits.cpu: "1"`)

```yaml
# LAB 6: ป้ายกฎขนาดกล่องของโซน budget (ใช้กับแต่ละ container)
apiVersion: v1
kind: LimitRange
metadata:
  name: box-size
  namespace: budget
spec:
  limits:
    - type: Container
      defaultRequest:            # ไม่ระบุ requests → เติมค่านี้ให้
        cpu: 100m
        memory: 64Mi
      default:                   # ไม่ระบุ limits → เติมค่านี้ให้
        cpu: 200m
        memory: 128Mi
      max:                       # ห้าม limits เกินค่านี้ (ต่อ container)
        cpu: 500m
        memory: 256Mi
```

### ขั้นที่ 1: คืนที่ว่างในงบ แล้วติดป้ายกฎขนาดกล่อง

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl delete pod small-2 small-3 -n budget
kubectl apply -f labs/lab06-limitrange/limitrange.yaml
kubectl describe limitrange -n budget
```

```text
pod "small-2" deleted from budget namespace
pod "small-3" deleted from budget namespace
limitrange/box-size created
Name:       box-size
Namespace:  budget
Type        Resource  Min  Max    Default Request  Default Limit  Max Limit/Request Ratio
----        --------  ---  ---    ---------------  -------------  -----------------------
Container   memory    -    256Mi  64Mi             128Mi          -
Container   cpu       -    500m   100m             200m           -
```

### ขั้นที่ 2: Pod ที่ไม่ระบุขนาด คราวนี้ผ่าน

```bash
kubectl apply -f labs/lab05-quota/no-request-pod.yaml
kubectl get pod no-request -n budget -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
kubectl get pod no-request -n budget -o jsonpath="{.metadata.annotations.kubernetes\.io/limit-ranger}{\"\n\"}"
kubectl apply -f labs/lab06-limitrange/plain-pod.yaml
kubectl get pod plain -n budget -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
```

```text
pod/no-request created
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
LimitRanger plugin set: cpu, memory request for container app; cpu, memory limit for container app
pod/plain created
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
```

ไฟล์ `no-request-pod.yaml` ตัวเดียวกับที่ถูกปฏิเสธใน LAB 5 คราวนี้ผ่าน เพราะ LimitRange เติมค่าให้ก่อนถึงด่าน quota

### ขั้นที่ 3: กล่องใหญ่เกิน max

```bash
kubectl apply -f labs/lab06-limitrange/big-pod.yaml
kubectl get pods -n budget
kubectl describe quota -n budget
```

```text
Error from server (Forbidden): error when creating "labs/lab06-limitrange/big-pod.yaml": pods "big" is forbidden: maximum cpu usage per Container is 500m, but limit is 1
NAME         READY   STATUS              RESTARTS   AGE
no-request   1/1     Running             0          1s
plain        0/1     ContainerCreating   0          1s
small-1      1/1     Running             0          10s
Name:            budget-quota
Namespace:       budget
Resource         Used   Hard
--------         ----   ----
limits.cpu       600m   1
limits.memory    384Mi  512Mi
pods             3      3
requests.cpu     300m   500m
requests.memory  192Mi  256Mi
```

สังเกตว่าตอนนี้ `pods` เต็ม 3/3 แล้ว แต่ `big` ได้ข้อความของ **LimitRange** ไม่ใช่ `exceeded quota` เพราะ LimitRanger ตรวจก่อน quota

### ขั้นที่ 4: ทั้งสองด่านในภาพเดียว

```bash
kubectl apply -f labs/lab05-quota/small-pods.yaml
kubectl describe ns budget
```

```text
pod/small-1 unchanged
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-2" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-3" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-4" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
Name:         budget
Labels:       kubernetes.io/metadata.name=budget
Annotations:  <none>
Status:       Active

Resource Quotas
  Name:            budget-quota
  Resource         Used   Hard
  --------         ---    ---
  limits.cpu       600m   1
  limits.memory    384Mi  512Mi
  pods             3      3
  requests.cpu     300m   500m
  requests.memory  192Mi  256Mi

Resource Limits
 Type       Resource  Min  Max    Default Request  Default Limit  Max Limit/Request Ratio
 ----       --------  ---  ---    ---------------  -------------  -----------------------
 Container  memory    -    256Mi  64Mi             128Mi          -
 Container  cpu       -    500m   100m             200m           -
```

### สิ่งที่เห็น

- Pod ที่ไม่ระบุ resources ได้ requests 100m/64Mi และ limits 200m/128Mi จาก LimitRange พร้อม annotation `kubernetes.io/limit-ranger`
- LimitRange + quota ทำงานคู่กัน: LimitRange เติมค่าให้ Pod ที่ลืม จึงผ่านเงื่อนไข `must specify` ของ quota
- `max` บังคับต่อ container และถูกตรวจก่อน quota
- `kubectl describe ns` แสดงทั้ง `Resource Quotas` และ `Resource Limits` ของโซน

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `default.memory` ของ LimitRange เป็น 256Mi แล้วสร้าง Pod ไม่ระบุ resources เพิ่ม (หลังลบให้ `pods` ว่าง) ค่า `limits.memory` ของ quota จะหมดเร็วขึ้นแค่ไหน การตั้งค่า default สูงหรือต่ำเกินไปมีผลเสียอย่างไร

**เก็บกวาด:** `kubectl delete ns budget` (หรือเก็บไว้ลบรวมใน LAB 9)

---

## LAB 7: RBAC: บัตรพนักงานเฉพาะโซน

<p align="center" id="fig-11">
  <img src="images/11-lab7-intern-badge.png" alt="รูปที่ 11 LAB 7 บัตร intern ของ team-a" width="900"><br>
  <em><b>รูปที่ 11</b> LAB7: ServiceAccount intern + Role pod-reader + RoleBinding ใน team-a ตรวจด้วย auth can-i --as ได้ yes เฉพาะการดู</em>
</p>

**เป้าหมาย:** สร้าง ServiceAccount + Role + RoleBinding ตรวจสิทธิ์ด้วย `kubectl auth can-i --as` ใช้ ClusterRole สำเร็จรูปในโซนเดียว และใช้ token ของ ServiceAccount จริงผ่าน context ใหม่ พร้อมเห็นกับดัก `--token`

**ต้องมีจาก LAB 4:** namespace `team-a` (Pod `web`, `client`) และ `team-b` (Pod `client`)

**ไฟล์:** `labs/lab07-rbac/sa-role-binding.yaml` (ใน `team-a`: SA `intern`, Role `pod-reader` = get/list/watch บน `pods`, `pods/log`, RoleBinding `intern-pod-reader`) และ `view-clusterrole-binding.yaml` (ใน `team-b`: SA `auditor` + RoleBinding `auditor-view` ที่อ้าง ClusterRole `view`)

```yaml
# LAB 7: ใช้สมุดกฎมาตรฐานของท่าเรือ (ClusterRole "view") แต่ผูกด้วย RoleBinding → มีผลแค่โซน team-b
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auditor
  namespace: team-b
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: auditor-view
  namespace: team-b
subjects:
  - kind: ServiceAccount
    name: auditor
    namespace: team-b
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole              # ClusterRole สำเร็จรูป: view (ดูได้เกือบทุกอย่าง ยกเว้น Secret)
  name: view
```

(เนื้อหาของ `sa-role-binding.yaml` ดูทฤษฎีหัวข้อ 13.2 หรือ `cat labs/lab07-rbac/sa-role-binding.yaml`)

### ขั้นที่ 1: เราเป็นใคร และสร้างบัตร

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl auth whoami
kubectl apply -f labs/lab07-rbac/sa-role-binding.yaml -f labs/lab07-rbac/view-clusterrole-binding.yaml
kubectl get sa,role,rolebinding -n team-a
kubectl get sa,rolebinding -n team-b -o wide
```

```text
ATTRIBUTE                                           VALUE
Username                                            kubernetes-admin
Groups                                              [kubeadm:cluster-admins system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [X509SHA256=ac241dd4...]
serviceaccount/intern created
role.rbac.authorization.k8s.io/pod-reader created
rolebinding.rbac.authorization.k8s.io/intern-pod-reader created
serviceaccount/auditor created
rolebinding.rbac.authorization.k8s.io/auditor-view created
NAME                     AGE
serviceaccount/default   51s
serviceaccount/intern    1s

NAME                                        CREATED AT
role.rbac.authorization.k8s.io/pod-reader   2026-10-04T13:31:09Z

NAME                                                      ROLE              AGE
rolebinding.rbac.authorization.k8s.io/intern-pod-reader   Role/pod-reader   1s
NAME                     AGE
serviceaccount/auditor   1s
serviceaccount/default   51s

NAME                                                 ROLE               AGE   USERS   GROUPS   SERVICEACCOUNTS
rolebinding.rbac.authorization.k8s.io/auditor-view   ClusterRole/view   1s                     team-b/auditor
```

(ค่า `X509SHA256` ตัดให้สั้น) เราคือ `kubernetes-admin` ในกลุ่ม `kubeadm:cluster-admins` ทำได้ทุกอย่าง และทุก namespace มี SA `default` อยู่แล้ว

### ขั้นที่ 2: ตรวจสิทธิ์ intern ด้วยเครื่องอ่านบัตร

```bash
kubectl auth can-i list pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i delete pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i get pods/log -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i list pods -n team-b --as=system:serviceaccount:team-a:intern
kubectl auth can-i create pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i --list -n team-a --as=system:serviceaccount:team-a:intern | head -6
```

```text
yes
no
yes
no
no
Resources                                       Non-Resource URLs                      Resource Names   Verbs
selfsubjectreviews.authentication.k8s.io        []                                     []               [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []               [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []               [create]
pods/log                                        []                                     []               [get list watch]
pods                                            []                                     []               [get list watch]
```

คำตอบ `no` ทำให้คำสั่งคืนค่า exit code 1 (ใช้ในสคริปต์ได้) และรายการ `--list` แสดงสิทธิ์จาก Role ของเรา (`pods`, `pods/log`) รวมกับสิทธิ์พื้นฐานที่ทุกคนได้ (ถามว่าตัวเองเป็นใคร/ทำอะไรได้)

### ขั้นที่ 3: ลงมือจริงในบทบาท intern และ auditor

```bash
kubectl delete pod web -n team-a --as=system:serviceaccount:team-a:intern
kubectl get pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl logs web -n team-a --tail=2 --as=system:serviceaccount:team-a:intern
kubectl auth can-i list pods -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i list configmaps -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i list secrets -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i delete pods -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i list pods -n team-a --as=system:serviceaccount:team-b:auditor
kubectl get pods -n team-a --as=system:serviceaccount:team-b:auditor
```

```text
Error from server (Forbidden): pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          52s
web      1/1     Running   0          52s
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
yes
yes
no
no
no
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:team-b:auditor" cannot list resource "pods" in API group "" in the namespace "team-a"
```

log ของ nginx แสดงคำขอจาก `10.244.2.8` (IP ของ `team-b/client` ใน LAB 4) ส่วน `auditor` ดูได้ทั้ง Pod และ ConfigMap ใน team-b แต่อ่าน Secret ไม่ได้ ลบไม่ได้ และมองไม่เห็น team-a

### ขั้นที่ 4: กับดัก --token

<p align="center" id="fig-12">
  <img src="images/12-lab7-token-context.png" alt="รูปที่ 12 LAB 7 --token กับ context ใหม่" width="900"><br>
  <em><b>รูปที่ 12</b> LAB7: kubectl --token ยังใช้บัตร admin เดิม ต้องสร้าง context ใหม่ที่มีแต่ token ของ intern จึงเห็นสิทธิ์จริงของ intern</em>
</p>

ขอ token อายุ 1 ชั่วโมงของ intern แล้วลองส่งด้วย `--token`

```bash
T=$(kubectl create token intern -n team-a --duration=1h)
echo "token ยาว ${#T} ตัวอักษร ขึ้นต้น ${T:0:10}..."
kubectl --token=$T get pods -n team-b
kubectl --token=$T auth whoami
```

```text
token ยาว 925 ตัวอักษร ขึ้นต้น eyJhbGciOi...
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          53s
ATTRIBUTE                                           VALUE
Username                                            kubernetes-admin
Groups                                              [kubeadm:cluster-admins system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [X509SHA256=ac241dd4...]
```

ยังเห็น team-b และยังเป็น `kubernetes-admin` เพราะ user `kind-lab` มี client certificate (LAB 2 ขั้นที่ 4) API server ยืนยันตัวตนจาก certificate ได้ก่อน token จึงไม่ถูกใช้ **อย่า `echo $T` ทั้งก้อน** token คือรหัสผ่านของ intern

### ขั้นที่ 5: context ใหม่ที่มีแต่ token ของ intern

```bash
kubectl config set-credentials intern --token=$T
kubectl config set-context intern@lab --cluster=kind-lab --user=intern --namespace=team-a
kubectl config get-contexts
kubectl --context intern@lab auth whoami
kubectl --context intern@lab get pods
kubectl --context intern@lab logs web --tail=3
```

```text
User "intern" set.
Context "intern@lab" created.
CURRENT   NAME         CLUSTER    AUTHINFO   NAMESPACE
          intern@lab   kind-lab   intern     team-a
*         kind-lab     kind-lab   kind-lab   default
ATTRIBUTE                                           VALUE
Username                                            system:serviceaccount:team-a:intern
UID                                                 14329203-56ac-41c3-8758-19d9d0aadd74
Groups                                              [system:serviceaccounts system:serviceaccounts:team-a system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [JTI=9e870e3d-...]
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          54s
web      1/1     Running   0          54s
10.244.2.7 - - [04/Oct/2026:13:30:31 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
```

context `intern@lab` ไม่ใช่ context ปัจจุบัน (ไม่มี `*`) เราเลือกใช้ทีละคำสั่งด้วย `--context` จึงไม่กระทบคำสั่งอื่น ลองสิ่งที่ intern ไม่ควรทำได้

```bash
kubectl --context intern@lab delete pod web
kubectl --context intern@lab get pods -n team-b
kubectl --context intern@lab get nodes
kubectl --context intern@lab get ns
kubectl --context intern@lab exec web -- id
```

```text
Error from server (Forbidden): pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:team-a:intern" cannot list resource "pods" in API group "" in the namespace "team-b"
Error from server (Forbidden): nodes is forbidden: User "system:serviceaccount:team-a:intern" cannot list resource "nodes" in API group "" at the cluster scope
Error from server (Forbidden): namespaces is forbidden: User "system:serviceaccount:team-a:intern" cannot list resource "namespaces" in API group "" at the cluster scope
error: unable to upgrade connection: pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot create resource "pods/exec" in API group "" in the namespace "team-a"
```

ข้อความของ Node และ namespace ลงท้าย `at the cluster scope` เพราะเป็นของส่วนกลาง และ `exec` ต้องการสิทธิ์ `create` บน `pods/exec` ซึ่ง Role ไม่ได้ให้

### สิ่งที่เห็น

- ServiceAccount + Role + RoleBinding ทำให้ intern ดูและอ่าน log ได้เฉพาะ `team-a` ลบ, สร้าง, exec และดูโซนอื่นไม่ได้
- ClusterRole `view` + RoleBinding ใน `team-b` ทำให้ auditor อ่านได้เฉพาะ `team-b` และไม่รวม Secret
- `kubectl auth can-i --as` และคำสั่งจริงที่ใส่ `--as` ให้ผลตรงกัน
- `kubectl --token` บน kubeconfig ของ kind **ยังเป็น admin** ต้องสร้าง user + context ใหม่ที่มีแต่ token จึงเห็นสิทธิ์จริงของ intern

> **🤔 คำถามชวนคิด:** ถ้าอยากให้ intern ใช้ `kubectl exec` เข้า Pod ใน team-a ได้ด้วย ต้องเพิ่มกฎอะไรใน Role (บอก resource และ verb) และควรให้สิทธิ์นี้กับเด็กฝึกงานหรือไม่ เพราะอะไร

**เก็บกวาด (ต้องทำ):** ลบ context และ user ของ intern ออกจาก kubeconfig แล้วยืนยันว่ายังใช้ `kind-lab`

```bash
kubectl config current-context
kubectl config delete-context intern@lab
kubectl config delete-user intern
unset T
kubectl config get-contexts
```

```text
kind-lab
deleted context intern@lab from /root/.kube/config
deleted user intern from /root/.kube/config
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
```

namespace `team-a`/`team-b` จะลบรวมใน LAB 9 (หรือ `kubectl delete ns team-a team-b` ตอนนี้ก็ได้)

---

## LAB 8: Pod Security Admission: ด่านตรวจหน้าโซน

<p align="center" id="fig-13">
  <img src="images/13-lab8-psa-gate.png" alt="รูปที่ 13 LAB 8 ด่านตรวจ restricted" width="900"><br>
  <em><b>รูปที่ 13</b> LAB8: namespace secure เริ่มที่ baseline + warn restricted แล้วเปลี่ยนเป็น enforce restricted: nginx ที่รันเป็น root ถูกปฏิเสธ แต่ busybox ที่ตั้ง securityContext ครบผ่าน</em>
</p>

**เป้าหมาย:** ตั้งด่านตรวจของ namespace ด้วย label เห็นผลของ `warn` และ `enforce` ในระดับ baseline และ restricted เปลี่ยนระดับอย่างปลอดภัยด้วย `--dry-run=server` และทำ Pod ให้ผ่าน restricted

**ไฟล์:** `labs/lab08-psa/root-nginx-pod.yaml` (nginx ทางการ ไม่มี securityContext), `privileged-pod.yaml` (busybox `privileged: true`), `restricted-ok-pod.yaml` (busybox ที่ตั้ง securityContext ครบ ดูทฤษฎีหัวข้อ 14.4)

### ขั้นที่ 1: สร้างโซน secure ระดับ baseline + เตือน restricted

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl create ns secure
kubectl label ns secure pod-security.kubernetes.io/enforce=baseline pod-security.kubernetes.io/warn=restricted
kubectl get ns secure --show-labels
```

```text
namespace/secure created
namespace/secure labeled
NAME     STATUS   AGE   LABELS
secure   Active   1s    kubernetes.io/metadata.name=secure,pod-security.kubernetes.io/enforce=baseline,pod-security.kubernetes.io/warn=restricted
```

### ขั้นที่ 2: nginx ที่รันเป็น root และ Pod ที่ขอ privileged

```bash
kubectl apply -f labs/lab08-psa/root-nginx-pod.yaml
kubectl apply -f labs/lab08-psa/privileged-pod.yaml
kubectl wait --for=condition=Ready pod/root-nginx -n secure --timeout=60s
kubectl exec -n secure root-nginx -- id
```

```text
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/root-nginx created
Error from server (Forbidden): error when creating "labs/lab08-psa/privileged-pod.yaml": pods "privileged" is forbidden: violates PodSecurity "baseline:latest": privileged (container "app" must not set securityContext.privileged=true)
pod/root-nginx condition met
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
```

- `root-nginx` **ผ่าน** ด่าน baseline (enforce) แต่ได้ **Warning** จากกระดิ่ง restricted (warn) 4 ข้อ และรันเป็น `uid=0(root)` จริง
- `privileged` ถูกด่าน baseline **ปฏิเสธ**

### ขั้นที่ 3: ลองยกระดับเป็น restricted แบบไม่บังคับจริงก่อน

```bash
kubectl label --dry-run=server --overwrite ns secure pod-security.kubernetes.io/enforce=restricted
kubectl get ns secure --show-labels
```

```text
Warning: existing pods in namespace "secure" violate the new PodSecurity enforce level "restricted:latest"
Warning: root-nginx: allowPrivilegeEscalation != false, unrestricted capabilities, runAsNonRoot != true, seccompProfile
namespace/secure labeled (server dry run)
NAME     STATUS   AGE   LABELS
secure   Active   2s    kubernetes.io/metadata.name=secure,pod-security.kubernetes.io/enforce=baseline,pod-security.kubernetes.io/warn=restricted
```

dry-run บอกล่วงหน้าว่า Pod เดิมตัวไหนจะผิดกฎ และ label ยังเป็น `enforce=baseline` เหมือนเดิม

### ขั้นที่ 4: บังคับ restricted จริง

```bash
kubectl label --overwrite ns secure pod-security.kubernetes.io/enforce=restricted
kubectl get pods -n secure
kubectl run root-nginx-2 -n secure --image=nginx:1.27-alpine
```

```text
Warning: existing pods in namespace "secure" violate the new PodSecurity enforce level "restricted:latest"
Warning: root-nginx: allowPrivilegeEscalation != false, unrestricted capabilities, runAsNonRoot != true, seccompProfile
namespace/secure labeled
NAME         READY   STATUS    RESTARTS   AGE
root-nginx   1/1     Running   0          1s
Error from server (Forbidden): pods "root-nginx-2" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "root-nginx-2" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "root-nginx-2" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "root-nginx-2" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "root-nginx-2" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

`root-nginx` เดิม **ยัง Running** (PSA ตรวจเฉพาะตอนสร้าง) แต่ nginx ตัวใหม่แบบเดียวกันถูกปฏิเสธ

### ขั้นที่ 5: Pod ที่ผ่าน restricted

```bash
cat labs/lab08-psa/restricted-ok-pod.yaml
kubectl apply -f labs/lab08-psa/restricted-ok-pod.yaml
kubectl wait --for=condition=Ready pod/restricted-ok -n secure --timeout=60s
kubectl exec -n secure restricted-ok -- id
kubectl get ns secure --show-labels
```

```text
pod/restricted-ok created
pod/restricted-ok condition met
uid=1000 gid=1000 groups=1000
NAME     STATUS   AGE   LABELS
secure   Active   3s    kubernetes.io/metadata.name=secure,pod-security.kubernetes.io/enforce=restricted,pod-security.kubernetes.io/warn=restricted
```

ไม่มี Warning เลย และรันเป็น uid/gid 1000 (ถ้าลบ `runAsGroup: 1000` ออกจากไฟล์ จะได้ `uid=1000 gid=0(root) groups=0(root)` ซึ่ง restricted ยอม แต่ไม่ควร)

### สิ่งที่เห็น

- label `pod-security.kubernetes.io/<โหมด>=<ระดับ>` บน namespace คือการตั้งด่าน: `enforce` ปฏิเสธ, `warn` เตือนที่ kubectl
- baseline ยอม nginx ที่รันเป็น root แต่ไม่ยอม `privileged: true` ส่วน restricted ไม่ยอมทั้งคู่
- เปลี่ยนระดับภายหลัง Pod เดิมยังรัน ใช้ `--dry-run=server` ดูผลกระทบก่อน
- ผ่าน restricted ด้วย securityContext 4 เรื่อง: runAsNonRoot (+ runAsUser), allowPrivilegeEscalation false, drop ALL, seccomp RuntimeDefault

> **🤔 คำถามชวนคิด:** ทีม dev อยากใช้ `enforce=restricted` ตั้งแต่วันแรก แต่ image หลายตัวยังรันเป็น root ควรเริ่มด้วยการตั้ง label แบบไหนก่อน และใช้ข้อมูลอะไรตัดสินว่าพร้อมเปลี่ยนเป็น enforce

**เก็บกวาด:** `kubectl delete ns secure` (หรือเก็บไว้ลบรวมใน LAB 9)

---

## LAB 9: ลบโซนทั้งก้อน

<p align="center" id="fig-14">
  <img src="images/14-lab9-delete-zone.png" alt="รูปที่ 14 LAB 9 ลบโซน doomed" width="900"><br>
  <em><b>รูปที่ 14</b> LAB9: kubectl delete ns doomed ทุกอย่างข้างในหายตามไปหมด ระหว่าง Terminating สร้างของใหม่ในโซนนั้นไม่ได้</em>
</p>

**เป้าหมาย:** เห็นว่าลบ namespace = ลบทุกอย่างข้างใน เห็นสถานะ `Terminating` และ finalizer ทดลองสร้างของระหว่างกำลังลบ ตรวจว่า namespace ระบบตัวไหนลบไม่ได้ แล้วเก็บกวาด namespace ของ LAB 1–8 ทั้งหมด

**ไฟล์:** `labs/lab09-delete-ns/doomed.yaml` (namespace `doomed` + ConfigMap `menu` + SA `cleaner` + Role `cleaner-role` + RoleBinding `cleaner-binding` + ResourceQuota `doomed-quota` (`pods: "5"`) + Pod busybox `crate-1`, `crate-2`) Pod ทั้งสองตั้ง `terminationGracePeriodSeconds: 15` (`sleep` เป็น PID 1 ไม่ตอบ SIGTERM จึงรอครบ 15 วินาที) โซนจะค้าง Terminating นานพอให้ทดลอง

### ขั้นที่ 1: สร้างโซนที่มีของหลายชนิด

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab09-delete-ns/doomed.yaml
kubectl wait --for=condition=Ready pod --all -n doomed --timeout=60s
kubectl get all,sa,role,rolebinding,cm,quota -n doomed
kubectl get ns doomed -o jsonpath="{.spec.finalizers}{\"\n\"}"
```

```text
namespace/doomed created
configmap/menu created
serviceaccount/cleaner created
role.rbac.authorization.k8s.io/cleaner-role created
rolebinding.rbac.authorization.k8s.io/cleaner-binding created
resourcequota/doomed-quota created
pod/crate-1 created
pod/crate-2 created
pod/crate-1 condition met
pod/crate-2 condition met
```

ผลของคำสั่งที่สาม (`all` + ชนิดที่ระบุเพิ่ม) ส่วนแรกที่มาจาก `all` มีแค่ Pod ส่วน ServiceAccount, Role, RoleBinding, ConfigMap และ quota ปรากฏเพราะเราระบุชนิดเพิ่มเอง (`all` ไม่ได้แปลว่าทุกชนิด)

```text
NAME          READY   STATUS    RESTARTS   AGE
pod/crate-1   1/1     Running   0          0s
pod/crate-2   1/1     Running   0          0s

NAME                     AGE
serviceaccount/cleaner   0s
serviceaccount/default   0s

NAME                                          CREATED AT
role.rbac.authorization.k8s.io/cleaner-role   2026-10-04T13:31:41Z

NAME                                                    ROLE                AGE
rolebinding.rbac.authorization.k8s.io/cleaner-binding   Role/cleaner-role   1s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      1s
configmap/menu               1      1s

NAME                         REQUEST     LIMIT   AGE
resourcequota/doomed-quota   pods: 2/5           1s
["kubernetes"]
```

### ขั้นที่ 2: สั่งลบแบบไม่รอ แล้วสังเกตระหว่าง Terminating

พิมพ์ชุดนี้ต่อกันเร็ว ๆ (หรือคัดลอกทั้งบล็อก) ต้องทำภายในราว 15 วินาทีหลังสั่งลบ

```bash
kubectl delete ns doomed --wait=false
kubectl get ns doomed
kubectl run x -n doomed --image=busybox:1.36 -- sleep 60
kubectl create configmap late -n doomed --from-literal=a=b
kubectl get pods -n doomed
kubectl get sa,role,rolebinding,cm,quota -n doomed
```

```text
namespace "doomed" deleted
NAME     STATUS        AGE
doomed   Terminating   1s
Error from server (Forbidden): pods "x" is forbidden: unable to create new content in namespace doomed because it is being terminated
error: failed to create configmap: configmaps "late" is forbidden: unable to create new content in namespace doomed because it is being terminated
NAME      READY   STATUS    RESTARTS   AGE
crate-1   1/1     Running   0          1s
crate-2   1/1     Running   0          1s
NAME                     AGE
serviceaccount/cleaner   2s
serviceaccount/default   2s
...
```

- `deleted` แปลว่า "รับคำขอแล้ว" โซนยังอยู่ในสถานะ `Terminating`
- สร้างของใหม่ทุกชนิดไม่ได้ (`unable to create new content ... being terminated`)
- ช่วงแรกของข้างในยังอยู่ครบ controller กำลังทยอยลบ (Pod รอ grace 15 วินาที)

### ขั้นที่ 3: รอจนหายจริง

```bash
time kubectl wait --for=delete ns/doomed --timeout=120s
kubectl get ns
kubectl get nodes
```

```text
namespace/doomed condition met

real	0m20.096s
...
NAME                 STATUS   AGE
blue                 Active   2m28s
budget               Active   76s
default              Active   4m19s
green                Active   2m28s
kube-node-lease      Active   4m19s
kube-public          Active   4m19s
kube-system          Active   4m19s
local-path-storage   Active   4m15s
secure               Active   44s
team-a               Active   104s
team-b               Active   104s
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   4m19s   v1.37.0
lab-worker          Ready    <none>          4m9s    v1.37.0
lab-worker2         Ready    <none>          4m9s    v1.37.0
```

`doomed` หายไปในราว 20 วินาที namespace อื่นและเรือทั้ง 3 ลำไม่กระทบ (รายการ namespace ของนักศึกษาขึ้นกับว่าเก็บกวาด LAB ก่อนหน้าไปแล้วหรือยัง)

### ขั้นที่ 4: namespace ระบบที่ลบไม่ได้ (ทดสอบแบบไม่ลบจริง)

> ⚠️ ใช้ `--dry-run=server` **ทุกบรรทัดยกเว้น `default`** (ซึ่งระบบกันไว้แน่นอน) ห้ามตัด `--dry-run=server` ออกเด็ดขาด

```bash
kubectl delete ns default
kubectl delete ns kube-system --dry-run=server
kubectl delete ns kube-public --dry-run=server
kubectl delete ns kube-node-lease --dry-run=server
```

```text
Error from server (Forbidden): namespaces "default" is forbidden: this namespace may not be deleted
Error from server (Forbidden): namespaces "kube-system" is forbidden: this namespace may not be deleted
Error from server (Forbidden): namespaces "kube-public" is forbidden: this namespace may not be deleted
namespace "kube-node-lease" deleted (server dry run)
```

ระบบกันการลบแค่ `default`, `kube-system`, `kube-public` ส่วน `kube-node-lease` **ผ่าน dry-run = ลบได้จริงถ้าสั่ง** แต่ห้ามลบเพราะเป็นที่เก็บ heartbeat ของเรือทุกลำ

### ขั้นที่ 5: เก็บกวาด namespace ของ LAB 1–8 ในคำสั่งเดียว

```bash
time kubectl delete ns blue green team-a team-b budget secure
kubectl get ns
kubectl config get-contexts
```

```text
namespace "blue" deleted
namespace "green" deleted
namespace "team-a" deleted
namespace "team-b" deleted
namespace "budget" deleted
namespace "secure" deleted

real	0m42.224s
...
NAME                 STATUS   AGE
default              Active   5m6s
kube-node-lease      Active   5m6s
kube-public          Active   5m6s
kube-system          Active   5m6s
local-path-storage   Active   5m2s
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
```

ใช้เวลาราว 42 วินาที เพราะ Pod `blue/peek` จาก LAB 2 สร้างด้วย `kubectl run` (grace period ค่าเริ่มต้น 30 วินาที และ `sleep` ไม่ตอบ SIGTERM) ถ้าลบ namespace บางตัวไปแล้ว kubectl จะแจ้ง `NotFound` สำหรับตัวนั้น ไม่เป็นไร

### สิ่งที่เห็น

- `kubectl delete ns` ลบ Pod, ConfigMap, SA, Role, RoleBinding, quota ทั้งหมดในโซน ส่วน Node และ namespace อื่นไม่กระทบ
- ลำดับ: `Terminating` ทันที → controller ลบของข้างใน (รอ grace ของ Pod) → เอา finalizer `kubernetes` ออก → หายจริง
- ระหว่าง Terminating สร้างของใหม่ไม่ได้
- `kubectl get all` ไม่ได้แสดงทุกชนิด
- ระบบป้องกันการลบ `default`, `kube-system`, `kube-public` แต่ **ไม่กัน** `kube-node-lease`

> **🤔 คำถามชวนคิด:** ถ้า namespace หนึ่งค้าง `Terminating` นานหลายนาที นักศึกษาจะตรวจหาสาเหตุด้วยคำสั่งอะไรบ้าง (ใบ้: ดู `status.conditions` และหาของที่ยังเหลือ ดูทฤษฎีหัวข้อ 8.3)

**เก็บกวาด:** ทำไปแล้วในขั้นที่ 5 ตอนนี้คลัสเตอร์ควรเหลือ namespace ตั้งต้น 5 ตัวและ context อยู่ที่ `default`

---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มแยก environment

<p align="center" id="fig-15">
  <img src="images/15-lab10-opening-three-envs.png" alt="รูปที่ 15 LAB 10 ภาพเปิด ร้านน้องส้ม 3 environment" width="900"><br>
  <em><b>รูปที่ 15</b> LAB สุดท้าย: ร้านอาหารแมวน้องส้มแยกเป็น 3 environment คือ som-dev, som-staging, som-prod ในคลัสเตอร์เดียว ทุกโซนมี Pod ชื่อ som-shop เหมือนกัน</em>
</p>

**เรื่องเล่า:** ร้านอาหารแมวน้องส้มมีทีมพัฒนาที่ลองของใหม่ทุกวัน ทีมทดสอบ และร้านจริงที่ลูกค้าใช้ น้องส้มจะเปิดร้านทั้ง 3 environment ในคลัสเตอร์เดียว แต่ละ environment อยู่ในโซนของตัวเอง ใช้ manifest **ไฟล์เดียว** Pod ชื่อ `som-shop` เหมือนกันทุกโซน หน้าร้านบอกเองว่าอยู่โซนไหน ร้านจริงมีงบ กฎขนาดกล่อง และด่านตรวจระดับ restricted เด็กฝึกงานมีบัตรที่ดูได้อย่างเดียวและเฉพาะโซน dev และสุดท้ายลบโซน dev ทั้งก้อนโดยร้านจริงไม่สะดุด

**เป้าหมาย:** รวมทุกอย่างของบทนี้: namespace + label, manifest เดียวหลาย namespace, Downward API `metadata.namespace`, ResourceQuota + LimitRange + Pod Security `restricted` ใน prod, RBAC ของ intern, port-forward หลาย environment พร้อมกัน และการลบ environment ทั้งก้อน

**ต้องมี:** คลัสเตอร์สะอาดจาก LAB 9 (เหลือ namespace ตั้งต้น 5 ตัว, context อยู่ที่ `default`) และพื้นที่ดิสก์สำหรับ build image ราว 1 GB

### 10.1 สถาปัตยกรรมและไฟล์

| ไฟล์ใน `som-shop-envs/k8s/` | เนื้อหา | มี `metadata.namespace`? |
|---|---|:---:|
| `00-namespaces.yaml` | namespace `som-dev`, `som-staging` (label `env`, `team: som`, `pod-security.kubernetes.io/warn: restricted`) และ `som-prod` (เพิ่ม `enforce: restricted`, `enforce-version: latest`) | – (เป็น Namespace) |
| `prod-guardrails.yaml` | ResourceQuota `prod-budget` (`pods: "2"`, requests 1 CPU/1Gi, limits 2 CPU/2Gi) และ LimitRange `prod-box-size` (defaultRequest 50m/64Mi, default 200m/128Mi, max 1 CPU/1Gi) | ✓ `som-prod` (ของ prod เท่านั้น) |
| `som-shop.yaml` | Pod `som-shop`: sidecar `db` (postgres), init `wait-for-db`, `db-seed` และ `web` (som-shop-web:1.1) พร้อม securityContext ระดับ restricted และ env ที่บอก namespace | ✗ (เลือกด้วย `-n`) |
| `som-shop-v002.yaml` | สำเนาร้านฉบับบทที่ 2 ชื่อ `som-shop-old` ไม่มี securityContext ไว้ลองกับด่านของ prod | ✗ |
| `intern-rbac.yaml` | ใน `som-dev`: SA `intern`, Role `shop-viewer` (`pods`, `pods/log`: get/list/watch), RoleBinding `intern-shop-viewer` | ✓ `som-dev` |

<p align="center" id="fig-16">
  <img src="images/16-lab10-downward-namespace.png" alt="รูปที่ 16 Downward API ส่งชื่อ namespace เข้าหน้าร้าน" width="900"><br>
  <em><b>รูปที่ 16</b> ไฟล์เดียวแต่หน้าร้านแต่ละ env ต่างกัน: Downward API ส่ง metadata.namespace เข้า env POD_NAMESPACE แล้วต่อเป็น SHOP_NAME</em>
</p>

ส่วนสำคัญของ `som-shop.yaml` (ตัดบางส่วน ดูไฟล์เต็มด้วย `cat som-shop-envs/k8s/som-shop.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  # ชื่อเดียวกันได้ทุกโซน (ชื่อเต็ม = <namespace>/som-shop)
  # บรรทัด name ห้ามมีคอมเมนต์ต่อท้าย เพราะ LAB ใช้ sed 's/name: som-shop$/.../' เปลี่ยนชื่อสาขา
  name: som-shop
  labels:
    app: som-shop
spec:
  securityContext:               # ระดับ Pod: ใช้กับทุก container
    runAsNonRoot: true           # ห้ามรันเป็น root
    fsGroup: 70                  # volume (emptyDir) เป็นของกลุ่ม 70 = postgres เขียนได้
    seccompProfile:
      type: RuntimeDefault
  # ... (ตัด)
  initContainers:
    - name: db
      image: postgres:17.11-alpine
      restartPolicy: Always
      securityContext:
        runAsUser: 70            # uid ของ postgres ใน image alpine
        runAsGroup: 70
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
      # ... (ตัด)
  containers:
    - name: web
      image: som-shop-web:1.1
      imagePullPolicy: IfNotPresent
      securityContext:
        runAsUser: 1000          # image ระบุ USER node เป็นชื่อ จึงต้องใส่ตัวเลข
        runAsGroup: 1000
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
      env:
        - name: POD_NAMESPACE      # Downward API: namespace ของ Pod นี้ (ต้องประกาศก่อน SHOP_NAME)
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: SHOP_NAME          # → "ร้านอาหารแมวน้องส้ม (som-dev)" / "(som-staging)" / "(som-prod)"
          value: "ร้านอาหารแมวน้องส้ม ($(POD_NAMESPACE))"
        - name: SHOP_EYEBROW       # ข้อความเล็กเหนือชื่อร้าน (som-shop-web:1.1 อ่านจาก env)
          value: "⚓ ท่าเรือ Kubernetes · โซน $(POD_NAMESPACE)"
        - name: SHOP_FOOTER        # ข้อความท้ายหน้า
          value: "Next.js + PostgreSQL · Kubernetes LAB 004 · namespace $(POD_NAMESPACE)"
        - name: DATABASE_URL
          value: postgres://som:meow1234@localhost:5432/catshop
      # ... (ตัด)
```

- **ไม่มี `metadata.namespace`** ไฟล์เดียวจึงสั่งเข้าได้ทุกโซนด้วย `-n`
- `POD_NAMESPACE` ได้ค่าจาก Downward API (บทที่ 3 ใช้ `spec.nodeName` บทนี้ใช้ `metadata.namespace`) แล้ว `$(POD_NAMESPACE)` ถูกแทนค่าใน env ตัวถัดไป หน้าร้านแต่ละโซนจึงแสดงต่างกันโดยไม่ต้องแก้ไฟล์
- ทุก container มี securityContext ครบ 4 เรื่องของ restricted และระบุ uid/gid เป็นตัวเลข (`db`, `wait-for-db` = 70, `db-seed`, `web` = 1000) `fsGroup: 70` ทำให้ postgres เขียน emptyDir ได้
- resources ของทุก container ยังเหมือนบทที่ 2 (ระบุครบจึงผ่าน quota และไม่เกิน max ของ LimitRange)
- รหัส `meow1234` ใช้เพื่อการเรียนเท่านั้น

> **ทำไมต้อง build image ใหม่เป็น `som-shop-web:1.1`:** แอปในโฟลเดอร์ `som-shop-envs/app` แก้จากบทที่ 2 เพียงจุดเดียว คือ `app/page.tsx` อ่านข้อความเล็กเหนือชื่อร้านจาก `SHOP_EYEBROW` และข้อความท้ายหน้าจาก `SHOP_FOOTER` (ถ้าไม่ตั้ง ใช้ข้อความเดิมของบทที่ 2 ทุกตัวอักษร) image `som-shop-web:1.0` ของบทที่ 2–3 ยังรันได้แต่หน้าเว็บจะไม่บอกชื่อโซนที่หัวและท้ายหน้า Dockerfile เหมือนเดิม (`USER node`)

### 10.2 เตรียม image ให้ทุก Node

🐧 **ใน SSH session ของ k8s-lab** (เริ่มที่ `/workspace/004_kubernetes_namespace/02_LAB`)

```bash
cd som-shop-envs/app
time docker build -q -t som-shop-web:1.1 .
cd ../..
docker images som-shop-web
time kind load docker-image som-shop-web:1.1 --name lab
```

```text
sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c

real	0m28.328s
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
som-shop-web:1.1   d1aecb886b11        305MB         76.6MB        
Image: "som-shop-web:1.1" with ID "sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.1" with ID "sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.1" with ID "sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c" not yet present on node "lab-control-plane", loading...

real	0m4.847s
```

(`-q` = แสดงแค่ ID ของ image ที่ได้ ถ้าอยากเห็นขั้นตอนการ build ให้ตัด `-q` ออก ครั้งแรกอาจใช้เวลาหลายนาทีเพราะต้องดึง `node:22-alpine` และติดตั้ง dependency)

image ของ postgres เป็นแบบหลาย platform `kind load docker-image` ตรง ๆ อาจล้มเหลว จึงใช้ `docker save --platform` เลือก platform เดียวแล้ว `kind load image-archive` (เครื่องสถาปัตยกรรม ARM ให้เปลี่ยนเป็น `linux/arm64` ซึ่งไม่ได้ทดสอบในเอกสารนี้)

```bash
docker pull -q postgres:17.11-alpine
time (docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab)
docker exec lab-worker crictl images | grep -E "som-shop|postgres"
```

```text
docker.io/library/postgres:17.11-alpine

real	0m5.620s
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.1                  4e9bfe88de285       76.6MB
```

`crictl images` บนเรือ `lab-worker` ต้องเห็นทั้งสอง image (ID ที่ containerd แสดงต่างจาก ID ของ docker ได้ เป็นเรื่องปกติ)

### 10.3 สร้าง 3 โซนและชุดป้องกันของ prod

<p align="center" id="fig-17">
  <img src="images/17-lab10-prod-guardrails.png" alt="รูปที่ 17 ชุดป้องกันของ som-prod" width="900"><br>
  <em><b>รูปที่ 17</b> som-prod มีชุดป้องกันครบ: ResourceQuota (งบ), LimitRange (ขนาดกล่อง) และ Pod Security แบบ restricted ที่หน้าโซน</em>
</p>

```bash
kubectl apply -f som-shop-envs/k8s/00-namespaces.yaml
kubectl get ns -l team=som -L env
kubectl get ns -l team=som --show-labels
kubectl apply -f som-shop-envs/k8s/prod-guardrails.yaml
kubectl describe quota,limitrange -n som-prod
```

```text
namespace/som-dev created
namespace/som-staging created
namespace/som-prod created
NAME          STATUS   AGE   ENV
som-dev       Active   0s    dev
som-prod      Active   0s    prod
som-staging   Active   0s    staging
NAME          STATUS   AGE   LABELS
som-dev       Active   0s    env=dev,kubernetes.io/metadata.name=som-dev,pod-security.kubernetes.io/warn=restricted,team=som
som-prod      Active   0s    env=prod,kubernetes.io/metadata.name=som-prod,pod-security.kubernetes.io/enforce-version=latest,pod-security.kubernetes.io/enforce=restricted,pod-security.kubernetes.io/warn=restricted,team=som
som-staging   Active   0s    env=staging,kubernetes.io/metadata.name=som-staging,pod-security.kubernetes.io/warn=restricted,team=som
resourcequota/prod-budget created
limitrange/prod-box-size created
Name:            prod-budget
Namespace:       som-prod
Resource         Used  Hard
--------         ----  ----
limits.cpu       0     2
limits.memory    0     2Gi
pods             0     2
requests.cpu     0     1
requests.memory  0     1Gi


Name:       prod-box-size
Namespace:  som-prod
Type        Resource  Min  Max  Default Request  Default Limit  Max Limit/Request Ratio
----        --------  ---  ---  ---------------  -------------  -----------------------
Container   cpu       -    1    50m              200m           -
Container   memory    -    1Gi  64Mi             128Mi          -
```

### 10.4 ร้านฉบับเก่าไม่ผ่านด่านของ prod

<p align="center" id="fig-18">
  <img src="images/18-lab10-old-shop-rejected.png" alt="รูปที่ 18 ร้านฉบับเก่าถูกด่าน restricted ปฏิเสธ" width="900"><br>
  <em><b>รูปที่ 18</b> ร้านฉบับบท 002 (ไม่มี securityContext) ถูกด่าน restricted ของ som-prod ปฏิเสธ ส่วนฉบับใหม่ที่รันด้วย uid 70 และ 1000 ผ่านเข้าไป</em>
</p>

```bash
kubectl apply -f som-shop-envs/k8s/som-shop-v002.yaml -n som-prod
kubectl apply -f som-shop-envs/k8s/som-shop.yaml -n som-prod --dry-run=server
```

```text
Error from server (Forbidden): error when creating "som-shop-envs/k8s/som-shop-v002.yaml": pods "som-shop-old" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (containers "db", "wait-for-db", "db-seed", "web" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (containers "db", "wait-for-db", "db-seed", "web" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or containers "db", "wait-for-db", "db-seed", "web" must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "db", "wait-for-db", "db-seed", "web" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/som-shop created (server dry run)
```

ร้านฉบับบทที่ 2 ผิดกฎทั้ง 4 ข้อในทั้ง 4 container ส่วนฉบับใหม่ผ่านทุกด่าน (`--dry-run=server` ตรวจจริงที่ API server แต่ยังไม่สร้าง)

### 10.5 เปิดร้าน 3 โซนจากไฟล์เดียว

```bash
for ns in som-dev som-staging som-prod; do kubectl apply -f som-shop-envs/k8s/som-shop.yaml -n $ns; done
kubectl get pods -A -l app=som-shop -o wide
for ns in som-dev som-staging som-prod; do kubectl wait --for=condition=Ready pod/som-shop -n $ns --timeout=180s; done
kubectl get pods -A -l app=som-shop -o wide
```

```text
pod/som-shop created
pod/som-shop created
pod/som-shop created
NAMESPACE     NAME       READY   STATUS     RESTARTS   AGE   IP       NODE          NOMINATED NODE   READINESS GATES
som-dev       som-shop   0/2     Init:0/3   0          0s    <none>   lab-worker    <none>           <none>
som-prod      som-shop   0/2     Init:0/3   0          0s    <none>   lab-worker2   <none>           <none>
som-staging   som-shop   0/2     Init:0/3   0          0s    <none>   lab-worker    <none>           <none>
pod/som-shop condition met
pod/som-shop condition met
pod/som-shop condition met
NAMESPACE     NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-dev       som-shop   2/2     Running   0          8s    10.244.2.10   lab-worker    <none>           <none>
som-prod      som-shop   2/2     Running   0          8s    10.244.1.12   lab-worker2   <none>           <none>
som-staging   som-shop   2/2     Running   0          8s    10.244.2.11   lab-worker    <none>           <none>
```

- Pod ชื่อ `som-shop` เหมือนกัน 3 ตัว คนละ NAMESPACE ไม่ชนกัน
- dev/staging ไม่มี Warning เลย (ไฟล์ผ่าน restricted แล้ว กระดิ่ง warn จึงเงียบ)
- `2/2` = sidecar `db` + `web` และ `Init:0/3` ตอนเริ่มคือ init 3 ตัว (`db` นับเป็น init แบบ sidecar) ร้านพร้อมในไม่กี่วินาทีเพราะ image อยู่บนเรือแล้ว
- dev และ staging อยู่เรือเดียวกัน ส่วน prod อยู่อีกลำ (ในเครื่องนักศึกษาอาจต่างได้) namespace ไม่ได้กำหนดเรือ

### 10.6 ตรวจว่าแต่ละร้านรู้ว่าตัวเองอยู่โซนไหน และรันแบบไม่ใช่ root

```bash
kubectl exec -n som-staging som-shop -c web -- printenv SHOP_NAME POD_NAMESPACE SHOP_FOOTER
for ns in som-dev som-staging som-prod; do kubectl exec -n $ns som-shop -c web -- printenv SHOP_NAME; done
kubectl exec -n som-prod som-shop -c web -- id
kubectl exec -n som-prod som-shop -c db -- id
kubectl exec -n som-prod som-shop -c db -- ls -ld /var/lib/postgresql/data /var/lib/postgresql/data/pgdata
kubectl exec -n som-prod som-shop -c db -- grep -E "^Cap(Eff|Prm|Bnd)" /proc/1/status
kubectl exec -n som-prod som-shop -c db -- pg_isready -U som -d catshop -h 127.0.0.1
kubectl exec -n som-prod som-shop -c web -- wget -qO- http://127.0.0.1:3000/api/health; echo
kubectl logs -n som-prod som-shop -c db-seed
```

```text
ร้านอาหารแมวน้องส้ม (som-staging)
som-staging
Next.js + PostgreSQL · Kubernetes LAB 004 · namespace som-staging
ร้านอาหารแมวน้องส้ม (som-dev)
ร้านอาหารแมวน้องส้ม (som-staging)
ร้านอาหารแมวน้องส้ม (som-prod)
uid=1000(node) gid=1000(node) groups=70,1000(node)
uid=70(postgres) gid=70(postgres) groups=70(postgres)
drwxrwsrwx    3 root     postgres      4096 Oct  4 13:33 /var/lib/postgresql/data
drwx------   19 postgres postgres      4096 Oct  4 13:33 /var/lib/postgresql/data/pgdata
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	0000000000000000
127.0.0.1:5432 - accepting connections
{"ok":true,"db":"up"}
connected to database
tables ready: products, orders
seeded 6 products (new: 6)
```

- `SHOP_NAME` ต่างกันตาม namespace ทั้งที่ใช้ไฟล์เดียว
- `web` รันเป็น uid 1000 (`groups=70` มาจาก `fsGroup`) และ `db` เป็น uid 70 ไม่มี root
- โฟลเดอร์ข้อมูลเป็นของกลุ่ม `postgres` (`fsGroup: 70`) postgres จึงเขียนได้ และ capability ทั้งหมดเป็น 0 (`drop: ["ALL"]`) แต่ฐานข้อมูลยังทำงานปกติ

### 10.7 งบของ prod: สาขาที่ 2 และ 3

<p align="center" id="fig-19">
  <img src="images/19-lab10-prod-quota-third-branch.png" alt="รูปที่ 19 สาขาที่ 3 ชนงบของ som-prod" width="900"><br>
  <em><b>รูปที่ 19</b> ใน som-prod เปิดสาขาที่ 2 ได้ แต่สาขาที่ 3 ชนงบ ResourceQuota หลายรายการพร้อมกัน (pods 2/2, limits.cpu, limits.memory, requests.memory) จึงถูกปฏิเสธ</em>
</p>

```bash
kubectl describe quota prod-budget -n som-prod
sed 's/name: som-shop$/name: som-shop-2/' som-shop-envs/k8s/som-shop.yaml | kubectl apply -n som-prod -f -
kubectl describe quota prod-budget -n som-prod
sed 's/name: som-shop$/name: som-shop-3/' som-shop-envs/k8s/som-shop.yaml | kubectl apply -n som-prod -f -
kubectl get pods -n som-prod
kubectl get quota -n som-prod
```


```text
Name:            prod-budget
Namespace:       som-prod
Resource         Used   Hard
--------         ----   ----
limits.cpu       1      2
limits.memory    1Gi    2Gi
pods             1      2
requests.cpu     200m   1
requests.memory  448Mi  1Gi
pod/som-shop-2 created
Name:            prod-budget
Namespace:       som-prod
Resource         Used   Hard
--------         ----   ----
limits.cpu       2      2
limits.memory    2Gi    2Gi
pods             2      2
requests.cpu     400m   1
requests.memory  896Mi  1Gi
Error from server (Forbidden): error when creating "STDIN": pods "som-shop-3" is forbidden: exceeded quota: prod-budget, requested: limits.cpu=1,limits.memory=1Gi,pods=1,requests.memory=448Mi, used: limits.cpu=2,limits.memory=2Gi,pods=2,requests.memory=896Mi, limited: limits.cpu=2,limits.memory=2Gi,pods=2,requests.memory=1Gi
NAME         READY   STATUS     RESTARTS   AGE
som-shop     2/2     Running    0          77s
som-shop-2   0/2     Init:0/3   0          0s
NAME          REQUEST                                                       LIMIT                                     AGE
prod-budget   pods: 2/2, requests.cpu: 400m/1, requests.memory: 896Mi/1Gi   limits.cpu: 2/2, limits.memory: 2Gi/2Gi   77s
```

- 1 ร้านใช้ requests **200m/448Mi** และ limits **1 CPU/1Gi** (นับแบบ effective ของ Pod ที่มี init/sidecar ดูทฤษฎีหัวข้อ 11.4)
- สาขาที่ 3 ชนงบ **4 ค่าพร้อมกัน**: `pods`, `limits.cpu`, `limits.memory` และ `requests.memory` (896Mi + 448Mi > 1Gi) ข้อความรวมทุกค่าที่เกินไว้ในบรรทัดเดียว และ `"STDIN"` หมายถึง manifest มาจากท่อ `|`

> ⚠️ **กับดักของ sed:** pattern `name: som-shop$` ต้องตรงกับบรรทัดที่ "จบ" ด้วย `som-shop` ถ้าบรรทัด `name:` มีคอมเมนต์ต่อท้าย sed จะไม่แทนค่า และ `kubectl apply` จะได้ `pod/som-shop configured` (ไปแก้ร้านเดิมเงียบ ๆ ไม่ได้สร้างสาขาใหม่) ไฟล์ของบทนี้จึงย้ายคอมเมนต์ขึ้นไปไว้บรรทัดบน ถ้าเห็นคำว่า `configured` แทน `created` ให้ตรวจไฟล์ด้วย `grep -n "name: som-shop" som-shop-envs/k8s/som-shop.yaml`

ปิดสาขาที่ 2 ก่อนทำต่อ

```bash
kubectl delete pod som-shop-2 -n som-prod
```

```text
pod "som-shop-2" deleted from som-prod namespace
```

### 10.8 (ลองเพิ่มเติม) ถ้าลืม runAsUser และ LimitRange ของ prod

ส่วนนี้ไม่บังคับ แต่ช่วยให้เข้าใจเหตุผลของการตั้งค่าใน `som-shop.yaml`

**(ก) ลบ `runAsUser: 1000` ออก** ลองใน `som-dev` (ใช้ sed เปลี่ยนชื่อ Pod และลบบรรทัด `runAsUser: 1000` ทิ้ง ไฟล์จริงไม่ถูกแก้)

```bash
sed -e 's/name: som-shop$/name: som-shop-nouid/' -e '/runAsUser: 1000/d' som-shop-envs/k8s/som-shop.yaml | kubectl apply -n som-dev -f -
sleep 20
kubectl get pod som-shop-nouid -n som-dev
kubectl get events -n som-dev --field-selector involvedObject.name=som-shop-nouid,type=Warning
kubectl delete pod som-shop-nouid -n som-dev
```

```text
pod/som-shop-nouid created
NAME             READY   STATUS                            RESTARTS   AGE
som-shop-nouid   1/2     Init:CreateContainerConfigError   0          20s
LAST SEEN   TYPE      REASON      OBJECT               MESSAGE
18s         Warning   Unhealthy   pod/som-shop-nouid   Startup probe failed: 127.0.0.1:5432 - no response
14s         Warning   Failed      pod/som-shop-nouid   Error: container has runAsNonRoot and image has non-numeric user (node), cannot verify user is non-root (pod: "som-shop-nouid_som-dev(a1ebff7e-81ad-4ab6-808d-fd9601ea25dc)", container: db-seed)
pod "som-shop-nouid" deleted from som-dev namespace
```

`db` (uid 70) เริ่มได้ แต่ `db-seed` ที่ใช้ image `USER node` (ชื่อ ไม่ใช่ตัวเลข) ถูก kubelet ปฏิเสธ Pod จึงค้าง `Init:CreateContainerConfigError` สังเกตว่า **ไม่มีคำเตือนจาก PSA** เพราะ manifest ยังตั้ง `runAsNonRoot: true` ถูกตามกฎ (ส่วน `Startup probe failed` ช่วงแรกคือ postgres ยังเริ่มไม่เสร็จ เป็นเรื่องปกติ)

**(ข) Pod debug ใน prod ที่ไม่ระบุ resources**

```bash
kubectl run debug -n som-prod --image=busybox:1.36 -- sleep 3600
```

```text
Error from server (Forbidden): pods "debug" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "debug" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "debug" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "debug" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "debug" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

ด่าน restricted ปฏิเสธก่อน ต้องส่ง securityContext ผ่าน `--overrides` (คำสั่งยาว พิมพ์บรรทัดเดียว)

```bash
kubectl run debug -n som-prod --image=busybox:1.36 --overrides='{"spec":{"terminationGracePeriodSeconds":1,"securityContext":{"runAsNonRoot":true,"runAsUser":1000,"runAsGroup":1000,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"debug","image":"busybox:1.36","args":["sleep","3600"],"securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}}}]}}'
kubectl get pod debug -n som-prod -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
kubectl get pod debug -n som-prod -o jsonpath="{.metadata.annotations.kubernetes\.io/limit-ranger}{\"\n\"}"
kubectl get quota -n som-prod
kubectl delete pod debug -n som-prod
```

```text
pod/debug created
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}
LimitRanger plugin set: cpu, memory request for container debug; cpu, memory limit for container debug
NAME          REQUEST                                                       LIMIT                                            AGE
prod-budget   pods: 2/2, requests.cpu: 250m/1, requests.memory: 512Mi/1Gi   limits.cpu: 1200m/2, limits.memory: 1152Mi/2Gi   90s
pod "debug" deleted from som-prod namespace
```

`debug` ได้ค่าจาก `prod-box-size` (requests 50m/64Mi, limits 200m/128Mi) และถูกนับเข้างบของ prod ทันที (pods 2/2) ส่วน `som-shop` ไม่ได้ annotation นี้ เพราะระบุ resources ครบเองแล้ว

### 10.9 บัตรเด็กฝึกงานของ som-dev

<p align="center" id="fig-20">
  <img src="images/20-lab10-intern-dev-only.png" alt="รูปที่ 20 intern ดูได้อย่างเดียวเฉพาะ som-dev" width="900"><br>
  <em><b>รูปที่ 20</b> ServiceAccount intern ดูได้อย่างเดียวและเฉพาะ som-dev: get/list/logs ได้ แต่ลบไม่ได้และเข้า som-prod ไม่ได้</em>
</p>

```bash
kubectl apply -f som-shop-envs/k8s/intern-rbac.yaml
for chk in 'get pods -n som-dev' 'get pods/log -n som-dev' 'delete pods -n som-dev' 'get pods -n som-prod' 'create pods -n som-dev'; do printf '%-26s %s\n' "$chk" "$(kubectl auth can-i $chk --as=system:serviceaccount:som-dev:intern)"; done
```

```text
serviceaccount/intern created
role.rbac.authorization.k8s.io/shop-viewer created
rolebinding.rbac.authorization.k8s.io/intern-shop-viewer created
get pods -n som-dev        yes
get pods/log -n som-dev    yes
delete pods -n som-dev     no
get pods -n som-prod       no
create pods -n som-dev     no
```

สร้าง context ของ intern จาก token จริง (เหมือน LAB 7) แล้วลองใช้งาน

```bash
T=$(kubectl create token intern -n som-dev --duration=1h) && kubectl config set-credentials intern --token=$T && kubectl config set-context intern@som-dev --cluster=kind-lab --user=intern --namespace=som-dev
kubectl --context intern@som-dev auth whoami
kubectl --context intern@som-dev get pods
kubectl --context intern@som-dev logs som-shop -c web --tail=5
kubectl --context intern@som-dev logs som-shop --tail=3
kubectl --context intern@som-dev delete pod som-shop
kubectl --context intern@som-dev get pods -n som-prod
kubectl --context intern@som-dev port-forward pod/som-shop 3009:3000
kubectl config current-context
```

```text
User "intern" set.
Context "intern@som-dev" created.
ATTRIBUTE                                           VALUE
Username                                            system:serviceaccount:som-dev:intern
UID                                                 e23bf9f9-b091-46c7-a304-5dd9bec6db55
Groups                                              [system:serviceaccounts system:serviceaccounts:som-dev system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [JTI=38a0afcf-...]
NAME       READY   STATUS    RESTARTS   AGE
som-shop   2/2     Running   0          101s
▲ Next.js 16.3.8
- Local:         http://localhost:3000
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
✓ Running next.config took 1.0ms
Defaulted container "web" out of: web, db (init), wait-for-db (init), db-seed (init)
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
✓ Running next.config took 1.0ms
Error from server (Forbidden): pods "som-shop" is forbidden: User "system:serviceaccount:som-dev:intern" cannot delete resource "pods" in API group "" in the namespace "som-dev"
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:som-dev:intern" cannot list resource "pods" in API group "" in the namespace "som-prod"
error: error upgrading connection: unable to upgrade connection: pods "som-shop" is forbidden: User "system:serviceaccount:som-dev:intern" cannot create resource "pods/portforward" in API group "" in the namespace "som-dev"
kind-lab
```

intern ดู Pod และ log ของร้าน dev ได้ แต่ลบไม่ได้ ดู prod ไม่ได้ และ **เปิดหน้าร้านด้วย port-forward ไม่ได้** (ต้องการ `create` บน `pods/portforward`) context ปัจจุบันยังเป็น `kind-lab` (admin) ขั้นต่อไปจึงใช้ admin เปิด port-forward

### 10.10 เปิดหน้าร้าน 3 โซนใน browser

<p align="center" id="fig-21">
  <img src="images/21-lab10-three-port-forwards.png" alt="รูปที่ 21 port-forward 3 โซนผ่าน ssh -L" width="900"><br>
  <em><b>รูปที่ 21</b> เปิดหน้าร้านทั้ง 3 env พร้อมกัน: port-forward คนละ port (3001/3002/3003) แล้ว ssh -L ไปยัง browser บนเครื่องนักศึกษา</em>
</p>

**ขั้นที่ 1:** 🐧 **SSH session หลักของ k8s-lab** เปิด port-forward ทั้ง 3 โซนไว้เบื้องหลัง (โซนละ port: dev 3001, staging 3002, prod 3003) เก็บข้อความไว้ในไฟล์ log

```bash
kubectl port-forward -n som-dev     pod/som-shop 3001:3000 > /tmp/pf-3001.log 2>&1 &
kubectl port-forward -n som-staging pod/som-shop 3002:3000 > /tmp/pf-3002.log 2>&1 &
kubectl port-forward -n som-prod    pod/som-shop 3003:3000 > /tmp/pf-3003.log 2>&1 &
sleep 2; cat /tmp/pf-300*.log
for p in 3001 3002 3003; do echo "== $p: $(curl -s localhost:$p | grep -o "<h1>[^<]*</h1>")"; done
```

```text
Forwarding from 127.0.0.1:3001 -> 3000
Forwarding from 127.0.0.1:3002 -> 3000
Forwarding from 127.0.0.1:3003 -> 3000
== 3001: <h1>ร้านอาหารแมวน้องส้ม (som-dev)</h1>
== 3002: <h1>ร้านอาหารแมวน้องส้ม (som-staging)</h1>
== 3003: <h1>ร้านอาหารแมวน้องส้ม (som-prod)</h1>
```

(ในเครื่องที่รองรับ IPv6 อาจมีบรรทัด `Forwarding from [::1]:...` เพิ่ม ใช้ได้เหมือนกัน)

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ ต่อท่อ SSH 3 ท่อในคำสั่งเดียว (ถ้ามีหน้าต่าง `ssh -L` จากบทก่อนค้างอยู่ ให้ `exit` ก่อน) แล้วเปิดหน้าต่างนี้ทิ้งไว้

```bash
ssh -p 2223 -L 3001:localhost:3001 -L 3002:localhost:3002 -L 3003:localhost:3003 root@localhost
```

**ขั้นที่ 3:** 🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:3001**, **http://localhost:3002** และ **http://localhost:3003** คนละแท็บ แล้วลองกดสั่งซื้อในแต่ละโซนไม่เท่ากัน (เช่น dev 1 ครั้ง, staging 2 ครั้ง, prod 3 ครั้ง) แล้วรีเฟรชทุกแท็บ

หน้าเว็บทั้ง 3 โซน **สีและหน้าตาเหมือนกัน** (เป็น image เดียวกัน) ต่างกันที่ชื่อร้าน `(som-dev)`/`(som-staging)`/`(som-prod)` ข้อความเล็ก `⚓ ท่าเรือ Kubernetes · โซน som-...` ข้อความท้ายหน้า `namespace som-...` และตัวเลขออเดอร์ ส่วนป้าย `เสิร์ฟโดย Pod: som-shop` เหมือนกันทุกโซน เพราะชื่อ Pod เหมือนกัน

<p align="center" id="fig-22">
  <img src="images/screenshots/20261004_2050_lab10ns_01-som-dev.png" alt="รูปที่ 22 ภาพหน้าจอจริง โซน som-dev" width="700"><br>
  <em><b>รูปที่ 22</b> ภาพหน้าจอจริงจากการทดลอง: http://localhost:3001 หัวเว็บ "ร้านอาหารแมวน้องส้ม (som-dev)" ข้อความเล็ก "โซน som-dev" ออเดอร์ทั้งหมด 1 และท้ายหน้า "Kubernetes LAB 004 · namespace som-dev"</em>
</p>

<p align="center" id="fig-23">
  <img src="images/screenshots/20261004_2050_lab10ns_02-som-staging.png" alt="รูปที่ 23 ภาพหน้าจอจริง โซน som-staging" width="700"><br>
  <em><b>รูปที่ 23</b> ภาพหน้าจอจริงจากการทดลอง: http://localhost:3002 ร้าน som-staging ออเดอร์ทั้งหมด 2 ไม่เกี่ยวกับออเดอร์ของ dev เพราะแต่ละโซนมีฐานข้อมูลใน Pod ของตัวเอง</em>
</p>

<p align="center" id="fig-24">
  <img src="images/screenshots/20261004_2050_lab10ns_03-som-prod.png" alt="รูปที่ 24 ภาพหน้าจอจริง โซน som-prod" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: http://localhost:3003 ร้าน som-prod (ร้านจริง) ออเดอร์ทั้งหมด 3 เปิดจาก manifest ไฟล์เดียวกับอีกสองโซน</em>
</p>

**(ทางเลือก) สั่งซื้อด้วย curl** 🐧 ใน k8s-lab

```bash
curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo
```

ตัวอย่างผลเมื่อสั่งในร้านที่ยังไม่มีออเดอร์ (ถ้าเคยสั่งไปแล้ว `order_id` และ `stock` จะต่างจากนี้)

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
```

แอปนี้มี API แค่ `POST /api/orders` (สั่งซื้อ), `GET /api/products` และ `GET /api/health` — **ไม่มี `GET /api/orders`** (เรียกแล้วได้ `405 Method Not Allowed`) จึงตรวจจำนวนออเดอร์ของแต่ละโซนจากหน้าเว็บ (ช่อง "ออเดอร์ทั้งหมด") หรือด้วยคำสั่งด้านล่าง

```bash
# จำนวนออเดอร์ทั้งหมดของแต่ละโซน (ตัวเลขหน้าคำว่า ออเดอร์ทั้งหมด)
for p in 3001 3002 3003; do echo -n "$p: "; curl -s localhost:$p/ | grep -o '[0-9,]*</span><span class="label">ออเดอร์ทั้งหมด'; done
# stock ของสินค้า id 1 ในแต่ละโซน
for p in 3001 3002 3003; do echo -n "$p: "; curl -s localhost:$p/api/products | grep -o '"stock":[0-9]*' | head -1; done
```

สิ่งที่ควรสังเกต: หลังสั่งที่ dev 1 ออเดอร์ ตัวเลขออเดอร์ของ dev เพิ่มขึ้น 1 และ stock ของสินค้า id 1 ใน dev ลดลง 1 ส่วน staging และ prod ไม่เปลี่ยนเลย เพราะแต่ละโซนมีฐานข้อมูลของตัวเอง

### 10.11 ลบโซน dev ทั้งก้อน

<p align="center" id="fig-25">
  <img src="images/22-lab10-delete-dev.png" alt="รูปที่ 25 ลบ som-dev แล้ว staging และ prod ยังเปิดอยู่" width="900"><br>
  <em><b>รูปที่ 25</b> ลบ som-dev ทั้ง namespace: ร้าน dev, บัตร intern และสิทธิ์หายไปทั้งหมด แต่ som-staging และ som-prod ยังเปิดขายตามปกติ (ลบเสร็จในราว 10 วินาที)</em>
</p>

🐧 **SSH session หลักของ k8s-lab** (เปิดแท็บ browser ทั้ง 3 ค้างไว้)

```bash
time kubectl delete ns som-dev
kubectl get pods -A -l app=som-shop
kubectl get sa intern -n som-dev
kubectl get role,rolebinding -n som-dev
kubectl --context intern@som-dev get pods
kubectl --context intern@som-dev auth whoami
for p in 3001 3002 3003; do echo "== $p: $(curl -s -m 3 localhost:$p | grep -o "<h1>[^<]*</h1>") (curl exit $?)"; done
```

```text
namespace "som-dev" deleted

real	0m10.266s
NAMESPACE     NAME       READY   STATUS    RESTARTS   AGE
som-prod      som-shop   2/2     Running   0          2m30s
som-staging   som-shop   2/2     Running   0          2m30s
Error from server (NotFound): namespaces "som-dev" not found
No resources found in som-dev namespace.
error: You must be logged in to the server (Unauthorized)
error: You must be logged in to the server (Unauthorized)
== 3001:  (curl exit 1)
== 3002: <h1>ร้านอาหารแมวน้องส้ม (som-staging)</h1> (curl exit 0)
== 3003: <h1>ร้านอาหารแมวน้องส้ม (som-prod)</h1> (curl exit 0)
```

- คำสั่งเดียวลบร้าน dev, ฐานข้อมูล dev, SA `intern`, Role และ RoleBinding ทั้งหมด ใช้เวลาราว 10 วินาที
- token ของ intern ใช้ไม่ได้ทันที (`Unauthorized`) เพราะ ServiceAccount ที่ token ผูกอยู่ถูกลบไปแล้ว
- `get role,rolebinding -n som-dev` ตอบ `No resources found` แต่ `get sa intern -n som-dev` ตอบ `namespaces "som-dev" not found` (คำขอดูของชิ้นเดียวตามชื่อ ระบบตรวจว่ามี namespace ก่อน ส่วนการลิสต์ตอบรายการว่าง)
- ร้าน staging และ prod ยังขายได้ตามปกติ

port-forward ของ 3001 **ไม่จบทันที** ที่ลบโซน มันจบตอนมีคนเข้าครั้งถัดไป ดูได้จาก log

```bash
tail -3 /tmp/pf-3001.log
pgrep -af "[k]ubectl port-forward -n som-dev" || echo "port-forward 3001 จบไปแล้ว"
```

```text
Handling connection for 3001
E1004 20:36:23.281489   21804 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod bbdd6f51ffc1d038082947a75864cda8efbd54f689e9c63973dc79bbb97f059b, uid : network namespace for sandbox \"bbdd6f51ffc1d038082947a75864cda8efbd54f689e9c63973dc79bbb97f059b\" is closed" localPort=3001 remotePort=3000
error: lost connection to pod
port-forward 3001 จบไปแล้ว
```

(คำว่า "network namespace" ในข้อความนี้คือกลไกของ Linux ที่แยกเครือข่ายของ container คนละเรื่องกับ Kubernetes namespace) 🌐 รีเฟรชแท็บ browser

<p align="center" id="fig-26">
  <img src="images/screenshots/20261004_2051_lab10ns_04-som-dev-gone.png" alt="รูปที่ 26 ภาพหน้าจอจริง โซน som-dev หายแล้ว" width="700"><br>
  <em><b>รูปที่ 26</b> ภาพหน้าจอจริงจากการทดลอง: หลัง kubectl delete ns som-dev ราว 10 วินาที แท็บ http://localhost:3001 เปิดไม่ได้ (ERR_CONNECTION_RESET) เพราะ Pod ปลายทางของ port-forward ถูกลบไปพร้อมโซน</em>
</p>

<p align="center" id="fig-27">
  <img src="images/screenshots/20261004_2051_lab10ns_05-som-prod-still-open.png" alt="รูปที่ 27 ภาพหน้าจอจริง som-prod ยังเปิดอยู่" width="700"><br>
  <em><b>รูปที่ 27</b> ภาพหน้าจอจริงจากการทดลอง: ในเวลาเดียวกัน http://localhost:3003 ร้าน som-prod ยังเปิดได้ปกติและออเดอร์ทั้ง 3 ยังอยู่ การลบโซน dev ไม่กระทบโซนอื่น</em>
</p>

ในรอบที่ถ่ายภาพหน้าจอ ผลของคำสั่งชุดเดียวกันคือ

```text
$ time kubectl delete ns som-dev
namespace "som-dev" deleted

real	0m10.226s
$ kubectl get pods -A -l app=som-shop -o wide
NAMESPACE     NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-prod      som-shop   2/2     Running   0          13m   10.244.1.16   lab-worker2   <none>           <none>
som-staging   som-shop   2/2     Running   0          13m   10.244.2.13   lab-worker    <none>           <none>
$ kubectl --context intern@som-dev get pods
error: You must be logged in to the server (Unauthorized)
```

### สิ่งที่เห็นใน LAB 10

- manifest **ไฟล์เดียว** ที่ไม่มี `metadata.namespace` เปิดร้านได้ 3 โซนด้วย `-n` Pod ชื่อ `som-shop` เหมือนกันไม่ชนกัน
- Downward API `metadata.namespace` ทำให้หน้าร้านแต่ละโซนบอกชื่อโซนของตัวเอง
- `som-prod` มีชุดป้องกันครบ: ร้านฉบับเก่าถูก PSA restricted ปฏิเสธ สาขาที่ 3 ชนงบ quota และ Pod ที่ไม่ระบุขนาดได้ค่าจาก LimitRange
- ทำ Pod ที่มี postgres + Next.js ให้ผ่าน restricted ได้ด้วย uid/gid ตัวเลข, `fsGroup`, drop ALL, no privilege escalation และ seccomp RuntimeDefault
- intern ดูได้อย่างเดียวและเฉพาะ `som-dev` และ token ใช้ไม่ได้ทันทีเมื่อโซนถูกลบ
- ลบโซน dev ทั้งก้อนในคำสั่งเดียวราว 10 วินาที staging และ prod ไม่กระทบ

### 10.12 เก็บกวาด LAB 10

🐧 **ใน SSH session ของ k8s-lab**

```bash
pkill -f "[k]ubectl port-forward"; sleep 1; pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
time kubectl delete ns som-staging som-prod
kubectl config delete-context intern@som-dev; kubectl config delete-user intern; kubectl config get-contexts
unset T
kubectl get ns; kubectl get pods -A -l app=som-shop
```

```text
ไม่มี port-forward ค้าง
namespace "som-staging" deleted
namespace "som-prod" deleted

real	0m10.474s
deleted context intern@som-dev from /root/.kube/config
deleted user intern from /root/.kube/config
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
NAME                 STATUS   AGE
default              Active   9m6s
kube-node-lease      Active   9m6s
kube-public          Active   9m6s
kube-system          Active   9m6s
local-path-storage   Active   9m2s
No resources found
```

pattern `"[k]ubectl port-forward"` (มีวงเล็บเหลี่ยม) ทำให้ `pkill`/`pgrep` ไม่ไปจับ command line ของ shell ตัวเองที่มีข้อความเดียวกัน จากนั้น 🖥️ ปิดหน้าต่าง `ssh -L` บนเครื่องนักศึกษาด้วย `exit`

image `som-shop-web:1.1` และ `postgres:17.11-alpine` ยังอยู่บนเรือ ใช้ต่อในบทถัดไปได้

<p align="center" id="fig-28">
  <img src="images/23-lab10-wrap-up.png" alt="รูปที่ 28 สรุป LAB บทที่ 4" width="900"><br>
  <em><b>รูปที่ 28</b> สรุป LAB: namespace เดียวกันกับไฟล์เดียว ใช้แยก environment ได้ พร้อมงบ ขนาดกล่อง สิทธิ์ ด่านตรวจ และลบทั้งก้อนได้ในคำสั่งเดียว</em>
</p>

### คำถามท้าย LAB 10

1. ทำไม `som-shop.yaml` จึงไม่ใส่ `metadata.namespace` แต่ `prod-guardrails.yaml` และ `intern-rbac.yaml` ใส่ ถ้าสลับกันจะเกิดปัญหาอะไร
2. อธิบายว่า `SHOP_NAME` ของแต่ละโซนได้ค่า `ร้านอาหารแมวน้องส้ม (som-...)` มาอย่างไร และทำไม `POD_NAMESPACE` ต้องประกาศก่อน `SHOP_NAME`
3. คำนวณให้ดูว่าทำไมร้าน 1 Pod จึงใช้งบ requests 200m/448Mi ทั้งที่ผลรวม requests ของทุก container คือ 260m/528Mi และทำไมสาขาที่ 3 จึงชน `requests.memory` แต่ไม่ชน `requests.cpu`
4. ร้านฉบับบทที่ 2 ถูกปฏิเสธใน `som-prod` แต่ถ้า apply เข้า `som-dev` จะเกิดอะไรขึ้น (ทำนายจาก label ของ `som-dev` แล้วลองดูได้) ในงานจริงการตั้ง dev เป็น `warn` และ prod เป็น `enforce` มีข้อดีข้อเสียอย่างไร
5. หลังลบ `som-dev` ทำไม `kubectl --context intern@som-dev get pods` จึงได้ `Unauthorized` (ไม่ใช่ `Forbidden`) และสองคำนี้ต่างกันอย่างไร

> **🏆 ท้าทาย:** เขียน NetworkPolicy สำหรับ `som-prod` ที่ให้ Pod ใน `som-prod` รับการเชื่อมต่อเข้าจาก Pod ใน `som-prod` เท่านั้น (แบบ LAB 4) แล้วเปิดร้าน prod ใหม่ ทดสอบว่า (1) Pod busybox ใน `som-staging` เรียก `http://<IP ของร้าน prod>:3000` ไม่ได้ (2) port-forward 3003 + browser ยังเปิดร้านได้หรือไม่ บันทึกผลและอธิบายว่าทำไม (เอกสารนี้ไม่ได้เฉลยผลข้อ 2 ให้ทดลองเอง)

> **ปูทางบทหน้า:** ร้านทั้ง 3 โซนยังเป็น Pod เดี่ยว ถ้า Pod ถูกลบก็ไม่มีใครสร้างคืน และต้องเปิดหน้าร้านด้วย port-forward ทีละ Pod บทถัดไปน้องส้มจะใช้ Deployment ดูแลจำนวนร้านให้อัตโนมัติ และใช้ Service เป็นที่อยู่คงที่ของร้านในแต่ละโซน (ชื่อ DNS แบบ `<service>.<namespace>` ที่เห็นใน search domain ของ LAB 4) โดยใช้ namespace, quota, LimitRange, RBAC และ PSA ของบทนี้ต่อได้ทันที

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-envs/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 004_kubernetes_namespace k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/004_kubernetes_namespace/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (connection refused) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ ถ้าจะทำ LAB 10 ต้อง build/`kind load` image ใหม่ |
| `Error from server (NotFound): namespaces "blue" not found` | ข้าม LAB ที่สร้าง namespace นั้น หรือเก็บกวาดไปแล้ว | สร้างใหม่ตาม LAB ก่อนหน้า (ดูบรรทัด "ต้องมีจาก LAB ..." ในแต่ละ LAB) |
| `kubectl get pods` เห็นของแปลก ๆ หรือไม่เห็น Pod ที่เพิ่งสร้าง, Pod ใหม่ไปโผล่ผิดโซน | ลืมคืน namespace ของ context หลัง LAB 2 | `kubectl config get-contexts` ดูคอลัมน์ NAMESPACE แล้ว `kubectl config set-context --current --namespace=default` |
| `error: the namespace from the provided object "..." does not match the namespace "..."` | ไฟล์มี `metadata.namespace` แต่สั่ง `-n` คนละค่า | ตัด `-n` ออก หรือใส่ `-n` ให้ตรงกับไฟล์ |
| `error: a resource cannot be retrieved by name across all namespaces` | ใช้ `kubectl get pod <ชื่อ> -A` | ใช้ `kubectl get pods -A --field-selector metadata.name=<ชื่อ>` |
| NetworkPolicy สร้างได้แต่ไม่มีผล | คลัสเตอร์อื่นที่ network plugin ไม่รองรับ (kind v0.33 รองรับ) หรือ `podSelector`/label ไม่ตรง | ตรวจ `kubectl describe netpol -n <ns>` และ `kubectl get pods --show-labels -n <ns>` |
| `wget: download timed out` ทั้งที่ยังไม่ได้ apply policy | ใช้ IP เก่า (Pod ถูกสร้างใหม่ได้ IP ใหม่) | อ่าน IP ใหม่ด้วย `kubectl get pod web -n team-a -o jsonpath='{.status.podIP}'` |
| `failed quota: ... must specify ...` | namespace มี quota ของ compute แต่ Pod ไม่ระบุ resources | ใส่ `resources` ให้ครบทุก container หรือเพิ่ม LimitRange (LAB 6) |
| `exceeded quota: ...` | ใช้งบเต็ม | ลบ Pod ที่ไม่ใช้ แล้วดู `kubectl describe quota -n <ns>` |
| `--token` แล้วยังทำได้ทุกอย่าง / `auth whoami` ยังเป็น `kubernetes-admin` | kubeconfig ของ kind ใช้ client certificate ซึ่งถูกใช้ก่อน token | สร้าง user + context ใหม่ที่มีแต่ token (LAB 7 ขั้นที่ 5) |
| `error: You must be logged in to the server (Unauthorized)` | token หมดอายุ หรือ ServiceAccount/namespace ถูกลบแล้ว | ขอ token ใหม่ด้วย `kubectl create token ...` แล้ว `set-credentials` ใหม่ (ต้องมี SA อยู่) |
| `error: context "intern@lab" does not exist` / kubectl ใช้ context ผิด | ลบ context ไปแล้ว หรือพิมพ์ชื่อผิด | `kubectl config get-contexts` และ `kubectl config use-context kind-lab` |
| Pod ไม่ผ่านด่าน `violates PodSecurity "restricted:latest"` | ขาด securityContext | เพิ่มตามตารางในทฤษฎีหัวข้อ 14.4 |
| `Init:CreateContainerConfigError` + `image has non-numeric user (node)` | `runAsNonRoot: true` แต่ไม่ระบุ `runAsUser` ตัวเลข | ใส่ `runAsUser: 1000` (node) หรือ `70` (postgres) |
| namespace ค้าง `Terminating` นาน | Pod ที่ grace period ยาว หรือ object ที่มี finalizer ค้าง | รอ grace period (`peek` 30 วินาที) ถ้าเกินหลายนาที ดู `kubectl get ns <ns> -o jsonpath='{.status.conditions}'` (ทฤษฎีหัวข้อ 8.3) |
| `unable to create new content in namespace ... because it is being terminated` | กำลังลบ namespace นั้นอยู่ | รอให้หายแล้วสร้าง namespace ใหม่ |
| `som-shop` ค้าง `Init:ErrImagePull` / `ImagePullBackOff` | ไม่มี image บน Node (เช่น สร้างคลัสเตอร์ใหม่แต่ยังไม่ `kind load`) | ทำขั้น 10.2 แล้ว `kubectl delete pod som-shop -n <ns>` และ apply ใหม่ |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` |
| หน้าร้านไม่แสดงชื่อโซนที่หัวและท้ายหน้า (ท้ายหน้าเขียน `Kubernetes LAB 002`) | ใช้ image `som-shop-web:1.0` ของบทก่อน | build และ load `som-shop-web:1.1` ตามขั้น 10.2 |
| `sed ... som-shop-2` แล้วได้ `pod/som-shop configured` แทน `created` | บรรทัด `name: som-shop` มีคอมเมนต์ต่อท้าย sed จึงไม่แทนค่า | ตรวจ `grep -n "name: som-shop" som-shop-envs/k8s/som-shop.yaml` ย้ายคอมเมนต์ขึ้นบรรทัดบน (ไฟล์ของบทนี้แก้แล้ว) |
| `kubectl port-forward` แจ้ง `address already in use` | port-forward ตัวเก่ายังค้าง | `pgrep -af "[k]ubectl port-forward"` แล้ว `pkill -f "[k]ubectl port-forward"` |
| browser เปิด `localhost:3001`–`3003` ไม่ได้ (`ERR_CONNECTION_RESET`/refused) | หน้าต่าง `ssh -L` ถูกปิด หรือ port-forward หลุดเพราะ Pod/โซนถูกลบ | ดู `cat /tmp/pf-3001.log` ถ้ามี `lost connection to pod` ให้เปิด port-forward ใหม่หลังมี Pod ใหม่ |
| `ssh -L` แจ้งว่า bind port ไม่ได้ | port 3001–3003 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ | เปลี่ยนเลขซ้ายของ `-L` เช่น `-L 13001:localhost:3001` แล้วเปิด `http://localhost:13001` |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ **ห้ามมี token ของ ServiceAccount ในภาพ**

- [ ] **LAB 0** `kubectl get ns --show-labels` (5 namespace) และ `kubectl get pods -A -o wide`
- [ ] **LAB 1** `kubectl get pods -A -l app=snack -o wide` (snack 3 ตัว) และ error `does not match the namespace`
- [ ] **LAB 2** `kubectl config get-contexts` ตอน NAMESPACE เป็น `blue` และหลังคืนค่าเป็น `default`
- [ ] **LAB 3** `kubectl get nodes -n blue` และจำนวน 34/37 ของ api-resources
- [ ] **LAB 4** Pod ของ 2 โซนบนเรือลำเดียวกัน, `resolv.conf`, `download timed out` หลัง `allow-same-namespace` และ `team-b เข้าได้` หลัง `allow-from-team-b`
- [ ] **LAB 5** `must specify ...` และ `exceeded quota ... pods=3` พร้อม `describe quota`
- [ ] **LAB 6** resources ที่ LimitRange เติมให้ `no-request` และ error `maximum cpu usage per Container`
- [ ] **LAB 7** ผล can-i ของ intern, ผล `--token ... auth whoami` (ยังเป็น admin) และ `--context intern@lab auth whoami`
- [ ] **LAB 8** Warning ของ root-nginx, Forbidden ของ privileged และ `uid=1000 gid=1000` ของ restricted-ok
- [ ] **LAB 9** `doomed Terminating` + `unable to create new content` และผล `--dry-run=server` ของ namespace ระบบ
- [ ] **LAB 10** (1) `kubectl get pods -A -l app=som-shop -o wide` 3 โซน (2) Forbidden ของ `som-shop-v002.yaml` (3) `exceeded quota` ของ `som-shop-3` (4) ตาราง can-i ของ intern (5) browser 3 แท็บแสดงชื่อโซนและออเดอร์ต่างกัน (6) หลังลบ `som-dev`: แท็บ 3001 เปิดไม่ได้ แต่ 3003 ยังเปิดได้
- [ ] ท้ายสุด `kubectl get ns` เหลือ 5 namespace ตั้งต้น และ `kubectl config get-contexts` มีแค่ `kind-lab` ที่ NAMESPACE เป็น `default`

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| namespace `blue`, `green` | 1–4 | `kubectl get ns` | `kubectl delete ns blue green` |
| namespace `kube-mine` | 1 | `kubectl get ns kube-mine` | `kubectl delete ns kube-mine` |
| Pod `snack` ใน default | 1 | `kubectl get pods` | `kubectl delete pod snack` |
| namespace ของ context ไม่ใช่ default | 2 | `kubectl config get-contexts` | `kubectl config set-context --current --namespace=default` |
| namespace `team-a`, `team-b` | 4, 7 | `kubectl get ns` | `kubectl delete ns team-a team-b` |
| namespace `budget` | 5, 6 | `kubectl get ns budget` | `kubectl delete ns budget` |
| context/user `intern@lab`, `intern@som-dev`, `intern` | 7, 10 | `kubectl config get-contexts` และ `kubectl config get-users` | `kubectl config delete-context <ชื่อ>` และ `kubectl config delete-user intern` |
| namespace `secure` | 8 | `kubectl get ns secure` | `kubectl delete ns secure` |
| namespace `doomed` | 9 | `kubectl get ns doomed` | `kubectl delete ns doomed` |
| namespace `som-dev`, `som-staging`, `som-prod` | 10 | `kubectl get ns -l team=som` | `kubectl delete ns som-dev som-staging som-prod` |
| port-forward ค้าง | 10 | `pgrep -af "[k]ubectl port-forward"` | `pkill -f "[k]ubectl port-forward"` |
| ตัวแปร token `T` ใน shell | 7, 10 | `echo ${#T}` (ความยาว ถ้าไม่ใช่ 0 แปลว่ายังมี) | `unset T` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get ns
kubectl get pods
kubectl config get-contexts
pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
```

ผลที่ถูกต้อง: เหลือ namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), ไม่มี Pod ใน `default` (`No resources found in default namespace.`), มี context เดียวคือ `kind-lab` ที่ NAMESPACE เป็น `default` และไม่มี port-forward ค้าง

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ `kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพเป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก
