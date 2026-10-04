
## LAB 4: ข้ามโซน: Pod IP, เรือเดียวกัน และ NetworkPolicy

{{FIG:L07|LAB 4 ต่างโซนอยู่เรือเดียวกันและคุยกันได้}}

**เป้าหมาย:** เห็นด้วยตาว่า namespace ไม่ได้แยก Node และไม่ได้กั้นเครือข่าย ดู search domain ของ DNS แล้วสร้างรั้วด้วย NetworkPolicy และเปิดประตูให้เฉพาะโซนที่ต้องการ

**ไฟล์:** `labs/lab04-network/`

| ไฟล์ | เนื้อหา |
|---|---|
| `zones.yaml` | namespace `team-a` (label `team: a`) และ `team-b` (label `team: b`) |
| `web-pod.yaml` | nginx ชื่อ `web` ใน `team-a` ปักไว้ที่ `lab-worker` ด้วย `nodeSelector` |
| `client-pods.yaml` | busybox ชื่อ `client` ใน `team-a` และ `team-b` (ชื่อเดียวกัน) บน `lab-worker` ทั้งคู่ |
| `np-same-ns.yaml` | รั้ว: ทุก Pod ใน `team-a` รับเฉพาะจาก Pod ใน `team-a` |
| `np-allow-team-b.yaml` | ประตู: Pod `app=web` รับจาก namespace `team-b` ได้ด้วย |

ทุก Pod ติด label `lab: net` ไว้ดูรวมกันได้

### ขั้นที่ 1: สร้างโซนและ Pod

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab04-network/zones.yaml
kubectl apply -f labs/lab04-network/web-pod.yaml -f labs/lab04-network/client-pods.yaml
kubectl wait --for=condition=Ready pod -l lab=net -A --timeout=120s
kubectl get pods -A -o wide -l lab=net
```

```text
namespace/team-a created
namespace/team-b created
pod/web created
pod/client created
pod/client created
pod/client condition met
pod/web condition met
pod/client condition met
NAMESPACE   NAME     READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
team-a      client   1/1     Running   0          8s    10.244.2.7   lab-worker   <none>           <none>
team-a      web      1/1     Running   0          8s    10.244.2.6   lab-worker   <none>           <none>
team-b      client   1/1     Running   0          8s    10.244.2.8   lab-worker   <none>           <none>
```

Pod ของ 2 โซนอยู่บน **เรือลำเดียวกัน** (`lab-worker`)

### ขั้นที่ 2: ก่อนมีรั้ว ข้ามโซนได้

เก็บ IP ของ `web` ไว้ในตัวแปร (IP ในเครื่องนักศึกษาต่างจากเอกสาร ใช้ `$WEB_IP` แทนการพิมพ์เลขเอง)

```bash
WEB_IP=$(kubectl get pod web -n team-a -o jsonpath='{.status.podIP}'); echo $WEB_IP
kubectl -n team-b exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
kubectl -n team-a exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
```

```text
10.244.2.6
<title>Welcome to nginx!</title>
<title>Welcome to nginx!</title>
```

ทั้ง `team-b` และ `team-a` เข้าเว็บได้เหมือนกัน (`-T 3` = รอไม่เกิน 3 วินาที)

### ขั้นที่ 3: search domain ของแต่ละโซน

```bash
kubectl -n team-b exec client -- cat /etc/resolv.conf
kubectl -n team-a exec client -- cat /etc/resolv.conf
```

```text
search team-b.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
search team-a.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

เครือข่ายไม่ได้แยก แต่ **ชื่อ DNS แยกตามโซน** บรรทัด `search` ขึ้นต้นด้วยชื่อ namespace ของ Pod เอง (ทฤษฎีหัวข้อ 9.2)

### ขั้นที่ 4: สร้างรั้วรอบ team-a

{{FIG:L08|LAB 4 NetworkPolicy กั้นแล้วเปิดประตู}}

```bash
cat labs/lab04-network/np-same-ns.yaml
kubectl apply -f labs/lab04-network/np-same-ns.yaml
kubectl get netpol -n team-a
time kubectl -n team-b exec client -- wget -qO- -T 3 http://$WEB_IP
kubectl -n team-a exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
kubectl -n blue exec snack -- wget -qO- -T 3 http://$WEB_IP
```

```yaml
# LAB 4 (รั้วที่ 1): ทุก Pod ใน team-a รับการเชื่อมต่อเข้าเฉพาะจาก Pod ในโซน team-a เอง
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: team-a
spec:
  podSelector: {}                # {} = เลือกทุก Pod ในโซนนี้ → Pod เหล่านี้เปลี่ยนเป็น "ปฏิเสธ ยกเว้นที่อนุญาต"
  policyTypes: ["Ingress"]       # คุมเฉพาะขาเข้า
  ingress:
    - from:
        - podSelector: {}        # podSelector อย่างเดียว (ไม่มี namespaceSelector) = Pod ในโซนเดียวกันเท่านั้น
```

```text
networkpolicy.networking.k8s.io/allow-same-namespace created
NAME                   POD-SELECTOR   AGE
allow-same-namespace   <none>         0s
wget: download timed out
command terminated with exit code 1

real	0m3.060s
user	0m0.029s
sys	0m0.025s
<title>Welcome to nginx!</title>
wget: download timed out
command terminated with exit code 1
```

- รั้วมีผล **ทันที** (คำสั่งแรกหลัง apply ก็ถูกกั้นแล้ว) kindnet ของ kind บังคับใช้ NetworkPolicy จริง
- `team-b` รอครบ 3 วินาทีแล้ว `download timed out` เพราะ packet ถูกทิ้งเงียบ ๆ (ไม่มีข้อความปฏิเสธกลับมา)
- `team-a/client` ยังเข้าได้ และ `blue/snack` จากโซนอื่นก็ถูกกั้นเช่นกัน
- คอลัมน์ `POD-SELECTOR` แสดง `<none>` สำหรับ `podSelector: {}` (หมายถึงทุก Pod ไม่ใช่ไม่มี Pod)

### ขั้นที่ 5: เปิดประตูให้ team-b เข้า web

```bash
cat labs/lab04-network/np-allow-team-b.yaml
kubectl apply -f labs/lab04-network/np-allow-team-b.yaml
for i in 1 2 3 4 5 6 7 8 9 10; do if kubectl -n team-b exec client -- wget -qO- -T 2 http://$WEB_IP >/dev/null 2>&1; then echo "team-b เข้าได้ในรอบที่ $i"; break; fi; sleep 1; done
kubectl -n team-b exec client -- wget -qO- -T 3 http://$WEB_IP | grep -o '<title>.*</title>'
kubectl -n blue exec snack -- wget -qO- -T 3 http://$WEB_IP
kubectl -n team-b exec client -- wget -qO- -T 3 http://$(kubectl get pod client -n team-a -o jsonpath='{.status.podIP}'):80
```

```yaml
# LAB 4 (ประตูที่ 2): เปิดให้ทุก Pod จากโซนที่มี label kubernetes.io/metadata.name=team-b เข้า web ได้
# policy รวมกันแบบ OR: ผ่านข้อใดข้อหนึ่งก็เข้าได้
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
              kubernetes.io/metadata.name: team-b   # label ที่ระบบใส่ให้ทุก namespace อัตโนมัติ
```

```text
networkpolicy.networking.k8s.io/allow-from-team-b created
team-b เข้าได้ในรอบที่ 1
<title>Welcome to nginx!</title>
wget: download timed out
command terminated with exit code 1
wget: download timed out
command terminated with exit code 1
```

`team-b` กลับมาเข้า `web` ได้ทันที แต่ `blue` ยังถูกกั้น และ `team-b` ยังเข้า `client` ของ `team-a` ไม่ได้ เพราะประตูที่ 2 เลือกเฉพาะ Pod `app=web`

### ขั้นที่ 6: อ่าน policy ทั้งสอง

```bash
kubectl get netpol -n team-a
kubectl describe netpol -n team-a
```

```text
NAME                   POD-SELECTOR   AGE
allow-from-team-b      app=web        7s
allow-same-namespace   <none>         13s
Name:         allow-from-team-b
Namespace:    team-a
Created on:   2026-10-04 20:30:34 +0700 +07
Labels:       <none>
Annotations:  <none>
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

### สิ่งที่เห็น

- Pod ต่าง namespace อยู่บนเรือลำเดียวกันได้ และคุยกันด้วย Pod IP ได้ทันทีถ้าไม่มี NetworkPolicy
- `/etc/resolv.conf` ของแต่ละ Pod มี search domain ตาม namespace ของตัวเอง
- `allow-same-namespace` เปลี่ยน Pod ทุกตัวใน `team-a` เป็น "ปฏิเสธยกเว้นที่อนุญาต" ผู้ถูกกั้นได้ `download timed out`
- policy รวมกันแบบ OR: `web` รับจาก team-a (policy 1) หรือ team-b (policy 2) ส่วน `client` ของ team-a รับแค่ team-a

| ผู้เรียก → ปลายทาง | ก่อน policy | หลัง `allow-same-namespace` | หลัง `allow-from-team-b` |
|---|:---:|:---:|:---:|
| `team-a/client` → `team-a/web` | ✅ | ✅ | ✅ |
| `team-b/client` → `team-a/web` | ✅ | ❌ timed out | ✅ |
| `blue/snack` → `team-a/web` | (ไม่ได้ทดสอบ) | ❌ timed out | ❌ timed out |
| `team-b/client` → `team-a/client` | (ไม่ได้ทดสอบ) | (ไม่ได้ทดสอบ) | ❌ timed out |

> **🤔 คำถามชวนคิด:** ถ้าลบ `allow-same-namespace` ออกแต่เก็บ `allow-from-team-b` ไว้ `team-a/client` จะยังเข้า `web` ได้ไหม และ `blue/snack` จะเข้า `team-a/client` ได้ไหม (ลองทำนายก่อนทดลอง)

**เก็บกวาด:** เก็บ `team-a` และ `team-b` (รวม Pod และ policy) ไว้ใช้ใน LAB 7 ถ้าจะหยุดที่ LAB นี้ ให้ `kubectl delete ns team-a team-b`

---

## LAB 5: ResourceQuota: งบของโซน

{{FIG:L09|LAB 5 ใบงบของโซน budget}}

**เป้าหมาย:** ตั้งงบให้โซน `budget` แล้วเห็นการปฏิเสธ 2 แบบ คือ Pod ที่ไม่ระบุขนาด (`must specify`) และ Pod ที่ทำให้เกินงบ (`exceeded quota`)

**ไฟล์:** `labs/lab05-quota/quota.yaml` (namespace `budget` + ResourceQuota `budget-quota`), `no-request-pod.yaml` (busybox ไม่มี resources), `small-pods.yaml` (busybox 4 ตัว ตัวละ requests 100m/64Mi, limits 200m/128Mi)

```yaml
# LAB 5: โซน budget + ใบงบประมาณ (ResourceQuota) ของโซน
apiVersion: v1
kind: Namespace
metadata:
  name: budget
---
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

> คำนวณก่อนลงมือ: Pod เล็ก 4 ตัวรวมกันขอ requests 400m/256Mi และ limits 800m/512Mi ซึ่ง **ยังไม่เกินงบ CPU/หน่วยความจำ** ตัวที่ 4 จึงควรชนแค่ `pods: 3`

