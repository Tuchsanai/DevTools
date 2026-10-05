# SUMMARY: ทดสอบ LAB บท 009 StatefulSet (รันจริง 5 ต.ค. 2569)

- container ทดลอง `k8s-lab-sts009lab-19f6aa` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`, NodePort `30090-30092→30080-30082`) **ยังเปิดอยู่** ตามคำสั่ง (ดู `handoff.md`) ไม่ได้แตะ `k8s-lab` ของผู้เรียน / `deep_vision_5090_vllm` / ไม่ได้ `docker system prune`; `cgroup v2 controllers: cpuset cpu io memory hugetlb pids rdma`
- `k8s-up` สำเร็จ 3 Node Ready (ไม่ได้จับเวลา: เครื่อง agent ไม่มี `bc` บรรทัดท้าย `k8s-up.log` จึงว่าง); kubectl v1.37.1 / Node v1.37.0 / containerd 2.3.4
- `docker cp 009_kubernetes_statefulset` ไปที่ `/workspace/` (ไม่ได้ copy บทอื่น จึงยืนยันว่าบทนี้ใช้ได้ด้วยตัวเอง) แล้วรันทุกคำสั่งจาก `/workspace/009_kubernetes_statefulset/02_LAB` (LAB 1–9 `labs/labNN-*`, LAB 10 `som-shop-v5`); md5 ไฟล์ใน container ตรงกับ repo 46 ไฟล์
- log: `k8s-up.log`, `lab00.log` … `lab09.log`, `lab10.log` (ขั้น A–I), `lab10-final.log` (คืนสภาพ + ทดสอบจาก host + SSH), `screenshot-scenes.log` (ซ้อมฉาก handoff 3–5); บรรทัด `### hh:mm:ss` = UTC ของเครื่อง agent; `date` ใน shell ของ k8s-lab = เวลาไทย แต่ `date` ใน nginx/busybox/postgres = **UTC** (เช่น `first-born web-1 06:51:47` = 13:51:47 ไทย)
- ทดสอบจาก "เครื่องนักศึกษา" ด้วย host ของ agent: `http://172.18.0.1:30090` → HTTP 200, footer `Kubernetes LAB 009 · namespace som-shop`, `/api/stats` `orders=4 products=6`, `hit.sh` จาก host `ok=30 err=0` (กระจาย 3 Pod); SSH password `-p 2224` → `k8s-lab`

## ไฟล์ที่สร้าง (`009_kubernetes_statefulset/02_LAB/`)

- `labs/` 15 ไฟล์:
  - `lab01-compare/{web-deploy,web-sts}.yaml` — Deployment `web-d` (app=web-d) กับ StatefulSet `web` (app=web) รันคู่กันได้
  - `lab02-headless/{svc-headless,sts,dns-pod}.yaml`
  - `lab03-vct/sts.yaml` (headless Service + StatefulSet + vct `www`; ใช้ต่อใน LAB 4–8)
  - `lab04-order/{bad,par}.yaml`
  - `lab05-retention/par.yaml`
  - `lab06-update/{show.sh,partition-2.yaml,partition-0.yaml}`
  - `lab07-ondelete/{min-ready.yaml,ondelete.yaml}`
  - `lab09-node-down/sts-tol.yaml`
- `som-shop-v5/`:
  - `app/` สำเนา `008…/som-shop-v4/app` (ไม่มี node_modules/.next, **ไม่แก้โค้ด**); `hit.sh` สำเนา ไม่แก้
  - `k8s-008/{00-namespace,10-db,20-web}.yaml` = สภาพท้ายบท 008 (Deployment + PVC `som-db-data` + Service ClusterIP) เปลี่ยนแค่คอมเมนต์และ footer `LAB 009`
  - `k8s/{00-namespace,10-db,20-web}.yaml` — `10-db` = headless Service `som-db` + StatefulSet `som-db` (vct `data` 1Gi standard RWO); `20-web` = ของ 008 เปลี่ยน host เป็น `som-db-0.som-db` (wait-for-db, db-seed, web) + change-cause `1.2 db เป็น StatefulSet (som-db-0.som-db)`
  - `migrate/data-som-db-0-pvc.yaml` (`volumeName: PVNAME`), `extra/replica.yaml`
