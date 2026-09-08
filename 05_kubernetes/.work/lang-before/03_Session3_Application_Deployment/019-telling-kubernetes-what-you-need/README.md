# LAB 19 — บอก Kubernetes ว่าแอปต้องการอะไร : จองให้พอและจำกัดไม่ให้กินหมด

> โฟลเดอร์ `019-telling-kubernetes-what-you-need` = LAB 19 ของชุด Kubernetes ครั้งที่ 3
> (ไฟล์ของแล็บนี้: `manifests/02-web-deployment.yaml`, `manifests/03-web-service.yaml`, `manifests/06-ingress.yaml`, `03-web-too-big.yaml`, `04-web-oom.yaml`)

> 💡 **แนวคิดหลักของแล็บนี้:** Kubernetes ต้องรู้ว่าแอปใช้ทรัพยากรเท่าไร จึงจะเลือก node ให้ถูกและกันไม่ให้ตัวหนึ่งกินหมด

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:
1. อธิบายได้ว่า `requests` มีผลต่อการตัดสินใจของ scheduler อย่างไร
2. อธิบายได้ว่า `limits` ถูกบังคับขณะ container รันอย่างไร
3. อ่านหลักฐาน `Pending`, `Insufficient cpu` และ `OOMKilled` ได้
4. เชื่อมค่าที่ประกาศใน YAML กับทรัพยากรที่ node จองจริงได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ถ้า Compose เป็นการวางกล่องบนเครื่องเดียว Kubernetes คือการเลือกว่าจะวาง Pod บน node ใด
scheduler จึงต้องมีตัวเลขสำหรับเปรียบเทียบกับความจุที่เหลือ ตัวเลขนั้นคือ `requests`
ส่วน `limits` คือเพดานระหว่างรัน ไม่ใช่ข้อมูลหลักที่ใช้เลือก node
| ค่า | ใช้เมื่อไร | ผลเมื่อเกิน |
|---|---|---|
| `requests.cpu` / `requests.memory` | ตอน schedule | ไม่มี node พอแล้ว Pod ค้าง `Pending` |
| `limits.cpu` | ตอนรัน | process ถูก throttle ให้ใช้ CPU ช้าลง |
| `limits.memory` | ตอนรัน | kernel หยุด process และ Kubernetes รายงาน `OOMKilled` |
Kubernetes เปรียบเทียบ requests ที่จองไว้ ไม่ใช่ usage ณ วินาทีนั้น
ดังนั้นเครื่องอาจดูว่างจาก `kubectl top` แต่ Pod ยัง schedule ไม่ได้หากขอเกิน allocatable
QoS มีสามชั้น: `Guaranteed` เมื่อทุก container กำหนด request เท่ากับ limit ครบ,
`Burstable` เมื่อกำหนดบางส่วนหรือค่าไม่เท่ากัน และ `BestEffort` เมื่อไม่กำหนดเลย
เมื่อเครื่องตึง QoS เป็นหนึ่งในข้อมูลที่ใช้ตัดสินใจว่า Pod ใดควรถูกขับออกก่อน
HPA ใช้ metrics ปรับจำนวน replicas อัตโนมัติและต้องมี requests เป็นฐานสำหรับค่า utilization; ResourceQuota จำกัดยอดรวมของ namespace ส่วน LimitRange กำหนค่าขั้นต่ำ/สูงหรือค่าปริยายต่อ Pod/container ทั้งสามเป็นขอบเขตขั้นต่อยอด ไม่ได้สร้างในแล็บนี้

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น usage จริงจาก metrics-server แยกจากทรัพยากรที่จอง
- จะได้พิสูจน์ว่า `requests` ปรากฏในส่วน Allocated resources ของ node
- จะได้เห็น scheduler ปฏิเสธ Pod ที่ขอ CPU มากเกินไป
- จะได้อ่าน Events เพื่อระบุว่าปัญหาอยู่ที่การ schedule
- จะได้ทำให้ Next.js ชน memory limit และเห็น `OOMKilled`
- จะได้ใช้ Last State แยกอาการ resource limit ออกจาก application error
- จะได้ตรวจหน้า SkillSpace และ log เป็นหลักฐานว่าตัวปกติยังให้บริการ

## ภาพรวมของแล็บนี้

1. ตรวจ cluster, image และ metrics ก่อนสร้าง workload
2. deploy web ที่ประกาศ requests/limits แล้วดูสิ่งที่ node จอง
3. เปิด SkillSpace ผ่าน Ingress และตรวจ log
4. ขอ CPU เกินเพื่อดู `Pending`
5. จำกัด memory ต่ำเพื่อดู `OOMKilled`
6. แก้กลับ จากนั้นลบและสร้างใหม่เพื่อพิสูจน์ Clean Re-run

![scheduler ใช้ requests และ runtime บังคับ limits](../slides_assets/lab019-architecture.svg)
> **คำถามก่อนเริ่ม:** ถ้า node ใช้ CPU จริงเพียงเล็กน้อย แต่ Pod ขอ `cpu: 64` scheduler ควรยอมวาง Pod หรือไม่?

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** เข้าเครื่องเรียนด้วย `docker exec -it` (ทุกคำสั่งหลังจากนี้พิมพ์ในเครื่องเรียน) · `k8s-bootstrap` ข้ามเองถ้า cluster มีแล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image ใน kind node
ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `localhost:8080`

✅ **Expected output** — node ทั้งสามเป็น `Ready` และพบ image ทั้งสี่; AGE, hash และขนาดต่างกันได้ (ตัดบางแถว):
```text
NAME                     STATUS   ROLES           AGE    VERSION
devtools-control-plane   Ready    control-plane   114s   v1.36.4
devtools-worker          Ready    <none>          101s   v1.36.4
devtools-worker2         Ready    <none>          101s   v1.36.4
docker.io/library/k8s-lab-api   v1   42d77457f3a7b   186MB
…
docker.io/library/k8s-lab-web   v2   36782d1182745   209MB
```
ถ้าผล `grep` ว่าง → ทำขั้น build/load ใน README ระดับชุดหรือ LAB 001

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need
```
> 📝 **คำอธิบาย:** `mkdir -p` สร้าง workspace แบบรันซ้ำได้ · `&&` ทำขั้นถัดไปเมื่อขั้นก่อนผ่าน · `git clone` ดาวน์โหลด repository · `cd` เข้าโฟลเดอร์ LAB 19

✅ **Expected output** — clone สำเร็จและเข้าถึงโฟลเดอร์แล็บได้:
```text
Cloning into 'DevTools'...
/root/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need
```
ถ้า clone ไว้แล้ว ไม่ต้อง clone ซ้ำ ให้อัปเดตด้วย:
```bash
cd ~/labwork/DevTools && git pull
cd 05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need
```
> 📝 **คำอธิบาย:** `git pull` ดึง commit ล่าสุด · คำสั่ง `cd` ที่สองกลับเข้าโฟลเดอร์แล็บ

✅ **Expected output** — repository เป็นเวอร์ชันล่าสุด:
```text
Already up to date.
```

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `manifests/02-web-deployment.yaml` | Deployment | รัน web พร้อม requests/limits ปกติ | [resources](../YAML_Guide.md#2-resources) |
| `manifests/03-web-service.yaml` | Service | เป็นปลายทางของ web | [ทบทวน Service](../YAML_Guide.md#service) |
| `manifests/06-ingress.yaml` | Ingress | เปิด path `/` มายัง web | [Ingress](../YAML_Guide.md#1-ingress) |
| `03-web-too-big.yaml` | Deployment | จงใจ request 64 CPU ให้ Pending | [resources ผิดบ่อย](../YAML_Guide.md#2-resources) |
| `04-web-oom.yaml` | Deployment | จงใจจำกัด memory 32Mi ให้ OOMKilled | [resources ผิดบ่อย](../YAML_Guide.md#2-resources) |

ค่าที่ scheduler และ runtime อ่านจริงจาก `manifests/02-web-deployment.yaml`:

```yaml
resources:
  requests:            # ใช้ตอน schedule
    cpu: 100m          # 0.1 CPU core
    memory: 128Mi      # 128 mebibytes
  limits:              # ใช้บังคับตอนรัน
    cpu: 500m          # เกินแล้วถูก throttle
    memory: 256Mi      # เกินแล้วมีโอกาส OOMKilled
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `requests.cpu` | CPU ที่ scheduler จอง; ถ้าเว้นไว้แต่มี limit จะใช้ limit เป็น request | `"64"` คือ 64 cores ไม่ใช่ 64m และเกินทุก worker ในแล็บ |
| `requests.memory` | memory ที่ใช้เลือก node; กฎ default เหมือน CPU | สูงเกิน allocatable ของทุก node ทำให้ Pending |
| `limits.cpu` | เพดาน CPU; ไม่มี default | process ใช้เกินจะถูก throttle |
| `limits.memory` | เพดาน memory; ไม่มี default | process ใช้เกินอาจจบเป็น OOMKilled |

