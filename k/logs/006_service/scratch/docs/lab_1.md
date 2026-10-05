# LAB บทที่ 6: Service — ประภาคารที่ชื่อและที่อยู่ไม่เคยเปลี่ยน สู่ร้านน้องส้มที่แยก web กับ db

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ Service — ปัญหาของการเรียก Pod ด้วย IP, ClusterIP และ EndpointSlice, port/targetPort/ชื่อพอร์ต, DNS/search domain/env var, การกระจายโหลดและ sessionAffinity, readinessProbe กับ endpoints, debug Service, NodePort/LoadBalancer/keep-alive, เรียกข้าม namespace, headless, ExternalName, NetworkPolicy และร้านอาหารแมวน้องส้มที่แยก web กับ db ด้วย ReplicaSet + Service
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่สร้าง **ประภาคาร (Service)** ให้ร้าน เริ่มจากเห็นด้วยตาตัวเองว่าการจด IP ของ Pod ไว้ใช้ไม่ได้ แล้วสร้าง Service ตัวแรก อ่านรายชื่อบูธใน EndpointSlice ลองพอร์ต 3 ชั้น เรียกร้านด้วยชื่อ DNS ดูการสุ่มกระจายลูกค้า ปิดไฟเขียวของบูธหนึ่ง ไล่ debug Service ที่ตั้งค่าผิด เปิดร้านจาก browser ด้วย **`http://localhost:30080`** (บทแรกที่ไม่ต้องใช้ port-forward/ssh -L) และเรียก Service ข้าม namespace ปิดท้ายด้วย **ร้านอาหารแมวน้องส้มที่แยกหน้าร้าน (web) ออกจากครัวกลาง (db) เป็นครั้งแรก** ทำให้ออเดอร์จากทุกบูธรวมที่เดียว แต่จะเผยปัญหาตอนเปลี่ยนรุ่นที่ส่งต่อให้บทที่ 7

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, Kubernetes v1.37.0) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, ClusterIP, Pod IP, ชื่อ Pod ที่สุ่ม (เช่น `web-k2nk5`), จำนวนครั้งที่สุ่มได้ และ Node ที่ scheduler เลือก ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ และเมื่อคำสั่งในเอกสารมีชื่อ Pod หรือ IP ให้ **แทนด้วยค่าที่เห็นในเครื่องตัวเอง** (หรือใช้ตัวแปรตามที่เอกสารแสดง)

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
- **LAB 1–9 ใช้ namespace `shop` ต่อเนื่องกัน** (LAB 9 เพิ่ม `kitchen`) แล้วลบทิ้งตอนท้าย LAB 9 ส่วน LAB 10 ใช้ `som-shop` ถ้าหยุดกลางทางหรือผลเพี้ยน ให้ `kubectl delete ns shop kitchen` แล้วเริ่มใหม่จาก LAB 1 ได้ (ดู [ตารางเก็บกวาด]({{A:ตารางเก็บกวาดและคืนสภาพ}}))
- **NodePort 30080 จองได้ทีละ Service ทั้งคลัสเตอร์** ต้องลบ `web-nodeport` ของ LAB 8 ก่อนเริ่ม LAB 10
- Pod busybox ใน LAB ตั้ง `terminationGracePeriodSeconds: 1` และ image สาธารณะ (`nginx:1.27-alpine`, `busybox:1.36`) ให้ Node ดึงเอง ไม่ต้อง `kind load`
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง (ของจริงเก็บใน Secret ซึ่งเป็นเนื้อหาบทหลัง)

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์และตรวจพอร์ต 30080–30082]({{A:LAB 0: เตรียมคลัสเตอร์และตรวจพอร์ต 30080–30082}}) | 15 นาที | ⭐ |
| 1 | [ปัญหาก่อนมี Service]({{A:LAB 1: ปัญหาก่อนมี Service}}) | 10 นาที | ⭐ |
| 2 | [ClusterIP แรกและ EndpointSlice]({{A:LAB 2: ClusterIP แรกและ EndpointSlice}}) | 15 นาที | ⭐ |
| 3 | [port, targetPort และชื่อพอร์ต]({{A:LAB 3: port, targetPort และชื่อพอร์ต}}) | 10 นาที | ⭐⭐ |
| 4 | [DNS, search domain และ env var]({{A:LAB 4: DNS, search domain และ env var}}) | 15 นาที | ⭐⭐ |
| 5 | [การกระจายโหลดและ sessionAffinity]({{A:LAB 5: การกระจายโหลดและ sessionAffinity}}) | 10 นาที | ⭐⭐ |
| 6 | [readinessProbe กับ endpoints]({{A:LAB 6: readinessProbe กับ endpoints}}) | 10 นาที | ⭐⭐ |
| 7 | [debug Service]({{A:LAB 7: debug Service}}) | 15 นาที | ⭐⭐⭐ |
| 8 | [NodePort 30080, LoadBalancer และ keep-alive]({{A:LAB 8: NodePort 30080, LoadBalancer และ keep-alive}}) | 20 นาที | ⭐⭐⭐ |
| 9 | [ข้าม namespace, headless, ExternalName และ NetworkPolicy]({{A:LAB 9: ข้าม namespace, headless, ExternalName และ NetworkPolicy}}) | 20 นาที | ⭐⭐⭐⭐ |
| 10 | [LAB สุดท้าย: แยก web กับ db ครั้งแรก]({{A:LAB 10: LAB สุดท้าย: แยก web กับ db ครั้งแรก}}) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting]({{A:Troubleshooting}}) · [Checklist ส่งงาน]({{A:Checklist ส่งงาน}}) · [ตารางเก็บกวาดและคืนสภาพ]({{A:ตารางเก็บกวาดและคืนสภาพ}}) · [เก็บกวาดหลังจบบท]({{A:เก็บกวาดหลังจบบท}}) | | |

