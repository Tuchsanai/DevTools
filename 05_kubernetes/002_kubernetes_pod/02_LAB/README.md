# LAB บทที่ 2: Kubernetes Pod — จาก Pod แรกสู่ร้านอาหารแมวน้องส้ม

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Kubernetes Pod — `kubectl run`, YAML manifest, exec/logs/port-forward, labels, lifecycle, env/resources, probes, multi-container และแอป Next.js + PostgreSQL ใน Pod เดียว
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้ม ตั้งแต่สร้างคลัสเตอร์ท่าเรือ สร้าง Pod แรก เขียน YAML เอง ไล่ดีบัก Pod ที่พัง ไปจนถึงเปิด **"ร้านอาหารแมวน้องส้ม"** (Next.js + PostgreSQL) ใน Pod เดียว แล้วพิสูจน์ด้วยตาว่า "container ตาย → ข้อมูลรอด แต่ Pod หาย → ข้อมูลหาย"

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container `k8s-lab` (image `tuchsanai/devtools-kind:2569_1`, kind v0.33.0 go1.26.7, kubectl client v1.37.1 (Kustomize v5.8.1), node/server Kubernetes v1.37.0, containerd 2.3.4, Docker 29.8.2) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม (hash ท้ายชื่อ), UID, image ID และ Node ที่ Pod ไปอยู่ ในเครื่องนักศึกษาอาจต่างจากตัวอย่าง** เป็นเรื่องปกติ

ทุกไฟล์ `.yaml` ที่ LAB ใช้ มีหัวข้อย่อย **"อธิบาย YAML"** ตรงจุดที่ใช้ไฟล์นั้น และในไฟล์เองก็มี comment ภาษาไทย (`# ...`) กำกับ field สำคัญไว้ (comment ไม่มีผลต่อการทำงาน)

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

### กติกาของ LAB บทนี้

