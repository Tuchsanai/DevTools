# คู่มือ YAML ครั้งที่ 2 — Networking, Config & Storage

> อ่านคู่กับแล็บ 008–014 · ทุกตัวอย่างคัดจากไฟล์จริงในโฟลเดอร์แล็บของครั้งนี้ และระบุไฟล์ต้นทางไว้เสมอ
## 0. อ่าน YAML ให้เป็น (สรุป)

1. `apiVersion` เลือก API group/version ส่วน `kind` บอกชนิด object ที่จะสร้าง
2. `metadata` ระบุชื่อ, namespace, labels และข้อมูลกำกับของ object
3. `spec` คือสภาพที่เราต้องการ ส่วน `status` คือสภาพจริงที่ controller เขียนกลับ
4. YAML ใช้ย่อหน้าและ `-` สร้างโครงต้นไม้ จึงต้องอ่าน parent ของ field ให้ถูก
5. คู่มือ YAML ครั้งที่ 1 มีฉบับเต็มเรื่อง syntax, โครง object และวิธีใช้ `kubectl explain`; ครั้งนี้ต่อยอดจากพื้นฐานนั้น
## Deployment

**ทบทวน:** Deployment คุมจำนวนและการเปลี่ยนรุ่นของ Pod; ดูไฟล์เต็มและทดลองได้ใน [LAB 008](008-why-we-need-service/README.md)
YAML ย่อจาก `008-why-we-need-service/02-api.yaml`:

```yaml
apiVersion: apps/v1              # API group/version ของ Deployment
kind: Deployment                 # controller ที่ดูแล Pod
metadata:
  name: api                      # ชื่อ Deployment
spec:
  replicas: 2                    # ต้องการ API 2 Pod
  selector:                      # ต้องตรงกับ labels ใต้ template
    matchLabels:
      app: api                   # label ที่ Deployment ใช้เลือก Pod
  template:                      # แม่แบบของ Pod ที่จะสร้าง
```
field สำคัญคือ `replicas`, `selector.matchLabels`, `template`, และ `strategy`; ไฟล์นี้ไม่ระบุ `strategy` จึงใช้ `RollingUpdate`
## Ingress

**ทบทวน:** Ingress เป็น “ประตู” ที่ route HTTP จากภายนอกไป Service; ดูไฟล์เต็มและทดลองได้ใน [LAB 008](008-why-we-need-service/README.md) · YAML ย่อจาก `008-why-we-need-service/01-web.yaml`:

```yaml
kind: Ingress                    # กฎทางเข้า HTTP
spec:
  ingressClassName: nginx        # ให้ nginx controller รับกฎนี้
  rules:                         # ไม่ใส่ host จึงรับทุก host
    - http:
        paths:
          - path: /              # URL ที่เริ่มจับคู่
            pathType: Prefix     # จับคู่ตาม prefix; ต้องระบุ
            backend:
              service:
                name: web        # Service ปลายทาง
                port:
                  number: 3000   # พอร์ตของ Service
```
field สำคัญคือ `ingressClassName`, `rules[].http.paths[].path`, `pathType`, และ `backend.service`; LAB 008 ใช้เป็นประตูสำเร็จรูป
## Service

Service แก้ปัญหา Pod IP เปลี่ยน โดยให้ virtual IP และชื่อ DNS คงที่ แล้วเลือก Pod ปลายทางจาก label นักศึกษาจึงควรถามทุกครั้งว่า “Service เลือกใคร รับที่พอร์ตใด และส่งไปพอร์ตใด”
โครงจริงจาก `008-why-we-need-service/04-api-service.yaml`:

```yaml
apiVersion: v1              # API version ของ Service
kind: Service               # ปลายทางคงที่หน้า Pod
metadata:
  name: api                 # ชื่อสั้นที่ Pod ใน namespace เดียวกันใช้เรียก
  namespace: lab008         # namespace ของ Service
spec:
  selector:                 # map สำหรับเลือก Pod
    app: api                # เลือก Pod ที่มี label app=api
  ports:                    # รายการพอร์ตที่ Service เปิด
    - name: http            # ตั้งชื่อพอร์ตเพื่อให้อ้างอิงได้
      port: 8000            # พอร์ตของ Service
      targetPort: http      # ส่งไป container port ชื่อ http
```
`type` ไม่ปรากฏในไฟล์นี้ จึงใช้ค่า default `ClusterIP` ส่วน NodePort จริงอยู่ใน `009-service-types-and-access/02-web-nodeport.yaml`:

```yaml
spec:
  type: NodePort        # เปิดเพิ่มผ่านพอร์ตบนทุก Node
  selector:
    app: web            # เลือก Pod web
  ports:
    - port: 3000        # พอร์ตของ Service
      targetPort: http  # ชื่อ container port ปลายทาง
      nodePort: 30080   # พอร์ตภายนอกในช่วงที่ cluster กำหนด
```
| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืมจะเกิดอะไร |
|---|---|---|---|
| `spec.type` | `ClusterIP`, `NodePort`, `LoadBalancer`, `ExternalName` | `ClusterIP` | `NodePort` เพิ่มทางเข้าที่พอร์ตของทุก Node; `LoadBalancer` ขอ load balancer จากระบบที่รองรับ |
| `spec.selector` | map ของ label | ไม่มี | selector ไม่ตรงทำให้ Service มี endpoint ว่าง แม้ Pod ยัง Running |
| `spec.ports[].port` | เลข 1–65535 | ไม่มี ต้องระบุ | เป็นพอร์ตที่ client เรียกบน Service |
| `targetPort` | เลขหรือชื่อ port ของ Pod | เท่ากับ `port` | ชื่อที่ไม่มีใน Pod ทำให้ส่ง traffic ไปไม่ถึง |
| `nodePort` | โดยปกติ 30000–32767 หรือปล่อยให้ระบบเลือก | ระบบจัดสรร | ระบุนอกช่วงหรือซ้ำจะถูก API server ปฏิเสธ |
| `protocol` | `TCP`, `UDP`, `SCTP` | `TCP` | ต้องตรงกับ protocol ที่ปลายทางใช้ |
DNS ภายใน cluster มีรูปเต็ม `<service>.<namespace>.svc.<cluster-domain>`; ในแล็บนี้คือ `api.lab008.svc.cluster.local` เพราะ cluster domain คือ `cluster.local`
Pod ใน `lab008` เรียกสั้น ๆ ว่า `api` ได้ ส่วน Pod ต่าง namespace ใช้ `api.lab008` หรือชื่อเต็ม
EndpointSlice ถูก controller สร้างและอัปเดตจาก Pod ที่ตรง `selector`; Service ไม่ได้ “เก็บ Pod IP ไว้ตายตัว” หาก selector ผิด EndpointSlice จะไม่มีปลายทางโดยไม่มี YAML validation error ใช้ `kubectl get endpointslice -l kubernetes.io/service-name=api`; ส่วน `kubectl get endpoints api` ยังดูได้แต่แสดง Warning ว่า Endpoints deprecated ตั้งแต่ v1.33
**ผิดบ่อย:** runlog ของ LAB 009 บันทึกข้อความจริง `provided port is not in the valid range. The range of valid ports is 30000-32767` และ `provided port is already allocated` จาก `03-nodeport-bad.yaml` ส่วน selector ผิดใน LAB 008 apply ได้ แต่หน้าเว็บตอบ `"error":"fetch failed"`; ให้ดู `kubectl describe service api` และ EndpointSlice
คำสั่งดูของจริง:
```bash
kubectl get service api -n lab008 -o yaml
kubectl get endpointslice -n lab008 -l kubernetes.io/service-name=api
kubectl explain service.spec.ports
```
## ConfigMap

ConfigMap แยกค่าที่ไม่ลับออกจาก image ทำให้ image เดียวใช้ config ต่างกันได้ การเลือก `envFrom`, `configMapKeyRef` หรือ mount เป็นไฟล์ขึ้นกับว่าโปรแกรมต้องการอ่านค่าแบบใด
โครงจริงจาก `010-configmap-separate-config/02-configmap.yaml`:

```yaml
apiVersion: v1             # API version ของ ConfigMap
kind: ConfigMap            # object สำหรับ config ที่ไม่ลับ
metadata:
  name: web-config         # ชื่อที่ workload ใช้อ้าง
  namespace: lab010       # ต้องอยู่ namespace เดียวกับ Pod
data:                     # map ที่ทุก value เป็น string
  SITE_NAME: "ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์" # ข้อความจึงใส่ quote
  THEME: amber            # ค่า theme ของเว็บ
```
การนำทุก key เข้า environment จริงจาก `010-configmap-separate-config/03-web-envfrom.yaml`:

```yaml
containers:                       # อยู่ใต้ spec.template.spec
  - name: web                     # container ที่รับค่า config
    image: k8s-lab-web:v1         # image จริงของแล็บ
    # ... imagePullPolicy และ ports อยู่ตรงนี้ในไฟล์จริง
    envFrom:                      # นำทุก key เข้า environment
      - configMapRef:
          name: web-config        # ConfigMap ใน namespace เดียวกัน
```
| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืมจะเกิดอะไร |
|---|---|---|---|
| `data` | map ที่ value เป็น string | ไม่มี | quote ค่าที่ YAML อาจตีความเป็น number/bool; ConfigMap ไม่ใช่ที่เก็บ secret |
| `envFrom[].configMapRef.name` | ชื่อ ConfigMap namespace เดียวกัน | ไม่มี | ทุก key ที่เป็นชื่อ env ที่ถูกต้องถูกนำเข้า container |
| `env[].valueFrom.configMapKeyRef` | `name` + `key` | ไม่มี | เลือกเพียง key เดียวและตั้งชื่อ env ฝั่ง container ใหม่ได้ |
| `optional` ใน ref | `true`/`false` | `false` | ถ้าเป็น `false` แล้ว object/key ไม่มี Container จะเริ่มไม่ได้ |
| ConfigMap volume | ชื่อ ConfigMap + path ของ volume | ไม่มี | แต่ละ key กลายเป็นไฟล์; การอัปเดตมาถึงภายหลัง แต่โปรแกรมต้อง reload เอง |
`configMapKeyRef` และ ConfigMap volume เป็นกลไกที่อธิบายเพิ่ม แต่ไม่มี YAML ตัวอย่างในไฟล์ของ LAB 010 จึงไม่สร้าง snippet สมมุติขึ้นมา สำหรับ `envFrom` ค่าเปลี่ยนจะไม่ไหลเข้า environment ของ container เดิม ต้องสร้าง Pod ใหม่ เช่น `kubectl rollout restart deployment/web`; volume จะอัปเดตไฟล์ภายหลัง ยกเว้น mount ผ่าน `subPath`
**ผิดบ่อย:** runlog ของ LAB 010 บันทึก Pod เป็น `CreateContainerConfigError` และ Event จริง `Error: configmap "web-confg" not found` เมื่อสะกดชื่อผิด อีกกรณีคือ apply ConfigMap ใหม่แล้วคาดว่า environment ของ Container เดิมจะเปลี่ยน—กรณีนี้ไม่มี error และต้องสร้าง Pod ใหม่
คำสั่งดูของจริง:
```bash
kubectl get configmap web-config -n lab010 -o yaml
kubectl explain configmap.data
kubectl explain deployment.spec.template.spec.containers.envFrom.configMapRef
```
## Secret

Secret แยกข้อมูลที่ต้องควบคุมสิทธิ์ออกจาก manifest ของ workload แต่ base64 เป็นเพียง encoding ไม่ใช่ encryption ห้าม commit credential จริง และควรเปิด encryption at rest/RBAC ตามนโยบายของระบบจริง
โครงจริงจาก `011-secret-and-why-not-configmap/01-secret.yaml`:

```yaml
apiVersion: v1             # API version ของ Secret
kind: Secret               # object สำหรับข้อมูลที่ควบคุมสิทธิ์
metadata:
  name: db-secret          # ชื่อที่ Pod ใช้อ้าง
  namespace: lab011       # namespace เดียวกับ Pod
type: Opaque              # Secret key/value ทั่วไป
stringData:               # API server encode เป็น base64 ให้
  POSTGRES_PASSWORD: labpass # ค่าสมมุติสำหรับห้องเรียน
```
การอ่าน key เดียวจริงจาก `011-secret-and-why-not-configmap/03-api.yaml`:

```yaml
containers:                         # อยู่ใต้ spec.template.spec
  - name: api                       # container ผู้ใช้ Secret
    # ... image, ports และ env อื่นอยู่ตรงนี้ในไฟล์จริง
    env:
      - name: DB_PASSWORD           # ชื่อ environment ฝั่ง API
        valueFrom:
          secretKeyRef:
            name: db-secret         # Secret ใน namespace เดียวกัน
            key: POSTGRES_PASSWORD  # key ที่ต้องมีอยู่จริง
```
| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืมจะเกิดอะไร |
|---|---|---|---|
| `type` | `Opaque` หรือชนิดเฉพาะ เช่น TLS | `Opaque` เมื่อเว้นว่าง | ชนิดเฉพาะอาจมีการตรวจ key ที่จำเป็น |
| `stringData` | map ของข้อความที่เขียนง่าย | ไม่มี | API server รวมลง `data`; key ซ้ำกับ `data` ให้ `stringData` ชนะ |
| `data` | map ของ byte ที่ encode เป็น base64 | ไม่มี | `kubectl get -o yaml` แสดง base64 ซึ่งถอดกลับได้ ไม่ใช่การเข้ารหัส |
| `secretKeyRef.name/key` | ชื่อ Secret และ key | ไม่มี | object/key ไม่มีและไม่ optional ทำให้ Container เริ่มไม่ได้ |
| `envFrom[].secretRef` | นำทุก key เข้า env | ไม่มี | สะดวกแต่กระจาย secret กว้างกว่าเลือกทีละ key |
`envFrom.secretRef` เป็นกลไกที่กล่าวถึงเพิ่มและไม่มีใน manifest ของ LAB 011 ตัวอย่างจริงจึงใช้ `secretKeyRef` เท่านั้น Secret ที่ใช้ผ่าน environment มี snapshot ตอน Container เริ่มเหมือน ConfigMap; เปลี่ยน Secret แล้วต้องสร้าง Pod ใหม่เพื่อให้ env เปลี่ยน
**ผิดบ่อย:** `secretKeyRef.name` หรือ `key` ผิดทำให้ Pod เป็น `CreateContainerConfigError`; ใช้ `kubectl describe pod` ดูว่า Secret/key ใดหาไม่พบ และ `data:` ที่ใส่ข้อความซึ่งไม่ใช่ base64 ถูกปฏิเสธด้วย `illegal base64 data at input byte ...` อีกกรณีคือ Secret ของ API กับ db ไม่ตรงกัน แม้ YAML apply ผ่าน แต่ runlog LAB 011 มี `FATAL: password authentication failed for user "opsuser"`
คำสั่งดูของจริง:
```bash
kubectl get secret db-secret -n lab011 -o yaml
kubectl explain secret.stringData
kubectl explain deployment.spec.template.spec.containers.env.valueFrom.secretKeyRef
```
## Volume-PVC

Volume ผูกพื้นที่เก็บข้อมูลเข้ากับ Pod ส่วน `volumeMounts` บอกจุดที่ Container มองเห็น ชื่อทั้งสองฝั่งต้องตรงกัน LAB 012 ใช้ `emptyDir` เพื่อพิสูจน์อายุเท่า Pod และ LAB 013 เปลี่ยน source เป็น PVC เพื่อให้อายุข้อมูลแยกจาก Pod
ส่วน `spec.template.spec` จริงจาก `012-why-data-disappears/02-db-emptydir.yaml`:

```yaml
containers:                              # รายการ container ของ Pod
  - name: db                             # container PostgreSQL
    # ... image, ports และ env อื่นอยู่ตรงนี้ในไฟล์จริง
    env:
      - name: PGDATA                     # data directory ของ PostgreSQL
        value: /var/lib/postgresql/data/pgdata # subdirectory ใต้ mount
    volumeMounts:                        # mount อยู่ระดับ container
      - name: data                       # ต้องตรงกับ volumes[].name
        mountPath: /var/lib/postgresql/data # path ที่เห็นใน container
volumes:                                 # volume อยู่ระดับ Pod
  - name: data                           # ชื่อที่ volumeMounts อ้าง
    emptyDir: {}                         # หายเมื่อ Pod ถูกนำออกจาก Node
```
PVC จริงจาก `013-persistent-storage-with-pvc/01-pvc.yaml`:

```yaml
apiVersion: v1                    # API version ของ PVC
kind: PersistentVolumeClaim      # คำขอพื้นที่เก็บข้อมูล
metadata:
  name: db-data                  # ชื่อ claim ที่ Pod ใช้อ้าง
  namespace: lab013             # namespace เดียวกับ Pod
spec:
  accessModes:                  # ต้องระบุอย่างน้อยหนึ่ง mode
    - ReadWriteOnce            # ให้ node เดียว mount แบบ read-write
  resources:
    requests:
      storage: 1Gi             # ต้องระบุขนาดพื้นที่ที่ขอ
```
การอ้าง claim จริงจาก `013-persistent-storage-with-pvc/02-db.yaml`:

