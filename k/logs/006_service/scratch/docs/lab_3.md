## LAB 10: LAB สุดท้าย: แยก web กับ db ครั้งแรก

{{FIG:L15}}

**เป้าหมาย:** รวมทุกอย่างของบทนี้เปิด **ร้านอาหารแมวน้องส้ม** ที่แยกหน้าร้าน (web 3 บูธ) ออกจากครัวกลาง (db 1 ตัว) ด้วย **ReplicaSet 2 ตัว + Service 2 ตัว** เปิดร้านให้ลูกค้าที่ `http://localhost:30080` พิสูจน์ว่าออเดอร์จากทุกบูธรวมที่เดียว (แก้ปัญหาบทที่ 5) ดูว่า db ได้ IP ใหม่แต่ web ยังหาเจอด้วยชื่อ Service แล้วลองเปลี่ยนร้านเป็นรุ่น 1.3 ด้วยมือจนเห็นปัญหาที่บทที่ 7 จะแก้

**สิ่งที่ต้องมีก่อน:** ทำ LAB 0–9 แล้ว (เข้าใจ ClusterIP, EndpointSlice, NodePort, DNS และ readiness) **NodePort 30080 ต้องว่าง** (ลบ `web-nodeport` ใน LAB 8 แล้ว) และมี SSH session 2 หน้าต่าง (terminal 1, terminal 2) สำหรับข้อ 10.8 และ 10.12

### 10.1 สถาปัตยกรรมและไฟล์

บทที่ 2–5 ร้านน้องส้มใส่ web + db ไว้ใน Pod เดียว (db เป็น native sidecar คุยกันผ่าน `localhost`) พอบทที่ 5 scale เป็น 3 บูธ แต่ละบูธจึงมี db ของตัวเองและออเดอร์ไม่ตรงกัน LAB นี้แยกเป็น 2 ส่วนใน namespace `som-shop`

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080 → kube-proxy)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort http = 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-xxxxx     Pod som-web-xxxxx     Pod som-web-xxxxx      (ReplicaSet som-web, replicas 3 → 5 → 3)
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop  (ชื่อ Service ไม่ใช่ IP) ────┘
                                   ▼
                    Service som-db (ClusterIP, 5432 → targetPort postgres)   ← ชื่อ/IP คงที่แม้ Pod db เกิดใหม่
                                   ▼
                    Pod som-db-xxxxx (ReplicaSet som-db, replicas 1, emptyDir — ข้อมูลหายเมื่อเกิดใหม่)
namespace som-shop (PSA warn: restricted)
```

| ไฟล์ | เนื้อหา |
|---|---|
| `som-shop-v2/k8s/00-namespace.yaml` | namespace `som-shop` label `pod-security.kubernetes.io/warn: restricted` (แบบบทที่ 4) |
| `som-shop-v2/k8s/10-db.yaml` | ReplicaSet `som-db` (`replicas: 1`, `postgres:17.11-alpine`, PGDATA บน `emptyDir`, readiness `pg_isready`) + Service `som-db` ชนิด ClusterIP `5432 → postgres` |
| `som-shop-v2/k8s/20-web.yaml` | ReplicaSet `som-web` (`replicas: 3`, `som-shop-web:1.2`, initContainers `wait-for-db` + `db-seed`, readiness `/api/health`, liveness `/api/live`) + Service `som-web` ชนิด NodePort `80 → http`, `nodePort: 30080` |
| `som-shop-v2/app/` | แอป Next.js (สำเนาจากบทที่ 5 แล้วปรับเป็นรุ่น 1.2/1.3) |
| `som-shop-v2/hit.sh` | ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน |

ส่วนสำคัญของ `10-db.yaml` (ตัดมา)

```yaml
spec:
  # replicas ต้องเป็น 1 — postgres 2 ตัว "ไม่แชร์ข้อมูลกัน" (Service จะสุ่มส่งไปคนละ db)
  replicas: 1
  template:
    spec:
      volumes:
        # !!! emptyDir = ข้อมูลอยู่กับ Pod นี้เท่านั้น → Pod db ถูกลบ/เกิดใหม่ = ข้อมูลหายหมด
        # (ตั้งใจให้เห็นใน LAB — บทหลังใช้ PersistentVolumeClaim)
        - name: db-data
          emptyDir: {}
      containers:
        - name: postgres
          image: postgres:17.11-alpine
          env:
            - name: POSTGRES_PASSWORD
              value: meow1234        # เพื่อการเรียนเท่านั้น (ของจริงใช้ Secret — บทหลัง)
          ports:
            - name: postgres         # Service อ้าง targetPort: postgres
              containerPort: 5432
---
# ประภาคารของครัว: ClusterIP เท่านั้น (ใช้ภายในคลัสเตอร์ — ไม่เปิด NodePort ให้ db)
apiVersion: v1
kind: Service
metadata:
  name: som-db
  namespace: som-shop
spec:
  type: ClusterIP
  selector:
    app: som-db
  ports:
    - port: 5432
      targetPort: postgres
```

ส่วนสำคัญของ `20-web.yaml` (ตัดมา)

```yaml
      initContainers:
        # 1) รอจน Service som-db มี db ที่พร้อม
        - name: wait-for-db
          image: postgres:17.11-alpine
          command:
            - sh
            - -c
            - until pg_isready -h som-db -p 5432 -U som -d catshop; do echo "รอฐานข้อมูล som-db..."; sleep 2; done; echo "ฐานข้อมูลพร้อมแล้ว"
        # 2) เติมสินค้าเข้าชั้น (สร้างตาราง + สินค้าตั้งต้น) — ทุก Pod รัน แต่มี advisory lock กันชน
        - name: db-seed
          image: som-shop-web:1.2
          command: ["node", "scripts/seed.mjs"]
      containers:
        - name: web
          image: som-shop-web:1.2    # รุ่นและธีมฝังอยู่ใน image (APP_VERSION/APP_THEME)
          env:
            - name: DATABASE_URL     # เรียก db ด้วยชื่อ Service (ไม่ใช่ IP ของ Pod db)
              value: postgres://som:meow1234@som-db:5432/catshop
          ports:
            - name: http
              containerPort: 3000
          readinessProbe:            # ต่อ db ได้ไหม (SELECT 1) → ไม่ผ่าน = Service ไม่ส่งลูกค้ามา
            httpGet:
              path: /api/health
              port: http
            periodSeconds: 3
            failureThreshold: 2
          livenessProbe:             # process ยังไม่ค้าง (ไม่แตะ db)
            httpGet:
              path: /api/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
