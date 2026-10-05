# LAB บทที่ 5: ReplicaSet — หัวหน้ากะที่นับบูธให้ครบ สู่ร้านน้องส้ม 3 บูธ

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ ReplicaSet — ทบทวน Pod เดี่ยวที่หายถาวร, สร้าง ReplicaSet แรก, self-healing (ลบ Pod, drain, เรือล่ม), scale, กับดัก label, selector ที่แก้ไม่ได้และ template ใหม่, ลบแบบ cascade/orphan, ReplicaSet กับ quota/LimitRange/PSA, กระจาย replica ข้ามเรือ และร้านอาหารแมวน้องส้ม 3 บูธด้วย ReplicaSet
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะทำตามน้องส้มที่จ้าง **หัวหน้ากะ (ReplicaSet)** มานับบูธให้ครบ เริ่มจากยืนยันอีกครั้งว่า Pod เดี่ยวลบแล้วหายถาวร แล้วสร้าง ReplicaSet ตัวแรก ลองลบ Pod, drain เรือ และ (ทางเลือก) ทำให้เรือล่มเพื่อดู self-healing scale ขึ้นลงและดูว่า Pod ตัวไหนถูกลบ เจอกับดักของการ "นับจาก label" ลองแก้ selector และ template ลบ ReplicaSet แบบต่าง ๆ ทดลองกับงบและด่านความปลอดภัยของบทที่ 4 และกระจายบูธข้ามเรือแบบบทที่ 3 ปิดท้ายด้วย **ร้านอาหารแมวน้องส้ม 3 บูธ** ที่ไม่ล้มแม้บูธหาย แต่จะเผยปัญหาใหม่ 3 ข้อที่ส่งต่อไปบทที่ 6 และ 7

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`: kubectl v1.37.1, kind 0.33.0, Node v1.37.0, containerd 2.3.4) เมื่อ 5 ตุลาคม 2569 โดยรันคำสั่งในเอกสารตามลำดับตั้งแต่ LAB 0 ถึง LAB 9 ในคลัสเตอร์เดียวกัน ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม (เช่น `snack-rs-2xn5v`), uid, เลข process และ Node ที่ scheduler เลือก (lab-worker หรือ lab-worker2) ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ และเมื่อคำสั่งในเอกสารมีชื่อ Pod ให้ **แทนด้วยชื่อที่เห็นในเครื่องตัวเอง** (หรือใช้ตัวแปรตามที่เอกสารแสดง)

ทุกไฟล์ YAML ที่ LAB ใช้มีหัวข้อย่อย **"อธิบาย YAML"** ตรงจุดที่ใช้ไฟล์นั้นครั้งแรก และในไฟล์เองมีคอมเมนต์ภาษาไทย (`# ...`) กำกับ field สำคัญ

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind` และ `docker` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิดท่อ `ssh -L` ใน LAB 9 ที่ทำ 🖥️ บนเครื่องนักศึกษา หลาย LAB ใช้ **2 หน้าต่าง** (เรียกว่า terminal 1 และ terminal 2) ให้เปิด SSH session ที่สองด้วยคำสั่งเดียวกัน

### กติกาของ LAB บทนี้

- ทุก LAB ทำในโฟลเดอร์ **`/workspace/005_kubernetes_replicaset/02_LAB`** ภายใน k8s-lab (LAB 9 ย้ายเข้า `som-booths/` ตามที่บอกในขั้นตอน)
- บทนี้ใช้ **ReplicaSet เท่านั้น** ยังไม่ใช้ตัวช่วยเรื่องที่อยู่คงที่หรือการเปลี่ยนรุ่น (เนื้อหาบทที่ 6–7) การเข้าถึงแอปใช้ `kubectl exec`, `kubectl logs` และ `kubectl port-forward pod/...` + `ssh -L` เหมือนบทที่ 2–4
- **ทุก LAB ทำใน namespace ของตัวเอง** LAB 0–6 ใช้ namespace `rs-lab` ต่อเนื่องกัน (ลบตอนท้าย LAB 6) LAB 7 ใช้ `rs-quota`/`rs-psa` LAB 8 ใช้ `rs-spread` LAB 9 ใช้ `som-booths` ทุก LAB จบด้วยบล็อก "เก็บกวาด"
- Pod busybox ใน LAB ตั้ง `terminationGracePeriodSeconds: 1` เพราะ `sh` ไม่ตอบ SIGTERM ทำให้ Pod ที่ถูกลบขึ้นสถานะ `Error` ชั่วครู่ก่อนหาย **ไม่ใช่ความผิดพลาด**
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์ + ทบทวน Pod เดี่ยวหายถาวร](#lab-0-เตรียมคลัสเตอร์--ทบทวน-pod-เดี่ยวหายถาวร) | 15 นาที | ⭐ |
| 1 | [ReplicaSet แรก](#lab-1-replicaset-แรก) | 15 นาที | ⭐ |
| 2 | [Self-healing: ลบ Pod, drain และเรือล่ม](#lab-2-self-healing-ลบ-pod-drain-และเรือล่ม) | 20 นาที (+10 นาทีทางเลือก) | ⭐⭐ |
| 3 | [Scale](#lab-3-scale) | 10 นาที | ⭐⭐ |
| 4 | [กับดัก label](#lab-4-กับดัก-label) | 20 นาที | ⭐⭐⭐ |
| 5 | [selector แก้ไม่ได้ + template ใหม่ Pod เดิมไม่เปลี่ยน](#lab-5-selector-แก้ไม่ได้--template-ใหม่-pod-เดิมไม่เปลี่ยน) | 15 นาที | ⭐⭐⭐ |
| 6 | [ลบ ReplicaSet แบบ cascade vs orphan](#lab-6-ลบ-replicaset-แบบ-cascade-vs-orphan) | 10 นาที | ⭐⭐⭐ |
| 7 | [ReplicaSet กับ quota, LimitRange และ PSA](#lab-7-replicaset-กับ-quota-limitrange-และ-psa) | 15 นาที | ⭐⭐⭐ |
| 8 | [กระจาย replica ด้วย anti-affinity และ topology spread](#lab-8-กระจาย-replica-ด้วย-anti-affinity-และ-topology-spread) | 15 นาที | ⭐⭐⭐ |
| 9 | [LAB สุดท้าย: ร้านน้องส้ม 3 บูธด้วย ReplicaSet](#lab-9-lab-สุดท้าย-ร้านน้องส้ม-3-บูธด้วย-replicaset) | 60 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (LAB 9 อาจมีช่วง build image ของแอปถ้าเป็นคลัสเตอร์ใหม่)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [LAB 0 เตรียมคลัสเตอร์](#fig-1) | 13 | [LAB 9 3 บูธบน 2 เรือ](#fig-13) |
| 2 | [LAB 1 ReplicaSet แรก](#fig-2) | 14 | [LAB 9 port-forward ทีละบูธ](#fig-14) |
| 3 | [LAB 2 ลบ Pod แล้วดูด้วย -w](#fig-3) | 15 | [LAB 9 ออเดอร์ไม่ตรงกัน](#fig-15) |
| 4 | [LAB 2 drain และเรือล่ม](#fig-4) | 16 | [ภาพหน้าจอจริง บูธที่ 1](#fig-16) |
| 5 | [LAB 3 scale](#fig-5) | 17 | [ภาพหน้าจอจริง บูธที่ 2](#fig-17) |
| 6 | [LAB 4 กับดัก label](#fig-6) | 18 | [ภาพหน้าจอจริง บูธที่ 3](#fig-18) |
| 7 | [LAB 5 template ใหม่ Pod เดิมไม่เปลี่ยน](#fig-7) | 19 | [LAB 9 ลบบูธแล้วข้อมูลหาย](#fig-19) |
| 8 | [LAB 6 cascade vs orphan](#fig-8) | 20 | [ภาพหน้าจอจริง บูธใหม่ออเดอร์ 0](#fig-20) |
| 9 | [LAB 7 quota, LimitRange, PSA](#fig-9) | 21 | [LAB 9 scale 3→5→2](#fig-21) |
| 10 | [LAB 8 กระจาย replica](#fig-10) | 22 | [LAB 9 template promo](#fig-22) |
| 11 | [LAB 9 สถาปัตยกรรมร้าน 3 บูธ](#fig-11) | 23 | [LAB 9 เปลี่ยนรุ่นทีละบูธด้วยมือ](#fig-23) |
| 12 | [LAB 9 เตรียม image](#fig-12) | 24 | [สรุป LAB 9 และปัญหาส่งต่อ](#fig-24) |

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ + screenshots/ ภาพหน้าจอจริงของร้าน 3 บูธ
├── labs/
│   ├── lab00-lonely/lonely-pod.yaml                 ← Pod เดี่ยว (ทบทวน)
│   ├── lab01-first-rs/00-ns.yaml                    ← namespace rs-lab (LAB 0–6)
│   ├── lab01-first-rs/snack-rs.yaml                 ← ReplicaSet ตัวแรก (ใช้ซ้ำใน LAB 1–6)
│   ├── lab01-first-rs/snack-rs-bad-labels.yaml      ← label ของ template ไม่ตรง selector
│   ├── lab01-first-rs/snack-rs-expr.yaml            ← selector แบบ matchExpressions
│   ├── lab02-self-heal/snack-rs-fast-evict.yaml     ← snack-rs + toleration 30 วินาที (ทางเลือก)
│   ├── lab04-label-trap/stray-pod.yaml              ← Pod หลงที่ป้าย app=snack
│   ├── lab04-label-trap/snack-rs-b.yaml             ← RS ตัวที่สอง selector ทับกัน
│   ├── lab05-template/web-rs.yaml                   ← nginx 1.27 / v1
│   ├── lab05-template/web-rs-v2.yaml                ← nginx 1.28 / v2
│   ├── lab05-template/web-rs-new-selector.yaml      ← ลองแก้ selector
│   ├── lab07-quota/00-ns-quota.yaml                 ← namespace rs-quota + ResourceQuota + LimitRange
│   ├── lab07-quota/quota-rs.yaml                    ← replicas 6 เกินงบ
│   ├── lab07-quota/psa-rs.yaml                      ← namespace rs-psa (enforce restricted) + RS (ทางเลือก)
│   ├── lab08-spread/00-ns.yaml                      ← namespace rs-spread
│   ├── lab08-spread/spread-required.yaml            ← required anti-affinity
│   ├── lab08-spread/spread-preferred.yaml           ← preferred anti-affinity
│   └── lab08-spread/spread-topology.yaml            ← topologySpreadConstraints
└── som-booths/                        ← LAB 9 ร้านน้องส้ม 3 บูธ
    ├── app/                           ← แอป Next.js + Dockerfile (สำเนาจากบทที่ 4: som-shop-web:1.1)
    └── k8s/
        ├── 00-namespace.yaml          ← namespace som-booths (warn=restricted)
        ├── som-booth.yaml             ← ReplicaSet som-booth replicas 3
        └── som-booth-promo.yaml       ← เหมือนกันทุกบรรทัด ยกเว้น image 1.1-promo + ข้อความโปร
```

---

## LAB 0: เตรียมคลัสเตอร์ + ทบทวน Pod เดี่ยวหายถาวร

<p align="center" id="fig-1">
  <img src="images/01-lab0-prepare.png" alt="รูปที่ 1 LAB 0 เตรียมคลัสเตอร์" width="900"><br>
  <em><b>รูปที่ 1</b> LAB0: เช็กเรือ 3 ลำ Ready, ลบ Pod เดี่ยวแล้วยืนยันว่าหายถาวร และส่องหา kube-controller-manager ใน kube-system</em>
</p>

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 4 หรือสร้างใหม่) ยืนยันว่าไม่มีของค้างจากบทก่อน ทบทวนว่า Pod เดี่ยวลบแล้วไม่มีใครสร้างใหม่ และส่องหา `kube-controller-manager` ที่ ReplicaSet controller อาศัยอยู่

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md), [2](../../002_kubernetes_pod/02_LAB/README.md), [3](../../003_kubernetes_node_pod/02_LAB/README.md) และ [4](../../004_kubernetes_namespace/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`) และมีโฟลเดอร์ `005_kubernetes_replicaset` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=^k8s-lab$
```

> `--filter name=k8s-lab` เฉย ๆ เป็นการค้นแบบ "มีคำนี้อยู่ในชื่อ" จึงแสดง container อื่นที่ชื่อขึ้นต้นด้วย `k8s-lab` ด้วย (เช่น `k8s-lab-xxxx`) ใส่ `^` และ `$` เพื่อให้ตรงชื่อ `k8s-lab` พอดี (ใน PowerShell ใส่เครื่องหมายคำพูดครอบได้ `"name=^k8s-lab$"`)

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `005_kubernetes_replicaset` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 005_kubernetes_replicaset k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลัง ต้องสั่ง `docker cp` ซ้ำ โฟลเดอร์นี้มีทั้ง YAML ของ LAB 0–8 (`02_LAB/labs/`) และแอปกับ manifest ของ LAB 9 (`02_LAB/som-booths/`) จึงคัดลอกครั้งเดียวพอ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` หน้าต่างนี้คือ **terminal 1** (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และเตรียมคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/005_kubernetes_replicaset/02_LAB
ls
kubectl get nodes
```

`ls` ต้องเห็น `README.md  images  labs  som-booths` จากนั้นเลือกทางตามผลของ `kubectl get nodes`

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node (`lab-control-plane`, `lab-worker`, `lab-worker2`) เป็น `Ready` (คลัสเตอร์จากบทที่ 4 ยังอยู่) | **ใช้ต่อได้เลย** ทำขั้นที่ 4 เพื่อตรวจของค้าง |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `time k8s-up` (ประมาณ 1 นาที ผลลัพธ์เหมือนบทที่ 4 LAB 0) |

ผลจริงจากคลัสเตอร์ที่เพิ่งสร้าง (สร้างด้วย `k8s-up` ก่อนเริ่ม LAB ราว 1 นาที AGE ในเครื่องนักศึกษาจะต่างไป)

```text
README.md
images
labs
som-booths
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   70s   v1.37.0
lab-worker          Ready    <none>          56s   v1.37.0
lab-worker2         Ready    <none>          56s   v1.37.0
```

(ในหน้าต่าง SSH `ls` จะแสดงชื่อเรียงในบรรทัดเดียว) ถ้าสั่ง `k8s-up` ทั้งที่คลัสเตอร์มีอยู่แล้ว จะไม่สร้างซ้ำ แต่แจ้ง `[k8s-up] cluster 'lab' มีอยู่แล้ว — ข้ามการสร้าง (ลบด้วย k8s-down)` แล้วแสดงตาราง Node (ในการทดลองใช้ 0.143 วินาที)

### ขั้นที่ 4: ตรวจว่าไม่มีของค้างจากบทก่อน

```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key,UNSCHED:.spec.unschedulable
kubectl get pods -A -o wide --field-selector spec.nodeName=lab-worker2
kubectl get ns
```

```text
NAME                TAINTS                                  UNSCHED
lab-control-plane   node-role.kubernetes.io/control-plane   <none>
lab-worker          <none>                                  <none>
lab-worker2         <none>                                  <none>
NAMESPACE     NAME               READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
kube-system   kindnet-888zx      1/1     Running   0          56s   172.19.0.3   lab-worker2   <none>           <none>
kube-system   kube-proxy-2jqvp   1/1     Running   0          56s   172.19.0.3   lab-worker2   <none>           <none>
NAME                 STATUS   AGE
default              Active   71s
kube-node-lease      Active   71s
kube-public          Active   71s
kube-system          Active   71s
local-path-storage   Active   67s
```

(IP ของ Node เช่น `172.19.0.3` เป็น IP ในเครือข่าย docker ของ kind อาจต่างในเครื่องนักศึกษา)

ผลที่ถูกต้อง: worker ทั้งสองลำ **ไม่มี taint และไม่ถูก cordon** (UNSCHED เป็น `<none>`), บน `lab-worker2` มีแค่ Pod ระบบ (`kindnet`, `kube-proxy`) และมี namespace ตั้งต้น 5 ตัว ถ้ายังมี taint/cordon จากบทที่ 3 ให้ทำ "ตารางคืนสภาพคลัสเตอร์" ของบทที่ 3 ถ้ายังมี namespace จากบทที่ 4 (`som-dev`, `team-a` ฯลฯ) ให้ทำ [ตารางเก็บกวาดของบทที่ 4](../../004_kubernetes_namespace/02_LAB/README.md#ตารางเก็บกวาดและคืนสภาพ) ก่อน (LAB 2 ต้อง drain และหยุดเรือ `lab-worker2` จึงไม่ควรมี Pod เดี่ยวของบทก่อนอยู่บนเรือลำนั้น)

### ขั้นที่ 5: Pod เดี่ยวลบแล้วหายถาวร

สร้าง namespace `rs-lab` (ใช้ถึง LAB 6) และ Pod เดี่ยว `lonely` (busybox) แล้วลบทิ้ง

```bash
cat labs/lab00-lonely/lonely-pod.yaml
kubectl apply -f labs/lab01-first-rs/00-ns.yaml -f labs/lab00-lonely/lonely-pod.yaml
kubectl wait --for=condition=Ready pod/lonely -n rs-lab --timeout=120s; kubectl get pods -n rs-lab -o wide
kubectl delete pod lonely -n rs-lab
sleep 5; kubectl get pods -n rs-lab
```

```text
namespace/rs-lab created
pod/lonely created
pod/lonely condition met
NAME     READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
lonely   1/1     Running   0          6s    10.244.2.2   lab-worker2   <none>           <none>
pod "lonely" deleted from rs-lab namespace
No resources found in rs-lab namespace.
```

kubectl v1.37 แจ้งการลบแบบใหม่ว่า `pod "lonely" deleted from rs-lab namespace` และ 5 วินาทีต่อมา namespace ว่างเปล่า **ไม่มีใครสร้าง Pod ใหม่แทน** นี่คือปัญหาที่บทนี้จะแก้ (IP และ Node ที่ได้อาจต่างจากตัวอย่าง)

#### อธิบาย YAML: `labs/lab01-first-rs/00-ns.yaml` และ `labs/lab00-lonely/lonely-pod.yaml`

```yaml
# LAB 0–6: โซนฝึกของบทนี้ (ลบทิ้งตอนท้าย LAB 6)
apiVersion: v1
kind: Namespace   # โซนแยกของบทนี้
metadata:
  name: rs-lab   # LAB 0–6 ใช้ร่วมกัน ลบทีเดียวด้วย kubectl delete ns rs-lab
```

```yaml
# LAB 0: Pod เดี่ยว (ไม่มีใครดูแล) — ลบแล้วหายถาวร
apiVersion: v1
kind: Pod   # Pod เดี่ยว ไม่มี controller ดูแล → ลบแล้วไม่มีใครสร้างแทน
metadata:
  name: lonely
  namespace: rs-lab   # namespace ของ LAB 0–6 (สร้างจาก 00-ns.yaml)
  labels:
    app: lonely   # ป้ายไม่ชนกับ app=snack ของ snack-rs
spec:
  terminationGracePeriodSeconds: 1   # busybox ไม่รับ SIGTERM → ให้ปิดเร็ว
  containers:
    - name: app
      image: busybox:1.36   # image เล็ก มี sh/sleep
      command: ["sh", "-c", "echo บูธเดี่ยวเปิดแล้ว; sleep 3600"]   # พิมพ์ข้อความแล้วนอน 1 ชม. ให้ Running ค้างไว้
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `kind: Namespace`, `name: rs-lab` | สร้างโซนแยกให้ LAB 0–6 ใช้ร่วมกัน ลบทั้งโซนทีเดียวได้ตอนจบ LAB 6 | `namespace/rs-lab created` |
| `kind: Pod` (ไม่มี ReplicaSet ครอบ) | Pod เดี่ยวไม่มี `ownerReferences` ไม่มี controller คอยนับ | ลบแล้วได้ `No resources found` ไม่มีตัวแทน |
| `name: lonely` | ชื่อตายตัวที่เราตั้งเอง ต่างจาก Pod ของ RS ที่ได้ชื่อสุ่ม | ใช้ `pod/lonely` ใน `kubectl wait` ได้ตรง ๆ |
| `labels: app: lonely` | ป้ายที่ไม่ชนกับ `app=snack` ของ LAB 1 จึงไม่ถูก RS ใดนับรวม | – |
| `terminationGracePeriodSeconds: 1` | `sh` ที่เป็น PID 1 ไม่ตอบ SIGTERM ถ้าใช้ค่าเริ่มต้น 30 วินาที การลบจะค้างนาน | `kubectl delete pod lonely` จบเร็ว |
| `image: busybox:1.36` + `command` | image เล็กที่มี `sh`/`sleep` พิมพ์ข้อความแล้วนอน 1 ชั่วโมงให้ Pod `Running` ค้างไว้ | `lonely 1/1 Running` |

### ขั้นที่ 6: ส่องหา kube-controller-manager

```bash
kubectl get pods -n kube-system -l component=kube-controller-manager -o wide
kubectl -n kube-system get pod kube-controller-manager-lab-control-plane -o jsonpath='{.spec.containers[0].command}' | grep -o -- '--controllers=[^"]*'
kubectl -n kube-system get pod kube-controller-manager-lab-control-plane -o jsonpath='{.metadata.ownerReferences}{"\n"}'
```

```text
NAME                                        READY   STATUS    RESTARTS   AGE   IP           NODE                NOMINATED NODE   READINESS GATES
kube-controller-manager-lab-control-plane   1/1     Running   0          86s   172.19.0.4   lab-control-plane   <none>           <none>
--controllers=*,bootstrapsigner,tokencleaner
[{"apiVersion":"v1","controller":true,"kind":"Node","name":"lab-control-plane","uid":"8cabc248-2167-4c29-95ac-483b2dcfdabb"}]
```

(`uid` และ IP ในเครื่องนักศึกษาจะต่างจากตัวอย่าง)

> **ทำไมใช้ `grep -o`:** `command` เป็น JSON array ถ้าใช้ `tr ',' '\n' | grep controllers` ค่าจะถูกตัดที่ comma เหลือแค่ `"--controllers=*` (ทดลองแล้ว) คำสั่งข้างบนดึงทั้งค่า หรือจะใช้ `-o jsonpath='{range .spec.containers[0].command[*]}{@}{"\n"}{end}' | grep controllers` ก็ได้ผลเดียวกัน

### สิ่งที่เห็น

- คลัสเตอร์พร้อม 3 Node ไม่มี taint/cordon ค้างบน worker
- Pod เดี่ยวที่ถูกลบหายถาวร ไม่มีอะไรเกิดแทน
- `kube-controller-manager` เป็น static Pod บน `lab-control-plane` เปิด controller มาตรฐานทั้งหมด (`*`) ซึ่งรวม ReplicaSet controller และเจ้าของของมันคือ `kind: Node` (mirror pod ที่ kubelet ดูแล ไม่ใช่ controller)

> **🤔 คำถามชวนคิด:** ถ้าลบ Pod `kube-controller-manager-lab-control-plane` ทิ้ง Pod นี้จะกลับมาไหม ใครเป็นผู้สร้างกลับ (ทบทวน static Pod บทที่ 3) — ไม่ต้องลองจริง

**เก็บกวาด:** เก็บ namespace `rs-lab` ไว้ใช้ต่อใน LAB 1

---

## LAB 1: ReplicaSet แรก

<p align="center" id="fig-2">
  <img src="images/02-lab1-first-rs.png" alt="รูปที่ 2 LAB 1 ReplicaSet แรก" width="900"><br>
  <em><b>รูปที่ 2</b> LAB1: สร้าง snack-rs 3 ตัว ดูชื่อ Pod แบบ &lt;rs&gt;-&lt;สุ่ม&gt;, ownerReferences, Events SuccessfulCreate และลอง template ที่ label ไม่ตรง selector</em>
</p>

**เป้าหมาย:** สร้าง ReplicaSet `snack-rs` 3 บูธ ดูชื่อ Pod, ownerReferences, Events และ status ทดลอง template ที่ label ไม่ตรง selector และ selector แบบ matchExpressions

**ไฟล์:** `labs/lab01-first-rs/snack-rs.yaml` (โครง 3 ส่วนอธิบายใน [ทฤษฎีหัวข้อ 3.1](../01_Theory/README.md#31-โครง-3-ส่วน))

```bash
cat labs/lab01-first-rs/snack-rs.yaml
```

#### อธิบาย YAML: `labs/lab01-first-rs/snack-rs.yaml`

```yaml
# LAB 1: ReplicaSet ตัวแรก — หัวหน้ากะดูแลบูธขนม 3 บูธ
apiVersion: apps/v1          # ReplicaSet อยู่ในกลุ่ม apps (Pod อยู่ใน v1)
kind: ReplicaSet   # หัวหน้ากะ: รักษาจำนวน Pod ให้ครบตามที่สั่ง
metadata:
  name: snack-rs   # ชื่อ RS = คำนำหน้าชื่อ Pod (snack-rs-xxxxx)
  namespace: rs-lab   # Pod ที่ปั๊มออกมาอยู่ namespace เดียวกับ RS
  labels:
    app: snack   # ป้ายของตัว RS เอง (ไม่ใช้ในการนับ)
spec:
  replicas: 3                # จำนวนบูธที่ต้องมีตลอดเวลา
  selector:                  # หัวหน้ากะนับเฉพาะ Pod ที่มีป้ายตรงนี้
    matchLabels:
      app: snack   # นับทุก Pod ที่มีป้ายนี้ ไม่สนว่าใครสร้าง
  template:                  # แบบพิมพ์สำหรับปั๊ม Pod ใหม่ (ไม่มี name → ระบบตั้งชื่อ snack-rs-xxxxx)
    metadata:
      labels:
        app: snack           # ต้องตรงกับ selector ไม่งั้นสร้าง RS ไม่ได้
    spec:
      terminationGracePeriodSeconds: 1   # busybox ไม่รับ SIGTERM → ถูก kill หลัง 1 วิ (เห็น Error ชั่วครู่)
      containers:
        - name: app
          image: busybox:1.36   # ทุก Pod ใช้ image เดียวกันจาก template
          command: ["sh", "-c", "echo บูธขนม $(hostname) เปิดแล้ว; sleep 3600"]   # $(hostname) = ชื่อ Pod
          resources:
            requests: { cpu: 10m, memory: 16Mi }   # ขั้นต่ำที่จองไว้ (ใช้ตอน scheduler จัดวาง)
            limits:   { cpu: 50m, memory: 32Mi }   # เพดานที่ใช้ได้จริง
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `apiVersion: apps/v1`, `kind: ReplicaSet` | ReplicaSet อยู่ในกลุ่ม API `apps` (ต่างจาก Pod ที่เป็น `v1`) | `replicaset.apps/snack-rs created` |
| `metadata.name: snack-rs` | ชื่อ RS ถูกใช้เป็นคำนำหน้าชื่อ Pod + อักษรสุ่ม 5 ตัว | Pod ชื่อ `snack-rs-2xn5v` ฯลฯ |
| `metadata.labels` | ป้ายของ **ตัว RS** ใช้ค้นหา RS ไม่เกี่ยวกับการนับ Pod | คอลัมน์ LABELS ของ `get rs -o wide --show-labels` |
| `spec.replicas: 3` | จำนวน Pod ที่ต้องมีตลอดเวลา บรรทัดนี้มีคอมเมนต์ต่อท้าย ซึ่ง `sed` ใน LAB 3 อาศัยช่องว่างหลังตัวเลข | DESIRED `3` |
| `spec.selector.matchLabels: app: snack` | กติกาการนับ: RS นับ **ทุก** Pod ใน namespace ที่มีป้ายนี้ ไม่ดูว่าใครสร้าง | ที่มาของกับดักใน LAB 4 |
| `spec.template` (ไม่มี `name`) | แบบพิมพ์ Pod ที่ไม่ใส่ชื่อ เพราะ RS ต้องปั๊มหลายตัว ชื่อจึงถูกสุ่ม | – |
| `template.metadata.labels: app: snack` | ป้ายที่ Pod ใหม่ทุกตัวได้ ต้องผ่าน selector มิฉะนั้น API server ปฏิเสธ | ขั้นที่ 4 (`snak`) ถูกปฏิเสธ |
| `terminationGracePeriodSeconds: 1` | `sh` ไม่ตอบ SIGTERM จึงให้ kill หลัง 1 วินาที | Pod ที่ถูกลบขึ้น `Error` ชั่วครู่ก่อนหาย (LAB 2–4) |
| `command` ที่มี `$(hostname)` | `$(hostname)` ถูก `sh` ขยายเป็นชื่อ Pod log จึงบอกว่าเป็นบูธไหน | `บูธขนม snack-rs-2xn5v เปิดแล้ว` |
| `resources.requests` / `limits` | requests ใช้ตอน scheduler หา Node ที่มีที่ว่าง limits คือเพดานจริง | `describe rs` แสดง `Limits`/`Requests` ใน Pod Template |

### ขั้นที่ 1: สร้าง ReplicaSet

```bash
kubectl apply -f labs/lab01-first-rs/snack-rs.yaml
kubectl get rs -n rs-lab; kubectl get pods -n rs-lab -o wide --show-labels
sleep 4; kubectl get rs,pods -n rs-lab -o wide --show-labels
```

```text
replicaset.apps/snack-rs created
NAME       DESIRED   CURRENT   READY   AGE
snack-rs   3         3         0       0s
NAME             READY   STATUS              RESTARTS   AGE   IP       NODE          NOMINATED NODE   READINESS GATES   LABELS
snack-rs-2xn5v   0/1     ContainerCreating   0          0s    <none>   lab-worker2   <none>           <none>            app=snack
snack-rs-4snct   0/1     ContainerCreating   0          0s    <none>   lab-worker2   <none>           <none>            app=snack
snack-rs-tf8d5   0/1     ContainerCreating   0          0s    <none>   lab-worker    <none>           <none>            app=snack
NAME                       DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR    LABELS
replicaset.apps/snack-rs   3         3         2       4s    app          busybox:1.36   app=snack   app=snack

NAME                 READY   STATUS              RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES   LABELS
pod/snack-rs-2xn5v   1/1     Running             0          4s    10.244.2.4   lab-worker2   <none>           <none>            app=snack
pod/snack-rs-4snct   1/1     Running             0          4s    10.244.2.3   lab-worker2   <none>           <none>            app=snack
pod/snack-rs-tf8d5   0/1     ContainerCreating   0          4s    <none>       lab-worker    <none>           <none>            app=snack
```

คำสั่งเดียวได้ Pod 3 ตัว ชื่อ `snack-rs-` + อักษรสุ่ม 5 ตัว ทุกตัวมีป้าย `app=snack` จาก template ช่วงแรก READY เป็น 0 และ 2 เพราะ Node ต้องดึง `busybox:1.36` ก่อน (ในการทดลอง `lab-worker` ช้ากว่าเล็กน้อย Node ไหนได้กี่ตัวในเครื่องนักศึกษาอาจต่าง) รอสักครู่จะเป็น `3 3 3`

### ขั้นที่ 2: ป้ายเจ้าของ, log และ Events

```bash
kubectl wait --for=condition=Ready pod -l app=snack -n rs-lab --timeout=120s
P=$(kubectl get pods -n rs-lab -l app=snack -o jsonpath='{.items[0].metadata.name}'); echo $P
kubectl get pod $P -n rs-lab -o jsonpath='{.metadata.ownerReferences}{"\n"}'
kubectl logs -n rs-lab $P
kubectl describe rs snack-rs -n rs-lab
```

```text
pod/snack-rs-2xn5v condition met
pod/snack-rs-4snct condition met
pod/snack-rs-tf8d5 condition met
snack-rs-2xn5v
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"ReplicaSet","name":"snack-rs","uid":"326d7872-c4da-4d72-9caa-f0065f8adb08"}]
บูธขนม snack-rs-2xn5v เปิดแล้ว
Name:         snack-rs
Namespace:    rs-lab
Selector:     app=snack
Labels:       app=snack
Annotations:  <none>
Replicas:     3 current / 3 desired
Pods Status:  3 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=snack
  Containers:
   app:
    Image:      busybox:1.36
    Port:       <none>
    Host Port:  <none>
    Command:
      sh
      -c
      echo บูธขนม $(hostname) เปิดแล้ว; sleep 3600
    Limits:
      cpu:     50m
      memory:  32Mi
    Requests:
      cpu:         10m
      memory:      16Mi
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Events:
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  4s    replicaset-controller  Created pod: snack-rs-4snct
  Normal  SuccessfulCreate  4s    replicaset-controller  Created pod: snack-rs-tf8d5
  Normal  SuccessfulCreate  4s    replicaset-controller  Created pod: snack-rs-2xn5v
```

- `kubectl wait` รอให้บูธทั้ง 3 ตัว Ready ก่อน (ถ้าสั่ง `kubectl logs` ทันทีหลังขั้นที่ 1 ขณะ Pod ยัง `ContainerCreating` จะได้ `Error from server (BadRequest): container "app" in pod "..." is waiting to start: ContainerCreating`)
- `ownerReferences` บอกว่าเจ้าของคือ `ReplicaSet/snack-rs` (`controller: true`, `blockOwnerDeletion: true`) พร้อม `uid` ของ RS ตัวนี้
- log ของแต่ละบูธพิมพ์ชื่อของตัวเอง (`$(hostname)` = ชื่อ Pod)
- Events มี `SuccessfulCreate` 3 บรรทัด ระบุชื่อ Pod ที่สร้าง

### ขั้นที่ 3: อ่าน status

```bash
kubectl get rs snack-rs -n rs-lab -o jsonpath='{.status}{"\n"}'
```

```text
{"availableReplicas":2,"fullyLabeledReplicas":3,"observedGeneration":1,"readyReplicas":2,"replicas":3,"terminatingReplicas":0}
```

ตอนอ่านค่านี้มี Pod Ready 2 ตัว จึงได้ `readyReplicas: 2` และ `availableReplicas: 2` ส่วน `replicas: 3` และ `fullyLabeledReplicas: 3` (Pod ที่มี label ครบตาม template) ฟิลด์ `terminatingReplicas` (จำนวน Pod ที่กำลังถูกลบ) มีใน Kubernetes v1.37 ความหมายของแต่ละฟิลด์ดู [ทฤษฎีหัวข้อ 3.6](../01_Theory/README.md#36-อ่านสถานะของ-replicaset)

### ขั้นที่ 4: template ที่ label ไม่ตรง selector

ไฟล์ `snack-rs-bad-labels.yaml` จงใจพิมพ์ `app: snak` ใน template ขณะที่ selector เป็น `app: snack`

```bash
grep -n -A1 "matchLabels\|labels:" labs/lab01-first-rs/snack-rs-bad-labels.yaml
kubectl apply -f labs/lab01-first-rs/snack-rs-bad-labels.yaml; echo "exit=$?"
```

```text
10:    matchLabels:
11-      app: snack
--
14:      labels:
15-        app: snak            # ← พิมพ์ผิด ไม่ตรงกับ selector
The ReplicaSet "snack-rs-bad" is invalid: spec.template.metadata.labels: Invalid value: {"app":"snak"}: `selector` does not match template `labels`
exit=1
```

API server ปฏิเสธตั้งแต่ต้น ไม่มี RS `snack-rs-bad` เกิดขึ้น (ถ้ายอมให้สร้าง RS จะปั๊ม Pod ที่ตัวเองนับไม่เห็นไปเรื่อย ๆ)

#### อธิบาย YAML: `labs/lab01-first-rs/snack-rs-bad-labels.yaml`

```yaml
# LAB 1: ตั้งใจพิมพ์ป้ายผิด (snak) → label ของ template ไม่ตรง selector → API server ปฏิเสธ
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs-bad   # RS นี้จะไม่ถูกสร้างเลย
  namespace: rs-lab
spec:
  replicas: 3   # ไม่มีผล เพราะถูกปฏิเสธตั้งแต่ apply
  selector:
    matchLabels:
      app: snack
  template:   # ป้ายในแบบพิมพ์ไม่ผ่าน selector → API server ปฏิเสธทั้งก้อน
    metadata:
      labels:
        app: snak            # ← พิมพ์ผิด ไม่ตรงกับ selector
    spec:
      terminationGracePeriodSeconds: 1
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
```

- `selector.matchLabels: app: snack` กับ `template.metadata.labels: app: snak` ต่างกันแค่ตัวอักษรเดียว แต่ API server ตรวจตอนรับ object ว่า "ป้ายของแบบพิมพ์ต้องผ่าน selector" จึงได้ `` `selector` does not match template `labels` `` และ `exit=1`
- บรรทัด 10, 11, 14, 15 คือบรรทัดที่ `grep -n -A1` แสดง (คอมเมนต์ในไฟล์ตั้งใจไม่ใช้คำว่า `labels:` เพื่อไม่ให้ grep จับบรรทัดอื่นเพิ่ม)
- `replicas`, `command` ไม่มีผลใด ๆ เพราะ RS ไม่ถูกบันทึกเลย

### ขั้นที่ 5: selector แบบ matchExpressions

```bash
cat labs/lab01-first-rs/snack-rs-expr.yaml
kubectl apply -f labs/lab01-first-rs/snack-rs-expr.yaml; sleep 4
kubectl get pods -n rs-lab -l "tier in (snack,drink)" --show-labels
kubectl get rs -n rs-lab
kubectl get rs snack-rs-expr -n rs-lab -o wide
```

```text
replicaset.apps/snack-rs-expr created
NAME                  READY   STATUS    RESTARTS   AGE   LABELS
snack-rs-expr-dkw9w   1/1     Running   0          4s    tier=drink
snack-rs-expr-rcl5g   1/1     Running   0          4s    tier=drink
NAME            DESIRED   CURRENT   READY   AGE
snack-rs        3         3         3       8s
snack-rs-expr   2         2         2       4s
NAME            DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR
snack-rs-expr   2         2         2       5s    app          busybox:1.36   tier in (drink,snack),!track
```

selector `tier In (snack, drink)` + `track DoesNotExist` แสดงในรูป `tier in (drink,snack),!track` และ RS สองตัวอยู่ใน namespace เดียวกันได้โดยไม่ยุ่งกัน เพราะ selector ไม่ทับกัน (`app=snack` กับ `tier in (...)`)

#### อธิบาย YAML: `labs/lab01-first-rs/snack-rs-expr.yaml`

```yaml
# LAB 1: selector แบบ matchExpressions — นับ Pod ที่ tier เป็น snack หรือ drink และต้องไม่มีป้าย track
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs-expr
  namespace: rs-lab
spec:
  replicas: 2   # ขอ 2 Pod
  selector:   # ทุกเงื่อนไขต้องผ่านพร้อมกัน (AND)
    matchExpressions:
      - { key: tier, operator: In, values: [snack, drink] }   # tier ต้องเป็น snack หรือ drink
      - { key: track, operator: DoesNotExist }   # ต้องไม่มีป้าย key track เลย
  template:
    metadata:
      labels:
        tier: drink          # อยู่ในรายการ In → ผ่าน และไม่มีป้าย track → ผ่าน
    spec:
      terminationGracePeriodSeconds: 1
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]   # แค่นอน ไม่พิมพ์ log
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 50m, memory: 32Mi }
```

- `matchExpressions` เขียนเงื่อนไขได้ยืดหยุ่นกว่า `matchLabels` ทุกข้อในรายการต้องผ่านพร้อมกัน kubectl แสดงรวมเป็น `tier in (drink,snack),!track` (`!track` = DoesNotExist)
- `operator: In` + `values: [snack, drink]` → ป้าย `tier` ต้องเป็นค่าใดค่าหนึ่งในรายการ
- `operator: DoesNotExist` → Pod ต้องไม่มีป้าย key `track` (ไม่สนค่า)
- template ใส่แค่ `tier: drink` จึงผ่านทั้งสองข้อ ได้ Pod 2 ตัวที่ LABELS เป็น `tier=drink` ตาม `replicas: 2`
- ไม่มีป้าย `app` เลย จึงไม่ถูก `snack-rs` (selector `app=snack`) นับรวม และ snack-rs-expr ก็ไม่นับ Pod ของ snack-rs เพราะไม่มีป้าย `tier`

ลบ RS ตัวนี้ทิ้ง

```bash
kubectl delete -f labs/lab01-first-rs/snack-rs-expr.yaml; kubectl get rs,pods -n rs-lab -o wide
```

```text
replicaset.apps "snack-rs-expr" deleted from rs-lab namespace
NAME                       DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR
replicaset.apps/snack-rs   3         3         3       9s    app          busybox:1.36   app=snack

