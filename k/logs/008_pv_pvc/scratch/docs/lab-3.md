## LAB 10: LAB สุดท้าย: ร้านน้องส้มจำได้แล้ว

**เป้าหมาย:** เปลี่ยน volume ของฐานข้อมูลร้านน้องส้มจาก `emptyDir` (บทที่ 7) เป็น PVC แล้วพิสูจน์ด้วยตัวเลขจาก `/api/stats`, `psql` และหน้าร้านจริงใน browser ว่า **ลบ Pod db, rollout restart db และลบ Deployment db แล้ว apply ใหม่ ออเดอร์ไม่หายและไม่ต้อง restart web** เปิดดูไฟล์ของ postgres บน Node ทดลองสิ่งที่ห้ามทำ (scale db เป็น 2) เพื่อเห็นข้อมูลเสียจริง แล้วใช้ StorageClass แบบ Retain + `ReadWriteOncePod` ป้องกันและกู้ข้อมูล

**ต้องมีก่อน:** LAB 0 (image `som-shop-web:1.2` และ `postgres:17.11-alpine` อยู่บน Node, NodePort 30080 ว่าง, ไม่มี namespace `som-shop` ค้างจากบทที่ 7) และ 3 Node `Ready` (ถ้าเพิ่งทำ LAB 8 ตรวจว่า `docker start` แล้ว)

### 10.1 สถาปัตยกรรมและไฟล์

<p align="center" id="fig-14">
  <img src="images/14-lab10-architecture.png" alt="รูปที่ 14 LAB 10 ภาพรวม som-shop-v4" width="900"><br>
  <em><b>รูปที่ 14</b> LAB10 ภาพรวม som-shop-v4: web Deployment 3 บูธ (NodePort 30080) → Service som-db → db Deployment replicas 1 Recreate → PVC som-db-data (standard 1Gi RWO) → PV บน Node</em>
</p>

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)
   ▼                     ▼                     ▼
Pod som-web-<hash>-a  Pod som-web-<hash>-b  Pod som-web-<hash>-c   (Deployment som-web 3 บูธ แบบบทที่ 7)
   │
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop
                                   ▼
                    Service som-db (ClusterIP, 5432)
                                   ▼
                    Pod som-db-<hash>-x (Deployment som-db, replicas 1, Recreate)
                                   │ volume db-data → persistentVolumeClaim som-db-data
                                   ▼
                    PVC som-db-data (standard, RWO, 1Gi) ══ PV pvc-<uid> (Delete)
                                   ▼
                    โฟลเดอร์ /var/local-path-provisioner/pvc-<uid>_som-shop_som-db-data/pgdata บน Node ที่ db ลง
```

**ตาราง LAB 10** ไฟล์ใน `som-shop-v4/`

| ไฟล์ | เนื้อหา |
|---|---|
| `k8s/00-namespace.yaml` | namespace `som-shop` (Pod Security `warn: restricted`) เหมือนบทที่ 6–7 |
| `k8s/10-db.yaml` | **PVC `som-db-data`** (`standard`, RWO, 1Gi) + Deployment `som-db` (replicas 1, `Recreate`, volume `db-data` → `claimName: som-db-data`, `PGDATA=/var/lib/postgresql/data/pgdata`, uid/gid 70, `fsGroup: 70` ซึ่งไม่มีผลกับ local-path) + Service ClusterIP `som-db` |
| `k8s/20-web.yaml` | Deployment `som-web` 3 บูธ (initContainer `wait-for-db` + `db-seed`, RollingUpdate maxSurge 1/maxUnavailable 0, preStop 5 วินาที) + Service NodePort `som-web` 30080 — เหมือนบทที่ 7 เปลี่ยนแค่ footer `LAB 008` และ change-cause |
| `k8s-retain/sc-retain.yaml` | StorageClass `standard-retain` (local-path, **Retain**, WaitForFirstConsumer) — ขั้น H |
| `k8s-retain/10-db.yaml` | เหมือน `k8s/10-db.yaml` แต่ PVC ใช้ `standard-retain` และ **`ReadWriteOncePod`** — ขั้น H |
| `k8s-retain/pvc-rescue.yaml` | PVC `som-db-data` ที่มี `volumeName: PV_NAME` ใช้กู้ตู้เดิม (แทนค่าด้วย `sed`) — ขั้น H2 |
| `hit.sh` | ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน / นับ ok-err |

> **ข้อควรระวัง:** **ห้าม `kubectl apply -f k8s-retain/`** ทั้งโฟลเดอร์ เพราะ `pvc-rescue.yaml` ยังมีคำว่า `PV_NAME` อยู่ ใช้ทีละไฟล์ตามขั้นที่บอกเท่านั้น ส่วน `k8s/` apply ทั้งโฟลเดอร์ได้

ต่างจากบทที่ 7 จุดเดียวคือ volume `db-data` ของ `som-db`

```yaml
      volumes:
        # ตู้เซฟของร้าน: อ้างใบเบิก (PVC) ด้วยชื่อ — Pod ไม่ต้องรู้ว่าตู้อยู่ที่ไหน
        - name: db-data
          persistentVolumeClaim:
            claimName: som-db-data
```

(บทที่ 7 เป็น `emptyDir: {}`) ส่วน web ไม่เก็บข้อมูลเองจึงไม่ต้องมี volume

### 10.2 ขั้น A: เปิดร้านและสั่งซื้อแรก

<p align="center" id="fig-15">
  <img src="images/15-lab10-first-orders.png" alt="รูปที่ 15 LAB 10 ขั้น A สั่งซื้อแรก" width="900"><br>
  <em><b>รูปที่ 15</b> LAB10 ขั้น A: apply → PVC Bound หลัง Pod db ลงเรือ → สั่งซื้อ 3 ครั้ง → /api/stats orders=3</em>
</p>

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/som-shop-v4
kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml; kubectl -n som-shop get pvc
```

```text
namespace/som-shop created
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db created
NAME          STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Pending                                      standard       <unset>                 0s
```

PVC `Pending` ทันทีหลังสร้าง (WaitForFirstConsumer แบบ LAB 3) รอ db พร้อม

```bash
time kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pvc,pv; kubectl -n som-shop get pod -o wide
```

```text
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out

real	0m8.205s
...
NAME                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/som-db-data   Bound    pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            standard       <unset>                 8s

NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            Delete           Bound    som-shop/som-db-data   standard       <unset>                          5s
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-7b786655f5-tk2bn   1/1     Running   0          8s    10.244.2.15   lab-worker   <none>           <none>
```

db พร้อมใน ~8 วินาที (รวมสร้างตู้) PV เป็น `Delete` ตาม class `standard` เปิดหน้าร้าน

```bash
kubectl apply -f k8s/20-web.yaml; time kubectl -n som-shop rollout status deploy/som-web --timeout=180s; kubectl -n som-shop get deploy,svc,pod -o wide
```

```text
deployment.apps/som-web created
service/som-web created
Waiting for deployment "som-web" rollout to finish: 0 of 3 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m6.044s
...
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                  SELECTOR
deployment.apps/som-db    1/1     1            1           15s   postgres     postgres:17.11-alpine   app=som-db
deployment.apps/som-web   3/3     3            3           7s    web          som-shop-web:1.2        app=som-web

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/som-db    ClusterIP   10.96.185.22   <none>        5432/TCP       15s   app=som-db
service/som-web   NodePort    10.96.94.32    <none>        80:30080/TCP   7s    app=som-web

NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
pod/som-db-7b786655f5-tk2bn    1/1     Running   0          15s   10.244.2.15   lab-worker    <none>           <none>
pod/som-web-7d79d9779f-8c8tt   1/1     Running   0          7s    10.244.2.17   lab-worker    <none>           <none>
pod/som-web-7d79d9779f-dcvkb   1/1     Running   0          7s    10.244.1.4    lab-worker2   <none>           <none>
pod/som-web-7d79d9779f-rthbz   1/1     Running   0          7s    10.244.2.16   lab-worker    <none>           <none>
```

สั่งซื้อ 3 ครั้งด้วย API แล้วดูสถิติ (`/api/stats` ตอบ `<ชื่อ Pod web> <รุ่น> orders=<จำนวน> products=<จำนวน>`)

```bash
curl -s localhost:30080/api/stats; for i in 1 2 3; do curl -s -X POST localhost:30080/api/orders -H "content-type: application/json" -d "{\"product_id\":1,\"qty\":1}"; echo; done; for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
som-web-7d79d9779f-8c8tt 1.2 orders=0 products=6
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":3,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":17}}
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
```

