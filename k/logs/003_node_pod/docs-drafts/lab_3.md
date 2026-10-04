
## LAB 10: LAB สุดท้าย: ร้านน้องส้มหลายสาขาบนกองเรือ

<p align="center" id="fig-14">
  <img src="images/14-lab10-opening-branches.png" alt="รูปที่ 14 LAB10 ภาพเปิด 2 สาขาบนเรือคนละลำ" width="900"><br>
  <em><b>รูปที่ 14</b> LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้ม 2 สาขา som-shop-a และ som-shop-b บนเรือคนละลำ</em>
</p>

**เป้าหมาย:** เปิดร้านอาหารแมวน้องส้ม (Next.js + PostgreSQL จากบทที่ 2) **2 สาขาเป็น Pod เดี่ยว 2 ตัวบนเรือคนละลำ** โดยรวมทุกอย่างที่เรียนในบทนี้

- **node label + required node affinity**: เปิดสาขาได้เฉพาะเรือที่ติดธง `shop=open`
- **required pod anti-affinity**: สาขาของร้านห้ามอยู่เรือลำเดียวกัน
- **Downward API + `$(NODE_NAME)`**: ชื่อร้านบอกเองว่าอยู่เรือลำไหน
- **toleration `tolerationSeconds: 60`**: ถ้าเรือหายในหมอกเกิน 60 วินาที ยอมให้ถูกไล่
- **drain** เรือของสาขาหนึ่ง และ **เรือล่ม** ของอีกสาขา แล้วดูว่าร้านเป็นอย่างไร

**ไฟล์:** `som-shop-branches/` (อยู่ใน k8s-lab ที่ `/workspace/003_kubernetes_node_pod/02_LAB/som-shop-branches/` ตั้งแต่ `docker cp` ใน LAB 0)

| path | เนื้อหา |
|---|---|
| `som-shop-branches/app/` | แอป Next.js + `Dockerfile` + `scripts/seed.mjs` **สำเนาจากบทที่ 2 ไม่ได้แก้โค้ด** |
| `som-shop-branches/k8s/som-shop-a.yaml` | Pod สาขา a |
| `som-shop-branches/k8s/som-shop-b.yaml` | Pod สาขา b (ต่างจาก a แค่ชื่อและ label `branch: b`) |
| `som-shop-branches/k8s/som-shop-c.yaml` | Pod สาขา c ไว้ทดลองว่า "เรือเต็ม" |

> **หมายเหตุเรื่องหน้าเว็บ:** เพราะใช้แอปเดิมจากบทที่ 2 ทั้งหมด footer ของหน้าเว็บจึงยังเขียน `Next.js + PostgreSQL · Kubernetes LAB 002` และข้อความบนหัวเว็บยังเป็น `⚓ ท่าเรือ Kubernetes · Pod เดียวครบทั้งร้าน` ไม่ใช่ข้อผิดพลาด ส่วนชื่อร้านมาจาก env `SHOP_NAME` ที่เราตั้งใหม่

### 10.1 สถาปัตยกรรมและโครง manifest

เป้าหมายที่ต้องการ (scheduler เป็นคนเลือกว่าสาขาไหนได้เรือลำไหน เรากำหนดแค่ "คนละลำ")

```text
lab-control-plane  (taint control-plane:NoSchedule, ไม่มีธง shop)  ← ไม่มีสาขา
lab-worker   [shop=open]  └─ Pod som-shop-a  "ร้านอาหารแมวน้องส้ม สาขา lab-worker"    ← port-forward 3001
lab-worker2  [shop=open]  └─ Pod som-shop-b  "ร้านอาหารแมวน้องส้ม สาขา lab-worker2"   ← port-forward 3002
(สาขา a อาจได้ lab-worker2 และ b ได้ lab-worker ก็ได้ ให้ดูของจริงจาก kubectl get pod -o wide)
```

แต่ละสาขาเป็น Pod all-in-one แบบเดียวกับ `som-shop` ในบทที่ 2: `db` (native sidecar) → `wait-for-db` → `db-seed` → `web` และ **มีฐานข้อมูลใน emptyDir ของตัวเอง** ออเดอร์ของสาขา a จึงไม่เห็นที่สาขา b (เป็นข้อจำกัดที่ตั้งใจให้เห็นในบทนี้ บทหน้าจะใช้ฐานข้อมูลกลาง)

<p align="center" id="fig-15">
  <img src="images/15-lab10-manifest-anatomy.png" alt="รูปที่ 15 โครง manifest ของสาขา" width="900"><br>
  <em><b>รูปที่ 15</b> โครง Pod สาขา: nodeAffinity เลือกเรือที่มีธง shop=open, podAntiAffinity ห้ามสาขาอยู่เรือเดียวกัน และ Downward API ใส่ NODE_NAME ในชื่อร้าน</em>
</p>