```yaml
volumes:                        # อยู่ใต้ spec.template.spec
  - name: data                 # ชื่อเดียวกับ volumeMounts
    persistentVolumeClaim:
      claimName: db-data       # PVC ใน namespace เดียวกัน
```
| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืมจะเกิดอะไร |
|---|---|---|---|
| `volumes[].name` | ชื่อ DNS label ที่ไม่ซ้ำใน Pod | ไม่มี | ต้องตรงกับ `volumeMounts[].name` |
| `emptyDir` | `{}`, `medium`, `sizeLimit` | default medium ของ Node; `sizeLimit` ไม่กำหนด | อยู่รอดเมื่อ Container restart แต่ถูกลบเมื่อ Pod ถูกนำออกจาก Node |
| `volumeMounts[].mountPath` | absolute path ใน Container | ไม่มี | ข้อมูลใต้ path มาจาก volume ไม่ใช่ writable layer เดิม |
| `persistentVolumeClaim.claimName` | PVC ใน namespace เดียวกัน | ไม่มี | claim ไม่พบทำให้ Pod schedule/mount ไม่ได้ |
| `accessModes` | `ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`, `ReadWriteOncePod` | ไม่มี—ต้องระบุอย่างน้อย 1 mode | เป็นความสามารถ/เงื่อนไขการจับคู่ volume ไม่ใช่คำสั่ง chmod |
| `resources.requests.storage` | Quantity เช่น `1Gi` | ไม่มี—ต้องระบุ | ขอ capacity ขั้นต่ำ; class/driver ต้องรองรับ |
| `storageClassName` | ชื่อ StorageClass, `""`, หรือไม่ระบุ | ถ้าไม่ระบุอาจถูกเติมด้วย default StorageClass | `""` หมายถึงไม่ขอ class และปิด dynamic provisioning แบบ default |
ชื่อย่อที่พบบ่อยคือ RWO = node เดียว mount แบบ read-write, ROX = หลาย node mount แบบ read-only และ RWX = หลาย node mount แบบ read-write; ความสามารถจริงขึ้นกับ volume plugin
`PGDATA` ไม่ใช่ field ของ Kubernetes แต่เป็น environment variable ของ PostgreSQL ในไฟล์จริง โดยตั้งเป็น subdirectory ใต้ mount (`.../pgdata`) ให้ data directory แยกจาก root ของ volume; เปลี่ยน path แล้ว PostgreSQL จะมองคนละ data directory
**ผิดบ่อย:** ชื่อ mount ไม่ตรง volume เป็นตัวอย่างข้อความ (ไม่มีใน runlog): `spec.template.spec.containers[0].volumeMounts[0].name: Not found: "data"` ส่วน runlog LAB 013 มี Event `0/3 nodes are available: persistentvolumeclaim "db-data" not found.` (`FailedScheduling`)
คำสั่งดูของจริง:
```bash
kubectl get pvc db-data -n lab013 -o yaml
kubectl explain pod.spec.volumes.emptyDir
kubectl explain persistentvolumeclaim.spec.resources.requests
```
## Probes

Probe ตอบคนละคำถาม: readiness ถาม “ควรรับ traffic หรือยัง”, liveness ถาม “ควร restart Container หรือไม่” และ startup ให้เวลาสำหรับโปรแกรมที่เริ่มช้า ก่อนเปิด readiness/liveness
โครงจริงจาก `014-running-is-not-ready/01-api-with-probes.yaml`:

```yaml
readinessProbe:            # พร้อมรับ traffic หรือยัง
  httpGet:
    path: /ready           # เช็ก dependency ด้วย SELECT 1
    port: http             # อ้าง container port ชื่อ http
  periodSeconds: 5         # ตรวจทุก 5 วินาที
  timeoutSeconds: 2        # เกิน 2 วินาทีถือว่า fail
  failureThreshold: 2      # fail ต่อเนื่อง 2 ครั้งจึง NotReady
livenessProbe:             # process ยังควรถูกรันต่อหรือไม่
  httpGet:
    path: /health          # เช็กเฉพาะ process ของ API
    port: http             # อ้าง container port ชื่อ http
  initialDelaySeconds: 5   # รอ 5 วินาทีก่อนเริ่มตรวจ
  periodSeconds: 10        # ตรวจทุก 10 วินาที
  timeoutSeconds: 2        # เกิน 2 วินาทีถือว่า fail
  failureThreshold: 3      # fail 3 ครั้งจึง restart
```
| field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืมจะเกิดอะไร |
|---|---|---|---|
| `readinessProbe` | HTTP, TCP, gRPC, exec | ไม่สร้าง probe | fail แล้ว Ready condition = `False` (`READY 0/1`) แต่ `STATUS` ยัง `Running`; ถูกถอดจาก Service endpoints และ Container ไม่ restart |
| `livenessProbe` | HTTP, TCP, gRPC, exec | ไม่สร้าง probe | fail ครบ threshold แล้ว kubelet restart Container ตาม restart policy |
| `startupProbe` | HTTP, TCP, gRPC, exec | ไม่สร้าง probe | ขณะยังไม่สำเร็จ readiness/liveness ยังไม่เริ่ม; fail ครบ threshold แล้ว restart |
| `httpGet.path` / `port` | path; port เป็นชื่อหรือเลข | path `/`; `port` ต้องระบุ | path/port ต้องตรง endpoint ที่ process เปิดจริง |
| `exec.command` | list ของคำสั่งและ argument | ไม่มี ต้องระบุ | exit code 0 = สำเร็จ; non-zero = fail และไม่รันผ่าน shell อัตโนมัติ |
| `initialDelaySeconds` | จำนวนวินาที ≥ 0 | `0` | รอก่อนตรวจครั้งแรก; มากไปทำให้ตรวจพบปัญหาช้า |
| `periodSeconds` | จำนวนวินาที ≥ 1 | `10` | ช่วงห่างการตรวจ; ต่ำไปเพิ่ม load |
| `timeoutSeconds` | จำนวนวินาที ≥ 1 | `1` | เกินเวลาถือว่า fail |
| `failureThreshold` | จำนวนครั้งต่อเนื่อง ≥ 1 | `3` | คูณกับ period โดยประมาณเป็นเวลาทนก่อนเปลี่ยนสถานะ/รีสตาร์ต |
| `successThreshold` | จำนวนครั้งต่อเนื่อง ≥ 1 | `1` | liveness/startup ต้องเป็น `1`; readiness เพิ่มได้เพื่อกันอาการแกว่ง |
สำหรับ `httpGet` สถานะ HTTP 200–399 ถือว่าสำเร็จ; 400 ขึ้นไปหรือเชื่อมต่อ/timeout ไม่สำเร็จถือว่า fail
`readinessProbe.exec` ปรากฏครั้งแรกใน `013-persistent-storage-with-pvc/02-db.yaml` ด้วย `command: ["pg_isready", "-U", "opsuser", "-d", "skillspace"]`; LAB 013 จึงชี้กลับหัวข้อนี้ ส่วน `startupProbe` ไม่มีใน manifest ของครั้งนี้ จึงกล่าวถึงโดยไม่แต่ง YAML เพิ่ม
**ผิดบ่อย:** runlog LAB 014 บันทึกจริง `Readiness probe failed: HTTP probe failed with statuscode: 404` เมื่อใช้ `/readyz`; readiness ผิดทำให้ endpoints ว่าง ไม่ได้ restart ส่วน liveness ที่ fail บันทึก `Container api failed liveness probe, will be restarted`
คำสั่งดูของจริง:
```bash
kubectl get deployment api -n lab014 -o yaml
kubectl describe pod -n lab014 -l app=api
kubectl explain deployment.spec.template.spec.containers.readinessProbe
```
## สรุป field ของครั้งนี้

| field | object | แล็บแรกที่ใช้ |
|---|---|---:|
| `type`, `selector`, `ports.port/targetPort/nodePort/protocol` | Service | 008–009 |
| Service DNS และ EndpointSlice จาก selector | Service | 008 |
| `data`, `envFrom.configMapRef`, `configMapKeyRef` | ConfigMap / Pod | 010 |
| `type`, `stringData`, `data`, `secretKeyRef` | Secret / Pod | 011 |
| `volumes`, `volumeMounts`, `emptyDir`, `PGDATA` | Pod / PostgreSQL | 012 |
| `accessModes`, `requests.storage`, `storageClassName`, `claimName` | PVC / Pod | 013 |
| `readinessProbe.exec` | Pod | 013 |
| `readinessProbe.httpGet`, `livenessProbe`, `startupProbe` | Pod | 014 |
| `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `failureThreshold`, `successThreshold` | Probe | 014 |
**จำภาพเดียวให้ได้:** Service ทำให้ “ปลายทาง” คงที่, ConfigMap/Secret แยก “ค่า”, Volume/PVC แยก “ข้อมูล”, และ Probes บอกว่า Pod ใด “พร้อมจริง” แม้ทุกชิ้นจะถูกประกาศผ่าน YAML ต้นไม้แบบเดียวกัน