QoS อ่านจาก request/limit ของทุก container: เท่ากันครบ CPU+memory = `Guaranteed`, มีอย่างน้อยหนึ่งค่าแต่ไม่ครบเงื่อนไข
= `Burstable`, ไม่มีทั้งหมด = `BestEffort`; manifest หลักนี้เป็น `Burstable` เพราะ request กับ limit ไม่เท่ากัน

**ผิดบ่อยในแล็บนี้:** runlog ของ `03-web-too-big.yaml` แสดง
`0/3 nodes are available: ... 2 Insufficient cpu.` ส่วน `04-web-oom.yaml` แสดง `Reason: OOMKilled` และ exit code 137—สองอาการเกิดคนละจังหวะ จึงอย่าแก้ limit เมื่อปัญหาอยู่ที่ scheduling

ดู field ได้ด้วย `kubectl explain deployment.spec.template.spec.containers.resources.requests`, `kubectl explain deployment.spec.template.spec.containers.resources.limits` และ `kubectl get pod -n lab019 -l app=web -o jsonpath='{.items[0].status.qosClass}'`

## 3. วัดก่อนบอกความต้องการ

สร้าง namespace แล้วดูทรัพยากรที่ node จองและ usage จริงก่อน deploy:
```bash
kubectl create namespace lab019
kubectl describe node devtools-worker | sed -n '/Allocated resources:/,/Events:/p'
kubectl top nodes
kubectl top pods -n lab019
```
> 📝 **คำอธิบาย:** `create namespace` แยก resource ของแล็บ · `describe node` แสดง capacity และ allocation · `sed -n` ตัดมาเฉพาะช่วงที่ต้องอ่าน · `top nodes` อ่าน usage จาก metrics-server · `top pods -n` จำกัดผลใน namespace นี้

✅ **Expected output** — เห็น allocation เดิม, usage ของสาม node และยังไม่มี Pod ใน `lab019`; ตัวเลข CPU/RAM และ AGE ต่างกันได้:
```text
Allocated resources:
  Resource           Requests    Limits
  cpu                200m (0%)   0 (0%)
  memory             250Mi (0%)  0 (0%)
NAME                     CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
devtools-control-plane   154m         0%       1202Mi          1%
devtools-worker          29m          0%       312Mi           0%
devtools-worker2         23m          0%       314Mi           0%
No resources found in lab019 namespace.
```
(ตัดบางบรรทัดจาก `describe`; ค่า 200m/250Mi มาจาก Pod ระบบที่มีอยู่ก่อนแล้ว)

## 4. ประกาศ requests และ limits

