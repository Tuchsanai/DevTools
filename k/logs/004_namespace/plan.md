# แผนบทเรียน 004 — Namespace (แบ่งโซนบนท่าเรือเดียวกัน)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB และยังไม่รัน LAB)
> Storyboard ภาพ: `logs/004_namespace/images.json` (Theory 38 ภาพ T01–T38, LAB 23 ภาพ L01–L23) สร้างจาก `logs/004_namespace/build_images.py`
> ภาพตัวละครอ้างอิง: `004_kubernetes_namespace/01_Theory/images/00-character-som.png`
> ผล pre-check ที่ใช้ตัดสินใจออกแบบ (รันจริงใน container ชั่วคราว 4 ต.ค. 2569 ลบแล้ว): `logs/004_namespace/precheck.md`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่านบท 001 (สถาปัตยกรรม, `k8s-lab`), 002 (Pod, YAML, labels, resources, probes, multi-container, ร้าน som-shop) และ 003 (Node, scheduler, label/affinity/taint, Downward API) แล้ว
- เข้าเครื่อง: `ssh -p 2223 root@localhost` (รหัส `passwd`) หรือ JupyterLab `http://localhost:8889`; คลัสเตอร์ kind `lab` (`lab-control-plane`, `lab-worker`, `lab-worker2`, context `kind-lab`, K8s v1.37) ถ้ายังไม่มีหรือเพิ่งรีสตาร์ท container ให้รัน `k8s-up` (LAB0)
- โฟลเดอร์ LAB: `docker cp 004_kubernetes_namespace k8s-lab:/workspace/` แล้ว `cd /workspace/004_kubernetes_namespace/02_LAB` (แบบเดียวกับบท 002–003)
- **ห้ามใช้ Service / NodePort / Deployment / ReplicaSet / DaemonSet / Ingress ใน LAB** ให้ใช้ Pod เดี่ยว และเข้าถึงแอปด้วย `exec`, `logs`, `port-forward` + `ssh -L`
  - กล่าวถึงได้ในทฤษฎีเท่านั้น: ชื่อ DNS ของ Service ข้าม namespace (`<service>.<namespace>.svc.cluster.local`) เพื่ออธิบายว่าทำไม search domain ใน `/etc/resolv.conf` ของ Pod มีชื่อ namespace (ดูได้จริงโดยไม่ต้องสร้าง Service), Pod ของ kube-system บางตัวมาจาก DaemonSet/Deployment (บอกชื่อเฉย ๆ)
- image ที่ใช้: `nginx:1.27-alpine`, `busybox:1.36` (ดึงแล้วในบทก่อน), `som-shop-web:1.0` + `postgres:17.11-alpine` (LAB สุดท้าย: build ใหม่ถ้ายังไม่มี + `kind load docker-image som-shop-web:1.0 --name lab` และ `docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab`)
- Pod busybox ทุกตัวใส่ `terminationGracePeriodSeconds: 1` (บทเรียนจากบท 002: `sh` เป็น PID 1 ลบช้า 30 วินาที)
- ทุก LAB ทำใน namespace ของตัวเอง **ไม่ทิ้งของไว้ใน `default`** และจบด้วย "เก็บกวาด" = `kubectl delete ns ...` (เป็นการฝึกหัวข้อบทนี้ไปในตัว) + คืน context namespace เป็น `default`

### ผลจาก pre-check ที่กำหนดการออกแบบ

| คำถาม | ผล | ผลต่อแผน |
|---|---|---|
| kindnet (`kindest/kindnetd:v20260820-69b56db7`) ของ kind 0.33 รองรับ NetworkPolicy ไหม | **รองรับและบังคับใช้จริง** (deny แล้ว `wget: download timed out`, allow ด้วย `namespaceSelector` แล้วกลับมาเข้าได้ภายใน 5 วิ) | ทำ NetworkPolicy เป็น **LAB จริง** (LAB4) |
| postgres:17.11-alpine รันภายใต้ PSA restricted ได้ไหม | **ได้** ด้วย `runAsUser/runAsGroup/fsGroup: 70` + seccomp RuntimeDefault + drop ALL + no privilege escalation | LAB สุดท้ายให้ som-prod ใช้ **restricted** (ไม่ใช่แค่ baseline) |
| `kubectl --token=<SA token>` เปลี่ยนตัวตนได้ไหม | **ไม่ได้** kubeconfig ของ kind มี client certificate ซึ่งถูกใช้ก่อน token → ยังเป็น admin | LAB7 สอน 2 วิธีที่ถูก: `--as` (impersonate) และสร้าง user/context ที่มีแต่ token; ยกกับดัก `--token` เป็นจุดเรียนรู้ |
| namespace เริ่มต้นใน kind | มี **5 ตัว**: `default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage` | ทฤษฎีบอก 4 ตัวมาตรฐาน + `local-path-storage` ที่ kind เพิ่มเอง |

### อุปมา (ต่อจากบท 001–003 + ของใหม่บทนี้)

| Kubernetes | อุปมาท่าเรือ | ใหม่? |
|---|---|---|
| container | ตู้สินค้า | – |
| Pod | กล่องห้องโดยสารใสสี teal ห่อตู้ มีป้าย IP 1 ป้าย | – |
| Node | เรือสินค้า (`lab-worker`, `lab-worker2`) | – |
| Control Plane | หอบังคับการบนท่า (`lab-control-plane`) | – |
| คลัสเตอร์ | ท่าเรือทั้งท่า | – |
| **Namespace** | **โซนทาสีบนแผนผังท่าเรือ มีป้ายชื่อโซน** — เป็นการแบ่ง "ทางทะเบียน/ตรรกะ" ไม่ใช่เรือ ไม่ใช่ที่ดินจริง: กล่องของโซนเดียวกันกระจายอยู่บนเรือหลายลำได้ วาดเป็น "ป้ายคล้องสีประจำโซน" บนกล่อง + แฟ้มสีของโซนบนแผนผังในหอ | ใหม่ |
| ชื่อเต็ม `namespace/name` | ที่อยู่แบบ "โซน + ชื่อกล่อง" (กล่องชื่อ `snack` มีได้ในหลายโซน) | ใหม่ |
| namespaced resource | ของประจำโซน (กล่อง Pod, บัตรพนักงาน, ใบโควตา) | ใหม่ |
| cluster-scoped resource | ของส่วนกลางของท่าเรือ (เรือ, หอ, ป้ายโซนเอง, โกดังกลาง = PersistentVolume/StorageClass, ป้าย VIP = PriorityClass) | ใหม่ |
| kubeconfig / context | พวงกุญแจ/กระเป๋าบัตร: บัตรท่าเรือ (cluster) + บัตรประจำตัว (user) + โซนที่ไปบ่อย (namespace) | ใหม่ |
| `-n` / `-A` | ไฟฉายส่องโซนเดียว / ไฟสปอตไลต์ส่องทั้งท่า | ใหม่ |
| ResourceQuota | ใบงบประมาณ/ใบโควตาของโซน (มีมาตรวัดใช้ไป/เพดาน) | ใหม่ |
| LimitRange | ป้ายกฎขนาดกล่องมาตรฐานของโซน (ไม่ระบุขนาด → ติดสติกเกอร์ขนาดมาตรฐานให้) | ใหม่ |
| RBAC: User / ServiceAccount | บัตรพนักงานคน / บัตรของหุ่นยนต์พนักงานอัตโนมัติ (ห้ามวาดหุ่นยนต์เป็นแมวตัวที่สอง) | ใหม่ |
| Role / RoleBinding | การ์ดสิทธิ์ (ทำอะไรได้กับอะไร) / สายคล้องที่ผูกบัตรกับการ์ดสิทธิ์ ใช้ได้เฉพาะโซนนั้น | ใหม่ |
| ClusterRole / ClusterRoleBinding | สมุดกฎสิทธิ์มาตรฐานของท่าเรือ (นำไปผูกในโซนเดียวด้วย RoleBinding ได้) / ผูกทั้งท่า | ใหม่ |
| `kubectl auth can-i` | เครื่องอ่านบัตรตอบไฟเขียว yes / ไฟแดง no | ใหม่ |
| Pod Security Admission | ด่านตรวจความปลอดภัยหน้าโซน มี 3 ระดับ (privileged/baseline/restricted) และ 3 โหมด (enforce = ไม้กั้น, warn = กระดิ่งเตือน, audit = สมุดบันทึก) | ใหม่ |
| NetworkPolicy | รั้วและประตูระหว่างโซน (ประตูเปิดให้เฉพาะโซนที่มีป้ายตรง) | ใหม่ |
| finalizers | เช็กลิสต์ที่ต้องติ๊กครบก่อนปลดป้ายโซน (ค้าง = Terminating) | ใหม่ |