🌐 **browser บนเครื่องนักศึกษา** เปิด `http://localhost:30080` จะเห็นร้านรุ่น 1.2 footer `Next.js + PostgreSQL · Kubernetes LAB 008 · namespace som-shop` และลองกดปุ่ม "สั่งซื้อ" เพิ่มเองได้ (ตัวเลขออเดอร์ของนักศึกษาจะต่างจากเอกสารตามจำนวนที่กด)

<p align="center" id="fig-16">
  <img src="images/screenshots/20261005_1302_lab10pv_01-shop-4-orders.png" alt="รูปที่ 16 ภาพหน้าจอจริง ร้านที่ db ใช้ PVC" width="700"><br>
  <em><b>รูปที่ 16</b> ภาพหน้าจอจริงจากการทดลอง: ร้าน som-shop-v4 ที่ db เก็บข้อมูลใน PVC som-db-data — ออเดอร์ทั้งหมด 4 รายการ (รอบถ่ายภาพสั่งซื้อ 4 ครั้ง) เสิร์ฟโดย Pod som-web-7d79d9779f-55j9n เวอร์ชัน 1.2 หัวเว็บยังเขียน "ReplicaSet + Service" เพราะใช้แอปเดิม</em>
</p>

> **หมายเหตุ:** ภาพหน้าจอจริงในหัวข้อนี้ถ่ายจากรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ ซึ่งสั่งซื้อ 4 รายการ (สินค้า 1, 2, 3, 1) ตัวเลขในภาพจึงเป็น 4 ส่วนผลคำสั่งในเอกสารมาจากรอบหลักที่สั่งซื้อ 3 รายการ

### 10.3 ขั้น B–C: ลบ Pod db และ rollout restart db

<p align="center" id="fig-17">
  <img src="images/16-lab10-delete-pod-db.png" alt="รูปที่ 17 LAB 10 ขั้น B–C ลบ Pod db และ restart" width="900"><br>
  <em><b>รูปที่ 17</b> LAB10 ขั้น B–C: ลบ Pod db และ rollout restart db → Pod ใหม่ใช้ PVC เดิม orders=3 (request แรกหลังลบ Pod อาจได้ 503 หนึ่งครั้ง) ไม่ต้อง rollout restart web แบบบท 007</em>
</p>

**ขั้น B** ทำสิ่งเดียวกับที่ทำให้ร้านบทที่ 7 ลืมทุกอย่าง

```bash
date +%T; kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; date +%T; kubectl -n som-shop get pod -l app=som-db -o wide; for i in 1 2 3 4 5 6; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; sleep 1; done
```

```text
12:47:36
pod "som-db-7b786655f5-tk2bn" deleted from som-shop namespace
deployment "som-db" successfully rolled out
12:47:37
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-7b786655f5-zdw4m   1/1     Running   0          1s    10.244.2.18   lab-worker   <none>           <none>
som-web-7d79d9779f-dcvkb 1.2 db-not-ready
 [503]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
```

- Pod db ใหม่ (`zdw4m`) พร้อมใน ~1 วินาที บน **Node เดิม** (ตาม nodeAffinity ของ PV) และเห็น **`orders=3` เท่าเดิม**
- request แรกได้ `db-not-ready [503]` เพราะ connection เดิมใน pool ของ web ตัวนั้นหลุดไปกับ db ตัวเก่า หลังจากนั้น 200 ทั้งหมด **ไม่ต้อง rollout restart web** (ต่างจากบทที่ 7 ที่ db ใหม่ว่างเปล่าจนต้อง seed ใหม่)

**ขั้น C** rollout restart db (Recreate: ปิดตัวเก่าก่อนเปิดตัวใหม่)

```bash
kubectl -n som-shop rollout restart deploy/som-db; time kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pod -l app=som-db -o wide; sleep 3; for i in 1 2 3 4; do curl -s -m 2 localhost:30080/api/stats; done
```

```text
deployment.apps/som-db restarted
Waiting for deployment "som-db" rollout to finish: 0 out of 1 new replicas have been updated...
...
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out

real	0m1.247s
...
NAME                     READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-bb9948676-hgt7s   1/1     Running   0          1s    10.244.2.19   lab-worker   <none>           <none>
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
```

ReplicaSet ใหม่ (`bb9948676`) Pod ใหม่ แต่ใบเบิกเดิม ออเดอร์ยัง 3

### 10.4 ขั้น D: ลบ Deployment db ทั้งตัวแล้ว apply ใหม่

<p align="center" id="fig-18">
  <img src="images/17-lab10-delete-deploy.png" alt="รูปที่ 18 LAB 10 ขั้น D ลบ Deployment db" width="900"><br>
  <em><b>รูปที่ 18</b> LAB10 ขั้น D: ลบ Deployment som-db ทั้งตัว → PVC ยัง Bound → apply ใหม่ → ต่อตู้เดิม orders=3</em>
</p>

```bash
kubectl -n som-shop delete deploy som-db; kubectl -n som-shop get deploy,pvc; curl -s -m 3 -w " [%{http_code}]\n" localhost:30080/api/stats
```

```text
deployment.apps "som-db" deleted from som-shop namespace
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-web   3/3     3            3           39s

NAME                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/som-db-data   Bound    pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            standard       <unset>                 47s
som-web-7d79d9779f-dcvkb 1.2 db-not-ready
 [503]
```

ไม่มี db แล้ว (ร้าน 503) แต่ **ใบเบิกยัง `Bound` กับตู้เดิม** เพราะ PVC เป็น object แยก ไม่ได้เป็นของ Deployment apply ไฟล์เดิมอีกครั้ง

```bash
kubectl apply -f k8s/10-db.yaml; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; sleep 3; for i in 1 2 3 4; do curl -s -m 2 localhost:30080/api/stats; done
```

```text
persistentvolumeclaim/som-db-data unchanged
deployment.apps/som-db created
service/som-db unchanged
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
```

`persistentvolumeclaim/som-db-data unchanged` — Deployment ใหม่ใช้ใบเบิกเดิม ออเดอร์ 3 กลับมาโดยไม่ต้องทำอะไรกับ web

🌐 refresh browser ที่ `http://localhost:30080` ตัวเลขออเดอร์เท่าเดิม

<p align="center" id="fig-19">
  <img src="images/screenshots/20261005_1303_lab10pv_02-after-db-deploy-deleted-still-4.png" alt="รูปที่ 19 ภาพหน้าจอจริง หลังลบ Deployment db ออเดอร์ยังอยู่" width="700"><br>
  <em><b>รูปที่ 19</b> ภาพหน้าจอจริงจากการทดลอง: ลบ Pod db แล้วต่อด้วยลบ Deployment som-db และ apply k8s/10-db.yaml ใหม่ (PVC som-db-data ยัง Bound — persistentvolumeclaim/som-db-data unchanged) ออเดอร์ยังเป็น 4 โดยไม่ต้อง restart web</em>
</p>

### 10.5 ขั้น E: ดูไฟล์ postgres บน Node

<p align="center" id="fig-20">
  <img src="images/18-lab10-peek-pgdata.png" alt="รูปที่ 20 LAB 10 ขั้น E ดูไฟล์ postgres บน Node" width="900"><br>
  <em><b>รูปที่ 20</b> LAB10 ขั้น E: docker exec &lt;node&gt; ls -ln /var/local-path-provisioner/pvc-…_som-shop_som-db-data/pgdata → ไฟล์ของ postgres uid 70 (PG_VERSION, base)</em>
</p>

```bash
N=$(kubectl -n som-shop get pod -l app=som-db -o jsonpath="{.items[0].spec.nodeName}"); PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath="{.spec.volumeName}"); echo "N=$N PV=$PV"; docker exec $N ls -ln /var/local-path-provisioner/${PV}_som-shop_som-db-data/; docker exec $N ls -ln /var/local-path-provisioner/${PV}_som-shop_som-db-data/pgdata | head -12
```

