
## 10. NetworkPolicy: รั้วและประตูระหว่างโซน

### 10.1 แนวคิด

{{FIG:T22|NetworkPolicy รั้วรอบโซน}}

**NetworkPolicy** เป็น object แบบ namespaced ที่กำหนดว่า Pod กลุ่มหนึ่ง **รับ** (ingress) หรือ **ส่ง** (egress) การเชื่อมต่อกับใครได้บ้าง หลักสำคัญมี 4 ข้อ

1. **ต้องมี network plugin ที่รองรับ** Kubernetes เก็บ NetworkPolicy ไว้เฉย ๆ คนที่บังคับใช้จริงคือ network plugin (CNI) ถ้า plugin ไม่รองรับ เราสร้าง object ได้แต่ **ไม่มีผลอะไร** kind v0.33 ใช้ **kindnet** ซึ่งรองรับและบังคับใช้จริง (ยืนยันใน LAB 4)
2. **Pod ที่ไม่ถูก policy ใดเลือก = เปิดหมด** (ค่าเริ่มต้นของคลัสเตอร์)
3. **Pod ที่ถูก policy เลือกด้วย `podSelector`** จะเปลี่ยนเป็น **"ปฏิเสธทุกอย่าง ยกเว้นที่ policy อนุญาต"** สำหรับทิศที่ระบุใน `policyTypes`
4. **policy รวมกันแบบ OR (additive)** ถ้ามีหลาย policy เลือก Pod เดียวกัน การเชื่อมต่อที่ policy ใดอนุญาตก็ผ่าน ไม่มี policy แบบ "deny" ให้หักล้าง

ตัวอย่างที่ 1 รั้วรอบโซน: ทุก Pod ใน `team-a` รับเฉพาะการเชื่อมต่อจาก Pod ใน `team-a` เอง (ไฟล์ `labs/lab04-network/np-same-ns.yaml`)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: team-a
spec:
  podSelector: {}                # {} = เลือกทุก Pod ในโซนนี้
  policyTypes: ["Ingress"]       # คุมเฉพาะขาเข้า
  ingress:
    - from:
        - podSelector: {}        # podSelector อย่างเดียว = Pod ใน namespace เดียวกับ policy เท่านั้น
```

`podSelector` ใน `from` ที่ไม่มี `namespaceSelector` คู่กัน หมายถึง Pod ใน **namespace เดียวกับ policy** เสมอ ผลจริงจาก LAB 4 หลัง apply (มีผลตั้งแต่คำสั่งแรกหลัง apply)

```text
$ time kubectl -n team-b exec client -- wget -qO- -T 3 http://10.244.2.6
wget: download timed out
command terminated with exit code 1

real	0m3.060s

$ kubectl -n team-a exec client -- wget -qO- -T 3 http://10.244.2.6 | grep -o '<title>.*</title>'
<title>Welcome to nginx!</title>
```

สังเกตว่า "ถูกปฏิเสธ" ในที่นี้คือ **packet ถูกทิ้งเงียบ ๆ** ฝั่งผู้เรียกจึงรอจนหมดเวลา (`-T 3` = 3 วินาที) ไม่ได้ข้อความ "ปฏิเสธ" กลับมา

### 10.2 เปิดประตูให้โซนที่มีป้ายตรง

{{FIG:T23|เปิดประตูด้วย namespaceSelector}}

ตัวอย่างที่ 2 เปิดให้ทุก Pod จาก namespace `team-b` เข้า Pod `app=web` ได้ (ไฟล์ `labs/lab04-network/np-allow-team-b.yaml`) ใช้ label อัตโนมัติ `kubernetes.io/metadata.name` จึงไม่ต้องติด label ให้ namespace เอง

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-team-b
  namespace: team-a
spec:
  podSelector:
    matchLabels:
      app: web                   # ใช้กับ Pod web เท่านั้น
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: team-b
```

ผลจริงจาก LAB 4 หลังมีทั้ง 2 policy: `team-b` เข้า `web` ได้อีกครั้ง (รอบแรกทันที) แต่ `blue/snack` ยังถูกกั้น และ `team-b` ยังเข้า `client` ของ `team-a` ไม่ได้ เพราะ policy ที่ 2 เลือกเฉพาะ `app=web`

```text
$ kubectl describe netpol -n team-a
Name:         allow-from-team-b
Namespace:    team-a
...
Spec:
  PodSelector:     app=web
  Allowing ingress traffic:
    To Port: <any> (traffic allowed to all ports)
    From:
      NamespaceSelector: kubernetes.io/metadata.name=team-b
  Not affecting egress traffic
  Policy Types: Ingress


Name:         allow-same-namespace
Namespace:    team-a
...
Spec:
  PodSelector:     <none> (Allowing the specific traffic to all pods in this namespace)
  Allowing ingress traffic:
    To Port: <any> (traffic allowed to all ports)
    From:
      PodSelector: <none>
  Not affecting egress traffic
  Policy Types: Ingress
```

### 10.3 AND กับ OR ใน from

จุดที่สับสนบ่อยคือการเขียน `namespaceSelector` กับ `podSelector` **ในรายการเดียวกัน** หรือ **คนละรายการ** (ตัวอย่างทฤษฎี ไม่ได้ใช้ใน LAB)

```yaml
# แบบ A: รายการเดียว (ขีด - ตัวเดียว) = AND
# อนุญาตเฉพาะ Pod ที่มี role=monitor และอยู่ใน namespace team-b
ingress:
  - from:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: team-b
        podSelector:
          matchLabels:
            role: monitor
---
# แบบ B: สองรายการ (ขีด - สองตัว) = OR
# อนุญาตทุก Pod ใน team-b หรือ Pod ที่มี role=monitor ใน namespace ของ policy เอง
ingress:
  - from:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: team-b
      - podSelector:
          matchLabels:
            role: monitor
```

