# SUMMARY: ทดสอบ LAB บท 008 PersistentVolume และ PVC (รันจริง 5 ต.ค. 2569)

- container ทดลอง `k8s-lab-pv008lab-ff12a9` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`, NodePort `30090-30092→30080-30082`) **ยังเปิดอยู่** ตามคำสั่ง (ดู `handoff.md`) ไม่ได้แตะ `k8s-lab` ของผู้เรียน / `deep_vision_5090_vllm` / ไม่ได้ `docker system prune`
- `k8s-up` 53.2 วิ; kubectl v1.37.1 / server v1.37.0 / containerd 2.3.4; `docker cp 008_kubernetes_pv_pvc` ไปที่ `/workspace/` (ไม่ได้ copy บทอื่น จึงยืนยันว่าบทนี้ใช้งานได้ด้วยตัวเอง) แล้วรันทุกคำสั่งจาก `/workspace/008_kubernetes_pv_pvc/02_LAB` (LAB 1–9 `labs/labNN-*`, LAB 10 `som-shop-v4`); ไฟล์ใน container ตรงกับ repo (md5 62 ไฟล์)
- log: `lab00.log` … `lab09.log`, `lab10.log` (ขั้น A–I), `lab10-scale2-round2.log`, `lab10-scale2-round3.log` (ขั้น F ซ้ำ), `lab10-final.log` (คืนสภาพสำหรับ screenshot และทดสอบจาก host); บรรทัด `### hh:mm:ss` = UTC ของเครื่อง agent; `date` ใน shell ของ k8s-lab = เวลาไทย แต่ `date` ใน busybox/postgres = **UTC**
- ทดสอบจาก "เครื่องนักศึกษา" ด้วย host ของ agent: `http://172.18.0.1:30090` (gateway → container 30080 → kind extraPortMappings) ได้หน้าร้าน HTTP 200, footer `Kubernetes LAB 008 · namespace som-shop`, `/api/stats` และ `hit.sh` จาก host `ok=30 err=0`; SSH password `-p 2224` → `hostname` = `k8s-lab`

## ไฟล์ที่สร้าง (`008_kubernetes_pv_pvc/02_LAB/`)

- `labs/` 33 ไฟล์:
  - `lab01-emptydir/pod.yaml`
  - `lab02-hostpath/{00-ns,pod-worker,pod-worker2}.yaml`
  - `lab03-first-pvc/{pvc,pod}.yaml`
  - `lab04-static/{pv,pvc,pvc-too-big,pod}.yaml`
  - `lab05-access/{rwo,rwo-second,rwop,rwop-second,rwx,blk}.yaml`
  - `lab06-lifecycle/{pvc,pod,pvc-reuse}.yaml`
  - `lab07-storageclass/{sc-retain,sc-immediate,sc-expand,pvc-retain,pvc-standard,pvc-expand,pvc-immediate}.yaml`
  - `lab08-node-down/nd.yaml`
  - `lab09-misc/{00-ns-quota,pvc-400,pvc-200,pvc-100,pvc-10,pod-mounts}.yaml`
- `som-shop-v4/`:
  - `app/`: สำเนา `007.../som-shop-v3/app` ไม่รวม node_modules/.next และ**ไม่แก้โค้ด** (page.tsx ยังมี fallback footer `LAB 006` แต่ env ใน YAML ทับเป็น `LAB 008`)
  - `hit.sh`: สำเนา ไม่แก้
  - `k8s/{00-namespace,10-db,20-web}.yaml`: `10-db` = PVC `som-db-data` (standard, RWO, 1Gi) + Deployment Recreate + Service; `20-web` = บท 007 เปลี่ยนแค่ footer `LAB 008` + change-cause `1.2 ร้านจำได้ (db ใช้ PVC)`
  - `k8s-retain/{sc-retain,10-db,pvc-rescue}.yaml`
