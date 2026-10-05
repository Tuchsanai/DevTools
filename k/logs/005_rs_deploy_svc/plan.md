# แผนบทเรียน 005 — ReplicaSet, Deployment และ Service (หัวหน้ากะ ผู้จัดการร้าน และประภาคาร)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB และยังไม่รัน LAB เต็ม)
> Storyboard ภาพ: `logs/005_rs_deploy_svc/images.json` (Theory 40 ภาพ T01–T40, LAB 27 ภาพ L01–L27) สร้างจาก `logs/005_rs_deploy_svc/build_images.py` (แก้ prompt ที่ไฟล์นี้แล้วรันใหม่ — ได้ทั้ง JSON และ `imagegen-prompts.md` ทั้งสองไฟล์)
> ภาพตัวละครอ้างอิง: `005_kubernetes_replicaset_deployment_service/01_Theory/images/00-character-som.png`
> ผล pre-check ที่ใช้ตัดสินใจออกแบบ (รันจริงใน container ชั่วคราว 5 ต.ค. 2569 ลบแล้ว): `logs/005_rs_deploy_svc/precheck.md`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่านบท 001 (สถาปัตยกรรม, `k8s-lab`), 002 (Pod, YAML, labels, probes, multi-container, ร้าน som-shop), 003 (Node, scheduler, Downward API) และ 004 (Namespace, quota, RBAC, PSA, NetworkPolicy, DNS search domain) แล้ว
- เข้าเครื่อง: `ssh -p 2223 root@localhost` (รหัส `passwd`) หรือ JupyterLab `http://localhost:8889`; คลัสเตอร์ kind `lab` (`lab-control-plane`, `lab-worker`, `lab-worker2`, K8s v1.37); port 30080–30082 ของเครื่องนักศึกษา map ตรงเข้า NodePort 30080–30082 ของ `lab-control-plane` (extraPortMappings) → **บทนี้เป็นบทแรกที่เปิดร้านจาก browser ด้วย `http://localhost:30080` โดยไม่ต้อง port-forward/ssh -L**
- โฟลเดอร์ LAB: `docker cp 005_kubernetes_replicaset_deployment_service k8s-lab:/workspace/` แล้ว `cd /workspace/005_kubernetes_replicaset_deployment_service/02_LAB`
- บทนี้ "ปลดล็อก" สิ่งที่บทก่อนเกริ่นไว้: Pod เดี่ยวหายแล้วไม่มีใครสร้างใหม่ (→ ReplicaSet/Deployment), IP เปลี่ยน + port-forward หลุดเมื่อ Pod ถูกลบ (บท 004 LAB10) (→ Service), ชื่อ DNS `<svc>.<ns>.svc.cluster.local` ที่บท 004 เห็นแค่ search domain (→ ใช้จริง)
- ยังไม่สอน (กล่าวถึงเป็นการปูทางเท่านั้น): PersistentVolume/PVC, StatefulSet, Ingress, ConfigMap/Secret แบบละเอียด (ใช้ env ตรง ๆ เหมือนบท 002–004), HPA, DaemonSet/Job (Job กล่าวถึงเป็นทางเลือกการเติมสินค้าใน LAB12 เท่านั้น)
- ทุก LAB ทำใน namespace ของตัวเอง (ต่อยอดบท 004) และจบด้วย `kubectl delete ns ...`; NodePort `30080` ถูกจองทั้งคลัสเตอร์ → LAB9 ต้องลบ Service NodePort ก่อนถึง LAB12
- Pod busybox ทุกตัวใส่ `terminationGracePeriodSeconds: 1` (บทเรียนบท 002)
- image: `nginx:1.27-alpine` → `nginx:1.28-alpine` (เปลี่ยนรุ่น), `busybox:1.36`, `postgres:17.11-alpine`, `som-shop-web:1.2` / `1.3` (build ใหม่บทนี้), tag ที่ไม่มีจริง `nginx:9.99-nope`, `som-shop-web:1.4`
  - **pre-check:** `kind load docker-image nginx:1.27-alpine` ล้มเหลว (`ctr: content digest ...: not found` — image multi-arch) → image สาธารณะให้ Node pull เองจาก Docker Hub (ทำงานได้); `kind load` ใช้เฉพาะ image ที่ build เอง; postgres ใช้วิธีบท 004 (`docker save --platform linux/amd64` + `kind load image-archive`) หรือให้ Node pull เอง

### ผลจาก pre-check ที่กำหนดการออกแบบ (รายละเอียดใน `precheck.md`)

| คำถาม | ผล | ผลต่อแผน |
|---|---|---|
| kube-proxy mode | `iptables` | ทฤษฎีเน้น iptables, กล่าวถึง nftables/ipvs |
| Pod หลง label ตรง | สร้างหลัง RS → ถูกลบทันที (`Deleted pod: stray`); มีก่อน RS → ถูกรับเลี้ยง (ownerReferences) RS สร้างเพิ่มแค่ 2 | LAB2 สอนทั้งสองกรณี |
| rollout ค่า default | maxSurge/maxUnavailable `25%`, revisionHistoryLimit `10`; replicas 3 → เพิ่มทีละ 1 ลดทีละ 1 (ไม่มีช่วงที่ต่ำกว่า 3) | ภาพ T15 ใช้ลำดับจริง 5 ขั้น |
| change-cause | revision ใหม่ที่ไม่ annotate สืบทอดข้อความเดิม; undo ย้าย revision 2 → 4 | LAB4 เน้น annotate ทุกครั้ง; ภาพ T21/L06 ใช้ 1, 3, 4 |
| image ผิด | `ErrImagePull`→`ImagePullBackOff`; `error: deployment "web" exceeded its progress deadline`; `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`; Pod เก่ายังตอบ | LAB6 และ LAB12 |
| Endpoints | `Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice` | สอน EndpointSlice เป็นหลัก |
| Pod ไม่ ready | คอลัมน์ ENDPOINTS ของ `get endpointslice` ยังแสดง IP แต่ `conditions.ready=false` | กับดักใน LAB8, ภาพ T37 |
| การกระจาย | สุ่ม (9 ครั้ง → 5/4/0); browser (Chromium) 10/10 ไป Pod เดียว (keep-alive) | LAB7/9/12 ใช้ curl ≥30 ครั้ง |
| zero-downtime | ไม่มี preStop: 3/150 และ 3/300 error; preStop 5s + maxUnavailable 0: 0/300 สองรอบ | LAB10 เทียบ 2 รอบ |
| seed 3 replicas พร้อมกัน | 2/3 init `db-seed` restart 1 ครั้ง `duplicate key value violates unique constraint "pg_type_typname_nsp_index"` | 1.2 ใช้ advisory lock |
| ลบ Pod db (emptyDir) | Pod ใหม่ 4.2 วิ, ตารางหาย, หน้าเว็บ HTTP 500 แต่ `/api/health` ok | 1.2 หน้าเว็บแจ้งเป็นมิตร (503) + LAB12 ใช้ `rollout restart` เติมสินค้าใหม่ |
| NodePort ผ่าน extraPortMappings | host → container → kind control-plane ใช้ได้ | LAB9/12 (ต้องยืนยันบน `k8s-lab` จริงของนักศึกษา) |

### อุปมา (ต่อจากบท 001–004 + ของใหม่บทนี้)

| Kubernetes | อุปมาท่าเรือ | ใหม่? |
|---|---|---|
| container / Pod / Node / Control Plane / Namespace | ตู้สินค้า / กล่องใส teal มีป้าย IP (บทนี้ทำเป็น "บูธร้าน" มีกันสาด) / เรือ / หอบังคับการ / โซนทาสี | – |
| label | ป้ายห้อยกระเป๋าสีบนกล่อง | – |
| controller + reconciliation loop | พนักงานหุ่นยนต์ในหอที่วน "ดู → เทียบ → แก้" ไม่รู้จบ | ใหม่ |
| **ReplicaSet** | **หัวหน้ากะ** (หุ่นยนต์กล่องสี teal ถือคลิปบอร์ดนับหัว) นับกล่องที่ป้ายตรงให้ครบจำนวนตลอดเวลา | ใหม่ |
| Pod template | แบบพิมพ์/พิมพ์เขียวที่หัวหน้ากะใช้ปั๊มกล่องใหม่ | ใหม่ |
| ownerReferences | ป้ายเจ้าของที่คล้องบนกล่อง | ใหม่ |
| **Deployment** | **ผู้จัดการร้าน** (หุ่นยนต์สีกรมท่าตัวสูง ผูกหูกระต่าย ถือสมุดบันทึกรุ่น) คุมหัวหน้ากะ 1 คนต่อ 1 รุ่น | ใหม่ |
| pod-template-hash | สติกเกอร์บาร์โค้ดประจำรุ่น (ห้ามวาดเป็นอาหาร) | ใหม่ |
| rolling update | เปลี่ยนป้ายร้านทีละบูธโดยร้านไม่ปิด | ใหม่ |
| Recreate | ปิดทุกบูธก่อนแล้วเปิดใหม่ (มีช่วงป้าย CLOSED) | ใหม่ |
| rollout history / undo | สมุดบันทึกรุ่น / พลิกสมุดย้อนกลับ (ปุ่ม rewind) | ใหม่ |
| **Service** | **ประภาคาร/เคาน์เตอร์ต้อนรับ** บนท่า มีป้ายชื่อและป้ายที่อยู่คงที่ ส่งลูกค้าไปบูธที่พร้อม | ใหม่ |
| EndpointSlice | คลิปบอร์ดรายชื่อบูธที่เปิดอยู่ ติดข้างประภาคาร | ใหม่ |
| readinessProbe | ไฟเขียวหน้าบูธ (ไฟแดง = ไม่ได้ลูกค้า) | ใหม่ |
| kube-proxy | ป้ายบอกทางบนเรือทุกลำ (และที่ท่าหอ) | ใหม่ |
| NodePort | ประตูทางขึ้นเรือหมายเลข 30080 บนทุก Node | ใหม่ |
| LoadBalancer | เครนของผู้ให้บริการคลาวด์ที่ส่งป้ายที่อยู่สาธารณะ (ใน kind ไม่มา → `<pending>`) | ใหม่ |
| ExternalName / headless | ป้ายชี้ออกทะเลไปเกาะซัพพลายเออร์ / สมุดโทรศัพท์รายชื่อบูธ (ไม่มีเคาน์เตอร์กลาง — ห้ามวาดคนไม่มีหัว) | ใหม่ |
| blue/green, canary | บูธสองแถวสีน้ำเงิน/เขียว + คันโยกที่ประภาคาร / บูธทดลอง 1 ใน 10 (ห้ามวาดนก) | ใหม่ |

