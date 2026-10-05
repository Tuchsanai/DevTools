# แผนบทเรียน 009 — Kubernetes StatefulSet (หัวหน้ากะที่ตั้งเลขบูธและแจกตู้เซฟประจำตัว)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB) — pre-check รันจริงแล้ว 5 ต.ค. 2569 ใน container ทดลอง `k8s-lab-pvsts-142c4b` (ใช้ร่วมกับบท 008, ลบแล้ว)
> Storyboard: `logs/009_statefulset/images.json` (Theory 38 ภาพ T01–T38, LAB 24 ภาพ L01–L24, needs_test 43 ภาพ) สร้างจาก `logs/009_statefulset/build_images.py` + `imgcommon.py` (สำเนาเดียวกับ 008) → `images.json`, `009_kubernetes_statefulset/01_Theory/images/imagegen-prompts.md`, `009_kubernetes_statefulset/02_LAB/images/imagegen-prompts.md`
> ภาพตัวละครอ้างอิง: `009_kubernetes_statefulset/01_Theory/images/00-character-som.png` · สร้างภาพด้วย `logs/009_statefulset/gen_images.sh`
> manifest ทดลอง: `logs/009_statefulset/scratch/t/` (`sts.yaml`, `sts-tol.yaml`, `par.yaml`, `bad.yaml`, log `s1–s4.log`), `logs/009_statefulset/scratch/shop/` (`10-db-008.yaml`, `10-db.yaml`, `20-web-sts.yaml`, `migrate-pvc.yaml`, `replica.yaml`, log `run.log`, `rep.log`)

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่าน 001–008 (รวม PV/PVC/StorageClass, Retain/rescue, RWOP, Node ล่มกับ local-path, ผลเสียหายของ db replicas 2 บน Deployment)
- โฟลเดอร์ LAB: `docker cp 009_kubernetes_statefulset k8s-lab:/workspace/` → `cd /workspace/009_kubernetes_statefulset/02_LAB` (LAB1–9 `cd labs/labNN-*`, LAB10 `cd som-shop-v5`)
- **ใช้ได้ใน LAB:** ทุกอย่างของ 001–008 + StatefulSet, headless Service, volumeClaimTemplates, partition/OnDelete, taint `out-of-service`
- **ยังไม่ใช้:** ConfigMap/Secret (รหัสผ่านยังอยู่ใน YAML — ปิดบทปูทาง; LAB เสริม replication แก้ `pg_hba.conf` ด้วย `kubectl exec` แทน ConfigMap), Ingress, HPA, PodDisruptionBudget/anti-affinity (แนวคิดในแนวปฏิบัติ), Operator (แนวคิด)
- อุปมาใหม่: **StatefulSet = หุ่นยนต์หัวหน้ากะสีม่วง-กรมท่ามีเครื่องจ่ายบัตรคิวตัวเลข** เปิดบูธทีละบูธตามลำดับ ป้าย -0/-1/-2; **แต่ละบูธมีตู้เซฟประจำตัวเลขเดียวกัน**; volumeClaimTemplates = สมุดใบเบิกพิมพ์ไว้แล้วฉีกทีละใบ; **headless Service = สมุดรายชื่อบนแท่นอ่าน (ไม่มีไฟประภาคาร) บอกที่อยู่รายบูธตรง ๆ**; partition = เชือกกั้นแถวบูธ; streaming replication = สายพานส่งหน้าสมุดจากบูธ -0 ไปบูธสำเนา (อ่านอย่างเดียว); Node ล่ม = เรือติดหมอก

## 1. สารบัญทฤษฎี (01_Theory/README.md) — ภาพ T01–T38

