
## LAB 10: LAB สุดท้าย: ร้านน้องส้มแยก environment

{{FIG:L15|LAB 10 ภาพเปิด ร้านน้องส้ม 3 environment}}

**เรื่องเล่า:** ร้านอาหารแมวน้องส้มมีทีมพัฒนาที่ลองของใหม่ทุกวัน ทีมทดสอบ และร้านจริงที่ลูกค้าใช้ น้องส้มจะเปิดร้านทั้ง 3 environment ในคลัสเตอร์เดียว แต่ละ environment อยู่ในโซนของตัวเอง ใช้ manifest **ไฟล์เดียว** Pod ชื่อ `som-shop` เหมือนกันทุกโซน หน้าร้านบอกเองว่าอยู่โซนไหน ร้านจริงมีงบ กฎขนาดกล่อง และด่านตรวจระดับ restricted เด็กฝึกงานมีบัตรที่ดูได้อย่างเดียวและเฉพาะโซน dev และสุดท้ายลบโซน dev ทั้งก้อนโดยร้านจริงไม่สะดุด

**เป้าหมาย:** รวมทุกอย่างของบทนี้: namespace + label, manifest เดียวหลาย namespace, Downward API `metadata.namespace`, ResourceQuota + LimitRange + Pod Security `restricted` ใน prod, RBAC ของ intern, port-forward หลาย environment พร้อมกัน และการลบ environment ทั้งก้อน

**ต้องมี:** คลัสเตอร์สะอาดจาก LAB 9 (เหลือ namespace ตั้งต้น 5 ตัว, context อยู่ที่ `default`) และพื้นที่ดิสก์สำหรับ build image ราว 1 GB

### 10.1 สถาปัตยกรรมและไฟล์

| ไฟล์ใน `som-shop-envs/k8s/` | เนื้อหา | มี `metadata.namespace`? |
|---|---|:---:|
| `00-namespaces.yaml` | namespace `som-dev`, `som-staging` (label `env`, `team: som`, `pod-security.kubernetes.io/warn: restricted`) และ `som-prod` (เพิ่ม `enforce: restricted`, `enforce-version: latest`) | – (เป็น Namespace) |
| `prod-guardrails.yaml` | ResourceQuota `prod-budget` (`pods: "2"`, requests 1 CPU/1Gi, limits 2 CPU/2Gi) และ LimitRange `prod-box-size` (defaultRequest 50m/64Mi, default 200m/128Mi, max 1 CPU/1Gi) | ✓ `som-prod` (ของ prod เท่านั้น) |
| `som-shop.yaml` | Pod `som-shop`: sidecar `db` (postgres), init `wait-for-db`, `db-seed` และ `web` (som-shop-web:1.1) พร้อม securityContext ระดับ restricted และ env ที่บอก namespace | ✗ (เลือกด้วย `-n`) |
| `som-shop-v002.yaml` | สำเนาร้านฉบับบทที่ 2 ชื่อ `som-shop-old` ไม่มี securityContext ไว้ลองกับด่านของ prod | ✗ |
| `intern-rbac.yaml` | ใน `som-dev`: SA `intern`, Role `shop-viewer` (`pods`, `pods/log`: get/list/watch), RoleBinding `intern-shop-viewer` | ✓ `som-dev` |

{{FIG:L16|Downward API ส่งชื่อ namespace เข้าหน้าร้าน}}

