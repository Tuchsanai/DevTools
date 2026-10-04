# สรุปผลทดสอบ LAB 003 — Node กับ Pod (รันจริง 4 ต.ค. 2569)

- container ทดลอง: `k8s-lab-nodepod003-211945` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`) — **ยังเปิดไว้** ตาม handoff ดู `handoff.md`
- ไฟล์ LAB: `003_kubernetes_node_pod/02_LAB/{labs,som-shop-branches}` → `docker cp` ไปที่ `/workspace/003_kubernetes_node_pod/02_LAB` รันทุก LAB ต่อเนื่องในคลัสเตอร์เดียว (สร้างใหม่ด้วย `k8s-up`) ตามลำดับ 0→10
- log คำสั่ง + output จริง: `lab00.log` … `lab10.log` (เวลาในวงเล็บ `[HH:MM:SS]` = UTC ของเครื่องที่สั่ง, เวลาใน container/`describe` = +0700)
- เวอร์ชัน: kubectl v1.37.1 / server v1.37.0, kind 0.33.0, Docker ใน container 29.8.2, containerd บน node 2.3.4, `nginx:1.27-alpine`, `busybox:1.36`, `postgres:17.11-alpine` (ID `b0f9560a2de0`), `som-shop-web:1.0` build ใหม่ ID `84cfc41b9bcb`
- manifest ทุกไฟล์ผ่าน `kubectl apply --dry-run=server` ก่อนรันจริง

## ผลรายข้อ

| LAB | ผล | ค่าจริงที่สำคัญ |
|---|---|---|
| 0 สำรวจกองเรือ | ✅ | `k8s-up` 51.3 วิ; 3 node Ready v1.37.0, ROLES `control-plane`/`<none>`; มี label `beta.kubernetes.io/arch|os` ด้วย; control-plane มี label `node.kubernetes.io/exclude-from-external-load-balancers`; **allocatable = capacity ทุกค่า** (cpu 32, memory 64489564Ki, pods 110, ephemeral 1081101176832) และทุก node เห็นเท่ากัน; taint เฉพาะ control-plane; `crictl ps` worker = `kindnet-cni`, `kube-proxy`; control-plane = etcd/apiserver/scheduler/controller-manager + coredns×2 + local-path-provisioner + kindnet + kube-proxy; lease 3 ตัว `leaseDurationSeconds: 40` ต่ออายุทุก 10 วิ (วัดได้ 10.17 วิ); kube-controller-manager ไม่ได้ตั้ง `node-monitor-grace-period` (ใช้ default) |
| 1 Pending | ✅ | fit-pod Running (lab-worker2); huge-pod: `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.`; Allocated resources ของ node: cpu 100m→200m, memory 50Mi→114Mi; apply ไฟล์ที่แก้เป็น 256Mi → `Forbidden: pod updates may not change fields other than ...`; ลบ + apply ใหม่ → Running |
| 2 nodeName + Downward | ✅ | pinned-pod Running บน lab-control-plane ไม่มี toleration และ Events **ไม่มี `Scheduled`** (มีแค่ Pulling/Pulled/Created/Started); ghost-node-pod Pending, `Node: lab-worker9/`, Events `<none>` แล้ว **PodGC ลบทิ้งเองที่ ~62 วิ** (log controller-manager: `"PodGC is force deleting Pod" pod="default/ghost-node-pod"`); `whereami` → `สวัสดีจาก whereami บนเรือ lab-worker2 (Pod IP 10.244.2.3, Node IP 172.19.0.2)` ตรง `-o wide`, `$(VAR)` แทนค่าถูก |
| 3 nodeSelector / affinity | ✅ | ก่อนติด label: `... 2 node(s) didn't match Pod's node affinity/selector ...`; หลังติด label ถูกวาง **ภายใน ~1 วิ**; ลบ label → Pod ยังอยู่; `label` ซ้ำไม่ใส่ `--overwrite` → `error: 'fleet' already has a value (fast), and --overwrite is false`; required → lab-worker; preferred 4 ตัว → **lab-worker2 ทั้ง 4**; เมื่อไม่มีเรือ fast (ทั้งคู่ eco) preferred ยัง Running 2+2 แต่ selector-pod Pending; Gt → lab-worker2 |
| 4 pod (anti-)affinity | ✅ | apply web-near-cache ก่อน cache → `2 node(s) didn't match pod affinity rules` แล้วถูกวางเองทันทีเมื่อ cache มา (ทั้งคู่ lab-worker); crew-1/2 คนละ worker, **crew-3 Pending**: `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.`; preferred (deckhand) 3 ตัว Running 2+1; เสริม: ลบ crew-1 → crew-3 ถูกวางเองใน ~3 วิ |
| 5 topology spread | ✅ (ตรงแผน) | **Ignore (default) ทำให้ Pending จริง**: spread-1/2 Running 1+1, spread-3/4 Pending `... 2 node(s) didn't match pod topology spread constraints ...`; Honor → 4 ตัว 2:2; `-o jsonpath` ยืนยันว่า spec ไม่มี `nodeTaintsPolicy` เมื่อไม่ได้ตั้ง |
| 6 taints | ✅ | plain-pod ลง lab-worker 5/5 รอบ; vip-pod ลง lab-worker2; control-plane-pod ลง lab-control-plane; NoExecute: `no-pass` ถูกไล่ **< 1 วิ**, `pass-30s` ถูกไล่ที่ **+30–31 วิ**, `pass-forever` อยู่ต่อ; **vip-pod (บน lab-worker2) ถูกไล่ด้วย** เพราะไม่มีบัตร maintenance; Event `Normal TaintManagerEviction ... Marking for deletion Pod default/no-pass` + `Killing ... Stopping container web`; Pod ที่ถูกไล่ไป Terminating → Completed → หายจาก list ภายใน ~1 วิ (node ปกติ ไม่ค้าง) |
| 7 cordon / drain | ✅ | cordon → `Ready,SchedulingDisabled`, `spec.unschedulable: true` + taint `node.kubernetes.io/unschedulable:NoSchedule`; Pod ใหม่ (`kubectl run late-cargo`) ไป lab-worker2; drain ไม่มี --force → `error: unable to drain node "lab-worker" due to error: [cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4, cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry], continuing command...`; ไม่ใส่ `--ignore-daemonsets` → `cannot delete DaemonSet-managed Pods (use --ignore-daemonsets to ignore): kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl`; ครบ → `Warning: deleting Pods that declare no controller: ...; ignoring DaemonSet-managed Pods: ...` `evicting pod ...` `pod/... evicted` `node/lab-worker drained` ใช้ **2.06 วิ**; ไม่มี Pod ใหม่บน lab-worker2, uncordon แล้วก็ไม่กลับ; Events node `NodeNotSchedulable` / `NodeSchedulable` |
| 8 node NotReady | ✅ | ดูหัวข้อ "เวลาจริง" — node กลับ Ready เองหลัง `docker start` ทุกครั้ง (3 รอบรวม LAB10) ไม่ต้องใช้แผนสำรอง |
| 9 static Pod | ✅ | control-plane มี 4 ไฟล์; `staticPodPath: /etc/kubernetes/manifests` และ **โฟลเดอร์มีอยู่แล้ว (ว่าง)** บน worker; mirror pod `static-snack-lab-worker` โผล่และ Ready **ทันที (< 1 วิ)** หลัง `docker cp` (ไม่ต้องรอ 20 วิ); annotation `kubernetes.io/config.mirror`, `config.source: file`; ownerReferences `kind: Node name: lab-worker`; Events ไม่มี Scheduled; **`kubectl delete` mirror pod ค้าง 65–80 วิ** (วัด 3 รอบ: ~70 วิ, 65.5 วิ, ~80 วิ) แสดง `Terminating` แล้วกลับมาเป็น mirror ใหม่ (UID ใหม่) โดย container จริงไม่ถูก restart (crictl ATTEMPT 0, IP เดิม); `rm` ไฟล์ → หายใน 3 วิ |
| 10 som-shop-branches | ✅ | ดูหัวข้อ LAB10 ด้านล่าง |

## เวลาจริง (node ล่ม / evict / กลับมา)

| เหตุการณ์ | LAB8 รอบหลัก | LAB8 รอบเสริม | LAB10 |
|---|---|---|---|
| `docker stop lab-worker2` ใช้เวลา | 0.8 วิ | – | – |
| stop → `NotReady` (Ready=`Unknown`, reason `NodeStatusUnknown`, `Kubelet stopped posting node status.`) | **44 วิ** (LastTransitionTime; monitor เห็นที่ +45) | **50 วิ** | **43 วิ** |
| heartbeat ล่าสุด (lease RenewTime) → NotReady | 53 วิ (renew 19:06:10, NotReady 19:07:03) ≈ grace 50 วิ + รอบตรวจ | | |
| taint อัตโนมัติ | `node.kubernetes.io/unreachable:NoSchedule` + `:NoExecute` พร้อมกับ NotReady | | |
| Pod ระหว่าง NotReady | `READY 1/1`, `STATUS Running` ค้าง แต่ condition `Ready=False`; Event `Warning NodeNotReady pod/... Node is not ready` | | som-shop-b `2/2 Running` ค้าง |
| ถูกไล่ (tolerationSeconds 30) `fog-fast` | Terminating ที่ +73 วิ (= NotReady + 29–30 วิ) | | |
| ถูกไล่ (default 300) `fog-default` | Terminating ที่ +345 วิ (= NotReady + 301 วิ) | | |
| ถูกไล่ (tolerationSeconds 60) `som-shop-b` | | | Terminating ที่ +104 วิ (= NotReady + 61 วิ) |
| หลัง evict | `Terminating` ค้างจนเรือกลับ (6 นาที+) ไม่ถูกสร้างที่อื่น | | ค้าง Terminating |
| `docker start` → Ready | **2 วิ** | **2 วิ** | **2 วิ** |
| Pod ที่ถูก evict หายจริง | ~5 วิหลัง start (เห็น `Unknown`/Failed ชั่วขณะ) | – | 5 วิ |
| taint unreachable หาย | ~7 วิหลัง start | | < 30 วิ |
| IP ของ node | ไม่เปลี่ยน (172.19.0.2) | ไม่เปลี่ยน | ไม่เปลี่ยน |
| Pod ระบบบนเรือ | kindnet/kube-proxy Running, RESTARTS +1 ทุกครั้งที่ stop/start | | |
| Pod ที่ **ไม่ทัน** ถูกไล่ (เรือกลับก่อนครบ) | | fog-default/fog-fast อยู่ต่อ **RESTARTS 1** และ **Pod IP เปลี่ยน** (10.244.2.2↔.3 สลับกัน เพราะ sandbox ถูกสร้างใหม่) | |

- คำสั่งไป Pod บนเรือที่ล่ม: `kubectl exec` → `error: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host`; `kubectl logs` → `Error from server: Get "https://172.19.0.2:10250/containerLogs/...": dial tcp 172.19.0.2:10250: connect: no route to host`; `kubectl port-forward` ใหม่ → `error: error upgrading connection: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host` (รอ ~6 วิ)
- port-forward ที่เปิดอยู่ไป Pod บนเรือที่ `docker stop` → หลุด **ทันที** `error: lost connection to pod` (curl ได้ exit 7)
- `kubectl apply` ซ้ำขณะ Pod Terminating → `Warning: Detected changes to resource fog-fast which is currently being deleted.` + `pod/fog-fast unchanged` (LAB10: `pod/som-shop-b configured` + warning เดียวกัน) — ไม่มี Pod ใหม่ ไม่ใช่ AlreadyExists
- Events: `NodeNotReady` (node + pod), `TaintManagerEviction ... Marking for deletion Pod default/<name>`; หลัง start: `Starting`, `NodeHasSufficientMemory`, ..., `NodeReady`

## LAB10 ร้านน้องส้มหลายสาขา — ผลจริงตาม "จุดที่ต้องยืนยัน" (แผน 3.6)

1. ✅ `$(NODE_NAME)` แทนค่าจริง: `printenv` → `ร้านอาหารแมวน้องส้ม สาขา lab-worker` / `... lab-worker2`, POD_IP ตรง `-o wide`; หน้าเว็บ `<h1>` แสดงชื่อสาขา **และ `<title>` ก็แสดงชื่อสาขาด้วย** (metadata อ่าน env ตอน runtime เพราะหน้าเป็น force-dynamic — แท็บ browser เป็นชื่อสาขา ไม่ใช่ชื่อร้านเฉย ๆ); footer `เสิร์ฟโดย Pod: som-shop-a` / `som-shop-b`
2. ✅ `kind load` ใส่ image ทั้ง 3 node (รวม control-plane); `crictl images` เห็นทั้ง 2 worker; READY `2/2`; ลำดับ STATUS เหมือนบท 002 (`Init:0/3` → `Init:1/3` → `1/2 Init:1/3` → `1/2 Init:2/3` → `PodInitializing` → `1/2 Running` → `2/2 Running`) Ready ทั้งคู่ **8 วิหลังติดธง**; build 28.2 วิ, `kind load docker-image` 4.9 วิ, `docker save --platform linux/amd64` 1.5 วิ + `kind load image-archive` 4.0 วิ; image ยังอยู่บน node หลัง `docker stop/start`
3. FailedScheduling จริง:
   - ก่อนติดธง: `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector. ...`
   - som-shop-c: `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.` — **control-plane ถูกนับเป็น "untolerated taint" ไม่ใช่ "didn't match node affinity"** (ต่างจากแผน; แต่ละ node แสดงเหตุผลแรกที่ตกเท่านั้น)
   - som-shop-a ระหว่าง cordon: `0/3 nodes are available: 1 node(s) didn't match pod anti-affinity rules, 1 node(s) had untolerated taint(s), 1 node(s) were unschedulable. preemption: ...` — **มี `node(s) were unschedulable` จริง**
4. ✅ drain ไม่มี --force/--delete-emptydir-data → `cannot delete Pods with local storage (use --delete-emptydir-data to override): default/som-shop-a` (บอกแค่เหตุผล local storage — node ถูก cordon แล้วแม้ error); ใส่ครบ → evict ใน **1.06 วิ** (Postgres + Next.js ปิดเร็ว ไม่ถึง grace 30 วิ); port-forward 3001: `"An error occurred forwarding" err="... network namespace for sandbox ... is closed"` แล้ว `error: lost connection to pod`; สาขา b ขายต่อได้; เหลือ 1 Pod ไม่มีใครสร้างคืน; apply a → Pending → `uncordon` → Running **7 วิ** ออเดอร์เริ่มที่ 0
5. ✅ NotReady 43 วิ; som-shop-b Terminating ที่ NotReady + 61 วิ; ระหว่างนั้นสั่งซื้อที่สาขา a ได้ปกติ (`{"ok":true,...}`)
6. ✅ `docker start` → Ready 2 วิ, IP เดิม, som-shop-b หาย 5 วิ, kindnet/kube-proxy Running (RESTARTS สะสม), apply b ใหม่ได้ (ออเดอร์ 0) → ไม่ต้องใช้แผนสำรอง `k8s-down && k8s-up`
7. ทรัพยากร: requests ที่ scheduler นับต่อสาขา = **200m CPU / 448Mi** (db sidecar 100m/256Mi + web 100m/192Mi; init ปกติเล็กกว่า) — node ที่มี 1 สาขา + kindnet: `cpu 300m, memory 498Mi` (limits 1 CPU / 1Gi) น้อยกว่าที่แผนประเมิน (~520m/1Gi); หน่วยความจำจริงของ node container: lab-worker ~391MiB, control-plane ~758MiB
8. ✅ apply ระหว่าง Terminating → `pod/som-shop-b configured` + `Warning: Detected changes to resource som-shop-b which is currently being deleted.` (ไม่ใช่ AlreadyExists, ไม่มี Pod ใหม่)
- ✅ ssh -L จากเครื่อง agent ผ่าน gateway 172.18.0.1:2224 (askpass) → curl `localhost:13001` / `13002` ได้หน้าเว็บ "สาขา lab-worker" / "สาขา lab-worker2" และ `/som.png` 200; POST `/api/orders` ที่สาขา a 2 ครั้ง → stock 20→18 และกล่องสถิติ a = 2 / b = 0 (db แยก)
- ✅ บล็อกเก็บกวาด (`pkill`, `delete pod -l app=som-shop`, `label ... shop-`) ทำงานถูก

## การเปลี่ยนแปลงจากแผน