---
# ประภาคารของหน้าร้าน: NodePort 30080 → เปิด http://localhost:30080 บนเครื่องนักศึกษา
apiVersion: v1
kind: Service
metadata:
  name: som-web
  namespace: som-shop
spec:
  type: NodePort
  selector:
    app: som-web
  ports:
    - port: 80
      targetPort: http       # = 3000 ของ container web
      nodePort: 30080
```

**สิ่งที่เปลี่ยนในแอปรุ่น 1.2/1.3** (เทียบกับ `som-shop-web:1.1` ของบทที่ 4–5)

| ส่วน | รายละเอียด | ใช้ทำอะไรใน LAB |
|---|---|---|
| `Dockerfile` | `ARG APP_VERSION`, `ARG APP_THEME` → `ENV` แต่ละ tag "จำ" รุ่นและธีมของตัวเอง | build 1.2 (ธีม `harbor`) และ 1.3 (ธีม `sunset` + แบนเนอร์เมนูใหม่) จากโค้ดเดียว |
| หน้าแรก | ป้าย "เวอร์ชัน 1.2" และแถบ `🐱 เสิร์ฟโดย Pod: <ชื่อ Pod> · เวอร์ชัน <รุ่น>` | เห็นว่า browser ได้คำตอบจากบูธไหน |
| `GET /api/whoami` | ตอบ `<ชื่อ Pod> <รุ่น>` ไม่แตะ db | `hit.sh` นับการกระจายและรุ่น |
| `GET /api/stats` | ตอบ `<ชื่อ Pod> <รุ่น> orders=<n> products=<n>` ถ้า db ยังไม่มีตาราง ตอบ `db-not-ready` (HTTP 503) | เทียบว่าทุกบูธเห็นออเดอร์ชุดเดียวกัน |
| `GET /api/health` / `GET /api/live` | readiness (`SELECT 1` ไม่ตรวจตาราง) / liveness (ไม่แตะ db) | ทฤษฎีหัวข้อ 12.3 |
| `proxy.ts` | หน้า `/` ตรวจตาราง `products` ไม่มี → หน้า "ร้านกำลังเตรียมสินค้า" **HTTP 503** และ refresh เองทุก 5 วินาที | เห็นหลังลบ Pod db (ข้อ 10.9) |
| `scripts/seed.mjs` | `pg_advisory_xact_lock(5005)` + `CREATE TABLE IF NOT EXISTS` + `INSERT ... ON CONFLICT DO NOTHING` | 3 บูธเติมสินค้าพร้อมกันไม่ชนกัน (ข้อ 10.4) |
| `lib/db.ts` | `pool.on('error', ...)` สายเก่าขาดแล้วต่อใหม่เอง log บรรทัดเดียว | web ต่อ db ใหม่โดยไม่ต้อง restart (ข้อ 10.9) |

`hit.sh` (รันใน k8s-lab) ใช้งาน `./hit.sh [-q] [URL] [N] [DELAY]` ค่าเริ่มต้น URL `http://localhost:30080/api/whoami`, N=60, DELAY=0.1 วินาที ใช้ `curl -sS -f -m 2` แยกคำสั่งทุกครั้ง (connection ใหม่ทุกครั้ง HTTP 4xx/5xx นับเป็น err) แล้วพิมพ์ตาราง `จำนวน  Pod  เวอร์ชัน` และ `ok=… err=…` ส่วนโหมด `-q` พิมพ์ `.` (สำเร็จ) / `x` (ล้มเหลว) ระหว่างยิง แล้วสรุปข้อความ error และ "ช่วงที่มี err" ใช้ตอนลบ Pod

### 10.2 เตรียม image ให้ทุก Node

{{FIG:L16}}

🐧 **ใน SSH session ของ k8s-lab (terminal 1)** ตรวจว่า 30080 ว่าง แล้ว build รุ่น 1.2 และ 1.3 จากโค้ดเดียวกัน ต่างกันแค่ build-arg

```bash
cd /workspace/006_kubernetes_service/02_LAB
kubectl get svc -A | grep 30080 || echo '(ว่าง)'
cd som-shop-v2/app
time docker build -q --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 .
time docker build -q --build-arg APP_VERSION=1.3 --build-arg APP_THEME=sunset -t som-shop-web:1.3 .
```

```text
(ว่าง)
sha256:d82b21fba19a4da1c6cf66ca3d0c430c50d3422afacdbac618b4ef769cf0d620

real	0m28.035s
...
sha256:c8ff9b7a6dd688ac6836f31c4247d68de6cfe15ccfc85f4b49f93914bc15175f

real	0m0.880s
```

รุ่น 1.2 ใช้เวลาราว 28 วินาที (ดาวน์โหลด dependency และคอมไพล์) ส่วนรุ่น 1.3 ไม่ถึง 1 วินาที เพราะทุกชั้นก่อน `ENV` ใช้ cache เดิม ต่างกันแค่ค่า `APP_VERSION`/`APP_THEME` ในชั้นท้าย (เครื่องนักศึกษาอาจใช้เวลานานกว่านี้หลายเท่า)

นำ image ทั้งสองเข้าทุก Node แล้วเตรียม postgres

```bash
time kind load docker-image som-shop-web:1.2 som-shop-web:1.3 --name lab
cd ..
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o ../pg.tar && kind load image-archive ../pg.tar --name lab && rm ../pg.tar)
```

```text
Image: "som-shop-web:1.2" with ID "sha256:d82b21fb..." not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.2" with ID "sha256:d82b21fb..." not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.2" with ID "sha256:d82b21fb..." not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.3" with ID "sha256:c8ff9b7a..." not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.3" with ID "sha256:c8ff9b7a..." not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.3" with ID "sha256:c8ff9b7a..." not yet present on node "lab-worker", loading...

real	0m4.443s
docker.io/library/postgres:17.11-alpine

real	0m15.226s
```