### เรื่องเล่า

ร้านอาหารแมวน้องส้มเปิดแยก environment ได้แล้ว (บท 004) แต่ทุกครั้งที่กล่องร้านหาย (ลบผิด/Node ล่ม) ร้านปิดจนกว่าน้องส้มจะสร้างใหม่เอง และลูกค้าที่จำ IP หรือ port-forward ไว้ก็หลง น้องส้มจึงจ้าง **หัวหน้ากะ** ที่คอยนับกล่องให้ครบ แล้วมี **ผู้จัดการร้าน** ที่เปลี่ยนรุ่นเมนูทีละบูธอย่างปลอดภัยและย้อนรุ่นได้ จากนั้นสร้าง **ประภาคาร** ที่ชื่อและที่อยู่ไม่เคยเปลี่ยน ส่งลูกค้าไปเฉพาะบูธที่ไฟเขียว เปิด **ประตูหมายเลข 30080** ให้ลูกค้าภายนอก และปิดท้ายด้วย "ร้านแบบโปรดักชันครั้งแรก" ที่แยก web 3 บูธกับฐานข้อมูล เปลี่ยนรุ่นระหว่างขายโดยไม่มีลูกค้าคนไหนเจอ error — แต่ฐานข้อมูลยังลืมทุกอย่างเมื่อกล่องเกิดใหม่ ซึ่งเป็นโจทย์ของบทหน้า

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001–004: รายวิชา/หัวข้อ/CLO, บทก่อนหน้า (ลิงก์บท 004), บทคัดย่อ, วัตถุประสงค์การเรียนรู้ (~12 ข้อ), สารบัญ, ตารางอุปมา; ทุก output ในทฤษฎีให้ใช้ "ผลจริง" จาก pre-check/การรัน LAB (หลังทดสอบ)

1. **บทนำ: กล่องเดี่ยวหาย ไม่มีใครสร้างใหม่** (T01–T02)
   - ทบทวน: บท 002 ลบ Pod แล้วหายถาวร, บท 003 drain/Node ล่มแล้ว Pod เดี่ยวไม่ย้ายเอง, บท 004 port-forward หลุดเมื่อลบ namespace และ IP ของ Pod เปลี่ยนทุกครั้งที่สร้างใหม่
   - Pod = หน่วยที่ "ตายแล้วไม่ฟื้น" (ไม่ย้าย ไม่ถูกสร้างแทน) → ต้องมีผู้ดูแลระดับสูงกว่า (workload controller) และที่อยู่คงที่ (Service)
   - ภาพรวมบท + ตารางอุปมาใหม่
2. **Controller และ reconciliation loop** (T03–T04)
   - declarative: เราเขียน `spec` (desired state), ระบบรายงาน `status` (actual) → controller วน observe → diff → act (level-triggered ไม่ใช่ event-triggered: พลาด event ก็แก้ทันรอบถัดไป)
   - controller อยู่ใน `kube-controller-manager` (static Pod ใน kube-system จากบท 004) ทำงานผ่าน API server เท่านั้น (watch); ตัวที่ใช้บทนี้: ReplicaSet, Deployment, EndpointSlice controller; kube-proxy บนทุก Node ก็ watch แบบเดียวกัน
   - ตัวอย่างอื่น (ชื่อเท่านั้น): DaemonSet, Job, StatefulSet, Node controller
3. **ReplicaSet: หัวหน้ากะที่นับกล่องให้ครบ** (T05–T12)
   - 3.1 โครง manifest `apps/v1 ReplicaSet`: `replicas`, `selector.matchLabels` (และ `matchExpressions`), `template` (Pod spec ไม่มี name — ชื่อ = `<rs>-<สุ่ม 5 ตัว>`); เงื่อนไข: label ใน template ต้องตรง selector ไม่งั้น apply ไม่ผ่าน (`selector does not match template labels`); selector แก้ไม่ได้หลังสร้าง (apps/v1)
   - 3.2 self-healing: ลบ Pod → นับได้ 2/3 → สร้างใหม่ทันที (pre-check ~3 วิ, ตัวใหม่เกิดขณะตัวเก่ายัง Terminating); Node ล่ม → Pod ที่หายถูกสร้างใหม่บน Node อื่น (โยงบท 003 — หลัง Node NotReady + toleration 300 วิ)
   - 3.3 นับด้วย label ไม่ใช่ชื่อ — **กับดัก**: (ก) Pod เดี่ยวที่ label ตรงและไม่มีเจ้าของ ถูกรับเลี้ยง (ownerReferences ถูกเติม) ทำให้ RS สร้างเพิ่มน้อยกว่าที่คิด และ template ของ Pod นั้นอาจต่างจากที่ RS กำหนด; (ข) Pod ที่ label ตรงเกินจำนวน → RS ลบทิ้ง (เลือกตัวที่ "เสียได้มากที่สุด" ตามลำดับ: ยังไม่ schedule > pending > not ready > ใหม่กว่า) — pre-check `Deleted pod: stray`; (ค) สอง RS ที่ selector ทับกันจะแย่งกันนับ (ทำไม Deployment ต้องมี pod-template-hash)
   - 3.4 `metadata.ownerReferences` (`kind: ReplicaSet`, `controller: true`, `blockOwnerDeletion: true`) และ garbage collector: `kubectl delete rs` ลบ Pod ตาม (cascade background/foreground), `--cascade=orphan` ทิ้ง Pod ไว้ (แล้ว RS ใหม่ที่ selector ตรงจะรับเลี้ยงต่อ); ถอด label ออกจาก Pod = ปลดออกจาก RS (RS สร้างตัวแทน, Pod เก่ากลายเป็นกำพร้า — เทคนิค debug)
   - 3.5 scale: `kubectl scale rs snack-rs --replicas=5`, แก้ YAML แล้ว apply; scale เป็น 0 ได้
   - 3.6 ทำไมไม่ใช้ ReplicaSet ตรง ๆ: แก้ template แล้ว Pod เดิม **ไม่ถูกเปลี่ยน** (มีผลเฉพาะ Pod ที่เกิดใหม่) → ไม่มี rolling update, ไม่มีประวัติ/ย้อนรุ่น → ใช้ Deployment; ReplicationController = รุ่นเก่า (กล่าวถึง)
