# LAB 9 — Service Types and Access : ต่างกันที่ใครเข้าถึงได้

> โฟลเดอร์ `009-service-types-and-access` = LAB 9 ของชุด Kubernetes ครั้งที่ 2
> (ไฟล์ของแล็บนี้: `01-api.yaml`, `02-web-nodeport.yaml`, `03-nodeport-bad.yaml` และ `images/`)

> 💡 **แนวคิดหลักของแล็บนี้:** Service มีหลายแบบ ต่างกันที่ "ใครเข้าถึงได้" ไม่ใช่ที่การทำงาน

## วัตถุประสงค์ของแล็บ

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายขอบเขตการเข้าถึงของ ClusterIP และ NodePort ได้
2. อธิบาย `port`, `targetPort` และ `nodePort` ว่าอยู่คนละชั้นอย่างไร
3. พิสูจน์ว่า NodePort เดียวกันเปิดบนทุก node แม้ Pod ไม่ได้อยู่ทุก node
4. เลือกชนิด Service ให้ web และ api ตามผู้เรียกที่ต้องการได้

## แนวคิดและทฤษฎีที่เกี่ยวข้อง

ใน Compose เรา publish `ports:` เฉพาะ web ส่วน api/db อยู่ใน network ภายใน; กฎเดียวกันใช้กับ Kubernetes:

| ชนิด | ผู้เรียก | ปลายทางที่เปิด | ใช้กับ |
|---|---|---|---|
| ClusterIP | Pod ภายใน cluster | Service IP/DNS | api, db |
| NodePort | ภายนอกที่เข้าถึง Node IP ได้ | `<NodeIP>:30000-32767` | ทดสอบ/ห้องเรียน |
| LoadBalancer | ผู้ใช้ภายนอกผ่าน cloud LB | external IP | งาน cloud |
| Ingress | HTTP client ผ่านประตู L7 | host/path เดียว | web/API หลาย route |

NodePort ไม่ใช่ Service คนละกลไกจาก ClusterIP แต่เป็น ClusterIP ที่เพิ่มทางเข้าบนทุก node
ในแล็บนี้ api จึงซ่อนด้วย ClusterIP ส่วน web เปิด NodePort 30080

| field | อยู่ตรงไหน | หน้าที่ |
|---|---|---|
| `port: 3000` | Service | พอร์ตที่ client ใน cluster เรียก |
| `targetPort: http` | Pod | ส่งต่อไป named containerPort 3000 |
| `nodePort: 30080` | ทุก Node | พอร์ตที่ผู้เรียกนอก cluster ใช้ |

## สิ่งที่จะได้เรียนรู้

- จะได้อ่าน TYPE และ `3000:30080/TCP` จาก Service จริง
- จะได้เรียก NodePort ผ่าน control-plane และ worker ทั้งสอง
- จะได้เห็น ClusterIP timeout จากเครื่องเรียน
- จะได้เรียก ClusterIP ผ่านชื่อ `api` จากใน web Pod สำเร็จ
- จะได้อ่าน error ของ nodePort นอกช่วงและพอร์ตซ้ำ

## ภาพรวมของแล็บนี้

1. สร้าง api แบบ ClusterIP และ web แบบ NodePort
2. ยิง NodePort ที่ IP ของ kind nodes ทั้งสาม
3. เทียบ ClusterIP จากนอก/ใน cluster
4. เปิดหน้าเว็บผ่าน port-forward และอ่านสามพอร์ตใน YAML
5. apply Service ผิดสองแบบแล้วแก้กลับ

![ClusterIP เปิดภายใน ส่วน NodePort เปิดพอร์ตเดียวกันบนทุก Node](../slides_assets/lab009-architecture.svg)

> **คำถามก่อนเริ่ม:** ถ้า web Pod อยู่ worker2 เหตุใด request ที่เข้า NodePort ของ control-plane จึงยังถึง web ได้?

## 0. เตรียมเครื่องเรียน

รันคำสั่งแรกบนเครื่องหลัก แล้ว `docker exec` เข้าเครื่องเรียน; ทุกคำสั่งหลังจากนั้นพิมพ์ในเครื่องเรียน ในเทอร์มินัลของเครื่องเรียนใช้ `localhost` พอร์ต 80 ส่วนเบราว์เซอร์บนเครื่องของคุณใช้ `http://localhost:8080`

