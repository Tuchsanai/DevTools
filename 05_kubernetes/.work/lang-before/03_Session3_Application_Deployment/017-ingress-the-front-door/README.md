# LAB 17 — Ingress, the Front Door : URL เดียวแยกทางด้วย path

> โฟลเดอร์ `017-ingress-the-front-door` = LAB 17 ของชุด Kubernetes ครั้งที่ 3
> (ไฟล์ของแล็บนี้: `manifests/01-configmap.yaml` ถึง `manifests/10-db-service.yaml`, `06-ingress-bad.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** Ingress คือประตูหน้าบ้านที่ทำหน้าที่เดียวกับ reverse proxy ที่เคยเรียน แต่รับคำสั่งจาก Kubernetes

## วัตถุประสงค์ของแล็บ

1. อธิบายได้ว่า Ingress และ ingress controller เป็นคนละสิ่งกัน
2. อธิบายได้ว่า Ingress ต่างจาก NodePort ตรงขอบเขตและวิธี route อย่างไร
3. เชื่อมแนวคิด Ingress กับ reverse proxy/Traefik ที่เคยเรียนได้
4. อ่าน 503 จาก backend name/port ที่ผิด แล้วแก้กฎกลับได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ถ้าเปิดทุก Service ด้วย NodePort ระบบ 20 service จะมี 20 port ให้ผู้ใช้จำ ปัญหานี้เหมือนตอนใช้ Docker หลาย container ก่อนมี reverse proxy

Ingress เป็น object ที่เก็บ “กฎ” ส่วน ingress-nginx controller คือ proxy ตัวจริงที่ watch Kubernetes API แล้วสร้าง config ตามกฎนั้น การสร้าง Ingress โดยไม่มี controller จึงเหมือนเขียนแผนที่แต่ไม่มีคนเฝ้าประตู
สำหรับ HTTPS, Ingress อ้าง Secret ใน `spec.tls[].secretName` เพื่อให้ controller ใช้ certificate/key นั้น เครื่องเรียน map HTTPS ออกที่ `localhost:8443`; แล็บนี้ยังใช้ HTTP เพื่อโฟกัส path routing

| สิ่งที่เทียบ | NodePort | Ingress | Traefik ที่เคยเรียน |
|---|---|---|---|
| ชั้นเครือข่าย | L4 port | L7 HTTP path/host | L7 HTTP router |
| จุดเข้าหลัก | หนึ่ง port ต่อ Service | 80/443 จุดเดียว | entrypoint |
| กฎเลือกทาง | port number | Ingress rule/path | router rule |
| ปลายทาง | Service | backend Service | Traefik service |

แล็บนี้ไม่ใส่ `host:` จึงเปิด `http://localhost:8080` ได้ตรง ๆ และใช้ `pathType: Prefix`: `/api` ไป FastAPI ส่วน `/` ไป Next.js โดยไม่ rewrite เพราะ API รู้จัก prefix `/api` อยู่แล้ว

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น ingress-nginx controller ที่ bootstrap เตรียมไว้
- จะได้ตามเส้นทาง host `8080` → container `80` → node hostPort `80` → controller
- จะได้ route `/info` ไป web และ `/api/whoami` ไป api
- จะได้ดูหน้าเว็บและ JSON ผ่าน port เดียวกัน
- จะได้อ่าน access log ที่ระบุ backend จริง
- จะได้ทำ Service name และ Service port ให้ผิดจนได้ 503
- จะได้ซ่อมด้วยการ apply manifest ซึ่งเป็น source of truth

## ภาพรวมของแล็บนี้

1. ตรวจ controller และ hostPort 80/443
2. deploy ระบบสามชั้นพร้อม Ingress แบบสอง path
3. ทดสอบ `/`, `/api/whoami` และ `/api/dashboard`
4. อ่าน controller access log
5. เปลี่ยน backend ให้ผิด อ่าน 503 แล้วแก้กลับ
6. Cleanup และ Clean Re-run

![เส้นทาง request ผ่าน ingress-nginx ไป web และ api](../slides_assets/lab017-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า web และ api มี Service ของตัวเองอยู่แล้ว เหตุใดผู้ใช้จึงยังควรเข้าผ่าน “ประตู” เดียว?

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** เข้าเครื่องเรียนด้วย `docker exec -it` (ทุกคำสั่งหลังจากนี้พิมพ์ในเครื่องเรียน) · `k8s-bootstrap` ข้ามเองถ้า cluster มีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน kind node

ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `localhost:8080`

✅ **Expected output** — node ทั้งสาม Ready และ image แอปอยู่ใน node แล้ว (AGE และ image ID ต่างกันได้):
```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready    control-plane   22m   v1.36.4
devtools-worker          Ready    <none>          22m   v1.36.4
devtools-worker2         Ready    <none>          22m   v1.36.4
docker.io/library/k8s-lab-api   v1   1b0af425a075d   186MB
docker.io/library/k8s-lab-db    v1   35984a84885cb   300MB
docker.io/library/k8s-lab-web   v1   2a74c90a62059   209MB
docker.io/library/k8s-lab-web   v2   7bedccdeefc86   209MB
```

ถ้าผล `grep` ว่าง → ทำขั้น build/load ใน README ระดับชุดหรือ LAB 001

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/017-ingress-the-front-door
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้างโฟลเดอร์ซ้ำได้ · `&&` หยุดเมื่อขั้นก่อนพลาด · `git clone` ดาวน์โหลด repo · `cd` เข้า LAB 17

✅ **Expected output** — clone สำเร็จและเข้าโฟลเดอร์แล็บได้:
```text
Cloning into 'DevTools'...
```

ถ้ามี repo แล้วให้อัปเดตแทน:
```bash
cd ~/labwork/DevTools && git pull
```
> 📝 **คำอธิบาย:** `git pull` ดึงและรวม commit ล่าสุดของ branch ปัจจุบัน

✅ **Expected output** — repository เป็นเวอร์ชันล่าสุด:
```text
Already up to date.
```

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/01-configmap.yaml` | ConfigMap | ส่ง config ให้ web | [ทบทวน ConfigMap](../YAML_Guide.md#configmap) |
| `manifests/02-web-deployment.yaml` | Deployment | รัน web พร้อม readiness | [ทบทวน Deployment](../YAML_Guide.md#deployment) · [ทบทวน Probes](../YAML_Guide.md#probes) |
| `manifests/03-web-service.yaml` | Service | backend ของ path `/` | [ทบทวน Service](../YAML_Guide.md#service) · [Ingress backend](../YAML_Guide.md#1-ingress) |
| `manifests/04-api-deployment.yaml` | Deployment | รัน api ที่รู้จัก db | [ทบทวน Deployment](../YAML_Guide.md#deployment) |
| `manifests/05-api-service.yaml` | Service | backend ของ path `/api` | [ทบทวน Service](../YAML_Guide.md#service) · [Ingress backend](../YAML_Guide.md#1-ingress) |
| `manifests/06-ingress.yaml` | Ingress | route สอง path ไปคนละ Service | [Ingress](../YAML_Guide.md#1-ingress) |
| `manifests/07-secret.yaml` | Secret | ให้ข้อมูลเชื่อมต่อ db | [ทบทวน Secret](../YAML_Guide.md#secret) |
| `manifests/08-pvc.yaml` | PersistentVolumeClaim | ขอพื้นที่ของ db | [ทบทวน PVC](../YAML_Guide.md#pvc) |
| `manifests/09-db-deployment.yaml` | Deployment | รัน db บน PVC แบบ Recreate | [strategy](../YAML_Guide.md#3-strategy) |
| `manifests/10-db-service.yaml` | Service | ให้ api หา db | [ทบทวน Service](../YAML_Guide.md#service) |
| `06-ingress-bad.yaml` | Ingress | จงใจชี้ Service `web-svc` ที่ไม่มี | [Ingress ผิดบ่อย](../YAML_Guide.md#1-ingress) |

ส่วนใหม่ที่ต้องอ่านจาก `manifests/06-ingress.yaml` คือ:

```yaml
spec:
  ingressClassName: nginx       # controller class ที่จะรับกฎ
  rules:
    - http:                     # ไม่ใส่ host = รับทุก host ที่มาถึง controller
        paths:
          - path: /api          # Prefix จับ /api และ path ย่อย
            pathType: Prefix    # field บังคับ; ไม่มี default
            backend:
              service:
                name: api       # Service ใน namespace lab017
                port:
                  number: 8000  # Service port
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `ingressClassName` | เลือก IngressClass `nginx` | class อื่นต้องมี controller ที่รับ class นั้น |
| `path` + `pathType` | กำหนด URL ที่จับและวิธีเทียบ | `Exact` จะไม่จับ path ย่อยแบบ `Prefix` |
| `backend.service` | Service name และ port ปลายทาง | ชื่อ/port ผิดทำให้ route ไม่มี backend ใช้งานได้ |
| `host` / `tls` | ไฟล์นี้ไม่ใส่ จึงรับทุก host ผ่าน HTTP | ระบบจริงเพิ่มโดเมนและ Secret ใบรับรองได้ |

**ผิดบ่อยในแล็บนี้:** `06-ingress-bad.yaml` ใช้ `name: web-svc`; runlog จาก `describe ingress`
แสดง `<error: services "web-svc" not found>` และ curl ได้ `503 Service Temporarily Unavailable`

ดู field ได้ด้วย `kubectl explain ingress.spec.ingressClassName`, `kubectl explain ingress.spec.rules.http.paths.pathType` และ `kubectl explain ingress.spec.tls`

## 3. ตรวจ proxy ตัวจริง

```bash
kubectl -n ingress-nginx get pods,svc -o wide
kubectl -n ingress-nginx get deploy ingress-nginx-controller \
  -o jsonpath='{range .spec.template.spec.containers[0].ports[*]}{.name}{" containerPort="}{.containerPort}{" hostPort="}{.hostPort}{"\n"}{end}'
```
> 📝 **คำอธิบาย:** `-n ingress-nginx` เลือก namespace ของ controller · `pods,svc` ดู proxy และ Service · `-o wide` เพิ่ม node/IP · `jsonpath` อ่าน port จาก Pod template · `hostPort` คือ port ที่ kind control-plane เปิดรับ

✅ **Expected output** — controller `1/1 Running` บน control-plane และฟัง hostPort 80/443 (ชื่อ Pod, IP และ AGE ต่างกันได้):
```text
pod/ingress-nginx-controller-5d9bb85749-mbclt   1/1   Running   0   21m   10.244.0.5   devtools-control-plane
service/ingress-nginx-controller   NodePort   10.96.227.22   <none>   80:30934/TCP,443:30998/TCP
http containerPort=80 hostPort=80
https containerPort=443 hostPort=443
webhook containerPort=8443 hostPort=
```

เส้นทางที่ต้องจำคือ browser `localhost:8080` → container port `80` → control-plane hostPort `80` → ingress-nginx → Service → Pod

## 4. สร้างกฎสอง path

หัวใจของ `manifests/06-ingress.yaml` มีเพียง backend สองทาง:
```yaml
rules:
  - http:
      paths:
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: api
              port:
                number: 8000
        - path: /
          pathType: Prefix
          backend:
            service:
              name: web
              port:
                number: 3000
```

`ingressClassName: nginx` เลือก controller · ไม่มี `host` จึงรับทุก Host header · backend อ้าง Service ไม่อ้าง Pod IP
```bash
kubectl create namespace lab017
kubectl apply -f manifests/
kubectl wait -n lab017 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
kubectl describe ingress -n lab017 skillspace
```
> 📝 **คำอธิบาย:** `create namespace` แยกห้อง · `apply -f manifests/` สร้างระบบครบ · `wait` รอสาม Deployment · `describe ingress` แปลกฎเป็น backend พร้อม endpoint · `--timeout` จำกัดเวลารอ

✅ **Expected output** — object ถูกสร้างครบและ describe แสดง `/api → api:8000`, `/ → web:3000` (IP ต่างกันได้):
```text
namespace/lab017 created
ingress.networking.k8s.io/skillspace created
deployment.apps/db condition met
deployment.apps/api condition met
deployment.apps/web condition met
Rules:
  Host  Path  Backends
  *
        /api  api:8000 (10.244.2.12:8000)
        /     web:3000 (10.244.1.13:3000)
```

## 5. พิสูจน์ URL เดียวไปสอง backend

```bash
until curl -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
curl -s http://localhost/api/whoami | jq -c '{pod,version,time}'
curl -s http://localhost/api/dashboard | jq -c '{tickets,loans_active}'
```
> 📝 **คำอธิบาย:** URL ทั้งสามใช้ host/port เดียว · `/info` ต้องเข้า web · prefix `/api` ต้องเข้า FastAPI · `whoami` แสดง API Pod · `dashboard` พิสูจน์ว่า API อ่าน DB ได้ · `jq` จัด JSON

✅ **Expected output** — web และ api ตอบจาก Pod คนละชื่อ และ dashboard มี seed data (ชื่อ Pod/เวลาแตกต่างกันได้):
```text
{"pod":"web-7484cf7478-8ljdm","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-q6fmx"},"db":{"status":"up"}}
{"pod":"api-6b56dd98f-q6fmx","version":"v1","time":"2026-09-02T16:53:47+00:00"}
{"tickets":{"NEW":3,"ASSIGNED":2,"IN_PROGRESS":1,"DONE":2},"loans_active":2}
```

เปิด `http://localhost:8080` และ `http://localhost:8080/api/dashboard` ใน browser

![หน้า SkillSpace ผ่าน path / ของ Ingress](images/03-root-via-ingress.png)

![JSON dashboard ผ่าน path /api ของ Ingress เดียวกัน](images/03-api-dashboard-json-via-ingress.png)

## 6. อ่าน access log ของ ingress controller

```bash
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=8
```
> 📝 **คำอธิบาย:** `logs deploy/...` อ่าน Pod ของ controller โดยไม่ต้องจำชื่อ · `--tail=8` เลือก request ล่าสุด · ช่อง `[lab017-web-3000]` หรือ `[lab017-api-8000]` คือ upstream ที่กฎเลือก

✅ **Expected output** — `/info` ไป web ส่วน `/api/*` ไป api และทุก request ได้ 200 (เวลา/IP/request ID ต่างกันได้):
```text
172.18.0.1 - - [02/Sep/2026:16:53:47 +0000] "GET /info HTTP/1.1" 200 206 "-" "curl/8.18.0" 77 0.020 [lab017-web-3000] [] 10.244.1.13:3000 206 0.019 200 510516c839c378298461476c1236e0a4
172.18.0.1 - - [02/Sep/2026:16:53:47 +0000] "GET /api/whoami HTTP/1.1" 200 79 "-" "curl/8.18.0" 83 0.002 [lab017-api-8000] [] 10.244.2.12:8000 79 0.003 200 a84fbc7b9ce781af8692c2dab25cd6c4
172.18.0.1 - - [02/Sep/2026:16:53:47 +0000] "GET /api/dashboard HTTP/1.1" 200 672 "-" "curl/8.18.0" 86 0.013 [lab017-api-8000] [] 10.244.2.12:8000 672 0.013 200 0f2780542471d36e014be4b356d3af49
```

## 7. ทดลองให้พัง — backend Service ไม่มีจริง

ไฟล์ `06-ingress-bad.yaml` เปลี่ยน backend ของ `/` จาก `web` เป็น `web-svc` ซึ่งไม่มีใน namespace
```bash
kubectl apply -f 06-ingress-bad.yaml
until [ "$(curl --retry 0 -s -o /dev/null -w '%{http_code}' http://localhost/)" = 503 ]; do sleep 1; done
curl --retry 0 -i http://localhost/
kubectl describe ingress -n lab017 skillspace
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=5
kubectl apply -f manifests/06-ingress.yaml
until curl --retry 0 -sf http://localhost/ >/dev/null; do sleep 1; done
```
> 📝 **คำอธิบาย:** loop รอ controller sync จนเห็น 503 · `--retry 0` ปิดค่า retry=5 จาก `~/.curlrc` · `-i` แสดง status/header · `describe` ชี้ Service ที่หาไม่เจอ · apply ไฟล์ดีและรอ 200

✅ **Expected output** — ได้ 503, describe บอก Service ไม่มี และเมื่อ apply ไฟล์ดี Ingress ถูก configured กลับ:
```text
ingress.networking.k8s.io/skillspace configured
HTTP/1.1 503 Service Temporarily Unavailable
<center><h1>503 Service Temporarily Unavailable</h1></center>
/   web-svc:3000 (<error: services "web-svc" not found>)
172.18.0.1 - - [02/Sep/2026:16:55:09 +0000] "GET / HTTP/1.1" 503 190 "-" "curl/8.18.0" 73 0.000 [lab017-web-svc-3000] [] - - - - 1aa02b095220632f739e57939c8cbd25
ingress.networking.k8s.io/skillspace configured
```

สาเหตุอยู่ชั้น route: web Pod และ Service `web` ยังปกติ แต่กฎชี้ชื่อที่ไม่มี จึงไม่มี upstream ให้ proxy ส่งต่อ

## 8. ทดลองให้พัง — Service ถูกแต่ port ผิด

```bash
kubectl patch ingress -n lab017 skillspace --type=json \
  -p='[{"op":"replace","path":"/spec/rules/0/http/paths/1/backend/service/port/number","value":3001}]'
until [ "$(curl --retry 0 -s -o /dev/null -w '%{http_code}' http://localhost/)" = 503 ]; do sleep 1; done
curl --retry 0 -i http://localhost/
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=5
kubectl apply -f manifests/06-ingress.yaml
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** `patch --type=json` แก้ field เดียวชั่วคราว · `replace` เปลี่ยน backend port เป็น 3001 · curl อ่าน 503 · log ต้องเห็น `[lab017-web-3001]` · apply YAML คืนค่าประกาศ · `/info` ยืนยันระบบกลับปกติครบสามชั้น

✅ **Expected output** — port ผิดให้ 503 และหลัง apply กลับ `/info` เป็น db up:
```text
ingress.networking.k8s.io/skillspace patched
HTTP/1.1 503 Service Temporarily Unavailable
172.18.0.1 - - [02/Sep/2026:16:55:45 +0000] "GET / HTTP/1.1" 503 190 "-" "curl/8.18.0" 73 0.000 [lab017-web-3001] [] - - - - f11e6b81f49fde915b2e530a57e04306
ingress.networking.k8s.io/skillspace configured
{"pod":"web-7484cf7478-8ljdm","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-q6fmx"},"db":{"status":"up"}}
```

## 9. แบบฝึกหัดสั้น (Exercise)

ออกแบบ path `/status` ให้ไป web โดยไม่เพิ่ม NodePort แล้วตอบก่อนว่า path `/status/api` จะถูก rule ใดเลือกเมื่อมีทั้ง `/status` และ `/` แบบ Prefix

เกณฑ์สำเร็จ: อธิบาย longest matching path ได้ และตรวจด้วย controller access logว่าปลายทางตรงกับที่ทาย โดยไม่แก้ host file

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get ingress,svc,endpoints -n lab017
kubectl describe ingress -n lab017 skillspace
curl -s -o /dev/null -w '%{http_code}\n' http://localhost/
curl -s -o /dev/null -w '%{http_code}\n' http://localhost/api/whoami
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=5
```
> 📝 **คำอธิบาย:** `ingress,svc,endpoints` ดู rule กับปลายทาง · `describe` ต้องไม่มี backend error · `-o /dev/null` ทิ้ง body · `-w` แสดงเฉพาะ HTTP code · log เป็นหลักฐานจาก proxy

✅ **Expected output** — ทั้งสอง path ได้ 200, Service มี endpoint และ log ระบุ backend ถูก:
```text
skillspace   nginx   *   10.96.227.22   80
api   10.244.2.12:8000
web   10.244.1.13:3000
200
200
172.18.0.1 - - [02/Sep/2026:16:53:47 +0000] "GET /api/whoami HTTP/1.1" 200 79 "-" "curl/8.18.0" 83 0.002 [lab017-api-8000] [] 10.244.2.12:8000 79 0.003 200 a84fbc7b9ce781af8692c2dab25cd6c4
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| เปิดแล้วได้ 404 จาก nginx | ยังไม่มี Ingress หรือ path ไม่ match | ดู `kubectl get/describe ingress -A` |
| ได้ 503 และ backend ว่าง | Service name ผิดหรือไม่มี Ready endpoint | เทียบ backend, Service name, selector และ endpoints |
| ได้ 503 เมื่อชื่อ Service ถูก | port ใน Ingress ไม่ตรง Service port | ตรวจ `describe ingress` และ controller log |
| `/api` ไป web | วาง path/ชน prefix ผิด | ตรวจ rule และใช้ `pathType: Prefix` ให้ตรงเจตนา |
| ADDRESS ยังว่างช่วงแรก | controller ยัง sync status | รอ Events `Sync`; ไม่ใช้ ADDRESS อย่างเดียวตัดสิน route |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab017 --wait=true
kubectl get all -n lab017
kubectl create namespace lab017
kubectl apply -f manifests/
kubectl wait -n lab017 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
until curl -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
curl -s http://localhost/api/whoami | jq -c '{pod,version,time}'
kubectl delete namespace lab017 --wait=true
kubectl get all -n lab017
```
> 📝 **คำอธิบาย:** ลบ namespace พร้อมรอ · `get all` พิสูจน์ความว่าง · สร้าง/apply/wait จากไฟล์เดิม · curl สอง path พิสูจน์ route เดิม · ลบครั้งสุดท้ายไม่ทิ้ง resource ให้แล็บถัดไป

✅ **Expected output** — Clean Re-run ตอบได้ทั้ง web/api แล้วปิดท้ายไม่เหลือ resource (ชื่อ Pod/เวลาต่างกันได้):
```text
namespace "lab017" deleted
No resources found in lab017 namespace.
namespace/lab017 created
deployment.apps/db condition met
deployment.apps/api condition met
deployment.apps/web condition met
{"pod":"web-7484cf7478-qpz5f","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-45jzl"},"db":{"status":"up"}}
{"pod":"api-6b56dd98f-45jzl","version":"v1","time":"2026-09-02T16:56:48+00:00"}
namespace "lab017" deleted
No resources found in lab017 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get/describe ingress` | อ่านกฎ, address และ backend |
| `curl .../info` | ทดสอบ path ที่ไป web |
| `curl .../api/whoami` | ทดสอบ path ที่ไป api |
| `kubectl logs -n ingress-nginx ...` | อ่าน access/error log ของ proxy |
| `kubectl patch ingress` | เปลี่ยน field ชั่วคราวเพื่อทดลอง |
| `kubectl apply -f manifests/06-ingress.yaml` | คืนกฎที่ถูกจาก source of truth |

## สรุปสิ่งที่ได้เรียนรู้

Ingress ทำให้ผู้ใช้จำ URL เดียว แต่ยังคง Service แยกหน้าที่ภายใน cluster:

- Ingress คือกฎ ส่วน ingress controller คือ reverse proxy ที่นำกฎไปทำงาน
- NodePort เปิด port ต่อ Service; Ingress แยกทางด้วย HTTP path/host ที่ประตูเดียว
- backend ต้องอ้าง Service name และ Service port ที่มีจริง ไม่ใช่ container port ที่เดาเอง
- 503 จาก controller บอกว่าเข้าประตูได้แล้ว แต่เดินต่อไป backend ไม่ได้

**จำภาพเดียวให้ได้:** Ingress คือป้ายบอกทางหน้าประตู; controller คือยามที่อ่านป้าย แล้วส่ง `/` ไป web และ `/api` ไป api

🧭 ต่อยอด: [LAB 18 — Updating without Downtime](../018-updating-without-downtime/README.md) ใช้ประตูเดิมเฝ้าดู rolling update

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **Ingress ต่างจาก NodePort อย่างไร?** — NodePort เปิด L4 port ต่อ Service; Ingress ใช้ L7 path/host รวมหลาย Service ไว้หลัง 80/443
2. **Ingress เกี่ยวข้องกับ reverse proxy อย่างไร?** — Ingress คือ config object; controller เช่น nginx/Traefik คือ proxy ที่ watch object แล้ว config ตัวเอง
3. **ทำไม `/api` ไม่ต้องตัด prefix?** — FastAPI ของ SkillSpace ประกาศ route ใต้ `/api` อยู่แล้ว; แอปที่ไม่รู้จัก prefix จึงค่อยต้อง rewrite

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] controller Running และ hostPort 80/443 พร้อม
- [ ] เปิดหน้าเว็บผ่าน `http://localhost:8080` ได้
- [ ] `/api/whoami` ตอบชื่อ API Pod ผ่าน URL เดียวกัน
- [ ] อ่าน controller log แล้วชี้ backend ของแต่ละ path ได้
- [ ] ทำ Service name และ port ให้ผิดจนเห็น 503 จริงแล้ว
- [ ] apply manifest ที่ถูกและยืนยัน 200 กลับมาแล้ว
- [ ] Clean Re-run ผ่านและลบ `lab017` ปิดท้ายแล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
