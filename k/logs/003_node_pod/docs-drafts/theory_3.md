
## 14. Static Pod: ตู้ที่ต้นเรือดูแลเอง

### 14.1 แนวคิด

<p align="center" id="fig-32">
  <img src="images/32-static-pod-first-mate.png" alt="รูปที่ 32 static Pod ของต้นเรือ" width="900"><br>
  <em><b>รูปที่ 32</b> static Pod คือตู้ที่ต้นเรือ (kubelet) สร้างเองจากแฟ้มบนเรือ /etc/kubernetes/manifests ไม่ผ่านหอบังคับการและ scheduler</em>
</p>

**static Pod** คือ Pod ที่ kubelet สร้างเองจาก **ไฟล์ manifest บนเครื่อง** ในโฟลเดอร์ `staticPodPath` (ใน kind/kubeadm คือ `/etc/kubernetes/manifests`) โดย **ไม่ผ่าน scheduler และไม่ได้ถูกสร้างผ่าน API server**

- kubelet เฝ้าดูโฟลเดอร์ เจอไฟล์ใหม่ → สร้าง Pod, ไฟล์ถูกแก้ → สร้างใหม่, **ไฟล์ถูกลบ → ลบ Pod**
- เพื่อให้หอบังคับการ "เห็น" kubelet สร้าง **mirror pod** (เงา) ใน API server ชื่อ **`<ชื่อ Pod>-<ชื่อ Node>`** เช่น `static-snack-lab-worker`
- mirror pod มี annotation `kubernetes.io/config.mirror` และ `kubernetes.io/config.source: file` และ `ownerReferences` ชี้ไปที่ **Node** (ไม่ใช่ controller ใด)

ไฟล์จริงใน LAB 9 (ไม่ได้ `kubectl apply` แต่ copy ไปวางบนเรือ)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: static-snack           # ชื่อที่ kubectl เห็นจะต่อท้ายด้วยชื่อ node เช่น static-snack-lab-worker
  labels:
    app: static-snack
spec:
  containers:
    - name: web
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
```

ผลจริงจาก LAB 9

| การทดลอง | ผล |
|---|---|
| `docker cp` ไฟล์ไปที่ `lab-worker:/etc/kubernetes/manifests/` | mirror pod `static-snack-lab-worker` โผล่และ Ready เกือบทันที (< 1 วินาที) Events ไม่มี `Scheduled` |
| `kubectl delete pod static-snack-lab-worker` | คำสั่งค้างราว 65–80 วินาที (แสดง `Terminating`) แล้ว mirror pod **กลับมาใหม่** (UID ใหม่) โดย container จริงบนเรือ **ไม่ถูกรีสตาร์ต** (`crictl` ATTEMPT 0) |
| ลบไฟล์บนเรือ (`docker exec lab-worker rm ...`) | Pod หายจริงภายใน ~3 วินาที |

> **สรุป:** ลบ static Pod ผ่าน kubectl ไม่ได้ ต้องลบ **ไฟล์บนเรือ** เพราะ kubectl ลบได้แค่ "เงา" ส่วนต้นเรือยังถือแฟ้มอยู่

ข้อจำกัดของ static Pod

- อ้างอิง object อื่นใน API ไม่ได้ เช่น ConfigMap, Secret, ServiceAccount
- ไม่ถูกจัดการโดย scheduler หรือ controller ใด ไม่ถูก drain ไล่
- ใช้เฉพาะงานที่ต้องผูกกับเครื่องจริง ๆ

### 14.2 control plane ของ kind คือ static Pod

<p align="center" id="fig-33">
  <img src="images/33-control-plane-static-pods.png" alt="รูปที่ 33 static Pod บน control-plane" width="900"><br>
  <em><b>รูปที่ 33</b> บน lab-control-plane ส่วนประกอบหลัก etcd, kube-apiserver, kube-controller-manager, kube-scheduler เป็น static Pod ที่ kubelet ของหอรันเอง</em>
</p>

static Pod ตอบคำถามไก่กับไข่ว่า "**ใครวาง scheduler ถ้า scheduler ยังไม่เกิด**" คำตอบคือ kubelet บน `lab-control-plane` อ่านไฟล์ 4 ไฟล์แล้วรันเอง

```text
$ docker exec lab-control-plane ls /etc/kubernetes/manifests
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
```

mirror pod ของทั้ง 4 ตัวจึงมีชื่อลงท้ายด้วย `-lab-control-plane` เช่น `kube-scheduler-lab-control-plane` และใช้ IP ของ Node (`172.19.0.3`) เพราะใช้เครือข่ายของเครื่องโดยตรง

---

## 15. Downward API: ป้ายชื่อเรือที่ติดให้ตู้

<p align="center" id="fig-34">
  <img src="images/34-downward-api-nametag.png" alt="รูปที่ 34 Downward API ป้ายชื่อเรือ" width="900"><br>
  <em><b>รูปที่ 34</b> Downward API ให้ Pod รู้ข้อมูลตัวเอง เช่น spec.nodeName เป็น env NODE_NAME แล้วนำไปต่อข้อความด้วย $(NODE_NAME)</em>
</p>

แอปใน container ไม่รู้ว่าตัวเองอยู่บนเรือลำไหน **Downward API** ให้ kubelet ส่งข้อมูลของ Pod เข้า container ได้ ผ่าน env (`fieldRef`, `resourceFieldRef`) หรือผ่านไฟล์ (volume ชนิด `downwardAPI`)

**ตารางที่ 12** ฟิลด์ที่ใช้กับ env `fieldRef` ได้

| `fieldPath` | ค่า | ตัวอย่างผลจริง |
|---|---|---|
| `spec.nodeName` | ชื่อ Node ที่ Pod ถูกวาง | `lab-worker2` |
| `metadata.name` | ชื่อ Pod | `whereami` |
| `metadata.namespace` | namespace | `default` |
| `metadata.uid` | UID ของ Pod | – |
| `metadata.labels['<key>']` | ค่า label หนึ่งตัว | `metadata.labels['app']` |
| `metadata.annotations['<key>']` | ค่า annotation หนึ่งตัว | – |
| `status.podIP` | IP ของ Pod | `10.244.2.3` |
| `status.hostIP` | IP ของ Node | `172.19.0.2` |
| `spec.serviceAccountName` | ชื่อ ServiceAccount | – |

`resourceFieldRef` ให้ค่า requests/limits ของ container เช่น `limits.memory` ส่วน label/annotation **ทั้งหมด** ต้องใช้แบบ volume

**การอ้างตัวแปรด้วย `$(VAR)`** ใน `value`, `command`, `args` อ้าง env ตัวอื่น **ที่ประกาศก่อนหน้าในลิสต์** ได้ Kubernetes แทนค่าให้ตอนสร้าง container (ไม่ต้องมี shell) ถ้าอ้างตัวที่ไม่มี ข้อความ `$(VAR)` จะคงอยู่ตามตัวอักษร และ `$$(VAR)` ใช้ escape ให้ได้ข้อความ `$(VAR)` จริง ๆ

ไฟล์จริงจาก LAB 2

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: whereami
  labels:
    lab: "03"
spec:
  terminationGracePeriodSeconds: 1
  containers:
    - name: app
      image: busybox:1.36
      env:
        - name: NODE_NAME            # ชื่อ node ที่ Pod ถูกวาง (ต้นเรือเติมให้ตอนสร้าง container)
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP               # IP ของ Pod (10.244.x.x)
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: HOST_IP              # IP ของ node (172.18.0.x ใน kind)
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: GREETING             # $(ชื่อตัวแปร) อ้างตัวแปรที่ประกาศ "ก่อนหน้า" ในลิสต์นี้ได้
          value: "สวัสดีจาก $(POD_NAME) บนเรือ $(NODE_NAME)"
      command: ["sh", "-c", "echo \"$GREETING (Pod IP $POD_IP, Node IP $HOST_IP)\"; sleep 3600"]
```