- คอมเมนต์ภาษาไทยทุกไฟล์; ใช้รหัสผ่าน LAB `meow1234` ตามบทก่อน ไม่มี credential จริงหรือ `.env`
- ยังไม่มี `02_LAB/README.md` (อยู่นอกขอบเขตงานนี้ เหมือนบท 008)

## ผลรายข้อ

| LAB | ผล | เวลาจริง | ผลจริงสำคัญ |
|---|---|---|---|
| 0 | ✅ | postgres pull+save+load 17.2 วิ, build 1.2 29.1 วิ, kind load 5.0 วิ | 3 Node Ready; `standard (default) rancher.io/local-path Delete WaitForFirstConsumer false`; `kubectl get pv,pvc -A` → `No resources found`; postgres/som-shop-web:1.2 อยู่บน lab-worker และ lab-worker2 (nginx/busybox ไม่ได้โหลดล่วงหน้า Node ดึงเองตอนใช้) |
| 1 | ✅ | Deployment Ready ~8–10 วิ; sts ครบ 3 ตัว ~14 วิ (web-0 รอ pull nginx) | Deployment `web-d-d8cf7b4b8-lgww5/pgrgg/vn6cv` เกิดพร้อมกัน; StatefulSet เกิด `web-0` ก่อน แล้ว `web-1`, `web-2`; `hostname` = ชื่อ Pod ทั้งสองแบบ; label `app=web,apps.kubernetes.io/pod-index=1,controller-revision-hash=web-8776b8748,statefulset.kubernetes.io/pod-name=web-1`; ลบ Pod: Deployment ได้ชื่อใหม่ `web-d-d8cf7b4b8-d7zkr`, StatefulSet ได้ `web-1` คืน UID ใหม่ (`3091ecf4…` → `1e1cfe64…`) IP ใหม่ (`10.244.1.3` → `10.244.1.5`) |
| 2 | ✅ (ยืนยันจุด Pod ไม่ Ready) | – | `web ClusterIP None`; `kubectl run dns … --rm -it` ใช้ได้ (ทดสอบผ่าน `script` ให้มี tty); `nslookup web` → 3 Address **แต่มีบรรทัด `** server can't find web.cluster.local: NXDOMAIN` / `web.svc.cluster.local: NXDOMAIN` ปนหลายบรรทัด** (busybox ลองทุก search domain); `nslookup web-0.web.default.svc.cluster.local` → IP เดียว; `wget -qO- web-1.web` → `first-born web-1 06:49:20`; **ทำ web-1 ไม่ Ready** (`kubectl exec web-1 -- rm …/index.html` → `Readiness probe failed: HTTP probe failed with statuscode: 403`) → `nslookup web` เหลือ 2 Address, `nslookup web-1.web.default.svc.cluster.local` → `NXDOMAIN` exit 1, EndpointSlice ยังแสดง IP ครบในคอลัมน์ ENDPOINTS แต่ `conditions.ready=false`; **`wget web-1.web` (ชื่อสั้น) → `wget: can't connect to remote host (127.0.53.53): Connection refused`** (หลุดไปถาม DNS ภายนอก `.web` เป็น TLD จริง) ส่วนชื่อเต็มได้ `bad address`; เขียนไฟล์คืน → Ready ภายใน ~6 วิ กลับเข้า DNS |
| 3 | ✅ | PVC/Pod ห่างกัน ~5 วิ (image อยู่แล้ว) | `www-web-0 → 1 → 2` เกิดตามลำดับ (Pending → Bound เมื่อ Pod ของตัวเองถูก schedule); `10Mi RWO standard`, label `app=web`; `first-born web-0 06:51:43 / web-1 06:51:47 / web-2 06:51:52`; claimName ของ web-1 = `www-web-1`; ลบ web-1 → ข้อความเดิม Node เดิม (lab-worker) |
| 4 | ✅ | bad-0 ค้าง 0/1 ≥16 วิ; touch → bad-1 เกิดใน ≤2 วิ | `bad 0/3`, ไม่มี bad-1 จน `touch /tmp/ready`; bad-2 เกิดหลัง touch ใน bad-1; Parallel: `par-0/1/2 Pending` ในวินาทีเดียวกัน → Running ใน 1 วิ; scale par 3→0 → Terminating พร้อมกันทั้ง 3; scale web 3→1: `web-2 Terminating` ขณะ `web-1 Running` → แล้ว `web-1 Completed` → เหลือ web-0 (ทั้งหมด ~4 วิ); PVC 3 ใบยัง Bound |
| 5 | ✅ | – | default `{"whenDeleted":"Retain","whenScaled":"Retain"}`; scale 3 → `web-2` อ่าน `first-born web-2 06:51:52` เดิม; par: ownerReferences `[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"StatefulSet","name":"par",…}]` ส่วน `www-web-0` ownerReferences ว่าง; scale par 3→1 เหลือ `www-par-0`; ลบ sts par → PVC par หมด, PV ของ par 0 |
| 6 | ✅ (ยืนยัน rollout undo) | canary web-2 Ready ~8 วิ (pull 1.28); partition 0 → web-1 ~2 วิ แล้ว web-0 ~8 วิ; undo ทั้ง 3 ตัว ~6 วิ | default `{"rollingUpdate":{"maxUnavailable":1,"partition":0},"type":"RollingUpdate"}`; partition 2 → `currentRevision=web-67f445dc6c updateRevision=web-5888c97b8 updated=1/3` เฉพาะ web-2 1.28; **`rollout status` ตอน partition 2 จบทันที `partitioned roll out complete: 1 new pods have been updated...` exit 0**; partition 0 → ลำดับ 2→1→0, `partitioned roll out complete: 3 new pods have been updated...`; history REVISION 1, 2; **`kubectl rollout undo sts/web`** → `Warning: resource statefulsets/web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation…` + `statefulset.apps/web rolled back` → ทุกตัวกลับ 1.27 ลำดับ 2→1→0, revision hash เดิม `web-67f445dc6c` กลายเป็น REVISION 3 (history เหลือ `2, 3`); ไฟล์ first-born เดิมทุกตัว |
| 7 | ✅ (ยืนยัน minReadySeconds) | ดูช่อง "ผลจริง" | `minReadySeconds=10` (patch แล้วไม่เกิด rollout เอง) + set image 1.28 → web-2 เปลี่ยน 13:57:21, web-1 13:57:32, web-0 13:57:42 (**ห่าง ~10–11 วิ** เทียบ ~2 วิ ตอน undo ใน LAB 6), `available=2` ค้าง ~10 วิ หลังแต่ละตัว Ready; OnDelete: `{"type":"OnDelete"}`, set image 1.27 → 10 วิ ไม่มี Pod เปลี่ยน (`updated=/3`), **`kubectl rollout status` → `error: rollout status is only available for RollingUpdate strategy type` exit 1**; ลบ web-1 → web-1 1.27 ตัวเดียว (`updated=1/3`) ไฟล์ `first-born web-1 06:51:47` เดิม; ลบ web-0, web-2 → ครบ 3/3 |
| 8 | ✅ (ยืนยัน --cascade=orphan) | delete sts 0.04 วิ, Pod หายใน ≤2 วิ | PVC 3 ใบ Bound; apply → `service/web unchanged` + `statefulset.apps/web created` อ่าน first-born เวลาเดิมครบ; `--cascade=orphan` → `get sts` ว่าง แต่ Pod 3 ตัว Running, ownerReferences `[]`; ลบ web-2 ที่กำพร้า → ไม่มีใครสร้างคืน; apply ใหม่ → รับ web-0/1 เดิม (AGE ต่อเนื่อง 12s) ownerReferences `StatefulSet/web` และสร้าง web-2 ใหม่ |
| 9 | ✅ | ดูช่อง "ผลจริง" | apply `sts-tol.yaml` ทับ web เดิม → rolling update 3 ตัว (tolerations อยู่ใน template); web-1 อยู่ `lab-worker`; `docker stop lab-worker` ใช้ 1 วิ (14:00:25→26); **NotReady 40–50 วิหลัง stop** (14:01:06 Ready, 14:01:16 NotReady); **web-1 `1/1 Terminating` ~80 วิหลัง stop** (deletionTimestamp `07:01:50Z` รวม grace 5 วิ) Ready=False และ**ค้างจนถึง 3 นาที 21 วิหลัง stop** ไม่มี web-1 ใหม่, `sts web 2/3`; Taints `node.kubernetes.io/unreachable:NoExecute` + `NoSchedule`; ใส่ taint 14:04:11 → ≤15 วิ web-1 ใหม่ `0/1 Pending` `<none>`, event `FailedScheduling … 0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.`; PV nodeAffinity `["lab-worker"]`; เอา taint ออก + `docker start` → Node Ready 2 วิ, web-1 Ready 4 วิ บน lab-worker อ่าน `first-born web-1 06:51:47` เดิม; **ไม่ได้ kind load ระหว่าง Node หยุด**; หลัง LAB: 3 Node Ready, Taints `<none>`, image postgres/som-shop-web:1.2 บนทั้ง 2 worker ยังอยู่; ลบ sts/svc/PVC ของ web แล้ว PV ว่าง |
| 10 | ✅ ทุกขั้น A–I (+ เสริม H) | ดูหัวข้อถัดไป | ดูหัวข้อถัดไป |