### ขั้นที่ 1: สร้างโซนและใบงบ

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab05-quota/quota.yaml
kubectl describe quota -n budget
kubectl get quota -n budget
```

```text
namespace/budget created
resourcequota/budget-quota created
Name:            budget-quota
Namespace:       budget
Resource         Used  Hard
--------         ----  ----
limits.cpu       0     1
limits.memory    0     512Mi
pods             0     3
requests.cpu     0     500m
requests.memory  0     256Mi
NAME           REQUEST                                                     LIMIT                                     AGE
budget-quota   pods: 0/3, requests.cpu: 0/500m, requests.memory: 0/256Mi   limits.cpu: 0/1, limits.memory: 0/512Mi   0s
```

### ขั้นที่ 2: Pod ที่ไม่ระบุขนาด

```bash
kubectl apply -f labs/lab05-quota/no-request-pod.yaml
```

```text
Error from server (Forbidden): error when creating "labs/lab05-quota/no-request-pod.yaml": pods "no-request" is forbidden: failed quota: budget-quota: must specify limits.cpu for: app; limits.memory for: app; requests.cpu for: app; requests.memory for: app
```

### ขั้นที่ 3: Pod เล็ก 4 ตัว

```bash
kubectl apply -f labs/lab05-quota/small-pods.yaml
kubectl get pods -n budget
kubectl describe quota -n budget
```

```text
pod/small-1 created
pod/small-2 created
pod/small-3 created
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-4" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
NAME      READY   STATUS              RESTARTS   AGE
small-1   0/1     ContainerCreating   0          0s
small-2   0/1     ContainerCreating   0          0s
small-3   0/1     ContainerCreating   0          0s
Name:            budget-quota
Namespace:       budget
Resource         Used   Hard
--------         ----   ----
limits.cpu       600m   1
limits.memory    384Mi  512Mi
pods             3      3
requests.cpu     300m   500m
requests.memory  192Mi  256Mi
```

### ขั้นที่ 4: ภาพรวมของโซน

```bash
kubectl describe ns budget
```

```text
Name:         budget
Labels:       kubernetes.io/metadata.name=budget
Annotations:  <none>
Status:       Active

Resource Quotas
  Name:            budget-quota
  Resource         Used   Hard
  --------         ---    ---
  limits.cpu       600m   1
  limits.memory    384Mi  512Mi
  pods             3      3
  requests.cpu     300m   500m
  requests.memory  192Mi  256Mi

No LimitRange resource.
```

### สิ่งที่เห็น

- quota ตรวจ **ตอนสร้าง** Pod ที่ไม่ผ่านถูกปฏิเสธทันที ไม่ได้ค้าง Pending (`small-4` ไม่มีใน `kubectl get pods` เลย)
- Pod ที่ไม่ระบุ resources ถูกปฏิเสธพร้อมรายชื่อค่าที่ขาดครบ 4 ค่าและชื่อ container (`app`)
- `small-4` ชนแค่ `pods` ตามที่คำนวณไว้ ข้อความ `exceeded quota` บอก requested / used / limited
- Used ของ CPU/หน่วยความจำ = ผลรวมของ 3 Pod (300m/192Mi และ 600m/384Mi)

> **🤔 คำถามชวนคิด:** ถ้าแก้ quota เป็น `pods: "10"` แต่คงค่าอื่นไว้ Pod เล็กจะสร้างได้สูงสุดกี่ตัว ค่าไหนจะชนก่อน

**เก็บกวาด:** เก็บ `budget` ไว้ใช้ต่อใน LAB 6 ทันที (ถ้าจะหยุดที่นี่ `kubectl delete ns budget`)

---

## LAB 6: LimitRange: กฎขนาดกล่อง

{{FIG:L10|LAB 6 LimitRange เติมค่าและกันกล่องใหญ่}}

**เป้าหมาย:** เพิ่ม LimitRange ให้โซน `budget` แล้วเห็นว่า Pod ที่ไม่ระบุ resources ได้ค่าตั้งต้นและผ่าน quota ได้ ส่วน Pod ที่ขอเกิน `max` ถูกปฏิเสธ

**ต้องมีจาก LAB 5:** namespace `budget` ที่มี `small-1`, `small-2`, `small-3`

**ไฟล์:** `labs/lab06-limitrange/limitrange.yaml`, `plain-pod.yaml` (Pod ไม่ระบุ resources ชื่อ `plain`), `big-pod.yaml` (ขอ `limits.cpu: "1"`)

```yaml
# LAB 6: ป้ายกฎขนาดกล่องของโซน budget (ใช้กับแต่ละ container)
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

### ขั้นที่ 1: คืนที่ว่างในงบ แล้วติดป้ายกฎขนาดกล่อง

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl delete pod small-2 small-3 -n budget
kubectl apply -f labs/lab06-limitrange/limitrange.yaml
kubectl describe limitrange -n budget
```

```text
pod "small-2" deleted from budget namespace
pod "small-3" deleted from budget namespace
limitrange/box-size created
Name:       box-size
Namespace:  budget
Type        Resource  Min  Max    Default Request  Default Limit  Max Limit/Request Ratio
----        --------  ---  ---    ---------------  -------------  -----------------------
Container   memory    -    256Mi  64Mi             128Mi          -
Container   cpu       -    500m   100m             200m           -
```

### ขั้นที่ 2: Pod ที่ไม่ระบุขนาด คราวนี้ผ่าน

```bash
kubectl apply -f labs/lab05-quota/no-request-pod.yaml
kubectl get pod no-request -n budget -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
kubectl get pod no-request -n budget -o jsonpath="{.metadata.annotations.kubernetes\.io/limit-ranger}{\"\n\"}"
kubectl apply -f labs/lab06-limitrange/plain-pod.yaml
kubectl get pod plain -n budget -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
```

```text
pod/no-request created
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
LimitRanger plugin set: cpu, memory request for container app; cpu, memory limit for container app
pod/plain created
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}
```

ไฟล์ `no-request-pod.yaml` ตัวเดียวกับที่ถูกปฏิเสธใน LAB 5 คราวนี้ผ่าน เพราะ LimitRange เติมค่าให้ก่อนถึงด่าน quota

### ขั้นที่ 3: กล่องใหญ่เกิน max

```bash
kubectl apply -f labs/lab06-limitrange/big-pod.yaml
kubectl get pods -n budget
kubectl describe quota -n budget
```

```text
Error from server (Forbidden): error when creating "labs/lab06-limitrange/big-pod.yaml": pods "big" is forbidden: maximum cpu usage per Container is 500m, but limit is 1
NAME         READY   STATUS              RESTARTS   AGE
no-request   1/1     Running             0          1s
plain        0/1     ContainerCreating   0          1s
small-1      1/1     Running             0          10s
Name:            budget-quota
Namespace:       budget
Resource         Used   Hard
--------         ----   ----
limits.cpu       600m   1
limits.memory    384Mi  512Mi
pods             3      3
requests.cpu     300m   500m
requests.memory  192Mi  256Mi
```

สังเกตว่าตอนนี้ `pods` เต็ม 3/3 แล้ว แต่ `big` ได้ข้อความของ **LimitRange** ไม่ใช่ `exceeded quota` เพราะ LimitRanger ตรวจก่อน quota

### ขั้นที่ 4: ทั้งสองด่านในภาพเดียว

```bash
kubectl apply -f labs/lab05-quota/small-pods.yaml
kubectl describe ns budget
```

```text
pod/small-1 unchanged
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-2" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-3" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
Error from server (Forbidden): error when creating "labs/lab05-quota/small-pods.yaml": pods "small-4" is forbidden: exceeded quota: budget-quota, requested: pods=1, used: pods=3, limited: pods=3
Name:         budget
Labels:       kubernetes.io/metadata.name=budget
Annotations:  <none>
Status:       Active

