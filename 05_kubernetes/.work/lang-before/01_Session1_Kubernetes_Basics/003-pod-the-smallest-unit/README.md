# LAB 3 — Pod หน่วยเล็กที่สุด : เปิด SkillSpace บน Kubernetes
> โฟลเดอร์ `003-pod-the-smallest-unit` = LAB 3 ของชุด Kubernetes ครั้งที่ 1
> (ไฟล์ของแล็บนี้: `README.md`, `02-pod-with-sidecar.yaml`, `images/03-first-page-on-kubernetes.png`)

> 💡 **แนวคิดหลักของแล็บนี้:** หน่วยเล็กที่สุดที่ Kubernetes ดูแลคือ Pod ไม่ใช่ container

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายได้ว่า Pod ครอบ container หนึ่งตัวหรือหลายตัวได้อย่างไร
2. อธิบายได้ว่า container ใน Pod เดียวกันแชร์ network namespace และวงจรชีวิตร่วมกันอย่างไร
3. อ่านลำดับ Scheduled → Pulled → Created → Started จาก Events ได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

บน Docker เราคุ้นกับการรัน container โดยตรง แต่ Kubernetes schedule Pod—“ซอง” ที่บรรจุ container อย่างน้อยหนึ่งตัว

| เรื่อง | Container | Pod |
|---|---|---|
| สิ่งที่เป็น | process ที่แยกด้วย namespace/cgroup | หน่วยที่ Kubernetes schedule |
| จำนวน | หนึ่ง process หลักต่อ container | มี container ตั้งแต่หนึ่งตัวขึ้นไป |
| Network | มี namespace ของตนตาม runtime | container ใน Pod แชร์ IP/port/loopback |
| Lifecycle | runtime เริ่ม/หยุด process | Kubernetes สร้าง/ลบ container ทั้งกลุ่ม |

หลาย container เหมาะเมื่อ “ตัวช่วย” ต้องเกาะแอปหลักแน่น; web, API และ database ไม่ควรอยู่ Pod เดียวเพราะต้อง scale/เปลี่ยนแยกกัน

Pod ในแล็บนี้ยังไม่มี controller ถือ desired count หากลบจึงหายจริง
ภาพนี้จะเป็นฐานเปรียบเทียบกับ ReplicaSet ใน LAB 006

## สิ่งที่จะได้เรียนรู้

- จะได้สร้าง Pod ของ web v1 แบบ imperative
- จะได้เห็นสถานะ Pending, ContainerCreating และ Running จริง
- จะได้อ่าน startup log ของ Next.js
- จะได้เข้า container เพื่อดู process และ endpoint
- จะได้พิสูจน์ network ที่แชร์กันด้วย sidecar
- จะได้ทำ tag ผิดและอ่าน ErrImagePull/ImagePullBackOff

## ภาพรวมของแล็บนี้

1. สร้าง namespace และ Pod `web`
2. ตรวจสถานะ, Events และ logs
3. exec เข้า container และเรียก endpoint ภายใน
4. port-forward แล้วตรวจหน้าเว็บจริง
5. apply Pod `web2` ที่มีสอง container
6. ลบ Pod เดี่ยวเพื่อดูว่าไม่มีตัวแทน