- image ที่ build เอง (`som-shop-web`) ไม่มีใน Docker Hub ต้อง `kind load docker-image` ให้ทุก Node และ YAML ใช้ `imagePullPolicy: IfNotPresent`
- postgres เป็น image หลาย platform ถ้า `kind load docker-image` ตรง ๆ อาจได้ `ctr: content digest sha256:...: not found` จึงใช้ `docker save --platform linux/amd64` + `kind load image-archive` (ถ้าข้ามขั้นนี้ Node จะดึงจาก Docker Hub เองได้แต่ช้ากว่า) ถ้าเคยโหลดไว้ในบทก่อนและคลัสเตอร์ยังเดิม ข้ามขั้นนี้ได้
- ตอนนี้อยู่ที่โฟลเดอร์ `/workspace/006_kubernetes_service/02_LAB/som-shop-v2` คำสั่งที่เหลือของ LAB 10 รันจากที่นี่

### 10.3 เปิดครัวกลาง: db + Service som-db

{{FIG:L17}}

```bash
kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml
time kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=120s
kubectl -n som-shop get rs,pods,svc,endpointslice -o wide
```

```text
namespace/som-shop created
replicaset.apps/som-db created
service/som-db created
pod/som-db-vhn7w condition met

real	0m3.791s

NAME                     DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                  SELECTOR
replicaset.apps/som-db   1         1         1       4s    postgres     postgres:17.11-alpine   app=som-db

NAME               READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
pod/som-db-vhn7w   1/1     Running   0          4s    10.244.2.21   lab-worker   <none>           <none>

NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE   SELECTOR
service/som-db   ClusterIP   10.96.93.105   <none>        5432/TCP   4s    app=som-db

NAME                                          ADDRESSTYPE   PORTS   ENDPOINTS     AGE
endpointslice.discovery.k8s.io/som-db-v78pk   IPv4          5432    10.244.2.21   4s
```

**จดไว้ 2 ค่า** จะใช้เทียบในข้อ 10.9: ClusterIP ของ `som-db` (`10.96.93.105`) และ IP ของ Pod db (`10.244.2.21`) ไม่มีคำเตือน Pod Security เพราะ Pod ตั้ง securityContext ครบตามระดับ restricted แล้ว (บทที่ 4)

### 10.4 เปิดหน้าร้าน 3 บูธ และเติมสินค้าแบบกันชน

{{FIG:L18}}

```bash
kubectl apply -f k8s/20-web.yaml && timeout 12 kubectl -n som-shop get pods -l app=som-web -w; true
```

ผลจริง (ตัดบรรทัดซ้ำ)

```text
replicaset.apps/som-web created
service/som-web created
NAME            READY   STATUS     RESTARTS   AGE
som-web-6h94x   0/1     Pending    0          1s
som-web-8g2wt   0/1     Init:0/2   0          1s
som-web-zk8jj   0/1     Init:0/2   0          1s
...
som-web-8g2wt   0/1     Init:1/2   0          2s
som-web-zk8jj   0/1     Init:1/2   0          2s
som-web-6h94x   0/1     Init:1/2   0          2s
...
som-web-8g2wt   0/1     PodInitializing   0          3s
...
som-web-8g2wt   0/1     Running           0          3s
...
som-web-8g2wt   1/1     Running           0          4s
som-web-6h94x   1/1     Running           0          4s
som-web-zk8jj   1/1     Running           0          4s
```

แต่ละบูธผ่าน `Init:0/2` (รอ db) → `Init:1/2` (เติมสินค้า) → `PodInitializing` → `Running 0/1` (รอ readiness) → `1/1` (`timeout 12` หยุดการดูให้เองหลัง 12 วินาที) ดู log ของ initContainer `db-seed` ทั้ง 3 บูธ

```bash
kubectl -n som-shop logs -l app=som-web -c db-seed --prefix
kubectl -n som-shop get pods -o custom-columns=NAME:.metadata.name,INIT_RESTARTS:.status.initContainerStatuses[*].restartCount,NODE:.spec.nodeName
```

```text
[pod/som-web-8g2wt/db-seed] connected to database
[pod/som-web-8g2wt/db-seed] got seed lock 5005
[pod/som-web-8g2wt/db-seed] tables ready: products, orders
[pod/som-web-8g2wt/db-seed] seeded 6 products (new: 0)
[pod/som-web-zk8jj/db-seed] connected to database
[pod/som-web-zk8jj/db-seed] got seed lock 5005
[pod/som-web-zk8jj/db-seed] tables ready: products, orders
[pod/som-web-zk8jj/db-seed] seeded 6 products (new: 0)
[pod/som-web-6h94x/db-seed] connected to database
[pod/som-web-6h94x/db-seed] got seed lock 5005
[pod/som-web-6h94x/db-seed] tables ready: products, orders
[pod/som-web-6h94x/db-seed] seeded 6 products (new: 6)
NAME            INIT_RESTARTS   NODE
som-db-vhn7w    <none>          lab-worker
som-web-6h94x   0,0             lab-worker
som-web-8g2wt   0,0             lab-worker2
som-web-zk8jj   0,0             lab-worker
```

- ทั้ง 3 บูธเริ่มเติมสินค้าพร้อมกันเข้า **db ตัวเดียวกัน** แต่ `pg_advisory_xact_lock(5005)` ทำให้เข้าคิวทีละบูธ บูธแรกที่ได้ lock เพิ่มสินค้า 6 รายการ (`new: 6`) บูธที่เหลือเห็นว่ามีแล้ว (`new: 0`) เพราะ `ON CONFLICT DO NOTHING`
- `INIT_RESTARTS 0,0` ทุกบูธ ในการตรวจก่อนเขียนบท แอปรุ่นเก่าที่ **ไม่มี lock** ทำให้ 2 ใน 3 บูธ init ล้ม 1 ครั้งด้วย `duplicate key value violates unique constraint "pg_type_typname_nsp_index"` เพราะ `CREATE TABLE IF NOT EXISTS` พร้อมกันชนกัน บทเรียน: **งานที่ replica หลายตัวทำซ้ำพร้อมกันต้องรันซ้ำได้ (idempotent) และกันชน** (งานแบบทำครั้งเดียวมีเครื่องมือเฉพาะในบทหลัง)
- จำนวนบูธต่อ Node (2+1) ขึ้นกับ scheduler ของเครื่องตัวเอง

### 10.5 web หา db ด้วยชื่อ Service

แทน `som-web-6h94x` ด้วยชื่อบูธในเครื่องตัวเอง