ส่วนที่เพิ่มจากบทที่ 2 ใน `som-shop-branches/k8s/som-shop-a.yaml` (ตัดส่วน init container, probes และ resources ที่เหมือนเดิมออก ดูไฟล์เต็มด้วย `cat`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: som-shop-a
  labels:
    app: som-shop
    part: branch                 # ใช้ในกฎ podAntiAffinity ด้านล่าง
    branch: a
spec:
  affinity:
    nodeAffinity:                # ต้องเปิดบนเรือที่ติดธง shop=open เท่านั้น
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: shop
                operator: In
                values: ["open"]
    podAntiAffinity:             # สาขาของ som-shop ห้ามอยู่เรือลำเดียวกัน (1 เรือ 1 สาขา)
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels:
              app: som-shop
              part: branch
          topologyKey: kubernetes.io/hostname
  tolerations:                   # เรือหายในหมอกเกิน 60 วิ → ยอมให้ถูกไล่ (ค่าเริ่มต้น 300 วิ นานไปสำหรับ LAB)
    - key: node.kubernetes.io/unreachable
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 60
    - key: node.kubernetes.io/not-ready
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 60
  volumes:
    - name: db-data              # ฐานข้อมูลของสาขานี้เท่านั้น (แต่ละสาขามี emptyDir ของตัวเอง) หายเมื่อ Pod ถูกลบ
      emptyDir: {}
  containers:
    - name: web
      image: som-shop-web:1.0
      imagePullPolicy: IfNotPresent
      env:
        - name: NODE_NAME          # Downward API: ชื่อเรือที่ Pod นี้ถูกวาง (ต้องประกาศก่อน SHOP_NAME)
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: SHOP_NAME          # $(NODE_NAME) ถูกแทนค่าตอนสร้าง container → "สาขา lab-worker" หรือ "สาขา lab-worker2"
          value: "ร้านอาหารแมวน้องส้ม สาขา $(NODE_NAME)"
        - name: DATABASE_URL
          value: postgres://som:meow1234@localhost:5432/catshop
        - name: PORT
          value: "3000"
        - name: HOSTNAME
          value: "0.0.0.0"
      ports:
        - containerPort: 3000
```

อธิบายทีละส่วน

| ส่วน | ทำให้เกิดอะไร |
|---|---|
| `nodeAffinity` required `shop In ["open"]` | สาขาเปิดได้เฉพาะเรือที่เราติดธง ถ้ายังไม่ติดธง → Pending |
| `podAntiAffinity` required, `labelSelector: app=som-shop, part=branch`, `topologyKey: kubernetes.io/hostname` | ทุกสาขา (ที่มี label ทั้งสอง) ห้ามอยู่เรือเดียวกัน เรือ `shop=open` มี 2 ลำ จึงเปิดได้สูงสุด 2 สาขา |
| `tolerations` 60 วินาที | เขียนทับค่าเริ่มต้น 300 วินาที ให้ LAB ไม่ต้องรอนาน |
| env `NODE_NAME` จาก `spec.nodeName` + `SHOP_NAME` ที่มี `$(NODE_NAME)` | kubelet แทนค่าตอนสร้าง container หน้าเว็บอ่าน `SHOP_NAME` ตอน runtime จึงแสดงชื่อสาขาตามเรือ (และชื่อแท็บของ browser ก็เปลี่ยนตามด้วย) |
| `som-shop-b.yaml`, `som-shop-c.yaml` | ก๊อปปี้ไฟล์เดิมแล้วเปลี่ยนแค่ชื่อและ `branch` เพราะยังไม่มีตัวช่วยสร้าง Pod หลายตัวจากแม่แบบเดียว |

### 10.2 เตรียม image ให้ทุก Node

<p align="center" id="fig-16">
  <img src="images/16-lab10-images-ready.png" alt="รูปที่ 16 เตรียม image ให้ทุก Node" width="900"><br>
  <em><b>รูปที่ 16</b> เตรียม image: build som-shop-web:1.0 จากบทที่ 2 แล้ว kind load ไปทุก node ส่วน postgres ใช้ docker save --platform แล้ว kind load image-archive</em>
</p>

**ตรวจก่อนว่าต้องทำไหม** ถ้าใช้คลัสเตอร์ต่อจากบทที่ 2 (ไม่ได้ `k8s-up` ใหม่) image อาจมีบนทั้งสอง worker แล้ว ข้ามขั้นนี้ได้

```bash
docker image ls som-shop-web
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

ถ้าทั้ง `lab-worker` และ `lab-worker2` มีทั้ง `som-shop-web 1.0` และ `postgres 17.11-alpine` ให้ข้ามไป 10.3 ถ้าไม่มี (เช่น สร้างคลัสเตอร์ใหม่ใน LAB 0) ทำต่อดังนี้

**ขั้นที่ 1: build image ของเว็บ** (ประมาณ 30 วินาที ถ้าเคย build ในบทที่ 2 จะเร็วขึ้นเพราะมี cache)

```bash
docker build -t som-shop-web:1.0 som-shop-branches/app 2>&1 | tail -5
```

```text
#16 exporting manifest list sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807 0.0s done
#16 naming to docker.io/library/som-shop-web:1.0 done
#16 unpacking to docker.io/library/som-shop-web:1.0
#16 unpacking to docker.io/library/som-shop-web:1.0 1.3s done
#16 DONE 2.4s
```

**ขั้นที่ 2: นำเข้าทุก Node**

```bash
time kind load docker-image som-shop-web:1.0 --name lab
```

```text
Image: "som-shop-web:1.0" with ID "sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.0" with ID "sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807" not yet present on node "lab-worker2", loading...
Image: "som-shop-web:1.0" with ID "sha256:84cfc41b9bcbaef3de8c81a4cbd165dd97de32090daae1b8005f6ed70a9ab807" not yet present on node "lab-control-plane", loading...

real	0m4.863s
```

**ขั้นที่ 3: postgres** ใช้วิธีเดียวกับบทที่ 2 (`docker save --platform` แล้ว `kind load image-archive` เลี่ยงปัญหา image หลาย platform) เครื่อง ARM (เช่น Mac ชิป Apple) ให้เปลี่ยนเป็น `--platform linux/arm64`

```bash
docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
```

```text
docker.io/library/postgres:17.11-alpine
== lab-worker
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  b95826bfd89f2       76.6MB
== lab-worker2
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  b95826bfd89f2       76.6MB
```

> image ต้องอยู่บน **ทุก worker** เพราะเราไม่รู้ล่วงหน้าว่า scheduler จะวางสาขาไหนบนเรือลำไหน (`kind load` ใส่ให้ทุก Node อยู่แล้ว)

### 10.3 เปิดสาขาก่อนติดธง แล้วติดธง

**ขั้นที่ 1:** apply ทั้งสองสาขาตอนที่ยังไม่มีเรือลำไหนติดธง `shop=open`

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-a.yaml -f som-shop-branches/k8s/som-shop-b.yaml; sleep 3; kubectl get pod -l app=som-shop -o wide
kubectl describe pod som-shop-a | sed -n '/^Events/,$p'
```

```text
pod/som-shop-a created
pod/som-shop-b created
NAME         READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
som-shop-a   0/2     Pending   0          3s    <none>   <none>   <none>           <none>
som-shop-b   0/2     Pending   0          3s    <none>   <none>   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  3s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match Pod's node affinity/selector. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

**ขั้นที่ 2:** ติดธงให้ทั้งสองลำ แล้วเฝ้าดูลำดับการเริ่ม (กด Ctrl+C เมื่อทั้งคู่ `2/2 Running`)

```bash
kubectl label node lab-worker lab-worker2 shop=open; kubectl get nodes -L shop
kubectl get pod -l app=som-shop -w
```

```text
node/lab-worker labeled
node/lab-worker2 labeled
NAME                STATUS   ROLES           AGE   VERSION   SHOP
lab-control-plane   Ready    control-plane   29m   v1.37.0   
lab-worker          Ready    <none>          28m   v1.37.0   open
lab-worker2         Ready    <none>          28m   v1.37.0   open
NAME         READY   STATUS     RESTARTS   AGE
som-shop-a   0/2     Init:0/3   0          3s
som-shop-b   0/2     Init:0/3   0          3s
som-shop-a   0/2     Init:1/3   0          8s
som-shop-b   0/2     Init:1/3   0          8s
som-shop-a   1/2     Init:1/3   0          8s
som-shop-b   1/2     Init:1/3   0          8s
som-shop-a   1/2     Init:2/3   0          8s
som-shop-b   1/2     Init:2/3   0          9s
som-shop-a   1/2     PodInitializing   0          9s
som-shop-a   1/2     Running           0          9s
som-shop-b   1/2     PodInitializing   0          10s
som-shop-b   1/2     Running           0          10s
som-shop-a   2/2     Running           0          10s
som-shop-b   2/2     Running           0          11s
```

(ตัดบรรทัดที่ซ้ำกันออก ในการทดลองทั้งคู่ Ready ภายใน 8 วินาทีหลังติดธง เพราะ image อยู่บน Node แล้ว)

```bash
kubectl get pod -l app=som-shop -o wide -L branch
```

```text
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES   BRANCH
som-shop-a   2/2     Running   0          11s   10.244.1.23   lab-worker    <none>           <none>            a
som-shop-b   2/2     Running   0          11s   10.244.2.4    lab-worker2   <none>           <none>            b
```

### 10.4 ตรวจ Downward API

```bash
kubectl exec som-shop-a -c web -- printenv NODE_NAME SHOP_NAME POD_IP; kubectl exec som-shop-b -c web -- printenv NODE_NAME SHOP_NAME POD_IP
kubectl get pod -l app=som-shop -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,IP:.status.podIP
kubectl exec som-shop-a -c web -- wget -qO- http://127.0.0.1:3000/api/health; echo
```

```text
lab-worker
ร้านอาหารแมวน้องส้ม สาขา lab-worker
10.244.1.23
lab-worker2
ร้านอาหารแมวน้องส้ม สาขา lab-worker2
10.244.2.4
NAME         NODE          IP
som-shop-a   lab-worker    10.244.1.23
som-shop-b   lab-worker2   10.244.2.4
{"ok":true,"db":"up"}
```

### 10.5 ทดลองสาขาที่ 3

<p align="center" id="fig-17">
  <img src="images/17-lab10-anti-affinity-pending.png" alt="รูปที่ 17 สาขาที่ 3 Pending" width="900"><br>
  <em><b>รูปที่ 17</b> ทดลองสาขาที่ 3 som-shop-c: มีเรือติดธง shop=open แค่ 2 ลำและทั้งสองลำมีสาขาแล้ว จึง Pending</em>
</p>

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-c.yaml; sleep 3; kubectl get pod -l app=som-shop -o wide
kubectl describe pod som-shop-c | sed -n '/^Events/,$p'
```

```text
pod/som-shop-c created
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          32s   10.244.1.23   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          32s   10.244.2.4    lab-worker2   <none>           <none>
som-shop-c   0/2     Pending   0          3s    <none>        <none>        <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  4s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod anti-affinity rules. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

สังเกตว่า control-plane ถูกนับเป็น `untolerated taint(s)` (เหตุผลแรกที่ตก) ไม่ใช่ "ไม่มีธง shop" เพราะแต่ละ Node ถูกนับในเหตุผลเดียว ลบสาขา c ทิ้ง

```bash
kubectl delete -f som-shop-branches/k8s/som-shop-c.yaml; kubectl get pod -l app=som-shop
```

```text
pod "som-shop-c" deleted from default namespace
NAME         READY   STATUS    RESTARTS   AGE
som-shop-a   2/2     Running   0          33s
som-shop-b   2/2     Running   0          33s
```

### 10.6 เปิดหน้าร้าน 2 สาขาใน browser

<p align="center" id="fig-18">
  <img src="images/18-lab10-two-tunnels.png" alt="รูปที่ 18 port-forward 2 ท่อ" width="900"><br>
  <em><b>รูปที่ 18</b> เปิดหน้าร้าน 2 สาขาด้วย kubectl port-forward คนละ port (3001, 3002) และ ssh -L สองชั้นจากเครื่องนักศึกษา</em>
</p>

**ขั้นที่ 1:** 🐧 **SSH session หลักของ k8s-lab** เปิด port-forward ทั้งสองสาขาไว้เบื้องหลัง (เก็บข้อความไว้ในไฟล์ log เพื่อดูภายหลังว่าท่อหลุดเมื่อไร)

```bash
kubectl port-forward pod/som-shop-a 3001:3000 > /tmp/pf-a.log 2>&1 &
kubectl port-forward pod/som-shop-b 3002:3000 > /tmp/pf-b.log 2>&1 &
sleep 2; cat /tmp/pf-a.log /tmp/pf-b.log
curl -s localhost:3001 | grep -o "<h1>[^<]*</h1>"; curl -s localhost:3002 | grep -o "<h1>[^<]*</h1>"
```

```text
Forwarding from 127.0.0.1:3001 -> 3000
Forwarding from 127.0.0.1:3002 -> 3000
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker2</h1>
```

(ในเครื่องที่รองรับ IPv6 อาจมีบรรทัด `Forwarding from [::1]:...` เพิ่ม ใช้ได้เหมือนกัน)

**ขั้นที่ 2:** 🖥️ **บนเครื่องนักศึกษา** เปิดหน้าต่างใหม่ ต่อท่อ SSH สองท่อพร้อมกัน (ถ้ามีหน้าต่าง `ssh -L` จากบทที่ 2 ค้างอยู่ ให้ `exit` ก่อน)

```bash
ssh -p 2223 -L 3001:localhost:3001 -L 3002:localhost:3002 root@localhost
```

**ขั้นที่ 3:** 🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:3001** และ **http://localhost:3002** คนละแท็บ กดสั่งซื้อที่สาขาแรก 2 ครั้ง แล้วรีเฟรชทั้งสองแท็บ

<p align="center" id="fig-19">
  <img src="images/19-lab10-browser-branch-names.png" alt="รูปที่ 19 หน้าเว็บ 2 สาขา" width="900"><br>
  <em><b>รูปที่ 19</b> หน้าเว็บสองสาขาแสดงชื่อร้านพร้อมชื่อเรือจาก Downward API และออเดอร์ของแต่ละสาขาแยกกันเพราะฐานข้อมูลอยู่ใน Pod ของตัวเอง</em>
</p>

<p align="center" id="fig-20">
  <img src="images/screenshots/20261004_1938_lab10_01-branch-a-lab-worker.png" alt="รูปที่ 20 ภาพหน้าจอจริง สาขา lab-worker" width="700"><br>
  <em><b>รูปที่ 20</b> ภาพหน้าจอจริงจากการทดลอง: http://localhost:3001 สาขา a บนเรือ lab-worker หัวเว็บแสดง "ร้านอาหารแมวน้องส้ม สาขา lab-worker" ออเดอร์ทั้งหมด 2 และ footer เสิร์ฟโดย Pod som-shop-a</em>
</p>

<p align="center" id="fig-21">
  <img src="images/screenshots/20261004_1938_lab10_02-branch-b-lab-worker2.png" alt="รูปที่ 21 ภาพหน้าจอจริง สาขา lab-worker2" width="700"><br>
  <em><b>รูปที่ 21</b> ภาพหน้าจอจริงจากการทดลอง: http://localhost:3002 สาขา b บนเรือ lab-worker2 ออเดอร์ทั้งหมด 0 แม้สาขา a จะขายไปแล้ว เพราะแต่ละสาขามีฐานข้อมูลของตัวเอง</em>
</p>

**(ทางเลือก) สั่งซื้อด้วย curl** 🐧 ใน k8s-lab ผลจริง

```bash
curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo
curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'; echo
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
```

หลังสั่งซื้อ กล่องสถิติของสาขา a คือ `2 ออเดอร์ทั้งหมด · 2 ชิ้นที่ขายแล้ว · 6 สินค้าในร้าน` และสินค้า id 1 เหลือ 18 ชิ้น ส่วนสาขา b ยังเป็น `0 · 0 · 6` และสินค้า id 1 ยังเหลือ 20 ชิ้น

### 10.7 ซ่อมเรือของสาขา a (drain)

<p align="center" id="fig-22">
  <img src="images/20-lab10-drain-branch-closed.png" alt="รูปที่ 22 drain เรือของสาขา a" width="900"><br>
  <em><b>รูปที่ 22</b> drain เรือของสาขา a: สาขา a ปิดและหายไป สาขา b ยังขายได้ เปิด a ใหม่ระหว่าง cordon จะ Pending จนกว่า uncordon</em>
</p>

**หาเรือของสาขา a จากของจริงเสมอ** (อย่าจำตามภาพ เพราะ scheduler อาจวางสลับกัน)

```bash
NODE_A=$(kubectl get pod som-shop-a -o jsonpath={.spec.nodeName}); echo NODE_A=$NODE_A
kubectl drain $NODE_A --ignore-daemonsets
```

```text
NODE_A=lab-worker
node/lab-worker cordoned
error: unable to drain node "lab-worker" due to error: cannot delete Pods with local storage (use --delete-emptydir-data to override): default/som-shop-a, continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete Pods with local storage (use --delete-emptydir-data to override): default/som-shop-a
```

สาขามีฐานข้อมูลใน emptyDir drain จึงขอให้ยืนยันว่ายอมให้ข้อมูลหาย (และสังเกตว่า Node ถูก cordon ไปแล้วแม้ error) ใส่ให้ครบ

```bash
time kubectl drain $NODE_A --ignore-daemonsets --delete-emptydir-data --force
kubectl get pod -l app=som-shop -o wide; kubectl get nodes
```

```text
node/lab-worker already cordoned
Warning: ignoring DaemonSet-managed Pods: kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl; deleting Pods that declare no controller: default/som-shop-a
evicting pod default/som-shop-a
pod/som-shop-a evicted
node/lab-worker drained

real	0m1.059s
NAME         READY   STATUS    RESTARTS   AGE    IP           NODE          NOMINATED NODE   READINESS GATES
som-shop-b   2/2     Running   0          119s   10.244.2.4   lab-worker2   <none>           <none>
NAME                STATUS                     ROLES           AGE   VERSION
lab-control-plane   Ready                      control-plane   31m   v1.37.0
lab-worker          Ready,SchedulingDisabled   <none>          30m   v1.37.0
lab-worker2         Ready                      <none>          30m   v1.37.0
```

ดูผลต่อหน้าร้าน

```bash
curl -s -m 5 localhost:3001 >/dev/null; echo "curl 3001 exit=$?"
curl -s localhost:3002 | grep -o "<h1>[^<]*</h1>"
tail -3 /tmp/pf-a.log
```

```text
curl 3001 exit=52
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker2</h1>
Handling connection for 3001
E1004 19:24:06.053551   56187 portforward.go:549] "An error occurred forwarding" err="error forwarding port 3000 to pod ec253c7d3678b25fd2e8d10064013265a7b3ff87384fee4101b22f22294a7289, uid : network namespace for sandbox \"ec253c7d3678b25fd2e8d10064013265a7b3ff87384fee4101b22f22294a7289\" is closed" localPort=3001 remotePort=3000
error: lost connection to pod
```

🌐 แท็บ `localhost:3001` เปิดไม่ได้แล้ว ส่วนแท็บ `localhost:3002` ยังขายได้ปกติ

### 10.8 เปิดสาขา a ใหม่ระหว่างเรือยังอยู่ในอู่

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-a.yaml; sleep 3; kubectl get pod -l app=som-shop -o wide
kubectl describe pod som-shop-a | sed -n '/^Events/,$p'
```

```text
pod/som-shop-a created
NAME         READY   STATUS    RESTARTS   AGE     IP           NODE          NOMINATED NODE   READINESS GATES
som-shop-a   0/2     Pending   0          3s      <none>       <none>        <none>           <none>
som-shop-b   2/2     Running   0          2m40s   10.244.2.4   lab-worker2   <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  3s    default-scheduler  0/3 nodes are available: 1 node(s) didn't match pod anti-affinity rules, 1 node(s) had untolerated taint(s), 1 node(s) were unschedulable. preemption: 0/3 nodes are available: 1 No preemption victims found for incoming pod, 2 Preemption is not helpful for scheduling.
```

ซ่อมเสร็จ เอาเชือกออก แล้วเปิดท่อใหม่ (ท่อเก่าตายไปพร้อม Pod เดิม)

```bash
kubectl uncordon $NODE_A; kubectl wait --for=condition=Ready pod/som-shop-a --timeout=120s; kubectl get pod -l app=som-shop -o wide; kubectl get nodes
kubectl port-forward pod/som-shop-a 3001:3000 > /tmp/pf-a.log 2>&1 &
sleep 2; curl -s localhost:3001 | grep -oE "<h1>[^<]*</h1>|<span class=\"num\">[^<]*</span><span class=\"label\">ออเดอร์ทั้งหมด"
```

```text
node/lab-worker uncordoned
pod/som-shop-a condition met
NAME         READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          10s     10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          2m47s   10.244.2.4    lab-worker2   <none>           <none>
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   31m   v1.37.0
lab-worker          Ready    <none>          31m   v1.37.0
lab-worker2         Ready    <none>          31m   v1.37.0
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
<span class="num">0</span><span class="label">ออเดอร์ทั้งหมด
```

(ในการทดลอง `som-shop-a` Ready ภายใน 7 วินาทีหลัง uncordon) 🌐 รีเฟรชแท็บ `localhost:3001` จะเห็นร้านกลับมา แต่ **ออเดอร์เป็น 0** และ IP ใหม่ เพราะเป็น Pod ใหม่ที่มี emptyDir ใหม่

### 10.9 เรือของสาขา b หายในหมอก

<p align="center" id="fig-23">
  <img src="images/21-lab10-fog-branch-lost.png" alt="รูปที่ 23 เรือของสาขา b หายในหมอก" width="900"><br>
  <em><b>รูปที่ 23</b> เรือ lab-worker2 หายในหมอก (docker stop): สาขา b ถูกไล่ออกหลัง NotReady 60 วินาที สาขา a ยังขายได้ แต่ไม่มีใครเปิดสาขาใหม่ให้</em>
</p>

> ⚠️ 🐧 รันใน **SSH session ของ k8s-lab** และตรวจให้แน่ใจว่า `NODE_B` เป็น `lab-worker` หรือ `lab-worker2` เท่านั้น (ห้ามเป็น `lab-control-plane`)

```bash
NODE_B=$(kubectl get pod som-shop-b -o jsonpath={.spec.nodeName}); echo NODE_B=$NODE_B; date +%T; docker stop $NODE_B
```

```text
NODE_B=lab-worker2
19:25:15
lab-worker2
```

ทันทีหลังหยุดเรือ

```bash
curl -s -m 5 localhost:3002 >/dev/null; echo "curl 3002 exit=$?"; tail -2 /tmp/pf-b.log
curl -s -m 5 localhost:3001 | grep -o "<h1>[^<]*</h1>"
```

```text
curl 3002 exit=7
Handling connection for 3002
error: lost connection to pod
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
```

รอ ~45–50 วินาทีแล้วดูสถานะ และลองสั่งซื้อที่สาขา a ระหว่างเรือ b ล่ม

```bash
kubectl get nodes; kubectl get pod -l app=som-shop -o wide
curl -s -X POST localhost:3001/api/orders -H "Content-Type: application/json" -d '{"product_id":2,"qty":2}'; echo
```

```text
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   33m   v1.37.0
lab-worker          Ready      <none>          33m   v1.37.0
lab-worker2         NotReady   <none>          33m   v1.37.0
NAME         READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          95s     10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          4m12s   10.244.2.4    lab-worker2   <none>           <none>
{"ok":true,"order_id":1,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":13}}
```

ภาพหน้าจอจริงช่วงนี้ (ถ่ายจากการทดลองอีกรอบหนึ่งซึ่งสาขา a มี 2 ออเดอร์อยู่ก่อน แล้ว `docker stop lab-worker2` ซึ่ง Node เป็น NotReady หลัง 51 วินาที)

<p align="center" id="fig-24">
  <img src="images/screenshots/20261004_1940_lab10_03-branch-a-still-selling-while-worker2-down.png" alt="รูปที่ 24 ภาพหน้าจอจริง สาขา a ยังขายได้" width="700"><br>
  <em><b>รูปที่ 24</b> ภาพหน้าจอจริงจากการทดลอง: ระหว่างที่ lab-worker2 ถูก docker stop และเป็น NotReady สาขา a บน lab-worker ยังรับออเดอร์ได้ ออเดอร์ทั้งหมดเพิ่มเป็น 3</em>
</p>

<p align="center" id="fig-25">
  <img src="images/screenshots/20261004_1940_lab10_04-branch-b-unreachable.png" alt="รูปที่ 25 ภาพหน้าจอจริง สาขา b เปิดไม่ได้" width="700"><br>
  <em><b>รูปที่ 25</b> ภาพหน้าจอจริงจากการทดลอง: browser เปิด http://localhost:3002 (สาขา b) ไม่ได้ ขึ้น ERR_CONNECTION_RESET เพราะ port-forward ไปยัง Pod บนเรือที่ล่มหลุดไปแล้ว</em>
</p>

รอต่ออีกราว 60 วินาทีหลัง NotReady (บัตรผ่าน `tolerationSeconds: 60`) แล้วลองช่วยสาขา b

```bash
kubectl get pod -l app=som-shop -o wide
time timeout 40 kubectl port-forward pod/som-shop-b 3002:3000; echo "exit=$?"
kubectl apply -f som-shop-branches/k8s/som-shop-b.yaml
kubectl delete pod som-shop-b --wait=false; kubectl get pod som-shop-b
kubectl get events --field-selector involvedObject.name=som-shop-b | tail -4
```

```text
NAME         READY   STATUS        RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running       0          2m37s   10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Terminating   0          5m14s   10.244.2.4    lab-worker2   <none>           <none>
error: error upgrading connection: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host

real	0m6.174s
exit=1
pod/som-shop-b configured
Warning: Detected changes to resource som-shop-b which is currently being deleted.
pod "som-shop-b" deleted from default namespace
NAME         READY   STATUS        RESTARTS   AGE
som-shop-b   2/2     Terminating   0          5m20s
5m11s       Normal    Started                pod/som-shop-b   Container started
5m11s       Warning   Unhealthy              pod/som-shop-b   Readiness probe failed: Get "http://10.244.2.4:3000/api/health": dial tcp 10.244.2.4:3000: connect: connection refused
89s         Warning   NodeNotReady           pod/som-shop-b   Node is not ready
29s         Normal    TaintManagerEviction   pod/som-shop-b   Marking for deletion Pod default/som-shop-b
```

(Event `Unhealthy` ตอนอายุ 5m11s เป็นของช่วงเปิดร้านใหม่ ๆ ที่เว็บยังไม่พร้อม เป็นเรื่องปกติจากบทที่ 2)

ไทม์ไลน์จริงจากสคริปต์เฝ้าดู (T0 = `docker stop` ตัดบางบรรทัดและคอลัมน์ท้าย)

```text
19:25:15 +0s node=Ready Ready=True taints=[] pods: som-shop-a=Running som-shop-b=Running
19:25:57 +40s node=Ready Ready=True taints=[] pods: som-shop-a=Running som-shop-b=Running
19:25:59 +43s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Running
19:26:58 +102s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Running
19:27:00 +104s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Terminating
...
19:27:48 +152s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: som-shop-a=Running som-shop-b=Terminating
```

ตอนนี้ร้านน้องส้มเหลือสาขาเดียว และ **ไม่มีใครเปิดสาขา b ใหม่บนเรือที่ยังดีให้** (ถึงจะมีเรือ `lab-worker` ว่างอยู่ ก็ติดกฎ anti-affinity กับสาขา a และไม่มีใครสร้าง Pod ใหม่ให้อยู่ดี)

### 10.10 เรือกลับมา

```bash
docker start $NODE_B; T0=$(date +%s); until kubectl get node $NODE_B --no-headers | grep -q " Ready "; do sleep 1; done; echo "$NODE_B Ready หลัง docker start $(( $(date +%s) - T0 )) วินาที"; while kubectl get pod som-shop-b >/dev/null 2>&1; do sleep 1; done; echo "som-shop-b หายจริงหลัง docker start $(( $(date +%s) - T0 )) วินาที"; kubectl get nodes; kubectl get pod -l app=som-shop -o wide
```

```text
lab-worker2
lab-worker2 Ready หลัง docker start 2 วินาที
som-shop-b หายจริงหลัง docker start 5 วินาที
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   34m   v1.37.0
lab-worker          Ready    <none>          34m   v1.37.0
lab-worker2         Ready    <none>          34m   v1.37.0
NAME         READY   STATUS    RESTARTS   AGE    IP            NODE         NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          3m8s   10.244.1.24   lab-worker   <none>           <none>
```

ตรวจเรือที่กลับมา (taint หาย, Pod ระบบกลับมา, image ยังอยู่บนเรือ)

```bash
kubectl get node $NODE_B -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key
kubectl get pod -n kube-system -o wide --field-selector spec.nodeName=$NODE_B
docker exec $NODE_B crictl images | grep -E "som-shop|postgres"
```

```text
NAME          TAINTS
lab-worker2   <none>
NAME               READY   STATUS    RESTARTS      AGE   IP           NODE          NOMINATED NODE   READINESS GATES
kindnet-68hkk      1/1     Running   3 (30s ago)   35m   172.19.0.2   lab-worker2   <none>           <none>
kube-proxy-7k6xk   1/1     Running   3 (30s ago)   35m   172.19.0.2   lab-worker2   <none>           <none>
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.0                  b95826bfd89f2       76.6MB
```

(RESTARTS ของ `kindnet`/`kube-proxy` สะสมทุกครั้งที่หยุด/เริ่มเรือ ในตัวอย่างเป็น 3 เพราะผ่าน LAB 8 มาแล้ว) เปิดสาขา b ใหม่เอง

```bash
kubectl apply -f som-shop-branches/k8s/som-shop-b.yaml && kubectl wait --for=condition=Ready pod/som-shop-b --timeout=120s; kubectl get pod -l app=som-shop -o wide
kubectl port-forward pod/som-shop-b 3002:3000 > /tmp/pf-b.log 2>&1 &
sleep 2; for p in 3001 3002; do curl -s localhost:$p | grep -oE "<h1>[^<]*</h1>|<span class=\"num\">[^<]*</span><span class=\"label\">ออเดอร์ทั้งหมด"; done
```

```text
pod/som-shop-b created
pod/som-shop-b condition met
NAME         READY   STATUS    RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
som-shop-a   2/2     Running   0          3m41s   10.244.1.24   lab-worker    <none>           <none>
som-shop-b   2/2     Running   0          7s      10.244.2.2    lab-worker2   <none>           <none>
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker</h1>
<span class="num">1</span><span class="label">ออเดอร์ทั้งหมด
<h1>ร้านอาหารแมวน้องส้ม สาขา lab-worker2</h1>
<span class="num">0</span><span class="label">ออเดอร์ทั้งหมด
```

🌐 รีเฟรชทั้งสองแท็บ ร้านกลับมาครบ 2 สาขา (สาขา a มี 1 ออเดอร์ที่สั่งระหว่างเรือ b ล่ม สาขา b เริ่มที่ 0 ใหม่)

**(ทางเลือก) ดูทรัพยากรที่สาขาหนึ่งจอง**

```bash
kubectl describe node lab-worker | sed -n '/Allocated resources/,/^Events/p' | head -6
docker stats --no-stream --format "{{.Name}} {{.MemUsage}}"
```

```text
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                300m (0%)   1 (3%)
  memory             498Mi (0%)  1Gi (1%)
lab-worker 391.4MiB / 61.5GiB
lab-worker2 206.1MiB / 61.5GiB
lab-control-plane 758.3MiB / 61.5GiB
```

(1 สาขาจอง 200m/448Mi บวกกับ `kindnet` 100m/50Mi = 300m/498Mi ตามที่คำนวณในทฤษฎีหัวข้อ 5)

### สิ่งที่เห็นใน LAB 10

| ขั้น | ผลจริง |
|---|---|
| ก่อนติดธง | ทั้งสองสาขา Pending `didn't match Pod's node affinity/selector` |
| ติดธง `shop=open` | ถูกวางเองทันที `2/2 Running` บนเรือคนละลำ ภายใน 8 วินาที |
| Downward API | `SHOP_NAME=ร้านอาหารแมวน้องส้ม สาขา lab-worker` / `... lab-worker2` หน้าเว็บและชื่อแท็บแสดงชื่อสาขา |
| สาขาที่ 3 | Pending `2 node(s) didn't match pod anti-affinity rules` |
| ออเดอร์ | แต่ละสาขานับแยกกัน (a = 2, b = 0) เพราะ emptyDir แยก |
| drain เรือของ a | ต้องใส่ `--delete-emptydir-data` และ `--force`, สาขา a หายใน ~1 วินาที, port-forward `lost connection to pod`, สาขา b ขายต่อ, ไม่มีใครเปิด a ใหม่ |
| เปิด a ใหม่ระหว่าง cordon | Pending มีเหตุผล `node(s) were unschedulable` ครบ → uncordon แล้ว Running ใน ~7 วินาที ออเดอร์เริ่มที่ 0 |
| เรือของ b ล่ม | port-forward หลุดทันที, NotReady ~43 วินาที, สาขา a ขายได้ตลอด, b ถูกไล่ที่ NotReady + ~61 วินาที แล้วค้าง Terminating, apply ซ้ำได้แค่ Warning |
| เรือกลับ | Ready ใน 2 วินาที, b หายจริงใน 5 วินาที, ต้อง apply b ใหม่เอง ข้อมูลเริ่มใหม่ |

### 10.11 เก็บกวาด LAB 10

1. 🖥️ หน้าต่าง `ssh -L 3001 ... 3002`: พิมพ์ `exit`
2. 🐧 SSH session หลักของ k8s-lab: หยุด port-forward ลบทุกสาขา และ **ลบธง `shop`** ตรวจว่าไม่มี Node ใดเป็น `SchedulingDisabled` หรือ `NotReady`

```bash
pkill -f "[k]ubectl port-forward pod/som-shop"
kubectl delete pod -l app=som-shop
kubectl label node lab-worker lab-worker2 shop-
kubectl get nodes -L shop; kubectl get pod
pgrep -af "[k]ubectl port-forward" || echo "(ไม่มี port-forward ค้าง)"
```

```text
pod "som-shop-a" deleted from default namespace
pod "som-shop-b" deleted from default namespace
node/lab-worker unlabeled
node/lab-worker2 unlabeled
NAME                STATUS   ROLES           AGE   VERSION   SHOP
lab-control-plane   Ready    control-plane   36m   v1.37.0   
lab-worker          Ready    <none>          36m   v1.37.0   
lab-worker2         Ready    <none>          36m   v1.37.0   
No resources found in default namespace.
```

(pattern `[k]ubectl` ใช้กัน `pkill`/`pgrep` ไปตรงกับ command line ของตัวเอง บรรทัดสุดท้ายควรได้ `(ไม่มี port-forward ค้าง)`)

### 10.12 ปูทางบทหน้า: ทำไมร้านจริงไม่ทำแบบนี้

<p align="center" id="fig-26">
  <img src="images/22-lab10-next-deployment-service.png" alt="รูปที่ 26 ปูทางบทหน้า" width="900"><br>
  <em><b>รูปที่ 26</b> ปิดท้าย: ถ้าอยากให้มีคนเปิดสาขาใหม่อัตโนมัติและมีที่อยู่เดียวสำหรับลูกค้า ต้องใช้ Deployment และ Service ในบทหน้า</em>
</p>

สิ่งที่น้องส้มเจอใน LAB นี้คือปัญหาจริงของ Pod เดี่ยว

| ปัญหาที่เห็นใน LAB 10 | สิ่งที่บทหน้าจะใช้แก้ |
|---|---|
| drain/เรือล่มแล้วสาขาหาย **ไม่มีใครเปิดใหม่** ต้อง `kubectl apply` เอง | **Deployment** กำหนด "ต้องการ 2 สาขา" แล้ว controller สร้าง Pod ใหม่ให้เองบนเรือที่ยังดี |
| ต้องก๊อปปี้ YAML เป็น a, b, c | Pod template เดียวใน Deployment ใส่ affinity/anti-affinity/toleration ที่เรียนในบทนี้ได้เหมือนเดิม |
| ลูกค้าต้องจำ 2 port (3001, 3002) และ port-forward หลุดทุกครั้งที่ Pod หาย | **Service** ที่อยู่เดียวคงที่ กระจายลูกค้าไปทุกสาขาที่พร้อม |
| ออเดอร์แต่ละสาขาแยกกันและหายเมื่อ Pod หาย | ฐานข้อมูลกลาง + ที่เก็บข้อมูลถาวร (PersistentVolumeClaim) |

### คำถามท้าย LAB 10

1. ทำไม `som-shop-c` จึง Pending และข้อความ FailedScheduling นับ control-plane เป็น "untolerated taint" แทน "ไม่มีธง shop"
2. ถ้าลบ `podAntiAffinity` ออกจากทั้ง 3 ไฟล์แล้ว apply ใหม่ทั้ง 3 สาขา ผลการจัดวางจะเป็นอย่างไร และร้านจะเสี่ยงอะไรเพิ่มขึ้น
3. ตอน drain เรือของสาขา a ทำไมต้องใส่ `--delete-emptydir-data` และข้อมูลออเดอร์ของสาขา a หายไปไหน
4. ทำไม `som-shop-a` ที่ apply ใหม่ระหว่าง cordon จึง Pending ทั้งที่ `lab-worker` ยัง `Ready` อยู่ อ่านเหตุผลจากข้อความ FailedScheduling ให้ครบทั้ง 3 Node
5. หลัง `docker stop` ทำไมหน้า 3002 เปิดไม่ได้ **ทันที** ทั้งที่ Node ยังแสดง `Ready` อีกเกือบ 45 วินาที และทำไม `som-shop-b` ถูกไล่ที่ราว 104 วินาทีหลัง stop ไม่ใช่ 60 วินาที

> **🏆 ท้าทาย:** แก้ toleration ของ `som-shop-b.yaml` ให้ไม่มี `tolerationSeconds` (อยู่ต่อได้ตลอดเมื่อเรือล่ม) แล้วทำขั้น 10.9 ซ้ำ บันทึกว่าเกิดอะไรขึ้นกับสาขา b และอธิบายว่าในงานจริงตัวเลือกนี้ดีหรือไม่ดีอย่างไร

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-branches/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 003_kubernetes_node_pod k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/003_kubernetes_node_pod/02_LAB` (ตรวจด้วย `pwd`) |
| `docker stop lab-worker2` ได้ `Error response from daemon: No such container: lab-worker2` | พิมพ์บน **เครื่องตัวเอง** ไม่ใช่ใน k8s-lab | 🐧 พิมพ์ใน SSH session ของ k8s-lab (`ssh -p 2223 root@localhost`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (connection refused) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ แล้วถ้าจะทำ LAB 10 ต้อง build/`kind load` image ใหม่ |
| Pod ค้าง `Pending` | กฎจัดวางไม่มี Node ใดผ่าน | อ่าน `kubectl describe pod <ชื่อ> \| sed -n '/^Events/,$p'` แล้วดูตาราง "ข้อความ FailedScheduling" ในทฤษฎีหัวข้อ 4.3 ตรวจ label (`kubectl get nodes -L ...`), taint (`custom-columns` แบบ LAB 0) และ cordon (`kubectl get nodes`) |
| LAB ถัดไปผลไม่ตรงเอกสาร (เช่น Pod ไปลงแต่ `lab-worker2` หรือ Pending แปลก ๆ) | ลืมเก็บกวาด label/taint/cordon จาก LAB ก่อน | ทำ [ตารางคืนสภาพคลัสเตอร์](#ตารางคืนสภาพคลัสเตอร์) |
| `error: 'fleet' already has a value (fast), and --overwrite is false` | เปลี่ยนค่า label ที่มีอยู่แล้ว | ใส่ `--overwrite` |
| drain ขึ้น `cannot delete Pods that declare no controller` / `with local storage` / `DaemonSet-managed Pods` | ด่านป้องกันของ drain | ใส่ `--force` / `--delete-emptydir-data` / `--ignore-daemonsets` ตามข้อความ แล้ว **อย่าลืม `kubectl uncordon`** |
| Node ค้าง `Ready,SchedulingDisabled` | drain (แม้ error) หรือ cordon แล้วลืม uncordon | `kubectl uncordon <ชื่อ node>` |
| `lab-worker2` ค้าง `NotReady` | ลืม `docker start lab-worker2` หลัง LAB 8/10 | 🐧 `docker ps -a` ดูสถานะ แล้ว `docker start lab-worker2` รอ `kubectl get nodes` (ปกติ Ready ใน 2 วินาที) ถ้าไม่กลับภายใน 2 นาที ใช้แผนสำรอง `k8s-down && k8s-up` แล้ว load image ใหม่ |
| Pod ค้าง `Terminating` นาน | Pod อยู่บนเรือที่ล่ม kubelet ยืนยันการลบไม่ได้ | ปกติ จะหายเองภายในไม่กี่วินาทีหลัง `docker start` |
| `kubectl exec/logs/port-forward` ได้ `dial tcp 172.19.0.x:10250: connect: no route to host` | Pod อยู่บนเรือที่ล่ม | ปกติระหว่าง LAB 8/10 รอเรือกลับ |
| `kubectl delete pod static-snack-lab-worker` ค้างราว 1 นาที แล้ว Pod กลับมาอีก | เป็น mirror pod ของ static Pod | ใช้ `--wait=false` หรือ Ctrl+C และลบไฟล์บนเรือ `docker exec lab-worker rm /etc/kubernetes/manifests/static-snack.yaml` |
| `spread-3`/`spread-4` Pending ทั้งที่ worker ว่าง | `nodeTaintsPolicy` ค่าเริ่มต้นเป็น `Ignore` นับ control-plane | เป็นผลที่ตั้งใจใน LAB 5 ใช้ `nodeTaintsPolicy: Honor` |
| `som-shop-*` ค้าง `Init:ErrImagePull` / `ImagePullBackOff` | ไม่มี image บน Node (สร้างคลัสเตอร์ใหม่แต่ยังไม่ `kind load`) | ทำ 10.2 แล้ว `kubectl delete pod -l app=som-shop` และ apply ใหม่ |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` (ARM ใช้ `linux/arm64`) |
| `kubectl port-forward` แจ้ง `address already in use` | port-forward ตัวเก่ายังค้าง | `pgrep -af "[k]ubectl port-forward"` แล้ว `pkill -f "[k]ubectl port-forward pod/som-shop"` |
| browser เปิด `localhost:3001`/`3002` ไม่ได้ (`ERR_CONNECTION_RESET`/refused) | หน้าต่าง `ssh -L` ถูกปิด หรือ port-forward หลุดเพราะ Pod ถูกลบ/เรือล่ม | ดู `cat /tmp/pf-a.log` ถ้ามี `lost connection to pod` ให้เปิด port-forward ใหม่หลังมี Pod ใหม่ |
| `ssh -L` แจ้งว่า bind port ไม่ได้ | port 3001/3002 บนเครื่องนักศึกษาถูกโปรแกรมอื่นใช้ | เปลี่ยนเลขซ้ายของ `-L` เช่น `-L 13001:localhost:3001` แล้วเปิด `http://localhost:13001` |
| หน้าเว็บ footer เขียน `Kubernetes LAB 002` | ใช้แอปเดิมจากบทที่ 2 โดยไม่แก้โค้ด | ไม่ใช่ข้อผิดพลาด |
| scheduler วางสาขาสลับกับในเอกสาร (a อยู่ `lab-worker2`) | scheduler เลือกเอง เรากำหนดแค่ "คนละลำ" | ใช้ `NODE_A`/`NODE_B` จาก `kubectl get pod ... -o jsonpath={.spec.nodeName}` ทุกครั้ง |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes -o wide`, ผล capacity/allocatable และ `docker exec lab-worker crictl ps`
- [ ] **LAB 1** Events `FailedScheduling ... Insufficient memory` ของ `huge-pod` และ `Allocated resources` หลังวาง `fit-pod`
- [ ] **LAB 2** `kubectl get pod -o wide` ที่ `pinned-pod` อยู่บน `lab-control-plane` และ `kubectl logs whereami`
- [ ] **LAB 3** Events ของ `selector-pod` ที่มีทั้ง `FailedScheduling` และ `Scheduled` และผล `prefer-*` เมื่อไม่มีเรือ fast
- [ ] **LAB 4** `crew-3` Pending พร้อมข้อความ `didn't match pod anti-affinity rules`
- [ ] **LAB 5** ตารางเปรียบเทียบ `spread-*` (Pending 2 ตัว) กับ `honor-*` (2 : 2)
- [ ] **LAB 6** Events `TaintManagerEviction` ของ `no-pass` และ `pass-30s`
- [ ] **LAB 7** ผล drain ที่สำเร็จ (`node/lab-worker drained`) และ `kubectl get pod -o wide` หลัง drain
- [ ] **LAB 8** `describe node lab-worker2` ที่ condition เป็น `Unknown` พร้อม taint `unreachable` และ `fog-*` ค้าง `Terminating`
- [ ] **LAB 9** annotation `kubernetes.io/config.mirror` และ ownerReferences `kind: Node` ของ `static-snack-lab-worker`
- [ ] **LAB 10** (1) `kubectl get pod -l app=som-shop -o wide` 2 สาขาคนละ NODE (2) browser 2 แท็บแสดงชื่อสาขาต่างกันและออเดอร์แยก (3) FailedScheduling ของ `som-shop-c` (4) ผล drain และ `som-shop-a` Pending ระหว่าง cordon (5) `lab-worker2 NotReady` + `som-shop-b Terminating` ขณะสาขา a ยังรับออเดอร์ได้
- [ ] ท้ายสุด `kubectl get pods` ได้ `No resources found in default namespace.`, Node ทั้ง 3 `Ready` ไม่มี `SchedulingDisabled` และไม่มี label/taint ที่เราติดค้าง

---

## ตารางคืนสภาพคลัสเตอร์

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| Pod ของ LAB | 1–8 | `kubectl get pod -l lab=03` | `kubectl delete pod -l lab=03 --now` |
| label `fleet`, `deck` | 3 | `kubectl get nodes -L fleet,deck` | `kubectl label node lab-worker lab-worker2 fleet- deck-` |
| taint `dedicated`, `maintenance` | 6 | `kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key` (ต้องเหลือแค่ของ control-plane) | `kubectl taint node lab-worker2 maintenance=true:NoExecute- dedicated=vip:NoSchedule-` |
| Node ถูก cordon | 7, 10 | `kubectl get nodes` (ไม่มี `SchedulingDisabled`) | `kubectl uncordon lab-worker` (หรือ `lab-worker2`) |
| เรือ `lab-worker2` หยุดอยู่ | 8, 10 | `docker ps -a --format '{{.Names}}\t{{.Status}}'` และ `kubectl get nodes` | `docker start lab-worker2` แล้วรอ `Ready` |
| ไฟล์ static Pod บนเรือ | 9 | `docker exec lab-worker ls /etc/kubernetes/manifests` (ต้องว่าง) | `docker exec lab-worker rm -f /etc/kubernetes/manifests/static-snack.yaml` |
| สาขาร้าน | 10 | `kubectl get pod -l app=som-shop` | `kubectl delete pod -l app=som-shop` |
| label `shop` | 10 | `kubectl get nodes -L shop` | `kubectl label node lab-worker lab-worker2 shop-` |
| port-forward ค้าง | 10 | `pgrep -af "[k]ubectl port-forward"` | `pkill -f "[k]ubectl port-forward pod/som-shop"` |

ตอนลบ label/taint ที่ไม่มีอยู่แล้ว kubectl อาจแจ้งว่า `not found` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get pods
kubectl get nodes -L fleet,deck,shop
kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key
docker exec lab-worker ls /etc/kubernetes/manifests
pgrep -af "[k]ubectl port-forward" || echo "ไม่มี port-forward ค้าง"
```

ผลที่ถูกต้อง: ไม่มี Pod ใน default namespace, Node ทั้ง 3 `Ready` ไม่มีคอลัมน์ `FLEET/DECK/SHOP` ที่มีค่า, taint เหลือเฉพาะ `node-role.kubernetes.io/control-plane` บน `lab-control-plane`, โฟลเดอร์ manifests ของ `lab-worker` ว่าง และไม่มี port-forward ค้าง

คลัสเตอร์ `lab` เก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ `kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

> **บทถัดไป:** น้องส้มจะเลิกก๊อปปี้ YAML ทีละสาขา ให้ Deployment ดูแลจำนวนสาขาและเปิดสาขาใหม่เองเมื่อเรือล่ม ใช้ Service เป็นที่อยู่เดียวของร้าน และนำกฎ affinity/anti-affinity/toleration ที่เรียนในบทนี้ไปใส่ใน Pod template