![ภาพสถาปัตยกรรม LAB 003: Pod เดี่ยวและ Pod ที่มี web กับ sidecar แชร์ network](../slides_assets/lab003-architecture.svg)
> **คำถามก่อนเริ่ม:** ถ้า web กับตัวตรวจสุขภาพต้องคุยกันผ่าน loopback และย้าย node พร้อมกัน เราควรให้ Kubernetes ดูแลเป็นหนึ่งหน่วยอะไร?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกจากเครื่องหลัก จากนั้นเข้าเครื่องเรียนและพิมพ์ทุกคำสั่งหลังจากนั้นใน shell ที่เปิด:
```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```
> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิมหรือสร้างใหม่ · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` ข้ามขั้นสร้างเองเมื่อมี cluster แล้ว · `get nodes` ตรวจ cluster · `crictl images` ตรวจ image จาก node

✅ **Expected output** — node ทั้งสาม `Ready` และมี web v1/v2, api v1, db v1:
```text
Set kubectl context to "kind-devtools"
NAME                     STATUS   ROLES           AGE     VERSION
…
docker.io/library/k8s-lab-api   v1   c01adaec89c6d   186MB
docker.io/library/k8s-lab-db    v1   a5a8c986a5421   300MB
docker.io/library/k8s-lab-web   v1   34d144d726eda   209MB
docker.io/library/k8s-lab-web   v2   0bdb9ed2beecf   209MB
```
ตัดแถว node ทั้งสามออกจากตัวอย่างเพื่อไม่ตรึง AGE; ผลจริงต้องเห็นทุกแถวเป็น `Ready` ส่วน image ID/ขนาดต่างกันได้ หาก image ไม่ครบให้ทำขั้น build/load ของ LAB 001 ก่อน

ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 เมื่อเรียก Ingress ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`; แล็บนี้เปิดหน้า port-forward ที่ `http://localhost:3000`

## 1. Clone โค้ดแล็บ
```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit
pwd
```
> 📝 **คำอธิบาย:** `mkdir -p` เตรียม workspace · `&&` ไปต่อเมื่อสำเร็จ · `git clone` ดึง repository · `cd` เข้า LAB 003 · `pwd` ยืนยัน path