4. **Deployment: ผู้จัดการร้านที่เปลี่ยนรุ่นอย่างปลอดภัย** (T13–T24)
   - 4.1 ความสัมพันธ์ Deployment → ReplicaSet (1 ตัวต่อ 1 template) → Pod; เราแก้ Deployment อย่างเดียว ห้ามแก้ RS ที่ Deployment เป็นเจ้าของ (แก้ไป controller ก็ปรับกลับ — ยืนยันใน LAB3)
   - 4.2 manifest: `replicas`, `selector`, `template`, `strategy`, `minReadySeconds`, `revisionHistoryLimit`, `progressDeadlineSeconds`; `kubectl create deployment --dry-run=client -o yaml` เป็นจุดเริ่ม; คอลัมน์ `READY / UP-TO-DATE / AVAILABLE`
   - 4.3 `pod-template-hash`: Deployment เติม label นี้ใน selector ของ RS และ Pod (`web-6f58b8bd67-frgpm` = `<deploy>-<hash>-<สุ่ม>`) กัน RS สองรุ่นนับกล่องปนกัน
   - 4.4 อะไรทำให้เกิด rollout: เปลี่ยน **`.spec.template`** เท่านั้น (image, env, probe, resources, label/annotation ใน template); `scale` ไม่สร้าง revision; `kubectl rollout restart` = เติม annotation `kubectl.kubernetes.io/restartedAt` ใน template
   - 4.5 RollingUpdate: `maxSurge` (เกินได้กี่ตัว — % ปัด **ขึ้น**) และ `maxUnavailable` (หายได้กี่ตัว — % ปัด **ลง**) ค่า default 25%/25%; ทั้งคู่เป็น 0 ไม่ได้; ตารางตัวอย่าง: replicas 3 → +1/−0 (รวมสูงสุด 4, พร้อมอย่างน้อย 3); replicas 4 → +1/−1 (5/3); replicas 10 → +3/−2 (13/8); ลำดับเหตุการณ์จริงของ replicas 3 (pre-check Events: up 0→1, down 3→2, up 1→2, down 2→1, up 2→3, down 1→0)
   - 4.6 Recreate: ลบทั้งหมดก่อนแล้วสร้างใหม่ (มี downtime) ใช้เมื่อสองรุ่นอยู่พร้อมกันไม่ได้ เช่น db ที่ใช้ volume เดียว/migration ไม่เข้ากัน (ใช้กับ som-db ใน LAB12)
   - 4.7 readinessProbe + `minReadySeconds` เป็นตัวตัดสินว่า Pod ใหม่ "available" → rollout เดินต่อ; ไม่มี readiness = ถือว่าพร้อมทันทีที่ container start (อันตราย); liveness ไม่ควรพึ่ง db (บทเรียนสำหรับ 1.2)
   - 4.8 `progressDeadlineSeconds` (default 600): ไม่คืบหน้าเกินเวลา → condition `Progressing=False reason ProgressDeadlineExceeded` (pre-check: `ReplicaSet "web-58b898d795" has timed out progressing.`), `kubectl rollout status` exit 1 (`error: deployment "web" exceeded its progress deadline`) — **Kubernetes ไม่ rollback ให้อัตโนมัติ** แต่ Pod เก่ายังรับลูกค้าเพราะ maxUnavailable จำกัดการลด
   - 4.9 คำสั่ง rollout: `status`, `history` (+ `--revision=N`), `undo` (+ `--to-revision=N`), `pause` / `resume`, `restart`; `kubernetes.io/change-cause` (ใช้ `kubectl annotate`; `--record` ถูกถอดแล้ว) — **กับดัก** revision ใหม่สืบทอดข้อความเดิมถ้าไม่ annotate ใหม่ (pre-check); undo = revision ใหม่ (เลขเดิมหายจาก history: 1, 3, 4); undo บน object ที่ apply มามีคำเตือน last-applied-configuration → หลัง undo ฉุกเฉินให้แก้ YAML ใน git ให้ตรง
   - 4.10 `revisionHistoryLimit` (default 10): RS เก่าเก็บไว้ด้วย replicas 0 = ข้อมูลสำหรับ undo; ตั้ง 0 = undo ไม่ได้
   - 4.11 วิธีเปลี่ยน: `kubectl set image deploy/web nginx=nginx:1.28-alpine`, `set env`, `scale`, `edit`, `patch`, `apply -f` (แนะนำ: ไฟล์เป็นความจริงหนึ่งเดียว); เตือนเรื่องการ `apply` ทับค่า replicas ที่ scale ด้วยมือ
   - 4.12 สถานการณ์พัง: image tag ผิด (`ErrImagePull` → `ImagePullBackOff`), readiness ล้ม (Pod `0/1 Running`), CrashLoopBackOff — วิธีอ่าน: `rollout status`, `get rs`, `describe deploy` (Conditions/Events), `get pods`, แล้ว `rollout undo`
5. **แนวคิด blue/green และ canary ด้วย label** (T25–T26) — ทฤษฎีสั้น ไม่มี LAB บังคับ
   - blue/green: Deployment 2 ชุด (`version=blue` / `version=green`) + Service ที่สลับ selector ทีเดียว (`kubectl patch svc`) ย้อนกลับเร็ว ใช้ทรัพยากร 2 เท่า
   - canary: Deployment `track=stable` 9 replicas + `track=canary` 1 replica ใช้ label `app=web` ร่วมกัน → Service ส่งไปรุ่นใหม่ราว 10% (สุ่ม, ตามสัดส่วนจำนวน Pod); ละเอียดกว่านี้ต้องใช้ Ingress/Gateway/service mesh (บทหลัง)
6. **Service: ประภาคารที่มีชื่อและที่อยู่คงที่** (T27–T38)
   - 6.1 ทำไมต้องมี: Pod IP เปลี่ยน, มีหลาย Pod, Pod ไม่พร้อมบางตัว → Service = ชื่อ DNS + ClusterIP (virtual IP ไม่ผูกกับเครื่องใด ping ไม่ได้) + การเลือก Pod ด้วย selector
   - 6.2 selector → EndpointSlice (`discovery.k8s.io/v1`, label `kubernetes.io/service-name`, สูงสุด 100 endpoint/slice); v1 Endpoints deprecated ตั้งแต่ v1.33 (คำเตือนจริง); Service ไม่มี selector + EndpointSlice ทำมือ (กล่าวถึง)
   - 6.3 ClusterIP และพอร์ต: `port` (ของ Service) → `targetPort` (ของ container, ใช้ชื่อพอร์ตได้ เช่น `targetPort: http`) / `nodePort`; `protocol`; หลายพอร์ตต้องตั้งชื่อ; Service CIDR ของ kind `10.96.0.0/16` (`kubernetes` = 10.96.0.1, DNS 10.96.0.10)
   - 6.4 DNS: A record `<svc>.<ns>.svc.cluster.local` → ClusterIP; จาก resolv.conf (บท 004) ชื่อสั้น `web` ได้เฉพาะ namespace เดียวกัน ข้ามใช้ `web.shop` หรือชื่อเต็ม; env `WEB_SERVICE_HOST` (มีเฉพาะ Service ที่สร้างก่อน Pod — เหตุผลที่ควรใช้ DNS); SRV record (กล่าวถึง)
   - 6.5 kube-proxy: DaemonSet บนทุก Node watch Service/EndpointSlice แล้วเขียนกฎ (kind = `iptables` — pre-check; โหมดอื่น `nftables`, `ipvs`) → แปลงปลายทาง (DNAT) ตั้งแต่ Node ต้นทาง ไม่มี "เครื่องประภาคาร" จริง; กล่าวถึงว่าดูกฎได้ด้วย `docker exec lab-worker iptables-save | grep web` (ทางเลือก)
   - 6.6 การกระจายโหลด: เลือก Pod แบบสุ่มต่อ connection (ไม่ใช่ round-robin, ไม่ใช่ต่อ request) → keep-alive ของ browser ติด Pod เดิม (pre-check 10/10); `sessionAffinity: ClientIP` (+ timeout default 10800 วิ); `internalTrafficPolicy` / `externalTrafficPolicy: Local` (กล่าวถึง)
   - 6.7 NodePort: ช่วง **30000–32767** (ข้อความ error จริงเมื่อผิดช่วง), เปิดบน **ทุก Node**, ระบุเองหรือให้สุ่ม, ซ้ำไม่ได้ทั้งคลัสเตอร์ (`provided port is already allocated`); ทำไม `localhost:30080` บนเครื่องนักศึกษาใช้ได้: Docker publish 30080 ของเครื่อง → container `k8s-lab` → kind extraPortMappings → `lab-control-plane:30080` → kube-proxy → Pod บน Node ใดก็ได้
   - 6.8 LoadBalancer: บนคลาวด์ได้ external IP/hostname จาก cloud controller; kind ไม่มี → `EXTERNAL-IP <pending>` แต่ได้ nodePort (`80:30456/TCP`) — ทางเลือก cloud-provider-kind/MetalLB (กล่าวถึง)
   - 6.9 ExternalName (CNAME ไปชื่อนอกคลัสเตอร์ ไม่มี ClusterIP ไม่มี proxy) และ headless `clusterIP: None` (DNS คืน IP ของทุก Pod ที่ ready — ปูทาง StatefulSet)
   - 6.10 debug Service ทีละขั้น: (1) `get svc` / `describe svc` (2) `get endpointslice -l kubernetes.io/service-name=<svc>` ว่าง? → เทียบ `selector` กับ `get pods --show-labels` (3) มี endpoint แต่ `Connection refused`/timeout → `targetPort` ตรงกับพอร์ตที่แอปฟังไหม (4) Pod ready ไหม (5) DNS (`nslookup`) (6) ข้าม namespace ใช้ชื่อถูกไหม (7) NetworkPolicy (บท 004)
   - 6.11 readinessProbe ↔ endpoints: Pod ไม่ ready ยังอยู่ใน EndpointSlice แต่ `conditions.ready=false` (คอลัมน์ ENDPOINTS ของ `kubectl get` ยังแสดง IP — pre-check) kube-proxy ไม่ส่งไป; Pod ที่กำลัง Terminating → `serving/terminating`
   - 6.12 zero-downtime rollout: readinessProbe + `maxUnavailable: 0` + `lifecycle.preStop.sleep.seconds: 5` (ให้ kube-proxy ทุก Node ลบ endpoint ก่อน process ปิด) + `terminationGracePeriodSeconds` เพียงพอ + แอปปิดอย่าง graceful; pre-check: ไม่มี preStop 3/300 error, มี 0/300
