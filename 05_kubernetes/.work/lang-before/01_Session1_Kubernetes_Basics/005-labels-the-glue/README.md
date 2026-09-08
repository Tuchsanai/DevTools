# LAB 5 — Labels : กาวที่จับ object เป็นกลุ่ม

> โฟลเดอร์ `005-labels-the-glue` = LAB 5 ของชุด Kubernetes ครั้งที่ 1
> (ไฟล์ของแล็บนี้: `01-pods-with-labels.yaml` · `images/03-web-b-v2-label.png`)

> 💡 **แนวคิดหลักของแล็บนี้:** label คือกาวที่ทำให้ object ต่าง ๆ รู้จักกัน โดยไม่ต้องรู้จักชื่อหรือ IP ของกันและกัน

> ชื่อ Pod ของระบบ, IP, AGE, เวลา และ hash เป็นค่าที่ไม่คงที่ — **ค่าเหล่านี้ต่างกันได้**

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายได้ว่าทำไม Kubernetes ใช้ label แทนชื่อหรือ IP
2. อ่าน equality-based และ set-based selector ได้
3. อธิบายได้ว่าเปลี่ยน label แล้วสมาชิกของกลุ่มเปลี่ยนทันทีอย่างไร
4. เชื่อม label selector ไปยัง ReplicaSet, Service และ node scheduling ได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ชื่อ Pod บอกว่า "ตัวไหน" แต่ label บอกว่า "มีคุณสมบัติอะไร" หากระบบมี web 300 ตัว การจดชื่อทุกตัวไม่ช่วยเมื่อ Pod เกิดใหม่หรือ IP เปลี่ยน แต่ selector `app=web,version=v2` ยังบรรยายกลุ่มเดิมได้

| ข้อมูล | ตัวอย่าง | เหมาะกับอะไร |
|---|---|---|
| name | `web-b` | อ้าง object ตัวเดียว |
| label | `app=web` | จัดกลุ่มตามหน้าที่ |
| selector | `version=v2` | เลือกสมาชิกที่ตรงเงื่อนไข |

เครื่องหมาย comma ใน selector หมายถึง AND ทุกเงื่อนไขต้องเป็นจริง ส่วน `in (...)` เลือกได้หลายค่า และ `!tier` หมายถึงไม่มี key นี้

## สิ่งที่จะได้เรียนรู้

- จะได้เห็น label เป็นคอลัมน์และเป็น key/value จริง
- จะได้เลือก Pod ด้วย selector หลายรูปแบบ
- จะได้พิสูจน์ว่า label ไม่จำเป็นต้องเหมือนกันทุก Pod
- จะได้เปลี่ยนสมาชิกของกลุ่มโดยไม่เปลี่ยนชื่อ Pod
- จะได้ลบทั้งกลุ่มด้วย selector เดียว
- จะได้เห็น ingress controller เลือก node ด้วย label
- จะได้อ่าน `FailedScheduling` ที่เกิดจาก label ไม่ตรง

## ภาพรวมของแล็บนี้

1. สร้าง web 3 Pod พร้อม label ต่างกัน
2. แสดงและเลือกกลุ่มด้วย `-l`
3. เปลี่ยน label แล้วลบสมาชิก v2
4. ดูตัวอย่าง node label ที่ระบบจริงพึ่งพา
5. ถอด label สำคัญให้ ingress Pending แล้วแก้กลับ

![Labels และ selectors จับกลุ่ม Pod กับ node](../slides_assets/lab005-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้าเปลี่ยน `web-c` จาก `version=v1` เป็น `version=v2` โดยไม่ restart Pod ผลของ selector จะเปลี่ยนทันทีหรือไม่?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกจากเครื่องหลัก จากนั้นเข้าเครื่องเรียนและพิมพ์คำสั่งที่เหลือใน shell ที่เปิด:
```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** `docker start` เปิดเครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` ข้ามขั้นสร้างเองเมื่อมี cluster แล้ว · `get nodes` ตรวจ cluster · `crictl images` อ่าน image ใน runtime

✅ **Expected output** — 3 nodes Ready และมี image แอปครบ 4 รายการ (AGE และ image ID ต่างกันได้):
```text
Set kubectl context to "kind-devtools"
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready   control-plane   21m   v1.36.4
devtools-worker          Ready   <none>          21m   v1.36.4
devtools-worker2         Ready   <none>          21m   v1.36.4
docker.io/library/k8s-lab-api   v1   f0b9cc03efb0e   186MB
docker.io/library/k8s-lab-db    v1   c6f278c2d20e4   300MB
docker.io/library/k8s-lab-web   v1   47289fcac09e8   209MB
docker.io/library/k8s-lab-web   v2   f2d6e974702f8   209MB
```

ถ้า image ยังไม่อยู่ใน kind ให้ทำขั้น build/load ของ LAB 001 หรือ README ระดับชุดก่อน
ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 เมื่อเรียก Ingress ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`; แล็บนี้เปิดหน้า port-forward ที่ `http://localhost:3000`

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/005-labels-the-glue
```
> 📝 **คำอธิบาย:** `mkdir -p` เตรียม workspace · `git clone` ดาวน์โหลด repository · `cd` เข้า LAB 005

✅ **Expected output** — clone สำเร็จและเข้าโฟลเดอร์ได้โดยไม่มี error:
```text
Cloning into 'DevTools'...
```

ผู้ที่ clone แล้วไม่ต้อง clone ซ้ำ ให้รัน `cd ~/labwork/DevTools && git pull` แล้วกลับเข้าโฟลเดอร์แล็บ; ถ้ามี conflict ให้หยุดก่อนแก้ manifest

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-pods-with-labels.yaml` | Pod × 3 | สร้าง web-a/web-b/web-c ที่ label ต่างกันในไฟล์เดียว | [ดู YAML_Guide.md → Pod](../YAML_Guide.md#pod) |

ไฟล์จริงใช้ `---` คั่น document; ส่วนต้นของ object ที่สองเป็นดังนี้:

```yaml
---                    # จบ Pod ก่อนหน้าและเริ่ม YAML document ใหม่
apiVersion: v1
kind: Pod
metadata:
  name: web-b
  labels:
    app: web           # อยู่กลุ่ม web เหมือนกัน
    version: v2        # แต่เป็นคนละเวอร์ชัน
    tier: frontend
```

`metadata.labels` เป็น map ของ string key/value ไม่ใช่ลำดับชั้น และ `kubectl apply -f` จะอ่านครบทั้ง 3 document ส่วนโครง Pod และ field ของ container เรียนแล้ว จึงไม่อธิบายซ้ำ: [YAML_Guide.md → อ่าน YAML ให้เป็น](../YAML_Guide.md#อ่าน-yaml-ให้เป็น)

**ผิดบ่อยในแล็บนี้:** runlog ไม่มี YAML validation error ของไฟล์นี้; อาการที่ตั้งใจสร้างคือ selector ไม่พบสมาชิกเมื่อถอด/เลือก label ผิด ซึ่งคำสั่งตอบ `No resources found in lab005 namespace.` ไม่ใช่ parser error ให้ตรวจค่าจริงด้วย `kubectl get pods -n lab005 --show-labels`

ดู schema ด้วย `kubectl explain pod.metadata.labels` และ `kubectl explain pod.spec.containers`

## 3. สร้าง Pod สามตัวพร้อม labels

ไฟล์ `01-pods-with-labels.yaml` มี 3 document คั่นด้วย `---`; ทุก Pod ใช้ `app=web` แต่ `version` และ `tier` ต่างกัน:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-a
  labels:
    app: web
    version: v1
    tier: frontend
spec:
  containers:
    - name: web
      image: k8s-lab-web:v1
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 3000
```

> 📝 **คำอธิบาย:** `metadata.name` ระบุ Pod เดียว · `labels` บอกหน้าที่/รุ่น/ชั้น · `spec.containers` กำหนดตัวรันจริง · `imagePullPolicy` ใช้ image ที่ load ไว้ · `containerPort` บอกพอร์ตแอป; document ของ web-b/web-c ใช้โครงเดียวกันแต่ค่า label และ image ต่างกัน

```bash
kubectl create namespace lab005
kubectl apply -n lab005 -f 01-pods-with-labels.yaml
kubectl wait -n lab005 --for=condition=Ready pod -l app=web --timeout=120s
```
> 📝 **คำอธิบาย:** namespace แยก object ของแล็บ · `apply -f` อ่านทั้ง 3 document · `wait` ใช้ selector `-l app=web` รอสมาชิกทุกตัว · `--timeout` ป้องกันรอไม่สิ้นสุด

✅ **Expected output** — Pod ทั้งสามถูกสร้างและ Ready:
```text
namespace/lab005 created
pod/web-a created
pod/web-b created
pod/web-c created
pod/web-a condition met
pod/web-b condition met
pod/web-c condition met
```

## 4. มองและเลือกด้วย selector

```bash
kubectl get pods -n lab005 --show-labels
kubectl get pods -n lab005 -L app,version
```
> 📝 **คำอธิบาย:** `--show-labels` แสดงทุก label ท้ายตาราง · `-L app,version` ยกสอง key เป็นคอลัมน์ · `-n` จำกัด namespace

✅ **Expected output** — อ่านได้ว่า web-c ไม่มี `tier` (AGE ต่างกันได้):
```text
web-a   1/1   Running   0   1s   app=web,tier=frontend,version=v1
web-b   1/1   Running   0   1s   app=web,tier=frontend,version=v2
web-c   1/1   Running   0   1s   app=web,version=v1
```

ลอง equality, AND, set และ does-not-exist:

```bash
kubectl get pods -n lab005 -l version=v1
kubectl get pods -n lab005 -l app=web,version=v2
kubectl get pods -n lab005 -l 'version in (v1,v2)'
kubectl get pods -n lab005 -l '!tier'
```
> 📝 **คำอธิบาย:** `-l` รับ label selector · comma เป็น AND · `in` เลือกสมาชิกที่ค่าอยู่ในชุด · quote ป้องกัน shell ตีความวงเล็บ/`!` · `!tier` เลือก Pod ที่ไม่มี key tier

✅ **Expected output** — ได้กลุ่ม 2, 1, 3 และ 1 ตัวตามลำดับ:
```text
NAME    READY   STATUS    RESTARTS   AGE
web-a   1/1     Running   0          1s
web-c   1/1     Running   0          1s
NAME    READY   STATUS    RESTARTS   AGE
web-b   1/1     Running   0          1s
NAME    READY   STATUS    RESTARTS   AGE
web-a   1/1     Running   0          1s
web-b   1/1     Running   0          1s
web-c   1/1     Running   0          1s
NAME    READY   STATUS    RESTARTS   AGE
web-c   1/1     Running   0          1s
```

selector เดียวกันนี้คือสะพานไปยัง ReplicaSet ซึ่งใช้นับสมาชิก และ Service ซึ่งใช้เลือกปลายทาง โดยไม่ผูกกับชื่อ Pod

เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้ง จากนั้นรัน port-forward ในหน้าต่างใหม่นั้นเพื่อเทียบ label `version=v2` กับหน้าแอปจริง:

```bash
kubectl port-forward -n lab005 pod/web-b 3000:3000 --address 0.0.0.0
```
> 📝 **คำอธิบาย:** `port-forward` ปักที่ Pod เดียวเพื่อพิสูจน์ตัวตน · `3000:3000` map พอร์ต · `--address 0.0.0.0` ให้ browser เปิด `http://localhost:3000` ได้

✅ **Expected output** — หน้าเว็บแสดง Pod `web-b`, version `v2`, theme `emerald`:
```text
Forwarding from 0.0.0.0:3000 -> 3000
```

![หน้า web-b ยืนยัน label version v2](images/03-web-b-v2-label.png)

กด `Ctrl+C` หลังตรวจภาพ

## 5. เปลี่ยนสมาชิกของกลุ่มทันที

```bash
kubectl label pod web-c -n lab005 version=v2 --overwrite
kubectl get pods -n lab005 -l version=v2 --show-labels
kubectl delete pods -n lab005 -l version=v2
kubectl get pods -n lab005 --show-labels
```
> 📝 **คำอธิบาย:** `label pod` แก้ metadata โดยไม่ restart · `--overwrite` อนุญาตทับค่าเดิม · get ตรวจกลุ่มใหม่ · `delete pods -l` ทำงานกับสมาชิกทั้งกลุ่ม

✅ **Expected output** — web-c เข้ากลุ่ม v2 ทันที จากนั้น web-b/web-c ถูกลบ เหลือ web-a:
```text
pod/web-c labeled
web-b   1/1   Running   0   1s   app=web,tier=frontend,version=v2
web-c   1/1   Running   0   1s   app=web,version=v2
pod "web-b" deleted from lab005 namespace
pod "web-c" deleted from lab005 namespace
web-a   1/1   Running   0   3s   app=web,tier=frontend,version=v1
```

## 6. Label ที่ระบบจริงใช้

```bash
kubectl get nodes --show-labels
kubectl -n ingress-nginx get deploy ingress-nginx-controller -o jsonpath='{.spec.template.spec.nodeSelector}{"\n"}'
```
> 📝 **คำอธิบาย:** node ก็มี labels · `jsonpath` เลือก nodeSelector ของ template · controller ต้องการ `ingress-ready=true` และ Linux

✅ **Expected output** — control-plane มี label ที่ controller เลือก (ตัดบางคอลัมน์ของตาราง node):
```text
devtools-control-plane   …   ingress-ready=true,…
{"ingress-ready":"true","kubernetes.io/os":"linux"}
```

## 7. ทดลองให้พัง — ถอด label ที่ ingress พึ่งพา

คำเตือน: ทำสองคำสั่งแรกติดกันและต้องทำขั้นแก้กลับด้านล่าง ห้ามปิดเครื่องค้างไว้กลางขั้น

```bash
kubectl label node devtools-control-plane ingress-ready-
kubectl -n ingress-nginx delete pod -l app.kubernetes.io/component=controller
kubectl -n ingress-nginx get pods -l app.kubernetes.io/component=controller -o wide
kubectl -n ingress-nginx describe pod -l app.kubernetes.io/component=controller
```
> 📝 **คำอธิบาย:** suffix `-` ลบ label key · delete บังคับ Deployment สร้าง controller ใหม่ · get อ่านอาการ · describe อ่านเหตุผลจาก scheduler

✅ **Expected output** — Pod ใหม่ Pending และ event ชี้ selector ไม่ตรง (ชื่อ Pod และ AGE ต่างกันได้):
```text
node/devtools-control-plane unlabeled
pod "ingress-nginx-controller-5d9bb85749-stvjp" deleted from ingress-nginx namespace
ingress-nginx-controller-5d9bb85749-gzpzj   0/1   Pending   0   12s   <none>   <none>
Warning  FailedScheduling  0/3 nodes are available: 3 node(s) didn't match Pod's node affinity/selector. no new claims to deallocate, preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

สาเหตุไม่ใช่ image หรือแอป crash แต่ไม่มี node ใดมีคุณสมบัติตรง `nodeSelector`

แก้กลับและยืนยันทั้งสถานะกับ log:

```bash
kubectl label node devtools-control-plane ingress-ready=true
kubectl -n ingress-nginx wait --for=condition=Ready pod -l app.kubernetes.io/component=controller --timeout=120s
kubectl -n ingress-nginx get pods -l app.kubernetes.io/component=controller -o wide
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=8
```
> 📝 **คำอธิบาย:** ใส่ key/value กลับ · wait รอ controller พร้อม · get ยืนยัน node · logs ตรวจว่า config reload สำเร็จ

✅ **Expected output** — controller กลับ Running และ log แปดบรรทัดท้ายจบด้วย reload สำเร็จ:
```text
node/devtools-control-plane labeled
pod/ingress-nginx-controller-5d9bb85749-gzpzj condition met
ingress-nginx-controller-5d9bb85749-gzpzj   1/1   Running   0   24s   10.244.0.7   devtools-control-plane
I0902 16:53:38.405894      11 nginx.go:319] "Starting NGINX process"
I0902 16:53:38.405981      11 leaderelection.go:258] "Attempting to acquire leader lease..." lock="ingress-nginx/ingress-nginx-leader"
I0902 16:53:38.406220      11 nginx.go:339] "Starting validation webhook" address=":8443" certPath="/usr/local/certificates/cert" keyPath="/usr/local/certificates/key"
I0902 16:53:38.406479      11 controller.go:217] "Configuration changes detected, backend reload required"
I0902 16:53:38.408193      11 status.go:85] "New leader elected" identity="ingress-nginx-controller-5d9bb85749-stvjp"
I0902 16:53:38.424023      11 controller.go:231] "Backend successfully reloaded"
I0902 16:53:38.424102      11 controller.go:243] "Initial sync, sleeping for 1 second"
I0902 16:53:38.424170      11 event.go:377] Event(v1.ObjectReference{Kind:"Pod", Namespace:"ingress-nginx", Name:"ingress-nginx-controller-5d9bb85749-gzpzj", UID:"90c10a6c-337a-4a48-835f-344cae550fb4", APIVersion:"v1", ResourceVersion:"4149", FieldPath:""}): type: 'Normal' reason: 'RELOAD' NGINX reload triggered due to a change in configuration
```

## 8. แบบฝึกหัดสั้น (Exercise)

เพิ่ม label `track=stable` ให้ web-a แล้วออกแบบ selector ที่เลือกเฉพาะ `app=web` ซึ่งมี `track` อยู่ เกณฑ์ผ่านคือคำสั่งเลือก web-a ได้เพียงตัวเดียว และอธิบายได้ว่า selector ไม่ผูกกับชื่อ `web-a`

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get pods -n lab005 --show-labels
kubectl get events -n lab005 --sort-by=.lastTimestamp
kubectl get node devtools-control-plane -o jsonpath='{.metadata.labels.ingress-ready}{"\n"}'
kubectl -n ingress-nginx get pods -l app.kubernetes.io/component=controller
```
> 📝 **คำอธิบาย:** get pods ตรวจสมาชิก · events พิสูจน์ lifecycle · jsonpath ต้องได้ `true` · คำสั่งสุดท้ายกันไม่ให้จบแล็บพร้อม ingress ที่พัง