(comment ในไฟล์เขียนว่า `172.18.0.x` แต่ในการทดลองจริง Node ได้ `172.19.0.x` ช่วงนี้ขึ้นกับเครือข่าย Docker ของแต่ละเครื่อง)

ผลจริง

```text
$ kubectl logs whereami
สวัสดีจาก whereami บนเรือ lab-worker2 (Pod IP 10.244.2.3, Node IP 172.19.0.2)
```

ใน LAB สุดท้าย ร้านแต่ละสาขาใช้เทคนิคเดียวกันตั้งชื่อร้านตามเรือ

```yaml
env:
  - name: NODE_NAME          # Downward API: ชื่อเรือที่ Pod นี้ถูกวาง (ต้องประกาศก่อน SHOP_NAME)
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
  - name: SHOP_NAME          # $(NODE_NAME) ถูกแทนค่าตอนสร้าง container
    value: "ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"
```

ผลจริง `printenv SHOP_NAME` ได้ `ร้านอาหารแมวน้องส้ม สาขา lab-worker` และหน้าเว็บแสดงชื่อสาขาตามเรือ

> **ข้อควรจำ:** ค่าจาก env ถูกกำหนด **ตอนสร้าง container** ครั้งเดียว ถ้าค่าต้นทางเปลี่ยนภายหลัง (เช่น label) env ไม่เปลี่ยนตาม ต้องใช้แบบ volume ถ้าต้องการค่าที่อัปเดต

---

## 16. QoS กับ node-pressure eviction

<p align="center" id="fig-35">
  <img src="images/35-qos-node-pressure-eviction.png" alt="รูปที่ 35 QoS กับ node-pressure eviction" width="900"><br>
  <em><b>รูปที่ 35</b> เมื่อเรือใกล้เต็ม (MemoryPressure) kubelet ไล่ Pod ออกตามลำดับ QoS: BestEffort ก่อน, Burstable ที่ใช้เกิน requests, Guaranteed หลังสุด</em>
</p>

ทบทวน QoS จากบทที่ 2

| QoS | เงื่อนไข |
|---|---|
| `Guaranteed` | ทุก container มี requests = limits ทั้ง cpu และ memory |
| `Burstable` | มี requests หรือ limits อย่างน้อยหนึ่งค่า แต่ไม่เข้าเงื่อนไข Guaranteed |
| `BestEffort` | ไม่มี requests/limits เลย |

**node-pressure eviction** คือการที่ **kubelet** ไล่ Pod ออกจากเรือเองเมื่อทรัพยากรบนเรือใกล้หมด ตามเกณฑ์ eviction threshold เช่น `memory.available<100Mi` (ค่าเริ่มต้นแบบ hard) เมื่อถึงเกณฑ์