ส่วนสำคัญของ `som-shop.yaml` (ตัดบางส่วน ดูไฟล์เต็มด้วย `cat som-shop-envs/k8s/som-shop.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  # ชื่อเดียวกันได้ทุกโซน (ชื่อเต็ม = <namespace>/som-shop)
  # บรรทัด name ห้ามมีคอมเมนต์ต่อท้าย เพราะ LAB ใช้ sed 's/name: som-shop$/.../' เปลี่ยนชื่อสาขา
  name: som-shop
  labels:
    app: som-shop
spec:
  securityContext:               # ระดับ Pod: ใช้กับทุก container
    runAsNonRoot: true           # ห้ามรันเป็น root
    fsGroup: 70                  # volume (emptyDir) เป็นของกลุ่ม 70 = postgres เขียนได้
    seccompProfile:
      type: RuntimeDefault
  # ... (ตัด)
  initContainers:
    - name: db
      image: postgres:17.11-alpine
      restartPolicy: Always
      securityContext:
        runAsUser: 70            # uid ของ postgres ใน image alpine
        runAsGroup: 70
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
      # ... (ตัด)
  containers:
    - name: web
      image: som-shop-web:1.1
      imagePullPolicy: IfNotPresent
      securityContext:
        runAsUser: 1000          # image ระบุ USER node เป็นชื่อ จึงต้องใส่ตัวเลข
        runAsGroup: 1000
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
      env:
        - name: POD_NAMESPACE      # Downward API: namespace ของ Pod นี้ (ต้องประกาศก่อน SHOP_NAME)
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: SHOP_NAME          # → "ร้านอาหารแมวน้องส้ม (som-dev)" / "(som-staging)" / "(som-prod)"
          value: "ร้านอาหารแมวน้องส้ม ($(POD_NAMESPACE))"
        - name: SHOP_EYEBROW       # ข้อความเล็กเหนือชื่อร้าน (som-shop-web:1.1 อ่านจาก env)
          value: "⚓ ท่าเรือ Kubernetes · โซน $(POD_NAMESPACE)"
        - name: SHOP_FOOTER        # ข้อความท้ายหน้า
          value: "Next.js + PostgreSQL · Kubernetes LAB 004 · namespace $(POD_NAMESPACE)"
        - name: DATABASE_URL
          value: postgres://som:meow1234@localhost:5432/catshop
      # ... (ตัด)
```

- **ไม่มี `metadata.namespace`** ไฟล์เดียวจึงสั่งเข้าได้ทุกโซนด้วย `-n`
- `POD_NAMESPACE` ได้ค่าจาก Downward API (บทที่ 3 ใช้ `spec.nodeName` บทนี้ใช้ `metadata.namespace`) แล้ว `$(POD_NAMESPACE)` ถูกแทนค่าใน env ตัวถัดไป หน้าร้านแต่ละโซนจึงแสดงต่างกันโดยไม่ต้องแก้ไฟล์
- ทุก container มี securityContext ครบ 4 เรื่องของ restricted และระบุ uid/gid เป็นตัวเลข (`db`, `wait-for-db` = 70, `db-seed`, `web` = 1000) `fsGroup: 70` ทำให้ postgres เขียน emptyDir ได้
- resources ของทุก container ยังเหมือนบทที่ 2 (ระบุครบจึงผ่าน quota และไม่เกิน max ของ LimitRange)
- รหัส `meow1234` ใช้เพื่อการเรียนเท่านั้น

> **ทำไมต้อง build image ใหม่เป็น `som-shop-web:1.1`:** แอปในโฟลเดอร์ `som-shop-envs/app` แก้จากบทที่ 2 เพียงจุดเดียว คือ `app/page.tsx` อ่านข้อความเล็กเหนือชื่อร้านจาก `SHOP_EYEBROW` และข้อความท้ายหน้าจาก `SHOP_FOOTER` (ถ้าไม่ตั้ง ใช้ข้อความเดิมของบทที่ 2 ทุกตัวอักษร) image `som-shop-web:1.0` ของบทที่ 2–3 ยังรันได้แต่หน้าเว็บจะไม่บอกชื่อโซนที่หัวและท้ายหน้า Dockerfile เหมือนเดิม (`USER node`)

### 10.2 เตรียม image ให้ทุก Node

🐧 **ใน SSH session ของ k8s-lab** (เริ่มที่ `/workspace/004_kubernetes_namespace/02_LAB`)

```bash
cd som-shop-envs/app
time docker build -q -t som-shop-web:1.1 .
cd ../..
docker images som-shop-web
time kind load docker-image som-shop-web:1.1 --name lab
```

```text
sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c

real	0m28.328s
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
som-shop-web:1.1   d1aecb886b11        305MB         76.6MB        
Image: "som-shop-web:1.1" with ID "sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.1" with ID "sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.1" with ID "sha256:d1aecb886b11e889228016287c9a6bdaf794c74f1e2d9c87f4e147e497199b6c" not yet present on node "lab-control-plane", loading...

real	0m4.847s
```

(`-q` = แสดงแค่ ID ของ image ที่ได้ ถ้าอยากเห็นขั้นตอนการ build ให้ตัด `-q` ออก ครั้งแรกอาจใช้เวลาหลายนาทีเพราะต้องดึง `node:22-alpine` และติดตั้ง dependency)

image ของ postgres เป็นแบบหลาย platform `kind load docker-image` ตรง ๆ อาจล้มเหลว จึงใช้ `docker save --platform` เลือก platform เดียวแล้ว `kind load image-archive` (เครื่องสถาปัตยกรรม ARM ให้เปลี่ยนเป็น `linux/arm64` ซึ่งไม่ได้ทดสอบในเอกสารนี้)

```bash
docker pull -q postgres:17.11-alpine
time (docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab)
docker exec lab-worker crictl images | grep -E "som-shop|postgres"
```

```text
docker.io/library/postgres:17.11-alpine

real	0m5.620s
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.1                  4e9bfe88de285       76.6MB
```

`crictl images` บนเรือ `lab-worker` ต้องเห็นทั้งสอง image (ID ที่ containerd แสดงต่างจาก ID ของ docker ได้ เป็นเรื่องปกติ)

### 10.3 สร้าง 3 โซนและชุดป้องกันของ prod

{{FIG:L17|ชุดป้องกันของ som-prod}}

```bash
kubectl apply -f som-shop-envs/k8s/00-namespaces.yaml
kubectl get ns -l team=som -L env
kubectl get ns -l team=som --show-labels
kubectl apply -f som-shop-envs/k8s/prod-guardrails.yaml
kubectl describe quota,limitrange -n som-prod
```

```text
namespace/som-dev created
namespace/som-staging created
namespace/som-prod created
NAME          STATUS   AGE   ENV
som-dev       Active   0s    dev
som-prod      Active   0s    prod
som-staging   Active   0s    staging
NAME          STATUS   AGE   LABELS
som-dev       Active   0s    env=dev,kubernetes.io/metadata.name=som-dev,pod-security.kubernetes.io/warn=restricted,team=som
som-prod      Active   0s    env=prod,kubernetes.io/metadata.name=som-prod,pod-security.kubernetes.io/enforce-version=latest,pod-security.kubernetes.io/enforce=restricted,pod-security.kubernetes.io/warn=restricted,team=som
som-staging   Active   0s    env=staging,kubernetes.io/metadata.name=som-staging,pod-security.kubernetes.io/warn=restricted,team=som
resourcequota/prod-budget created
limitrange/prod-box-size created
Name:            prod-budget
Namespace:       som-prod
Resource         Used  Hard
--------         ----  ----
limits.cpu       0     2
limits.memory    0     2Gi
pods             0     2
requests.cpu     0     1
requests.memory  0     1Gi


Name:       prod-box-size
Namespace:  som-prod
Type        Resource  Min  Max  Default Request  Default Limit  Max Limit/Request Ratio
----        --------  ---  ---  ---------------  -------------  -----------------------
Container   cpu       -    1    50m              200m           -
Container   memory    -    1Gi  64Mi             128Mi          -
```

### 10.4 ร้านฉบับเก่าไม่ผ่านด่านของ prod

{{FIG:L18|ร้านฉบับเก่าถูกด่าน restricted ปฏิเสธ}}

```bash
kubectl apply -f som-shop-envs/k8s/som-shop-v002.yaml -n som-prod
kubectl apply -f som-shop-envs/k8s/som-shop.yaml -n som-prod --dry-run=server
```

```text
Error from server (Forbidden): error when creating "som-shop-envs/k8s/som-shop-v002.yaml": pods "som-shop-old" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (containers "db", "wait-for-db", "db-seed", "web" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (containers "db", "wait-for-db", "db-seed", "web" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or containers "db", "wait-for-db", "db-seed", "web" must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "db", "wait-for-db", "db-seed", "web" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/som-shop created (server dry run)
```

ร้านฉบับบทที่ 2 ผิดกฎทั้ง 4 ข้อในทั้ง 4 container ส่วนฉบับใหม่ผ่านทุกด่าน (`--dry-run=server` ตรวจจริงที่ API server แต่ยังไม่สร้าง)

### 10.5 เปิดร้าน 3 โซนจากไฟล์เดียว

```bash
for ns in som-dev som-staging som-prod; do kubectl apply -f som-shop-envs/k8s/som-shop.yaml -n $ns; done
kubectl get pods -A -l app=som-shop -o wide
for ns in som-dev som-staging som-prod; do kubectl wait --for=condition=Ready pod/som-shop -n $ns --timeout=180s; done
kubectl get pods -A -l app=som-shop -o wide
```

```text
pod/som-shop created
pod/som-shop created
pod/som-shop created
NAMESPACE     NAME       READY   STATUS     RESTARTS   AGE   IP       NODE          NOMINATED NODE   READINESS GATES
som-dev       som-shop   0/2     Init:0/3   0          0s    <none>   lab-worker    <none>           <none>
som-prod      som-shop   0/2     Init:0/3   0          0s    <none>   lab-worker2   <none>           <none>
som-staging   som-shop   0/2     Init:0/3   0          0s    <none>   lab-worker    <none>           <none>
pod/som-shop condition met
pod/som-shop condition met
pod/som-shop condition met
NAMESPACE     NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-dev       som-shop   2/2     Running   0          8s    10.244.2.10   lab-worker    <none>           <none>
som-prod      som-shop   2/2     Running   0          8s    10.244.1.12   lab-worker2   <none>           <none>
som-staging   som-shop   2/2     Running   0          8s    10.244.2.11   lab-worker    <none>           <none>
```

- Pod ชื่อ `som-shop` เหมือนกัน 3 ตัว คนละ NAMESPACE ไม่ชนกัน
- dev/staging ไม่มี Warning เลย (ไฟล์ผ่าน restricted แล้ว กระดิ่ง warn จึงเงียบ)
- `2/2` = sidecar `db` + `web` และ `Init:0/3` ตอนเริ่มคือ init 3 ตัว (`db` นับเป็น init แบบ sidecar) ร้านพร้อมในไม่กี่วินาทีเพราะ image อยู่บนเรือแล้ว
- dev และ staging อยู่เรือเดียวกัน ส่วน prod อยู่อีกลำ (ในเครื่องนักศึกษาอาจต่างได้) namespace ไม่ได้กำหนดเรือ

### 10.6 ตรวจว่าแต่ละร้านรู้ว่าตัวเองอยู่โซนไหน และรันแบบไม่ใช่ root

```bash
kubectl exec -n som-staging som-shop -c web -- printenv SHOP_NAME POD_NAMESPACE SHOP_FOOTER
for ns in som-dev som-staging som-prod; do kubectl exec -n $ns som-shop -c web -- printenv SHOP_NAME; done
kubectl exec -n som-prod som-shop -c web -- id
kubectl exec -n som-prod som-shop -c db -- id
kubectl exec -n som-prod som-shop -c db -- ls -ld /var/lib/postgresql/data /var/lib/postgresql/data/pgdata
kubectl exec -n som-prod som-shop -c db -- grep -E "^Cap(Eff|Prm|Bnd)" /proc/1/status
kubectl exec -n som-prod som-shop -c db -- pg_isready -U som -d catshop -h 127.0.0.1
kubectl exec -n som-prod som-shop -c web -- wget -qO- http://127.0.0.1:3000/api/health; echo
kubectl logs -n som-prod som-shop -c db-seed
```

```text
ร้านอาหารแมวน้องส้ม (som-staging)
som-staging
Next.js + PostgreSQL · Kubernetes LAB 004 · namespace som-staging
ร้านอาหารแมวน้องส้ม (som-dev)
ร้านอาหารแมวน้องส้ม (som-staging)
ร้านอาหารแมวน้องส้ม (som-prod)
uid=1000(node) gid=1000(node) groups=70,1000(node)
uid=70(postgres) gid=70(postgres) groups=70(postgres)
drwxrwsrwx    3 root     postgres      4096 Oct  4 13:33 /var/lib/postgresql/data
drwx------   19 postgres postgres      4096 Oct  4 13:33 /var/lib/postgresql/data/pgdata
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	0000000000000000
127.0.0.1:5432 - accepting connections
{"ok":true,"db":"up"}
connected to database
tables ready: products, orders
seeded 6 products (new: 6)
```

- `SHOP_NAME` ต่างกันตาม namespace ทั้งที่ใช้ไฟล์เดียว
- `web` รันเป็น uid 1000 (`groups=70` มาจาก `fsGroup`) และ `db` เป็น uid 70 ไม่มี root
- โฟลเดอร์ข้อมูลเป็นของกลุ่ม `postgres` (`fsGroup: 70`) postgres จึงเขียนได้ และ capability ทั้งหมดเป็น 0 (`drop: ["ALL"]`) แต่ฐานข้อมูลยังทำงานปกติ

### 10.7 งบของ prod: สาขาที่ 2 และ 3

{{FIG:L19|สาขาที่ 3 ชนงบของ som-prod}}

```bash
kubectl describe quota prod-budget -n som-prod
sed 's/name: som-shop$/name: som-shop-2/' som-shop-envs/k8s/som-shop.yaml | kubectl apply -n som-prod -f -
kubectl describe quota prod-budget -n som-prod
sed 's/name: som-shop$/name: som-shop-3/' som-shop-envs/k8s/som-shop.yaml | kubectl apply -n som-prod -f -
kubectl get pods -n som-prod
kubectl get quota -n som-prod
```


```text
Name:            prod-budget
Namespace:       som-prod
Resource         Used   Hard
--------         ----   ----
limits.cpu       1      2
limits.memory    1Gi    2Gi
pods             1      2
requests.cpu     200m   1
requests.memory  448Mi  1Gi
pod/som-shop-2 created
Name:            prod-budget
Namespace:       som-prod
Resource         Used   Hard
--------         ----   ----
limits.cpu       2      2
limits.memory    2Gi    2Gi
pods             2      2
requests.cpu     400m   1
requests.memory  896Mi  1Gi
Error from server (Forbidden): error when creating "STDIN": pods "som-shop-3" is forbidden: exceeded quota: prod-budget, requested: limits.cpu=1,limits.memory=1Gi,pods=1,requests.memory=448Mi, used: limits.cpu=2,limits.memory=2Gi,pods=2,requests.memory=896Mi, limited: limits.cpu=2,limits.memory=2Gi,pods=2,requests.memory=1Gi
NAME         READY   STATUS     RESTARTS   AGE
som-shop     2/2     Running    0          77s
som-shop-2   0/2     Init:0/3   0          0s
NAME          REQUEST                                                       LIMIT                                     AGE
prod-budget   pods: 2/2, requests.cpu: 400m/1, requests.memory: 896Mi/1Gi   limits.cpu: 2/2, limits.memory: 2Gi/2Gi   77s
```

- 1 ร้านใช้ requests **200m/448Mi** และ limits **1 CPU/1Gi** (นับแบบ effective ของ Pod ที่มี init/sidecar ดูทฤษฎีหัวข้อ 11.4)
- สาขาที่ 3 ชนงบ **4 ค่าพร้อมกัน**: `pods`, `limits.cpu`, `limits.memory` และ `requests.memory` (896Mi + 448Mi > 1Gi) ข้อความรวมทุกค่าที่เกินไว้ในบรรทัดเดียว และ `"STDIN"` หมายถึง manifest มาจากท่อ `|`

> ⚠️ **กับดักของ sed:** pattern `name: som-shop$` ต้องตรงกับบรรทัดที่ "จบ" ด้วย `som-shop` ถ้าบรรทัด `name:` มีคอมเมนต์ต่อท้าย sed จะไม่แทนค่า และ `kubectl apply` จะได้ `pod/som-shop configured` (ไปแก้ร้านเดิมเงียบ ๆ ไม่ได้สร้างสาขาใหม่) ไฟล์ของบทนี้จึงย้ายคอมเมนต์ขึ้นไปไว้บรรทัดบน ถ้าเห็นคำว่า `configured` แทน `created` ให้ตรวจไฟล์ด้วย `grep -n "name: som-shop" som-shop-envs/k8s/som-shop.yaml`

ปิดสาขาที่ 2 ก่อนทำต่อ

```bash
kubectl delete pod som-shop-2 -n som-prod
```

```text
pod "som-shop-2" deleted from som-prod namespace
```

### 10.8 (ลองเพิ่มเติม) ถ้าลืม runAsUser และ LimitRange ของ prod

ส่วนนี้ไม่บังคับ แต่ช่วยให้เข้าใจเหตุผลของการตั้งค่าใน `som-shop.yaml`

**(ก) ลบ `runAsUser: 1000` ออก** ลองใน `som-dev` (ใช้ sed เปลี่ยนชื่อ Pod และลบบรรทัด `runAsUser: 1000` ทิ้ง ไฟล์จริงไม่ถูกแก้)

```bash
sed -e 's/name: som-shop$/name: som-shop-nouid/' -e '/runAsUser: 1000/d' som-shop-envs/k8s/som-shop.yaml | kubectl apply -n som-dev -f -
sleep 20
kubectl get pod som-shop-nouid -n som-dev
kubectl get events -n som-dev --field-selector involvedObject.name=som-shop-nouid,type=Warning
kubectl delete pod som-shop-nouid -n som-dev
```

```text
pod/som-shop-nouid created
NAME             READY   STATUS                            RESTARTS   AGE
som-shop-nouid   1/2     Init:CreateContainerConfigError   0          20s
LAST SEEN   TYPE      REASON      OBJECT               MESSAGE
18s         Warning   Unhealthy   pod/som-shop-nouid   Startup probe failed: 127.0.0.1:5432 - no response
14s         Warning   Failed      pod/som-shop-nouid   Error: container has runAsNonRoot and image has non-numeric user (node), cannot verify user is non-root (pod: "som-shop-nouid_som-dev(a1ebff7e-81ad-4ab6-808d-fd9601ea25dc)", container: db-seed)
pod "som-shop-nouid" deleted from som-dev namespace
```

`db` (uid 70) เริ่มได้ แต่ `db-seed` ที่ใช้ image `USER node` (ชื่อ ไม่ใช่ตัวเลข) ถูก kubelet ปฏิเสธ Pod จึงค้าง `Init:CreateContainerConfigError` สังเกตว่า **ไม่มีคำเตือนจาก PSA** เพราะ manifest ยังตั้ง `runAsNonRoot: true` ถูกตามกฎ (ส่วน `Startup probe failed` ช่วงแรกคือ postgres ยังเริ่มไม่เสร็จ เป็นเรื่องปกติ)

**(ข) Pod debug ใน prod ที่ไม่ระบุ resources**

```bash
kubectl run debug -n som-prod --image=busybox:1.36 -- sleep 3600
```

```text
Error from server (Forbidden): pods "debug" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "debug" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "debug" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "debug" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "debug" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

ด่าน restricted ปฏิเสธก่อน ต้องส่ง securityContext ผ่าน `--overrides` (คำสั่งยาว พิมพ์บรรทัดเดียว)

```bash
kubectl run debug -n som-prod --image=busybox:1.36 --overrides='{"spec":{"terminationGracePeriodSeconds":1,"securityContext":{"runAsNonRoot":true,"runAsUser":1000,"runAsGroup":1000,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"debug","image":"busybox:1.36","args":["sleep","3600"],"securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}}}]}}'
kubectl get pod debug -n som-prod -o jsonpath="{.spec.containers[0].resources}{\"\n\"}"
kubectl get pod debug -n som-prod -o jsonpath="{.metadata.annotations.kubernetes\.io/limit-ranger}{\"\n\"}"
kubectl get quota -n som-prod
kubectl delete pod debug -n som-prod
```

```text
pod/debug created
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}
LimitRanger plugin set: cpu, memory request for container debug; cpu, memory limit for container debug
NAME          REQUEST                                                       LIMIT                                            AGE
prod-budget   pods: 2/2, requests.cpu: 250m/1, requests.memory: 512Mi/1Gi   limits.cpu: 1200m/2, limits.memory: 1152Mi/2Gi   90s
pod "debug" deleted from som-prod namespace
```

`debug` ได้ค่าจาก `prod-box-size` (requests 50m/64Mi, limits 200m/128Mi) และถูกนับเข้างบของ prod ทันที (pods 2/2) ส่วน `som-shop` ไม่ได้ annotation นี้ เพราะระบุ resources ครบเองแล้ว

### 10.9 บัตรเด็กฝึกงานของ som-dev

{{FIG:L20|intern ดูได้อย่างเดียวเฉพาะ som-dev}}

```bash
kubectl apply -f som-shop-envs/k8s/intern-rbac.yaml
for chk in 'get pods -n som-dev' 'get pods/log -n som-dev' 'delete pods -n som-dev' 'get pods -n som-prod' 'create pods -n som-dev'; do printf '%-26s %s\n' "$chk" "$(kubectl auth can-i $chk --as=system:serviceaccount:som-dev:intern)"; done
```

```text
serviceaccount/intern created
role.rbac.authorization.k8s.io/shop-viewer created
rolebinding.rbac.authorization.k8s.io/intern-shop-viewer created
get pods -n som-dev        yes
get pods/log -n som-dev    yes
delete pods -n som-dev     no
get pods -n som-prod       no
create pods -n som-dev     no
```

สร้าง context ของ intern จาก token จริง (เหมือน LAB 7) แล้วลองใช้งาน

```bash
T=$(kubectl create token intern -n som-dev --duration=1h) && kubectl config set-credentials intern --token=$T && kubectl config set-context intern@som-dev --cluster=kind-lab --user=intern --namespace=som-dev
kubectl --context intern@som-dev auth whoami
kubectl --context intern@som-dev get pods
kubectl --context intern@som-dev logs som-shop -c web --tail=5
kubectl --context intern@som-dev logs som-shop --tail=3
kubectl --context intern@som-dev delete pod som-shop
kubectl --context intern@som-dev get pods -n som-prod
kubectl --context intern@som-dev port-forward pod/som-shop 3009:3000
kubectl config current-context
```

```text
User "intern" set.
Context "intern@som-dev" created.
ATTRIBUTE                                           VALUE
Username                                            system:serviceaccount:som-dev:intern
UID                                                 e23bf9f9-b091-46c7-a304-5dd9bec6db55
Groups                                              [system:serviceaccounts system:serviceaccounts:som-dev system:authenticated]
Extra: authentication.kubernetes.io/credential-id   [JTI=38a0afcf-...]
NAME       READY   STATUS    RESTARTS   AGE
som-shop   2/2     Running   0          101s
▲ Next.js 16.3.8
- Local:         http://localhost:3000
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
✓ Running next.config took 1.0ms
Defaulted container "web" out of: web, db (init), wait-for-db (init), db-seed (init)
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
✓ Running next.config took 1.0ms
Error from server (Forbidden): pods "som-shop" is forbidden: User "system:serviceaccount:som-dev:intern" cannot delete resource "pods" in API group "" in the namespace "som-dev"
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:som-dev:intern" cannot list resource "pods" in API group "" in the namespace "som-prod"
error: error upgrading connection: unable to upgrade connection: pods "som-shop" is forbidden: User "system:serviceaccount:som-dev:intern" cannot create resource "pods/portforward" in API group "" in the namespace "som-dev"
kind-lab
```

intern ดู Pod และ log ของร้าน dev ได้ แต่ลบไม่ได้ ดู prod ไม่ได้ และ **เปิดหน้าร้านด้วย port-forward ไม่ได้** (ต้องการ `create` บน `pods/portforward`) context ปัจจุบันยังเป็น `kind-lab` (admin) ขั้นต่อไปจึงใช้ admin เปิด port-forward

### 10.10 เปิดหน้าร้าน 3 โซนใน browser

{{FIG:L21|port-forward 3 โซนผ่าน ssh -L}}

**ขั้นที่ 1:** 🐧 **SSH session หลักของ k8s-lab** เปิด port-forward ทั้ง 3 โซนไว้เบื้องหลัง (โซนละ port: dev 3001, staging 3002, prod 3003) เก็บข้อความไว้ในไฟล์ log

```bash
kubectl port-forward -n som-dev     pod/som-shop 3001:3000 > /tmp/pf-3001.log 2>&1 &
kubectl port-forward -n som-staging pod/som-shop 3002:3000 > /tmp/pf-3002.log 2>&1 &
kubectl port-forward -n som-prod    pod/som-shop 3003:3000 > /tmp/pf-3003.log 2>&1 &
sleep 2; cat /tmp/pf-300*.log
for p in 3001 3002 3003; do echo "== $p: $(curl -s localhost:$p | grep -o "<h1>[^<]*</h1>")"; done
```

```text
Forwarding from 127.0.0.1:3001 -> 3000
Forwarding from 127.0.0.1:3002 -> 3000
Forwarding from 127.0.0.1:3003 -> 3000
== 3001: <h1>ร้านอาหารแมวน้องส้ม (som-dev)</h1>
== 3002: <h1>ร้านอาหารแมวน้องส้ม (som-staging)</h1>
== 3003: <h1>ร้านอาหารแมวน้องส้ม (som-prod)</h1>
```

(ในเครื่องที่รองรับ IPv6 อาจมีบรรทัด `Forwarding from [::1]:...` เพิ่ม ใช้ได้เหมือนกัน)

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ ต่อท่อ SSH 3 ท่อในคำสั่งเดียว (ถ้ามีหน้าต่าง `ssh -L` จากบทก่อนค้างอยู่ ให้ `exit` ก่อน) แล้วเปิดหน้าต่างนี้ทิ้งไว้

```bash
ssh -p 2223 -L 3001:localhost:3001 -L 3002:localhost:3002 -L 3003:localhost:3003 root@localhost
```

**ขั้นที่ 3:** 🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:3001**, **http://localhost:3002** และ **http://localhost:3003** คนละแท็บ แล้วลองกดสั่งซื้อในแต่ละโซนไม่เท่ากัน (เช่น dev 1 ครั้ง, staging 2 ครั้ง, prod 3 ครั้ง) แล้วรีเฟรชทุกแท็บ

หน้าเว็บทั้ง 3 โซน **สีและหน้าตาเหมือนกัน** (เป็น image เดียวกัน) ต่างกันที่ชื่อร้าน `(som-dev)`/`(som-staging)`/`(som-prod)` ข้อความเล็ก `⚓ ท่าเรือ Kubernetes · โซน som-...` ข้อความท้ายหน้า `namespace som-...` และตัวเลขออเดอร์ ส่วนป้าย `เสิร์ฟโดย Pod: som-shop` เหมือนกันทุกโซน เพราะชื่อ Pod เหมือนกัน

{{SS:20261004_2050_lab10ns_01-som-dev.png|ภาพหน้าจอจริง โซน som-dev|ภาพหน้าจอจริงจากการทดลอง: http://localhost:3001 หัวเว็บ "ร้านอาหารแมวน้องส้ม (som-dev)" ข้อความเล็ก "โซน som-dev" ออเดอร์ทั้งหมด 1 และท้ายหน้า "Kubernetes LAB 004 · namespace som-dev"}}

{{SS:20261004_2050_lab10ns_02-som-staging.png|ภาพหน้าจอจริง โซน som-staging|ภาพหน้าจอจริงจากการทดลอง: http://localhost:3002 ร้าน som-staging ออเดอร์ทั้งหมด 2 ไม่เกี่ยวกับออเดอร์ของ dev เพราะแต่ละโซนมีฐานข้อมูลใน Pod ของตัวเอง}}

{{SS:20261004_2050_lab10ns_03-som-prod.png|ภาพหน้าจอจริง โซน som-prod|ภาพหน้าจอจริงจากการทดลอง: http://localhost:3003 ร้าน som-prod (ร้านจริง) ออเดอร์ทั้งหมด 3 เปิดจาก manifest ไฟล์เดียวกับอีกสองโซน}}

**(ทางเลือก) สั่งซื้อด้วย curl** 🐧 ใน k8s-lab

```bash
curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
```

ผลจริงหลังสั่งซื้อที่ dev 1 ออเดอร์: dev มีออเดอร์ 1 และสินค้า id 1 เหลือ 19 ชิ้น ส่วน staging และ prod ยังเป็น 0 ออเดอร์และเหลือ 20 ชิ้น (ตรวจเองได้ด้วย `curl -s localhost:3002/api/orders` และ `curl -s localhost:3002/api/products`)

### 10.11 ลบโซน dev ทั้งก้อน

{{FIG:L22|ลบ som-dev แล้ว staging และ prod ยังเปิดอยู่}}

🐧 **SSH session หลักของ k8s-lab** (เปิดแท็บ browser ทั้ง 3 ค้างไว้)

```bash
time kubectl delete ns som-dev
kubectl get pods -A -l app=som-shop
kubectl get sa intern -n som-dev
kubectl get role,rolebinding -n som-dev
kubectl --context intern@som-dev get pods
kubectl --context intern@som-dev auth whoami
for p in 3001 3002 3003; do echo "== $p: $(curl -s -m 3 localhost:$p | grep -o "<h1>[^<]*</h1>") (curl exit $?)"; done
```

```text
namespace "som-dev" deleted