## LAB 10: ผลแต่ละขั้น (ออเดอร์จาก `/api/stats`)

| ขั้น | ผลจริง | orders |
|---|---|---|
| A | `kubectl apply -f k8s-008/` → db rollout 6.9 วิ, web 10.2 วิ; POST 3 ครั้ง `order_id 1..3`; Pod `som-db-7b786655f5-bdsgq`, PVC `som-db-data Bound pvc-6c88d7af-…` | 0 → **3** |
| B (error) | **`kubectl apply -f k8s/10-db.yaml --dry-run=server`** ขณะ Service ClusterIP เดิมยังอยู่ → `statefulset.apps/som-db created (server dry run)` + **`The Service "som-db" is invalid: spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set`** exit 1 (ไม่ใช่ `spec.clusterIP … field is immutable` ตามที่แผนคาด); apply จริงใน ns ทิ้งได้ (`errtest`) ได้ข้อความเดียวกัน | 3 |
| B | patch PV → Retain; ลบ deploy/svc/pvc → PV `Released som-shop/som-db-data`; remove claimRef → `Available`; `sed … migrate/… \| kubectl apply -f -` → `persistentvolumeclaim/data-som-db-0 created`; apply `k8s/10-db.yaml` → rollout 1.5 วิ `som-db-0 1/1 Running`, `som-db ClusterIP None`, PV `Bound som-shop/data-som-db-0`; **web รุ่นเก่า (ยังใช้ `som-db`) ตอบ `orders=3` ได้ทันที** เพราะชื่อ headless `som-db` ชี้ IP ของ som-db-0 ตัวเดียว | **3** |
| B2 | apply `k8s/20-web.yaml` → rollout 18.9 วิ; ทันทีหลัง rollout ยังเจอ Pod เก่า (preStop 5 วิ) 2 ครั้ง, รอ 8 วิ ได้ Pod ใหม่ทั้งหมด; wait-for-db `som-db-0.som-db:5432 - accepting connections`; history `1 1.2 ร้านจำได้ (db ใช้ PVC)` / `2 1.2 db เป็น StatefulSet (som-db-0.som-db)`; คืน PV เป็น Delete; PVC label `app=som-db` | **3** |
| C | ลบ som-db-0 → ชื่อเดิม UID `ea0d5d48…` → `acfc1cf3…`, IP `10.244.2.45` → `10.244.2.48`, Node เดิม lab-worker2, `claimName=data-som-db-0`; stats 200 ทุกครั้ง (ไม่เจอ 503) | **3** |
| D | patch memory 768Mi → rollout 2.0 วิ, history REVISION 1, 2, Pod `768Mi som-db-84b948b59f`; POST สินค้า 4 | 3 → **4** |
| E | delete sts → Pod หาย, PVC `data-som-db-0 Bound`, stats `db-not-ready [503]`; apply `k8s/10-db.yaml` → `service/som-db unchanged`, `statefulset.apps/som-db created` (memory กลับเป็น 512Mi ตามไฟล์) | 503 → **4** |
| F | scale 3 → rollout 17.1 วิ; `som-db-1` lab-worker, `som-db-2` lab-worker2 (som-db-0 lab-worker2); PVC `data-som-db-1/2` ใหม่; psql `som-db-0: 4`, `som-db-1/2: ERROR:  relation "orders" does not exist`; `nslookup som-db` 3 Address, `som-db-1.som-db.som-shop.svc.cluster.local` IP เดียว; Warning PodSecurity ตอน `kubectl -n som-shop run dns`; stats 6 ครั้ง `orders=4` | **4** |
| G | scale 1 → som-db-2 Terminating ก่อน แล้วเหลือ som-db-0 ใน ~2 วิ; PVC 1/2 ยัง Bound → ลบเอง | **4** |
| H (เสริม) | `pg_reload_conf t`; replica rollout 6.0 วิ, init log `waiting for checkpoint` / `30955/30955 kB (100%), 1/1 tablespace` / `cloned`; exec ไม่ใส่ `-c` → `Defaulted container "postgres" out of: postgres, clone-from-primary (init)`; `t\|4`; POST → `primary: 5 replica: 5`; `pg_stat_replication` = `10.244.2.55\|streaming\|async`; INSERT บน replica → `ERROR:  cannot execute INSERT in a read-only transaction`; ลบ replica → `already-cloned` `t\|5`; ลบ som-db-0 → replica log `could not translate host name "som-db-0.som-db" to address: Name does not resolve` แล้ว `started streaming WAL from primary` เอง, `repl=1`, `primary: 6 replica: 6` (บรรทัด pg_hba.conf อยู่ใน PVC จึงรอด restart) — **ผ่านบนคลัสเตอร์สะอาดเป็นรอบที่ 2** | 4 → 5 → **6** |
| I | `kubectl delete ns som-shop` 32.2 วิ → PV หมด, `/var/local-path-provisioner` บนทั้ง 2 worker ว่าง | – |
| คืนสภาพ | `kubectl apply -f k8s/` (ร้านใหม่ ใช้ PVC จาก vct) → POST 4 ครั้ง (สินค้า 1,2,3,1) → ซ้อมฉาก screenshot 3–5 แล้วคืน replicas 1 + ลบ PVC 1/2 | **4** |

