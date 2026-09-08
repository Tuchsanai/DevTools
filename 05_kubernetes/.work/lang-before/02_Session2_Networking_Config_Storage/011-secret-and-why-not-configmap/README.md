# LAB 11 — Secret : แยกข้อมูลลับ และเปิดหน้ากาก base64

> โฟลเดอร์ `011-secret-and-why-not-configmap` = LAB 11 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `01-secret.yaml`, `02-db.yaml`, `03-api.yaml`, `04-web.yaml`, `05-door.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** ข้อมูลลับต้องแยกออกมาต่างหาก และ base64 ไม่ใช่การเข้ารหัส

## วัตถุประสงค์ของแล็บ

1. อธิบายได้ว่า Secret แยก “เจตนาและขอบเขตสิทธิ์” ออกจาก ConfigMap อย่างไร
2. พิสูจน์ได้ว่า base64 ถอดกลับเป็นข้อความเดิมได้ทันที
3. อธิบายเส้นทาง Secret → db/api Pod โดยไม่ฝังรหัสผ่านใน image
4. อ่านอาการรหัสผ่านผิดจากหน้าเว็บ, `/ready` และ log แล้วแก้กลับได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ConfigMap และ Secret ส่งค่าเข้า Pod ด้วยกลไกคล้ายกัน แต่ Secret บอกชัดว่า object นี้เป็นข้อมูลอ่อนไหว จึงแยก RBAC, audit และ encryption at rest ได้ง่ายกว่า ค่าใน `data` ยังเป็นเพียง base64 ซึ่งออกแบบเพื่อขนส่ง bytes ผ่าน YAML/JSON ไม่ได้ออกแบบเพื่อซ่อนข้อมูล

| เปรียบเทียบ | ConfigMap | Secret |
|---|---|---|
| ข้อมูล | ชื่อระบบ, theme, URL | รหัสผ่าน, token, key |
| ค่าใน API | ข้อความ | base64 โดยปกติ |
| ถอดกลับได้ | อ่านตรง ๆ | ได้ในคำสั่งเดียว |
| ความปลอดภัยจริง | RBAC | RBAC + encryption at rest + rotation |

ไฟล์ `01-secret.yaml` ใช้ `stringData` เพื่อให้ผู้เรียนอ่านง่าย API server จะแปลงไปเก็บใต้ `data` เป็น base64 งานจริงไม่ควร commit ค่าจริงลง Git; ใช้ external secret manager หรือ inject ตอน deploy

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น Secret ใน YAML กลายเป็น `bGFicGFzcw==`
- จะได้ใช้ `secretKeyRef` กับทั้ง PostgreSQL และ API
- จะได้เห็น dashboard มี seed data และการ์ด web/api/db เขียวครบ
- จะได้ถอด base64 กลับเป็น `labpass`
- จะได้ทำรหัสผิดและอ่าน `password authentication failed`
- จะได้แก้ Secret พร้อม restart เฉพาะ consumer ที่ต้องอ่านค่าใหม่

## ภาพรวมของแล็บนี้

1. สร้าง Secret
2. เปิด db, api, web และ Ingress โดยส่งรหัสผ่านผ่าน `secretKeyRef`
3. พิสูจน์ระบบครบ 3 ชั้นจาก UI และฐานข้อมูล
4. ถอด base64 และอ่าน environment ใน Pod
5. ใส่รหัสผิด, อ่านอาการ, แก้กลับ และทำ Clean Re-run

![Secret ส่งรหัสผ่านให้ API และ PostgreSQL](../slides_assets/lab011-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้าใครถอด base64 ได้ในคำสั่งเดียว ความปลอดภัยของ Secret มาจากส่วนไหนกันแน่?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน kind node

✅ **Expected output** — 3 nodes Ready และพบ image 4 ตัว (ตัดบางคอลัมน์; AGE/hash ต่างกันได้):

```text
devtools-control-plane   Ready   control-plane   12m   v1.36.4
devtools-worker          Ready   <none>          12m   v1.36.4
devtools-worker2         Ready   <none>          12m   v1.36.4
docker.io/library/k8s-lab-api   v1   37b98a526d09b   186MB
docker.io/library/k8s-lab-db    v1   12de2be925d8a   300MB
docker.io/library/k8s-lab-web   v1   f46e8e22f91a6   209MB
docker.io/library/k8s-lab-web   v2   fccf050046905   209MB
…
```

ถ้ายังไม่พบ image ให้ทำขั้น build/load ใน LAB 001 หรือ README ระดับชุดก่อน

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap
```

> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace · `git clone` ดึง repository · `cd` เข้า LAB 11

✅ **Expected output** — clone เริ่มและ path ถูกต้อง:

```text
Cloning into 'DevTools'...
/root/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap
```

ถ้ามี repository แล้ว ให้ใช้ `git pull` ในของเดิมแทนการ clone ซ้ำ

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-secret.yaml` | Secret | เก็บรหัสผ่านสมมุติของแล็บ | [Secret](../YAML_Guide.md#secret) |
| `02-db.yaml` | Deployment, Service | ส่งรหัสผ่าน key เดียวให้ PostgreSQL | [Deployment](../YAML_Guide.md#deployment) · [Secret](../YAML_Guide.md#secret) |
| `03-api.yaml` | Deployment, Service | ให้ API อ่าน Secret key เดียวกัน | [Deployment](../YAML_Guide.md#deployment) · [Secret](../YAML_Guide.md#secret) |
| `04-web.yaml` | Deployment, Service | ต่อ web ไป API ด้วย Service DNS | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `05-door.yaml` | Ingress | เปิดประตู path `/` ไป web | [Ingress](../YAML_Guide.md#ingress) |

Secret จริงจาก `01-secret.yaml`:

```yaml
type: Opaque
stringData:
  POSTGRES_PASSWORD: labpass
```

จุดอ่านค่าจริงจาก `03-api.yaml`:

```yaml
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: POSTGRES_PASSWORD
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `type: Opaque` | Secret แบบ key/value ทั่วไป | เว้นว่างก็ default เป็น `Opaque` |
| `stringData` | รับข้อความแล้ว API server encode ไปเก็บใน `data` | เหมาะตอนเขียน แต่ base64 ที่เก็บไม่ใช่ encryption |
| `data` | map ของค่า base64 ที่เห็นจาก `get -o yaml` | ไม่มีในไฟล์ต้นทางนี้ จึงไม่แต่งค่าตัวอย่าง |
| `secretKeyRef` | เลือก Secret และ key ให้ env ตัวเดียว | ชื่อ/key ผิดทำให้ Container เริ่มไม่ได้ |

`envFrom.secretRef` ใช้นำทุก key เข้า env ได้ แต่ไม่มีใน manifest แล็บนี้และกระจายค่าเกินจำเป็นสำหรับโจทย์นี้ Secret ผ่าน env จะเปลี่ยนเมื่อสร้าง Container ใหม่ ไม่อัปเดต env เดิม

**ผิดบ่อยในแล็บนี้:** ค่า Secret ของ API กับ db ไม่ตรงกันยัง apply ผ่าน แต่ runlog บันทึกจริง `FATAL: password authentication failed for user "opsuser"`; ห้ามแก้ด้วยการเขียนรหัสจริงลง Deployment ให้ตรวจ `secretKeyRef`, rollout restart Deployment ที่อ้าง Secret และดู `kubectl logs`

ดู schema ได้ด้วย `kubectl explain secret.stringData` และ `kubectl explain deployment.spec.template.spec.containers.env.valueFrom.secretKeyRef`

## 3. สร้าง namespace และ Secret

ส่วนสำคัญของ `01-secret.yaml`:

```yaml
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: labpass
```

`Opaque` คือ Secret ทั่วไป · `stringData` รับข้อความและแปลงเป็น base64 · `labpass` เป็นค่าสมมุติสำหรับห้องเรียนเท่านั้น

```bash
kubectl create namespace lab011
kubectl apply -f 01-secret.yaml
kubectl get secret db-secret -n lab011 -o yaml
```

> 📝 **คำอธิบาย:** namespace แยก resource ของแล็บ · apply ส่ง Secret · `-o yaml` อ่านสิ่งที่ API server เก็บจริง

✅ **Expected output** — ค่าอยู่ใต้ `data` เป็น base64 (ตัดบางแถวจาก metadata):

```text
namespace/lab011 created
secret/db-secret created
…
data:
  POSTGRES_PASSWORD: bGFicGFzcw==
type: Opaque
```

## 4. ส่ง Secret ให้ db และ api

ทั้งสอง Deployment เลือก key เดียวกันด้วย:

```yaml
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: POSTGRES_PASSWORD
```

ฝั่ง db ใช้ชื่อ environment `POSTGRES_PASSWORD` ส่วน api ใช้ `DB_PASSWORD` ชื่อปลายทางต่างกันได้ แต่ Secret/key ต้นทางเดียวกัน

```bash
kubectl apply -f 02-db.yaml
kubectl wait -n lab011 --for=condition=available deployment/db --timeout=180s
kubectl apply -f 03-api.yaml -f 04-web.yaml -f 05-door.yaml
kubectl wait -n lab011 --for=condition=available deployment/api deployment/web --timeout=180s
until curl --retry 0 -sf http://localhost/info >/dev/null; do sleep 1; done
```

> 📝 **คำอธิบาย:** เปิด db ก่อน consumer · Service `db` ให้ชื่อคงที่ · API อ่านค่าจาก Secret · web เรียก `http://api:8000` · Ingress path `/` เปิดที่ `localhost:8080`

✅ **Expected output** — Deployment และ Service ครบ 3 ชั้นถูกสร้าง:

```text
deployment.apps/db created
service/db created
deployment.apps/db condition met
deployment.apps/api created
service/api created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/api condition met
deployment.apps/web condition met
```

`03-api.yaml` กำหนด `DB_PORT: "5432"` ชัดเจน เพื่อไม่ให้ชนกับ Service environment variable ชื่อเดียวกัน

## 5. พิสูจน์ระบบครบ 3 ชั้น

```bash
curl -s http://localhost/info | jq -c '{api,db}'
kubectl exec -n lab011 deployment/db -- psql -U opsuser -d skillspace -c 'select count(*) from tickets;'
```

> 📝 **คำอธิบาย:** `/info` ตรวจ Pod และ dependency จากมุม web · `exec` เข้า db · `psql -U/-d` เลือก user/database · query นับ seed data

✅ **Expected output** — API reachable, DB up และมี ticket 8 ใบ; ชื่อ Pod/เวลาแตกต่างกันได้:

```text
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-dk7wf"},"db":{"status":"up"}}
 count
-------
     8
(1 row)
```

![dashboard มีข้อมูลจริงและสถานะเขียวครบสามชั้น](images/03-dashboard-with-real-data.png)

ภาพจริงแสดง web Pod, api Pod และ PostgreSQL `up` พร้อมตัวเลขจาก seed data

## 6. ถอด base64 และดูค่าที่ Pod ใช้จริง

```bash
kubectl get secret db-secret -n lab011 -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
kubectl exec -n lab011 deployment/api -- sh -c "env | grep -E '^DB_(HOST|PORT|NAME|USER|PASSWORD)=' | sort"
```

> 📝 **คำอธิบาย:** `jsonpath` เลือกค่าหนึ่ง key · pipe ส่งให้ `base64 -d` ถอดกลับ · `env` ยืนยันว่า process ต้องได้รับข้อความจริงจึงจะ login ได้

✅ **Expected output** — base64 ไม่ได้ปกปิดรหัส และ API เห็นค่าจริง:

```text
labpass
DB_HOST=db
DB_NAME=skillspace
DB_PASSWORD=labpass
DB_PORT=5432
DB_USER=opsuser
```

คนที่มีสิทธิ์อ่าน Secret หรือ exec เข้า Pod จึงอาจเห็นค่าจริง ความปลอดภัยมาจากการจำกัดสิทธิ์ ไม่ใช่รูปแบบ base64

## 7. ทดลองให้พัง — เปลี่ยนรหัสเฉพาะ API

```bash
kubectl create secret generic db-secret -n lab011 --from-literal=POSTGRES_PASSWORD=wrongpass --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart -n lab011 deployment/api
kubectl rollout status -n lab011 deployment/api --timeout=120s
kubectl exec -n lab011 deployment/web -- wget -T 5 -S -O- http://api:8000/ready || true
sleep 3
kubectl exec -n lab011 deployment/web -- wget -T 5 -S -O- http://api:8000/ready || true
```

> 📝 **คำอธิบาย:** `--from-literal` สร้างค่าทดลอง · API ต้อง restart เพราะ env ไม่ reload · `wget -T 5` จำกัดเวลารอ · ครั้งแรกอาจ connection refused จึงรอ 3 วินาทีแล้วรันซ้ำ · `|| true` ให้ไปอ่าน log ต่อ

✅ **Expected output** — API process ยัง Running แต่ `/ready` ปฏิเสธ 503:

```text
secret/db-secret configured
deployment.apps/api restarted
deployment "api" successfully rolled out
Connecting to api:8000 (10.96.116.113:8000)
wget: can't connect to remote host (10.96.116.113): Connection refused
command terminated with exit code 1
Connecting to api:8000 (10.96.116.113:8000)
  HTTP/1.1 503 Service Unavailable
wget: server returned error: HTTP/1.1 503 Service Unavailable
command terminated with exit code 1
```

อ่านสาเหตุจาก log และหน้าเว็บ:

```bash
kubectl logs -n lab011 deployment/api | grep -E 'startup db=down|GET /ready' | tail -3
curl -s http://localhost/info | jq -c '{api,db}'
```

> 📝 **คำอธิบาย:** log คือเสียงของแอปและบอก authentication โดยตรง · `/info` แสดงผลกระทบที่ผู้ใช้เห็น · ไม่ต้องเดาจากสถานะ Running

✅ **Expected output** — log ชี้รหัสผิด และการ์ด db เป็น down (ตัดข้อความท้ายในค่า `error` ด้วย `…`):

```text
[api] startup db=down (connection failed: connection to server at "10.96.88.226", port 5432 failed: FATAL: password authentication failed for user "opsuser") — API ยังให้บริการต่อ
[api] GET /ready 503 6ms
[api] GET /ready 503 5ms
{"api":{"configured":true,"reachable":true,"pod":"api-6477946b67-gt56j"},"db":{"status":"down","error":"connection failed: connection to server at \"10.96.88.226\", port 5432 failed: FATAL: password authentication failed for …"}}
```

![หน้าเว็บยังตอบได้แต่ฐานข้อมูลแสดง authentication failed](images/break-db-auth-failed.png)

แล็บนี้ยังไม่มี volume หาก restart db จริง Pod ใหม่จะ init ฐานข้อมูลใหม่และอาจรับรหัสใหม่ ซึ่งทำให้ข้อมูล reset และบดบังบทเรียน Secret จึงแก้เฉพาะ Secret และ restart consumer ส่วนกรณีฐานข้อมูลที่มี persistent data การ restart ไม่เปลี่ยนรหัสที่ init ไปแล้ว

แก้ Secret กลับและสร้าง API Pod ใหม่:

```bash
kubectl apply -f 01-secret.yaml
kubectl rollout restart -n lab011 deployment/api
kubectl rollout status -n lab011 deployment/api --timeout=120s
until curl --retry 0 -s http://localhost/info | jq -e '.db.status == "up"' >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{api,db}'
```

> 📝 **คำอธิบาย:** apply คืน `labpass` · restart ให้ API อ่านค่าใหม่ · curl ยืนยันทั้ง API และ DB ไม่ใช่ดู rollout อย่างเดียว

✅ **Expected output** — ระบบกลับมาเขียว:

```text
secret/db-secret configured
deployment.apps/api restarted
deployment "api" successfully rolled out
{"api":{"configured":true,"reachable":true,"pod":"api-b569554f7-wpsg7"},"db":{"status":"up"}}
```

## 8. แบบฝึกหัดสั้น (Exercise)

สร้าง Secret อีกตัวชื่อ `api-secret` มี key `DEMO_TOKEN` แล้วส่งเฉพาะ key นี้เข้า API ด้วย `secretKeyRef` เกณฑ์สำเร็จคือ Pod ใหม่ Running, `describe` ไม่พิมพ์ค่าจริง และผู้เรียนอธิบายได้ว่าทำไมยังต้องจำกัดสิทธิ์ exec

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get all,ingress,secret -n lab011
kubectl logs -n lab011 deployment/api --tail=12
curl -s http://localhost/info | jq -c '{api,db}'
```

> 📝 **คำอธิบาย:** `get all` ตรวจ resource หลัก · ระบุ `ingress,secret` เพิ่ม · log ยืนยัน DB connection · `/info` ตรวจเส้นทาง browser → web → api → db

✅ **Expected output** — Deployment ทั้งสาม `1/1`, log มี `startup db=up`, UI/API/DB พร้อม (ตัดบางแถว/บางคอลัมน์):

```text
…
deployment.apps/api   1/1   1   1
deployment.apps/db    1/1   1   1
deployment.apps/web   1/1   1   1
[api] startup db=up
{"api":{"configured":true,"reachable":true,"pod":"api-b569554f7-wpsg7"},"db":{"status":"up"}}
```

ค่า Pod, ClusterIP, AGE, hash และเวลาแตกต่างกันได้

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `Servname not supported for ai_socktype` | `DB_PORT` ชน Service env | กำหนด `DB_PORT: "5432"` |
| `/ready` ตอบ 503 | รหัส/host/db ไม่พร้อม | อ่าน API log |
| API connection refused ทันทีหลัง rollout | process เพิ่งเริ่มแต่ไม่มี readiness probe | รอสั้น ๆ แล้วเรียกซ้ำ |
| Secret เปลี่ยนแต่ API ยังใช้ค่าเดิม | env เป็น snapshot | restart API Deployment |
| `ImagePullBackOff` | image ไม่อยู่ใน kind | กลับไป build/load LAB 001 |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab011 --wait=true
kubectl get all -n lab011
kubectl create namespace lab011
kubectl apply -f 01-secret.yaml -f 02-db.yaml -f 03-api.yaml -f 04-web.yaml -f 05-door.yaml
kubectl wait -n lab011 --for=condition=available deployment/db deployment/api deployment/web --timeout=180s
until curl --retry 0 -s http://localhost/info | jq -e '.api.reachable == true and .db.status == "up"' >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{api,db}'
kubectl delete namespace lab011 --wait=true
kubectl get all -n lab011
```