real	0m10.266s
NAMESPACE     NAME       READY   STATUS    RESTARTS   AGE
som-prod      som-shop   2/2     Running   0          2m30s
som-staging   som-shop   2/2     Running   0          2m30s
Error from server (NotFound): namespaces "som-dev" not found
No resources found in som-dev namespace.
error: You must be logged in to the server (Unauthorized)
error: You must be logged in to the server (Unauthorized)
== 3001:  (curl exit 1)
== 3002: <h1>ร้านอาหารแมวน้องส้ม (som-staging)</h1> (curl exit 0)
== 3003: <h1>ร้านอาหารแมวน้องส้ม (som-prod)</h1> (curl exit 0)
```

- คำสั่งเดียวลบร้าน dev, ฐานข้อมูล dev, SA `intern`, Role และ RoleBinding ทั้งหมด ใช้เวลาราว 10 วินาที
- token ของ intern ใช้ไม่ได้ทันที (`Unauthorized`) เพราะ ServiceAccount ที่ token ผูกอยู่ถูกลบไปแล้ว
- `get role,rolebinding -n som-dev` ตอบ `No resources found` แต่ `get sa intern -n som-dev` ตอบ `namespaces "som-dev" not found` (คำขอดูของชิ้นเดียวตามชื่อ ระบบตรวจว่ามี namespace ก่อน ส่วนการลิสต์ตอบรายการว่าง)
- ร้าน staging และ prod ยังขายได้ตามปกติ

port-forward ของ 3001 **ไม่จบทันที** ที่ลบโซน มันจบตอนมีคนเข้าครั้งถัดไป ดูได้จาก log

```bash
tail -3 /tmp/pf-3001.log
pgrep -af "[k]ubectl port-forward -n som-dev" || echo "port-forward 3001 จบไปแล้ว"
```

```text
Handling connection for 3001
E1004 20:36:23.281489   21804 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod bbdd6f51ffc1d038082947a75864cda8efbd54f689e9c63973dc79bbb97f059b, uid : network namespace for sandbox \"bbdd6f51ffc1d038082947a75864cda8efbd54f689e9c63973dc79bbb97f059b\" is closed" localPort=3001 remotePort=3000
error: lost connection to pod
port-forward 3001 จบไปแล้ว
```

(คำว่า "network namespace" ในข้อความนี้คือกลไกของ Linux ที่แยกเครือข่ายของ container คนละเรื่องกับ Kubernetes namespace) 🌐 รีเฟรชแท็บ browser

{{SS:20261004_2051_lab10ns_04-som-dev-gone.png|ภาพหน้าจอจริง โซน som-dev หายแล้ว|ภาพหน้าจอจริงจากการทดลอง: หลัง kubectl delete ns som-dev ราว 10 วินาที แท็บ http://localhost:3001 เปิดไม่ได้ (ERR_CONNECTION_RESET) เพราะ Pod ปลายทางของ port-forward ถูกลบไปพร้อมโซน}}

{{SS:20261004_2051_lab10ns_05-som-prod-still-open.png|ภาพหน้าจอจริง som-prod ยังเปิดอยู่|ภาพหน้าจอจริงจากการทดลอง: ในเวลาเดียวกัน http://localhost:3003 ร้าน som-prod ยังเปิดได้ปกติและออเดอร์ทั้ง 3 ยังอยู่ การลบโซน dev ไม่กระทบโซนอื่น}}

ในรอบที่ถ่ายภาพหน้าจอ ผลของคำสั่งชุดเดียวกันคือ

```text
$ time kubectl delete ns som-dev
namespace "som-dev" deleted

