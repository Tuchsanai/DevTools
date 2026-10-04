# แผนบทเรียน 003 — Node กับ Pod (Pod ไปอยู่บนเรือลำไหน และเราควบคุมได้อย่างไร)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB และยังไม่รัน LAB)
> Storyboard ภาพ: `logs/003_node_pod/images.json` (Theory 39 ภาพ T01–T39, LAB 22 ภาพ L01–L22)
> ภาพตัวละครอ้างอิง: `002_kubernetes_pod/01_Theory/images/00-character-som.png` (คัดลอกไว้ที่ `003_kubernetes_node_pod/01_Theory/images/00-character-som.png` แล้ว)

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่านบท 001 (สถาปัตยกรรม, container `k8s-lab`) และบท 002 (Pod, YAML, labels, resources, probes, multi-container, LAB ร้าน som-shop) แล้ว
- เข้าเครื่อง: `ssh -p 2223 root@localhost` (รหัส `passwd`) หรือ JupyterLab `http://localhost:8889`; คลัสเตอร์ kind `lab` (`lab-control-plane` + `lab-worker` + `lab-worker2`, context `kind-lab`, K8s v1.37) — ถ้ายังไม่มีหรือเพิ่งรีสตาร์ท container ให้ `k8s-up` (LAB0)
- โฟลเดอร์ LAB ใน container: `docker cp 003_kubernetes_node_pod k8s-lab:/workspace/` แล้ว `cd /workspace/003_kubernetes_node_pod/02_LAB` (แบบเดียวกับบท 002)
- **ห้ามใช้ Service / NodePort / Deployment / ReplicaSet / DaemonSet / Ingress ใน LAB** — ใช้ Pod เดี่ยวหลายตัวแทน; การเข้าถึงแอปใช้ `exec`, `logs`, `port-forward` + `ssh -L` เหมือนบท 002
  - ข้อยกเว้นที่ต้องอธิบายสั้น ๆ: `kubectl drain --ignore-daemonsets` (บน worker มี Pod ระบบ `kube-proxy`, `kindnet` ที่ "ระบบดูแลให้ทุกเรือมีหนึ่งตัว" — บอกแค่ว่าเป็น DaemonSet ซึ่งจะเรียนภายหลัง)
- **คำสั่ง `docker ...` ใน LAB รันใน SSH session ของ k8s-lab** (dockerd ภายใน k8s-lab คือที่อยู่ของ node container `lab-*`) ไม่ใช่บนเครื่องนักศึกษา ยกเว้น `docker cp`/`docker exec k8s-lab` ตอนเตรียมไฟล์
- ทุก LAB จบด้วยการลบ Pod/label/taint ที่สร้าง และ `uncordon` คืน (มีบล็อก "เก็บกวาด" ท้ายทุก LAB + ตารางคำสั่งคืนสภาพรวมท้าย README)

### อุปมา (ต่อจากบท 001–002 + ของใหม่บทนี้)

| Kubernetes | อุปมาท่าเรือ | ใหม่? |
|---|---|---|
| container | ตู้สินค้า | – |
| Pod | กล่องห้องโดยสารใสสี teal ห่อตู้ มีป้าย IP 1 ป้าย | – |
| Node | เรือสินค้า (`lab-worker`, `lab-worker2`) | – |
| Control Plane | หอบังคับการบนท่า (`lab-control-plane`) | – |
| kube-scheduler | เจ้าหน้าที่จัดตู้ขึ้นเรือ (ถือ clipboard ตรวจเรือ) | – |
| kubelet | ต้นเรือ (first mate) ประจำเรือแต่ละลำ | – |
| container runtime (containerd) | ห้องเครื่อง/เครนบนเรือที่ยกตู้จริง | ใหม่ |
| kube-proxy | นายท่าจราจรบนเรือ (ปูทาง Service — กล่าวถึงเท่านั้น) | ใหม่ |
| Node object / status | สมุดประจำเรือ (ทะเบียนเรือ) | ใหม่ |
| capacity / allocatable | ระวางเรือทั้งหมด / ระวางที่ขายให้ลูกค้าได้ (หักส่วนของลูกเรือ) | ใหม่ |
| node conditions | ไฟแสดงสถานะบนแผงเรือ (Ready, MemoryPressure, DiskPressure, PIDPressure) | ใหม่ |
| node label | ธง/ป้ายบนเสากระโดงเรือ | ใหม่ |
| nodeSelector | ใบสั่ง "ต้องขึ้นเรือที่มีธงนี้" | ใหม่ |
| node affinity | แม่เหล็กดึงกล่องไปหาธงเรือ (required = ต้อง, preferred = อยากได้) | ใหม่ |
| pod affinity / anti-affinity | แม่เหล็กดึงดูด / ผลัก ระหว่างกล่อง | ใหม่ |
| topologyKey | เส้นแบ่งเขต "ถือว่าเป็นที่เดียวกัน" (เรือลำเดียวกัน / ท่าเดียวกัน) | ใหม่ |
| topologySpreadConstraints | ตาชั่งถ่วงน้ำหนักให้กองเรือสมดุล | ใหม่ |
| taint | ป้าย "ห้ามขึ้น" ที่ขอบเรือ | ใหม่ |
| toleration | บัตรผ่าน (มีบัตร = ขึ้นได้ ไม่ได้แปลว่าต้องขึ้น) | ใหม่ |
| NoExecute + tolerationSeconds | ป้ายไล่ลงเรือ + นาฬิกาทราย | ใหม่ |
| cordon | เชือกกั้นท่าเรือ (ห้ามขึ้นเพิ่ม คนเดิมอยู่ต่อ) | ใหม่ |
| drain | ย้ายของลงจากเรือ (ห้ามวาดเป็นท่อระบายน้ำ) | ใหม่ |
| NotReady / unreachable | เรือขาดการติดต่อในหมอก วิทยุเงียบ | ใหม่ |
| Lease heartbeat | สัญญาณวิทยุ "ยังอยู่" ทุก 10 วินาที | ใหม่ |
| static Pod | ตู้ที่ต้นเรือดูแลเองจากแฟ้มบนเรือ ไม่ผ่านหอ (หอเห็นแค่ "เงา" = mirror pod) | ใหม่ |
| Downward API | ป้ายชื่อเรือที่ต้นเรือติดให้ตู้ตอนขึ้นเรือ | ใหม่ |
| PriorityClass / preemption | ป้ายสินค้าด่วน VIP แซงคิว | ใหม่ |

### เรื่องเล่า

ร้านอาหารแมวน้องส้ม (บท 002) เปิดสำเร็จแล้วบน Pod เดียว ลูกค้าเยอะขึ้น น้องส้มอยากเปิด **หลายสาขาบนกองเรือ** แต่พบคำถาม "กล่องของฉันไปอยู่เรือลำไหน ใครเลือก เลือกยังไง และถ้าเรือต้องเข้าอู่หรือหายในหมอกจะเป็นอย่างไร" → เรียนรู้เจ้าหน้าที่จัดตู้ (scheduler), ธงเรือ, แม่เหล็ก, ป้ายห้ามขึ้น, บัตรผ่าน, การซ่อมเรือ และเรือล่ม → LAB สุดท้ายเปิด 2 สาขาคนละเรือ เรือลำหนึ่งล่ม สาขาที่เหลือยังขายได้ แต่ "ไม่มีใครเปิดสาขาใหม่ให้" → ปูทาง Deployment/Service

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001/002: รายวิชา/หัวข้อ/CLO-5, CLO-6, บทก่อนหน้า (ลิงก์บท 002), บทคัดย่อ, วัตถุประสงค์การเรียนรู้ (~9 ข้อ), สารบัญ, สารบัญรูปภาพ (ตาราง 2 คอลัมน์), ภาพแบบ `<p align="center" id="fig-N">`

