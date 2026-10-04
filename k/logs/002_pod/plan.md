# แผนบทเรียน 002 — Kubernetes Pod (Pod ตัวแรกของน้องส้ม)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README และยังไม่รัน LAB)
> Storyboard ภาพ: `logs/002_pod/images.json` (Theory 32 ภาพ, LAB 16 ภาพ)
> ภาพตัวละครอ้างอิง: `002_kubernetes_pod/01_Theory/images/00-character-som.png`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่านบท 001 แล้ว (ทฤษฎีสถาปัตยกรรม + ตรวจเครื่องมือใน container `k8s-lab`) **แต่ยังไม่มีคลัสเตอร์** → LAB0 ต้องเริ่มด้วย `k8s-up` (kind cluster `lab`: `lab-control-plane` + `lab-worker` + `lab-worker2`, context `kind-lab`)
- เข้าเครื่อง: `ssh -p 2223 root@localhost` (รหัส `passwd`) หรือ JupyterLab `http://localhost:8889`
- **ห้ามใช้ Service / NodePort / Deployment / ReplicaSet / Ingress ใน LAB** — พอร์ต 30080–30082 ยังไม่ใช้ในบทนี้
- การเข้าถึงแอป: `kubectl exec`, `kubectl logs`, `kubectl port-forward` (ฟังที่ 127.0.0.1 ใน k8s-lab) + `ssh -p 2223 -L <port>:localhost:<port> root@localhost` จากเครื่องนักศึกษาเพื่อเปิดใน browser
- อุปมาเดียวตลอดบท (ต่อจาก 001):

| Kubernetes | อุปมาท่าเรือ |
|---|---|
| container | ตู้สินค้า (shipping container) |
| Pod | ห้องโดยสาร/กล่องห่อตู้ (cabin box) มีป้าย IP เดียว 1 ป้าย |
| Node | เรือ (`lab-worker`, `lab-worker2`) |
| Control Plane | หอบังคับการบนท่า (`lab-control-plane`) |
| kube-scheduler | เจ้าหน้าที่วางแผนจัดตู้ขึ้นเรือ |
| kubelet | ต้นเรือ (first mate) ประจำเรือแต่ละลำ |
| image registry | โกดังต้นแบบตู้สินค้า |
| emptyDir | ชั้นวางของร่วมในห้องโดยสาร (หายเมื่อห้องถูกรื้อ) |
| label | ป้ายแท็กห้อยกล่อง |
| probe | เจ้าหน้าที่ตรวจสุขภาพ (หูฟังแพทย์) |
| init container | ทีมเตรียมงานที่ต้องทำเสร็จก่อนเปิดร้าน |
| sidecar | ผู้ช่วยที่ทำงานคู่ตลอดเวลา |

- เรื่องเล่า: น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes อยากเปิด "ร้านอาหารแมวน้องส้ม" บนเรือ จึงต้องเรียนรู้การจัดกล่อง Pod ตั้งแต่ใบสั่งงาน YAML จนเปิดร้านจริงใน LAB สุดท้าย และจบด้วยปัญหา "กล่องหายแล้วไม่มีใครสร้างใหม่" → ปูทาง Deployment/Service

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001: รายวิชา/หัวข้อ/CLO, บทคัดย่อ, วัตถุประสงค์การเรียนรู้, สารบัญ, สารบัญรูปภาพ (ตาราง), ภาพแบบ `<p align="center" id="fig-N">`

1. **บทนำ: น้องส้มอยากเปิดร้าน** — ทบทวนอุปมาท่าเรือจากบท 001, เป้าหมายบทนี้ (ภาพ T01–T02)
2. **Pod คืออะไร** — หน่วยเล็กที่สุดที่ deploy ได้, ห่อ container ≥1, มี IP เดียว, แชร์ volume ได้, อยู่บน Node เดียวเสมอ, ไม่สร้าง container เดี่ยว ๆ ใน K8s (T03)
3. **ทำไมต้องมี Pod ไม่ใช้ container ตรง ๆ** — container ที่ต้อง "อยู่ด้วยกัน ไปด้วยกัน", 1 Pod = 1 instance ของแอป, แนวปฏิบัติ: ปกติ 1 แอปหลักต่อ Pod (T04)
4. **Pod กับ Node** — scheduler เลือก Node ครั้งเดียว, Pod ไม่ย้ายเรือ, container ใน Pod ไม่แยก Node, control-plane ของ kind มี taint จึงไม่รับ Pod ทั่วไป (T05)
5. **เครือข่ายของ Pod**
   - 5.1 หนึ่ง Pod หนึ่ง IP (network namespace ร่วม, pause/sandbox), คุยกันผ่าน `localhost`, ห้ามใช้ port ชนกันใน Pod เดียว (T06)
   - 5.2 Pod-to-Pod ด้วย Pod IP ผ่าน CNI (kind: 10.244.x.x), IP เปลี่ยนเมื่อสร้าง Pod ใหม่ → ทำไมต้องมี Service ในบทหน้า (T07)
