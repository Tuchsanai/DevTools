# คู่มือ YAML ครั้งที่ 3 — ประกอบ เปลี่ยน และวินิจฉัยระบบจริง

> ศึกษาควบคู่กับปฏิบัติการ 015-021 · ตัวอย่างทั้งหมดคัดจากไฟล์จริงในโฟลเดอร์ปฏิบัติการของการสอนครั้งนี้

## 0. สรุปโครง object ใน 5 บรรทัด

1. `apiVersion` บอก API group/version และ `kind` บอกชนิด object ที่จะสร้าง
2. `metadata` ระบุตัวตน เช่น `name`, `namespace`, `labels` และ `annotations`
3. `spec` คือสภาพที่ต้องการ (desired state) ที่ผู้เรียนกำหนด โดย controller จะปรับสภาพจริงให้สอดคล้องกับข้อกำหนดนี้
4. `status` คือสภาพจริง (actual state) ที่ระบบเขียนกลับ จึงไม่ใส่ใน manifest ที่ใช้ `apply`
5. YAML ใช้การเยื้อง (indentation) ขนาด 2 ช่องและ `-` เป็นสมาชิก list; ครั้งที่ 1 มีฉบับเต็มเรื่อง syntax และคำสั่งค้น field

เมื่อไม่แน่ใจเกี่ยวกับความหมายของ field ให้ใช้ `kubectl explain <kind>.<field>` และเปรียบเทียบไฟล์กับ object จริงผ่าน
`kubectl get <kind> <name> -n <namespace> -o yaml`

## 1. Ingress

Ingress แก้ปัญหาการมีหลาย Service โดยไม่ประสงค์จะเปิดหลาย port ด้วยการบันทึกกฎ HTTP/HTTPS
ส่วน ingress controller เช่น nginx เป็น proxy ที่อ่านกฎดังกล่าวและส่ง request ไปยัง Service ที่ระบุ

โครงเต็มต่อไปนี้มาจาก `017-ingress-the-front-door/manifests/06-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1 # API group/version ของ Ingress
kind: Ingress                   # object เก็บกฎรับ traffic
metadata:
  name: skillspace              # ชื่อ Ingress ใน namespace นี้
  namespace: lab017             # ทุก backend ต้องเป็น Service ใน namespace เดียวกัน
spec:
  ingressClassName: nginx       # เลือก controller class ชื่อ nginx
  rules:                        # list ของกฎ host/path
    - http:                     # ไม่ใส่ host จึงรับทุก host ที่ส่งมาถึง controller
        paths:                  # list เส้นทางภายใต้กฎนี้
          - path: /api          # จับ /api และ path ย่อยตาม Prefix
            pathType: Prefix    # เทียบ path เป็นองค์ประกอบที่ขึ้นต้นตรงกัน
            backend:
              service:
                name: api       # ส่งต่อไป Service api
                port:
                  number: 8000  # ใช้ Service port 8000 ไม่ใช่ Pod IP
          - path: /             # กฎครอบ path อื่นของเว็บ
            pathType: Prefix
            backend:
              service:
                name: web       # ส่งต่อไป Service web
                port:
                  number: 3000
```

| field | ค่าที่ใช้ได้ | ค่า default | ผลเมื่อเปลี่ยนหรือลืมกำหนดค่า |
|---|---|---|---|
| `spec.ingressClassName` | ชื่อ IngressClass เช่น `nginx` | ไม่มี (เว้นแต่ cluster กำหนด IngressClass default ไว้) | API ยอมรับชื่อที่กำหนด แต่หากไม่มี controller สำหรับ class นั้น Ingress จะไม่มี Address และไม่ route |
| `rules[].host` | DNS name ที่ถูกต้อง | ไม่ระบุ = รับทุก host | ระบุแล้ว request ที่ Host ไม่ตรงจะไม่เข้ากฎนี้ |
| `rules[].http.paths[].path` | path เช่น `/`, `/api` | ไม่มี | ต้องขึ้นต้น `/`; เส้นทางเปลี่ยนทำให้ URL ที่จับเปลี่ยน |
| `pathType` | `Exact`, `Prefix`, `ImplementationSpecific` | **ไม่มีและเป็น field บังคับ** | ลืมแล้ว API ปฏิเสธ object; `Exact` ไม่จับ path ย่อย |
| `backend.service.name` | ชื่อ Service ใน namespace เดียวกัน | ไม่มี | ชื่อที่ไม่มีอยู่จริงทำให้ backend ใช้งานไม่ได้และมักตอบ 503 |
| `backend.service.port.number` หรือ `.name` | Service port 1-65535 หรือชื่อ port | ไม่มี; ต้องระบุอย่างใดอย่างหนึ่ง | `number` กับ `name` ใช้พร้อมกันไม่ได้ และค่าต้องตรง `Service.spec.ports[].port` หรือ `.name` |
| `spec.tls` | list ของ `hosts` กับ `secretName` | ไม่มี | ไม่ใส่ยังรับ HTTP; ใส่แล้ว controller ใช้ Secret ใบรับรองตามที่รองรับ |