```text
N=lab-worker PV=pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d
total 4
drwx------ 19 70 70 4096 Oct  5 05:48 pgdata
total 128
-rw------- 1 70 70     3 Oct  5 05:47 PG_VERSION
drwx------ 6 70 70  4096 Oct  5 05:47 base
drwx------ 2 70 70  4096 Oct  5 05:48 global
drwx------ 2 70 70  4096 Oct  5 05:47 pg_commit_ts
drwx------ 2 70 70  4096 Oct  5 05:47 pg_dynshmem
-rw------- 1 70 70  5743 Oct  5 05:47 pg_hba.conf
-rw------- 1 70 70  2640 Oct  5 05:47 pg_ident.conf
drwx------ 4 70 70  4096 Oct  5 05:47 pg_logical
drwx------ 4 70 70  4096 Oct  5 05:47 pg_multixact
drwx------ 2 70 70  4096 Oct  5 05:47 pg_notify
drwx------ 2 70 70  4096 Oct  5 05:47 pg_replslot
```

```bash
kubectl -n som-shop exec deploy/som-db -- id; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c "select count(*) from orders"
```

```text
uid=70(postgres) gid=70(postgres) groups=70(postgres)
 count 
-------
     3
(1 row)
```

ในโฟลเดอร์ของตู้มีแค่ `pgdata` (ตาม `PGDATA`) ซึ่ง postgres (uid 70) สร้างเองเป็น `drwx------ 70 70` ไฟล์ทุกไฟล์เป็นของ uid 70 นี่คือ "สมุดออเดอร์" ตัวจริงที่อยู่บน Node และอยู่รอดทุกครั้งที่ Pod เปลี่ยน

### 10.6 ขั้น F (ทดลองอันตราย): scale db เป็น 2

<p align="center" id="fig-21">
  <img src="images/19-lab10-scale-two.png" alt="รูปที่ 21 LAB 10 ขั้น F scale db เป็น 2" width="900"><br>
  <em><b>รูปที่ 21</b> LAB10 ขั้น F: scale db เป็น 2 → ทั้งคู่ลง Node เดียว (RWO) Running/Ready ทั้งคู่ → postgres ตัวที่ 2 recovery บนโฟลเดอร์เดียวกัน → psql ผ่าน Service ได้ orders 3 กับ 6 สลับกัน</em>
</p>

> **⚠️ คำเตือน:** ขั้นนี้ **ตั้งใจทำให้ข้อมูลเสียจริง** เพื่อให้เห็นว่าทำไม db บน Deployment ต้องเป็น 1 ตัว ทำหลังขั้น E เท่านั้น และ **ต้องทำขั้น G ต่อทันทีหลังจบ** เพื่อเริ่มฐานข้อมูลใหม่ ห้ามทำแบบนี้กับระบบจริง

ผลของขั้นนี้ **ไม่แน่นอนในแต่ละเครื่อง แต่เสียหายทุกครั้ง** การทดลองจริงพบได้สามแบบ

| แบบ | อาการหลัง scale กลับเป็น 1 | พบเมื่อ |
|---|---|---|
| 1 | ราว 1 นาทีต่อมา postgres ตัวที่เหลือหยุดเอง (`lock file is invalid`) แล้ว restart **ออเดอร์หาย 6 → 3** | รอบหลักของ LAB |
| 2 | เหมือนแบบ 1 แต่ Pod ขึ้น `Completed` → **`CrashLoopBackOff` ชั่วครู่** (~10–24 วินาที) แล้ว `Running` เอง ออเดอร์ 6 → 3 | รอบทดลองซ้ำ 2 รอบ |
| 3 | postgres เริ่มไม่ได้อีกเลย log มี **`PANIC: could not locate a valid checkpoint record`** และค้าง `CrashLoopBackOff` ร้านขึ้น `db-not-ready` | การตรวจสอบก่อนเขียนบท (pre-check) |

**ขั้นที่ F1** scale เป็น 2 แล้วดูว่า Pod ลงที่ไหน

```bash
kubectl -n som-shop scale deploy/som-db --replicas=2; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pod -l app=som-db -o wide
```

```text
deployment.apps/som-db scaled
Waiting for deployment "som-db" rollout to finish: 1 of 2 updated replicas are available...
deployment "som-db" successfully rolled out
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-7b786655f5-mkhsg   1/1     Running   0          4s    10.244.2.21   lab-worker   <none>           <none>
som-db-7b786655f5-phtbj   1/1     Running   0          14s   10.244.2.20   lab-worker   <none>           <none>
```

ไม่มีอะไรห้าม ทั้งคู่ `Running 1/1` บน **Node เดียวกัน** (PVC เป็น RWO ซึ่งกันแค่ต่าง Node) ดู log ของทั้งสองตัว

```bash
for p in $(kubectl -n som-shop get pod -l app=som-db -o name); do echo "== $p"; kubectl -n som-shop logs $p --tail=6; done
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db -o jsonpath="{range .items[*].endpoints[*]}{.addresses[0]} ready={.conditions.ready} {.targetRef.name}{\"\n\"}{end}"
```

```text
== pod/som-db-7b786655f5-mkhsg
2026-10-05 05:48:11.148 UTC [26] LOG:  database system was not properly shut down; automatic recovery in progress
2026-10-05 05:48:11.153 UTC [26] LOG:  invalid record length at 0/1960848: expected at least 24, got 0
2026-10-05 05:48:11.153 UTC [26] LOG:  redo is not required
2026-10-05 05:48:11.163 UTC [24] LOG:  checkpoint starting: end-of-recovery immediate wait
2026-10-05 05:48:11.187 UTC [24] LOG:  checkpoint complete: wrote 3 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.008 s, sync=0.004 s, total=0.027 s; sync files=2, longest=0.003 s, average=0.002 s; distance=0 kB, estimate=0 kB; lsn=0/1960848, redo lsn=0/1960848
2026-10-05 05:48:11.192 UTC [1] LOG:  database system is ready to accept connections
== pod/som-db-7b786655f5-phtbj
2026-10-05 05:48:00.265 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-10-05 05:48:00.265 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-10-05 05:48:00.272 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-10-05 05:48:00.314 UTC [26] LOG:  database system was shut down at 2026-10-05 05:47:59 UTC
2026-10-05 05:48:00.314 UTC [27] FATAL:  the database system is starting up
2026-10-05 05:48:00.320 UTC [1] LOG:  database system is ready to accept connections
10.244.2.20 ready=true som-db-7b786655f5-phtbj
10.244.2.21 ready=true som-db-7b786655f5-mkhsg
```

ตัวที่ 2 (`mkhsg`) เปิดโฟลเดอร์ที่ตัวแรกยังใช้อยู่ คิดว่าเครื่องดับกะทันหัน (`not properly shut down; automatic recovery in progress`) แล้วทำ checkpoint ของตัวเอง ทั้งคู่ ready และอยู่ใน EndpointSlice ของ Service `som-db` (postgres กันการเปิดซ้ำด้วยไฟล์ล็อก `postmaster.pid` และการตรวจ process แต่สอง container อยู่คนละ PID/IPC namespace จึงมองไม่เห็นกัน)

**ขั้นที่ F2** สั่งซื้อแล้วถามฐานข้อมูลทั้งสองตัว

```bash
for i in 1 2 3; do curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H "content-type: application/json" -d "{\"product_id\":2,\"qty\":1}"; done; echo; for i in 1 2 3 4 5 6; do curl -s localhost:30080/api/stats; done
for p in $(kubectl -n som-shop get pod -l app=som-db -o name); do echo "$p orders=$(kubectl -n som-shop exec $p -- psql -U som -d catshop -tAc "select count(*) from orders")"; done
```

```text
201 201 201 
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-rthbz 1.2 orders=6 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-dcvkb 1.2 orders=6 products=6
som-web-7d79d9779f-rthbz 1.2 orders=6 products=6
pod/som-db-7b786655f5-mkhsg orders=3
pod/som-db-7b786655f5-phtbj orders=6
```

หน้าเว็บเห็น `orders=6` (connection pool ของ web ยังต่อกับตัวแรก) แต่ถามตรงที่ Pod ได้ **6 กับ 3** — ฐานข้อมูลสองตัวบนโฟลเดอร์เดียวกันเห็นข้อมูลไม่ตรงกัน ถามผ่าน Service (connection ใหม่ทุกครั้ง)

```bash
P=$(kubectl -n som-shop get pod -l app=som-db -o name | head -1); for i in 1 2 3 4 5 6 7 8; do kubectl -n som-shop exec $P -- env PGPASSWORD=meow1234 psql -h som-db -U som -d catshop -tAc "select inet_server_addr(), count(*) from orders"; done
```

```text
10.244.2.20|6
10.244.2.20|6
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
10.244.2.21|3
```

Service สุ่มส่งไปทั้งสองตัว ลูกค้าคนใหม่ (หรือ web ที่ต่อใหม่) อาจได้ข้อมูลชุดไหนก็ได้