### 10.4 default deny และ egress

ตัวอย่างที่ 3 **default-deny ingress** ของทั้ง namespace: เลือกทุก Pod แต่ไม่อนุญาตอะไรเลย (ตัวอย่างทฤษฎี)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: team-a
spec:
  podSelector: {}
  policyTypes: ["Ingress"]       # มี Ingress แต่ไม่มีรายการ ingress = ไม่รับจากใครเลย
```

ถ้าคุมขาออกด้วย (`policyTypes: ["Egress"]`) ต้องระวัง **DNS** เพราะ Pod ต้องส่งคำถามไปที่ CoreDNS ใน `kube-system` (UDP/TCP port 53) ถ้าลืมอนุญาต Pod จะเรียกชื่อใดไม่ได้เลยแม้ปลายทางจะอนุญาต วิธีมาตรฐานคือเพิ่ม egress ที่อนุญาต `namespaceSelector` ของ `kube-system` port 53 ไว้ทุกครั้ง

---

## 11. ResourceQuota: งบประมาณของโซน

### 11.1 แนวคิดและชนิดของเพดาน

{{FIG:T24|ResourceQuota ใบงบของโซน}}

**ResourceQuota** เป็น object แบบ namespaced ที่กำหนด **เพดานรวมของทั้ง namespace** แบ่งเป็น 2 กลุ่ม

| กลุ่ม | ตัวอย่างคีย์ใน `spec.hard` | ความหมาย |
|---|---|---|
| compute | `requests.cpu`, `requests.memory`, `limits.cpu`, `limits.memory` | ผลรวม requests/limits ของทุก Pod (ที่ยังไม่จบ) ในโซน |
| จำนวน object | `pods`, `configmaps`, `secrets`, `persistentvolumeclaims`, `count/<resource>.<group>` เช่น `count/jobs.batch` | จำนวน object แต่ละชนิดในโซน |

ไฟล์ `labs/lab05-quota/quota.yaml` ของ LAB 5

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: budget-quota
  namespace: budget
spec:
  hard:
    pods: "3"                    # Pod ได้ไม่เกิน 3 ตัว
    requests.cpu: 500m           # ผลรวม requests ของทุก Pod ในโซน
    requests.memory: 256Mi
    limits.cpu: "1"              # ผลรวม limits ของทุก Pod ในโซน
    limits.memory: 512Mi
```

ดูสถานะงบด้วย `kubectl describe quota` (คอลัมน์ Used/Hard) ผลจริงก่อนมี Pod

```text
$ kubectl describe quota -n budget
Name:            budget-quota
Namespace:       budget
Resource         Used  Hard
--------         ----  ----
limits.cpu       0     1
limits.memory    0     512Mi
pods             0     3
requests.cpu     0     500m
requests.memory  0     256Mi
```

### 11.2 ตรวจตอนสร้าง และข้อความเมื่อเกินงบ

{{FIG:T25|quota นับจำนวน Pod}}

ResourceQuota ทำงานเป็น **admission** คือด่านตรวจตอน API server รับคำขอ "สร้าง" (หรือแก้ไข) object ถ้าการสร้างทำให้ Used เกิน Hard คำขอจะถูกปฏิเสธทันที Pod จึงไม่เคยเกิดขึ้นเลย (ไม่ใช่ Pending) และ quota **ไม่ไล่ Pod เดิม** ที่มีอยู่ก่อน

ผลจริงจาก LAB 5: สร้าง Pod เล็ก 4 ตัว (ตัวละ requests 100m/64Mi, limits 200m/128Mi) ในงบ `pods: 3`

```text
$ kubectl apply -f labs/lab05-quota/small-pods.yaml
pod/small-1 created
pod/small-2 created
pod/small-3 created
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-4" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3

$ kubectl describe quota -n budget
...
Resource         Used   Hard
--------         ----   ----
limits.cpu       600m   1
limits.memory    384Mi  512Mi
pods             3      3
requests.cpu     300m   500m
requests.memory  192Mi  256Mi
```

อ่านข้อความ `exceeded quota`: `requested` = สิ่งที่ Pod ใหม่ขอ, `used` = ใช้ไปแล้ว, `limited` = เพดาน ข้อความจะแสดง **ทุกค่าที่เกิน** ในบรรทัดเดียว (LAB สุดท้ายเกินพร้อมกัน 4 ค่า หัวข้อ 11.4)

### 11.3 Pod ที่ไม่ระบุขนาดถูกปฏิเสธ

{{FIG:T26|Pod ไม่ระบุขนาดถูกปฏิเสธ}}

เมื่อ quota มีเพดานของ compute resource ใด Pod ใหม่ **ทุกตัว** ต้องระบุค่านั้นในทุก container เพราะถ้าไม่ระบุ ระบบคำนวณงบไม่ได้ ผลจริงจาก LAB 5 กับ Pod `no-request` ที่ไม่มี `resources` เลย

```text
$ kubectl apply -f labs/lab05-quota/no-request-pod.yaml
Error from server (Forbidden): error when creating "labs/lab05-quota/no-request-pod.yaml": pods "no-request" is forbidden: failed quota: budget-quota: must specify limits.cpu for: app; limits.memory for: app; requests.cpu for: app; requests.memory for: app
```