`host` และ `tls` ไม่ปรากฏใน manifest ของชุดนี้ เพื่อให้เข้าถึง `localhost` ได้โดยไม่กำหนด Host header
ตารางข้างต้นอธิบายองค์ประกอบดังกล่าวเพื่อสนับสนุนการอ่าน manifest ของระบบจริงที่แยกโดเมนและเปิด HTTPS
`Exact` เทียบทั้ง path แบบ case-sensitive, `Prefix` เทียบทีละส่วนที่คั่นด้วย `/`, ส่วน
`ImplementationSpecific` มอบวิธีเทียบให้ IngressClass/controller จึงต้องอ่านเอกสารของ controller เพิ่ม

**ผิดบ่อย**

- `06-ingress-bad.yaml` เปลี่ยน backend เป็น `web-svc` ที่ไม่มีอยู่จริง โดย runlog แสดง
  `<error: services "web-svc" not found>` และผู้ใช้ได้รับ `503 Service Temporarily Unavailable`
- การเปลี่ยน `number: 3000` เป็น port ที่ Service ไม่ได้ประกาศทำให้ route ไม่สำเร็จ ให้ตรวจสอบด้วย `kubectl describe ingress`
- ลืม `pathType` แล้ว server/apply จะตอบ `The Ingress "x" is invalid: spec.rules[0].http.paths[0].pathType: Required value: pathType must be specified`; `--dry-run=client` ไม่ตรวจเงื่อนไขนี้

ตรวจสอบ object จริงด้วย `kubectl get ingress skillspace -n lab017 -o yaml`,
`kubectl describe ingress skillspace -n lab017` และ `kubectl explain ingress.spec.rules.http.paths`

## 2. resources

`resources` เป็นส่วนของ container ไม่ใช่ object แยก: `requests` บอก scheduler ว่าต้อง “จอง” เท่าไร
ส่วน `limits` เป็นเพดานระหว่างการทำงาน โดย CPU จะถูก throttle ขณะที่ memory ที่เกินอาจสิ้นสุดด้วย `OOMKilled`

ตัวอย่างจริงจาก `019-telling-kubernetes-what-you-need/manifests/02-web-deployment.yaml`
(ตัดส่วน `readinessProbe` ที่อยู่ถัดจาก `resources` ออกเพื่อโฟกัส field นี้):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: lab019
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: k8s-lab-web:v1
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 3000
          resources:             # ความต้องการของ container web
            requests:            # scheduler ใช้เลือก node
              cpu: 100m          # 100 millicpu = 0.1 CPU core
              memory: 128Mi      # 128 mebibytes
            limits:              # เพดานที่ runtime บังคับ
              cpu: 500m          # 0.5 CPU core
              memory: 256Mi      # เกินเพดานนี้มีโอกาส OOMKilled