## จุดที่แผนสั่งให้ยืนยัน

1. **LAB 2 Pod ไม่ Ready หายจาก DNS** ✅ (`nslookup web` 3 → 2 Address, ชื่อรายตัว NXDOMAIN, EndpointSlice `ready=false`) และ **`kubectl run dns --rm -it`** ใช้ได้ (ต้องกด Enter ถ้าไม่เห็น prompt: `If you don't see a command prompt, try pressing enter.`; ตอน `exit` มี `Session ended, resume using 'kubectl attach dns …'` แล้ว Pod ถูกลบ) — เพิ่ม `dns-pod.yaml` เป็นทางเลือกแบบ `kubectl exec dns -- nslookup …`
2. **LAB 6 `rollout undo sts/web`** ✅ (มี Warning last-applied); **LAB 7 `minReadySeconds`** ✅ (ห่าง ~10–11 วิ ต่อ Pod)
3. **LAB 8 `--cascade=orphan`** ✅
4. **LAB 10 error apply headless ทับ ClusterIP** ✅ ข้อความจริง `The Service "som-db" is invalid: spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set`
5. **LAB 10 เสริม replica บนคลัสเตอร์สะอาด** ✅ (ผลตรง pre-check ทุกตัวเลข 30955 kB, 5=5, 6=6)
6. **ลำดับ OrderedReady/Parallel, retention, partition/OnDelete, Node ล่ม, ย้าย PVC เป็น data-som-db-0** ✅ ทั้งหมด (ตารางด้านบน); Node กลับ Ready ก่อน LAB 10 และไม่ได้ kind load ระหว่าง Node หยุด