NAME                      READY   STATUS        RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
pod/snack-rs-2xn5v        1/1     Running       0          9s    10.244.2.4   lab-worker2   <none>           <none>
pod/snack-rs-4snct        1/1     Running       0          9s    10.244.2.3   lab-worker2   <none>           <none>
pod/snack-rs-expr-dkw9w   1/1     Terminating   0          5s    10.244.2.5   lab-worker2   <none>           <none>
pod/snack-rs-expr-rcl5g   1/1     Terminating   0          5s    10.244.1.3   lab-worker    <none>           <none>
pod/snack-rs-tf8d5        1/1     Running       0          9s    10.244.1.2   lab-worker    <none>           <none>
```

ลบ RS แล้ว Pod ของมันถูกลบตามอัตโนมัติ (garbage collector ตาม ownerReferences — ดู LAB 6)

### สิ่งที่เห็น

- ReplicaSet `snack-rs` ได้ `3 3 3` ชื่อ Pod `snack-rs-xxxxx` ทุกตัวมี ownerReferences ชี้ไปที่ RS
- Events บอกชื่อ Pod ที่สร้าง และ status มี `replicas`, `readyReplicas`, `availableReplicas`, `fullyLabeledReplicas`, `terminatingReplicas`
- label ของ template ที่ไม่ตรง selector ถูกปฏิเสธด้วย `` `selector` does not match template `labels` ``
- selector แบบ `matchExpressions` ใช้ In/DoesNotExist ได้ และลบ RS แล้ว Pod หายตาม

> **🤔 คำถามชวนคิด:** ถ้าเพิ่ม label `version: v1` ใน template ของ snack-rs แต่ไม่เพิ่มใน selector จะสร้างได้ไหม และ `fullyLabeledReplicas` ใช้นับอะไร

**เก็บกวาด:** เก็บ `snack-rs` ไว้ใช้ต่อใน LAB 2

---

## LAB 2: Self-healing: ลบ Pod, drain และเรือล่ม

<p align="center" id="fig-3">
  <img src="images/03-lab2-delete-watch.png" alt="รูปที่ 3 LAB 2 ลบ Pod แล้วดูด้วย -w" width="900"><br>
  <em><b>รูปที่ 3</b> LAB2: ลบ Pod (ทั้งทีละตัวและ -l app=snack) ขณะเปิด kubectl get pods -w อีกหน้าต่าง เห็นตัวใหม่เกิดขณะตัวเก่ายัง Terminating</em>
</p>

**เป้าหมาย:** เห็นด้วยตาว่า ReplicaSet สร้าง Pod แทนเมื่อ Pod ถูกลบ (ทีละตัวและพร้อมกัน) เมื่อ drain เรือ และ (ทางเลือก) เมื่อเรือล่ม พร้อมวัดเวลา

**ต้องมีจาก LAB 1:** `snack-rs` ใน `rs-lab` (`3 3 3`)

### ขั้นที่ 1: เปิดหน้าต่างเฝ้าดู

🐧 **terminal 2** (SSH session ที่สอง) เปิดค้างไว้ตลอด LAB นี้

```bash
kubectl get pods -n rs-lab -o wide -w
```

### ขั้นที่ 2: ลบ Pod หนึ่งตัว

🐧 **terminal 1**

```bash
P=$(kubectl get pods -n rs-lab -l app=snack -o jsonpath="{.items[0].metadata.name}")
date +%T; kubectl delete pod $P -n rs-lab --wait=false; kubectl get pods -n rs-lab -o wide
sleep 3; kubectl get pods -n rs-lab -o wide
kubectl describe rs snack-rs -n rs-lab | tail -6
```

```text
17:10:47
pod "snack-rs-2xn5v" deleted from rs-lab namespace
NAME             READY   STATUS              RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
snack-rs-2xn5v   1/1     Terminating         0          29s   10.244.2.4   lab-worker2   <none>           <none>
snack-rs-4snct   1/1     Running             0          29s   10.244.2.3   lab-worker2   <none>           <none>
snack-rs-tf8d5   1/1     Running             0          29s   10.244.1.2   lab-worker    <none>           <none>
snack-rs-zj8vw   0/1     ContainerCreating   0          0s    <none>       lab-worker2   <none>           <none>
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
snack-rs-4snct   1/1     Running   0          32s   10.244.2.3   lab-worker2   <none>           <none>
snack-rs-tf8d5   1/1     Running   0          32s   10.244.1.2   lab-worker    <none>           <none>
snack-rs-zj8vw   1/1     Running   0          3s    10.244.2.6   lab-worker2   <none>           <none>
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  32s   replicaset-controller  Created pod: snack-rs-4snct
  Normal  SuccessfulCreate  32s   replicaset-controller  Created pod: snack-rs-tf8d5
  Normal  SuccessfulCreate  32s   replicaset-controller  Created pod: snack-rs-2xn5v
  Normal  SuccessfulCreate  3s    replicaset-controller  Created pod: snack-rs-zj8vw
```

(`date +%T` แสดงเวลาตาม timezone ของ k8s-lab ในเครื่องนักศึกษาจะเป็นเวลาที่ทำจริง) terminal 2 เห็นลำดับเหตุการณ์ละเอียดกว่า (ตัดคอลัมน์ท้ายและบรรทัดซ้ำ)

```text
snack-rs-2xn5v   1/1     Terminating   0          29s   10.244.2.4   lab-worker2
snack-rs-zj8vw   0/1     Pending       0          0s    <none>       <none>
snack-rs-zj8vw   0/1     Pending       0          0s    <none>       lab-worker2
snack-rs-zj8vw   0/1     ContainerCreating   0          0s    <none>       lab-worker2
snack-rs-zj8vw   1/1     Running             0          1s    10.244.2.6   lab-worker2
snack-rs-2xn5v   0/1     Error               0          31s   10.244.2.4   lab-worker2
```

`--wait=false` ทำให้ kubectl ไม่รอ Pod หายจริงก่อนพิมพ์ผลต่อ เราจึงเห็นว่า **ตัวใหม่ `zj8vw` เกิดทันทีขณะที่ตัวเก่ายัง Terminating** และ Running ภายในราว 1–2 วินาที ส่วนตัวเก่าขึ้น `Error` ก่อนหาย (busybox ถูก kill หลัง grace period 1 วินาที)

### ขั้นที่ 3: ลบทุกตัวพร้อมกัน

```bash
date +%T; kubectl delete pod -n rs-lab -l app=snack --wait=false; kubectl get pods -n rs-lab
sleep 4; kubectl get rs,pods -n rs-lab -o wide
```

```text
17:10:50
pod "snack-rs-4snct" deleted from rs-lab namespace
pod "snack-rs-tf8d5" deleted from rs-lab namespace
pod "snack-rs-zj8vw" deleted from rs-lab namespace
NAME             READY   STATUS              RESTARTS   AGE
snack-rs-4snct   1/1     Terminating         0          32s
snack-rs-9x54q   0/1     ContainerCreating   0          0s
snack-rs-bg4qr   0/1     ContainerCreating   0          0s
snack-rs-tf8d5   1/1     Terminating         0          32s
snack-rs-x4fwm   0/1     Pending             0          0s
snack-rs-zj8vw   1/1     Terminating         0          3s
NAME                       DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR
replicaset.apps/snack-rs   3         3         3       36s   app          busybox:1.36   app=snack

NAME                 READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
pod/snack-rs-9x54q   1/1     Running   0          4s    10.244.2.7   lab-worker2   <none>           <none>
pod/snack-rs-bg4qr   1/1     Running   0          4s    10.244.1.4   lab-worker    <none>           <none>
pod/snack-rs-x4fwm   1/1     Running   0          4s    10.244.2.8   lab-worker2   <none>           <none>
```

ลบทั้งร้านพร้อมกัน ร้านก็กลับมาครบ 3 บูธภายในไม่กี่วินาที (ตัวใหม่บางตัวอาจยังเป็น `Pending` อยู่ในจังหวะแรก เพราะ scheduler ยังไม่ได้วาง) แต่ **ทุกบูธเป็นบูธใหม่** (ชื่อใหม่ IP ใหม่) ช่วงเวลาสั้น ๆ นั้นร้านไม่มีบูธที่พร้อมให้บริการเลย

### ขั้นที่ 4: drain เรือ lab-worker2

<p align="center" id="fig-4">
  <img src="images/04-lab2-drain-rebirth.png" alt="รูปที่ 4 LAB 2 drain และเรือล่ม" width="900"><br>
  <em><b>รูปที่ 4</b> LAB2 (ต่อ): drain lab-worker2 → Pod ของ snack-rs บนเรือนั้นถูกไล่และเกิดใหม่บน lab-worker แล้ว uncordon (Pod ไม่ย้ายกลับเอง) — ทางเลือก: docker stop lab-worker2 + tolerationSeconds 30</em>
</p>

ในบทที่ 3 drain เรือที่มี Pod เดี่ยวต้องใช้ `--force` ครั้งนี้ไม่ต้อง

```bash
kubectl get pods -n rs-lab -o wide
time kubectl drain lab-worker2 --ignore-daemonsets
kubectl get nodes; kubectl get pods -n rs-lab -o wide
```

```text
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
snack-rs-9x54q   1/1     Running   0          4s    10.244.2.7   lab-worker2   <none>           <none>
snack-rs-bg4qr   1/1     Running   0          4s    10.244.1.4   lab-worker    <none>           <none>
snack-rs-x4fwm   1/1     Running   0          4s    10.244.2.8   lab-worker2   <none>           <none>
node/lab-worker2 cordoned
Warning: ignoring DaemonSet-managed Pods: kube-system/kindnet-888zx, kube-system/kube-proxy-2jqvp
evicting pod rs-lab/snack-rs-x4fwm
evicting pod rs-lab/snack-rs-9x54q
pod/snack-rs-x4fwm evicted
pod/snack-rs-9x54q evicted
node/lab-worker2 drained

