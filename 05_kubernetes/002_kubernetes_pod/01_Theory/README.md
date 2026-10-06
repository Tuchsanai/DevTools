# Kubernetes Pod: Pod แรกของน้องส้ม ตั้งแต่แนวคิดถึงการเขียน YAML

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Pod — หน่วยการติดตั้งใช้งานที่เล็กที่สุด, YAML manifest, วงจรชีวิต, การตรวจสุขภาพ และ Pod หลาย container
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 1 Kubernetes และสถาปัตยกรรม](../../001_kubernetes-introduction/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

บทที่ 1 ให้ภาพรวมว่า Kubernetes ทำงานเหมือน **ท่าเรือขนส่งตู้สินค้า** ที่มีหอบังคับการ (Control Plane) คอยตัดสินใจ และมีเรือ (Worker Node) บรรทุกตู้สินค้า (container) บทนี้ซูมเข้าไปที่ "กล่อง" ที่ห่อตู้สินค้าก่อนขึ้นเรือ นั่นคือ **Pod** ซึ่งเป็นหน่วยที่เล็กที่สุดที่ Kubernetes สร้าง จัดวาง และดูแลได้

เนื้อหาเริ่มจากความหมายของ Pod ความสัมพันธ์กับ Node และเครือข่ายภายใน Pod ต่อด้วยเส้นทางที่ Pod ถูกสร้างขึ้นจริงในคลัสเตอร์ จากนั้นสอน **การเขียน Kubernetes YAML** ตั้งแต่ไวยากรณ์ YAML พื้นฐาน, โครงสร้าง manifest สี่ส่วน, การกำหนด image, env, command/args, resources, labels ไปจนถึงการสร้าง/ลบ Pod จากไฟล์ด้วย `kubectl apply`/`create`/`delete` ช่วงท้ายเป็นเรื่อง **วงจรชีวิตของ Pod** และการอ่านข้อผิดพลาดยอดฮิต (CrashLoopBackOff, ImagePullBackOff, OOMKilled, Pending), **probes**, **emptyDir**, **init container และ sidecar** รวมถึงชุดเครื่องมือดีบัก และการเปิดเว็บใน Pod จาก browser ด้วย `kubectl port-forward` ร่วมกับ `ssh -L`

ตลอดบทเราจะเดินทางไปกับ **น้องส้ม** ผู้ช่วยกัปตันท่าเรือ Kubernetes ที่อยากเปิด "ร้านอาหารแมวน้องส้ม" บนเรือ ผลลัพธ์คำสั่งที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (Kubernetes v1.37.0) ของ LAB ประจำบท เมื่อ 4 ตุลาคม 2569

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายว่า Pod คืออะไร แตกต่างจาก container อย่างไร และเหตุใด Kubernetes จึงจัดการ container ผ่าน Pod
2. อธิบายการแชร์เครือข่าย (IP เดียว, `localhost`) และ volume ภายใน Pod รวมถึงการสื่อสารระหว่าง Pod ได้
3. อธิบายลำดับเหตุการณ์ตั้งแต่ `kubectl apply` จนกระทั่ง Pod อยู่ในสถานะ `Running`
4. อ่านและเขียนไฟล์ YAML ของ Pod ที่ถูกต้อง ทั้งส่วน `apiVersion`, `kind`, `metadata`, `spec` และกำหนด image, ports, env, command/args, resources, labels ได้
5. อ่าน phase, STATUS, RESTARTS และ Events เพื่อวินิจฉัยปัญหา CrashLoopBackOff, ImagePullBackOff, OOMKilled และ Pending ได้
6. เลือกใช้ startupProbe, livenessProbe และ readinessProbe ได้เหมาะสม
7. ออกแบบ Pod หลาย container ด้วย emptyDir, init container และ sidecar และบอกได้ว่าเมื่อใดไม่ควรรวม container ไว้ใน Pod เดียว
8. ใช้ `kubectl get/describe/logs/exec/port-forward` สำรวจและดีบัก Pod และเปิดเว็บใน Pod จาก browser ผ่าน SSH tunnel ได้

## สารบัญ

1. [บทนำ: น้องส้มอยากเปิดร้าน](#1-บทนำ-น้องส้มอยากเปิดร้าน)
2. [Pod คืออะไร](#2-pod-คืออะไร)
3. [ทำไมต้องมี Pod ไม่ใช้ container ตรง ๆ](#3-ทำไมต้องมี-pod-ไม่ใช้-container-ตรง-ๆ)
4. [Pod กับ Node](#4-pod-กับ-node)
5. [เครือข่ายของ Pod](#5-เครือข่ายของ-pod)
6. [เส้นทางการเกิดของ Pod](#6-เส้นทางการเกิดของ-pod)
7. [พื้นฐาน YAML](#7-พื้นฐาน-yaml)
8. [โครงสร้าง Kubernetes Manifest](#8-โครงสร้าง-kubernetes-manifest)
9. [เขียน spec ของ container](#9-เขียน-spec-ของ-container)
10. [Labels, Selectors และ Annotations](#10-labels-selectors-และ-annotations)
11. [สร้างและลบ Pod จากไฟล์ YAML](#11-สร้างและลบ-pod-จากไฟล์-yaml)
12. [วงจรชีวิตของ Pod](#12-วงจรชีวิตของ-pod)
13. [Probes ตรวจสุขภาพ container](#13-probes-ตรวจสุขภาพ-container)
14. [Volume ภายใน Pod ด้วย emptyDir](#14-volume-ภายใน-pod-ด้วย-emptydir)
15. [Multi-container Pod](#15-multi-container-pod)
16. [เข้าถึงและดีบัก Pod](#16-เข้าถึงและดีบัก-pod)
17. [Pod เป็นของชั่วคราว](#17-pod-เป็นของชั่วคราว)
18. [ปูทางบทหน้า: Deployment และ Service](#18-ปูทางบทหน้า-deployment-และ-service)
19. [สรุปและคำถามทบทวน](#19-สรุปและคำถามทบทวน)
20. [เอกสารอ้างอิง](#20-เอกสารอ้างอิง)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [น้องส้มฝันอยากเปิดร้านอาหารแมวบนเรือ](#fig-1) | 17 | [Labels และ Selectors](#fig-17) |
| 2 | [ทบทวนอุปมาท่าเรือ](#fig-2) | 18 | [เครื่องมือเสริม: explain และ --dry-run](#fig-18) |
| 3 | [Pod คืออะไร](#fig-3) | 19 | [Pod phase ทั้ง 5 ค่า](#fig-19) |
| 4 | [ทำไมต้องห่อ container ด้วย Pod](#fig-4) | 20 | [Container state และ restartPolicy](#fig-20) |
| 5 | [Pod อยู่บน Node เดียวเสมอ](#fig-5) | 21 | [CrashLoopBackOff](#fig-21) |
| 6 | [เครือข่ายร่วมภายใน Pod และ localhost](#fig-6) | 22 | [ErrImagePull / ImagePullBackOff](#fig-22) |
| 7 | [Pod-to-Pod ด้วย Pod IP](#fig-7) | 23 | [Probe สามแบบ](#fig-23) |
| 8 | [เส้นทางการเกิดของ Pod](#fig-8) | 24 | [กลไกของ probe](#fig-24) |
| 9 | [ไวยากรณ์ YAML พื้นฐาน](#fig-9) | 25 | [emptyDir ชั้นวางของร่วม](#fig-25) |
| 10 | [ข้อผิดพลาด YAML ที่พบบ่อย](#fig-10) | 26 | [Init containers](#fig-26) |
| 11 | [Manifest สี่ส่วน](#fig-11) | 27 | [Sidecar pattern](#fig-27) |
| 12 | [spec กับ status](#fig-12) | 28 | [ชุดเครื่องมือดีบัก Pod](#fig-28) |
| 13 | [image, tag และ containerPort](#fig-13) | 29 | [port-forward ร่วมกับ ssh -L](#fig-29) |
| 14 | [ตัวแปร env](#fig-14) | 30 | [Pod เป็นของชั่วคราว](#fig-30) |
| 15 | [command/args ทับ ENTRYPOINT/CMD](#fig-15) | 31 | [ตัวอย่างบทหน้า: Deployment และ Service](#fig-31) |
| 16 | [requests และ limits](#fig-16) | 32 | [สรุปบทที่ 2](#fig-32) |

---

## 1. บทนำ: น้องส้มอยากเปิดร้าน

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

<p align="center" id="fig-1">
  <img src="images/01-opening-som-dream-shop.png" alt="รูปที่ 1 น้องส้มฝันอยากเปิดร้านอาหารแมวบนเรือ" width="900"><br>
  <em><b>รูปที่ 1</b> น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ฝันอยากเปิดร้านอาหารแมวบนเรือ จึงต้องเรียนรู้การจัดกล่อง Pod</em>
</p>

หลังจากเรียนรู้ว่าท่าเรือ Kubernetes ทำงานอย่างไรในบทที่ 1 น้องส้มมีความฝันใหม่ คืออยากเปิด **"ร้านอาหารแมวน้องส้ม"** บนเรือสินค้า ร้านนี้มีหน้าเว็บ (Next.js) และฐานข้อมูลเก็บสินค้ากับออเดอร์ (PostgreSQL) แต่กัปตันบอกว่า

> "ท่าเรือเราไม่รับตู้สินค้าเปล่า ๆ นะส้ม ทุกตู้ต้องถูก **ห่อในกล่อง Pod** พร้อม **ใบสั่งงาน YAML** ก่อน หอบังคับการถึงจะจัดขึ้นเรือให้"

บทนี้จึงเป็นการเรียนรู้ของน้องส้ม ตั้งแต่ "กล่อง Pod คืออะไร" ไปจนถึง "เขียนใบสั่งงานอย่างไรให้ร้านเปิดได้จริง" และใน LAB สุดท้าย น้องส้มจะเปิดร้านจริงใน Pod เดียว แล้วเจอบทเรียนสำคัญว่า "ถ้ากล่องหาย จะไม่มีใครสร้างคืนให้"

<p align="center" id="fig-2">
  <img src="images/02-harbor-metaphor-map.png" alt="รูปที่ 2 ทบทวนอุปมาท่าเรือ" width="900"><br>
  <em><b>รูปที่ 2</b> ทบทวนอุปมาท่าเรือจากบทที่ 1: ตู้สินค้า = container, กล่อง Pod ห่อตู้, เรือ = Node, หอบังคับการ = Control Plane</em>
</p>

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ตลอดบท

| Kubernetes | อุปมาท่าเรือ | ในคลัสเตอร์ LAB ของเรา |
|---|---|---|
| container | ตู้สินค้า (shipping container) | nginx, busybox, postgres, เว็บร้าน |
| **Pod** | กล่อง/ห้องโดยสารที่ห่อตู้สินค้า มี **ป้าย IP เดียว** | `web`, `som-shop` |
| Node | เรือ | `lab-worker`, `lab-worker2` |
| Control Plane | หอบังคับการบนท่า | `lab-control-plane` |
| kube-scheduler | เจ้าหน้าที่วางแผนว่ากล่องไหนขึ้นเรือลำไหน | อยู่ใน `lab-control-plane` |
| kubelet | ต้นเรือ (first mate) ประจำเรือแต่ละลำ | ทำงานในทุก node |
| image registry | โกดังต้นแบบตู้สินค้า | Docker Hub |
| emptyDir | ชั้นวางของร่วมในห้องโดยสาร (หายเมื่อห้องถูกรื้อ) | `db-data` ในร้านน้องส้ม |
| label | ป้ายแท็กห้อยกล่อง | `app=som-shop` |
| probe | เจ้าหน้าที่ตรวจสุขภาพ (หูฟังแพทย์) | `/api/health` |
| init container | ทีมเตรียมงานที่ต้องทำเสร็จก่อนเปิดร้าน | `wait-for-db`, `db-seed` |
| sidecar | ผู้ช่วยที่ทำงานคู่ตลอดเวลา | `db` (native sidecar) |

**สนามทดลองของบทนี้** (เตรียมใน LAB 0) ทุกอย่างอยู่ใน container เดียวบนเครื่องนักศึกษา

```text
เครื่องนักศึกษา (Docker Desktop)
 └─ container k8s-lab  ← สร้างจาก image tuchsanai/devtools-kind:2569_1, เข้าด้วย ssh -p 2223 root@localhost
     ├─ /workspace/DevTools/...  ← ไฟล์ LAB ที่ git clone มา (README, labs/*.yaml, som-shop/)
     └─ kind cluster "lab" (k8s-up)  ← node แต่ละตัวเป็น container ซ้อนใน Docker ของ k8s-lab
         ├─ lab-control-plane  (หอบังคับการ, มี taint ไม่รับ Pod ทั่วไป)
         ├─ lab-worker         (เรือ ← Pod ของเราอยู่ที่นี่)
         └─ lab-worker2        (เรือ ← Pod ของเราอยู่ที่นี่)
```

ไฟล์ YAML ของทุก LAB **เตรียมไว้ให้แล้ว** ในโฟลเดอร์ `labs/` นักศึกษาจะอ่านไฟล์ ทำความเข้าใจทีละ field แล้วสั่ง `kubectl apply -f` เนื้อหาหัวข้อ 7–10 ในเอกสารนี้จึงเน้นให้ **อ่าน YAML ออก** และแก้ได้เมื่อต้องการ

> **ขอบเขตของบทนี้:** เราจะสร้าง **Pod เดี่ยว ๆ** เท่านั้น เพื่อให้เห็นพฤติกรรมของ Pod ชัดที่สุด ทรัพยากรระดับสูงอย่าง Deployment, Service, PersistentVolumeClaim และ Secret จะกล่าวถึงเพื่อปูทางเท่านั้น และเป็น **เนื้อหาของบทถัดไป**

---

## 2. Pod คืออะไร

<p align="center" id="fig-3">
  <img src="images/03-what-is-a-pod.png" alt="รูปที่ 3 Pod คืออะไร" width="900"><br>
  <em><b>รูปที่ 3</b> Pod คือหน่วยเล็กที่สุดที่ Kubernetes deploy ได้ ห่อ container ตั้งแต่ 1 ตัวขึ้นไป มี IP เดียวและใช้ volume ร่วมกันได้</em>
</p>

**Pod** คือหน่วยที่เล็กที่สุดที่ Kubernetes สร้างและจัดการได้ (smallest deployable unit) Pod หนึ่งตัวห่อ container ไว้ **ตั้งแต่ 1 ตัวขึ้นไป** โดย container ทั้งหมดใน Pod เดียวกัน

- **ใช้ network namespace เดียวกัน** → มี IP เดียว และเรียกกันผ่าน `localhost` ได้
- **ใช้ volume ร่วมกันได้** → container หนึ่งเขียนไฟล์ อีก container อ่านได้
- **อยู่บน Node เดียวกันเสมอ** → ถูกจัดขึ้นเรือพร้อมกัน ลบพร้อมกัน
- **มีวงจรชีวิตร่วมกัน** → Pod ถูกสร้างครั้งเดียว และเมื่อถูกลบ container ทั้งหมดหายไปด้วย

สิ่งสำคัญที่มือใหม่มักเข้าใจผิดคือ **Kubernetes ไม่มีคำสั่งให้รัน container เดี่ยว ๆ** แม้เราจะพิมพ์ `kubectl run hello --image=nginx:1.27-alpine` ซึ่งดูเหมือนรัน container ตัวเดียว แต่สิ่งที่ถูกสร้างจริงคือ **Pod ชื่อ `hello` ที่มี container 1 ตัว** ดังผลจริงจาก LAB 1

```text
$ kubectl run hello --image=nginx:1.27-alpine
pod/hello created

$ kubectl get pods -o wide
NAME    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
hello   1/1     Running   0          6s    10.244.3.2   lab-worker2   <none>           <none>
```

คอลัมน์ `READY 1/1` หมายถึง "container ที่พร้อมแล้ว / container ทั้งหมดใน Pod" ส่วน `IP` คือป้าย IP ของกล่อง และ `NODE` คือเรือที่กล่องนี้อยู่

**ตารางที่ 2** container (Docker) เทียบกับ Pod (Kubernetes)

| ประเด็น | container ที่รันด้วย `docker run` | Pod ใน Kubernetes |
|---|---|---|
| หน่วยที่ระบบจัดการ | container ทีละตัว | Pod (ห่อ container ≥ 1 ตัว) |
| IP | container ละ IP | Pod ละ IP (container ภายในใช้ร่วมกัน) |
| ใครเลือกเครื่อง | ผู้ใช้เลือกเอง | kube-scheduler เลือก Node ให้ |
| ใครดูแลเมื่อ container ล้ม | `--restart` ของ Docker บนเครื่องนั้น | kubelet ตาม `restartPolicy` |
| วิธีสั่ง | คำสั่งยาวหลาย flag | ไฟล์ YAML (declarative) |

---

## 3. ทำไมต้องมี Pod ไม่ใช้ container ตรง ๆ

<p align="center" id="fig-4">
  <img src="images/04-why-pod-not-container.png" alt="รูปที่ 4 ทำไมต้องห่อ container ด้วย Pod" width="900"><br>
  <em><b>รูปที่ 4</b> container ที่ต้องทำงานใกล้ชิดกันถูกห่อไว้ใน Pod เดียว จึงถูกสร้าง ย้าย และลบไปพร้อมกัน</em>
</p>

บางงานต้องการ container หลายตัวที่ "อยู่ด้วยกัน ไปด้วยกัน" เช่น เว็บเซิร์ฟเวอร์กับตัวช่วยที่คอยอัปเดตไฟล์หน้าเว็บ ถ้าสองตัวนี้ไปอยู่คนละเครื่อง จะแชร์ไฟล์กันไม่ได้และต้องคุยผ่านเครือข่ายภายนอก Kubernetes จึงออกแบบ "กล่อง" ที่รับประกันว่า container ในกล่องเดียวกันจะ

1. ถูกวางบนเรือลำเดียวกันเสมอ
2. คุยกันผ่าน `localhost` ได้ทันที
3. แชร์ volume เดียวกันได้
4. เกิดและตายพร้อมกัน

นอกจากนี้ Pod ยังเป็นชั้นนามธรรมที่ทำให้ Kubernetes ไม่ผูกกับ container runtime ตัวใดตัวหนึ่ง (Docker, containerd, CRI-O) และเป็นที่รวมข้อมูลกำกับ เช่น labels, probes, resources

> **แนวปฏิบัติ:** โดยทั่วไป **1 Pod = 1 instance ของแอปหลัก 1 ตัว** ถ้าต้องการรองรับผู้ใช้มากขึ้น ให้เพิ่มจำนวน Pod (scale out) ไม่ใช่ยัด container แอปเดิมหลายตัวลง Pod เดียว container ตัวที่สองควรเป็น "ผู้ช่วย" ที่ผูกชะตากับแอปหลักจริง ๆ เท่านั้น (ดูหัวข้อ [15](#15-multi-container-pod))

---

## 4. Pod กับ Node

<p align="center" id="fig-5">
  <img src="images/05-pod-lives-on-one-node.png" alt="รูปที่ 5 Pod อยู่บน Node เดียวเสมอ" width="900"><br>
  <em><b>รูปที่ 5</b> kube-scheduler เลือกเรือให้ Pod ครั้งเดียว ทุก container ใน Pod อยู่บน Node เดียวกันเสมอ ไม่มีการแยกครึ่ง Pod ข้ามเรือ</em>
</p>

เมื่อ Pod ถูกสร้าง **kube-scheduler** จะเลือก Node ที่เหมาะสม **เพียงครั้งเดียว** และผูก Pod ไว้กับ Node นั้นตลอดอายุของ Pod ข้อควรรู้มีดังนี้

- **Pod ไม่ย้ายเรือ** ถ้า Node พังหรือ Pod ถูกลบ Pod ตัวนั้นจบชีวิต ถ้าต้องการ Pod ใหม่บน Node อื่น ต้องมีใคร "สร้าง Pod ใหม่" (ในบทนี้คือเราเอง บทหน้าคือ Deployment)
- **container ใน Pod ไม่แยก Node** ไม่มีกรณีที่ container A อยู่ `lab-worker` แต่ container B อยู่ `lab-worker2`
- **Node ของ Control Plane ไม่รับ Pod ทั่วไป** ในคลัสเตอร์ kind ของเรา `lab-control-plane` มี **taint** ติดไว้ (ผลจริงจาก LAB 0) Pod ของเราจึงไปอยู่ที่ `lab-worker` หรือ `lab-worker2` เท่านั้น

```text
$ kubectl describe node lab-control-plane | grep -i taints
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
```

taint เปรียบเหมือนป้าย "เรือลำนี้สำหรับหอบังคับการเท่านั้น" Pod ที่ไม่มี toleration ที่ตรงกันจะไม่ถูกจัดขึ้นเรือลำนี้ เราจะเห็นผลนี้อีกครั้งใน LAB 6 ตอนที่ Pod ขอ CPU มากเกินไป แล้ว scheduler รายงานว่า `1 node(s) had untolerated taint(s), 2 Insufficient cpu`

---

## 5. เครือข่ายของ Pod

### 5.1 หนึ่ง Pod หนึ่ง IP และ localhost ร่วม

<p align="center" id="fig-6">
  <img src="images/06-pod-shared-network-localhost.png" alt="รูปที่ 6 เครือข่ายร่วมภายใน Pod และ localhost" width="900"><br>
  <em><b>รูปที่ 6</b> container ใน Pod เดียวกันใช้ network namespace ร่วมกัน มี IP เดียว และคุยกันผ่าน localhost ได้ แต่ห้ามใช้ port ซ้ำกัน</em>
</p>

เมื่อ kubelet สร้าง Pod ขั้นแรกจะสร้าง **sandbox** ของ Pod (container เล็ก ๆ ที่เรียกว่า *pause container*) ซึ่งถือ network namespace ไว้ แล้ว container ทุกตัวใน Pod จะเข้าไปใช้ namespace นี้ร่วมกัน ผลที่ตามมาคือ

- ทุก container ใน Pod เห็น **IP เดียวกัน**
- container หนึ่งเรียกอีก container ได้ด้วย `localhost:<port>`
- **ห้ามมีสอง container ฟัง port เดียวกัน** ใน Pod เดียว (เหมือนสองโปรแกรมบนเครื่องเดียวแย่ง port กัน)

ผลจริงจาก LAB 8 ซึ่ง Pod มี container `web` (nginx) และ `helper` (busybox)

```text
$ kubectl exec shared-localhost-pod -c helper -- wget -qO- localhost:80 | grep -o "<title>.*</title>"
<title>Welcome to nginx!</title>

$ kubectl exec shared-localhost-pod -c helper -- hostname -i; kubectl exec shared-localhost-pod -c web -- hostname -i
10.244.3.12
10.244.3.12
```

container `helper` ไม่มีเว็บเซิร์ฟเวอร์ของตัวเอง แต่เรียก `localhost:80` แล้วได้หน้า nginx เพราะ nginx ใน container `web` ฟังอยู่ใน network namespace เดียวกัน

> **ข้อควรรู้: `localhost` อาจเป็น IPv4 หรือ IPv6** ไฟล์ `/etc/hosts` ใน container มีทั้ง `127.0.0.1 localhost` และ `::1 localhost` โปรแกรมบางตัว (เช่น `wget` ของ busybox) จะลอง `::1` ก่อน ถ้าแอปฟังเฉพาะ IPv4 (`0.0.0.0`) จะได้ `Connection refused` ทางแก้คือเรียก `127.0.0.1` ตรง ๆ เราจะเจอกรณีนี้จริงใน LAB 9

### 5.2 Pod-to-Pod ด้วย Pod IP

<p align="center" id="fig-7">
  <img src="images/07-pod-to-pod-ip.png" alt="รูปที่ 7 Pod-to-Pod ด้วย Pod IP" width="900"><br>
  <em><b>รูปที่ 7</b> แต่ละ Pod มี IP ของตัวเองบนเครือข่ายคลัสเตอร์ (CNI) Pod ต่างเรือคุยกันด้วย Pod IP ได้ แต่ IP จะเปลี่ยนเมื่อ Pod ถูกสร้างใหม่</em>
</p>

โมเดลเครือข่ายของ Kubernetes กำหนดว่า **ทุก Pod ต้องคุยกับทุก Pod ได้โดยตรงด้วย Pod IP โดยไม่ต้องทำ NAT** ไม่ว่าจะอยู่บน Node เดียวกันหรือไม่ งานนี้เป็นหน้าที่ของ **CNI plugin** (ในคลัสเตอร์ kind คือ `kindnet`) ซึ่งแจก IP จากช่วง `10.244.0.0/16` โดยแต่ละ Node ได้ช่วงย่อยของตัวเอง เช่น Pod บน `lab-worker` ได้ `10.244.1.x` และบน `lab-worker2` ได้ `10.244.3.x` (ค่าจริงจากการทดลอง เครื่องอื่นอาจต่างกัน)

ปัญหาคือ **Pod IP ไม่คงที่** เมื่อลบ Pod แล้วสร้างใหม่ (แม้ชื่อเดิม) จะได้ IP ใหม่ ผลจริงจาก LAB 9 เมื่อลบ Pod `som-shop` แล้ว apply ใหม่ IP เปลี่ยนจาก `10.244.3.15` เป็น `10.244.3.16` ดังนั้นการ hard-code Pod IP ในแอปจึงไม่ใช่ทางที่ถูก ปัญหานี้คือเหตุผลที่ Kubernetes มีทรัพยากรชื่อ **Service** ซึ่งให้ชื่อและที่อยู่คงที่ (เนื้อหาบทถัดไป)

---

## 6. เส้นทางการเกิดของ Pod

<p align="center" id="fig-8">
  <img src="images/08-pod-creation-journey.png" alt="รูปที่ 8 เส้นทางการเกิดของ Pod" width="900"><br>
  <em><b>รูปที่ 8</b> ลำดับเมื่อสั่ง kubectl apply: kube-apiserver บันทึกลง etcd, kube-scheduler เลือก Node, kubelet สั่ง container runtime ดึง image และเริ่ม container</em>
</p>

เมื่อน้องส้มยื่นใบสั่งงาน (`kubectl apply -f pod.yaml`) เกิดเหตุการณ์ตามลำดับดังนี้

1. **kubectl** อ่านไฟล์ YAML แปลงเป็น JSON แล้วส่ง HTTP request ไปที่ **kube-apiserver**
2. **kube-apiserver** ตรวจสิทธิ์ (authentication/authorization), ตรวจความถูกต้องของ object (validation, admission) แล้วบันทึกลง **etcd** ตอนนี้ Pod มีอยู่แล้วแต่ยังไม่มี Node (`Pending`)
3. **kube-scheduler** เห็น Pod ที่ยังไม่มี Node จึงกรอง Node ที่รับไม่ได้ (เช่น มี taint, CPU ไม่พอ) ให้คะแนน Node ที่เหลือ แล้วผูก Pod เข้ากับ Node ที่ดีที่สุด (event `Scheduled`)
4. **kubelet** บน Node นั้นเห็นว่ามี Pod ใหม่ของตน จึงสั่ง **container runtime** (containerd) ผ่าน CRI ให้สร้าง sandbox, ให้ CNI แจก IP, **ดึง image** (`Pulling` → `Pulled`), สร้าง container (`Created`) และเริ่ม container (`Started`)
5. kubelet รายงานสถานะกลับไปที่ kube-apiserver → Pod เป็น `Running`

ลำดับนี้มองเห็นได้จริงในส่วน **Events** ของ `kubectl describe pod` (ผลจริงจาก LAB 1 บน Kubernetes v1.37 ข้อความของ kubelet ขึ้นต้นด้วยชื่อ container เช่น `spec.containers{hello}:`)

```text
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  6s    default-scheduler  Successfully assigned default/hello to lab-worker2
  Normal  Pulling    6s    kubelet            spec.containers{hello}: Pulling image "nginx:1.27-alpine"
  Normal  Pulled     0s    kubelet            spec.containers{hello}: Successfully pulled image "nginx:1.27-alpine" in 5.905s (5.905s including waiting). Image size: 20984244 bytes.
  Normal  Created    0s    kubelet            spec.containers{hello}: Container created
  Normal  Started    0s    kubelet            spec.containers{hello}: Container started
```

> **เคล็ดลับดีบัก:** เมื่อ Pod ไม่ขึ้น ให้ดูว่า Events หยุดอยู่ที่ขั้นไหน ถ้าไม่มี `Scheduled` แปลว่าติดที่ scheduler (เช่น resources ไม่พอ) ถ้าติดที่ `Pulling` แปลว่าดึง image ไม่ได้ ถ้า `Started` แล้วแต่ล้ม แปลว่าปัญหาอยู่ที่ตัวแอป

---

## 7. พื้นฐาน YAML

ใบสั่งงานของ Kubernetes เขียนด้วย **YAML** (YAML Ain't Markup Language) ซึ่งเป็นรูปแบบข้อมูลที่อ่านง่ายสำหรับมนุษย์ ก่อนเขียน Pod จึงต้องเข้าใจไวยากรณ์ YAML ให้แม่นก่อน

### 7.1 ไวยากรณ์ที่ต้องรู้

<p align="center" id="fig-9">
  <img src="images/09-yaml-syntax-basics.png" alt="รูปที่ 9 ไวยากรณ์ YAML พื้นฐาน" width="900"><br>
  <em><b>รูปที่ 9</b> YAML ใช้ key: value, การเยื้องด้วยช่องว่างบอกลำดับชั้น และขีด - บอกรายการ (list)</em>
</p>

```yaml
# บรรทัดที่ขึ้นต้นด้วย # คือ comment
shop: ร้านอาหารแมวน้องส้ม        # key: value (ต้องมีช่องว่างหลัง :)
open: true                       # boolean
tables: 4                        # number
phone: "0812345678"              # string (ใส่ quote กันถูกตีความเป็นตัวเลข)
owner:                           # map ซ้อน: เยื้องเข้าไป 2 ช่องว่าง
  name: น้องส้ม
  role: ผู้ช่วยกัปตัน
menu:                            # list: แต่ละรายการขึ้นต้นด้วย "- "
  - ปลาทูน่า
  - ปลาซาบะ
staff:                           # list ของ map
  - name: ส้ม
    shift: เช้า
  - name: ดำ
    shift: บ่าย
welcome: |                       # block scalar: เก็บข้อความหลายบรรทัดตามจริง
  ยินดีต้อนรับสู่ร้าน
  เปิดทุกวัน 9 โมง
---
# --- คั่นเอกสาร YAML หลายชิ้นในไฟล์เดียว (ใช้สร้างหลาย Pod ในไฟล์เดียวได้)
shop: ร้านของเล่น
```

**ตารางที่ 3** สรุปไวยากรณ์ YAML ที่ใช้บ่อยใน Kubernetes

| ไวยากรณ์ | ความหมาย | ตัวอย่างใน Kubernetes |
|---|---|---|
| `key: value` | คู่ข้อมูล (ต้องมีช่องว่างหลัง `:`) | `kind: Pod` |
| การเยื้อง | บอกลำดับชั้น **ใช้ช่องว่างเท่านั้น** นิยม 2 ช่อง | `metadata:` → `  name: web` |
| `- ` | รายการใน list | `containers:` → `  - name: nginx` |
| `"..."` | บังคับให้เป็น string | `value: "5432"` |
| `#` | comment | `# LAB 2` |
| `---` | คั่นหลายเอกสาร (หลาย object) | `shop-pods.yaml` ใน LAB 4 |
| `\|` | ข้อความหลายบรรทัด เก็บการขึ้นบรรทัดใหม่ | สคริปต์ใน `command` ของ init container |
| `[a, b]` | list แบบบรรทัดเดียว (flow style) | `command: ["sh", "-c", "sleep 3600"]` |
| `{k: v}` | map แบบบรรทัดเดียว | `requests: { cpu: 100m, memory: 256Mi }` |

### 7.2 ข้อผิดพลาดยอดฮิต

<p align="center" id="fig-10">
  <img src="images/10-yaml-common-mistakes.png" alt="รูปที่ 10 ข้อผิดพลาด YAML ที่พบบ่อย" width="900"><br>
  <em><b>รูปที่ 10</b> ข้อผิดพลาดที่พบบ่อย: ใช้ Tab แทนช่องว่าง, ลืมเว้นวรรคหลังเครื่องหมาย :, และเยื้องผิดระดับ</em>
</p>

**ตารางที่ 4** ข้อผิดพลาด YAML ที่เจอบ่อยและวิธีแก้

| ข้อผิดพลาด | ตัวอย่างที่ผิด | ที่ถูก |
|---|---|---|
| ใช้ Tab เยื้อง | `metadata:` ↵ `⇥name: web` | ใช้ช่องว่าง 2 ช่อง (ตั้ง editor ให้แปลง Tab เป็น space) |
| ลืมเว้นวรรคหลัง `:` | `name:web` | `name: web` |
| เยื้องผิดระดับ | `image` เยื้องไม่ตรงกับ `name` ใน container เดียวกัน | key ในระดับเดียวกันต้องเยื้องเท่ากันพอดี |
| ลืม `-` หน้ารายการ | `containers:` ↵ `  name: nginx` | `containers:` ↵ `  - name: nginx` |
| ตัวเลขที่ต้องเป็น string | `value: 9` ใน `env` | `value: "9"` |
| ค่าที่ดูเหมือน boolean | `value: yes` หรือ `on` | `value: "yes"` |
| พิมพ์ชื่อ field ผิดตัวพิมพ์ | `containerport: 80` | `containerPort: 80` (field เป็น camelCase) |

ตัวอย่างข้อผิดพลาดจริงจาก LAB 6 เมื่อลบ quote ของ `value: "9"` ใน `env` ออก kube-apiserver ปฏิเสธทันที เพราะ `env.value` ต้องเป็น string

```text
Error from server (BadRequest): error when creating "STDIN": Pod in version "v1" cannot be handled as a Pod: json: cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string
```

> **ข้อควรจำ:** YAML ที่ "ถูกไวยากรณ์" ยังอาจ "ผิดความหมาย" สำหรับ Kubernetes ได้ ไม่ต้องกลัว เพราะ kube-apiserver ตรวจทุกไฟล์ตอน `kubectl apply` อยู่แล้ว ถ้าผิดจะปฏิเสธพร้อมบอกชื่อ field ที่ผิด (เช่น `EnvVar.spec.containers.env.value`) และไม่สร้างอะไรเลย ให้อ่านข้อความ error แล้วแก้ไฟล์ตามนั้น

---

## 8. โครงสร้าง Kubernetes Manifest

### 8.1 สี่ส่วนหลัก

<p align="center" id="fig-11">
  <img src="images/11-manifest-four-parts.png" alt="รูปที่ 11 Manifest สี่ส่วน" width="900"><br>
  <em><b>รูปที่ 11</b> Pod manifest มี 4 ส่วนหลัก: apiVersion, kind, metadata และ spec</em>
</p>

ไฟล์ที่บรรยาย object ของ Kubernetes เรียกว่า **manifest** ทุก manifest มีสี่ส่วนหลัก ตัวอย่างนี้คือไฟล์จริง `02_LAB/labs/lab02-first-yaml/nginx-pod.yaml`

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

**ตารางที่ 5** หน้าที่ของสี่ส่วนหลัก

| ส่วน | หน้าที่ | ค่าสำหรับ Pod | อุปมา |
|---|---|---|---|
| `apiVersion` | กลุ่มและเวอร์ชันของ API | `v1` (กลุ่ม core) | แบบฟอร์มฉบับไหน |
| `kind` | ชนิดของ object | `Pod` | ใบสั่งงานประเภทไหน |
| `metadata` | ตัวตนของ object: `name`, `namespace`, `labels`, `annotations` | `name: web` | ชื่อและป้ายแท็กบนกล่อง |
| `spec` | สิ่งที่ต้องการ (desired state) | `containers`, `volumes`, `restartPolicy` ... | รายละเอียดสิ่งที่อยู่ในกล่อง |

ข้อกำหนดสำคัญของ `metadata.name` คือใช้ **ตัวพิมพ์เล็ก ตัวเลข และ `-`** (ขึ้นต้นและลงท้ายด้วยตัวอักษรหรือตัวเลข) เช่น `som-shop`, `web-1` ห้ามใช้ตัวพิมพ์ใหญ่หรือช่องว่าง ถ้าไม่ระบุ `namespace` Pod จะอยู่ใน namespace `default`

> ใช้ `kubectl api-resources` ดูว่าแต่ละ kind ใช้ `apiVersion` อะไร เช่น Pod ใช้ `v1` แต่ Deployment (บทหน้า) ใช้ `apps/v1`

### 8.2 spec กับ status

<p align="center" id="fig-12">
  <img src="images/12-spec-vs-status.png" alt="รูปที่ 12 spec กับ status" width="900"><br>
  <em><b>รูปที่ 12</b> spec คือสิ่งที่เราต้องการ (desired state) ส่วน status คือสภาพจริงที่ระบบเขียนรายงานกลับมา</em>
</p>

เราเขียนเฉพาะ `spec` ส่วน `status` เป็นหน้าที่ของระบบ (kubelet และ controller) ที่จะเขียนรายงานกลับมา ดูทั้งสองส่วนได้ด้วย `kubectl get pod <ชื่อ> -o yaml` ผลจริงจาก LAB 2 (กรองเฉพาะบรรทัดสำคัญพร้อมเลขบรรทัด)

```text
$ kubectl get pod web -o yaml | grep -nE "^(apiVersion|kind|metadata|spec|status):|podIP:|phase:|qosClass:|  - containerPort"
1:apiVersion: v1
2:kind: Pod
3:metadata:
16:spec:
22:    - containerPort: 80
70:status:
135:  phase: Running
136:  podIP: 10.244.1.2
139:  qosClass: BestEffort
```

สังเกตว่าไฟล์ที่เราเขียนมีแค่ประมาณ 15 บรรทัด แต่ object จริงยาวกว่า 130 บรรทัด เพราะระบบเติม **ค่าเริ่มต้น (defaults)** ใน `spec` เช่น `imagePullPolicy`, `restartPolicy`, `dnsPolicy` และเขียน `status` เช่น `phase`, `podIP`, `qosClass`, `containerStatuses` ให้ ดึงค่าเฉพาะจุดได้ด้วย `jsonpath`

```text
$ kubectl get pod web -o jsonpath="{.status.phase} {.status.podIP}{\"\\n\"}"
Running 10.244.1.2
```

---

## 9. เขียน spec ของ container

`spec.containers` เป็น list ของ container แต่ละตัวมี field สำคัญดังต่อไปนี้

### 9.1 name, image, imagePullPolicy และ ports

<p align="center" id="fig-13">
  <img src="images/13-container-image-ports.png" alt="รูปที่ 13 image, tag และ containerPort" width="900"><br>
  <em><b>รูปที่ 13</b> ระบุ image พร้อม tag เสมอ และ containerPort เป็นเพียงข้อมูลบอกว่า container ฟังพอร์ตใด ไม่ได้เปิดพอร์ตออกนอกคลัสเตอร์</em>
</p>

```yaml
containers:
  - name: nginx                    # ชื่อ container (ไม่ซ้ำกันใน Pod) ใช้กับ -c ในคำสั่ง logs/exec
    image: nginx:1.27-alpine       # <ชื่อ image>:<tag>
    imagePullPolicy: IfNotPresent  # มีอยู่บน node แล้วไม่ต้องดึงใหม่
    ports:
      - containerPort: 80
        name: http                 # ตั้งชื่อ port ได้ (ไม่บังคับ)
```

- **`image` ระบุ tag เสมอ** เช่น `nginx:1.27-alpine`, `busybox:1.36`, `postgres:17.11-alpine` หลีกเลี่ยง `latest` หรือไม่ใส่ tag เพราะวันนี้กับพรุ่งนี้อาจได้ image ต่างกัน ทำให้ผลลัพธ์ไม่คงที่
- **`imagePullPolicy`** มีสามค่า

**ตารางที่ 6** ค่า imagePullPolicy

| ค่า | พฤติกรรม | ค่าเริ่มต้นเมื่อ |
|---|---|---|
| `IfNotPresent` | ดึงจาก registry เฉพาะเมื่อ node ยังไม่มี image นี้ | ระบุ tag ที่ไม่ใช่ `latest` |
| `Always` | ถาม registry ทุกครั้งที่เริ่ม container | tag เป็น `latest` หรือไม่ระบุ tag |
| `Never` | ไม่ดึงเลย ใช้เฉพาะ image ที่อยู่บน node | ต้องตั้งเอง |

  image ที่ build เองในเครื่อง (เช่น `som-shop-web:1.0` ใน LAB 9) ไม่ได้อยู่ใน Docker Hub ต้องนำเข้า node ด้วย `kind load docker-image` แล้วใช้ `IfNotPresent` (หรือ `Never`) มิฉะนั้น node จะพยายามดึงจากอินเทอร์เน็ตและล้มเหลว

- **`ports.containerPort` เป็นข้อมูลประกอบ (documentation)** ไม่ได้เปิดหรือปิด port ใด ๆ แอปที่ฟัง port อยู่จะเข้าถึงได้จาก Pod IP เสมอแม้ไม่ได้ประกาศ ดังที่ `kubectl explain` อธิบายไว้ (ผลจริงจากคลัสเตอร์ kind ของ LAB)

```text
$ kubectl explain pod.spec.containers.ports | head -30
...
DESCRIPTION:
    List of ports to expose from the container. Not specifying a port here DOES
    NOT prevent that port from being exposed. Any port which is listening on the
    default "0.0.0.0" address inside a container will be accessible from the
    network. ...
```

  ถึงอย่างนั้นก็ควรประกาศไว้เสมอ เพราะช่วยให้คนอ่านรู้ว่าแอปฟัง port อะไร และทรัพยากรอื่นอ้างอิงชื่อ port ได้

### 9.2 env: ส่งค่าตั้งค่าเข้า container

<p align="center" id="fig-14">
  <img src="images/14-env-variables.png" alt="รูปที่ 14 ตัวแปร env" width="900"><br>
  <em><b>รูปที่ 14</b> env ส่งค่าตั้งค่าเข้า container เป็นคู่ name/value โดย value ต้องเป็นข้อความ (string)</em>
</p>

แอปที่ดีไม่ควร hard-code ค่าตั้งค่าไว้ใน image แต่รับจาก **environment variables** (แนวคิด Twelve-Factor App) ใน Pod กำหนดได้ด้วย `env`

```yaml
env:
  - name: SHOP_NAME
    value: "ร้านอาหารแมวน้องส้ม"
  - name: OPEN_HOUR
    value: "9"            # ตัวเลขต้องใส่ "" ให้เป็น string
  - name: DATABASE_URL
    value: postgres://som:meow1234@localhost:5432/catshop
```

ผลจริงจาก LAB 6 (`env-command-pod.yaml`)

```text
$ kubectl exec env-command-pod -- env | grep -E "SHOP_NAME|OPEN_HOUR|HOSTNAME"
HOSTNAME=env-command-pod
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9
```

สังเกตว่า `HOSTNAME` ของ container มีค่าเป็น **ชื่อ Pod** โดยอัตโนมัติ

> ⚠️ **ความปลอดภัย:** รหัสผ่านฐานข้อมูล `meow1234` ที่ใส่ใน `env` ตรง ๆ ในบทนี้ใช้ **เพื่อการเรียนเท่านั้น** เพราะใครที่อ่าน YAML หรือรัน `kubectl get pod -o yaml` ได้ก็เห็นรหัสผ่าน งานจริงต้องเก็บใน **Secret** แล้วอ้างอิงด้วย `valueFrom.secretKeyRef` (บทถัดไป)

### 9.3 command และ args

<p align="center" id="fig-15">
  <img src="images/15-command-args-override.png" alt="รูปที่ 15 command/args ทับ ENTRYPOINT/CMD" width="900"><br>
  <em><b>รูปที่ 15</b> command ใน Pod ทับ ENTRYPOINT และ args ทับ CMD ของ image</em>
</p>

ทุก image มีคำสั่งเริ่มต้นที่กำหนดไว้ใน Dockerfile ด้วย `ENTRYPOINT` และ `CMD` ใน Pod เราสามารถทับได้ด้วย `command` และ `args`

**ตารางที่ 7** ผลของการกำหนด command/args

| `command` ใน Pod | `args` ใน Pod | สิ่งที่รันจริง |
|---|---|---|
| ไม่กำหนด | ไม่กำหนด | `ENTRYPOINT` + `CMD` ของ image (ตามที่ image ตั้งไว้) |
| กำหนด | ไม่กำหนด | `command` เท่านั้น (ทั้ง `ENTRYPOINT` และ `CMD` ของ image ถูกละทิ้ง) |
| ไม่กำหนด | กำหนด | `ENTRYPOINT` ของ image + `args` |
| กำหนด | กำหนด | `command` + `args` |

ตัวอย่างจาก `env-command-pod.yaml` ใน LAB 6

```yaml
command: ["sh", "-c"]             # ทับ ENTRYPOINT ของ image
args:                             # ทับ CMD ของ image
  - echo "SHOP_NAME=$SHOP_NAME"; echo "OPEN_HOUR=$OPEN_HOUR"; sleep 3600
```

```text
$ kubectl logs env-command-pod
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9
```

> **ข้อควรจำ:** `command` และ `args` เป็น **list ของ string** ไม่ได้ผ่าน shell โดยอัตโนมัติ ถ้าต้องการใช้ `;`, `&&`, `$VAR` หรือ redirect ต้องเรียกผ่าน `sh -c` เหมือนตัวอย่าง และ container ต้องมีโปรแกรม `sh` อยู่ด้วย

### 9.4 resources: requests และ limits

<p align="center" id="fig-16">
  <img src="images/16-resources-requests-limits.png" alt="รูปที่ 16 requests และ limits" width="900"><br>
  <em><b>รูปที่ 16</b> requests ใช้ตอนเลือก Node (จองที่) ส่วน limits คือเพดานจริง ใช้ memory เกิน limit จะถูก OOMKilled ส่วน CPU จะถูกชะลอ</em>
</p>

```yaml
resources:
  requests:            # "ขอจองที่" ใช้ตอน scheduler เลือก Node
    cpu: "50m"         # 50 millicore = 0.05 core
    memory: "32Mi"
  limits:              # "เพดาน" ขณะรันจริง
    cpu: "100m"
    memory: "64Mi"
```

- **requests** คือปริมาณที่ "จอง" ไว้ kube-scheduler จะวาง Pod บน Node ที่ยังมีที่ว่างพอสำหรับ requests เท่านั้น ถ้าไม่มี Node ไหนพอ Pod จะค้าง `Pending` พร้อม event `FailedScheduling`
- **limits** คือเพดานที่บังคับใช้จริงขณะรัน
  - **CPU เกิน limit** → ถูกชะลอ (throttle) โปรแกรมช้าลงแต่ไม่ตาย
  - **memory เกิน limit** → kernel ฆ่า process ทันที เรียกว่า **OOMKilled** (exit code 137) แล้ว kubelet restart container ตาม `restartPolicy`

**ตารางที่ 8** หน่วยของ resources

| ทรัพยากร | หน่วย | ตัวอย่าง |
|---|---|---|
| CPU | core หรือ millicore (`m`) โดย 1 core = `1000m` | `"0.5"` = `"500m"`, `"64"` = 64 core |
| memory | byte แบบฐาน 2: `Ki`, `Mi`, `Gi` หรือฐาน 10: `k`, `M`, `G` | `64Mi` = 64 × 1024 × 1024 byte |

> ⚠️ **กับดักตัวพิมพ์:** memory `128m` แปลว่า 0.128 **byte** (m ตัวเล็ก = milli) ไม่ใช่ 128 เมกะไบต์ ต้องเขียน `128Mi`

ผลจริงจาก LAB 6 เมื่อ container ใช้ memory เกิน limit 32Mi และเมื่อ Pod ขอ CPU 64 core

```text
$ kubectl describe pod oom-pod | sed -n "/^    State:/,/^    Restart Count/p"
    State:          Terminated
      Reason:       OOMKilled
      Exit Code:    137
...
    Restart Count:  2

$ kubectl describe pod pending-pod | sed -n "/^Events:/,\$p"
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  31s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

จาก requests และ limits Kubernetes จัด Pod เป็น **QoS class** ซึ่งใช้ตัดสินว่าจะไล่ Pod ใดออกก่อนเมื่อ Node ขาด memory

**ตารางที่ 9** QoS class

| QoS class | เงื่อนไข | ลำดับการถูกไล่ออกเมื่อ Node ขาดทรัพยากร |
|---|---|---|
| `Guaranteed` | ทุก container กำหนด requests = limits ทั้ง CPU และ memory | ถูกไล่ออกเป็นลำดับสุดท้าย |
| `Burstable` | มีอย่างน้อยหนึ่ง container กำหนด requests หรือ limits แต่ไม่เข้าเงื่อนไข Guaranteed | ลำดับกลาง |
| `BestEffort` | ไม่กำหนด requests/limits เลย | ถูกไล่ออกก่อน |

ใน LAB เราเห็นจริงว่า Pod `web` ที่ไม่มี resources เป็น `BestEffort` ส่วน `env-command-pod` (requests < limits) เป็น `Burstable`

---

## 10. Labels, Selectors และ Annotations

<p align="center" id="fig-17">
  <img src="images/17-labels-selectors.png" alt="รูปที่ 17 Labels และ Selectors" width="900"><br>
  <em><b>รูปที่ 17</b> labels คือป้ายแท็กคู่ key=value ที่ติดกับ Pod และใช้ selector -l ค้นหากลุ่ม Pod ได้</em>
</p>

**Labels** คือป้ายแท็ก `key=value` ที่ติดกับ object เพื่อจัดกลุ่มและค้นหา เช่น `app=som-shop`, `tier=web`, `env=dev` labels เป็นกลไกหลักที่ทรัพยากรอื่นใช้ "เลือก" Pod (เช่น Deployment และ Service ในบทหน้า เลือก Pod จาก labels ไม่ใช่จากชื่อ)

```yaml
metadata:
  name: shop-web
  labels:
    app: som-shop     # ร้านของน้องส้ม
    tier: web         # ชั้นหน้าเว็บ
  annotations:
    description: "หน้าร้านทดลอง"
```

กฎการตั้งชื่อ label โดยย่อ: key และ value ยาวไม่เกิน 63 ตัวอักษร ใช้ตัวอักษรอังกฤษ ตัวเลข `-`, `_`, `.` และต้องขึ้นต้น/ลงท้ายด้วยตัวอักษรหรือตัวเลข key อาจมี prefix แบบโดเมน เช่น `app.kubernetes.io/name`

**ตารางที่ 10** รูปแบบ selector ที่ใช้บ่อย

| รูปแบบ | ความหมาย | ตัวอย่าง |
|---|---|---|
| equality | เท่ากับ / ไม่เท่ากับ | `-l app=som-shop`, `-l app!=som-shop` |
| AND หลายเงื่อนไข | คั่นด้วย `,` | `-l app=som-shop,tier=web` |
| set-based | อยู่ใน / ไม่อยู่ในชุด | `-l 'tier in (web,cache)'`, `-l 'env notin (prod)'` |
| exists | มี key นี้ / ไม่มี | `-l env`, `-l '!env'` |

ผลจริงจาก LAB 4

```text
$ kubectl get pods --show-labels
NAME         READY   STATUS    RESTARTS   AGE   LABELS
shop-cache   1/1     Running   0          6s    app=som-shop,tier=cache
shop-web     1/1     Running   0          6s    app=som-shop,tier=web
toy-web      1/1     Running   0          6s    app=toy-shop,tier=web

$ kubectl get pods -l app=som-shop,tier=web
NAME       READY   STATUS    RESTARTS   AGE
shop-web   1/1     Running   0          6s
```

คำสั่งจัดการ label: `kubectl label pod toy-web env=dev` (เพิ่ม), `--overwrite` (แก้ค่าที่มีอยู่), `kubectl label pod toy-web env-` (ลบ ด้วยการเติม `-` ท้าย key), `kubectl get pods -L app,tier` (แสดง label เป็นคอลัมน์)

**Annotations** ก็เป็น key/value เหมือนกัน แต่ **ใช้เก็บข้อมูลประกอบ ไม่ได้ใช้ค้นหา/เลือก** เช่น ผู้ดูแล คำอธิบาย ลิงก์เอกสาร และค่าเป็นข้อความยาวหรือภาษาไทยได้

**ตารางที่ 11** labels เทียบกับ annotations

| | labels | annotations |
|---|---|---|
| ใช้ทำอะไร | จัดกลุ่ม เลือก ค้นหา (`-l`) | ข้อมูลประกอบสำหรับคนหรือเครื่องมือ |
| ข้อจำกัดของค่า | สั้น ≤ 63 ตัวอักษร ชุดอักขระจำกัด | ยาวได้ ใส่ข้อความอิสระได้ |
| ตัวอย่าง | `app=som-shop` | `owner: น้องส้ม` |

---

## 11. สร้างและลบ Pod จากไฟล์ YAML

เมื่อมีไฟล์ YAML แล้ว (ใน LAB เตรียมไว้ให้ในโฟลเดอร์ `labs/`) คำสั่งที่ใช้กับไฟล์มีสามตัวหลัก คือ `kubectl apply -f`, `kubectl create -f` และ `kubectl delete -f`

**ตารางที่ 12** `kubectl apply` เทียบกับ `kubectl create`

| | `kubectl apply -f` | `kubectl create -f` |
|---|---|---|
| แนวคิด | declarative: "ทำให้เป็นแบบในไฟล์" | imperative: "สร้างใหม่" |
| ยังไม่มี object | สร้างให้ (`created`) | สร้างให้ (`created`) |
| มีแล้วและไฟล์ไม่เปลี่ยน | `unchanged` | error `AlreadyExists` |
| มีแล้วและไฟล์เปลี่ยน | พยายามอัปเดต (`configured`) | error `AlreadyExists` |

ผลจริงจาก LAB 2 (สั่ง `apply` ครั้งแรกได้ `pod/web created` จากนั้นสั่งซ้ำ)

```text
$ kubectl apply -f labs/lab02-first-yaml/nginx-pod.yaml
pod/web unchanged

$ kubectl create -f labs/lab02-first-yaml/nginx-pod.yaml
Error from server (AlreadyExists): error when creating "labs/lab02-first-yaml/nginx-pod.yaml": pods "web" already exists
```

ลบด้วยไฟล์เดียวกันได้ด้วย `kubectl delete -f <ไฟล์>` หรือลบทุกไฟล์ในโฟลเดอร์ด้วย `kubectl delete -f labs/lab05-lifecycle/` (ใช้ทั้งโฟลเดอร์กับ `apply -f` ได้เช่นกัน)

> **ทำไมใน LAB ใช้ `apply` เป็นหลัก:** สั่งซ้ำกี่ครั้งก็ได้ผลเหมือนเดิม (ไม่ error) และเป็นรูปแบบเดียวกับที่ใช้กับ Deployment/Service ในบทถัดไป ส่วน `create` ใช้ใน LAB 2 เพื่อให้เห็นความต่างเท่านั้น

### 11.1 เครื่องมือเสริมเมื่อต้องเขียนไฟล์เอง (ไม่ได้ใช้ใน LAB)

<p align="center" id="fig-18">
  <img src="images/18-kubectl-explain-dry-run.png" alt="รูปที่ 18 kubectl explain และ --dry-run" width="900"><br>
  <em><b>รูปที่ 18</b> เครื่องมือเสริม: kubectl explain เป็นคู่มือ field ของ YAML และ --dry-run=client -o yaml ช่วยร่างไฟล์ Pod โดยยังไม่สร้างจริง</em>
</p>

ถ้าวันหนึ่งต้องเขียน YAML ขึ้นใหม่เอง มีสองเครื่องมือช่วย

- **`kubectl run <ชื่อ> --image=<image> --dry-run=client -o yaml > pod.yaml`** พิมพ์ YAML ตั้งต้นออกมา (ไม่สร้าง Pod จริง) แล้วนำไปแก้ต่อ
- **`kubectl explain <path>`** เปิดคู่มือของ field เช่น `kubectl explain pod.spec.containers` หรือ `kubectl explain pod.spec.containers.livenessProbe`

---

## 12. วงจรชีวิตของ Pod

### 12.1 Pod phase

<p align="center" id="fig-19">
  <img src="images/19-pod-phases.png" alt="รูปที่ 19 Pod phase ทั้ง 5 ค่า" width="900"><br>
  <em><b>รูปที่ 19</b> Pod phase มี 5 ค่า: Pending, Running, Succeeded, Failed และ Unknown</em>
</p>

**phase** คือสรุปสถานะระดับ Pod อยู่ใน `status.phase` มีเพียง 5 ค่า

**ตารางที่ 13** Pod phase

| phase | ความหมาย | ตัวอย่างใน LAB |
|---|---|---|
| `Pending` | ระบบรับ Pod แล้วแต่ container ยังไม่พร้อมรัน: ยังไม่ได้ Node, กำลังดึง image หรือ init container ยังไม่เสร็จ | `pending-pod` (CPU ไม่พอ), `bad-image-pod` |
| `Running` | ได้ Node แล้วและมี container อย่างน้อย 1 ตัวกำลังรัน (หรือกำลัง restart) | `web`, `crash-pod` |
| `Succeeded` | container ทุกตัวจบด้วย exit 0 และจะไม่ restart อีก | `completed-pod` |
| `Failed` | container ทุกตัวจบแล้ว และอย่างน้อย 1 ตัวจบด้วยความล้มเหลว (และไม่ restart) | Pod ที่ `restartPolicy: Never` แล้ว exit 1 |
| `Unknown` | ระบบติดต่อ Node ไม่ได้ จึงไม่รู้สถานะ | Node ล่ม/เครือข่ายขาด |

> **ข้อควรจำ:** คอลัมน์ **STATUS** ใน `kubectl get pods` **ไม่ใช่ phase** เสมอไป kubectl เลือกแสดงข้อมูลที่ "มีประโยชน์ที่สุด" ซึ่งมักเป็นเหตุผลของ container เช่น `ContainerCreating`, `CrashLoopBackOff`, `Completed`

ตัวอย่างจริงจาก LAB 5: `crash-pod` แสดง STATUS เป็น `Error` หรือ `CrashLoopBackOff` แต่ phase จริงคือ `Running`

```text
$ kubectl get pod crash-pod -o jsonpath="phase={.status.phase}{\"\\n\"}"
phase=Running
```

**ตารางที่ 14** ค่า STATUS ที่พบบ่อยและความหมาย

| STATUS ที่เห็น | phase จริง | ความหมาย |
|---|---|---|
| `Pending` | Pending | ยังไม่ได้ Node (ดู Events หา `FailedScheduling`) |
| `ContainerCreating` | Pending | ได้ Node แล้ว กำลังดึง image/สร้าง container |
| `Init:1/3` | Pending | init container เสร็จ 1 จาก 3 ตัว |
| `PodInitializing` | Pending | init เสร็จหมดแล้ว กำลังเริ่ม app container |
| `Running` | Running | container หลักกำลังทำงาน |
| `Completed` | Succeeded | ทำงานเสร็จด้วย exit 0 |
| `Error` | Running หรือ Failed | container จบด้วย exit code ≠ 0 |
| `CrashLoopBackOff` | Running | ล้มซ้ำ ๆ kubelet กำลังรอก่อน restart รอบถัดไป |
| `ErrImagePull` / `ImagePullBackOff` | Pending | ดึง image ไม่ได้ |
| `OOMKilled` | Running | container ถูกฆ่าเพราะใช้ memory เกิน limit |
| `Terminating` | (ค่าเดิม) | กำลังถูกลบ รอ container ปิดตัว |

### 12.2 Container state และ restartPolicy

<p align="center" id="fig-20">
  <img src="images/20-container-states-restartpolicy.png" alt="รูปที่ 20 Container state และ restartPolicy" width="900"><br>
  <em><b>รูปที่ 20</b> container มีสถานะ Waiting, Running, Terminated และ restartPolicy (Always, OnFailure, Never) กำหนดว่า kubelet จะ restart container ใน Pod เดิมหรือไม่</em>
</p>

นอกจาก phase ของ Pod แล้ว **container แต่ละตัว** มี state ของตัวเอง 3 แบบ คือ `Waiting` (รอ เช่น กำลังดึง image หรือรอ back-off), `Running` และ `Terminated` (จบแล้ว พร้อม `reason` และ `exitCode`) ดูได้ใน `kubectl describe pod` ช่อง `State` และ `Last State`

**`restartPolicy`** กำหนดที่ระดับ Pod (ใช้กับทุก container ใน `containers`) ว่าเมื่อ container จบการทำงาน kubelet จะทำอะไร

**ตารางที่ 15** restartPolicy

| ค่า | exit 0 | exit ≠ 0 | เหมาะกับ |
|---|---|---|---|
| `Always` (ค่าเริ่มต้น) | restart | restart | เว็บ/บริการที่ต้องรันตลอด |
| `OnFailure` | ไม่ restart → `Completed` | restart | งานที่ต้องทำให้สำเร็จ |
| `Never` | ไม่ restart → `Completed` | ไม่ restart → `Error` | งานครั้งเดียว ต้องการเก็บผลล้มเหลวไว้ดู |

สิ่งที่ต้องเข้าใจให้ตรงคือ **kubelet restart container ภายใน Pod เดิม** (Pod ชื่อเดิม IP เดิม Node เดิม) และนับใน **RESTARTS** ไม่ได้สร้าง Pod ใหม่ ผลจริงจาก LAB 5 ที่ประมาณวินาทีที่ 20

```text
NAME            READY   STATUS             RESTARTS      AGE
bad-image-pod   0/1     ImagePullBackOff   0             24s
completed-pod   0/1     Completed          0             24s
crash-pod       1/1     Running            2 (16s ago)   24s
onfailure-pod   0/1     Completed          1 (17s ago)   24s
```

`onfailure-pod` ล้มรอบแรก (exit 1) จึงถูก restart 1 ครั้ง แล้วสำเร็จรอบสองจึงจบที่ `Completed` ส่วน `crash-pod` ที่ล้มทุกรอบภายใต้ `Always` จะถูก restart ไปเรื่อย ๆ

### 12.3 CrashLoopBackOff

<p align="center" id="fig-21">
  <img src="images/21-crashloopbackoff.png" alt="รูปที่ 21 CrashLoopBackOff" width="900"><br>
  <em><b>รูปที่ 21</b> container ล้มซ้ำ ๆ kubelet จะ restart โดยรอนานขึ้นเรื่อย ๆ 10 วินาที, 20, 40 ... สูงสุด 5 นาที เรียกว่า CrashLoopBackOff</em>
</p>

เมื่อ container ล้มซ้ำ ๆ kubelet ไม่ restart ทันทีทุกครั้ง แต่ **รอนานขึ้นแบบทวีคูณ (exponential back-off)** 10 วินาที → 20 → 40 → ... สูงสุด 5 นาที ช่วงที่รออยู่ STATUS จะแสดง `CrashLoopBackOff` ถ้า container รันได้นานพอ (10 นาที) โดยไม่ล้ม ตัวนับ back-off จะเริ่มใหม่

ผลจริงจาก LAB 5 เมื่อผ่านไปราว 7 นาที เห็นว่ารอบรอขยายไปถึงเพดาน 5 นาทีแล้ว

```text
$ kubectl get pod crash-pod -o jsonpath="{.status.containerStatuses[0].state.waiting}{\"\\n\"}"
{"message":"back-off 5m0s restarting failed container=app pod=crash-pod_default(6d6ccac7-645d-4901-bc5f-eff032deb1ef)","reason":"CrashLoopBackOff"}
```

**วิธีหาสาเหตุ** สิ่งที่ต้องดูคือ log ของ container รอบที่ล้ม ใช้ `kubectl logs <pod> --previous` และดู `Last State` / `Exit Code` ใน `kubectl describe`

```text
$ kubectl logs crash-pod --previous
กำลังเปิดร้าน...
ERROR: หาไฟล์เมนูไม่เจอ
```

> **หมายเหตุจากการทดลองจริง (K8s 1.37):** STATUS ของ Pod ที่ล้มซ้ำจะสลับระหว่าง `Running` → `Error` → `CrashLoopBackOff` และมักเห็น `Error` บ่อยกว่า สิ่งที่บอกว่าเป็น crash loop จริงคือ **RESTARTS ที่เพิ่มขึ้นเรื่อย ๆ** และ Events `BackOff  Back-off restarting failed container`

### 12.4 ErrImagePull และ ImagePullBackOff

<p align="center" id="fig-22">
  <img src="images/22-imagepullbackoff.png" alt="รูปที่ 22 ErrImagePull / ImagePullBackOff" width="900"><br>
  <em><b>รูปที่ 22</b> ถ้าชื่อหรือ tag ของ image ผิด หรือ image อยู่แค่ในเครื่องแต่ไม่ได้ kind load, node จะดึง image ไม่ได้และขึ้น ErrImagePull / ImagePullBackOff</em>
</p>

เมื่อ kubelet ดึง image ไม่สำเร็จ STATUS จะเป็น `ErrImagePull` และระหว่างรอลองใหม่ (ซึ่งใช้ back-off เช่นกัน) จะเป็น `ImagePullBackOff` สองค่านี้สลับกันไปมา สาเหตุที่พบบ่อย

1. **tag หรือชื่อ image ผิด** เช่น `nginx:9.99-doesnotexist`
2. **image อยู่ใน registry ส่วนตัว** แต่ไม่ได้ตั้งค่า `imagePullSecrets`
3. **image build เองในเครื่อง แต่ยังไม่ได้ `kind load`** node ของ kind ไม่เห็น image ใน Docker ของเครื่องเรา
4. **ติด rate limit ของ Docker Hub** (เช่นทั้งห้องดึงพร้อมกันจาก IP เดียว) จะเห็นคำว่า `toomanyrequests`

ข้อความใน Events บอกสาเหตุชัดเจน (ผลจริงจาก LAB 5 ตัดให้กระชับ)

```text
Warning  Failed     ...  kubelet  spec.containers{web}: Failed to pull image "nginx:9.99-doesnotexist": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:9.99-doesnotexist": failed to resolve reference "docker.io/library/nginx:9.99-doesnotexist": docker.io/library/nginx:9.99-doesnotexist: not found
Warning  Failed     ...  kubelet  spec.containers{web}: Error: ErrImagePull
Warning  Failed     ...  kubelet  spec.containers{web}: Error: ImagePullBackOff
Normal   BackOff    ...  kubelet  spec.containers{web}: Back-off pulling image "nginx:9.99-doesnotexist"
```

### 12.5 ตารางวินิจฉัยปัญหาที่พบบ่อย

**ตารางที่ 16** สาเหตุ → อาการ → คำสั่งตรวจ

| ปัญหา | อาการที่เห็น | สาเหตุที่พบบ่อย | คำสั่งตรวจ |
|---|---|---|---|
| Pending ไม่ได้ Node | `Pending`, NODE เป็น `<none>` | requests เกินที่ Node มี, taint, nodeSelector ไม่ตรง | `kubectl describe pod` ดู `FailedScheduling` |
| ดึง image ไม่ได้ | `ErrImagePull` / `ImagePullBackOff` | tag/ชื่อผิด, ไม่ได้ `kind load`, rate limit | `kubectl describe pod` ดู `Failed to pull image` |
| ตั้งค่าไม่ครบ | `CreateContainerConfigError` | อ้าง ConfigMap/Secret ที่ไม่มี | `kubectl describe pod` |
| แอปล้ม | `Error` / `CrashLoopBackOff`, RESTARTS เพิ่ม | bug, ค่า config ผิด, ต่อ DB ไม่ได้ | `kubectl logs --previous`, `describe` ดู `Exit Code` |
| memory เกิน | `OOMKilled`, exit 137 | limits ต่ำเกินไปหรือแอปรั่ว | `kubectl describe pod` ดู `Last State` |
| ไม่พร้อม | `Running` แต่ READY `0/1` | readinessProbe ไม่ผ่าน | `kubectl describe pod` ดู `Readiness probe failed` |
| ถูก restart เป็นระยะ | RESTARTS เพิ่ม, Events `Killing` | livenessProbe ไม่ผ่าน | `kubectl describe pod` ดู `Liveness probe failed` |

---

## 13. Probes ตรวจสุขภาพ container

### 13.1 Probe สามแบบ

<p align="center" id="fig-23">
  <img src="images/23-probes-three-inspectors.png" alt="รูปที่ 23 Probe สามแบบ" width="900"><br>
  <em><b>รูปที่ 23</b> kubelet ใช้ probe ตรวจสุขภาพ container: startupProbe รอให้เริ่มเสร็จ, livenessProbe ตรวจว่ายังมีชีวิต, readinessProbe ตรวจว่าพร้อมรับงาน</em>
</p>

"container ยังรันอยู่" ไม่ได้แปลว่า "แอปทำงานได้" แอปอาจค้าง (deadlock) หรือยังเชื่อมฐานข้อมูลไม่ได้ Kubernetes จึงให้ **kubelet** บนแต่ละ Node ตรวจสุขภาพ container เป็นระยะด้วย **probe** เหมือนเจ้าหน้าที่ตรวจสุขภาพ 3 คนที่มีหน้าที่ต่างกัน

**ตารางที่ 17** เปรียบเทียบ probe สามแบบ

| probe | ถามว่า | ถ้าไม่ผ่าน | ใช้เมื่อ |
|---|---|---|---|
| `startupProbe` | "เริ่มต้นเสร็จหรือยัง" | ระหว่างยังไม่ผ่าน probe อีกสองตัวถูกพักไว้ ถ้าไม่ผ่านเกิน `failureThreshold` → restart container | แอปที่เริ่มช้า เช่น ฐานข้อมูล |
| `livenessProbe` | "ยังมีชีวิตอยู่ไหม" | **kubelet ฆ่าและ restart container** (RESTARTS เพิ่ม) | แอปที่อาจค้างโดยไม่ตาย |
| `readinessProbe` | "พร้อมรับงานหรือยัง" | container ถูกทำเครื่องหมายว่า **ไม่พร้อม** (READY ลดลง เช่น `0/1`) **ไม่ถูก restart** | แอปที่ต้องรอ dependency หรือพักรับงานชั่วคราว |

ผลจริงจาก LAB 7: `readiness-http-pod` ไม่ผ่าน readiness จึงเป็น `0/1` แต่ RESTARTS ยังเป็น 0 ขณะที่ `liveness-exec-pod` ไม่ผ่าน liveness จึงถูก restart

```text
$ kubectl get pods
NAME                 READY   STATUS    RESTARTS      AGE
liveness-exec-pod    1/1     Running   1 (25s ago)   101s
readiness-http-pod   0/1     Running   0             101s
```

> **ผลของ readiness ต่อทราฟฟิก:** ในบทนี้เราเห็นแค่ READY `0/1` แต่ผลจริงจะชัดเมื่อเรียน Service ในบทหน้า เพราะ Service จะส่งทราฟฟิกเฉพาะ Pod ที่ Ready เท่านั้น

### 13.2 กลไกและพารามิเตอร์

<p align="center" id="fig-24">
  <img src="images/24-probe-mechanisms.png" alt="รูปที่ 24 กลไกของ probe" width="900"><br>
  <em><b>รูปที่ 24</b> probe ตรวจได้ 3 แบบหลัก: httpGet, tcpSocket และ exec พร้อมพารามิเตอร์ periodSeconds และ failureThreshold</em>
</p>

**ตารางที่ 18** กลไกการตรวจ

| กลไก | ผ่านเมื่อ | ตัวอย่าง |
|---|---|---|
| `httpGet` | ได้ HTTP status 200–399 | `path: /api/health`, `port: 3000` |
| `tcpSocket` | เปิดการเชื่อมต่อ TCP ได้ | `port: 5432` |
| `exec` | คำสั่งใน container จบด้วย exit 0 | `command: ["pg_isready", "-h", "127.0.0.1"]` |
| `grpc` | gRPC health check ตอบ SERVING | สำหรับแอป gRPC |

**ตารางที่ 19** พารามิเตอร์ของ probe (ค่าเริ่มต้นตาม Kubernetes)

| พารามิเตอร์ | ความหมาย | ค่าเริ่มต้น |
|---|---|---|
| `initialDelaySeconds` | รอกี่วินาทีหลัง container เริ่มก่อนตรวจครั้งแรก | 0 |
| `periodSeconds` | ตรวจทุกกี่วินาที | 10 |
| `timeoutSeconds` | รอคำตอบนานสุดกี่วินาที | 1 |
| `failureThreshold` | ไม่ผ่านติดกันกี่ครั้งจึงถือว่าล้ม | 3 |
| `successThreshold` | ผ่านติดกันกี่ครั้งจึงถือว่ากลับมาดี (liveness/startup ต้องเป็น 1) | 1 |

ตัวอย่าง livenessProbe แบบ exec จาก `liveness-exec-pod.yaml`

```yaml
livenessProbe:
  exec:
    command: ["cat", "/tmp/healthy"]   # exit 0 = ผ่าน, ไม่ใช่ 0 = ไม่ผ่าน
  initialDelaySeconds: 5               # รอ 5 วินาทีก่อนตรวจครั้งแรก
  periodSeconds: 5                     # ตรวจทุก 5 วินาที
  failureThreshold: 3                  # ไม่ผ่าน 3 ครั้งติด → restart
```

และ probe ของ container `web` ในร้านน้องส้ม (LAB 9) ซึ่งเรียก endpoint `/api/health` ที่ทดสอบการเชื่อมต่อฐานข้อมูลด้วย `SELECT 1`

```yaml
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
```

> **ข้อควรระวังในการออกแบบ:** livenessProbe ควรตรวจเฉพาะ "ตัวเองยังทำงานได้" และควรใจกว้าง (failureThreshold สูง) ถ้า liveness ไปพึ่ง dependency ภายนอก เมื่อ dependency ล่ม container ทุกตัวจะถูก restart วนพร้อมกันโดยไม่ช่วยอะไร ในร้านน้องส้มจึงตั้ง liveness ของ web ให้ทนได้ถึง 60 วินาที (10 วินาที × 6 ครั้ง)

---

## 14. Volume ภายใน Pod ด้วย emptyDir

<p align="center" id="fig-25">
  <img src="images/25-emptydir-shared-shelf.png" alt="รูปที่ 25 emptyDir ชั้นวางของร่วม" width="900"><br>
  <em><b>รูปที่ 25</b> emptyDir เป็นพื้นที่เก็บไฟล์ร่วมของ Pod ข้อมูลรอดเมื่อ container restart แต่หายไปเมื่อ Pod ถูกลบ</em>
</p>

ไฟล์ที่ container เขียนลง filesystem ของตัวเองจะ **หายเมื่อ container ถูก restart** (container ใหม่เริ่มจาก image สะอาด) ถ้าต้องการพื้นที่ที่อยู่นานกว่านั้น หรือต้องการแชร์ไฟล์ระหว่าง container ใน Pod ให้ใช้ **volume** ชนิดที่ง่ายที่สุดคือ **emptyDir**

การใช้ volume มีสองขั้น คือ **ประกาศ volume ที่ระดับ Pod** (`spec.volumes`) แล้ว **mount เข้า container** ที่ต้องการ (`volumeMounts`) โดยแต่ละ container mount ไว้คนละ path ได้

```yaml
spec:
  volumes:
    - name: html                # ชั้นวางของร่วมของทุก container ใน Pod
      emptyDir: {}              # เกิดพร้อม Pod หายพร้อม Pod
  containers:
    - name: web
      image: nginx:1.27-alpine
      volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html   # nginx เห็นที่ path นี้
    - name: menu-writer
      image: busybox:1.36
      command: ["sh", "-c", "while true; do date >> /html/index.html; sleep 5; done"]
      volumeMounts:
        - name: html
          mountPath: /html                   # busybox เห็นโฟลเดอร์เดียวกันที่ path นี้
```

**ตารางที่ 20** อายุของข้อมูลในแต่ละที่เก็บ

| เหตุการณ์ | filesystem ของ container | emptyDir | PersistentVolume (บทหน้า) |
|---|---|---|---|
| container restart (crash, OOMKilled, liveness) | หาย | **รอด** | รอด |
| ลบ Pod / สร้าง Pod ใหม่ | หาย | **หาย** | รอด |
| Node พัง | หาย | หาย | ขึ้นกับชนิดของที่เก็บ |

ตัวเลือกเพิ่มเติม: `emptyDir: { medium: Memory }` เก็บใน RAM (tmpfs) เร็วแต่ถูกนับรวมใน memory ของ container และ `sizeLimit: 100Mi` จำกัดขนาด ถ้าใช้เกิน Pod จะถูกไล่ออก (evicted)

ใน LAB 8 และ LAB 9 เราจะพิสูจน์ด้วยตาว่า เมื่อ container ตายแล้วเกิดใหม่ ไฟล์ใน emptyDir ยังอยู่ แต่เมื่อลบ Pod ข้อมูลหายหมด ถ้าต้องการข้อมูลถาวรจริง (เช่นฐานข้อมูล) ต้องใช้ **PersistentVolumeClaim (PVC)** ซึ่งเป็นเนื้อหาบทถัดไป

---

## 15. Multi-container Pod

### 15.1 Init containers

<p align="center" id="fig-26">
  <img src="images/26-init-containers.png" alt="รูปที่ 26 Init containers" width="900"><br>
  <em><b>รูปที่ 26</b> init container รันทีละตัวตามลำดับและต้องจบสำเร็จก่อน app container จึงจะเริ่มทำงาน</em>
</p>

**init container** คือ container ที่ประกาศใน `spec.initContainers` เปรียบเหมือน "ทีมเตรียมงานที่ต้องทำเสร็จก่อนเปิดร้าน" กฎของ init container คือ

1. รัน **ทีละตัวตามลำดับ** จากบนลงล่าง
2. แต่ละตัวต้อง **จบด้วย exit 0** ตัวถัดไปจึงเริ่ม
3. app container (ใน `containers`) จะเริ่มก็ต่อเมื่อ init ทุกตัวสำเร็จ
4. ถ้า init ล้ม kubelet restart ตาม `restartPolicy` ของ Pod (ถ้า `Never` Pod จะ `Failed`)
5. ระหว่างนี้ STATUS แสดงเป็น `Init:<เสร็จแล้ว>/<ทั้งหมด>` เช่น `Init:0/1` แล้วตามด้วย `PodInitializing`

งานที่เหมาะกับ init container เช่น รอ dependency พร้อม, สร้างตาราง/ใส่ข้อมูลตั้งต้นในฐานข้อมูล, ดาวน์โหลดหรือสร้างไฟล์ config ลง volume ข้อดีคือ image ของแอปไม่ต้องมีเครื่องมือเหล่านี้

ตัวอย่างจาก `init-sidecar-pod.yaml` ใน LAB 8 (init container `prepare` เขียนหน้าเว็บลง emptyDir ก่อน nginx เริ่ม)

```yaml
initContainers:               # ทำงานก่อน container หลัก ต้องจบด้วย exit 0
  - name: prepare
    image: busybox:1.36
    command:
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
        mountPath: /html
```

```text
$ kubectl get pod init-sidecar-pod
NAME               READY   STATUS     RESTARTS   AGE
init-sidecar-pod   0/2     Init:0/1   0          3s
...
$ kubectl get pod init-sidecar-pod
NAME               READY   STATUS    RESTARTS   AGE
init-sidecar-pod   2/2     Running   0          8s
```

### 15.2 Sidecar: แบบดั้งเดิมและแบบ native

<p align="center" id="fig-27">
  <img src="images/27-sidecar-pattern.png" alt="รูปที่ 27 Sidecar pattern" width="900"><br>
  <em><b>รูปที่ 27</b> sidecar ทำงานคู่กับ container หลักตลอดอายุ Pod เช่น เก็บ log หรือเตรียมไฟล์ผ่าน volume ร่วม; native sidecar คือ initContainers ที่ตั้ง restartPolicy: Always</em>
</p>

**sidecar** คือ container ผู้ช่วยที่ทำงานคู่กับ container หลัก **ตลอดอายุของ Pod** เช่น ส่ง log ออกไปเก็บ, ซิงก์ไฟล์, เป็น proxy มีสองวิธีเขียน

**ตารางที่ 21** sidecar แบบดั้งเดิมเทียบกับ native sidecar

| | sidecar แบบดั้งเดิม | native sidecar (GA ตั้งแต่ Kubernetes 1.33) |
|---|---|---|
| ประกาศที่ | `containers` (คู่กับแอปหลัก) | `initContainers` พร้อม `restartPolicy: Always` |
| ลำดับการเริ่ม | เริ่มพร้อมแอปหลัก ไม่รับประกันว่าใครก่อน | **เริ่มก่อน** init container ตัวถัดไปและแอปหลัก (รอ startupProbe ผ่านได้) |
| ระหว่างทำงาน | รันคู่กันตลอด | รันคู่กันตลอด ถ้าล้มจะถูก restart เอง |
| ตอนปิด | ปิดพร้อมกัน | ปิด **หลัง** แอปหลัก |
| ตัวอย่างใน LAB | `menu-writer` ใน LAB 8 | `db` (PostgreSQL) ใน LAB 9 |

ในร้านน้องส้ม (LAB 9) ฐานข้อมูล `db` ต้องเป็น **native sidecar** ด้วยเหตุผลนี้ ถ้าวาง PostgreSQL ไว้ใน `containers` แล้วใช้ init container `wait-for-db` คอยรอฐานข้อมูล จะเกิด **deadlock** เพราะ init container ต้องจบก่อน `containers` จึงจะเริ่ม แต่ฐานข้อมูลอยู่ใน `containers` จึงไม่มีวันเริ่ม และ `wait-for-db` ก็รอไม่มีวันจบ เมื่อย้าย `db` ไปเป็น native sidecar ลำดับจะเป็น

```text
db (native sidecar, รอ startupProbe ผ่าน) → wait-for-db (exit 0) → db-seed (exit 0) → web
                         └── db ยังทำงานต่อตลอดอายุ Pod ──────────────────────────────┘
```

```yaml
initContainers:
  - name: db
    image: postgres:17.11-alpine
    restartPolicy: Always      # ทำให้ init container นี้กลายเป็น sidecar (K8s 1.33+)
    startupProbe:              # ผ่านเมื่อไร init ตัวถัดไปจึงเริ่ม
      exec:
        command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
      periodSeconds: 2
      failureThreshold: 30     # รอได้สูงสุด 2 x 30 = 60 วินาที
  - name: wait-for-db
    image: postgres:17.11-alpine
    command:
      - sh
      - -c
      - until pg_isready -h localhost -p 5432 -U som -d catshop; do echo "รอฐานข้อมูล..."; sleep 2; done; echo "ฐานข้อมูลพร้อมแล้ว"
```

(manifest เต็มอยู่ที่ `02_LAB/som-shop/k8s/som-shop-pod.yaml`) ใน LAB 9 จะเห็นว่า READY ของ Pod นี้เป็น `2/2` เพราะนับ `web` กับ native sidecar `db` ส่วน init ที่จบแล้วไม่นับ

### 15.3 รูปแบบอื่นและเมื่อใดควรรวม container

รูปแบบ multi-container ที่พบบ่อยอีกสองแบบ

- **adapter** แปลงข้อมูลจากแอปหลักให้อยู่ในรูปแบบมาตรฐาน เช่น แปลง log/metrics ให้ระบบ monitoring อ่านได้
- **ambassador** เป็นตัวกลางเชื่อมออกภายนอกแทนแอปหลัก เช่น proxy ไปฐานข้อมูล แอปแค่ต่อ `localhost`

**ตารางที่ 22** ควรรวม container ไว้ใน Pod เดียวหรือไม่

| ควรรวม ✅ | ไม่ควรรวม ❌ |
|---|---|
| ต้องแชร์ไฟล์ผ่าน volume หรือคุยผ่าน `localhost` อย่างใกล้ชิด | แค่ "คุยกัน" ผ่านเครือข่ายตามปกติ |
| ต้องเกิด/ตาย/ย้ายไปพร้อมกันเสมอ | ต้องการ **scale แยก** (เช่น เว็บ 5 ตัว แต่ฐานข้อมูล 1 ตัว) |
| ตัวช่วยไม่มีความหมายถ้าไม่มีแอปหลัก | อัปเดตเวอร์ชันแยกกัน |
| ตัวอย่าง: nginx + ตัวซิงก์ไฟล์, แอป + log shipper | ตัวอย่าง: เว็บ + ฐานข้อมูล (ร้านน้องส้มรวมไว้ **เพื่อการเรียนเท่านั้น**) |

---

## 16. เข้าถึงและดีบัก Pod

<p align="center" id="fig-28">
  <img src="images/28-debug-toolkit.png" alt="รูปที่ 28 ชุดเครื่องมือดีบัก Pod" width="900"><br>
  <em><b>รูปที่ 28</b> ชุดเครื่องมือดีบัก Pod: get -o wide, describe (Events), logs, exec และ port-forward</em>
</p>

**ตารางที่ 23** ชุดเครื่องมือดีบัก

| คำสั่ง | ใช้ดู/ทำอะไร |
|---|---|
| `kubectl get pods -o wide` | สถานะ, READY, RESTARTS, IP, NODE |
| `kubectl get pod <ชื่อ> -w` | เฝ้าดูสถานะเปลี่ยนแบบสด (Ctrl+C เพื่อออก) |
| `kubectl describe pod <ชื่อ>` | รายละเอียดทุก container, State/Last State, probes และ **Events** |
| `kubectl logs <ชื่อ> [-c container] [-f] [--previous] [--tail=N]` | log ของ container (`-f` ตามสด, `--previous` รอบที่แล้ว) |
| `kubectl exec -it <ชื่อ> [-c container] -- sh` | เข้าไปใน container (busybox/alpine ใช้ `sh` ไม่มี `bash`) |
| `kubectl port-forward pod/<ชื่อ> <port เครื่องเรา>:<port ใน Pod>` | ส่งต่อ port จากเครื่องที่รัน kubectl เข้า Pod |
| `kubectl get events --sort-by=.lastTimestamp` | เหตุการณ์ทั้ง namespace เรียงตามเวลา |
| `kubectl debug` | ต่อ container ชั่วคราว (ephemeral container) เข้า Pod เพื่อดีบัก (ขั้นสูง ไม่ใช้ในบทนี้) |

เมื่อ Pod มีหลาย container คำสั่ง `logs` และ `exec` ต้องระบุ `-c <ชื่อ container>` ถ้าไม่ระบุ kubectl จะเลือก container แรกใน `containers` ให้และแจ้งไว้ (ผลจริงจาก LAB 9)

```text
$ kubectl logs som-shop 2>&1 | head -3
Defaulted container "web" out of: web, db (init), wait-for-db (init), db-seed (init)
▲ Next.js 16.3.8
- Local:         http://localhost:3000
```

**ลำดับการดีบักแนะนำ:** `get` (ดู STATUS/RESTARTS) → `describe` (อ่าน Events จากล่างขึ้นบน) → `logs` / `logs --previous` → `exec` เข้าไปตรวจจากข้างใน

### 16.1 เปิดเว็บใน Pod จาก browser ของนักศึกษา

<p align="center" id="fig-29">
  <img src="images/29-port-forward-ssh-tunnel.png" alt="รูปที่ 29 port-forward ร่วมกับ ssh -L" width="900"><br>
  <em><b>รูปที่ 29</b> เปิดเว็บใน Pod จาก browser: เครื่องนักศึกษา → ssh -L → container k8s-lab → kubectl port-forward → Pod</em>
</p>

Pod IP (`10.244.x.x`) ใช้ได้เฉพาะภายในคลัสเตอร์ browser บนเครื่องนักศึกษาเข้าถึงตรง ๆ ไม่ได้ ในบทนี้เราจึงต่อ "ท่อ" สองช่วง

```text
browser (เครื่องนักศึกษา) http://localhost:8080
   │  ช่วงที่ 1: ssh -p 2223 -L 8080:localhost:8080 root@localhost
   ▼
container k8s-lab  127.0.0.1:8080
   │  ช่วงที่ 2: kubectl port-forward pod/web 8080:80
   ▼
Pod web (10.244.x.x) port 80
```

1. **ใน k8s-lab** รัน `kubectl port-forward pod/web 8080:80` ซึ่งเปิด port 8080 ที่ `127.0.0.1` ของ k8s-lab แล้วส่งต่อเข้า port 80 ของ Pod (ผลจริง: `Forwarding from 127.0.0.1:8080 -> 80`) คำสั่งนี้ต้องรันค้างไว้
2. **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่แล้ว `ssh -p 2223 -L 8080:localhost:8080 root@localhost` ซึ่งบอก SSH ว่า "เปิด port 8080 บนเครื่องฉัน แล้วส่งต่อไปที่ `localhost:8080` ฝั่ง k8s-lab"
3. เปิด browser ไปที่ `http://localhost:8080`

> **ทำไมไม่ใช้ port 30080–30082 ที่ map ไว้ตอนสร้าง k8s-lab ใน LAB 0?** port ชุดนั้นเตรียมไว้สำหรับ Service ชนิด NodePort ซึ่งเป็นเนื้อหาบทถัดไป ในบทนี้เราใช้แค่ Pod จึงใช้ `port-forward` + `ssh -L` ซึ่งเป็นวิธีเข้าถึงชั่วคราวสำหรับนักพัฒนา (ไม่ใช่วิธีเปิดบริการให้ผู้ใช้จริง)

---

## 17. Pod เป็นของชั่วคราว

<p align="center" id="fig-30">
  <img src="images/30-pod-is-ephemeral.png" alt="รูปที่ 30 Pod เป็นของชั่วคราว" width="900"><br>
  <em><b>รูปที่ 30</b> Pod เดี่ยวที่ถูกลบจะไม่มีใครสร้างคืนให้ และ Pod ใหม่จะได้ IP ใหม่กับ emptyDir ว่างเปล่า</em>
</p>

Pod ถูกออกแบบให้เป็นของ **ชั่วคราว (ephemeral)** และใช้แล้วทิ้ง ข้อเท็จจริงที่ต้องจำ

1. **Pod เดี่ยวที่ถูกลบจะไม่มีใครสร้างคืน** kubelet restart ได้แค่ "container ภายใน Pod ที่ยังอยู่" แต่ถ้า Pod ทั้งกล่องหายไป (ถูกลบ, Node พัง, ถูกไล่ออก) ไม่มีกลไกใดในบทนี้สร้างใหม่ให้ ผลจริงจาก LAB 9: หลัง `kubectl delete pod som-shop` ผ่านไป 10 วินาทียังคงเป็น `No resources found in default namespace.`
2. **Pod ใหม่ = ของใหม่ทั้งหมด** แม้ apply ไฟล์เดิมได้ชื่อเดิม แต่ได้ UID ใหม่, **IP ใหม่** และ **emptyDir ว่างเปล่า** (ใน LAB 9 ออเดอร์ทั้งหมดหาย stock กลับค่าเริ่มต้น)
3. **แก้ spec ของ Pod ที่รันอยู่ได้น้อยมาก (immutable)** แก้ได้แค่บาง field เช่น `image` ส่วนอื่นต้องลบแล้วสร้างใหม่ ผลจริงจาก LAB 2 เมื่อพยายามเปลี่ยน `containerPort`

```text
The Pod "web" is invalid: spec: Forbidden: pod updates may not change fields other than `spec.containers[*].image`,`spec.initContainers[*].image`,`spec.activeDeadlineSeconds`,`spec.tolerations` (only additions to existing tolerations),`spec.terminationGracePeriodSeconds` (allow it to be set to 1 if it was previously negative)
```

4. **การลบ Pod มีช่วงผ่อนผัน (grace period)** ค่าเริ่มต้น 30 วินาที kubelet ส่งสัญญาณ SIGTERM ให้ container ปิดตัวอย่างสุภาพ ถ้าไม่ปิดภายในเวลา จะส่ง SIGKILL Pod ที่รัน `sh` ของ busybox เป็นโปรเซสหลักมักไม่ตอบ SIGTERM จึงลบช้าราว 30 วินาที (เห็นจริงใน LAB 8) ใช้ `kubectl delete pod <ชื่อ> --now` เพื่อลดเวลารอได้

> **สรุปสั้น ๆ:** "**container ตาย → kubelet ชุบชีวิตในกล่องเดิม ข้อมูลใน emptyDir รอด** / **กล่อง Pod หาย → ไม่มีใครสร้างคืน ข้อมูลหายทั้งหมด**"

---

## 18. ปูทางบทหน้า: Deployment และ Service

<p align="center" id="fig-31">
  <img src="images/31-next-chapter-preview.png" alt="รูปที่ 31 ตัวอย่างบทหน้า: Deployment และ Service" width="900"><br>
  <em><b>รูปที่ 31</b> บทหน้า: Deployment ช่วยดูแลและสร้าง Pod ใหม่ให้อัตโนมัติ และ Service ให้ที่อยู่คงที่แม้ IP ของ Pod เปลี่ยน</em>
</p>

ปัญหาที่น้องส้มพบในบทนี้ล้วนมีทางแก้ในบทถัดไป หัวข้อนี้เป็น **ภาพตัวอย่าง (preview) เท่านั้น** ยังไม่ต้องเขียนหรือใช้ใน LAB ของบทนี้

**ตารางที่ 24** ปัญหาของ Pod เดี่ยวและเครื่องมือในบทถัดไป

| ปัญหาที่เจอในบทนี้ | ทรัพยากรในบทถัดไป | แนวคิด |
|---|---|---|
| ลบ Pod แล้วไม่มีใครสร้างคืน, อยาก scale หลายตัว, อยากอัปเดตเวอร์ชันโดยไม่หยุดบริการ | **Deployment** (ผ่าน ReplicaSet) | บอกว่า "ต้องการ Pod แบบนี้ 3 ตัว" แล้ว controller คอยรักษาจำนวนให้ |
| Pod IP เปลี่ยนทุกครั้งที่สร้างใหม่, ต้องกระจายทราฟฟิกไปหลาย Pod | **Service** | ชื่อและ IP คงที่ เลือก Pod ด้วย labels ส่งทราฟฟิกเฉพาะ Pod ที่ Ready |
| เปิดเว็บต้อง port-forward + ssh -L | **Service ชนิด NodePort** (port 30080–30082 ของ k8s-lab) | เปิดบริการออกนอกคลัสเตอร์ถาวร |
| ข้อมูลใน emptyDir หายเมื่อลบ Pod | **PersistentVolumeClaim** / StatefulSet | ที่เก็บข้อมูลที่อยู่นานกว่า Pod |
| รหัสผ่านอยู่ใน YAML ตรง ๆ | **Secret** / ConfigMap | แยกค่าตั้งค่าและความลับออกจาก manifest |

---

## 19. สรุปและคำถามทบทวน

<p align="center" id="fig-32">
  <img src="images/32-chapter-summary.png" alt="รูปที่ 32 สรุปบทที่ 2" width="900"><br>
  <em><b>รูปที่ 32</b> สรุปบทที่ 2: Pod, YAML, lifecycle, probes, emptyDir และ multi-container พร้อมสำหรับ LAB</em>
</p>

### 19.1 สรุป

1. **Pod** คือหน่วยที่เล็กที่สุดที่ Kubernetes deploy ได้ ห่อ container ≥ 1 ตัวที่ใช้ IP เดียว คุยกันผ่าน `localhost` แชร์ volume ได้ และอยู่บน Node เดียวเสมอ
2. kube-scheduler เลือก Node ให้ Pod ครั้งเดียว ส่วน kubelet บน Node นั้นสั่ง container runtime ดึง image และเริ่ม container โดยดูขั้นตอนได้จาก **Events**
3. **YAML** ใช้ `key: value` การเยื้องด้วย **ช่องว่าง** และ `-` สำหรับ list ค่าที่ต้องเป็น string (เช่น `env.value`) ต้องใส่ quote
4. manifest มี 4 ส่วน: `apiVersion`, `kind`, `metadata`, `spec` เราเขียน `spec` ส่วนระบบเขียน `status`
5. container spec ที่สำคัญ: `image` พร้อม tag, `imagePullPolicy`, `ports` (เป็นข้อมูลประกอบ), `env`, `command`/`args`, `resources` (requests ใช้จัดวาง, limits เป็นเพดาน)
6. **labels** ใช้จัดกลุ่มและเลือกด้วย `-l` ส่วน **annotations** เก็บข้อมูลประกอบ
7. **phase** มี 5 ค่า แต่คอลัมน์ STATUS แสดงรายละเอียดกว่า; kubelet restart container ในกล่องเดิมตาม `restartPolicy` และใช้ back-off เมื่อล้มซ้ำ (`CrashLoopBackOff`)
8. **probes**: startup (รอเริ่มเสร็จ), liveness (ล้ม → restart), readiness (ล้ม → ไม่พร้อม ไม่ restart)
9. **emptyDir** รอด container restart แต่หายเมื่อลบ Pod; **init container** รันจนจบตามลำดับก่อนแอป; **native sidecar** คือ init container ที่มี `restartPolicy: Always`
10. Pod เป็นของ **ชั่วคราว**: ลบแล้วไม่มีใครสร้างคืน ได้ IP ใหม่ และ spec ส่วนใหญ่แก้ไม่ได้ → บทหน้าจะใช้ Deployment, Service, PVC และ Secret

> **ข้อควรจำก่อนเข้า LAB**
> - เริ่มจาก LAB 0: `docker run` container `k8s-lab` → `ssh -p 2223 root@localhost` → `git clone` แล้ว `cd /workspace/DevTools/05_kubernetes/002_kubernetes_pod/02_LAB` → `k8s-up`
> - ทุกคำสั่งรันใน SSH session ของ `k8s-lab` ยกเว้นคำสั่ง `ssh -L` และ browser ซึ่งทำบนเครื่องนักศึกษา
> - ดูปัญหาตามลำดับ `get` → `describe` (Events) → `logs --previous` → `exec`
> - Pod ที่มีหลาย container ต้องใส่ `-c <ชื่อ>` กับ `logs` และ `exec`
> - image ที่ build เองต้อง `kind load` ก่อนเสมอ

### 19.2 คำถามทบทวน

**1. ถ้าพิมพ์ `kubectl run hello --image=nginx:1.27-alpine` Kubernetes สร้างอะไรขึ้นมา และทำไมจึงไม่ได้สร้าง "container เดี่ยว"**

<details>
<summary>แนวคำตอบ</summary>

สร้าง **Pod** ชื่อ `hello` ที่มี container 1 ตัว (ชื่อ `hello`) เพราะ Pod เป็นหน่วยที่เล็กที่สุดที่ Kubernetes จัดการได้ ระบบจัดวาง ตรวจสุขภาพ และจัดสรรเครือข่ายในระดับ Pod เสมอ แม้จะมี container เพียงตัวเดียว (ดูหัวข้อ 2)
</details>

**2. container สองตัวใน Pod เดียวกันคุยกันอย่างไร และทำไมจึงฟัง port เดียวกันไม่ได้**

<details>
<summary>แนวคำตอบ</summary>

ทั้งสองใช้ network namespace เดียวกัน (มี IP เดียว) จึงเรียกกันผ่าน `localhost:<port>` ได้ และเพราะเป็น namespace เดียวกัน port จึงเป็นทรัพยากรร่วม ถ้าสองโปรแกรมฟัง port เดียวกัน ตัวที่สองจะ bind ไม่ได้ (address already in use) เหมือนสองโปรแกรมบนเครื่องเดียว
</details>

**3. จงเรียงลำดับเหตุการณ์ตั้งแต่ `kubectl apply -f pod.yaml` จนถึง Pod `Running` และระบุว่า Event ใดใน `describe` บอกแต่ละขั้น**

<details>
<summary>แนวคำตอบ</summary>

kubectl ส่งคำขอ → kube-apiserver ตรวจสอบและบันทึกลง etcd → kube-scheduler เลือก Node (Event `Scheduled`) → kubelet บน Node สั่ง container runtime สร้าง sandbox และขอ IP จาก CNI → ดึง image (`Pulling`, `Pulled`) → สร้าง container (`Created`) → เริ่ม container (`Started`) → kubelet รายงาน status กลับ → `Running`
</details>

**4. YAML ต่อไปนี้ผิดกี่จุด อะไรบ้าง**

```text
apiVersion: v1
kind: pod
metadata:
  name: Som_Shop
spec:
  containers:
  name: web
    image:nginx
    env:
      - name: PORT
        value: 3000
```

<details>
<summary>แนวคำตอบ</summary>

1. `kind: pod` ต้องเป็น `Pod` (ตัวพิมพ์ใหญ่ตามชื่อ kind)
2. `name: Som_Shop` ผิดกฎชื่อ ต้องเป็นตัวพิมพ์เล็ก ตัวเลข และ `-` เช่น `som-shop`
3. `containers:` เป็น list ต้องมี `- name: web`
4. `image` เยื้องไม่ตรงกับ `name` และ `image:nginx` ขาดช่องว่างหลัง `:` และไม่มี tag ควรเป็น `image: nginx:1.27-alpine`
5. `value: 3000` ต้องเป็น string `value: "3000"`
</details>

**5. `spec` กับ `status` ต่างกันอย่างไร และใครเป็นผู้เขียนแต่ละส่วน**

<details>
<summary>แนวคำตอบ</summary>

`spec` คือสถานะที่ต้องการ (desired state) ผู้ใช้เขียนผ่าน manifest (ระบบอาจเติมค่าเริ่มต้นให้) ส่วน `status` คือสถานะจริงที่ระบบ (kubelet/controller) เขียนรายงาน เช่น `phase`, `podIP`, `containerStatuses` ผู้ใช้ไม่ต้องเขียนเอง
</details>

**6. ถ้า Pod กำหนด `command: ["sh","-c"]` และ `args: ["echo hi"]` แต่ image มี `ENTRYPOINT ["nginx"]` และ `CMD ["-g","daemon off;"]` สิ่งที่รันจริงคืออะไร**

<details>
<summary>แนวคำตอบ</summary>

`sh -c "echo hi"` เพราะ `command` ทับ `ENTRYPOINT` และ `args` ทับ `CMD` (ตารางที่ 7) nginx จะไม่ถูกเรียกเลย
</details>

**7. requests กับ limits ต่างกันอย่างไร ถ้า container ใช้ memory เกิน limit และใช้ CPU เกิน limit จะเกิดอะไรขึ้นตามลำดับ**

<details>
<summary>แนวคำตอบ</summary>

requests ใช้ตอน scheduler เลือก Node (จองที่) ถ้าไม่มี Node ไหนพอ Pod จะ `Pending` ส่วน limits เป็นเพดานขณะรัน memory เกินจะถูก kernel ฆ่า (`OOMKilled`, exit 137) แล้ว kubelet restart ตาม restartPolicy ส่วน CPU เกินจะถูกชะลอ (throttle) แต่ไม่ถูกฆ่า
</details>

**8. STATUS `CrashLoopBackOff` บอกอะไร และควรใช้คำสั่งใดหาสาเหตุ**

<details>
<summary>แนวคำตอบ</summary>

container ล้มซ้ำ ๆ และ kubelet กำลังรอ (back-off 10s, 20s, 40s ... สูงสุด 5 นาที) ก่อน restart รอบถัดไป phase ของ Pod ยังเป็น `Running` หาสาเหตุด้วย `kubectl logs <pod> --previous` (log รอบที่ล้ม) และ `kubectl describe pod <pod>` ดู `Last State`, `Exit Code` และ Events
</details>

**9. นักศึกษา build image `myshop:1.0` ใน k8s-lab แล้ว apply Pod ที่ใช้ image นี้ทันที ได้ `ErrImagePull` เพราะอะไร แก้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

image อยู่ใน Docker ของ k8s-lab เท่านั้น แต่ node ของ kind เป็น container แยกที่มี containerd ของตัวเอง จึงมองไม่เห็น และพยายามดึงจาก Docker Hub ซึ่งไม่มี image นี้ แก้ด้วย `kind load docker-image myshop:1.0 --name lab` และตั้ง `imagePullPolicy: IfNotPresent` แล้วลบ Pod และ apply ใหม่
</details>

**10. livenessProbe กับ readinessProbe ล้มแล้วผลต่างกันอย่างไร ใน LAB 7 สังเกตจากคอลัมน์ใด**

<details>
<summary>แนวคำตอบ</summary>

liveness ล้ม → kubelet ฆ่าและ restart container → คอลัมน์ **RESTARTS** เพิ่ม; readiness ล้ม → container ถูกทำเครื่องหมายว่าไม่พร้อม → คอลัมน์ **READY** เป็น `0/1` แต่ RESTARTS ไม่เพิ่ม และกลับเป็น `1/1` เมื่อ probe ผ่านอีกครั้ง
</details>

**11. ข้อมูลใน emptyDir จะเป็นอย่างไรในสามกรณี: (ก) container ถูก OOMKilled (ข) ลบ Pod แล้ว apply ใหม่ (ค) restart container ด้วย liveness**

<details>
<summary>แนวคำตอบ</summary>

(ก) รอด (ข) หาย เพราะ emptyDir มีอายุเท่ากับ Pod เมื่อ Pod ใหม่ถูกสร้างจะได้ emptyDir ว่าง (ค) รอด เพราะเป็นการ restart container ภายใน Pod เดิม
</details>

**12. ทำไมฐานข้อมูลในร้านน้องส้มต้องเป็น native sidecar (`initContainers` + `restartPolicy: Always`) แทนที่จะอยู่ใน `containers`**

<details>
<summary>แนวคำตอบ</summary>

เพราะ init container `wait-for-db` และ `db-seed` ต้องใช้ฐานข้อมูล แต่ init container ต้องรันจบก่อน `containers` จะเริ่ม ถ้าฐานข้อมูลอยู่ใน `containers` จะยังไม่เริ่ม init container จึงรอตลอดไป (deadlock) native sidecar เริ่มก่อน init ตัวถัดไป (รอ startupProbe ผ่าน) และทำงานต่อตลอดอายุ Pod จึงแก้ปัญหานี้ได้
</details>

**13. เหตุใดเว็บกับฐานข้อมูลไม่ควรอยู่ใน Pod เดียวกันในงานจริง ยกเหตุผลอย่างน้อย 3 ข้อ**

<details>
<summary>แนวคำตอบ</summary>

(1) scale แยกไม่ได้ ถ้าเพิ่มเว็บเป็น 3 Pod ฐานข้อมูลก็ถูกคูณ 3 ด้วยและข้อมูลไม่ตรงกัน (2) อัปเดตเว็บต้องสร้าง Pod ใหม่ ทำให้ฐานข้อมูลถูกรีสตาร์ทและข้อมูลใน emptyDir หาย (3) ลบ Pod หรือ Node พังข้อมูลหายทั้งหมด (4) จัดสรร resources และดูแลความปลอดภัยแยกกันไม่ได้
</details>

**14. ทำไมในบทนี้จึงเปิดเว็บด้วย `kubectl port-forward` ร่วมกับ `ssh -L` และแต่ละคำสั่งรันที่เครื่องใด**

<details>
<summary>แนวคำตอบ</summary>

Pod IP เข้าถึงได้เฉพาะในคลัสเตอร์ และบทนี้ยังไม่ใช้ Service จึงต้องต่อท่อสองช่วง: `kubectl port-forward pod/<ชื่อ> 8080:80` รันใน k8s-lab เปิด port ที่ `127.0.0.1` ของ k8s-lab ส่งเข้า Pod ส่วน `ssh -p 2223 -L 8080:localhost:8080 root@localhost` รันบนเครื่องนักศึกษา ส่ง port 8080 ของเครื่องนักศึกษาไปที่ `localhost:8080` ของ k8s-lab จากนั้นเปิด `http://localhost:8080` ใน browser
</details>

---

## 20. เอกสารอ้างอิง

1. The Kubernetes Authors. *Pods*. https://kubernetes.io/docs/concepts/workloads/pods/
2. The Kubernetes Authors. *Pod Lifecycle*. https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
3. The Kubernetes Authors. *Init Containers*. https://kubernetes.io/docs/concepts/workloads/pods/init-containers/
4. The Kubernetes Authors. *Sidecar Containers*. https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
5. The Kubernetes Authors. *Liveness, Readiness, and Startup Probes*. https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
6. The Kubernetes Authors. *Configure Liveness, Readiness and Startup Probes*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
7. The Kubernetes Authors. *Volumes — emptyDir*. https://kubernetes.io/docs/concepts/storage/volumes/#emptydir
8. The Kubernetes Authors. *Resource Management for Pods and Containers*. https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
9. The Kubernetes Authors. *Pod Quality of Service Classes*. https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/
10. The Kubernetes Authors. *Labels and Selectors*. https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ · *Annotations*. https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/
11. The Kubernetes Authors. *Define a Command and Arguments for a Container*. https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/
12. The Kubernetes Authors. *Define Environment Variables for a Container*. https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/
13. The Kubernetes Authors. *Images* (imagePullPolicy). https://kubernetes.io/docs/concepts/containers/images/
14. The Kubernetes Authors. *Objects In Kubernetes* (spec และ status, การเขียน YAML). https://kubernetes.io/docs/concepts/overview/working-with-objects/
15. The Kubernetes Authors. *Use Port Forwarding to Access Applications in a Cluster*. https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/
16. The Kubernetes Authors. *Debug Pods*. https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/
17. The Kubernetes Authors. *kubectl Quick Reference*. https://kubernetes.io/docs/reference/kubectl/quick-reference/
18. The Kubernetes Authors. *Cluster Networking*. https://kubernetes.io/docs/concepts/cluster-administration/networking/
19. YAML Language Development Team. *YAML Ain't Markup Language Version 1.2.2*. https://yaml.org/spec/1.2.2/
20. kind — Kubernetes IN Docker. *Quick Start: Loading an Image Into Your Cluster*. https://kind.sigs.k8s.io/docs/user/quick-start/#loading-an-image-into-your-cluster

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 32 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (kind v0.33.0, Kubernetes v1.37.0) ค่าเวลา, IP และชื่อ Pod ในเครื่องผู้เรียนอาจต่างกัน