## การเปลี่ยนแปลงจากแผน

1. **ไม่มี `scratch/split-contract.md` และ `logs/005_rs_deploy_svc/precheck.md`** ใน repo → ใช้ `plan.md` + `scratch/` + โครงไฟล์บท 008 แทน
2. **LAB 1 Deployment ชื่อ `web-d` (app=web-d)** เพื่อ apply คู่กับ StatefulSet `web` ได้พร้อมกัน; `web-sts.yaml` มี `serviceName: web` แต่ยังไม่สร้าง Service (สร้างได้ปกติ — Service มาใน LAB 2)
3. **LAB 2 เพิ่ม `dns-pod.yaml`** และใช้ "ลบ index.html" ทำให้ไม่ Ready (sts ของ LAB 2 ไม่มี PVC เขียนหน้าเว็บใหม่ทุกครั้งที่เริ่ม → ลบ Pod ก็คืนสภาพ)
4. **`lab03-vct/sts.yaml` รวม headless Service ไว้ในไฟล์** ใช้ต่อ LAB 4–8; LAB 9 apply `sts-tol.yaml` ทับ web เดิม (rolling update, PVC เดิม) แทนการสร้างใหม่
5. **LAB 4 `par.yaml` ไม่มี vct** (เห็น Pending → Running พร้อมกันใน 1 วิ และ scale 3→0 Terminating พร้อมกัน ไม่มี PVC ต้องเก็บกวาด); vct + retention อยู่ที่ `lab05-retention/par.yaml` ตามแผน
6. **LAB 6 ไม่มี `sts.yaml`**: ใช้ web ของ LAB 3 + `partition-2.yaml`/`partition-0.yaml` (`kubectl patch sts web --patch-file …` เลี่ยง JSON ในบรรทัดคำสั่ง) + `show.sh` (แก้หลังรันครั้งแรก: คอลัมน์ `AGE` → `CREATED` เพราะเป็นเวลาสร้าง); เพิ่ม `rollout undo`
7. **LAB 7 ลำดับ: minReadySeconds ก่อน** (`min-ready.yaml` + set image 1.28 หลัง undo กลับ 1.27) แล้ว **OnDelete** (`ondelete.yaml` ตั้ง `minReadySeconds: 0` + `rollingUpdate: null`) + set image 1.27 ตามแผน; จบด้วยลบ web-0/web-2 ให้ครบรุ่นเดียว
8. **LAB 10 ขั้น B ให้ดู error ด้วย `--dry-run=server`** แทน apply จริง: ถ้า apply จริงทั้งไฟล์ StatefulSet จะถูกสร้าง (Service ล้มอย่างเดียว) และสร้าง PVC `data-som-db-0` เปล่าจาก template ก่อนเราย้าย PV → ย้ายข้อมูลไม่ได้
9. **`k8s/` มี `00-namespace.yaml` ด้วย** → `kubectl apply -f k8s/` สร้างร้านใหม่ทั้งร้านได้ (ใช้ตอนคืนสภาพ); `k8s-008/` แยกโฟลเดอร์ห้ามปนกับ `k8s/`
10. **README เลือกคืน PV เป็น `Delete` หลังขั้น B2** (cleanup `delete ns` จึงไม่เหลือ PV); replica เพิ่ม `resources` (แผนไม่มี)
11. ขั้น F ไม่ได้รัน `for i in 1 2 3; do st; done` แบบรอ ใช้ curl 6 ครั้ง