```

| field | ค่าที่ใช้ได้ | ค่า default | ผลเมื่อเปลี่ยนหรือลืมกำหนดค่า |
|---|---|---|---|
| `requests.cpu` | Quantity เช่น `100m`, `1` | ถ้ามี limit จะใช้ limit; ไม่เช่นนั้น implementation-defined | สูงขึ้นจอง CPU มากขึ้น; สูงเกินทุก node ทำให้ Pending |
| `limits.cpu` | Quantity เช่น `500m`, `2` | ไม่มี | process ที่ต้องการเกินถูก throttle ไม่ใช่ OOMKilled |
| `requests.memory` | bytes หรือหน่วย เช่น `128Mi`, `1Gi` | ถ้ามี limit จะใช้ limit; ไม่เช่นนั้น implementation-defined | scheduler เทียบกับ memory ที่ node ยังจัดสรรได้ |
| `limits.memory` | bytes หรือหน่วย เช่น `256Mi`, `1Gi` | ไม่มี | ใช้เกินอาจถูก kernel OOM kill แล้ว container restart |

หน่วย CPU `m` คือหนึ่งในพัน core; memory `Mi`/`Gi` เป็นฐาน 1024 ส่วน `M`/`G` เป็นฐาน 1000
และมีความหมายต่างกัน จึงไม่ควรละอักษร `i` โดยไม่ตั้งใจ ถ้ากำหนด limit แต่ไม่กำหนด request
Kubernetes ใช้ limit เป็น request; admission policy เช่น LimitRange อาจเติมค่าให้ก่อนหน้านั้นได้

### QoS class

| QoS | เงื่อนไขของ Pod | ผลที่ควรจำ |
|---|---|---|
| `Guaranteed` | ทุก container มี CPU+memory request/limit และแต่ละคู่เท่ากัน | ได้รับระดับการป้องกันการ eviction สูงสุดในสาม class |
| `Burstable` | ไม่ถึง Guaranteed แต่มี request หรือ limit อย่างน้อยหนึ่งรายการ | burst ได้ภายใน limit แต่ถูกพิจารณา eviction ก่อน Guaranteed |
| `BestEffort` | ไม่มี CPU/memory request และ limit ในทุก container | scheduler ไม่เห็นการจองและถูก eviction ก่อนเมื่อ node กดดัน |

**ผิดบ่อย**

- `03-web-too-big.yaml` ใช้ `cpu: "64"` ซึ่งคือ 64 cores ไม่ใช่ 64m; runlog แสดง
  `0/3 nodes are available: ... 2 Insufficient cpu.`
- `04-web-oom.yaml` จำกัด `memory: 32Mi`; runlog แสดง `Reason: OOMKilled` และ exit code 137
- การกำหนดเพียง limit โดยสันนิษฐานว่า request เป็นศูนย์อาจทำให้ค่าคลาดเคลื่อน เนื่องจากระบบอาจนำ limit ไปเป็น request ดังที่กล่าวข้างต้น

ตรวจสอบ object จริงด้วย `kubectl get pod -n lab019 -l app=web -o jsonpath='{.items[0].status.qosClass}'`,
`kubectl describe pod <pod> -n lab019` และ `kubectl explain deployment.spec.template.spec.containers.resources`

## 3. strategy

Deployment ใช้ strategy ควบคุมวิธีแทนที่เมื่อ Pod template เปลี่ยนแปลง โดยอาจแทนที่อย่างเป็นลำดับหรือหยุดชุดเดิมก่อน
ค่าต้องอ่านคู่กับ readiness เพราะ Pod ใหม่ถูกนับ Available หลัง Ready ครบ `minReadySeconds`

ตัวอย่างจริงจาก `018-updating-without-downtime/manifests/02-web-deployment.yaml`:

```yaml
spec:
  replicas: 3                    # desired Pod ปกติสามตัว
  minReadySeconds: 5            # ต้อง Ready ต่อเนื่อง 5 วินาทีก่อนนับ Available
  strategy:
    type: RollingUpdate          # ค่อย ๆ แทน Pod เก่าด้วย Pod ใหม่
    rollingUpdate:
      maxSurge: 1                # ระหว่าง rollout สร้างเกิน replicas ได้หนึ่งตัว
      maxUnavailable: 0          # ห้ามจำนวน Available ต่ำกว่าสามเพราะ rollout
```

ไฟล์ทดลอง `018-updating-without-downtime/02-web-recreate.yaml` ใช้ค่าจริงอีกแบบ:

```yaml
spec:
  replicas: 3
  strategy:
    type: Recreate               # ลบ Pod เก่าก่อนสร้าง Pod รุ่นใหม่เมื่อ template เปลี่ยน