6. **เส้นทางการเกิดของ Pod** — kubectl → kube-apiserver → etcd → kube-scheduler → kubelet → container runtime (pull image, create, start) → Running (T08)
7. **พื้นฐาน YAML**
   - 7.1 key: value, map ซ้อนด้วยการเยื้อง (space เท่านั้น ปกติ 2), list ด้วย `-`, string/number/boolean, quote, comment `#`, multi-document `---`, block scalar `|` (T09)
   - 7.2 ข้อผิดพลาดยอดฮิต: ใช้ Tab, ลืมเว้นวรรคหลัง `:`, เยื้องผิดระดับ, ตัวเลขที่ควรเป็น string (เช่น env value `"5432"`) (T10)
8. **โครงสร้าง Kubernetes manifest**
   - 8.1 สี่ส่วนหลัก `apiVersion: v1`, `kind: Pod`, `metadata` (name, namespace, labels, annotations), `spec` (T11)
   - 8.2 `spec` (desired) vs `status` (ระบบเขียน) — ดูด้วย `kubectl get pod -o yaml` (T12)
9. **เขียน spec ของ container**
   - 9.1 `name`, `image` (ระบุ tag เสมอ หลีกเลี่ยง `latest`), `imagePullPolicy` (IfNotPresent/Always/Never), `ports.containerPort` เป็นข้อมูลประกอบ (ไม่ได้เปิด/ปิด port) (T13)
   - 9.2 `env` (name/value, value ต้องเป็น string) — ตัวอย่างรหัสผ่านใน env เป็นแค่เพื่อการเรียน บทหน้าใช้ Secret (T14)
   - 9.3 `command`/`args` ทับ ENTRYPOINT/CMD ของ Dockerfile (ตาราง 4 กรณี) (T15)
   - 9.4 `resources.requests` (ใช้ตัดสินใจ scheduling) / `limits` (CPU ถูก throttle, memory เกิน → OOMKilled), หน่วย `m`, `Mi`, Pending เมื่อไม่มี Node รับไหว, QoS class (Guaranteed/Burstable/BestEffort) แบบสั้น (T16)
10. **Labels, Selectors และ Annotations** — key/value, กฎการตั้งชื่อ, `-l app=shop`, `-l 'tier in (web,db)'`, `--show-labels`, `-L`, `kubectl label`; annotations สำหรับข้อมูลประกอบ (T17)
11. **เครื่องมือช่วยเขียน YAML** — `kubectl explain pod.spec.containers --recursive`, `kubectl run ... --dry-run=client -o yaml > pod.yaml`, `kubectl apply` vs `create`, `kubectl diff`, `kubectl delete -f` (T18)
12. **วงจรชีวิตของ Pod**
    - 12.1 Pod phase: Pending, Running, Succeeded, Failed, Unknown — และ STATUS ใน `kubectl get pods` (ContainerCreating, Completed, CrashLoopBackOff) **ไม่ใช่ phase** (T19)
    - 12.2 container state Waiting/Running/Terminated, `restartPolicy` Always (ค่าเริ่มต้น)/OnFailure/Never, RESTARTS, kubelet restart container ใน Pod เดิม (ไม่ใช่สร้าง Pod ใหม่) (T20)
    - 12.3 CrashLoopBackOff: exponential back-off 10s → 20s → 40s … สูงสุด 5 นาที, ดู `kubectl logs --previous` (T21)
    - 12.4 ErrImagePull / ImagePullBackOff: tag ผิด, ชื่อผิด, private registry, image local ที่ยังไม่ `kind load` (T22)
    - 12.5 Pending จาก resources ไม่พอ / CreateContainerConfigError / OOMKilled (ตาราง สาเหตุ → อาการ → คำสั่งตรวจ)
