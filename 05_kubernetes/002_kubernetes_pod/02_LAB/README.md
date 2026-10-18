# LAB บทที่ 2: Kubernetes Pod — จาก Pod แรกสู่ร้านอาหารแมวน้องส้ม

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Kubernetes Pod — `kubectl run`, YAML manifest, exec/logs/port-forward, labels, lifecycle, env/resources, probes, multi-container และแอป Next.js + PostgreSQL ใน Pod เดียว
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ทุก LAB ทำ **ใน container `k8s-lab`** (image `tuchsanai/devtools-kind:2569_1` มี kubectl, kind, helm, k9s และ Docker ข้างในครบ) โดยทำตามน้องส้มตั้งแต่สร้างคลัสเตอร์ สร้าง Pod แรก ดีบัก Pod ที่พัง จนถึงเปิด **"ร้านอาหารแมวน้องส้ม"** (Next.js + PostgreSQL) ใน Pod เดียว

> บล็อก **Expected output** คือผลที่ควรเห็นหลังรันคำสั่ง (ไม่ต้องพิมพ์ตาม) มาจากการทดลองจริงเมื่อ 5 ต.ค. 2569 (kind v0.33.0, kubectl v1.37.1, Kubernetes v1.37.0) ค่า AGE, IP, ชื่อ Pod ที่สุ่ม และ Node ในเครื่องนักศึกษาอาจต่างไป เป็นเรื่องปกติ

| สัญลักษณ์ | รันที่ไหน |
|---|---|
| 🖥️ | Terminal/PowerShell บนเครื่องนักศึกษา |
| 🐧 | SSH session ใน k8s-lab (prompt `root@k8s-lab`) |
| 🌐 | browser บนเครื่องนักศึกษา |

### กติกา