- คอมเมนต์ภาษาไทยทุกไฟล์; ใช้รหัสผ่าน LAB `meow1234` ตามบทก่อน ไม่มี credential จริงหรือ `.env`
- ยังไม่มี `02_LAB/README.md` (อยู่นอกขอบเขตงานนี้)

## ผลรายข้อ

| LAB | ผล | เวลาจริง | ผลจริงสำคัญ |
|---|---|---|---|
| 0 | ✅ | postgres pull+save+load 17.3 วิ, build 1.2 30.0 วิ, kind load 5.3 วิ | 3 Node Ready; `standard (default)   rancher.io/local-path   Delete   WaitForFirstConsumer   false`; provisioner `local-path-provisioner-…` Running บน `lab-control-plane` image `docker.io/kindest/local-path-provisioner:v20260820-69b56db7`; `nodePathMap` `DEFAULT_PATH_FOR_NON_LISTED_NODES` → `/var/local-path-provisioner`; **ยังไม่มี PV เลย โฟลเดอร์ `/var/local-path-provisioner` จึงยังไม่มีบน Node** (`No such file or directory`) จนมี PV แรก |
| 1 | ✅ (ยืนยันวิธี restart) | – | **`kubectl exec cache-demo -- kill 1` และ `kill -9 1` ไม่ทำให้ container ตาย** (RESTARTS 0 ทั้งคู่); วิธีที่ใช้ได้: `kubectl exec cache-demo -- touch /tmp/stop` ทำให้ loop จบ (exit 1) → `RESTARTS 1 (3s ago)`; หลัง restart `/cache/x.txt` (emptyDir) **อยู่**, `/ram/r.txt` (emptyDir `medium: Memory`) **อยู่**, `/tmp/y.txt` (ไฟล์ใน container) **หาย**; `boot.log` 2 บรรทัด; `logs --previous` = `เจอ /tmp/stop → จบ process …`, lastState `exitCode 1 reason Error`; `df` เห็น `/cache` = ดิสก์ Node `1006.9G`, `/ram` = `tmpfs 16.0M`; ลบ Pod + apply → `/cache` ว่าง มีแค่ boot.log บรรทัดเดียว |
| 2 | ✅ (ยืนยัน PSA) | ลบ ns 10.5 วิ | ข้อความ PSA ทุกครั้งที่ apply Pod: `Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (…), unrestricted capabilities (…), restricted volume types (volume "host" uses restricted volume type "hostPath"), runAsNonRoot != true (…), seccompProfile (…)` (Pod ยังถูกสร้าง เพราะเป็นแค่ warn); `docker exec lab-worker cat /srv/som-hostpath/notes.txt` เห็นไฟล์; Pod บน lab-worker2 เห็นไฟล์**ของตัวเองเท่านั้น**; ลบ Pod แล้วสร้างใหม่ (lab-worker) ไฟล์เดิม + บรรทัดใหม่; **ลบ namespace แล้วไฟล์บน Node ยังอยู่** (ต้อง `docker exec … rm -rf`); โฟลเดอร์ hostPath = `drwxr-xr-x root` |
| 3 | ✅ | Pod Ready ~5 วิ (รวมสร้าง PV ~3 วิ) | `notes   Pending   …   standard`; event `WaitForFirstConsumer … waiting for first consumer to be created before binding`; หลัง Pod: `Bound   pvc-b4fb1995-…   10Mi   RWO   standard`; events `ExternalProvisioning` → `Provisioning` → `ProvisioningSucceeded  Successfully provisioned volume pvc-…`; PV `hostPath.path: /var/local-path-provisioner/pvc-<uid>_default_notes` `type: DirectoryOrCreate`, `nodeAffinity … values: [lab-worker]`, finalizer `kubernetes.io/pv-protection`; **ชื่อ PV = `pvc-` + uid ของ PVC** (ตรงกับ `claimRef.uid`); annotation `volume.kubernetes.io/selected-node: lab-worker`; `/data` = `drwxrwxrwx root`; ลบ Pod สร้างใหม่ ลง Node เดิม log 2 บรรทัด; **ใหม่ใน 1.37: `describe pvc` มี `Conditions: Unused False … PodUsingPVC  A pod is currently referencing this PVC`**; ลบ PVC → PV และโฟลเดอร์หาย |
| 4 | ✅ (ยืนยัน Pod บน lab-worker2) | – | `pv-manual   100Mi   RWO   Retain   Available`; หลัง PVC: `Bound   default/manual-claim` ภายใน 2 วิ (ไม่รอ Pod), PVC `CAPACITY 100Mi` STORAGECLASS ว่าง; `too-big` Pending event `FailedBinding  no persistent volumes available for this claim and no storage class is set`; **Pod `manual-user` (ไม่ได้ปัก Node) ลง `lab-worker2`** ตาม nodeAffinity ของ PV, ไฟล์อยู่ที่ `lab-worker2:/srv/som-manual/manual.txt`; ลบ PVC → PV `Released`; ลบ PV → ไฟล์บน Node ยังอยู่ |
| 5 | ✅ | – | RWO: `rwo-a` และ `rwo-b` Running บน `lab-worker` ทั้งคู่ อ่านไฟล์เดียวกันได้; `dd` 50MB ลง PVC 10Mi สำเร็จ (`52428800 bytes (50.0MB) copied`), `df -h /data` = `1006.9G` (ดิสก์ทั้ง Node); RWOP ตัวที่ 2: `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: …`; RWX: `ProvisioningFailed … failed to provision volume with StorageClass "standard": NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes`; Block: `ProvisioningFailed … rancher.io/local-path does not support block volume provisioning`; **Pod `use-rwx`/`use-blk` Pending โดยไม่มี event ของ Pod เลย** (ต้องดูที่ `describe pvc`); ลบแล้ว PV `Released` ชั่วครู่ก่อนหาย |
| 6 | ✅ | – | `delete pvc --wait=false` → `Terminating`, `Finalizers: [kubernetes.io/pvc-protection]`, `Used By: ledger-pod`; ลบ Pod → PV `Released` 1–2 วิ แล้ว PV และโฟลเดอร์หาย (Delete); `patch pv … Retain` → ลบ PVC → `Released` และ `keepme.txt` ยังอยู่บน Node; **apply `pvc.yaml` ชื่อเดิมซ้ำ → ได้ PV ใหม่ (`pvc-9b83…`) ไม่ใช่ตู้เดิม** (PV ที่ Released ไม่ถูกใช้ซ้ำอัตโนมัติ); ลบ claimRef → `Available`; `sed "s/PV_NAME/$PV/" pvc-reuse.yaml \| kubectl apply -f -` → `Bound` PV เดิม, log `keepme เขียนเมื่อ 05:41:40` (เวลาเดิม); finalizer PV `["kubernetes.io/pv-protection"]`; ลบ PV ที่ Retain → โฟลเดอร์ `pvc-…_default_ledger` ยังอยู่ |
| 7 | ✅ | – | `kubectl get sc`: `standard-retain … Retain WaitForFirstConsumer false`, `local-immediate … Delete Immediate false`, `local-expand … Delete WaitForFirstConsumer true`; `imm` Pending `ProvisioningFailed … failed to provision volume with StorageClass "local-immediate": configuration error, no node was specified`; patch `std`: `Error from server (Forbidden): persistentvolumeclaims "std" is forbidden: only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize` (exit 1); patch `ex` 20Mi → `patched`, 20 วิต่อมา `spec=20Mi status=10Mi`, PV 10Mi, **มี event `ExternalExpanding  waiting for an external controller to expand this PVC`** (แผนบอกว่าไม่มี event); ลดเป็น 5Mi: `The PersistentVolumeClaim "ex" is invalid: spec.resources.requests.storage: Forbidden: field can not be less than status.capacity`; PV ของ `kept` = Retain → `Released` และ**ลบ StorageClass แล้ว PV ยังอยู่** |
| 8 | ✅ | ดูด้านล่าง | Pod `nd-…` บน `lab-worker` (ดึงชื่อ Node ด้วย jsonpath); `docker stop lab-worker` ใช้ **10 วิ** (12:43:21→12:43:31); **NotReady 41 วิหลัง stop เสร็จ** (12:44:12); Pod เก่า `Terminating` + Pod ใหม่ `Pending` **66 วิหลัง stop** (12:44:37 = NotReady + ~25–30 วิ); event (`kubectl get events`) `FailedScheduling … 0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.`; Taints `node.kubernetes.io/unreachable:NoExecute` + `NoSchedule`; **`kubectl describe pod -l app=nd \| grep FailedScheduling` ไม่เจอ** ในรอบนี้ (ใช้ `kubectl get events` หรือ `describe pod <ชื่อ>`); `docker start` → Node Ready ใน 3 วิ, Pod เก่า `Unknown` แล้วหาย, Pod ใหม่ Running ใน **7 วิ** บน lab-worker, `boot.txt` 2 บรรทัด (ข้อมูลเดิมอยู่), event `TaintManagerEviction  Cancelling deletion of Pod`; ไม่ได้ `kind load` ระหว่าง Node หยุด; หลัง LAB 3 Node Ready และ image `postgres`/`som-shop-web:1.2` บน lab-worker ยังอยู่ |
| 9 | ✅ (แก้ไฟล์ 1 จุด) | ลบ ns 10.3 วิ | `p200`: `Error from server (Forbidden): error when creating "pvc-200.yaml": persistentvolumeclaims "p200" is forbidden: exceeded quota: storage, requested: standard.storageclass.storage.k8s.io/requests.storage=200Mi, used: standard.storageclass.storage.k8s.io/requests.storage=400Mi, limited: standard.storageclass.storage.k8s.io/requests.storage=500Mi`; p100 ผ่าน → `describe quota` `persistentvolumeclaims 2/2, requests.storage 500Mi/1Gi, standard…requests.storage 500Mi/500Mi`; `p10`: `exceeded quota: storage, requested: persistentvolumeclaims=1,standard.storageclass.storage.k8s.io/requests.storage=10Mi, used: persistentvolumeclaims=2,…=500Mi, limited: persistentvolumeclaims=2,…=500Mi`; PVC ใน quota ยัง Pending ได้ (quota นับตอนสร้าง); Pod `fsg`: `uid=70 gid=70 groups=70`, `ls -ldn /data /eph` = `drwxrwxrwx 0 0` (**fsGroup ไม่มีผล**), `ls /data/site → page.txt` (ไฟล์เป็น `70 70` บน Node), `touch: /ro/x: Read-only file system`; `fsg-e` 5Mi Bound มี ownerReferences `kind Pod name fsg`; ลบ Pod → `fsg-e` หาย `fsg-data` อยู่; **`kubectl logs fsg` ทันทีหลัง Ready ได้แค่บรรทัดแรก** (รอ 2 วิแล้วครบ) |
| 10 | ✅ (ขั้น F ได้แบบ "ออเดอร์หาย" ทั้ง 3 รอบ) | ดูด้านล่าง | ดูหัวข้อถัดไป |

