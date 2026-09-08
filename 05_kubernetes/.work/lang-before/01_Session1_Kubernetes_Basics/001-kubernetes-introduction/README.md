# LAB 1 — Kubernetes Introduction : จากเครื่องเดียวสู่ผู้ดูแล cluster
> โฟลเดอร์ `001-kubernetes-introduction` = LAB 1 ของชุด Kubernetes ครั้งที่ 1
> (ไฟล์ของแล็บนี้: `README.md`; แล็บนี้ยังไม่มี manifest เพราะสำรวจ cluster ที่มีอยู่แล้ว)

> 💡 **แนวคิดหลักของแล็บนี้:** Kubernetes คือผู้ดูแลที่คอยรันแอปให้ตรงกับที่เราสั่งไว้เสมอ แม้เครื่องจะพังหรือแอปจะตาย

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายได้ว่า Kubernetes แก้ข้อจำกัดของระบบที่รันด้วย Docker Compose บนเครื่องเดียวอย่างไร
2. อธิบายบทบาทที่ต่างกันของ control plane และ worker node ได้
3. อ่านหลักฐานพื้นฐานจาก `kubectl get`, `kubectl describe`, logs และ events ได้
4. อธิบายได้ว่าทำไม image ที่ build ในเครื่องเรียนต้อง load เข้า kind node ก่อนใช้งาน

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ลองนึกถึง SkillSpace ที่รันด้วย Docker Compose: ถ้าเครื่องเดียวดับ ทุก service ก็ดับตาม; ถ้าต้องเปิด web 10 ตัวบน 3 เครื่อง เราต้องเลือกเครื่อง เฝ้า process และสั่งเปิดใหม่เอง ปัญหาจึงไม่ใช่แค่ “เปิด container อย่างไร” แต่คือ “ใครเฝ้าระบบตลอดเวลา”

Kubernetes เพิ่ม control plane เป็นสมองกลาง ส่วน worker node รับงานไปทำ; ผู้ใช้ส่งคำขอผ่าน API server แล้ว scheduler/controller คอยเทียบสภาพจริงกับสภาพที่ต้องการ

| มุมมอง | Docker Compose | Kubernetes |
|---|---|---|
| ขอบเขตหลัก | เครื่องเดียว | หลาย node ใน cluster |
| ผู้เก็บ desired state | ไฟล์อยู่กับผู้ใช้ | API server และ etcd |
| ผู้เฝ้าและแก้ส่วนต่าง | ผู้ใช้/สคริปต์ | controller |
| เมื่อเครื่องหาย | ระบบไม่รู้จักเครื่องอื่น | control plane เห็น node เป็น `NotReady` |
| หน่วยงาน | container/service | Pod และ object ชนิดต่าง ๆ |

ในห้องเรียนนี้ kind จำลอง node แต่ละเครื่องด้วย Docker container แต่ยังใช้ Kubernetes API และกลไกควบคุมจริง

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น cluster จริงที่มี 1 control-plane และ 2 worker
- จะได้พิสูจน์ว่า `kubectl` ติดต่อ API server และรายงานเวอร์ชันทั้ง client/server
- จะได้อ่านว่า system Pod ใดเป็น “ลูกน้อง” ที่ทำให้ cluster ทำงาน
- จะได้ build และ load image SkillSpace สำหรับใช้ต่อทั้งชุด
- จะได้เห็น control plane ตรวจพบ worker ที่หยุดทำงาน
- จะได้พิสูจน์ว่า worker กลับมา `Ready` ได้หลังเปิดคืน

## ภาพรวมของแล็บนี้

1. เปิดเครื่องเรียนและ bootstrap cluster
2. ตรวจ API server, version และ node
3. สำรวจ system Pod และรายละเอียด worker
4. build/load image ของ SkillSpace
5. หยุด worker2 อ่านอาการ แล้วเปิดกลับ
6. ตรวจหลักฐานและเก็บกวาด