```

| field | ค่าที่ใช้ได้ | ค่า default | ผลเมื่อเปลี่ยนหรือลืมกำหนดค่า |
|---|---|---|---|
| `strategy.type` | `RollingUpdate`, `Recreate` | `RollingUpdate` | Recreate มีช่วงที่ replica เก่าเป็นศูนย์ จึงเหมาะกับงานที่ไม่สามารถทำงานสองรุ่นพร้อมกันได้ |
| `maxSurge` | จำนวนเต็มหรือเปอร์เซ็นต์ | `25%` ปัดขึ้น | สูงขึ้น rollout เร็วขึ้นแต่ใช้ capacity ชั่วคราวมากขึ้น; ใช้ไม่ได้กับ Recreate |
| `maxUnavailable` | จำนวนเต็มหรือเปอร์เซ็นต์ | `25%` ปัดลง | สูงขึ้นแทนที่เร็วแต่ Available ลดได้มากขึ้น; ห้ามทั้งค่านี้และ maxSurge เป็น 0 |
| `minReadySeconds` | จำนวนวินาทีตั้งแต่ 0 | `0` | สูงขึ้นชะลอการนับ Available เพื่อตรวจพบความล้มเหลวหลังเริ่มทำงานได้ไม่นาน |
| `revisionHistoryLimit` | จำนวน revision ที่บันทึกไว้ | `10` | `0` ล้าง ReplicaSet เก่าและทำให้ rollback revision ก่อนหน้าไม่ได้ |

`maxUnavailable: 0` เพียงค่าเดียวไม่สามารถป้องกัน downtime ได้ แต่ต้องใช้ readinessProbe ที่สะท้อนความพร้อมรับงานจริงร่วมด้วย
ส่วน `Recreate` หยุด Pod เก่าของ Deployment ก่อนสร้าง Pod รุ่นใหม่เมื่อ template เปลี่ยน แต่ถ้าลบ Pod เอง
ระหว่าง Recreate นั้น ReplicaSet จะสร้าง Pod ทดแทนทันที แม้ Pod เดิมยังอยู่ในสถานะ `Terminating`

**ผิดบ่อย**

- การใช้ Recreate กับ web ไม่รับประกันความต่อเนื่องของบริการ โดย runlog ของปฏิบัติการ 018 แสดง `FAIL` ต่อเนื่องระหว่าง rollout
- ตั้ง `maxUnavailable: 0` แต่ถอด readinessProbe ทำให้ process ที่ยังไม่พร้อมรับงานอาจถูกเพิ่มเป็นปลายทางเร็วเกินไป
- การลด `revisionHistoryLimit` มากเกินไปทำให้ไม่มี revision เดิมสำหรับดำเนินการ rollback

ตรวจสอบ object จริงด้วย `kubectl get deployment web -n lab018 -o yaml`,
`kubectl rollout history deployment/web -n lab018` และ `kubectl explain deployment.spec.strategy.rollingUpdate`

## 4. โครงโฟลเดอร์ manifests

โฟลเดอร์ `manifests/` ทำหน้าที่เป็นแหล่งสภาพที่ต้องการของระบบ ตัวเลขนำหน้าช่วยให้ผู้เรียนอ่านตามลำดับ
Config → workload → network โดยแต่ละไฟล์ยังคงเป็น object อิสระ ตัวอย่างจริงในปฏิบัติการ 015 มีดังนี้:

```text
manifests/
├── 01-configmap.yaml
├── 02-web-deployment.yaml
├── 03-web-service.yaml
├── 04-api-deployment.yaml
├── 05-api-service.yaml
└── 06-ingress.yaml
```

ให้พิจารณา directory เดียวกันผ่านคำสั่งสามลักษณะต่อไปนี้:

| คำสั่ง | อ่านคำสั่งอย่างไร | สิ่งที่ควรเห็น |
|---|---|---|
| `kubectl apply -f manifests/` | ส่ง manifest ใน directory (ไม่ลง subdirectory เว้นใช้ `-R`) | `created`, `configured` หรือ `unchanged` ต่อ object |
| `kubectl diff -f manifests/` | เทียบไฟล์กับ live object ก่อน apply | ไม่มี output เมื่อเหมือน; exit code 1 เมื่อมี diff; มากกว่า 1 คือ error |
| `kubectl get -f manifests/` | ค้นหา live object จากชนิด/ชื่อ/namespace ในไฟล์ | ตารางสถานะของ object ที่ไฟล์ระบุ |

ไม่ควรตีความเลขชื่อไฟล์ว่าเป็นการ “รอ Ready ตามลำดับ” เนื่องจาก `apply` เพียงส่งสภาพที่ต้องการ
Pod อาจเริ่มก่อน ConfigMap พร้อมชั่วคราว แต่เมื่อ apply ครบ controller จะ reconcile ต่อเอง

**ผิดบ่อย**

- การเรียกใช้งานจาก directory ที่ไม่ถูกต้องให้ผล `error: the path "manifests/" does not exist` (เป็นตัวอย่างข้อความซึ่งไม่ปรากฏใน runlog)
- การลบ `web-config` แล้ว restart ตามปฏิบัติการ 015 ทำให้เกิด `CreateContainerConfigError` โดย runlog ระบุ
  `Error: configmap "web-config" not found` และ apply ทั้งโฟลเดอร์สร้างกลับได้
- ใช้ `kubectl diff ... || true` เหมาะกับการสาธิต แต่ใน CI อาจบดบังทั้ง “มี diff” และ error จริง ควรอ่าน exit code

ศึกษาวิธีรับ `-f` ด้วย `kubectl apply --help`, `kubectl diff --help` และ `kubectl get --help`

## 5. manifest ที่มีข้อผิดพลาดโดยเจตนาของปฏิบัติการ 020

ปฏิบัติการนี้ไม่ได้เสนอ syntax ใหม่ แต่มุ่งฝึกพิจารณาสภาพที่ต้องการและคาดการณ์อาการก่อนเรียกใช้งาน
ค่าต่อไปนี้คัดจากไฟล์จริงทั้งสี่คู่และ exercise:

```yaml
# broken/01-pending.yaml → fixed/01-pending.yaml
cpu: "64"                         # ผิด: ขอ 64 cores
cpu: 50m                           # แก้: ขอ 0.05 core
# broken/02-imagepull.yaml → fixed/02-imagepull.yaml
image: k8s-lab-web:v1.0            # ผิด: tag ไม่มีในแล็บ
image: k8s-lab-web:v1              # แก้: tag ที่ build/load แล้ว
# broken/03-crashloop.yaml
command: ["node", "missing.js"]    # ผิด: override command ให้เปิดไฟล์ไม่มีจริง
# broken/04-no-endpoints.yaml → fixed/04-no-endpoints.yaml
app: wep                           # ผิด: Service selector ไม่ตรง Pod label
app: web                           # แก้: selector ตรง label
# exercise/05-mystery.yaml
targetPort: 3001                   # endpoint มี แต่ process ฟัง containerPort 3000
```

| อ่าน field แล้วถาม | อาการจริงจาก runlog | เปิดหลักฐานด้วย |
|---|---|---|
| requests ใหญ่เกิน node ใดรับได้หรือไม่ | `FailedScheduling ... Insufficient cpu` | `kubectl describe pod pending-web -n lab020` |
| image:tag มีอยู่ใน node/registry หรือไม่ | `ErrImagePull` แล้ว `ImagePullBackOff` | `kubectl describe pod imagepull-web -n lab020` |
| command ชี้ executable/file จริงหรือไม่ | `Error: Cannot find module '/app/missing.js'` | `kubectl logs crashloop-web -n lab020` |
| Service selector ตรง Pod labels หรือไม่ | Endpoints เป็น `<none>` ทั้งที่ Pod Running | `kubectl describe service web -n lab020` |
| targetPort มี process ฟังหรือไม่ | `wget: can't connect to remote host (10.96.178.73): Connection refused` แม้ endpoint มี | `kubectl exec ... -- wget ...` |