ส่วนสำคัญใน `manifests/02-web-deployment.yaml` คือ:
```yaml
resources:
  requests:      # scheduler ใช้ค่าที่จองนี้เลือก node
    cpu: 100m
    memory: 128Mi
  limits:        # runtime บังคับเพดานสูงสุด
    cpu: 500m
    memory: 256Mi
```
`100m` คือหนึ่งในสิบ CPU core ส่วน `128Mi` คือ 128 mebibytes
apply ทั้ง Deployment, Service และ Ingress แล้วอ่านค่าที่ API server เก็บ:
```bash
kubectl apply -f manifests/
kubectl wait -n lab019 --for=condition=available deployment/web --timeout=120s
kubectl get pods -n lab019 -o wide
kubectl get pod -n lab019 -l app=web -o jsonpath='{.items[0].spec.containers[0].resources}{"\n"}'
```
> 📝 **คำอธิบาย:** `apply -f manifests/` ส่งทุก YAML ในโฟลเดอร์ · `wait --for=condition=available` รอ Deployment พร้อม · `--timeout=120s` กันการรอไม่สิ้นสุด · `-o wide` เพิ่ม IP/node · `-l app=web` เลือกด้วย label · `jsonpath` หยิบเฉพาะ resources

✅ **Expected output** — Deployment พร้อมและค่าที่อ่านกลับตรง YAML; ชื่อ Pod, IP, node และ AGE ต่างกันได้:
```text
deployment.apps/web created
service/web created
ingress.networking.k8s.io/skillspace created
deployment.apps/web condition met
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE
web-6c7867dd5b-cd47c   1/1     Running   0          7s    10.244.2.4   devtools-worker2
{"limits":{"cpu":"500m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}
```
ดู node ที่รับ Pod และวัด usage หลังแอปรัน:
```bash
NODE=$(kubectl get pod -n lab019 -l app=web -o jsonpath='{.items[0].spec.nodeName}')
kubectl describe node "$NODE" | sed -n '/Allocated resources:/,/Events:/p'
kubectl top pods -n lab019
```
> 📝 **คำอธิบาย:** command substitution เก็บชื่อ node ใน `NODE` · `describe` แสดงยอดจองรวม · `top pods` แสดงการใช้จริงซึ่งไม่จำเป็นต้องเท่ากับ requests

✅ **Expected output** — limits/request ถูกนับใน node และ usage จริงต่ำกว่าเพดาน; node และตัวเลขต่างกันได้:
```text
Allocated resources:
  Resource           Requests    Limits
  cpu                200m (0%)   500m (1%)
  memory             178Mi (0%)  256Mi (0%)
NAME                   CPU(cores)   MEMORY(bytes)
web-6c7867dd5b-cd47c   2m           50Mi
```
(ตัดบางบรรทัดจาก `describe`; ตัวเลข node/usage ต่างกันได้)

## 5. พิสูจน์จากหน้าเว็บและ log

เปิด `http://localhost:8080` แล้วตรวจการ์ด WEB จากนั้นดู JSON และ log:
```bash
until BODY=$(curl -fsS http://localhost/info); do sleep 2; done
echo "$BODY" | jq -c '{pod,version}'
kubectl logs -n lab019 deployment/web --tail=10
```
> 📝 **คำอธิบาย:** loop รอ Ingress · `/info` คืนหลักฐาน Pod/version · `jq -c '{pod,version}'` เลือก field ให้ตรงผลที่แสดง · `logs deployment/web` ให้ Kubernetes เลือก Pod · `--tail=10` จำกัดท้าย log

✅ **Expected output** — web ตอบ v1 และ log ระบุว่า Next.js พร้อม; ชื่อ Pod ต่างกันได้:
```text
{"pod":"web-6c7867dd5b-cd47c","version":"v1"}
▲ Next.js 16.3.1
- Local:         http://localhost:3000
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
```

![หน้า SkillSpace แสดงชื่อ web Pod และเวอร์ชัน v1](images/02-web-with-resources.png)

## 6. ทดลองให้พัง — requests ใหญ่จน Pending

