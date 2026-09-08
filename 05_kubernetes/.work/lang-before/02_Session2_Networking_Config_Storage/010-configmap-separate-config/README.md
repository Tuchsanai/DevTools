# LAB 10 — ConfigMap : เปลี่ยนพฤติกรรมโดยไม่ build image ใหม่

> โฟลเดอร์ `010-configmap-separate-config` = LAB 10 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `01-web.yaml`, `02-configmap.yaml`, `03-web-envfrom.yaml`, `04-configmap-rose.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** config ไม่ควรอยู่ใน image — build ครั้งเดียวแต่เปลี่ยนพฤติกรรมได้ตามที่ deploy

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายได้ว่าทำไมชื่อระบบ สี และ URL ไม่ควรถูกฝังไว้ใน image
2. อธิบายหน้าที่ของ ConfigMap และวิธีส่งค่าเข้า Pod ผ่าน environment variable
3. พิสูจน์ได้ว่า environment variable อ่านค่า ConfigMap ตอนสร้าง container เท่านั้น
4. อ่านอาการ `CreateContainerConfigError` และแก้ชื่อ ConfigMap ที่อ้างผิดได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ลองคิดถึง image เป็น “กล่องแอปที่ปิดผนึกแล้ว” ถ้าชื่อหน่วยงานหรือสีธีมอยู่ในกล่อง ทุกหน่วยงานต้อง build กล่องใหม่ ทั้งที่โค้ดเหมือนเดิมทั้งหมด ConfigMap แยกค่าที่ไม่ลับออกมาเป็น object ของ Kubernetes แล้วนำกล่องเดิมไปใช้ได้หลายสภาพแวดล้อม

| สิ่งที่เปรียบเทียบ | ฝังใน image | ConfigMap |
|---|---|---|
| เปลี่ยนชื่อ/สี | ต้อง build image ใหม่ | แก้ object แล้วสร้าง Pod ใหม่ |
| image ระหว่าง dev/prod | มีโอกาสคนละชุด | ใช้ digest/tag เดียวกันได้ |
| เหมาะกับ | โค้ดและ default | config ที่ไม่ลับ |
| เทียบกับ Compose | ค่าใน Dockerfile | `environment:` / `env_file` |

ConfigMap ไม่ใช่ที่เก็บรหัสผ่าน เพราะค่าถูกอ่านเป็นข้อความปกติ เรื่องข้อมูลลับจะพิสูจน์ใน LAB 11

## สิ่งที่จะได้เรียนรู้

- จะได้เห็นหน้าเว็บใช้ default `SkillSpace` และ theme `blue` จาก image
- จะได้ส่งทุก key ด้วย `envFrom.configMapRef`
- จะได้เห็นชื่อระบบและธีม amber โดยไม่ build image ใหม่
- จะได้พิสูจน์ว่าแก้ ConfigMap เป็น rose แล้ว Pod เดิมยังเป็น amber
- จะได้อ่าน Event ที่บอก `configmap "web-confg" not found`

## ภาพรวมของแล็บนี้

1. เปิดเว็บด้วย config เริ่มต้นจาก image
2. สร้าง ConfigMap สำหรับชื่อระบบและ theme
3. ผูก ConfigMap เข้ากับ Deployment แล้วดูหน้า amber
4. เปลี่ยนค่าเป็น rose และพิสูจน์ว่ายังไม่เกิดผลทันที
5. restart, ทดลองชื่อผิด, แก้กลับ และพิสูจน์ Clean Re-run

![ConfigMap แยกค่าตั้งค่าออกจาก image](../slides_assets/lab010-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้าคณะสามแห่งใช้โค้ดชุดเดียวกันแต่ชื่อและสีต่างกัน เราควรมี image สามชุดจริงหรือ?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิม · `|| docker run` สร้างเมื่อยังไม่มี · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · สองคำสั่งท้ายตรวจ node และ image ใน kind

✅ **Expected output** — 3 nodes เป็น `Ready` และพบ image 4 รายการ (ตัดบางคอลัมน์; AGE/hash ต่างกันได้):

```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready    control-plane   12m   v1.36.4
devtools-worker          Ready    <none>          12m   v1.36.4
devtools-worker2         Ready    <none>          12m   v1.36.4
docker.io/library/k8s-lab-api   v1   37b98a526d09b   186MB
docker.io/library/k8s-lab-db    v1   12de2be925d8a   300MB
docker.io/library/k8s-lab-web   v1   f46e8e22f91a6   209MB
docker.io/library/k8s-lab-web   v2   fccf050046905   209MB
…
```

ถ้ายังไม่พบ image ให้กลับไปทำขั้น build/load ใน LAB 001 หรือ README ระดับชุดก่อน

## 1. Clone โค้ดแล็บ
```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace แบบทำซ้ำได้ · `git clone` ดึง repository · `cd` เข้าโฟลเดอร์ LAB 10 ที่มี manifest พร้อมใช้