| # | หัวข้อ | เนื้อหาหลัก | ภาพ |
|---|-------|------------|-----|
| 1 | บทนำ | ต่อท้ายบท 008: db จำได้แต่มีได้ตัวเดียว; Deployment = template เดียว → `claimName` เดียว → replicas 2 เสียหาย (ผล 008); อุปมาใหม่ | T01–T03 |
| 2 | ทำไม Deployment ไม่พอ | stateless vs stateful (ชามกระดาษ vs ชามเซรามิกสลักชื่อ); ชื่อ Pod สุ่ม `som-db-7b786655f5-9hf7p`, RollingUpdate ทำให้มี 2 ตัวพร้อมกัน, ไม่มี identity/ลำดับ/PVC ต่อ Pod | T04–T05 |
| 3 | คุณสมบัติ StatefulSet | 3 การรับประกัน (ชื่อ, DNS, storage); manifest (`serviceName`, `replicas`, `selector`, `template`, `volumeClaimTemplates`, `updateStrategy`, `podManagementPolicy`, `minReadySeconds`, `persistentVolumeClaimRetentionPolicy`, `ordinals.start` แนวคิด); ชื่อ `<sts>-<ordinal>`, hostname = ชื่อ Pod, label อัตโนมัติ `statefulset.kubernetes.io/pod-name`, `apps.kubernetes.io/pod-index`, `controller-revision-hash`; ลบ Pod → ชื่อเดิม UID/IP ใหม่ PVC เดิม | T06–T09 |
| 4 | headless Service + DNS | `clusterIP: None` vs ClusterIP; `<pod>.<svc>.<ns>.svc.cluster.local`; nslookup service ได้ IP ทุก Pod ที่ Ready (ไม่ Ready ไม่อยู่ — `publishNotReadyAddresses` แนวคิด); `serviceName` ต้องตรงกับ headless Service ที่สร้างเอง; เปลี่ยน Service เดิมจาก ClusterIP เป็น headless ไม่ได้ (clusterIP immutable) ต้องลบสร้างใหม่ | T10–T13 |
| 5 | volumeClaimTemplates | PVC `<template>-<sts>-<ordinal>` (`data-som-db-0`), ได้ label ตาม selector ของ sts; PVC ติดตามชื่อ Pod; ไม่ถูกลบเมื่อ scale down/ลบ sts (default `whenDeleted: Retain, whenScaled: Retain`); ตั้ง `Delete` → PVC มี `ownerReferences` ถึง StatefulSet และหายตาม; ต่างจาก PV reclaimPolicy (คนละชั้น: PVC ↔ PV) | T14–T17 |
| 6 | ลำดับ: podManagementPolicy | OrderedReady (default) สร้าง 0→1→2 รอ Ready, Pod ก่อนหน้าไม่ Ready → ค้าง; scale down ลบเลขมากก่อน; Parallel สร้าง/ลบพร้อมกัน (ไม่มีผลกับลำดับของ update) | T18–T20 |
| 7 | updateStrategy | RollingUpdate (default, `maxUnavailable: 1`, `partition: 0`) อัปเดต 2→1→0; partition = canary (อัปเดตเฉพาะ ordinal ≥ partition); ControllerRevision, `currentRevision`/`updateRevision`, `kubectl rollout history/undo sts`; OnDelete; `minReadySeconds`; rollout ที่ Pod พังต้องแก้ template + ลบ Pod ที่ค้างเอง (แนวคิด "forced rollback") | T21–T25 |
| 8 | replicas ≠ replication | scale 3 = 3 db ข้อมูลแยก (`relation "orders" does not exist`); ต้องทำ replication ระดับแอป (postgres streaming: `pg_basebackup -R`, standby อ่านอย่างเดียว); Operator สำหรับ failover/backup (แนวคิด) | T26–T28 |
| 9 | StatefulSet กับ Node ล่ม | Pod ค้าง Terminating ไม่สร้างแทน (at most one); force delete อันตราย (สองตัวชื่อเดียว เขียนพร้อมกัน); taint `node.kubernetes.io/out-of-service=nodeshutdown:NoExecute` เมื่อยืนยันว่า Node ดับจริง → Pod ถูกลบ แต่ local-path PV ผูก Node → Pending จน Node กลับ | T29–T31 |
| 10 | เทียบและแนวปฏิบัติ | Deployment vs StatefulSet vs DaemonSet (แนวคิด); web ต่อ db ด้วย `som-db-0.som-db` (headless `som-db` ตอบทุก IP); ย้าย PVC เดิมเข้ามาโดยตั้งชื่อ `data-som-db-0` ล่วงหน้า; แนวปฏิบัติ (probe, resources, Retain, backup นอกคลัสเตอร์, ไม่ force delete, กระจาย Node, Operator) | T32–T35 |
| 11 | สรุป | ตารางสรุป, cheatsheet, ปูทาง ConfigMap/Secret, Ingress, HPA | T36–T38 |

## 2. ตาราง LAB (02_LAB/README.md) — ภาพ L01–L24

| LAB | ชื่อ | เป้าหมาย | ไฟล์ (02_LAB/) | คำสั่งหลัก | ผลที่ต้องเห็น (pre-check) | สิ่งที่ต้องยืนยัน |
|-----|------|---------|---------------|-----------|--------------------------|------------------|
| 0 | เตรียม | คลัสเตอร์สะอาด + image | – | `kubectl get nodes,sc,pv`; โหลด postgres (`docker save --platform linux/amd64` + `kind load image-archive`); build/load `som-shop-web:1.2` | `kubectl get pv` → `No resources found` (ถ้ามี PV Retain ค้างจาก 008 ให้ลบ + ลบโฟลเดอร์บน Node) | – |
| 1 | Deployment vs StatefulSet | เห็นชื่อสุ่ม vs ชื่อคงที่ | `labs/lab01-compare/{web-deploy,web-sts}.yaml` | apply ทั้งคู่ → `get pod` → ลบ Pod หนึ่งตัวของแต่ละแบบ | sts: `web-0/1/2`, ลบ `web-1` ได้ `web-1` คืน; hostname = ชื่อ Pod | ไฟล์ Deployment เทียบ (ยังไม่ได้รันคู่กัน — พฤติกรรมรู้จากบท 007) |
| 2 | headless Service + DNS | DNS รายตัว | `labs/lab02-headless/{svc-headless,sts}.yaml` + Pod `dns` (busybox) | `kubectl run dns --image=busybox:1.36 --rm -it --restart=Never -- sh` → `nslookup web`, `nslookup web-0.web.default.svc.cluster.local`, `wget -qO- web-1.web` | `nslookup web` ได้ 3 Address; รายตัวได้ IP เดียว; `wget web-1.web` → `first-born web-1 …` | Pod ที่ไม่ Ready ไม่อยู่ใน `nslookup web` และ `web-N.web` resolve ไม่ได้ (ยังไม่ได้รัน); ใช้ `-it` แทน `-i` (pre-check `-i --rm` เจอ warning attach) |
| 3 | volumeClaimTemplates | PVC ต่อ Pod | `labs/lab03-vct/sts.yaml` (nginx เขียน `first-born $(hostname) $(date +%T)` ครั้งแรกเท่านั้น) | `get pvc`; `kubectl exec web-N -- cat /usr/share/nginx/html/index.html`; ลบ Pod | `www-web-0/1/2` Bound 10Mi RWO standard สร้างห่างกัน ~11 วิ (ตามลำดับ); ลบ Pod แล้วข้อความเดิม; PVC มี label `app=web` | – |
| 4 | ลำดับ | OrderedReady/Parallel | `labs/lab04-order/{bad,par}.yaml` | apply `bad` (readiness `cat /tmp/ready`) → `kubectl exec bad-0 -- touch /tmp/ready`; apply `par`; `scale sts web --replicas=1` + ดูทุก 2 วิ | `bad-0 0/1 Running` 15 วิ ไม่มี bad-1 → touch แล้ว `bad-1` เกิด; `par-0/1/2 Pending` พร้อมกันใน 4 วิ; scale 3→1: `web-2 Terminating` ก่อน แล้วเหลือ `web-0` | – |
| 5 | scale + retention | PVC ค้าง/หายตาม policy | `labs/lab05-retention/par.yaml` (`whenScaled: Delete, whenDeleted: Delete`) | `scale sts web --replicas=1` → `get pvc` → scale 3 → อ่านไฟล์; `get pvc www-par-0 -o jsonpath='{.metadata.ownerReferences}'`; scale/delete par | web: PVC 3 ใบยัง Bound, `web-2` กลับมาอ่าน `first-born web-2` เดิม; par: PVC มี ownerReferences `kind: StatefulSet name: par`; scale 3→1 เหลือ `www-par-0`; ลบ sts → PVC หมด, PV 0 | – |
| 6 | RollingUpdate + partition | canary ทีละขั้น | `labs/lab06-update/sts.yaml` | `kubectl patch sts web -p '{"spec":{"updateStrategy":{"type":"RollingUpdate","rollingUpdate":{"partition":2}}}}'`; `kubectl set image sts/web nginx=nginx:1.28-alpine`; `get sts web -o jsonpath='{.status.currentRevision} {.status.updateRevision} {.status.updatedReplicas}'`; partition 0; `rollout history sts/web` | default `{"rollingUpdate":{"maxUnavailable":1,"partition":0},"type":"RollingUpdate"}`; partition 2 → เฉพาะ `web-2 nginx:1.28-alpine`, `updated=1`; partition 0 → web-1 (~6 วิ) แล้ว web-0; `rollout status` = `partitioned roll out complete: 3 new pods have been updated...`; history REVISION 1, 2 | `kubectl rollout undo sts/web` (ยังไม่ได้รัน) |
| 7 | OnDelete + minReadySeconds | คุมจังหวะเอง | `labs/lab07-ondelete/` | `kubectl patch sts web --type merge -p '{"spec":{"updateStrategy":{"type":"OnDelete","rollingUpdate":null}}}'`; set image 1.27; ลบ web-1 | ไม่มี Pod เปลี่ยนเอง; ลบ web-1 → `web-1 nginx:1.27-alpine` ตัวเดียว ไฟล์เดิม | **minReadySeconds ยังไม่ได้รัน** (ตั้ง 10 แล้วดูช่วงห่างการ update) |
| 8 | ลบ sts แล้ว apply ใหม่ | PVC รอเจ้าของ | `labs/lab03-vct/sts.yaml` | `kubectl delete sts web` → `get pod,pvc` → apply | Pod หมดใน 10 วิ, PVC 3 ใบ Bound; apply ใหม่ → อ่าน `first-born web-0/1/2` เวลาเดิมครบ | `--cascade=orphan` (ทางเลือก ยังไม่ได้รัน) |
| 9 | Node ล่ม | at-most-one + out-of-service | `labs/lab09-node-down/sts-tol.yaml` (tolerations 30 วิ) | `N=$(kubectl get pod web-1 -o jsonpath='{.spec.nodeName}'); docker stop $N`; ดู 2–3 นาที; `kubectl taint node $N node.kubernetes.io/out-of-service=nodeshutdown:NoExecute`; `describe pod web-1`; เอา taint ออก + `docker start $N` | NotReady ~40–60 วิ; `web-1` เป็น `Terminating` ~78 วิหลัง stop (READY ยังแสดง `1/1`, condition Ready=False) และค้างต่อ ≥ 2.5 นาที ไม่มี web-1 ใหม่; ใส่ taint → ภายใน ~10–20 วิ web-1 ถูกลบ + สร้างใหม่ `Pending` `0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s).`; start Node → web-1 Running บน Node เดิม อ่าน `first-born web-1` เดิม | ห้าม force delete กับ db (สาธิตเฉพาะคำอธิบาย) |
| 10 | **ร้านน้องส้มแบบโปรดักชัน** | db เป็น StatefulSet (ข้อ 3) | `som-shop-v5/` | ข้อ 3 | ข้อ 3 | ข้อ 3 |