1. condition `MemoryPressure` (หรือ `DiskPressure`, `PIDPressure`) เป็น `True` และระบบติด taint `node.kubernetes.io/memory-pressure:NoSchedule` กัน Pod ใหม่
2. kubelet เลือก Pod ที่จะไล่ตามลำดับ: (1) Pod ที่ **ใช้เกิน requests** ก่อน (2) priority ต่ำกว่าก่อน (3) ใช้เกิน requests มากกว่าก่อน ผลในทางปฏิบัติคือ BestEffort มักโดนก่อน ตามด้วย Burstable ที่ใช้เกิน ส่วน Guaranteed และ Pod ที่ใช้ไม่เกิน requests ถูกไล่หลังสุด
3. Pod ที่ถูกไล่มีสถานะ `Failed` reason `Evicted`

**ตารางที่ 13** การไล่ Pod แบบต่าง ๆ ในบทนี้

| ชนิด | ใครทำ | เหตุ | ผลต่อ Pod |
|---|---|---|---|
| OOMKilled (บทที่ 2) | kernel | container ใช้ memory เกิน **limits ของตัวเอง** | container ถูกฆ่าและ restart ใน Pod เดิม |
| node-pressure eviction | kubelet | **ทั้งเรือ** ทรัพยากรใกล้หมด | ทั้ง Pod ถูกไล่ (`Evicted`) |
| taint `NoExecute` | taint eviction controller | Pod ไม่มีบัตรผ่าน / หมดเวลา `tolerationSeconds` | Pod ถูกลบ |
| drain | ผู้ดูแล (`kubectl drain`) | ซ่อมบำรุงเรือ | Pod ถูกไล่ผ่าน Eviction API |
| preemption | scheduler | ต้องเปิดที่ให้ Pod priority สูงกว่า | Pod ถูกลบ (หัวข้อ 17) |

> บทนี้ **ไม่ทดลอง** node-pressure eviction ใน LAB เพราะต้องทำให้หน่วยความจำของเครื่องเกือบเต็ม ซึ่งจะทำให้ k8s-lab และเครื่องนักศึกษาทั้งเครื่องช้าหรือค้าง

---

## 17. Priority และ Preemption

<p align="center" id="fig-36">
  <img src="images/36-priority-preemption.png" alt="รูปที่ 36 Priority และ Preemption" width="900"><br>
  <em><b>รูปที่ 36</b> PriorityClass ให้ Pod สำคัญแซงคิวได้ เมื่อเรือเต็ม scheduler อาจไล่ Pod priority ต่ำออก (preemption) เพื่อเปิดที่ให้</em>
</p>

**PriorityClass** คือ object ระดับคลัสเตอร์ที่กำหนด "ความสำคัญ" เป็นตัวเลข Pod อ้างด้วย `priorityClassName`

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: vip-order
value: 100000                        # ยิ่งมากยิ่งสำคัญ
globalDefault: false                 # true = ใช้กับ Pod ที่ไม่ระบุ priorityClassName (มีได้ class เดียว)
preemptionPolicy: PreemptLowerPriority   # หรือ Never = แซงคิวได้แต่ไม่ไล่ใคร
description: "ออเดอร์ด่วน VIP ของร้านน้องส้ม"
---
apiVersion: v1
kind: Pod
metadata:
  name: vip-order-pod
spec:
  priorityClassName: vip-order
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลของ priority

1. **แซงคิว:** Pod priority สูงถูกหยิบไปจัดวางก่อน
2. **Preemption:** ถ้าไม่มี Node ใดรับได้ scheduler หา Node ที่ "ถ้าไล่ Pod priority ต่ำกว่าบางตัวออกแล้วจะวางได้" แล้วลบ Pod เหยื่อ (victim) เพื่อเปิดที่ ส่วน `preemption: ...` ท้ายข้อความ FailedScheduling คือผลการคิดเรื่องนี้ เช่น `Preemption is not helpful for scheduling` (ไล่ใครก็ไม่ช่วย) หรือ `No preemption victims found for incoming pod` (ไม่มี Pod ที่ไล่ได้)
3. class ระบบที่มีมาให้: `system-cluster-critical` และ `system-node-critical` (ค่าสูงมาก) สำหรับองค์ประกอบสำคัญ เช่น CoreDNS และ Pod บน control-plane

> **ใช้อย่างระวัง:** ถ้าทุกคนตั้ง priority สูงหมดก็ไม่มีความหมาย และ preemption อาจทำให้งานอื่นสะดุด บทนี้ **ไม่ทดลองใน LAB**

---

## 18. เลือกเครื่องมือจัดวางแบบไหนเมื่อไร

<p align="center" id="fig-37">
  <img src="images/37-placement-cheatsheet.png" alt="รูปที่ 37 ตารางเลือกเครื่องมือจัดวาง" width="900"><br>
  <em><b>รูปที่ 37</b> ตารางเลือกเครื่องมือจัดวาง: ต้องการเรือชนิดหนึ่ง ใช้ nodeSelector/node affinity, อยู่ใกล้/ห่าง Pod อื่น ใช้ pod (anti-)affinity, กระจาย ใช้ spread, กันเรือ ใช้ taint</em>
</p>

**ตารางที่ 14** สรุปเครื่องมือจัดวาง