### เรื่องเล่า

ร้านอาหารแมวน้องส้ม (บท 002) เปิดหลายสาขาบนกองเรือได้แล้ว (บท 003) ตอนนี้ทีมใหญ่ขึ้น: มีทีมพัฒนาทดลองของใหม่ทุกวัน ทีมทดสอบ และร้านจริงที่ลูกค้าใช้ ทุกคนวางกล่องรวมกันในท่าเรือเดียว ชื่อชนกัน ใครลบของใครก็ได้ ทีม dev ใช้ทรัพยากรจนร้านจริงช้า เด็กฝึกงานเผลอลบร้านจริง น้องส้มจึง **ทาสีแบ่งโซน** บนแผนผังท่าเรือ ให้แต่ละโซนมีงบประมาณ กฎขนาดกล่อง บัตรพนักงานเฉพาะโซน ด่านตรวจความปลอดภัย และรั้วระหว่างโซน ปิดท้ายด้วยการแยกร้านเป็น `som-dev` / `som-staging` / `som-prod` ในคลัสเตอร์เดียว

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001–003: รายวิชา/หัวข้อ/CLO-5, CLO-6, บทก่อนหน้า (ลิงก์บท 003), บทคัดย่อ, วัตถุประสงค์การเรียนรู้ (~10 ข้อ), สารบัญ, ตารางอุปมา (หัวข้อ 0) ทุกคำสั่งในทฤษฎีที่มีผลลัพธ์ให้ใช้ "ผลจริง" จากการรัน LAB (หลังทดสอบ) เหมือนบท 003

1. **บทนำ: ท่าเรือที่ทุกทีมวางของปนกัน** (T01–T02)
   - ทบทวน: คลัสเตอร์ = ท่าเรือ, Node = เรือ, Pod = กล่อง; ถึงตอนนี้ทุก LAB สร้าง Pod ใน `default` โดยไม่รู้ตัว
   - ปัญหาเมื่อหลายทีม/หลาย environment ใช้คลัสเตอร์เดียว: ชื่อชนกัน (`som-shop` ของ dev กับ prod), แย่งทรัพยากร, สิทธิ์ (ใครลบอะไรได้), ความปลอดภัย, การลบของทั้งชุด
   - ตารางอุปมาใหม่
2. **Namespace คืออะไร** (T03–T05)
   - 2.1 นิยาม: ขอบเขตของ "ชื่อ" (scope of names) ภายในคลัสเตอร์เดียว + หน่วยที่ใช้แนบนโยบาย (quota, LimitRange, RBAC, PSA, NetworkPolicy); Namespace เองเป็น object (`apiVersion: v1, kind: Namespace`)
   - 2.2 **Namespace ไม่ใช่เครื่อง ไม่ใช่ Node และไม่ใช่ VM**: Pod ของ namespace เดียวกันกระจายอยู่หลาย Node ได้ และ Node เดียวรับ Pod จากหลาย namespace (ยืนยันใน LAB4 ด้วย `-o wide`)
   - 2.3 ทำไมต้องมี: หลายทีม (team-a/team-b), หลาย environment (dev/staging/prod), แยกแอป; เทียบกับ "หนึ่งคลัสเตอร์ต่อทีม" (แยกขาดกว่าแต่แพง/ดูแลยาก) — namespace = soft multi-tenancy
   - 2.4 namespace ซ้อนกันไม่ได้ (flat), ชื่อตามกฎ DNS label (RFC 1123: a-z 0-9 `-` ≤ 63 ตัว), ห้ามขึ้นต้น `kube-` (สงวนให้ระบบ)
3. **Namespace เริ่มต้นและสิ่งที่อยู่ข้างใน** (T06–T08)
   - `default` (ที่ที่ object ไปอยู่ถ้าไม่ระบุ ลบไม่ได้), `kube-system` (control plane static pod, coredns, kube-proxy, kindnet — โยงบท 003), `kube-public` (อ่านได้แม้ไม่ล็อกอิน มี ConfigMap `cluster-info`), `kube-node-lease` (Lease ของแต่ละ Node = heartbeat โยงบท 003), และ **`local-path-storage`** (kind เพิ่มเอง: ตัวจัดสรร storage สำหรับ StorageClass `standard` — ปูทางบท storage)
   - ทุก namespace ได้ ConfigMap `kube-root-ca.crt` และ ServiceAccount `default` อัตโนมัติ
   - คำสั่ง: `kubectl get ns`, `kubectl get pods -n kube-system -o wide`, `kubectl get cm -n kube-public`, `kubectl get lease -n kube-node-lease`
4. **Namespaced vs cluster-scoped resources** (T09–T10)
   - `kubectl api-resources --namespaced=true` (Pod, ConfigMap, Secret, ServiceAccount, Role, RoleBinding, ResourceQuota, LimitRange, NetworkPolicy, PVC, Event, Lease … 34 ชนิดใน v1.37) vs `--namespaced=false` (Node, Namespace, PersistentVolume, StorageClass, PriorityClass, ClusterRole, ClusterRoleBinding, CSIDriver, IngressClass, RuntimeClass …)
   - ผล: `-n` กับ cluster-scoped resource ไม่มีผล (`kubectl get nodes -n kube-system` ได้ผลเหมือนเดิม), คอลัมน์ NAMESPACED, `kubectl explain` ไม่บอก scope → ใช้ api-resources
   - เหตุผล: ของบางอย่างเป็นของส่วนกลางโดยธรรมชาติ (เรือ, ป้ายโซนเอง, โกดังกลาง)
5. **สร้างและใช้ namespace** (T11–T14)
   - 5.1 imperative `kubectl create namespace blue` vs YAML `kind: Namespace` + `kubectl apply -f`; `--dry-run=client -o yaml`
   - 5.2 `metadata.namespace` ใน manifest vs `-n`: ไม่ระบุทั้งคู่ → namespace ของ context (ปกติ `default`); ระบุใน manifest → ไปที่นั่น; ระบุทั้งคู่แต่ไม่ตรง → error (`the namespace from the provided object "..." does not match the namespace "..."` — ยืนยันข้อความจริงใน LAB1); แนวปฏิบัติ: manifest ที่ใช้ซ้ำหลาย environment **ไม่ใส่** `metadata.namespace` แล้วเลือกด้วย `-n` (ใช้ใน LAB สุดท้าย)
   - 5.3 ชื่อซ้ำได้ข้าม namespace (ชื่อเต็ม = `namespace/name`), ซ้ำใน namespace เดียวไม่ได้ (`AlreadyExists`)
   - 5.4 `-n <ns>` / `--namespace`, `-A` / `--all-namespaces` (เพิ่มคอลัมน์ NAMESPACE), ใช้ร่วมกับ `-l`; `kubectl get pod snack -A` ใช้ไม่ได้ (ต้องใช้ field selector `--field-selector metadata.name=snack -A`)
   - 5.5 namespace ของ namespace ไม่มี: `kubectl get ns blue -o yaml` เห็น `spec.finalizers`, `status.phase: Active`
6. **kubeconfig, context และ namespace เริ่มต้น** (T15–T16)
   - kubeconfig (`~/.kube/config`) มี 3 ส่วน: `clusters` (ที่อยู่ API server + CA), `users` (client cert/token), `contexts` (cluster + user + namespace) และ `current-context`
   - `kubectl config get-contexts`, `current-context`, `view --minify`, `set-context --current --namespace=blue`, ดู namespace ปัจจุบัน `kubectl config view --minify -o jsonpath='{..namespace}'`, คืนค่าด้วย `--namespace=default`
   - ข้อควรระวัง: ลืมว่าเปลี่ยน namespace ไว้ → สร้าง/ลบผิดที่ (ใน prod ให้ใส่ `-n` ทุกครั้ง); เครื่องมือเสริม `kubens`/`kubectx` (กล่าวถึง ไม่ติดตั้ง); สร้าง context ใหม่สำหรับ user อื่น (ใช้ใน LAB7)
7. **Label ของ namespace** (T17)
   - `kubernetes.io/metadata.name=<ชื่อ>` ระบบใส่ให้อัตโนมัติและแก้ไม่ได้ (ใช้อ้างใน NetworkPolicy `namespaceSelector`)
   - label เอง เช่น `env=prod`, `team=som` → `kubectl get ns -l team=som`, `-L env`; label พิเศษของ PSA (`pod-security.kubernetes.io/*`)
8. **การลบ namespace** (T18–T19)
   - `kubectl delete ns blue` ลบ **ทุก object ในนั้น** (Pod, SA, Role, RoleBinding, quota, …) ไม่มีถังขยะ; cluster-scoped (Node, PV) ไม่ถูกลบ
   - ลำดับ: `status.phase: Terminating` → namespace controller ลบของข้างใน → เอา finalizer `kubernetes` ออก → object หาย; ระหว่าง Terminating สร้างของใหม่ในนั้นไม่ได้ (`forbidden: unable to create new content in namespace ... because it is being terminated` — ยืนยันใน LAB9)
   - finalizers คืออะไร (เช็กลิสต์ก่อนลบ); กรณีค้าง Terminating (เช่น API ที่ลงทะเบียนไว้ล่ม/ของมี finalizer ที่ controller หาย) → ดู `status.conditions` ก่อน ไม่แนะนำแก้ finalizer เองถ้าไม่เข้าใจ
   - ข้อควรระวัง: `default`, `kube-system`, `kube-public`, `kube-node-lease` ลบไม่ได้/ห้ามลบ
9. **Namespace ไม่ได้แยก network/node** (T20–T21)
   - Pod ข้าม namespace คุยกันด้วย Pod IP ได้ทันที (flat Pod network จากบท 001) และอยู่บน Node เดียวกันได้
   - DNS (ทฤษฎีสั้น): `/etc/resolv.conf` ของ Pod มี `search <ns>.svc.cluster.local svc.cluster.local cluster.local` → ชื่อสั้นของ Service หาได้เฉพาะใน namespace ตัวเอง ข้าม namespace ต้องใช้ `<service>.<namespace>` หรือชื่อเต็ม (Service เรียนบทหน้า; LAB ดูแค่ resolv.conf)
   - Namespace ≠ ขอบเขตความปลอดภัยสมบูรณ์: ต้องเพิ่ม NetworkPolicy/RBAC/PSA/quota เอง
10. **NetworkPolicy: รั้วและประตูระหว่างโซน** (T22–T23)
    - ต้องมี network plugin ที่รองรับ: kind 0.33 (kindnet) รองรับ (pre-check); บางคลัสเตอร์ไม่รองรับ → สร้าง object ได้แต่ไม่มีผล
    - หลัก: Pod ที่ถูก policy เลือก (`podSelector`) จะเปลี่ยนเป็น "ปฏิเสธทุกอย่างยกเว้นที่อนุญาต" สำหรับทิศที่ระบุใน `policyTypes`; policy เป็นแบบ additive (OR)
    - ตัวอย่าง: (1) allow-same-namespace (`ingress.from.podSelector: {}`) = กั้นทุก namespace อื่น, (2) allow จาก namespace ที่มี label (`namespaceSelector.matchLabels kubernetes.io/metadata.name: team-b`), (3) default-deny ingress (`ingress` ว่าง); ความต่างของ `namespaceSelector` + `podSelector` ในรายการเดียว (AND) vs คนละรายการ (OR)
    - egress กล่าวถึง (ระวัง DNS ถ้า deny egress)
11. **ResourceQuota: งบประมาณของโซน** (T24–T26)
    - compute: `requests.cpu`, `requests.memory`, `limits.cpu`, `limits.memory`; object count: `pods`, `configmaps`, `secrets`, `count/...`; `kubectl describe quota` (Used/Hard)
    - ตรวจตอนสร้าง (admission) ไม่ไล่ Pod เดิม; ถ้ามี quota ของ requests.cpu แล้ว Pod ที่ไม่ระบุ requests จะถูกปฏิเสธ (`failed quota: q: must specify requests.cpu for: q1` — ผล pre-check)
    - ข้อความเมื่อเกิน: `exceeded quota: q, requested: pods=1, used: pods=2, limited: pods=2` (ผล pre-check)
    - การนับ Pod ที่มี init/sidecar: effective request = max(ผลรวม sidecar + container หลัก, init แต่ละตัว + sidecar ที่เริ่มก่อน) → som-shop ≈ cpu 200m, memory 448Mi, limits cpu 1, memory 1Gi (ยืนยันตัวเลข Used จริงใน LAB10)