```bash
kubectl -n som-shop exec som-web-6h94x -c web -- node -e "require('dns').lookup('som-db',(e,a)=>console.log(a))"
kubectl -n som-shop get svc som-db
kubectl -n som-shop exec som-web-6h94x -c web -- env | grep SOM_DB_SERVICE
kubectl -n som-shop get rs,svc
```

```text
10.96.93.105
NAME     TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
som-db   ClusterIP   10.96.93.105   <none>        5432/TCP   35s
SOM_DB_SERVICE_PORT=5432
SOM_DB_SERVICE_HOST=10.96.93.105
NAME                      DESIRED   CURRENT   READY   AGE
replicaset.apps/som-db    1         1         1       35s
replicaset.apps/som-web   3         3         3       31s

NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/som-db    ClusterIP   10.96.93.105   <none>        5432/TCP       35s
service/som-web   NodePort    10.96.77.163   <none>        80:30080/TCP   31s
```

- ในบูธ web ชื่อ `som-db` แปลเป็น ClusterIP ของ Service `som-db` (search domain `som-shop.svc.cluster.local`) ไม่ใช่ IP ของ Pod db
- มี env `SOM_DB_SERVICE_HOST` เพราะบูธ web ถูกสร้างหลัง Service `som-db` (ถ้าสลับลำดับ apply จะไม่มี แต่ DNS ยังใช้ได้ แอปจึงใช้ชื่อใน `DATABASE_URL`)
- `som-web` เป็น NodePort `80:30080/TCP` พร้อมให้ลูกค้าเข้าแล้ว

### 10.6 เปิดร้านที่ http://localhost:30080

{{FIG:L19}}

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:30080** จะเห็นร้านธีม harbor (น้ำเงิน teal) ป้าย **"เวอร์ชัน 1.2"** แถบ **"🐱 เสิร์ฟโดย Pod: som-web-… · เวอร์ชัน 1.2"** ข้อความเล็ก `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service` และท้ายหน้า `Next.js + PostgreSQL · Kubernetes LAB 006 · namespace som-shop`

{{FIG:S1}}

กด refresh หลายครั้ง ส่วนใหญ่ชื่อ Pod **ไม่เปลี่ยน** (keep-alive แบบ LAB 8 ผลจริงของร้านนี้ใน Chromium: reload 9 ครั้งได้ Pod เดิมทั้ง 9) ดูการกระจายจริงด้วย `hit.sh`

🐧 **ใน SSH session ของ k8s-lab** (อยู่ที่ `som-shop-v2`)

```bash
./hit.sh
```

```text
จำนวน  Pod  เวอร์ชัน
     25 som-web-6h94x 1.2
     17 som-web-8g2wt 1.2
     18 som-web-zk8jj 1.2
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
```

60 ครั้งไปครบทั้ง 3 บูธ ไม่มี error

### 10.7 ออเดอร์จากทุกบูธรวมที่เดียว

{{FIG:L20}}

สั่งซื้อ 3 ออเดอร์ผ่าน NodePort (แต่ละคำสั่งอาจไปตกคนละบูธ) แล้วนับในฐานข้อมูลโดยตรง และถามทุกบูธด้วย `/api/stats`

```bash
for i in 1 2 3; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":2}'; echo; done
kubectl -n som-shop exec $(kubectl -n som-shop get pod -l app=som-db -o name) -- psql -U som -d catshop -c 'select count(*) from orders'
for i in $(seq 12); do curl -s localhost:30080/api/stats; done | sort | uniq -c
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":16}}
{"ok":true,"order_id":3,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":14}}
 count 
-------
     3
(1 row)

      2 som-web-6h94x 1.2 orders=3 products=6
      8 som-web-8g2wt 1.2 orders=3 products=6
      2 som-web-zk8jj 1.2 orders=3 products=6
```

ทุกบูธเห็น `orders=3` เท่ากัน และ `order_id` เรียง 1, 2, 3 ต่อกัน (stock ลดต่อเนื่อง 18 → 16 → 14) เพราะทุกบูธเขียนลง **db กลางตัวเดียว** ผ่านชื่อ `som-db` ต่างจากบทที่ 5 ที่บูธหนึ่งออเดอร์ 2 แต่อีกบูธ 0

🌐 กดปุ่ม 🛒 **สั่งซื้อ** ในหน้าร้านอีก 1 ครั้ง ผลจริงในการทดลอง: ข้อความ `สั่งซื้อแล้ว! ออเดอร์ #4` และตัวเลข "ออเดอร์ทั้งหมด" เปลี่ยนจาก 3 เป็น 4 (บูธที่เสิร์ฟคือ `som-web-zk8jj`) ไม่ว่าคำสั่งซื้อจะไปตกบูธไหน ตัวเลขก็ต่อกัน

> ไม่ควรใช้ `curl -s localhost:30080 | grep ...` เพื่อดูชื่อ Pod จากหน้าแรก เพราะหน้า Next.js มีข้อมูล RSC ฝังอยู่ ทำให้ได้ข้อความยาวหลายพันตัวอักษร ให้ใช้ `/api/whoami` หรือ `/api/stats` แทน

### 10.8 scale 3 → 5 และ self-healing ใต้ Service

{{FIG:L21}}

```bash
kubectl -n som-shop scale rs/som-web --replicas=5
kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=90s
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
./hit.sh
```

```text
replicaset.apps/som-web scaled
pod/som-web-6h94x condition met
pod/som-web-8g2wt condition met
pod/som-web-kx775 condition met
pod/som-web-zk8jj condition met
pod/som-web-zr5pd condition met
NAME            ADDRESSTYPE   PORTS   ENDPOINTS                                         AGE
som-web-d5hqj   IPv4          3000    10.244.2.22,10.244.1.14,10.244.2.23 + 2 more...   68s
10.244.2.22 som-web-zk8jj ready=true
10.244.1.14 som-web-8g2wt ready=true
10.244.2.23 som-web-6h94x ready=true
10.244.1.15 som-web-kx775 ready=true
10.244.1.16 som-web-zr5pd ready=true
จำนวน  Pod  เวอร์ชัน
     20 som-web-6h94x 1.2
      8 som-web-8g2wt 1.2
      9 som-web-kx775 1.2
     12 som-web-zk8jj 1.2
     11 som-web-zr5pd 1.2
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
```

