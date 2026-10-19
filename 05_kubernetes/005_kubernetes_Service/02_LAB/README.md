# LAB บทที่ 5: Kubernetes Service — ที่อยู่เดียวของร้านน้องส้ม

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Kubernetes Service — ClusterIP, selector และ Endpoints, ชื่อ Service กับ DNS, NodePort และร้านน้องส้มที่มีที่อยู่เดียวแม้ Deployment จะเปลี่ยนรุ่น
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ทุก LAB ทำ **ใน container `k8s-lab`** (image `tuchsanai/devtools-kind:2569_1` มี kubectl, kind, helm, k9s และ Docker ข้างในครบ) บทที่แล้ว LAB 4 จบด้วยปัญหาว่า `kubectl port-forward` ต่อท่อเข้า **Pod ได้ทีละตัว** และท่อ **หลุดทุกครั้ง** (`lost connection to pod`) ที่ Deployment เปลี่ยนรุ่นแล้ว Pod ตัวนั้นถูกปิด บทนี้ให้ **Service** เป็น **ที่อยู่เดียว** ของ Pod ทั้งกลุ่ม ตั้งแต่ Service แรกที่เรียกด้วยชื่อจากในคลัสเตอร์ ดูว่า Service หา Pod จากป้ายอย่างไร เปิดประตู NodePort ให้ browser บนเครื่องเราเข้าได้ จนถึงให้ **"ร้านอาหารแมวน้องส้ม"** มีที่อยู่เดียว `http://localhost:30080` ที่กระจายลูกค้าไปทุกสาขา และไม่หลุดแม้ร้านจะเปลี่ยนเมนูเป็นเวอร์ชัน 2.0

> บล็อก **Expected output** คือผลที่ควรเห็นหลังรันคำสั่ง (ไม่ต้องพิมพ์ตาม) มาจากการทดลองจริงรอบเดียวกันทั้งบทเมื่อ 19 ต.ค. 2569 บนคลัสเตอร์ที่สร้างใหม่ (kind v0.33.0, kubectl v1.37.1, Kubernetes v1.37.0) **ชื่อ Pod, IP ของ Pod, IP ของ Node และ CLUSTER-IP ของ Service ถูกสุ่มทุกครั้ง** (เช่น `web-65b66cc75b-gm2pc`, `10.244.2.6`, `10.96.169.141`) และ **Pod ที่ตอบในแต่ละครั้งก็สุ่ม** ค่าในเครื่องนักศึกษาจะต่างไป เป็นเรื่องปกติ

| สัญลักษณ์ | รันที่ไหน |
|---|---|
| 🖥️ | Terminal/PowerShell บนเครื่องนักศึกษา |
| 🐧 | SSH session ใน k8s-lab (prompt `root@k8s-lab`) |
| 🌐 | browser บนเครื่องนักศึกษา |