## ป้าย/ข้อความในภาพ storyboard ที่ไม่ตรงผลจริง (ควรแก้)

| ภาพ | ตอนนี้ | ผลจริง / ค่าที่ควรใช้ |
|---|---|---|
| **L11** Text | `"docker stop lab-worker2"` | Node ของ web-1 แล้วแต่ scheduler (รอบนี้ **`lab-worker`**) → ใช้ **`"docker stop $N"`** (หรือ `"docker stop lab-worker"`); caption "รอ ~2.5 นาที ยังค้าง" → "**รอ 3 นาที ยังค้าง**" (Terminating ~80 วิหลัง stop ค้างถึง 3 นาที 21 วิ) |
| **L01** caption | "image postgres:17.11-alpine, nginx:1.27/1.28-alpine, som-shop-web:1.2 พร้อม" | LAB 0 โหลดเฉพาะ `postgres:17.11-alpine` + `som-shop-web:1.2`; nginx/busybox **Node ดึงจาก Docker Hub เองตอนใช้** (ไม่ต้อง kind load) → "image postgres:17.11-alpine และ som-shop-web:1.2 อยู่บนทุก Node" (Text ในภาพไม่ต้องแก้) |
| **L08** caption | "rollout history มี 2 revision" | ถูกก่อน undo; ถ้า README ใส่ `rollout undo` ต่อท้าย ให้เติม "→ rollout undo กลับ 1.27 (history เป็น 2, 3)" |
| **L03** / **T12** | ภาพสมุดแสดง 3 บรรทัดสะอาด | ผลจริงของ busybox มีบรรทัด `** server can't find web.cluster.local: NXDOMAIN` ปน (ไม่ต้องใส่ในภาพ แต่ README ต้องเตือน); T12 "ไม่ Ready = ไม่อยู่ในสมุด" ✅ ยืนยันแล้ว |
| **T02** Text | `"PANIC"` | เป็นผลจาก pre-check ของบท 008 เท่านั้น; LAB run ของ 008 ทั้ง 3 รอบได้ "ออเดอร์หาย + restart" ไม่เจอ PANIC → แนะนำ **`"ออเดอร์หาย"`** (caption "ออเดอร์หาย/PANIC" ใช้ได้) |
| **T05** Text | `som-db-7b786655f5-9hf7p` | hash ของ RS ตรง (`som-db-7b786655f5-…` รอบนี้ `-bdsgq`) ส่วนท้ายสุ่มทุกครั้ง — ใช้ได้ |