✅ **Expected output** — ก่อน cleanup web-a ยัง Running, label node เป็น true และ controller 1/1 Running:
```text
web-a   1/1   Running   0   3s   app=web,tier=frontend,version=v1
true
ingress-nginx-controller-5d9bb85749-gzpzj   1/1   Running   0   46s
```

สามบรรทัดนี้มาจากการตรวจคนละช่วงเวลาในรอบเดียวกัน จึงไม่ควรเปรียบเทียบ AGE ข้ามกัน

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| selector ไม่คืนผล | key/value หรือ namespace ไม่ตรง | ใช้ `--show-labels` เทียบทีละ key |
| shell error เมื่อใช้ `!`/วงเล็บ | ไม่ได้ quote set selector | ครอบ selector ด้วย single quotes |
| `--overwrite is false` | key มีค่าเดิมอยู่แล้ว | ตรวจค่าก่อนแล้วเพิ่ม `--overwrite` |
| ingress controller Pending | `ingress-ready` ถูกลบ | ใส่ label กลับแล้ว wait Ready |
| log ยังไม่ขึ้น `Backend successfully reloaded` | controller เพิ่งเริ่มและยัง initial sync | รอ 5–10 วินาทีแล้วรัน logs ซ้ำ |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

```bash
kubectl delete namespace lab005
kubectl wait --for=delete namespace/lab005 --timeout=120s
kubectl get all -n lab005
```
> 📝 **คำอธิบาย:** ลบทั้งห้อง · wait จน namespace หาย · get all ตรวจว่า workload ไม่ค้าง