1. **บทนำ: ร้านน้องส้มอยากมีหลายสาขา** (T01–T02)
   - ทบทวนบท 002: Pod อยู่บน Node เดียวเสมอ, scheduler เลือกครั้งเดียว Pod ไม่ย้ายเรือ
   - คำถามนำบท: ใครเลือกเรือ, เลือกจากอะไร, เราสั่งได้แค่ไหน, เรือซ่อม/ล่มแล้ว Pod เป็นอย่างไร
   - ตารางอุปมาใหม่ (หัวข้อ 0)
2. **ทบทวน Node: เรือหนึ่งลำมีอะไรบ้าง** (T03–T04)
   - 2.1 องค์ประกอบบน worker: kubelet (ต้นเรือ ลงทะเบียน node, รายงานสถานะ, สั่ง runtime, รัน probe), container runtime (containerd ผ่าน CRI), kube-proxy (กฎเครือข่ายสำหรับ Service — บทหน้า), CNI (kindnet ให้ IP 10.244.x.x)
   - 2.2 Node ใน kind คือ Docker container ใน k8s-lab: `docker ps` เห็น `lab-control-plane`, `lab-worker`, `lab-worker2`; `docker exec lab-worker crictl ps` เห็น container ใน node; node "ล่ม" จำลองได้ด้วย `docker stop`
   - 2.3 control-plane ของ kind ก็เป็น node (มี kubelet) แต่มี taint ไม่รับ Pod ทั่วไป
3. **Node object: สมุดประจำเรือ** (T05–T08)
   - 3.1 `kubectl get nodes [-o wide] [--show-labels]` (STATUS, ROLES, VERSION, INTERNAL-IP, OS-IMAGE, CONTAINER-RUNTIME)
   - 3.2 Labels มาตรฐาน: `kubernetes.io/hostname`, `kubernetes.io/os`, `kubernetes.io/arch`, `node-role.kubernetes.io/control-plane` (ROLES มาจาก label นี้; worker ใน kind แสดง `<none>`), `topology.kubernetes.io/zone|region` (คลาวด์ — kind ไม่มี) + label ที่เราติดเอง; prefix `kubernetes.io/` สงวนไว้
   - 3.3 capacity vs allocatable: allocatable = capacity − kube-reserved − system-reserved − eviction-threshold; kind เห็น CPU/RAM เท่าเครื่องจริงและแต่ละ node "เห็นเครื่องเดียวกัน" (ข้อควรระวัง: 3 node ไม่ได้มีทรัพยากรจริง 3 เท่า); `pods: 110`
   - 3.4 conditions: Ready (True/False/Unknown), MemoryPressure, DiskPressure, PIDPressure, (NetworkUnavailable) — ความหมายของ Unknown = หอไม่ได้ยินข่าวจากต้นเรือ
   - 3.5 addresses (InternalIP, Hostname), nodeInfo (kubeletVersion, containerRuntimeVersion, osImage), `spec.podCIDR`, `spec.taints`, `spec.unschedulable`
   - 3.6 `kubectl describe node`: Labels, Taints, Unschedulable, Conditions, Addresses, Capacity/Allocatable, System Info, Non-terminated Pods, **Allocated resources** (ผลรวม requests/limits เทียบ allocatable), Events
   - 3.7 Heartbeat: Lease ใน namespace `kube-node-lease` ต่ออายุทุก ~10 วินาที + NodeStatus update
4. **kube-scheduler: เจ้าหน้าที่จัดตู้ขึ้นเรือ** (T09–T11)
   - 4.1 scheduler เฝ้าดู Pod ที่ `spec.nodeName` ว่าง → เลือก node → เขียน binding (`spec.nodeName`) → kubelet ของ node นั้นเห็นแล้วสร้าง container (ทบทวนเส้นทางบท 002)
   - 4.2 รอบการตัดสินใจ: **Filtering** (NodeResourcesFit, NodeName, NodeAffinity/nodeSelector, TaintToleration, InterPodAffinity, PodTopologySpread, NodeUnschedulable, NodePorts, ...) → **Scoring** (LeastAllocated/BalancedAllocation, ImageLocality, preferred affinity, PreferNoSchedule, ScheduleAnyway spread) → เลือกคะแนนสูงสุด (เสมอ = สุ่ม) → **Binding**
   - 4.3 ไม่มี node ผ่าน filter → `Pending` + Event `FailedScheduling` อ่านข้อความ `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. preemption: ...` (ข้อความจริงจากบท 002) — นับครบทุก node; scheduler ลองใหม่เองเมื่อคลัสเตอร์เปลี่ยน (เช่น เพิ่ม label/ลบ taint) ไม่ต้องลบ Pod
   - 4.4 ตัดสินใจครั้งเดียว: Pod ที่ bind แล้วไม่ถูกย้ายแม้ภายหลังกฎ "preferred" จะไม่ตรง (scheduler ไม่ rebalance; descheduler เป็นโปรเจกต์เสริม)
5. **requests เทียบ allocatable** (T12)
   - ใช้ **ผลรวม requests** ของ Pod บน node ไม่ใช่การใช้งานจริง; Pod ไม่ระบุ requests = นับเป็น 0 (วางได้เสมอ แต่เสี่ยงถูก evict); init container นับค่าสูงสุด; limits ไม่ใช้ตัดสิน scheduling
   - ตัวอย่างคำนวณ: allocatable cpu 4 → Pod ขอ 1500m วางได้ 2 ตัว ตัวที่ 3 Pending
6. **nodeName: ข้ามเจ้าหน้าที่จัดตู้** (T13)
   - kubelet ของ node นั้นรับไปเลย ไม่ผ่าน filter (taint NoSchedule/resources ไม่ถูกตรวจโดย scheduler — kubelet ยังตรวจ resources/admission เองและอาจ reject เป็น `OutOfcpu`/`OutOfmemory`); ชื่อ node ผิด → ค้าง Pending ไม่มีใครรับ (และ PodGC อาจลบทิ้ง)
   - ใช้เมื่อ: ดีบัก/ทดลองเท่านั้น งานจริงใช้ nodeSelector/affinity
7. **nodeSelector: ใบสั่ง "ต้องขึ้นเรือที่มีธงนี้"** (T14)
   - `kubectl label node lab-worker disk=ssd`, `--overwrite`, `disk-`; nodeSelector เป็น AND ทุก key; ไม่มี node ตรง → Pending `didn't match Pod's node affinity/selector`
   - ติด label ภายหลัง → Pod ที่ Pending ถูกวางทันที; ลบ label ภายหลัง → Pod ที่รันอยู่ไม่ถูกไล่ (IgnoredDuringExecution)