## LAB 10: ผลแต่ละขั้น (ออเดอร์ก่อน/หลังจาก `/api/stats`)

| ขั้น | ผลจริง | orders |
|---|---|---|
| A | PVC `Pending` ทันทีหลัง apply แล้ว `Bound pvc-6a5a0bc7-… 1Gi RWO standard` หลัง Pod db ลง `lab-worker`; db rollout 8.2 วิ, web 6.0 วิ; POST 3 ครั้ง `{"ok":true,"order_id":1..3,…}` | 0 → **3** |
| B | `delete pod -l app=som-db` แล้ว `rollout status` จบใน ~1 วิ (Pod ใหม่ Ready 1 วิ); **request แรกได้ `db-not-ready [503]`** แล้วตามด้วย 200 ทั้งหมด **โดยไม่ต้อง rollout restart web** | 3 → **3** |
| C | `rollout restart deploy/som-db` (Recreate) 1.2 วิ | **3** |
| D | `delete deploy som-db` → PVC ยัง `Bound`, stats `db-not-ready [503]`; `kubectl apply -f k8s/10-db.yaml` → `persistentvolumeclaim/som-db-data unchanged`, `deployment.apps/som-db created` | **3** |
| E | `docker exec lab-worker ls -ln …/pvc-6a5a0bc7-…_som-shop_som-db-data/` → `drwx------ 19 70 70 pgdata`; ใน pgdata: `PG_VERSION`, `base`, `global`, … ทุกไฟล์ `70 70`; `id` = `uid=70(postgres) gid=70(postgres) groups=70(postgres)`; psql `count 3` | 3 |
| F | scale 2 → ทั้งคู่ `Running 1/1` บน **lab-worker** และ EndpointSlice `ready=true` ทั้งคู่; ตัวที่ 2 log `database system was not properly shut down; automatic recovery in progress` … `redo is not required` … `ready to accept connections`; POST 3 ครั้ง (201) → web เห็น `orders=6` ทุกครั้ง (pool ต่อตัวแรก); psql ใน Pod: ตัวแรก 6 / ตัวที่ 2 3; psql ผ่าน Service: `10.244.2.20\|6` ×2, `10.244.2.21\|3` ×6; scale 1 → ตัวที่เหลือทำงานต่อ ~35 วิ แล้ว log `could not open file "postmaster.pid": No such file or directory` / `performing immediate shutdown because data directory lock file is invalid` → container จบ (`exitCode 0 reason Completed`) → restart → `orders=3` (**ออเดอร์ 3 รายการหาย**) | 3 → 6 → **3** |
| F รอบ 2–3 | ผลเหมือนเดิม: ก่อน scale 1 ตัวเก่า 6 / ตัวใหม่ 3 → ตัวที่เหลือ restart ที่วินาทีที่ :00/:01 ของนาทีถัดไป (postgres ตรวจ lock file ทุก 1 นาที) → **`orders=3` ทุกรอบ**; สถานะ Pod เป็น **`Completed` → `CrashLoopBackOff` ~10 วิ (รอบ 2) และ ~24 วิ (รอบ 3)** แล้ว Running เอง (back-off สะสมจาก RESTARTS); **ไม่เจอ `PANIC: could not locate a valid checkpoint record` ทั้ง 3 รอบ** (เจอเฉพาะ pre-check) | 3 → 6 → **3** ×2 |
| G | ลบ deploy + PVC (0.9 วิ) → PV `Released` แล้วหายใน <4 วิ, โฟลเดอร์ใน `/var/local-path-provisioner/` หาย; apply db ใหม่ → stats `db-not-ready [503]` และหน้าแรก **503**; `rollout restart deploy/som-web` 18.4 วิ | 3 → 503 → **0** |
| H | `standard-retain` สร้างได้; PVC `RWOP standard-retain`, PV `Retain` (ลงบน **lab-worker2** รอบนี้); restart web + POST 2 | **2**; scale 2 → Pod ที่ 2 `Pending` `… 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. …`, `som-db 1/2`; scale 1 → **2** |
| H2 | ลบ deploy+PVC → `Released` (stats 503) → remove claimRef → `Available` → `sed … pvc-rescue.yaml \| kubectl apply -f -` + **`kubectl apply -f k8s-retain/10-db.yaml -l app=som-db`** → `Bound` PV เดิม → **orders=2 ทันทีไม่ต้อง restart web** | **2** |
| I | `kubectl delete ns som-shop` 32.6 วิ → PV Retain ยัง `Released` + โฟลเดอร์ยังอยู่ → `delete pv` + `docker exec lab-worker2 rm -rf …` + `delete sc standard-retain` | – |
| คืนสภาพ | `kubectl apply -f k8s/` → POST 4 ครั้ง (สินค้า 1,2,3,1) | **4** |

