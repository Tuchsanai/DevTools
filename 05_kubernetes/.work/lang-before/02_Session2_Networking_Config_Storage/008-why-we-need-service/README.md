# LAB 8 — Why We Need Service : ชื่อคงที่สำหรับ Pod ที่ IP เปลี่ยนได้

> โฟลเดอร์ `008-why-we-need-service` = LAB 8 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `01-web.yaml`, `02-api.yaml`, `03-web-ip.yaml`, `04-api-service.yaml`, `05-web-by-name.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** Pod เกิดใหม่แล้ว IP เปลี่ยน จึงต้องมี "ชื่อคงที่" ให้เรียกแทน

## วัตถุประสงค์ของแล็บ

1. อธิบายได้ว่าทำไม Pod IP ไม่ควรถูกบันทึกเป็นปลายทางถาวร
2. อธิบาย Service ในฐานะชื่อ DNS, virtual IP และตัวเลือก Pod ด้วย label
3. พิสูจน์ว่า Endpoints เปลี่ยนตาม Pod แต่ชื่อ `api` ไม่เปลี่ยน
4. อ่านอาการ Service ไม่มี endpoint และแก้ selector กลับได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ใน Docker Compose เราเรียก `http://api:8000` โดยไม่ต้องรู้ container IP เพราะ network มี DNS ให้
Kubernetes แยก Pod ซึ่งเกิดใหม่ได้ตลอด ออกจาก Service ซึ่งมีตัวตนและชื่อคงที่กว่า:

| สิ่งที่อ้าง | อายุ | เมื่อ Pod เกิดใหม่ |
|---|---|---|
| Pod IP | ชั่วคราว | IP เดิมใช้ต่อไม่ได้ |
| Service `api` | คงอยู่จนกว่าจะลบ Service | Endpoints ถูกอัปเดตให้ชี้ Pod ชุดใหม่ |
| `api.lab008.svc.cluster.local` | DNS ของ Service | resolve ไป ClusterIP เดิม |

Service ไม่ได้ “ย้าย IP ให้ Pod” แต่สร้างหน้าปลายทางใหม่ไว้ด้านหน้า แล้วเลือก Pod จาก `spec.selector`
ดังนั้น label ผิดเพียงตัวเดียวทำให้ Service มี `<none>` แม้ Pod ทุกตัวยัง Running

## สิ่งที่จะได้เรียนรู้

- จะได้ให้ web เรียก API ด้วย Pod IP โดยตรง
- จะได้เห็น IP เปลี่ยนหลังลบ Pod และหน้าเว็บเรียก IP เก่าไม่ได้
- จะได้สร้าง ClusterIP Service และอ่าน Endpoints
- จะได้ทำ selector ผิด อ่านอาการ และแก้กลับ

## ภาพรวมของแล็บนี้

1. เปิด web และ API สอง Pod โดยยังไม่มี Service หน้า API
2. ฝัง API Pod IP ใน web แล้วลบ Pod เป้าหมาย
3. สร้าง Service `api` และเปลี่ยน web ให้เรียกด้วยชื่อ
4. ลบ API Pod/ทำ selector ผิด แล้วสังเกต Endpoints ก่อนแก้กลับ

![Pod IP เปลี่ยน แต่ Service api เป็นชื่อคงที่หน้า Pod หลายตัว](../slides_assets/lab008-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า web จำ IP ของ API Pod แล้ว Pod นั้นถูกสร้างใหม่ request ถัดไปจะวิ่งไปที่ไหน?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิม · `|| docker run` สร้างเมื่อยังไม่มี · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · `kubectl get nodes` ตรวจ cluster · `crictl` ตรวจ image ใน kind node

✅ **Expected output** — 3 nodes เป็น Ready และมี image web/api/db ครบ (ตัดบางคอลัมน์; AGE และ image ID ต่างกันได้):

```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready    control-plane   15m   v1.36.4
devtools-worker          Ready    <none>          15m   v1.36.4
devtools-worker2         Ready    <none>          15m   v1.36.4
docker.io/library/k8s-lab-api  v1  682aa17deaef3  186MB
docker.io/library/k8s-lab-db   v1  901da7602fb40  300MB
docker.io/library/k8s-lab-web  v1  a389e8bc3c5ed  209MB
docker.io/library/k8s-lab-web  v2  65ea95c8496b6  209MB
…
```

ถ้า image ยังไม่อยู่ใน kind ให้ทำขั้น build/load ของแล็บ 001 หรือ README ระดับชุดก่อน

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/008-why-we-need-service
```

> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace · `git clone` ดึงชุดเรียน · `cd` เข้า LAB 008 เพื่อเรียกไฟล์ด้วย relative path

✅ **Expected output** — clone สำเร็จและ `cd` ไม่แสดง error:

```text
Cloning into 'DevTools'...
```

ถ้า clone ไว้แล้ว ให้รัน `git pull` ใน `~/labwork/DevTools` แทนการ clone ซ้ำ

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-web.yaml` | Deployment, Service, Ingress | เปิด web และประตูของแล็บ | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) · [Ingress](../YAML_Guide.md#ingress) |
| `02-api.yaml` | Deployment | สร้าง API 2 Pod เพื่อเห็น IP เปลี่ยน | [Deployment](../YAML_Guide.md#deployment) |
| `03-web-ip.yaml` | Deployment | จงใจผูก web กับ Pod IP | [Deployment](../YAML_Guide.md#deployment) |
| `04-api-service.yaml` | Service | ให้ชื่อและพอร์ตคงที่แก่ API | [Service](../YAML_Guide.md#service) |
| `05-web-by-name.yaml` | Deployment | เปลี่ยน web มาเรียก `http://api:8000` | [Deployment](../YAML_Guide.md#deployment) · [Service DNS](../YAML_Guide.md#service) |

ส่วนใหม่ที่ต้องอ่านจาก `04-api-service.yaml` จริงคือ:

```yaml
spec:
  selector:
    app: api
  ports:
    - name: http
      port: 8000
      targetPort: http
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `selector.app` | เลือก Pod label `app=api` เพื่อสร้าง endpoints | ไม่ตรงแล้ว Service ยังอยู่ แต่ไม่มีปลายทาง |
| `ports[].port` | พอร์ตคงที่ที่ client เรียกบน Service | client ต้องเรียกพอร์ตใหม่ |
| `targetPort: http` | ส่งต่อไป port ชื่อ `http` ของ API Pod | ชื่อไม่ตรงกับ container port แล้วส่งต่อไม่ได้ |
| ไม่ระบุ `protocol` | ใช้ default `TCP` | เปลี่ยนเป็น UDP/SCTP ต้องตรงกับ protocol ของแอป |
| ไม่ระบุ `type` | ใช้ default `ClusterIP` | ใส่ `NodePort` จะเพิ่มทางเข้าจากพอร์ตบนทุก Node |

ชื่อสั้น `api` ใช้ได้ใน namespace เดียวกัน; ชื่อเต็มคือ `api.lab008.svc.cluster.local` และรายการ EndpointSlice จะเปลี่ยนตาม Pod ที่ selector เลือก

**ผิดบ่อยในแล็บนี้:** selector ผิดยัง apply สำเร็จ จึงไม่มี validation error แต่ EndpointSlice ไม่มีปลายทาง; runlog ขั้น selector ผิดบันทึก `"error":"fetch failed"` ส่วน `"error":"The operation was aborted due to timeout"` เกิดในขั้นที่ web ยังชี้ Pod IP เก่า ให้เทียบ `spec.selector` กับ Pod labels และดู `kubectl get endpointslice -l kubernetes.io/service-name=api`

ดู field จาก schema ได้ด้วย `kubectl explain service.spec.ports` และ `kubectl explain service.spec.selector`

## 3. เปิด web และ API ที่ยังไม่มี Service

`01-web.yaml` มี Deployment web + ประตูสำเร็จรูป ส่วน `02-api.yaml` มี API 2 Pod แต่ยังไม่มี Service

```bash
kubectl create namespace lab008
kubectl apply -f 01-web.yaml -f 02-api.yaml
kubectl wait -n lab008 --for=condition=available deployment/web deployment/api --timeout=120s
kubectl get pods -n lab008 -o wide
```

> 📝 **คำอธิบาย:** namespace แยก resource ของแล็บ · `apply` สร้าง web/api · `wait` รอ Deployment · `-o wide` เพิ่มคอลัมน์ Pod IP และ Node

✅ **Expected output** — web 1 Pod และ api 2 Pod Running โดย API แต่ละตัวมี IP ของตัวเอง (ตัดบางคอลัมน์; ชื่อ/IP/Node/AGE ต่างกันได้):

```text
…
namespace/lab008 created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/api created
deployment.apps/web condition met
deployment.apps/api condition met
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE
api-5bdf56b96d-95fs9   1/1     Running   0          2s    10.244.1.8    devtools-worker2
api-5bdf56b96d-w8d8z   1/1     Running   0          2s    10.244.2.15   devtools-worker
web-89cc7866c-lthlv    1/1     Running   0          2s    10.244.2.14   devtools-worker
```

## 4. ผูก web กับ Pod IP โดยตรง

รอ process ของ API พร้อมก่อน เพราะ Deployment นี้ยังไม่มี readinessProbe:

```bash
API_POD=$(kubectl get pod -n lab008 -l app=api -o jsonpath='{.items[0].metadata.name}')
API_POD_IP=$(kubectl get pod -n lab008 "$API_POD" -o jsonpath='{.status.podIP}')
until kubectl exec -n lab008 deployment/web -- wget -qO- "http://$API_POD_IP:8000/health"; do sleep 1; done
sed "s/API_POD_IP/$API_POD_IP/" 03-web-ip.yaml | kubectl apply -f -
kubectl rollout status deployment/web -n lab008 --timeout=120s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,api,db}'
```

> 📝 **คำอธิบาย:** `jsonpath` อ่านชื่อ/IP จาก object จริง · `until` กัน race ที่ container Running แต่แอปยังไม่ฟังพอร์ต · `sed` แทน placeholder โดยไม่แก้ไฟล์ต้นฉบับ · `apply -f -` อ่าน YAML จาก stdin · `/info` ตรวจการ์ดสถานะในรูป JSON

✅ **Expected output** — health ตอบ ok, rollout ผ่าน และ web ติดต่อ API Pod ตาม IP ได้; db down เป็นผลถูกต้องเพราะแล็บนี้ยังไม่มีฐานข้อมูล (ค่าต่างกันได้):

```text
wget: can't connect to remote host (10.244.1.8): Connection refused
command terminated with exit code 1
{"status":"ok","pod":"api-5bdf56b96d-95fs9","version":"v1"}
deployment.apps/web configured
deployment "web" successfully rolled out
{"pod":"web-67449df4b8-49w6w","api":{"configured":true,"reachable":true,"pod":"api-5bdf56b96d-95fs9"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
```

![หน้าเว็บเรียก API ด้วย Pod IP ได้ก่อนลบ Pod](images/02-api-by-ip-connected.png)

## 5. ลบ Pod ที่ IP ถูกฝังไว้

```bash
kubectl delete pod -n lab008 "$API_POD"
kubectl wait -n lab008 --for=condition=Ready pod -l app=api --timeout=120s
kubectl get pods -n lab008 -o wide
sleep 3
curl -s http://localhost/info | jq -c '{pod,api,db}'
```

> 📝 **คำอธิบาย:** ลบ Pod เป้าหมายโดยชื่อที่บันทึกไว้ · Deployment สร้างตัวแทน · `-o wide` เปรียบเทียบ IP · web ยังเรียก IP เก่าจึง timeout

✅ **Expected output** — Pod เดิมหาย, ตัวใหม่ได้ `10.244.1.9` แทน `10.244.1.8` และ API กลายเป็น reachable false (ตัดบางคอลัมน์; ค่าเหล่านี้ต่างกันได้):

```text
…
pod "api-5bdf56b96d-95fs9" deleted from lab008 namespace
pod/api-5bdf56b96d-8twmk condition met
NAME                   READY   STATUS    RESTARTS   AGE   IP
api-5bdf56b96d-8twmk   1/1     Running   0          2s    10.244.1.9
api-5bdf56b96d-w8d8z   1/1     Running   0          64s   10.244.2.15
{"pod":"web-67449df4b8-49w6w","api":{"configured":true,"reachable":false,"error":"The operation was aborted due to timeout"},"db":{"status":"unknown"}}
```

![หลังลบ Pod การ์ด API แสดงว่า IP เดิมติดต่อไม่ได้](images/03-api-pod-deleted-unreachable.png)

## 6. ใส่ Service เป็นชื่อคงที่

`04-api-service.yaml` ใช้ selector `app: api`; `05-web-by-name.yaml` เปลี่ยนปลายทางเป็น `http://api:8000`

```bash
kubectl apply -f 04-api-service.yaml
kubectl get service,endpoints api -n lab008
kubectl apply -f 05-web-by-name.yaml
kubectl rollout status deployment/web -n lab008 --timeout=120s
for i in $(seq 1 10); do kubectl exec -n lab008 deployment/web -- wget -qO- http://api:8000/health | jq -r .pod; done
```

> 📝 **คำอธิบาย:** Service ให้ ClusterIP/DNS คงที่ · Endpoints คือ IP ปัจจุบันที่ selector พบ · rollout เปลี่ยน web ให้เรียกชื่อ · `seq` สร้าง connection ใหม่หลายครั้งเพื่อเห็นการกระจายโหลด

✅ **Expected output** — Endpoints มี API สอง IP และ connection ใหม่ไปถึงทั้งสอง Pod (ชื่อ/IP ต่างกันได้):

```text
service/api created
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
api    ClusterIP   10.96.150.141   <none>        8000/TCP   0s
NAME   ENDPOINTS                          AGE
api    10.244.1.9:8000,10.244.2.15:8000   0s
deployment.apps/web configured
deployment "web" successfully rolled out
api-5bdf56b96d-8twmk
api-5bdf56b96d-w8d8z
api-5bdf56b96d-w8d8z
api-5bdf56b96d-8twmk
api-5bdf56b96d-w8d8z
api-5bdf56b96d-w8d8z
api-5bdf56b96d-8twmk
api-5bdf56b96d-8twmk
api-5bdf56b96d-w8d8z
api-5bdf56b96d-8twmk
```

![web เรียก API ด้วยชื่อ Service และการ์ดแสดง API Pod ที่ตอบ](images/05-api-by-service-name.png)

> Kubernetes v1.36 ยังอ่าน `Endpoints` ได้ แต่เตือนว่า deprecated; งานใหม่ควรดู `EndpointSlice` ด้วย

## 7. ลบ API Pod ซ้ำและตรวจ DNS/log

```bash
API_POD=$(kubectl get pod -n lab008 -l app=api -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod -n lab008 "$API_POD"
kubectl wait -n lab008 --for=condition=Ready pod -l app=api --timeout=120s
kubectl get endpoints api -n lab008
kubectl exec -n lab008 deployment/web -- nslookup api || true
kubectl logs -n lab008 deployment/api --tail=8
```

> 📝 **คำอธิบาย:** ลบสมาชิกแต่ไม่ลบ Service · Endpoints ต้องเปลี่ยนเอง · `nslookup` พิสูจน์ FQDN/ClusterIP · `|| true` รองรับ BusyBox ที่คืน 1 หลังลอง suffix อื่น · logs เป็นหลักฐานว่า request ถึง API จริง

✅ **Expected output** — IP เก่า `10.244.1.9` เปลี่ยนเป็น `10.244.1.10`, DNS ชี้ ClusterIP และ log มี `GET /ready` (ค่าต่างกันได้):

```text
pod "api-5bdf56b96d-8twmk" deleted from lab008 namespace
pod/api-5bdf56b96d-s862d condition met
pod/api-5bdf56b96d-w8d8z condition met
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                           AGE
api    10.244.1.10:8000,10.244.2.15:8000   54s
Server:  10.96.0.10
Address: 10.96.0.10:53
** server can't find api.cluster.local: NXDOMAIN
Name:    api.lab008.svc.cluster.local
Address: 10.96.150.141
** server can't find api.cluster.local: NXDOMAIN
** server can't find api.svc.cluster.local: NXDOMAIN
** server can't find api.svc.cluster.local: NXDOMAIN
command terminated with exit code 1
Found 2 pods, using pod/api-5bdf56b96d-w8d8z
  File "/usr/local/lib/python3.12/site-packages/psycopg/_conninfo_attempts.py", line 53, in conninfo_attempts
    raise e.OperationalError(str(last_exc))
psycopg.OperationalError: [Errno -5] No address associated with hostname
[api] GET /ready 503 3ms
INFO:     10.244.2.17:37462 - "GET /ready HTTP/1.1" 503 Service Unavailable
```

BusyBox ลอง DNS search suffix หลายแบบจึงพิมพ์ NXDOMAIN และคืน exit code 1 แม้ชื่อเต็ม resolve สำเร็จ ส่วน `/ready` ตอบ 503 เพราะ LAB 008 ยังไม่มีฐานข้อมูล ไม่ใช่เพราะ Service เสีย

## 8. ทดลองให้พัง — selector ไม่ตรง label

```bash
kubectl patch service api -n lab008 -p '{"spec":{"selector":{"app":"apii"}}}'
sleep 2
kubectl get endpoints api -n lab008
curl -s http://localhost/info | jq -c '{api,db}'
kubectl describe service api -n lab008
kubectl patch service api -n lab008 -p '{"spec":{"selector":{"app":"api"}}}'
sleep 2
kubectl get endpoints api -n lab008
```

> 📝 **คำอธิบาย:** `patch` จงใจเปลี่ยน selector เป็น label ที่ไม่มี · Endpoints และหน้าเว็บแสดงอาการ · `describe` เปิดค่าที่ผิด · patch ครั้งหลังแก้กลับเป็น `app=api`

✅ **Expected output** — ตอนพัง Endpoints เป็น none ทั้งที่ Pod Running; หลังแก้ IP ทั้งสองกลับมา (ตัดบางแถวจาก `describe`; IP/AGE ต่างกันได้):

```text
…
service/api patched
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS   AGE
api    <none>      86s
{"api":{"configured":true,"reachable":false,"error":"fetch failed"},"db":{"status":"unknown"}}
Selector:                 app=apii
Endpoints:
service/api patched
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                           AGE
api    10.244.1.10:8000,10.244.2.15:8000   86s
```

## 9. แบบฝึกหัดสั้น (Exercise)

เพิ่ม label `track=stable` ให้ API Pod เพียงหนึ่งตัว แล้วปรับ selector ในสำเนา Service ให้เลือกทั้ง `app=api` และ `track=stable`
ถือว่าสำเร็จเมื่อ Endpoints เหลือหนึ่ง IP โดย Pod อีกตัวยัง Running และอธิบายได้ว่า selector ทุกเงื่อนไขทำงานแบบ AND

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get endpoints api -n lab008
curl -s http://localhost/info | jq -c '{pod,api,db}'
```

> 📝 **คำอธิบาย:** ดูปลายทางปัจจุบันของ Service แล้วตรวจจากมุมผู้ใช้ · db down ถือว่าถูกต้องใน LAB 008

✅ **Expected output** — Endpoints มี 2 IP และ `api.reachable=true`; ค่าชื่อ/IP/เวลาแตกต่างกันได้:

```text
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                           AGE
api   10.244.1.10:8000,10.244.2.15:8000   54s
{"pod":"web-74bf7d87c4-kjhhb","api":{"configured":true,"reachable":true,"pod":"api-5bdf56b96d-s862d"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| wget ครั้งแรก Connection refused | Pod Running ก่อน Uvicorn ฟังพอร์ต | รอ `/health` หรือเพิ่ม readinessProbe ในแล็บ 014 |
| `/info` ได้ HTML 404/503 ชั่วครู่ | Ingress หรือ endpoints ยัง converge | รอแล้วตรวจซ้ำก่อนส่งเข้า `jq` |
| Endpoints เป็น `<none>` | selector ไม่ตรง label | เทียบ `describe svc` กับ `get pods --show-labels` |
| `nslookup` คืน code 1 แต่มี Name/Address | BusyBox ลอง search suffix ที่ไม่มีด้วย | อ่าน FQDN ที่ resolve สำเร็จหรือใช้ wget ยืนยัน |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab008
kubectl wait --for=delete namespace/lab008 --timeout=120s
kubectl create namespace lab008
kubectl apply -f 01-web.yaml -f 02-api.yaml -f 04-api-service.yaml -f 05-web-by-name.yaml
kubectl wait -n lab008 --for=condition=available deployment/web deployment/api --timeout=120s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
kubectl get deploy,pods,svc,endpoints,ingress -n lab008
curl -s http://localhost/info | jq -c '{pod,api,db}'
kubectl delete namespace lab008
kubectl wait --for=delete namespace/lab008 --timeout=120s
kubectl get all -n lab008
```

> 📝 **คำอธิบาย:** ลบและสร้างจาก final state · รอ Deployment/Ingress · ตรวจผลเดิม · ลบ namespace รอบสุดท้ายและยืนยันว่าไม่เหลือ resource

✅ **Expected output** — Clean Re-run ได้ web 1, api 2, Endpoints 2 IP และ API reachable แล้วจบสะอาด (ค่าเหล่านี้ต่างกันได้; ตัดบางแถว/บางคอลัมน์):

```text
namespace "lab008" deleted
namespace/lab008 created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/api created
service/api created
deployment.apps/web configured
deployment.apps/web condition met
deployment.apps/api condition met
deployment.apps/api   2/2   2   2   5s
deployment.apps/web   1/1   1   1   5s
…
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
endpoints/api   10.244.1.11:8000,10.244.2.19:8000   5s
{"pod":"web-74bf7d87c4-xlp78","api":{"configured":true,"reachable":true,"pod":"api-5bdf56b96d-jsdb4"},"db":{"status":"down","error":"[Errno -5] No address associated with hostname"}}
namespace "lab008" deleted
No resources found in lab008 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get pods -o wide` | ดู Pod IP และ Node |
| `kubectl get service,endpoints` | ดูชื่อคงที่และปลายทางปัจจุบัน |
| `kubectl patch service` | เปลี่ยน selector เพื่อทดลอง/แก้กลับ |

## สรุปสิ่งที่ได้เรียนรู้

Pod IP เป็นรายละเอียดชั่วคราว ส่วน Service เป็นสัญญาการเชื่อมต่อที่คงที่กว่า: DNS/ClusterIP เดิมชี้ไปยัง Endpoints ชุดล่าสุดที่ตรง selector

- IP ตรงพังทันทีเมื่อ Pod ถูกแทนที่
- Service ติดตามสมาชิกด้วย label ไม่ใช่ชื่อ Pod
- connection ใหม่ถูกกระจายไปหลาย endpoint

**จำภาพเดียวให้ได้:** web โทรหา “api” ที่สมุดโทรศัพท์ Service แล้ว Service เลือก Pod ที่ยังอยู่ให้

🧭 ต่อยอด: แล็บ 009 จะเปรียบเทียบว่า Service แบบใดเปิดให้ใครเข้าถึงได้

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **ทำไมเรียก Pod IP ตรง ๆ ไม่ได้?** — Pod ใหม่มีตัวตนและ IP ใหม่ ไม่มีสัญญาว่าเลขเดิมจะอยู่ต่อ
2. **Service ช่วยอะไร?** — ให้ DNS/ClusterIP คงที่และส่ง connection ไป endpoint ปัจจุบัน
3. **Service รู้จัก Pod ได้อย่างไร?** — selector จับ label แล้ว controller อัปเดต EndpointSlice/Endpoints

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เห็น API Pod IP ก่อนและหลังลบต่างกันแล้ว
- [ ] สร้าง Service และเรียก `api:8000` ได้แล้ว
- [ ] เห็น Endpoints ปรับตาม Pod แล้ว
- [ ] ทำ selector ผิดและแก้กลับได้แล้ว
- [ ] Clean Re-run ผ่านและลบ namespace ปิดท้ายแล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
