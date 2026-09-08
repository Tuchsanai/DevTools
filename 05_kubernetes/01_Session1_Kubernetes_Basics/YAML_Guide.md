# คู่มือ YAML ครั้งที่ 1 — หลักการทำความเข้าใจสภาพที่ต้องการ (desired state)
> ใช้ประกอบปฏิบัติการ 001-007 · ตัวอย่างทั้งหมดคัดจากไฟล์จริงในโฟลเดอร์ปฏิบัติการของการสอนครั้งนี้

คู่มือนี้มุ่งเน้นความเข้าใจแทนการท่องจำ โดยให้พิจารณาตามลำดับว่า object เป็นชนิดใด อยู่ใน namespace ใด และกำหนดให้ระบบรักษาสภาพใด จากนั้นใช้ `kubectl explain` เมื่อต้องการตรวจสอบ schema

## หลักการอ่าน YAML

YAML เป็นรูปแบบข้อมูล ส่วน Kubernetes API ทำหน้าที่ตรวจสอบว่า field สอดคล้องกับ schema ของ object หรือไม่ ดังนั้น YAML ที่มีการเยื้องถูกต้องอาจยังไม่สอดคล้องกับ schema ได้

ตัวอย่างจาก `004-declarative-yaml/01-pod.yaml`:

```yaml
apiVersion: v1                    # core API group เวอร์ชัน v1
kind: Pod                         # ชนิด object; ตัวพิมพ์ต้องตรง
metadata:                         # ข้อมูลระบุตัวและข้อมูลประกอบ
  name: web                       # ชื่อ object ใน namespace
  labels:                         # คู่ key/value สำหรับจัดกลุ่ม
    app: web                      # label app มีค่า string web
    version: v1                   # label version มีค่า string v1
spec:                             # desired state ที่ผู้ใช้ส่งให้ระบบ
  containers:                     # list ของ container ใน Pod
    - name: web                   # สมาชิก list ตัวแรก
      image: k8s-lab-web:v1       # image ที่ต้องการรัน
      imagePullPolicy: IfNotPresent # ใช้ image ใน node ก่อนถ้ามี
      ports:                      # list ของ port ที่ container ประกาศ
        - containerPort: 3000     # แอปฟังที่ port 3000
```

| ส่วน | อ่านอย่างไร | ผลเมื่อเปลี่ยนหรือละเว้นค่า |
|---|---|---|
| `apiVersion` | `v1` คือ core group; `apps/v1` คือ group `apps` version `v1` | หากไม่รองรับ group/version ระบบจะไม่พบ resource mapping; ตรวจสอบด้วย `kubectl api-resources` |
| `kind` | ชนิด เช่น `Pod`, `ReplicaSet`, `Deployment` | ตัวพิมพ์หรือชื่อผิด API ไม่รู้จัก |
| `metadata.name` | ชื่อไม่ซ้ำภายใน kind และ namespace เดียวกัน | การเปลี่ยนชื่อเป็นการอ้างถึง object อื่น ไม่ใช่การ rename |
| `metadata.namespace` | ขอบเขตของ namespaced object | หากไม่ระบุ ระบบใช้ namespace ของ request/context; ค่าในไฟล์ต้องสอดคล้องกับ `-n` |
| `metadata.labels` | string key/value ที่ selector ใช้จัดกลุ่ม | เปลี่ยนแล้ว membership เปลี่ยนทันที |
| `metadata.annotations` | ข้อมูลประกอบที่ไม่ใช้เลือกสมาชิก | เหมาะกับ change cause ไม่ใช่ identity ของกลุ่ม |
| `spec` | สภาพที่ผู้ใช้/controller ต้องการ | schema ต่างกันตาม `kind` |
| `status` | สภาพจริง (actual state) ที่ controller/kubelet บันทึกกลับ | โดยทั่วไปไม่เขียนใน manifest และไม่กำหนดโดยตรงด้วย `apply` |