- ทุก LAB ทำในโฟลเดอร์ **`/workspace/002_kubernetes_pod/02_LAB`** ภายใน k8s-lab และ **จบด้วยการลบ Pod ของตัวเองเสมอ**
- บทนี้ใช้ **Pod เดี่ยว ๆ เท่านั้น** ไม่ใช้ Deployment หรือทรัพยากรเครือข่ายอื่น การเข้าถึงแอปใช้ `kubectl exec`, `kubectl logs` และ `kubectl port-forward` + `ssh -L` เท่านั้น
- **port 30080–30082** ที่ map ไว้ตั้งแต่บทที่ 1 **ยังไม่ใช้ในบทนี้** (เตรียมไว้สำหรับ Service ชนิด NodePort ในบทถัดไป) แม้ข้อความของ `k8s-up` จะแนะนำไว้ก็ตาม
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [สร้างคลัสเตอร์ท่าเรือ](#lab-0-สร้างคลัสเตอร์ท่าเรือ) | 15 นาที | ⭐ |
| 1 | [Pod แรกด้วย kubectl run](#lab-1-pod-แรกด้วย-kubectl-run) | 10 นาที | ⭐ |
| 2 | [Pod YAML แรก](#lab-2-pod-yaml-แรก) | 15 นาที | ⭐⭐ |
| 3 | [เข้าไปใน Pod: exec, logs, port-forward](#lab-3-เข้าไปใน-pod-exec-logs-port-forward) | 20 นาที | ⭐⭐ |
| 4 | [Labels และ Selectors](#lab-4-labels-และ-selectors) | 15 นาที | ⭐⭐ |
| 5 | [Lifecycle และการดีบัก Pod ที่พัง](#lab-5-lifecycle-และการดีบัก-pod-ที่พัง) | 25 นาที | ⭐⭐⭐ |
| 6 | [env, command และ resources](#lab-6-env-command-และ-resources) | 20 นาที | ⭐⭐⭐ |
| 7 | [Probes ตรวจสุขภาพ](#lab-7-probes-ตรวจสุขภาพ) | 15 นาที | ⭐⭐⭐ |
| 8 | [Multi-container: localhost, emptyDir, init, sidecar](#lab-8-multi-container-localhost-emptydir-init-sidecar) | 25 นาที | ⭐⭐⭐⭐ |
| 9 | [LAB สุดท้าย: ร้านอาหารแมวน้องส้ม](#lab-9-lab-สุดท้าย-ร้านอาหารแมวน้องส้ม) | 45–60 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3.5–4 ชั่วโมง (เครื่องช้าหรือเน็ตช้าอาจนานกว่านี้ เพราะต้องดึง image จาก Docker Hub)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 สร้างคลัสเตอร์](#fig-1) | 12 | [สถาปัตยกรรม Pod som-shop](#fig-12) |
| 2 | [LAB 1 kubectl run](#fig-2) | 13 | [ลำดับการเริ่ม Pod som-shop](#fig-13) |
| 3 | [LAB 2 YAML แรก](#fig-3) | 14 | [build และ kind load](#fig-14) |
| 4 | [LAB 3 exec/logs/port-forward](#fig-4) | 15 | [เปิดร้านจาก browser](#fig-15) |
| 5 | [ภาพหน้าจอจริง: หน้าเว็บ nginx ของ LAB 3](#fig-5) | 16 | [ภาพหน้าจอจริง: หน้าร้านเริ่มต้น](#fig-16) |
| 6 | [LAB 4 labels](#fig-6) | 17 | [ภาพหน้าจอจริง: หลังสั่งซื้อ 3 ครั้ง](#fig-17) |
| 7 | [LAB 5 lifecycle และดีบัก](#fig-7) | 18 | [emptyDir รอด vs หาย](#fig-18) |
| 8 | [LAB 6 env/command/resources](#fig-8) | 19 | [ภาพหน้าจอจริง: หลัง restart db](#fig-19) |
| 9 | [LAB 7 probes](#fig-9) | 20 | [ภาพหน้าจอจริง: หลังลบ Pod แล้วสร้างใหม่](#fig-20) |
| 10 | [LAB 8 multi-container](#fig-10) | 21 | [บทหน้า: แยกเว็บกับฐานข้อมูล](#fig-21) |
| 11 | [LAB 9 ร้านอาหารแมวน้องส้ม](#fig-11) |  |  |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                     ← เอกสารนี้
├── images/                       ← ภาพประกอบ + screenshots/ ภาพหน้าจอจริงของร้าน
├── labs/
│   ├── lab02-first-yaml/nginx-pod.yaml
│   ├── lab04-labels/shop-pods.yaml
│   ├── lab05-lifecycle/{completed-pod,crash-pod,onfailure-pod,bad-image-pod}.yaml
│   ├── lab06-env-resources/{env-command-pod,oom-pod,pending-pod}.yaml
│   ├── lab07-probes/{liveness-exec-pod,readiness-http-pod}.yaml
│   └── lab08-multi-container/{shared-localhost-pod,init-sidecar-pod}.yaml
└── som-shop/
    ├── app/                      ← แอป Next.js 16 + pg (Dockerfile, scripts/seed.mjs, ...)
    └── k8s/som-shop-pod.yaml     ← manifest ของ Pod ร้านน้องส้ม
```

---

## LAB 0: สร้างคลัสเตอร์ท่าเรือ

<p align="center" id="fig-1">
  <img src="images/01-lab0-cluster-up.png" alt="รูปที่ 1 LAB0 สร้างคลัสเตอร์" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: รัน k8s-up ใน k8s-lab เพื่อสร้าง kind cluster ชื่อ lab มี control-plane 1 ตัวและ worker 2 ตัว</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า container `k8s-lab` สร้างคลัสเตอร์ kind ชื่อ `lab` (1 control-plane + 2 worker) และตรวจว่าพร้อมใช้งาน

**สิ่งที่ต้องมีก่อน:** ทำ [LAB บทที่ 1](../../001_kubernetes-introduction/02_LAB/readme.md) แล้ว คือมี container `k8s-lab` (SSH port `2223`) ที่รันอยู่ และมีโฟลเดอร์ `002_kubernetes_pod` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้สั่ง `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

จากนั้น `cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `002_kubernetes_pod` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 002_kubernetes_pod k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลัง ต้องสั่ง `docker cp` ซ้ำ (ไฟล์ชื่อเดิมจะถูกเขียนทับ)

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` ต่อจากนี้หน้าต่างนี้คือ **SSH session หลัก**

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และสร้างคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/002_kubernetes_pod/02_LAB
ls
time k8s-up
```

`ls` ต้องเห็น `README.md  images  labs  som-shop` ส่วน `k8s-up` ใช้เวลาประมาณ 1 นาที (ครั้งแรกบางเครื่องอาจนานกว่านี้เพราะต้องเตรียม node image) ผลจริง (ตัดบางส่วน ส่วนที่ตัดคือตาราง `kubectl get nodes -o wide` และรายการคำแนะนำท้ายข้อความ เวลา `real` ของแต่ละเครื่องจะต่างกัน)

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

real	0m48.440s
```

> ท้ายข้อความ `k8s-up` จะมีคำแนะนำเรื่องไฟล์ตัวอย่างและ port 30080–30082 (บรรทัดสุดท้ายคือ `NodePort ที่ map ออก host: 30080 30081 30082`) ซึ่งเป็นของบทถัดไป **บทนี้ยังไม่ต้องใช้**

### ขั้นที่ 4: ตรวจคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -A
kubectl describe node lab-control-plane | grep -i taints
```

ผลจริง (ตัดคอลัมน์ `KERNEL-VERSION` ของ `get nodes`; ชื่อ Pod ที่มี hash ต่อท้าย เช่น `coredns-559f6c778d-xxxxx`, `kindnet-xxxxx`, IP ของ node และ AGE จะต่างในแต่ละเครื่อง)

```text
$ kubectl config current-context
kind-lab

$ kubectl get nodes -o wide
NAME                STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       ...   CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   23s   v1.37.0   172.19.0.3    <none>        Debian GNU/Linux 13 (trixie)   ...   containerd://2.3.4
lab-worker          Ready    <none>          13s   v1.37.0   172.19.0.4    <none>        Debian GNU/Linux 13 (trixie)   ...   containerd://2.3.4
lab-worker2         Ready    <none>          13s   v1.37.0   172.19.0.2    <none>        Debian GNU/Linux 13 (trixie)   ...   containerd://2.3.4

$ kubectl get pods -A
NAMESPACE            NAME                                        READY   STATUS    RESTARTS   AGE
kube-system          coredns-559f6c778d-n4mg8                    1/1     Running   0          13s
kube-system          coredns-559f6c778d-wh2cb                    1/1     Running   0          13s
kube-system          etcd-lab-control-plane                      1/1     Running   0          20s
kube-system          kindnet-6bjtm                               1/1     Running   0          13s
kube-system          kindnet-7vvdp                               1/1     Running   0          13s
kube-system          kindnet-ktxwk                               1/1     Running   0          13s
kube-system          kube-apiserver-lab-control-plane            1/1     Running   0          20s
kube-system          kube-controller-manager-lab-control-plane   1/1     Running   0          22s
kube-system          kube-proxy-bpx5t                            1/1     Running   0          13s
kube-system          kube-proxy-sx7nd                            1/1     Running   0          13s
kube-system          kube-proxy-z99zt                            1/1     Running   0          13s
kube-system          kube-scheduler-lab-control-plane            1/1     Running   0          20s
local-path-storage   local-path-provisioner-75f7fc7dc5-pqxsl     1/1     Running   0          13s

$ kubectl describe node lab-control-plane | grep -i taints
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
```

(ทางเลือก) ตรวจเวอร์ชันของเครื่องมือด้วย `kubectl version; kind version` ผลจริงในรอบทดลอง

```text
Client Version: v1.37.1
Kustomize Version: v5.8.1
Server Version: v1.37.0
kind v0.33.0 go1.26.7 linux/amd64
```

client (`kubectl` ใน k8s-lab) เป็น v1.37.1 ส่วน server/node เป็น v1.37.0 ต่างกันแค่ patch version จึงใช้ร่วมกันได้ปกติ

### สิ่งที่เห็น

- context คือ `kind-lab` และมี node 3 ตัวสถานะ `Ready` ได้แก่ หอบังคับการ `lab-control-plane` และเรือ `lab-worker`, `lab-worker2`
- Pod ระบบใน `kube-system` คือองค์ประกอบที่เรียนในบทที่ 1 (etcd, kube-apiserver, kube-scheduler, kube-controller-manager, kube-proxy, CoreDNS และ CNI `kindnet`) ตอนแรกบางตัวอาจยัง `0/1` รอสักครู่จะเป็น `1/1`
- `lab-control-plane` มี taint `NoSchedule` → Pod ของเราจะไปอยู่บน worker เท่านั้น

> **🤔 คำถามชวนคิด:** ทำไม `kindnet` และ `kube-proxy` มีอย่างละ 3 Pod แต่ `kube-apiserver` มีแค่ 1 Pod

---

## LAB 1: Pod แรกด้วย kubectl run

<p align="center" id="fig-2">
  <img src="images/02-lab1-kubectl-run.png" alt="รูปที่ 2 LAB1 kubectl run" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: สร้าง Pod แรกด้วย kubectl run แล้วดูสถานะด้วย kubectl get pods -o wide</em>
</p>

**เป้าหมาย:** สร้าง ดู อธิบาย และลบ Pod แบบ imperative (สั่งตรง ๆ ไม่ใช้ไฟล์)

🐧 **ใน SSH session ของ k8s-lab** (ทุกขั้นใน LAB นี้)

### ขั้นที่ 1: สร้าง Pod และดูสถานะ

```bash
kubectl run hello --image=nginx:1.27-alpine
kubectl get pods
kubectl wait --for=condition=Ready pod/hello --timeout=180s
kubectl get pods -o wide
```

```text
$ kubectl run hello --image=nginx:1.27-alpine
pod/hello created

$ kubectl get pods
NAME    READY   STATUS              RESTARTS   AGE
hello   0/1     ContainerCreating   0          0s

$ kubectl wait --for=condition=Ready pod/hello --timeout=180s
pod/hello condition met

$ kubectl get pods -o wide
NAME    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
hello   1/1     Running   0          7s    10.244.3.2   lab-worker2   <none>           <none>
```

(IP และ NODE ของนักศึกษาอาจต่างจากนี้ เช่นได้ `lab-worker` แทน `lab-worker2`)

### ขั้นที่ 2: อ่านรายละเอียดด้วย describe

```bash
kubectl describe pod hello
```

ผลจริง (ตัดเฉพาะส่วนสำคัญ)

```text
Name:             hello
Namespace:        default
Node:             lab-worker2/172.19.0.2
Labels:           run=hello
Status:           Running
IP:               10.244.3.2
Containers:
  hello:
    Image:          nginx:1.27-alpine
    State:          Running
    Ready:          True
    Restart Count:  0
...
QoS Class:                   BestEffort
...
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  7s    default-scheduler  Successfully assigned default/hello to lab-worker2
  Normal  Pulling    6s    kubelet            spec.containers{hello}: Pulling image "nginx:1.27-alpine"
  Normal  Pulled     0s    kubelet            spec.containers{hello}: Successfully pulled image "nginx:1.27-alpine" in 6.284s (6.284s including waiting). Image size: 20984244 bytes.
  Normal  Created    0s    kubelet            spec.containers{hello}: Container created
  Normal  Started    0s    kubelet            spec.containers{hello}: Container started
```

### ขั้นที่ 3: ลบ Pod

```bash
kubectl delete pod hello
kubectl get pods
```

```text
pod "hello" deleted from default namespace
No resources found in default namespace.
```

### สิ่งที่เห็น

- `kubectl run` สร้าง **Pod** (ไม่ใช่ container เดี่ยว) STATUS เปลี่ยนจาก `ContainerCreating` เป็น `Running` ภายในไม่กี่วินาที
- Pod ได้ IP ช่วง `10.244.x.x` และถูกวางบน worker ตัวใดตัวหนึ่ง (ของนักศึกษาอาจเป็น `lab-worker`)
- Events เรียงตามเส้นทางการเกิดของ Pod: `Scheduled` → `Pulling` → `Pulled` → `Created` → `Started`
- `kubectl run` ติด label `run=hello` ให้อัตโนมัติ และ Pod ที่ไม่กำหนด resources มี QoS เป็น `BestEffort`
- เมื่อลบแล้ว **ไม่มีใครสร้างคืน** Pod หายถาวร

> **🤔 คำถามชวนคิด:** สร้าง `hello` ใหม่อีกครั้งแล้วดู IP และ NODE ได้ค่าเดิมหรือไม่ เพราะอะไร (อย่าลืมลบหลังทดลอง)

---

## LAB 2: Pod YAML แรก

<p align="center" id="fig-3">
  <img src="images/03-lab2-first-yaml.png" alt="รูปที่ 3 LAB2 YAML แรก" width="900"><br>
  <em><b>รูปที่ 3</b> LAB2: ร่าง YAML ด้วย --dry-run=client -o yaml เขียน nginx-pod.yaml แล้ว kubectl apply -f</em>
</p>

**เป้าหมาย:** ร่าง YAML ด้วยเครื่องมือ อ่านไฟล์ `nginx-pod.yaml` สร้าง Pod แบบ declarative และเห็นทั้ง `spec` กับ `status`

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/002_kubernetes_pod/02_LAB`)

### ขั้นที่ 1: ให้ kubectl ร่าง YAML ให้

```bash
kubectl run web --image=nginx:1.27-alpine --dry-run=client -o yaml
kubectl explain pod.spec.containers.ports | head -30
```

```text
$ kubectl run web --image=nginx:1.27-alpine --dry-run=client -o yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: web
  name: web
spec:
  containers:
  - image: nginx:1.27-alpine
    name: web
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}

$ kubectl explain pod.spec.containers.ports | head -30
KIND:       Pod
VERSION:    v1

FIELD: ports <[]ContainerPort>

DESCRIPTION:
    List of ports to expose from the container. Not specifying a port here DOES
    NOT prevent that port from being exposed. ...
FIELDS:
  containerPort	<integer> -required-
    Number of port to expose on the pod's IP address. This must be a valid port
    number, 0 < x < 65536.
...
```

`--dry-run=client` แค่พิมพ์ YAML ออกมา **ยังไม่ได้สร้าง Pod** (ถ้าต้องการเก็บเป็นไฟล์ ให้ต่อท้ายด้วย `> my-pod.yaml`)

### ขั้นที่ 2: อ่านไฟล์ YAML ของ LAB

```bash
cat labs/lab02-first-yaml/nginx-pod.yaml
```

```yaml
# LAB 2: Pod YAML แรก — เว็บเซิร์ฟเวอร์ nginx 1 container
apiVersion: v1            # กลุ่ม/เวอร์ชันของ API ที่ใช้ (Pod อยู่ในกลุ่ม core = v1)
kind: Pod                 # ชนิดของ object ที่ต้องการสร้าง
metadata:                 # ข้อมูลระบุตัวตนของ object
  name: web               # ชื่อ Pod (ต้องไม่ซ้ำใน namespace เดียวกัน)
  labels:                 # ป้ายแท็ก key: value ไว้ค้นหา/จัดกลุ่ม
    app: web
    owner: nong-som
spec:                     # สิ่งที่เราอยากได้ (desired state)
  containers:             # รายการ container ใน Pod (เป็น list จึงขึ้นต้นด้วย -)
    - name: nginx         # ชื่อ container ภายใน Pod
      image: nginx:1.27-alpine   # image + tag (ระบุ tag เสมอ ไม่ใช้ latest)
      ports:
        - containerPort: 80      # บอกว่าแอปฟัง port 80 (เป็นข้อมูลประกอบ ไม่ได้เปิด port ให้ภายนอก)
```

#### อธิบาย YAML: `labs/lab02-first-yaml/nginx-pod.yaml`

| field | ค่า | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|---|
| `apiVersion` | `v1` | Pod อยู่ในกลุ่ม API หลัก (core) จึงเขียนแค่ `v1` | บรรทัด `1:apiVersion: v1` ในขั้นที่ 4 |
| `kind` | `Pod` | บอก kube-apiserver ว่าจะสร้าง object ชนิด Pod | `pod/web created` |
| `metadata.name` | `web` | ชื่อ Pod ต้องไม่ซ้ำใน namespace | `create` ซ้ำจึงได้ `AlreadyExists` (ขั้นที่ 5) |
| `metadata.labels` | `app: web`, `owner: nong-som` | ป้ายสำหรับค้นหา/จัดกลุ่ม (ใช้จริงใน LAB 4) ต่างจาก `kubectl run` ที่ติด `run=web` ให้เอง | คอลัมน์ `LABELS` = `app=web,owner=nong-som` |
| `spec.containers` | list 1 ตัว | Pod นี้มี container เดียว ขึ้นต้นด้วย `-` เพราะเป็น list | READY `1/1` |
| `containers[].name` | `nginx` | ชื่อ container ภายใน Pod (ใช้กับ `-c` ภายหลัง) ตั้งต่างจากชื่อ Pod ได้ | `kubectl run` ตั้งชื่อ container = ชื่อ Pod (`web`) แต่ไฟล์นี้ใช้ `nginx` |
| `containers[].image` | `nginx:1.27-alpine` | ระบุ tag ชัดเจนเพื่อให้ได้เวอร์ชันเดิมทุกครั้ง (ไม่ใช้ `latest`) | LAB 3 เห็น `nginx version: nginx/1.27.5` |
| `ports[].containerPort` | `80` | **ข้อมูลประกอบ** ว่าแอปฟัง port 80 ไม่ได้เปิด port ออกนอก Pod และแก้บน Pod ที่รันอยู่ไม่ได้ | `22:    - containerPort: 80` และเปลี่ยนเป็น 8080 แล้วได้ `Forbidden` |

field ที่ **ไม่ได้เขียน** (เช่น `restartPolicy: Always`, `dnsPolicy: ClusterFirst`, `imagePullPolicy: IfNotPresent`) ระบบเติมค่าเริ่มต้นให้ จึงเห็นใน `kubectl get pod web -o yaml` และใน `kubectl diff`

### ขั้นที่ 3: ตรวจก่อนแล้ว apply

```bash
kubectl diff -f labs/lab02-first-yaml/nginx-pod.yaml | head -20
kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
kubectl wait --for=condition=Ready pod/web --timeout=120s && kubectl get pod web -o wide --show-labels
```

```text
$ kubectl diff -f labs/lab02-first-yaml/nginx-pod.yaml | head -20
diff -u -N /tmp/LIVE-2353270854/v1.Pod.default.web /tmp/MERGED-4131215826/v1.Pod.default.web
--- /tmp/LIVE-2353270854/v1.Pod.default.web	2026-10-05 17:00:33.954052467 +0700
+++ /tmp/MERGED-4131215826/v1.Pod.default.web	2026-10-05 17:00:33.954052467 +0700
@@ -0,0 +1,67 @@
+apiVersion: v1
+kind: Pod
...

$ kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
pod/web created

$ kubectl wait --for=condition=Ready pod/web --timeout=120s && kubectl get pod web -o wide --show-labels
pod/web condition met
NAME   READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES   LABELS
web    1/1     Running   0          0s    10.244.3.4   lab-worker2   <none>           <none>            app=web,owner=nong-som
```

(ชื่อไฟล์ `/tmp/LIVE-...`/`/tmp/MERGED-...` เวลา, IP และ NODE จะต่างในแต่ละครั้ง)

`kubectl diff` แสดงทุกบรรทัดเป็น `+` เพราะยังไม่มี Pod `web` ในคลัสเตอร์ (ทั้งหมดคือของใหม่)

### ขั้นที่ 4: ดู spec และ status ของจริง

```bash
kubectl get pod web -o yaml | grep -nE "^(apiVersion|kind|metadata|spec|status):|podIP:|phase:|qosClass:|  - containerPort"
kubectl get pod web -o jsonpath="{.status.phase} {.status.podIP}{\"\\n\"}"
```

```text
1:apiVersion: v1
2:kind: Pod
3:metadata:
16:spec:
22:    - containerPort: 80
70:status:
135:  phase: Running
136:  podIP: 10.244.3.4
139:  qosClass: BestEffort

Running 10.244.3.4
```

ลองเปิดดูทั้งหมดด้วย `kubectl get pod web -o yaml | less` (กด `q` เพื่อออก) จะเห็นว่าระบบเติมค่าเริ่มต้นใน `spec` และเขียน `status` ให้ยาวกว่า 130 บรรทัด (รอบทดลองจริง `kubectl get pod web -o yaml | wc -l` ได้ `141`)

### ขั้นที่ 5: apply ซ้ำ, create ซ้ำ และลองแก้ Pod ที่รันอยู่

```bash
kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
kubectl create -f labs/lab02-first-yaml/nginx-pod.yaml
sed "s/containerPort: 80/containerPort: 8080/" labs/lab02-first-yaml/nginx-pod.yaml > /tmp/web-8080.yaml
kubectl apply -f /tmp/web-8080.yaml
```

```text
$ kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
pod/web unchanged

$ kubectl create -f labs/lab02-first-yaml/nginx-pod.yaml
Error from server (AlreadyExists): error when creating "labs/lab02-first-yaml/nginx-pod.yaml": pods "web" already exists

$ kubectl apply -f /tmp/web-8080.yaml
The Pod "web" is invalid: spec: Forbidden: pod updates may not change fields other than `spec.containers[*].image`,`spec.initContainers[*].image`,`spec.activeDeadlineSeconds`,`spec.tolerations` (only additions to existing tolerations),`spec.terminationGracePeriodSeconds` (allow it to be set to 1 if it was previously negative)
@@ -104,7 +104,7 @@
...
-     "ContainerPort": 80,
+     "ContainerPort": 8080,
...
```

หลังข้อความ `Forbidden` kubectl แสดง diff ของ field ที่เราพยายามเปลี่ยน (`ContainerPort` 80 → 8080) ทั้ง `create` และ `apply` ที่ล้มเหลวจบด้วย exit code 1

### ขั้นที่ 6: ลบ Pod

```bash
kubectl delete -f labs/lab02-first-yaml/nginx-pod.yaml
kubectl get pods
```

```text
pod "web" deleted from default namespace
No resources found in default namespace.
```

### สิ่งที่เห็น

- `apply` เป็นแบบ declarative: ไฟล์ไม่เปลี่ยน → `unchanged` ส่วน `create` สร้างซ้ำไม่ได้ → `AlreadyExists`
- Pod ที่รันอยู่ **แก้ได้แค่บาง field** (เช่น `image`) การเปลี่ยน `containerPort` ถูกปฏิเสธด้วย `Forbidden` ต้องลบแล้วสร้างใหม่
- `-o yaml` + `grep`/`jsonpath` ช่วยดึงเฉพาะค่าที่สนใจ

> **🏆 ท้าทาย:** เขียนไฟล์ `/tmp/my-pod.yaml` เองจากผล dry-run ให้ Pod ชื่อ `my-web` มี label `owner=<ชื่อเล่นของคุณ>` แล้ว apply, ตรวจด้วย `--show-labels` และลบทิ้ง

---

## LAB 3: เข้าไปใน Pod: exec, logs, port-forward

<p align="center" id="fig-4">
  <img src="images/04-lab3-exec-logs-portforward.png" alt="รูปที่ 4 LAB3 exec/logs/port-forward" width="900"><br>
  <em><b>รูปที่ 4</b> LAB3: เข้าไปใน Pod ด้วย exec แก้หน้าเว็บ ดู access log และเปิดเว็บผ่าน port-forward + ssh -L</em>
</p>

**เป้าหมาย:** สำรวจภายใน container, แก้หน้าเว็บ, ดู access log และ **เปิดเว็บใน Pod จาก browser บนเครื่องนักศึกษา**

### ขั้นที่ 1: สร้าง Pod และสำรวจภายใน

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml && kubectl wait --for=condition=Ready pod/web --timeout=120s
kubectl exec web -- sh -c "hostname; whoami; head -2 /etc/os-release; nginx -v; ls /usr/share/nginx/html"
```

```text
pod/web created
pod/web condition met
web
root
NAME="Alpine Linux"
ID=alpine
nginx version: nginx/1.27.5
50x.html
index.html
```

#### อธิบาย YAML: ใช้ `labs/lab02-first-yaml/nginx-pod.yaml` ซ้ำ

LAB นี้ใช้ไฟล์เดียวกับ LAB 2 (ดูตารางอธิบายทีละ field ที่ [LAB 2 ขั้นที่ 2](#lab-2-pod-yaml-แรก)) จุดที่เกี่ยวกับ LAB นี้คือ

- `containers[].image: nginx:1.27-alpine` → เป็น Alpine Linux จึงเห็น `ID=alpine`, `nginx version: nginx/1.27.5` และ **ไม่มี `bash`** (ผลจริง `which bash` ไม่เจอ ต้องใช้ `sh`)
- `containers[].name: nginx` → Pod มี container เดียว `kubectl exec`/`logs` จึงไม่ต้องใส่ `-c`
- `ports[].containerPort: 80` → เป็นแค่ข้อมูลประกอบ การเข้าถึงจากภายนอกต้องใช้ `kubectl port-forward pod/web 8080:80` (เลขขวา `80` คือ port ที่ nginx ฟังจริงใน Pod)

ลองเข้า shell แบบโต้ตอบด้วย `kubectl exec -it web -- sh` (image alpine ไม่มี `bash`) สำรวจด้วย `ls`, `cat /etc/nginx/conf.d/default.conf` แล้วพิมพ์ `exit` เพื่อออก

### ขั้นที่ 2: เปลี่ยนหน้าเว็บเป็นของน้องส้ม

```bash
kubectl exec web -- sh -c "echo \"<meta charset=utf-8><h1>สวัสดีจากน้องส้ม 🐱</h1>\" > /usr/share/nginx/html/index.html"
kubectl exec web -- cat /usr/share/nginx/html/index.html
```

```text
<meta charset=utf-8><h1>สวัสดีจากน้องส้ม 🐱</h1>
```

> ใส่ `<meta charset=utf-8>` ไว้หน้าข้อความ เพราะ nginx ส่ง header `Content-Type: text/html` โดยไม่บอก charset ถ้าไม่ใส่ ภาษาไทยอาจแสดงเพี้ยนใน browser

### ขั้นที่ 3: เปิด port-forward (ค้างไว้)

🐧 **ใน SSH session หลักของ k8s-lab**

```bash
kubectl port-forward pod/web 8080:80
```

```text
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
```

คำสั่งนี้ **ค้างอยู่** (ห้ามปิด) มันเปิด port 8080 ที่ `127.0.0.1` ของ k8s-lab แล้วส่งต่อเข้า port 80 ของ Pod `web` ทุกครั้งที่มีการเชื่อมต่อจะพิมพ์ `Handling connection for 8080`

### ขั้นที่ 4: เปิดท่อ SSH จากเครื่องนักศึกษา

🖥️ **บนเครื่องนักศึกษา** เปิด Terminal/PowerShell **หน้าต่างใหม่**

```bash
ssh -p 2223 -L 8080:localhost:8080 root@localhost
```

ใส่รหัส `passwd` หน้าต่างนี้ทำสองหน้าที่พร้อมกัน คือ (1) เป็นท่อส่ง port 8080 ของเครื่องนักศึกษาไปที่ `localhost:8080` ใน k8s-lab และ (2) เป็น shell ของ k8s-lab อีกหน้าต่างหนึ่ง **ให้เปิดค้างไว้ตลอดที่ใช้ browser**

🐧 **ใน SSH session ที่สอง (หน้าต่างท่อ)** ทดสอบด้วย curl

```bash
curl -s localhost:8080
curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/nope
```

```text
<meta charset=utf-8><h1>สวัสดีจากน้องส้ม 🐱</h1>
404
```

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:8080** จะเห็นหัวข้อ "สวัสดีจากน้องส้ม 🐱" (ในรอบทดลองจริง เครื่องที่ใช้ทดสอบไม่ได้เปิด SSH ของ container ออกภายนอก จึงเปิดท่อ `ssh -L 18080:localhost:8080` ภายใน k8s-lab ไปยัง sshd ของตัวเอง กลไกเหมือนกันต่างแค่เลข port ฝั่งซ้าย และดึงหน้าเว็บผ่านท่อได้ข้อความเดียวกัน หน้าต่าง port-forward พิมพ์ `Handling connection for 8080` ทุกครั้งที่มี request)

<p align="center" id="fig-5">
  <img src="images/screenshots/20261005_1725_lab002_02-lab3-nginx.png" alt="รูปที่ 5 ภาพหน้าจอจริง หน้าเว็บ nginx สวัสดีจากน้องส้ม" width="700"><br>
  <em><b>รูปที่ 5</b> ภาพหน้าจอจริงจากการทดลอง: หน้าเว็บของ Pod web (nginx) หลังแก้ index.html ใน LAB 3 แสดงหัวข้อ "สวัสดีจากน้องส้ม 🐱" บนหน้าขาว (ตอนถ่ายภาพเปิดผ่าน NodePort Service ชั่วคราวที่เพิ่มเองเพื่อถ่ายภาพเท่านั้น นักศึกษาใช้ port-forward + ssh -L ตามขั้นข้างต้น ผลที่เห็นเหมือนกัน)</em>
</p>

```text
browser (เครื่องนักศึกษา) http://localhost:8080
   │  ssh -p 2223 -L 8080:localhost:8080 root@localhost      ← หน้าต่าง 🖥️ ใหม่
   ▼
k8s-lab 127.0.0.1:8080
   │  kubectl port-forward pod/web 8080:80                   ← SSH session หลัก 🐧
   ▼
Pod web : 80
```

### ขั้นที่ 5: ดู access log แบบสด

🐧 **ใน SSH session ที่สอง**

```bash
kubectl logs web --tail=5
kubectl logs -f web
```

ผลจริงของ `--tail=5` (รอบทดลองนี้มี request เพียง 3 ครั้ง คือ curl `/`, curl `/nope` และ request ผ่านท่อที่จำลอง browser ด้วย curl ซึ่งตั้ง User-Agent เป็น `Mozilla/5.0 (browser-sim)` บรรทัดแรกจึงยังเป็น log ตอน nginx เริ่มทำงาน)

```text
2026/10/05 10:02:17 [notice] 1#1: start worker process 65
127.0.0.1 - - [05/Oct/2026:10:02:26 +0000] "GET / HTTP/1.1" 200 83 "-" "curl/8.5.0" "-"
2026/10/05 10:02:26 [error] 35#35: *2 open() "/usr/share/nginx/html/nope" failed (2: No such file or directory), client: 127.0.0.1, server: localhost, request: "GET /nope HTTP/1.1", host: "localhost:8080"
127.0.0.1 - - [05/Oct/2026:10:02:26 +0000] "GET /nope HTTP/1.1" 404 153 "-" "curl/8.5.0" "-"
127.0.0.1 - - [05/Oct/2026:10:02:26 +0000] "GET / HTTP/1.1" 200 83 "-" "Mozilla/5.0 (browser-sim)" "-"
```

> **ลำดับบรรทัดอาจสลับกันได้:** บรรทัด `[error] ... open() "/usr/share/nginx/html/nope" failed` (error log ออกทาง stderr) กับบรรทัด `"GET /nope HTTP/1.1" 404` (access log ออกทาง stdout) มาจากคนละ stream จึงอาจขึ้นก่อนหรือหลังกันก็ได้ จำนวน/เวลาของบรรทัดที่เห็นใน `--tail=5` ขึ้นกับจำนวน request ที่นักศึกษาส่งไปก่อนหน้า (ถ้า request น้อยจะยังเห็นบรรทัด `[notice] ... start worker process`) และ User-Agent ของ browser จริงจะเป็นข้อความยาว ๆ เช่น `Mozilla/5.0 (Windows NT 10.0; ...)`

ขณะ `logs -f` ทำงาน ให้กด refresh ใน browser จะเห็นบรรทัด `GET /` ใหม่ปรากฏทันที (จาก browser จะเห็น User-Agent ของ browser แทน `curl`) กด **Ctrl+C** เพื่อหยุด `logs -f` ผลจริงจากรอบทดลอง (request จำลอง browser ผ่านท่อ โดยตั้ง User-Agent แบบ Chrome)

```text
127.0.0.1 - - [05/Oct/2026:10:02:29 +0000] "GET / HTTP/1.1" 200 83 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0" "-"
```

### ขั้นที่ 6: ปิดทุกอย่างและลบ Pod

1. 🐧 SSH session หลัก: กด **Ctrl+C** เพื่อหยุด `kubectl port-forward`
2. 🖥️ หน้าต่างท่อ: พิมพ์ `exit` เพื่อปิด SSH tunnel
3. 🐧 SSH session หลัก:

```bash
kubectl delete -f labs/lab02-first-yaml/nginx-pod.yaml
```

```text
pod "web" deleted from default namespace
```

### สิ่งที่เห็น

- `kubectl exec` รันคำสั่งใน container ได้เหมือนอยู่ในเครื่องนั้น การแก้ไฟล์ด้วยวิธีนี้ **เป็นการชั่วคราว** ถ้า Pod ถูกลบไฟล์ที่แก้จะหาย
- log ของ nginx มีทั้ง access log (stdout) และ error log (stderr) `kubectl logs` เห็นทั้งสองอย่าง
- request ใน log มาจาก `127.0.0.1` เพราะ port-forward ส่งเข้ามาทาง loopback ภายใน Pod
- การเปิดเว็บต้องต่อท่อ 2 ช่วง และ **ไม่ต้องใช้ port 30080–30082** ในบทนี้

> **🤔 คำถามชวนคิด:** ถ้าปิดหน้าต่าง `ssh -L` แต่ port-forward ยังทำงาน `curl localhost:8080` ใน k8s-lab ยังได้ผลไหม และ browser บนเครื่องนักศึกษายังเปิดได้ไหม

---

## LAB 4: Labels และ Selectors

<p align="center" id="fig-6">
  <img src="images/05-lab4-labels.png" alt="รูปที่ 6 LAB4 labels" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4: ติดป้าย label ให้ Pod 3 ตัวและใช้ -l เลือกเฉพาะกลุ่มที่ต้องการ</em>
</p>

**เป้าหมาย:** สร้าง Pod หลายตัวจากไฟล์เดียว (multi-document `---`) ติด แก้ ลบ label และค้นหาด้วย selector

ไฟล์ `labs/lab04-labels/shop-pods.yaml` มี 3 Pod

| Pod | image | labels |
|---|---|---|
| `shop-web` | `nginx:1.27-alpine` | `app=som-shop`, `tier=web` |
| `shop-cache` | `busybox:1.36` | `app=som-shop`, `tier=cache` |
| `toy-web` | `nginx:1.27-alpine` | `app=toy-shop`, `tier=web` |

#### อธิบาย YAML: `labs/lab04-labels/shop-pods.yaml`

ส่วนสำคัญ (Pod แรกเต็ม ๆ และส่วนที่ต่างของอีกสองตัว)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: shop-web
  labels:             # label = ป้าย key: value ที่ใช้เลือกด้วย -l
    app: som-shop     # ร้านของน้องส้ม
    tier: web         # ชั้นหน้าเว็บ
spec:
  containers:
    - name: nginx
      image: nginx:1.27-alpine
---                   # ขึ้น document ใหม่ = object ถัดไปในไฟล์เดียวกัน
...
  name: shop-cache
  labels:
    app: som-shop
    tier: cache       # ชั้นแคช
...
    - name: cache
      image: busybox:1.36
      command: ["sh", "-c", "echo cache ready; sleep 3600"]   # จำลองว่าเป็น cache
---
...
  name: toy-web
  labels:
    app: toy-shop     # ร้านของเล่น (คนละร้าน)
    tier: web
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `---` | คั่น YAML หลาย document ในไฟล์เดียว แต่ละ document คือ object หนึ่งตัว | `apply` ครั้งเดียวได้ `created` 3 บรรทัด และ `delete -f` ลบได้ทั้งไฟล์ |
| `metadata.labels.app` | บอกว่า Pod เป็นของร้านไหน ตั้งให้ 2 ตัวเป็น `som-shop` และ 1 ตัวเป็น `toy-shop` เพื่อให้มีทั้งตัวที่ตรงและไม่ตรง selector | `-l app=som-shop` ได้ 2 ตัว, `-l app!=som-shop` ได้แค่ `toy-web` |
| `metadata.labels.tier` | บอกชั้นของระบบ (`web`/`cache`) ตั้งให้ `toy-web` เป็น `web` เหมือน `shop-web` เพื่อให้ selector ข้ามร้านได้ | `-l tier=web` ได้ `shop-web` + `toy-web`, `-l app=som-shop,tier=web` (AND) เหลือ `shop-web` ตัวเดียว |
| `shop-cache` → `command: [... "sleep 3600"]` | busybox ไม่มีโปรแกรมที่รันค้างเอง ถ้าไม่ใส่ `sleep` container จะจบทันทีและถูก restart วน | Pod `shop-cache` เป็น `1/1 Running` เหมือนอีกสองตัว |
| ไม่มี `annotations` ในไฟล์ | annotation ถูกเพิ่มทีหลังด้วย `kubectl annotate` ในขั้นที่ 3 | `describe` เห็น `Annotations: description: ... owner: น้องส้ม` |

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: สร้างและดู labels

```bash
kubectl apply -f labs/lab04-labels/shop-pods.yaml && kubectl wait --for=condition=Ready pod --all --timeout=120s
kubectl get pods --show-labels
```

```text
pod/shop-web created
pod/shop-cache created
pod/toy-web created
pod/shop-cache condition met
pod/shop-web condition met
pod/toy-web condition met
NAME         READY   STATUS    RESTARTS   AGE   LABELS
shop-cache   1/1     Running   0          6s    app=som-shop,tier=cache
shop-web     1/1     Running   0          6s    app=som-shop,tier=web
toy-web      1/1     Running   0          6s    app=toy-shop,tier=web
```

### ขั้นที่ 2: เลือกด้วย selector

```bash
kubectl get pods -l app=som-shop
kubectl get pods -l tier=web
kubectl get pods -l app=som-shop,tier=web
kubectl get pods -l 'tier in (web,cache)'
kubectl get pods -l app!=som-shop
kubectl get pods -L app,tier
```

```text
$ kubectl get pods -l app=som-shop
NAME         READY   STATUS    RESTARTS   AGE
shop-cache   1/1     Running   0          6s
shop-web     1/1     Running   0          6s

$ kubectl get pods -l tier=web
NAME       READY   STATUS    RESTARTS   AGE
shop-web   1/1     Running   0          6s
toy-web    1/1     Running   0          6s

$ kubectl get pods -l app=som-shop,tier=web
NAME       READY   STATUS    RESTARTS   AGE
shop-web   1/1     Running   0          6s

$ kubectl get pods -l 'tier in (web,cache)'
NAME         READY   STATUS    RESTARTS   AGE
shop-cache   1/1     Running   0          7s
shop-web     1/1     Running   0          7s
toy-web      1/1     Running   0          7s

$ kubectl get pods -l app!=som-shop
NAME      READY   STATUS    RESTARTS   AGE
toy-web   1/1     Running   0          7s

$ kubectl get pods -L app,tier
NAME         READY   STATUS    RESTARTS   AGE   APP        TIER
shop-cache   1/1     Running   0          7s    som-shop   cache
shop-web     1/1     Running   0          7s    som-shop   web
toy-web      1/1     Running   0          7s    toy-shop   web
```

> ใส่ `'...'` ครอบ selector ที่มีวงเล็บหรือ `!` เพื่อไม่ให้ shell ตีความเอง

### ขั้นที่ 3: เพิ่ม แก้ ลบ label และใส่ annotation

```bash
kubectl label pod toy-web env=dev && kubectl get pod toy-web --show-labels
kubectl label pod toy-web env=prod
kubectl label pod toy-web env=prod --overwrite && kubectl get pod toy-web -L env
kubectl label pod toy-web env- && kubectl get pod toy-web --show-labels
kubectl annotate pod shop-web owner="น้องส้ม" description="หน้าร้านทดลอง"
kubectl describe pod shop-web | sed -n "/^Labels/,/^Status/p"
```

```text
pod/toy-web labeled
NAME      READY   STATUS    RESTARTS   AGE   LABELS
toy-web   1/1     Running   0          7s    app=toy-shop,env=dev,tier=web

error: 'env' already has a value (dev), and --overwrite is false

pod/toy-web labeled
NAME      READY   STATUS    RESTARTS   AGE   ENV
toy-web   1/1     Running   0          7s    prod

pod/toy-web unlabeled
NAME      READY   STATUS    RESTARTS   AGE   LABELS
toy-web   1/1     Running   0          7s    app=toy-shop,tier=web

pod/shop-web annotated
Labels:           app=som-shop
                  tier=web
Annotations:      description: หน้าร้านทดลอง
                  owner: น้องส้ม
Status:           Running
```

### ขั้นที่ 4: ลบเป็นกลุ่มด้วย label แล้วเก็บกวาด

```bash
kubectl delete pod -l app=som-shop
kubectl get pods --show-labels
kubectl delete -f labs/lab04-labels/shop-pods.yaml --ignore-not-found
```

```text
pod "shop-cache" deleted from default namespace
pod "shop-web" deleted from default namespace
NAME      READY   STATUS    RESTARTS   AGE   LABELS
toy-web   1/1     Running   0          39s   app=toy-shop,tier=web
pod "toy-web" deleted from default namespace
```

### สิ่งที่เห็น

- ไฟล์เดียวสร้างได้หลาย object ด้วย `---`
- `,` ใน selector คือ AND ส่วน `in (...)` คือ "ค่าใดค่าหนึ่งในชุด"
- การแก้ label ที่มีค่าอยู่แล้วต้องใช้ `--overwrite` ลบ label ด้วย `key-`
- annotation ใส่ภาษาไทยได้ แต่ใช้ `-l` ค้นหาไม่ได้
- `delete -l` ลบทุก Pod ที่ตรง selector ในคำสั่งเดียว (ใช้อย่างระวัง!) ส่วน `--ignore-not-found` ทำให้ไม่ error เมื่อ Pod บางตัวถูกลบไปแล้ว

> **🏆 ท้าทาย:** หา Pod ทั้งหมดในทุก namespace ที่มี label key `k8s-app` ด้วย `kubectl get pods -A -l k8s-app` แล้วอธิบายว่าเป็น Pod อะไร

---

## LAB 5: Lifecycle และการดีบัก Pod ที่พัง

<p align="center" id="fig-7">
  <img src="images/06-lab5-lifecycle-debug.png" alt="รูปที่ 7 LAB5 lifecycle และดีบัก" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: สังเกต Completed, CrashLoopBackOff และ ImagePullBackOff แล้วใช้ describe กับ logs --previous หาสาเหตุ</em>
</p>

**เป้าหมาย:** อ่าน phase, STATUS, RESTARTS ให้ออก และไล่หาสาเหตุ Pod ที่พังด้วย `describe` และ `logs --previous`

**ตาราง** Pod ทั้ง 4 ตัวใน `labs/lab05-lifecycle/`

| ไฟล์ | สิ่งที่ทำ | restartPolicy | คาดว่าจะเห็น |
|---|---|---|---|
| `completed-pod.yaml` | busybox echo แล้ว `exit 0` | `Never` | `Completed`, phase `Succeeded` |
| `crash-pod.yaml` | echo, รอ 3 วินาที, `exit 1` ทุกครั้ง | `Always` | RESTARTS เพิ่ม, `Error`/`CrashLoopBackOff` |
| `onfailure-pod.yaml` | รอบแรก `exit 1` รอบสอง `exit 0` (ใช้ emptyDir `/work` จำว่าเคยลองแล้ว ซึ่งจะเรียนละเอียดใน LAB 8) | `OnFailure` | restart 1 ครั้งแล้ว `Completed` |
| `bad-image-pod.yaml` | `image: nginx:9.99-doesnotexist` | (ค่าเริ่มต้น) | `ErrImagePull` ⇄ `ImagePullBackOff` |

#### อธิบาย YAML: ไฟล์ทั้ง 4 ใน `labs/lab05-lifecycle/`

ทั้ง 4 ไฟล์เป็น Pod container เดียว ต่างกันที่ **`restartPolicy`** (ระดับ Pod ใช้กับทุก container) และ **คำสั่งที่จบด้วย exit code อะไร** ส่วนสำคัญของแต่ละไฟล์

```yaml
# completed-pod.yaml
spec:
  restartPolicy: Never    # จบแล้วไม่ต้องเริ่มใหม่
  containers:
    - name: job
      image: busybox:1.36
      command: ["sh", "-c", "echo 'น้องส้มนับสต็อกเสร็จแล้ว'; exit 0"]   # พิมพ์ข้อความแล้วจบด้วย exit 0 (สำเร็จ)
```

```yaml
# crash-pod.yaml
spec:
  restartPolicy: Always   # ค่าเริ่มต้น: ล้มเมื่อไรก็เริ่มใหม่ (รอนานขึ้นเรื่อย ๆ)
  containers:
    - name: app
      image: busybox:1.36
      # stdout 1 บรรทัด, รอ 3 วิ, stderr 1 บรรทัด แล้ว exit 1 (ล้ม) ทุกรอบ
      command: ["sh", "-c", "echo 'กำลังเปิดร้าน...'; sleep 3; echo 'ERROR: หาไฟล์เมนูไม่เจอ' >&2; exit 1"]
```

```yaml
# onfailure-pod.yaml
spec:
  restartPolicy: OnFailure   # exit ≠ 0 → restart, exit 0 → จบ (Completed)
  containers:
    - name: app
      image: busybox:1.36
      ...
      command: ["sh", "-c", "if [ -f /work/tried ]; then echo 'รอบสองสำเร็จ'; exit 0; else touch /work/tried; echo 'รอบแรกล้ม'; exit 1; fi"]
      volumeMounts:
        - name: work         # ต้องตรงกับชื่อใน volumes ด้านล่าง
          mountPath: /work   # ตำแหน่งที่ volume โผล่ใน container
  volumes:
    - name: work
      emptyDir: {}           # โฟลเดอร์ว่างที่มีอายุเท่ากับ Pod
```

```yaml
# bad-image-pod.yaml
spec:                     # ไม่ระบุ restartPolicy จึงได้ค่าเริ่มต้น Always
  containers:
    - name: web
      image: nginx:9.99-doesnotexist   # tag ผิด! แก้เป็น nginx:1.27-alpine แล้วลบ/apply ใหม่
```

| ไฟล์ / field | ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| completed: `restartPolicy: Never` + `exit 0` | งานที่ทำครั้งเดียวจบ ไม่ต้องเริ่มใหม่ | `0/1 Completed` RESTARTS 0, `phase=Succeeded exitCode=0 reason=Completed` |
| crash: `restartPolicy: Always` + `exit 1` | จำลองแอปที่ล้มทุกครั้ง kubelet จึง restart วนไม่จบ | RESTARTS เพิ่มเรื่อย ๆ, STATUS สลับ `Running`/`Error`/`CrashLoopBackOff`, `back-off` ยาวขึ้นจนตันที่ `5m0s` |
| crash: `sleep 3` และ `>&2` | ให้ container มีชีวิตอยู่ 3 วินาทีพอให้เห็น `Running` และส่งข้อความ error ทาง stderr | snapshot ~3s/~20s เห็น `1/1 Running`; `logs --previous` เห็นทั้งบรรทัด stdout และ stderr |
| onfailure: `restartPolicy: OnFailure` | restart เฉพาะตอน exit ≠ 0 | รอบแรก `exit 1` → restart 1 ครั้ง → รอบสอง `exit 0` → `Completed`, `restarts=1`, `phase=Succeeded` |
| onfailure: `volumes` emptyDir + `volumeMounts` `/work` | ไฟล์ `/work/tried` ต้องรอดข้ามการ restart container จึงต้องอยู่บน volume ระดับ Pod (ถ้าเขียนลงไฟล์ระบบของ container เอง จะหายทุกครั้งที่ restart แล้วล้มวนตลอด) | log สุดท้ายคือ `รอบสองสำเร็จ` |
| bad-image: `image: nginx:9.99-doesnotexist` | tag ที่ไม่มีอยู่จริงบน Docker Hub | Events `... not found`, STATUS `ErrImagePull` ⇄ `ImagePullBackOff`; แก้ด้วย `sed` เปลี่ยน tag (comment ท้ายบรรทัดติดไปด้วย จึงเห็นใน `grep image:`) |

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: สร้างทั้ง 4 Pod แล้วเฝ้าดู

```bash
kubectl apply -f labs/lab05-lifecycle/completed-pod.yaml -f labs/lab05-lifecycle/crash-pod.yaml -f labs/lab05-lifecycle/onfailure-pod.yaml -f labs/lab05-lifecycle/bad-image-pod.yaml
kubectl get pods
```

สั่ง `kubectl get pods` ซ้ำทุก ~10 วินาที (หรือใช้ `kubectl get pods -w` แล้วกด Ctrl+C เมื่อพอ) ผลจริงที่เวลาต่าง ๆ

```text
# ~3s
NAME            READY   STATUS              RESTARTS   AGE
bad-image-pod   0/1     ContainerCreating   0          3s
completed-pod   0/1     ContainerCreating   0          3s
crash-pod       1/1     Running             0          3s
onfailure-pod   0/1     ContainerCreating   0          3s

# ~10s
NAME            READY   STATUS         RESTARTS     AGE
bad-image-pod   0/1     ErrImagePull   0            11s
completed-pod   0/1     Completed      0            11s
crash-pod       0/1     Error          1 (7s ago)   11s
onfailure-pod   0/1     Completed      1 (2s ago)   11s

# ~20s
NAME            READY   STATUS         RESTARTS      AGE
bad-image-pod   0/1     ErrImagePull   0             20s
completed-pod   0/1     Completed      0             20s
crash-pod       1/1     Running        2 (13s ago)   20s
onfailure-pod   0/1     Completed      1 (11s ago)   20s

# ~7 นาที
NAME            READY   STATUS             RESTARTS        AGE
bad-image-pod   0/1     ImagePullBackOff   0               7m14s
completed-pod   0/1     Completed          0               7m14s
crash-pod       0/1     Error              6 (3m51s ago)   7m14s
onfailure-pod   0/1     Completed          1 (7m5s ago)    7m14s
```

> **หมายเหตุจากการทดลองจริง:** STATUS ของ `crash-pod` สลับไปมาระหว่าง `Running` → `Error` → `CrashLoopBackOff` และเห็น `Error` บ่อยที่สุด (สุ่มดูทุก 3 วินาทีตั้งแต่วินาทีที่ 20 ถึง 200: `Error` 47 ครั้ง, `CrashLoopBackOff` 7 ครั้ง, `Running` 4 ครั้ง) ดังนั้นที่ ~7 นาที นักศึกษาอาจเห็น `0/1 Error` (อย่างในรอบทดลองนี้) หรือ `0/1 CrashLoopBackOff` ก็ได้ ทั้งสองแบบถูกต้อง สิ่งที่ยืนยันว่าเป็น crash loop คือ **RESTARTS ที่เพิ่มขึ้นเรื่อย ๆ โดยช่วงห่างยาวขึ้น** (ที่ ~7 นาทีมี RESTARTS 6 แต่ restart ครั้งล่าสุดเมื่อ 3m51s ก่อน) ส่วน `bad-image-pod` ก็สลับ `ErrImagePull` ⇄ `ImagePullBackOff` เช่นกัน (ช่วงเวลาเดียวกัน: `ErrImagePull` 13 ครั้ง, `ImagePullBackOff` 45 ครั้ง) ตัวเลข AGE/RESTARTS และจำนวนครั้งที่นับได้จะต่างกันตามจังหวะที่สั่งคำสั่ง

### ขั้นที่ 2: สืบสวน crash-pod

```bash
kubectl describe pod crash-pod
kubectl logs crash-pod --previous
kubectl get pod crash-pod -o jsonpath="{.status.containerStatuses[0].state.waiting}{\"\\n\"}"
kubectl get pod crash-pod -o jsonpath="phase={.status.phase}{\"\\n\"}"
```

ผลจริงที่ประมาณ 3 นาที 20 วินาทีหลังสร้าง (ตัดเฉพาะส่วนสำคัญ)

```text
Containers:
  app:
    Image:         busybox:1.36
    Command:
      sh
      -c
      echo 'กำลังเปิดร้าน...'; sleep 3; echo 'ERROR: หาไฟล์เมนูไม่เจอ' >&2; exit 1
    State:          Running
      Started:      Mon, 05 Oct 2026 17:07:15 +0700
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
      Started:      Mon, 05 Oct 2026 17:05:45 +0700
      Finished:     Mon, 05 Oct 2026 17:05:48 +0700
    Ready:          True
    Restart Count:  5
...
Events:
  Type     Reason     Age                  From               Message
  ----     ------     ----                 ----               -------
  Normal   Scheduled  3m21s                default-scheduler  Successfully assigned default/crash-pod to lab-worker
  Warning  BackOff    24s (x5 over 3m13s)  kubelet            spec.containers{app}: Back-off restarting failed container app in pod crash-pod_default(9390c699-fd0e-4e5a-a275-345e190554b4)
  Normal   Pulled     1s (x6 over 3m20s)   kubelet            spec.containers{app}: Container image "busybox:1.36" already present on machine and can be accessed by the pod
  Normal   Created    1s (x6 over 3m20s)   kubelet            spec.containers{app}: Container created
  Normal   Started    1s (x6 over 3m20s)   kubelet            spec.containers{app}: Container started

$ kubectl logs crash-pod --previous
กำลังเปิดร้าน...
ERROR: หาไฟล์เมนูไม่เจอ

$ kubectl get pod crash-pod -o jsonpath="{.status.containerStatuses[0].state.waiting}{\"\\n\"}"
{"message":"back-off 2m40s restarting failed container=app pod=crash-pod_default(9390c699-fd0e-4e5a-a275-345e190554b4)","reason":"CrashLoopBackOff"}

$ kubectl get pod crash-pod -o jsonpath="phase={.status.phase}{\"\\n\"}"
phase=Running
```

ในจังหวะที่ `describe` นี้ container เพิ่งถูกเริ่มรอบใหม่ (`State: Running`, `Started` 17:07:15) จึงเห็น `Ready: True` ส่วน `Last State` คือรอบที่ล้มก่อนหน้า (`Error`, `Exit Code: 1`) ถ้าสั่งในจังหวะอื่นอาจเห็น `State: Waiting` (`CrashLoopBackOff`) หรือ `Terminated` (`Error`) แทน ค่า UID ในวงเล็บ `crash-pod_default(...)` และเวลาจะต่างในแต่ละเครื่อง

(คำสั่ง `jsonpath` ของ `state.waiting` จะได้ผลเฉพาะตอนที่ container กำลังรอ back-off ถ้าได้ผลว่างให้ลองใหม่อีกครั้ง — ในรอบทดลองต้องสั่งซ้ำทุก 2 วินาทีถึง 33 ครั้งกว่าจะได้ผล เพราะช่วงส่วนใหญ่ container อยู่ในสถานะ `Running` หรือ `Terminated`)

ถ้า `kubectl logs crash-pod --previous` ได้ `unable to retrieve container logs for containerd://...` แปลว่าสั่งตอน container เพิ่งจบ (`State: Terminated`) ให้รอแล้วสั่งใหม่ตอน STATUS เป็น `CrashLoopBackOff` หรือ `Running` (หรือใช้ `kubectl logs crash-pod` ไม่ใส่ `--previous` ซึ่งจะเห็น log ของรอบที่เพิ่งล้ม)

> **ตัวเลข back-off อ่านอย่างไร:** kubelet รอก่อน restart เป็นเท่าตัวทุกครั้งที่ล้มซ้ำ คือ `10s` → `20s` → `40s` → `1m20s` → `2m40s` → แล้ว **ตันที่ `5m0s`** (เพดานสูงสุด) ในรอบทดลองนี้สั่งที่ประมาณ 3.5 นาทีหลังสร้าง Pod จึงเห็น `back-off 2m40s` ถ้ารอให้ล้มซ้ำอีกรอบ ค่าถัดไปคือ 2m40s × 2 = 5m20s ซึ่งเกินเพดาน จึงเห็น `back-off 5m0s` และคงที่ไปเรื่อย ๆ ตัวเลขที่นักศึกษาเห็นจึงขึ้นกับว่าสั่งตอนไหน

### ขั้นที่ 3: ตรวจ completed-pod และ onfailure-pod

```bash
kubectl get pod completed-pod -o jsonpath="phase={.status.phase} exitCode={.status.containerStatuses[0].state.terminated.exitCode} reason={.status.containerStatuses[0].state.terminated.reason}{\"\\n\"}"; kubectl logs completed-pod
kubectl get pod onfailure-pod -o jsonpath="phase={.status.phase} restarts={.status.containerStatuses[0].restartCount}{\"\\n\"}"; kubectl logs onfailure-pod
```

```text
phase=Succeeded exitCode=0 reason=Completed
น้องส้มนับสต็อกเสร็จแล้ว
phase=Succeeded restarts=1
รอบสองสำเร็จ
```

### ขั้นที่ 4: สืบสวนและแก้ bad-image-pod

```bash
kubectl describe pod bad-image-pod | sed -n "/^Events:/,\$p"
```

```text
Events:
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  7m14s                 default-scheduler  Successfully assigned default/bad-image-pod to lab-worker2
  Normal   Pulling    4m2s (x5 over 7m13s)  kubelet            spec.containers{web}: Pulling image "nginx:9.99-doesnotexist"
  Warning  Failed     4m1s (x5 over 7m7s)   kubelet            spec.containers{web}: Failed to pull image "nginx:9.99-doesnotexist": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:9.99-doesnotexist": failed to resolve reference "docker.io/library/nginx:9.99-doesnotexist": docker.io/library/nginx:9.99-doesnotexist: not found
  Warning  Failed     4m1s (x5 over 7m7s)   kubelet            spec.containers{web}: Error: ErrImagePull
  Warning  Failed     118s (x20 over 7m7s)  kubelet            spec.containers{web}: Error: ImagePullBackOff
  Normal   BackOff    104s (x21 over 7m7s)  kubelet            spec.containers{web}: Back-off pulling image "nginx:9.99-doesnotexist"
```

สาเหตุคือ tag `9.99-doesnotexist` ไม่มีอยู่จริง (`not found`) แก้โดยสร้างไฟล์ที่แก้ tag แล้ว จากนั้น **ลบ Pod แล้ว apply ใหม่**

```bash
sed "s/nginx:9.99-doesnotexist/nginx:1.27-alpine/" labs/lab05-lifecycle/bad-image-pod.yaml > /tmp/bad-image-fixed.yaml && grep image: /tmp/bad-image-fixed.yaml
kubectl delete pod bad-image-pod && kubectl apply -f /tmp/bad-image-fixed.yaml && kubectl wait --for=condition=Ready pod/bad-image-pod --timeout=60s && kubectl get pod bad-image-pod
```

```text
      image: nginx:1.27-alpine   # tag ผิด! แก้เป็น nginx:1.27-alpine แล้วลบ/apply ใหม่
pod "bad-image-pod" deleted from default namespace
pod/bad-image-pod created
pod/bad-image-pod condition met
NAME            READY   STATUS    RESTARTS   AGE
bad-image-pod   1/1     Running   0          1s
```

> **รู้ไว้:** `image` เป็น field ที่แก้ได้บน Pod ที่รันอยู่ ในการทดลองจริง ถ้า `kubectl apply -f /tmp/bad-image-fixed.yaml` โดยไม่ลบก่อนจะได้ `pod/bad-image-pod configured` แล้ว Pod เป็น `Running` เช่นกัน แต่การ "ลบแล้วสร้างใหม่" เป็นแนวทางที่ใช้ได้กับทุก field

### ขั้นที่ 5: ลบทั้งหมด

```bash
kubectl delete -f labs/lab05-lifecycle/ --ignore-not-found; kubectl get pods
```

```text
pod "bad-image-pod" deleted from default namespace
pod "completed-pod" deleted from default namespace
pod "crash-pod" deleted from default namespace
pod "onfailure-pod" deleted from default namespace
No resources found in default namespace.
```

### สิ่งที่เห็น

- STATUS ในตารางไม่ใช่ phase: `crash-pod` แสดง `Error`/`CrashLoopBackOff` แต่ phase คือ `Running`; `completed-pod` แสดง `Completed` แต่ phase คือ `Succeeded`
- kubelet restart container **ใน Pod เดิม** โดยรอนานขึ้นเป็นเท่าตัว (`10s` → `20s` → `40s` → `1m20s` → `2m40s`) จนถึงเพดาน `back-off 5m0s`
- `logs --previous` คือกุญแจสำคัญในการดู log ของรอบที่ล้ม
- `OnFailure` restart เฉพาะตอนล้ม เมื่อสำเร็จแล้วจบที่ `Completed`
- ปัญหา image ดูที่ Events ข้อความ `not found` บอกว่าชื่อหรือ tag ผิด

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `crash-pod` เป็น `restartPolicy: Never` คาดว่า STATUS, RESTARTS และ phase จะเป็นอย่างไร (ลองทำแล้วตรวจคำตอบ อย่าลืมลบ Pod)

---

## LAB 6: env, command และ resources

<p align="center" id="fig-8">
  <img src="images/07-lab6-env-command-resources.png" alt="รูปที่ 8 LAB6 env/command/resources" width="900"><br>
  <em><b>รูปที่ 8</b> LAB6: ส่ง env และ command เข้า container ทดลอง memory limit จนเกิด OOMKilled และ request CPU เกินจน Pending</em>
</p>

**เป้าหมาย:** ส่งค่าเข้า container ด้วย `env`, ทับคำสั่งด้วย `command`/`args`, เห็นผลของ memory limit (OOMKilled) และ CPU request ที่เกิน (Pending)

ไฟล์ใน `labs/lab06-env-resources/`: `env-command-pod.yaml` (env + command/args + requests/limits), `oom-pod.yaml` (limit memory 32Mi แล้วรัน `tail /dev/zero` ซึ่งกิน RAM ไม่หยุด), `pending-pod.yaml` (ขอ `cpu: "64"`)

#### อธิบาย YAML: `labs/lab06-env-resources/env-command-pod.yaml`

```yaml
    - name: app
      image: busybox:1.36
      env:                              # ตัวแปรสภาพแวดล้อม (value ต้องเป็น string)
        - name: SHOP_NAME
          value: "ร้านอาหารแมวน้องส้ม"       # ภาษาไทยใช้ได้
        - name: OPEN_HOUR
          value: "9"                    # ตัวเลขต้องใส่ "" ให้เป็น string
      command: ["sh", "-c"]             # ทับ ENTRYPOINT ของ image
      args:                             # ทับ CMD ของ image
        - echo "SHOP_NAME=$SHOP_NAME"; echo "OPEN_HOUR=$OPEN_HOUR"; sleep 3600
      resources:
        requests:                       # ใช้ตอน scheduler เลือก Node
          cpu: "50m"                    # 50 milliCPU = 0.05 core
          memory: "32Mi"
        limits:                         # เพดานสูงสุดขณะรัน
          cpu: "100m"                   # เกินแล้วถูกหน่วง (throttle) ไม่ถูกฆ่า
          memory: "64Mi"                # เกินแล้วถูกฆ่า (OOMKilled)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `env[].name/value` | ส่งค่าเข้า container เป็นตัวแปรสภาพแวดล้อม `value` ต้องเป็น **string** เสมอ จึงใส่ `"9"` | `logs` เห็น `SHOP_NAME=ร้านอาหารแมวน้องส้ม`, `OPEN_HOUR=9`; ขั้นที่ 4 ถอด quote แล้วได้ `BadRequest ... cannot unmarshal number ... of type string` |
| (ไม่ได้เขียน) `HOSTNAME` | Kubernetes ตั้งให้ทุก container อัตโนมัติ = ชื่อ Pod | `env` เห็น `HOSTNAME=env-command-pod` (จุดนี้สำคัญใน LAB 9) |
| `command: ["sh", "-c"]` | ทับ ENTRYPOINT ของ image ให้รันผ่าน shell | jsonpath ได้ `["sh","-c"]` |
| `args: [ "echo ...; sleep 3600" ]` | ทับ CMD ของ image เป็นสคริปต์ 1 บรรทัด ซึ่ง `sh -c` รับไปรัน (`$SHOP_NAME` ถูกแทนค่าโดย shell) และ `sleep 3600` ทำให้ container ไม่จบ | jsonpath ได้ args 1 ตัว, Pod `1/1 Running` |
| `resources.requests` 50m / 32Mi | ปริมาณที่ "จอง" ไว้ scheduler ใช้ตัดสินว่า Node ไหนรับได้ | `describe` เห็น `Requests: cpu 50m, memory 32Mi` |
| `resources.limits` 100m / 64Mi | เพดานขณะรัน CPU เกินจะถูกหน่วง memory เกินจะถูกฆ่า | `Limits: cpu 100m, memory 64Mi`; requests < limits จึงได้ QoS `Burstable` |

#### อธิบาย YAML: `oom-pod.yaml` และ `pending-pod.yaml`

```yaml
# oom-pod.yaml
spec:                                   # ไม่ระบุ restartPolicy = Always จึงถูก restart วน
  containers:
    - name: hungry
      image: busybox:1.36
      command: ["sh", "-c", "echo 'กินแรมไม่หยุด...'; tail /dev/zero"]   # tail จะอ่านข้อมูลเก็บในแรมไปเรื่อย ๆ
      resources:
        requests:
          memory: "16Mi"                # ขั้นต่ำที่ขอจอง (ใช้ตอนเลือก Node)
        limits:
          memory: "32Mi"                # เกิน 32Mi เมื่อไร โดน OOMKilled
```

```yaml
# pending-pod.yaml
    - name: big
      image: nginx:1.27-alpine
      resources:
        requests:                       # scheduler ต้องหา Node ที่มี CPU ว่างพอตามนี้
          cpu: "64"                     # ขอ 64 core! ไม่มี Node ไหนรับไหว
```

| ไฟล์ / field | ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| oom: `command: ... tail /dev/zero` | `/dev/zero` ไม่มีขึ้นบรรทัดใหม่ `tail` จึงเก็บข้อมูลไว้ในหน่วยความจำไปเรื่อย ๆ | ใช้ memory พุ่งจนชนเพดานภายในไม่ถึงวินาที (`Started` กับ `Finished` เป็นวินาทีเดียวกัน) |
| oom: `limits.memory: "32Mi"` | เพดานต่ำ ทำให้ kernel ฆ่าโปรเซสด้วย SIGKILL เร็ว | `Reason: OOMKilled`, `Exit Code: 137` (= 128 + 9) |
| oom: ไม่มี `restartPolicy` | ค่าเริ่มต้น `Always` | RESTARTS เพิ่มขึ้นเรื่อย ๆ (เห็น `2 (15s ago)` ที่ 16 วินาที) |
| pending: `requests.cpu: "64"` | ขอ CPU มากกว่าที่ node มี (`Allocatable cpu: 32` ในเครื่องทดสอบ) และ control-plane มี taint | `Pending`, IP/NODE เป็น `<none>`, Events `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu` |
| pending: ไม่มี `limits` | ทดสอบเฉพาะการตัดสินใจของ scheduler ซึ่งดูแค่ `requests` | Pod ไม่เคยถูกวางบน node จึงไม่เคยรัน container เลย |

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: env และ command/args

```bash
cat labs/lab06-env-resources/env-command-pod.yaml
kubectl apply -f labs/lab06-env-resources/env-command-pod.yaml && kubectl wait --for=condition=Ready pod/env-command-pod --timeout=60s
kubectl logs env-command-pod
kubectl exec env-command-pod -- env | grep -E "SHOP_NAME|OPEN_HOUR|HOSTNAME"
kubectl get pod env-command-pod -o jsonpath="{.spec.containers[0].command} {.spec.containers[0].args}{\"\\n\"}"
```

```text
pod/env-command-pod created
pod/env-command-pod condition met

$ kubectl logs env-command-pod
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9

$ kubectl exec env-command-pod -- env | grep -E "SHOP_NAME|OPEN_HOUR|HOSTNAME"
HOSTNAME=env-command-pod
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9

$ kubectl get pod env-command-pod -o jsonpath="{.spec.containers[0].command} {.spec.containers[0].args}{\"\\n\"}"
["sh","-c"] ["echo \"SHOP_NAME=$SHOP_NAME\"; echo \"OPEN_HOUR=$OPEN_HOUR\"; sleep 3600"]
```

### ขั้นที่ 2: resources และ QoS

```bash
kubectl describe pod env-command-pod | grep -A6 -E "^    (Limits|Requests):" | head -8
kubectl get pod env-command-pod -o jsonpath="{.status.qosClass}{\"\\n\"}"
```

```text
    Limits:
      cpu:     100m
      memory:  64Mi
    Requests:
      cpu:     50m
      memory:  32Mi
    Environment:
      SHOP_NAME:  ร้านอาหารแมวน้องส้ม
Burstable
```

### ขั้นที่ 3: ทดลอง OOMKilled และ Pending

```bash
kubectl apply -f labs/lab06-env-resources/oom-pod.yaml -f labs/lab06-env-resources/pending-pod.yaml
kubectl get pods
kubectl describe pod oom-pod | sed -n "/^    State:/,/^    Restart Count/p"
kubectl describe pod pending-pod | sed -n "/^Events:/,\$p"
kubectl get pod pending-pod -o wide
```

```text
pod/oom-pod created
pod/pending-pod created

$ kubectl get pods
NAME              READY   STATUS      RESTARTS      AGE
env-command-pod   1/1     Running     0             18s
oom-pod           0/1     OOMKilled   2 (15s ago)   16s
pending-pod       0/1     Pending     0             16s

$ kubectl describe pod oom-pod | sed -n "/^    State:/,/^    Restart Count/p"
    State:          Terminated
      Reason:       OOMKilled
      Exit Code:    137
      Started:      Mon, 05 Oct 2026 17:11:46 +0700
      Finished:     Mon, 05 Oct 2026 17:11:46 +0700
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
      Started:      Mon, 05 Oct 2026 17:11:33 +0700
      Finished:     Mon, 05 Oct 2026 17:11:33 +0700
    Ready:          False
    Restart Count:  2

$ kubectl describe pod pending-pod | sed -n "/^Events:/,\$p"
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  30s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.

$ kubectl get pod pending-pod -o wide
NAME          READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
pending-pod   0/1     Pending   0          30s   <none>   <none>   <none>           <none>
```

(ค่า RESTARTS ของ `oom-pod` ขึ้นกับจังหวะที่สั่ง เช่น 1 หรือ 2 และเพิ่มต่อไปเรื่อย ๆ เพราะ restart วน; เวลา `Started`/`Finished` จะต่างในแต่ละเครื่อง)

ดูว่า node มี CPU เท่าไร

```bash
kubectl describe node lab-worker | sed -n "/^Allocatable:/,/^System Info/p" | head -8
```

```text
Allocatable:
  cpu:                32
  ephemeral-storage:  1081101176832
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             64489564Ki
  pods:               110
System Info:
```

> node ของ kind มองเห็น CPU/RAM เท่ากับเครื่องจริง เครื่องทดสอบมี 32 core ของนักศึกษาจะน้อยกว่านี้ ซึ่งยิ่งทำให้ `cpu: "64"` เกินแน่นอน (ยกเว้นเครื่องที่มีมากกว่า 64 thread ซึ่งแทบไม่มี)

### ขั้นที่ 4: ทดลองลืม quote ใน env

```bash
sed 's/value: "9"/value: 9/' labs/lab06-env-resources/env-command-pod.yaml | sed 's/name: env-command-pod/name: env-number-test/' | kubectl apply -f -
```

```text
Error from server (BadRequest): error when creating "STDIN": Pod in version "v1" cannot be handled as a Pod: json: cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string
```

### ขั้นที่ 5: ลบทั้งหมด

```bash
kubectl delete -f labs/lab06-env-resources/; kubectl get pods
```

```text
pod "env-command-pod" deleted from default namespace
pod "oom-pod" deleted from default namespace
pod "pending-pod" deleted from default namespace
No resources found in default namespace.
```

### สิ่งที่เห็น

- `env` ส่งข้อความภาษาไทยได้ และ `HOSTNAME` ของ container มีค่าเป็นชื่อ Pod
- `command`/`args` ทับคำสั่งเริ่มต้นของ image busybox
- memory เกิน limit → `OOMKilled` exit code `137` (= 128 + สัญญาณ 9 SIGKILL) แล้วถูก restart วน
- CPU request เกินที่ Node ไหนจะมี → `Pending` ไม่มี IP ไม่มี NODE เพราะยังไม่ผ่านขั้น scheduler เลย ข้อความ `1 node(s) had untolerated taint(s)` คือ `lab-control-plane`
- `env.value` ที่เป็นตัวเลขต้องใส่ quote ไม่เช่นนั้น kube-apiserver ปฏิเสธ

> **🏆 ท้าทาย:** แก้ `oom-pod` ให้ limit เป็น `requests` = `limits` ทั้ง CPU และ memory (เช่น `cpu: 100m`, `memory: 64Mi`) และเปลี่ยนคำสั่งเป็น `sleep 3600` แล้วตรวจว่า QoS class เป็นอะไร

---

## LAB 7: Probes ตรวจสุขภาพ

<p align="center" id="fig-9">
  <img src="images/08-lab7-probes.png" alt="รูปที่ 9 LAB7 probes" width="900"><br>
  <em><b>รูปที่ 9</b> LAB7: liveness ล้มแล้ว container ถูก restart ส่วน readiness ล้มแล้ว Pod เป็น READY 0/1 โดยไม่ถูก restart</em>
</p>

**เป้าหมาย:** เห็นความต่างของ liveness กับ readiness ด้วยตาตัวเอง

| ไฟล์ | probe | กลไก |
|---|---|---|
| `labs/lab07-probes/liveness-exec-pod.yaml` | `livenessProbe` exec `cat /tmp/healthy` ทุก 5 วินาที, failureThreshold 3 | container สร้าง `/tmp/healthy` แล้วลบทิ้งหลัง 30 วินาที (จำลองแอปค้าง) |
| `labs/lab07-probes/readiness-http-pod.yaml` | `readinessProbe` httpGet `/ready.html` port 80 ทุก 3 วินาที | ยังไม่มีไฟล์ → 404 → ไม่พร้อม |

#### อธิบาย YAML: `liveness-exec-pod.yaml` และ `readiness-http-pod.yaml`

```yaml
# liveness-exec-pod.yaml
    - name: app
      image: busybox:1.36
      # สร้างไฟล์ healthy → ผ่านไป 30 วินาทีลบทิ้ง (จำลองแอปค้าง)
      command: ["sh", "-c", "touch /tmp/healthy; echo 'สบายดี'; sleep 30; rm -f /tmp/healthy; echo 'ไม่สบายแล้ว'; sleep 600"]
      livenessProbe:                         # ไม่ผ่าน → kubelet ฆ่าแล้ว restart container
        exec:
          command: ["cat", "/tmp/healthy"]   # exit 0 = ผ่าน, ไม่ใช่ 0 = ไม่ผ่าน
        initialDelaySeconds: 5               # รอ 5 วินาทีก่อนตรวจครั้งแรก
        periodSeconds: 5                     # ตรวจทุก 5 วินาที
        failureThreshold: 3                  # ไม่ผ่าน 3 ครั้งติด → restart
```

```yaml
# readiness-http-pod.yaml
    - name: web
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
      readinessProbe:            # ไม่ผ่าน → READY 0/1 เท่านั้น ไม่ restart
        httpGet:                 # ตอบ 200–399 = ผ่าน, อย่างอื่น (เช่น 404) = ไม่ผ่าน
          path: /ready.html      # ยังไม่มีไฟล์นี้ → 404 → ยังไม่พร้อม
          port: 80
        periodSeconds: 3         # ตรวจทุก 3 วินาที
        failureThreshold: 1      # ล้มครั้งเดียวก็ถือว่าไม่พร้อมทันที
```

| field | ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| liveness: `command` ที่ `sleep 30` แล้ว `rm -f /tmp/healthy` | จำลองแอปที่ทำงานปกติ 30 วินาทีแล้ว "ค้าง" (ยังรันอยู่แต่ไม่สบาย) ข้อความ echo ช่วยให้เห็นใน log | `logs --previous` ได้ `สบายดี` / `ไม่สบายแล้ว` |
| liveness: `exec: cat /tmp/healthy` | probe แบบรันคำสั่งใน container ผ่านเมื่อ exit 0 | ข้อความ `Liveness probe failed: cat: can't open '/tmp/healthy'` |
| liveness: `initialDelaySeconds: 5`, `periodSeconds: 5`, `failureThreshold: 3` | ตรวจทุก 5 วินาที ล้ม 3 ครั้งติด (~15 วินาที) จึงสั่ง restart | `Unhealthy (x3 over 25s)` แล้ว `Killing`; `describe` แสดง `delay=5s timeout=1s period=5s successThreshold=1 failureThreshold=3` (`timeout`/`successThreshold` เป็นค่าเริ่มต้น) |
| readiness: `httpGet path: /ready.html, port: 80` | ตรวจด้วย HTTP GET ไฟล์ที่ตั้งใจไม่ให้มี เพื่อควบคุมได้ด้วยการสร้าง/ลบไฟล์ | ครั้งแรก `connection refused` (nginx ยังไม่เริ่ม) แล้ว `statuscode: 404` |
| readiness: `periodSeconds: 3`, `failureThreshold: 1` | ตรวจถี่และล้มครั้งเดียวก็ไม่พร้อม เพื่อให้เห็นผลภายในไม่กี่วินาที | สร้าง `ready.html` → `1/1`, ลบ → `0/1` ภายใน 3–5 วินาที; `describe` แสดง `delay=0s ... period=3s ... failureThreshold=1` |
| readiness: ไม่มี `livenessProbe` | readiness ไม่เคยทำให้ restart | RESTARTS คงที่ `0` ตลอด |

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: สร้างทั้งสอง Pod

```bash
kubectl apply -f labs/lab07-probes/liveness-exec-pod.yaml -f labs/lab07-probes/readiness-http-pod.yaml
kubectl get pods
kubectl describe pod readiness-http-pod | sed -n "/^Events:/,\$p"
```

```text
pod/liveness-exec-pod created
pod/readiness-http-pod created

# ~10s
NAME                 READY   STATUS    RESTARTS   AGE
liveness-exec-pod    1/1     Running   0          11s
readiness-http-pod   0/1     Running   0          11s

Events:
  Type     Reason     Age   From               Message
  ----     ------     ----  ----               -------
  Normal   Scheduled  10s   default-scheduler  Successfully assigned default/readiness-http-pod to lab-worker
  Normal   Pulling    10s   kubelet            spec.containers{web}: Pulling image "nginx:1.27-alpine"
  Normal   Pulled     4s    kubelet            spec.containers{web}: Successfully pulled image "nginx:1.27-alpine" in 6.105s (6.105s including waiting). Image size: 20984244 bytes.
  Normal   Created    4s    kubelet            spec.containers{web}: Container created
  Normal   Started    4s    kubelet            spec.containers{web}: Container started
  Warning  Unhealthy  4s    kubelet            spec.containers{web}: Readiness probe failed: Get "http://10.244.1.5:80/ready.html": dial tcp 10.244.1.5:80: connect: connection refused
  Warning  Unhealthy  3s    kubelet            spec.containers{web}: Readiness probe failed: HTTP probe failed with statuscode: 404
```

(IP ของ Pod, node และจำนวนครั้ง `(xN over ...)` จะต่างตามจังหวะที่สั่ง ถ้า node มี image `nginx:1.27-alpine` อยู่แล้วจะเห็น `already present on machine` แทน `Pulling`/`Pulled`)

ครั้งแรก `connection refused` เพราะ nginx ยังเริ่มไม่เสร็จ หลังจากนั้นเป็น `404` เพราะยังไม่มีไฟล์ `/ready.html`

### ขั้นที่ 2: ทำให้ readiness ผ่าน แล้วไม่ผ่านอีกครั้ง

```bash
kubectl exec readiness-http-pod -- sh -c "echo ready > /usr/share/nginx/html/ready.html"
kubectl get pod readiness-http-pod
kubectl exec readiness-http-pod -- rm /usr/share/nginx/html/ready.html
kubectl get pod readiness-http-pod
```

(รอ 3–5 วินาทีก่อน `get` แต่ละครั้ง เพราะ probe ตรวจทุก 3 วินาที)

```text
NAME                 READY   STATUS    RESTARTS   AGE
readiness-http-pod   1/1     Running   0          15s

NAME                 READY   STATUS    RESTARTS   AGE
readiness-http-pod   0/1     Running   0          19s
```

### ขั้นที่ 3: รอ liveness ล้ม (อย่างน้อย 90 วินาที)

```bash
kubectl describe pod liveness-exec-pod | sed -n "/^Events:/,\$p"
kubectl get pods
kubectl logs liveness-exec-pod --previous
```

ผลจริงที่ประมาณ 60 วินาที (Events) และ 95 วินาที (`get pods`)

```text
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  61s                default-scheduler  Successfully assigned default/liveness-exec-pod to lab-worker2
  Normal   Pulled     60s                kubelet            spec.containers{app}: Container image "busybox:1.36" already present on machine and can be accessed by the pod
  Normal   Created    60s                kubelet            spec.containers{app}: Container created
  Normal   Started    60s                kubelet            spec.containers{app}: Container started
  Warning  Unhealthy  15s (x3 over 25s)  kubelet            spec.containers{app}: Liveness probe failed: cat: can't open '/tmp/healthy': No such file or directory
  Normal   Killing    15s                kubelet            spec.containers{app}: Container app failed liveness probe, will be restarted

# ~95s
NAME                 READY   STATUS    RESTARTS      AGE
liveness-exec-pod    1/1     Running   1 (21s ago)   97s
readiness-http-pod   0/1     Running   0             97s

$ kubectl logs liveness-exec-pod --previous
สบายดี
ไม่สบายแล้ว
```

> **ทำไมต้องรอนาน:** probe เริ่มล้มหลังวินาทีที่ ~30 ต้องล้ม 3 ครั้ง (ทุก 5 วินาที) จึงสั่ง `Killing` ที่ราววินาทีที่ 45 (Events ที่ 60 วินาทีแสดง `Killing 15s` ก่อนหน้า) แต่ `sh` ของ busybox ไม่ตอบสัญญาณ SIGTERM kubelet จึงต้องรอ grace period 30 วินาทีก่อนบังคับปิด ทำให้ RESTARTS เปลี่ยนเป็น 1 ที่ราววินาทีที่ 75 (รอบทดลองจริง: ยังเป็น 0 ที่วินาทีที่ 71 และเป็น `1 (1s ago)` ที่วินาทีที่ 76)

### ขั้นที่ 4: เปรียบเทียบการตั้งค่า probe แล้วลบ

```bash
kubectl describe pod liveness-exec-pod | grep -E "Restart Count|Liveness:"; kubectl describe pod readiness-http-pod | grep -E "Restart Count|Readiness:"
kubectl delete -f labs/lab07-probes/ --now; kubectl get pods
```

```text
    Restart Count:  1
    Liveness:       exec [cat /tmp/healthy] delay=5s timeout=1s period=5s successThreshold=1 failureThreshold=3
    Restart Count:  0
    Readiness:      http-get http://:80/ready.html delay=0s timeout=1s period=3s successThreshold=1 failureThreshold=1
pod "liveness-exec-pod" deleted from default namespace
pod "readiness-http-pod" deleted from default namespace
No resources found in default namespace.
```

### สิ่งที่เห็น

- **readiness ล้ม** → READY `0/1` แต่ RESTARTS = 0 container ยังทำงานอยู่ และกลับมา `1/1` ได้เองเมื่อ probe ผ่าน
- **liveness ล้ม** → Events `Killing` แล้ว RESTARTS เพิ่ม log รอบก่อนหน้าดูด้วย `--previous`
- `--now` ช่วยให้ลบ Pod ที่ใช้ busybox ได้เร็ว ไม่ต้องรอ 30 วินาที (รอบทดลอง `time kubectl delete -f labs/lab07-probes/ --now` ใช้ราว 2.5 วินาที)
- ผลของ READY `0/1` ต่อการรับทราฟฟิกจริงจะเห็นชัดในบทถัดไป

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน readinessProbe ของ `readiness-http-pod` เป็น livenessProbe (ค่าเดิม) จะเกิดอะไรกับ RESTARTS เมื่อไม่มีไฟล์ `/ready.html`

---

## LAB 8: Multi-container: localhost, emptyDir, init, sidecar

<p align="center" id="fig-10">
  <img src="images/09-lab8-multi-container.png" alt="รูปที่ 10 LAB8 multi-container" width="900"><br>
  <em><b>รูปที่ 10</b> LAB8: Pod หลาย container คุยกันผ่าน localhost ใช้ emptyDir ร่วมกัน มี init container เตรียมไฟล์ และ sidecar เขียนข้อมูลต่อเนื่อง</em>
</p>

**เป้าหมาย:** พิสูจน์ว่า container ใน Pod เดียวกันใช้ IP เดียวกัน, ใช้ emptyDir ร่วมกัน, เห็นลำดับ init container และพฤติกรรมของข้อมูลเมื่อ container restart เทียบกับเมื่อลบ Pod

🐧 **ใน SSH session ของ k8s-lab**

### ส่วน A: shared-localhost-pod (nginx + busybox)

#### อธิบาย YAML: `labs/lab08-multi-container/shared-localhost-pod.yaml`

```yaml
spec:
  containers:                   # มี 2 ตัว → READY 2/2, ตัวแรก (web) คือ container เริ่มต้นของ kubectl
    - name: web                 # container หลัก: nginx ฟัง port 80
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
    - name: helper              # container ผู้ช่วย: ไม่มีเว็บของตัวเอง
      image: busybox:1.36
      command: ["sh", "-c", "sleep 3600"]   # แค่นอนรอ ไว้ให้เรา exec เข้าไปทดสอบ
```

| field | ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `containers` มี 2 รายการ | container ทุกตัวใน Pod เดียวกันใช้ network namespace (IP, port, `localhost`) ร่วมกัน | READY `2/2`, `hostname -i` ของทั้งสองได้ IP เดียวกัน |
| `web` อยู่ลำดับแรก | kubectl ใช้ container แรกเมื่อไม่ระบุ `-c` | `Defaulted container "web" out of: web, helper` |
| `web` → `containerPort: 80` | nginx ฟัง port 80 (ข้อมูลประกอบ) | `netstat` ใน `helper` เห็น `0.0.0.0:80` และ `:::80` |
| `helper` → `command: sleep 3600` | busybox ไม่มีโปรแกรมทำงานค้าง ต้องให้ `sleep` ไว้ ไม่เช่นนั้นจะจบทันทีแล้วถูก restart วน | `helper` ใช้ `wget -qO- localhost:80` ได้ `<title>Welcome to nginx!</title>` |

```bash
kubectl apply -f labs/lab08-multi-container/shared-localhost-pod.yaml && kubectl wait --for=condition=Ready pod/shared-localhost-pod --timeout=60s && kubectl get pod shared-localhost-pod -o wide
kubectl exec shared-localhost-pod -c helper -- wget -qO- localhost:80 | grep -o "<title>.*</title>"
kubectl exec shared-localhost-pod -c helper -- hostname -i; kubectl exec shared-localhost-pod -c web -- hostname -i
kubectl exec shared-localhost-pod -c helper -- netstat -tln
kubectl exec shared-localhost-pod -- hostname
```

```text
pod/shared-localhost-pod created
pod/shared-localhost-pod condition met
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
shared-localhost-pod   2/2     Running   0          0s    10.244.3.18   lab-worker2   <none>           <none>

$ kubectl exec shared-localhost-pod -c helper -- wget -qO- localhost:80 | grep -o "<title>.*</title>"
<title>Welcome to nginx!</title>

$ kubectl exec shared-localhost-pod -c helper -- hostname -i; kubectl exec shared-localhost-pod -c web -- hostname -i
10.244.3.18
10.244.3.18

$ kubectl exec shared-localhost-pod -c helper -- netstat -tln
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      
tcp        0      0 :::80                   :::*                    LISTEN      

$ kubectl exec shared-localhost-pod -- hostname
Defaulted container "web" out of: web, helper
shared-localhost-pod
```

(IP และ NODE จะต่างในแต่ละเครื่อง แต่ IP ของสอง container ต้องเท่ากันเสมอ)

container `helper` (busybox) ไม่มีเว็บเซิร์ฟเวอร์ แต่ `netstat` ใน helper กลับเห็น port 80 ที่ nginx เปิดไว้ เพราะใช้ network namespace เดียวกัน ลบ Pod นี้ก่อนไปส่วนถัดไป

```bash
kubectl delete pod shared-localhost-pod --now
```

### ส่วน B: init-sidecar-pod (init + nginx + sidecar + emptyDir)

โครงสร้างของ `labs/lab08-multi-container/init-sidecar-pod.yaml`

```text
Pod init-sidecar-pod
├─ volumes:        html (emptyDir)
├─ initContainers: prepare      (busybox) รอ 5 วิ เขียน /html/index.html แล้วจบ
└─ containers:     web          (nginx)   เสิร์ฟ /usr/share/nginx/html  ← emptyDir html
                   menu-writer  (busybox) sidecar ต่อบรรทัด "อัปเดต <เวลา>" ทุก 5 วิ  ← emptyDir html
```

#### อธิบาย YAML: `labs/lab08-multi-container/init-sidecar-pod.yaml`

```yaml
spec:
  volumes:
    - name: html                # ชั้นวางของร่วมของทุก container ใน Pod
      emptyDir: {}              # เกิดพร้อม Pod หายพร้อม Pod
  initContainers:               # ทำงานก่อน container หลัก ต้องจบด้วย exit 0
    - name: prepare
      image: busybox:1.36
      command:                  # รอ 5 วิ แล้วเขียนหัวเมนู + เวลาสร้าง ลง /html/index.html
        - sh
        - -c
        - |
          echo "เตรียมหน้าร้าน..."
          sleep 5
          echo "<h1>เมนูวันนี้ของน้องส้ม</h1>" > /html/index.html
          echo "สร้างเมื่อ $(date)" >> /html/index.html
          echo "prepare เสร็จ"
      volumeMounts:
        - name: html
          mountPath: /html      # prepare เห็น emptyDir ที่ /html
  containers:
    - name: web                 # เสิร์ฟไฟล์จาก emptyDir
      image: nginx:1.27-alpine
      volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html   # volume เดียวกัน แต่ mount คนละ path ได้
    - name: menu-writer         # sidecar: เขียนเวลาลงไฟล์ทุก 5 วินาที
      image: busybox:1.36
      command: ["sh", "-c", "while true; do echo \"<p>อัปเดต $(date +%T)</p>\" >> /html/index.html; sleep 5; done"]
      volumeMounts:
        - name: html
          mountPath: /html
```

| field | ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `volumes: html` → `emptyDir: {}` | โฟลเดอร์ว่างที่สร้างตอน Pod ถูกวางบน node อายุเท่ากับ Pod ใช้แชร์ไฟล์ระหว่าง container | restart container `web` แล้วไฟล์ยังอยู่ แต่ลบ Pod แล้ว "สร้างเมื่อ" เป็นเวลาใหม่ |
| `initContainers: prepare` | รันจนจบ (exit 0) **ก่อน** container หลักทุกตัว เหมาะกับงานเตรียมการ | STATUS `Init:0/1` ช่วงแรก, `describe` เห็น `prepare` เป็น `Terminated / Completed / Exit Code: 0` |
| `prepare` → `command` แบบ block (`\|`) | สคริปต์หลายบรรทัด มี `sleep 5` เพื่อให้ทันเห็นสถานะ `Init:0/1` และใช้ `>` (เขียนทับ) สร้างไฟล์ใหม่ | `logs -c prepare` ได้ `เตรียมหน้าร้าน...` / `prepare เสร็จ`; บรรทัดแรกของหน้าเว็บคือหัวเมนู |
| `volumeMounts` ของ `prepare`/`menu-writer` ที่ `/html` แต่ของ `web` ที่ `/usr/share/nginx/html` | volume เดียวกันถูก mount คนละ path ได้ nginx เสิร์ฟจากโฟลเดอร์เริ่มต้นของมันโดยไม่ต้องแก้ config | `wget -qO- localhost` ใน `web` เห็นไฟล์ที่ `prepare` และ `menu-writer` เขียน |
| `menu-writer` → `while true ... >> ... sleep 5` | sidecar ทำงานคู่กับ `web` ตลอดอายุ Pod ต่อท้ายไฟล์ (`>>`) ทุก 5 วินาที | บรรทัด `<p>อัปเดต HH:MM:SS</p>` เพิ่มทุก 5 วินาที, `wc -l` เพิ่มขึ้นเรื่อย ๆ |
| ไม่ได้ตั้ง `restartPolicy` | ค่าเริ่มต้น `Always` → container ที่จบ (แม้ exit 0) จะถูกเริ่มใหม่ | หลัง `nginx -s stop` container `web` จบด้วย `Completed / Exit Code: 0` แล้วถูก restart (`Restart Count: 1`) |
| `menu-writer` ใช้ `sh` เป็นโปรเซสหลัก | `sh` ไม่ตอบ SIGTERM | `kubectl delete` ใช้เวลาราว 30 วินาที (`real 0m30.841s`) |

**ขั้นที่ 1: สร้างและดูลำดับ init**

```bash
kubectl apply -f labs/lab08-multi-container/init-sidecar-pod.yaml
kubectl get pod init-sidecar-pod
```

สั่ง `get` ซ้ำทุก 2–3 วินาที (ผลจริงสั่งทุก 2 วินาที)

```text
NAME               READY   STATUS     RESTARTS   AGE
init-sidecar-pod   0/2     Init:0/1   0          0s

NAME               READY   STATUS     RESTARTS   AGE
init-sidecar-pod   0/2     Init:0/1   0          2s

NAME               READY   STATUS     RESTARTS   AGE
init-sidecar-pod   0/2     Init:0/1   0          4s

NAME               READY   STATUS    RESTARTS   AGE
init-sidecar-pod   2/2     Running   0          6s
```

`Init:0/1` ค้างอยู่ราว 5 วินาทีเพราะ `prepare` มี `sleep 5`

**ขั้นที่ 2: ดูผลงานของ init และ sidecar**

```bash
kubectl logs init-sidecar-pod -c prepare
kubectl exec init-sidecar-pod -c web -- wget -qO- localhost
kubectl describe pod init-sidecar-pod | sed -n "/^Init Containers:/,/^Containers:/p" | grep -E "^  [a-z]|State|Reason|Exit Code"
```

```text
เตรียมหน้าร้าน...
prepare เสร็จ

<h1>เมนูวันนี้ของน้องส้ม</h1>
สร้างเมื่อ Mon Oct  5 10:14:29 UTC 2026
<p>อัปเดต 10:14:30</p>
<p>อัปเดต 10:14:35</p>
<p>อัปเดต 10:14:40</p>
<p>อัปเดต 10:14:45</p>
<p>อัปเดต 10:14:50</p>
<p>อัปเดต 10:14:55</p>
<p>อัปเดต 10:15:00</p>

  prepare:
    State:          Terminated
      Reason:       Completed
      Exit Code:    0
```

(เวลาใน busybox เป็น UTC ช้ากว่าเวลาไทย 7 ชั่วโมง จำนวนบรรทัด "อัปเดต" ขึ้นกับว่ารอนานเท่าไรก่อนสั่ง)

**ขั้นที่ 3: ทำให้ container web ตาย แล้วดูว่าไฟล์ยังอยู่ไหม**

```bash
kubectl exec init-sidecar-pod -c web -- nginx -s stop
kubectl get pod init-sidecar-pod
kubectl describe pod init-sidecar-pod | sed -n "/^Containers:/,/^Conditions:/p" | grep -E "^  [a-z]|Restart Count|Reason|Exit Code"
kubectl exec init-sidecar-pod -c web -- sh -c "head -3 /usr/share/nginx/html/index.html; wc -l /usr/share/nginx/html/index.html"
```

```text
2026/10/05 10:15:00 [notice] 72#72: signal process started

NAME               READY   STATUS    RESTARTS     AGE
init-sidecar-pod   2/2     Running   1 (5s ago)   41s

  web:
      Reason:       Completed
      Exit Code:    0
    Restart Count:  1
  menu-writer:
    Restart Count:  0

<h1>เมนูวันนี้ของน้องส้ม</h1>
สร้างเมื่อ Mon Oct  5 10:14:29 UTC 2026
<p>อัปเดต 10:14:30</p>
10 /usr/share/nginx/html/index.html
```

container `web` ถูก restart (RESTARTS 1) แต่ไฟล์เดิมใน emptyDir ยังอยู่ครบ (บรรทัด "สร้างเมื่อ" เป็นเวลาเดิม และจำนวนบรรทัดเพิ่มขึ้นเรื่อย ๆ เพราะ sidecar ยังเขียนต่อ) และ init container **ไม่ถูกรันซ้ำ** (ตรวจได้ด้วย `kubectl get pod init-sidecar-pod -o jsonpath="{.status.initContainerStatuses[0].name} restarts={.status.initContainerStatuses[0].restartCount}{\"\\n\"}"` ผลจริง `prepare restarts=0`) จำนวนบรรทัดจาก `wc -l` (รอบนี้ 10) ขึ้นกับเวลาที่ผ่านไป

**ขั้นที่ 4: ลบ Pod แล้วสร้างใหม่**

```bash
time kubectl delete -f labs/lab08-multi-container/init-sidecar-pod.yaml
kubectl apply -f labs/lab08-multi-container/init-sidecar-pod.yaml && kubectl wait --for=condition=Ready pod/init-sidecar-pod --timeout=90s && kubectl exec init-sidecar-pod -c web -- head -3 /usr/share/nginx/html/index.html
```

```text
pod "init-sidecar-pod" deleted from default namespace

real	0m30.841s
...
pod/init-sidecar-pod created
pod/init-sidecar-pod condition met
<h1>เมนูวันนี้ของน้องส้ม</h1>
สร้างเมื่อ Mon Oct  5 10:15:42 UTC 2026
<p>อัปเดต 10:15:43</p>
```

การลบรอประมาณ 30 วินาที (เพราะ `sh` ของ busybox ใน `menu-writer` ไม่ตอบ SIGTERM) และเมื่อสร้างใหม่ เวลา "สร้างเมื่อ" เป็นค่าใหม่ แสดงว่า emptyDir เริ่มจากว่างเปล่า

**ขั้นที่ 5: ลบ Pod**

```bash
kubectl delete pod init-sidecar-pod --now; kubectl get pods
```

```text
pod "init-sidecar-pod" deleted from default namespace
No resources found in default namespace.
```

### สิ่งที่เห็น

- container หลายตัวใน Pod เดียว: READY `2/2`, IP เดียว, คุยกันผ่าน `localhost`
- `kubectl exec`/`logs` ที่ไม่ระบุ `-c` จะใช้ container แรกและแจ้ง `Defaulted container ...`
- init container รันจบก่อน (`Init:0/1` → `Running`) และไม่ถูกนับใน READY
- **container restart → emptyDir รอด / ลบ Pod → emptyDir ว่างใหม่** นี่คือหัวใจที่จะใช้ใน LAB 9

> **🏆 ท้าทาย:** เพิ่ม sidecar ตัวที่สามชื่อ `counter` (busybox) ที่ทุก 10 วินาทีพิมพ์จำนวนบรรทัดของ `/html/index.html` ลง stdout แล้วดูด้วย `kubectl logs init-sidecar-pod -c counter -f`

---

## LAB 9: LAB สุดท้าย: ร้านอาหารแมวน้องส้ม

<p align="center" id="fig-11">
  <img src="images/10-lab9-som-shop-storefront.png" alt="รูปที่ 11 LAB9 ร้านอาหารแมวน้องส้ม" width="900"><br>
  <em><b>รูปที่ 11</b> LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้มด้วย Next.js + PostgreSQL ใน Pod เดียว</em>
</p>

**เป้าหมาย:** build image ของแอป Next.js เอง นำเข้าคลัสเตอร์ด้วย `kind load` เปิดร้านใน Pod เดียวที่มี native sidecar (PostgreSQL), init container 2 ตัว, emptyDir, env, resources และ probes ครบ แล้วเปิดร้านใน browser กดสั่งซื้อ และทดลองว่าข้อมูลรอดหรือหายในสถานการณ์ใด

> ⚠️ **ออกแบบเพื่อการเรียนรู้เท่านั้น** การใส่เว็บกับฐานข้อมูลไว้ใน Pod เดียว **ไม่ควรทำในงานจริง** (scale แยกไม่ได้, ลบ Pod = ข้อมูลหาย, อัปเดตเว็บต้องรีสตาร์ทฐานข้อมูลด้วย) รหัสผ่าน `meow1234` ใน env ก็ใช้เพื่อการเรียนเท่านั้น บทถัดไปจะแยกส่วนอย่างถูกต้อง

### 9.1 สถาปัตยกรรมของ Pod som-shop

<p align="center" id="fig-12">
  <img src="images/11-lab9-pod-architecture.png" alt="รูปที่ 12 สถาปัตยกรรม Pod som-shop" width="900"><br>
  <em><b>รูปที่ 12</b> สถาปัตยกรรม Pod som-shop: web (Next.js :3000) คุยกับ db (PostgreSQL :5432) ผ่าน localhost ภายใน Pod เดียว และเก็บข้อมูล DB บน emptyDir</em>
</p>

```text
Pod som-shop  (labels: app=som-shop, part=all-in-one)   IP เดียว เช่น 10.244.3.21   อยู่บน lab-worker หรือ lab-worker2
├─ initContainers (ทำงานตามลำดับ)
│  1. db           postgres:17.11-alpine   restartPolicy: Always (native sidecar)   :5432
│  2. wait-for-db  postgres:17.11-alpine   until pg_isready -h localhost ...         (exit 0)
│  3. db-seed      som-shop-web:1.0        node scripts/seed.mjs                     (exit 0)
├─ containers
│  └─ web          som-shop-web:1.0        Next.js (node server.js)                  :3000
└─ volumes
   └─ db-data      emptyDir {}  → mount ที่ db:/var/lib/postgresql/data
```

**ตาราง** container ทั้ง 4 ตัว

| container | image | หน้าที่ | probes | resources (requests / limits) |
|---|---|---|---|---|
| `db` | `postgres:17.11-alpine` | ฐานข้อมูล `catshop` (user `som`) ทำงานตลอดอายุ Pod | startup + readiness: exec `pg_isready`, liveness: tcpSocket 5432 | 100m/256Mi — 500m/512Mi |
| `wait-for-db` | `postgres:17.11-alpine` | วน `pg_isready` จนต่อ DB ทาง `localhost` ได้ | – | 10m/16Mi — 100m/64Mi |
| `db-seed` | `som-shop-web:1.0` | สร้างตาราง `products`, `orders` และใส่สินค้า 6 รายการ (รันซ้ำได้ ไม่ซ้ำข้อมูล) | – | 50m/64Mi — 300m/256Mi |
| `web` | `som-shop-web:1.0` | หน้าร้าน, `/api/health`, `/api/products`, `POST /api/orders` | readiness + liveness: httpGet `/api/health` :3000 | 100m/192Mi — 500m/512Mi |

แอป Next.js (โฟลเดอร์ `som-shop/app/`) ใช้ Next.js 16.3.8, React 19.3.0 และ `pg` 8.23.1 build แบบ multi-stage บน `node:22-alpine` และรันเป็น user `node` (ไม่ใช่ root) ทั้ง `db-seed` และ `web` ต่อฐานข้อมูลด้วย `DATABASE_URL=postgres://som:meow1234@localhost:5432/catshop` ซึ่งใช้ `localhost` ได้เพราะอยู่ใน Pod เดียวกับ `db`

### 9.2 ลำดับการเริ่มและทำไม db ต้องเป็น native sidecar

<p align="center" id="fig-13">
  <img src="images/12-lab9-startup-order.png" alt="รูปที่ 13 ลำดับการเริ่ม Pod som-shop" width="900"><br>
  <em><b>รูปที่ 13</b> ลำดับเริ่ม Pod: db (native sidecar) เริ่มก่อนและผ่าน startupProbe → wait-for-db รอ pg_isready → db-seed สร้างตารางและสินค้า → web เริ่มทำงาน</em>
</p>

init container ปกติต้องรันจนจบก่อน app container ทุกตัว ถ้าวาง PostgreSQL ไว้ใน `containers` แล้วให้ `wait-for-db` รอ จะรอไม่มีวันจบ (deadlock) จึงวาง `db` ไว้ **บนสุดของ `initContainers` พร้อม `restartPolicy: Always`** (native sidecar, GA ตั้งแต่ Kubernetes 1.33 คลัสเตอร์ของเราเป็น v1.37.0) kubelet จะเริ่ม `db` แล้วรอ startupProbe ผ่านก่อนรัน init ตัวถัดไป และ `db` ทำงานต่อตลอดอายุ Pod

เนื้อหาเต็มของ `som-shop/k8s/som-shop-pod.yaml` (ดูในเครื่องได้ด้วย `cat som-shop/k8s/som-shop-pod.yaml`)

```yaml
# LAB 9: ร้านอาหารแมวน้องส้ม — Next.js + PostgreSQL ใน Pod เดียว
# ออกแบบเพื่อการเรียนรู้เท่านั้น! งานจริงควรแยก web กับ db คนละ Pod (บทหน้า)
apiVersion: v1
kind: Pod
metadata:
  name: som-shop
  labels:                       # ใช้ค้นหาด้วย -l app=som-shop
    app: som-shop
    part: all-in-one
spec:
  volumes:
    - name: db-data              # ที่เก็บข้อมูล Postgres: รอดตอน container restart แต่หายเมื่อลบ Pod
      emptyDir: {}

  initContainers:                # ทำงานตามลำดับจากบนลงล่าง
    # 1) db: native sidecar (restartPolicy: Always) → เริ่มก่อน และรันต่อไปตลอดอายุ Pod
    - name: db
      image: postgres:17.11-alpine
      restartPolicy: Always      # ทำให้ init container นี้กลายเป็น sidecar (K8s 1.33+)
      env:
        - name: POSTGRES_USER
          value: som
        - name: POSTGRES_PASSWORD
          value: meow1234        # เพื่อการเรียนเท่านั้น บทหน้าจะย้ายไปเก็บใน Secret
        - name: POSTGRES_DB
          value: catshop
        - name: PGDATA           # ใช้โฟลเดอร์ย่อย กันปัญหา "directory ไม่ว่าง"
          value: /var/lib/postgresql/data/pgdata
      ports:
        - containerPort: 5432    # PostgreSQL ฟัง port นี้ (ข้อมูลประกอบ)
      volumeMounts:
        - name: db-data
          mountPath: /var/lib/postgresql/data   # ข้อมูล DB ไปอยู่บน emptyDir
      startupProbe:              # ผ่านเมื่อไร init ตัวถัดไปจึงเริ่ม
        exec:
          command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
        periodSeconds: 2
        failureThreshold: 30     # รอได้สูงสุด 2 x 30 = 60 วินาที
      readinessProbe:            # ผ่าน → db นับเป็น READY (เห็น 1/2)
        exec:
          command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
        periodSeconds: 5
      livenessProbe:             # เปิด port 5432 ไม่ได้ 3 ครั้งติด → restart db
        tcpSocket:
          port: 5432
        periodSeconds: 10
        failureThreshold: 3
      resources:                 # requests = จองตอนเลือก Node, limits = เพดาน
        requests: { cpu: 100m, memory: 256Mi }
        limits:   { cpu: 500m, memory: 512Mi }

    # 2) wait-for-db: รอจนต่อ db ทาง localhost ได้ (exit 0 แล้วจบ)
    - name: wait-for-db
      image: postgres:17.11-alpine # ใช้ image เดียวกับ db เพื่อให้มีคำสั่ง pg_isready
      command:
        - sh
        - -c
        - until pg_isready -h localhost -p 5432 -U som -d catshop; do echo "รอฐานข้อมูล..."; sleep 2; done; echo "ฐานข้อมูลพร้อมแล้ว"
      resources:
        requests: { cpu: 10m, memory: 16Mi }
        limits:   { cpu: 100m, memory: 64Mi }

    # 3) db-seed: สร้างตาราง + ใส่สินค้าตั้งต้น (ใช้ image เดียวกับเว็บ)
    - name: db-seed
      image: som-shop-web:1.0
      imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน node (ไม่ไปดึงจาก Docker Hub)
      command: ["node", "scripts/seed.mjs"]   # สร้างตาราง + ใส่สินค้า 6 รายการ (รันซ้ำได้)
      env:
        - name: DATABASE_URL     # ต่อ db ผ่าน localhost เพราะอยู่ Pod เดียวกัน
          value: postgres://som:meow1234@localhost:5432/catshop
      resources:
        requests: { cpu: 50m, memory: 64Mi }
        limits:   { cpu: 300m, memory: 256Mi }

  containers:
    # web: หน้าร้าน Next.js คุยกับ db ผ่าน localhost:5432
    - name: web
      image: som-shop-web:1.0
      imagePullPolicy: IfNotPresent
      env:
        - name: DATABASE_URL
          value: postgres://som:meow1234@localhost:5432/catshop
        - name: SHOP_NAME          # ชื่อร้านที่แสดงบนหน้าเว็บ
          value: "ร้านอาหารแมวน้องส้ม"
        - name: PORT               # port ที่ Next.js ฟัง
          value: "3000"
        - name: HOSTNAME           # ให้ Next.js ฟังทุก interface (ค่าเดิมของ HOSTNAME คือชื่อ Pod)
          value: "0.0.0.0"
      ports:
        - containerPort: 3000    # port ที่ port-forward 3000:3000 ส่งเข้ามา
      readinessProbe:              # พร้อมรับลูกค้าเมื่อ /api/health ตอบ 200
        httpGet:
          path: /api/health
          port: 3000
        periodSeconds: 5
        failureThreshold: 2
      livenessProbe:               # ค้างนานเกินไป → kubelet restart container web
        httpGet:
          path: /api/health
          port: 3000
        initialDelaySeconds: 10
        periodSeconds: 10
        failureThreshold: 6
      resources:
        requests: { cpu: 100m, memory: 192Mi }
        limits:   { cpu: 500m, memory: 512Mi }
```

#### อธิบาย YAML: `som-shop/k8s/som-shop-pod.yaml`

**ระดับ Pod**

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `metadata.labels` `app: som-shop`, `part: all-in-one` | ป้ายสำหรับค้นหา และเตรียมไว้ให้ Service ใช้เลือก Pod ในบทถัดไป | ใช้ `-l app=som-shop` ค้นหาได้ |
| `volumes: db-data` → `emptyDir: {}` | ที่เก็บไฟล์ฐานข้อมูล อายุเท่ากับ Pod | 9.9 restart `db` แล้วออเดอร์ยังอยู่ (3), 9.10 ลบ Pod แล้วออเดอร์เป็น 0 |
| `initContainers` 3 ตัว (`db`, `wait-for-db`, `db-seed`) | ทำงานตามลำดับบนลงล่าง ตัวถัดไปเริ่มเมื่อตัวก่อนหน้า "เสร็จ" (init ปกติ = exit 0, sidecar = startupProbe ผ่าน) | STATUS `Init:0/3` → `Init:1/3` → `Init:2/3` → `PodInitializing` |
| `containers` 1 ตัว (`web`) | แอปหลัก เริ่มหลัง init ทุกตัวเสร็จ | `kubectl logs som-shop` เลือก `web` ให้: `Defaulted container "web" out of: web, db (init), wait-for-db (init), db-seed (init)` |

**container `db` (native sidecar)**

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `restartPolicy: Always` (ใน initContainers) | เปลี่ยน init container ให้เป็น **native sidecar**: เริ่มก่อนและรันตลอดอายุ Pod ไม่ต้องรอให้จบ | READY นับ `db` ด้วย จึงเป็น `2/2`; ถูก restart เองเมื่อ PostgreSQL หยุด (9.9) |
| `env` `POSTGRES_USER/PASSWORD/DB` | image postgres ใช้สร้าง user `som`, รหัส `meow1234`, ฐานข้อมูล `catshop` ครั้งแรกที่โฟลเดอร์ข้อมูลว่าง | `psql -U som -d catshop` ใช้ได้, log `PostgreSQL init process complete` |
| `env` `PGDATA=/var/lib/postgresql/data/pgdata` | ให้ข้อมูลอยู่ในโฟลเดอร์ย่อยของ volume (กันปัญหาโฟลเดอร์ mount ไม่ว่าง) | – |
| `volumeMounts` `db-data` → `/var/lib/postgresql/data` | ไฟล์ฐานข้อมูลลงไปอยู่บน emptyDir ไม่ใช่ใน container | ข้อมูลรอดเมื่อ container `db` restart |
| `startupProbe` exec `pg_isready ... -h 127.0.0.1` ทุก 2 วิ สูงสุด 30 ครั้ง | บอก kubelet ว่า sidecar "เริ่มเสร็จ" เมื่อไร init ตัวถัดไปจึงเริ่ม (รอได้ 60 วินาที) ใช้ `127.0.0.1` เพื่อเลี่ยงปัญหา IPv6 | `Init:0/3` → `Init:1/3` ที่ราววินาทีที่ 4 |
| `readinessProbe` exec `pg_isready` ทุก 5 วิ | บอกว่า `db` พร้อมรับงาน | READY เปลี่ยนจาก `0/2` เป็น `1/2` ระหว่าง init |
| `livenessProbe` tcpSocket 5432 ทุก 10 วิ, failureThreshold 3 | ถ้าเปิด port ไม่ได้ติดกัน 3 ครั้งจะ restart `db` | ไม่ล้มในการทดลอง (restart ใน 9.9 เกิดจากโปรเซสจบ ไม่ใช่ probe) |
| `resources` 100m/256Mi — 500m/512Mi | จอง/จำกัดทรัพยากรของฐานข้อมูล | Pod มี requests จึงไม่ใช่ BestEffort |

**init `wait-for-db` และ `db-seed`**

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `wait-for-db` → `image: postgres:17.11-alpine` | ใช้ image เดียวกับ `db` เพื่อให้มีคำสั่ง `pg_isready` (และไม่ต้องดึง image เพิ่ม) | – |
| `wait-for-db` → `until pg_isready -h localhost ...; do ...; done` | วนจนต่อ `db` ผ่าน `localhost` ได้ แล้ว exit 0 พิสูจน์ว่า container อื่นเห็น `db` ทาง localhost | `logs -c wait-for-db`: `localhost:5432 - accepting connections` / `ฐานข้อมูลพร้อมแล้ว` |
| `db-seed` → `image: som-shop-web:1.0` + `imagePullPolicy: IfNotPresent` | ใช้ image ของเว็บที่ `kind load` ไว้บน node (มี `scripts/seed.mjs` และ `pg`) ไม่ไปดึงจาก Docker Hub (ซึ่งไม่มี image นี้) | ถ้าลืม `kind load` จะค้าง `Init:ErrImagePull` (ดู Troubleshooting) |
| `db-seed` → `command: ["node", "scripts/seed.mjs"]` | สร้างตารางและใส่สินค้า 6 รายการ เขียนให้รันซ้ำได้โดยไม่ซ้ำข้อมูล | `seeded 6 products (new: 6)`; หลัง 9.9 log ยังเป็นของรอบแรก (ไม่ถูกรันซ้ำ) |
| `DATABASE_URL=postgres://som:meow1234@localhost:5432/catshop` | ต่อ `db` ทาง `localhost` ได้เพราะอยู่ Pod เดียวกัน | `connected to database` |

**container `web`**

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `env SHOP_NAME` | ชื่อร้านที่แอปแสดงบนหน้าเว็บ | `<title>ร้านอาหารแมวน้องส้ม</title>` |
| `env PORT="3000"` | port ที่ Next.js ฟัง (ต้องเป็น string) | `- Local: http://localhost:3000` |
| `env HOSTNAME="0.0.0.0"` | Next.js standalone ใช้ `HOSTNAME` เป็นที่อยู่ที่จะฟัง แต่ Kubernetes ตั้ง `HOSTNAME` = ชื่อ Pod ให้อัตโนมัติ (เห็นแล้วใน LAB 6) จึงต้องทับเป็น `0.0.0.0` | `- Network: http://0.0.0.0:3000`; `netstat` เห็น `0.0.0.0:3000` (IPv4 เท่านั้น จึงเกิดเรื่องใน 9.7) |
| `ports: containerPort: 3000` | ข้อมูลประกอบว่าแอปฟัง 3000 | `kubectl port-forward pod/som-shop 3000:3000` |
| `readinessProbe` httpGet `/api/health` :3000 ทุก 5 วิ | `web` พร้อมเมื่อแอปตอบ 200 (endpoint นี้ตรวจการต่อ DB ด้วย) | READY `1/2` → `2/2`; `{"ok":true,"db":"up"}` |
| `livenessProbe` httpGet `/api/health` เริ่มที่ 10 วิ ทุก 10 วิ ล้ม 6 ครั้ง | ถ้าแอปค้างนาน (~60 วินาที) จึง restart ตั้งให้ทนนานกว่า readiness เพื่อไม่ให้ restart เว็บเพียงเพราะ DB หยุดชั่วครู่ | 9.9 `web restarts=0` แม้ `db` restart |
| `resources` 100m/192Mi — 500m/512Mi | จอง/จำกัดทรัพยากรของเว็บ | – |

### 9.3 Build image และนำเข้าคลัสเตอร์

<p align="center" id="fig-14">
  <img src="images/13-lab9-build-kind-load.png" alt="รูปที่ 14 build และ kind load" width="900"><br>
  <em><b>รูปที่ 14</b> build image som-shop-web:1.0 ใน k8s-lab แล้วใช้ kind load docker-image นำ image เข้าไปในทุก node ของคลัสเตอร์</em>
</p>

node ของ kind เป็น container แยก มี containerd ของตัวเอง **มองไม่เห็น image ใน Docker ของ k8s-lab** จึงต้อง `kind load` เข้าไปก่อน

🐧 **ใน SSH session ของ k8s-lab**

**ขั้นที่ 1: build image** (เครื่องทดสอบใช้ ~30–35 วินาที เครื่องหรือเน็ตช้าอาจหลายนาที เพราะต้องดึง `node:22-alpine` และ `npm ci`)

```bash
cd /workspace/002_kubernetes_pod/02_LAB/som-shop/app
time docker build -t som-shop-web:1.0 .
docker images som-shop-web:1.0
```

```text
...
#15 [runner 6/6] COPY --from=build --chown=node:node /app/scripts ./scripts
#15 DONE 0.1s

#16 exporting to image
...
#16 naming to docker.io/library/som-shop-web:1.0 done
#16 unpacking to docker.io/library/som-shop-web:1.0 1.4s done
#16 DONE 2.8s

real	0m33.589s

IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
som-shop-web:1.0   f7f95c33aeb3        305MB         76.6MB        
```

(image ID เปลี่ยนทุกครั้งที่ build ของนักศึกษาจะไม่ใช่ `f7f95c33aeb3` และเวลา `real` ขึ้นกับความเร็วเครื่อง/เน็ต)

**ขั้นที่ 2: นำ image ของเว็บเข้าทุก node**

```bash
cd /workspace/002_kubernetes_pod/02_LAB
time kind load docker-image som-shop-web:1.0 --name lab
```

```text
Image: "som-shop-web:1.0" with ID "sha256:f7f95c33aeb3b8f0330ce25d02245bcc148cca8e527f8be472505e5de83a85b6" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.0" with ID "sha256:f7f95c33aeb3b8f0330ce25d02245bcc148cca8e527f8be472505e5de83a85b6" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.0" with ID "sha256:f7f95c33aeb3b8f0330ce25d02245bcc148cca8e527f8be472505e5de83a85b6" not yet present on node "lab-worker", loading...

real	0m5.377s
```

(ลำดับของ node ในข้อความอาจสลับกันได้ เพราะ kind โหลดเข้าทุก node พร้อมกัน)

**ขั้นที่ 3: preload image ของ PostgreSQL** (แนะนำ เพื่อเลี่ยง rate limit ของ Docker Hub เมื่อทั้งห้องดึงพร้อมกัน)

```bash
docker pull postgres:17.11-alpine
docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar
kind load image-archive /tmp/pg.tar --name lab
```

> **ทำไมไม่ใช้ `kind load docker-image postgres:17.11-alpine` ตรง ๆ?** ในการทดสอบจริง คำสั่งนั้นล้มเหลวด้วยข้อความ
>
> ```text
> ERROR: failed to load image: command "docker exec --privileged -i lab-worker ctr --namespace=k8s.io images import --all-platforms --digests --snapshotter=overlayfs -" failed with error: exit status 1
>
> Command Output: ctr: content digest sha256:612d0227f7b0bbd2261526483482a421f7045756d847650f8434e495bdfc3906: not found
> ```
>
> (ชื่อ node ในข้อความ `docker exec ... -i <node> ctr ...` อาจต่างกันในแต่ละครั้ง รอบทดลองล่าสุดเป็น `lab-worker` และได้ digest `sha256:612d0227...` เดียวกัน) ส่วนวิธีด้านล่าง `docker save` + `kind load image-archive` ทำงานสำเร็จโดย **ไม่พิมพ์อะไรออกมา**
>
> สาเหตุคือ Docker 29 ใน k8s-lab ใช้ containerd image store และ `postgres` เป็น image แบบหลาย platform ซึ่ง `docker pull` ดาวน์โหลดเนื้อหามาเฉพาะ platform ของเครื่องเรา (amd64) แต่ `kind load docker-image` สั่ง node ให้นำเข้า **ทุก platform** (`--all-platforms`) จึงหาเนื้อหาของ platform อื่นไม่เจอ ส่วน `docker save --platform linux/amd64` ส่งออกเฉพาะ platform เดียวที่มีอยู่จริง จึงนำเข้าได้ (`som-shop-web:1.0` ที่ build เองมี platform เดียวอยู่แล้ว จึงใช้ `kind load docker-image` ได้ปกติ)
>
> - **เครื่อง ARM (เช่น Apple Silicon):** เปลี่ยนเป็น `--platform linux/arm64` (ยังไม่ได้ทดสอบบน ARM)
> - **ถ้าข้ามขั้นนี้:** kubelet จะดึง `postgres:17.11-alpine` จาก Docker Hub เองตอนสร้าง Pod (ต้องมีอินเทอร์เน็ตและไม่ติด rate limit กรณีนี้ไม่ได้ทดสอบในรอบทดลอง)

**ขั้นที่ 4: ตรวจว่า image อยู่บน node แล้ว**

```bash
docker exec lab-worker crictl images | grep -E "som-shop|postgres"; docker exec lab-worker2 crictl images | grep -E "som-shop|postgres"
```

```text
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  7d41ccc7d40d3       76.6MB
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  7d41ccc7d40d3       76.6MB
```

(IMAGE ID ของ `som-shop-web` ต่างกันทุกครั้งที่ build ส่วน `postgres` ควรได้ `79bd7c99e9231` เหมือนกัน; `docker exec lab-worker ...` ใช้ได้เพราะ node ของ kind คือ container ใน Docker ของ k8s-lab และ `crictl` คือเครื่องมือดู image/container ของ containerd บน node)

### 9.4 Apply และเฝ้าดูลำดับการเริ่ม

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/002_kubernetes_pod/02_LAB`)

```bash
kubectl apply -f som-shop/k8s/som-shop-pod.yaml
kubectl get pod som-shop -w
```

เมื่อเห็น `2/2 Running` แล้วกด **Ctrl+C** ผลจริง

```text
pod/som-shop created
NAME       READY   STATUS     RESTARTS   AGE
som-shop   0/2     Init:0/3   0          0s
som-shop   0/2     Init:0/3   0          0s
som-shop   0/2     Init:0/3   0          1s
som-shop   0/2     Init:1/3   0          4s
som-shop   0/2     Init:1/3   0          4s
som-shop   1/2     Init:1/3   0          4s
som-shop   1/2     Init:1/3   0          4s
som-shop   1/2     Init:2/3   0          5s
som-shop   1/2     Init:2/3   0          5s
som-shop   1/2     PodInitializing   0          6s
som-shop   1/2     Running           0          6s
som-shop   2/2     Running           0          7s
som-shop   2/2     Running           0          8s
```

(จำนวนบรรทัดซ้ำและ AGE ของแต่ละบรรทัดอาจต่างเล็กน้อย แต่ลำดับสถานะจะเหมือนกัน)

**อ่านผล:** `Init:1/3` = `db` เริ่มแล้วและผ่าน startupProbe → `1/2` = `db` พร้อม (readiness ผ่าน) → `Init:2/3` = `wait-for-db` จบ → `PodInitializing` = `db-seed` จบ กำลังเริ่ม `web` → `2/2 Running` = `web` ผ่าน readinessProbe READY เป็น **`2/2`** เพราะนับ `web` กับ native sidecar `db` ส่วน init ที่จบแล้วไม่นับ (ถ้า image อยู่บน node แล้วจะใช้เวลาราว 7–9 วินาที)

```bash
kubectl get pod som-shop -o wide
kubectl describe pod som-shop | sed -n "/^Init Containers:/,/^Volumes:/p" | grep -E "^  [a-z-]+:|State:|Ready:|Restart Count|Reason"
```

```text
NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-shop   2/2     Running   0          20s   10.244.3.21   lab-worker2   <none>           <none>

  db:
    State:          Running
    Ready:          True
    Restart Count:  0
  wait-for-db:
    State:          Terminated
      Reason:       Completed
    Ready:          True
    Restart Count:  0
  db-seed:
    State:          Terminated
      Reason:       Completed
    Ready:          True
    Restart Count:  0
  web:
    State:          Running
    Ready:          True
    Restart Count:  0
```

### 9.5 อ่าน logs ของแต่ละ container

```bash
kubectl logs som-shop -c wait-for-db
kubectl logs som-shop -c db-seed
kubectl logs som-shop -c db | tail -8
kubectl logs som-shop -c web
```

```text
$ kubectl logs som-shop -c wait-for-db
localhost:5432 - accepting connections
ฐานข้อมูลพร้อมแล้ว

$ kubectl logs som-shop -c db-seed
connected to database
tables ready: products, orders
seeded 6 products (new: 6)

$ kubectl logs som-shop -c db | tail -8
PostgreSQL init process complete; ready for start up.

2026-10-05 10:16:53.381 UTC [1] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
2026-10-05 10:16:53.381 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-10-05 10:16:53.381 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-10-05 10:16:53.388 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-10-05 10:16:53.396 UTC [68] LOG:  database system was shut down at 2026-10-05 10:16:53 UTC
2026-10-05 10:16:53.405 UTC [1] LOG:  database system is ready to accept connections

$ kubectl logs som-shop -c web
▲ Next.js 16.3.8
- Local:         http://localhost:3000
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
✓ Running next.config took 1.0ms
```

ถ้าไม่ใส่ `-c` kubectl จะเลือก `web` และแจ้ง `Defaulted container "web" out of: web, db (init), wait-for-db (init), db-seed (init)`

### 9.6 สำรวจฐานข้อมูลด้วย psql

```bash
kubectl exec som-shop -c db -- psql -U som -d catshop -c 'SELECT sku,name_th,price_baht,stock FROM products;'
```

```text
      sku      |           name_th            | price_baht | stock 
---------------+------------------------------+------------+-------
 DRY-TUNA-15   | อาหารเม็ดสูตรปลาทูน่า 1.5 กก.    |     459.00 |    20
 DRY-KITTEN-1  | อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก. |     389.00 |    15
 DRY-SENIOR-12 | อาหารเม็ดแมวสูงวัย 1.2 กก.      |     499.00 |    10
 WET-SABA-85   | อาหารเปียกปลาซาบะ 85 ก.       |      35.00 |    60
 TRT-LICK-4    | ขนมแมวเลียรสไก่ (แพ็ก 4)        |      59.00 |    40
 TRT-SALMON-40 | ขนมฟรีซดรายแซลมอน 40 ก.       |     129.00 |    25
(6 rows)
```

(คอลัมน์ภาษาไทยอาจไม่ตรงแนวใน terminal เป็นเรื่องปกติ)

### 9.7 ตรวจ health ภายใน Pod และเรื่อง localhost กับ IPv6

ลองเรียก `/api/health` จากใน container `web`

```bash
kubectl exec som-shop -c web -- wget -qO- http://localhost:3000/api/health; echo
```

```text
wget: can't connect to remote host: Connection refused
command terminated with exit code 1
```

ทำไมล้มเหลว ทั้งที่ readinessProbe ผ่าน มาสืบกัน

```bash
kubectl exec som-shop -c web -- sh -c "grep localhost /etc/hosts; netstat -tln"
```

```text
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 0.0.0.0:3000            0.0.0.0:*               LISTEN      
tcp        0      0 0.0.0.0:5432            0.0.0.0:*               LISTEN      
tcp        0      0 :::5432                 :::*                    LISTEN      
```

(ลำดับบรรทัดของ `netstat` อาจสลับกันได้ สิ่งที่สำคัญคือมี `:::5432` แต่ **ไม่มี** `:::3000`)

- `localhost` มีทั้ง IPv4 (`127.0.0.1`) และ IPv6 (`::1`) และ `wget` ของ busybox ลอง `::1` ก่อน
- Next.js (`HOSTNAME=0.0.0.0`) ฟัง port 3000 **เฉพาะ IPv4** (`0.0.0.0:3000` ไม่มี `:::3000`) จึงปฏิเสธการเชื่อมต่อทาง `::1`
- PostgreSQL ฟังทั้ง IPv4 และ IPv6 (`0.0.0.0:5432` และ `:::5432`) ดังนั้น `localhost:5432` ใช้ได้ทุกกรณี
- `netstat` ใน container `web` เห็น port 5432 ของ `db` ด้วย พิสูจน์ว่าใช้ network namespace เดียวกัน

แก้โดยเรียก IPv4 ตรง ๆ

```bash
kubectl exec som-shop -c web -- wget -qO- http://127.0.0.1:3000/api/health; echo
kubectl exec som-shop -c web -- sh -c "hostname; id; hostname -i"; kubectl exec som-shop -c db -- hostname -i
```

```text
{"ok":true,"db":"up"}

som-shop
uid=1000(node) gid=1000(node) groups=1000(node)
10.244.3.21
10.244.3.21
```

container `web` รันเป็น user `node` (ไม่ใช่ root) และทั้ง `web` กับ `db` มี IP เดียวกัน

### 9.8 เปิดร้านใน browser และสั่งซื้อ

<p align="center" id="fig-15">
  <img src="images/14-lab9-open-in-browser.png" alt="รูปที่ 15 เปิดร้านจาก browser" width="900"><br>
  <em><b>รูปที่ 15</b> เปิดร้านจากเครื่องนักศึกษา: kubectl port-forward pod/som-shop 3000:3000 ใน k8s-lab และ ssh -L 3000:localhost:3000 จากเครื่องนักศึกษา</em>
</p>

**ขั้นที่ 1:** 🐧 **ใน SSH session หลักของ k8s-lab** เปิด port-forward ค้างไว้

```bash
kubectl port-forward pod/som-shop 3000:3000
```

```text
Forwarding from 127.0.0.1:3000 -> 3000
Forwarding from [::1]:3000 -> 3000
```

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ (ถ้าหน้าต่าง `ssh -L 8080` จาก LAB 3 ยังเปิดอยู่ ให้ `exit` ก่อน)

```bash
ssh -p 2223 -L 3000:localhost:3000 root@localhost
```

**ขั้นที่ 3:** 🐧 **ใน SSH session ที่สอง (หน้าต่างท่อ)** ทดสอบ API

```bash
curl -s localhost:3000/api/health; echo
curl -s localhost:3000/api/products | head -c 300; echo
```

```text
{"ok":true,"db":"up"}
[{"id":1,"sku":"DRY-TUNA-15","name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","category":"dry","price_baht":"459.00","stock":20,"emoji":"🐟"},{"id":2,"sku":"DRY-KITTEN-1","name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 �
```

(ตัวอักษรเพี้ยนท้ายบรรทัดเกิดจาก `head -c 300` ตัดกลางตัวอักษรไทย ไม่ใช่ข้อผิดพลาด)

**ขั้นที่ 4:** 🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:3000**

<p align="center" id="fig-16">
  <img src="images/screenshots/20261005_1725_lab002_01-som-shop.png" alt="รูปที่ 16 ภาพหน้าจอจริง หน้าร้านเริ่มต้น" width="700"><br>
  <em><b>รูปที่ 16</b> ภาพหน้าจอจริงจากการทดลอง: หน้าร้านอาหารแมวน้องส้มเมื่อเปิดครั้งแรก มีสินค้า 6 รายการ ออเดอร์ทั้งหมด 0 และ footer แสดงว่าเสิร์ฟโดย Pod som-shop (ภาพนี้ถ่ายผ่าน NodePort Service ชั่วคราวที่เพิ่มเองเพื่อถ่ายภาพ หน้าที่เห็นเหมือนกับที่เปิดผ่าน port-forward + ssh -L)</em>
</p>

กดปุ่ม **🛒 สั่งซื้อ** 3 ครั้ง (เลือกสินค้าต่างกันได้) แต่ละการ์ดจะขึ้น "สั่งซื้อแล้ว! ออเดอร์ #N" จำนวน "เหลือ ... ชิ้น" ลดลง และมีรายการใน "ออเดอร์ล่าสุด"

<p align="center" id="fig-17">
  <img src="images/screenshots/20261004_1814_lab9_02-shop-after-orders.png" alt="รูปที่ 17 ภาพหน้าจอจริง หลังสั่งซื้อ 3 ครั้ง" width="700"><br>
  <em><b>รูปที่ 17</b> ภาพหน้าจอจริงจากการทดลอง: หลังกดสั่งซื้อ 3 ครั้ง ออเดอร์ทั้งหมดเป็น 3, stock ของสินค้าที่สั่งลดลง และมีรายการออเดอร์ล่าสุด 3 รายการ</em>
</p>

**(ทางเลือก) สั่งซื้อด้วย curl** ใน SSH session ที่สอง เพื่อดู API โดยตรง ผลจริงจากรอบทดสอบ (รอบนั้นมีออเดอร์แรกเป็นสินค้า id 1 จำนวน 1 ชิ้นก่อนแล้ว — ได้ `{"ok":true,"order_id":1,"product":{"id":1,...,"stock":19}}` — order_id ด้านล่างจึงเริ่มที่ 2)

```bash
curl -s -X POST localhost:3000/api/orders -H 'Content-Type: application/json' -d '{"product_id":4,"qty":2}'; echo
curl -s -X POST localhost:3000/api/orders -H 'Content-Type: application/json' -d '{"product_id":4,"qty":3}'; echo
curl -s -X POST localhost:3000/api/orders -H 'Content-Type: application/json' -d '{"product_id":3,"qty":99}'; echo
```

```text
{"ok":true,"order_id":2,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":58}}
{"ok":true,"order_id":3,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":55}}
{"ok":false,"error":"ข้อมูลไม่ถูกต้อง"}
```

(API รับ `qty` ได้ 1–10 ต่อออเดอร์ จึงปฏิเสธ `99`) ตรวจออเดอร์ในฐานข้อมูล

```bash
kubectl exec som-shop -c db -- psql -U som -d catshop -c 'SELECT o.id, p.sku, o.qty, p.stock FROM orders o JOIN products p ON p.id=o.product_id ORDER BY o.id;'
```

```text
 id |     sku     | qty | stock 
----+-------------+-----+-------
  1 | DRY-TUNA-15 |   1 |    19
  2 | WET-SABA-85 |   2 |    55
  3 | WET-SABA-85 |   3 |    55
(3 rows)
```

(คอลัมน์ `stock` คือ stock **ปัจจุบัน** ของสินค้านั้น ไม่ใช่ ณ เวลาที่สั่ง ผลของนักศึกษาจะต่างตามสินค้าที่กดสั่ง)

### 9.9 ทดลองที่ 1: ฐานข้อมูลตาย แล้วข้อมูลยังอยู่ไหม

<p align="center" id="fig-18">
  <img src="images/15-lab9-emptydir-survive-vs-lost.png" alt="รูปที่ 18 emptyDir รอด vs หาย" width="900"><br>
  <em><b>รูปที่ 18</b> ทดลองกับข้อมูลออเดอร์: restart container db แล้วข้อมูลยังอยู่บน emptyDir แต่ลบ Pod แล้วข้อมูลหายทั้งหมด</em>
</p>

🐧 **ใน SSH session ที่สอง** (ให้ port-forward ในหน้าต่างหลักทำงานต่อไป) สั่งหยุด PostgreSQL ภายใน container `db`

```bash
kubectl exec som-shop -c db -- su postgres -c 'pg_ctl stop -m fast'
kubectl get pod som-shop -w
```

```text
waiting for server to shut down....command terminated with exit code 137
```

`exit code 137` **เป็นเรื่องปกติ** เพราะเมื่อ PostgreSQL (โปรเซสหลักของ container) หยุด container `db` จะจบ และคำสั่ง `exec` ที่รันอยู่ข้างในจึงถูกตัดไปด้วย ผลการเฝ้าดูจริง (สุ่มดูทุก ~1 วินาที)

```text
t+1s  2/2 Running 0 31s
t+2s  2/2 Running 0 32s
t+3s  1/2 Init:0/3 1 (1s ago) 33s
t+4s  1/2 Running 1 (3s ago) 35s
t+5s  2/2 Running 1 (4s ago) 36s
... (t+6s ถึง t+20s คงที่ 2/2 Running 1 — ไม่มีการเปลี่ยนแปลงเพิ่ม)
```

(คอลัมน์คือ เวลา, READY, STATUS, RESTARTS, AGE; AGE และวินาทีที่เห็นแต่ละสถานะจะต่างตามจังหวะ)

> **สังเกต:** ช่วงสั้น ๆ ที่ sidecar `db` กำลัง restart คอลัมน์ STATUS แสดง `Init:0/3` แต่ **ไม่ได้แปลว่า init container รันใหม่** (`wait-for-db` และ `db-seed` ไม่ถูกรันซ้ำ) เป็นเพียงวิธีที่ kubectl สรุปสถานะเมื่อ container ใน `initContainers` ยังไม่พร้อม จากนั้นอาจเห็นบรรทัดกลาง **`1/2 Running`** อยู่ราว 1 วินาที (container ทำงานแล้วแต่ยังมีตัวหนึ่งที่ readinessProbe ยังไม่ผ่าน) ก่อนกลับเป็น `2/2 Running` ถ้าสุ่มดูไม่ตรงจังหวะอาจไม่เห็นบางบรรทัด (`Init:0/3` หรือ `1/2 Running`) ก็ได้

กด Ctrl+C แล้วตรวจว่าใครถูก restart และข้อมูลยังอยู่ไหม

```bash
kubectl get pod som-shop -o jsonpath="{range .status.initContainerStatuses[*]}{.name}{\" restarts=\"}{.restartCount}{\"\\n\"}{end}{range .status.containerStatuses[*]}{.name}{\" restarts=\"}{.restartCount}{\"\\n\"}{end}"
kubectl exec som-shop -c db -- psql -U som -d catshop -c 'SELECT count(*) AS orders FROM orders;'
kubectl logs som-shop -c db --previous | tail -4
curl -s localhost:3000/api/health; echo
```

```text
db restarts=1
wait-for-db restarts=0
db-seed restarts=0
web restarts=0

 orders 
--------
      3
(1 row)

2026-10-05 10:17:22.399 UTC [66] LOG:  shutting down
2026-10-05 10:17:22.403 UTC [66] LOG:  checkpoint starting: shutdown immediate
2026-10-05 10:17:22.474 UTC [66] LOG:  checkpoint complete: wrote 77 buffers (0.5%); ...
2026-10-05 10:17:22.477 UTC [1] LOG:  database system is shut down

{"ok":true,"db":"up"}
```

🌐 **browser** กด refresh หน้าร้าน ข้อมูลออเดอร์ยังอยู่ครบ

<p align="center" id="fig-19">
  <img src="images/screenshots/20261004_1815_lab9_03-after-db-restart.png" alt="รูปที่ 19 ภาพหน้าจอจริง หลัง restart db" width="700"><br>
  <em><b>รูปที่ 19</b> ภาพหน้าจอจริงจากการทดลอง: หลังหยุด PostgreSQL ด้วย pg_ctl stop จน container db ถูก restart ข้อมูล 3 ออเดอร์และ stock ที่ลดลงยังอยู่ครบ</em>
</p>

**สรุปทดลองที่ 1:** kubelet restart เฉพาะ container `db` (RESTARTS ของ Pod เป็น 1 ซึ่งมาจาก `db`) ภายใน Pod เดิม IP เดิม ส่วน `web` ไม่ถูก restart และ **ข้อมูลรอด เพราะอยู่บน emptyDir ซึ่งมีอายุเท่ากับ Pod**

### 9.10 ทดลองที่ 2: ลบ Pod แล้วสร้างใหม่

🐧 **ใน SSH session ที่สอง**

```bash
kubectl get pod som-shop -o wide
time kubectl delete pod som-shop
sleep 10; kubectl get pods
```

```text
NAME       READY   STATUS    RESTARTS      AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-shop   2/2     Running   1 (21s ago)   53s   10.244.3.21   lab-worker2   <none>           <none>

pod "som-shop" deleted from default namespace

real	0m1.663s

No resources found in default namespace.
```

**ไม่มีใครสร้าง Pod คืนให้** แม้ผ่านไป 10 วินาที และถ้าดูที่หน้าต่าง port-forward (SSH session หลัก) จะเห็นว่ามันหลุดแล้ว (ผลจริงเมื่อมีการเชื่อมต่อเข้ามาหลัง Pod ถูกลบ — ในรอบทดลอง `curl localhost:3000/api/health` ได้คำตอบว่างเปล่า (curl exit code 52) แล้ว port-forward พิมพ์ข้อความนี้และจบการทำงาน)

```text
Handling connection for 3000
E1005 17:17:55.559596   23705 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod 845f47ee29e8c8c233e9dcd602f96df316ee98ec12ceecf93e6923c4ce5b0e87, uid : failed to find sandbox \"845f47ee29e8c8c233e9dcd602f96df316ee98ec12ceecf93e6923c4ce5b0e87\" in store: not found" localPort=3000 remotePort=3000
error: lost connection to pod
```

> **ข้อความก่อน `lost connection` อาจต่างกัน:** ขึ้นกับว่า Pod ถูกเก็บกวาดไปถึงขั้นไหนแล้วตอนที่มีการเชื่อมต่อเข้ามา ในรอบทดลองนี้ได้ `failed to find sandbox "<id>" in store: not found` (sandbox ถูกลบไปแล้ว) ส่วนในรอบทดลองก่อนหน้าได้ `network namespace for sandbox "<id>" is closed` (sandbox ยังอยู่แต่ network ปิดแล้ว) ทั้งสองแบบจบด้วย `error: lost connection to pod` เหมือนกัน ส่วน `<id>` และเวลาจะต่างในทุกเครื่อง

port-forward ผูกกับ Pod ตัวเดิม เมื่อ Pod ถูกลบจึงใช้ต่อไม่ได้ (ถ้า prompt ยังไม่กลับมา ให้กด Ctrl+C)

สร้าง Pod ใหม่จากไฟล์เดิม แล้วตรวจข้อมูล

```bash
kubectl apply -f som-shop/k8s/som-shop-pod.yaml
kubectl get pod som-shop -w
```

เมื่อเห็น `2/2 Running` แล้ว Ctrl+C

```bash
kubectl get pod som-shop -o wide
kubectl exec som-shop -c db -- psql -U som -d catshop -c 'SELECT count(*) AS orders FROM orders;' -c 'SELECT sku, stock FROM products ORDER BY id;'
kubectl logs som-shop -c db-seed
```

```text
NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-shop   2/2     Running   0          21s   10.244.3.22   lab-worker2   <none>           <none>

 orders 
--------
      0
(1 row)

      sku      | stock 
---------------+-------
 DRY-TUNA-15   |    20
 DRY-KITTEN-1  |    15
 DRY-SENIOR-12 |    10
 WET-SABA-85   |    60
 TRT-LICK-4    |    40
 TRT-SALMON-40 |    25
(6 rows)

connected to database
tables ready: products, orders
seeded 6 products (new: 6)
```

🐧 **ใน SSH session หลัก** รัน port-forward ใหม่ แล้ว 🌐 refresh browser

```bash
kubectl port-forward pod/som-shop 3000:3000
```

<p align="center" id="fig-20">
  <img src="images/screenshots/20261004_1815_lab9_04-after-pod-delete.png" alt="รูปที่ 20 ภาพหน้าจอจริง หลังลบ Pod แล้วสร้างใหม่" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: หลังลบ Pod แล้ว apply ใหม่ (และรัน port-forward ใหม่) ร้านกลับเป็น 0 ออเดอร์ และ stock กลับเป็นค่าตั้งต้น</em>
</p>

**สรุปทดลองที่ 2:** Pod ใหม่ได้ **IP ใหม่** (รอบทดลองนี้ `10.244.3.21` → `10.244.3.22` ของนักศึกษาจะเป็นเลขอื่น และอาจย้ายไปอีก node ด้วย), emptyDir ว่างเปล่า PostgreSQL จึงสร้างฐานข้อมูลใหม่ และ `db-seed` ใส่สินค้าใหม่ทั้ง 6 รายการ (`new: 6`) **ออเดอร์ทั้งหมดหายไป**

### 9.11 ทำไมงานจริงต้องแยก และบทหน้าจะทำอะไร

<p align="center" id="fig-21">
  <img src="images/16-lab9-next-split.png" alt="รูปที่ 21 บทหน้า: แยกเว็บกับฐานข้อมูล" width="900"><br>
  <em><b>รูปที่ 21</b> Pod เดียวรวมเว็บกับฐานข้อมูลเป็นการออกแบบเพื่อการเรียนรู้ บทหน้าจะแยก web เป็น Deployment, db ใช้ที่เก็บถาวร และเชื่อมกันด้วย Service</em>
</p>

| ปัญหาที่น้องส้มเจอใน LAB 9 | สิ่งที่บทถัดไปจะใช้ (ยังไม่ทำในบทนี้) |
|---|---|
| ลบ Pod แล้วไม่มีใครสร้างคืน ร้านปิด | **Deployment** สร้าง Pod ใหม่ให้อัตโนมัติ และ scale เว็บหลายตัวได้ |
| ข้อมูลออเดอร์หายเมื่อ Pod ใหม่ | **StatefulSet + PersistentVolumeClaim** สำหรับฐานข้อมูล |
| IP เปลี่ยนทุกครั้ง, port-forward หลุด, ต้อง ssh -L | **Service** ให้ชื่อและที่อยู่คงที่ และชนิด NodePort เปิดร้านผ่าน port 30080–30082 |
| รหัสผ่านอยู่ใน YAML | **Secret** |
| เว็บกับ DB scale/อัปเดตแยกกันไม่ได้ | แยกเป็นคนละ Pod คุยกันผ่าน Service แทน `localhost` |

### 9.12 เก็บกวาด LAB 9

1. 🐧 SSH session หลัก: Ctrl+C หยุด port-forward
2. 🖥️ หน้าต่าง `ssh -L 3000`: พิมพ์ `exit`
3. 🐧 SSH session หลัก:

```bash
kubectl delete -f som-shop/k8s/som-shop-pod.yaml
kubectl get pods
```

```text
pod "som-shop" deleted from default namespace
No resources found in default namespace.
```

### คำถามท้าย LAB 9

1. ทำไม `kubectl get pod som-shop` แสดง READY `2/2` ทั้งที่ Pod มี container ทั้งหมด 4 ตัว
2. ถ้าลบบรรทัด `restartPolicy: Always` ออกจาก `db` จะเกิดอะไรขึ้นกับ STATUS ของ Pod (คาดคะเนก่อน แล้วค่อยลองถ้ามีเวลา)
3. ทำไม `wget http://localhost:3000/api/health` ใน container `web` ล้มเหลว แต่ readinessProbe และ port-forward ใช้งานได้ปกติ
4. ตอน `pg_ctl stop` ทำไมข้อมูลยังอยู่ แต่ตอน `kubectl delete pod` ข้อมูลหาย ตอบโดยอ้างถึงอายุของ emptyDir
5. ถ้าแก้โค้ดเว็บแล้ว build เป็น `som-shop-web:1.1` ต้องทำขั้นตอนใดบ้างจึงจะเห็นเวอร์ชันใหม่ และข้อมูลออเดอร์จะเป็นอย่างไร

> **🏆 ท้าทาย:** เปลี่ยน env `SHOP_NAME` ใน manifest เป็นชื่อร้านของคุณเอง แล้วทำให้หน้าร้านแสดงชื่อใหม่ (คำใบ้: แก้ env ของ Pod ที่รันอยู่ไม่ได้)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 002_kubernetes_pod k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/002_kubernetes_pod/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (เช่น connection refused) | ยังไม่ได้รัน `k8s-up` หรือคลัสเตอร์ถูกลบ/หยุดไป | 🐧 รัน `k8s-up` ใหม่ (ถ้าเพิ่ง restart container `k8s-lab` คลัสเตอร์อาจต้องสร้างใหม่) |
| Pod `som-shop` ค้าง `Init:ErrImagePull` / `ImagePullBackOff` ที่ `db-seed` หรือ `web` | ลืม `kind load docker-image som-shop-web:1.0 --name lab` node จึงไปหา image บน Docker Hub ซึ่งไม่มี | 🐧 `kind load docker-image som-shop-web:1.0 --name lab` แล้ว `kubectl delete pod som-shop` และ `kubectl apply -f som-shop/k8s/som-shop-pod.yaml` |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform กับ containerd image store (ดู [9.3](#93-build-image-และนำเข้าคลัสเตอร์)) | ใช้ `docker save --platform linux/amd64 ... -o /tmp/pg.tar` + `kind load image-archive /tmp/pg.tar --name lab` (เครื่อง ARM ใช้ `linux/arm64`) |
| `ErrImagePull` ที่ Events มีคำว่า `toomanyrequests` / `429 Too Many Requests` | Docker Hub จำกัดจำนวนการดึงแบบไม่ล็อกอิน (ทั้งห้องใช้ IP เดียว) | รอสักพักแล้วลองใหม่ หรือ `docker pull` ล่วงหน้าแล้ว `kind load` (สำหรับ postgres ใช้วิธีใน 9.3) |
| `kubectl port-forward` แจ้งว่า listen ไม่ได้ มีคำว่า `address already in use` | port-forward ตัวเก่ายังรันอยู่ (เช่นลืม Ctrl+C จาก LAB 3) | หาและหยุดด้วย `pgrep -af "kubectl port-forward"` / `pkill -f "kubectl port-forward"` หรือใช้ port อื่น เช่น `kubectl port-forward pod/web 8081:80` (แล้วใช้ `-L 8081:localhost:8081`) |
| `ssh -L` แจ้งว่า bind port ไม่ได้ (`Address already in use` / `cannot listen to port`) หรือ browser เปิดแล้วเป็นเว็บอื่น | port 8080/3000 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ (เช่น dev server) | เปลี่ยนเลข **ซ้าย** ของ `-L` เช่น `ssh -p 2223 -L 13000:localhost:3000 root@localhost` แล้วเปิด `http://localhost:13000` |
| browser เปิดไม่ได้ (connection refused/ERR_CONNECTION_RESET) | หน้าต่าง `ssh -L` ถูกปิด หรือ port-forward หยุด/หลุด | ตรวจว่าทั้งสองหน้าต่างยังทำงาน ดูหน้าต่าง port-forward ว่ามี `Handling connection for ...` |
| port-forward ขึ้น `error: lost connection to pod` | Pod ถูกลบ/สร้างใหม่ port-forward ผูกกับ Pod เดิม | Ctrl+C แล้วรัน `kubectl port-forward ...` ใหม่ |
| หน้าเว็บ LAB 3 แสดงภาษาไทยเพี้ยน | nginx ไม่ส่ง charset | ใส่ `<meta charset=utf-8>` นำหน้าใน `index.html` |
| `kubectl delete` Pod ที่ใช้ busybox ค้างประมาณ 30 วินาที | `sh` เป็นโปรเซสหลัก ไม่ตอบ SIGTERM จึงรอ grace period 30 วินาที | รอ หรือใช้ `kubectl delete pod <ชื่อ> --now` |
| `wget http://localhost:3000/...` ใน container `web` ได้ `Connection refused` | `localhost` ถูก resolve เป็น `::1` แต่ Next.js ฟังเฉพาะ IPv4 | ใช้ `http://127.0.0.1:3000/...` (ดู [9.7](#97-ตรวจ-health-ภายใน-pod-และเรื่อง-localhost-กับ-ipv6)) |
| `kubectl logs crash-pod --previous` ได้ `unable to retrieve container logs for containerd://...` | สั่งตอน container เพิ่งจบ (`State: Terminated`) kubelet ลบ container รอบก่อนหน้าไปแล้ว | รอแล้วสั่งใหม่ตอน STATUS เป็น `CrashLoopBackOff` หรือ `Running` หรือใช้ `kubectl logs crash-pod` (ไม่ใส่ `--previous`) ซึ่งจะเห็น log ของรอบที่เพิ่งล้ม |
| ไม่เคยเห็น `CrashLoopBackOff` เห็นแต่ `Error` | บน K8s 1.37 STATUS สลับ `Error`/`CrashLoopBackOff` | ดู RESTARTS ที่เพิ่มขึ้นและ Events `BackOff` แทน |
| `liveness-exec-pod` ยังไม่ restart | ต้องรอ ~75 วินาที (ล้มที่ ~45 วิ + รอ kill 30 วิ) | รออย่างน้อย 90 วินาทีก่อนตรวจ |
| `pending-pod` ไม่ Pending แต่ Running | เครื่องมีมากกว่า 64 CPU thread | เพิ่มค่า `cpu` ใน `pending-pod.yaml` ให้เกินจำนวน CPU ของเครื่อง |
| `kubectl logs <pod>` / `exec` ได้ข้อมูลของ container ผิดตัว (มีข้อความ `Defaulted container ...`) | Pod มีหลาย container kubectl จึงเลือก container แรกให้ | ใส่ `-c <ชื่อ container>` |
| คำสั่ง `kubectl wait` timeout | image ใหญ่/เน็ตช้า | ดู `kubectl describe pod` ว่าติดขั้นไหน แล้วรอหรือแก้ตามสาเหตุ |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการต่อไปนี้ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 9 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes -o wide` เห็น 3 node `Ready` และ context `kind-lab`
- [ ] **LAB 1** `kubectl describe pod hello` ส่วน Events ครบ `Scheduled` → `Started`
- [ ] **LAB 2** ผล `pod/web unchanged`, `AlreadyExists` และ `Forbidden: pod updates may not change fields ...`
- [ ] **LAB 3** browser บนเครื่องนักศึกษาเปิด `http://localhost:8080` เห็น "สวัสดีจากน้องส้ม" และหน้าต่าง `kubectl logs -f web` ที่มี request จาก browser
- [ ] **LAB 4** ผล `kubectl get pods -l app=som-shop,tier=web` และ `-L app,tier`
- [ ] **LAB 5** `kubectl get pods` ที่เห็น `Completed`, `Error`/`CrashLoopBackOff` (RESTARTS > 0) และ `ErrImagePull`/`ImagePullBackOff` พร้อม `kubectl logs crash-pod --previous`
- [ ] **LAB 6** `OOMKilled` exit code 137 และ Events `FailedScheduling ... Insufficient cpu`
- [ ] **LAB 7** `kubectl get pods` ที่ `liveness-exec-pod` RESTARTS ≥ 1 และ `readiness-http-pod` READY `0/1` RESTARTS 0
- [ ] **LAB 8** `hostname -i` ของสอง container เท่ากัน และหลัง `nginx -s stop` ไฟล์ใน emptyDir ยังอยู่
- [ ] **LAB 9** (1) `kubectl get pod som-shop -o wide` เป็น `2/2 Running` (2) browser หน้าร้านหลังสั่งซื้อ (3) หลัง `pg_ctl stop` ออเดอร์ยังอยู่ และ `db restarts=1` (4) หลังลบ Pod และ apply ใหม่ ออเดอร์เป็น 0 และ IP เปลี่ยน
- [ ] ท้ายสุด `kubectl get pods` ได้ `No resources found in default namespace.`

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจว่าไม่มี Pod ค้างและไม่มี port-forward ค้าง

```bash
kubectl get pods
pgrep -af "kubectl port-forward" || echo "ไม่มี port-forward ค้าง"
```

```text
No resources found in default namespace.
ไม่มี port-forward ค้าง
```

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ `kind load` ใหม่) จากนั้นออกจาก SSH ด้วย `exit`

> **บทถัดไป:** น้องส้มจะแยกเว็บกับฐานข้อมูลออกจากกัน ให้ Deployment ดูแลการสร้าง Pod ใหม่ ใช้ Service ให้ที่อยู่คงที่ (และเปิดร้านผ่าน port 30080–30082 ได้โดยไม่ต้อง port-forward) เก็บข้อมูลบนที่เก็บถาวร และย้ายรหัสผ่านไปไว้ใน Secret