![ภาพสถาปัตยกรรม LAB 001: kubectl ติดต่อ control plane ซึ่งดูแล worker node](../slides_assets/lab001-architecture.svg)
> **คำถามก่อนเริ่ม:** ถ้า worker node หายไปหนึ่งเครื่อง control plane จะรู้หรือไม่ และเราจะเห็นหลักฐานนั้นจากตรงไหน?

## 0. เตรียมเครื่องเรียน

รันจากเครื่องหลัก คำสั่งแรกจะเปิดเครื่องเดิมถ้ามีอยู่ หรือสร้างใหม่เมื่อยังไม่มี แล้วรอให้ Docker daemon ภายในพร้อม:
```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
until docker exec devtools-k8s docker info >/dev/null 2>&1; do sleep 2; done
```
> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิมโดยไม่ลบงาน · `||` สร้าง container เมื่อยังไม่มี · option ที่เหลือเตรียม Docker-in-Docker, resource limit และ port mapping · loop เรียก `docker info` ทุก 2 วินาทีเพื่อกันการ bootstrap เร็วกว่าที่ daemon พร้อม

✅ **Expected output** — ได้ชื่อ `devtools-k8s` หรือ container ID 64 ตัว; คำสั่งรอจบโดยไม่แสดงข้อความ:
```text
devtools-k8s
```
ค่าจริงอาจเป็น container ID และต่างกันทุกเครื่อง

เข้าเครื่องเรียน แล้วพิมพ์ทุกคำสั่งหลังจากนี้ใน shell นี้:
```bash
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster ครั้งแรกและข้ามขั้นสร้างเองเมื่อมี cluster แล้ว โดยอาจใช้เวลาหลายนาที · `get nodes` ตรวจ node · `crictl images` ตรวจ image จากมุมของ node จริง

✅ **Expected output** — bootstrap ตั้ง context สำเร็จและ node ทั้งสามเป็น `Ready`; รอบแรกที่ยังไม่เห็น image เป็นเรื่องปกติ ให้ทำขั้น build/load ในหัวข้อ 6:
```text
Set kubectl context to "kind-devtools"
NAME                     STATUS   ROLES           AGE     VERSION
devtools-control-plane   Ready    control-plane   5m14s   v1.36.4
devtools-worker          Ready    <none>          5m5s    v1.36.4
devtools-worker2         Ready    <none>          5m5s    v1.36.4
docker.io/library/k8s-lab-api   v1   c01adaec89c6d   186MB
docker.io/library/k8s-lab-db    v1   a5a8c986a5421   300MB
docker.io/library/k8s-lab-web   v1   34d144d726eda   209MB
docker.io/library/k8s-lab-web   v2   0bdb9ed2beecf   209MB
```
ค่า `AGE`, image ID และขนาดอาจต่างกันได้

ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 เมื่อเรียก Ingress ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

## 1. Clone โค้ดแล็บ
```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/001-kubernetes-introduction
pwd
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace ถ้ายังไม่มี · `&&` ไปต่อเมื่อคำสั่งก่อนหน้าสำเร็จ · `git clone` ดาวน์โหลด repository · `cd` เข้า LAB 001 · `pwd` ยืนยันตำแหน่งก่อนรันคำสั่ง

✅ **Expected output** — clone สำเร็จและอยู่ในโฟลเดอร์ LAB 001:
```text
Cloning into 'DevTools'...
/root/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/001-kubernetes-introduction
```
ถ้า clone ไว้แล้ว ไม่ต้อง clone ซ้ำ ให้รัน `cd ~/labwork/DevTools && git pull` แล้วกลับเข้าโฟลเดอร์แล็บ

## 2. อ่าน YAML ของแล็บนี้