บทนี้ลงมือ Service 2 แบบจาก 3 แบบใน [ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร): **LAB 1–2 ใช้ ClusterIP** (เรียกจากภายในคลัสเตอร์) และ **LAB 3–4 ใช้ NodePort** (เรียกจากนอกคลัสเตอร์) ตัวเลข `port` / `targetPort` / `nodePort` ของทุก LAB สรุปเทียบกันไว้ใน [ทฤษฎีหัวข้อ 4](../01_Theory/README.md#4-ที่อยู่-3-แบบ-และ-port-4-ตัว-ศัพท์ที่ต้องแยกให้ออก)

ทุก LAB มี **ภาพแผนการทดลอง** บอกว่า LAB นั้นมีกี่การทดลอง และทุกขั้นเริ่มด้วย 2 บรรทัดนี้ อ่านก่อนพิมพ์คำสั่ง

- 🎯 **เป้าหมายขั้นนี้** = ขั้นนี้ทดลองเพื่อพิสูจน์หลักการอะไร (มีลิงก์ไปหัวข้อทฤษฎีที่เกี่ยวข้อง)
- 🔍 **สังเกต** = ตอนดูผลลัพธ์ให้มองหาอะไร ถ้าเห็นตามนี้ แปลว่าหลักการนั้นเป็นจริง

### กติกา

- ทำงานในโฟลเดอร์ `/workspace/DevTools/05_kubernetes/005_kubernetes_Service/02_LAB` และ **ลบ Service และ Deployment ของตัวเองทุกครั้งที่จบ LAB**
- **ชื่อ Pod, IP ของ Pod และ IP ของ Node ในเครื่องแต่ละคนไม่เหมือนกัน** คำสั่งที่มี `# ← เปลี่ยนเป็น ... ของตัวเอง` ให้แทนด้วยค่าที่เห็นจาก `kubectl get pods -o wide` หรือ `kubectl get nodes -o wide` ในเครื่องตัวเอง
- บทนี้ **ไม่ใช้ port-forward และไม่ต้องใช้ VS Code แล้ว** เข้าถึงแอปผ่าน Service แบบ **ClusterIP** (จากในคลัสเตอร์) และ **NodePort** (จากนอกคลัสเตอร์ ที่ `http://localhost:30080`) เท่านั้น (Ingress และ LoadBalancer ไม่อยู่ในบทนี้)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมสภาพแวดล้อม (Setup)](#lab-0-เตรียมสภาพแวดล้อม-setup) (container `k8s-lab` ที่เปิด port NodePort + คลัสเตอร์ + git clone) | 20–30 นาที | ⭐ |
| 1 | [Service แรก (ClusterIP)](#lab-1-service-แรก-clusterip) | 25 นาที | ⭐⭐ |
| 2 | [Service หา Pod จากป้าย](#lab-2-service-หา-pod-จากป้าย) | 25 นาที | ⭐⭐⭐ |
| 3 | [NodePort: เปิดประตูให้คนนอกคลัสเตอร์](#lab-3-nodeport-เปิดประตูให้คนนอกคลัสเตอร์) | 20 นาที | ⭐⭐⭐ |
| 4 | [LAB สุดท้าย: ร้านน้องส้มมีที่อยู่เดียว](#lab-4-lab-สุดท้าย-ร้านน้องส้มมีที่อยู่เดียว) | 45–60 นาที | ⭐⭐⭐⭐⭐ |
| – | [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) · [สรุปคำสั่ง kubectl ในบทนี้](#สรุปคำสั่ง-kubectl-ในบทนี้) | | |

รวมประมาณ 2.5–3 ชั่วโมง (เครื่องช้าหรือเน็ตช้าอาจนานกว่านี้ เพราะต้องดึง image จาก Docker Hub)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 Setup container และคลัสเตอร์](#fig-1) | 9 | [ภาพหน้าจอจริง: nginx ผ่าน NodePort](#fig-9) |
| 2 | [LAB 0 git clone](#fig-2) | 10 | [LAB 4 Endpoints ของ som-menu ระหว่างและหลังเปลี่ยนรุ่น](#fig-10) |
| 3 | [LAB 1 Service ClusterIP และชื่อใน DNS](#fig-3) | 11 | [แผนการทดลอง LAB 4](#fig-11) |
| 4 | [แผนการทดลอง LAB 1](#fig-4) | 12 | [ภาพหน้าจอจริง: หน้าร้านเวอร์ชัน 1.0 Pod แรก](#fig-12) |
| 5 | [LAB 2 Endpoints ตาม label และกับดัก 2 แบบ](#fig-5) | 13 | [ภาพหน้าจอจริง: refresh แล้วได้อีก Pod](#fig-13) |
| 6 | [แผนการทดลอง LAB 2](#fig-6) | 14 | [ภาพหน้าจอจริง: แค่ refresh ก็ได้เวอร์ชัน 2.0](#fig-14) |
| 7 | [LAB 3 NodePort 30080 บน Node ทุกตัว](#fig-7) | 15 | [บทที่ 4 port-forward หลุด เทียบกับบทที่ 5 ที่อยู่เดียว](#fig-15) |
| 8 | [แผนการทดลอง LAB 3](#fig-8) | | |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                     ← เอกสารนี้
├── images/                       ← ภาพประกอบ + screenshots/ ภาพหน้าจอจริง
├── labs/
│   ├── lab01-clusterip/{web-deploy,web-svc,client-pod}.yaml   ← ใช้ใน LAB 1, 2 (web-deploy ใช้ใน LAB 3 ด้วย)
│   ├── lab02-selector/{web-svc-typo,web-svc-wrongport}.yaml   ← ใช้ใน LAB 2 (กับดัก selector ผิด / targetPort ผิด)
│   └── lab03-nodeport/{web-svc-nodeport,web-svc-lb}.yaml      ← ใช้ใน LAB 3 (NodePort / LoadBalancer)
└── som-menu/
    ├── app/                      ← เว็บหน้าร้าน Node.js (server.js + Dockerfile)
    └── k8s/{som-menu-deploy,som-menu-deploy-v2,som-menu-svc}.yaml
```

---

## LAB 0: เตรียมสภาพแวดล้อม (Setup)

**เป้าหมาย:** สร้าง container `k8s-lab` **ที่เปิด port NodePort `30080–30082` ออกมาถึงเครื่องนักศึกษา** และคลัสเตอร์ kind ชื่อ `lab` (1 control-plane + 2 worker) แล้วดึงไฟล์ LAB มาไว้ใน container (รายละเอียดของแต่ละคำสั่งดูได้จาก [LAB บทที่ 1](../../001_kubernetes-introduction/02_LAB/readme.md))

**ต้องมี:** Docker Desktop (Linux containers, RAM อย่างน้อย 4 GB) และ SSH client

> **ถ้ายังมี container `k8s-lab` จากบทก่อน:** container นั้นสร้างโดย **ไม่มี** `-p 30080-30082:30080-30082` จึงเปิด NodePort จาก browser บนเครื่องไม่ได้ (เพิ่ม port ให้ container ที่สร้างไปแล้วไม่ได้) ให้ลบทิ้งแล้วสร้างใหม่ตามขั้นที่ 1 ด้วย 🖥️ `docker rm -f k8s-lab` ไม่ต้องกังวล ไฟล์ LAB ได้จาก git clone ใหม่ในขั้นที่ 2 และคลัสเตอร์สร้างใหม่ได้ด้วย `k8s-up` (ถ้ามีงานของตัวเองเก็บไว้ใน container ให้คัดลอกออกมาก่อน)

### ขั้นที่ 1: Setup container และคลัสเตอร์

<p align="center" id="fig-1">
  <img src="images/01-lab0-setup.png" alt="รูปที่ 1 LAB0 Setup container และคลัสเตอร์" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0 ขั้นที่ 1: (1) docker run สร้าง container k8s-lab (2) ssh -p 2223 เข้าไปข้างใน (3) รัน k8s-up สร้าง kind cluster ชื่อ lab ได้ 3 node Ready (control-plane 1 ตัว + worker 2 ตัว)</em>
</p>

**1) สร้าง container** 🖥️ **บนเครื่องนักศึกษา** (image ประมาณ 1.5 GB ครั้งแรกใช้เวลาหลายนาที)

```bash
docker pull tuchsanai/devtools-kind:2569_1
```

```bash
docker run -dit --name k8s-lab --hostname k8s-lab --privileged -p 2223:22 -p 8889:8888 -p 30080-30082:30080-30082 tuchsanai/devtools-kind:2569_1
```

- `--privileged` ให้รัน Docker ซ้อนใน container ได้ (kind ต้องใช้) **ขาดไม่ได้**
- `-p 2223:22` เปิดทาง SSH เข้า container ผ่าน port `2223`
- `-p 8889:8888` เปิด JupyterLab ที่ `http://localhost:8889/lab` (ทางเลือก)
- `-p 30080-30082:30080-30082` **ใหม่ในบทนี้** เปิด port `30080`, `30081`, `30082` ของ container ออกมาที่เครื่องนักศึกษา เป็นทางให้ browser เข้าถึง Service แบบ **NodePort** ใน LAB 3–4 (`http://localhost:30080`)

หลัง `docker run` **รอสัก 5–10 วินาที** ให้ container เริ่ม sshd และ dockerd ข้างในให้เสร็จก่อน

**2) SSH เข้า container** 🖥️ ครั้งแรกพิมพ์ `yes` แล้วใส่รหัสผ่าน `passwd`

```bash
ssh -p 2223 root@localhost
```

**3) สร้างและตรวจคลัสเตอร์** 🐧 **ใน SSH session ของ k8s-lab** (prompt `root@k8s-lab:~#`)

```bash
time k8s-up
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
...
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
...
  NodePort ที่ map ออก host: 30080 30081 30082

real	0m34.846s
</pre>

`k8s-up` สร้างคลัสเตอร์ใช้เวลาราว 30 วินาที – 1 นาที บรรทัด **`NodePort ที่ map ออก host: 30080 30081 30082`** ที่บทก่อน ๆ ข้ามไป บทนี้ใช้จริงแล้ว: คลัสเตอร์ `lab` เปิด port 30080–30082 ของ Node ออกมาที่ container `k8s-lab` และ `-p 30080-30082:30080-30082` ตอน `docker run` ต่อออกมาถึงเครื่องเราอีกชั้น

```bash
kubectl get nodes
```

**Expected output**

<pre>
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   76s   v1.37.0
lab-worker          Ready    &lt;none&gt;          63s   v1.37.0
lab-worker2         Ready    &lt;none&gt;          63s   v1.37.0
</pre>

```bash
kubectl get pods -A
```

**Expected output**

<pre>
NAMESPACE            NAME                                        READY   STATUS    RESTARTS   AGE
kube-system          coredns-559f6c778d-67zbz                    1/1     Running   0          67s
kube-system          coredns-559f6c778d-75xpb                    1/1     Running   0          67s
kube-system          etcd-lab-control-plane                      1/1     Running   0          77s
kube-system          kindnet-8bqwn                               1/1     Running   0          67s
kube-system          kindnet-kcskk                               1/1     Running   0          64s
kube-system          kindnet-twl2f                               1/1     Running   0          64s
kube-system          kube-apiserver-lab-control-plane            1/1     Running   0          77s
kube-system          kube-controller-manager-lab-control-plane   1/1     Running   0          77s
kube-system          kube-proxy-46hjr                            1/1     Running   0          67s
kube-system          kube-proxy-98vh8                            1/1     Running   0          64s
kube-system          kube-proxy-gggjh                            1/1     Running   0          64s
kube-system          kube-scheduler-lab-control-plane            1/1     Running   0          77s
local-path-storage   local-path-provisioner-75f7fc7dc5-2snl4     1/1     Running   0          67s
</pre>

ถ้า `coredns` บางตัวยังเป็น `0/1` ให้รอสัก 10 วินาที แล้วสั่งซ้ำ บทนี้มี 2 กลุ่มที่ทำงานให้ Service

- **`kube-proxy`** มี **3 ตัว = 1 ตัวต่อ Node** ทำหน้าที่วางเส้นทางบนทุก Node ว่าลูกค้าที่เรียก Service จะถูกส่งต่อไป Pod ไหน
- **`coredns`** คือ **สมุดรายชื่อ** (DNS) ของคลัสเตอร์ แปลงชื่อ Service เช่น `web` เป็นที่อยู่ IP

```bash
kubectl get svc -A
```

**Expected output**

<pre>
NAMESPACE     NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       kubernetes   ClusterIP   10.96.0.1    &lt;none&gt;        443/TCP                  77s
kube-system   kube-dns     ClusterIP   10.96.0.10   &lt;none&gt;        53/UDP,53/TCP,9153/TCP   76s
</pre>

(`svc` คือชื่อย่อของ `service`) คลัสเตอร์ใหม่ก็มี Service อยู่แล้ว 2 ตัว

- `kubernetes` = ที่อยู่ของ API server สำหรับโปรแกรมที่รันใน Pod
- **`kube-dns`** = Service ของ `coredns` ที่ **`10.96.0.10`** port 53 **จำเลขนี้ไว้** จะเจออีกใน LAB 1

> **✅ ผ่านเมื่อ:** node 3 ตัว `Ready`, Pod ระบบทุกตัวเป็น `1/1 Running` และเห็น Service `kube-dns`

### ขั้นที่ 2: git clone ไฟล์ LAB

<p align="center" id="fig-2">
  <img src="images/01c-lab0-git-clone.png" alt="รูปที่ 2 LAB0 ขั้นที่ 2 git clone และ cd" width="900"><br>
  <em><b>รูปที่ 2</b> LAB0 ขั้นที่ 2: git clone ดึง repo DevTools มาไว้ที่ /workspace/DevTools ใน k8s-lab แล้ว cd ลงไปจนถึงโฟลเดอร์ 02_LAB ของบทที่ 5 ที่มี labs และ som-menu</em>
</p>

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace
```

```bash
git clone https://github.com/Tuchsanai/DevTools.git
```

ถ้าเคย clone ไว้แล้วใน container นี้ จะขึ้นว่า `already exists` ให้ `cd DevTools` แล้ว `git pull` แทน จากนั้น `cd /workspace`

```bash
cd DevTools/05_kubernetes/005_kubernetes_Service/02_LAB
```

> **✅ ผ่านเมื่อ:** prompt เป็น `root@k8s-lab:/workspace/DevTools/05_kubernetes/005_kubernetes_Service/02_LAB#` ทุกคำสั่งที่อ้าง `labs/...` หรือ `som-menu/...` ต้องรันจากโฟลเดอร์นี้

---

## LAB 1: Service แรก (ClusterIP)

<p align="center" id="fig-3">
  <img src="images/02-lab1-clusterip.png" alt="รูปที่ 3 LAB1 Service ClusterIP เรียกด้วยชื่อจาก Pod ในคลัสเตอร์" width="900"><br>
  <em><b>รูปที่ 3</b> LAB1 (ค่าจริงจากการทดลอง): (1) Pod client ถาม kube-dns ได้ว่าชื่อ web คือ ClusterIP 10.96.169.141 (2) เรียก http://web ที่ port 80 ของ Service (3) Service ส่ง request ต่อไป Pod ใน Endpoints ซึ่งคือ Pod IP:targetPort ของ Pod 3 ตัวที่มี label app=web บน lab-worker และ lab-worker2</em>
</p>

**เป้าหมาย:** สร้าง Pod nginx 3 ตัวด้วย Deployment แล้วสร้าง Service แบบ ClusterIP เป็นที่อยู่เดียวของทั้ง 3 ตัว เรียกด้วยชื่อ `web` จาก Pod อีกตัวในคลัสเตอร์ ดูว่า Service กระจายงาน และชื่อ `web` แปลงเป็น IP ได้อย่างไร

<p align="center" id="fig-4">
  <img src="images/02a-lab1-plan.png" alt="รูปที่ 4 แผนการทดลอง LAB1" width="900"><br>
  <em><b>รูปที่ 4</b> แผนการทดลอง LAB1 มี 4 การทดลอง: (1) ขั้นที่ 1–2 สร้าง Service แบบ ClusterIP ได้ IP คงที่ 1 อัน (2) ขั้นที่ 3 Endpoints คือรายชื่อ Pod IP:targetPort ที่ selector หาเจอ (3) ขั้นที่ 4–6 เรียกชื่อ web จาก Pod ในคลัสเตอร์ request กระจายไปทุก Pod และ DNS แปลชื่อเป็น ClusterIP (4) ขั้นที่ 7–8 เรียก Pod IP ตรง ๆ ได้ Pod ตัวเดียว จึงควรเรียกด้วยชื่อ Service</em>
</p>

🐧 **ใน SSH session ของ k8s-lab** (ทุกขั้นใน LAB 1–3)

### ขั้นที่ 1: Pod nginx 3 ตัวที่บอกชื่อตัวเอง

> 🎯 **เป้าหมายขั้นนี้:** เตรียม Pod 3 ตัวที่มี label `app: web` และตอบชื่อ Pod ของตัวเอง ไว้ดูว่า Service ส่ง request ไป Pod ไหน ([ทฤษฎีหัวข้อ 8](../01_Theory/README.md#8-service-หา-pod-จากป้าย))
>
> 🔍 **สังเกต:** Pod 3 ตัวมี Pod IP คนละอัน (`10.244.x.x`) และอยู่บน 2 Node ถ้าเรียก Pod IP เอง ต้องจำ IP ถึง 3 อัน

ไฟล์ `labs/lab01-clusterip/web-deploy.yaml`

```yaml
# LAB 1, 2, 3: เว็บ nginx 3 Pod ที่บอกชื่อ Pod ของตัวเองบนหน้าเว็บ — ไว้ดูว่า Service ส่งลูกค้าไป Pod ไหน
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web                 # ← ป้ายนี้แหละที่ Service ใช้หา Pod
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          command: ["/bin/sh", "-c"]   # เปลี่ยนคำสั่งเริ่มต้น (บทที่ 2): เขียนหน้าเว็บก่อน แล้วค่อยเปิด nginx
          args:
            - echo "Hello from Pod $(hostname)" > /usr/share/nginx/html/index.html && exec nginx -g "daemon off;"
          ports:
            - containerPort: 80
```

ทำงานอย่างไร

- เป็น Deployment แบบบทที่ 4: ชื่อ `web`, ขอ Pod 3 ตัว, ป้าย **`app: web`** (ป้ายนี้คือสิ่งที่ Service จะใช้หา Pod)
- `command` + `args` (เรื่องเดียวกับบทที่ 2) เปลี่ยนคำสั่งเริ่มต้นของ container ให้ shell ทำ 2 อย่างต่อกัน: เขียนหน้าเว็บ `Hello from Pod <ชื่อ Pod>` (`$(hostname)` ใน Pod = ชื่อ Pod) แล้วค่อยเปิด nginx
- หน้าเว็บของแต่ละ Pod จึงต่างกัน เราจะรู้ได้ทันทีว่า **Pod ไหนเป็นคนตอบ**

```bash
kubectl apply -f labs/lab01-clusterip/web-deploy.yaml
```

**Expected output**

<pre>
deployment.apps/web created
</pre>

รอจน Pod พร้อมครบ 3 ตัวด้วย `rollout status` (คำสั่งเดียวกับบทที่ 4) คำสั่งนี้จะค้างจนพร้อม ครั้งแรกบนคลัสเตอร์ใหม่อาจนานหลายสิบวินาที เพราะ Node ต้องดึง image `nginx` ก่อน

```bash
kubectl rollout status deployment/web
```

**Expected output**

<pre>
Waiting for deployment "web" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 2 of 3 updated replicas are available...
deployment "web" successfully rolled out
</pre>

> **ทำไมต้องรอให้พร้อมก่อน:** ตอนทดลองบนคลัสเตอร์ใหม่ ถ้ารอแค่ 10 วินาทีแล้วสร้าง Service เลย Pod ยังเป็น `ContainerCreating` อยู่ และ `kubectl describe svc web` ขึ้น `Endpoints:` ว่าง เพราะ Service ใส่ในรายชื่อเฉพาะ Pod ที่พร้อมแล้ว (ทฤษฎีหัวข้อ 12)

ดู Pod พร้อม IP

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
web-65b66cc75b-gm2pc   1/1     Running   0          0s    10.244.2.6   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-jmvlk   1/1     Running   0          0s    10.244.2.5   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-wrw8f   1/1     Running   0          0s    10.244.1.3   lab-worker2   &lt;none&gt;           &lt;none&gt;
</pre>

Pod 3 ตัว **IP คนละอัน** อยู่บนเรือ 2 ลำ ถ้าโปรแกรมอื่นอยากเรียกเว็บนี้ จะจำ IP ตัวไหน และถ้า Pod ถูกลบ IP ก็เปลี่ยน นี่คือปัญหาที่ Service แก้

### ขั้นที่ 2: สร้าง Service

> 🎯 **เป้าหมายขั้นนี้:** สร้าง Service แบบ **ClusterIP** แล้วดูว่าได้ IP คงที่ 1 อันสำหรับ Pod ทั้ง 3 ตัว ([ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร) · [ทฤษฎีหัวข้อ 6](../01_Theory/README.md#6-อ่าน-yaml-ของ-service-ทีละบรรทัด))
>
> 🔍 **สังเกต:** `TYPE ClusterIP`, `CLUSTER-IP` ขึ้นต้น `10.96.` (คนละช่วงกับ Pod IP) และ `PORT(S) 80/TCP` ไม่มีเลข nodePort

ไฟล์ `labs/lab01-clusterip/web-svc.yaml`

```yaml
# LAB 1, 2: Service แรก (ClusterIP) — ที่อยู่เดียวของ Pod ทุกตัวที่ติดป้าย app=web ใช้ได้เฉพาะในคลัสเตอร์
apiVersion: v1               # Service อยู่กลุ่มหลัก v1 เหมือน Pod
kind: Service
metadata:
  name: web                  # ชื่อ Service = ชื่อที่ Pod อื่นใช้เรียก เช่น http://web
spec:
  type: ClusterIP            # ค่าเริ่มต้น: ได้ IP ภายในคลัสเตอร์ 1 อันที่ไม่เปลี่ยน
  selector:
    app: web                 # ส่งงานให้ Pod ที่มีป้ายนี้ (ไม่มี matchLabels แบบ ReplicaSet)
  ports:
    - port: 80               # port ของ Service (คนเรียกใช้ port นี้)
      targetPort: 80         # port ของ container ใน Pod ที่จะส่งต่อไป
```

ทำงานอย่างไร

- `kind: Service` ชื่อ **`web`** = ชื่อนี้คือที่อยู่ที่ Pod อื่นใช้เรียก (`http://web`)
- `type: ClusterIP` = ได้ **IP ภายในคลัสเตอร์ 1 อัน ที่ไม่เปลี่ยน** ตลอดอายุของ Service (เรียกได้เฉพาะจากในคลัสเตอร์)
- `selector: app: web` = ส่งงานให้ **ทุก Pod ที่มีป้าย `app=web`** (เขียนป้ายตรง ๆ ไม่มี `matchLabels` แบบ ReplicaSet)
- `port: 80` คือ port ของ Service (ที่ ClusterIP) ส่วน `targetPort: 80` คือ port ของ Pod ที่ Service ส่ง request ต่อไป เลขเท่ากันแต่เป็นคนละ port (ทฤษฎีหัวข้อ 4) และใน LAB 4 สองค่านี้จะไม่เท่ากัน
- Service ไม่ได้สร้าง Pod เลย และไม่ใช่เจ้าของ Pod มันแค่ **หา Pod จากป้าย** แล้วส่งงานให้

```bash
kubectl apply -f labs/lab01-clusterip/web-svc.yaml
```

**Expected output**

<pre>
service/web created
</pre>

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1       &lt;none&gt;        443/TCP   2m32s
web          ClusterIP   10.96.169.141   &lt;none&gt;        80/TCP    0s
</pre>

Service `web` ได้ **`CLUSTER-IP 10.96.169.141`** (ขึ้นต้น `10.96.` เหมือน `kube-dns` ใน LAB 0 คนละช่วงกับ IP ของ Pod ที่ขึ้นต้น `10.244.`) และเปิด port `80/TCP`

### ขั้นที่ 3: Service ส่งงานให้ใคร (Endpoints)

> 🎯 **เป้าหมายขั้นนี้:** ดูว่า Service หา Pod จาก `selector` แล้วจดเป็น **Endpoints** ([ทฤษฎีหัวข้อ 5](../01_Theory/README.md#5-service-ทำงานอย่างไร))
>
> 🔍 **สังเกต:** `Endpoints` คือ Pod IP:targetPort (`:80`) ของ Pod ทั้ง 3 ตัว ตรงกับ `kubectl get pods -o wide` ในขั้นที่ 1

```bash
kubectl describe svc web
```

**Expected output**

<pre>
Name:                     web
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.169.141
IPs:                      10.96.169.141
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
Endpoints:                10.244.2.6:80,10.244.1.3:80,10.244.2.5:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

- `Selector: app=web` = หา Pod จากป้ายนี้
- `IP: 10.96.169.141` = ที่อยู่คงที่ของ Service
- **`Endpoints`** = รายชื่อ **IP:port ของ Pod ที่ Service จะส่งงานให้** เทียบกับ `kubectl get pods -o wide` ในขั้นที่ 1: `10.244.2.6`, `10.244.2.5`, `10.244.1.3` ตรงกับ Pod ทั้ง 3 ตัว (ลำดับไม่สำคัญ)

Kubernetes เก็บรายชื่อนี้ไว้ใน object ชื่อ **EndpointSlice** ดูได้โดยตรง

```bash
kubectl get endpointslices
```

**Expected output**

<pre>
NAME         ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
kubernetes   IPv4          6443    172.19.0.4                         2m33s
web-vn2gl    IPv4          80      10.244.2.6,10.244.1.3,10.244.2.5   1s
</pre>

EndpointSlice `web-vn2gl` (ชื่อ Service + ตัวอักษรสุ่ม) ถูกสร้างให้เองพร้อม Service มี IP ของ Pod ทั้ง 3 ตัว เราไม่ต้องเขียนรายชื่อนี้เอง

### ขั้นที่ 4: Pod ลูกค้า

> 🎯 **เป้าหมายขั้นนี้:** สร้าง Pod ไว้เรียก Service จากภายในคลัสเตอร์ เพราะ ClusterIP เรียกจากนอกคลัสเตอร์ไม่ได้ ([ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร) · [ทฤษฎีหัวข้อ 10](../01_Theory/README.md#10-clusterip-ที่อยู่ภายในคลัสเตอร์))
>
> 🔍 **สังเกต:** Pod `client` ไม่มี label `app: web` จึงไม่ถูกนับเป็นปลายทางของ Service

Service แบบ ClusterIP เรียกได้จาก **ในคลัสเตอร์** เท่านั้น จึงต้องมี Pod ไว้เป็นลูกค้า ไฟล์ `labs/lab01-clusterip/client-pod.yaml`

```yaml
# LAB 1, 2: Pod ลูกค้า — busybox ที่นอนรอเฉย ๆ ให้เรา exec เข้าไปเรียก Service จากในคลัสเตอร์
apiVersion: v1
kind: Pod
metadata:
  name: client
spec:
  containers:
    - name: busybox
      image: busybox:1.37
      command: ["sleep", "3600"]   # นอนรอ 1 ชั่วโมง (มี wget และ nslookup ให้ใช้)
```

ทำงานอย่างไร

- Pod เดี่ยวชื่อ `client` จาก image `busybox` (Linux ตัวเล็กที่มีคำสั่งพื้นฐาน เช่น `wget` และ `nslookup`)
- `command: ["sleep", "3600"]` = ไม่ทำอะไร แค่นอนรอ 1 ชั่วโมง ให้เรา `kubectl exec` เข้าไปสั่งคำสั่งได้
- **ไม่มีป้าย `app: web`** Service `web` จึงไม่ส่งงานให้ Pod นี้

```bash
kubectl apply -f labs/lab01-clusterip/client-pod.yaml
```

**Expected output**

<pre>
pod/client created
</pre>

รอสัก 10 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE
client                 1/1     Running   0          10s
web-65b66cc75b-gm2pc   1/1     Running   0          11s
web-65b66cc75b-jmvlk   1/1     Running   0          11s
web-65b66cc75b-wrw8f   1/1     Running   0          11s
</pre>

### ขั้นที่ 5: เรียก Service ด้วยชื่อ

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่าเรียก **ชื่อ Service ชื่อเดียว** แล้ว request ถูกกระจายไปทุก Pod ([ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร) · [ทฤษฎีหัวข้อ 5](../01_Theory/README.md#5-service-ทำงานอย่างไร))
>
> 🔍 **สังเกต:** เรียก `http://web` (port 80) ซ้ำ ชื่อ Pod ที่ตอบเปลี่ยนไปมา ทั้งที่เรียกชื่อเดียวกันทุกครั้ง

```bash
kubectl exec client -- wget -qO- http://web
```

- `kubectl exec client -- <คำสั่ง>` = รันคำสั่งใน Pod `client` (บทที่ 2)
- `wget -qO- <url>` = ดึงหน้าเว็บแล้วพิมพ์ออกจอ (`-q` ไม่พิมพ์ความคืบหน้า, `-O-` เขียนผลออกจอ)

**สั่งซ้ำ 6 ครั้ง** (กดลูกศรขึ้นแล้ว Enter)

**Expected output** (ผลของทั้ง 6 ครั้งต่อกัน)

<pre>
Hello from Pod web-65b66cc75b-jmvlk
Hello from Pod web-65b66cc75b-jmvlk
Hello from Pod web-65b66cc75b-wrw8f
Hello from Pod web-65b66cc75b-jmvlk
Hello from Pod web-65b66cc75b-jmvlk
Hello from Pod web-65b66cc75b-wrw8f
</pre>

- เรียกที่อยู่เดียว `http://web` แต่ **ชื่อ Pod ที่ตอบเปลี่ยนไปมา** = Service **กระจาย request** ให้ Pod ใน Endpoints
- Service เลือก Pod แบบสุ่มทุกครั้งที่เปิดการเชื่อมต่อใหม่ ไม่ได้วนตามลำดับ จึงอาจได้ตัวเดิมซ้ำ (รอบนี้ `jmvlk` 4 ครั้ง `wrw8f` 2 ครั้ง ส่วน `gm2pc` ยังไม่ถูกเลือก สั่งเพิ่มอีกก็จะเจอ และขั้นที่ 7 ได้คำตอบจาก `gm2pc`)

### ขั้นที่ 6: ชื่อ web มาจากไหน (DNS)

> 🎯 **เป้าหมายขั้นนี้:** ดูว่าใครแปลชื่อ `web` เป็น ClusterIP ([ทฤษฎีหัวข้อ 7](../01_Theory/README.md#7-เรียกด้วยชื่อ-dns-ในคลัสเตอร์))
>
> 🔍 **สังเกต:** `Server: 10.96.0.10` คือ `kube-dns` และ `Address` ตรงกับ `CLUSTER-IP` ของขั้นที่ 2

ชื่อ `web` เป็นชื่อย่อ ชื่อเต็มของ Service คือ `<ชื่อ Service>.<namespace>.svc.cluster.local`

```bash
kubectl exec client -- wget -qO- http://web.default.svc.cluster.local
```

**Expected output**

<pre>
Hello from Pod web-65b66cc75b-wrw8f
</pre>

ได้ผลเหมือนกัน (`default` คือ namespace ที่เราสร้าง Service ไว้) แล้วใครแปลงชื่อเป็นที่อยู่ ถามสมุดรายชื่อด้วย `nslookup`

```bash
kubectl exec client -- nslookup web.default.svc.cluster.local
```

**Expected output**

<pre>
Server:		10.96.0.10
Address:	10.96.0.10:53

Name:	web.default.svc.cluster.local
Address: 10.96.169.141
</pre>

- `Server: 10.96.0.10` = ผู้ตอบคือ **`kube-dns`** (CoreDNS) ที่เห็นใน `kubectl get svc -A` ของ LAB 0
- `Address: 10.96.169.141` = ตรงกับ **CLUSTER-IP** ของ Service `web` ในขั้นที่ 2
- ลำดับจริงคือ `http://web` → DNS แปลงเป็น `10.96.169.141` → kube-proxy บน Node ส่งต่อไป Pod ตัวใดตัวหนึ่งใน Endpoints

### ขั้นที่ 7: เรียก Pod ด้วย IP ตรง ๆ ได้ไหม

> 🎯 **เป้าหมายขั้นนี้:** เทียบการเรียก **Pod IP ตรง ๆ** กับการเรียกผ่าน Service ([ทฤษฎีหัวข้อ 4](../01_Theory/README.md#4-ที่อยู่-3-แบบ-และ-port-4-ตัว-ศัพท์ที่ต้องแยกให้ออก))
>
> 🔍 **สังเกต:** เรียก Pod IP ได้ แต่ได้ Pod ตัวเดียวทุกครั้ง และ IP นี้ผูกอยู่กับ Pod ตัวนั้นเท่านั้น

เลือก IP ของ Pod มา 1 ตัวจาก `kubectl get pods -o wide` ในขั้นที่ 1

```bash
kubectl exec client -- wget -qO- http://10.244.2.6    # ← เปลี่ยนเป็น IP ของ Pod web ตัวหนึ่งของตัวเอง
```

**Expected output**

<pre>
Hello from Pod web-65b66cc75b-gm2pc
</pre>

ดูอีกครั้งว่า IP นี้เป็นของ Pod ไหน (`-l app=web` = เลือกเฉพาะ Pod ที่มีป้าย `app=web` จึงไม่มี `client`)

```bash
kubectl get pods -l app=web -o wide
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
web-65b66cc75b-gm2pc   1/1     Running   0          11s   10.244.2.6   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-jmvlk   1/1     Running   0          11s   10.244.2.5   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-wrw8f   1/1     Running   0          11s   10.244.1.3   lab-worker2   &lt;none&gt;           &lt;none&gt;
</pre>

`10.244.2.6` คือ `web-65b66cc75b-gm2pc` เรียกด้วย IP ของ Pod **ได้** แต่ได้ Pod ตัวเดียวทุกครั้ง และ IP นี้จะหายไปเมื่อ Pod ถูกลบหรือเปลี่ยนรุ่น (LAB 2 จะเห็น) งานจริงจึงเรียกด้วย **ชื่อ Service** เสมอ

### ขั้นที่ 8: ลบทุกอย่างของ LAB 1

> 🎯 **เป้าหมายขั้นนี้:** เก็บกวาดทุกอย่างของ LAB 1 ด้วยชื่อโฟลเดอร์
>
> 🔍 **สังเกต:** คำสั่งค้างราว 30 วินาที (Pod `client`) แล้วเหลือแค่ Service `kubernetes` ของระบบ

`kubectl delete -f` ใส่ชื่อ **โฟลเดอร์** ได้ จะลบทุกอย่างจากทุกไฟล์ในโฟลเดอร์นั้นในคำสั่งเดียว

```bash
kubectl delete -f labs/lab01-clusterip/
```

**Expected output**

<pre>
pod "client" deleted from default namespace
deployment.apps "web" deleted from default namespace
service "web" deleted from default namespace
</pre>

คำสั่งนี้ **ค้างราว 30 วินาที** เพราะ `sleep` ใน Pod `client` ไม่ตอบสัญญาณขอปิด (SIGTERM) Kubernetes จึงรอครบเวลาผ่อนผัน 30 วินาทีแล้วบังคับปิด รอสัก 5 วินาที

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    &lt;none&gt;        443/TCP   3m20s
</pre>

```bash
kubectl get pods
```

**Expected output**

<pre>
No resources found in default namespace.
</pre>

### สิ่งที่เห็น

- Service `web` (ClusterIP) ได้ **ที่อยู่คงที่** 1 อัน (`CLUSTER-IP`) และ **ชื่อ** `web` ที่ Pod อื่นใช้เรียกได้
- Service หา Pod จาก `selector` (ป้าย `app=web`) แล้วเก็บรายชื่อ IP ของ Pod ไว้ใน **Endpoints** (EndpointSlice)
- เรียก `http://web` หลายครั้ง → Pod ที่ตอบสลับกันไป = Service กระจายงาน
- ชื่อ `web` แปลงเป็น `CLUSTER-IP` ได้ด้วย **DNS ของคลัสเตอร์** (`kube-dns` ที่ `10.96.0.10`) ชื่อเต็มคือ `web.default.svc.cluster.local`

> **🤔 คำถามชวนคิด:** ถ้ารัน `kubectl delete -f labs/lab01-clusterip/web-svc.yaml` แล้ว apply ใหม่ CLUSTER-IP จะเท่าเดิมไหม แล้ว Pod `client` ที่เรียกด้วยชื่อ `http://web` ต้องแก้อะไรหรือเปล่า (ลองสังเกตใน LAB 2)

---

## LAB 2: Service หา Pod จากป้าย

<p align="center" id="fig-5">
  <img src="images/03-lab2-endpoints-labels.png" alt="รูปที่ 5 LAB2 Endpoints ตาม label และกับดัก 2 แบบ" width="900"><br>
  <em><b>รูปที่ 5</b> LAB2 (ค่าจริงจากการทดลอง): แถวบน Endpoints ของ Service web เปลี่ยนเองทุกครั้งที่ลบ Pod ถอด label หรือ scale (เขียว = เข้ารายชื่อ แดง = ออกจากรายชื่อ) ส่วน ClusterIP 10.96.62.215 ไม่เปลี่ยน แถวล่าง กับดัก 2 แบบที่ได้ Connection refused เหมือนกัน: selector ผิดทำให้ Endpoints ว่าง และ targetPort ผิดทำให้ Endpoints มีครบแต่ชี้ไปที่ port 8080 ที่ nginx ไม่ได้ฟัง</em>
</p>

**เป้าหมาย:** ดูว่า Endpoints ของ Service เปลี่ยนตาม Pod เองเมื่อ Pod ถูกลบ ถูกถอดป้าย หรือเพิ่มจำนวน และเจอกับดักที่พบบ่อยที่สุด: พิมพ์ป้ายใน `selector` ผิด

<p align="center" id="fig-6">
  <img src="images/03a-lab2-plan.png" alt="รูปที่ 6 แผนการทดลอง LAB2" width="900"><br>
  <em><b>รูปที่ 6</b> แผนการทดลอง LAB2 มี 4 การทดลอง: (1) ขั้นที่ 1–2 ลบ Pod แล้ว Endpoints เปลี่ยนเอง ClusterIP เดิม (2) ขั้นที่ 3 ถอด label แล้ว Pod หลุดจาก Endpoints ทั้งที่ยัง Running (3) ขั้นที่ 4 scale เป็น 5 แล้ว Endpoints เพิ่มเอง (4) ขั้นที่ 5–7 กับดัก selector ผิด (Endpoints ว่าง) และ targetPort ผิด (Endpoints ครบแต่ต่อไม่ติด)</em>
</p>

### ขั้นที่ 1: สร้างทุกอย่างจากโฟลเดอร์เดียว

> 🎯 **เป้าหมายขั้นนี้:** สร้าง Service จากไฟล์เดิมอีกครั้ง แล้วดูว่าได้ ClusterIP ใหม่ ส่วนชื่อเหมือนเดิม ([ทฤษฎีหัวข้อ 10](../01_Theory/README.md#10-clusterip-ที่อยู่ภายในคลัสเตอร์))
>
> 🔍 **สังเกต:** `IP` เป็น `10.96.62.215` ไม่ใช่ `10.96.169.141` ของ LAB 1 และ Endpoints ไม่มี IP ของ Pod `client`

`kubectl apply -f` ใส่ชื่อโฟลเดอร์ได้เหมือน `delete` จะสร้าง Deployment, Service และ Pod client จากไฟล์ทั้ง 3 ใน LAB 1 พร้อมกัน

```bash
kubectl apply -f labs/lab01-clusterip/
```

**Expected output**

<pre>
pod/client created
deployment.apps/web created
service/web created
</pre>

รอจน Pod web พร้อมครบ

```bash
kubectl rollout status deployment/web
```

**Expected output**

<pre>
Waiting for deployment "web" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 2 of 3 updated replicas are available...
deployment "web" successfully rolled out
</pre>

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
client                 1/1     Running   0          6s    10.244.2.8    lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-mtg6r   1/1     Running   0          6s    10.244.1.4    lab-worker2   &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-r9wlj   1/1     Running   0          6s    10.244.2.10   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-wmdll   1/1     Running   0          6s    10.244.2.9    lab-worker    &lt;none&gt;           &lt;none&gt;
</pre>

```bash
kubectl describe svc web
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
Name:                     web
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.62.215
IPs:                      10.96.62.215
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
Endpoints:                10.244.1.4:80,10.244.2.9:80,10.244.2.10:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

Service สร้างใหม่จึงได้ IP ใหม่ `10.96.62.215` (ไม่ใช่ `10.96.169.141` ของ LAB 1) แต่ชื่อยังเป็น `web` เหมือนเดิม Endpoints มี IP ของ Pod web ทั้ง 3 ตัว (ไม่มี `client` `10.244.2.8` เพราะไม่มีป้าย `app=web`)

### ขั้นที่ 2: ลบ Pod แล้ว Endpoints เปลี่ยนเอง

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า **ลบ Pod แล้ว Endpoints อัปเดตเอง** โดยไม่ต้องแก้ Service ([ทฤษฎีหัวข้อ 8](../01_Theory/README.md#8-service-หา-pod-จากป้าย))
>
> 🔍 **สังเกต:** IP ของ Pod ที่ถูกลบหายไป IP ของ Pod ใหม่เข้ามาแทน ส่วน `IP` ของ Service ไม่เปลี่ยน

```bash
kubectl delete pod web-65b66cc75b-mtg6r    # ← เปลี่ยนเป็นชื่อ Pod web ตัวหนึ่งของตัวเอง
```

**Expected output**

<pre>
pod "web-65b66cc75b-mtg6r" deleted from default namespace
</pre>

รอสัก 5 วินาที

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
client                 1/1     Running   0          12s   10.244.2.8    lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-fm44v   1/1     Running   0          6s    10.244.1.5    lab-worker2   &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-r9wlj   1/1     Running   0          12s   10.244.2.10   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-wmdll   1/1     Running   0          12s   10.244.2.9    lab-worker    &lt;none&gt;           &lt;none&gt;
</pre>

ReplicaSet สร้าง `web-65b66cc75b-fm44v` มาแทน (บทที่ 3) และได้ **IP ใหม่ `10.244.1.5`** (ตัวที่ถูกลบคือ `10.244.1.4`)

```bash
kubectl describe svc web
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
Name:                     web
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.62.215
IPs:                      10.96.62.215
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
Endpoints:                10.244.2.9:80,10.244.2.10:80,10.244.1.5:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

`10.244.1.4` หายไป และ `10.244.1.5` เข้ามาแทนใน Endpoints **เอง** ส่วน IP ของ Service (`10.96.62.215`) ไม่เปลี่ยน ลูกค้าที่เรียก `http://web` ไม่ต้องรู้เลยว่า Pod เปลี่ยนตัว

### ขั้นที่ 3: ถอดป้ายออกจาก Pod

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า Service เลือก Pod **จาก label เท่านั้น** ([ทฤษฎีหัวข้อ 8](../01_Theory/README.md#8-service-หา-pod-จากป้าย))
>
> 🔍 **สังเกต:** Pod ที่ถอด label ยัง `Running` แต่หายจาก Endpoints และไม่ได้รับ request เลยใน 4 ครั้ง

`kubectl label pod <ชื่อ> app-` = **ลบป้าย** `app` ออกจาก Pod (ชื่อป้ายตามด้วย `-`) ลองถอดป้ายจาก Pod ที่เพิ่งเกิดใหม่

```bash
kubectl label pod web-65b66cc75b-fm44v app-    # ← เปลี่ยนเป็นชื่อ Pod web ตัวหนึ่งของตัวเอง
```

**Expected output**

<pre>
pod/web-65b66cc75b-fm44v unlabeled
</pre>

รอสัก 5 วินาที

```bash
kubectl get pods -o wide --show-labels
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES   LABELS
client                 1/1     Running   0          17s   10.244.2.8    lab-worker    &lt;none&gt;           &lt;none&gt;            &lt;none&gt;
web-65b66cc75b-fm44v   1/1     Running   0          11s   10.244.1.5    lab-worker2   &lt;none&gt;           &lt;none&gt;            pod-template-hash=65b66cc75b
web-65b66cc75b-r9wlj   1/1     Running   0          17s   10.244.2.10   lab-worker    &lt;none&gt;           &lt;none&gt;            app=web,pod-template-hash=65b66cc75b
web-65b66cc75b-rxwr5   1/1     Running   0          5s    10.244.1.6    lab-worker2   &lt;none&gt;           &lt;none&gt;            app=web,pod-template-hash=65b66cc75b
web-65b66cc75b-wmdll   1/1     Running   0          17s   10.244.2.9    lab-worker    &lt;none&gt;           &lt;none&gt;            app=web,pod-template-hash=65b66cc75b
</pre>

- `fm44v` เหลือแค่ป้าย `pod-template-hash` แต่ **ยัง Running** อยู่
- ReplicaSet นับ Pod จากป้าย `app=web` เหลือ 2 ตัว จึงสร้าง `rxwr5` (`10.244.1.6`) มาเติมให้ครบ 3 (เหมือนบทที่ 3)

```bash
kubectl describe svc web
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
Name:                     web
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.62.215
IPs:                      10.96.62.215
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
Endpoints:                10.244.2.9:80,10.244.2.10:80,10.244.1.6:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

`10.244.1.5` (Pod `fm44v` ที่ถอดป้าย) **หลุดออกจาก Endpoints** แม้จะยัง Running และ `10.244.1.6` (`rxwr5`) เข้ามาแทน ลองเรียก Service

```bash
kubectl exec client -- wget -qO- http://web
```

**สั่งซ้ำ 4 ครั้ง**

**Expected output** (ผลของทั้ง 4 ครั้งต่อกัน)

<pre>
Hello from Pod web-65b66cc75b-r9wlj
Hello from Pod web-65b66cc75b-wmdll
Hello from Pod web-65b66cc75b-r9wlj
Hello from Pod web-65b66cc75b-wmdll
</pre>

ไม่มี `fm44v` เลย Service ส่งงานให้ **เฉพาะ Pod ที่ป้ายตรงกับ selector** เท่านั้น ไม่สนว่า Pod จะ Running อยู่หรือมาจาก Deployment ไหน

### ขั้นที่ 4: ลบ Pod ที่ถอดป้าย แล้วเพิ่มเป็น 5 ตัว

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า **scale แล้ว Endpoints เพิ่มตาม** โดยไม่ต้องแก้ Service ([ทฤษฎีหัวข้อ 8](../01_Theory/README.md#8-service-หา-pod-จากป้าย))
>
> 🔍 **สังเกต:** `Endpoints` แสดง 3 ตัวแรกตามด้วย `+ 2 more...` รวมเป็น 5 ตามจำนวน Pod

Pod `fm44v` ไม่มีใครดูแลแล้ว (ReplicaSet ไม่นับ Service ไม่ส่งงาน) ลบทิ้ง

```bash
kubectl delete pod web-65b66cc75b-fm44v    # ← เปลี่ยนเป็นชื่อ Pod ที่ถอดป้ายของตัวเอง
```

**Expected output**

<pre>
pod "web-65b66cc75b-fm44v" deleted from default namespace
</pre>

```bash
kubectl scale deployment web --replicas=5
```

**Expected output**

<pre>
deployment.apps/web scaled
</pre>

รอสัก 5 วินาที

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
client                 1/1     Running   0          23s   10.244.2.8    lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-5g6zf   1/1     Running   0          5s    10.244.1.7    lab-worker2   &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-mzbfz   1/1     Running   0          5s    10.244.2.11   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-r9wlj   1/1     Running   0          23s   10.244.2.10   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-rxwr5   1/1     Running   0          11s   10.244.1.6    lab-worker2   &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-wmdll   1/1     Running   0          23s   10.244.2.9    lab-worker    &lt;none&gt;           &lt;none&gt;
</pre>

```bash
kubectl describe svc web
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
Name:                     web
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.62.215
IPs:                      10.96.62.215
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
Endpoints:                10.244.2.9:80,10.244.2.10:80,10.244.1.6:80 + 2 more...
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

`+ 2 more...` = `describe` แสดงแค่ 3 ตัวแรก แล้วบอกว่ายังมีอีก 2 รวมเป็น **5** ตามจำนวน Pod Pod ใหม่ (`10.244.1.7`, `10.244.2.11`) เข้ารายชื่อเองทันทีที่พร้อม ไม่ต้องแก้ Service เลย

### ขั้นที่ 5: กับดัก — พิมพ์ป้ายใน selector ผิด

> 🎯 **เป้าหมายขั้นนี้:** เจอกับดัก **selector พิมพ์ผิด** และฝึกตรวจจากบรรทัด `Endpoints` ([ทฤษฎีหัวข้อ 9](../01_Theory/README.md#9-กับดัก-selector-พิมพ์ผิด-แล้ว-endpoints-ว่าง))
>
> 🔍 **สังเกต:** apply ผ่านและได้ `CLUSTER-IP` ปกติ แต่ `Endpoints:` ว่าง เรียกแล้วได้ `Connection refused`

ไฟล์ `labs/lab02-selector/web-svc-typo.yaml`

```yaml
# LAB 2: Service ที่พิมพ์ป้ายผิด — selector หา Pod ไม่เจอ จึงไม่มีใครรับงาน
apiVersion: v1
kind: Service
metadata:
  name: web-typo
spec:
  selector:
    app: wbe                 # ← พิมพ์ผิด (ที่ถูกคือ web) ไม่มี Pod ไหนติดป้ายนี้
  ports:
    - port: 80
      targetPort: 80
```

ทำงานอย่างไร

- Service ชื่อ `web-typo` ไม่ได้เขียน `type` จึงเป็น **ClusterIP** (ค่าเริ่มต้น)
- `selector: app: wbe` **พิมพ์สลับตัวอักษร** (ที่ถูกคือ `web`) ไม่มี Pod ไหนติดป้ายนี้

```bash
kubectl apply -f labs/lab02-selector/web-svc-typo.yaml
```

**Expected output**

<pre>
service/web-typo created
</pre>

Kubernetes **ไม่เตือนอะไรเลย** สร้างให้ตามปกติ

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1      &lt;none&gt;        443/TCP   3m43s
web          ClusterIP   10.96.62.215   &lt;none&gt;        80/TCP    23s
web-typo     ClusterIP   10.96.62.39    &lt;none&gt;        80/TCP    0s
</pre>

`web-typo` ได้ `CLUSTER-IP` และ port ปกติทุกอย่าง ดูจากตรงนี้ไม่รู้เลยว่าผิด

```bash
kubectl describe svc web-typo
```

**Expected output**

<pre>
Name:                     web-typo
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=wbe
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.62.39
IPs:                      10.96.62.39
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
Endpoints:                
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

**`Endpoints:` ว่างเปล่า** = selector `app=wbe` หา Pod ไม่เจอสักตัว ลองเรียกดู

```bash
kubectl exec client -- wget -qO- http://web-typo
```

**Expected output**

<pre>
wget: can't connect to remote host (10.96.62.39): Connection refused
command terminated with exit code 1
</pre>

ชื่อ `web-typo` แปลงเป็น IP `10.96.62.39` ได้ (DNS ทำงาน) แต่ไม่มี Pod ให้ส่งต่อ จึงได้ **`Connection refused`** เวลาเรียก Service แล้วต่อไม่ได้ ให้ตรวจ **Endpoints** ด้วย `kubectl describe svc` เป็นอย่างแรก ถ้าว่าง = selector ไม่ตรงกับป้ายของ Pod

### ขั้นที่ 6: กับดักที่ 2 — targetPort ไม่ตรงกับ port ของแอป

> 🎯 **เป้าหมายขั้นนี้:** เจอกับดัก **targetPort ผิด** ซึ่งต่างจาก selector ผิด: label ถูก Endpoints จึงมีครบ แต่ request ถูกส่งไปที่ port ที่แอปไม่ได้ฟัง ([ทฤษฎีหัวข้อ 4](../01_Theory/README.md#4-ที่อยู่-3-แบบ-และ-port-4-ตัว-ศัพท์ที่ต้องแยกให้ออก) · [ทฤษฎีหัวข้อ 9](../01_Theory/README.md#9-กับดัก-selector-พิมพ์ผิด-แล้ว-endpoints-ว่าง))
>
> 🔍 **สังเกต:** `Endpoints` มีครบ 5 ตัวแต่ลงท้ายด้วย `:8080` และเรียกแล้วได้ `Connection refused` เหมือนขั้นที่ 5

ไฟล์ `labs/lab02-selector/web-svc-wrongport.yaml`

```yaml
# LAB 2: Service ที่ targetPort ผิด — selector ถูก Endpoints จึงมีครบ แต่ส่ง request ไปที่ port ที่ nginx ไม่ได้ฟัง
apiVersion: v1
kind: Service
metadata:
  name: web-wrongport
spec:
  selector:
    app: web                 # label ถูกต้อง Endpoints จึงมี Pod ครบ
  ports:
    - port: 80
      targetPort: 8080       # ← ผิด: nginx ใน Pod ฟังที่ port 80 (containerPort: 80) ไม่ใช่ 8080
```

ทำงานอย่างไร

- `selector: app: web` **ถูกต้อง** Service จึงหา Pod เจอครบ
- `targetPort: 8080` **ผิด** เพราะ nginx ใน Pod ฟังที่ port 80 (`containerPort: 80` ใน `web-deploy.yaml`) ทฤษฎีหัวข้อ 4: `targetPort` ต้องเท่ากับ `containerPort` เสมอ

```bash
kubectl apply -f labs/lab02-selector/web-svc-wrongport.yaml
```

**Expected output**

<pre>
service/web-wrongport created
</pre>

```bash
kubectl describe svc web-wrongport
```

**Expected output**

<pre>
Name:                     web-wrongport
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.192.168
IPs:                      10.96.192.168
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               8080/TCP
Endpoints:                10.244.2.11:8080,10.244.1.6:8080,10.244.1.7:8080 + 2 more...
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

`Endpoints` **มีครบ** ต่างจาก `web-typo` แต่ทุกตัวลงท้ายด้วย `:8080` ซึ่งไม่มีแอปไหนฟังอยู่ ลองเรียกดู

```bash
kubectl exec client -- wget -qO- http://web-wrongport
```

**Expected output** (อาจค้างราว 20 วินาทีก่อนขึ้นผล)

<pre>
wget: can't connect to remote host (10.96.192.168): Connection refused
command terminated with exit code 1
</pre>

ได้ `Connection refused` เหมือนขั้นที่ 5 แต่สาเหตุคนละอย่าง แยกได้จาก `kubectl describe svc` ตามลำดับในทฤษฎีหัวข้อ 9

- `Endpoints:` **ว่าง** = selector ไม่ตรงกับ label ของ Pod (ขั้นที่ 5) แก้ที่ `selector`
- `Endpoints` **มีครบ** แต่ต่อไม่ติด = `targetPort` ไม่ตรงกับ port ที่แอปฟัง (ขั้นที่ 6) แก้ `targetPort` ให้เท่ากับ `containerPort`

### ขั้นที่ 7: ลบทุกอย่างของ LAB 2

> 🎯 **เป้าหมายขั้นนี้:** เก็บกวาด Service ทั้ง 2 ตัว Deployment และ Pod `client`
>
> 🔍 **สังเกต:** `get pods` ขึ้น `No resources found`

ลบ Service ทั้ง 2 ตัวในโฟลเดอร์ `lab02-selector` ในคำสั่งเดียว

```bash
kubectl delete -f labs/lab02-selector/
```

**Expected output**

<pre>
service "web-typo" deleted from default namespace
service "web-wrongport" deleted from default namespace
</pre>

```bash
kubectl delete -f labs/lab01-clusterip/
```

**Expected output** (ค้างราว 30 วินาทีเหมือน LAB 1)

<pre>
pod "client" deleted from default namespace
deployment.apps "web" deleted from default namespace
service "web" deleted from default namespace
</pre>

รอสัก 5 วินาที

```bash
kubectl get pods
```

**Expected output**

<pre>
No resources found in default namespace.
</pre>

ไฟล์ Deployment ยังเขียน `replicas: 3` แต่ไม่เป็นไร `delete -f` ลบตามชื่อ Deployment จึงลบทั้ง 5 ตัวที่ scale ไว้

### สิ่งที่เห็น

- Endpoints **อัปเดตเอง** ทุกครั้งที่ Pod เปลี่ยน: ลบ Pod → IP เก่าออก IP ใหม่เข้า, scale เพิ่ม → IP ใหม่เข้า ส่วน IP และชื่อของ Service ไม่เปลี่ยน
- Service เลือก Pod **จากป้ายเท่านั้น** ถอดป้าย `app` ออก Pod ก็หลุดจาก Endpoints ทันทีแม้ยัง Running (และ ReplicaSet สร้างตัวใหม่มาแทน เพราะนับจากป้ายเหมือนกัน)
- `describe svc` แสดง Endpoints แค่ 3 ตัวแรก ที่เหลือเป็น `+ N more...`
- selector พิมพ์ผิด → Service มี IP ปกติแต่ **Endpoints ว่าง** เรียกแล้วได้ `Connection refused`
- targetPort ผิด → **Endpoints มีครบ** แต่ลงท้ายด้วย port ที่แอปไม่ได้ฟัง ก็ได้ `Connection refused` เหมือนกัน วิธีแยกคือดู `kubectl describe svc` ว่า Endpoints ว่างหรือมีครบ

> **🤔 คำถามชวนคิด:** ถ้าสร้าง Pod เดี่ยวอีกตัวที่ติดป้าย `app: web` เอง (ไม่ได้มาจาก Deployment `web`) Service `web` จะส่งงานให้ Pod นั้นด้วยหรือไม่ เพราะอะไร

---

## LAB 3: NodePort: เปิดประตูให้คนนอกคลัสเตอร์

<p align="center" id="fig-7">
  <img src="images/04-lab3-nodeport.png" alt="รูปที่ 7 LAB3 NodePort 30080 บน Node ทุกตัว" width="900"><br>
  <em><b>รูปที่ 7</b> LAB3 (ค่าจริงจากการทดลอง): Service web-nodeport เปิด nodePort 30080 บน Node ทั้ง 3 ตัว request จาก curl หรือ browser เข้าทาง Node ไหนก็ได้ ส่งต่อไปที่ Service (ClusterIP 10.96.231.50 port 80) แล้วไป Pod ที่ targetPort 80 แม้ Node นั้น (lab-control-plane) จะไม่มี Pod web อยู่เลย</em>
</p>

**เป้าหมาย:** ClusterIP เรียกได้แค่ในคลัสเตอร์ คราวนี้ใช้ Service แบบ **NodePort** เปิด port `30080` บนทุก Node ให้ curl และ browser จากนอกคลัสเตอร์เข้าถึง Pod ได้ โดยไม่ต้องใช้ port-forward

<p align="center" id="fig-8">
  <img src="images/04a-lab3-plan.png" alt="รูปที่ 8 แผนการทดลอง LAB3" width="900"><br>
  <em><b>รูปที่ 8</b> แผนการทดลอง LAB3 มี 4 การทดลอง: (1) ขั้นที่ 1–2 เปลี่ยน type เป็น NodePort ยังมี ClusterIP และได้ nodePort 30080 เพิ่ม (2) ขั้นที่ 3 เรียก localhost:30080 จากนอกคลัสเตอร์ (3) ขั้นที่ 4–5 nodePort เปิดบน Node ทุกตัว และเปิดจาก browser ได้ (4) ขั้นที่ 6–7 ลอง type LoadBalancer ได้ EXTERNAL-IP pending แต่ nodePort ใช้ได้ แล้วเก็บกวาด</em>
</p>

### ขั้นที่ 1: สร้าง Pod nginx 3 ตัว

> 🎯 **เป้าหมายขั้นนี้:** เตรียม Pod 3 ตัวเดิม และจดไว้ว่า Pod ไหนอยู่ Node ไหน ([ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node))
>
> 🔍 **สังเกต:** Pod อยู่บน `lab-worker` และ `lab-worker2` ไม่มี Pod บน `lab-control-plane`

ใช้ไฟล์ Deployment เดิมของ LAB 1

```bash
kubectl apply -f labs/lab01-clusterip/web-deploy.yaml
```

**Expected output**

<pre>
deployment.apps/web created
</pre>

```bash
kubectl rollout status deployment/web
```

**Expected output**

<pre>
Waiting for deployment "web" rollout to finish: 0 out of 3 new replicas have been updated...
Waiting for deployment "web" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 3 updated replicas are available...
Waiting for deployment "web" rollout to finish: 2 of 3 updated replicas are available...
deployment "web" successfully rolled out
</pre>

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
web-65b66cc75b-qpmms   1/1     Running   0          1s    10.244.2.12   lab-worker    &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-xrcb5   1/1     Running   0          1s    10.244.1.8    lab-worker2   &lt;none&gt;           &lt;none&gt;
web-65b66cc75b-z6qjn   1/1     Running   0          1s    10.244.2.13   lab-worker    &lt;none&gt;           &lt;none&gt;
</pre>

**จดไว้ว่า Pod ไหนอยู่ Node ไหน** จะใช้ในขั้นที่ 4

### ขั้นที่ 2: Service แบบ NodePort

> 🎯 **เป้าหมายขั้นนี้:** เปลี่ยน `type` เป็น **NodePort** แล้วดูว่าได้อะไรเพิ่มจาก ClusterIP ([ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร) · [ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node))
>
> 🔍 **สังเกต:** ยังมี `CLUSTER-IP` อยู่ `PORT(S)` เป็น `80:30080/TCP` และมีบรรทัด `NodePort: 30080/TCP` เพิ่มจาก LAB 1

ไฟล์ `labs/lab03-nodeport/web-svc-nodeport.yaml`

```yaml
# LAB 3: Service แบบ NodePort — เปิดประตู 30080 บนทุก Node ให้คนนอกคลัสเตอร์เข้าถึงได้
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort             # ← ใหม่: ได้ทั้ง ClusterIP และ port บนทุก Node
  selector:
    app: web
  ports:
    - port: 80               # port ของ Service ในคลัสเตอร์
      targetPort: 80         # port ของ container
      nodePort: 30080        # ← ใหม่: port บนทุก Node (ต้องอยู่ในช่วง 30000–32767) แล็บนี้ map ออกมาถึงเครื่องเราแล้ว
```

ทำงานอย่างไร

- ต่างจาก `web-svc.yaml` ของ LAB 1 แค่ **2 บรรทัดที่มี `← ใหม่`** (และชื่อ `web-nodeport`)
- `type: NodePort` = ได้ทุกอย่างของ ClusterIP (IP ภายใน + ชื่อ) **บวก** port บน **ทุก Node** ของคลัสเตอร์
- `nodePort: 30080` = เลข port บน Node ต้องอยู่ในช่วง `30000–32767` (ถ้าไม่เขียน Kubernetes จะสุ่มให้) ที่เลือก 30080 เพราะเป็น port ที่ LAB 0 map ออกมาถึงเครื่องเราไว้แล้ว
- เส้นทาง: `<IP ของ Node ไหนก็ได้>:30080` → `port: 80` ของ Service → `targetPort: 80` ของ Pod

```bash
kubectl apply -f labs/lab03-nodeport/web-svc-nodeport.yaml
```

**Expected output**

<pre>
service/web-nodeport created
</pre>

รอสัก 5 วินาที

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME           TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes     ClusterIP   10.96.0.1      &lt;none&gt;        443/TCP        5m4s
web-nodeport   NodePort    10.96.231.50   &lt;none&gt;        80:30080/TCP   5s
</pre>

- `TYPE NodePort` แต่ **ยังมี `CLUSTER-IP`** (`10.96.231.50`) Pod ในคลัสเตอร์ยังเรียกด้วยชื่อ `web-nodeport` ได้เหมือน LAB 1
- `PORT(S) 80:30080/TCP` = port `80` ของ Service และ port **`30080` บน Node**

```bash
kubectl describe svc web-nodeport
```

**Expected output**

<pre>
Name:                     web-nodeport
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     NodePort
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.231.50
IPs:                      10.96.231.50
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
NodePort:                 &lt;unset&gt;  30080/TCP
Endpoints:                10.244.2.12:80,10.244.1.8:80,10.244.2.13:80
Session Affinity:         None
External Traffic Policy:  Cluster
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

มีบรรทัด **`NodePort: 30080/TCP`** เพิ่มจาก LAB 1 ส่วน `Endpoints` ยังเป็น IP ของ Pod 3 ตัวตามป้าย `app=web` เหมือนเดิม

### ขั้นที่ 3: เรียกจากนอกคลัสเตอร์ด้วย curl

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า **เครื่องนอกคลัสเตอร์** เรียก Service ผ่าน nodePort ได้ ([ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node))
>
> 🔍 **สังเกต:** ได้คำตอบจาก Pod ทั้ง 3 ตัว แม้ request เข้าทาง `lab-control-plane` ที่ไม่มี Pod อยู่เลย

ตอนนี้เราอยู่ใน container `k8s-lab` ซึ่ง **อยู่นอกคลัสเตอร์** (คลัสเตอร์คือ Node 3 ตัวที่ kind สร้างไว้ข้างใน) `localhost:30080` ของ k8s-lab ถูก map ไปที่ port 30080 ของ Node `lab-control-plane` ตั้งแต่ `k8s-up`

```bash
curl http://localhost:30080
```

**สั่งซ้ำ 4 ครั้ง**

**Expected output** (ผลของทั้ง 4 ครั้งต่อกัน)

<pre>
Hello from Pod web-65b66cc75b-xrcb5
Hello from Pod web-65b66cc75b-z6qjn
Hello from Pod web-65b66cc75b-z6qjn
Hello from Pod web-65b66cc75b-z6qjn
</pre>

request เข้าทาง nodePort ของ `lab-control-plane` ซึ่ง **ไม่มี Pod web อยู่เลย** แต่ยังได้คำตอบจาก Pod บน Node worker สลับกัน (`xrcb5` บน `lab-worker2`, `z6qjn` บน `lab-worker`) เพราะ kube-proxy บน Node นั้นส่งต่อให้

### ขั้นที่ 4: ประตูเปิดบนทุก Node

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า **nodePort เปิดบน Node ทุกตัว** ([ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node))
>
> 🔍 **สังเกต:** Node ทั้ง 2 ตัวตอบ และ Pod ที่ตอบอาจอยู่คนละ Node กับ Node IP ที่เรียก

ดู IP ของ Node แต่ละตัว

```bash
kubectl get nodes -o wide
```

**Expected output**

<pre>
NAME                STATUS   ROLES           AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   5m4s    v1.37.0   172.19.0.4    &lt;none&gt;        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker          Ready    &lt;none&gt;          4m51s   v1.37.0   172.19.0.2    &lt;none&gt;        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker2         Ready    &lt;none&gt;          4m51s   v1.37.0   172.19.0.3    &lt;none&gt;        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
</pre>

`INTERNAL-IP` คือ IP ของ Node แต่ละตัว ลองเคาะประตู 30080 ของ `lab-worker` ตรง ๆ

```bash
curl http://172.19.0.2:30080    # ← เปลี่ยนเป็น INTERNAL-IP ของ lab-worker ของตัวเอง
```

**สั่งซ้ำ 3 ครั้ง**

**Expected output** (ผลของทั้ง 3 ครั้งต่อกัน)

<pre>
Hello from Pod web-65b66cc75b-z6qjn
Hello from Pod web-65b66cc75b-xrcb5
Hello from Pod web-65b66cc75b-xrcb5
</pre>

แล้วประตูของ `lab-worker2`

```bash
curl http://172.19.0.3:30080    # ← เปลี่ยนเป็น INTERNAL-IP ของ lab-worker2 ของตัวเอง
```

**สั่งซ้ำ 3 ครั้ง**

**Expected output** (ผลของทั้ง 3 ครั้งต่อกัน)

<pre>
Hello from Pod web-65b66cc75b-z6qjn
Hello from Pod web-65b66cc75b-xrcb5
Hello from Pod web-65b66cc75b-z6qjn
</pre>

- ทั้ง 2 Node ตอบได้ = **NodePort เปิด port เดียวกันบนทุก Node** (รวม `lab-control-plane` ในขั้นที่ 3)
- เข้าประตู `lab-worker` แต่ได้ `xrcb5` ที่อยู่บน **`lab-worker2`** และเข้าประตู `lab-worker2` แต่ได้ `z6qjn` ที่อยู่บน **`lab-worker`** (เทียบกับขั้นที่ 1) = เข้าประตูไหนก็ส่งไปได้ทุก Pod ใน Endpoints

### ขั้นที่ 5: เปิดด้วย browser บนเครื่องนักศึกษา

> 🎯 **เป้าหมายขั้นนี้:** เปิดแอปจาก browser บนเครื่องเรา โดยไม่ใช้ port-forward ([ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node))
>
> 🔍 **สังเกต:** หน้าเว็บขึ้น `Hello from Pod ...` ที่ `http://localhost:30080`

🌐 เปิด browser บนเครื่องนักศึกษา ไปที่ `http://localhost:30080`

<p align="center" id="fig-9">
  <img src="images/screenshots/20261019_lab3_01-nodeport-browser.png" alt="รูปที่ 9 ภาพหน้าจอจริง nginx ผ่าน NodePort" width="500"><br>
  <em><b>รูปที่ 9</b> ภาพหน้าจอจริงจากการทดลอง: browser เปิด http://localhost:30080 เห็น Hello from Pod web-65b66cc75b-qpmms ผ่าน Service web-nodeport (ทดสอบ 19 ต.ค. 2569 ด้วย browser จริงบนเครื่อง host ตอนถ่าย container ทดลอง map port 30080 ไปที่ port อื่นของ host นักศึกษาเปิด http://localhost:30080 ตรง ๆ หน้าเว็บที่เห็นเหมือนกัน)</em>
</p>

เส้นทางคือ browser → port 30080 ของเครื่องเรา (`-p 30080-30082:30080-30082` ตอน `docker run`) → port 30080 ของ k8s-lab → port 30080 ของ Node `lab-control-plane` (`k8s-up` map ไว้) → kube-proxy → Pod **ไม่ต้องใช้ port-forward และไม่ต้องเปิดค้างไว้**

กด refresh แล้วมักได้ **ชื่อ Pod เดิม** เพราะ browser ใช้การเชื่อมต่อเดิมซ้ำ (keep-alive) และ Service เลือก Pod ตอน **เปิดการเชื่อมต่อใหม่** เท่านั้น แอปน้องส้มใน LAB 4 แก้เรื่องนี้ไว้แล้ว

### ขั้นที่ 6: ลองแบบ LoadBalancer บน kind

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า **LoadBalancer = NodePort + load balancer ของคลาวด์** บน kind ที่ไม่มีคลาวด์ ส่วน load balancer ไม่มา แต่ส่วน NodePort ยังใช้ได้ ([ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร))
>
> 🔍 **สังเกต:** `EXTERNAL-IP` เป็น `<pending>` ตลอด `PORT(S)` ได้ nodePort ที่ระบบสุ่มให้ และเรียก `<Node IP>:<nodePort นั้น>` ได้จริง

ไฟล์ `labs/lab03-nodeport/web-svc-lb.yaml`

```yaml
# LAB 3: Service แบบ LoadBalancer — บน kind ไม่มี load balancer ของคลาวด์ EXTERNAL-IP จึงค้างเป็น <pending> แต่ nodePort ใช้ได้
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  type: LoadBalancer         # ← ใหม่: NodePort + ขอ load balancer จากผู้ให้บริการคลาวด์
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
      # ไม่เขียน nodePort ระบบสุ่มให้
```

ทำงานอย่างไร

- ต่างจาก `web-svc-nodeport.yaml` แค่ `type: LoadBalancer` (และชื่อ `web-lb`) กับไม่ได้เขียน `nodePort`
- `type: LoadBalancer` = ได้ทุกอย่างของ NodePort **บวก** ขอให้ผู้ให้บริการคลาวด์สร้าง load balancer ที่มี IP สาธารณะ (`EXTERNAL-IP`) ให้
- ไม่เขียน `nodePort` Kubernetes จึงสุ่มเลขในช่วง 30000–32767 ให้ (เลขนี้ไม่ได้ map ออกมาถึงเครื่องเรา เรียกได้จากใน k8s-lab เท่านั้น)

```bash
kubectl apply -f labs/lab03-nodeport/web-svc-lb.yaml
```

**Expected output**

<pre>
service/web-lb created
</pre>

รอสัก 10 วินาที

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME           TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes     ClusterIP      10.96.0.1      &lt;none&gt;        443/TCP        5m49s
web-lb         LoadBalancer   10.96.28.234   &lt;pending&gt;     80:31484/TCP   11s
web-nodeport   NodePort       10.96.231.50   &lt;none&gt;        80:30080/TCP   50s
</pre>

- `web-lb` เป็น `TYPE LoadBalancer` มี `CLUSTER-IP` เหมือนแบบอื่น
- **`EXTERNAL-IP <pending>`** = รอผู้ให้บริการคลาวด์สร้าง load balancer ให้ บน kind จะค้างอย่างนี้ตลอด
- `PORT(S) 80:31484/TCP` = มี nodePort `31484` ที่ระบบสุ่มให้ (เลขในเครื่องนักศึกษาจะต่างไป)

```bash
kubectl describe svc web-lb
```

**Expected output**

<pre>
Name:                     web-lb
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=web
Type:                     LoadBalancer
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.28.234
IPs:                      10.96.28.234
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               80/TCP
NodePort:                 &lt;unset&gt;  31484/TCP
Endpoints:                10.244.2.13:80,10.244.2.12:80,10.244.1.8:80
Session Affinity:         None
External Traffic Policy:  Cluster
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

ลองเรียกผ่าน nodePort ที่สุ่มได้ ที่ Node `lab-worker`

```bash
curl http://172.19.0.2:31484    # ← เปลี่ยนเป็น INTERNAL-IP ของ lab-worker และ nodePort ของ web-lb ของตัวเอง
```

**Expected output**

<pre>
Hello from Pod web-65b66cc75b-z6qjn
</pre>

ได้คำตอบจาก Pod แม้ `EXTERNAL-IP` ยัง `<pending>` แปลว่าข้างใน LoadBalancer คือ NodePort ที่ใช้งานได้แล้ว ส่วนที่ขาดไปมีแค่ load balancer ของคลาวด์ ตรงกับภาพชั้นซ้อนในทฤษฎีหัวข้อ 3 (ClusterIP ⊂ NodePort ⊂ LoadBalancer)

### ขั้นที่ 7: ลบ Service และ Deployment

> 🎯 **เป้าหมายขั้นนี้:** เก็บกวาด Service และ Deployment ของ LAB 3
>
> 🔍 **สังเกต:** เหลือแค่ Service `kubernetes` และ `No resources found`

ลบ Service ทั้ง 2 ตัวในโฟลเดอร์ `lab03-nodeport` ในคำสั่งเดียว

```bash
kubectl delete -f labs/lab03-nodeport/
```

**Expected output**

<pre>
service "web-lb" deleted from default namespace
service "web-nodeport" deleted from default namespace
</pre>

```bash
kubectl delete -f labs/lab01-clusterip/web-deploy.yaml
```

**Expected output**

<pre>
deployment.apps "web" deleted from default namespace
</pre>

รอสัก 5 วินาที

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    &lt;none&gt;        443/TCP   5m54s
</pre>

```bash
kubectl get pods
```

**Expected output**

<pre>
No resources found in default namespace.
</pre>

### สิ่งที่เห็น

- `type: NodePort` + `nodePort: 30080` = Service แบบ ClusterIP ที่เปิด port `30080` เพิ่มบน **ทุก Node** (`PORT(S) 80:30080/TCP`)
- เคาะประตู 30080 ของ Node ไหนก็ได้ (`localhost:30080` ใน k8s-lab, IP ของ `lab-worker` หรือ `lab-worker2`) Service ส่งต่อให้ทุก Pod ใน Endpoints แม้ Pod จะอยู่คนละ Node
- browser บนเครื่องเราเข้าถึงแอปในคลัสเตอร์ได้ผ่าน `http://localhost:30080` โดยไม่ต้องใช้ port-forward
- `type: LoadBalancer` บน kind ได้ `EXTERNAL-IP <pending>` แต่ nodePort ที่สุ่มได้ใช้งานได้ทันที = LoadBalancer มี NodePort อยู่ข้างใน

> **🤔 คำถามชวนคิด:** ถ้ามีอีกทีมสร้าง Service แบบ NodePort ที่ระบุ `nodePort: 30080` เหมือนกันในคลัสเตอร์เดียวกัน จะเกิดอะไรขึ้น และทำไมคลัสเตอร์ถึงต้องห้ามแบบนั้น

---

## LAB 4: LAB สุดท้าย: ร้านน้องส้มมีที่อยู่เดียว

<p align="center" id="fig-10">
  <img src="images/05-lab4-som-menu-service.png" alt="รูปที่ 10 LAB4 Endpoints ของ som-menu ระหว่างและหลังเปลี่ยนรุ่น" width="900"><br>
  <em><b>รูปที่ 10</b> LAB4 (ค่าจริงจากการทดลอง): ซ้าย ระหว่างเปลี่ยนรุ่น Pod 2.0 ที่ยัง READY 0/1 ไม่อยู่ใน Endpoints curl จึงได้ 1.0 ทั้งหมด ขวา หลังเปลี่ยนรุ่น Endpoints เป็น IP ของ Pod 2.0 ทั้ง 3 ตัว ส่วน Pod ที่ Terminating ถูกถอดออก ตลอดเวลา ClusterIP 10.96.187.5 และ nodePort 30080 ไม่เปลี่ยน</em>
</p>

**เป้าหมาย:** เปิดร้านน้องส้ม 3 สาขาด้วย Deployment แล้วให้ Service แบบ NodePort เป็น **ที่อยู่เดียวของร้าน** `http://localhost:30080` refresh แล้วได้สาขาต่าง ๆ เปลี่ยนเมนูเป็นเวอร์ชัน 2.0 และย้อนกลับ โดยลูกค้า **ไม่ต้องเปลี่ยนที่อยู่และไม่ต้องต่อท่อใหม่** เลย (แก้ปัญหา port-forward หลุดของบทที่ 4)

<p align="center" id="fig-11">
  <img src="images/05a-lab4-plan.png" alt="รูปที่ 11 แผนการทดลอง LAB4" width="900"><br>
  <em><b>รูปที่ 11</b> แผนการทดลอง LAB4 มี 4 การทดลอง: (1) ขั้นที่ 1–5 Deployment + Service แบบ NodePort ที่ port 80 → targetPort 3000 และ nodePort 30080 (2) ขั้นที่ 6–7 ที่อยู่เดียวกระจาย request ไปหลาย Pod (3) ขั้นที่ 8–10 เปลี่ยนเป็นเวอร์ชัน 2.0 Pod ที่ยัง 0/1 ไม่อยู่ใน Endpoints และแค่ refresh ก็ได้รุ่นใหม่ (4) ขั้นที่ 11–13 rollback ได้ 1.0 กับ 2.0 ปนกันเพราะ selector ดูแค่ app=som-menu แล้วเก็บกวาด</em>
</p>

**ไม่ต้องใช้ VS Code** ทุกคำสั่งพิมพ์ใน 🐧 **SSH session ของ k8s-lab** ตามเดิม ส่วนหน้าเว็บเปิดด้วย 🌐 browser บนเครื่องนักศึกษา

หน้าร้าน (`som-menu/app/server.js`) เป็นเว็บ Node.js ตัวเดียวกับบทที่ 4 บอก **ชื่อ Pod ที่เสิร์ฟหน้านี้** และเวอร์ชันของร้าน แต่ละ Pod = 1 สาขา บทนี้แก้โค้ด 2 จุดให้ทำงานคู่กับ Service

- **ตอบ `connection: close`** ทุกครั้งที่เสิร์ฟหน้าร้าน browser จึงต้องเปิดการเชื่อมต่อใหม่ทุกครั้งที่ refresh และ Service ได้เลือกสาขาใหม่ทุกครั้ง (nginx ใน LAB 3 ไม่ได้ทำ refresh จึงมักได้ Pod เดิม)

  ```js
  res.writeHead(200, { "content-type": "text/html; charset=utf-8", connection: "close" });
  ```

- **รอ 5 วินาทีหลังได้รับ SIGTERM** (สัญญาณขอปิดที่ Kubernetes ส่งมาตอนลบ Pod หรือเปลี่ยนรุ่น) ให้ Service ถอดสาขานี้ออกจาก Endpoints ให้เสร็จก่อน ระหว่างนั้นลูกค้าที่ยังหลงมาก็ยังได้รับบริการ แล้วค่อยปิดร้าน

  ```js
  process.on("SIGTERM", () => {
    console.log(`ปิดสาขา ${POD_NAME} (รอ 5 วินาทีให้ Service หยุดส่งลูกค้ามาก่อน)`);
    setTimeout(() => {
  ```

### ขั้นที่ 1: build image ของหน้าร้าน 2 เวอร์ชัน

> 🎯 **เป้าหมายขั้นนี้:** เตรียม image `som-menu` 2 เวอร์ชันจากโค้ดเดียวกัน ไว้ทดสอบว่าเปลี่ยนรุ่นแล้วที่อยู่ของ Service ไม่เปลี่ยน ([ทฤษฎีหัวข้อ 13](../01_Theory/README.md#13-อ่าน-yaml-ร้านน้องส้มทั้งไฟล์))
>
> 🔍 **สังเกต:** ได้ `som-menu:1.0` และ `som-menu:2.0` ต่างกันแค่ค่า `APP_VERSION` ที่ส่งตอน build

```bash
cd som-menu/app
```

```bash
docker build -t som-menu:1.0 .
```

**Expected output** (บรรทัดท้าย ๆ ครั้งแรกต้องดึง `node:22-alpine` อาจใช้เวลาหลายสิบวินาที)

<pre>
...
#9 naming to docker.io/library/som-menu:1.0 done
#9 unpacking to docker.io/library/som-menu:1.0
#9 unpacking to docker.io/library/som-menu:1.0 1.2s done
#9 DONE 1.9s
</pre>

เวอร์ชัน 2.0 ใช้โค้ดเดียวกัน แต่ส่งค่า `APP_VERSION=2.0` ตอน build (หน้าร้านจะเปลี่ยนสีและมีเมนูใหม่)

```bash
docker build -t som-menu:2.0 --build-arg APP_VERSION=2.0 .
```

**Expected output** (บรรทัดท้าย ๆ)

<pre>
...
#9 naming to docker.io/library/som-menu:2.0 done
#9 unpacking to docker.io/library/som-menu:2.0 0.0s done
#9 DONE 0.2s
</pre>

กลับไปที่โฟลเดอร์ `02_LAB`

```bash
cd ../..
```

### ขั้นที่ 2: นำ image เข้าคลัสเตอร์

> 🎯 **เป้าหมายขั้นนี้:** ส่ง image ทั้ง 2 เวอร์ชันเข้า **Node ทุกตัว** เพราะ Pod ไปเกิดบน Node ไหนก็ได้
>
> 🔍 **สังเกต:** ขึ้น `loading...` 6 บรรทัด (3 Node × 2 เวอร์ชัน)

```bash
kind load docker-image som-menu:1.0 som-menu:2.0 --name lab
```

**Expected output**

<pre>
Image: "som-menu:1.0" with ID "sha256:b2001d0c85410cd108dc48b2f03873ca30eb77f4e5a57e54429bca89833bd743" not yet present on node "lab-worker2", loading...
Image: "som-menu:1.0" with ID "sha256:b2001d0c85410cd108dc48b2f03873ca30eb77f4e5a57e54429bca89833bd743" not yet present on node "lab-worker", loading...
Image: "som-menu:1.0" with ID "sha256:b2001d0c85410cd108dc48b2f03873ca30eb77f4e5a57e54429bca89833bd743" not yet present on node "lab-control-plane", loading...
Image: "som-menu:2.0" with ID "sha256:f6075576ff09ea6f399119dcd2ab8e48a8174d4a49c6bea3ee4bb906190a130e" not yet present on node "lab-worker2", loading...
Image: "som-menu:2.0" with ID "sha256:f6075576ff09ea6f399119dcd2ab8e48a8174d4a49c6bea3ee4bb906190a130e" not yet present on node "lab-worker", loading...
Image: "som-menu:2.0" with ID "sha256:f6075576ff09ea6f399119dcd2ab8e48a8174d4a49c6bea3ee4bb906190a130e" not yet present on node "lab-control-plane", loading...
</pre>

ส่งทั้ง 2 เวอร์ชันเข้าทุก node ไว้ก่อน เพราะ Pod ไปเกิดบนเรือลำไหนก็ได้

### ขั้นที่ 3: Deployment ของร้าน 3 สาขา

> 🎯 **เป้าหมายขั้นนี้:** อ่าน Deployment ให้เห็นค่าที่ Service จะใช้: label `app: som-menu`, `containerPort: 3000` และ `readinessProbe` ([ทฤษฎีหัวข้อ 13](../01_Theory/README.md#13-อ่าน-yaml-ร้านน้องส้มทั้งไฟล์))
>
> 🔍 **สังเกต:** label อยู่ใต้ `template` และ `containerPort` เป็น 3000 ไม่ใช่ 80

ไฟล์ `som-menu/k8s/som-menu-deploy.yaml`

```yaml
# LAB 4: ร้านอาหารแมวน้องส้ม — Deployment ดูแลหน้าร้าน 3 สาขา (เวอร์ชัน 1.0) ใช้คู่กับ som-menu-svc.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: som-menu
  labels:
    app: som-menu
  annotations:
    kubernetes.io/change-cause: "เมนูเวอร์ชัน 1.0"   # โชว์ใน kubectl rollout history
spec:
  replicas: 3                    # เปิด 3 สาขา = Pod 3 ตัว
  minReadySeconds: 10            # สาขาใหม่ต้องพร้อมต่อเนื่อง 10 วินาที จึงนับว่าเปิดแล้ว (ช้าลงพอให้เห็นการเปลี่ยนรุ่น)
  strategy:
    type: RollingUpdate          # เปลี่ยนรุ่นแบบทยอยทีละสาขา (ค่าเริ่มต้นของ Deployment)
    rollingUpdate:
      maxSurge: 1                # เปิดสาขาใหม่เกิน 3 ได้ทีละ 1 สาขา
      maxUnavailable: 0          # สาขาที่พร้อมต้องไม่ต่ำกว่า 3 เลย → ร้านไม่ปิดระหว่างเปลี่ยนรุ่น
  selector:
    matchLabels:
      app: som-menu              # นับเฉพาะ Pod ที่มีป้ายนี้
  template:                      # แม่พิมพ์ของทุกสาขา
    metadata:
      labels:
        app: som-menu            # ต้องตรงกับ selector
        version: "1.0"           # ป้ายเสริมไว้ดูรุ่น (selector ไม่ได้ใช้)
    spec:
      containers:
        - name: web
          image: som-menu:1.0
          imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน node
          env:
            - name: SHOP_NAME
              value: "ร้านอาหารแมวน้องส้ม"
          ports:
            - containerPort: 3000      # port ที่ Service ส่งต่อเข้ามา (targetPort)
          readinessProbe:              # ตอบ /api/health ได้ = สาขาพร้อมรับลูกค้า
            httpGet:
              path: /api/health
              port: 3000
            periodSeconds: 5
          livenessProbe:               # ค้างนานเกินไป → kubelet restart container
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:                   # ทุกสาขาจองเท่ากัน เพราะมาจากแม่พิมพ์เดียวกัน
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 200m, memory: 128Mi }
```

ทำงานอย่างไร

- **เหมือน `som-menu-deploy.yaml` ของบทที่ 4 ทุกบรรทัด** ต่างแค่ comment 2 จุด: บรรทัดแรก (`ใช้คู่กับ som-menu-svc.yaml`) และ comment ของ `containerPort: 3000` ที่ตอนนี้เป็น port ที่ **Service** ส่งต่อเข้ามา (ไม่ใช่ port-forward แล้ว)
- ป้าย `app: som-menu` ในแม่พิมพ์คือป้ายที่ Service จะใช้หาสาขา ส่วนป้าย `version` ไว้ดูรุ่น
- `readinessProbe` สำคัญกับ Service มาก: Pod ที่ **ยังไม่ผ่าน** readinessProbe (`READY 0/1`) จะ **ไม่ถูกใส่ใน Endpoints** ลูกค้าจึงไม่ถูกส่งไปสาขาที่ยังไม่พร้อม (ขั้นที่ 8 จะเห็น)

### ขั้นที่ 4: Service ที่อยู่เดียวของร้าน

> 🎯 **เป้าหมายขั้นนี้:** อ่าน Service แบบ NodePort ที่ตัวเลข port ทั้ง 3 ตัวไม่ซ้ำกัน ([ทฤษฎีหัวข้อ 4](../01_Theory/README.md#4-ที่อยู่-3-แบบ-และ-port-4-ตัว-ศัพท์ที่ต้องแยกให้ออก) · [ทฤษฎีหัวข้อ 13](../01_Theory/README.md#13-อ่าน-yaml-ร้านน้องส้มทั้งไฟล์))
>
> 🔍 **สังเกต:** `port: 80` (Service), `targetPort: 3000` (= `containerPort`) และ `nodePort: 30080` (Node)

ไฟล์ `som-menu/k8s/som-menu-svc.yaml`

```yaml
# LAB 4: ที่อยู่เดียวของร้านน้องส้ม — Service แบบ NodePort กระจายลูกค้าไปทุกสาขาที่พร้อม
apiVersion: v1
kind: Service
metadata:
  name: som-menu
spec:
  type: NodePort
  selector:
    app: som-menu            # ทุกสาขาที่ติดป้ายนี้ ไม่สนว่า version 1.0 หรือ 2.0
  ports:
    - port: 80               # ในคลัสเตอร์เรียก http://som-menu (port 80)
      targetPort: 3000       # หน้าร้าน Node.js ฟัง port 3000
      nodePort: 30080        # นอกคลัสเตอร์เปิด http://localhost:30080
```

ทำงานอย่างไร

- Service ชื่อ `som-menu` แบบ **NodePort** เหมือน LAB 3
- `selector: app: som-menu` = ทุกสาขาที่มีป้ายนี้ **ไม่ดูป้าย `version`** ระหว่างเปลี่ยนรุ่น Service จึงส่งลูกค้าได้ทั้งสาขา 1.0 และ 2.0
- port 3 ตัวไม่เท่ากันแล้ว: `nodePort: 30080` (ประตูบนทุก Node ที่ browser เข้ามา) → `port: 80` (port ของ Service ในคลัสเตอร์ Pod อื่นเรียก `http://som-menu`) → `targetPort: 3000` (port ที่หน้าร้าน Node.js ฟังอยู่ ตรงกับ `containerPort: 3000`)

### ขั้นที่ 5: เปิดร้าน

> 🎯 **เป้าหมายขั้นนี้:** ยืนยันว่า Service ส่ง request ต่อไปที่ **targetPort 3000** ของ Pod ([ทฤษฎีหัวข้อ 4](../01_Theory/README.md#4-ที่อยู่-3-แบบ-และ-port-4-ตัว-ศัพท์ที่ต้องแยกให้ออก))
>
> 🔍 **สังเกต:** `PORT(S) 80:30080/TCP`, `TargetPort: 3000/TCP` และ Endpoints ลงท้าย `:3000`

```bash
kubectl apply -f som-menu/k8s/som-menu-deploy.yaml
```

**Expected output**

<pre>
deployment.apps/som-menu created
</pre>

```bash
kubectl apply -f som-menu/k8s/som-menu-svc.yaml
```

**Expected output**

<pre>
service/som-menu created
</pre>

```bash
kubectl rollout status deployment/som-menu
```

**Expected output** (รอประมาณ 10 วินาที)

<pre>
Waiting for deployment "som-menu" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "som-menu" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "som-menu" rollout to finish: 0 of 3 updated replicas are available...
deployment "som-menu" successfully rolled out
</pre>

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
kubernetes   ClusterIP   10.96.0.1     &lt;none&gt;        443/TCP        6m31s
som-menu     NodePort    10.96.187.5   &lt;none&gt;        80:30080/TCP   11s
</pre>

```bash
kubectl get pods -o wide
```

**Expected output**

<pre>
NAME                        READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-menu-5f5c95db8f-gqsd2   1/1     Running   0          11s   10.244.2.14   lab-worker    &lt;none&gt;           &lt;none&gt;
som-menu-5f5c95db8f-jfjlg   1/1     Running   0          11s   10.244.1.9    lab-worker2   &lt;none&gt;           &lt;none&gt;
som-menu-5f5c95db8f-zq7lg   1/1     Running   0          11s   10.244.2.15   lab-worker    &lt;none&gt;           &lt;none&gt;
</pre>

```bash
kubectl describe svc som-menu
```

**Expected output**

<pre>
Name:                     som-menu
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=som-menu
Type:                     NodePort
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.187.5
IPs:                      10.96.187.5
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               3000/TCP
NodePort:                 &lt;unset&gt;  30080/TCP
Endpoints:                10.244.1.9:3000,10.244.2.14:3000,10.244.2.15:3000
Session Affinity:         None
External Traffic Policy:  Cluster
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

- `Port: 80/TCP` → `TargetPort: 3000/TCP` และ `NodePort: 30080/TCP` ตรงกับไฟล์
- `Endpoints` = IP ของ 3 สาขาที่ **port 3000** ตรงกับ `kubectl get pods -o wide`

### ขั้นที่ 6: ลูกค้าเข้าร้านทาง localhost:30080

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า nodePort ที่อยู่เดียว (`localhost:30080`) กระจาย request ไปทุก Pod ([ทฤษฎีหัวข้อ 3](../01_Theory/README.md#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร) · [ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node))
>
> 🔍 **สังเกต:** ชื่อ Pod ใน `/api/info` เปลี่ยนไปมา และเป็นเวอร์ชัน `1.0` ทั้งหมด

`/api/info` ของหน้าร้านตอบชื่อสาขา (Pod) และเวอร์ชันเป็น JSON สั้น ๆ เหมาะกับ curl

```bash
curl http://localhost:30080/api/info
```

**สั่งซ้ำ 6 ครั้ง**

**Expected output** (ผลของทั้ง 6 ครั้งต่อกัน)

<pre>
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-jfjlg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-gqsd2","version":"1.0"}
</pre>

ที่อยู่เดียว ได้ครบทั้ง 3 สาขา เวอร์ชัน `1.0`

### ขั้นที่ 7: เปิดหน้าร้านใน browser

> 🎯 **เป้าหมายขั้นนี้:** เปิดแอปจาก browser บนเครื่องเราโดยไม่ใช้ port-forward ([ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-nodeport-ประตูบนทุก-node) · [ทฤษฎีหัวข้อ 12](../01_Theory/README.md#12-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update))
>
> 🔍 **สังเกต:** refresh แล้วชื่อ Pod บนหน้าเว็บเปลี่ยน และตรงกับจำนวนครั้งใน `kubectl logs`

🌐 เปิด browser บนเครื่องนักศึกษา ไปที่ `http://localhost:30080` **ไม่ต้องใช้ VS Code และไม่ต้องรัน port-forward** แบบบทที่ 4

<p align="center" id="fig-12">
  <img src="images/screenshots/20261019_lab4_01-shop-v1-pod-a.png" alt="รูปที่ 12 ภาพหน้าจอจริง หน้าร้านเวอร์ชัน 1.0 Pod แรก" width="520"><br>
  <em><b>รูปที่ 12</b> ภาพหน้าจอจริงจากการทดลอง: เปิด http://localhost:30080 ครั้งแรก ได้หน้าร้านเวอร์ชัน 1.0 เสิร์ฟโดย Pod som-menu-5f5c95db8f-gqsd2 (ทดสอบ 19 ต.ค. 2569 ด้วย browser จริงบนเครื่อง host ตอนถ่าย container ทดลอง map port 30080 ไปที่ port อื่นของ host นักศึกษาเปิด http://localhost:30080 ตรง ๆ หน้าเว็บที่เห็นเหมือนกัน)</em>
</p>

กด **refresh** ไปเรื่อย ๆ Service สุ่ม Pod ให้ทุกครั้ง จึงอาจได้ Pod เดิมซ้ำหลายครั้ง (ตอนทดลอง ครั้งที่ 1 ได้ `gqsd2` ครั้งที่ 2–4 ได้ `jfjlg`)

<p align="center" id="fig-13">
  <img src="images/screenshots/20261019_lab4_02-shop-v1-pod-b.png" alt="รูปที่ 13 ภาพหน้าจอจริง refresh แล้วได้อีก Pod" width="520"><br>
  <em><b>รูปที่ 13</b> ภาพหน้าจอจริงจากการทดลอง: ที่อยู่เดิม http://localhost:30080 กด refresh ครั้งที่ 4 ได้ Pod som-menu-5f5c95db8f-jfjlg ซึ่งเสิร์ฟไปแล้ว 3 ครั้ง (ครั้งที่ 2–4) (ทดสอบ 19 ต.ค. 2569 ด้วย browser จริงบนเครื่อง host ตอนถ่าย container ทดลอง map port 30080 ไปที่ port อื่นของ host นักศึกษาเปิด http://localhost:30080 ตรง ๆ หน้าเว็บที่เห็นเหมือนกัน)</em>
</p>

ดู log ของ 2 Pod ที่เห็นบนหน้าเว็บ

```bash
kubectl logs som-menu-5f5c95db8f-gqsd2    # ← เปลี่ยนเป็นชื่อ Pod แรกที่เห็นบนหน้าเว็บของตัวเอง
```

**Expected output**

<pre>
ร้านอาหารแมวน้องส้ม v1.0 เปิดสาขา som-menu-5f5c95db8f-gqsd2 ที่ port 3000
[v1.0] som-menu-5f5c95db8f-gqsd2 เสิร์ฟหน้าร้านครั้งที่ 1
</pre>

```bash
kubectl logs som-menu-5f5c95db8f-jfjlg    # ← เปลี่ยนเป็นชื่อ Pod ที่สองที่เห็นบนหน้าเว็บของตัวเอง
```

**Expected output**

<pre>
ร้านอาหารแมวน้องส้ม v1.0 เปิดสาขา som-menu-5f5c95db8f-jfjlg ที่ port 3000
[v1.0] som-menu-5f5c95db8f-jfjlg เสิร์ฟหน้าร้านครั้งที่ 1
[v1.0] som-menu-5f5c95db8f-jfjlg เสิร์ฟหน้าร้านครั้งที่ 2
[v1.0] som-menu-5f5c95db8f-jfjlg เสิร์ฟหน้าร้านครั้งที่ 3
</pre>

log ตรงกับที่ refresh: `gqsd2` เสิร์ฟ 1 ครั้ง (ครั้งที่ 1) และ `jfjlg` เสิร์ฟ 3 ครั้ง (ครั้งที่ 2–4) (การเรียก `/api/info` ด้วย curl ไม่นับในบรรทัด "เสิร์ฟหน้าร้าน")

### ขั้นที่ 8: เปลี่ยนเป็นเมนูเวอร์ชัน 2.0

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า **Pod ที่ readinessProbe ยังไม่ผ่าน (`0/1`) ยังไม่อยู่ใน Endpoints** ([ทฤษฎีหัวข้อ 12](../01_Theory/README.md#12-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update))
>
> 🔍 **สังเกต:** curl 6 ครั้งได้ `1.0` ทั้งหมด ทั้งที่มี Pod `2.0` ที่ label ตรงแต่ยัง `READY 0/1`

ไฟล์ `som-menu/k8s/som-menu-deploy-v2.yaml`

```yaml
# LAB 4: ร้านอาหารแมวน้องส้ม — เปลี่ยนเป็นเมนูเวอร์ชัน 2.0 (Service ตัวเดิม ไม่ต้องแก้)
# ต่างจาก som-menu-deploy.yaml แค่ 3 บรรทัดที่มี ← เท่านั้น
apiVersion: apps/v1
kind: Deployment
metadata:
  name: som-menu
  labels:
    app: som-menu
  annotations:
    kubernetes.io/change-cause: "เมนูเวอร์ชัน 2.0"   # ← เปลี่ยน
spec:
  replicas: 3                    # เปิด 3 สาขา = Pod 3 ตัว
  minReadySeconds: 10            # สาขาใหม่ต้องพร้อมต่อเนื่อง 10 วินาที จึงนับว่าเปิดแล้ว (ช้าลงพอให้เห็นการเปลี่ยนรุ่น)
  strategy:
    type: RollingUpdate          # เปลี่ยนรุ่นแบบทยอยทีละสาขา (ค่าเริ่มต้นของ Deployment)
    rollingUpdate:
      maxSurge: 1                # เปิดสาขาใหม่เกิน 3 ได้ทีละ 1 สาขา
      maxUnavailable: 0          # สาขาที่พร้อมต้องไม่ต่ำกว่า 3 เลย → ร้านไม่ปิดระหว่างเปลี่ยนรุ่น
  selector:
    matchLabels:
      app: som-menu              # นับเฉพาะ Pod ที่มีป้ายนี้
  template:                      # แม่พิมพ์ของทุกสาขา
    metadata:
      labels:
        app: som-menu            # ต้องตรงกับ selector
        version: "2.0"           # ← เปลี่ยน
    spec:
      containers:
        - name: web
          image: som-menu:2.0           # ← เปลี่ยน
          imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน node
          env:
            - name: SHOP_NAME
              value: "ร้านอาหารแมวน้องส้ม"
          ports:
            - containerPort: 3000      # port ที่ Service ส่งต่อเข้ามา (targetPort)
          readinessProbe:              # ตอบ /api/health ได้ = สาขาพร้อมรับลูกค้า
            httpGet:
              path: /api/health
              port: 3000
            periodSeconds: 5
          livenessProbe:               # ค้างนานเกินไป → kubelet restart container
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:                   # ทุกสาขาจองเท่ากัน เพราะมาจากแม่พิมพ์เดียวกัน
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 200m, memory: 128Mi }
```

ต่างจาก `som-menu-deploy.yaml` แค่ **3 บรรทัดที่มี `← เปลี่ยน`** (โน้ต `change-cause`, ป้าย `version: "2.0"` และ `image: som-menu:2.0`) ส่วน **Service ไม่ต้องแก้อะไรเลย** เพราะสาขาใหม่ยังติดป้าย `app: som-menu` เหมือนเดิม

เตรียมพิมพ์คำสั่งถัดไป **ทันที** หลัง apply เพื่อจับจังหวะที่สาขาใหม่เพิ่งเกิด

```bash
kubectl apply -f som-menu/k8s/som-menu-deploy-v2.yaml
```

**Expected output**

<pre>
deployment.apps/som-menu configured
</pre>

รอสัก 3 วินาที แล้วเรียกร้าน

```bash
curl http://localhost:30080/api/info
```

**สั่งซ้ำ 6 ครั้ง** (เร็ว ๆ)

**Expected output** (ผลของทั้ง 6 ครั้งต่อกัน)

<pre>
{"pod":"som-menu-5f5c95db8f-jfjlg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-jfjlg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-gqsd2","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-jfjlg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-jfjlg","version":"1.0"}
</pre>

ยังเป็น **`1.0` ทั้งหมด** ทั้งที่ apply v2 ไปแล้ว ดูว่าเกิดอะไรขึ้น

```bash
kubectl get pods --show-labels
```

**Expected output**

<pre>
NAME                        READY   STATUS    RESTARTS   AGE   LABELS
som-menu-5f5c95db8f-gqsd2   1/1     Running   0          46s   app=som-menu,pod-template-hash=5f5c95db8f,version=1.0
som-menu-5f5c95db8f-jfjlg   1/1     Running   0          46s   app=som-menu,pod-template-hash=5f5c95db8f,version=1.0
som-menu-5f5c95db8f-zq7lg   1/1     Running   0          46s   app=som-menu,pod-template-hash=5f5c95db8f,version=1.0
som-menu-6bf6c9f6c5-687px   0/1     Running   0          3s    app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
</pre>

- สาขาใหม่ `som-menu-6bf6c9f6c5-687px` (`version=2.0`) เกิดแล้ว และมีป้าย `app=som-menu` ตรงกับ selector ของ Service
- แต่ยังเป็น **`READY 0/1`** = **readinessProbe ยังไม่ผ่าน** (ยังไม่ได้ตอบ `/api/health`) Kubernetes จึง **ยังไม่ใส่สาขานี้ใน Endpoints** และ **Service ยังไม่ส่งลูกค้าไปหา** ลูกค้าจึงได้แต่สาขา 1.0 ที่พร้อมแล้ว ไม่มีใครเจอสาขาที่ยังเปิดไม่เสร็จ

### ขั้นที่ 9: รอให้เปลี่ยนรุ่นเสร็จ

> 🎯 **เป้าหมายขั้นนี้:** ยืนยันว่าเปลี่ยนรุ่นแล้ว **Endpoints เปลี่ยนเป็น IP ชุดใหม่ แต่ ClusterIP และ nodePort เดิม** ([ทฤษฎีหัวข้อ 12](../01_Theory/README.md#12-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update))
>
> 🔍 **สังเกต:** Endpoints ไม่มี IP ของ Pod `1.0` แล้ว `IP 10.96.187.5` และ `NodePort 30080` เหมือนเดิม และ curl ได้ `2.0`

```bash
kubectl rollout status deployment/som-menu
```

**Expected output** (รอประมาณ 30 วินาที)

<pre>
Waiting for deployment "som-menu" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
deployment "som-menu" successfully rolled out
</pre>

รอสัก 5 วินาที ให้สาขาเก่าตัวสุดท้ายปิดเสร็จ (แต่ละสาขารอ 5 วินาทีหลังได้ SIGTERM)

```bash
kubectl get pods --show-labels
```

**Expected output**

<pre>
NAME                        READY   STATUS        RESTARTS   AGE   LABELS
som-menu-5f5c95db8f-zq7lg   1/1     Terminating   0          86s   app=som-menu,pod-template-hash=5f5c95db8f,version=1.0
som-menu-6bf6c9f6c5-687px   1/1     Running       0          43s   app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
som-menu-6bf6c9f6c5-b58wj   1/1     Running       0          16s   app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
som-menu-6bf6c9f6c5-kpgxt   1/1     Running       0          27s   app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
</pre>

```bash
kubectl describe svc som-menu
```

**Expected output** (ตัดเฉพาะส่วนสำคัญ)

<pre>
Name:                     som-menu
Namespace:                default
Labels:                   &lt;none&gt;
Annotations:              &lt;none&gt;
Selector:                 app=som-menu
Type:                     NodePort
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.187.5
IPs:                      10.96.187.5
Port:                     &lt;unset&gt;  80/TCP
TargetPort:               3000/TCP
NodePort:                 &lt;unset&gt;  30080/TCP
Endpoints:                10.244.1.10:3000,10.244.2.16:3000,10.244.2.17:3000
Session Affinity:         None
External Traffic Policy:  Cluster
Internal Traffic Policy:  Cluster
Events:                   &lt;none&gt;
</pre>

**Endpoints เป็น IP ชุดใหม่ทั้งหมด** (ไม่มี `10.244.2.14`, `10.244.2.15`, `10.244.1.9` ของสาขา 1.0 แล้ว) แต่ IP ของ Service (`10.96.187.5`) และ NodePort `30080` **เหมือนเดิมทุกอย่าง**

```bash
curl http://localhost:30080/api/info
```

**สั่งซ้ำ 4 ครั้ง**

**Expected output** (ผลของทั้ง 4 ครั้งต่อกัน)

<pre>
{"pod":"som-menu-6bf6c9f6c5-kpgxt","version":"2.0"}
{"pod":"som-menu-6bf6c9f6c5-b58wj","version":"2.0"}
{"pod":"som-menu-6bf6c9f6c5-b58wj","version":"2.0"}
{"pod":"som-menu-6bf6c9f6c5-687px","version":"2.0"}
</pre>

### ขั้นที่ 10: แค่ refresh ก็ได้เมนูใหม่

> 🎯 **เป้าหมายขั้นนี้:** เทียบกับบทที่ 4: ที่อยู่เดิม แค่ refresh ก็ได้รุ่นใหม่ ([ทฤษฎีหัวข้อ 12](../01_Theory/README.md#12-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update))
>
> 🔍 **สังเกต:** หน้าเว็บเป็นเวอร์ชัน 2.0 โดยไม่ต้องทำอะไรเพิ่ม

🌐 กลับไปที่ browser แล้ว **กด refresh อย่างเดียว** ไม่ต้องทำอะไรเพิ่ม

<p align="center" id="fig-14">
  <img src="images/screenshots/20261019_lab4_03-shop-v2.png" alt="รูปที่ 14 ภาพหน้าจอจริง แค่ refresh ก็ได้เวอร์ชัน 2.0" width="520"><br>
  <em><b>รูปที่ 14</b> ภาพหน้าจอจริงจากการทดลอง: หลังเปลี่ยนรุ่น แค่กด refresh ที่ http://localhost:30080 เดิม ได้หน้าร้านสีเขียวอมฟ้าเวอร์ชัน 2.0 เสิร์ฟโดย Pod som-menu-6bf6c9f6c5-b58wj มีเมนูใหม่ไอศกรีมแมว (ทดสอบ 19 ต.ค. 2569 ด้วย browser จริงบนเครื่อง host ตอนถ่าย container ทดลอง map port 30080 ไปที่ port อื่นของ host นักศึกษาเปิด http://localhost:30080 ตรง ๆ หน้าเว็บที่เห็นเหมือนกัน)</em>
</p>

<p align="center" id="fig-15">
  <img src="images/06-lab4-no-more-lost-connection.png" alt="รูปที่ 15 บทที่ 4 ท่อหลุด เทียบกับบทที่ 5 ที่อยู่เดียว" width="900"><br>
  <em><b>รูปที่ 15</b> เทียบสองบท: บทที่ 4 port-forward ต่อท่อตรงเข้าสาขาเดียว พอสาขานั้นถูกปิดตอนเปลี่ยนรุ่น ท่อก็ขาด (lost connection to pod) บทที่ 5 browser เข้าทางประตู 30080 ไปที่บูธ Service som-menu ซึ่งส่งต่อไปสาขาที่พร้อมเสมอ สาขาไหนถูกปิด ลูกค้าก็ไปสาขาอื่นได้ทันที</em>
</p>

เทียบกับบทที่ 4: ตอนนั้น port-forward ผูกกับ **Pod ตัวเดียว** พอเปลี่ยนรุ่นแล้ว Pod นั้นถูกปิด ท่อก็ขาด ต้องรัน port-forward ใหม่ทุกครั้ง คราวนี้ browser ต่อกับ **ประตู 30080 ของ Service** ซึ่งไม่เคยหายไปไหน Service แค่เปลี่ยนรายชื่อสาขาใน Endpoints ลูกค้าจึง **ไม่ต้องเปลี่ยนที่อยู่และไม่ต้องต่อท่อใหม่**

### ขั้นที่ 11: ย้อนกลับ ระหว่างย้อนลูกค้าได้ทั้งสองรุ่น

> 🎯 **เป้าหมายขั้นนี้:** ทดสอบว่า selector ดูแค่ `app=som-menu` ระหว่าง rollback Pod ที่พร้อมทั้ง 2 รุ่นอยู่ใน Endpoints พร้อมกัน ([ทฤษฎีหัวข้อ 12](../01_Theory/README.md#12-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update))
>
> 🔍 **สังเกต:** ได้ `1.0` กับ `2.0` ปนกัน และ Pod ที่ `Terminating` ไม่ได้รับ request

```bash
kubectl rollout history deployment/som-menu
```

**Expected output**

<pre>
deployment.apps/som-menu 
REVISION  CHANGE-CAUSE
1         เมนูเวอร์ชัน 1.0
2         เมนูเวอร์ชัน 2.0
</pre>

```bash
kubectl rollout undo deployment/som-menu
```

**Expected output**

<pre>
Warning: resource deployments/som-menu was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
deployment.apps/som-menu rolled back
</pre>

`Warning` เรื่องเดียวกับบทที่ 4 (ไฟล์ที่ apply ล่าสุดยังเป็น v2 ขั้นที่ 12 จะแก้) รอสัก 15 วินาที แล้วเรียกร้าน

```bash
curl http://localhost:30080/api/info
```

**สั่งซ้ำ 6 ครั้ง**

**Expected output** (ผลของทั้ง 6 ครั้งต่อกัน)

<pre>
{"pod":"som-menu-5f5c95db8f-jqbz6","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-5d9r4","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-jqbz6","version":"1.0"}
{"pod":"som-menu-6bf6c9f6c5-b58wj","version":"2.0"}
{"pod":"som-menu-6bf6c9f6c5-b58wj","version":"2.0"}
{"pod":"som-menu-6bf6c9f6c5-b58wj","version":"2.0"}
</pre>

**`1.0` กับ `2.0` ปนกัน** = ระหว่างย้อนกลับ ทั้งสาขาเก่าและใหม่ที่พร้อมอยู่ใน Endpoints พร้อมกัน (selector ดูแค่ `app=som-menu` ไม่ดู `version`) ลูกค้าแต่ละคนจึงอาจได้คนละรุ่น แต่ **ทุกคนได้รับบริการ**

```bash
kubectl get pods --show-labels
```

**Expected output**

<pre>
NAME                        READY   STATUS        RESTARTS   AGE   LABELS
som-menu-5f5c95db8f-5d9r4   1/1     Running       0          15s   app=som-menu,pod-template-hash=5f5c95db8f,version=1.0
som-menu-5f5c95db8f-jqbz6   1/1     Running       0          4s    app=som-menu,pod-template-hash=5f5c95db8f,version=1.0
som-menu-6bf6c9f6c5-687px   1/1     Terminating   0          76s   app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
som-menu-6bf6c9f6c5-b58wj   1/1     Running       0          49s   app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
som-menu-6bf6c9f6c5-kpgxt   1/1     Running       0          60s   app=som-menu,pod-template-hash=6bf6c9f6c5,version=2.0
</pre>

- Pod ที่ `Running` มี 1.0 ตัวใหม่ 2 ตัว (`5d9r4`, `jqbz6`) + 2.0 ที่ยังเปิดอยู่ 2 ตัว (`b58wj`, `kpgxt`) ทั้ง 4 ตัวอยู่ใน Endpoints และ curl 6 ครั้งข้างบนเจอ 3 ตัวในนั้น
- `som-menu-6bf6c9f6c5-687px` เป็น **`Terminating`** (กำลังปิด รอ 5 วินาทีตามที่แก้ใน server.js) ถูกถอดออกจาก Endpoints แล้ว จึง **ไม่มีลูกค้าถูกส่งไป** (ไม่มีชื่อนี้ใน curl ทั้ง 6 ครั้ง)

```bash
kubectl rollout status deployment/som-menu
```

**Expected output**

<pre>
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "som-menu" rollout to finish: 1 old replicas are pending termination...
deployment "som-menu" successfully rolled out
</pre>

เริ่มที่ `2 out of 3` เพราะเราสั่งช้ากว่า undo ไปราว 15 วินาที รอสัก 5 วินาที แล้วเรียกร้านอีกครั้ง

```bash
curl http://localhost:30080/api/info
```

**สั่งซ้ำ 4 ครั้ง**

**Expected output** (ผลของทั้ง 4 ครั้งต่อกัน)

<pre>
{"pod":"som-menu-5f5c95db8f-cr8xb","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-cr8xb","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-jqbz6","version":"1.0"}
{"pod":"som-menu-5f5c95db8f-5d9r4","version":"1.0"}
</pre>

กลับเป็น **`1.0` ทั้งหมด** ที่อยู่ยังเป็น `http://localhost:30080` เหมือนเดิม (refresh browser ก็จะเห็นหน้าร้านสีส้มเวอร์ชัน 1.0 กลับมา)

### ขั้นที่ 12: ทำให้ไฟล์ตรงกับคลัสเตอร์

> 🎯 **เป้าหมายขั้นนี้:** ทำให้ไฟล์ที่ apply ล่าสุดตรงกับรุ่นที่ย้อนไป (เหมือนบทที่ 4)
>
> 🔍 **สังเกต:** ขึ้น `configured`

เหมือนบทที่ 4: apply ไฟล์เวอร์ชัน 1.0 ให้ไฟล์ที่ apply ล่าสุดตรงกับรุ่นที่ย้อนไป

```bash
kubectl apply -f som-menu/k8s/som-menu-deploy.yaml
```

**Expected output**

<pre>
deployment.apps/som-menu configured
</pre>

### ขั้นที่ 13: เก็บกวาด

> 🎯 **เป้าหมายขั้นนี้:** เก็บกวาด Service และ Deployment ของ LAB 4
>
> 🔍 **สังเกต:** `deleted` ทั้ง 2 รายการ

```bash
kubectl delete -f som-menu/k8s/som-menu-svc.yaml
```

**Expected output**

<pre>
service "som-menu" deleted from default namespace
</pre>

```bash
kubectl delete -f som-menu/k8s/som-menu-deploy.yaml
```

**Expected output**

<pre>
deployment.apps "som-menu" deleted from default namespace
</pre>

ไม่ต้องกด Ctrl+C หยุดอะไรเลย เพราะบทนี้ไม่มี port-forward ค้างไว้

### สิ่งที่เห็น

- Service `som-menu` แบบ NodePort = **ที่อยู่เดียวของร้าน** `http://localhost:30080` ทั้ง curl และ browser refresh แล้วได้สาขาต่าง ๆ ไม่ต้องใช้ VS Code หรือ port-forward
- ระหว่างเปลี่ยนรุ่น สาขาใหม่ที่ยัง `0/1` (readinessProbe ยังไม่ผ่าน) **ไม่อยู่ใน Endpoints** และสาขาที่กำลังปิด (`Terminating`) ก็ถูกถอดออก Service จึงส่งลูกค้าไปเฉพาะสาขาที่พร้อม
- เปลี่ยนรุ่นหรือย้อนกลับ → Endpoints เปลี่ยนเป็น IP ชุดใหม่ แต่ IP ของ Service, NodePort และที่อยู่ที่ลูกค้าใช้ **ไม่เปลี่ยน** แค่ refresh ก็ได้รุ่นใหม่ ไม่หลุดแบบ port-forward ในบทที่ 4
- selector ดูแค่ `app=som-menu` ระหว่างเปลี่ยนรุ่นลูกค้าจึงได้ทั้ง `1.0` และ `2.0` ปนกัน

### คำถามท้าย LAB 4

1. ตอนเปลี่ยนเป็นเวอร์ชัน 2.0 ทำไม curl 6 ครั้งแรกไม่เจอสาขา 2.0 เลยทั้งที่ Pod `som-menu-6bf6c9f6c5-687px` เกิดแล้วและมีป้าย `app=som-menu` ถ้าลบ `readinessProbe` ออกจาก Deployment ลูกค้าที่เข้ามาช่วงนั้นอาจเจออะไร
2. ถ้าแก้ selector ของ `som-menu-svc.yaml` เป็น `app: som-menu` และ `version: "2.0"` แล้ว apply ขณะที่ร้านยังเป็นเวอร์ชัน 1.0 ทั้งหมด ลูกค้าที่เปิด `http://localhost:30080` จะเจออะไร และวิธีตรวจคืออะไร (นึกถึงขั้นที่ 5 ของ LAB 2)

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจว่าไม่มี Service, Deployment และ Pod ค้าง รอสัก 10 วินาทีหลังลบใน LAB 4 แล้วสั่ง

```bash
kubectl get svc
```

**Expected output**

<pre>
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    &lt;none&gt;        443/TCP   8m52s
</pre>

เหลือแค่ Service `kubernetes` ของระบบ (ห้ามลบ)

```bash
kubectl get deploy
```

**Expected output**

<pre>
No resources found in default namespace.
</pre>

```bash
kubectl get pods
```

**Expected output**

<pre>
No resources found in default namespace.
</pre>

ถ้ายังเห็นอยู่ ให้ลบด้วย `kubectl delete svc <ชื่อ>` และ `kubectl delete deploy <ชื่อ>` (Pod `client` ลบด้วย `kubectl delete pod client`)

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (ทางเลือก, image ที่ `kind load` ไว้จะหายไปด้วย) จากนั้นออกจาก SSH ด้วย `exit`

🖥️ **บนเครื่องนักศึกษา** (ทางเลือก) หยุด container เพื่อคืน RAM/CPU แล้วเปิดใหม่ครั้งหน้าด้วย `docker start k8s-lab` (คลัสเตอร์, ไฟล์ใน `/workspace` และ port `30080–30082` ที่ map ไว้ยังอยู่)

```bash
docker stop k8s-lab
```

---

## สรุปคำสั่ง kubectl ในบทนี้

**สร้าง / ลบ**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl apply -f <ไฟล์>` | สร้าง/อัปเดต Service หรือ Deployment ตามไฟล์ |
| `kubectl apply -f <โฟลเดอร์>/` | สร้าง/อัปเดตจากทุกไฟล์ในโฟลเดอร์ในคำสั่งเดียว |
| `kubectl delete -f <ไฟล์หรือโฟลเดอร์>` | ลบทุกอย่างที่อยู่ในไฟล์ (หรือทุกไฟล์ในโฟลเดอร์) |
| `kubectl delete svc <ชื่อ>` | ลบ Service ตามชื่อ (Pod ไม่ถูกลบตาม) |
| `kubectl delete pod <ชื่อ>` | ลบ Pod (ถ้ามี ReplicaSet ดูแล จะสร้างตัวใหม่แทนและ Endpoints เปลี่ยนตาม) |

**ดู Service / Endpoints**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl get svc` | รายการ Service: TYPE, CLUSTER-IP, PORT(S) (`80:30080/TCP` = NodePort) |
| `kubectl get svc -A` | Service ทุก namespace (เช่น `kube-dns` ของระบบ) |
| `kubectl describe svc <ชื่อ>` | รายละเอียด: Selector, IP, Port, TargetPort, NodePort และ **Endpoints** (ว่าง = selector ไม่ตรง) |
| `kubectl get endpointslices` | รายชื่อ IP ของ Pod ที่แต่ละ Service ส่งงานให้ |
| `kubectl get pods -o wide` | Pod พร้อม IP และ Node ไว้เทียบกับ Endpoints |
| `kubectl get pods -l <key>=<value> -o wide` | เฉพาะ Pod ที่มีป้ายนั้น (แบบที่ Service เลือก) |
| `kubectl get pods --show-labels` | ดูป้ายของ Pod (`app`, `version`, `pod-template-hash`) |
| `kubectl get nodes -o wide` | Node พร้อม `INTERNAL-IP` ไว้ทดสอบ NodePort |
| `kubectl get pods -A` | Pod ทุก namespace (เช่น `kube-proxy`, `coredns`) |

**แก้ป้าย / จำนวน**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl label pod <ชื่อ> <key>-` | ถอดป้ายออกจาก Pod (Pod หลุดจาก Endpoints และ ReplicaSet) |
| `kubectl scale deployment <ชื่อ> --replicas=<N>` | เปลี่ยนจำนวน Pod (Endpoints เพิ่ม/ลดตาม) |

**ทดสอบจากในคลัสเตอร์**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl exec <pod> -- wget -qO- http://<ชื่อ Service>` | เรียก Service ด้วยชื่อจาก Pod ในคลัสเตอร์ |
| `kubectl exec <pod> -- wget -qO- http://<ชื่อ>.<namespace>.svc.cluster.local` | เรียกด้วยชื่อเต็ม |
| `kubectl exec <pod> -- wget -qO- http://<IP ของ Pod>` | เรียก Pod ตัวเดียวตรง ๆ (IP เปลี่ยนเมื่อ Pod ใหม่) |
| `kubectl exec <pod> -- nslookup <ชื่อ>.<namespace>.svc.cluster.local` | ถาม DNS ว่าชื่อ Service แปลงเป็น IP อะไร |

**ทดสอบจากนอกคลัสเตอร์**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `curl http://localhost:30080` | เรียก NodePort จาก k8s-lab (ผ่าน `lab-control-plane`) |
| `curl http://<INTERNAL-IP ของ Node>:30080` | เคาะประตู NodePort ของ Node ที่ระบุ |
| 🌐 `http://localhost:30080` | เปิดด้วย browser บนเครื่องนักศึกษา (ต้อง `docker run` ด้วย `-p 30080-30082:30080-30082`) |

**Deployment / rollout / log**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl rollout status deployment/<ชื่อ>` | รอดูการเปลี่ยนรุ่นจนเสร็จ |
| `kubectl rollout history deployment/<ชื่อ>` | ดูรายการ revision พร้อม `CHANGE-CAUSE` |
| `kubectl rollout undo deployment/<ชื่อ>` | ย้อนกลับไปรุ่นก่อนหน้า แล้วควร apply ไฟล์ให้ตรง |
| `kubectl logs <ชื่อ Pod>` | ดูสิ่งที่แอปใน Pod พิมพ์ออกมา |

**คลัสเตอร์และ image**

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `k8s-up` / `k8s-down` | สร้าง / ลบคลัสเตอร์ kind ชื่อ `lab` |
| `docker build -t <ชื่อ:tag> --build-arg <KEY=VALUE> .` | build image และส่งค่าเข้าไปตอน build |
| `kind load docker-image <image...> --name lab` | ส่ง image เข้าทุก node ของคลัสเตอร์ |