13. **Probes ตรวจสุขภาพ**
    - 13.1 startupProbe / livenessProbe / readinessProbe — ใครตรวจ (kubelet), ล้มเหลวแล้วเกิดอะไร (T23)
    - 13.2 กลไก httpGet / tcpSocket / exec (+grpc), พารามิเตอร์ initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold (T24)
    - หมายเหตุ: readiness ล้ม → READY 0/1 (Pod ยัง Running ไม่ถูก restart) ผลต่อ traffic จะเห็นชัดเมื่อเรียน Service
14. **Volumes ภายใน Pod: emptyDir** — `volumes` ระดับ Pod + `volumeMounts` ระดับ container, อายุเท่า Pod (รอด container restart, หายเมื่อลบ Pod), `medium: Memory`, `sizeLimit`; preview PVC บทถัดไป (T25)
15. **Multi-container Pod**
    - 15.1 Init container: รันตามลำดับทีละตัว ต้องสำเร็จ (exit 0) ก่อน app container, ล้ม → restart ตาม restartPolicy, STATUS `Init:0/2` (T26)
    - 15.2 Sidecar: แบบดั้งเดิม (container คู่ใน `containers`) และ **native sidecar** (`initContainers` + `restartPolicy: Always`, GA ตั้งแต่ K8s 1.33) — เริ่มก่อน app, อยู่ตลอดอายุ Pod (T27)
    - 15.3 รูปแบบอื่นโดยย่อ: adapter, ambassador; เมื่อไรควร/ไม่ควรรวม container ไว้ Pod เดียว (scale แยกไม่ได้)
16. **เข้าถึงและดีบัก Pod** — `get -o wide`, `describe` (Events), `logs [-c] [-f] [--previous]`, `exec -it [-c] -- sh`, `port-forward`, `get events --sort-by=.lastTimestamp`, `kubectl debug` (กล่าวถึง) (T28)
    - 16.1 เปิดเว็บจากเครื่องนักศึกษา: browser → `ssh -L` → k8s-lab → `kubectl port-forward` → Pod (T29)
17. **Pod เป็นของชั่วคราว** — ลบ Pod เดี่ยวแล้วไม่มีใครสร้างคืน, Pod ใหม่ = ชื่อ/IP/ข้อมูล emptyDir ใหม่, แก้ field ส่วนใหญ่ของ Pod ที่รันอยู่ไม่ได้ (immutable) ต้องลบสร้างใหม่ (T30)
18. **ปูทางบทหน้า: Deployment และ Service** — Deployment ดูแลจำนวน Pod/สร้างใหม่อัตโนมัติ, Service ให้ที่อยู่คงที่ (เป็นภาพ preview เท่านั้น) (T31)
19. **สรุปและคำถามทบทวน** (T32) + เอกสารอ้างอิง (kubernetes.io: Pods, Pod Lifecycle, Init Containers, Sidecar Containers, Probes, Volumes, YAML)

## 2. รายการ LAB (`02_LAB/README.md`)

โครงไฟล์ LAB ที่จะสร้าง (ในบทถัดไปของงาน):

```text
02_LAB/
  README.md
  images/ (L01–L16 + imagegen-prompts.md)
  labs/
    lab02-first-yaml/nginx-pod.yaml
    lab04-labels/shop-pods.yaml
    lab05-lifecycle/{completed-pod,crash-pod,onfailure-pod,bad-image-pod}.yaml
    lab06-env-resources/{env-command-pod,oom-pod,pending-pod}.yaml
    lab07-probes/{liveness-exec-pod,readiness-http-pod}.yaml
    lab08-multi-container/{shared-localhost-pod,init-sidecar-pod}.yaml
  som-shop/  (LAB สุดท้าย ดูหัวข้อ 3)
```

