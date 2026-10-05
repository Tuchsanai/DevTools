
---

## LAB 7: zero-downtime ผ่าน NodePort 30080

{{FIG:L11|LAB 7 นับ error ก่อน/หลังใส่ preStop}}

**เป้าหมาย:** นับ error ที่ลูกค้าเห็นระหว่าง rollout ผ่าน NodePort 30080 เทียบแบบไม่มี preStop กับแบบ `preStop` + `maxSurge 1 / maxUnavailable 0`

**ไฟล์:** `lab07-zero-downtime/00-ns.yaml` (namespace `zdt-lab`), `lab07-zero-downtime/web.yaml` (3 replicas strategy default ไม่มี preStop), `lab07-zero-downtime/web-nodeport.yaml` (Service NodePort `30080`), `lab07-zero-downtime/patches/graceful-patch.yaml` (`maxSurge: 1`, `maxUnavailable: 0`, `terminationGracePeriodSeconds: 30`, `preStop.sleep.seconds: 5`) และสคริปต์ `../som-shop-v3/hit.sh`

**hit.sh** (สำเนาจากบทที่ 6) ยิงคำขอด้วย `curl` ใหม่ทุกครั้ง (connection ใหม่ → Service สุ่ม Pod ใหม่ทุกครั้ง) รูปแบบ `./hit.sh [-q] [URL] [N] [DELAY]` ค่าเริ่มต้น URL `http://localhost:30080/api/whoami`, N 60, DELAY 0.1 วินาที โหมด `-q` พิมพ์ `.` (สำเร็จ) / `x` (ล้มเหลว) แล้วสรุป `ok=… err=…` ใน LAB นี้ส่ง URL เป็นหน้าแรกของ nginx `http://localhost:30080/`

### ขั้นที่ 1: เปิด NodePort 30080

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab07-zero-downtime/ && kubectl -n zdt-lab rollout status deploy/web && sleep 2 && curl -s localhost:30080
../som-shop-v3/hit.sh http://localhost:30080/ 30
```

```text
namespace/zdt-lab created
service/web created
deployment.apps/web created
...
deployment "web" successfully rolled out
web v1 from web-779cb4fbb8-4zk8b
จำนวน  Pod  เวอร์ชัน
      9 web v1 from web-779cb4fbb8-4zk8b
     14 web v1 from web-779cb4fbb8-ql6cc
      7 web v1 from web-779cb4fbb8-zzkgv
ok=30 err=0 (ใช้เวลา 3.2 วินาที)
```

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:30080** จะเห็นข้อความ `web v1 from web-...` (refresh แล้วมักได้ Pod เดิมเพราะ keep-alive ของ browser — บทที่ 6) หัวตารางของ hit.sh เขียน `จำนวน  Pod  เวอร์ชัน` เพราะออกแบบไว้สำหรับร้านน้องส้ม แต่ใช้นับหน้า nginx ได้ถูกต้อง

### ขั้นที่ 2: รอบที่ 1 — ไม่มี preStop

**terminal 1** — ยิง 300 ครั้ง (ราว 33 วินาที)

```bash
../som-shop-v3/hit.sh -q http://localhost:30080/ 300
```

**terminal 2** — ภายในไม่กี่วินาทีหลังเริ่มยิง ให้เปลี่ยนรุ่น

```bash
kubectl -n zdt-lab set env deploy/web VERSION=v2 && time kubectl -n zdt-lab rollout status deploy/web >/dev/null
```

ผลจริงใน terminal 1 (rollout ใช้ราว 3.6 วินาที)

```text
.........................................x..xx.x....(ตัดจุด)
ข้อความ error:
      1 curl: (28) Operation timed out
      3 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 2.6 วินาที
ok=296 err=4 (ใช้เวลา 33.9 วินาที)
```

ทำซ้ำอีก 2 รอบ (`VERSION=v3`, `VERSION=v4`) ได้ผลจริง

```text
ข้อความ error:
      1 curl: (28) Operation timed out
      1 curl: (52) Empty reply from server
      2 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 3.4 วินาที
ok=296 err=4 (ใช้เวลา 34.1 วินาที)
...
ข้อความ error:
      1 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 0.0 วินาที
ok=299 err=1 (ใช้เวลา 32.8 วินาที)
```

รวม 3 รอบได้ error **4, 4, 1** จาก 300 ครั้ง ทั้งหมดเกิดช่วงที่ Pod เก่าถูกปิด (ทฤษฎีหัวข้อ 6.1) จำนวนเป็นการสุ่ม เครื่องนักศึกษาอาจได้มากหรือน้อยกว่านี้ (บางรอบอาจเป็น 0)

### ขั้นที่ 3: ใส่ graceful-patch

```bash
cat lab07-zero-downtime/patches/graceful-patch.yaml
kubectl -n zdt-lab patch deploy web --patch-file lab07-zero-downtime/patches/graceful-patch.yaml && time kubectl -n zdt-lab rollout status deploy/web >/dev/null && kubectl -n zdt-lab get deploy web -o jsonpath="{.spec.strategy}{\"\n\"}{.spec.template.spec.containers[0].lifecycle}{\"\n\"}"
```

```text
deployment.apps/web patched

real	0m3.803s
...
{"rollingUpdate":{"maxSurge":1,"maxUnavailable":0},"type":"RollingUpdate"}
{"preStop":{"sleep":{"seconds":5}}}
```

patch นี้แก้ template ด้วย (เพิ่ม `lifecycle` และ grace period) จึงเกิด rollout 1 ครั้ง **รอให้จบก่อน** เริ่มนับรอบที่ 2

### ขั้นที่ 4: รอบที่ 2 — preStop 5 วินาที + maxUnavailable 0

ทำแบบเดียวกับขั้นที่ 2 (terminal 1 `../som-shop-v3/hit.sh -q http://localhost:30080/ 300`, terminal 2 `kubectl -n zdt-lab set env deploy/web VERSION=v5 && time kubectl -n zdt-lab rollout status deploy/web >/dev/null`) ผลจริง 3 รอบ (v5, v6, v7)

```text
rollout status ใช้เวลา 3.9 วินาที
............................................................................................................................................................................................................................................................................................................
ok=300 err=0 (ใช้เวลา 32.0 วินาที)
...
rollout status ใช้เวลา 3.9 วินาที
ok=300 err=0 (ใช้เวลา 31.9 วินาที)
...
rollout status ใช้เวลา 5.7 วินาที
ok=300 err=0 (ใช้เวลา 31.9 วินาที)
```

ทั้ง 3 รอบ **err 0 จาก 300** ถ้ารัน `hit.sh` แบบไม่มี `-q` ระหว่างเปลี่ยนรุ่น จะเห็นทั้งรุ่นเก่าและใหม่ปนกัน ผลจริงเมื่อยิง 200 ครั้งจากเครื่องฝั่งนักศึกษาผ่าน NodePort ระหว่าง `set env VERSION=v8`

```text
จำนวน  Pod  เวอร์ชัน
     35 web v7 from web-7547dd7659-nsmbn
     14 web v7 from web-7547dd7659-wx4n7
     23 web v7 from web-7547dd7659-zqrz9
     41 web v8 from web-5d8fddbb74-dw24d
     47 web v8 from web-5d8fddbb74-kbvmc
     40 web v8 from web-5d8fddbb74-pzzqg
ok=200 err=0 (ใช้เวลา 21.4 วินาที)
```

### ขั้นที่ 5: เก็บกวาด (ต้องทำก่อน LAB 10)

```bash
time kubectl delete ns zdt-lab; kubectl get svc -A | grep -E "3008[0-2]" || echo "(30080 ว่าง)"
```

```text
namespace "zdt-lab" deleted

real	0m27.034s
(30080 ว่าง)
```

ลบ namespace ครั้งนี้ใช้ราว 27 วินาที (นานกว่า LAB อื่น) เพราะ Pod มี `preStop` 5 วินาทีและ grace period 30 วินาที

### สิ่งที่เห็น

- ไม่มี preStop: err 4, 4, 1 จาก 300 (`Connection reset by peer`, `Operation timed out`, `Empty reply from server`)
- preStop 5 + maxSurge 1 / maxUnavailable 0: err 0, 0, 0 จาก 300

**คำถามชวนคิด**

1. ถ้าตั้ง `preStop.sleep.seconds: 40` แต่ `terminationGracePeriodSeconds: 30` จะเกิดอะไรขึ้นกับ Pod ที่กำลังปิด
2. ทำไมรอบแรกบางครั้งได้ error เพียง 1 แต่บางครั้งได้ 4 ทั้งที่คำสั่งเหมือนกัน

---

## LAB 8: ย้าย ReplicaSet เป็น Deployment

{{FIG:L12|LAB 8 Deployment รับเลี้ยง RS เดิม}}

**เป้าหมาย:** ร้านที่ใช้ ReplicaSet แบบบทที่ 6 อยู่แล้ว ย้ายมาเป็น Deployment ชื่อเดิม selector เดิม โดยลูกค้าไม่สะดุด และเห็นการ "รับเลี้ยง" ReplicaSet เดิม

**ไฟล์:** `lab08-migrate/00-ns.yaml` (namespace `migrate-lab`), `lab08-migrate/web-rs.yaml` (ReplicaSet `web` 3 replicas `app=web` VERSION v1), `lab08-migrate/web-svc.yaml`, `lab08-migrate/client-pod.yaml`, `lab08-migrate/web-deploy.yaml` (Deployment `web` selector `app=web` VERSION v2)

### ขั้นที่ 1: สร้างร้านแบบบทที่ 6

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab08-migrate/00-ns.yaml -f lab08-migrate/web-rs.yaml -f lab08-migrate/web-svc.yaml -f lab08-migrate/client-pod.yaml && kubectl -n migrate-lab wait --for=condition=Ready pod -l app=web --timeout=90s && kubectl -n migrate-lab wait --for=condition=Ready pod/client --timeout=60s && kubectl -n migrate-lab get rs,pods --show-labels
```

```text
namespace/migrate-lab created
replicaset.apps/web created
service/web created
pod/client created
...
NAME                  DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web   3         3         3       2s    app=web

NAME            READY   STATUS    RESTARTS   AGE   LABELS
pod/client      1/1     Running   0          2s    role=client
pod/web-nw85z   1/1     Running   0          2s    app=web
pod/web-phg2q   1/1     Running   0          2s    app=web
pod/web-r58mb   1/1     Running   0          2s    app=web
```

ReplicaSet ที่เขียนเองไม่มี `pod-template-hash` ชื่อ Pod จึงเป็น `web-<สุ่ม 5 ตัว>`

### ขั้นที่ 2: apply Deployment ระหว่างที่ลูกค้ายิงวน

**terminal 2** — `kubectl -n migrate-lab get rs -w`

**terminal 3** — `kubectl -n migrate-lab exec client -- sh -c "while true; do wget -qO- -T 2 http://web || echo ERR; sleep 0.2; done"`

**terminal 1**

```bash
kubectl apply -f lab08-migrate/web-deploy.yaml && time kubectl -n migrate-lab rollout status deploy/web
```

```text
deployment.apps/web created
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
...
deployment "web" successfully rolled out

real	0m3.785s
```

ผลจริงใน terminal 2 (ตัดบรรทัดซ้ำ)

```text
NAME   DESIRED   CURRENT   READY   AGE
web    3         3         3       6s
web-7b6cd79469   1         0         0       0s
web-7b6cd79469   1         1         1       2s
web              2         3         3       11s
web              2         2         2       11s
web-7b6cd79469   2         2         2       3s
web              1         2         2       12s
web              1         1         1       12s
web-7b6cd79469   3         3         3       4s
web              0         1         1       13s
web              0         0         0       13s
```

ผลจริงของลูกค้าใน terminal 3 (สรุป)

```text
     30 web v1 from web-xxxxx (Pod ของ RS เดิม)
    143 web v2 from web-7b6cd79469-xxxxx
