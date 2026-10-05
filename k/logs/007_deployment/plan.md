# แผนบทเรียน 007 — Kubernetes Deployment (ผู้จัดการร้านที่เปลี่ยนรุ่นทีละบูธและพลิกสมุดย้อนรุ่นได้)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB และยังไม่รัน LAB)
> แตกจากบทรวม `logs/005_rs_deploy_svc/` (อ่านอย่างเดียว) ตามสัญญา `logs/005_replicaset/scratch/split-contract.md`
> Storyboard ภาพ: `logs/007_deployment/images.json` (Theory 36 ภาพ T01–T36, LAB 23 ภาพ L01–L23) สร้างจาก `logs/007_deployment/build_images.py` (ใช้ `imgcommon.py` ร่วม — ห้ามแก้) → ได้ `images.json`, `image-sources.tsv`, `007_kubernetes_deployment/01_Theory/images/imagegen-prompts.md`, `007_kubernetes_deployment/02_LAB/images/imagegen-prompts.md`
> ภาพตัวละครอ้างอิง: `007_kubernetes_deployment/01_Theory/images/00-character-som.png`
> ที่มาของภาพแต่ละภาพ: `logs/007_deployment/README-split.md`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่าน 001 (k8s-lab, kind `lab`: lab-control-plane / lab-worker / lab-worker2, K8s v1.37, kubectl 1.37; `ssh -p 2223 root@localhost` รหัส `passwd`, JupyterLab `http://localhost:8889`; พอร์ต 30080–30082 ของเครื่องนักศึกษา map ตรงเข้า NodePort ของ lab-control-plane), 002 (Pod, YAML, labels, probes, init/native sidecar, ร้าน all-in-one), 003 (scheduling, drain, Node ล่ม, Downward API), 004 (Namespace, quota, PSA, NetworkPolicy, DNS search domain, `som-shop-web:1.1`), **005 (ReplicaSet: template, selector, ownerReferences, รับเลี้ยง Pod หลง, `--cascade=orphan`, แก้ template แล้ว Pod เดิมไม่เปลี่ยน)** และ **006 (Service: ClusterIP, EndpointSlice, DNS, NodePort 30080, readiness ↔ endpoints, endpoint `terminating`, `hit.sh`, ร้าน `som-shop-v2` แยก web/db ด้วย ReplicaSet + `som-shop-web:1.2/1.3`)**
- โฟลเดอร์ LAB: `docker cp 007_kubernetes_deployment k8s-lab:/workspace/` แล้ว `cd /workspace/007_kubernetes_deployment/02_LAB`
- **ใช้ได้ในขั้นตอน LAB:** Pod, label, probe, init container, ReplicaSet, Service (ClusterIP/NodePort), EndpointSlice, Deployment, `kubectl rollout`
- **ห้ามใช้ในขั้นตอน LAB (ปูทางเท่านั้น):** PVC/PV/StatefulSet, Ingress/Gateway, HPA, ConfigMap/Secret แบบละเอียด (ยังใช้ env ตรง ๆ แบบบท 002–006), Job/CronJob
- ทุก LAB ทำใน namespace ของตัวเองและจบด้วย `kubectl delete ns ...` (LAB1–3 ใช้ `deploy-lab` ต่อเนื่องกันแล้วลบตอนจบ LAB3); Pod busybox ใส่ `terminationGracePeriodSeconds: 1`; NodePort `30080` ใช้ใน LAB7 และ LAB10 เท่านั้น → LAB7 ต้องลบ ns ก่อนถึง LAB10
- image: `nginx:1.27-alpine` / `nginx:1.28-alpine` (ให้ Node pull เอง — pre-check #6), `busybox:1.36` (client), tag ที่ไม่มีจริง `nginx:9.99-nope`, `postgres:17.11-alpine` (Node pull เอง หรือ `docker save --platform linux/amd64 ... -o <ไฟล์ใน workspace>` + `kind load image-archive ... --name lab`), `som-shop-web:1.2` / `1.3` (build ในบท 006 — ถ้าคลัสเตอร์ใหม่ build จาก `/workspace/006_kubernetes_service/02_LAB/som-shop-v2/app` ด้วย build-arg `APP_VERSION`/`APP_THEME` แล้ว `kind load docker-image ... --name lab`), `som-shop-web:1.4` **ไม่มีจริง**
- แอปตัวอย่าง LAB1–9 (ไม่ต้อง build): `nginx` ที่ `command` เขียน `index.html` = `web $VERSION from $(hostname)` แล้ว `exec nginx -g 'daemon off;'` + `readinessProbe httpGet / periodSeconds 2` → curl/wget เห็นเวอร์ชันและชื่อ Pod
- kubectl 1.37 พิมพ์ `pod "x" deleted from <ns> namespace` (pre-check #4)

### ผล pre-check ที่เกี่ยวข้อง (คัดลอกจาก `logs/005_rs_deploy_svc/precheck.md` เลขข้อเดิม)

| # | คำถาม | ผลจริง | ผลต่อแผนบท 007 |
|---|---|---|---|
| 4 | ลบ Pod ของ RS | ตัวใหม่ขึ้นภายใน ~3 วิ (ตัวเก่ายัง Terminating อยู่ก็สร้างแล้ว); ownerReferences `{"kind":"ReplicaSet","name":"snack-rs","controller":true,"blockOwnerDeletion":true}`; kubectl 1.37 พิมพ์ `pod "x" deleted from default namespace` | LAB1 ลบ Pod ของ Deployment; ข้อความรูปแบบใหม่ |
| 5 | ค่า default ของ Deployment | `{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"}`, `revisionHistoryLimit: 10` (progressDeadlineSeconds default 600) ; label `pod-template-hash=6f58b8bd67` ทั้งบน RS และ Pod | ทฤษฎี 2–4, LAB1, ภาพ T09 |
| 6 | `kind load docker-image nginx:1.27-alpine` | **ล้มเหลว** `ctr: content digest sha256:...: not found` แต่ Node ดึง image จาก Docker Hub เองได้ | LAB ไม่ kind load nginx/busybox; som-shop-web ยังต้อง kind load |
| 7 | rolling update 3 replicas (nginx 1.27→1.28, readiness ทุก 2 วิ) | 14 วิ (รวม pull 1.28); Events: `Scaled up replica set web-7c987cc6b4 from 0 to 1` → `Scaled down ... web-6f58b8bd67 from 3 to 2` → up 1→2 → down 2→1 → up 2→3 → down 1→0; RS เก่าเหลือ `0 0 0` | ภาพ T11 (7 แถวตาม Events), LAB2 |
| 8 | change-cause | `kubectl annotate deploy web kubernetes.io/change-cause=...` ใช้ได้; **กับดัก:** revision ถัดไปที่ไม่ได้ annotate ใหม่ (image พัง) สืบทอดข้อความเดิม `v2 nginx 1.28`; `rollout undo` ย้าย revision 2 → **4** (history เหลือ 1, 3, 4) | ทฤษฎี 8, LAB3, ภาพ T21–T23 |
| 9 | `rollout undo` บน object ที่สร้างด้วย apply | `Warning: resource deployments/web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation ...` | ภาพ T24, LAB3 |
| 10 | image ผิด + `progressDeadlineSeconds: 30` | Pod ใหม่ `ErrImagePull` (ต่อมา `ImagePullBackOff`), RS ใหม่ `1 1 0`, RS เก่ายัง `3 3 3`; `rollout status` → `error: deployment "web" exceeded its progress deadline` (exit 1); `get deploy` → `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`; condition `Progressing=False ProgressDeadlineExceeded: ReplicaSet "web-58b898d795" has timed out progressing.`; ระหว่างนั้นยิง 6 ครั้งได้ครบจาก Pod เก่า 3 ตัว | ทฤษฎี 7, LAB6, LAB10 ขั้น 5, ภาพ T19/T20/L10/L20 |
| 12 | Pod ไม่ ready | Pod `0/1 Running`; คอลัมน์ ENDPOINTS ยังแสดง IP แต่ `conditions.ready=false` | LAB5 (readiness ล้มระหว่าง rollout) |
| 19 | NodePort ผ่าน extraPortMappings จากนอก container | host `:30090`/`:30091` (map → 30080/30081 ของ container → kind control-plane) ได้หน้าเว็บ และกระจายหลาย Pod | LAB7/LAB10 ใช้ `localhost:30080` (บท 006 ยืนยันบน k8s-lab จริงแล้วหรือยัง — ดูผลบท 006) |
| 20 | browser keep-alive | Chromium `fetch('/')` 10 ครั้ง → Pod เดียวกัน 10/10 | LAB10: browser ใช้ดูธีม; นับด้วย `hit.sh` |
| 21 | zero-downtime (nginx, 5 ครั้ง/วิ) | ไม่มี preStop: **3/150 error**; `preStop.sleep.seconds: 5`: 1/150, 0/200, 0/200 | ทฤษฎี 6, LAB7 |
| 22 | zero-downtime (som-shop Next.js ผ่าน NodePort, 10 ครั้ง/วิ) | ไม่มี preStop 3/300; preStop 5 วิ 2/300 และ 0/300; **preStop 5 วิ + `maxUnavailable: 0, maxSurge: 1`: 0/300 สองรอบ**; rollout 3 replicas 9–11 วิ; Pod Next.js ที่ถูกปิดขึ้นสถานะ `Error` ชั่วครู่ | ทฤษฎี 6, LAB7, LAB10 ขั้น 3 |
| 24 | web ต่อ db ผ่าน Service `som-db` | ได้; rollout 3 replicas 13.6 วิ | LAB10 |
| 25 | ลบ Pod db (emptyDir) | Pod ใหม่พร้อมใน 4.2 วิ; `relation "orders" does not exist`; initContainer ไม่รันซ้ำเอง ต้อง `kubectl rollout restart deploy/som-web` จึงสร้างตารางใหม่ (ข้อมูลเดิมหาย) | LAB10 ขั้น 7 (1.2 แสดงหน้า 503 เป็นมิตร — ทำในบท 006) |
| 27 | API สั่งซื้อ | `POST /api/orders` body `{"product_id":1,"qty":2}` → `{"ok":true,"order_id":1,...}` | LAB10 พิสูจน์ออเดอร์อยู่/หาย |

**ยังไม่มี pre-check (ต้องยืนยันตอนทดสอบ):** Deployment รับเลี้ยง ReplicaSet ที่ไม่มีเจ้าของ (LAB8/LAB10), เวลา rollout ร้าน som-shop ที่มี initContainer + minReadySeconds, จำนวน Pod สูงสุด/ต่ำสุดของ LAB4, ข้อความ change-cause หลัง undo, เลข revision ใน LAB3/LAB10, Event readiness 404 ของ nginx, ข้อความจริงของ som-web 1.4

### อุปมา (ของเดิม + ของใหม่บทนี้)

| Kubernetes | อุปมาท่าเรือ | ใหม่? |
|---|---|---|
| container / Pod / Node / Control Plane / Namespace | ตู้สินค้า / บูธร้าน (กล่องใส teal มีกันสาด ป้าย IP) / เรือ / หอบังคับการ / โซนทาสี | – |
| ReplicaSet / Pod template / ownerReferences | หัวหน้ากะ (หุ่นยนต์ teal ถือคลิปบอร์ดนับหัว) / พิมพ์เขียว / ป้ายเจ้าของ (บท 005) | – |
| Service / EndpointSlice / readinessProbe / NodePort | ประภาคาร / คลิปบอร์ดรายชื่อบูธ / ไฟเขียวหน้าบูธ / ประตูทางขึ้นเรือหมายเลข 30080 (บท 006) | – |
| **Deployment** | **ผู้จัดการร้าน** (หุ่นยนต์กรมท่าตัวสูง ผูกหูกระต่าย ถือสมุดบันทึกรุ่น) คุมหัวหน้ากะ 1 คนต่อ 1 รุ่น | ใหม่ |
| pod-template-hash | สติกเกอร์บาร์โค้ดประจำรุ่น (ห้ามวาดเป็นอาหาร) | ใหม่ |
| RollingUpdate / maxSurge / maxUnavailable | เปลี่ยนป้ายทีละบูธโดยร้านไม่ปิด / เพดานจำนวนบูธ / พื้นจำนวนบูธที่ต้องเปิด | ใหม่ |
| Recreate | ปิดทุกบูธก่อน (ป้าย CLOSED) แล้วเปิดใหม่ | ใหม่ |
| minReadySeconds / progressDeadlineSeconds | นาฬิกาทรายหน้าบูธใหม่ / นาฬิกาทรายของผู้จัดการ (หมดแล้วชูการ์ดแดง) | ใหม่ |
| rollout history / undo / pause | สมุดบันทึกรุ่น / ปุ่มกรอกลับ / ป้ายพัก | ใหม่ |
| preStop + terminationGracePeriodSeconds | บูธที่ถูกขีดชื่อออกจากคลิปบอร์ดแล้วยังเสิร์ฟลูกค้าคนสุดท้ายระหว่างนาฬิกาทราย ก่อนปิดชัตเตอร์ | ใหม่ |
| blue/green, canary | บูธสองแถวสีน้ำเงิน/เขียว + คันโยกที่ประภาคาร / บูธทดลองดาวเล็ก 1 ใน 10 (ห้ามวาดนก) | ใหม่ |

### เรื่องเล่า

จบบท 006 ร้านน้องส้มมีประภาคารที่ลูกค้าหาเจอเสมอ และฐานข้อมูลกลางตัวเดียว แต่ตอนอยากเปลี่ยนเป็นรุ่น 1.3 น้องส้มสั่ง `set image` ที่หัวหน้ากะแล้ว **ไม่มีอะไรเปลี่ยน** ต้องลบบูธเองทีละตัว ลูกค้าบางคนชนบูธที่กำลังปิด และพอรุ่นใหม่มีปัญหาก็ไม่มีสมุดให้ย้อนกลับ น้องส้มจึงจ้าง **ผู้จัดการร้าน** ที่สั่งหัวหน้ากะรุ่นใหม่ให้เปิดบูธทีละตัว รอไฟเขียวก่อนค่อยให้หัวหน้ากะรุ่นเก่าปิดบูธ จดทุกการเปลี่ยนลงสมุด และพลิกสมุดย้อนกลับได้ในคำสั่งเดียว บทนี้จบด้วย "ร้านแบบโปรดักชันจริง" ที่เปลี่ยนรุ่นระหว่างขายโดยไม่มีลูกค้าเจอ error รุ่นพังก็ยังขายได้ — แต่เมื่อกล่องฐานข้อมูลเกิดใหม่ ออเดอร์ทั้งหมดก็ยังหาย ซึ่งเป็นโจทย์ของบทหน้า (PVC/StatefulSet)

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001–006: รายวิชา/หัวข้อ/CLO, บทก่อนหน้า (ลิงก์บท 006), บทคัดย่อ, วัตถุประสงค์การเรียนรู้ (~12 ข้อ), สารบัญ, ตารางอุปมา; ทุก output ใช้ "ผลจริง" จาก pre-check/การรัน LAB

1. **บทนำ: เปลี่ยนรุ่นด้วยมือแล้วร้านสะดุด** (T01–T03)
   - ทบทวนท้ายบท 006: `kubectl set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3` แล้ว Pod เดิมยังเป็น 1.2 (ReplicaSet สนแค่ "จำนวน" ไม่สน "รุ่น" ของ Pod ที่มีอยู่); ลบ Pod เองทีละตัว → ช่วงที่ endpoints เหลือน้อย/ว่าง ลูกค้า error; ลบทีเดียว `delete pod -l` → ร้านล่มชั่วครู่; ไม่มีประวัติ/ย้อนรุ่น
   - สิ่งที่อยากได้: เปลี่ยนรุ่นทีละบูธ รอบูธใหม่พร้อมก่อน จำกัดจำนวนที่หาย บันทึกประวัติ ย้อนกลับได้ → Deployment
   - ภาพรวมบท + ตารางอุปมาใหม่ (T03)
2. **Deployment → ReplicaSet → Pod** (T04–T09)
   - 2.1 ความสัมพันธ์: Deployment สร้าง/คุม ReplicaSet **1 ตัวต่อ 1 template** (รุ่น), RS สร้าง Pod; ownerReferences เป็นสายโซ่ Deployment → RS → Pod (ลบ Deployment = ลบทั้งสาย)
   - 2.2 ห้ามแก้ RS ที่ Deployment เป็นเจ้าของ: `kubectl scale rs <hash-rs> --replicas=6` → Deployment controller ปรับกลับเป็นค่าของ Deployment (ยืนยันใน LAB1); แก้ template ของ RS ตรง ๆ ก็ไม่เกิด rollout (T05)
   - 2.3 manifest `apps/v1 Deployment`: `replicas`, `selector` (immutable เหมือน RS), `template` + ฟิลด์เฉพาะ `strategy`, `minReadySeconds` (default 0), `revisionHistoryLimit` (default 10), `progressDeadlineSeconds` (default 600), `paused` (T06)
   - 2.4 จุดเริ่มเขียน YAML: `kubectl create deployment web --image=nginx:1.27-alpine --replicas=3 --dry-run=client -o yaml > web.yaml` แล้วแก้ต่อ (เติม command, env, readiness) (T07)
   - 2.5 คอลัมน์ `kubectl get deploy`: `READY` (ready/desired), `UP-TO-DATE` (Pod ของ template ล่าสุด), `AVAILABLE` (ready ต่อเนื่องครบ minReadySeconds); ตัวอย่างระหว่างรุ่นพัง `READY 3/3 UP-TO-DATE 1 AVAILABLE 3` (pre-check #10) (T08)
   - 2.6 `pod-template-hash`: Deployment คำนวณ hash ของ template เติมเป็น label ใน selector/template ของ RS และ Pod (`pod-template-hash=6f58b8bd67` — pre-check #5) → ชื่อ RS `<deploy>-<hash>` และ Pod `<deploy>-<hash>-<สุ่ม 5 ตัว>` เช่น `web-6f58b8bd67-frgpm`; เหตุผล: RS สองรุ่นที่ใช้ `app=web` ร่วมกันจะไม่นับ Pod ปนกัน (โยงกับดัก label บท 005) (T09)
3. **อะไรทำให้เกิด rollout** (T10)
   - เปลี่ยน **`.spec.template`** เท่านั้น → hash ใหม่ → RS ใหม่ → revision ใหม่ (image, env, command, probe, resources, label/annotation ใน template)
   - `scale`/แก้ `replicas` ไม่สร้าง revision (RS เดิมแค่ปรับจำนวน); แก้ `strategy`/`minReadySeconds` ก็ไม่สร้าง revision
   - `kubectl rollout restart` = เติม annotation `kubectl.kubernetes.io/restartedAt: <เวลา>` ใน template → Pod ใหม่ทั้งหมดด้วย image เดิม (ใช้ "เติมสินค้าใหม่" หลัง db หายใน LAB10 แทนการลบ Pod เองแบบบท 006)
   - template เหมือน revision เก่าทุกตัวอักษร → Deployment นำ RS เก่ากลับมาใช้ (hash เดิม) ไม่สร้าง RS ใหม่
4. **RollingUpdate: maxSurge / maxUnavailable** (T11–T14)
   - 4.1 ลำดับ rolling replicas 3 ค่า default ตาม Events จริง (pre-check #7): new 0→1, old 3→2, new 1→2, old 2→1, new 2→3, old 1→0 (T11)
   - 4.2 `maxSurge` (Pod เกิน replicas ได้กี่ตัว — % ปัด **ขึ้น**) / `maxUnavailable` (ไม่พร้อมได้กี่ตัว — % ปัด **ลง**); default 25%/25% (pre-check #5); ตั้ง 0 ทั้งคู่ไม่ได้ (validation error); ตาราง: replicas 3 → +1/−0 (สูงสุด 4 พร้อมอย่างน้อย 3), 4 → +1/−1 (5/3), 10 → +3/−2 (13/8) (T12)
   - 4.3 รูปแบบที่ใช้บ่อย: `maxSurge 1, maxUnavailable 0` (ปลอดภัย ต้องมีทรัพยากรเผื่อ 1 Pod — ใช้กับ som-web), `maxSurge 0, maxUnavailable 1` (ไม่มีทรัพยากรเผื่อ), `maxSurge 100%` (เร็ว ใช้ทรัพยากร 2 เท่า)
   - 4.4 `Recreate`: scale RS เก่าเป็น 0 รอ Pod เก่าหายหมด แล้วค่อยสร้างใหม่ → มี downtime (T13); ใช้เมื่อสองรุ่นอยู่ร่วมกันไม่ได้ — ตัวอย่าง som-db: ถ้า rolling จะมี postgres 2 ตัว (ต่างคนต่าง emptyDir) และ Service som-db จะส่ง web ไปคนละฐานข้อมูล; ในอนาคตกับ volume แบบเขียนได้ทีละ Node ก็ต้อง Recreate (กล่าวถึง) (T14)
5. **readinessProbe และ minReadySeconds ตัดสินจังหวะ rollout** (T15–T16)
   - Pod ใหม่นับเป็น available เมื่อ ready ต่อเนื่องครบ `minReadySeconds` → rollout จึงลด RS เก่าได้; readiness ล้ม → rollout ค้าง (Pod `0/1 Running`) แต่ maxUnavailable กัน Pod เก่าไม่ให้ถูกลดเกิน (T15)
   - ไม่มี readinessProbe = ถือว่า ready ทันทีที่ container start → rollout เร็วเกินจริง ลูกค้าเจอ error; `minReadySeconds` ช่วยกันแอปที่ "ready แป๊บเดียวแล้วล้ม"
   - liveness ไม่ควรพึ่ง db (som-web 1.2: readiness `/api/health` ตรวจ db, liveness `/api/live` ไม่ตรวจ) — ถ้า liveness ตรวจ db แล้ว db ล่ม Pod web ทุกตัวถูก restart พร้อมกัน (T16)
6. **zero-downtime rollout** (T17–T18)
   - ลำดับการปิด Pod: Pod ถูกสั่งลบ → endpoint ใน EndpointSlice เป็น `serving/terminating` (ไม่ ready — บท 006) และ kube-proxy ทุก Node ค่อย ๆ อัปเดตกฎ **พร้อมกับ** kubelet เริ่ม `preStop` → SIGTERM → แอปปิด graceful → เกิน `terminationGracePeriodSeconds` (default 30) โดน SIGKILL (T17)
   - สูตร: readinessProbe + `maxUnavailable: 0` (`maxSurge: 1`) + `lifecycle.preStop.sleep.seconds: 5` (sleep action ไม่ต้องมี binary sleep ใน image) + grace period พอ + แอปจัดการ SIGTERM (nginx official image ใช้ STOPSIGNAL SIGQUIT = graceful)
   - ผล pre-check: nginx ไม่มี preStop 3/150 error, มี 0/200 (#21); Next.js ไม่มี preStop 3/300, preStop 5 + maxUnavailable 0 ได้ **0/300 สองรอบ** (#22); Pod Next.js ที่ถูกปิดขึ้น `Error` ชั่วครู่ (exit ไม่เป็น 0 ตอนรับ SIGTERM) ไม่ใช่ rollout พัง (T18)
7. **progressDeadlineSeconds: rollout ค้างแต่ร้านยังขาย** (T19–T20)
   - ไม่คืบหน้าเกินเวลา → condition `Progressing=False reason ProgressDeadlineExceeded` (`ReplicaSet "web-58b898d795" has timed out progressing.`), `kubectl rollout status` exit 1 `error: deployment "web" exceeded its progress deadline` (pre-check #10) (T19)
   - **Kubernetes ไม่ rollback อัตโนมัติ** — แต่ Pod เก่ายังรับลูกค้าเพราะ maxUnavailable จำกัดการลด (`READY 3/3 UP-TO-DATE 1 AVAILABLE 3`); ใช้ exit code ของ `rollout status` ใน CI/CD ตัดสินว่าจะ undo (T20)
8. **คำสั่ง rollout, history, change-cause, undo, pause, revisionHistoryLimit** (T21–T26)
   - `kubectl rollout status | history [--revision=N] | undo [--to-revision=N] | pause | resume | restart`
   - change-cause: `kubectl annotate deploy/web kubernetes.io/change-cause="v2 nginx 1.28"` (`--record` ถูกถอดแล้ว) (T21); **กับดัก** revision ถัดไปที่ลืม annotate สืบทอดข้อความเดิม (pre-check #8) → annotate ทุกครั้ง หรือใส่ annotation ใน YAML (`metadata.annotations`) พร้อมการเปลี่ยน (T22)
   - undo = เอา template ของ revision เป้าหมายมาเป็น revision ใหม่ → เลขเดิมหายจากรายการ (1, 2, 3 → undo ไป 2 → เหลือ 1, 3, 4 — pre-check #8) (T23)
   - undo บน object ที่ apply มา → `Warning: ... Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation` (pre-check #9) → undo = แก้ฉุกเฉิน แล้วแก้ YAML ใน git ให้ตรง (T24)
   - pause/resume: แก้หลายอย่าง (`set image` + `set env` + resources) ระหว่าง pause แล้ว resume ได้ revision เดียว; ระหว่าง pause `rollout undo` ใช้ไม่ได้ (T25)
   - `revisionHistoryLimit` (default 10): RS เก่าเก็บไว้ด้วย replicas 0 = ข้อมูลสำหรับ undo; เกินถูกลบ; ตั้ง 0 = undo ไม่ได้ (T26)
9. **วิธีเปลี่ยน Deployment และกับดัก apply** (T27–T28)
   - `kubectl set image deploy/web web=nginx:1.28-alpine`, `set env deploy/web VERSION=v3`, `scale`, `edit`, `patch` (เร็ว เหมาะทดลอง/ฉุกเฉิน) vs แก้ไฟล์แล้ว `apply -f` (ไฟล์ใน git เป็นความจริงหนึ่งเดียว — แนะนำ) (T27)
   - กับดัก: `scale --replicas=5` แล้วภายหลัง `apply -f` ไฟล์ที่เขียน `replicas: 3` → กลับเป็น 3; ถ้าในอนาคตใช้ตัวปรับอัตโนมัติ (HPA — บทหลัง) ให้ไม่ใส่ `replicas` ในไฟล์ (T28)
10. **ย้ายจาก ReplicaSet (บท 006) เป็น Deployment** (T29–T30)
    - Deployment controller **รับเลี้ยง ReplicaSet ที่ label ตรง selector และยังไม่มีเจ้าของ** (เติม ownerReferences ชี้ Deployment) แบบเดียวกับที่ RS รับเลี้ยง Pod หลง (บท 005); ถ้า template ต่างจากของ Deployment RS เดิมจะถูกมองเป็นรุ่นเก่า → ถูก scale ลงระหว่าง rolling ขณะ RS ใหม่ (มี hash) เพิ่มขึ้น; Pod ใหม่มี `app=web` ตรง selector ของ RS เดิมด้วย แต่มีเจ้าของแล้ว RS เดิมจึงไม่นับ — **ต้องยืนยันใน LAB8** (รวมถึงกรณี template เหมือนกันทุกตัวอักษร: คาดว่า RS เดิมถูกใช้เป็นรุ่นปัจจุบันโดยไม่เกิด rolling — เขียนตามผลจริง) (T29)
    - ทางสำรอง: `kubectl delete rs web --cascade=orphan` (Pod เดิมอยู่ต่อ ไม่มีเจ้าของ ยังอยู่หลัง Service) → apply Deployment (RS ใหม่ selector มี hash จึงไม่รับเลี้ยง Pod เดิม) → เมื่อ Deployment พร้อมจึง `kubectl delete pod -l app=web,'!pod-template-hash'` (T30)
11. **rollout พัง: อ่านอาการและแก้** (T31)
    - image ผิด: `ErrImagePull` → `ImagePullBackOff` (Events `Failed to pull image ...`); readiness ล้ม: `0/1 Running` + `Readiness probe failed`; แอปล้ม: `CrashLoopBackOff`; initContainer พัง: `Init:...`
    - ลำดับอ่าน: `rollout status` → `get deploy,rs` (RS ใหม่ `1 1 0`) → `describe deploy` (Conditions/Events) → `get pods` / `describe pod` / `logs --previous` → `rollout undo` → แก้ YAML ใน git
12. **blue/green และ canary ด้วย label + Service** (T32–T33) — ทฤษฎีสั้น + LAB9 เล็ก
    - blue/green: Deployment `web-blue` (`version=blue`) + `web-green` (`version=green`) พร้อมกัน, Service selector `app=web,version=blue` → `kubectl patch svc web` เปลี่ยนเป็น green ทีเดียว ย้อนได้ทันที ใช้ทรัพยากร 2 เท่า
    - canary: `track=stable` 9 replicas + `track=canary` 1 replica ใช้ `app=web` ร่วม → Service สุ่มตามสัดส่วนจำนวน Pod (~10%); คุมเป็นเปอร์เซ็นต์ละเอียดต้องใช้ Ingress/Gateway/service mesh (บทหลัง)
13. **สรุปและบทถัดไป** (T34–T36)
    - ตารางเลือก workload: Pod เดี่ยว (ทดลอง/debug) / ReplicaSet (แทบไม่สร้างเอง — ให้ Deployment สร้าง) / Deployment RollingUpdate (แอป stateless — ค่าเริ่มต้น) / Deployment Recreate (ห้ามมี 2 รุ่นพร้อมกัน) (T34)
    - ตารางคำสั่ง (T35): `create deployment --dry-run`, `apply -f`, `set image/env`, `scale`, `annotate change-cause`, `rollout status/history/undo/pause/resume/restart`, `get deploy,rs,pods --show-labels`
    - HPA ปูทาง: ผู้จัดการร้านปรับ `replicas` เองได้ แต่ "ปรับอัตโนมัติตามโหลด" คือ HorizontalPodAutoscaler (ชื่อ/แนวคิดเท่านั้น)
    - ปิดบท (T36): db ใน Deployment + emptyDir ยังลืมทุกอย่าง → PVC/StatefulSet; รหัสผ่าน/คอนฟิกใน YAML → ConfigMap/Secret; ชื่อโดเมน/path → Ingress; ขยายอัตโนมัติ → HPA

## 2. รายการ LAB (`02_LAB/README.md`)

```text
02_LAB/
  README.md
  images/ (L01–L23 + imagegen-prompts.md)
  labs/
    lab01-deployment/{00-ns.yaml (deploy-lab), web.yaml}
    lab02-rolling/{web-v2.yaml, web-svc.yaml (ClusterIP), client-pod.yaml}
    lab04-strategy/{00-ns.yaml (strategy-lab), rolling.yaml, nosurge.yaml, recreate.yaml}
    lab05-readiness/{00-ns.yaml (ready-lab), web-minready.yaml, readiness-broken-patch.yaml, client-pod.yaml}
    lab06-broken/{00-ns.yaml (broken-lab), web.yaml (progressDeadlineSeconds: 30), web-svc.yaml, client-pod.yaml, crash-patch.yaml}
    lab07-zero-downtime/{00-ns.yaml (zdt-lab), web.yaml, web-nodeport.yaml (30080), graceful-patch.yaml}
    lab08-migrate/{00-ns.yaml (migrate-lab), web-rs.yaml, web-svc.yaml, client-pod.yaml, web-deploy.yaml}
    lab09-release/{00-ns.yaml (release-lab), web-blue.yaml, web-green.yaml, web-svc.yaml, web-stable.yaml, web-canary.yaml, client-pod.yaml}
  som-shop-v3/
    k8s-rs/{00-namespace.yaml, 10-db.yaml, 20-web.yaml}   (สำเนาจากบท 006 som-shop-v2/k8s — ReplicaSet + Service)
    k8s/{10-db.yaml, 20-web.yaml}                          (Deployment + Service เดิม)
    hit.sh                                                 (สำเนาจากบท 006)
```

**hit.sh** (สำเนาจากบท 006): `./hit.sh [-q] [URL=http://localhost:30080/api/whoami] [N=60] [DELAY=0.1]` → ตาราง `จำนวน คำตอบ` (sort | uniq -c) + `ok=… err=…`; `-q` นับเฉพาะ ok/err; LAB7 ใช้ URL `http://localhost:30080/` (หน้า nginx `web vX from <pod>`)

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ |
|---|---|---|---|---|---|---|
| 0 | เตรียมคลัสเตอร์ พอร์ต และ image | คลัสเตอร์พร้อม, 30080 ว่าง, image 1.2/1.3 ของบท 006 อยู่บน Node | – | `kubectl get nodes`; `kubectl get svc -A \| grep -E '3008[0-2]'` (ต้องว่าง — ถ้ามีค้างจากบท 006 ให้ `kubectl delete ns som-shop`); `kubectl get ns`; `kubectl get node lab-worker -o jsonpath='{.status.images[*].names}' \| tr ' ' '\n' \| grep som-shop-web` (ทำทั้ง lab-worker/lab-worker2) หรือ `docker exec lab-worker crictl images \| grep som-shop-web`; ถ้าไม่มี: build จาก `/workspace/006_kubernetes_service/02_LAB/som-shop-v2/app` (`--build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor` / `1.3 sunset`) + `kind load docker-image som-shop-web:1.2 som-shop-web:1.3 --name lab`; `docker cp` โฟลเดอร์บท | 3 Node Ready; ไม่มี Service ใช้ 30080–30082; เห็น `docker.io/library/som-shop-web:1.2` และ `:1.3` บนทั้งสอง worker | รูปแบบชื่อ image ใน `.status.images` (มี prefix `docker.io/library/`?); บท 006 เก็บกวาด ns `som-shop` แล้วจริง |
| 1 | Deployment แรก: deploy → rs → pod | เห็นสายเจ้าของ, hash, strategy default, scale ไม่เกิด revision, แก้ RS ตรงไม่ได้ | `lab01-deployment/00-ns.yaml`, `web.yaml` (nginx:1.27-alpine, VERSION=v1, 3 replicas, readiness; สร้างจาก `create deployment --dry-run=client -o yaml` แล้วแก้) | `kubectl create deployment web --image=nginx:1.27-alpine --replicas=3 --dry-run=client -o yaml` (ดูเฉย ๆ); `kubectl apply -f lab01-deployment/`; `kubectl -n deploy-lab rollout status deploy/web`; `get deploy,rs,pods --show-labels`; `get deploy web -o jsonpath='{.spec.strategy}'` / `{.spec.revisionHistoryLimit}` / `{.spec.progressDeadlineSeconds}`; `get rs -o jsonpath='{.items[0].metadata.ownerReferences}'`; `kubectl scale deploy web --replicas=5` แล้ว `=2` แล้ว `=3`; `rollout history deploy/web`; `kubectl scale rs <web-hash> --replicas=6` + `get rs,pods`; `delete pod <หนึ่งตัว>` | `READY 3/3 UP-TO-DATE 3 AVAILABLE 3`; ชื่อ `web-<hash>` / `web-<hash>-<สุ่ม>`; `pod-template-hash` บน RS และ Pod; strategy 25%/25%, 10, 600; RS owner = Deployment `web`; scale แล้ว RS DESIRED เปลี่ยน history ยังมี revision 1 แถวเดียว; scale RS ตรง → กลับเป็น 3; ลบ Pod → ตัวใหม่ hash เดิม | scale RS ตรงถูกปรับกลับเร็วแค่ไหน (เห็น Pod เพิ่มชั่วครู่หรือไม่); ข้อความ `pod "x" deleted from deploy-lab namespace` |
| 2 | rolling update + Service ClusterIP | ดู RS เก่า/ใหม่ระหว่าง rolling และผลต่อลูกค้าผ่าน Service | `lab02-rolling/web-v2.yaml` (nginx:1.28-alpine + VERSION=v2 — template เปลี่ยน 2 จุดใน revision เดียว), `web-svc.yaml` (ClusterIP `web` 80→80), `client-pod.yaml` (busybox loop) | `kubectl apply -f web-svc.yaml -f client-pod.yaml`; terminal 2: `kubectl -n deploy-lab get rs -w`; terminal 3: `kubectl -n deploy-lab exec client -- sh -c 'while true; do wget -qO- -T 2 http://web; sleep 0.2; done'`; `kubectl apply -f web-v2.yaml`; `rollout status`; `describe deploy web` (Events); `get rs` | RS ใหม่ 0→1→2→3, เก่า 3→2→1→0 ตามลำดับ Events (pre-check #7); client เห็น `web v1 from web-<hashเก่า>-…` และ `web v2 from web-<hashใหม่>-…` ปนกันช่วงสั้นแล้วเหลือ v2; RS เก่า `0 0 0` ยังอยู่ | เวลา rollout (pre-check 14 วิ รวม pull 1.28); client มี error ไหม (ไม่มี preStop อาจมี — โยง LAB7) |
| 3 | history / change-cause / undo / pause-resume / restart | ใช้สมุดบันทึกรุ่นให้เป็น และเห็นกับดัก | ใช้ Deployment เดิม | `rollout history deploy/web` (2 แถว `<none>`); `kubectl annotate deploy web kubernetes.io/change-cause="v2 nginx 1.28 (apply web-v2.yaml)"`; `set env deploy/web VERSION=v3` + annotate `"v3 set env"`; `set env VERSION=v4` **ไม่ annotate** → history (rev 4 สืบทอด "v3 set env"); `rollout history --revision=3`; `rollout undo --to-revision=2` (สังเกต Warning last-applied) → history; `rollout pause` → `set image deploy/web web=nginx:1.27-alpine` + `set env VERSION=v6` → `get rs` (ไม่มี RS ใหม่) → `rollout resume`; `rollout restart deploy/web` → `get deploy web -o jsonpath='{.spec.template.metadata.annotations}'`; เก็บกวาด `kubectl delete ns deploy-lab` | history มี CHANGE-CAUSE; rev 4 ข้อความซ้ำ rev 3; undo → rev 2 หายกลายเป็น rev 5 (รายการ 1, 3, 4, 5) และ client เห็น v2; pause แล้วไม่เกิด rollout จน resume ได้ revision เดียว; restart → annotation `kubectl.kubernetes.io/restartedAt` และ Pod ใหม่ทุกตัว | เลข revision จริง, CHANGE-CAUSE ของ rev 5 หลัง undo (คาดเอาข้อความของ rev 2 กลับมา), ข้อความ Warning last-applied, `rollout undo` ระหว่าง pause ได้ error อะไร |
| 4 | เทียบ maxSurge/maxUnavailable และ Recreate | เห็นผลของ strategy ต่อจำนวน Pod ระหว่างเปลี่ยนรุ่น + คำนวณ replicas 10 | `lab04-strategy/00-ns.yaml` (strategy-lab), `rolling.yaml` (4 replicas default), `nosurge.yaml` (maxSurge 0 / maxUnavailable 1), `recreate.yaml` (Recreate) — 3 Deployment label `lab=strategy` | `kubectl apply -f lab04-strategy/`; ทีละตัว terminal 2 `kubectl -n strategy-lab get pods -l app=<name> -w` + `kubectl -n strategy-lab set env deploy/<name> VERSION=v2`; บันทึกจำนวน Pod รวมสูงสุด และ Ready ต่ำสุด; แบบฝึก: คำนวณ replicas 10 → 13/8 แล้วลอง `kubectl patch deploy rolling -p '{"spec":{"replicas":10}}'` + set env ดู (เสริม); ลอง `maxSurge: 0, maxUnavailable: 0` ได้ error; เก็บกวาด ns | rolling: สูงสุด 5 Pod Ready ต่ำสุด 3; nosurge: ไม่เกิน 4 Ready ต่ำสุด 3; recreate: Pod เก่า Terminating ทั้ง 4 ก่อนแล้วตัวใหม่ค่อยเกิด (ช่วง 0 Ready); 0/0 → `may not be 0 when maxSurge is 0` | ตัวเลข max/min ที่เห็นจริงจาก watch (ใช้ `set env` ไม่ต้อง pull); ระยะเวลา gap ของ Recreate; ข้อความ error 0/0 จริง |
| 5 | readiness + minReadySeconds ตัดสิน rollout | เห็นว่า "พร้อม" คือสิ่งที่ rollout รอ | `lab05-readiness/00-ns.yaml` (ready-lab), `web-minready.yaml` (3 replicas, `minReadySeconds: 10`, readiness `/`), `readiness-broken-patch.yaml` (readiness path `/nope`), `client-pod.yaml` | apply; `set env VERSION=v2` + `kubectl -n ready-lab get deploy web -w` (READY ขึ้นก่อน AVAILABLE ~10 วิ); `kubectl patch deploy web --patch-file readiness-broken-patch.yaml` → `get pods` (Pod ใหม่ `0/1 Running`), `describe pod` (Events), `get endpointslice -l kubernetes.io/service-name=web` (เสริม), client ยิงวนยังได้ v2; `rollout undo`; เก็บกวาด ns | AVAILABLE ตามหลัง READY; Pod ใหม่ `0/1 Running` + `Readiness probe failed: HTTP probe failed with statuscode: 404`; rollout ค้าง Pod เก่า 3 ตัวยังตอบ; undo กลับ 3/3 | Event readiness 404 ของ nginx (ข้อความจริง); AVAILABLE ช้ากว่า READY เท่าไร |
| 6 | image ผิด + progressDeadlineSeconds → undo | rollout ค้าง แต่ Service ยังส่งไป Pod เก่า; Kubernetes ไม่ rollback ให้ | `lab06-broken/00-ns.yaml` (broken-lab), `web.yaml` (`progressDeadlineSeconds: 30`), `web-svc.yaml`, `client-pod.yaml`, `crash-patch.yaml` (command `exit 1` — เสริม) | apply; `kubectl -n broken-lab set image deploy/web web=nginx:9.99-nope`; `get pods,rs`; `rollout status deploy/web` (รอ ~30 วิ, `echo $?`); `get deploy web`; `describe deploy web` (Conditions); client ยิงวนยังได้ทุกครั้ง; `rollout undo`; เสริม: `kubectl patch deploy web --patch-file crash-patch.yaml` → `CrashLoopBackOff` → undo; เก็บกวาด ns | `ErrImagePull`→`ImagePullBackOff`, RS ใหม่ `1 1 0`, `error: deployment "web" exceeded its progress deadline` (exit 1), `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`, `ProgressDeadlineExceeded`; client ok ตลอด; undo กลับปกติ | ยืนยันแล้วใน pre-check #10; ยืนยันส่วนเสริม CrashLoopBackOff และ exit code |
| 7 | zero-downtime ผ่าน NodePort | นับ error ระหว่าง rollout เทียบไม่มี/มี preStop + maxUnavailable 0 | `lab07-zero-downtime/00-ns.yaml` (zdt-lab), `web.yaml` (3 replicas default strategy ไม่มี preStop), `web-nodeport.yaml` (NodePort 30080), `graceful-patch.yaml` (`preStop.sleep.seconds: 5`, `terminationGracePeriodSeconds: 30`, maxSurge 1 / maxUnavailable 0), `../../som-shop-v3/hit.sh` | apply; `curl -s localhost:30080`; terminal 1: `./hit.sh -q http://localhost:30080/ 300`; terminal 2: `kubectl -n zdt-lab set env deploy/web VERSION=v2`; รอบ 2: `kubectl patch deploy web --patch-file graceful-patch.yaml` (รอ rollout จบ) แล้วยิงใหม่ + `set env VERSION=v3`; ทำ 2 รอบ; เก็บกวาด `kubectl delete ns zdt-lab` (คืน 30080) | รอบแรก err 0–3/300 (สุ่ม); รอบหลัง 0/300; ระหว่างทางเห็น v1/v2 ปนช่วงสั้น | จำนวน error จริง (อาจเป็น 0 ทั้งสองรอบ — README เขียนว่า "อาจ"); hit.sh กับหน้า nginx (ไม่ใช่ /api/whoami) นับถูก |
| 8 | ย้าย ReplicaSet → Deployment | Deployment รับเลี้ยง RS ที่ไม่มีเจ้าของ และ RS เดิมถูก scale ลงระหว่าง rolling | `lab08-migrate/00-ns.yaml` (migrate-lab), `web-rs.yaml` (ReplicaSet `web` 3 replicas `app=web`, VERSION=v1 — แบบบท 006), `web-svc.yaml`, `client-pod.yaml`, `web-deploy.yaml` (Deployment `web` selector `app=web`, VERSION=v2) | apply rs+svc+client; client ยิงวน; `kubectl apply -f web-deploy.yaml`; terminal 2 `get rs -w`; `get rs web -o jsonpath='{.metadata.ownerReferences}'`; `get pods --show-labels`; `rollout history deploy/web`; ทางสำรอง (ทำซ้ำใน ns ใหม่หรือหลังลบ): `kubectl delete rs web --cascade=orphan` → apply deploy → `delete pod -l 'app=web,!pod-template-hash'`; เก็บกวาด ns | RS `web` มี owner = Deployment `web`; RS `web` 3→0 และ RS `web-<hash>` 0→3; client เห็น v1→v2 ไม่ขาด; Pod ใหม่มี `pod-template-hash` Pod เก่าไม่มี | **ยังไม่มี pre-check**: รับเลี้ยงจริงไหม, RS เดิมได้ annotation `deployment.kubernetes.io/revision` อะไร/ปรากฏใน history ไหม, กรณี template เหมือนกันทุกตัวอักษร; ถ้าไม่รับเลี้ยงให้ใช้ทางสำรองเป็นหลัก |
| 9 | blue/green และ canary (เล็ก) | สลับรุ่นด้วย selector ของ Service และแบ่งลูกค้าตามจำนวน Pod | `lab09-release/00-ns.yaml` (release-lab), `web-blue.yaml` / `web-green.yaml` (2 replicas, label `version`), `web-svc.yaml` (selector `app=web,version=blue`), `web-stable.yaml` (4 replicas `track=stable`) / `web-canary.yaml` (1 replica `track=canary`), `client-pod.yaml` | blue/green: apply → client ยิง 20 ครั้ง (blue ล้วน) → `kubectl patch svc web -p '{"spec":{"selector":{"version":"green"}}}'` → green ล้วน → สลับกลับ; canary: ลบ blue/green, `kubectl patch svc web --type=json -p '[{"op":"remove","path":"/spec/selector/version"}]'`, apply stable+canary → client ยิง 50 ครั้ง `\| sort \| uniq -c`; เก็บกวาด ns | สลับทันทีทั้งหมด; canary ราว 1 ใน 5 (สุ่ม ไม่เท่ากันเป๊ะ) | สัดส่วนจริง; patch แบบ json remove ใช้ได้ (หรือ apply `web-svc-all.yaml`) |
| 10 | LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริง | แปลงร้านบท 006 เป็น Deployment แล้วเปลี่ยนรุ่น/ย้อน/รุ่นพัง/scale/restart โดยร้านไม่สะดุด | `som-shop-v3/` | ดูหัวข้อ 3 | ดูหัวข้อ 3 | ดูหัวข้อ 3.6 |

## 3. LAB สุดท้าย — "ร้านน้องส้มแบบโปรดักชันจริง" (LAB10, `som-shop-v3/`)

### 3.1 แนวคิด

- เริ่มจาก **สภาพเดียวกับท้ายบท 006** (`k8s-rs/` = ReplicaSet som-db/som-web + Service som-db ClusterIP + som-web NodePort 30080) เพื่อให้นักศึกษารู้สึกถึง "ร้านที่มีอยู่แล้ว" และฝึกย้ายโดยไม่เปลี่ยนชื่อ Service (ลูกค้าและ web ยังเรียก `som-db`, `localhost:30080` เหมือนเดิม)
- แปลงเป็น Deployment ชื่อเดิม selector เดิม: `som-db` **Recreate** (ห้ามมี postgres 2 ตัว — หัวข้อทฤษฎี 4.4) และ `som-web` RollingUpdate แบบ zero-downtime (`maxSurge 1, maxUnavailable 0`, `preStop.sleep.seconds: 5`, `terminationGracePeriodSeconds: 30`, `minReadySeconds: 3`, `progressDeadlineSeconds: 60`, `revisionHistoryLimit: 5`)
- ใช้ `hit.sh` นับ ok/err ทุกครั้งที่เปลี่ยนรุ่น → พิสูจน์ด้วยตัวเลข; ใช้ browser ดูธีม 1.2/1.3
- 1.4 ไม่มีจริง → สอนว่า rollout พังแล้ว "ร้านยังขาย" เพราะ maxUnavailable 0 + Kubernetes ไม่ rollback ให้ ต้อง undo เอง
- จบด้วยปัญหาเดิมที่ยังไม่หาย: db ลืมทุกอย่าง (emptyDir) → บทหน้า PVC/StatefulSet; `rollout restart` ใช้เติมสินค้าใหม่แทนการลบ Pod เองแบบบท 006

### 3.2 สถาปัตยกรรม

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-<hash>-a  Pod som-web-<hash>-b  Pod som-web-<hash>-c   (Deployment som-web, replicas 3→5,
   │                                                                RollingUpdate maxSurge 1 / maxUnavailable 0,
   └──── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop    preStop sleep 5, minReadySeconds 3)
                                   ▼
                    Service som-db (ClusterIP, 5432)
                                   ▼
                    Pod som-db-<hash>-x (Deployment som-db, replicas 1, Recreate, emptyDir)
```

### 3.3 ไฟล์ manifest

- `k8s-rs/00-namespace.yaml`, `k8s-rs/10-db.yaml`, `k8s-rs/20-web.yaml`: **สำเนาตรง** จากบท 006 `som-shop-v2/k8s/` (ReplicaSet `som-db` 1 + Service ClusterIP `som-db`; ReplicaSet `som-web` 3 `som-shop-web:1.2` + Service NodePort `som-web` 30080) — namespace `som-shop` (PSA warn restricted)
- `k8s/10-db.yaml`: Deployment `som-db` `replicas: 1`, `strategy: {type: Recreate}`, selector/labels `app: som-db` (เท่าบท 006), Pod spec เหมือนบท 006 ทุกอย่าง (postgres:17.11-alpine, emptyDir, readiness `pg_isready`, securityContext restricted) + คอมเมนต์ "emptyDir = ข้อมูลหายเมื่อ Pod ถูกสร้างใหม่ (บทหน้าใช้ PVC)"; Service `som-db` เหมือนเดิมทุกตัวอักษร
- `k8s/20-web.yaml`: Deployment `som-web` `replicas: 3`, `revisionHistoryLimit: 5`, `progressDeadlineSeconds: 60`, `minReadySeconds: 3`, `strategy.rollingUpdate: {maxSurge: 1, maxUnavailable: 0}`; Pod spec จากบท 006 (initContainers `wait-for-db` + `db-seed` `som-shop-web:1.2`, container `web` `som-shop-web:1.2`, readiness `/api/health`, liveness `/api/live`, env `DATABASE_URL`, `POD_NAMESPACE`, `SHOP_FOOTER` = `... Kubernetes LAB 007 ...`) + **ใหม่** `lifecycle.preStop.sleep.seconds: 5`, `terminationGracePeriodSeconds: 30`; `metadata.annotations.kubernetes.io/change-cause: "1.2 แปลงเป็น Deployment"`; Service `som-web` เหมือนเดิม
- `hit.sh`: สำเนาจากบท 006

### 3.4 ขั้นตอน

1. **เตรียม**: LAB0 ผ่านแล้ว (30080 ว่าง, 1.2/1.3 บน Node); `cd som-shop-v3`
2. **สร้างสภาพบท 006**: `kubectl apply -f k8s-rs/` → `kubectl -n som-shop get rs,pods,svc` → เปิด `http://localhost:30080` (1.2 ธีม harbor) → สั่งซื้อ 2 ออเดอร์ (หน้าเว็บหรือ `curl -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":2}'`) → `./hit.sh` เห็น 3 Pod; ทวน: "ถ้าจะเปลี่ยนเป็น 1.3 ตอนนี้ต้องลบ Pod เอง"
3. **แปลง db** (เตือนก่อน: Recreate = Pod db ใหม่ ข้อมูล emptyDir หาย): `kubectl apply -f k8s/10-db.yaml` → `kubectl -n som-shop rollout status deploy/som-db` → `get rs -n som-shop -l app=som-db` + `get rs som-db -o jsonpath='{.metadata.ownerReferences}'` (รับเลี้ยง?) → หน้าเว็บ 503 "ร้านกำลังเตรียมสินค้า" (web เดิมต่อ db ใหม่ที่ยังไม่มีตาราง)
4. **แปลง web** ระหว่างยิง: terminal 1 `./hit.sh -q http://localhost:30080/api/whoami 300`; terminal 2 `kubectl apply -f k8s/20-web.yaml` + `kubectl -n som-shop get rs -w` → RS `som-web` (เดิม) 3→0, `som-web-<hash>` 0→3; initContainer ของ Pod ใหม่เติมสินค้าเข้าฐานข้อมูลใหม่ → หน้าเว็บกลับมา (ออเดอร์ 0 — ผลจากขั้น 3); hit.sh err=0 (whoami ไม่แตะ db)
   - ถ้าไม่รับเลี้ยง/RS เดิมไม่ลด: ทางสำรอง `kubectl -n som-shop delete rs som-web som-db --cascade=orphan` ก่อน apply แล้วลบ Pod เก่าหลัง Deployment พร้อม (`kubectl -n som-shop delete pod -l 'app=som-web,!pod-template-hash'`)
5. สั่งซื้อใหม่ 2 ออเดอร์ (ใช้พิสูจน์ในขั้น 7–9)
6. **rolling 1.2 → 1.3**: terminal 1 `./hit.sh -q http://localhost:30080/api/whoami 300`; terminal 2 `kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3` + `kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.3 ธีม sunset" --overwrite` + `rollout status` → **err=0** (pre-check #22); ระหว่างทาง `./hit.sh` (ไม่ -q) เห็น 1.2/1.3 ปน; browser Ctrl+F5 เห็นธีม sunset + "เวอร์ชัน 1.3" + แบนเนอร์เมนูใหม่; `get pods` เห็น Pod เก่าขึ้น `Error` ชั่วครู่ (pre-check #22 — อธิบายว่าไม่ใช่ rollout พัง)
7. **history / undo**: `rollout history deploy/som-web` → `rollout undo` (กลับ 1.2, ออเดอร์ยังอยู่ — db ไม่ถูกแตะ, schema เข้ากันได้ทั้งสองรุ่น) → `rollout undo` อีกครั้ง (กลับ 1.3 — undo ไม่ระบุ revision = กลับไป revision ก่อนหน้า) → history อีกครั้ง (เลข revision เลื่อน)
8. **รุ่นพัง 1.4**: `kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.4` (เฉพาะ container web — db-seed ยัง 1.3 จึงเห็น `ErrImagePull` ที่ตัว web ไม่ใช่ `Init:ErrImagePull`) + annotate `"1.4 (ทดสอบรุ่นพัง)"` → Pod ใหม่ 1 ตัว `ErrImagePull`/`ImagePullBackOff`, Pod เก่า 3 ตัวไม่ถูกปิด (maxUnavailable 0) → `rollout status` รอ ~60 วิ → `error: deployment "som-web" exceeded its progress deadline`; `get deploy som-web` → `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`; ระหว่างนั้น `./hit.sh -q` ok ทั้งหมด + สั่งซื้อได้ → `rollout undo` → Pod พังหาย
9. **scale 3→5**: `kubectl -n som-shop scale deploy/som-web --replicas=5` → `get pods`, `get endpointslice -l kubernetes.io/service-name=som-web` (5 IP), `rollout history` (ไม่มี revision ใหม่), `./hit.sh` เห็น 5 Pod
10. **ลบ db + rollout restart**: `kubectl -n som-shop delete pod -l app=som-db` → Pod ใหม่ (Deployment/RS สร้าง) → หน้าเว็บ 503 → `kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c 'select count(*) from orders'` → `relation "orders" does not exist` → `./hit.sh -q ... 300` ระหว่าง `kubectl -n som-shop rollout restart deploy/som-web` (initContainer รันใหม่ เติมสินค้า; ต่างจากบท 006 ที่ต้องลบ Pod เอง) → ร้านกลับมา **ออเดอร์ = 0** → อภิปราย: Deployment จัดการรุ่นได้ แต่ข้อมูลต้องอยู่ที่ volume ที่ไม่หายตาม Pod → PVC/StatefulSet บทหน้า
11. **เก็บกวาด**: `kubectl delete ns som-shop` (30080 ว่างอีกครั้ง)

### 3.5 ผลที่ต้องเห็น

- หลังแปลง: `get deploy -n som-shop` → `som-db 1/1`, `som-web 3/3`; `get rs` → `som-web` (เดิม) `0 0 0` + `som-web-<hash>` `3 3 3`; ownerReferences ของ RS เดิมชี้ Deployment
- rolling 1.2→1.3: `ok=300 err=0`; history มี CHANGE-CAUSE `1.2 แปลงเป็น Deployment` / `1.3 ธีม sunset`
- undo สองครั้ง: หน้า 1.2 แล้วกลับ 1.3; ออเดอร์เท่าเดิม
- 1.4: `ImagePullBackOff`, `exceeded its progress deadline`, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`, hit.sh err=0; undo กลับปกติ
- scale 5: EndpointSlice 5 IP; ไม่มี revision ใหม่
- ลบ db: 503 → rollout restart → ร้านกลับมา ออเดอร์ 0

### 3.6 จุดที่ต้องยืนยันตอนทดสอบจริง

1. **การรับเลี้ยง RS เดิม** (`som-web`, `som-db`) ด้วย Deployment ชื่อเดียวกัน: ownerReferences ถูกเติมไหม, RS เดิมถูก scale 3→0 แบบ rolling ไหม, RS เดิมได้ revision อะไรและโผล่ใน `rollout history` ไหม, RS เดิมถูกลบเมื่อเกิน `revisionHistoryLimit` ไหม; ถ้าผลต่างจากคาด ให้ทางสำรอง `--cascade=orphan` เป็นขั้นหลัก
2. Recreate ของ som-db ตอนแปลง: Pod db เดิมถูกปิดก่อน → ช่วงที่ web เดิมต่อ db ไม่ได้ → readiness `/api/health` ของ web เดิมล้ม → endpoints ว่างชั่วครู่ (ร้านล่มสั้น ๆ ระหว่างแปลง db — บันทึกเวลาจริง และ hit.sh ช่วงนั้น)
3. **เวลา rollout** 1.2→1.3 ของ 3 replicas (มี initContainer 2 ตัว + minReadySeconds 3 + maxSurge 1 → คาด ~30–45 วิ) และ rollout restart ของ 5 replicas
4. **err=0** ระหว่างแปลง web, rolling 1.3, undo, 1.4 และ rollout restart (pre-check #22 0/300 สองรอบ — บันทึกตัวเลขจริง ถ้ามี error ให้ลอง preStop 10 วิ)
5. **ข้อความจริงของ 1.4**: Events (`Failed to pull image "som-shop-web:1.4": ... pull access denied ...`?), `error: deployment "som-web" exceeded its progress deadline`, condition `ReplicaSet "som-web-<hash>" has timed out progressing.`; สถานะ `ErrImagePull` vs `ImagePullBackOff` ณ เวลาที่ดู
6. **หน้าร้าน 1.3** จริง (ธีม sunset, ป้าย "เวอร์ชัน 1.3", แบนเนอร์ "เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟", ชื่อ Pod) ตามที่บท 006 build
7. **change-cause**: annotation ใน YAML ของ `20-web.yaml` + `annotate --overwrite` แสดงถูก revision ไหม; หลัง undo ข้อความเป็นของ revision ไหน; ลำดับเลข revision หลัง undo สองครั้ง
8. `set image ... db-seed=...` ใช้กับ initContainer ได้ (คาดได้); 1.4 เปลี่ยนแค่ web
9. resource 5 web + 1 surge + 1 db ไม่ Pending; Pod Next.js ที่ถูกปิดขึ้น `Error` ชั่วครู่
10. `rollout restart` หลังลบ db: init `db-seed` สร้างตารางใหม่ได้ (pre-check #25) และหน้าเว็บกลับมาจาก 503

### 3.7 screenshot ที่จะเก็บตอนทดสอบจริง (ไม่ใช่ภาพ imagegen)

- browser `localhost:30080`: 1.2 (ก่อนแปลง), 503 หลังแปลง db, 1.3 ธีม sunset, ระหว่าง 1.4 ร้านยังขาย, หลังลบ db (ออเดอร์ 0)
- terminal: `get deploy,rs,pods -n som-shop` หลังแปลง (RS เดิม 0 + ownerReferences), `hit.sh -q` ระหว่าง rolling (`err=0`), `rollout history`, 1.4 `ImagePullBackOff` + `exceeded its progress deadline`, `get endpointslice` 5 IP

## 4. งานถัดไป (หลังอนุมัติแผน)

1. สร้างภาพจาก `images.json` (ผู้ประสานงานจัดการ `gen_images.sh`) → ตรวจภาพ (ป้ายสะกด/จำนวน, น้องส้มตรง reference, หุ่นยนต์ไม่เป็นแมว, ไม่มีนก/เด็กกำพร้า/อาหาร hash) → ภาพ `needs_test` สร้างหรือปรับหลังทดสอบ LAB จริง
2. เขียนไฟล์ LAB (`labs/`, `som-shop-v3/` — `k8s-rs/` สำเนาจากบท 006 หลังบท 006 เขียนเสร็จ) + README ทฤษฎี/LAB
3. รัน LAB0–10 ใน container ชั่วคราว (skill k8s-lab) → `logs/007_deployment/lab-run/SUMMARY.md` แล้วแก้ README/ภาพด้วยผลจริง (โดยเฉพาะ LAB8 การรับเลี้ยง)

## 5. สรุป storyboard

- **Theory 36 ภาพ (T01–T36)**: บทนำ T01–T03 (T01 ป้าย "บทที่ 7"), Deployment→RS→Pod T04–T09, trigger T10, RollingUpdate/Recreate T11–T14, readiness T15–T16, zero-downtime T17–T18, progress deadline T19–T20, rollout/history/undo T21–T26, วิธีเปลี่ยน T27–T28, ย้าย RS T29–T30, อาการพัง T31, blue/green + canary T32–T33, สรุป T34–T36 (T36 ปูทางบทถัดไป `allow=True`)
- **LAB 23 ภาพ (L01–L23)**: LAB0 L01, LAB1 L02–L03, LAB2 L04–L05, LAB3 L06–L07, LAB4 L08, LAB5 L09, LAB6 L10, LAB7 L11, LAB8 L12, LAB9 L13, LAB10 L14–L23 (10 ภาพ: สถาปัตยกรรม, สภาพบท 006, แปลงเป็น Deployment, rolling 1.3, หน้าร้าน 1.3, history/undo, 1.4 พังแต่ขาย, scale 5, ลบ db + restart (`allow=True` ป้าย PVC), สรุป)
- **needs_test (12)**: T29 (รับเลี้ยง RS), L06 (เลข revision 1/3/4/5 + change-cause), L08 (max/min Pod LAB4), L09 (Event `statuscode: 404`), L11 (`3/300` vs `0/300` ของ nginx ในคลัสเตอร์นักศึกษา), L12 (รับเลี้ยง RS ใน LAB8), L16 (แปลงร้าน + err=0), L17 (rolling 1.3 err=0), L18 (หน้าร้าน 1.3), L19 (undo + ออเดอร์ 2), L20 (1.4 ImagePullBackOff/ProgressDeadlineExceeded + err=0), L22 (ลบ db `orders: 2 → 0`, 503)
- ภาพที่ใช้ค่าจาก pre-check (ไม่ติด needs_test แต่ตรวจป้ายอีกครั้งหลังรัน): T09 (`6f58b8bd67`/`7c987cc6b4`), T11 (Events 7 แถว), T12 (3/4/10), T18 (`0/300`), T19/T20/L10 (`ImagePullBackOff`, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`), T21–T23 (change-cause สืบทอด, revision 1/3/4), T24 (Warning last-applied)
- กฎภาพ: ป้ายตามจำนวนตรงตัว (ป้ายซ้ำระบุว่าซ้ำ), ของในภาพเป็นร้านอาหารแมว/ท่าเรือ, ไม่วาดคำตามตัวอักษร (canary ≠ นก, hash ≠ อาหาร, orphan ≠ เด็ก/สัตว์กำพร้า → บูธที่ไม่มีป้ายเจ้าของ, adopt → ติดป้ายเจ้าของ, seed → เติมสินค้าเข้าชั้น), หุ่นยนต์ไม่เป็นแมว, ห้าม Ingress/StatefulSet/PV/HPA/ConfigMap ยกเว้น T36 และ L22
