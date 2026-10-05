# SUMMARY — ทดสอบ LAB บท 005 ReplicaSet (รันจริง 5 ต.ค. 2569)

- container ทดลอง `k8s-lab-rs005lab-abd71a` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`) — **ยังเปิดอยู่** ตามคำสั่ง (ดู `handoff.md`) ไม่ได้แตะ `k8s-lab` ของผู้เรียน / `deep_vision_5090_vllm`
- `k8s-up` 54 วิ, kubectl v1.37.1 / server v1.37.0; โฟลเดอร์บท `docker cp` ไปที่ `/workspace/005_kubernetes_replicaset` แล้วรันทุกคำสั่งจาก `02_LAB`
- log คำสั่ง+output จริง: `lab00.log` … `lab09.log`, `handoff-commands.log` (บรรทัด `### hh:mm:ss` เป็นเวลา UTC ของเครื่อง agent; `date` ในคำสั่งเป็นเวลาไทย)
- ไม่มี Service/Deployment/`kubectl rollout` ในขั้นตอน LAB

## ผลรายข้อ

| LAB | ผล | เวลาจริง (รวมพิมพ์) | ผลจริงสำคัญ |
|---|---|---|---|
| 0 | ✅ (แก้คำสั่ง 1 จุด) | <1 นาที | 3 Node Ready, ไม่มี taint/unschedulable ค้างบน worker; `pod "lonely" deleted from rs-lab namespace` → `No resources found in rs-lab namespace.`; `kube-controller-manager-lab-control-plane` บน lab-control-plane; **คำสั่งในแผน `... \| tr ',' '\n' \| grep controllers` ได้แค่ `"--controllers=*`** (ค่าถูกตัดที่ comma) → ใช้ `... -o jsonpath='{.spec.containers[0].command}' \| grep -o -- '--controllers=[^"]*'` ได้ `--controllers=*,bootstrapsigner,tokencleaner` |
| 1 | ✅ | <1 นาที | `snack-rs 3 3 3` (5 วิแรก `3 3 2` เพราะ Node แรก pull busybox); ownerReferences `[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"ReplicaSet","name":"snack-rs","uid":"..."}]`; Events `SuccessfulCreate ... Created pod: snack-rs-w5dtc` ×3 (ระบุชื่อ Pod); status `{"availableReplicas":2,"fullyLabeledReplicas":3,"observedGeneration":1,"readyReplicas":2,"replicas":3,"terminatingReplicas":0}` (**มี `terminatingReplicas`**); bad-labels: `The ReplicaSet "snack-rs-bad" is invalid: spec.template.metadata.labels: Invalid value: {"app":"snak"}: `selector` does not match template `labels`` exit 1; expr: SELECTOR แสดง `tier in (drink,snack),!track` |
| 2 | ✅ | ~4 นาที (รวม docker stop) | ลบ 1 ตัว: ตัวใหม่ Pending ใน <1 วิ, Running 2 วิ ขณะตัวเก่า Terminating; ลบ `-l app=snack` ได้ 3 ตัวใหม่ Running ใน ~2 วิ; **Pod เก่าขึ้น STATUS `Error` ชั่วครู่** (busybox ถูก kill หลัง grace 1 วิ exit 137) ; drain ไม่ต้อง `--force` ใช้ 3.07 วิ (`Warning: ignoring DaemonSet-managed Pods: kube-system/kindnet-..., kube-system/kube-proxy-...`, `evicting pod rs-lab/...`, `node/lab-worker2 drained`) Pod 2 ตัวไปเกิดบน lab-worker, uncordon แล้วไม่ย้ายกลับ; ทางเลือก docker stop (toleration 30): stop ใช้ 11 วิ, **NotReady ที่ t≈41–44 วิ** (นับจากเริ่ม stop), ตัวแทนเกิดบน lab-worker ที่ **t≈74–77 วิ**; ระหว่าง NotReady `get rs` = `3 3 1`; หลังไล่ `3 3 3` และ status มี `"terminatingReplicas":2`; Pod เก่าค้าง `Terminating` จน `docker start` (Node Ready 2 วิ, Pod เก่าหาย 4 วิ หลัง start) |
| 3 | ✅ | ~1 นาที | 3→5 ทันที; **5→2 ลบ `ldzjc` (ตัวเก่า บน lab-worker2 ที่มี 3 ตัว), `m259n` (ใหม่ บน lab-worker), `zsdq7` (ใหม่ บน lab-worker2)** → เหลือ 1+1 (ตัวเก่า 2 ตัว) = ไม่ใช่ "ใหม่สุด 3 ตัว" แต่ตามเกณฑ์เรือแออัดก่อนแล้วค่อยอายุ; `sed` แก้ไฟล์ → 4; `kubectl edit` ใช้ได้ (k8s-lab มี nano/vi/vim, EDITOR ไม่ได้ตั้ง → ค่าเริ่มต้น vi; แนะนำ `KUBE_EDITOR=nano`); scale 0 → `0 0 0` RS ยังอยู่, Pod ขึ้น `Error` ก่อนหาย; apply ไฟล์ทับค่าที่ scale |
| 4 | ✅ (มีข้อควรระวัง) | ~2 นาที | (ก) stray ถูกลบทันที (`get pods` เห็น `stray 0/1 Terminating 0s`) แต่ **Event `Deleted pod: stray` ไม่ขึ้นในรอบแรก** เพราะ event spam filter ของ controller (~25 event ต่อ object/uid) ถูกใช้หมดจาก LAB 2–3 — ทดสอบซ้ำกับ RS ที่สร้างใหม่ (uid ใหม่) ได้ `Normal SuccessfulDelete 2s replicaset-controller Deleted pod: stray2` ; (ข) สร้างเพิ่มแค่ 2, stray มี ownerReferences `snack-rs`, `kubectl exec stray -- cat /proc/1/cmdline` = command ต่างจาก template; (ค) snack-rs-b สร้างของตัวเอง 3 ตัว รวม `-l app=snack` 6 ตัว แต่ละ RS นับ 3 ของตัวเอง ไม่แย่งกัน (OWNER คนละตัว); (ง) `kubectl label pod ... app-` → ownerReferences ว่าง **ทันที** (ตรวจหลัง label <0.1 วิ ก็ว่างแล้ว), RS สร้างตัวแทนภายใน 1 วิ, Pod ที่ถอดป้ายยัง Running + logs ได้ |
| 5 | ✅ (แก้คำสั่ง 1 จุด) | ~1 นาที | web Ready 9 วิ (pull nginx:1.27); **`kubectl exec <pod> -- wget -qO- localhost` → `wget: can't connect to remote host: Connection refused`** เพราะ `command` ทับ entrypoint ของ nginx (สคริปต์เปิด listen IPv6 ไม่ทำงาน) และ localhost → `::1` ก่อน → ใช้ `wget -qO- 127.0.0.1` ได้ `web v1 from web-6qrsq`; selector: `The ReplicaSet "web" is invalid: spec.selector: Invalid value: {"matchLabels":{"app":"web","tier":"front"}}: field is immutable`; หลัง apply v2: `get rs -o wide` IMAGES `nginx:1.28-alpine` แต่ Pod ทั้ง 3 ยัง `nginx:1.27-alpine v1`; ลบ 1 ตัว → ตัวใหม่ `nginx:1.28-alpine v2` ตอบ `web v2 from web-d4lf5` (pull 1.28 6.854 วิ) |
| 6 | ✅ | ~1 นาที | orphan: Pod 3 ตัวอยู่ต่อ OWNER `<none>`; apply ใหม่ → `3 3 3` ไม่มี Pod ใหม่, `Events: <none>`, ownerReferences กลับมาด้วย uid ใหม่ของ RS; foreground: terminal 2 เห็น `["foregroundDeletion"]` หลายบรรทัด และ `get rs -w` เห็น CURRENT 3→2→0 ก่อน RS หาย, `kubectl delete` ใช้ ~3.3 วิ (grace 1 วิพอ ไม่ต้องเพิ่มเป็น 10); `kubectl delete ns rs-lab` 6 วิ |
| 7 | ✅ | ~2 นาที | `quota-rs 6 4 4`; Event `Warning FailedCreate ... Error creating: pods "quota-rs-kxq2g" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4` (ตามด้วย `(combined from similar events)` xN); Conditions `ReplicaFailure True FailedCreate`; resources ที่ LimitRange เติม `{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}`; **หลัง patch quota เป็น 6 ใช้ 46 วิ RS จึงสร้างครบ** (backoff ของ controller) condition หายไป; PSA: `Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (...), unrestricted capabilities (...), runAsNonRoot != true (...), seccompProfile (...)` ตอน apply RS, `psa-rs 3 0 0`, FailedCreate `Error creating: pods "psa-rs-7qhvg" is forbidden: violates PodSecurity "restricted:latest": ...` |
| 8 | ✅ (แก้ manifest 1 จุด) | ~2 นาที | required: 2 Running คนละเรือ + 1 Pending `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.`; preferred 5 รอบ = 2+1 ทุกรอบ (lab-worker2 2, lab-worker 1); topology (+`nodeTaintsPolicy: Honor`) 2+2 → scale 5 = 2+3; **ถ้าไม่ใส่ Honor ได้ 1+1 + Pending 2** (`... 2 node(s) didn't match pod topology spread constraints ...`) |
| 9 | ✅ | ~7 นาที | ดูหัวข้อถัดไป |