```

RS `web` เดิมถูก scale 3→2→1→0 สลับกับ RS ใหม่ `web-7b6cd79469` 0→1→2→3 แบบ rolling ปกติ ลูกค้า 173 ครั้ง **ไม่มี ERR**

### ขั้นที่ 3: ตรวจการรับเลี้ยง

```bash
kubectl -n migrate-lab get rs web -o jsonpath='{.metadata.ownerReferences}{"\n"}{.metadata.annotations}{"\n"}{.spec.selector}{"\n"}{.metadata.labels}{"\n"}'
kubectl -n migrate-lab get deploy,rs,pods --show-labels; kubectl -n migrate-lab rollout history deploy/web
kubectl -n migrate-lab describe deploy web | sed -n "/^OldReplicaSets/,\$p"
```

```text
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"web","uid":"0d405a82-4d4c-4556-a59d-c6cbf64d4639"}]
{"deployment.kubernetes.io/desired-replicas":"3","deployment.kubernetes.io/max-replicas":"4","kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"apps/v1\",\"kind\":\"ReplicaSet\",...
{"matchLabels":{"app":"web"}}
{"app":"web"}
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/web   3/3     3            3           42s   app=web

NAME                             DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web              0         0         0       51s   app=web
replicaset.apps/web-7b6cd79469   3         3         3       42s   app=web,pod-template-hash=7b6cd79469

NAME                       READY   STATUS    RESTARTS   AGE   LABELS
pod/client                 1/1     Running   0          51s   role=client
pod/web-7b6cd79469-5c5n8   1/1     Running   0          39s   app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-kr5l2   1/1     Running   0          40s   app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-kwhzj   1/1     Running   0          42s   app=web,pod-template-hash=7b6cd79469
deployment.apps/web 
REVISION  CHANGE-CAUSE
0         <none>
1         <none>

OldReplicaSets:  web (0/0 replicas created)
NewReplicaSet:   web-7b6cd79469 (3/3 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  42s   deployment-controller  Scaled up replica set web-7b6cd79469 from 0 to 1
  Normal  ScalingReplicaSet  40s   deployment-controller  Scaled down replica set web from 3 to 2
  Normal  ScalingReplicaSet  40s   deployment-controller  Scaled up replica set web-7b6cd79469 from 1 to 2
  Normal  ScalingReplicaSet  39s   deployment-controller  Scaled down replica set web from 2 to 1
  Normal  ScalingReplicaSet  39s   deployment-controller  Scaled up replica set web-7b6cd79469 from 2 to 3
  Normal  ScalingReplicaSet  38s   deployment-controller  Scaled down replica set web from 1 to 0
```

- RS `web` เดิมได้ **ownerReferences ชี้ Deployment `web`** และ annotation `desired-replicas`/`max-replicas` แต่ **ไม่มี** annotation `revision` และไม่ได้ label `pod-template-hash`
- `rollout history` มี **REVISION 0** (= RS เดิม) และ 1 (= รุ่นใหม่) `describe` แสดง RS เดิมเป็น `OldReplicaSets`

ลอง undo (เสริม)

```bash
kubectl -n migrate-lab rollout undo deploy/web; echo "exit=$?"; sleep 6; kubectl -n migrate-lab get rs --show-labels; kubectl -n migrate-lab get pods --show-labels; kubectl -n migrate-lab rollout history deploy/web
```

```text
Warning: resource deployments/web was previously managed with 'kubectl apply'. ...
deployment.apps/web rolled back
exit=0
NAME             DESIRED   CURRENT   READY   AGE   LABELS
web              3         3         3       64s   app=web
web-7b6cd79469   0         0         0       55s   app=web,pod-template-hash=7b6cd79469
NAME        READY   STATUS    RESTARTS   AGE   LABELS
client      1/1     Running   0          64s   role=client
web-7897n   1/1     Running   0          6s    app=web
web-bss8k   1/1     Running   0          5s    app=web
web-zkcks   1/1     Running   0          4s    app=web
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

undo กลับไปขยาย RS `web` เดิมได้จริง (Pod ไม่มี hash) และ RS เดิมกลายเป็น revision 2

### ขั้นที่ 4 (เสริม): template เหมือนกันทุกตัวอักษร

เริ่ม namespace ใหม่ที่มีแค่ ReplicaSet แล้ว apply Deployment ที่ใช้ `VERSION v1` เท่ากับ RS (ใช้ `sed` แก้ค่าในไฟล์ระหว่างส่งให้ kubectl โดยไม่แก้ไฟล์จริง)

```bash
kubectl delete ns migrate-lab >/dev/null; kubectl apply -f lab08-migrate/00-ns.yaml -f lab08-migrate/web-rs.yaml >/dev/null && kubectl -n migrate-lab wait --for=condition=Ready pod -l app=web --timeout=90s >/dev/null && kubectl -n migrate-lab get pods
sed "s/value: v2 .*/value: v1/" lab08-migrate/web-deploy.yaml | kubectl apply -f - && sleep 8 && kubectl -n migrate-lab get deploy,rs,pods --show-labels && kubectl -n migrate-lab rollout history deploy/web
```

```text
NAME        READY   STATUS    RESTARTS   AGE
web-drr68   1/1     Running   0          2s
web-rfv4z   1/1     Running   0          2s
web-wgv7n   1/1     Running   0          2s
deployment.apps/web created
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/web   3/3     3            3           8s    app=web

NAME                  DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web   3         3         3       10s   app=web

NAME            READY   STATUS    RESTARTS   AGE   LABELS
pod/web-drr68   1/1     Running   0          10s   app=web
pod/web-rfv4z   1/1     Running   0          10s   app=web
pod/web-wgv7n   1/1     Running   0          10s   app=web
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
```

ไม่มี ReplicaSet ใหม่ ไม่มี Pod ใหม่ RS `web` เดิมกลายเป็น **รุ่นปัจจุบัน (revision 1)** ทันที ผลนี้สำคัญกับ LAB 10 (ฐานข้อมูล `som-db`)

### ขั้นที่ 5 (เสริม): ทางสำรอง --cascade=orphan

```bash
kubectl delete ns migrate-lab >/dev/null; kubectl apply -f lab08-migrate/00-ns.yaml -f lab08-migrate/web-rs.yaml -f lab08-migrate/web-svc.yaml -f lab08-migrate/client-pod.yaml >/dev/null && kubectl -n migrate-lab wait --for=condition=Ready pod -l app=web --timeout=90s >/dev/null && kubectl -n migrate-lab wait --for=condition=Ready pod/client --timeout=60s >/dev/null
kubectl -n migrate-lab delete rs web --cascade=orphan && kubectl -n migrate-lab get rs,pods --show-labels
```

```text
replicaset.apps "web" deleted from migrate-lab namespace
NAME            READY   STATUS    RESTARTS   AGE   LABELS
pod/client      1/1     Running   0          2s    role=client
pod/web-nb7dg   1/1     Running   0          2s    app=web
pod/web-nglsz   1/1     Running   0          2s    app=web
pod/web-vrtjs   1/1     Running   0          2s    app=web
```

เปิดลูกค้ายิงวนใน terminal 3 อีกครั้ง แล้ว apply Deployment และลบ Pod เดิมที่ไม่มี `pod-template-hash`

```bash
kubectl apply -f lab08-migrate/web-deploy.yaml && kubectl -n migrate-lab rollout status deploy/web && kubectl -n migrate-lab get rs,pods --show-labels
kubectl -n migrate-lab delete pod -l "app=web,!pod-template-hash"; kubectl -n migrate-lab get pods --show-labels
```

```text
deployment.apps/web created
...
deployment "web" successfully rolled out
NAME                             DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/web-7b6cd79469   3         3         3       1s    app=web,pod-template-hash=7b6cd79469

NAME                       READY   STATUS    RESTARTS   AGE   LABELS
pod/client                 1/1     Running   0          5s    role=client
pod/web-7b6cd79469-9s6jr   1/1     Running   0          1s    app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-dps2l   1/1     Running   0          1s    app=web,pod-template-hash=7b6cd79469
pod/web-7b6cd79469-kj7xw   1/1     Running   0          1s    app=web,pod-template-hash=7b6cd79469
pod/web-nb7dg              1/1     Running   0          5s    app=web
pod/web-nglsz              1/1     Running   0          5s    app=web
pod/web-vrtjs              1/1     Running   0          5s    app=web
pod "web-nb7dg" deleted from migrate-lab namespace
pod "web-nglsz" deleted from migrate-lab namespace
pod "web-vrtjs" deleted from migrate-lab namespace
...
```

ผลจริงของลูกค้าในรอบนี้

```text
      1 ERR
     28 web v1 from web-xxxxx (Pod เดิมที่ไม่มีเจ้าของ)
    119 web v2 from web-7b6cd79469-xxxxx
      1 wget: can't connect to remote host (10.96.60.208): Connection refused
```

Deployment ไม่รับเลี้ยง Pod หลง (selector ของ RS ใหม่มี hash) จึงสร้าง Pod ใหม่ครบ 3 ตัว ช่วงหนึ่งมี 6 Pod หลัง Service และตอนลบ Pod เดิมพร้อมกันลูกค้าเจอ error 1 ครั้ง ทางหลัก (รับเลี้ยง) จึงนุ่มนวลกว่า

### ขั้นที่ 6: เก็บกวาด

```bash
time kubectl delete ns migrate-lab
```

```text
namespace "migrate-lab" deleted

real	0m10.437s
```

### สิ่งที่เห็น

- Deployment รับเลี้ยง RS ที่ไม่มีเจ้าของซึ่ง label ตรง selector: ติด ownerReferences, scale ลงแบบ rolling, โผล่ใน history เป็น REVISION 0, undo กลับไปได้
- template เหมือนกันทุกตัวอักษร → RS เดิมเป็นรุ่นปัจจุบัน ไม่มีอะไรถูกสร้างใหม่
- ทางสำรอง orphan ใช้ได้แต่ต้องลบ Pod เก่าเอง (เจอ error 1 ครั้ง)

**คำถามชวนคิด**

1. ถ้า Deployment ใช้ selector `app: web, tier: front` (ไม่ตรงกับ RS เดิม) จะเกิดอะไรขึ้นกับ RS `web` และ Service `web` ช่วงนั้น
2. ทำไม Pod ใหม่ของ Deployment (มี `app=web`) จึงไม่ถูก RS `web` เดิมนับรวม ทั้งที่ selector ของ RS เดิมคือ `app=web`

---

## LAB 9: blue/green และ canary

{{FIG:L13|LAB 9 blue/green และ canary}}

**เป้าหมาย:** สลับรุ่นทั้งร้านด้วย selector ของ Service (blue/green) และแบ่งลูกค้าตามจำนวน Pod (canary)

**ไฟล์:** `lab09-release/00-ns.yaml` (namespace `release-lab`), `web-blue.yaml`/`web-green.yaml` (2 replicas label `version`), `web-svc.yaml` (selector `app=web,version=blue`), `web-stable.yaml` (4 replicas `track=stable`), `web-canary.yaml` (1 replica `track=canary`), `web-svc-all.yaml` (selector `app=web` อย่างเดียว), `client-pod.yaml`

### ขั้นที่ 1: blue/green

🐧 **terminal 1** (อยู่ที่ `02_LAB/labs`)

```bash
kubectl apply -f lab09-release/00-ns.yaml -f lab09-release/web-blue.yaml -f lab09-release/web-green.yaml -f lab09-release/web-svc.yaml -f lab09-release/client-pod.yaml && kubectl -n release-lab rollout status deploy/web-blue && kubectl -n release-lab rollout status deploy/web-green && kubectl -n release-lab wait --for=condition=Ready pod/client --timeout=60s && kubectl -n release-lab get deploy,pods --show-labels
kubectl -n release-lab exec client -- sh -c 'for i in $(seq 20); do wget -qO- -T 2 http://web; done' | sort | uniq -c
```

```text
...
NAME                             READY   STATUS    RESTARTS   AGE   LABELS
pod/client                       1/1     Running   0          2s    role=client
pod/web-blue-65757d87bc-9dkgq    1/1     Running   0          2s    app=web,pod-template-hash=65757d87bc,version=blue
pod/web-blue-65757d87bc-hd8xl    1/1     Running   0          2s    app=web,pod-template-hash=65757d87bc,version=blue
pod/web-green-7547c8b9d9-94r9t   1/1     Running   0          2s    app=web,pod-template-hash=7547c8b9d9,version=green
pod/web-green-7547c8b9d9-kpwvl   1/1     Running   0          2s    app=web,pod-template-hash=7547c8b9d9,version=green
     10 web blue from web-blue-65757d87bc-9dkgq
     10 web blue from web-blue-65757d87bc-hd8xl
```

ทั้งสองชุดเปิดพร้อมกัน แต่ลูกค้าไปชุด blue ทั้งหมด สลับเป็น green ด้วยคำสั่งเดียว แล้ว **รอ 2 วินาที** ก่อนยิงทดสอบ

```bash
kubectl -n release-lab patch svc web -p '{"spec":{"selector":{"version":"green"}}}'
sleep 2; kubectl -n release-lab exec client -- sh -c 'for i in $(seq 20); do wget -qO- -T 2 http://web; done' | sort | uniq -c
```

```text
service/web patched
     13 web green from web-green-7547c8b9d9-94r9t
      7 web green from web-green-7547c8b9d9-kpwvl
```

> **ข้อควรระวัง (เจอจริงตอนทดสอบ):** ถ้ายิง 20 ครั้งต่อจาก `patch` ทันที (คำขอทั้ง 20 จบในไม่ถึง 1 วินาที) ยังได้ blue ทั้ง 20 ครั้ง และเมื่อ patch กลับเป็น blue แล้วยิงทันทีกลับได้ green ทั้ง 20 ครั้ง เพราะ EndpointSlice และ kube-proxy ยังอัปเดตไม่ทัน เมื่อวัดละเอียดด้วยการยิงทุก 0.1 วินาทีพร้อมเวลา คำขอในวินาทีเดียวกับคำสั่ง patch เริ่มเป็น green แล้ว คือสลับเสร็จภายในไม่ถึง 1 วินาที

ย้อนกลับก็ใช้คำสั่งเดียวกันโดยเปลี่ยนเป็น `"version":"blue"` (ทั้งสองชุดยังรันอยู่ จึงย้อนได้ทันที แลกกับการใช้ทรัพยากร 2 เท่า)

### ขั้นที่ 2: canary

ลบชุด blue/green ถอด `version` ออกจาก selector ของ Service แล้วสร้าง stable 4 + canary 1

```bash
kubectl -n release-lab delete deploy web-blue web-green && kubectl -n release-lab patch svc web --type=json -p '[{"op":"remove","path":"/spec/selector/version"}]' && kubectl -n release-lab get svc web -o jsonpath='{.spec.selector}{"\n"}' && kubectl apply -f lab09-release/web-stable.yaml -f lab09-release/web-canary.yaml && kubectl -n release-lab rollout status deploy/web-stable && kubectl -n release-lab rollout status deploy/web-canary && kubectl -n release-lab get pods -L track
```

```text
deployment.apps "web-blue" deleted from release-lab namespace
deployment.apps "web-green" deleted from release-lab namespace
service/web patched
{"app":"web"}
deployment.apps/web-stable created
deployment.apps/web-canary created
...
NAME                          READY   STATUS      RESTARTS   AGE   TRACK
client                        1/1     Running     0          27s   
web-canary-9f8b957d4-jdlck    1/1     Running     0          2s    canary
web-green-7547c8b9d9-94r9t    0/1     Completed   0          27s   
web-stable-5ff56dccfd-52vzh   1/1     Running     0          2s    stable
web-stable-5ff56dccfd-7ckzs   1/1     Running     0          2s    stable
web-stable-5ff56dccfd-fdmjp   1/1     Running     0          2s    stable
web-stable-5ff56dccfd-h2hgl   1/1     Running     0          2s    stable
```

(`web-green-...` ที่ `0/1 Completed` คือ Pod ของ Deployment ที่เพิ่งลบ กำลังหายไป) ยิง 50 ครั้งแล้วนับตาม track — ทำซ้ำหลายรอบ

```bash
kubectl -n release-lab exec client -- sh -c 'for i in $(seq 50); do wget -qO- -T 2 http://web; done' | awk '{print $2}' | sort | uniq -c
```

```text
      5 canary
     45 stable
```

ผลจริง 7 รอบ (50 ครั้ง/รอบ) ได้ canary **5, 6, 7, 9, 12, 11, 3** ครั้ง แกว่งมากเพราะ kube-proxy เลือกแบบสุ่มต่อ connection เมื่อยิง 500 ครั้งได้ canary **101 ครั้ง (20.2%)** และ stable 4 ตัวได้ 81–108 ครั้งต่อตัว ใกล้สัดส่วน 1 ใน 5 ที่คาด

ทางเลือกแทน `patch --type=json` คือ apply Service ที่ไม่มี `version` ตั้งแต่แรก

```bash
kubectl apply -f lab09-release/web-svc-all.yaml && kubectl -n release-lab get svc web -o jsonpath='{.spec.selector}{"\n"}'
```

```text
service/web configured
{"app":"web"}
```

### ขั้นที่ 3: เก็บกวาด

```bash
time kubectl delete ns release-lab
```

```text
namespace "release-lab" deleted

real	0m10.562s
```

### สิ่งที่เห็น

- blue/green: สลับ selector ของ Service ทีเดียว ลูกค้าย้ายทั้งหมดภายในไม่ถึง 1 วินาที (รอ 1–2 วินาทีก่อนทดสอบ) ย้อนได้ทันที
- canary: แบ่งตามจำนวน Pod 50 ครั้งแกว่ง 3–12 ครั้ง 500 ครั้งได้ 20.2%

**คำถามชวนคิด**

1. ถ้าอยากให้ canary ได้ลูกค้าราว 10% ด้วยวิธีนี้ ต้องตั้ง replicas ของ stable และ canary อย่างไร และมีข้อจำกัดอะไร
2. blue/green ในบทนี้ใช้ Deployment สองตัว ถ้าใช้ Deployment ตัวเดียวแบบ RollingUpdate จะได้ข้อดีข้อใดของ blue/green และเสียข้อใด

---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริง

**เป้าหมาย:** แปลงร้านของบทที่ 6 (ReplicaSet + Service) เป็น Deployment **โดยไม่เปลี่ยนชื่อ Service** แล้วเปลี่ยนรุ่น 1.2 → 1.3, ย้อนรุ่น, เจอรุ่นพัง 1.4, scale และ restart โดยร้านไม่สะดุด พิสูจน์ด้วยตัวเลขจาก `hit.sh` และหน้าร้านจริงใน browser แล้วปิดท้ายด้วยปัญหาข้อมูลหายที่ยังเหลือ

**ต้องมีก่อน:** LAB 0 (image `som-shop-web:1.2`/`1.3` และ postgres อยู่บน Node) และ **ลบ namespace `zdt-lab` ของ LAB 7 แล้ว** (30080 ว่าง)

### 10.1 สถาปัตยกรรมและไฟล์

{{FIG:L14|LAB 10 สถาปัตยกรรมเป้าหมาย}}

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-<hash>-a  Pod som-web-<hash>-b  Pod som-web-<hash>-c   (Deployment som-web, replicas 3→5,
   │                                                                RollingUpdate maxSurge 1 / maxUnavailable 0,
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop    preStop sleep 5, minReadySeconds 3)
                                   ▼
                    Service som-db (ClusterIP, 5432)
                                   ▼
                    Pod som-db-... (Deployment som-db, replicas 1, Recreate, emptyDir)
```

**ตาราง LAB 10** ไฟล์ใน `som-shop-v3/`

| ไฟล์ | เนื้อหา |
|---|---|
| `k8s-rs/00-namespace.yaml` | namespace `som-shop` (Pod Security `warn: restricted`) — สำเนาจากบทที่ 6 |
| `k8s-rs/10-db.yaml` | **ReplicaSet** `som-db` 1 ตัว (postgres:17.11-alpine, `emptyDir`, readiness `pg_isready`) + Service ClusterIP `som-db:5432` — สำเนาจากบทที่ 6 (แก้แค่คอมเมนต์) |
| `k8s-rs/20-web.yaml` | **ReplicaSet** `som-web` 3 ตัว `som-shop-web:1.2` (initContainers `wait-for-db` + `db-seed`, readiness `/api/health`, liveness `/api/live`, footer `LAB 006`, ไม่มี preStop) + Service NodePort `som-web` 30080 |
| `k8s/10-db.yaml` | **Deployment** `som-db` ชื่อ/selector เดิม `replicas: 1`, `strategy: Recreate` Pod spec เหมือน ReplicaSet เดิมทุกตัวอักษร + Service `som-db` เดิม |
| `k8s/20-web.yaml` | **Deployment** `som-web` ชื่อ/selector เดิม `replicas: 3`, `revisionHistoryLimit: 5`, `progressDeadlineSeconds: 60`, `minReadySeconds: 3`, `maxSurge: 1`/`maxUnavailable: 0`, annotation `kubernetes.io/change-cause: "1.2 แปลงเป็น Deployment"`, footer `LAB 007` และ **เพิ่ม** `lifecycle.preStop.sleep.seconds: 5` + Service `som-web` เดิม |
| `hit.sh` | สำเนาจากบทที่ 6 (ดู LAB 7) |
| `app/` | สำเนาแอป Next.js จากบทที่ 6 (โค้ดไม่แก้) |

ส่วนที่เปลี่ยนใน `k8s/20-web.yaml` เทียบกับ `k8s-rs/20-web.yaml` (ไฟล์จริง ตัดบางส่วน)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: som-web
  namespace: som-shop
  labels:
    app: som-web
  annotations:
    kubernetes.io/change-cause: "1.2 แปลงเป็น Deployment"
spec:
  replicas: 3
  revisionHistoryLimit: 5          # เก็บ ReplicaSet รุ่นเก่าไว้ย้อนได้ 5 รุ่น
  progressDeadlineSeconds: 60      # rollout ไม่คืบหน้าเกิน 60 วิ = ล้มเหลว (เห็นในขั้นรุ่นพัง 1.4)
  minReadySeconds: 3               # Pod ใหม่ต้องพร้อมต่อเนื่อง 3 วิ ถึงนับว่าใช้ได้
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                  # เปิดบูธใหม่เกินได้ 1 ตัว
      maxUnavailable: 0            # ห้ามบูธที่พร้อมลดลงเลย → ลูกค้าไม่เจอร้านว่าง
  selector:
    matchLabels:
      app: som-web
  template:
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: web
          image: som-shop-web:1.2
          lifecycle:
            preStop:                 # ถูกสั่งปิดแล้วยังเสิร์ฟต่อ 5 วิ ระหว่างที่ทุก Node ลบบูธนี้ออกจากรายชื่อ
              sleep:
                seconds: 5
```

> ไฟล์จริงมี initContainers, securityContext, env และ probe ครบเหมือนบทที่ 6 ดูทั้งไฟล์ด้วย `cat k8s/20-web.yaml` หรือเทียบความต่างด้วย `diff k8s-rs/20-web.yaml k8s/20-web.yaml`

ใช้ **3 หน้าต่าง** ใน LAB นี้ ทุกหน้าต่าง `cd` ไปที่โฟลเดอร์ร้าน

```bash
cd /workspace/007_kubernetes_deployment/02_LAB/som-shop-v3
```

- **terminal 1:** `hit.sh` นับ ok/err
- **terminal 2:** คำสั่งเปลี่ยนรุ่น
- **terminal 3:** เฝ้าดู (`get rs -w` / `get pods -w`) ตามที่บอกในแต่ละขั้น

### 10.2 เริ่มจากสภาพบทที่ 6

{{FIG:L15|LAB 10 เริ่มจากสภาพบทที่ 6}}

🐧 **terminal 2**

```bash
kubectl apply -f k8s-rs/ && time kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=120s && kubectl -n som-shop get rs,pods,svc
```

```text
namespace/som-shop created
replicaset.apps/som-db created
service/som-db created
replicaset.apps/som-web created
service/som-web created
pod/som-web-gw6mc condition met
pod/som-web-kw4z6 condition met
pod/som-web-x4jkt condition met

real	0m8.235s
...
NAME                      DESIRED   CURRENT   READY   AGE
replicaset.apps/som-db    1         1         1       8s
replicaset.apps/som-web   3         3         3       8s

NAME                READY   STATUS    RESTARTS   AGE
pod/som-db-sdznc    1/1     Running   0          8s
pod/som-web-gw6mc   1/1     Running   0          8s
pod/som-web-kw4z6   1/1     Running   0          8s
pod/som-web-x4jkt   1/1     Running   0          8s

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/som-db    ClusterIP   10.96.177.9    <none>        5432/TCP       8s
service/som-web   NodePort    10.96.194.40   <none>        80:30080/TCP   8s
```

🌐 **browser** เปิด **http://localhost:30080** จะเห็นร้านธีม harbor ป้าย "เวอร์ชัน 1.2" แถบ "เสิร์ฟโดย Pod: som-web-gw6mc · เวอร์ชัน 1.2" (ชื่อ Pod ของ ReplicaSet ไม่มี hash) และท้ายหน้า `Kubernetes LAB 006`

สั่งซื้อ 2 ออเดอร์ (กดปุ่ม "สั่งซื้อ" บนหน้าเว็บก็ได้ หรือใช้ API) แล้วดูการกระจายและยอดออเดอร์

```bash
for p in 1 4; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":2}"; echo; done
./hit.sh && for i in $(seq 6); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":2,"product":{"id":4,"name_th":"อาหารเปียกปลาซาบะ 85 ก.","stock":58}}
จำนวน  Pod  เวอร์ชัน
     22 som-web-gw6mc 1.2
     19 som-web-kw4z6 1.2
     19 som-web-x4jkt 1.2
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
      2 som-web-gw6mc 1.2 orders=2 products=6
      2 som-web-kw4z6 1.2 orders=2 products=6
      2 som-web-x4jkt 1.2 orders=2 products=6
```

นี่คือร้านเดียวกับท้ายบทที่ 6 ถ้าจะเปลี่ยนเป็น 1.3 ตอนนี้ต้องลบ Pod เอง ขั้นต่อไปจะให้ผู้จัดการร้านมาดูแลแทน

### 10.3 แปลง db เป็น Deployment: รับเลี้ยงทันที ไม่สร้างใหม่

**terminal 1** — ยิง `/api/whoami` (ไม่แตะ db) วนไว้ระหว่างแปลง

```bash
./hit.sh -q http://localhost:30080/api/whoami 400
```

**terminal 2**

```bash
kubectl apply -f k8s/10-db.yaml && time kubectl -n som-shop rollout status deploy/som-db
kubectl -n som-shop get deploy,rs,pods -l app=som-db --show-labels; kubectl -n som-shop get rs som-db -o jsonpath="{.metadata.ownerReferences}{\"\n\"}"; kubectl -n som-shop rollout history deploy/som-db
for i in 1 2 3; do curl -s localhost:30080/api/stats; done
```

```text
deployment.apps/som-db created
service/som-db unchanged
deployment "som-db" successfully rolled out

real	0m0.040s
...
NAME                     READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/som-db   1/1     1            1           48s   app=som-db

NAME                     DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/som-db   1         1         1       80s   app=som-db

NAME               READY   STATUS    RESTARTS   AGE   LABELS
pod/som-db-sdznc   1/1     Running   0          80s   app=som-db
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"som-db","uid":"e30639ab-de6f-45ce-bcce-f0478aa5e658"}]
deployment.apps/som-db 
REVISION  CHANGE-CAUSE
1         <none>

som-web-x4jkt 1.2 orders=2 products=6
som-web-gw6mc 1.2 orders=2 products=6
som-web-x4jkt 1.2 orders=2 products=6
```

ผลจริงใน terminal 1: `ok=400 err=0`

- template ของ `k8s/10-db.yaml` **เหมือน ReplicaSet เดิมทุกตัวอักษร** (`strategy: Recreate` อยู่นอก template) Deployment จึงรับเลี้ยง RS `som-db` เป็น **รุ่นปัจจุบัน** ทันที (`rollout status` 0.04 วินาที) แบบเดียวกับ LAB 8 ขั้นที่ 4
- Pod `som-db-sdznc` **ตัวเดิม ไม่ถูกสร้างใหม่** ข้อมูลใน `emptyDir` จึงยังอยู่ (`orders=2`) ไม่มีช่วงร้านล่ม และไม่มีหน้า 503
- `Recreate` จะมีผลเมื่อเกิด rollout ครั้งถัดไปของ `som-db` (สาธิตใน [10.11](#1011-เสริม-recreate-ของ-som-db-ของจริง))

### 10.4 แปลง web เป็น Deployment ระหว่างขาย

{{FIG:L16|LAB 10 แปลงร้านเป็น Deployment}}

**terminal 1**

```bash
./hit.sh -q http://localhost:30080/api/whoami 300
```

**terminal 3**

```bash
kubectl -n som-shop get rs -w
```

**terminal 2**

```bash
kubectl apply -f k8s/20-web.yaml && time kubectl -n som-shop rollout status deploy/som-web
```

```text
deployment.apps/som-web created
service/som-web unchanged
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out

real	0m17.724s
```

ผลจริงใน terminal 3 (เติมเวลาหน้าบรรทัด ตัดบรรทัดซ้ำ)

```text
10:29:53 som-web   3         3         3       91s
10:29:56 som-web-7955fccc94   1         0         0       0s
10:29:59 som-web-7955fccc94   1         1         1       3s
10:30:02 som-web              2         3         3       100s
10:30:02 som-web-7955fccc94   2         1         1       6s
10:30:02 som-web              2         2         2       100s
10:30:05 som-web-7955fccc94   2         2         2       9s
10:30:08 som-web              1         2         2       106s
10:30:08 som-web-7955fccc94   3         2         2       12s
10:30:08 som-web              1         1         1       106s
10:30:11 som-web-7955fccc94   3         3         3       15s
10:30:14 som-web              0         1         1       112s
10:30:14 som-web              0         0         0       112s
```

ผลจริงใน terminal 1

```text
..................................................................................x.......................................................x.................................................................................................................................................................
ข้อความ error:
      2 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 6.1 วินาที
ok=298 err=2 (ใช้เวลา 32.5 วินาที)
```

- RS `som-web` เดิมถูกรับเลี้ยงแล้ว scale 3→2→1→0 สลับกับ `som-web-7955fccc94` 0→1→2→3 ห่างกันขั้นละราว 6 วินาที (Pod ใหม่ ready ~3 วินาที + `minReadySeconds: 3`)
- **อาจเห็น error 1–2 ครั้ง** (ผลจริง 2/300 และในรอบทดสอบซ้ำ 1/300) เพราะบูธที่ถูกปิดในขั้นนี้คือ **Pod เดิมของ ReplicaSet บทที่ 6 ซึ่งยังไม่มี preStop** หลังจากนี้ทุกบูธเป็นของ Deployment ที่มี preStop แล้ว การเปลี่ยนรุ่นครั้งต่อ ๆ ไปจะได้ err 0
- ถ้ายิงหน้าแรก `/` พร้อมกัน (`./hit.sh -q http://localhost:30080/ 150 0.2` ใน terminal เพิ่ม) ผลจริงได้ 1/150 และ 0/150 ในสองรอบ

ตรวจผล

```bash
kubectl -n som-shop get deploy,rs,pods -o wide; kubectl -n som-shop get rs som-web -o jsonpath="{.metadata.ownerReferences}{\"\n\"}"; kubectl -n som-shop rollout history deploy/som-web
```

```text
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE    CONTAINERS   IMAGES                  SELECTOR
deployment.apps/som-db    1/1     1            1           115s   postgres     postgres:17.11-alpine   app=som-db
deployment.apps/som-web   3/3     3            3           52s    web          som-shop-web:1.2        app=som-web

NAME                                 DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                  SELECTOR
replicaset.apps/som-db               1         1         1       2m26s   postgres     postgres:17.11-alpine   app=som-db
replicaset.apps/som-web              0         0         0       2m26s   web          som-shop-web:1.2        app=som-web
replicaset.apps/som-web-7955fccc94   3         3         3       52s     web          som-shop-web:1.2        app=som-web,pod-template-hash=7955fccc94

NAME                           READY   STATUS    RESTARTS   AGE     IP             NODE          NOMINATED NODE   READINESS GATES
pod/som-db-sdznc               1/1     Running   0          2m26s   10.244.2.98    lab-worker    <none>           <none>
pod/som-web-7955fccc94-cgjqm   1/1     Running   0          46s     10.244.1.62    lab-worker2   <none>           <none>
pod/som-web-7955fccc94-m4f6r   1/1     Running   0          52s     10.244.2.101   lab-worker    <none>           <none>
pod/som-web-7955fccc94-vs9kw   1/1     Running   0          40s     10.244.2.102   lab-worker    <none>           <none>
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"Deployment","name":"som-web","uid":"f55bf804-9b63-48d8-9f57-5f2ab2ff3637"}]
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
1         1.2 แปลงเป็น Deployment
```

- Deployment `som-db 1/1`, `som-web 3/3` RS `som-web` เดิม `0 0 0` มีเจ้าของเป็น Deployment และโผล่ใน history เป็น **REVISION 0** ส่วน revision 1 ได้ CHANGE-CAUSE จาก annotation ในไฟล์ YAML
- **ไม่ต้องใช้ทางสำรอง `--cascade=orphan`** เพราะการรับเลี้ยงทำงานได้ (ถ้าวันหนึ่ง selector ไม่ตรง ใช้วิธีใน LAB 8 ขั้นที่ 5)
- Pod `som-db-sdznc` ตัวเดิมยังอยู่

### 10.5 สั่งซื้อเพิ่ม (ใช้พิสูจน์ในขั้นต่อไป)

```bash
for p in 5 6; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d "{\"product_id\":$p,\"qty\":1}"; echo; done; curl -s localhost:30080/api/stats
```

```text
{"ok":true,"order_id":3,"product":{"id":5,"name_th":"ขนมแมวเลียรสไก่ (แพ็ก 4)","stock":39}}
{"ok":true,"order_id":4,"product":{"id":6,"name_th":"ขนมฟรีซดรายแซลมอน 40 ก.","stock":24}}
som-web-7955fccc94-m4f6r 1.2 orders=4 products=6
```

ออเดอร์รวม **4** (2 ก่อนแปลง + 2 ตอนนี้) เพราะ db ไม่ถูกสร้างใหม่ตอนแปลง

🌐 refresh **http://localhost:30080** (Ctrl+F5) ชื่อ Pod ในแถบ "เสิร์ฟโดย Pod" มี hash แล้ว และท้ายหน้าเป็น `Kubernetes LAB 007 · namespace som-shop`

{{SS:20261005_1044_lab10deploy_01-shop-1.2-deployment.png|ภาพหน้าจอจริง ร้าน 1.2 หลังแปลงเป็น Deployment|ภาพหน้าจอจริงจากการทดลอง: เปิด http://localhost:30080 (NodePort โดยตรง) หลังแปลงร้านเป็น Deployment — ป้าย "เวอร์ชัน 1.2" แถบ "🐱 เสิร์ฟโดย Pod: som-web-7955fccc94-fjsv6 · เวอร์ชัน 1.2" ชื่อ Pod มี pod-template-hash แล้ว และออเดอร์ทั้งหมด 4 (ข้อมูลเดิมไม่หายเพราะ som-db ถูกรับเลี้ยงโดยไม่สร้าง Pod ใหม่)}}

> **หมายเหตุ:** หัวเว็บยังเขียน `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service` เพราะบทนี้ใช้แอปเดิมจากบทที่ 6 (ข้อความนี้ฝังอยู่ในโค้ดของแอป) แต่ร้านตอนนี้ดูแลด้วย Deployment แล้ว ดูได้จากชื่อ Pod ที่มี hash และ `kubectl -n som-shop get deploy`

### 10.6 rolling update 1.2 → 1.3 ระหว่างขาย

{{FIG:L17|LAB 10 rolling 1.2 → 1.3 ไม่มี error}}

**terminal 1**

```bash
./hit.sh -q http://localhost:30080/api/whoami 300
```

**terminal 3** (ดู Pod ที่กำลังปิด)

```bash
kubectl -n som-shop get pods -w
```

**terminal 2** — เปลี่ยน image ของทั้ง container `web` และ initContainer `db-seed` บันทึกเหตุผล แล้วจับเวลา

```bash
kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.3 ธีม sunset" --overwrite
time kubectl -n som-shop rollout status deploy/som-web
```

```text
deployment.apps/som-web image updated
deployment.apps/som-web annotated
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
```

ผลจริง: rollout ใช้ **18.1 วินาที** (รอบถ่ายภาพหน้าจอ 16.9 วินาที) และ terminal 1

```text
............................................................................................................................................................................................................................................................................................................
ok=300 err=0 (ใช้เวลา 32.5 วินาที)
```

**err = 0 จาก 300** (หน้าแรก `/` 150 ครั้งก็ err 0) ใน terminal 3 จะเห็น Pod เก่าขึ้น `Error` ราว 5 วินาทีหลัง `Terminating`

```text
10:31:11 som-web-7955fccc94-vs9kw   1/1     Terminating       0          63s
10:31:16 som-web-7955fccc94-vs9kw   0/1     Error             0          68s
10:31:17 som-web-7955fccc94-m4f6r   1/1     Terminating       0          81s
10:31:22 som-web-7955fccc94-m4f6r   0/1     Error             0          86s
```

นี่คือ preStop 5 วินาที แล้ว Next.js รับ SIGTERM และออกด้วย exit code ไม่เป็น 0 **ไม่ใช่ rollout พัง** ตรวจผล

```bash
kubectl -n som-shop rollout history deploy/som-web; kubectl -n som-shop get rs -o wide; kubectl -n som-shop get pods
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.initContainers[*].image}{" | "}{.spec.template.spec.containers[*].image}{"\n"}'
```

```text
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
1         1.2 แปลงเป็น Deployment
2         1.3 ธีม sunset

NAME                 DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                  SELECTOR
som-db               1         1         1       3m20s   postgres     postgres:17.11-alpine   app=som-db
som-web              0         0         0       3m20s   web          som-shop-web:1.2        app=som-web
som-web-7955fccc94   0         0         0       106s    web          som-shop-web:1.2        app=som-web,pod-template-hash=7955fccc94
som-web-ffc7b9f94    3         3         3       38s     web          som-shop-web:1.3        app=som-web,pod-template-hash=ffc7b9f94
NAME                      READY   STATUS    RESTARTS   AGE
som-db-sdznc              1/1     Running   0          3m20s
som-web-ffc7b9f94-dl8cm   1/1     Running   0          31s
som-web-ffc7b9f94-g88n9   1/1     Running   0          38s
som-web-ffc7b9f94-v5rnr   1/1     Running   0          25s
postgres:17.11-alpine som-shop-web:1.3 | som-shop-web:1.3
```

`set image` ใช้กับ initContainer ได้ (`db-seed` เป็น 1.3) ส่วน `wait-for-db` ยังเป็น postgres

{{FIG:L18|LAB 10 หน้าร้าน 1.3}}

🌐 **browser** กด **Ctrl+F5** ที่ http://localhost:30080 จะเห็นธีม sunset (ส้ม–ชมพู) แบนเนอร์ด้านบน `🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟` และแถบ `🐱 เสิร์ฟโดย Pod: som-web-ffc7b9f94-… · เวอร์ชัน 1.3` (ผลจริงจาก curl: `เสิร์ฟโดย Pod: som-web-ffc7b9f94-g88n9 · เวอร์ชัน 1.3` และ footer `Kubernetes LAB 007 · namespace som-shop`) ออเดอร์ยังเป็น 4 เพราะเปลี่ยนแค่ web

{{SS:20261005_1046_lab10deploy_02-shop-1.3-after-rolling-err0.png|ภาพหน้าจอจริง ร้าน 1.3 หลัง rolling err 0|ภาพหน้าจอจริงจากการทดลอง: หลัง set image 1.3 (rollout 16.9 วินาที ระหว่างนั้น hit.sh ok=300 err=0) หน้าร้านเป็นธีม sunset ป้าย "เวอร์ชัน 1.3" แบนเนอร์ "🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟" แถบ "เสิร์ฟโดย Pod: som-web-ffc7b9f94-scnkp · เวอร์ชัน 1.3" และออเดอร์ยังเป็น 4}}

### 10.7 rollout history และ undo สองครั้ง

{{FIG:L19|LAB 10 history และ undo}}

ทำเหมือนขั้นก่อน (terminal 1 ยิง `./hit.sh -q http://localhost:30080/api/whoami 300`) แล้วใน **terminal 2**

```bash
kubectl -n som-shop rollout undo deploy/som-web && kubectl -n som-shop rollout status deploy/som-web
kubectl -n som-shop rollout history deploy/som-web; for i in $(seq 6); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
Warning: resource deployments/som-web was previously managed with 'kubectl apply'. ...
deployment.apps/som-web rolled back
...
deployment "som-web" successfully rolled out
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
2         1.3 ธีม sunset
3         1.2 แปลงเป็น Deployment

      2 som-web-7955fccc94-5hkh9 1.2 orders=4 products=6
      2 som-web-7955fccc94-kbwrx 1.2 orders=4 products=6
      2 som-web-7955fccc94-q2nrb 1.2 orders=4 products=6
```

กลับเป็น 1.2 (RS `som-web-7955fccc94` เดิม) ใน 17.5 วินาที hit.sh `ok=300 err=0` ออเดอร์ **ยังเป็น 4** เพราะ undo เปลี่ยนแค่ web ไม่แตะ db และ schema ของสองรุ่นเข้ากันได้ undo อีกครั้ง (ไม่ระบุ revision = กลับไปรุ่นก่อนหน้า)

```bash
kubectl -n som-shop rollout undo deploy/som-web 2>&1 | grep -v ^Warning; kubectl -n som-shop rollout status deploy/som-web
kubectl -n som-shop rollout history deploy/som-web; for i in $(seq 6); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
deployment.apps/som-web rolled back
...
deployment "som-web" successfully rolled out
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
4         1.3 ธีม sunset

      6 som-web-ffc7b9f94-qtmdt 1.3 orders=4 products=6
```

กลับเป็น 1.3 ใน 18.2 วินาที err 0 อีกครั้ง เลข revision เลื่อนไปเรื่อย ๆ (`0, 2, 3` → `0, 3, 4`) และแต่ละ revision ได้ CHANGE-CAUSE ของรุ่นเป้าหมาย

### 10.8 รุ่นพัง 1.4: rollout ค้างแต่ร้านยังขาย

{{FIG:L20|LAB 10 รุ่นพัง 1.4 แต่ร้านยังขาย}}

`som-shop-web:1.4` **ไม่มีจริง** (ตั้งใจให้พัง) เปลี่ยนเฉพาะ container `web` (`db-seed` ยังเป็น 1.3)

**terminal 1** — ยิงนานขึ้นให้ครอบช่วง deadline 60 วินาที

```bash
./hit.sh -q http://localhost:30080/api/whoami 700
```

**terminal 2**

```bash
kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.4 && kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.4 (ทดสอบรุ่นพัง)" --overwrite && sleep 8 && kubectl -n som-shop get pods && kubectl -n som-shop get deploy som-web
time kubectl -n som-shop rollout status deploy/som-web; echo "exit=$?"
```

```text
deployment.apps/som-web image updated
deployment.apps/som-web annotated
NAME                       READY   STATUS            RESTARTS   AGE
som-db-sdznc               1/1     Running           0          4m54s
som-web-6cd4d5d687-dqh9r   0/1     PodInitializing   0          8s
som-web-ffc7b9f94-k896q    1/1     Running           0          35s
som-web-ffc7b9f94-qtmdt    1/1     Running           0          41s
som-web-ffc7b9f94-vdmf6    1/1     Running           0          48s
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
som-web   3/3     1            3           3m20s
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
error: deployment "som-web" exceeded its progress deadline
exit=1
```

- 8 วินาทีแรก Pod ใหม่เป็น **`PodInitializing`** (initContainer `wait-for-db` และ `db-seed` 1.3 รันผ่าน) แล้วค่อยเป็น `ErrImagePull`/`ImagePullBackOff` ตอนดึง image ของ container หลัก
- `rollout status` จบด้วย `exceeded its progress deadline` และ **exit 1** ราว 60 วินาทีหลัง `set image` (`progressDeadlineSeconds: 60`)
- terminal 1 ผลจริง `ok=700 err=0 (ใช้เวลา 75.7 วินาที)` (หน้าแรก `/` 350 ครั้งก็ err 0)

ดูอาการและสั่งซื้อระหว่างรุ่นพัง

```bash
kubectl -n som-shop get deploy som-web; kubectl -n som-shop get pods; kubectl -n som-shop get rs
kubectl -n som-shop get deploy som-web -o jsonpath='{range .status.conditions[*]}{.type}={.status} {.reason}: {.message}{"\n"}{end}'
P=$(kubectl -n som-shop get pods -l app=som-web --no-headers | awk "\$2==\"0/1\"{print \$1}"); kubectl -n som-shop describe pod $P | sed -n "/^Events/,\$p"
curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":2,"qty":1}'; echo; kubectl -n som-shop rollout history deploy/som-web
```

```text
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
som-web   3/3     1            3           4m33s
NAME                       READY   STATUS             RESTARTS   AGE
som-db-sdznc               1/1     Running            0          6m7s
som-web-6cd4d5d687-dqh9r   0/1     ImagePullBackOff   0          81s
som-web-ffc7b9f94-k896q    1/1     Running            0          108s
som-web-ffc7b9f94-qtmdt    1/1     Running            0          114s
som-web-ffc7b9f94-vdmf6    1/1     Running            0          2m1s
NAME                 DESIRED   CURRENT   READY   AGE
som-db               1         1         1       6m7s
som-web              0         0         0       6m7s
som-web-6cd4d5d687   1         1         0       81s
som-web-7955fccc94   0         0         0       4m33s
som-web-ffc7b9f94    3         3         3       3m25s
Available=True MinimumReplicasAvailable: Deployment has minimum availability.
Progressing=False ProgressDeadlineExceeded: ReplicaSet "som-web-6cd4d5d687" has timed out progressing.
Events:
  ...
  Normal   Started    79s                kubelet            spec.initContainers{db-seed}: Container started
  Normal   Pulling    35s (x3 over 78s)  kubelet            spec.containers{web}: Pulling image "som-shop-web:1.4"
  Warning  Failed     33s (x3 over 76s)  kubelet            spec.containers{web}: Failed to pull image "som-shop-web:1.4": failed to pull and unpack image "docker.io/library/som-shop-web:1.4": failed to resolve reference "docker.io/library/som-shop-web:1.4": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Warning  Failed     33s (x3 over 76s)  kubelet            spec.containers{web}: Error: ErrImagePull
  Normal   BackOff    8s (x3 over 50s)   kubelet            spec.containers{web}: Back-off pulling image "som-shop-web:1.4"
  Warning  Failed     8s (x3 over 50s)   kubelet            spec.containers{web}: Error: ImagePullBackOff
{"ok":true,"order_id":5,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":14}}
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
4         1.3 ธีม sunset
5         1.4 (ทดสอบรุ่นพัง)
```

`READY 3/3 UP-TO-DATE 1 AVAILABLE 3`: `maxUnavailable: 0` ไม่ยอมปิดบูธ 1.3 จนกว่าบูธ 1.4 จะพร้อม (ซึ่งไม่มีวัน) ร้านจึงยังเป็น 1.3 และ **สั่งซื้อได้** (`order_id 5`) Kubernetes ตั้ง `ProgressDeadlineExceeded` แต่ไม่ย้อนรุ่นให้ ต้องสั่งเอง

{{SS:20261005_1047_lab10deploy_03-broken-1.4-shop-still-selling.png|ภาพหน้าจอจริง รุ่นพัง 1.4 ร้านยังขาย|ภาพหน้าจอจริงจากการทดลอง: ระหว่างที่ set image เป็น 1.4 (ไม่มี image จริง) Pod ใหม่ค้าง ErrImagePull และ Deployment เป็น READY 3/3 UP-TO-DATE 1 AVAILABLE 3 — หน้าร้านยังเป็นเวอร์ชัน 1.3 (เสิร์ฟโดย Pod: som-web-ffc7b9f94-7m6wn) และยังสั่งซื้อได้ ออเดอร์เพิ่มเป็น 5 จากนั้น rollout status แจ้ง exceeded its progress deadline (exit 1) แล้วจึงสั่ง rollout undo}}

**terminal 2** — undo (terminal 1 ยิง `./hit.sh -q http://localhost:30080/api/whoami 300` อีกรอบ)

```bash
kubectl -n som-shop rollout undo deploy/som-web 2>&1 | grep -v ^Warning; kubectl -n som-shop rollout status deploy/som-web
kubectl -n som-shop get pods; kubectl -n som-shop rollout history deploy/som-web
```

```text
deployment.apps/som-web rolled back
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
NAME                      READY   STATUS    RESTARTS   AGE
som-db-sdznc              1/1     Running   0          6m47s
som-web-ffc7b9f94-k896q   1/1     Running   0          2m28s
som-web-ffc7b9f94-qtmdt   1/1     Running   0          2m34s
som-web-ffc7b9f94-vdmf6   1/1     Running   0          2m41s
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
5         1.4 (ทดสอบรุ่นพัง)
6         1.3 ธีม sunset
```

undo จาก 1.4 กลับ 1.3 ใช้แค่ **0.1 วินาที** (RS 1.3 ยังพร้อมครบ แค่ลบ Pod 1.4 ที่พัง) และ hit.sh ระหว่าง undo ได้ `ok=300 err=0` ส่วนรอบถ่ายภาพหน้าจอซึ่งไม่ได้ทำขั้น 10.7 ได้ history หลังขั้นนี้เป็น `0, 1, 3, 4` (เลข revision ขึ้นกับลำดับคำสั่งที่ทำมา)

### 10.9 scale 3 → 5

{{FIG:L21|LAB 10 scale 3 → 5}}

```bash
kubectl -n som-shop scale deploy/som-web --replicas=5 && time kubectl -n som-shop rollout status deploy/som-web && kubectl -n som-shop get pods -o wide
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web; kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'; kubectl -n som-shop rollout history deploy/som-web
./hit.sh
```

```text
deployment.apps/som-web scaled
Waiting for deployment "som-web" rollout to finish: 3 out of 5 new replicas have been updated...
Waiting for deployment "som-web" rollout to finish: 3 of 5 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m5.405s
NAME                      READY   STATUS    RESTARTS   AGE     IP             NODE          NOMINATED NODE   READINESS GATES
som-db-sdznc              1/1     Running   0          6m58s   10.244.2.98    lab-worker    <none>           <none>
som-web-ffc7b9f94-7784v   1/1     Running   0          6s      10.244.1.66    lab-worker2   <none>           <none>
som-web-ffc7b9f94-9p8n7   1/1     Running   0          6s      10.244.2.110   lab-worker    <none>           <none>
som-web-ffc7b9f94-k896q   1/1     Running   0          2m39s   10.244.2.108   lab-worker    <none>           <none>
som-web-ffc7b9f94-qtmdt   1/1     Running   0          2m45s   10.244.1.65    lab-worker2   <none>           <none>
som-web-ffc7b9f94-vdmf6   1/1     Running   0          2m52s   10.244.2.107   lab-worker    <none>           <none>
NAME            ADDRESSTYPE   PORTS   ENDPOINTS                                           AGE
som-web-9sxgw   IPv4          3000    10.244.2.107,10.244.1.65,10.244.2.108 + 2 more...   6m58s
10.244.2.107 som-web-ffc7b9f94-vdmf6 ready=true
10.244.1.65 som-web-ffc7b9f94-qtmdt ready=true
10.244.2.108 som-web-ffc7b9f94-k896q ready=true
10.244.2.110 som-web-ffc7b9f94-9p8n7 ready=true
10.244.1.66 som-web-ffc7b9f94-7784v ready=true
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
5         1.4 (ทดสอบรุ่นพัง)
6         1.3 ธีม sunset
จำนวน  Pod  เวอร์ชัน
     15 som-web-ffc7b9f94-7784v 1.3
      9 som-web-ffc7b9f94-9p8n7 1.3
     11 som-web-ffc7b9f94-k896q 1.3
     12 som-web-ffc7b9f94-qtmdt 1.3
     13 som-web-ffc7b9f94-vdmf6 1.3
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
```

- 5 บูธพร้อมใน 5.4 วินาที EndpointSlice มี 5 endpoint `ready=true` เอง (คอลัมน์ ENDPOINTS แสดงแค่ 3 IP แล้ว `+ 2 more...` จึงดูด้วย jsonpath)
- `rollout history` **ไม่มี revision ใหม่** (scale ไม่แตะ template) และ hit.sh เห็นครบ 5 บูธ
- ทรัพยากรพอ ไม่มี Pod `Pending` (5 web + 1 surge ระหว่าง rollout + 1 db)

### 10.10 ลบ Pod db แล้วเติมสินค้าด้วย rollout restart

{{FIG:L22|LAB 10 ลบ Pod db แล้ว rollout restart}}

Deployment สร้าง Pod db แทนให้ได้ แต่ข้อมูลอยู่ใน `emptyDir` ของ Pod เดิม

```bash
kubectl -n som-shop get pod -l app=som-db -o wide; kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=60s; kubectl -n som-shop get pod -l app=som-db -o wide; kubectl -n som-shop get rs -l app=som-db
```

```text
NAME           READY   STATUS    RESTARTS   AGE     IP            NODE         NOMINATED NODE   READINESS GATES
som-db-sdznc   1/1     Running   0          7m12s   10.244.2.98   lab-worker   <none>           <none>
pod "som-db-sdznc" deleted from som-shop namespace
pod/som-db-66sc7 condition met
NAME           READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-db-66sc7   1/1     Running   0          4s    10.244.1.67   lab-worker2   <none>           <none>
NAME     DESIRED   CURRENT   READY   AGE
som-db   1         1         1       7m16s
```

Pod db ใหม่ (`som-db-66sc7`) พร้อมใน 4.4 วินาที คนละ Node คนละ IP แต่ Service `som-db` ชื่อเดิม (ReplicaSet `som-db` ที่ถูกรับเลี้ยงเป็นผู้สร้าง) ดูหน้าร้านและฐานข้อมูล

```bash
sleep 2; curl -s -o /dev/null -w '%{http_code}\n' localhost:30080; curl -s localhost:30080/api/health; echo; curl -s localhost:30080/api/stats; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c 'select count(*) from orders'
for i in 1 2 3 4 5 6; do echo "$(date +%T) code=$(curl -s -m 2 -o /dev/null -w '%{http_code}' localhost:30080) health=$(curl -s -m 2 localhost:30080/api/health)"; sleep 1; done; kubectl -n som-shop get pods -l app=som-web; curl -s localhost:30080/api/stats; kubectl -n som-shop get events --sort-by=.lastTimestamp | grep -i -E 'unhealthy|readiness' | tail -5
```

```text
000

ERROR:  relation "orders" does not exist
LINE 1: select count(*) from orders
                             ^
command terminated with exit code 1
10:35:46 code=503 health={"ok":true,"db":"up"}
10:35:47 code=503 health={"ok":true,"db":"up"}
...
10:35:51 code=503 health={"ok":true,"db":"up"}
NAME                      READY   STATUS    RESTARTS   AGE
som-web-ffc7b9f94-7784v   1/1     Running   0          38s
...
som-web-ffc7b9f94-k896q 1.3 db-not-ready
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-vdmf6     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-qtmdt     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-9p8n7     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-k896q     Readiness probe failed: HTTP probe failed with statuscode: 503
14s         Warning   Unhealthy           pod/som-web-ffc7b9f94-7784v     Readiness probe failed: HTTP probe failed with statuscode: 503
```

- ช่วงแรก **2–5 วินาที เปิดหน้าเว็บไม่ได้เลย** (`curl` ได้ code `000`) เพราะ readiness ของ web ทุกตัวล้มพร้อมกันตอน db หาย (Event `statuscode: 503` ทั้ง 5 Pod) endpoint จึงว่างชั่วครู่ browser อาจขึ้นหน้า error ก่อน
- จากนั้น db ใหม่ตอบแล้ว (`/api/health` = `{"ok":true,"db":"up"}`) web กลับมา ready แต่หน้าแรกได้ **503** "ร้านกำลังเตรียมสินค้า" เพราะ db ใหม่ **ว่างเปล่า** ไม่มีตาราง `orders` (`relation "orders" does not exist`) web ไม่มีตัวไหนถูก restart (liveness ไม่พึ่ง db)

initContainer `db-seed` (สร้างตาราง + สินค้า) รันเฉพาะตอน Pod เกิด บทที่ 6 ต้องลบ Pod web เอง บทนี้ใช้ **`rollout restart`** ให้ผู้จัดการร้านทยอยสร้างบูธใหม่ตามกติกา zero-downtime (terminal 1 ยิง `./hit.sh -q http://localhost:30080/api/whoami 300`)

```bash
kubectl -n som-shop rollout restart deploy/som-web && time kubectl -n som-shop rollout status deploy/som-web
for i in $(seq 10); do curl -s localhost:30080/api/stats; done | sort | uniq -c; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c "select count(*) from orders"; kubectl -n som-shop rollout history deploy/som-web; P=$(kubectl -n som-shop get pods -l app=som-web -o name | head -1); kubectl -n som-shop logs $P -c db-seed
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 1 out of 5 new replicas have been updated...
...
deployment "som-web" successfully rolled out
      4 som-web-7cbbcddf4-559c2 1.3 orders=0 products=6
      1 som-web-7cbbcddf4-5z79n 1.3 orders=0 products=6
      1 som-web-7cbbcddf4-6cgfv 1.3 orders=0 products=6
      2 som-web-7cbbcddf4-hg9gh 1.3 orders=0 products=6
      2 som-web-7cbbcddf4-rtplg 1.3 orders=0 products=6
 count 
-------
     0
(1 row)

deployment.apps/som-web 
REVISION  CHANGE-CAUSE
0         <none>
3         1.2 แปลงเป็น Deployment
5         1.4 (ทดสอบรุ่นพัง)
6         1.3 ธีม sunset
7         1.3 ธีม sunset

connected to database
got seed lock 5005
tables ready: products, orders
seeded 6 products (new: 6)
```

- rollout restart 5 replicas ใช้ **32.9 วินาที** `/api/whoami` ได้ `ok=300 err=0`
- ถ้ายิงหน้าแรก `/` พร้อมกัน ผลจริง `ok=125 err=25` (`The requested URL returned error: 503` ในช่วง 5.1 วินาทีแรก) — ร้าน 503 อยู่แล้วก่อน restart และหายทันทีที่บูธใหม่ตัวแรก seed ตารางเสร็จ (ไม่ใช่ error จากการ rollout)
- ร้านกลับมาขายได้ แต่ **ออเดอร์ = 0** (เดิม 5) revision 7 สืบทอด change-cause `1.3 ธีม sunset` (ลืม annotate)

### 10.11 (เสริม) Recreate ของ som-db ของจริง

ตอนแปลง db (ขั้น 10.3) ไม่เกิด Recreate เพราะ template เหมือนเดิม ถ้าอยากเห็นลำดับ "ปิดก่อนเปิด" ของจริง ใช้ `rollout restart` กับ `som-db`

**terminal 3** — `kubectl -n som-shop get pods -w`

**terminal 2**

```bash
curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":1}'; echo
kubectl -n som-shop rollout restart deploy/som-db && time kubectl -n som-shop rollout status deploy/som-db
kubectl -n som-shop get rs -l app=som-db; kubectl -n som-shop rollout history deploy/som-db
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
deployment.apps/som-db restarted
Waiting for deployment "som-db" rollout to finish: 0 out of 1 new replicas have been updated...
...
Waiting for deployment "som-db" rollout to finish: 0 of 1 updated replicas are available...
deployment "som-db" successfully rolled out
NAME                DESIRED   CURRENT   READY   AGE
som-db              0         0         0       9m2s
som-db-786556dc4f   1         1         1       32s
deployment.apps/som-db 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

ผลจริงใน terminal 3 (เติมเวลาหน้าบรรทัด)

```text
10:36:51 som-db-66sc7   1/1     Terminating   0          77s
10:36:52 som-db-66sc7   0/1     Completed     0          78s
10:36:52 som-db-786556dc4f-ljl5d   0/1     Pending       0          0s
10:36:52 som-db-786556dc4f-ljl5d   0/1     ContainerCreating   0          0s
10:36:52 som-db-786556dc4f-ljl5d   0/1     Running             0          0s
10:36:56 som-db-786556dc4f-ljl5d   1/1     Running             0          4s
10:36:54 som-web-7cbbcddf4-559c2   0/1     Running           0          51s
...
10:36:58 som-web-7cbbcddf4-559c2   1/1     Running           0          54s
```

- Pod db เก่า `Completed` **ก่อน** แล้ว Pod db ใหม่จึงเกิด (rollout 4.3 วินาที) ไม่มีช่วงที่มี db 2 ตัว = Recreate ทำงานตามที่ออกแบบ RS `som-db` เดิมเหลือ 0 และได้ RS ใหม่ `som-db-786556dc4f` (revision 2)
- web 4 ใน 5 ตัว `0/1` ชั่วครู่ระหว่างไม่มี db `/api/whoami` ยัง 300/300 แต่หน้าแรกเป็น 503 (ผลจริง `ok=14 err=136` จาก 150) จนกว่าจะเติมสินค้าใหม่ และออเดอร์ที่เพิ่งสั่ง (`order_id 1`) หายไปพร้อม Pod db เก่า

```bash
kubectl -n som-shop rollout restart deploy/som-web >/dev/null && kubectl -n som-shop rollout status deploy/som-web >/dev/null && curl -s -o /dev/null -w "%{http_code}\n" localhost:30080 && curl -s localhost:30080/api/stats
```

```text
200
som-web-7cbbcddf4-559c2 1.3 orders=0 products=6
```

### 10.12 สรุป LAB 10 และปัญหาที่ส่งต่อ

{{FIG:L23|สรุป LAB สุดท้าย}}

**ตารางสรุป** สิ่งที่ Deployment แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| ย้ายจาก ReplicaSet โดยไม่เปลี่ยนชื่อ Service | db ถูกรับเลี้ยงทันที (ไม่สร้างใหม่ ข้อมูลอยู่), web รับเลี้ยงแล้วแทนทีละบูธ err 1–2/300 (บูธเดิมไม่มี preStop) | ✅ Deployment (บทนี้) |
| เปลี่ยนรุ่นระหว่างขายโดยลูกค้าไม่เจอ error | rolling 1.2→1.3 18.1 วินาที err 0/300 | ✅ RollingUpdate + readiness + maxUnavailable 0 + preStop |
| สมุดประวัติและย้อนรุ่น | `rollout history` มี CHANGE-CAUSE, undo สองครั้ง err 0 ออเดอร์อยู่ครบ | ✅ `rollout history/undo` |
| รุ่นพังแต่ร้านยังขาย | 1.4 `ImagePullBackOff` + `ProgressDeadlineExceeded` แต่ hit.sh 700/700 และสั่งซื้อได้ | ✅ maxUnavailable 0 + progressDeadlineSeconds (คนต้อง undo เอง) |
| ปรับจำนวนบูธ | scale 3→5 ใน 5.4 วินาที ไม่มี revision ใหม่ | ✅ (สั่งเอง) → ปรับอัตโนมัติด้วย HPA (บทหลัง) |
| ห้ามมี db สองตัว | `rollout restart deploy/som-db` ปิดก่อนเปิด | ✅ Recreate |
| ข้อมูล db คงอยู่เมื่อ Pod db เกิดใหม่ | ลบ Pod db / Recreate แล้ว `relation "orders" does not exist` ออเดอร์ 0 | ❌ → **PersistentVolume/PVC/StatefulSet (บทถัดไป)** |
| รหัสผ่านไม่อยู่ใน YAML | `meow1234` ยังเขียนตรง ๆ ใน `k8s/*.yaml` | ❌ → ConfigMap/Secret (บทหลัง) |

### สิ่งที่เห็นใน LAB 10

- แปลงร้านด้วยไฟล์ชื่อ/selector เดิม: `som-db` template เดิม → รับเลี้ยงเป็นรุ่นปัจจุบัน ไม่มี Recreate ข้อมูลไม่หาย, `som-web` → RS เดิมเป็น REVISION 0 แล้วถูกแทนแบบ rolling (err 1–2/300 เพราะบูธเดิมไม่มี preStop)
- rolling 1.2 → 1.3, undo สองครั้ง, undo จาก 1.4 และ rollout restart: `/api/whoami` err 0/300 ทุกครั้ง Pod เก่าขึ้น `Error` ชั่วครู่ (ปกติ)
- รุ่นพัง 1.4: `PodInitializing` → `ImagePullBackOff`, `exceeded its progress deadline` (exit 1) ~60 วินาที, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` ร้านยังขาย undo 0.1 วินาที
- scale 5: EndpointSlice 5 endpoint ไม่มี revision ใหม่
- ลบ Pod db: เปิดไม่ได้ 2–5 วินาที → 503 → `rollout restart deploy/som-web` เติมสินค้า ออเดอร์ 5 → 0 และ Recreate ของ `som-db` ปิดก่อนเปิดจริง

### 10.13 เก็บกวาด LAB 10

🐧 **ใน SSH session ของ k8s-lab** (หยุด `hit.sh` และ `-w` ในหน้าต่างอื่นด้วย Ctrl+C ก่อน)

```bash
time kubectl delete ns som-shop; kubectl get svc -A | grep -E "3008[0-2]" || echo "(30080 ว่าง)"
```

```text
namespace "som-shop" deleted

real	0m27.898s
(30080 ว่าง)
```

ลบ namespace ราว 28 วินาที (Pod web มี preStop และ grace period) พอร์ต 30080 ว่างอีกครั้ง image `som-shop-web:1.2`/`1.3` และ postgres ยังอยู่บน Node

### คำถามท้าย LAB 10

1. ทำไมตอน `kubectl apply -f k8s/10-db.yaml` (ขั้น 10.3) Pod db เดิมจึงไม่ถูกปิดทั้งที่ไฟล์เขียน `strategy: Recreate` ถ้าแก้ env ใดก็ได้ของ postgres ในไฟล์ก่อน apply จะเกิดอะไรกับออเดอร์
2. ทำไมการแปลง web (ขั้น 10.4) จึงมี error 1–2 ครั้ง แต่ rolling 1.2 → 1.3 (ขั้น 10.6) ได้ 0 ทั้งที่ใช้ Deployment ตัวเดียวกัน
3. อธิบายค่า `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` ระหว่างรุ่น 1.4 และบอกว่าถ้า `maxUnavailable` เป็น 1 ลูกค้าจะเห็นอะไรต่างไป
4. หลังลบ Pod db ทำไมช่วงแรกเปิดหน้าเว็บไม่ได้เลย แล้วค่อยเป็น 503 และทำไม `rollout restart deploy/som-web` จึงทำให้ร้านกลับมา (เทียบกับวิธีของบทที่ 6)
5. ถ้าน้องส้มอยากให้ออเดอร์ไม่หายเมื่อ Pod db ถูกสร้างใหม่ ต้องเปลี่ยนส่วนใดของ `k8s/10-db.yaml` และ Deployment ช่วยเรื่องนี้ได้หรือไม่ เพราะอะไร

> **🏆 ท้าทาย:** แก้ `k8s/20-web.yaml` ให้ใช้ `som-shop-web:1.3` และเปลี่ยน annotation `kubernetes.io/change-cause` เป็นข้อความใหม่ แล้ว `kubectl apply -f k8s/20-web.yaml` แทนการใช้ `set image` บันทึกว่า `rollout history` และ Warning เรื่อง last-applied เปลี่ยนไปอย่างไรเมื่อเทียบกับการใช้ `set image` + `undo` (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเอง)

> **ปูทางบทหน้า:** ผู้จัดการร้านดูแล "จำนวนและรุ่น" ได้ดีแล้ว แต่ครัวกลางยังลืมทุกอย่างทุกครั้งที่ Pod db เกิดใหม่ บทถัดไปจะให้ db มีที่เก็บข้อมูลถาวร (PersistentVolume/PersistentVolumeClaim) และรู้จัก StatefulSet

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v3/`, kubectl แจ้ง `the path "lab01-deployment/" does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 007_kubernetes_deployment k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/007_kubernetes_deployment/02_LAB/labs` (LAB 10 ใช้ `../som-shop-v3`) ตรวจด้วย `pwd` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 5 (build/load image ใหม่) |
| `error validating "...-patch.yaml": error validating data: [apiVersion not set, kind not set]` | apply ทั้งโฟลเดอร์ที่มีไฟล์ patch ปน (ไฟล์ patch ไม่มี apiVersion/kind) | ไฟล์ patch ต้องอยู่ใน `patches/` และใช้กับ `kubectl patch ... --patch-file` เท่านั้น |
| `The Deployment "zero" is invalid: ... may not be 0 when maxSurge is 0` ตอน apply LAB 4 | ไฟล์แบบฝึกอยู่ในโฟลเดอร์เดียวกับ `apply -f` | `zero-zero.yaml` อยู่ใน `exercise/` ใช้กับ `--dry-run=server` เท่านั้น |
| นับ Pod จาก `get pods -w` ได้มากกว่าที่คำนวณ | นับรวมบรรทัด `Terminating`/`Completed` ของ Pod ที่กำลังปิด | นับเฉพาะ Pod ที่ยังไม่ถูกสั่งปิด หรือดู annotation `deployment.kubernetes.io/max-replicas` ของ RS (LAB 4 ขั้นที่ 3) |
| Pod ขึ้น `0/1 Completed` (nginx/postgres) หรือ `0/1 Error` (Next.js) ระหว่าง rollout | Pod รุ่นเก่ากำลังปิด (ออกสะอาด / ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM) | ปกติ ไม่ใช่ rollout พัง รอสักครู่จะหายไป |
| `describe deploy` เห็น Events ไม่ครบ มี `(combined from similar events)` | ระบบรวม event ที่คล้ายกัน | ใช้ `kubectl get rs -w` หรือ `get rs` ดูจำนวนจริง |
| CHANGE-CAUSE ของ revision ใหม่ซ้ำกับของเก่า | ลืม `annotate` (รวมถึงหลัง `rollout restart`) | `kubectl -n <ns> annotate deploy <ชื่อ> kubernetes.io/change-cause="..." --overwrite` ทุกครั้ง หรือใส่ใน YAML |
| `error: you cannot rollback a paused deployment` | สั่ง undo ระหว่าง pause | `kubectl -n <ns> rollout resume deploy/<ชื่อ>` ก่อน |
| `rollout status` รอไม่จบ | Deployment ถูก pause อยู่ หรือรุ่นใหม่พังแต่ deadline ยังไม่หมด (default 600 วินาที) | ใส่ `--timeout=10s`, ตรวจ `kubectl get deploy` (UP-TO-DATE) และ `kubectl describe deploy` |
| `rollout status` จบด้วย `exceeded its progress deadline` (exit 1) | รุ่นใหม่ไม่พร้อมภายใน `progressDeadlineSeconds` | ดูสาเหตุด้วย `get pods`, `describe pod`, `logs --previous` แล้ว `kubectl rollout undo` |
| Pod ใหม่ `ErrImagePull`/`ImagePullBackOff` | tag ไม่มีจริง (ตั้งใจใน LAB 6/10) หรือลืม `kind load` image ที่ build เอง | LAB 6/10: `rollout undo`; ถ้าเป็น `som-shop-web:1.2`/`1.3` ทำ LAB 0 ขั้นที่ 5 |
| Pod ใหม่ค้าง `PodInitializing` ราว 8 วินาทีก่อน `ErrImagePull` (LAB 10 รุ่น 1.4) | initContainer รันก่อน แล้วจึงดึง image ของ container หลัก | ปกติ รอดูต่อ |
| `kubectl get node ... -o jsonpath='{.status.images...}'` ไม่เห็น image ทั้งที่เพิ่ง `kind load` | ข้อมูลใน `.status.images` อัปเดตช้า (30–60 วินาที) | ใช้ `docker exec lab-worker crictl images` |
| `provided port is already allocated` ตอน apply NodePort 30080 | Service อื่นจอง 30080 (LAB 7 ยังไม่ลบ, ร้านบทที่ 6, ตัวอย่างของบทที่ 1) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace/ตัวอย่างที่ค้าง |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นบนเครื่องใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| browser refresh แล้วเห็นรุ่น/ชื่อ Pod เดิม | keep-alive และ cache ของ browser | กด Ctrl+F5 และนับการกระจายด้วย `hit.sh` |
| หลัง `kubectl patch svc` เปลี่ยน selector ยังได้รุ่นเดิม | EndpointSlice/kube-proxy ยังอัปเดตไม่ทัน | รอ 1–2 วินาทีก่อนยิงทดสอบ |
| canary 50 ครั้งได้รุ่นใหม่ไม่ถึง/เกิน 10 ครั้ง | การสุ่มต่อ connection | ปกติ ยิงหลายร้อยครั้งจึงใกล้ 20% |
| ENDPOINTS แสดง `... + 2 more...` | kubectl ตัดการแสดงผลเกิน 3 IP | ใช้ jsonpath `{range .items[0].endpoints[*]}...` |
| หลังลบ Pod db หน้าเว็บเปิดไม่ได้ 2–5 วินาที แล้วเป็น 503 "ร้านกำลังเตรียมสินค้า" ค้าง | web ทุกตัว not ready ชั่วครู่ แล้ว db ใหม่ว่างเปล่า (ตั้งใจให้เห็น) | `kubectl -n som-shop rollout restart deploy/som-web` (ขั้น 10.10) |
| err ของ `hit.sh` มากกว่าในเอกสาร | เครื่องช้ากว่า หรือรอบที่บูธเดิมยังไม่มี preStop | ปกติ บันทึกตัวเลขของตัวเอง ถ้ามี error หลังใส่ preStop แล้ว ตรวจว่า patch/rollout จบก่อนเริ่มนับ |
| `./hit.sh: Permission denied` | สิทธิ์ execute หายระหว่างคัดลอก | `chmod +x ../som-shop-v3/hit.sh` หรือรันด้วย `bash` |
| ลบ namespace ใช้เวลานาน ~27 วินาที | Pod มี preStop 5 วินาทีและ grace period | ปกติ รอให้จบ |
| `hit.sh` หรือ `kubectl ... -w` ค้างอยู่ในอีกหน้าต่าง | ยังไม่ได้หยุด | กด Ctrl+C ในหน้าต่างนั้น ถ้าหาไม่เจอใช้ `pkill -f "[h]it.sh"` (ใส่วงเล็บเหลี่ยมเพื่อไม่ให้จับคำสั่ง pkill เอง) |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), ผล `grep -E '3008[0-2]'` ที่ว่าง และ `crictl images` ที่เห็น `som-shop-web` 1.2/1.3 + postgres
- [ ] **LAB 1** `get deploy,rs,pods --show-labels` (เห็น `pod-template-hash`), ownerReferences ของ RS และ Pod, history หลัง scale (revision 1 แถวเดียว) และ Event `Scaled down replica set ... from 6 to 3`
- [ ] **LAB 2** ผล `get rs -w` ที่ RS ใหม่เพิ่ม/เก่าลด และผลรวมคำตอบของ client (v1/v2 ปน ไม่มี ERR)
- [ ] **LAB 3** history ที่มี revision สืบทอด change-cause, history หลัง undo (`1, 3, 4, 5`), error ของ undo ระหว่าง pause และ annotation `restartedAt`
- [ ] **LAB 4** ตาราง Pod สูงสุด/พร้อมต่ำสุดของ 3 กลยุทธ์ (ตัวเลขของตัวเอง), `max-replicas 13` และ error ของ `zero-zero.yaml`
- [ ] **LAB 5** `get deploy -w` ที่ AVAILABLE ตาม READY ~10 วินาที และ Pod `0/1 Running` + Event `statuscode: 404`
- [ ] **LAB 6** `exceeded its progress deadline` + `exit=1`, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` และ condition `ProgressDeadlineExceeded`
- [ ] **LAB 7** ผล `hit.sh -q` รอบไม่มี preStop และรอบ graceful-patch (ตัวเลข err ของตัวเอง)
- [ ] **LAB 8** ownerReferences ของ RS `web` ที่ชี้ Deployment และ history `0`/`1`
- [ ] **LAB 9** ผล blue → green และสัดส่วน canary อย่างน้อย 3 รอบ
- [ ] **LAB 10** (1) history `0 <none>` / `1 1.2 แปลงเป็น Deployment` และ RS เดิม `0 0 0` (2) browser หน้าร้าน 1.2 ที่ชื่อ Pod มี hash (3) `hit.sh -q` ระหว่าง rolling 1.3 (`err=0`) (4) browser หน้าร้าน 1.3 (5) history หลัง undo สองครั้ง (6) 1.4: `ImagePullBackOff` + `exceeded its progress deadline` + `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` + สั่งซื้อได้ (7) EndpointSlice 5 endpoint (8) `relation "orders" does not exist` และร้านกลับมา `orders=0`
- [ ] ท้ายสุด `kubectl get ns` เหลือ namespace ตั้งต้น 5 ตัว และ `kubectl get svc -A | grep 3008` ว่าง

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| namespace `deploy-lab` (Deployment `web`, Service `web`, `client`) | 1–3 | `kubectl get all -n deploy-lab` | `kubectl delete ns deploy-lab` |
| Deployment ที่ถูก pause | 3 | `kubectl -n deploy-lab get deploy web -o jsonpath='{.spec.paused}'` | `kubectl -n deploy-lab rollout resume deploy/web` |
| namespace `strategy-lab` | 4 | `kubectl get ns strategy-lab` | `kubectl delete ns strategy-lab` |
| namespace `ready-lab` | 5 | `kubectl get ns ready-lab` | `kubectl delete ns ready-lab` |
| namespace `broken-lab` (Pod `ImagePullBackOff`/`CrashLoopBackOff`) | 6 | `kubectl get pods -n broken-lab` | `kubectl delete ns broken-lab` |
| namespace `zdt-lab` (**จอง NodePort 30080**) | 7 | `kubectl get svc -A \| grep 30080` | `kubectl delete ns zdt-lab` |
| namespace `migrate-lab` | 8 | `kubectl get ns migrate-lab` | `kubectl delete ns migrate-lab` |
| namespace `release-lab` | 9 | `kubectl get ns release-lab` | `kubectl delete ns release-lab` |
| namespace `som-shop` (**จอง NodePort 30080**) | 10 | `kubectl get ns som-shop` | `kubectl delete ns som-shop` |
| `hit.sh` หรือ `kubectl ... -w` ที่ยังรันอยู่ | 2–10 | `pgrep -af "[h]it.sh"` | Ctrl+C หรือ `pkill -f "[h]it.sh"` |
| image `som-shop-web:1.2`/`1.3`, postgres บน Node | 0, 10 | `docker exec lab-worker crictl images \| grep -E "som-shop\|postgres"` | **เก็บไว้ได้** (ใช้ซ้ำได้ ถ้า `k8s-down` จะหายไปด้วย) |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get ns
kubectl get svc -A
pgrep -af "[h]it.sh" || echo "ไม่มี hit.sh ค้าง"
```

ผลที่ถูกต้อง: เหลือ namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), Service มีแค่ `kubernetes` และ `kube-dns` และไม่มี `hit.sh` ค้าง

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ค่า hash, จำนวน error และจำนวนออเดอร์) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบทดลองที่ทำซ้ำเพื่อถ่ายภาพ ชื่อ Pod, เวลา rollout และเลข revision ในรอบนั้นจึงอาจต่างจากผลคำสั่งในเอกสาร