1. `lab03-node-labels/affinity-preferred-pod.yaml` มี 4 Pod (`prefer-1..4`, label `group=prefer`) เพื่อดูสัดส่วนจริงตามที่แผนให้ทดสอบ 3–5 ตัว; เพิ่มการทดลอง "ไม่มีเรือ fast" (`fleet=eco --overwrite` ทั้งสองลำ) ให้เห็นว่า preferred ยัง Running แต่ nodeSelector Pending
2. `lab04-pod-affinity/crew-preferred-pods.yaml` ใช้ชื่อ `deckhand-1..3` label `team=deckhand` (ไม่ใช้ `team=crew` เพื่อไม่ให้ไปชนกฎ required anti ของ crew)
3. `lab05-topology-spread/spread-honor-pods.yaml` ใช้ชื่อ `honor-1..4` label `group=honor` → apply ต่อจากไฟล์ Ignore ได้ทันทีและเห็นเปรียบเทียบในตารางเดียว (ไม่ต้องลบก่อน)
4. LAB7: Pod ใหม่หลัง cordon ใช้ `kubectl run late-cargo --image=nginx:1.27-alpine -l lab=03` (ไม่มีไฟล์); `pantry` (emptyDir) ปักที่ lab-worker ด้วย nodeSelector; `cargo-1..4` กระจายด้วย spread Honor (ได้ 2+2 จริง)
5. LAB1 ทางแก้ huge-pod: `kubectl delete pod huge-pod --now` แล้ว `sed "s/4000Gi/256Mi/" labs/lab01-scheduler/huge-pod.yaml | kubectl apply -f -` (ไม่แก้ไฟล์ต้นฉบับ) — **ค้นพบเพิ่ม**: K8s 1.37 `kubectl patch pod huge-pod --subresource resize -p '{"spec":{"containers":[{"name":"app","resources":{"requests":{"memory":"256Mi"}}}]}}'` ใช้กับ Pod ที่ Pending ได้และ scheduler วางให้ทันที (ใส่เป็นกล่อง "รู้ไว้" ได้ แต่ทางหลักยังเป็นลบ + สร้างใหม่)
6. LAB2: ghost-node-pod ถูก PodGC ลบเองที่ ~62 วิ → ให้ README บอก "ดูภายใน 1 นาที" และใช้เป็นจุดสอน
7. LAB6: vip-pod ถูกไล่พร้อม no-pass เมื่อใส่ `maintenance=true:NoExecute` → README ต้องบอกผลนี้ (เป็นตัวอย่างเพิ่มว่า NoExecute ไล่ทุก Pod ที่ไม่มีบัตร)
8. LAB9: `static-snack.yaml` **ไม่ใส่ label `lab=03`** (กัน `kubectl delete pod -l lab=03` ไปลบ mirror pod แล้วค้าง ~1 นาที); `mkdir -p` ไม่จำเป็น (โฟลเดอร์มีอยู่แล้ว) แต่คงไว้ไม่เสียหาย; `kubectl delete` mirror pod ให้ใช้ `--wait=false` แล้วดู `kubectl get pod -w` (ไม่งั้นคำสั่งค้าง ~1 นาที)
9. LAB8: ทดลองเสริม "เรือกลับก่อนครบเวลา" (stop → NotReady → +10 วิ → start) ได้ผล RESTARTS 1 + IP เปลี่ยน — แนะนำใส่ใน README เป็นข้อสังเกต
10. LAB10: ข้อความ FailedScheduling ของ som-shop-c ต่างจากแผน (ดูข้อ 3 ด้านบน); `<title>` เปลี่ยนตามสาขา (แผนคาดว่าอาจไม่เปลี่ยน); ครั้งหนึ่งที่ apply ใหม่ scheduler วาง a→lab-worker2, b→lab-worker (สลับ) — README ต้องให้หา node ด้วย `kubectl get pod som-shop-a -o jsonpath={.spec.nodeName}` (คำสั่งที่ใช้ทดสอบ: `NODE_A=$(...)`, `NODE_B=$(...)`)
11. แอป `som-shop-branches/app` คัดลอกจากบท 002 โดยไม่แก้โค้ด (ไม่รวม node_modules/.next/.env) — หน้าเว็บยังมีข้อความ footer `Next.js + PostgreSQL · Kubernetes LAB 002` และ eyebrow `⚓ ท่าเรือ Kubernetes · Pod เดียวครบทั้งร้าน` (ถ้าต้องการให้ภาพหน้าจอบอกบท 003 ต้องแก้ `app/page.tsx` เอง)
12. สภาพ handoff จัดให้ a อยู่ lab-worker, b อยู่ lab-worker2 (ใช้ `cordon lab-worker2` ชั่วคราวตอน apply a) และสั่งซื้อที่ a ไว้ 2 ออเดอร์ ให้ตรงภาพ L14/L19