แล็บนี้สำรวจ object ที่ cluster สร้างไว้แล้ว จึงไม่มีไฟล์ `.yaml` ให้ apply แต่เรายังอ่านโครง object จริงด้วย `kubectl get ... -o yaml` ได้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| — ไม่มีไฟล์ `.yaml` | Node และ system Pod มาจาก cluster | อ่าน actual state โดยไม่สร้าง manifest | [ดู YAML_Guide.md → อ่าน YAML ให้เป็น](../YAML_Guide.md#อ่าน-yaml-ให้เป็น) |

ลองเทียบ `kubectl get node devtools-worker -o yaml` กับตารางในคู่มือ: `metadata` บอกตัวตน, `spec` คือค่าที่ระบบใช้ และ `status` คือสิ่งที่ kubelet/controller รายงานกลับ อย่าคัด `status` ไปเป็น desired state

**ผิดบ่อยในแล็บนี้:** runlog ไม่มี YAML validation error เพราะแล็บนี้ไม่มี manifest; ข้อความตัวอย่างเมื่อระบุไฟล์ที่ไม่มีคือ `error: the path "node.yaml" does not exist` จึงควรเช็ก `pwd` และแยกคำสั่งอ่าน object (`get -o yaml`) ออกจากคำสั่ง apply ไฟล์

ดู schema ที่ใช้ในแล็บนี้ด้วย `kubectl explain node.spec` และ `kubectl explain node.status.conditions`

## 3. ถาม cluster ว่า control plane อยู่ที่ไหน
```bash
kubectl cluster-info
kubectl version
```
> 📝 **คำอธิบาย:** `cluster-info` แสดง endpoint หลักที่ context ปัจจุบันชี้อยู่ · `version` แสดงเวอร์ชัน client ของ kubectl และ server ของ Kubernetes · เวอร์ชันต่างกันเล็กน้อยได้เพราะสื่อสารผ่าน API ที่รองรับกัน

✅ **Expected output** — ติดต่อ control plane ได้ และเห็น client v1.37.0/server v1.36.4:
```text
Kubernetes control plane is running at https://127.0.0.1:40417
CoreDNS is running at https://127.0.0.1:40417/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

Client Version: v1.37.0
Server Version: v1.36.4
```
เลข port ของ API server ต่างกันได้

## 4. มอง node จากสองมุม
```bash
kubectl get nodes -o wide
docker ps
```
> 📝 **คำอธิบาย:** `get nodes` อ่าน object ชนิด Node · `-o wide` เพิ่ม IP, OS และ runtime · `docker ps` แสดง container ที่รันอยู่ในเครื่องเรียน · ชื่อ `devtools-*` ทำให้จับคู่สองมุมได้

✅ **Expected output** — Kubernetes เห็นสาม node และ Docker เห็น kind container สามตัวชื่อเดียวกัน:
```text
NAME                     STATUS   ROLES           VERSION   INTERNAL-IP   CONTAINER-RUNTIME
devtools-control-plane   Ready    control-plane   v1.36.4   172.18.0.4    containerd://2.3.4
devtools-worker          Ready    <none>          v1.36.4   172.18.0.2    containerd://2.3.4
devtools-worker2         Ready    <none>          v1.36.4   172.18.0.3    containerd://2.3.4

IMAGE                  NAMES
kindest/node:v1.36.4   devtools-worker2
…
```
ค่า IP, AGE, container ID และลำดับแถวต่างกันได้ (ตัดบางแถวจาก `docker ps`)

## 5. สำรวจ “ลูกน้อง” ที่ทำให้ cluster ทำงาน
```bash
kubectl get pods -A
```
> 📝 **คำอธิบาย:** `get pods` อ่าน Pod · `-A` หรือ `--all-namespaces` ขยายมุมมองจาก namespace ปัจจุบันไปทุก namespace · สังเกต CoreDNS, API server, scheduler, controller, metrics-server และ ingress controller

✅ **Expected output** — system Pod หลักเป็น `Running`:
```text
NAMESPACE            NAME                                             READY   STATUS
ingress-nginx        ingress-nginx-controller-5d9bb85749-hczf6        1/1     Running
kube-system          coredns-589f44dc88-kfjdg                         1/1     Running
kube-system          etcd-devtools-control-plane                      1/1     Running
kube-system          kube-apiserver-devtools-control-plane            1/1     Running
…
```
ชื่อ Pod ต่อท้าย hash และ AGE ต่างกันได้ (ตัดบางแถว)

## 6. อ่านรายละเอียด worker หนึ่งเครื่อง
```bash
kubectl describe node devtools-worker | head -40
```
> 📝 **คำอธิบาย:** `describe node` รวมข้อมูลที่มนุษย์ใช้วินิจฉัย · `devtools-worker` คือ object เป้าหมาย · `head -40` จำกัดให้เริ่มจาก identity, label, taint, lease, Conditions และ capacity

✅ **Expected output** — Condition `Ready=True` และไม่มี Memory/Disk/PID pressure:
```text
Name:               devtools-worker
Roles:              <none>
Unschedulable:      false
Conditions:
  Type             Status  Reason
  MemoryPressure   False   KubeletHasSufficientMemory
  DiskPressure     False   KubeletHasNoDiskPressure
  PIDPressure      False   KubeletHasSufficientPID
  Ready            True    KubeletReady
…
```
เวลา, CPU และ RAM ต่างกันได้ตามเครื่อง (ตัดข้อความท้ายหลัง Conditions)

## 7. เตรียม image ของ SkillSpace สำหรับทั้งชุด

build image ทั้งสี่จากแอปที่ผ่านการตรวจแล้ว:
```bash
cd ~/labwork/DevTools/05_kubernetes/app
./build-images.sh
```
> 📝 **คำอธิบาย:** `cd` เข้า source ของแอปกลาง · `build-images.sh` build web v1/v2, API v1 และ DB v1 ด้วย tag ที่แล็บอื่นอ้างถึง · ขั้นนี้ทำครั้งเดียวตอนต้นชุดและใช้เวลาประมาณ 3–5 นาที

✅ **Expected output** — ท้าย build มี image ครบสี่ tag:
```text
k8s-lab-api:v1   c01adaec89c6   181MB
k8s-lab-db:v1    a5a8c986a542   297MB
k8s-lab-web:v1   34d144d726ed   205MB
k8s-lab-web:v2   0bdb9ed2beec   205MB
```
image ID, ขนาด และเวลาที่ build ต่างกันได้

load image เข้า node ทั้งสามแล้วตรวจจาก control-plane:
```bash
kind load docker-image k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 --name devtools
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** `kind load docker-image` คัดลอก local image เข้า node · รายชื่อสี่ image ตามด้วย tag · `--name devtools` เลือก cluster ให้ถูก · `docker exec` เข้า control-plane · `crictl images` ถาม container runtime ของ node · `grep` เหลือเฉพาะ image แล็บ

✅ **Expected output** — runtime ใน node มองเห็น image ครบ:
```text
Image: "k8s-lab-web:v1" with ID "sha256:34d144d726eda34af4b53fe67378ac193987443d8d326b53b2662b05557eb72a" not yet present on node "devtools-worker2", loading...
…
docker.io/library/k8s-lab-api   v1   c01adaec89c6d   186MB
docker.io/library/k8s-lab-db    v1   a5a8c986a5421   300MB
docker.io/library/k8s-lab-web   v1   34d144d726eda   209MB
docker.io/library/k8s-lab-web   v2   0bdb9ed2beecf   209MB
```
image ID และขนาดต่างกันได้ นี่คือคนละ image store กับ dockerd ชั้นนอก (ตัดข้อความการ load ของ node อื่น)

## 8. ทดลองให้พัง — หยุด worker node

เปิด Terminal แรกค้างไว้เพื่อดูการเปลี่ยนสถานะ:
```bash
kubectl get nodes -w
```
> 📝 **คำอธิบาย:** `get nodes` แสดง node · `-w` หรือ `--watch` ไม่จบคำสั่ง แต่รอ event ใหม่จาก API server · กด `Ctrl+C` เมื่อทดลองเสร็จ

✅ **Expected output** — ตอนเริ่มทั้งสาม node ยัง `Ready`:
```text
NAME                     STATUS   ROLES           AGE    VERSION
devtools-control-plane   Ready    control-plane   5m47s  v1.36.4
devtools-worker          Ready    <none>          5m38s  v1.36.4
devtools-worker2         Ready    <none>          5m38s  v1.36.4
```
เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้ง จากนั้นหยุด worker2 และรอสถานะให้เปลี่ยนอย่างชัดเจน:
```bash
docker stop devtools-worker2
kubectl wait --for=condition=Ready=false node/devtools-worker2 --timeout=90s
kubectl get nodes
kubectl describe node devtools-worker2 | sed -n '/Conditions:/,/Addresses:/p'
```
> 📝 **คำอธิบาย:** `docker stop` จำลองเครื่อง worker หาย · `wait` รอ `Ready=false` แทนการรีบอ่านสถานะเดิม · `get nodes` อ่านสถานะที่ control plane รับรู้ · `describe` เปิด Conditions และสาเหตุ

✅ **Expected output** — worker2 เป็น `NotReady` และ kubelet หยุดส่งสถานะ:
```text
devtools-worker2   NotReady   <none>   7m2s   v1.36.4

Conditions:
  Type             Status    Reason              Message
  MemoryPressure   Unknown   NodeStatusUnknown   Kubelet stopped posting node status.
  DiskPressure     Unknown   NodeStatusUnknown   Kubelet stopped posting node status.
  PIDPressure      Unknown   NodeStatusUnknown   Kubelet stopped posting node status.
  Ready            Unknown   NodeStatusUnknown   Kubelet stopped posting node status.
```
AGE และเวลาต่างกันได้ สถานะ `Unknown` แปลว่า control plane ติดต่อ kubelet ไม่ได้ ไม่ได้แปลว่ารู้แน่ชัดว่าฮาร์ดแวร์เสีย

แก้กลับด้วยการเปิด worker2 และรอ Condition:
```bash
docker start devtools-worker2
kubectl wait --for=condition=Ready=True node/devtools-worker2 --timeout=90s
kubectl get nodes
```
> 📝 **คำอธิบาย:** `docker start` เปิด node เดิม · `kubectl wait` รอเงื่อนไขแทนการเดาเวลา · `--for=condition=Ready=True` ระบุผลที่ต้องการ · `--timeout=90s` ป้องกันรอไม่จบ · `get nodes` ยืนยันภาพรวมอีกครั้ง

✅ **Expected output** — Condition ผ่านและ worker2 กลับเป็น `Ready`:
```text
devtools-worker2
node/devtools-worker2 condition met
NAME                     STATUS   ROLES           AGE     VERSION
devtools-control-plane   Ready    control-plane   7m22s   v1.36.4
devtools-worker          Ready    <none>          7m13s   v1.36.4
devtools-worker2         Ready    <none>          7m13s   v1.36.4
```
AGE ต่างกันได้ ส่วนหน้าต่าง watch จะเห็น `Ready → NotReady → Ready` จริง

อ่าน logs และ events หลังเหตุการณ์:
```bash
kubectl -n kube-system logs deploy/metrics-server --tail=5
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp | tail -10
```
> 📝 **คำอธิบาย:** `logs` อ่านเสียงจาก metrics-server · ตาราง `-o wide` ใช้ตรวจว่า Pod ใดอยู่บน `devtools-worker2` · events เรียงตามเวลาล่าสุด; หลักฐาน restart ด้านล่างเกิดเมื่อ metrics-server อยู่บน worker2 ที่หยุด

✅ **Expected output** — logs กลับมา sync และ events บันทึกผลกระทบชั่วคราวพร้อมการเริ่มใหม่:
```text
I0902 16:40:29.289774 1 shared_informer.go:409] "Caches are synced"
I0902 16:40:29.289781 1 shared_informer.go:409] "Caches are synced"