| เป้าหมาย | เครื่องมือ | hard/soft | เขียนที่ | ตัวอย่างใน LAB |
|---|---|---|---|---|
| ระบุเรือเจาะจงเพื่อทดลอง | `nodeName` | ข้าม scheduler | Pod | `pinned-pod` |
| ต้องอยู่เรือชนิดหนึ่ง | `nodeSelector` / required node affinity | hard | Pod (+label บน Node) | `selector-pod`, `affinity-gt-pod`, สาขาร้าน `shop=open` |
| อยากอยู่เรือชนิดหนึ่ง | preferred node affinity | soft | Pod | `prefer-1..4` |
| อยู่ใกล้ Pod อื่น | podAffinity | hard/soft | Pod | `web-near-cache` |
| แยกห่างจาก Pod อื่น (1 ต่อโดเมน) | podAntiAffinity | hard/soft | Pod | `crew-1..3`, `deckhand-1..3`, สาขาร้านคนละเรือ |
| กระจายให้สมดุล | `topologySpreadConstraints` | hard (`DoNotSchedule`) / soft (`ScheduleAnyway`) | Pod | `spread-*`, `honor-*`, `cargo-*` |
| กันคนทั่วไปออกจากเรือ | taint + toleration (+ affinity ถ้าต้องการดึงเข้า) | hard (`NoSchedule`/`NoExecute`) / soft (`PreferNoSchedule`) | Node + Pod | `dedicated=vip`, `maintenance=true` |
| ซ่อมเรือ | `cordon` / `drain` / `uncordon` | – | Node | LAB 7, LAB 10 |
| ให้ Pod ทนเรือล่มได้นาน/สั้น | toleration `unreachable`/`not-ready` + `tolerationSeconds` | – | Pod | `fog-fast`, สาขาร้าน 60 วินาที |
| Pod ประจำเครื่องที่ kubelet ดูแล | static Pod | – | ไฟล์บน Node | `static-snack` |
| ให้งานสำคัญได้ที่ก่อน | PriorityClass | – | คลัสเตอร์ + Pod | (ไม่ทดลอง) |

**ลำดับการคิดเมื่อออกแบบ**

1. งานนี้ต้องการเรือแบบไหน → label + nodeSelector/affinity
2. มีเรือที่ต้องกันไว้ให้งานเฉพาะไหม → taint บน Node + toleration ในงานนั้น
3. สำเนาหลายตัวต้องแยกเรือไหม → anti-affinity (1 ต่อเรือ) หรือ spread (สมดุล)
4. ตรวจผลด้วย `kubectl get pod -o wide` และถ้า Pending ให้อ่าน `FailedScheduling`

---

## 19. ปูทางบทหน้า: Deployment และ Service

<p align="center" id="fig-38">
  <img src="images/38-preview-deployment-service.png" alt="รูปที่ 38 ปูทาง Deployment และ Service" width="900"><br>
  <em><b>รูปที่ 38</b> Pod เดี่ยวหายแล้วไม่มีใครสร้างใหม่ บทหน้าจะใช้ Deployment ดูแลจำนวน Pod และ Service เป็นที่อยู่คงที่ของทุกสาขา</em>
</p>

ใน LAB สุดท้ายของบทนี้ น้องส้มเปิด 2 สาขาบนเรือคนละลำได้สำเร็จ แต่จะเจอปัญหาต่อไปนี้ซึ่งบทถัดไปจะแก้

| ปัญหาที่เจอในบทนี้ | ทรัพยากรในบทถัดไป | แนวคิด |
|---|---|---|
| drain หรือเรือล่มแล้ว **สาขาหายไม่มีใครเปิดใหม่** | **Deployment** (ผ่าน ReplicaSet) | บอกว่า "ต้องการ 2 สาขา" controller คอยสร้าง Pod ใหม่บนเรือที่ยังดีให้เอง |
| ต้องก๊อปปี้ YAML เป็น `som-shop-a`, `som-shop-b`, `som-shop-c` | Pod template ใน Deployment | เขียน Pod ครั้งเดียว ใส่ affinity/anti-affinity/spread ที่เรียนวันนี้ไว้ใน template ได้เลย |
| ลูกค้าต้องจำ port ต่างกันของแต่ละสาขา (3001, 3002) และ port-forward หลุดเมื่อ Pod หาย | **Service** | ที่อยู่เดียวคงที่ กระจายลูกค้าไปทุกสาขาที่ Ready |
| ข้อมูลแต่ละสาขาแยกกันและหายเมื่อ Pod หาย (emptyDir) | ฐานข้อมูลกลาง + PersistentVolumeClaim / StatefulSet | เว็บหลายตัวใช้ฐานข้อมูลเดียวกัน และข้อมูลอยู่นานกว่า Pod |

ความรู้ในบทนี้ไม่สูญเปล่า เพราะ controller เหล่านั้น **ยังใช้ scheduler ตัวเดิม** ทุก Pod ที่ Deployment สร้างก็ผ่าน Filtering/Scoring และกฎ affinity, spread, taint/toleration ชุดเดียวกับที่เรียนวันนี้

---

## 20. สรุปและคำถามทบทวน

<p align="center" id="fig-39">
  <img src="images/39-summary-fleet-master.png" alt="รูปที่ 39 สรุปบทที่ 3" width="900"><br>
  <em><b>รูปที่ 39</b> สรุปบท: scheduler เลือกเรือด้วย filter/score, เราช่วยกำหนดด้วย label, affinity, spread, taint และดูแลเรือด้วย cordon/drain</em>