## LAB 9 — ผลตาม "จุดที่ต้องยืนยัน" (แผน 3.6)

1. **resource 5 บูธ:** ขึ้นครบ ไม่มี Pending; scale 3→5 Ready ใน 8 วิ; Allocated requests: lab-worker (2 บูธ) cpu 500m / mem 946Mi, lab-worker2 (3 บูธ) 700m / 1394Mi; memory ใช้จริง (`docker stats` ใน k8s-lab) lab-worker 497MiB, lab-worker2 522MiB, control-plane 749MiB; container ทดลองทั้งตัว 4.0GiB (รวม cache/build) — เครื่องทดสอบ 62GB RAM, allocatable ของ Node = ทั้งเครื่อง (32 CPU / ~61Gi) จึงยืนยันกรณี RAM 8GB ไม่ได้ ยังให้คำแนะนำ `--replicas=4` ไว้
2. preferred 2+1 ✅ (lab-worker2 2 / lab-worker 1); 5 บูธ = **2+3** (lab-worker 2, lab-worker2 3; แผนเขียน 3+2 — กลับด้านได้); 5→2 ลบ `7szlj`, `qfxhd` (ใหม่ทั้งคู่ บน lab-worker2 ที่แออัด) + `szvhd` (ใหม่กว่า บน lab-worker) → เหลือบูธเดิม 2 ตัว 1+1 ✅; port-forward 8081 (ไป szvhd) ตาย, 8082/8083 ยัง 200
3. `docker tag som-shop-web:1.1 som-shop-web:1.1-promo` + `kind load docker-image som-shop-web:1.1-promo --name lab` → kind แจ้ง `Image: "som-shop-web:1.1-promo" with ID "sha256:2f06fd68..." not yet present on node "lab-worker2", loading...` (3 Node, 3.1 วิ) และ `crictl images` เห็น tag `1.1-promo` ID เดียวกับ 1.1 ✅ **ไม่ต้องใช้ทางสำรอง `--label`**
4. port-forward เมื่อ Pod ถูกลบ: process **ไม่จบทันที** (`pgrep` ยังเห็น) จนมี connection แรก → curl `exit 52` (empty reply, http 000), ผ่าน ssh -L ได้ curl exit 56; log: `E1005 ... portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod <sandbox-id>, uid : network namespace for sandbox \"...\" is closed" localPort=8081 remotePort=3000` ตามด้วย `error: lost connection to pod` แล้ว process จบ; browser (Chromium/Playwright ผ่าน ssh -L) = **`net::ERR_CONNECTION_RESET`**; port-forward ใหม่ที่ 8081 ใช้ tunnel ssh -L เดิมได้ทันทีไม่ต้องต่อใหม่
5. `$(POD_NAME)` ✅ หน้าเว็บ `⚓ บูธ som-booth-9t78k` / promo `🎉 โปรบูธใหม่ · som-booth-5h2fk`, emoji แสดงถูก (ตรวจภาพจริงใน Chromium), ท้ายหน้า `🐱 เสิร์ฟโดย Pod: som-booth-...` + `Next.js + PostgreSQL · Kubernetes LAB 005 · ReplicaSet som-booth`, title `ร้านอาหารแมวน้องส้ม (หลายบูธ)`
6. ไม่มี Warning PSA ตอน apply ✅
7. `POST /api/orders` `{"product_id":1,"qty":1}` → `{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}` ✅; **`GET /api/orders` ไม่มี → `HTTP/1.1 405 Method Not Allowed`** (แอป 1.1 มีแค่ POST; README บท 004 บรรทัด ~2360 ก็อ้าง `curl localhost:3002/api/orders` ซึ่งใช้ไม่ได้) ใช้แทน: `curl -s localhost:808N/api/products \| grep -o '"stock":[0-9]*' \| head -1` (ได้ 18/20/20) หรือ `curl -s localhost:808N \| grep -o '[0-9]*</span><span class="label">ออเดอร์ทั้งหมด'` (ได้ 2/0/0)
8. เวลาบูธใหม่ Ready หลังลบ: **~7 วิ** (วัด 4 ครั้ง: 7, 7, 7, 7 วิ — db init + seed + web); เปิดร้านครั้งแรก 3 บูธ 8 วิ (image อยู่บน Node แล้ว); ลบ ns som-booths 10.9 วิ