`03-web-too-big.yaml` ขอ `cpu: "64"` ซึ่งใหญ่กว่า allocatable ของ worker ทุกตัว:
```bash
kubectl apply -f 03-web-too-big.yaml
sleep 3
kubectl get pods -n lab019
POD=$(kubectl get pod -n lab019 -l app=web-too-big -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod -n lab019 "$POD" | grep -A8 '^Events:'
```
> 📝 **คำอธิบาย:** `apply` สร้าง Deployment ที่จงใจพัง · `sleep 3` ให้ scheduler บันทึกเหตุการณ์ · `get pods` อ่านอาการ · `jsonpath` เก็บชื่อ Pod ที่มี hash · `describe` เปิดเหตุผล · `grep -A8` แสดง Events และอีกแปดบรรทัด

✅ **Expected output** — Pod ค้าง `Pending` และ Events บอก `Insufficient cpu`; ชื่อ Pod และ AGE ต่างกันได้:
```text
deployment.apps/web-too-big created
NAME                          READY   STATUS    RESTARTS   AGE
web-6c7867dd5b-cd47c          1/1     Running   0          71s
web-too-big-85f7c9db4-c6brj   0/1     Pending   0          3s
Events:
  Type     Reason            Age   From               Message
  Warning  FailedScheduling  3s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. no new claims to deallocate, preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```
control-plane ของ kind มี taint จึงไม่นับเป็น worker ปกติ ข้อความจริงจึงแยกเป็นหนึ่ง node ที่ติด taint และสอง node ที่ CPU ไม่พอ
แก้กลับโดยลบ workload ที่จงใจขอเกิน:
```bash
kubectl delete deployment web-too-big -n lab019
kubectl get pods -n lab019
```
> 📝 **คำอธิบาย:** `delete deployment` ลบ Deployment และ Pod ลูก · `-n lab019` ระบุ namespace · `get pods` ยืนยันว่าเหลือ web ปกติ

✅ **Expected output** — `web-too-big` หายและ web หลักยัง Running; ชื่อ Pod/AGE ต่างกันได้:
```text
deployment.apps "web-too-big" deleted from lab019 namespace
NAME                   READY   STATUS    RESTARTS   AGE
web-6c7867dd5b-cd47c   1/1     Running   0          72s
```

## 7. ทดลองให้พัง — memory limit ต่ำจน OOMKilled

`04-web-oom.yaml` จำกัด Next.js ไว้เพียง `32Mi` ให้สังเกต restart และ Last State:
```bash
kubectl apply -f 04-web-oom.yaml
sleep 15
kubectl get pods -n lab019
POD=$(kubectl get pod -n lab019 -l app=web-oom -o jsonpath='{.items[0].metadata.name}')
kubectl get pod -n lab019 "$POD" -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}'
```
> 📝 **คำอธิบาย:** `sleep 15` เปิดเวลาให้ container ชน limit และ restart · `containerStatuses[0]` เลือก container แรก · `lastState.terminated.reason` อ่านสาเหตุรอบก่อน

✅ **Expected output** — RESTARTS เพิ่มและเหตุผลเป็น `OOMKilled`; ชื่อ Pod, จำนวน restart และเวลาแตกต่างกันได้:
```text
deployment.apps/web-oom created
NAME                       READY   STATUS    RESTARTS      AGE
web-oom-57d64f4844-qnfrp   1/1     Running   2 (12s ago)   16s
OOMKilled
```
ตรวจรายละเอียดแล้วแก้กลับ:
```bash
kubectl describe pod -n lab019 -l app=web-oom | sed -n '/Containers:/,/Conditions:/p'
kubectl logs -n lab019 deployment/web-oom --previous --tail=10
kubectl delete deployment web-oom -n lab019
kubectl wait -n lab019 --for=condition=ready pod -l app=web --timeout=60s
```
> 📝 **คำอธิบาย:** `Last State` เก็บเหตุผลของ process ที่จบ · `--previous` อ่าน stdout ของ container รอบก่อน · การลบ workload พังคืนสภาพ · `wait condition=ready` ยืนยัน web หลักพร้อม

✅ **Expected output** — เห็น `OOMKilled`, exit code 137 และ web ปกติยัง Ready:
```text
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
Limits:
  memory:  32Mi
…
▲ Next.js 16.3.1
✓ Ready in 0ms
deployment.apps "web-oom" deleted from lab019 namespace
pod/web-6c7867dd5b-cd47c condition met
```
(ตัดบางบรรทัดระหว่าง `Containers:` ถึง `Conditions:`)