real	0m3.093s
user	0m0.041s
sys	0m0.025s
NAME                STATUS                     ROLES           AGE    VERSION
lab-control-plane   Ready                      control-plane   2m5s   v1.37.0
lab-worker          Ready                      <none>          111s   v1.37.0
lab-worker2         Ready,SchedulingDisabled   <none>          111s   v1.37.0
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
snack-rs-bg4qr   1/1     Running   0          7s    10.244.1.4   lab-worker   <none>           <none>
snack-rs-dqf8j   1/1     Running   0          3s    10.244.1.5   lab-worker   <none>           <none>
snack-rs-tcnjj   1/1     Running   0          3s    10.244.1.6   lab-worker   <none>           <none>
```

drain จบใน 3 วินาที Pod 2 ตัวบน `lab-worker2` ถูก evict แล้ว RS สร้างตัวแทนบน `lab-worker` ร้านยังครบ 3 บูธ (ถ้าในเครื่องนักศึกษาไม่มี Pod ของ snack-rs อยู่บน `lab-worker2` เลย drain จะไม่ evict อะไร ให้ uncordon แล้วลบ Pod ทั้งหมดให้ scheduler วางใหม่ก่อนลองอีกครั้ง)

คืนเรือแล้วดูว่า Pod ย้ายกลับไหม

```bash
kubectl uncordon lab-worker2; sleep 3; kubectl get pods -n rs-lab -o wide
```

```text
node/lab-worker2 uncordoned
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
snack-rs-bg4qr   1/1     Running   0          10s   10.244.1.4   lab-worker   <none>           <none>
snack-rs-dqf8j   1/1     Running   0          6s    10.244.1.5   lab-worker   <none>           <none>
snack-rs-tcnjj   1/1     Running   0          6s    10.244.1.6   lab-worker   <none>           <none>
```

**ไม่ย้ายกลับ** ทั้ง 3 บูธยังอยู่บน `lab-worker` เพราะ ReplicaSet นับแค่จำนวน และ scheduler ทำงานเฉพาะตอน Pod เกิดใหม่

### ขั้นที่ 5 (ทางเลือก): เรือล่มด้วย toleration 30 วินาที

ขั้นนี้ใช้เวลาราว 3–4 นาที แสดงสิ่งที่เกิดเมื่อเรือหายไปโดยไม่มีใครสั่ง ถ้าเวลาไม่พอให้ข้ามไปขั้นที่ 6 ได้ (อ่านผลจากเอกสาร)

ค่าเริ่มต้นต้องรอ 300 วินาทีหลังเรือเป็น NotReady จึงจะสร้างแทน เพื่อไม่ให้รอนาน ใช้ `snack-rs-fast-evict.yaml` ที่เพิ่ม toleration 30 วินาทีใน template **template ใหม่ไม่เปลี่ยน Pod เดิม** (จะเห็นชัดใน LAB 5) จึงต้องลบ Pod ให้เกิดใหม่จาก template ใหม่ และต้องมี Pod อยู่บน `lab-worker2` ก่อน stop (หลังขั้นที่ 4 ทุกตัวอยู่บน `lab-worker`)

```bash
diff labs/lab01-first-rs/snack-rs.yaml labs/lab02-self-heal/snack-rs-fast-evict.yaml
kubectl apply -f labs/lab02-self-heal/snack-rs-fast-evict.yaml
kubectl delete pod -n rs-lab -l app=snack; sleep 3; kubectl get pods -n rs-lab -o wide
kubectl get pods -n rs-lab -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.tolerations}{"\n"}{end}'
```

```text
replicaset.apps/snack-rs configured
pod "snack-rs-bg4qr" deleted from rs-lab namespace
pod "snack-rs-dqf8j" deleted from rs-lab namespace
pod "snack-rs-tcnjj" deleted from rs-lab namespace
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-8gn5s   1/1     Running   0          7s    10.244.1.7    lab-worker    <none>           <none>
snack-rs-j85td   1/1     Running   0          7s    10.244.2.9    lab-worker2   <none>           <none>
snack-rs-m55bt   1/1     Running   0          7s    10.244.2.10   lab-worker2   <none>           <none>
snack-rs-8gn5s  [{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":30},{"effect":"NoExecute","key":"node.kubernetes.io/unreachable","operator":"Exists","tolerationSeconds":30}]
...
```

(ปกติระบบเติม toleration 300 วินาทีของ 2 key นี้ให้ทุก Pod อัตโนมัติ แต่เมื่อ template ระบุ key เดียวกันเองแล้ว ระบบจะไม่เติมซ้ำ จึงเห็นเฉพาะค่า 30 วินาที) ต้องเห็นอย่างน้อย 1 ตัวอยู่บน `lab-worker2` ถ้าไม่มี ให้ลบ Pod อีกรอบ (Pod ไหนไปอยู่เรือไหนขึ้นกับ scheduler ในเครื่องนักศึกษาอาจต่าง)

#### อธิบาย YAML: `labs/lab02-self-heal/snack-rs-fast-evict.yaml`

ไฟล์นี้คือ `snack-rs.yaml` เดิมทุก field (ชื่อ, selector, template, resources เหมือนกัน — อธิบายไว้ใน LAB 1) ต่างกันที่ **เพิ่ม `tolerations`** ใน template (ส่วนอื่นของ `diff` เป็นแค่คอมเมนต์ที่ต่างกัน)

```yaml
# LAB 2 (ทางเลือก): snack-rs เดิม + toleration 30 วิ → ถูกไล่ออกจากเรือที่ล่มเร็วขึ้น (ค่าเริ่มต้น 300 วิ, บท 003)
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs   # ชื่อเดิม → apply แล้วเป็นการแก้ template ของ snack-rs ตัวเดิม
...
    spec:
      terminationGracePeriodSeconds: 1
      tolerations:                     # ทนเรือ NotReady/ติดต่อไม่ได้แค่ 30 วิ
        - key: node.kubernetes.io/not-ready   # taint ที่ระบบใส่ให้เรือที่ NotReady
          operator: Exists   # ไม่สน value ของ taint
          effect: NoExecute   # taint ชนิดไล่ Pod ที่รันอยู่ออก
          tolerationSeconds: 30   # ทนได้ 30 วิ แล้วถูกไล่ (ค่าเริ่มต้นที่ระบบเติม = 300)
        - key: node.kubernetes.io/unreachable   # taint เมื่อ control-plane ติดต่อเรือไม่ได้
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
...
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `metadata.name: snack-rs` (ชื่อเดิม) | `apply` จึงเป็นการ **แก้** RS ตัวเดิม ไม่ใช่สร้างตัวใหม่ | `replicaset.apps/snack-rs configured` และต้องลบ Pod เพื่อให้เกิดจาก template ใหม่ |
| `key: node.kubernetes.io/not-ready` / `unreachable` | taint 2 ตัวที่ node lifecycle controller ใส่ให้เรือที่ NotReady หรือติดต่อไม่ได้ | – |
| `operator: Exists` | ทนได้ทุก value ของ key นี้ | – |
| `effect: NoExecute` | taint ชนิดที่ **ไล่** Pod ที่รันอยู่แล้ว ไม่ใช่แค่ห้ามวางใหม่ | Pod บนเรือที่ล่มถูกใส่ `deletionTimestamp` (`DEL`) |
| `tolerationSeconds: 30` | ทนได้ 30 วินาทีแทนค่าเริ่มต้น 300 เพื่อให้เห็นผลเร็ว | ตัวแทนเกิดราว 30 วินาทีหลัง NotReady (t≈72–76 วินาที) |

หยุดเรือ `lab-worker2` แล้ววัดเวลาด้วยลูป (คัดลอกทั้งบล็อกไปวางทีเดียว)

```bash
T0=$(date +%s); docker stop lab-worker2; echo "stop ใช้ $(( $(date +%s)-T0 )) วิ"
for i in $(seq 1 40); do
  t=$(( $(date +%s)-T0 ))
  n=$(kubectl get node lab-worker2 --no-headers | awk '{print $2}')
  rs=$(kubectl get rs snack-rs -n rs-lab --no-headers | awk '{print $2"/"$3"/"$4}')
  echo "t=${t}s node=$n rs(D/C/R)=$rs pods: $(kubectl get pods -n rs-lab --no-headers -o custom-columns=N:.metadata.name,S:.status.phase,R:.metadata.deletionTimestamp,NODE:.spec.nodeName | awk '{printf "%s:%s:%s:%s ", substr($1,10),$2,($3=="<none>"?"-":"DEL"),$4}')"
  [ $t -gt 120 ] && break; sleep 4
done
```

```text
lab-worker2
stop ใช้ 10 วิ
t=10s node=Ready rs(D/C/R)=3/3/3 pods: 8gn5s:Running:-:lab-worker j85td:Running:-:lab-worker2 m55bt:Running:-:lab-worker2 
...
t=43s node=Ready rs(D/C/R)=3/3/3 pods: 8gn5s:Running:-:lab-worker j85td:Running:-:lab-worker2 m55bt:Running:-:lab-worker2 
t=47s node=NotReady rs(D/C/R)=3/3/1 pods: 8gn5s:Running:-:lab-worker j85td:Running:-:lab-worker2 m55bt:Running:-:lab-worker2 
...
t=72s node=NotReady rs(D/C/R)=3/3/1 pods: 8gn5s:Running:-:lab-worker j85td:Running:-:lab-worker2 m55bt:Running:-:lab-worker2 
t=76s node=NotReady rs(D/C/R)=3/3/3 pods: 8gn5s:Running:-:lab-worker czbjw:Running:-:lab-worker j85td:Running:DEL:lab-worker2 m55bt:Running:DEL:lab-worker2 q6kvc:Running:-:lab-worker 
...
t=122s node=NotReady rs(D/C/R)=3/3/3 pods: 8gn5s:Running:-:lab-worker czbjw:Running:-:lab-worker j85td:Running:DEL:lab-worker2 m55bt:Running:DEL:lab-worker2 q6kvc:Running:-:lab-worker 
```

อ่านผล (นับจากเริ่มสั่ง stop; `DEL` = Pod มี `deletionTimestamp` แล้ว; ลูปตรวจทุกราว 4 วินาที เวลาที่เห็นจึงคลาดได้ไม่กี่วินาที และในเครื่องนักศึกษาอาจต่างจากตัวอย่าง)

| เวลา | เหตุการณ์ |
|---|---|
| t≈40–50 วินาที (ในการทดลองเห็นครั้งแรกที่ t=47) | Node เป็น `NotReady` → RS แสดง `3/3/1` (CURRENT ยังนับ Pod บนเรือที่ล่ม แต่ไม่ Ready) |
| ราว 30 วินาทีหลัง NotReady (ในการทดลอง t≈72–76) | ครบ toleration 30 วินาที Pod 2 ตัวบน `lab-worker2` ถูกไล่ (`DEL`) ตัวแทน `czbjw`, `q6kvc` เกิดบน `lab-worker` → `3/3/3` |
| หลังจากนั้น | Pod เก่ายังค้าง (phase ยังแสดง Running เพราะ kubelet บนเรือที่ล่มรายงานไม่ได้) |

```bash
kubectl get rs,pods -n rs-lab -o wide
kubectl get rs snack-rs -n rs-lab -o jsonpath='{.status}{"\n"}'
```

```text
NAME                       DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES         SELECTOR
replicaset.apps/snack-rs   3         3         3       2m51s   app          busybox:1.36   app=snack

NAME                 READY   STATUS        RESTARTS   AGE    IP            NODE          NOMINATED NODE   READINESS GATES
pod/snack-rs-8gn5s   1/1     Running       0          2m9s   10.244.1.7    lab-worker    <none>           <none>
pod/snack-rs-czbjw   1/1     Running       0          49s    10.244.1.8    lab-worker    <none>           <none>
pod/snack-rs-j85td   1/1     Terminating   0          2m9s   10.244.2.9    lab-worker2   <none>           <none>
pod/snack-rs-m55bt   1/1     Terminating   0          2m9s   10.244.2.10   lab-worker2   <none>           <none>
pod/snack-rs-q6kvc   1/1     Running       0          49s    10.244.1.9    lab-worker    <none>           <none>
{"availableReplicas":3,"fullyLabeledReplicas":3,"observedGeneration":2,"readyReplicas":3,"replicas":3,"terminatingReplicas":2}
```

Pod เก่า 2 ตัวค้าง `Terminating` (status แสดง `"terminatingReplicas":2`) และ RS ไม่นับมันแล้ว นำเรือกลับมา

```bash
T0=$(date +%s); docker start lab-worker2
until [ "$(kubectl get node lab-worker2 --no-headers | awk '{print $2}')" = Ready ]; do sleep 2; done; echo "Ready หลัง start $(( $(date +%s)-T0 )) วิ"
for i in 1 2 3 4 5 6 7 8 9 10; do c=$(kubectl get pods -n rs-lab --no-headers | wc -l); [ $c -eq 3 ] && break; sleep 2; done; echo "Pod เก่าหายหลัง start $(( $(date +%s)-T0 )) วิ"
kubectl get nodes; kubectl get pods -n rs-lab -o wide
```

```text
lab-worker2
Ready หลัง start 2 วิ
Pod เก่าหายหลัง start 4 วิ
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   4m21s   v1.37.0
lab-worker          Ready    <none>          4m7s    v1.37.0
lab-worker2         Ready    <none>          4m7s    v1.37.0
NAME             READY   STATUS    RESTARTS   AGE     IP           NODE         NOMINATED NODE   READINESS GATES
snack-rs-8gn5s   1/1     Running   0          2m13s   10.244.1.7   lab-worker   <none>           <none>
snack-rs-czbjw   1/1     Running   0          53s     10.244.1.8   lab-worker   <none>           <none>
snack-rs-q6kvc   1/1     Running   0          53s     10.244.1.9   lab-worker   <none>           <none>
```

เมื่อ kubelet บนเรือกลับมา จึงยืนยันการลบ Pod เก่าได้ Pod เก่าหายภายในไม่กี่วินาที ใน terminal 2 จะเห็นว่าหลัง `docker start` Pod เก่าเปลี่ยนเป็น `0/1 Terminating` แล้วขึ้นสถานะ **`Unknown`** ชั่วครู่ (container เดิมหายไปตั้งแต่เรือถูกหยุด จึงไม่มีสถานะจริงให้รายงาน) ก่อนหายไป ไม่ต้องตกใจ (ตัดคอลัมน์ท้าย)

```text
snack-rs-m55bt   0/1     Terminating         0          2m12s   <none>        lab-worker2
snack-rs-j85td   0/1     Terminating         0          2m12s   <none>        lab-worker2
snack-rs-m55bt   0/1     Unknown             0          2m12s   <none>        lab-worker2
snack-rs-j85td   0/1     Unknown             0          2m12s   <none>        lab-worker2
...
```

### ขั้นที่ 6: คืน template เดิม

ถ้าทำขั้นที่ 5 ต้องคืน snack-rs เป็น template เดิม (ไม่มี toleration 30 วินาที) และลบ Pod ให้เกิดใหม่จาก template เดิม ถ้าข้ามขั้นที่ 5 ก็สั่งได้เหมือนกัน (ได้ Pod ชุดใหม่ที่กระจายอีกครั้ง)

```bash
kubectl apply -f labs/lab01-first-rs/snack-rs.yaml; kubectl delete pod -n rs-lab -l app=snack; sleep 4; kubectl get pods -n rs-lab -o wide
```

```text
replicaset.apps/snack-rs configured
pod "snack-rs-8gn5s" deleted from rs-lab namespace
pod "snack-rs-czbjw" deleted from rs-lab namespace
pod "snack-rs-q6kvc" deleted from rs-lab namespace
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-lmk9h   1/1     Running   0          8s    10.244.2.2    lab-worker2   <none>           <none>
snack-rs-q5cmf   1/1     Running   0          8s    10.244.1.10   lab-worker    <none>           <none>
snack-rs-xd68x   1/1     Running   0          8s    10.244.2.3    lab-worker2   <none>           <none>
```

ปิด terminal 2 ด้วย `Ctrl+C`

### สิ่งที่เห็น

- ลบ Pod (ทีละตัวหรือทั้งหมด) → ตัวใหม่เกิดทันทีขณะตัวเก่ายัง Terminating และ Running ภายในราว 1–2 วินาที
- drain ไม่ต้อง `--force` Pod ที่ถูก evict ไปเกิดใหม่บนเรืออีกลำ และ uncordon แล้วไม่ย้ายกลับ
- (ทางเลือก) เรือล่ม: NotReady ราว 40–50 วินาที → รอ toleration อีก 30 วินาที → ตัวแทนเกิดที่ราว 75–85 วินาที Pod เก่าค้าง Terminating จนเรือกลับมา (ขึ้น `Unknown` ชั่วครู่แล้วหาย)

> **🤔 คำถามชวนคิด:** ถ้าไม่ใส่ toleration 30 วินาที (ใช้ค่าเริ่มต้น) ตัวแทนจะเกิดราววินาทีที่เท่าไรหลังเรือล่ม และระหว่างนั้นร้านมีบูธที่ใช้ได้กี่บูธ

**เก็บกวาด:** ตรวจว่า `kubectl get nodes` เป็น `Ready` ทั้ง 3 ลำ (ไม่มี `SchedulingDisabled`) เก็บ `snack-rs` ไว้ใช้ต่อใน LAB 3

---

## LAB 3: Scale

<p align="center" id="fig-5">
  <img src="images/05-lab3-scale.png" alt="รูปที่ 5 LAB 3 scale" width="900"><br>
  <em><b>รูปที่ 5</b> LAB3: scale ด้วย kubectl scale, แก้ไฟล์แล้ว apply, kubectl edit และ scale 0 พร้อมบันทึกว่า Pod ตัวไหนถูกลบตอน scale ลง</em>
</p>

**เป้าหมาย:** scale ด้วย 3 วิธี (คำสั่ง, แก้ไฟล์, editor) และ scale เป็น 0 บันทึกว่า Pod ตัวไหนถูกลบตอน scale ลง และเห็นว่า `apply` ไฟล์ทับค่าที่ scale ไว้

**ต้องมีจาก LAB 2:** `snack-rs` ใน `rs-lab` (`3 3 3`)

### ขั้นที่ 1: scale ขึ้นเป็น 5

```bash
kubectl scale rs snack-rs -n rs-lab --replicas=5; sleep 4
kubectl get pods -n rs-lab -o wide --sort-by=.metadata.creationTimestamp
```

```text
replicaset.apps/snack-rs scaled
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-lmk9h   1/1     Running   0          25s   10.244.2.2    lab-worker2   <none>           <none>
snack-rs-q5cmf   1/1     Running   0          25s   10.244.1.10   lab-worker    <none>           <none>
snack-rs-xd68x   1/1     Running   0          25s   10.244.2.3    lab-worker2   <none>           <none>
snack-rs-ggvbq   1/1     Running   0          4s    10.244.1.11   lab-worker    <none>           <none>
snack-rs-xfjqd   1/1     Running   0          4s    10.244.2.4    lab-worker2   <none>           <none>
```

**จดไว้:** ตัวไหนเก่า/ใหม่ และแต่ละเรือมีกี่ตัว (ในการทดลอง `lab-worker2` มี 3 ตัว `lab-worker` มี 2 ตัว ในเครื่องนักศึกษาอาจกลับกัน)

### ขั้นที่ 2: scale ลงเป็น 2 แล้วดูว่าใครถูกลบ

```bash
kubectl scale rs snack-rs -n rs-lab --replicas=2; kubectl get pods -n rs-lab -o wide --sort-by=.metadata.creationTimestamp
sleep 3; kubectl get pods -n rs-lab -o wide
kubectl get events -n rs-lab --field-selector reason=SuccessfulDelete --sort-by=.lastTimestamp
```

```text
replicaset.apps/snack-rs scaled
NAME             READY   STATUS        RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-lmk9h   1/1     Terminating   0          25s   10.244.2.2    lab-worker2   <none>           <none>
snack-rs-q5cmf   1/1     Running       0          25s   10.244.1.10   lab-worker    <none>           <none>
snack-rs-xd68x   1/1     Running       0          25s   10.244.2.3    lab-worker2   <none>           <none>
snack-rs-ggvbq   1/1     Terminating   0          4s    10.244.1.11   lab-worker    <none>           <none>
snack-rs-xfjqd   1/1     Terminating   0          4s    10.244.2.4    lab-worker2   <none>           <none>
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-lmk9h   0/1     Error     0          28s   10.244.2.2    lab-worker2   <none>           <none>
snack-rs-q5cmf   1/1     Running   0          28s   10.244.1.10   lab-worker    <none>           <none>
snack-rs-xd68x   1/1     Running   0          28s   10.244.2.3    lab-worker2   <none>           <none>
LAST SEEN   TYPE     REASON             OBJECT                MESSAGE
3s          Normal   SuccessfulDelete   replicaset/snack-rs   Deleted pod: snack-rs-xfjqd
3s          Normal   SuccessfulDelete   replicaset/snack-rs   Deleted pod: snack-rs-lmk9h
3s          Normal   SuccessfulDelete   replicaset/snack-rs   Deleted pod: snack-rs-ggvbq
```

ตัวที่ถูกลบไม่ใช่ "ใหม่สุด 3 ตัว" `lmk9h` เป็นตัวเก่าแต่อยู่บน `lab-worker2` ที่แออัด (3 ตัว) จึงถูกลบก่อน ส่วนตัวใหม่ `ggvbq` และ `xfjqd` ถูกลบตามเกณฑ์อายุ เหลือเรือละ 1 ตัว (เกณฑ์ครบดู [ทฤษฎีหัวข้อ 5.2](../01_Theory/README.md#52-scale-ลงแล้วลบตัวไหน)) ผลในเครื่องนักศึกษาอาจต่าง ให้อธิบายจากเกณฑ์

> **ยังเห็น `0/1 Error` หลัง scale ลง:** 3 วินาทีหลังสั่ง Pod ที่ถูกลบบางตัวอาจยังค้างอยู่ในรายการเป็น `0/1 Error` (ในการทดลองคือ `lmk9h`) เพราะ busybox ถูก kill หลัง grace period แล้วรอระบบเก็บกวาด ไม่ได้ถูกนับเป็นบูธแล้ว รออีกไม่กี่วินาทีจะหายไปเอง (ลำดับบรรทัดของ events ก็อาจต่างจากตัวอย่าง)

> ใช้ `kubectl get events --field-selector reason=SuccessfulDelete` แทน `describe rs` เพราะหลัง LAB 2 Events ของ snack-rs ยาวมากและถูกรวมเป็น `(combined from similar events)`

### ขั้นที่ 3: แก้ไฟล์แล้ว apply

แก้บรรทัด `replicas: 3` ในไฟล์เป็น 4 ด้วย `sed` (บรรทัดนี้มีคอมเมนต์ต่อท้าย pattern จึงมีช่องว่างหลังตัวเลข) หรือแก้ด้วย `nano` ก็ได้

```bash
sed -i 's/replicas: 3 /replicas: 4 /' labs/lab01-first-rs/snack-rs.yaml
grep -n 'replicas:' labs/lab01-first-rs/snack-rs.yaml
kubectl apply -f labs/lab01-first-rs/snack-rs.yaml; sleep 3; kubectl get rs snack-rs -n rs-lab
```

```text
10:  replicas: 4                # จำนวนบูธที่ต้องมีตลอดเวลา
replicaset.apps/snack-rs configured
NAME       DESIRED   CURRENT   READY   AGE
snack-rs   4         4         4       3m26s
```

> **YAML ที่แก้ในขั้นนี้:** ใช้ `snack-rs.yaml` ตัวเดิม (อธิบายทุก field ไว้ใน LAB 1) เปลี่ยนแค่ `spec.replicas` บรรทัดที่ 10 ซึ่ง `sed` จับด้วย `replicas: 3 ` (มีช่องว่างตามด้วยคอมเมนต์) และในไฟล์มีคำว่า `replicas:` อยู่บรรทัดเดียว `grep -n` จึงแสดงบรรทัดเดียว `apply` ส่ง spec ทั้งไฟล์ไปเทียบ RS ตัวเดิม ฟิลด์ที่เปลี่ยนมีแค่ `replicas` จึงได้ `configured` และ DESIRED เป็น 4

### ขั้นที่ 4: แก้สดด้วย kubectl edit

k8s-lab มี `nano`, `vi`, `vim` แต่ไม่ได้ตั้งตัวแปร `EDITOR` (`kubectl edit` จะเปิด `vi`) ใช้ `nano` ที่ง่ายกว่า

```bash
KUBE_EDITOR=nano kubectl edit rs snack-rs -n rs-lab
```

ใน nano เลื่อนลงหาบรรทัด `  replicas: 4` ใต้ `spec:` (ไม่ใช่ `status:` ด้านล่าง) แก้เป็น `6` แล้วกด `Ctrl+O` `Enter` `Ctrl+X`

```bash
sleep 3; kubectl get rs snack-rs -n rs-lab
```

```text
replicaset.apps/snack-rs edited
NAME       DESIRED   CURRENT   READY   AGE
snack-rs   6         6         6       3m30s
```

(บรรทัด `replicaset.apps/snack-rs edited` ขึ้นหลังบันทึกและออกจาก nano แล้ว)

### ขั้นที่ 5: scale เป็น 0

```bash
kubectl scale rs snack-rs -n rs-lab --replicas=0; sleep 3; kubectl get rs,pods -n rs-lab
```

```text
replicaset.apps/snack-rs scaled
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/snack-rs   0         0         0       3m33s

NAME                 READY   STATUS   RESTARTS   AGE
pod/snack-rs-7rd7x   0/1     Error    0          10s
pod/snack-rs-fbv6k   0/1     Error    0          10s
pod/snack-rs-pb9w5   0/1     Error    0          6s
pod/snack-rs-q5cmf   0/1     Error    0          38s
pod/snack-rs-xd68x   0/1     Error    0          38s
```

RS ยังอยู่ (`0 0 0`) พร้อม template Pod ที่เหลือกำลังถูกลบ (ขึ้น `Error` ชั่วครู่แล้วหาย จำนวนบรรทัด `Error` ที่เห็นขึ้นกับจังหวะที่สั่ง ในการทดลองเห็น 5 จาก 6 ตัว) นี่คือวิธี "ปิดร้านชั่วคราว" โดยไม่ต้องลบ RS

### ขั้นที่ 6: apply ไฟล์ทับค่าที่ scale ไว้ (และคืนไฟล์เป็น 3)

คืนไฟล์เป็น `replicas: 3` (**ต้องทำ** เพราะ LAB 4 และ 6 ใช้ไฟล์นี้ต่อ) แล้ว apply

```bash
sed -i 's/replicas: 4 /replicas: 3 /' labs/lab01-first-rs/snack-rs.yaml
grep -n 'replicas:' labs/lab01-first-rs/snack-rs.yaml
kubectl apply -f labs/lab01-first-rs/snack-rs.yaml; sleep 4; kubectl get rs,pods -n rs-lab -o wide
```

```text
10:  replicas: 3                # จำนวนบูธที่ต้องมีตลอดเวลา
replicaset.apps/snack-rs configured
NAME                       DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES         SELECTOR
replicaset.apps/snack-rs   3         3         3       3m37s   app          busybox:1.36   app=snack

NAME                 READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/snack-rs-hjwhf   1/1     Running   0          4s    10.244.1.14   lab-worker    <none>           <none>
pod/snack-rs-tklkt   1/1     Running   0          4s    10.244.2.7    lab-worker2   <none>           <none>
pod/snack-rs-z77g8   1/1     Running   0          4s    10.244.2.8    lab-worker2   <none>           <none>
```

แม้เราเพิ่ง scale เป็น 0 แต่ `apply` ไฟล์ที่มี `replicas: 3` ทำให้ร้านกลับมา 3 บูธทันที **ค่าในไฟล์ชนะค่าที่ scale ไว้เสมอ** (ถ้าไม่ได้แก้ไฟล์กลับเป็น 3 ร้านจะกลับมา 4 บูธตามไฟล์)

### สิ่งที่เห็น

- `kubectl scale`, แก้ไฟล์ + apply, และ `kubectl edit` เปลี่ยนจำนวนได้ทันที scale 0 แล้ว RS ยังอยู่
- scale ลงไม่ได้ลบ "ตัวใหม่สุด" เสมอ เรือที่แออัดถูกพิจารณาก่อนอายุ
- `kubectl apply` ทับค่าที่ `scale`/`edit` ไว้

> **🤔 คำถามชวนคิด:** ถ้าต้องการให้ Pod `snack-rs-hjwhf` (หรือชื่อในเครื่องตัวเอง) ถูกลบเป็นตัวแรกตอน scale ลงครั้งหน้า จะใช้ annotation อะไร (ดูทฤษฎีหัวข้อ 5.2)

**เก็บกวาด:** ตรวจว่า `grep -n 'replicas:' labs/lab01-first-rs/snack-rs.yaml` เป็น 3 แล้ว เก็บ `snack-rs` (`3 3 3`) ไว้ใช้ต่อใน LAB 4

---

## LAB 4: กับดัก label

<p align="center" id="fig-6">
  <img src="images/06-lab4-label-trap.png" alt="รูปที่ 6 LAB 4 กับดัก label" width="900"><br>
  <em><b>รูปที่ 6</b> LAB4: Pod stray ที่ label ตรงถูกลบทันทีเมื่อ RS ครบแล้ว แต่ถ้ามีอยู่ก่อนจะถูกรับเลี้ยง และถอด label เพื่อแยก Pod ออกมา debug</em>
</p>

**เป้าหมาย:** เห็นว่า ReplicaSet นับจาก label (ก) Pod ที่ป้ายตรงและสร้างทีหลังถูกลบทันที (ข) Pod ที่มีอยู่ก่อนถูกรับเลี้ยง (ค) RS สองตัว selector ทับกัน (ง) ถอด label เพื่อแยก Pod ออกมา debug

**ต้องมีจาก LAB 3:** `snack-rs` ใน `rs-lab` (`3 3 3`)

**ไฟล์:** `labs/lab04-label-trap/stray-pod.yaml` (Pod เดี่ยวชื่อ `stray` ป้าย `app: snack` แต่ command เป็น `echo ฉันคือ stray ไม่ได้มาจากแบบพิมพ์; sleep 3600`) และ `snack-rs-b.yaml`

```bash
cat labs/lab04-label-trap/stray-pod.yaml
```

#### อธิบาย YAML: `labs/lab04-label-trap/stray-pod.yaml`

```yaml
# LAB 4: Pod หลงที่ติดป้าย app=snack เหมือนบูธของ snack-rs แต่ทำงานคนละอย่าง (command ต่าง)
apiVersion: v1
kind: Pod   # Pod ที่เราสร้างเอง ตอนเกิดไม่มี ownerReferences
metadata:
  name: stray
  namespace: rs-lab
  labels:
    app: snack               # ป้ายตรง selector ของ snack-rs → หัวหน้ากะนับรวม
spec:
  terminationGracePeriodSeconds: 1   # ถูก RS ลบแล้วปิดเร็ว
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "echo ฉันคือ stray ไม่ได้มาจากแบบพิมพ์; sleep 3600"]   # ต่างจาก template ของ snack-rs → ใช้จับ "บูธปลอม"
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `kind: Pod` (สร้างเอง) | ตอนเกิดไม่มี `ownerReferences` จึงเป็น "Pod ไร้เจ้าของ" ที่ RS รับเลี้ยงได้ | (ข) ได้ ownerReferences ชี้ `snack-rs` |
| `name: stray` | ชื่อตายตัว บรรทัดนี้ไม่มีคอมเมนต์ต่อท้ายเพราะขั้นที่ 3 ใช้ `sed 's/name: stray$/name: stray2/'` ที่ต้องเจอ `stray` เป็นคำสุดท้ายของบรรทัด | ขั้นที่ 3 ได้ `pod/stray2 created` |
| `labels: app: snack` | ป้ายตรง selector ของ snack-rs นี่คือ "กับดัก" ทั้งหมดของ LAB นี้ | (ก) ถูกลบทันที (ข) ถูกนับเป็นสมาชิก |
| `terminationGracePeriodSeconds: 1` | ปิดเร็วเมื่อ RS สั่งลบ | `stray 0/1 Terminating 0s` แล้วหายใน 2 วินาที |
| `command` ต่างจาก template | พิมพ์ `ฉันคือ stray ...` แทน `บูธขนม ...` ใช้พิสูจน์ว่า Pod ที่ถูกรับเลี้ยงไม่ได้ถูกเปลี่ยนตาม template | `kubectl logs stray` และ `/proc/1/cmdline` |

### ขั้นที่ 1 (ก): Pod ที่สร้างทีหลังถูกลบทันที

```bash
kubectl apply -f labs/lab04-label-trap/stray-pod.yaml; kubectl get pods -n rs-lab --show-labels
sleep 2; kubectl get pods -n rs-lab
```

```text
pod/stray created
NAME             READY   STATUS        RESTARTS   AGE   LABELS
snack-rs-hjwhf   1/1     Running       0          4s    app=snack
snack-rs-tklkt   1/1     Running       0          4s    app=snack
snack-rs-z77g8   1/1     Running       0          4s    app=snack
stray            0/1     Terminating   0          0s    app=snack
NAME             READY   STATUS    RESTARTS   AGE
snack-rs-hjwhf   1/1     Running   0          6s
snack-rs-tklkt   1/1     Running   0          6s
snack-rs-z77g8   1/1     Running   0          6s
```

kubectl บอก `created` แต่ `stray` เป็น `Terminating` ตั้งแต่อายุ 0 วินาที RS นับได้ 4 เกิน 3 จึงลบตัวที่ยังไม่ Ready และใหม่สุด ซึ่งคือ `stray`

> **Event อาจไม่ขึ้น:** ในการทดลองจริง ขั้นนี้ไม่มี event `Deleted pod: stray` ให้เห็นใน `describe rs` เพราะ snack-rs สร้าง/ลบ Pod มาหลายสิบครั้งตั้งแต่ LAB 2 จนเกินขีดจำกัด event ต่อ object (spam filter) ให้เชื่อผลของ `kubectl get pods` เป็นหลัก ในขั้นที่ 3 จะเห็น event นี้กับ RS ที่สร้างใหม่

### ขั้นที่ 2 (ข): Pod ที่มีอยู่ก่อนถูกรับเลี้ยง

ลบ RS แล้วสร้าง `stray` ก่อน จากนั้นจึงสร้าง RS

```bash
kubectl delete rs snack-rs -n rs-lab
kubectl apply -f labs/lab04-label-trap/stray-pod.yaml
kubectl wait --for=condition=Ready pod/stray -n rs-lab --timeout=60s
kubectl apply -f labs/lab01-first-rs/snack-rs.yaml; sleep 4; kubectl get pods -n rs-lab -o wide
```

```text
replicaset.apps "snack-rs" deleted from rs-lab namespace
pod/stray created
pod/stray condition met
replicaset.apps/snack-rs created
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-hkn87   1/1     Running   0          4s    10.244.1.16   lab-worker    <none>           <none>
snack-rs-k7h8d   1/1     Running   0          4s    10.244.1.15   lab-worker    <none>           <none>
stray            1/1     Running   0          5s    10.244.2.9    lab-worker2   <none>           <none>
```

RS ใหม่สร้างเพิ่มแค่ **2 ตัว** ตรวจว่า `stray` มีเจ้าของแล้ว และยังทำงานคนละอย่างกับ template

```bash
kubectl get pod stray -n rs-lab -o jsonpath='{.metadata.ownerReferences}{"\n"}'
kubectl logs stray -n rs-lab
kubectl exec stray -n rs-lab -- cat /proc/1/cmdline | tr '\0' ' '; echo
kubectl describe rs snack-rs -n rs-lab | grep -A6 Events
```

```text
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"ReplicaSet","name":"snack-rs","uid":"475cb184-1aaa-4340-9bfa-f831fc0171dd"}]
ฉันคือ stray ไม่ได้มาจากแบบพิมพ์
sh -c echo ฉันคือ stray ไม่ได้มาจากแบบพิมพ์; sleep 3600 
Events:
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  4s    replicaset-controller  Created pod: snack-rs-k7h8d
  Normal  SuccessfulCreate  4s    replicaset-controller  Created pod: snack-rs-hkn87
```

`stray` ได้ ownerReferences ชี้ `snack-rs` (uid ของ RS ตัวใหม่) แต่ process ข้างใน (`/proc/1/cmdline`) ยังเป็น command ของ `stray` เอง ไม่ใช่ของ template ร้านมี "บูธปลอม" ปนอยู่หนึ่งบูธ

### ขั้นที่ 3: ยืนยัน event ของ (ก) กับ RS ตัวใหม่

ตอนนี้ snack-rs (uid ใหม่) ครบ 3 แล้ว (รวม `stray`) ลองสร้าง Pod หลงตัวที่สองชื่อ `stray2` (ใช้ `sed` เปลี่ยนชื่อจากไฟล์เดิมแล้วส่งเข้า kubectl ทาง `-f -`)

```bash
sed 's/name: stray$/name: stray2/' labs/lab04-label-trap/stray-pod.yaml | kubectl apply -f -
sleep 2; kubectl get pods -n rs-lab; kubectl describe rs snack-rs -n rs-lab | grep -A8 Events
```

```text
pod/stray2 created
NAME             READY   STATUS    RESTARTS   AGE
snack-rs-hkn87   1/1     Running   0          6s
snack-rs-k7h8d   1/1     Running   0          6s
stray            1/1     Running   0          7s
Events:
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  6s    replicaset-controller  Created pod: snack-rs-k7h8d
  Normal  SuccessfulCreate  6s    replicaset-controller  Created pod: snack-rs-hkn87
  Normal  SuccessfulDelete  2s    replicaset-controller  Deleted pod: stray2
```

คราวนี้เห็นหลักฐาน `SuccessfulDelete ... Deleted pod: stray2` ชัดเจน

### ขั้นที่ 4 (ค): RS ตัวที่สองที่ selector ทับกัน

`snack-rs-b.yaml` ใช้ selector `app: snack` เหมือน snack-rs (**ห้ามทำในงานจริง**)

#### อธิบาย YAML: `labs/lab04-label-trap/snack-rs-b.yaml`

```yaml
# LAB 4 (ทางเลือก): หัวหน้ากะคนที่สองที่ selector ซ้ำกับ snack-rs (ห้ามทำในงานจริง)
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs-b   # Pod ของ RS นี้ชื่อ snack-rs-b-xxxxx (เรียงก่อน snack-rs-xxxxx)
  namespace: rs-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app: snack   # selector ซ้ำกับ snack-rs ← ต้นเหตุความสับสน
  template:
    metadata:
      labels:
        app: snack
    spec:
      terminationGracePeriodSeconds: 1   # หลังลบ RS นี้ Pod ขึ้น Error ค้างอยู่ชั่วครู่
      containers:
        - name: app
          image: busybox:1.36
          command: ["sh", "-c", "echo บูธของ snack-rs-b; sleep 3600"]   # log บอกว่าเป็น Pod ของ snack-rs-b
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 50m, memory: 32Mi }
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `name: snack-rs-b` | Pod ได้ชื่อ `snack-rs-b-xxxxx` ซึ่ง **เรียงตามตัวอักษรก่อน** `snack-rs-xxxxx` | ในรายการ `-l app=snack` Pod ของ snack-rs-b อยู่บนสุด (สำคัญในขั้นที่ 5) |
| `selector` / `template.labels` = `app: snack` | ซ้ำกับ snack-rs ทุกตัวอักษร แต่ RS จะไม่แย่ง Pod ที่มี controller เป็น RS อื่นอยู่แล้ว | snack-rs-b สร้างของตัวเอง 3 ตัว เห็นในคอลัมน์ OWNER |
| `replicas: 3` | นับเฉพาะ Pod ที่ตัวเองเป็นเจ้าของ จึงต้องสร้างครบ 3 เอง | `snack-rs-b 3 3 3` ขณะที่ `-l app=snack` เห็น 6 ตัว |
| `terminationGracePeriodSeconds: 1` | เหมือน snack-rs แต่หลังลบ RS นี้ Pod ทั้ง 3 ยังค้างเป็น `0/1 Error` อยู่หลายวินาทีก่อนหาย | ผลหลัง `delete rs snack-rs-b; sleep 3` |
| `command` พิมพ์ `บูธของ snack-rs-b` | log บอกได้ทันทีว่า Pod เป็นของ RS ไหน | ใช้ตรวจว่าขั้นที่ 5 เลือก Pod ถูกตัว |

```bash
kubectl apply -f labs/lab04-label-trap/snack-rs-b.yaml; sleep 15
kubectl get rs -n rs-lab
kubectl get pods -n rs-lab -l app=snack -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name,STATUS:.status.phase
kubectl describe rs snack-rs-b -n rs-lab | grep -A8 Events
```

```text
replicaset.apps/snack-rs-b created
NAME         DESIRED   CURRENT   READY   AGE
snack-rs     3         3         3       21s
snack-rs-b   3         3         3       15s
NAME               OWNER        STATUS
snack-rs-b-pn9nj   snack-rs-b   Running
snack-rs-b-r8hz4   snack-rs-b   Running
snack-rs-b-xbph5   snack-rs-b   Running
snack-rs-hkn87     snack-rs     Running
snack-rs-k7h8d     snack-rs     Running
stray              snack-rs     Running
Events:
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  15s   replicaset-controller  Created pod: snack-rs-b-r8hz4
  Normal  SuccessfulCreate  15s   replicaset-controller  Created pod: snack-rs-b-pn9nj
  Normal  SuccessfulCreate  15s   replicaset-controller  Created pod: snack-rs-b-xbph5
```

snack-rs-b ไม่แตะ Pod ที่มีเจ้าของแล้ว จึงสร้างของตัวเอง 3 ตัว แต่ละ RS นับเฉพาะ Pod ที่ตัวเองเป็นเจ้าของ (คอลัมน์ OWNER) ไม่แย่งและไม่ลบของกัน แต่ `-l app=snack` เห็น 6 ตัวปนกัน ใครมาดูทีหลังจะงง ลบ RS ตัวที่สอง

```bash
kubectl delete rs snack-rs-b -n rs-lab; sleep 3; kubectl get rs,pods -n rs-lab
```

```text
replicaset.apps "snack-rs-b" deleted from rs-lab namespace
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/snack-rs   3         3         3       25s

NAME                   READY   STATUS    RESTARTS   AGE
pod/snack-rs-b-pn9nj   0/1     Error     0          19s
pod/snack-rs-b-r8hz4   0/1     Error     0          19s
pod/snack-rs-b-xbph5   0/1     Error     0          19s
pod/snack-rs-hkn87     1/1     Running   0          25s
pod/snack-rs-k7h8d     1/1     Running   0          25s
pod/stray              1/1     Running   0          26s
```

RS `snack-rs-b` หายแล้ว แต่ 3 วินาทีต่อมา **Pod ของมันยังค้างอยู่เป็น `0/1 Error`** (กำลังถูกลบตาม garbage collector ตัว busybox ถูก kill หลัง grace period) อีกไม่กี่วินาทีจึงหายไปเอง ในเครื่องนักศึกษาอาจเห็นหรือไม่เห็นบรรทัดเหล่านี้ก็ได้ ขึ้นกับจังหวะ

### ขั้นที่ 5 (ง): ถอด label แยก Pod ออกมา debug

เลือก Pod ตัวแรกที่ **เจ้าของ (OWNER) เป็น `snack-rs`** แล้วถอด label `app`

```bash
P=$(kubectl get pods -n rs-lab -l app=snack --no-headers -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name | awk '$2=="snack-rs"{print $1; exit}'); echo P=$P
kubectl label pod $P -n rs-lab app-
kubectl get pod $P -n rs-lab -o jsonpath='owner={.metadata.ownerReferences}{"\n"}'
kubectl get pods -n rs-lab --show-labels
kubectl logs $P -n rs-lab
```

> **ทำไมไม่ใช้ `{.items[0].metadata.name}` ตรง ๆ (เจอจริงในการทดลอง):** ถ้าเลือกด้วย `kubectl get pods -n rs-lab -l app=snack -o jsonpath='{.items[0].metadata.name}'` ทันทีหลังขั้นที่ 4 Pod `snack-rs-b-*` ที่ยังค้าง `Error` จะติดป้าย `app=snack` อยู่และเรียงชื่อก่อน `snack-rs-*` คำสั่งจึงได้ `P=snack-rs-b-pn9nj` ผลที่ได้ในการทดลองรอบแรกคือ `owner=` ยังชี้ `snack-rs-b`, `snack-rs` ไม่สร้างตัวแทน และ log เป็น `บูธของ snack-rs-b` ซึ่ง **ไม่ใช่สิ่งที่ขั้นนี้ต้องการแสดง** คำสั่งใหม่ดึงคอลัมน์ NAME กับ OWNER (แบบเดียวกับขั้นที่ 4) แล้วให้ `awk` เลือกบรรทัดแรกที่ OWNER เป็น `snack-rs` พอดี (`$2=="snack-rs"` ไม่ตรงกับ `snack-rs-b`) จึงได้ Pod ของ snack-rs เสมอแม้ Pod ของ snack-rs-b ยังค้างอยู่ (อีกทางหนึ่งคือรอให้ `kubectl get pods -n rs-lab` ไม่เหลือ `snack-rs-b-*` ก่อนแล้วค่อยทำขั้นนี้)

ผลด้านล่างมาจากการรันขั้นนี้ซ้ำหลัง Pod ของ snack-rs-b หายหมดแล้ว (ตอนนั้น Pod ตัวแรกในรายการคือ `snack-rs-hkn87` ซึ่งเป็นตัวเดียวกับที่คำสั่งใหม่เลือก เพราะเป็นตัวแรกที่ OWNER เป็น `snack-rs`)

```text
P=snack-rs-hkn87
pod/snack-rs-hkn87 unlabeled
owner=
NAME             READY   STATUS              RESTARTS   AGE   LABELS
snack-rs-d5wp2   0/1     ContainerCreating   0          0s    app=snack
snack-rs-hkn87   1/1     Running             0          56s   <none>
snack-rs-k7h8d   1/1     Running             0          56s   app=snack
stray            1/1     Running             0          57s   app=snack
บูธขนม snack-rs-hkn87 เปิดแล้ว
```

ทันทีที่ถอดป้าย ownerReferences ของ `snack-rs-hkn87` **ว่างเปล่า** (RS ปล่อยแล้ว) และ RS สร้างตัวแทน `snack-rs-d5wp2` ทันที (อายุ 0 วินาที) ส่วน Pod ที่ถอดป้ายยังรันและอ่าน log ได้ (log `บูธขนม ...` ยืนยันว่าเป็น Pod ของ snack-rs) ตรวจเสร็จแล้วต้องลบเอง

```bash
kubectl delete pod $P -n rs-lab; kubectl get rs,pods -n rs-lab
```

```text
pod "snack-rs-hkn87" deleted from rs-lab namespace
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/snack-rs   3         3         3       60s

NAME                 READY   STATUS    RESTARTS   AGE
pod/snack-rs-d5wp2   1/1     Running   0          4s
pod/snack-rs-k7h8d   1/1     Running   0          60s
pod/stray            1/1     Running   0          61s
```

ลบ Pod ที่ถูกปล่อยแล้ว RS ไม่สร้างอะไรเพิ่ม (ไม่ใช่ของมันแล้ว)

### สิ่งที่เห็น

- (ก) Pod ป้ายตรงที่สร้างหลัง RS ครบ → ถูกลบทันที (Event อาจไม่ขึ้นถ้า RS มี event มากแล้ว)
- (ข) Pod ไร้เจ้าของที่มีอยู่ก่อน → ถูกรับเลี้ยง RS สร้างเพิ่มแค่ส่วนที่ขาด แม้ Pod นั้นต่างจาก template
- (ค) RS สองตัว selector ทับกันไม่แย่ง Pod ที่มีเจ้าของ แต่ดูปนกันจนสับสน (หลังลบ RS ตัวที่สอง Pod ของมันยังค้าง `Error` ชั่วครู่ จึงต้องดู OWNER ก่อนเลือก Pod)
- (ง) ถอด label → RS ปล่อย Pod ทันทีและสร้างตัวแทน Pod เดิมอยู่ให้ตรวจ

> **🤔 คำถามชวนคิด:** ตอนนี้ snack-rs มี `stray` เป็นสมาชิกอยู่ ถ้าในงานจริงเกิดแบบนี้ จะตรวจหา "บูธปลอม" ได้อย่างไร (ใบ้: เทียบชื่อ Pod กับ `generateName` หรือเทียบ image/command กับ template)

**เก็บกวาด:** เก็บ `snack-rs` (รวม `stray`) ไว้ใช้ใน LAB 6

---

## LAB 5: selector แก้ไม่ได้ + template ใหม่ Pod เดิมไม่เปลี่ยน

<p align="center" id="fig-7">
  <img src="images/07-lab5-template-old-pods.png" alt="รูปที่ 7 LAB 5 template ใหม่ Pod เดิมไม่เปลี่ยน" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: เปลี่ยน selector ได้ field is immutable; เปลี่ยน image ใน template เป็น nginx:1.28-alpine แล้ว custom-columns ยังเห็น 1.27 ทุกตัว จนกว่าจะลบ Pod</em>
</p>

**เป้าหมาย:** เห็นข้อจำกัดของ ReplicaSet ในการเปลี่ยนรุ่น selector แก้ไม่ได้ และ template ใหม่มีผลเฉพาะ Pod ที่เกิดใหม่

**ไฟล์:** `labs/lab05-template/web-rs.yaml` (nginx `1.27-alpine`, env `VERSION=v1` เขียนหน้า index เป็น `web $VERSION from <ชื่อ Pod>` มี readinessProbe), `web-rs-v2.yaml` (เปลี่ยน image เป็น `1.28-alpine` และ `VERSION=v2`), `web-rs-new-selector.yaml` (เพิ่ม `tier: front` ใน selector) ทั้งหมดอยู่ใน `rs-lab` คู่กับ snack-rs (selector `app=web` ไม่ทับกับ `app=snack`)

```bash
diff labs/lab05-template/web-rs.yaml labs/lab05-template/web-rs-v2.yaml
```

```text
1c1
< # LAB 5: ReplicaSet web รุ่น v1 (nginx:1.27-alpine) หน้าเว็บตอบ "web v1 from <ชื่อ Pod>"
---
> # LAB 5: แบบพิมพ์ใหม่ (image 1.28 + VERSION v2) — Pod เดิมจะไม่เปลี่ยนตาม
21c21
<           image: nginx:1.27-alpine
---
>           image: nginx:1.28-alpine   # ← เปลี่ยนรุ่น
24c24
<               value: v1
---
>               value: v2              # ← เปลี่ยนรุ่น
```

#### อธิบาย YAML: `labs/lab05-template/web-rs.yaml`, `web-rs-v2.yaml`, `web-rs-new-selector.yaml`

```yaml
# LAB 5: ReplicaSet web รุ่น v1 (nginx:1.27-alpine) หน้าเว็บตอบ "web v1 from <ชื่อ Pod>"
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web
  namespace: rs-lab
  labels:
    app: web
spec:
  replicas: 3   # 3 บูธ
  selector:
    matchLabels:
      app: web   # selector: แก้ไม่ได้หลังสร้าง (immutable)
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx   # ชื่อ container (คอลัมน์ CONTAINERS ของ get rs -o wide)
          image: nginx:1.27-alpine
          env:
            - name: VERSION          # รุ่นของหน้าเว็บ (ดูด้วย custom-columns ได้)
              value: v1
          # เขียนหน้า index ให้บอกรุ่นและชื่อ Pod แล้วเปิด nginx
          command: ["sh", "-c", "echo \"web $VERSION from $(hostname)\" > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]
          ports:
            - containerPort: 80   # nginx ฟังพอร์ต 80 (เฉพาะ IPv4 เพราะ command ทับสคริปต์ตั้งต้น)
          readinessProbe:   # Ready เมื่อ GET / ได้ 200 → kubectl wait ใช้เงื่อนไขนี้
            httpGet: { path: /, port: 80 }
            periodSeconds: 2   # ตรวจทุก 2 วิ
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 100m, memory: 64Mi }
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `selector.matchLabels: app: web` | ไม่ทับกับ `app=snack` จึงอยู่ใน `rs-lab` คู่กับ snack-rs ได้ และเป็น field ที่ **แก้ไม่ได้** หลังสร้าง | ขั้นที่ 2 `field is immutable` |
| `image: nginx:1.27-alpine` | รุ่นเริ่มต้น `web-rs-v2.yaml` เปลี่ยนเป็น `1.28-alpine` | custom-columns IMAGE |
| `env VERSION: v1` | ตัวแปรที่ `command` ใช้เขียนหน้าเว็บ และเป็น `env[0]` ที่ custom-columns ดึงมาแสดง v2 เปลี่ยนเป็น `v2` | คอลัมน์ VERSION และ `web v1 from ...` |
| `command` (sh -c ... `exec nginx`) | เขียน `index.html` เป็น `web $VERSION from $(hostname)` แล้วเปิด nginx แทนสคริปต์ตั้งต้นของ image ผลข้างเคียงคือ nginx ไม่ได้เปิดฟัง IPv6 | `wget 127.0.0.1` ได้ แต่ `wget localhost` ได้ Connection refused |
| `ports.containerPort: 80` | ประกาศพอร์ตที่ nginx ฟัง | – |
| `readinessProbe httpGet / port 80`, `periodSeconds: 2` | Pod จะ Ready เมื่อหน้าแรกตอบ 200 ตรวจทุก 2 วินาที | `kubectl wait --for=condition=Ready` จบเมื่อทั้ง 3 ตัวตอบได้ (ราว 9 วินาทีรวมเวลาดึง image) |
| `resources` | ขนาดเล็กพอให้รันคู่กับ snack-rs ได้ | – |

- **`web-rs-v2.yaml`** เหมือนกันทุกบรรทัด ยกเว้น 3 บรรทัดตาม `diff` ข้างบน (คอมเมนต์หัวไฟล์, `image: nginx:1.28-alpine`, `value: v2`) จึงเป็น "template ใหม่" ของ RS `web` ตัวเดิม (ชื่อ, selector เหมือนเดิม) `apply` จึงได้ `configured`
- **`web-rs-new-selector.yaml`** เพิ่ม `tier: front` ทั้งใน `selector.matchLabels` และ `template.metadata.labels` (template ยังผ่าน selector) แต่ RS `web` มีอยู่แล้ว การเปลี่ยน selector จึงถูกปฏิเสธ

```yaml
  selector:
    matchLabels:
      app: web
      tier: front          # ← เพิ่มป้ายใน selector (ห้ามแก้ selector หลังสร้าง)
  template:
    metadata:
      labels:
        app: web
        tier: front
```

### ขั้นที่ 1: สร้าง RS web รุ่น v1

```bash
kubectl apply -f labs/lab05-template/web-rs.yaml
time kubectl wait --for=condition=Ready pod -l app=web -n rs-lab --timeout=120s
kubectl get pods -n rs-lab -l app=web -o wide
```

```text
replicaset.apps/web created
pod/web-hchtr condition met
pod/web-hghp6 condition met
pod/web-pjkt9 condition met

real	0m9.033s
user	0m0.049s
sys	0m0.026s
NAME        READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
web-hchtr   1/1     Running   0          9s    10.244.2.13   lab-worker2   <none>           <none>
web-hghp6   1/1     Running   0          9s    10.244.1.18   lab-worker    <none>           <none>
web-pjkt9   1/1     Running   0          9s    10.244.1.19   lab-worker    <none>           <none>
```

(เวลา `real` รวมเวลาที่ Node ดึง `nginx:1.27-alpine` ครั้งแรก ในเครื่องนักศึกษาอาจนานกว่านี้)

ทดสอบหน้าเว็บจากในบูธ (ใช้ **`127.0.0.1`** ไม่ใช่ `localhost` — ดูหมายเหตุ)

```bash
P=$(kubectl get pods -n rs-lab -l app=web -o jsonpath="{.items[0].metadata.name}")
kubectl exec -n rs-lab $P -- wget -qO- 127.0.0.1
```

```text
web v1 from web-hchtr
```

> **ทำไมไม่ใช้ `localhost`:** ทดลองแล้ว `wget -qO- localhost` ได้ `wget: can't connect to remote host: Connection refused` (ตามด้วย `command terminated with exit code 1`) เพราะ `localhost` ใน `/etc/hosts` ของ Pod ชี้ทั้ง `127.0.0.1` และ `::1` (IPv6) และ wget ลอง `::1` ก่อน ขณะที่ manifest นี้ทับ `command` ของ nginx ทำให้สคริปต์ตั้งต้นที่เปิดฟัง IPv6 ไม่ได้ทำงาน nginx จึงฟังเฉพาะ IPv4

### ขั้นที่ 2: ลองแก้ selector

```bash
kubectl apply -f labs/lab05-template/web-rs-new-selector.yaml; echo "exit=$?"
```

```text
The ReplicaSet "web" is invalid: spec.selector: Invalid value: {"matchLabels":{"app":"web","tier":"front"}}: field is immutable
exit=1
```

### ขั้นที่ 3: apply template ใหม่ (v2)

```bash
kubectl apply -f labs/lab05-template/web-rs-v2.yaml; sleep 2
kubectl get pods -n rs-lab -l app=web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,VERSION:.spec.containers[0].env[0].value
kubectl get rs web -n rs-lab -o wide
for p in $(kubectl get pods -n rs-lab -l app=web -o name); do kubectl exec -n rs-lab $p -- wget -qO- 127.0.0.1; done
```

```text
replicaset.apps/web configured
NAME        IMAGE               VERSION
web-hchtr   nginx:1.27-alpine   v1
web-hghp6   nginx:1.27-alpine   v1
web-pjkt9   nginx:1.27-alpine   v1
NAME   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES              SELECTOR
web    3         3         3       11s   nginx        nginx:1.28-alpine   app=web
web v1 from web-hchtr
web v1 from web-hghp6
web v1 from web-pjkt9
```

RS บอก IMAGES `nginx:1.28-alpine` (template) แต่ Pod ทั้ง 3 ตัวยังเป็น `1.27` / `v1` และหน้าเว็บยังตอบ v1 ทุกบูธ

### ขั้นที่ 4: ลบ Pod หนึ่งตัว

```bash
P=$(kubectl get pods -n rs-lab -l app=web -o jsonpath="{.items[0].metadata.name}")
kubectl delete pod $P -n rs-lab; T0=$(date +%s)
kubectl wait --for=condition=Ready pod -l app=web -n rs-lab --timeout=120s >/dev/null; echo "รอ Ready $(( $(date +%s)-T0 )) วิ"
kubectl get pods -n rs-lab -l app=web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,VERSION:.spec.containers[0].env[0].value,AGE:.metadata.creationTimestamp
for p in $(kubectl get pods -n rs-lab -l app=web -o name); do kubectl exec -n rs-lab $p -- wget -qO- 127.0.0.1; done
```

```text
pod "web-hchtr" deleted from rs-lab namespace
รอ Ready 7 วิ
NAME        IMAGE               VERSION   AGE
web-hghp6   nginx:1.27-alpine   v1        2026-10-05T10:15:05Z
web-pjkt9   nginx:1.27-alpine   v1        2026-10-05T10:15:05Z
web-shrj5   nginx:1.28-alpine   v2        2026-10-05T10:15:17Z
web v1 from web-hghp6
web v1 from web-pjkt9
web v2 from web-shrj5
```

ตัวที่เกิดใหม่เท่านั้นที่เป็น v2 (Node ต้องดึง `nginx:1.28-alpine` ก่อน จึงใช้เวลาหลายวินาที) ร้านตอนนี้มี **รุ่นปนกัน** ถ้าจะให้ครบต้องลบอีก 2 ตัวทีละตัวและรอเอง ซึ่งจะเจออีกครั้งใน LAB 9

> **ลำดับบรรทัด:** `kubectl get pods` เรียงตาม **ชื่อ** ไม่ใช่อายุ ตัวใหม่จึงอาจอยู่บน ล่าง หรือกลางตารางก็ได้ (ในการทดลอง `web-shrj5` อยู่ล่างสุด) ให้ดูคอลัมน์ AGE (`creationTimestamp` เป็นเวลา UTC) หรือ VERSION แทนตำแหน่งบรรทัด ชื่อ Pod และเวลาในเครื่องนักศึกษาจะต่างจากตัวอย่าง

### ขั้นที่ 5: ลบ RS web

```bash
kubectl delete rs web -n rs-lab; kubectl get rs,pods -n rs-lab
```

```text
replicaset.apps "web" deleted from rs-lab namespace
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/snack-rs   3         3         3       87s

NAME                 READY   STATUS        RESTARTS   AGE
pod/snack-rs-d5wp2   1/1     Running       0          31s
pod/snack-rs-k7h8d   1/1     Running       0          87s
pod/stray            1/1     Running       0          88s
pod/web-hghp6        1/1     Terminating   0          20s
pod/web-pjkt9        1/1     Terminating   0          20s
pod/web-shrj5        1/1     Terminating   0          8s
```

### สิ่งที่เห็น

- แก้ selector → `field is immutable`
- apply template ใหม่ → `get rs -o wide` เปลี่ยน แต่ Pod เดิมยังรุ่นเก่าทุกตัว
- ลบ Pod → เฉพาะตัวใหม่ได้รุ่นใหม่ เปลี่ยนรุ่นทั้งร้านต้องลบเองทีละตัว

> **🤔 คำถามชวนคิด:** ถ้าสั่ง `kubectl delete pod -n rs-lab -l app=web` เพื่อเปลี่ยนรุ่นทีเดียวทั้ง 3 ตัว จะเกิดอะไรกับลูกค้าในช่วงนั้น

**เก็บกวาด:** ลบ RS web แล้วในขั้นที่ 5 เก็บ `snack-rs` ไว้ใช้ใน LAB 6

---

## LAB 6: ลบ ReplicaSet แบบ cascade vs orphan

<p align="center" id="fig-8">
  <img src="images/08-lab6-cascade-orphan.png" alt="รูปที่ 8 LAB 6 cascade vs orphan" width="900"><br>
  <em><b>รูปที่ 8</b> LAB6: ลบ RS ปกติ Pod หายตาม, ลบด้วย --cascade=orphan Pod อยู่ต่อแบบไม่มีเจ้าของ แล้ว apply RS เดิมอีกครั้ง → รับเลี้ยงโดยไม่สร้างเพิ่ม</em>
</p>

**เป้าหมาย:** ลบ RS แบบ orphan แล้วให้ RS ใหม่รับเลี้ยง Pod เดิมโดยไม่สร้างเพิ่ม และลบแบบ foreground เพื่อดู finalizer

**ต้องมีจาก LAB 4:** `snack-rs` ใน `rs-lab` (`3 3 3` มี `stray` เป็นสมาชิก) ส่วนแบบ background (ค่าเริ่มต้น) เราเห็นแล้วตอนลบ RS `snack-rs-expr` (LAB 1) และ `web` (LAB 5) ที่ Pod หายตาม

### ขั้นที่ 1: ลบแบบ orphan

```bash
kubectl delete rs snack-rs -n rs-lab --cascade=orphan; kubectl get rs,pods -n rs-lab
kubectl get pods -n rs-lab -l app=snack -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name,UID:.metadata.ownerReferences[0].uid
```

```text
replicaset.apps "snack-rs" deleted from rs-lab namespace
NAME                 READY   STATUS        RESTARTS   AGE
pod/snack-rs-d5wp2   1/1     Running       0          32s
pod/snack-rs-k7h8d   1/1     Running       0          88s
pod/stray            1/1     Running       0          89s
pod/web-hghp6        1/1     Terminating   0          21s
pod/web-pjkt9        1/1     Terminating   0          21s
pod/web-shrj5        1/1     Terminating   0          9s
NAME             OWNER    UID
snack-rs-d5wp2   <none>   <none>
snack-rs-k7h8d   <none>   <none>
stray            <none>   <none>
```

(บรรทัด `web-...  Terminating` เป็นของ LAB 5 ที่ยังหายไม่หมด ถ้าทำขั้นนี้ช้ากว่าจะไม่เห็น) RS หายไป แต่บูธทั้ง 3 ยังเปิดอยู่ ไม่มีเจ้าของ (`<none>`)

### ขั้นที่ 2: RS ใหม่รับเลี้ยง

```bash
kubectl apply -f labs/lab01-first-rs/snack-rs.yaml; sleep 3; kubectl get rs,pods -n rs-lab
kubectl get rs snack-rs -n rs-lab -o jsonpath='RS uid={.metadata.uid}{"\n"}'
kubectl get pods -n rs-lab -l app=snack -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name,UID:.metadata.ownerReferences[0].uid
kubectl describe rs snack-rs -n rs-lab | grep -A5 Events
```

```text
replicaset.apps/snack-rs created
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/snack-rs   3         3         3       3s

NAME                 READY   STATUS    RESTARTS   AGE
pod/snack-rs-d5wp2   1/1     Running   0          35s
pod/snack-rs-k7h8d   1/1     Running   0          91s
pod/stray            1/1     Running   0          92s
RS uid=b9257656-3a69-41f0-baf5-37eae28d72e4
NAME             OWNER      UID
snack-rs-d5wp2   snack-rs   b9257656-3a69-41f0-baf5-37eae28d72e4
snack-rs-k7h8d   snack-rs   b9257656-3a69-41f0-baf5-37eae28d72e4
stray            snack-rs   b9257656-3a69-41f0-baf5-37eae28d72e4
Events:            <none>
```

RS ใหม่ `3 3 3` ทันทีโดย **ไม่มี Pod ใหม่** (AGE ของ Pod มากกว่าอายุ RS `3s`, `Events: <none>`) และ ownerReferences กลับมาพร้อม uid ของ RS ตัวใหม่ นี่คือวิธี "เปลี่ยนหัวหน้ากะโดยไม่ปิดบูธ" (ไฟล์ที่ apply คือ `snack-rs.yaml` ตัวเดิมจาก LAB 1: `selector.matchLabels: app: snack` ตรงกับ Pod ไร้เจ้าของทั้ง 3 ตัว และ `replicas: 3` พอดีกับจำนวนที่มี RS จึงไม่ต้องสร้างเพิ่ม)

### ขั้นที่ 3: ลบแบบ foreground

🐧 **terminal 2** เฝ้า finalizer ของ RS (เปิดก่อนสั่งลบ)

```bash
kubectl get rs snack-rs -n rs-lab -o jsonpath='{.metadata.finalizers}{"\n"}' -w
```

(ถ้ามีหน้าต่างที่ 3 เปิด `kubectl get rs snack-rs -n rs-lab -w` เพิ่มได้) 🐧 **terminal 1**

```bash
date +%T; kubectl delete rs snack-rs -n rs-lab --cascade=foreground; date +%T; kubectl get rs,pods -n rs-lab
```

```text
17:15:31
replicaset.apps "snack-rs" deleted from rs-lab namespace
17:15:34
No resources found in rs-lab namespace.
```

terminal 2 และหน้าต่างที่ 3

```text

["foregroundDeletion"]
["foregroundDeletion"]
...
NAME       DESIRED   CURRENT   READY   AGE
snack-rs   3         3         3       3s
snack-rs   3         3         3       5s
snack-rs   3         2         2       5s
snack-rs   3         0         0       5s
...
```

(บรรทัดแรกของ terminal 2 ว่าง เพราะตอนเปิดยังไม่มี finalizer; AGE ของ RS ขึ้นกับว่าเปิดหน้าต่างเฝ้าเมื่อไร)

kubectl รอราว 3 วินาที ระหว่างนั้น RS มี finalizer `foregroundDeletion` และ CURRENT ลด 3 → 2 → 0 ก่อน RS หายไป ต่างจาก background ที่ RS หายทันทีแล้ว Pod ค่อยหายตาม กด `Ctrl+C` ที่ terminal 2

### ขั้นที่ 4: เก็บกวาด namespace rs-lab

```bash
time kubectl delete ns rs-lab; kubectl get ns
```

```text
namespace "rs-lab" deleted

real	0m6.105s
...
NAME                 STATUS   AGE
default              Active   6m51s
kube-node-lease      Active   6m51s
kube-public          Active   6m51s
kube-system          Active   6m51s
local-path-storage   Active   6m47s
```

### สิ่งที่เห็น

- `--cascade=orphan` ลบเฉพาะ RS Pod อยู่ต่อแบบไม่มีเจ้าของ และ RS ใหม่ที่ selector ตรงรับเลี้ยงโดยไม่สร้างเพิ่ม (uid ใหม่)
- `--cascade=foreground` RS ค้างพร้อม finalizer `foregroundDeletion` จน Pod หายหมด

> **🤔 คำถามชวนคิด:** ถ้าต้องการเปลี่ยนชื่อ RS จาก `snack-rs` เป็น `snack` โดยร้านไม่ปิดแม้แต่วินาทีเดียว จะใช้ขั้นตอนไหนของ LAB นี้

**เก็บกวาด:** ลบ namespace `rs-lab` แล้วในขั้นที่ 4

---

## LAB 7: ReplicaSet กับ quota, LimitRange และ PSA

<p align="center" id="fig-9">
  <img src="images/09-lab7-quota.png" alt="รูปที่ 9 LAB 7 quota, LimitRange, PSA" width="900"><br>
  <em><b>รูปที่ 9</b> LAB7: namespace rs-quota มี quota pods=4 + LimitRange → RS replicas 6 ได้แค่ 4, Events FailedCreate exceeded quota, condition ReplicaFailure; เพิ่ม quota แล้ว RS สร้างต่อเอง (อาจรอราว 1 นาทีหลังเพิ่มโควตา เพราะ backoff); ทางเลือก PSA enforce ให้ RS สร้างได้แต่ Pod ถูกปฏิเสธ</em>
</p>

**เป้าหมาย:** เห็นว่า ResourceQuota และ Pod Security Admission (บทที่ 4) ตรวจที่ **Pod** ที่ RS สร้าง ไม่ใช่ตัว RS และอ่าน condition/event ของ RS ที่สร้าง Pod ไม่ครบ

**ไฟล์:** `labs/lab07-quota/00-ns-quota.yaml` (namespace `rs-quota` + ResourceQuota `rs-quota` `pods: "4"` + LimitRange `box-size` defaultRequest 100m/64Mi default 200m/128Mi), `quota-rs.yaml` (replicas 6 ไม่ระบุ resources), `psa-rs.yaml` (namespace `rs-psa` enforce+warn `restricted` + RS ไม่มี securityContext)

#### อธิบาย YAML: `labs/lab07-quota/00-ns-quota.yaml` และ `quota-rs.yaml`

```yaml
# LAB 7: โซน rs-quota + ใบงบ (ResourceQuota) จำกัด 4 Pod + ป้ายขนาดกล่อง (LimitRange) แบบบท 004
apiVersion: v1
kind: Namespace   # โซนของ LAB 7
metadata:
  name: rs-quota
---
apiVersion: v1
kind: ResourceQuota   # ใบงบรวมของทั้ง namespace
metadata:
  name: rs-quota
  namespace: rs-quota
spec:
  hard:
    pods: "4"                    # Pod ได้ไม่เกิน 4 ตัว (ตรวจตอนสร้าง "Pod" ไม่ใช่ตอนสร้าง RS)
---
apiVersion: v1
kind: LimitRange   # ค่าตั้งต้น/เพดานต่อ container
metadata:
  name: box-size
  namespace: rs-quota
spec:
  limits:
    - type: Container   # ใช้กับทุก container ใน namespace นี้
      defaultRequest: { cpu: 100m, memory: 64Mi }   # ไม่ระบุ requests → เติมค่านี้
      default:        { cpu: 200m, memory: 128Mi }  # ไม่ระบุ limits → เติมค่านี้
      max:            { cpu: 500m, memory: 256Mi }   # เกินเพดานนี้ → Pod ถูกปฏิเสธ
```

```yaml
# LAB 7: ขอ 6 บูธ แต่ใบงบให้ 4 Pod → RS สร้างได้ 4 ตัว ที่เหลือ FailedCreate
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: quota-rs
  namespace: rs-quota
spec:
  replicas: 6   # ขอ 6 แต่ quota ให้ 4 → DESIRED 6 CURRENT 4
  selector:
    matchLabels:
      app: quota   # selector
  template:
    metadata:
      labels:
        app: quota
    spec:
      terminationGracePeriodSeconds: 1
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
          # ไม่ระบุ resources → LimitRange เติมค่า default ให้
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| ไฟล์เดียวหลายเอกสาร (`---`) | สร้าง namespace, quota, LimitRange ในคำสั่งเดียว เรียง namespace ไว้ก่อน | `namespace/rs-quota created`, `resourcequota/...`, `limitrange/...` |
| `ResourceQuota spec.hard.pods: "4"` | จำกัดจำนวน Pod ทั้ง namespace ตรวจที่ admission ตอนสร้าง **Pod** (ตัว RS ไม่ใช่ Pod จึงสร้างได้) | `quota-rs 6 4 4`, `exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4` |
| `LimitRange type: Container` + `defaultRequest`/`default` | เติม requests/limits ให้ container ที่ไม่ได้ระบุ | ขั้นที่ 2 Pod ได้ `requests 100m/64Mi`, `limits 200m/128Mi` |
| `LimitRange max` | เพดานต่อ container (ค่า default ไม่เกินเพดานจึงผ่าน) | – |
| `quota-rs replicas: 6` | ตั้งใจขอเกินงบ 2 ตัว | DESIRED 6 CURRENT 4, `ReplicaFailure True FailedCreate` |
| template ไม่มี `resources` | ให้เห็นว่า LimitRange ทำงานกับ Pod ที่ RS สร้าง | ผลขั้นที่ 2 |

### ขั้นที่ 1: ขอ 6 บูธในโซนที่ให้ 4

```bash
kubectl apply -f labs/lab07-quota/00-ns-quota.yaml
kubectl apply -f labs/lab07-quota/quota-rs.yaml; sleep 5; kubectl get rs,pods -n rs-quota
```

```text
namespace/rs-quota created
resourcequota/rs-quota created
limitrange/box-size created
replicaset.apps/quota-rs created
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/quota-rs   6         4         4       5s

NAME                 READY   STATUS    RESTARTS   AGE
pod/quota-rs-2hgc5   1/1     Running   0          5s
pod/quota-rs-d2pdv   1/1     Running   0          5s
pod/quota-rs-nxp7t   1/1     Running   0          5s
pod/quota-rs-tk4jh   1/1     Running   0          5s
```

`apply` สำเร็จทุกบรรทัด แต่ `DESIRED 6 CURRENT 4` ดูสาเหตุ

```bash
kubectl describe rs quota-rs -n rs-quota | sed -n "/Conditions/,\$p"
kubectl get rs quota-rs -n rs-quota -o jsonpath='{.status.conditions}{"\n"}'
kubectl describe quota -n rs-quota
```

```text
Conditions:
  Type             Status  Reason
  ----             ------  ------
  ReplicaFailure   True    FailedCreate
Events:
  Type     Reason            Age               From                   Message
  ----     ------            ----              ----                   -------
  Normal   SuccessfulCreate  5s                replicaset-controller  Created pod: quota-rs-tk4jh
  Normal   SuccessfulCreate  5s                replicaset-controller  Created pod: quota-rs-nxp7t
  Normal   SuccessfulCreate  5s                replicaset-controller  Created pod: quota-rs-d2pdv
  Warning  FailedCreate      5s                replicaset-controller  Error creating: pods "quota-rs-qwbzx" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4
  Warning  FailedCreate      5s                replicaset-controller  Error creating: pods "quota-rs-j4jrj" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4
  Normal   SuccessfulCreate  5s                replicaset-controller  Created pod: quota-rs-2hgc5
...
  Warning  FailedCreate      3s (x12 over 5s)  replicaset-controller  (combined from similar events): Error creating: pods "quota-rs-kmc84" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4
[{"lastTransitionTime":"2026-10-05T10:15:43Z","message":"pods \"quota-rs-qwbzx\" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4","reason":"FailedCreate","status":"True","type":"ReplicaFailure"}]
Name:       rs-quota
Namespace:  rs-quota
Resource    Used  Hard
--------    ----  ----
pods        4     4
```

- condition `ReplicaFailure=True` reason `FailedCreate` บอกว่า RS สร้าง Pod ไม่ได้
- event `exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4` เป็นข้อความเดียวกับบทที่ 4 แต่คราวนี้ผู้ถูกปฏิเสธคือ RS ไม่ใช่เรา
- RS พยายามซ้ำหลายครั้งในไม่กี่วินาที (ในการทดลอง `x12 over 5s` ตัวเลขในเครื่องนักศึกษาอาจต่าง) แล้วค่อย ๆ เว้นระยะห่างขึ้น (backoff)

### ขั้นที่ 2: LimitRange เติมขนาดให้ Pod ของ RS

```bash
P=$(kubectl get pods -n rs-quota -o jsonpath='{.items[0].metadata.name}')
kubectl get pod $P -n rs-quota -o jsonpath='{.spec.containers[0].resources}{"\n"}'
```

```text
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
```

template ไม่มี `resources` แต่ Pod ทุกตัวที่ RS สร้างได้ค่าตั้งต้นจาก LimitRange `box-size`

### ขั้นที่ 3: เพิ่ม quota แล้วรอ

🐧 **terminal 2** (ทางเลือก) `kubectl get rs quota-rs -n rs-quota -w` 🐧 **terminal 1**

```bash
date +%T; kubectl patch resourcequota rs-quota -n rs-quota -p '{"spec":{"hard":{"pods":"6"}}}'
T0=$(date +%s); until [ "$(kubectl get rs quota-rs -n rs-quota -o jsonpath='{.status.readyReplicas}')" = 6 ]; do sleep 1; done; echo "ครบ 6 หลัง patch $(( $(date +%s)-T0 )) วิ"
kubectl get rs,pods -n rs-quota; kubectl get rs quota-rs -n rs-quota -o jsonpath='conditions={.status.conditions}{"\n"}'
```

```text
17:15:49
resourcequota/rs-quota patched
ครบ 6 หลัง patch 58 วิ
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/quota-rs   6         6         6       64s

NAME                 READY   STATUS    RESTARTS   AGE
pod/quota-rs-2hgc5   1/1     Running   0          64s
pod/quota-rs-d2pdv   1/1     Running   0          64s
pod/quota-rs-nxp7t   1/1     Running   0          64s
pod/quota-rs-tk4jh   1/1     Running   0          64s
pod/quota-rs-v9ntk   1/1     Running   0          2s
pod/quota-rs-zmjqz   1/1     Running   0          2s
conditions=
```

terminal 2

```text
NAME       DESIRED   CURRENT   READY   AGE
quota-rs   6         4         4       5s
quota-rs   6         4         4       62s
quota-rs   6         6         4       62s
quota-rs   6         6         5       63s
quota-rs   6         6         6       63s
```

ไม่ต้องสั่งอะไร RS เพิ่ม แต่ต้อง **รอ** ราว 45–65 วินาทีหลัง patch (backoff ของ controller; ในการทดลองนี้ใช้ 58 วินาที) RS จึงสร้างอีก 2 ตัว และ condition `ReplicaFailure` หายไปเอง (`conditions=` ว่าง) ในเครื่องนักศึกษาเวลาอาจต่าง ถ้ารอเกินราว 1 นาทีแล้วยังไม่ครบให้ดู `kubectl describe rs quota-rs -n rs-quota`

### ขั้นที่ 4 (ทางเลือก): PSA enforce

```bash
kubectl apply -f labs/lab07-quota/psa-rs.yaml; sleep 4; kubectl get rs,pods -n rs-psa
kubectl describe rs psa-rs -n rs-psa | sed -n "/Conditions/,\$p" | head -8
```

```text
namespace/rs-psa created
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "app" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "app" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "app" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
replicaset.apps/psa-rs created
NAME                     DESIRED   CURRENT   READY   AGE
replicaset.apps/psa-rs   3         0         0       4s
Conditions:
  Type             Status  Reason
  ----             ------  ------
  ReplicaFailure   True    FailedCreate
Events:
  Type     Reason        Age   From                   Message
  ----     ------        ----  ----                   -------
  Warning  FailedCreate  4s    replicaset-controller  Error creating: pods "psa-rs-rp28p" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "app" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "app" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "app" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

ตอนสร้าง RS ได้แค่ `Warning: would violate ...` (จากโหมด `warn` ที่ตรวจ Pod template ของ workload) แล้ว `replicaset.apps/psa-rs created` แต่โหมด `enforce` ปฏิเสธ **Pod ทุกตัว** RS จึงเป็น `3 0 0` ร้านมี 0 บูธ

#### อธิบาย YAML: `labs/lab07-quota/psa-rs.yaml`

```yaml
# LAB 7 (ทางเลือก): โซนบังคับ Pod Security ระดับ restricted + RS ที่ template ไม่มี securityContext
apiVersion: v1
kind: Namespace
metadata:
  name: rs-psa
  labels:
    pod-security.kubernetes.io/enforce: restricted   # Pod ไม่ผ่าน → ปฏิเสธ
    pod-security.kubernetes.io/warn: restricted      # เตือนที่ kubectl (ตรวจ template ของ RS ด้วย)
---
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: psa-rs
  namespace: rs-psa
spec:
  replicas: 3   # ขอ 3 แต่ Pod ถูกปฏิเสธทุกตัว → 3 0 0
  selector:
    matchLabels:
      app: psa
  template:
    metadata:
      labels:
        app: psa
    spec:
      terminationGracePeriodSeconds: 1
      containers:   # ไม่มี securityContext → ไม่ผ่านระดับ restricted
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| label `pod-security.kubernetes.io/enforce: restricted` | admission ปฏิเสธ **Pod** ที่ไม่ผ่านระดับ restricted (ตัว RS ไม่ใช่ Pod จึงไม่ถูกปฏิเสธ) | Events `FailedCreate ... violates PodSecurity "restricted:latest"` และ `3 0 0` |
| label `pod-security.kubernetes.io/warn: restricted` | เตือนกลับมาที่ kubectl ตอน apply และตรวจ Pod template ใน workload อย่าง RS ด้วย | `Warning: would violate PodSecurity ...` ก่อน `replicaset.apps/psa-rs created` |
| template ไม่มี `securityContext` | ขาดทั้ง 4 ข้อของ restricted (`allowPrivilegeEscalation`, `capabilities.drop`, `runAsNonRoot`, `seccompProfile`) | ข้อความเตือนและ error ระบุครบ 4 ข้อ |
| `replicas: 3` | RS พยายามสร้างตลอด แต่ถูกปฏิเสธทุกครั้ง | `ReplicaFailure True FailedCreate` |

### ขั้นที่ 5: เก็บกวาด

```bash
kubectl delete ns rs-quota rs-psa
```

```text
namespace "rs-quota" deleted
namespace "rs-psa" deleted
```

(ถ้าข้ามขั้นที่ 4 จะมีข้อความ `namespaces "rs-psa" not found` ซึ่งไม่เป็นไร)

### สิ่งที่เห็น

- quota นับที่ Pod: RS ถูกสร้างได้แต่ได้ Pod แค่ 4 จาก 6 เห็นได้จาก `DESIRED/CURRENT` และ `ReplicaFailure`/`FailedCreate`
- LimitRange เติม requests/limits ให้ Pod ที่ RS สร้าง
- เพิ่ม quota แล้ว RS สร้างต่อเองหลัง backoff (ราว 45–65 วินาที ในการทดลอง 58 วินาที)
- PSA enforce: RS สร้างได้พร้อม Warning แต่ Pod ถูกปฏิเสธทั้งหมด (`3 0 0`)

> **🤔 คำถามชวนคิด:** ในงานจริง ถ้ามีคนแจ้งว่า "deploy แล้วไม่มี error แต่แอปไม่ขึ้น" ควรดูคำสั่งอะไรเป็นอันดับแรก และจะเห็นคำว่าอะไร

**เก็บกวาด:** ลบ namespace แล้วในขั้นที่ 5

---

## LAB 8: กระจาย replica ด้วย anti-affinity และ topology spread

<p align="center" id="fig-10">
  <img src="images/10-lab8-spread.png" alt="รูปที่ 10 LAB 8 กระจาย replica" width="900"><br>
  <em><b>รูปที่ 10</b> LAB8: required anti-affinity + replicas 3 บน worker 2 ลำ → 1 Pending; เปลี่ยนเป็น preferred → 2+1; topologySpreadConstraints maxSkew 1 ได้ 2+2 → scale 5 ได้ 2+3 เมื่อใส่ nodeTaintsPolicy: Honor (ไม่ใส่ จะนับ control-plane แล้วค้าง Pending)</em>
</p>

**เป้าหมาย:** ใช้กฎการจัดวางของบทที่ 3 กับ replicas ของ RS เห็นข้อจำกัดของ required anti-affinity เมื่อเรือมีน้อยกว่าจำนวน Pod และใช้ preferred/topologySpreadConstraints แทน

**ไฟล์:** `labs/lab08-spread/` (`00-ns.yaml`, `spread-required.yaml`, `spread-preferred.yaml`, `spread-topology.yaml` — ส่วนสำคัญอยู่ใน [ทฤษฎีหัวข้อ 11](../01_Theory/README.md#11-replicaset-กับการจัดวาง-anti-affinity-และ-topology-spread))

#### อธิบาย YAML: `labs/lab08-spread/00-ns.yaml`

ทั้ง 3 ไฟล์ RS ของ LAB นี้ใช้โครงเดียวกับ snack-rs (busybox `sleep 3600`, `terminationGracePeriodSeconds: 1`, resources 10m/16Mi–50m/32Mi) ต่างกันที่กฎการจัดวางใน template (อธิบายในแต่ละขั้นด้านล่าง) ส่วน `00-ns.yaml` สร้างแค่ namespace `rs-spread` ให้ทุกขั้นใช้ร่วมกัน และลบทีเดียวในขั้นที่ 5

```yaml
# LAB 8: โซนฝึกกระจายบูธข้ามเรือ
apiVersion: v1
kind: Namespace   # โซนของ LAB 8 (ลบทีเดียวตอนจบ)
metadata:
  name: rs-spread
```

### ขั้นที่ 1: required anti-affinity กับ 3 บูธบน 2 เรือ

#### อธิบาย YAML: `labs/lab08-spread/spread-required.yaml` (ส่วนสำคัญ)

```yaml
spec:
  replicas: 3   # 3 บูธ แต่ worker มีแค่ 2 ลำ
  selector:
    matchLabels:
      app: spread-req
  template:
    metadata:
      labels:
        app: spread-req
    spec:
      terminationGracePeriodSeconds: 1
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:   # บังคับ: ทำตามไม่ได้ = ไม่วาง (Pending)
            - labelSelector:
                matchLabels:
                  app: spread-req   # ห้ามอยู่เรือเดียวกับ Pod ป้ายนี้ (รวมพวกเดียวกันเอง)
              topologyKey: kubernetes.io/hostname   # 1 เรือ = 1 โดเมน
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `requiredDuringSchedulingIgnoredDuringExecution` | กฎ **บังคับ** ตอน scheduler วาง Pod (Pod ที่รันอยู่แล้วไม่ถูกไล่ภายหลัง) | บูธที่ 3 `Pending` |
| `labelSelector app: spread-req` | ห้ามอยู่เรือเดียวกับ Pod ที่มีป้ายนี้ ซึ่งก็คือบูธพวกเดียวกันเอง | `2 node(s) didn't match pod anti-affinity rules` |
| `topologyKey: kubernetes.io/hostname` | ใช้ชื่อ Node เป็นโดเมน = เรือละ 1 บูธ | worker 2 ลำรับได้ 2 บูธ |
| `replicas: 3` | มากกว่าจำนวน worker (control-plane มี taint) | `3 3 2` และ `1 node(s) had untolerated taint(s)` |

```bash
kubectl apply -f labs/lab08-spread/00-ns.yaml -f labs/lab08-spread/spread-required.yaml; sleep 6
kubectl get rs,pods -n rs-spread -o wide
P=$(kubectl get pods -n rs-spread --field-selector status.phase=Pending -o jsonpath="{.items[0].metadata.name}")
kubectl describe pod $P -n rs-spread | sed -n "/Events/,\$p"
```

```text
namespace/rs-spread created
replicaset.apps/spread-req created
NAME                         DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR
replicaset.apps/spread-req   3         3         2       6s    app          busybox:1.36   app=spread-req

NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/spread-req-527qf   0/1     Pending   0          6s    <none>        <none>        <none>           <none>
pod/spread-req-h6jcl   1/1     Running   0          6s    10.244.2.18   lab-worker2   <none>           <none>
pod/spread-req-mvlv4   1/1     Running   0          6s    10.244.1.23   lab-worker    <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  6s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

worker 2 ลำรับได้ลำละ 1 บูธ control-plane มี taint บูธที่ 3 จึง `Pending` และ RS แสดง `3 3 2` (Pod ที่ Pending นับเป็น CURRENT แล้ว RS ไม่แก้อะไรให้)

### ขั้นที่ 2: preferred anti-affinity

#### อธิบาย YAML: `labs/lab08-spread/spread-preferred.yaml` (ส่วนสำคัญ)

```yaml
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:   # ขอร้อง: ทำตามไม่ได้ก็ยังวางได้
            - weight: 100   # น้ำหนักสูงสุด (1–100) ตอนให้คะแนน Node
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: spread-pref
                topologyKey: kubernetes.io/hostname   # 1 เรือ = 1 โดเมน
```

- `preferred...` เป็นแค่ "คะแนน" ที่ scheduler ใช้จัดอันดับ Node ไม่ใช่เงื่อนไขกรอง เมื่อ 2 บูธแรกแยกเรือแล้ว บูธที่ 3 ไม่มีเรือว่างให้ แต่ยังวางได้ → 2+1 ไม่มี Pending
- `weight: 100` ให้กฎนี้มีน้ำหนักสูงสุด แต่คะแนนจากปัจจัยอื่น (เช่น ทรัพยากรที่เหลือ) ยังมีผล เรือลำไหนได้ 2 บูธจึงไม่ตายตัว
- `podAffinityTerm` ใช้ `labelSelector` + `topologyKey` แบบเดียวกับ required (ซ้อนอยู่ใต้ `weight`)
- ส่วนอื่น (`replicas: 3`, selector/labels `app: spread-pref`) เหมือน spread-required

```bash
kubectl delete -f labs/lab08-spread/spread-required.yaml
kubectl apply -f labs/lab08-spread/spread-preferred.yaml; sleep 5; kubectl get pods -n rs-spread -o wide
```

```text
replicaset.apps "spread-req" deleted from rs-spread namespace
replicaset.apps/spread-pref created
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
spread-pref-5hkwt   1/1     Running   0          5s    10.244.1.24   lab-worker    <none>           <none>
spread-pref-m594p   1/1     Running   0          5s    10.244.2.20   lab-worker2   <none>           <none>
spread-pref-r2wh2   1/1     Running   0          5s    10.244.2.19   lab-worker2   <none>           <none>
```

ได้ 2+1 ไม่มี Pending ลองซ้ำอีก 4 รอบเพื่อดูว่าคงที่ไหม

```bash
for i in 1 2 3 4; do kubectl delete -f labs/lab08-spread/spread-preferred.yaml >/dev/null; sleep 3; kubectl apply -f labs/lab08-spread/spread-preferred.yaml >/dev/null; sleep 4; echo "รอบ $i: $(kubectl get pods -n rs-spread -l app=spread-pref --no-headers -o custom-columns=N:.spec.nodeName | sort | uniq -c | tr -s " " | tr "\n" ",")"; done
```

```text
รอบ 1:  1 lab-worker, 2 lab-worker2,
รอบ 2:  2 lab-worker, 1 lab-worker2,
รอบ 3:  1 lab-worker, 2 lab-worker2,
รอบ 4:  1 lab-worker, 2 lab-worker2,
```

ทั้ง 4 รอบได้ **2+1** (ไม่มี 3+0 และไม่มี Pending) แต่ **เรือลำที่ได้ 2 บูธสลับกันได้** ในการทดลองรอบ 2 เป็น `lab-worker` ที่ได้ 2 ส่วนรอบอื่นเป็น `lab-worker2` ในเครื่องนักศึกษาจะได้รูปแบบต่างจากนี้ก็ได้

### ขั้นที่ 3: topologySpreadConstraints

#### อธิบาย YAML: `labs/lab08-spread/spread-topology.yaml` (ส่วนสำคัญ)

```yaml
spec:
  replicas: 4   # 4 บูธ → 2+2 (ขั้นที่ 3 scale เป็น 5)
...
    spec:
      terminationGracePeriodSeconds: 1
      topologySpreadConstraints:
        - maxSkew: 1                           # ต่างกันได้ไม่เกิน 1 ตัว
          topologyKey: kubernetes.io/hostname   # นับต่อเรือ
          whenUnsatisfiable: DoNotSchedule     # ถ้าทำไม่ได้ → ไม่จัดลง (Pending)
          nodeTaintsPolicy: Honor              # ไม่นับ control-plane (มี taint) — บท 003 LAB 5
          labelSelector:   # นับเฉพาะ Pod ป้าย app=spread-topo
            matchLabels:
              app: spread-topo
```

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `maxSkew: 1` | จำนวนบูธของเรือที่มากสุดกับน้อยสุดต่างกันได้ไม่เกิน 1 | 4 บูธ → 2+2, 5 บูธ → 2+3 |
| `topologyKey: kubernetes.io/hostname` | นับแยกตาม Node (เรือ) | – |
| `whenUnsatisfiable: DoNotSchedule` | ถ้าวางแล้วเกิน maxSkew จะไม่วาง (Pending) แทนที่จะยอม | ขั้นที่ 4 ได้ Pending |
| `nodeTaintsPolicy: Honor` | ไม่นับ Node ที่ Pod ทนไม่ได้ (control-plane มี taint) เป็นโดเมน | มีบรรทัดนี้ → ไม่มี Pending, ตัดออก (ขั้นที่ 4) → Pending 2 ตัว คอมเมนต์ในไฟล์จึงเลี่ยงคำนี้ในบรรทัดอื่น เพราะ `grep -v` จะตัดทุกบรรทัดที่มีคำนี้ |
| `labelSelector app: spread-topo` | นับเฉพาะบูธของ RS นี้ | – |
| `replicas: 4` | จำนวนคู่ ให้เห็นการแบ่งเท่ากันพอดี แล้ว scale เป็น 5 | `2 lab-worker`, `3 lab-worker2` |

```bash
kubectl delete -f labs/lab08-spread/spread-preferred.yaml
kubectl apply -f labs/lab08-spread/spread-topology.yaml; sleep 5; kubectl get pods -n rs-spread -o wide
kubectl scale rs spread-topo -n rs-spread --replicas=5; sleep 4
kubectl get pods -n rs-spread --no-headers -o custom-columns=N:.spec.nodeName | sort | uniq -c
```

```text
replicaset.apps "spread-pref" deleted from rs-spread namespace
replicaset.apps/spread-topo created
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
spread-topo-b5667   1/1     Running   0          5s    10.244.1.30   lab-worker    <none>           <none>
spread-topo-f99ws   1/1     Running   0          5s    10.244.2.29   lab-worker2   <none>           <none>
spread-topo-fv6df   1/1     Running   0          5s    10.244.1.31   lab-worker    <none>           <none>
spread-topo-gwgw9   1/1     Running   0          5s    10.244.2.28   lab-worker2   <none>           <none>
replicaset.apps/spread-topo scaled
      2 lab-worker
      3 lab-worker2
```

4 บูธได้ 2+2 พอดี scale เป็น 5 ได้ 2+3 (ลำไหนได้ 3 ขึ้นกับ scheduler) ต่างกันไม่เกิน `maxSkew: 1`

### ขั้นที่ 4: ถ้าไม่มี nodeTaintsPolicy: Honor

ลองตัดบรรทัด `nodeTaintsPolicy` ออกด้วย `grep -v` แล้วส่งเข้า kubectl

```bash
kubectl delete -f labs/lab08-spread/spread-topology.yaml >/dev/null
grep -v nodeTaintsPolicy labs/lab08-spread/spread-topology.yaml | kubectl apply -f -; sleep 5; kubectl get pods -n rs-spread -o wide
P=$(kubectl get pods -n rs-spread --field-selector status.phase=Pending -o jsonpath='{.items[0].metadata.name}'); kubectl describe pod $P -n rs-spread | grep FailedScheduling
```

```text
replicaset.apps/spread-topo created
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
spread-topo-5tvkb   0/1     Pending   0          5s    <none>        <none>        <none>           <none>
spread-topo-ff6z7   1/1     Running   0          5s    10.244.1.32   lab-worker    <none>           <none>
spread-topo-k4g5t   1/1     Running   0          5s    10.244.2.31   lab-worker2   <none>           <none>
spread-topo-qnhmq   0/1     Pending   0          5s    <none>        <none>        <none>           <none>
  Warning  FailedScheduling  3s (x7 over 6s)  default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod topology spread constraints. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

ค่าเริ่มต้น `nodeTaintsPolicy: Ignore` นับ `lab-control-plane` (มี 0 Pod ตลอด) เป็นโดเมนด้วย เมื่อ worker มีลำละ 1 การวางเพิ่มจะทำให้ส่วนต่างเป็น 2 จึง Pending 2 ตัว (บทที่ 3 LAB 5 อธิบายไว้แล้ว)

### ขั้นที่ 5: เก็บกวาด

```bash
kubectl delete ns rs-spread
```

```text
namespace "rs-spread" deleted
```

### สิ่งที่เห็น

- required anti-affinity + replicas มากกว่าจำนวนเรือ → Pod เกินค้าง Pending (`didn't match pod anti-affinity rules`) RS ไม่แก้ให้
- preferred → 2+1 ทุกรอบ (เรือลำที่ได้ 2 สลับกันได้), topology spread (`maxSkew: 1` + `nodeTaintsPolicy: Honor`) → 2+2 และ 2+3
- ไม่มี `nodeTaintsPolicy: Honor` ใน kind → Pending เพราะนับ control-plane

> **🤔 คำถามชวนคิด:** ร้านน้องส้มใน LAB 9 ใช้ preferred anti-affinity ถ้าเปลี่ยนเป็น required แล้ว scale เป็น 5 บูธ จะได้กี่บูธที่ Running

**เก็บกวาด:** ลบ namespace แล้วในขั้นที่ 5

---

## LAB 9: LAB สุดท้าย: ร้านน้องส้ม 3 บูธด้วย ReplicaSet

<p align="center" id="fig-11">
  <img src="images/11-lab9-architecture.png" alt="รูปที่ 11 LAB 9 สถาปัตยกรรมร้าน 3 บูธ" width="900"><br>
  <em><b>รูปที่ 11</b> LAB9 สถาปัตยกรรม: namespace som-booths, ReplicaSet som-booth replicas 3, Pod template = ร้าน all-in-one ของบท 004 (web som-shop-web:1.1 + db sidecar postgres + emptyDir) ทุกบูธจึงมีฐานข้อมูลของตัวเอง</em>
</p>

**เป้าหมาย:** นำร้าน all-in-one ของบทที่ 4 มาเป็น **Pod template** ของ ReplicaSet `som-booth` 3 บูธ เปิดหน้าร้านทีละบูธ สั่งซื้อ ลบบูธ scale และเปลี่ยนรุ่น เพื่อเห็นทั้งสิ่งที่ ReplicaSet ทำได้ดี และ **3 ปัญหาที่ ReplicaSet แก้ไม่ได้** ซึ่งเป็นโจทย์ของบทที่ 6 และ 7

### 9.0 สถาปัตยกรรมและไฟล์

```text
เครื่องนักศึกษา  browser  http://localhost:8081 / 8082 / 8083
     │ ssh -p 2223 -L 8081:localhost:8081 -L 8082:localhost:8082 -L 8083:localhost:8083 root@localhost
k8s-lab   kubectl port-forward -n som-booths pod/<บูธที่ 1> 8081:3000   (บูธที่ 2 → 8082, บูธที่ 3 → 8083)
     │
namespace som-booths  (pod-security.kubernetes.io/warn=restricted)
  ReplicaSet som-booth  replicas 3  selector app=som-booth
   ├─ Pod som-booth-xxxxx  (lab-worker2)  web:3000 + db sidecar + emptyDir   ← ออเดอร์ของบูธนี้เท่านั้น
   ├─ Pod som-booth-yyyyy  (lab-worker2)  web + db + emptyDir
   └─ Pod som-booth-zzzzz  (lab-worker)   web + db + emptyDir                ← preferred anti-affinity → 2+1
```

| ไฟล์ | หน้าที่ |
|---|---|
| `som-booths/app/` | แอป Next.js + Dockerfile สำเนาจากบทที่ 4 (`som-shop-web:1.1` อ่านข้อความหัว/ท้ายหน้าจาก env `SHOP_EYEBROW`, `SHOP_FOOTER`) |
| `som-booths/k8s/00-namespace.yaml` | namespace `som-booths` label `team: som` และ `pod-security.kubernetes.io/warn: restricted` |
| `som-booths/k8s/som-booth.yaml` | ReplicaSet `som-booth` replicas 3 template = Pod ร้านของบทที่ 4 ทั้งก้อน (securityContext restricted, emptyDir `db-data`, native sidecar `db` postgres:17.11-alpine + probes, init `wait-for-db`, `db-seed`, container `web` + probes) |
| `som-booths/k8s/som-booth-promo.yaml` | เหมือน `som-booth.yaml` ทุกบรรทัด ยกเว้น image `som-shop-web:1.1-promo` (2 จุด) และข้อความ eyebrow โปร |

สิ่งที่ `som-booth.yaml` ต่างจาก `som-shop.yaml` ของบทที่ 4 คือห่อด้วย `kind: ReplicaSet` (template ไม่มี `name`) และเพิ่ม 2 อย่างใน template

```bash
cd /workspace/005_kubernetes_replicaset/02_LAB/som-booths
sed -n '1,40p' k8s/som-booth.yaml
grep -n -B1 -A3 "POD_NAME\|SHOP_EYEBROW\|SHOP_FOOTER" k8s/som-booth.yaml | head -30
```

#### อธิบาย YAML: `som-booths/k8s/som-booth.yaml` (ส่วนสำคัญ ตัดจากไฟล์จริง `...` = ส่วนที่ละไว้)

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: som-booth
  namespace: som-booths
  labels:
    app: som-booth
spec:
  replicas: 3                      # จำนวนบูธ
  selector:
    matchLabels:
      app: som-booth
  template:                        # แบบพิมพ์บูธ (ไม่มี name → ระบบตั้ง som-booth-xxxxx)
    metadata:
      labels:
        app: som-booth             # ต้องตรงกับ selector
    spec:
      securityContext:               # ระดับ Pod: ใช้กับทุก container
        runAsNonRoot: true           # ห้ามรันเป็น root
        fsGroup: 70                  # volume (emptyDir) เป็นของกลุ่ม 70 = postgres เขียนได้
        seccompProfile:
          type: RuntimeDefault

      affinity:                      # ขอร้อง (preferred) ให้บูธอยู่คนละเรือ ถ้าไม่ได้ก็ยอม (บท 003)
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: som-booth
                topologyKey: kubernetes.io/hostname   # กระจายตาม Node (เรือ)

      volumes:
        - name: db-data              # ฐานข้อมูลของ "บูธนี้" เท่านั้น หายเมื่อ Pod ถูกลบ
          emptyDir: {}

      initContainers:
        # 1) db: native sidecar (restartPolicy: Always) → เริ่มก่อนและรันตลอดอายุ Pod
        - name: db
          image: postgres:17.11-alpine
          restartPolicy: Always   # init container ที่ restartPolicy Always = native sidecar รันค้างคู่กับ web
...
          startupProbe:   # ให้ postgres เริ่มได้ถึง 2×30 = 60 วิ
...
          resources:
            requests: { cpu: 100m, memory: 256Mi }   # db: รวมกับ web ≈ 200m/448Mi ต่อบูธ (ขั้น 9.6)
            limits:   { cpu: 500m, memory: 512Mi }

        # 2) wait-for-db: รอจนต่อ db ได้
...
        # 3) db-seed: สร้างตาราง + สินค้าตั้งต้น
        - name: db-seed
          image: som-shop-web:1.1
          imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน Node
          command: ["node", "scripts/seed.mjs"]
...
      containers:
        - name: web
          image: som-shop-web:1.1
          imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน Node
...
          env:
            - name: POD_NAME           # Downward API: ชื่อ Pod (= ชื่อบูธ) ต้องประกาศก่อนตัวที่ใช้ $(POD_NAME)
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: SHOP_NAME
              value: "ร้านอาหารแมวน้องส้ม (หลายบูธ)"
            - name: SHOP_EYEBROW       # ข้อความเล็กเหนือชื่อร้าน → บอกว่าเป็นบูธไหน
              value: "⚓ บูธ $(POD_NAME)"
            - name: SHOP_FOOTER
              value: "Next.js + PostgreSQL · Kubernetes LAB 005 · ReplicaSet som-booth"
...
          ports:
            - containerPort: 3000   # port-forward pod/... 808x:3000 ชี้มาที่พอร์ตนี้
          readinessProbe:
            httpGet:
              path: /api/health   # บูธ Ready เมื่อ health ตอบ 200 → kubectl wait รอเงื่อนไขนี้
              port: 3000
...
          resources:
            requests: { cpu: 100m, memory: 192Mi }   # web
            limits:   { cpu: 500m, memory: 512Mi }
```

(ส่วนที่ละไว้คือ `securityContext` ราย container, env ของ postgres, `wait-for-db` ทั้งตัว, probes ที่เหลือ และ env `DATABASE_URL`/`PORT`/`HOSTNAME` ที่มีรหัส `meow1234` ซึ่งเป็นค่าตัวอย่างเพื่อการเรียน ดูทั้งไฟล์ด้วย `cat k8s/som-booth.yaml` และคำอธิบายราย field ของ Pod ร้านอยู่ใน LAB บทที่ 4)

สิ่งที่เพิ่มจาก Pod ร้านของบทที่ 4 มี 2 อย่าง

1. **env `POD_NAME`** จาก Downward API แล้วใช้ใน `SHOP_EYEBROW="⚓ บูธ $(POD_NAME)"` หน้าเว็บจึงบอกชื่อบูธ (ชื่อ Pod) ของตัวเอง (`$(VAR)` ขยายได้เฉพาะตัวแปรที่ประกาศ **ก่อน** ในรายการ env)
2. **preferred podAntiAffinity** กับ label `app=som-booth` เพื่อกระจายบูธข้ามเรือเท่าที่ทำได้ (แบบ LAB 8 ขั้นที่ 2 จึงได้ 2+1 และลำที่ได้ 2 สลับได้)

| field | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `kind: ReplicaSet`, `replicas: 3`, selector/labels `app: som-booth` | ห่อ Pod ร้านทั้งก้อนเป็น template ให้ RS ดูแล 3 บูธ | `som-booth 3 3 3` และชื่อ `som-booth-xxxxx` |
| `securityContext` (runAsNonRoot, seccompProfile, fsGroup 70) | ผ่านระดับ restricted ตั้งแต่บทที่ 4 และให้ postgres (gid 70) เขียน emptyDir ได้ | ไม่มี `Warning` ของ PSA ตอน apply |
| `volumes: db-data emptyDir` | ที่เก็บฐานข้อมูลอยู่กับ Pod หายเมื่อ Pod ถูกลบ ทุกบูธจึงมี db ของตัวเอง | ออเดอร์ไม่ตรงกัน (9.4) และบูธใหม่ออเดอร์ 0 (9.5) |
| init `db` + `restartPolicy: Always` | native sidecar: postgres เริ่มก่อนและรันคู่กับ web ตลอด | READY `2/2` (web + db) |
| init `wait-for-db`, `db-seed` | รอ db แล้วสร้างตาราง + สินค้า 6 รายการ | `Init:0/3 → 1/3 → 2/3`, log `seeded 6 products (new: 6)` ทุกบูธ |
| `imagePullPolicy: IfNotPresent` | ใช้ image ที่ `kind load` ไว้ ไม่ไปดึงจาก registry (ไม่มีใน registry) | ถ้าไม่ได้ทำ 9.1 จะค้าง `ErrImagePull` |
| `env POD_NAME` → `SHOP_EYEBROW` | หน้าเว็บแสดง `⚓ บูธ <ชื่อ Pod>` | `บูธ som-booth-h2v5v` ฯลฯ |
| `containerPort: 3000` | พอร์ตของ Next.js | `kubectl port-forward pod/... 8081:3000` |
| `readinessProbe /api/health` | บูธ Ready เมื่อเว็บต่อ db ได้ | `kubectl wait --for=condition=Ready` และเวลา "พร้อมครบ 3 บูธ" |
| `resources` (db 100m/256Mi + web 100m/192Mi) | บูธละราว 200m CPU / 448Mi | ข้อควรระวังตอน scale 5 (9.6) |

ทุกบูธยังมีฐานข้อมูล postgres อยู่ใน Pod ของตัวเอง (emptyDir) นี่คือที่มาของปัญหาข้อแรกที่จะเห็น

#### อธิบาย YAML: `som-booths/k8s/00-namespace.yaml`

```yaml
# LAB 9: โซนของร้านน้องส้มหลายบูธ — เตือน (warn) ถ้า Pod ไม่ผ่าน Pod Security ระดับ restricted (แบบบท 004)
apiVersion: v1
kind: Namespace
metadata:
  name: som-booths
  labels:
    team: som   # ป้ายบอกเจ้าของ (แบบบท 004)
    pod-security.kubernetes.io/warn: restricted   # แค่เตือน ไม่ปฏิเสธ (ไม่มี enforce)
```

- `warn: restricted` ทำให้ kubectl เตือนถ้า template ไม่ผ่านระดับ restricted แต่ไม่ปฏิเสธ (ต่างจาก `rs-psa` ใน LAB 7 ที่มี `enforce`) template ของ som-booth ผ่านอยู่แล้วจึงไม่มีคำเตือนเลย
- `team: som` เป็นป้ายบอกเจ้าของ namespace แบบบทที่ 4 ไม่มีผลต่อการทำงาน

### 9.1 เตรียม image ให้ทุก Node

<p align="center" id="fig-12">
  <img src="images/12-lab9-prepare-image.png" alt="รูปที่ 12 LAB 9 เตรียม image" width="900"><br>
  <em><b>รูปที่ 12</b> LAB9 เตรียม image: ถ้าคลัสเตอร์ใหม่ build som-shop-web:1.1 จากโฟลเดอร์ som-booths/app ของบทนี้ (สำเนาแอปจากบท 004) แล้ว kind load ให้ทุก Node, postgres ใช้ docker save --platform + kind load image-archive หรือให้ Node pull เอง</em>
</p>

🐧 **ใน SSH session ของ k8s-lab** ตรวจว่า Node มี image อยู่แล้วหรือยัง (ถ้าใช้คลัสเตอร์ต่อจากบทที่ 4 ที่เคย `kind load som-shop-web:1.1` และ postgres ไว้ จะเห็นทั้งสอง)

```bash
docker exec lab-worker crictl images | grep -E "som-shop-web|postgres" || echo "(ยังไม่มี image บน Node)"
```

```text
(ยังไม่มี image บน Node)
```

ถ้ายังไม่มี (คลัสเตอร์ใหม่) ให้ build แอปจากโฟลเดอร์ `som-booths/app` ของบทนี้แล้วโหลดเข้าทุก Node (ถ้ามีครบแล้วข้ามไปทำ `1.1-promo` ด้านล่าง)

```bash
cd /workspace/005_kubernetes_replicaset/02_LAB/som-booths/app
time docker build -q -t som-shop-web:1.1 . && docker images som-shop-web
time kind load docker-image som-shop-web:1.1 --name lab
```

```text
sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4

real	0m31.177s
...
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
som-shop-web:1.1   a706e5e4013b        305MB         76.6MB        
Image: "som-shop-web:1.1" with ID "sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.1" with ID "sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.1" with ID "sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4" not yet present on node "lab-worker", loading...

real	0m5.654s
```

(ครั้งแรกในเครื่องที่ยังไม่มี `node:22-alpine` อาจใช้หลายนาที **image ID เปลี่ยนทุกครั้งที่ build** และลำดับบรรทัด `not yet present on node ...` สลับกันได้ เป็นเรื่องปกติ) postgres เป็น image หลาย platform จึงใช้วิธีเดียวกับบทที่ 4

```bash
docker pull -q postgres:17.11-alpine
time (docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab)
```

```text
docker.io/library/postgres:17.11-alpine

real	0m6.284s
```

เตรียม image "รุ่นโปร" ไว้ใช้ในขั้น 9.7 เลย `1.1-promo` เป็นแค่ **tag ใหม่ของ image เดิม** (หน้าตาแอปเหมือนเดิม ต่างกันที่ข้อความ eyebrow ซึ่งมาจาก env ใน template ใหม่)

```bash
docker tag som-shop-web:1.1 som-shop-web:1.1-promo; docker images som-shop-web
time kind load docker-image som-shop-web:1.1-promo --name lab
docker exec lab-worker crictl images | grep -E "som-shop|postgres"
```

```text
IMAGE                    ID             DISK USAGE   CONTENT SIZE   EXTRA
som-shop-web:1.1         a706e5e4013b        305MB         76.6MB        
som-shop-web:1.1-promo   a706e5e4013b        305MB         76.6MB        
Image: "som-shop-web:1.1-promo" with ID "sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.1-promo" with ID "sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.1-promo" with ID "sha256:a706e5e4013bfb9e74812c99756ed1e063418123981f337c0f1d6fcac5ab25b4" not yet present on node "lab-worker", loading...

real	0m3.556s
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.1                  8290f900e21c7       76.6MB
docker.io/library/som-shop-web                  1.1-promo            8290f900e21c7       76.6MB
```

`crictl images` บนเรือต้องเห็นครบ 3 รายการ (`1.1` กับ `1.1-promo` มี ID เดียวกันเพราะเป็น image เดียวกัน และ ID ของ containerd ต่างจาก ID ของ docker ได้ เป็นเรื่องปกติ)

### 9.2 เปิดร้าน 3 บูธ

<p align="center" id="fig-13">
  <img src="images/13-lab9-three-booths-two-ships.png" alt="รูปที่ 13 LAB 9 3 บูธบน 2 เรือ" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9: apply แล้ว kubectl get pods -o wide เห็น 3 บูธกระจาย 2 เรือ (preferred anti-affinity → 2+1) แต่ละบูธชื่อไม่ซ้ำ</em>
</p>

🐧 **terminal 2** เฝ้าดู

```bash
kubectl get pods -n som-booths -o wide -w
```

(เปิดหลังสั่ง apply ในบล็อกถัดไปทันทีก็ได้) 🐧 **terminal 1**

```bash
cd /workspace/005_kubernetes_replicaset/02_LAB/som-booths
T0=$(date +%s); kubectl apply -f k8s/00-namespace.yaml -f k8s/som-booth.yaml
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=180s; echo "พร้อมครบ 3 บูธใน $(( $(date +%s)-T0 )) วิ"
kubectl get rs -n som-booths -o wide; kubectl get pods -n som-booths -o wide
```

```text
namespace/som-booths created
replicaset.apps/som-booth created
pod/som-booth-h2v5v condition met
pod/som-booth-wzxhk condition met
pod/som-booth-x5rqv condition met
พร้อมครบ 3 บูธใน 11 วิ
NAME        DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES             SELECTOR
som-booth   3         3         3       11s   web          som-shop-web:1.1   app=som-booth
NAME              READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-booth-h2v5v   2/2     Running   0          11s   10.244.2.32   lab-worker2   <none>           <none>
som-booth-wzxhk   2/2     Running   0          11s   10.244.1.33   lab-worker    <none>           <none>
som-booth-x5rqv   2/2     Running   0          11s   10.244.2.33   lab-worker2   <none>           <none>
```

terminal 2 เห็นแต่ละบูธผ่านขั้นตอนเดียวกับบทที่ 4 (ย่อ ตัดคอลัมน์ท้ายและบรรทัดซ้ำ)

```text
som-booth-h2v5v   0/2     Pending   0          0s    <none>   lab-worker2
som-booth-h2v5v   0/2     Init:0/3   0          1s    10.244.2.32   lab-worker2
som-booth-wzxhk   0/2     Init:1/3   0          7s    10.244.1.33   lab-worker
som-booth-wzxhk   1/2     Init:1/3   0          7s    10.244.1.33   lab-worker
som-booth-wzxhk   1/2     Init:2/3   0          8s    10.244.1.33   lab-worker
som-booth-wzxhk   1/2     PodInitializing   0          9s    10.244.1.33   lab-worker
som-booth-wzxhk   1/2     Running           0          9s    10.244.1.33   lab-worker
som-booth-wzxhk   2/2     Running           0          10s   10.244.1.33   lab-worker
```

- ไม่มี `Warning` ของ PSA ตอน apply เพราะ template ผ่าน restricted ตั้งแต่บทที่ 4
- RS `3 3 3` Pod ทุกตัว `2/2` (web + db sidecar) ใช้เวลาราว 8–11 วินาทีเมื่อ image อยู่บน Node แล้ว (ในการทดลองนี้ 11 วินาที) READY ขึ้น `1/2` ตั้งแต่ช่วง `Init:1/3` เพราะ db sidecar พร้อมแล้ว
- preferred anti-affinity กระจายเป็น 2+1 (ลำไหนได้ 2 ในเครื่องนักศึกษาอาจกลับกัน)

ตรวจว่าทุกบูธเตรียมฐานข้อมูลของตัวเอง

```bash
for p in $(kubectl get pods -n som-booths -l app=som-booth -o name); do echo "== $p"; kubectl logs -n som-booths $p -c db-seed; done
```

```text
== pod/som-booth-h2v5v
connected to database
tables ready: products, orders
seeded 6 products (new: 6)
== pod/som-booth-wzxhk
connected to database
tables ready: products, orders
seeded 6 products (new: 6)
== pod/som-booth-x5rqv
connected to database
tables ready: products, orders
seeded 6 products (new: 6)
```

ทุกบูธ `seeded 6 products (new: 6)` แปลว่าแต่ละบูธสร้างตารางและสินค้าตั้งต้นใน **ฐานข้อมูลของตัวเอง** (ไม่ได้ใช้ร่วมกัน)

### 9.3 เปิดหน้าร้านทีละบูธ

<p align="center" id="fig-14">
  <img src="images/14-lab9-port-forward-each.png" alt="รูปที่ 14 LAB 9 port-forward ทีละบูธ" width="900"><br>
  <em><b>รูปที่ 14</b> LAB9: ลูกค้าเข้าร้านได้ทีละบูธเท่านั้น: kubectl port-forward pod/&lt;ชื่อ&gt; 8081/8082/8083:3000 ใน k8s-lab แล้ว ssh -L จากเครื่องนักศึกษา เปิด 3 แท็บ</em>
</p>

ยังไม่มี "ที่อยู่ของร้าน" ที่รวมทุกบูธ ลูกค้าจึงต้องเข้าทีละบูธผ่าน port-forward ไปที่ Pod ตรง ๆ (บูธละ port)

**ขั้นที่ 1:** 🐧 **terminal 1** เก็บชื่อบูธไว้ในตัวแปร array `P` แล้วเปิด port-forward 3 ตัวไว้เบื้องหลัง

```bash
P=($(kubectl get pods -n som-booths -l app=som-booth -o jsonpath="{.items[*].metadata.name}")); echo ${P[@]}
kubectl port-forward -n som-booths pod/${P[0]} 8081:3000 > /tmp/pf-8081.log 2>&1 &
kubectl port-forward -n som-booths pod/${P[1]} 8082:3000 > /tmp/pf-8082.log 2>&1 &
kubectl port-forward -n som-booths pod/${P[2]} 8083:3000 > /tmp/pf-8083.log 2>&1 &
sleep 2; cat /tmp/pf-808*.log
pgrep -af "[k]ubectl port-forward"
for p in 8081 8082 8083; do curl -s localhost:$p | grep -o "บูธ som-booth-[a-z0-9]*" | head -1; done
```

```text
som-booth-h2v5v som-booth-wzxhk som-booth-x5rqv
Forwarding from 127.0.0.1:8081 -> 3000
Forwarding from [::1]:8081 -> 3000
Forwarding from 127.0.0.1:8082 -> 3000
Forwarding from [::1]:8082 -> 3000
Forwarding from 127.0.0.1:8083 -> 3000
Forwarding from [::1]:8083 -> 3000
34167 kubectl port-forward -n som-booths pod/som-booth-h2v5v 8081:3000
34168 kubectl port-forward -n som-booths pod/som-booth-wzxhk 8082:3000
34169 kubectl port-forward -n som-booths pod/som-booth-x5rqv 8083:3000
บูธ som-booth-h2v5v
บูธ som-booth-wzxhk
บูธ som-booth-x5rqv
```

แต่ละ port ไปคนละบูธ (เลข process หน้าคำสั่งในเครื่องนักศึกษาจะต่าง) หน้าเว็บบอกชื่อบูธของตัวเองที่ eyebrow (จาก `$(POD_NAME)`) ตรวจข้อความท้ายหน้าได้ด้วย

```bash
curl -s localhost:8081 | grep -o "<code>[^<]*</code>"; curl -s localhost:8081 | grep -o "Kubernetes LAB 005[^<]*" | head -1
```

```text
<code>som-booth-h2v5v</code>
Kubernetes LAB 005 · ReplicaSet som-booth
```

> `pgrep`/`pkill` ให้ใช้ pattern `"[k]ubectl port-forward"` เสมอ (วงเล็บกันไม่ให้ pattern ไปตรงกับ shell ที่พิมพ์คำสั่งนั้นเอง)

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ ต่อท่อ SSH 3 ท่อในคำสั่งเดียว (ถ้ามีหน้าต่าง `ssh -L` จากบทก่อนค้างอยู่ ให้ `exit` ก่อน) แล้วเปิดหน้าต่างนี้ทิ้งไว้จนจบ LAB

```bash
ssh -p 2223 -L 8081:localhost:8081 -L 8082:localhost:8082 -L 8083:localhost:8083 root@localhost
```

**ขั้นที่ 3:** 🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:8081**, **http://localhost:8082** และ **http://localhost:8083** คนละแท็บ ทุกแท็บเป็นร้าน `ร้านอาหารแมวน้องส้ม (หลายบูธ)` หน้าตาเหมือนกัน (image และ template เดียวกัน) ต่างกันที่ข้อความเล็ก `⚓ บูธ som-booth-xxxxx` ด้านบน และ `🐱 เสิร์ฟโดย Pod: som-booth-xxxxx` ด้านล่าง

### 9.4 สั่งซื้อแล้วออเดอร์ไม่ตรงกัน

<p align="center" id="fig-15">
  <img src="images/15-lab9-orders-mismatch.png" alt="รูปที่ 15 LAB 9 ออเดอร์ไม่ตรงกัน" width="900"><br>
  <em><b>รูปที่ 15</b> LAB9: สั่งซื้อที่บูธ a แล้วเปิดบูธ b/c → ออเดอร์ไม่ตรงกัน เพราะแต่ละบูธมี db ของตัวเอง</em>
</p>

🌐 กดปุ่ม **สั่งซื้อ** ที่แท็บ 8081 สองครั้ง แล้วรีเฟรชทั้ง 3 แท็บ หรือสั่งด้วย curl 🐧 ใน k8s-lab

```bash
for i in 1 2; do curl -s -X POST localhost:8081/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo; done
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
```

แอปนี้มี API แค่ `POST /api/orders` (สั่งซื้อ), `GET /api/products` และ `GET /api/health` **ไม่มี `GET /api/orders`**

```bash
curl -s -i localhost:8081/api/orders | head -1
```

```text
HTTP/1.1 405 Method Not Allowed
```

จึงตรวจจำนวนออเดอร์จากหน้าเว็บ (ช่อง "ออเดอร์ทั้งหมด") หรือดึงตัวเลขด้วย `grep` และดู stock ของสินค้า id 1 จาก `/api/products`

```bash
for p in 8081 8082 8083; do curl -s localhost:$p | grep -o '[0-9]*</span><span class="label">ออเดอร์ทั้งหมด'; done
for p in 8081 8082 8083; do echo "$p: $(curl -s localhost:$p/api/products | grep -o '"stock":[0-9]*' | head -1)"; done
```

```text
2</span><span class="label">ออเดอร์ทั้งหมด
0</span><span class="label">ออเดอร์ทั้งหมด
0</span><span class="label">ออเดอร์ทั้งหมด
8081: "stock":18
8082: "stock":20
8083: "stock":20
```

บูธ 8081 มี 2 ออเดอร์และ stock ลดเหลือ 18 แต่บูธ 8082/8083 ยัง **0 ออเดอร์ stock เต็ม 20** "ร้านเดียวกัน แต่มีสมุดออเดอร์ 3 เล่ม" ลูกค้าที่สั่งที่บูธหนึ่งแล้วไปถามอีกบูธจะไม่เจอออเดอร์ของตัวเอง

ภาพหน้าจอจริงด้านล่างมาจากการทดลองอีกรอบหนึ่ง (ชื่อบูธจึงต่างจากผล terminal ข้างบน) ที่สั่งซื้อบูธละไม่เท่ากัน คือ 1, 2 และ 3 ออเดอร์ (ตอนถ่ายภาพเปิดแต่ละบูธผ่าน NodePort Service ชั่วคราวที่เพิ่มเพื่อถ่ายภาพเท่านั้น หน้าเว็บเหมือนกับที่เปิดผ่าน port-forward ตามขั้นตอนข้างบน)

<p align="center" id="fig-16">
  <img src="images/screenshots/20261005_1725_lab005_01-booth1.png" alt="รูปที่ 16 ภาพหน้าจอจริง บูธที่ 1" width="700"><br>
  <em><b>รูปที่ 16</b> ภาพหน้าจอจริงจากการทดลอง: บูธแรก หัวเว็บ "⚓ บูธ som-booth-7btl6" สั่งซื้อไป 1 ครั้ง ช่องออเดอร์ทั้งหมดเป็น 1 และอาหารเม็ดสูตรปลาทูน่าเหลือ 19 ชิ้น</em>
</p>

<p align="center" id="fig-17">
  <img src="images/screenshots/20261005_1725_lab005_02-booth2.png" alt="รูปที่ 17 ภาพหน้าจอจริง บูธที่ 2" width="700"><br>
  <em><b>รูปที่ 17</b> ภาพหน้าจอจริงจากการทดลอง: บูธที่สอง "⚓ บูธ som-booth-fd5ct" (ReplicaSet เดียวกัน แบบพิมพ์เดียวกัน) แต่ออเดอร์ทั้งหมดเป็น 2 และอาหารเม็ดสูตรปลาทูน่าเหลือ 18 ชิ้น ไม่รวมออเดอร์ของบูธแรก</em>
</p>

<p align="center" id="fig-18">
  <img src="images/screenshots/20261005_1725_lab005_03-booth3.png" alt="รูปที่ 18 ภาพหน้าจอจริง บูธที่ 3" width="700"><br>
  <em><b>รูปที่ 18</b> ภาพหน้าจอจริงจากการทดลอง: บูธที่สาม "⚓ บูธ som-booth-gjzg7" ออเดอร์ทั้งหมด 3 อาหารเม็ดสูตรปลาทูน่าเหลือ 17 ชิ้น — ร้านเดียวกันแต่มีสมุดออเดอร์ 3 เล่ม เพราะแต่ละบูธมีฐานข้อมูล (emptyDir) ของตัวเอง</em>
</p>

### 9.5 ลบบูธ: บูธใหม่ ชื่อใหม่ ออเดอร์หาย port-forward หลุด

<p align="center" id="fig-19">
  <img src="images/16-lab9-delete-pod-data-lost.png" alt="รูปที่ 19 LAB 9 ลบบูธแล้วข้อมูลหาย" width="900"><br>
  <em><b>รูปที่ 19</b> LAB9: ลบ Pod บูธ a → RS สร้างบูธใหม่ ชื่อใหม่ IP ใหม่ ออเดอร์เป็น 0 (emptyDir หายพร้อม Pod) และ port-forward ที่ต่อบูธเดิมหลุด</em>
</p>

ลบบูธแรก (ที่ต่อกับ 8081 และมี 2 ออเดอร์) แล้วจับเวลาว่า RS สร้างบูธใหม่ให้พร้อมเมื่อไร

```bash
T0=$(date +%s); kubectl delete pod -n som-booths ${P[0]}
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s; echo "ครบ Ready หลังสั่งลบ $(( $(date +%s)-T0 )) วิ"
kubectl get pods -n som-booths -o wide
```

```text
pod "som-booth-h2v5v" deleted from som-booths namespace
pod/som-booth-d9fwm condition met
pod/som-booth-wzxhk condition met
pod/som-booth-x5rqv condition met
ครบ Ready หลังสั่งลบ 8 วิ
NAME              READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-booth-d9fwm   2/2     Running   0          8s    10.244.1.34   lab-worker    <none>           <none>
som-booth-wzxhk   2/2     Running   0          21s   10.244.1.33   lab-worker    <none>           <none>
som-booth-x5rqv   2/2     Running   0          21s   10.244.2.33   lab-worker2   <none>           <none>
```

ร้านกลับมาครบ 3 บูธในราว 7–11 วินาที (ในการทดลองนี้ 8 วินาที: db เริ่ม + seed + web พร้อม) บูธใหม่ `d9fwm` **ชื่อใหม่ IP ใหม่** และในการทดลองนี้ไปอยู่ `lab-worker` (ตัวเดิม `h2v5v` อยู่ `lab-worker2`) ในเครื่องนักศึกษาอาจได้เรือคนละลำกับตัวอย่าง

> ถ้าพิมพ์ `kubectl wait` ช้า อาจเห็นแค่บูธเดิม 2 ตัวที่ Ready อยู่แล้ว ให้ดู `kubectl get pods -w` ประกอบ

แล้ว port-forward 8081 ล่ะ

```bash
pgrep -af "[k]ubectl port-forward"
curl -s -o /dev/null -w "curl 8081 → http=%{http_code} exit=" localhost:8081; echo $?
sleep 1; tail -n 4 /tmp/pf-8081.log; pgrep -af "[k]ubectl port-forward"
```

```text
34167 kubectl port-forward -n som-booths pod/som-booth-h2v5v 8081:3000
34168 kubectl port-forward -n som-booths pod/som-booth-wzxhk 8082:3000
34169 kubectl port-forward -n som-booths pod/som-booth-x5rqv 8083:3000
curl 8081 → http=000 exit=52
Handling connection for 8081
Handling connection for 8081
E1005 17:19:33.401176   34167 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod 01427b172b7cbf730b49a103087daa5e24f836713bfdc18905b6857ae227516c, uid : network namespace for sandbox \"01427b172b7cbf730b49a103087daa5e24f836713bfdc18905b6857ae227516c\" is closed" localPort=8081 remotePort=3000
error: lost connection to pod
34168 kubectl port-forward -n som-booths pod/som-booth-wzxhk 8082:3000
34169 kubectl port-forward -n som-booths pod/som-booth-x5rqv 8083:3000
```

สิ่งที่น่าสนใจ: port-forward ไปบูธที่ถูกลบ **ยังดูเหมือนทำงานอยู่** (`pgrep` ยังเห็น) จนกระทั่งมีคนเข้ามา จึงได้ curl `exit=52` (empty reply) แล้ว port-forward จบพร้อม `error: lost connection to pod` ใน browser จะเห็น `ERR_CONNECTION_RESET` (เหมือนบทที่ 4) port-forward ผูกกับ **Pod ตัวนั้น** ไม่ได้ตามไปหาบูธใหม่

เปิด port-forward ใหม่ไปบูธใหม่ (Pod ที่สร้างล่าสุด) ที่ port 8081 เดิม

```bash
NEW=$(kubectl get pods -n som-booths -l app=som-booth --sort-by=.metadata.creationTimestamp -o jsonpath="{.items[-1].metadata.name}"); echo NEW=$NEW
kubectl port-forward -n som-booths pod/$NEW 8081:3000 > /tmp/pf-8081.log 2>&1 &
sleep 2; curl -s localhost:8081 | grep -o "บูธ som-booth-[a-z0-9]*" | head -1
curl -s localhost:8081 | grep -o "[0-9]*</span><span class=\"label\">ออเดอร์ทั้งหมด"
kubectl logs -n som-booths $NEW -c db-seed | tail -1
```

```text
NEW=som-booth-d9fwm
บูธ som-booth-d9fwm
0</span><span class="label">ออเดอร์ทั้งหมด
seeded 6 products (new: 6)
```

🌐 รีเฟรชแท็บ 8081 (ไม่ต้องเปิด `ssh -L` ใหม่ ท่อเดิมใช้ต่อได้) จะเป็นบูธชื่อใหม่ **ออเดอร์ 0** สองออเดอร์ที่ลูกค้าสั่งไว้หายไปพร้อม emptyDir ของบูธเดิม

<p align="center" id="fig-20">
  <img src="images/screenshots/20261005_0832_lab9rs_04-replacement-booth-0-orders.png" alt="รูปที่ 20 ภาพหน้าจอจริง บูธใหม่ออเดอร์ 0" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: หลังลบบูธ som-booth-rmcck ReplicaSet สร้างบูธใหม่ som-booth-z96mn ภายในราว 7 วินาที ร้านกลับมาครบ 3 บูธ แต่ออเดอร์ทั้งหมดเป็น 0 และสต็อกกลับเป็นค่าตั้งต้น เพราะฐานข้อมูลของบูธใหม่ว่างเปล่า (และต้องเปิด port-forward ใหม่เพราะตัวเดิมหลุด)</em>
</p>

รูปที่ 20 มาจากการทดลองอีกรอบหนึ่ง (คนละรอบกับรูปที่ 16–18) หลังลบบูธ `som-booth-rmcck` ผลคำสั่งจริงในรอบนั้น

```text
$ kubectl delete pod -n som-booths som-booth-rmcck
pod "som-booth-rmcck" deleted from som-booths namespace
$ kubectl get rs,pods -n som-booths -o wide
NAME                        DESIRED   CURRENT   READY   AGE    CONTAINERS   IMAGES             SELECTOR
replicaset.apps/som-booth   3         3         3       7m3s   web          som-shop-web:1.1   app=som-booth

NAME                  READY   STATUS    RESTARTS   AGE    IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-booth-gxx9d   2/2     Running   0          7m3s   10.244.3.39   lab-worker2   <none>           <none>
pod/som-booth-tdxr6   2/2     Running   0          7m3s   10.244.3.38   lab-worker2   <none>           <none>
pod/som-booth-z96mn   2/2     Running   0          7s     10.244.1.39   lab-worker    <none>           <none>
...
error: lost connection to pod
```

### 9.6 scale 3 → 5 → 2

<p align="center" id="fig-21">
  <img src="images/17-lab9-scale-3-5-2.png" alt="รูปที่ 21 LAB 9 scale 3→5→2" width="900"><br>
  <em><b>รูปที่ 21</b> LAB9: kubectl scale rs som-booth --replicas=5 แล้ว 2 — ดูว่าบูธไหนถูกปิด; 5 บูธแบ่ง 2+3 (ลำไหนได้ 3 ไม่แน่นอน) (ระวัง resource: 5 บูธขอราว 1 CPU / 2.2Gi ถ้า Pending ให้ใช้ 4 — ในเครื่องทดสอบไม่มี Pending)</em>
</p>

> **ระวังทรัพยากร:** บูธหนึ่งขอ requests ราว 200m CPU / 448Mi (db + web) 5 บูธจึงขอราว 1 CPU / 2.2Gi ในการทดลองไม่มีบูธ Pending แต่ถ้าเครื่องนักศึกษามี RAM น้อย (เช่น 8GB) แล้วมีบูธ `Pending` (`Insufficient memory`/`cpu`) หรือ k8s-lab ช้ามาก ให้ใช้ `--replicas=4` แทน

```bash
T0=$(date +%s); kubectl scale rs som-booth -n som-booths --replicas=5
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=180s >/dev/null; echo "5 บูธ Ready หลัง scale $(( $(date +%s)-T0 )) วิ"
kubectl get rs -n som-booths; kubectl get pods -n som-booths -o wide --sort-by=.metadata.creationTimestamp
kubectl describe node lab-worker | grep -A5 "Allocated resources"; kubectl describe node lab-worker2 | grep -A5 "Allocated resources"
```

```text
replicaset.apps/som-booth scaled
5 บูธ Ready หลัง scale 8 วิ
NAME        DESIRED   CURRENT   READY   AGE
som-booth   5         5         5       32s
NAME              READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-booth-wzxhk   2/2     Running   0          32s   10.244.1.33   lab-worker    <none>           <none>
som-booth-x5rqv   2/2     Running   0          32s   10.244.2.33   lab-worker2   <none>           <none>
som-booth-d9fwm   2/2     Running   0          19s   10.244.1.34   lab-worker    <none>           <none>
som-booth-268jq   2/2     Running   0          8s    10.244.2.34   lab-worker2   <none>           <none>
som-booth-cnswk   2/2     Running   0          8s    10.244.2.35   lab-worker2   <none>           <none>
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                500m (1%)   2 (6%)
  memory             946Mi (1%)  2Gi (3%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests     Limits
  --------           --------     ------
  cpu                700m (2%)    3 (9%)
  memory             1394Mi (2%)  3Gi (4%)
```

5 บูธพร้อมใน 8 วินาที (ในเครื่องนักศึกษาอาจราว 7–11 วินาที; AGE ในตัวอย่างสั้นเพราะสคริปต์ทดลองทำขั้น 9.2–9.6 ต่อกันทันที ถ้าทำด้วยมือ AGE จะยาวกว่านี้) กระจาย 2+3 (ลำไหนได้ 3 ไม่แน่นอน) เปอร์เซ็นต์ในวงเล็บเทียบกับ allocatable ของ Node ซึ่งใน kind คือทรัพยากรของเครื่องทั้งเครื่อง ตัวเลขในเครื่องนักศึกษาจึงต่างกันมาก (ในการทดลอง หน่วยความจำที่ Node container ใช้จริงตอน 5 บูธอยู่ที่ราว 500 MiB ต่อ worker ดูของเครื่องตัวเองได้ด้วย `docker stats --no-stream`)

scale ลงเหลือ 2 แล้วดูว่าบูธไหนถูกปิด และ port-forward ไหนยังอยู่

```bash
pgrep -af "[k]ubectl port-forward"
kubectl scale rs som-booth -n som-booths --replicas=2; kubectl get events -n som-booths --field-selector reason=SuccessfulDelete
sleep 4; kubectl get pods -n som-booths -o wide
for p in 8081 8082 8083; do curl -s -o /dev/null -w "$p http=%{http_code}\n" localhost:$p; done
sleep 1; pgrep -af "[k]ubectl port-forward"
```

```text
34168 kubectl port-forward -n som-booths pod/som-booth-wzxhk 8082:3000
34169 kubectl port-forward -n som-booths pod/som-booth-x5rqv 8083:3000
34923 kubectl port-forward -n som-booths pod/som-booth-d9fwm 8081:3000
replicaset.apps/som-booth scaled
LAST SEEN   TYPE     REASON             OBJECT                 MESSAGE
0s          Normal   SuccessfulDelete   replicaset/som-booth   Deleted pod: som-booth-d9fwm
0s          Normal   SuccessfulDelete   replicaset/som-booth   Deleted pod: som-booth-cnswk
0s          Normal   SuccessfulDelete   replicaset/som-booth   Deleted pod: som-booth-268jq
NAME              READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-booth-wzxhk   2/2     Running   0          36s   10.244.1.33   lab-worker    <none>           <none>
som-booth-x5rqv   2/2     Running   0          36s   10.244.2.33   lab-worker2   <none>           <none>
8081 http=000
8082 http=200
8083 http=200
34168 kubectl port-forward -n som-booths pod/som-booth-wzxhk 8082:3000
34169 kubectl port-forward -n som-booths pod/som-booth-x5rqv 8083:3000
```

RS ลบ `268jq` และ `cnswk` (ใหม่ทั้งคู่ บน `lab-worker2` ที่แออัด) กับ `d9fwm` (ใหม่กว่าบูธเดิมบน `lab-worker`) เหลือบูธเดิม 2 บูธ เรือละ 1 ตามเกณฑ์ในทฤษฎีหัวข้อ 5.2 และ port-forward 8081 ที่ต่อ `d9fwm` ตายอีกครั้ง (ในเครื่องนักศึกษาชื่อและเรืออาจต่าง ให้อธิบายจากเกณฑ์)

**ขั้นสำคัญก่อนไป 9.7:** scale กลับเป็น 3 (บูธที่เกิดใหม่ยังเป็นรุ่น 1.1 เพราะ template ยังเป็นของเดิม)

```bash
kubectl scale rs som-booth -n som-booths --replicas=3
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s >/dev/null
kubectl get pods -n som-booths -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName
```

```text
NAME              IMAGE              NODE
som-booth-72c8p   som-shop-web:1.1   lab-worker2
som-booth-wzxhk   som-shop-web:1.1   lab-worker
som-booth-x5rqv   som-shop-web:1.1   lab-worker2
```

(ผลข้างบนเป็นสภาพจริงในการทดลองเมื่อร้านกลับมามี 3 บูธรุ่น 1.1 ชื่อบูธที่ 3 และเรือที่มันไปอยู่ในเครื่องนักศึกษาจะต่าง) เหตุผลที่ต้อง scale กลับก่อนดูในกล่อง "ถ้าลืม scale กลับ" ของขั้น 9.7

### 9.7 template ใหม่ (รุ่นโปร): บูธเดิมไม่เปลี่ยน

<p align="center" id="fig-22">
  <img src="images/18-lab9-template-promo.png" alt="รูปที่ 22 LAB 9 template promo" width="900"><br>
  <em><b>รูปที่ 22</b> LAB9: scale กลับเป็น 3 ก่อน แล้วแก้ template เป็น som-shop-web:1.1-promo + ข้อความโปร แล้ว apply → บูธเดิมทั้ง 3 ยังเป็น 1.1 (template ใหม่ใช้กับบูธที่เกิดใหม่เท่านั้น; ถ้าไม่ scale กลับ apply จะคืน replicas=3 แล้วเกิดบูธ promo ทันที 1 ตัว)</em>
</p>

`som-booth-promo.yaml` ต่างจาก `som-booth.yaml` แค่ 3 บรรทัด

```bash
cd /workspace/005_kubernetes_replicaset/02_LAB/som-booths
diff k8s/som-booth.yaml k8s/som-booth-promo.yaml
```

```text
104c104
<           image: som-shop-web:1.1
---
>           image: som-shop-web:1.1-promo
122c122
<           image: som-shop-web:1.1
---
>           image: som-shop-web:1.1-promo
142c142
<               value: "⚓ บูธ $(POD_NAME)"
---
>               value: "🎉 โปรบูธใหม่ · $(POD_NAME)"
```

(บรรทัด 104 คือ image ของ init container `db-seed` บรรทัด 122 คือ image ของ `web` และ 142 คือ `SHOP_EYEBROW`)

#### อธิบาย YAML: `som-booths/k8s/som-booth-promo.yaml`

ไฟล์นี้เหมือน `som-booth.yaml` ทุกบรรทัด (รวมคอมเมนต์) ยกเว้น 3 บรรทัดตาม `diff` ข้างบน

| field ที่ต่าง | ทำอะไร / ทำไมตั้งแบบนี้ | โยงกับผลที่เห็น |
|---|---|---|
| `metadata.name: som-booth` (เหมือนเดิม) | เป็น RS ตัวเดิม `apply` จึง **แก้ template** ไม่ได้สร้าง RS ใหม่ | `replicaset.apps/som-booth configured` |
| `db-seed` `image: som-shop-web:1.1-promo` (บรรทัด 104) | init container ที่ seed ฐานข้อมูลใช้ image เดียวกับ web จึงต้องเปลี่ยนคู่กัน | – |
| `web` `image: som-shop-web:1.1-promo` (บรรทัด 122) | image ของหน้าร้าน (เป็น tag ใหม่ของ image เดิมที่เตรียมใน 9.1) | `get rs -o wide` IMAGES เป็น `1.1-promo` แต่ Pod เดิมยัง `1.1` |
| `SHOP_EYEBROW` = `"🎉 โปรบูธใหม่ · $(POD_NAME)"` (บรรทัด 142) | ข้อความหัวเว็บที่ต่างจากรุ่นเดิม ใช้แยกด้วยตาว่าบูธไหนเป็นรุ่นใหม่ | บูธเดิมยัง `⚓ บูธ ...` บูธที่เกิดใหม่ (9.8) เป็น `🎉 โปรบูธใหม่ · ...` |
| `spec.replicas: 3` (เหมือนเดิม) | ค่าในไฟล์จะทับค่าที่ scale ไว้ทุกครั้งที่ apply (LAB 3) | ถ้าลืม scale กลับเป็น 3 จะเกิดบูธ promo ทันที (กล่องด้านล่าง) |

คอมเมนต์ที่เพิ่มในทั้งสองไฟล์ใส่ไว้ท้ายบรรทัดอื่น ไม่แตะ 3 บรรทัดนี้ `diff` จึงยังแสดงแค่ 3 จุดเดิม

```bash
kubectl apply -f k8s/som-booth-promo.yaml; sleep 3
kubectl get rs som-booth -n som-booths -o wide
kubectl get pods -n som-booths -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName
curl -s localhost:8082 | grep -o "[⚓🎉][^<]*" | head -1
```

```text
replicaset.apps/som-booth configured
NAME        DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                   SELECTOR
som-booth   3         3         3       48s   web          som-shop-web:1.1-promo   app=som-booth
NAME              IMAGE              NODE
som-booth-72c8p   som-shop-web:1.1   lab-worker2
som-booth-wzxhk   som-shop-web:1.1   lab-worker
som-booth-x5rqv   som-shop-web:1.1   lab-worker2
⚓ บูธ som-booth-wzxhk
```

RS บอกว่า template เป็น `1.1-promo` แล้ว แต่ **บูธทั้ง 3 ยังเป็น `1.1`** และหน้าเว็บยังแสดง `⚓ บูธ ...` แบบเดิม (เหมือน LAB 5)

> **ถ้าลืม scale กลับ (ยังเป็น 2 บูธ):** ทดลองจริงแล้ว `kubectl apply -f k8s/som-booth-promo.yaml` จะคืน `replicas` เป็น 3 ตามไฟล์ด้วย RS จึงสร้างบูธที่ 3 จาก template ใหม่ทันที ได้ผลแบบนี้ (ผลจากการทดลองรอบก่อนหน้า ชื่อบูธจึงต่างจากผลข้างบน)
>
> ```text
> NAME        DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                   SELECTOR
> som-booth   3         3         2       3m45s   web          som-shop-web:1.1-promo   app=som-booth
> NAME              IMAGE                    NODE
> som-booth-6tq4x   som-shop-web:1.1-promo   lab-worker2
> som-booth-mdzn8   som-shop-web:1.1         lab-worker2
> som-booth-mf68c   som-shop-web:1.1         lab-worker
> ```
>
> ซึ่งเป็นตัวอย่างของกับดัก "apply ไฟล์ทับค่าที่ scale" จาก LAB 3 ถ้าเกิดแบบนี้และอยากทำตามเอกสารต่อ ให้ `kubectl apply -f k8s/som-booth.yaml` แล้วลบบูธ promo ตัวนั้นให้ RS สร้างคืนเป็นรุ่น 1.1 จากนั้น apply promo ใหม่

### 9.8 เปลี่ยนรุ่นทีละบูธด้วยมือ

<p align="center" id="fig-23">
  <img src="images/19-lab9-manual-replace.png" alt="รูปที่ 23 LAB 9 เปลี่ยนรุ่นทีละบูธด้วยมือ" width="900"><br>
  <em><b>รูปที่ 23</b> LAB9: ต้องลบ Pod ทีละตัวด้วยมือจึงได้บูธรุ่นโปร ระหว่างนั้นบูธที่ถูกลบปิดชั่วคราว ออเดอร์ของบูธนั้นหาย และต้อง port-forward ใหม่ทุกครั้ง</em>
</p>

วิธีเดียวที่ ReplicaSet มีให้คือ **ลบบูธเดิมทีละตัว** แล้วรอให้ตัวใหม่ (จาก template ใหม่) พร้อม ลบบูธแรก

```bash
OLD=som-booth-x5rqv        # ← เปลี่ยนเป็นชื่อบูธรุ่น 1.1 ตัวหนึ่งในเครื่องตัวเอง (ดูจาก custom-columns ในขั้น 9.7)
T0=$(date +%s); kubectl delete pod -n som-booths $OLD
kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s >/dev/null; echo "Ready หลังลบ $(( $(date +%s)-T0 )) วิ"
kubectl get pods -n som-booths -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName
pgrep -af "[k]ubectl port-forward"
```

```text
pod "som-booth-x5rqv" deleted from som-booths namespace
Ready หลังลบ 8 วิ
NAME              IMAGE                    NODE
som-booth-72c8p   som-shop-web:1.1         lab-worker2
som-booth-kgzj6   som-shop-web:1.1-promo   lab-worker
som-booth-wzxhk   som-shop-web:1.1         lab-worker
34168 kubectl port-forward -n som-booths pod/som-booth-wzxhk 8082:3000
34169 kubectl port-forward -n som-booths pod/som-booth-x5rqv 8083:3000
```

ในการทดลองลบ `som-booth-x5rqv` ซึ่งเป็นบูธที่ต่อกับ 8083 อยู่ port-forward 8083 จึง **ใช้ไม่ได้แล้ว แต่ `pgrep` ยังเห็น process อยู่** (เหมือนขั้น 9.5) process จะจบพร้อม `error: lost connection to pod` เมื่อมีคนพยายามเข้า `localhost:8083` ครั้งแรก เปิด port-forward ไปบูธใหม่ที่ port 8081 (port-forward 8081 เดิมจบไปแล้วตั้งแต่ขั้น 9.6 ถ้า `pgrep` ยังเห็น ให้ `pkill -f "[k]ubectl port-forward.* 8081:3000"` ก่อน) แล้วดูหน้าเว็บ

```bash
NEW=$(kubectl get pods -n som-booths -l app=som-booth --sort-by=.metadata.creationTimestamp -o jsonpath="{.items[-1].metadata.name}")
kubectl port-forward -n som-booths pod/$NEW 8081:3000 > /tmp/pf-8081.log 2>&1 &
sleep 2; curl -s localhost:8081 | grep -o "[⚓🎉][^<]*" | head -1
```

```text
🎉 โปรบูธใหม่ · som-booth-kgzj6
```

🌐 รีเฟรชแท็บ 8081 จะเห็นข้อความ `🎉 โปรบูธใหม่ · som-booth-...` ขณะที่บูธเดิมในแท็บ 8082 ยังเป็น `⚓ บูธ ...` (ร้านมี 2 รุ่นปนกัน) เปลี่ยนบูธที่เหลือทีละตัวด้วยลูป (ลบ → รอ Ready → ตัวถัดไป)

```bash
for old in $(kubectl get pods -n som-booths -l app=som-booth -o jsonpath='{range .items[?(@.spec.containers[0].image=="som-shop-web:1.1")]}{.metadata.name}{" "}{end}'); do
  T0=$(date +%s); kubectl delete pod -n som-booths $old
  kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s >/dev/null; echo "แทน $old เสร็จใน $(( $(date +%s)-T0 )) วิ"
done
kubectl get pods -n som-booths -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName
```

```text
pod "som-booth-72c8p" deleted from som-booths namespace
แทน som-booth-72c8p เสร็จใน 8 วิ
pod "som-booth-wzxhk" deleted from som-booths namespace
แทน som-booth-wzxhk เสร็จใน 8 วิ
NAME              IMAGE                    NODE
som-booth-dp9v5   som-shop-web:1.1-promo   lab-worker2
som-booth-g9cnr   som-shop-web:1.1-promo   lab-worker2
som-booth-kgzj6   som-shop-web:1.1-promo   lab-worker
```

ครบ 3 บูธรุ่นโปรแล้ว (แต่ละรอบใช้ราว 7–11 วินาที ในการทดลองนี้ 8 วินาที) แต่ลองนับสิ่งที่ต้องทำเอง

- ต้องเขียนลูปเอง ลบทีละตัวและ **รอเอง** ให้ตัวใหม่ Ready ก่อนลบตัวถัดไป (ถ้าสั่ง `kubectl delete pod -l app=som-booth` ร้านจะปิดทุกบูธพร้อมกัน)
- ออเดอร์ของบูธที่ถูกลบ **หายทุกครั้ง** และ port-forward ที่ต่อบูธนั้นต้องเปิดใหม่ทุกครั้ง
- ถ้ารุ่นโปรมีปัญหา การย้อนกลับ = apply `som-booth.yaml` แล้ววนลบทีละตัวอีกรอบ ไม่มีประวัติรุ่นให้เลือก

### 9.9 เก็บกวาด LAB 9

🐧 **ใน SSH session ของ k8s-lab**

```bash
pkill -f "[k]ubectl port-forward"; sleep 1; pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
time kubectl delete ns som-booths; kubectl get ns
```

```text
ไม่มี port-forward ค้าง
namespace "som-booths" deleted

real	0m10.898s
...
NAME                 STATUS   AGE
default              Active   11m
kube-node-lease      Active   11m
kube-public          Active   11m
kube-system          Active   11m
local-path-storage   Active   11m
```

(AGE ของ namespace ตั้งต้นขึ้นกับว่าสร้างคลัสเตอร์ไว้นานเท่าไร)

🖥️ **บนเครื่องนักศึกษา** พิมพ์ `exit` ในหน้าต่าง `ssh -L` image `som-shop-web:1.1`, `1.1-promo` และ postgres บน Node เก็บไว้ได้ (บทถัดไปใช้ต่อ)

### 9.10 สรุป LAB 9 และปัญหาที่ส่งต่อ

<p align="center" id="fig-24">
  <img src="images/20-lab9-wrap-up-handoff.png" alt="รูปที่ 24 สรุป LAB 9 และปัญหาส่งต่อ" width="900"><br>
  <em><b>รูปที่ 24</b> สรุป LAB9 และปัญหาส่งต่อ: (1) แต่ละบูธมี db ของตัวเอง ข้อมูลไม่ตรงกัน (2) ชื่อ/IP เปลี่ยน ต้อง port-forward ทีละ Pod → บท 006 Service (3) เปลี่ยนรุ่นต้องลบ Pod เอง → บท 007 Deployment</em>
</p>

**ReplicaSet ทำได้ดี:** ร้านมี 3 บูธเสมอ บูธหายก็ได้บูธใหม่ภายในราว 7–11 วินาที scale ขึ้นลงได้ทันที และกระจายบูธข้ามเรือได้

**ReplicaSet แก้ไม่ได้:**

| ปัญหาที่เห็นใน LAB 9 | หลักฐานจากการทดลอง | บทที่แก้ |
|---|---|---|
| 1. แต่ละบูธมีฐานข้อมูลของตัวเอง ออเดอร์ไม่ตรงกัน บูธใหม่เริ่มจาก 0 | 8081 ออเดอร์ 2 แต่ 8082/8083 ออเดอร์ 0, บูธใหม่ `d9fwm` ออเดอร์ 0 | บทที่ 6 แยกฐานข้อมูลออกมาให้ทุกบูธใช้ร่วมกัน |
| 2. ไม่มีที่อยู่คงที่ ต้อง port-forward ทีละ Pod และหลุดทุกครั้งที่บูธถูกแทนหรือถูก scale ลง | `error: lost connection to pod`, `8081 http=000` | บทที่ 6 **Service** |
| 3. เปลี่ยนรุ่นต้องลบ Pod เองทีละตัว รอเอง ย้อนรุ่นยาก | template promo แล้วบูธเดิมยัง 1.1 ทั้ง 3 จนลบเอง | บทที่ 7 **Deployment** |

### สิ่งที่เห็นใน LAB 9

- template ของ ReplicaSet = Pod ร้านทั้งก้อนของบทที่ 4 ได้ `3 3 3` บูธละ `2/2` กระจาย 2+1 ไม่มี Warning PSA
- หน้าเว็บบอกชื่อบูธจาก `$(POD_NAME)` และออเดอร์ของแต่ละบูธแยกกัน (`GET /api/orders` ไม่มี ใช้หน้าเว็บหรือ `/api/products` ตรวจ)
- ลบบูธ → บูธใหม่ชื่อใหม่ IP ใหม่ ออเดอร์ 0 ในราว 7–11 วินาที port-forward เดิม `lost connection to pod` (process ยังค้างใน `pgrep` จนกว่าจะมีคนเข้า)
- scale 5 (2+3) แล้ว 2 (เหลือเรือละ 1) port-forward ของบูธที่ถูกปิดตาย
- template promo ไม่เปลี่ยนบูธเดิม ต้องลบทีละตัว และต้อง scale กลับเป็น 3 ก่อน apply มิฉะนั้น apply จะคืน replicas และเกิดบูธ promo ทันที

### คำถามท้าย LAB 9

1. ทำไมออเดอร์ที่สั่งที่บูธ 8081 จึงไม่ปรากฏที่บูธ 8082 ทั้งที่เป็น ReplicaSet และ image เดียวกัน ถ้าจะให้ทุกบูธเห็นออเดอร์เดียวกันต้องเปลี่ยนโครงสร้างอย่างไร
2. หลังลบบูธ ทำไม port-forward 8081 ไม่ตามไปหาบูธใหม่เอง สิ่งที่ลูกค้าต้องการคือ "ที่อยู่" แบบไหน
3. ตอน scale 5 → 2 บูธไหนถูกปิด อธิบายด้วยเกณฑ์ในทฤษฎีหัวข้อ 5.2
4. ทำไมต้อง scale กลับเป็น 3 ก่อน `kubectl apply -f k8s/som-booth-promo.yaml` ถ้าไม่ทำจะเห็นอะไร
5. ถ้าร้านจริงมี 30 บูธ การเปลี่ยนรุ่นแบบขั้น 9.8 มีความเสี่ยงอะไรบ้าง และอยากได้เครื่องมือที่ทำอะไรให้อัตโนมัติ

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-booths/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 005_kubernetes_replicaset k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/005_kubernetes_replicaset/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (connection refused) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ ถ้าจะทำ LAB 9 ต้อง build/`kind load` image ใหม่ (ขั้น 9.1) |
| `Error from server (NotFound): namespaces "rs-lab" not found` | ข้าม LAB 0 หรือเก็บกวาดไปแล้ว | `kubectl apply -f labs/lab01-first-rs/00-ns.yaml` แล้วสร้าง snack-rs ใหม่ตาม LAB 1 |
| `` `selector` does not match template `labels` `` | label ใน template ไม่ผ่าน selector | แก้ให้ label ของ template มีทุก key/value ที่ selector ต้องการ |
| `spec.selector: Invalid value: ...: field is immutable` | แก้ selector ของ RS ที่มีอยู่แล้ว | สร้าง RS ใหม่ (ลบเดิมแบบ `--cascade=orphan` ถ้าไม่อยากให้ Pod หาย) |
| Pod ที่เพิ่งลบขึ้น `Error` ชั่วครู่ | busybox ไม่รับ SIGTERM ถูก kill หลัง grace 1 วินาที (exit 137) | ปกติ รอให้หายเอง |
| Pod ที่สร้างเองหายทันทีหลัง `created` | label ตรง selector ของ RS ที่ครบอยู่แล้ว RS ลบตัวเกิน | ใช้ label ที่ไม่ชนกับ workload (LAB 4 ข้อ ก) |
| LAB 4 ขั้นที่ 5 ได้ `P=snack-rs-b-...`, `owner=` ยังชี้ `snack-rs-b`, ไม่มีตัวแทนเกิด และ log เป็น `บูธของ snack-rs-b` | Pod ของ snack-rs-b ที่เพิ่งลบยังค้าง `Error` และเรียงชื่อก่อน (เลือกด้วย `items[0]`) | Pod ที่เลือกผิดเป็นของ snack-rs-b ที่กำลังถูกลบอยู่แล้ว ลบทิ้งได้เลย (`kubectl delete pod $P -n rs-lab`) แล้วทำขั้นที่ 5 ใหม่ด้วยคำสั่งที่กรอง OWNER เป็น `snack-rs` (หรือรอให้ `snack-rs-b-*` หายก่อน) |
| เห็น Pod `0/1 Error` หลัง scale ลงหรือหลังลบ RS | busybox ถูก kill หลัง grace period แล้วรอระบบเก็บ | ปกติ รอไม่กี่วินาทีจะหายเอง |
| Pod ขึ้น `Unknown` หลัง `docker start lab-worker2` (LAB 2 ขั้นที่ 5) | Pod เก่าบนเรือที่ล่ม กำลังถูกเก็บกวาด | ปกติ รอไม่กี่วินาทีจะหายเอง |
| RS สร้าง Pod น้อยกว่าที่คาด และมี Pod ชื่อแปลกเป็นสมาชิก | RS รับเลี้ยง Pod ไร้เจ้าของที่ label ตรง | ดู `kubectl get pods -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name` |
| `describe rs` ไม่มี event `SuccessfulDelete`/`SuccessfulCreate` ที่ควรมี | event ของ object นั้นเกินขีดจำกัด (spam filter) | ดู `kubectl get pods` / `get rs` เป็นหลัก หรือ `kubectl get events --field-selector reason=...` หรือเริ่ม RS ใหม่ |
| drain แล้วไม่มี Pod ถูก evict | ไม่มี Pod ของ snack-rs อยู่บนเรือนั้น | uncordon แล้ว `kubectl delete pod -n rs-lab -l app=snack` ให้กระจายใหม่ |
| หลัง LAB 2 `get nodes` ยังเป็น `SchedulingDisabled` หรือ `NotReady` | ลืม `uncordon` หรือ `docker start lab-worker2` | `kubectl uncordon lab-worker2` / 🐧 `docker start lab-worker2` |
| scale/edit แล้วจำนวนกลับเป็นค่าเดิม | มีการ `kubectl apply -f` ไฟล์ที่มี `replicas:` ทับ | แก้ `replicas` ในไฟล์ให้ตรงกับที่ต้องการ |
| LAB 4/6 ได้ 4 บูธแทน 3 | ลืม sed ไฟล์ `snack-rs.yaml` กลับเป็น 3 หลัง LAB 3 | `sed -i 's/replicas: 4 /replicas: 3 /' labs/lab01-first-rs/snack-rs.yaml` แล้ว apply |
| `kubectl edit` เปิด vi แล้วออกไม่เป็น | `EDITOR` ไม่ได้ตั้ง ค่าเริ่มต้นคือ vi | กด `Esc` พิมพ์ `:q!` Enter แล้วใช้ `KUBE_EDITOR=nano kubectl edit ...` |
| `wget: can't connect to remote host: Connection refused` ใน LAB 5 | ใช้ `localhost` (ไป `::1` ก่อน) แต่ nginx ฟังแค่ IPv4 | ใช้ `wget -qO- 127.0.0.1` |
| RS ค้าง `DESIRED 6 CURRENT 4` แม้เพิ่ม quota แล้ว | RS อยู่ในช่วง backoff | รอราว 45–65 วินาที (ในการทดลอง 58 วินาที) |
| `psa-rs 3 0 0` | enforce restricted ปฏิเสธ Pod | อ่าน `kubectl describe rs` แล้วแก้ securityContext ใน template |
| topology spread ได้ Pending ทั้งที่ worker ว่าง | ไม่มี `nodeTaintsPolicy: Honor` (นับ control-plane) | ใช้ไฟล์ `spread-topology.yaml` ของบทนี้ที่ใส่ไว้แล้ว |
| บูธค้าง `Init:ErrImagePull` / `ImagePullBackOff` | ไม่มี image บน Node (คลัสเตอร์ใหม่ยังไม่ `kind load`) | ทำขั้น 9.1 แล้ว `kubectl delete pod -n som-booths -l app=som-booth` |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` |
| บูธ `Pending` ตอน scale 5 (`Insufficient memory`/`cpu`) | ทรัพยากรเครื่องไม่พอ | scale แค่ 4 หรือ 3 |
| `curl localhost:8081/api/orders` ได้ `405 Method Not Allowed` | แอปไม่มี `GET /api/orders` | ดูออเดอร์จากหน้าเว็บ หรือ `grep` ตัวเลขหน้าคำว่า ออเดอร์ทั้งหมด (ขั้น 9.4) |
| browser เปิด `localhost:8081` ไม่ได้ (`ERR_CONNECTION_RESET`), log มี `lost connection to pod` | บูธที่ต่อไว้ถูกลบ/ถูก scale ลง | เปิด port-forward ใหม่ไปบูธที่มีอยู่ (ขั้น 9.5) ไม่ต้องเปิด `ssh -L` ใหม่ |
| `kubectl port-forward` แจ้ง `address already in use` หรือ `pgrep` ยังเห็น port-forward ไปบูธที่ถูกลบแล้ว | port-forward ตัวเก่ายังค้าง (ยังไม่มีใครเข้าจึงยังไม่จบ ขั้น 9.5 และ 9.8) | `pgrep -af "[k]ubectl port-forward"` แล้ว `pkill -f "[k]ubectl port-forward.* 8081:3000"` |
| `ssh -L` แจ้งว่า bind port ไม่ได้ | port 8081–8083 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ | เปลี่ยนเลขซ้ายของ `-L` เช่น `-L 18081:localhost:8081` แล้วเปิด `http://localhost:18081` |
| apply promo แล้วมีบูธ promo เกิดทันที 1 ตัว | apply ตอน replicas ยังเป็น 2 ไฟล์คืนค่าเป็น 3 | ดูกล่อง "ถ้าลืม scale กลับ" ในขั้น 9.7 |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 9 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `pod "lonely" deleted ...` ตามด้วย `No resources found in rs-lab namespace.` และค่า `--controllers=...`
- [ ] **LAB 1** `kubectl get rs,pods -n rs-lab -o wide --show-labels` (`3 3 3`), ownerReferences ของ Pod หนึ่งตัว และ error `` `selector` does not match template `labels` ``
- [ ] **LAB 2** terminal 2 ที่เห็นตัวใหม่เกิดขณะตัวเก่า Terminating, ผล `kubectl drain` (ไม่มี `--force`) และ `get pods -o wide` หลัง uncordon (ทางเลือก: ผลลูปเรือล่ม)
- [ ] **LAB 3** `get events --field-selector reason=SuccessfulDelete` ตอน scale 5→2 พร้อมคำอธิบายว่าทำไมตัวนั้นถูกลบ และ `0 0 0`
- [ ] **LAB 4** `stray 0/1 Terminating 0s`, ownerReferences ของ stray ที่ถูกรับเลี้ยง, ตาราง OWNER ตอนมี snack-rs-b และผลหลัง `kubectl label pod ... app-`
- [ ] **LAB 5** error `field is immutable` และ custom-columns ที่มีทั้ง `1.27-alpine v1` และ `1.28-alpine v2`
- [ ] **LAB 6** ตาราง OWNER `<none>` หลัง orphan และ `Events: <none>` หลัง apply ใหม่
- [ ] **LAB 7** `quota-rs 6 4 4` + `ReplicaFailure True FailedCreate` + `exceeded quota` และผลหลัง patch quota
- [ ] **LAB 8** `FailedScheduling ... didn't match pod anti-affinity rules` และผล 2+2 / 2+3 ของ topology spread
- [ ] **LAB 9** (1) `kubectl get rs,pods -n som-booths -o wide` 3 บูธ 2+1 (2) browser 3 แท็บที่ชื่อบูธและออเดอร์ต่างกัน (3) บูธใหม่ออเดอร์ 0 พร้อม `lost connection to pod` (4) events ตอน scale 5→2 (5) custom-columns หลัง apply promo ที่บูธเดิมยัง `1.1` และหน้าเว็บ `🎉 โปรบูธใหม่`
- [ ] ท้ายสุด `kubectl get ns` เหลือ 5 namespace ตั้งต้น และ `kubectl get nodes` Ready ทั้ง 3 ลำไม่มี `SchedulingDisabled`

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| namespace `rs-lab` (snack-rs, stray, web) | 0–6 | `kubectl get ns rs-lab` | `kubectl delete ns rs-lab` |
| ไฟล์ `snack-rs.yaml` ยังเป็น `replicas: 4` | 3 | `grep -n 'replicas:' labs/lab01-first-rs/snack-rs.yaml` | `sed -i 's/replicas: 4 /replicas: 3 /' labs/lab01-first-rs/snack-rs.yaml` |
| เรือ `lab-worker2` ถูก cordon หรือหยุดอยู่ | 2 | `kubectl get nodes` | `kubectl uncordon lab-worker2` / `docker start lab-worker2` |
| namespace `rs-quota`, `rs-psa` | 7 | `kubectl get ns` | `kubectl delete ns rs-quota rs-psa` |
| namespace `rs-spread` | 8 | `kubectl get ns rs-spread` | `kubectl delete ns rs-spread` |
| namespace `som-booths` | 9 | `kubectl get ns som-booths` | `kubectl delete ns som-booths` |
| port-forward ค้าง | 9 | `pgrep -af "[k]ubectl port-forward"` | `pkill -f "[k]ubectl port-forward"` |
| หน้าต่าง `ssh -L` บนเครื่องนักศึกษา | 9 | หน้าต่างที่ยังเปิดอยู่ | 🖥️ `exit` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get ns
kubectl get nodes
kubectl get rs,pods -A | grep -v kube-system
pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
```

```text
NAME                 STATUS   AGE
default              Active   12m
kube-node-lease      Active   12m
kube-public          Active   12m
kube-system          Active   12m
local-path-storage   Active   12m
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          11m   v1.37.0
lab-worker2         Ready    <none>          11m   v1.37.0
NAMESPACE            NAME                                                DESIRED   CURRENT   READY   AGE
local-path-storage   replicaset.apps/local-path-provisioner-75f7fc7dc5   1         1         1       12m

NAMESPACE            NAME                                            READY   STATUS    RESTARTS        AGE
local-path-storage   pod/local-path-provisioner-75f7fc7dc5-kfm2f     1/1     Running   0               12m
ไม่มี port-forward ค้าง
```

ผลที่ถูกต้อง: เหลือ namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), Node `Ready` ทั้ง 3 ลำไม่มี `SchedulingDisabled`, ไม่มี ReplicaSet/Pod ของบทนี้ค้าง (บรรทัดที่เหลือเป็นของ `local-path-storage` ที่ระบบสร้าง) และไม่มี port-forward ค้าง

คลัสเตอร์ `lab` และ image บน Node เก็บไว้ใช้ต่อในบทที่ 6 (Service) ซึ่งเริ่มจากปัญหา "ออเดอร์ไม่ตรงกัน" และ "ที่อยู่ไม่คงที่" ของ LAB 9 ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ `kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพเป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก
