# LAB 16 — Adding a Database : ทำไมชั้นข้อมูลจึง scale เหมือน web ไม่ได้

> โฟลเดอร์ `016-adding-a-database` = LAB 16 ของชุด Kubernetes ครั้งที่ 3
> (ไฟล์ของแล็บนี้: `manifests/01-configmap.yaml` ถึง `manifests/10-db-service.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** ส่วนที่มีข้อมูลต้องการการดูแลต่างจากส่วนที่ไม่มีข้อมูล

## วัตถุประสงค์ของแล็บ

1. อธิบายได้ว่า stateless กับ stateful ต่างกันอย่างไรในทางปฏิบัติ
2. อธิบายบทบาทของ Secret, PVC และ Service ที่ทำให้ PostgreSQL เป็นชั้นข้อมูลของระบบ
3. พิสูจน์ได้ว่าข้อมูลบน PVC อยู่ต่อ แม้ DB Pod ถูกลบและสร้างใหม่
4. อ่านอาการผิดปกติเมื่อพยายามให้ PostgreSQL สองตัวใช้ data directory เดียวกันได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

web และ api เป็น stateless: Pod ใหม่เริ่มจาก image เดิม รับ request แล้วจบงานโดยไม่ต้องพกไฟล์ประจำตัวไปด้วย จึงเพิ่มหรือลด replica ได้ง่าย

PostgreSQL เป็น stateful: ตัว process อาจสร้างใหม่ได้ แต่ข้อมูลต้องมีเจ้าของ ตำแหน่งเก็บ และกติกาการเขียนที่ชัดเจน แล็บนี้ใช้ PVC ขอพื้นที่ `1Gi` และ mount ที่ `/var/lib/postgresql/data`

| ประเด็น | web / api (stateless) | PostgreSQL (stateful) |
|---|---|---|
| สร้าง Pod ใหม่ | เริ่มรับงานจาก image เดิม | ต้องกลับมาเห็น data directory เดิม |
| scale | เพิ่ม replica ได้ตรง ๆ | ต้องออกแบบ replication และเจ้าของข้อมูล |
| สิ่งที่ต้องรักษา | config และ image version | ข้อมูล, ลำดับการเริ่ม, backup |
| object ที่ช่วย | Deployment + Service | PVC + Deployment; งานจริงมักใช้ StatefulSet/managed DB |

Secret ในแล็บนี้แยกรหัสผ่านจำลอง `labpass` ออกจาก Deployment ส่วน PVC แยกข้อมูลออกจากวงจรชีวิตของ Pod แต่ PVC ไม่ใช่ backup และไม่ได้ทำให้ PostgreSQL scale ได้โดยอัตโนมัติ

## สิ่งที่จะได้เรียนรู้

- จะได้เห็นระบบ SkillSpace ครบ web → api → db ผ่าน URL เดียว
- จะได้เห็น API อ่าน `DB_PASSWORD` จาก Secret
- จะได้พิสูจน์ว่า ticket ที่สร้างจากหน้าเว็บยังอยู่หลัง DB Pod เปลี่ยนชื่อ
- จะได้เห็น web และ api เพิ่มเป็น 3 replicas ได้โดยไม่ผูกกับดิสก์
- จะได้เห็นความเสี่ยงเมื่อ PostgreSQL สอง process ใช้ PVC เดียวกัน
- จะได้อ่านหลักฐานจาก `kubectl get`, application log และหน้าเว็บ
- จะได้พิสูจน์ว่า manifests ชุดเดิมสร้างระบบใหม่จาก namespace ว่างได้

## ภาพรวมของแล็บนี้

1. สร้าง namespace และ apply manifest 10 ไฟล์
2. ตรวจระบบครบสามชั้นจาก terminal, หน้าเว็บ และ log
3. สร้าง ticket แล้วลบ DB Pod เพื่อพิสูจน์ persistence
4. scale stateless workload แล้วเปรียบเทียบกับ database
5. จงใจลบ Secret อ่านอาการ แล้วซ่อมจาก manifest
6. Cleanup, Clean Re-run และลบปิดท้าย

![สถาปัตยกรรม web, api, PostgreSQL และ PVC ของ LAB 16](../slides_assets/lab016-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า web เพิ่มจาก 1 เป็น 3 ตัวได้ด้วยคำสั่งเดียว เหตุใด PostgreSQL จึงไม่ควรทำแบบเดียวกันบน PVC เดียว?

## 0. เตรียมเครื่องเรียน

เปิดเครื่องเรียนจาก host; ถ้ามี container เดิมคำสั่งแรกจะ start ต่อ ถ้ายังไม่มีจึงสร้างใหม่
```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** เข้าเครื่องเรียนด้วย `docker exec -it` (ทุกคำสั่งหลังจากนี้พิมพ์ในเครื่องเรียน) · `k8s-bootstrap` ข้ามเองถ้า cluster มีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน kind node

ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `localhost:8080`

✅ **Expected output** — node ทั้ง 3 เป็น `Ready` และพบ image แอป 4 รายการ (ชื่อ Pod, IP, AGE และ image ID ต่างกันได้):
```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready    control-plane   92s   v1.36.4
devtools-worker          Ready    <none>          81s   v1.36.4
devtools-worker2         Ready    <none>          81s   v1.36.4
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
cd ~/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/016-adding-a-database
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง path ซ้ำได้ · `&&` ทำขั้นถัดไปเมื่อขั้นก่อนสำเร็จ · `git clone` ดาวน์โหลด repository · `cd` เข้าโฟลเดอร์ LAB 16

✅ **Expected output** — clone สำเร็จและ prompt อยู่ในโฟลเดอร์แล็บ:
```text
Cloning into 'DevTools'...
```

ถ้า clone ไว้แล้ว ไม่ต้อง clone ซ้ำ ให้เข้า `~/labwork/DevTools` แล้วใช้ `git pull` ก่อน `cd` เข้าแล็บ

## 2. อ่าน YAML ของแล็บนี้

อ่านชุดนี้เป็นสองกลุ่ม: `01-06` ประกอบ web/api เดิม ส่วน `07-10` เติม Secret, PVC และ db
การเปลี่ยน `04-api-deployment.yaml` คือจุดเชื่อมฐานข้อมูลเข้ากับระบบเดิม

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/01-configmap.yaml` | ConfigMap | กำหนดชื่อเว็บและ URL ของ api | [ทบทวน ConfigMap](../YAML_Guide.md#configmap) |
| `manifests/02-web-deployment.yaml` | Deployment | รัน web พร้อม readiness | [ทบทวน Deployment](../YAML_Guide.md#deployment) · [ทบทวน Probes](../YAML_Guide.md#probes) |
| `manifests/03-web-service.yaml` | Service | เป็นปลายทางคงที่ของ web | [ทบทวน Service](../YAML_Guide.md#service) |
| `manifests/04-api-deployment.yaml` | Deployment | อ่าน Secret แล้วเชื่อม db | [ทบทวน Deployment](../YAML_Guide.md#deployment) · [ทบทวน Secret](../YAML_Guide.md#secret) |
| `manifests/05-api-service.yaml` | Service | ให้ web เรียก api ด้วย DNS | [ทบทวน Service](../YAML_Guide.md#service) |
| `manifests/06-ingress.yaml` | Ingress | แยก `/api` กับ `/` | [Ingress](../YAML_Guide.md#1-ingress) |
| `manifests/07-secret.yaml` | Secret | เก็บค่าเชื่อมต่อ PostgreSQL ของแล็บ | [ทบทวน Secret](../YAML_Guide.md#secret) |
| `manifests/08-pvc.yaml` | PersistentVolumeClaim | ขอ storage 1Gi แบบ ReadWriteOnce | [ทบทวน PVC](../YAML_Guide.md#pvc) |
| `manifests/09-db-deployment.yaml` | Deployment | mount PVC และใช้ `Recreate` | [strategy](../YAML_Guide.md#3-strategy) |
| `manifests/10-db-service.yaml` | Service | ให้ api เรียก db ที่ port 5432 | [ทบทวน Service](../YAML_Guide.md#service) |

สังเกตว่า `resources.requests.storage` ของ PVC คือ “ขอพื้นที่” ไม่ใช่ container resources;
ส่วน `strategy.type: Recreate` อยู่ที่ Deployment เพราะไม่ต้องการให้ db สอง Pod ใช้ data directory พร้อมกัน

**ผิดบ่อยในแล็บนี้:** ลบ Secret แล้ว restart api ทำให้ Pod ใหม่เป็น `CreateContainerConfigError`;
runlog บันทึกสถานะนี้จริง ให้ `kubectl describe pod` หา key/Secret ที่ขาด แล้ว apply `07-secret.yaml` คืน

ดู field ได้ด้วย `kubectl explain deployment.spec.strategy`, `kubectl explain pvc.spec.resources.requests` และ `kubectl explain pod.spec.containers.env.valueFrom.secretKeyRef`

## 3. สร้างระบบสามชั้นจาก manifest

ไฟล์ใหม่ที่ทำให้ระบบจาก LAB 15 มีฐานข้อมูลคือ `07-secret.yaml`, `08-pvc.yaml`, `09-db-deployment.yaml` และ `10-db-service.yaml`; `04-api-deployment.yaml` ถูกต่อให้ใช้ Secret
```yaml
env:
  - name: DB_PORT
    value: "5432"       # กันการชนกับ Service env ชื่อ DB_PORT
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: POSTGRES_PASSWORD
```
```yaml
volumeMounts:
  - name: data
    mountPath: /var/lib/postgresql/data
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: db-data
```

`secretKeyRef` ไม่เปิดเผยค่าใน Pod template · `claimName` ผูก Pod กับ PVC · `PGDATA` ในไฟล์เต็มชี้ไป subdirectory `pgdata` · ทุก image ของแอปใช้ `imagePullPolicy: IfNotPresent`
```bash
kubectl create namespace lab016
kubectl apply -f manifests/
kubectl wait -n lab016 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
```
> 📝 **คำอธิบาย:** `create namespace` สร้างห้องแยกของแล็บ · `apply -f manifests/` ส่งทุก YAML ในโฟลเดอร์ · `wait` รอ Deployment ทั้งสามมี Available replica · `--timeout=180s` หยุดรอเมื่อเกินสามนาที

✅ **Expected output** — object ทั้ง 10 ถูกสร้างและ Deployment ทั้งสามผ่าน condition:
```text
namespace/lab016 created
configmap/web-config created
deployment.apps/web created
service/web created
deployment.apps/api created
service/api created
ingress.networking.k8s.io/skillspace created
secret/db-secret created
persistentvolumeclaim/db-data created
deployment.apps/db created
service/db created
deployment.apps/db condition met
deployment.apps/api condition met
deployment.apps/web condition met
```

## 4. ตรวจหลักฐานสามมุม

```bash
kubectl get all,ingress,pvc,secret,configmap -n lab016
until curl -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
kubectl logs -n lab016 deploy/api --tail=5
```
> 📝 **คำอธิบาย:** `get all,ingress,pvc,secret,configmap` ดู compute, network, storage และ config พร้อมกัน · `curl -s` ไม่แสดง progress · `/info` เป็นหลักฐานสดจาก web · `jq` จัด JSON · `logs deploy/api` ให้ Kubernetes เลือก Pod ใต้ Deployment · `--tail=5` จำกัดห้าบรรทัดล่าสุด

✅ **Expected output** — Pod พร้อม 3 ตัว, PVC เป็น `Bound`, JSON บอก `db.status=up` และ log มี `/ready 200` (ชื่อ Pod, IP, AGE และเวลาต่างกันได้):
```text
persistentvolumeclaim/db-data   Bound   pvc-cc676cd3-3115-4fc5-85df-c1511d5a926c   1Gi   RWO
{"pod":"web-7484cf7478-8cznl","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-6fn92"},"db":{"status":"up"}}
[api] GET /ready 200 7ms
```

(ตัดบางแถวจาก `kubectl get`; ชื่อ Pod, IP และ AGE ต่างกันได้)

เปิด `http://localhost:8080` แล้วดูการ์ด WEB, API และ DB ต้องเป็นสถานะพร้อมทั้งสามแถว

![ระบบครบสามชั้นและการ์ดสถานะเขียว](images/02-full-stack-with-data.png)

## 5. พิสูจน์ว่าข้อมูลอยู่รอดหลัง DB Pod เกิดใหม่

เปิด `http://localhost:8080/tickets` เลือกครุภัณฑ์ กรอกหัวข้อ `ทดสอบ PVC ข้อมูลต้องอยู่รอด` แล้วกด **แจ้งซ่อม** จากนั้นตรวจ record และลบ DB Pod
```bash
curl -s http://localhost/api/tickets | jq -c '.[-1] | {id,title,status}'
kubectl get pod -n lab016 -l app=db -o name
kubectl delete pod -n lab016 -l app=db
kubectl wait -n lab016 --for=condition=ready pod -l app=db --timeout=120s
kubectl get pod -n lab016 -l app=db -o name
curl -s http://localhost/api/tickets | jq -c '.[-1] | {id,title,status}'
```
> 📝 **คำอธิบาย:** `.[-1] | {id,title,status}` เลือก record สุดท้ายและ field ที่แสดง · `-l app=db` เลือก Pod ด้วย label · `delete pod` ไม่ลบ PVC · `wait` รอ DB ใหม่พร้อมก่อนอ่านซ้ำ · path `/api` ผ่าน Ingress ที่มากับ manifest ของแล็บนี้

✅ **Expected output** — ชื่อ DB Pod เปลี่ยน แต่ ticket `#9` และข้อความเดิมยังอยู่ (suffix และเวลาแตกต่างกันได้):
```text
{"id":9,"title":"ทดสอบ PVC ข้อมูลต้องอยู่รอด","status":"NEW"}
pod/db-7dd8b59fd7-2sbkr
pod "db-7dd8b59fd7-2sbkr" deleted from lab016 namespace
pod/db-7dd8b59fd7-86jqs condition met
pod/db-7dd8b59fd7-86jqs
{"id":9,"title":"ทดสอบ PVC ข้อมูลต้องอยู่รอด","status":"NEW"}
```

![ticket #9 ยังอยู่หลัง DB Pod ถูกสร้างใหม่](images/03-data-survives.png)

## 6. เปรียบเทียบการ scale แบบ stateless

```bash
kubectl scale -n lab016 deploy/web deploy/api --replicas=3
kubectl wait -n lab016 --for=condition=available deploy/web deploy/api --timeout=120s
kubectl get pods -n lab016 -l 'app in (web,api)'
kubectl scale -n lab016 deploy/web deploy/api --replicas=1
```
> 📝 **คำอธิบาย:** `scale` เปลี่ยน desired replicas · ระบุ Deployment สองตัวในคำสั่งเดียว · `--replicas=3` ต้องการอย่างละสาม Pod · selector แบบ set `app in (...)` เลือกสองค่า · คำสั่งสุดท้ายคืน baseline อย่างละหนึ่ง

✅ **Expected output** — web และ api ขึ้นครบอย่างละ 3 โดยทุกตัว `1/1 Running` แล้ว scale กลับได้ (ชื่อ Pod และ AGE ต่างกันได้):
```text
deployment.apps/web scaled
deployment.apps/api scaled
api-6b56dd98f-6fn92    1/1   Running   0   2m26s
api-6b56dd98f-84dgh    1/1   Running   0   7s
api-6b56dd98f-dcsls    1/1   Running   0   7s
web-7484cf7478-8cznl   1/1   Running   0   6m21s
web-7484cf7478-kbk2c   1/1   Running   0   7s
web-7484cf7478-zhsmz   1/1   Running   0   7s
deployment.apps/web scaled
deployment.apps/api scaled
```

## 7. ทดลองให้พัง — PostgreSQL สองตัวเขียน PVC เดียวกัน

ทายก่อน: Pod ที่สองจะ `Pending`, crash หรือขึ้น `Ready`? ผลจริงบน local-path provisioner รอบนี้น่ากลัวกว่าการ fail ชัดเจน
```bash
kubectl scale -n lab016 deploy/db --replicas=2
kubectl get pods -n lab016 -l app=db -o wide
kubectl logs -n lab016 $(kubectl get pods -n lab016 -l app=db --sort-by=.metadata.creationTimestamp -o name | tail -1) --tail=20
kubectl scale -n lab016 deploy/db --replicas=1
kubectl rollout status -n lab016 deploy/db --timeout=120s
sleep 30
kubectl get pods -n lab016
```
> 📝 **คำอธิบาย:** `--replicas=2` จงใจให้ PostgreSQL สอง process ใช้ claim เดียว · `-o wide` ตรวจว่าอยู่ node ใด · `--sort-by` เรียงตามเวลาสร้าง · `tail -1` เลือก Pod ใหม่สุด · `logs` อ่านสิ่งที่ database ทำจริง · scale กลับหนึ่งทันทีเพื่อลดความเสี่ยง

✅ **Expected output** — Pod ที่สองขึ้น Ready บน node เดียวกัน และ log มี `automatic recovery`; หลังลด replica รอ rollout แล้วเหลือ DB หนึ่งตัว (ชื่อ Pod/เวลาต่างกันได้):
```text
db-7dd8b59fd7-86jqs   1/1   Running   0   2m7s   devtools-worker
db-7dd8b59fd7-n6cvl   1/1   Running   0   35s    devtools-worker
PostgreSQL Database directory appears to contain a database; Skipping initialization
LOG: database system was interrupted
LOG: database system was not properly shut down; automatic recovery in progress
deployment.apps/db scaled
deployment "db" successfully rolled out
db-7dd8b59fd7-86jqs   1/1   Running   0   2m40s
```

สาเหตุคือ `ReadWriteOnce` อนุญาตหลาย Pod บน node เดียวกันได้ จึงไม่ใช่ mutex ป้องกัน database สองตัว ผลจริงต่างจากที่หลายคนคาด (`CrashLoopBackOff`/`Pending`): ต้องใช้ replication ที่ PostgreSQL เข้าใจ, StatefulSet ที่มี PVC แยก หรือ managed database

## 8. ทดลองให้พัง — ลบ Secret แล้วซ่อมกลับ

```bash
kubectl delete secret -n lab016 db-secret
kubectl rollout restart -n lab016 deploy/api
sleep 8
kubectl get pods -n lab016 -l app=api
kubectl apply -f manifests/07-secret.yaml
kubectl rollout status -n lab016 deploy/api --timeout=120s
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** `delete secret` เอา dependency ของ Pod ใหม่ออก · `rollout restart` บังคับสร้าง Pod จาก template เดิม · `CreateContainerConfigError` ต้องอ่านว่า config ขาดก่อนดู log · `apply` คืน source of truth · `rollout status` ยืนยันการซ่อม · `/info` ตรวจครบถึง DB

✅ **Expected output** — Pod ใหม่ค้างเพราะ Secret หาย ขณะที่ Pod เก่ายังบริการ; apply คืนแล้ว rollout สำเร็จและ DB กลับ `up` (ชื่อ Podต่างกันได้):
```text
secret "db-secret" deleted from lab016 namespace
deployment.apps/api restarted
api-6b56dd98f-6fn92    1/1   Running                      0   4m6s
api-7b7c458b55-nd6lb   0/1   CreateContainerConfigError   0   8s
secret/db-secret created
deployment "api" successfully rolled out
{"pod":"web-7484cf7478-8cznl","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-7b7c458b55-nd6lb"},"db":{"status":"up"}}
```

## 9. แบบฝึกหัดสั้น (Exercise)

เปลี่ยนขนาด PVC ในไฟล์จาก `1Gi` เป็น `2Gi` แล้วใช้ `kubectl diff -f manifests/08-pvc.yaml` ทายก่อนว่า storage class นี้ขยาย volume เดิมได้หรือไม่ ห้าม apply จนกว่าจะอ่าน diff และ `kubectl describe storageclass standard` จบ

เกณฑ์สำเร็จ: อธิบายได้ว่า PVC คือ “คำขอพื้นที่” ไม่ใช่ตัว database และบอกได้ว่าต้องตรวจ `allowVolumeExpansion` ก่อนแก้ของจริง

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get pods,svc,endpoints,pvc -n lab016
kubectl get events -n lab016 --sort-by=.lastTimestamp
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
kubectl logs -n lab016 deploy/api --tail=10
```
> 📝 **คำอธิบาย:** `pods,svc,endpoints,pvc` ครอบคลุมตัวรัน เส้นทาง และ storage · `events --sort-by` เรียงเหตุการณ์ตามเวลา · `/info` เป็นมุมผู้ใช้ · `logs` เป็นมุมแอป

✅ **Expected output** — Pod ทั้งสาม Ready, Service มี endpoints, PVC Bound, `/info` บอก api reachable และ db up, log ไม่มี error ต่อเนื่อง:
```text
NAME                       READY   STATUS    RESTARTS
pod/api-7b7c458b55-nd6lb   1/1     Running   0
pod/db-7dd8b59fd7-86jqs    1/1     Running   1
pod/web-7484cf7478-8cznl   1/1     Running   0
{"pod":"web-7484cf7478-8cznl","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-7b7c458b55-nd6lb"},"db":{"status":"up"}}
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| API `/ready` 503 และ error `Servname not supported` | ไม่กำหนด `DB_PORT`; Service env ชื่อเดียวกันมีค่า `tcp://...` | กำหนด `DB_PORT: "5432"` ใน API Deployment แล้ว apply |
| API Pod เป็น `CreateContainerConfigError` | `db-secret` ไม่มี หรือ key ไม่ตรง | ดู Events แล้ว apply `07-secret.yaml` |
| PVC ค้าง `Pending` | provisioner ยังไม่พร้อมหรือยังไม่มี consumer | ดู PVC Events และ `local-path-provisioner` |
| DB Pod ใหม่ขึ้นแต่ข้อมูลหาย | mount/claim ผิด หรือสร้าง namespace ใหม่ซึ่งได้ PVC ใหม่ | ตรวจ `volumeMounts`, `claimName` และ PV ที่ Bound |
| DB สองตัวดูเหมือน Ready | RWO ยังยอมให้ mount หลาย Pod บน node เดียว | ลดเหลือหนึ่ง ตรวจ log/data และออกแบบ replication อย่างถูกต้อง |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

ลบทั้งห้อง รอจนหาย สร้างใหม่จากไฟล์เดิม ตรวจผล แล้วลบปิดท้าย
```bash
kubectl delete namespace lab016 --wait=true
kubectl get all -n lab016
kubectl create namespace lab016
kubectl apply -f manifests/
kubectl wait -n lab016 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
until BODY=$(curl -fsS http://localhost/info); do sleep 2; done
echo "$BODY" | jq -c '{pod,version,theme,api,db}'
kubectl delete namespace lab016 --wait=true
kubectl get all -n lab016
```
> 📝 **คำอธิบาย:** `delete namespace --wait=true` รอ resource ในห้องถูกลบ · `get all` พิสูจน์ว่าไม่เหลือ workload · สร้าง/apply/wait คือ Clean Re-run · `curl` พิสูจน์ผลเดิมจากระบบใหม่ · สองคำสั่งท้ายจบสะอาด

✅ **Expected output** — รอบใหม่กลับมาครบสามชั้น แล้วหลังลบสุดท้ายไม่เหลือ resource (ชื่อ Pod/เวลาต่างกันได้):
```text
namespace "lab016" deleted
No resources found in lab016 namespace.
namespace/lab016 created
deployment.apps/db condition met
deployment.apps/api condition met
deployment.apps/web condition met
{"pod":"web-7484cf7478-vmtk5","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-slc8z"},"db":{"status":"up"}}
namespace "lab016" deleted
No resources found in lab016 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl apply -f manifests/` | ทำ actual state ให้ตรงกับ manifest ทั้งชุด |
| `kubectl get all,ingress,pvc -n lab016` | ดู workload, ประตู และ storage |
| `kubectl delete pod -l app=db` | ทดสอบสร้าง DB Pod ใหม่โดยไม่ลบ PVC |
| `kubectl scale deploy/... --replicas=N` | เปลี่ยน desired replicas |
| `kubectl logs ...` | อ่านพฤติกรรมจริงของ process |
| `kubectl rollout restart/status` | สร้าง Pod ใหม่และติดตามผล |
| `kubectl delete namespace ... --wait=true` | ลบ resource ของแล็บและรอจนสะอาด |

## สรุปสิ่งที่ได้เรียนรู้

ระบบครบสามชั้นไม่ได้แปลว่าทุกชั้นดูแลเหมือนกัน:

- web/api สร้างทดแทนและ scale ได้ เพราะไม่ถือข้อมูลถาวรใน Pod
- PVC ทำให้ข้อมูลรอดจากการเปลี่ยน DB Pod แต่ไม่ทำ replication และไม่ใช่ backup
- Secret เป็น dependency ตอนสร้าง container; ถ้าหาย Pod เก่าอาจยังวิ่ง แต่ Pod ใหม่เริ่มไม่ได้
- อาการ `Ready` เพียงอย่างเดียวไม่พอจะสรุปว่า database scale ถูกต้อง ต้องอ่าน log และตรวจความถูกต้องของข้อมูล

**จำภาพเดียวให้ได้:** stateless Pod เหมือนพนักงานที่เปลี่ยนเวรได้ แต่ database คือสมุดบัญชี—เปลี่ยนคนเฝ้าได้ แต่อย่าให้สองคนเขียนเล่มเดียวโดยไม่มีกติกา

🧭 ต่อยอด: LAB 17 จะวาง Ingress เป็นประตูหน้าเดียว แยก `/` ไป web และ `/api` ไป api

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **stateless กับ stateful ต่างกันอย่างไรในทางปฏิบัติ?** — stateless ทิ้ง/สร้าง/scale ได้โดยไม่มีข้อมูลติด Pod; stateful ต้องรักษาดิสก์ เจ้าของข้อมูล ลำดับ และ backup
2. **ทำไม DB scale เป็น 2 แล้วไม่ถือว่าสำเร็จ แม้ทั้งคู่ Ready?** — readiness ตรวจเพียง process ตอบได้ ไม่ยืนยันความปลอดภัยของ concurrent writes; log รอบนี้แสดง recovery และ Pod เดิม restart
3. **ถ้าต้องการ PostgreSQL หลายตัวจริงควรทำอย่างไร?** — ใช้ replication ที่ PostgreSQL รองรับร่วมกับ StatefulSet/PVC แยก หรือ managed database

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] อธิบายบทบาท Secret, PVC และ DB Service ได้
- [ ] เห็นการ์ด WEB/API/DB พร้อมจากหน้าเว็บจริง
- [ ] สร้าง ticket และพิสูจน์ว่ารอดหลังลบ DB Pod แล้ว
- [ ] scale web/api แล้วอธิบายว่าทำไมทำได้ง่ายกว่า DB
- [ ] อ่าน log ของการ scale DB สองตัวและอธิบายความเสี่ยงได้
- [ ] ทำ Secret พัง แก้กลับ และยืนยัน `/info` ปกติแล้ว
- [ ] ทำ Clean Re-run สำเร็จและลบ namespace ปิดท้ายแล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
