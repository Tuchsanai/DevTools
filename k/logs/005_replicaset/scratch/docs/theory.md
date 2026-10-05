# ReplicaSet: หัวหน้ากะที่นับบูธให้ครบเสมอ

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes ReplicaSet — controller และ reconciliation loop, โครงสร้าง manifest (replicas, selector, template), ownerReferences, self-healing, scale, กับดัก label, selector ที่แก้ไม่ได้, การลบแบบ cascade/orphan, ReplicationController, ReplicaSet กับ ResourceQuota/LimitRange/Pod Security และการกระจาย replica ข้าม Node
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 4 Namespace](../../004_kubernetes_namespace/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

ตลอดบทที่ 2–4 เราสร้าง **Pod เดี่ยว** ด้วยมือมาตลอด และเห็นจุดอ่อนของมันซ้ำแล้วซ้ำอีก ลบผิดตัวเดียวร้านปิดถาวร ซ่อมเรือ (drain) ต้องใช้ `--force` แล้ว Pod หายไปเลย เรือล่มก็ไม่มีใครสร้างบูธแทน และทุกครั้งที่สร้างใหม่ Pod ได้ IP ใหม่จน port-forward หลุด บทนี้แก้ปัญหาข้อแรกและใหญ่ที่สุดคือ **"จำนวน"** ด้วย **ReplicaSet** ซึ่งเปรียบเหมือน **หัวหน้ากะ** ที่ถือคลิปบอร์ดเดินนับบูธที่ติดป้ายของร้านตลอดเวลา ขาดก็ปั๊มบูธใหม่จากแบบพิมพ์ เกินก็เก็บ

เนื้อหาเริ่มจากหัวใจของ Kubernetes คือ **controller** และ **reconciliation loop** (ดู → เทียบ → แก้) ว่าทำงานอยู่ที่ไหนและทำไมจึงทนต่อเหตุการณ์ที่พลาดไป ต่อด้วยโครงสร้างของ ReplicaSet ทั้ง 3 ส่วน (**replicas**, **selector**, **template**), การตั้งชื่อ Pod, **ownerReferences** และการอ่านสถานะ จากนั้นดูพฤติกรรมจริงเมื่อ Pod ถูกลบ เรือถูก drain และเรือล่ม การ scale และลำดับที่ ReplicaSet เลือกลบ Pod กับดักที่เกิดจากการที่ ReplicaSet **นับจาก label ไม่ใช่จากชื่อ** (รับเลี้ยง Pod แปลกหน้า, ลบ Pod ที่เกิน, selector ทับกัน และเทคนิคถอด label เพื่อ debug) ข้อจำกัดเรื่อง **selector แก้ไม่ได้** และ **template ใหม่ไม่เปลี่ยน Pod เดิม** การลบ ReplicaSet แบบ background/foreground/orphan ประวัติของ ReplicationController การทำงานร่วมกับ ResourceQuota, LimitRange และ Pod Security Admission ของบทที่ 4 และการกระจาย replica ข้ามเรือด้วย anti-affinity/topology spread ของบทที่ 3 ปิดท้ายด้วยปัญหาที่ ReplicaSet ยังแก้ไม่ได้ ซึ่งเป็นงานของ **Service (บทที่ 6)** และ **Deployment (บทที่ 7)**

ผลลัพธ์คำสั่งและข้อความ error ที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind ใน container ที่สร้างจาก image เดียวกับ `k8s-lab` (Kubernetes v1.37.0, kubectl v1.37.1) ใน LAB ประจำบทเมื่อ 5 ตุลาคม 2569 **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างจากตัวอย่าง**

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายว่าทำไม Pod เดี่ยวจึงเป็นหน่วยที่ "ตายแล้วไม่ฟื้น" และทำไมต้องมี workload controller ดูแลอีกชั้น
2. อธิบาย reconciliation loop (observe → diff → act), ความหมายของ desired state (`spec`) กับ actual state (`status`) และแนวคิด level-triggered ได้
3. บอกได้ว่า ReplicaSet controller อยู่ใน `kube-controller-manager` และทำงานผ่าน kube-apiserver เท่านั้น
4. เขียน ReplicaSet manifest ที่มี `replicas`, `selector` (`matchLabels`/`matchExpressions`) และ `template` ได้ถูกต้อง และอธิบาย error เมื่อ label ของ template ไม่ตรงกับ selector
5. อ่าน `ownerReferences` ของ Pod, คอลัมน์ `DESIRED/CURRENT/READY` และฟิลด์ใน `status` ของ ReplicaSet ได้
6. อธิบายพฤติกรรม self-healing เมื่อลบ Pod, drain Node และ Node ล่ม รวมถึงบทบาทของ `tolerationSeconds`
7. scale ReplicaSet ได้หลายวิธี และอธิบายเกณฑ์ที่ ReplicaSet ใช้เลือก Pod ที่จะลบตอน scale ลง
8. อธิบายกับดักที่เกิดจากการนับด้วย label (รับเลี้ยง, ลบตัวเกิน, selector ทับกัน) และใช้การถอด label เพื่อแยก Pod ออกมา debug ได้
9. อธิบายว่าทำไม selector แก้ไม่ได้และทำไม template ใหม่ไม่เปลี่ยน Pod เดิม และเลือกวิธีลบ ReplicaSet (background/foreground/orphan) ให้เหมาะกับงาน
10. อธิบายผลของ ResourceQuota, LimitRange, Pod Security Admission และกฎการจัดวาง (anti-affinity, topology spread) ต่อ Pod ที่ ReplicaSet สร้าง และอ่านข้อความ `FailedCreate`/`FailedScheduling` ได้
11. บอกปัญหาที่ ReplicaSet ยังแก้ไม่ได้ และเชื่อมโยงไปยัง Service และ Deployment ได้

## สารบัญ

1. [บทนำ: บูธเดี่ยวหาย ไม่มีใครสร้างใหม่](#1-บทนำ-บูธเดี่ยวหาย-ไม่มีใครสร้างใหม่)
2. [Controller และ reconciliation loop](#2-controller-และ-reconciliation-loop)
3. [ReplicaSet manifest: replicas, selector, template](#3-replicaset-manifest-replicas-selector-template)
4. [Self-healing: ลบ Pod, drain และเรือล่ม](#4-self-healing-ลบ-pod-drain-และเรือล่ม)
5. [Scale: เพิ่ม ลด และลบตัวไหนก่อน](#5-scale-เพิ่ม-ลด-และลบตัวไหนก่อน)
6. [กับดัก label](#6-กับดัก-label)
7. [selector แก้ไม่ได้ และ template ใหม่ไม่เปลี่ยน Pod เดิม](#7-selector-แก้ไม่ได้-และ-template-ใหม่ไม่เปลี่ยน-pod-เดิม)
8. [ลบ ReplicaSet: cascade และ orphan](#8-ลบ-replicaset-cascade-และ-orphan)
9. [ReplicationController: รุ่นพี่ที่เกษียณแล้ว](#9-replicationcontroller-รุ่นพี่ที่เกษียณแล้ว)
10. [ReplicaSet ใน namespace: quota, LimitRange และ PSA](#10-replicaset-ใน-namespace-quota-limitrange-และ-psa)
11. [ReplicaSet กับการจัดวาง: anti-affinity และ topology spread](#11-replicaset-กับการจัดวาง-anti-affinity-และ-topology-spread)
12. [ข้อควรรู้: Pod จาก ReplicaSet ไม่มีชื่อคงที่และ IP คงที่](#12-ข้อควรรู้-pod-จาก-replicaset-ไม่มีชื่อคงที่และ-ip-คงที่)
13. [สรุปและปูทางบทถัดไป](#13-สรุปและปูทางบทถัดไป)
14. [คำถามทบทวน](#14-คำถามทบทวน)
15. [เอกสารอ้างอิง](#15-เอกสารอ้างอิง)

### สารบัญรูปภาพ

{{FIGTOC}}

---

## 1. บทนำ: บูธเดี่ยวหาย ไม่มีใครสร้างใหม่

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

{{FIG:T01}}

ร้านอาหารแมวน้องส้มเปิดได้ครบ 3 environment แล้วในบทที่ 4 แต่ทุกบูธยังเป็น **Pod เดี่ยว** ที่น้องส้มสร้างด้วยมือ ทุกครั้งที่บูธหาย ไม่ว่าจะเพราะลบผิด ซ่อมเรือ หรือเรือล่ม ร้านจะปิดจนกว่าน้องส้มจะมาสร้างใหม่เอง และเมื่อสร้างใหม่ บูธก็ได้ IP ใหม่ ลูกค้าที่จำที่อยู่เดิมหรือ port-forward ที่ต่อไว้ก็ใช้ไม่ได้

{{FIG:T02}}

ทบทวนปัญหาที่เราเจอมาแล้วจริง ๆ ในบทก่อน

| บท | สิ่งที่ทำ | ผลที่เห็น |
|---|---|---|
| 2 | `kubectl delete pod ...` | Pod หายถาวร ไม่มีอะไรเกิดขึ้นแทน |
| 3 | `kubectl drain lab-worker2 ...` | Pod เดี่ยวต้องใช้ `--force` จึงจะ drain ได้ และ Pod หายไปเลย ไม่ย้ายไปเรืออื่น |
| 3 | `docker stop lab-worker2` (เรือล่ม) | Node เป็น `NotReady` แล้ว Pod ถูกไล่หลังครบ `tolerationSeconds` (ค่าเริ่มต้น 300 วินาที) แต่ไม่มีใครสร้างแทน |
| 4 | ลบ Pod แล้วสร้างใหม่ | Pod ใหม่ได้ IP ใหม่ และ port-forward ที่ต่อ Pod เดิมหลุด (`ERR_CONNECTION_RESET`) |

สิ่งที่ปัญหาทั้งหมดนี้มีร่วมกันคือ **Pod เป็นหน่วยที่ "ตายแล้วไม่ฟื้น"** Pod ไม่ย้ายตัวเองไปเรือลำอื่น และไม่มีกลไกในตัว Pod ที่จะสร้างตัวเองใหม่ (kubelet รีสตาร์ต **container** ใน Pod ได้ตาม `restartPolicy` แต่ถ้า **Pod** ถูกลบหรือ Node หายไป Pod นั้นจบชีวิตทันที) เราจึงต้องมีผู้ดูแลระดับสูงกว่า Pod ที่คอยเฝ้าดูและสร้าง Pod ใหม่แทน ผู้ดูแลแบบนี้เรียกว่า **workload controller** และตัวที่พื้นฐานที่สุดคือ **ReplicaSet**

ReplicaSet แก้ปัญหา **"จำนวน"** ได้ (ต้องมี N บูธเสมอ) แต่ยังไม่แก้ปัญหา **"ที่อยู่คงที่"** (บทที่ 6) และ **"เปลี่ยนรุ่นอย่างปลอดภัย"** (บทที่ 7) ซึ่งเราจะเห็นด้วยตาตัวเองใน LAB สุดท้าย

{{FIG:T03}}

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–4)

| Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| container | ตู้สินค้า | |
| Pod | กล่องใสสี teal มีป้าย IP (บทนี้วาดเป็น "บูธร้าน" มีกันสาด) | |
| Node | เรือสินค้า (`lab-worker`, `lab-worker2`) | |
| Control Plane | หอบังคับการ (`lab-control-plane`) | |
| Namespace | โซนทาสีบนแผนผังท่าเรือ | |
| label | ป้ายห้อยกระเป๋าสี | |
| controller + reconciliation loop | หุ่นยนต์ในหอบังคับการที่วน "ดู → เทียบ → แก้" ไม่รู้จบ | ✅ |
| **ReplicaSet** | **หัวหน้ากะ** หุ่นยนต์กล่องสี teal ถือคลิปบอร์ดนับหัว | ✅ |
| selector | แว่นขยายส่องป้ายห้อย | ✅ |
| Pod template | แบบพิมพ์ (พิมพ์เขียว) ที่ใช้ปั๊มบูธใหม่ | ✅ |
| ownerReferences | ป้ายเจ้าของหนีบมุมบูธ โยงเชือกกลับหาหัวหน้ากะ | ✅ |
| cascade / orphan | ลบหัวหน้ากะแล้วบูธหายตามเชือก / ตัดเชือกทิ้งบูธไว้ | ✅ |
| ResourceQuota / LimitRange | ใบงบของโซน / ป้ายกฎขนาดกล่อง (บทที่ 4) | |

---

## 2. Controller และ reconciliation loop

### 2.1 Desired state กับ actual state

ตั้งแต่บทที่ 2 เราเขียน YAML แล้ว `kubectl apply` มาตลอด สิ่งที่เราเขียนในส่วน `spec` คือ **สิ่งที่เราต้องการ (desired state)** ส่วนที่ระบบเขียนกลับมาใน `status` คือ **สิ่งที่เป็นจริง (actual state)** วิธีทำงานแบบนี้เรียกว่า **declarative** เราบอกว่า "อยากได้อะไร" ไม่ได้บอกว่า "ให้ทำทีละขั้นอย่างไร"

ผู้ที่ทำให้ actual state เข้าใกล้ desired state คือ **controller** แต่ละตัวดูแล object ชนิดหนึ่ง และทำงานเป็นวงวน 3 ขั้นไม่รู้จบ

1. **Observe (ดู)** อ่านสภาพปัจจุบันจาก kube-apiserver เช่น "ตอนนี้มี Pod ที่ป้ายตรงอยู่กี่ตัว"
2. **Diff (เทียบ)** เทียบกับ `spec` เช่น "ต้องการ 3 มีอยู่ 2 ขาด 1"
3. **Act (แก้)** สั่งงานผ่าน API เพื่อลดส่วนต่าง เช่น "สร้าง Pod ใหม่ 1 ตัวจาก template" แล้วกลับไปข้อ 1

{{FIG:T04}}

วงวนนี้เรียกว่า **reconciliation loop** (หรือ control loop) เป็นหลักการเดียวกับเทอร์โมสตัทของเครื่องปรับอากาศ เราตั้ง 25 องศา (desired) เครื่องวัดอุณหภูมิห้อง (actual) แล้วเปิดหรือปิดคอมเพรสเซอร์ให้ใกล้ค่าที่ตั้ง เราไม่ต้องสั่ง "เปิดคอมเพรสเซอร์ 10 นาที"

### 2.2 controller อยู่ที่ไหน

controller ในตัวของ Kubernetes (ReplicaSet, Node, Namespace, Job, Deployment ฯลฯ) ถูกรวมไว้ในโปรแกรมเดียวชื่อ **`kube-controller-manager`** ซึ่งในคลัสเตอร์ kind รันเป็น **static Pod** ใน namespace `kube-system` บนเรือ `lab-control-plane` (ชื่อลงท้ายด้วยชื่อ Node ตามแบบ static Pod ที่เห็นในบทที่ 3) ผลจริงจาก LAB 0

```text
$ kubectl get pods -n kube-system -l component=kube-controller-manager -o wide
NAME                                        READY   STATUS    RESTARTS   AGE   IP           NODE                NOMINATED NODE   READINESS GATES
kube-controller-manager-lab-control-plane   1/1     Running   0          73s   172.19.0.3   lab-control-plane   <none>           <none>

$ kubectl -n kube-system get pod kube-controller-manager-lab-control-plane -o jsonpath='{.spec.containers[0].command}' | grep -o -- '--controllers=[^"]*'
--controllers=*,bootstrapsigner,tokencleaner
```

`--controllers=*` แปลว่าเปิด controller มาตรฐานทั้งหมด (รวม ReplicaSet controller) และเปิดเพิ่มอีก 2 ตัวที่ปกติปิดไว้ ส่วน `ownerReferences` ของ Pod นี้ชี้ไปที่ `kind: Node` ชื่อ `lab-control-plane` เพราะเป็น mirror pod ของ static Pod (kubelet ดูแล ไม่ใช่ controller ใด ๆ)

{{FIG:T05}}

ข้อสำคัญคือ **controller ไม่คุยกับเรือ (kubelet) ตรง ๆ** ทุกอย่างผ่าน kube-apiserver

- controller **list + watch** object ที่สนใจจาก API server เก็บสำเนาไว้ในหน่วยความจำ (informer cache) เพื่อไม่ต้องถาม API server ทุกครั้ง
- เมื่อมีการเปลี่ยนแปลง ชื่อ object ที่เกี่ยวข้องจะถูกใส่ใน **work queue** แล้ว worker หยิบไป reconcile ทีละตัว ถ้าทำไม่สำเร็จจะใส่กลับเข้าคิวพร้อมหน่วงเวลาที่ยาวขึ้นเรื่อย ๆ (backoff — เราจะเห็นผลนี้ในหัวข้อ 10)
- ReplicaSet controller "สร้าง Pod" ด้วยการส่ง Pod object ไปที่ API server เท่านั้น จากนั้น **kube-scheduler** เลือกเรือ และ **kubelet** บนเรือนั้นเป็นผู้เปิด container จริง
- `kube-controller-manager` ในคลัสเตอร์ที่มี control plane หลายเครื่องจะมีหลายสำเนา แต่ทำงานจริงทีละตัวผ่านการเลือกหัวหน้า (leader election) ด้วย Lease object ใน `kube-system`

controller ที่เราเคยเห็นผลงานมาแล้วโดยไม่รู้ตัว ได้แก่ **Node controller** (ติด taint `node.kubernetes.io/unreachable` และไล่ Pod เมื่อเรือล่มในบทที่ 3) และ **Namespace controller** (ลบของทุกชิ้นในโซนก่อนลบ namespace ในบทที่ 4) บทนี้คือ **ReplicaSet controller**

### 2.3 Level-triggered: เทียบสภาพ ไม่ได้จำเหตุการณ์

{{FIG:T06}}

ระบบแบบ **edge-triggered** ทำงานเมื่อ "ได้ยินเหตุการณ์" เช่น "มีคนลบ Pod ให้สร้างใหม่ 1 ตัว" ถ้าพลาดเหตุการณ์ไป (controller กำลังรีสตาร์ต หรือการเชื่อมต่อ watch ขาด) งานนั้นก็หายไปด้วย

controller ของ Kubernetes เป็นแบบ **level-triggered** คือทุกรอบจะ **เทียบสภาพปัจจุบันทั้งหมด** กับ desired state เหตุการณ์ทำหน้าที่แค่ "ปลุก" ให้ทำงานเร็วขึ้น ถ้าพลาดเหตุการณ์ไป รอบถัดไปก็ยังนับได้ว่าขาดกี่ตัวและแก้ได้ถูก ผลที่ตามมาคือการ reconcile เป็น **idempotent** ทำซ้ำกี่รอบก็ได้ผลเดิม (ถ้าครบแล้ว ก็ไม่ทำอะไร) นี่คือเหตุผลที่ ReplicaSet ไม่ได้ "จำ" ว่าเคยสร้าง Pod ตัวไหน แต่ **นับใหม่ทุกรอบจาก label** ซึ่งเป็นที่มาของทั้งความทนทานและกับดักในหัวข้อ 6

---

## 3. ReplicaSet manifest: replicas, selector, template

### 3.1 โครง 3 ส่วน

{{FIG:T07}}

ReplicaSet มีส่วนสำคัญใน `spec` เพียง 3 ส่วน

| ส่วน | ความหมาย | อุปมา |
|---|---|---|
| `replicas` | จำนวน Pod ที่ต้องมีตลอดเวลา (ไม่ใส่ = 1) | ตัวเลขบนคลิปบอร์ด |
| `selector` | เงื่อนไข label ที่ใช้ "นับ" ว่า Pod ไหนอยู่ในความดูแล | แว่นขยายส่องป้าย |
| `template` | Pod spec ที่ใช้สร้าง Pod ใหม่เมื่อนับได้ไม่ครบ | แบบพิมพ์ปั๊มบูธ |

{{FIG:T08}}

ไฟล์ `labs/lab01-first-rs/snack-rs.yaml` ที่ใช้ใน LAB 1

```yaml
# LAB 1: ReplicaSet ตัวแรก — หัวหน้ากะดูแลบูธขนม 3 บูธ
apiVersion: apps/v1          # ReplicaSet อยู่ในกลุ่ม apps (Pod อยู่ใน v1)
kind: ReplicaSet
metadata:
  name: snack-rs
  namespace: rs-lab
  labels:
    app: snack
spec:
  replicas: 3                # จำนวนบูธที่ต้องมีตลอดเวลา
  selector:                  # หัวหน้ากะนับเฉพาะ Pod ที่มีป้ายตรงนี้
    matchLabels:
      app: snack
  template:                  # แบบพิมพ์สำหรับปั๊ม Pod ใหม่ (ไม่มี name → ระบบตั้งชื่อ snack-rs-xxxxx)
    metadata:
      labels:
        app: snack           # ต้องตรงกับ selector ไม่งั้นสร้าง RS ไม่ได้
    spec:
      terminationGracePeriodSeconds: 1
      containers:
        - name: app
          image: busybox:1.36
          command: ["sh", "-c", "echo บูธขนม $(hostname) เปิดแล้ว; sleep 3600"]
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 50m, memory: 32Mi }
```

ข้อสังเกต

- `apiVersion: apps/v1` ไม่ใช่ `v1` เพราะ ReplicaSet อยู่ใน API group `apps` (ดูได้ด้วย `kubectl api-resources | grep -i replicaset` ซึ่งบอกชื่อย่อ `rs` ที่ใช้กับ kubectl ได้ เช่น `kubectl get rs`)
- ทุกอย่างใต้ `template` คือ **Pod ทั้งก้อนแบบที่เขียนในบทที่ 2** (`metadata.labels` + `spec.containers`, probes, resources, volumes, init container ฯลฯ) ยกเว้นไม่มี `apiVersion`, `kind` และ **ไม่มี `metadata.name`**
- `metadata.labels` ด้านบนสุดเป็น label ของ **ตัว ReplicaSet เอง** (ไว้ค้น RS) ไม่เกี่ยวกับการนับ Pod
- ReplicaSet มีฟิลด์ `spec.minReadySeconds` ด้วย (ค่าเริ่มต้น 0) ใช้กำหนดว่า Pod ต้อง Ready ต่อเนื่องนานเท่าไรจึงนับเป็น "available"

### 3.2 ชื่อ Pod: `<ชื่อ RS>-<สุ่ม 5 ตัว>`

{{FIG:T09}}

template ไม่มีชื่อ เพราะ ReplicaSet ต้องสร้าง Pod หลายตัวจากแบบเดียวกัน ระบบจึงใช้กลไก `generateName` ตั้งชื่อเป็น `<ชื่อ RS>-` ตามด้วยอักษรสุ่ม 5 ตัว ผลจริงจาก LAB 1

```text
$ kubectl apply -f labs/lab01-first-rs/snack-rs.yaml
replicaset.apps/snack-rs created

$ sleep 4; kubectl get rs,pods -n rs-lab -o wide --show-labels
NAME                       DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR    LABELS
replicaset.apps/snack-rs   3         3         2       5s    app          busybox:1.36   app=snack   app=snack

NAME                 READY   STATUS              RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES   LABELS
pod/snack-rs-46p58   1/1     Running             0          5s    10.244.3.4   lab-worker2   <none>           <none>            app=snack
pod/snack-rs-bdpcw   0/1     ContainerCreating   0          5s    <none>       lab-worker    <none>           <none>            app=snack
pod/snack-rs-w5dtc   1/1     Running             0          5s    10.244.3.3   lab-worker2   <none>           <none>            app=snack
```

Pod ที่ถูกสร้างแทนจะได้ **ชื่อใหม่เสมอ** (ไม่ใช้ชื่อเดิมซ้ำ) ดังนั้นห้ามเขียนสคริปต์ที่อ้างชื่อ Pod ของ ReplicaSet ตายตัว ให้ค้นด้วย label แทน เช่น `kubectl get pods -l app=snack` (ถ้าชื่อ RS ยาวมาก ส่วนหน้าของชื่อ Pod จะถูกตัดให้รวมแล้วไม่เกินความยาวที่ระบบกำหนด)

### 3.3 selector: matchLabels และ matchExpressions

{{FIG:T10}}

selector เขียนได้ 2 แบบ ใช้คู่กันได้ และ **ทุกข้อต้องเป็นจริงพร้อมกัน (AND)**

| รูปแบบ | ตัวอย่าง | ความหมาย |
|---|---|---|
| `matchLabels` | `app: snack` | label `app` ต้องเท่ากับ `snack` |
| `matchExpressions` `In` | `{key: tier, operator: In, values: [snack, drink]}` | `tier` เป็น `snack` หรือ `drink` |
| `matchExpressions` `NotIn` | `{key: env, operator: NotIn, values: [test]}` | `env` ไม่ใช่ `test` (Pod ที่ไม่มี `env` เลยก็ผ่าน) |
| `matchExpressions` `Exists` | `{key: tier, operator: Exists}` | มี label `tier` (ค่าอะไรก็ได้) |
| `matchExpressions` `DoesNotExist` | `{key: track, operator: DoesNotExist}` | ต้องไม่มี label `track` |

ไฟล์ `labs/lab01-first-rs/snack-rs-expr.yaml` (ตัดส่วน container ที่เหมือน snack-rs ออก)

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs-expr
  namespace: rs-lab
spec:
  replicas: 2
  selector:
    matchExpressions:
      - { key: tier, operator: In, values: [snack, drink] }
      - { key: track, operator: DoesNotExist }
  template:
    metadata:
      labels:
        tier: drink          # อยู่ในรายการ In → ผ่าน และไม่มีป้าย track → ผ่าน
    spec:
      terminationGracePeriodSeconds: 1
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
```

kubectl แสดง selector นี้ในรูปแบบ set-based แบบเดียวกับที่ใช้กับ `-l` ในบทที่ 2

```text
$ kubectl get rs snack-rs-expr -n rs-lab -o wide
NAME            DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES         SELECTOR
snack-rs-expr   2         2         2       4s    app          busybox:1.36   tier in (drink,snack),!track

$ kubectl get pods -n rs-lab -l "tier in (snack,drink)" --show-labels
NAME                  READY   STATUS    RESTARTS   AGE   LABELS
snack-rs-expr-9sn9g   1/1     Running   0          4s    tier=drink
snack-rs-expr-x6sxw   1/1     Running   0          4s    tier=drink
```

`!track` คือ `DoesNotExist` ใช้ทดสอบ selector ก่อนสร้าง RS ได้ด้วย `kubectl get pods -l 'tier in (snack,drink),!track'` ถ้าคำสั่งนี้เห็น Pod ที่ไม่ควรเห็น แปลว่า RS ก็จะนับ Pod เหล่านั้นด้วย

### 3.4 label ของ template ต้องตรงกับ selector

{{FIG:T11}}

ถ้า label ใน template ไม่ผ่าน selector ของตัวเอง API server จะ **ปฏิเสธตั้งแต่ตอนสร้าง** ไฟล์ `snack-rs-bad-labels.yaml` จงใจพิมพ์ `app: snak` ใน template ขณะที่ selector เป็น `app: snack`

```text
$ kubectl apply -f labs/lab01-first-rs/snack-rs-bad-labels.yaml; echo "exit=$?"
The ReplicaSet "snack-rs-bad" is invalid: spec.template.metadata.labels: Invalid value: {"app":"snak"}: `selector` does not match template `labels`
exit=1
```

เหตุผลคือถ้ายอมให้สร้างได้ ReplicaSet จะสร้าง Pod ที่ป้าย `snak` ซึ่งตัวเอง **นับไม่เห็น** นับได้ 0 ตลอดจึงสร้างใหม่ไปเรื่อย ๆ ไม่รู้จบ ด้วยเหตุผลเดียวกัน ใน `apps/v1` selector **ห้ามว่าง** (selector ว่างจะตรงกับทุก Pod ใน namespace)

template มี label มากกว่า selector ได้ (เช่น selector `app: snack` แต่ template มี `app: snack` และ `version: v1`) ซึ่งเป็นเรื่องปกติและมีประโยชน์ในการค้นหา

### 3.5 ownerReferences: ป้ายเจ้าของบนบูธ

{{FIG:T12}}

Pod ทุกตัวที่ ReplicaSet สร้าง (หรือรับเลี้ยง) จะมี `metadata.ownerReferences` ชี้กลับไปที่ RS ผลจริงจาก LAB 1

```text
$ kubectl get pod snack-rs-46p58 -n rs-lab -o jsonpath='{.metadata.ownerReferences}{"\n"}'
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"ReplicaSet","name":"snack-rs","uid":"cd70be6b-fd70-45e9-acaf-a66877fa6fad"}]
```

| ฟิลด์ | ความหมาย |
|---|---|
| `apiVersion`, `kind`, `name` | เจ้าของคือ ReplicaSet ชื่อ `snack-rs` |
| `uid` | uid ของ RS **ตัวนั้น** (ลบแล้วสร้าง RS ชื่อเดิมใหม่ uid จะเปลี่ยน) |
| `controller: true` | เจ้าของรายนี้เป็น "ผู้ควบคุม" Pod หนึ่งตัวมี controller ได้ **รายเดียว** |
| `blockOwnerDeletion: true` | ตอนลบ RS แบบ foreground ต้องรอให้ Pod นี้หายก่อน RS จึงหาย (หัวข้อ 8) |

ownerReferences คือสิ่งที่ทำให้

- RS สองตัวที่ selector ทับกันไม่แย่ง Pod ที่มีเจ้าของแล้ว (หัวข้อ 6.4)
- **garbage collector** รู้ว่าต้องลบ Pod ไหนตามเมื่อ RS ถูกลบ (หัวข้อ 8)
- `kubectl describe pod` บอกเจ้าของของ Pod ในบรรทัด `Controlled By`

### 3.6 อ่านสถานะของ ReplicaSet

{{FIG:T13}}

`kubectl get rs` แสดง 3 ตัวเลข

| คอลัมน์ | มาจาก | ความหมาย |
|---|---|---|
| `DESIRED` | `spec.replicas` | จำนวนที่ต้องการ |
| `CURRENT` | `status.replicas` | จำนวน Pod ที่ RS นับว่าเป็นของตน (ไม่รวม Pod ที่กำลังถูกลบ) |
| `READY` | `status.readyReplicas` | จำนวน Pod ที่ Ready แล้ว |

`-o wide` เพิ่ม `CONTAINERS`, `IMAGES` (image ใน **template ปัจจุบัน** ไม่ใช่ของ Pod ที่รันอยู่ — สำคัญมากในหัวข้อ 7) และ `SELECTOR`

ส่วน `status` เต็ม ๆ ดูได้ด้วย jsonpath ผลจริงตอน Pod เพิ่งขึ้นได้ 2 ใน 3 ตัว

```text
$ kubectl get rs snack-rs -n rs-lab -o jsonpath='{.status}{"\n"}'
{"availableReplicas":2,"fullyLabeledReplicas":3,"observedGeneration":1,"readyReplicas":2,"replicas":3,"terminatingReplicas":0}
```

| ฟิลด์ | ความหมาย |
|---|---|
| `replicas` | จำนวน Pod ที่นับได้ (= CURRENT) |
| `readyReplicas` | Pod ที่ Ready (= READY) |
| `availableReplicas` | Pod ที่ Ready ต่อเนื่องครบ `minReadySeconds` |
| `fullyLabeledReplicas` | Pod ที่มี label ครบตาม **template** (ไม่ใช่แค่ตรง selector) |
| `observedGeneration` | รุ่นของ `spec` ที่ controller เห็นแล้ว (เทียบกับ `metadata.generation` ที่เพิ่มทุกครั้งที่แก้ spec) |
| `terminatingReplicas` | Pod ของ RS ที่กำลังถูกลบ (มี `deletionTimestamp`) — ฟิลด์ใหม่ที่ v1.37 แสดงแล้ว |
| `conditions` | ปรากฏเมื่อมีปัญหา เช่น `ReplicaFailure` (หัวข้อ 10) |

`kubectl describe rs` แสดง Pod template และ **Events** ที่บอกว่า RS สร้าง/ลบ Pod ตัวไหน

```text
$ kubectl describe rs snack-rs -n rs-lab
Name:         snack-rs
Namespace:    rs-lab
Selector:     app=snack
Labels:       app=snack
Annotations:  <none>
Replicas:     3 current / 3 desired
Pods Status:  2 Running / 1 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=snack
  Containers:
   app:
    Image:      busybox:1.36
...
Events:
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  5s    replicaset-controller  Created pod: snack-rs-w5dtc
  Normal  SuccessfulCreate  5s    replicaset-controller  Created pod: snack-rs-46p58
  Normal  SuccessfulCreate  5s    replicaset-controller  Created pod: snack-rs-bdpcw
```

> **ข้อควรรู้เรื่อง Events:** ระบบจำกัดจำนวน event ต่อ object (spam filter) เมื่อ RS ตัวหนึ่งสร้าง/ลบ Pod บ่อย ๆ event เก่าจะถูกรวมเป็น `(combined from similar events)` และ event ใหม่อาจ **ไม่ปรากฏเลย** ในการทดลองจริง หลังจากลบและ scale snack-rs หลายรอบ การลบ Pod หลงตัวหนึ่งไม่มี event `SuccessfulDelete` ให้เห็น แต่เมื่อลองกับ RS ที่สร้างใหม่ (uid ใหม่) ก็เห็นตามปกติ ดังนั้น **ให้เชื่อ `kubectl get pods` และ `kubectl get rs` เป็นหลัก** และใช้ Events เป็นข้อมูลเสริม

---

## 4. Self-healing: ลบ Pod, drain และเรือล่ม

{{FIG:T14}}

### 4.1 ลบ Pod ของ ReplicaSet

เมื่อ Pod ตัวหนึ่งถูกลบ ReplicaSet นับได้ 2 ไม่ตรงกับ 3 จึงสร้างตัวใหม่จาก template ทันที ผลจริงจาก LAB 2 (terminal ที่ 2 เปิด `kubectl get pods -n rs-lab -o wide -w` ไว้ ตัดคอลัมน์ท้ายและบรรทัดที่ซ้ำกันออก)

```text
$ kubectl delete pod snack-rs-46p58 -n rs-lab --wait=false
pod "snack-rs-46p58" deleted from rs-lab namespace

--- terminal 2 ---
snack-rs-46p58   1/1     Terminating   0          38s   10.244.3.4   lab-worker2
snack-rs-kf5vp   0/1     Pending       0          0s    <none>       <none>
snack-rs-kf5vp   0/1     Pending       0          0s    <none>       lab-worker2
snack-rs-kf5vp   0/1     ContainerCreating   0          1s    <none>       lab-worker2
snack-rs-kf5vp   1/1     Running             0          2s    10.244.3.6   lab-worker2
snack-rs-46p58   0/1     Error               0          41s   10.244.3.4   lab-worker2
```

{{FIG:T15}}

สังเกต 3 อย่าง

1. ตัวใหม่ `snack-rs-kf5vp` ถูกสร้าง **ในวินาทีเดียวกับที่สั่งลบ** และ Running ภายใน 2 วินาที (ในเครื่องที่ image อยู่บน Node แล้ว)
2. ตัวใหม่เกิด **ขณะที่ตัวเก่ายัง Terminating** เพราะ RS ไม่นับ Pod ที่มี `deletionTimestamp` แล้ว จึงมีช่วงสั้น ๆ ที่ "Pod อยู่จริง" มากกว่า `replicas` (แอปที่ห้ามรันซ้อนกันเด็ดขาด ต้องระวังเรื่องนี้)
3. ตัวเก่าขึ้น `Error` ชั่วครู่ก่อนหาย เพราะ `sh` ใน busybox ไม่รับ SIGTERM จึงถูก kill หลัง grace period 1 วินาที (exit code 137) ไม่ใช่ความผิดพลาด

ลบทั้ง 3 ตัวพร้อมกันด้วย `kubectl delete pod -n rs-lab -l app=snack` ก็ได้ Pod ใหม่ 3 ตัว Running ภายในราว 2 วินาทีเช่นกัน ร้านกลับมาครบ แต่ **ทุกตัวเป็นบูธใหม่** ชื่อใหม่ IP ใหม่

### 4.2 drain Node: ไม่ต้อง `--force` อีกต่อไป

{{FIG:T16}}

ในบทที่ 3 การ drain เรือที่มี Pod เดี่ยวต้องใส่ `--force` และ Pod หายไปเลย เพราะ kubectl เตือนว่าไม่มี controller ดูแล Pod นั้น เมื่อ Pod มี ReplicaSet เป็นเจ้าของ drain ทำได้ตามปกติ ผลจริงจาก LAB 2

```text
$ time kubectl drain lab-worker2 --ignore-daemonsets
node/lab-worker2 cordoned
Warning: ignoring DaemonSet-managed Pods: kube-system/kindnet-ggn6v, kube-system/kube-proxy-pfmq7
evicting pod rs-lab/snack-rs-n2x77
evicting pod rs-lab/snack-rs-2rfqd
pod/snack-rs-n2x77 evicted
pod/snack-rs-2rfqd evicted
node/lab-worker2 drained

real	0m3.070s

$ kubectl get pods -n rs-lab -o wide
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
snack-rs-frvwx   1/1     Running   0          3s    10.244.1.6   lab-worker   <none>           <none>
snack-rs-ll2f9   1/1     Running   0          31s   10.244.1.4   lab-worker   <none>           <none>
snack-rs-p9mhg   1/1     Running   0          3s    10.244.1.5   lab-worker   <none>           <none>
```

Pod 2 ตัวบน `lab-worker2` ถูกไล่ (evict) แล้ว RS สร้างตัวแทน 2 ตัว scheduler วางลง `lab-worker` เพราะ `lab-worker2` ถูก cordon อยู่ ข้อควรรู้: หลัง `kubectl uncordon lab-worker2` **Pod ไม่ย้ายกลับเอง** ทั้ง 3 ตัวยังอยู่บน `lab-worker` เพราะ scheduler ทำงานเฉพาะตอน Pod เกิดใหม่ และ ReplicaSet นับแค่จำนวน ไม่ได้สนใจว่าอยู่เรือไหน (การจัดสมดุลใหม่ต้องใช้เครื่องมือเสริม เช่น descheduler ซึ่งไม่อยู่ในบทนี้)

### 4.3 เรือล่ม: ช้ากว่าที่คิด

{{FIG:T17}}

เมื่อเรือล่มกะทันหัน (`docker stop lab-worker2`) ไม่มีใครสั่งลบ Pod ระบบต้องผ่านหลายขั้นก่อน ReplicaSet จะรู้ว่าต้องสร้างแทน

1. kubelet บนเรือนั้นหยุดส่ง heartbeat → หลังผ่านไปราว 40–50 วินาที Node controller เปลี่ยน Node เป็น `NotReady` และติด taint `node.kubernetes.io/unreachable:NoExecute` (หรือ `not-ready`)
2. Pod บนเรือนั้นถูกทำเครื่องหมายว่าไม่ Ready แต่ **ยังนับเป็น CURRENT** (`kubectl get rs` แสดง `3 3 1`)
3. Pod ทุกตัวมี toleration อัตโนมัติสำหรับ taint ทั้งสองแบบ `tolerationSeconds: 300` จึงยังไม่ถูกไล่จนครบ 300 วินาที
4. เมื่อครบเวลา Pod ถูกไล่ (มี `deletionTimestamp`) → RS ไม่นับแล้ว → สร้างตัวแทนบนเรือที่เหลือ
5. Pod เก่า **ค้าง `Terminating`** เพราะ kubelet บนเรือที่ล่มยืนยันการลบไม่ได้ จนกว่าเรือจะกลับมา

ถ้าต้องการให้สร้างแทนเร็วขึ้น ใส่ toleration ของเราเองใน template (ไฟล์ `labs/lab02-self-heal/snack-rs-fast-evict.yaml`)

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs
  namespace: rs-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app: snack
  template:
    metadata:
      labels:
        app: snack
    spec:
      terminationGracePeriodSeconds: 1
      tolerations:                     # ทนเรือ NotReady/ติดต่อไม่ได้แค่ 30 วิ
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
      containers:
        - name: app
          image: busybox:1.36
          command: ["sh", "-c", "echo บูธขนม $(hostname) เปิดแล้ว; sleep 3600"]
```

ผลจริงจาก LAB 2 (ทางเลือก) วัดเวลานับจากเริ่มสั่ง `docker stop lab-worker2` ซึ่งใช้เวลาเอง 11 วินาที (ย่อจากลูปที่พิมพ์ทุก 4 วินาที; `DEL` = Pod มี `deletionTimestamp` แล้ว)

```text
t=11s node=Ready    rs(D/C/R)=3/3/3 pods: 5ddqd:Running:-:lab-worker2 ddvjr:Running:-:lab-worker2 qdrs7:Running:-:lab-worker
...
t=40s node=Ready    rs(D/C/R)=3/3/3 ...
t=44s node=NotReady rs(D/C/R)=3/3/1 pods: 5ddqd:Running:-:lab-worker2 ddvjr:Running:-:lab-worker2 qdrs7:Running:-:lab-worker
...
t=73s node=NotReady rs(D/C/R)=3/3/1 ...
t=77s node=NotReady rs(D/C/R)=3/3/3 pods: 5ddqd:Running:DEL:lab-worker2 9wccl:Running:-:lab-worker ddvjr:Running:DEL:lab-worker2 qdrs7:Running:-:lab-worker wvv6s:Running:-:lab-worker
```

| ช่วงเวลา (นับจากเริ่ม stop) | เหตุการณ์ |
|---|---|
| ~41–44 วินาที | Node เป็น `NotReady` RS แสดง `3 3 1` |
| ~74–77 วินาที | ครบ toleration 30 วินาที Pod เก่า 2 ตัวถูกไล่ ตัวแทน 2 ตัวเกิดบน `lab-worker` RS กลับเป็น `3 3 3` และ status มี `"terminatingReplicas":2` |
| หลัง `docker start` | Node Ready ใน 2 วินาที Pod เก่าที่ค้าง Terminating หายใน 4 วินาที |

ถ้าใช้ค่าเริ่มต้น 300 วินาที ร้านจะเหลือบูธที่ใช้ได้ 1 ใน 3 นานกว่า 5 นาที การลด `tolerationSeconds` ทำให้กู้เร็วขึ้น แต่แลกกับการที่ Pod อาจถูกย้ายบ่อยเมื่อเครือข่ายสะดุดเพียงชั่วครู่ จึงต้องเลือกให้เหมาะกับงาน

---

## 5. Scale: เพิ่ม ลด และลบตัวไหนก่อน

### 5.1 วิธี scale

{{FIG:T18}}

| วิธี | คำสั่ง | ข้อดี/ข้อควรระวัง |
|---|---|---|
| คำสั่ง scale | `kubectl scale rs snack-rs -n rs-lab --replicas=5` | เร็ว แต่ **ไม่แก้ไฟล์** |
| แก้ไฟล์แล้ว apply | แก้ `replicas: 4` ในไฟล์ → `kubectl apply -f snack-rs.yaml` | ไฟล์ตรงกับความจริงเสมอ (แนะนำในงานจริง) |
| แก้สดใน editor | `KUBE_EDITOR=nano kubectl edit rs snack-rs -n rs-lab` | แก้ object ในคลัสเตอร์โดยตรง ไม่แก้ไฟล์ |
| หยุดชั่วคราว | `kubectl scale rs snack-rs -n rs-lab --replicas=0` | Pod หายหมด แต่ **RS ยังอยู่** พร้อม template (`0 0 0`) |

> **กับดัก:** `kubectl apply -f` ไฟล์ที่มีบรรทัด `replicas:` จะ **ทับค่าที่เคย scale ไว้** เสมอ เช่น scale เป็น 0 ไว้ แล้วมีคน apply ไฟล์เดิม (replicas 3) ร้านจะกลับมา 3 บูธทันที ใน LAB สุดท้ายเราจะเจอกับดักนี้จริง

### 5.2 scale ลงแล้วลบตัวไหน

{{FIG:T19}}

เมื่อต้องลบ Pod ตอน scale ลง ReplicaSet ไม่ได้สุ่ม แต่เรียง Pod ตามเกณฑ์ "ลบตัวที่เสียหายน้อยที่สุดก่อน" ตามลำดับต่อไปนี้ (เทียบทีละข้อ ข้อแรกที่ต่างกันเป็นตัวตัดสิน)

1. Pod ที่ **ยังไม่ได้ถูกวางบนเรือ** ก่อน Pod ที่วางแล้ว
2. Pod ที่ `Pending` ก่อน `Unknown` ก่อน `Running`
3. Pod ที่ **ไม่ Ready** ก่อน Pod ที่ Ready
4. Pod ที่มี annotation `controller.kubernetes.io/pod-deletion-cost` ต่ำกว่าก่อน
5. Pod ที่อยู่บน **เรือที่มี Pod ของ RS นี้มากกว่า** ก่อน (ช่วยให้กระจายดีขึ้น)
6. Pod ที่ **เพิ่ง Ready** (Ready มาสั้นกว่า) ก่อน
7. Pod ที่ restart มากกว่าก่อน
8. Pod ที่ **สร้างใหม่กว่า** ก่อน

ผลจริงจาก LAB 3: เริ่มจาก 3 ตัว (`6s8m9`, `ldzjc` บน lab-worker2, `trdgg` บน lab-worker) scale เป็น 5 ได้ตัวใหม่ `m259n` (lab-worker) และ `zsdq7` (lab-worker2) แล้ว scale ลงเป็น 2

```text
$ kubectl get events -n rs-lab --field-selector reason=SuccessfulDelete --sort-by=.lastTimestamp
LAST SEEN   TYPE     REASON             OBJECT                MESSAGE
18s         Normal   SuccessfulDelete   replicaset/snack-rs   Deleted pod: snack-rs-ldzjc
18s         Normal   SuccessfulDelete   replicaset/snack-rs   Deleted pod: snack-rs-m259n
18s         Normal   SuccessfulDelete   replicaset/snack-rs   Deleted pod: snack-rs-zsdq7
```

ตัวที่ถูกลบคือ `ldzjc` (ตัว **เก่า** แต่อยู่บน lab-worker2 ที่มี 3 ตัว) ร่วมกับ `m259n` และ `zsdq7` (ตัวใหม่) เหลือ `6s8m9` (lab-worker2) และ `trdgg` (lab-worker) อย่างละลำ ผลนี้แสดงว่า **ไม่ใช่ "ลบตัวใหม่สุดเสมอ"** เกณฑ์ "เรือแออัด" (ข้อ 5) มาก่อนเกณฑ์อายุ ส่วนเกณฑ์ข้อ 6 ใช้การปัดเวลาแบบลอการิทึม Pod ที่อายุใกล้เคียงกันจึงอาจถือว่าเท่ากันแล้วไปตัดสินที่ข้อถัดไป ถ้าต้องการบังคับว่า Pod ตัวไหนควรถูกลบก่อน ให้ใช้ annotation `pod-deletion-cost` (ค่ายิ่งต่ำยิ่งถูกลบก่อน)

---

## 6. กับดัก label

### 6.1 นับจาก label ไม่ใช่จากชื่อหรือประวัติ

{{FIG:T20}}

ReplicaSet ไม่มีรายชื่อ Pod ของตัวเองเก็บไว้ ทุกรอบมันนับ Pod ใน namespace เดียวกันที่ **label ตรง selector** แล้ว **ยังไม่มี controller คนอื่นเป็นเจ้าของ** หรือมีเจ้าของเป็นตัวมันเอง ผลคือ Pod ที่เราสร้างด้วยมือก็ถูกนับได้ถ้าป้ายตรง ซึ่งนำไปสู่กับดัก 3 ข้อ และเทคนิคที่มีประโยชน์ 1 ข้อ

### 6.2 กับดักที่ 1: Pod ที่มีอยู่ก่อนถูก "รับเลี้ยง"

{{FIG:T21}}

ไฟล์ `labs/lab04-label-trap/stray-pod.yaml` เป็น Pod เดี่ยวชื่อ `stray` ติดป้าย `app: snack` แต่ command ต่างจาก template ของ snack-rs ถ้า `stray` มีอยู่ **ก่อน** สร้าง snack-rs

```text
$ kubectl delete rs snack-rs -n rs-lab; kubectl apply -f labs/lab04-label-trap/stray-pod.yaml; ...; kubectl apply -f labs/lab01-first-rs/snack-rs.yaml
...
replicaset.apps/snack-rs created
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
snack-rs-cd24l   1/1     Running   0          4s    10.244.1.16   lab-worker    <none>           <none>
snack-rs-f4p6n   1/1     Running   0          4s    10.244.1.15   lab-worker    <none>           <none>
stray            1/1     Running   0          5s    10.244.3.9    lab-worker2   <none>           <none>

$ kubectl get pod stray -n rs-lab -o jsonpath='{.metadata.ownerReferences}{"\n"}'
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"ReplicaSet","name":"snack-rs","uid":"399a5799-de51-46e0-af67-f05d04995463"}]

$ kubectl exec stray -n rs-lab -- cat /proc/1/cmdline | tr '\0' ' '
sh -c echo ฉันคือ stray ไม่ได้มาจากแบบพิมพ์; sleep 3600
```

RS สร้างเพิ่ม **แค่ 2 ตัว** และติดป้ายเจ้าของให้ `stray` ทั้งที่ `stray` ทำงานคนละอย่างกับ template ไม่มีใครแก้ `stray` ให้ตรง template ร้านจึงมี "บูธปลอม" ปนอยู่หนึ่งบูธโดยไม่มีใครรู้ (ชื่อ Pod ที่ไม่ขึ้นต้นด้วย `snack-rs-` เป็นเบาะแสเดียว)

### 6.3 กับดักที่ 2: Pod ที่สร้างทีหลังถูกลบทันที

{{FIG:T22}}

ถ้า RS มีครบ 3 ตัวแล้ว เราสร้าง Pod ที่ป้ายตรงเพิ่ม RS นับได้ 4 เกิน 3 จึงลบทิ้ง ตามเกณฑ์หัวข้อ 5.2 ตัวที่ยังไม่ Ready และใหม่สุดถูกเลือก ซึ่งก็คือ Pod ที่เราเพิ่งสร้าง

```text
$ kubectl apply -f labs/lab04-label-trap/stray-pod.yaml; kubectl get pods -n rs-lab --show-labels
pod/stray created
NAME             READY   STATUS        RESTARTS   AGE   LABELS
snack-rs-29zjp   1/1     Running       0          20s   app=snack
snack-rs-ldj4t   1/1     Running       0          20s   app=snack
snack-rs-ps7x9   1/1     Running       0          20s   app=snack
stray            0/1     Terminating   0          0s    app=snack
```

kubectl แจ้งว่า `created` สำเร็จ แต่ภายในวินาทีเดียว `stray` ก็เป็น `Terminating` ผู้ที่ไม่รู้เรื่องนี้จะงงว่า "Pod หายไปไหน" เมื่อทดสอบกับ RS ที่ยังมี event ไม่มาก จะเห็นหลักฐานใน Events ของ RS

```text
  Normal  SuccessfulDelete  2s    replicaset-controller  Deleted pod: stray2
```

### 6.4 กับดักที่ 3: สอง ReplicaSet ที่ selector ทับกัน

{{FIG:T23}}

ไฟล์ `snack-rs-b.yaml` เป็น RS ตัวที่สองที่ selector `app: snack` เหมือน snack-rs ผลจริง

```text
$ kubectl get rs -n rs-lab; kubectl get pods -n rs-lab -l app=snack -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name,STATUS:.status.phase
NAME         DESIRED   CURRENT   READY   AGE
snack-rs     3         3         3       84s
snack-rs-b   3         3         3       15s
NAME               OWNER        STATUS
snack-rs-b-4psck   snack-rs-b   Running
snack-rs-b-ftbp8   snack-rs-b   Running
snack-rs-b-w7ctx   snack-rs-b   Running
snack-rs-cd24l     snack-rs     Running
snack-rs-f4p6n     snack-rs     Running
stray              snack-rs     Running
```

ownerReferences ป้องกันไม่ให้ RS แย่ง Pod ที่มีเจ้าของแล้ว แต่ละ RS จึงนับเฉพาะ 3 ตัวของตัวเองและไม่ลบของกันและกัน แต่ปัญหายังมี

- `kubectl get pods -l app=snack` เห็น 6 ตัวปนกัน คนที่ดูแลงงว่าทำไมมี 6
- Pod ที่ **ไม่มีเจ้าของ** และป้ายตรง (เช่น Pod หลง หรือ Pod ที่ถูก orphan) จะถูก RS ตัวที่ทำงานเร็วกว่ารับไป ผลไม่แน่นอน
- เครื่องมืออื่นที่เลือก Pod ด้วย label เดียวกัน (เช่น Service ในบทที่ 6) จะเห็น Pod ของทั้งสอง RS รวมกัน

แนวปฏิบัติ: ออกแบบ selector ให้เฉพาะเจาะจง เช่นเพิ่ม label ที่ระบุตัว RS (`app: snack` + `rs: snack-a`) และอย่าสร้าง Pod เดี่ยวที่ใช้ label ชุดเดียวกับ workload

### 6.5 เทคนิค debug: ถอด label แยก Pod ออกมาตรวจ

{{FIG:T24}}

ความสามารถในการ "ปล่อย" Pod กลายเป็นเครื่องมือที่มีประโยชน์ เมื่อ Pod ตัวหนึ่งมีอาการแปลก ๆ แต่เราไม่อยากให้ร้านขาดบูธ และไม่อยากลบ Pod ทิ้งก่อนตรวจ ให้ถอด label ที่ selector ใช้ออก

```text
$ kubectl label pod snack-rs-cd24l -n rs-lab app-
pod/snack-rs-cd24l unlabeled

$ kubectl get pod snack-rs-cd24l -n rs-lab -o jsonpath='owner={.metadata.ownerReferences}{"\n"}'
owner=

$ kubectl get pods -n rs-lab --show-labels
NAME             READY   STATUS              RESTARTS   AGE    LABELS
snack-rs-cd24l   1/1     Running             0          102s   <none>
snack-rs-f4p6n   1/1     Running             0          102s   app=snack
snack-rs-h9wk2   0/1     ContainerCreating   0          1s     app=snack
stray            1/1     Running             0          103s   app=snack

$ kubectl logs snack-rs-cd24l -n rs-lab
บูธขนม snack-rs-cd24l เปิดแล้ว
```

`app-` (ชื่อ label ตามด้วย `-`) คือการลบ label นั้น ผลที่ได้

1. RS **ปล่อย** Pod ทันที (ownerReferences ว่างตั้งแต่ตรวจครั้งแรกหลังสั่ง) เพราะ label ไม่ตรง selector แล้ว
2. RS นับได้ 2 จึงสร้างตัวแทน `snack-rs-h9wk2` ภายใน 1 วินาที ร้านยังครบ 3 บูธ
3. Pod เดิมยัง Running พร้อม log และสถานะให้ `kubectl logs`/`kubectl exec` เข้าไปตรวจ เมื่อตรวจเสร็จต้อง **ลบเอง** เพราะไม่มีใครดูแลแล้ว

อีกแบบคือเปลี่ยนค่าแทนการลบ เช่น `kubectl label pod <ชื่อ> app=debug --overwrite` ซึ่งช่วยให้ค้น Pod ที่แยกออกมาได้ด้วย `-l app=debug`

---

## 7. selector แก้ไม่ได้ และ template ใหม่ไม่เปลี่ยน Pod เดิม

### 7.1 selector เป็น immutable

{{FIG:T25}}

ใน `apps/v1` ฟิลด์ `spec.selector` ของ ReplicaSet **แก้ไม่ได้หลังสร้าง** ไฟล์ `labs/lab05-template/web-rs-new-selector.yaml` เพิ่ม `tier: front` ใน selector ของ RS `web` ที่มีอยู่แล้ว

```text
$ kubectl apply -f labs/lab05-template/web-rs-new-selector.yaml; echo "exit=$?"
The ReplicaSet "web" is invalid: spec.selector: Invalid value: {"matchLabels":{"app":"web","tier":"front"}}: field is immutable
exit=1
```

เหตุผลคือถ้าเปลี่ยน selector ได้ RS จะ "ลืม" Pod ชุดเดิมทันที (ป้ายไม่ตรงแล้ว) แล้วสร้างชุดใหม่ซ้อน ขณะที่ชุดเดิมกลายเป็น Pod ไร้เจ้าของค้างอยู่ ถ้าจำเป็นต้องเปลี่ยน selector จริง ๆ ให้สร้าง RS ใหม่ เช่น ลบ RS เดิมแบบ orphan (หัวข้อ 8) แล้วสร้าง RS ใหม่ที่ selector ใหม่และติด label ใหม่ให้ Pod

### 7.2 template ใหม่ไม่แตะ Pod ที่มีอยู่

{{FIG:T26}}

`web-rs.yaml` เป็น nginx 3 ตัว (`nginx:1.27-alpine`, env `VERSION=v1`) หน้าเว็บตอบ `web v1 from <ชื่อ Pod>` ส่วน `web-rs-v2.yaml` เปลี่ยนเป็น `nginx:1.28-alpine` และ `VERSION=v2` ผลจริงหลัง apply v2

```text
$ kubectl apply -f labs/lab05-template/web-rs-v2.yaml
replicaset.apps/web configured

$ kubectl get pods -n rs-lab -l app=web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,VERSION:.spec.containers[0].env[0].value
NAME        IMAGE               VERSION
web-6qrsq   nginx:1.27-alpine   v1
web-l5jx4   nginx:1.27-alpine   v1
web-q7bgq   nginx:1.27-alpine   v1

$ kubectl get rs web -n rs-lab -o wide
NAME   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES              SELECTOR
web    3         3         3       30s   nginx        nginx:1.28-alpine   app=web
```

RS บอกว่า IMAGES เป็น `1.28` แล้ว แต่ Pod ทุกตัวยังเป็น `1.27` เพราะในมุมของ reconciliation loop "ต้องการ 3 มี 3" ไม่มีส่วนต่างให้แก้ ReplicaSet **ไม่เทียบเนื้อหาของ Pod กับ template** template ใหม่จะใช้เฉพาะกับ Pod ที่ **เกิดใหม่** หลังจากนี้

```text
$ kubectl delete pod web-6qrsq -n rs-lab
pod "web-6qrsq" deleted from rs-lab namespace

NAME        IMAGE               VERSION   AGE
web-d4lf5   nginx:1.28-alpine   v2        2026-10-05T01:12:15Z
web-l5jx4   nginx:1.27-alpine   v1        2026-10-05T01:11:45Z
web-q7bgq   nginx:1.27-alpine   v1        2026-10-05T01:11:45Z
```

ถ้าจะเปลี่ยนรุ่นทั้งร้านด้วย ReplicaSet อย่างเดียว ต้อง **ลบ Pod เองทีละตัว** ซึ่งมีปัญหาหลายข้อ

- ต้องคอยดูเองว่าตัวใหม่ Ready แล้วจึงลบตัวถัดไป ถ้าลบพร้อมกันทั้งหมด (`delete pod -l app=web`) ร้านปิดทุกบูธพร้อมกัน
- ระหว่างเปลี่ยน มีทั้งรุ่นเก่าและรุ่นใหม่ปนกันโดยไม่มีใครติดตาม
- ถ้ารุ่นใหม่พัง ต้อง apply ไฟล์เดิมแล้วลบ Pod ทีละตัวอีกรอบ ไม่มีประวัติรุ่นให้ย้อน

งานทั้งหมดนี้คือเหตุผลที่มี **Deployment** (บทที่ 7) ซึ่งสร้าง ReplicaSet ใหม่ให้แต่ละรุ่นและค่อย ๆ ย้าย Pod ไปให้อัตโนมัติ

---

## 8. ลบ ReplicaSet: cascade และ orphan

### 8.1 สามแบบของการลบ

{{FIG:T27}}

| คำสั่ง | สิ่งที่เกิด |
|---|---|
| `kubectl delete rs snack-rs` (เท่ากับ `--cascade=background` ค่าเริ่มต้น) | RS หายทันที แล้ว **garbage collector** ไล่ลบ Pod ที่มี ownerReferences ชี้ไป RS ตัวนั้นตามหลัง |
| `kubectl delete rs snack-rs --cascade=foreground` | RS ได้ `deletionTimestamp` และ finalizer `foregroundDeletion` ค้างไว้ garbage collector ลบ Pod (ที่ `blockOwnerDeletion: true`) ก่อน เมื่อ Pod หายหมด RS จึงหาย |
| `kubectl delete rs snack-rs --cascade=orphan` | ถอด ownerReferences ออกจาก Pod แล้วลบเฉพาะ RS **Pod อยู่ต่อ** แบบไม่มีเจ้าของ |

ผลจริงของ foreground จาก LAB 6 (terminal 2 เฝ้า finalizer ส่วน terminal 2b เฝ้า RS)

```text
$ kubectl delete rs snack-rs -n rs-lab --cascade=foreground
replicaset.apps "snack-rs" deleted from rs-lab namespace

--- terminal 2: kubectl get rs snack-rs -n rs-lab -o jsonpath='{.metadata.finalizers}{"\n"}' -w ---
["foregroundDeletion"]
["foregroundDeletion"]
...
--- terminal 2b: kubectl get rs snack-rs -n rs-lab -w ---
NAME       DESIRED   CURRENT   READY   AGE
snack-rs   3         3         3       20s
snack-rs   3         2         2       22s
snack-rs   3         0         0       22s
...
```

คำสั่ง `kubectl delete` แบบ foreground ใช้เวลาราว 3.3 วินาทีเพราะรอ Pod หายก่อน ระหว่างนั้นตัว RS ยังอยู่ให้เห็น และ CURRENT ลดลง 3 → 2 → 0 ก่อน RS หายไป (แบบนี้เหมาะเมื่อต้องการแน่ใจว่า Pod หายหมดแล้วจริงก่อนทำขั้นต่อไป)

### 8.2 orphan แล้วรับเลี้ยงใหม่: เปลี่ยน RS โดยไม่ปิดบูธ

{{FIG:T28}}

ผลจริงจาก LAB 6: ลบแบบ orphan แล้ว Pod ทั้ง 3 ตัว (รวม `stray` ที่ถูกรับเลี้ยงไว้ใน LAB 4) ยังรันอยู่โดยไม่มีเจ้าของ

```text
$ kubectl delete rs snack-rs -n rs-lab --cascade=orphan
replicaset.apps "snack-rs" deleted from rs-lab namespace

$ kubectl get pods -n rs-lab -l app=snack -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name,UID:.metadata.ownerReferences[0].uid
NAME             OWNER    UID
snack-rs-f4p6n   <none>   <none>
snack-rs-h9wk2   <none>   <none>
stray            <none>   <none>
```

จากนั้น apply ไฟล์ snack-rs เดิมอีกครั้ง RS ใหม่ (uid ใหม่) รับเลี้ยงทั้ง 3 ตัวโดย **ไม่สร้าง Pod เพิ่มเลย** (`Events: <none>`)

```text
$ kubectl apply -f labs/lab01-first-rs/snack-rs.yaml
replicaset.apps/snack-rs created
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/snack-rs   3         3         3       3s
RS uid=38910974-1f02-43d6-b69a-32a745bd42a4
NAME             OWNER      UID
snack-rs-f4p6n   snack-rs   38910974-1f02-43d6-b69a-32a745bd42a4
snack-rs-h9wk2   snack-rs   38910974-1f02-43d6-b69a-32a745bd42a4
stray            snack-rs   38910974-1f02-43d6-b69a-32a745bd42a4
Events:            <none>
```

เทคนิคนี้ใช้เมื่อต้องการเปลี่ยนสิ่งที่แก้ไม่ได้ของ RS (เช่น ชื่อ หรือ selector ที่ยังครอบ Pod เดิมได้) โดยร้านไม่ต้องปิด

---

## 9. ReplicationController: รุ่นพี่ที่เกษียณแล้ว

{{FIG:T29}}

ก่อนมี ReplicaSet Kubernetes ใช้ **ReplicationController** (`apiVersion: v1`, `kind: ReplicationController`, ชื่อย่อ `rc`) ทำหน้าที่เดียวกัน ความต่างหลัก

| | ReplicationController | ReplicaSet |
|---|---|---|
| API | `v1` (core) | `apps/v1` |
| selector | แบบเท่ากับเท่านั้น (`app: snack`) และไม่ใส่ก็ได้ (ใช้ label ของ template) | `matchLabels` + `matchExpressions` (In/NotIn/Exists/DoesNotExist) และต้องระบุ |
| การเปลี่ยนรุ่น | เคยใช้ `kubectl rolling-update` ซึ่งทำงาน **ฝั่ง client** (ถ้าปิด terminal กลางทางก็ค้างครึ่ง ๆ) และถูกถอดออกจาก kubectl แล้ว | ไม่มีในตัว ใช้ **Deployment** ที่ทำงานฝั่ง server แทน |

API ของ ReplicationController ยังมีให้ใช้เพื่อความเข้ากันได้ แต่ **ไม่ควรสร้างใหม่** ถ้าเจอในระบบเก่า ให้รู้ว่ามันคือ "ReplicaSet รุ่นแรก"

---

## 10. ReplicaSet ใน namespace: quota, LimitRange และ PSA

### 10.1 ResourceQuota ตรวจที่ Pod ไม่ใช่ที่ RS

{{FIG:T30}}

จากบทที่ 4 ResourceQuota ถูกตรวจ **ตอนสร้าง object** แต่ละชิ้น สำหรับ ReplicaSet สิ่งที่ถูกตรวจกับ quota `pods` คือ **Pod แต่ละตัว** ที่ RS พยายามสร้าง ไม่ใช่ตัว RS ไฟล์ `labs/lab07-quota/00-ns-quota.yaml` สร้าง namespace `rs-quota` ที่มี quota `pods: "4"` และ LimitRange แบบบทที่ 4 ส่วน `quota-rs.yaml` ขอ `replicas: 6` ผลจริง

```text
$ kubectl get rs,pods -n rs-quota
NAME                       DESIRED   CURRENT   READY   AGE
replicaset.apps/quota-rs   6         4         4       6s
...

$ kubectl describe rs quota-rs -n rs-quota | sed -n "/Conditions/,\$p"
Conditions:
  Type             Status  Reason
  ----             ------  ------
  ReplicaFailure   True    FailedCreate
Events:
  Type     Reason            Age               From                   Message
  ----     ------            ----              ----                   -------
  Normal   SuccessfulCreate  6s                replicaset-controller  Created pod: quota-rs-z962r
...
  Warning  FailedCreate      5s                replicaset-controller  Error creating: pods "quota-rs-kxq2g" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4
...
  Warning  FailedCreate      4s (x11 over 5s)  replicaset-controller  (combined from similar events): Error creating: pods "quota-rs-4zbwn" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4
```

สิ่งที่ต้องอ่านให้เป็น

- `kubectl apply` สร้าง RS สำเร็จ ไม่มี error ที่หน้าจอ ความผิดปกติเห็นได้จาก `DESIRED 6 CURRENT 4` เท่านั้น
- ต้อง `kubectl describe rs` จึงเห็นสาเหตุ: condition `ReplicaFailure=True` (reason `FailedCreate`) และ event `exceeded quota`
- RS **พยายามซ้ำ** เรื่อย ๆ ด้วยการหน่วงเวลาที่ยาวขึ้น (backoff) เมื่อเพิ่ม quota เป็น 6 ด้วย `kubectl patch resourcequota ...` ในการทดลองจริง RS ใช้เวลา **46 วินาที** จึงสร้างครบ 6 และ condition หายไปเอง (ไม่ต้องสั่งอะไร RS เพิ่ม แต่ต้องรอ)

ส่วน LimitRange ทำงานกับ Pod ที่ RS สร้างตามปกติ template ที่ไม่มี `resources` จะได้ค่าตั้งต้นจาก LimitRange

```text
$ kubectl get pod quota-rs-5vjwb -n rs-quota -o jsonpath='{.spec.containers[0].resources}{"\n"}'
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
```

### 10.2 Pod Security Admission: เตือนที่ RS แต่ปฏิเสธที่ Pod

{{FIG:T31}}

PSA (บทที่ 4) ตรวจ workload ต่างกันตามโหมด

| โหมด | ตรวจตอนสร้าง RS (ดู Pod template) | ตรวจตอนสร้าง Pod |
|---|:---:|:---:|
| `warn` | ✅ แสดง `Warning:` ที่ kubectl | ✅ |
| `audit` | ✅ บันทึกใน audit log | ✅ |
| `enforce` | ❌ (RS ถูกสร้างได้) | ✅ ปฏิเสธ Pod |

ไฟล์ `labs/lab07-quota/psa-rs.yaml` สร้าง namespace `rs-psa` ที่มีทั้ง `enforce` และ `warn` ระดับ `restricted` และ RS busybox ที่ไม่มี `securityContext` ผลจริง

```text
$ kubectl apply -f labs/lab07-quota/psa-rs.yaml
namespace/rs-psa created
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "app" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "app" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "app" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
replicaset.apps/psa-rs created
NAME                     DESIRED   CURRENT   READY   AGE
replicaset.apps/psa-rs   3         0         0       4s

$ kubectl describe rs psa-rs -n rs-psa | sed -n "/Conditions/,\$p" | head -8
Conditions:
  Type             Status  Reason
  ----             ------  ------
  ReplicaFailure   True    FailedCreate
Events:
  Type     Reason        Age   From                   Message
  ----     ------        ----  ----                   -------
  Warning  FailedCreate  4s    replicaset-controller  Error creating: pods "psa-rs-7qhvg" is forbidden: violates PodSecurity "restricted:latest": ...
```

สังเกตว่าข้อความตอนสร้าง RS เป็นแค่ `Warning: would violate ...` แล้วตามด้วย `replicaset.apps/psa-rs created` ผู้ที่อ่านไม่ละเอียดจะคิดว่าสำเร็จ แต่จริง ๆ ร้าน **มี 0 บูธ** วิธีแก้คือแก้ template ให้ผ่าน restricted (ดูตารางในบทที่ 4 หัวข้อ 14.4) แล้ว apply ใหม่ RS จะสร้าง Pod ได้เอง ร้านน้องส้มใน LAB สุดท้ายมี `securityContext` ครบตั้งแต่บทที่ 4 จึงไม่มี Warning เลย

---

## 11. ReplicaSet กับการจัดวาง: anti-affinity และ topology spread

### 11.1 required anti-affinity

{{FIG:T32}}

ทบทวนบทที่ 3: ถ้า 3 บูธอยู่บนเรือลำเดียวกัน เรือลำนั้นล่มร้านก็ปิดทั้งร้าน เราจึงใส่ `podAntiAffinity` ใน template โดยใช้ **label ของ Pod ใน RS เดียวกัน** เป็นตัวเลือก และ `topologyKey: kubernetes.io/hostname` (1 เรือ = 1 โดเมน) ไฟล์ `labs/lab08-spread/spread-required.yaml` (ส่วนสำคัญ)

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: spread-req
  namespace: rs-spread
spec:
  replicas: 3
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
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: spread-req
              topologyKey: kubernetes.io/hostname   # 1 เรือ = 1 โดเมน
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
```

คลัสเตอร์ `lab` มี worker 2 ลำ (control-plane มี taint) แต่ขอ 3 บูธแบบ "ห้ามอยู่ด้วยกันเด็ดขาด" ผลจริง

```text
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE
pod/spread-req-cg7n6   0/1     Pending   0          6s    <none>        <none>
pod/spread-req-gg8pw   1/1     Running   0          6s    10.244.1.24   lab-worker
pod/spread-req-gmkgc   1/1     Running   0          6s    10.244.3.17   lab-worker2

Warning  FailedScheduling  6s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

`kubectl get rs` แสดง `3 3 2` เพราะ Pod ที่ Pending **ถูกนับเป็น CURRENT แล้ว** ReplicaSet ทำหน้าที่ของมันครบ (สร้าง Pod ครบ 3) ส่วนการหาเรือเป็นหน้าที่ของ scheduler ReplicaSet จึงไม่ "แก้" Pending ให้

### 11.2 preferred และ topologySpreadConstraints

{{FIG:T33}}

| วิธี | ผลจริงใน kind `lab` (worker 2 ลำ) |
|---|---|
| `preferredDuringSchedulingIgnoredDuringExecution` (weight 100) replicas 3 | ทำซ้ำ 5 รอบได้ **2+1 ทุกรอบ** ไม่มี Pending |
| `topologySpreadConstraints` `maxSkew: 1`, `whenUnsatisfiable: DoNotSchedule`, **`nodeTaintsPolicy: Honor`** replicas 4 | **2+2** แล้ว scale เป็น 5 ได้ **2+3** |
| แบบเดียวกันแต่ **ไม่ใส่** `nodeTaintsPolicy: Honor` | 1+1 และ **Pending 2 ตัว** (`2 node(s) didn't match pod topology spread constraints`) |

ส่วนสำคัญของ `spread-topology.yaml`

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: spread-topo
  namespace: rs-spread
spec:
  replicas: 4
  selector:
    matchLabels:
      app: spread-topo
  template:
    metadata:
      labels:
        app: spread-topo
    spec:
      topologySpreadConstraints:
        - maxSkew: 1                           # ต่างกันได้ไม่เกิน 1 ตัว
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule     # ถ้าทำไม่ได้ → ไม่จัดลง (Pending)
          nodeTaintsPolicy: Honor              # ไม่นับ control-plane (มี taint) — บท 003 LAB 5
          labelSelector:
            matchLabels:
              app: spread-topo
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
```

ทำไม `nodeTaintsPolicy: Honor` สำคัญ: ค่าเริ่มต้นคือ `Ignore` ซึ่งนับ `lab-control-plane` เป็นโดเมนหนึ่งด้วย (มี 0 Pod ตลอดเพราะมี taint) เมื่อ worker แต่ละลำมี 1 ตัว ส่วนต่างกับ control-plane คือ 1 แล้ว การวางเพิ่มจะทำให้ต่างเป็น 2 เกิน `maxSkew` จึง Pending (บทที่ 3 LAB 5 อธิบายไว้แล้ว)

ข้อควรรู้: กฎทั้งหมดนี้ใช้ **ตอน scheduler วาง Pod ใหม่เท่านั้น** เมื่อ scale ลงหรือเรือกลับมา ระบบไม่จัดสมดุลใหม่ให้ (เกณฑ์ลบตอน scale ลงข้อ 5 ในหัวข้อ 5.2 ช่วยให้ไม่เอียงมากเท่านั้น) ร้านน้องส้มใน LAB สุดท้ายใช้แบบ preferred เพราะไม่อยากให้บูธค้าง Pending เมื่อมีเรือน้อยกว่าจำนวนบูธ

---

## 12. ข้อควรรู้: Pod จาก ReplicaSet ไม่มีชื่อคงที่และ IP คงที่

{{FIG:T34}}

ReplicaSet ทำให้ร้าน **มีบูธครบจำนวน** เสมอ แต่ทุกบูธที่เกิดใหม่เป็น "คนละบูธ" กับตัวเดิมจริง ๆ

- **ชื่อใหม่** (`som-booth-rmcck` ถูกแทนด้วย `som-booth-z96mn`) สคริปต์หรือคำสั่งที่อ้างชื่อเดิมใช้ไม่ได้
- **IP ใหม่** และอาจอยู่เรือคนละลำ ลูกค้าที่จำ IP เดิมหาร้านไม่เจอ
- **port-forward ที่ต่อ Pod เดิมหลุด** ผลจริงจาก LAB 9 เมื่อมีคนเข้า port ที่ต่อกับ Pod ที่ถูกลบไปแล้ว

```text
E1005 08:21:37.281151   34928 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod 4547b54fde31..., uid : network namespace for sandbox \"4547b54fde31...\" is closed" localPort=8081 remotePort=3000
error: lost connection to pod
```

- **ข้อมูลใน `emptyDir` หายพร้อม Pod** ร้านแบบ all-in-one ของบทที่ 2–4 มีฐานข้อมูลอยู่ใน Pod เมื่อนำมาเป็น template ของ ReplicaSet แต่ละบูธจึงมีฐานข้อมูลของตัวเอง ออเดอร์ของแต่ละบูธไม่ตรงกัน และบูธใหม่เริ่มจากออเดอร์ 0

สิ่งที่ร้านต้องการเพิ่มคือ **"ที่อยู่คงที่"** ที่ลูกค้าจำได้ และคอยตามหา Pod ด้วย label แบบเดียวกับที่ ReplicaSet ใช้นับ (นี่คือ **Service** ในบทที่ 6) และการแยกฐานข้อมูลออกมาให้ทุกบูธใช้ร่วมกัน

---

## 13. สรุปและปูทางบทถัดไป

### 13.1 สรุป

{{FIG:T35}}

- Pod เดี่ยวตายแล้วไม่ฟื้น ต้องมี **workload controller** ดูแล controller ทุกตัวทำงานแบบ **reconciliation loop** เทียบ `spec` กับสภาพจริงทุกรอบ (level-triggered) อยู่ใน `kube-controller-manager` และสั่งงานผ่าน API server เท่านั้น
- **ReplicaSet** = `replicas` + `selector` + `template` นับ Pod ใน namespace เดียวกันที่ label ตรง selector สร้างจาก template เมื่อขาด ลบเมื่อเกิน label ของ template ต้องตรง selector และ selector แก้ไม่ได้
- Pod ของ RS ชื่อ `<rs>-<สุ่ม 5 ตัว>` มี `ownerReferences` (`controller: true`, `blockOwnerDeletion: true`) ชี้ไปที่ RS
- **Self-healing**: ลบ Pod → ตัวใหม่เกิดทันทีขณะตัวเก่ายัง Terminating; drain ไม่ต้อง `--force`; เรือล่ม → รอ NotReady (~45 วินาที) + `tolerationSeconds` (ค่าเริ่มต้น 300) ก่อนสร้างแทน
- **Scale** ได้ทันที แต่ `kubectl apply` ไฟล์ทับค่าที่ scale ไว้ ตอน scale ลง RS เลือกลบ Pod ที่ยังไม่พร้อม/อยู่เรือแออัด/ใหม่กว่าก่อน
- **นับจาก label**: รับเลี้ยง Pod ไร้เจ้าของที่ป้ายตรง ลบ Pod ที่เกิน และใช้ถอด label เพื่อแยก Pod ออกมา debug ได้
- template ใหม่ **ไม่เปลี่ยน Pod เดิม** การลบ RS มี background (ค่าเริ่มต้น), foreground และ orphan
- quota และ PSA enforce ตรวจที่ **Pod** RS จึงสร้างได้แต่ Pod ขาด ต้องดู `DESIRED/CURRENT` และ `describe rs` (`ReplicaFailure`, `FailedCreate`)

**ตารางที่ 2** คำสั่งที่ใช้บ่อยในบทนี้

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl get rs [-o wide] -n <ns>` | ดู DESIRED/CURRENT/READY (และ IMAGES/SELECTOR ของ template) |
| `kubectl describe rs <ชื่อ> -n <ns>` | ดู template, Conditions และ Events (`SuccessfulCreate`, `SuccessfulDelete`, `FailedCreate`) |
| `kubectl get rs <ชื่อ> -o jsonpath='{.status}'` | ดู status เต็ม |
| `kubectl scale rs <ชื่อ> --replicas=N` | เปลี่ยนจำนวน (ไม่แก้ไฟล์) |
| `KUBE_EDITOR=nano kubectl edit rs <ชื่อ>` | แก้ object สด ๆ |
| `kubectl get pods -l app=snack --show-labels` | ดู Pod ตาม selector และป้ายทั้งหมด |
| `kubectl get pod <ชื่อ> -o jsonpath='{.metadata.ownerReferences}'` | ดูเจ้าของของ Pod |
| `kubectl get pods -o custom-columns=NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].name` | ดูเจ้าของของทุก Pod ในตารางเดียว |
| `kubectl label pod <ชื่อ> app-` | ถอด label เพื่อแยก Pod ออกจาก RS |
| `kubectl delete rs <ชื่อ> --cascade=orphan` / `--cascade=foreground` | ลบ RS แต่เก็บ Pod / ลบ Pod ให้หมดก่อน RS |
| `kubectl get pods -w` | เฝ้าดูการเปลี่ยนแปลงแบบสด |
| `kubectl get events --field-selector reason=SuccessfulDelete` | หาว่า RS ลบ Pod ตัวไหน |

**ตารางที่ 3** Pod เดี่ยวเทียบกับ ReplicaSet

| สถานการณ์ | Pod เดี่ยว (บทที่ 2–4) | ReplicaSet (บทนี้) |
|---|---|---|
| ลบ Pod | หายถาวร | ตัวใหม่เกิดทันที (ชื่อใหม่ IP ใหม่) |
| drain Node | ต้อง `--force` และ Pod หาย | evict ได้เลย ตัวแทนเกิดบนเรืออื่น |
| เรือล่ม | ถูกไล่หลัง ~300 วินาทีแล้วหาย | ถูกไล่แล้วตัวแทนเกิดบนเรืออื่น (ปรับเวลาด้วย `tolerationSeconds`) |
| เพิ่ม/ลดจำนวน | สร้าง/ลบทีละไฟล์ทีละชื่อ | `kubectl scale` หรือแก้ `replicas` |
| เปลี่ยนรุ่น | ลบแล้วสร้างใหม่ (ร้านปิดระหว่างนั้น) | แก้ template แล้ว **ยังต้องลบ Pod เองทีละตัว** |
| ที่อยู่ของร้าน | ชื่อเดิมได้ แต่ IP ใหม่ทุกครั้ง | ชื่อและ IP ใหม่ทุกครั้ง |

### 13.2 ปัญหาที่ส่งต่อบทถัดไป

{{FIG:T36}}

LAB สุดท้ายของบทนี้นำร้านน้องส้ม all-in-one ของบทที่ 4 มาเป็น template ของ ReplicaSet `som-booth` 3 บูธ ร้านไม่ล้มแม้บูธหาย แต่เราจะเห็นปัญหาใหม่ 3 ข้อด้วยตาตัวเอง

| ปัญหาที่เห็นใน LAB 9 | ทำไม ReplicaSet แก้ไม่ได้ | บทที่แก้ |
|---|---|---|
| ออเดอร์ของแต่ละบูธไม่ตรงกัน บูธใหม่เริ่มจาก 0 | แต่ละ Pod มีฐานข้อมูล (emptyDir) ของตัวเอง | บทที่ 6 แยกฐานข้อมูลออกมาให้ทุกบูธใช้ร่วมกัน |
| ลูกค้าต้องเข้าทีละบูธด้วย port-forward และหลุดทุกครั้งที่บูธถูกแทน | Pod ไม่มีชื่อ/IP คงที่ | บทที่ 6 **Service** ที่อยู่คงที่ที่ตามหา Pod ด้วย label |
| เปลี่ยนรุ่นต้องลบ Pod เองทีละตัว รอเอง ย้อนรุ่นยาก | RS ไม่เทียบ Pod กับ template | บทที่ 7 **Deployment** เปลี่ยนรุ่นทีละบูธอัตโนมัติและย้อนรุ่นได้ |

ในงานจริงแทบไม่มีใครสร้าง ReplicaSet เองโดยตรง แต่ **ต้องเข้าใจ ReplicaSet** เพราะ Deployment ในบทที่ 7 สร้างและจัดการ ReplicaSet ให้เบื้องหลัง ทุกพฤติกรรมในบทนี้ (self-healing, การนับจาก label, ownerReferences, ลำดับการลบตอน scale ลง) ยังเกิดขึ้นเหมือนเดิมใน Deployment

---

## 14. คำถามทบทวน

**1. ทำไม Pod เดี่ยวที่ถูกลบจึงไม่ถูกสร้างใหม่ ทั้งที่ Pod มี `restartPolicy: Always`**

<details>
<summary>แนวคำตอบ</summary>

`restartPolicy` เป็นหน้าที่ของ kubelet ที่รีสตาร์ต **container** ภายใน Pod ที่ยังมีอยู่ เมื่อ **Pod object** ถูกลบ (หรือ Node หายไปจนถูกไล่) ไม่มีใครถือ "ความต้องการ" ว่าต้องมี Pod นี้อยู่ จึงไม่มีใครสร้างใหม่ ต้องมี controller ระดับสูงกว่า เช่น ReplicaSet ที่เก็บ desired state (`replicas` + template) ไว้และสร้าง Pod ใหม่แทน
</details>

**2. อธิบาย reconciliation loop ของ ReplicaSet และความหมายของ level-triggered ถ้า kube-controller-manager รีสตาร์ตในช่วงที่มีคนลบ Pod 2 ตัว จะเกิดอะไรขึ้น**

<details>
<summary>แนวคำตอบ</summary>

loop คือ observe (นับ Pod ที่ label ตรง selector และไม่ได้กำลังถูกลบ) → diff (เทียบกับ `spec.replicas`) → act (สร้างจาก template หรือลบส่วนเกินผ่าน API server) วนไม่รู้จบ level-triggered หมายถึงตัดสินใจจากสภาพปัจจุบันทั้งหมด ไม่ได้พึ่งการได้ยินเหตุการณ์ "ลบ" ทีละครั้ง เมื่อ controller กลับมาและ list Pod ใหม่ จะนับได้ 1 จาก 3 แล้วสร้างเพิ่ม 2 ตัวได้ถูกต้อง แม้จะพลาดเหตุการณ์การลบไป
</details>

**3. ไฟล์ ReplicaSet ด้านล่างจะเกิดอะไรขึ้นเมื่อ apply และทำไม Kubernetes จึงออกแบบให้เป็นแบบนั้น**

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: snack-rs-bad
spec:
  replicas: 3
  selector:
    matchLabels:
      app: snack
  template:
    metadata:
      labels:
        app: snak
    spec:
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
```

<details>
<summary>แนวคำตอบ</summary>

ถูกปฏิเสธด้วย `The ReplicaSet "snack-rs-bad" is invalid: spec.template.metadata.labels: Invalid value: {"app":"snak"}: `selector` does not match template `labels`` เพราะถ้ายอมให้สร้าง Pod ที่สร้างออกมาจะมีป้าย `snak` ซึ่ง RS นับไม่เห็น RS จะนับได้ 0 ตลอดและสร้าง Pod ไปไม่รู้จบ
</details>

**4. `kubectl get rs` แสดง `snack-rs   3   3   1` ระหว่างที่เรือ `lab-worker2` ล่ม อธิบายแต่ละตัวเลข และทำไม RS ยังไม่สร้างตัวแทน**

<details>
<summary>แนวคำตอบ</summary>

DESIRED 3 = `spec.replicas`, CURRENT 3 = RS ยังนับ Pod ทั้ง 3 ตัว (Pod บนเรือที่ล่มยังไม่ถูกลบ ไม่มี `deletionTimestamp`), READY 1 = มีแค่ Pod บนเรือที่ยังดีที่ Ready RS ไม่สร้างตัวแทนเพราะ "ต้องการ 3 นับได้ 3" Pod บนเรือที่ล่มจะถูกไล่หลังครบ `tolerationSeconds` ของ taint `node.kubernetes.io/unreachable` (ค่าเริ่มต้น 300 วินาที) เมื่อถูกไล่แล้ว RS จึงไม่นับและสร้างตัวแทน
</details>

**5. ถ้าต้องการให้ร้านสร้างบูธแทนเร็วขึ้นเมื่อเรือล่ม ทำอย่างไร และมีข้อเสียอะไร**

<details>
<summary>แนวคำตอบ</summary>

ใส่ toleration ของ `node.kubernetes.io/not-ready` และ `node.kubernetes.io/unreachable` effect `NoExecute` พร้อม `tolerationSeconds` ที่สั้นลง (เช่น 30) ใน **template** แล้วให้ Pod ถูกสร้างใหม่ (Pod เดิมไม่เปลี่ยนตาม template) ในการทดลองจริงตัวแทนเกิดราว 75 วินาทีหลังเริ่ม stop เรือ ข้อเสียคือถ้าเครือข่ายสะดุดเพียงชั่วครู่ Pod อาจถูกไล่และสร้างใหม่โดยไม่จำเป็น (ข้อมูลใน emptyDir หาย, เริ่มระบบใหม่)
</details>

**6. scale snack-rs จาก 5 เหลือ 2 ในการทดลองจริง ตัวที่ถูกลบมีตัวเก่าปนอยู่ด้วย เพราะอะไร และถ้าอยากกำหนดเองว่าตัวไหนควรถูกลบก่อนทำอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

RS เรียง Pod ตามเกณฑ์หลายข้อ เกณฑ์ "อยู่บนเรือที่มี Pod ของ RS นี้มากกว่า" มาก่อนเกณฑ์อายุ ตอนนั้น lab-worker2 มี 3 ตัว จึงลบตัวบน lab-worker2 (รวมตัวเก่า `ldzjc`) ก่อน และเกณฑ์เวลาที่ Ready ใช้การปัดแบบลอการิทึม ทำให้อายุใกล้กันถือว่าเท่ากัน กำหนดเองได้ด้วย annotation `controller.kubernetes.io/pod-deletion-cost` บน Pod (ค่ายิ่งต่ำยิ่งถูกลบก่อน)
</details>

**7. เพื่อนร่วมทีม `kubectl scale rs som-booth --replicas=0` เพื่อปิดร้านชั่วคราว ต่อมามีคน `kubectl apply -f som-booth.yaml` (ในไฟล์ `replicas: 3`) จะเกิดอะไรขึ้น และควรป้องกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

apply จะตั้ง `replicas` กลับเป็น 3 ตามไฟล์ ร้านเปิด 3 บูธทันที เพราะ `kubectl scale` ไม่ได้แก้ไฟล์ ควรใช้ไฟล์เป็นความจริงเพียงแหล่งเดียว (แก้ `replicas` ในไฟล์แล้ว apply) หรือถ้าใช้ scale ต้องแก้ไฟล์ตามให้ตรงกัน
</details>

**8. มี Pod เดี่ยวชื่อ `stray` label `app: snack` อยู่ก่อน แล้วจึงสร้าง snack-rs (replicas 3, selector `app: snack`) จะมี Pod กี่ตัว และ `stray` เปลี่ยนไปอย่างไร ถ้าสลับลำดับ (สร้าง RS ก่อน แล้วสร้าง stray) ผลต่างกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

กรณีแรก RS รับเลี้ยง `stray` (ใส่ ownerReferences ชี้ snack-rs) แล้วสร้างเพิ่มแค่ 2 รวม 3 ตัว `stray` ยังทำงานตาม command เดิมของตัวเองที่ต่างจาก template กรณีหลัง RS มีครบ 3 แล้ว เมื่อ `stray` เกิดขึ้นนับได้ 4 RS จึงลบ Pod หนึ่งตัวทันที ซึ่งตามเกณฑ์คือ `stray` ที่ยังไม่ Ready และใหม่สุด (เห็น `stray 0/1 Terminating 0s`)
</details>

**9. Pod `som-booth-abcde` ตอบช้าผิดปกติ อยากเก็บไว้ตรวจโดยร้านยังมี 3 บูธ ทำอย่างไร และหลังตรวจเสร็จต้องทำอะไร**

<details>
<summary>แนวคำตอบ</summary>

ถอด label ที่ selector ใช้ `kubectl label pod som-booth-abcde -n som-booths app-` (หรือ `app=debug --overwrite`) RS จะถอด ownerReferences ปล่อย Pod นั้นทันทีและสร้างบูธใหม่แทน Pod เดิมยังรันให้ `logs`/`exec` ตรวจได้ เมื่อเสร็จต้อง `kubectl delete pod som-booth-abcde` เองเพราะไม่มี controller ดูแลแล้ว
</details>

**10. แก้ image ใน template ของ RS `web` จาก `nginx:1.27-alpine` เป็น `nginx:1.28-alpine` แล้ว apply `kubectl get rs web -o wide` บอก `nginx:1.28-alpine` แต่หน้าเว็บยังเป็นรุ่นเก่า เพราะอะไร และจะทำให้ทุก Pod เป็นรุ่นใหม่ด้วย ReplicaSet อย่างเดียวได้อย่างไร มีข้อเสียอะไร**

<details>
<summary>แนวคำตอบ</summary>

คอลัมน์ IMAGES แสดง image ของ template ส่วน Pod ที่มีอยู่ไม่ถูกเปลี่ยน เพราะ RS นับได้ครบ 3 ไม่มีส่วนต่างให้แก้ และไม่เทียบเนื้อหา Pod กับ template ต้องลบ Pod ทีละตัวเพื่อให้ตัวใหม่สร้างจาก template ใหม่ ข้อเสีย: ต้องรอให้ตัวใหม่ Ready เองก่อนลบตัวถัดไป ถ้าลบพร้อมกันร้านปิด ระหว่างทางรุ่นปนกัน และย้อนรุ่นต้องทำซ้ำด้วยมือ ไม่มีประวัติ — งานนี้คือหน้าที่ของ Deployment (บทที่ 7)
</details>

**11. อยากเปลี่ยน selector ของ RS ที่รันอยู่ แต่ได้ `field is immutable` จะเปลี่ยนโดยไม่ปิดร้านได้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ลบ RS เดิมด้วย `kubectl delete rs <ชื่อ> --cascade=orphan` (Pod อยู่ต่อแบบไม่มีเจ้าของ) ติด label ใหม่ให้ Pod ถ้า selector ใหม่ต้องใช้ (`kubectl label pod ...`) แล้วสร้าง RS ใหม่ที่ selector ใหม่ RS ใหม่จะรับเลี้ยง Pod ที่ label ตรงโดยไม่สร้างเพิ่ม (ในการทดลองจริงได้ `3 3 3` และ `Events: <none>`)
</details>

**12. เปรียบเทียบ `kubectl delete rs snack-rs` แบบ background, foreground และ orphan**

<details>
<summary>แนวคำตอบ</summary>

background (ค่าเริ่มต้น): RS หายทันที garbage collector ลบ Pod ตามหลัง; foreground: RS ค้างอยู่ด้วย finalizer `foregroundDeletion` จน Pod ที่มี `blockOwnerDeletion: true` ถูกลบหมด แล้ว RS จึงหาย (เห็น CURRENT 3 → 2 → 0); orphan: ถอด ownerReferences ออกจาก Pod แล้วลบเฉพาะ RS Pod รันต่อแบบไร้เจ้าของ
</details>

**13. namespace มี ResourceQuota `pods: 4` แต่สร้าง RS `replicas: 6` `kubectl apply` ไม่มี error แล้วจะรู้ได้อย่างไรว่ามีปัญหา และหลังเพิ่ม quota ต้องทำอะไรต่อ**

<details>
<summary>แนวคำตอบ</summary>

quota ตรวจตอนสร้าง Pod แต่ละตัว ไม่ใช่ตอนสร้าง RS ดูจาก `kubectl get rs` ที่ `DESIRED 6 CURRENT 4` และ `kubectl describe rs` ที่มี condition `ReplicaFailure True FailedCreate` และ event `exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4` หลังเพิ่ม quota ไม่ต้องทำอะไรกับ RS เพราะ RS พยายามซ้ำเอง แต่มี backoff ในการทดลองจริงใช้ 46 วินาทีจึงครบ 6
</details>

**14. namespace ตั้ง `pod-security.kubernetes.io/enforce: restricted` แล้ว apply RS ที่ไม่มี securityContext ได้ข้อความ `Warning: would violate PodSecurity ...` ตามด้วย `replicaset.apps/psa-rs created` แปลว่าร้านเปิดสำเร็จหรือไม่ อธิบาย**

<details>
<summary>แนวคำตอบ</summary>

ไม่สำเร็จ RS ถูกสร้างได้เพราะ enforce ตรวจเฉพาะ Pod (ส่วน Warning มาจากโหมด warn ที่ตรวจ Pod template ของ workload) เมื่อ RS สร้าง Pod ทุกตัวถูกปฏิเสธ ได้ `psa-rs 3 0 0` และ event `FailedCreate ... violates PodSecurity "restricted:latest"` ต้องแก้ template ให้ผ่าน restricted แล้ว apply ใหม่
</details>

**15. RS 3 ตัวใช้ required podAntiAffinity กับ label ตัวเองบนคลัสเตอร์ที่มี worker 2 ลำ ได้ Pod หนึ่งตัว Pending ทำไม RS ไม่แก้ปัญหานี้ และควรเปลี่ยนเป็นอะไร**

<details>
<summary>แนวคำตอบ</summary>

RS สร้าง Pod ครบ 3 แล้ว (CURRENT 3) หน้าที่ของ RS จบที่การมี Pod object ครบ การหาเรือเป็นของ scheduler ซึ่งหาเรือที่ไม่มี Pod เดียวกันไม่ได้ (`2 node(s) didn't match pod anti-affinity rules` และ control-plane มี taint) ควรใช้ preferred anti-affinity (ได้ 2+1) หรือ topologySpreadConstraints `maxSkew: 1` + `nodeTaintsPolicy: Honor`
</details>

**16. ReplicaSet แก้ปัญหาอะไรของร้านน้องส้มได้แล้ว และยังเหลือปัญหาอะไรที่บทที่ 6 และ 7 จะแก้**

<details>
<summary>แนวคำตอบ</summary>

แก้ได้: จำนวนบูธครบเสมอเมื่อ Pod ถูกลบ เรือถูก drain หรือเรือล่ม และ scale ได้ทันที ยังเหลือ: (1) แต่ละบูธมีฐานข้อมูลของตัวเอง ออเดอร์ไม่ตรงกัน (2) ชื่อ/IP เปลี่ยนทุกครั้ง ต้อง port-forward ทีละ Pod และหลุดเมื่อ Pod ถูกแทน → บทที่ 6 Service (และแยกฐานข้อมูล) (3) เปลี่ยนรุ่นต้องลบ Pod เองทีละตัว ไม่มีประวัติให้ย้อน → บทที่ 7 Deployment
</details>

---

## 15. เอกสารอ้างอิง

1. The Kubernetes Authors. *ReplicaSet*. https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
2. The Kubernetes Authors. *Workload Management*. https://kubernetes.io/docs/concepts/workloads/controllers/
3. The Kubernetes Authors. *Controllers*. https://kubernetes.io/docs/concepts/architecture/controller/
4. The Kubernetes Authors. *kube-controller-manager* (command line reference). https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/
5. The Kubernetes Authors. *Labels and Selectors*. https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
6. The Kubernetes Authors. *Owners and Dependents*. https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/
7. The Kubernetes Authors. *Garbage Collection*. https://kubernetes.io/docs/concepts/architecture/garbage-collection/
8. The Kubernetes Authors. *Use Cascading Deletion in a Cluster*. https://kubernetes.io/docs/tasks/administer-cluster/use-cascading-deletion/
9. The Kubernetes Authors. *ReplicationController*. https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/
10. The Kubernetes Authors. *Pod Lifecycle*. https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
11. The Kubernetes Authors. *Taints and Tolerations* (taint based evictions). https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
12. The Kubernetes Authors. *Safely Drain a Node*. https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/
13. The Kubernetes Authors. *Assigning Pods to Nodes* (affinity and anti-affinity). https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/
14. The Kubernetes Authors. *Pod Topology Spread Constraints*. https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
15. The Kubernetes Authors. *Resource Quotas*. https://kubernetes.io/docs/concepts/policy/resource-quotas/
16. The Kubernetes Authors. *Limit Ranges*. https://kubernetes.io/docs/concepts/policy/limit-range/
17. The Kubernetes Authors. *Pod Security Admission*. https://kubernetes.io/docs/concepts/security/pod-security-admission/
18. The Kubernetes Authors. *Well-Known Labels, Annotations and Taints* (`controller.kubernetes.io/pod-deletion-cost`, `node.kubernetes.io/unreachable`). https://kubernetes.io/docs/reference/labels-annotations-taints/
19. The Kubernetes Authors. *kubectl scale*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_scale/
20. The Kubernetes Authors. *Deployments* (อ่านล่วงหน้าสำหรับบทที่ 7). https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
21. The Kubernetes Authors. *Service* (อ่านล่วงหน้าสำหรับบทที่ 6). https://kubernetes.io/docs/concepts/services-networking/service/

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 36 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น IP ของ Pod และเวลา) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (Kubernetes v1.37.0) ค่าเวลา, IP, ชื่อ Pod และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างกัน