<p align="center" id="fig-22">
  <img src="images/20-lab10-corruption.png" alt="รูปที่ 22 LAB 10 ขั้น F ผล: ข้อมูลเสีย" width="900"><br>
  <em><b>รูปที่ 22</b> LAB10 ขั้น F (ผล): scale กลับ 1 → ราว 1 นาทีต่อมา postgres ตัวที่เหลือหยุดเอง ("lock file is invalid") แล้ว restart ออเดอร์หาย 6 → 3 มี CrashLoopBackOff ชั่วครู่ (บางเครื่องอาจพังเป็น PANIC)</em>
</p>

**ขั้นที่ F3** scale กลับเป็น 1 แล้ว **รอดูอย่างน้อย 1 นาที** (คำสั่งเฝ้าดู 15 รอบ × 6 วินาที)

```bash
kubectl -n som-shop scale deploy/som-db --replicas=1; for i in $(seq 1 15); do sleep 6; echo "--- $(date +%T) $(kubectl -n som-shop get pod -l app=som-db --no-headers | tr -s " " | tr "\n" ";")"; done
```

```text
deployment.apps/som-db scaled
--- 12:48:31 som-db-7b786655f5-phtbj 1/1 Running 0 33s;
--- 12:48:38 som-db-7b786655f5-phtbj 1/1 Running 0 39s;
--- 12:48:44 som-db-7b786655f5-phtbj 1/1 Running 0 45s;
--- 12:48:50 som-db-7b786655f5-phtbj 1/1 Running 0 51s;
--- 12:48:56 som-db-7b786655f5-phtbj 1/1 Running 0 57s;
--- 12:49:02 som-db-7b786655f5-phtbj 1/1 Running 1 (2s ago) 63s;
--- 12:49:08 som-db-7b786655f5-phtbj 1/1 Running 1 (8s ago) 69s;
...
--- 12:49:56 som-db-7b786655f5-phtbj 1/1 Running 1 (56s ago) 117s;
```

ReplicaSet ลบตัวใหม่กว่า (`mkhsg`) เหลือ `phtbj` ซึ่งดูปกติอยู่ราว 35 วินาที แล้ว `RESTARTS` กลายเป็น 1 ดู log ของ container ก่อน restart และหลัง restart

```bash
P=$(kubectl -n som-shop get pod -l app=som-db -o name); kubectl -n som-shop logs $P --previous --tail=8; echo ---; kubectl -n som-shop logs $P --tail=8; kubectl -n som-shop get $P -o jsonpath="{.status.containerStatuses[0].lastState}{\"\n\"}"
```

```text
2026-10-05 05:48:00.314 UTC [26] LOG:  database system was shut down at 2026-10-05 05:47:59 UTC
2026-10-05 05:48:00.314 UTC [27] FATAL:  the database system is starting up
2026-10-05 05:48:00.320 UTC [1] LOG:  database system is ready to accept connections
2026-10-05 05:49:00.010 UTC [1] LOG:  could not open file "postmaster.pid": No such file or directory
2026-10-05 05:49:00.010 UTC [1] LOG:  performing immediate shutdown because data directory lock file is invalid
2026-10-05 05:49:00.010 UTC [1] LOG:  received immediate shutdown request
2026-10-05 05:49:00.010 UTC [1] LOG:  could not open file "postmaster.pid": No such file or directory
2026-10-05 05:49:00.013 UTC [1] LOG:  database system is shut down
---

2026-10-05 05:49:01.022 UTC [1] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
2026-10-05 05:49:01.022 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-10-05 05:49:01.022 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-10-05 05:49:01.028 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-10-05 05:49:01.037 UTC [26] LOG:  database system was shut down at 2026-10-05 05:48:26 UTC
2026-10-05 05:49:01.037 UTC [27] FATAL:  the database system is starting up
2026-10-05 05:49:01.043 UTC [1] LOG:  database system is ready to accept connections
{"terminated":{"containerID":"containerd://3e73bfeab6f490cca285b1dd901a3ef80e6eb5812dbd46ceebcf4fa395e394aa","exitCode":0,"finishedAt":"2026-10-05T05:49:00Z","reason":"Completed","startedAt":"2026-10-05T05:48:00Z"}}
```

- ตอน scale ลง postgres ตัวที่ 2 ถูกปิดอย่างสุภาพและลบไฟล์ล็อก `postmaster.pid` ซึ่งเป็นไฟล์เดียวกับของตัวแรก ตัวแรกตรวจไฟล์นี้ทุกนาที (ที่วินาที `:00` ของนาทีถัดไป) จึงพบว่าหายไป แล้ว **หยุดตัวเองทันที** (`performing immediate shutdown because data directory lock file is invalid`, `exitCode 0 reason Completed`)
- kubelet เริ่ม container ใหม่ (`restartPolicy: Always`) postgres อ่านสภาพจากดิสก์ที่ตัวที่ 2 ปิดไว้ตอน `05:48:26` (`database system was shut down at 2026-10-05 05:48:26 UTC`) — สภาพที่ไม่มีออเดอร์ 3 รายการหลัง

```bash
kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -tAc "select count(*) from orders"; for i in 1 2 3 4; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; sleep 1; done
```

```text
3
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-rthbz 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-dcvkb 1.2 orders=3 products=6
 [200]
som-web-7d79d9779f-8c8tt 1.2 orders=3 products=6
 [200]
```

**ออเดอร์ 3 รายการที่ลูกค้าได้คำตอบ `201` ไปแล้วหายไป (6 → 3)** โดยไม่มี error ใดเตือนลูกค้าเลย

**ถ้าเห็นแบบ 2 (CrashLoopBackOff ชั่วครู่)** — ผลจริงจากรอบทดลองซ้ำ (Pod เดิม restart มาแล้วจึงมี back-off สะสม)

```text
--- 12:50:58 som-db-7b786655f5-phtbj 1/1 Running 1 (118s ago) 2m59s;
--- 12:51:04 som-db-7b786655f5-phtbj 0/1 Completed 1 (2m4s ago) 3m5s;
--- 12:51:10 som-db-7b786655f5-phtbj 0/1 CrashLoopBackOff 1 (9s ago) 3m11s;
--- 12:51:16 som-db-7b786655f5-phtbj 1/1 Running 2 (15s ago) 3m17s;
```

ไม่ต้องทำอะไร รอให้ `Running` เอง (ช่วงนั้นร้านขึ้น `db-not-ready`) แล้วตรวจจำนวนออเดอร์ด้วยคำสั่ง `psql` ด้านบน รอบทดลองซ้ำได้ `3` เช่นกัน

**ถ้าเห็นแบบ 3 (PANIC)** — `kubectl -n som-shop logs deploy/som-db` มี `PANIC: could not locate a valid checkpoint record` และ Pod ค้าง `CrashLoopBackOff` เกิน 2–3 นาที ฐานข้อมูลในตู้นี้เสียจนเปิดไม่ได้ **ไปขั้น G ทันที** (ขั้น G ลบใบเบิกและเริ่มฐานข้อมูลใหม่ จึงใช้กู้ได้ทุกแบบ)

### 10.7 ขั้น G: ลบใบเบิก = ข้อมูลหายจริง

<p align="center" id="fig-23">
  <img src="images/21-lab10-delete-pvc.png" alt="รูปที่ 23 LAB 10 ขั้น G ลบ PVC" width="900"><br>
  <em><b>รูปที่ 23</b> LAB10 ขั้น G: ลบ Deployment db + PVC → PV (Delete) ถูกลบพร้อมโฟลเดอร์ → apply ใหม่ได้ db ว่าง → rollout restart web เพื่อ seed → orders=0</em>
</p>

เริ่มฐานข้อมูลใหม่หลังขั้น F และดูว่าการลบ PVC ที่ reclaimPolicy เป็น `Delete` ทำอะไร

```bash
PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); echo "PV=$PV N=$N"; kubectl -n som-shop delete deploy som-db; time kubectl -n som-shop delete pvc som-db-data; kubectl get pv; sleep 4; kubectl get pv; docker exec $N ls /var/local-path-provisioner/
```

```text
PV=pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d N=lab-worker
deployment.apps "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace

real	0m0.949s
...
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d   1Gi        RWO            Delete           Released   som-shop/som-db-data   standard       <unset>                          6m49s
No resources found
```