</p>

### 20.1 สรุป

1. **Node** มี kubelet (ต้นเรือ), container runtime, kube-proxy และ CNI ใน kind แต่ละ Node คือ Docker container ใน k8s-lab ทุก Node เห็น CPU/RAM ของเครื่องเดียวกัน
2. **Node object** บอก labels, taints, capacity/allocatable, conditions และ heartbeat (Lease ต่ออายุทุก ~10 วินาที) อ่านครบได้จาก `kubectl describe node` โดยเฉพาะ `Allocated resources`
3. **kube-scheduler** เลือก Node ให้ Pod ที่ยังไม่มี `nodeName` ด้วย **Filtering → Scoring → Binding** ครั้งเดียว ไม่ย้ายภายหลัง ถ้าไม่มี Node ผ่าน filter Pod `Pending` และมี `FailedScheduling` ที่นับเหตุผลครบทุก Node
4. scheduler ใช้ **ผลรวม requests เทียบ allocatable** ไม่ใช้การใช้งานจริงและไม่ใช้ limits
5. `nodeName` ข้าม scheduler (ทดลองเท่านั้น) `nodeSelector` = ต้องตรงทุก label, node affinity เพิ่ม operator (`In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt`) และแบบ required/preferred ทั้งหมดเป็น `IgnoredDuringExecution`
6. pod affinity/anti-affinity เลือกเรือจาก Pod ที่อยู่แล้ว โดย `topologyKey` นิยาม "ที่เดียวกัน" ส่วน topology spread คุมความต่างด้วย `maxSkew` และใน kind ต้องตั้ง `nodeTaintsPolicy: Honor` ไม่งั้น control-plane ถูกนับเป็นโดเมน
7. **taint** อยู่บน Node, **toleration** อยู่บน Pod `NoSchedule` กันของใหม่, `PreferNoSchedule` เลี่ยง, `NoExecute` ไล่ของเดิมด้วย และ **toleration ไม่ใช่แรงดึงดูด**
8. `cordon` กันของใหม่, `drain` = cordon + ไล่ (Pod เดี่ยวต้อง `--force` และหายถาวร), `uncordon` รับของใหม่แต่ของเก่าไม่กลับ
9. เรือล่ม → NotReady ~45–50 วินาที → taint `unreachable` → Pod ถูกไล่หลังอีก 300 วินาที (ค่าเริ่มต้น) → ค้าง Terminating จนเรือกลับ → **Pod เดี่ยวไม่ถูกสร้างใหม่**
10. static Pod ถูกสร้างจากไฟล์บนเรือโดย kubelet (control plane ของ kind ก็เป็น static Pod) และ Downward API ให้ Pod รู้ชื่อเรือ/IP ของตัวเอง

> **ข้อควรจำก่อนเข้า LAB**
> - คำสั่ง `docker stop/start lab-worker2`, `docker exec lab-worker ...`, `docker cp ... lab-worker:...` รัน **ใน SSH session ของ k8s-lab** ไม่ใช่เครื่องตัวเอง และ **ห้าม `docker stop lab-control-plane`**
> - ทุกครั้งที่ drain (แม้ error) ต้อง `uncordon` และทุกครั้งที่ติด label/taint ต้องลบคืนตอนเก็บกวาด
> - Pending ไม่ต้องตกใจ อ่าน `kubectl describe pod` ส่วน Events ก่อนเสมอ
> - ตำแหน่งที่ scheduler เลือก (lab-worker หรือ lab-worker2) อาจต่างจากเอกสาร ให้ดูจาก `kubectl get pod -o wide` ทุกครั้ง

### 20.2 คำถามทบทวน

**1. ใครเป็นผู้ "ตัดสินใจ" และใครเป็นผู้ "ลงมือ" เมื่อ Pod ใหม่ถูกวางบน Node และเราดูจากตรงไหนได้ว่าแต่ละขั้นเกิดขึ้นแล้ว**

<details>
<summary>แนวคำตอบ</summary>

kube-scheduler (บน control plane) เป็นผู้ตัดสินใจ โดยเลือก Node แล้วเขียน binding ทำให้ `spec.nodeName` ถูกเติม (Event `Scheduled` จาก `default-scheduler`) ส่วน kubelet บน Node นั้นเป็นผู้ลงมือสั่ง container runtime ดึง image และสร้าง container (Event `Pulled`, `Created`, `Started` จาก `kubelet`) ดูได้จาก `kubectl describe pod` ส่วน Events และคอลัมน์ `NODE` ของ `kubectl get pod -o wide`
</details>

**2. allocatable ต่างจาก capacity อย่างไร ทำไมใน kind สองค่านี้จึงเท่ากัน และทำไมคลัสเตอร์ kind 3 Node จึงไม่ได้มีทรัพยากรจริง 3 เท่า**

<details>
<summary>แนวคำตอบ</summary>

allocatable = capacity − kube-reserved − system-reserved − eviction-threshold คือส่วนที่ scheduler ยอมให้ Pod จอง ใน kind ไม่ได้ตั้ง reserved จึงเท่ากัน (ผลจริง cpu 32 ทั้งสองค่า) และเพราะทุก Node เป็น container บนเครื่องเดียวกัน แต่ละ Node จึงรายงาน CPU/RAM ของเครื่องจริงทั้งเครื่อง ทรัพยากรจริงมีชุดเดียวที่ทั้ง 3 Node ใช้ร่วมกัน
</details>