ข้อความบอกครบทั้ง 4 ค่าที่ขาด และชื่อ container (`app`) ทางแก้คือใส่ `resources` ให้ครบ หรือให้ **LimitRange** เติมค่าให้อัตโนมัติ (หัวข้อ 12)

### 11.4 Pod ที่มี init container และ sidecar นับงบอย่างไร

quota นับ **effective request/limit ของ Pod** ซึ่งคิดจากช่วงเวลาที่ Pod ใช้ทรัพยากรมากที่สุด

> effective = ค่ามากที่สุดระหว่าง (1) ผลรวมของ sidecar ทุกตัว + container หลักทุกตัว และ (2) init container แต่ละตัว + sidecar ที่เริ่มทำงานก่อนมัน

ร้าน `som-shop` ใน LAB สุดท้ายมี `db` (sidecar), `wait-for-db`, `db-seed` (init) และ `web`

| ช่วงเวลา | container ที่รันพร้อมกัน | requests (cpu/memory) | limits (cpu/memory) |
|---|---|---|---|
| ระหว่าง `wait-for-db` | `db` + `wait-for-db` | 110m / 272Mi | 600m / 576Mi |
| ระหว่าง `db-seed` | `db` + `db-seed` | 150m / 320Mi | 800m / 768Mi |
| ร้านเปิดแล้ว | `db` + `web` | **200m / 448Mi** | **1 / 1Gi** |

ค่ามากที่สุดคือแถวสุดท้าย ตรงกับผลจริงใน LAB สุดท้าย (1 Pod ใน `som-prod`)

```text
$ kubectl describe quota prod-budget -n som-prod
Name:            prod-budget
Namespace:       som-prod
Resource         Used   Hard
--------         ----   ----
limits.cpu       1      2
limits.memory    1Gi    2Gi
pods             1      2
requests.cpu     200m   1
requests.memory  448Mi  1Gi
```

เมื่อเปิดสาขาที่ 2 Used กลายเป็น pods 2/2, limits.cpu 2/2, limits.memory 2Gi/2Gi, requests.memory 896Mi/1Gi สาขาที่ 3 จึงถูกปฏิเสธพร้อมกัน 4 ค่า

```text
Error from server (Forbidden): error when creating "STDIN": pods "som-shop-3" is forbidden: exceeded quota: prod-budget, requested: limits.cpu=1,limits.memory=1Gi,pods=1,requests.memory=448Mi, used: limits.cpu=2,limits.memory=2Gi,pods=2,requests.memory=896Mi, limited: limits.cpu=2,limits.memory=2Gi,pods=2,requests.memory=1Gi
```

(`requests.memory` เกินด้วยเพราะ 896Mi + 448Mi = 1344Mi มากกว่า 1Gi = 1024Mi ส่วน `requests.cpu` 400m + 200m = 600m ยังไม่เกิน 1 จึงไม่อยู่ในรายการ)

> ResourceQuota ยังมี **scopes** ให้นับเฉพาะ Pod บางกลุ่มได้ เช่น `BestEffort`, `NotBestEffort`, `Terminating`, `NotTerminating` หรือ Pod ที่ใช้ PriorityClass หนึ่ง ๆ (ศึกษาเพิ่มเติมได้จากเอกสารอ้างอิง)

---

## 12. LimitRange: กฎขนาดกล่องมาตรฐาน

### 12.1 แนวคิดและฟิลด์

{{FIG:T27|LimitRange ป้ายกฎขนาดกล่อง}}

**LimitRange** เป็น object แบบ namespaced ที่คุม **ขนาดต่อกล่อง** (ต่อ container, ต่อ Pod หรือต่อ PersistentVolumeClaim) และ **เติมค่าตั้งต้น** ให้ของที่ไม่ได้ระบุ

| `type` | ใช้กับ | ฟิลด์ที่ใช้บ่อย |
|---|---|---|
| `Container` | ทุก container รวม init container และ sidecar | `defaultRequest` (requests ที่เติมให้), `default` (limits ที่เติมให้), `min`, `max`, `maxLimitRequestRatio` |
| `Pod` | ผลรวมของทุก container ใน Pod | `min`, `max`, `maxLimitRequestRatio` |
| `PersistentVolumeClaim` | ขนาดพื้นที่ที่ขอ | `min`, `max` (บท storage) |

ไฟล์ `labs/lab06-limitrange/limitrange.yaml` ของ LAB 6

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: box-size
  namespace: budget
spec:
  limits:
    - type: Container
      defaultRequest:            # ไม่ระบุ requests → เติมค่านี้ให้
        cpu: 100m
        memory: 64Mi
      default:                   # ไม่ระบุ limits → เติมค่านี้ให้
        cpu: 200m
        memory: 128Mi
      max:                       # ห้าม limits เกินค่านี้ (ต่อ container)
        cpu: 500m
        memory: 256Mi