ภาพอื่น (L02, L04–L07, L09, L10, L12, L14–L23, T08, T09, T15–T24, T26, T27, T29, T31, T33, T34) ตรงผลจริง: `orders=3/4`, `REVISION 2`, `memory: 768Mi`, `data-som-db-0: Bound`, `relation "orders" does not exist`, `streaming async`, `cannot execute INSERT in a read-only transaction`, `web-1 Pending`, `didn't match PersistentVolume's node affinity`, `updated=1`, `web-1: 1.27` / `web-0, web-2: 1.28`, `bad-0 0/1`, `2 → 1 → 0` ✅

## ข้อควรระวังสำหรับนักศึกษา (ใส่ใน README)

1. `nslookup` ของ busybox พิมพ์ `NXDOMAIN` ของ search domain อื่นปนกับคำตอบจริง → ดูเฉพาะบรรทัด `Name:`/`Address:` หลัง `Name: web.default.svc.cluster.local`
2. **ชื่อสั้น `web-1.web` ของ Pod ที่ไม่ Ready หลุดไปถาม DNS ภายนอก** (`.web` เป็น TLD จริง) ได้ `127.0.53.53: Connection refused` แทน "ไม่พบชื่อ" — ใช้ชื่อเต็ม `web-1.web.default.svc.cluster.local` เมื่อตรวจ
3. `date` ใน container (nginx/busybox/postgres) เป็น UTC ช้ากว่าเวลาไทย 7 ชม.
4. Pod busybox `sleep` ไม่รับ SIGTERM → ใส่ `terminationGracePeriodSeconds: 1` แล้วตอนลบจะเห็นสถานะ `Error` ชั่วครู่ (ปกติ)
5. `kubectl rollout status` ตอนมี partition จะบอก `partitioned roll out complete: 1 new pods have been updated...` ทั้งที่อัปเดตแค่ตัวเดียว (ถึงเส้นเชือกแล้ว = จบ); ใช้กับ OnDelete ไม่ได้ (`error: rollout status is only available for RollingUpdate strategy type`)
6. `rollout undo` / `patch` / `set image` ทำให้ YAML ในไฟล์ไม่ตรงกับคลัสเตอร์ (Warning last-applied) — apply ไฟล์เดิมอีกครั้งจะเปลี่ยนกลับตามไฟล์ (เช่น LAB 10 ขั้น E memory กลับเป็น 512Mi)
7. scale ลดหรือลบ StatefulSet **PVC ไม่หาย** (default Retain) — ลบเองเมื่อไม่ใช้ (`kubectl delete pvc -l app=web`), ไม่งั้น scale กลับจะได้ข้อมูลเก่าคืน
8. LAB 9: Node ใช้ ~40–50 วิกว่าจะ NotReady และ ~80 วิกว่า Pod จะ Terminating; **ห้าม `kind load` ระหว่าง Node หยุด**; ต้องเอา taint `out-of-service` ออกและ `docker start` ให้ Node Ready ก่อนทำ LAB ถัดไป; ห้าม `kubectl delete pod --force` กับ db
9. LAB 10 ขั้น B: **ต้อง `delete svc som-db` ก่อน apply `k8s/10-db.yaml`** — ถ้าลืม StatefulSet จะถูกสร้าง (ดูจาก dry-run: `statefulset.apps/som-db created (server dry run)` — ไม่ได้ลอง apply จริงใน som-shop) และสร้าง PVC `data-som-db-0` เปล่าแย่งชื่อไปก่อน (ต้องลบ sts + PVC เปล่านั้นก่อนทำขั้น migrate ใหม่); ต้องสร้าง `data-som-db-0` จาก `migrate/` **ก่อน** apply StatefulSet
10. LAB 10 ขั้น B2: หลัง rollout web ไม่กี่วินาทีแรกยังอาจได้คำตอบจาก Pod เก่า (preStop 5 วิ) ไม่ใช่ปัญหา
11. LAB 10 ขั้น F: scale db เป็น 3 **ไม่ใช่การสำรองข้อมูล** — som-db-1/2 เป็น db เปล่า; ต้อง scale กลับ 1 และลบ `data-som-db-1/2` ก่อนทำขั้นถัดไป
12. LAB 10 เสริม: `kubectl exec` เข้า replica ใส่ `-c postgres`; replica ไม่ใช่ failover อัตโนมัติ; `kubectl -n som-shop run dns` จะมี Warning PodSecurity (ns ตั้ง warn: restricted) — เป็นแค่คำเตือน
13. `kubectl delete ns som-shop` ใช้ ~32 วิ
