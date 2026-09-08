# LAB 15 — Assembling a Real Application : ต่อ object ให้กลายเป็นระบบ

> โฟลเดอร์ `015-assembling-a-real-application` = LAB 15 ของชุด Kubernetes ครั้งที่ 3
> (ไฟล์ของแล็บนี้: `manifests/01-configmap.yaml` ถึง `manifests/06-ingress.yaml`)

> 💡 **แนวคิดหลักของแล็บนี้:** แอปจริงคือหลาย object ที่ทำงานร่วมกัน ไม่ใช่ object เดียว

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:
1. อธิบายหน้าที่ของ Deployment, Service, ConfigMap และ Ingress ในระบบเดียวกันได้
2. ไล่เส้นทาง request จาก browser ไปถึง web และ api Pod ได้
3. ทำนายอาการเมื่อ Service, Ingress หรือ ConfigMap หายได้
4. อธิบายได้ว่าทำไม apply ทั้งโฟลเดอร์ซ้ำแล้วซ่อมเฉพาะส่วนที่ต่าง

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ใน Compose หนึ่ง service รวมเรื่อง process, network name และ runtime config ไว้ใน block เดียว
Kubernetes แยกความรับผิดชอบออกเป็น object เล็ก ๆ ที่ controller ดูแลแยกกัน:
| Compose | Kubernetes object | หน้าที่ในแล็บนี้ |
|---|---|---|
| `service: web` | web Deployment + Service | รันหน้าเว็บสอง Pod และให้ชื่อ `web` |
| `service: api` | api Deployment + Service | รัน API สอง Pod และให้ชื่อ `api` |
| `environment:` | ConfigMap | ส่ง SITE_NAME, THEME และ API_BASE_URL |
| `ports:` / proxy | Ingress | เปิด `/` จากภายนอกไป Service web |
แล็บนี้ตั้งใจยังไม่มี PostgreSQL การ์ด web และ api จึงเชื่อมต่อได้ แต่ db แสดง `down`
นี่คือ baseline ที่ถูกต้องก่อนเพิ่ม stateful layer ใน LAB 16
ไฟล์ใน `manifests/` คือ source of truth: ของที่ตรงอยู่แล้วเป็น `unchanged`
ของที่หายเป็น `created` และของที่ต่างเป็น `configured`

## สิ่งที่จะได้เรียนรู้

- จะได้ apply object หลายชนิดด้วยคำสั่งเดียว
- จะได้เห็น web/api กระจายอยู่คนละ node
- จะได้เปิดระบบผ่าน Ingress ที่ URL เดียว
- จะได้ลบ API Service ทั้งที่ Pod ยัง Running
- จะได้ลบ Ingress และเห็น 404 จาก ingress-nginx
- จะได้ใช้ apply ซ้ำเพื่อสร้างเฉพาะ object ที่หาย
- จะได้ทำให้ ConfigMap หายและเห็น `CreateContainerConfigError`
- จะได้พิสูจน์ว่าของเก่ายังให้บริการระหว่าง rollout ที่ของใหม่ไม่พร้อม

## ภาพรวมของแล็บนี้

1. อ่าน manifest หกไฟล์และ map แต่ละไฟล์กับหน้าที่
2. apply ทั้งโฟลเดอร์แล้วเปิดหน้าเว็บจริง
3. ลบ Service และ Ingress ทีละตัว แล้ว apply คืน
4. เปรียบเทียบไฟล์กับ actual state
5. ลบ ConfigMap, restart web, อ่านอาการ แล้วซ่อมจากไฟล์
6. Cleanup และ Clean Re-run

