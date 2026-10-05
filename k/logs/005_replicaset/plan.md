# แผนบทเรียน 005 — Kubernetes ReplicaSet (หัวหน้ากะที่นับบูธให้ครบ)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB และยังไม่รัน LAB)
> แยกจากบทรวม `logs/005_rs_deploy_svc/` ตามสัญญา `logs/005_replicaset/scratch/split-contract.md` (บทถัดไป: 006 Service, 007 Deployment)
> Storyboard ภาพ: `logs/005_replicaset/images.json` (Theory 36 ภาพ T01–T36, LAB 20 ภาพ L01–L20, needs_test 16) สร้างจาก `logs/005_replicaset/build_images.py` (ใช้ `imgcommon.py` ร่วม) → ได้ `005_kubernetes_replicaset/01_Theory/images/imagegen-prompts.md`, `02_LAB/images/imagegen-prompts.md`, `image-sources.tsv`; ที่มาของภาพแต่ละภาพ: `README-split.md`
> ภาพตัวละครอ้างอิง: `005_kubernetes_replicaset/01_Theory/images/00-character-som.png`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่าน 001 (k8s-lab, kind `lab`: `lab-control-plane` / `lab-worker` / `lab-worker2`, K8s v1.37), 002 (Pod, YAML, labels, probes, multi-container/native sidecar, init container, ร้าน som-shop all-in-one), 003 (Node, scheduler, affinity/anti-affinity/topology spread, taints/tolerations + `tolerationSeconds` 300, cordon/drain, `docker stop lab-worker2`, Downward API), 004 (Namespace, ResourceQuota, LimitRange, RBAC, PSA, NetworkPolicy, `som-shop-web:1.1` + `SHOP_EYEBROW`/`SHOP_FOOTER`, port-forward หลุดเมื่อ Pod ถูกลบ)
- เข้าเครื่อง: `ssh -p 2223 root@localhost` (รหัส `passwd`) หรือ JupyterLab `http://localhost:8889`; คำสั่ง kubectl/kind/docker ทั้งหมดรัน 🐧 ใน SSH session ของ k8s-lab ยกเว้น `docker cp` และ `ssh -L` (🖥️ เครื่องนักศึกษา)
- โฟลเดอร์ LAB: `docker cp 005_kubernetes_replicaset k8s-lab:/workspace/` แล้ว `cd /workspace/005_kubernetes_replicaset/02_LAB`
- **ขอบเขต:** ReplicaSet เท่านั้น — **ห้ามใช้ Service (รวม `kubectl expose`), Deployment, `kubectl rollout` ในขั้นตอน LAB** (กล่าวชื่อเพื่อปูทางได้ในทฤษฎี/ปิดบท); การเข้าถึงแอปยังใช้ `kubectl exec`, `kubectl logs`, `kubectl port-forward pod/...` + `ssh -L` เหมือนบท 002–004
- ทุก LAB ทำใน namespace ของตัวเองและจบด้วย `kubectl delete ns ...`; busybox ใส่ `terminationGracePeriodSeconds: 1`; image สาธารณะ (`busybox:1.36`, `nginx:1.27-alpine`/`1.28-alpine`) ให้ Node pull เอง (pre-check #6); image ที่ build เองใช้ `kind load docker-image ... --name lab`; postgres ใช้ `docker save --platform linux/amd64 ... && kind load image-archive ...` (วิธีบท 004) หรือให้ Node pull เอง
- ข้อความ kubectl 1.37: `pod "x" deleted from <ns> namespace` (pre-check #4)

### ผล pre-check ที่เกี่ยวข้อง (คัดลอกจาก `logs/005_rs_deploy_svc/precheck.md` เลขข้อเดิม)

| # | คำถาม | ผลจริง | ผลต่อแผนบทนี้ |
|---|---|---|---|
| 2 | RS เจอ Pod หลงที่ label ตรง (สร้าง **หลัง** RS) | RS 3 ตัว + `stray` → RS ลบ `stray` ทันที (Event `SuccessfulDelete ... Deleted pod: stray` — ตัวที่ใหม่สุดถูกลบ) | T22, LAB4 ขั้น ก |
| 3 | Pod หลงที่มีอยู่ **ก่อน** สร้าง RS | RS ใหม่รับเลี้ยง: สร้างเพิ่มแค่ 2 ตัว, `stray.metadata.ownerReferences[0].name = snack-rs` | T21, LAB4 ขั้น ข |
| 4 | ลบ Pod ของ RS | ตัวใหม่ขึ้นภายใน ~3 วิ (ตัวเก่ายัง Terminating อยู่ก็สร้างแล้ว); ownerReferences `{"kind":"ReplicaSet","name":"snack-rs","controller":true,"blockOwnerDeletion":true}`; kubectl 1.37 พิมพ์ `pod "x" deleted from default namespace` | T12, T15, LAB1–2 |
| 6 | `kind load docker-image nginx:1.27-alpine` | **ล้มเหลว** `ctr: content digest sha256:...: not found` (multi-arch) แต่ Node ดึงเองได้ | LAB5 ไม่ kind load nginx; LAB9 kind load เฉพาะ som-shop-web |
| 26 | build `som-shop-web:1.1` ใน container | 28.6 วิ | LAB9 build ใหม่เฉพาะเมื่อคลัสเตอร์ใหม่/ไม่มี image บน Node |

ผลอื่นที่ยกมาจากบทก่อน (README จริงของบท 003/004): drain Pod เดี่ยวต้อง `--force` และ Pod หายไม่กลับ (003 LAB7); `docker stop lab-worker2` → NotReady ~45–50 วิ, toleration 30 วิถูกไล่ที่ NotReady+~30 วิ, ค่าเริ่มต้นที่ NotReady+~300 วิ, Pod ค้าง Terminating จนเรือกลับ (003 LAB8); quota error `exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3` และ LimitRange default requests 100m/64Mi limits 200m/128Mi (004 LAB5–6); PSA `Warning: would violate PodSecurity "restricted:latest": ...` (004 LAB8); port-forward ไป Pod ที่ถูกลบ → browser `ERR_CONNECTION_RESET` (004 LAB10)

### อุปมา (ต่อจากบท 001–004 + ของใหม่บทนี้)

| Kubernetes | อุปมาท่าเรือ | ใหม่? |
|---|---|---|
| container / Pod / Node / Control Plane / Namespace / label | ตู้สินค้า / กล่องใส teal มีป้าย IP (บทนี้คือ "บูธร้าน" มีกันสาด) / เรือ / หอบังคับการ / โซนทาสี / ป้ายห้อยกระเป๋าสี | – |
| controller + reconciliation loop | หุ่นยนต์ในหอที่วน "ดู → เทียบ → แก้" ไม่รู้จบ | ใหม่ |
| **ReplicaSet** | **หัวหน้ากะ** หุ่นยนต์กล่องสี teal ถือคลิปบอร์ดนับหัว | ใหม่ |
| selector | แว่นขยายส่องป้ายห้อย | ใหม่ |
| Pod template | แบบพิมพ์/พิมพ์เขียวที่ใช้ปั๊มบูธใหม่ | ใหม่ |
| ownerReferences | ป้ายเจ้าของ (badge) หนีบมุมบูธ โยงเชือกประกลับหาหัวหน้ากะ | ใหม่ |
| cascade / orphan | ลบหัวหน้ากะแล้วบูธหายตามเชือก / ตัดเชือกทิ้งบูธไว้ (ห้ามวาดน้ำตก/เด็กกำพร้า) | ใหม่ |
| ResourceQuota / LimitRange | เสาประตูนับช่องของโซน / เครื่องติดสติกเกอร์ขนาด (ห้ามวาดเงิน) | บท 004 |

ภาพบทนี้ห้ามมีประภาคาร/ผู้จัดการร้าน/คำว่า Service/Deployment (imgcommon ใส่ข้อห้ามให้) ยกเว้นภาพปูทาง T36 และ L20 (`allow=True`, วาดเป็นเงาจาง ๆ ที่ขอบฟ้า)

### เรื่องเล่า

ร้านอาหารแมวน้องส้มเปิดได้ 3 environment แล้ว (บท 004) แต่ทุกครั้งที่บูธหาย (ลบผิด ซ่อมเรือ เรือล่ม) ร้านปิดจนกว่าน้องส้มจะสร้างใหม่เอง น้องส้มจึงจ้าง **หัวหน้ากะ** ที่ถือคลิปบอร์ดนับบูธที่ติดป้ายของร้านตลอดเวลา ขาดก็ปั๊มจากแบบพิมพ์ เกินก็เก็บ น้องส้มได้เรียนรู้ว่าหัวหน้ากะ "นับจากป้าย ไม่ใช่จากชื่อ" (จึงรับเลี้ยงบูธแปลกหน้าและลบบูธที่เกินได้) รู้วิธีแยกบูธป่วยออกมาตรวจ วิธีปลดหัวหน้ากะโดยไม่ปิดบูธ และการทำงานร่วมกับงบโซน/ด่านความปลอดภัย/การกระจายบูธข้ามเรือ ปิดท้ายด้วย **ร้านน้องส้ม 3 บูธ** ที่ไม่ล้มแม้บูธหาย แต่ก็พบ 3 ปัญหาใหม่ — ออเดอร์แต่ละบูธไม่ตรงกัน ลูกค้าหาบูธไม่เจอเพราะชื่อ/IP เปลี่ยน และเปลี่ยนรุ่นต้องลบบูธเองทีละตัว → บท 006 (ประภาคาร = Service) และบท 007 (ผู้จัดการร้าน = Deployment)

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001–004: รายวิชา/หัวข้อ/CLO, บทก่อนหน้า (ลิงก์บท 004), บทคัดย่อ, วัตถุประสงค์การเรียนรู้ (~10 ข้อ), สารบัญ, ตารางอุปมา; output ทุกชิ้นในทฤษฎีใช้ผลจริงจาก pre-check/การรัน LAB (หลังทดสอบ)

1. **บทนำ: บูธเดี่ยวหาย ไม่มีใครสร้างใหม่** (T01–T03)
   - ทบทวน 3 ปัญหา: บท 002 ลบ Pod แล้วหายถาวร; บท 003 drain ต้อง `--force` แล้ว Pod เดี่ยวหาย ไม่ย้ายไปเรืออื่น, เรือล่มแล้ว Pod ถูกไล่หลัง 300 วิแต่ไม่มีใครสร้างแทน; บท 004 Pod ใหม่ได้ IP ใหม่ port-forward หลุด
   - Pod = หน่วยที่ "ตายแล้วไม่ฟื้น" (ไม่ย้าย ไม่ถูกสร้างแทน) → ต้องมีผู้ดูแลระดับสูงกว่า = workload controller; บทนี้แก้ "จำนวน" ส่วน "ที่อยู่คงที่" (บท 006) และ "เปลี่ยนรุ่น" (บท 007) ยังไม่แก้
   - ภาพรวมบท + ตารางอุปมา
2. **Controller และ reconciliation loop** (T04–T06)
   - declarative: เราเขียน `spec` (desired) ระบบรายงาน `status` (actual) controller วน observe → diff → act
   - level-triggered vs edge-triggered: ไม่ได้ "ทำตามเหตุการณ์" แต่ "ทำให้สภาพตรง" — พลาด event (controller รีสตาร์ต, ขาด watch) รอบถัดไปก็แก้ทัน; idempotent
   - controller อยู่ใน `kube-controller-manager` (static Pod ใน kube-system — เห็นในบท 001/003) ทำงานผ่าน kube-apiserver เท่านั้น (list + watch, informer cache, work queue) ไม่คุยกับ kubelet ตรง ๆ; ตัวอย่าง controller ที่รู้จักแล้ว: Node controller (NotReady + taint บท 003), Namespace controller (ลบของในโซนบท 004), ReplicaSet controller (บทนี้); leader election ด้วย Lease (กล่าวถึง)
3. **ReplicaSet manifest** (T07–T13)
   - 3.1 `apiVersion: apps/v1`, `kind: ReplicaSet`, `spec.replicas` (default 1), `spec.selector`, `spec.template` (= Pod spec บท 002 ทั้งก้อน ไม่มี `name`)
   - 3.2 ชื่อ Pod = `<ชื่อ RS>-<สุ่ม 5 ตัว>` (generateName) ตัวใหม่ได้ชื่อใหม่เสมอ; ชื่อ RS ยาวเกินถูกตัด (กล่าวถึง)
   - 3.3 selector: `matchLabels` (เท่ากับ) และ `matchExpressions` `In`/`NotIn`/`Exists`/`DoesNotExist` (AND กันทุกข้อ); ตัวอย่าง `tier In (snack, drink)`, `env NotIn (test)`, `track DoesNotExist`; เทียบ `kubectl get pods -l 'tier in (snack,drink)'` (set-based selector จากบท 002)
   - 3.4 template labels ต้องตรง selector ไม่งั้น apply ไม่ผ่าน (คาด `spec.template.metadata.labels: Invalid value: ...: \`selector\` does not match template \`labels\`` — **ยืนยันข้อความจริงใน LAB1**) เหตุผล: ถ้ายอมให้สร้าง RS จะปั๊ม Pod ที่ตัวเองนับไม่เห็นไม่รู้จบ; selector ว่างไม่ได้ใน apps/v1
   - 3.5 `metadata.ownerReferences` บน Pod (pre-check #4: `kind: ReplicaSet`, `name: snack-rs`, `controller: true`, `blockOwnerDeletion: true`, + `uid`, `apiVersion`) — Pod มี controller ได้ตัวเดียว
   - 3.6 status และคอลัมน์: `kubectl get rs` → `NAME DESIRED CURRENT READY AGE` (`-o wide` เพิ่ม CONTAINERS/IMAGES/SELECTOR); `status.replicas`, `readyReplicas`, `availableReplicas` (Ready ต่อเนื่องตาม `minReadySeconds`), `fullyLabeledReplicas` (Pod ที่มี label ครบตาม template), `observedGeneration`, `conditions` (ReplicaFailure); **ตรวจใน v1.37 ว่ามี `status.terminatingReplicas` (KEP-3973) แสดงหรือไม่**
4. **Self-healing** (T14–T17)
   - 4.1 ลบ Pod → นับได้ 2/3 → สร้างใหม่ (~3 วิ, pre-check #4) ขณะตัวเก่ายัง Terminating: RS ไม่นับ Pod ที่มี `deletionTimestamp` จึงมีช่วงที่ "Pod อยู่จริง" เกิน replicas ชั่วคราว (ข้อควรรู้สำหรับแอปที่ห้ามรันซ้อน)
   - 4.2 drain Node: Pod ของ RS ถูก evict แล้ว RS สร้างใหม่บนเรือที่เหลือ (scheduler ปกติ) ไม่ต้อง `--force` (เทียบบท 003 ที่ Pod เดี่ยวต้อง `--force` และหายไปเลย); uncordon แล้ว **Pod ไม่ย้ายกลับเอง** (ไม่มี rebalance)
   - 4.3 เรือล่ม (`docker stop lab-worker2`): NotReady หลัง ~45–50 วิ → taint `node.kubernetes.io/unreachable:NoExecute` → Pod มี toleration อัตโนมัติ `tolerationSeconds: 300` → ถูกไล่หลังครบเวลา (ค้าง Terminating เพราะ kubelet ตอบไม่ได้) → RS สร้างตัวแทนบนเรืออื่น; ร้านจริงอาจใส่ toleration `not-ready`/`unreachable` `tolerationSeconds: 30` ใน template ให้สร้างแทนเร็วขึ้น (แลกกับการย้ายบ่อยเมื่อเครือข่ายสะดุด) — **เวลาจริงยืนยันใน LAB2 ทางเลือก**
5. **Scale** (T18–T19)
   - `kubectl scale rs snack-rs --replicas=5`, แก้ `replicas` ในไฟล์แล้ว `kubectl apply -f` (วิธีที่ถูกเพราะไฟล์ = ความจริง), `kubectl edit rs snack-rs`, `scale --replicas=0` (หยุดชั่วคราวโดยไม่ลบ RS); `kubectl scale` ไม่แก้ไฟล์ → apply ไฟล์เดิมแล้วจำนวนกลับ (กับดัก)
   - ลำดับเลือก Pod ที่ถูกลบตอน scale ลง (ตาม ReplicaSet controller `ActivePodsWithRanks`): ยังไม่ได้ schedule ก่อน → Pending < Unknown < Running → ไม่ Ready ก่อน Ready → `controller.kubernetes.io/pod-deletion-cost` ต่ำกว่าก่อน → อยู่บน Node ที่มี replica เดียวกันมากกว่าก่อน → เพิ่ง Ready (เวลาสั้นกว่า, ปัดแบบ log scale) ก่อน → restart มากกว่าก่อน → สร้างใหม่กว่าก่อน — **ยืนยันใน LAB3/LAB9 ว่าเห็นตามนี้**; pre-check #2 สอดคล้อง (stray ใหม่สุดถูกลบ)
6. **กับดัก label** (T20–T24)
   - 6.1 RS นับจาก label ไม่ใช่ชื่อ/ประวัติ
   - 6.2 Pod เดี่ยวที่ label ตรงและ **ไม่มี owner** มีอยู่ก่อน → ถูกรับเลี้ยง (pre-check #3) RS สร้างเพิ่มแค่ 2 และ Pod ที่รับเลี้ยงอาจ image/สเปกต่างจาก template (ไม่มีใครแก้ให้)
   - 6.3 สร้าง Pod ที่ label ตรงหลัง RS ครบแล้ว → เกินจำนวน → ถูกลบทันที (pre-check #2)
   - 6.4 สอง RS selector ทับกัน: ownerReferences กันไม่ให้แย่ง Pod ที่มีเจ้าของแล้ว (RS นับเฉพาะ Pod ของตัวเอง + Pod ไร้เจ้าของที่ตรง) แต่ `kubectl get pods -l app=snack` เห็นปนกัน, Pod ไร้เจ้าของถูกตัวไหนรับไปก็ได้ → ออกแบบ selector ให้เฉพาะเจาะจง (เพิ่ม label เช่น `rs: snack-a`)
   - 6.5 เทคนิค debug: `kubectl label pod <ชื่อ> app-` (หรือ `--overwrite app=debug`) → Pod หลุดจาก selector, ownerReferences ถูกถอด (ยืนยัน), RS สร้างตัวแทน, Pod เดิมอยู่ต่อพร้อม log/สถานะให้ `exec`/`logs` — เสร็จแล้วลบเอง
7. **selector immutable และ template ใหม่ไม่เปลี่ยน Pod เดิม** (T25–T26)
   - apps/v1: แก้ `spec.selector` → `field is immutable` (ข้อความเต็มยืนยันใน LAB5); ต้องสร้าง RS ใหม่ (เช่น ลบแบบ orphan แล้วสร้างใหม่)
   - แก้ template (image/env) → RS เก็บ template ใหม่ แต่ไม่แตะ Pod ที่มีอยู่ (นับครบแล้ว ไม่มีอะไรต้องแก้) → ต้องลบ Pod เองทีละตัว ไม่มีการรอ Ready ก่อนลบตัวถัดไป ไม่มีประวัติ/ย้อนรุ่น → ปูทาง **Deployment (บท 007)** กล่าวชื่อเท่านั้น
8. **ลบ ReplicaSet: cascade vs orphan** (T27–T28)
   - `kubectl delete rs snack-rs` (`--cascade=background` ค่าเริ่มต้น: RS หายทันที garbage collector ลบ Pod ตาม), `--cascade=foreground` (RS ค้างด้วย finalizer `foregroundDeletion` จน Pod ที่ `blockOwnerDeletion` หายก่อน), `--cascade=orphan` (ถอด ownerReferences ออกจาก Pod แล้วลบ RS — Pod อยู่ต่อ)
   - Pod ที่เหลือ (ไร้เจ้าของ) + สร้าง RS ใหม่ selector ตรง → ถูกรับเลี้ยงโดยไม่สร้างเพิ่ม (ใช้เปลี่ยน selector/ชื่อ RS โดยไม่ปิดบูธ)
9. **ReplicationController (ประวัติสั้น)** (T29)
   - `v1` ReplicationController: selector แบบเท่ากับเท่านั้น; เคยเปลี่ยนรุ่นด้วย `kubectl rolling-update` ฝั่ง client (ถูกถอดออกจาก kubectl แล้ว) → แทนด้วย ReplicaSet + Deployment; ยังมี API ให้ใช้ได้แต่ไม่ควรสร้างใหม่
10. **ReplicaSet ใน namespace: quota, LimitRange, PSA** (T30–T31)
    - ResourceQuota ตรวจที่การสร้าง **Pod** ไม่ใช่ RS: quota `pods: 4` + replicas 6 → RS ถูกสร้าง, Pod ได้ 4, ที่เหลือ Event `FailedCreate` (`Error creating: pods "quota-rs-xxxxx" is forbidden: exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4` — คาด, ยืนยันใน LAB7), condition `ReplicaFailure=True reason FailedCreate`, `DESIRED 6 CURRENT 4`; RS พยายามซ้ำ (backoff) — เพิ่ม quota แล้วสร้างต่อเอง (ยืนยันเวลา)
    - LimitRange เติม requests/limits ให้ Pod ที่ RS สร้าง (annotation `kubernetes.io/limit-ranger`) — template ไม่ต้องมี resources ก็ผ่าน quota ที่บังคับ requests/limits
    - PSA: `warn`/`audit` ตรวจ Pod template ของ workload ตั้งแต่ตอนสร้าง RS (เตือนที่ kubectl), `enforce` ตรวจเฉพาะ Pod → RS ถูกสร้างสำเร็จแต่ Pod ถูกปฏิเสธ `FailedCreate ... violates PodSecurity "restricted:latest"` → `0/3` ต้องดู `describe rs` (ยืนยันใน LAB7 ทางเลือก)
11. **ReplicaSet กับการจัดวาง** (T32–T33)
    - ทบทวนบท 003: podAntiAffinity กับ label ของ Pod ตัวเอง (`app=snack`) + `topologyKey: kubernetes.io/hostname`
    - required: 2 worker + replicas 3 → Pod ที่ 3 `Pending` (`FailedScheduling ... didn't match pod anti-affinity rules` + control-plane taint) — RS ไม่ "แก้" Pending ให้ (นับว่ามีแล้ว)
    - preferred: กระจายเท่าที่ทำได้ 2+1; topologySpreadConstraints `maxSkew: 1`, `whenUnsatisfiable: DoNotSchedule` → 2+2, 3+2; scheduler จัดเฉพาะตอนสร้าง Pod (scale ลง/Node กลับมาไม่ rebalance — กล่าวถึง descheduler)
12. **ข้อควรรู้: Pod จาก RS ไม่มีชื่อคงที่และ IP คงที่** (T34)
    - ตัวแทนได้ชื่อใหม่ IP ใหม่; port-forward/IP ที่จดไว้ใช้ไม่ได้ → ต้องมีที่อยู่คงที่ที่ตามหา Pod ด้วย label เหมือน RS (ปูทาง **Service บท 006**)
    - ข้อมูลใน emptyDir หายพร้อม Pod (ร้าน all-in-one แต่ละบูธมี db ของตัวเอง) → ปูทางแยก db (บท 006) และ volume ถาวร (บทหลัง)
13. **สรุป + ตารางคำสั่ง + ปิดบท** (T35–T36)
    - ตารางคำสั่ง: `get rs [-o wide]`, `describe rs`, `scale rs`, `edit rs`, `get pods -l ... --show-labels`, `get pod -o jsonpath='{.metadata.ownerReferences}'`, `label pod x app-`, `delete rs --cascade=orphan|foreground`, `get pods -o custom-columns=...`, `get pods -w`
    - ตารางเทียบ Pod เดี่ยว vs ReplicaSet (ลบ/drain/เรือล่ม/scale/เปลี่ยนรุ่น)
    - ปิดบท: 3 ปัญหาจาก LAB9 → บท 006 Service (ชื่อ/ที่อยู่คงที่, แยก db) และบท 007 Deployment (เปลี่ยนรุ่นทีละบูธ ย้อนรุ่นได้) — "ในงานจริงแทบไม่สร้าง ReplicaSet เอง แต่ต้องเข้าใจเพราะ Deployment สร้างมันให้"

## 2. รายการ LAB (`02_LAB/README.md`)

```text
005_kubernetes_replicaset/02_LAB/
  README.md
  images/ (L01–L20 + imagegen-prompts.md, screenshots/)
  labs/
    lab00-lonely/lonely-pod.yaml                     (busybox Pod เดี่ยว ns rs-lab)
    lab01-first-rs/00-ns.yaml                        (ns rs-lab)
    lab01-first-rs/snack-rs.yaml                     (busybox:1.36, replicas 3, app=snack, grace 1, requests 10m/16Mi)
    lab01-first-rs/snack-rs-bad-labels.yaml          (template label app=snak)
    lab01-first-rs/snack-rs-expr.yaml                (matchExpressions tier In (snack,drink) + track DoesNotExist)
    lab02-self-heal/snack-rs-fast-evict.yaml         (snack-rs + tolerations not-ready/unreachable 30 วิ — ทางเลือก)
    lab04-label-trap/stray-pod.yaml                  (Pod stray label app=snack, image busybox แต่ command ต่าง)
    lab04-label-trap/snack-rs-b.yaml                 (RS ตัวที่สอง selector app=snack ทับกัน — ทางเลือก)
    lab05-template/web-rs.yaml                       (nginx:1.27-alpine เขียน index "web $VERSION from $(hostname)", VERSION=v1, readiness / period 2)
    lab05-template/web-rs-v2.yaml                    (image nginx:1.28-alpine + VERSION=v2)
    lab05-template/web-rs-new-selector.yaml          (selector เพิ่ม tier=front)
    lab07-quota/00-ns-quota.yaml                     (ns rs-quota + ResourceQuota rs-quota pods: "4" + LimitRange แบบบท 004)
    lab07-quota/quota-rs.yaml                        (busybox replicas 6 ไม่มี resources)
    lab07-quota/psa-rs.yaml                          (ns rs-psa enforce+warn restricted + RS busybox ไม่มี securityContext — ทางเลือก)
    lab08-spread/00-ns.yaml                          (ns rs-spread)
    lab08-spread/spread-required.yaml                (replicas 3 required anti-affinity)
    lab08-spread/spread-preferred.yaml               (replicas 3 preferred)
    lab08-spread/spread-topology.yaml                (replicas 4 topologySpreadConstraints maxSkew 1 DoNotSchedule)
  som-booths/
    k8s/00-namespace.yaml                            (ns som-booths, warn=restricted)
    k8s/som-booth.yaml                               (ReplicaSet som-booth replicas 3)
    k8s/som-booth-promo.yaml                         (เหมือน som-booth.yaml ต่างที่ image 1.1-promo + SHOP_EYEBROW โปร)
```

LAB3, LAB6 ใช้ `lab01-first-rs/snack-rs.yaml` ซ้ำ; LAB0–LAB6 ใช้ ns `rs-lab` (ลบตอนท้าย LAB6); แอปของ LAB9 **ไม่คัดลอก** — อ้างโฟลเดอร์บท 004 `som-shop-envs/app` (image 1.1 ไม่เปลี่ยน, ลดสำเนาซ้ำ) ถ้า `/workspace/004_kubernetes_namespace` ไม่มีให้ `docker cp` บท 004 เข้าไปก่อน

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ |
|---|---|---|---|---|---|---|
| 0 | เตรียม + ทบทวน Pod เดี่ยวหายถาวร + ดู kube-controller-manager | คลัสเตอร์พร้อม ไม่มีของค้าง เห็นว่า Pod เดี่ยวไม่มีใครดูแล และ controller อยู่ที่ไหน | `lab01-first-rs/00-ns.yaml`, `lab00-lonely/lonely-pod.yaml` | `kubectl get nodes`; `kubectl get pods -A -o wide --field-selector spec.nodeName=lab-worker2` (ต้องไม่มี Pod เดี่ยวค้างจากบทก่อน); `kubectl apply -f`; `kubectl delete pod lonely -n rs-lab`; `kubectl get pods -n rs-lab` (No resources); `kubectl get pods -n kube-system -l component=kube-controller-manager -o wide`; `kubectl -n kube-system get pod kube-controller-manager-lab-control-plane -o jsonpath='{.spec.containers[0].command}' \| tr ',' '\n' \| grep controllers` | 3 Node Ready; `pod "lonely" deleted from rs-lab namespace` แล้วไม่มีอะไรเกิดใหม่; controller-manager รันบน lab-control-plane, `--controllers=*,bootstrapsigner,tokencleaner` | node ไม่มี SchedulingDisabled/taint ค้างจากบท 003; ชื่อ static Pod และค่า `--controllers` จริง; leftover ns ของบท 004 |
| 1 | ReplicaSet แรก | เห็นโครง RS, ชื่อ Pod, ownerReferences, Events, เงื่อนไข label | `snack-rs.yaml`, `snack-rs-bad-labels.yaml`, `snack-rs-expr.yaml` | `kubectl apply -f lab01-first-rs/snack-rs.yaml`; `kubectl get rs,pods -n rs-lab -o wide --show-labels`; `kubectl get pod <ชื่อ> -n rs-lab -o jsonpath='{.metadata.ownerReferences}'`; `kubectl describe rs snack-rs -n rs-lab` (Events); `kubectl get rs snack-rs -n rs-lab -o jsonpath='{.status}'`; `kubectl apply -f snack-rs-bad-labels.yaml`; `kubectl apply -f snack-rs-expr.yaml` + `kubectl get pods -l 'tier in (snack,drink)'` แล้วลบ | `snack-rs 3 3 3`; ชื่อ `snack-rs-xxxxx`; ownerReferences ตาม pre-check #4; Events `SuccessfulCreate` 3 บรรทัด; status มี replicas/readyReplicas/availableReplicas/fullyLabeledReplicas; bad-labels ถูกปฏิเสธ | ข้อความ error เต็มของ template ไม่ตรง selector; มี `terminatingReplicas` ใน status ไหม; Events ระบุชื่อ Pod |
| 2 | Self-healing | ลบ Pod/ลบหลายตัว/ drain / (ทางเลือก) เรือล่ม แล้ว RS สร้างแทน | `snack-rs.yaml`, `lab02-self-heal/snack-rs-fast-evict.yaml` | terminal 2: `kubectl get pods -n rs-lab -o wide -w`; `kubectl delete pod <หนึ่งตัว> -n rs-lab --wait=false`; `kubectl delete pod -n rs-lab -l app=snack --wait=false`; `kubectl drain lab-worker2 --ignore-daemonsets` (ไม่ต้อง `--force`); `kubectl get pods -o wide`; `kubectl uncordon lab-worker2`; ทางเลือก: `kubectl apply -f snack-rs-fast-evict.yaml` (แทนตัวเดิม → ลบ Pod ให้ได้ template ใหม่) แล้ว 🐧 `docker stop lab-worker2` + ลูปดูเวลา → `docker start lab-worker2` | ตัวใหม่เกิดใน ~3 วิขณะตัวเก่า Terminating; ลบทั้งหมดแล้วได้ 3 ตัวใหม่; drain สำเร็จโดยไม่ต้อง `--force` Pod บน lab-worker2 ไปเกิดบน lab-worker, uncordon แล้ว Pod ไม่ย้ายกลับ; ทางเลือก: NotReady ~50 วิ + 30 วิ → Pod เก่า Terminating ค้าง ตัวแทนเกิดบน lab-worker | เวลา drain และเวลาเกิดใหม่; drain ติดเพราะ Pod อื่นค้างไหม; เวลาจริงของ docker stop → ตัวแทน (คาด ~80 วิ); Pod เก่าค้าง Terminating จนเรือกลับ; `get rs` ระหว่างนั้นแสดง READY เท่าไร |
| 3 | Scale | scale 3 วิธี + scale 0 + ดูว่าตัวไหนถูกลบ | `snack-rs.yaml` | `kubectl scale rs snack-rs -n rs-lab --replicas=5`; `kubectl get pods -o wide --sort-by=.metadata.creationTimestamp`; `kubectl scale ... --replicas=2` + `describe rs` (Events `SuccessfulDelete`); แก้ `replicas: 4` ในไฟล์ (`sed -i`) + `apply`; `KUBE_EDITOR=nano kubectl edit rs snack-rs -n rs-lab`; `--replicas=0` แล้ว `get rs` (`0 0 0`) และ RS ยังอยู่; `apply -f snack-rs.yaml` (กลับเป็นค่าในไฟล์) | จำนวนเปลี่ยนทันที; scale ลงลบตัวใหม่กว่า/ตัวบนเรือที่มี replica มากกว่าก่อน; apply ไฟล์เดิมทับค่าที่ scale ไว้ | ลำดับ Pod ที่ถูกลบจริง (5→2 อาจไม่ใช่ "ใหม่สุด 3 ตัว" เพราะเกณฑ์ Node แออัด); editor ใน k8s-lab (nano/vi) |
| 4 | กับดัก label | รับเลี้ยง/ลบตัวเกิน/selector ทับ/ถอด label debug | `lab04-label-trap/stray-pod.yaml`, `snack-rs-b.yaml` | (ก) RS ครบ 3 → `apply stray-pod.yaml` → `get pods`, `describe rs` (ข) `kubectl delete rs snack-rs` → `apply stray` → `apply snack-rs` → `get pods`, ownerReferences ของ stray, `kubectl exec stray -- ...` เห็นว่า command ต่างจาก template (ค) ทางเลือก `apply snack-rs-b.yaml` → `get rs` (snack-rs-b สร้างของตัวเอง 3 ตัว), `get pods -l app=snack` 6 ตัว ปน; ลบ snack-rs-b (ง) `kubectl label pod <ตัวหนึ่ง> app-` → `get pods --show-labels`, ownerReferences ของตัวนั้น, `logs`; ลบตัวนั้นเอง | (ก) `Deleted pod: stray` (ข) สร้างเพิ่มแค่ 2, stray มี owner snack-rs (ค) แต่ละ RS นับ 3 ของตัวเอง ไม่แย่งกัน (ง) RS สร้างตัวแทน, Pod ที่ถอด label ไม่มี ownerReferences และยังรัน | (ค) พฤติกรรมจริงของ selector ทับกัน (Pod ไร้เจ้าของ/การนับ); (ง) ownerReferences ถูกถอดจริงหรือไม่ และใช้เวลาเท่าไร |
| 5 | selector immutable + template ใหม่ Pod เดิมไม่เปลี่ยน | เห็นข้อจำกัดของ RS ในการเปลี่ยนรุ่น | `lab05-template/web-rs.yaml`, `web-rs-v2.yaml`, `web-rs-new-selector.yaml` | `apply web-rs.yaml`; `kubectl exec <pod> -- wget -qO- localhost`; `apply web-rs-new-selector.yaml` (ล้ม); `apply web-rs-v2.yaml`; `kubectl get pods -n rs-lab -l app=web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,VERSION:.spec.containers[0].env[0].value`; `kubectl get rs web -o wide` (IMAGES เป็น 1.28); ลบ Pod 1 ตัว → custom-columns อีกครั้ง | selector → `field is immutable`; หลัง apply v2 Pod เดิมยัง `nginx:1.27-alpine`/v1 ทุกตัว; ตัวที่เกิดใหม่เป็น `nginx:1.28-alpine`/v2 และ wget ตอบ `web v2 from web-xxxxx` | ข้อความ error เต็มของ selector; เวลา pull nginx:1.28 บน Node; custom-columns ของ env |
| 6 | ลบ RS: cascade vs orphan + RS ใหม่รับเลี้ยง | เข้าใจ garbage collector และการเปลี่ยน RS โดยไม่ปิด Pod | `snack-rs.yaml` | `kubectl delete rs snack-rs -n rs-lab --cascade=orphan`; `get rs,pods`; ownerReferences (ว่าง); `apply snack-rs.yaml` → `get pods` (ไม่มีตัวใหม่) + ownerReferences กลับมา (uid ใหม่); `kubectl delete rs snack-rs --cascade=foreground` + terminal 2 `kubectl get rs snack-rs -o jsonpath='{.metadata.finalizers}' -w`; เก็บกวาด `kubectl delete ns rs-lab` | orphan: Pod 3 ตัวอยู่ต่อ ไม่มี owner; RS ใหม่ `3 3 3` โดยไม่มี `SuccessfulCreate`; foreground: เห็น finalizer `foregroundDeletion` ชั่วครู่ RS หายหลัง Pod | finalizer foreground เห็นทันไหม (busybox grace 1 วิอาจเร็วมาก — ถ้าไม่ทันให้เพิ่ม grace เป็น 10 ใน LAB นี้); uid ใหม่ใน ownerReferences |
| 7 | RS กับ quota/LimitRange/PSA (ต่อบท 004) | เห็นว่า quota/PSA ตรวจที่ Pod ไม่ใช่ RS | `lab07-quota/00-ns-quota.yaml`, `quota-rs.yaml`, `psa-rs.yaml` | `apply 00-ns-quota.yaml`; `apply quota-rs.yaml`; `get rs,pods -n rs-quota`; `describe rs quota-rs` (Events, Conditions); `describe quota -n rs-quota`; `get pod <ตัวหนึ่ง> -o jsonpath='{.spec.containers[0].resources}'`; `kubectl patch resourcequota rs-quota -n rs-quota -p '{"spec":{"hard":{"pods":"6"}}}'` แล้ว `get rs -w`; ทางเลือก PSA: `apply psa-rs.yaml` → Warning, `get rs` `3 0 0`, `describe rs` FailedCreate; เก็บกวาด `kubectl delete ns rs-quota rs-psa` | `DESIRED 6 CURRENT 4`; Events `FailedCreate ... exceeded quota: rs-quota, requested: pods=1, used: pods=4, limited: pods=4`; condition `ReplicaFailure True FailedCreate`; resources ได้ค่า default 100m/64Mi–200m/128Mi; เพิ่ม quota แล้วครบ 6; PSA: Warning ตอน apply RS, Pod ถูกปฏิเสธ | ข้อความ Event/condition จริง; เวลาที่ RS สร้างต่อหลังเพิ่ม quota (backoff); PSA: ข้อความ Warning ตอนสร้าง RS (ระดับ workload) และข้อความ FailedCreate |
| 8 | กระจาย replica (ต่อบท 003) | ใช้ anti-affinity/topology spread กับ replicas | `lab08-spread/*.yaml` | `apply spread-required.yaml` → `get pods -o wide` + `describe pod <Pending>`; ลบแล้ว `apply spread-preferred.yaml` → 2+1; `apply spread-topology.yaml` → 2+2 → `scale --replicas=5` → 3+2; เก็บกวาด `kubectl delete ns rs-spread` | required: 2 Running คนละเรือ + 1 `Pending` `FailedScheduling 0/3 nodes are available: 1 node(s) had untolerated taint ..., 2 node(s) didn't match pod anti-affinity rules ...`; preferred: 2+1; topology: 2+2 แล้ว 3+2 | ข้อความ FailedScheduling เต็ม; preferred ได้ 2+1 ทุกครั้งไหม |
| 9 | LAB สุดท้าย: ร้านน้องส้ม 3 บูธด้วย ReplicaSet | รวมทุกอย่างกับแอปจริง และเห็นปัญหาที่ RS แก้ไม่ได้ | `som-booths/k8s/*` | ดูหัวข้อ 3 | ดูหัวข้อ 3 | ดูหัวข้อ 3.6 |

## 3. LAB สุดท้าย — "ร้านน้องส้ม 3 บูธด้วย ReplicaSet" (LAB9)

### 3.1 แนวคิด

- นำ Pod ร้าน all-in-one ของบท 004 (`som-shop.yaml`) มาเป็น **Pod template** ของ ReplicaSet `som-booth` replicas 3 → ร้านไม่ล้มเมื่อบูธหาย แต่ทุกบูธมี db (native sidecar + emptyDir) ของตัวเอง
- ตั้งใจให้นักศึกษาเห็น 3 ปัญหาด้วยตา (ส่งต่อบท 006/007): ออเดอร์ไม่ตรงกัน, ชื่อ/IP เปลี่ยนจน port-forward หลุด, เปลี่ยนรุ่นต้องลบเองทีละตัว
- ไม่สร้าง image ใหม่: ใช้ `som-shop-web:1.1` (อ่าน `SHOP_EYEBROW`/`SHOP_FOOTER`); หน้าเว็บมี "เสิร์ฟโดย Pod: <ชื่อ Pod>" อยู่แล้ว + ใส่ชื่อบูธที่ eyebrow; `1.1-promo` = `docker tag` ของ 1.1 (หน้าตาเหมือนเดิม ต่างที่ข้อความ eyebrow จาก env ใน template ใหม่)

### 3.2 สถาปัตยกรรม

```text
เครื่องนักศึกษา  browser  http://localhost:8081 / 8082 / 8083
     │ ssh -p 2223 -L 8081:localhost:8081 -L 8082:... -L 8083:...
k8s-lab   kubectl port-forward -n som-booths pod/<บูธ a> 8081:3000  (b → 8082, c → 8083)
     │
namespace som-booths  (pod-security.kubernetes.io/warn=restricted)
  ReplicaSet som-booth  replicas 3  selector app=som-booth
   ├─ Pod som-booth-xxxxx  (lab-worker)   web:3000 + db sidecar + emptyDir  ← ออเดอร์ของบูธนี้เท่านั้น
   ├─ Pod som-booth-yyyyy  (lab-worker2)  web + db + emptyDir
   └─ Pod som-booth-zzzzz  (lab-worker / lab-worker2)  ← preferred anti-affinity → 2+1
```

### 3.3 ไฟล์ manifest

- `00-namespace.yaml`: Namespace `som-booths` labels `pod-security.kubernetes.io/warn: restricted` (แบบ 004)
- `som-booth.yaml`: `apiVersion: apps/v1`, `kind: ReplicaSet`, `metadata.name: som-booth`, labels `app: som-booth`; `spec.replicas: 3`; `selector.matchLabels: {app: som-booth}`; `template.metadata.labels: {app: som-booth}`; `template.spec` = spec ของ `004/.../som-shop.yaml` ทั้งก้อน (securityContext restricted, emptyDir `db-data`, init `db` native sidecar postgres:17.11-alpine + probes, `wait-for-db`, `db-seed` som-shop-web:1.1, container `web` som-shop-web:1.1 + probes, resources เดิม) ต่างที่:
  - env ของ web: `POD_NAME` (Downward API `metadata.name`, ประกาศก่อน), `POD_NAMESPACE`, `SHOP_NAME="ร้านอาหารแมวน้องส้ม (หลายบูธ)"`, `SHOP_EYEBROW="⚓ บูธ $(POD_NAME)"`, `SHOP_FOOTER="Next.js + PostgreSQL · Kubernetes LAB 005 · ReplicaSet som-booth"`
  - `affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution` weight 100, labelSelector `app=som-booth`, topologyKey `kubernetes.io/hostname`
  - คอมเมนต์อธิบายว่าส่วนไหนมาจากบท 004 และ "template ไม่มี name"
- `som-booth-promo.yaml`: เหมือนกันทุกบรรทัด ยกเว้น image ของ `db-seed`/`web` = `som-shop-web:1.1-promo` และ `SHOP_EYEBROW="🎉 โปรบูธใหม่ · $(POD_NAME)"` (ให้ `diff som-booth.yaml som-booth-promo.yaml` เห็นแค่ 3 บรรทัด)
- **resource:** requests ต่อบูธ (effective) = max(init: wait-for-db+db 110m/272Mi, db-seed+db 150m/320Mi; หลัก: db+web 200m/448Mi) = **200m / 448Mi** → 3 บูธ 600m/1.3Gi, **5 บูธ 1 CPU / 2,240Mi (~2.2Gi)**, limits 5 บูธ 5 CPU/5Gi (overcommit ได้) — kind Node ทุกตัวรายงาน allocatable = ทรัพยากรของ WSL/เครื่องทั้งเครื่อง จึงมักจัดลงได้ แต่หน่วยความจำจริงอาจตึงบนเครื่อง RAM 8GB (WSL ได้ ~4GB) → ต้องยืนยัน; ทางออก: ถ้ามีบูธ `Pending` (`Insufficient memory/cpu`) หรือ k8s-lab ช้า/OOM ให้ใช้ `--replicas=4`

### 3.4 ขั้นตอน

1. **9.1 เตรียม image** (🐧): `docker exec lab-worker crictl images | grep -E "som-shop-web|postgres"`; ถ้าไม่มี 1.1 (คลัสเตอร์ใหม่) → `cd /workspace/004_kubernetes_namespace/02_LAB/som-shop-envs/app && docker build -q -t som-shop-web:1.1 .` + `kind load docker-image som-shop-web:1.1 --name lab`; postgres ตามบท 004 (`docker save --platform linux/amd64 ... && kind load image-archive ...`) หรือให้ Node pull; เตรียม promo ไว้เลย: `docker tag som-shop-web:1.1 som-shop-web:1.1-promo && kind load docker-image som-shop-web:1.1-promo --name lab` แล้ว `crictl images` ต้องเห็น tag `1.1-promo` (ถ้า kind แจ้ง image ID มีอยู่แล้วและไม่ re-tag → ทางสำรอง `docker build -q --label promo=true -t som-shop-web:1.1-promo .` ให้ได้ ID ใหม่แล้ว kind load ใหม่)
2. **9.2 เปิดร้าน**: `cd /workspace/005_kubernetes_replicaset/02_LAB/som-booths`; `kubectl apply -f k8s/00-namespace.yaml -f k8s/som-booth.yaml` (ไม่มี Warning PSA เพราะ template restricted แล้ว); terminal 2 `kubectl get pods -n som-booths -o wide -w` จน `2/2 Running` ทั้ง 3; `kubectl get rs -n som-booths` `3 3 3`; `kubectl logs -n som-booths <บูธ> -c db-seed` (`seeded 6 products`); ดูเรือ: 2+1
3. **9.3 port-forward ทีละบูธ**: `P=($(kubectl get pods -n som-booths -l app=som-booth -o jsonpath='{.items[*].metadata.name}'))`; `kubectl port-forward -n som-booths pod/${P[0]} 8081:3000 > /tmp/pf-8081.log 2>&1 &` (8082 → `${P[1]}`, 8083 → `${P[2]}`); ตรวจ `for p in 8081 8082 8083; do curl -s localhost:$p | grep -o "บูธ som-booth-[a-z0-9]*" | head -1; done`; 🖥️ `ssh -p 2223 -L 8081:localhost:8081 -L 8082:localhost:8082 -L 8083:localhost:8083 root@localhost`; 🌐 เปิด 3 แท็บ — หัวหน้าเว็บบอกชื่อบูธต่างกัน, "เสิร์ฟโดย Pod" ต่างกัน
4. **9.4 สั่งซื้อแล้วออเดอร์ไม่ตรงกัน**: กดสั่งซื้อที่แท็บ 8081 สองครั้ง (หรือ `curl -s -X POST localhost:8081/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'` ×2) → รีเฟรช 8082/8083 ออเดอร์ 0 และสต็อกเต็ม; `curl -s localhost:808{1,2,3}/api/orders` — "ร้านเดียวกันแต่ 3 สมุดออเดอร์"
5. **9.5 ลบบูธ a**: `kubectl delete pod -n som-booths ${P[0]}` → `-w` เห็นตัวใหม่ชื่อใหม่ IP ใหม่ (เรืออาจต่าง); `cat /tmp/pf-8081.log` (error/หลุด) + `jobs`; แท็บ 8081 รีเฟรชไม่ได้; port-forward ใหม่ไปบูธใหม่ที่ 8081 → ออเดอร์ 0 (emptyDir ใหม่)
6. **9.6 scale 3→5→2**: `kubectl scale rs som-booth -n som-booths --replicas=5` → `get pods -o wide` (3+2), `kubectl describe node lab-worker | grep -A8 "Allocated resources"`; ถ้า Pending → ใช้ 4; จากนั้น `--replicas=2` → ดูว่าบูธไหนถูกปิด (ใหม่กว่า/บนเรือที่แออัดก่อน) และ port-forward ไหนตาย (`jobs`, log)
7. **9.7 template ใหม่ (promo)**: `diff k8s/som-booth.yaml k8s/som-booth-promo.yaml`; `kubectl apply -f k8s/som-booth-promo.yaml`; `kubectl get rs som-booth -n som-booths -o wide` (IMAGES = 1.1-promo); `kubectl get pods -n som-booths -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName` → บูธเดิมยัง `som-shop-web:1.1` ทุกตัว; หน้าเว็บยังเป็น eyebrow เดิม
8. **9.8 ลบทีละตัวด้วยมือ**: ลบบูธหนึ่ง → รอ `kubectl wait --for=condition=Ready pod -l app=som-booth -n som-booths --timeout=120s` → port-forward ใหม่ → หน้าเว็บ "🎉 โปรบูธใหม่ · som-booth-..."; ลบตัวที่เหลือ; อภิปราย: ต้องรอเอง, ออเดอร์หาย, port-forward ใหม่ทุกครั้ง, ถ้าใช้ `kubectl delete pod -l app=som-booth` ร้านปิดทุกบูธพร้อมกัน, ย้อนกลับ = apply ไฟล์เดิมแล้วลบอีกรอบ
9. **9.9 เก็บกวาด**: `pkill -f "[k]ubectl port-forward"`; `kubectl delete ns som-booths`; 🖥️ `exit` หน้าต่าง `ssh -L` (image 1.1/1.1-promo เก็บไว้ได้)
10. **9.10 ปิด LAB/คำถามท้ายบท**: ตาราง 3 ปัญหา → บท 006 Service (ชื่อ/ที่อยู่คงที่ + แยก db ให้ทุกบูธใช้ร่วม), บท 007 Deployment (เปลี่ยนรุ่นทีละบูธ รอ Ready ย้อนรุ่นได้)

### 3.5 ผลที่ต้องเห็น

- RS `som-booth 3 3 3`, Pod `2/2 Running` (web + db sidecar) กระจาย 2+1; หน้าเว็บ 3 แท็บชื่อบูธต่างกัน
- สั่งซื้อที่ 8081 → 8082/8083 ยัง 0 ออเดอร์
- ลบบูธ → ตัวใหม่ชื่อ/IP ใหม่ ออเดอร์ 0, port-forward 8081 เดิมใช้ไม่ได้
- scale 5 (3+2) แล้ว 2 (คาด 1+1); template promo แล้ว custom-columns ยัง 1.1 ทุกบูธจนกว่าจะลบเอง

### 3.6 จุดที่ต้องยืนยันตอนทดสอบ

1. **resource 5 บูธ** (~1 CPU / 2.2Gi requests): ขึ้นครบไหม, เวลาเริ่มต่อบูธ, หน่วยความจำ k8s-lab/WSL ตอน 5 บูธ (`docker stats --no-stream` ใน k8s-lab); ทางออก scale 4
2. preferred anti-affinity ได้ 2+1 จริง และ 5 → 3+2; scale ลง 5→2 ลบบูธไหน (คาดเหลือ 1+1 ตามเกณฑ์ Node แออัด)
3. `kind load docker-image som-shop-web:1.1-promo` เมื่อ ID ซ้ำกับ 1.1: re-tag บน Node หรือไม่ (ถ้าไม่ ใช้ `--label` build ทางสำรอง)
4. ข้อความ/พฤติกรรม `kubectl port-forward` เมื่อ Pod ปลายทางถูกลบ (process จบเองหรือค้าง, ข้อความใน log) และ browser (`ERR_CONNECTION_RESET`/`ERR_EMPTY_RESPONSE`)
5. `$(POD_NAME)` ใน `SHOP_EYEBROW` แสดงชื่อบูธจริงบนหน้า และ emoji 🎉/⚓ แสดงถูก
6. ไม่มี Warning PSA ตอน apply (template restricted); ถ้ามี ให้แก้ manifest
7. ออเดอร์ API (`POST /api/orders` pre-check #27) และ `GET /api/orders` รูปแบบผลลัพธ์จริง
8. เวลาที่บูธใหม่ Ready หลังลบ (postgres init + seed) เพื่อเขียนคำว่า "รอราว N วินาที"

### 3.7 Screenshot ที่จะเก็บ (`02_LAB/images/screenshots/`)

- `..._lab9_01-booth-a.png` / `_02-booth-b.png` (หน้าร้าน 2 บูธชื่อต่างกัน), `_03-orders-mismatch.png` (8081 มีออเดอร์ 8082 ไม่มี), `_04-after-delete-booth-a.png` (บูธใหม่ ออเดอร์ 0), `_05-promo-booth.png` (eyebrow โปรบูธใหม่ข้างบูธเดิม)

## 4. งานถัดไป

1. ทดสอบ LAB0–LAB9 ใน container ชั่วคราว (skill `k8s-lab`, แยกชื่อ/port, ไม่แตะ `k8s-lab` ของผู้เรียน) เก็บผลจริงของทุกจุดในคอลัมน์ "สิ่งที่ต้องยืนยัน" + หัวข้อ 3.6
2. เขียน `02_LAB/labs/*`, `som-booths/k8s/*` ตามหัวข้อ 2–3 แล้วรันทั้งชุดอีกรอบ
3. เขียน `01_Theory/README.md` และ `02_LAB/README.md` โดยใช้ output จริง
4. ปรับ prompt ภาพ needs_test ตามผลจริง (ตัวเลข/ข้อความ) แล้ว `python3 build_images.py` → สร้างภาพทั้งหมด (gen_images.sh ของผู้ประสานงาน)
5. ประสานบท 006: LAB สุดท้ายบท 006 เริ่มจากปัญหา "ออเดอร์ไม่ตรงกัน/ชื่อเปลี่ยน" ของ LAB9 นี้ และใช้ RS เป็นตัวสร้าง Pod หลัง Service

## 5. สรุป storyboard

- Theory 36 ภาพ (T01–T36): บทนำ 3, controller 3, manifest 7, self-healing 4, scale 2, กับดัก label 5, immutable/template 2, cascade/orphan 2, ReplicationController 1, namespace (quota/LimitRange/PSA) 2, scheduling 2, ชื่อ/IP ไม่คงที่ 1, สรุป/ปูทาง 2 — T01 ป้าย "บทที่ 5", T36 ปูทาง (allow=True)
- LAB 20 ภาพ (L01–L20): LAB0–LAB8 อย่างน้อย LAB ละ 1 (LAB2 มี 2) + LAB9 10 ภาพ (L11–L20; L20 ปูทาง allow=True)
- จากบทรวม 15 ภาพ (T01–T12 + L01–L03: ใช้ prompt เดิม 6, แก้ 9) ใหม่ 41 ภาพ — ดู `README-split.md`

**needs_test (16):** T11 selector-template-mismatch (ข้อความ error), T17 node-down-timeline (เวลา NotReady/สร้างแทน), T19 scale-down-order (ลำดับลบ), T25 selector-immutable (ข้อความ), T30 rs-quota-cap (FailedCreate/ReplicaFailure), T31 psa-workload-warn (Warning/FailedCreate), L04 lab2-drain-rebirth, L05 lab3-scale (Pod ที่ถูกลบ), L07 lab5-template-old-pods, L09 lab7-quota, L13 lab9-three-booths-two-ships (การกระจาย), L15 lab9-orders-mismatch (ออเดอร์จริง), L16 lab9-delete-pod-data-lost, L17 lab9-scale-3-5-2 (resource 5 บูธ), L18 lab9-template-promo (1.1-promo kind load), L19 lab9-manual-replace