7. **สรุปและบทถัดไป** (T39–T40)
   - ตารางเลือกใช้: Pod เดี่ยว (ทดลอง/debug) / ReplicaSet (แทบไม่สร้างเอง) / Deployment (แอป stateless — ค่าเริ่มต้น) / Deployment + Recreate (งานรุ่นเดียว) / Service ClusterIP (ภายใน) / NodePort (LAB, on-prem ง่าย ๆ) / LoadBalancer (คลาวด์) / ExternalName / headless
   - ตารางคำสั่งสรุป (scale / set image / rollout ... / get endpointslice)
   - ปูทาง: db ใน Deployment + emptyDir ข้อมูลหายเมื่อ Pod ใหม่ → PVC/StatefulSet; ชื่อโดเมน/path → Ingress/Gateway; แยกค่าคอนฟิก/รหัสผ่าน → ConfigMap/Secret; ขยายอัตโนมัติ → HPA

## 2. รายการ LAB (`02_LAB/README.md`)

```text
02_LAB/
  README.md
  images/ (L01–L27 + imagegen-prompts.md)
  labs/
    lab01-replicaset/{00-ns.yaml (rs-lab), snack-rs.yaml}
    lab02-label-trap/{stray-pod.yaml}
    lab03-deployment/{00-ns.yaml (deploy-lab), web-deploy.yaml}
    lab05-strategy/{rolling.yaml, nosurge.yaml, recreate.yaml}
    lab06-broken/{readiness-broken-patch.yaml}
    lab07-service/{00-ns.yaml (shop), web-deploy.yaml, web-svc.yaml, client-pod.yaml}
    lab08-debug/{web-typo-svc.yaml, web-badport-svc.yaml}
    lab09-nodeport/{web-nodeport.yaml, web-lb.yaml}
    lab10-zero-downtime/{web-graceful-patch.yaml, hit.sh}
    lab11-cross-ns/{kitchen.yaml (ns kitchen + client Pod), web-headless.yaml, supplier-externalname.yaml}
  som-shop-v2/
    app/  (สำเนาจาก 004 som-shop-envs/app + แก้เป็น 1.2/1.3 ดูหัวข้อ 3.3)
    k8s/{00-namespace.yaml, 10-db.yaml, 20-web.yaml}
    hit.sh  (ยิงคำขอวน นับชื่อ Pod/เวอร์ชัน และ error)
```

**แอปตัวอย่าง LAB3–11** (ไม่ต้อง build): `nginx:1.27-alpine` ที่ `command` เขียน `index.html` = `web $VERSION from $(hostname)` แล้ว `exec nginx -g 'daemon off;'` (pre-check ใช้ได้) + `readinessProbe httpGet / periodSeconds 2` → `curl` เห็นชื่อ Pod และเวอร์ชันทันที; เปลี่ยนรุ่นด้วย `set image nginx:1.28-alpine` หรือ `set env VERSION=v2`

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ |
|---|---|---|---|---|---|---|
| 0 | เตรียมคลัสเตอร์ ไฟล์ และ image | คลัสเตอร์พร้อม, NodePort 30080 ว่าง, เข้าใจว่า image ไหนต้อง kind load | – | `kubectl get nodes`, `kubectl get svc -A \| grep -E '3008[0-2]'` (ต้องไม่มี — ถ้ามี `web` ของ `/workspace/examples` จากบท 001 ให้ลบ), `kubectl get ns`, `docker cp ...`, `kubectl -n kube-system get cm kube-proxy -o yaml \| grep mode` | 3 Node Ready; ไม่มี Service ใช้ 30080–30082; `mode: iptables` | ตัวอย่าง `examples/web-deployment.yaml` (NodePort 30080) ค้างในคลัสเตอร์นักศึกษาไหม — ถ้าค้าง LAB9/12 จะได้ `provided port is already allocated` |
| 1 | ReplicaSet แรก + self-healing | เห็นหัวหน้ากะนับ/สร้างแทน/scale และ ownerReferences | `lab01-replicaset/00-ns.yaml`, `snack-rs.yaml` (busybox 3 replicas, label `app=snack`) | `kubectl apply -f`, `kubectl get rs,pods -n rs-lab --show-labels`, `kubectl delete pod <หนึ่งตัว> --wait=false` + `kubectl get pods -w`, `kubectl get pod <ชื่อ> -o jsonpath='{.metadata.ownerReferences}'`, `kubectl describe rs snack-rs` (Events), `kubectl scale rs snack-rs --replicas=5` แล้ว `=2`, ลอง apply template ที่ label ไม่ตรง selector | Pod ใหม่ชื่อใหม่เกิดภายในไม่กี่วิ (ขณะตัวเก่ายัง Terminating), ownerReferences ชี้ `snack-rs`, Events `SuccessfulCreate`/`SuccessfulDelete`, scale ลดลบ Pod ใหม่สุดก่อน; template ไม่ตรง → `selector does not match template labels` | ข้อความ error เมื่อ label template ไม่ตรง selector (คาด `spec.template.metadata.labels: Invalid value: ...: selector does not match template labels`), รูปแบบ `pod "x" deleted from rs-lab namespace` |
| 2 | กับดัก label: รับเลี้ยงและลบ Pod เกิน | เข้าใจว่า RS นับด้วย label | `lab02-label-trap/stray-pod.yaml` (Pod `stray` label `app=snack`) | (ก) RS ครบ 3 แล้ว `kubectl apply -f stray-pod.yaml` → `get pods` + `describe rs` (ข) `kubectl delete rs snack-rs` (Pod หายตาม) → apply stray → apply snack-rs อีกครั้ง → `get pods`, ownerReferences ของ stray (ค) `kubectl label pod <rs-pod> app-` ปลด Pod ออกจาก RS (ง) `kubectl delete rs snack-rs --cascade=orphan` → Pod ยังอยู่ ไม่มี owner | (ก) stray ถูกลบทันที `Deleted pod: stray` (ข) RS สร้างเพิ่มแค่ 2, stray มี owner `snack-rs` (ค) RS สร้างตัวแทน, Pod ที่ปลด label อยู่ต่อแบบกำพร้า (ง) Pod 3 ตัวอยู่ต่อ | (ก)(ข) ยืนยันแล้วใน pre-check; ยืนยัน (ค)(ง) และลำดับเลือก Pod ที่ถูกลบ |
| 3 | Deployment แรก + scale | เห็น deploy → rs → pod, pod-template-hash, scale, แก้ RS ตรงไม่ได้ | `lab03-deployment/00-ns.yaml`, `web-deploy.yaml` (3 replicas, `progressDeadlineSeconds: 30`, readiness) | `kubectl apply -f`, `kubectl rollout status deploy/web`, `kubectl get deploy,rs,pods -n deploy-lab --show-labels`, `kubectl get deploy web -o jsonpath='{.spec.strategy}'`, `kubectl exec <pod> -- wget -qO- localhost` , `kubectl scale deploy web --replicas=5` / `=2`, `kubectl scale rs <rs> --replicas=6` แล้ว `get rs` อีกครั้ง, ลบ Pod หนึ่งตัว | `READY 3/3 UP-TO-DATE 3 AVAILABLE 3`; label `pod-template-hash=<hash>` ทั้ง RS/Pod; strategy default 25%/25%; scale แล้ว rs DESIRED เปลี่ยน (ไม่เกิด revision ใหม่); scale RS ตรง → ถูกปรับกลับเป็นค่าของ Deployment | scale RS ตรงถูก Deployment ปรับกลับเร็วแค่ไหน (เห็น Pod เพิ่มชั่วครู่หรือไม่), `rollout history` หลัง scale ยังเป็น revision 1 |
| 4 | Rolling update + history + undo | ดู RS เก่า/ใหม่ระหว่าง rolling, ใช้ history/undo | ใช้ `web-deploy.yaml` เดิม | terminal 2: `kubectl get rs -n deploy-lab -w`; `kubectl annotate deploy web kubernetes.io/change-cause="v1 nginx 1.27"`; `kubectl set image deploy/web nginx=nginx:1.28-alpine` + annotate `v2`; `kubectl rollout status`; `kubectl describe deploy web` (Events); `kubectl set env deploy/web VERSION=v3` + annotate; `kubectl rollout history deploy/web` / `--revision=2`; `kubectl rollout undo deploy/web --to-revision=2`; history อีกครั้ง; ทดลอง pause → set image + set env → resume | RS ใหม่ 0→1→2→3, เก่า 3→2→1→0 (Events `Scaled up/down replica set`); RS เก่าคงอยู่ที่ 0; history 3 แถวพร้อม CHANGE-CAUSE; undo แล้ว revision 2 หายจากรายการกลายเป็น 4; pause/resume = เปลี่ยน 2 อย่างได้ revision เดียว | เวลา rollout (pre-check 14 วิ รวม pull 1.28), ข้อความ Warning last-applied ตอน undo, change-cause ที่สืบทอด (ถ้าลืม annotate) |
| 5 | เทียบ maxSurge/maxUnavailable และ Recreate | เห็นผลของ strategy ต่อจำนวน Pod ระหว่างเปลี่ยนรุ่น | `lab05-strategy/rolling.yaml` (4 replicas default), `nosurge.yaml` (maxSurge 0 / maxUnavailable 1), `recreate.yaml` (Recreate) — 3 Deployment ใน deploy-lab label `lab=strategy` | `kubectl apply -f lab05-strategy/`; ทีละตัว: `kubectl get pods -l app=<name> -w` (terminal 2) + `kubectl set env deploy/<name> VERSION=v2`; บันทึกจำนวน Pod สูงสุด/ต่ำสุดที่ Ready; (เสริม) คำนวณ replicas 10 | rolling: สูงสุด 5 Pod, Ready ต่ำสุด 3; nosurge: ไม่เกิน 4, Ready ต่ำสุด 3; recreate: Pod เก่า Terminating ทั้ง 4 ก่อนแล้วตัวใหม่ค่อยเกิด (ช่วง 0 Ready) | ใช้ `set env` (ไม่ต้อง pull) ให้เห็นจังหวะชัด; ระยะเวลา gap ของ Recreate (nginx ปิดเร็ว); ตัวเลข max/min ที่เห็นจริงจาก watch |
| 6 | rollout พัง แล้ว rollback | เห็น rollout ค้าง 2 แบบ + ร้านยังขาย + undo | `lab06-broken/readiness-broken-patch.yaml` (readinessProbe path `/nope`) | `kubectl set image deploy/web nginx=nginx:9.99-nope`; `kubectl get pods,rs`; `kubectl rollout status deploy/web` (รอ ~30 วิ); `kubectl get deploy web`; `kubectl describe deploy web \| grep -A3 Conditions` ; client Pod ยิง `wget` (หรือ `kubectl exec` เข้า Pod เก่า) เห็นยังตอบ; `kubectl rollout undo`; แบบที่ 2: `kubectl patch deploy web --patch-file lab06-broken/readiness-broken-patch.yaml` → Pod ใหม่ `0/1 Running` → undo | `ErrImagePull`/`ImagePullBackOff`, RS ใหม่ `1 1 0`, `error: deployment "web" exceeded its progress deadline`, `READY 3/3 UP-TO-DATE 1 AVAILABLE 3`, condition `ProgressDeadlineExceeded`; readiness แบบ: Pod ใหม่ `0/1 Running` + Events `Readiness probe failed: HTTP probe failed with statuscode: 404`; undo แล้วกลับ 3/3 | ข้อความ condition จริง (pre-check ได้แล้ว), Event readiness 404 ของ nginx, สถานะ `ErrImagePull` vs `ImagePullBackOff` ตามเวลา |
| 7 | Service ClusterIP + DNS + การกระจายโหลด | สร้าง Service แล้วเรียกด้วยชื่อจาก Pod อื่น ดู EndpointSlice/สุ่ม | `lab07-service/00-ns.yaml` (shop), `web-deploy.yaml`, `web-svc.yaml` (ClusterIP port 80 → targetPort 80), `client-pod.yaml` (busybox) | `kubectl apply -f lab07-service/`; `kubectl get svc,endpointslice -n shop`; `kubectl get endpoints web` (เห็นคำเตือน deprecated); `kubectl exec client -- nslookup web`; `... cat /etc/resolv.conf`; `kubectl exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' \| sort \| uniq -c`; `kubectl patch svc web -p '{"spec":{"sessionAffinity":"ClientIP"}}'` แล้วยิงซ้ำ; scale 3→5 แล้วดู endpointslice | ClusterIP 10.96.x.x, EndpointSlice 3 IP ตรงกับ `get pods -o wide`; nslookup `web.shop.svc.cluster.local`; 30 ครั้งกระจาย 3 Pod (ไม่เท่ากันเป๊ะ); affinity → Pod เดียว 30/30; scale แล้ว endpoint เพิ่มเอง | สัดส่วนสุ่มจริง (pre-check 9 ครั้งได้ 5/4/0 → ใช้ 30); `nslookup` ของ busybox 1.36 แสดงผลรูปแบบไหน (มีบรรทัด NXDOMAIN ของ search domain อื่นปนหรือไม่) |
| 8 | debug Service ที่ไม่มี endpoints | ไล่ debug selector ผิด, targetPort ผิด, Pod ไม่ ready | `lab08-debug/web-typo-svc.yaml` (selector `app=wbe`), `web-badport-svc.yaml` (targetPort 8080) | apply ทั้งสอง; `kubectl exec client -- wget -qO- -T 3 http://web-typo`; `kubectl get endpointslice -l kubernetes.io/service-name=web-typo`; `kubectl describe svc web-typo`; เทียบ `get pods --show-labels`; แก้ด้วย `kubectl patch`/แก้ไฟล์; badport: `wget http://web-badport`; Pod ไม่ ready: `kubectl exec <pod> -- rm /usr/share/nginx/html/index.html` แล้ว `get pods`, `get endpointslice ... -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} ready={.conditions.ready}{"\n"}{end}'` | typo: `ENDPOINTS <unset>`, `Connection refused`; badport: มี endpoint แต่ `Connection refused` (ไม่มีใครฟัง 8080); not ready: Pod `0/1`, ENDPOINTS ยังแสดง 3 IP แต่ `ready=false` 1 ตัว และ curl 30 ครั้งไม่ไปตัวนั้น | ข้อความ wget ของ badport (refused หรือ timeout), Pod ที่ลบ index.html ได้ 403/404 จาก nginx → readiness ล้ม; ให้ `kubectl delete pod` คืนสภาพ |
| 9 | NodePort 30080 จาก browser | เปิดหน้าเว็บจากเครื่องนักศึกษาตรง ๆ, เห็นข้อจำกัด browser keep-alive | `lab09-nodeport/web-nodeport.yaml` (NodePort 30080), `web-lb.yaml` (LoadBalancer, ลองเพิ่ม) | `kubectl apply -f web-nodeport.yaml`; `kubectl get svc -n shop`; ใน k8s-lab: `curl -s localhost:30080`; **บนเครื่องนักศึกษา:** เปิด `http://localhost:30080` แล้วกด refresh หลายครั้ง; `for i in $(seq 30); do curl -s localhost:30080; done \| sort \| uniq -c` (ใน k8s-lab หรือ PowerShell `1..30 \| % { (curl.exe -s localhost:30080) }`); `kubectl create service nodeport bad --tcp=80:80 --node-port=29999 -n shop`; apply `web-lb.yaml` → `<pending>` แล้วลบ web-lb; **เก็บ web-nodeport ไว้ใช้ LAB10** (ถูกลบพร้อม ns `shop` ตอนเก็บกวาด LAB11) | browser เห็น `web v1 from web-...` (มักชื่อ Pod เดิมเมื่อ refresh); curl วนเห็นหลาย Pod; error `provided port is not in the valid range. The range of valid ports is 30000-32767`; LB `EXTERNAL-IP <pending>` `80:3xxxx/TCP` | **NodePort 30080 จาก host ของนักศึกษาผ่าน extraPortMappings** (pre-check ยืนยันกลไกด้วย port 30090 ของ container ทดลอง — ต้องยืนยันบน k8s-lab จริงพร้อม screenshot browser); browser Chrome/Edge บน Windows ติด Pod เดียวจริงไหม (pre-check Chromium 10/10), Ctrl+F5 เปลี่ยน Pod ไหม; คำสั่ง curl บน PowerShell |
| 10 | zero-downtime rollout | ยิงคำขอวนระหว่าง rollout แล้วนับ error เทียบก่อน/หลังปรับ | `lab10-zero-downtime/hit.sh` (ยิง N ครั้งทุก 0.1 วิ แสดง ok/err และ Pod ที่ตอบ), `web-graceful-patch.yaml` (`preStop.sleep.seconds: 5`, `maxUnavailable: 0`, `maxSurge: 1`) | ใน k8s-lab: `./hit.sh -q http://localhost:30080 300` (bash + curl ผ่าน NodePort `web-nodeport` จาก LAB9); terminal 2: `kubectl set env deploy/web VERSION=v2`; รอบ 2: `kubectl patch deploy web --patch-file web-graceful-patch.yaml` แล้ว `set env VERSION=v3` | รอบแรก error 0–3 ใน 300 (สุ่ม); รอบหลัง 0/300; คำตอบเปลี่ยนจาก v1 → v2 ระหว่างทาง (เห็นสองรุ่นปนกันช่วงสั้น ๆ) | จำนวน error จริงของรอบแรกในคลัสเตอร์นักศึกษา (อาจเป็น 0 — README ต้องเขียนว่า "อาจ"), เวอร์ชัน busybox รองรับ `seq`/`$((...))` (pre-check ใช้ while loop แทน) — ตัดสินใจว่า hit.sh รันใน k8s-lab (bash+curl) เป็นหลัก; ลำดับการลบ NodePort ระหว่าง LAB9/10 |
| 11 | ข้าม namespace ด้วย DNS + headless/ExternalName | เรียก Service ข้าม namespace, เห็น DNS ของ headless | `lab11-cross-ns/kitchen.yaml` (ns `kitchen` + busybox `cook`), `web-headless.yaml` (`clusterIP: None` selector `app=web` ใน shop), `supplier-externalname.yaml` (ExternalName `example.com`) | `kubectl exec -n kitchen cook -- wget -qO- -T 3 http://web` (ล้ม), `http://web.shop`, `http://web.shop.svc.cluster.local`; `cat /etc/resolv.conf`; `nslookup web-headless.shop` (ได้ IP Pod ทุกตัว) vs `nslookup web.shop` (ได้ ClusterIP); `nslookup supplier.shop` (CNAME); เก็บกวาด `kubectl delete ns rs-lab deploy-lab shop kitchen` | `web` → `wget: bad address 'web'`; `web.shop` และชื่อเต็มได้หน้าเว็บ; search `kitchen.svc.cluster.local ...`; headless คืน Pod IP 3 ตัว; ExternalName คืน CNAME `example.com` | ข้อความ wget เมื่อหาชื่อไม่เจอ (`bad address`), ผล nslookup ExternalName (ต้องมีเน็ตออก — ถ้าไม่มีให้ดูแค่ `canonical name`), NetworkPolicy ไม่มีค้างจากบท 004 |
| 12 | LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริงครั้งแรก | รวมทุกอย่าง: แยก web/db, Service ClusterIP + NodePort, scale, self-healing, rolling update ไม่มี error, rollback, rollout พังแต่ร้านยังขาย, ข้อมูล db หาย (ปูทาง PVC) | `som-shop-v2/` | ดูหัวข้อ 3 | ดูหัวข้อ 3 | ดูหัวข้อ 3.7 |