- ทำงานในโฟลเดอร์ `/workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB` และ **ลบ Pod ของตัวเองทุกครั้งที่จบ LAB**
- ใช้ **Pod เดี่ยว ๆ เท่านั้น** เข้าถึงแอปด้วย `kubectl exec`, `logs` และ `port-forward` + `ssh -L`
- รหัส `passwd` (SSH) และ `meow1234` (ฐานข้อมูล) เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมสภาพแวดล้อม (Setup)](#lab-0-เตรียมสภาพแวดล้อม-setup) (container `k8s-lab` + คลัสเตอร์ + git clone) | 20–30 นาที | ⭐ |
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
| 1 | [LAB 0 Setup container และคลัสเตอร์](#fig-1) | 13 | [LAB 8 multi-container](#fig-13) |
| 2 | [LAB 0 git clone](#fig-2) | 14 | [LAB 9 ร้านอาหารแมวน้องส้ม](#fig-14) |
| 3 | [LAB 1 kubectl run](#fig-3) | 15 | [สถาปัตยกรรม Pod som-shop](#fig-15) |
| 4 | [LAB 2 YAML แรก](#fig-4) | 16 | [ลำดับการเริ่ม Pod som-shop](#fig-16) |
| 5 | [LAB 3 exec/logs/port-forward](#fig-5) | 17 | [build และ kind load](#fig-17) |
| 6 | [LAB 3 attach VS Code เข้า k8s-lab](#fig-6) | 18 | [เปิดร้านจาก browser](#fig-18) |
| 7 | [LAB 3 เปิดเว็บผ่าน VS Code PORTS](#fig-7) | 19 | [ภาพหน้าจอจริง: หน้าร้านเริ่มต้น](#fig-19) |
| 8 | [ภาพหน้าจอจริง: หน้าเว็บ nginx ของ LAB 3](#fig-8) | 20 | [ภาพหน้าจอจริง: หลังสั่งซื้อ 3 ครั้ง](#fig-20) |
| 9 | [LAB 4 labels](#fig-9) | 21 | [emptyDir รอด vs หาย](#fig-21) |
| 10 | [LAB 5 lifecycle และดีบัก](#fig-10) | 22 | [ภาพหน้าจอจริง: หลัง restart db](#fig-22) |
| 11 | [LAB 6 env/command/resources](#fig-11) | 23 | [ภาพหน้าจอจริง: หลังลบ Pod แล้วสร้างใหม่](#fig-23) |
| 12 | [LAB 7 probes](#fig-12) | 24 | [บทหน้า: แยกเว็บกับฐานข้อมูล](#fig-24) |

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

## LAB 0: เตรียมสภาพแวดล้อม (Setup)

**เป้าหมาย:** สร้าง container `k8s-lab` และคลัสเตอร์ kind ชื่อ `lab` (1 control-plane + 2 worker) แล้วดึงไฟล์ LAB มาไว้ใน container (รายละเอียดของแต่ละคำสั่งดูได้จาก [LAB บทที่ 1](../../001_kubernetes-introduction/02_LAB/readme.md))

**ต้องมี:** Docker Desktop (Linux containers, RAM อย่างน้อย 4 GB) และ SSH client

### ขั้นที่ 1: Setup container และคลัสเตอร์

<p align="center" id="fig-1">
  <img src="images/01-lab0-setup.png" alt="รูปที่ 1 LAB0 Setup container และคลัสเตอร์" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0 ขั้นที่ 1: (1) docker run สร้าง container k8s-lab (2) ssh -p 2223 เข้าไปข้างใน (3) รัน k8s-up สร้าง kind cluster ชื่อ lab ได้ 3 node Ready (control-plane 1 ตัว + worker 2 ตัว)</em>
</p>

**1) สร้าง container** 🖥️ **บนเครื่องนักศึกษา** (image ประมาณ 1.5 GB ครั้งแรกใช้เวลาหลายนาที)

```bash
docker pull tuchsanai/devtools-kind:2569_1
docker run -dit --name k8s-lab --hostname k8s-lab --privileged -p 2223:22 -p 8889:8888 tuchsanai/devtools-kind:2569_1
```

- `--privileged` ให้รัน Docker ซ้อนใน container ได้ (kind ต้องใช้) **ขาดไม่ได้**
- `-p 2223:22` เปิดทาง SSH เข้า container ผ่าน port `2223`
- `-p 8889:8888` เปิด JupyterLab ที่ `http://localhost:8889/lab` ไว้เปิดดูไฟล์/terminal ข้างใน container เวลาดีบัก (ทางเลือก)

หลัง `docker run` **รอสัก 5–10 วินาที** ให้ container เริ่ม sshd และ dockerd ข้างในให้เสร็จก่อน (ตรวจได้ด้วย `docker ps --filter name=k8s-lab` ต้องเห็น `Up`) ถ้ามี `k8s-lab` จากบทที่ 1 อยู่แล้วใช้ `docker start k8s-lab` แทนได้

**2) SSH เข้า container** 🖥️ ครั้งแรกพิมพ์ `yes` แล้วใส่รหัสผ่าน `passwd`

```bash
ssh -p 2223 root@localhost
```

**3) สร้างและตรวจคลัสเตอร์** 🐧 **ใน SSH session ของ k8s-lab** (prompt `root@k8s-lab:~#`)

```bash
time k8s-up            # สร้างคลัสเตอร์ kind ชื่อ lab ใช้เวลาราว 1 นาที
kubectl get nodes      # ต้องเห็น 3 node Ready
kubectl get pods -A    # Pod ระบบใน kube-system ต้อง Running
```

**Expected output**

<pre>
...
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
...
real	0m48.440s

NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   23s   v1.37.0
lab-worker          Ready    &lt;none&gt;          13s   v1.37.0
lab-worker2         Ready    &lt;none&gt;          13s   v1.37.0
</pre>

> **✅ ผ่านเมื่อ:** node 3 ตัว `Ready` และ Pod ใน `kube-system` เป็น `Running` ทุกตัว (ช่วงแรกอาจยัง `0/1` รอสักครู่) ข้อความเรื่อง NodePort ท้าย `k8s-up` ข้ามได้ ปัญหาอื่นดู [Troubleshooting](#troubleshooting)

### ขั้นที่ 2: git clone ไฟล์ LAB

<p align="center" id="fig-2">
  <img src="images/01c-lab0-step3-git-clone.png" alt="รูปที่ 2 LAB0 ขั้นที่ 2 git clone และ cd" width="900"><br>
  <em><b>รูปที่ 2</b> LAB0 ขั้นที่ 2: git clone ดึง repo DevTools มาไว้ที่ /workspace/DevTools ใน k8s-lab แล้ว cd ลงไปจนถึงโฟลเดอร์ 02_LAB ที่มี labs และ som-shop</em>
</p>

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace
git clone https://github.com/Tuchsanai/DevTools.git     # เคย clone แล้ว: cd DevTools && git pull
cd DevTools/05_kubernetes/002_kubernetes_pod/02_LAB
```

> **✅ ผ่านเมื่อ:** prompt เป็น `root@k8s-lab:/workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB#` ทุกคำสั่งที่อ้าง `labs/...` หรือ `som-shop/...` ต้องรันจากโฟลเดอร์นี้

---

## LAB 1: Pod แรกด้วย kubectl run

<p align="center" id="fig-3">
  <img src="images/02-lab1-kubectl-run.png" alt="รูปที่ 3 LAB1 kubectl run" width="900"><br>
  <em><b>รูปที่ 3</b> LAB1: สร้าง Pod แรกด้วย kubectl run แล้วดูสถานะด้วย kubectl get pods -o wide</em>
</p>

**เป้าหมาย:** สร้าง ดู อธิบาย และลบ Pod แบบ imperative (สั่งตรง ๆ ไม่ใช้ไฟล์)

🐧 **ใน SSH session ของ k8s-lab** (ทุกขั้นใน LAB นี้)

### ขั้นที่ 1: สร้าง Pod แล้วดูสถานะ

**1.1 สร้าง Pod ชื่อ `hello` จาก image nginx**

```bash
kubectl run hello --image=nginx:1.27-alpine
```

**Expected output**

<pre>
pod/hello created
</pre>

**1.2 ดูรายการ Pod ทันที**

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME    READY   STATUS              RESTARTS   AGE
hello   0/1     ContainerCreating   0          0s
</pre>

STATUS ยังเป็น `ContainerCreating` และ READY `0/1` เพราะ Pod **ยังสร้างไม่เสร็จ** node กำลังดึง image จาก Docker Hub

**1.3 รอสัก 10 วินาที แล้วสั่ง `kubectl get pods` อีกครั้ง** (ถ้ายังไม่ `Running` ก็รอแล้วสั่งซ้ำ)

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME    READY   STATUS    RESTARTS   AGE
hello   1/1     Running   0          10s
</pre>

เมื่อเห็น `1/1` และ `Running` แปลว่า Pod พร้อมใช้งานแล้ว

### ขั้นที่ 2: ดูแบบละเอียดด้วย `-o wide`

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
hello   1/1     Running   0          10s   10.244.2.3   lab-worker2   &lt;none&gt;           &lt;none&gt;
</pre>

เทียบกับผลของ `kubectl get pods` ในขั้นที่ 1.3 จะเห็นว่า `-o wide` แสดง **คอลัมน์เพิ่ม** ขึ้นมา

| คำสั่ง | คอลัมน์ที่เห็น | ใช้เมื่อ |
|---|---|---|
| `kubectl get pods` | `NAME`, `READY`, `STATUS`, `RESTARTS`, `AGE` | อยากรู้แค่ว่า Pod พร้อมหรือยัง |
| `kubectl get pods -o wide` | ทุกคอลัมน์ข้างบน **+** `IP` (IP ของ Pod) และ `NODE` (Pod ไปอยู่บน node ไหน) | อยากรู้ว่า Pod อยู่ที่ไหน มี IP อะไร |

(IP และ NODE ของนักศึกษาอาจต่างจากนี้ เช่นได้ `lab-worker` แทน `lab-worker2`)

### ขั้นที่ 3: อ่านรายละเอียดด้วย describe

```bash
kubectl describe pod hello
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
Name:             hello
Namespace:        default
Node:             lab-worker2/172.19.0.3
Labels:           run=hello
Status:           Running
IP:               10.244.2.3
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
  Normal  Scheduled  10s   default-scheduler  Successfully assigned default/hello to lab-worker2
  Normal  Pulling    10s   kubelet            spec.containers{hello}: Pulling image "nginx:1.27-alpine"
  Normal  Pulled     2s    kubelet            spec.containers{hello}: Successfully pulled image "nginx:1.27-alpine" in 7.852s (7.852s including waiting). Image size: 20984244 bytes.
  Normal  Created    2s    kubelet            spec.containers{hello}: Container created
  Normal  Started    2s    kubelet            spec.containers{hello}: Container started
</pre>

### ขั้นที่ 4: ลบ Pod แล้วตรวจ

```bash
kubectl delete pod hello
kubectl get pods
```

**Expected output**

<pre>
pod "hello" deleted from default namespace
No resources found in default namespace.
</pre>

`No resources found` = ไม่มี Pod เหลือใน namespace `default` แล้ว

### สิ่งที่เห็น

- `kubectl run` สร้าง **Pod** (ไม่ใช่ container เดี่ยว) STATUS เปลี่ยนจาก `ContainerCreating` เป็น `Running` ภายในไม่กี่วินาที
- `get pods -o wide` บอกว่า Pod ได้ IP ช่วง `10.244.x.x` และถูกวางบน worker ตัวใดตัวหนึ่ง (ของนักศึกษาอาจเป็น `lab-worker`)
- Events เรียงตามเส้นทางการเกิดของ Pod: `Scheduled` → `Pulling` → `Pulled` → `Created` → `Started`
- `kubectl run` ติด label `run=hello` ให้อัตโนมัติ และ Pod ที่ไม่กำหนด resources มี QoS เป็น `BestEffort`
- เมื่อลบแล้ว **ไม่มีใครสร้างคืน** Pod หายถาวร

> **🤔 คำถามชวนคิด:** สร้าง `hello` ใหม่อีกครั้งแล้วดู IP และ NODE ได้ค่าเดิมหรือไม่ เพราะอะไร (อย่าลืมลบหลังทดลอง)

---

## LAB 2: Pod YAML แรก

<p align="center" id="fig-4">
  <img src="images/03-lab2-first-yaml.png" alt="รูปที่ 4 LAB2 YAML แรก" width="900"><br>
  <em><b>รูปที่ 4</b> LAB2: อ่านไฟล์ nginx-pod.yaml ที่เตรียมไว้ แล้ว kubectl apply -f สร้าง Pod web</em>
</p>

**เป้าหมาย:** สร้าง Pod จากไฟล์ YAML (แบบ declarative = เขียนสิ่งที่อยากได้ไว้ในไฟล์ แล้วให้ Kubernetes ทำตาม)

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB`)

### ขั้นที่ 1: เปิดดูไฟล์ YAML

```bash
cat labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
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
</pre>

อ่านความหมายของแต่ละบรรทัดได้จาก comment (`# ...`) ในไฟล์ สรุปสั้น ๆ คือ "ขอ Pod ชื่อ `web` ที่มี container `nginx` 1 ตัว"

### ขั้นที่ 2: สร้าง Pod จากไฟล์

```bash
kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
pod/web created
</pre>

`kubectl apply -f <ไฟล์>` = ส่งไฟล์ให้ Kubernetes สร้าง Pod ตามที่เขียนไว้ จากนั้นรอสัก 10 วินาทีแล้วดูสถานะ

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME   READY   STATUS    RESTARTS   AGE
web    1/1     Running   0          11s
</pre>

(ถ้ายังเป็น `ContainerCreating` ให้รอแล้วสั่งซ้ำ)

### ขั้นที่ 3: ดู Pod ในรูป YAML ที่ Kubernetes เก็บไว้

```bash
kubectl get pod web -o yaml
```

**Expected output** (ยาวกว่า 150 บรรทัด ตัดมาเฉพาะส่วนสำคัญ)

<pre>
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: web
    owner: nong-som
  name: web
  namespace: default
...
spec:
  containers:
  - image: nginx:1.27-alpine
    imagePullPolicy: IfNotPresent
    name: nginx
    ports:
    - containerPort: 80
      protocol: TCP
...
  nodeName: lab-worker2
  restartPolicy: Always
...
status:
...
  phase: Running
  podIP: 10.244.2.4
...
</pre>

- ส่วน `spec` คือ **สิ่งที่เราขอ** (จากไฟล์) และมีค่าที่ระบบเติมให้เอง เช่น `restartPolicy: Always`
- ส่วน `status` คือ **สถานะจริงตอนนี้** ที่ระบบเขียนให้ เช่น `phase: Running` และ IP ของ Pod

### ขั้นที่ 4: apply ซ้ำ เทียบกับ create ซ้ำ

```bash
kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
pod/web unchanged
</pre>

```bash
kubectl create -f labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
Error from server (AlreadyExists): error when creating "labs/lab02-first-yaml/nginx-pod.yaml": pods "web" already exists
</pre>

- `apply` ดูว่าไฟล์ต่างจากของที่มีอยู่ไหม ไม่ต่าง → `unchanged` (สั่งซ้ำได้เสมอ)
- `create` สร้างใหม่อย่างเดียว ถ้ามีชื่อนี้แล้ว → error `AlreadyExists`

### ขั้นที่ 5: ลบ Pod

```bash
kubectl delete -f labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
pod "web" deleted from default namespace
</pre>

```bash
kubectl get pods
```

**Expected output**

<pre>
No resources found in default namespace.
</pre>

### สิ่งที่เห็น

- ไฟล์ YAML บอก "สิ่งที่อยากได้" แล้ว `kubectl apply -f` ให้ Kubernetes สร้างตาม
- `get pod web -o yaml` มีทั้ง `spec` (สิ่งที่ขอ) และ `status` (สถานะจริง)
- `apply` สั่งซ้ำได้ (`unchanged`) แต่ `create` ซ้ำไม่ได้ (`AlreadyExists`)
- ลบด้วยไฟล์เดิมได้ด้วย `kubectl delete -f`

> **🏆 ท้าทาย:** คัดลอก `nginx-pod.yaml` เป็น `/tmp/my-pod.yaml` แก้ชื่อ Pod เป็น `my-web` แล้ว `kubectl apply -f /tmp/my-pod.yaml` ดูด้วย `kubectl get pods` แล้วลบทิ้ง

---

## LAB 3: เข้าไปใน Pod: exec, logs, port-forward

<p align="center" id="fig-5">
  <img src="images/04-lab3-exec-logs-portforward.png" alt="รูปที่ 5 LAB3 exec/logs/port-forward" width="900"><br>
  <em><b>รูปที่ 5</b> LAB3: เข้าไปใน Pod ด้วย exec แก้หน้าเว็บ ดู access log และเปิดเว็บผ่าน port-forward + แท็บ PORTS ของ VS Code</em>
</p>

**เป้าหมาย:** เข้าไปใน Pod แก้หน้าเว็บ แล้ว **เปิดเว็บใน Pod จาก browser บนเครื่องนักศึกษา** ผ่าน VS Code และดู log

**ต้องมี:** VS Code + extension **Container Tools** (หรือ Docker) และ **Dev Containers** ติดตั้งบนเครื่องนักศึกษา ทุกคำสั่งใน LAB นี้พิมพ์ใน **Terminal ของ VS Code** ที่ attach เข้า container k8s-lab

### ขั้นที่ 0: เปิด VS Code แล้ว attach เข้า container k8s-lab

<p align="center" id="fig-6">
  <img src="images/04a-lab3-vscode-attach.png" alt="รูปที่ 6 LAB3 attach VS Code เข้า container k8s-lab" width="900"><br>
  <em><b>รูปที่ 6</b> LAB3 ขั้นที่ 0 (ภาพจำลองหน้าจอ VS Code): ในแท็บ Containers คลิกขวาที่ k8s-lab แล้วเลือก Attach Visual Studio Code</em>
</p>

1. เปิด VS Code บนเครื่องนักศึกษา กดไอคอน **Containers** ที่แถบซ้าย
2. **คลิกขวา** ที่ container `k8s-lab` (image `tuchsanai/devtools-kind:2569_1`) แล้วเลือก **Attach Visual Studio Code**
3. VS Code จะเปิดหน้าต่างใหม่ มุมล่างซ้ายขึ้น `Container tuchsanai/devtools-kind:2569_1 (k8s-lab)` = ตอนนี้ทำงานอยู่ **ใน container** แล้ว
4. เมนู **File → Open Folder** เลือก `/workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB`
5. เมนู **Terminal → New Terminal** แล้วตรวจว่าใช้ kubectl ได้

```bash
kubectl get nodes
```

**Expected output**

<pre>
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   21m   v1.37.0
lab-worker          Ready    &lt;none&gt;          20m   v1.37.0
lab-worker2         Ready    &lt;none&gt;          20m   v1.37.0
</pre>

### ขั้นที่ 1: สร้าง Pod web

```bash
kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
pod/web created
</pre>

รอสัก 10 วินาทีแล้วตรวจว่า `Running`

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME   READY   STATUS    RESTARTS   AGE
web    1/1     Running   0          11s
</pre>

### ขั้นที่ 2: เข้าไปใน Pod แล้วแก้หน้าเว็บ

```bash
kubectl exec -it web -- sh
```

prompt จะเปลี่ยนเป็น `/ #` แปลว่าตอนนี้อยู่ **ใน container ของ Pod** แล้ว (image นี้เป็น Alpine จึงใช้ `sh` ไม่มี `bash`) พิมพ์ทีละบรรทัด

```bash
ls /usr/share/nginx/html
echo '<meta charset=utf-8><h1>สวัสดีจากน้องส้ม 🐱</h1>' > /usr/share/nginx/html/index.html
cat /usr/share/nginx/html/index.html
exit
```

**Expected output**

<pre>
50x.html
index.html
&lt;meta charset=utf-8&gt;&lt;h1&gt;สวัสดีจากน้องส้ม 🐱&lt;/h1&gt;
</pre>

- `ls` เห็นไฟล์หน้าเว็บของ nginx ส่วน `echo ... >` เขียนทับ `index.html` ด้วยข้อความของเรา
- `<meta charset=utf-8>` ช่วยให้ภาษาไทยแสดงถูกใน browser
- `exit` ออกจาก Pod กลับมาที่ prompt `root@k8s-lab`

### ขั้นที่ 3: เปิดทางเข้าเว็บด้วย port-forward

```bash
kubectl port-forward pod/web 8080:80
```

**Expected output**

<pre>
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
</pre>

คำสั่งนี้ **ค้างไว้** (อย่าปิด) มันส่งต่อ port `8080` ของ k8s-lab เข้าไปที่ port `80` ของ Pod `web`

### ขั้นที่ 4: เปิดเว็บจาก VS Code

<p align="center" id="fig-7">
  <img src="images/04b-lab3-vscode-ports.png" alt="รูปที่ 7 LAB3 เปิดเว็บผ่านแท็บ PORTS ของ VS Code" width="900"><br>
  <em><b>รูปที่ 7</b> LAB3 ขั้นที่ 4 (ภาพจำลองหน้าจอ VS Code ที่ attach เข้า k8s-lab แล้ว): แท็บ PORTS แสดง port 8080 ที่ VS Code ส่งต่อมาให้อัตโนมัติ (Auto Forwarded) ชี้ที่แถวนั้นแล้วกดไอคอนลูกโลก Open in Browser</em>
</p>

1. ใน VS Code เปิดแท็บ **PORTS** (แถบเดียวกับ TERMINAL ด้านล่าง)
2. จะเห็นแถว port **8080** ที่ VS Code ส่งต่อมาให้อัตโนมัติ (ถ้าไม่เห็น กด **Forward a Port** แล้วพิมพ์ `8080`)
3. ชี้ที่แถวนั้นแล้วกดไอคอน **ลูกโลก (Open in Browser)**

🌐 browser จะเปิด `http://localhost:8080` และเห็นหัวข้อ "สวัสดีจากน้องส้ม 🐱"

<p align="center" id="fig-8">
  <img src="images/screenshots/20261005_1725_lab002_02-lab3-nginx.png" alt="รูปที่ 8 ภาพหน้าจอจริง หน้าเว็บ nginx สวัสดีจากน้องส้ม" width="700"><br>
  <em><b>รูปที่ 8</b> ภาพหน้าจอจริงจากการทดลอง: หน้าเว็บของ Pod web หลังแก้ index.html แสดงหัวข้อ "สวัสดีจากน้องส้ม 🐱"</em>
</p>

ทุกครั้งที่เปิดหรือ refresh หน้าเว็บ หน้าต่าง port-forward จะพิมพ์ `Handling connection for 8080`

### ขั้นที่ 5: ดู log ของ Pod

เปิด **Terminal ใหม่** ใน VS Code (กด `+` ที่แท็บ TERMINAL) เพราะ terminal แรกยังรัน port-forward อยู่

```bash
kubectl logs web
```

**Expected output** (บรรทัดท้าย ๆ)

<pre>
...
2026/10/18 00:20:45 [notice] 1#1: start worker process 65
127.0.0.1 - - [18/Oct/2026:00:20:58 +0000] "GET / HTTP/1.1" 200 83 "-" "Mozilla/5.0 ..." "-"
</pre>

บรรทัด `GET / ... 200` คือการเปิดหน้าเว็บจาก browser เมื่อสักครู่ (refresh browser แล้วสั่งซ้ำจะเห็นบรรทัดเพิ่ม)

### ขั้นที่ 6: ปิดและลบ Pod

กลับไปที่ terminal แรกแล้วกด **Ctrl+C** เพื่อหยุด port-forward จากนั้น

```bash
kubectl delete -f labs/lab02-first-yaml/nginx-pod.yaml
```

**Expected output**

<pre>
pod "web" deleted from default namespace
</pre>

### สิ่งที่เห็น

- `kubectl exec -it <pod> -- sh` พาเข้าไปใน container เหมือนอยู่ในเครื่องนั้น การแก้ไฟล์แบบนี้ **ชั่วคราว** ถ้าลบ Pod ไฟล์จะหาย
- `kubectl port-forward` เปิดทางจาก k8s-lab เข้า Pod แล้ว VS Code (ที่ attach เข้า container) ส่งต่อ port นั้นมาที่เครื่องนักศึกษาให้เอง
- `kubectl logs` ดูสิ่งที่แอปใน Pod พิมพ์ออกมา (สำหรับ nginx คือ log ของทุก request)

> **🤔 คำถามชวนคิด:** ถ้ากด Ctrl+C หยุด port-forward แล้ว refresh browser จะเกิดอะไรขึ้น เพราะอะไร

---

## LAB 4: Labels และ Selectors

<p align="center" id="fig-9">
  <img src="images/05-lab4-labels.png" alt="รูปที่ 9 LAB4 labels" width="900"><br>
  <em><b>รูปที่ 9</b> LAB4: ติดป้าย label ให้ Pod 3 ตัวและใช้ -l เลือกเฉพาะกลุ่มที่ต้องการ</em>
</p>

**เป้าหมาย:** ติดป้าย (label) ให้ Pod แล้วใช้ป้ายนั้นเลือกเฉพาะ Pod ที่ต้องการ

**label** คือป้าย `key=value` ที่แปะไว้กับ Pod เช่น `app=som-shop` เอาไว้จัดกลุ่มและค้นหา ไฟล์ `labs/lab04-labels/shop-pods.yaml` มี 3 Pod (คั่นแต่ละตัวด้วย `---`)

| Pod | labels |
|---|---|
| `shop-web` | `app=som-shop`, `tier=web` |
| `shop-cache` | `app=som-shop`, `tier=cache` |
| `toy-web` | `app=toy-shop`, `tier=web` |

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: สร้าง Pod ทั้ง 3 ตัว แล้วดู label

```bash
kubectl apply -f labs/lab04-labels/shop-pods.yaml
```

**Expected output**

<pre>
pod/shop-web created
pod/shop-cache created
pod/toy-web created
</pre>

ไฟล์เดียวสร้างได้ 3 Pod รอสัก 10 วินาทีแล้วดู label ด้วย `--show-labels`

```bash
kubectl get pods --show-labels
```

**Expected output**

<pre>
NAME         READY   STATUS    RESTARTS   AGE   LABELS
shop-cache   1/1     Running   0          11s   app=som-shop,tier=cache
shop-web     1/1     Running   0          11s   app=som-shop,tier=web
toy-web      1/1     Running   0          11s   app=toy-shop,tier=web
</pre>

### ขั้นที่ 2: เลือก Pod ด้วย label (`-l`)

**2.1 เฉพาะร้านน้องส้ม**

```bash
kubectl get pods -l app=som-shop
```

**Expected output**

<pre>
NAME         READY   STATUS    RESTARTS   AGE
shop-cache   1/1     Running   0          11s
shop-web     1/1     Running   0          11s
</pre>

**2.2 เฉพาะ Pod ที่เป็นหน้าเว็บ (ทุกร้าน)**

```bash
kubectl get pods -l tier=web
```

**Expected output**

<pre>
NAME       READY   STATUS    RESTARTS   AGE
shop-web   1/1     Running   0          11s
toy-web    1/1     Running   0          11s
</pre>

**2.3 ต้องตรงทั้งสองป้าย (ร้านน้องส้ม **และ** หน้าเว็บ)**

```bash
kubectl get pods -l app=som-shop,tier=web
```

**Expected output**

<pre>
NAME       READY   STATUS    RESTARTS   AGE
shop-web   1/1     Running   0          11s
</pre>

เครื่องหมาย `,` แปลว่า "และ" จึงเหลือ Pod เดียว

### ขั้นที่ 3: ติดป้ายเพิ่ม แล้วถอดออก

```bash
kubectl label pod toy-web env=dev
```

**Expected output**

<pre>
pod/toy-web labeled
</pre>

```bash
kubectl get pods --show-labels
```

**Expected output**

<pre>
NAME         READY   STATUS    RESTARTS   AGE   LABELS
shop-cache   1/1     Running   0          11s   app=som-shop,tier=cache
shop-web     1/1     Running   0          11s   app=som-shop,tier=web
toy-web      1/1     Running   0          11s   app=toy-shop,env=dev,tier=web
</pre>

`toy-web` มีป้าย `env=dev` เพิ่มขึ้นมา ถอดป้ายออกด้วยการใส่ `-` ต่อท้ายชื่อ key

```bash
kubectl label pod toy-web env-
```

**Expected output**

<pre>
pod/toy-web unlabeled
</pre>

### ขั้นที่ 4: ลบเป็นกลุ่มด้วย label

```bash
kubectl delete pod -l app=som-shop
```

**Expected output**

<pre>
pod "shop-cache" deleted from default namespace
pod "shop-web" deleted from default namespace
</pre>

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME      READY   STATUS    RESTARTS   AGE
toy-web   1/1     Running   0          42s
</pre>

Pod ของร้านน้องส้มหายไปทั้งคู่ในคำสั่งเดียว เหลือแค่ `toy-web` (ใช้อย่างระวัง!) ลบตัวที่เหลือ

```bash
kubectl delete pod toy-web
```

**Expected output**

<pre>
pod "toy-web" deleted from default namespace
</pre>

### สิ่งที่เห็น

- label คือป้าย `key=value` บน Pod ดูได้ด้วย `--show-labels`
- `-l key=value` เลือกเฉพาะ Pod ที่มีป้ายนั้น ใส่หลายป้ายคั่นด้วย `,` = ต้องตรงทุกป้าย
- `kubectl label pod <ชื่อ> key=value` ติดป้าย, `key-` ถอดป้าย
- `kubectl delete pod -l ...` ลบทุก Pod ที่ตรงป้ายในครั้งเดียว

> **🏆 ท้าทาย:** ลอง `kubectl get pods -A -l k8s-app` ดู Pod ระบบที่มีป้าย key `k8s-app` แล้วอธิบายว่าเป็น Pod อะไร

---

## LAB 5: Lifecycle และการดีบัก Pod ที่พัง

<p align="center" id="fig-10">
  <img src="images/06-lab5-lifecycle-debug.png" alt="รูปที่ 10 LAB5 lifecycle และดีบัก" width="900"><br>
  <em><b>รูปที่ 10</b> LAB5: สังเกต Completed, CrashLoopBackOff และ ImagePullBackOff แล้วใช้ describe กับ logs หาสาเหตุ</em>
</p>

**เป้าหมาย:** ดู STATUS ของ Pod แบบต่าง ๆ แล้วหาสาเหตุ Pod ที่พังด้วยคำสั่งพื้นฐาน 2 ตัว คือ `kubectl describe` กับ `kubectl logs`

ในโฟลเดอร์ `labs/lab05-lifecycle/` มี 4 Pod แต่ละตัวจงใจให้จบต่างกัน

- `completed-pod` ทำงานเสร็จแล้วจบ
- `crash-pod` ล้มทุกครั้ง
- `onfailure-pod` ล้มรอบแรก สำเร็จรอบสอง
- `bad-image-pod` ระบุ image ผิด

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: สร้าง Pod ทั้ง 4 ตัว

ใส่ชื่อ **โฟลเดอร์** แทนชื่อไฟล์ kubectl จะ apply ทุกไฟล์ในโฟลเดอร์ให้

```bash
kubectl apply -f labs/lab05-lifecycle/
```

**Expected output**

<pre>
pod/bad-image-pod created
pod/completed-pod created
pod/crash-pod created
pod/onfailure-pod created
</pre>

### ขั้นที่ 2: รอ 20 วินาที แล้วดูสถานะ

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME            READY   STATUS             RESTARTS      AGE
bad-image-pod   0/1     ImagePullBackOff   0             20s
completed-pod   0/1     Completed          0             20s
crash-pod       0/1     Error              1 (7s ago)    20s
onfailure-pod   0/1     Completed          1 (11s ago)   20s
</pre>

แต่ละ Pod จบไม่เหมือนกัน ขั้นต่อไปจะดูทีละตัวว่าเพราะอะไร (STATUS ของ `crash-pod` อาจเป็น `Error`, `CrashLoopBackOff` หรือ `Running` สลับกันไป และ `bad-image-pod` อาจเป็น `ErrImagePull` ก็ได้ ขึ้นกับจังหวะที่สั่ง)

### ขั้นที่ 3: completed-pod — งานเสร็จแล้วจบ

```yaml
# completed-pod.yaml (ส่วนสำคัญ)
spec:
  restartPolicy: Never    # จบแล้วไม่ต้องเริ่มใหม่
  containers:
    - name: job
      image: busybox:1.36
      command: ["sh", "-c", "echo 'น้องส้มนับสต็อกเสร็จแล้ว'; exit 0"]
```

```bash
kubectl logs completed-pod
```

**Expected output**

<pre>
น้องส้มนับสต็อกเสร็จแล้ว
</pre>

พิมพ์ข้อความแล้วจบด้วย `exit 0` (สำเร็จ) และ `restartPolicy: Never` จึงไม่เริ่มใหม่ STATUS เป็น `Completed`

### ขั้นที่ 4: crash-pod — ล้มวนไม่จบ

```yaml
# crash-pod.yaml (ส่วนสำคัญ)
spec:
  restartPolicy: Always   # ล้มเมื่อไรก็เริ่มใหม่
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "echo 'กำลังเปิดร้าน...'; sleep 3; echo 'ERROR: หาไฟล์เมนูไม่เจอ' >&2; exit 1"]
```

**4.1 ดู log ว่าแอปพูดอะไรก่อนล้ม**

```bash
kubectl logs crash-pod
```

**Expected output**

<pre>
กำลังเปิดร้าน...
ERROR: หาไฟล์เมนูไม่เจอ
</pre>

**4.2 ดูรายละเอียดด้วย describe**

```bash
kubectl describe pod crash-pod
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
...
    State:          Terminated
      Reason:       Error
      Exit Code:    1
...
    Restart Count:  2
...
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
...
  Normal   Started    15s (x3 over 35s)  kubelet            spec.containers{app}: Container started
  Warning  BackOff    11s (x2 over 27s)  kubelet            spec.containers{app}: Back-off restarting failed container app in pod crash-pod_default(...)
</pre>

- log บอกสาเหตุ: แอปหาไฟล์เมนูไม่เจอ แล้วจบด้วย `Exit Code: 1` (ล้ม)
- `restartPolicy: Always` ทำให้ Kubernetes เริ่มใหม่เรื่อย ๆ `Restart Count` จึงเพิ่มขึ้น และรอนานขึ้นทุกรอบ (`Back-off`) อาการนี้เรียกว่า **CrashLoopBackOff**
- สั่ง `kubectl get pods` ซ้ำอีกสักพัก จะเห็น RESTARTS ของ `crash-pod` เพิ่มขึ้นเรื่อย ๆ

### ขั้นที่ 5: onfailure-pod — ล้มรอบแรก สำเร็จรอบสอง

```yaml
# onfailure-pod.yaml (ส่วนสำคัญ)
spec:
  restartPolicy: OnFailure   # เริ่มใหม่เฉพาะตอนล้ม (exit ไม่ใช่ 0)
  containers:
    - name: app
      image: busybox:1.36
      # รอบแรกยังไม่มีไฟล์ /work/tried → สร้างไฟล์แล้ว exit 1 / รอบสองเจอไฟล์ → exit 0
      command: ["sh", "-c", "if [ -f /work/tried ]; then echo 'รอบสองสำเร็จ'; exit 0; else touch /work/tried; echo 'รอบแรกล้ม'; exit 1; fi"]
```

(ไฟล์จริงมี `volumes` ชื่อ `work` เพิ่ม เพื่อให้ไฟล์ `/work/tried` อยู่รอดข้ามการเริ่มใหม่ จะเรียนใน LAB 8)

```bash
kubectl logs onfailure-pod
```

**Expected output**

<pre>
รอบสองสำเร็จ
</pre>

ในขั้นที่ 2 เห็น RESTARTS = `1` และ STATUS `Completed` = ล้ม 1 ครั้ง เริ่มใหม่ แล้วสำเร็จจึงหยุด

### ขั้นที่ 6: bad-image-pod — image ผิด แล้วแก้

```yaml
# bad-image-pod.yaml (ส่วนสำคัญ)
spec:
  containers:
    - name: web
      image: nginx:9.99-doesnotexist   # tag ผิด! ไม่มีอยู่จริง
```

**6.1 หาสาเหตุจาก Events**

```bash
kubectl describe pod bad-image-pod
```

**Expected output** (ส่วน Events ท้ายสุด)

<pre>
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
...
  Warning  Failed     1s (x3 over 43s)   kubelet            spec.containers{web}: Failed to pull image "nginx:9.99-doesnotexist": ... docker.io/library/nginx:9.99-doesnotexist: not found
  Warning  Failed     1s (x3 over 43s)   kubelet            spec.containers{web}: Error: ErrImagePull
</pre>

คำว่า `not found` บอกว่าหา image `nginx:9.99-doesnotexist` ไม่เจอ (tag ผิด)

**6.2 แก้ image เป็นตัวที่ถูก**

```bash
kubectl set image pod/bad-image-pod web=nginx:1.27-alpine
```

**Expected output**

<pre>
pod/bad-image-pod image updated
</pre>

`web=` คือชื่อ container ใน Pod รอสัก 10 วินาทีแล้วดูอีกครั้ง

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME            READY   STATUS      RESTARTS      AGE
bad-image-pod   1/1     Running     0             55s
completed-pod   0/1     Completed   0             55s
crash-pod       1/1     Running     3 (22s ago)   55s
onfailure-pod   0/1     Completed   1 (46s ago)   55s
</pre>

`bad-image-pod` เป็น `Running` แล้ว ส่วน `crash-pod` ยังล้มวนอยู่ (RESTARTS เพิ่มเป็น 3)

### ขั้นที่ 7: ลบทั้งหมด

```bash
kubectl delete -f labs/lab05-lifecycle/
```

**Expected output**

<pre>
pod "bad-image-pod" deleted from default namespace
pod "completed-pod" deleted from default namespace
pod "crash-pod" deleted from default namespace
pod "onfailure-pod" deleted from default namespace
</pre>

### สิ่งที่เห็น

- `Completed` = ทำงานเสร็จ (exit 0) / `Error`, `CrashLoopBackOff` = ล้มแล้วถูกเริ่มใหม่วนไป / `ErrImagePull`, `ImagePullBackOff` = ดึง image ไม่ได้
- `restartPolicy` กำหนดว่าจะเริ่มใหม่เมื่อไร: `Always` ทุกครั้ง, `OnFailure` เฉพาะตอนล้ม, `Never` ไม่เริ่มใหม่
- Pod พัง ให้เริ่มจาก 2 คำสั่งนี้: `kubectl logs <pod>` (แอปพูดอะไร) และ `kubectl describe pod <pod>` (ดู `State`, `Exit Code` และ `Events`)

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `crash-pod` เป็น `restartPolicy: Never` คาดว่า STATUS และ RESTARTS จะเป็นอย่างไร (ลองทำแล้วตรวจคำตอบ อย่าลืมลบ Pod)

---

## LAB 6: env, command และ resources

<p align="center" id="fig-11">
  <img src="images/07-lab6-env-command-resources.png" alt="รูปที่ 11 LAB6 env/command/resources" width="900"><br>
  <em><b>รูปที่ 11</b> LAB6: ส่ง env และ command เข้า container ทดลอง memory limit จนเกิด OOMKilled และ request CPU เกินจน Pending</em>
</p>

**เป้าหมาย:** ส่งค่าเข้า container ด้วย `env` และดูว่าเกิดอะไรเมื่อใช้ memory เกินเพดาน (OOMKilled) หรือขอ CPU มากเกินไป (Pending)

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: ส่งค่าเข้า container ด้วย env

```yaml
# env-command-pod.yaml (ส่วนสำคัญ)
      env:                              # ตัวแปรที่ส่งเข้า container
        - name: SHOP_NAME
          value: "ร้านอาหารแมวน้องส้ม"
        - name: OPEN_HOUR
          value: "9"                    # ตัวเลขต้องใส่ "" เสมอ
      command: ["sh", "-c"]             # คำสั่งที่ใช้แทนคำสั่งเดิมของ image
      args:
        - echo "SHOP_NAME=$SHOP_NAME"; echo "OPEN_HOUR=$OPEN_HOUR"; sleep 3600
      resources:
        requests:                       # ขอจองไว้ (scheduler ใช้เลือก node)
          cpu: "50m"                    # 50m = 0.05 core
          memory: "32Mi"
        limits:                         # เพดานสูงสุดที่ใช้ได้
          cpu: "100m"
          memory: "64Mi"
```

```bash
kubectl apply -f labs/lab06-env-resources/env-command-pod.yaml
```

**Expected output**

<pre>
pod/env-command-pod created
</pre>

รอสัก 10 วินาทีแล้วดูว่าแอปพิมพ์อะไรออกมา

```bash
kubectl logs env-command-pod
```

**Expected output**

<pre>
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9
</pre>

ค่าใน `env` ถูกส่งเข้าไปให้แอปใช้ได้จริง ลองดูตัวแปรทั้งหมดใน container

```bash
kubectl exec env-command-pod -- env
```

**Expected output** (ตัดบางบรรทัด)

<pre>
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOSTNAME=env-command-pod
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9
...
</pre>

นอกจากค่าที่เราใส่ ยังมี `HOSTNAME` ซึ่ง Kubernetes ตั้งให้เป็นชื่อ Pod อัตโนมัติ

### ขั้นที่ 2: ดู requests และ limits

```bash
kubectl describe pod env-command-pod
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
...
    Limits:
      cpu:     100m
      memory:  64Mi
    Requests:
      cpu:     50m
      memory:  32Mi
...
QoS Class:                   Burstable
...
</pre>

- **Requests** = ปริมาณที่ขอจองไว้ **Limits** = เพดานที่ใช้ได้สูงสุด
- requests น้อยกว่า limits จึงได้ QoS Class `Burstable`

### ขั้นที่ 3: ใช้ memory เกินเพดาน → OOMKilled

```yaml
# oom-pod.yaml (ส่วนสำคัญ)
      command: ["sh", "-c", "echo 'กินแรมไม่หยุด...'; tail /dev/zero"]   # กิน RAM ไปเรื่อย ๆ
      resources:
        limits:
          memory: "32Mi"                # เกิน 32Mi เมื่อไร โดนฆ่า
```

```bash
kubectl apply -f labs/lab06-env-resources/oom-pod.yaml
```

**Expected output**

<pre>
pod/oom-pod created
</pre>

รอสัก 10 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME              READY   STATUS             RESTARTS     AGE
env-command-pod   1/1     Running            0            20s
oom-pod           0/1     CrashLoopBackOff   1 (8s ago)   10s
</pre>

STATUS ของ `oom-pod` จะสลับระหว่าง `OOMKilled` กับ `CrashLoopBackOff` ดูสาเหตุด้วย describe

```bash
kubectl describe pod oom-pod
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
...
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
...
    Restart Count:  1
...
</pre>

`OOMKilled` = ใช้ memory เกิน limit จึงถูกระบบฆ่าทิ้ง (Exit Code `137`) แล้วถูกเริ่มใหม่วนไป

### ขั้นที่ 4: ขอ CPU มากเกินไป → Pending

```yaml
# pending-pod.yaml (ส่วนสำคัญ)
      resources:
        requests:
          cpu: "64"                     # ขอ 64 core! ไม่มี node ไหนมีพอ
```

```bash
kubectl apply -f labs/lab06-env-resources/pending-pod.yaml
```

**Expected output**

<pre>
pod/pending-pod created
</pre>

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME              READY   STATUS      RESTARTS      AGE
env-command-pod   1/1     Running     0             25s
oom-pod           0/1     OOMKilled   2 (13s ago)   15s
pending-pod       0/1     Pending     0             5s
</pre>

`pending-pod` ค้างที่ `Pending` ไม่ว่ารอนานแค่ไหน ดูเหตุผลใน Events

```bash
kubectl describe pod pending-pod
```

**Expected output** (ส่วน Events ท้ายสุด)

<pre>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  5s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. ...
</pre>

`Insufficient cpu` = ไม่มี worker ตัวไหนมี CPU พอ ส่วน `untolerated taint` คือ control-plane ที่ห้ามวาง Pod ทั่วไป Pod จึงไม่ได้ไปอยู่ node ไหนเลย

### ขั้นที่ 5: ลบทั้งหมด

```bash
kubectl delete -f labs/lab06-env-resources/
```

**Expected output**

<pre>
pod "env-command-pod" deleted from default namespace
pod "oom-pod" deleted from default namespace
pod "pending-pod" deleted from default namespace
</pre>

### สิ่งที่เห็น

- `env` ส่งค่า (ภาษาไทยได้) เข้า container ตัวเลขต้องใส่ `""` เสมอ
- **requests** = ขอจอง (ใช้ตอนเลือก node) / **limits** = เพดานขณะรัน
- memory เกิน limit → `OOMKilled` (Exit Code 137) แล้วถูกเริ่มใหม่วนไป
- ขอ CPU เกินที่ node มี → `Pending` ตลอด ดูเหตุผลที่ Events ของ `describe`

> **🏆 ท้าทาย:** คัดลอก `env-command-pod.yaml` แล้วแก้ requests ให้เท่ากับ limits (`cpu: 100m`, `memory: 64Mi`) apply แล้วดูด้วย `kubectl describe` ว่า QoS Class เปลี่ยนเป็นอะไร

---

## LAB 7: Probes ตรวจสุขภาพ

<p align="center" id="fig-12">
  <img src="images/08-lab7-probes.png" alt="รูปที่ 12 LAB7 probes" width="900"><br>
  <em><b>รูปที่ 12</b> LAB7: liveness ล้มแล้ว container ถูก restart ส่วน readiness ล้มแล้ว Pod เป็น READY 0/1 โดยไม่ถูก restart</em>
</p>

**เป้าหมาย:** เห็นความต่างของ probe 2 แบบด้วยตาตัวเอง

- **readiness** ไม่ผ่าน → Pod แค่ "ยังไม่พร้อม" (READY `0/1`) **ไม่ถูกเริ่มใหม่**
- **liveness** ไม่ผ่าน → container ถูก **ฆ่าแล้วเริ่มใหม่** (RESTARTS เพิ่ม)

🐧 **ใน SSH session ของ k8s-lab**

### ขั้นที่ 1: readiness — พร้อมหรือยัง

```yaml
# readiness-http-pod.yaml (ส่วนสำคัญ)
      readinessProbe:
        httpGet:                 # เปิดหน้าเว็บนี้ ได้ 200 = พร้อม, 404 = ไม่พร้อม
          path: /ready.html      # ตอนแรกยังไม่มีไฟล์นี้
          port: 80
        periodSeconds: 3         # ตรวจทุก 3 วินาที
```

**1.1 สร้าง Pod**

```bash
kubectl apply -f labs/lab07-probes/readiness-http-pod.yaml
```

**Expected output**

<pre>
pod/readiness-http-pod created
</pre>

รอสัก 10 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME                 READY   STATUS    RESTARTS   AGE
readiness-http-pod   0/1     Running   0          10s
</pre>

STATUS เป็น `Running` แต่ READY `0/1` = container ทำงานอยู่ แต่ **ยังไม่พร้อม** ดูเหตุผล

```bash
kubectl describe pod readiness-http-pod
```

**Expected output** (ส่วน Events ท้ายสุด)

<pre>
Events:
...
  Warning  Unhealthy  0s (x4 over 9s)  kubelet            spec.containers{web}: Readiness probe failed: HTTP probe failed with statuscode: 404
</pre>

probe เปิด `/ready.html` แล้วได้ `404` (ไม่มีไฟล์) จึงถือว่ายังไม่พร้อม

**1.2 สร้างไฟล์ให้ probe ผ่าน**

```bash
kubectl exec readiness-http-pod -- touch /usr/share/nginx/html/ready.html
```

คำสั่งนี้ไม่มี output รอสัก 5 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME                 READY   STATUS    RESTARTS   AGE
readiness-http-pod   1/1     Running   0          15s
</pre>

**1.3 ลบไฟล์ทิ้ง**

```bash
kubectl exec readiness-http-pod -- rm /usr/share/nginx/html/ready.html
```

รอสัก 5 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME                 READY   STATUS    RESTARTS   AGE
readiness-http-pod   0/1     Running   0          20s
</pre>

READY กลับเป็น `0/1` แต่ RESTARTS ยังเป็น `0` = readiness ไม่เคยทำให้ container ถูกเริ่มใหม่

### ขั้นที่ 2: liveness — ยังมีชีวิตอยู่ไหม

```yaml
# liveness-exec-pod.yaml (ส่วนสำคัญ)
      # สร้างไฟล์ /tmp/healthy → ผ่านไป 30 วินาทีลบทิ้ง (จำลองแอปค้าง)
      command: ["sh", "-c", "touch /tmp/healthy; echo 'สบายดี'; sleep 30; rm -f /tmp/healthy; echo 'ไม่สบายแล้ว'; sleep 600"]
      livenessProbe:
        exec:
          command: ["cat", "/tmp/healthy"]   # อ่านไฟล์ได้ = ยังมีชีวิต
        initialDelaySeconds: 5               # รอ 5 วินาทีก่อนตรวจครั้งแรก
        periodSeconds: 5                     # ตรวจทุก 5 วินาที
        failureThreshold: 3                  # ไม่ผ่าน 3 ครั้งติด → เริ่มใหม่
```

**2.1 สร้าง Pod**

```bash
kubectl apply -f labs/lab07-probes/liveness-exec-pod.yaml
```

**Expected output**

<pre>
pod/liveness-exec-pod created
</pre>

รอสัก 10 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME                 READY   STATUS    RESTARTS   AGE
liveness-exec-pod    1/1     Running   0          10s
readiness-http-pod   0/1     Running   0          30s
</pre>

ตอนนี้ `liveness-exec-pod` ยังสบายดี (มีไฟล์ `/tmp/healthy`)

**2.2 รอประมาณ 1 นาทีครึ่ง แล้วดูอีกครั้ง**

ไฟล์จะถูกลบที่วินาทีที่ 30 → probe ไม่ผ่าน 3 ครั้ง → container ถูกฆ่าแล้วเริ่มใหม่ (รวมเวลาปิด container ราว 75–90 วินาที)

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME                 READY   STATUS    RESTARTS      AGE
liveness-exec-pod    1/1     Running   1 (15s ago)   90s
readiness-http-pod   0/1     Running   0             110s
</pre>

RESTARTS ของ `liveness-exec-pod` เพิ่มเป็น `1` ส่วน `readiness-http-pod` ยังเป็น `0` ดูเหตุผล

```bash
kubectl describe pod liveness-exec-pod
```

**Expected output** (ส่วน Events ท้ายสุด)

<pre>
Events:
...
  Warning  Unhealthy  45s (x3 over 55s)  kubelet            spec.containers{app}: Liveness probe failed: cat: can't open '/tmp/healthy': No such file or directory
  Normal   Killing    45s                kubelet            spec.containers{app}: Container app failed liveness probe, will be restarted
...
</pre>

`Unhealthy (x3)` = probe ไม่ผ่าน 3 ครั้ง แล้ว `Killing` = ฆ่า container เพื่อเริ่มใหม่

### ขั้นที่ 3: ลบทั้งหมด

```bash
kubectl delete -f labs/lab07-probes/
```

**Expected output** (รอราว 30 วินาที)

<pre>
pod "liveness-exec-pod" deleted from default namespace
pod "readiness-http-pod" deleted from default namespace
</pre>

### สิ่งที่เห็น

- **readiness** ไม่ผ่าน → READY `0/1` แต่ไม่ restart และกลับมา `1/1` ได้เองเมื่อผ่าน
- **liveness** ไม่ผ่านครบ `failureThreshold` → `Killing` แล้ว RESTARTS เพิ่ม
- ดูผลของ probe ได้จาก Events ใน `kubectl describe pod`

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน readinessProbe ของ `readiness-http-pod` เป็น livenessProbe (ค่าเดิม) จะเกิดอะไรกับ RESTARTS เมื่อไม่มีไฟล์ `/ready.html`

---

## LAB 8: Multi-container: localhost, emptyDir, init, sidecar

<p align="center" id="fig-13">
  <img src="images/09-lab8-multi-container.png" alt="รูปที่ 13 LAB8 multi-container" width="900"><br>
  <em><b>รูปที่ 13</b> LAB8: Pod หลาย container คุยกันผ่าน localhost ใช้ emptyDir ร่วมกัน มี init container เตรียมไฟล์ และ sidecar เขียนข้อมูลต่อเนื่อง</em>
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

<p align="center" id="fig-14">
  <img src="images/10-lab9-som-shop-storefront.png" alt="รูปที่ 14 LAB9 ร้านอาหารแมวน้องส้ม" width="900"><br>
  <em><b>รูปที่ 14</b> LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้มด้วย Next.js + PostgreSQL ใน Pod เดียว</em>
</p>

**เป้าหมาย:** build image ของแอป Next.js เอง นำเข้าคลัสเตอร์ด้วย `kind load` เปิดร้านใน Pod เดียวที่มี native sidecar (PostgreSQL), init container 2 ตัว, emptyDir, env, resources และ probes ครบ แล้วเปิดร้านใน browser กดสั่งซื้อ และทดลองว่าข้อมูลรอดหรือหายในสถานการณ์ใด

> ⚠️ **ออกแบบเพื่อการเรียนรู้เท่านั้น** การใส่เว็บกับฐานข้อมูลไว้ใน Pod เดียว **ไม่ควรทำในงานจริง** (scale แยกไม่ได้, ลบ Pod = ข้อมูลหาย, อัปเดตเว็บต้องรีสตาร์ทฐานข้อมูลด้วย) รหัสผ่าน `meow1234` ใน env ก็ใช้เพื่อการเรียนเท่านั้น บทถัดไปจะแยกส่วนอย่างถูกต้อง

### 9.1 สถาปัตยกรรมของ Pod som-shop

<p align="center" id="fig-15">
  <img src="images/11-lab9-pod-architecture.png" alt="รูปที่ 15 สถาปัตยกรรม Pod som-shop" width="900"><br>
  <em><b>รูปที่ 15</b> สถาปัตยกรรม Pod som-shop: web (Next.js :3000) คุยกับ db (PostgreSQL :5432) ผ่าน localhost ภายใน Pod เดียว และเก็บข้อมูล DB บน emptyDir</em>
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

<p align="center" id="fig-16">
  <img src="images/12-lab9-startup-order.png" alt="รูปที่ 16 ลำดับการเริ่ม Pod som-shop" width="900"><br>
  <em><b>รูปที่ 16</b> ลำดับเริ่ม Pod: db (native sidecar) เริ่มก่อนและผ่าน startupProbe → wait-for-db รอ pg_isready → db-seed สร้างตารางและสินค้า → web เริ่มทำงาน</em>
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

<p align="center" id="fig-17">
  <img src="images/13-lab9-build-kind-load.png" alt="รูปที่ 17 build และ kind load" width="900"><br>
  <em><b>รูปที่ 17</b> build image som-shop-web:1.0 ใน k8s-lab แล้วใช้ kind load docker-image นำ image เข้าไปในทุก node ของคลัสเตอร์</em>
</p>

node ของ kind เป็น container แยก มี containerd ของตัวเอง **มองไม่เห็น image ใน Docker ของ k8s-lab** จึงต้อง `kind load` เข้าไปก่อน

🐧 **ใน SSH session ของ k8s-lab**

**ขั้นที่ 1: build image** (เครื่องทดสอบใช้ ~30–35 วินาที เครื่องหรือเน็ตช้าอาจหลายนาที เพราะต้องดึง `node:22-alpine` และ `npm ci`)

```bash
cd /workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB/som-shop/app
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
cd /workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB
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

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB`)

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

<p align="center" id="fig-18">
  <img src="images/14-lab9-open-in-browser.png" alt="รูปที่ 18 เปิดร้านจาก browser" width="900"><br>
  <em><b>รูปที่ 18</b> เปิดร้านจากเครื่องนักศึกษา: kubectl port-forward pod/som-shop 3000:3000 ใน k8s-lab และ ssh -L 3000:localhost:3000 จากเครื่องนักศึกษา</em>
</p>

**ขั้นที่ 1:** 🐧 **ใน SSH session หลักของ k8s-lab** เปิด port-forward ค้างไว้

```bash
kubectl port-forward pod/som-shop 3000:3000
```

```text
Forwarding from 127.0.0.1:3000 -> 3000
Forwarding from [::1]:3000 -> 3000
```

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ (ถ้า port-forward จาก LAB 3 ยังรันอยู่ ให้กด Ctrl+C ก่อน)

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

<p align="center" id="fig-19">
  <img src="images/screenshots/20261005_1725_lab002_01-som-shop.png" alt="รูปที่ 19 ภาพหน้าจอจริง หน้าร้านเริ่มต้น" width="700"><br>
  <em><b>รูปที่ 19</b> ภาพหน้าจอจริงจากการทดลอง: หน้าร้านอาหารแมวน้องส้มเมื่อเปิดครั้งแรก มีสินค้า 6 รายการ ออเดอร์ทั้งหมด 0 และ footer แสดงว่าเสิร์ฟโดย Pod som-shop (ภาพนี้ถ่ายผ่าน NodePort Service ชั่วคราวที่เพิ่มเองเพื่อถ่ายภาพ หน้าที่เห็นเหมือนกับที่เปิดผ่าน port-forward + ssh -L)</em>
</p>

กดปุ่ม **🛒 สั่งซื้อ** 3 ครั้ง (เลือกสินค้าต่างกันได้) แต่ละการ์ดจะขึ้น "สั่งซื้อแล้ว! ออเดอร์ #N" จำนวน "เหลือ ... ชิ้น" ลดลง และมีรายการใน "ออเดอร์ล่าสุด"

<p align="center" id="fig-20">
  <img src="images/screenshots/20261004_1814_lab9_02-shop-after-orders.png" alt="รูปที่ 20 ภาพหน้าจอจริง หลังสั่งซื้อ 3 ครั้ง" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: หลังกดสั่งซื้อ 3 ครั้ง ออเดอร์ทั้งหมดเป็น 3, stock ของสินค้าที่สั่งลดลง และมีรายการออเดอร์ล่าสุด 3 รายการ</em>
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

<p align="center" id="fig-21">
  <img src="images/15-lab9-emptydir-survive-vs-lost.png" alt="รูปที่ 21 emptyDir รอด vs หาย" width="900"><br>
  <em><b>รูปที่ 21</b> ทดลองกับข้อมูลออเดอร์: restart container db แล้วข้อมูลยังอยู่บน emptyDir แต่ลบ Pod แล้วข้อมูลหายทั้งหมด</em>
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

<p align="center" id="fig-22">
  <img src="images/screenshots/20261004_1815_lab9_03-after-db-restart.png" alt="รูปที่ 22 ภาพหน้าจอจริง หลัง restart db" width="700"><br>
  <em><b>รูปที่ 22</b> ภาพหน้าจอจริงจากการทดลอง: หลังหยุด PostgreSQL ด้วย pg_ctl stop จน container db ถูก restart ข้อมูล 3 ออเดอร์และ stock ที่ลดลงยังอยู่ครบ</em>
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

<p align="center" id="fig-23">
  <img src="images/screenshots/20261004_1815_lab9_04-after-pod-delete.png" alt="รูปที่ 23 ภาพหน้าจอจริง หลังลบ Pod แล้วสร้างใหม่" width="700"><br>
  <em><b>รูปที่ 23</b> ภาพหน้าจอจริงจากการทดลอง: หลังลบ Pod แล้ว apply ใหม่ (และรัน port-forward ใหม่) ร้านกลับเป็น 0 ออเดอร์ และ stock กลับเป็นค่าตั้งต้น</em>
</p>

**สรุปทดลองที่ 2:** Pod ใหม่ได้ **IP ใหม่** (รอบทดลองนี้ `10.244.3.21` → `10.244.3.22` ของนักศึกษาจะเป็นเลขอื่น และอาจย้ายไปอีก node ด้วย), emptyDir ว่างเปล่า PostgreSQL จึงสร้างฐานข้อมูลใหม่ และ `db-seed` ใส่สินค้าใหม่ทั้ง 6 รายการ (`new: 6`) **ออเดอร์ทั้งหมดหายไป**

### 9.11 ทำไมงานจริงต้องแยก และบทหน้าจะทำอะไร

<p align="center" id="fig-24">
  <img src="images/16-lab9-next-split.png" alt="รูปที่ 24 บทหน้า: แยกเว็บกับฐานข้อมูล" width="900"><br>
  <em><b>รูปที่ 24</b> Pod เดียวรวมเว็บกับฐานข้อมูลเป็นการออกแบบเพื่อการเรียนรู้ บทหน้าจะแยก web เป็น Deployment, db ใช้ที่เก็บถาวร และเชื่อมกันด้วย Service</em>
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
| `docker run` แจ้ง `Conflict. The container name "/k8s-lab" is already in use` | มี container ชื่อ `k8s-lab` อยู่แล้ว (เช่นจากบทที่ 1) | ใช้ตัวเดิม (`docker start k8s-lab`) หรือลบก่อนด้วย `docker rm -f k8s-lab` แล้ว `docker run` ใหม่ (ดู [LAB 0 ขั้นที่ 1](#ขั้นที่-1-setup-container-และคลัสเตอร์)) |
| `docker run` แจ้ง `port is already allocated` | container อื่นใช้ port `2223`/`8889` อยู่ | 🖥️ `docker ps` หาตัวที่ใช้ port แล้ว `docker stop <ชื่อ>` จากนั้น `docker rm -f k8s-lab` แล้วสั่ง `docker run` ใหม่ |
| `docker pull` ช้ามากหรือแจ้ง `toomanyrequests` | image ใหญ่ ~1.5 GB หรือ Docker Hub จำกัดการดึง | รอแล้วสั่งซ้ำ (ส่วนที่โหลดแล้วไม่ต้องโหลดใหม่) หรือ `docker login` ด้วยบัญชี Docker Hub ของตัวเอง |
| `ssh -p 2223` แจ้ง `Connection refused` | container ไม่ได้รัน หรือ sshd ยังไม่ขึ้น | 🖥️ `docker ps -a --filter name=k8s-lab` ถ้า `Exited` ให้ `docker start k8s-lab` แล้วรอ 2–3 วินาที |
| `ssh` แจ้ง `REMOTE HOST IDENTIFICATION HAS CHANGED!` | ลบแล้วสร้าง `k8s-lab` ใหม่ host key จึงเปลี่ยน | 🖥️ `ssh-keygen -R "[localhost]:2223"` แล้ว ssh ใหม่ |
| `k8s-up` ล้ม มีข้อความ `Structure needs cleaning` หรือ `docker logs k8s-lab` ไม่มี `memory`/`io` ในบรรทัด cgroup | สร้าง container โดยไม่ใส่ `--privileged` หรือ Docker ไม่ได้ใช้ cgroup v2 | ลบแล้วสร้างใหม่ด้วยคำสั่ง `docker run` เต็มใน LAB 0 (ต้องมี `--privileged`) และใช้ Docker Desktop แบบ WSL2/Linux containers |
| `git clone` แจ้ง `Could not resolve host: github.com` หรือค้างนาน | container ออกเน็ตไม่ได้ หรือเน็ตช้า | 🐧 ตรวจด้วย `curl -sI https://github.com \| head -1` ถ้าเน็ตช้าใช้ `git clone --depth 1 ...` |
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `git clone` หรืออยู่ผิดโฟลเดอร์ | 🐧 ทำ [LAB 0 ขั้นที่ 2](#ขั้นที่-2-git-clone-ไฟล์-lab) (`cd /workspace && git clone https://github.com/Tuchsanai/DevTools.git`) แล้ว `cd /workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (เช่น connection refused) | ยังไม่ได้รัน `k8s-up` หรือคลัสเตอร์ถูกลบ/หยุดไป | 🐧 รัน `k8s-up` ใหม่ (ถ้าเพิ่ง restart container คลัสเตอร์อาจต้องสร้างใหม่) |
| Pod `som-shop` ค้าง `Init:ErrImagePull` / `ImagePullBackOff` ที่ `db-seed` หรือ `web` | ลืม `kind load docker-image som-shop-web:1.0 --name lab` node จึงไปหา image บน Docker Hub ซึ่งไม่มี | 🐧 `kind load docker-image som-shop-web:1.0 --name lab` แล้ว `kubectl delete pod som-shop` และ `kubectl apply -f som-shop/k8s/som-shop-pod.yaml` |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform กับ containerd image store (ดู [9.3](#93-build-image-และนำเข้าคลัสเตอร์)) | ใช้ `docker save --platform linux/amd64 ... -o /tmp/pg.tar` + `kind load image-archive /tmp/pg.tar --name lab` (เครื่อง ARM ใช้ `linux/arm64`) |
| `ErrImagePull` ที่ Events มีคำว่า `toomanyrequests` / `429 Too Many Requests` | Docker Hub จำกัดจำนวนการดึงแบบไม่ล็อกอิน (ทั้งห้องใช้ IP เดียว) | รอสักพักแล้วลองใหม่ หรือ `docker pull` ล่วงหน้าแล้ว `kind load` (สำหรับ postgres ใช้วิธีใน 9.3) |
| `kubectl port-forward` แจ้งว่า listen ไม่ได้ มีคำว่า `address already in use` | port-forward ตัวเก่ายังรันอยู่ (เช่นลืม Ctrl+C จาก LAB 3) | หาและหยุดด้วย `pgrep -af "kubectl port-forward"` / `pkill -f "kubectl port-forward"` หรือใช้ port อื่น เช่น `kubectl port-forward pod/web 8081:80` |
| `ssh -L` แจ้งว่า bind port ไม่ได้ (`Address already in use` / `cannot listen to port`) หรือ browser เปิดแล้วเป็นเว็บอื่น | port 8080/3000 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ (เช่น dev server) | เปลี่ยนเลข **ซ้าย** ของ `-L` เช่น `ssh -p 2223 -L 13000:localhost:3000 root@localhost` แล้วเปิด `http://localhost:13000` |
| browser เปิดไม่ได้ (connection refused/ERR_CONNECTION_RESET) | หน้าต่าง `ssh -L` ถูกปิด หรือ port-forward หยุด/หลุด | ตรวจว่าทั้งสองหน้าต่างยังทำงาน ดูหน้าต่าง port-forward ว่ามี `Handling connection for ...` |
| port-forward ขึ้น `error: lost connection to pod` | Pod ถูกลบ/สร้างใหม่ port-forward ผูกกับ Pod เดิม | Ctrl+C แล้วรัน `kubectl port-forward ...` ใหม่ |
| หน้าเว็บ LAB 3 แสดงภาษาไทยเพี้ยน | nginx ไม่ส่ง charset | ใส่ `<meta charset=utf-8>` นำหน้าใน `index.html` |
| `kubectl delete` Pod ที่ใช้ busybox ค้างประมาณ 30 วินาที | `sh` เป็นโปรเซสหลัก ไม่ตอบ SIGTERM จึงรอ grace period 30 วินาที | รอ หรือใช้ `kubectl delete pod <ชื่อ> --now` |
| `wget http://localhost:3000/...` ใน container `web` ได้ `Connection refused` | `localhost` ถูก resolve เป็น `::1` แต่ Next.js ฟังเฉพาะ IPv4 | ใช้ `http://127.0.0.1:3000/...` (ดู [9.7](#97-ตรวจ-health-ภายใน-pod-และเรื่อง-localhost-กับ-ipv6)) |
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
- [ ] **LAB 2** ผล `pod/web unchanged` และ `AlreadyExists`
- [ ] **LAB 3** browser บนเครื่องนักศึกษาเปิด `http://localhost:8080` เห็น "สวัสดีจากน้องส้ม" และ `kubectl logs web` มี request จาก browser
- [ ] **LAB 4** ผล `kubectl get pods -l app=som-shop,tier=web` เหลือ `shop-web` ตัวเดียว
- [ ] **LAB 5** `kubectl get pods` ที่เห็น `Completed`, `Error`/`CrashLoopBackOff` (RESTARTS > 0) และ `ErrImagePull`/`ImagePullBackOff` พร้อม `kubectl logs crash-pod`
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

🖥️ **บนเครื่องนักศึกษา** (ทางเลือก) หยุด container เพื่อคืน RAM/CPU แล้วเปิดใหม่ครั้งหน้าด้วย `docker start k8s-lab` (คลัสเตอร์และไฟล์ใน `/workspace` ยังอยู่) หรือลบทิ้งทั้งหมดถ้าไม่ใช้แล้ว (ครั้งหน้าต้องเริ่มจาก LAB 0 ขั้นที่ 1 ใหม่ แต่ไม่ต้อง pull image ซ้ำ)

```bash
docker stop k8s-lab      # หยุดชั่วคราว ข้อมูลยังอยู่
docker rm -f k8s-lab     # ลบ container รวมคลัสเตอร์และไฟล์ข้างในทั้งหมด (image ยังอยู่)
```

> **บทถัดไป:** น้องส้มจะแยกเว็บกับฐานข้อมูลออกจากกัน ให้ Deployment ดูแลการสร้าง Pod ใหม่ ใช้ Service ให้ที่อยู่คงที่ (และเปิดร้านผ่าน port 30080–30082 ได้โดยไม่ต้อง port-forward) เก็บข้อมูลบนที่เก็บถาวร และย้ายรหัสผ่านไปไว้ใน Secret