ทุก LAB รันใน SSH session ของ `k8s-lab` ยกเว้นขั้น `ssh -L` และ browser บนเครื่องนักศึกษา ทุก LAB จบด้วยการลบ Pod ของตัวเอง

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | ผลที่ต้องเห็น |
|---|---|---|---|---|
| 0 | สร้างคลัสเตอร์ท่าเรือ | `k8s-up`, `kubectl config current-context`, `get nodes -o wide`, `get pods -A` | (ไม่มี ใช้ `k8s-up`) | context `kind-lab`; 3 node `Ready` (`lab-control-plane`, `lab-worker`, `lab-worker2`); system pods ใน `kube-system` Running |
| 1 | Pod แรกด้วย `kubectl run` | สร้าง/ดู/อธิบาย/ลบ Pod แบบ imperative | – | `kubectl run hello --image=nginx:1.27-alpine` → `get pods -o wide` เห็น `1/1 Running`, IP 10.244.x.x, NODE เป็น worker; `describe` เห็น Events Scheduled→Pulling→Pulled→Created→Started; ลบแล้วหายถาวร |
| 2 | Pod YAML แรก | YAML → apply | `labs/lab02-first-yaml/nginx-pod.yaml` | `kubectl run web --image=nginx:1.27-alpine --dry-run=client -o yaml` ได้โครง; `kubectl explain pod.spec.containers.ports`; `apply -f` → `pod/web created`; `get pod web -o yaml` เห็นทั้ง spec และ status (podIP, phase Running); `apply` ซ้ำ → `unchanged`; `delete -f` |
| 3 | เข้าไปใน Pod: exec / logs / port-forward | สำรวจ container, เปลี่ยนหน้าเว็บ, เปิดใน browser | ใช้ nginx-pod.yaml | `exec -it web -- sh` แก้ `/usr/share/nginx/html/index.html` เป็น "สวัสดีจากน้องส้ม"; `port-forward pod/web 8080:80` + `curl localhost:8080` (อีกหน้าต่าง) ได้ HTML; บนเครื่องนักศึกษา `ssh -p 2223 -L 8080:localhost:8080 root@localhost` → browser `http://localhost:8080` เห็นหน้าเว็บ; `logs -f web` เห็น access log ของ GET / |
| 4 | Labels & Selectors | ติด/ค้น/แก้ label | `labs/lab04-labels/shop-pods.yaml` (3 Pod ใน multi-doc: `shop-web` app=som-shop,tier=web / `shop-cache` tier=cache / `toy-web` app=toy-shop,tier=web) | `--show-labels`; `-l app=som-shop` ได้ 2 Pod; `-l tier=web` ได้ 2; `-l 'tier in (web,cache)'`; `-L app,tier`; `kubectl label pod toy-web env=dev`, `--overwrite`, ลบด้วย `env-`; `kubectl annotate`; `delete -l app=som-shop` |
| 5 | Lifecycle & Debug error | อ่าน phase/STATUS/RESTARTS และไล่หาสาเหตุ | `labs/lab05-lifecycle/*.yaml` | `completed-pod` (busybox:1.36 echo แล้ว exit 0, restartPolicy Never) → `Completed`, phase Succeeded; `crash-pod` (exit 1, Always) → RESTARTS เพิ่ม, `CrashLoopBackOff`, `logs --previous`, `describe` เห็น Back-off; `onfailure-pod` เปรียบเทียบ; `bad-image-pod` (`nginx:9.99-doesnotexist`) → `ErrImagePull`→`ImagePullBackOff`, Events "not found"; แก้ด้วยลบแล้ว apply ใหม่ด้วย tag ถูก (เพราะเปลี่ยน image ได้แต่สอนแนว delete/apply) |
| 6 | env / command / resources | ส่งค่าเข้า container, ทับคำสั่ง, จำกัดทรัพยากร | `labs/lab06-env-resources/*.yaml` | `env-command-pod`: logs แสดง `SHOP_NAME=ร้านอาหารแมวน้องส้ม`, `exec -- env`; command/args ทับ CMD; `oom-pod` (limit memory 32Mi + `tail /dev/zero`) → `OOMKilled`, Last State Terminated Reason OOMKilled exit 137; `pending-pod` (request cpu "64") → `Pending`, Events `FailedScheduling ... Insufficient cpu`; `get pod -o jsonpath='{.status.qosClass}'` |
| 7 | Probes | เห็นผล liveness vs readiness | `labs/lab07-probes/*.yaml` | `liveness-exec-pod` (busybox สร้าง `/tmp/healthy` แล้วลบหลัง 30s, exec `cat /tmp/healthy`) → Events `Liveness probe failed`, RESTARTS เพิ่ม; `readiness-http-pod` (nginx, httpGet `/ready.html`) → `0/1` จน `exec` สร้างไฟล์ → `1/1`, ลบไฟล์ → กลับ `0/1` โดย RESTARTS ไม่เพิ่ม |
| 8 | Multi-container: localhost, emptyDir, init, sidecar | ประกอบ Pod หลาย container | `labs/lab08-multi-container/*.yaml` | `shared-localhost-pod` (nginx + busybox) → `exec -c helper -- wget -qO- localhost:80` ได้หน้า nginx, `get pod -o wide` มี IP เดียว, `READY 2/2`; `init-sidecar-pod`: init `prepare` เขียน index.html ลง emptyDir → STATUS `Init:0/1` → `PodInitializing` → Running; container `web` (nginx) เสิร์ฟไฟล์ และ sidecar `menu-writer` (busybox) เขียนเวลาลงไฟล์ทุก 5s; `logs -c prepare`; kill nginx ใน container (`exec -c web -- nginx -s stop`) → restart แต่ไฟล์ยังอยู่; ลบ Pod แล้ว apply ใหม่ → ไฟล์เริ่มใหม่ |
| 9 | LAB สุดท้าย: ร้านอาหารแมวน้องส้ม | Next.js + PostgreSQL ใน Pod เดียว | `som-shop/` | ดูหัวข้อ 3 |