## ป้าย/ข้อความในภาพ storyboard ที่ไม่ตรงผลจริง (เทียบ images.json "Text (verbatim")

| ภาพ | ป้ายเดิม | ผลจริง | ค่าที่ควรใช้แทน |
|---|---|---|---|
| L12 | `NotReady ~40-50s` | วัดได้ 43, 44, 50 วิ | `NotReady ~45-50s` (หรือคงไว้ได้ ยังครอบคลุม 43–50) |
| L12 | `fog-fast: +30s`, `fog-default: +300s` | นับจาก **NotReady** ไม่ใช่จาก docker stop (จาก stop = ~73 วิ / ~345 วิ) | `fog-fast: NotReady+30s`, `fog-default: NotReady+300s` หรือวาง marker ต่อจาก NotReady ให้ชัด |
| L19 | `ออเดอร์: 2`, `ออเดอร์: 0` | หน้าเว็บแสดงตัวเลขใหญ่ + ป้าย `ออเดอร์ทั้งหมด` (2 / 0) และ tab title = ชื่อสาขา | `ออเดอร์ทั้งหมด 2`, `ออเดอร์ทั้งหมด 0` |
| L21 (caption) | "สาขา b ถูกไล่ออกหลัง 60 วินาที" | Terminating ที่ NotReady + 61 วิ (≈104 วิหลัง docker stop) | "หลัง NotReady 60 วินาที" |
| L10 (caption) | "drain ด้วย --ignore-daemonsets --force" | ใน LAB7 มี pantry (emptyDir) ต้องใส่ `--delete-emptydir-data` ด้วย ไม่งั้น error | caption: "drain ด้วย --ignore-daemonsets --delete-emptydir-data --force" (ป้าย `kubectl drain --force` ใช้ได้) |
| L04 | `บนเรือ lab-worker` | whereami ถูก scheduler วางที่ lab-worker2 ในรอบทดสอบ (สุ่มได้ทั้งสองลำ) | ใช้ได้ถ้าเข้าใจว่าเป็นตัวอย่าง หรือเปลี่ยนเป็น `บนเรือ lab-worker2` ให้ตรง log |
| L09 | ฉากมี 3 Pod บน lab-worker2 | vip-pod (จาก LAB6 ช่วงแรก) ก็อยู่บน lab-worker2 และถูกไล่ทันทีด้วย | ไม่ต้องแก้ป้าย; README ให้ลบ vip-pod ก่อนใส่ NoExecute หรืออธิบายว่าถูกไล่ด้วย |

ภาพอื่น (T20, L01–L03, L05–L08, L11, L13–L18, L20, L22) ป้ายตรงผลจริง: T20 Ignore → Pending / Honor ✓, `crew-3: Pending` ✓ (crew-3 เป็นตัวที่ Pending จริง), `2 : 2` ✓, `node.kubernetes.io/unreachable` ✓, `static-snack-lab-worker` ✓, `som-shop-c: Pending` ✓, `image-archive` ✓, `som-shop-b: Terminating` ✓

## ข้อควรระวังสำหรับนักศึกษา (ใส่ใน README)

