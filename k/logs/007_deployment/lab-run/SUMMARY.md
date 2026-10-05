# SUMMARY — ทดสอบ LAB บท 007 Deployment (รันจริง 5 ต.ค. 2569)

- container ทดลอง `k8s-lab-deploy007lab-06e5cc` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`, NodePort `30090-30092→30080-30082`) — **ยังเปิดอยู่** ตามคำสั่ง (ดู `handoff.md`) ไม่ได้แตะ `k8s-lab` ของผู้เรียน / `deep_vision_5090_vllm`
- `k8s-up` 53.7 วิ; kubectl v1.37.1 / server v1.37.0; `docker cp 007_kubernetes_deployment` → `/workspace/` (**ไม่ได้ copy บท 006** — ยืนยันว่าบทนี้ใช้งานได้ด้วยตัวเอง) แล้วรันทุกคำสั่งจาก `02_LAB` (LAB 1–9 `cd labs`, LAB 10 `cd som-shop-v3`); ไฟล์ใน container = repo (md5 64 ไฟล์)
- log คำสั่ง+output จริง: `lab00.log` … `lab09.log`, `lab10.log` (รอบหลัก), `lab10-final.log` (รอบคืนสภาพ = รอบที่ 2 ของขั้นแปลง); บรรทัด `### hh:mm:ss` = UTC ของเครื่อง agent, `date` ในคำสั่ง = เวลาไทย
- ทดสอบจาก "เครื่องนักศึกษา" ด้วย host ของ agent: `http://172.18.0.1:30090` (gateway → container 30080 → kind extraPortMappings → lab-control-plane:30080) — ได้หน้าร้าน HTTP 200, `/api/*`, hit.sh จาก host `ok=200 err=0`
- นับ error ด้วย `som-shop-v3/hit.sh -q` (curl ใหม่ทุกครั้ง `-f -m 2`, DELAY 0.1 → 300 ครั้ง ≈ 32.5 วิ) ยิงพร้อมกัน 2 ชุด: `/api/whoami` (ไม่แตะ db) และ `/` (หน้าร้าน ต้องใช้ db, DELAY 0.2)

## ไฟล์ที่สร้าง (`007_kubernetes_deployment/02_LAB/`)

- `labs/` 36 ไฟล์: `lab01-deployment/{00-ns,web}.yaml`, `lab02-rolling/{web-v2,web-svc,client-pod}.yaml`, `lab04-strategy/{00-ns,rolling,nosurge,recreate}.yaml` + `exercise/zero-zero.yaml`, `lab05-readiness/{00-ns,web-minready(+Service),client-pod}.yaml` + `patches/readiness-broken-patch.yaml`, `lab06-broken/{00-ns,web,web-svc,client-pod}.yaml` + `patches/crash-patch.yaml`, `lab07-zero-downtime/{00-ns,web,web-nodeport}.yaml` + `patches/graceful-patch.yaml`, `lab08-migrate/{00-ns,web-rs,web-svc,client-pod,web-deploy}.yaml`, `lab09-release/{00-ns,web-blue,web-green,web-svc,web-svc-all,web-stable,web-canary,client-pod}.yaml`
- `som-shop-v3/`: `k8s-rs/{00-namespace,10-db,20-web}.yaml` (สำเนาบท 006 แก้แค่คอมเมนต์บรรทัดแรก), `k8s/{10-db,20-web}.yaml` (Deployment), `hit.sh` (สำเนาบท 006 ไม่แก้), `app/` (สำเนา `006.../som-shop-v2/app` ไม่รวม node_modules/.next — **โค้ดไม่แก้เลย** จึง build ได้ image เดียวกับบท 006)
- ยังไม่มี `02_LAB/README.md` (นอกขอบเขตงานนี้)

## ผลรายข้อ

