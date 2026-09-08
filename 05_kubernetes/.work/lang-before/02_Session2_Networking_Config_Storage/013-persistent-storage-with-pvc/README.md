# LAB 13 — Persistent Storage with PVC : Pod เปลี่ยนได้ แต่ข้อมูลต้องอยู่

> โฟลเดอร์ `013-persistent-storage-with-pvc` = LAB 13 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `01-pvc.yaml` · `02-db.yaml` · `03-secret.yaml` · `04-api.yaml` · `05-web.yaml` · `06-door.yaml`)

> 💡 **แนวคิดหลักของแล็บนี้:** ถ้าอยากให้ข้อมูลอยู่รอด ต้องเก็บไว้ "นอก" container โดยขอพื้นที่ผ่าน PVC

## วัตถุประสงค์ของแล็บ

1. อธิบายได้ว่า PVC เป็น “ใบขอพื้นที่” ไม่ใช่ดิสก์ที่ Pod สร้างเอง
2. อธิบายความสัมพันธ์ระหว่าง PVC, PV และ StorageClass ได้
3. พิสูจน์ได้ว่าการลบ db Pod ไม่ทำให้ข้อมูลที่อยู่บน PV หาย

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ใน Compose เราใช้ named volume `pgdata`; Kubernetes เพิ่มชั้น “การขอ” เพราะ Pod อาจย้ายไปคนละ node ได้

| สิ่งที่เห็น | หน้าที่ |
|---|---|
| PersistentVolumeClaim (PVC) | ระบุขนาดและ access mode ที่ workload ต้องการ |
| PersistentVolume (PV) | พื้นที่จริงที่ cluster จัดให้และผูกกับ claim |
| StorageClass | กติกาที่ provision พื้นที่ให้อัตโนมัติ |
| volumeMount | จุดที่ container มองเห็นพื้นที่นั้น |

| สิ่งที่คุ้นจาก Compose/LAB 12 | สิ่งที่ใช้ใน LAB 13 | อายุข้อมูล |
|---|---|---|
| named volume | PVC ขอ PV ผ่าน StorageClass | แยกจาก Pod และใช้กับ Pod ใหม่ได้ |
| `emptyDir` | `emptyDir` เหมือนเดิม | อยู่ถึงแค่ Pod เดิม |
| path ที่ mount ใน container | `volumeMounts.mountPath` | เป็นทางเข้าพื้นที่ ไม่ใช่ตัวพื้นที่เอง |

`ReadWriteOnce` หมายถึง volume ถูก mount เพื่อเขียนจาก node เดียวในเวลาเดียวกัน ส่วน `PGDATA` ชี้ PostgreSQL ไปยัง subdirectory ใต้ mount เพื่อให้ initdb ทำงานได้แน่นอน

อายุ PVC ยาวกว่า Pod แต่ข้อมูลยังลบได้: StorageClass `standard` ใน kind ใช้ reclaim policy `Delete` จึงลบพื้นที่จริงพร้อม claim

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น PVC เปลี่ยนจาก `Pending` เป็น `Bound` เมื่อมี Pod มาใช้
- จะได้พิสูจน์ด้วย SQL ว่า ticket ยังอยู่หลัง db Pod ถูกสร้างใหม่
- จะได้ตามรอย data directory ไปถึง node ของ kind
- จะได้เห็น finalizer ป้องกัน PVC ที่กำลังถูกใช้งาน

## ภาพรวมของแล็บนี้

1. สร้าง namespace และขอพื้นที่ 1Gi
2. เพิ่ม ticket ผ่าน UI และตรวจจำนวนด้วย SQL
3. ลบ db Pod แล้วตรวจ ticket เดิม
4. จงใจลบ PVC อ่านอาการ และสร้างกลับ