```

ผลจริงจาก LAB 6

```text
$ kubectl describe limitrange -n budget
Name:       box-size
Namespace:  budget
Type        Resource  Min  Max    Default Request  Default Limit  Max Limit/Request Ratio
----        --------  ---  ---    ---------------  -------------  -----------------------
Container   memory    -    256Mi  64Mi             128Mi          -
Container   cpu       -    500m   100m             200m           -
```

ผลกับ Pod ที่ **ไม่ใส่ resources** (`no-request` ตัวเดิมที่ถูก quota ปฏิเสธใน LAB 5 คราวนี้สร้างได้)

```text
$ kubectl get pod no-request -n budget -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
```

และระบบติด annotation บอกว่าเติมอะไรให้

```text
kubernetes.io/limit-ranger: LimitRanger plugin set: cpu, memory request for container app; cpu, memory limit for container app
```

ผลกับ Pod ที่ขอ limit เกิน `max` (`big-pod.yaml` ขอ `limits.cpu: "1"`)

```text
$ kubectl apply -f labs/lab06-limitrange/big-pod.yaml
Error from server (Forbidden): error when creating "labs/lab06-limitrange/big-pod.yaml": pods "big" is forbidden: maximum cpu usage per Container is 500m, but limit is 1
```

ข้อควรรู้เพิ่มเติม

- LimitRange มีผลเฉพาะ **ตอนสร้าง/แก้ไข** Pod เหมือน quota Pod ที่มีอยู่ก่อนไม่ถูกแก้
- ถ้าตั้ง `default` แต่ไม่ตั้ง `defaultRequest` ระบบจะใช้ค่า `default` เป็น requests ด้วย
- container ที่ใส่ limits แต่ไม่ใส่ requests จะได้ requests เท่ากับ limits ของตัวเอง (กฎปกติของ Kubernetes) ไม่ใช่ `defaultRequest`

### 12.2 ใช้คู่กับ ResourceQuota

{{FIG:T28|ResourceQuota เทียบ LimitRange}}

ลำดับในด่านตรวจของ API server คือ **LimitRanger (เติมค่า + ตรวจ min/max) ก่อน แล้วจึงเป็น ResourceQuota (ตรวจงบรวม)** ผลที่ตามมา

1. Pod ที่ลืมใส่ resources ได้ค่าจาก LimitRange ก่อน จึงผ่านเงื่อนไข "must specify" ของ quota ได้
2. ใน LAB 6 ตอนที่ `pods` เต็ม 3/3 แล้ว `big-pod.yaml` ยังได้ข้อความ `maximum cpu usage per Container ...` ของ LimitRange ไม่ใช่ `exceeded quota` เพราะถูกตัดตกตั้งแต่ด่านแรก

**ตารางที่ 4** ResourceQuota เทียบกับ LimitRange

| | ResourceQuota | LimitRange |
|---|---|---|
| คุมอะไร | **ผลรวมทั้งโซน** (งบ) และจำนวน object | **ขนาดต่อกล่อง** (ต่อ container/Pod/PVC) |
| เติมค่าให้ไหม | ไม่ เพียงตรวจ | เติม `defaultRequest`/`default` |
| เมื่อผิด | `exceeded quota` / `must specify` | `maximum ... per Container` / `minimum ...` |
| ตรวจเมื่อไร | ตอนสร้าง/แก้ไข (หลัง LimitRange) | ตอนสร้าง/แก้ไข (ก่อน quota) |
| ดูด้วย | `kubectl describe quota -n <ns>` | `kubectl describe limitrange -n <ns>` |
| ภาพรวมทั้งสอง | `kubectl describe ns <ns>` แสดงทั้ง `Resource Quotas` และ `Resource Limits` | |

---

## 13. RBAC แบบ namespace: บัตรพนักงานเฉพาะโซน

### 13.1 ใครเป็นผู้เรียก API

{{FIG:T29|User และ ServiceAccount}}

ทุกคำขอที่เข้า API server ต้องผ่าน 2 ขั้น คือ **authentication** (คุณคือใคร) และ **authorization** (คุณทำสิ่งนี้ได้ไหม) **RBAC** (Role-Based Access Control) เป็นกลไก authorization หลัก ผู้เรียก (subject) มี 3 แบบ

| subject | คืออะไร | เป็น object ใน Kubernetes ไหม | ตัวอย่างชื่อ |
|---|---|---|---|
| **User** | คน | **ไม่มี** object User มาจากหลักฐานภายนอก เช่น client certificate (CN/O), OIDC | `kubernetes-admin` |
| **ServiceAccount** | ตัวตนของโปรแกรม/Pod | **มี** และเป็น namespaced ทุก namespace มี `default` | `system:serviceaccount:team-a:intern` |
| **Group** | กลุ่มของ User/ServiceAccount | ไม่มี object | `system:serviceaccounts:team-a`, `system:authenticated` |

ผลจริง (LAB 7): เราในฐานะผู้ใช้ kind คือ `kubernetes-admin` ในกลุ่ม `kubeadm:cluster-admins` ซึ่งมีสิทธิ์ทุกอย่าง

```text
$ kubectl auth whoami
ATTRIBUTE                                           VALUE
Username                                            kubernetes-admin
Groups                                              [kubeadm:cluster-admins system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [X509SHA256=ac241dd4...]
```

(`X509SHA256` บอกว่ายืนยันตัวตนด้วย client certificate ตัดค่าให้สั้น)

### 13.2 Role และ RoleBinding

{{FIG:T30|Role และ RoleBinding}}

- **Role** (namespaced) = การ์ดสิทธิ์ บอกว่า **ทำอะไร (verbs) กับอะไร (resources ใน apiGroups)** ได้ **ภายใน namespace ของ Role**
- **RoleBinding** (namespaced) = สายคล้องที่ผูก **subjects** (ใคร) กับ **roleRef** (การ์ดใบไหน) มีผล **เฉพาะ namespace ของ RoleBinding**

ไฟล์ `labs/lab07-rbac/sa-role-binding.yaml` ของ LAB 7

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: intern
  namespace: team-a
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: team-a
rules:
  - apiGroups: [""]                    # "" = core API group (Pod อยู่กลุ่มนี้)
    resources: ["pods", "pods/log"]    # pods/log = subresource สำหรับ kubectl logs
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: intern-pod-reader
  namespace: team-a
subjects:
  - kind: ServiceAccount
    name: intern
    namespace: team-a
roleRef:                               # แก้ทีหลังไม่ได้ ต้องลบแล้วสร้างใหม่
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
```

**ตารางที่ 5** verbs และคำสั่ง kubectl ที่เกี่ยวข้อง

| verb | คำสั่ง kubectl ตัวอย่าง |
|---|---|
| `get` | `kubectl get pod web`, `kubectl describe pod web` |
| `list` | `kubectl get pods` |
| `watch` | `kubectl get pods -w` |
| `create` | `kubectl create -f`, `kubectl run` |
| `update` / `patch` | `kubectl apply` กับของที่มีอยู่, `kubectl label`, `kubectl edit` |
| `delete` / `deletecollection` | `kubectl delete pod web` / `kubectl delete pods --all` |

subresource บางตัวต้องให้สิทธิ์แยก เช่น `kubectl logs` ต้องการ `get` บน `pods/log`, `kubectl exec` ต้องการ `create` บน `pods/exec` และ `kubectl port-forward` ต้องการ `create` บน `pods/portforward` (ยืนยันใน LAB 7 และ LAB สุดท้าย)

กฎสำคัญของ RBAC

- **allow-only** มีแต่การ "อนุญาต" ไม่มีกฎ "ห้าม" ค่าเริ่มต้นคือห้ามทุกอย่าง สิทธิ์จากหลาย binding รวมกันแบบ OR
- **`roleRef` แก้ไม่ได้** หลังสร้าง RoleBinding ถ้าจะเปลี่ยนการ์ดต้องลบแล้วสร้างใหม่
- Role/RoleBinding ใน `team-a` ไม่มีผลใด ๆ ใน `team-b`

### 13.3 ClusterRole กับ RoleBinding และ ClusterRoleBinding

{{FIG:T31|ClusterRole ใช้ในโซนเดียวหรือทั้งท่า}}

**ClusterRole** (cluster-scoped) คือสมุดกฎสิทธิ์มาตรฐานของท่าเรือ เขียนครั้งเดียวใช้ได้หลายที่ คลัสเตอร์มี ClusterRole สำเร็จรูปให้ (ผลจริง LAB 3: `view`, `edit`, `admin`, `cluster-admin` และอื่น ๆ รวม 77 ตัว)

| ClusterRole | สิทธิ์โดยสรุป |
|---|---|
| `view` | อ่านได้เกือบทุกอย่างใน namespace **ยกเว้น Secret** และ Role/RoleBinding |
| `edit` | `view` + สร้าง/แก้/ลบ object ทั่วไปใน namespace (ไม่รวม Role/RoleBinding) |
| `admin` | `edit` + จัดการ Role/RoleBinding ใน namespace (แต่แก้ ResourceQuota หรือตัว namespace ไม่ได้) |
| `cluster-admin` | ทุกอย่างทั้งคลัสเตอร์ |

**ตารางที่ 6** การจับคู่ Role กับ Binding

| การ์ด | สายคล้อง | ผล |
|---|---|---|
| Role | RoleBinding | สิทธิ์ใน namespace นั้น (แบบที่ใช้กับ `intern`) |
| ClusterRole | RoleBinding | ใช้กฎมาตรฐานแต่มีผล **แค่ namespace ของ RoleBinding** (แบบที่ใช้กับ `auditor`) |
| ClusterRole | ClusterRoleBinding | สิทธิ์ **ทุก namespace และของ cluster-scoped** ⚠️ ระวัง ให้เท่าที่จำเป็น |
| Role | ClusterRoleBinding | ทำไม่ได้ (ClusterRoleBinding อ้างได้แค่ ClusterRole) |

ไฟล์ `labs/lab07-rbac/view-clusterrole-binding.yaml` ผูก ClusterRole `view` ให้ SA `auditor` ด้วย RoleBinding ใน `team-b` ผลจริงจาก LAB 7: `auditor` ดู Pod และ ConfigMap ใน `team-b` ได้ แต่ Secret ไม่ได้ ลบไม่ได้ และดู `team-a` ไม่ได้

```text
$ kubectl auth can-i list pods -n team-b --as=system:serviceaccount:team-b:auditor
yes
$ kubectl auth can-i list secrets -n team-b --as=system:serviceaccount:team-b:auditor
no
$ kubectl get pods -n team-a --as=system:serviceaccount:team-b:auditor
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:team-b:auditor" cannot list resource "pods" in API group "" in the namespace "team-a"
```

### 13.4 ตรวจสิทธิ์ด้วย kubectl auth can-i

{{FIG:T32|auth can-i เครื่องอ่านบัตร}}

`kubectl auth can-i <verb> <resource> -n <ns>` ถาม API server ว่า "ทำได้ไหม" ได้คำตอบ `yes`/`no` โดยไม่ต้องลงมือจริง เพิ่ม `--as=<ผู้ใช้>` เพื่อสวมบทเป็นคนอื่น (impersonate ทำได้เพราะเราเป็น admin) ชื่อของ ServiceAccount ที่ใช้กับ `--as` คือ `system:serviceaccount:<namespace>:<ชื่อ>` ผลจริงจาก LAB 7

| คำถาม (`--as=system:serviceaccount:team-a:intern`) | คำตอบ |
|---|:---:|
| `list pods -n team-a` | yes |
| `delete pods -n team-a` | no |
| `get pods/log -n team-a` | yes |
| `list pods -n team-b` | no |
| `create pods -n team-a` | no |

ดูสิทธิ์ทั้งหมดด้วย `--list` (ตัดบางส่วน)

```text
$ kubectl auth can-i --list -n team-a --as=system:serviceaccount:team-a:intern
Resources                                       Non-Resource URLs                      Resource Names   Verbs
selfsubjectreviews.authentication.k8s.io        []                                     []               [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []               [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []               [create]
pods/log                                        []                                     []               [get list watch]
pods                                            []                                     []               [get list watch]
...
```

เมื่อทำสิ่งที่ไม่มีสิทธิ์จริง ข้อความ Forbidden บอกครบว่า **ใคร** ทำ **อะไร** กับ **ชนิดไหน** ใน **namespace ไหน**

```text
$ kubectl delete pod web -n team-a --as=system:serviceaccount:team-a:intern
Error from server (Forbidden): pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"
```

### 13.5 ใช้ตัวตนของ ServiceAccount จริง และกับดัก --token

{{FIG:T33|token ของ ServiceAccount กับ context ใหม่}}

`--as` เป็นการ "สวมบท" ของ admin ถ้าอยากใช้ตัวตนของ ServiceAccount จริง ๆ ต้องมี **token** ขอ token อายุสั้นด้วย

```bash
T=$(kubectl create token intern -n team-a --duration=1h)
```

token เป็นข้อความยาว (ใน LAB 7 ยาว 925 ตัวอักษร ขึ้นต้น `eyJhbGciOi...`) เป็นรหัสลับ **ห้ามแปะลงเอกสารหรือแชท**

**กับดัก:** คิดว่าแค่ใส่ `--token` ก็จะกลายเป็น intern ผลจริงจาก LAB 7

```text
$ kubectl --token=$T get pods -n team-b
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          53s

$ kubectl --token=$T auth whoami
ATTRIBUTE                                           VALUE
Username                                            kubernetes-admin
Groups                                              [kubeadm:cluster-admins system:authenticated]
...
```

ยังเป็น `kubernetes-admin` เพราะ user `kind-lab` ใน kubeconfig มี **client certificate** อยู่แล้ว kubectl จึงยังส่ง certificate ไปด้วย และ API server ยืนยันตัวตนจาก certificate สำเร็จก่อน token ไม่ถูกใช้

**วิธีที่ถูก:** สร้าง user ใหม่ใน kubeconfig ที่มี **แต่ token** แล้วสร้าง context ใหม่ที่ใช้ user นั้น

```bash
kubectl config set-credentials intern --token=$T
kubectl config set-context intern@lab --cluster=kind-lab --user=intern --namespace=team-a
kubectl --context intern@lab auth whoami
```

ผลจริงจาก LAB 7

```text
ATTRIBUTE                                           VALUE
Username                                            system:serviceaccount:team-a:intern
UID                                                 14329203-56ac-41c3-8758-19d9d0aadd74
Groups                                              [system:serviceaccounts system:serviceaccounts:team-a system:authenticated]
...
```

ผ่าน context นี้ intern ดู Pod และ log ใน `team-a` ได้ แต่ลบ, ดู `team-b`, ดู Node/namespace และ `exec` ไม่ได้

```text
$ kubectl --context intern@lab exec web -- id
error: unable to upgrade connection: pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot create resource "pods/exec" in API group "" in the namespace "team-a"
```

token จาก `kubectl create token` ผูกกับ ServiceAccount ตัวนั้น เมื่อ ServiceAccount หรือ namespace ถูกลบ token ใช้ไม่ได้ทันที (ผลจริง LAB สุดท้าย: `error: You must be logged in to the server (Unauthorized)`) อย่าลืมลบ context และ user ที่สร้างไว้ด้วย `kubectl config delete-context ...` และ `kubectl config delete-user ...`

> **Pod ใช้ ServiceAccount อย่างไร:** Pod ระบุ `spec.serviceAccountName` (ไม่ระบุ = `default`) แล้ว kubelet จะ mount token อายุสั้นของ ServiceAccount นั้นไว้ที่ `/var/run/secrets/kubernetes.io/serviceaccount/` ให้โปรแกรมใน Pod ใช้เรียก API ได้ตามสิทธิ์ของ ServiceAccount (ปิดได้ด้วย `automountServiceAccountToken: false`)

---

## 14. Pod Security Admission: ด่านตรวจหน้าโซน

### 14.1 Pod Security Standards 3 ระดับ

{{FIG:T34|Pod Security Standards 3 ระดับ}}

Kubernetes กำหนดมาตรฐานความปลอดภัยของ Pod (Pod Security Standards) ไว้ 3 ระดับ

| ระดับ | แนวคิด | ตัวอย่างสิ่งที่ห้าม |
|---|---|---|
| `privileged` | ไม่จำกัดเลย | – (สำหรับงานระบบที่ต้องการสิทธิ์เต็ม) |
| `baseline` | กันของอันตรายที่ชัดเจน ใช้ได้กับ image ทั่วไปส่วนใหญ่ | `privileged: true`, `hostNetwork`/`hostPID`/`hostIPC`, volume แบบ `hostPath`, `hostPort`, เพิ่ม capability นอกชุดปลอดภัย, seccomp `Unconfined` |
| `restricted` | เข้มที่สุด ตามแนวปฏิบัติที่ดี | ทุกข้อของ baseline + ต้อง `runAsNonRoot: true` (และห้าม `runAsUser: 0`), `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]` (เพิ่มคืนได้แค่ `NET_BIND_SERVICE`), `seccompProfile.type` เป็น `RuntimeDefault` หรือ `Localhost`, ใช้ volume ได้เฉพาะชนิดที่ปลอดภัย (เช่น `emptyDir`, `configMap`, `secret`, `projected`, `persistentVolumeClaim`) |

**Pod Security Admission (PSA)** เป็นด่านตรวจที่มีในตัว API server อยู่แล้ว ทำหน้าที่บังคับมาตรฐานเหล่านี้ **ต่อ namespace** (PSA มาแทน PodSecurityPolicy ที่ถูกถอดออกตั้งแต่ Kubernetes v1.25)

### 14.2 3 โหมด ตั้งด้วย label ของ namespace

{{FIG:T35|โหมด enforce warn audit}}

| label บน namespace | โหมด | ผลเมื่อ Pod ไม่ผ่านระดับที่กำหนด |
|---|---|---|
| `pod-security.kubernetes.io/enforce: <ระดับ>` | ไม้กั้น | **ปฏิเสธ** ไม่สร้าง Pod (`Forbidden`) |
| `pod-security.kubernetes.io/warn: <ระดับ>` | กระดิ่ง | สร้างได้ แต่ kubectl แสดง `Warning: would violate PodSecurity ...` |
| `pod-security.kubernetes.io/audit: <ระดับ>` | สมุดบันทึก | สร้างได้ แต่จดลง audit log ของ API server |
| `pod-security.kubernetes.io/<โหมด>-version: latest` หรือ `v1.37` | | เลือกเวอร์ชันของมาตรฐาน (ไม่ระบุ = `latest`) |

ตั้งหลายโหมดพร้อมกันได้ เช่น namespace `som-prod` ใน LAB สุดท้าย (`som-shop-envs/k8s/00-namespaces.yaml`)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: som-prod
  labels:
    env: prod
    team: som
    pod-security.kubernetes.io/enforce: restricted        # ด่านปฏิเสธ
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted           # กระดิ่งเตือนที่ kubectl
```

ส่วน `som-dev` และ `som-staging` ใส่แค่ `warn: restricted` (เห็นคำเตือนแต่ไม่บล็อก) ซึ่งเป็นรูปแบบที่พบบ่อย: ผ่อนใน dev เข้มใน prod

ผลจริงจาก LAB 8 ใน namespace `secure` ที่ตั้ง `enforce=baseline` + `warn=restricted`

```text
$ kubectl apply -f labs/lab08-psa/root-nginx-pod.yaml
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/root-nginx created

$ kubectl apply -f labs/lab08-psa/privileged-pod.yaml
Error from server (Forbidden): error when creating "labs/lab08-psa/privileged-pod.yaml": pods "privileged" is forbidden: violates PodSecurity "baseline:latest": privileged (container "app" must not set securityContext.privileged=true)
```

nginx ทางการรันเป็น root ผ่าน baseline (แต่มีคำเตือนของ restricted) ส่วน Pod ที่ขอ `privileged: true` ถูก baseline ปฏิเสธ

### 14.3 ตรวจเฉพาะตอนสร้าง Pod

PSA ตรวจ **ตอนสร้าง Pod** เท่านั้น ถ้าเปลี่ยน label ของ namespace ให้เข้มขึ้นภายหลัง Pod เดิม **ยังรันต่อ** มีแต่คำเตือน ก่อนเปลี่ยนจริงจึงควรลองด้วย `--dry-run=server` ผลจริงจาก LAB 8

```text
$ kubectl label --dry-run=server --overwrite ns secure pod-security.kubernetes.io/enforce=restricted
Warning: existing pods in namespace "secure" violate the new PodSecurity enforce level "restricted:latest"
Warning: root-nginx: allowPrivilegeEscalation != false, unrestricted capabilities, runAsNonRoot != true, seccompProfile
namespace/secure labeled (server dry run)
```

หลังเปลี่ยนจริง `root-nginx` เดิมยัง `Running` แต่ Pod ใหม่แบบเดียวกันถูกปฏิเสธ

```text
$ kubectl run root-nginx-2 -n secure --image=nginx:1.27-alpine
Error from server (Forbidden): pods "root-nginx-2" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "root-nginx-2" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "root-nginx-2" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "root-nginx-2" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "root-nginx-2" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

เมื่อ Pod มีหลาย container ข้อความจะรวมชื่อ container ไว้ในแต่ละข้อ เช่น ร้านฉบับบทที่ 2 (`som-shop-v002.yaml`) ที่ไม่มี `securityContext` เลยเมื่อ apply เข้า `som-prod` (ผลจริง LAB สุดท้าย)

```text
Error from server (Forbidden): error when creating "som-shop-envs/k8s/som-shop-v002.yaml": pods "som-shop-old" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (containers "db", "wait-for-db", "db-seed", "web" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (containers "db", "wait-for-db", "db-seed", "web" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or containers "db", "wait-for-db", "db-seed", "web" must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "db", "wait-for-db", "db-seed", "web" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

### 14.4 ทำ Pod ให้ผ่าน restricted

{{FIG:T36|เช็กลิสต์ผ่าน restricted}}

ข้อความ Forbidden บอก 4 เรื่องที่ต้องแก้ แต่ละเรื่องแก้ด้วย `securityContext` ระดับ Pod หรือระดับ container

| ข้อความ | แก้ด้วย | ระดับ |
|---|---|---|
| `runAsNonRoot != true` | `runAsNonRoot: true` + `runAsUser: <เลขที่ไม่ใช่ 0>` | Pod หรือ container |
| `allowPrivilegeEscalation != false` | `allowPrivilegeEscalation: false` | container |
| `unrestricted capabilities` | `capabilities: {drop: ["ALL"]}` | container |
| `seccompProfile` | `seccompProfile: {type: RuntimeDefault}` | Pod หรือ container |

ไฟล์ `labs/lab08-psa/restricted-ok-pod.yaml` ของ LAB 8

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: restricted-ok
  namespace: secure
spec:
  terminationGracePeriodSeconds: 1
  securityContext:               # ระดับ Pod: ใช้กับทุก container
    runAsNonRoot: true           # ห้ามรันเป็น root
    runAsUser: 1000              # uid ที่ใช้รัน (ต้องเป็นตัวเลข)
    runAsGroup: 1000             # gid หลัก
    seccompProfile:
      type: RuntimeDefault       # ตัวกรอง system call มาตรฐานของ container runtime
  containers:
    - name: app
      image: busybox:1.36
      command: ["sleep", "3600"]
      securityContext:           # ระดับ container
        allowPrivilegeEscalation: false   # ห้ามยกระดับสิทธิ์ (เช่น setuid)
        capabilities:
          drop: ["ALL"]          # ทิ้งสิทธิ์พิเศษของ Linux ทั้งหมด
```

ผลจริง: Pod ผ่าน restricted และรันด้วย `uid=1000 gid=1000 groups=1000` (ถ้าไม่ใส่ `runAsGroup` จะได้ `gid=0(root)` ซึ่ง restricted ยอม แต่ไม่ควร)

**กับดัก image ที่ระบุ USER เป็นชื่อ:** image `som-shop-web` ระบุ `USER node` (เป็น "ชื่อ" ไม่ใช่ตัวเลข) เมื่อ Pod ตั้ง `runAsNonRoot: true` แต่ไม่ได้ระบุ `runAsUser` kubelet ตรวจไม่ได้ว่า `node` ไม่ใช่ root จึงไม่ยอมเริ่ม container ผลจริงจาก LAB สุดท้าย (ทดลองลบ `runAsUser: 1000`)

```text
som-shop-nouid   1/2     Init:CreateContainerConfigError   0          20s
Error: container has runAsNonRoot and image has non-numeric user (node), cannot verify user is non-root (pod: "som-shop-nouid_som-dev(...)", container: db-seed)
```

ข้อนี้ **PSA ไม่เตือน** เพราะ manifest ตั้ง `runAsNonRoot: true` ครบตามกฎแล้ว error มาจาก kubelet ตอนสร้าง container ทางแก้คือใส่ `runAsUser` เป็นตัวเลข (`node` = 1000, `postgres` ใน image alpine = 70)

> nginx ทางการ (`nginx:1.27-alpine`) เริ่มทำงานเป็น root เพื่อเปิด port 80 จึงผ่าน restricted ไม่ได้ ถ้าต้องการ nginx ใน namespace restricted ต้องใช้ image รุ่นที่ออกแบบให้รันแบบ non-root

---

## 15. แนวปฏิบัติการตั้งชื่อและแบ่ง namespace

{{FIG:T37|แนวปฏิบัติการแบ่ง namespace}}

**การแบ่งและตั้งชื่อ**

- เลือกแกนการแบ่งให้ชัด: ตามทีม, ตาม environment, ตามแอป หรือ **ทีม + environment** (`som-dev`, `som-staging`, `som-prod`) และใช้รูปแบบเดียวกันทั้งองค์กร
- **อย่าแบ่งละเอียดเกินไป** namespace ละ 1 Pod ทำให้ต้องดูแล quota/RBAC/policy จำนวนมาก
- ติด label มาตรฐานให้ namespace เช่น `env`, `team`, `app.kubernetes.io/part-of` เพื่อค้นหาและใช้กับ selector
- ไม่ใช้ชื่อขึ้นต้น `kube-` (สงวนให้ระบบตามธรรมเนียม แม้ API จะยอม)

**ชุดตั้งต้นของทุก namespace ใหม่**

| ชิ้น | ทำไม |
|---|---|
| ResourceQuota | กันทีมเดียวใช้ทรัพยากรจนคนอื่นช้า |
| LimitRange | เติมค่าให้ Pod ที่ลืมใส่ resources (ไม่งั้นติด "must specify" ของ quota) และกันกล่องใหญ่เกิน |
| RoleBinding | ให้ทีมมีสิทธิ์เฉพาะโซนตัวเอง (มักใช้ ClusterRole `edit`/`view` + RoleBinding) |
| label ของ PSA | อย่างน้อย `warn=restricted` และ `enforce=restricted` ใน prod |
| NetworkPolicy | default deny + อนุญาตเฉพาะที่จำเป็น |

**ข้อควรระวังในการทำงานจริง**

- **อย่าใช้ `default` กับงานจริง** ไม่มี quota, LimitRange และเป็นที่ที่ของ "หลง" มาอยู่เมื่อลืมระบุ namespace
- **`kubectl delete ns` ลบทั้งก้อน** ไม่มีถังขยะ ตรวจชื่อและ context ทุกครั้ง
- ในสคริปต์และกับ prod ให้ใส่ `-n` ชัดเจนทุกคำสั่ง
- ต้องการแยกขาดจริง (ลูกค้าต่างบริษัท, ข้อกำหนดด้านความปลอดภัยสูง) ให้แยกคลัสเตอร์

> **ปูทางบทหน้า:** บทนี้ยังใช้ Pod เดี่ยวและเปิดหน้าร้านด้วย `kubectl port-forward` บทถัดไปจะให้ตัวสร้าง Pod อัตโนมัติ (Deployment) ดูแลจำนวน Pod และใช้ Service เป็นที่อยู่คงที่ของร้าน ซึ่งทั้งสองอย่างเป็น object แบบ namespaced อีกเช่นกัน ทุกอย่างที่เรียนในบทนี้ (quota, LimitRange, RBAC, PSA, NetworkPolicy และชื่อ DNS `<service>.<namespace>`) จะใช้ต่อได้ทันที

---