Resource Quotas
  Name:            budget-quota
  Resource         Used   Hard
  --------         ---    ---
  limits.cpu       600m   1
  limits.memory    384Mi  512Mi
  pods             3      3
  requests.cpu     300m   500m
  requests.memory  192Mi  256Mi

Resource Limits
 Type       Resource  Min  Max    Default Request  Default Limit  Max Limit/Request Ratio
 ----       --------  ---  ---    ---------------  -------------  -----------------------
 Container  memory    -    256Mi  64Mi             128Mi          -
 Container  cpu       -    500m   100m             200m           -
```

### สิ่งที่เห็น

- Pod ที่ไม่ระบุ resources ได้ requests 100m/64Mi และ limits 200m/128Mi จาก LimitRange พร้อม annotation `kubernetes.io/limit-ranger`
- LimitRange + quota ทำงานคู่กัน: LimitRange เติมค่าให้ Pod ที่ลืม จึงผ่านเงื่อนไข `must specify` ของ quota
- `max` บังคับต่อ container และถูกตรวจก่อน quota
- `kubectl describe ns` แสดงทั้ง `Resource Quotas` และ `Resource Limits` ของโซน

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `default.memory` ของ LimitRange เป็น 256Mi แล้วสร้าง Pod ไม่ระบุ resources เพิ่ม (หลังลบให้ `pods` ว่าง) ค่า `limits.memory` ของ quota จะหมดเร็วขึ้นแค่ไหน การตั้งค่า default สูงหรือต่ำเกินไปมีผลเสียอย่างไร

**เก็บกวาด:** `kubectl delete ns budget` (หรือเก็บไว้ลบรวมใน LAB 9)

---

## LAB 7: RBAC: บัตรพนักงานเฉพาะโซน

{{FIG:L11|LAB 7 บัตร intern ของ team-a}}

**เป้าหมาย:** สร้าง ServiceAccount + Role + RoleBinding ตรวจสิทธิ์ด้วย `kubectl auth can-i --as` ใช้ ClusterRole สำเร็จรูปในโซนเดียว และใช้ token ของ ServiceAccount จริงผ่าน context ใหม่ พร้อมเห็นกับดัก `--token`

**ต้องมีจาก LAB 4:** namespace `team-a` (Pod `web`, `client`) และ `team-b` (Pod `client`)

**ไฟล์:** `labs/lab07-rbac/sa-role-binding.yaml` (ใน `team-a`: SA `intern`, Role `pod-reader` = get/list/watch บน `pods`, `pods/log`, RoleBinding `intern-pod-reader`) และ `view-clusterrole-binding.yaml` (ใน `team-b`: SA `auditor` + RoleBinding `auditor-view` ที่อ้าง ClusterRole `view`)

```yaml
# LAB 7: ใช้สมุดกฎมาตรฐานของท่าเรือ (ClusterRole "view") แต่ผูกด้วย RoleBinding → มีผลแค่โซน team-b
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auditor
  namespace: team-b
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: auditor-view
  namespace: team-b
subjects:
  - kind: ServiceAccount
    name: auditor
    namespace: team-b
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole              # ClusterRole สำเร็จรูป: view (ดูได้เกือบทุกอย่าง ยกเว้น Secret)
  name: view
```

(เนื้อหาของ `sa-role-binding.yaml` ดูทฤษฎีหัวข้อ 13.2 หรือ `cat labs/lab07-rbac/sa-role-binding.yaml`)

### ขั้นที่ 1: เราเป็นใคร และสร้างบัตร

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl auth whoami
kubectl apply -f labs/lab07-rbac/sa-role-binding.yaml -f labs/lab07-rbac/view-clusterrole-binding.yaml
kubectl get sa,role,rolebinding -n team-a
kubectl get sa,rolebinding -n team-b -o wide
```

```text
ATTRIBUTE                                           VALUE
Username                                            kubernetes-admin
Groups                                              [kubeadm:cluster-admins system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [X509SHA256=ac241dd4...]
serviceaccount/intern created
role.rbac.authorization.k8s.io/pod-reader created
rolebinding.rbac.authorization.k8s.io/intern-pod-reader created
serviceaccount/auditor created
rolebinding.rbac.authorization.k8s.io/auditor-view created
NAME                     AGE
serviceaccount/default   51s
serviceaccount/intern    1s

NAME                                        CREATED AT
role.rbac.authorization.k8s.io/pod-reader   2026-10-04T13:31:09Z

NAME                                                      ROLE              AGE
rolebinding.rbac.authorization.k8s.io/intern-pod-reader   Role/pod-reader   1s
NAME                     AGE
serviceaccount/auditor   1s
serviceaccount/default   51s

NAME                                                 ROLE               AGE   USERS   GROUPS   SERVICEACCOUNTS
rolebinding.rbac.authorization.k8s.io/auditor-view   ClusterRole/view   1s                     team-b/auditor
```

(ค่า `X509SHA256` ตัดให้สั้น) เราคือ `kubernetes-admin` ในกลุ่ม `kubeadm:cluster-admins` ทำได้ทุกอย่าง และทุก namespace มี SA `default` อยู่แล้ว

### ขั้นที่ 2: ตรวจสิทธิ์ intern ด้วยเครื่องอ่านบัตร

```bash
kubectl auth can-i list pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i delete pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i get pods/log -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i list pods -n team-b --as=system:serviceaccount:team-a:intern
kubectl auth can-i create pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl auth can-i --list -n team-a --as=system:serviceaccount:team-a:intern | head -6
```

```text
yes
no
yes
no
no
Resources                                       Non-Resource URLs                      Resource Names   Verbs
selfsubjectreviews.authentication.k8s.io        []                                     []               [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []               [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []               [create]
pods/log                                        []                                     []               [get list watch]
pods                                            []                                     []               [get list watch]
```

คำตอบ `no` ทำให้คำสั่งคืนค่า exit code 1 (ใช้ในสคริปต์ได้) และรายการ `--list` แสดงสิทธิ์จาก Role ของเรา (`pods`, `pods/log`) รวมกับสิทธิ์พื้นฐานที่ทุกคนได้ (ถามว่าตัวเองเป็นใคร/ทำอะไรได้)

### ขั้นที่ 3: ลงมือจริงในบทบาท intern และ auditor

```bash
kubectl delete pod web -n team-a --as=system:serviceaccount:team-a:intern
kubectl get pods -n team-a --as=system:serviceaccount:team-a:intern
kubectl logs web -n team-a --tail=2 --as=system:serviceaccount:team-a:intern
kubectl auth can-i list pods -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i list configmaps -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i list secrets -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i delete pods -n team-b --as=system:serviceaccount:team-b:auditor
kubectl auth can-i list pods -n team-a --as=system:serviceaccount:team-b:auditor
kubectl get pods -n team-a --as=system:serviceaccount:team-b:auditor
```

```text
Error from server (Forbidden): pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          52s
web      1/1     Running   0          52s
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
yes
yes
no
no
no
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:team-b:auditor" cannot list resource "pods" in API group "" in the namespace "team-a"
```

log ของ nginx แสดงคำขอจาก `10.244.2.8` (IP ของ `team-b/client` ใน LAB 4) ส่วน `auditor` ดูได้ทั้ง Pod และ ConfigMap ใน team-b แต่อ่าน Secret ไม่ได้ ลบไม่ได้ และมองไม่เห็น team-a

### ขั้นที่ 4: กับดัก --token

{{FIG:L12|LAB 7 --token กับ context ใหม่}}

ขอ token อายุ 1 ชั่วโมงของ intern แล้วลองส่งด้วย `--token`

```bash
T=$(kubectl create token intern -n team-a --duration=1h)
echo "token ยาว ${#T} ตัวอักษร ขึ้นต้น ${T:0:10}..."
kubectl --token=$T get pods -n team-b
kubectl --token=$T auth whoami
```

```text
token ยาว 925 ตัวอักษร ขึ้นต้น eyJhbGciOi...
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          53s
ATTRIBUTE                                           VALUE
Username                                            kubernetes-admin
Groups                                              [kubeadm:cluster-admins system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [X509SHA256=ac241dd4...]
```

ยังเห็น team-b และยังเป็น `kubernetes-admin` เพราะ user `kind-lab` มี client certificate (LAB 2 ขั้นที่ 4) API server ยืนยันตัวตนจาก certificate ได้ก่อน token จึงไม่ถูกใช้ **อย่า `echo $T` ทั้งก้อน** token คือรหัสผ่านของ intern

### ขั้นที่ 5: context ใหม่ที่มีแต่ token ของ intern

```bash
kubectl config set-credentials intern --token=$T
kubectl config set-context intern@lab --cluster=kind-lab --user=intern --namespace=team-a
kubectl config get-contexts
kubectl --context intern@lab auth whoami
kubectl --context intern@lab get pods
kubectl --context intern@lab logs web --tail=3
```

```text
User "intern" set.
Context "intern@lab" created.
CURRENT   NAME         CLUSTER    AUTHINFO   NAMESPACE
          intern@lab   kind-lab   intern     team-a
*         kind-lab     kind-lab   kind-lab   default
ATTRIBUTE                                           VALUE
Username                                            system:serviceaccount:team-a:intern
UID                                                 14329203-56ac-41c3-8758-19d9d0aadd74
Groups                                              [system:serviceaccounts system:serviceaccounts:team-a system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [JTI=9e870e3d-...]
NAME     READY   STATUS    RESTARTS   AGE
client   1/1     Running   0          54s
web      1/1     Running   0          54s
10.244.2.7 - - [04/Oct/2026:13:30:31 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
10.244.2.8 - - [04/Oct/2026:13:30:34 +0000] "GET / HTTP/1.1" 200 615 "-" "Wget" "-"
```

context `intern@lab` ไม่ใช่ context ปัจจุบัน (ไม่มี `*`) เราเลือกใช้ทีละคำสั่งด้วย `--context` จึงไม่กระทบคำสั่งอื่น ลองสิ่งที่ intern ไม่ควรทำได้

```bash
kubectl --context intern@lab delete pod web
kubectl --context intern@lab get pods -n team-b
kubectl --context intern@lab get nodes
kubectl --context intern@lab get ns
kubectl --context intern@lab exec web -- id
```

```text
Error from server (Forbidden): pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:team-a:intern" cannot list resource "pods" in API group "" in the namespace "team-b"
Error from server (Forbidden): nodes is forbidden: User "system:serviceaccount:team-a:intern" cannot list resource "nodes" in API group "" at the cluster scope
Error from server (Forbidden): namespaces is forbidden: User "system:serviceaccount:team-a:intern" cannot list resource "namespaces" in API group "" at the cluster scope
error: unable to upgrade connection: pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot create resource "pods/exec" in API group "" in the namespace "team-a"
```

ข้อความของ Node และ namespace ลงท้าย `at the cluster scope` เพราะเป็นของส่วนกลาง และ `exec` ต้องการสิทธิ์ `create` บน `pods/exec` ซึ่ง Role ไม่ได้ให้

### สิ่งที่เห็น

- ServiceAccount + Role + RoleBinding ทำให้ intern ดูและอ่าน log ได้เฉพาะ `team-a` ลบ, สร้าง, exec และดูโซนอื่นไม่ได้
- ClusterRole `view` + RoleBinding ใน `team-b` ทำให้ auditor อ่านได้เฉพาะ `team-b` และไม่รวม Secret
- `kubectl auth can-i --as` และคำสั่งจริงที่ใส่ `--as` ให้ผลตรงกัน
- `kubectl --token` บน kubeconfig ของ kind **ยังเป็น admin** ต้องสร้าง user + context ใหม่ที่มีแต่ token จึงเห็นสิทธิ์จริงของ intern

> **🤔 คำถามชวนคิด:** ถ้าอยากให้ intern ใช้ `kubectl exec` เข้า Pod ใน team-a ได้ด้วย ต้องเพิ่มกฎอะไรใน Role (บอก resource และ verb) และควรให้สิทธิ์นี้กับเด็กฝึกงานหรือไม่ เพราะอะไร

**เก็บกวาด (ต้องทำ):** ลบ context และ user ของ intern ออกจาก kubeconfig แล้วยืนยันว่ายังใช้ `kind-lab`

```bash
kubectl config current-context
kubectl config delete-context intern@lab
kubectl config delete-user intern
unset T
kubectl config get-contexts
```

```text
kind-lab
deleted context intern@lab from /root/.kube/config
deleted user intern from /root/.kube/config
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
```

namespace `team-a`/`team-b` จะลบรวมใน LAB 9 (หรือ `kubectl delete ns team-a team-b` ตอนนี้ก็ได้)

---

## LAB 8: Pod Security Admission: ด่านตรวจหน้าโซน

{{FIG:L13|LAB 8 ด่านตรวจ restricted}}

**เป้าหมาย:** ตั้งด่านตรวจของ namespace ด้วย label เห็นผลของ `warn` และ `enforce` ในระดับ baseline และ restricted เปลี่ยนระดับอย่างปลอดภัยด้วย `--dry-run=server` และทำ Pod ให้ผ่าน restricted

**ไฟล์:** `labs/lab08-psa/root-nginx-pod.yaml` (nginx ทางการ ไม่มี securityContext), `privileged-pod.yaml` (busybox `privileged: true`), `restricted-ok-pod.yaml` (busybox ที่ตั้ง securityContext ครบ ดูทฤษฎีหัวข้อ 14.4)

### ขั้นที่ 1: สร้างโซน secure ระดับ baseline + เตือน restricted

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl create ns secure
kubectl label ns secure pod-security.kubernetes.io/enforce=baseline pod-security.kubernetes.io/warn=restricted
kubectl get ns secure --show-labels
```

```text
namespace/secure created
namespace/secure labeled
NAME     STATUS   AGE   LABELS
secure   Active   1s    kubernetes.io/metadata.name=secure,pod-security.kubernetes.io/enforce=baseline,pod-security.kubernetes.io/warn=restricted
```

### ขั้นที่ 2: nginx ที่รันเป็น root และ Pod ที่ขอ privileged

```bash
kubectl apply -f labs/lab08-psa/root-nginx-pod.yaml
kubectl apply -f labs/lab08-psa/privileged-pod.yaml
kubectl wait --for=condition=Ready pod/root-nginx -n secure --timeout=60s
kubectl exec -n secure root-nginx -- id
```

```text
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/root-nginx created
Error from server (Forbidden): error when creating "labs/lab08-psa/privileged-pod.yaml": pods "privileged" is forbidden: violates PodSecurity "baseline:latest": privileged (container "app" must not set securityContext.privileged=true)
pod/root-nginx condition met
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
```

- `root-nginx` **ผ่าน** ด่าน baseline (enforce) แต่ได้ **Warning** จากกระดิ่ง restricted (warn) 4 ข้อ และรันเป็น `uid=0(root)` จริง
- `privileged` ถูกด่าน baseline **ปฏิเสธ**

### ขั้นที่ 3: ลองยกระดับเป็น restricted แบบไม่บังคับจริงก่อน

```bash
kubectl label --dry-run=server --overwrite ns secure pod-security.kubernetes.io/enforce=restricted
kubectl get ns secure --show-labels
```

```text
Warning: existing pods in namespace "secure" violate the new PodSecurity enforce level "restricted:latest"
Warning: root-nginx: allowPrivilegeEscalation != false, unrestricted capabilities, runAsNonRoot != true, seccompProfile
namespace/secure labeled (server dry run)
NAME     STATUS   AGE   LABELS
secure   Active   2s    kubernetes.io/metadata.name=secure,pod-security.kubernetes.io/enforce=baseline,pod-security.kubernetes.io/warn=restricted
```

dry-run บอกล่วงหน้าว่า Pod เดิมตัวไหนจะผิดกฎ และ label ยังเป็น `enforce=baseline` เหมือนเดิม

### ขั้นที่ 4: บังคับ restricted จริง

```bash
kubectl label --overwrite ns secure pod-security.kubernetes.io/enforce=restricted
kubectl get pods -n secure
kubectl run root-nginx-2 -n secure --image=nginx:1.27-alpine
```

```text
Warning: existing pods in namespace "secure" violate the new PodSecurity enforce level "restricted:latest"
Warning: root-nginx: allowPrivilegeEscalation != false, unrestricted capabilities, runAsNonRoot != true, seccompProfile
namespace/secure labeled
NAME         READY   STATUS    RESTARTS   AGE
root-nginx   1/1     Running   0          1s
Error from server (Forbidden): pods "root-nginx-2" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "root-nginx-2" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "root-nginx-2" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "root-nginx-2" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "root-nginx-2" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

`root-nginx` เดิม **ยัง Running** (PSA ตรวจเฉพาะตอนสร้าง) แต่ nginx ตัวใหม่แบบเดียวกันถูกปฏิเสธ

### ขั้นที่ 5: Pod ที่ผ่าน restricted

```bash
cat labs/lab08-psa/restricted-ok-pod.yaml
kubectl apply -f labs/lab08-psa/restricted-ok-pod.yaml
kubectl wait --for=condition=Ready pod/restricted-ok -n secure --timeout=60s
kubectl exec -n secure restricted-ok -- id
kubectl get ns secure --show-labels
```

```text
pod/restricted-ok created
pod/restricted-ok condition met
uid=1000 gid=1000 groups=1000
NAME     STATUS   AGE   LABELS
secure   Active   3s    kubernetes.io/metadata.name=secure,pod-security.kubernetes.io/enforce=restricted,pod-security.kubernetes.io/warn=restricted
```

ไม่มี Warning เลย และรันเป็น uid/gid 1000 (ถ้าลบ `runAsGroup: 1000` ออกจากไฟล์ จะได้ `uid=1000 gid=0(root) groups=0(root)` ซึ่ง restricted ยอม แต่ไม่ควร)

### สิ่งที่เห็น

- label `pod-security.kubernetes.io/<โหมด>=<ระดับ>` บน namespace คือการตั้งด่าน: `enforce` ปฏิเสธ, `warn` เตือนที่ kubectl
- baseline ยอม nginx ที่รันเป็น root แต่ไม่ยอม `privileged: true` ส่วน restricted ไม่ยอมทั้งคู่
- เปลี่ยนระดับภายหลัง Pod เดิมยังรัน ใช้ `--dry-run=server` ดูผลกระทบก่อน
- ผ่าน restricted ด้วย securityContext 4 เรื่อง: runAsNonRoot (+ runAsUser), allowPrivilegeEscalation false, drop ALL, seccomp RuntimeDefault

> **🤔 คำถามชวนคิด:** ทีม dev อยากใช้ `enforce=restricted` ตั้งแต่วันแรก แต่ image หลายตัวยังรันเป็น root ควรเริ่มด้วยการตั้ง label แบบไหนก่อน และใช้ข้อมูลอะไรตัดสินว่าพร้อมเปลี่ยนเป็น enforce

**เก็บกวาด:** `kubectl delete ns secure` (หรือเก็บไว้ลบรวมใน LAB 9)

---

## LAB 9: ลบโซนทั้งก้อน

{{FIG:L14|LAB 9 ลบโซน doomed}}

**เป้าหมาย:** เห็นว่าลบ namespace = ลบทุกอย่างข้างใน เห็นสถานะ `Terminating` และ finalizer ทดลองสร้างของระหว่างกำลังลบ ตรวจว่า namespace ระบบตัวไหนลบไม่ได้ แล้วเก็บกวาด namespace ของ LAB 1–8 ทั้งหมด

**ไฟล์:** `labs/lab09-delete-ns/doomed.yaml` (namespace `doomed` + ConfigMap `menu` + SA `cleaner` + Role `cleaner-role` + RoleBinding `cleaner-binding` + ResourceQuota `doomed-quota` (`pods: "5"`) + Pod busybox `crate-1`, `crate-2`) Pod ทั้งสองตั้ง `terminationGracePeriodSeconds: 15` (`sleep` เป็น PID 1 ไม่ตอบ SIGTERM จึงรอครบ 15 วินาที) โซนจะค้าง Terminating นานพอให้ทดลอง

### ขั้นที่ 1: สร้างโซนที่มีของหลายชนิด

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab09-delete-ns/doomed.yaml
kubectl wait --for=condition=Ready pod --all -n doomed --timeout=60s
kubectl get all,sa,role,rolebinding,cm,quota -n doomed
kubectl get ns doomed -o jsonpath="{.spec.finalizers}{\"\n\"}"
```

```text
namespace/doomed created
configmap/menu created
serviceaccount/cleaner created
role.rbac.authorization.k8s.io/cleaner-role created
rolebinding.rbac.authorization.k8s.io/cleaner-binding created
resourcequota/doomed-quota created
pod/crate-1 created
pod/crate-2 created
pod/crate-1 condition met
pod/crate-2 condition met
```

ผลของคำสั่งที่สาม (`all` + ชนิดที่ระบุเพิ่ม) ส่วนแรกที่มาจาก `all` มีแค่ Pod ส่วน ServiceAccount, Role, RoleBinding, ConfigMap และ quota ปรากฏเพราะเราระบุชนิดเพิ่มเอง (`all` ไม่ได้แปลว่าทุกชนิด)

```text
NAME          READY   STATUS    RESTARTS   AGE
pod/crate-1   1/1     Running   0          0s
pod/crate-2   1/1     Running   0          0s

NAME                     AGE
serviceaccount/cleaner   0s
serviceaccount/default   0s

NAME                                          CREATED AT
role.rbac.authorization.k8s.io/cleaner-role   2026-10-04T13:31:41Z

NAME                                                    ROLE                AGE
rolebinding.rbac.authorization.k8s.io/cleaner-binding   Role/cleaner-role   1s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      1s
configmap/menu               1      1s