บูธใหม่ 2 ตัว Ready ในราว 4 วินาที EndpointSlice มี 5 IP เอง (PORTS `3000` = พอร์ตของ container) และลูกค้ากระจายไปครบ 5 บูธโดยไม่ต้องแก้ Service

**self-healing ใต้ Service:** ใช้ 2 หน้าต่าง

🐧 **terminal 1** (`cd /workspace/006_kubernetes_service/02_LAB/som-shop-v2` ก่อน) ยิง 100 ครั้งแบบโหมดเงียบ

```bash
./hit.sh -q http://localhost:30080/api/whoami 100
```

🐧 **terminal 2** สั่งทันทีระหว่างที่ terminal 1 กำลังยิง (ลบบูธแรกในรายชื่อ)

```bash
kubectl -n som-shop delete $(kubectl -n som-shop get pod -l app=som-web -o name | head -1)
```

ผลจริง 3 รอบ (รอบละครั้ง terminal 2 แสดง `pod "som-web-..." deleted from som-shop namespace`)

```text
....................x...............................................................................
ข้อความ error:
      1 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 0.0 วินาที
ok=99 err=1 (ใช้เวลา 10.8 วินาที)

....................................................................................................
ok=100 err=0 (ใช้เวลา 10.8 วินาที)

....................................................................................................
ok=100 err=0 (ใช้เวลา 10.8 วินาที)
```

ReplicaSet สร้างบูธใหม่แทน EndpointSlice ถอดบูธเก่าออกและใส่บูธใหม่เมื่อ Ready ร้านขายต่อได้เกือบทุกครั้ง แต่บางรอบมี 1 request ที่โดน `Connection reset by peer` เพราะไปถึงบูธตอนกำลังปิดพอดี (ทฤษฎีหัวข้อ 12.2) ในการทดสอบ 5 รอบได้ err 1, 0, 1, 0, 0 ถ้าดู `kubectl -n som-shop get pods -w` ระหว่างนั้นจะเห็นบูธที่ถูกลบขึ้นสถานะ `Error` ชั่วครู่ก่อนหาย (Next.js ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM) เป็นเรื่องปกติ

คืนเป็น 3 บูธ

```bash
kubectl -n som-shop scale rs/som-web --replicas=3
sleep 3; kubectl -n som-shop get pods
```

```text
replicaset.apps/som-web scaled
NAME            READY   STATUS    RESTARTS   AGE
som-db-vhn7w    1/1     Running   0          2m18s
som-web-lm7jj   1/1     Running   0          40s
som-web-zk8jj   1/1     Running   0          2m14s
som-web-zr5pd   1/1     Running   0          71s
```

### 10.9 ลบ Pod db: ชื่อเดิม IP ใหม่ แต่ข้อมูลหาย

{{FIG:L22}}

```bash
kubectl -n som-shop get pod -l app=som-db -o wide
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
S=$(date +%s.%N); kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=60s; E=$(date +%s.%N); awk -v a=$S -v b=$E "BEGIN{printf \"db ใหม่ Ready หลังสั่งลบ %.1f วินาที\n\", b-a}"
kubectl -n som-shop get pod -l app=som-db -o wide
kubectl -n som-shop get svc som-db
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
```

```text
NAME           READY   STATUS    RESTARTS   AGE     IP            NODE         NOMINATED NODE   READINESS GATES
som-db-vhn7w   1/1     Running   0          2m38s   10.244.2.21   lab-worker   <none>           <none>
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-v78pk   IPv4          5432    10.244.2.21   2m39s
pod "som-db-vhn7w" deleted from som-shop namespace
pod/som-db-mlfx7 condition met
db ใหม่ Ready หลังสั่งลบ 4.7 วินาที
NAME           READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
som-db-mlfx7   1/1     Running   0          4s    10.244.2.26   lab-worker   <none>           <none>
NAME     TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
som-db   ClusterIP   10.96.93.105   <none>        5432/TCP   2m44s
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-v78pk   IPv4          5432    10.244.2.26   2m44s
```

- ReplicaSet `som-db` สร้าง db ใหม่ Ready ในราว 5 วินาที ได้ **ชื่อใหม่และ IP ใหม่** (`10.244.2.21 → 10.244.2.26`)
- Service `som-db` ยังเป็น **ClusterIP เดิม** (`10.96.93.105`) EndpointSlice ชื่อเดิม (`som-db-v78pk`) แค่เปลี่ยน IP ข้างใน web ทุกบูธจึงไม่ต้องแก้อะไร

ตรวจหน้าร้านและฐานข้อมูล

```bash
curl -s -o /dev/null -w "%{http_code}\n" localhost:30080; curl -s localhost:30080/api/health; echo
for i in 1 2 3 4 5 6; do curl -s localhost:30080/api/stats; done | sort | uniq -c
kubectl -n som-shop exec $(kubectl -n som-shop get pod -l app=som-db -o name) -- psql -U som -d catshop -c 'select count(*) from orders'
kubectl -n som-shop get pods; kubectl -n som-shop logs -l app=som-web -c web --tail=2 --prefix
```

```text
503
{"ok":true,"db":"up"}
      4 som-web-lm7jj 1.2 db-not-ready
      1 som-web-zk8jj 1.2 db-not-ready
      1 som-web-zr5pd 1.2 db-not-ready
ERROR:  relation "orders" does not exist
LINE 1: select count(*) from orders
                             ^
command terminated with exit code 1
NAME            READY   STATUS    RESTARTS   AGE
som-db-mlfx7    1/1     Running   0          5s
som-web-lm7jj   1/1     Running   0          66s
som-web-zk8jj   1/1     Running   0          2m40s
som-web-zr5pd   1/1     Running   0          97s
[pod/som-web-lm7jj/web] ✓ Running next.config took 1.0ms
[pod/som-web-lm7jj/web] db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)
[pod/som-web-zk8jj/web] ✓ Running next.config took 1.0ms
[pod/som-web-zk8jj/web] db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)
[pod/som-web-zr5pd/web] ✓ Running next.config took 0.8ms
[pod/som-web-zr5pd/web] db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)
```

- web **ต่อ db ใหม่ได้เองโดยไม่ restart** (`/api/health` → `{"ok":true,"db":"up"}`, RESTARTS 0, บูธยัง `1/1`) log บอกแค่ว่าสายเก่าขาดแล้วจะต่อใหม่เอง
- แต่ db ตัวใหม่ **ว่างเปล่า** เพราะข้อมูลเก่าอยู่ใน `emptyDir` ของ Pod db ที่ถูกลบ ตาราง `orders` จึงไม่มี (`relation "orders" does not exist`) ทุกบูธตอบ `/api/stats` ว่า `db-not-ready` และหน้าแรกตอบ **HTTP 503**

🌐 refresh browser จะเห็นหน้า **"ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱"** (หน้านี้ลองใหม่เองทุก 5 วินาที)

{{FIG:S2}}

ภาพหน้าจอจริงด้านบนมาจากการทดลองอีกรอบหนึ่ง ซึ่งได้ผลแบบเดียวกัน (ผลคำสั่งของรอบนั้น)

```text
$ kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-vnbxx   IPv4          5432    10.244.2.33   7m52s
$ kubectl -n som-shop delete pod -l app=som-db
pod "som-db-zcwt6" deleted from som-shop namespace
$ kubectl -n som-shop get svc som-db
NAME     TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
som-db   ClusterIP   10.96.188.142   <none>        5432/TCP   7m56s
$ kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db
NAME           ADDRESSTYPE   PORTS   ENDPOINTS     AGE
som-db-vnbxx   IPv4          5432    10.244.2.38   7m56s
$ curl -s -o /dev/null -w %{http_code} localhost:30080
503
```

ทำไมบูธ web ยัง Ready ทั้งที่หน้าเว็บ 503: readinessProbe (`/api/health`) ตรวจแค่ "ต่อ db ได้" ไม่ตรวจตาราง ถ้าตรวจตารางด้วย ทุกบูธจะ not ready พร้อมกัน Service ไม่มีปลายทาง ลูกค้าจะได้ connection refused ทั้งร้านแทนหน้าแจ้งเตือนที่เป็นมิตร (ทฤษฎีหัวข้อ 12.3)

### 10.10 เติมสินค้าใหม่ด้วยการลบ Pod web 1 ตัว

initContainer `db-seed` รันเฉพาะตอนสร้าง Pod บทนี้ยังไม่มีคำสั่งสั่งให้บูธเริ่มใหม่ทั้งชุด วิธีที่ง่ายที่สุดคือลบบูธ web **ตัวเดียว** ให้ ReplicaSet สร้างใหม่ initContainer ของบูธใหม่จะสร้างตารางและสินค้าให้ db กลาง ซึ่งทุกบูธใช้ร่วมกัน

```bash
P=$(kubectl -n som-shop get pod -l app=som-web -o name | head -1); echo $P
S=$(date +%s.%N); kubectl -n som-shop delete $P; kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=60s; E=$(date +%s.%N); awk -v a=$S -v b=$E "BEGIN{printf \"Pod web ใหม่ Ready หลังสั่งลบ %.1f วินาที\n\", b-a}"
kubectl -n som-shop logs -l app=som-web -c db-seed --prefix | grep seeded
for i in $(seq 9); do curl -s localhost:30080/api/stats; done | sort | uniq -c; for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " localhost:30080; done; echo
```

ผลจริง (ในการทดลองบูธที่ถูกลบคือ `som-web-zk8jj`)

```text
pod "som-web-zk8jj" deleted from som-shop namespace
pod/som-web-lm7jj condition met
pod/som-web-n5vw6 condition met
pod/som-web-zr5pd condition met
Pod web ใหม่ Ready หลังสั่งลบ 3.6 วินาที
[pod/som-web-lm7jj/db-seed] seeded 6 products (new: 0)
[pod/som-web-n5vw6/db-seed] seeded 6 products (new: 6)
[pod/som-web-zr5pd/db-seed] seeded 6 products (new: 0)
      4 som-web-lm7jj 1.2 orders=0 products=6
      2 som-web-n5vw6 1.2 orders=0 products=6
      3 som-web-zr5pd 1.2 orders=0 products=6
200 200 200 200 200 200 
```

- บูธใหม่ `som-web-n5vw6` เติมสินค้า `new: 6` ลง db ใหม่ (log `new: 0` ของอีกสองบูธเป็นของตอนที่บูธนั้นเกิด ไม่ได้รันใหม่)
- **ทุกบูธกลับมาขายทันที** (`200` ทุกครั้ง `products=6`) โดยไม่ต้องลบบูธอื่น เพราะใช้ db กลางตัวเดียว
- แต่ **`orders=0`** ออเดอร์เก่าหายถาวร

{{FIG:S3}}

**บทเรียน:** Service ทำให้ "ที่อยู่" ของ db คงที่ แต่ไม่ได้ทำให้ "ข้อมูล" คงอยู่ db ที่เก็บข้อมูลบน `emptyDir` เสียข้อมูลทุกครั้งที่ Pod db เกิดใหม่ (แก้ด้วย PersistentVolumeClaim ในบทหลัง) และ `replicas` ของ db ต้องเป็น 1 เพราะ postgres 2 ตัวไม่แชร์ข้อมูลกัน Service จะสุ่มส่งไปคนละ db

### 10.11 อยากเปลี่ยนเป็นรุ่น 1.3

{{FIG:L23}}

น้องส้มอยากเปิดตัวเมนูใหม่ในรุ่น 1.3 (ธีม sunset + แบนเนอร์) image เตรียมไว้แล้วในข้อ 10.2 คำสั่ง `kubectl set image` เปลี่ยน image ใน template ของ ReplicaSet ได้ทั้ง container หลัก (`web`) และ initContainer (`db-seed`)

```bash
kubectl -n som-shop set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
kubectl -n som-shop get rs som-web -o jsonpath='{.spec.template.spec.containers[0].image} {.spec.template.spec.initContainers[1].image}'; echo
kubectl -n som-shop get rs som-web -o wide
kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
./hit.sh
```

```text
replicaset.apps/som-web image updated
som-shop-web:1.3 som-shop-web:1.3
NAME      DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES             SELECTOR
som-web   3         3         3       3m11s   web          som-shop-web:1.3   app=som-web
NAME            IMAGE
som-web-lm7jj   som-shop-web:1.2
som-web-n5vw6   som-shop-web:1.2
som-web-zr5pd   som-shop-web:1.2
จำนวน  Pod  เวอร์ชัน
     21 som-web-lm7jj 1.2
     18 som-web-n5vw6 1.2
     21 som-web-zr5pd 1.2
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
```