**3. อ่านข้อความนี้แล้วอธิบายว่าเกิดอะไรขึ้นกับแต่ละ Node:** `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.`

<details>
<summary>แนวคำตอบ</summary>

ไม่มี Node ใดผ่าน filter: control-plane 1 ลำตกเพราะมี taint ที่ Pod ไม่มี toleration, worker 2 ลำตกเพราะ memory ที่เหลือ (allocatable − ผลรวม requests เดิม) ไม่พอ requests ของ Pod ส่วน preemption บอกว่าแม้ไล่ Pod อื่นออกก็ยังวางไม่ได้ (เพราะขอเกินทั้งเครื่อง) ทางแก้คือลด requests แล้วสร้าง Pod ใหม่
</details>

**4. Pod ที่ไม่ระบุ requests เลยจะถูก scheduler มองอย่างไร ข้อดีและข้อเสียคืออะไร**

<details>
<summary>แนวคำตอบ</summary>

นับ requests เป็น 0 จึงผ่าน `NodeResourcesFit` เสมอ (วางได้ง่าย) แต่เป็น QoS BestEffort ซึ่งไม่มีการรับประกันทรัพยากร และมักถูก kubelet ไล่เป็นกลุ่มแรกเมื่อเรือเกิด MemoryPressure นอกจากนี้ scheduler ก็ไม่รู้ว่าเรือเต็มจริงหรือยัง อาจทำให้ Node แน่นเกินไป
</details>

**5. ทำไม `pinned-pod` ที่ใส่ `nodeName: lab-control-plane` จึงรันบน control-plane ได้ทั้งที่ไม่มี toleration และทำไม `ghost-node-pod` ที่ใส่ `nodeName: lab-worker9` จึงไม่มี Event อะไรเลย**

<details>
<summary>แนวคำตอบ</summary>

taint `NoSchedule` ถูกบังคับใช้โดย scheduler แต่ Pod ที่มี nodeName ไม่ผ่าน scheduler เลย kubelet บน control-plane จึงรับไปรันตรง ๆ (Events ไม่มี `Scheduled`) ส่วน `lab-worker9` ไม่มีอยู่จริง ไม่มี scheduler มาเขียน FailedScheduling และไม่มี kubelet ชื่อนั้นมารับ Pod จึงค้าง Pending เงียบ ๆ จน PodGC ลบทิ้ง (~62 วินาทีในการทดลอง)
</details>

**6. เขียน node affinity ที่หมายความว่า "ต้องไปเรือที่ `disk=ssd` และ `deck` มากกว่า 3 หรือเรือที่มี label `vip` (ค่าอะไรก็ได้)"**

<details>
<summary>แนวคำตอบ</summary>

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:        # term 1: AND
            - key: disk
              operator: In
              values: ["ssd"]
            - key: deck
              operator: Gt
              values: ["3"]
        - matchExpressions:        # term 2: OR กับ term 1
            - key: vip
              operator: Exists