real	0m10.226s
$ kubectl get pods -A -l app=som-shop -o wide
NAMESPACE     NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-prod      som-shop   2/2     Running   0          13m   10.244.1.16   lab-worker2   <none>           <none>
som-staging   som-shop   2/2     Running   0          13m   10.244.2.13   lab-worker    <none>           <none>
$ kubectl --context intern@som-dev get pods
error: You must be logged in to the server (Unauthorized)
```

### สิ่งที่เห็นใน LAB 10

- manifest **ไฟล์เดียว** ที่ไม่มี `metadata.namespace` เปิดร้านได้ 3 โซนด้วย `-n` Pod ชื่อ `som-shop` เหมือนกันไม่ชนกัน
- Downward API `metadata.namespace` ทำให้หน้าร้านแต่ละโซนบอกชื่อโซนของตัวเอง
- `som-prod` มีชุดป้องกันครบ: ร้านฉบับเก่าถูก PSA restricted ปฏิเสธ สาขาที่ 3 ชนงบ quota และ Pod ที่ไม่ระบุขนาดได้ค่าจาก LimitRange
- ทำ Pod ที่มี postgres + Next.js ให้ผ่าน restricted ได้ด้วย uid/gid ตัวเลข, `fsGroup`, drop ALL, no privilege escalation และ seccomp RuntimeDefault
- intern ดูได้อย่างเดียวและเฉพาะ `som-dev` และ token ใช้ไม่ได้ทันทีเมื่อโซนถูกลบ
- ลบโซน dev ทั้งก้อนในคำสั่งเดียวราว 10 วินาที staging และ prod ไม่กระทบ

### 10.12 เก็บกวาด LAB 10

🐧 **ใน SSH session ของ k8s-lab**

```bash
pkill -f "[k]ubectl port-forward"; sleep 1; pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
time kubectl delete ns som-staging som-prod
kubectl config delete-context intern@som-dev; kubectl config delete-user intern; kubectl config get-contexts
unset T
kubectl get ns; kubectl get pods -A -l app=som-shop
```

```text
ไม่มี port-forward ค้าง
namespace "som-staging" deleted
namespace "som-prod" deleted