kube-system   metrics-server-55c6b8755f-ngbgr   1/1   Running   2 (59s ago)   8m25s   10.244.2.2   devtools-worker2
…
kube-system   60s   Warning   Unhealthy   pod/metrics-server-55c6b8755f-ngbgr   Liveness probe failed
kube-system   50s   Normal    Killing     pod/metrics-server-55c6b8755f-ngbgr   Container metrics-server failed liveness probe, will be restarted
kube-system   44s   Normal    Started     pod/metrics-server-55c6b8755f-ngbgr   Container started
```
ชื่อ Pod, เวลา และจำนวน restart ต่างกันได้ (ตัดบางแถว/บางคอลัมน์และข้อความท้าย) หาก metrics-server อยู่ node อื่น จะไม่เห็น restart ชุดนี้ ให้เลือกอ่าน Pod ระบบที่อยู่บน worker2 แทน

## 9. แบบฝึกหัดสั้น (Exercise)

เลือก system Pod หนึ่งตัวจากหัวข้อ 4 แล้วตอบโดยไม่ copy คำสั่งใหม่:

- Pod นั้นอยู่ namespace ใดและตกอยู่บน node ใด
- ชื่อของมันบอกบทบาทอะไร
- ถ้า node ที่มันอยู่หาย คุณคาดว่าจะเห็นหลักฐานแรกตรงไหน

ถือว่าสำเร็จเมื่อชี้หลักฐานจากตาราง Pod, node และ events ได้ครบ โดยไม่ตอบจากการเดาชื่อ component

## วิธีตรวจสอบผลการทดลอง

รันชุดตรวจเดียวหลังแก้ worker กลับแล้ว:
```bash
kubectl get nodes
kubectl -n kube-system get deploy,pod | grep metrics-server
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** คำสั่งแรกยืนยันสุขภาพ node · คำสั่งที่สองยืนยัน metrics-server ทั้ง Deployment และ Pod · คำสั่งสุดท้ายยืนยัน image store ของ node สำหรับแล็บถัดไป