✅ **Expected output** — clone เริ่มสำเร็จและ path สุดท้ายตรงกับแล็บ:
```text
Cloning into 'DevTools'...
/root/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config
```
ถ้า clone ไว้แล้ว ไม่ต้อง clone ซ้ำ ให้เข้า repository เดิมแล้วใช้ `git pull` ก่อนเข้าพาธข้างต้น

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-web.yaml` | Deployment, Service, Ingress | เปิด web ด้วยค่า default จาก image | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) · [Ingress](../YAML_Guide.md#ingress) |
| `02-configmap.yaml` | ConfigMap | เก็บชื่อระบบและ theme นอก image | [ConfigMap](../YAML_Guide.md#configmap) |
| `03-web-envfrom.yaml` | Deployment | นำทุก key เข้า environment | [Deployment](../YAML_Guide.md#deployment) · [ConfigMap](../YAML_Guide.md#configmap) |
| `04-configmap-rose.yaml` | ConfigMap | เปลี่ยน `THEME` เป็น `rose` | [ConfigMap](../YAML_Guide.md#configmap) |

ค่าจริงจาก `02-configmap.yaml`:

```yaml
data:
  SITE_NAME: "ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์"
  THEME: amber
```

จุดอ้าง ConfigMap จริงจาก `03-web-envfrom.yaml`:

```yaml
envFrom:
  - configMapRef:
      name: web-config
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `data` | map ที่ค่าทุกตัวต้องเป็น string | Pod ใหม่จะได้รับค่าใหม่; env ของ Pod เดิมไม่เปลี่ยน |
| `envFrom.configMapRef.name` | นำทุก key จาก ConfigMap ชื่อนี้เข้า env | สะกดชื่อผิดแล้ว Container ใหม่เริ่มไม่ได้ |
| `configMapKeyRef` | เลือกเพียง key เดียวและตั้งชื่อ env ใหม่ได้ | กลไกนี้ไม่มีใน YAML ของ LAB 010 จึงไม่แต่ง snippet เพิ่ม |
| ConfigMap volume | mount key เป็นไฟล์และอัปเดตไฟล์ได้ภายหลัง | ไม่มีใน YAML นี้; process ต้อง reload ไฟล์เอง |

**ผิดบ่อยในแล็บนี้:** runlog บันทึกสถานะจริง `CreateContainerConfigError` และ Event `Error: configmap "web-confg" not found` เมื่อชื่อใน `configMapRef` ผิด ให้ใช้ `kubectl describe pod` หา ref ที่หาไม่พบ

ดู schema ได้ด้วย `kubectl explain configmap.data` และ `kubectl explain deployment.spec.template.spec.containers.envFrom.configMapRef`

## 3. เปิดหน้าเว็บด้วยค่า default จาก image

ไฟล์ `01-web.yaml` มี Deployment, Service และ Ingress แบบ path-only; Service หา Pod ด้วย label `app: web` และ Ingress ส่ง `/` ไปพอร์ต 3000
```bash
kubectl create namespace lab010
kubectl apply -f 01-web.yaml
kubectl wait -n lab010 --for=condition=available deployment/web --timeout=120s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
```
> 📝 **คำอธิบาย:** `create namespace` แยก object ของแล็บ · `apply -f` ส่ง desired state จากไฟล์ · `--for=condition=available` รอ Deployment ใช้งานได้ · `--timeout` จำกัดเวลารอ