ต้องลบ Deployment ก่อน (ไม่อย่างนั้น PVC ค้าง `Terminating` เพราะ Pod db ยังใช้อยู่) PV `Released` ชั่วครู่แล้วหายภายใน 4 วินาที คำสั่ง `ls` สุดท้ายไม่แสดงอะไร **โฟลเดอร์ `pgdata` บน Node ถูกลบแล้ว** apply db ใหม่

```bash
kubectl apply -f k8s/10-db.yaml; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; sleep 5; for i in 1 2 3; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; done; curl -s -o /dev/null -w "หน้าแรก %{http_code}\n" localhost:30080/
```

```text
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db unchanged
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
som-web-7d79d9779f-rthbz 1.2 db-not-ready
 [503]
som-web-7d79d9779f-rthbz 1.2 db-not-ready
 [503]
som-web-7d79d9779f-8c8tt 1.2 db-not-ready
 [503]
หน้าแรก 503
```

`persistentvolumeclaim/som-db-data created` (ไม่ใช่ `unchanged`) = ใบเบิกใหม่ ตู้ใหม่ว่างเปล่า ไม่มีตาราง ร้านเป็น 503 แบบเดียวกับบทที่ 7

🌐 browser จะเห็นหน้า "ร้านกำลังเตรียมสินค้า"

<p align="center" id="fig-24">
  <img src="images/screenshots/20261005_1304_lab10pv_03-pvc-deleted-503.png" alt="รูปที่ 24 ภาพหน้าจอจริง ลบ PVC แล้ว 503" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: ลบ PVC som-db-data → PV เป็น Released แล้วถูกลบเพราะ reclaimPolicy Delete → apply ใหม่ได้ PVC/PV ใหม่ที่ว่างเปล่า หน้าร้านขึ้น "ร้านกำลังเตรียมสินค้า" (HTTP 503, db-not-ready)</em>
</p>

เติมตารางและสินค้าด้วย initContainer `db-seed` ของ web (วิธีเดียวกับบทที่ 7)

```bash
kubectl -n som-shop rollout restart deploy/som-web; time kubectl -n som-shop rollout status deploy/som-web --timeout=180s; for i in 1 2 3; do curl -s localhost:30080/api/stats; done; kubectl -n som-shop get pvc
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out

real	0m18.351s
...
som-web-7fdc4fd7cb-psq5x 1.2 orders=0 products=6
som-web-7fdc4fd7cb-tn9mg 1.2 orders=0 products=6
som-web-7fdc4fd7cb-psq5x 1.2 orders=0 products=6
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Bound    pvc-70baae7e-16d6-473f-a19f-d993a143a34b   1Gi        RWO            standard       <unset>                 33s
```

ร้านกลับมาขายได้ แต่ **`orders=0`** และ PV เป็นชื่อใหม่ (`pvc-70ba…`) **ลบใบเบิกที่เป็น Delete = ทิ้งข้อมูลจริง**

<p align="center" id="fig-25">
  <img src="images/screenshots/20261005_1305_lab10pv_04-new-pvc-0-orders.png" alt="รูปที่ 25 ภาพหน้าจอจริง PVC ใหม่ ออเดอร์ 0" width="700"><br>
  <em><b>รูปที่ 25</b> ภาพหน้าจอจริงจากการทดลอง: หลัง rollout restart deploy/som-web ให้ db-seed เติมสินค้าใหม่ ร้านกลับมาขายได้ด้วย Pod web ชุดใหม่ (som-web-5564dcc7dd-…) แต่ออเดอร์เป็น 0 เพราะเป็นตู้ใหม่</em>
</p>

### 10.8 ขั้น H: Retain + ReadWriteOncePod

<p align="center" id="fig-26">
  <img src="images/22-lab10-retain-rwop.png" alt="รูปที่ 26 LAB 10 ขั้น H Retain + RWOP" width="900"><br>
  <em><b>รูปที่ 26</b> LAB10 ขั้น H: StorageClass standard-retain + PVC ReadWriteOncePod → orders=2 → scale db 2 → Pod ที่ 2 Pending (ReadWriteOncePod already in-use) ปลอดภัย</em>
</p>

ทำ db ให้ปลอดภัยขึ้นสองเรื่อง: ตู้ไม่ถูกบดเมื่อลบใบเบิก (`Retain`) และระบบไม่ยอมให้ Pod ที่ 2 ใช้ตู้ (`ReadWriteOncePod`) spec ของ PVC ที่มีอยู่แก้ class/โหมดไม่ได้ จึงลบชุดเดิมแล้วสร้างใหม่

```bash
kubectl -n som-shop delete deploy som-db; kubectl -n som-shop delete pvc som-db-data; kubectl apply -f k8s-retain/sc-retain.yaml -f k8s-retain/10-db.yaml; kubectl get sc; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pvc; kubectl get pv
```

```text
deployment.apps "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace
storageclass.storage.k8s.io/standard-retain created
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
service/som-db unchanged
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  21m
standard-retain      rancher.io/local-path   Retain          WaitForFirstConsumer   false                  0s
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Bound    pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           standard-retain   <unset>                 8s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Bound    som-shop/som-db-data   standard-retain   <unset>                          5s
```

PVC `RWOP` class `standard-retain` PV เป็น `Retain` (ในรอบนี้ db ลง `lab-worker2` Node ของนักศึกษาอาจต่าง) db ใหม่ว่าง จึง seed ด้วย rollout restart web แล้วสั่งซื้อ 2 รายการ

```bash
kubectl -n som-shop rollout restart deploy/som-web; kubectl -n som-shop rollout status deploy/som-web --timeout=180s >/dev/null; for i in 1 2; do curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H "content-type: application/json" -d "{\"product_id\":5,\"qty\":1}"; done; echo; for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
deployment.apps/som-web restarted
201 201 
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
som-web-69c6c4b4c6-w7fh2 1.2 orders=2 products=6
```

ลองความผิดพลาดเดิมของขั้น F

```bash
kubectl -n som-shop scale deploy/som-db --replicas=2; sleep 10; kubectl -n som-shop get pod -l app=som-db -o wide; P=$(kubectl -n som-shop get pod -l app=som-db --field-selector=status.phase=Pending -o name); kubectl -n som-shop describe $P | sed -n "/Events:/,\$p"; kubectl -n som-shop get deploy som-db
```

```text
deployment.apps/som-db scaled
NAME                      READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
som-db-7b786655f5-cmcz8   0/1     Pending   0          10s   <none>       <none>        <none>           <none>
som-db-7b786655f5-n6bzl   1/1     Running   0          37s   10.244.1.7   lab-worker2   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  10s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
NAME     READY   UP-TO-DATE   AVAILABLE   AGE
som-db   1/2     2            1           37s
```

Pod ที่ 2 ค้าง `Pending` (`ReadWriteOncePod access mode already in-use`) postgres ตัวที่ 2 ไม่เคยได้เปิดโฟลเดอร์ scale กลับ

```bash
kubectl -n som-shop scale deploy/som-db --replicas=1; sleep 3; kubectl -n som-shop get pod -l app=som-db; for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
deployment.apps/som-db scaled
NAME                      READY   STATUS    RESTARTS   AGE
som-db-7b786655f5-n6bzl   1/1     Running   0          40s
som-web-69c6c4b4c6-w7fh2 1.2 orders=2 products=6
som-web-69c6c4b4c6-c86ph 1.2 orders=2 products=6
som-web-69c6c4b4c6-w7fh2 1.2 orders=2 products=6
```

ReplicaSet ลบ Pod ที่ Pending ทิ้ง ร้านปกติ `orders=2` ไม่มีอะไรเสียหาย (`k8s-retain/10-db.yaml` ยังเป็น `Recreate` เพราะ RWOP + RollingUpdate จะทำให้ rollout ค้าง — ทฤษฎีหัวข้อ 14.2)

### 10.9 ขั้น H2: ลบใบเบิกแล้วกู้ตู้ที่ Retain

<p align="center" id="fig-27">
  <img src="images/23-lab10-rescue-retained.png" alt="รูปที่ 27 LAB 10 ขั้น H2 กู้ตู้ที่ Retain" width="900"><br>
  <em><b>รูปที่ 27</b> LAB10 ขั้น H (ต่อ): ลบ PVC → PV Released ข้อมูลยังอยู่ → ลบ claimRef → PVC ใหม่ volumeName → Bound → orders=2 กลับมา</em>
</p>

จำลองการ "ลบใบเบิกพลาด" แล้วกู้ด้วยขั้นตอนเดียวกับ LAB 6