หลักคิดคือ `get` ระบุอาการ → `describe` ตรวจสอบสาเหตุ → `logs` ตรวจข้อความจาก process → `events` พิจารณาภาพรวม;
ให้แก้ไขด้วยไฟล์ใน `fixed/` ทีละคู่ แล้วพิสูจน์ว่าอาการได้รับการแก้ไข มิใช่เพียงเปลี่ยนสถานะให้ปรากฏว่าปกติ

## 6. ทบทวน object ที่เรียนแล้ว

### Deployment
ย่อจาก `021-the-big-picture/manifests/02-web-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: lab021
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
```
field สำคัญ: `replicas`, `selector.matchLabels`, `template.metadata.labels` (ต้องตรง selector) และ `template.spec` ซึ่งเป็น Pod template · ใช้ใน [LAB 021](021-the-big-picture/README.md)

### Service
ย่อจาก `021-the-big-picture/manifests/03-web-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: lab021
spec:
  selector:
    app: web
  ports:
    - name: http
      port: 3000
      targetPort: http
```
field สำคัญ: `type` (ไฟล์ไม่ใส่จึง default `ClusterIP`), `selector`, `ports[].port`, `targetPort` และ `protocol` (default `TCP`) · ใช้ใน [LAB 021](021-the-big-picture/README.md)

