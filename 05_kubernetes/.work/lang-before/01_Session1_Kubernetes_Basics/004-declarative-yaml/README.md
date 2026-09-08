# LAB 4 — Declarative YAML : บอกปลายทาง แล้วให้ Kubernetes จัดการ

> โฟลเดอร์ `004-declarative-yaml` = LAB 4 ของชุด Kubernetes ครั้งที่ 1
> (ไฟล์ของแล็บนี้: `01-pod.yaml` · `02-pod-v2.yaml` · `03-pod-typo.yaml` · `images/05-pod-v2-after-apply.png`)

> 💡 **แนวคิดหลักของแล็บนี้:** เราไม่ได้สั่งว่า "ทำอะไร" แต่บอกว่า "อยากได้สภาพแบบไหน" แล้ว Kubernetes จัดการให้เอง (declarative)

> ชื่อ Pod, IP, UID, AGE, เวลา และ node ที่ scheduler เลือกเป็นค่าที่ไม่คงที่ — **ค่าเหล่านี้ต่างกันได้**

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายความต่างระหว่าง imperative กับ declarative ได้
2. อ่านหน้าที่ของ `apiVersion`, `kind`, `metadata` และ `spec` ได้
3. อธิบายได้ว่าทำไม `kubectl apply` ซ้ำแล้วผลยังเหมือนเดิม
4. อธิบายได้ว่าทำไม Pod บาง field แก้ตรง ๆ ไม่ได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ในแล็บก่อนเราใช้ `kubectl run` ซึ่งคล้าย `docker run`; ไฟล์ YAML กลับทำหน้าที่คล้าย `compose.yaml` โดยเก็บ "สภาพที่อยากได้" แล้วส่งให้ API server เปรียบเทียบกับ object จริง

| วิธี | สิ่งที่เราบอก | ผลเมื่อทำซ้ำ |
|---|---|---|
| imperative | ขั้นตอน เช่น run, delete | อาจ error เพราะของเดิมมีอยู่แล้ว |
| declarative | สภาพปลายทางใน YAML | `created`, `configured` หรือ `unchanged` |

ทุก object มีแกนเดียวกัน: `apiVersion` เลือก API · `kind` บอกชนิด · `metadata` บอกตัวตนและ label · `spec` บอก desired state ส่วน `status` เป็นหลักฐาน actual state ที่ Kubernetes เติมกลับมา

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น kubectl สร้าง YAML จากคำสั่ง imperative
- จะได้พิสูจน์ว่า apply ไฟล์เดิมซ้ำเป็น `unchanged`
- จะได้อ่าน diff ก่อนเปลี่ยน image จาก v1 เป็น v2
- จะได้เห็น error ของ immutable field
- จะได้แยก syntax/schema error สองชนิดจากข้อความจริง

## ภาพรวมของแล็บนี้

1. สร้าง Pod v1 จาก YAML
2. apply ซ้ำและเทียบ desired กับ actual
3. ดู diff แล้วเปลี่ยนเป็น v2
4. ทดลองแก้ field ที่ immutable
5. ส่ง YAML ผิดให้ server ตรวจ แล้วแก้กลับ