✅ **Expected output** — namespace ถูกลบและว่าง:
```text
namespace "lab005" deleted
No resources found in lab005 namespace.
```

```bash
kubectl create namespace lab005
kubectl apply -n lab005 -f 01-pods-with-labels.yaml
kubectl wait -n lab005 --for=condition=Ready pod -l app=web --timeout=120s
kubectl get pods -n lab005 -l version=v2 --show-labels
kubectl delete namespace lab005
kubectl wait --for=delete namespace/lab005 --timeout=120s
kubectl get all -n lab005
```
> 📝 **คำอธิบาย:** สร้างจาก source of truth เดิม · wait สมาชิกทั้งหมด · selector ต้องหา web-b ได้เหมือนรอบแรก · ลบปิดท้ายและตรวจซ้ำ

✅ **Expected output** — Clean Re-run ให้ web-b v2 แล้วไม่เหลือ resource:
```text
namespace/lab005 created
pod/web-a created
pod/web-b created
pod/web-c created
pod/web-a condition met
pod/web-b condition met
pod/web-c condition met
web-b   1/1   Running   0   2s   app=web,tier=frontend,version=v2
namespace "lab005" deleted
No resources found in lab005 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get --show-labels` | แสดง label ทุกตัว |
| `kubectl get -L key` | ยก label เป็นคอลัมน์ |
| `kubectl get -l selector` | เลือก object เป็นกลุ่ม |
| `kubectl label --overwrite` | เปลี่ยน label ที่มีอยู่ |
| `kubectl label ... key-` | ลบ label key |
| `kubectl delete -l selector` | ลบสมาชิกทั้งกลุ่ม |