## จุดที่แผนสั่งให้ยืนยัน

1. **LAB 1 วิธี restart container:** `kill 1` และ `kill -9 1` ไม่ได้ผล วิธีที่ใช้ได้คือไฟล์ trigger `/tmp/stop` (อยู่ในตัว container จึงหายเองหลัง restart ไม่วนซ้ำ) ✅
2. **LAB 2 ข้อความ PSA** (เต็มในตารางด้านบน) ✅ และ Pod ที่ใช้ static PV ลง lab-worker2 ✅ (LAB 4)
3. **ขั้น F:** รันหลังขั้น E และกู้ด้วยขั้น G ✅ ทั้ง 3 รอบได้แบบ "ออเดอร์หาย + restart (+ CrashLoopBackOff ชั่วครู่)"; แบบ PANIC ไม่เกิดในรอบนี้ README ต้องเขียนให้ครอบคลุมทั้งสองแบบ
4. ภาพ needs_test: ดูหัวข้อ "ป้ายภาพ" ด้านล่าง
5. **เวลา Node ล่ม:** NotReady 41 วิหลัง `docker stop` เสร็จ (stop ใช้ 10 วิ เท่ากับ ~51 วิหลังกด Enter ตรงกับบทเรียนก่อน "~45–50 วิ"); Pending 66 วิหลัง stop เสร็จ; กลับมา Running 7 วิหลัง start