## 8. แบบฝึกหัดสั้น (Exercise)

ปรับค่าของ web หลักให้ request เท่ากับ limit ทั้ง CPU และ memory แล้วตอบสองข้อ:
1. QoS เปลี่ยนจาก `Burstable` เป็นอะไร
2. การเปลี่ยนนี้ทำให้ usage จาก `kubectl top` เท่ากับ request หรือไม่ เพราะอะไร
เกณฑ์สำเร็จ: Pod ต้อง Ready, หน้าเว็บยังเปิดได้ และอธิบายได้ว่า QoS กับ usage เป็นคนละเรื่อง

## วิธีตรวจสอบผลการทดลอง

ใช้ชุดตรวจสั้นนี้หลังแก้กลับ:
```bash
kubectl get all,ingress -n lab019
kubectl get pod -n lab019 -l app=web -o jsonpath='{.items[0].status.qosClass}{"\n"}'
curl -s http://localhost/info | jq -c '{pod,version}'
```
> 📝 **คำอธิบาย:** `get all,ingress` ตรวจ workload และทางเข้า · `status.qosClass` อ่าน QoS ที่ระบบคำนวณ · `curl /info` ตรวจมุมผู้ใช้

✅ **Expected output** — มี web 1 ตัว Ready, QoS เป็น `Burstable` และหน้าเว็บตอบ v1; ชื่อ Pod, ClusterIP และ AGE ต่างกันได้:
```text
pod/web-6c7867dd5b-cd47c   1/1   Running   0   113s
service/web               ClusterIP   10.96.172.216   <none>   3000/TCP
deployment.apps/web       1/1   1   1   113s
ingress.networking.k8s.io/skillspace   nginx   *   10.96.167.146   80
Burstable
{"pod":"web-6c7867dd5b-cd47c","version":"v1"}
```
ผ่านเมื่อหลักฐานสามมุมตรงกัน: kubectl บอก Ready, UI แสดง web Pod/v1 และ log บอก Next.js Ready

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `kubectl top` ยังไม่มีค่า | metrics-server เพิ่งเริ่ม | รอครู่หนึ่งแล้วลองใหม่ |
| curl ได้ 404/503 ทันทีหลัง apply | ingress-nginx ยัง sync rule/endpoints | รอแล้วลองซ้ำด้วย `curl -f` |
| Pod `Pending` | requests เกิน allocatable | อ่าน Events แล้วลด request |
| RESTARTS เพิ่มและ Last State `OOMKilled` | memory limit ต่ำกว่า working set | เพิ่ม limit หรือแก้ memory leak |
| image ไม่ขึ้น | ยังไม่ได้ build/load เข้า kind | กลับไปขั้น build/load ของแล็บ 001 |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

ลบ namespace แล้วสร้างใหม่จากไฟล์เดิม:
```bash
kubectl delete namespace lab019
kubectl wait --for=delete namespace/lab019 --timeout=120s
kubectl get all -n lab019
kubectl create namespace lab019
kubectl apply -f manifests/
kubectl wait -n lab019 --for=condition=available deployment/web --timeout=120s
until BODY=$(curl -fsS http://localhost/info); do sleep 2; done
echo "$BODY" | jq -c '{pod,version}'
```
> 📝 **คำอธิบาย:** `delete namespace` ลบทั้งห้อง · `wait --for=delete` รอให้หายจริง · `get all` ตรวจว่าไม่มีของค้าง · สร้าง namespace และ apply จาก source of truth ใหม่ · ลูป `until` รอทั้ง Pod และ Ingress พร้อมจริง · `curl -f` ถือ HTTP 4xx/5xx เป็นความล้มเหลว

