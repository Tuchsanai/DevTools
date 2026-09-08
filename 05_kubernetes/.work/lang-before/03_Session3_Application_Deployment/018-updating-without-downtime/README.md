# LAB 18 — Updating without Downtime : v1 ไป v2 โดยประตูไม่เคยปิด

> โฟลเดอร์ `018-updating-without-downtime` = LAB 18 ของชุด Kubernetes ครั้งที่ 3
> (ไฟล์ของแล็บนี้: `manifests/01-configmap.yaml` ถึง `manifests/10-db-service.yaml`, `02-web-recreate.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** เปลี่ยนเวอร์ชันทีละส่วนทำให้ผู้ใช้ไม่สะดุด

## วัตถุประสงค์ของแล็บ

1. อธิบายได้ว่า rolling update รักษา availability ด้วย Pod เก่าและใหม่อย่างไร
2. อธิบายความสัมพันธ์ของ `maxSurge`, `maxUnavailable`, readiness และ `minReadySeconds` ได้
3. พิสูจน์จาก request ต่อเนื่องได้ว่า rollout และ rollback ไม่ทำให้เว็บล่ม

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

Deployment ไม่แก้ container เดิม แต่สร้าง ReplicaSet ใหม่จาก Pod template เวอร์ชันใหม่ แล้วค่อยปรับจำนวนระหว่าง ReplicaSet เก่า/ใหม่

| ค่า | คำถามที่ตอบ | ค่าในแล็บ |
|---|---|---|
| `replicas` | ปกติต้องมี web กี่ตัว | 3 |
| `maxSurge` | ระหว่าง update เพิ่มเกินได้เท่าไร | 1 |
| `maxUnavailable` | ยอมให้ตัวพร้อมหายกี่ตัว | 0 |
| readiness | Pod ใหม่รับ request ได้หรือยัง | `GET /readyz` |
| `minReadySeconds` | ต้องพร้อมนิ่งนานเท่าไรก่อนเดินต่อ | 5 วินาที |

`maxUnavailable: 0` ทำให้ Pod เก่ายังอยู่ แต่ zero-downtime จะสมบูรณ์ก็ต่อเมื่อ Service ไม่ส่งงานให้ Pod ใหม่ก่อนแอปพร้อม นั่นคือหน้าที่ของ readinessProbe

Recreate ตรงกันข้าม: ลบ Pod เก่าทั้งหมดก่อนสร้างใหม่ จึงมีช่วงที่ Service ไม่มี endpoint และ ingress-nginx ตอบ 503

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น ReplicaSet v1 และ v2 ปรับจำนวนทีละส่วน
- จะได้ยิง request ทุก 0.3 วินาทีระหว่าง update
- จะได้เห็นหน้าเว็บธีมน้ำเงิน v1 เปลี่ยนเป็น emerald v2
- จะได้ undo กลับ v1 โดยใช้ ReplicaSet revision เดิม
- จะได้ทำ Recreate และถอด readiness จนเห็น `FAIL` จริง
- จะได้พิสูจน์ Clean Re-run จาก manifest baseline v1

## ภาพรวมของแล็บนี้

1. deploy ระบบครบโดย web v1 มี 3 replicas
2. เปิด request loop, ReplicaSet watch, stern และ refresh หน้าเว็บ
3. เปลี่ยน image เป็น v2 แล้วติดตามจนจบ
4. undo กลับ v1 โดยไม่มี `FAIL`
5. ทดลอง Recreate และทดลองถอด readinessProbe
6. apply baseline คืน, Cleanup และ Clean Re-run

![ไทม์ไลน์ rolling update จาก web v1 ไป v2](../slides_assets/lab018-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า Pod ใหม่ใช้เวลาสตาร์ต แม้เพียงเสี้ยววินาที Kubernetes ต้องรู้อะไรจึงกล้าหยุด Pod เก่า?

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** เข้าเครื่องเรียนด้วย `docker exec -it` (ทุกคำสั่งหลังจากนี้พิมพ์ในเครื่องเรียน) · `k8s-bootstrap` ข้ามเองถ้า cluster มีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image v1/v2

ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `localhost:8080`

✅ **Expected output** — node ทั้งสาม Ready และมี web v1/v2 พร้อม rollout (AGE และ image ID ต่างกันได้):
```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready   control-plane   31m   v1.36.4
devtools-worker          Ready   <none>          30m   v1.36.4
devtools-worker2         Ready   <none>          30m   v1.36.4
docker.io/library/k8s-lab-api   v1   1b0af425a075d   186MB
docker.io/library/k8s-lab-db    v1   35984a84885cb   300MB
docker.io/library/k8s-lab-web   v1   2a74c90a62059   209MB
docker.io/library/k8s-lab-web   v2   7bedccdeefc86   209MB
```

ถ้าผล `grep` ว่าง → ทำขั้น build/load ใน README ระดับชุดหรือ LAB 001

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/018-updating-without-downtime
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง path ซ้ำได้ · `&&` ไปต่อเมื่อสำเร็จ · `git clone` ดาวน์โหลด repository · `cd` เข้า LAB 18

✅ **Expected output** — clone สำเร็จและเข้าโฟลเดอร์แล็บได้:
```text
Cloning into 'DevTools'...
```

ถ้า clone แล้วให้ใช้ `git pull` ใน `~/labwork/DevTools` แทนการ clone ซ้ำ

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/01-configmap.yaml` | ConfigMap | ให้ config แก่ web | [ทบทวน ConfigMap](../YAML_Guide.md#configmap) |
| `manifests/02-web-deployment.yaml` | Deployment | กำหนด RollingUpdate แบบไม่ลด Available | [strategy](../YAML_Guide.md#3-strategy) |
| `manifests/03-web-service.yaml` | Service | ส่งงานเฉพาะ web Pod ที่ Ready | [ทบทวน Service](../YAML_Guide.md#service) · [ทบทวน Probes](../YAML_Guide.md#probes) |
| `manifests/04-api-deployment.yaml` | Deployment | รัน api ของระบบประกอบ | [ทบทวน Deployment](../YAML_Guide.md#deployment) |
| `manifests/05-api-service.yaml` | Service | ให้ web หา api | [ทบทวน Service](../YAML_Guide.md#service) |
| `manifests/06-ingress.yaml` | Ingress | เปิด `/` และ `/api` | [Ingress](../YAML_Guide.md#1-ingress) |
| `manifests/07-secret.yaml` | Secret | ให้ค่าเชื่อมต่อ db | [ทบทวน Secret](../YAML_Guide.md#secret) |
| `manifests/08-pvc.yaml` | PersistentVolumeClaim | ขอพื้นที่ db | [ทบทวน PVC](../YAML_Guide.md#pvc) |
| `manifests/09-db-deployment.yaml` | Deployment | ใช้ Recreate กับ db/PVC | [Recreate](../YAML_Guide.md#3-strategy) |
| `manifests/10-db-service.yaml` | Service | ให้ api หา db | [ทบทวน Service](../YAML_Guide.md#service) |
| `02-web-recreate.yaml` | Deployment | จงใจเปลี่ยน web เป็น Recreate เพื่อเห็น downtime | [Recreate](../YAML_Guide.md#3-strategy) |

ค่าจริงจาก `manifests/02-web-deployment.yaml`:

```yaml
spec:
  replicas: 3
  minReadySeconds: 5       # Ready ต่อเนื่อง 5 วินาทีจึงนับ Available
  strategy:
    type: RollingUpdate    # default ก็เป็นชนิดนี้ แต่ไฟล์เขียนให้เห็นชัด
    rollingUpdate:
      maxSurge: 1          # เกิน desired replicas ได้ 1 Pod
      maxUnavailable: 0    # ไม่ยอมให้ Available ลดเพราะ rollout
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `type` | `RollingUpdate` หรือ `Recreate`; default `RollingUpdate` | Recreate ลบชุดเก่าก่อนสร้างชุดใหม่ |
| `maxSurge` | จำนวน/เปอร์เซ็นต์ที่สร้างเกิน; default 25% ปัดขึ้น | มากขึ้นเร็วขึ้นแต่ใช้ capacity ชั่วคราวมากขึ้น |
| `maxUnavailable` | จำนวน/เปอร์เซ็นต์ที่ขาดได้; default 25% ปัดลง | มากขึ้นยอมให้บริการเหลือน้อยลง; ห้ามทั้งคู่เป็น 0 |
| `minReadySeconds` | เวลาที่ Ready ต่อเนื่อง; default 0 | เพิ่มเวลาเฝ้าดู Pod ใหม่ก่อนนับ Available |
| `revisionHistoryLimit` | revision เก่าที่เก็บ; ไฟล์ไม่ใส่จึง default 10 | ตั้ง 0 แล้ว rollback revision เก่าไม่ได้ |

**ผิดบ่อยในแล็บนี้:** เห็น `maxUnavailable: 0` แล้วคิดว่าเพียงพอ แต่ถ้า readiness ไม่สะท้อนการพร้อมรับงาน
Pod ใหม่อาจรับ request เร็วไป; ส่วน `02-web-recreate.yaml` ทำให้ runlog แสดง `FAIL` ต่อเนื่องจริงระหว่างเปลี่ยนรุ่น

ดู field ได้ด้วย `kubectl explain deployment.spec.strategy.rollingUpdate`, `kubectl explain deployment.spec.minReadySeconds` และ `kubectl explain deployment.spec.revisionHistoryLimit`

## 3. สร้าง baseline v1 จำนวน 3 Pod

ส่วนสำคัญของ `manifests/02-web-deployment.yaml` คือ:
```yaml
replicas: 3
minReadySeconds: 5
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
# container มี readinessProbe path /readyz
```

ทุก image ของแอปกำหนด `imagePullPolicy: IfNotPresent`; readiness ใช้ port ชื่อ `http` จึงไม่ผูกกับเลขซ้ำหลายจุด
```bash
kubectl create namespace lab018
kubectl apply -f manifests/
kubectl wait -n lab018 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
kubectl get pods -n lab018 -o wide
until curl -sf http://localhost/info >/dev/null; do sleep 1; done
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** สร้าง namespace แยก · apply ระบบครบ · wait รอ Available · `-o wide` ดู Pod/node · `/info` ตรวจ request จริงผ่าน Ingress และแสดง version

✅ **Expected output** — web v1 พร้อม 3 Pod, api/db พร้อม และ `/info` เป็น v1/db up (ชื่อ Pod, IP, node, AGE และเวลาต่างกันได้):
```text
api-6b56dd98f-skstx   1/1   Running   0   19s
db-7dd8b59fd7-rfgk4   1/1   Running   0   18s
web-74cb858c9-8nxgf   1/1   Running   0   19s
web-74cb858c9-l5mqf   1/1   Running   0   19s
web-74cb858c9-w6nqk   1/1   Running   0   19s
{"pod":"web-74cb858c9-8nxgf","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-skstx"},"db":{"status":"up"}}
```

## 4. เปิดหลักฐานแบบต่อเนื่อง

เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้งเป็นเทอร์มินัล 2 สำหรับยิง request; กด `Ctrl+C` หลัง rollout จบ
```bash
while true; do
  curl --retry 0 -s -f -m 2 http://localhost/info \
    | jq -c '{pod,version}' || echo FAIL
  sleep 0.3
done
```
> 📝 **คำอธิบาย:** `--retry 0` ไม่ซ่อน failure · `-s -f` เงียบแต่คืน non-zero เมื่อ HTTP error · `-m 2` timeout สองวินาที · `jq -c '{pod,version}'` เลือก field ให้ตรงผลที่แสดง · `|| echo FAIL` ทำ downtime ให้เห็น · `sleep 0.3` ยิงประมาณสามครั้งต่อวินาที

✅ **Expected output** — ก่อน update เห็นชื่อ v1 สลับกันและไม่มี `FAIL` (ชื่อ Podต่างกันได้):
```text
{"pod":"web-74cb858c9-l5mqf","version":"v1"}
{"pod":"web-74cb858c9-8nxgf","version":"v1"}
{"pod":"web-74cb858c9-w6nqk","version":"v1"}
```

เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้งสำหรับแต่ละเทอร์มินัล 3–4 ที่ใช้ดูโครงสร้างและ log:
```bash
kubectl get rs -n lab018 -w
stern -n lab018 web --tail 3
```
> 📝 **คำอธิบาย:** `get rs -w` watch จำนวน desired/current/ready ของทุก ReplicaSet · `stern` รวม log Pod ที่ชื่อ/label match `web` · `--tail 3` เริ่มจากสามบรรทัดล่าสุดต่อตัว

✅ **Expected output** — เริ่มด้วย ReplicaSet v1 desired=3 และ stern ผูก log ครบหลาย Pod (hash ต่างกันได้):
```text
web-74cb858c9   3   3   3   47s
+ web-74cb858c9-8nxgf › web
+ web-74cb858c9-l5mqf › web
+ web-74cb858c9-w6nqk › web
web-74cb858c9-8nxgf web ✓ Ready in 0ms
```

## 5. Rolling update จาก v1 เป็น v2

```bash
kubectl set image deployment/web web=k8s-lab-web:v2 -n lab018 >/dev/null
kubectl rollout status -n lab018 deploy/web --timeout=180s
kubectl get rs,pods -n lab018 -l app=web
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** `set image` เปลี่ยน live Pod template โดยไม่แก้ไฟล์ baseline v1 · `rollout status` รอ controller เดินครบ · `get rs,pods` เห็น RS เก่าลดเป็น 0 · `/info` ยืนยัน version/theme

✅ **Expected output** — v2 เพิ่มทีละส่วน, RS v1 ลดเหลือ 0 และ v2 พร้อม 3 (hash/Pod/เวลาต่างกันได้):
```text
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "web" rollout to finish: 2 out of 3 new replicas have been updated...
deployment "web" successfully rolled out
web-678694c6b8   3   3   3   26s
web-74cb858c9    0   0   0   108s
{"pod":"web-678694c6b8-fw4w4","version":"v2","theme":"emerald","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-skstx"},"db":{"status":"up"}}
```

ภาพของผู้สอนถ่ายระหว่างที่ Pod มี image v1/v2 ร่วมกัน; นักศึกษาให้ refresh browser ระหว่าง rollout เพื่อสังเกตผลเอง

![ระหว่าง rollout คลัสเตอร์มี v1 และ v2 ขณะที่ผู้ใช้ยังได้หน้า v1 ปกติ](images/04-rollout-in-progress-mixed.png)

![หลัง rollout จบ หน้าเว็บเป็นธีม emerald และป้าย v2](images/04-rollout-done-v2.png)

หลักฐาน ReplicaSet, Pod และภาพระหว่างรันยืนยันว่า v1 และ v2 อยู่ร่วมกันก่อน v2 ขึ้นครบ

## 6. Rollback กลับ v1

```bash
kubectl rollout undo -n lab018 deploy/web
kubectl rollout status -n lab018 deploy/web --timeout=180s
kubectl rollout history -n lab018 deploy/web
kubectl get rs,pods -n lab018 -l app=web
```
> 📝 **คำอธิบาย:** `rollout undo` นำ Pod template revision ก่อนหน้ากลับมา · `status` รอ rollback · `history` แสดง revision ที่ Deployment เก็บ · `get rs,pods` พิสูจน์ว่า RS v1 ถูก scale ขึ้น และ RS v2 ลดเป็น 0

✅ **Expected output** — loop เห็น v2/v1 ปะปนแต่ไม่มี `FAIL`, แล้ว v1 กลับครบ 3 (hashต่างกันได้):
```text
Warning: resource deployments/web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
deployment.apps/web rolled back
{"pod":"web-678694c6b8-pf7v9","version":"v2"}
{"pod":"web-74cb858c9-x6d76","version":"v1"}
{"pod":"web-678694c6b8-fw4w4","version":"v2"}
{"pod":"web-74cb858c9-x6d76","version":"v1"}
deployment "web" successfully rolled out
REVISION  CHANGE-CAUSE
2         <none>
3         <none>
web-678694c6b8   0   0   0
web-74cb858c9    3   3   3
```

คำเตือนบอกว่า `rollout undo` ไม่แก้ annotation ของ `kubectl apply`; ขั้นต่อไปจึง apply ไฟล์ baseline คืนให้ source of truth ตรงกับ live state

![หลัง undo หน้าเว็บกลับเป็นป้าย v1 และธีมน้ำเงิน](images/06-after-undo-v1.png)

## 7. ทดลองให้พัง — เปลี่ยน strategy เป็น Recreate

เปิด request loop เดิมไว้ แล้ว apply ไฟล์ที่ใช้ `strategy.type: Recreate` และ image v2
```bash
kubectl apply -f 02-web-recreate.yaml
kubectl rollout status -n lab018 deploy/web --timeout=180s
kubectl get pods -n lab018 -l app=web
```
> 📝 **คำอธิบาย:** `Recreate` หยุด Pod เก่าทั้งหมดก่อนเริ่มชุดใหม่ · `rollout status` ยังบอกสำเร็จในที่สุด แต่ request loop เปิดเผยช่วงที่ผู้ใช้เข้าไม่ได้ · `get pods` ยืนยันปลายทางเป็น v2 ใหม่ทั้งหมด

✅ **Expected output** — มี `FAIL` รวม 17 ครั้งระหว่างรอ v2; จำนวนขึ้นกับความเร็วเครื่อง:
```text
{"pod":"web-74cb858c9-x6d76","version":"v1"}
FAIL
Waiting for deployment "web" rollout to finish: 0 of 3 updated replicas are available...
FAIL
Waiting for deployment "web" rollout to finish: 2 of 3 updated replicas are available...
FAIL
deployment "web" successfully rolled out
FAIL
{"pod":"web-678694c6b8-dss9d","version":"v2"}
{"pod":"web-678694c6b8-gkzj9","version":"v2"}
```

(ตัดบางแถว; ลำดับที่แสดงคงตาม transcript จริง)

แก้กลับด้วยการ apply `manifests/02-web-deployment.yaml` ซึ่งเป็น baseline v1 แบบ RollingUpdate แล้วรอ rollout จบ

## 8. ทดลองให้พัง — ถอด readinessProbe

จงใจลบ probe พร้อมเปลี่ยน image เป็น v2 ใน Pod template เดียว แล้วเปิด loop ที่ยิงถี่ขึ้น
```bash
kubectl patch deploy -n lab018 web --type=json \
  -p='[{"op":"remove","path":"/spec/template/spec/containers/0/readinessProbe"},{"op":"replace","path":"/spec/template/spec/containers/0/image","value":"k8s-lab-web:v2"}]'
kubectl rollout status -n lab018 deploy/web --timeout=180s
kubectl apply -f manifests/02-web-deployment.yaml
kubectl rollout status -n lab018 deploy/web --timeout=180s
```
> 📝 **คำอธิบาย:** JSON patch `remove` ถอด gate ที่ Service ใช้ · `replace` ทำให้เกิด rollout ใหม่ · Kubernetes จึงนับ container Ready เร็วเกิน · สองคำสั่งท้ายคืน strategy, readiness และ image v1 จาก manifest

✅ **Expected output** — loop จริงพบ `FAIL` 2 ครั้งก่อน rollout จบและ 3 ครั้งหลังจบ แล้ว apply baseline คืนสำเร็จ (จำนวนต่างกันได้):
```text
deployment.apps/web patched
{"pod":"web-7fdfc9d944-655vp","version":"v2"}
{"pod":"web-74cb858c9-mtfqf","version":"v1"}
FAIL
FAIL
deployment "web" successfully rolled out
FAIL
FAIL
FAIL
deployment "web" successfully rolled out
RollingUpdate maxSurge=1 maxUnavailable=0 readiness=/readyz image=k8s-lab-web:v1
```

## 9. แบบฝึกหัดสั้น (Exercise)

ทายและอธิบายผลถ้าเปลี่ยน `maxUnavailable` จาก 0 เป็น 1 โดยยังมี 3 replicas และ readiness เดิม: rollout เร็วขึ้นอย่างไร และจำนวน Pod พร้อมต่ำสุดเป็นเท่าไร

เกณฑ์สำเร็จ: วาด timeline จำนวน v1/v2 ในแต่ละจังหวะได้ โดยไม่จำคำสั่ง และอธิบาย trade-off ระหว่างความเร็วกับ capacity

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get deploy,rs,pods,endpoints -n lab018
kubectl rollout history -n lab018 deploy/web
kubectl get deploy -n lab018 web -o jsonpath='{.spec.strategy.type}{" maxSurge="}{.spec.strategy.rollingUpdate.maxSurge}{" maxUnavailable="}{.spec.strategy.rollingUpdate.maxUnavailable}{" readiness="}{.spec.template.spec.containers[0].readinessProbe.httpGet.path}{" image="}{.spec.template.spec.containers[0].image}{"\n"}'
curl -s http://localhost/info | jq -c '{pod,version,theme,api,db}'
```
> 📝 **คำอธิบาย:** ดู Deployment→ReplicaSet→Pod→Endpoint ครบสาย · history ยืนยัน revision · jsonpath ตรวจค่าที่สำคัญโดยตรง · `/info` ตรวจจากมุมผู้ใช้

✅ **Expected output** — baseline สุดท้ายเป็น RollingUpdate, v1, readiness `/readyz`, web 3 Pod Ready และ DB up:
```text
RollingUpdate maxSurge=1 maxUnavailable=0 readiness=/readyz image=k8s-lab-web:v1
web-74cb858c9-vzbr9   1/1   Running
web-74cb858c9-4mjnw   1/1   Running
web-74cb858c9-q6sq2   1/1   Running
{"pod":"web-74cb858c9-vzbr9","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-skstx"},"db":{"status":"up"}}
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| rollout ค้าง | Pod ใหม่ไม่ผ่าน readiness หรือ image ไม่มี | `describe pod`, `logs`, ตรวจ Events/image |
| ยังเห็น v1 หลังเริ่ม update | Pod เก่ายังให้บริการตาม strategy/controller sync | ดู RS/Pod คู่กับ request loop ไม่ใช้ request เดียวสรุป |
| RollingUpdate ยังมี 502/FAIL | ไม่มี readiness หรือ probe ไม่ตรวจสิ่งที่จำเป็น | คืน `/readyz` และทดสอบ endpoint จริง |
| Recreate ทำให้ 503 | Service ไม่มี endpoint ระหว่างลบเก่า-สร้างใหม่ | ใช้ RollingUpdate เมื่อ workload รองรับหลาย replica |
| undo แล้ว apply ให้ผลแปลก | annotation last-applied ยังเป็นค่าก่อน undo | คืนไฟล์ baseline แล้ว `kubectl apply` ให้ตรง source of truth |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab018 --wait=true
kubectl get all -n lab018
kubectl create namespace lab018
kubectl apply -f manifests/
kubectl wait -n lab018 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
kubectl get pods -n lab018 -l app=web
until BODY=$(curl -fsS http://localhost/info); do sleep 2; done
echo "$BODY" | jq -c '{pod,version,theme,api,db}'
kubectl delete namespace lab018 --wait=true
kubectl get all -n lab018
```
> 📝 **คำอธิบาย:** ลบและรอ namespace · `get all` พิสูจน์ความว่าง · สร้าง/apply/wait จาก baseline · loop รอ Ingress และ `/info` · ลบปิดท้าย

✅ **Expected output** — Clean Re-run ได้ v1 สาม Pod ระบบครบ แล้วปิดท้ายไม่มี resource (ชื่อ Pod และเวลาต่างกันได้):
```text
namespace "lab018" deleted
No resources found in lab018 namespace.
web-74cb858c9-5h5jh   1/1   Running   0   18s
web-74cb858c9-6z78f   1/1   Running   0   18s
web-74cb858c9-vcdrz   1/1   Running   0   18s
{"pod":"web-74cb858c9-6z78f","version":"v1","theme":"blue","api":{"configured":true,"reachable":true,"pod":"api-6b56dd98f-4k9bp"},"db":{"status":"up"}}
namespace "lab018" deleted
No resources found in lab018 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl rollout status` | ติดตาม rollout จนสำเร็จ/timeout |
| `kubectl get rs -w` | ดู ReplicaSet เก่า/ใหม่เปลี่ยนจำนวน |
| `stern -n lab018 web` | รวม log จากหลาย web Pod |
| `kubectl rollout undo` | นำ Pod template revision ก่อนหน้ากลับมา |
| `kubectl rollout history` | ดู revision ที่ยังเก็บไว้ |
| `kubectl patch ...` | ทำการทดลองเปลี่ยน field ชั่วคราว |
| `kubectl apply -f manifests/02-web-deployment.yaml` | คืน baseline จาก source of truth |

## สรุปสิ่งที่ได้เรียนรู้

zero-downtime ไม่ได้เกิดจากคำว่า RollingUpdate เพียงคำเดียว:

- `maxUnavailable: 0` รักษา Pod เก่าที่พร้อมไว้จนตัวใหม่มาทดแทน
- readiness กัน Pod ใหม่ออกจาก Service จนแอปพร้อมจริง
- ReplicaSet revision ทำให้ undo เปลี่ยนจำนวนกลับได้ ไม่ต้อง rebuild image
- Recreate ทำให้เห็นช่องว่าง endpoint ชัดเจน; ถอด readiness ทำให้ error ประปราย

**จำภาพเดียวให้ได้:** rolling update คือเปลี่ยนหลอดไฟทีละดวงโดยเปิดดวงเก่าไว้ จนดวงใหม่สว่างและผ่านการตรวจแล้ว

🧭 ต่อยอด: LAB 19 จะเพิ่ม requests/limits เพื่อให้ scheduler รู้ว่า Pod แต่ละรุ่นต้องการทรัพยากรเท่าไร

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **ทำไม rolling update จึงไม่ทำให้เว็บล่ม?** — มี Pod เก่าพร้อมเสมอจาก `maxUnavailable: 0` และ Pod ใหม่เข้า Service หลัง readiness ผ่าน
2. **rollback ทำได้เพราะระบบเก็บอะไร?** — Deployment เก็บ Pod template แต่ละ revisionไว้ใน ReplicaSet ที่ scale เป็น 0 ได้
3. **readinessProbe เกี่ยวอะไรกับ zero-downtime?** — มันเป็น gate ของ Service; ถ้าไม่มี Pod ถูกนับ Readyตั้งแต่ container เริ่ม แม้แอปยังไม่ฟัง port

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] baseline web v1 พร้อม 3 Pod
- [ ] เห็น ReplicaSet v1/v2 อยู่ร่วมกันระหว่าง rollout
- [ ] request loop ของ RollingUpdate/undo ไม่มี `FAIL`
- [ ] screenshot mixed, v2 และ after-undo มาจากหน้าเว็บจริง
- [ ] Recreate ทำให้เห็น `FAIL` ต่อเนื่องแล้ว
- [ ] ถอด readiness แล้วเห็น `FAIL` ประปรายและแก้คืนแล้ว
- [ ] อธิบายบทบาทของ maxSurge/maxUnavailable/readiness ได้
- [ ] Clean Re-run ผ่านและลบ namespace `lab018` แล้ว

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