8. **Node affinity: แม่เหล็กดึงไปหาธงเรือ** (T15–T16)
   - 8.1 `requiredDuringSchedulingIgnoredDuringExecution` (ต้อง) vs `preferredDuringSchedulingIgnoredDuringExecution` (weight 1–100, อยากได้ — ไม่มีก็วางที่อื่น); ความหมายของ "IgnoredDuringExecution"
   - 8.2 operators: `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt` (ค่าเป็นจำนวนเต็มในรูป string); `nodeSelectorTerms` หลายอัน = OR, `matchExpressions` หลายอันในเทอมเดียว = AND; ใช้ร่วมกับ nodeSelector = ต้องผ่านทั้งคู่; `NotIn`/`DoesNotExist` ใช้ทำ "ห้ามไปเรือนี้" แบบ soft-anti
9. **Inter-pod affinity / anti-affinity: แม่เหล็กระหว่างกล่อง** (T17–T18)
   - 9.1 podAffinity (อยากอยู่ใกล้ Pod ที่มี label X เช่น web ใกล้ cache) / podAntiAffinity (ไม่อยากอยู่ใกล้ เช่น สาขาเดียวกันห้ามอยู่เรือเดียวกัน) แบบ required/preferred; `labelSelector`, `namespaces`
   - 9.2 `topologyKey` นิยามคำว่า "ใกล้": `kubernetes.io/hostname` = node เดียวกัน, `topology.kubernetes.io/zone` = zone เดียวกัน; ต้องมี label นั้นบน node
   - ข้อควรระวัง: required anti-affinity + Pod มากกว่าจำนวน node → ตัวเกิน Pending; คำนวณหนักในคลัสเตอร์ใหญ่
10. **topologySpreadConstraints: ตาชั่งกองเรือ** (T19–T20)
    - `maxSkew`, `topologyKey`, `whenUnsatisfiable` (DoNotSchedule/ScheduleAnyway), `labelSelector`, `minDomains`, `nodeAffinityPolicy` (default Honor), `nodeTaintsPolicy` (default **Ignore**)
    - **กับดักใน kind**: node control-plane ที่มี taint ยังถูกนับเป็น domain (0 Pod) เมื่อ `nodeTaintsPolicy: Ignore` → Pod ตัวที่ 3 Pending ทั้งที่ worker ว่าง → แก้ด้วย `nodeTaintsPolicy: Honor` (ต้องยืนยันใน LAB5)
    - เทียบ anti-affinity: anti = "ห้ามเกิน 1 ต่อ node", spread = "กระจายให้ต่างกันไม่เกิน maxSkew" (Pod มากกว่า node ได้)
11. **Taints & Tolerations: ป้ายห้ามขึ้นและบัตรผ่าน** (T21–T25)
    - 11.1 taint อยู่บน node (`key=value:effect`), toleration อยู่บน Pod (`key`, `operator` Equal/Exists, `value`, `effect`, `tolerationSeconds`); `kubectl taint node lab-worker2 dedicated=vip:NoSchedule`, ลบด้วย `...NoSchedule-`
    - 11.2 effect: `NoSchedule` (ไม่รับใหม่ ของเดิมอยู่ต่อ), `PreferNoSchedule` (เลี่ยงถ้าทำได้), `NoExecute` (ไม่รับใหม่ + ไล่ Pod เดิมที่ไม่มีบัตร)
    - 11.3 control-plane ของ kind: `node-role.kubernetes.io/control-plane:NoSchedule` (ยืนยันแล้วในบท 002) → Pod ทั่วไปไม่ลง; Pod ระบบ/ที่มี toleration + nodeSelector จึงลงได้; ไม่ควรวางงานจริงบน control-plane
    - 11.4 NoExecute + `tolerationSeconds`: ไม่มีบัตร → ถูกไล่ทันที; มีบัตรแบบมีเวลา → อยู่ได้ N วินาทีแล้วถูกไล่; มีบัตรไม่ระบุเวลา → อยู่ตลอด
    - 11.5 **toleration ≠ ดึงดูด**: มีบัตรผ่านไม่ได้แปลว่าต้องไปเรือนั้น → node เฉพาะกิจ (dedicated) ใช้ taint + toleration + node affinity คู่กัน
12. **บำรุงรักษา node: cordon / drain / uncordon** (T26–T28)
    - 12.1 `kubectl cordon` → `SchedulingDisabled` (`spec.unschedulable: true` + taint `node.kubernetes.io/unschedulable:NoSchedule`) Pod เดิมอยู่ต่อ
    - 12.2 `kubectl drain lab-worker --ignore-daemonsets --delete-emptydir-data --force`: cordon + evict ทีละ Pod (เคารพ PodDisruptionBudget — บทหน้า); Pod ที่ไม่มี controller ดูแล drain จะไม่ยอมจนกว่าจะใส่ `--force` (ข้อความ `cannot delete Pods that declare no controller`); **Pod เดี่ยวถูกลบแล้วหายไปเลย ไม่ถูกสร้างใหม่บนเรือลำอื่น**; Pod ที่ใช้ emptyDir ต้อง `--delete-emptydir-data` (ข้อมูลหาย); Pod ระบบ (kube-proxy, kindnet) ถูกข้ามด้วย `--ignore-daemonsets`; static/mirror pod ไม่ถูกลบ
    - 12.3 `kubectl uncordon` → รับ Pod ใหม่ได้ แต่ **Pod ที่หายไปไม่กลับมาเอง**
13. **เมื่อเรือล่ม: Node NotReady และ taint อัตโนมัติ** (T29–T31)
    - 13.1 kubelet หยุดส่ง heartbeat (Lease/NodeStatus) → node lifecycle controller รอ `node-monitor-grace-period` (ค่า default ~40–50 วินาที แล้วแต่เวอร์ชัน — ยืนยันใน LAB8) → Ready=`Unknown` → STATUS `NotReady`
    - 13.2 taint อัตโนมัติ: `node.kubernetes.io/unreachable` (Ready=Unknown) / `node.kubernetes.io/not-ready` (Ready=False) ทั้งแบบ `NoSchedule` และ `NoExecute`; อื่น ๆ: `memory-pressure`, `disk-pressure`, `pid-pressure`, `unschedulable`, `network-unavailable`
    - 13.3 admission `DefaultTolerationSeconds` ใส่ toleration ให้ทุก Pod: not-ready/unreachable `NoExecute` `tolerationSeconds: 300` → Pod รอ 5 นาทีก่อนถูก evict (ปรับให้สั้นลงได้ใน Pod)
    - 13.4 ระหว่างรอ: Pod condition Ready=False, STATUS อาจยังโชว์ `Running` (ไม่มีใครอัปเดตจากเรือ); หลัง evict: Pod ถูกสั่งลบ → `Terminating` ค้างจนกว่า kubelet กลับมา (ไม่มีใครยืนยันว่า container ตายแล้ว) — `--force --grace-period=0` และ taint `node.kubernetes.io/out-of-service` เป็นทางลัดที่ต้องระวัง; **Pod เดี่ยวไม่ถูกสร้างใหม่ที่ไหนเลย**
14. **Static Pod: ตู้ที่ต้นเรือดูแลเอง** (T32–T33)
    - kubelet อ่านไฟล์ใน `staticPodPath` (kind/kubeadm: `/etc/kubernetes/manifests`) สร้าง Pod เอง ไม่ผ่าน scheduler/API; สร้าง **mirror pod** ชื่อ `<name>-<nodeName>` ให้ API เห็น (อ่านอย่างเดียว ลบผ่าน kubectl แล้วกลับมาใหม่); ลบไฟล์ = ลบ Pod
    - control-plane components (`etcd`, `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`) ของ kind เป็น static pod บน `lab-control-plane` → ตอบคำถาม "ใครวาง scheduler ถ้า scheduler ยังไม่มี"
    - ข้อจำกัด: อ้าง ConfigMap/Secret/ServiceAccount ไม่ได้, ไม่ถูก drain
15. **Downward API: ป้ายชื่อเรือที่ติดให้ตู้** (T34)
    - `env.valueFrom.fieldRef.fieldPath`: `spec.nodeName`, `metadata.name`, `metadata.namespace`, `status.podIP`, `status.hostIP`, `metadata.labels['app']`; `resourceFieldRef` (requests/limits); แบบ volume (`downwardAPI`) กล่าวถึง
    - การอ้าง env ด้วย `$(VAR)` ใน `value`/`command`/`args` (ต้องประกาศตัวแปรก่อนหน้าในลิสต์; `$$(VAR)` = escape) → `SHOP_NAME="ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"`
16. **QoS กับ node-pressure eviction** (T35)
    - ทบทวน QoS (Guaranteed/Burstable/BestEffort จากบท 002); kubelet ไล่ Pod เมื่อทรัพยากรบนเรือใกล้หมด (eviction thresholds เช่น `memory.available<100Mi`) → condition MemoryPressure + taint → Pod `Failed` reason `Evicted`
    - ลำดับ: Pod ที่ใช้เกิน requests ก่อน (BestEffort/Burstable) → priority → ใช้เกินมากแค่ไหน; Guaranteed ไล่หลังสุด; ต่างจาก OOMKilled (kernel ฆ่า container เดียว) — ไม่ทำใน LAB (อาจทำให้ k8s-lab ทั้งเครื่องช้า)
17. **Priority และ Preemption (แนวคิดสั้น ๆ)** (T36)
    - PriorityClass (`value`, `globalDefault`, `preemptionPolicy`), `priorityClassName`, class ระบบ `system-cluster-critical`/`system-node-critical`; scheduler ไล่ Pod priority ต่ำกว่าเพื่อเปิดที่ให้ Pod สำคัญ (ข้อความ `preemption: ...` ใน FailedScheduling); ใช้อย่างระวัง — ไม่ทำใน LAB
18. **เลือกเครื่องมือจัดวางแบบไหนเมื่อไร** (T37) — ตารางสรุป: เป้าหมาย → เครื่องมือ → hard/soft → อยู่ที่ Pod หรือ Node → ตัวอย่าง
    - เจาะจง node เดียวเพื่อทดลอง → nodeName; ต้องอยู่ node ชนิดหนึ่ง → nodeSelector / required node affinity; อยากอยู่ → preferred; ห้ามคนทั่วไปเข้า node → taint (+toleration +affinity); อยู่ใกล้ Pod อื่น → podAffinity; แยกห่าง → podAntiAffinity; กระจายสมดุล → topologySpread; ซ่อม node → cordon/drain; Pod ประจำ node ที่ kubelet ดูแล → static pod
19. **ปูทางบทหน้า: Deployment และ Service** (T38) — Pod เดี่ยวหายเมื่อ drain/node ล่ม → ต้องมีผู้ดูแลจำนวน Pod (ReplicaSet/Deployment) และที่อยู่คงที่ (Service); affinity/spread ที่เรียนวันนี้จะใส่ใน Pod template ของ Deployment
20. **สรุปและคำถามทบทวน** (T39) + เอกสารอ้างอิง (kubernetes.io: Nodes, Node Status, Kubernetes Scheduler, Assigning Pods to Nodes, Pod Topology Spread Constraints, Taints and Tolerations, Safely Drain a Node, Node-pressure Eviction, Pod Priority and Preemption, Static Pods, Downward API, Well-Known Labels/Annotations/Taints)

## 2. รายการ LAB (`02_LAB/README.md`)

```text
02_LAB/
  README.md
  images/ (L01–L22 + imagegen-prompts.md)
  labs/
    lab01-scheduler/{fit-pod,huge-pod}.yaml
    lab02-nodename-downward/{pinned-pod,ghost-node-pod,whereami-pod}.yaml
    lab03-node-labels/{selector-pod,affinity-required-pod,affinity-preferred-pod,affinity-gt-pod}.yaml
    lab04-pod-affinity/{cache-pod,web-near-cache-pod,crew-anti-pods,crew-preferred-pods}.yaml
    lab05-topology-spread/{spread-ignore-pods,spread-honor-pods}.yaml
    lab06-taints/{plain-pod,vip-pod,control-plane-pod,noexecute-pods}.yaml
    lab07-drain/fleet-pods.yaml
    lab08-node-down/fog-pods.yaml
    lab09-static-pod/static-snack.yaml
  som-shop-branches/
    app/        (สำเนาจาก 002_kubernetes_pod/02_LAB/som-shop/app ไม่แก้โค้ด — ให้บทนี้ใช้เองได้)
    k8s/{som-shop-a,som-shop-b,som-shop-c}.yaml
```

image ที่ใช้ใน LAB0–9: `nginx:1.27-alpine`, `busybox:1.36` (ดึงแล้วในบท 002) — Pod busybox ใช้ `sleep` + `terminationGracePeriodSeconds: 1`/`--now` เพื่อลบเร็ว (บทเรียนบท 002: sh เป็น PID 1 ลบช้า 30 วิ); ทุก Pod ใส่ label `lab=03` → เก็บกวาดด้วย `kubectl delete pod -l lab=03 --now`

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ |
|---|---|---|---|---|---|---|
| 0 | สำรวจกองเรือ | เตรียมคลัสเตอร์/ไฟล์ และอ่าน Node object; เห็นว่า node คือ container | – | `k8s-up` (ถ้าจำเป็น), `kubectl get nodes -o wide`, `--show-labels`, `-L kubernetes.io/arch,kubernetes.io/os`, `describe node lab-worker`, `get node lab-worker -o jsonpath='{.status.capacity}{"\n"}{.status.allocatable}'`, `kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key`, `docker ps --format '{{.Names}}'`, `docker exec lab-worker crictl ps`, `docker exec lab-control-plane crictl ps`, `kubectl get lease -n kube-node-lease` | 3 node Ready v1.37.x, ROLES `control-plane` / `<none>`; label hostname/os=linux/arch=amd64; control-plane มี taint `node-role.kubernetes.io/control-plane:NoSchedule` worker ไม่มี; capacity vs allocatable (pods 110); `crictl ps` บน worker เห็น `kube-proxy`, `kindnet-cni`; บน control-plane เห็น etcd/apiserver/scheduler/controller-manager; lease 3 ตัว RENEW ล่าสุด | ค่า capacity/allocatable จริง (cpu/memory/ephemeral-storage) ว่าต่างกันหรือไม่ใน kind (คาดว่า allocatable ≈ capacity เพราะไม่ได้ตั้ง reserved); ชื่อ container ใน `crictl ps`; ROLES ของ worker; มี label `beta.kubernetes.io/*` หรือไม่ |
| 1 | เจ้าหน้าที่จัดตู้กับ Pending | เห็น filtering จาก requests, อ่าน FailedScheduling, scheduler ลองใหม่เอง | `lab01-scheduler/fit-pod.yaml` (nginx req 100m/64Mi), `huge-pod.yaml` (busybox req `memory: 4000Gi`) | `apply`, `get pod -o wide`, `describe pod huge-pod`, `get events --field-selector reason=FailedScheduling`, `describe node lab-worker` (Allocated resources) | fit-pod Running บน worker ตัวใดตัวหนึ่ง (ไม่ใช่ control-plane); huge-pod `Pending`, Events `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory. preemption: ...`; Allocated resources ของ node เพิ่ม 100m; แก้ไม่ได้ด้วย apply (requests immutable) → ลบแล้วลดเป็น `256Mi` → Running | ข้อความ FailedScheduling จริงของ memory; ใช้ 4000Gi ไม่เกินเครื่องทดสอบ (ถ้าเครื่องจริงมี RAM มาก ปรับ); scheduler รายงานเวลา/ข้อความซ้ำอย่างไร; การแก้ requests ใน Pod ที่ Pending ถูกปฏิเสธ (ข้อความ Forbidden) — K8s 1.37 มี in-place resize (`resize` subresource) แต่ไม่ใช้กับ Pod Pending เพื่อแก้ scheduling ให้ยืนยันพฤติกรรมจริง |
| 2 | nodeName และ Downward API | วาง Pod ตรงเรือโดยข้าม scheduler; ให้ Pod รู้ว่าอยู่เรือไหน | `lab02-nodename-downward/pinned-pod.yaml` (`nodeName: lab-control-plane`, ไม่มี toleration), `ghost-node-pod.yaml` (`nodeName: lab-worker9`), `whereami-pod.yaml` (busybox env NODE_NAME/POD_NAME/POD_IP/HOST_IP + `GREETING="สวัสดีจาก $(POD_NAME) บนเรือ $(NODE_NAME)"`) | `apply`, `get pod -o wide`, `describe pod` (ไม่มี Event Scheduled), `logs whereami`, `exec whereami -- env \| grep -E 'NODE\|POD'` | pinned-pod ไปอยู่ `lab-control-plane` ทั้งที่มี taint NoSchedule (เพราะไม่ผ่าน scheduler) และ Events ไม่มี `Scheduled`; ghost Pending ไม่มี Event FailedScheduling; whereami logs `สวัสดีจาก whereami บนเรือ lab-worker…` ค่า POD_IP ตรง `-o wide` | pinned-pod บน control-plane Running จริงหรือถูก kubelet reject; ghost-node-pod ถูก PodGC ลบอัตโนมัติหรือไม่และหลังกี่วินาที (orphan pod GC) — ถ้าหายเองให้ใช้เป็นจุดสอน; ค่า `$(VAR)` แทนค่าถูกต้องเมื่อ NODE_NAME มาก่อน |
| 3 | ธงเรือ: nodeSelector + node affinity | ติด label node, บังคับ/ขอ node ด้วย selector และ affinity ทุกแบบ | `lab03-node-labels/selector-pod.yaml` (`nodeSelector: {fleet: fast}`), `affinity-required-pod.yaml` (`fleet In [fast, eco]`), `affinity-preferred-pod.yaml` (preferred weight 80 `fleet=fast`, weight 20 `cabin Exists`), `affinity-gt-pod.yaml` (`deck Gt "3"`) | `kubectl label node lab-worker2 fleet=fast deck=5`, `kubectl label node lab-worker fleet=eco deck=2`, `get nodes -L fleet,deck`, `apply`, `get pod -o wide -w`, `label node ... fleet-`, `--overwrite` | selector-pod: ก่อนติด label → Pending `didn't match Pod's node affinity/selector` → ติด label แล้วถูกวางเองบน lab-worker2; ลบ label หลังรัน → Pod ยังอยู่ (IgnoredDuringExecution); required ได้ทั้ง 2 worker; preferred ส่วนใหญ่ไป lab-worker2 แต่ถ้า taint/เต็มก็ไปที่อื่นได้; Gt ไป lab-worker2 เท่านั้น | ข้อความ FailedScheduling ของ selector เวอร์ชัน 1.37 (`node(s) didn't match Pod's node affinity/selector`); เวลาที่ Pod Pending ถูกวางหลังติด label (ควร < 5 วิ); preferred ไม่รับประกัน — ทดสอบ 3–5 ตัวดูสัดส่วนจริง |
| 4 | แม่เหล็กระหว่างกล่อง: pod affinity / anti-affinity | วาง Pod ใกล้/ห่าง Pod อื่นด้วย topologyKey hostname | `lab04-pod-affinity/cache-pod.yaml` (app=cache, nodeName ไม่ใช้ — ใช้ nodeSelector hostname lab-worker), `web-near-cache-pod.yaml` (required podAffinity app=cache), `crew-anti-pods.yaml` (3 Pod `crew-1..3` required podAntiAffinity `team=crew` hostname), `crew-preferred-pods.yaml` (3 Pod preferred anti) | `apply`, `get pod -o wide -L app,team`, `describe pod crew-3` | web อยู่ node เดียวกับ cache; crew-1/2 อยู่คนละ worker, crew-3 `Pending` (`didn't match pod anti-affinity rules` + taint control-plane); แบบ preferred ทั้ง 3 Running (ตัวที่ 3 ซ้ำเรือ) | ข้อความ FailedScheduling จริงของ anti-affinity; ลำดับการ apply multi-doc ทำให้ crew ตัวไหน Pending; web-near-cache ถ้า apply ก่อน cache → Pending แล้ววางเองเมื่อ cache มา (ยืนยัน) |
| 5 | ตาชั่งกองเรือ: topologySpreadConstraints | กระจาย Pod สมดุลด้วย maxSkew และเห็นกับดัก control-plane | `lab05-topology-spread/spread-ignore-pods.yaml` (4 Pod `spread-1..4` maxSkew 1 hostname DoNotSchedule label `group=spread`), `spread-honor-pods.yaml` (เหมือนเดิม + `nodeTaintsPolicy: Honor`) | `apply`, `get pod -o wide`, `describe pod spread-3`, `kubectl get pod -l group=spread -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName` | แบบ Ignore: 2 ตัว Running (1+1), ตัวที่ 3–4 Pending เพราะ control-plane นับเป็น domain 0 Pod (`didn't match pod topology spread constraints`); แบบ Honor: 4 ตัว Running 2+2 | **สำคัญ**: ยืนยันว่า Ignore ทำให้ Pending จริงใน 1.37 (nodeTaintsPolicy default Ignore) — ถ้าไม่ Pending ให้ปรับเรื่องเล่าเป็น "เปรียบเทียบ maxSkew" ด้วย nodeAffinity เลือกเฉพาะ worker แทน; ข้อความ Event จริง |
| 6 | ป้ายห้ามขึ้นและบัตรผ่าน: taints & tolerations | NoSchedule, toleration, control-plane, NoExecute + tolerationSeconds | `lab06-taints/plain-pod.yaml`, `vip-pod.yaml` (toleration `dedicated=vip:NoSchedule` + nodeSelector hostname lab-worker2), `control-plane-pod.yaml` (toleration control-plane + nodeSelector `node-role.kubernetes.io/control-plane: ""`), `noexecute-pods.yaml` (3 Pod บน lab-worker2: `no-pass`, `pass-30s` tolerationSeconds 30, `pass-forever`) | `kubectl taint node lab-worker2 dedicated=vip:NoSchedule`, `describe node \| grep Taints`, `apply`, `kubectl taint node lab-worker2 maintenance=true:NoExecute`, `get pod -o wide -w`, ลบ taint `...-` | plain ลง lab-worker เท่านั้น; vip ลง lab-worker2 ได้; control-plane-pod Running บน lab-control-plane; หลังใส่ NoExecute: `no-pass` ถูกไล่ทันที, `pass-30s` ถูกไล่ ~30 วิ, `pass-forever` อยู่ต่อ; Pod ที่ถูกไล่หายไปไม่กลับมา | Events/สถานะตอนถูกไล่จริง (คาด `TaintManagerEviction` "Marking for deletion Pod ...") และ Pod หายจาก list หรือค้าง Terminating; ระยะเวลาจริงของ 30 วิ; ต้องใส่ toleration `dedicated=vip:NoSchedule` ใน noexecute-pods ด้วย (หรือลบ taint แรกก่อน) |
| 7 | ซ่อมเรือ: cordon / drain / uncordon | เห็นต่างของ cordon กับ drain และชะตากรรม Pod เดี่ยว | `lab07-drain/fleet-pods.yaml` (4 Pod nginx `cargo-1..4` + 1 Pod มี emptyDir, กระจายด้วย spread Honor) | `kubectl cordon lab-worker`, `get nodes`, `apply` Pod ใหม่ (ไปเรือ 2 ทั้งหมด), `kubectl drain lab-worker --ignore-daemonsets` (ไม่ใส่ --force ก่อน), แล้ว `--force --delete-emptydir-data`, `get pod -o wide`, `uncordon` | cordon → `Ready,SchedulingDisabled`, Pod เดิมอยู่ต่อ, Pod ใหม่ไป lab-worker2; drain ไม่มี --force → error `cannot delete Pods that declare no controller (use --force to override)` และ/หรือ `cannot delete Pods with local storage`; ใส่ครบ → `evicting pod ...` `pod/... evicted` `node/lab-worker drained`; Pod บน lab-worker หายถาวร ไม่ไปเกิดใหม่ที่ lab-worker2; uncordon แล้วก็ไม่กลับมา | ข้อความ drain จริงทั้งหมด (warning `ignoring DaemonSet-managed Pods: kube-system/kindnet-..., kube-system/kube-proxy-...`, `deleting Pods that declare no controller`); drain ใช้เวลาเท่าไร; ยืนยันว่าไม่มี Pod ไหนถูกสร้างใหม่ |
| 8 | เรือหายในหมอก: node NotReady | จำลอง node ล่ม ดู NotReady, taint อัตโนมัติ, default toleration 300 วิ, eviction และการกลับมา | `lab08-node-down/fog-pods.yaml` (บน lab-worker2 ผ่าน nodeSelector hostname: `fog-default` ไม่ตั้ง toleration, `fog-fast` tolerationSeconds 30 สำหรับ unreachable+not-ready NoExecute) | `apply`, `get pod fog-default -o yaml \| grep -A4 tolerations` (เห็น 300 ที่ระบบใส่), `docker stop lab-worker2`, `kubectl get nodes -w` (จับเวลา), `describe node lab-worker2` (Conditions Unknown `Kubelet stopped posting node status.`, Taints), `get pod -o wide -w`, `docker start lab-worker2`, `get nodes -w` | ~40–50 วิ node → `NotReady`; taint `node.kubernetes.io/unreachable:NoSchedule` + `:NoExecute`; ~30 วิหลังจากนั้น `fog-fast` → `Terminating` (ค้าง); `fog-default` ยังแสดงอยู่จน ~300 วิ; หลัง `docker start` node กลับ Ready, Pod ที่ถูก evict หายไป, ไม่มี Pod ใหม่ | **เวลาจริง** ตั้งแต่ docker stop ถึง NotReady และถึง evict; STATUS ของ Pod ระหว่าง NotReady (Running/Terminating/Unknown?); `docker start` แล้ว node กลับ Ready ได้ไหม (IP ของ node container เปลี่ยนหรือไม่ — kind multi-node อาจมีปัญหา) ใช้เวลาเท่าไร; Pod ใน lab-worker2 ที่ไม่ถูก evict (fog-default ถ้ากลับก่อน 300 วิ) restart หรือไม่; ข้อความ Events จริง (`NodeNotReady`, `TaintManagerEviction`); ถ้า docker start ไม่คืน ให้มีแผนสำรอง `k8s-down && k8s-up` |
| 9 | ตู้ของต้นเรือ: static Pod | เห็นว่า kubelet สร้าง Pod จากไฟล์เองไม่ผ่าน scheduler | `lab09-static-pod/static-snack.yaml` (nginx `static-snack`) | `docker exec lab-control-plane ls /etc/kubernetes/manifests`, `kubectl get pod -n kube-system -o wide \| grep lab-control-plane`, `docker exec lab-worker mkdir -p /etc/kubernetes/manifests`, `docker cp labs/lab09-static-pod/static-snack.yaml lab-worker:/etc/kubernetes/manifests/`, `kubectl get pod -o wide`, `kubectl delete pod static-snack-lab-worker`, `docker exec lab-worker rm /etc/kubernetes/manifests/static-snack.yaml` | control-plane มี 4 ไฟล์ (etcd, kube-apiserver, kube-controller-manager, kube-scheduler) และ Pod ชื่อลงท้าย `-lab-control-plane`; mirror pod `static-snack-lab-worker` Running ภายใน ~20 วิ, `-o yaml` มี annotation `kubernetes.io/config.mirror` และ ownerReferences เป็น Node; ลบด้วย kubectl → กลับมาเอง; ลบไฟล์ → หายจริง | staticPodPath ของ worker ใน kind (`docker exec lab-worker grep staticPodPath /var/lib/kubelet/config.yaml`), โฟลเดอร์มีอยู่แล้วหรือไม่; เวลาที่ kubelet เห็นไฟล์ (fileCheckFrequency 20 วิ); พฤติกรรมเมื่อ kubectl delete mirror pod ใน 1.37 |
| 10 | LAB สุดท้าย: ร้านน้องส้มหลายสาขาบนกองเรือ | รวม label, node affinity, pod anti-affinity, Downward API, port-forward, drain, node ล่ม | `som-shop-branches/` | ดูหัวข้อ 3 | ดูหัวข้อ 3 | ดูหัวข้อ 3.6 |

## 3. LAB สุดท้าย — "เปิดร้านน้องส้มหลายสาขาบนกองเรือ" (LAB10)

### 3.1 แนวคิดและเหตุผลการออกแบบ

- ใช้แอปเดิม `som-shop-web:1.0` + `postgres:17.11-alpine` จากบท 002 ไม่แก้โค้ด (หน้าเว็บอ่าน `SHOP_NAME` ตอน runtime เพราะ `page.tsx` เป็น `force-dynamic` และแสดง `os.hostname()` = ชื่อ Pod)
- Pod all-in-one 2 สาขา `som-shop-a`, `som-shop-b` (โครงเดียวกับ `som-shop` บท 002: db native sidecar → wait-for-db → db-seed → web, emptyDir) + ส่วนจัดวางใหม่
- ทุกสาขามีฐานข้อมูลของตัวเอง (emptyDir แยก) → ออเดอร์สาขา a ไม่เห็นที่สาขา b — บอกนักศึกษาตรง ๆ ว่าเป็นข้อจำกัดของการออกแบบเพื่อการเรียน (บทหน้า: web หลายตัวใช้ db กลางผ่าน Service)
- เลือกสร้าง 2 ไฟล์ Pod (ไม่ใช้ template) เพื่อให้เห็นว่า "ถ้าไม่มี Deployment เราต้องก๊อปปี้ YAML เอง" → แรงจูงใจบทหน้า

### 3.2 Manifest ที่ต้องมี

`som-shop-branches/k8s/som-shop-a.yaml` (b และ c ต่างกันเฉพาะชื่อและ label `branch`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: som-shop-a
  labels: { app: som-shop, part: branch, branch: a }
spec:
  affinity:
    nodeAffinity:                      # ต้องเปิดบนเรือที่ติดธง shop=open
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - { key: shop, operator: In, values: ["open"] }
    podAntiAffinity:                   # สาขาของ som-shop ห้ามอยู่เรือลำเดียวกัน
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels: { app: som-shop, part: branch }
          topologyKey: kubernetes.io/hostname
  tolerations:                         # เรือหายในหมอกเกิน 60 วิ → ยอมให้ถูกไล่ (ค่าเริ่มต้น 300 วิ ยาวไปสำหรับ LAB)
    - { key: node.kubernetes.io/unreachable, operator: Exists, effect: NoExecute, tolerationSeconds: 60 }
    - { key: node.kubernetes.io/not-ready,  operator: Exists, effect: NoExecute, tolerationSeconds: 60 }
  volumes: [ { name: db-data, emptyDir: {} } ]
  initContainers:  # db (native sidecar), wait-for-db, db-seed — เหมือนบท 002 ทุกบรรทัด
    ...
  containers:
    - name: web
      image: som-shop-web:1.0
      imagePullPolicy: IfNotPresent
      env:
        - name: NODE_NAME              # Downward API: ต้นเรือบอกชื่อเรือ (ต้องประกาศก่อน SHOP_NAME)
          valueFrom: { fieldRef: { fieldPath: spec.nodeName } }
        - name: POD_IP
          valueFrom: { fieldRef: { fieldPath: status.podIP } }
        - name: SHOP_NAME
          value: "ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"
        - { name: DATABASE_URL, value: postgres://som:meow1234@localhost:5432/catshop }
        - { name: PORT, value: "3000" }
        - { name: HOSTNAME, value: "0.0.0.0" }
      ports: [ { containerPort: 3000 } ]
      readinessProbe/livenessProbe/resources: เหมือนบท 002
```

`som-shop-c.yaml` = สาขาที่ 3 ไว้ทดลองว่า anti-affinity + เรือ shop=open มีแค่ 2 ลำ → Pending

### 3.3 สถาปัตยกรรมเป้าหมาย

```text
lab-control-plane  (taint control-plane:NoSchedule, ไม่มีธง shop)  ← ไม่มีสาขา
lab-worker   [shop=open]  └─ Pod som-shop-a  "ร้านอาหารแมวน้องส้ม สาขา lab-worker"    ← port-forward 3001
lab-worker2  [shop=open]  └─ Pod som-shop-b  "ร้านอาหารแมวน้องส้ม สาขา lab-worker2"   ← port-forward 3002
(สาขา a อาจได้ lab-worker2 และ b ได้ lab-worker — scheduler เป็นคนเลือก เรากำหนดแค่ "คนละลำ")
```

### 3.4 ขั้นตอน

1. **เตรียม image** (ข้ามได้ถ้ายังมีจากบท 002 — ตรวจ `docker image ls som-shop-web` และ `docker exec lab-worker crictl images | grep -E 'som-shop|postgres'` ทั้ง 2 worker)
   - `cd /workspace/003_kubernetes_node_pod/02_LAB/som-shop-branches/app && docker build -t som-shop-web:1.0 .`
   - `kind load docker-image som-shop-web:1.0 --name lab`
   - postgres (workaround จากบท 002): `docker pull postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab` (ARM: `linux/arm64`)
   - หมายเหตุ: ถ้าคลัสเตอร์ถูกสร้างใหม่ (`k8s-up` ใหม่) image บน node หายต้อง load ใหม่
2. **ติดธงเรือ**: `kubectl label node lab-worker lab-worker2 shop=open` → `kubectl get nodes -L shop`
3. **ทดลองก่อนติดธง (ทางเลือก)**: apply ก่อนข้อ 2 → ทั้งสองสาขา Pending `didn't match Pod's node affinity/selector` แล้วติดธง → วางเอง
4. **เปิดสาขา**: `kubectl apply -f k8s/som-shop-a.yaml -f k8s/som-shop-b.yaml` → `kubectl get pod -l app=som-shop -o wide -w` → ทั้งคู่ `2/2 Running` คนละ NODE
5. **ตรวจ Downward API**: `kubectl exec som-shop-a -c web -- printenv NODE_NAME SHOP_NAME POD_IP`
6. **ทดลองสาขาที่ 3**: `kubectl apply -f k8s/som-shop-c.yaml` → `Pending`; `describe` เห็น `0/3 nodes are available: 1 node(s) didn't match Pod's node affinity/selector, 2 node(s) didn't match pod anti-affinity rules ...` → `kubectl delete -f k8s/som-shop-c.yaml`
7. **เปิดหน้าร้าน 2 สาขา**: k8s-lab หน้าต่าง 1 `kubectl port-forward pod/som-shop-a 3001:3000`, หน้าต่าง 2 `kubectl port-forward pod/som-shop-b 3002:3000`; เครื่องนักศึกษา `ssh -p 2223 -L 3001:localhost:3001 -L 3002:localhost:3002 root@localhost` → browser `http://localhost:3001`, `http://localhost:3002` เห็นชื่อร้าน "สาขา lab-worker" / "สาขา lab-worker2" และ footer ชื่อ Pod ต่างกัน; กดสั่งซื้อที่สาขา a → stock สาขา b ไม่เปลี่ยน (db แยก)
8. **ซ่อมเรือ (drain)**: หา node ของสาขา a → `kubectl drain <node-a> --ignore-daemonsets --delete-emptydir-data --force` → som-shop-a ถูก evict หายไป, port-forward หน้าต่าง 1 `lost connection to pod`, สาขา b ยังขายได้; `kubectl get pod -l app=som-shop` เหลือ 1 ตัว ไม่มีใครสร้างคืน
9. **เปิดสาขา a ใหม่ระหว่างซ่อม**: `kubectl apply -f k8s/som-shop-a.yaml` → `Pending` (node-a ถูก cordon + อีกลำมีสาขา b → anti-affinity) → `kubectl uncordon <node-a>` → ถูกวางเองบน node-a, ออเดอร์เริ่มใหม่ (emptyDir ใหม่) → port-forward ใหม่
10. **เรือหายในหมอก**: `docker stop <node-b>` → `kubectl get nodes -w` NotReady (~40–50 วิ), สาขา a ยังขายได้, หน้า 3002 ใช้ไม่ได้; ~60 วิหลังจากนั้น som-shop-b ถูกไล่ → `Terminating` ค้าง; `kubectl apply -f k8s/som-shop-b.yaml` ไม่ได้ (ชื่อซ้ำ/ยัง Terminating) → ชวนคิด "ถ้ามีคนดูแลจำนวนสาขาให้ล่ะ"
11. **เรือกลับมา**: `docker start <node-b>` → Ready, som-shop-b หายจริง (ไม่ถูกสร้างใหม่) → apply ใหม่ได้ (ข้อมูลเริ่มใหม่)
12. **เก็บกวาด**: `kubectl delete pod -l app=som-shop`, `kubectl label node lab-worker lab-worker2 shop-`, ตรวจ `kubectl get nodes` ไม่มี SchedulingDisabled
13. **คำถามท้าย LAB + ปูทาง**: ทำไมสาขาที่หายไม่มีใครเปิดใหม่ (ไม่มี controller), ลูกค้าต้องจำ port ต่างกันของแต่ละสาขา (ไม่มีที่อยู่กลาง), ข้อมูลแต่ละสาขาแยกกัน → Deployment (replicas + Pod template ที่ใส่ affinity เดิมได้), Service (ที่อยู่เดียวกระจายไปทุกสาขา), StatefulSet/PVC

### 3.5 ผลที่ต้องเห็น (สรุป)

| ขั้น | ผล |
|---|---|
| 4 | `som-shop-a 2/2 Running` และ `som-shop-b 2/2 Running` บน `lab-worker` กับ `lab-worker2` คนละลำ ไม่มีบน control-plane |
| 5 | `NODE_NAME=lab-worker…`, `SHOP_NAME=ร้านอาหารแมวน้องส้ม สาขา lab-worker…`, `POD_IP` ตรง `-o wide` |
| 6 | `som-shop-c` Pending พร้อมเหตุผล anti-affinity/affinity/taint ครบ 3 node |
| 7 | browser 2 แท็บแสดงชื่อสาขาตามเรือ, ออเดอร์แยกกัน |
| 8 | drain แล้วเหลือ 1 สาขา, ไม่มี Pod ใหม่ |
| 9 | Pending ระหว่าง cordon → uncordon แล้ว Running |
| 10–11 | node NotReady → สาขาบนเรือนั้นถูก evict (Terminating) → เรือกลับ Pod หาย ไม่ถูกสร้างใหม่; อีกสาขาขายได้ตลอด |

### 3.6 จุดที่ต้องยืนยันตอนทดสอบจริง

1. `$(NODE_NAME)` ใน `SHOP_NAME` ถูกแทนค่าจริง และหน้าเว็บ (body) แสดงชื่อสาขาตาม node; `<title>` ใน `layout.tsx` เป็น metadata แบบ static อาจถูก bake ตอน build → แท็บ browser อาจยังเป็น "ร้านอาหารแมวน้องส้ม" (ยืนยันแล้วบันทึก; ไม่แก้โค้ดแอป)
2. image `som-shop-web:1.0`/postgres มีบน **ทั้ง 2 worker** (kind load ใส่ทุก node) และ READY `2/2` เหมือนบท 002
3. ข้อความ FailedScheduling จริงของ som-shop-c และของ som-shop-a ระหว่าง cordon (มี `node(s) were unschedulable` หรือไม่)
4. drain: ข้อความครบ (`--delete-emptydir-data` จำเป็นจริงเพราะ emptyDir), เวลา evict (Postgres + Next.js ปิดตัวภายใน grace 30 วิ)
5. **เวลา NotReady** หลัง `docker stop` และเวลา evict หลังตั้ง tolerationSeconds 60; สถานะ Pod ระหว่างนั้น (`Running` ค้าง/`Terminating`); `kubectl port-forward` ไป Pod บนเรือที่ล่ม error อะไร
6. `docker start` worker แล้วกลับ Ready ภายในกี่วินาที, IP node เปลี่ยนไหม, Pod ระบบบนเรือนั้นกลับมาปกติไหม; แผนสำรองถ้าไม่กลับ: `k8s-down && k8s-up` + load image ใหม่
7. ทรัพยากรรวม 2 สาขาพอบนเครื่องนักศึกษา (requests รวม ~520m CPU / ~1Gi RAM ต่อสาขาเมื่อรวม init สูงสุด) และ build image ซ้ำบนเครื่องช้า
8. ถ้า apply `som-shop-b` ระหว่างตัวเก่า Terminating → ข้อความจริง (`object is being deleted` / AlreadyExists)

## 4. Storyboard ภาพ (รายละเอียด prompt ใน images.json)

- Theory T01–T39 (39 ภาพ): เปิดเรื่อง → อุปมาใหม่ → กายวิภาคเรือ → node ใน kind → labels/allocatable/conditions/describe → scheduler path/filter-score-bind/Pending → requests → nodeName → nodeSelector → node affinity (2) → pod affinity/topologyKey → spread (2) → taints (5) → cordon/drain/uncordon → NotReady/taint อัตโนมัติ/evict → static pod (2) → Downward API → QoS eviction → priority → ตารางเลือกเครื่องมือ → preview → สรุป
- LAB L01–L22 (22 ภาพ): ภาพเปิด LAB0–LAB9 (LAB0 2 ภาพ, LAB6 2 ภาพ, LAB8 2 ภาพ) และ LAB สุดท้าย 9 ภาพ (L14–L22)
- ภาพที่อนุญาตให้มี Deployment/Service: T38 และ L22 เท่านั้น; DaemonSet ไม่ปรากฏเป็นคำในภาพใดเลย
- กฎ prompt ร่วม: ของในภาพเกี่ยวกับร้านอาหารแมวเท่านั้น; คำว่า drain/taint/cordon/eviction/static/spread/pressure ห้ามวาดตามตัวอักษร; ทุกแถว/ช่องในตาราง/แผงต้องมีป้าย; control-plane มีป้ายห้ามขึ้นเสมอเว้นภาพที่สอน toleration; Pod หนึ่งกล่องอยู่บนเรือลำเดียวเสมอ; Pod เดี่ยวที่หายไม่มีกล่องใหม่โผล่
