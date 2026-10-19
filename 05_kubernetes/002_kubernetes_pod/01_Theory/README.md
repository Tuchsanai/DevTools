# บทที่ 2: Kubernetes Pod — Pod แรกของน้องส้ม

> **รายวิชา:** Software Development Tools and Environments (DevTools) · **CLO-5, CLO-6**
> **บทก่อนหน้า:** [บทที่ 1 Kubernetes และสถาปัตยกรรม](../../001_kubernetes-introduction/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

อ่านบทนี้จบแล้วควรทำได้ 4 อย่าง

1. อธิบายได้ว่า **Pod** คืออะไร และต่างจาก container อย่างไร
2. **อ่านไฟล์ YAML ของ Pod ออกทุกบรรทัด** และแก้เองได้
3. ดู STATUS แล้วบอกได้ว่า Pod พังเพราะอะไร
4. เข้าใจเรื่อง probe, emptyDir และ Pod ที่มีหลาย container ก่อนเปิดร้านน้องส้มใน LAB 8

## สารบัญ

1. [เริ่มเรื่อง: น้องส้มอยากเปิดร้าน](#1-เริ่มเรื่อง-น้องส้มอยากเปิดร้าน)
2. [Pod คืออะไร](#2-pod-คืออะไร)
3. [Pod อยู่ที่ไหน และคุยกันอย่างไร](#3-pod-อยู่ที่ไหน-และคุยกันอย่างไร)
4. [Pod เกิดขึ้นได้อย่างไร](#4-pod-เกิดขึ้นได้อย่างไร)
5. [YAML ฉบับเข้าใจง่าย](#5-yaml-ฉบับเข้าใจง่าย)
6. [อ่าน YAML ของ Pod ทีละบรรทัด](#6-อ่าน-yaml-ของ-pod-ทีละบรรทัด)
7. [ตั้งค่า container: image, env, command, resources](#7-ตั้งค่า-container-image-env-command-resources)
8. [Labels: ป้ายแท็กของ Pod](#8-labels-ป้ายแท็กของ-pod)
9. [วงจรชีวิตของ Pod และอาการพังยอดฮิต](#9-วงจรชีวิตของ-pod-และอาการพังยอดฮิต)
10. [Probes: ตรวจสุขภาพ container](#10-probes-ตรวจสุขภาพ-container)
11. [emptyDir: ที่เก็บไฟล์ของ Pod](#11-emptydir-ที่เก็บไฟล์ของ-pod)
12. [Pod หลาย container: init และ sidecar](#12-pod-หลาย-container-init-และ-sidecar)
13. [เข้าไปดู ดีบัก และเปิดเว็บใน Pod](#13-เข้าไปดู-ดีบัก-และเปิดเว็บใน-pod)
14. [Pod เป็นของชั่วคราว และบทถัดไป](#14-pod-เป็นของชั่วคราว-และบทถัดไป)
15. [สรุปและคำถามทบทวน](#15-สรุปและคำถามทบทวน)

---

## 1. เริ่มเรื่อง: น้องส้มอยากเปิดร้าน

<p align="center">
  <img src="images/01-opening-som-dream-shop.png" alt="น้องส้มฝันอยากเปิดร้านอาหารแมวบนเรือ" width="800">
</p>

น้องส้มอยากเปิด **"ร้านอาหารแมวน้องส้ม"** มีหน้าเว็บ (Next.js) กับฐานข้อมูล (PostgreSQL) แต่กัปตันบอกว่า

> "ท่าเรือเราไม่รับตู้สินค้าเปล่า ๆ นะส้ม ทุกตู้ต้อง **ใส่กล่อง Pod** พร้อม **ใบสั่งงาน YAML** ก่อน"

ทบทวนอุปมาท่าเรือจากบทที่ 1 สั้น ๆ

<p align="center">
  <img src="images/02-harbor-metaphor-map.png" alt="ทบทวนอุปมาท่าเรือ" width="800">
</p>

- **container** = ตู้สินค้า (เช่น nginx, postgres)
- **Pod** = กล่องที่ห่อตู้สินค้า มี **ป้าย IP 1 อัน**
- **Node** = เรือ (`lab-worker`, `lab-worker2`)
- **Control Plane** = หอบังคับการ (`lab-control-plane`)

สนามทดลองของเรา (สร้างใน LAB 0) อยู่ใน container ตัวเดียวบนเครื่องนักศึกษา

```text
เครื่องนักศึกษา (Docker Desktop)
 └─ container k8s-lab
     ├─ /workspace/DevTools/...   ← ไฟล์ LAB ที่ git clone มา
     └─ คลัสเตอร์ kind ชื่อ lab
         ├─ lab-control-plane      ← หอบังคับการ (ไม่รับ Pod ทั่วไป)
         ├─ lab-worker             ← เรือ: Pod ของเราอยู่ที่นี่
         └─ lab-worker2            ← เรือ: Pod ของเราอยู่ที่นี่
```

> **ขอบเขตบทนี้:** เราสร้าง **Pod เดี่ยว ๆ** เท่านั้น เรื่อง Deployment, Service, Secret เป็นของบทถัดไป

---

## 2. Pod คืออะไร

<p align="center">
  <img src="images/03-what-is-a-pod.png" alt="Pod คืออะไร" width="800">
</p>

**Pod คือหน่วยที่เล็กที่สุดที่ Kubernetes สร้างและดูแลได้** Pod หนึ่งตัวห่อ container ไว้ 1 ตัวขึ้นไป และ container ในกล่องเดียวกันจะ

- ใช้ **IP เดียวกัน** และเรียกกันผ่าน `localhost` ได้
- ใช้ **โฟลเดอร์ร่วมกัน (volume)** ได้
- อยู่บน **เรือลำเดียวกัน** เสมอ
- **เกิดพร้อมกัน ตายพร้อมกัน**

จุดที่มือใหม่มักเข้าใจผิด: **Kubernetes ไม่รัน container เดี่ยว ๆ** แม้สั่ง `kubectl run` ซึ่งดูเหมือนรัน container ตัวเดียว สิ่งที่ได้จริงคือ "Pod ที่มี container 1 ตัว" (LAB 1)

```text
$ kubectl run hello --image=nginx:1.27-alpine
pod/hello created

$ kubectl get pods -o wide
NAME    READY   STATUS    RESTARTS   AGE   IP           NODE
hello   1/1     Running   0          10s   10.244.2.3   lab-worker2
```

- `READY 1/1` = container ที่พร้อม / container ทั้งหมด
- `IP` = ป้าย IP ของกล่อง
- `NODE` = เรือที่กล่องนี้อยู่

**ทำไมต้องมีกล่อง?** บางงานต้องใช้ container หลายตัวที่ "อยู่ด้วยกัน ไปด้วยกัน" เช่น ฐานข้อมูลกับเว็บของร้านน้องส้มใน LAB 8 ถ้าแยกกันคนละเรือ จะแชร์ไฟล์กันไม่ได้และคุยผ่าน `localhost` ไม่ได้ Pod จึงรับประกันว่าทั้งกลุ่มไปด้วยกันเสมอ

<p align="center">
  <img src="images/04-why-pod-not-container.png" alt="ทำไมต้องห่อ container ด้วย Pod" width="800">
</p>

> **แนวปฏิบัติ:** ปกติ **1 Pod = แอปหลัก 1 ตัว** ถ้าอยากรับลูกค้าเพิ่ม ให้เพิ่มจำนวน Pod ไม่ใช่ยัด container แอปเดิมหลายตัวลง Pod เดียว

---

## 3. Pod อยู่ที่ไหน และคุยกันอย่างไร

### Pod อยู่บนเรือลำเดียว และไม่ย้ายเรือ

<p align="center">
  <img src="images/05-pod-lives-on-one-node.png" alt="Pod อยู่บน Node เดียวเสมอ" width="800">
</p>

- **kube-scheduler** เลือกเรือให้ Pod **ครั้งเดียว** แล้ว Pod อยู่บนเรือนั้นจนตาย
- ถ้า Pod ถูกลบหรือเรือพัง Pod ตัวนั้นจบ ไม่มีการย้าย ต้องสร้าง Pod ใหม่
- `lab-control-plane` มีป้ายห้าม (**taint**) ไว้ Pod ของเราจึงไปอยู่ได้แค่ `lab-worker` กับ `lab-worker2` (จะเห็นข้อความ `untolerated taint` ใน LAB 6)

### คุยกันภายใน Pod: ใช้ localhost

<p align="center">
  <img src="images/06-pod-shared-network-localhost.png" alt="เครือข่ายร่วมภายใน Pod และ localhost" width="800">
</p>

container ใน Pod เดียวกันใช้เครือข่ายเดียวกัน เหมือนโปรแกรมหลายตัวในคอมเครื่องเดียว

- เรียกกันด้วย `localhost:<port>` ได้เลย
- **ห้ามฟัง port ซ้ำกัน** (เหมือนสองโปรแกรมแย่ง port เดียวกัน)

ตัวอย่างจริงใน LAB 8: container `web` ต่อฐานข้อมูลใน container `db` ด้วยที่อยู่นี้

```yaml
- name: DATABASE_URL
  value: postgres://som:meow1234@localhost:5432/catshop   # db อยู่ Pod เดียวกัน จึงใช้ localhost
```

### คุยข้าม Pod: ใช้ Pod IP (แต่ IP เปลี่ยนได้)

<p align="center">
  <img src="images/07-pod-to-pod-ip.png" alt="Pod-to-Pod ด้วย Pod IP" width="800">
</p>

ทุก Pod ได้ IP ของตัวเอง (ในคลัสเตอร์ kind คือช่วง `10.244.x.x`) และคุยกับ Pod อื่นได้โดยตรงแม้อยู่คนละเรือ

**ปัญหาคือ Pod IP ไม่คงที่** ลบ Pod แล้วสร้างใหม่ก็ได้ IP ใหม่ จึงห้าม hard-code IP ในแอป บทถัดไปจะใช้ **Service** แก้เรื่องนี้

---

## 4. Pod เกิดขึ้นได้อย่างไร

<p align="center">
  <img src="images/08-pod-creation-journey.png" alt="เส้นทางการเกิดของ Pod" width="800">
</p>

เมื่อสั่ง `kubectl apply -f pod.yaml` เกิด 5 ขั้นนี้

1. **kubectl** ส่ง YAML ไปให้ **kube-apiserver**
2. **kube-apiserver** ตรวจไฟล์ แล้วบันทึกลง **etcd** (ตอนนี้ Pod ยังไม่มีเรือ = `Pending`)
3. **kube-scheduler** เลือกเรือที่เหมาะสม → event `Scheduled`
4. **kubelet** บนเรือนั้นดึง image และเริ่ม container → `Pulling` → `Pulled` → `Created` → `Started`
5. kubelet รายงานกลับ → Pod เป็น `Running`

ดูขั้นตอนนี้ได้จริงใน **Events** ของ `kubectl describe pod` (LAB 1)

```text
Events:
  Type    Reason     Age   From               Message
  Normal  Scheduled  10s   default-scheduler  Successfully assigned default/hello to lab-worker2
  Normal  Pulling    10s   kubelet            spec.containers{hello}: Pulling image "nginx:1.27-alpine"
  Normal  Pulled     2s    kubelet            spec.containers{hello}: Successfully pulled image ...
  Normal  Created    2s    kubelet            spec.containers{hello}: Container created
  Normal  Started    2s    kubelet            spec.containers{hello}: Container started
```

> **เคล็ดลับดีบัก:** Pod ไม่ขึ้น ให้ดูว่า Events **หยุดที่ขั้นไหน**
> - ไม่มี `Scheduled` → หาเรือไม่ได้ (เช่น CPU ไม่พอ)
> - ค้างที่ `Pulling` → ดึง image ไม่ได้
> - `Started` แล้วแต่ล้ม → ปัญหาอยู่ที่ตัวแอป

---

## 5. YAML ฉบับเข้าใจง่าย

ใบสั่งงานของ Kubernetes เขียนด้วย **YAML** ทุก LAB มีไฟล์เตรียมไว้ให้แล้ว งานหลักของเราคือ **อ่านให้ออก** และแก้เป็น หัวข้อนี้จึงสอนละเอียดที่สุด

### 5.1 YAML มีของแค่ 3 แบบ

<p align="center">
  <img src="images/33-yaml-map-list.png" alt="YAML มี map, list และ list ของ map" width="800">
</p>

ข้อมูลทุกอย่างใน YAML ประกอบจาก 3 แบบนี้

**แบบที่ 1: ค่าเดี่ยว `key: value`** — ชื่อข้อมูล ตามด้วย `:` **เว้นวรรค 1 ช่อง** แล้วตามด้วยค่า

```yaml
kind: Pod
name: web
```

**แบบที่ 2: map (กลุ่มข้อมูลที่มีชื่อ)** — key ที่ไม่มีค่าต่อท้าย แต่มีข้อมูลย่อย **เยื้องเข้าไป** ข้างใต้

```yaml
metadata:        # metadata เป็นกลุ่ม
  name: web      # name อยู่ "ใน" metadata
  namespace: default
```

**แบบที่ 3: list (รายการ)** — แต่ละรายการขึ้นต้นด้วย `- ` (ขีด + เว้นวรรค)

```yaml
menu:
  - ปลาทูน่า
  - ปลาซาบะ
```

### 5.2 แบบที่ใช้บ่อยที่สุด: list ของ map

ใน Kubernetes เจอแบบนี้แทบทุกไฟล์ เช่น `containers`, `env`, `ports` คือ **รายการ** ที่แต่ละรายการเป็น **กลุ่มข้อมูล**

```yaml
containers:
  - name: db                    # ← ขีด = เริ่มรายการที่ 1
    image: postgres:17.11-alpine  #   ยังเป็นของรายการที่ 1 (เยื้องตรงกับ name)
  - name: web                   # ← ขีดใหม่ = เริ่มรายการที่ 2
    image: som-shop-web:1.0       #   ของรายการที่ 2
```

วิธีอ่าน: **ขีด `-` หนึ่งอัน = หนึ่งชิ้น** บรรทัดที่เยื้องตรงกับคำหลังขีด ยังเป็นของชิ้นเดียวกัน ไฟล์นี้จึงมี container **2 ตัว** คือ `db` กับ `web`

ถ้าเขียนเป็นภาษาพูดจะได้ว่า

```text
containers = [
  ตัวที่ 1: { name = db,  image = postgres:17.11-alpine },
  ตัวที่ 2: { name = web, image = som-shop-web:1.0 }
]
```

### 5.3 การเยื้อง = ใครเป็นลูกของใคร

<p align="center">
  <img src="images/34-yaml-indent-tree.png" alt="การเยื้องใน YAML คือโครงสร้างต้นไม้" width="800">
</p>

YAML ไม่มีวงเล็บ ใช้ **การเยื้องด้วยช่องว่าง** บอกลำดับชั้นแทน จำกฎ 2 ข้อ

- **เยื้องเข้าไป = เป็นลูก** ของบรรทัดข้างบนที่เยื้องน้อยกว่า
- **เยื้องเท่ากัน = เป็นพี่น้อง** อยู่ระดับเดียวกัน

```yaml
spec:                          # ระดับ 0
  containers:                  # ระดับ 1 → ลูกของ spec
    - name: nginx              # ระดับ 2 → รายการที่ 1 ของ containers
      image: nginx:1.27-alpine #          พี่น้องของ name (อยู่ใน nginx ตัวเดียวกัน)
      ports:                   #          พี่น้องของ name
        - containerPort: 80    # ระดับ 3 → รายการที่ 1 ของ ports
```

> **เคล็ดลับ:** เวลาอ่านไฟล์ยาว ให้เอานิ้ว (หรือเคอร์เซอร์) ไล่ขึ้นไปตรง ๆ จนเจอบรรทัดแรกที่ **เยื้องน้อยกว่า** บรรทัดนั้นคือ "พ่อ" ใน VS Code จะเห็นเส้นจาง ๆ ช่วยไล่ระดับให้

สรุป 3 กฎในภาพเดียว

<p align="center">
  <img src="images/09-yaml-syntax-basics.png" alt="สรุปไวยากรณ์ YAML: key: value, เยื้อง 2 ช่องว่าง, - รายการ" width="700">
</p>

### 5.4 เรื่องเล็กที่ต้องรู้

```yaml
# บรรทัดที่ขึ้นต้นด้วย # คือ comment (คอมพิวเตอร์ไม่อ่าน)
port: 3000              # ตัวเลข
value: "3000"           # ใส่ "" = บังคับเป็นข้อความ (string)
open: true              # true/false = ค่าจริง/เท็จ
command: ["sh", "-c", "echo hi"]          # list แบบเขียนบรรทัดเดียว
requests: { cpu: 100m, memory: 256Mi }    # map แบบเขียนบรรทัดเดียว
emptyDir: {}            # map ว่าง = "ใช้ค่าเริ่มต้นทั้งหมด"
---                     # คั่นเอกสาร: ไฟล์เดียวมีหลาย Pod ได้ (LAB 4)
```

`[ ]` กับ `{ }` เป็นแค่ **ทางลัด** ความหมายเหมือนเขียนหลายบรรทัด เช่น สองแบบนี้เหมือนกันทุกประการ

```yaml
command: ["sh", "-c", "echo hi"]
```

```yaml
command:
  - sh
  - -c
  - echo hi
```

### 5.5 ผิดบ่อย แก้ง่าย

<p align="center">
  <img src="images/10-yaml-common-mistakes.png" alt="ข้อผิดพลาด YAML ที่พบบ่อย" width="800">
</p>

| ผิด | ถูก | เพราะ |
|---|---|---|
| ใช้ปุ่ม Tab เยื้อง | ใช้ช่องว่าง 2 ช่อง | YAML ไม่รับ Tab |
| `name:web` | `name: web` | ต้องเว้นวรรคหลัง `:` |
| `containers:` ↵ `  name: nginx` | `containers:` ↵ `  - name: nginx` | `containers` เป็น list ต้องมี `-` |
| `value: 9` (ใน env) | `value: "9"` | ค่าของ env ต้องเป็นข้อความ |
| `containerport: 80` | `containerPort: 80` | ชื่อ field ตัวพิมพ์เล็ก-ใหญ่ต้องตรง |
| `kind: pod` | `kind: Pod` | ชื่อ kind ขึ้นต้นตัวใหญ่ |

ไม่ต้องกลัวพิมพ์ผิด เพราะ Kubernetes ตรวจไฟล์ทุกครั้งที่ `apply` ถ้าผิดจะ **ไม่สร้างอะไรเลย** และบอกชื่อ field ที่ผิด เช่น ลืมใส่ `""` ให้ `value: 9` จะได้

```text
Error from server (BadRequest): ... cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string
```

อ่านจากท้ายข้อความ: `env.value` ต้องเป็น `string` (ข้อความ) → ใส่ `""` แล้ว apply ใหม่

---

## 6. อ่าน YAML ของ Pod ทีละบรรทัด

### 6.1 ทุกไฟล์มี 4 ส่วนเสมอ

<p align="center">
  <img src="images/11-manifest-four-parts.png" alt="Manifest สี่ส่วน" width="800">
</p>

ไฟล์ YAML ของ Kubernetes เรียกว่า **manifest** ทุกไฟล์ขึ้นต้นด้วย 4 ส่วนนี้

- `apiVersion` — ใช้แบบฟอร์มรุ่นไหน (Pod ใช้ `v1`)
- `kind` — จะสร้างอะไร (`Pod`)
- `metadata` — ชื่อและป้ายแท็กของสิ่งที่สร้าง
- `spec` — รายละเอียดว่าอยากได้อะไร (ข้างในกล่องมีอะไร)

### 6.2 ไล่ไฟล์จริงจาก LAB 2

ไฟล์ `02_LAB/labs/lab02-first-yaml/nginx-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
    owner: nong-som
spec:
  containers:
    - name: nginx
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
```

อ่านทีละบรรทัด

| บรรทัด | ความหมาย |
|---|---|
| `apiVersion: v1` | ใช้ API รุ่น `v1` (Pod อยู่ในกลุ่มพื้นฐาน) |
| `kind: Pod` | ขอสร้าง **Pod** |
| `metadata:` | เริ่มส่วนข้อมูลประจำตัว |
| `  name: web` | Pod ชื่อ `web` (ตัวพิมพ์เล็ก ตัวเลข และ `-` เท่านั้น ห้ามซ้ำ) |
| `  labels:` | เริ่มกลุ่มป้ายแท็ก |
| `    app: web` / `owner: nong-som` | ป้าย 2 อัน ไว้ค้นหาภายหลัง (หัวข้อ 8) |
| `spec:` | เริ่มส่วน "อยากได้อะไร" |
| `  containers:` | รายการ container ในกล่องนี้ |
| `    - name: nginx` | container ตัวที่ 1 ชื่อ `nginx` |
| `      image: nginx:1.27-alpine` | ใช้ image `nginx` รุ่น (tag) `1.27-alpine` |
| `      ports:` | รายการ port ที่แอปฟัง |
| `        - containerPort: 80` | แอปฟัง port 80 (เป็นข้อมูลบอกคนอ่าน ไม่ได้เปิดประตูให้ภายนอก) |

แปลทั้งไฟล์เป็นประโยคเดียว: **"ขอ Pod ชื่อ `web` ติดป้าย `app=web` ข้างในมี container `nginx` 1 ตัว ใช้ image `nginx:1.27-alpine` ฟัง port 80"**

### 6.3 spec = สิ่งที่ขอ, status = สิ่งที่เป็นจริง

<p align="center">
  <img src="images/12-spec-vs-status.png" alt="spec กับ status" width="800">
</p>

เราเขียนแค่ `spec` ส่วน `status` ระบบเขียนรายงานกลับมาให้ ดูทั้งสองส่วนด้วย `kubectl get pod web -o yaml` (LAB 2)

```yaml
spec:
  containers:
  - image: nginx:1.27-alpine
    imagePullPolicy: IfNotPresent   # ← ระบบเติมค่าเริ่มต้นให้
    name: nginx
  ...
  nodeName: lab-worker2             # ← scheduler เลือกเรือให้
  restartPolicy: Always             # ← ระบบเติมค่าเริ่มต้นให้
status:
  phase: Running                    # ← สถานะจริงตอนนี้
  podIP: 10.244.2.4
```

ไฟล์ที่เราเขียนมีราว 15 บรรทัด แต่ของจริงยาวกว่า 150 บรรทัด เพราะระบบ **เติมค่าเริ่มต้น** และ **เขียน status** ให้

### 6.4 สั่งงานด้วยไฟล์: apply, create, delete

| คำสั่ง | ถ้ายังไม่มี Pod | ถ้ามีแล้ว |
|---|---|---|
| `kubectl apply -f <ไฟล์>` | `created` | `unchanged` (สั่งซ้ำได้เสมอ) |
| `kubectl create -f <ไฟล์>` | `created` | error `AlreadyExists` |
| `kubectl delete -f <ไฟล์>` | — | ลบ Pod ตามชื่อในไฟล์ |

ใส่ชื่อ **โฟลเดอร์** แทนไฟล์ได้ เช่น `kubectl apply -f labs/lab05-lifecycle/` จะ apply ทุกไฟล์ในโฟลเดอร์ ใน LAB จึงใช้ `apply` เป็นหลัก

<p align="center">
  <img src="images/18-kubectl-explain-dry-run.png" alt="kubectl explain และ --dry-run" width="800">
</p>

ถ้าวันหนึ่งต้องเขียนไฟล์เอง มีผู้ช่วย 2 ตัว

- `kubectl explain pod.spec.containers` — คู่มือบอกว่า field นี้มีอะไรบ้าง
- `kubectl run web --image=nginx:1.27-alpine --dry-run=client -o yaml > pod.yaml` — ให้ kubectl ร่างไฟล์ให้ (ยังไม่สร้าง Pod จริง)

### 6.5 ลบโดยไม่ต้องมีไฟล์ YAML

`kubectl delete -f <ไฟล์>` ไม่ได้ใช้ไฟล์ทั้งไฟล์ kubectl แค่อ่าน **ชนิด (`kind`) กับชื่อ (`metadata.name`)** จากไฟล์ แล้วลบ object ที่ชื่อนั้น ถ้ารู้ 2 อย่างนี้ก็ **ลบได้เลยโดยไม่ต้องมีไฟล์**

| วิธี | ตัวอย่างใน LAB | ใช้เมื่อ |
|---|---|---|
| ตามไฟล์ | `kubectl delete -f labs/lab02-first-yaml/nginx-pod.yaml` (LAB 2) | มีไฟล์ที่ใช้สร้างอยู่ในมือ |
| ตามชนิด + ชื่อ | `kubectl delete pod hello` (LAB 1) หรือเขียน `pod/hello` | ไม่มีไฟล์ เช่น Pod ที่สร้างด้วย `kubectl run` ซึ่งไม่มีไฟล์ YAML เลย ดูชื่อก่อนด้วย `kubectl get pods` |
| ตามป้าย | `kubectl delete pod -l app=som-shop` (LAB 4) | ลบหลาย Pod ที่ติดป้ายเดียวกันในคำสั่งเดียว (ระวัง ตรงป้ายเมื่อไรลบหมด) |

```text
$ kubectl delete pod hello
pod "hello" deleted from default namespace
$ kubectl delete pod hello
Error from server (NotFound): pods "hello" not found      ← ลบชื่อที่ไม่มีแล้ว ได้ NotFound
```

- `-l` หาจากป้าย **บนตัว object ที่สั่งลบ** Pod ติดป้ายไว้ที่ `metadata.labels` ของตัวเอง `kubectl delete pod -l ...` จึงเจอ (บทที่ 3–4 ป้ายจะย้ายไปอยู่ใน `template` แล้วกลายเป็นกับดัก)
- Pod เดี่ยวลบแล้ว **หายถาวร** ไม่ว่าลบด้วยวิธีไหน ไม่มีใครสร้างคืน (หัวข้อ 14)

---

## 7. ตั้งค่า container: image, env, command, resources

ทุกอย่างในหัวข้อนี้เขียน **ใต้ container แต่ละตัว** (ระดับเดียวกับ `name` และ `image`)

### 7.1 image และ ports

<p align="center">
  <img src="images/13-container-image-ports.png" alt="image, tag และ containerPort" width="800">
</p>

```yaml
- name: nginx                     # ชื่อ container (ใช้กับ -c ในคำสั่ง logs/exec)
  image: nginx:1.27-alpine        # <ชื่อ image>:<tag>
  imagePullPolicy: IfNotPresent   # node มี image แล้ว ไม่ต้องดึงใหม่
  ports:
    - containerPort: 80
```

- **ใส่ tag เสมอ** (`1.27-alpine`) อย่าใช้ `latest` เพราะวันนี้กับพรุ่งนี้อาจได้ของไม่เหมือนกัน
- **`imagePullPolicy: IfNotPresent`** = ถ้าบน node มี image อยู่แล้วก็ใช้เลย สำคัญมากใน LAB 8 เพราะ image `som-shop-web:1.0` เรา build เอง ไม่มีใน Docker Hub ต้อง `kind load` เข้า node ก่อน
- **`containerPort`** เป็นแค่ข้อมูลบอกคนอ่านว่าแอปฟัง port อะไร ไม่ได้เปิดหรือปิด port

### 7.2 env: ส่งค่าเข้า container

<p align="center">
  <img src="images/14-env-variables.png" alt="ตัวแปร env" width="800">
</p>

แทนที่จะฝังค่าตั้งค่าไว้ในโค้ด เราส่งเข้าไปเป็น **ตัวแปรสภาพแวดล้อม** (environment variable) `env` เป็น list ของคู่ `name` / `value`

```yaml
env:
  - name: SHOP_NAME                 # ชื่อตัวแปร
    value: "ร้านอาหารแมวน้องส้ม"      # ค่า
  - name: OPEN_HOUR
    value: "9"                      # ตัวเลขต้องใส่ "" เสมอ
```

ผลใน LAB 6: แอปอ่านค่าได้จริง และ Kubernetes ตั้ง `HOSTNAME` เป็นชื่อ Pod ให้เอง

```text
$ kubectl exec env-command-pod -- env
HOSTNAME=env-command-pod
SHOP_NAME=ร้านอาหารแมวน้องส้ม
OPEN_HOUR=9
```

> ⚠️ รหัสผ่าน `meow1234` ใน `env` ของร้านน้องส้มใช้ **เพื่อการเรียนเท่านั้น** งานจริงต้องเก็บใน **Secret** (บทถัดไป)

### 7.3 command และ args: เปลี่ยนคำสั่งเริ่มต้น

<p align="center">
  <img src="images/15-command-args-override.png" alt="command/args ทับ ENTRYPOINT/CMD" width="800">
</p>

ทุก image มีคำสั่งเริ่มต้นของตัวเองอยู่แล้ว (`ENTRYPOINT` และ `CMD` ใน Dockerfile) ถ้าอยากให้ทำอย่างอื่น ใช้

- **`command`** → ทับ `ENTRYPOINT` (ตัวโปรแกรม)
- **`args`** → ทับ `CMD` (สิ่งที่ส่งให้โปรแกรม)
- ไม่เขียนเลย → ใช้คำสั่งเดิมของ image

ตัวอย่างจาก LAB 6

```yaml
command: ["sh", "-c"]       # ให้ shell เป็นคนรัน
args:
  - echo "SHOP_NAME=$SHOP_NAME"; echo "OPEN_HOUR=$OPEN_HOUR"; sleep 3600
```

ทำไมต้องมี `sh -c`? เพราะ `command` ไม่ได้ผ่าน shell เอง ถ้าจะใช้ `;`, `$ตัวแปร` หรือ `>` ต้องให้ `sh -c` เป็นคนแปล

### 7.4 resources: จองที่ และเพดาน

<p align="center">
  <img src="images/16-resources-requests-limits.png" alt="requests และ limits" width="800">
</p>

```yaml
resources:
  requests:          # "ขอจอง" ใช้ตอนเลือกเรือ
    cpu: "50m"       # 50m = 0.05 core (1000m = 1 core)
    memory: "32Mi"   # Mi = เมบิไบต์
  limits:            # "เพดาน" ห้ามใช้เกิน
    cpu: "100m"
    memory: "64Mi"
```

- **requests** = ขอจองไว้ scheduler จะวาง Pod บนเรือที่มีที่ว่างพอเท่านั้น ถ้าไม่มีเรือไหนพอ → Pod ค้าง **`Pending`**
- **limits** = เพดานตอนรันจริง
  - **memory เกิน → ถูกฆ่าทันที (`OOMKilled`, exit code 137)**
  - CPU เกิน → แค่ช้าลง ไม่ตาย

> ⚠️ **กับดัก:** memory ต้องเขียน `128Mi` ถ้าเขียน `128m` (m เล็ก) แปลว่า 0.128 byte!

Kubernetes ยังใช้ requests/limits จัด **QoS class** (ใครถูกไล่ออกก่อนเมื่อเรือ memory ไม่พอ): ไม่ใส่เลย = `BestEffort` (โดนก่อน), requests < limits = `Burstable`, requests = limits ทุกค่า = `Guaranteed` (โดนทีหลังสุด) ใน LAB 1 Pod `hello` เป็น `BestEffort` ส่วนใน LAB 6 `env-command-pod` เป็น `Burstable`

---

## 8. Labels: ป้ายแท็กของ Pod

<p align="center">
  <img src="images/17-labels-selectors.png" alt="Labels และ Selectors" width="800">
</p>

**label** คือป้าย `key=value` ที่แปะไว้กับ Pod เพื่อจัดกลุ่มและค้นหา เขียนไว้ใน `metadata.labels`

```yaml
metadata:
  name: shop-web
  labels:
    app: som-shop     # ร้านไหน
    tier: web         # ทำหน้าที่อะไร
```

ใช้ `-l` เลือก Pod ตามป้าย (LAB 4)

```text
$ kubectl get pods -l app=som-shop             # ร้านน้องส้มทั้งหมด
shop-cache, shop-web

$ kubectl get pods -l app=som-shop,tier=web    # , แปลว่า "และ"
shop-web
```

คำสั่งที่ใช้บ่อย

- `kubectl get pods --show-labels` — ดูป้ายทั้งหมด
- `kubectl label pod toy-web env=dev` — ติดป้าย
- `kubectl label pod toy-web env-` — ถอดป้าย (เติม `-` ท้าย key)
- `kubectl delete pod -l app=som-shop` — ลบทุกตัวที่ตรงป้าย (ระวัง!)

labels สำคัญมากในบทหน้า เพราะ Deployment และ Service **เลือก Pod จากป้าย ไม่ใช่จากชื่อ**

---

## 9. วงจรชีวิตของ Pod และอาการพังยอดฮิต

### 9.1 phase กับ STATUS ไม่ใช่สิ่งเดียวกัน

<p align="center">
  <img src="images/19-pod-phases.png" alt="Pod phase ทั้ง 5 ค่า" width="800">
</p>

**phase** คือสถานะรวมของ Pod มีแค่ 5 ค่า

- `Pending` — รับเรื่องแล้ว แต่ยังไม่ได้รัน (หาเรือ / ดึง image / รอ init)
- `Running` — มี container กำลังรันอยู่
- `Succeeded` — ทุก container ทำงานเสร็จ (exit 0)
- `Failed` — จบแล้ว และมีตัวที่ล้ม
- `Unknown` — ติดต่อเรือไม่ได้

แต่คอลัมน์ **STATUS** ใน `kubectl get pods` จะบอก **ละเอียดกว่า** เช่น `ContainerCreating`, `CrashLoopBackOff`, `Completed` ซึ่งเป็นสิ่งที่เราดูจริงทุกวัน

### 9.2 restartPolicy: ล้มแล้วเริ่มใหม่ไหม

<p align="center">
  <img src="images/20-container-states-restartpolicy.png" alt="Container state และ restartPolicy" width="800">
</p>

`restartPolicy` เขียนใต้ `spec` บอกว่าเมื่อ container จบการทำงาน kubelet จะทำอะไร

| ค่า | จบแบบสำเร็จ (exit 0) | จบแบบล้ม (exit ≠ 0) | ใช้กับ |
|---|---|---|---|
| `Always` (ค่าเริ่มต้น) | เริ่มใหม่ | เริ่มใหม่ | เว็บที่ต้องเปิดตลอด |
| `OnFailure` | หยุด → `Completed` | เริ่มใหม่ | งานที่ต้องทำให้สำเร็จ |
| `Never` | หยุด → `Completed` | หยุด → `Error` | งานครั้งเดียว |

**สำคัญ:** การเริ่มใหม่เกิด **ใน Pod เดิม** (ชื่อเดิม IP เดิม เรือเดิม) และนับในคอลัมน์ **RESTARTS** ไม่ได้สร้าง Pod ใหม่

### 9.3 อาการพังยอดฮิต

ผลจริงจาก LAB 5 ที่สร้าง 4 Pod พร้อมกัน

```text
NAME            READY   STATUS             RESTARTS      AGE
bad-image-pod   0/1     ImagePullBackOff   0             20s
completed-pod   0/1     Completed          0             20s
crash-pod       0/1     Error              1 (7s ago)    20s
onfailure-pod   0/1     Completed          1 (11s ago)   20s
```

<p align="center">
  <img src="images/21-crashloopbackoff.png" alt="CrashLoopBackOff" width="800">
</p>

**`Error` / `CrashLoopBackOff` — แอปล้มซ้ำ ๆ** แอปจบด้วย exit ≠ 0 แล้วถูกเริ่มใหม่วนไป kubelet จะ **รอนานขึ้นทุกรอบ** (10 → 20 → 40 วินาที ... สูงสุด 5 นาที) ช่วงที่รอนี้เรียกว่า back-off บน Kubernetes 1.37 STATUS จะสลับ `Error` / `CrashLoopBackOff` / `Running` ไปมา สิ่งที่ยืนยันคือ **RESTARTS เพิ่มขึ้นเรื่อย ๆ** หาสาเหตุด้วย `kubectl logs crash-pod` (ถ้าอยากเห็น log ของรอบที่แล้วใส่ `--previous`)

```text
$ kubectl logs crash-pod
กำลังเปิดร้าน...
ERROR: หาไฟล์เมนูไม่เจอ
```

<p align="center">
  <img src="images/22-imagepullbackoff.png" alt="ErrImagePull / ImagePullBackOff" width="800">
</p>

**`ErrImagePull` / `ImagePullBackOff` — ดึง image ไม่ได้** สาเหตุที่เจอบ่อย: พิมพ์ชื่อหรือ tag ผิด, build image เองแต่ลืม `kind load`, หรือ Docker Hub จำกัดการดึง (`toomanyrequests`) ดูคำว่า `not found` ใน Events

```text
Warning  Failed  ...  Failed to pull image "nginx:9.99-doesnotexist": ... not found
```

สรุปอาการทั้งหมดที่เจอใน LAB และวิธีหาสาเหตุ

| STATUS ที่เห็น | แปลว่า | ดูที่ไหน |
|---|---|---|
| `Pending` (นาน) | หาเรือไม่ได้ เช่น ขอ CPU เกิน | `describe` → `FailedScheduling` |
| `ContainerCreating` | กำลังดึง image / สร้าง container (รอได้) | — |
| `ErrImagePull` / `ImagePullBackOff` | ดึง image ไม่ได้ | `describe` → `Failed to pull image` |
| `Error` / `CrashLoopBackOff` | แอปล้มซ้ำ RESTARTS เพิ่ม | `logs`, `describe` → `Exit Code` |
| `OOMKilled` | ใช้ memory เกิน limit (exit 137) | `describe` → `Last State` |
| `Completed` | ทำงานเสร็จ (exit 0) — ไม่ใช่ปัญหา | `logs` |
| `Running` แต่ READY `0/1` | readiness probe ไม่ผ่าน | `describe` → `Readiness probe failed` |
| `Init:1/3` | init container ทำเสร็จ 1 จาก 3 ตัว | `logs -c <ชื่อ init>` |

> **จำง่าย ๆ:** Pod พังให้เริ่มจาก 2 คำสั่ง → `kubectl logs <pod>` (แอปพูดอะไร) และ `kubectl describe pod <pod>` (อ่าน `State`, `Exit Code` และ **Events** ด้านล่างสุด)

---

## 10. Probes: ตรวจสุขภาพ container

<p align="center">
  <img src="images/23-probes-three-inspectors.png" alt="Probe สามแบบ" width="800">
</p>

"container ยังรันอยู่" ไม่ได้แปลว่า "แอปใช้งานได้" แอปอาจค้าง หรือยังต่อฐานข้อมูลไม่ได้ Kubernetes จึงให้ kubelet ตรวจเป็นระยะด้วย **probe** ซึ่งมี 3 แบบ

| probe | ถามว่า | ถ้าไม่ผ่าน |
|---|---|---|
| `readinessProbe` | พร้อมรับลูกค้าหรือยัง | READY เป็น `0/1` **ไม่ถูกเริ่มใหม่** |
| `livenessProbe` | ยังมีชีวิตอยู่ไหม | **ถูกฆ่าแล้วเริ่มใหม่** (RESTARTS เพิ่ม) |
| `startupProbe` | เริ่มเสร็จหรือยัง | ระหว่างยังไม่ผ่าน probe อีก 2 ตัวรอไว้ก่อน (เหมาะกับแอปเริ่มช้า เช่นฐานข้อมูล) |

ผลจริงจาก LAB 7 ที่เห็นความต่างชัดที่สุด

```text
NAME                 READY   STATUS    RESTARTS      AGE
liveness-exec-pod    1/1     Running   1 (15s ago)   90s    ← liveness ล้ม → ถูกเริ่มใหม่
readiness-http-pod   0/1     Running   0             110s   ← readiness ล้ม → แค่ "ยังไม่พร้อม"
```

### อ่าน YAML ของ probe

<p align="center">
  <img src="images/24-probe-mechanisms.png" alt="กลไกของ probe" width="800">
</p>

probe ตรวจได้ 3 วิธี: เปิดหน้าเว็บ (`httpGet` ได้ 200–399 = ผ่าน), ต่อ port (`tcpSocket`), หรือรันคำสั่ง (`exec` จบด้วย exit 0 = ผ่าน)

```yaml
livenessProbe:                         # ตรวจว่ายังมีชีวิตไหม
  exec:                                # วิธีตรวจ: รันคำสั่งใน container
    command: ["cat", "/tmp/healthy"]   # อ่านไฟล์ได้ = ผ่าน
  initialDelaySeconds: 5               # รอ 5 วินาทีหลังเริ่ม ก่อนตรวจครั้งแรก
  periodSeconds: 5                     # ตรวจทุก 5 วินาที
  failureThreshold: 3                  # ไม่ผ่าน 3 ครั้งติด → ถือว่าตาย
```

```yaml
readinessProbe:          # ตรวจว่าพร้อมรับลูกค้าไหม
  httpGet:               # วิธีตรวจ: เปิดหน้าเว็บ
    path: /ready.html    # ได้ 200 = พร้อม, ได้ 404 = ยังไม่พร้อม
    port: 80
  periodSeconds: 3       # ตรวจทุก 3 วินาที
```

ไม่เขียนพารามิเตอร์ก็ได้ ค่าเริ่มต้นคือ ตรวจทุก 10 วินาที และไม่ผ่าน 3 ครั้งติดจึงนับว่าล้ม

---

## 11. emptyDir: ที่เก็บไฟล์ของ Pod

<p align="center">
  <img src="images/25-emptydir-shared-shelf.png" alt="emptyDir ชั้นวางของร่วม" width="800">
</p>

ไฟล์ที่ container เขียนลงเครื่องตัวเอง **หายเมื่อ container ถูกเริ่มใหม่** ถ้าอยากเก็บไว้นานกว่านั้น หรืออยากแชร์ไฟล์ระหว่าง container ให้ใช้ **volume** ชนิดง่ายที่สุดคือ **emptyDir** (โฟลเดอร์ว่างที่มีอายุเท่ากับ Pod)

ใช้ 2 ขั้น: **ประกาศ** ที่ระดับ Pod แล้ว **mount** เข้า container ตัวอย่างจากร้านน้องส้ม (LAB 8)

```yaml
spec:
  volumes:                          # ขั้นที่ 1: ประกาศ volume ของ Pod
    - name: db-data                 #   ตั้งชื่อ
      emptyDir: {}                  #   ชนิด emptyDir ใช้ค่าเริ่มต้น
  initContainers:
    - name: db
      volumeMounts:                 # ขั้นที่ 2: เอาไปเสียบเข้า container
        - name: db-data             #   ชื่อต้องตรงกับที่ประกาศ
          mountPath: /var/lib/postgresql/data   # โผล่ใน container ที่ path นี้
```

ข้อมูลรอดหรือหาย?

- **container ตายแล้วเริ่มใหม่** → ข้อมูลใน emptyDir **รอด** (LAB 8: หยุด db แล้วออเดอร์ยังอยู่ 3 รายการ)
- **ลบ Pod แล้วสร้างใหม่** → ข้อมูล **หายหมด** (LAB 8: ออเดอร์กลับเป็น 0)

ถ้าต้องการเก็บข้อมูลถาวรจริง ต้องใช้ **PersistentVolume** ในบทถัดไป

---

## 12. Pod หลาย container: init และ sidecar

### 12.1 init container: ทีมเตรียมร้าน

<p align="center">
  <img src="images/26-init-containers.png" alt="Init containers" width="800">
</p>

**init container** เขียนไว้ใน `spec.initContainers` คือ container ที่ต้อง **ทำงานให้เสร็จก่อน** แอปหลักจะเริ่ม กฎมี 3 ข้อ

1. รัน **ทีละตัว** จากบนลงล่าง
2. ตัวก่อนต้อง **จบสำเร็จ (exit 0)** ตัวถัดไปจึงเริ่ม
3. ครบทุกตัวแล้ว container ใน `containers` จึงเริ่ม

ระหว่างนั้น STATUS แสดงเป็น `Init:<เสร็จแล้ว>/<ทั้งหมด>` เช่น `Init:0/3` → `Init:2/3`

### 12.2 sidecar: ผู้ช่วยที่อยู่ตลอด

<p align="center">
  <img src="images/27-sidecar-pattern.png" alt="Sidecar pattern" width="800">
</p>

**sidecar** คือ container ผู้ช่วยที่ทำงานคู่กับแอปหลัก **ตลอดอายุ Pod** วิธีเขียนแบบใหม่ (Kubernetes 1.33 ขึ้นไป) คือใส่ไว้ใน `initContainers` แล้วเติม `restartPolicy: Always` ผลคือมัน **เริ่มก่อนใคร** และ **ไม่จบ** ทำงานต่อไปเรื่อย ๆ

### 12.3 อ่าน YAML ร้านน้องส้มทั้งไฟล์

<p align="center">
  <img src="images/35-som-shop-yaml-skeleton.png" alt="โครงของไฟล์ som-shop-pod.yaml" width="800">
</p>

ไฟล์ `02_LAB/som-shop/k8s/som-shop-pod.yaml` ยาวราว 120 บรรทัด อย่าเพิ่งตกใจ ถ้าพับเหลือแค่ "โครง" จะเหลือแค่นี้

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: som-shop
spec:
  volumes:
    - name: db-data          # ที่เก็บข้อมูลฐานข้อมูล (emptyDir)
  initContainers:
    - name: db               # 1) ฐานข้อมูล PostgreSQL — sidecar อยู่ตลอด
    - name: wait-for-db      # 2) รอจนฐานข้อมูลพร้อม แล้วจบ
    - name: db-seed          # 3) สร้างตาราง + ใส่สินค้า 6 รายการ แล้วจบ
  containers:
    - name: web              # 4) หน้าร้าน Next.js port 3000
```

แล้วค่อย ๆ เปิดดูทีละตัว ส่วนที่เหลือเป็นของที่เรียนมาแล้วทั้งหมด

```yaml
    - name: db
      image: postgres:17.11-alpine
      restartPolicy: Always          # ← ทำให้ init ตัวนี้เป็น sidecar (ไม่จบ)
      env:                           # ← หัวข้อ 7.2: ตั้งชื่อผู้ใช้/รหัส/ชื่อฐานข้อมูล
        - name: POSTGRES_USER
          value: som
        ...
      volumeMounts:                  # ← หัวข้อ 11: เก็บข้อมูลบน emptyDir
        - name: db-data
          mountPath: /var/lib/postgresql/data
      startupProbe:                  # ← หัวข้อ 10: ผ่านเมื่อไร init ตัวถัดไปจึงเริ่ม
        exec:
          command: ["pg_isready", "-U", "som", "-d", "catshop", "-h", "127.0.0.1"]
        periodSeconds: 2
        failureThreshold: 30         # รอได้สูงสุด 2 × 30 = 60 วินาที
      resources:                     # ← หัวข้อ 7.4
        requests: { cpu: 100m, memory: 256Mi }
        limits:   { cpu: 500m, memory: 512Mi }
```

ไฟล์ยาวก็จริง แต่มีค่าไม่กี่ตัวที่ **ต้องเขียนให้ตรงกันหลายที่** ถ้าพิมพ์ไม่ตรงแม้ตัวเดียว ร้านจะเปิดไม่ได้ ภาพนี้ตัดมาเฉพาะส่วนนั้น **วงสีเดียวกัน = ค่าที่ต้องตรงกัน** และ `...` = บรรทัดที่ตัดออก

<p align="center">
  <img src="images/35a-som-shop-matching-map.png" alt="ใน som-shop-pod.yaml ชื่อ volume db-data port 5432 และ port 3000 ต้องตรงกันหลายที่" width="900">
</p>

- **① ชื่อ volume ต้องตรงกัน** `db-data` ที่ประกาศใน `volumes` ต้องเหมือนกับใน `volumeMounts` ทุกตัวอักษร ไม่งั้น apply ไม่ผ่าน (หัวข้อ 11)
- **② 5432 = port ที่ PostgreSQL ฟังจริง** `containerPort` และ `livenessProbe` ของ db กับ `DATABASE_URL` ของ web จึงใช้เลขเดียวกัน และ web เรียก db ด้วย `localhost` เพราะอยู่ Pod เดียวกัน ใช้เครือข่ายเดียวกัน (หัวข้อ 3)
- **③ 3000 = port ที่ Next.js ฟัง** env `PORT: "3000"` เป็นตัวสั่ง ดังนั้น `containerPort`, `readinessProbe` และ `kubectl port-forward 3000:3000` ใน LAB 8 ต้องใช้ 3000 ตาม

ลำดับการเริ่มจึงเป็น

```text
db (sidecar เริ่มก่อน รอ startupProbe ผ่าน) → wait-for-db (จบ) → db-seed (จบ) → web
 └── db ยังทำงานต่อไปตลอดอายุ Pod ─────────────────────────────────────────┘
```

**ทำไม db ต้องเป็น sidecar?** ถ้าวาง db ไว้ใน `containers` จะเกิด **ทางตัน** เพราะ `containers` จะเริ่มก็ต่อเมื่อ init ทุกตัวจบ แต่ `wait-for-db` (init) รอ db อยู่ ซึ่งยังไม่ได้เริ่ม ต่างฝ่ายต่างรอกันไม่มีวันจบ

นี่คือเหตุผลที่ LAB 8 เห็น READY เป็น **`2/2`** ทั้งที่มี 4 container: นับเฉพาะตัวที่ทำงานตลอด คือ `db` (sidecar) กับ `web` ส่วน 2 ตัวที่จบแล้วไม่นับ

> **งานจริงไม่ทำแบบนี้:** เว็บกับฐานข้อมูลไม่ควรอยู่ Pod เดียว เพราะ scale แยกไม่ได้ (เพิ่มเว็บ 3 ตัว ฐานข้อมูลก็ถูกคูณ 3) และลบ Pod ข้อมูลหาย ร้านน้องส้มรวมไว้ **เพื่อการเรียนเท่านั้น** container ที่ควรอยู่ Pod เดียวกันคือคู่ที่ต้องแชร์ไฟล์หรือ `localhost` อย่างใกล้ชิดและต้องเกิด-ตายพร้อมกันจริง ๆ เช่น แอปกับตัวส่ง log

---

## 13. เข้าไปดู ดีบัก และเปิดเว็บใน Pod

<p align="center">
  <img src="images/28-debug-toolkit.png" alt="ชุดเครื่องมือดีบัก Pod" width="800">
</p>

ชุดคำสั่งที่ใช้ตลอดทั้ง LAB

- `kubectl get pods -o wide` — สถานะ, RESTARTS, IP, NODE
- `kubectl describe pod <ชื่อ>` — รายละเอียดทุกอย่าง + **Events**
- `kubectl logs <ชื่อ>` — แอปพิมพ์อะไรออกมา (`--previous` = รอบที่แล้ว, `-f` = ตามดูสด)
- `kubectl exec -it <ชื่อ> -- sh` — เข้าไปข้างใน container (image alpine/busybox มีแค่ `sh` ไม่มี `bash`)
- `kubectl port-forward pod/<ชื่อ> <port ฝั่งเรา>:<port ใน Pod>` — เปิดทางเข้าเว็บใน Pod

ถ้า Pod มีหลาย container ต้องบอกด้วย `-c <ชื่อ container>` เช่น `kubectl logs som-shop -c db-seed` ไม่งั้น kubectl จะเลือกตัวแรกให้เอง

**ลำดับดีบักที่แนะนำ:** `get` → `describe` (อ่าน Events) → `logs` → `exec`

### เปิดเว็บใน Pod จาก browser

<p align="center">
  <img src="images/29-port-forward-vscode-ports.png" alt="เปิดเว็บใน Pod ผ่าน kubectl port-forward และแท็บ PORTS ของ VS Code" width="800">
</p>

Pod IP (`10.244.x.x`) ใช้ได้แค่ในคลัสเตอร์ browser บนเครื่องนักศึกษาเข้าตรง ๆ ไม่ได้ จึงต่อ "ท่อ" 2 ช่วง (LAB 3 และ LAB 8)

```text
browser บนเครื่องนักศึกษา  http://localhost:8080
   │  ช่วงที่ 2: VS Code (attach เข้า k8s-lab) ส่งต่อ port ให้อัตโนมัติ → แท็บ PORTS
   ▼
container k8s-lab  port 8080
   │  ช่วงที่ 1: kubectl port-forward pod/web 8080:80   (รันค้างไว้)
   ▼
Pod web  port 80
```

1. ใน Terminal ของ VS Code ที่ attach เข้า k8s-lab รัน `kubectl port-forward pod/web 8080:80` แล้วปล่อยค้างไว้
2. เปิดแท็บ **PORTS** จะเห็น port `8080` กดไอคอน **ลูกโลก** เพื่อเปิด browser

วิธีนี้เป็นทางเข้าชั่วคราวสำหรับนักพัฒนาเท่านั้น ถ้าลบ Pod ท่อจะหลุด (`lost connection to pod`) ต้องรันใหม่

---

## 14. Pod เป็นของชั่วคราว และบทถัดไป

<p align="center">
  <img src="images/30-pod-is-ephemeral.png" alt="Pod เป็นของชั่วคราว" width="800">
</p>

Pod ถูกออกแบบให้ **ใช้แล้วทิ้ง** สิ่งที่ต้องจำ

1. **Pod ที่ถูกลบ ไม่มีใครสร้างคืน** kubelet ชุบชีวิตได้แค่ container ใน Pod ที่ยังอยู่
2. **Pod ใหม่ = ของใหม่ทั้งหมด** แม้ apply ไฟล์เดิม ก็ได้ IP ใหม่และ emptyDir ว่างเปล่า
3. **แก้ Pod ที่รันอยู่ได้น้อยมาก** แก้ได้ไม่กี่อย่าง เช่น `image` (LAB 5 ใช้ `kubectl set image`) ส่วนอื่นต้องลบแล้วสร้างใหม่
4. **ลบ Pod ต้องรอได้ถึง 30 วินาที** เพื่อให้แอปปิดตัวเรียบร้อย ใช้ `--now` ถ้าไม่อยากรอ

> **ประโยคเดียวที่ต้องจำ:** container ตาย → เกิดใหม่ในกล่องเดิม ข้อมูลใน emptyDir รอด / กล่อง Pod หาย → ไม่มีใครสร้างคืน ข้อมูลหายหมด

<p align="center">
  <img src="images/31-next-chapter-preview.png" alt="ตัวอย่างบทหน้า: Deployment และ Service" width="800">
</p>

ปัญหาที่น้องส้มเจอในบทนี้ บทถัดไปมีทางแก้

- ลบ Pod แล้วไม่มีใครสร้างคืน → **Deployment**
- IP เปลี่ยน ต้อง port-forward ใหม่ทุกครั้ง → **Service**
- ข้อมูลหายเมื่อได้ Pod ใหม่ → **PersistentVolume**
- รหัสผ่านอยู่ใน YAML → **Secret**

---

## 15. สรุปและคำถามทบทวน

<p align="center">
  <img src="images/32-chapter-summary.png" alt="สรุปบทที่ 2" width="800">
</p>

### สรุป

1. **Pod** = กล่องที่ห่อ container ≥ 1 ตัว ใช้ IP เดียว คุยกันผ่าน `localhost` อยู่เรือลำเดียว เกิด-ตายพร้อมกัน
2. **YAML** มีแค่ค่าเดี่ยว (`key: value`), map (เยื้องเข้า) และ list (`- `) — **การเยื้องบอกว่าใครเป็นลูกใคร**
3. ทุก manifest มี `apiVersion`, `kind`, `metadata`, `spec` — เราเขียน `spec` ระบบเขียน `status`
4. ใต้ container ตั้งค่าได้: `image` (ใส่ tag), `env` (ค่าเป็น string), `command`/`args`, `resources` (requests = จอง, limits = เพดาน)
5. **labels** ใช้จัดกลุ่มและเลือกด้วย `-l`
6. Pod พัง → `logs` + `describe` (Events) และจำอาการ: `Pending`, `ImagePullBackOff`, `CrashLoopBackOff`, `OOMKilled`
7. **readiness** ล้ม → ไม่พร้อม (ไม่ restart) / **liveness** ล้ม → restart
8. **emptyDir** รอดตอน container restart แต่หายเมื่อลบ Pod
9. **init container** ทำทีละตัวจนเสร็จก่อนแอปเริ่ม / **sidecar** = init ที่มี `restartPolicy: Always`
10. Pod เป็นของชั่วคราว → บทหน้าใช้ Deployment, Service, PersistentVolume และ Secret

### คำถามทบทวน

**1. สั่ง `kubectl run hello --image=nginx:1.27-alpine` แล้ว Kubernetes สร้างอะไรขึ้นมา**

<details>
<summary>แนวคำตอบ</summary>

สร้าง **Pod** ชื่อ `hello` ที่มี container 1 ตัว เพราะ Kubernetes จัดการทุกอย่างเป็นหน่วย Pod ไม่รัน container เดี่ยว ๆ
</details>

**2. ใน LAB 8 ทำไม `web` ต่อฐานข้อมูลด้วย `localhost:5432` ได้**

<details>
<summary>แนวคำตอบ</summary>

เพราะ `web` กับ `db` อยู่ใน Pod เดียวกัน ใช้เครือข่ายเดียวกัน จึงเรียกกันผ่าน `localhost` ได้เหมือนโปรแกรมสองตัวในเครื่องเดียว
</details>

**3. YAML นี้มี container กี่ตัว ชื่ออะไร และ `image` บรรทัดที่สองเป็นของใคร**

```yaml
containers:
  - name: db
    image: postgres:17.11-alpine
  - name: web
    image: som-shop-web:1.0
```

<details>
<summary>แนวคำตอบ</summary>

2 ตัว คือ `db` และ `web` (นับจากจำนวน `-`) `image: som-shop-web:1.0` เยื้องตรงกับ `name: web` จึงเป็นของ `web`
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

1. `kind: pod` ต้องเป็น `Pod`
2. `name: Som_Shop` ผิดกฎชื่อ ต้องเป็นตัวเล็ก ตัวเลข และ `-` เช่น `som-shop`
3. `containers` เป็น list ต้องเป็น `- name: web`
4. `image` เยื้องไม่ตรงกับ `name` และ `image:nginx` ขาดเว้นวรรคหลัง `:` และไม่มี tag ควรเป็น `image: nginx:1.27-alpine`
5. `value: 3000` ต้องเป็น `value: "3000"`
</details>

**5. container ใช้ memory เกิน limit กับใช้ CPU เกิน limit ผลต่างกันอย่างไร และถ้าขอ requests มากเกินจะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

memory เกิน → ถูกฆ่า `OOMKilled` (exit 137) แล้วเริ่มใหม่ / CPU เกิน → แค่ช้าลง / requests มากเกินที่เรือไหนจะมี → `Pending` และ Events ขึ้น `FailedScheduling ... Insufficient cpu`
</details>

**6. เห็น STATUS `CrashLoopBackOff` ควรทำอะไรก่อน**

<details>
<summary>แนวคำตอบ</summary>

`kubectl logs <pod>` (หรือ `--previous`) ดูว่าแอปพูดอะไรก่อนล้ม แล้ว `kubectl describe pod <pod>` ดู `Exit Code` และ Events
</details>

**7. build image `myshop:1.0` ใน k8s-lab แล้ว apply Pod ทันที ได้ `ErrImagePull` เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

node ของ kind มองไม่เห็น image ที่ build ไว้ใน Docker ของ k8s-lab จึงไปหาใน Docker Hub ซึ่งไม่มี แก้ด้วย `kind load docker-image myshop:1.0 --name lab` ใช้ `imagePullPolicy: IfNotPresent` แล้วลบ Pod และ apply ใหม่
</details>

**8. liveness กับ readiness ล้มแล้วต่างกันอย่างไร ใน LAB 7 ดูจากคอลัมน์ไหน**

<details>
<summary>แนวคำตอบ</summary>

liveness ล้ม → container ถูกเริ่มใหม่ ดูคอลัมน์ **RESTARTS** / readiness ล้ม → แค่ไม่พร้อม ดูคอลัมน์ **READY** (`0/1`) และ RESTARTS ไม่เพิ่ม
</details>

**9. ใน LAB 8 ทำไมหยุดฐานข้อมูลแล้วข้อมูลยังอยู่ แต่ลบ Pod แล้วข้อมูลหาย**

<details>
<summary>แนวคำตอบ</summary>

ข้อมูลเก็บบน emptyDir ซึ่งมีอายุเท่ากับ **Pod** หยุด db = container เริ่มใหม่ใน Pod เดิม emptyDir ยังอยู่ / ลบ Pod = emptyDir หายไปด้วย Pod ใหม่ได้ emptyDir ว่าง
</details>

**10. ทำไมฐานข้อมูลในร้านน้องส้มต้องเป็น sidecar แทนที่จะอยู่ใน `containers`**

<details>
<summary>แนวคำตอบ</summary>

`wait-for-db` และ `db-seed` (init) ต้องใช้ฐานข้อมูล แต่ `containers` จะเริ่มหลัง init ทุกตัวจบ ถ้า db อยู่ใน `containers` จะไม่มีวันได้เริ่ม เกิดทางตัน sidecar เริ่มก่อน init ตัวถัดไปและทำงานตลอด จึงแก้ได้
</details>

---

## เอกสารอ้างอิง

- Kubernetes Docs: [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) · [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) · [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) · [Sidecar Containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- Kubernetes Docs: [Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) · [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) · [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) · [Volumes: emptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)
- Kubernetes Docs: [Objects In Kubernetes (spec/status)](https://kubernetes.io/docs/concepts/overview/working-with-objects/) · [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) · [Port Forwarding](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/)
- [YAML 1.2.2 Specification](https://yaml.org/spec/1.2.2/) · [kind: Loading an Image Into Your Cluster](https://kind.sigs.k8s.io/docs/user/quick-start/#loading-an-image-into-your-cluster)

> ภาพประกอบในโฟลเดอร์ [`images/`](images/) สร้างด้วย AI เพื่อการเรียนการสอน (prompt อยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md)) ผลลัพธ์คำสั่งมาจาก LAB จริงบน kind v0.33.0 / Kubernetes v1.37.0 ค่า IP, AGE และชื่อ Node ในเครื่องผู้เรียนอาจต่างกัน