ภาพ LAB: L01 (LAB0), L02 (LAB1), L03 (LAB2), L04 (LAB3), L05–L06 (LAB4), L07 (LAB5), L08 (LAB6), L09 (LAB7), L10 (LAB8), L11–L12 (LAB9), L13–L24 (LAB10 = 12 ภาพ รวม LAB เสริม 2 ภาพ)

## 3. LAB10 "ร้านน้องส้มแบบโปรดักชัน: db เป็น StatefulSet" (som-shop-v5)

**ไฟล์:** คัดลอก `som-shop-v4/{app,hit.sh}` ของบท 008 (แอป 1.2 เดิม ไม่ต้องทำรุ่นใหม่)
- `k8s-008/` = สภาพท้ายบท 008 (`00-namespace.yaml`, `10-db.yaml` Deployment + PVC `som-db-data` standard RWO, `20-web.yaml`) — ให้บทนี้เริ่มเองได้โดยไม่ต้องมีของค้างจาก 008
- `k8s/10-db.yaml` = headless Service `som-db` (`clusterIP: None`, port `postgres` 5432) + StatefulSet `som-db` (`serviceName: som-db`, replicas 1, template เดิมของ db, `volumeClaimTemplates: data` standard RWO 1Gi, mount `/var/lib/postgresql/data`, PGDATA `…/pgdata`) — ไม่มี `strategy` (ใช้ `updateStrategy` default)
- `k8s/20-web.yaml` = เดิม แต่ `DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop` (web, db-seed) และ `wait-for-db` ใช้ `-h som-db-0.som-db`
- `migrate/data-som-db-0-pvc.yaml` (`name: data-som-db-0`, label `app: som-db`, `storageClassName: standard`, `volumeName: <PV>`, 1Gi RWO)
- `extra/replica.yaml` = StatefulSet `som-db-replica` (`serviceName: som-db`, init `clone-from-primary`: ถ้า `$PGDATA/PG_VERSION` ยังไม่มี → `pg_basebackup -h som-db-0.som-db -U som -D $PGDATA -R -X stream -P`, env `PGPASSWORD`, uid 70) + container postgres เดิม + vct `data`