```bash
docker start devtools-k8s || docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
k8s-bootstrap
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
```

> 📝 **คำอธิบาย:** `docker start` ใช้เครื่องเดิม · `|| docker run` สร้างเครื่องเมื่อยังไม่มี · `docker exec -it ... bash` เข้าเครื่องเรียน · `k8s-bootstrap` สร้าง cluster และข้ามเองถ้ามีแล้ว · `get nodes` และ `crictl` ตรวจ cluster/image

✅ **Expected output** — nodes ทั้งสาม Ready และ image อยู่ใน node (ตัดบางคอลัมน์; AGE และ image ID ต่างกันได้):

```text
NAME                     STATUS   ROLES           AGE   VERSION
devtools-control-plane   Ready    control-plane   24m   v1.36.4
devtools-worker          Ready    <none>          23m   v1.36.4
devtools-worker2         Ready    <none>          23m   v1.36.4
docker.io/library/k8s-lab-api  v1  682aa17deaef3  186MB
docker.io/library/k8s-lab-db   v1  901da7602fb40  300MB
docker.io/library/k8s-lab-web  v1  a389e8bc3c5ed  209MB
docker.io/library/k8s-lab-web  v2  65ea95c8496b6  209MB
…
```

ถ้า image ยังไม่อยู่ใน kind ให้ทำขั้น build/load ของแล็บ 001 หรือ README ระดับชุดก่อน

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork && git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/009-service-types-and-access
```

> 📝 **คำอธิบาย:** `mkdir -p` เตรียม workspace · `git clone` ดึงชุดเรียน · `cd` เข้า LAB 009 เพื่อใช้ manifest ตามลำดับ

✅ **Expected output** — clone สำเร็จและเข้าโฟลเดอร์ได้โดยไม่มี error:

```text
Cloning into 'DevTools'...
```

ถ้า clone ไว้แล้ว ให้ใช้ `git pull` ใน `~/labwork/DevTools` แล้วกลับมาโฟลเดอร์นี้

## 2. อ่าน YAML ของแล็บนี้

| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |
|---|---|---|---|
| `01-api.yaml` | Deployment, Service | เปิด API ภายในด้วย ClusterIP | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `02-web-nodeport.yaml` | Deployment, Service | เปิด web ด้วย NodePort 30080 | [Deployment](../YAML_Guide.md#deployment) · [Service](../YAML_Guide.md#service) |
| `03-nodeport-bad.yaml` | Service ×2 | จงใจใช้ nodePort ผิดช่วงและซ้ำ | ตาราง error ด้านล่าง |

ส่วน Service จริงจาก `02-web-nodeport.yaml`:

```yaml
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 3000
      targetPort: http
      nodePort: 30080
