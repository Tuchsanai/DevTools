# LAB 12 — Ephemeral Data : ทำไม Pod ใหม่แล้วข้อมูลหาย

> โฟลเดอร์ `012-why-data-disappears` = LAB 12 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `manifests/01-secret.yaml` ถึง `05-door.yaml`, `02-db-emptydir.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** ข้อมูลที่เขียนไว้ใน container หายเมื่อ Pod เกิดใหม่ เพราะ container ถูกสร้างใหม่จาก image เสมอ

## วัตถุประสงค์ของแล็บ

1. อธิบาย image layer กับ writable layer ของ container ได้
2. พิสูจน์จาก UI และ SQL ว่าข้อมูลใหม่หายหลัง db Pod ถูกสร้างใหม่
3. แยก container restart ออกจาก Pod recreation ด้วย `emptyDir`

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

container เริ่มจาก image แบบอ่านอย่างเดียว แล้วมี writable layer ชั่วคราววางทับ เมื่อ container/Pod ถูกทิ้ง layer นี้ก็ถูกทิ้งด้วย Kubernetes ไม่ได้ทำข้อมูลหายเอง แต่กำลังทำตามโมเดล “ทิ้งแล้วสร้างใหม่จาก image” เหมือน `docker rm` แล้ว `docker run` ใหม่

| ที่เก็บ | อายุข้อมูล | รอด container restart | รอด Pod ใหม่ |
|---|---:|---:|---:|
| writable layer | container | ไม่ | ไม่ |
| `emptyDir` | Pod | ใช่ | ไม่ |
| PVC/PV | นอก Pod | ใช่ | ใช่ (LAB 13) |

## สิ่งที่จะได้เรียนรู้

- จะได้เพิ่ม ticket ผ่านฟอร์มหน้าเว็บจริงจน count จาก 8 เป็น 9
- จะได้ลบ db Pod แล้วเห็น ticket ใหม่หายจากทั้ง UI และ SQL
- จะได้เขียนไฟล์ใน web Pod แล้วพิสูจน์ว่า Pod ใหม่ไม่มีไฟล์นั้น
- จะได้ใช้ `emptyDir` แยกอายุ container ออกจากอายุ Pod
- จะได้เห็น Pod เดิม restart แล้ว count 9 ยังอยู่

## ภาพรวมของแล็บนี้

1. deploy ระบบจากโฟลเดอร์ `manifests/`
2. เพิ่ม ticket/ไฟล์ชั่วคราว แล้ว recreate db/web Pod เพื่อตรวจว่าข้อมูลหาย
3. เปลี่ยน db เป็น `emptyDir`
4. เปรียบเทียบ container restart กับ Pod recreation

![writable layer, emptyDir และอายุของ Pod](../slides_assets/lab012-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้าผู้ใช้บันทึกงานไว้ใน PostgreSQL แล้ว Kubernetes ย้าย Pod ไปตัวใหม่ ข้อมูลที่เขียนใน container จะตามไปด้วยหรือไม่?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน kind runtime

✅ **Expected output** — 3 nodes Ready และพบ image 4 ตัว (ตัดบางคอลัมน์; AGE/hash ต่างกันได้):

```text
devtools-control-plane   Ready   control-plane   17m   v1.36.4
devtools-worker          Ready   <none>          17m   v1.36.4
devtools-worker2         Ready   <none>          17m   v1.36.4
docker.io/library/k8s-lab-api   v1   37b98a526d09b   186MB
docker.io/library/k8s-lab-db    v1   12de2be925d8a   300MB
docker.io/library/k8s-lab-web   v1   f46e8e22f91a6   209MB
docker.io/library/k8s-lab-web   v2   fccf050046905   209MB
…
```

ถ้ายังไม่มี image ให้กลับไป build/load ตาม LAB 001 หรือ README ระดับชุด

## 1. Clone โค้ดแล็บ
```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/012-why-data-disappears
```
> 📝 **คำอธิบาย:** สร้าง workspace · clone repository · เข้า LAB 12 ที่มี manifest ระบบครบและ variant `emptyDir`

✅ **Expected output** — clone เริ่มและ path ตรง:
```text
Cloning into 'DevTools'...
```

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/01-secret.yaml` | Secret | รหัสผ่านสมมุติสำหรับ db/api | [Secret](../YAML_Guide.md#secret) |
| `manifests/02-db.yaml` | Deployment, Service | ฐานข้อมูลที่ยังเก็บใน writable layer | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `manifests/03-api.yaml` | Deployment, Service | API เชื่อม db | [Deployment](../YAML_Guide.md#deployment) · [Secret](../YAML_Guide.md#secret) |
| `manifests/04-web.yaml` | Deployment, Service | web เรียก API ด้วยชื่อ Service | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `manifests/05-door.yaml` | Ingress | เปิดประตูไป web | [Ingress](../YAML_Guide.md#ingress) |
| `02-db-emptydir.yaml` | Deployment | เพิ่ม volume อายุเท่า Pod ให้ db | [Deployment](../YAML_Guide.md#deployment) · [Volume/PVC](../YAML_Guide.md#volume-pvc) |

ส่วนใหม่จริงจาก `02-db-emptydir.yaml`:

```yaml
containers:
  - name: db
    # ... image, ports และ env อื่นอยู่ตรงนี้ในไฟล์จริง
    env:
      - name: PGDATA
        value: /var/lib/postgresql/data/pgdata
    volumeMounts:
      - name: data
        mountPath: /var/lib/postgresql/data
volumes:
  - name: data
    emptyDir: {}
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `volumeMounts[].name` ↔ `volumes[].name` | เชื่อม mount กับแหล่ง volume | ชื่อไม่ตรงแล้ว Pod ถูกปฏิเสธ |
| `mountPath` | ตำแหน่งที่ Container เห็น volume | `PGDATA` ต้องเป็น path นี้หรือ subdirectory ใต้ path ไม่เช่นนั้นข้อมูลจะไม่ได้อยู่ใน volume |
| `emptyDir: {}` | พื้นที่ที่สร้างพร้อม Pod | รอดจาก Container restart แต่หายเมื่อ Pod ถูกแทน |
| `PGDATA` | env ของ PostgreSQL ไม่ใช่ field Kubernetes | เปลี่ยนแล้ว PostgreSQL มอง data directory คนละที่ |

**ผิดบ่อยในแล็บนี้:** อย่าสรุปว่า `emptyDir` ไม่ช่วยอะไร—มันช่วยข้าม Container restart แต่ไม่ข้าม Pod; runlog บันทึก `HTTP/1.1 503 Service Unavailable` ระหว่าง rollout ไปยัง db ชุด `emptyDir` ก่อน Pod ใหม่พร้อม ส่วนชื่อ mount ไม่ตรงมีตัวอย่างข้อความ (ไม่ได้มาจาก runlog) `volumeMounts[0].name: Not found: "data"`

ดู schema ได้ด้วย `kubectl explain deployment.spec.template.spec.volumes.emptyDir` และ `kubectl explain deployment.spec.template.spec.containers.volumeMounts`

## 3. เปิดระบบที่ยังไม่มี persistent storage

โฟลเดอร์ `manifests/` มี Secret, db/api/web Deployment+Service และ Ingress โดย db ไม่มี `volumes` หรือ `volumeMounts` ข้อมูล PostgreSQL จึงอยู่ใน writable layer
```bash
kubectl create namespace lab012
kubectl apply -f manifests/
kubectl wait -n lab012 --for=condition=available deployment/db deployment/api deployment/web --timeout=180s
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -c 'select count(*) from tickets;'
```
> 📝 **คำอธิบาย:** namespace แยกแล็บ · apply ทั้งโฟลเดอร์ตามชื่อไฟล์ · wait ทั้งสาม Deployment · `psql` นับ baseline จาก seed

✅ **Expected output** — ระบบขึ้นครบและเริ่มที่ 8 tickets:
```text
namespace/lab012 created
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
 count
-------
     8
```

ถ้า `psql` ต่อไม่ได้ทันทีระหว่าง PostgreSQL ทำ `initdb` ให้รอ 5–10 วินาทีแล้วรันคำสั่ง `psql` ซ้ำ

## 4. เพิ่มข้อมูลจากหน้าเว็บจริง

เปิด `http://localhost:8080/tickets` ตรวจการ์ดสถานะให้ web/api/db เขียว และจำ baseline NEW = 3, งานไม่ปิด = 6

![กระดานก่อนเพิ่ม ticket มีข้อมูล seed 8 ใบ](images/02-tickets-before-create.png)

ในฟอร์ม “แจ้งซ่อมใหม่” เลือก `A-003`, กรอกหัวข้อ `โปรเจกเตอร์ห้อง 999 ภาพไม่ขึ้น`, ใส่รายละเอียด และกด “แจ้งซ่อม” การทดลองจริงใช้ browser กรอกและกดปุ่ม ไม่ได้ยิง API ข้าม UI

![หลังกดฟอร์ม งานไม่ปิดเพิ่มจาก 6 เป็น 7 และ NEW จาก 3 เป็น 4](images/02-ticket-created.png)

```bash
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -c 'select count(*) from tickets;'
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -c 'select id,title from tickets order by id desc limit 1;'
```
> 📝 **คำอธิบาย:** คำสั่งแรกยืนยันจำนวน · คำสั่งที่สองอ่าน record ล่าสุด · หลักฐาน SQL ป้องกันการสรุปจาก UI เพียงมุมเดียว

✅ **Expected output** — count เป็น 9 และ record ล่าสุดตรงกับฟอร์ม:
```text
 count
-------
     9
 id |           title
----+---------------------------
  9 | โปรเจกเตอร์ห้อง 999 ภาพไม่ขึ้น
(1 row)
```

## 5. เขียนไฟล์ชั่วคราวใน web Pod
```bash
kubectl exec -n lab012 deployment/web -- sh -c 'echo hi > /tmp/note.txt'
kubectl exec -n lab012 deployment/web -- cat /tmp/note.txt
```
> 📝 **คำอธิบาย:** `sh -c` ให้ redirection เกิดข้างใน container · `/tmp` อยู่ใน writable layer · `cat` ยืนยันว่าไฟล์มีอยู่จริงก่อนทำลาย Pod

✅ **Expected output** — อ่านไฟล์ได้:
```text
hi
```

## 6. ลบ db Pod แล้วดูข้อมูลหาย
```bash
kubectl get pods -n lab012 -l app=db -o wide
kubectl delete pod -n lab012 -l app=db
kubectl wait -n lab012 --for=condition=ready pod -l app=db --timeout=120s
kubectl get pods -n lab012 -l app=db -o wide
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -c 'select count(*) from tickets;'
```
> 📝 **คำอธิบาย:** จดชื่อ/IP เดิม · Deployment สร้าง Pod ใหม่หลัง delete · wait รอ container ใหม่ · PostgreSQL init seed ใหม่เพราะ writable layer เดิมหาย

✅ **Expected output** — Pod ใหม่ชื่อ/IP ใหม่และ count กลับเป็น 8; ค่าเหล่านี้ต่างกันได้:
```text
NAME                  READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE   READINESS GATES
db-7cbb4874f6-pcc6r   1/1     Running   0          76s   10.244.2.21   devtools-worker   <none>           <none>
pod "db-7cbb4874f6-pcc6r" deleted from lab012 namespace
pod/db-7cbb4874f6-k2jwp condition met
NAME                  READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE   READINESS GATES
db-7cbb4874f6-k2jwp   1/1     Running   0          4s    10.244.2.24   devtools-worker   <none>           <none>
 count
-------
     8
(1 row)
```

ถ้า Pod ใหม่เป็น Ready แต่ `psql` ยังต่อไม่ได้ ให้รอ 5–10 วินาทีแล้วรัน `psql` ซ้ำ เพราะ LAB 012 ยังไม่ได้สอน readiness probe ของฐานข้อมูล
เพื่อพิสูจน์ไฟล์ web ต้อง recreate web Pod ด้วย เพราะการลบ db ไม่ได้แตะ web:
```bash
kubectl delete pod -n lab012 -l app=web
kubectl wait -n lab012 --for=condition=ready pod -l app=web --timeout=120s
kubectl exec -n lab012 deployment/web -- sh -c 'if [ -f /tmp/note.txt ]; then cat /tmp/note.txt; else echo /tmp/note.txt: No such file; fi'
```
> 📝 **คำอธิบาย:** selector ลบ web Pod ที่มีไฟล์ · Deployment สร้าง Pod ใหม่ · test ตรวจ path เดิมใน writable layer ใหม่

✅ **Expected output** — ไฟล์เดิมไม่ตาม Pod มา:
```text
pod "web-c5f8c4c66-28vnw" deleted from lab012 namespace
pod/web-c5f8c4c66-dsf6p condition met
/tmp/note.txt: No such file
```

![ticket ที่เพิ่มหายและตัวเลขกลับเป็น baseline หลัง Pod ใหม่](images/04-ticket-gone-after-pod-recreate.png)

## 7. เพิ่ม emptyDir เพื่อแยก container restart จาก Pod ใหม่

ส่วนสำคัญของ `02-db-emptydir.yaml`:
```yaml
env:
  - name: PGDATA
    value: /var/lib/postgresql/data/pgdata
volumeMounts:
  - name: data
    mountPath: /var/lib/postgresql/data
volumes:
  - name: data
    emptyDir: {}
```
```bash
kubectl apply -f 02-db-emptydir.yaml
kubectl rollout status -n lab012 deployment/db --timeout=180s
```
> 📝 **คำอธิบาย:** `PGDATA` ใช้ subdirectory ใต้ mount · การเปลี่ยน Pod template สร้าง db Pod ใหม่ · `rollout status` รอการแทนที่ · `emptyDir` ยังอยู่เมื่อ container ใน Pod เดิม restart

✅ **Expected output** — rollout ผ่านและ endpoint มีพอร์ต:
```text
deployment.apps/db configured
deployment "db" successfully rolled out
```
เพิ่ม ticket ผ่านฟอร์มอีกครั้งจน SQL count เป็น 9 แล้วทดสอบ restart process:
```bash
kubectl get pod -n lab012 -l app=db --no-headers -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount
kubectl exec -n lab012 deployment/db -- kill 1
sleep 5
kubectl get pod -n lab012 -l app=db --no-headers -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -c 'select count(*) from tickets;'
```
> 📝 **คำอธิบาย:** `kill 1` จบ PostgreSQL container process · restartPolicy ทำให้ kubelet restart container ใน Pod เดิม · custom columns เทียบชื่อ/RESTARTS · emptyDir เดิมยังถูก mount กลับ

✅ **Expected output** — ชื่อ Pod เดิม, RESTARTS เพิ่ม 0 → 1 และข้อมูล 9 ใบยังอยู่:
```text
db-7c8fd4985d-n8xsw   0
db-7c8fd4985d-n8xsw   1
 count
-------
     9
(1 row)
```

ถ้า `RESTARTS` ยังเป็น 0 หรือ `psql` ต่อไม่ได้ ให้รอ 5–10 วินาทีแล้วรันสองคำสั่งตรวจซ้ำ

ลบ Pod เดิมแล้วตรวจซ้ำ:
```bash
kubectl delete pod -n lab012 -l app=db
kubectl wait -n lab012 --for=condition=ready pod -l app=db --timeout=120s
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -Atc 'select count(*) from tickets'
```
> 📝 **คำอธิบาย:** Pod ใหม่ได้ emptyDir ก้อนใหม่ · `-A/-t` ให้ psql พิมพ์เฉพาะค่า · สิ่งที่อยู่รอด container restart จึงยังหายพร้อม Pod

✅ **Expected output** — ชื่อ Pod เปลี่ยนและ count กลับเป็น 8:
```text
pod "db-7c8fd4985d-n8xsw" deleted from lab012 namespace
pod/db-7c8fd4985d-n64jq condition met
8
```

ถ้า `psql` ต่อไม่ได้หลัง Pod ใหม่ ให้รอ 5–10 วินาทีแล้วรันซ้ำ

## 8. ทดลองให้พัง — Scale db เป็น 0 แล้วกลับเป็น 1

หลังเพิ่ม ticket ทดสอบให้ count เป็น 9:
```bash
kubectl scale -n lab012 deployment/db --replicas=0
kubectl wait -n lab012 --for=delete pod -l app=db --timeout=120s
curl -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** scale 0 ลบ db Pod และ emptyDir · wait รอ Pod หาย · หน้าเว็บยังตอบแต่ API รายงาน DB down

✅ **Expected output** — db หายและผู้ใช้เห็น dependency down (ตัดข้อความท้ายในค่า `error` ด้วย `…`):
```text
deployment.apps/db scaled
pod/db-7c8fd4985d-n64jq condition met
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-wjd77"},"db":{"status":"down","error":"connection failed: connection to server at \"10.96.159.201\", port 5432 failed: Connection refused Is the server running …"}}
```
แก้บริการให้กลับมาทำงาน:
```bash
kubectl scale -n lab012 deployment/db --replicas=1
kubectl wait -n lab012 --for=condition=available deployment/db --timeout=180s
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -Atc 'select count(*) from tickets'
curl -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** scale 1 สร้าง Pod/emptyDir ใหม่ · PostgreSQL init seed · บริการกลับมาได้แต่ข้อมูลที่หายกู้คืนไม่ได้ · วิธีป้องกันจริงคือ PVC ใน LAB 13

✅ **Expected output** — ระบบกลับมาเขียว แต่เหลือ seed 8:
```text
deployment.apps/db scaled
deployment.apps/db condition met
8
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-wjd77"},"db":{"status":"up"}}
```

ถ้า `psql` ต่อไม่ได้หรือ `/info` ยังเป็น db down ให้รอ 5–10 วินาทีแล้วรันสองคำสั่งตรวจซ้ำ

## 9. แบบฝึกหัดสั้น (Exercise)

อธิบายโดยไม่รันคำสั่งว่า log file, user upload และ PostgreSQL data ควรอยู่ใน writable layer, emptyDir หรือ PVC เพราะอะไร เกณฑ์สำเร็จคือเลือกอายุข้อมูลให้ตรงกับความต้องการและบอกผลเมื่อ Pod ถูกย้าย node ได้

## วิธีตรวจสอบผลการทดลอง
```bash
kubectl get all,ingress -n lab012
kubectl logs -n lab012 deployment/db --tail=15
kubectl get events -n lab012 --sort-by=.lastTimestamp | tail -25
```
> 📝 **คำอธิบาย:** `get` ตรวจ state ปัจจุบัน · db log แสดง init/ready · Events แสดง delete/create/restart ตามลำดับเวลา

✅ **Expected output** — db Running, log พร้อมรับ connection และ Events มี Pod เกิดใหม่ (ตัดบางแถว/บางคอลัมน์/ข้อความท้าย):
```text
…
deployment.apps/db   1/1   1   1
database system is ready to accept connections
…
117s   Normal   SuccessfulCreate   replicaset/db-7c8fd4985d   Created pod: db-7c8fd4985d-n8xsw
…
```
Pod, IP, AGE, hash, เวลาและจำนวน restart จากรอบทดลองต่างกันได้

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| psql ต่อไม่ได้ทันทีหลัง Pod Ready | ไม่มี readiness probe ของ db | retry จน log บอก ready |
| restart แล้วข้อมูลยังอยู่ | เป็น container restart ใน Pod เดิม + emptyDir | ตรวจชื่อ Pod และ RESTARTS |
| ลบ Pod แล้วข้อมูลหาย | ยังไม่มี PVC | ทำ LAB 13 |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run
```bash
kubectl delete namespace lab012 --wait=true
kubectl get all -n lab012
kubectl create namespace lab012
kubectl apply -f manifests/
kubectl wait -n lab012 --for=condition=available deployment/db deployment/api deployment/web --timeout=180s
kubectl exec -n lab012 deployment/db -- psql -U opsuser -d skillspace -Atc 'select count(*) from tickets'
until curl --retry 0 -s http://localhost/info | jq -e '.db.status == "up"' >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{api,db}'
kubectl delete namespace lab012 --wait=true
kubectl get all -n lab012
```
> 📝 **คำอธิบาย:** ลบ namespace รอจนสะอาด · สร้างระบบจาก manifest เดิม · ยืนยัน seed และเส้นทาง 3 ชั้น · ลบปิดท้าย

✅ **Expected output** — Clean Re-run ได้ seed 8, DB up และไม่เหลือ resource:
```text
namespace "lab012" deleted
No resources found in lab012 namespace.
namespace/lab012 created
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
8
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-wjd77"},"db":{"status":"up"}}
namespace "lab012" deleted
No resources found in lab012 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl delete pod -l app=db` | บังคับให้ Deployment สร้าง db Pod ใหม่ |
| `kubectl exec ... psql` | ตรวจข้อมูลจากฐานข้อมูลจริง |
| `kubectl exec ... kill 1` | ทำ container restart ใน Pod เดิม |
| `kubectl scale ... --replicas=0/1` | ลบ/สร้าง Pod ตาม desired state |
| `kubectl delete namespace lab012` | ล้างแล็บทั้งห้อง |

## สรุปสิ่งที่ได้เรียนรู้

writable layer อยู่กับ container ส่วน emptyDir อยู่กับ Pod ทั้งคู่ไม่รอด Pod ใหม่ ข้อมูลที่ต้องอยู่ต่อจึงต้องย้ายออกนอก Pod ผ่าน persistent storage

- แยก container restart กับ Pod recreation ได้
- อธิบาย workload แบบ stateful/stateless ได้

**จำภาพเดียวให้ได้:** Pod ใหม่คือกล่องใหม่จาก image เดิม—ของที่เขียนไว้ในกล่องเก่าไม่เดินตามมา

🧭 ต่อยอด: [LAB 13 — Persistent storage ด้วย PVC](../013-persistent-storage-with-pvc/README.md)

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **ทำไมข้อมูลถึงหาย?** — อยู่ใน writable layer/emptyDir ที่ถูกทิ้งพร้อม container หรือ Pod
2. **แอปแบบไหนได้รับผลกระทบ?** — database, upload, queue และงานที่เก็บ state ในตัวเอง
3. **emptyDir ช่วยและไม่ช่วยอะไร?** — รอด container restart/แชร์ใน Pod ได้ แต่ไม่รอด Pod ใหม่

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เพิ่ม ticket ผ่าน UI และเห็น count 9
- [ ] ลบ db Pod แล้วเห็น count กลับ 8
- [ ] เห็น emptyDir รอด container restart
- [ ] เห็น emptyDir หายเมื่อ Pod ใหม่
- [ ] Clean Re-run ผ่านและลบ `lab012` แล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