**ขั้นตอน (ผล pre-check จริง):**

| ขั้น | ทำอะไร | ผล pre-check |
|-----|--------|-------------|
| A | `kubectl apply -f k8s-008/` → สั่งซื้อ 3 → `/api/stats` | `orders=3 products=6` |
| B | ย้ายตู้เซฟ: `PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}')`; `kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'`; `delete deploy som-db`; `delete svc som-db` (ClusterIP → headless ต้องลบก่อน); `delete pvc som-db-data` → `Released`; `patch pv … remove /spec/claimRef` → `Available`; `sed "s/PVNAME/$PV/" migrate/… \| kubectl apply -f -`; `kubectl apply -f k8s/10-db.yaml` | `som-db-0 1/1 Running` ภายใน ~1 วิ, PVC `data-som-db-0 Bound` PV เดิม (`som-shop/data-som-db-0`) |
| B2 | `kubectl apply -f k8s/20-web.yaml` → rollout → stats; คืน policy `Delete` (หรือคง Retain เป็นแนวปฏิบัติ — README เลือกอย่างใดอย่างหนึ่งแล้ว cleanup ให้ตรง) | `orders=3` ข้อมูลย้ายมาครบ |
| C | `kubectl -n som-shop delete pod som-db-0` | ชื่อเดิม `som-db-0`, UID ใหม่, IP ใหม่ (`10.244.1.58 → 10.244.1.61`), `claimName data-som-db-0`; `orders=3` |
| D | rolling update: `kubectl -n som-shop patch sts som-db --type json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"768Mi"}]'` → `rollout status/history` → สั่งซื้อ 1 | REVISION 1, 2; `orders=4` |
| E | `kubectl -n som-shop delete sts som-db` → `get pvc` → apply `k8s/10-db.yaml` | PVC `data-som-db-0` Bound ตลอด → `orders=4` |
| F | `kubectl -n som-shop scale sts som-db --replicas=3` → `get pod,pvc -o wide` → psql ทีละตัว → nslookup `som-db` | PVC `data-som-db-1/2` ใหม่ (som-db-1/2 ลง lab-worker2, som-db-0 lab-worker); som-db-0 `4`, som-db-1/2 `ERROR:  relation "orders" does not exist`; `nslookup som-db` ได้ 3 Address; `/api/stats` ยัง `orders=4` (web ชี้ som-db-0) |
| G | scale 1 → `get pod,pvc` → ลบ `data-som-db-1/2` เอง | เหลือ som-db-0, PVC 1/2 ยัง Bound |
| H (เสริม) | `kubectl -n som-shop exec som-db-0 -- sh -c 'echo "host replication all all scram-sha-256" >> $PGDATA/pg_hba.conf; psql -U som -d catshop -c "select pg_reload_conf()"'` → apply `extra/replica.yaml` → logs init → psql | init `30955/30955 kB (100%), 1/1 tablespace` + `cloned`; replica `pg_is_in_recovery = t`, orders เท่า primary; สั่งซื้อใหม่ replica เห็นทันที (5=5); `pg_stat_replication` = `<ip>|streaming|async`; INSERT บน replica → `ERROR:  cannot execute INSERT in a read-only transaction`; ลบ replica → init `already-cloned`; ลบ som-db-0 → replica ต่อกลับเอง (repl=1, 6=6) |
| I | สรุป + cleanup: `kubectl delete ns som-shop` (PVC ในนี้หาย → PV Delete หาย; ถ้าคง Retain ต้องลบ PV + โฟลเดอร์บน Node เอง) | – |