```

| field | ความหมาย | ถ้าเปลี่ยนค่านี้ |
|---|---|---|
| `type` | `ClusterIP` รับจากใน cluster; `NodePort` เพิ่มพอร์ตบนทุก Node | เว้นไว้จะ default เป็น `ClusterIP` |
| `port` | พอร์ตของ Service | client ภายในต้องเรียกเลขใหม่ |
| `targetPort` | เลขหรือชื่อพอร์ตของ Pod | ต้องตรง `containerPort`/ชื่อ port ของ web |
| `nodePort` | พอร์ตภายนอก; ปกติ 30000–32767 | เว้นไว้ให้ระบบจัดสรร หรือระบุเลขว่างในช่วง |

**ผิดบ่อยในแล็บนี้:** runlog ของ `03-nodeport-bad.yaml` มีข้อความจริง `provided port is not in the valid range. The range of valid ports is 30000-32767` และ `provided port is already allocated` จึงต้องอ่านเลขที่ `spec.ports[0].nodePort` ไม่ใช่แก้ `port`

ดู schema ได้ด้วย `kubectl explain service.spec.type` และ `kubectl explain service.spec.ports.nodePort`

## 3. สร้าง ClusterIP และ NodePort

`01-api.yaml` มี API Deployment + ClusterIP; `02-web-nodeport.yaml` มี web 2 replicas + NodePort 30080

```bash
kubectl create namespace lab009
kubectl apply -f 01-api.yaml -f 02-web-nodeport.yaml
kubectl wait -n lab009 --for=condition=available deployment/api deployment/web --timeout=120s
until kubectl exec -n lab009 deployment/web -- wget -qO- http://api:8000/health >/dev/null 2>&1; do sleep 1; done
kubectl get service -n lab009
kubectl get pods -n lab009 -o wide
```

> 📝 **คำอธิบาย:** namespace แยกแล็บ · `wait` รอ available · `until ... /health` รอ API process ฟังพอร์ตจริง · `get service` เทียบ TYPE/PORT(S) · `-o wide` ดูว่า Pod อยู่ Node ใด

✅ **Expected output** — api เป็น ClusterIP, web เป็น NodePort และ Pod ทั้งสาม Running (ชื่อ/IP/Node/AGE ต่างกันได้):

```text
namespace/lab009 created
deployment.apps/api created
service/api created
deployment.apps/web created
service/web created
deployment.apps/api condition met
deployment.apps/web condition met
NAME   TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
api    ClusterIP   10.96.5.88    <none>        8000/TCP         1s
web    NodePort    10.96.53.54   <none>        3000:30080/TCP   1s
NAME                   READY   STATUS    RESTARTS   AGE   IP            NODE               NOMINATED NODE   READINESS GATES
api-5bdf56b96d-5hbxr   1/1     Running   0          1s    10.244.2.21   devtools-worker    <none>           <none>
web-74bf7d87c4-bkx9r   1/1     Running   0          1s    10.244.1.12   devtools-worker2   <none>           <none>
web-74bf7d87c4-nn5dv   1/1     Running   0          1s    10.244.2.22   devtools-worker    <none>           <none>
```

## 4. พิสูจน์ว่า NodePort เปิดบนทุก Node

```bash
kubectl get nodes -o wide
for NODE_IP in $(kubectl get nodes -o jsonpath='{range .items[*]}{.status.addresses[?(@.type=="InternalIP")].address}{"\n"}{end}'); do
  printf "%s -> " "$NODE_IP"
  curl -s -H 'Connection: close' "http://$NODE_IP:30080/info" | jq -c '{pod}'
done
```

> 📝 **คำอธิบาย:** `get nodes -o wide` จับคู่ชื่อ node กับ InternalIP · `jsonpath` ดึง IP ทุก node · `nodePort 30080` เหมือนกันทุก node · `Connection: close` เปิด connection ใหม่ · `jq -c '{pod}'` คงรูป JSON บรรทัดเดียวและบอกผู้ตอบจริง

✅ **Expected output** — IP ทั้งสามตอบได้ และ request ไปถึง web สอง Pod ได้แม้ control-plane ไม่มี web Pod (IP/ชื่อ Pod ต่างกันได้):

```text
NAME                     STATUS   ROLES           AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
devtools-control-plane   Ready    control-plane   3m9s    v1.36.4   172.18.0.3    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
devtools-worker          Ready    <none>          2m59s   v1.36.4   172.18.0.4    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
devtools-worker2         Ready    <none>          2m59s   v1.36.4   172.18.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
172.18.0.3 -> {"pod":"web-74bf7d87c4-pc6pn"}
172.18.0.4 -> {"pod":"web-74bf7d87c4-pc6pn"}
172.18.0.2 -> {"pod":"web-74bf7d87c4-7qksk"}
```

NodePort ของจริงเปิดที่ Node IP แต่ kind nodes อยู่ใน Docker อีกชั้น นักศึกษาจึงใช้ port-forward ในหัวข้อ 6 เพื่อเปิดจาก browser ตาม environment ของชุดเรียน

## 5. พิสูจน์ขอบเขตของ ClusterIP

ลองจาก shell ของเครื่องเรียนซึ่งอยู่นอก network namespace ของ kind nodes:

```bash
API_CLUSTER_IP=$(kubectl get service api -n lab009 -o jsonpath='{.spec.clusterIP}')
curl -sS -m 3 "http://$API_CLUSTER_IP:8000/health"
echo "curl exit code=$?"
kubectl exec -n lab009 deployment/web -- wget -qO- http://api:8000/health
```

> 📝 **คำอธิบาย:** อ่าน ClusterIP จริง · `-m 3` จำกัดเวลารอ · exit 28 คือ timeout จากนอก cluster · `kubectl exec` เปลี่ยนมุมผู้เรียกเป็น Pod ภายใน · `api` คือ Service DNS

✅ **Expected output** — จากเครื่องเรียน timeout แต่จาก web Pod ได้ JSON 200 (ชื่อ API Pod ต่างกันได้):

```text
curl: (28) Connection timed out after 3002 milliseconds
curl: (28) Connection timed out after 3002 milliseconds
curl: (28) Connection timed out after 3002 milliseconds
curl: (28) Connection timed out after 3002 milliseconds
curl: (28) Connection timed out after 3002 milliseconds
curl: (28) Connection timed out after 3001 milliseconds
curl exit code=28
{"status":"ok","pod":"api-5bdf56b96d-5hbxr","version":"v1"}
```

เครื่องเรียนมี curl retry policy จึงเห็น timeout ซ้ำ แต่ผลสุดท้ายยังเป็น exit code 28 เหมือนเดิม

## 6. เปิดหน้าเว็บผ่าน port-forward

เปิดหน้าต่างใหม่บนเครื่องหลักแล้ว `docker exec -it devtools-k8s bash` อีกครั้ง จากนั้นรันคำสั่งนี้ในเครื่องเรียนหน้าต่างที่สองและคง process ไว้; ใช้หน้าต่างแรกทำหัวข้อถัดไป:

```bash
kubectl port-forward -n lab009 service/web 3000:3000 --address 0.0.0.0
```

> 📝 **คำอธิบาย:** `service/web` ให้ kubectl เลือก Pod หลัง Service · `3000:3000` map local ไป Service port · `--address 0.0.0.0` ให้ browser นอกเครื่องเรียนเข้าถึงได้ · หยุดด้วย `Ctrl+C`

✅ **Expected output** — tunnel ฟัง port 3000 และมี Handling connection เมื่อเปิด `http://localhost:3000`:

```text
Forwarding from 0.0.0.0:3000 -> 3000
Handling connection for 3000
```

![หน้า SkillSpace ผ่าน port-forward แสดงชื่อ web Pod และ API Pod](images/04-web-via-port-forward.png)

## 7. อ่าน port, targetPort และ nodePort

```bash
kubectl get service web -n lab009 -o yaml | grep -A4 'ports:'
kubectl logs -n lab009 deployment/api --tail=8
```

> 📝 **คำอธิบาย:** YAML แสดง mapping ครบสามชั้น · `grep -A4` จำกัด output · logs ยืนยัน `/health` จาก web เดินถึง API ภายในผ่าน ClusterIP

✅ **Expected output** — port 3000 ส่งไป named port http และ NodePort 30080; `/ready` 503 เป็นปกติเพราะแล็บนี้ยังไม่มี db ก่อนที่ log จะมี `/health` 200:

```text
  ports:
  - nodePort: 30080
    port: 3000
    protocol: TCP
    targetPort: http
[api] GET /ready 503 3ms
INFO:     10.244.2.22:40524 - "GET /ready HTTP/1.1" 503 Service Unavailable
[api] GET /ready 503 3ms
INFO:     10.244.2.22:40524 - "GET /ready HTTP/1.1" 503 Service Unavailable
[api] GET /ready 503 2ms
INFO:     10.244.1.12:43942 - "GET /ready HTTP/1.1" 503 Service Unavailable
[api] GET /health 200 1ms
INFO:     10.244.1.12:47780 - "GET /health HTTP/1.1" 200 OK
```

## 8. ทดลองให้พัง — nodePort ผิดช่วงและซ้ำ

`03-nodeport-bad.yaml` มี Service ผิดสอง document เพื่อให้ API server ตรวจพร้อมกัน:

```bash
kubectl apply -f 03-nodeport-bad.yaml
kubectl get service -n lab009
```

> 📝 **คำอธิบาย:** Service แรกใช้ 3000 นอกช่วง · Service ที่สองแย่ง 30080 จาก web · `get service` ยืนยันว่า object ที่ผิดไม่ถูกสร้างค้าง

✅ **Expected output** — API server ปฏิเสธทั้งสองเหตุผล และเหลือเฉพาะ api/web เดิม:

```text
Error from server (Invalid): error when creating "03-nodeport-bad.yaml": Service "web-bad-range" is invalid: spec.ports[0].nodePort: Invalid value: 3000: provided port is not in the valid range. The range of valid ports is 30000-32767
Error from server (Invalid): error when creating "03-nodeport-bad.yaml": Service "web-duplicate" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated
NAME   TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
api    ClusterIP   10.96.5.88    <none>        8000/TCP         107s
web    NodePort    10.96.53.54   <none>        3000:30080/TCP   107s
```

ไฟล์ผิดไม่เปลี่ยน desired state เดิม แก้กลับโดย apply ไฟล์ถูก:

```bash
kubectl apply -f 02-web-nodeport.yaml
kubectl get service web -n lab009
```

> 📝 **คำอธิบาย:** apply manifest ที่ถูกต้องซ้ำเพื่อยืนยัน idempotency · `get` ตรวจว่า NodePort เดิมยังอยู่

✅ **Expected output** — Deployment/Service unchanged และ 30080 ยังใช้งานได้:

```text
deployment.apps/web unchanged
service/web unchanged
NAME   TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
web    NodePort   10.96.53.54   <none>        3000:30080/TCP   107s
```

## 9. แบบฝึกหัดสั้น (Exercise)

ออกแบบตาราง Service สำหรับ `web`, `api`, `db` โดยเลือก TYPE และผู้เรียก ถือว่าสำเร็จเมื่อ web เปิดสู่ผู้ใช้ แต่ api/db ไม่มี NodePort และอธิบายเหตุผลด้าน attack surface ได้

## วิธีตรวจสอบผลการทดลอง

```bash
kubectl get pods,service -n lab009 -o wide
kubectl exec -n lab009 deployment/web -- wget -qO- http://api:8000/health
NODE_IP=$(kubectl get node devtools-control-plane -o jsonpath='{.status.addresses[0].address}')
curl -s -H 'Connection: close' "http://$NODE_IP:30080/info" | jq -c '{pod,api}'
```

> 📝 **คำอธิบาย:** ตรวจ resource/ตำแหน่ง Pod · ตรวจ api จากด้านใน · ดึง InternalIP ของ control-plane จาก object จริง แล้วตรวจ NodePort โดยไม่ hard-code IP

✅ **Expected output** — web 2/API 1 พร้อม, internal health ok และ NodePort ตอบชื่อ Pod จริง (ตัดบางคอลัมน์; ค่า IP/Pod/AGE ต่างกันได้):

```text
…
api-5bdf56b96d-5hbxr   1/1   Running   10.244.2.21   devtools-worker
web-74bf7d87c4-bkx9r   1/1   Running   10.244.1.12   devtools-worker2
web-74bf7d87c4-nn5dv   1/1   Running   10.244.2.22   devtools-worker
api   ClusterIP   10.96.5.88    8000/TCP
web   NodePort    10.96.53.54   3000:30080/TCP
{"status":"ok","pod":"api-5bdf56b96d-5hbxr","version":"v1"}
{"pod":"web-74bf7d87c4-nn5dv","api":{"configured":true,"reachable":true,"pod":"api-5bdf56b96d-5hbxr"}}
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| ClusterIP จากเครื่องเรียน timeout | ClusterIP ออกแบบให้ใช้ใน cluster | ทดสอบจาก Pod ด้วย `kubectl exec` |
| NodePort apply ไม่ผ่าน | นอกช่วงหรือพอร์ตถูกจอง | ใช้ 30000–32767 และตรวจ Service อื่น |
| host เปิด `<NodeIP>:30080` ไม่ได้ใน kind | node ซ้อนอยู่ใน Docker | ใช้ port-forward ตามหัวข้อ 6 |
| port-forward บอก address in use | process เก่ายังจับ port 3000 | กด Ctrl+C/kill process เก่าก่อนเปิดใหม่ |

## เก็บกวาด (Cleanup) และพิสูจน์ Clean Re-run

กลับไปหน้าต่างที่สอง กด `Ctrl+C` หยุด port-forward แล้วกลับมารันคำสั่งต่อในหน้าต่างแรก:

```bash
kubectl delete namespace lab009
kubectl wait --for=delete namespace/lab009 --timeout=120s
kubectl create namespace lab009
kubectl apply -f 01-api.yaml -f 02-web-nodeport.yaml
kubectl wait -n lab009 --for=condition=available deployment/api deployment/web --timeout=120s
kubectl get deploy,pods,service -n lab009
NODE_IP=$(kubectl get node devtools-control-plane -o jsonpath='{.status.addresses[0].address}')
curl -s -H 'Connection: close' "http://$NODE_IP:30080/info" | jq -c '{pod,api}'
```

> 📝 **คำอธิบาย:** ลบ namespace และรอให้หาย · สร้างจากสองไฟล์หลัก · รอ Deployment · ตรวจ NodePort จาก control-plane IP ซึ่งเปลี่ยนได้ตาม cluster

✅ **Expected output** — Clean Re-run ได้ API 1, web 2 และ NodePort ตอบพร้อม API reachable (IP/ชื่อ/AGE ต่างกันได้; ตัดบางแถว/บางคอลัมน์):

```text
…
namespace "lab009" deleted
namespace/lab009 created
deployment.apps/api created
service/api created
deployment.apps/web created
service/web created
deployment.apps/api condition met
deployment.apps/web condition met
deployment.apps/api   1/1   1   1   4s
deployment.apps/web   2/2   2   2   4s
service/api   ClusterIP   10.96.53.207   8000/TCP
service/web   NodePort    10.96.14.160   3000:30080/TCP
{"pod":"web-74bf7d87c4-lcqdt","api":{"configured":true,"reachable":true,"pod":"api-5bdf56b96d-l8hdh"}}
```

```bash
kubectl delete namespace lab009
kubectl wait --for=delete namespace/lab009 --timeout=120s
kubectl get all -n lab009
```

> 📝 **คำอธิบาย:** ลบรอบสุดท้าย · `get all` พิสูจน์ว่า namespace ไม่มี resource; tunnel ถูกหยุดด้วย `Ctrl+C` ก่อนหน้าแล้ว

✅ **Expected output** — จบสะอาดและไม่มี namespace resource:

```text
namespace "lab009" deleted
No resources found in lab009 namespace.
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `kubectl get service` | อ่าน TYPE, ClusterIP และ PORT(S) |
| `curl <NodeIP>:30080` | เข้าถึง NodePort จากนอก cluster |
| `kubectl exec ... wget http://api:8000` | เข้าถึง ClusterIP จากใน cluster |
| `kubectl port-forward service/web` | เปิด tunnel สำหรับเครื่องเรียน |

## สรุปสิ่งที่ได้เรียนรู้

ClusterIP และ NodePort ส่งงานไป Pod ด้วย selector เหมือนกัน ต่างกันตรงขอบเขตของผู้เรียก: ภายในเท่านั้นหรือผ่านทุก Node IP

- api ที่ไม่มีผู้ใช้ภายนอกเรียกควรเป็น ClusterIP
- NodePort เพิ่มทางเข้า แต่ไม่ได้บังคับว่า Pod ต้องอยู่ Node ที่รับ request
- `port`, `targetPort`, `nodePort` อยู่คนละช่วงของเส้นทาง

**จำภาพเดียวให้ได้:** ClusterIP คือประตูห้องด้านใน; NodePort คือเพิ่มกริ่งหมายเลขเดียวกันไว้ที่หน้าทุก node

🧭 ต่อยอด: แล็บ 010 จะแยก config ของหน้าเว็บออกจาก image โดยใช้ ConfigMap

## ❓ คำถามที่ต้องตอบได้ก่อนจบแล็บ

1. **ClusterIP กับ NodePort ต่างกันตรงไหน?** — NodePort เพิ่มพอร์ตบนทุก node; ClusterIP ให้เรียกใน cluster
2. **ใช้อันไหนเมื่อไร?** — api/db ใช้ ClusterIP; NodePort เหมาะกับทดลอง ส่วนงานจริงมักใช้ LoadBalancer/Ingress
3. **ทำไม NodePort จำกัด 30000–32767?** — แยกช่วงพอร์ตบริการออกจากพอร์ตระบบและจองเลขเดียวกันบนทุก node

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] แยก ClusterIP กับ NodePort จาก `kubectl get svc` ได้แล้ว
- [ ] ยิง NodePort ผ่านทั้งสาม Node IP ได้แล้ว
- [ ] พิสูจน์ ClusterIP จากนอก timeout แต่จาก Pod สำเร็จแล้ว
- [ ] เห็น error nodePort ผิดช่วงและซ้ำแล้ว
- [ ] Clean Re-run ผ่านและไม่มี port-forward/namespace ค้าง

*Expected output และ screenshot ในเอกสารนี้มาจากการรันจริงบน tuchsanai/devtools-k8s:2569_1 (kind v0.33.0 · Kubernetes v1.36.4 · kubectl v1.37.0) เมื่อ 2 กันยายน 2026*