| LAB | ผล | เวลาจริง | ผลจริงสำคัญ |
|---|---|---|---|
| 0 | ✅ | build 1.2 29.0 วิ / 1.3 0.9 วิ, kind load 6.0 วิ, postgres pull+save+load 16.3 วิ | 3 Node Ready; ไม่มี Service 30080–30082; คลัสเตอร์ใหม่ไม่มี image → build จาก `som-shop-v3/app`; ชื่อใน `.status.images` = **`docker.io/library/som-shop-web:1.2`** (มี prefix) แต่ **อัปเดตช้า ~30–60 วิหลัง kind load** (ครั้งแรกว่าง) ส่วน `docker exec lab-worker crictl images \| grep som-shop-web` เห็นทันที; jsonpath `{.status.images[*].names}` พิมพ์เป็น JSON array ต่อ image (`["docker.io/library/import-2026-10-05@sha256:…","docker.io/library/som-shop-web:1.2"]`) |
| 1 | ✅ | rollout 9.3 วิ | `READY 3/3 UP-TO-DATE 3 AVAILABLE 3`; RS `web-779cb4fbb8`, Pod `web-779cb4fbb8-4jwkw`; strategy `{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"}` / 10 / 600 / minReadySeconds ว่าง; owner RS→`Deployment web`, Pod→`ReplicaSet web-779cb4fbb8`; annotation RS `desired-replicas 3, max-replicas 4, revision 1`; scale 5/2/3 → history `1 <none>` แถวเดียว; **scale RS ตรงเป็น 6 → Pod ใหม่ 3 ตัวเกิด (`Pending`→`ContainerCreating`) แล้วถูกลบภายใน ~1 วิ** (สถานะ `ContainerStatusUnknown` ชั่วครู่) Event `Scaled down replica set web-779cb4fbb8 from 6 to 3`; ลบ Pod → `pod "web-779cb4fbb8-6xw2m" deleted from deploy-lab namespace` ตัวใหม่ hash เดิม |
| 2 | ✅ | rollout 17.5 วิ (รวม pull 1.28 ~7 วิ) | RS ใหม่ `web-7c974c65c6` 0→1→2→3 เก่า 3→2→1→0 (ตรง pre-check #7); Events 6 ขั้นแต่ขั้น up 2→3 ถูกรวมเป็น **`(combined from similar events): Scaled down replica set web-779cb4fbb8 from 1 to 0`** (x2) — describe อาจไม่เห็นครบ 6 บรรทัด; client 168 ครั้ง `81 v1 / 87 v2` **ERR 0** (ไม่มี preStop ก็ไม่ error ผ่าน ClusterIP รอบนี้); RS เก่า `0 0 0` |
| 3 | ✅ | – | history `1 <none> / 2 <none>` → annotate → `2 v2 nginx 1.28 (apply web-v2.yaml)`; set env v3+annotate, v4 ไม่ annotate → **`3 v3 set env` / `4 v3 set env`** (สืบทอด); `--revision=3` แสดง template + `Annotations: kubernetes.io/change-cause: v3 set env`; undo `--to-revision=2` → Warning last-applied (ข้อความเต็มตรง pre-check #9) → **history `1, 3, 4, 5` และ rev 5 = `v2 nginx 1.28 (apply web-v2.yaml)`** (ข้อความของ rev 2 กลับมา) ใช้ RS `7c974c65c6` เดิม; pause → set image+set env → ไม่มี RS ใหม่ `READY 3/3 UP-TO-DATE 0 AVAILABLE 3`; **undo ระหว่าง pause → `error: you cannot rollback a paused deployment; resume it first with 'kubectl rollout resume' and try again`** (exit 1, Warning พิมพ์ก่อน); `rollout status --timeout=5s` ระหว่าง pause → `error: timed out waiting for the condition`; resume → revision เดียว (6); restart → `{"kubectl.kubernetes.io/restartedAt":"2026-10-05T10:09:39+07:00"}` Pod ใหม่ทุกตัว, rev 7 สืบทอด change-cause ของ rev 6; Pod nginx เก่าขึ้น `0/1 Completed`; ลบ ns 11.1 วิ |
| 4 | ✅ (แก้ไฟล์ 1 จุด) | rollout 3–7 วิ | **rolling: active สูงสุด 5 Ready ต่ำสุด 3; nosurge: สูงสุด 4 ต่ำสุด 3; recreate: ต่ำสุด 0** (ช่วง 0 Ready ~2 วิ: 10:13:00.9 → 10:13:02.9); replicas 10 → **สูงสุด 13 Ready ต่ำสุด 8** และ annotation RS `deployment.kubernetes.io/max-replicas: 13`; 0/0 → `The Deployment "zero" is invalid: spec.strategy.rollingUpdate.maxUnavailable: Invalid value: 0: may not be 0 when \`maxSurge\` is 0`; **กับดักการนับ:** Pod nginx ที่กำลังปิดแสดง `0/1 Completed` (ไม่ใช่ Terminating ตลอด) — ถ้านับทุกบรรทัดจาก `get pods -w` จะได้เกินจริง (rolling 7–8, recreate 8); Recreate สร้าง Pod ใหม่ทันทีที่ Pod เก่าเป็น `Completed` แม้ยังเห็นในรายการ |
| 5 | ✅ (แก้ไฟล์) | rollout 32.8 วิ (3 × ~11 วิ) | `get deploy -w`: **AVAILABLE ตาม READY ช้า 10–11 วิพอดี** (เช่น 10:14:34 `4/3 1 3` → 10:14:44 `4/3 1 4`); Pod readiness พัง `0/1 Running`, RS ใหม่ `1 1 0`, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`; Events: ครั้งแรก `Readiness probe failed: Get "http://10.244.2.51:80/nope": dial tcp 10.244.2.51:80: connect: connection refused` แล้ว **`Readiness probe failed: HTTP probe failed with statuscode: 404`** (x6); EndpointSlice ENDPOINTS `… + 1 more...` jsonpath เห็นตัวใหม่ `ready=false`; client 149 ครั้ง v2 ล้วน ERR 0; undo กลับ 3/3 |
| 6 | ✅ | deadline ~31 วิหลัง set image | Pod `ErrImagePull` (4 วิ) → สลับ `ImagePullBackOff`/`ErrImagePull`; RS ใหม่ `1 1 0` เก่า `3 3 3`; `error: deployment "web" exceeded its progress deadline` exit 1; `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`; `Progressing=False ProgressDeadlineExceeded: ReplicaSet "web-b6c6fccd4" has timed out progressing.`; Event `Failed to pull image "nginx:9.99-nope": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:9.99-nope": failed to resolve reference "docker.io/library/nginx:9.99-nope": docker.io/library/nginx:9.99-nope: not found`; client 297/297 v1; history หลัง undo `2 <none> / 3 <none>`; เสริม crash → `CrashLoopBackOff` RESTARTS 2 ใน 25 วิ, `logs`/`--previous` = `แอปรุ่นนี้พัง: ไม่เจอไฟล์ตั้งค่า`, lastState `exitCode 1 reason Error`, `rollout status` ก็ exceeded deadline (exit 1) → undo |
| 7 | ✅ (แก้ไฟล์) | rollout 3.2–5.7 วิ | **ไม่มี preStop: err 4, 4, 1 /300** (ข้อความ `Connection reset by peer` 1–3, `Operation timed out` 0–1, `Empty reply from server` 0–1, ช่วง err 0–3.4 วิ); **graceful-patch (preStop 5 + maxSurge 1/maxUnavailable 0): err 0, 0, 0 /300**; จาก host `hit.sh http://172.18.0.1:30090/ 200` ระหว่างเปลี่ยนรุ่น `ok=200 err=0` เห็น v7/v8 ปน 6 Pod; hit.sh กับหน้า nginx นับถูก (หัวตาราง `จำนวน  Pod  เวอร์ชัน` ยังใช้ได้); ลบ ns 27 วิ แล้ว 30080 ว่าง |
| 8 | ✅ | rollout 3.8 วิ | **Deployment รับเลี้ยง RS ที่ไม่มีเจ้าของจริง**: RS `web` ได้ ownerReferences `Deployment web` + annotation `desired-replicas/max-replicas` (**ไม่มี** `deployment.kubernetes.io/revision`), ไม่ได้ label `pod-template-hash`; RS `web` 3→2→1→0 สลับกับ `web-7b6cd79469` 0→1→2→3 (Events แบบ rolling ปกติ); client 173 ครั้ง (30 v1 / 143 v2) **ERR 0**; **history แสดง `0 <none>` (RS เดิม) และ `1 <none>`**; `describe` → `OldReplicaSets: web (0/0 replicas created)`; `rollout undo` → กลับไป RS `web` เดิม (Pod ไม่มี hash) กลายเป็น revision 2; **template เหมือนกันทุกตัวอักษร (v1) → รับเลี้ยงเป็นรุ่นปัจจุบัน ไม่เกิด rolling Pod เดิมอยู่ต่อ history `1 <none>`**; ทางสำรอง `--cascade=orphan` → `replicaset.apps "web" deleted from migrate-lab namespace` Pod 3 ตัวอยู่ต่อ → apply → Pod ใหม่ 3 ตัว (Deployment ไม่รับ Pod หลง) → `delete pod -l "app=web,!pod-template-hash"` → client **ERR 1** (`wget: can't connect to remote host (10.96.60.208): Connection refused`) |
| 9 | ✅ | – | blue 20/20 → patch green → **ทันทีหลัง patch ยังได้ blue 20/20 (คำขอทั้ง 20 จบใน <1 วิ)**; วัดจริงสลับภายใน <1 วิ (patch 10:27:13.120 เวลาไทย = 03:27:13 UTC ของ busybox → คำขอในวินาทีเดียวกันเริ่มเป็น green); รอ 2 วิแล้ว green 20/20; canary: json remove → selector `{"app":"web"}`; 50 ครั้ง × 7 รอบ canary **5, 6, 7, 9, 12, 11, 3** (ค่าเฉลี่ย ~15%) และ **500 ครั้ง → canary 101 (20.2%)** stable 4 ตัว 81–108; `web-svc-all.yaml` ใช้แทน patch ได้; Pod ของ Deployment ที่ถูกลบ (`web-green`) ยังเห็น `0/1 Completed` ใน `get pods` ชั่วครู่ |
| 10 | ✅ (ผลต่างจากแผน 3 จุด) | ดูด้านล่าง | ดูหัวข้อถัดไป |

## LAB 10 — ผลตาม "จุดที่ต้องยืนยัน" (แผน 3.6)

1. **การรับเลี้ยง RS เดิม**
   - `som-db`: template ของ `k8s/10-db.yaml` **เหมือน RS เดิมทุกตัวอักษร** (strategy อยู่นอก template) → Deployment รับเลี้ยง RS `som-db` (ไม่มี hash) เป็น revision 1 ทันที — `rollout status` จบใน 0.04 วิ, **Pod `som-db-sdznc` ไม่ถูกสร้างใหม่ ข้อมูลไม่หาย** (orders=2 เท่าเดิม), hit.sh `/api/whoami` 400/400 และ `/` 200/200 err 0, `rollout history deploy/som-db` → `1 <none>` (ยืนยันซ้ำในรอบคืนสภาพ)
   - `som-web`: template ต่าง (footer LAB 007 + preStop) → RS `som-web` ได้ ownerReferences `Deployment som-web` (ไม่มี annotation revision) แล้วถูก scale 3→2→1→0 สลับกับ `som-web-7955fccc94` 0→1→2→3 แบบ rolling (`maxSurge 1 / maxUnavailable 0` + `minReadySeconds 3` ห่างขั้นละ ~6 วิ); history **`0 <none>` / `1 1.2 แปลงเป็น Deployment`**; RS เดิมยังอยู่ `0 0 0` ตลอด LAB (history รวม ≤ 5 รุ่น จึงยังไม่ถูกลบ) → **ไม่ต้องใช้ทางสำรอง `--cascade=orphan`**
   - hash `som-web-7955fccc94` ได้ค่าเดิมทั้งสองรอบ (template เดิม = hash เดิม)
2. **Recreate ตอนแปลง db: ไม่เกิด** (ข้อ 1) → ไม่มีช่วงร้านล่ม ไม่มี 503 หลังแปลง (แผนคาดว่ามี) — ทดสอบ Recreate จริงด้วย `kubectl -n som-shop rollout restart deploy/som-db` (เสริม): Pod เก่า `Terminating` 10:36:51 → `Completed` 10:36:52 → **แล้วจึง** Pod ใหม่ `Pending` 10:36:52 → `1/1` 10:36:56 (rollout status 4.3 วิ, ไม่มี db 2 ตัวพร้อมกัน); web 4 ใน 5 ตัว `0/1` ชั่วครู่ (10:36:54–58) แต่เหลือ 1 ตัว ready → `/api/whoami` 300/300; หน้าแรก 503 จนกว่าจะ restart web (ออเดอร์หาย); RS ใหม่ `som-db-786556dc4f` + RS เดิม `som-db` 0, history `1, 2`
3. **เวลา rollout** 1.2→1.3 (3 replicas): **18.1 วิ** (undo 17.5 / 18.2 วิ, แปลง web 17.7 / 18.6 วิ) — เร็วกว่าที่แผนคาด 30–45 วิ (เครื่องทดสอบ 32 CPU, image อยู่บน Node แล้ว); undo จาก 1.4 กลับ 1.3 = 0.1 วิ (RS 1.3 ยังพร้อมครบ); scale 3→5 5.4 วิ; **rollout restart 5 replicas 32.9 วิ**
4. **err** (`/api/whoami` 300 ครั้ง / `/` 150 ครั้ง)
   | ขั้น | whoami | หน้าแรก `/` |
   |---|---|---|
   | แปลง web (Pod เดิมของ RS **ยังไม่มี preStop**) | **2/300**, **1/300** (2 รอบ) `Connection reset by peer` | 1/150, 0/150 |
   | rolling 1.2→1.3 | **0/300** | 0/150 |
   | undo → 1.2 / undo → 1.3 | 0/300, 0/300 | 0/150, 0/150 |
   | 1.4 พัง (700 ครั้ง ครอบ deadline) | **0/700** | 0/350 |
   | undo จาก 1.4 | 0/300 | 0/150 |
   | rollout restart 5 replicas (หลังลบ db) | **0/300** | 25/150 = HTTP 503 ช่วง 5.1 วิแรก (ร้าน 503 อยู่แล้วก่อน restart; หายเมื่อ Pod ใหม่ตัวแรก seed ตาราง) |
   | rollout restart som-db (Recreate, เสริม) | 0/300 | 136/150 (503 ตลอดจน restart web) |
5. **ข้อความจริงของ 1.4**: `kubectl get pods` ~8 วิแรก **`PodInitializing`** (init `wait-for-db`/`db-seed` 1.3 รันผ่าน) แล้ว `ErrImagePull`/`ImagePullBackOff` (81 วิ: `ImagePullBackOff`); Event `Failed to pull image "som-shop-web:1.4": failed to pull and unpack image "docker.io/library/som-shop-web:1.4": failed to resolve reference "docker.io/library/som-shop-web:1.4": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed`; `error: deployment "som-web" exceeded its progress deadline` (exit 1) ~60 วิหลัง set image; `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`; `Progressing=False ProgressDeadlineExceeded: ReplicaSet "som-web-6cd4d5d687" has timed out progressing.`; สั่งซื้อระหว่างนั้นได้ `order_id 5`
6. **หน้าร้าน 1.3**: `🐱 เสิร์ฟโดย Pod: som-web-ffc7b9f94-g88n9 · เวอร์ชัน 1.3`, แบนเนอร์ `🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟`, footer `Kubernetes LAB 007 · namespace som-shop` (curl จาก host; ธีมดูจาก browser ในฉาก handoff)
7. **change-cause / revision**: annotation ใน YAML แสดงที่ rev 1 ✅; `annotate --overwrite` หลัง set image → rev 2 `1.3 ธีม sunset` ✅; undo → rev 3 = `1.2 แปลงเป็น Deployment` (ข้อความของรุ่นเป้าหมาย) → undo → rev 4 `1.3 ธีม sunset`; history หลัง undo สองครั้ง: **`0, 3, 4`**; หลัง 1.4 `0, 3, 4, 5 (1.4 (ทดสอบรุ่นพัง))` → undo → **`0, 3, 5, 6 (1.3 ธีม sunset)`**; restart → rev 7 สืบทอด `1.3 ธีม sunset`
8. `set image ... db-seed=som-shop-web:1.3` ✅ (template `postgres:17.11-alpine som-shop-web:1.3 | som-shop-web:1.3`); 1.4 เปลี่ยนเฉพาะ web ✅ (Event init ใช้ `som-shop-web:1.3`)
9. resource ✅ 5 web + 1 surge + 1 db ไม่มี Pending (requests lab-worker 500m/882Mi, lab-worker2 300m/434Mi); Pod เก่า **`Terminating` → `0/1 Error` 5 วิต่อมา** (preStop 5 วิ แล้ว SIGTERM) ✅
10. **ลบ db + rollout restart** ✅: Pod db ใหม่ Ready 4.4 วิ (IP `10.244.2.98 → 10.244.1.67` ย้ายไป lab-worker2); **ต่างจากบท 006: web ทุกตัว readiness ล้มชั่วครู่** (Event `Readiness probe failed: HTTP probe failed with statuscode: 503` ทั้ง 5 Pod) → 2 วิหลัง db Ready ยังได้ `curl` code `000` (เชื่อมต่อไม่ได้) แล้วเป็น `503` + `/api/health` `{"ok":true,"db":"up"}`; psql `ERROR:  relation "orders" does not exist`; `rollout restart deploy/som-web` → db-seed `seeded 6 products (new: 6)` → **orders=0** ทุก Pod; ลบ ns som-shop 27.9 วิ แล้ว 30080 ว่าง

## การเปลี่ยนแปลงจากแผน

1. **คัดลอกแอป `app/` เข้า `som-shop-v3/`** (ตามคำสั่งงาน แทนการ build จากโฟลเดอร์บท 006 ในแผน LAB 0) — LAB 0 build จาก `som-shop-v3/app`; โค้ดไม่แก้ (page.tsx ยังมี fallback footer `LAB 006` แต่ env ใน YAML ทับเป็น `LAB 007`)
2. **ไฟล์ patch ย้ายไป `patches/`** (`lab05-readiness/patches/readiness-broken-patch.yaml`, `lab06-broken/patches/crash-patch.yaml`, `lab07-zero-downtime/patches/graceful-patch.yaml`) และ **`zero-zero.yaml` ไป `lab04-strategy/exercise/`** — `kubectl apply -f <โฟลเดอร์>/` หยิบไฟล์ patch ไปด้วยแล้วได้ `error validating "...-patch.yaml": error validating data: [apiVersion not set, kind not set]` และ zero-zero ทำให้มี `The Deployment "zero" is invalid` ปนผลปกติ
3. **LAB 5 Service `web` อยู่ใน `web-minready.yaml`** (แผนไม่ได้ระบุไฟล์ Service ของ LAB 5)
4. **LAB 9 เพิ่ม `web-svc-all.yaml`** (ทางเลือกแทน `patch --type=json remove` — ทดสอบแล้วทั้งคู่)
5. **LAB 10 ขั้น 3 (แปลง db) ไม่มี Recreate/503/ข้อมูลหาย** — Deployment รับเลี้ยง RS เดิมเพราะ template เหมือนกัน → README ต้องเปลี่ยนคำเตือน "ข้อมูลจะหาย" เป็น "template เหมือนเดิม → รับเลี้ยง ไม่สร้าง Pod ใหม่ ข้อมูลอยู่ครบ" และย้ายการสาธิต Recreate ไปที่ `rollout restart deploy/som-db` (ทดสอบแล้ว ข้อ 2 ด้านบน — แนะนำใส่เป็นขั้นเสริมหรือใช้แทน "ลบ Pod db" ในขั้น 10 เพราะได้เห็นทั้ง Recreate และข้อมูลหาย); ขั้น 4 หน้าเว็บ **ไม่** หายเป็น 503 และออเดอร์ **ไม่** เป็น 0 → ออเดอร์สะสม 2 (ก่อนแปลง) + 2 (ขั้น 5) = **4**
6. **LAB 10 ขั้นแปลง web มี err 1–2/300** (แผนคาด err=0) เพราะ Pod เดิมของ ReplicaSet บท 006 ไม่มี preStop — README ควรเขียน "อาจมี error 1–2 ครั้ง เพราะบูธเดิมยังไม่มี preStop; หลังจากนี้ทุกบูธมีแล้ว err=0"
7. LAB 10 ขั้น 10: หลังลบ db มีช่วง 2–5 วิที่เปิดหน้าเว็บไม่ได้เลย (web ทุกตัว not ready) ก่อนเป็น 503 — README เตือนว่า browser อาจขึ้น error ชั่วครู่ก่อนหน้า "ร้านกำลังเตรียมสินค้า"
8. วิธีนับ Pod ใน LAB 4: ถ้า README ให้นับจาก `get pods -w` ต้องบอกให้ **ไม่นับบรรทัด `Terminating`/`Completed`** (ตัวที่กำลังปิด) หรือใช้ `kubectl -n strategy-lab get rs -l app=<name> -o jsonpath='{..metadata.annotations.deployment\.kubernetes\.io/max-replicas}'` ดูเพดานที่ controller คำนวณ (rolling 4 → 5, replicas 10 → 13)
9. hit.sh/คำสั่งรอของ agent: ห้ามใช้ `pgrep -f '[h]it.sh -q'` รอ hit.sh เมื่อ command line ของ shell มีข้อความ `hit.sh -q` อยู่ (จับตัวเอง ค้าง) — ใช้ `wait $PID`; รอบ v3 ของ LAB 7 รันระหว่างลูปค้างแต่ผลครบ (บันทึกใน log)

## ป้าย/ข้อความ/ฉากในภาพ storyboard (`images.json`) เทียบผลจริง

| ภาพ | ตอนนี้ | ผลจริง / ควรใช้แทน |
|---|---|---|
| **T29** (needs_test) | `ReplicaSet som-web (เดิม)`, `ownerReferences: Deployment`, `app=som-web`, `3 → 0`, `0 → 3`; caption "(ต้องยืนยันใน LAB)" | ✅ ป้ายตรงทั้งหมด (LAB 8 และ LAB 10) — **caption ตัด "(ต้องยืนยันใน LAB)"** และเติมได้ว่า "RS เดิมโผล่ใน rollout history เป็น REVISION 0; ถ้า template เหมือนกันทุกตัวอักษร RS เดิมกลายเป็นรุ่นปัจจุบันโดยไม่เกิด rolling" |
| **L06** (needs_test) | `1` `3` `4` `5` + `rollout undo --to-revision=2` | ✅ ตรงเป๊ะ (history `1, 3, 4, 5`, rev 5 = ข้อความของ rev 2) |
| **L08** (needs_test) | `rolling.yaml: max 5, min 3` / `nosurge.yaml: max 4, min 3` / `recreate.yaml: min 0` | ✅ ตรง (นับ Pod ที่ยังไม่ถูกสั่งลบ); caption ใช้ได้ |
| **L09** (needs_test) | `minReadySeconds: 10`, `statuscode: 404`, `0/1 Running` | ✅ ตรง (AVAILABLE ช้ากว่า READY 10–11 วิ) |
| **L11** (needs_test) | `errors: 3/300` / `errors: 0/300` | **แก้ `errors: 3/300` → `errors: 4/300`** (จริง 4, 4, 1 จาก 3 รอบ) หรือ `errors: 1–4/300`; `0/300` ✅ (3/3 รอบ) |
| **L12** (needs_test) | `rs/web`, `ownerReferences: Deployment`, `3 → 0`, `0 → 3`, `http://web` | ✅ ตรง (client ERR 0) |
| **L16** (needs_test) | ป้าย `Recreate`, `err=0`; caption "som-db แบบ Recreate ปิดก่อนเปิดใหม่ (ข้อมูล emptyDir หาย)"; Scene "database booth briefly shows a closed shutter and an empty chest" | **ไม่ตรง** — db ถูกรับเลี้ยง ไม่ปิด/ไม่สร้างใหม่ ข้อมูลอยู่ครบ และ web มี err 1–2: Scene ควรเป็น "the database supervisor just receives an owner badge while its booth keeps serving and its chest stays full; blue web booths swapped one by one"; ป้าย `Recreate` → **`template เดิม = ไม่สร้างใหม่`** (หรือ `som-db รับเลี้ยงทันที`); `err=0` → **`err 1–2/300`**; caption → "apply k8s/ (ชื่อ/selector เดิม) — som-db template เดิมจึงถูกรับเลี้ยงทันที (Pod เดิม ข้อมูลอยู่ครบ) ส่วน som-web รับเลี้ยง RS เดิมแล้วแทนบูธทีละตัว hit.sh err 1–2 จาก 300 เพราะบูธเดิมยังไม่มี preStop" |
| **L17** (needs_test) | `เวอร์ชัน 1.2` → `1.3`, `hit.sh -q 300`, `err=0` | ✅ ตรง (0/300, rollout 18 วิ) |
| **L18** (needs_test) | `localhost:30080`, `เวอร์ชัน 1.3`, `เมนูใหม่: ขนมปลาทูน่าอบกรอบ`, `som-web-…` | ✅ ตรง (แบนเนอร์จริงมี `🎉` นำหน้าและ `🐟` ท้าย; ชื่อ Pod รูปแบบ `som-web-ffc7b9f94-g88n9`) |
| **L19** (needs_test) | `orders: 2` | **แก้เป็น `orders: 4`** (db ไม่หายตอนแปลง → 2 + 2); caption ✅ |
| **L20** (needs_test) | `som-shop-web:1.4`, `ImagePullBackOff`, `ProgressDeadlineExceeded`, `err=0` | ✅ ตรง (700/700, deadline ~60 วิ); caption ใช้ได้ (เพิ่มได้: 8 วิแรกเป็น `PodInitializing`) |
| **L22** (needs_test) | `orders: 2` → `orders: 0`, `503` | **แก้ `orders: 2` → `orders: 4`** (ถ้า README ไม่ให้สั่งซื้อระหว่าง 1.4; รอบทดสอบสั่งเพิ่ม 1 → `5 → 0`); `503` ✅ |
| T09 (pre-check) | `pod-template-hash=6f58b8bd67` / `7c987cc6b4` / `web-6f58b8bd67-frgpm` | ค่าตัวอย่างใช้ได้; ค่าจริง LAB 1–2 = `779cb4fbb8` → `7c974c65c6` (`web-779cb4fbb8-4jwkw`) ถ้าอยากให้ตรง LAB |
| T11 | 7 แถว เก่า/ใหม่ | ✅ ลำดับตรง (LAB 2 และ LAB 8); หมายเหตุ README: `describe deploy` อาจรวม event ท้ายเป็น `(combined from similar events)` |
| T12 | 3 → +1/−0, 4 → +1/−1, 10 → 13/8 | ✅ ยืนยันจริงทั้ง 3 ค่า (LAB 5 replicas 3 เห็น `4/3` สูงสุด, LAB 4) |
| T15 | `minReadySeconds: 5` | ไม่ผิด (ภาพแนวคิด) แต่ LAB ใช้ 10 (LAB 5) และ 3 (LAB 10) — ถ้าอยากตรง LAB ใช้ `minReadySeconds: 10` |
| T18 | `errors: 0/300` | ✅ (LAB 7 nginx 3/3 รอบ, LAB 10 Next.js ทุกขั้นหลังแปลง) |
| T19 / T20 / L10 | `ImagePullBackOff`, `READY 3/3`, `UP-TO-DATE 1`, `AVAILABLE 3`, `exceeded its progress deadline`, `progressDeadlineSeconds: 30` | ✅ ตรงเป๊ะ (LAB 6 และ LAB 10) |
| T21 / T22 / T23 | change-cause สืบทอด / 1, 3, 4 | ✅ แนวคิดตรง (LAB 3 จริง `3 v3 set env` / `4 v3 set env`) |
| T24 | Warning last-applied | ✅ ข้อความตรงทุกตัวอักษร |
| T25 / L07 | pause → revision เดียว | ✅; เพิ่มได้ว่า undo ระหว่าง pause → `you cannot rollback a paused deployment` |
| T30 | `--cascade=orphan`, `ลบ Pod เก่าทีหลัง` | ✅ ใช้ได้ (ทางสำรอง err 1 ตอนลบ Pod เก่าพร้อมกัน — ทางหลักรับเลี้ยง err 0) |
| T31 | 3 อาการ | ✅ (ImagePullBackOff LAB 6, 0/1 Running LAB 5, CrashLoopBackOff LAB 6) |
| T13 / T14 / L14 / L23 | `Recreate` | ✅ แนวคิดถูก (ยืนยันลำดับปิดก่อนเปิดด้วย `rollout restart deploy/som-db`) แต่ไม่ได้เกิดตอนแปลง — ไม่ต้องแก้ภาพ |
| L01 | `som-shop-web:1.2` / `1.3` บน Node | ✅ (README: `.status.images` อาจยังว่างใน 1 นาทีแรกหลัง kind load → ใช้ `crictl images`) |
| L03 | scale RS → `ปรับกลับ` | ✅ (Pod เกินเกิดแล้วถูกลบใน ~1 วิ) |
| L13 | `~20%` | ✅ (500 ครั้ง = 20.2%; รอบ 50 ครั้งแกว่ง 3–12 — caption "ราว 1 ใน 5" ควรเติม "สุ่ม แต่ละรอบไม่เท่ากัน") |
| L21 | `3 → 5`, `ไม่เกิด revision` | ✅ |

## ข้อควรระวังสำหรับนักศึกษา (ใส่ README)

- `kubectl apply -f <โฟลเดอร์>/` อ่านทุกไฟล์ `.yaml` ในโฟลเดอร์นั้น (ไม่ลงโฟลเดอร์ย่อย) — ไฟล์ patch จึงแยกไว้ใน `patches/`
- Pod ที่กำลังปิดอาจขึ้น `Completed` (nginx/postgres ปิดสะอาด) หรือ `Error` (Next.js รับ SIGTERM) ชั่วครู่ — ไม่ใช่ rollout พัง และอย่านับเป็น Pod ที่ทำงาน
- `describe deploy` อาจรวม Events ท้าย ๆ เป็น `(combined from similar events)`
- ลืม `annotate` = revision ใหม่สืบทอด CHANGE-CAUSE เดิม (รวมถึง `rollout restart`); undo เอาข้อความของรุ่นเป้าหมายกลับมา
- undo ระหว่าง pause ไม่ได้ — `resume` ก่อน
- ย้ายจาก ReplicaSet: RS เดิมโผล่ใน `rollout history` เป็น `REVISION 0`; template เหมือนเดิมทุกตัวอักษร → ไม่มีอะไรถูกสร้างใหม่ (เช่น som-db) — ข้อมูลไม่หายตอนแปลง แต่หายเมื่อ Recreate/restart ครั้งถัดไป (emptyDir)
- ตอนแปลง som-web อาจเห็น error 1–2 ครั้ง (บูธเดิมยังไม่มี preStop) — หลังจากนั้นเปลี่ยนรุ่น/undo/restart ได้ err=0
- rollout พัง (1.4) ร้านยังขายได้ แต่ `rollout status` รอจนเกิน deadline (~60 วิ) แล้ว exit 1 — Kubernetes ไม่ undo ให้; ช่วงแรก Pod ขึ้น `PodInitializing` ก่อนเป็น `ErrImagePull`
- หลัง `kubectl patch svc` เปลี่ยน selector รอ 1–2 วิก่อนยิงทดสอบ (EndpointSlice/kube-proxy ยังไม่อัปเดต)
- canary ด้วยจำนวน Pod เป็นการสุ่ม: 50 ครั้งอาจได้ 3–12 ครั้ง (คาด 10); ต้องยิงหลายร้อยครั้งจึงใกล้ 20%
- `kubectl get endpointslice` คอลัมน์ ENDPOINTS ตัดที่ 3 IP (`+ 2 more...`) — ดู 5 IP ด้วย jsonpath
- ลบ db แล้วหน้าเว็บอาจเปิดไม่ได้เลย 2–5 วิก่อนเป็น 503; ลบ namespace ที่มี preStop ใช้เวลา ~27 วิ
- ตัวเลข error/เวลาขึ้นกับความเร็วเครื่อง (ทดสอบบน 32 CPU: rollout 1.3 ~18 วิ) เครื่องช้ากว่าใช้เวลานานกว่าและอาจเห็น error ในรอบไม่มี preStop มากกว่า
- ถ้าต้องหยุด process ด้วย pattern ให้ใช้ `pkill -f "[k]ubectl ..."` และอย่าให้ command line ของ shell เองมีข้อความเดียวกัน

## สถานะไฟล์/cleanup

- scratch (`logs/007_deployment/scratch/`): `r.sh` (ตัวรันของ agent), `container-name`, `h7host.out`, `storyboard-extract.txt`; askpass ลบแล้ว; ไม่ได้ใช้ /tmp ของเครื่อง (ยกเว้นไฟล์ output ของ background task ที่ Claude Code สร้างเอง)
- ใน container: ตัวช่วยของ agent `/root/{count.sh,round.sh,round10.sh}` และไฟล์ผล `/root/*.out`, ไฟล์เดิมที่ย้ายออก `/root/old-*.yaml` (ไม่อยู่ใต้ `/workspace`); `/workspace/examples` ไม่ได้ใช้
- skill k8s-lab: คำสั่งทดสอบ SSH ด้วย askpass ต้องใช้ **`setsid -w`** ไม่เช่นนั้น output หาย (rc=0 แต่ไม่พิมพ์อะไร) — ควรแก้ในไฟล์ skill
- container `k8s-lab-deploy007lab-06e5cc` ยังรัน (SSH 2224, NodePort 30090–30092) — ผู้ประสานงานลบเอง