**ข้อควรรู้จาก pre-check:** `kubectl exec` เข้า replica ต้องใส่ `-c postgres` (มี init container จะขึ้น `Defaulted container "postgres" out of: postgres, clone-from-primary (init)`); `pg_hba.conf` อยู่ใน PGDATA บน PVC จึงคงอยู่ข้าม restart; replica ไม่ใช่ failover อัตโนมัติ (ถ้า som-db-0 ตาย web ยังเขียนไม่ได้)

**ปิดบท:** รหัสผ่าน `meow1234` อยู่ใน YAML ทุกไฟล์ → ConfigMap/Secret; เปิดร้านผ่าน NodePort 30080 → Ingress; web ต้อง `scale` เอง → HPA (ต้องมี metrics-server)

## 4. ผล pre-check ที่ยืนยันแล้ว (5 ต.ค. 2569)

- container `k8s-lab-pvsts-142c4b` (image ID `8108a1bc7901`, SSH 2224, NodePort 30090–30092) — **ลบแล้ว**; ไม่ได้แตะ `k8s-lab` ของผู้เรียน / `deep_vision_5090_vllm`
- StatefulSet default ใน v1.37: `podManagementPolicy: OrderedReady`, `updateStrategy {"rollingUpdate":{"maxUnavailable":1,"partition":0},"type":"RollingUpdate"}`, `persistentVolumeClaimRetentionPolicy {whenDeleted: Retain, whenScaled: Retain}`
- label บน Pod: `apps.kubernetes.io/pod-index`, `controller-revision-hash`, `statefulset.kubernetes.io/pod-name`; hostname = ชื่อ Pod
- ลำดับสร้าง: AGE 45/34/23 วิ (ห่าง ~11 วิ เพราะรอ Ready + pull image); scale down ลบ -2 ก่อน; OrderedReady ค้างเมื่อ -0 ไม่ Ready; Parallel สร้างพร้อมกัน
- DNS headless: `nslookup web` 3 Address, `web-0.web.default.svc.cluster.local` IP เดียว, `wget web-1.web` ได้
- partition 2 → `currentRevision web-669f84ffcf`, `updateRevision web-74ccccbb4d`, `updated=1`; ลำดับ 2→1→0; OnDelete ใช้ได้
- `nginx:1.27-alpine` และ `nginx:1.28-alpine` Node ดึงได้; postgres ใน Docker Hub ล่าสุดของสาย 17 = `17.11-alpine` (มี `17.11-alpine3.24`, `17.10-alpine`) → rolling update ของ db ใช้การเปลี่ยน resources แทนเปลี่ยน tag
- Node ล่ม: StatefulSet ไม่สร้าง Pod แทน (ค้าง Terminating), out-of-service taint ลบ Pod ให้ แต่ PV local-path → Pending; Node กลับ → ข้อมูลเดิม
- ร้านน้องส้ม: ย้าย PVC เดิมเข้า StatefulSet สำเร็จ, ทุกขั้น A–H ผ่านตามตาราง

## 5. จุดที่ต้องยืนยันตอนเขียน/รัน LAB จริง

1. LAB2: Pod ไม่ Ready หายจาก DNS headless (ยังไม่ได้รัน) และวิธีรัน Pod dns แบบ interactive
2. LAB6: `kubectl rollout undo sts/web`; LAB7: `minReadySeconds` (ยังไม่ได้รัน)
3. LAB8: `--cascade=orphan` (ถ้าจะใส่)
4. LAB10 ขั้น B: ข้อความ error ถ้าผู้เรียน apply headless ทับ Service ClusterIP เดิมโดยไม่ลบก่อน (คาดว่า `spec.clusterIP … field is immutable` — ยังไม่ได้รัน)
5. LAB10 เสริม: ทดสอบซ้ำบนคลัสเตอร์สะอาดอีกรอบตอนเขียนไฟล์จริง (pre-check ผ่าน 1 รอบ)
6. ภาพ needs_test (43 ภาพ) ตรวจตัวเลข/ข้อความกับ log รันจริงก่อนสร้างภาพ (เช่น `orders=3/4`, IP, revision hash ไม่ใส่ในภาพ)