- **คำสั่ง `docker stop/start lab-worker2`, `docker exec lab-worker ...`, `docker cp ... lab-worker:` ต้องพิมพ์ใน SSH session ของ k8s-lab** ไม่ใช่ PowerShell/Terminal ของเครื่องตัวเอง
- หลัง LAB8 และ LAB10 ขั้น 10–11 ต้อง `docker start lab-worker2` แล้วรอ `kubectl get nodes` เป็น Ready ทุกตัว (จริง 2 วิ, taint หายใน ~10 วิ) ก่อนไป LAB ถัดไป ถ้าไม่กลับภายใน 2 นาที: `docker ps -a` ดูว่า container ขึ้นหรือยัง แล้วค่อย `k8s-down && k8s-up` + load image ใหม่ (ทดสอบแล้วไม่จำเป็น)
- อย่า `docker stop lab-control-plane` (คลัสเตอร์ทั้งหมดใช้ไม่ได้)
- NotReady ใช้เวลา ~45–50 วิ, Pod ที่ default 300 วิจะถูกไล่หลัง NotReady อีก 5 นาที → LAB8 ใช้เวลารวม ~6–7 นาที ระหว่างรอทำอย่างอื่นได้; Pod ที่ถูกไล่บนเรือที่ล่มจะ **ค้าง `Terminating`** จนเรือกลับ (ไม่ใช่ error ของเรา) และ STATUS ช่วงแรกยังเป็น `Running 1/1` ทั้งที่เรือล่ม
- ระหว่างเรือล่ม `kubectl exec/logs/port-forward` ไป Pod บนเรือนั้นจะ error `dial tcp 172.19.0.x:10250: connect: no route to host` — ปกติ
- `kubectl delete` mirror pod (LAB9) จะค้าง ~1 นาที ให้ใช้ `--wait=false` หรือกด Ctrl+C ได้ และอย่าลืม `rm` ไฟล์ใน `/etc/kubernetes/manifests` ตอนเก็บกวาด (ไม่งั้น static-snack อยู่ตลอด แม้ restart)
- drain ที่ error ก็ **cordon node ไปแล้ว** — ต้อง `uncordon` ทุกครั้งที่ทดลอง drain
- port-forward ผูกกับ Pod: Pod ถูก drain/evict/ลบ หรือเรือล่ม → `error: lost connection to pod` ต้องรันใหม่หลังมี Pod ใหม่
- scheduler อาจวาง som-shop-a ที่ lab-worker2 ก็ได้ ให้ดู NODE จาก `kubectl get pod -o wide` ก่อน drain/stop (อย่าจำตามภาพ)
- ถ้าจะ `pkill -f` ใน script/`bash -c` ให้ใช้ pattern แบบ `"[k]ubectl port-forward"` กัน pattern ไปตรงกับ command line ของ shell ตัวเอง (ในการทดสอบนี้ `pkill -f "ssh -f -N ..."` ฆ่า shell ที่สั่งเองไปหนึ่งครั้ง) — ใน shell ปกติแนะนำ Ctrl+C หน้าต่าง port-forward ง่ายกว่า
- nodeTaintsPolicy default = Ignore → spread บน kind ต้องตั้ง `Honor` (หรือ nodeAffinity เลือก worker) ไม่งั้น Pod ตัวที่ 3 Pending
- requests ใหญ่ ๆ ของ LAB1 (`4000Gi`) เกินทุกเครื่องแน่นอน แต่ node ใน kind เห็น CPU/RAM เท่าเครื่องจริงทุก node (allocatable = capacity) — 3 node ไม่ได้มีทรัพยากร 3 เท่า
- image `nginx:1.27-alpine`, `busybox:1.36` ถูก pull ครั้งแรกบนแต่ละ node (~6 วิ) — ถ้าคลัสเตอร์สร้างใหม่ (`k8s-up` ใหม่) ต้อง build/load `som-shop-web:1.0` และ postgres ใหม่ (ARM ใช้ `--platform linux/arm64`, ไม่ได้ทดสอบ)
- รหัส DB `meow1234` อยู่ใน YAML เพื่อการเรียนเท่านั้น

## สถานะ cleanup

- container `k8s-lab-nodepod003-211945` **ยังเปิดอยู่โดยตั้งใจ** (som-shop-a บน lab-worker + som-shop-b บน lab-worker2, port-forward 127.0.0.1:3001/3002 ใน container, SSH 2224) — ผู้ประสานงานลบเองด้วย `docker rm -fv k8s-lab-nodepod003-211945`
- ไม่ได้แตะ `k8s-lab` ของผู้เรียน และ `deep_vision_5090_vllm`; ไม่ได้ build/แตะ tag ของผู้ใช้บน host (build `som-shop-web:1.0` เฉพาะใน dockerd ของ container ทดลอง); ไม่ได้ใช้ `docker system prune`
- ssh tunnel ฝั่ง agent ปิดแล้ว; askpass และสคริปต์ช่วยใน `/tmp/k003` ลบแล้ว