## 3. LAB สุดท้าย — "ร้านอาหารแมวน้องส้ม" (som-shop)

### 3.1 เหตุผลการออกแบบ (ต้องบอกนักศึกษาตรง ๆ)

- **ออกแบบเพื่อการเรียนรู้** ให้ใช้ทุกแนวคิดของบทนี้ใน Pod เดียว: multi-container, localhost, init container, native sidecar, emptyDir, env, resources, probes, port-forward
- ในงานจริง **ไม่ควร** ใส่เว็บกับฐานข้อมูลใน Pod เดียว (scale แยกไม่ได้, ลบ Pod = ข้อมูลหาย, อัปเดตเว็บต้องรีสตาร์ท DB ด้วย) — บทหน้าจะแยกเป็น Deployment (web) + StatefulSet/PVC (db) + Service
- รหัสผ่าน DB อยู่ใน env ตรง ๆ เพื่อการเรียนเท่านั้น บทหน้าเปลี่ยนเป็น Secret

### 3.2 ทำไม Postgres ต้องเป็น native sidecar

init container ปกติรันจนจบก่อน app container ทุกตัว ถ้าวาง Postgres ไว้ใน `containers` แล้วให้ init container "รอ DB" จะรอไม่มีวันจบ (deadlock) จึงวาง Postgres ใน `initContainers` พร้อม `restartPolicy: Always` (native sidecar, GA ใน K8s 1.33; ต้องตรวจเวอร์ชัน node ของ kind ตอนทดสอบ LAB ด้วย `kubectl get nodes -o wide`) → kubelet เริ่ม `db` ก่อน รอ startupProbe ผ่าน แล้วจึงรัน init ถัดไป และ `db` ทำงานต่อตลอดอายุ Pod

### 3.3 สถาปัตยกรรม Pod `som-shop`

```text
Pod som-shop  (labels: app=som-shop, part=all-in-one)   IP เดียว เช่น 10.244.1.7   อยู่บน lab-worker หรือ lab-worker2
├─ initContainers (ลำดับ)
│  1. db           postgres:17-alpine    restartPolicy: Always (native sidecar)  :5432
│  2. wait-for-db  postgres:17-alpine    until pg_isready -h localhost -p 5432 …  (exit 0)
│  3. db-seed      som-shop-web:1.0      node scripts/seed.mjs  (CREATE TABLE IF NOT EXISTS + seed ถ้าตารางว่าง)
├─ containers
│  └─ web          som-shop-web:1.0      Next.js (standalone, node server.js) :3000
└─ volumes
   └─ db-data      emptyDir {}  → mount ที่ db:/var/lib/postgresql/data
```