✅ **Expected output** — namespace และประตูเว็บถูกสร้าง แล้ว Deployment available:
```text
namespace/lab010 created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/web condition met
```
ดูค่าที่ container ได้รับและค่าที่หน้าเว็บตอบ:
```bash
kubectl exec -n lab010 deploy/web -- sh -c "env | grep -E 'SITE_NAME|THEME' || true"
curl -s http://localhost/info | jq -c '{site_name,theme,pod,version}'
```
> 📝 **คำอธิบาย:** `exec` รันใน Pod ของ Deployment · `grep -E` ค้นหลายชื่อ · `|| true` ยอมให้ไปต่อเมื่อไม่พบตัวแปร · `curl /info` อ่านหลักฐานจากแอปจริง · `jq` เลือก field สำคัญ

✅ **Expected output** — ยังไม่มี `SITE_NAME`/`THEME` จากภายนอก จึงใช้ default blue; ชื่อ Pod ต่างกันได้:
```text
DEFAULT_THEME=blue
{"site_name":"SkillSpace","theme":"blue","pod":"web-65665dddc4-4k49k","version":"v1"}
```

## 4. สร้าง ConfigMap สำหรับค่าที่ไม่ลับ

หัวใจของ `02-configmap.yaml` คือ:
```yaml
kind: ConfigMap
metadata:
  name: web-config
data:
  SITE_NAME: "ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์"
  THEME: amber
```
`metadata.name` คือชื่อที่ Deployment จะอ้าง · `data` เป็นคู่ key/value แบบข้อความ · ค่านี้ไม่ใช่ข้อมูลลับ
```bash
kubectl apply -f 02-configmap.yaml
kubectl get configmap web-config -n lab010 -o yaml
```
> 📝 **คำอธิบาย:** `apply` สร้าง object · `get configmap` อ่านกลับจาก API server · `-o yaml` แสดงทั้ง data และ metadata

✅ **Expected output** — เห็นสอง key ที่ส่งเข้า cluster (ตัดบางแถวจาก metadata):
```text
configmap/web-config created
…
data:
  SITE_NAME: ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์
  THEME: amber
```

## 5. ส่ง ConfigMap เข้า container ด้วย envFrom

ส่วนสำคัญของ `03-web-envfrom.yaml` คือ:
```yaml
envFrom:
  - configMapRef:
      name: web-config
```
`envFrom` นำทุก key เข้าเป็น environment variable ส่วน `configMapRef.name` ต้องตรงกับ object ที่สร้างไว้
```bash
kubectl apply -f 03-web-envfrom.yaml
kubectl rollout status -n lab010 deployment/web --timeout=120s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
kubectl exec -n lab010 deploy/web -- sh -c "env | grep -E 'SITE_NAME|THEME' | sort"
```
> 📝 **คำอธิบาย:** การแก้ Pod template ทำให้ Deployment rollout Pod ใหม่ · `rollout status` รอการแทนที่ · `sort` ทำให้ผลอ่านเทียบง่าย

✅ **Expected output** — Pod ใหม่เห็นชื่อระบบและ amber:
```text
deployment.apps/web configured
deployment "web" successfully rolled out
DEFAULT_THEME=blue
SITE_NAME=ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์
THEME=amber
```

![หน้าเว็บอ่านชื่อระบบและ theme amber จาก ConfigMap](images/03-web-amber-new-name.png)

## 6. เปลี่ยน ConfigMap แล้วสังเกตว่า Pod เดิมยังไม่เปลี่ยน
```bash
kubectl apply -f 04-configmap-rose.yaml
kubectl get configmap web-config -n lab010 -o jsonpath='{.data.THEME}{"\n"}'
curl -s http://localhost/info | jq -c '{site_name,theme,pod}'
```
> 📝 **คำอธิบาย:** ไฟล์ใหม่ตั้ง `THEME=rose` · `jsonpath` อ่านค่าจาก ConfigMap โดยตรง · `/info` อ่านค่าที่ process ปัจจุบันใช้จริง

✅ **Expected output** — ConfigMap เป็น rose แต่ Pod เดิมยังตอบ amber:
```text
configmap/web-config configured
rose
{"site_name":"ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์","theme":"amber","pod":"web-7dd74555f6-vf45n"}
```
environment variable ถูกสร้างตอน container เริ่ม ไม่ได้ติดตาม ConfigMap แบบ live

## 7. Restart ให้ Pod ใหม่อ่านค่า rose
```bash
kubectl rollout restart -n lab010 deployment/web
kubectl rollout status -n lab010 deployment/web --timeout=120s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s --max-time 5 http://localhost/info | jq -c '{site_name,theme,pod}'
```
> 📝 **คำอธิบาย:** `rollout restart` เปลี่ยน annotation ใน Pod template · Deployment จึงสร้าง Pod ใหม่ · `--max-time` กัน curl ค้าง · Pod ใหม่อ่าน ConfigMap ล่าสุดตอนเริ่ม

✅ **Expected output** — เว็บเปลี่ยนเป็น rose; ชื่อ Pod/hash ต่างกันได้:
```text
deployment.apps/web restarted
deployment "web" successfully rolled out
{"site_name":"ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์","theme":"rose","pod":"web-556f5fbfc7-pbk5d"}
```

![หน้าเว็บเปลี่ยนเป็น theme rose หลัง restart](images/04-web-rose-after-restart.png)

ถ้า rollout เพิ่งจบ Ingress อาจตอบ 503 ชั่วครู่ระหว่าง EndpointSlice อัปเดต ให้รอ 1–2 วินาทีแล้วตรวจซ้ำ

## 8. เลือก envFrom หรือ valueFrom ให้เหมาะ

`envFrom` เหมาะเมื่อ Pod ใช้ทุก key ใน ConfigMap ส่วน `valueFrom.configMapKeyRef` เหมาะเมื่ออยากเลือก key และตั้งชื่อ environment variable ใหม่ การ mount ConfigMap เป็นไฟล์สามารถเห็นการอัปเดตไฟล์ภายหลังได้ แต่ process ต้องออกแบบให้ reload ไฟล์เอง แล็บนี้จงใจใช้ environment variable เพื่อให้เห็นขอบเขตชัดเจน

## 9. ทดลองให้พัง — อ้างชื่อ ConfigMap ผิด

ทำชื่อ `web-config` หล่นตัวอักษรหนึ่งตัว:
```bash
kubectl patch deployment web -n lab010 --type=strategic -p '{"spec":{"template":{"spec":{"containers":[{"name":"web","envFrom":[{"configMapRef":{"name":"web-confg"}}]}]}}}}'
kubectl rollout status -n lab010 deployment/web --timeout=10s || true
kubectl get pods -n lab010
```
> 📝 **คำอธิบาย:** `patch` เปลี่ยนเฉพาะ Pod template · `--type=strategic` merge container ตามชื่อ · timeout สั้นทำให้เห็น rollout ค้าง · `|| true` ให้ทำขั้นอ่านอาการต่อได้

✅ **Expected output** — Pod ใหม่ค้าง แต่ Pod เก่ายัง Running; ชื่อ/hash/AGE ต่างกันได้:
```text
deployment.apps/web patched
error: timed out waiting for the condition
NAME                   READY   STATUS                       RESTARTS   AGE
web-556f5fbfc7-pbk5d   1/1     Running                      0          112s
web-5c57687654-j82s8   0/1     CreateContainerConfigError   0          11s
```
อ่านสาเหตุจาก Event แล้วพิสูจน์ว่าเว็บเก่ายังให้บริการ:
```bash
kubectl get events -n lab010 --sort-by=.lastTimestamp
curl -s --max-time 5 http://localhost/info | jq -c '{theme,pod}'
```
> 📝 **คำอธิบาย:** `--sort-by` เรียงเหตุการณ์ตามเวลา · Event เปิดเผย object ที่หาไม่เจอ · Deployment ไม่ปิด Pod เก่าจนกว่าตัวใหม่พร้อม

✅ **Expected output** — พบชื่อ ConfigMap ผิด และเว็บยังเป็น rose (ตัดบางแถวจาก Events):
```text
…
Warning   Failed   pod/web-5c57687654-j82s8   Error: configmap "web-confg" not found
{"theme":"rose","pod":"web-556f5fbfc7-pbk5d"}
```
แก้กลับด้วย manifest ที่ถูกต้อง:
```bash
kubectl apply -f 03-web-envfrom.yaml
kubectl rollout status -n lab010 deployment/web --timeout=120s
kubectl get pods -n lab010
```
> 📝 **คำอธิบาย:** apply คืน reference เป็น `web-config` · Deployment scale ReplicaSet ที่พังลง 0 · rollout สำเร็จโดย Pod เก่ายังให้บริการ

✅ **Expected output** — rollout กลับมาปกติและ Pod ที่พังกำลังหายไป:
```text
deployment.apps/web configured
deployment "web" successfully rolled out
NAME                   READY   STATUS        RESTARTS   AGE
web-556f5fbfc7-pbk5d   1/1     Running       0          113s
web-5c57687654-j82s8   0/1     Terminating   0          12s
```

## 10. แบบฝึกหัดสั้น (Exercise)

เพิ่ม key `BANNER_TEXT` ใน ConfigMap แล้วส่งเข้า Pod ด้วย `valueFrom.configMapKeyRef` แทน `envFrom` โดยไม่เปลี่ยน image เกณฑ์สำเร็จคือ Pod ใหม่เป็น Running, environment variable มีข้อความที่ตั้ง และสามารถอธิบายได้ว่าทำไมต้องสร้าง Pod ใหม่

## วิธีตรวจสอบผลการทดลอง
```bash
kubectl get all,ingress,configmap -n lab010
kubectl logs -n lab010 deployment/web --tail=8
curl -s http://localhost/info | jq -c '{site_name,theme,pod,version}'
```
> 📝 **คำอธิบาย:** `get all` ตรวจ desired/actual state · เพิ่ม `ingress,configmap` เพราะไม่รวมใน all · `logs` เป็นหลักฐานจาก process · `/info` เป็นหลักฐานจากมุมผู้ใช้

✅ **Expected output** — Deployment `1/1`, Pod Running, log มี `Ready`, และ `/info` ตอบชื่อใหม่/theme rose (ตัดบางแถว/บางคอลัมน์):
```text
…
deployment.apps/web   1/1   1   1
▲ Next.js 16.3.1
✓ Ready in 0ms
{"site_name":"ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์","theme":"rose","pod":"web-556f5fbfc7-pbk5d","version":"v1"}
```
ค่า Pod, IP, AGE, hash และเวลาในทุกบล็อกต่างกันได้

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `CreateContainerConfigError` | ชื่อ ConfigMap/key ผิด | อ่าน Events แล้วเทียบ `configMapRef` |
| ConfigMap เป็น rose แต่เว็บยัง amber | env ของ Pod เดิมไม่ reload | restart Deployment |
| curl ได้ HTML 503 หลัง rollout | Ingress/EndpointSlice ยัง sync | รอ 1–2 วินาทีแล้วตรวจซ้ำ |
| `ImagePullBackOff` | ยังไม่ได้ load image เข้า kind | กลับไป build/load ใน LAB 001 |
| หน้าเว็บเปิดไม่ได้ | ingress-nginx หรือ Service ยังไม่พร้อม | ตรวจ Pod, Service, Ingress ตามลำดับ |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

ลบทั้งห้องและพิสูจน์ว่าไม่เหลือ resource:
```bash
kubectl delete namespace lab010 --wait=true
kubectl get all -n lab010
```
> 📝 **คำอธิบาย:** การลบ namespace ลบ object ที่อยู่ข้างในทั้งหมด · `--wait=true` รอจนลบเสร็จ · `get all` ตรวจซ้ำ

✅ **Expected output** — namespace ถูกลบและไม่มี resource:
```text
namespace "lab010" deleted
No resources found in lab010 namespace.
```
สร้างใหม่จากไฟล์และยืนยันผลเดิม:
```bash
kubectl create namespace lab010
kubectl apply -f 04-configmap-rose.yaml -f 01-web.yaml -f 03-web-envfrom.yaml
kubectl rollout status -n lab010 deployment/web --timeout=120s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{site_name,theme,version}'
```
> 📝 **คำอธิบาย:** เริ่มจาก namespace ว่าง · apply ConfigMap/ประตู/Deployment · wait ให้พร้อม · ตรวจพฤติกรรม ไม่ใช่ดูแค่สถานะ Pod

✅ **Expected output** — clean run ให้ผล rose เหมือนเดิม:
```text
namespace/lab010 created
configmap/web-config created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/web configured
deployment "web" successfully rolled out
{"site_name":"ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์","theme":"rose","version":"v1"}
```
ลบปิดท้ายอีกครั้ง:
```bash
kubectl delete namespace lab010 --wait=true
kubectl get all -n lab010
```
> 📝 **คำอธิบาย:** ลบสภาพ Clean Re-run · ตรวจ namespace เดิมอีกครั้งเพื่อไม่ทิ้งของชน LAB ถัดไป

✅ **Expected output** — จบสะอาด:
```text
namespace "lab010" deleted
No resources found in lab010 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl apply -f 02-configmap.yaml` | สร้าง ConfigMap |
| `kubectl get configmap ... -o yaml` | อ่านค่าที่ API server เก็บ |
| `kubectl rollout restart deployment/web` | สร้าง Pod ใหม่ให้อ่าน env ล่าสุด |
| `kubectl get events --sort-by=.lastTimestamp` | อ่านสาเหตุจากเหตุการณ์ |
| `curl .../info` | ตรวจค่าที่แอปใช้จริง |
| `kubectl delete namespace lab010` | ล้างแล็บทั้งห้อง |

## สรุปสิ่งที่ได้เรียนรู้

ConfigMap ทำให้ image หนึ่งชุดเปลี่ยนชื่อระบบและสีตาม environment ได้ แต่ environment variable เป็น snapshot ตอน container เริ่ม การเปลี่ยน ConfigMap จึงต้องตามด้วย Pod ใหม่ และ reference ที่ผิดจะกันไม่ให้ container เริ่ม

- แยก config ที่ไม่ลับออกจาก image ได้
- อธิบาย `envFrom` และ `valueFrom` ได้
- อ่าน `CreateContainerConfigError` จาก Events ได้
- พิสูจน์ Clean Re-run และจบโดยไม่มี resource ค้างได้

**จำภาพเดียวให้ได้:** image คือกล่องเดิม ส่วน ConfigMap คือป้ายตั้งค่าที่ติดให้กล่องตอนเปิดใช้งาน

🧭 ต่อยอด: [LAB 11 — Secret และเหตุผลที่ base64 ไม่ใช่ encryption](../011-secret-and-why-not-configmap/README.md)

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **ถ้าฝัง config ใน image จะมีปัญหาอะไร?** — เปลี่ยนค่าเดียวก็ต้อง build/push/deploy ใหม่ และ image เดียวใช้หลาย environment ยาก
2. **ทำไมแก้ ConfigMap แล้วเว็บไม่เปลี่ยนทันที?** — environment variable ถูก inject ตอนสร้าง container จึงต้องสร้าง Pod ใหม่
3. **ConfigMap ควรเก็บอะไร?** — ชื่อระบบ สี URL และค่าที่ไม่ลับ; รหัสผ่านใช้ Secret

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] cluster 3 nodes เป็น Ready และ image อยู่ใน kind
- [ ] เห็นหน้า amber และ rose จาก image เดิม
- [ ] อธิบายได้ว่าทำไมต้อง restart
- [ ] อ่าน Event ของชื่อ ConfigMap ผิดได้
- [ ] Clean Re-run ผ่านและลบ `lab010` แล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