### ConfigMap
คัดจาก `021-the-big-picture/manifests/01-configmap.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
  namespace: lab021
data:
  SITE_NAME: SkillSpace
  THEME: blue
  API_BASE_URL: http://api:8000 # web เรียก api ผ่านชื่อ Service
```
field สำคัญ: `metadata.name`, `metadata.namespace`, `data` (ค่าเป็น string) และ `envFrom.configMapRef.name` ฝั่ง Deployment · ใช้ใน [LAB 021](021-the-big-picture/README.md)

### Secret
คัดจาก `021-the-big-picture/manifests/07-secret.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: lab021
type: Opaque
stringData:
  POSTGRES_PASSWORD: labpass # ค่าสมมุติสำหรับห้องเรียนเท่านั้น
```
field สำคัญ: `type`, `stringData`, `data` (API บันทึกเป็น base64) และ `secretKeyRef.name/key`; ห้าม commit ค่าจริง · ใช้ใน [LAB 021](021-the-big-picture/README.md)

### PVC
คัดจาก `021-the-big-picture/manifests/08-pvc.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data
  namespace: lab021
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi # ขอพื้นที่โดยไม่ผูกชื่อ PV เอง
```
field สำคัญ: `accessModes`, `resources.requests.storage`, `storageClassName` (ไม่ระบุให้ใช้ default StorageClass) และ `metadata.name` ที่ `claimName` อ้างถึง · ใช้ใน [LAB 021](021-the-big-picture/README.md)

### Probes
ย่อจาก `021-the-big-picture/manifests/02-web-deployment.yaml`:
```yaml
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
```
field สำคัญ: `httpGet.path/port`, `initialDelaySeconds`, `periodSeconds` และชนิด probe; readiness fail จะถอดจาก Service endpoint ส่วน liveness fail จะ restart container · ใช้ใน [LAB 021](021-the-big-picture/README.md)

## สรุป field ทั้งหมดของครั้งนี้

| field/กลไก | object | ปฏิบัติการแรกที่เน้น |
|---|---|---:|
| `ingressClassName`, `rules[].http.paths[]`, `pathType`, backend, `host`, `tls` | Ingress | 017 |
| `requests`, `limits`, หน่วย CPU/memory, QoS | Container resources | 019 |
| `RollingUpdate`, `maxSurge`, `maxUnavailable`, `Recreate`, `minReadySeconds`, `revisionHistoryLimit` | Deployment | 018 |
| ชื่อไฟล์ `01-...`, `apply/diff/get -f` | directory manifests | 015 |
| request/image/command/selector/targetPort ที่จงใจผิด | Pod/Service | 020 |

**ภาพรวมที่ควรจดจำ:** YAML คือแผนที่สภาพที่ต้องการซึ่งอ่านจากชนิดและชื่อลงไปยัง `spec`
จากนั้นคาดการณ์ผลของแต่ละ field และใช้ `get → describe → logs → events` ตรวจสอบว่าสภาพจริงดำเนินไปตามแผนหรือหยุดที่ส่วนใด