NAME                         REQUEST     LIMIT   AGE
resourcequota/doomed-quota   pods: 2/5           1s
["kubernetes"]
```

### ขั้นที่ 2: สั่งลบแบบไม่รอ แล้วสังเกตระหว่าง Terminating

พิมพ์ชุดนี้ต่อกันเร็ว ๆ (หรือคัดลอกทั้งบล็อก) ต้องทำภายในราว 15 วินาทีหลังสั่งลบ

```bash
kubectl delete ns doomed --wait=false
kubectl get ns doomed
kubectl run x -n doomed --image=busybox:1.36 -- sleep 60
kubectl create configmap late -n doomed --from-literal=a=b
kubectl get pods -n doomed
kubectl get sa,role,rolebinding,cm,quota -n doomed
```

```text
namespace "doomed" deleted
NAME     STATUS        AGE
doomed   Terminating   1s
Error from server (Forbidden): pods "x" is forbidden: unable to create new content in namespace doomed because it is being terminated
error: failed to create configmap: configmaps "late" is forbidden: unable to create new content in namespace doomed because it is being terminated
NAME      READY   STATUS    RESTARTS   AGE
crate-1   1/1     Running   0          1s
crate-2   1/1     Running   0          1s
NAME                     AGE
serviceaccount/cleaner   2s
serviceaccount/default   2s
...
```

- `deleted` แปลว่า "รับคำขอแล้ว" โซนยังอยู่ในสถานะ `Terminating`
- สร้างของใหม่ทุกชนิดไม่ได้ (`unable to create new content ... being terminated`)
- ช่วงแรกของข้างในยังอยู่ครบ controller กำลังทยอยลบ (Pod รอ grace 15 วินาที)

### ขั้นที่ 3: รอจนหายจริง

```bash
time kubectl wait --for=delete ns/doomed --timeout=120s
kubectl get ns
kubectl get nodes
```

```text
namespace/doomed condition met

real	0m20.096s
...
NAME                 STATUS   AGE
blue                 Active   2m28s
budget               Active   76s
default              Active   4m19s
green                Active   2m28s
kube-node-lease      Active   4m19s
kube-public          Active   4m19s
kube-system          Active   4m19s
local-path-storage   Active   4m15s
secure               Active   44s
team-a               Active   104s
team-b               Active   104s
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   4m19s   v1.37.0
lab-worker          Ready    <none>          4m9s    v1.37.0
lab-worker2         Ready    <none>          4m9s    v1.37.0
```

`doomed` หายไปในราว 20 วินาที namespace อื่นและเรือทั้ง 3 ลำไม่กระทบ (รายการ namespace ของนักศึกษาขึ้นกับว่าเก็บกวาด LAB ก่อนหน้าไปแล้วหรือยัง)

### ขั้นที่ 4: namespace ระบบที่ลบไม่ได้ (ทดสอบแบบไม่ลบจริง)

> ⚠️ ใช้ `--dry-run=server` **ทุกบรรทัดยกเว้น `default`** (ซึ่งระบบกันไว้แน่นอน) ห้ามตัด `--dry-run=server` ออกเด็ดขาด

```bash
kubectl delete ns default
kubectl delete ns kube-system --dry-run=server
kubectl delete ns kube-public --dry-run=server
kubectl delete ns kube-node-lease --dry-run=server
```

```text
Error from server (Forbidden): namespaces "default" is forbidden: this namespace may not be deleted
Error from server (Forbidden): namespaces "kube-system" is forbidden: this namespace may not be deleted
Error from server (Forbidden): namespaces "kube-public" is forbidden: this namespace may not be deleted
namespace "kube-node-lease" deleted (server dry run)
```

ระบบกันการลบแค่ `default`, `kube-system`, `kube-public` ส่วน `kube-node-lease` **ผ่าน dry-run = ลบได้จริงถ้าสั่ง** แต่ห้ามลบเพราะเป็นที่เก็บ heartbeat ของเรือทุกลำ

### ขั้นที่ 5: เก็บกวาด namespace ของ LAB 1–8 ในคำสั่งเดียว

```bash
time kubectl delete ns blue green team-a team-b budget secure
kubectl get ns
kubectl config get-contexts
```

```text
namespace "blue" deleted
namespace "green" deleted
namespace "team-a" deleted
namespace "team-b" deleted
namespace "budget" deleted
namespace "secure" deleted

real	0m42.224s
...
NAME                 STATUS   AGE
default              Active   5m6s
kube-node-lease      Active   5m6s
kube-public          Active   5m6s
kube-system          Active   5m6s
local-path-storage   Active   5m2s
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
```

ใช้เวลาราว 42 วินาที เพราะ Pod `blue/peek` จาก LAB 2 สร้างด้วย `kubectl run` (grace period ค่าเริ่มต้น 30 วินาที และ `sleep` ไม่ตอบ SIGTERM) ถ้าลบ namespace บางตัวไปแล้ว kubectl จะแจ้ง `NotFound` สำหรับตัวนั้น ไม่เป็นไร

### สิ่งที่เห็น

- `kubectl delete ns` ลบ Pod, ConfigMap, SA, Role, RoleBinding, quota ทั้งหมดในโซน ส่วน Node และ namespace อื่นไม่กระทบ
- ลำดับ: `Terminating` ทันที → controller ลบของข้างใน (รอ grace ของ Pod) → เอา finalizer `kubernetes` ออก → หายจริง
- ระหว่าง Terminating สร้างของใหม่ไม่ได้
- `kubectl get all` ไม่ได้แสดงทุกชนิด
- ระบบป้องกันการลบ `default`, `kube-system`, `kube-public` แต่ **ไม่กัน** `kube-node-lease`

> **🤔 คำถามชวนคิด:** ถ้า namespace หนึ่งค้าง `Terminating` นานหลายนาที นักศึกษาจะตรวจหาสาเหตุด้วยคำสั่งอะไรบ้าง (ใบ้: ดู `status.conditions` และหาของที่ยังเหลือ ดูทฤษฎีหัวข้อ 8.3)

**เก็บกวาด:** ทำไปแล้วในขั้นที่ 5 ตอนนี้คลัสเตอร์ควรเหลือ namespace ตั้งต้น 5 ตัวและ context อยู่ที่ `default`

---