อื่น ๆ: build `som-shop-web:1.1` 28.8 วิ, kind load 1.1 5.1 วิ, postgres save+load 5.7 วิ; db-seed ทุกบูธ `connected to database` / `tables ready: products, orders` / `seeded 6 products (new: 6)` ไม่มี init restart (db แยกบูธ จึงไม่ชน race แบบ pre-check #23)

## การเปลี่ยนแปลงจากแผน

1. **คัดลอกแอปมาไว้ใน `02_LAB/som-booths/app/`** (ตามคำสั่งผู้ประสานงาน แทนการอ้างโฟลเดอร์บท 004 ในแผน) — ไม่รวม node_modules/.next; build จาก `som-booths/app` ได้ผลเหมือนเดิม (ID ต่างกันตามเวลา build)
2. `spread-topology.yaml` เพิ่ม `nodeTaintsPolicy: Honor` (ค่าเริ่มต้น Ignore นับ control-plane → 1+1+Pending 2; บท 003 LAB 5 สอนไว้แล้ว)
3. LAB 0: เปลี่ยนคำสั่งดู `--controllers` เป็น `grep -o -- '--controllers=[^"]*'`
4. LAB 5: `wget -qO- 127.0.0.1` แทน `localhost`
5. LAB 9.4: ไม่มี `GET /api/orders` → ใช้ `/api/products` (stock) หรือ grep ตัวเลข "ออเดอร์ทั้งหมด" จากหน้าเว็บ
6. LAB 9.7: **`kubectl apply -f k8s/som-booth-promo.yaml` หลัง 9.6 (replicas=2) คืนค่า replicas เป็น 3 ตามไฟล์ → เกิดบูธ promo ทันที 1 ตัว** (ทดสอบจริง: `som-booth-6tq4x som-shop-web:1.1-promo`) ทำให้ไม่เห็น "บูธเดิม 1.1 ทุกตัว" แบบที่แผนคาด → แนะนำให้ท้าย 9.6 `kubectl scale rs som-booth -n som-booths --replicas=3` (บูธที่ 3 เป็น 1.1) ก่อน 9.7 — ทดสอบลำดับนี้แล้ว: apply promo → `IMAGES som-shop-web:1.1-promo` แต่ Pod ทั้ง 3 ยัง `som-shop-web:1.1` ✅ (หรือใช้ผลนี้สอนเพิ่มว่า apply ไฟล์ทับค่าที่ scale)
7. LAB 4: แนะนำเริ่ม LAB 4 ด้วย `kubectl delete rs snack-rs -n rs-lab && kubectl apply -f labs/lab01-first-rs/snack-rs.yaml` (RS uid ใหม่ → Event ขึ้นครบ) หรือบอกนักศึกษาว่า Event อาจไม่ขึ้น ให้ดูจาก `get pods` แทน
8. LAB 3: แผนใช้ `describe rs` ดู `SuccessfulDelete` — หลัง LAB 2 Events ยาวและมี `(combined from similar events)` แนะนำ `kubectl get events -n rs-lab --field-selector reason=SuccessfulDelete`
9. LAB 2 ทางเลือก: snack-rs-fast-evict ต้อง `kubectl delete pod -n rs-lab -l app=snack` หลัง apply ให้ Pod ได้ toleration ใหม่ และต้องเช็กว่ามี Pod บน lab-worker2 ก่อน stop (หลัง drain+uncordon Pod อยู่ lab-worker หมด); ท้าย LAB 2 apply `snack-rs.yaml` คืน + ลบ Pod เพื่อกลับ template เดิม
10. LAB 3 `sed -i` แก้ไฟล์ `snack-rs.yaml` ของนักศึกษา (replicas 4) — LAB 4/6 ใช้ไฟล์เดียวกันต่อ ต้องให้ sed กลับเป็น 3 (ทดสอบแล้ว `sed -i 's/replicas: 4 /replicas: 3 /'` — มีช่องว่างหลังเลขเพราะมีคอมเมนต์ต่อท้าย)
11. port-forward ของ handoff ใช้ 3001–3003 + `--address 127.0.0.1` ตามคำสั่ง (ใน LAB ใช้ 8081–8083 ตามแผน)

## ป้าย/ข้อความในภาพ storyboard (`images.json`) ที่ไม่ตรงผลจริง

| ภาพ | ตอนนี้ | ผลจริง / ควรใช้แทน |
|---|---|---|
| **T17** node-down-timeline | ป้าย `NotReady ~50 วิ`; caption "NotReady หลังราว 50 วิ" | วัดได้ **~40–45 วิ** (บท 003 ~45–50) → ป้าย `NotReady ~45 วิ`; ถ้าอยากใส่เวลาสร้างแทนใช้ `สร้างแทน ~75 วิ` (toleration 30) |
| **L18** template-promo | Scene "the two booths on the ships still show the old plain signboards", ป้าย `1.1` ×2 | ถ้าทำตามแผน (replicas 2) จะมีบูธ promo เกิดทันที → แก้ README ตามข้อ 6 แล้วเปลี่ยนเป็น **3 บูธ** ป้าย `1.1` ×3 (หรือคง 2 บูธ + เพิ่มบูธที่ 3 เป็น promo ถ้าจะสอนเรื่อง apply ทับ replicas) |
| **L12** lab9-prepare-image | caption "build som-shop-web:1.1 จากโฟลเดอร์บท 004" | build จาก `som-booths/app` ในบทนี้ (สำเนาจากบท 004) |
| **L17** scale-3-5-2 | Scene "five booths on two ships (three and two)" | จริง 2+3 (ลำไหนได้ 3 ไม่แน่นอน) — ภาพไม่ระบุชื่อเรือจึงใช้ได้; caption "ถ้า Pending ให้ใช้ 4" ยังคงไว้ได้แต่ระบุว่าในเครื่องทดสอบไม่มี Pending |
| **L10** lab8 | caption "topologySpreadConstraints maxSkew 1 → 2+2 / 3+2" | ได้จริงเมื่อใส่ `nodeTaintsPolicy: Honor` (ไม่ใส่ → Pending) ควรเติมใน caption; ผล 5 ตัวจริง 2+3 |
| **T33** preferred/topology | caption ไม่พูดถึง Honor | เติม "(ใน kind ต้อง nodeTaintsPolicy: Honor ไม่งั้นนับ control-plane)" |
| **L09** lab7-quota | caption "เพิ่ม quota แล้ว RS สร้างต่อเอง" | จริงต้องรอ **~46 วิ** (backoff) → เติม "(อาจรอเกือบ 1 นาที)" |
| **T11** selector-template-mismatch | ป้าย `selector does not match template labels` | ข้อความจริงมี backtick: `` `selector` does not match template `labels` `` (ป้ายในภาพใช้แบบไม่มี backtick ได้ แต่ README ต้องคัดลอกตามจริง) |
| **T22 / L06** | ป้าย `Deleted pod: stray` | ข้อความถูกต้อง แต่ Event อาจไม่ขึ้นถ้า RS มี event เยอะแล้ว (ข้อ 7) — ภาพไม่ต้องแก้ |
| T15 | `~3 วิ` | จริง ตัวใหม่ถูกสร้าง <1 วิ, Running ~2 วิ — `~3 วิ` ยังถูกในฐานะ "ภายใน" ไม่ต้องแก้ |
| T01/T34 IP ตัวอย่าง | `10.244.2.9`, `10.244.2.15` | คลัสเตอร์ทดสอบได้ Pod CIDR lab-worker `10.244.1.x`, lab-worker2 `10.244.3.x` (ไม่มี 10.244.2.x) — เป็นค่าตัวอย่าง แก้หรือไม่ก็ได้ |

ภาพ needs_test อื่นตรงผลจริง: T19 (ลำดับ: แออัดก่อน แล้วใหม่กว่า — ผลจริงสอดคล้อง), T25, T30 (`4/6`, `FailedCreate: exceeded quota`, `ReplicaFailure`), T31 (`0/3` = `3 0 0`, Warning จริงขึ้นต้น `Warning: would violate PodSecurity`), L04, L05, L07 (1.27 ×2 + 1.28 ×1 ตรงสภาพหลังลบ 1 ตัว), L13 (2+1), L15 (`ออเดอร์ 2`/`0`/`0` ตรงเป๊ะ), L16 (ออเดอร์ 0, 8081 หลุด), L19 (ทีละตัว ~7 วิ/บูธ)

## ข้อควรระวังสำหรับนักศึกษา

- Pod busybox ที่ถูกลบ/scale ลงจะขึ้น `Error` ชั่วครู่ก่อนหาย (ถูก kill หลัง grace 1 วิ) ไม่ใช่ความผิดพลาด
- ใน nginx ที่ทับ `command` ให้ `wget 127.0.0.1` ไม่ใช่ `localhost`
- Event ของ RS อาจหายเมื่อมีเหตุการณ์เยอะ (rate limit) ให้เชื่อ `kubectl get pods` / `get rs` เป็นหลัก
- หลังเพิ่ม quota RS อาจรอเกือบ 1 นาทีกว่าจะสร้างต่อ
- `kubectl apply` ไฟล์ที่มี `replicas:` จะทับค่าที่ `kubectl scale` ไว้เสมอ
- `kubectl wait -l app=som-booth` หลังลบบูธ: ตัวใหม่ถูกสร้างทันทีจึงรอได้ถูก แต่ถ้าพิมพ์ช้าอาจเห็นแค่บูธเดิม Ready — ดู `get pods -w` ประกอบ
- port-forward ไป Pod ที่ถูกลบยังดูเหมือนทำงาน (`jobs`/`pgrep` ยังเห็น) จนมีคนเข้า แล้วจึงจบพร้อม `error: lost connection to pod`; tunnel `ssh -L` ไม่ต้องเปิดใหม่ เปิดแค่ port-forward ใหม่
- `pkill -f`/`pgrep -f` ใช้ pattern `"[k]ubectl port-forward"` เสมอ (ทดสอบแล้ว pattern ที่ไม่มีวงเล็บฆ่า shell ที่พิมพ์คำสั่งนั้นเอง)
- `GET /api/orders` ไม่มี (405) ดูออเดอร์ที่หน้าเว็บหรือ stock ใน `/api/products`
- sed ใน LAB 3 แก้ไฟล์ของนักศึกษา ต้องแก้กลับก่อน LAB 4
- ระหว่างเรือล่ม `get rs` แสดง `3 3 1` (CURRENT ยังนับ Pod บนเรือที่ตาย) จน Pod ถูกไล่ (~30 วิหลัง NotReady ด้วย toleration 30 หรือ ~300 วิค่าเริ่มต้น)
- 5 บูธต้องการ requests ~1 CPU / ~2.2Gi; เครื่อง RAM น้อยให้ scale แค่ 4

## สถานะไฟล์/cleanup

- ไฟล์ LAB: `005_kubernetes_replicaset/02_LAB/labs/**` (18 ไฟล์), `som-booths/k8s/{00-namespace,som-booth,som-booth-promo}.yaml`, `som-booths/app/` (17 ไฟล์) — ยังไม่มี `02_LAB/README.md` (นอกขอบเขตงานนี้)
- scratch: `r.sh` (ตัวช่วยรัน+log), `container-name`, `check-8081.png`/`check-promo.png` (ภาพตรวจ ไม่ใช่ screenshot ส่งงาน), `storyboard-extract.txt`; askpass ลบแล้ว, ssh tunnel ของ agent ปิดแล้ว
- container `k8s-lab-rs005lab-abd71a` ยังรัน (SSH 2224) — ผู้ประสานงานลบเอง