> 📝 **คำอธิบาย:** ลบ namespace ให้สะอาด · apply manifest ทั้งชุดจากศูนย์ · wait ทั้งสาม Deployment · ตรวจ dependency จริง · ลบปิดท้ายไม่ให้ชนแล็บถัดไป

✅ **Expected output** — Clean Re-run เขียวครบและจบโดยไม่เหลือ resource:

```text
namespace "lab011" deleted
No resources found in lab011 namespace.
namespace/lab011 created
secret/db-secret created
deployment.apps/db created
service/db created
deployment.apps/api created
service/api created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/web created
deployment.apps/db condition met
deployment.apps/api condition met
deployment.apps/web condition met
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-bxm7s"},"db":{"status":"up"}}
namespace "lab011" deleted
No resources found in lab011 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get secret ... -o yaml` | อ่าน representation ใน API |
| `base64 -d` | ถอด base64 กลับเป็นข้อความ |
| `secretKeyRef` | เลือก key จาก Secret เข้า env |
| `kubectl logs deployment/api` | อ่านสาเหตุการเชื่อมต่อ DB |
| `kubectl rollout restart` | สร้าง consumer ใหม่ให้อ่าน Secret ล่าสุด |
| `kubectl delete namespace lab011` | ล้างทุก object ในแล็บ |

## สรุปสิ่งที่ได้เรียนรู้

Secret แยกข้อมูลอ่อนไหวออกจาก image/ConfigMap แต่ base64 ถอดกลับได้ ความปลอดภัยจริงต้องพึ่ง RBAC, encryption at rest, audit, rotation และการไม่ commit ค่าจริงลง Git

- ส่งรหัสเดียวกันให้ db/api ผ่าน key reference ได้
- พิสูจน์ได้ว่า Pod เห็น plaintext เพื่อใช้งาน
- อ่าน 503 และ authentication failure จากหลักฐานสามมุมได้
- แก้ Secret, restart consumer และ Clean Re-run ได้

**จำภาพเดียวให้ได้:** base64 คือซองจัดรูปแบบ ไม่ใช่ตู้เซฟ; กุญแจจริงคือสิทธิ์เข้าถึง

🧭 ต่อยอด: [LAB 12 — ทำไมข้อมูลใน container จึงหาย](../012-why-data-disappears/README.md)

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **Secret ต่างจาก ConfigMap อย่างไร?** — กลไกส่งค่าคล้ายกัน แต่ Secret แยกชนิดเพื่อคุมสิทธิ์/เข้ารหัส/audit ได้เหมาะสม
2. **base64 ปลอดภัยไหม?** — ไม่ ถอดกลับได้ทันที; ความปลอดภัยมาจาก access control และ encryption at rest
3. **ทำไมห้าม commit Secret จริงลง Git?** — Git เก็บประวัติยาวและผู้เข้าถึง repository อาจอ่านรหัสได้แม้ลบใน commit ใหม่

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เห็น Secret เป็น base64 และถอดกลับได้
- [ ] เห็น dashboard พร้อมข้อมูล seed
- [ ] ทำรหัสผิดและอ่าน 503/log ได้
- [ ] แก้กลับจน db เป็น up
- [ ] Clean Re-run ผ่านและลบ `lab011` แล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