✅ **Expected output** — clone สำเร็จและอยู่ในโฟลเดอร์ที่มี manifest:
```text
Cloning into 'DevTools'...
/root/labwork/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit
```
ถ้า clone แล้ว ให้ใช้ `cd ~/labwork/DevTools && git pull` แล้วกลับเข้าโฟลเดอร์นี้

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `02-pod-with-sidecar.yaml` | Pod | รัน web กับ sidecar ใน Pod เดียวเพื่อพิสูจน์ network ที่แชร์กัน | [ดู YAML_Guide.md → Pod](../YAML_Guide.md#pod) |

ส่วนที่ทำให้แล็บนี้ต่างจาก Pod เดี่ยว คัดจาก `02-pod-with-sidecar.yaml`:

```yaml
spec:
  containers:                         # list: Pod นี้มีสมาชิก 2 container
    - name: web                       # ชื่อใช้อ้างตอน logs/exec
      image: k8s-lab-web:v1           # image ของแอปหลัก
      imagePullPolicy: IfNotPresent   # ใช้ image ใน node ถ้ามี
      ports:
        - containerPort: 3000         # แอปฟัง port นี้; ยังไม่ใช่การเปิดออกนอก Pod
    - name: sidecar                   # container ตัวที่สอง
      image: busybox:1.36.1
      imagePullPolicy: IfNotPresent
      command: ["sh", "-c"]          # แทน ENTRYPOINT ของ image
      args:                           # argument ของ command ข้างบน
        - while true; do
            wget -qO- http://127.0.0.1:3000/healthz;
            echo;
            sleep 10;
          done
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `containers[]` | รายการ container ที่อยู่ใน Pod/node เดียวกันและแชร์ IP | เพิ่มสมาชิกก็เพิ่ม process แต่ไม่เพิ่ม Pod IP |
| `name` / `image` | ตัวตนใน Pod / สิ่งที่จะรัน | ชื่อต้องไม่ซ้ำ; tag image ผิดดึงไม่ได้ |
| `imagePullPolicy` | `IfNotPresent` ใช้ cache ก่อน | `Always` ตรวจ registry ทุกครั้ง; `Never` ล้มถ้า node ไม่มี image |
| `containerPort` | ข้อมูลว่า process ฟัง port 3000 | ไม่ได้สร้าง Service หรือ publish port ให้เอง |
| `command` / `args` | แทน ENTRYPOINT / ส่ง argument แทน CMD | process หลักและพฤติกรรม sidecar เปลี่ยน |

`env`, `envFrom`, ค่า default ของ `restartPolicy: Always` และข้อจำกัด immutable สรุปไว้ใน [YAML_Guide.md → Pod](../YAML_Guide.md#pod) เพราะไฟล์นี้ไม่ได้เขียน field เหล่านั้น

**ผิดบ่อยในแล็บนี้:** runlog มีข้อความจริง `Error: ImagePullBackOff` เมื่อใช้ `k8s-lab-web:v9`; นี่ไม่ใช่ปัญหาการเยื้อง แต่เป็นค่าของ `image` ที่หาไม่ได้ อ่านเหตุผลเต็มด้วย `kubectl describe pod web-broken -n lab003` ก่อนแก้ tag

ดู schema ด้วย `kubectl explain pod.spec.containers` และ `kubectl explain pod.spec.containers.command`

## 3. สร้าง Pod แรกแบบ imperative
```bash
kubectl config set-context --current --namespace=default
kubectl create namespace lab003
kubectl run web --image=k8s-lab-web:v1 --port=3000 -n lab003
kubectl get pods -n lab003 -w
```
> 📝 **คำอธิบาย:** ตั้ง context กลับ default กันผลจากแล็บก่อน · `create namespace` สร้างห้อง · `run web` สร้าง Pod ชื่อ web · `--image` เลือก image ที่ load แล้ว · `--port=3000` บันทึก port ของ container · `-n lab003` ระบุห้อง · `-w` เฝ้าการเปลี่ยนสถานะและหยุดด้วย `Ctrl+C`

✅ **Expected output** — เห็นวงจรจาก Pending ผ่าน ContainerCreating ไป Running:
```text
namespace/lab003 created
pod/web created
NAME   READY   STATUS              RESTARTS   AGE
web    0/1     Pending             0          0s
web    0/1     ContainerCreating   0          0s
web    1/1     Running             0          1s
```
AGE และระยะเวลาระหว่างสถานะต่างกันได้

## 4. หาให้เจอว่า Pod อยู่ที่ไหนและเริ่มอย่างไร
```bash
kubectl get pods -n lab003 -o wide
kubectl describe pod web -n lab003 | sed -n '/Events:/,$p'
kubectl logs web -n lab003
```
> 📝 **คำอธิบาย:** `-o wide` เพิ่ม Pod IP และ node · `describe` แสดง Events · `sed` เลือกช่วง Events ถึงท้าย · `logs` อ่าน stdout/stderr ของ container ตัวเดียวใน Pod

✅ **Expected output** — web อยู่บน worker, Events ครบสี่ขั้น และ Next.js พร้อมที่ port 3000:
```text
NAME   READY   STATUS    IP           NODE
web    1/1     Running   10.244.1.4   devtools-worker
Normal  Scheduled  Successfully assigned lab003/web to devtools-worker
Normal  Pulled     Container image "k8s-lab-web:v1" already present on machine
Normal  Created    Container created
Normal  Started    Container started
▲ Next.js 16.3.1
- Network:       http://0.0.0.0:3000
✓ Ready in 0ms
```
IP, NODE, AGE และเวลา startup ต่างกันได้ คำว่า `already present` พิสูจน์ผลของ `kind load`

## 5. เข้าไปดูใน container

เริ่มจากชื่อ host ของ kernel แล้วเปิด shell:
```bash
kubectl exec -n lab003 web -- hostname
kubectl exec -it -n lab003 web -- sh
ps
env | grep HOSTNAME
wget -qO- localhost:3000/info
exit
```
> 📝 **คำอธิบาย:** `exec` รันใน container · `-it` เปิด shell · `--` คั่น option ของ kubectl จากคำสั่งใน container · `ps` ดู process · `env` อ่านตัวแปร · `wget -qO-` พิมพ์ response · `localhost` ทดลอง loopback

✅ **Expected output** — `hostname` ของ kernel คือ `web` และ Next.js เป็น PID 1 ส่วนตัวแปร `HOSTNAME=0.0.0.0` เป็นค่าที่ image ใช้บอกให้แอปรับ connection ทุก IPv4 interface; รอบนี้ `localhost` resolve ไป IPv6 loopback แต่แอปฟัง IPv4 จึงต่อไม่ได้:
```text
web
PID   USER     TIME  COMMAND
    1 webapp    0:00 next-server (v
HOSTNAME=0.0.0.0
wget: can't connect to remote host: Connection refused
command terminated with exit code 1
```
ผลนี้เป็นบทเรียนเสริมว่า `hostname` กับตัวแปร `HOSTNAME` อาจสื่อคนละเรื่อง และ `localhost` ไม่ได้บังคับว่าจะเป็น IPv4 เสมอ จึงลองระบุ IPv4 loopback ที่ process ฟังอยู่โดยตรง:
```bash
kubectl exec -n lab003 web -- wget -qO- http://127.0.0.1:3000/info
```
> 📝 **คำอธิบาย:** ระบุ `127.0.0.1` เพื่อบังคับ IPv4 loopback · endpoint `/info` คืน identity/runtime state ของ web · ชื่อ Pod มาจาก `os.hostname()` จึงยังเป็น `web`

✅ **Expected output** — endpoint ตอบ JSON ของ Pod เดิม:
```json
{"pod":"web","version":"v1","theme":"blue","site_name":"SkillSpace","time":"23:51:58","api":{"configured":false,"reachable":false},"db":{"status":"unknown"}}
```
เวลาต่างกันได้

## 6. เปิดหน้าเว็บจริงผ่าน port-forward

เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้ง จากนั้นรันคำสั่งต่อไปนี้ในหน้าต่างใหม่และคงไว้:
```bash
kubectl port-forward pod/web 3000:3000 -n lab003 --address 0.0.0.0
```
> 📝 **คำอธิบาย:** `port-forward pod/web` ปักทางไป Pod ตัวเดียว · `3000:3000` map port เครื่องเรียนไป container · `-n` เลือก namespace · `--address 0.0.0.0` ทำให้ browser นอกเครื่องเรียนเข้าถึงได้ · คงหน้าต่างใหม่นี้ไว้ระหว่างทดสอบ

✅ **Expected output** — forward พร้อมรับ connection:
```text
Forwarding from 0.0.0.0:3000 -> 3000
Handling connection for 3000
```
เปิด `http://localhost:3000` แล้วตรวจการ์ดบนสุด ต้องเห็น `ตอบโดย Pod: web`, ป้าย `v1`, API เป็นโหมดเดี่ยว และ DB เป็น unknown

![หน้า SkillSpace ที่รันจริงบน Pod web ผ่าน port-forward](images/03-first-page-on-kubernetes.png)

ภาพนี้ capture จากระบบจริงที่ขั้นนี้ ไม่ใช่ภาพจำลอง

## 7. หนึ่ง Pod มีสอง container

อ่าน manifest `02-pod-with-sidecar.yaml` สั้น ๆ ก่อน apply:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web2
  namespace: lab003
  labels:
    app: web
spec:
  containers:
    - name: web
      image: k8s-lab-web:v1
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 3000
    - name: sidecar
      image: busybox:1.36.1
      imagePullPolicy: IfNotPresent
      command: ["sh", "-c"]
      args:
        - while true; do
            wget -qO- http://127.0.0.1:3000/healthz;
            echo;
            sleep 10;
          done
```
> 📝 **คำอธิบาย:** `apiVersion/kind` เลือกชนิด API · `metadata` ตั้งชื่อ/namespace/label · `spec.containers` มีสมาชิกสองตัว · `command` เปิด shell · `args` เป็น loop เรียก health ทุก 10 วินาที · `imagePullPolicy` ใช้ image ที่ node มี · sidecar ใช้ IPv4 loopback เพราะ `localhost` ใน web image รอบนี้ต่อไม่ได้

apply แล้วตรวจทั้งจำนวน container และ log ของ sidecar:
```bash
kubectl apply -f 02-pod-with-sidecar.yaml
kubectl wait -n lab003 --for=condition=Ready pod/web2 --timeout=120s
kubectl get pod web2 -n lab003 -o jsonpath='{.spec.containers[*].name}{"\n"}'
kubectl logs web2 -n lab003 -c sidecar --tail=5
```
> 📝 **คำอธิบาย:** `apply -f` ส่ง desired object จากไฟล์ · `wait` รอ Pod Ready · `--timeout` กันค้าง · JSONPath เลือกชื่อ container · `logs web2` ต้องเติม `-c sidecar` เพราะ Pod มีหลาย container · `--tail=5` จำกัดผล

✅ **Expected output** — Pod พร้อมและ sidecar ได้ health response จาก web ผ่าน loopback ร่วม:
```text
pod/web2 created
pod/web2 condition met
web sidecar
{"status":"ok","pod":"web2","version":"v1"}
```
ถ้า sidecar ต้องวิ่งข้าม Pod จะใช้ `127.0.0.1` ไม่ได้ หลักฐานนี้จึงพิสูจน์ network namespace ร่วมกัน

## 8. ลบ Pod เดี่ยวแล้วสังเกตความว่าง

หยุด port-forward ด้วย `Ctrl+C` แล้วลบ `web`:
```bash
kubectl delete pod web -n lab003
kubectl get pods -n lab003
```
> 📝 **คำอธิบาย:** `delete pod` ลบ object ที่ไม่มี controller เจ้าของ · `get pods` ตรวจ actual state · `web2` ยังอยู่เพราะเป็นคนละ object

✅ **Expected output** — `web` หายและไม่มี `web-...` ตัวใหม่เกิดแทน:
```text
pod "web" deleted from lab003 namespace
NAME   READY   STATUS    RESTARTS   AGE
web2   2/2     Running   0          33s
```
AGE ต่างกันได้ จำภาพนี้ไว้เทียบ LAB 006

## 9. ทดลองให้พัง — ใช้ image tag ที่ไม่มีจริง
```bash
kubectl run web-broken --image=k8s-lab-web:v9 -n lab003
sleep 25
kubectl get pod web-broken -n lab003
kubectl describe pod web-broken -n lab003 | sed -n '/Events:/,$p'
```
> 📝 **คำอธิบาย:** สร้าง Pod ด้วย tag `v9` ที่ไม่ได้ build/load · `sleep 25` รอให้ kubelet pull ซ้ำจนเห็น backoff · `get` บอกอาการ · `describe` เปิดเหตุผลจาก Events

✅ **Expected output** — เห็นทั้ง ErrImagePull และการ back off หลังลองซ้ำ:
```text
pod/web-broken created
web-broken   0/1   ImagePullBackOff   0   21s
Warning  Failed   Failed to pull image "k8s-lab-web:v9": failed to pull and unpack image "docker.io/library/k8s-lab-web:v9": failed to resolve reference "docker.io/library/k8s-lab-web:v9": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
Warning  Failed   Error: ErrImagePull
Normal   BackOff  Back-off pulling image "k8s-lab-web:v9"
Warning  Failed   Error: ImagePullBackOff
```
AGE และจำนวน retry ต่างกันได้ สาเหตุอยู่ชั้น image ไม่ใช่โค้ด Next.js เพราะ container ยังเริ่มไม่ได้

แก้กลับโดยลบ object ที่ตั้งใจสร้างผิด:
```bash
kubectl delete pod web-broken -n lab003
kubectl get pods -n lab003
```
> 📝 **คำอธิบาย:** `delete` หยุดการ retry ของ kubelet · `get` ยืนยันว่าเหลือเฉพาะ Pod ที่ดี · ทางแก้อีกแบบในงานจริงคือแก้ tag/load image ผ่าน controller แต่ Pod เปล่าแก้ spec ส่วนใหญ่ไม่ได้

✅ **Expected output** — broken Pod หายและ web2 ยังปกติ:
```text
pod "web-broken" deleted from lab003 namespace
NAME   READY   STATUS    RESTARTS   AGE
web2   2/2     Running   0          92s
```

## 10. แบบฝึกหัดสั้น (Exercise)

วาด Pod เป็นซองหนึ่งใบ ใส่ web และ sidecar แล้วเขียนกำกับว่าสิ่งใดแชร์กัน
จากนั้นตอบว่าเหตุใด database จึงไม่ควรใส่ในซองเดียวกับ web เพียงเพราะ “คุยผ่าน localhost ได้”

ถือว่าสำเร็จเมื่อระบุ shared network/IP/lifecycle ได้ และอธิบายได้ว่า web กับ DB ต้อง scale/update/fail แยกกัน

## วิธีตรวจสอบผลการทดลอง
```bash
kubectl get pods -n lab003
kubectl logs web2 -n lab003 -c sidecar --tail=1
kubectl get events -n lab003 --sort-by=.lastTimestamp | tail -12
```
> 📝 **คำอธิบาย:** `get` ตรวจ READY `2/2` · `logs -c` พิสูจน์การคุยข้าม container · `events` เรียงหลักฐานตามเวลาและเก็บทั้ง success/failure ที่เพิ่งทดลอง

✅ **Expected output** — web2 พร้อม, health ตอบ ok และ Events มี Started ของสอง container:
```text
web2   2/2   Running   0   92s
{"status":"ok","pod":"web2","version":"v1"}
90s   Normal    Pulling   pod/web2         Pulling image "busybox:1.36.1"
90s   Normal    Started   pod/web2         Container started
84s   Normal    Started   pod/web2         Container started
84s   Normal    Created   pod/web2         Container created
84s   Normal    Pulled    pod/web2         Successfully pulled image "busybox:1.36.1" in 5.351s (5.351s including waiting). Image size: 2217006 bytes.
59s   Normal    Killing   pod/web          Stopping container web
33s   Normal    Scheduled pod/web-broken   Successfully assigned lab003/web-broken to devtools-worker
19s   Normal    Pulling   pod/web-broken   Pulling image "k8s-lab-web:v9"
17s   Warning   Failed    pod/web-broken   Failed to pull image "k8s-lab-web:v9": failed to pull and unpack image "docker.io/library/k8s-lab-web:v9": failed to resolve reference "docker.io/library/k8s-lab-web:v9": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
17s   Warning   Failed    pod/web-broken   Error: ErrImagePull
3s    Warning   Failed    pod/web-broken   Error: ImagePullBackOff
3s    Normal    BackOff   pod/web-broken   Back-off pulling image "k8s-lab-web:v9"
```
ชื่อ Pod, AGE และลำดับ Events ต่างกันได้ บรรทัด Warning ยืนยันว่าปัญหาอยู่ที่ image/tag ไม่ใช่ process ในแอป

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `ImagePullBackOff` | tag ผิดหรือยังไม่ `kind load` | ตรวจ describe แล้ว build/load tag ที่ถูก |
| `logs` บอกให้เลือก container | Pod มีหลาย container | เติม `-c web` หรือ `-c sidecar` |
| `localhost` ได้ connection refused | `localhost` resolve เป็น IPv6 แต่แอปฟัง IPv4 | ระบุ `127.0.0.1` เพื่อใช้ IPv4 loopback |
| browser เข้า port 3000 ไม่ได้ | port-forward จบหรือ bind แค่ loopback ใน container | รันใหม่พร้อม `--address 0.0.0.0` |
| ลบ Pod แล้วไม่กลับมา | Pod เปล่าไม่มี controller ถือ desired count | เป็นพฤติกรรมที่ถูก; ใช้ controller ใน LAB 006 |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

ลบ namespace แรก สร้างใหม่จาก manifest ตรวจผลเดิม แล้วลบปิดท้าย:
```bash
kubectl delete namespace lab003 --wait=true --timeout=90s
kubectl create namespace lab003
kubectl apply -f 02-pod-with-sidecar.yaml
kubectl wait -n lab003 --for=condition=Ready pod/web2 --timeout=120s
kubectl get pods -n lab003
kubectl logs web2 -n lab003 -c sidecar --tail=1
kubectl delete namespace lab003 --wait=true --timeout=90s
kubectl get all -n lab003
```
> 📝 **คำอธิบาย:** การลบ namespace เก็บทุก object ในห้อง · `--wait` รอ cleanup · `create` เตรียมห้องใหม่เพราะ manifest ระบุ namespace · `apply -f` สร้าง Pod จากไฟล์ · `wait/get/logs` พิสูจน์ผลเดิม · ลบครั้งสุดท้ายและ `get all` กันของค้าง

✅ **Expected output** — clean run ได้ `2/2 Running`, sidecar ตอบ ok แล้ว namespace ว่างหลังลบ:
```text
namespace "lab003" deleted
namespace/lab003 created
pod/web2 created
pod/web2 condition met
web2   2/2   Running   0   14s
{"status":"ok","pod":"web2","version":"v1"}
namespace "lab003" deleted
No resources found in lab003 namespace.
```
AGE ต่างกันได้ และต้องไม่มี process `kubectl port-forward` ค้างก่อนขึ้นแล็บถัดไป

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl run` | สร้าง Pod แบบ imperative |
| `kubectl get pods -w` | เฝ้าการเปลี่ยนสถานะ |
| `kubectl logs POD [-c NAME]` | อ่าน log ของ container |
| `kubectl exec POD -- CMD` | รันคำสั่งใน container |
| `kubectl port-forward` | เปิดทางชั่วคราวไป Pod/Service |
| `kubectl apply -f FILE` | สร้าง/ปรับ object จาก desired state ในไฟล์ |

## สรุปสิ่งที่ได้เรียนรู้

Pod เป็นเส้นแบ่งที่ Kubernetes ใช้ schedule และดูแล lifecycle ไม่ใช่เพียงชื่อใหม่ของ container
web กับ sidecar ใน `web2` พิสูจน์ด้วย response จริงว่าแชร์ loopback และถูกนับ Ready รวมกันเป็น `2/2`

- อธิบาย Pod เทียบกับ container ได้
- อ่าน Events และ logs เพื่อไล่วงจรเริ่มงานได้
- เปิดหน้าเว็บจริงและเห็น identity ของ Pod ได้
- แยกอาการระดับ image ออกจากอาการระดับแอปได้

**จำภาพเดียวให้ได้:** Pod คือซองที่ Kubernetes ย้ายทั้งใบ—container ข้างในแชร์ที่อยู่และชะตาเดียวกัน

🧭 ต่อยอด: [LAB 004 — Declarative YAML](../004-declarative-yaml/README.md) จะเปลี่ยนจากคำสั่ง imperative ไปประกาศ desired state ด้วยไฟล์

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **Pod ต่างจาก container อย่างไร?** — Pod เป็นหน่วย schedule ที่ครอบ container และกำหนด network/volume/lifecycle ร่วมกัน
2. **ทำไมหน่วยเล็กสุดจึงเป็น Pod?** — แอปกับตัวช่วยที่ต้องอยู่เครื่อง/IP เดียวกันถูกจัดกลุ่มและย้ายทั้งชุดได้
3. **ลบ Pod แล้วทำไมไม่มีตัวใหม่?** — Pod เปล่าไม่มี controller ถือ desired count

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] เห็น web เปลี่ยนจาก ContainerCreating เป็น Running
- [ ] เห็น web2 เป็น `2/2 Running`
- [ ] sidecar ได้ health JSON ผ่าน shared loopback
- [ ] เห็น ErrImagePull และ ImagePullBackOff จริง
- [ ] อธิบายได้ว่าทำไมลบ Pod แล้วไม่เกิดใหม่
- [ ] ลบ namespace และ port-forward จนไม่เหลือ

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