```bash
curl -s localhost:30080/api/stats; kubectl -n som-shop delete deploy som-db; kubectl -n som-shop delete pvc som-db-data; sleep 3; PV=$(kubectl get pv -o jsonpath="{.items[?(@.status.phase==\"Released\")].metadata.name}"); echo PV=$PV; kubectl get pv $PV; kubectl patch pv $PV --type json -p "[{\"op\":\"remove\",\"path\":\"/spec/claimRef\"}]"; kubectl get pv $PV
```

```text
som-web-69c6c4b4c6-c86ph 1.2 orders=2 products=6
deployment.apps "som-db" deleted from som-shop namespace
persistentvolumeclaim "som-db-data" deleted from som-shop namespace
PV=pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Released   som-shop/som-db-data   standard-retain   <unset>                          78s
persistentvolume/pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Available           standard-retain   <unset>                          78s
```

ตู้ `Retain` เหลือ `Released` (ช่วงนี้ร้านเป็น `db-not-ready [503]`) ลบ `claimRef` แล้วเป็น `Available` ต่อไปสร้างใบเบิกที่ชี้ตู้นี้ และเปิด db **เฉพาะ Deployment** ด้วย `-l app=som-db`

```bash
PV=$(kubectl get pv -o jsonpath="{.items[?(@.status.phase==\"Available\")].metadata.name}"); sed "s/PV_NAME/$PV/" k8s-retain/pvc-rescue.yaml | kubectl apply -f -; kubectl apply -f k8s-retain/10-db.yaml -l app=som-db; echo "exit=$?"; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop get pvc; kubectl get pv; sleep 3; for i in 1 2 3 4; do curl -s -m 2 -w " [%{http_code}]\n" -o >(cat) localhost:30080/api/stats; sleep 1; done
```

```text
persistentvolumeclaim/som-db-data created
deployment.apps/som-db created
exit=0
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
som-db-data   Bound    pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           standard-retain   <unset>                 1s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Bound    som-shop/som-db-data   standard-retain   <unset>                          80s
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
 [200]
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
 [200]
som-web-69c6c4b4c6-c86ph 1.2 orders=2 products=6
 [200]
som-web-69c6c4b4c6-rfl45 1.2 orders=2 products=6
 [200]
```

ได้ **ตู้เดิม** (`pvc-80ce…`) และ **`orders=2` กลับมาทันที โดยไม่ต้อง restart web** (ตารางและออเดอร์อยู่ในตู้)

> **ทำไมต้อง `-l app=som-db`:** ถ้า apply `k8s-retain/10-db.yaml` ทั้งไฟล์หลัง `pvc-rescue.yaml` kubectl จะพยายามแก้ PVC `som-db-data` ให้ตรงกับไฟล์ (ซึ่งไม่มี `volumeName`) ผลจริงในการทดลองคือ
>
> ```text
> The PersistentVolumeClaim "som-db-data" is invalid: spec: Forbidden: spec is immutable after creation except resources.requests and volumeAttributesClassName for bound claims
> @@ -9,7 +9,7 @@
> ...
> - "VolumeName": "pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38",
> + "VolumeName": "",
> ...
> exit=1
> ```
>
> (Deployment ถูกสร้างได้แต่คำสั่งจบด้วย exit 1) `-l app=som-db` เลือกเฉพาะ object ที่มี label นี้ซึ่งคือ Deployment `som-db` จึงไม่แตะ PVC (วิธีนี้เขียนไว้ในคอมเมนต์ของ `pvc-rescue.yaml` ด้วย)

### 10.10 ขั้น I: เก็บกวาด LAB 10

```bash
PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); echo "PV=$PV N=$N"; time kubectl delete ns som-shop; kubectl get pv; docker exec $N ls /var/local-path-provisioner/
```

```text
PV=pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38 N=lab-worker2
namespace "som-shop" deleted

real	0m32.585s
...
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                  STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38   1Gi        RWOP           Retain           Released   som-shop/som-db-data   standard-retain   <unset>                          2m6s
pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38_som-shop_som-db-data
```

ลบ namespace ราว 30 วินาที (Pod web มี preStop และ grace period) แต่ **PV ที่ Retain ไม่อยู่ใน namespace จึงยังอยู่** พร้อมโฟลเดอร์ ลบ PV, โฟลเดอร์ และ StorageClass เอง

```bash
PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); kubectl delete pv $PV; docker exec $N rm -rf /var/local-path-provisioner/${PV}_som-shop_som-db-data; docker exec $N ls /var/local-path-provisioner/; kubectl delete sc standard-retain; kubectl get sc,pv; kubectl get ns
```

```text
persistentvolume "pvc-80ce1972-e685-4c0c-84fb-fef1cd3b8c38" deleted
storageclass.storage.k8s.io "standard-retain" deleted
NAME                                             PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
storageclass.storage.k8s.io/standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  23m
NAME                 STATUS   AGE
default              Active   23m
kube-node-lease      Active   23m
kube-public          Active   23m
kube-system          Active   23m
local-path-storage   Active   23m
```

ไม่มี PV เหลือ (`kubectl get sc,pv` แสดงแค่ class `standard`) namespace กลับเป็น 5 ตัวตั้งต้น image ของร้านยังอยู่บน Node

### 10.11 สรุป LAB 10 และปัญหาที่ส่งต่อ

<p align="center" id="fig-28">
  <img src="images/24-lab10-wrap-up.png" alt="รูปที่ 28 สรุป LAB สุดท้าย" width="900"><br>
  <em><b>รูปที่ 28</b> LAB10 สรุป: PVC ทำให้ db จำได้ แต่ยังได้แค่ 1 ตัว, ข้อมูลผูก Node และ Deployment ให้ทุก Pod ใช้ใบเบิกเดียวกัน → บท 009 StatefulSet</em>
</p>

**ตารางสรุป** สิ่งที่ PVC แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| ลบ Pod db / rollout restart db แล้วข้อมูลอยู่ | `orders=3` เท่าเดิม (request แรกอาจ 503 ครั้งเดียว) ไม่ต้อง restart web | ✅ PVC (บทนี้) |
| ลบ Deployment db แล้ว apply ใหม่ | `persistentvolumeclaim/som-db-data unchanged` → `orders=3` | ✅ PVC เป็น object แยกจาก Deployment |
| ลบ PVC พลาด | class `standard` (Delete): PV + โฟลเดอร์หาย `orders=0` / class `standard-retain` (Retain): `Released` → ลบ `claimRef` + `volumeName` → `orders=2` กลับมา | ✅ Retain + ขั้นตอนกู้ (ผู้ดูแลต้องลบตู้เองเมื่อเลิกใช้) |
| เผลอ scale db เป็น 2 | RWO: postgres สองตัวบนโฟลเดอร์เดียว ออเดอร์ 6 → 3 / CrashLoopBackOff / PANIC — RWOP: Pod ที่ 2 `Pending` ปลอดภัย | ✅ `replicas: 1` + Recreate + RWOP (กันได้ แต่ยังมีได้ตัวเดียว) |
| **db หลายตัว แต่ละตัวมีข้อมูลของตัวเอง** | Deployment มี template เดียว ทุก Pod อ้าง `claimName: som-db-data` เดียวกัน | ❌ → **StatefulSet** (`volumeClaimTemplates` ให้ PVC ประจำตัวทุก Pod, บทที่ 9) |
| **ชื่อ db คงที่** | ชื่อ Pod สุ่มทุกครั้ง (`tk2bn` → `zdw4m` → `hgt7s` …) | ❌ → **StatefulSet** (ชื่อเลขลำดับ `<ชื่อ>-0`, `<ชื่อ>-1`) |
| Node ที่ db อยู่ล่ม | local-path ผูก Node (LAB 8) db หยุดจน Node กลับ | ❌ → storage เครือข่าย (CSI) หรือ replication ระดับแอป |
| รหัสผ่านไม่อยู่ใน YAML | `meow1234` ยังเขียนตรง ๆ | ❌ → ConfigMap/Secret (บทหลัง) |

### สิ่งที่เห็นใน LAB 10

