# LAB บทที่ 6: Service — ประภาคารที่ชื่อและที่อยู่ไม่เคยเปลี่ยน สู่ร้านน้องส้มที่แยก web กับ db

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Service — ปัญหาของการเรียก Pod ด้วย IP, ClusterIP และ EndpointSlice, port/targetPort/ชื่อพอร์ต, DNS/search domain/env var, การกระจายโหลดและ sessionAffinity, readinessProbe กับ endpoints, debug Service, NodePort/LoadBalancer/keep-alive, เรียกข้าม namespace, headless, ExternalName, NetworkPolicy และร้านอาหารแมวน้องส้มที่แยก web กับ db ด้วย ReplicaSet + Service
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่สร้าง **ประภาคาร (Service)** ให้ร้าน เริ่มจากเห็นด้วยตาตัวเองว่าการจด IP ของ Pod ไว้ใช้ไม่ได้ แล้วสร้าง Service ตัวแรก อ่านรายชื่อบูธใน EndpointSlice ลองพอร์ต 3 ชั้น เรียกร้านด้วยชื่อ DNS ดูการสุ่มกระจายลูกค้า ปิดไฟเขียวของบูธหนึ่ง ไล่ debug Service ที่ตั้งค่าผิด เปิดร้านจาก browser ด้วย **`http://localhost:30080`** (บทแรกที่ไม่ต้องใช้ port-forward/ssh -L) และเรียก Service ข้าม namespace ปิดท้ายด้วย **ร้านอาหารแมวน้องส้มที่แยกหน้าร้าน (web) ออกจากครัวกลาง (db) เป็นครั้งแรก** ทำให้ออเดอร์จากทุกบูธรวมที่เดียว แต่จะเผยปัญหาตอนเปลี่ยนรุ่นที่ส่งต่อให้บทที่ 7

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`: kubectl client v1.37.1, Kubernetes/Node v1.37.0, kind 0.33.0, Node เป็น Debian 13 + containerd 2.3.4) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, ClusterIP, Pod IP, ชื่อ Pod ที่สุ่ม (เช่น `web-68gh2`), จำนวนครั้งที่สุ่มได้ และ Node ที่ scheduler เลือก ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เวลาที่วัดด้วย `time` (build image, `k8s-up`, ลบ namespace) ก็ขึ้นกับความเร็วเครื่อง เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ และเมื่อคำสั่งในเอกสารมีชื่อ Pod หรือ IP ให้ **แทนด้วยค่าที่เห็นในเครื่องตัวเอง** (หรือใช้ตัวแปรตามที่เอกสารแสดง)

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิด browser ที่ `http://localhost:30080` ซึ่งทำ 🖥️/🌐 บนเครื่องนักศึกษา LAB 10 ใช้ **2 หน้าต่าง** (terminal 1 และ terminal 2) ให้เปิด SSH session ที่สองด้วยคำสั่งเดียวกัน

### กติกาของ LAB บทนี้