รวมประมาณ 3–3.5 ชั่วโมง (LAB 10 มีช่วง build image ของแอป)

### สารบัญรูปภาพ

{{FIGTOC}}

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

{{FIG:L01}}

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 5 หรือสร้างใหม่) ตรวจว่า NodePort 30080–30082 ยังว่าง และรู้จัก Service ที่มีอยู่ในคลัสเตอร์ตั้งแต่แรก

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md), [2](../../002_kubernetes_pod/02_LAB/README.md), [3](../../003_kubernetes_node_pod/02_LAB/README.md), [4](../../004_kubernetes_namespace/02_LAB/README.md) และ [5](../../005_kubernetes_replicaset/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`) และมีโฟลเดอร์ `006_kubernetes_service` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

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
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   4m30s   v1.37.0
lab-worker          Ready    <none>          4m19s   v1.37.0
lab-worker2         Ready    <none>          4m19s   v1.37.0
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

real	0m47.936s
```

สังเกตสองบรรทัดท้าย: `k8s-up` แนะนำตัวอย่าง `/workspace/examples/web-deployment.yaml` ที่เปิดหน้าเว็บที่ `http://localhost:30080` และบอกว่า **NodePort 30080 30081 30082 ถูก map ออกมาที่เครื่องนักศึกษา** ทั้งสองเรื่องเกี่ยวกับบทนี้โดยตรง

### ขั้นที่ 4: ตรวจว่า NodePort 30080–30082 ยังว่าง

ถ้าเคยลองตัวอย่างของบทที่ 1 ไว้ Service ของตัวอย่างนั้นจะยังจองพอร์ต 30080 อยู่ (เลข nodePort ใช้ได้ทีละ Service ทั้งคลัสเตอร์) ทำให้ LAB 8 และ LAB 10 สร้าง Service ไม่ได้

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get svc -A | grep -E '3008[0-2]' || echo '(ว่าง)'
```

ถ้าได้ `(ว่าง)` ข้ามไปขั้นที่ 5 ได้เลย ถ้าเห็นบรรทัดแบบนี้ (ผลจริงเมื่อจำลองว่าตัวอย่างของบทที่ 1 ยังค้างอยู่)

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
default       kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  4m57s
kube-system   kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   4m56s

NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   4m57s

    mode: iptables

NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
kube-proxy   3         3         3       3            3           kubernetes.io/os=linux   4m56s

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

lab-control-plane	0.0.0.0:30080-30082->30080-30082/tcp, 127.0.0.1:41689->6443/tcp
lab-worker2	
lab-worker	
```

เส้นทางของพอร์ต 30080 ถูกเตรียมไว้ตั้งแต่บทที่ 1 แล้ว 3 ชั้น

1. 🖥️ เครื่องนักศึกษา `localhost:30080` → container `k8s-lab` (ตอนสร้าง k8s-lab ในบทที่ 1 ใช้ `docker run ... -p 30080-30082:30080-30082 ...`)
2. 🐧 `k8s-lab:30080` → container `lab-control-plane:30080` (kind `extraPortMappings` ที่เห็นใน `docker ps` ด้านบน)
3. `lab-control-plane:30080` → Pod ที่อยู่หลัง Service ชนิด NodePort ที่ใช้ `nodePort: 30080` (ยังไม่มีตอนนี้ จะสร้างใน LAB 8 และ LAB 10)

เลขพอร์ต `127.0.0.1:41689->6443` ของ API server ในเครื่องนักศึกษาจะต่างจากนี้ ไม่ต้องสนใจ

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

{{FIG:L02}}

**เป้าหมาย:** สร้างร้าน `web` 3 บูธด้วย ReplicaSet แล้วเห็นว่า IP ของ Pod เปลี่ยนเมื่อ ReplicaSet สร้าง Pod แทน IP ที่จดไว้จึงใช้ไม่ได้

ไฟล์ใน `labs/lab01-before-service/` (ตัด `resources` ออกเพื่อให้สั้น)

```yaml
# LAB 1: ร้าน web 3 บูธ (ReplicaSet จากบท 005) — ยังไม่มี Service
# หน้าเว็บตอบ "web v1 from <ชื่อ Pod>" → เห็นทันทีว่า request ไปตกบูธไหน
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web
  namespace: shop
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web                   # Service จะเลือก Pod ด้วยป้ายนี้ (LAB 2)
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine   # image สาธารณะ — Node pull เอง ไม่ต้อง kind load
          env:
            - name: VERSION
              value: v1
          # เขียนหน้า index ให้บอกรุ่นและชื่อ Pod แล้วเปิด nginx
          command: ["sh", "-c", "echo \"web $VERSION from $(hostname)\" > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]
          ports:
            - name: http             # ตั้งชื่อพอร์ต → Service อ้าง targetPort: http ได้
              containerPort: 80
          readinessProbe:            # ไฟเขียวหน้าบูธ: ไม่ผ่าน = Service ไม่ส่งลูกค้ามา (LAB 6)
            httpGet: { path: /, port: http }
            periodSeconds: 2
```

นอกจากนี้มี `00-ns.yaml` (namespace `shop` label `team: som`) และ `client-pod.yaml` (Pod `client` image `busybox:1.36` label `role=client` รัน `sleep infinity` ไว้ยิง `wget`/`nslookup` จากในคลัสเตอร์)

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
pod/web-999d4 condition met
pod/web-9gngn condition met
pod/web-mgz49 condition met
pod/client condition met

NAME                  DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES              SELECTOR   LABELS
replicaset.apps/web   3         3         3       13s   nginx        nginx:1.27-alpine   app=web    app=web

NAME            READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES   LABELS
pod/client      1/1     Running   0          13s   10.244.2.4   lab-worker    <none>           <none>            role=client
pod/web-999d4   1/1     Running   0          13s   10.244.2.5   lab-worker    <none>           <none>            app=web
pod/web-9gngn   1/1     Running   0          13s   10.244.1.3   lab-worker2   <none>           <none>            app=web
pod/web-mgz49   1/1     Running   0          13s   10.244.1.4   lab-worker2   <none>           <none>            app=web
```

ครั้งแรก Node ต้องดึง image `nginx` และ `busybox` จาก Docker Hub จึงใช้เวลาราว 10–20 วินาที

### ขั้นที่ 2: เรียกบูธด้วย Pod IP แล้วลบบูธนั้น

เลือก Pod `web` ตัวหนึ่งจากผลของขั้นที่ 1 แล้ว **แทน `10.244.1.3` และ `web-9gngn` ด้วย IP และชื่อในเครื่องตัวเอง**

```bash
kubectl -n shop exec client -- wget -qO- http://10.244.1.3
kubectl -n shop delete pod web-9gngn
kubectl -n shop exec client -- wget -qO- -T 3 http://10.244.1.3; echo "exit=$?"
kubectl -n shop get pods -o wide
```

```text
web v1 from web-9gngn
pod "web-9gngn" deleted from shop namespace
wget: download timed out
command terminated with exit code 1
exit=1
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          33s   10.244.2.4   lab-worker    <none>           <none>
web-999d4   1/1     Running   0          33s   10.244.2.5   lab-worker    <none>           <none>
web-k2nk5   1/1     Running   0          4s    10.244.2.6   lab-worker    <none>           <none>
web-mgz49   1/1     Running   0          33s   10.244.1.4   lab-worker2   <none>           <none>
```

- หน้าเว็บบอก `web v1 from web-9gngn` คือชื่อ Pod ที่ตอบ (มาจาก `$(hostname)` ใน command ของ container)
- หลังลบ ReplicaSet สร้าง `web-k2nk5` แทนภายในไม่กี่วินาที แต่ได้ **ชื่อใหม่และ IP ใหม่** (`10.244.2.6`)
- เรียก IP เดิมได้ `wget: download timed out` (ใช้ `-T 3` ให้รอแค่ 3 วินาที) ถ้า IP เดิมบังเอิญถูก Pod อื่นนำไปใช้ อาจได้คำตอบจาก Pod ที่ไม่เกี่ยวข้องหรือ `Connection refused` แทน ซึ่งแย่กว่าเพราะดูเหมือนใช้ได้

### สิ่งที่เห็น

- ReplicaSet แก้ปัญหา "จำนวน" (ยังมี 3 บูธ) แต่ไม่แก้ปัญหา "ที่อยู่" ลูกค้าที่จด IP ไว้หาร้านไม่เจอ
- เราจะใช้ Pod `client` ตัวนี้เป็นลูกค้าในคลัสเตอร์ต่อไปจนถึง LAB 9 (อย่าลบ)

**คำถามชวนคิด**

1. ถ้ามีแอปอื่นจด IP `10.244.2.5` ของ `web-999d4` ไว้ แล้วน้องส้ม scale ReplicaSet ลงเหลือ 2 แอปนั้นจะเจออะไร
2. ทำไม Pod `client` จึงไม่ถูกนับเป็นบูธของ ReplicaSet `web`

---

## LAB 2: ClusterIP แรกและ EndpointSlice

{{FIG:L03}}

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
  clusterIP: 10.96.84.23
  clusterIPs:
  - 10.96.84.23
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

ไฟล์ `labs/lab02-clusterip/web-svc.yaml`

```yaml
# LAB 2: Service แรก — ClusterIP (ค่าเริ่มต้น) ชื่อ web
# ชื่อ "web" + IP เสมือน (ClusterIP) คงที่ ส่งต่อไป Pod ที่มีป้าย app=web และ Ready
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: shop
spec:
  type: ClusterIP          # ไม่ใส่ก็ได้ (ค่าเริ่มต้น)
  selector:
    app: web               # เลือก Pod ด้วย label (ไม่สนว่าใครสร้าง Pod)
  ports:
    - port: 80             # พอร์ตที่ Service รับ (http://web:80)
      targetPort: http     # พอร์ตของ container (ชื่อ http = containerPort 80)
```

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
service/web   ClusterIP   10.96.55.132   <none>        80/TCP    0s

NAME                                       ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
endpointslice.discovery.k8s.io/web-5r58w   IPv4          80      10.244.2.5,10.244.1.4,10.244.2.6   0s

NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          50s   10.244.2.4   lab-worker    <none>           <none>
web-999d4   1/1     Running   0          50s   10.244.2.5   lab-worker    <none>           <none>
web-k2nk5   1/1     Running   0          21s   10.244.2.6   lab-worker    <none>           <none>
web-mgz49   1/1     Running   0          50s   10.244.1.4   lab-worker2   <none>           <none>

Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                                   AGE
web    10.244.1.4:80,10.244.2.5:80,10.244.2.6:80   1s

Name:                     web
Namespace:                shop
Labels:                   <none>
Annotations:              <none>
Selector:                 app=web
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.96.55.132
IPs:                      10.96.55.132
Port:                     <unset>  80/TCP
TargetPort:               http/TCP
Endpoints:                10.244.2.5:80,10.244.1.4:80,10.244.2.6:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
```

- Service `web` ได้ ClusterIP `10.96.55.132` (ในเครื่องนักศึกษาจะเป็นเลขอื่นในช่วง `10.96.x.x`) **จดไว้** จะใช้ในขั้นที่ 4
- EndpointSlice ชื่อ `web-5r58w` (ชื่อ Service + สุ่ม) มี 3 IP ตรงกับ Pod `web-*` ไม่มี `client` เพราะ label ไม่ตรง
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
    - 10.244.2.5
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: lab-worker
    targetRef:
      kind: Pod
      name: web-999d4
      namespace: shop
  ...
  kind: EndpointSlice
  metadata:
    ...
    generateName: web-
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web
    name: web-5r58w
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

แทน `10.96.55.132` ด้วย ClusterIP ของตัวเอง และ `10.244.2.5` ด้วย IP ของ Pod `web` ตัวหนึ่ง

```bash
kubectl -n shop exec client -- wget -qO- http://web
kubectl -n shop exec client -- ping -c 2 -W 2 10.96.55.132; echo "exit=$?"
kubectl -n shop exec client -- ping -c 2 -W 2 10.244.2.5
```

```text
web v1 from web-999d4

PING 10.96.55.132 (10.96.55.132): 56 data bytes

--- 10.96.55.132 ping statistics ---
2 packets transmitted, 0 packets received, 100% packet loss
command terminated with exit code 1
exit=1

PING 10.244.2.5 (10.244.2.5): 56 data bytes
64 bytes from 10.244.2.5: seq=0 ttl=63 time=0.063 ms
64 bytes from 10.244.2.5: seq=1 ttl=63 time=0.064 ms

--- 10.244.2.5 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.063/0.063/0.064 ms
```

`wget http://web` ได้หน้าเว็บด้วย **ชื่อ** แต่ ping ClusterIP ได้ 100% packet loss ส่วน ping Pod IP ได้ปกติ เพราะ ClusterIP เป็นที่อยู่เสมือนที่ไม่มีเครื่องใดถือจริง (ทฤษฎีหัวข้อ 2.2) **ping ไม่ตอบไม่ได้แปลว่า Service เสีย**

### ขั้นที่ 5: scale และลบ Pod แล้วดูรายชื่อเปลี่ยนเอง

{{FIG:L04}}

```bash
kubectl -n shop scale rs web --replicas=5
kubectl -n shop wait --for=condition=Ready pod -l app=web --timeout=60s >/dev/null
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
```

```text
replicaset.apps/web scaled
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-5r58w   IPv4          80      10.244.2.5,10.244.1.4,10.244.2.6 + 2 more...   39s
```

คอลัมน์ ENDPOINTS แสดงแค่ 3 IP แรกแล้วต่อด้วย `+ 2 more...` (แม้ใช้ `-o wide`) ดูครบทุกตัวด้วย jsonpath

```bash
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
```

จากนั้นลบ Pod ตัวหนึ่ง (แทน `web-999d4` ด้วยชื่อในเครื่องตัวเอง) แล้วดูรายชื่อก่อนและหลังรอ 3 วินาที เทียบกับ ClusterIP

```bash
kubectl -n shop delete pod web-999d4
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
sleep 3; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
kubectl -n shop get svc web
```

```text
pod "web-999d4" deleted from shop namespace
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-5r58w   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5 + 2 more...   41s
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-5r58w   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5 + 2 more...   44s
NAME   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
web    ClusterIP   10.96.55.132   <none>        80/TCP    44s
```

IP `10.244.2.5` ของ Pod ที่ถูกลบหายจากรายชื่อทันที Pod ใหม่เข้ามาแทน ส่วน **ClusterIP ยังเป็นเลขเดิม** ลูกค้าที่เรียก `web` ไม่ต้องรู้เรื่องนี้เลย

คืนเป็น 3 บูธ

```bash
kubectl -n shop scale rs web --replicas=3
sleep 2; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
kubectl -n shop get pods -o wide
```

```text
replicaset.apps/web scaled
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-5r58w   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5   46s
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
client      1/1     Running   0          95s   10.244.2.4   lab-worker    <none>           <none>
web-gsgss   1/1     Running   0          9s    10.244.1.5   lab-worker2   <none>           <none>
web-k2nk5   1/1     Running   0          66s   10.244.2.6   lab-worker    <none>           <none>
web-mgz49   1/1     Running   0          95s   10.244.1.4   lab-worker2   <none>           <none>
```

### สิ่งที่เห็น

- `kubectl expose` สร้าง Service ได้เร็วแต่ใส่ targetPort เป็นเลข ไฟล์ YAML ควบคุมได้ละเอียดกว่า
- EndpointSlice ถูกเขียนให้อัตโนมัติ มี IP ของ Pod ที่ตรง selector, conditions, targetRef และ ownerReferences ชี้ Service
- ClusterIP ping ไม่ตอบ แต่เรียกด้วยชื่อ/พอร์ตของ Service ได้
- scale หรือลบ Pod แล้วรายชื่อเปลี่ยนเอง ClusterIP ไม่เปลี่ยน

**คำถามชวนคิด**

1. ถ้าลบ Service `web` แล้ว apply ใหม่ ClusterIP จะเหมือนเดิมไหม แอปที่เรียกด้วยชื่อ `web` จะกระทบไหม
2. ทำไม PORTS ของ EndpointSlice จึงเป็น `80` ทั้งที่ Service ใช้ `targetPort: http`

---

## LAB 3: port, targetPort และชื่อพอร์ต

{{FIG:L05}}

**เป้าหมาย:** เข้าใจพอร์ต 3 ชั้นด้วย Service ที่รับคนละพอร์ตกับ Pod และ Service หลายพอร์ตที่ต้องตั้งชื่อ

**ต้องมีจาก LAB 2:** Service `web` และ Pod `client`

### ขั้นที่ 1: Service รับ 8080 ส่งต่อ 80

ไฟล์ `labs/lab03-ports/web-alt-svc.yaml`

```yaml
# LAB 3: Service รับที่พอร์ต 8080 แต่ส่งต่อไปพอร์ต 80 (ชื่อ http) ของ Pod
apiVersion: v1
kind: Service
metadata:
  name: web-alt
  namespace: shop
spec:
  selector:
    app: web
  ports:
    - port: 8080           # ลูกค้าเรียก http://web-alt:8080
      targetPort: http     # → containerPort ชื่อ http (80)
```

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab03-ports/web-alt-svc.yaml
kubectl -n shop get svc web-alt
kubectl -n shop exec client -- wget -qO- http://web-alt:8080
time kubectl -n shop exec client -- wget -qO- -T 3 http://web-alt; echo "exit=$?"
```

```text
service/web-alt created
NAME      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
web-alt   ClusterIP   10.96.141.242   <none>        8080/TCP   0s
web v1 from web-gsgss
wget: download timed out
command terminated with exit code 1

real	0m3.060s
user	0m0.031s
sys	0m0.019s
exit=1
```

`web-alt:8080` ได้หน้าเว็บ (kube-proxy แปลง `8080 → 80` ให้) แต่เรียก `web-alt` เฉย ๆ (พอร์ต 80) **เงียบจนครบ 3 วินาที** (`download timed out`) ไม่ใช่ถูกปฏิเสธ เพราะ Service นี้ไม่ได้ประกาศพอร์ต 80 จึงไม่มีกฎรองรับ

### ขั้นที่ 2: Service หลายพอร์ต

ไฟล์ `labs/lab03-ports/web-multi-svc.yaml`

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
    - name: http
      port: 80
      targetPort: http
    - name: alt
      port: 8080
      targetPort: http     # สองพอร์ตของ Service ชี้ไปพอร์ตเดียวกันของ Pod ได้
```

```bash
kubectl apply -f labs/lab03-ports/web-multi-svc.yaml
kubectl -n shop get svc web-multi
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-multi
kubectl -n shop exec client -- wget -qO- http://web-multi
kubectl -n shop exec client -- wget -qO- http://web-multi:8080
```

```text
service/web-multi created
NAME        TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)           AGE
web-multi   ClusterIP   10.96.28.97   <none>        80/TCP,8080/TCP   0s
NAME              ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-multi-4gzd9   IPv4          80,80   10.244.1.5,10.244.1.4,10.244.2.6   0s
wget: can't connect to remote host (10.96.28.97): Connection refused
command terminated with exit code 1
web v1 from web-k2nk5
```

ครั้งแรกที่เรียก `web-multi` หลังสร้างเสร็จไม่ถึง 1 วินาที ได้ `Connection refused` เพราะ kube-proxy ยังเขียนกฎไม่เสร็จ **ลองซ้ำอีกครั้ง** จะใช้ได้ทั้งสองพอร์ต ผลจริงเมื่อเรียกซ้ำ และดูพอร์ตใน EndpointSlice

```bash
for i in 1 2 3; do kubectl -n shop exec client -- wget -qO- http://web-multi; done
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-multi -o jsonpath="{.items[0].ports}"; echo
```

```text
web v1 from web-k2nk5
web v1 from web-k2nk5
web v1 from web-gsgss
[{"name":"alt","port":80,"protocol":"TCP"},{"name":"http","port":80,"protocol":"TCP"}]
```

EndpointSlice เก็บพอร์ตแยกตามชื่อของพอร์ต Service (`alt`, `http`) ทั้งคู่ชี้ไปพอร์ต 80 ของ Pod คอลัมน์ PORTS จึงเป็น `80,80`

### ขั้นที่ 3: ลืมตั้งชื่อพอร์ต

ไฟล์ `labs/lab03-ports/web-multi-noname.yaml` (ตั้งใจผิด)

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
    - name: http
      port: 80
      targetPort: http
    - port: 8080           # ← ไม่มี name (ports[1])
      targetPort: http
```

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
- Service ที่เพิ่งสร้างอาจตอบ `Connection refused` ใน ~1 วินาทีแรก

**คำถามชวนคิด**

1. ถ้าวันหนึ่ง nginx ใน Pod เปลี่ยนไปฟังพอร์ต 8080 แต่ยังตั้งชื่อ `http` Service `web`, `web-alt`, `web-multi` ต้องแก้ไหม
2. Service `web-quick` ที่สร้างด้วย `expose` ใน LAB 2 (targetPort `80`) จะเป็นอย่างไรในสถานการณ์ข้อ 1

---

## LAB 4: DNS, search domain และ env var

{{FIG:L06}}

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

** server can't find web.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN


Name:	web.shop.svc.cluster.local
Address: 10.96.55.132

** server can't find web.svc.cluster.local: NXDOMAIN

command terminated with exit code 1

Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web.shop.svc.cluster.local
Address: 10.96.55.132
```

- `nslookup web` **หาเจอ** (`web.shop.svc.cluster.local` → ClusterIP ของ `web`) แต่ `nslookup` ของ busybox ถามทุก search domain พร้อมกันแล้วพิมพ์ทุกผล จึงมีบรรทัด `NXDOMAIN` ของโดเมนที่ไม่ตรงปนอยู่ และจบด้วย `exit code 1` **ไม่ได้แปลว่า DNS เสีย**
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

web v1 from web-k2nk5

web v1 from web-k2nk5
```

- `search` ขึ้นต้นด้วย namespace ของ Pod (`shop.svc.cluster.local`) ชื่อสั้น `web` จึงกลายเป็น `web.shop.svc.cluster.local`
- `ndots:5`: ชื่อที่มีจุดน้อยกว่า 5 ถูกลองเติม search domain ก่อน `wget http://web.shop` จึงใช้ได้ (เติม `.svc.cluster.local`)
- แต่ `nslookup web.shop` ของ busybox ได้ NXDOMAIN เพราะ busybox ไม่เติม search domain ให้ชื่อที่มีจุด เป็นข้อจำกัดของเครื่องมือ ไม่ใช่ของคลัสเตอร์
- ชื่อเต็มลงท้ายจุด (`web.shop.svc.cluster.local.`) ข้ามการเติม search ทั้งหมด

### ขั้นที่ 3: env var ของ Service

Pod `client` ถูกสร้างใน LAB 1 **ก่อน** มี Service ส่วน `client2` (ไฟล์ `labs/lab04-dns/client2-pod.yaml` เหมือน `client` ทุกอย่างยกเว้นชื่อ) จะสร้าง **หลัง** Service `web`, `web-alt`, `web-multi`

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
WEB_ALT_PORT=tcp://10.96.141.242:8080
WEB_ALT_PORT_8080_TCP=tcp://10.96.141.242:8080
WEB_ALT_PORT_8080_TCP_ADDR=10.96.141.242
WEB_ALT_PORT_8080_TCP_PORT=8080
WEB_ALT_PORT_8080_TCP_PROTO=tcp
WEB_ALT_SERVICE_HOST=10.96.141.242
WEB_ALT_SERVICE_PORT=8080
WEB_MULTI_PORT=tcp://10.96.28.97:80
...
WEB_MULTI_SERVICE_HOST=10.96.28.97
WEB_MULTI_SERVICE_PORT=80
WEB_MULTI_SERVICE_PORT_ALT=8080
WEB_MULTI_SERVICE_PORT_HTTP=80
WEB_PORT=tcp://10.96.55.132:80
WEB_PORT_80_TCP=tcp://10.96.55.132:80
WEB_PORT_80_TCP_ADDR=10.96.55.132
WEB_PORT_80_TCP_PORT=80
WEB_PORT_80_TCP_PROTO=tcp
WEB_SERVICE_HOST=10.96.55.132
WEB_SERVICE_PORT=80
```

- `client` ไม่มี env `WEB_*` เลย (`grep` ไม่เจอจึง `exit=1`) เพราะ env ของ container ถูกตั้งครั้งเดียวตอนสร้าง
- `client2` ได้ env ของทุก Service ใน `shop` ชื่อ Service แปลงเป็นตัวพิมพ์ใหญ่และ `-` เป็น `_` (`web-alt` → `WEB_ALT_...`)
- มี `WEB_MULTI_SERVICE_PORT_HTTP`/`_ALT` เพราะพอร์ตของ `web-multi` มีชื่อ แต่ **ไม่มี `WEB_SERVICE_PORT_HTTP`** เพราะพอร์ตของ Service `web` ไม่ได้ตั้งชื่อ

Pod `web` เองก็เป็นแบบเดียวกัน ดูชื่อด้วย `kubectl -n shop get pods` แล้วแทนชื่อด้วย Pod ที่สร้าง **ก่อน** LAB 2 (เช่น `web-mgz49`) และ Pod ที่เกิด **หลัง** LAB 2 (เช่น `web-gsgss` ที่เกิดตอน scale ใน LAB 2)

```bash
kubectl -n shop exec web-mgz49 -- env | grep SERVICE_HOST
kubectl -n shop exec web-gsgss -- env | grep WEB_SERVICE
```

```text
KUBERNETES_SERVICE_HOST=10.96.0.1
WEB_SERVICE_HOST=10.96.55.132
WEB_SERVICE_PORT=80
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