- เปลี่ยน `emptyDir` เป็น `persistentVolumeClaim` จุดเดียว: ลบ Pod db, rollout restart db, ลบ Deployment db → ออเดอร์อยู่ครบ ไม่ต้อง restart web
- ข้อมูลจริงคือโฟลเดอร์ `pgdata` (uid 70) ใน `/var/local-path-provisioner/pvc-<uid>_som-shop_som-db-data/` บน Node ที่ db ลง
- scale db เป็น 2 กับ RWO: ทั้งสองตัว Running บนโฟลเดอร์เดียวกัน ข้อมูลแยก (6/3) แล้วหาย (6 → 3) ภายในราว 1 นาทีหลัง scale กลับ
- ลบ PVC (Delete) = ข้อมูลหายจริง `orders=0`, Retain + RWOP: Pod ที่ 2 Pending และกู้ตู้เดิมได้ `orders=2`
- ลบ namespace แล้ว PV ที่ Retain และ StorageClass ยังอยู่ ต้องลบเอง

### คำถามท้าย LAB 10

1. ทำไมขั้น B (ลบ Pod db) ในบทนี้จึงไม่ต้อง `rollout restart deploy/som-web` แต่ในบทที่ 7 ต้องทำ และทำไม request แรกจึงอาจได้ 503
2. ขั้น D แสดง `persistentvolumeclaim/som-db-data unchanged` หมายความว่าอะไร ถ้าต้องการให้การลบ Deployment ลบข้อมูลไปด้วยต้องทำอย่างไร และควรทำหรือไม่
3. อธิบายลำดับเหตุการณ์ในขั้น F ตั้งแต่ scale เป็น 2 จนออเดอร์เหลือ 3 โดยอ้างข้อความ log อย่างน้อย 2 บรรทัด และบอกว่าทำไม RWO จึงไม่กันเหตุการณ์นี้
4. ถ้าขั้น H ใช้ RWOP แต่เปลี่ยน strategy เป็น RollingUpdate แล้วสั่ง `rollout restart deploy/som-db` คาดว่าจะเห็นอะไร (ตอบจากทฤษฎีหัวข้อ 14.2)
5. ถ้าน้องส้มอยากมี db 2 ตัว (ตัวหลัก + ตัวสำรอง) แต่ละตัวต้องมีอะไรที่ Deployment ให้ไม่ได้ และบทที่ 9 จะให้อะไร

> **🏆 ท้าทาย:** ก่อนขั้น G ลองใช้ `kubectl patch pv` เปลี่ยน PV ของ `som-db-data` (class `standard`) เป็น `Retain` แล้วลบ Deployment + PVC แล้วกู้ตู้กลับมาด้วยขั้นตอนของ LAB 6 (ใบเบิกใหม่ต้องใช้ class `standard` และ RWO ให้ตรงกับ PV) บันทึกว่าออเดอร์กลับมากี่รายการ (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเองและอย่าลืมเก็บกวาดตู้ที่ Retain)

