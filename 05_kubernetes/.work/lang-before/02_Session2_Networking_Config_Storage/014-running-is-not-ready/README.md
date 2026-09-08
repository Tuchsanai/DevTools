# LAB 14 — Running is not Ready : ส่งงานให้เฉพาะ Pod ที่ทำงานได้จริง

> โฟลเดอร์ `014-running-is-not-ready` = LAB 14 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `manifests/` · `01-api-with-probes.yaml` · `02-api-bad-readiness.yaml`)

> 💡 **แนวคิดหลักของแล็บนี้:** "Pod Running" ไม่ได้แปลว่า "แอปพร้อมรับงาน"

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายได้ว่า phase `Running` บอกสถานะ process แต่ไม่ได้รับรอง dependency
2. อธิบายคำถามและผลลัพธ์ที่ต่างกันของ readiness กับ liveness ได้
3. อ่าน Events ของ probe ที่ตอบ 503 หรือ 404 ได้
4. เลือก endpoint สำหรับ probe โดยไม่ทำให้ dependency failure กลายเป็น restart loop

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

Compose มี `healthcheck` และ `depends_on: condition: service_healthy` ส่วน Kubernetes ถามสองคำถามแยกกันตลอดอายุของ Pod:

| Probe | คำถาม | เมื่อไม่ผ่าน | เทียบกับ Compose |
|---|---|---|---|
| readiness | “ตอนนี้รับ request ได้ไหม?” | ถอด Pod ออกจาก Service endpoints ชั่วคราว | `healthcheck` ใช้กับลำดับ start ได้ แต่ไม่ได้ถอดจาก Kubernetes Service |
| liveness | “process นี้ค้างหรือตายแล้วหรือยัง?” | restart container | Compose healthcheck อย่างเดียวไม่สั่ง restart เพราะ unhealthy |

API ของ SkillSpace มี `/health` ที่ตรวจเฉพาะตัว process และ `/ready` ที่ยิง `SELECT 1` ไปยัง PostgreSQL จริง การแยกสอง path ทำให้ db ล่มแล้ว API ไม่ถูกฆ่าวนโดยไม่จำเป็น

Service ไม่อ่าน phase `Running` โดยตรง แต่เลือกเฉพาะ Pod ที่ตรง selector และ Ready ดังนั้นผู้ใช้ไม่ต้องรับ error จาก Pod ที่รู้ตัวว่ายังทำงานไม่ได้

## สิ่งที่จะได้เรียนรู้

- จะได้เรียก `/health` และ `/ready` จากใน cluster
- จะได้เห็น API `Running` แต่ `READY 0/1`
- จะได้เห็น endpoints ว่างเมื่อ db ถูก scale เป็นศูนย์
- จะได้สั่ง process ป่วยและเห็น liveness restart
- จะได้ทดลอง probe path ที่ไม่มีจริงและอ่าน HTTP 404

## ภาพรวมของแล็บนี้

1. deploy ระบบครบสามชั้นและเพิ่ม probe ให้ API สอง replica
2. scale db ลงเป็นศูนย์แล้วคืนกลับเพื่อดู readiness/endpoints
3. ทำให้ `/health` ตอบ 503 แล้วดู liveness restart
4. ใส่ readiness path ผิด แก้กลับ และ Clean Re-run

![readiness ถอด Pod จาก Service ส่วน liveness restart container](../slides_assets/lab014-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า API process ยังเปิดพอร์ตได้แต่ query ฐานข้อมูลไม่ได้ Service ควรส่งงานให้ Pod นั้นหรือไม่?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน node

✅ **Expected output** — cluster พร้อมและ image ครบ (ตัดบางคอลัมน์); ชื่อ node, AGE, version และ hash ต่างกันได้ ถ้าไม่พบ image ให้ build/load ตาม LAB 001 หรือ README ระดับชุด:

```text
devtools-control-plane   Ready   control-plane   14m   v1.36.4
devtools-worker          Ready   <none>          13m   v1.36.4
devtools-worker2         Ready   <none>          13m   v1.36.4
k8s-lab-api  v1    c662b53377da4
k8s-lab-db   v1    9bb05e9c07722
k8s-lab-web  v1    c07ef6ef4b6a3
k8s-lab-web  v2    685541d4b6ff0
…
```

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/014-running-is-not-ready
```

> 📝 **คำอธิบาย:** เตรียม workspace · clone repository · เข้า LAB 14; ถ้ามี repository แล้วให้ใช้ `git pull` ใน repository เดิมแทนการ clone ซ้ำ

✅ **Expected output** — clone เริ่มทำงานและ `cd` ไม่แสดง error:

```text
Cloning into 'DevTools'...
```

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/01-pvc.yaml` | PersistentVolumeClaim | ขอพื้นที่ฐานข้อมูล | [Volume/PVC](../YAML_Guide.md#volume-pvc) |
| `manifests/02-secret.yaml` | Secret | รหัสผ่านสมมุติ | [Secret](../YAML_Guide.md#secret) |
| `manifests/03-db.yaml` | Deployment, Service | db พร้อม readiness แบบ `exec` | [Probes](../YAML_Guide.md#probes) |
| `manifests/04-api.yaml` | Deployment, Service | API baseline ที่ยังไม่มี probe | [Service](../YAML_Guide.md#service) |
| `manifests/05-web.yaml` | Deployment, Service | web เรียก API | [Service](../YAML_Guide.md#service) |
| `manifests/06-door.yaml` | Ingress | เปิดประตูไป web | [Ingress](../YAML_Guide.md#ingress) |
| `01-api-with-probes.yaml` | Deployment, Service | เพิ่ม readiness และ liveness ที่ถูกต้อง | [Probes](../YAML_Guide.md#probes) |
| `02-api-bad-readiness.yaml` | Deployment | จงใจใช้ readiness path `/readyz` | [Deployment](../YAML_Guide.md#deployment) · ตาราง error ด้านล่าง |

ใน `02-api-bad-readiness.yaml` ค่า `strategy.type: Recreate` หยุด Pod เก่าก่อนสร้างชุดใหม่ และ `rollingUpdate: null` ใช้ล้างค่า rollingUpdate เดิมที่อาจค้างจากการ apply ตอนสลับ strategy

ส่วนจริงจาก `01-api-with-probes.yaml`:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: http
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

| field | ความหมาย/ค่า default | เมื่อ fail หรือเปลี่ยน |
|---|---|---|
| `readinessProbe` | ไม่มี probe โดย default | fail → `READY 0/1` (Ready condition `False`) แต่ `STATUS` ยัง `Running`; ออกจาก endpoints และไม่ restart |
| `livenessProbe` | ไม่มี probe โดย default | fail ครบ threshold → restart Container |
| `startupProbe` | ไม่มีในไฟล์นี้และไม่มีโดย default | ถ้ามี จะกัน readiness/liveness ไว้จน startup ผ่าน |
| `httpGet` / `exec` | HTTP path+port หรือ command; db ใช้ `exec` จริง | path ผิดอาจได้ 404; exec exit non-zero คือ fail |
| เวลา 5 ค่า | `initialDelay=0`, `period=10`, `timeout=1`, `failure=3`, `success=1` วินาที/ครั้ง | liveness/startup กำหนด `successThreshold` ได้เพียง 1 |

**ผิดบ่อยในแล็บนี้:** runlog มีข้อความจริง `Readiness probe failed: HTTP probe failed with statuscode: 404` จาก `/readyz`; readiness ผิดทำให้ endpoints ว่าง ส่วน liveness fail มี Event `Container api failed liveness probe, will be restarted`

ดู schema ได้ด้วย `kubectl explain deployment.spec.template.spec.containers.readinessProbe` และ `kubectl explain deployment.spec.template.spec.containers.livenessProbe.httpGet`

## 3. Deploy ระบบและเพิ่ม probes

ส่วน probe จากไฟล์ `01-api-with-probes.yaml` จริง:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: http
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

> 📝 **คำอธิบาย YAML:** `httpGet.path/port` ระบุ endpoint และ named port · `periodSeconds` คือช่วงห่างการตรวจ · `timeoutSeconds` จำกัดเวลาต่อครั้ง · `failureThreshold` คือจำนวนครั้งติดกันก่อนถือว่าล้ม · `initialDelaySeconds` ของ liveness เว้นเวลาให้ process เริ่มก่อนตรวจ

```bash
kubectl create namespace lab014
kubectl apply -f manifests/
kubectl apply -f 01-api-with-probes.yaml
kubectl rollout status deployment/api -n lab014 --timeout=180s
kubectl wait --for=condition=available deployment/db deployment/web -n lab014 --timeout=180s
```
> 📝 **คำอธิบาย:** สร้าง namespace แยก · `apply -f manifests/` สร้าง PVC, Secret, db, api, web และประตู · apply ไฟล์ probe ปรับ API · `rollout status` รอ rollout ทั้งชุดแทนการจับ Pod เก่าด้วย label · `wait` รอ db และ web · `--timeout` จำกัดเวลารอ

✅ **Expected output** — API rollout สำเร็จและส่วนอื่น available:

```text
namespace/lab014 created
persistentvolumeclaim/db-data created
secret/db-secret created
deployment.apps/db created
service/db created
deployment.apps/api created
service/api created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/api configured
service/api unchanged
deployment "api" successfully rolled out
deployment.apps/db condition met
deployment.apps/web condition met
```

## 4. อ่าน endpoint ก่อนทำให้พัง

```bash
kubectl get pods -n lab014 -l app=api -o wide
kubectl get endpoints api -n lab014
kubectl exec deployment/web -n lab014 -- wget -T 5 -qO- http://api:8000/health
kubectl exec deployment/web -n lab014 -- wget -T 5 -qO- http://api:8000/ready
```
> 📝 **คำอธิบาย:** `-l app=api` เลือก API Pod · `get endpoints` ดูปลายทางที่ Service ส่งงานให้ · Warning deprecated หมายถึง object นี้ยังอ่านได้แต่ Kubernetes แนะนำ EndpointSlice สำหรับงานใหม่ · `wget -T 5` จำกัดเวลารอ · `/health` ไม่แตะ db · `/ready` query db จริง; Pod เก่าอาจยังแสดง `Terminating` ชั่วครู่หลัง rollout แต่ไม่อยู่ใน endpoints แล้ว

✅ **Expected output** — API สอง Pod Ready และ endpoints มีสอง IP:
```text
NAME                   READY   STATUS        RESTARTS   AGE   IP            NODE               NOMINATED NODE   READINESS GATES
api-68c74dcd8c-4krgz   1/1     Running       0          18s   10.244.1.7    devtools-worker    <none>           <none>
api-68c74dcd8c-rgwjs   1/1     Running       0          7s    10.244.2.16   devtools-worker2   <none>           <none>
api-7c94cf584b-ml8zm   1/1     Terminating   0          18s   10.244.2.13   devtools-worker2   <none>           <none>
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                          AGE
api    10.244.1.7:8000,10.244.2.16:8000   18s
{"status":"ok","pod":"api-68c74dcd8c-4krgz","version":"v1"}
{"status":"ready","db":"up","pod":"api-68c74dcd8c-rgwjs"}
```

## 5. ทำให้ db หายและสังเกต readiness

```bash
kubectl scale deployment/db -n lab014 --replicas=0
sleep 15
kubectl get pods -n lab014 -l app=api -o wide
kubectl get endpoints api -n lab014
kubectl get events -n lab014 --sort-by=.lastTimestamp | grep -E 'Unhealthy.*api' | tail -2
curl --retry 0 -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** `scale --replicas=0` ทำให้ db ไม่มี Pod · `sleep 15` รอ readiness สองครั้งตาม threshold · API ยัง Running แต่ endpoints ถอด Pod · Events ระบุ 503 · `--retry 0` ปิด retry policy ของเครื่องเรียนเพื่ออ่านผลทันที

✅ **Expected output** — API ยัง Running แต่ 0/1, endpoints ว่าง และ probe ตอบ 503 (ตัดบางคอลัมน์):
```text
…
api-68c74dcd8c-4krgz   0/1   Running   0   2m42s   10.244.1.7    devtools-worker
api-68c74dcd8c-rgwjs   0/1   Running   0   2m31s   10.244.2.16   devtools-worker2
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS
api
5s   Warning   Unhealthy   pod/api-68c74dcd8c-rgwjs   Readiness probe failed: HTTP probe failed with statuscode: 503
1s   Warning   Unhealthy   pod/api-68c74dcd8c-4krgz   Readiness probe failed: HTTP probe failed with statuscode: 503
{"api":{"configured":true,"reachable":false,"error":"fetch failed"},"db":{"status":"unknown"}}
```

![API Running แต่ไม่ Ready เมื่อฐานข้อมูลหาย](images/03-api-not-ready-when-db-down.png)

## 6. คืน db แล้วดูระบบฟื้นเอง

```bash
kubectl scale deployment/db -n lab014 --replicas=1
kubectl wait --for=condition=available deployment/db -n lab014 --timeout=180s
kubectl wait --for=condition=ready pod -n lab014 -l app=api --timeout=120s
kubectl get pods -n lab014 -l app=api
kubectl get endpoints api -n lab014
curl --retry 0 -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** scale db กลับเป็นหนึ่ง · รอ readiness ของ PostgreSQL · ดู API เปลี่ยนจาก 0/1 เป็น 1/1 โดยไม่ restart · endpoints รับ IP กลับอัตโนมัติ · `/info` ตรวจเส้นทางจริง

✅ **Expected output** — API กลับ Ready ทั้งสองและ db up (ตัดบางคอลัมน์):
```text
…
deployment.apps/db condition met
pod/api-68c74dcd8c-4krgz condition met
pod/api-68c74dcd8c-rgwjs condition met
api-68c74dcd8c-4krgz   1/1   Running   0   2m47s
api-68c74dcd8c-rgwjs   1/1   Running   0   2m36s
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
api   10.244.1.7:8000,10.244.2.16:8000   2m48s
{"api":{"configured":true,"reachable":true,"pod":"api-68c74dcd8c-4krgz"},"db":{"status":"up"}}
```

![readiness ผ่านอีกครั้งและ Service ส่งงานได้](images/04-api-ready-again.png)

## 7. พิสูจน์ liveness ด้วย process ที่จงใจป่วย

```bash
RESPONSE=$(kubectl exec deployment/web -n lab014 -- wget -T 5 -qO- --post-data='{"ok":false}' --header='Content-Type: application/json' http://api:8000/debug/health)
echo "$RESPONSE"
TARGET=$(printf '%s' "$RESPONSE" | jq -r .pod)
sleep 35
kubectl get pods -n lab014 -l app=api -o custom-columns='NAME:.metadata.name,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
kubectl logs pod/$TARGET -n lab014 --previous --tail=12
kubectl get events -n lab014 --sort-by=.lastTimestamp | grep -E '(Liveness probe failed|failed liveness probe)' | tail -2
```
> 📝 **คำอธิบาย:** เก็บชื่อ Pod ที่ตอบไว้ใน `TARGET` · `sleep 35` รอ liveness 10 วินาที × 3 ครั้งและเวลาเริ่มตรวจ · custom columns อ่าน restart · `logs --previous` อ่าน process ก่อนถูก restart · Events ยืนยันสาเหตุ

✅ **Expected output** — Pod ที่ตอบคำสั่งมี RESTARTS เพิ่มเป็น 1 แล้วกลับ Ready:
```text
{"ok":false,"pod":"api-68c74dcd8c-4krgz"}
NAME                   READY   RESTARTS
api-68c74dcd8c-4krgz   true    1
api-68c74dcd8c-rgwjs   true    0
[api] GET /health 503 0ms
INFO:     10.244.1.1:36256 - "GET /health HTTP/1.1" 503 Service Unavailable
…
INFO:     Finished server process [1]
13s   Warning   Unhealthy   pod/api-68c74dcd8c-4krgz   Liveness probe failed: HTTP probe failed with statuscode: 503
13s   Normal    Killing     pod/api-68c74dcd8c-4krgz   Container api failed liveness probe, will be restarted
```

บล็อกนี้ตัดข้อความกลางของ `logs --previous` บางบรรทัดด้วย `…`; 503 เป็นผลที่ตั้งใจให้ liveness ตรวจพบก่อน restart

## 8. ทดลองให้พัง — readiness path ไม่มีจริง

```bash
kubectl apply -f 02-api-bad-readiness.yaml
sleep 15
kubectl get pods -n lab014 -l app=api
kubectl get endpoints api -n lab014
kubectl get events -n lab014 --sort-by=.lastTimestamp | grep -E 'Readiness probe failed.*404' | tail -2
```
> 📝 **คำอธิบาย:** manifest จงใจใช้ `/readyz` ซึ่ง API ไม่มี · strategy `Recreate` ทำให้เห็น Pod ชุดผิดโดยไม่มีของเก่าค้ำ · Pod process ยัง Running แต่ readiness ตอบ 404 · Service ไม่มี endpoint

✅ **Expected output** — Pod 0/1, endpoints ว่าง และ Event ระบุ 404 (ตัดบางคอลัมน์):
```text
…
api-cc95575c6-qmgrl   0/1   Running   0   15s
api-cc95575c6-rt8f4   0/1   Running   0   15s
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS
api
2s   Warning   Unhealthy   pod/api-cc95575c6-rt8f4   Readiness probe failed: HTTP probe failed with statuscode: 404
2s   Warning   Unhealthy   pod/api-cc95575c6-qmgrl   Readiness probe failed: HTTP probe failed with statuscode: 404
```

แก้ path กลับจาก source of truth:

```bash
kubectl apply -f 01-api-with-probes.yaml
kubectl rollout status deployment/api -n lab014 --timeout=180s
kubectl get pods -n lab014 -l app=api
kubectl get endpoints api -n lab014
```
> 📝 **คำอธิบาย:** apply manifest ที่ใช้ `/ready` · `rollout status` รอ Pod ชุดถูกต้องและการ terminate ชุดเก่า · สองคำสั่งท้ายยืนยันทั้ง Pod และ Service

✅ **Expected output** — rollout ผ่าน, API 2/2 และ endpoints กลับมา (ตัดบางคอลัมน์):
```text
…
deployment.apps/api configured
service/api unchanged
deployment "api" successfully rolled out
api-7cf4f8dcc-9nhw2   1/1   Running   0
api-7cf4f8dcc-ps7dp   1/1   Running   0
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
api   10.244.1.21:8000,10.244.2.12:8000
```

## 9. แบบฝึกหัดสั้น (Exercise)

เพิ่ม `initialDelaySeconds` ให้ readiness แล้วอธิบายว่า delay เพียงเลื่อนเวลาที่ kubelet เริ่มถาม จากนั้นเสนอค่า period/failure threshold ที่รวมกันไม่เกิน 30 วินาทีพร้อมเหตุผล

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get pods -n lab014
kubectl get endpoints api -n lab014
```
> 📝 **คำอธิบาย:** ตรวจว่า API ทั้งสอง Pod เป็น Ready และ Service มีสองปลายทาง; หลักฐาน response/log/Event ถูกตรวจครบในหัวข้อก่อนหน้าแล้ว

✅ **Expected output** — API 2 Pod เป็น 1/1 และ endpoints มีสอง IP (ตัดบางคอลัมน์):

```text
…
api-7cf4f8dcc-9nhw2   1/1   Running   0   85s
api-7cf4f8dcc-ps7dp   1/1   Running   0   87s
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
api   10.244.1.21:8000,10.244.2.12:8000   4m45s
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| API Running แต่ 0/1 | `/ready` ต่อ db ไม่ได้ | ตรวจ db Pod, Service และ API logs |
| API restart ทั้งหมดเมื่อ db ล่ม | ใช้ db check เป็น liveness | ย้าย dependency check ไป readiness |
| `kubectl wait -l` รอนานหลัง rollout | จับ Pod เก่าที่กำลัง terminate | ใช้ `kubectl rollout status deployment/api` |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab014
kubectl wait --for=delete namespace/lab014 --timeout=180s
kubectl create namespace lab014
kubectl apply -f manifests/
kubectl apply -f 01-api-with-probes.yaml
kubectl rollout status deployment/api -n lab014 --timeout=180s
kubectl wait --for=condition=available deployment/db deployment/web -n lab014 --timeout=180s
until curl --retry 0 -s http://localhost/info | jq -e '.api.reachable == true and .db.status == "up"' >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** ลบและรอ namespace เก่า · สร้างทุก object จาก manifest · apply probe ที่ถูก · รอ rollout/availability · `/info` ยืนยันผลเดิมจากสภาพสะอาด

✅ **Expected output** — API พร้อมสอง replica และสถานะ db up (ตัดบางแถว/ข้อความท้าย):
```text
…
namespace/lab014 created
deployment "api" successfully rolled out
deployment.apps/db condition met
deployment.apps/web condition met
{"api":{"configured":true,"reachable":true,"pod":"api-7cf4f8dcc-pvc5t"},"db":{"status":"up"}}
```

```bash
kubectl delete namespace lab014
kubectl wait --for=delete namespace/lab014 --timeout=180s
kubectl get all -n lab014
```
> 📝 **คำอธิบาย:** ลบ namespace รอบสุดท้าย · รอจนหายจริง · ตรวจว่าไม่มี workload/Service ค้าง

✅ **Expected output** — จบสะอาด:
```text
namespace "lab014" deleted
No resources found in lab014 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get endpoints api` | ดู Pod ที่ Service ส่งงานให้จริง |
| `kubectl scale deployment/db --replicas=0` | จำลอง dependency หาย |
| `kubectl get events` | อ่านผล probe จาก kubelet |
| `kubectl rollout status deployment/api` | รอการเปลี่ยน Pod template จบ |
| `kubectl logs --previous` | อ่าน log ของ container ก่อน restart |

## สรุปสิ่งที่ได้เรียนรู้

`Running` บอกเพียงว่า container process ทำงานอยู่ ส่วน `Ready` บอกว่าส่งงานให้ได้ตอนนี้

- readiness fail ไม่ฆ่า container แต่ถอด IP จาก Service
- liveness fail restart container เพื่อคืนจากอาการค้าง
- probe path ผิดทำให้ระบบตัด Pod ดีออกได้ จึงต้องอ่าน Events

**จำภาพเดียวให้ได้:** Running คือไฟเครื่องติด ส่วน Ready คือป้ายหน้าร้านว่า “รับลูกค้าได้”

🧭 ต่อยอด: แล็บ 015 ของครั้งที่ 3 จะประกอบ object หลายชนิดให้เป็นระบบเดียว

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **readiness กับ liveness ตอบคนละคำถามอย่างไร?** — รับงานได้ไหม กับ process ยังมีชีวิตไหม
2. **ทำไม `/ready` ต้อง query db จริง?** — เพื่อไม่ส่งงานให้ API ที่เปิดพอร์ตแต่ทำงานธุรกิจไม่ได้
3. **ทำไมไม่ใส่ db check ใน liveness?** — db ล่มไม่ใช่ความผิดของ API; restart วนไม่ได้ซ่อม dependency

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เห็น API Running แต่ READY 0/1 เมื่อ db หาย
- [ ] เห็น endpoints ว่างและกลับมาเอง
- [ ] เห็น liveness ทำให้ RESTARTS เพิ่ม
- [ ] อ่าน Event 503 และ 404 ได้
- [ ] อธิบาย readiness/liveness ได้

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
