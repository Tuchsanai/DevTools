# Node กับ Pod: Pod ไปอยู่บนเรือลำไหน และเราควบคุมได้อย่างไร

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Node และการจัดวาง Pod (scheduling) — Node object, kube-scheduler, nodeName, nodeSelector, node affinity, pod affinity/anti-affinity, topology spread, taints/tolerations, cordon/drain, Node ล่ม, static Pod และ Downward API
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 2 Kubernetes Pod](../../002_kubernetes_pod/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

บทที่ 2 สอนให้เราสร้าง **Pod** และเปิด "ร้านอาหารแมวน้องส้ม" ได้สำเร็จใน Pod เดียว แต่เราไม่เคยถามเลยว่า **Pod ไปอยู่บน Node ไหน ใครเป็นคนเลือก และเลือกจากอะไร** บทนี้ตอบคำถามนั้นทั้งหมด

เนื้อหาเริ่มจากการทบทวนว่า Node (เรือ) หนึ่งลำมีอะไรบ้าง และใน kind แต่ละ Node คือ Docker container ตัวหนึ่ง จากนั้นอ่าน **Node object** (labels, capacity/allocatable, conditions, heartbeat) แล้วซูมเข้าไปที่ **kube-scheduler** ว่าคัดกรอง (Filtering) ให้คะแนน (Scoring) และผูก Pod กับ Node (Binding) อย่างไร ต่อด้วยเครื่องมือที่เราใช้ "ช่วยบอก" scheduler ได้แก่ `nodeName`, `nodeSelector`, **node affinity**, **pod affinity/anti-affinity**, **topologySpreadConstraints** และ **taints/tolerations** จากนั้นเป็นเรื่องการดูแลเรือ ได้แก่ **cordon/drain/uncordon** และสิ่งที่เกิดขึ้นเมื่อ **Node ล่ม** (NotReady, taint อัตโนมัติ, การไล่ Pod หลัง 300 วินาที) ปิดท้ายด้วย **static Pod**, **Downward API**, node-pressure eviction และ priority/preemption

ตลอดบทเราจะเดินทางไปกับ **น้องส้ม** ที่อยากขยายร้านเป็น **หลายสาขาบนกองเรือ** ค่าที่ยกมาในเอกสาร (ข้อความ Event, เวลาที่ Node กลายเป็น NotReady, เวลาที่ Pod ถูกไล่ ฯลฯ) มาจากการทดลองจริงบนคลัสเตอร์ kind (kind v0.33.0, Kubernetes v1.37.0) ใน LAB ประจำบท เมื่อ 4 ตุลาคม 2569

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายองค์ประกอบบน Node (kubelet, container runtime, kube-proxy, CNI) และบอกได้ว่าใน kind แต่ละ Node คืออะไร
2. อ่าน Node object ด้วย `kubectl get nodes` และ `kubectl describe node` ได้ ทั้ง labels, taints, capacity/allocatable, conditions และ Allocated resources
3. อธิบายขั้นตอน Filtering → Scoring → Binding ของ kube-scheduler และอ่านข้อความ `FailedScheduling` เพื่อหาสาเหตุที่ Pod ค้าง `Pending` ได้
4. อธิบายว่า scheduler ใช้ **ผลรวม requests** เทียบกับ allocatable ไม่ได้ใช้การใช้งานจริง
5. เลือกใช้ `nodeName`, `nodeSelector`, node affinity (required/preferred และ operator ต่าง ๆ) ได้ถูกต้อง
6. ใช้ pod affinity/anti-affinity และ `topologySpreadConstraints` กำหนดให้ Pod อยู่ใกล้หรือกระจายห่างกัน และอธิบายความหมายของ `topologyKey` และ `nodeTaintsPolicy` ได้
7. ใช้ taints และ tolerations ทั้ง 3 effect (`NoSchedule`, `PreferNoSchedule`, `NoExecute`) และ `tolerationSeconds` ได้ และบอกได้ว่าทำไม toleration อย่างเดียวไม่ได้ดึง Pod ไปที่ Node นั้น
8. อธิบายผลของ `cordon`, `drain`, `uncordon` และลำดับเหตุการณ์เมื่อ Node ล่ม รวมถึงชะตากรรมของ **Pod เดี่ยว** ในทั้งสองกรณี
9. อธิบาย static Pod, mirror pod และใช้ Downward API ให้ Pod รู้ชื่อ Node ของตัวเองได้

## สารบัญ

1. [บทนำ: ร้านน้องส้มอยากมีหลายสาขา](#1-บทนำ-ร้านน้องส้มอยากมีหลายสาขา)
2. [ทบทวน Node: เรือหนึ่งลำมีอะไรบ้าง](#2-ทบทวน-node-เรือหนึ่งลำมีอะไรบ้าง)
3. [Node object: สมุดประจำเรือ](#3-node-object-สมุดประจำเรือ)
4. [kube-scheduler: เจ้าหน้าที่จัดตู้ขึ้นเรือ](#4-kube-scheduler-เจ้าหน้าที่จัดตู้ขึ้นเรือ)
5. [requests เทียบ allocatable](#5-requests-เทียบ-allocatable)
6. [nodeName: ข้ามเจ้าหน้าที่จัดตู้](#6-nodename-ข้ามเจ้าหน้าที่จัดตู้)
7. [nodeSelector: ใบสั่งให้ขึ้นเรือที่มีธงตรงกัน](#7-nodeselector-ใบสั่งให้ขึ้นเรือที่มีธงตรงกัน)
8. [Node affinity: แม่เหล็กดึงไปหาธงเรือ](#8-node-affinity-แม่เหล็กดึงไปหาธงเรือ)
9. [Inter-pod affinity และ anti-affinity: แม่เหล็กระหว่างกล่อง](#9-inter-pod-affinity-และ-anti-affinity-แม่เหล็กระหว่างกล่อง)
10. [topologySpreadConstraints: ตาชั่งกองเรือ](#10-topologyspreadconstraints-ตาชั่งกองเรือ)
11. [Taints และ Tolerations: ป้ายห้ามขึ้นและบัตรผ่าน](#11-taints-และ-tolerations-ป้ายห้ามขึ้นและบัตรผ่าน)
12. [บำรุงรักษา Node: cordon, drain และ uncordon](#12-บำรุงรักษา-node-cordon-drain-และ-uncordon)
13. [เมื่อเรือล่ม: Node NotReady และ taint อัตโนมัติ](#13-เมื่อเรือล่ม-node-notready-และ-taint-อัตโนมัติ)
14. [Static Pod: ตู้ที่ต้นเรือดูแลเอง](#14-static-pod-ตู้ที่ต้นเรือดูแลเอง)
15. [Downward API: ป้ายชื่อเรือที่ติดให้ตู้](#15-downward-api-ป้ายชื่อเรือที่ติดให้ตู้)
16. [QoS กับ node-pressure eviction](#16-qos-กับ-node-pressure-eviction)
17. [Priority และ Preemption](#17-priority-และ-preemption)
18. [เลือกเครื่องมือจัดวางแบบไหนเมื่อไร](#18-เลือกเครื่องมือจัดวางแบบไหนเมื่อไร)
19. [ปูทางบทหน้า: Deployment และ Service](#19-ปูทางบทหน้า-deployment-และ-service)
20. [สรุปและคำถามทบทวน](#20-สรุปและคำถามทบทวน)
21. [เอกสารอ้างอิง](#21-เอกสารอ้างอิง)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [ร้านน้องส้มอยากมีหลายสาขา](#fig-1) | 21 | [taint และ toleration](#fig-21) |
| 2 | [แผนผังอุปมาใหม่ของบทนี้](#fig-2) | 22 | [effect ทั้ง 3 ของ taint](#fig-22) |
| 3 | [กายวิภาคของเรือ (Node)](#fig-3) | 23 | [taint ของ control-plane ใน kind](#fig-23) |
| 4 | [Node ใน kind คือ Docker container](#fig-4) | 24 | [NoExecute กับ tolerationSeconds](#fig-24) |
| 5 | [label มาตรฐานของ Node](#fig-5) | 25 | [toleration ไม่ใช่แรงดึงดูด](#fig-25) |
| 6 | [capacity กับ allocatable](#fig-6) | 26 | [cordon: เชือกกั้นท่าเรือ](#fig-26) |
| 7 | [conditions ของ Node](#fig-7) | 27 | [drain: Pod เดี่ยวหายไปเลย](#fig-27) |
| 8 | [kubectl describe node](#fig-8) | 28 | [uncordon แล้ว Pod ไม่กลับมา](#fig-28) |
| 9 | [scheduler เฝ้าดู Pod ที่ยังไม่มีเรือ](#fig-9) | 29 | [heartbeat และ NotReady](#fig-29) |
| 10 | [Filtering → Scoring → Binding](#fig-10) | 30 | [taint อัตโนมัติ unreachable](#fig-30) |
| 11 | [Pending และ FailedScheduling](#fig-11) | 31 | [Pod ถูกไล่ ค้าง Terminating](#fig-31) |
| 12 | [ผลรวม requests เทียบ allocatable](#fig-12) | 32 | [static Pod ของต้นเรือ](#fig-32) |
| 13 | [nodeName ข้าม scheduler](#fig-13) | 33 | [static Pod บน control-plane](#fig-33) |
| 14 | [nodeSelector กับธงเรือ](#fig-14) | 34 | [Downward API ป้ายชื่อเรือ](#fig-34) |
| 15 | [node affinity required/preferred](#fig-15) | 35 | [QoS กับ node-pressure eviction](#fig-35) |
| 16 | [operator ของ node affinity](#fig-16) | 36 | [Priority และ Preemption](#fig-36) |
| 17 | [pod affinity และ anti-affinity](#fig-17) | 37 | [ตารางเลือกเครื่องมือจัดวาง](#fig-37) |
| 18 | [ความหมายของ topologyKey](#fig-18) | 38 | [ปูทาง Deployment และ Service](#fig-38) |
| 19 | [topology spread และ maxSkew](#fig-19) | 39 | [สรุปบทที่ 3](#fig-39) |
| 20 | [กับดัก nodeTaintsPolicy ใน kind](#fig-20) | | |

---

## 1. บทนำ: ร้านน้องส้มอยากมีหลายสาขา

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

<p align="center" id="fig-1">
  <img src="images/01-opening-fleet-branches.png" alt="รูปที่ 1 ร้านน้องส้มอยากมีหลายสาขา" width="900"><br>
  <em><b>รูปที่ 1</b> ร้านอาหารแมวน้องส้มจากบทที่ 2 ขายดีจนอยากเปิดหลายสาขา แต่กล่อง Pod แต่ละกล่องจะไปอยู่บนเรือลำไหน ใครเป็นคนเลือก</em>
</p>

ร้านอาหารแมวน้องส้มที่เปิดใน Pod เดียวเมื่อบทที่ 2 ขายดีมาก ลูกค้าต่อคิวยาว น้องส้มจึงอยากเปิด **หลายสาขาบนกองเรือ** แต่พอเริ่มวางแผนก็เจอคำถามที่ไม่เคยคิดมาก่อน

- ตอนบทที่ 2 เราแค่ `kubectl apply` แล้ว Pod ก็ไปโผล่บน `lab-worker` หรือ `lab-worker2` เอง **ใครเป็นคนเลือก**
- เลือกจาก **อะไร** ระวางเรือ ป้ายบนเรือ หรือสุ่ม
- ถ้าน้องส้มอยากให้ **สองสาขาอยู่คนละลำ** (ลำหนึ่งล่ม อีกสาขายังขายได้) จะ **สั่ง** ได้อย่างไร
- ถ้าเรือต้อง **เข้าอู่ซ่อม** หรือ **หายไปในหมอก** สาขาบนเรือลำนั้นจะเป็นอย่างไร

ทบทวนสิ่งที่รู้จากบทที่ 2 ก่อน

1. **Pod หนึ่งตัวอยู่บน Node เดียวเสมอ** container ทุกตัวใน Pod อยู่ด้วยกันบนเรือลำเดียว
2. **kube-scheduler เลือก Node ให้ Pod ครั้งเดียว** ตอน Pod เกิด หลังจากนั้น Pod **ไม่ย้ายเรือ** ถ้า Pod ถูกลบ ต้องสร้าง Pod ใหม่ (ซึ่งอาจได้เรือลำอื่น)
3. **kubelet** บนเรือลำนั้นเป็นคนสั่งสร้าง container จริง

บทนี้จะเปิดกล่องดำของข้อ 2 ว่าเจ้าหน้าที่จัดตู้ (kube-scheduler) คิดอย่างไร และเรามีเครื่องมืออะไรบ้างไว้ "กระซิบ" หรือ "บังคับ" การตัดสินใจนั้น

<p align="center" id="fig-2">
  <img src="images/02-new-metaphor-map.png" alt="รูปที่ 2 แผนผังอุปมาใหม่ของบทนี้" width="900"><br>
  <em><b>รูปที่ 2</b> แผนผังอุปมาใหม่ของบทนี้: ธงบนเรือ = node label, ป้ายห้ามขึ้น = taint, บัตรผ่าน = toleration, แม่เหล็ก = affinity/anti-affinity, เชือกกั้น = cordon</em>
</p>

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–2)

| Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| container | ตู้สินค้า | |
| Pod | กล่องห้องโดยสารห่อตู้ มีป้าย IP 1 ป้าย | |
| Node | เรือสินค้า (`lab-worker`, `lab-worker2`) | |
| Control Plane | หอบังคับการบนท่า (`lab-control-plane`) | |
| kube-scheduler | เจ้าหน้าที่จัดตู้ขึ้นเรือ (ถือ clipboard ตรวจเรือ) | |
| kubelet | ต้นเรือ (first mate) ประจำเรือแต่ละลำ | |
| container runtime (containerd) | ห้องเครื่อง/เครนบนเรือที่ยกตู้จริง | ✓ |
| kube-proxy | นายท่าจราจรบนเรือ (กล่าวถึงเท่านั้น) | ✓ |
| Node object / status | สมุดประจำเรือ (ทะเบียนเรือ) | ✓ |
| capacity / allocatable | ระวางเรือทั้งหมด / ระวางที่ขายให้ลูกค้าได้ | ✓ |
| node conditions | ไฟแสดงสถานะบนแผงเรือ | ✓ |
| node label | ธง/ป้ายบนเสากระโดงเรือ | ✓ |
| nodeSelector | ใบสั่ง "ต้องขึ้นเรือที่มีธงนี้" | ✓ |
| node affinity | แม่เหล็กดึงกล่องไปหาธงเรือ (required = ต้อง, preferred = อยากได้) | ✓ |
| pod affinity / anti-affinity | แม่เหล็กดึงดูด / ผลัก ระหว่างกล่อง | ✓ |
| topologyKey | เส้นแบ่งเขต "ถือว่าเป็นที่เดียวกัน" (เรือลำเดียวกัน / ท่าเดียวกัน) | ✓ |
| topologySpreadConstraints | ตาชั่งถ่วงน้ำหนักให้กองเรือสมดุล | ✓ |
| taint | ป้าย "ห้ามขึ้น" ที่ขอบเรือ | ✓ |
| toleration | บัตรผ่าน (มีบัตร = ขึ้นได้ ไม่ได้แปลว่าต้องขึ้น) | ✓ |
| NoExecute + tolerationSeconds | ป้ายไล่ลงเรือ + นาฬิกาทราย | ✓ |
| cordon | เชือกกั้นท่าเรือ (ห้ามขึ้นเพิ่ม คนเดิมอยู่ต่อ) | ✓ |
| drain | ย้ายของทั้งหมดลงจากเรือก่อนเข้าอู่ | ✓ |
| NotReady / unreachable | เรือขาดการติดต่อในหมอก วิทยุเงียบ | ✓ |
| Lease heartbeat | สัญญาณวิทยุ "ยังอยู่" ทุก 10 วินาที | ✓ |
| static Pod | ตู้ที่ต้นเรือดูแลเองจากแฟ้มบนเรือ (หอเห็นแค่ "เงา" = mirror pod) | ✓ |
| Downward API | ป้ายชื่อเรือที่ต้นเรือติดให้ตู้ตอนขึ้นเรือ | ✓ |
| PriorityClass / preemption | ป้ายสินค้าด่วน VIP แซงคิว | ✓ |

> **ขอบเขตของบทนี้:** ยังคงใช้ **Pod เดี่ยว ๆ** เหมือนบทที่ 2 เพื่อให้เห็นพฤติกรรมการจัดวางชัดที่สุด และจะได้เห็นด้วยตาว่า "Pod เดี่ยวที่หายไปไม่มีใครสร้างคืน" ทรัพยากรอย่าง Deployment และ Service จะกล่าวถึงเพื่อปูทางในหัวข้อ 19 เท่านั้น

---

## 2. ทบทวน Node: เรือหนึ่งลำมีอะไรบ้าง

### 2.1 องค์ประกอบบน worker node

<p align="center" id="fig-3">
  <img src="images/03-node-anatomy.png" alt="รูปที่ 3 กายวิภาคของเรือ (Node)" width="900"><br>
  <em><b>รูปที่ 3</b> เรือ (Node) หนึ่งลำมี kubelet เป็นต้นเรือ, container runtime เป็นห้องเครื่องยกตู้ และ kube-proxy ดูแลเส้นทางจราจร</em>
</p>

**Node** คือเครื่อง (จริงหรือเสมือน) ที่รัน Pod บน worker node ทุกเครื่องมีองค์ประกอบหลักดังนี้

| องค์ประกอบ | อุปมา | หน้าที่ |
|---|---|---|
| **kubelet** | ต้นเรือ | ลงทะเบียน Node กับ API server, ส่ง heartbeat และรายงานสถานะ (conditions, capacity), เฝ้าดู Pod ที่ถูกผูกกับ Node ของตัวเองแล้วสั่ง runtime สร้าง/ลบ container, รัน probe, ไล่ Pod เมื่อทรัพยากรใกล้หมด, ดูแล static Pod |
| **container runtime** (containerd) | ห้องเครื่อง/เครน | ดึง image และรัน container จริง kubelet สั่งผ่านมาตรฐาน **CRI** (Container Runtime Interface) |
| **kube-proxy** | นายท่าจราจร | เขียนกฎเครือข่าย (iptables/nftables) ให้ทราฟฟิกไปถึง Pod ปลายทาง ใช้กับ Service ซึ่งเป็นเนื้อหาบทหน้า |
| **CNI plugin** (kind ใช้ `kindnet`) | ฝ่ายแจกป้ายที่อยู่ | ให้ IP แก่ Pod (ใน kind คือ `10.244.x.x`) และเชื่อมเครือข่ายระหว่าง Node |

สังเกตว่า **scheduler ไม่ได้อยู่บน worker** scheduler อยู่ที่หอบังคับการ (control plane) ทำหน้าที่ "ตัดสินใจ" อย่างเดียว ส่วนการ "ลงมือ" สร้าง container เป็นงานของ kubelet บนเรือแต่ละลำ

### 2.2 Node ใน kind คือ Docker container

<p align="center" id="fig-4">
  <img src="images/04-kind-nodes-are-containers.png" alt="รูปที่ 4 Node ใน kind คือ Docker container" width="900"><br>
  <em><b>รูปที่ 4</b> ใน kind แต่ละ Node คือ Docker container ที่รันอยู่ใน k8s-lab จึงจำลองเรือล่มได้ด้วย docker stop</em>
</p>

คลัสเตอร์ของเราสร้างด้วย **kind** (Kubernetes IN Docker) ภายใน container `k8s-lab` ซึ่งมี dockerd ของตัวเอง แต่ละ Node ของคลัสเตอร์จึงเป็น **Docker container หนึ่งตัวใน k8s-lab** (ไม่ใช่บนเครื่องนักศึกษาโดยตรง)

```text
เครื่องนักศึกษา (Docker Desktop)
└── container k8s-lab            ← ssh -p 2223 root@localhost
    └── dockerd ภายใน k8s-lab
        ├── container lab-control-plane   (Node: หอบังคับการ)
        ├── container lab-worker          (Node: เรือลำที่ 1)
        └── container lab-worker2         (Node: เรือลำที่ 2)
            └── containerd → container ของ Pod ที่ถูกวางบนเรือลำนี้
```

ผลจริงจาก LAB 0 (รันใน SSH session ของ k8s-lab)

```text
$ docker ps --format '{{.Names}}\t{{.Status}}'
lab-worker	Up 3 minutes
lab-worker2	Up 3 minutes
lab-control-plane	Up 3 minutes

$ docker exec lab-worker crictl ps
CONTAINER           IMAGE               CREATED             STATE               NAME                ATTEMPT             POD ID              POD                 NAMESPACE
3ca8b31c44e17       4626fe10df5b9       3 minutes ago       Running             kindnet-cni         0                   f674bc63f9edb       kindnet-dmj46       kube-system
b9af0b8b13988       d6a28daf3e6b0       3 minutes ago       Running             kube-proxy          0                   05719e65616d7       kube-proxy-7xjpl    kube-system
```

`crictl` คือเครื่องมือคุยกับ container runtime ผ่าน CRI โดยตรง (ไม่ผ่าน API server) เหมือนเดินเข้าห้องเครื่องไปดูเองว่ามีตู้อะไรถูกยกขึ้นเรือแล้วบ้าง

ผลที่ตามมาซึ่งเราจะใช้ใน LAB

- **จำลองเรือล่ม** ได้ด้วย `docker stop lab-worker2` และคืนเรือด้วย `docker start lab-worker2` (คำสั่ง docker เหล่านี้ต้องรัน **ใน k8s-lab** เพราะ container `lab-*` อยู่ใน dockerd ของ k8s-lab)
- **วางไฟล์บนเรือ** ได้ด้วย `docker cp ... lab-worker:/path` (ใช้ใน static Pod)
- ข้อควรระวัง: ทุก Node "มองเห็น" CPU/RAM ของเครื่องเดียวกัน (ดูหัวข้อ 3.3)

### 2.3 control-plane ก็เป็น Node

`lab-control-plane` ก็มี kubelet และลงทะเบียนเป็น Node เหมือนกัน เพราะองค์ประกอบของหอบังคับการ (etcd, kube-apiserver, kube-scheduler, kube-controller-manager) เองก็รันเป็น Pod บน Node นี้ (เป็น static Pod ดูหัวข้อ 14) แต่ kind ติด **taint** `node-role.kubernetes.io/control-plane:NoSchedule` ไว้ Pod ทั่วไปจึงไม่ถูกวางที่นี่ (ดูหัวข้อ 11.3)

---

## 3. Node object: สมุดประจำเรือ

ทุก Node มี object ชนิด `Node` ใน API server เหมือนสมุดประจำเรือที่หอบังคับการเก็บไว้ ส่วน `spec` บอกการตั้งค่า (เช่น taints, unschedulable, podCIDR) ส่วน `status` คือสิ่งที่ kubelet รายงาน (capacity, conditions, addresses, nodeInfo)

### 3.1 kubectl get nodes

```bash
kubectl get nodes -o wide
```

```text
NAME                STATUS   ROLES           AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   3m13s   v1.37.0   172.19.0.3    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker          Ready    <none>          2m58s   v1.37.0   172.19.0.4    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker2         Ready    <none>          2m58s   v1.37.0   172.19.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
```

| คอลัมน์ | ความหมาย |
|---|---|
| `STATUS` | สรุปจาก condition `Ready` (`Ready` / `NotReady`) และอาจต่อท้าย `,SchedulingDisabled` เมื่อถูก cordon |
| `ROLES` | อ่านจาก label `node-role.kubernetes.io/<role>` worker ใน kind ไม่มี label นี้จึงแสดง `<none>` |
| `VERSION` | เวอร์ชันของ kubelet บน Node |
| `INTERNAL-IP` | IP ของ Node (ใน kind คือ IP ของ container `lab-*` ในเครือข่าย Docker เช่น `172.19.0.x`) ต่างจาก Pod IP (`10.244.x.x`) |
| `OS-IMAGE`, `KERNEL-VERSION`, `CONTAINER-RUNTIME` | ระบบปฏิบัติการใน Node, kernel ของเครื่องจริง (kind ใช้ kernel ร่วมกับเครื่อง) และ runtime |

### 3.2 Labels มาตรฐานของ Node

<p align="center" id="fig-5">
  <img src="images/05-node-standard-labels.png" alt="รูปที่ 5 label มาตรฐานของ Node" width="900"><br>
  <em><b>รูปที่ 5</b> label มาตรฐานของ Node เปรียบเป็นธงบนเสากระโดง เช่น kubernetes.io/hostname, kubernetes.io/os, kubernetes.io/arch</em>
</p>

kubelet ติด label ให้ Node อัตโนมัติชุดหนึ่ง ผลจริงจาก `kubectl get nodes --show-labels`

```text
NAME                STATUS   ROLES           AGE     VERSION   LABELS
lab-control-plane   Ready    control-plane   3m13s   v1.37.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=lab-control-plane,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=,node.kubernetes.io/exclude-from-external-load-balancers=
lab-worker          Ready    <none>          2m58s   v1.37.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=lab-worker,kubernetes.io/os=linux
lab-worker2         Ready    <none>          2m58s   v1.37.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=lab-worker2,kubernetes.io/os=linux
```

**ตารางที่ 2** label ที่พบบ่อยบน Node

| label | ตัวอย่างค่า | ความหมาย |
|---|---|---|
| `kubernetes.io/hostname` | `lab-worker` | ชื่อ Node (ไม่ซ้ำกัน) ใช้เป็น `topologyKey` แทน "เรือลำเดียวกัน" บ่อยที่สุด |
| `kubernetes.io/os` | `linux` | ระบบปฏิบัติการ (`linux`/`windows`) |
| `kubernetes.io/arch` | `amd64` | สถาปัตยกรรม CPU (`amd64`/`arm64`) |
| `node-role.kubernetes.io/control-plane` | `""` (ค่าว่าง) | บอกว่าเป็น control-plane และเป็นที่มาของคอลัมน์ `ROLES` |
| `beta.kubernetes.io/arch`, `beta.kubernetes.io/os` | `amd64`, `linux` | label รุ่นเก่า (deprecated) ยังติดไว้เพื่อความเข้ากันได้ ควรใช้ตัวที่ไม่มี `beta.` |
| `topology.kubernetes.io/zone`, `topology.kubernetes.io/region` | `asia-southeast1-a` | zone/region ของเครื่องบนคลาวด์ (cloud provider ติดให้) **kind ไม่มี** |
| `node.kubernetes.io/exclude-from-external-load-balancers` | `""` | ไม่ให้ load balancer ภายนอกส่งทราฟฟิกมาที่ Node นี้ (kind ติดให้ control-plane) |

นอกจากนี้เราติด label เองได้ เช่น `kubectl label node lab-worker disk=ssd` (ใช้ใน nodeSelector/affinity) ส่วน key ที่ขึ้นต้นด้วย `kubernetes.io/` และ `k8s.io/` **สงวนไว้ให้ Kubernetes** ไม่ควรตั้งเอง

> **รู้ไว้:** ดู label เป็นคอลัมน์ได้ด้วย `-L` เช่น `kubectl get nodes -L kubernetes.io/arch,kubernetes.io/os` จะได้คอลัมน์ `ARCH` และ `OS` อ่านง่ายกว่า `--show-labels`

### 3.3 capacity กับ allocatable

<p align="center" id="fig-6">
  <img src="images/06-capacity-vs-allocatable.png" alt="รูปที่ 6 capacity กับ allocatable" width="900"><br>
  <em><b>รูปที่ 6</b> capacity คือระวางเรือทั้งหมด allocatable คือส่วนที่เหลือให้ Pod หลังหักส่วนที่สงวนไว้ให้ระบบ</em>
</p>

- **capacity** = ทรัพยากรทั้งหมดที่ kubelet ตรวจพบบนเครื่อง (CPU, memory, ephemeral-storage, จำนวน Pod สูงสุด)
- **allocatable** = ส่วนที่ "ขายให้ Pod ได้" คำนวณจาก

```text
allocatable = capacity − kube-reserved − system-reserved − eviction-threshold
```

`kube-reserved` สงวนให้องค์ประกอบของ Kubernetes (kubelet, runtime) `system-reserved` สงวนให้ระบบปฏิบัติการ และ `eviction-threshold` คือเส้นที่ kubelet จะเริ่มไล่ Pod (หัวข้อ 16) **scheduler ใช้ allocatable** (ไม่ใช่ capacity) ในการตัดสินใจ

ผลจริงจาก LAB 0

```text
$ kubectl get node lab-worker -o jsonpath='{.status.capacity}{"\n"}{.status.allocatable}{"\n"}'
{"cpu":"32","ephemeral-storage":"1081101176832","hugepages-1Gi":"0","hugepages-2Mi":"0","memory":"64489564Ki","pods":"110"}
{"cpu":"32","ephemeral-storage":"1081101176832","hugepages-1Gi":"0","hugepages-2Mi":"0","memory":"64489564Ki","pods":"110"}
```

สิ่งที่เห็น

1. ใน kind **allocatable เท่ากับ capacity ทุกค่า** เพราะ kind ไม่ได้ตั้ง reserved ไว้ (บนคลัสเตอร์จริงหรือคลาวด์ allocatable มักน้อยกว่า capacity ชัดเจน)
2. `pods: 110` คือจำนวน Pod สูงสุดต่อ Node ค่าเริ่มต้นของ kubelet
3. **ข้อควรระวังใน kind:** ทุก Node เห็น `cpu: 32` และ memory ~61.5 GiB เท่ากัน เพราะทั้งสามเป็น container บน **เครื่องเดียวกัน** คลัสเตอร์ 3 Node จึง **ไม่ได้มีทรัพยากรจริง 3 เท่า** ตัวเลขในเครื่องนักศึกษาจะเท่ากับ CPU/RAM ของเครื่องตัวเอง (หรือของ VM ของ Docker Desktop)

### 3.4 Conditions: ไฟสถานะบนแผงเรือ

<p align="center" id="fig-7">
  <img src="images/07-node-conditions-panel.png" alt="รูปที่ 7 conditions ของ Node" width="900"><br>
  <em><b>รูปที่ 7</b> สถานะ (conditions) ของ Node เหมือนไฟบนแผงเรือ: Ready ต้องเป็น True ส่วน MemoryPressure, DiskPressure, PIDPressure ควรเป็น False</em>
</p>

**ตารางที่ 3** conditions ของ Node

| condition | ค่าปกติ | ความหมายเมื่อผิดปกติ |
|---|:---:|---|
| `Ready` | `True` | `False` = kubelet รายงานว่าไม่พร้อม (เช่น runtime หรือเครือข่ายมีปัญหา), **`Unknown` = หอบังคับการไม่ได้ยินข่าวจากต้นเรือเกินเวลาที่กำหนด** (หัวข้อ 13) |
| `MemoryPressure` | `False` | หน่วยความจำบน Node เหลือน้อยกว่าเกณฑ์ eviction |
| `DiskPressure` | `False` | พื้นที่ดิสก์ (หรือ inode) เหลือน้อย |
| `PIDPressure` | `False` | จำนวนโปรเซสใกล้เต็ม |
| `NetworkUnavailable` | `False` | เครือข่ายของ Node ยังตั้งค่าไม่เสร็จ (บาง CNI/คลาวด์เท่านั้นที่ตั้งค่านี้) |

แต่ละ condition มี `LastHeartbeatTime` (ครั้งล่าสุดที่ kubelet รายงาน) และ `LastTransitionTime` (ครั้งล่าสุดที่ค่าเปลี่ยน) พร้อม `Reason` และ `Message` เช่นผลจริงของ Node ปกติ

```text
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:14 +0700   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:14 +0700   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:14 +0700   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Sun, 04 Oct 2026 18:53:25 +0700   Sun, 04 Oct 2026 18:53:25 +0700   KubeletReady                 kubelet is posting ready status
```

### 3.5 ส่วนอื่นของ Node object

| ฟิลด์ | ตัวอย่างจาก `lab-worker` | ความหมาย |
|---|---|---|
| `status.addresses` | `InternalIP: 172.19.0.4`, `Hostname: lab-worker` | ที่อยู่ของ Node (คลาวด์อาจมี `ExternalIP`) |
| `status.nodeInfo` | `kubeletVersion: v1.37.0`, `containerRuntimeVersion: containerd://2.3.4`, `osImage: Debian GNU/Linux 13 (trixie)` | ข้อมูลระบบ (แสดงใน `System Info` ของ describe) |
| `spec.podCIDR` | `10.244.1.0/24` | ช่วง IP ที่ Pod บน Node นี้จะได้ (lab-worker ได้ `10.244.1.x`) |
| `spec.taints` | ไม่มี (control-plane มี 1 รายการ) | ป้ายห้ามขึ้น (หัวข้อ 11) |
| `spec.unschedulable` | `false` | `true` เมื่อถูก cordon (หัวข้อ 12) |

### 3.6 kubectl describe node: เปิดสมุดประจำเรือ

<p align="center" id="fig-8">
  <img src="images/08-describe-node-logbook.png" alt="รูปที่ 8 kubectl describe node" width="900"><br>
  <em><b>รูปที่ 8</b> kubectl describe node เหมือนเปิดสมุดประจำเรือ เห็น Labels, Taints, Conditions, Allocatable และผลรวม requests ของ Pod บนเรือ</em>
</p>

`kubectl describe node lab-worker` รวมทุกอย่างไว้ในหน้าเดียว ส่วนที่ควรอ่านเป็นประจำ (ผลจริง ตัดบางส่วน)

```text
Name:               lab-worker
Roles:              <none>
Labels:             beta.kubernetes.io/arch=amd64
                    ...
                    kubernetes.io/hostname=lab-worker
                    kubernetes.io/os=linux
Taints:             <none>
Unschedulable:      false
Lease:
  HolderIdentity:  lab-worker
  AcquireTime:     <unset>
  RenewTime:       Sun, 04 Oct 2026 18:56:27 +0700
Conditions:
  ...
Addresses:
  InternalIP:  172.19.0.4
  Hostname:    lab-worker
Capacity:
  cpu:                32
  ...
Allocatable:
  cpu:                32
  ...
PodCIDR:                      10.244.1.0/24
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

**ตารางที่ 4** ส่วนสำคัญของ `describe node` และใช้ตอบคำถามอะไร

| ส่วน | ใช้ตอบคำถาม |
|---|---|
| `Labels` | เรือลำนี้มีธงอะไร nodeSelector/affinity จะเลือกได้ไหม |
| `Taints`, `Unschedulable` | มีป้ายห้ามขึ้นหรือถูก cordon อยู่หรือเปล่า |
| `Lease` (`RenewTime`) | ต้นเรือส่งสัญญาณล่าสุดเมื่อไร |
| `Conditions` | เรือพร้อมไหม มีแรงกดดันทรัพยากรไหม |
| `Capacity` / `Allocatable` | ระวางทั้งหมด / ระวางที่ขายได้ |
| `Non-terminated Pods` | มี Pod อะไรอยู่บนเรือ พร้อม requests/limits ของแต่ละตัว |
| **`Allocated resources`** | **ผลรวม requests/limits ของทุก Pod บนเรือ เทียบเป็น % ของ allocatable** ตัวเลขนี้คือสิ่งที่ scheduler ใช้ตัดสินว่า "ระวางเหลือพอไหม" |
| `Events` | ประวัติของเรือ เช่น `NodeReady`, `NodeNotReady`, `NodeNotSchedulable` |

### 3.7 Heartbeat: สัญญาณวิทยุ "ยังอยู่"

หอบังคับการรู้ได้อย่างไรว่าเรือยังอยู่ kubelet ส่ง heartbeat สองแบบ

1. **Lease** ใน namespace `kube-node-lease` (Node ละ 1 ตัว ชื่อเดียวกับ Node) kubelet ต่ออายุ (`renewTime`) ประมาณทุก **10 วินาที** เป็น object เล็กมาก จึงประหยัดภาระของ API server
2. **NodeStatus** kubelet อัปเดต `status` ของ Node เมื่อมีการเปลี่ยนแปลง หรือเป็นระยะแม้ไม่มีอะไรเปลี่ยน

ผลจริงจาก LAB 0: วัด `renewTime` ห่างกัน 11 วินาที เห็นว่าต่ออายุไป 1 ครั้งห่างจากครั้งก่อน ~10.17 วินาที และ `leaseDurationSeconds` คือ 40

```text
$ kubectl get lease -n kube-node-lease
NAME                HOLDER              AGE
lab-control-plane   lab-control-plane   3m29s
lab-worker          lab-worker          3m6s
lab-worker2         lab-worker2         3m7s

$ kubectl get lease lab-worker -n kube-node-lease -o jsonpath='{.spec.renewTime}{"  "}{.spec.leaseDurationSeconds}{"\n"}'; sleep 11; kubectl get lease lab-worker -n kube-node-lease -o jsonpath='{.spec.renewTime}{"\n"}'
2026-10-04T11:56:27.119121Z  40
2026-10-04T11:56:37.288385Z
```

ถ้าวิทยุเงียบไปนาน **node lifecycle controller** (อยู่ใน kube-controller-manager) จะตัดสินว่าเรือขาดการติดต่อ รายละเอียดอยู่ในหัวข้อ 13

---

## 4. kube-scheduler: เจ้าหน้าที่จัดตู้ขึ้นเรือ

### 4.1 scheduler ทำงานอย่างไร

<p align="center" id="fig-9">
  <img src="images/09-scheduler-watches-unscheduled.png" alt="รูปที่ 9 scheduler เฝ้าดู Pod ที่ยังไม่มีเรือ" width="900"><br>
  <em><b>รูปที่ 9</b> Pod ใหม่ที่ยังไม่มี nodeName รอที่ท่า kube-scheduler หยิบมาเลือกเรือ แล้ว kubelet บนเรือนั้นเป็นคนสร้าง container</em>
</p>

ทบทวนเส้นทางการเกิดของ Pod จากบทที่ 2 โดยเน้นบทบาทของ scheduler

1. `kubectl apply` ส่ง Pod ไปที่ kube-apiserver ซึ่งบันทึกลง etcd ตอนนี้ Pod ยัง **ไม่มี `spec.nodeName`** (STATUS `Pending`)
2. **kube-scheduler เฝ้าดู (watch) Pod ที่ `spec.nodeName` ว่าง** หยิบเข้าคิว แล้วเลือก Node ที่เหมาะสม
3. scheduler เขียน **binding** กลับไปที่ API server ผลคือ `spec.nodeName` ของ Pod ถูกเติม และเกิด Event `Scheduled` เช่น `Successfully assigned default/huge-pod to lab-worker`
4. **kubelet บน Node นั้น** เห็นว่ามี Pod ใหม่ถูกผูกกับตัวเอง จึงสั่ง runtime สร้าง sandbox, ดึง image, สร้างและเริ่ม container (Event `Pulled`, `Created`, `Started` มาจาก `kubelet`)

> scheduler ไม่ได้สร้าง container และไม่ได้ส่งคำสั่งไปที่เรือโดยตรง มันแค่ "เขียนชื่อเรือลงบนใบงาน" ส่วนต้นเรือแต่ละลำคอยดูใบงานที่มีชื่อเรือตัวเอง

### 4.2 Filtering → Scoring → Binding

<p align="center" id="fig-10">
  <img src="images/10-filter-score-bind.png" alt="รูปที่ 10 Filtering Scoring Binding" width="900"><br>
  <em><b>รูปที่ 10</b> scheduler ทำ 3 ขั้น: Filtering ตัดเรือที่รับไม่ได้ → Scoring ให้คะแนนเรือที่เหลือ → Binding ผูก Pod กับเรือคะแนนสูงสุด</em>
</p>

การตัดสินใจของ scheduler สำหรับ Pod หนึ่งตัวแบ่งเป็นขั้น แต่ละขั้นประกอบด้วย **plugin** หลายตัว

**ขั้นที่ 1 Filtering (คัดทิ้ง)** ตรวจทุก Node ว่า "รับ Pod นี้ได้ไหม" ถ้า plugin ใดตอบว่าไม่ได้ Node นั้นถูกตัดทิ้ง

| plugin (ตัวอย่าง) | ตรวจอะไร | หัวข้อ |
|---|---|:---:|
| `NodeUnschedulable` | Node ถูก cordon (`spec.unschedulable: true`) หรือไม่ | 12 |
| `NodeName` | ถ้า Pod ระบุ `nodeName` ต้องตรงกับชื่อ Node | 6 |
| `NodeResourcesFit` | requests ของ Pod + ผลรวม requests เดิม ≤ allocatable หรือไม่ | 5 |
| `NodeAffinity` | ตรง `nodeSelector` และ required node affinity หรือไม่ | 7–8 |
| `TaintToleration` | Pod ทนทุก taint แบบ `NoSchedule`/`NoExecute` ของ Node ได้หรือไม่ | 11 |
| `InterPodAffinity` | ผ่านกฎ required pod affinity/anti-affinity หรือไม่ | 9 |
| `PodTopologySpread` | วางแล้วยังไม่เอียงเกิน `maxSkew` (แบบ `DoNotSchedule`) หรือไม่ | 10 |
| `NodePorts` | port ที่ Pod ขอผูกกับ Node (`hostPort`) ว่างหรือไม่ | – |

**ขั้นที่ 2 Scoring (ให้คะแนน)** Node ที่ผ่านทุก filter ถูกให้คะแนน 0–100 จากหลาย plugin แล้วรวมแบบถ่วงน้ำหนัก เช่น

- `NodeResourcesFit` (กลยุทธ์ค่าเริ่มต้น `LeastAllocated`) ชอบ Node ที่ยังว่างมาก และ `NodeResourcesBalancedAllocation` ชอบ Node ที่ใช้ CPU กับ memory สมดุลกัน
- `ImageLocality` ชอบ Node ที่มี image อยู่แล้ว (เริ่มเร็วกว่า)
- `NodeAffinity` ให้คะแนนตาม **preferred** node affinity (`weight`)
- `InterPodAffinity` ให้คะแนนตาม **preferred** pod affinity/anti-affinity
- `TaintToleration` หักคะแนน Node ที่มี taint แบบ `PreferNoSchedule`
- `PodTopologySpread` ให้คะแนนตามความสมดุลเมื่อใช้ `ScheduleAnyway`

**ขั้นที่ 3 Binding** เลือก Node คะแนนสูงสุด (ถ้าเสมอกันเลือกแบบสุ่ม) แล้วเขียน binding

> **ข้อควรจำ:** กฎแบบ "ต้อง" (required, `nodeSelector`, taint `NoSchedule`, `DoNotSchedule`) ทำงานในขั้น **Filtering** ส่วนกฎแบบ "อยากได้" (preferred, `PreferNoSchedule`, `ScheduleAnyway`) ทำงานในขั้น **Scoring** จึง **ไม่มีวันทำให้ Pod ค้าง Pending**

### 4.3 เมื่อไม่มีเรือลำไหนผ่าน: Pending และ FailedScheduling

<p align="center" id="fig-11">
  <img src="images/11-pending-failedscheduling.png" alt="รูปที่ 11 Pending และ FailedScheduling" width="900"><br>
  <em><b>รูปที่ 11</b> ถ้าไม่มีเรือลำไหนผ่าน filter Pod จะ Pending และมี Event FailedScheduling บอกเหตุผลของทุก node</em>
</p>

ถ้าไม่มี Node ใดผ่าน Filtering Pod จะค้าง `Pending` (คอลัมน์ `NODE` เป็น `<none>`) และ scheduler เขียน Event `FailedScheduling` ผลจริงจาก LAB 1 (Pod ขอ memory 4000Gi)

```text
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  10s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

วิธีอ่านข้อความนี้

| ส่วนของข้อความ | ความหมาย |
|---|---|
| `0/3 nodes are available` | จาก 3 Node ไม่มีสักลำที่ผ่าน |
| `1 node(s) had untolerated taint(s)` | 1 ลำ (control-plane) มี taint ที่ Pod ไม่มีบัตรผ่าน |
| `2 Insufficient memory` | 2 ลำ (worker) memory ที่เหลือไม่พอ requests |
| `preemption: ... Preemption is not helpful for scheduling` | scheduler ลองคิดแล้วว่า **ไล่ Pod อื่นออกก็ไม่ช่วย** (หัวข้อ 17) |

ข้อสังเกตสำคัญ

1. **ตัวเลขรวมกันต้องเท่ากับจำนวน Node ทั้งหมด** (1 + 2 = 3) แต่ละ Node ถูกนับใน **เหตุผลแรกที่ตกเท่านั้น** เช่น control-plane ถูกนับเป็น "untolerated taint" เสมอ ไม่ว่า Pod จะมีปัญหาอื่นกับ control-plane อีกหรือไม่
2. ข้อความเปลี่ยนตาม plugin ที่ทำให้ตก ตัวอย่างจริงจาก LAB ของบทนี้

| สถานการณ์ | ข้อความจริง (ส่วนที่เกี่ยวกับ worker) |
|---|---|
| ขอ memory เกิน | `2 Insufficient memory` |
| ไม่มี Node ตรง nodeSelector/required affinity | `2 node(s) didn't match Pod's node affinity/selector` |
| required pod affinity หา Pod เป้าหมายไม่เจอ | `2 node(s) didn't match pod affinity rules` |
| required anti-affinity ชน | `2 node(s) didn't match pod anti-affinity rules` |
| topology spread เอียงเกิน | `2 node(s) didn't match pod topology spread constraints` |
| Node ถูก cordon | `1 node(s) were unschedulable` |

3. **scheduler ลองใหม่เองเมื่อคลัสเตอร์เปลี่ยน** เช่น เราติด label ให้ Node, ลบ taint, uncordon หรือลบ Pod ที่กีดขวาง Pod ที่ Pending จะถูกนำกลับมาพิจารณาและถูกวางทันทีโดย **ไม่ต้องลบแล้วสร้างใหม่** (ใน LAB 3 Pod ถูกวางภายใน ~1 วินาทีหลังติด label)

คำสั่งที่ใช้ดูเหตุผลบ่อย

```bash
kubectl describe pod <ชื่อ> | sed -n '/^Events/,$p'
kubectl get events --field-selector reason=FailedScheduling
```

### 4.4 ตัดสินใจครั้งเดียว ไม่ย้ายภายหลัง

เมื่อ Pod ถูก bind แล้ว scheduler **ไม่กลับมาพิจารณาใหม่** แม้ภายหลังคลัสเตอร์จะเปลี่ยนจนกฎแบบ preferred ไม่ตรงแล้ว หรือมี Node ใหม่ที่ว่างกว่า Pod ก็อยู่ที่เดิม (Kubernetes มีโปรเจกต์เสริมชื่อ **descheduler** สำหรับไล่ Pod ออกเพื่อให้ถูกจัดวางใหม่ แต่ไม่ได้ติดตั้งมาด้วย) วิธีเดียวที่ Pod จะ "ย้ายเรือ" คือถูกลบแล้วมี Pod ใหม่เกิดขึ้นแทน

---

## 5. requests เทียบ allocatable

<p align="center" id="fig-12">
  <img src="images/12-requests-sum-vs-allocatable.png" alt="รูปที่ 12 ผลรวม requests เทียบ allocatable" width="900"><br>
  <em><b>รูปที่ 12</b> scheduler ดูผลรวม requests ของ Pod บนเรือเทียบ allocatable ไม่ได้ดูการใช้งานจริง เมื่อเต็มแล้ว Pod ตัวถัดไปต้อง Pending</em>
</p>

plugin `NodeResourcesFit` ตัดสินจาก **ตัวเลขที่ "จอง" ไว้ (requests)** ไม่ใช่การใช้งานจริง

```text
Node รับ Pod ใหม่ได้ ก็ต่อเมื่อ
  requests ของ Pod ใหม่ + ผลรวม requests ของ Pod ที่อยู่บน Node แล้ว  ≤  allocatable
(ตรวจแยกทีละทรัพยากร: cpu, memory, ephemeral-storage, จำนวน Pod)
```

กติกาที่ต้องรู้

1. **Pod ไม่ระบุ requests = นับเป็น 0** จึงวางได้เสมอ (ไม่เคย Insufficient) แต่เป็น QoS `BestEffort` ที่เสี่ยงถูกไล่เป็นลำดับแรกเมื่อเรือใกล้เต็ม (หัวข้อ 16)
2. **limits ไม่ถูกใช้ในการจัดวาง** limits เป็นเพดานตอนรัน ผลรวม limits บน Node จึงเกิน 100% ได้ (`describe node` เขียนไว้ว่า `Total limits may be over 100 percent, i.e., overcommitted.`)
3. **init container** นับแบบ "ค่าสูงสุด" requests ที่ใช้คำนวณของ Pod = ค่ามากกว่าระหว่าง (ผลรวมของ container หลัก + sidecar) กับ (init container ตัวที่ขอมากที่สุด + sidecar ที่เริ่มก่อนหน้า) เพราะ init container รันทีละตัวแล้วจบ ในร้านน้องส้ม (บทที่ 2) ค่าที่ใช้คือ `db` 100m/256Mi + `web` 100m/192Mi = **200m / 448Mi**
4. **ใช้งานจริงน้อยไม่ได้แปลว่าวางได้** Node ที่ CPU ว่าง 90% แต่ถูกจองครบแล้วก็รับ Pod ใหม่ไม่ได้

**ตัวอย่างคำนวณ** Node มี allocatable cpu `4` (4000m) ไม่มี Pod อื่น Pod แต่ละตัวขอ `cpu: 1500m`

| Pod ที่ | ผลรวม requests หลังวาง | ผล |
|:---:|---|---|
| 1 | 1500m ≤ 4000m | วางได้ |
| 2 | 3000m ≤ 4000m | วางได้ |
| 3 | 4500m > 4000m | **Pending** `Insufficient cpu` |

ผลจริงจาก LAB 1: `fit-pod` ขอ `cpu: 100m, memory: 64Mi` ถูกวางบน `lab-worker2` แล้ว `Allocated resources` ของ `lab-worker2` เพิ่มจาก 100m/50Mi (ของ `kindnet`) เป็น

```text
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                200m (0%)   0 (0%)
  memory             114Mi (0%)  0 (0%)
```

> **requests แก้ไม่ได้เมื่อ Pod เกิดแล้ว (ด้วย apply ปกติ):** ใน LAB 1 การ apply ไฟล์ที่ลด memory จาก `4000Gi` เป็น `256Mi` ได้ `Forbidden: pod updates may not change fields other than ...` วิธีปกติคือลบแล้วสร้างใหม่ (Kubernetes 1.37 มี subresource `resize` สำหรับปรับ resources ของ Pod ที่มีอยู่ ซึ่งในการทดลองใช้กับ Pod ที่ Pending ได้ด้วย แต่ไม่ใช่เนื้อหาหลักของบทนี้)

---

## 6. nodeName: ข้ามเจ้าหน้าที่จัดตู้

<p align="center" id="fig-13">
  <img src="images/13-nodename-bypass.png" alt="รูปที่ 13 nodeName ข้าม scheduler" width="900"><br>
  <em><b>รูปที่ 13</b> การใส่ nodeName คือเดินผ่านเจ้าหน้าที่จัดตู้ตรงไปหาต้นเรือเลย จึงไม่ผ่าน filter ของ scheduler ใช้เพื่อทดลองเท่านั้น</em>
</p>

ถ้าเราใส่ `spec.nodeName` เอง Pod จะมี nodeName ตั้งแต่เกิด scheduler จึงไม่หยิบไปพิจารณาเลย kubelet ของ Node ชื่อนั้นรับไปสร้างทันที

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pinned-pod
  labels:
    lab: "03"
spec:
  nodeName: lab-control-plane  # ระบุเรือเอง → scheduler ไม่ตรวจ taint ของ control-plane (ไม่มี toleration ก็ลงได้)
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลจริงจาก LAB 2

```text
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE                NOMINATED NODE   READINESS GATES
ghost-node-pod   0/1     Pending   0          7s    <none>       lab-worker9         <none>           <none>
pinned-pod       1/1     Running   0          7s    10.244.0.5   lab-control-plane   <none>           <none>
```

สิ่งที่เห็น

1. `pinned-pod` **Running บน `lab-control-plane` ทั้งที่ไม่มี toleration** เพราะ taint `NoSchedule` ถูกตรวจโดย scheduler ซึ่งถูกข้ามไป และ Events **ไม่มี `Scheduled`** (มีแค่ `Pulling`, `Pulled`, `Created`, `Started` จาก kubelet)
2. `ghost-node-pod` ระบุ `nodeName: lab-worker9` ซึ่งไม่มีอยู่จริง จึงค้าง `Pending` โดย **ไม่มี Event ใดเลย** (ไม่มี scheduler มาบอกเหตุผล และไม่มีต้นเรือชื่อนั้นมารับ) แล้ว **PodGC** ใน kube-controller-manager ลบทิ้งเองที่ประมาณ 62 วินาที (`"PodGC is force deleting Pod" pod="default/ghost-node-pod"`)

ข้อจำกัดของ nodeName

- ไม่ผ่าน filter ใด ๆ ของ scheduler (resources, affinity, taint `NoSchedule`) แต่ **kubelet ยังตรวจ admission ของตัวเอง** เช่น ถ้าทรัพยากรไม่พอ Pod จะถูกปฏิเสธเป็นสถานะ `OutOfcpu`/`OutOfmemory` และ taint แบบ `NoExecute` ยังมีผลไล่ Pod ตามปกติ
- ชื่อ Node ผิดหรือ Node ถูกลบ → Pod ค้างและถูก PodGC ลบ
- ผูกงานไว้กับเครื่องเดียว ยืดหยุ่นน้อยมาก

> **ใช้ nodeName เมื่อไร:** สำหรับดีบักหรือทดลองเท่านั้น งานจริงใช้ `nodeSelector` หรือ node affinity กับ label `kubernetes.io/hostname` แทน ซึ่งยังผ่านการตรวจของ scheduler ครบ

---

## 7. nodeSelector: ใบสั่งให้ขึ้นเรือที่มีธงตรงกัน

<p align="center" id="fig-14">
  <img src="images/14-nodeselector-flag-match.png" alt="รูปที่ 14 nodeSelector กับธงเรือ" width="900"><br>
  <em><b>รูปที่ 14</b> nodeSelector คือใบสั่งว่า Pod ต้องขึ้นเรือที่มีธงตรงกันเท่านั้น ถ้าไม่มีเรือลำไหนติดธงนั้น Pod จะ Pending</em>
</p>

`nodeSelector` เป็นวิธีที่ง่ายที่สุดในการบอกว่า "ต้องไปเรือที่มี label แบบนี้" เขียนเป็น map ของ `key: value` **ทุกคู่ต้องตรง (AND)**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: selector-pod
  labels:
    lab: "03"
spec:
  nodeSelector:               # ทุก key ต้องตรง (AND) ถ้าไม่มี node ไหนตรง → Pending
    fleet: fast
  containers:
    - name: web
      image: nginx:1.27-alpine
```

จัดการ label ของ Node ด้วย `kubectl label`

```bash
kubectl label node lab-worker2 fleet=fast deck=5     # ติด label (ได้หลายตัวพร้อมกัน)
kubectl label node lab-worker2 fleet=eco --overwrite # เปลี่ยนค่าเดิมต้องใส่ --overwrite
kubectl label node lab-worker2 fleet-                # ลบ label (ใส่ - ต่อท้าย key)
kubectl get nodes -L fleet,deck                      # ดูเป็นคอลัมน์
```

ถ้าลืม `--overwrite` ผลจริงคือ `error: 'fleet' already has a value (fast), and --overwrite is false`

พฤติกรรมที่เห็นใน LAB 3

1. apply ก่อนมี Node ใดติด `fleet=fast` → `Pending` พร้อม `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector.`
2. ติด label ให้ `lab-worker2` → scheduler ลองใหม่เองและวาง Pod บน `lab-worker2` ภายใน ~1 วินาที
3. **ลบ label ออกหลัง Pod รันแล้ว → Pod ยังอยู่ที่เดิม** เพราะ nodeSelector ตรวจตอนจัดวางเท่านั้น (แนวคิดเดียวกับ `IgnoredDuringExecution` ในหัวข้อ 8)

---

## 8. Node affinity: แม่เหล็กดึงไปหาธงเรือ

nodeSelector พูดได้แค่ "ต้องเท่ากับ" node affinity ขยายความสามารถให้ **พูดได้หลายแบบ** (ไม่เท่ากับ, มีอยู่, มากกว่า) และมีทั้งแบบ **ต้อง** และแบบ **อยากได้**

### 8.1 required กับ preferred

<p align="center" id="fig-15">
  <img src="images/15-node-affinity-required-preferred.png" alt="รูปที่ 15 node affinity required และ preferred" width="900"><br>
  <em><b>รูปที่ 15</b> node affinity แบบ required คือแม่เหล็กที่ต้องดูดติดเท่านั้น ส่วน preferred คือแม่เหล็กที่อยากได้ถ้าไม่มีก็ไปเรือลำอื่นได้</em>
</p>

| ฟิลด์ | แบบ | ทำงานในขั้น | ถ้าไม่มี Node ตรง |
|---|---|---|---|
| `requiredDuringSchedulingIgnoredDuringExecution` | ต้อง (hard) | Filtering | **Pending** |
| `preferredDuringSchedulingIgnoredDuringExecution` | อยากได้ (soft) มี `weight` 1–100 | Scoring | วางที่อื่นได้ตามปกติ |

ชื่อยาวแต่แยกอ่านได้ง่าย

- `requiredDuringScheduling` / `preferredDuringScheduling` = ตอน **จัดวาง** ต้อง / อยากได้
- `IgnoredDuringExecution` = ตอน **รันอยู่** ไม่สนใจ ถ้า label ของ Node เปลี่ยนจนไม่ตรงแล้ว Pod ที่รันอยู่ **ไม่ถูกไล่**

ตัวอย่าง required (ไฟล์จริงใน LAB 3)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-required-pod
  labels:
    lab: "03"
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:   # ต้องตรงตอนวาง / วางแล้วไม่ตรวจซ้ำ
        nodeSelectorTerms:          # หลาย term = OR
          - matchExpressions:       # หลาย expression ใน term เดียว = AND
              - key: fleet
                operator: In
                values: ["fast", "eco"]
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ตัวอย่าง preferred (ไฟล์จริงมี Pod หน้าตาเดียวกัน 4 ตัว `prefer-1..4` ที่นี่แสดงตัวเดียว)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: prefer-1
  labels:
    lab: "03"
    group: prefer
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
                operator: Exists
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลจริงจาก LAB 3

| สถานการณ์ | ผล |
|---|---|
| `lab-worker2` ติด `fleet=fast`, `lab-worker` ติด `fleet=eco` | `prefer-1..4` **อยู่บน lab-worker2 ทั้ง 4 ตัว** (weight 80 ชนะคะแนนด้านความว่างของเรือ) |
| เปลี่ยนเป็น `fleet=eco` ทั้งสองลำ (ไม่มีเรือ fast เลย) | `prefer-1..4` ยัง **Running ครบ** กระจาย 2 + 2 ส่วน `selector-pod` (nodeSelector `fleet: fast`) **Pending** |

> preferred **ไม่รับประกัน** ผล ขึ้นกับคะแนนรวมจาก plugin อื่นด้วย ถ้าต้องการรับประกันต้องใช้ required

### 8.2 Operators และการรวมเงื่อนไข

<p align="center" id="fig-16">
  <img src="images/16-affinity-operators.png" alt="รูปที่ 16 operator ของ node affinity" width="900"><br>
  <em><b>รูปที่ 16</b> ตัวดำเนินการของ node affinity: In, NotIn, Exists, DoesNotExist, Gt, Lt ใช้เทียบ label ของเรือ</em>
</p>

**ตารางที่ 5** operator ของ node affinity

| operator | `values` | ตรงเมื่อ | ตัวอย่าง |
|---|---|---|---|
| `In` | 1 ค่าขึ้นไป | ค่า label อยู่ในรายการ | `fleet In [fast, eco]` |
| `NotIn` | 1 ค่าขึ้นไป | ค่า label ไม่อยู่ในรายการ (รวมถึงไม่มี label นั้น) | `fleet NotIn [old]` |
| `Exists` | ไม่ต้องใส่ | มี key นี้ (ค่าอะไรก็ได้) | `cabin Exists` |
| `DoesNotExist` | ไม่ต้องใส่ | ไม่มี key นี้ | `maintenance DoesNotExist` |
| `Gt` | **1 ค่า** เป็นจำนวนเต็มในรูป string | ค่า label (ตีความเป็นจำนวนเต็ม) มากกว่า | `deck Gt ["3"]` |
| `Lt` | **1 ค่า** เป็นจำนวนเต็มในรูป string | ค่า label น้อยกว่า | `deck Lt ["3"]` |

ตัวอย่าง `Gt` (ไฟล์จริง) เมื่อ `lab-worker2` ติด `deck=5` และ `lab-worker` ติด `deck=2` Pod นี้ไปได้เฉพาะ `lab-worker2`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-gt-pod
  labels:
    lab: "03"
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: deck
                operator: Gt
                values: ["3"]         # ต้องใส่ค่าเดียว และเป็นตัวเลขในเครื่องหมายคำพูด
  containers:
    - name: web
      image: nginx:1.27-alpine
```

**กฎการรวมเงื่อนไข**

| โครงสร้าง | ความหมาย |
|---|---|
| หลาย `nodeSelectorTerms` | **OR** ผ่าน term ใด term หนึ่งก็พอ |
| หลาย `matchExpressions` ใน term เดียว | **AND** ต้องผ่านทุกข้อ |
| ใช้ `nodeSelector` ร่วมกับ node affinity | ต้องผ่าน **ทั้งคู่** |
| หลาย preferred term | คะแนนรวมของทุก term ที่ตรง (ตาม `weight`) |

ตัวอย่างโครงสร้าง "(fast **และ** deck > 3) **หรือ** (มี label `vip`)"

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: or-and-example
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:        # term ที่ 1: ต้องผ่านทั้งสองข้อ (AND)
              - key: fleet
                operator: In
                values: ["fast"]
              - key: deck
                operator: Gt
                values: ["3"]
          - matchExpressions:        # term ที่ 2: หรือ (OR) มี label vip
              - key: vip
                operator: Exists
  containers:
    - name: web
      image: nginx:1.27-alpine
```

> **เคล็ดลับ:** `NotIn` และ `DoesNotExist` ใช้ทำ "ห้ามไปเรือแบบนี้" ได้จากฝั่ง Pod (node anti-affinity) แต่ถ้าต้องการกัน **ทุก Pod** ออกจาก Node หนึ่ง ควรใช้ taint จากฝั่ง Node (หัวข้อ 11)

---