> **ปูทางบทหน้า:** ร้านจำได้แล้ว แต่ครัวกลางยังมีได้แค่ตัวเดียว เพราะ Deployment ให้ทุก Pod ใช้ใบเบิกใบเดียวกันและชื่อ Pod สุ่มทุกครั้ง บทที่ 9 จะใช้ **StatefulSet** ให้ Pod ฐานข้อมูลมี **ชื่อคงที่และตู้เซฟประจำตัวทุก Pod**

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v4/`, kubectl แจ้ง `the path "pod.yaml" does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 008_kubernetes_pv_pvc k8s-lab:/workspace/` แล้ว 🐧 `cd` ไปโฟลเดอร์ของ LAB นั้น ตรวจด้วย `pwd` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 6 (build/load image ใหม่) |
| PVC `Pending` + Event `WaitForFirstConsumer` | class `standard` รอ Pod ตัวแรก | ปกติ สร้าง Pod ที่ใช้ PVC แล้วจะ Bound เอง |
| PVC `Pending` + `ProvisioningFailed … NodePath only supports ReadWriteOnce and ReadWriteOncePod` / `does not support block volume provisioning` | local-path ไม่รองรับ RWX/Block (LAB 5 ตั้งใจ) | ใช้ RWO/RWOP และ `Filesystem` หรือใช้ storage ที่รองรับ |
| PVC `Pending` + `configuration error, no node was specified` | class `Immediate` กับ local-path (LAB 7 ตั้งใจ) | ใช้ `WaitForFirstConsumer` |
| PVC `Pending` + `FailedBinding … no storage class is set` | `storageClassName: ""` แต่ไม่มี static PV ที่ตรง (ขนาด/โหมด) | สร้าง PV ที่ตรง หรือเอา `""` ออกเพื่อใช้ default class |
| Pod `Pending` แต่ `describe pod` ไม่มี Event | Pod รอ PVC ที่ยังไม่มีตู้ | `kubectl describe pvc <ชื่อ>` ดู Events ของ PVC |
| Pod `Pending` + `didn't match PersistentVolume's node affinity` | ตู้อยู่บน Node ที่หยุด/มี taint (LAB 8) | `docker start <node>` แล้วรอ Node `Ready` |
| `kubectl delete pvc` แล้วค้าง `Terminating` | finalizer `pvc-protection` + มี Pod ใช้อยู่ (`Used By`) | ลบ Pod หรือ Deployment ที่ใช้ PVC ก่อน (อย่าลบ finalizer เอง) |
| PV ค้าง `Released` ไม่หาย | reclaimPolicy `Retain` | กู้ (ลบ `claimRef` + PVC `volumeName`) หรือ `kubectl delete pv` แล้วลบโฟลเดอร์บน Node เอง |
| apply PVC ชื่อเดิมแล้วได้ PV ใหม่ ข้อมูลเก่าไม่มา | PV เก่ายังมี `claimRef` ของ PVC ตัวเก่า | ลบ `claimRef` แล้วใช้ `pvc-reuse.yaml`/`pvc-rescue.yaml` ที่มี `volumeName` |
| `The PersistentVolumeClaim "som-db-data" is invalid: spec: Forbidden: spec is immutable after creation …` | apply ไฟล์ที่มี PVC ชื่อเดียวกันแต่ spec ต่างจากที่ Bound อยู่ (เช่น ไม่มี `volumeName`) | `kubectl apply -f k8s-retain/10-db.yaml -l app=som-db` (เฉพาะ Deployment) |
| apply `k8s-retain/` ทั้งโฟลเดอร์แล้ว PVC ค้างหรือ error เกี่ยวกับ `PV_NAME` | `pvc-rescue.yaml` เป็นแม่แบบที่ยังไม่แทนชื่อ PV | apply ทีละไฟล์ตามขั้น H/H2 เท่านั้น ลบ PVC ที่ผิดแล้วทำใหม่ |
| `Error from server (Forbidden): … only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize` | class ไม่มี `allowVolumeExpansion: true` | ปกติของ `standard` ใน kind (LAB 7) |
| PVC ขยายแล้ว CAPACITY ไม่เปลี่ยน + `ExternalExpanding` | driver ไม่มีตัวขยาย (local-path) | ปกติใน kind ระบบจริงต้องใช้ CSI ที่รองรับ resize |
| `kubectl exec … -- kill 1` แล้ว RESTARTS ไม่เพิ่ม | PID 1 ใน container ไม่ถูกปิดด้วยสัญญาณที่ไม่มี handler | `kubectl exec cache-demo -- touch /tmp/stop` (LAB 1) |
| `Warning: would violate PodSecurity "restricted:latest": … hostPath …` | namespace ตั้ง `warn: restricted` (LAB 2 และ `som-shop`) | ปกติ เป็นแค่คำเตือน Pod ยังถูกสร้าง |
| `docker exec lab-worker ls /var/local-path-provisioner` ได้ `No such file or directory` หรือไม่เห็นโฟลเดอร์ที่คาด | ยังไม่เคยมี PV บน Node นั้น หรือ Pod/ตู้อยู่อีก Node | ใช้ `N=$(kubectl get pod <ชื่อ> -o jsonpath='{.spec.nodeName}')` หรือ `nodeAffinity` ของ PV แล้ว `docker exec $N …` |
| `kubectl logs` ได้ไม่ครบทันทีหลัง Ready | สคริปต์ใน container ยังรันไม่ถึง | รอ 1–2 วินาทีแล้วสั่งใหม่ |
| เวลาใน log ของ Pod ช้ากว่านาฬิกา 7 ชั่วโมง | busybox/postgres ใช้ UTC | ปกติ (`date` ใน shell ของ k8s-lab เป็นเวลาไทย) |
| `kubectl describe pod -l app=nd \| grep FailedScheduling` ไม่เจอ (LAB 8) | Event ไม่แสดงในรอบนั้น | `kubectl get events --sort-by=.lastTimestamp \| grep FailedScheduling` |
| หลัง LAB 8 Node ยัง `NotReady` / Pod ใหม่ไม่ขึ้น | ลืม `docker start` | 🐧 `docker start lab-worker` (หรือ Node ที่หยุด) แล้วตรวจ `kubectl get nodes` |
| `kind load` ล้มเหลว `failed to detect containerd snapshotter` | สั่งระหว่างที่ Node ถูกหยุด | `docker start` Node ให้ครบก่อนแล้ว load ใหม่ |
| request แรกหลังลบ Pod db ได้ `db-not-ready [503]` | connection เดิมใน pool ของ web หลุด | ปกติ request ถัดไปเป็น 200 |
| หลังขั้น G ร้าน 503 ค้าง (`db-not-ready`) | db ใหม่ว่างเปล่า ไม่มีตาราง | `kubectl -n som-shop rollout restart deploy/som-web` |
| ขั้น F: Pod db `Completed` → `CrashLoopBackOff` | postgres หยุดเพราะ `lock file is invalid` (ตั้งใจให้เห็น) | รอ ~1 นาทีให้ Running เอง ถ้า log มี `PANIC` และค้างเกิน 2–3 นาที ไปขั้น G |
| `ImagePullBackOff` ของ `som-shop-web:1.2` หรือ `postgres:17.11-alpine` | ยังไม่ได้ load image เข้า Node (คลัสเตอร์ใหม่) | LAB 0 ขั้นที่ 6 |
| `provided port is already allocated` ตอน apply `k8s/20-web.yaml` | Service อื่นจอง 30080 (เช่น `som-shop` ของบทที่ 7 ค้าง) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace ที่ค้าง |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080/api/stats` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| ลบ namespace `som-shop` ใช้เวลา ~30 วินาที | Pod web มี preStop 5 วินาทีและ grace period | ปกติ รอให้จบ |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `kubectl get sc` (`standard (default)` … `WaitForFirstConsumer false`), Pod `local-path-provisioner` Running และ `crictl images` ที่เห็น `som-shop-web 1.2` + `postgres 17.11-alpine`
- [ ] **LAB 1** `RESTARTS 1` หลัง `touch /tmp/stop` + `ls` ที่ `/tmp` ว่างแต่ `/cache/x.txt` อยู่ และผลหลังลบ Pod (`boot.log` บรรทัดเดียว)
- [ ] **LAB 2** Warning `restricted volume type "hostPath"`, `cat notes.txt` บนสอง Node ที่ต่างกัน และไฟล์ที่ยังอยู่หลังลบ namespace
- [ ] **LAB 3** PVC `Pending` + Event `WaitForFirstConsumer`, PVC/PV `Bound` + annotation `selected-node`, `hostPath`/`nodeAffinity` ของ PV และ `ls /var/local-path-provisioner/` บน Node
- [ ] **LAB 4** `pv-manual` `Available` → `Bound` (`CAPACITY 100Mi`), `too-big` `FailedBinding` และ Pod `manual-user` บน `lab-worker2`
- [ ] **LAB 5** `rwo-a`/`rwo-b` บน Node เดียว, `dd` 50MB ลง PVC 10Mi, `rwop-b` Pending และ `ProvisioningFailed` ของ RWX กับ Block
- [ ] **LAB 6** `Terminating` + `pvc-protection` + `Used By`, PV `Retain`/`Released` + `keepme.txt` บน Node, PVC ชื่อเดิมได้ PV ใหม่ และหลังกู้ได้ `keepme` เวลาเดิม
- [ ] **LAB 7** `kubectl get sc` 4 class, `no node was specified`, Forbidden ของ `std`, `spec=20Mi status=10Mi` + `ExternalExpanding` ของ `ex`
- [ ] **LAB 8** ตารางเวลาของตัวเอง (NotReady, Pending), `FailedScheduling … didn't match PersistentVolume's node affinity` และ `boot.txt` 2 บรรทัดหลัง `docker start`
- [ ] **LAB 9** `exceeded quota` ของ `p200` และ `p10`, `describe quota`, log ของ Pod `fsg` (`drwxrwxrwx 0 0`, `Read-only file system`) และ `fsg-e` ที่หายหลังลบ Pod
- [ ] **LAB 10** (1) PVC `Bound` + `orders=3` (2) browser หน้าร้าน (3) ลบ Pod db / rollout restart db / ลบ Deployment db (`unchanged`) แล้วยัง `orders=3` (4) `ls -ln …/pgdata` บน Node (5) ขั้น F: Pod 2 ตัวบน Node เดียว, psql ได้ 6 กับ 3, log `lock file is invalid` (หรือ `PANIC`) และ `orders` หลัง scale กลับ (6) ขั้น G: `orders=0` + browser หน้า 503 (7) ขั้น H: `RWOP standard-retain` + Pod ที่ 2 `Pending` (8) ขั้น H2: `Bound` PV เดิม + `orders=2`
- [ ] ท้ายสุด `kubectl get pv,pvc -A` ว่าง, `kubectl get sc` เหลือ `standard` ตัวเดียว และ `kubectl get ns` เหลือ 5 ตัวตั้งต้น

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Pod `cache-demo` | 1 | `kubectl get pod cache-demo` | `kubectl delete pod cache-demo` |
| namespace `hostpath-lab` และโฟลเดอร์ `/srv/som-hostpath` บน Node | 2 | `kubectl get ns hostpath-lab`; `docker exec lab-worker ls /srv` | `kubectl delete ns hostpath-lab`; `for n in lab-worker lab-worker2; do docker exec $n rm -rf /srv/som-hostpath; done` |
| PVC/PV ใน `default` (`notes`, `rwo-data`, `single`, `shared`, `blk`, `ledger`, `kept`, `std`, `ex`, `imm`, `nd-data`, `fsg-data`) | 3, 5–9 | `kubectl get pv,pvc -A` | `kubectl delete -f .` ในโฟลเดอร์ของ LAB นั้น (ลบ Pod/Deployment ก่อน PVC) |
| PV `pv-manual` และ `/srv/som-manual` บน `lab-worker2` | 4 | `kubectl get pv pv-manual`; `docker exec lab-worker2 ls /srv` | `kubectl delete pv pv-manual`; `docker exec lab-worker2 rm -rf /srv/som-manual` |
| PV ที่ `Released` (Retain) และโฟลเดอร์ `pvc-…` | 6, 7, 10 | `kubectl get pv`; `docker exec <node> ls /var/local-path-provisioner/` | `kubectl delete pv <ชื่อ>`; `docker exec <node> rm -rf /var/local-path-provisioner/<โฟลเดอร์>` |
| StorageClass `standard-retain`, `local-immediate`, `local-expand` | 7, 10 | `kubectl get sc` | `kubectl delete sc <ชื่อ>` (ต้องเหลือ `standard` ตัวเดียว) |
| Node ที่ถูก `docker stop` | 8 | `kubectl get nodes`; `docker ps -a --filter name=lab-` | `docker start <node>` แล้วรอ `Ready` |
| namespace `quota-lab` | 9 | `kubectl get ns quota-lab` | `kubectl delete ns quota-lab` |
| namespace `som-shop` (**จอง NodePort 30080**) | 10 | `kubectl get ns som-shop` | `kubectl delete ns som-shop` แล้วลบ PV ที่ Retain + StorageClass ตามขั้น I |
| image `som-shop-web:1.2`, postgres บน Node | 0, 10 | `docker exec lab-worker crictl images \| grep -E "som-shop\|postgres"` | **เก็บไว้ได้** (ใช้ซ้ำในบทถัดไป ถ้า `k8s-down` จะหายไปด้วย) |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl get ns
kubectl get pv,pvc -A
kubectl get sc
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n ls /var/local-path-provisioner/ /srv 2>&1; done
```

ผลที่ถูกต้อง: 3 Node `Ready`, namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), `No resources found` สำหรับ PV/PVC, StorageClass เหลือ `standard (default)` ตัวเดียว และไม่มีโฟลเดอร์ `pvc-…`, `som-hostpath` หรือ `som-manual` ค้างบน Node

คลัสเตอร์ `lab` และ image ของร้านเก็บไว้ใช้ต่อในบทที่ 9 ได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ PV, จำนวนออเดอร์ และเวลา) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ (สั่งซื้อ 4 รายการ) ชื่อ Pod และจำนวนออเดอร์ในภาพจึงต่างจากผลคำสั่งในเอกสาร