- ทุก LAB ทำในโฟลเดอร์ **`/workspace/006_kubernetes_service/02_LAB`** ภายใน k8s-lab (LAB 10 ย้ายเข้า `som-shop-v2/` ตามที่บอกในขั้นตอน)
- Pod ที่อยู่หลัง Service ทุก LAB สร้างด้วย **ReplicaSet** (บทที่ 5) เพราะ Service เลือก Pod ด้วย label ไม่สนว่าใครสร้าง Pod บทนี้ **ไม่ใช้** ตัวช่วยเปลี่ยนรุ่นของบทที่ 7
- **LAB 1–9 ใช้ namespace `shop` ต่อเนื่องกัน** (LAB 9 เพิ่ม `kitchen`) แล้วลบทิ้งตอนท้าย LAB 9 ส่วน LAB 10 ใช้ `som-shop` ถ้าหยุดกลางทางหรือผลเพี้ยน ให้ `kubectl delete ns shop kitchen` แล้วเริ่มใหม่จาก LAB 1 ได้ (ดู [ตารางเก็บกวาด](#ตารางเก็บกวาดและคืนสภาพ))
- **NodePort 30080 จองได้ทีละ Service ทั้งคลัสเตอร์** ต้องลบ `web-nodeport` ของ LAB 8 ก่อนเริ่ม LAB 10
- **Service ที่เพิ่งสร้างหรือเพิ่งแก้ต้องรอ kube-proxy ราว 2 วินาที** (วัดจริง: เรียกสำเร็จครั้งแรกหลังสร้าง 1.7 วินาที) ถ้าเรียกทันทีหลัง `apply`/`patch` อาจได้ `Connection refused` หรือผลเก่า เอกสารจึงใส่ `sleep 2`/`sleep 3` ไว้ในจุดที่ทดลองแล้วเจอปัญหานี้ ถ้าพิมพ์ทีละคำสั่งด้วยมือมักไม่ทันเห็น
- Pod busybox ใน LAB ตั้ง `terminationGracePeriodSeconds: 1` และ image สาธารณะ (`nginx:1.27-alpine`, `busybox:1.36`) ให้ Node ดึงเอง ไม่ต้อง `kind load`
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง (ของจริงเก็บใน Secret ซึ่งเป็นเนื้อหาบทหลัง)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์และตรวจพอร์ต 30080–30082](#lab-0-เตรียมคลัสเตอร์และตรวจพอร์ต-3008030082) | 15 นาที | ⭐ |
| 1 | [ปัญหาก่อนมี Service](#lab-1-ปัญหาก่อนมี-service) | 10 นาที | ⭐ |
| 2 | [ClusterIP แรกและ EndpointSlice](#lab-2-clusterip-แรกและ-endpointslice) | 15 นาที | ⭐ |
| 3 | [port, targetPort และชื่อพอร์ต](#lab-3-port-targetport-และชื่อพอร์ต) | 10 นาที | ⭐⭐ |
| 4 | [DNS, search domain และ env var](#lab-4-dns-search-domain-และ-env-var) | 15 นาที | ⭐⭐ |
| 5 | [การกระจายโหลดและ sessionAffinity](#lab-5-การกระจายโหลดและ-sessionaffinity) | 10 นาที | ⭐⭐ |
| 6 | [readinessProbe กับ endpoints](#lab-6-readinessprobe-กับ-endpoints) | 10 นาที | ⭐⭐ |
| 7 | [debug Service](#lab-7-debug-service) | 15 นาที | ⭐⭐⭐ |
| 8 | [NodePort 30080, LoadBalancer และ keep-alive](#lab-8-nodeport-30080-loadbalancer-และ-keep-alive) | 20 นาที | ⭐⭐⭐ |
| 9 | [ข้าม namespace, headless, ExternalName และ NetworkPolicy](#lab-9-ข้าม-namespace-headless-externalname-และ-networkpolicy) | 20 นาที | ⭐⭐⭐⭐ |
| 10 | [LAB สุดท้าย: แยก web กับ db ครั้งแรก](#lab-10-lab-สุดท้าย-แยก-web-กับ-db-ครั้งแรก) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (LAB 10 มีช่วง build image ของแอป)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมคลัสเตอร์และตรวจพอร์ต](#fig-1) | 15 | [LAB 10 สถาปัตยกรรม](#fig-15) |
| 2 | [LAB 1 IP ของ Pod เปลี่ยน](#fig-2) | 16 | [LAB 10 build image 1.2 และ 1.3](#fig-16) |
| 3 | [LAB 2 expose และ EndpointSlice](#fig-3) | 17 | [LAB 10 db และ Service som-db](#fig-17) |
| 4 | [LAB 2 EndpointSlice ตาม Pod เอง](#fig-4) | 18 | [LAB 10 เติมสินค้าแบบกันชน](#fig-18) |
| 5 | [LAB 3 พอร์ตและชื่อพอร์ต](#fig-5) | 19 | [LAB 10 เปิดร้านที่ 30080](#fig-19) |
| 6 | [LAB 4 DNS และ env var](#fig-6) | 20 | [ภาพหน้าจอจริง ร้านเวอร์ชัน 1.2](#fig-20) |
| 7 | [LAB 5 สุ่มและ sessionAffinity](#fig-7) | 21 | [LAB 10 hit.sh และออเดอร์รวม](#fig-21) |
| 8 | [LAB 6 Pod ไม่ ready](#fig-8) | 22 | [LAB 10 scale และ self-healing](#fig-22) |
| 9 | [LAB 7 debug Service](#fig-9) | 23 | [LAB 10 ลบ Pod db ข้อมูลหาย](#fig-23) |
| 10 | [LAB 8 NodePort จาก browser](#fig-10) | 24 | [ภาพหน้าจอจริง หน้า 503 หลังลบ Pod db](#fig-24) |
| 11 | [LAB 8 keep-alive และ LoadBalancer](#fig-11) | 25 | [ภาพหน้าจอจริง ร้านกลับมาแต่ออเดอร์ 0](#fig-25) |
| 12 | [LAB 9 เรียกข้าม namespace](#fig-12) | 26 | [LAB 10 เปลี่ยนรุ่นด้วยมือจนสะดุด](#fig-26) |
| 13 | [LAB 9 headless และ ExternalName](#fig-13) | 27 | [ภาพหน้าจอจริง ร้านเวอร์ชัน 1.3](#fig-27) |
| 14 | [LAB 9 NetworkPolicy ใช้ targetPort](#fig-14) | 28 | [สรุป LAB บทที่ 6](#fig-28) |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ 01–24 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
├── labs/                              ← YAML ของ LAB 1–9 (namespace shop)
│   ├── lab01-before-service/{00-ns,web-rs,client-pod}.yaml
│   ├── lab02-clusterip/web-svc.yaml
│   ├── lab03-ports/{web-alt-svc,web-multi-svc,web-multi-noname}.yaml
│   ├── lab04-dns/client2-pod.yaml
│   ├── lab07-debug/{web-typo-svc,web-badport-svc}.yaml
│   ├── lab08-nodeport/{web-nodeport,web-dup-nodeport,web-lb}.yaml
│   └── lab09-cross-ns/{kitchen,web-headless,supplier-externalname,np-kitchen-8080,np-kitchen-80}.yaml
└── som-shop-v2/                       ← LAB 10 ร้านน้องส้ม web + db แยกกัน
    ├── app/                           ← แอป Next.js + Dockerfile (build เป็น som-shop-web:1.2 และ 1.3 จากโค้ดเดียว)
    ├── k8s/{00-namespace,10-db,20-web}.yaml
    └── hit.sh                         ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน
```

LAB 0, 5 และ 6 ไม่มีไฟล์ของตัวเอง ใช้คำสั่งล้วนกับของที่สร้างใน LAB ก่อนหน้า

---

## LAB 0: เตรียมคลัสเตอร์และตรวจพอร์ต 30080–30082

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมคลัสเตอร์และตรวจพอร์ต" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: เช็กคลัสเตอร์ 3 Node, ตรวจว่า NodePort 30080–30082 ยังว่าง (ตัวอย่างจากบท 001 อาจค้าง), ดู kube-proxy mode และ Service kubernetes ที่มีอยู่แล้ว</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 5 หรือสร้างใหม่) ตรวจว่า NodePort 30080–30082 ยังว่าง และรู้จัก Service ที่มีอยู่ในคลัสเตอร์ตั้งแต่แรก

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md), [2](../../002_kubernetes_pod/02_LAB/README.md), [3](../../003_kubernetes_node_pod/02_LAB/README.md), [4](../../004_kubernetes_namespace/02_LAB/README.md) และ [5](../../005_kubernetes_replicaset/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`) และมีโฟลเดอร์ `006_kubernetes_service` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=^k8s-lab$
```

> `--filter name=` เป็นการค้นแบบ "มีคำนี้อยู่ในชื่อ" ถ้าเขียนแค่ `name=k8s-lab` จะได้ container อื่นที่ชื่อขึ้นต้นด้วย `k8s-lab-...` มาด้วย `^...$` ทำให้ตรงชื่อ `k8s-lab` เป๊ะ (บน PowerShell คำสั่งเดียวกันใช้ได้)

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `006_kubernetes_service` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 006_kubernetes_service k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ โฟลเดอร์นี้มีทั้ง YAML ของ LAB 1–9 (`02_LAB/labs/`) และแอปกับ manifest ของ LAB 10 (`02_LAB/som-shop-v2/`) จึงคัดลอกครั้งเดียวพอ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` หน้าต่างนี้คือ **terminal 1** (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/006_kubernetes_service/02_LAB
ls -R labs som-shop-v2 | head -40
kubectl get nodes
```

ผลจริง (ตัดบางส่วน)

```text
labs:
lab01-before-service
lab02-clusterip
lab03-ports
lab04-dns
lab07-debug
lab08-nodeport
lab09-cross-ns
...
NAME                STATUS   ROLES           AGE    VERSION
lab-control-plane   Ready    control-plane   104s   v1.37.0
lab-worker          Ready    <none>          94s    v1.37.0
lab-worker2         Ready    <none>          94s    v1.37.0
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 5 ยังอยู่) | **ใช้ต่อได้เลย** ตรวจด้วย `kubectl get ns` ว่าไม่มี namespace ของบทก่อนค้าง (เช่น `rs-lab`, `som-booths`) ถ้ามีให้ลบตามตารางเก็บกวาดของบทที่ 5 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `time k8s-up` (ประมาณ 1 นาที) image ที่เคย `kind load` ในบทก่อนจะหายไป LAB 10 จะ build/load ใหม่ให้ |

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
[k8s-up] cluster 'lab' พร้อมใช้งาน (kubectl context: kind-lab)
  kubectl get pods -A                       # ดู pod ทั้งหมด (alias: k get pods -A)
  kubectl apply -f /workspace/examples/web-deployment.yaml   # deploy nginx → http://localhost:30080
  ...
  NodePort ที่ map ออก host: 30080 30081 30082

real	0m50.690s
```

ในการทดลองสร้างคลัสเตอร์ใช้ราว 51 วินาที (เครื่องนักศึกษาอาจเร็วหรือช้ากว่านี้) ถ้าคลัสเตอร์มีอยู่แล้ว `k8s-up` จะพิมพ์ `[k8s-up] cluster 'lab' มีอยู่แล้ว — ข้ามการสร้าง (ลบด้วย k8s-down)` แล้วจบในไม่ถึง 1 วินาที

สังเกตสองบรรทัดท้าย: `k8s-up` แนะนำตัวอย่าง `/workspace/examples/web-deployment.yaml` ที่เปิดหน้าเว็บที่ `http://localhost:30080` และบอกว่า **NodePort 30080 30081 30082 ถูก map ออกมาที่เครื่องนักศึกษา** ทั้งสองเรื่องเกี่ยวกับบทนี้โดยตรง

### ขั้นที่ 4: ตรวจว่า NodePort 30080–30082 ยังว่าง

ถ้าเคยลองตัวอย่างของบทที่ 1 ไว้ Service ของตัวอย่างนั้นจะยังจองพอร์ต 30080 อยู่ (เลข nodePort ใช้ได้ทีละ Service ทั้งคลัสเตอร์) ทำให้ LAB 8 และ LAB 10 สร้าง Service ไม่ได้

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get svc -A | grep -E '3008[0-2]' || echo '(ว่าง)'
```

ถ้าได้ `(ว่าง)` (ผลจริงในการทดลองบนคลัสเตอร์ใหม่) ข้ามไปขั้นที่ 5 ได้เลย ถ้าเห็นบรรทัดแบบนี้ (ผลจริงจากการทดลองรอบก่อน เมื่อจำลองว่าตัวอย่างของบทที่ 1 ยังค้างอยู่)

```text
default       web          NodePort    10.96.10.17   <none>        80:30080/TCP             8s
```

ให้ลบตัวอย่างนั้นด้วยไฟล์เดียวกับที่ใช้สร้าง แล้วตรวจซ้ำ

```bash
kubectl delete -f /workspace/examples/web-deployment.yaml
kubectl get svc -A | grep -E '3008[0-2]' || echo '(ว่าง)'
```

```text
deployment.apps "web" deleted from default namespace
service "web" deleted from default namespace
(ว่าง)
```

> ตัวอย่างของบทที่ 1 สร้างทั้งตัวดูแล Pod และ Service ชื่อ `web` ใน namespace `default` การลบด้วยไฟล์เดิมจึงเอาออกทั้งสองอย่าง (บทนี้แค่ลบของเก่าออก ไม่ได้ใช้ตัวอย่างนั้น) ถ้าเห็น Service ใช้ 3008x ที่ไม่ใช่ตัวอย่างนี้ ให้ดูว่ามาจากบทไหนแล้วลบ namespace ของบทนั้น

### ขั้นที่ 5: Service ที่มีอยู่ตั้งแต่สร้างคลัสเตอร์ และ kube-proxy

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get svc -A
kubectl get svc kubernetes
kubectl -n kube-system get cm kube-proxy -o yaml | grep mode
kubectl -n kube-system get ds kube-proxy
docker exec lab-control-plane cat /kind/kubeadm.conf | grep -i serviceSubnet
```

```text
NAMESPACE     NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  103s
kube-system   kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   101s

NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   103s

    mode: iptables

NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
kube-proxy   3         3         3       3            3           kubernetes.io/os=linux   101s

  serviceSubnet: 10.96.0.0/16
```

- คลัสเตอร์มี Service อยู่แล้ว 2 ตัว: `kubernetes` (`10.96.0.1:443` ทางเข้า API server จากใน Pod) และ `kube-dns` (`10.96.0.10` DNS ของคลัสเตอร์ พอร์ต 53 UDP/TCP และ 9153 สำหรับ metrics)
- ClusterIP ทั้งหมดมาจากช่วง **Service CIDR `10.96.0.0/16`** ซึ่งแยกจาก Pod IP (`10.244.x.x`)
- **kube-proxy** เป็น DaemonSet 1 ตัวต่อ Node (3 ตัว) ทำงานโหมด **iptables**

### ขั้นที่ 6: ทำไม localhost:30080 บนเครื่องนักศึกษาจึงถึงคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cat /etc/devtools/kind/kind-lab.yaml
docker ps --format '{{.Names}}\t{{.Ports}}'
kubectl version; kind --version
```

```text
# kind-lab.yaml — kind cluster สำหรับ lab (ใช้โดย k8s-up)
#   - ชื่อคลัสเตอร์ "lab" → kubectl context = kind-lab
#   - 1 control-plane + 2 worker (ทุก node เป็น container ใน Docker-in-Docker)
#   - extraPortMappings: NodePort 30080-30082 ของ control-plane ถูก map ออกมาที่ container k8s-lab
#     (docker-compose map ต่อไปที่ host อีกชั้น → เปิด http://localhost:30080 จากเครื่องตัวเองได้)
...
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
...
  - role: worker
  - role: worker

lab-worker2	
lab-worker	
lab-control-plane	0.0.0.0:30080-30082->30080-30082/tcp, 127.0.0.1:41983->6443/tcp

Client Version: v1.37.1
Kustomize Version: v5.8.1
Server Version: v1.37.0
kind version 0.33.0
```

เส้นทางของพอร์ต 30080 ถูกเตรียมไว้ตั้งแต่บทที่ 1 แล้ว 3 ชั้น

1. 🖥️ เครื่องนักศึกษา `localhost:30080` → container `k8s-lab` (ตอนสร้าง k8s-lab ในบทที่ 1 ใช้ `docker run ... -p 30080-30082:30080-30082 ...`)
2. 🐧 `k8s-lab:30080` → container `lab-control-plane:30080` (kind `extraPortMappings` ที่เห็นใน `docker ps` ด้านบน)
3. `lab-control-plane:30080` → Pod ที่อยู่หลัง Service ชนิด NodePort ที่ใช้ `nodePort: 30080` (ยังไม่มีตอนนี้ จะสร้างใน LAB 8 และ LAB 10)

เลขพอร์ต `127.0.0.1:41983->6443` ของ API server และลำดับแถวของ `docker ps` ในเครื่องนักศึกษาจะต่างจากนี้ ไม่ต้องสนใจ ส่วน `kubectl version` บอกว่า kubectl (client) เป็น v1.37.1 และคลัสเตอร์ (server/Node) เป็น v1.37.0 ต่างกันแค่เลข patch จึงใช้ร่วมกันได้ปกติ และ kind เป็นรุ่น 0.33.0

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node พร้อม และ NodePort 30080–30082 ว่าง (ลบตัวอย่างของบทที่ 1 ออกแล้วถ้ามี)
- มี Service `kubernetes` และ `kube-dns` อยู่แล้ว ClusterIP มาจาก `10.96.0.0/16`
- kube-proxy โหมด iptables ทำงานบนทุก Node
- พอร์ต 30080–30082 ของเครื่องนักศึกษาต่อทะลุถึง `lab-control-plane` แล้ว รอแค่ Service ชนิด NodePort

**คำถามชวนคิด**

1. ถ้าลืมลบตัวอย่างของบทที่ 1 แล้วไปถึง LAB 10 จะเจอข้อความอะไร (ดูทฤษฎีหัวข้อ 6.3)
2. ทำไม kube-proxy จึงต้องมีบนทุก Node รวม control plane ด้วย ไม่ใช่แค่ Node ที่มี Pod ของเรา

---

## LAB 1: ปัญหาก่อนมี Service

<p align="center" id="fig-2">
  <img src="images/02-lab1-ip-changes.png" alt="รูปที่ 2 LAB 1 IP ของ Pod เปลี่ยน" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: ReplicaSet web (nginx) 3 replicas หน้าเว็บบอก web v1 from &lt;ชื่อ Pod&gt; — เรียกด้วย Pod IP ได้ แต่ลบ Pod แล้วตัวใหม่ได้ IP ใหม่ ที่จดไว้ใช้ไม่ได้</em>
</p>

**เป้าหมาย:** สร้างร้าน `web` 3 บูธด้วย ReplicaSet แล้วเห็นว่า IP ของ Pod เปลี่ยนเมื่อ ReplicaSet สร้าง Pod แทน IP ที่จดไว้จึงใช้ไม่ได้

### อธิบาย YAML: `labs/lab01-before-service/`

`kubectl apply -f labs/lab01-before-service/` ในขั้นที่ 1 สร้างทุกไฟล์ในโฟลเดอร์นี้ตามลำดับชื่อไฟล์ (`00-ns.yaml` ขึ้นก่อน namespace จึงมีก่อน Pod)

**`00-ns.yaml`**

```yaml
# LAB 1–9: โซน (namespace) shop ของบทนี้ — จบ LAB 9 ลบทิ้งด้วย kubectl delete ns shop
apiVersion: v1
kind: Namespace
metadata:
  name: shop               # ทุกไฟล์ของ LAB 1–9 อ้าง namespace: shop
  labels:
    team: som              # ป้ายของโซน (เทียบ team: kitchen ที่ NetworkPolicy ใช้เลือกโซนใน LAB 9)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ |
|---|---|
| `kind: Namespace`, `name: shop` | โซนเดียวที่ LAB 1–9 ใช้ร่วมกัน จบ LAB 9 ลบทั้งโซนทีเดียว (`kubectl delete ns shop kitchen` ใช้ 10.8 วินาทีในการทดลอง) |
| `labels.team: som` | ป้ายของโซน ใช้เทียบกับ `team: kitchen` ใน LAB 9 ที่ NetworkPolicy ใช้เลือกโซนต้นทาง (โซน `shop` ไม่มีป้าย `kitchen` → `client` ถูกกั้น) |

**`web-rs.yaml`** (ร้าน 3 บูธ)

```yaml
# LAB 1: ร้าน web 3 บูธ (ReplicaSet จากบท 005) — ยังไม่มี Service
# หน้าเว็บตอบ "web v1 from <ชื่อ Pod>" → เห็นทันทีว่า request ไปตกบูธไหน
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web
  namespace: shop
  labels:
    app: web                       # kubectl expose (LAB 2) คัดลอกป้ายนี้ไปให้ Service
spec:
  replicas: 3                      # ดูแลให้มี 3 บูธเสมอ (ลบ 1 ตัว → สร้างใหม่แทน แต่ได้ IP ใหม่)
  selector:
    matchLabels:
      app: web                     # ReplicaSet นับ Pod ที่มีป้ายนี้
  template:
    metadata:
      labels:
        app: web                   # Service จะเลือก Pod ด้วยป้ายนี้ (LAB 2)
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine   # image สาธารณะ — Node pull เอง ไม่ต้อง kind load
          env:
            - name: VERSION          # รุ่นของหน้าเว็บ → ข้อความ "web v1 ..."
              value: v1
          # เขียนหน้า index ให้บอกรุ่นและชื่อ Pod แล้วเปิด nginx
          command: ["sh", "-c", "echo \"web $VERSION from $(hostname)\" > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]
          ports:
            - name: http             # ตั้งชื่อพอร์ต → Service อ้าง targetPort: http ได้
              containerPort: 80
          readinessProbe:            # ไฟเขียวหน้าบูธ: ไม่ผ่าน = Service ไม่ส่งลูกค้ามา (LAB 6)
            httpGet: { path: /, port: http }
            periodSeconds: 2         # ตรวจทุก 2 วินาที (ล้ม 3 ครั้งติดกัน = not ready)
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 100m, memory: 64Mi }
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `kind: ReplicaSet`, `replicas: 3` | ดูแลให้มี 3 บูธเสมอ (บทที่ 5) | ลบ `web-qr4kg` แล้วได้ `web-68gh2` แทน แต่ IP เปลี่ยน |
| `selector.matchLabels` / `template.metadata.labels` = `app: web` | ReplicaSet นับ Pod ด้วยป้ายนี้ และ Service ใน LAB 2 ก็เลือก Pod ด้วยป้ายเดียวกัน | `client` (ป้าย `role=client`) ไม่ถูกนับเป็นบูธ |
| `metadata.labels.app: web` (ของ ReplicaSet เอง) | `kubectl expose rs web` คัดลอกป้ายนี้ไปเป็น label ของ Service | `web-quick` มี `labels: app: web` ใน LAB 2 ขั้นที่ 1 |
| `env VERSION=v1` + `command` | เขียน `index.html` เป็น `web v1 from $(hostname)` ก่อนเปิด nginx (`exec` ให้ nginx เป็น process หลัก) | ทุกคำตอบบอกชื่อ Pod เช่น `web v1 from web-qr4kg` จึงนับการกระจายได้ |
| `ports: name: http, containerPort: 80` | ตั้งชื่อพอร์ตไว้ให้ Service อ้าง `targetPort: http` แทนเลข | LAB 2–3 ใช้ `targetPort: http` (EndpointSlice แปลงเป็น PORTS `80`) |
| `readinessProbe httpGet / port http`, `periodSeconds: 2` | ไฟเขียวของบูธ ตรวจหน้าแรกทุก 2 วินาที (`failureThreshold` ค่าเริ่มต้น 3) | LAB 6 ลบ `index.html` → 403 → `ready=false` ในราว 6 วินาที |
| `resources` | จองทรัพยากรเล็กน้อยให้ 3 บูธ + ลูกค้ารันบนเครื่องนักศึกษาได้สบาย | – |

**`client-pod.yaml`** (ลูกค้าในคลัสเตอร์)

```yaml
# LAB 1: Pod ลูกค้า (busybox) ไว้ยิง wget/nslookup จากในคลัสเตอร์
# สร้าง "ก่อน" Service → ไม่มี env WEB_SERVICE_HOST (เทียบใน LAB 4)
apiVersion: v1
kind: Pod                            # Pod เดี่ยว ไม่มี ReplicaSet ดูแล (เป็นลูกค้า ไม่ใช่บูธ)
metadata:
  name: client
  namespace: shop
  labels:
    role: client                     # ไม่มี app=web → ReplicaSet/Service web ไม่นับ Pod นี้
spec:
  terminationGracePeriodSeconds: 1   # ลบแล้วหายเร็ว
  containers:
    - name: busybox
      image: busybox:1.36            # มี wget, nslookup, ping ในตัว
      command: ["sleep", "infinity"] # อยู่เฉย ๆ ให้ kubectl exec เข้ามายิงคำสั่ง
      resources:                     # จองทรัพยากรเล็กน้อย
        requests: { cpu: 10m, memory: 16Mi }
        limits:   { cpu: 100m, memory: 32Mi }
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ |
|---|---|
| `kind: Pod` (ไม่มี ReplicaSet) | ลูกค้าตัวเดียว ไม่ใช่บูธ ใช้ยิงคำสั่งด้วย `kubectl exec` ไปจนถึง LAB 9 |
| `labels.role: client` | ไม่มี `app=web` จึงไม่อยู่ใน EndpointSlice ของ `web` (LAB 2 เห็นแค่ 3 IP ของ `web-*`) |
| `image: busybox:1.36`, `command: sleep infinity` | busybox มี `wget`, `nslookup`, `ping` ในตัว และ `sleep infinity` ทำให้ container อยู่ไปเรื่อย ๆ |
| `terminationGracePeriodSeconds: 1` | ไม่ต้องรอ 30 วินาทีตอนลบ namespace |
| (สร้างก่อน Service) | ไม่มี env `WEB_*` (LAB 4 ขั้นที่ 3 ได้ `exit=1`) |

### ขั้นที่ 1: สร้าง namespace, ร้าน 3 บูธ และลูกค้า

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `/workspace/006_kubernetes_service/02_LAB`)

```bash
kubectl apply -f labs/lab01-before-service/
kubectl -n shop wait --for=condition=Ready pod -l app=web --timeout=120s
kubectl -n shop wait --for=condition=Ready pod/client --timeout=120s
kubectl -n shop get rs,pods -o wide --show-labels
```

```text
namespace/shop created
pod/client created
replicaset.apps/web created
pod/web-ljmt4 condition met
pod/web-qr4kg condition met
pod/web-rppf4 condition met
pod/client condition met

NAME                  DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES              SELECTOR   LABELS
replicaset.apps/web   3         3         3       15s   nginx        nginx:1.27-alpine   app=web    app=web

NAME            READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES   LABELS
pod/client      1/1     Running   0          15s   10.244.2.2   lab-worker2   <none>           <none>            role=client
pod/web-ljmt4   1/1     Running   0          15s   10.244.1.2   lab-worker    <none>           <none>            app=web
pod/web-qr4kg   1/1     Running   0          15s   10.244.2.3   lab-worker2   <none>           <none>            app=web
pod/web-rppf4   1/1     Running   0          15s   10.244.2.4   lab-worker2   <none>           <none>            app=web
```

ครั้งแรก Node ต้องดึง image `nginx` และ `busybox` จาก Docker Hub จึงใช้เวลาราว 10–20 วินาที (ในการทดลอง `wait` ของ `web` ใช้ 10 วินาที) ชื่อ Pod, IP และ Node ที่ scheduler เลือก (รอบนี้ 2 บูธ + `client` อยู่ `lab-worker2`) ในเครื่องนักศึกษาจะต่างจากนี้

### ขั้นที่ 2: เรียกบูธด้วย Pod IP แล้วลบบูธนั้น

เลือก Pod `web` ตัวหนึ่งจากผลของขั้นที่ 1 แล้ว **แทน `10.244.2.3` และ `web-qr4kg` ด้วย IP และชื่อในเครื่องตัวเอง**

```bash
kubectl -n shop exec client -- wget -qO- http://10.244.2.3
kubectl -n shop delete pod web-qr4kg
kubectl -n shop exec client -- wget -qO- -T 3 http://10.244.2.3; echo "exit=$?"
kubectl -n shop get pods -o wide
```

```text
web v1 from web-qr4kg
pod "web-qr4kg" deleted from shop namespace
wget: download timed out
command terminated with exit code 1
exit=1
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          20s   10.244.2.2   lab-worker2   <none>           <none>
web-68gh2   1/1     Running   0          5s    10.244.2.5   lab-worker2   <none>           <none>
web-ljmt4   1/1     Running   0          20s   10.244.1.2   lab-worker    <none>           <none>
web-rppf4   1/1     Running   0          20s   10.244.2.4   lab-worker2   <none>           <none>
```

- หน้าเว็บบอก `web v1 from web-qr4kg` คือชื่อ Pod ที่ตอบ (มาจาก `$(hostname)` ใน command ของ container)
- หลังลบ ReplicaSet สร้าง `web-68gh2` แทนภายในไม่กี่วินาที แต่ได้ **ชื่อใหม่และ IP ใหม่** (`10.244.2.5`)
- เรียก IP เดิมได้ `wget: download timed out` (ใช้ `-T 3` ให้รอแค่ 3 วินาที) ถ้า IP เดิมบังเอิญถูก Pod อื่นนำไปใช้ อาจได้คำตอบจาก Pod ที่ไม่เกี่ยวข้องหรือ `Connection refused` แทน ซึ่งแย่กว่าเพราะดูเหมือนใช้ได้

### สิ่งที่เห็น

- ReplicaSet แก้ปัญหา "จำนวน" (ยังมี 3 บูธ) แต่ไม่แก้ปัญหา "ที่อยู่" ลูกค้าที่จด IP ไว้หาร้านไม่เจอ
- เราจะใช้ Pod `client` ตัวนี้เป็นลูกค้าในคลัสเตอร์ต่อไปจนถึง LAB 9 (อย่าลบ)

**คำถามชวนคิด**

1. ถ้ามีแอปอื่นจด IP `10.244.1.2` ของ `web-ljmt4` ไว้ แล้วน้องส้ม scale ReplicaSet ลงเหลือ 2 แอปนั้นจะเจออะไร
2. ทำไม Pod `client` จึงไม่ถูกนับเป็นบูธของ ReplicaSet `web`

---

## LAB 2: ClusterIP แรกและ EndpointSlice

<p align="center" id="fig-3">
  <img src="images/03-lab2-expose-endpointslice.png" alt="รูปที่ 3 LAB 2 expose และ EndpointSlice" width="900"><br>
  <em><b>รูปที่ 3</b> LAB2: kubectl expose rs web (เทียบกับเขียน YAML) → ได้ Service ClusterIP และ EndpointSlice ที่มี IP ของ Pod ทั้ง 3; get endpoints ขึ้นคำเตือน deprecated</em>
</p>

**เป้าหมาย:** สร้าง Service 2 วิธี อ่าน EndpointSlice ที่ระบบเขียนให้ และเห็นว่ารายชื่อบูธตาม Pod เองในขณะที่ ClusterIP ไม่เปลี่ยน

**ต้องมีจาก LAB 1:** namespace `shop`, ReplicaSet `web` 3 บูธ และ Pod `client`

### ขั้นที่ 1: สร้าง Service ด้วย kubectl expose แล้วลบ

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl -n shop expose rs web --port=80 --name=web-quick
kubectl -n shop get svc web-quick -o yaml
kubectl -n shop delete svc web-quick
```

```text
service/web-quick exposed
apiVersion: v1
kind: Service
metadata:
  ...
  labels:
    app: web
  name: web-quick
  namespace: shop
  ...
spec:
  clusterIP: 10.96.62.255
  clusterIPs:
  - 10.96.62.255
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: web
  sessionAffinity: None
  type: ClusterIP
status:
  loadBalancer: {}
service "web-quick" deleted from shop namespace
```

`expose` คัดลอก selector (`app: web`) และ label จาก ReplicaSet มาให้ และ API เติมค่าเริ่มต้นหลายอย่าง สังเกตว่า **`targetPort: 80` เป็นตัวเลข** ไม่ใช่ชื่อพอร์ต `http` เราจะใช้ไฟล์ YAML ที่ใช้ชื่อพอร์ตแทน

### ขั้นที่ 2: สร้าง Service จาก YAML

#### อธิบาย YAML: `labs/lab02-clusterip/web-svc.yaml`

```yaml
# LAB 2: Service แรก — ClusterIP (ค่าเริ่มต้น) ชื่อ web
# ชื่อ "web" + IP เสมือน (ClusterIP) คงที่ ส่งต่อไป Pod ที่มีป้าย app=web และ Ready
apiVersion: v1
kind: Service
metadata:
  name: web                # ชื่อนี้กลายเป็นชื่อ DNS web.shop.svc.cluster.local
  namespace: shop
spec:
  type: ClusterIP          # ไม่ใส่ก็ได้ (ค่าเริ่มต้น)
  selector:
    app: web               # เลือก Pod ด้วย label (ไม่สนว่าใครสร้าง Pod)
  ports:
    - port: 80             # พอร์ตที่ Service รับ (http://web:80)
      targetPort: http     # พอร์ตของ container (ชื่อ http = containerPort 80)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `kind: Service`, `name: web` | สร้าง "ประภาคาร" ชื่อ `web` ชื่อนี้กลายเป็นชื่อ DNS `web.shop.svc.cluster.local` | `wget http://web` ได้ (ขั้นที่ 4), LAB 4 `nslookup` ได้ ClusterIP `10.96.24.101` |
| `namespace: shop` | Service เลือก Pod ได้เฉพาะในโซนเดียวกัน | โซนอื่นต้องเรียก `web.shop` (LAB 9) |
| `type: ClusterIP` | ค่าเริ่มต้น ได้ IP เสมือนจากช่วง `10.96.0.0/16` ใช้ได้เฉพาะในคลัสเตอร์ | ได้ `10.96.24.101` ping ไม่ตอบแต่ wget ได้ |
| `selector: app: web` | เลือก Pod ด้วยป้าย (ไม่สนว่า ReplicaSet ไหนสร้าง) ระบบเขียน EndpointSlice ให้จาก Pod ที่ตรง | EndpointSlice `web-fqgqh` มี 3 IP ของ `web-*` ไม่มี `client` |
| `port: 80` | พอร์ตที่ลูกค้าเรียกบน ClusterIP / ชื่อ Service (`http://web` = พอร์ต 80) | `PORT(S) 80/TCP` |
| `targetPort: http` | ส่งต่อไปพอร์ต **ชื่อ** `http` ของ container (= 80 ใน `web-rs.yaml`) ถ้าวันหน้าเปลี่ยนเลขพอร์ตใน Pod ไม่ต้องแก้ Service | `describe svc` แสดง `TargetPort: http/TCP` ส่วน EndpointSlice แปลงเป็นเลข PORTS `80` |
| (ไม่ได้ตั้ง `name` ให้พอร์ต) | Service พอร์ตเดียวไม่บังคับตั้งชื่อ | `describe` แสดง `Port: <unset>  80/TCP` และไม่มี env `WEB_SERVICE_PORT_HTTP` (LAB 4) |

```bash
kubectl apply -f labs/lab02-clusterip/web-svc.yaml
kubectl -n shop get svc,endpointslice
kubectl -n shop get pods -o wide
kubectl -n shop get endpoints web
kubectl -n shop describe svc web
```

```text
service/web created
NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/web   ClusterIP   10.96.24.101   <none>        80/TCP    0s

NAME                                       ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
endpointslice.discovery.k8s.io/web-fqgqh   IPv4          80      10.244.2.4,10.244.1.2,10.244.2.5   0s

NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          20s   10.244.2.2   lab-worker2   <none>           <none>
web-68gh2   1/1     Running   0          5s    10.244.2.5   lab-worker2   <none>           <none>
web-ljmt4   1/1     Running   0          20s   10.244.1.2   lab-worker    <none>           <none>
web-rppf4   1/1     Running   0          20s   10.244.2.4   lab-worker2   <none>           <none>

Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                                   AGE
web    10.244.1.2:80,10.244.2.4:80,10.244.2.5:80   0s

Name:                     web
Namespace:                shop
Labels:                   <none>
Annotations:              <none>
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.24.101
IPs:                      10.96.24.101
Port:                     <unset>  80/TCP
TargetPort:               http/TCP
Endpoints:                10.244.2.4:80,10.244.1.2:80,10.244.2.5:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
```

- Service `web` ได้ ClusterIP `10.96.24.101` (ในเครื่องนักศึกษาจะเป็นเลขอื่นในช่วง `10.96.x.x`) **จดไว้** จะใช้ในขั้นที่ 4
- EndpointSlice ชื่อ `web-fqgqh` (ชื่อ Service + สุ่ม) มี 3 IP ตรงกับ Pod `web-*` ไม่มี `client` เพราะ label ไม่ตรง (ลำดับ IP ในแต่ละคำสั่งอาจไม่เหมือนกัน `get endpoints` เรียงตามเลข ส่วน EndpointSlice เรียงตามที่ controller เขียน)
- `kubectl get endpoints` ยังใช้ได้แต่ขึ้นคำเตือนว่าเลิกใช้แล้ว ให้ใช้ EndpointSlice แทน

### ขั้นที่ 3: อ่าน EndpointSlice แบบเต็ม

```bash
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o yaml
```

ผลจริง (ตัด endpoint ตัวที่ 2–3 และ uid ออก)

```text
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.2.4
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: lab-worker2
    targetRef:
      kind: Pod
      name: web-rppf4
      namespace: shop
  ...
  kind: EndpointSlice
  metadata:
    ...
    generateName: web-
    generation: 1
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web
    name: web-fqgqh
    namespace: shop
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: web
  ...
  ports:
  - name: ""
    port: 80
    protocol: TCP
```

หาให้เจอในผลของตัวเอง: `conditions` 3 ค่าของแต่ละ endpoint, `targetRef` ที่ชี้ชื่อ Pod, label `kubernetes.io/service-name: web` (ที่ใช้ค้น) และ `ownerReferences` ที่ชี้ **Service** `web` (ลบ Service แล้ว slice นี้หายตาม)

### ขั้นที่ 4: เรียกด้วยชื่อ และลอง ping ClusterIP

แทน `10.96.24.101` ด้วย ClusterIP ของตัวเอง และ `10.244.2.5` ด้วย IP ของ Pod `web` ตัวหนึ่ง

> ⚠️ **รอ kube-proxy ก่อนเรียก:** ถ้ารันขั้นนี้ต่อจาก `kubectl apply` ทันที (เช่นคัดลอกทั้งชุดไปวางรวดเดียว) ให้ `sleep 2` ก่อน ในการทดลองที่เรียกหลังสร้าง Service ไม่ถึง 1 วินาที ได้ `wget: can't connect to remote host (10.96.24.101): Connection refused` เพราะ kube-proxy ยังเขียนกฎไม่เสร็จ (วัดได้ว่าใช้ราว 1.7 วินาที) เรียกซ้ำแล้วได้ปกติ

```bash
sleep 2     # จำเป็นเฉพาะเมื่อเพิ่ง apply Service
kubectl -n shop exec client -- wget -qO- http://web
kubectl -n shop exec client -- ping -c 2 -W 2 10.96.24.101; echo "exit=$?"
kubectl -n shop exec client -- ping -c 2 -W 2 10.244.2.5
```

```text
web v1 from web-rppf4

PING 10.96.24.101 (10.96.24.101): 56 data bytes

--- 10.96.24.101 ping statistics ---
2 packets transmitted, 0 packets received, 100% packet loss
command terminated with exit code 1
exit=1

PING 10.244.2.5 (10.244.2.5): 56 data bytes
64 bytes from 10.244.2.5: seq=0 ttl=63 time=0.191 ms
64 bytes from 10.244.2.5: seq=1 ttl=63 time=0.089 ms

--- 10.244.2.5 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.089/0.140/0.191 ms
```

(บรรทัด `web v1 from web-rppf4` มาจากการเรียกซ้ำหลังรอ ในการทดลองที่ไม่มี `sleep 2` ครั้งแรกที่เรียกทันทีได้ `Connection refused` ตามคำเตือนด้านบน ชื่อ Pod ที่ตอบเป็นการสุ่ม)

`wget http://web` ได้หน้าเว็บด้วย **ชื่อ** แต่ ping ClusterIP ได้ 100% packet loss ส่วน ping Pod IP ได้ปกติ เพราะ ClusterIP เป็นที่อยู่เสมือนที่ไม่มีเครื่องใดถือจริง (ทฤษฎีหัวข้อ 2.2) **ping ไม่ตอบไม่ได้แปลว่า Service เสีย**

### ขั้นที่ 5: scale และลบ Pod แล้วดูรายชื่อเปลี่ยนเอง

<p align="center" id="fig-4">
  <img src="images/04-lab2-scale-endpoints-follow.png" alt="รูปที่ 4 LAB 2 EndpointSlice ตาม Pod เอง" width="900"><br>
  <em><b>รูปที่ 4</b> LAB2 (ต่อ): scale ReplicaSet 3→5 หรือ ลบ Pod → EndpointSlice เปลี่ยนตามเอง ClusterIP ไม่เปลี่ยน</em>
</p>

```bash
kubectl -n shop scale rs web --replicas=5
kubectl -n shop wait --for=condition=Ready pod -l app=web --timeout=60s >/dev/null
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
```

```text
replicaset.apps/web scaled
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-fqgqh   IPv4          80      10.244.2.4,10.244.1.2,10.244.2.5 + 2 more...   28s
```

คอลัมน์ ENDPOINTS แสดงแค่ 3 IP แรกแล้วต่อด้วย `+ 2 more...` (แม้ใช้ `-o wide`) ดูครบทุกตัวด้วย jsonpath

```bash
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
```

```text
10.244.2.4 web-rppf4 ready=true
10.244.1.2 web-ljmt4 ready=true
10.244.2.5 web-68gh2 ready=true
10.244.1.3 web-9d2ks ready=true
10.244.2.6 web-fbmpj ready=true
```

จากนั้นลบ Pod ตัวหนึ่ง (แทน `web-ljmt4` ด้วยชื่อในเครื่องตัวเอง ในการทดลองเลือกตัวที่เก่าที่สุด) แล้วดูรายชื่อก่อนและหลังรอ 3 วินาที เทียบกับ ClusterIP

```bash
kubectl -n shop delete pod web-ljmt4
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
sleep 3; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
kubectl -n shop get svc web
```

```text
pod "web-ljmt4" deleted from shop namespace
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-fqgqh   IPv4          80      10.244.2.4,10.244.2.5,10.244.1.3 + 2 more...   29s
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-fqgqh   IPv4          80      10.244.2.4,10.244.2.5,10.244.1.3 + 2 more...   33s
NAME   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
web    ClusterIP   10.96.24.101   <none>        80/TCP    33s
```

IP `10.244.1.2` ของ Pod ที่ถูกลบหายจากรายชื่อทันที Pod ใหม่เข้ามาแทน (ยังเห็น `+ 2 more...` คือครบ 5) ส่วน **ClusterIP ยังเป็นเลขเดิม** ลูกค้าที่เรียก `web` ไม่ต้องรู้เรื่องนี้เลย

คืนเป็น 3 บูธ

```bash
kubectl -n shop scale rs web --replicas=3
sleep 2; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
kubectl -n shop get pods -o wide
```

```text
replicaset.apps/web scaled
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-fqgqh   IPv4          80      10.244.2.4,10.244.2.5,10.244.2.6   35s
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          55s   10.244.2.2   lab-worker2   <none>           <none>
web-68gh2   1/1     Running   0          40s   10.244.2.5   lab-worker2   <none>           <none>
web-fbmpj   1/1     Running   0          9s    10.244.2.6   lab-worker2   <none>           <none>
web-rppf4   1/1     Running   0          55s   10.244.2.4   lab-worker2   <none>           <none>
```

ตอน scale ลง ReplicaSet เลือกลบบูธเองตามกติกาของบทที่ 5 รอบนี้เหลือ 3 บูธอยู่ `lab-worker2` ทั้งหมด (ในเครื่องนักศึกษาอาจกระจายต่างจากนี้) จำชื่อบูธ `web-rppf4` (เกิดก่อน Service) และ `web-fbmpj` (เกิดหลัง Service ตอน scale) ไว้ใช้ใน LAB 4

### สิ่งที่เห็น

- `kubectl expose` สร้าง Service ได้เร็วแต่ใส่ targetPort เป็นเลข ไฟล์ YAML ควบคุมได้ละเอียดกว่า
- EndpointSlice ถูกเขียนให้อัตโนมัติ มี IP ของ Pod ที่ตรง selector, conditions, targetRef และ ownerReferences ชี้ Service
- ClusterIP ping ไม่ตอบ แต่เรียกด้วยชื่อ/พอร์ตของ Service ได้ (Service ที่เพิ่งสร้างต้องรอ kube-proxy ราว 2 วินาที)
- scale หรือลบ Pod แล้วรายชื่อเปลี่ยนเอง ClusterIP ไม่เปลี่ยน

**คำถามชวนคิด**

1. ถ้าลบ Service `web` แล้ว apply ใหม่ ClusterIP จะเหมือนเดิมไหม แอปที่เรียกด้วยชื่อ `web` จะกระทบไหม
2. ทำไม PORTS ของ EndpointSlice จึงเป็น `80` ทั้งที่ Service ใช้ `targetPort: http`

---

## LAB 3: port, targetPort และชื่อพอร์ต

<p align="center" id="fig-5">
  <img src="images/05-lab3-ports-named.png" alt="รูปที่ 5 LAB 3 พอร์ตและชื่อพอร์ต" width="900"><br>
  <em><b>รูปที่ 5</b> LAB3: Service web-alt port 8080 → targetPort: http (ชื่อพอร์ตของ container = 80) และ Service หลายพอร์ตที่ต้องตั้งชื่อทุกพอร์ต; ไม่ใส่ชื่อ → apply ไม่ผ่าน</em>
</p>

**เป้าหมาย:** เข้าใจพอร์ต 3 ชั้นด้วย Service ที่รับคนละพอร์ตกับ Pod และ Service หลายพอร์ตที่ต้องตั้งชื่อ

**ต้องมีจาก LAB 2:** Service `web` และ Pod `client`

### ขั้นที่ 1: Service รับ 8080 ส่งต่อ 80

#### อธิบาย YAML: `labs/lab03-ports/web-alt-svc.yaml`

```yaml
# LAB 3: Service รับที่พอร์ต 8080 แต่ส่งต่อไปพอร์ต 80 (ชื่อ http) ของ Pod
apiVersion: v1
kind: Service
metadata:
  name: web-alt
  namespace: shop
spec:
  selector:
    app: web               # บูธชุดเดียวกับ Service web (Pod หนึ่งอยู่หลังหลาย Service ได้)
  ports:
    - port: 8080           # ลูกค้าเรียก http://web-alt:8080
      targetPort: http     # → containerPort ชื่อ http (80)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `selector: app: web` | บูธชุดเดียวกับ Service `web` Pod หนึ่งตัวอยู่หลังหลาย Service ได้ | ได้ `web v1 from web-rppf4` เหมือนเรียก `web` |
| `port: 8080` | พอร์ตที่ลูกค้าเรียก **ฝั่ง Service** มีแค่พอร์ตนี้พอร์ตเดียว | `PORT(S) 8080/TCP`, เรียก `web-alt` พอร์ต 80 ได้ `download timed out` |
| `targetPort: http` | kube-proxy แปลง `ClusterIP:8080 → Pod:80` (พอร์ตชื่อ `http`) | `web-alt:8080` ได้หน้าเว็บ และ LAB 9 ใช้ Service นี้พิสูจน์ว่า NetworkPolicy เห็นพอร์ต 80 ไม่ใช่ 8080 |
| (ไม่ใส่ `type`) | ได้ `ClusterIP` เป็นค่าเริ่มต้น | `TYPE ClusterIP` |

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab03-ports/web-alt-svc.yaml
kubectl -n shop get svc web-alt
sleep 2     # รอ kube-proxy เขียนกฎของ Service ใหม่
kubectl -n shop exec client -- wget -qO- http://web-alt:8080
time kubectl -n shop exec client -- wget -qO- -T 3 http://web-alt; echo "exit=$?"
```

```text
service/web-alt created
NAME      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
web-alt   ClusterIP   10.96.142.94   <none>        8080/TCP   0s
web v1 from web-rppf4
wget: download timed out
command terminated with exit code 1

real	0m3.171s
user	0m0.039s
sys	0m0.039s
exit=1
```

`web-alt:8080` ได้หน้าเว็บ (kube-proxy แปลง `8080 → 80` ให้) แต่เรียก `web-alt` เฉย ๆ (พอร์ต 80) **เงียบจนครบ 3 วินาที** (`download timed out`) ไม่ใช่ถูกปฏิเสธ เพราะ Service นี้ไม่ได้ประกาศพอร์ต 80 จึงไม่มีกฎรองรับ

> ⚠️ ในการทดลองที่เรียก `web-alt:8080` หลัง `apply` เพียง 0.2 วินาที (ไม่มี `sleep 2`) ได้ `wget: can't connect to remote host (10.96.142.94): Connection refused` เรียกซ้ำจึงได้ `web v1 from web-rppf4` ที่แสดงด้านบน ถ้าเจอแบบนี้ให้รอ 2 วินาทีแล้วลองใหม่

### ขั้นที่ 2: Service หลายพอร์ต

#### อธิบาย YAML: `labs/lab03-ports/web-multi-svc.yaml`

```yaml
# LAB 3: Service หลายพอร์ต — ต้องตั้ง name ให้ทุกพอร์ต
apiVersion: v1
kind: Service
metadata:
  name: web-multi
  namespace: shop
spec:
  selector:
    app: web
  ports:
    - name: http           # ชื่อพอร์ต → env WEB_MULTI_SERVICE_PORT_HTTP และชื่อใน EndpointSlice
      port: 80
      targetPort: http
    - name: alt            # พอร์ตที่ 2 ต้องมีชื่อไม่ซ้ำ (ไม่ใส่ = API ปฏิเสธ ดูขั้นที่ 3)
      port: 8080
      targetPort: http     # สองพอร์ตของ Service ชี้ไปพอร์ตเดียวกันของ Pod ได้
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `ports[0]`: `name: http`, `port: 80` | พอร์ตแรกของ Service | `PORT(S) 80/TCP,8080/TCP`, env `WEB_MULTI_SERVICE_PORT_HTTP=80` (LAB 4) |
| `ports[1]`: `name: alt`, `port: 8080` | พอร์ตที่สอง Service ที่มีหลายพอร์ต **ต้องตั้งชื่อทุกพอร์ตและห้ามซ้ำ** | env `WEB_MULTI_SERVICE_PORT_ALT=8080`; ไม่ตั้งชื่อ → ขั้นที่ 3 |
| `targetPort: http` ทั้งสองพอร์ต | สองพอร์ตของ Service ชี้ไปพอร์ตเดียวกันของ Pod ได้ | EndpointSlice PORTS `80,80` และ `ports` มีชื่อ `alt`, `http` |

```bash
kubectl apply -f labs/lab03-ports/web-multi-svc.yaml
kubectl -n shop get svc web-multi
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-multi
kubectl -n shop exec client -- wget -qO- http://web-multi
kubectl -n shop exec client -- wget -qO- http://web-multi:8080
```

ผลจริงเมื่อรันทั้งชุดต่อกันทันที (ไม่ได้รอ)

```text
service/web-multi created
NAME        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)           AGE
web-multi   ClusterIP   10.96.196.78   <none>        80/TCP,8080/TCP   0s
NAME              ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-multi-7f4bn   IPv4          80,80   10.244.2.6,10.244.2.4,10.244.2.5   0s
wget: can't connect to remote host (10.96.196.78): Connection refused
command terminated with exit code 1
wget: can't connect to remote host (10.96.196.78): Connection refused
command terminated with exit code 1
```

อาจได้ `Connection refused` หนึ่งหรือทั้งสองครั้ง (ในผลด้านบนได้ทั้งสองครั้ง) เพราะเรียกหลังสร้างเสร็จไม่ถึง 1 วินาที kube-proxy ยังเขียนกฎไม่เสร็จ (ครั้งที่สองค้างราว 21 วินาทีก่อนขึ้น error ในการทดลอง) **ถ้าเจอแบบนี้ให้ `sleep 2` แล้วลองซ้ำ** ผลจริงเมื่อเรียกซ้ำ และดูพอร์ตใน EndpointSlice

```bash
sleep 2
for i in 1 2 3; do kubectl -n shop exec client -- wget -qO- http://web-multi; done
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-multi -o jsonpath="{.items[0].ports}"; echo
```

```text
web v1 from web-fbmpj
web v1 from web-rppf4
web v1 from web-fbmpj
[{"name":"alt","port":80,"protocol":"TCP"},{"name":"http","port":80,"protocol":"TCP"}]
```

EndpointSlice เก็บพอร์ตแยกตามชื่อของพอร์ต Service (`alt`, `http`) ทั้งคู่ชี้ไปพอร์ต 80 ของ Pod คอลัมน์ PORTS จึงเป็น `80,80`

### ขั้นที่ 3: ลืมตั้งชื่อพอร์ต

#### อธิบาย YAML: `labs/lab03-ports/web-multi-noname.yaml` (ตั้งใจผิด)

```yaml
# LAB 3 (ตั้งใจผิด): หลายพอร์ตแต่พอร์ตที่ 2 ไม่ตั้ง name → API ปฏิเสธ
apiVersion: v1
kind: Service
metadata:
  name: web-noname
  namespace: shop
spec:
  selector:
    app: web
  ports:
    - name: http           # ports[0] มีชื่อ
      port: 80
      targetPort: http
    - port: 8080           # ← ไม่มี name (ports[1])
      targetPort: http
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `ports[0]` มี `name: http` | พอร์ตแรกถูกต้อง | – |
| `ports[1]` ไม่มี `name` | ตั้งใจลืมชื่อ ให้เห็นกฎ "หลายพอร์ตต้องมีชื่อ" ซึ่ง API ตรวจตอนสร้าง | `spec.ports[1].name: Required value` และ Service ไม่ถูกสร้าง |

```bash
kubectl apply -f labs/lab03-ports/web-multi-noname.yaml; echo "exit=$?"
```

```text
The Service "web-noname" is invalid: spec.ports[1].name: Required value
exit=1
```

API ปฏิเสธตั้งแต่ตอนสร้าง (`ports[1]` คือพอร์ตลำดับที่ 2 นับจาก 0) Service `web-noname` จึงไม่ถูกสร้าง

### สิ่งที่เห็น

- `port` (ของ Service) กับ `targetPort` (ของ Pod) ต่างกันได้ เรียกพอร์ตที่ Service ไม่ได้ประกาศจะ timeout
- Service หลายพอร์ตต้องตั้งชื่อทุกพอร์ต สองพอร์ตชี้ไปพอร์ตเดียวกันของ Pod ได้
- Service ที่เพิ่งสร้างอาจตอบ `Connection refused` ในราว 1–2 วินาทีแรก (รอ `sleep 2` แล้วลองซ้ำ)

**คำถามชวนคิด**

1. ถ้าวันหนึ่ง nginx ใน Pod เปลี่ยนไปฟังพอร์ต 8080 แต่ยังตั้งชื่อ `http` Service `web`, `web-alt`, `web-multi` ต้องแก้ไหม
2. Service `web-quick` ที่สร้างด้วย `expose` ใน LAB 2 (targetPort `80`) จะเป็นอย่างไรในสถานการณ์ข้อ 1

---

## LAB 4: DNS, search domain และ env var

<p align="center" id="fig-6">
  <img src="images/06-lab4-dns-env.png" alt="รูปที่ 6 LAB 4 DNS และ env var" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4: nslookup web.shop.svc.cluster.local ได้ ClusterIP (ชื่อสั้น web ก็หาเจอ แต่ nslookup ของ busybox พิมพ์บรรทัด NXDOMAIN ปนและจบด้วย exit 1), ดู resolv.conf; Pod ที่สร้างก่อน Service ไม่มี WEB_SERVICE_HOST แต่ Pod ใหม่มี</em>
</p>

**เป้าหมาย:** เรียก Service ด้วยชื่อ เข้าใจ search domain และ `ndots` และเห็นว่า env var ของ Service มีเฉพาะ Pod ที่สร้างหลัง Service

**ต้องมีจาก LAB 3:** Service `web`, `web-alt`, `web-multi` และ Pod `client`

### ขั้นที่ 1: nslookup ชื่อสั้นและชื่อเต็ม

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl -n shop exec client -- nslookup web
kubectl -n shop exec client -- nslookup web.shop.svc.cluster.local
```

```text
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find web.cluster.local: NXDOMAIN

Name:	web.shop.svc.cluster.local
Address: 10.96.24.101

** server can't find web.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN


** server can't find web.svc.cluster.local: NXDOMAIN

command terminated with exit code 1

Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web.shop.svc.cluster.local
Address: 10.96.24.101

```

- `nslookup web` **หาเจอ** (`web.shop.svc.cluster.local` → ClusterIP ของ `web`) แต่ `nslookup` ของ busybox ถามทุก search domain พร้อมกันแล้วพิมพ์ทุกผล จึงมีบรรทัด `NXDOMAIN` ของโดเมนที่ไม่ตรงปนอยู่ และจบด้วย `exit code 1` **ไม่ได้แปลว่า DNS เสีย** ลำดับบรรทัดเปลี่ยนได้ทุกครั้งที่รัน (ขึ้นกับว่าคำตอบไหนกลับมาก่อน)
- ชื่อเต็ม `web.shop.svc.cluster.local` ได้ผลสะอาด ใช้ชื่อเต็มเมื่อทดสอบด้วย `nslookup` ของ busybox
- `Server: 10.96.0.10` คือ ClusterIP ของ `kube-dns` ที่เห็นใน LAB 0

### ขั้นที่ 2: resolv.conf และชื่อที่มีจุด

```bash
kubectl -n shop exec client -- cat /etc/resolv.conf
kubectl -n shop exec client -- nslookup web.shop
kubectl -n shop exec client -- wget -qO- http://web.shop
kubectl -n shop exec client -- wget -qO- http://web.shop.svc.cluster.local.
```

```text
search shop.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5

Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find web.shop: NXDOMAIN

** server can't find web.shop: NXDOMAIN

command terminated with exit code 1

web v1 from web-68gh2

web v1 from web-rppf4
```

- `search` ขึ้นต้นด้วย namespace ของ Pod (`shop.svc.cluster.local`) ชื่อสั้น `web` จึงกลายเป็น `web.shop.svc.cluster.local`
- `ndots:5`: ชื่อที่มีจุดน้อยกว่า 5 ถูกลองเติม search domain ก่อน `wget http://web.shop` จึงใช้ได้ (เติม `.svc.cluster.local`)
- แต่ `nslookup web.shop` ของ busybox ได้ NXDOMAIN เพราะ busybox ไม่เติม search domain ให้ชื่อที่มีจุด เป็นข้อจำกัดของเครื่องมือ ไม่ใช่ของคลัสเตอร์
- ชื่อเต็มลงท้ายจุด (`web.shop.svc.cluster.local.`) ข้ามการเติม search ทั้งหมด

### ขั้นที่ 3: env var ของ Service

Pod `client` ถูกสร้างใน LAB 1 **ก่อน** มี Service ส่วน `client2` จะสร้าง **หลัง** Service `web`, `web-alt`, `web-multi`

#### อธิบาย YAML: `labs/lab04-dns/client2-pod.yaml`

```yaml
# LAB 4: Pod ลูกค้าตัวที่ 2 — สร้าง "หลัง" Service web/web-alt
# kubelet จึงใส่ env WEB_SERVICE_HOST / WEB_SERVICE_PORT ... ให้ (client ตัวแรกไม่มี)
apiVersion: v1
kind: Pod
metadata:
  name: client2                      # ต่างจาก client แค่ชื่อ (และเวลาที่สร้าง)
  namespace: shop
  labels:
    role: client
spec:
  terminationGracePeriodSeconds: 1
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "infinity"]
      resources:
        requests: { cpu: 10m, memory: 16Mi }
        limits:   { cpu: 100m, memory: 32Mi }
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `name: client2` | เหมือน `client-pod.yaml` ทุก field ยกเว้นชื่อ ตัวแปรที่ต่างจึงเหลือแค่ "เวลาที่สร้าง" | `client` ไม่มี `WEB_*` (`exit=1`) แต่ `client2` มี 27 ตัว |
| `labels.role: client` | ป้ายเดียวกับ `client` ไม่ใช่บูธ `web` | ไม่อยู่ใน EndpointSlice ของ `web` |
| `image: busybox:1.36`, `sleep infinity` | ใช้ยิง `wget`/`env` เหมือน `client` (และใช้ใน LAB 5 เป็นลูกค้า IP ที่สอง) | LAB 5 `client2` ติดบูธของตัวเองเมื่อเปิด `sessionAffinity` |
| (ไม่มี field env ในไฟล์เลย) | env `WEB_*` ไม่ได้มาจาก YAML แต่ kubelet ใส่ให้ตอนสร้าง container จาก Service ที่มีอยู่ **ณ ตอนนั้น** ใน namespace เดียวกัน | env ของ `client2` มีครบทั้ง `WEB_`, `WEB_ALT_`, `WEB_MULTI_` |

```bash
kubectl -n shop exec client -- env | grep WEB_; echo "exit=$?"
kubectl apply -f labs/lab04-dns/client2-pod.yaml
kubectl -n shop wait --for=condition=Ready pod/client2 --timeout=60s
kubectl -n shop exec client2 -- env | grep WEB_ | sort
```

```text
exit=1
pod/client2 created
pod/client2 condition met
WEB_ALT_PORT=tcp://10.96.142.94:8080
WEB_ALT_PORT_8080_TCP=tcp://10.96.142.94:8080
WEB_ALT_PORT_8080_TCP_ADDR=10.96.142.94
WEB_ALT_PORT_8080_TCP_PORT=8080
WEB_ALT_PORT_8080_TCP_PROTO=tcp
WEB_ALT_SERVICE_HOST=10.96.142.94
WEB_ALT_SERVICE_PORT=8080
WEB_MULTI_PORT=tcp://10.96.196.78:80
...
WEB_MULTI_SERVICE_HOST=10.96.196.78
WEB_MULTI_SERVICE_PORT=80
WEB_MULTI_SERVICE_PORT_ALT=8080
WEB_MULTI_SERVICE_PORT_HTTP=80
WEB_PORT=tcp://10.96.24.101:80
WEB_PORT_80_TCP=tcp://10.96.24.101:80
WEB_PORT_80_TCP_ADDR=10.96.24.101
WEB_PORT_80_TCP_PORT=80
WEB_PORT_80_TCP_PROTO=tcp
WEB_SERVICE_HOST=10.96.24.101
WEB_SERVICE_PORT=80
```

- `client` ไม่มี env `WEB_*` เลย (`grep` ไม่เจอจึง `exit=1`) เพราะ env ของ container ถูกตั้งครั้งเดียวตอนสร้าง
- `client2` ได้ env ของทุก Service ใน `shop` ชื่อ Service แปลงเป็นตัวพิมพ์ใหญ่และ `-` เป็น `_` (`web-alt` → `WEB_ALT_...`)
- มี `WEB_MULTI_SERVICE_PORT_HTTP`/`_ALT` เพราะพอร์ตของ `web-multi` มีชื่อ แต่ **ไม่มี `WEB_SERVICE_PORT_HTTP`** เพราะพอร์ตของ Service `web` ไม่ได้ตั้งชื่อ

Pod `web` เองก็เป็นแบบเดียวกัน ดูชื่อด้วย `kubectl -n shop get pods` แล้วแทนชื่อด้วย Pod ที่สร้าง **ก่อน** LAB 2 (ในการทดลองคือ `web-rppf4`) และ Pod ที่เกิด **หลัง** LAB 2 (ในการทดลองคือ `web-fbmpj` ที่เกิดตอน scale ใน LAB 2 ขั้นที่ 5)

```bash
kubectl -n shop exec web-rppf4 -- env | grep SERVICE_HOST
kubectl -n shop exec web-fbmpj -- env | grep WEB_SERVICE
```

```text
KUBERNETES_SERVICE_HOST=10.96.0.1
WEB_SERVICE_PORT=80
WEB_SERVICE_HOST=10.96.24.101
```

Pod เก่ามีแค่ `KUBERNETES_SERVICE_HOST` (Service `kubernetes` มีมาตั้งแต่สร้างคลัสเตอร์) ส่วน Pod ใหม่มี `WEB_SERVICE_HOST` ลำดับการสร้างมีผลแบบนี้ **แอปจึงควรหา Service ด้วย DNS**

### สิ่งที่เห็น

- ชื่อสั้น `web` ใช้ได้ในโซนเดียวกันเพราะ search domain ตัวแรกคือ `shop.svc.cluster.local`
- `nslookup` ของ busybox: ใช้ชื่อเต็ม ชื่อสั้นได้ผลแต่มีบรรทัด NXDOMAIN ปนและ exit 1 ส่วนชื่อที่มีจุด (`web.shop`) ได้ NXDOMAIN ทั้งที่ `wget` ใช้ได้
- env var ของ Service มีเฉพาะ Pod ที่สร้างหลัง Service

**คำถามชวนคิด**

1. ถ้าลบ Service `web` แล้วสร้างใหม่ (ได้ ClusterIP ใหม่) env `WEB_SERVICE_HOST` ใน `client2` จะเป็นค่าอะไร แอปที่ใช้ env จะเจออะไร
2. ชื่อ `example.com` ใน Pod ของ `shop` จะถูกลองถามกี่ชื่อก่อนถึงชื่อจริง (ใช้กฎ `ndots:5` และ search 3 ตัว)

---

## LAB 5: การกระจายโหลดและ sessionAffinity

<p align="center" id="fig-7">
  <img src="images/07-lab5-random-affinity.png" alt="รูปที่ 7 LAB 5 สุ่มและ sessionAffinity" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: client busybox เรียก http://web 30 ครั้ง แล้ว sort | uniq -c เห็นกระจายแบบสุ่ม; ตั้ง sessionAffinity: ClientIP แล้วไปบูธเดียวทั้ง 30</em>
</p>

**เป้าหมาย:** เห็นว่า kube-proxy เลือก Pod แบบสุ่มต่อ connection และเห็นผลของ `sessionAffinity: ClientIP`

**ต้องมีจาก LAB 4:** Service `web`, Pod `client` และ `client2`

### ขั้นที่ 1: ยิง 30 ครั้ง 2 รอบ

`wget` ของ busybox เปิด connection ใหม่ทุกครั้ง จึงเหมาะกับการดูการสุ่ม `sort | uniq -c` นับว่าแต่ละบรรทัดซ้ำกี่ครั้ง

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
```

```text
      3 web v1 from web-68gh2
     14 web v1 from web-fbmpj
     13 web v1 from web-rppf4

      9 web v1 from web-68gh2
      9 web v1 from web-fbmpj
     12 web v1 from web-rppf4
```

ทุก Pod ได้ลูกค้า แต่ **ไม่เท่ากันและแต่ละรอบต่างกัน** (รอบแรก `web-68gh2` ได้แค่ 3 ครั้ง) เพราะเป็นการสุ่มต่อ connection ไม่ใช่การวนตามลำดับ (round-robin) ตัวเลขในเครื่องนักศึกษาจะต่างจากนี้แน่นอน

### ขั้นที่ 2: เปิด sessionAffinity: ClientIP

หลัง `patch` ให้ **รอ 3 วินาที** ก่อนยิง เพราะ kube-proxy ต้องเขียนกฎ affinity ใหม่ก่อน

```bash
kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"ClientIP"}}'
sleep 3
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
kubectl -n shop exec client2 -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinityConfig}'; echo
```

```text
service/web patched
     30 web v1 from web-rppf4
     30 web v1 from web-rppf4
{"clientIP":{"timeoutSeconds":10800}}
```

`client` ไปบูธเดียวครบ 30/30 และ `client2` (คนละ IP) ก็ไปบูธเดียวของตัวเองครบ 30/30 (รอบนี้บังเอิญเป็นบูธเดียวกับ `client` คือ `web-rppf4` ในอีกรอบหนึ่ง `client2` ได้ `web-fbmpj` คนละบูธ) API เติม `timeoutSeconds: 10800` (3 ชั่วโมง) ให้เป็นค่าเริ่มต้น

> ⚠️ ในการทดลองที่ยิงทันทีหลัง `patch` (ไม่มี `sleep 3`) `client` ได้ `27 web-68gh2 / 2 web-fbmpj / 1 web-rppf4` ไม่ครบ 30/30 เพราะ request แรก ๆ ออกไปก่อนกฎ affinity จะพร้อม ถ้าเห็นผลกระจายแบบนี้ให้รอแล้วยิงใหม่

### ขั้นที่ 3: ปิด sessionAffinity

```bash
kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"None"}}'
kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinity} [{.spec.sessionAffinityConfig}]'; echo
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
```

```text
service/web patched
None []
     15 web v1 from web-68gh2
      7 web v1 from web-fbmpj
      8 web v1 from web-rppf4
```

กลับเป็น `None` แล้ว `sessionAffinityConfig` หายไปเอง (ในวงเล็บว่าง) และการกระจายกลับมา **ต้องปิดให้เรียบร้อย** เพราะ LAB ถัดไปใช้การกระจายแบบปกติ

### สิ่งที่เห็น

- kube-proxy สุ่ม Pod ต่อ connection ยิงน้อยครั้งอาจไม่เห็นครบทุก Pod ต้องยิงหลายสิบครั้ง
- `sessionAffinity: ClientIP` ผูกลูกค้าแต่ละ IP กับบูธเดียว (timeout เริ่มต้น 10800 วินาที)

**คำถามชวนคิด**

1. ถ้าทั้งคลาสใช้ Wi-Fi ที่ออกอินเทอร์เน็ตด้วย IP เดียวกัน แล้วร้านเปิด `sessionAffinity: ClientIP` จะเกิดอะไรกับการกระจายลูกค้า
2. ทำไมการยิงแค่ 3 ครั้งแล้วเห็น 3 Pod ไม่ครบจึงไม่ได้แปลว่า Service เสีย

---

## LAB 6: readinessProbe กับ endpoints

<p align="center" id="fig-8">
  <img src="images/08-lab6-not-ready.png" alt="รูปที่ 8 LAB 6 Pod ไม่ ready" width="900"><br>
  <em><b>รูปที่ 8</b> LAB6: ลบ index.html ใน Pod หนึ่ง → readiness ล้ม Pod 0/1 → EndpointSlice ยังแสดง IP แต่ ready=false และเรียก 30 ครั้งไม่ไปตัวนั้น; ใส่ไฟล์คืน → กลับมารับลูกค้า</em>
</p>

**เป้าหมาย:** ทำให้บูธหนึ่ง "ไฟแดง" แล้วเห็นว่ายังอยู่ในรายชื่อแต่ไม่ได้ลูกค้า จากนั้นคืนไฟเขียว

**ต้องมีจาก LAB 5:** Service `web` (sessionAffinity `None`), ReplicaSet `web` 3 บูธ และ Pod `client`

readinessProbe ของ `web` คือ `httpGet / port http` ทุก 2 วินาที ถ้าลบไฟล์ `index.html` nginx จะตอบ 403 และ probe ล้ม

### ขั้นที่ 1: ลบ index.html ของบูธหนึ่งแล้วจับเวลา

🐧 **ใน SSH session ของ k8s-lab** คำสั่งด้านล่างเลือก Pod `web` ตัวแรกใส่ตัวแปร `POD` ลบไฟล์ แล้ววนดูสถานะทุก 1 วินาทีจนกว่า endpoint ของบูธนั้นจะเป็น `ready=false` (คัดลอกทั้งบรรทัด)

```bash
POD=$(kubectl -n shop get pod -l app=web -o name | head -1); echo $POD; kubectl -n shop exec $POD -- rm /usr/share/nginx/html/index.html; date +%T; for i in $(seq 12); do kubectl -n shop get $POD --no-headers; S=$(kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath="{.items[0].endpoints[?(@.targetRef.name==\"${POD#pod/}\")].conditions.ready}"); echo "$(date +%T) ready=$S"; [ "$S" = false ] && break; sleep 1; done
```

```text
pod/web-68gh2
17:27:26
web-68gh2   1/1   Running   0     2m40s
17:27:26 ready=true
web-68gh2   1/1   Running   0     2m41s
17:27:27 ready=true
web-68gh2   1/1   Running   0     2m43s
17:27:29 ready=true
web-68gh2   1/1   Running   0     2m44s
17:27:30 ready=true
web-68gh2   1/1   Running   0     2m45s
17:27:31 ready=true
web-68gh2   0/1   Running   0     2m46s
17:27:32 ready=false
```

ราว **6 วินาที** หลังลบไฟล์ (17:27:26 → 17:27:32) Pod เปลี่ยนเป็น `0/1` และ endpoint เป็น `ready=false` (probe ทุก 2 วินาที ต้องล้มติดกัน 3 ครั้งตาม `failureThreshold` ค่าเริ่มต้น จึงใช้ราว 6–7 วินาทีแล้วแต่จังหวะ) Pod ยัง `Running` ไม่ถูก restart เพราะนี่คือ readiness ไม่ใช่ liveness เวลาที่ `date +%T` พิมพ์เป็นนาฬิกาของเครื่อง จะต่างจากนี้

### ขั้นที่ 2: รายชื่อยังมี IP แต่ไม่ได้ลูกค้า

```bash
kubectl -n shop get pods
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
```

```text
NAME        READY   STATUS    RESTARTS   AGE
client      1/1     Running   0          3m1s
client2     1/1     Running   0          60s
web-68gh2   0/1     Running   0          2m46s
web-fbmpj   1/1     Running   0          2m15s
web-rppf4   1/1     Running   0          3m1s

NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-fqgqh   IPv4          80      10.244.2.4,10.244.2.5,10.244.2.6   2m41s

10.244.2.4 web-rppf4 ready=true
10.244.2.5 web-68gh2 ready=false
10.244.2.6 web-fbmpj ready=true

     12 web v1 from web-fbmpj
     18 web v1 from web-rppf4
```

**กับดัก:** คอลัมน์ ENDPOINTS ยังแสดง 3 IP ครบ (รวม `10.244.2.5` ของบูธไฟแดง) ต้องดู `conditions.ready` จึงจะรู้ว่าตัวไหนไม่ได้ลูกค้า และยิง 30 ครั้งไม่ไป `web-68gh2` เลย

### ขั้นที่ 3: ดูสาเหตุจาก Pod และ EndpointSlice

แทน `web-68gh2` ด้วยชื่อในตัวแปร `POD` ของตัวเอง

```bash
kubectl -n shop describe pod web-68gh2 | grep -E "Readiness|Warning"
kubectl -n shop describe endpointslice -l kubernetes.io/service-name=web | sed -n "/Endpoints:/,\$p" | head -30
```

```text
    Readiness:  http-get http://:http/ delay=0s timeout=1s period=2s successThreshold=1 failureThreshold=3
  Warning  Unhealthy  2m46s            kubelet            spec.containers{nginx}: Readiness probe failed: Get "http://10.244.2.5:80/": dial tcp 10.244.2.5:80: connect: connection refused
  Warning  Unhealthy  2s (x4 over 6s)  kubelet            spec.containers{nginx}: Readiness probe failed: HTTP probe failed with statuscode: 403
Endpoints:
  - Addresses:  10.244.2.4
    Conditions:
      Ready:    true
    ...
  - Addresses:  10.244.2.5
    Conditions:
      Ready:    false
    Hostname:   <unset>
    TargetRef:  Pod/web-68gh2
    NodeName:   lab-worker2
    Zone:       <unset>
  ...
Events:         <none>
```

- Event `statuscode: 403` บอกสาเหตุตรง ๆ (nginx ไม่มีไฟล์หน้าแรกให้ตอบ) `(x4 over 6s)` คือ probe ล้มซ้ำ 4 ครั้งใน 6 วินาที
- Event `connection refused` เมื่อราว 3 นาทีก่อนเกิดตอน Pod เพิ่งเริ่มและ nginx ยังไม่เปิดพอร์ต เป็นเรื่องปกติ
- `describe endpointslice` แสดง `Conditions: Ready: false` ของบูธนั้นชัดเจน

### ขั้นที่ 4: คืนไฟเขียว

```bash
POD=pod/web-68gh2    # แทนด้วยชื่อของตัวเอง หรือใช้ตัวแปร POD จากขั้นที่ 1 ต่อได้เลย
kubectl -n shop exec $POD -- sh -c "echo \"web v1 from \$(hostname)\" > /usr/share/nginx/html/index.html"; date +%T; kubectl -n shop wait --for=condition=Ready $POD --timeout=30s; date +%T
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
kubectl -n shop exec client -- wget -qO- http://10.244.2.5
```

```text
17:27:33
pod/web-68gh2 condition met
17:27:33
10.244.2.4 web-rppf4 ready=true
10.244.2.5 web-68gh2 ready=true
10.244.2.6 web-fbmpj ready=true
web v1 from web-68gh2
```

ใส่ไฟล์คืนแล้วกลับมา Ready ภายในวินาทีเดียวกัน (probe รอบถัดไปผ่านครั้งเดียวก็พอ เพราะ `successThreshold=1`) และ `ready=true` อีกครั้งโดยไม่ต้องทำอะไรกับ Service

### สิ่งที่เห็น

- บูธที่ readiness ล้มยังอยู่ใน EndpointSlice แต่ `ready=false` จึงไม่ได้ลูกค้า (Pod ไม่ถูก restart)
- คอลัมน์ ENDPOINTS ไม่บอกเรื่อง ready ต้องดู jsonpath หรือ `describe endpointslice`
- เมื่อ probe ผ่าน บูธกลับมารับลูกค้าเอง

**คำถามชวนคิด**

1. ถ้าลบ `index.html` ของ **ทุก** บูธ ลูกค้าที่เรียก `http://web` จะเห็นข้อความอะไร (เทียบกับ LAB 7)
2. ถ้าเปลี่ยน probe นี้เป็น livenessProbe แทน ผลของการลบ `index.html` จะต่างไปอย่างไร

---

## LAB 7: debug Service

<p align="center" id="fig-9">
  <img src="images/09-lab7-debug.png" alt="รูปที่ 9 LAB 7 debug Service" width="900"><br>
  <em><b>รูปที่ 9</b> LAB7: Service web-typo (selector app=wbe) → ENDPOINTS &lt;unset&gt; + Connection refused; web-badport (targetPort 8080) → มี endpoint แต่ถูกปฏิเสธ; แก้แล้วกลับมาใช้ได้</em>
</p>

**เป้าหมาย:** ไล่ debug Service ที่ตั้งใจตั้งค่าผิด 3 แบบ: selector ผิด, targetPort ผิด และชื่อ DNS ผิด แล้วแก้ให้ใช้ได้

**ต้องมีจาก LAB 6:** ReplicaSet `web` 3 บูธที่ ready ทั้งหมด และ Pod `client`

### อธิบาย YAML: `labs/lab07-debug/`

โฟลเดอร์นี้มี Service ที่ตั้งใจตั้งค่าผิด 2 ไฟล์ `kubectl apply -f labs/lab07-debug/` สร้างทั้งคู่พร้อมกัน

**`web-typo-svc.yaml`** (ผิดที่ selector)

```yaml
# LAB 7 (ตั้งใจผิด #1): selector พิมพ์ผิด app=wbe → ไม่มี Pod ไหนตรง → ไม่มี endpoint
apiVersion: v1
kind: Service
metadata:
  name: web-typo
  namespace: shop
spec:
  selector:
    app: wbe               # ← พิมพ์ผิด (ที่ถูกคือ web)
  ports:
    - port: 80
      targetPort: http     # พอร์ตถูกต้อง ปัญหาอยู่ที่ selector อย่างเดียว
```

**`web-badport-svc.yaml`** (ผิดที่ targetPort)

```yaml
# LAB 7 (ตั้งใจผิด #2): selector ถูก แต่ targetPort 8080 — nginx ฟังที่ 80
apiVersion: v1
kind: Service
metadata:
  name: web-badport
  namespace: shop
spec:
  selector:
    app: web               # ถูกต้อง → มี endpoint ครบ 3 บูธ
  ports:
    - port: 80
      targetPort: 8080     # ← ผิด: ใน Pod ไม่มีอะไรฟัง 8080
```

| ไฟล์ / field | ค่าที่ตั้งใจผิด | ผลที่เห็นในการทดลอง | วิธีแก้ในขั้นตอน |
|---|---|---|---|
| `web-typo` `selector: app: wbe` | ไม่มี Pod ไหนมีป้าย `app=wbe` → EndpointSlice ว่าง | ENDPOINTS `<unset>`, `describe` → `Endpoints:` ว่าง, wget ได้ `Connection refused` ทันที | `patch` selector เป็น `app: web` (selector ของ Service แก้ได้ ต่างจาก ReplicaSet) |
| `web-typo` `targetPort: http` | ถูกต้อง ปัญหาอยู่ที่ selector อย่างเดียว | หลังแก้ selector ใช้ได้ทันที ไม่ต้องแก้พอร์ต | – |
| `web-badport` `selector: app: web` | ถูกต้อง | มี endpoint ครบ 3 บูธ | – |
| `web-badport` `targetPort: 8080` | nginx ใน Pod ฟังแค่ 80 → Pod ปฏิเสธ connection | PORTS `8080`, `Endpoints: ...:8080`, wget `Connection refused` ภายใน 0.16 วินาที | `patch` เป็น `targetPort: "http"` |
| ทั้งสองไฟล์ `port: 80` | พอร์ตฝั่ง Service ปกติ | ชื่อ DNS หาเจอ (ได้ ClusterIP) จึงไม่ใช่ `bad address` | – |

### ขั้นที่ 1: selector พิมพ์ผิด

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab07-debug/
sleep 2; kubectl -n shop exec client -- wget -qO- -T 3 http://web-typo; echo "exit=$?"
```

```text
service/web-badport created
service/web-typo created
wget: can't connect to remote host (10.96.145.14): Connection refused
command terminated with exit code 1
exit=1
```

DNS หาชื่อเจอ (ได้ ClusterIP `10.96.145.14`) แต่ถูกปฏิเสธ ไล่ตามบันไดในทฤษฎีหัวข้อ 13: ดู endpoint → ดู selector → เทียบ label

```bash
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-typo
kubectl -n shop describe svc web-typo | grep -E "Selector|Endpoints"
kubectl -n shop get pods --show-labels
```

```text
NAME             ADDRESSTYPE   PORTS     ENDPOINTS   AGE
web-typo-6w5rp   IPv4          <unset>   <unset>     3s

Selector:                 app=wbe
Endpoints:                

NAME        READY   STATUS    RESTARTS   AGE     LABELS
client      1/1     Running   0          3m6s    role=client
client2     1/1     Running   0          65s     role=client
web-68gh2   1/1     Running   0          2m51s   app=web
web-fbmpj   1/1     Running   0          2m20s   app=web
web-rppf4   1/1     Running   0          3m6s    app=web
```

EndpointSlice ว่าง (`<unset>`) เพราะไม่มี Pod ไหนมี label `app=wbe` เมื่อ Service ไม่มี endpoint kube-proxy ตอบปฏิเสธทันที (`Connection refused`) แก้ selector ได้เลย (selector ของ Service แก้ได้ ต่างจาก ReplicaSet)

```bash
kubectl -n shop patch svc web-typo -p '{"spec":{"selector":{"app":"web"}}}'
sleep 2; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-typo
kubectl -n shop exec client -- wget -qO- -T 3 http://web-typo
```

```text
service/web-typo patched
NAME             ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-typo-6w5rp   IPv4          80      10.244.2.6,10.244.2.4,10.244.2.5   5s
web v1 from web-68gh2
```

### ขั้นที่ 2: targetPort ผิด

```bash
time kubectl -n shop exec client -- wget -qO- -T 3 http://web-badport; echo "exit=$?"
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-badport
kubectl -n shop describe svc web-badport | grep -E "TargetPort|Endpoints"
```

```text
wget: can't connect to remote host (10.96.218.18): Connection refused
command terminated with exit code 1

real	0m0.157s
user	0m0.030s
sys	0m0.026s
exit=1
NAME                ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-badport-wpp2s   IPv4          8080    10.244.2.4,10.244.2.5,10.244.2.6   5s
TargetPort:               8080/TCP
Endpoints:                10.244.2.4:8080,10.244.2.5:8080,10.244.2.6:8080
```

ข้อความเหมือนขั้นที่ 1 (`Connection refused` ภายในราว 0.16 วินาที) แต่สาเหตุต่างกัน คราวนี้ **มี endpoint ครบ 3 ตัว** แต่ PORTS เป็น `8080` ซึ่งไม่มีโปรแกรมฟังใน Pod ตัว Pod จึงปฏิเสธ แก้ targetPort เป็นชื่อพอร์ต `http`

```bash
kubectl -n shop patch svc web-badport -p '{"spec":{"ports":[{"port":80,"targetPort":"http"}]}}'
sleep 2; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-badport
kubectl -n shop exec client -- wget -qO- -T 3 http://web-badport
```

```text
service/web-badport patched
NAME                ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-badport-wpp2s   IPv4          80      10.244.2.6,10.244.2.4,10.244.2.5   8s
web v1 from web-fbmpj
```

### ขั้นที่ 3: ชื่อ DNS ผิด

```bash
kubectl -n shop exec client -- wget -qO- -T 3 http://wbe; echo "exit=$?"
```

```text
wget: bad address 'wbe'
command terminated with exit code 1
exit=1
```

`bad address` แปลว่า DNS หาชื่อไม่เจอ ยังไม่ถึงขั้น Service เลย ตรวจการสะกดชื่อและ namespace (ในการทดลองคำสั่งนี้ใช้ราว 6 วินาทีกว่าจะขึ้น error เพราะต้องรอ DNS ตอบครบทุกชื่อที่เติม search domain ก่อน เวลาในเครื่องนักศึกษาอาจต่างจากนี้)

### ขั้นที่ 4: เก็บกวาด LAB 7

```bash
kubectl delete -f labs/lab07-debug/
```

```text
service "web-badport" deleted from shop namespace
service "web-typo" deleted from shop namespace
```

### สิ่งที่เห็น

| อาการ | สาเหตุ | หลักฐาน |
|---|---|---|
| `Connection refused` + ENDPOINTS `<unset>` | selector ไม่ตรง label ของ Pod | `describe svc` → `Selector: app=wbe`, `Endpoints:` ว่าง |
| `Connection refused` + มี endpoint ครบ | targetPort ไม่ตรงพอร์ตที่แอปฟัง | PORTS `8080`, `Endpoints: ...:8080` |
| `bad address` | ชื่อ DNS ผิด/ไม่มี | ยังไม่ถึง Service |

**คำถามชวนคิด**

1. ถ้า selector ถูกแต่ทุกบูธ readiness ล้ม (LAB 6 ทำกับทุกตัว) ลูกค้าจะเห็นข้อความเหมือนกรณีไหนในตาราง และจะแยกด้วยคำสั่งอะไร
2. ทำไม `web-badport` จึงได้ `Connection refused` ทันที แต่เรียก `web-alt` พอร์ต 80 ใน LAB 3 กลับ `timed out`

---

## LAB 8: NodePort 30080, LoadBalancer และ keep-alive

<p align="center" id="fig-10">
  <img src="images/10-lab8-nodeport-browser.png" alt="รูปที่ 10 LAB 8 NodePort จาก browser" width="900"><br>
  <em><b>รูปที่ 10</b> LAB8: Service web-nodeport (NodePort 30080) แล้วเปิด http://localhost:30080 บนเครื่องนักศึกษาได้ทันที ไม่ต้อง port-forward หรือ ssh -L</em>
</p>

**เป้าหมาย:** เปิดร้าน `web` จาก browser บนเครื่องนักศึกษาด้วย `http://localhost:30080` ดูว่าทุก Node ตอบ ลองกติกาของ NodePort และ LoadBalancer และเข้าใจว่าทำไม browser มักเห็น Pod เดิม

**ต้องมีจาก LAB 7:** ReplicaSet `web` 3 บูธใน `shop` และ NodePort 30080 ว่าง (LAB 0)

### ขั้นที่ 1: สร้าง NodePort 30080

#### อธิบาย YAML: `labs/lab08-nodeport/web-nodeport.yaml`

```yaml
# LAB 8: NodePort 30080 → เปิดประตูหมายเลข 30080 บน "ทุก Node"
# kind ของ k8s-lab map พอร์ต 30080 ของเครื่องนักศึกษา → lab-control-plane:30080 (extraPortMappings บท 001)
# → เปิด http://localhost:30080 จาก browser ได้เลย
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
  namespace: shop
spec:
  type: NodePort           # = ClusterIP + เปิดพอร์ตเดียวกันบนทุก Node
  selector:
    app: web
  ports:
    - port: 80             # ClusterIP:80 (ภายในคลัสเตอร์)
      targetPort: http     # → Pod:80
      nodePort: 30080      # ทุก Node:30080 (ช่วงที่ใช้ได้ 30000–32767)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `type: NodePort` | ได้ทุกอย่างของ ClusterIP **บวก** เปิดพอร์ตเดียวกันบนทุก Node | `TYPE NodePort` และยังได้ CLUSTER-IP `10.96.244.19` |
| `selector: app: web` | บูธชุดเดิม | curl วนเห็นทั้ง 3 บูธ |
| `port: 80` | พอร์ตบน ClusterIP สำหรับใช้ในคลัสเตอร์ | `PORT(S) 80:30080/TCP` (ตัวหน้า) |
| `targetPort: http` | ส่งต่อไปพอร์ต 80 ของ Pod | ได้ `web v1 from ...` |
| `nodePort: 30080` | เลือกเลขเองให้ตรงกับพอร์ตที่ k8s-lab map ออกเครื่องนักศึกษา (30080–30082) ถ้าไม่ใส่จะได้เลขสุ่มที่ map ไม่ถึง | `PORT(S) 80:30080/TCP` (ตัวหลัง), `localhost:30080` ใช้ได้ทั้งใน k8s-lab และ browser; เลขนี้จองได้ Service เดียว (ขั้นที่ 5) |

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab08-nodeport/web-nodeport.yaml
kubectl -n shop get svc web-nodeport
sleep 3; curl -s localhost:30080
```

```text
service/web-nodeport created
NAME           TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-nodeport   NodePort   10.96.244.19   <none>        80:30080/TCP   0s
web v1 from web-fbmpj
```

`PORT(S)` อ่านว่า "พอร์ต 80 ของ ClusterIP และพอร์ต 30080 ของทุก Node" ใน k8s-lab `localhost:30080` ไปถึง `lab-control-plane:30080` ผ่าน extraPortMappings (LAB 0 ขั้นที่ 6)

> ⚠️ **ต้องรอราว 3 วินาที:** ในการทดลองที่ใช้ `sleep 1` (2 ครั้งจาก 2) `curl -s localhost:30080` ไม่พิมพ์อะไรเลย (curl exit 56 = connection reset เพราะกฎ NodePort ยังไม่พร้อม) รออีก 2 วินาทีจึงได้ `web v1 from web-fbmpj` ที่แสดงด้านบน (บล็อกผลด้านบนจึงรวมจาก 2 รอบ: บรรทัด `get svc` จากรอบแรก บรรทัด `web v1` จากรอบที่รอครบ 3 วินาที) ถ้าไม่เห็นข้อความให้รอแล้ว curl ซ้ำ

### ขั้นที่ 2: ประตู 30080 เปิดบนทุก Node

```bash
for n in lab-control-plane lab-worker lab-worker2; do echo -n "$n: "; curl -s http://$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $n):30080; done
kubectl -n shop get pods -o wide
```

```text
lab-control-plane: web v1 from web-rppf4
lab-worker: web v1 from web-rppf4
lab-worker2: web v1 from web-fbmpj
NAME        READY   STATUS    RESTARTS   AGE     IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          4m6s    10.244.2.2   lab-worker2   <none>           <none>
client2     1/1     Running   0          2m5s    10.244.2.7   lab-worker2   <none>           <none>
web-68gh2   1/1     Running   0          3m51s   10.244.2.5   lab-worker2   <none>           <none>
web-fbmpj   1/1     Running   0          3m20s   10.244.2.6   lab-worker2   <none>           <none>
web-rppf4   1/1     Running   0          4m6s    10.244.2.4   lab-worker2   <none>           <none>
```

`docker inspect` อ่าน IP ของ container ที่เป็น Node แต่ละลำ ทั้ง 3 Node ตอบที่ 30080 ในการทดลองบูธ `web` ทั้ง 3 อยู่บน `lab-worker2` แต่ `lab-control-plane` และ `lab-worker` ที่ไม่มีบูธเลยก็ยังตอบได้ (kube-proxy บนเรือลำนั้นส่งต่อข้ามเรือให้) การกระจายบูธบน Node ในเครื่องนักศึกษาอาจต่างจากนี้ (ถ้ารันขั้นนี้เร็วเกินไปหลังสร้าง Service ทุก Node จะยังไม่ตอบ ให้รอแล้วลองใหม่)
### ขั้นที่ 3: เปิดจาก browser บนเครื่องนักศึกษา

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:30080** จะเห็นข้อความบรรทัดเดียว `web v1 from web-xxxxx` ไม่ต้องใช้ `kubectl port-forward` หรือ `ssh -L` เหมือนบทก่อน ๆ

<p align="center" id="fig-11">
  <img src="images/11-lab8-keepalive-lb.png" alt="รูปที่ 11 LAB 8 keep-alive และ LoadBalancer" width="900"><br>
  <em><b>รูปที่ 11</b> LAB8 (ต่อ): refresh browser มักเห็นชื่อ Pod เดิม (keep-alive) ส่วน curl วน 30 ครั้งเห็นหลาย Pod; ลอง nodePort 29999 (ผิดช่วง) และ LoadBalancer ที่ค้าง &lt;pending&gt; แล้วลบ NodePort ก่อน LAB สุดท้าย</em>
</p>

ลองกด refresh (F5) หลายครั้ง ส่วนใหญ่จะเห็น **ชื่อ Pod เดิมทุกครั้ง** ผลจริงเมื่อทดลองด้วย Chromium จากนอก container ผ่านเส้นทางเดียวกับ `localhost:30080` ของนักศึกษา (การทดลองรอบก่อน ชื่อ Pod จึงไม่ตรงกับรอบนี้)

| การทดลองใน browser | ผล |
|---|---|
| เปิดหน้า + reload 9 ครั้ง (รวม 10) | `web v1 from web-k2nk5` ทั้ง 10 ครั้ง |
| `fetch()` 10 ครั้งในหน้าเดิม | Pod เดียวทั้ง 10 ครั้ง |
| เปิด browser context ใหม่ทุกครั้ง (คล้ายหน้าต่าง Incognito ใหม่) 5 ครั้ง | 2 ชื่อ (3 + 2) |

รอบนี้จำลองพฤติกรรมเดียวกันด้วย `curl` **process เดียว** ที่ส่ง 10 request บน connection เดียว (แบบที่ browser ทำ) จากนอก container ได้ `10 web v1 from web-68gh2` คือ Pod เดียวทั้ง 10 ครั้ง

สาเหตุคือ **keep-alive**: browser เปิด connection เดียวแล้วใช้ส่งหลาย request ส่วน kube-proxy เลือก Pod **ตอนเปิด connection** เท่านั้น ถ้าอยากเห็นชื่อเปลี่ยน ให้ปิดหน้าต่างทั้งหมดแล้วรอสักครู่ หรือเปิดหน้าต่าง Incognito ใหม่ (ก็ยังสุ่มอยู่ดี) **การที่ refresh แล้วเห็นชื่อเดิมไม่ได้แปลว่ามี Pod เดียว**

### ขั้นที่ 4: ดูการกระจายด้วย curl วน

🐧 **ใน SSH session ของ k8s-lab** `curl` แยกคำสั่งเปิด connection ใหม่ทุกครั้ง

```bash
for i in $(seq 30); do curl -s localhost:30080; done | sort | uniq -c
```

```text
      9 web v1 from web-68gh2
      6 web v1 from web-fbmpj
     11 web v1 from web-rppf4
```

กระจายครบ 3 Pod (รวมได้ 26 ไม่ใช่ 30 เพราะในการทดลองรันขั้นนี้ทันทีหลังสร้าง Service ไม่กี่วินาที 4 ครั้งแรกจึงยังไม่ได้คำตอบ ถ้ารอแล้วตามขั้นที่ 1 จะได้ครบ 30)

🖥️ **บนเครื่องนักศึกษา (ทางเลือก)** ยิงจากเครื่องตัวเองผ่าน `localhost:30080` ได้เช่นกัน ผลจริงเมื่อยิง 30 ครั้งจากนอก container ผ่านพอร์ตที่ publish จาก k8s-lab

```bash
# macOS / Linux / Git Bash
for i in $(seq 30); do curl -s http://localhost:30080; done | sort | uniq -c
```

```powershell
# Windows PowerShell (ใช้ curl.exe ไม่ใช่ alias curl ของ PowerShell)
1..30 | ForEach-Object { curl.exe -s http://localhost:30080 } | Group-Object | Select-Object Count, Name
```

```text
     10 web v1 from web-68gh2
     11 web v1 from web-fbmpj
      9 web v1 from web-rppf4
```

(ผลข้างบนมาจากคำสั่ง bash ส่วน PowerShell แสดงเป็นตาราง `Count Name` แทน)

### ขั้นที่ 5: กติกาของ NodePort

#### อธิบาย YAML: `labs/lab08-nodeport/web-dup-nodeport.yaml` (ตั้งใจผิด)

```yaml
# LAB 8 (ตั้งใจผิด): ขอ nodePort 30080 ซ้ำ — 1 เลขใช้ได้ Service เดียวทั้งคลัสเตอร์
apiVersion: v1
kind: Service
metadata:
  name: web-dup            # ชื่อไม่ซ้ำ แต่เลข nodePort ซ้ำ
  namespace: shop
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: http
      nodePort: 30080      # ← ซ้ำกับ web-nodeport
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `name: web-dup` | ชื่อ Service ไม่ซ้ำ ให้เห็นว่าปัญหาไม่ได้อยู่ที่ชื่อ | – |
| `type: NodePort`, `nodePort: 30080` | ขอเลขเดียวกับ `web-nodeport` ที่ยังอยู่ เลข nodePort จองได้ Service เดียวทั้งคลัสเตอร์ | `provided port is already allocated` และ Service ไม่ถูกสร้าง |
| `selector`, `port`, `targetPort` | เหมือน `web-nodeport` ทุกอย่าง | – |

ส่วนคำสั่งแรกด้านล่างใช้ `kubectl create service` ขอเลขนอกช่วง (29999) โดยไม่ต้องมีไฟล์

```bash
kubectl -n shop create service nodeport bad --tcp=80:80 --node-port=29999; echo "exit=$?"
kubectl apply -f labs/lab08-nodeport/web-dup-nodeport.yaml; echo "exit=$?"
```

```text
error: failed to create NodePort service: Service "bad" is invalid: spec.ports[0].nodePort: Invalid value: 29999: provided port is not in the valid range. The range of valid ports is 30000-32767
exit=1
The Service "web-dup" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated
exit=1
```

- nodePort ต้องอยู่ใน **30000–32767**
- เลข **30080 ถูกจองแล้ว** โดย `web-nodeport` เลขเดียวใช้ได้ Service เดียวทั้งคลัสเตอร์ (แม้อยู่คนละ namespace ก็ไม่ได้)

### ขั้นที่ 6: LoadBalancer ใน kind

#### อธิบาย YAML: `labs/lab08-nodeport/web-lb.yaml`

```yaml
# LAB 8: LoadBalancer — บนคลาวด์จะได้ IP สาธารณะ ส่วน kind ไม่มีผู้จัดสรร → EXTERNAL-IP <pending>
# (แต่ยังได้ ClusterIP + nodePort แบบสุ่มให้)
apiVersion: v1
kind: Service
metadata:
  name: web-lb
  namespace: shop
spec:
  type: LoadBalancer       # = NodePort + ขอ IP ภายนอกจากผู้ให้บริการ (kind ไม่มี)
  selector:
    app: web
  ports:
    - port: 80
      targetPort: http     # ไม่ระบุ nodePort → ระบบสุ่มเลขในช่วง 30000–32767 ให้
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `type: LoadBalancer` | ขอ IP ภายนอกจากผู้ให้บริการ (บนคลาวด์จะได้ load balancer จริง) ซึ่ง kind ไม่มี | `EXTERNAL-IP <pending>` ค้างตลอด |
| ไม่ระบุ `nodePort` | LoadBalancer สร้างบน NodePort ระบบจึงสุ่มเลขในช่วง 30000–32767 ให้ | ได้ `80:30952/TCP` (สุ่ม เลขในเครื่องนักศึกษาจะต่าง) ซึ่งไม่ได้ map ออกเครื่องนักศึกษา |
| `selector`, `port: 80`, `targetPort: http` | เหมือน Service อื่นในบทนี้ | ยังได้ ClusterIP `10.96.82.207` ใช้ในคลัสเตอร์ได้ |

```bash
kubectl apply -f labs/lab08-nodeport/web-lb.yaml
sleep 5; kubectl -n shop get svc web-lb
kubectl delete -f labs/lab08-nodeport/web-lb.yaml
```

```text
service/web-lb created
NAME     TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-lb   LoadBalancer   10.96.82.207   <pending>     80:30952/TCP   5s
service "web-lb" deleted from shop namespace
```

kind ไม่มีผู้จัดสรร IP ภายนอก `EXTERNAL-IP` จึงค้าง `<pending>` แต่ยังได้ ClusterIP และ nodePort สุ่ม (`30952` ในการทดลอง) ซึ่ง **ไม่ได้ map ออกมาที่เครื่องนักศึกษา** (map แค่ 30080–30082)

### ขั้นที่ 7: ลบ NodePort ก่อน LAB สุดท้าย (ห้ามข้าม)

```bash
kubectl delete -f labs/lab08-nodeport/web-nodeport.yaml
kubectl get svc -A | grep 30080 || echo "(ว่าง — 30080 ว่างแล้ว)"
curl -sS -m 3 localhost:30080; echo "exit=$?"
sleep 3; curl -sS -m 3 localhost:30080; echo "exit=$?"
```

```text
service "web-nodeport" deleted from shop namespace
(ว่าง — 30080 ว่างแล้ว)
web v1 from web-rppf4
exit=0
curl: (56) Recv failure: Connection reset by peer
exit=56
```

`get svc` ยืนยันว่าเลข 30080 ว่างแล้ว แต่ **curl ครั้งแรกทันทีหลังลบยังได้หน้าเว็บอีก 1 ครั้ง** (`exit=0` เกิดทั้ง 2 รอบที่ทดลอง) เพราะ kube-proxy ยังลบกฎไม่เสร็จ รอ 3 วินาทีจึงได้ `curl: (56) Recv failure: Connection reset by peer` จากนอก container ก็เป็นแบบเดียวกัน คือได้หน้าเว็บอีก 1 ครั้งแล้วจึงได้ `curl: (7) Failed to connect ... Couldn't connect to server` 🌐 ลอง refresh browser ตอนนี้จะเปิดไม่ได้แล้ว

### สิ่งที่เห็น

- NodePort เปิดประตูเดียวกันบนทุก Node และ `http://localhost:30080` บนเครื่องนักศึกษาใช้ได้ทันที
- browser refresh มักเห็น Pod เดิม (keep-alive) ส่วน `curl` วนเห็นหลาย Pod
- nodePort ต้องอยู่ในช่วงและห้ามซ้ำ LoadBalancer ใน kind ค้าง `<pending>`
- ลบ `web-nodeport` แล้ว 30080 ว่างสำหรับ LAB 10

**คำถามชวนคิด**

1. ถ้าเปลี่ยน `web-nodeport` เป็น `nodePort: 31000` Service ยังใช้ได้ไหม แล้วจะเปิดจาก browser บนเครื่องนักศึกษาได้ไหม เพราะอะไร
2. ถ้าอยากให้ browser แสดงชื่อ Pod ต่างกันทุกครั้งที่ refresh ต้องเปลี่ยนที่ฝั่ง client หรือฝั่ง Service

---

## LAB 9: ข้าม namespace, headless, ExternalName และ NetworkPolicy

<p align="center" id="fig-12">
  <img src="images/12-lab9-cross-namespace.png" alt="รูปที่ 12 LAB 9 เรียกข้าม namespace" width="900"><br>
  <em><b>รูปที่ 12</b> LAB9: Pod cook ใน namespace kitchen เรียก web (bad address) แล้วเรียก web.shop และ web.shop.svc.cluster.local ได้; ดู search domain ใน resolv.conf</em>
</p>

**เป้าหมาย:** เรียก Service จาก namespace อื่น เทียบ DNS ของ Service ปกติ, headless และ ExternalName และเห็นว่า NetworkPolicy ต้องใช้พอร์ตของ Pod

**ต้องมีจาก LAB 8:** namespace `shop` ที่มี Service `web`, `web-alt`, `web-multi`, ReplicaSet `web` และ Pod `client`

### ขั้นที่ 1: ตรวจว่าไม่มี NetworkPolicy ค้าง แล้วสร้างโซนครัว

#### อธิบาย YAML: `labs/lab09-cross-ns/kitchen.yaml`

```yaml
# LAB 9: โซนครัว (namespace kitchen) + Pod cook ไว้เรียก Service ข้าม namespace
apiVersion: v1
kind: Namespace
metadata:
  name: kitchen            # search domain ของ Pod ในโซนนี้ขึ้นต้นด้วย kitchen.svc.cluster.local
  labels:
    team: kitchen          # NetworkPolicy ใน shop อ้างป้ายนี้
---
apiVersion: v1
kind: Pod
metadata:
  name: cook               # ลูกค้าจากโซนอื่น (busybox แบบเดียวกับ client)
  namespace: kitchen
spec:
  terminationGracePeriodSeconds: 1
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "infinity"]
      resources:
        requests: { cpu: 10m, memory: 16Mi }
        limits:   { cpu: 100m, memory: 32Mi }
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| เอกสารแรก `kind: Namespace`, `name: kitchen` | โซนที่สองของบทนี้ ไฟล์เดียวมี 2 object คั่นด้วย `---` (namespace มาก่อน Pod) | `namespace/kitchen created` แล้วจึง `pod/cook created` |
| `labels.team: kitchen` | ป้ายที่ NetworkPolicy ในขั้นที่ 4 ใช้ (`namespaceSelector`) | `cook` ผ่านรั้วได้เมื่อพอร์ตถูก ส่วน `client` (โซน `shop`) ไม่ผ่าน |
| เอกสารที่สอง `kind: Pod`, `name: cook`, `namespace: kitchen` | ลูกค้าจากโซนอื่น (busybox แบบเดียวกับ `client`) | `resolv.conf` ของ `cook` ขึ้นต้นด้วย `kitchen.svc.cluster.local` → ชื่อสั้น `web` ได้ `bad address` |
| `terminationGracePeriodSeconds: 1`, `sleep infinity`, `resources` | เหมือน `client-pod.yaml` | – |

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get networkpolicy -A
kubectl apply -f labs/lab09-cross-ns/kitchen.yaml
kubectl -n kitchen wait --for=condition=Ready pod/cook --timeout=60s
```

```text
No resources found
namespace/kitchen created
pod/cook created
pod/cook condition met
```

ถ้า `get networkpolicy -A` เจอ policy ค้างจากบทที่ 4 ให้ลบ namespace ของบทนั้นก่อน มิฉะนั้นผลจะเพี้ยน

### ขั้นที่ 2: เรียก Service ข้าม namespace

```bash
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web; echo "exit=$?"
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web.shop
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web.shop.svc.cluster.local
kubectl -n kitchen exec cook -- cat /etc/resolv.conf
```

```text
wget: bad address 'web'
command terminated with exit code 1
exit=1
web v1 from web-rppf4
web v1 from web-68gh2
search kitchen.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

search domain ตัวแรกของ `cook` คือ `kitchen.svc.cluster.local` ชื่อสั้น `web` จึงถูกหาใน `kitchen` (ไม่มี) ข้ามโซนต้องใช้ `web.shop` หรือชื่อเต็ม
### ขั้นที่ 3: headless เทียบกับ Service ปกติ และ ExternalName

<p align="center" id="fig-13">
  <img src="images/13-lab9-headless-externalname.png" alt="รูปที่ 13 LAB 9 headless และ ExternalName" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9 (ต่อ): nslookup web-headless.shop.svc.cluster.local คืน Pod IP ทุกตัว เทียบกับ web.shop.svc.cluster.local ที่คืน ClusterIP เดียว; nslookup supplier.shop.svc.cluster.local (ExternalName) คืน CNAME example.com (ต้องมีเน็ตออก) แต่ wget ได้ 409 Conflict เพราะ Host header ไม่ตรง</em>
</p>

#### อธิบาย YAML: `labs/lab09-cross-ns/web-headless.yaml` และ `supplier-externalname.yaml`

**`web-headless.yaml`**

```yaml
# LAB 9: headless Service (clusterIP: None) — ไม่มี IP กลาง
# DNS คืน IP ของทุก Pod ที่ Ready (สมุดรายชื่อบูธ) และ kube-proxy ไม่กระจายให้
apiVersion: v1
kind: Service
metadata:
  name: web-headless
  namespace: shop
spec:
  clusterIP: None          # headless: ไม่จอง ClusterIP (get svc แสดง CLUSTER-IP = None)
  selector:
    app: web               # ยังต้องมี selector เพื่อให้มี EndpointSlice/DNS ของ Pod
  ports:
    - port: 80
      targetPort: http
```

**`supplier-externalname.yaml`**

```yaml
# LAB 9: ExternalName — ชื่อในคลัสเตอร์ (supplier.shop) ที่ DNS ตอบเป็น CNAME ไปชื่อภายนอก
# ไม่มี selector / ClusterIP / kube-proxy
apiVersion: v1
kind: Service
metadata:
  name: supplier
  namespace: shop
spec:
  type: ExternalName
  externalName: example.com  # DNS ตอบ CNAME → example.com (Host header ของ client ยังเป็น supplier.shop)
```

| ไฟล์ / field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `web-headless` `clusterIP: None` | ไม่จอง IP กลาง → kube-proxy ไม่สร้างกฎ DNS ตอบเป็น IP ของ Pod แทน | `get svc` แสดง CLUSTER-IP `None`, nslookup ได้ 3 Address (`10.244.2.5`, `.6`, `.4`) |
| `web-headless` `selector: app: web` | ยังต้องมี selector เพื่อให้ระบบรู้ว่า Pod ไหนเป็นสมาชิก (เขียน EndpointSlice และ DNS ให้) | ได้ IP ของบูธที่ Ready ครบ 3 ตัว |
| `web-headless` `ports` | บอกพอร์ตไว้เป็นข้อมูล (ไม่มีการแปลงพอร์ต เพราะไม่มี kube-proxy) | PORT(S) `80/TCP` |
| `supplier` `type: ExternalName` | Service ที่เป็นแค่ชื่อ DNS ไม่มี selector / ClusterIP / endpoint | `get svc`: CLUSTER-IP `<none>`, PORT(S) `<none>` |
| `supplier` `externalName: example.com` | DNS ตอบ CNAME ชี้ไปชื่อภายนอก แต่ client ยังส่ง Host header เป็นชื่อเดิม | nslookup ได้ `canonical name = example.com`, wget ได้ `409 Conflict` |

```bash
kubectl apply -f labs/lab09-cross-ns/web-headless.yaml -f labs/lab09-cross-ns/supplier-externalname.yaml
kubectl -n kitchen exec cook -- nslookup web-headless.shop.svc.cluster.local
kubectl -n kitchen exec cook -- nslookup web.shop.svc.cluster.local
```

```text
service/web-headless created
service/supplier created
Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web-headless.shop.svc.cluster.local
Address: 10.244.2.5
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.2.6
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.2.4

Server:		10.96.0.10
Address:	10.96.0.10:53

Name:	web.shop.svc.cluster.local
Address: 10.96.24.101

```

headless (`clusterIP: None`) คืน **IP ของ Pod ทั้ง 3** (ลำดับสลับได้ทุกครั้ง) ส่วน Service ปกติคืน **ClusterIP เดียว** อย่าลืมใช้ชื่อเต็มกับ `nslookup` ของ busybox ผลจริงเมื่อใช้ชื่อย่อแบบมีจุด

```bash
kubectl -n kitchen exec cook -- nslookup web-headless.shop; echo "exit=$?"
```

```text
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find web-headless.shop: NXDOMAIN

** server can't find web-headless.shop: NXDOMAIN

command terminated with exit code 1
exit=1
```

ต่อด้วย ExternalName `supplier` (CNAME ไป `example.com`)

```bash
kubectl -n kitchen exec cook -- nslookup supplier.shop.svc.cluster.local
kubectl -n shop get svc
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://supplier.shop; echo "exit=$?"
```

```text
Server:		10.96.0.10
Address:	10.96.0.10:53

supplier.shop.svc.cluster.local	canonical name = example.com
Name:	example.com
Address: 2606:4700:10::6814:179a
Name:	example.com
Address: 2606:4700:10::ac42:93f3

supplier.shop.svc.cluster.local	canonical name = example.com
Name:	example.com
Address: 172.66.147.243
Name:	example.com
Address: 104.20.23.154

NAME           TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)           AGE
supplier       ExternalName   <none>         example.com   <none>            1s
web            ClusterIP      10.96.24.101   <none>        80/TCP            4m9s
web-alt        ClusterIP      10.96.142.94   <none>        8080/TCP          2m57s
web-headless   ClusterIP      None           <none>        80/TCP            1s
web-multi      ClusterIP      10.96.196.78   <none>        80/TCP,8080/TCP   2m52s
wget: server returned error: HTTP/1.1 409 Conflict
command terminated with exit code 1
exit=1
```

- `supplier` ได้ `canonical name = example.com` **2 ชุด** เพราะ busybox `nslookup` ถามทั้ง AAAA (IPv6 เช่น `2606:4700:10::6814:179a`) และ A (IPv4 เช่น `172.66.147.243`) แล้วพิมพ์ทั้งคู่ IP ในเครื่องนักศึกษาอาจต่าง (และลำดับชุดอาจสลับ) ถ้าไม่มีอินเทอร์เน็ตจะเห็นแค่บรรทัด canonical name
- `get svc`: ExternalName ไม่มี ClusterIP และ PORT(S) ส่วน headless มี CLUSTER-IP เป็น `None`
- `wget http://supplier.shop` ได้ `409 Conflict` เพราะ wget ส่ง Host header เป็น `supplier.shop` ซึ่งปลายทางไม่รู้จัก นี่คือข้อจำกัดของ ExternalName ที่เปลี่ยนแค่ DNS ไม่ได้เปลี่ยน Host header/TLS

### ขั้นที่ 4: NetworkPolicy กับพอร์ตของ Service

<p align="center" id="fig-14">
  <img src="images/14-lab9-networkpolicy-targetport.png" alt="รูปที่ 14 LAB 9 NetworkPolicy ใช้ targetPort" width="900"><br>
  <em><b>รูปที่ 14</b> LAB9 (ต่อ): NetworkPolicy ให้ kitchen เข้า web ได้ที่ port 8080 (port ของ Service web-alt) → ยัง timed out; แก้เป็น port 80 (targetPort ของ Pod) → เข้าได้ และ policy นี้ทำให้ Pod อื่นนอก kitchen (client ใน shop) เข้า web ไม่ได้ด้วย</em>
</p>

ก่อนมีรั้ว `cook` เรียก `web-alt.shop:8080` ได้ จากนั้นสร้าง policy ที่ "อนุญาต `kitchen` ที่พอร์ต 8080" (ไฟล์ `np-kitchen-8080.yaml` ตั้งใจผิด) แล้วแก้ด้วย `np-kitchen-80.yaml`

#### อธิบาย YAML: `labs/lab09-cross-ns/np-kitchen-8080.yaml` (ตั้งใจผิด) และ `np-kitchen-80.yaml` (ถูก)

**`np-kitchen-8080.yaml`**

```yaml
# LAB 9 (ตั้งใจผิด): อนุญาตครัวเข้า web "พอร์ต 8080" (= port ของ Service web-alt)
# NetworkPolicy ตรวจที่ Pod ปลายทาง "หลัง" kube-proxy แปลงที่อยู่แล้ว → เห็นพอร์ต 80 ของ Pod ไม่ใช่ 8080
# ผล: ครัวถูกกั้น (timed out)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-from-kitchen
  namespace: shop
spec:
  podSelector:
    matchLabels:
      app: web             # policy เลือก "Pod" ไม่ใช่ Service
  policyTypes: ["Ingress"] # คุมขาเข้า → Pod ที่ถูกเลือกรับเฉพาะที่ ingress อนุญาต
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              team: kitchen  # ต้นทาง = ทุก Pod ใน namespace ที่มีป้าย team=kitchen
      ports:
        - port: 8080       # ← ผิด: ต้องใช้พอร์ตของ Pod (targetPort)
```

**`np-kitchen-80.yaml`**

```yaml
# LAB 9 (ถูก): ใช้พอร์ตของ Pod (targetPort/containerPort 80) — เรียกผ่าน web-alt:8080 ก็ผ่าน
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-from-kitchen   # ชื่อเดียวกับไฟล์ 8080 (ลบตัวเก่าก่อน apply)
  namespace: shop
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              team: kitchen
      ports:
        - port: 80         # พอร์ตของ Pod (หรือใช้ชื่อ http ก็ได้)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `kind: NetworkPolicy`, `namespace: shop` | รั้วของโซน `shop` ต้องมี CNI ที่รองรับ NetworkPolicy (kind ของ k8s-lab บังคับใช้ได้ ผลกั้นจริงด้านล่าง) | ก่อนสร้าง `get networkpolicy -A` ได้ `No resources found` |
| `name: web-from-kitchen` (ทั้งสองไฟล์) | ชื่อเดียวกัน จึงต้อง `delete` ไฟล์ 8080 ก่อน `apply` ไฟล์ 80 | `deleted` แล้ว `created` |
| `podSelector: app: web` | policy เลือก **Pod** บูธ `web` ไม่ใช่ Service (Service `web` และ `web-alt` ส่งไป Pod ชุดนี้ทั้งคู่) | กั้นได้ทั้งทาง `web` และ `web-alt` |
| `policyTypes: ["Ingress"]` | คุมขาเข้า: ทันทีที่ Pod ถูกเลือก Pod นั้นรับเฉพาะต้นทางที่ ingress อนุญาต | ผลข้างเคียง: `client` ใน `shop` ถูกกั้นด้วย (`download timed out`) |
| `from.namespaceSelector: team: kitchen` | อนุญาตทุก Pod ในโซนที่มีป้าย `team=kitchen` (ป้ายใน `kitchen.yaml`) | `cook` ผ่านได้เมื่อพอร์ตถูก ส่วน `shop` (ป้าย `team: som`) ไม่ผ่าน |
| `ports.port: 8080` (ไฟล์ผิด) | เขียนตามพอร์ตของ **Service** `web-alt` แต่ policy ตรวจที่ Pod หลัง kube-proxy แปลงเป็น `Pod:80` แล้ว | `cook` → `web-alt.shop:8080` ได้ `download timed out` |
| `ports.port: 80` (ไฟล์ถูก) | ใช้พอร์ตของ **Pod** (targetPort/containerPort) | `cook` ผ่านทั้ง `web-alt.shop:8080` และ `web.shop` |

```bash
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web-alt.shop:8080
kubectl apply -f labs/lab09-cross-ns/np-kitchen-8080.yaml
sleep 2; kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web-alt.shop:8080; echo "exit=$?"
kubectl -n shop exec client -- wget -qO- -T 3 http://web; echo "exit=$?"
```

```text
web v1 from web-rppf4
networkpolicy.networking.k8s.io/web-from-kitchen created
wget: download timed out
command terminated with exit code 1
exit=1
wget: download timed out
command terminated with exit code 1
exit=1
```

- `cook` ถูกกั้น (`download timed out`) ทั้งที่ policy "อนุญาตพอร์ต 8080" เพราะ policy ตรวจที่ Pod **หลัง** kube-proxy แปลง `ClusterIP:8080` เป็น `Pod:80` แล้ว Pod เห็นพอร์ต 80 ซึ่งไม่ได้อนุญาต
- ผลข้างเคียง: `client` ใน `shop` เองก็ถูกกั้น เพราะทันทีที่มี policy เลือก Pod `app=web` Pod นั้นรับเฉพาะที่ policy อนุญาต (ต้นทางจาก `kitchen` เท่านั้น)

แก้เป็นพอร์ตของ Pod (ไฟล์ `np-kitchen-80.yaml` ค่าเหมือนเดิมทุกอย่างยกเว้น `port: 80` ต่างกันแค่ comment)

```bash
kubectl delete -f labs/lab09-cross-ns/np-kitchen-8080.yaml && kubectl apply -f labs/lab09-cross-ns/np-kitchen-80.yaml
sleep 2; kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web-alt.shop:8080
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web.shop
kubectl -n shop exec client -- wget -qO- -T 3 http://web; echo "exit=$?"
```

```text
networkpolicy.networking.k8s.io "web-from-kitchen" deleted from shop namespace
networkpolicy.networking.k8s.io/web-from-kitchen created
web v1 from web-rppf4
web v1 from web-rppf4
wget: download timed out
command terminated with exit code 1
exit=1
```

ตอนนี้ `cook` เข้าได้ทั้งทาง `web-alt:8080` และ `web:80` (ทั้งสอง Service ส่งไปพอร์ต 80 ของ Pod) ส่วน `client` ใน `shop` ยังถูกกั้นอยู่เพราะ policy นี้อนุญาตเฉพาะ `kitchen`

### ขั้นที่ 5: เก็บกวาด LAB 1–9

```bash
time kubectl delete ns shop kitchen
kubectl get ns
```

```text
namespace "shop" deleted
namespace "kitchen" deleted

real	0m10.767s
...
NAME                 STATUS   AGE
default              Active   6m59s
kube-node-lease      Active   6m59s
kube-public          Active   6m59s
kube-system          Active   6m59s
local-path-storage   Active   6m55s
```

ลบ namespace ใช้ราว 11 วินาที (รอ Pod ทุกตัวปิดตัว) แล้ว ReplicaSet, Pod, Service, EndpointSlice และ NetworkPolicy ทั้งหมดใน `shop`/`kitchen` หายไปด้วย

### สิ่งที่เห็น

- ข้ามโซนต้องใช้ `<svc>.<ns>` หรือชื่อเต็ม ชื่อสั้นได้ `bad address`
- headless คืน IP ของทุก Pod, Service ปกติคืน ClusterIP เดียว, ExternalName คืน CNAME พร้อม IPv6 (AAAA) และ IPv4 (A) ของปลายทาง (แต่ Host header ยังเป็นชื่อเดิม → `409 Conflict`)
- `nslookup` ของ busybox ต้องใช้ชื่อเต็ม (`web-headless.shop` ได้ NXDOMAIN)
- NetworkPolicy ต้องใช้พอร์ตของ Pod (targetPort) และเมื่อเลือก Pod แล้ว ทุกต้นทางที่ไม่ได้อนุญาตถูกกั้นหมด

**คำถามชวนคิด**

1. ถ้าต้องการให้ทั้ง `kitchen` และ Pod ใน `shop` เข้า `web` ได้ ต้องเพิ่มอะไรใน policy (ใบ้: ทฤษฎีบทที่ 4 หัวข้อ 10.3 เรื่อง OR)
2. ถ้าแอปในคลัสเตอร์ต้องเรียก API ภายนอกผ่าน HTTPS ด้วยชื่อ ExternalName ใบรับรอง TLS ของปลายทางจะตรวจผ่านไหม เพราะอะไร

---

## LAB 10: LAB สุดท้าย: แยก web กับ db ครั้งแรก

<p align="center" id="fig-15">
  <img src="images/15-lab10-architecture.png" alt="รูปที่ 15 LAB 10 สถาปัตยกรรม" width="900"><br>
  <em><b>รูปที่ 15</b> LAB10: สถาปัตยกรรม — ReplicaSet som-web 3 บูธ + Service NodePort 30080 สำหรับลูกค้าภายนอก และ ReplicaSet som-db 1 ตัว (emptyDir) + Service ClusterIP som-db ใน namespace som-shop</em>
</p>

**เป้าหมาย:** รวมทุกอย่างของบทนี้เปิด **ร้านอาหารแมวน้องส้ม** ที่แยกหน้าร้าน (web 3 บูธ) ออกจากครัวกลาง (db 1 ตัว) ด้วย **ReplicaSet 2 ตัว + Service 2 ตัว** เปิดร้านให้ลูกค้าที่ `http://localhost:30080` พิสูจน์ว่าออเดอร์จากทุกบูธรวมที่เดียว (แก้ปัญหาบทที่ 5) ดูว่า db ได้ IP ใหม่แต่ web ยังหาเจอด้วยชื่อ Service แล้วลองเปลี่ยนร้านเป็นรุ่น 1.3 ด้วยมือจนเห็นปัญหาที่บทที่ 7 จะแก้

**สิ่งที่ต้องมีก่อน:** ทำ LAB 0–9 แล้ว (เข้าใจ ClusterIP, EndpointSlice, NodePort, DNS และ readiness) **NodePort 30080 ต้องว่าง** (ลบ `web-nodeport` ใน LAB 8 แล้ว) และมี SSH session 2 หน้าต่าง (terminal 1, terminal 2) สำหรับข้อ 10.8 และ 10.12

### 10.1 สถาปัตยกรรมและไฟล์

บทที่ 2–5 ร้านน้องส้มใส่ web + db ไว้ใน Pod เดียว (db เป็น native sidecar คุยกันผ่าน `localhost`) พอบทที่ 5 scale เป็น 3 บูธ แต่ละบูธจึงมี db ของตัวเองและออเดอร์ไม่ตรงกัน LAB นี้แยกเป็น 2 ส่วนใน namespace `som-shop`

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080 → kube-proxy)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-xxxxx     Pod som-web-xxxxx     Pod som-web-xxxxx      (ReplicaSet som-web, replicas 3 → 5 → 3)
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop  (ชื่อ Service ไม่ใช่ IP) ────┘
                                   ▼
                    Service som-db (ClusterIP, 5432 → targetPort postgres)   ← ชื่อ/IP คงที่แม้ Pod db เกิดใหม่
                                   ▼
                    Pod som-db-xxxxx (ReplicaSet som-db, replicas 1, emptyDir — ข้อมูลหายเมื่อเกิดใหม่)
namespace som-shop (PSA warn: restricted)
```

| ไฟล์ | เนื้อหา |
|---|---|
| `som-shop-v2/k8s/00-namespace.yaml` | namespace `som-shop` label `pod-security.kubernetes.io/warn: restricted` (แบบบทที่ 4) |
| `som-shop-v2/k8s/10-db.yaml` | ReplicaSet `som-db` (`replicas: 1`, `postgres:17.11-alpine`, PGDATA บน `emptyDir`, readiness `pg_isready`) + Service `som-db` ชนิด ClusterIP `5432 → postgres` |
| `som-shop-v2/k8s/20-web.yaml` | ReplicaSet `som-web` (`replicas: 3`, `som-shop-web:1.2`, initContainers `wait-for-db` + `db-seed`, readiness `/api/health`, liveness `/api/live`) + Service `som-web` ชนิด NodePort `80 → http`, `nodePort: 30080` |
| `som-shop-v2/app/` | แอป Next.js (สำเนาจากบทที่ 5 แล้วปรับเป็นรุ่น 1.2/1.3) |
| `som-shop-v2/hit.sh` | ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน |

#### อธิบาย YAML: `som-shop-v2/k8s/00-namespace.yaml`

```yaml
# LAB 10: โซนของร้านน้องส้ม (web แยกจาก db) — เตือน (warn) ถ้า Pod ไม่ผ่าน Pod Security ระดับ restricted (แบบบท 004)
apiVersion: v1
kind: Namespace
metadata:
  name: som-shop                                # โซนของ LAB 10 (ลบทั้งร้านด้วย kubectl delete ns som-shop)
  labels:
    app.kubernetes.io/part-of: som-shop         # ป้ายบอกว่าเป็นส่วนหนึ่งของแอป som-shop
    pod-security.kubernetes.io/warn: restricted # warn = แค่เตือน ไม่ปฏิเสธ Pod (ผลจริง: ไม่มีคำเตือน เพราะตั้ง securityContext ครบ)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `name: som-shop` | โซนของ LAB 10 แยกจาก `shop` ของ LAB 1–9 เก็บกวาดทีเดียวด้วย `kubectl delete ns som-shop` | ลบ namespace ใช้ 11.1 วินาที (ข้อ 10.14) |
| `app.kubernetes.io/part-of: som-shop` | ป้ายมาตรฐานบอกว่าเป็นส่วนของแอป `som-shop` (ใช้ค้น/จัดกลุ่ม ไม่มีผลต่อการทำงาน) | – |
| `pod-security.kubernetes.io/warn: restricted` | ให้ API **เตือน** (ไม่ปฏิเสธ) เมื่อ Pod ไม่ผ่านระดับ restricted แบบบทที่ 4 | `apply` ไม่มีคำเตือนเลย เพราะทุก Pod ตั้ง `securityContext` ครบ |

#### อธิบาย YAML: `som-shop-v2/k8s/10-db.yaml` (ครัวกลาง)

```yaml
# LAB 10: ครัวกลาง (ฐานข้อมูล) — ReplicaSet som-db 1 ตัว + Service ClusterIP som-db:5432
# web ทุก Pod เรียก db ด้วยชื่อ "som-db" → Pod db เกิดใหม่ IP เปลี่ยน แต่ชื่อ/ClusterIP เดิม
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: som-db
  namespace: som-shop
  labels:
    app: som-db
spec:
  # replicas ต้องเป็น 1 — postgres 2 ตัว "ไม่แชร์ข้อมูลกัน" (Service จะสุ่มส่งไปคนละ db)
  replicas: 1
  selector:
    matchLabels:
      app: som-db                  # ReplicaSet นับ Pod ที่มีป้ายนี้
  template:
    metadata:
      labels:
        app: som-db                # Service som-db เลือก Pod ด้วยป้ายนี้
    spec:
      securityContext:               # ระดับ Pod: ผ่าน Pod Security restricted (บท 004)
        runAsNonRoot: true
        fsGroup: 70                  # emptyDir เป็นของกลุ่ม 70 = postgres เขียนได้
        seccompProfile:
          type: RuntimeDefault
      volumes:
        # !!! emptyDir = ข้อมูลอยู่กับ Pod นี้เท่านั้น → Pod db ถูกลบ/เกิดใหม่ = ข้อมูลหายหมด
        # (ตั้งใจให้เห็นใน LAB — บทหลังใช้ PersistentVolumeClaim)
        - name: db-data
          emptyDir: {}
      containers:
        - name: postgres
          image: postgres:17.11-alpine
          securityContext:
            runAsUser: 70            # uid ของ postgres ใน image alpine
            runAsGroup: 70
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
          env:
            - name: POSTGRES_USER    # postgres image สร้างผู้ใช้/ฐานข้อมูลนี้ตอนเริ่มครั้งแรก
              value: som
            - name: POSTGRES_PASSWORD
              value: meow1234        # เพื่อการเรียนเท่านั้น (ของจริงใช้ Secret — บทหลัง)
            - name: POSTGRES_DB
              value: catshop
            - name: PGDATA           # โฟลเดอร์ย่อยใน emptyDir (initdb ไม่ยอมใช้จุด mount ตรง ๆ)
              value: /var/lib/postgresql/data/pgdata
          ports:
            - name: postgres         # Service อ้าง targetPort: postgres
              containerPort: 5432
          volumeMounts:              # ต่อ emptyDir db-data เข้าที่เก็บข้อมูลของ postgres
            - name: db-data
              mountPath: /var/lib/postgresql/data
          readinessProbe:            # พร้อมรับงาน = pg_isready ผ่าน (ใช้ 127.0.0.1 ใน container เดียวกัน)
            exec:
              command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
            periodSeconds: 3
          livenessProbe:             # พอร์ต 5432 ยังเปิดอยู่ไหม (ไม่ผ่าน = kubelet restart container)
            tcpSocket:
              port: postgres
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:                 # postgres ใช้หน่วยความจำมากกว่า web จึงจองมากกว่า
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
---
# ประภาคารของครัว: ClusterIP เท่านั้น (ใช้ภายในคลัสเตอร์ — ไม่เปิด NodePort ให้ db)
apiVersion: v1
kind: Service
metadata:
  name: som-db
  namespace: som-shop
spec:
  type: ClusterIP
  selector:
    app: som-db
  ports:
    - port: 5432             # web เรียก som-db:5432
      targetPort: postgres   # → containerPort ชื่อ postgres (5432)
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `kind: ReplicaSet`, `replicas: 1` | db ต้องมีตัวเดียว postgres 2 ตัวไม่แชร์ข้อมูลกัน ถ้ามี 2 ตัว Service จะสุ่มส่งไปคนละ db | ลบ Pod db แล้ว ReplicaSet สร้างใหม่ให้ใน 4.1 วินาที (ข้อ 10.9) |
| `selector` / `template.labels` = `app: som-db` | ReplicaSet นับ Pod และ Service `som-db` เลือก Pod ด้วยป้ายนี้ | EndpointSlice ของ `som-db` มี IP ของ Pod db 1 ตัว |
| Pod `securityContext` (`runAsNonRoot`, `fsGroup: 70`, `seccompProfile`) | ผ่าน Pod Security restricted และให้ postgres (uid/gid 70) เขียน emptyDir ได้ | ไม่มีคำเตือน PSA, db Ready ใน 4.3 วินาที |
| `volumes: db-data emptyDir: {}` | ที่เก็บข้อมูลที่อยู่กับ Pod นี้เท่านั้น **ตั้งใจ** ให้เห็นว่าข้อมูลหายเมื่อ Pod เกิดใหม่ | หลังลบ Pod db: `relation "orders" does not exist`, หน้าเว็บ 503, ออเดอร์ 0 |
| `image: postgres:17.11-alpine` | image สาธารณะ แต่ LAB โหลดเข้า Node ไว้ก่อน (ข้อ 10.2) เพื่อให้เริ่มเร็ว | `kubectl get rs -o wide` แสดง IMAGES `postgres:17.11-alpine` |
| container `securityContext` (`runAsUser: 70`, `drop: ["ALL"]` ...) | รันเป็นผู้ใช้ postgres ไม่ใช่ root ตัดสิทธิ์พิเศษทั้งหมด | – |
| `env` `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` | image สร้างผู้ใช้ `som` รหัส `meow1234` และฐานข้อมูล `catshop` ตอนเริ่มครั้งแรก (รหัสเพื่อการเรียนเท่านั้น) | `psql -U som -d catshop` ใช้ได้ (ข้อ 10.7) |
| `env PGDATA` + `volumeMounts` | ให้ postgres เก็บข้อมูลในโฟลเดอร์ย่อยของ emptyDir | ข้อมูลอยู่ใน emptyDir จึงหายพร้อม Pod |
| `ports: name: postgres, containerPort: 5432` | ตั้งชื่อพอร์ตให้ Service อ้าง `targetPort: postgres` | EndpointSlice PORTS `5432` |
| `readinessProbe exec pg_isready ... -h 127.0.0.1`, `periodSeconds: 3` | db พร้อมรับงานจริงเมื่อ `pg_isready` ผ่าน ก่อนนั้น Service ยังไม่ส่งงานมา | `wait --for=condition=Ready` ผ่านใน 4.3 วินาที; initContainer `wait-for-db` ของ web รอจุดนี้ |
| `livenessProbe tcpSocket port postgres` | พอร์ต 5432 ยังเปิดอยู่ไหม (`initialDelaySeconds: 10` ให้เวลาเริ่มก่อน) | RESTARTS `0` ตลอด LAB |
| `resources` | postgres ใช้หน่วยความจำมากกว่า web จึงจอง 256Mi | – |
| Service `som-db` `type: ClusterIP` | ใช้ภายในคลัสเตอร์เท่านั้น ไม่เปิด NodePort ให้ db (ลูกค้าภายนอกไม่ควรต่อ db ตรง) | `som-db ClusterIP 10.96.93.117 5432/TCP` |
| Service `som-db` `port: 5432`, `targetPort: postgres` | web เรียก `som-db:5432` แล้วส่งต่อไปพอร์ตชื่อ `postgres` | ClusterIP **คงเดิม** แม้ IP ของ Pod db เปลี่ยน `10.244.2.9 → 10.244.2.14` |

#### อธิบาย YAML: `som-shop-v2/k8s/20-web.yaml` (หน้าร้าน)

```yaml
# LAB 10: หน้าร้าน — ReplicaSet som-web 3 บูธ + Service NodePort som-web (30080)
# ทุกบูธต่อ db กลางตัวเดียวผ่านชื่อ Service som-db → ออเดอร์จากทุกบูธรวมที่เดียว (แก้ปัญหาบท 005)
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: som-web
  namespace: som-shop
  labels:
    app: som-web
spec:
  replicas: 3                        # 3 บูธ (LAB 10.8 scale เป็น 5 แล้วคืนเป็น 3)
  selector:
    matchLabels:
      app: som-web
  template:
    metadata:
      labels:
        app: som-web               # Service som-web เลือก Pod ด้วยป้ายนี้
    spec:
      terminationGracePeriodSeconds: 30  # เวลาให้ Next.js ปิดตัวหลังได้ SIGTERM
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      initContainers:
        # 1) รอจน Service som-db มี db ที่พร้อม
        - name: wait-for-db
          image: postgres:17.11-alpine
          command:
            - sh
            - -c
            - until pg_isready -h som-db -p 5432 -U som -d catshop; do echo "รอฐานข้อมูล som-db..."; sleep 2; done; echo "ฐานข้อมูลพร้อมแล้ว"
          securityContext:
            runAsUser: 70
            runAsGroup: 70
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 100m, memory: 64Mi }
        # 2) เติมสินค้าเข้าชั้น (สร้างตาราง + สินค้าตั้งต้น) — ทุก Pod รัน แต่มี advisory lock กันชน
        - name: db-seed
          image: som-shop-web:1.2
          imagePullPolicy: IfNotPresent  # ใช้ image ที่ kind load ไว้บน Node (ไม่มีใน Docker Hub)
          command: ["node", "scripts/seed.mjs"]
          securityContext:
            runAsUser: 1000          # USER node ของ image เป็น "ชื่อ" → ใส่เลขให้ runAsNonRoot ตรวจได้
            runAsGroup: 1000
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
          env:
            - name: DATABASE_URL     # initContainer ก็ต่อ db ด้วยชื่อ Service som-db
              value: postgres://som:meow1234@som-db:5432/catshop
          resources:
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 300m, memory: 256Mi }
      containers:
        - name: web
          image: som-shop-web:1.2    # รุ่นและธีมฝังอยู่ใน image (APP_VERSION/APP_THEME)
          imagePullPolicy: IfNotPresent
          securityContext:
            runAsUser: 1000
            runAsGroup: 1000
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
          env:
            - name: POD_NAMESPACE    # Downward API (บท 003)
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: SHOP_NAME
              value: "ร้านอาหารแมวน้องส้ม"
            - name: SHOP_FOOTER
              value: "Next.js + PostgreSQL · Kubernetes LAB 006 · namespace $(POD_NAMESPACE)"
            - name: DATABASE_URL     # เรียก db ด้วยชื่อ Service (ไม่ใช่ IP ของ Pod db)
              value: postgres://som:meow1234@som-db:5432/catshop
            - name: PORT             # Next.js ฟังพอร์ต 3000 (= containerPort ชื่อ http)
              value: "3000"
            - name: HOSTNAME         # ฟังทุก interface ไม่ใช่แค่ localhost (ให้ probe/Service เข้าถึงได้)
              value: "0.0.0.0"
          ports:
            - name: http             # Service อ้าง targetPort: http
              containerPort: 3000
          readinessProbe:            # ต่อ db ได้ไหม (SELECT 1) → ไม่ผ่าน = Service ไม่ส่งลูกค้ามา
            httpGet:
              path: /api/health
              port: http
            periodSeconds: 3
            failureThreshold: 2
          livenessProbe:             # process ยังไม่ค้าง (ไม่แตะ db)
            httpGet:
              path: /api/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests: { cpu: 100m, memory: 192Mi }
            limits:   { cpu: 500m, memory: 512Mi }
---
# ประภาคารของหน้าร้าน: NodePort 30080 → เปิด http://localhost:30080 บนเครื่องนักศึกษา
apiVersion: v1
kind: Service
metadata:
  name: som-web
  namespace: som-shop
spec:
  type: NodePort
  selector:
    app: som-web
  ports:
    - port: 80               # ClusterIP:80 ภายในคลัสเตอร์
      targetPort: http       # = 3000 ของ container web
      nodePort: 30080        # ทุก Node:30080 → localhost:30080 บนเครื่องนักศึกษา
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลการทดลอง |
|---|---|---|
| `kind: ReplicaSet`, `replicas: 3` | หน้าร้าน 3 บูธ (ข้อ 10.8 scale เป็น 5 แล้วคืนเป็น 3) | `get rs`: `som-web 3 3 3` |
| `selector` / `template.labels` = `app: som-web` | ReplicaSet นับ Pod และ Service `som-web` เลือก Pod ด้วยป้ายนี้ | EndpointSlice `som-web-j4xfm` มี 3 → 5 → 3 IP |
| `terminationGracePeriodSeconds: 30` | ให้ Next.js ปิดตัวหลังได้ SIGTERM | ลบบูธระหว่างขาย บางรอบมี 1 request โดน `Connection reset by peer` (ข้อ 10.8) |
| Pod `securityContext` | ผ่าน Pod Security restricted | ไม่มีคำเตือน PSA |
| initContainer `wait-for-db` (image postgres, `until pg_isready -h som-db ...`) | รอจน Service `som-db` มี db ที่พร้อม ใช้ **ชื่อ Service** ไม่ใช่ IP | สถานะ `Init:0/2` ช่วงแรก |
| initContainer `db-seed` (`node scripts/seed.mjs`, image `som-shop-web:1.2`) | สร้างตาราง + สินค้าตั้งต้น ทุกบูธรัน แต่ใช้ advisory lock กันชน | `Init:1/2`, log `new: 6` / `new: 0` / `new: 0`, INIT_RESTARTS `0,0`; ข้อ 10.10 ใช้บูธใหม่เติมสินค้าให้ db ใหม่ |
| `imagePullPolicy: IfNotPresent` | ใช้ image ที่ `kind load` ไว้บน Node (ไม่มีใน Docker Hub) | ถ้าลืม `kind load` จะได้ `ErrImagePull` (Troubleshooting) |
| `runAsUser: 1000` | image ระบุ `USER node` เป็นชื่อ ต้องใส่เลขให้ `runAsNonRoot` ตรวจได้ | – |
| `env DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop` | ทั้ง `db-seed` และ `web` ต่อ db ด้วย **ชื่อ Service** `som-db` | `dns.lookup('som-db')` ได้ ClusterIP `10.96.93.117`; หลังลบ Pod db web ต่อใหม่เองโดยไม่ restart |
| `env POD_NAMESPACE` (Downward API), `SHOP_NAME`, `SHOP_FOOTER` | ข้อความบนหน้าเว็บ `$(POD_NAMESPACE)` ถูกแทนด้วยชื่อ namespace | ท้ายหน้าแสดง `... namespace som-shop` |
| `env PORT=3000`, `HOSTNAME=0.0.0.0` | Next.js ฟังพอร์ต 3000 ทุก interface ให้ probe และ Service เข้าถึงได้ | EndpointSlice PORTS `3000` |
| container `image: som-shop-web:1.2` | รุ่นและธีมฝังใน image (build-arg ข้อ 10.2) | หน้าแรก "เวอร์ชัน 1.2", `hit.sh` แสดงรุ่น `1.2`; ข้อ 10.11 `set image` เปลี่ยน template เป็น 1.3 |
| `ports: name: http, containerPort: 3000` | Service อ้าง `targetPort: http` | – |
| `readinessProbe /api/health` (`periodSeconds: 3`, `failureThreshold: 2`) | ตรวจแค่ "ต่อ db ได้" (`SELECT 1`) ไม่ตรวจตาราง | หลังลบ Pod db บูธยัง `1/1` และ `/api/health` → `{"ok":true,"db":"up"}` แต่หน้าแรก 503 |
| `livenessProbe /api/live` (`initialDelaySeconds: 10`) | process ยังไม่ค้าง ไม่แตะ db จึงไม่ restart บูธเพราะ db ล่ม | RESTARTS `0` แม้ db ถูกลบ |
| `resources` | จองให้ Next.js | – |
| Service `som-web` `type: NodePort` | เปิดร้านให้ลูกค้าภายนอก | `som-web NodePort 80:30080/TCP` |
| `port: 80`, `targetPort: http`, `nodePort: 30080` | ClusterIP:80 และทุก Node:30080 → Pod:3000 | `http://localhost:30080` เปิดร้านได้ทั้งใน k8s-lab และ browser |

**สิ่งที่เปลี่ยนในแอปรุ่น 1.2/1.3** (เทียบกับ `som-shop-web:1.1` ของบทที่ 4–5)

| ส่วน | รายละเอียด | ใช้ทำอะไรใน LAB |
|---|---|---|
| `Dockerfile` | `ARG APP_VERSION`, `ARG APP_THEME` → `ENV` แต่ละ tag "จำ" รุ่นและธีมของตัวเอง | build 1.2 (ธีม `harbor`) และ 1.3 (ธีม `sunset` + แบนเนอร์เมนูใหม่) จากโค้ดเดียว |
| หน้าแรก | ป้าย "เวอร์ชัน 1.2" และแถบ `🐱 เสิร์ฟโดย Pod: <ชื่อ Pod> · เวอร์ชัน <รุ่น>` | เห็นว่า browser ได้คำตอบจากบูธไหน |
| `GET /api/whoami` | ตอบ `<ชื่อ Pod> <รุ่น>` ไม่แตะ db | `hit.sh` นับการกระจายและรุ่น |
| `GET /api/stats` | ตอบ `<ชื่อ Pod> <รุ่น> orders=<n> products=<n>` ถ้า db ยังไม่มีตาราง ตอบ `db-not-ready` (HTTP 503) | เทียบว่าทุกบูธเห็นออเดอร์ชุดเดียวกัน |
| `GET /api/health` / `GET /api/live` | readiness (`SELECT 1` ไม่ตรวจตาราง) / liveness (ไม่แตะ db) | ทฤษฎีหัวข้อ 12.3 |
| `proxy.ts` | หน้า `/` ตรวจตาราง `products` ไม่มี → หน้า "ร้านกำลังเตรียมสินค้า" **HTTP 503** และ refresh เองทุก 5 วินาที | เห็นหลังลบ Pod db (ข้อ 10.9) |
| `scripts/seed.mjs` | `pg_advisory_xact_lock(5005)` + `CREATE TABLE IF NOT EXISTS` + `INSERT ... ON CONFLICT DO NOTHING` | 3 บูธเติมสินค้าพร้อมกันไม่ชนกัน (ข้อ 10.4) |
| `lib/db.ts` | `pool.on('error', ...)` สายเก่าขาดแล้วต่อใหม่เอง log บรรทัดเดียว | web ต่อ db ใหม่โดยไม่ต้อง restart (ข้อ 10.9) |

`hit.sh` (รันใน k8s-lab) ใช้งาน `./hit.sh [-q] [URL] [N] [DELAY]` ค่าเริ่มต้น URL `http://localhost:30080/api/whoami`, N=60, DELAY=0.1 วินาที ใช้ `curl -sS -f -m 2` แยกคำสั่งทุกครั้ง (connection ใหม่ทุกครั้ง HTTP 4xx/5xx นับเป็น err) แล้วพิมพ์ตาราง `จำนวน  Pod  เวอร์ชัน` และ `ok=… err=…` ส่วนโหมด `-q` พิมพ์ `.` (สำเร็จ) / `x` (ล้มเหลว) ระหว่างยิง แล้วสรุปข้อความ error และ "ช่วงที่มี err" ใช้ตอนลบ Pod

### 10.2 เตรียม image ให้ทุก Node

<p align="center" id="fig-16">
  <img src="images/16-lab10-build-images.png" alt="รูปที่ 16 LAB 10 build image 1.2 และ 1.3" width="900"><br>
  <em><b>รูปที่ 16</b> LAB10: build som-shop-web:1.2 และ 1.3 จากโค้ดเดียว (build-arg เวอร์ชัน/ธีม) แล้ว kind load ให้ทุก Node; postgres ใช้ kind load image-archive หรือให้ Node pull เอง</em>
</p>

🐧 **ใน SSH session ของ k8s-lab (terminal 1)** ตรวจว่า 30080 ว่าง แล้ว build รุ่น 1.2 และ 1.3 จากโค้ดเดียวกัน ต่างกันแค่ build-arg

```bash
cd /workspace/006_kubernetes_service/02_LAB
kubectl get svc -A | grep 30080 || echo '(ว่าง)'
cd som-shop-v2/app
time docker build -q --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 .
time docker build -q --build-arg APP_VERSION=1.3 --build-arg APP_THEME=sunset -t som-shop-web:1.3 .
```

```text
(ว่าง)
sha256:f6c9e393fe27394e67fa183dfe5b27db205816417b4dcfe85d7c143d92416720

real	0m33.743s
...
sha256:67f5f492bfa92eef2badb8bb8f96ed0ad1c196d717e57581a5e0c650fed713b3

real	0m1.484s
```

รุ่น 1.2 ใช้เวลาราว 34 วินาทีในการทดลอง (ดาวน์โหลด dependency และคอมไพล์) ส่วนรุ่น 1.3 ราว 1.5 วินาที เพราะทุกชั้นก่อน `ENV` ใช้ cache เดิม ต่างกันแค่ค่า `APP_VERSION`/`APP_THEME` ในชั้นท้าย (เครื่องนักศึกษาอาจใช้เวลานานกว่านี้หลายเท่า และ `sha256:...` จะเป็นค่าอื่น)

นำ image ทั้งสองเข้าทุก Node เตรียม postgres แล้ว **ให้สิทธิ์ execute กับ `hit.sh`** (ใช้ในข้อ 10.6 เป็นต้นไป)

```bash
time kind load docker-image som-shop-web:1.2 som-shop-web:1.3 --name lab
cd ..
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o ../pg.tar && kind load image-archive ../pg.tar --name lab && rm ../pg.tar)
chmod +x hit.sh
```

```text
Image: "som-shop-web:1.2" with ID "sha256:f6c9e393..." not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.2" with ID "sha256:f6c9e393..." not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.2" with ID "sha256:f6c9e393..." not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.3" with ID "sha256:67f5f492..." not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.3" with ID "sha256:67f5f492..." not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.3" with ID "sha256:67f5f492..." not yet present on node "lab-control-plane", loading...

real	0m6.512s
docker.io/library/postgres:17.11-alpine

real	0m16.602s
```

- image ที่ build เอง (`som-shop-web`) ไม่มีใน Docker Hub ต้อง `kind load docker-image` ให้ทุก Node และ YAML ใช้ `imagePullPolicy: IfNotPresent` (ลำดับ Node ในบรรทัด `loading...` สลับได้)
- postgres เป็น image หลาย platform ถ้า `kind load docker-image` ตรง ๆ อาจได้ `ctr: content digest sha256:...: not found` จึงใช้ `docker save --platform linux/amd64` + `kind load image-archive` (ถ้าข้ามขั้นนี้ Node จะดึงจาก Docker Hub เองได้แต่ช้ากว่า) ถ้าเคยโหลดไว้ในบทก่อนและคลัสเตอร์ยังเดิม ข้ามขั้นนี้ได้
- **`chmod +x hit.sh` จำเป็น:** ในการทดลองที่ไม่ได้สั่งบรรทัดนี้ ไฟล์เป็น `-rw-r--r--` และ `./hit.sh` ในข้อ 10.6 ได้ `./hit.sh: Permission denied` (exit 126) หลัง `chmod +x` จึงรันได้ (`chmod` ไม่พิมพ์อะไรเมื่อสำเร็จ ตรวจซ้ำได้ด้วย `ls -l hit.sh` ซึ่งต้องขึ้นต้นด้วย `-rwx`)
- ตอนนี้อยู่ที่โฟลเดอร์ `/workspace/006_kubernetes_service/02_LAB/som-shop-v2` คำสั่งที่เหลือของ LAB 10 รันจากที่นี่

### 10.3 เปิดครัวกลาง: db + Service som-db

<p align="center" id="fig-17">
  <img src="images/17-lab10-db-service.png" alt="รูปที่ 17 LAB 10 db และ Service som-db" width="900"><br>
  <em><b>รูปที่ 17</b> LAB10: db = ReplicaSet som-db replicas 1 ข้อมูลอยู่ใน emptyDir + Service ClusterIP som-db ให้ web เรียกด้วยชื่อ som-db:5432</em>
</p>

```bash
kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml
time kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=120s
kubectl -n som-shop get rs,pods,svc,endpointslice -o wide
```

```text
namespace/som-shop created
replicaset.apps/som-db created
service/som-db created
pod/som-db-kslt4 condition met

real	0m4.250s

NAME                     DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                  SELECTOR
replicaset.apps/som-db   1         1         1       4s    postgres     postgres:17.11-alpine   app=som-db

NAME               READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
pod/som-db-kslt4   1/1     Running   0          4s    10.244.2.9   lab-worker2   <none>           <none>

NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE   SELECTOR
service/som-db   ClusterIP   10.96.93.117   <none>        5432/TCP   4s    app=som-db

NAME                                          ADDRESSTYPE   PORTS   ENDPOINTS    AGE
endpointslice.discovery.k8s.io/som-db-b95qk   IPv4          5432    10.244.2.9   4s
```

**จดไว้ 2 ค่า** จะใช้เทียบในข้อ 10.9: ClusterIP ของ `som-db` (`10.96.93.117`) และ IP ของ Pod db (`10.244.2.9`) (ค่าในเครื่องนักศึกษาจะต่าง) ไม่มีคำเตือน Pod Security เพราะ Pod ตั้ง securityContext ครบตามระดับ restricted แล้ว (บทที่ 4)

### 10.4 เปิดหน้าร้าน 3 บูธ และเติมสินค้าแบบกันชน

<p align="center" id="fig-18">
  <img src="images/18-lab10-stock-shelves-once.png" alt="รูปที่ 18 LAB 10 เติมสินค้าแบบกันชน" width="900"><br>
  <em><b>รูปที่ 18</b> LAB10: web 3 replicas เริ่มพร้อมกัน initContainer เติมสินค้าเข้าฐานข้อมูลพร้อมกัน 3 ตัว — 1.2 ใช้ advisory lock ให้เข้าคิวทีละตัว และ ON CONFLICT DO NOTHING จึงไม่ซ้ำ</em>
</p>

```bash
kubectl apply -f k8s/20-web.yaml && timeout 12 kubectl -n som-shop get pods -l app=som-web -w; true
```

ผลจริง (ตัดบรรทัดซ้ำ)

```text
replicaset.apps/som-web created
service/som-web created
NAME            READY   STATUS     RESTARTS   AGE
som-web-fg4wd   0/1     Init:0/2   0          0s
som-web-l2zp4   0/1     Init:0/2   0          0s
som-web-tp95k   0/1     Init:0/2   0          0s
...
som-web-fg4wd   0/1     Init:1/2   0          2s
som-web-tp95k   0/1     Init:1/2   0          2s
som-web-l2zp4   0/1     Init:1/2   0          2s
...
som-web-fg4wd   0/1     PodInitializing   0          3s
...
som-web-fg4wd   0/1     Running           0          3s
...
som-web-fg4wd   1/1     Running           0          4s
som-web-tp95k   1/1     Running           0          4s
som-web-l2zp4   1/1     Running           0          4s
...
```

แต่ละบูธผ่าน `Init:0/2` (รอ db) → `Init:1/2` (เติมสินค้า) → `PodInitializing` → `Running 0/1` (รอ readiness) → `1/1` ในราว 4 วินาที (`timeout 12` หยุดการดูให้เองหลัง 12 วินาที บางครั้งจะเห็นบูธขึ้น `Pending` ชั่วครู่ก่อน `Init:0/2`) ดู log ของ initContainer `db-seed` ทั้ง 3 บูธ

```bash
kubectl -n som-shop logs -l app=som-web -c db-seed --prefix
kubectl -n som-shop get pods -o custom-columns=NAME:.metadata.name,INIT_RESTARTS:.status.initContainerStatuses[*].restartCount,NODE:.spec.nodeName
```

```text
[pod/som-web-tp95k/db-seed] connected to database
[pod/som-web-tp95k/db-seed] got seed lock 5005
[pod/som-web-tp95k/db-seed] tables ready: products, orders
[pod/som-web-tp95k/db-seed] seeded 6 products (new: 0)
[pod/som-web-fg4wd/db-seed] connected to database
[pod/som-web-fg4wd/db-seed] got seed lock 5005
[pod/som-web-fg4wd/db-seed] tables ready: products, orders
[pod/som-web-fg4wd/db-seed] seeded 6 products (new: 6)
[pod/som-web-l2zp4/db-seed] connected to database
[pod/som-web-l2zp4/db-seed] got seed lock 5005
[pod/som-web-l2zp4/db-seed] tables ready: products, orders
[pod/som-web-l2zp4/db-seed] seeded 6 products (new: 0)
NAME            INIT_RESTARTS   NODE
som-db-kslt4    <none>          lab-worker2
som-web-fg4wd   0,0             lab-worker
som-web-l2zp4   0,0             lab-worker2
som-web-tp95k   0,0             lab-worker2
```

- ทั้ง 3 บูธเริ่มเติมสินค้าพร้อมกันเข้า **db ตัวเดียวกัน** แต่ `pg_advisory_xact_lock(5005)` ทำให้เข้าคิวทีละบูธ บูธแรกที่ได้ lock (รอบนี้คือ `som-web-fg4wd`) เพิ่มสินค้า 6 รายการ (`new: 6`) บูธที่เหลือเห็นว่ามีแล้ว (`new: 0`) เพราะ `ON CONFLICT DO NOTHING` (`logs --prefix` เรียงตาม Pod ไม่ได้เรียงตามเวลา บูธที่ได้ `new: 6` จึงอยู่แถวไหนก็ได้)
- `INIT_RESTARTS 0,0` ทุกบูธ ในการตรวจก่อนเขียนบท แอปรุ่นเก่าที่ **ไม่มี lock** ทำให้ 2 ใน 3 บูธ init ล้ม 1 ครั้งด้วย `duplicate key value violates unique constraint "pg_type_typname_nsp_index"` เพราะ `CREATE TABLE IF NOT EXISTS` พร้อมกันชนกัน บทเรียน: **งานที่ replica หลายตัวทำซ้ำพร้อมกันต้องรันซ้ำได้ (idempotent) และกันชน** (งานแบบทำครั้งเดียวมีเครื่องมือเฉพาะในบทหลัง)
- จำนวนบูธต่อ Node (2+1) ขึ้นกับ scheduler ของเครื่องตัวเอง

### 10.5 web หา db ด้วยชื่อ Service

แทน `som-web-fg4wd` ด้วยชื่อบูธในเครื่องตัวเอง

```bash
kubectl -n som-shop exec som-web-fg4wd -c web -- node -e "require('dns').lookup('som-db',(e,a)=>console.log(a))"
kubectl -n som-shop get svc som-db
kubectl -n som-shop exec som-web-fg4wd -c web -- env | grep SOM_DB_SERVICE
kubectl -n som-shop get rs,svc
```

```text
10.96.93.117
NAME     TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
som-db   ClusterIP   10.96.93.117   <none>        5432/TCP   17s
SOM_DB_SERVICE_HOST=10.96.93.117
SOM_DB_SERVICE_PORT=5432
NAME                      DESIRED   CURRENT   READY   AGE
replicaset.apps/som-db    1         1         1       17s
replicaset.apps/som-web   3         3         3       13s

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/som-db    ClusterIP   10.96.93.117   <none>        5432/TCP       17s
service/som-web   NodePort    10.96.55.166   <none>        80:30080/TCP   13s
```

- ในบูธ web ชื่อ `som-db` แปลเป็น ClusterIP ของ Service `som-db` (search domain `som-shop.svc.cluster.local`) ไม่ใช่ IP ของ Pod db
- มี env `SOM_DB_SERVICE_HOST` เพราะบูธ web ถูกสร้างหลัง Service `som-db` (ถ้าสลับลำดับ apply จะไม่มี แต่ DNS ยังใช้ได้ แอปจึงใช้ชื่อใน `DATABASE_URL`) ลำดับบรรทัด env ไม่แน่นอน
- `som-web` เป็น NodePort `80:30080/TCP` พร้อมให้ลูกค้าเข้าแล้ว

### 10.6 เปิดร้านที่ http://localhost:30080

<p align="center" id="fig-19">
  <img src="images/19-lab10-open-shop-30080.png" alt="รูปที่ 19 LAB 10 เปิดร้านที่ 30080" width="900"><br>
  <em><b>รูปที่ 19</b> LAB10: เปิด http://localhost:30080 บนเครื่องนักศึกษา หน้าร้านแสดงป้ายเวอร์ชัน 1.2 และชื่อ Pod ที่เสิร์ฟ (ชื่อ Pod ของ ReplicaSet = som-web-&lt;สุ่ม 5 ตัว&gt;)</em>
</p>

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:30080** จะเห็นร้านธีม harbor (น้ำเงิน teal) ป้าย **"เวอร์ชัน 1.2"** แถบ **"🐱 เสิร์ฟโดย Pod: som-web-… · เวอร์ชัน 1.2"** ข้อความเล็ก `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service` และท้ายหน้า `Next.js + PostgreSQL · Kubernetes LAB 006 · namespace som-shop`

<p align="center" id="fig-20">
  <img src="images/screenshots/20261005_1736_lab006_02-shop-nodeport-1.2.png" alt="รูปที่ 20 ภาพหน้าจอจริง ร้านเวอร์ชัน 1.2 ออเดอร์ 4" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: หน้าร้านธีม harbor ป้าย "เวอร์ชัน 1.2" แถบ "🐱 เสิร์ฟโดย Pod: som-web-bhpqg · เวอร์ชัน 1.2" ออเดอร์ทั้งหมด 4 ชิ้นที่ขายแล้ว 8 สินค้าในร้าน 6 ซึ่งรวมจากทุกบูธใน db กลางตัวเดียว (หมายเหตุ: ภาพนี้ถ่ายจาก namespace som-shop-v12 ที่สร้างเพิ่มบน NodePort 30081 เพื่อถ่ายภาพ ท้ายหน้าจึงเป็น namespace som-shop-v12 บนเครื่องนักศึกษาให้เปิด http://localhost:30080 ตามขั้นตอนเดิม ท้ายหน้าจะเป็น namespace som-shop)</em>
</p>

กด refresh หลายครั้ง ส่วนใหญ่ชื่อ Pod **ไม่เปลี่ยน** (keep-alive แบบ LAB 8 ผลจริงของร้านนี้ใน Chromium จากการทดลองรอบก่อน: reload 9 ครั้งได้ Pod เดิมทั้ง 9) ดูการกระจายจริงด้วย `hit.sh`

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `som-shop-v2` และสั่ง `chmod +x hit.sh` ในข้อ 10.2 แล้ว)

```bash
./hit.sh
```

```text
จำนวน  Pod  เวอร์ชัน
     18 som-web-fg4wd 1.2
     16 som-web-l2zp4 1.2
     26 som-web-tp95k 1.2
ok=60 err=0 (ใช้เวลา 6.6 วินาที)
```

60 ครั้งไปครบทั้ง 3 บูธ ไม่มี error ถ้าได้ `./hit.sh: Permission denied` แปลว่ายังไม่ได้ `chmod +x hit.sh` (ข้อ 10.2) ให้สั่งแล้วรันใหม่

ตรวจหน้าแรกจาก k8s-lab ด้วย `curl` ได้เช่นกัน (ดึงเฉพาะป้ายรุ่นและแถบชื่อ Pod)

```bash
curl -s -o /dev/null -w "%{http_code} %{size_download} bytes\n" localhost:30080; curl -s localhost:30080 | grep -o "เวอร์ชัน 1\.[23]" | head -2; curl -s localhost:30080 | grep -o "เสิร์ฟโดย Pod[^<]*" | head -1
```

```text
200 17696 bytes
เวอร์ชัน 1.2
เวอร์ชัน 1.2
เสิร์ฟโดย Pod: som-web-fg4wd · เวอร์ชัน 1.2
```

### 10.7 ออเดอร์จากทุกบูธรวมที่เดียว

<p align="center" id="fig-21">
  <img src="images/20-lab10-hit-orders-shared.png" alt="รูปที่ 21 LAB 10 hit.sh และออเดอร์รวม" width="900"><br>
  <em><b>รูปที่ 21</b> LAB10: ./hit.sh 60 ครั้งเห็นทุก replica ตอบ และออเดอร์ที่สั่งผ่าน Pod ไหนก็เห็นตัวเลขเดียวกัน เพราะใช้ db กลางตัวเดียว (แก้ปัญหาบท 005)</em>
</p>

สั่งซื้อ 3 ออเดอร์ผ่าน NodePort (แต่ละคำสั่งอาจไปตกคนละบูธ) แล้วนับในฐานข้อมูลโดยตรง และถามทุกบูธด้วย `/api/stats`

```bash
for i in 1 2 3; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":2}'; echo; done
kubectl -n som-shop exec $(kubectl -n som-shop get pod -l app=som-db -o name) -- psql -U som -d catshop -c 'select count(*) from orders'
for i in $(seq 12); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":16}}
{"ok":true,"order_id":3,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":14}}
 count 
-------
     3
(1 row)

      3 som-web-fg4wd 1.2 orders=3 products=6
      2 som-web-l2zp4 1.2 orders=3 products=6
      7 som-web-tp95k 1.2 orders=3 products=6
```

ทุกบูธเห็น `orders=3` เท่ากัน และ `order_id` เรียง 1, 2, 3 ต่อกัน (stock ลดต่อเนื่อง 18 → 16 → 14) เพราะทุกบูธเขียนลง **db กลางตัวเดียว** ผ่านชื่อ `som-db` ต่างจากบทที่ 5 ที่บูธหนึ่งออเดอร์ 2 แต่อีกบูธ 0 (จำนวนครั้งที่แต่ละบูธตอบเป็นการสุ่ม)

🌐 กดปุ่ม 🛒 **สั่งซื้อ** ในหน้าร้านอีก 1 ครั้ง ผลจริงในการทดลองรอบก่อน: ข้อความ `สั่งซื้อแล้ว! ออเดอร์ #4` และตัวเลข "ออเดอร์ทั้งหมด" เปลี่ยนจาก 3 เป็น 4 (บูธที่เสิร์ฟคือ `som-web-zk8jj`) ไม่ว่าคำสั่งซื้อจะไปตกบูธไหน ตัวเลขก็ต่อกัน

> ไม่ควรใช้ `curl -s localhost:30080 | grep ...` แบบไม่มี `-o` เพื่อดูชื่อ Pod จากหน้าแรก เพราะหน้า Next.js มีข้อมูล RSC ฝังอยู่ ทำให้ได้ข้อความยาวหลายพันตัวอักษร ถ้าจะดูจากหน้าแรกให้ใช้ `grep -o` แบบข้อ 10.6 หรือใช้ `/api/whoami` / `/api/stats` แทน

### 10.8 scale 3 → 5 และ self-healing ใต้ Service

<p align="center" id="fig-22">
  <img src="images/21-lab10-scale-and-heal.png" alt="รูปที่ 22 LAB 10 scale และ self-healing" width="900"><br>
  <em><b>รูปที่ 22</b> LAB10: scale rs/som-web 3→5 EndpointSlice เพิ่มเป็น 5 IP เอง; ลบ Pod web หนึ่งตัวระหว่าง hit.sh → ReplicaSet สร้างแทน ร้านยังขาย</em>
</p>

```bash
kubectl -n som-shop scale rs/som-web --replicas=5
kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=90s
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
./hit.sh
```

```text
replicaset.apps/som-web scaled
pod/som-web-7rbjb condition met
pod/som-web-cwxqc condition met
pod/som-web-fg4wd condition met
pod/som-web-l2zp4 condition met
pod/som-web-tp95k condition met
NAME            ADDRESSTYPE   PORTS   ENDPOINTS                                        AGE
som-web-j4xfm   IPv4          3000    10.244.1.5,10.244.2.11,10.244.2.10 + 2 more...   33s
10.244.1.5 som-web-fg4wd ready=true
10.244.2.11 som-web-tp95k ready=true
10.244.2.10 som-web-l2zp4 ready=true
10.244.2.12 som-web-cwxqc ready=true
10.244.1.6 som-web-7rbjb ready=true
จำนวน  Pod  เวอร์ชัน
      9 som-web-7rbjb 1.2
     13 som-web-cwxqc 1.2
     13 som-web-fg4wd 1.2
     10 som-web-l2zp4 1.2
     15 som-web-tp95k 1.2
ok=60 err=0 (ใช้เวลา 6.6 วินาที)
```

บูธใหม่ 2 ตัว Ready ในราว 4 วินาที (`wait` ใช้ 4.3 วินาที) EndpointSlice มี 5 IP เอง (PORTS `3000` = พอร์ตของ container) และลูกค้ากระจายไปครบ 5 บูธโดยไม่ต้องแก้ Service

**self-healing ใต้ Service:** ใช้ 2 หน้าต่าง

🐧 **terminal 1** (`cd /workspace/006_kubernetes_service/02_LAB/som-shop-v2` ก่อน) ยิง 100 ครั้งแบบโหมดเงียบ

```bash
./hit.sh -q http://localhost:30080/api/whoami 100
```

🐧 **terminal 2** สั่งทันทีระหว่างที่ terminal 1 กำลังยิง (ลบบูธแรกในรายชื่อ)

```bash
kubectl -n som-shop delete $(kubectl -n som-shop get pod -l app=som-web -o name | head -1)
```

ผลจริง 3 รอบ (terminal 2 ลบ `som-web-7rbjb`, `som-web-cwxqc`, `som-web-fg4wd` ตามลำดับ แต่ละรอบแสดง `pod "som-web-..." deleted from som-shop namespace`)

```text
....................................................................................................
ok=100 err=0 (ใช้เวลา 11.0 วินาที)

....................................................................................................
ok=100 err=0 (ใช้เวลา 11.0 วินาที)

....................x...............................................................................
ข้อความ error:
      1 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 0.0 วินาที
ok=99 err=1 (ใช้เวลา 10.9 วินาที)
```

ReplicaSet สร้างบูธใหม่แทน EndpointSlice ถอดบูธเก่าออกและใส่บูธใหม่เมื่อ Ready ร้านขายต่อได้เกือบทุกครั้ง แต่บางรอบมี 1 request ที่โดน `Connection reset by peer` เพราะไปถึงบูธตอนกำลังปิดพอดี (ทฤษฎีหัวข้อ 12.2) รอบนี้ได้ err 0, 0, 1 (การทดสอบรอบก่อน 5 รอบได้ err 1, 0, 1, 0, 0) ถ้าดู `kubectl -n som-shop get pods -w` ระหว่างนั้นจะเห็นบูธที่ถูกลบขึ้นสถานะ `Error` ชั่วครู่ก่อนหาย (Next.js ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM) เป็นเรื่องปกติ

คืนเป็น 3 บูธ

```bash
kubectl -n som-shop scale rs/som-web --replicas=3
sleep 3; kubectl -n som-shop get pods
```

```text
replicaset.apps/som-web scaled
NAME            READY   STATUS    RESTARTS   AGE
som-db-kslt4    1/1     Running   0          81s
som-web-l2zp4   1/1     Running   0          77s
som-web-r6dmt   1/1     Running   0          24s
som-web-tp95k   1/1     Running   0          77s
```

### 10.9 ลบ Pod db: ชื่อเดิม IP ใหม่ แต่ข้อมูลหาย

<p align="center" id="fig-23">
  <img src="images/22-lab10-db-pod-lost-data.png" alt="รูปที่ 23 LAB 10 ลบ Pod db ข้อมูลหาย" width="900"><br>
  <em><b>รูปที่ 23</b> LAB10: ลบ Pod db → ReplicaSet สร้างใหม่ในราว 5 วินาทีได้ IP ใหม่ แต่ชื่อ som-db/ClusterIP เดิม web ต่อใหม่เองโดยไม่ต้อง restart; emptyDir ว่าง หน้าเว็บ 503 "ร้านกำลังเตรียมสินค้า" → ลบ Pod web 1 ตัวให้ initContainer เติมสินค้าใหม่ → ทุกบูธกลับมาขาย แต่ออเดอร์ = 0</em>
</p>

```bash
kubectl -n som-shop get pod -l app=som-db -o wide
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
S=$(date +%s.%N); kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=60s; E=$(date +%s.%N); awk -v a=$S -v b=$E "BEGIN{printf \"db ใหม่ Ready หลังสั่งลบ %.1f วินาที\n\", b-a}"
kubectl -n som-shop get pod -l app=som-db -o wide
kubectl -n som-shop get svc som-db
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
```
```text
NAME           READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
som-db-kslt4   1/1     Running   0          81s   10.244.2.9   lab-worker2   <none>           <none>
NAME           ADDRESSTYPE   PORTS   ENDPOINTS    AGE
som-db-b95qk   IPv4          5432    10.244.2.9   81s
pod "som-db-kslt4" deleted from som-shop namespace
pod/som-db-m52lz condition met
db ใหม่ Ready หลังสั่งลบ 4.1 วินาที
NAME           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-db-m52lz   1/1     Running   0          4s    10.244.2.14   lab-worker2   <none>           <none>
NAME     TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
som-db   ClusterIP   10.96.93.117   <none>        5432/TCP   85s
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-b95qk   IPv4          5432    10.244.2.14   85s
```

- ReplicaSet `som-db` สร้าง db ใหม่ Ready ในราว 4 วินาที ได้ **ชื่อใหม่และ IP ใหม่** (`10.244.2.9 → 10.244.2.14`)
- Service `som-db` ยังเป็น **ClusterIP เดิม** (`10.96.93.117`) EndpointSlice ชื่อเดิม (`som-db-b95qk`) แค่เปลี่ยน IP ข้างใน web ทุกบูธจึงไม่ต้องแก้อะไร

ตรวจหน้าร้านและฐานข้อมูล

```bash
curl -s -o /dev/null -w "%{http_code}\n" localhost:30080; curl -s localhost:30080/api/health; echo
for i in 1 2 3 4 5 6; do curl -s localhost:30080/api/stats; done | sort | uniq -c
kubectl -n som-shop exec $(kubectl -n som-shop get pod -l app=som-db -o name) -- psql -U som -d catshop -c 'select count(*) from orders'
kubectl -n som-shop get pods; kubectl -n som-shop logs -l app=som-web -c web --tail=2 --prefix
```

```text
503
{"ok":true,"db":"up"}
      2 som-web-l2zp4 1.2 db-not-ready
      1 som-web-r6dmt 1.2 db-not-ready
      3 som-web-tp95k 1.2 db-not-ready
ERROR:  relation "orders" does not exist
LINE 1: select count(*) from orders
                             ^
command terminated with exit code 1
NAME            READY   STATUS    RESTARTS   AGE
som-db-m52lz    1/1     Running   0          5s
som-web-l2zp4   1/1     Running   0          82s
som-web-r6dmt   1/1     Running   0          29s
som-web-tp95k   1/1     Running   0          82s
[pod/som-web-l2zp4/web] ✓ Running next.config took 0.7ms
[pod/som-web-l2zp4/web] db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)
[pod/som-web-r6dmt/web] ✓ Running next.config took 0.9ms
[pod/som-web-r6dmt/web] db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)
[pod/som-web-tp95k/web] ✓ Running next.config took 1.0ms
[pod/som-web-tp95k/web] db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)
```

- web **ต่อ db ใหม่ได้เองโดยไม่ restart** (`/api/health` → `{"ok":true,"db":"up"}`, RESTARTS 0, บูธยัง `1/1`) log บอกแค่ว่าสายเก่าขาดแล้วจะต่อใหม่เอง
- แต่ db ตัวใหม่ **ว่างเปล่า** เพราะข้อมูลเก่าอยู่ใน `emptyDir` ของ Pod db ที่ถูกลบ ตาราง `orders` จึงไม่มี (`relation "orders" does not exist`) ทุกบูธตอบ `/api/stats` ว่า `db-not-ready` และหน้าแรกตอบ **HTTP 503**

ดูข้อความบนหน้า 503 จาก k8s-lab ได้ด้วย

```bash
curl -s localhost:30080 | grep -o "ร้านกำลังเตรียมสินค้า[^<]*" | head -1
```

```text
ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱
```

🌐 refresh browser จะเห็นหน้า **"ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱"** (หน้านี้ลองใหม่เองทุก 5 วินาที)

<p align="center" id="fig-24">
  <img src="images/screenshots/20261005_1736_lab006_03-shop-503.png" alt="รูปที่ 24 ภาพหน้าจอจริง หน้า 503 ร้านกำลังเตรียมสินค้า หลังลบ Pod db" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: หลังลบ Pod db Service som-db ยังใช้ ClusterIP เดิม 10.96.232.78 แต่ endpoint เปลี่ยนจาก 10.244.1.15 เป็น 10.244.1.17 ฐานข้อมูลใหม่ยังว่าง หน้าเว็บจึงตอบ HTTP 503 "ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱" "ฐานข้อมูลยังไม่มีสินค้า (HTTP 503) · หน้านี้จะลองใหม่เองทุก 5 วินาที" (เสิร์ฟโดย Pod som-web-2q6hd เวอร์ชัน 1.2 ที่ยัง Ready อยู่) (หมายเหตุ: ถ่ายจาก namespace som-shop-503 ที่สร้างเพิ่มบน NodePort 30082 เพื่อถ่ายภาพ บนเครื่องนักศึกษาคือ http://localhost:30080)</em>
</p>

ภาพหน้าจอจริงด้านบนมาจากการทดลองอีกรอบหนึ่ง ซึ่งได้ผลแบบเดียวกัน (ผลคำสั่งของรอบนั้น)

```text
$ kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-vnbxx   IPv4          5432    10.244.2.33   7m52s
$ kubectl -n som-shop delete pod -l app=som-db
pod "som-db-zcwt6" deleted from som-shop namespace
$ kubectl -n som-shop get svc som-db
NAME     TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
som-db   ClusterIP   10.96.188.142   <none>        5432/TCP   7m56s
$ kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-vnbxx   IPv4          5432    10.244.2.38   7m56s
$ curl -s -o /dev/null -w %{http_code} localhost:30080
503
```

ทำไมบูธ web ยัง Ready ทั้งที่หน้าเว็บ 503: readinessProbe (`/api/health`) ตรวจแค่ "ต่อ db ได้" ไม่ตรวจตาราง ถ้าตรวจตารางด้วย ทุกบูธจะ not ready พร้อมกัน Service ไม่มีปลายทาง ลูกค้าจะได้ connection refused ทั้งร้านแทนหน้าแจ้งเตือนที่เป็นมิตร (ทฤษฎีหัวข้อ 12.3)

### 10.10 เติมสินค้าใหม่ด้วยการลบ Pod web 1 ตัว

initContainer `db-seed` รันเฉพาะตอนสร้าง Pod บทนี้ยังไม่มีคำสั่งสั่งให้บูธเริ่มใหม่ทั้งชุด วิธีที่ง่ายที่สุดคือลบบูธ web **ตัวเดียว** ให้ ReplicaSet สร้างใหม่ initContainer ของบูธใหม่จะสร้างตารางและสินค้าให้ db กลาง ซึ่งทุกบูธใช้ร่วมกัน

```bash
P=$(kubectl -n som-shop get pod -l app=som-web -o name | head -1); echo $P
S=$(date +%s.%N); kubectl -n som-shop delete $P; kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=60s; E=$(date +%s.%N); awk -v a=$S -v b=$E "BEGIN{printf \"Pod web ใหม่ Ready หลังสั่งลบ %.1f วินาที\n\", b-a}"
kubectl -n som-shop logs -l app=som-web -c db-seed --prefix | grep seeded
for i in $(seq 9); do curl -s localhost:30080/api/stats; done | sort | uniq -c; for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " localhost:30080; done; echo
```

ผลจริง (ในการทดลองบูธที่ถูกลบคือ `som-web-l2zp4`)

```text
pod/som-web-l2zp4
pod "som-web-l2zp4" deleted from som-shop namespace
pod/som-web-r6dmt condition met
pod/som-web-tp95k condition met
pod/som-web-tqzg5 condition met
Pod web ใหม่ Ready หลังสั่งลบ 3.6 วินาที
[pod/som-web-r6dmt/db-seed] seeded 6 products (new: 0)
[pod/som-web-tp95k/db-seed] seeded 6 products (new: 0)
[pod/som-web-tqzg5/db-seed] seeded 6 products (new: 6)
      5 som-web-r6dmt 1.2 orders=0 products=6
      4 som-web-tp95k 1.2 orders=0 products=6
200 200 200 200 200 200 
```

- บูธใหม่ `som-web-tqzg5` เติมสินค้า `new: 6` ลง db ใหม่ (log `new: 0` ของอีกสองบูธเป็นของตอนที่บูธนั้นเกิด ไม่ได้รันใหม่ ถ้าบูธที่เติมสินค้าคนแรกในข้อ 10.4 ยังอยู่ จะเห็น `new: 6` ของบูธนั้นด้วย)
- **ทุกบูธกลับมาขายทันที** (`200` ทุกครั้ง `products=6`) โดยไม่ต้องลบบูธอื่น เพราะใช้ db กลางตัวเดียว (9 ครั้งของ `/api/stats` รอบนี้ไม่ตกบูธใหม่เลย ไม่ใช่ความบังเอิญ แต่เพราะเรียกทันทีหลัง `wait` kube-proxy ยังไม่ได้เพิ่ม endpoint ของบูธใหม่ลงกฎ ตามกติกาเรื่องรอราว 2 วินาที ถ้ารอสักครู่แล้วเรียกซ้ำจะเห็นบูธใหม่ตอบด้วย)
- แต่ **`orders=0`** ออเดอร์เก่าหายถาวร

<p align="center" id="fig-25">
  <img src="images/screenshots/20261005_1737_lab006_04-shop-back-0-orders.png" alt="รูปที่ 25 ภาพหน้าจอจริง ร้านกลับมาแต่ออเดอร์ 0" width="700"><br>
  <em><b>รูปที่ 25</b> ภาพหน้าจอจริงจากการทดลอง: ลบ Pod web 1 ตัวให้ initContainer db-seed ของ Pod ใหม่เติมสินค้าใหม่ ร้านกลับมาขายได้ทุกบูธ (ภาพนี้เสิร์ฟโดยบูธเดิม som-web-fcvgx เวอร์ชัน 1.2) สินค้าในร้าน 6 แต่ออเดอร์ทั้งหมด 0 ชิ้นที่ขายแล้ว 0 และ "ยังไม่มีออเดอร์ ลองกดสั่งซื้อดูสิ" เพราะข้อมูลเดิมหายไปพร้อม emptyDir ของ Pod db ตัวเก่า (หมายเหตุ: ถ่ายจาก namespace som-shop-503 บน NodePort 30082 ที่สร้างเพิ่มเพื่อถ่ายภาพ บนเครื่องนักศึกษาคือ http://localhost:30080)</em>
</p>

**บทเรียน:** Service ทำให้ "ที่อยู่" ของ db คงที่ แต่ไม่ได้ทำให้ "ข้อมูล" คงอยู่ db ที่เก็บข้อมูลบน `emptyDir` เสียข้อมูลทุกครั้งที่ Pod db เกิดใหม่ (แก้ด้วย PersistentVolumeClaim ในบทหลัง) และ `replicas` ของ db ต้องเป็น 1 เพราะ postgres 2 ตัวไม่แชร์ข้อมูลกัน Service จะสุ่มส่งไปคนละ db

### 10.11 อยากเปลี่ยนเป็นรุ่น 1.3

<p align="center" id="fig-26">
  <img src="images/23-lab10-manual-update-pain.png" alt="รูปที่ 26 LAB 10 เปลี่ยนรุ่นด้วยมือจนสะดุด" width="900"><br>
  <em><b>รูปที่ 26</b> LAB10: set image rs/som-web เป็น 1.3 → Pod เดิมยังเป็น 1.2; ลบ Pod ทีละตัวเอง (1.2/1.3 ปนกัน err 0–1) หรือลบทีเดียวทั้งหมด → ร้านสะดุดราว 2–4 วินาที hit.sh นับ err 4–7 ครั้ง (Connection reset by peer / Operation timed out)</em>
</p>

น้องส้มอยากเปิดตัวเมนูใหม่ในรุ่น 1.3 (ธีม sunset + แบนเนอร์) image เตรียมไว้แล้วในข้อ 10.2 คำสั่ง `kubectl set image` เปลี่ยน image ใน template ของ ReplicaSet ได้ทั้ง container หลัก (`web`) และ initContainer (`db-seed`)

```bash
kubectl -n som-shop set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
kubectl -n som-shop get rs som-web -o jsonpath='{.spec.template.spec.containers[0].image} {.spec.template.spec.initContainers[1].image}'; echo
kubectl -n som-shop get rs som-web -o wide
kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
./hit.sh
```

```text
replicaset.apps/som-web image updated
som-shop-web:1.3 som-shop-web:1.3
NAME      DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES             SELECTOR
som-web   3         3         3       86s   web          som-shop-web:1.3   app=som-web
NAME            IMAGE
som-web-r6dmt   som-shop-web:1.2
som-web-tp95k   som-shop-web:1.2
som-web-tqzg5   som-shop-web:1.2
จำนวน  Pod  เวอร์ชัน
     17 som-web-r6dmt 1.2
     25 som-web-tp95k 1.2
     18 som-web-tqzg5 1.2
ok=60 err=0 (ใช้เวลา 6.6 วินาที)
```
template ของ ReplicaSet เป็น 1.3 แล้ว แต่ **บูธเดิมทั้ง 3 ยังเป็น 1.2** และลูกค้ายังเห็น 1.2 ทุกครั้ง (ทบทวนบทที่ 5: ReplicaSet ดูแลแค่จำนวน ไม่เปลี่ยน Pod ที่มีอยู่) น้องส้มต้องลบบูธเองเพื่อให้ ReplicaSet สร้างบูธใหม่จาก template ใหม่

### 10.12 ลบ Pod เองทีละตัว แล้วลบที่เหลือทีเดียว

**แบบที่ 1: ลบทีละตัว** ใช้ 2 หน้าต่าง

🐧 **terminal 1** ยิง 200 ครั้งแบบแสดงตาราง

```bash
./hit.sh http://localhost:30080/api/whoami 200
```

🐧 **terminal 2** ระหว่างที่ terminal 1 ยิงอยู่ ลบบูธ 1 ตัวแล้วรอจนทุกบูธ Ready

```bash
kubectl -n som-shop delete $(kubectl -n som-shop get pod -l app=som-web -o name | head -1) && kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=90s
```

ผลจริง (terminal 2 แล้วตามด้วย terminal 1)

```text
pod "som-web-r6dmt" deleted from som-shop namespace
pod/som-web-tp95k condition met
pod/som-web-tqzg5 condition met
pod/som-web-trnbl condition met

จำนวน  Pod  เวอร์ชัน
     10 som-web-r6dmt 1.2
     73 som-web-tp95k 1.2
     68 som-web-tqzg5 1.2
     49 som-web-trnbl 1.3
ok=200 err=0 (ใช้เวลา 21.9 วินาที)
```

ระหว่างนี้ **ลูกค้าเห็นร้านคนละรุ่นปนกัน** (บางคนเห็นธีม sunset 1.3 จาก `som-web-trnbl` บางคนเห็น harbor 1.2) รอบนี้ err 0 (การทดลองรอบก่อนมีรอบที่ได้ err 1) ถ้าจะทำต่ออีก 2 บูธต้องพิมพ์ชื่อและรอเองทีละตัว น่าเบื่อและเสี่ยงลบผิดตัว

```bash
kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
```

```text
NAME            IMAGE
som-web-tp95k   som-shop-web:1.2
som-web-tqzg5   som-shop-web:1.2
som-web-trnbl   som-shop-web:1.3
```

**แบบที่ 2: ทางลัดที่ผิด ลบทั้งหมดในคำสั่งเดียว**

🐧 **terminal 1**

```bash
./hit.sh -q http://localhost:30080/api/whoami 200
```

🐧 **terminal 2** ระหว่างที่ terminal 1 ยิงอยู่

```bash
kubectl -n som-shop delete pod -l app=som-web
kubectl -n som-shop get pods
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web
```

ผลจริง (terminal 2 แล้วตามด้วย terminal 1)

```text
pod "som-web-tp95k" deleted from som-shop namespace
pod "som-web-tqzg5" deleted from som-shop namespace
pod "som-web-trnbl" deleted from som-shop namespace
NAME            READY   STATUS     RESTARTS   AGE
som-db-m52lz    1/1     Running    0          41s
som-web-khfrr   0/1     Init:1/2   0          1s
som-web-p5z2k   0/1     Init:1/2   0          1s
som-web-wvlfd   0/1     Init:1/2   0          1s
NAME            ADDRESSTYPE   PORTS   ENDPOINTS                             AGE
som-web-j4xfm   IPv4          3000    10.244.2.16,10.244.1.11,10.244.1.10   118s

...................xxxxx................................................................................................................................................................................
ข้อความ error:
      2 curl: (28) Operation timed out
      3 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 4.4 วินาที
ok=195 err=5 (ใช้เวลา 25.9 วินาที)
```

ตรวจรุ่นหลังร้านกลับมา

```bash
kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=90s >/dev/null; kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image; ./hit.sh
curl -s localhost:30080 | grep -o "เวอร์ชัน 1\.[23]" | head -1; curl -s localhost:30080 | grep -o "เมนูใหม่[^<]*" | head -1
```

```text
NAME            IMAGE
som-web-khfrr   som-shop-web:1.3
som-web-p5z2k   som-shop-web:1.3
som-web-wvlfd   som-shop-web:1.3
จำนวน  Pod  เวอร์ชัน
     15 som-web-khfrr 1.3
     16 som-web-p5z2k 1.3
     29 som-web-wvlfd 1.3
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
เวอร์ชัน 1.3
เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟
```

- ลบทั้งหมดพร้อมกัน → บูธใหม่ทุกตัวยังอยู่ใน `Init` ไม่มีบูธที่ ready ให้ส่งลูกค้า (ENDPOINTS ที่เห็นเป็น IP ของบูธใหม่ที่ยัง `ready=false`) **ร้านสะดุด** แถว `x` ต่อกัน 5 ตัว ในช่วงราว 4.4 วินาที
- ข้อความ error คือ `Connection reset by peer` และ `Operation timed out` จำนวน err ต่างกันทุกรอบ: รอบนี้ 5 จาก 200, การทดลองรอบก่อนได้ 7 จาก 200 (ช่วง 2.6 วินาที), 4 และ 4 (ช่วง 2.3 และ 4.3 วินาที) และในรอบที่ถ่ายภาพหน้าจอ **ยิง 150 ครั้งได้ error 7 ครั้ง** (`during delete-all: ok=143 err=7`) โดยรวมอยู่ในช่วง 4–7 ครั้ง
- ตัวเลขนี้มาจากเครื่องทดสอบที่บูธใหม่ Ready ในราว 3–4 วินาที **เครื่องที่ช้ากว่าจะเห็น err มากกว่านี้** และถ้าร้านมี 30 บูธ ทั้งสองแบบยิ่งลำบาก

🌐 refresh browser จะเห็นร้านรุ่นใหม่

<p align="center" id="fig-27">
  <img src="images/screenshots/20261005_1736_lab006_01-shop-1.3.png" alt="รูปที่ 27 ภาพหน้าจอจริง ร้านเวอร์ชัน 1.3 ออเดอร์ 3" width="700"><br>
  <em><b>รูปที่ 27</b> ภาพหน้าจอจริงจากการทดลอง: เมื่อทุกบูธเป็น 1.3 แล้วจะได้ร้านธีม sunset ป้าย "เวอร์ชัน 1.3" แถบ "🐱 เสิร์ฟโดย Pod: som-web-pglfq · เวอร์ชัน 1.3" และแบนเนอร์ "🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟" ท้ายหน้า namespace som-shop — ออเดอร์ทั้งหมด 3 ชิ้นที่ขายแล้ว 3 สินค้าในร้าน 6 เก็บอยู่ใน db กลาง ซึ่งการลบ Pod web ไม่ได้แตะ (หมายเหตุ: ร้านในภาพสร้างใหม่ด้วย image 1.3 ใน namespace som-shop บน NodePort 30080 เพื่อถ่ายภาพ ไม่ได้ผ่านขั้น set image + ลบ Pod ในรอบถ่ายภาพ)</em>
</p>

### 10.13 สรุป LAB 10 และปัญหาที่ส่งต่อ

<p align="center" id="fig-28">
  <img src="images/24-lab10-wrap-up-bridge.png" alt="รูปที่ 28 สรุป LAB บทที่ 6" width="900"><br>
  <em><b>รูปที่ 28</b> สรุป LAB สุดท้าย: Service ให้ชื่อคงที่ (som-db, som-web) และ NodePort 30080 ใช้ db กลางตัวเดียว แต่เปลี่ยนรุ่นต้องลบ Pod เองจนร้านสะดุด → ต้องมีผู้จัดการร้านที่เปลี่ยนรุ่นทีละบูธ รอไฟเขียว และย้อนรุ่นได้ (บทที่ 7)</em>
</p>

**ตารางสรุป** สิ่งที่ Service แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| ที่อยู่คงที่ของร้านและของ db | `som-db` ClusterIP เดิมแม้ IP ของ Pod db เปลี่ยน, `som-web` NodePort 30080 | ✅ Service (บทนี้) |
| ออเดอร์ตรงกันทุกบูธ | `orders=3` ทุกบูธ, `order_id` ต่อกัน | ✅ แยก db + Service `som-db` (บทนี้) |
| กระจายลูกค้า + ส่งเฉพาะบูธที่พร้อม | `hit.sh` ครบทุกบูธ, scale 5 แล้ว EndpointSlice ตามเอง | ✅ Service + readinessProbe (บทนี้) |
| เปิดร้านจาก browser | `http://localhost:30080` ไม่ต้อง port-forward | ✅ NodePort (บทนี้) |
| เปลี่ยนรุ่นทีละบูธอัตโนมัติ รอไฟเขียวก่อนรื้อบูธถัดไป | ต้องลบ Pod เอง ลบทีเดียว err 4–7 ครั้ง, ลบทีละตัวต้องพิมพ์ชื่อและรอเอง | ❌ → **บทที่ 7 Deployment** |
| ประวัติรุ่นและย้อนรุ่น | ไม่มี ถ้า 1.3 พังต้อง `set image` กลับแล้วลบ Pod เองอีกรอบ | ❌ → **บทที่ 7 Deployment** |
| ข้อมูล db คงอยู่เมื่อ Pod db เกิดใหม่ | `relation "orders" does not exist`, ออเดอร์ 0 | ❌ → PersistentVolumeClaim (บทหลัง) |

### สิ่งที่เห็นใน LAB 10

- ReplicaSet 2 ตัว + Service 2 ตัวแยก web กับ db ได้ web เรียก db ด้วยชื่อ `som-db` (DNS → ClusterIP) ไม่ใช่ IP
- 3 บูธเติมสินค้าพร้อมกันโดยไม่ชนกันด้วย advisory lock (`new: 6/0/0`, init restart 0)
- เปิดร้านจาก browser ที่ `localhost:30080` ได้ทันที browser ติดบูธเดิม (keep-alive) ส่วน `hit.sh` เห็นครบทุกบูธ `ok=60 err=0`
- ออเดอร์จากทุกบูธรวมใน db กลาง scale 5 แล้ว EndpointSlice ตามเอง ลบบูธหนึ่งระหว่างขาย err 0–1
- ลบ Pod db: IP ใหม่ ClusterIP เดิม web ต่อใหม่เอง แต่ข้อมูลหาย หน้า 503 → ลบบูธ web 1 ตัวเพื่อเติมสินค้า ทุกบูธกลับมา ออเดอร์ 0
- `set image rs` ไม่เปลี่ยนบูธเดิม ลบทีละตัวเห็น 1.2/1.3 ปน ลบทีเดียวร้านสะดุด (รอบนี้ err 5 จาก 200 ในช่วง 4.4 วินาที รอบก่อน 7 จาก 200 และ 7 จาก 150)

### 10.14 เก็บกวาด LAB 10

🐧 **ใน SSH session ของ k8s-lab** (ปิด `hit.sh` ที่อาจยังรันอยู่ใน terminal อื่นด้วย Ctrl+C ก่อน)

```bash
time kubectl delete ns som-shop
kubectl get svc -A | grep 30080 || echo "(30080 ว่าง)"
docker exec lab-worker crictl images | grep som-shop
```

```text
namespace "som-shop" deleted

real	0m11.089s
...
(30080 ว่าง)
docker.io/library/som-shop-web                  1.2                  76eb03e99952e       76.6MB
docker.io/library/som-shop-web                  1.3                  332937a52995b       76.6MB
```

ลบ namespace ราว 11 วินาที พอร์ต 30080 ว่างอีกครั้ง image `som-shop-web:1.2` และ `1.3` ยังอยู่บน Node (IMAGE ID ที่ `crictl` แสดงเปลี่ยนทุกครั้งที่ build ใหม่ ในเครื่องนักศึกษาจะต่างจากนี้) **เก็บไว้ใช้ต่อในบทที่ 7** (ถ้า `k8s-down` ต้อง build และ `kind load` ใหม่)

### คำถามท้าย LAB 10

1. ทำไม `DATABASE_URL` จึงใช้ `som-db:5432` แทน IP ของ Pod db ถ้าใส่ IP ของ Pod db (ในการทดลองคือ `10.244.2.9`) ไว้ ข้อ 10.9 จะเกิดอะไรขึ้น
2. ทำไม Service `som-db` จึงเป็น ClusterIP ไม่ใช่ NodePort และทำไม ReplicaSet `som-db` ต้องมี `replicas: 1` ถ้าตั้งเป็น 3 ลูกค้าจะเห็นออเดอร์อย่างไร
3. ถ้าแอปรุ่น 1.2 ไม่มี advisory lock ใน `seed.mjs` แต่ยัง scale เป็น 3 บูธพร้อมกัน จะเห็นอะไรใน `INIT_RESTARTS` และ log ของ `db-seed` และควรแก้แบบไหนอีกบ้าง
4. หลังลบ Pod db ทำไมหน้าเว็บ 503 ทั้งที่บูธ web ยัง `1/1 Ready` และทำไมการลบบูธ web แค่ 1 ตัวจึงทำให้ **ทุก** บูธกลับมาขายได้
5. เทียบตัวเลข err ของ "ลบบูธ 1 ตัวระหว่างขาย" (ข้อ 10.8) กับ "ลบทั้งหมดในคำสั่งเดียว" (ข้อ 10.12) อธิบายว่าทำไมต่างกันมาก และเครื่องมือที่จะเปลี่ยนรุ่นแบบไม่สะดุดควรทำอะไรให้อัตโนมัติบ้าง

> **🏆 ท้าทาย:** เพิ่ม `sessionAffinity: ClientIP` ให้ Service `som-web` แล้วรัน `./hit.sh` ใหม่ ผลเปลี่ยนไปอย่างไร จากนั้นทำข้อ 10.12 แบบที่ 1 อีกครั้ง (ลบบูธที่ hit.sh ติดอยู่) บันทึกว่าลูกค้าเห็นอะไรระหว่างบูธนั้นถูกลบ และอธิบายว่าทำไม (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเอง)

> **ปูทางบทหน้า:** น้องส้มเปลี่ยนร้านเป็น 1.3 ได้ แต่ต้องรื้อบูธเองจนร้านสะดุด บทที่ 7 จะใช้ **Deployment** เป็น "ผู้จัดการร้าน" ที่สั่ง ReplicaSet รุ่นใหม่และรุ่นเก่า เปลี่ยนทีละบูธโดยรอไฟเขียว และย้อนรุ่นได้ โดยใช้ Service `som-db`/`som-web` และ image `som-shop-web:1.2`/`1.3` ของบทนี้ต่อได้ทันที

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v2/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 006_kubernetes_service k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/006_kubernetes_service/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (connection refused) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ ถ้าจะทำ LAB 10 ต้อง build/`kind load` image ใหม่ (ข้อ 10.2) |
| `Error from server (NotFound): namespaces "shop" not found` | ข้าม LAB 1 หรือเก็บกวาดไปแล้ว | เริ่มใหม่จาก LAB 1 (`kubectl apply -f labs/lab01-before-service/`) แล้วทำ LAB ที่ต้องมีก่อนตามบรรทัด "ต้องมีจาก LAB ..." |
| `provided port is already allocated` ตอน apply NodePort 30080 | Service อื่นจอง 30080 อยู่ (ตัวอย่างของบทที่ 1, `web-nodeport` ของ LAB 8 หรือ `som-web` ที่ยังไม่ลบ) | `kubectl get svc -A \| grep 30080` แล้วลบตัวที่ค้าง (LAB 0 ขั้นที่ 4, LAB 8 ขั้นที่ 7) |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080` ได้ | container `k8s-lab` ไม่ได้ publish พอร์ต 30080 (สร้างไม่ตรงบทที่ 1) หรือโปรแกรมอื่นบนเครื่องใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมีบรรทัดของ `30080/tcp` ถ้าไม่มี ใช้ทางสำรอง 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิด `http://localhost:30080` อีกครั้ง (ถ้าพอร์ตชน เปลี่ยนเลขซ้ายเป็น `-L 13080:localhost:30080` แล้วเปิด `http://localhost:13080`) |
| `curl -s localhost:30080` ไม่พิมพ์อะไรเลย (exit 56) หรือ loop ของ Node ไม่ได้คำตอบ ทันทีหลังสร้าง NodePort | กฎ NodePort ของ kube-proxy ยังไม่พร้อม | รอ 2–3 วินาที (LAB 8 ขั้นที่ 1 ใช้ `sleep 3`) แล้ว curl ซ้ำ |
| ลบ NodePort แล้ว `curl localhost:30080` ยังได้หน้าเว็บอีก 1 ครั้ง | kube-proxy ยังลบกฎไม่เสร็จ | ปกติ รอ 3 วินาทีแล้วจะได้ `(56) Connection reset by peer` / `(7) Couldn't connect` |
| เปิด `sessionAffinity: ClientIP` แล้วยิง 30 ครั้งยังกระจายหลายบูธ | ยิงทันทีหลัง `patch` กฎ affinity ยังไม่พร้อม | `sleep 3` หลัง `patch` แล้วยิงใหม่ (LAB 5 ขั้นที่ 2) |
| browser refresh แล้วเห็นชื่อ Pod เดิมตลอด | keep-alive ของ browser (ไม่ใช่ความผิดปกติ) | ดูการกระจายด้วย `curl` วน หรือ `./hit.sh` (LAB 8 ขั้นที่ 4) |
| `ping` ClusterIP ได้ 100% packet loss | ClusterIP เป็น IP เสมือน (ปกติ) | ทดสอบด้วย `wget`/`curl` ไปที่พอร์ตของ Service |
| `nslookup web` มีบรรทัด `** server can't find ... NXDOMAIN` ปน และ exit 1 / `nslookup web.shop` ได้ NXDOMAIN | ข้อจำกัดของ `nslookup` ใน busybox | ใช้ชื่อเต็ม `web.shop.svc.cluster.local` กับ nslookup ส่วนการทดสอบแอปใช้ `wget http://web.shop` |
| `wget: bad address 'web'` | เรียกชื่อสั้นจาก namespace อื่น หรือสะกดผิด | ใช้ `web.shop` หรือชื่อเต็ม ตรวจชื่อด้วย `kubectl get svc -A` |
| `wget: can't connect to remote host (10.96.x.x): Connection refused` | Service ไม่มี endpoint ที่ ready (selector ผิด/Pod ไม่ ready) หรือ targetPort ผิด หรือ Service เพิ่งสร้าง (kube-proxy ยังเขียนกฎไม่เสร็จ ราว 2 วินาทีแรก) | `sleep 2` แล้วลองซ้ำ ถ้ายังได้อีกให้ไล่ตาม LAB 7: `get endpointslice -l kubernetes.io/service-name=<svc>`, `describe svc`, `get pods --show-labels` |
| `wget: download timed out` | เรียกพอร์ตที่ Service ไม่ได้ประกาศ, NetworkPolicy กั้น หรือเรียก Pod IP ที่ไม่มีแล้ว | ตรวจ `PORT(S)` ของ Service, `kubectl get netpol -A`, ใช้ชื่อ Service แทน IP |
| ENDPOINTS แสดง IP ครบแต่บางบูธไม่ได้ลูกค้า | บูธนั้น `ready=false` | ดูด้วย jsonpath `conditions.ready` หรือ `describe endpointslice` (LAB 6) |
| ENDPOINTS แสดง `... + 2 more...` | kubectl ตัดการแสดงผลเกิน 3 IP | ใช้ jsonpath `{range .items[0].endpoints[*]}...` |
| `sessionAffinity` ยังเป็น `ClientIP` ทำให้ LAB 6 ยิงไปบูธเดียว | ลืมปิดในท้าย LAB 5 | `kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"None"}}'` |
| `client` ใน shop เรียก `web` ได้ `download timed out` หลัง LAB 9 ขั้นที่ 4 | NetworkPolicy เลือก Pod `app=web` แล้วอนุญาตเฉพาะ `kitchen` (ตั้งใจให้เห็น) | ลบ policy `kubectl -n shop delete netpol web-from-kitchen` หรือลบ namespace ตามขั้นที่ 5 |
| `wget http://supplier.shop` ได้ `409 Conflict` / nslookup ExternalName ไม่ได้ A record | Host header ไม่ตรง (ข้อจำกัดของ ExternalName) / เครื่องไม่มีอินเทอร์เน็ต | เป็นผลที่คาดไว้ ดูแค่บรรทัด `canonical name = example.com` |
| `./hit.sh: Permission denied` (exit 126) | ไฟล์ `hit.sh` ไม่มีสิทธิ์ execute (เช่น ข้าม `chmod` ในข้อ 10.2 หรือสิทธิ์หายระหว่างคัดลอกไฟล์) ถ้าเจอ `Permission denied` ให้ `chmod +x hit.sh` | `chmod +x hit.sh` (ข้อ 10.2) หรือรันด้วย `bash hit.sh` |
| `som-web` ค้าง `Init:0/2` นาน, log `wait-for-db` พิมพ์ `รอฐานข้อมูล som-db...` ซ้ำ ๆ | db ยังไม่ Ready หรือ Service `som-db` ไม่มี endpoint | `kubectl -n som-shop get pods,endpointslice` และ `kubectl -n som-shop logs -l app=som-web -c wait-for-db` ตรวจว่า apply `10-db.yaml` แล้ว |
| `som-web` ค้าง `ErrImagePull` / `ImagePullBackOff` (`som-shop-web:1.2`) | ยังไม่ `kind load docker-image` หรือสร้างคลัสเตอร์ใหม่หลัง load | ทำข้อ 10.2 แล้ว `kubectl -n som-shop delete pod -l app=som-web` |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` (ข้อ 10.2) |
| หน้าเว็บ 503 "ร้านกำลังเตรียมสินค้า" ค้าง | db เกิดใหม่และยังว่าง (ตั้งใจให้เห็นในข้อ 10.9) | ลบบูธ web 1 ตัวตามข้อ 10.10 |
| log ของ web มี `db connection lost: terminating connection due to administrator command` | สายเก่าไป db ตัวที่ถูกลบขาด | ปกติ pool ต่อใหม่เองใน request ถัดไป |
| Event `Readiness probe failed: ... connect: connection refused` ตอน Pod เพิ่งเริ่ม / บูธที่ถูกลบขึ้น `Error` ชั่วครู่ | แอปยังไม่เปิดพอร์ต / Next.js ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM | ปกติ ไม่ต้องแก้ |
| err ของ `hit.sh` ตอนลบบูธมากกว่าในเอกสาร | เครื่องช้ากว่า บูธใหม่ Ready ช้ากว่า | ปกติ บันทึกตัวเลขของตัวเองไว้เทียบกับบทที่ 7 |
| `hit.sh` หรือ `kubectl ... -w` ค้างอยู่ในอีกหน้าต่าง | ยังไม่ได้หยุด | กด Ctrl+C ในหน้าต่างนั้น ถ้าหาไม่เจอใช้ `pkill -f "[h]it.sh"` |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get svc -A` (มี `kubernetes`, `kube-dns`), `mode: iptables` และผล `grep -E '3008[0-2]'` ที่ว่าง
- [ ] **LAB 1** `wget` ด้วย Pod IP ได้ก่อนลบ และ `download timed out` หลังลบ พร้อม `get pods -o wide` ที่เห็นชื่อ/IP ใหม่
- [ ] **LAB 2** `get svc,endpointslice` ที่ ENDPOINTS ตรงกับ Pod IP, คำเตือน `v1 Endpoints is deprecated` และ ping ClusterIP 100% packet loss คู่กับ `wget http://web` ที่ได้
- [ ] **LAB 3** `web-alt:8080` ได้ / `web-alt` timed out และ error `spec.ports[1].name: Required value`
- [ ] **LAB 4** `resolv.conf`, `nslookup web.shop.svc.cluster.local` และ env `WEB_*` ของ `client` (ว่าง) เทียบ `client2`
- [ ] **LAB 5** ผลยิง 30 ครั้งแบบ `None` และแบบ `ClientIP` (30/30)
- [ ] **LAB 6** jsonpath ที่มี `ready=false` คู่กับผลยิง 30 ครั้งที่ไม่ไปบูธนั้น
- [ ] **LAB 7** ENDPOINTS `<unset>` ของ `web-typo` และ PORTS `8080` ของ `web-badport` พร้อมผลหลังแก้
- [ ] **LAB 8** browser ที่ `http://localhost:30080` แสดง `web v1 from web-...`, ผล `curl` วน 30 ครั้ง, error ของ 29999 และ 30080 ซ้ำ, `web-lb` ที่ `<pending>`
- [ ] **LAB 9** `bad address 'web'` จาก `kitchen`, nslookup ของ `web-headless` (3 IP) เทียบ `web` (1 IP), `canonical name = example.com` และผล NetworkPolicy port 8080 (timed out) เทียบ port 80 (ได้)
- [ ] **LAB 10** (1) `get rs,svc -n som-shop` (2) log `db-seed` `new: 6/0/0` (3) browser หน้าร้าน 1.2 ที่ `localhost:30080` (4) `./hit.sh` ครบทุกบูธ + `/api/stats` `orders=` เท่ากันทุกบูธ (5) EndpointSlice ของ `som-db` ก่อน/หลังลบ Pod db + ClusterIP เดิม + หน้า 503 (6) ร้านกลับมา `orders=0` (7) Pod ยัง 1.2 หลัง `set image` (8) `hit.sh` ที่เห็น 1.2/1.3 ปน และผล `-q` ตอนลบทีเดียว (ตัวเลข err ของตัวเอง) (9) browser หน้าร้าน 1.3
- [ ] ท้ายสุด `kubectl get ns` เหลือ namespace ตั้งต้น 5 ตัว และ `kubectl get svc -A | grep 3008` ว่าง

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| ตัวอย่าง `web` ของบทที่ 1 ที่จอง 30080 | ก่อนบทนี้ | `kubectl get svc -A \| grep 30080` | `kubectl delete -f /workspace/examples/web-deployment.yaml` |
| namespace `shop` (ReplicaSet `web`, `client`, `client2`, Service ทั้งหมด, NetworkPolicy) | 1–9 | `kubectl get all,netpol -n shop` | `kubectl delete ns shop` |
| Service `web-quick` | 2 | `kubectl -n shop get svc web-quick` | `kubectl -n shop delete svc web-quick` |
| `sessionAffinity: ClientIP` ของ `web` | 5 | `kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinity}'` | `kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"None"}}'` |
| บูธที่ไม่มี `index.html` (`0/1`) | 6 | `kubectl -n shop get pods` | คืนไฟล์ตามขั้นที่ 4 หรือ `kubectl -n shop delete pod <ชื่อ>` ให้ ReplicaSet สร้างใหม่ |
| Service `web-typo`, `web-badport` | 7 | `kubectl -n shop get svc` | `kubectl delete -f labs/lab07-debug/` |
| Service `web-nodeport` (30080), `web-lb` | 8 | `kubectl get svc -A \| grep -E '30080\|LoadBalancer'` | `kubectl delete -f labs/lab08-nodeport/web-nodeport.yaml -f labs/lab08-nodeport/web-lb.yaml` |
| namespace `kitchen` | 9 | `kubectl get ns kitchen` | `kubectl delete ns kitchen` |
| NetworkPolicy `web-from-kitchen` | 9 | `kubectl get netpol -A` | `kubectl -n shop delete netpol web-from-kitchen` |
| namespace `som-shop` (30080) | 10 | `kubectl get ns som-shop` | `kubectl delete ns som-shop` |
| `hit.sh` ที่ยังยิงอยู่ | 10 | `pgrep -af "[h]it.sh"` | Ctrl+C หรือ `pkill -f "[h]it.sh"` |
| image `som-shop-web:1.2`/`1.3`, postgres บน Node | 10 | `docker exec lab-worker crictl images \| grep -E "som-shop\|postgres"` | **เก็บไว้** ใช้ต่อในบทที่ 7 |

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

คลัสเตอร์ `lab` และ image `som-shop-web:1.2`/`1.3` บน Node **เก็บไว้ใช้ต่อในบทที่ 7 (Deployment)** ซึ่งเริ่มจากปัญหา "เปลี่ยนรุ่นแล้วร้านสะดุด" ของ LAB 10 ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น IP และจำนวน err) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริงถ่ายจาก NodePort 30080–30082 ของ namespace ที่สร้างเพื่อถ่ายภาพ (ดูหมายเหตุใต้แต่ละภาพ) ชื่อ Pod, IP และจำนวนออเดอร์ในภาพมาจากการทดลองรอบที่ถ่ายภาพ จึงอาจต่างจากผลคำสั่งในเอกสาร