## 3. LAB สุดท้าย — "ร้านน้องส้มแบบโปรดักชันจริงครั้งแรก" (LAB12)

### 3.1 แนวคิดและเหตุผลการออกแบบ

- บท 002–004 ใส่ web + db ไว้ใน Pod เดียว (db เป็น native sidecar, คุยผ่าน localhost) → scale web ไม่ได้ (ทุกสาขามี db ของตัวเอง ข้อมูลไม่ตรงกัน — บท 003/004 เห็นแล้ว) และ rolling update ร้าน = ปิด db ไปด้วย
- บทนี้แยกเป็น **2 Deployment + 2 Service** ใน namespace `som-shop`:
  - `som-db`: Deployment `replicas: 1`, **`strategy: Recreate`** (ห้ามมี postgres 2 ตัวใช้ข้อมูลชุดเดียว — ถ้าเป็น RollingUpdate จะมีช่วงที่ 2 ตัวรันพร้อมกัน), `emptyDir` สำหรับ PGDATA + อธิบายชัดว่า **ข้อมูลหายเมื่อ Pod db ถูกสร้างใหม่** (ลบ Pod, rollout, Node ล่ม) → บทหน้าใช้ PVC/StatefulSet; Service ClusterIP `som-db:5432` (ภายในเท่านั้น ไม่เปิด NodePort ให้ db)
  - `som-web`: Deployment `replicas: 3` (`som-shop-web:1.2`) + initContainers `wait-for-db` (pg_isready `-h som-db`) และ `db-seed` (เติมสินค้า idempotent) + Service **NodePort 30080** → เปิด `http://localhost:30080` ได้ตรง
- เลือก **initContainer** (ไม่ใช่ Job) เพราะนักศึกษารู้จักแล้วจากบท 002 และทำให้ Pod web ทุกตัว "ตรวจว่าตารางพร้อม" ก่อนรับลูกค้า; ปัญหา 3 replicas เติมพร้อมกัน (race จริงใน pre-check: `duplicate key value violates unique constraint "pg_type_typname_nsp_index"` ทำให้ init restart) แก้ด้วย `pg_advisory_xact_lock` + `ON CONFLICT DO NOTHING` → เป็นจุดสอน "replica หลายตัวทำงานซ้ำพร้อมกัน ต้องออกแบบให้ idempotent และกันชน"; กล่าวถึงทางเลือก Job (`kind: Job` รันครั้งเดียวจนสำเร็จ — บทหลัง) ในกล่องหมายเหตุ
- คงเรื่อง namespace (บท 004): ใช้ namespace `som-shop` + label `pod-security.kubernetes.io/warn: restricted` และคง securityContext แบบ restricted จาก 004 (ไม่สอนใหม่ แค่ใช้ต่อ)
- web แสดง **ชื่อ Pod + เวอร์ชัน** บนหน้า และมี `/api/whoami` ตอบข้อความสั้นสำหรับ curl วน → เห็น load balancing; browser ติด Pod เดียว (keep-alive) จึงสอนให้ใช้ `hit.sh`
- zero-downtime: web ใช้ readiness (`/api/health` ตรวจ db) + liveness แยก (`/api/live` ไม่ตรวจ db — ถ้า db ล่ม web ไม่ควรถูก restart ทั้งหมด) + `preStop.sleep.seconds: 5` + `maxUnavailable: 0, maxSurge: 1` (pre-check 0/300)

### 3.2 สถาปัตยกรรม

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-xxx-a     Pod som-web-xxx-b     Pod som-web-xxx-c    (Deployment som-web, replicas 3→5, RollingUpdate)
   └──────── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop ────────┘
                                   ▼
                    Service som-db (ClusterIP, 5432)
                                   ▼
                    Pod som-db-xxx (Deployment som-db, replicas 1, Recreate, emptyDir)