## การเปลี่ยนแปลงจากแผน

1. **ไม่มี `split-contract.md` และ `logs/005_rs_deploy_svc/precheck.md`** ใน repo จึงใช้ `plan.md` + `scratch/` + โครงของบท 007 แทน
2. **LAB 0 build แค่ `som-shop-web:1.2`** (แผนบอก 1.2/1.3): บทนี้ไม่ได้ใช้ 1.3 เลย (L01 caption ต้องแก้)
3. **LAB 1 ใช้ `touch /tmp/stop`** แทน `kill 1` และเพิ่ม volume `ram` (`medium: Memory`, `sizeLimit: 16Mi`) ให้เห็นตามทฤษฎีข้อ 2
4. **LAB 5 ไฟล์เปลี่ยนเป็น `{rwo,rwo-second,rwop,rwop-second,rwx,blk}.yaml`** (แผน `{rwx,rwop,blk,writer2}`): ทำให้ LAB 5 ไม่ต้องพึ่ง PVC `notes` จาก LAB 3 (LAB 3 ลบทิ้งตอนจบ)
5. **LAB 6 ใช้ PVC `ledger` / Pod `ledger-pod` / ไฟล์ `keepme.txt`**; `pvc-reuse.yaml` ใช้ชื่อเดิม `ledger` + `volumeName: PV_NAME` (แทนด้วย `sed`) ให้ใช้ `pod.yaml` เดิมได้; เพิ่มฉาก "apply PVC ชื่อเดิมได้ PV ใหม่"
6. **LAB 7 แยก PVC เป็น `pvc-retain` (kept), `pvc-standard` (std), `pvc-expand` (ex), `pvc-immediate` (imm)** แต่ละไฟล์มี Pod `<pvc>-user` ยกเว้น imm
7. **LAB 9 `pod-mounts.yaml` มี PVC `fsg-data` ของตัวเองใน namespace default** (ephemeral PVC นับใน quota จึงไม่วางใน `quota-lab`); subPath ใช้โฟลเดอร์ `site`; ไฟล์ PVC ชื่อ `pvc-{400,200,100,10}.yaml` ชื่อ PVC `p400…p10`; **แก้หลังรันรอบแรก:** เอา `df -h /eph` ออก (แสดง `Mounted on /data` เพราะอยู่ดิสก์เดียวกัน ชวนสับสน) และเปลี่ยนข้อความ subPath เป็น `ls /data/site → page.txt`
8. **LAB 10 H2:** apply `k8s-retain/10-db.yaml` ทั้งไฟล์หลัง `pvc-rescue.yaml` ได้ `The PersistentVolumeClaim "som-db-data" is invalid: spec: Forbidden: spec is immutable after creation except resources.requests and volumeAttributesClassName for bound claims` (diff `VolumeName: "pvc-…" → ""`, exit 1 แม้ Deployment จะถูกสร้าง) → เปลี่ยนเป็น **`kubectl apply -f k8s-retain/10-db.yaml -l app=som-db`** (เลือกเฉพาะ Deployment) และเขียนวิธีไว้ในคอมเมนต์ `pvc-rescue.yaml` แล้ว (รันซ้ำผ่าน exit 0)
9. **LAB 10 ขั้น A ใช้ `kubectl apply -f k8s/`** ได้ (โฟลเดอร์ `k8s/` มีแต่ manifest จริง); `k8s-retain/` **ห้าม** apply ทั้งโฟลเดอร์ เพราะมี `pvc-rescue.yaml` ที่ยังเป็น `PV_NAME`
10. ใส่ `terminationGracePeriodSeconds: 1` ให้ Pod busybox ทุกตัว (sh/sleep ไม่รับ SIGTERM ถ้าไม่ใส่ ลบ Pod ต้องรอ 30 วิ)

## ป้าย/ข้อความ/ฉากในภาพ storyboard ที่ไม่ตรงผลจริง (และค่าที่ควรใช้แทน)

| ภาพ | ส่วน | ปัจจุบัน | ควรเป็น |
|---|---|---|---|
| L01 | caption | "โหลด postgres:17.11-alpine ด้วย image-archive และ som-shop-web:1.2/1.3" | "… และ som-shop-web:1.2" (บทนี้ไม่ใช้ 1.3) |
| L02 | caption/scene | "kill container ไฟล์ยังอยู่ (RESTARTS 1)" | "touch /tmp/stop ให้ container จบเอง → RESTARTS 1 ไฟล์ใน emptyDir ยังอยู่ (ไฟล์ใน /tmp หาย)" (`kill 1` ไม่ได้ผลจริง); ป้าย `RESTARTS 1: ยังอยู่` ใช้ได้ |
| L08 | caption | "…, ขยาย PVC ถูกปฏิเสธ —" | ตัดส่วนนี้ออก (การขยายอยู่ใน LAB 7/L11 ไม่ใช่ LAB 5) |
| L10 | caption | "Released ไฟล์ k.txt ยังอยู่" | "Released ไฟล์ keepme.txt ยังอยู่" |
| L11 | caption | (ไม่ได้ระบุ event) | ถ้าจะใส่ข้อความ: local-expand มี event `ExternalExpanding: waiting for an external controller to expand this PVC` (ไม่ใช่ "ไม่มี event"); ป้ายเดิมใช้ได้ |
| L12 | caption | "NotReady ~40 วิ" | "NotReady ~40–50 วิ (หลังกด docker stop ~50 วิ) → Pod ใหม่ Pending ~65–70 วิ"; ป้าย `docker stop lab-worker` ตรงกับรอบนี้ แต่ Node จริงขึ้นกับว่า Pod ลงที่ไหน (ใช้ `$N`) |
| L16 | caption | "orders=3 ทันที" | "orders=3 (request แรกหลังลบ Pod อาจได้ 503 db-not-ready 1 ครั้ง)"; ป้ายใช้ได้ |
| L20 | label/caption | `PANIC: could not locate a valid checkpoint record` + "พังเป็น CrashLoopBackOff" | รอบนี้ 3/3 รอบ = **ออเดอร์หาย 6→3 + log `performing immediate shutdown because data directory lock file is invalid` + CrashLoopBackOff ชั่วครู่** แล้วกลับมาเอง; PANIC เจอเฉพาะ pre-check แนะนำเปลี่ยนป้าย PANIC เป็น `lock file is invalid` หรือ `orders 6 → 3` หรือเขียนว่า "หรือ (บางครั้ง) PANIC" |
| T27 | label | `Used By: writer` | LAB ที่สาธิต finalizer (LAB 6) ได้ `Used By: ledger-pod` (ถ้าอยากให้ตรงกับ LAB); ถ้าเป็นภาพแนวคิดเฉย ๆ คงไว้ได้ |
| T29 | label | `subPath: pgdata` | som-shop ใช้ PGDATA เป็นโฟลเดอร์ย่อยผ่าน env **ไม่ได้ใช้ subPath**; LAB 9 ใช้ `subPath: site` → ใช้ `subPath: site` หรือเปลี่ยนเป็นตัวอย่างกลาง ๆ |
| T35 | label | `PANIC` | เหมือน L20: ผลที่พบบ่อยในรอบนี้ = ออเดอร์หาย; แนะนำ "ออเดอร์หาย / PANIC" |
| T18/T31/L05/L18 | nodeAffinity/Node | `lab-worker` | ตรงกับรอบนี้สำหรับ db ขั้น A–G (ขั้น H ลง lab-worker2) แต่ Node สุ่มได้ ควรเลี่ยงการยืนยันว่าต้องเป็น lab-worker ใน caption |