✅ **Expected output** — หลังลบไม่พบ resource และ re-run กลับมาตอบ v1; ชื่อ Podต่างกันได้:
```text
namespace "lab019" deleted
No resources found in lab019 namespace.
namespace/lab019 created
deployment.apps/web created
service/web created
ingress.networking.k8s.io/skillspace created
deployment.apps/web condition met
curl: (22) The requested URL returned error: 503
{"pod":"web-6c7867dd5b-dhdns","version":"v1"}
```
ข้อความ 503 หนึ่งครั้งมาจากรอบที่ ingress ยัง sync; ลูปรอจนได้ response จริงจึงถือว่าผ่าน จากนั้นลบปิดท้าย:
```bash
kubectl delete namespace lab019
kubectl wait --for=delete namespace/lab019 --timeout=120s
kubectl get all -n lab019
kubectl get namespace lab019
```
> 📝 **คำอธิบาย:** ลบ namespace รอบ re-run · รอการลบ · ตรวจ resource · ตรวจ namespace โดยตรงเพื่อกันของค้าง

✅ **Expected output** — ไม่มี resource และ namespace ไม่อยู่แล้ว:
```text
namespace "lab019" deleted
No resources found in lab019 namespace.
Error from server (NotFound): namespaces "lab019" not found
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl top nodes/pods` | ดู usage จริงจาก metrics-server |
| `kubectl describe node` | ดู capacity และ requests/limits ที่จอง |
| `kubectl apply -f manifests/` | สร้างสภาพที่ต้องการจาก YAML |
| `kubectl describe pod` | อ่าน Events และ Last State |
| `kubectl logs --previous` | อ่าน log ของ container รอบก่อน |
| `kubectl get ... -o jsonpath=...` | หยิบ field เฉพาะจาก object |
| `kubectl delete namespace lab019` | ลบ resource ทั้งแล็บ |

## สรุปสิ่งที่ได้เรียนรู้

Kubernetes ไม่อาจเลือก node หรือปกป้องเพื่อนบ้านได้ดีหากเราไม่บอกขนาดงาน
- `requests` คือคำสัญญาที่ scheduler ใช้ตอนวาง Pod
- `limits` คือรั้วที่ runtime บังคับหลัง Pod เริ่มรัน
- `Pending` พร้อม `Insufficient cpu` ชี้ไปที่ชั้น scheduler
- `OOMKilled` ชี้ว่า process ใช้ memory เกิน limit
- metrics บอกสิ่งที่ใช้จริง ส่วน requests บอกสิ่งที่ระบบต้องกันไว้
**จำภาพเดียวให้ได้:** requests คือที่นั่งที่จองก่อนขึ้นรถ ส่วน limits คือรั้วที่ห้ามแผ่เกินพื้นที่ระหว่างเดินทาง
🧭 ต่อยอด: ไปที่ [LAB 20 — Reading the Symptoms](../020-reading-the-symptoms/README.md) เพื่อฝึกอ่านอาการเสียหลายชั้นอย่างเป็นลำดับ

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **requests กับ limits มีผลคนละจังหวะอย่างไร?** — requests ใช้ตอน schedule; limits บังคับตอนรัน
2. **ทำไม Pod Pending ทั้งที่ `top` ดูเหมือนเครื่องว่าง?** — scheduler นับ requests ที่จองและ allocatable ไม่ใช่ usage ณ ขณะนั้น
3. **ควรตั้ง requests เท่าไร?** — เริ่มจากการวัด workload จริง ตั้ง request ใกล้ usage ปกติ และ limit ใกล้ยอดสูงสุดที่ระบบยอมรับได้

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] node ทั้งสามเป็น Ready และ image แอปอยู่ใน kind
- [ ] web ปกติแสดง requests/limits ตรง YAML
- [ ] เปิด UI แล้วเห็นชื่อ web Pod และป้าย v1
- [ ] เห็น `Pending` พร้อม `Insufficient cpu` จริง
- [ ] เห็น `OOMKilled` และ exit code 137 จริง
- [ ] อธิบายจังหวะทำงานของ requests และ limits ได้
- [ ] Clean Re-run ผ่านและลบ `lab019` ปิดท้ายแล้ว
*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