![เส้นทาง web ไปยัง PostgreSQL ซึ่ง mount PVC](../slides_assets/lab013-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า db Pod ชื่อและ IP เปลี่ยน แต่ยัง mount claim ชื่อเดิม ข้อมูลจะตาม Pod ใหม่มาได้หรือไม่?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · `kubectl get nodes` ตรวจ node ทั้งสาม · `crictl images` ตรวจ image ใน kind node

✅ **Expected output** — node ทั้ง 3 เป็น `Ready` และพบ image ครบ 4 รายการ (ตัดบางคอลัมน์); ชื่อ node, AGE, version, hash และขนาดต่างกันได้ ถ้าไม่พบ image ให้ build/load ตาม LAB 001 หรือ README ระดับชุด:

```text
NAME                     STATUS   ROLES           AGE     VERSION
devtools-control-plane   Ready    control-plane   8m18s   v1.36.4
devtools-worker          Ready    <none>          8m7s    v1.36.4
devtools-worker2         Ready    <none>          8m7s    v1.36.4
docker.io/library/k8s-lab-api   v1   c662b53377da4   186MB
docker.io/library/k8s-lab-db    v1   9bb05e9c07722   300MB
docker.io/library/k8s-lab-web   v1   c07ef6ef4b6a3   209MB
docker.io/library/k8s-lab-web   v2   685541d4b6ff0   209MB
…
```

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/013-persistent-storage-with-pvc
```

> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace · `git clone` ดาวน์โหลด repository · `cd` เข้า LAB 13; ถ้ามี repository แล้วให้ใช้ `git pull` ใน repository เดิมแทนการ clone ซ้ำ

✅ **Expected output** — clone เริ่มสำเร็จและ `cd` ไม่แสดง error:

```text
Cloning into 'DevTools'...
```

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-pvc.yaml` | PersistentVolumeClaim | ขอพื้นที่ 1Gi แบบ ReadWriteOnce | [Volume/PVC](../YAML_Guide.md#volume-pvc) |
| `02-db.yaml` | Deployment, Service | mount claim เดิมให้ PostgreSQL; ใช้ Recreate และ readiness exec | [Deployment](../YAML_Guide.md#deployment) · [Volume/PVC](../YAML_Guide.md#volume-pvc) · [Probes](../YAML_Guide.md#probes) |
| `03-secret.yaml` | Secret | รหัสผ่านสมมุติของฐานข้อมูล | [Secret](../YAML_Guide.md#secret) |
| `04-api.yaml` | Deployment, Service | ต่อ API ไป db | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `05-web.yaml` | Deployment, Service | ต่อ web ไป API | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `06-door.yaml` | Ingress | เปิดประตู path `/` | [Ingress](../YAML_Guide.md#ingress) |

ส่วนขอพื้นที่จริงจาก `01-pvc.yaml`:

```yaml
accessModes:
  - ReadWriteOnce
resources:
  requests:
    storage: 1Gi
```

ส่วนอ้าง claim จริงจาก `02-db.yaml`:

```yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: db-data
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `accessModes` | `ReadWriteOnce` (RWO), `ReadOnlyMany` (ROX), `ReadWriteMany` (RWX) | ต้องสัมพันธ์กับ storage backend; ไม่ใช่ Unix permission |
| `requests.storage` | capacity ขั้นต่ำที่ขอ | เพิ่มได้เมื่อ StorageClass/driver รองรับ; ลด claim เดิมไม่ได้ |
| `storageClassName` | เลือกวิธี provision | ไฟล์นี้ไม่ระบุ จึงใช้ default StorageClass ถ้ามี; `""` หมายถึงไม่ใช้ class |
| `claimName` | PVC ใน namespace เดียวกับ Pod | ชื่อผิดทำให้ Pod รอ schedule/mount |

`volumeMounts`, `mountPath` และ `PGDATA` อยู่ใน `02-db.yaml` เช่นกัน แต่เรียนครั้งแรกใน LAB 012 จึงทบทวนที่ [Volume/PVC](../YAML_Guide.md#volume-pvc); ไฟล์เดียวกันใช้ `strategy.type: Recreate` (เรียนครั้งที่ 1; ทบทวน [Deployment](../YAML_Guide.md#deployment)) และ `readinessProbe.exec` ด้วย `pg_isready` (ดู [Probes](../YAML_Guide.md#probes))

**ผิดบ่อยในแล็บนี้:** runlog มี Event จริง `persistentvolumeclaim "db-data" not found` เมื่อลบ claim ที่ workload ยังใช้ Pod จึง `Pending`; ตรวจ `kubectl describe pod` และสถานะ PVC/PV ก่อนคิดว่า image พัง

ดู schema ได้ด้วย `kubectl explain persistentvolumeclaim.spec.accessModes`, `kubectl explain persistentvolumeclaim.spec.resources.requests` และ `kubectl explain persistentvolumeclaim.spec.storageClassName`

## 3. สร้าง namespace และขอพื้นที่

ไฟล์ `01-pvc.yaml` จริงขอพื้นที่ดังนี้:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data
  namespace: lab013
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

> 📝 **คำอธิบาย YAML:** `metadata.name/namespace` ระบุ claim ที่ Pod จะอ้าง · `accessModes: ReadWriteOnce` ให้ mount เพื่อเขียนจาก node เดียวในเวลาเดียวกัน · `resources.requests.storage: 1Gi` คือขนาดที่ขอจาก StorageClass ค่าเริ่มต้น

ส่วน storage ของ `02-db.yaml` จริงเชื่อม PostgreSQL กับ claim ดังนี้:

```yaml
env:
  - name: PGDATA
    value: /var/lib/postgresql/data/pgdata
volumeMounts:
  - name: data
    mountPath: /var/lib/postgresql/data
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: db-data
```

> 📝 **คำอธิบาย YAML:** `PGDATA` แยก data directory เป็น subdirectory ใต้ mount · `volumeMounts.name` จับคู่กับ `volumes.name` · `mountPath` คือ path ที่ container เห็น · `persistentVolumeClaim.claimName` ต้องตรงกับ PVC `db-data`

```bash
kubectl create namespace lab013
kubectl apply -f 01-pvc.yaml
kubectl get pvc,pv,storageclass -n lab013
```
> 📝 **คำอธิบาย:** `create namespace` สร้างห้องของแล็บ · `apply -f` ส่ง desired state จากไฟล์ · `get pvc,pv,storageclass` ดู claim, volume และผู้ provision · `-n lab013` จำกัดผลใน namespace นี้

✅ **Expected output** — claim เริ่ม `Pending` เพราะ StorageClass ใช้ `WaitForFirstConsumer` (ตัดบางคอลัมน์):
```text
namespace/lab013 created
persistentvolumeclaim/db-data created
NAME                            STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
persistentvolumeclaim/db-data   Pending                                      standard
NAME                                             PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE
storageclass.storage.k8s.io/standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer
…
```

## 4. ประกอบระบบครบสามชั้น

```bash
kubectl apply -f 03-secret.yaml -f 02-db.yaml -f 04-api.yaml -f 05-web.yaml -f 06-door.yaml
kubectl wait --for=condition=available deployment/db deployment/api deployment/web -n lab013 --timeout=180s
until curl --retry 0 -s http://localhost/info | jq -e '.api.reachable == true and .db.status == "up"' >/dev/null; do sleep 1; done
kubectl get all,ingress,pvc -n lab013 -o wide
curl -s http://localhost/info | jq -c '{pod,api,db}'
```
> 📝 **คำอธิบาย:** `-f` หลายครั้งเรียง dependency ที่อ่านง่าย · `wait --for=condition=available` รอ Deployment พร้อม · `--timeout=180s` กันการรอไม่จบ · `-o wide` เพิ่ม IP และ node · `curl -s` เรียก Ingress แบบไม่แสดง progress · `/info` คืนหลักฐานชื่อ Pod · `jq` จัด JSON ให้อ่านง่าย

✅ **Expected output** — PVC เป็น `Bound`, Deployment พร้อม และสถานะสามชั้นใช้งานได้ (ตัดบางแถว/บางคอลัมน์):
```text
…
deployment.apps/db condition met
deployment.apps/api condition met
deployment.apps/web condition met
persistentvolumeclaim/db-data   Bound   pvc-861b9218-a5d5-4289-9188-90c8c36f6e9c   1Gi   RWO   standard
{"pod":"web-74bf7d87c4-wfm82","api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-jk7wh"},"db":{"status":"up"}}
```

## 5. เพิ่มข้อมูลผ่านหน้าเว็บ

เปิด `http://localhost:8080/tickets` เลือกครุภัณฑ์หนึ่งรายการ กรอกหัวข้อ
`โปรเจกเตอร์ห้อง 999 ภาพไม่ขึ้น` แล้วกด **แจ้งซ่อม**

![ticket ใหม่และการ์ดสถานะทั้งสามชั้น](images/03-ticket-created.png)

```bash
kubectl exec deployment/db -n lab013 -- psql -U opsuser -d skillspace -c 'select count(*) from tickets'
kubectl exec deployment/db -n lab013 -- psql -U opsuser -d skillspace -c "select id,title,status from tickets order by id desc limit 1"
```
> 📝 **คำอธิบาย:** `exec deployment/db` ให้ kubectl เลือก db Pod · `--` แยก flag ของ kubectl จากคำสั่งใน container · `psql -U` ระบุ user · `-d` ระบุ database · `-c` รัน SQL แล้วออก · `order by id desc limit 1` เลือก ticket ล่าสุด

✅ **Expected output** — count เพิ่มจาก seed 8 เป็น 9 และ ticket ล่าสุดเป็น NEW:
```text
 count
-------
     9
(1 row)

 id |           title           | status
----+---------------------------+--------
  9 | โปรเจกเตอร์ห้อง 999 ภาพไม่ขึ้น | NEW
(1 row)
```

## 6. ลบ db Pod แล้วพิสูจน์ว่า ticket ยังอยู่

```bash
kubectl get pod -n lab013 -l app=db -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName'
kubectl delete pod -n lab013 -l app=db
kubectl wait --for=condition=ready pod -n lab013 -l app=db --timeout=180s
kubectl get pod -n lab013 -l app=db -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName'
kubectl exec deployment/db -n lab013 -- psql -U opsuser -d skillspace -c 'select count(*) from tickets'
kubectl describe pvc db-data -n lab013 | grep -E 'Used By|Finalizers'
```
> 📝 **คำอธิบาย:** `-l app=db` เลือกด้วย label · `custom-columns` แสดงเฉพาะชื่อและ node · `delete pod` ลบ instance แต่ Deployment ยังถือ desired state · `wait condition=ready` รอ readiness ของ PostgreSQL · SQL เดิมใช้เทียบก่อนและหลัง

✅ **Expected output** — ชื่อ Pod เปลี่ยน แต่ count ยังเป็น 9:
```text
NAME                  NODE
db-7979ccf8db-46zp8   devtools-worker2
pod "db-7979ccf8db-46zp8" deleted from lab013 namespace
pod/db-7979ccf8db-d7p49 condition met
NAME                  NODE
db-7979ccf8db-d7p49   devtools-worker2
 count
-------
     9
(1 row)
Finalizers:    [kubernetes.io/pvc-protection]
Used By:       db-7979ccf8db-d7p49
```

![Pod ใหม่ยังอ่าน ticket #9 จาก PVC เดิม](images/04-ticket-survives-pod-delete.png)

## 7. ตามรอย PVC ไปยังพื้นที่จริง

```bash
PV=$(kubectl get pvc db-data -n lab013 -o jsonpath='{.spec.volumeName}')
kubectl describe pv "$PV"
NODE=$(kubectl get pod -n lab013 -l app=db -o jsonpath='{.items[0].spec.nodeName}')
docker exec "$NODE" find /var/local-path-provisioner -maxdepth 2 -type d
```
> 📝 **คำอธิบาย:** `jsonpath` ดึงชื่อ PV และ node โดยไม่ต้องคัดลอก · `describe pv` แสดง claim, affinity และ host path · `docker exec "$NODE"` เข้า kind node ที่ถือ volume · `find -maxdepth 2 -type d` แสดง directory โดยไม่ไล่ลึกเกินจำเป็น

✅ **Expected output** — PV ผูกกับ claim และพบ `pgdata` นอก container ของ db (ตัดบางแถว/ข้อความท้าย):
```text
…
Status:            Bound
Claim:             lab013/db-data
Reclaim Policy:    Delete
Path:              /var/local-path-provisioner/pvc-861b9218-a5d5-4289-9188-90c8c36f6e9c_lab013_db-data
/var/local-path-provisioner/pvc-861b9218-a5d5-4289-9188-90c8c36f6e9c_lab013_db-data/pgdata
```

ชื่อ PV, path และ node ต่างกันได้ และ local path นี้เหมาะกับ kind เพื่อการเรียน ไม่ใช่ storage แบบย้ายข้าม node ใน production

## 8. ทดลองให้พัง — ลบ PVC ที่ฐานข้อมูลกำลังใช้

```bash
kubectl delete pvc db-data -n lab013 --wait=false
kubectl get pvc db-data -n lab013
kubectl delete pod -n lab013 -l app=db
kubectl get pods,pvc -n lab013 -o wide
kubectl describe pod -n lab013 -l app=db
```
> 📝 **คำอธิบาย:** `--wait=false` ส่งคำขอลบแล้วคืน prompt เพื่อให้เห็นช่วง `Terminating` · finalizer `pvc-protection` ชะลอการลบระหว่างมี Pod ใช้ · เมื่อลบ db Pod claim จึงหายจริง · Deployment สร้าง Pod ใหม่แต่ scheduler หา claim ไม่พบ · `describe` เปิด Events ที่อธิบายสาเหตุ

✅ **Expected output** — claim ค้าง Terminating ก่อน แล้ว db Pod ใหม่ Pending (ตัดบางแถว/บางคอลัมน์/ข้อความท้าย):
```text
…
db-data   Terminating   pvc-861b9218-a5d5-4289-9188-90c8c36f6e9c   1Gi   RWO   standard
pod "db-7979ccf8db-d7p49" deleted from lab013 namespace
pod/db-7979ccf8db-fqjx5   0/1   Pending   0   2s
Warning  FailedScheduling  persistentvolumeclaim "db-data" is being deleted. not found
Warning  FailedScheduling  persistentvolumeclaim "db-data" not found. not found
```

```bash
kubectl apply -f 01-pvc.yaml
kubectl rollout status deployment/db -n lab013 --timeout=180s
kubectl exec deployment/db -n lab013 -- psql -U opsuser -d skillspace -c 'select count(*) from tickets'
```
> 📝 **คำอธิบาย:** apply PVC สร้าง claim และ PV ชุดใหม่ให้ Deployment เดิม · `rollout status` รอ db กลับมาพร้อม · SQL ตรวจผลของการลบ storage; Kubernetes สร้างพื้นที่ใหม่ได้แต่กู้ข้อมูลที่ผู้ใช้สั่งลบไม่ได้

✅ **Expected output** — ระบบกลับมา แต่ข้อมูลใหม่หายและเหลือ seed 8:
```text
persistentvolumeclaim/db-data created
deployment "db" successfully rolled out
 count
-------
     8
(1 row)
```

## 9. แบบฝึกหัดสั้น (Exercise)

ปรับ `01-pvc.yaml` ให้ขอ `2Gi` แล้วอธิบายก่อนรันว่า claim เดิมจะขยายได้หรือไม่
เกณฑ์สำเร็จคือผู้เรียนตรวจ `allowVolumeExpansion` ของ StorageClass แล้วอธิบาย error ที่ `kubectl apply` คืนเมื่อ StorageClass ไม่อนุญาตให้ขยาย

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get pods,pvc -n lab013
kubectl exec deployment/db -n lab013 -- psql -U opsuser -d skillspace -c 'select count(*) from tickets'
curl -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** `get pods,pvc` ตรวจ runtime กับ storage · SQL ตรวจข้อมูลโดยตรง · `/info` ตรวจเส้นทางผู้ใช้โดยไม่พึ่ง Event ที่อาจหมดอายุ

✅ **Expected output** — PVC Bound, SQL ตอบ seed 8 หลังทดลองลบ claim, หน้าเว็บรายงาน api reachable และ db up (ตัดบางแถว/บางคอลัมน์):

```text
…
db-data   Bound   pvc-556e598f-86c2-4868-a170-e24196b1d90d   1Gi   RWO   standard
 count
-------
     8
(1 row)
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-c2wzw"},"db":{"status":"up"}}
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| PVC ค้าง Pending ก่อนสร้าง db | `WaitForFirstConsumer` รอ Pod | apply db แล้วดู Events ของ PVC |
| db Pod ยังไม่ Ready | PostgreSQL กำลัง initdb และ readiness ยังไม่ผ่าน | รอ `kubectl rollout status deployment/db` |
| db Pod Pending หลังลบ claim | Deployment อ้าง PVC ที่ไม่มีแล้ว | apply `01-pvc.yaml` และอ่าน Events |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab013
kubectl wait --for=delete namespace/lab013 --timeout=180s
kubectl create namespace lab013
kubectl apply -f 01-pvc.yaml -f 03-secret.yaml -f 02-db.yaml -f 04-api.yaml -f 05-web.yaml -f 06-door.yaml
kubectl wait --for=condition=available deployment/db deployment/api deployment/web -n lab013 --timeout=180s
until curl --retry 0 -s http://localhost/info | jq -e '.api.reachable == true and .db.status == "up"' >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{api,db}'
```
> 📝 **คำอธิบาย:** ลบ namespace เพื่อล้าง object และ volume claim ทั้งห้อง · `wait --for=delete` กัน resource เก่าชนรอบใหม่ · สร้างและ apply จากไฟล์เท่านั้น · รอ Deployment · `/info` พิสูจน์ผลเดิมจากสภาพสะอาด

✅ **Expected output** — รอบใหม่สร้างครบและสามชั้นกลับมาใช้งาน (ตัดบางแถว/ข้อความท้าย):
```text
…
namespace/lab013 created
persistentvolumeclaim/db-data created
deployment.apps/db created
deployment.apps/api created
deployment.apps/web created
{"api":{"configured":true,"reachable":true,"pod":"api-7c94cf584b-jk7wh"},"db":{"status":"up"}}
```

```bash
kubectl delete namespace lab013
kubectl wait --for=delete namespace/lab013 --timeout=180s
kubectl get all -n lab013
```
> 📝 **คำอธิบาย:** ลบ namespace รอบ Clean Re-run · รอให้หายจริง · `get all` ตรวจซ้ำว่า workload และ Service ไม่ค้าง

✅ **Expected output** — namespace ว่าง:
```text
namespace "lab013" deleted
No resources found in lab013 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl apply -f 01-pvc.yaml` | ขอ persistent storage |
| `kubectl get pvc,pv,storageclass` | ดู claim, volume และ provisioner |
| `kubectl exec deployment/db -- psql ...` | ตรวจข้อมูลใน PostgreSQL |
| `kubectl delete pod -l app=db` | บังคับให้ Deployment สร้าง db Pod ใหม่ |

## สรุปสิ่งที่ได้เรียนรู้

Pod เป็นของที่ทิ้งและสร้างใหม่ได้ ส่วนข้อมูลต้องมีวงจรชีวิตแยกจาก Pod

- PVC บอกความต้องการ ส่วน PV คือพื้นที่ที่ตอบคำขอนั้น
- db Pod ใหม่เห็น ticket เดิมเพราะ mount claim และ PV เดิม
- การลบ PVC บน StorageClass นี้ทำให้ PV และข้อมูลถูกลบจริง

**จำภาพเดียวให้ได้:** Pod เปลี่ยนชื่อได้ แต่สาย mount ต้องกลับไปที่ PVC เดิมจึงจะเห็นข้อมูลเดิม

🧭 ต่อยอด: ไปที่ [LAB 14 — Running is not Ready](../014-running-is-not-ready/README.md) เพื่อใช้ readiness ตัด Pod ที่ยังทำงานกับฐานข้อมูลไม่ได้ออกจาก Service

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **PVC คือการขออะไร?** — ขอพื้นที่ตามขนาดและ access mode แล้ว cluster จัด PV มาผูกให้
2. **PVC ต่างจาก emptyDir อย่างไร?** — emptyDir ผูกกับอายุ Pod; PVC เป็น object แยกที่อยู่รอดหลัง Pod หาย
3. **ทำไม db Pod ใหม่เห็น ticket เดิม?** — เพราะ mount claim เดิมซึ่งยัง Bound กับ PV และ directory เดิม

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] PVC `db-data` เป็น Bound
- [ ] เพิ่ม ticket ผ่าน UI และตรวจ SQL ได้ 9 แถว
- [ ] ลบ db Pod แล้ว ticket เดิมยังอยู่
- [ ] อธิบาย PVC, PV และ StorageClass ได้
- [ ] ลบ namespace `lab013` แล้วไม่เหลือ resource

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