### ไวยากรณ์ที่ต้องทำความเข้าใจ

- เยื้องด้วย space อย่างสม่ำเสมอ; ชุดนี้ใช้ 2 ช่องต่อระดับ ห้ามใช้ tab
- `key: value` คือ mapping; หลัง `:` ต้องมีช่องว่างเมื่อมีค่า
- `-` ระบุสมาชิกของ list เช่น สมาชิกแต่ละรายการใน `containers` หรือ `ports`
- scalar มีชนิด string, number, boolean; schema Kubernetes กำหนดชนิดที่ field รับ
- environment variable ต้องเป็น string จึงต้อง quote ค่าที่มีรูปแบบคล้ายตัวเลข เช่น `"5432"` เพื่อมิให้ YAML ตีความเป็น number (ตัวอย่างเพิ่มเติมซึ่งไม่อยู่ในไฟล์ของปฏิบัติการ); หากเขียน `5432` จะพบ `json: cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string`
- `#` เริ่ม comment ถึงจบบรรทัด และไม่ถูกส่งให้ API
- `---` คั่นหลาย document; `005-labels-the-glue/01-pods-with-labels.yaml` มี Pod 3 object
- quote ไม่จำเป็นกับ string ธรรมดาทุกค่า; `"release v1"` ในไฟล์ Deployment เป็น string ชัดเจน

ให้ตรวจสอบตามลำดับก่อนดำเนินการ apply จริง:

```bash
kubectl apply --dry-run=client -f 01-pod.yaml
kubectl apply --dry-run=server -f 01-pod.yaml
kubectl explain pod.spec.containers.imagePullPolicy
kubectl get pod web -n lab004 -o yaml
```

`--dry-run=client` ตรวจสอบว่า YAML สามารถอ่านได้และรู้จัก kind แต่ไม่ตรวจ unknown field หรือชนิดของทุก field; `--dry-run=server` ส่งข้อมูลให้ API ตรวจ schema/admission โดยไม่บันทึก object; `explain` อ่าน schema ของ cluster; `get -o yaml` แสดง object จริงซึ่งมี default, status และ metadata ที่ระบบเพิ่มจากไฟล์ต้นฉบับ

ข้อผิดพลาดที่พบบ่อย: runlog ของปฏิบัติการ 004 มี `strict decoding error: unknown field "containers"` เมื่อวาง field ผิดระดับ (ตรวจพบด้วย server dry-run) และ `no matches for kind "Pods" in version "v1"` เมื่อเขียน kind ไม่ถูกต้อง โดยตรวจสอบระดับที่ถูกต้องได้ด้วย `kubectl explain pod.spec`

## Pod

Pod คือหน่วยที่ scheduler จัดวางบน node และเป็นขอบเขตที่ container หลายรายการใช้ network namespace ร่วมกัน ปฏิบัติการ 003 ใช้ sidecar พิสูจน์ว่าทั้งสองส่วนสื่อสารกันผ่าน loopback ได้

โครงจริงจาก `003-pod-the-smallest-unit/02-pod-with-sidecar.yaml`:

```yaml
apiVersion: v1                       # core API
kind: Pod                            # object ชนิด Pod
metadata:
  name: web2                         # ชื่อ Pod
  namespace: lab003                  # ห้อง lab003
  labels:
    app: web                         # label จัดกลุ่ม
spec:
  containers:                        # list มีสอง container
    - name: web                      # แอปหลัก
      image: k8s-lab-web:v1          # SkillSpace web v1
      imagePullPolicy: IfNotPresent  # ใช้ cache ก่อน
      ports:
        - containerPort: 3000        # แอปฟัง port 3000
    - name: sidecar                  # container ผู้ช่วย
      image: busybox:1.36.1
      imagePullPolicy: IfNotPresent
      command: ["sh", "-c"]         # แทน ENTRYPOINT
      args:                          # argument ของ command
        - while true; do
            wget -qO- http://127.0.0.1:3000/healthz;
            echo;
            sleep 10;
          done
```

| field | ค่าที่ใช้ได้ | ค่า default | ผลเมื่อเปลี่ยนหรือละเว้นค่า |
|---|---|---|---|
| `spec.containers[]` | list อย่างน้อย 1 รายการ | ไม่มี; required | ทุกรายการอยู่ใน Pod/node เดียวกันและใช้ IP/port space ร่วมกัน |
| `name` | ชื่อไม่ซ้ำใน Pod | ไม่มี; required | ใช้กับ `logs -c`; ซ้ำแล้ว validation ไม่ผ่าน |
| `image` | image reference | ไม่มี | tag ผิดมักเป็น `ErrImagePull`/`ImagePullBackOff` |
| `imagePullPolicy` | `Always`, `IfNotPresent`, `Never` | tag `latest`/ไม่มี tag → `Always`; tag อื่นหรือ digest → `IfNotPresent` | `Never` ต้องมี image ใน node; default ถูกกำหนดตอนสร้าง |
| `ports` / `ports[].containerPort` | สามารถละ list ได้; หากมีสมาชิก `containerPort` ต้องเป็น integer 1-65535 | `ports` ไม่มี; `containerPort` ไม่มีและ required ต่อสมาชิก | เป็นข้อมูลระบุตำแหน่งที่แอปรอรับการเชื่อมต่อ โดยไม่ได้เปิดช่องทางเข้าสู่ระบบโดยอัตโนมัติ |
| `env[]` / `envFrom[]` | รายตัว / นำเข้าหลายค่าจากแหล่งอ้างอิง | ไม่มี | `env` ชื่อซ้ำมีผลเหนือค่าจาก `envFrom`; ครั้งนี้เริ่มใช้ `env` ใน 007 |
| `command` / `args` | list string | ENTRYPOINT / CMD จาก image | เปลี่ยน process หลัก |
| `spec.restartPolicy` | `Always`, `OnFailure`, `Never` | `Always` | เป็นนโยบายระดับ Pod สำหรับ app container และแก้ภายหลังไม่ได้ |

ชื่อ `sidecar` ในไฟล์นี้ระบุ “บทบาทผู้ช่วย” แต่ในมุมมองของ API ยังคงเป็น app container ปกติใน `containers[]`; Kubernetes v1.36 มี ContainerRestartRules ระดับ container แบบ beta แต่ปฏิบัติการนี้ไม่ได้ใช้

Pod spec ส่วนใหญ่เป็น immutable หลังการสร้าง Runlog ของปฏิบัติการ 004 ระบุ field ที่แก้ไขได้ ได้แก่ `spec.containers[*].image`, `spec.initContainers[*].image`, `spec.activeDeadlineSeconds`, `spec.tolerations` (เพิ่มได้เท่านั้น) และ `spec.terminationGracePeriodSeconds` (กำหนดเป็น 1 ได้เมื่อค่าเดิมเป็นลบ); การเพิ่ม env ให้ Pod เดิมจึงถูกปฏิเสธและควรสร้าง Pod ใหม่ผ่าน controller ส่วน runlog 003 มี `Error: ImagePullBackOff` จาก tag ที่ไม่มีอยู่จริง ซึ่งตรวจสอบได้ด้วย `kubectl describe pod`

คำสั่งตรวจสอบ object จริง: `kubectl get pod web2 -n lab003 -o yaml` · `kubectl explain pod.spec.containers` · `kubectl explain pod.spec.restartPolicy`

## ReplicaSet

ReplicaSet รักษาจำนวน Pod โดยใช้ selector สำหรับนับสมาชิกและ template สำหรับสร้าง Pod ทดแทน

โครงจริงจาก `006-desired-state-and-self-healing/01-replicaset.yaml`:

```yaml
apiVersion: apps/v1                 # API group apps
kind: ReplicaSet                    # controller รักษาจำนวน Pod
metadata:
  name: web
spec:
  replicas: 3                       # desired Pod 3 ตัว
  selector:
    matchLabels:
      app: web                      # กฎนับสมาชิก
  template:                         # แม่พิมพ์ Pod ทั้งก้อน
    metadata:
      labels:
        app: web                    # ต้องตรง selector
        version: v1
    spec:
      containers:
        - name: web
          image: k8s-lab-web:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 3000
```

| field | ค่าที่ใช้ได้ | ค่า default | ผลเมื่อเปลี่ยนหรือละเว้นค่า |
|---|---|---|---|
| `spec.replicas` | integer ≥ 0 | `1` | เพิ่มหรือลดจำนวนในสภาพที่ต้องการ; 0 หยุด Pod ใต้ controller |
| `selector.matchLabels` | map label | ไม่มี; required และ immutable | ต้อง match label ใน template |
| `template.metadata.labels` | labels ของ Pod ใหม่ | ไม่มีค่าคงที่ | ต้องครอบคลุม selector |
| `template.spec` | PodSpec ทั้งหมด | ตาม default ของ Pod | field ภายในมีพฤติกรรมเช่นเดียวกับ field ของ Pod |

ข้อผิดพลาดที่พบบ่อยคือ selector ที่ไม่สอดคล้องกับ template ซึ่งจะไม่ผ่าน validation; ข้อความจริงคือ ``The ReplicaSet "web" is invalid: spec.template.metadata.labels: Invalid value: {"app":"webx"}: `selector` does not match template `labels` ``

ปฏิบัติการ 006 แสดงว่า ReplicaSet ไม่ดำเนินการ rolling update กล่าวคือ เมื่อเปลี่ยน template แล้ว Pod เดิมยังคงเป็น v1 จนกว่าจะลบ Pod หนึ่งรายการ จึงปรากฏ v1/v2 ร่วมกัน

แบบฝึกหัดกำหนดให้เปลี่ยน label เพื่อให้ Pod เดิมเป็น orphan และทำให้ ReplicaSet สร้างสมาชิกใหม่จนครบ โดยตรวจสอบด้วย `kubectl get pods -l app=web --show-labels` และ `kubectl describe rs`

คำสั่งตรวจสอบ object จริง: `kubectl get rs web -n lab006 -o yaml` · `kubectl explain replicaset.spec.selector` · `kubectl explain replicaset.spec.template`

## Deployment

Deployment เพิ่มกลไก revision และ rollout เหนือ ReplicaSet จึงสามารถเปลี่ยน version พร้อมกับรักษาจำนวน Pod ที่พร้อมทำงานได้

ตัวอย่างจาก `007-deployment-manages-change/01-deployment.yaml` (แสดงเฉพาะส่วนหลักโดยคงค่าตามไฟล์):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: lab007
  annotations:
    kubernetes.io/change-cause: "release v1" # เหตุผลของ revision
spec:
  replicas: 3
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
```

| field | ค่าที่ใช้ได้ | ค่า default | ผลเมื่อเปลี่ยนหรือละเว้นค่า |
|---|---|---|---|
| `replicas`, `selector`, `template` | หลักเดียวกับ ReplicaSet | replicas 1; selector required | Deployment สร้าง/ดูแล ReplicaSet; selector immutable |
| `strategy.type` | `RollingUpdate`, `Recreate` | `RollingUpdate` | Recreate ปิด Pod เดิมก่อน; RollingUpdate ทยอยสร้าง Pod ทดแทน |
| `rollingUpdate.maxSurge` | จำนวนหรือร้อยละ | `25%` | จำนวน Pod สูงสุดที่เพิ่มเกินจำนวนในสภาพที่ต้องการ; ค่าร้อยละปัดขึ้น |
| `rollingUpdate.maxUnavailable` | จำนวนหรือร้อยละ | `25%` | จำนวนที่ยอมให้ไม่พร้อม; ปัดลง และห้ามเป็น 0 พร้อม maxSurge 0 |
| `minReadySeconds` | integer ≥ 0 | `0` | เวลาที่ Pod ต้อง Ready ต่อเนื่องก่อนนับ Available |
| `revisionHistoryLimit` | integer ≥ 0 | `10` | จำนวน ReplicaSet เดิมที่บันทึกไว้สำหรับ rollback |
| annotation `kubernetes.io/change-cause` | string | ไม่มี | ทำให้ rollout history แสดงเหตุผล; อยู่ metadata Deployment ไม่ใช่ Pod template |

ไฟล์ไม่ได้ระบุ strategy/minReadySeconds/revisionHistoryLimit จึงใช้ default ข้างต้น ข้อผิดพลาดที่พบบ่อยคือการแก้ selector หลังสร้าง ซึ่งถูกปฏิเสธด้วย `spec.selector: Invalid value: {...}: field is immutable`; runlog 007 มี `error: timed out waiting for the condition` และ `ImagePullBackOff` เมื่อ rollout ไปยัง image v3 ที่ไม่มีอยู่จริง

คำสั่งตรวจสอบ object จริง: `kubectl get deployment web -n lab007 -o yaml` · `kubectl explain deployment.spec.strategy.rollingUpdate` · `kubectl rollout history deployment/web -n lab007`

## Downward API ด้วย fieldRef

เนื่องจากชื่อ Pod ถูกสร้างภายหลัง Downward API จึงนำ field ของ Pod ปัจจุบันเข้าสู่ environment variable โดยไม่กำหนดค่าแบบ hard-code
ตัวอย่างจาก `007-deployment-manages-change/01-deployment.yaml` มีดังนี้:

```yaml
env:
  - name: POD_NAME                 # environment variable ใน container
    valueFrom:
      fieldRef:
        fieldPath: metadata.name   # ชื่อ Pod ตอนรัน
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName   # node ที่ scheduler เลือก
```

| field | ค่าในครั้งนี้ | ค่า default | ผลเมื่อเปลี่ยนหรือละเว้นค่า |
|---|---|---|---|
| `env[].name` | `POD_NAME`, `NODE_NAME` | ไม่มี; required | ชื่อ environment variable ต้องตรงกับชื่อที่แอปอ้างอิง |
| `fieldRef.fieldPath` | `metadata.name`, `spec.nodeName` | ไม่มี; required | API จะปฏิเสธคำขอสร้าง object เมื่อกำหนด path ที่ไม่รองรับ; ค่าผูกกับแต่ละ Pod |
| `fieldRef.apiVersion` | ไม่เขียนในไฟล์ | `v1` | schema field selector v1 |

ข้อผิดพลาดที่พบบ่อย: การสลับ `value` กับ `valueFrom` หรือใช้ fieldPath ที่ไม่รองรับ; ตัวอย่างข้อความ (ไม่ได้มาจาก runlog) คือ `spec.containers[0].env[0].valueFrom.fieldRef.fieldPath: Invalid value: "metadata.whoops": error converting fieldPath: field label not supported: metadata.whoops` ซึ่ง API ปฏิเสธในขั้น create

คำสั่งตรวจสอบ object จริง: `kubectl get pod <ชื่อ-pod> -n lab007 -o yaml` · `kubectl explain pod.spec.containers.env.valueFrom.fieldRef`

## namespace ในไฟล์

ไฟล์ของปฏิบัติการ 006 ไม่ระบุ namespace จึงใช้ `kubectl apply -n lab006` ส่วน `007-deployment-manages-change/01-deployment.yaml` ระบุ `metadata.namespace: lab007` ไว้ใน object

| รูปแบบ | ผล |
|---|---|
| มี `metadata.namespace` | object อยู่ใน namespace ที่ระบุ และ `-n` ต้องสอดคล้องกัน |
| ไม่มี field แต่มี `-n lab006` | request ใช้ `lab006` |
| ไม่มีทั้งสอง | ใช้ namespace ของ current context ซึ่งมักเป็น `default` |

ข้อผิดพลาดที่พบบ่อย: ไฟล์ระบุ lab007 แต่กำหนด `-n lab006`; ตัวอย่างข้อความ (ไม่ได้มาจาก runlog) คือ `the namespace from the provided object "lab007" does not match the namespace "lab006"` ตรวจสอบด้วย `kubectl config view --minify`

คำสั่งตรวจสอบ schema: `kubectl explain deployment.metadata.namespace`

## Service และ Ingress

`door.yaml` เป็น manifest ที่เตรียมไว้สำหรับสร้างช่องทางเข้าถึงระบบและสังเกต self-healing/rollout ผ่าน request การสอนครั้งนี้พิจารณาเฉพาะ `Ingress → Service → Pod`; Service จะศึกษาโดยละเอียดในการสอนครั้งที่ 2 และ Ingress ในครั้งที่ 3

จาก `006-desired-state-and-self-healing/02-door.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web                       # เลือก Pod app=web
  ports:
    - port: 3000                  # port ของ Service
      targetPort: 3000            # ส่งเข้า container port
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
spec:
  ingressClassName: nginx          # nginx controller รับผิดชอบ
  rules:
    - http:                        # ไม่กำหนด host: รับทุก host
        paths:
          - path: /
            pathType: Prefix       # path ที่ขึ้นต้นด้วย /
            backend:
              service:
                name: web          # ไป Service web
                port:
                  number: 3000     # port ของ Service
```

Service ไม่ระบุ `type` จึงใช้ default `ClusterIP` และไม่ระบุ `protocol` จึงใช้ default `TCP`; Ingress `pathType` ไม่มี default และต้องระบุ ส่วน `ingressClassName` field นี้ไม่มีค่า default (admission อาจเพิ่มค่าจาก default IngressClass)

ข้อผิดพลาดที่พบบ่อย: selector ที่ไม่สอดคล้องกันทำให้ EndpointSlice ว่าง และ targetPort ที่มีชื่อไม่ตรงกับ Pod ทำให้ไม่สามารถส่งต่อข้อมูลได้ ตรวจสอบด้วย `kubectl describe service`/`kubectl get endpointslice`; สำหรับ Ingress ให้ตรวจสอบด้วย `kubectl describe ingress`

คำสั่งตรวจสอบ object จริง: `kubectl get service,ingress -n lab006 -o yaml` · `kubectl explain service.spec.ports` · `kubectl explain ingress.spec.rules.http.paths`

## ตารางสรุป field ของครั้งนี้

| field | object | ปฏิบัติการแรกที่ศึกษา |
|---|---|---:|
| `apiVersion`, `kind`, `metadata`, `spec`, `status` | ทุก object | 004 |
| `name`, `labels`, `annotations`, `namespace` | ทุก object | 004/007 |
| `containers`, `image`, `imagePullPolicy`, `ports`, `command`, `args`, `env` | Pod/template | 003/007 |
| `restartPolicy` และ immutability | Pod | 004 |
| `replicas`, `selector.matchLabels`, `template` | ReplicaSet | 006 |
| `strategy`, `minReadySeconds`, `revisionHistoryLimit`, change cause | Deployment | 007 |
| `valueFrom.fieldRef.fieldPath` | Downward API | 007 |
| `selector`, `ports`, `rules`, `pathType`, `backend` | Service/Ingress (ภาพรวม) | 006 |

**ภาพรวมที่ควรจดจำ:** YAML คือคำประกาศสภาพที่ต้องการ; API ตรวจสอบโครงสร้าง จากนั้น controller เพิ่ม `status` และทำให้สภาพจริงเข้าใกล้ `spec` — หากไม่ทราบ field ให้ตรวจสอบด้วย `kubectl explain`
