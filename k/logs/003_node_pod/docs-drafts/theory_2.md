
## 9. Inter-pod affinity และ anti-affinity: แม่เหล็กระหว่างกล่อง

node affinity เลือกเรือจาก **label ของเรือ** ส่วน inter-pod affinity เลือกเรือจาก **Pod ที่อยู่บนเรืออยู่แล้ว** เช่น "อยากอยู่ใกล้ cache" หรือ "สาขาเดียวกันห้ามอยู่เรือเดียวกัน"

### 9.1 podAffinity และ podAntiAffinity

<p align="center" id="fig-17">
  <img src="images/17-pod-affinity-anti.png" alt="รูปที่ 17 pod affinity และ anti-affinity" width="900"><br>
  <em><b>รูปที่ 17</b> pod affinity คือแม่เหล็กดึงกล่องให้อยู่ใกล้ Pod ที่มี label ตรง ส่วน pod anti-affinity คือแม่เหล็กผลักไม่ให้อยู่เรือลำเดียวกัน</em>
</p>

| ฟิลด์ | ความหมาย | ตัวอย่างการใช้ |
|---|---|---|
| `podAffinity` | ต้อง/อยากอยู่ "ที่เดียวกัน" กับ Pod ที่ตรง `labelSelector` | เว็บอยู่ใกล้ cache เพื่อลด latency |
| `podAntiAffinity` | ต้อง/อยาก **ไม่** อยู่ "ที่เดียวกัน" กับ Pod ที่ตรง `labelSelector` | สาขา/สำเนาของแอปเดียวกันแยกเรือ เพื่อไม่ให้ล่มพร้อมกัน |

ทั้งสองมีแบบ `requiredDuringSchedulingIgnoredDuringExecution` (รายการของ term) และ `preferredDuringSchedulingIgnoredDuringExecution` (มี `weight` และ `podAffinityTerm`) ฟิลด์ใน term ที่ต้องรู้

| ฟิลด์ | ความหมาย |
|---|---|
| `labelSelector` | เลือก Pod เป้าหมายด้วย label (`matchLabels` / `matchExpressions`) |
| `topologyKey` | label ของ **Node** ที่ใช้นิยามคำว่า "ที่เดียวกัน" (หัวข้อ 9.2) |
| `namespaces` / `namespaceSelector` | namespace ของ Pod เป้าหมาย (ไม่ระบุ = namespace เดียวกับ Pod นี้) |

ตัวอย่าง required podAffinity (ไฟล์จริงใน LAB 4)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-near-cache
  labels:
    lab: "03"
    app: web
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:            # หา Pod อื่นที่มีป้ายนี้ (ใน namespace เดียวกัน)
            matchLabels:
              app: cache
          topologyKey: kubernetes.io/hostname   # "ที่เดียวกัน" = node เดียวกัน
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ตัวอย่าง required podAntiAffinity (ไฟล์จริงมี `crew-1..3` หน้าตาเดียวกัน)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crew-1
  labels:
    lab: "03"
    team: crew
spec:
  affinity:
    podAntiAffinity:              # ผลักกัน: ห้ามอยู่เรือลำเดียวกับ Pod team=crew ตัวอื่น
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels:
              team: crew
          topologyKey: kubernetes.io/hostname
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ตัวอย่าง preferred podAntiAffinity (`deckhand-1..3`) สังเกตว่าแบบ preferred ต้องห่อ term ไว้ใน `podAffinityTerm`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: deckhand-1
  labels:
    lab: "03"
    team: deckhand
spec:
  affinity:
    podAntiAffinity:              # แบบ "อยากได้": พยายามแยกเรือ แต่ถ้าไม่มีเรือว่างก็ยอมอยู่ด้วยกัน
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                team: deckhand
            topologyKey: kubernetes.io/hostname
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลจริงจาก LAB 4

| การทดลอง | ผล |
|---|---|
| apply `web-near-cache` **ก่อน** `cache` | Pending: `... 2 node(s) didn't match pod affinity rules.` แล้วถูกวางเองทันทีเมื่อ `cache` เกิด (ทั้งคู่อยู่ `lab-worker`) |
| required anti-affinity 3 Pod บน worker 2 ลำ | `crew-1` อยู่ `lab-worker2`, `crew-2` อยู่ `lab-worker`, **`crew-3` Pending** |
| ลบ `crew-1` | `crew-3` ถูกวางเองภายใน ~3 วินาที |
| preferred anti-affinity 3 Pod | Running ครบ กระจาย 2 + 1 (ตัวที่ 3 ยอมอยู่เรือซ้ำ) |

ข้อความจริงของ `crew-3`