template ของ ReplicaSet เป็น 1.3 แล้ว แต่ **บูธเดิมทั้ง 3 ยังเป็น 1.2** และลูกค้ายังเห็น 1.2 ทุกครั้ง (ทบทวนบทที่ 5: ReplicaSet ดูแลแค่จำนวน ไม่เปลี่ยน Pod ที่มีอยู่) น้องส้มต้องลบบูธเองเพื่อให้ ReplicaSet สร้างบูธใหม่จาก template ใหม่

### 10.12 ลบ Pod เองทีละตัว แล้วลบที่เหลือทีเดียว

**แบบที่ 1: ลบทีละตัว** ใช้ 2 หน้าต่าง

🐧 **terminal 1** ยิง 200 ครั้งแบบแสดงตาราง

```bash
./hit.sh http://localhost:30080/api/whoami 200
```

🐧 **terminal 2** ระหว่างที่ terminal 1 ยิงอยู่ ลบบูธ 1 ตัวแล้วรอจนทุกบูธ Ready

```bash
kubectl -n som-shop delete $(kubectl -n som-shop get pod -l app=som-web -o name | head -1) && kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=90s
```

ผลจริง (terminal 2 แล้วตามด้วย terminal 1)

```text
pod "som-web-lm7jj" deleted from som-shop namespace
pod/som-web-mtvzf condition met
pod/som-web-n5vw6 condition met
pod/som-web-zr5pd condition met

จำนวน  Pod  เวอร์ชัน
      6 som-web-lm7jj 1.2
     58 som-web-mtvzf 1.3
     62 som-web-n5vw6 1.2
     74 som-web-zr5pd 1.2
ok=200 err=0 (ใช้เวลา 21.7 วินาที)
```

ระหว่างนี้ **ลูกค้าเห็นร้านคนละรุ่นปนกัน** (บางคนเห็นธีม sunset 1.3 บางคนเห็น harbor 1.2) รอบนี้ err 0 (อีกรอบได้ err 1) ถ้าจะทำต่ออีก 2 บูธต้องพิมพ์ชื่อและรอเองทีละตัว น่าเบื่อและเสี่ยงลบผิดตัว

```bash
kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
```

```text
NAME            IMAGE
som-web-mtvzf   som-shop-web:1.3
som-web-n5vw6   som-shop-web:1.2
som-web-zr5pd   som-shop-web:1.2
```

**แบบที่ 2: ทางลัดที่ผิด ลบทั้งหมดในคำสั่งเดียว**

🐧 **terminal 1**

```bash
./hit.sh -q http://localhost:30080/api/whoami 200
```

🐧 **terminal 2** ระหว่างที่ terminal 1 ยิงอยู่

```bash
kubectl -n som-shop delete pod -l app=som-web
kubectl -n som-shop get pods
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-web
```

ผลจริง (terminal 2 แล้วตามด้วย terminal 1)

```text
pod "som-web-mtvzf" deleted from som-shop namespace
pod "som-web-n5vw6" deleted from som-shop namespace
pod "som-web-zr5pd" deleted from som-shop namespace
NAME            READY   STATUS     RESTARTS   AGE
som-db-mlfx7    1/1     Running    0          111s
som-web-6pk9k   0/1     Init:0/2   0          2s
som-web-7pl88   0/1     Init:1/2   0          2s
som-web-jv599   0/1     Init:1/2   0          1s
NAME            ADDRESSTYPE   PORTS   ENDPOINTS                             AGE
som-web-d5hqj   IPv4          3000    10.244.2.29,10.244.1.19,10.244.1.18   4m26s

...................xxxxxxx..............................................................................................................................................................................
ข้อความ error:
      1 curl: (28) Operation timed out
      6 curl: (56) Recv failure: Connection reset by peer
ช่วงที่มี err: 2.6 วินาที
ok=193 err=7 (ใช้เวลา 24.7 วินาที)
```

ตรวจรุ่นหลังร้านกลับมา

```bash
kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image; ./hit.sh
```

```text
NAME            IMAGE
som-web-6pk9k   som-shop-web:1.3
som-web-7pl88   som-shop-web:1.3
som-web-jv599   som-shop-web:1.3
จำนวน  Pod  เวอร์ชัน
     23 som-web-6pk9k 1.3
     20 som-web-7pl88 1.3
     17 som-web-jv599 1.3
ok=60 err=0 (ใช้เวลา 6.5 วินาที)
```

- ลบทั้งหมดพร้อมกัน → บูธใหม่ทุกตัวยังอยู่ใน `Init` ไม่มีบูธที่ ready ให้ส่งลูกค้า (ENDPOINTS ที่เห็นเป็น IP ของบูธใหม่ที่ยัง `ready=false`) **ร้านสะดุด** แถว `x` ต่อกัน 7 ตัว ในช่วงราว 2.6 วินาที
- ข้อความ error คือ `Connection reset by peer` และ `Operation timed out` ทดลองซ้ำอีก 2 รอบได้ err 4 และ 4 (ช่วง 2.3 และ 4.3 วินาที) และในรอบที่ถ่ายภาพหน้าจอ **ยิง 150 ครั้งได้ error 7 ครั้ง** (`during delete-all: ok=143 err=7`)
- ตัวเลขนี้มาจากเครื่องทดสอบที่บูธใหม่ Ready ในราว 3–4 วินาที **เครื่องที่ช้ากว่าจะเห็น err มากกว่านี้** และถ้าร้านมี 30 บูธ ทั้งสองแบบยิ่งลำบาก

🌐 refresh browser จะเห็นร้านรุ่นใหม่

{{FIG:S4}}

### 10.13 สรุป LAB 10 และปัญหาที่ส่งต่อ

{{FIG:L24}}

**ตารางสรุป** สิ่งที่ Service แก้ได้และยังแก้ไม่ได้ในร้านน้องส้ม