ภาพอื่นที่ needs_test (T14, T17, T21, T22, T24, T26, T28, T30, T32, T33, T36, L03–L07, L09, L13, L15, L17, L19, L21–L23): ตรงกับผลจริงทุกป้าย (T36 "RWOP + RollingUpdate = ค้าง" ไม่ได้รันซ้ำในรอบนี้ อ้างจาก pre-check)

## ข้อควรระวังสำหรับนักศึกษา

- **ห้าม `kubectl apply -f k8s-retain/`** (ทั้งโฟลเดอร์) เพราะ `pvc-rescue.yaml` มี `PV_NAME` อยู่; ตอนกู้ให้ใช้ `-l app=som-db` ตามคอมเมนต์ในไฟล์
- ขั้น F (scale db 2) **ทำให้ข้อมูลเสียจริง** ผลแต่ละเครื่องต่างกัน (ออเดอร์หาย / CrashLoopBackOff ชั่วครู่ / PANIC ค้าง) ต้องรอ **~1 นาที** หลัง scale 1 จึงเห็นผล (postgres ตรวจ lock file ทุกนาที) ถ้าเจอ PANIC + CrashLoopBackOff ไม่หาย ให้ไปขั้น G ทันที
- `kill 1` ใน busybox ไม่ทำให้ container restart; ใช้ `touch /tmp/stop` ตาม LAB 1
- `date` ใน Pod busybox/log postgres เป็น **UTC** (ช้ากว่าเวลาไทย 7 ชม.)
- `kubectl logs` ทันทีหลัง `wait Ready` อาจยังไม่ครบ ให้รอ 1–2 วิ
- ลบ namespace / PVC / PV ที่ Retain แล้ว **โฟลเดอร์บน Node ยังอยู่** (hostPath, static PV, PV Retain) ต้อง `docker exec <node> rm -rf …` เอง
- PVC ชื่อเดิมไม่ได้ตู้เดิมกลับมา ต้องลบ claimRef แล้วใช้ `volumeName`
- LAB 8: ใช้ Node ที่ Pod อยู่จริง (`N=$(kubectl get pod -l app=nd -o jsonpath='{.items[0].spec.nodeName}')`), อย่า `kind load` ระหว่าง Node หยุด, `docker start $N` ก่อนไป LAB ถัดไป และตรวจว่า 3 Node `Ready`; ถ้า `describe pod -l` ไม่เห็น FailedScheduling ให้ใช้ `kubectl get events --sort-by=.lastTimestamp`
- `df`/ขนาด PVC ใน local-path เป็นแค่ตัวเลข (ดิสก์ของเครื่องแต่ละคนต่างกัน รอบนี้ `1006.9G`)
- หลังลบ Pod db (ขั้น B/D) request แรกอาจได้ 503 เพราะ connection pool เก่าหลุด แล้วกลับมาปกติเอง