real	0m10.474s
deleted context intern@som-dev from /root/.kube/config
deleted user intern from /root/.kube/config
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   default
NAME                 STATUS   AGE
default              Active   9m6s
kube-node-lease      Active   9m6s
kube-public          Active   9m6s
kube-system          Active   9m6s
local-path-storage   Active   9m2s
No resources found
```

pattern `"[k]ubectl port-forward"` (มีวงเล็บเหลี่ยม) ทำให้ `pkill`/`pgrep` ไม่ไปจับ command line ของ shell ตัวเองที่มีข้อความเดียวกัน จากนั้น 🖥️ ปิดหน้าต่าง `ssh -L` บนเครื่องนักศึกษาด้วย `exit`

image `som-shop-web:1.1` และ `postgres:17.11-alpine` ยังอยู่บนเรือ ใช้ต่อในบทถัดไปได้

{{FIG:L23|สรุป LAB บทที่ 4}}

### คำถามท้าย LAB 10

1. ทำไม `som-shop.yaml` จึงไม่ใส่ `metadata.namespace` แต่ `prod-guardrails.yaml` และ `intern-rbac.yaml` ใส่ ถ้าสลับกันจะเกิดปัญหาอะไร
2. อธิบายว่า `SHOP_NAME` ของแต่ละโซนได้ค่า `ร้านอาหารแมวน้องส้ม (som-...)` มาอย่างไร และทำไม `POD_NAMESPACE` ต้องประกาศก่อน `SHOP_NAME`
3. คำนวณให้ดูว่าทำไมร้าน 1 Pod จึงใช้งบ requests 200m/448Mi ทั้งที่ผลรวม requests ของทุก container คือ 260m/528Mi และทำไมสาขาที่ 3 จึงชน `requests.memory` แต่ไม่ชน `requests.cpu`
4. ร้านฉบับบทที่ 2 ถูกปฏิเสธใน `som-prod` แต่ถ้า apply เข้า `som-dev` จะเกิดอะไรขึ้น (ทำนายจาก label ของ `som-dev` แล้วลองดูได้) ในงานจริงการตั้ง dev เป็น `warn` และ prod เป็น `enforce` มีข้อดีข้อเสียอย่างไร
5. หลังลบ `som-dev` ทำไม `kubectl --context intern@som-dev get pods` จึงได้ `Unauthorized` (ไม่ใช่ `Forbidden`) และสองคำนี้ต่างกันอย่างไร

> **🏆 ท้าทาย:** เขียน NetworkPolicy สำหรับ `som-prod` ที่ให้ Pod ใน `som-prod` รับการเชื่อมต่อเข้าจาก Pod ใน `som-prod` เท่านั้น (แบบ LAB 4) แล้วเปิดร้าน prod ใหม่ ทดสอบว่า (1) Pod busybox ใน `som-staging` เรียก `http://<IP ของร้าน prod>:3000` ไม่ได้ (2) port-forward 3003 + browser ยังเปิดร้านได้หรือไม่ บันทึกผลและอธิบายว่าทำไม (เอกสารนี้ไม่ได้เฉลยผลข้อ 2 ให้ทดลองเอง)