✅ **Expected output** — node พร้อม 3/3, metrics-server พร้อม 1/1 และ image ครบ 4 tag:
```text
devtools-control-plane   Ready   control-plane   8m3s    v1.36.4
devtools-worker          Ready   <none>          7m54s   v1.36.4
devtools-worker2         Ready   <none>          7m54s   v1.36.4
deployment.apps/metrics-server   1/1   1   1   8m25s
pod/metrics-server-55c6b8755f-ngbgr   1/1   Running   2 (59s ago)   8m25s
docker.io/library/k8s-lab-web   v1
…
```
ชื่อ Pod, AGE, restart และ image ID ต่างกันได้ (ตัดบางแถว/บางคอลัมน์)

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `The connection to the server localhost:8080 was refused` | bootstrap ยังไม่เสร็จหรือ context ยังไม่ถูกสร้าง | รอคำสั่งเดิมให้จบ แล้วตรวจ context `kind-devtools` |
| worker ยัง `Ready` ทันทีหลัง stop | control plane ต้องรอ heartbeat หมดอายุ | เฝ้าด้วย `-w` ประมาณ 40–60 วินาที |
| metrics-server restart หลัง worker หาย | probe ติดต่อ node ที่หยุดไม่ได้ชั่วคราว | เปิด worker กลับ แล้วตรวจ Deployment พร้อม 1/1 |
| image ไม่ปรากฏใน `crictl images` | build เฉพาะ dockerd ชั้นนอก ยังไม่ load เข้า kind | รันขั้น build/load ให้ครบ |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

LAB 001 ใช้ cluster-scoped object ที่ bootstrap สร้าง และไม่มี manifest/namespace ของแล็บ
จึงไม่ลบ cluster ที่จะใช้ต่อ แต่พิสูจน์ว่าไม่มี namespace หรือ workload ของ `lab001` ค้าง แล้วรันการตรวจซ้ำได้ผลเดิม:
```bash
kubectl delete namespace lab001 --ignore-not-found
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl get all -n lab001
```
> 📝 **คำอธิบาย:** `delete namespace` พร้อม `--ignore-not-found` ทำให้ cleanup ซ้ำได้ · `get nodes` คือ Clean Re-run ของการสำรวจ cluster · `crictl images` ยืนยันของที่เตรียมยังอยู่ · `get all -n lab001` พิสูจน์ว่าไม่มี workload ของแล็บค้าง

✅ **Expected output** — cluster ยังพร้อมเหมือนเดิมและ `lab001` ว่าง:
```text
NAME                     STATUS   ROLES           AGE     VERSION
devtools-control-plane   Ready    control-plane   8m3s    v1.36.4
devtools-worker          Ready    <none>          7m54s   v1.36.4
devtools-worker2         Ready    <none>          7m54s   v1.36.4
docker.io/library/k8s-lab-api   v1
…
No resources found in lab001 namespace.
```
AGE และ image ID ต่างกันได้ (ตัดบางแถว/บางคอลัมน์) อย่ารัน `k8s-teardown` ตอนนี้ เพราะ LAB 002 ใช้ cluster เดิมต่อ

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `k8s-bootstrap` | สร้าง kind cluster และ component ห้องเรียน |
| `kubectl cluster-info` | แสดง endpoint ของ control plane |
| `kubectl get nodes -o wide` | ดู node พร้อม IP/OS/runtime |
| `kubectl get pods -A` | ดู Pod ทุก namespace |
| `kubectl describe node NAME` | อ่าน Conditions และรายละเอียด node |
| `kind load docker-image ...` | load image เข้า kind node |
| `kubectl get nodes -w` | เฝ้าการเปลี่ยนสถานะ node |

