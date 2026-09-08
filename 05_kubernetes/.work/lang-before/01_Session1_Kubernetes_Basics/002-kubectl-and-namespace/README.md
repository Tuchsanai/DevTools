# LAB 2 — kubectl และ Namespace : หา object ให้ถูกห้อง
> โฟลเดอร์ `002-kubectl-and-namespace` = LAB 2 ของชุด Kubernetes ครั้งที่ 1
> (ไฟล์ของแล็บนี้: `README.md`; ไม่มี manifest เพราะสร้าง Namespace แบบ imperative เพื่อศึกษา object)

> 💡 **แนวคิดหลักของแล็บนี้:** ทุกอย่างใน Kubernetes คือ "object" ที่เราสั่งผ่าน kubectl และถูกจัดกลุ่มด้วย namespace

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายได้ว่า kubectl ส่งคำขอไปยัง Kubernetes API อย่างไร
2. อธิบายได้ว่า namespace ช่วยแยก object และชื่อไม่ให้ชนกันอย่างไร
3. แยก resource แบบ namespaced ออกจาก cluster-scoped ได้
4. อ่าน `get`, `describe`, `-o wide`, `-o yaml` และ `explain` เพื่อหาคำตอบด้วยตนเองได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

คำถามตั้งต้นคือ: LAB 001 เห็น Pod อยู่หลายตัว แต่พอพิมพ์ `kubectl get pods` กลับว่าง
Pod ไม่ได้หาย เราเพียงกำลังมองคนละ “ห้อง”

kubectl เป็น client ที่อ่าน context เพื่อเลือก cluster, user และ namespace แล้วส่งคำขอไป API server
สิ่งที่อ่านกลับมาคือ object เช่น Pod, Service, Deployment, Node และ Namespace

| มุมมอง | ความหมาย | เหมาะกับอะไร |
|---|---|---|
| `get` | ตารางสรุป object หลายตัว | มองอาการเร็ว |
| `describe` | รายละเอียดที่จัดให้อ่านง่ายพร้อม Events | วินิจฉัย object หนึ่งตัว |
| `-o wide` | ตารางที่เพิ่ม IP/NODE | ดูตำแหน่งและเครือข่าย |
| `-o yaml` | object ตาม API รวม spec/status | อ่านทุก field |

namespace คล้ายห้องในอาคารเดียวกัน: `web` ใน `lab002` กับ `web` ในอีก namespace ใช้ชื่อซ้ำได้
แต่ Node และ Namespace เป็นทรัพยากรระดับ cluster จึงไม่สังกัดห้องใด

## สิ่งที่จะได้เรียนรู้

- จะได้เห็นว่า namespace เริ่มต้นอาจว่าง แม้ cluster มี Pod จำนวนมาก
- จะได้ใช้ `-A` และ `-n` เพื่อเปลี่ยนขอบเขตการค้นหา
- จะได้อ่านคอลัมน์ IP และ NODE จาก `-o wide`
- จะได้พิสูจน์ว่า Namespace เองก็เป็น Kubernetes object
- จะได้เห็นโครง `apiVersion`, `kind`, `metadata`, `spec`, `status`
- จะได้ใช้ `kubectl explain` เป็นคู่มือที่ตรงกับ API version
- จะได้ทดลองตั้ง default namespace ผิด อ่านอาการ แล้วแก้กลับ
- จะได้รู้ว่า alias ช่วยพิมพ์สั้น แต่ไม่ได้เพิ่มความสามารถใหม่

## ภาพรวมของแล็บนี้

1. เทียบ Pod ใน default กับทุก namespace
2. เปิดห้อง `kube-system` แล้วดูแบบ wide
3. สำรวจชนิด object ที่ API รองรับ
4. อ่าน Pod เดียวด้วย describe และ YAML
5. สร้าง namespace `lab002` แล้วอ่าน object ของมัน
6. ใช้คู่มือในตัวและ alias
7. ตั้ง context ผิด ทดลองอาการ แล้วแก้กลับ

![ภาพสถาปัตยกรรม LAB 002: kubectl มอง object ที่แยกอยู่ใน namespace](../slides_assets/lab002-architecture.svg)
> **คำถามก่อนเริ่ม:** ถ้า cluster มี Pod อยู่จริง ทำไม `kubectl get pods` จึงตอบว่าไม่พบ resource ได้โดยไม่ถือว่าเป็น error?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกจากเครื่องหลัก จากนั้นเข้าเครื่องเรียนและพิมพ์ทุกคำสั่งหลังจากนั้นใน shell ที่เปิด:
```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** `docker start` เปิดเครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` ข้ามขั้นสร้างเองเมื่อ cluster มีอยู่แล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจจาก runtime ของ kind node

✅ **Expected output** — node พร้อม 3/3 และ image แอปครบ 4 tag:
```text
Set kubectl context to "kind-devtools"
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready   control-plane   13m   v1.36.4
devtools-worker          Ready   <none>          13m   v1.36.4
devtools-worker2         Ready   <none>          13m   v1.36.4
docker.io/library/k8s-lab-api   v1   c01adaec89c6d   186MB
docker.io/library/k8s-lab-db    v1   a5a8c986a5421   300MB
docker.io/library/k8s-lab-web   v1   34d144d726eda   209MB
docker.io/library/k8s-lab-web   v2   0bdb9ed2beecf   209MB
```
AGE, image ID และขนาดต่างกันได้ ถ้ายังไม่มี image ให้กลับไปทำขั้น build/load ของ LAB 001 หรือ README ระดับชุด

ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 เมื่อเรียก Ingress ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

## 1. Clone โค้ดแล็บ
```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/002-kubectl-and-namespace
pwd
```
> 📝 **คำอธิบาย:** `mkdir -p` เตรียม workspace · `&&` หยุดเมื่อขั้นก่อนหน้าล้ม · `git clone` ดึง repository · `cd` เลือก LAB 002 · `pwd` ป้องกันรันผิดโฟลเดอร์

✅ **Expected output** — clone สำเร็จและ path ลงท้ายด้วยโฟลเดอร์แล็บ:
```text
Cloning into 'DevTools'...
/root/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/002-kubectl-and-namespace
```
ถ้า clone แล้ว ให้ใช้ `cd ~/labwork/DevTools && git pull` แล้วกลับเข้าโฟลเดอร์นี้

## 2. อ่าน YAML ของแล็บนี้

แล็บนี้สร้าง Namespace ด้วยคำสั่งและอ่าน object ที่มีอยู่ จึงยังไม่มี manifest ในโฟลเดอร์

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| — ไม่มีไฟล์ `.yaml` | Namespace, Pod | เทียบ object เดียวในรูปตาราง, `describe` และ YAML | [ดู YAML_Guide.md → อ่าน YAML ให้เป็น](../YAML_Guide.md#อ่าน-yaml-ให้เป็น) |

`kubectl get namespace lab002 -o yaml` จะมี `apiVersion`, `kind`, `metadata`, `spec` และ `status`; รอบนี้สังเกตว่า `status` มาจากระบบ ไม่ใช่ field ที่เราต้องจำหรือเขียนสั่ง และอ่านเรื่องขอบเขต namespace ต่อได้ที่ [YAML_Guide.md → namespace ในไฟล์](../YAML_Guide.md#namespace-ในไฟล์)

**ผิดบ่อยในแล็บนี้:** runlog ไม่มี YAML error; `No resources found in lab002 namespace.` เป็นผลจริงที่บอกว่าเลือกห้องถูกแต่ห้องว่าง ไม่ใช่ YAML เสีย ส่วนข้อความตัวอย่างจากการวาง field ผิดระดับคือ `strict decoding error: unknown field ...` ให้ใช้ `kubectl explain namespace` ตรวจโครงก่อน

ดู schema ด้วย `kubectl explain namespace.metadata` และ `kubectl explain namespace.status`

## 3. Pod หายไปไหน

ตั้ง context กลับ default เพื่อให้ทุกคนเริ่มจากภาพเดียวกัน แล้วเทียบสองขอบเขต:
```bash
kubectl config set-context --current --namespace=default
kubectl get pods
kubectl get pods -A
kubectl get namespaces
```
> 📝 **คำอธิบาย:** `config set-context` แก้ context ปัจจุบัน · `--namespace=default` ตั้งห้องเริ่มต้น · `get pods` ค้นเฉพาะห้องนั้น · `-A` ค้นทุก namespace · `get namespaces` แสดงรายชื่อห้องใน cluster

✅ **Expected output** — default ว่าง แต่ `-A` พบ system Pod และ namespace หลัก:
```text
Context "kind-devtools" modified.
No resources found in default namespace.
NAMESPACE       NAME                                      READY   STATUS
ingress-nginx   ingress-nginx-controller-5d9bb85749-hczf6 1/1     Running
kube-system     coredns-589f44dc88-kfjdg                  1/1     Running
kube-system     metrics-server-55c6b8755f-ngbgr           1/1     Running

NAME                 STATUS   AGE
default              Active   13m
ingress-nginx        Active   12m
kube-system          Active   13m
local-path-storage   Active   13m
```
ชื่อ Pod, hash, AGE และจำนวน restart ต่างกันได้ คำว่า “No resources” ไม่ใช่ error แต่บอกขอบเขตที่ค้น
(แสดงบางแถวจากตาราง Pod และ Namespace)

## 4. เปลี่ยนห้องและเพิ่มรายละเอียด
```bash
kubectl get pods -n kube-system
kubectl get pods -n kube-system -o wide
```
> 📝 **คำอธิบาย:** `-n kube-system` เลือก namespace ชัดเจนโดยไม่เปลี่ยน context · `-o wide` เพิ่ม IP, NODE, nominated node และ readiness gates · เทียบชื่อ Pod เดิมระหว่างสองตาราง

✅ **Expected output** — ตาราง wide เพิ่มตำแหน่งที่ Pod รัน:
```text
NAME                              READY   STATUS    IP           NODE
coredns-589f44dc88-kfjdg          1/1     Running   10.244.0.3   devtools-control-plane
kindnet-72znx                     1/1     Running   172.18.0.3   devtools-worker2
metrics-server-55c6b8755f-ngbgr   1/1     Running   10.244.2.2   devtools-worker2
```
ชื่อ Pod, IP, NODE, AGE และ restart ต่างกันได้

## 5. พิสูจน์ว่า API เต็มไปด้วย object
```bash
kubectl api-resources | head -30
```
> 📝 **คำอธิบาย:** `api-resources` ถาม discovery API ว่ารองรับ resource ใด · `head -30` จำกัดสามสิบบรรทัดแรก · อ่าน `SHORTNAMES`, `APIVERSION`, `NAMESPACED`, `KIND` ให้ครบ

✅ **Expected output** — พบทั้ง object แบบอยู่ใน namespace และแบบระดับ cluster:
```text
NAME          SHORTNAMES   APIVERSION   NAMESPACED   KIND
configmaps    cm           v1           true         ConfigMap
namespaces    ns           v1           false        Namespace
nodes         no           v1           false        Node
pods          po           v1           true         Pod
services      svc          v1           true         Service
deployments   deploy       apps/v1      true         Deployment
replicasets   rs           apps/v1      true         ReplicaSet
```
ลำดับและชนิด API อาจต่างกันเมื่อ Kubernetes version เปลี่ยน

## 6. อ่าน object เดียวสองรูปแบบ

เลือก ingress controller ด้วย label แล้วอ่านแบบ describe และ YAML:
```bash
POD=$(kubectl get pod -n ingress-nginx -l app.kubernetes.io/component=controller -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod -n ingress-nginx "$POD" | head -35
kubectl get pod -n ingress-nginx "$POD" -o yaml | head -40
```
> 📝 **คำอธิบาย:** `-l` เลือก Pod ด้วย label · `-o jsonpath` ดึงชื่อจริง · ตัวแปร `POD` กันการคัดลอก hash · `describe` จัดข้อมูลเพื่อวินิจฉัย · `-o yaml` แสดงโครง API · `head` จำกัดส่วนต้นที่ใช้เรียน

✅ **Expected output** — object เดียวกันแสดง identity และสี่ส่วนหลัก:
```text
Name:             ingress-nginx-controller-5d9bb85749-hczf6
Namespace:        ingress-nginx
Node:             devtools-control-plane/172.18.0.4
Status:           Running
Controlled By:    ReplicaSet/ingress-nginx-controller-5d9bb85749

apiVersion: v1
kind: Pod
metadata:
  name: ingress-nginx-controller-5d9bb85749-hczf6
  namespace: ingress-nginx
spec:
  containers:
```
ชื่อ, hash, IP, UID, resourceVersion และเวลาต่างกันได้ `status` อยู่ช่วงท้ายของ YAML ที่ถูกตัดออก

## 7. สร้าง Namespace แล้วอ่านกลับเป็น object
```bash
kubectl create namespace lab002
kubectl get ns lab002 -o yaml
```
> 📝 **คำอธิบาย:** `create namespace` สร้าง object แบบ imperative · `lab002` คือชื่อห้องของแล็บ · `get ns` ใช้ shortname ของ Namespace · `-o yaml` แสดงค่าที่ API server เก็บและเติมให้

✅ **Expected output** — namespace ถูกสร้างและสถานะเป็น `Active`:
```text
namespace/lab002 created
apiVersion: v1
kind: Namespace
metadata:
  labels:
    kubernetes.io/metadata.name: lab002
  name: lab002
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
```
creationTimestamp, resourceVersion และ UID ต่างกันได้

## 8. ใช้คู่มือและ alias ในเครื่องเรียน
```bash
kubectl explain pod.spec.containers | head -20
alias k kgp kgn
kubectl get pods -A --field-selector status.phase=Running | wc -l
```
> 📝 **คำอธิบาย:** `explain` อ่าน schema จาก API ที่ใช้อยู่ · path แบบจุดเดินจาก Pod ไป `spec.containers` · `alias` แสดงคำย่อ `k`, `kgp`, `kgn` · `--field-selector` กรอง phase ฝั่ง API · `wc -l` นับบรรทัดรวม header

✅ **Expected output** — คู่มือบอกว่า Pod ต้องมี container อย่างน้อยหนึ่งตัว, alias ชี้ไป kubectl และพบ 16 บรรทัดในรอบทดสอบ:
```text
KIND:       Pod
VERSION:    v1
FIELD: containers <[]Container>
DESCRIPTION:
    List of containers belonging to the pod. Containers cannot currently be
    added or removed. There must be at least one container in a Pod. Cannot be
    updated.
    A single application container that you want to run within a pod.
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgn='kubectl get nodes'
16
```
จำนวน Running Pod ต่างกันได้ และ `wc -l` นับ header อีกหนึ่งบรรทัด

## 9. ทดลองให้พัง — มองผิด namespace

ตั้ง default namespace เป็นห้องว่าง แต่สั่งแบบระบุ `-n` เพื่อเทียบผล:
```bash
kubectl config set-context --current --namespace=lab002
kubectl get pods -n kube-system | head -5
kubectl get pods
```
> 📝 **คำอธิบาย:** `set-context --current` เปลี่ยน default ของคำสั่งถัดไป · `-n kube-system` มีสิทธิ์เหนือค่า default จึงยังเจอ Pod · คำสั่งสุดท้ายไม่มี `-n` จึงค้นใน `lab002`

✅ **Expected output** — คำสั่งแรกเจอ system Pod แต่คำสั่งสุดท้ายบอกชัดว่าค้นใน `lab002`:
```text
Context "kind-devtools" modified.
NAME                              READY   STATUS
coredns-589f44dc88-kfjdg          1/1     Running
coredns-589f44dc88-v67bc          1/1     Running
etcd-devtools-control-plane       1/1     Running
No resources found in lab002 namespace.
```
ชื่อ Pod, hash และ AGE ต่างกันได้ อาการนี้แปลว่า “ห้องนี้ว่าง” ไม่ได้แปลว่า cluster พัง

แก้ context กลับทันที เพื่อไม่ให้ LAB ถัดไปหลงห้อง:
```bash
kubectl config set-context --current --namespace=default
kubectl config view --minify | grep namespace
```
> 📝 **คำอธิบาย:** คำสั่งแรกคืน default namespace · `config view` แสดง config ที่มีผล · `--minify` เหลือ context ปัจจุบัน · `grep namespace` เลือกบรรทัดพิสูจน์

✅ **Expected output** — context กลับสู่ default:
```text
Context "kind-devtools" modified.
    namespace: default
```

## 10. แบบฝึกหัดสั้น (Exercise)

เลือก resource จากผล `api-resources` สามชนิด แล้วจัดลงสองกลุ่ม: namespaced กับ cluster-scoped
จากนั้นอธิบายว่าทำไม Node ไม่ควรถูกซ่อนไว้ใน namespace ของทีมใดทีมหนึ่ง

ถือว่าสำเร็จเมื่ออ่านค่าจากคอลัมน์ `NAMESPACED` เป็นหลักฐาน และยกตัวอย่างอย่างน้อยกลุ่มละหนึ่งชนิด

## วิธีตรวจสอบผลการทดลอง

ตรวจทั้ง object, log และ event:
```bash
kubectl get ns lab002 -o jsonpath='{.metadata.name}{"  "}{.status.phase}{"\n"}'
POD=$(kubectl get pod -n ingress-nginx -l app.kubernetes.io/component=controller -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n ingress-nginx "$POD" --tail=3
kubectl get events -n lab002 --sort-by=.lastTimestamp
```
> 📝 **คำอธิบาย:** JSONPath พิมพ์ชื่อและ phase จริงโดยไม่แต่ง AGE · label/JSONPath หา Pod จริง · `logs --tail=3` อ่านสามบรรทัดท้ายจาก ingress controller · `get events -n lab002` ตรวจว่าห้องว่างไม่มีเหตุผิดปกติ

✅ **Expected output** — namespace Active, controller sync สำเร็จ และ lab002 ยังไม่มี event:
```text
lab002  Active
I0902 16:34:06.152989      11 controller.go:231] "Backend successfully reloaded"
I0902 16:34:06.153103      11 controller.go:243] "Initial sync, sleeping for 1 second"
I0902 16:34:06.153163      11 event.go:377] Event(v1.ObjectReference{Kind:"Pod", Namespace:"ingress-nginx", Name:"ingress-nginx-controller-5d9bb85749-hczf6", UID:"dfd7752e-702f-484d-9efb-6134b9fc1b3a", APIVersion:"v1", ResourceVersion:"800", FieldPath:""}): type: 'Normal' reason: 'RELOAD' NGINX reload triggered due to a change in configuration
No resources found in lab002 namespace.
```
ชื่อ Pod, UID, resourceVersion และ timestamp ใน log ต่างกันได้

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `No resources found` ทั้งที่จำได้ว่ามี Pod | มองผิด namespace | เติม `-A` หรือ `-n <namespace>` |
| `NotFound` เมื่อ describe ชื่อที่คัดลอกไว้ | Pod ถูกสร้างใหม่และ hash เปลี่ยน | หาใหม่ด้วย label/JSONPath |
| `-o wide` ไม่เห็น field ทุกตัว | wide เป็นเพียงตารางเสริม | ใช้ `-o yaml` หรือ `describe` |
| เปลี่ยน context แล้วแล็บถัดไปหา object ไม่เจอ | default namespace ยังเป็น `lab002` | ตั้งกลับ `--namespace=default` |
| `explain` หา field ไม่เจอ | path หรือชนิด resource สะกดผิด | ไล่ทีละระดับจาก `kubectl explain pod` |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

แล็บนี้ไม่มี manifest จึงทำ Clean Re-run ด้วยคำสั่ง imperative เดิม: ลบทั้งห้อง สร้างใหม่ ตรวจผล แล้วลบปิดท้าย
```bash
kubectl delete namespace lab002 --wait=true --timeout=60s
kubectl create namespace lab002
kubectl get ns lab002 -o jsonpath='{.metadata.name}{"  "}{.status.phase}{"\n"}'
kubectl get all -n lab002
kubectl delete namespace lab002 --wait=true --timeout=60s
kubectl get all -n lab002
```
> 📝 **คำอธิบาย:** `delete namespace` ลบทั้งห้อง · `--wait=true` รอจนเสร็จ · `--timeout=60s` กันคำสั่งค้าง · `create` ทำซ้ำจากจุดสะอาด · `jsonpath` พิมพ์ชื่อ/phase · `get all` พิสูจน์ว่าไม่มี workload · การลบครั้งสุดท้ายกัน resource ชน LAB 003

✅ **Expected output** — สร้างซ้ำได้เหมือนเดิม แล้วไม่เหลือ resource:
```text
namespace "lab002" deleted
namespace/lab002 created
lab002  Active
No resources found in lab002 namespace.
namespace "lab002" deleted
No resources found in lab002 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get pods -A` | ดู Pod ทุก namespace |
| `kubectl get pods -n NAME` | ดู Pod ใน namespace ที่เลือก |
| `kubectl get ... -o wide` | เพิ่ม IP และ NODE ในตาราง |
| `kubectl get ... -o yaml` | ดู object เต็มตาม API |
| `kubectl describe ...` | ดูรายละเอียดและ Events แบบอ่านง่าย |
| `kubectl api-resources` | ดู resource ที่ API รองรับ |
| `kubectl explain PATH` | อ่าน schema/คำอธิบาย field |
| `kubectl config set-context --current --namespace=NAME` | เปลี่ยน namespace เริ่มต้น |
| `kubectl create/delete namespace NAME` | สร้าง/ลบกลุ่ม object ทั้งห้อง |

## สรุปสิ่งที่ได้เรียนรู้

kubectl ไม่ได้ค้น “ทุกอย่าง” โดยอัตโนมัติ แต่ส่งคำขอภายใต้ context และ namespace ที่กำหนด
การอ่านข้อความที่บอก namespace จึงสำคัญกว่าการรีบสรุปว่า resource หาย

- อธิบายเส้นทาง kubectl → context → API server ได้
- แยก namespaced object กับ cluster-scoped object ได้
- เลือก `get`, `describe`, wide, YAML และ explain ตามคำถามได้
- ทดลองมองผิด namespace แล้วแก้ context กลับได้

**จำภาพเดียวให้ได้:** namespace คือห้อง—ของยังอยู่ในอาคาร แม้เราจะเปิดผิดประตูแล้วมองไม่เห็น

🧭 ต่อยอด: ไปที่ [LAB 003 — Pod หน่วยเล็กที่สุด](../003-pod-the-smallest-unit/README.md) เพื่อสร้าง object ของแอปจริงใน namespace ของเรา

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **namespace มีไว้ทำไม?**  
   แนวคำตอบ: แยกกลุ่ม object/ชื่อ/สิทธิ์/โควตา และลบทั้งกลุ่มได้ในครั้งเดียว
2. **ทำไมบางทีหา resource ไม่เจอ?**  
   แนวคำตอบ: มองผิด namespace หรือ resource นั้นเป็น cluster-scoped จึงไม่อยู่ใน namespace ใด
3. **`-o wide` กับ `-o yaml` ต่างกันอย่างไร?**  
   แนวคำตอบ: wide เพิ่มคอลัมน์ที่คนใช้บ่อย ส่วน YAML แสดง object เต็มรวม spec/status และค่าที่ระบบเติม

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] แยกผลของ `get pods` กับ `get pods -A` ได้
- [ ] ใช้ `-n kube-system` และ `-o wide` ได้
- [ ] อ่านคอลัมน์ `NAMESPACED` จาก api-resources ได้
- [ ] หา ingress Pod ด้วย label แทนการจำ hash ได้
- [ ] เห็น Namespace เป็น object แบบ YAML
- [ ] อธิบายอาการมองผิด namespace ได้
- [ ] context กลับเป็น `default`
- [ ] ลบ `lab002` และยืนยันว่าไม่เหลือ resource

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