> **ปูทางบทหน้า:** ร้านทั้ง 3 โซนยังเป็น Pod เดี่ยว ถ้า Pod ถูกลบก็ไม่มีใครสร้างคืน และต้องเปิดหน้าร้านด้วย port-forward ทีละ Pod บทถัดไปน้องส้มจะใช้ Deployment ดูแลจำนวนร้านให้อัตโนมัติ และใช้ Service เป็นที่อยู่คงที่ของร้านในแต่ละโซน (ชื่อ DNS แบบ `<service>.<namespace>` ที่เห็นใน search domain ของ LAB 4) โดยใช้ namespace, quota, LimitRange, RBAC และ PSA ของบทนี้ต่อได้ทันที

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-envs/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 004_kubernetes_namespace k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/004_kubernetes_namespace/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (connection refused) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ ถ้าจะทำ LAB 10 ต้อง build/`kind load` image ใหม่ |
| `Error from server (NotFound): namespaces "blue" not found` | ข้าม LAB ที่สร้าง namespace นั้น หรือเก็บกวาดไปแล้ว | สร้างใหม่ตาม LAB ก่อนหน้า (ดูบรรทัด "ต้องมีจาก LAB ..." ในแต่ละ LAB) |
| `kubectl get pods` เห็นของแปลก ๆ หรือไม่เห็น Pod ที่เพิ่งสร้าง, Pod ใหม่ไปโผล่ผิดโซน | ลืมคืน namespace ของ context หลัง LAB 2 | `kubectl config get-contexts` ดูคอลัมน์ NAMESPACE แล้ว `kubectl config set-context --current --namespace=default` |
| `error: the namespace from the provided object "..." does not match the namespace "..."` | ไฟล์มี `metadata.namespace` แต่สั่ง `-n` คนละค่า | ตัด `-n` ออก หรือใส่ `-n` ให้ตรงกับไฟล์ |
| `error: a resource cannot be retrieved by name across all namespaces` | ใช้ `kubectl get pod <ชื่อ> -A` | ใช้ `kubectl get pods -A --field-selector metadata.name=<ชื่อ>` |
| NetworkPolicy สร้างได้แต่ไม่มีผล | คลัสเตอร์อื่นที่ network plugin ไม่รองรับ (kind v0.33 รองรับ) หรือ `podSelector`/label ไม่ตรง | ตรวจ `kubectl describe netpol -n <ns>` และ `kubectl get pods --show-labels -n <ns>` |
| `wget: download timed out` ทั้งที่ยังไม่ได้ apply policy | ใช้ IP เก่า (Pod ถูกสร้างใหม่ได้ IP ใหม่) | อ่าน IP ใหม่ด้วย `kubectl get pod web -n team-a -o jsonpath='{.status.podIP}'` |
| `failed quota: ... must specify ...` | namespace มี quota ของ compute แต่ Pod ไม่ระบุ resources | ใส่ `resources` ให้ครบทุก container หรือเพิ่ม LimitRange (LAB 6) |
| `exceeded quota: ...` | ใช้งบเต็ม | ลบ Pod ที่ไม่ใช้ แล้วดู `kubectl describe quota -n <ns>` |
| `--token` แล้วยังทำได้ทุกอย่าง / `auth whoami` ยังเป็น `kubernetes-admin` | kubeconfig ของ kind ใช้ client certificate ซึ่งถูกใช้ก่อน token | สร้าง user + context ใหม่ที่มีแต่ token (LAB 7 ขั้นที่ 5) |
| `error: You must be logged in to the server (Unauthorized)` | token หมดอายุ หรือ ServiceAccount/namespace ถูกลบแล้ว | ขอ token ใหม่ด้วย `kubectl create token ...` แล้ว `set-credentials` ใหม่ (ต้องมี SA อยู่) |
| `error: context "intern@lab" does not exist` / kubectl ใช้ context ผิด | ลบ context ไปแล้ว หรือพิมพ์ชื่อผิด | `kubectl config get-contexts` และ `kubectl config use-context kind-lab` |
| Pod ไม่ผ่านด่าน `violates PodSecurity "restricted:latest"` | ขาด securityContext | เพิ่มตามตารางในทฤษฎีหัวข้อ 14.4 |
| `Init:CreateContainerConfigError` + `image has non-numeric user (node)` | `runAsNonRoot: true` แต่ไม่ระบุ `runAsUser` ตัวเลข | ใส่ `runAsUser: 1000` (node) หรือ `70` (postgres) |
| namespace ค้าง `Terminating` นาน | Pod ที่ grace period ยาว หรือ object ที่มี finalizer ค้าง | รอ grace period (`peek` 30 วินาที) ถ้าเกินหลายนาที ดู `kubectl get ns <ns> -o jsonpath='{.status.conditions}'` (ทฤษฎีหัวข้อ 8.3) |
| `unable to create new content in namespace ... because it is being terminated` | กำลังลบ namespace นั้นอยู่ | รอให้หายแล้วสร้าง namespace ใหม่ |
| `som-shop` ค้าง `Init:ErrImagePull` / `ImagePullBackOff` | ไม่มี image บน Node (เช่น สร้างคลัสเตอร์ใหม่แต่ยังไม่ `kind load`) | ทำขั้น 10.2 แล้ว `kubectl delete pod som-shop -n <ns>` และ apply ใหม่ |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` |
| หน้าร้านไม่แสดงชื่อโซนที่หัวและท้ายหน้า (ท้ายหน้าเขียน `Kubernetes LAB 002`) | ใช้ image `som-shop-web:1.0` ของบทก่อน | build และ load `som-shop-web:1.1` ตามขั้น 10.2 |
| `sed ... som-shop-2` แล้วได้ `pod/som-shop configured` แทน `created` | บรรทัด `name: som-shop` มีคอมเมนต์ต่อท้าย sed จึงไม่แทนค่า | ตรวจ `grep -n "name: som-shop" som-shop-envs/k8s/som-shop.yaml` ย้ายคอมเมนต์ขึ้นบรรทัดบน (ไฟล์ของบทนี้แก้แล้ว) |
| `kubectl port-forward` แจ้ง `address already in use` | port-forward ตัวเก่ายังค้าง | `pgrep -af "[k]ubectl port-forward"` แล้ว `pkill -f "[k]ubectl port-forward"` |
| browser เปิด `localhost:3001`–`3003` ไม่ได้ (`ERR_CONNECTION_RESET`/refused) | หน้าต่าง `ssh -L` ถูกปิด หรือ port-forward หลุดเพราะ Pod/โซนถูกลบ | ดู `cat /tmp/pf-3001.log` ถ้ามี `lost connection to pod` ให้เปิด port-forward ใหม่หลังมี Pod ใหม่ |
| `ssh -L` แจ้งว่า bind port ไม่ได้ | port 3001–3003 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ | เปลี่ยนเลขซ้ายของ `-L` เช่น `-L 13001:localhost:3001` แล้วเปิด `http://localhost:13001` |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ **ห้ามมี token ของ ServiceAccount ในภาพ**