![เส้นทาง Browser ผ่าน Ingress และ Service ไปยัง web กับ api](../slides_assets/lab015-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า api Pod ยัง Running แต่ Service `api` หาย หน้าเว็บจะหา API เจอจากอะไร?

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** คำสั่งแรก start เครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` คือเข้าเครื่องเรียน (ทุกคำสั่งหลังจากนี้พิมพ์ในเครื่องเรียน) · `k8s-bootstrap` จะข้ามเองถ้า cluster มีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน kind node
ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `localhost:8080`

✅ **Expected output** — node พร้อมและมี image แอปครบ; ชื่อ node, AGE, image ID และ version ต่างกันได้:
```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready   control-plane   20m   v1.36.4
devtools-worker          Ready   <none>          20m   v1.36.4
devtools-worker2         Ready   <none>          20m   v1.36.4
docker.io/library/k8s-lab-api   v1   c662b53377da4   186MB
docker.io/library/k8s-lab-db    v1   9bb05e9c07722   300MB
docker.io/library/k8s-lab-web   v1   c07ef6ef4b6a3   209MB
docker.io/library/k8s-lab-web   v2   685541d4b6ff0   209MB
```
ชื่อ Pod, hash และ AGE ต่างกันได้ ถ้าผล `grep` ว่าง → ทำขั้น build/load ใน README ระดับชุดหรือ LAB 001

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace · `&&` ทำต่อเมื่อสำเร็จ · `git clone` ดาวน์โหลด repository

✅ **Expected output** — clone เริ่มสำเร็จ:
```text
Cloning into 'DevTools'...
```
```bash
cd ~/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-application
pwd
```
> 📝 **คำอธิบาย:** `cd` เข้า LAB 15 ของครั้งที่ 3 · `pwd` ยืนยัน working directory ก่อน apply ทั้งโฟลเดอร์

✅ **Expected output** — path ถูกต้อง:
```text
/root/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-application
```
ถ้า clone ไว้แล้วให้อัปเดตก่อน:
```bash
cd ~/labwork/DevTools && git pull
```
> 📝 **คำอธิบาย:** `git pull` ดึงและรวม commit ล่าสุดของ branch ปัจจุบัน

✅ **Expected output** — repository ล่าสุดแล้ว:
```text
Already up to date.
```

## 2. อ่าน YAML ของแล็บนี้

แล็บนี้เริ่มอ่าน “ทั้งระบบ” จากชื่อไฟล์เรียง `01-` ถึง `06-`: config มาก่อน workload แล้วจึง network
แต่ละไฟล์ยังเป็น object อิสระ และ `kubectl apply -f manifests/` ส่ง desired state ทั้ง directory

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/01-configmap.yaml` | ConfigMap | ให้ `SITE_NAME`, `THEME`, `API_BASE_URL` แก่ web | [ทบทวน ConfigMap](../YAML_Guide.md#configmap) |
| `manifests/02-web-deployment.yaml` | Deployment | รัน web 2 replicas และอ่าน ConfigMap | [ทบทวน Deployment](../YAML_Guide.md#deployment) |
| `manifests/03-web-service.yaml` | Service | ให้ชื่อคงที่ `web` และ port 3000 | [ทบทวน Service](../YAML_Guide.md#service) |
| `manifests/04-api-deployment.yaml` | Deployment | รัน api 2 replicas | [ทบทวน Deployment](../YAML_Guide.md#deployment) |
| `manifests/05-api-service.yaml` | Service | ให้ web เรียก api ผ่านชื่อ `api` | [ทบทวน Service](../YAML_Guide.md#service) |
| `manifests/06-ingress.yaml` | Ingress | เปิด path `/` ไป Service web | [Ingress](../YAML_Guide.md#1-ingress) |

ลองอ่านชื่อก่อนเปิดไฟล์: `01-configmap.yaml` ควรถูกอ้างโดย `02-web-deployment.yaml`, label ของ
`02-web-deployment.yaml` ควรถูกเลือกโดย `03-web-service.yaml` และ Ingress ควรชี้ Service ไม่ใช่ Pod

**ผิดบ่อยในแล็บนี้:** ลบ ConfigMap แล้ว restart ทำให้ Pod ใหม่เป็น `CreateContainerConfigError`;
runlog ระบุข้อความจริง `Error: configmap "web-config" not found` การ apply ทั้ง directory ซ้ำจึงเป็นการคืนแหล่งความจริงให้ระบบ

ดู field ได้ด้วย `kubectl explain configmap.data`, `kubectl explain deployment.spec.template.spec` และ `kubectl explain ingress.spec.rules`

## 3. อ่านโฟลเดอร์ manifests ก่อน deploy

```bash
ls -1 manifests/
cat manifests/01-configmap.yaml
cat manifests/02-web-deployment.yaml
```
> 📝 **คำอธิบาย:** `ls -1` แสดงลำดับไฟล์ · `cat` แสดง YAML จริงทั้งไฟล์โดยไม่แก้ไข

✅ **Expected output** — พบไฟล์ 01 ถึง 06 ตามลำดับ (ตัดข้อความท้ายจาก `cat`; YAML สำคัญแสดงถัดไป):
```text
01-configmap.yaml
02-web-deployment.yaml
03-web-service.yaml
04-api-deployment.yaml
05-api-service.yaml
06-ingress.yaml
…
```
ส่วนที่ต้องสังเกตจาก `02-web-deployment.yaml` คือ:
```yaml
envFrom:
  - configMapRef:
      name: web-config
env:
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
```
> 📝 **อ่านทีละ field:** `envFrom` นำทุก key จาก ConfigMap เข้า environment · `configMapRef.name` ชี้ `web-config` · `fieldRef` อ่านข้อมูลของ Pod · `metadata.name` สร้าง `POD_NAME` · `spec.nodeName` สร้าง `NODE_NAME`

## 4. Apply ระบบทั้งชุด

```bash
kubectl create namespace lab015
kubectl apply -f manifests/
kubectl rollout status deployment/web -n lab015 --timeout=180s
kubectl rollout status deployment/api -n lab015 --timeout=180s
kubectl get all,ingress,configmap -n lab015 -o wide
```
> 📝 **คำอธิบาย:** สร้าง namespace ของแล็บ · `apply -f manifests/` อ่าน YAML ทุกไฟล์ใน directory · `rollout status` รอ Deployment แต่ละตัว · `get all,ingress,configmap` รวม object ที่ `all` ไม่ครอบคลุม · `-o wide` แสดง node/IP

✅ **Expected output** — web/api พร้อมอย่างละสอง Pod และ Ingress เปิด port 80 (ตัดบางแถว):
```text
configmap/web-config created
…
ingress.networking.k8s.io/web created
deployment "web" successfully rolled out
deployment "api" successfully rolled out
deployment.apps/web   2/2   2   2
deployment.apps/api   2/2   2   2
```

## 5. เปิดหน้าเว็บและอ่านสถานะที่ตั้งใจไว้

```bash
kubectl exec deployment/web -n lab015 -- wget -qO- http://api:8000/health
until curl -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
kubectl logs deployment/api -n lab015 --tail=8
```
> 📝 **คำอธิบาย:** `exec` พิสูจน์ web เรียก api ด้วย Service DNS · `/health` ไม่ต้องมี db · `/info` แสดง Pod ที่ตอบจริง · `logs --tail=8` ยืนยันว่า API เปิดบริการแม้ db ยังไม่มี

✅ **Expected output** — web กับ api เชื่อมกัน ส่วน db down ตามแผน:
```text
{"status":"ok","pod":"api-59d8fcb74b-v86vp","version":"v1"}
{"pod":"web-64b77cf7f4-c487j","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-59d8fcb74b-5llqm"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
[api] startup db=down ([Errno -5] No address associated with hostname) — API ยังให้บริการต่อ
```
ชื่อ Pod, node, IP, hash และเวลาต่างกันได้

![ระบบ web และ api ทำงานร่วมกัน โดยตั้งใจยังไม่มี db](images/03-web-api-assembled-no-db.png)

## 6. ถอด Service และ Ingress ทีละชิ้น

ลบ API Service ก่อน โดยไม่แตะ API Pod:
```bash
kubectl delete service api -n lab015
kubectl get pods,service,endpoints -n lab015
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** `delete service` ลบชื่อ DNS และตัวกระจายโหลด · `get pods,service,endpoints` พิสูจน์ว่า API Pod ยัง Running แต่ทางเชื่อมหาย · `/info` แสดงอาการที่ web เห็น

✅ **Expected output** — API Pod ยัง 1/1 แต่สถานะหน้าเว็บเป็น unreachable:
```text
service "api" deleted from lab015 namespace
pod/api-59d8fcb74b-5llqm   1/1   Running
pod/api-59d8fcb74b-v86vp   1/1   Running
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
{"pod":"web-64b77cf7f4-xzkzj","version":"v1","theme":"blue","api":{"configured":true,"reachable":false,"error":"fetch failed"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
```
คำเตือนเกิดเพราะ Kubernetes 1.33+ แนะนำ EndpointSlice แทน Endpoints แต่ไม่ทำให้การทดลองล้มเหลว

![Pod api ยังอยู่ แต่ขาด Service จึงเรียกด้วยชื่อ api ไม่ได้](images/04-api-service-deleted.png)
ใช้ source of truth ซ่อม แล้วทดลองประตู:
```bash
kubectl apply -f manifests/
kubectl exec deployment/web -n lab015 -- sh -c 'until wget -qO- http://api:8000/health; do sleep 2; done'
kubectl delete ingress web -n lab015
for i in $(seq 1 4); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/; sleep 2; done
kubectl apply -f manifests/
```
> 📝 **คำอธิบาย:** apply สร้าง Service ที่หาย · loop `wget` รอ DNS/endpoint; ถ้าเห็น `bad address` ให้รอ 5–10 วินาทีแล้วรันซ้ำ · loop `curl` แสดงช่วง ingress-nginx sync · apply คืนประตู

✅ **Expected output** — Service ถูกสร้างกลับ, Ingress เปลี่ยนจาก 200 เป็น 404 แล้วสร้างกลับ:
```text
service/api created
{"status":"ok","pod":"api-59d8fcb74b-5llqm","version":"v1"}
ingress.networking.k8s.io "web" deleted from lab015 namespace
200
200
404
404
ingress.networking.k8s.io/web created
```
การเปลี่ยน rule ไม่เกิดพร้อมคำสั่ง delete ในทันที เพราะ ingress controller ต้อง sync configuration ก่อน

## 7. เปรียบเทียบไฟล์กับ actual state

```bash
kubectl get -f manifests/
kubectl diff -f manifests/ || true
kubectl get pods -n lab015 -o wide
```
> 📝 **คำอธิบาย:** `get -f` ขอ object ที่ประกาศในไฟล์แทนการจำชนิด · `diff -f` เทียบ desired กับ live · `|| true` ให้ขั้นเรียนต่อได้เมื่อ diff ใช้ exit code 1 เพื่อบอกว่าต่าง · `-o wide` แสดงการกระจาย Pod ข้าม node

✅ **Expected output** — object ทุกตัวพบครบ, diff ว่าง และ Pod กระจายสอง worker:
```text
configmap/web-config   3
deployment.apps/web   2/2   2   2
service/web   ClusterIP
deployment.apps/api   2/2   2   2
service/api   ClusterIP
ingress.networking.k8s.io/web   nginx   *   80
web-64b77cf7f4-c487j   1/1   Running   devtools-worker2
api-59d8fcb74b-5llqm   1/1   Running   devtools-worker
```

## 8. ทดลองให้พัง — ลบ ConfigMap แล้ว restart web

```bash
kubectl delete configmap web-config -n lab015
kubectl rollout restart deployment/web -n lab015
sleep 5
kubectl get pods -n lab015 -l app=web
kubectl get events -n lab015 --sort-by=.lastTimestamp | tail -15
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/
```
> 📝 **คำอธิบาย:** ลบ config ที่ Pod ใหม่ต้องอ่าน · `rollout restart` เปลี่ยน Pod template ให้สร้าง revision ใหม่ · `get pods` เห็นของใหม่พังและของเก่ายังคงอยู่ · Events ระบุชื่อ ConfigMap · HTTP ตรวจว่าผู้ใช้ยังเข้าเว็บผ่าน Pod เก่าได้

✅ **Expected output** — Pod ใหม่ `CreateContainerConfigError`, Event บอก not found แต่เว็บยัง 200:
```text
web-5d848685f6-qt5nt   0/1   CreateContainerConfigError   0   12s
web-64b77cf7f4-c487j   1/1   Running                      0   100s
web-64b77cf7f4-xzkzj   1/1   Running                      0   100s
Warning  Failed  Error: configmap "web-config" not found
200
```
แก้กลับจาก manifest ทั้งชุด:
```bash
kubectl apply -f manifests/
kubectl rollout status deployment/web -n lab015 --timeout=180s
kubectl get pods -n lab015 -l app=web
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** apply สร้าง ConfigMap ที่หาย ส่วน object อื่น unchanged · rollout เดินต่อเองเมื่อ Pod ใหม่อ่าน config ได้ · ตรวจ Pod และ response จริง

✅ **Expected output** — ConfigMap ถูกสร้าง, rollout จบ และ API กลับ reachable:
```text
configmap/web-config created
deployment.apps/web unchanged
deployment "web" successfully rolled out
web-5d848685f6-j5f9q   1/1   Running
{"pod":"web-5d848685f6-j5f9q","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-59d8fcb74b-5llqm"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
```

## 9. แบบฝึกหัดสั้น (Exercise)

วาดตาราง object หกตัว แล้วทำนายอาการเมื่อ replicas ของ web เป็นศูนย์โดยไม่รันก่อน
จากนั้นทดลองใน namespace ของตนเองและอธิบายว่า Ingress, Service และ endpoints ตัวใดยังอยู่
เกณฑ์สำเร็จคือแยก “object หาย” ออกจาก “object อยู่แต่ไม่มีปลายทาง” ได้

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get all,ingress,configmap -n lab015
kubectl get endpoints -n lab015
kubectl exec deployment/web -n lab015 -- wget -qO- http://api:8000/health
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
kubectl logs deployment/api -n lab015 --tail=8
```
> 📝 **คำอธิบาย:** ตรวจ object, endpoint, การเรียกภายใน, เส้นทางภายนอก และ log แอปครบสามมุม · `--tail` จำกัดหลักฐานล่าสุด

✅ **Expected output** — web/api พร้อมอย่างละสอง, endpoints มี IP และ api reachable แม้ db down:
```text
deployment.apps/api   2/2   2   2
deployment.apps/web   2/2   2   2
api   10.244.1.29:8000,10.244.2.17:8000
web   10.244.1.28:3000,10.244.2.16:3000
{"pod":"web-5d848685f6-j5f9q","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-59d8fcb74b-5llqm"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| API Pod Running แต่ web fetch failed | Service `api` หายหรือ DNS cache ยังไม่หมด | apply manifests แล้วทดสอบ `/health` จาก web |
| หน้า Ingress ตอบ 404 หลัง apply | controller ยังไม่ sync rule | poll HTTP 200 และดู ingress-nginx Pod |
| web Pod เป็น CreateContainerConfigError | `web-config` ไม่มี | ดู Events แล้ว apply `01-configmap.yaml` |
| การ์ด db แดง | LAB 15 ตั้งใจยังไม่มี db | ไป LAB 16 เพื่อเพิ่ม Secret/PVC/db |
| `kubectl diff` ไม่มี output | live state ตรงกับไฟล์ | ถือว่าผ่าน ไม่ใช่คำสั่งเสีย |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab015
kubectl wait --for=delete namespace/lab015 --timeout=180s
kubectl create namespace lab015
kubectl apply -f manifests/
kubectl rollout status deployment/web -n lab015 --timeout=180s
kubectl rollout status deployment/api -n lab015 --timeout=180s
for i in $(seq 1 15); do code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/); echo "HTTP $code"; [ "$code" = 200 ] && break; sleep 2; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** ลบและรอ namespace เดิม · สร้างจาก source of truth · รอ Deployment · poll Ingress เพราะ rule sync ช้ากว่า Pod ได้ · หยุด loop เมื่อ HTTP 200 · `/info` ยืนยันผลเดิม

✅ **Expected output** — Clean Re-run ผ่านหลัง Ingress sync:
```text
namespace/lab015 created
deployment "web" successfully rolled out
deployment "api" successfully rolled out
HTTP 404
HTTP 200
{"pod":"web-64b77cf7f4-wrdhw","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-59d8fcb74b-zndcm"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
```
```bash
kubectl delete namespace lab015
kubectl wait --for=delete namespace/lab015 --timeout=180s
kubectl get all -n lab015
```
> 📝 **คำอธิบาย:** ลบ namespace รอบสุดท้าย · รอจน API server ยืนยันว่าหาย · ตรวจว่า workload และ Service ไม่ค้าง

✅ **Expected output** — จบสะอาด:
```text
namespace "lab015" deleted
No resources found in lab015 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl apply -f manifests/` | ทำ actual state ให้ตรงทุกไฟล์ในโฟลเดอร์ |
| `kubectl rollout restart deployment/web` | สร้าง Pod revision ใหม่ |
| `kubectl get events` | อ่านสาเหตุจาก controller/kubelet |

## สรุปสิ่งที่ได้เรียนรู้

ระบบจริงเกิดจาก object หลายตัวรับผิดชอบคนละเรื่องและเชื่อมกันด้วยชื่อกับ labels
- Deployment ดูแลจำนวนและการเปลี่ยน Pod
- Service ให้ชื่อคงที่และเลือกปลายทาง
- ConfigMap ส่งค่ารันโดยไม่ฝังใน image
- Ingress เป็นประตูจากภายนอกเข้าสู่ Service
- apply ทั้งโฟลเดอร์ซ่อม object ที่หายได้แบบ declarative
**จำภาพเดียวให้ได้:** Deployment สร้างคนทำงาน, Service ให้เบอร์กลาง, ConfigMap ส่งคู่มือ และ Ingress เปิดประตู
🧭 ต่อยอด: LAB 16 จะเพิ่ม PostgreSQL, Secret และ PVC ให้ระบบนี้ครบสามชั้น

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **แต่ละ object ทำหน้าที่อะไร?** — Deployment รัน/ดูแล Pod, Service ให้ชื่อและ endpoint, ConfigMap ให้ค่า, Ingress เปิดทางเข้า
2. **ถ้าขาดตัวไหนจะเกิดอะไร?** — ขาด API Service web หา API ไม่เจอ; ขาด Ingress ภายนอกได้ 404; ขาด ConfigMap Pod ใหม่เริ่มไม่ได้
3. **ทำไม apply ทั้งโฟลเดอร์ซ้ำได้?** — declarative apply เทียบ desired กับ actual แล้วแตะเฉพาะส่วนที่ต่าง

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] web และ api Deployment พร้อมอย่างละสอง Pod
- [ ] เปิด `http://localhost:8080` ได้
- [ ] เห็นชื่อ web/api Pod บนการ์ดสถานะ
- [ ] อธิบายได้ว่าทำไม db down เป็นผลที่ถูกต้องใน LAB 15
- [ ] ลบ Service/Ingress แล้วอ่านอาการได้
- [ ] ซ่อม ConfigMap ด้วย apply ทั้งโฟลเดอร์ได้
- [ ] Clean Re-run ผ่านหลังรอ Ingress sync
- [ ] ลบ namespace `lab015` แล้ว
*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