```

หลาย `nodeSelectorTerms` เป็น OR หลาย `matchExpressions` ใน term เดียวเป็น AND และ `Gt` ต้องมีค่าเดียวเป็นตัวเลขในรูป string
</details>

**7. Pod ที่ใช้ nodeSelector `fleet: fast` รันอยู่บน `lab-worker2` แล้วผู้ดูแลลบ label `fleet` ออกจาก `lab-worker2` จะเกิดอะไรขึ้น เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

Pod รันต่อที่เดิม (ผลจริงใน LAB 3) เพราะ nodeSelector และ node affinity แบบ `...IgnoredDuringExecution` ตรวจเฉพาะตอนจัดวาง แต่ถ้าลบ Pod แล้วสร้างใหม่ Pod ใหม่จะ Pending เพราะไม่มีเรือ `fleet=fast`
</details>

**8. ทำไม `crew-3` จึง Pending แต่ `deckhand-3` Running ทั้งที่ทั้งสองกลุ่มมี 3 Pod และมี worker 2 ลำเท่ากัน**

<details>
<summary>แนวคำตอบ</summary>

`crew-*` ใช้ **required** podAntiAffinity กับ `topologyKey: kubernetes.io/hostname` คือห้ามอยู่เรือเดียวกันเด็ดขาด worker 2 ลำรับได้ 2 ตัว ตัวที่ 3 ไม่มีที่ (control-plane ก็มี taint) จึง Pending ส่วน `deckhand-*` ใช้ **preferred** ซึ่งเป็นแค่คะแนน เมื่อไม่มีเรือว่างก็ยอมอยู่ซ้ำ จึง Running ครบแบบ 2 + 1
</details>

**9. ใน kind ทำไม Pod ตัวที่ 3 ของ topology spread (maxSkew 1, hostname, DoNotSchedule) จึง Pending ทั้งที่ worker ยังว่าง และแก้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ค่าเริ่มต้น `nodeTaintsPolicy: Ignore` ทำให้ `lab-control-plane` (ที่มี taint) ถูกนับเป็นโดเมนที่มี 0 Pod เสมอ หลังวาง 1 + 1 บน worker ตัวที่ 3 จะทำให้ skew = 2 − 0 = 2 เกิน maxSkew จึง Pending แก้ด้วย `nodeTaintsPolicy: Honor` (ผลจริง 2 : 2) หรือใช้ node affinity เลือกเฉพาะ worker (ด้วย `nodeAffinityPolicy: Honor` ซึ่งเป็นค่าเริ่มต้น)
</details>

**10. ผู้ดูแลติด taint `gpu=true:NoSchedule` ให้ Node GPU และใส่ toleration ที่ตรงให้ Pod งาน AI แต่พบว่า Pod งาน AI บางตัวไปอยู่บน Node ธรรมดา เกิดจากอะไรและแก้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

toleration ไม่ใช่แรงดึงดูด มันแค่ทำให้ Node GPU ไม่ถูกตัดทิ้ง Pod จึงยังไปที่ Node ธรรมดาได้ตามคะแนน แก้โดยติด label ให้ Node GPU (เช่น `gpu=true`) แล้วใส่ nodeSelector หรือ required node affinity ใน Pod งาน AI ร่วมกับ toleration เดิม (taint + toleration + affinity)
</details>

**11. ติด taint `maintenance=true:NoExecute` บน Node ที่มี Pod 3 ตัว: A ไม่มี toleration, B มี toleration ตรงพร้อม `tolerationSeconds: 30`, C มี toleration ตรงไม่ระบุเวลา ผลของแต่ละตัวคืออะไร และ Pod เดี่ยวที่ถูกไล่จะไปเกิดใหม่ที่ไหน**

<details>
<summary>แนวคำตอบ</summary>

A ถูกไล่ทันที (ในการทดลอง < 1 วินาที), B อยู่ได้ประมาณ 30 วินาทีแล้วถูกไล่, C อยู่ต่อ (Event `TaintManagerEviction ... Marking for deletion Pod ...`) Pod เดี่ยวที่ถูกไล่จะถูกลบทิ้ง **ไม่ไปเกิดใหม่ที่ไหน** เพราะไม่มี controller ดูแล
</details>

**12. `kubectl cordon` กับ `kubectl drain` ต่างกันอย่างไร ทำไม drain ของ LAB 7 จึงต้องใช้ทั้ง `--ignore-daemonsets`, `--delete-emptydir-data` และ `--force`**

<details>
<summary>แนวคำตอบ</summary>

cordon แค่ทำเครื่องหมายว่าไม่รับ Pod ใหม่ (`SchedulingDisabled`) Pod เดิมอยู่ต่อ ส่วน drain = cordon + ไล่ Pod ทีละตัว ใน LAB 7 บนเรือมี Pod ระบบ `kindnet`/`kube-proxy` ที่ระบบดูแลให้ทุกเรือมีหนึ่งตัว (ต้อง `--ignore-daemonsets` เพื่อข้าม), มี `pantry` ที่ใช้ emptyDir (ข้อมูลจะหาย ต้อง `--delete-emptydir-data`) และมี Pod เดี่ยว `cargo-2`, `cargo-4` ที่ลบแล้วไม่มีใครสร้างคืน (ต้อง `--force`)
</details>

**13. เรือ `lab-worker2` ล่มด้วย `docker stop` จงเรียงเหตุการณ์ที่เกิดกับ Node และ Pod `fog-default` (ไม่ได้ตั้ง toleration เอง) พร้อมเวลาโดยประมาณ จนถึงหลัง `docker start`**

<details>
<summary>แนวคำตอบ</summary>

0 วินาที เรือหยุด (Node ยังแสดง Ready) → ~45–50 วินาที Node `NotReady` (Ready=Unknown, `Kubelet stopped posting node status.`) ระบบติด taint `node.kubernetes.io/unreachable:NoSchedule` และ `:NoExecute` Pod ยังแสดง `Running` แต่ Ready=False → ครบ 300 วินาทีหลัง NotReady (บัตรผ่านเริ่มต้นจาก DefaultTolerationSeconds) Pod ถูกไล่และค้าง `Terminating` (ผลจริง +345 วินาทีจาก stop) → `docker start` แล้ว ~2 วินาที Node Ready, ~5 วินาที Pod หายจริง, taint หายภายในไม่กี่วินาที → ไม่มี Pod ใหม่เกิดขึ้น
</details>

**14. ทำไม Pod บนเรือที่ล่มจึงค้าง `Terminating` แทนที่จะหายไปทันที และทำไม `kubectl exec`/`logs` จึงใช้ไม่ได้**

<details>
<summary>แนวคำตอบ</summary>

การลบ Pod แบบปกติต้องรอให้ kubelet ยืนยันว่า container หยุดแล้ว แต่ kubelet ติดต่อไม่ได้ ระบบไม่รู้ว่า container ยังรันอยู่หรือไม่ จึงคง object ไว้ในสถานะ Terminating จนกว่า kubelet จะกลับมายืนยัน ส่วน exec/logs/port-forward ต้องเชื่อมต่อผ่าน API server ไปที่ kubelet port 10250 บน Node ซึ่งติดต่อไม่ได้ จึงได้ error `dial tcp 172.19.0.2:10250: connect: no route to host`
</details>

**15. static Pod ต่างจาก Pod ทั่วไปอย่างไร ถ้าลบด้วย `kubectl delete pod static-snack-lab-worker` จะเกิดอะไรขึ้น และต้องลบอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

static Pod ถูก kubelet สร้างจากไฟล์ใน `/etc/kubernetes/manifests` บน Node โดยไม่ผ่าน scheduler สิ่งที่ API server เห็นเป็นเพียง mirror pod ชื่อ `<ชื่อ>-<node>` เมื่อ kubectl delete จะลบได้แค่เงา (ในการทดลองค้าง Terminating ราว 1 นาที) แล้ว kubelet สร้าง mirror กลับมาใหม่ โดย container จริงไม่ถูกรีสตาร์ต การลบจริงต้องลบไฟล์บน Node เช่น `docker exec lab-worker rm /etc/kubernetes/manifests/static-snack.yaml`
</details>

**16. จงเขียน env ที่ทำให้ container มีตัวแปร `SHOP_NAME="ร้านอาหารแมวน้องส้ม สาขา <ชื่อ Node>"` และอธิบายว่าทำไมลำดับของ env จึงสำคัญ**

<details>
<summary>แนวคำตอบ</summary>

```yaml
env:
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
  - name: SHOP_NAME
    value: "ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"