```text
Warning  FailedScheduling  6s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

### 9.2 topologyKey: นิยามคำว่า "ที่เดียวกัน"

<p align="center" id="fig-18">
  <img src="images/18-topologykey-meaning.png" alt="รูปที่ 18 ความหมายของ topologyKey" width="900"><br>
  <em><b>รูปที่ 18</b> topologyKey บอกว่า "ใกล้" หมายถึงอะไร kubernetes.io/hostname คือเรือลำเดียวกัน ส่วน zone คือท่าเรือเดียวกัน</em>
</p>

`topologyKey` คือชื่อ label บน Node Node ทุกตัวที่มี **ค่าของ label นี้เท่ากัน** ถือว่าอยู่ใน "โดเมน (domain) เดียวกัน"

| topologyKey | 1 โดเมน = | ความหมายของ anti-affinity |
|---|---|---|
| `kubernetes.io/hostname` | Node 1 เครื่อง | ห้ามอยู่ **เรือลำเดียวกัน** |
| `topology.kubernetes.io/zone` | ทุก Node ใน zone เดียวกัน | ห้ามอยู่ **ท่าเรือ (zone) เดียวกัน** แม้คนละเรือ |
| `topology.kubernetes.io/region` | ทุก Node ใน region เดียวกัน | ห้ามอยู่ region เดียวกัน |

Node ต้องมี label ที่ใช้เป็น topologyKey จริง ใน kind ไม่มี label `zone` ถ้าใช้ `topology.kubernetes.io/zone` กับ required affinity Pod จะหาโดเมนที่ตรงไม่ได้

> **ข้อควรระวัง**
> - required anti-affinity กับ `kubernetes.io/hostname` ทำให้ **จำนวน Pod สูงสุด = จำนวน Node ที่ผ่านเงื่อนไขอื่น** ตัวที่เกินจะ Pending (เช่น `crew-3`) ถ้าต้องการกระจายแต่ยอมให้เกินได้ ใช้แบบ preferred หรือ topology spread (หัวข้อ 10)
> - กฎ anti-affinity มีผล **สองทาง** Pod ใหม่ที่ไม่มีกฎของตัวเองก็ถูกกันออกจาก Node ที่มี Pod ซึ่งประกาศ anti-affinity ต่อ label ของมัน
> - การคำนวณ inter-pod affinity หนักขึ้นตามจำนวน Pod ในคลัสเตอร์ใหญ่มาก ๆ (หลายพัน Node) จึงควรใช้เท่าที่จำเป็น

---

## 10. topologySpreadConstraints: ตาชั่งกองเรือ

### 10.1 แนวคิดและฟิลด์

<p align="center" id="fig-19">
  <img src="images/19-topology-spread-maxskew.png" alt="รูปที่ 19 topology spread และ maxSkew" width="900"><br>
  <em><b>รูปที่ 19</b> topologySpreadConstraints เหมือนตาชั่งกองเรือ จำนวน Pod ระหว่างเรือต่างกันได้ไม่เกิน maxSkew</em>
</p>

anti-affinity พูดได้แค่ "ห้ามอยู่ด้วยกัน" ส่วน **topology spread** พูดว่า "กระจายให้สมดุล" ซึ่งยืดหยุ่นกว่า (Pod มากกว่าจำนวน Node ได้)

```text
skew ของโดเมน = จำนวน Pod ที่ตรง labelSelector ในโดเมนนั้น − จำนวนต่ำสุดในบรรดาโดเมนที่เข้าเกณฑ์
เงื่อนไข: หลังวาง Pod ใหม่ skew ต้องไม่เกิน maxSkew
```

**ตารางที่ 6** ฟิลด์ของ `topologySpreadConstraints`

| ฟิลด์ | ค่า | ความหมาย |
|---|---|---|
| `maxSkew` | จำนวนเต็ม ≥ 1 | ความต่างสูงสุดที่ยอมรับได้ |
| `topologyKey` | label ของ Node | นิยามโดเมน (เหมือนหัวข้อ 9.2) |
| `whenUnsatisfiable` | `DoNotSchedule` (ค่าเริ่มต้น) / `ScheduleAnyway` | ทำตามไม่ได้แล้วจะ Pending (filter) หรือวางไปแต่ให้คะแนนตามความสมดุล (score) |
| `labelSelector` | selector | นับเฉพาะ Pod ที่ตรง (มักเป็น label ของกลุ่มตัวเอง) |
| `minDomains` | จำนวนเต็ม | จำนวนโดเมนขั้นต่ำที่ต้องมี (ใช้กับ `DoNotSchedule` เท่านั้น) |
| `nodeAffinityPolicy` | `Honor` (ค่าเริ่มต้น) / `Ignore` | นับเฉพาะ Node ที่ผ่าน nodeSelector/affinity ของ Pod หรือนับทุก Node |
| `nodeTaintsPolicy` | **`Ignore` (ค่าเริ่มต้น)** / `Honor` | นับ Node ที่ Pod **ทน taint ไม่ได้** เป็นโดเมนด้วยหรือไม่ |

ตัวอย่างการคิด (maxSkew 1, worker 2 ลำ, ไม่นับ control-plane): Pod ตัวที่ 1 → ลำ A (1:0), ตัวที่ 2 → ต้องไปลำ B (1:1), ตัวที่ 3 → ไปลำไหนก็ได้ (2:1 skew = 1), ตัวที่ 4 → ต้องไปลำที่น้อยกว่า (2:2)

### 10.2 กับดักใน kind: nodeTaintsPolicy

<p align="center" id="fig-20">
  <img src="images/20-spread-control-plane-trap.png" alt="รูปที่ 20 กับดัก nodeTaintsPolicy ใน kind" width="900"><br>
  <em><b>รูปที่ 20</b> กับดักใน kind: ค่าเริ่มต้น nodeTaintsPolicy: Ignore นับ control-plane ที่มี taint เป็นช่องที่มี 0 Pod ทำให้ Pod ตัวที่ 3 Pending ต้องตั้ง Honor</em>
</p>

ค่าเริ่มต้น `nodeTaintsPolicy: Ignore` แปลว่า "ไม่สนใจ taint เวลานับโดเมน" Node `lab-control-plane` (ซึ่งมี taint และ Pod ของเราลงไม่ได้) จึงถูกนับเป็นโดเมนที่มี **0 Pod ตลอดไป** ผลคือ

```text
โดเมน:        lab-control-plane   lab-worker   lab-worker2
Pod ตัวที่ 1:        0                0            1        (skew 1 ✓)
Pod ตัวที่ 2:        0                1            1        (skew 1 ✓)
Pod ตัวที่ 3:        0                2 หรือ        2        → skew = 2 − 0 = 2 > maxSkew 1  ✗  Pending
```

ผลจริงจาก LAB 5 ยืนยันว่าเกิด Pending จริงบน Kubernetes 1.37

```text
NAME       NODE          STATUS
spread-1   lab-worker2   Running
spread-2   lab-worker    Running
spread-3   <none>        Pending
spread-4   <none>        Pending
```

```text
Warning  FailedScheduling  8s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod topology spread constraints. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

แก้ด้วย `nodeTaintsPolicy: Honor` ให้นับเฉพาะ Node ที่ Pod ทน taint ได้ (ไฟล์จริง `honor-1..4`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: honor-1
  labels:
    lab: "03"
    group: honor
spec:
  topologySpreadConstraints:
    - maxSkew: 1                         # จำนวน Pod ระหว่าง "เรือที่มากสุด" กับ "เรือที่น้อยสุด" ต่างกันได้ไม่เกิน 1
      topologyKey: kubernetes.io/hostname   # 1 domain = 1 node
      whenUnsatisfiable: DoNotSchedule   # ถ้าทำให้เอียงเกิน → ไม่วาง (Pending)
      labelSelector:
        matchLabels:
          group: honor
      nodeTaintsPolicy: Honor        # ค่าเริ่มต้นคือ Ignore
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลจริง: `honor-1..4` Running ครบ 2 : 2 (`lab-worker2` 2 ตัว, `lab-worker` 2 ตัว) และเมื่อดู spec ที่ระบบเก็บไว้ จะเห็นว่าแบบที่ไม่ได้ตั้ง **ไม่มีฟิลด์ `nodeTaintsPolicy` เลย** (ใช้ค่าเริ่มต้น Ignore)

```text
[{"labelSelector":{"matchLabels":{"group":"spread"}},"maxSkew":1,"topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule"}]
[{"labelSelector":{"matchLabels":{"group":"honor"}},"maxSkew":1,"nodeTaintsPolicy":"Honor","topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule"}]
```

ทางแก้อื่นคือใช้ node affinity เลือกเฉพาะ worker ร่วมกับ `nodeAffinityPolicy: Honor` (ค่าเริ่มต้น) ซึ่งจะตัด control-plane ออกจากการนับเช่นกัน

**ตารางที่ 7** anti-affinity เทียบกับ topology spread

| ประเด็น | required podAntiAffinity | topologySpreadConstraints |
|---|---|---|
| คำพูด | "ห้ามอยู่โดเมนเดียวกันเกิน 1" | "แต่ละโดเมนต่างกันไม่เกิน maxSkew" |
| Pod มากกว่าจำนวนโดเมน | ตัวที่เกิน **Pending** | วางได้ (2:2, 3:3, ...) |
| แบบอ่อน | preferred + weight | `ScheduleAnyway` |
| กับดักใน kind | – | `nodeTaintsPolicy: Ignore` นับ control-plane |
| เหมาะกับ | 1 สำเนาต่อเครื่อง เช่น สาขาร้าน | กระจายจำนวนมากให้สมดุล |

---

## 11. Taints และ Tolerations: ป้ายห้ามขึ้นและบัตรผ่าน

กลไกในหัวข้อ 7–10 อยู่ที่ **Pod** (Pod เลือกเรือ) ส่วน taint อยู่ที่ **Node** (เรือปฏิเสธ Pod) ใช้เมื่ออยากกัน "ทุก Pod ยกเว้นคนที่มีบัตร" ออกจากเรือ

### 11.1 taint อยู่บน Node, toleration อยู่บน Pod

<p align="center" id="fig-21">
  <img src="images/21-taint-and-toleration.png" alt="รูปที่ 21 taint และ toleration" width="900"><br>
  <em><b>รูปที่ 21</b> taint คือป้ายห้ามขึ้นที่ติดบนเรือ toleration คือบัตรผ่านที่ติดกับ Pod มีบัตรตรงกันจึงขึ้นเรือได้</em>
</p>

taint มีรูปแบบ `key=value:effect` (value ไม่บังคับ)

```bash
kubectl taint node lab-worker2 dedicated=vip:NoSchedule      # ติดป้าย
kubectl describe node lab-worker2 | grep -A1 Taints          # ดูป้าย
kubectl taint node lab-worker2 dedicated=vip:NoSchedule-     # ลบป้าย (ใส่ - ต่อท้าย)
```

toleration อยู่ใน `spec.tolerations` ของ Pod

| ฟิลด์ | ความหมาย |
|---|---|
| `key` | key ของ taint ที่ทนได้ (ว่าง + `operator: Exists` = ทนทุก taint) |
| `operator` | `Equal` (ค่าเริ่มต้น ต้องตรงทั้ง key และ value) หรือ `Exists` (ตรงแค่ key ไม่สน value) |
| `value` | ค่าที่ต้องตรง (ใช้กับ `Equal`) |
| `effect` | effect ที่ทนได้ (ว่าง = ทุก effect ของ key นั้น) |
| `tolerationSeconds` | ใช้กับ `NoExecute` เท่านั้น อยู่ต่อได้กี่วินาทีหลังเจอ taint |

ตัวอย่าง (ไฟล์จริง `vip-pod.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vip-pod
  labels:
    lab: "03"
spec:
  tolerations:
    - key: dedicated
      operator: Equal          # key และ value ต้องตรงกับ taint
      value: vip
      effect: NoSchedule
  nodeSelector:
    kubernetes.io/hostname: lab-worker2
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลจริงจาก LAB 6 เมื่อ `lab-worker2` มี taint `dedicated=vip:NoSchedule`: `plain-pod` (ไม่มีบัตร) ถูกวางที่ `lab-worker` **ทั้ง 5 รอบ** ที่ลองสร้างใหม่ ส่วน `vip-pod` ลง `lab-worker2` ได้

### 11.2 effect ทั้ง 3 แบบ

<p align="center" id="fig-22">
  <img src="images/22-taint-effects.png" alt="รูปที่ 22 effect ทั้ง 3 ของ taint" width="900"><br>
  <em><b>รูปที่ 22</b> effect ของ taint: NoSchedule ไม่รับใหม่, PreferNoSchedule เลี่ยงถ้าได้, NoExecute ไม่รับใหม่และไล่ Pod ที่ไม่มีบัตรลงจากเรือ</em>
</p>

**ตารางที่ 8** effect ของ taint

| effect | Pod ใหม่ที่ไม่มีบัตร | Pod ที่รันอยู่แล้วและไม่มีบัตร | ทำงานที่ |
|---|---|---|---|
| `NoSchedule` | ไม่ถูกวาง | **อยู่ต่อ** | scheduler (Filtering) |
| `PreferNoSchedule` | เลี่ยงถ้ามีเรืออื่น (ถูกหักคะแนน) | อยู่ต่อ | scheduler (Scoring) |
| `NoExecute` | ไม่ถูกวาง | **ถูกไล่ออก** (evict) ทันที หรือหลัง `tolerationSeconds` | scheduler + taint eviction controller ใน kube-controller-manager |

### 11.3 control-plane ของ kind

<p align="center" id="fig-23">
  <img src="images/23-control-plane-taint-kind.png" alt="รูปที่ 23 taint ของ control-plane ใน kind" width="900"><br>
  <em><b>รูปที่ 23</b> ใน kind หอบังคับการ lab-control-plane มี taint node-role.kubernetes.io/control-plane:NoSchedule Pod ทั่วไปจึงไปลงเฉพาะเรือ worker</em>
</p>

```text
$ kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key,EFFECT:.spec.taints[*].effect
NAME                TAINTS                                  EFFECT
lab-control-plane   node-role.kubernetes.io/control-plane   NoSchedule
lab-worker          <none>                                  <none>
lab-worker2         <none>                                  <none>
```

นี่คือเหตุผลที่ข้อความ FailedScheduling ทุกครั้งมี `1 node(s) had untolerated taint(s)` ถ้าต้องการวาง Pod บน control-plane จริง ๆ (เพื่อการเรียนเท่านั้น) ต้องมี **ทั้งบัตรผ่านและใบสั่ง**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: control-plane-pod
  labels:
    lab: "03"
spec:
  tolerations:
    - key: node-role.kubernetes.io/control-plane
      operator: Exists         # Exists = ไม่สนค่า value (taint นี้ไม่มี value)
      effect: NoSchedule
  nodeSelector:
    node-role.kubernetes.io/control-plane: ""   # label นี้มีเฉพาะบน control-plane (ค่าว่าง)
  containers:
    - name: web
      image: nginx:1.27-alpine
```

ผลจริง: `control-plane-pod` Running บน `lab-control-plane` ส่วน Pod ระบบอย่าง CoreDNS ที่อยู่บน control-plane ก็ใช้หลักเดียวกัน (มี toleration) งานจริงไม่ควรวางแอปบน control-plane เพราะแย่งทรัพยากรกับหอบังคับการ

### 11.4 NoExecute และ tolerationSeconds

<p align="center" id="fig-24">
  <img src="images/24-noexecute-tolerationseconds.png" alt="รูปที่ 24 NoExecute กับ tolerationSeconds" width="900"><br>
  <em><b>รูปที่ 24</b> NoExecute กับ tolerationSeconds: Pod ไม่มีบัตรถูกไล่ทันที, บัตรแบบมีเวลาอยู่ได้ตามนาฬิกาทราย, บัตรไม่มีเวลาอยู่ต่อได้</em>
</p>

เมื่อ Node ถูกติด taint แบบ `NoExecute` Pod ที่อยู่บน Node นั้นแบ่งเป็น 3 กลุ่ม

| Pod | toleration ต่อ taint นี้ | ผล | ผลจริงใน LAB 6 |
|---|---|---|---|
| `no-pass` | ไม่มี | ถูกไล่ **ทันที** | Terminating ภายใน < 1 วินาที |
| `pass-30s` | มี `tolerationSeconds: 30` | อยู่ได้ 30 วินาทีแล้วถูกไล่ | ถูกไล่ที่ +30–31 วินาที |
| `pass-forever` | มี ไม่ระบุ `tolerationSeconds` | อยู่ต่อตลอด | Running ต่อ |

toleration ของ `pass-30s` (ไฟล์จริง)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pass-30s
  labels:
    lab: "03"
    group: noexecute
spec:
  nodeSelector:
    kubernetes.io/hostname: lab-worker2
  tolerations:
    - key: dedicated               # บัตรผ่านป้ายเดิม (NoSchedule) เพื่อให้ขึ้นเรือ lab-worker2 ได้ก่อน
      operator: Equal
      value: vip
      effect: NoSchedule
    - key: maintenance             # บัตรผ่านป้ายไล่ลงเรือ แต่ "มีเวลา" 30 วินาที
      operator: Equal
      value: "true"
      effect: NoExecute
      tolerationSeconds: 30
  containers:
    - name: web
      image: nginx:1.27-alpine
```

Event จริงเมื่อ Pod ถูกไล่

```text
61s         Normal    TaintManagerEviction      pod/no-pass                 Marking for deletion Pod default/no-pass
61s         Normal    Killing                   pod/no-pass                 Stopping container web
31s         Normal    Killing                   pod/pass-30s                Stopping container web
31s         Normal    TaintManagerEviction      pod/pass-30s                Marking for deletion Pod default/pass-30s
```

ข้อสังเกตจาก LAB 6

1. **`vip-pod` ที่อยู่บน `lab-worker2` ก่อนแล้วก็ถูกไล่ด้วย** เพราะมีบัตรแค่ `dedicated` ไม่มีบัตร `maintenance` แสดงว่า NoExecute ไล่ **ทุก Pod** ที่ไม่มีบัตรตรง ไม่ว่าจะมาก่อนหรือหลัง
2. การ "ไล่" ของ taint คือการ **ลบ Pod** (Terminating → หายไป) Pod เดี่ยวที่ถูกไล่ **ไม่ถูกสร้างใหม่ที่ไหน**
3. บน Node ปกติ Pod ที่ถูกไล่หายจากรายการภายในราว 1 วินาที (ต่างจาก Node ที่ล่ม ซึ่งจะค้าง Terminating ดูหัวข้อ 13)

### 11.5 toleration ไม่ใช่แรงดึงดูด

<p align="center" id="fig-25">
  <img src="images/25-toleration-not-attraction.png" alt="รูปที่ 25 toleration ไม่ใช่แรงดึงดูด" width="900"><br>
  <em><b>รูปที่ 25</b> มีบัตรผ่านไม่ได้แปลว่าต้องไปเรือลำนั้น ถ้าอยากได้เรือเฉพาะกิจต้องใช้ taint + toleration + node affinity คู่กัน</em>
</p>

ความเข้าใจผิดที่พบบ่อยที่สุด: "ใส่ toleration แล้ว Pod จะไปที่ Node ที่มี taint" **ไม่จริง** toleration แค่ทำให้ Node นั้น **ไม่ถูกตัดทิ้ง** Pod ยังอาจถูกวางบน Node ปกติลำอื่นได้ตามคะแนน

รูปแบบ **Node เฉพาะกิจ (dedicated nodes)** ที่ถูกต้องจึงใช้ 3 อย่างคู่กัน

| ชิ้นส่วน | อยู่ที่ | ทำหน้าที่ |
|---|---|---|
| taint `dedicated=vip:NoSchedule` | Node | กัน Pod ทั่วไปออก |
| toleration `dedicated=vip:NoSchedule` | Pod VIP | ให้ Pod VIP ผ่านป้ายได้ |
| label + nodeSelector/node affinity | Node + Pod VIP | ดึง Pod VIP ไปที่ Node นั้น (ไม่ไปที่อื่น) |

ใน `vip-pod.yaml` เราใช้ `nodeSelector: kubernetes.io/hostname: lab-worker2` ทำหน้าที่ชิ้นที่ 3 ในงานจริงควรติด label เฉพาะ เช่น `dedicated=vip` แล้วเลือกด้วย label นั้นแทนชื่อเครื่อง

---

## 12. บำรุงรักษา Node: cordon, drain และ uncordon

เรือต้องเข้าอู่เป็นระยะ (อัปเกรด kernel, เปลี่ยนฮาร์ดแวร์, อัปเกรด Kubernetes) Kubernetes มีคำสั่ง 3 ตัวสำหรับงานนี้

### 12.1 cordon: เชือกกั้นท่าเรือ

<p align="center" id="fig-26">
  <img src="images/26-cordon-rope.png" alt="รูปที่ 26 cordon เชือกกั้นท่าเรือ" width="900"><br>
  <em><b>รูปที่ 26</b> kubectl cordon คือเชือกกั้นท่าเรือ เรือขึ้นสถานะ SchedulingDisabled ไม่รับ Pod ใหม่ แต่ Pod เดิมยังอยู่บนเรือ</em>
</p>

`kubectl cordon lab-worker` ทำให้

- `spec.unschedulable: true` และระบบเติม taint `node.kubernetes.io/unschedulable:NoSchedule` ให้
- STATUS เป็น `Ready,SchedulingDisabled`
- **Pod เดิมอยู่ต่อ** แต่ Pod ใหม่จะไม่ถูกวางที่นี่ (plugin `NodeUnschedulable`)

ผลจริงจาก LAB 7

```text
$ kubectl get nodes
NAME                STATUS                     ROLES           AGE   VERSION
lab-control-plane   Ready                      control-plane   11m   v1.37.0
lab-worker          Ready,SchedulingDisabled   <none>          11m   v1.37.0
lab-worker2         Ready                      <none>          11m   v1.37.0

$ kubectl get node lab-worker -o jsonpath='{.spec.unschedulable} {.spec.taints}{"\n"}'
true [{"effect":"NoSchedule","key":"node.kubernetes.io/unschedulable","timeAdded":"2026-10-04T12:04:50Z"}]
```

### 12.2 drain: ย้ายของลงจากเรือ

<p align="center" id="fig-27">
  <img src="images/27-drain-standalone-pods-gone.png" alt="รูปที่ 27 drain Pod เดี่ยวหายไปเลย" width="900"><br>
  <em><b>รูปที่ 27</b> kubectl drain ย้ายของลงจากเรือ Pod เดี่ยวต้องใช้ --force และถูกลบหายไปเลย ไม่มีใครสร้างใหม่บนเรือลำอื่น</em>
</p>

`kubectl drain <node>` = **cordon + ไล่ (evict) Pod บน Node ทีละตัว** ผ่าน Eviction API ซึ่งเคารพ PodDisruptionBudget (เนื้อหาบทหลัง) drain มีด่านป้องกันหลายด่าน ต้องยืนยันด้วย flag

| flag | เกี่ยวกับ | ถ้าไม่ใส่ (ข้อความจริงจาก LAB 7) |
|---|---|---|
| `--ignore-daemonsets` | Pod ระบบที่ "ระบบดูแลให้ทุกเรือมีหนึ่งตัว" เช่น `kindnet`, `kube-proxy` (สร้างโดย DaemonSet ซึ่งจะเรียนภายหลัง) ลบไปก็ถูกสร้างคืนบนเรือเดิม จึงต้องข้าม | `cannot delete DaemonSet-managed Pods (use --ignore-daemonsets to ignore): kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl` |
| `--force` | **Pod เดี่ยว** (ไม่มี controller ดูแล) ถูกลบแล้วหายถาวร drain จึงขอให้ยืนยัน | `cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4` |
| `--delete-emptydir-data` | Pod ที่ใช้ emptyDir ข้อมูลจะหายเมื่อ Pod ถูกลบ | `cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry` |

ผลจริงเมื่อใส่ครบ (ใช้เวลา 2.06 วินาที)

```text
$ kubectl drain lab-worker --ignore-daemonsets --delete-emptydir-data --force
node/lab-worker already cordoned
Warning: deleting Pods that declare no controller: default/cargo-2, default/cargo-4, default/pantry; ignoring DaemonSet-managed Pods: kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl
evicting pod default/pantry
evicting pod default/cargo-2
evicting pod default/cargo-4
pod/pantry evicted
pod/cargo-4 evicted
pod/cargo-2 evicted
node/lab-worker drained
```

สิ่งที่ต้องจำ

1. **Pod เดี่ยวที่ถูก drain หายไปเลย ไม่ถูกสร้างใหม่บนเรือลำอื่น** ใน LAB 7 ก่อน drain มี Pod 6 ตัว หลัง drain เหลือ 3 ตัวบน `lab-worker2` (ตัวเดิม) ไม่มีตัวใหม่เกิดขึ้น
2. **drain ที่ error ก็ cordon Node ไปแล้ว** (ข้อความ `node/lab-worker cordoned` หรือ `already cordoned`) ต้อง `uncordon` เองเสมอ
3. Pod ระบบ (`kindnet`, `kube-proxy`) ยังอยู่บน Node และ static/mirror pod ไม่ถูกลบโดย drain
4. drain รอให้ Pod ปิดตัวตาม grace period (ค่าเริ่มต้น 30 วินาที) nginx และร้านน้องส้มปิดตัวเร็ว จึง drain เสร็จใน 1–2 วินาที

### 12.3 uncordon: เอาเชือกออก

<p align="center" id="fig-28">
  <img src="images/28-uncordon-but-not-back.png" alt="รูปที่ 28 uncordon แล้ว Pod ไม่กลับมา" width="900"><br>
  <em><b>รูปที่ 28</b> kubectl uncordon เอาเชือกออก เรือกลับมารับ Pod ใหม่ได้ แต่ Pod ที่ถูก drain ไปแล้วไม่กลับมาเอง</em>
</p>

`kubectl uncordon lab-worker` คืนสถานะ `Ready` (Event `NodeSchedulable`) Node รับ Pod **ใหม่** ได้อีกครั้ง แต่ **Pod ที่ถูก drain ไปแล้วไม่กลับมาเอง** และ Pod ที่ย้ายไปอยู่ลำอื่นก็ไม่ย้ายกลับ (scheduler ไม่ rebalance หัวข้อ 4.4)

**ตารางที่ 9** cordon / drain / uncordon

| คำสั่ง | Pod ใหม่ | Pod เดิม | STATUS |
|---|---|---|---|
| `cordon` | ไม่รับ | อยู่ต่อ | `Ready,SchedulingDisabled` |
| `drain` | ไม่รับ (cordon ให้ด้วย) | ถูกไล่ (Pod เดี่ยวหายถาวร) | `Ready,SchedulingDisabled` |
| `uncordon` | รับ | ไม่มีอะไรเปลี่ยน | `Ready` |

---

## 13. เมื่อเรือล่ม: Node NotReady และ taint อัตโนมัติ

drain คือการ "ซ่อมตามแผน" แต่บางครั้งเรือ **หายไปเฉย ๆ** (ไฟดับ, เครือข่ายขาด, เครื่องค้าง) เราจำลองได้ด้วย `docker stop lab-worker2` ใน k8s-lab

### 13.1 Heartbeat เงียบ → NotReady

<p align="center" id="fig-29">
  <img src="images/29-heartbeat-fog-notready.png" alt="รูปที่ 29 heartbeat และ NotReady" width="900"><br>
  <em><b>รูปที่ 29</b> kubelet ส่งสัญญาณ heartbeat ทุกประมาณ 10 วินาที เมื่อเงียบไปนานเกิน grace period หอบังคับการเปลี่ยนเรือเป็น NotReady</em>
</p>

1. kubelet บนเรือหยุดทำงาน → Lease ไม่ถูกต่ออายุ และ NodeStatus ไม่ถูกอัปเดต
2. **node lifecycle controller** ใน kube-controller-manager ตรวจทุกไม่กี่วินาที ถ้าไม่ได้ยินข่าวนานเกิน **`node-monitor-grace-period`** จะเปลี่ยน condition ทุกตัวเป็น `Unknown` (reason `NodeStatusUnknown`, message `Kubelet stopped posting node status.`) STATUS กลายเป็น `NotReady`
3. kind ไม่ได้ตั้งค่า `node-monitor-grace-period` เอง (ตรวจใน LAB 0) จึงใช้ค่าเริ่มต้นของเวอร์ชันนี้

ผลจริงที่วัดได้ (เวลานับจาก `docker stop`)

| รอบทดลอง | stop → NotReady |
|---|---|
| LAB 8 รอบหลัก | 44 วินาที (ตาม `LastTransitionTime`) |
| LAB 8 รอบเสริม | 50 วินาที |
| LAB 10 | 43 วินาที |
| รอบถ่ายภาพหน้าจอ LAB 10 | 51 วินาที |

นับจาก heartbeat ครั้งสุดท้าย (Lease `RenewTime` 19:06:10) ถึง NotReady (19:07:03) = 53 วินาที ซึ่งสอดคล้องกับ grace period ราว 50 วินาทีบวกรอบการตรวจ **สรุปง่าย ๆ ว่า Node จะเป็น NotReady ประมาณ 45–50 วินาทีหลังเรือล่ม** (ไม่ใช่ทันที)

ผลจริงของ `describe node` ระหว่างเรือล่ม

```text
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
  HolderIdentity:  lab-worker2
  AcquireTime:     <unset>
  RenewTime:       Sun, 04 Oct 2026 19:06:10 +0700
Conditions:
  Type             Status    LastHeartbeatTime                 LastTransitionTime                Reason              Message
  ----             ------    -----------------                 ------------------                ------              -------
  MemoryPressure   Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  DiskPressure     Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  PIDPressure      Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  Ready            Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
```

### 13.2 taint อัตโนมัติ

<p align="center" id="fig-30">
  <img src="images/30-auto-taints-unreachable.png" alt="รูปที่ 30 taint อัตโนมัติ unreachable" width="900"><br>
  <em><b>รูปที่ 30</b> ระบบใส่ taint อัตโนมัติ node.kubernetes.io/unreachable ให้เรือที่ขาดการติดต่อ และทุก Pod มีบัตรผ่านเริ่มต้น 300 วินาที</em>
</p>

พร้อมกับ NotReady ระบบติด taint ให้เรือเอง (เห็นพร้อมกันใน LAB 8)

**ตารางที่ 10** taint ที่ระบบติดให้อัตโนมัติ

| taint | เมื่อ | effect |
|---|---|---|
| `node.kubernetes.io/unreachable` | condition `Ready` เป็น `Unknown` (ติดต่อไม่ได้) | `NoSchedule` + `NoExecute` |
| `node.kubernetes.io/not-ready` | condition `Ready` เป็น `False` (ต้นเรือรายงานว่าไม่พร้อม) | `NoSchedule` + `NoExecute` |
| `node.kubernetes.io/memory-pressure` | `MemoryPressure=True` | `NoSchedule` |
| `node.kubernetes.io/disk-pressure` | `DiskPressure=True` | `NoSchedule` |
| `node.kubernetes.io/pid-pressure` | `PIDPressure=True` | `NoSchedule` |
| `node.kubernetes.io/network-unavailable` | เครือข่ายของ Node ยังไม่พร้อม | `NoSchedule` |
| `node.kubernetes.io/unschedulable` | Node ถูก cordon | `NoSchedule` |

`NoSchedule` กัน Pod ใหม่ ส่วน `NoExecute` เริ่ม "นาฬิกาทราย" ไล่ Pod เดิม

### 13.3 บัตรผ่านเริ่มต้น 300 วินาที

admission plugin **DefaultTolerationSeconds** เติม toleration ให้ **ทุก Pod** ที่ไม่ได้ระบุเอง ผลจริงจาก `kubectl get pod fog-default -o yaml` (Pod ที่เราไม่ได้เขียน tolerations เลย)

```yaml
tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
```

แปลว่า Pod จะ **รอเรือกลับมา 5 นาที (นับจากตอนที่ taint ถูกติด คือตอน NotReady)** ก่อนถูกไล่ เผื่อเป็นปัญหาเครือข่ายชั่วคราว ปรับให้สั้นลงได้ด้วยการเขียน toleration เองใน Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: fog-fast
  labels:
    lab: "03"
    group: fog
spec:
  nodeSelector:
    kubernetes.io/hostname: lab-worker2   # เรือที่เราจะทำให้ "หายในหมอก"
  tolerations:                     # เขียนทับค่าเริ่มต้น 300 วิ ที่ระบบใส่ให้ → ยอมรอแค่ 30 วิ
    - key: node.kubernetes.io/unreachable    # node ขาดการติดต่อ (Ready=Unknown)
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 30
    - key: node.kubernetes.io/not-ready      # node รายงานว่าไม่พร้อม (Ready=False)
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 30
  containers:
    - name: web
      image: nginx:1.27-alpine
```

### 13.4 ไทม์ไลน์จริงและชะตากรรมของ Pod

<p align="center" id="fig-31">
  <img src="images/31-evicted-terminating-no-replacement.png" alt="รูปที่ 31 Pod ถูกไล่ ค้าง Terminating" width="900"><br>
  <em><b>รูปที่ 31</b> เมื่อหมดเวลา Pod บนเรือที่ล่มถูกไล่ (evict) ค้างสถานะ Terminating จนเรือกลับมา และ Pod เดี่ยวจะไม่ถูกสร้างใหม่บนเรือลำอื่น</em>
</p>

**ตารางที่ 11** ไทม์ไลน์จริงจาก LAB 8 (T0 = `docker stop lab-worker2`)

| เวลา | เหตุการณ์ |
|---|---|
| +0 วินาที | `docker stop lab-worker2` (ใช้เวลา 0.8 วินาที) Node ยังแสดง `Ready` |
| ~+44 วินาที | Node `NotReady`, Ready=`Unknown`, taint `unreachable` ทั้ง `NoSchedule` และ `NoExecute` Pod ยังแสดง `1/1 Running` |
| +73 วินาที (NotReady + ~30) | `fog-fast` (tolerationSeconds 30) ถูกไล่ → `Terminating` |
| +345 วินาที (NotReady + ~300) | `fog-default` (ค่าเริ่มต้น 300) ถูกไล่ → `Terminating` |
| ต่อจากนั้น | ทั้งสองค้าง `Terminating` ไปเรื่อย ๆ ไม่มี Pod ใหม่เกิดที่ `lab-worker` |
| `docker start` +2 วินาที | Node กลับ `Ready` (IP เดิม `172.19.0.2`) |
| `docker start` +5 วินาที | Pod ที่ถูกไล่หายจากรายการจริง |
| `docker start` +~7 วินาที | taint `unreachable` หายหมด |

สิ่งที่ควรเข้าใจจากไทม์ไลน์

1. **ช่วงก่อนถูกไล่ STATUS ยังเป็น `Running`** เพราะไม่มีใครบนเรือรายงานสถานะ แต่ condition ของ Pod เปลี่ยนเป็น `Ready=False` (ผลจริง `PodReadyToStartContainers=True Initialized=True Ready=False ContainersReady=True PodScheduled=True`) และมี Event `NodeNotReady ... Node is not ready`
2. **ถูกไล่แล้วค้าง `Terminating`** เพราะการลบ Pod ต้องรอ kubelet ยืนยันว่า container หยุดแล้ว แต่ kubelet ติดต่อไม่ได้ ระบบจึงไม่กล้าลบ object ทิ้ง (อาจมี container ยังรันอยู่จริงบนเรือที่แค่ขาดการติดต่อ)
3. **คำสั่งที่ต้องคุยกับ kubelet ใช้ไม่ได้** ผลจริง `kubectl exec` → `error: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host` (port 10250 คือ port ของ kubelet) เช่นเดียวกับ `logs` และ `port-forward`
4. **Pod เดี่ยวไม่ถูกสร้างใหม่ที่ไหนเลย** การ apply ไฟล์เดิมซ้ำระหว่างค้าง Terminating ได้แค่ `Warning: Detected changes to resource fog-fast which is currently being deleted.` ไม่มี Pod ใหม่ (และไม่ใช่ error `AlreadyExists`)
5. **ถ้าเรือกลับมาก่อนครบเวลา** Pod ไม่ถูกไล่ แต่ container ถูกเริ่มใหม่ (ผลจริงรอบเสริม: `RESTARTS 1` และ **Pod IP เปลี่ยน** เพราะ sandbox ถูกสร้างใหม่หลัง Node รีสตาร์ต)

> **ทางลัดที่ต้องระวัง:** `kubectl delete pod <ชื่อ> --force --grace-period=0` ลบ object ทิ้งทันทีโดยไม่รอ kubelet และ taint `node.kubernetes.io/out-of-service` (ใช้กับกรณี Node ปิดตัวแบบไม่ปกติ) บอกระบบว่าเรือ "ดับจริง" ให้เก็บกวาด Pod ได้ ทั้งสองวิธีอาจทำให้มีโปรแกรมสองชุดทำงานซ้อนกันถ้าเรือแค่ขาดการติดต่อแต่ยังรันอยู่ ใช้เมื่อแน่ใจเท่านั้น

---