| เรื่อง | ผลใน LAB 10 | แก้ด้วย |
|---|---|---|
| ที่อยู่คงที่ของร้านและของ db | `som-db` ClusterIP เดิมแม้ IP ของ Pod db เปลี่ยน, `som-web` NodePort 30080 | ✅ Service (บทนี้) |
| ออเดอร์ตรงกันทุกบูธ | `orders=3` ทุกบูธ, `order_id` ต่อกัน | ✅ แยก db + Service `som-db` (บทนี้) |
| กระจายลูกค้า + ส่งเฉพาะบูธที่พร้อม | `hit.sh` ครบทุกบูธ, scale 5 แล้ว EndpointSlice ตามเอง | ✅ Service + readinessProbe (บทนี้) |
| เปิดร้านจาก browser | `http://localhost:30080` ไม่ต้อง port-forward | ✅ NodePort (บทนี้) |
| เปลี่ยนรุ่นทีละบูธอัตโนมัติ รอไฟเขียวก่อนรื้อบูธถัดไป | ต้องลบ Pod เอง ลบทีเดียว err 4–7 ครั้ง, ลบทีละตัวต้องพิมพ์ชื่อและรอเอง | ❌ → **บทที่ 7 Deployment** |
| ประวัติรุ่นและย้อนรุ่น | ไม่มี ถ้า 1.3 พังต้อง `set image` กลับแล้วลบ Pod เองอีกรอบ | ❌ → **บทที่ 7 Deployment** |
| ข้อมูล db คงอยู่เมื่อ Pod db เกิดใหม่ | `relation "orders" does not exist`, ออเดอร์ 0 | ❌ → PersistentVolumeClaim (บทหลัง) |

### สิ่งที่เห็นใน LAB 10

- ReplicaSet 2 ตัว + Service 2 ตัวแยก web กับ db ได้ web เรียก db ด้วยชื่อ `som-db` (DNS → ClusterIP) ไม่ใช่ IP
- 3 บูธเติมสินค้าพร้อมกันโดยไม่ชนกันด้วย advisory lock (`new: 6/0/0`, init restart 0)
- เปิดร้านจาก browser ที่ `localhost:30080` ได้ทันที browser ติดบูธเดิม (keep-alive) ส่วน `hit.sh` เห็นครบทุกบูธ `ok=60 err=0`
- ออเดอร์จากทุกบูธรวมใน db กลาง scale 5 แล้ว EndpointSlice ตามเอง ลบบูธหนึ่งระหว่างขาย err 0–1
- ลบ Pod db: IP ใหม่ ClusterIP เดิม web ต่อใหม่เอง แต่ข้อมูลหาย หน้า 503 → ลบบูธ web 1 ตัวเพื่อเติมสินค้า ทุกบูธกลับมา ออเดอร์ 0
- `set image rs` ไม่เปลี่ยนบูธเดิม ลบทีละตัวเห็น 1.2/1.3 ปน ลบทีเดียวร้านสะดุด (err 7 จาก 200 และ 7 จาก 150)

### 10.14 เก็บกวาด LAB 10

🐧 **ใน SSH session ของ k8s-lab** (ปิด `hit.sh` ที่อาจยังรันอยู่ใน terminal อื่นด้วย Ctrl+C ก่อน)

```bash
time kubectl delete ns som-shop
kubectl get svc -A | grep 30080 || echo "(30080 ว่าง)"
docker exec lab-worker crictl images | grep som-shop
```

```text
namespace "som-shop" deleted

real	0m11.214s
...
(30080 ว่าง)
docker.io/library/som-shop-web                  1.2                  5d645cb7b669b       76.6MB
docker.io/library/som-shop-web                  1.3                  3f71969dffec2       76.6MB
```

ลบ namespace ราว 11 วินาที พอร์ต 30080 ว่างอีกครั้ง image `som-shop-web:1.2` และ `1.3` ยังอยู่บน Node **เก็บไว้ใช้ต่อในบทที่ 7** (ถ้า `k8s-down` ต้อง build และ `kind load` ใหม่)

### คำถามท้าย LAB 10

1. ทำไม `DATABASE_URL` จึงใช้ `som-db:5432` แทน IP ของ Pod db ถ้าใส่ IP `10.244.2.21` ไว้ ข้อ 10.9 จะเกิดอะไรขึ้น
2. ทำไม Service `som-db` จึงเป็น ClusterIP ไม่ใช่ NodePort และทำไม ReplicaSet `som-db` ต้องมี `replicas: 1` ถ้าตั้งเป็น 3 ลูกค้าจะเห็นออเดอร์อย่างไร
3. ถ้าแอปรุ่น 1.2 ไม่มี advisory lock ใน `seed.mjs` แต่ยัง scale เป็น 3 บูธพร้อมกัน จะเห็นอะไรใน `INIT_RESTARTS` และ log ของ `db-seed` และควรแก้แบบไหนอีกบ้าง
4. หลังลบ Pod db ทำไมหน้าเว็บ 503 ทั้งที่บูธ web ยัง `1/1 Ready` และทำไมการลบบูธ web แค่ 1 ตัวจึงทำให้ **ทุก** บูธกลับมาขายได้
5. เทียบตัวเลข err ของ "ลบบูธ 1 ตัวระหว่างขาย" (ข้อ 10.8) กับ "ลบทั้งหมดในคำสั่งเดียว" (ข้อ 10.12) อธิบายว่าทำไมต่างกันมาก และเครื่องมือที่จะเปลี่ยนรุ่นแบบไม่สะดุดควรทำอะไรให้อัตโนมัติบ้าง

> **🏆 ท้าทาย:** เพิ่ม `sessionAffinity: ClientIP` ให้ Service `som-web` แล้วรัน `./hit.sh` ใหม่ ผลเปลี่ยนไปอย่างไร จากนั้นทำข้อ 10.12 แบบที่ 1 อีกครั้ง (ลบบูธที่ hit.sh ติดอยู่) บันทึกว่าลูกค้าเห็นอะไรระหว่างบูธนั้นถูกลบ และอธิบายว่าทำไม (เอกสารนี้ไม่ได้เฉลยผล ให้ทดลองเอง)

> **ปูทางบทหน้า:** น้องส้มเปลี่ยนร้านเป็น 1.3 ได้ แต่ต้องรื้อบูธเองจนร้านสะดุด บทที่ 7 จะใช้ **Deployment** เป็น "ผู้จัดการร้าน" ที่สั่ง ReplicaSet รุ่นใหม่และรุ่นเก่า เปลี่ยนทีละบูธโดยรอไฟเขียว และย้อนรุ่นได้ โดยใช้ Service `som-db`/`som-web` และ image `som-shop-web:1.2`/`1.3` ของบทนี้ต่อได้ทันที

---