```

`$(VAR)` อ้างได้เฉพาะตัวแปรที่ประกาศ **ก่อนหน้า** ในลิสต์ ถ้าสลับลำดับ `SHOP_NAME` จะได้ข้อความ `$(NODE_NAME)` ตามตัวอักษรแทนชื่อ Node
</details>

**17. OOMKilled, node-pressure eviction และการไล่ด้วย taint `NoExecute` ต่างกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

OOMKilled: kernel ฆ่า **container** ที่ใช้ memory เกิน limits ของตัวเอง แล้ว kubelet restart ใน Pod เดิม / node-pressure eviction: **kubelet** ไล่ทั้ง **Pod** เมื่อทรัพยากรของทั้งเรือใกล้หมด เลือกตามการใช้เกิน requests และ priority (BestEffort มักโดนก่อน) Pod เป็น `Failed`/`Evicted` / NoExecute: **taint eviction controller** ลบ Pod ที่ไม่มี toleration หรือหมด `tolerationSeconds` ไม่เกี่ยวกับการใช้ทรัพยากร
</details>

**18. ถ้าน้องส้มต้องการ (ก) สาขาร้านอยู่บนเรือที่ติดธง `shop=open` เท่านั้น (ข) สองสาขาห้ามอยู่เรือเดียวกัน (ค) ถ้าเรือล่มให้ยอมรอแค่ 60 วินาที ต้องใช้กลไกอะไรบ้าง**

<details>
<summary>แนวคำตอบ</summary>

(ก) required node affinity `shop In ["open"]` (+ `kubectl label node ... shop=open`) (ข) required podAntiAffinity เลือก label ของสาขา (`app: som-shop`, `part: branch`) กับ `topologyKey: kubernetes.io/hostname` (ค) toleration `node.kubernetes.io/unreachable` และ `node.kubernetes.io/not-ready` แบบ `NoExecute` พร้อม `tolerationSeconds: 60` ซึ่งเป็นสิ่งที่ LAB สุดท้ายใช้จริง
</details>

---

## 21. เอกสารอ้างอิง

1. The Kubernetes Authors. *Nodes*. https://kubernetes.io/docs/concepts/architecture/nodes/
2. The Kubernetes Authors. *Node Status*. https://kubernetes.io/docs/reference/node/node-status/
3. The Kubernetes Authors. *Kubernetes Scheduler*. https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/
4. The Kubernetes Authors. *Scheduling Framework*. https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/
5. The Kubernetes Authors. *Assigning Pods to Nodes* (nodeSelector, affinity, nodeName). https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/
6. The Kubernetes Authors. *Pod Topology Spread Constraints*. https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
7. The Kubernetes Authors. *Taints and Tolerations*. https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
8. The Kubernetes Authors. *Safely Drain a Node*. https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/
9. The Kubernetes Authors. *Node-pressure Eviction*. https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/
10. The Kubernetes Authors. *Pod Priority and Preemption*. https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/
11. The Kubernetes Authors. *Create static Pods*. https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/
12. The Kubernetes Authors. *Downward API*. https://kubernetes.io/docs/concepts/workloads/pods/downward-api/
13. The Kubernetes Authors. *Expose Pod Information to Containers Through Environment Variables*. https://kubernetes.io/docs/tasks/inject-data-application/environment-variable-expose-pod-information/
14. The Kubernetes Authors. *Well-Known Labels, Annotations and Taints*. https://kubernetes.io/docs/reference/labels-annotations-taints/
15. The Kubernetes Authors. *Resource Management for Pods and Containers*. https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
16. The Kubernetes Authors. *Pod Quality of Service Classes*. https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/
17. The Kubernetes Authors. *Reserve Compute Resources for System Daemons* (allocatable). https://kubernetes.io/docs/tasks/administer-cluster/reserve-compute-resources/
18. The Kubernetes Authors. *Non-Graceful Node Shutdown* (taint out-of-service). https://kubernetes.io/docs/concepts/cluster-administration/node-shutdown/
19. The Kubernetes Authors. *kubectl drain / cordon / uncordon / taint / label* (kubectl reference). https://kubernetes.io/docs/reference/kubectl/generated/
20. kind — Kubernetes IN Docker. *Quick Start*. https://kind.sigs.k8s.io/docs/user/quick-start/

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 39 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (kind v0.33.0, Kubernetes v1.37.0) ค่าเวลา, IP และชื่อ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างกัน