## สรุปสิ่งที่ได้เรียนรู้

Kubernetes ไม่ได้เป็นแค่คำสั่งเปิด container แบบใหม่ แต่เพิ่มสมองที่เห็น cluster ทั้งก้อนและคอยรับรู้ความต่างระหว่างสิ่งที่ต้องการกับสิ่งที่มีจริง

- อธิบายได้แล้วว่า Compose เน้นเครื่องเดียว ส่วน Kubernetes ประสานหลาย node
- แยกได้แล้วว่า control plane ตัดสินใจ ส่วน worker รันงาน
- อ่าน `NotReady`, Condition, logs และ events เป็นหลักฐานได้

**จำภาพเดียวให้ได้:** control plane คือผู้ดูแลที่เฝ้ามอง worker ทุกเครื่อง และรู้เมื่อแรงงานคนหนึ่งหายไป

🧭 ต่อยอด: ไปที่ [LAB 002 — kubectl และ namespace](../002-kubectl-and-namespace/README.md) เพื่อเรียนรู้ว่า object ที่เห็นถูกจัดกลุ่มอย่างไร

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **Docker Compose ทำอะไรไม่ได้บ้างที่ Kubernetes ทำได้?** — Compose ไม่มี control plane เฝ้าหลาย node หรือชดเชยงานเมื่อเครื่องหาย
2. **control plane กับ worker node ต่างกันอย่างไร?** — control plane รับ API/จำ desired state; worker ใช้ kubelet/runtime รัน Pod
3. **ทำไมต้อง `kind load` image?** — node มี image store ของตนเอง จึงมองไม่เห็น image ที่ build อยู่เฉพาะ dockerd ชั้นนอก

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เห็น node 3 ตัวเป็น `Ready`
- [ ] อธิบายบทบาท control plane และ worker ได้
- [ ] image SkillSpace ครบ 4 tag ใน kind node
- [ ] เห็น worker2 เปลี่ยนเป็น `NotReady` จริง
- [ ] เปิด worker2 กลับและตรวจเป็น `Ready`
- [ ] ยืนยันว่าไม่มี resource ใน `lab001`

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
