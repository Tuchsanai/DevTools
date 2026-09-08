# คู่มือ YAML ครั้งที่ 1 — อ่าน desired state ให้เห็นภาพ
> อ่านคู่กับแล็บ 001-007 · ทุกตัวอย่างคัดจากไฟล์จริงในโฟลเดอร์แล็บของครั้งนี้

คู่มือนี้ไม่ต้องท่องจำ ให้ถามทีละชั้นว่า “object ชนิดอะไร อยู่ห้องไหน และสั่งให้ระบบรักษาสภาพใด?” แล้วใช้ `kubectl explain` เมื่อต้องการดู schema

## อ่าน YAML ให้เป็น

YAML เป็นรูปแบบข้อมูล ส่วน Kubernetes API เป็นผู้ตรวจว่า field ตรง schema ของ object หรือไม่ ดังนั้น YAML ที่เยื้องถูกก็ยังผิด schema ได้

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

| ส่วน | อ่านอย่างไร | ถ้าเปลี่ยนหรือลืม |
|---|---|---|
| `apiVersion` | `v1` คือ core group; `apps/v1` คือ group `apps` version `v1` | group/version ไม่รองรับจะหา resource mapping ไม่พบ; ดูด้วย `kubectl api-resources` |
| `kind` | ชนิด เช่น `Pod`, `ReplicaSet`, `Deployment` | ตัวพิมพ์หรือชื่อผิด API ไม่รู้จัก |
| `metadata.name` | ชื่อไม่ซ้ำภายใน kind และ namespace เดียวกัน | เปลี่ยนชื่อคือชี้คนละ object ไม่ใช่ rename |
| `metadata.namespace` | ห้องของ namespaced object | ถ้าไม่เขียน ใช้ namespace ของ request/context; ค่าในไฟล์ต้องไม่ขัดกับ `-n` |
| `metadata.labels` | string key/value ที่ selector ใช้จัดกลุ่ม | เปลี่ยนแล้ว membership เปลี่ยนทันที |
| `metadata.annotations` | ข้อมูลประกอบที่ไม่ใช้เลือกสมาชิก | เหมาะกับ change cause ไม่ใช่ identity ของกลุ่ม |
| `spec` | สภาพที่ผู้ใช้/controller ต้องการ | schema ต่างกันตาม `kind` |
| `status` | สภาพจริงที่ controller/kubelet เขียนกลับ | ปกติไม่เขียนใน manifest และไม่ใช้ `apply` สั่งโดยตรง |

### ไวยากรณ์ที่ต้องอ่านออก

- เยื้องด้วย space อย่างสม่ำเสมอ; ชุดนี้ใช้ 2 ช่องต่อระดับ ห้ามใช้ tab
- `key: value` คือ mapping; หลัง `:` ต้องมีช่องว่างเมื่อมีค่า
- `-` เปิดสมาชิก list เช่นแต่ละตัวใน `containers` หรือ `ports`
- scalar มีชนิด string, number, boolean; schema Kubernetes กำหนดชนิดที่ field รับ
- environment variable ต้องเป็น string จึงต้อง quote ค่าหน้าตาเหมือนเลข เช่น `"5432"` ไม่ให้ YAML ตีความเป็น number (ตัวอย่างเพิ่มเติม ไม่อยู่ในไฟล์ของแล็บ); ถ้าเขียน `5432` จะพบ `json: cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string`
- `#` เริ่ม comment ถึงจบบรรทัด และไม่ถูกส่งให้ API
- `---` คั่นหลาย document; `005-labels-the-glue/01-pods-with-labels.yaml` มี Pod 3 object
- quote ไม่จำเป็นกับ string ธรรมดาทุกค่า; `"release v1"` ในไฟล์ Deployment เป็น string ชัดเจน

ตรวจเป็นชั้นก่อน apply จริง:

```bash
kubectl apply --dry-run=client -f 01-pod.yaml
kubectl apply --dry-run=server -f 01-pod.yaml
kubectl explain pod.spec.containers.imagePullPolicy
kubectl get pod web -n lab004 -o yaml
```

`--dry-run=client` ตรวจว่า YAML อ่านได้และรู้จัก kind แต่ไม่ตรวจ unknown field หรือชนิดของทุก field; `--dry-run=server` ส่งให้ API ตรวจ schema/admission โดยไม่บันทึก object; `explain` อ่าน schema ของ cluster; `get -o yaml` แสดง object จริงซึ่งมี default, status และ metadata ที่ระบบเติมมากกว่าไฟล์ต้นฉบับ

ผิดบ่อย: runlog แล็บ 004 มี `strict decoding error: unknown field "containers"` เมื่อวาง field ผิดระดับ (ตรวจพบด้วย server dry-run) และ `no matches for kind "Pods" in version "v1"` เมื่อเขียน kind ผิด ดูระดับที่ถูกด้วย `kubectl explain pod.spec`

## Pod

Pod คือหน่วยที่ scheduler วางลง node และเป็นขอบเขตที่หลาย container แชร์ network namespace เดียวกัน แล็บ 003 ใช้ sidecar พิสูจน์ว่าทั้งคู่เรียกกันผ่าน loopback ได้

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

| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืม |
|---|---|---|---|
| `spec.containers[]` | list อย่างน้อย 1 ตัว | ไม่มี; required | ทุกตัวอยู่ Pod/node เดียวกันและแชร์ IP/port space |
| `name` | ชื่อไม่ซ้ำใน Pod | ไม่มี; required | ใช้กับ `logs -c`; ซ้ำแล้ว validation ไม่ผ่าน |
| `image` | image reference | ไม่มี | tag ผิดมักเป็น `ErrImagePull`/`ImagePullBackOff` |
| `imagePullPolicy` | `Always`, `IfNotPresent`, `Never` | tag `latest`/ไม่มี tag → `Always`; tag อื่นหรือ digest → `IfNotPresent` | `Never` ต้องมี image ใน node; default ถูกกำหนดตอนสร้าง |
| `ports` / `ports[].containerPort` | ไม่เขียน list ก็ได้; ถ้ามีสมาชิก `containerPort` ต้องเป็น integer 1-65535 | `ports` ไม่มี; `containerPort` ไม่มีและ required ต่อสมาชิก | เป็นข้อมูลว่าแอปฟังที่ใด ไม่ได้เปิดทางเข้าเอง |
| `env[]` / `envFrom[]` | รายตัว / นำเข้าหลายค่าจากแหล่งอ้างอิง | ไม่มี | `env` ชื่อซ้ำมีผลเหนือค่าจาก `envFrom`; ครั้งนี้เริ่มใช้ `env` ใน 007 |
| `command` / `args` | list string | ENTRYPOINT / CMD จาก image | เปลี่ยน process หลัก |
| `spec.restartPolicy` | `Always`, `OnFailure`, `Never` | `Always` | เป็นนโยบายระดับ Pod สำหรับ app container และแก้ภายหลังไม่ได้ |

ชื่อ `sidecar` ในไฟล์นี้บอก “บทบาทผู้ช่วย” แต่ทาง API ยังเป็น app container ปกติใน `containers[]`; Kubernetes v1.36 มี ContainerRestartRules ระดับ container แบบ beta แต่แล็บนี้ไม่ได้ใช้

Pod spec ส่วนใหญ่ immutable หลังสร้าง Runlog แล็บ 004 ระบุ field ที่แก้ได้ว่า `spec.containers[*].image`, `spec.initContainers[*].image`, `spec.activeDeadlineSeconds`, `spec.tolerations` (เพิ่มได้อย่างเดียว) และ `spec.terminationGracePeriodSeconds` (ตั้งเป็น 1 ได้เมื่อค่าเดิมติดลบ); เมื่อเพิ่ม env ให้ Pod เดิมจึงถูกปฏิเสธ ควรสร้าง Pod ใหม่ผ่าน controller ส่วน runlog 003 มี `Error: ImagePullBackOff` จาก tag ที่ไม่มีจริง ดูด้วย `kubectl describe pod`

คำสั่งดูของจริง: `kubectl get pod web2 -n lab003 -o yaml` · `kubectl explain pod.spec.containers` · `kubectl explain pod.spec.restartPolicy`

## ReplicaSet

ReplicaSet รักษาจำนวน Pod ด้วย selector สำหรับนับสมาชิก และ template สำหรับสร้างตัวแทน

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

| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืม |
|---|---|---|---|
| `spec.replicas` | integer ≥ 0 | `1` | เพิ่ม/ลด desired count; 0 หยุด Pod ใต้ controller |
| `selector.matchLabels` | map label | ไม่มี; required และ immutable | ต้อง match label ใน template |
| `template.metadata.labels` | labels ของ Pod ใหม่ | ไม่มีค่าตายตัว | ต้องครอบ selector |
| `template.spec` | PodSpec ทั้งก้อน | ตาม default ของ Pod | field ข้างในทำงานเหมือน Pod |

ผิดบ่อย: selector กับ template ไม่ตรงจะไม่ผ่าน validation; ข้อความจริงคือ ``The ReplicaSet "web" is invalid: spec.template.metadata.labels: Invalid value: {"app":"webx"}: `selector` does not match template `labels` `` แล็บ 006 แสดงว่า ReplicaSet ไม่ทำ rolling update: เปลี่ยน template แล้ว Pod เก่ายังเป็น v1 จนลบหนึ่งตัว จึงเห็น v1/v2 ปนกัน; exercise เปลี่ยน label ให้ Pod เดิมเป็น orphan แล้ว ReplicaSet สร้างสมาชิกใหม่ให้ครบ ตรวจด้วย `kubectl get pods -l app=web --show-labels` และ `kubectl describe rs`

คำสั่งดูของจริง: `kubectl get rs web -n lab006 -o yaml` · `kubectl explain replicaset.spec.selector` · `kubectl explain replicaset.spec.template`

## Deployment

Deployment เพิ่ม revision และ rollout เหนือ ReplicaSet จึงเปลี่ยน version โดยรักษาจำนวน Pod ที่พร้อมได้

จาก `007-deployment-manages-change/01-deployment.yaml` (ตัดส่วนหลัก แต่ค่าตรงไฟล์):

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

| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืม |
|---|---|---|---|
| `replicas`, `selector`, `template` | หลักเดียวกับ ReplicaSet | replicas 1; selector required | Deployment สร้าง/ดูแล ReplicaSet; selector immutable |
| `strategy.type` | `RollingUpdate`, `Recreate` | `RollingUpdate` | Recreate ปิด Pod เก่าก่อน; RollingUpdate ค่อยแทน |
| `rollingUpdate.maxSurge` | จำนวนหรือร้อยละ | `25%` | เพดานที่เกิน desired; ค่าร้อยละปัดขึ้น |
| `rollingUpdate.maxUnavailable` | จำนวนหรือร้อยละ | `25%` | จำนวนที่ยอมให้ไม่พร้อม; ปัดลง และห้ามเป็น 0 พร้อม maxSurge 0 |
| `minReadySeconds` | integer ≥ 0 | `0` | เวลาที่ Pod ต้อง Ready ต่อเนื่องก่อนนับ Available |
| `revisionHistoryLimit` | integer ≥ 0 | `10` | จำนวน ReplicaSet เก่าที่เก็บสำหรับ rollback |
| annotation `kubernetes.io/change-cause` | string | ไม่มี | ให้ rollout history บอกเหตุผล; อยู่ metadata Deployment ไม่ใช่ Pod template |

ไฟล์ไม่ได้เขียน strategy/minReadySeconds/revisionHistoryLimit จึงใช้ default ข้างบน ผิดบ่อยคือแก้ selector หลังสร้างแล้วถูกปฏิเสธด้วย `spec.selector: Invalid value: {...}: field is immutable`; runlog 007 มี `error: timed out waiting for the condition` และ `ImagePullBackOff` เมื่อ rollout ไป image v3 ที่ไม่มีจริง

คำสั่งดูของจริง: `kubectl get deployment web -n lab007 -o yaml` · `kubectl explain deployment.spec.strategy.rollingUpdate` · `kubectl rollout history deployment/web -n lab007`

## Downward API ด้วย fieldRef

ชื่อ Pod ถูกสร้างทีหลัง Downward API จึงนำ field ของ Pod ปัจจุบันเข้า environment variable โดยไม่ hard-code จาก `007-deployment-manages-change/01-deployment.yaml`:

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

| field | ค่าในครั้งนี้ | ค่า default | ถ้าเปลี่ยน/ลืม |
|---|---|---|---|
| `env[].name` | `POD_NAME`, `NODE_NAME` | ไม่มี; required | แอปต้องอ่านชื่อตรงกัน |
| `fieldRef.fieldPath` | `metadata.name`, `spec.nodeName` | ไม่มี; required | path ไม่รองรับทำให้ API ปฏิเสธตอน create; ค่าผูกกับแต่ละ Pod |
| `fieldRef.apiVersion` | ไม่เขียนในไฟล์ | `v1` | schema field selector v1 |

ผิดบ่อย: สลับ `value` กับ `valueFrom` หรือใช้ fieldPath ที่ไม่รองรับ; ตัวอย่างข้อความ (ไม่ได้มาจาก runlog) คือ `spec.containers[0].env[0].valueFrom.fieldRef.fieldPath: Invalid value: "metadata.whoops": error converting fieldPath: field label not supported: metadata.whoops` ซึ่ง API ปฏิเสธตอน create

คำสั่งดูของจริง: `kubectl get pod <ชื่อ-pod> -n lab007 -o yaml` · `kubectl explain pod.spec.containers.env.valueFrom.fieldRef`

## namespace ในไฟล์

ไฟล์แล็บ 006 ไม่เขียน namespace จึงใช้ `kubectl apply -n lab006` ส่วน `007-deployment-manages-change/01-deployment.yaml` พก `metadata.namespace: lab007` มากับ object

| รูปแบบ | ผล |
|---|---|
| มี `metadata.namespace` | object ไปห้องนั้น และ `-n` ต้องตรง |
| ไม่มี field แต่มี `-n lab006` | request ใช้ `lab006` |
| ไม่มีทั้งสอง | ใช้ namespace ของ current context ซึ่งมักเป็น `default` |

ผิดบ่อย: ไฟล์ระบุ lab007 แต่สั่ง `-n lab006`; ตัวอย่างข้อความ (ไม่ได้มาจาก runlog) คือ `the namespace from the provided object "lab007" does not match the namespace "lab006"` ตรวจด้วย `kubectl config view --minify`

คำสั่งดู schema: `kubectl explain deployment.metadata.namespace`

## Service และ Ingress

`door.yaml` เป็น “ประตูสำเร็จรูป” เพื่อดู self-healing/rollout ผ่าน request ครั้งนี้อ่านเพียง `Ingress → Service → Pod`; Service จะเรียนละเอียดครั้งที่ 2 และ Ingress ครั้งที่ 3

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

Service ไม่เขียน `type` จึง default `ClusterIP` และไม่เขียน `protocol` จึง default `TCP`; Ingress `pathType` ไม่มี default และต้องระบุ ส่วน `ingressClassName` ไม่มี default ที่ field (admission อาจเติมจาก default IngressClass)

ผิดบ่อย: selector ไม่ตรงทำให้ EndpointSlice ว่าง และ targetPort ชื่อไม่ตรง Pod ทำให้ส่งต่อไม่ได้ ตรวจ `kubectl describe service`/`kubectl get endpointslice`; Ingress ตรวจ `kubectl describe ingress`

คำสั่งดูของจริง: `kubectl get service,ingress -n lab006 -o yaml` · `kubectl explain service.spec.ports` · `kubectl explain ingress.spec.rules.http.paths`

## ตารางสรุป field ของครั้งนี้

| field | object | แล็บแรกที่อ่าน |
|---|---|---:|
| `apiVersion`, `kind`, `metadata`, `spec`, `status` | ทุก object | 004 |
| `name`, `labels`, `annotations`, `namespace` | ทุก object | 004/007 |
| `containers`, `image`, `imagePullPolicy`, `ports`, `command`, `args`, `env` | Pod/template | 003/007 |
| `restartPolicy` และ immutability | Pod | 004 |
| `replicas`, `selector.matchLabels`, `template` | ReplicaSet | 006 |
| `strategy`, `minReadySeconds`, `revisionHistoryLimit`, change cause | Deployment | 007 |
| `valueFrom.fieldRef.fieldPath` | Downward API | 007 |
| `selector`, `ports`, `rules`, `pathType`, `backend` | Service/Ingress (ภาพรวม) | 006 |

**จำภาพเดียวให้ได้:** YAML คือคำประกาศ desired state; API ตรวจโครง แล้ว controller เติม `status` และทำให้สภาพจริงเข้าใกล้ `spec` — ถ้าจำ field ไม่ได้ ให้ถาม `kubectl explain`