![วงจร declarative จาก YAML ไปยัง Pod จริง](../slides_assets/lab004-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า apply ไฟล์เดิมสองครั้ง Kubernetes จะสร้าง Pod สองตัว หรือรักษา Pod ตัวเดิมไว้?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกจากเครื่องหลัก จากนั้นเข้าเครื่องเรียนและพิมพ์คำสั่งที่เหลือใน shell ที่เปิด:

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** `docker start` เปิดเครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` ข้ามขั้นสร้างเองเมื่อ cluster มีอยู่แล้ว · `kubectl get nodes` ตรวจ 3 nodes · `crictl images` อ่าน image ใน kind node

✅ **Expected output** — nodes ทั้งสามเป็น `Ready` และเห็น web v1/v2, api, db ครบ (AGE และ image ID ต่างกันได้):
```text
Set kubectl context to "kind-devtools"
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready    control-plane   20m   v1.36.4
devtools-worker          Ready    <none>          20m   v1.36.4
devtools-worker2         Ready    <none>          20m   v1.36.4
docker.io/library/k8s-lab-api   v1   f0b9cc03efb0e   186MB
docker.io/library/k8s-lab-db    v1   c6f278c2d20e4   300MB
docker.io/library/k8s-lab-web   v1   47289fcac09e8   209MB
docker.io/library/k8s-lab-web   v2   f2d6e974702f8   209MB
```

ถ้ายังไม่เห็น image ให้ย้อนทำขั้น build/load ของ LAB 001 หรือ README ระดับชุดก่อน
ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 เมื่อเรียก Ingress ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`; แล็บนี้เปิดหน้า port-forward ที่ `http://localhost:3000`

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/004-declarative-yaml
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace ถ้ายังไม่มี · `git clone` ดาวน์โหลดชุด LAB · `cd` เข้าสู่โฟลเดอร์ LAB 004

✅ **Expected output** — clone สำเร็จและ `cd` ไม่แสดง error:
```text
Cloning into 'DevTools'...
```

ถ้า clone ไว้แล้ว ไม่ต้อง clone ซ้ำ ให้รัน `cd ~/labwork/DevTools && git pull` แล้วกลับเข้าโฟลเดอร์แล็บ; หยุดและถามผู้สอนถ้ามี conflict

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-pod.yaml` | Pod | ประกาศ web v1 เป็น desired state เริ่มต้น | [ดู YAML_Guide.md → อ่าน YAML ให้เป็น](../YAML_Guide.md#อ่าน-yaml-ให้เป็น) |
| `02-pod-v2.yaml` | Pod | เปลี่ยน label และ image เป็น v2 เพื่อดู diff/apply | [ดู YAML_Guide.md → Pod](../YAML_Guide.md#pod) |
| `03-pod-typo.yaml` | `Pods` (ผิดตั้งใจ) | พิสูจน์ว่า YAML syntax ถูกแต่ Kubernetes schema ไม่รู้จัก kind | หัวข้อทดลองให้พังด้านล่าง |

โครงสี่ส่วนจาก `01-pod.yaml` คือแผนที่อ่าน object ทุกชนิด:

```yaml
apiVersion: v1             # API group/version; Pod ใช้ core group v1
kind: Pod                  # ชนิด object
metadata:                  # ตัวตนและข้อมูลประกอบ
  name: web                # ชื่อใน namespace
  labels:                  # key/value สำหรับจัดกลุ่ม
    app: web
    version: v1
spec:                      # desired state ที่เราสั่ง
  containers:              # list จึงใช้ - เปิดสมาชิก
    - name: web
      image: k8s-lab-web:v1
```

| field/รูปแบบ | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `apiVersion` / `kind` | เลือก schema ของ API | ชื่อไม่รองรับจะ map resource ไม่ได้ |
| `metadata.name` / `labels` | ระบุตัว object / จัดกลุ่ม | เปลี่ยน name คือคนละ object; label กระทบ selector |
| `spec` / `status` | สิ่งที่ต้องการ / สิ่งที่ระบบรายงาน | manifest ปกติเขียน `spec`; controller เขียน `status` |
| เยื้อง 2 ช่อง / `-` / `#` | nesting / สมาชิก list / comment | เยื้องผิดอาจย้าย field ไปผิด schema |

YAML รองรับ string/number/bool; ค่า environment ที่หน้าตาเป็นเลข เช่น `"5432"` ต้อง quote เพราะ field นั้นรับ string (ตัวอย่างเพิ่มเติม ไม่อยู่ในไฟล์ของแล็บ) ส่วน `---` ใช้คั่นหลาย object (จะเห็นจริงในแล็บ 005) และ annotations เป็น metadata ที่ selector ไม่ใช้เลือกสมาชิก (เห็นจริงใน 007) อ่านฉบับเต็มที่ [YAML_Guide.md → อ่าน YAML ให้เป็น](../YAML_Guide.md#อ่าน-yaml-ให้เป็น)

**ผิดบ่อยในแล็บนี้:** runlog มีข้อความจริง `strict decoding error: unknown field "containers"` เมื่อวาง field ผิดระดับ และ `no matches for kind "Pods" in version "v1"` จาก `03-pod-typo.yaml`; YAML parser อ่านได้ แต่ Kubernetes schema ปฏิเสธ

ตรวจ syntax/kind ด้วย `kubectl apply --dry-run=client -f 01-pod.yaml`, ตรวจ schema/admission ด้วย `kubectl apply --dry-run=server -f 01-pod.yaml` และดู field ด้วย `kubectl explain pod.spec.containers.imagePullPolicy`

## 3. จากคำสั่ง imperative สู่ YAML

สร้าง namespace และให้ kubectl แสดง YAML โดยยังไม่สร้าง Pod:

```bash
kubectl create namespace lab004
kubectl run web --image=k8s-lab-web:v1 --port=3000 --dry-run=client -o yaml
```
> 📝 **คำอธิบาย:** `create namespace` เปิดห้องแยกของแล็บ · `run web` ขอ Pod ชื่อ web · `--image` เลือก image · `--port=3000` บันทึก container port · `--dry-run=client` สร้างคำตอบในเครื่องโดยไม่ส่ง API · `-o yaml` แสดงเป็น YAML

✅ **Expected output** — เห็น namespace created และ YAML มีสี่ส่วนหลัก:
```text
namespace/lab004 created
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: web
  name: web
spec:
  containers:
  - image: k8s-lab-web:v1
    name: web
    ports:
    - containerPort: 3000
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```

ผลนี้มีครบทุก field ที่คำสั่งสร้างจริง ส่วนไฟล์ `01-pod.yaml` ด้านล่างตัด default ที่ไม่จำเป็นออก

ไฟล์ `01-pod.yaml` เขียนเฉพาะ desired state ที่ต้องการ:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
    version: v1
spec:
  containers:
    - name: web
      image: k8s-lab-web:v1
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 3000
```

`metadata.labels` ใช้จัดกลุ่ม · `spec.containers` คือรายการ container · `imagePullPolicy` ใช้ image ที่ load ไว้ก่อน · `containerPort` บอกพอร์ตของแอป ไม่ได้เปิดพอร์ตออกนอก cluster

## 4. Apply แล้วพิสูจน์ idempotency

```bash
kubectl apply -n lab004 -f 01-pod.yaml
kubectl wait -n lab004 --for=condition=Ready pod/web --timeout=120s
kubectl apply -n lab004 -f 01-pod.yaml
kubectl get pod web -n lab004 -o wide
```
> 📝 **คำอธิบาย:** `apply` ส่ง desired state · `-n lab004` เลือก namespace · `-f` อ่านไฟล์ · `wait --for=condition=Ready` รอ Pod พร้อม · `--timeout=120s` จำกัดเวลารอ · apply รอบสองพิสูจน์ idempotency · `-o wide` เพิ่ม IP และ NODE

✅ **Expected output** — รอบแรก `created`, รอบสอง `unchanged`, Pod เดิมยัง `Running` (IP, NODE, AGE ต่างกันได้):
```text
pod/web created
pod/web condition met
pod/web unchanged
NAME   READY   STATUS    RESTARTS   AGE   IP            NODE
web    1/1     Running   0          1s    10.244.1.29   devtools-worker2
```

ดู object ที่ API server เก็บและ log ของ process:

```bash
kubectl get pod web -n lab004 -o yaml
kubectl logs -n lab004 pod/web --tail=20
```
> 📝 **คำอธิบาย:** `-o yaml` แสดง desired และ status ฉบับเต็ม · `logs` อ่าน stdout/stderr · `--tail=20` จำกัด 20 บรรทัดท้าย

✅ **Expected output** — YAML มี `uid`, `nodeName`, `status.phase: Running` เพิ่มจากไฟล์ และ log บอก Next.js พร้อม (UID, เวลา และชื่อ volume ต่างกันได้):
```text
  uid: 2cbc86f7-8fe7-427a-9b75-4654d1c49e17
spec:
  nodeName: devtools-worker2
status:
  phase: Running
▲ Next.js 16.3.1
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
```

## 5. ดู diff แล้วเปลี่ยน desired state เป็น v2

```bash
kubectl diff -n lab004 -f 02-pod-v2.yaml
kubectl apply -n lab004 -f 02-pod-v2.yaml
kubectl get pod web -n lab004 -o jsonpath='{.metadata.labels.version}{" "}{.spec.containers[0].image}{"\n"}'
```
> 📝 **คำอธิบาย:** `diff` เทียบไฟล์กับของจริงโดยไม่แก้ · exit code 1 ของ diff หมายถึง "พบความต่าง" · apply ทำให้ actual เข้าใกล้ desired · `jsonpath` เลือกเฉพาะ label และ image

✅ **Expected output** — diff ชี้ v1→v2 แล้ว apply เป็น `configured`:
```text
-    version: v1
+    version: v2
-  - image: k8s-lab-web:v1
+  - image: k8s-lab-web:v2
pod/web configured
v2 k8s-lab-web:v2
```

เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้ง จากนั้นเปิดหน้าเว็บจาก Pod ตัวนี้และคงหน้าต่างใหม่ไว้:

```bash
kubectl port-forward -n lab004 pod/web 3000:3000 --address 0.0.0.0
```
> 📝 **คำอธิบาย:** `port-forward` ต่อพอร์ตเครื่องเรียนไปยัง Pod เดียว · `3000:3000` คือพอร์ตด้านเครื่องเรียน:พอร์ต Pod · `--address 0.0.0.0` ทำให้ browser ภายนอก container เข้าได้ · เปิด `http://localhost:3000`

✅ **Expected output** — terminal ค้างรับ connection และหน้าเว็บแสดง Pod `web`, ป้าย `v2`, theme `emerald`:
```text
Forwarding from 0.0.0.0:3000 -> 3000
```

![SkillSpace v2 หลัง apply image ใหม่](images/05-pod-v2-after-apply.png)

กด `Ctrl+C` เมื่อดูภาพเสร็จ

## 6. ขอบเขตการแก้ Pod

ทดลองเพิ่ม env ในสำเนาชั่วคราว แล้วให้ server ตัดสิน:

```bash
yq '.spec.containers[0].env = [{"name":"LAB_NOTE","value":"immutable"}]' 02-pod-v2.yaml > /tmp/pod-env.yaml
kubectl apply -n lab004 -f /tmp/pod-env.yaml
kubectl replace --force -n lab004 -f /tmp/pod-env.yaml
kubectl wait -n lab004 --for=condition=Ready pod/web --timeout=120s
kubectl exec -n lab004 pod/web -- printenv LAB_NOTE
```
> 📝 **คำอธิบาย:** `yq` เพิ่ม field ในสำเนา · `apply` พยายามแก้ Pod เดิม · `replace --force` ลบแล้วสร้างจาก desired state ใหม่ · `wait` ยืนยัน Pod ใหม่พร้อม · `printenv` พิสูจน์ว่า Pod ที่สร้างใหม่รับ `LAB_NOTE`

✅ **Expected output** — apply ถูกปฏิเสธ แต่ force replace สำเร็จ:
```text
The Pod "web" is invalid: spec: Forbidden: pod updates may not change fields other than `spec.containers[*].image`,`spec.initContainers[*].image`,`spec.activeDeadlineSeconds`,`spec.tolerations` (only additions to existing tolerations),`spec.terminationGracePeriodSeconds` (allow it to be set to 1 if it was previously negative)
pod "web" deleted from lab004 namespace
pod/web replaced
pod/web condition met
immutable
```

นี่คือเหตุผลที่งานจริงให้ Deployment จัดการการสร้าง Pod ใหม่ แทนการแก้ Pod ทีละตัว

## 7. ทดลองให้พัง — YAML ถูกไวยากรณ์แต่ schema ผิด

สร้างกรณีย่อหน้า `containers` ผิดระดับ แล้วตรวจฝั่ง server:

```bash
sed 's/^  containers:/containers:/' 01-pod.yaml > /tmp/pod-bad-indent.yaml
kubectl apply --dry-run=server -n lab004 -f /tmp/pod-bad-indent.yaml
kubectl apply --dry-run=server -n lab004 -f 03-pod-typo.yaml
```
> 📝 **คำอธิบาย:** `sed` ย้าย indentation เพื่อทำให้พังอย่างตั้งใจ · `--dry-run=server` ให้ API server validate โดยไม่สร้าง object · ไฟล์ `03-pod-typo.yaml` ใช้ `kind: Pods` ผิดจาก `Pod`

✅ **Expected output** — อ่านให้แยกได้ว่า field อยู่ผิดที่ กับชนิด object ไม่มีอยู่:
```text
Warning: resource pods/web is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
The request is invalid: patch: Invalid value: "map[containers:[map[image:k8s-lab-web:v1 imagePullPolicy:IfNotPresent name:web ports:[map[containerPort:3000]]]] metadata:map[annotations:map[kubectl.kubernetes.io/last-applied-configuration:{\"apiVersion\":\"v1\",\"containers\":[{\"image\":\"k8s-lab-web:v1\",\"imagePullPolicy\":\"IfNotPresent\",\"name\":\"web\",\"ports\":[{\"containerPort\":3000}]}],\"kind\":\"Pod\",\"metadata\":{\"annotations\":{},\"labels\":{\"app\":\"web\",\"version\":\"v1\"},\"name\":\"web\",\"namespace\":\"lab004\"},\"spec\":null}\n] labels:map[version:v1]] spec:<nil>]": strict decoding error: unknown field "containers"
error: resource mapping not found for name: "web-typo" namespace: "" from "03-pod-typo.yaml": no matches for kind "Pods" in version "v1"
ensure CRDs are installed first
```

Warning เกิดเพราะ `replace --force` สร้าง Pod ใหม่โดยไม่มี last-applied annotation จึงเป็นข้อความที่ผู้เรียนจะเห็นจริงก่อน error

แก้กลับด้วยไฟล์ถูกต้องและเปิดคู่มือ field:

```bash
kubectl replace --force -n lab004 -f 01-pod.yaml
kubectl wait -n lab004 --for=condition=Ready pod/web --timeout=120s
kubectl explain pod.spec.containers.imagePullPolicy
```
> 📝 **คำอธิบาย:** `replace --force` คืน Pod v1 ที่สะอาด · `explain` อ่าน schema จาก API ที่ cluster ใช้อยู่จริง · path แบบจุดไล่จาก Pod ไปยัง field

✅ **Expected output** — Pod กลับพร้อมและคู่มือแสดง enum สามค่า:
```text
pod "web" deleted from lab004 namespace
pod/web replaced
pod/web condition met
FIELD: imagePullPolicy <string>
ENUM:
    Always
    IfNotPresent
    Never
```

## 8. แบบฝึกหัดสั้น (Exercise)

เพิ่ม label `course: devtools` ในสำเนา manifest แล้วทายก่อนว่า apply จะ `configured` หรือถูกปฏิเสธ จากนั้นพิสูจน์ด้วยตนเอง เกณฑ์ผ่านคืออธิบายได้ว่า metadata label แก้ได้ แต่ field ใน Pod spec หลายตัวแก้ไม่ได้ และไฟล์ต้นฉบับยังคงถูกต้อง

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get pod web -n lab004
kubectl get events -n lab004 --sort-by=.lastTimestamp
kubectl logs -n lab004 pod/web --tail=5
```
> 📝 **คำอธิบาย:** `get pod` ตรวจ Ready/Status จากตารางจริง · `events --sort-by` เรียงเหตุการณ์ตามเวลา · `logs --tail=5` ตรวจ process จริง

✅ **Expected output** — Pod v1 Running, event มี Scheduled/Pulled/Created/Started และ log มี Ready (ตัดบางแถว/ข้อความท้าย; เวลาและ AGE ต่างกันได้):
```text
NAME   READY   STATUS    RESTARTS   AGE
web    1/1     Running   0          0s
Normal   Scheduled   pod/web   Successfully assigned lab004/web to devtools-worker2
Normal   Pulled      pod/web   Container image "k8s-lab-web:v1" already present on machine and can be accessed by the pod
…
✓ Ready in 0ms
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `unknown field` | indentation ทำให้ field อยู่ผิดระดับ | เทียบกับ `01-pod.yaml` และใช้ server dry-run |
| `no matches for kind` | สะกด `kind` ผิด | ใช้ `kubectl api-resources` หรือ `explain` |
| apply แล้ว Forbidden | กำลังแก้ immutable field ของ Pod | ลบ/สร้างใหม่ หรือใช้ Deployment |
| `ImagePullBackOff` | ยังไม่ได้ load image เข้า kind | ย้อน LAB 001 แล้ว `kind load` |
| หน้าเว็บเข้าไม่ได้ | port-forward หยุดหรือ bind เฉพาะ loopback | รันใหม่พร้อม `--address 0.0.0.0` |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

ลบทั้ง namespace แล้วพิสูจน์ว่าว่าง:

```bash
kubectl delete namespace lab004
kubectl wait --for=delete namespace/lab004 --timeout=120s
kubectl get all -n lab004
```
> 📝 **คำอธิบาย:** `delete namespace` ลบทุก namespaced object · `wait --for=delete` รอจนลบจริง · `get all` ตรวจว่าไม่เหลือ workload/service

✅ **Expected output** — ไม่มี resource ค้าง:
```text
namespace "lab004" deleted
No resources found in lab004 namespace.
```

สร้างใหม่จากไฟล์เดิม แล้วลบปิดท้ายอีกครั้ง:

```bash
kubectl create namespace lab004
kubectl apply -n lab004 -f 01-pod.yaml
kubectl wait -n lab004 --for=condition=Ready pod/web --timeout=120s
kubectl get pod web -n lab004
kubectl delete namespace lab004
kubectl wait --for=delete namespace/lab004 --timeout=120s
kubectl get all -n lab004
```
> 📝 **คำอธิบาย:** create เปิดห้องใหม่ · apply ใช้ source of truth เดิม · wait/get พิสูจน์ผลซ้ำ · สามคำสั่งท้ายลบและตรวจซ้ำ

✅ **Expected output** — Clean Re-run ได้ Pod 1/1 Running แล้วปิดท้ายว่าง (AGE ต่างกันได้):
```text
namespace/lab004 created
pod/web created
pod/web condition met
NAME   READY   STATUS    RESTARTS   AGE
web    1/1     Running   0          0s
namespace "lab004" deleted
No resources found in lab004 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl run --dry-run=client -o yaml` | ให้ kubectl ร่าง YAML โดยไม่สร้าง |
| `kubectl apply -f` | ทำให้ actual เข้าใกล้ desired |
| `kubectl diff -f` | ดูความต่างก่อน apply |
| `kubectl replace --force` | ลบแล้วสร้าง Pod ใหม่จากไฟล์ |
| `kubectl apply --dry-run=server` | ตรวจ manifest ด้วย API server |

## สรุปสิ่งที่ได้เรียนรู้

YAML ไม่ได้เป็นเพียงชุดคำสั่งที่เขียนหลายบรรทัด แต่เป็นสัญญาว่าเราอยากให้ object มีหน้าตาอย่างไร Kubernetes จึงตรวจและปรับของจริงให้สอดคล้อง

- imperative บอกขั้นตอน ส่วน declarative บอกปลายทาง
- สี่ส่วนหลักทำให้ object ทุกชนิดอ่านด้วยกรอบเดียวกัน
- apply ซ้ำได้เพราะระบบเปรียบเทียบ state ก่อนลงมือ
- Pod ถูกออกแบบให้สร้างใหม่เมื่อ spec สำคัญเปลี่ยน

**จำภาพเดียวให้ได้:** ไฟล์ YAML อยู่ฝั่ง desired state ส่วน `status` อยู่ฝั่ง actual state

🧭 ต่อยอด: [LAB 5 — Labels: the glue](../005-labels-the-glue/README.md)

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. imperative ต่างจาก declarative อย่างไร? — แบบแรกบอกขั้นตอนและต้องรู้สภาพปัจจุบัน แบบหลังประกาศปลายทางให้ระบบหาทางเอง
2. `apiVersion/kind/metadata/spec` บอกอะไร? — API ที่ใช้ · ชนิด object · ตัวตน/label · desired state
3. ทำไม image แก้ได้แต่ env ถูกปฏิเสธ? — Pod รองรับการ update ตรง ๆ เพียงบาง field; การเปลี่ยน template ปกติควรสร้าง Pod ใหม่ผ่าน controller

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] อธิบาย imperative กับ declarative ได้
- [ ] อ่านสี่ส่วนหลักของ manifest ได้
- [ ] เห็น `created` และ `unchanged` จริง
- [ ] อ่าน error `unknown field` กับ `no matches` ออก
- [ ] Clean Re-run ผ่านและไม่มี resource ค้าง

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