| container | image | env | ports | probes | resources (req / limit) |
|---|---|---|---|---|---|
| db | `postgres:17-alpine` (pin minor ตอนทดสอบ เช่น 17.x) | `POSTGRES_USER=som`, `POSTGRES_PASSWORD=meow1234`, `POSTGRES_DB=catshop`, `PGDATA=/var/lib/postgresql/data/pgdata` | 5432 | startupProbe + readinessProbe exec `pg_isready -U som -d catshop -h 127.0.0.1` (period 2s, failureThreshold 30) ; livenessProbe tcpSocket 5432 | 100m/256Mi — 500m/512Mi |
| wait-for-db | `postgres:17-alpine` | – | – | – | 10m/16Mi — 100m/64Mi |
| db-seed | `som-shop-web:1.0` | `DATABASE_URL=postgres://som:meow1234@localhost:5432/catshop` | – | – | 50m/64Mi — 300m/256Mi |
| web | `som-shop-web:1.0` (`imagePullPolicy: IfNotPresent`) | `DATABASE_URL` (เหมือนบน), `SHOP_NAME=ร้านอาหารแมวน้องส้ม`, `PORT=3000`, `HOSTNAME=0.0.0.0` (ให้ Next.js standalone ฟังทุก interface; หน้าเว็บแสดงชื่อ Pod จาก `os.hostname()`) | 3000 | readinessProbe + livenessProbe httpGet `/api/health` :3000 | 100m/192Mi — 500m/512Mi |

หมายเหตุ: Postgres 18 เปลี่ยน path ข้อมูลเริ่มต้น จึง pin 17 เพื่อให้ mountPath ตรงตามเอกสาร; ตั้ง `PGDATA` เป็นโฟลเดอร์ย่อยเพื่อเลี่ยงปัญหา directory ไม่ว่าง

### 3.4 แอป Next.js (`som-shop/app/`)

- Next.js 16 (App Router, pin เวอร์ชันตอน build) + `pg` (node-postgres), `output: 'standalone'`
- Dockerfile multi-stage: `node:22-alpine` (deps → build → runner, non-root user `node`), copy `scripts/seed.mjs` และ `node_modules/pg` เข้า runner, `CMD ["node","server.js"]`
- หน้า/route:
  - `/` (dynamic, `export const dynamic = 'force-dynamic'`) แสดงชื่อร้าน, การ์ดสินค้าจากตาราง `products` (ชื่อ, ราคา บาท, stock), ปุ่ม "สั่งซื้อ", จำนวนออเดอร์ทั้งหมด, footer "เสิร์ฟโดย Pod: <hostname>"
  - `GET /api/health` → `SELECT 1` สำเร็จ = 200 `{"ok":true,"db":"up"}` ไม่สำเร็จ = 503
  - `GET /api/products` → JSON รายการสินค้า
  - `POST /api/orders` `{product_id, qty}` → insert orders + ลด stock (transaction)
- ไฟล์: `package.json`, `next.config.mjs`, `app/layout.tsx`, `app/page.tsx`, `app/OrderButton.tsx`, `app/api/health/route.ts`, `app/api/products/route.ts`, `app/api/orders/route.ts`, `lib/db.ts`, `scripts/seed.mjs`, `public/som.png` (ภาพน้องส้ม), `Dockerfile`, `.dockerignore`
- Manifest: `som-shop/k8s/som-shop-pod.yaml`

### 3.5 Schema และข้อมูลตั้งต้น (`scripts/seed.mjs`)

```sql
CREATE TABLE IF NOT EXISTS products (
  id          SERIAL PRIMARY KEY,
  sku         TEXT UNIQUE NOT NULL,
  name_th     TEXT NOT NULL,
  category    TEXT NOT NULL CHECK (category IN ('dry','wet','treat')),
  price_baht  NUMERIC(8,2) NOT NULL CHECK (price_baht >= 0),
  stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  emoji       TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS orders (
  id          SERIAL PRIMARY KEY,
  product_id  INTEGER NOT NULL REFERENCES products(id),
  qty         INTEGER NOT NULL CHECK (qty > 0),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| sku | name_th | category | price_baht | stock |
|---|---|---|---:|---:|
| DRY-TUNA-15 | อาหารเม็ดสูตรปลาทูน่า 1.5 กก. | dry | 459 | 20 |
| DRY-KITTEN-1 | อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก. | dry | 389 | 15 |
| DRY-SENIOR-12 | อาหารเม็ดแมวสูงวัย 1.2 กก. | dry | 499 | 10 |
| WET-SABA-85 | อาหารเปียกปลาซาบะ 85 ก. | wet | 35 | 60 |
| TRT-LICK-4 | ขนมแมวเลียรสไก่ (แพ็ก 4) | treat | 59 | 40 |
| TRT-SALMON-40 | ขนมฟรีซดรายแซลมอน 40 ก. | treat | 129 | 25 |

seed ใช้ `INSERT … ON CONFLICT (sku) DO NOTHING` → รันซ้ำได้ (idempotent) ตอน container restart

### 3.6 ขั้นตอน LAB 9 และผลที่ต้องเห็น

1. `cd /workspace/.../som-shop/app && docker build -t som-shop-web:1.0 .` → image ใน dockerd ของ k8s-lab
2. `kind load docker-image som-shop-web:1.0 --name lab` (และแนะนำ `docker pull postgres:17-alpine && kind load docker-image postgres:17-alpine --name lab` เพื่อเลี่ยง rate limit) → `docker exec lab-worker crictl images | grep som-shop` เห็น image บน node
3. `kubectl apply -f k8s/som-shop-pod.yaml` แล้ว `kubectl get pod som-shop -w` → `Init:0/3` → `Init:1/3` → `Init:2/3` → `PodInitializing` → `Running` READY `2/2` (web + native sidecar db; ยืนยันการนับ READY ของ sidecar ตอนทดสอบจริง)
4. `kubectl logs som-shop -c wait-for-db`, `-c db-seed` ("seeded 6 products"), `-c db`, `-c web`
5. `kubectl exec -it som-shop -c db -- psql -U som -d catshop -c 'SELECT sku,name_th,price_baht,stock FROM products;'` → 6 แถว
6. `kubectl exec som-shop -c web -- wget -qO- http://localhost:3000/api/health` → `{"ok":true,"db":"up"}` (พิสูจน์ localhost ร่วม)
7. `kubectl port-forward pod/som-shop 3000:3000` + บนเครื่องนักศึกษา `ssh -p 2223 -L 3000:localhost:3000 root@localhost` → browser `http://localhost:3000` เห็นร้าน, กดสั่งซื้อ 2 ครั้ง stock ลด
8. ทดสอบ container restart: `kubectl exec som-shop -c db -- su postgres -c 'pg_ctl stop -m fast'` (หรือ `kill 1` ตามที่ทดสอบได้จริง) → RESTARTS ของ db เพิ่ม, web READY ชั่วคราวเป็น 0 แล้วกลับ, ออเดอร์ยังอยู่ (emptyDir รอด)
9. ทดสอบลบ Pod: `kubectl delete pod som-shop` แล้ว `apply` ใหม่ → IP ใหม่, ออเดอร์หาย stock กลับค่าเริ่มต้น (emptyDir หายพร้อม Pod) → ไม่มีใครสร้าง Pod คืนให้เองระหว่างที่ยังไม่ apply
10. คำถามท้าย LAB + ปูทางบทหน้า: แยก web เป็น Deployment, db เป็น StatefulSet+PVC, เชื่อมด้วย Service, ย้ายรหัสผ่านไป Secret

## 4. Storyboard ภาพ (สรุป — รายละเอียด prompt ใน images.json)

- Theory T01–T32: เปิดเรื่อง → อุปมา → Pod/Node/Network → เส้นทางการเกิด → YAML → manifest → container spec → labels → เครื่องมือ → lifecycle/errors → probes → emptyDir → init/sidecar → debug/port-forward → ephemeral → preview → สรุป
- LAB L01–L16: ภาพเปิดเรื่อง LAB0–LAB8 (L01–L09) และ LAB สุดท้าย 7 ภาพ (L10–L16: หน้าร้าน, สถาปัตยกรรม Pod, ลำดับ init, build+kind load, port-forward+ssh -L, emptyDir รอด/หาย, ปูทางบทหน้า)
- ภาพที่อนุญาตให้มี Service/Deployment: T31 และ L16 เท่านั้น (ภาพ preview บทหน้า)