```

### 3.3 การเปลี่ยนแอป (`som-shop-v2/app` จากสำเนา 004 `som-shop-envs/app`)

**1.2** (build: `docker build --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 .`)
- Dockerfile: `ARG APP_VERSION=dev`, `ARG APP_THEME=harbor` → `ENV APP_VERSION=$APP_VERSION APP_THEME=$APP_THEME` (image แต่ละ tag "จำ" เวอร์ชันของตัวเอง ไม่ต้องตั้ง env ใน YAML — การ set image จึงเปลี่ยนป้ายจริง)
- `app/page.tsx`: ป้าย **"เวอร์ชัน 1.2"** ใน hero; แถบ "🐱 เสิร์ฟโดย Pod: `<ชื่อ Pod>`" ย้ายขึ้นมาเด่นใต้ชื่อร้าน (ยังคงใน footer ด้วย); `className` ตาม `APP_THEME`; eyebrow/footer ค่าเริ่มต้นใหม่ (`⚓ ท่าเรือ Kubernetes · Deployment + Service`, `Next.js + PostgreSQL · Kubernetes LAB 005 · namespace $(POD_NAMESPACE)` ผ่าน env เดิม)
- ถ้า query ฐานข้อมูลล้ม (db ใหม่ยังไม่มีตาราง/ต่อไม่ได้) แสดงหน้า "ร้านกำลังเตรียมสินค้า กรุณารอสักครู่" + ชื่อ Pod/เวอร์ชัน และส่ง HTTP 503 แทน 500 (pre-check: 1.1 ได้ 500 ล้วน)
- `app/api/whoami/route.ts` (ใหม่): ตอบ text `som-web-7b44f6c986-4nhz6 1.2\n` ไม่แตะ db (ใช้กับ `hit.sh` และ curl วน)
- `app/api/live/route.ts` (ใหม่): `{"ok":true}` ไม่แตะ db (liveness); `/api/health` เดิม (readiness)
- `scripts/seed.mjs`: ครอบด้วย `BEGIN; SELECT pg_advisory_xact_lock(5005); ... COMMIT;` + ข้อความ log `seeded 6 products (new: N)`; `lib/db.ts` คอมเมนต์อธิบายว่าเรียก db ผ่านชื่อ Service
- `globals.css`: ธีม `harbor` (teal/navy เดิม)

**1.3** (build: `docker build --build-arg APP_VERSION=1.3 --build-arg APP_THEME=sunset -t som-shop-web:1.3 .` — โค้ดเดียวกัน)
- ธีม `sunset` (hero ส้ม-ชมพู ตลาดนัดริมท่ายามเย็น) + ป้าย "เวอร์ชัน 1.3" + แบนเนอร์ "เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟" (แสดงเมื่อ `APP_VERSION` = 1.3 — ไม่แก้ schema เพื่อให้ rollback กลับ 1.2 ได้ปลอดภัย: สอนว่า rollback ใช้ได้เมื่อ db เข้ากันได้ทั้งสองรุ่น)
- `som-shop-web:1.4` **ไม่ build** (ใช้จำลอง tag ผิด) — `imagePullPolicy: IfNotPresent` จะพยายาม pull `docker.io/library/som-shop-web:1.4` แล้ว `ErrImagePull`

### 3.4 ไฟล์ manifest

- `k8s/00-namespace.yaml`: Namespace `som-shop` labels `app.kubernetes.io/part-of: som-shop`, `pod-security.kubernetes.io/warn: restricted`
- `k8s/10-db.yaml`
  - Deployment `som-db`: `replicas: 1`, `strategy: {type: Recreate}`, selector/labels `app: som-db`, container postgres:17.11-alpine (env เดิม 004, PGDATA บน emptyDir `db-data`), securityContext restricted (uid/gid 70, fsGroup 70), readinessProbe `pg_isready -h 127.0.0.1`, livenessProbe tcp 5432, resources requests 100m/256Mi limits 500m/512Mi; คอมเมนต์ใหญ่ "emptyDir = ข้อมูลหายเมื่อ Pod นี้ถูกสร้างใหม่ (บทหน้าใช้ PVC)"
  - Service `som-db`: ClusterIP, `port: 5432`, `targetPort: 5432`, selector `app: som-db`
- `k8s/20-web.yaml`
  - Deployment `som-web`: `replicas: 3`, `revisionHistoryLimit: 5`, `progressDeadlineSeconds: 60`, `minReadySeconds: 3`, `strategy.rollingUpdate: {maxSurge: 1, maxUnavailable: 0}`; template annotation ไม่มี; Pod: `terminationGracePeriodSeconds: 30`, initContainers `wait-for-db` (postgres image, `until pg_isready -h som-db -p 5432 ...`) และ `db-seed` (`som-shop-web:1.2`, `node scripts/seed.mjs`); container `web` image `som-shop-web:1.2`, env `POD_NAMESPACE` (Downward API), `SHOP_FOOTER`, `DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop`, `PORT=3000`, `HOSTNAME=0.0.0.0` (ข้อสังเกต: env นี้คือ address ที่ Next.js ฟัง — ชื่อ Pod อ่านจาก `os.hostname()` ไม่ใช่ env); readinessProbe `/api/health` period 3 failure 2; livenessProbe `/api/live` initialDelay 10; `lifecycle.preStop.sleep.seconds: 5`; resources requests 100m/192Mi limits 500m/512Mi; securityContext restricted แบบ 004
  - Service `som-web`: `type: NodePort`, `port: 80`, `targetPort: 3000`, `nodePort: 30080`, selector `app: som-web`
- `hit.sh` (bash + curl, รันใน k8s-lab): `./hit.sh [URL=http://localhost:30080/api/whoami] [N=60] [DELAY=0.1]` → พิมพ์ตาราง `จำนวน  Pod  เวอร์ชัน` (sort | uniq -c) และบรรทัดสรุป `ok=… err=…`; โหมด `-q` นับเฉพาะ ok/err สำหรับระหว่าง rollout

### 3.5 ขั้นตอน

1. เตรียม: `kubectl get svc -A | grep 30080` ต้องว่าง (ลบ NodePort ของ LAB9/examples); build `som-shop-web:1.2` และ `1.3` (ครั้งแรก ~30 วิ ครั้งที่สองเร็วเพราะ cache) → `kind load docker-image som-shop-web:1.2 som-shop-web:1.3 --name lab`; postgres: `docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab` (หรือข้ามให้ Node pull เอง)
2. `kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml` → `kubectl -n som-shop rollout status deploy/som-db` → `kubectl -n som-shop get deploy,rs,pod,svc,endpointslice`
3. `kubectl apply -f k8s/20-web.yaml` → `rollout status deploy/som-web` → `kubectl -n som-shop logs -l app=som-web -c db-seed --prefix` (ตัวแรก `new: 6` อีกสองตัว `new: 0`), `kubectl -n som-shop get pods -o wide` (web กระจาย 2 Node) และ `get pod -o jsonpath` ดู initContainer `restartCount` = 0 ทุกตัว (เทียบกับ race ใน 1.1)
4. ทดสอบชื่อ Service จากภายใน: `kubectl -n som-shop exec deploy/som-web -c web -- node -e "require('dns').lookup('som-db',(e,a)=>console.log(a))"` (เห็น ClusterIP ของ som-db) หรือ `getent hosts som-db`
5. เปิด **`http://localhost:30080`** บนเครื่องนักศึกษา → หน้าร้านธีม harbor ป้าย "เวอร์ชัน 1.2" และ "เสิร์ฟโดย Pod: som-web-…"; refresh หลายครั้ง (มักเห็น Pod เดิม — keep-alive) → ใน k8s-lab `./hit.sh` 60 ครั้ง เห็นทั้ง 3 Pod
6. สั่งซื้อ 2–3 ออเดอร์ทางหน้าเว็บ (หรือ `curl -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":2}'`) → ตัวเลขออเดอร์เท่ากันไม่ว่า Pod ไหนเสิร์ฟ (db กลางตัวเดียว — ต่างจากบท 003/004)
7. scale: `kubectl -n som-shop scale deploy/som-web --replicas=5` → `get pods`, `get endpointslice -l kubernetes.io/service-name=som-web` (5 IP), `./hit.sh` เห็น 5 Pod
8. self-healing: `kubectl -n som-shop delete pod <web ตัวหนึ่ง>` ระหว่าง `./hit.sh -q ... 100` → Pod ใหม่เกิด, ok ทั้งหมด (หรือ error ไม่เกิน 1–2 ถ้าลบตอนกำลังตอบ — ยืนยัน)
9. rolling update เป็น 1.3 ระหว่างยิงวน: terminal 1 `./hit.sh -q http://localhost:30080/api/whoami 300`; terminal 2 `kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3` + `kubectl annotate ... kubernetes.io/change-cause="1.3 ธีม sunset"` + `rollout status` → **err=0**, ระหว่างทางเห็นทั้ง 1.2/1.3; browser refresh (Ctrl+F5) เห็นธีมใหม่; `kubectl get rs -n som-shop` (RS 1.2 เหลือ 0)
10. rollback: `kubectl -n som-shop rollout history deploy/som-web` → `rollout undo` → หน้ากลับเป็น 1.2 (ออเดอร์ยังอยู่ เพราะ db ไม่ถูกแตะ) → แล้ว `rollout undo` อีกครั้งหรือ set image 1.3 เพื่อไปต่อ (ตัดสินใจตอนเขียน README: จบขั้นนี้ที่ 1.3)
11. เวอร์ชันพัง: `kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.4` (+ change-cause) → Pod ใหม่ 1 ตัว `ErrImagePull`/`ImagePullBackOff` (maxSurge 1, maxUnavailable 0 → ไม่มี Pod เก่าถูกลบ) → `rollout status` รอ 60 วิ → `error: deployment "som-web" exceeded its progress deadline`; ระหว่างนั้น `./hit.sh` ok ทั้งหมด + หน้าเว็บยังสั่งซื้อได้ → `rollout undo` → Pod พังหายไป (ทางเลือกเสริม: `kubectl set env deploy/som-web DATABASE_URL=postgres://som:meow1234@som-dbb:5432/catshop` → Pod ใหม่ค้าง `Init:0/2` เพราะ wait-for-db หาไม่เจอ → undo)
12. ลบ Pod db: `kubectl -n som-shop delete pod -l app=som-db` → Pod ใหม่พร้อมใน ~5 วิ → หน้าเว็บขึ้น "ร้านกำลังเตรียมสินค้า" (503) / `/api/health` ok (ต่อได้แต่ไม่มีตาราง) → `kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c 'select count(*) from orders'` → `relation "orders" does not exist` → `kubectl -n som-shop rollout restart deploy/som-web` (initContainer รันใหม่ เติมสินค้า) → ร้านกลับมา **ออเดอร์ = 0** → อภิปราย: Deployment+emptyDir ไม่เหมาะกับ db → PVC/StatefulSet บทหน้า
13. เก็บกวาด: `kubectl delete ns som-shop` (NodePort 30080 ว่างอีกครั้ง)

### 3.6 ผลที่ต้องเห็น

- `get deploy -n som-shop`: `som-db 1/1`, `som-web 3/3` (ภายหลัง 5/5); `get svc`: `som-db ClusterIP 10.96.x.x 5432/TCP`, `som-web NodePort 10.96.x.x 80:30080/TCP`
- log db-seed: ตัวหนึ่ง `seeded 6 products (new: 6)` อีกตัว `(new: 0)` และไม่มี init restart
- browser `localhost:30080`: ป้ายเวอร์ชัน + ชื่อ Pod; `hit.sh` 60 ครั้งกระจายทุก Pod
- ออเดอร์รวมเหมือนกันทุก Pod; scale 5 → EndpointSlice 5 IP
- rolling 1.2→1.3 และ undo: `err=0` (เป้าหมาย), history แสดง change-cause
- 1.4: `ImagePullBackOff`, `exceeded its progress deadline`, `READY 5/5 UP-TO-DATE 1 AVAILABLE 5` (หรือ 3/3 ตาม replicas ขณะนั้น), ร้านยังขาย; undo กลับปกติ
- ลบ db: ข้อมูลหาย ออเดอร์เป็น 0 หลัง rollout restart

### 3.7 จุดที่ต้องยืนยันตอนทดสอบจริง

1. **NodePort 30080 ผ่าน extraPortMappings จาก host ของนักศึกษาได้จริง** (Windows + Docker Desktop: `http://localhost:30080` ใน browser) — pre-check ยืนยันแค่กลไกใน container ทดลอง (host port 30090/30091); ถ้าไม่ได้ ให้มีทางสำรอง `ssh -L 30080:localhost:30080`
2. **การกระจายโหลดจาก browser**: คาดติด Pod เดียวเพราะ keep-alive (pre-check Chromium 10/10) — ยืนยันกับ Chrome/Edge จริง, Ctrl+F5/หน้าต่าง Incognito เปลี่ยน Pod ไหม; สรุปให้ใช้ `hit.sh`
3. **seed พร้อมกัน 3 replicas ด้วย advisory lock**: initContainer restartCount = 0 ทุกตัว, log `new: 6` หนึ่งตัว; ถ้ายังชนให้ย้าย `CREATE TABLE` เข้า lock ด้วย (ต้องอยู่ใน transaction เดียวกัน)
4. **เวลา rollout** 1.2→1.3 ของ 3 replicas (pre-check 1.1: 9–14 วิ ต่อรอบ; ครั้งนี้มี initContainer 2 ตัว + minReadySeconds 3 → คาด ~25–35 วิ) และของ 5 replicas
5. **error ระหว่าง rollout** ด้วย preStop 5 วิ + maxUnavailable 0 ผ่าน NodePort: เป้าหมาย 0 (pre-check 0/300 สองรอบ) — บันทึกตัวเลขจริง; ถ้ามี error ให้ลอง preStop 10 วิ
6. **ข้อความ ProgressDeadlineExceeded จริง** ของ som-web (`progressDeadlineSeconds: 60`): `error: deployment "som-web" exceeded its progress deadline` และ condition `ReplicaSet "som-web-<hash>" has timed out progressing.`; สถานะ `ErrImagePull` vs `ImagePullBackOff` ณ เวลาที่ดู (image ไม่มีบน Docker Hub → คาด `pull access denied` ใน Events)
7. `set image` ต้องเปลี่ยนทั้ง `web` และ `db-seed` (ชื่อ container) — ถ้าเปลี่ยนแค่ web, initContainer ยังเป็น 1.2 (ไม่ผิดแต่ควรตรงกัน); ยืนยันว่า `kubectl set image deploy/som-web web=... db-seed=...` ใช้กับ initContainer ได้
8. หน้า "ร้านกำลังเตรียมสินค้า" 503 หลังลบ db และ readiness ยังผ่าน (`/api/health` = SELECT 1) — ตัดสินใจว่าจะให้ readiness ตรวจตาราง `products` ไหม (ถ้าตรวจ → web ทั้งหมด not ready → NodePort ตอบ `Connection refused`/ว่าง ซึ่งสอนเรื่อง endpoint ได้แต่ร้านดูล่มทั้งร้าน) — แผนปัจจุบัน: ไม่ตรวจ, ใช้หน้า 503 ที่เป็นมิตร
9. เวลา Pod db ใหม่ (pre-check 4.2 วิ) + web ต่อ db ใหม่ได้เองโดยไม่ restart (pre-check: `/api/health` ok ทันที — pool ต่อใหม่)
10. resource รวม 5 web + 1 db (requests ~600m/1.2Gi) ไม่ Pending บนเครื่องนักศึกษา; securityContext restricted + preStop sleep ใช้ร่วมกันได้ (sleep action ไม่ต้องมี binary `sleep`)
11. `kubectl rollout restart` หลังลบ db ใช้เวลาเท่าไร และ hit.sh ระหว่างนั้น (ร้านอยู่ในสถานะ 503 ก่อน restart)
12. Next.js Pod ที่ถูกปิดแสดงสถานะ `Error` ชั่วครู่ (pre-check) — อธิบายใน README ว่าไม่ใช่ความผิดพลาดของ rollout

### 3.8 ภาพ screenshot ที่จะเก็บตอนทดสอบจริง (ไม่ใช่ภาพ imagegen)

- browser `localhost:30080` เวอร์ชัน 1.2 และ 1.3 (เห็นชื่อ Pod), หน้า "ร้านกำลังเตรียมสินค้า"
- terminal: `get deploy,rs,pods,svc,endpointslice -n som-shop`, ผล `hit.sh` (กระจาย + err=0 ระหว่าง rollout), `rollout history`, ผล 1.4 `ImagePullBackOff` + progress deadline

## 4. งานถัดไป (หลังอนุมัติแผน)

1. สร้างภาพจาก `images.json` ด้วย `gen_images.sh` (มีแล้ว) → ตรวจภาพ (ป้ายสะกด/จำนวนป้าย, น้องส้มตรง reference, หุ่นยนต์ไม่เป็นแมว, ไม่มีนก/คนไม่มีหัว/เมล็ดพืช) → ภาพ `needs_test` สร้างหลังทดสอบ LAB จริงหรือปรับ prompt ตามผล
2. เขียนไฟล์ LAB (`labs/`, `som-shop-v2/` รวมโค้ด 1.2/1.3) + README ทฤษฎี/LAB + README หน้ารวม
3. รัน LAB0–12 ใน container ชั่วคราว (skill k8s-lab) บันทึก `logs/005_rs_deploy_svc/lab-run/SUMMARY.md` แล้วแก้ README/ภาพด้วยผลจริง

## 5. สรุป storyboard

- **Theory 40 ภาพ (T01–T40)**: บทนำ T01–T02, controller T03–T04, ReplicaSet T05–T12, Deployment T13–T24, blue/green + canary T25–T26, Service T27–T38, สรุป T39–T40
- **LAB 27 ภาพ (L01–L27)**: LAB0 L01, LAB1 L02, LAB2 L03, LAB3 L04, LAB4 L05–L06, LAB5 L07, LAB6 L08, LAB7 L09, LAB8 L10, LAB9 L11–L12, LAB10 L13, LAB11 L14, LAB12 L15–L27 (13 ภาพ: สถาปัตยกรรม, build/load, db+Service, เติมสินค้ากันชน, เปิดร้าน 30080, curl กระจาย, scale 3→5, ลบ Pod web, rollout 1.3, rollback, เวอร์ชันพังแต่ร้านยังขาย, ลบ db ข้อมูลหาย, สรุป)
- `needs_test: true` (สร้าง/ปรับหลังรัน LAB จริง): **L11** NodePort จาก browser นักศึกษา, **L12** browser keep-alive vs curl, **L13** ตัวเลข error zero-downtime (`3/300` vs `0/300` จาก pre-check), **L18** seed + advisory lock (`new: 6/0/0`), **L19** หน้าร้าน 1.2 (ชื่อ Pod ตัวอย่างจาก pre-check), **L20** curl กระจาย 3 Pod, **L23** rollout 1.3 `errors: 0`, **L25** 1.4 ImagePullBackOff/ProgressDeadlineExceeded, **L26** ลบ db (`orders: 2 → 0`, rollout restart)
- ภาพที่ใช้ค่าจาก pre-check แล้ว (ไม่ติด needs_test แต่ตรวจป้ายอีกครั้งหลังรัน): T06/T08/T09 (stray), T15 (ลำดับ rolling 5 ขั้น), T16 (10 → +3/−2, 3 → +1/−0), T19/L08 (`ImagePullBackOff`, `exceeded its progress deadline`, `3/3`), T21/L06 (revision 1, 3, 4), T28/T37 (IP ตัวอย่าง + `ready=false`), T32 (5/4/0), T33 (`30000–32767`), T34 (`80:30456/TCP`), T35 (headless IP), T36 (`ENDPOINTS <unset>`, `Connection refused`)
- กฎภาพที่ใช้ทุก prompt: ระบุจำนวนป้ายตรงตัว (ป้ายซ้ำระบุว่าซ้ำ), ทุกป้าย/แถว/โซนที่วาดมีข้อความ (ยกเว้นป้ายห้อยสี/กันสาด/แถวไอคอนที่ระบุชัดว่าไม่มีข้อความ), ของในภาพเป็นร้านอาหารแมว/ท่าเรือเท่านั้น, ไม่วาดคำตามตัวอักษร (canary ≠ นก, headless ≠ คนไม่มีหัว, hash ≠ อาหาร, seed ≠ เมล็ดพืช — ใช้ "เติมสินค้าเข้าชั้น"), หุ่นยนต์ไม่เป็นแมว, ห้ามโชว์ Ingress/StatefulSet/PV/HPA/ConfigMap ยกเว้น T40 และ L26