12. **LimitRange: กฎขนาดกล่องมาตรฐาน** (T27–T28)
    - `type: Container` (`default` = limits ที่ใส่ให้, `defaultRequest`, `min`, `max`, `maxLimitRequestRatio`), `type: Pod`, `type: PersistentVolumeClaim`
    - ผลกับ Pod ที่ไม่ใส่ resources: ได้ค่า default + annotation `kubernetes.io/limit-ranger: LimitRanger plugin set: ...` (ผล pre-check); ใส่เกิน max → `maximum cpu usage per Container is 500m, but limit is 1`; ใช้กับ init container ด้วย
    - ใช้คู่ quota: LimitRange เติมค่าให้ Pod ที่ลืม → ผ่านเงื่อนไข "must specify" ของ quota; ตารางเทียบ quota (รวมทั้งโซน) vs LimitRange (ต่อกล่อง)
13. **RBAC แบบ namespace** (T29–T33)
    - 13.1 ใครเป็นผู้เรียก API: User (คน — Kubernetes ไม่มี object User, มาจาก cert/OIDC), ServiceAccount (ตัวตนของโปรแกรม/Pod เป็น namespaced object, ทุก namespace มี `default`), Group (`system:serviceaccounts:<ns>`); ชื่อเต็ม SA `system:serviceaccount:<ns>:<name>`
    - 13.2 Role (rules: `apiGroups`, `resources` รวม subresource `pods/log`, `verbs` get/list/watch/create/update/patch/delete) + RoleBinding (`subjects` + `roleRef`, roleRef แก้ไม่ได้) — มีผลเฉพาะ namespace ของ binding; RBAC เป็น allow-only (ไม่มี deny)
    - 13.3 ClusterRole + RoleBinding = ใช้กฎมาตรฐานแค่ใน namespace เดียว (ClusterRole สำเร็จรูป `view`, `edit`, `admin`); ClusterRoleBinding = ทั้งคลัสเตอร์ (ระวัง); `cluster-admin` ของ kind คือเรา (`kubectl auth whoami`)
    - 13.4 ตรวจสิทธิ์: `kubectl auth can-i <verb> <resource> -n <ns> --as=system:serviceaccount:<ns>:<sa>`, `--list`, ข้อความ Forbidden จริง (`User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"`)
    - 13.5 ใช้ตัวตนของ SA จริง: `kubectl create token intern -n <ns> --duration=1h` (token อายุสั้น), สร้าง user + context ใน kubeconfig แล้ว `--context`; **กับดัก**: `kubectl --token=...` บน kubeconfig ที่มี client cert ยังเป็น admin (pre-check); Pod ใช้ SA ผ่าน `spec.serviceAccountName` (token ถูก mount ที่ `/var/run/secrets/kubernetes.io/serviceaccount/`) กล่าวถึง
14. **Pod Security Admission: ด่านตรวจหน้าโซน** (T34–T36)
    - Pod Security Standards 3 ระดับ: `privileged` (ไม่จำกัด), `baseline` (ห้าม privileged, hostNetwork/hostPID/hostPath, เพิ่ม capability อันตราย ฯลฯ), `restricted` (baseline + runAsNonRoot, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, seccompProfile RuntimeDefault/Localhost, volume บางชนิด)
    - 3 โหมดผ่าน label namespace: `pod-security.kubernetes.io/enforce` (ปฏิเสธ), `warn` (สร้างได้แต่เตือนที่ kubectl), `audit` (บันทึกใน audit log) + `-version` (`latest` หรือ `v1.37`)
    - ตรวจตอนสร้าง Pod เท่านั้น: ติด label ทีหลัง Pod เดิมยังรันแต่ได้คำเตือน (`existing pods in namespace ... violate the new PodSecurity enforce level "restricted:latest"` — pre-check); ใช้ `kubectl label --dry-run=server` ตรวจก่อนบังคับจริง
    - ข้อความ Forbidden ของ restricted (ผล pre-check) และวิธีแก้ทีละข้อด้วย `securityContext`; image ที่ USER เป็นชื่อ (เช่น `node`) ต้องใส่ `runAsUser` เป็นตัวเลข (ยืนยันใน LAB10); nginx ทางการรันเป็น root จึงไม่ผ่าน restricted
    - PSA แทน PodSecurityPolicy (ถูกถอดตั้งแต่ v1.25)
15. **แนวปฏิบัติการตั้งชื่อและแบ่ง namespace** (T37)
    - แบ่งตามทีม / environment / แอป / ทีม+environment (`som-dev`, `som-prod`); อย่าแบ่งละเอียดเกินไป; label มาตรฐาน `env`, `team`, `app.kubernetes.io/part-of`
    - ทุก namespace ใหม่ควรมี "ชุดตั้งต้น": quota + LimitRange + RoleBinding + PSA label (+ NetworkPolicy); prod แยกคลัสเตอร์เมื่อต้องการแยกขาดจริง
    - อย่าใช้ `default` กับงานจริง, ระวัง `kubectl delete ns` (ลบทั้งก้อน), ใส่ `-n` ชัดเจนในสคริปต์
16. **สรุปและคำถามทบทวน** (T38) + ตารางสรุปคำสั่งและแนวคิด (คำสั่ง → ใช้ทำอะไร → namespaced?) + ตารางเทียบนโยบาย 5 ชนิด (NetworkPolicy/Quota/LimitRange/RBAC/PSA: ควบคุมอะไร, ตรวจเมื่อไร, ผลเมื่อผิด) + เอกสารอ้างอิง (kubernetes.io: Namespaces, Share a Cluster with Namespaces, Organizing Cluster Access Using kubeconfig Files, Network Policies, Resource Quotas, Limit Ranges, Using RBAC Authorization, Service Accounts, Pod Security Standards, Pod Security Admission, Enforce Pod Security Standards with Namespace Labels)

## 2. รายการ LAB (`02_LAB/README.md`)

```text
02_LAB/
  README.md
  images/ (L01–L23 + imagegen-prompts.md)
  labs/
    lab01-create-ns/{ns-blue.yaml, snack-pod.yaml (ไม่มี metadata.namespace), snack-green-pod.yaml (metadata.namespace: green)}
    lab03-scope/            (ไม่มีไฟล์ ใช้คำสั่งล้วน)
    lab04-network/{zones.yaml (ns team-a, team-b), web-pod.yaml, client-pods.yaml, np-same-ns.yaml, np-allow-team-b.yaml}
    lab05-quota/{quota.yaml, no-request-pod.yaml, small-pods.yaml}
    lab06-limitrange/{limitrange.yaml, plain-pod.yaml, big-pod.yaml}
    lab07-rbac/{sa-role-binding.yaml, view-clusterrole-binding.yaml}
    lab08-psa/{root-nginx-pod.yaml, privileged-pod.yaml, restricted-ok-pod.yaml}
    lab09-delete-ns/{doomed.yaml}
  som-shop-envs/
    app/        (สำเนาจาก 002_kubernetes_pod/02_LAB/som-shop/app ไม่แก้โค้ด)
    k8s/{00-namespaces.yaml, som-shop.yaml, som-shop-v002.yaml (สำเนาเดิมบท 002 ไว้ทดสอบกับ prod), prod-guardrails.yaml, intern-rbac.yaml}
```

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ |
|---|---|---|---|---|---|---|
| 0 | สำรวจโซนเริ่มต้น | เตรียมคลัสเตอร์/ไฟล์ เห็น namespace ที่มีอยู่และของข้างใน | – | `k8s-up` (ถ้าจำเป็น), `kubectl get ns --show-labels`, `kubectl get pods -A -o wide`, `kubectl get pods -n kube-system`, `kubectl get cm -n kube-public`, `kubectl get lease -n kube-node-lease`, `kubectl get sa,cm -n default`, `kubectl describe ns default` | 5 namespace (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`) แต่ละตัวมี label `kubernetes.io/metadata.name`; kube-system มี etcd/apiserver/scheduler/controller-manager/coredns×2/kindnet×3/kube-proxy×3; kube-public ไม่มี Pod มี `cluster-info`; lease 3 ตัว | จำนวน/ชื่อ Pod ใน kube-system จริง, `describe ns default` แสดง `No resource quota.` / `No LimitRange resource.` หรือไม่, อายุ (AGE) |
| 1 | สร้าง/ลบ namespace + Pod ชื่อซ้ำ | สร้าง ns 2 วิธี, Pod ชื่อเดียวกันใน 2 ns, เข้าใจ metadata.namespace vs -n | `lab01-create-ns/ns-blue.yaml`, `snack-pod.yaml` (busybox `snack`), `snack-green-pod.yaml` | `kubectl create ns green`, `kubectl apply -f ns-blue.yaml`, `kubectl apply -f snack-pod.yaml -n blue`, `... -n green`, `kubectl apply -f snack-pod.yaml` (ไป default), `kubectl apply -f snack-green-pod.yaml -n blue` (ไม่ตรง), `kubectl get pods -A -l app=snack`, `kubectl get pod snack -n blue -o jsonpath='{.metadata.namespace}'`, `kubectl create -f snack-pod.yaml -n blue` (ซ้ำ) | `snack` 3 ตัวใน blue/green/default ไม่ชนกัน; คำสั่งที่ไม่ตรงได้ error; สร้างซ้ำใน ns เดียวได้ `AlreadyExists` | **ข้อความจริง** ของ namespace mismatch (คาด `error: the namespace from the provided object "green" does not match the namespace "blue". You must pass '--namespace=green' to perform this operation.`), ข้อความ AlreadyExists |
| 2 | เปลี่ยน namespace เริ่มต้นของ context | อ่าน kubeconfig/context และสลับ namespace เริ่มต้น | – | `kubectl config get-contexts`, `kubectl config view --minify`, `kubectl config set-context --current --namespace=blue`, `kubectl get pods` (เห็น snack ของ blue), `kubectl run peek --image=busybox:1.36 -- sleep 3600` (ไป blue), `kubectl config view --minify -o jsonpath='{..namespace}'`, คืน `--namespace=default` | คอลัมน์ NAMESPACE ใน get-contexts เปลี่ยนจากว่างเป็น `blue`; Pod ใหม่ไปอยู่ blue | output ของ get-contexts ก่อน/หลัง (ว่างหรือ `default`), kubeconfig ของ kind มี client-certificate-data (ใช้อธิบาย LAB7) |
| 3 | ของประจำโซน vs ของส่วนกลาง | แยก namespaced/cluster-scoped และเห็นว่า -n ไม่มีผลกับ cluster-scoped | – | `kubectl api-resources --namespaced=true \| head`, `--namespaced=false`, `kubectl api-resources --namespaced=true -o name \| wc -l`, `kubectl get nodes -n blue`, `kubectl get sc`, `kubectl get pv`, `kubectl get priorityclass`, `kubectl get ns blue -n green` | namespaced 34 ชนิด, cluster-scoped มี nodes/namespaces/persistentvolumes/storageclasses/priorityclasses/clusterroles; `get nodes -n blue` ได้ 3 node เหมือนเดิม; sc `standard (default)` | จำนวน 34 คงที่ไหมในคลัสเตอร์นักศึกษา, ชื่อ priorityclass ที่มี (`system-cluster-critical`, `system-node-critical`) |
| 4 | ข้ามโซน: Pod IP, Node เดียวกัน และ NetworkPolicy | เห็นว่า ns ไม่แยก network/node แล้วสร้างรั้วด้วย NetworkPolicy | `lab04-network/zones.yaml`, `web-pod.yaml` (nginx `web` ใน team-a, nodeSelector `kubernetes.io/hostname: lab-worker`), `client-pods.yaml` (busybox `client` ใน team-a และ team-b บน lab-worker ทั้งคู่), `np-same-ns.yaml`, `np-allow-team-b.yaml` | `kubectl get pods -A -o wide -l lab=net`, `kubectl -n team-b exec client -- wget -qO- -T 3 http://<IP>`, `kubectl -n team-b exec client -- cat /etc/resolv.conf`, `kubectl apply -f np-same-ns.yaml`, ทดสอบซ้ำจาก team-a/team-b, `kubectl apply -f np-allow-team-b.yaml`, `kubectl get netpol -n team-a`, `kubectl describe netpol` | ก่อน policy: team-b เข้า web ได้ และ Pod ทั้ง 2 ns อยู่บน lab-worker; resolv.conf มี `search team-b.svc.cluster.local ...`; หลัง np-same-ns: team-b `wget: download timed out` exit 1, team-a ยังได้; หลัง allow: team-b ได้อีกครั้ง | (pre-check ผ่านแล้ว) ยืนยันเวลาที่ policy มีผล (≤5 วิ), ข้อความ timeout, บรรทัด search ของ resolv.conf จริง |
| 5 | ResourceQuota | ตั้งงบให้โซนแล้วเห็นการปฏิเสธ | `lab05-quota/quota.yaml` (ns `budget`: `pods: 3`, `requests.cpu: 500m`, `requests.memory: 256Mi`, `limits.cpu: 1`, `limits.memory: 512Mi`), `no-request-pod.yaml`, `small-pods.yaml` (busybox 4 ตัว req 100m/64Mi lim 200m/128Mi) | `kubectl apply -f quota.yaml`, `kubectl describe quota -n budget`, `kubectl apply -f no-request-pod.yaml`, `kubectl apply -f small-pods.yaml`, `kubectl get pods -n budget`, `kubectl describe quota -n budget` | no-request ถูกปฏิเสธ `must specify limits.cpu for: ...,limits.memory,requests.cpu,requests.memory`; small-pods สร้างได้ 3 ตัว ตัวที่ 4 `exceeded quota ... pods=1, used: pods=3, limited: pods=3`; Used 3/3, 300m/500m | ลำดับคำใน "must specify" (หลาย resource), ตัวที่ 4 ชน `pods` หรือ `limits.memory` ก่อน (คำนวณ: 4×128Mi = 512Mi พอดี → ต้องชน pods) |
| 6 | LimitRange | เห็นค่า default ถูกเติมและ max ถูกบังคับ, ใช้คู่ quota | `lab06-limitrange/limitrange.yaml` (ใน ns `budget`: default 200m/128Mi, defaultRequest 100m/64Mi, max 500m/256Mi), `plain-pod.yaml`, `big-pod.yaml` (limit cpu 1) | ลบ small-pods 2 ตัว, `kubectl apply -f limitrange.yaml`, `kubectl describe limitrange -n budget`, `kubectl apply -f no-request-pod.yaml` (คราวนี้ผ่าน), `kubectl get pod no-request -n budget -o jsonpath='{.spec.containers[0].resources}'`, annotation limit-ranger, `kubectl apply -f big-pod.yaml` | no-request ผ่านและได้ `{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}`; big-pod `maximum cpu usage per Container is 500m, but limit is 1` | ข้อความจริงกรณีมีทั้ง LimitRange และ quota (quota ตรวจหลัง LimitRange เติมค่า), describe limitrange format |
| 7 | RBAC: บัตรพนักงานเฉพาะโซน | สร้าง SA + Role + RoleBinding ตรวจด้วย can-i/--as และใช้ token จริงผ่าน context | `lab07-rbac/sa-role-binding.yaml` (ns `team-a`: SA `intern`, Role `pod-reader` get/list/watch pods, pods/log, RoleBinding), `view-clusterrole-binding.yaml` (RoleBinding ClusterRole `view` ให้ SA `auditor` ใน team-b) | `kubectl auth whoami`, `kubectl apply -f ...`, `kubectl auth can-i list pods -n team-a --as=system:serviceaccount:team-a:intern`, `can-i delete pods`, `can-i get pods/log`, `can-i list pods -n team-b`, `--list`, `kubectl delete pod web -n team-a --as=...`, `T=$(kubectl create token intern -n team-a --duration=1h)`, `kubectl --token=$T get pods -n team-b` (กับดัก), `kubectl config set-credentials intern --token=$T`, `kubectl config set-context intern@lab --cluster=kind-lab --user=intern --namespace=team-a`, `kubectl --context intern@lab get pods`, `logs web`, `delete pod web`, `get pods -n team-b`, `auth whoami` | can-i: yes / no / yes / no; delete → Forbidden ข้อความเต็ม; `--token` ยังเห็น team-b (เพราะ cert มาก่อน); ผ่าน context intern: ns ตัวเองได้, delete และ ns อื่น Forbidden, whoami = `system:serviceaccount:team-a:intern`; auditor ดูได้แต่ team-b | (pre-check ผ่านแล้ว) ยืนยัน `logs` ผ่าน context intern ได้จริง, `--list` output, ClusterRole `view` + RoleBinding ใช้ได้เฉพาะ team-b; เก็บกวาด context/user (`kubectl config delete-context/delete-user`) |
| 8 | Pod Security Admission | ใช้ label namespace บังคับระดับความปลอดภัย, เห็น warn/enforce | `lab08-psa/root-nginx-pod.yaml`, `privileged-pod.yaml` (busybox `securityContext.privileged: true`), `restricted-ok-pod.yaml` (busybox runAsNonRoot/runAsUser 1000/drop ALL/no escalation/seccomp RuntimeDefault) | `kubectl create ns secure`, `kubectl label ns secure pod-security.kubernetes.io/enforce=baseline pod-security.kubernetes.io/warn=restricted`, apply root-nginx (ผ่าน + Warning), apply privileged (Forbidden baseline), `kubectl label --dry-run=server --overwrite ns secure pod-security.kubernetes.io/enforce=restricted`, label จริง, apply root-nginx ใหม่ชื่ออื่น (Forbidden restricted), apply restricted-ok (ผ่าน), `kubectl exec restricted-ok -- id` | baseline: nginx root ผ่านแต่มี `Warning: would violate PodSecurity "restricted:latest": ...`; privileged ถูกปฏิเสธ `violates PodSecurity "baseline:latest": privileged (container ... must not set securityContext.privileged=true)`; dry-run เตือนว่า Pod เดิมผิด; restricted: nginx Forbidden (ข้อความ 4 ข้อ), restricted-ok Running `uid=1000` | ข้อความ Warning/Forbidden ของ baseline จริง, ผล dry-run=server, nginx เดิมยังรันหลังเปลี่ยนเป็น restricted |
| 9 | ลบโซนทั้งก้อน | เห็นว่าลบ ns = ลบทุกอย่างข้างใน และสถานะ Terminating | `lab09-delete-ns/doomed.yaml` (ns `doomed` + Pod busybox 2 ตัว + SA + Role + RoleBinding + ConfigMap + quota) | `kubectl apply -f doomed.yaml`, `kubectl get all,sa,role,rolebinding,cm,quota -n doomed`, `kubectl delete ns doomed --wait=false`, `kubectl get ns doomed -o jsonpath='{.status.phase}'`, `kubectl run x -n doomed --image=busybox:1.36` ระหว่าง Terminating, `kubectl get ns doomed -o jsonpath='{.spec.finalizers}'`, `time kubectl wait --for=delete ns/doomed --timeout=120s`, `kubectl get ns`, ลบ ns อื่นของ LAB0–8 ทั้งหมด | Terminating แล้วหาย; สร้าง Pod ระหว่างนั้นถูกปฏิเสธ; ns อื่นไม่กระทบ; Node ยังอยู่ | ข้อความ forbidden ระหว่าง Terminating (ต้องจับให้ทัน — Pod busybox grace 1 วิอาจลบเร็วมาก ให้ใส่ Pod nginx หรือ grace 10 วิ เพื่อให้ Terminating นานพอ), เวลาที่ใช้ลบ, `get all` แสดง ConfigMap `kube-root-ca.crt` ด้วยไหม |
| 10 | LAB สุดท้าย: ร้านน้องส้มแยก environment | รวมทุกอย่าง: ns + label, manifest เดียวหลาย ns, Downward API namespace, quota + LimitRange + PSA restricted ใน prod, RBAC intern, port-forward หลาย env, ลบ env ทั้งก้อน | `som-shop-envs/` | ดูหัวข้อ 3 | ดูหัวข้อ 3 | ดูหัวข้อ 3.6 |

## 3. LAB สุดท้าย — "ร้านน้องส้มแยก environment" (LAB10)

### 3.1 แนวคิดและเหตุผลการออกแบบ

- ร้านเดียวกัน 3 environment ในคลัสเตอร์เดียว: `som-dev` (ทดลองของใหม่), `som-staging` (ทดสอบก่อนขึ้นจริง), `som-prod` (ร้านจริง)
- **Pod ชื่อ `som-shop` เหมือนกันทุก namespace จาก manifest ไฟล์เดียว** (`som-shop.yaml` ไม่มี `metadata.namespace`) → ใช้ `-n` เลือก environment = แสดงประโยชน์ของ namespace ด้านชื่อ
- `SHOP_NAME` บอก environment อัตโนมัติด้วย Downward API `metadata.namespace` → `POD_NAMESPACE` → `"ร้านอาหารแมวน้องส้ม ($(POD_NAMESPACE))"` (ต่อจากบท 003 ที่ใช้ `spec.nodeName`) — ไฟล์เดียวแต่หน้าร้านแต่ละ env แสดงต่างกัน
- prod เข้มงวด: ResourceQuota + LimitRange + PSA `enforce=restricted`; dev/staging ใช้ `warn=restricted` อย่างเดียว (เห็นคำเตือนแต่ไม่บล็อก) — สะท้อนชีวิตจริง
- `som-shop.yaml` ปรับ securityContext ให้ผ่าน restricted (pre-check ยืนยันว่า postgres ทำได้) และเก็บ `som-shop-v002.yaml` (ฉบับบท 002 ไม่มี securityContext) ไว้ลอง apply เข้า prod เพื่อเห็นด่านปฏิเสธ
- RBAC: SA `intern` ใน som-dev ดูได้อย่างเดียว (get/list/watch pods + pods/log) เฉพาะ som-dev → ทดสอบด้วย `can-i --as` และ context ที่ใช้ token จริง
- จบด้วยลบ `som-dev` ทั้ง namespace: Pod, SA intern, Role, RoleBinding หายหมด แต่ staging/prod ยังเปิดอยู่
- ไม่มี NetworkPolicy ใน LAB สุดท้าย (เรียนแล้วใน LAB4; ร้านแต่ละ Pod คุยกับ db ผ่าน localhost ภายใน Pod อยู่แล้ว) — มีเป็น "โจทย์ท้าทาย" ทางเลือก: กั้น ingress ของ som-prod ให้รับเฉพาะ Pod ใน som-prod แล้วยืนยันว่า port-forward ยังใช้ได้ (port-forward ไม่ผ่าน Pod network ปกติ — ต้องยืนยันถ้าจะใส่)

### 3.2 ไฟล์

- `k8s/00-namespaces.yaml`: Namespace 3 ตัว
  - `som-dev`: labels `env: dev`, `team: som`, `pod-security.kubernetes.io/warn: restricted`
  - `som-staging`: `env: staging`, `team: som`, `pod-security.kubernetes.io/warn: restricted`
  - `som-prod`: `env: prod`, `team: som`, `pod-security.kubernetes.io/enforce: restricted`, `pod-security.kubernetes.io/enforce-version: latest`, `pod-security.kubernetes.io/warn: restricted`
- `k8s/prod-guardrails.yaml` (`metadata.namespace: som-prod` ทั้งคู่ เพราะเป็นของ prod เท่านั้น)
  - ResourceQuota `prod-budget`: `pods: "2"`, `requests.cpu: "1"`, `requests.memory: 1Gi`, `limits.cpu: "2"`, `limits.memory: 2Gi`
  - LimitRange `prod-box-size` (Container): `defaultRequest` 50m/64Mi, `default` 200m/128Mi, `max` cpu 1 / memory 1Gi
- `k8s/som-shop.yaml`: ดัดแปลงจาก `003.../som-shop-a.yaml` (ตัด affinity/tolerations ออก) + เพิ่ม
  - pod `securityContext`: `runAsNonRoot: true`, `fsGroup: 70`, `seccompProfile: {type: RuntimeDefault}`
  - container `db`, `wait-for-db`: `runAsUser: 70`, `runAsGroup: 70`; `db-seed`, `web`: `runAsUser: 1000`, `runAsGroup: 1000` (image `USER node` เป็นชื่อ → ต้องเป็นตัวเลข); ทุก container `allowPrivilegeEscalation: false`, `capabilities: {drop: ["ALL"]}`
  - env `POD_NAMESPACE` (fieldRef `metadata.namespace`) ประกาศก่อน `SHOP_NAME: "ร้านอาหารแมวน้องส้ม ($(POD_NAMESPACE))"`; label `app: som-shop`
  - resources เดิม (ทุก container มี requests/limits อยู่แล้ว → ผ่าน quota)
- `k8s/som-shop-v002.yaml`: สำเนา Pod บท 002 เปลี่ยนชื่อเป็น `som-shop-old`
- `k8s/intern-rbac.yaml` (ใน som-dev): SA `intern`, Role `shop-viewer` (`pods`, `pods/log`: get/list/watch), RoleBinding `intern-shop-viewer`

### 3.3 ขั้นตอน

1. เตรียม image: `cd som-shop-envs/app && docker build -t som-shop-web:1.0 .` (ถ้ายังไม่มีจากบท 002/003) → `kind load docker-image som-shop-web:1.0 --name lab`; postgres ด้วย `docker save --platform linux/amd64` + `kind load image-archive`
2. `kubectl apply -f k8s/00-namespaces.yaml` → `kubectl get ns -l team=som -L env` (3 แถว env dev/staging/prod)
3. `kubectl apply -f k8s/prod-guardrails.yaml` → `kubectl describe quota,limitrange -n som-prod`
4. ลองของเก่าเข้า prod: `kubectl apply -f k8s/som-shop-v002.yaml -n som-prod` → **Forbidden** violates PodSecurity "restricted:latest" (รายการ container ทั้ง 4: db, wait-for-db, db-seed, web)
5. เปิดร้าน 3 env จากไฟล์เดียว: `for ns in som-dev som-staging som-prod; do kubectl apply -f k8s/som-shop.yaml -n $ns; done` → `kubectl get pods -A -l app=som-shop -o wide` (3 แถว ชื่อ som-shop เหมือนกัน คนละ NAMESPACE, อาจอยู่ Node เดียวกัน) รอ `2/2 Running`
6. ตรวจ env: `kubectl exec -n som-staging som-shop -c web -- printenv SHOP_NAME` → `ร้านอาหารแมวน้องส้ม (som-staging)`; `kubectl exec -n som-prod som-shop -c web -- id` → `uid=1000(node)`; `kubectl exec -n som-prod som-shop -c db -- id` → `uid=70(postgres)`
7. quota ของ prod: `kubectl describe quota prod-budget -n som-prod` (Used ≈ pods 1/2, requests.cpu 200m, requests.memory 448Mi, limits.cpu 1, limits.memory 1Gi) → ลองสาขาที่สอง `sed 's/name: som-shop$/name: som-shop-2/' k8s/som-shop.yaml | kubectl apply -n som-prod -f -` → ผ่าน (pods 2/2, limits.memory 2Gi/2Gi) → สาขาที่สาม `som-shop-3` → **exceeded quota** แล้วลบ som-shop-2
8. LimitRange: `kubectl run debug -n som-prod --image=busybox:1.36 ...` แบบไม่ใส่ resources → ถูก PSA ปฏิเสธก่อน (ไม่มี securityContext) → ใช้ `--overrides` ใส่ securityContext restricted แล้วดู resources ที่ LimitRange เติมให้ (ทางเลือก ถ้ายาวเกินให้ย้ายเป็น "ลองเพิ่มเติม")
9. RBAC intern: `kubectl apply -f k8s/intern-rbac.yaml`; ตาราง can-i: `get pods -n som-dev` yes, `get pods/log -n som-dev` yes, `delete pods -n som-dev` no, `get pods -n som-prod` no, `create pods -n som-dev` no (ทั้งหมด `--as=system:serviceaccount:som-dev:intern`); จากนั้นสร้าง token + context `intern@som-dev` → `kubectl --context intern@som-dev get pods`, `logs som-shop -c web --tail=5` ได้, `delete pod som-shop` Forbidden, `get pods -n som-prod` Forbidden
10. เปิดหน้าร้าน 3 env (3 terminal หรือ background `&`): `kubectl port-forward -n som-dev pod/som-shop 3001:3000`, `-n som-staging ... 3002:3000`, `-n som-prod ... 3003:3000` → บนเครื่องนักศึกษา `ssh -p 2223 -L 3001:localhost:3001 -L 3002:localhost:3002 -L 3003:localhost:3003 root@localhost` → เปิด `http://localhost:3001` / `3002` / `3003` (หัวร้านแสดง som-dev / som-staging / som-prod) สั่งซื้อใน dev แล้ว stock ของ prod ไม่เปลี่ยน (แต่ละ env มี db ของตัวเอง) — **screenshot ทีหลัง**
11. ลบ dev ทั้งก้อน: `kubectl delete ns som-dev` → port-forward 3001 หลุด, `kubectl get pods -A -l app=som-shop` เหลือ 2, `kubectl get sa intern -n som-dev` NotFound, `kubectl --context intern@som-dev get pods` ใช้ไม่ได้, `http://localhost:3003` ยังเปิดได้
12. เก็บกวาด: `kubectl delete ns som-staging som-prod`, `kubectl config delete-context intern@som-dev`, `kubectl config delete-user intern`

### 3.4 ผลที่ต้องเห็น

- `get ns -l team=som -L env`: 3 namespace พร้อม env
- `som-shop-v002.yaml` ใน prod ถูกปฏิเสธโดย PSA; `som-shop.yaml` ผ่านทั้ง 3 env และ `2/2 Running` (dev/staging ไม่มี Warning เพราะไฟล์ผ่าน restricted แล้ว)
- 3 Pod ชื่อ `som-shop` คนละ namespace; `SHOP_NAME` ต่างกันตาม namespace; หน้าร้านแต่ละ port แสดงชื่อ env และข้อมูลแยกกัน
- quota prod: สาขาที่ 3 ถูกปฏิเสธ `exceeded quota: prod-budget, ...`
- intern: can-i ตรงตาราง และ context intern ทำได้แค่ดูใน som-dev
- หลังลบ som-dev: ของใน som-dev หายหมด (รวม SA/Role/RoleBinding), prod ยังให้บริการ

### 3.5 ภาพ screenshot ที่จะเก็บตอนทดสอบจริง (ไม่ใช่ภาพ imagegen)

- terminal: `get pods -A -l app=som-shop -o wide`, Forbidden ของ PSA, describe quota, ตาราง can-i
- browser 3 แท็บ `localhost:3001/3002/3003` (หัวร้านคนละ env)
- terminal หลังลบ som-dev

### 3.6 จุดที่ต้องยืนยันตอนทดสอบจริง

1. **som-shop ทั้ง Pod ผ่าน PSA restricted** (sidecar `db` + init `wait-for-db`, `db-seed` + `web`): `runAsUser: 1000` ของ web/db-seed ทำงานกับ `/app` ที่ chown เป็น node ได้, Next.js standalone ไม่ต้องเขียนไฟล์นอก `/tmp`; ถ้าไม่ใส่ `runAsUser` ต้องเห็น `CreateContainerConfigError` (`image has non-numeric user (node), cannot verify user is non-root`) — ใช้เป็นจุดสอนได้ถ้าเกิดจริง
2. postgres ใน som-shop ด้วย `fsGroup: 70` + PGDATA บน emptyDir ผ่าน (pre-check ผ่านแบบ container เดียว) และ `pg_isready` probe ยังทำงานเมื่อ drop ALL capabilities
3. ข้อความ Forbidden จริงเมื่อ apply `som-shop-v002.yaml` เข้า som-prod (ยาวมาก ต้องเลือกตัดใน README)
4. ค่า Used ของ quota จริงสำหรับ Pod ที่มี sidecar/init (คาด requests.cpu 200m, requests.memory 448Mi, limits.cpu 1, limits.memory 1Gi) และสาขาที่ 3 ชน `pods` หรือ `limits.memory` (คาดชนทั้งคู่ ข้อความจะระบุทุกตัวที่เกิน)
5. LimitRange `max` ใช้กับ init container ด้วย — ค่าของ som-shop ต้องไม่เกิน max (db limit 500m/512Mi < 1/1Gi ✓)
6. `kubectl logs` ผ่าน context intern ต้องมีสิทธิ์ `pods/log` (pre-check ทดสอบแค่ get/list); `kubectl logs som-shop` (ไม่ระบุ -c) ต้อง get pod ด้วย ✓
7. หลังลบ som-dev: token ของ intern ใช้ไม่ได้ (คาด `error: You must be logged in to the server (Unauthorized)`) — ข้อความจริง
8. port-forward 3 ตัวพร้อมกัน + ssh -L 3 port ใช้ได้, ภาษาไทยใน SHOP_NAME แสดงถูกในหัวร้าน (บท 003 ยืนยันว่า SHOP_NAME + Downward API แสดงถูก)
9. เวลา Terminating ของ som-dev (postgres มี grace 30 วิ → คาด ~30 วิ) — บอกให้รอ
10. resource ของ 3 env + เครื่องนักศึกษา: 3 Pod som-shop requests รวม ~600m/1.3Gi ใน kind — ไม่น่ามีปัญหาแต่ให้ยืนยันว่าไม่ Pending

## 4. งานถัดไป (หลังอนุมัติแผน)

1. สร้างภาพจาก `images.json` (สคริปต์ `gen_images.sh` มีแล้ว) → ตรวจภาพ (ป้ายสะกด, น้องส้มตรง reference, ไม่มีของนอกเรื่อง) → ภาพที่มี `needs_test: true` สร้างหลังทดสอบ LAB จริงหรือปรับ prompt ตามผล
2. เขียนไฟล์ LAB + README ทฤษฎี/LAB + README หน้ารวม
3. รัน LAB0–10 ใน container ชั่วคราว (skill k8s-lab) บันทึก `logs/004_namespace/lab-run/SUMMARY.md` แล้วแก้ README ด้วยผลจริง

## 5. สรุป storyboard

- Theory 38 ภาพ (T01–T38) ตามช่วงที่ระบุในสารบัญหัวข้อ 1
- LAB 23 ภาพ: LAB0 L01–L02, LAB1 L03–L04, LAB2 L05, LAB3 L06, LAB4 L07–L08, LAB5 L09, LAB6 L10, LAB7 L11–L12, LAB8 L13, LAB9 L14, LAB10 L15–L23 (9 ภาพ)
- `needs_test: true` (สร้าง/ปรับ prompt หลังรัน LAB จริง): **L18** ร้านฉบับเก่าถูก restricted ปฏิเสธ / ฉบับใหม่ uid 70/1000 ผ่าน, **L19** quota สาขาที่ 3, **L21** port-forward 3 env + ssh -L, **L22** ลบ som-dev แล้ว staging/prod ยังอยู่
- ภาพที่อิงผล pre-check แล้ว (NetworkPolicy L08, quota L09, LimitRange L10, RBAC/--token L11–L12, PSA L13) ไม่ติด needs_test แต่ให้ตรวจป้ายอีกครั้งหลังรัน LAB