## สรุปสิ่งที่ได้เรียนรู้

label แยก "คุณสมบัติ" ออกจาก "ตัวตน" ทำให้ controller เลือกสมาชิกที่เกิดและตายได้ตลอด โดยไม่จดชื่อหรือ IP รายตัว

- equality selector เลือกค่าตรง; comma เชื่อมเงื่อนไขแบบ AND
- set selector เลือกหลายค่า/มี key/ไม่มี key ได้
- เปลี่ยน label เท่ากับเปลี่ยนสมาชิกของกลุ่มทันที
- nodeSelector ใช้กาวชนิดเดียวกันกับ workload จริง

**จำภาพเดียวให้ได้:** selector วาดวงล้อม object ที่มี label ตรงกัน สมาชิกเข้าออกวงได้โดยชื่อไม่สำคัญ

🧭 ต่อยอด: [LAB 6 — Desired state และ self-healing](../006-desired-state-and-self-healing/README.md)

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. ทำไมใช้ label แทนชื่อ? — เพราะชื่อ/สมาชิกเปลี่ยน แต่คุณสมบัติของกลุ่มยังอธิบายได้
2. `app=web` กับ `app=web,version=v2` ต่างกันอย่างไร? — แบบหลังใช้ AND จึงได้กลุ่มแคบกว่า
3. ถ้าเปลี่ยน label ของ Pod ใต้ ReplicaSet จะเกิดอะไร? — ReplicaSet จะนับไม่เจอและสร้าง Pod ใหม่ให้ desired count ครบ

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เห็น label ของ Pod ทั้งสามแล้ว
- [ ] ใช้ selector ทั้งสี่รูปแบบได้
- [ ] เปลี่ยน web-c เข้ากลุ่ม v2 ได้
- [ ] เห็นหน้า web-b v2 จริง
- [ ] ทำ ingress controller Pending และอ่านสาเหตุออก
- [ ] คืน `ingress-ready=true` แล้ว
- [ ] controller กลับ 1/1 Running
- [ ] Clean Re-run ผ่านและ namespace ว่าง

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