- [ ] **LAB 0** `kubectl get ns --show-labels` (5 namespace) และ `kubectl get pods -A -o wide`
- [ ] **LAB 1** `kubectl get pods -A -l app=snack -o wide` (snack 3 ตัว) และ error `does not match the namespace`
- [ ] **LAB 2** `kubectl config get-contexts` ตอน NAMESPACE เป็น `blue` และหลังคืนค่าเป็น `default`
- [ ] **LAB 3** `kubectl get nodes -n blue` และจำนวน 34/37 ของ api-resources
- [ ] **LAB 4** Pod ของ 2 โซนบนเรือลำเดียวกัน, `resolv.conf`, `download timed out` หลัง `allow-same-namespace` และ `team-b เข้าได้` หลัง `allow-from-team-b`
- [ ] **LAB 5** `must specify ...` และ `exceeded quota ... pods=3` พร้อม `describe quota`
- [ ] **LAB 6** resources ที่ LimitRange เติมให้ `no-request` และ error `maximum cpu usage per Container`
- [ ] **LAB 7** ผล can-i ของ intern, ผล `--token ... auth whoami` (ยังเป็น admin) และ `--context intern@lab auth whoami`
- [ ] **LAB 8** Warning ของ root-nginx, Forbidden ของ privileged และ `uid=1000 gid=1000` ของ restricted-ok
- [ ] **LAB 9** `doomed Terminating` + `unable to create new content` และผล `--dry-run=server` ของ namespace ระบบ
- [ ] **LAB 10** (1) `kubectl get pods -A -l app=som-shop -o wide` 3 โซน (2) Forbidden ของ `som-shop-v002.yaml` (3) `exceeded quota` ของ `som-shop-3` (4) ตาราง can-i ของ intern (5) browser 3 แท็บแสดงชื่อโซนและออเดอร์ต่างกัน (6) หลังลบ `som-dev`: แท็บ 3001 เปิดไม่ได้ แต่ 3003 ยังเปิดได้
- [ ] ท้ายสุด `kubectl get ns` เหลือ 5 namespace ตั้งต้น และ `kubectl config get-contexts` มีแค่ `kind-lab` ที่ NAMESPACE เป็น `default`

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| namespace `blue`, `green` | 1–4 | `kubectl get ns` | `kubectl delete ns blue green` |
| namespace `kube-mine` | 1 | `kubectl get ns kube-mine` | `kubectl delete ns kube-mine` |
| Pod `snack` ใน default | 1 | `kubectl get pods` | `kubectl delete pod snack` |
| namespace ของ context ไม่ใช่ default | 2 | `kubectl config get-contexts` | `kubectl config set-context --current --namespace=default` |
| namespace `team-a`, `team-b` | 4, 7 | `kubectl get ns` | `kubectl delete ns team-a team-b` |
| namespace `budget` | 5, 6 | `kubectl get ns budget` | `kubectl delete ns budget` |
| context/user `intern@lab`, `intern@som-dev`, `intern` | 7, 10 | `kubectl config get-contexts` และ `kubectl config get-users` | `kubectl config delete-context <ชื่อ>` และ `kubectl config delete-user intern` |
| namespace `secure` | 8 | `kubectl get ns secure` | `kubectl delete ns secure` |
| namespace `doomed` | 9 | `kubectl get ns doomed` | `kubectl delete ns doomed` |
| namespace `som-dev`, `som-staging`, `som-prod` | 10 | `kubectl get ns -l team=som` | `kubectl delete ns som-dev som-staging som-prod` |
| port-forward ค้าง | 10 | `pgrep -af "[k]ubectl port-forward"` | `pkill -f "[k]ubectl port-forward"` |
| ตัวแปร token `T` ใน shell | 7, 10 | `echo ${#T}` (ความยาว ถ้าไม่ใช่ 0 แปลว่ายังมี) | `unset T` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get ns
kubectl get pods
kubectl config get-contexts
pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
```

ผลที่ถูกต้อง: เหลือ namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), ไม่มี Pod ใน `default` (`No resources found in default namespace.`), มี context เดียวคือ `kind-lab` ที่ NAMESPACE เป็น `default` และไม่มี port-forward ค้าง

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ `kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพเป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก
