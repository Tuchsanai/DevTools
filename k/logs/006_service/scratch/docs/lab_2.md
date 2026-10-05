## LAB 5: การกระจายโหลดและ sessionAffinity

{{FIG:L07}}

**เป้าหมาย:** เห็นว่า kube-proxy เลือก Pod แบบสุ่มต่อ connection และเห็นผลของ `sessionAffinity: ClientIP`

**ต้องมีจาก LAB 4:** Service `web`, Pod `client` และ `client2`

### ขั้นที่ 1: ยิง 30 ครั้ง 2 รอบ

`wget` ของ busybox เปิด connection ใหม่ทุกครั้ง จึงเหมาะกับการดูการสุ่ม `sort | uniq -c` นับว่าแต่ละบรรทัดซ้ำกี่ครั้ง

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
```

```text
      4 web v1 from web-gsgss
     14 web v1 from web-k2nk5
     12 web v1 from web-mgz49

      8 web v1 from web-gsgss
      9 web v1 from web-k2nk5
     13 web v1 from web-mgz49
```

ทุก Pod ได้ลูกค้า แต่ **ไม่เท่ากันและแต่ละรอบต่างกัน** เพราะเป็นการสุ่มต่อ connection ไม่ใช่การวนตามลำดับ (round-robin) ตัวเลขในเครื่องนักศึกษาจะต่างจากนี้แน่นอน

### ขั้นที่ 2: เปิด sessionAffinity: ClientIP

```bash
kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"ClientIP"}}'
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
kubectl -n shop exec client2 -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinityConfig}'; echo
```

```text
service/web patched
     30 web v1 from web-k2nk5
     30 web v1 from web-mgz49
{"clientIP":{"timeoutSeconds":10800}}
```

`client` ไปบูธเดียวครบ 30/30 และ `client2` (คนละ IP) ก็ไปบูธเดียวของตัวเองครบ 30/30 (อาจเป็นบูธเดียวกับ `client` หรือไม่ก็ได้) API เติม `timeoutSeconds: 10800` (3 ชั่วโมง) ให้เป็นค่าเริ่มต้น

### ขั้นที่ 3: ปิด sessionAffinity

```bash
kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"None"}}'
kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinity} [{.spec.sessionAffinityConfig}]'; echo
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
```

```text
service/web patched
None []
      9 web v1 from web-gsgss
     11 web v1 from web-k2nk5
     10 web v1 from web-mgz49
```

กลับเป็น `None` แล้ว `sessionAffinityConfig` หายไปเอง (ในวงเล็บว่าง) และการกระจายกลับมา **ต้องปิดให้เรียบร้อย** เพราะ LAB ถัดไปใช้การกระจายแบบปกติ

### สิ่งที่เห็น

- kube-proxy สุ่ม Pod ต่อ connection ยิงน้อยครั้งอาจไม่เห็นครบทุก Pod ต้องยิงหลายสิบครั้ง
- `sessionAffinity: ClientIP` ผูกลูกค้าแต่ละ IP กับบูธเดียว (timeout เริ่มต้น 10800 วินาที)

**คำถามชวนคิด**

1. ถ้าทั้งคลาสใช้ Wi-Fi ที่ออกอินเทอร์เน็ตด้วย IP เดียวกัน แล้วร้านเปิด `sessionAffinity: ClientIP` จะเกิดอะไรกับการกระจายลูกค้า
2. ทำไมการยิงแค่ 3 ครั้งแล้วเห็น 3 Pod ไม่ครบจึงไม่ได้แปลว่า Service เสีย

---

## LAB 6: readinessProbe กับ endpoints

{{FIG:L08}}

**เป้าหมาย:** ทำให้บูธหนึ่ง "ไฟแดง" แล้วเห็นว่ายังอยู่ในรายชื่อแต่ไม่ได้ลูกค้า จากนั้นคืนไฟเขียว

**ต้องมีจาก LAB 5:** Service `web` (sessionAffinity `None`), ReplicaSet `web` 3 บูธ และ Pod `client`

readinessProbe ของ `web` คือ `httpGet / port http` ทุก 2 วินาที ถ้าลบไฟล์ `index.html` nginx จะตอบ 403 และ probe ล้ม

### ขั้นที่ 1: ลบ index.html ของบูธหนึ่งแล้วจับเวลา

🐧 **ใน SSH session ของ k8s-lab** คำสั่งด้านล่างเลือก Pod `web` ตัวแรกใส่ตัวแปร `POD` ลบไฟล์ แล้ววนดูสถานะทุก 1 วินาทีจนกว่า endpoint ของบูธนั้นจะเป็น `ready=false` (คัดลอกทั้งบรรทัด)

```bash
POD=$(kubectl -n shop get pod -l app=web -o name | head -1); echo $POD; kubectl -n shop exec $POD -- rm /usr/share/nginx/html/index.html; date +%T; for i in $(seq 12); do kubectl -n shop get $POD --no-headers; S=$(kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath="{.items[0].endpoints[?(@.targetRef.name==\"${POD#pod/}\")].conditions.ready}"); echo "$(date +%T) ready=$S"; [ "$S" = false ] && break; sleep 1; done
```

```text
pod/web-gsgss
09:00:35
web-gsgss   1/1   Running   0     2m44s
09:00:35 ready=true
web-gsgss   1/1   Running   0     2m45s
09:00:36 ready=true
...
web-gsgss   1/1   Running   0     2m50s
09:00:41 ready=true
web-gsgss   0/1   Running   0     2m51s
09:00:42 ready=false
```

ราว **7 วินาที** หลังลบไฟล์ Pod เปลี่ยนเป็น `0/1` และ endpoint เป็น `ready=false` (probe ทุก 2 วินาที ต้องล้มติดกัน 3 ครั้งตาม `failureThreshold` ค่าเริ่มต้น) Pod ยัง `Running` ไม่ถูก restart เพราะนี่คือ readiness ไม่ใช่ liveness

### ขั้นที่ 2: รายชื่อยังมี IP แต่ไม่ได้ลูกค้า

```bash
kubectl -n shop get pods
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
```

```text
NAME        READY   STATUS    RESTARTS   AGE
client      1/1     Running   0          4m33s
client2     1/1     Running   0          100s
web-gsgss   0/1     Running   0          3m7s
web-k2nk5   1/1     Running   0          4m4s
web-mgz49   1/1     Running   0          4m33s

NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-5r58w   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5   3m44s

10.244.1.4 web-mgz49 ready=true
10.244.2.6 web-k2nk5 ready=true
10.244.1.5 web-gsgss ready=false

     19 web v1 from web-k2nk5
     11 web v1 from web-mgz49
```

**กับดัก:** คอลัมน์ ENDPOINTS ยังแสดง 3 IP ครบ (รวม `10.244.1.5` ของบูธไฟแดง) ต้องดู `conditions.ready` จึงจะรู้ว่าตัวไหนไม่ได้ลูกค้า และยิง 30 ครั้งไม่ไป `web-gsgss` เลย

### ขั้นที่ 3: ดูสาเหตุจาก Pod และ EndpointSlice

แทน `web-gsgss` ด้วยชื่อในตัวแปร `POD` ของตัวเอง

```bash
kubectl -n shop describe pod web-gsgss | grep -E "Readiness|Warning"
kubectl -n shop describe endpointslice -l kubernetes.io/service-name=web | sed -n "/Endpoints:/,\$p" | head -30
```

```text
    Readiness:  http-get http://:http/ delay=0s timeout=1s period=2s successThreshold=1 failureThreshold=3
  Warning  Unhealthy  3m7s               kubelet            spec.containers{nginx}: Readiness probe failed: Get "http://10.244.1.5:80/": dial tcp 10.244.1.5:80: connect: connection refused
  Warning  Unhealthy  0s (x13 over 22s)  kubelet            spec.containers{nginx}: Readiness probe failed: HTTP probe failed with statuscode: 403
Endpoints:
  - Addresses:  10.244.1.4
    Conditions:
      Ready:    true
    ...
  - Addresses:  10.244.1.5
    Conditions:
      Ready:    false
    Hostname:   <unset>
    TargetRef:  Pod/web-gsgss
    NodeName:   lab-worker2
    Zone:       <unset>
Events:         <none>
```

- Event `statuscode: 403` บอกสาเหตุตรง ๆ (nginx ไม่มีไฟล์หน้าแรกให้ตอบ)
- Event `connection refused` เมื่อ 3 นาทีก่อนเกิดตอน Pod เพิ่งเริ่มและ nginx ยังไม่เปิดพอร์ต เป็นเรื่องปกติ
- `describe endpointslice` แสดง `Conditions: Ready: false` ของบูธนั้นชัดเจน

### ขั้นที่ 4: คืนไฟเขียว

```bash
POD=pod/web-gsgss    # แทนด้วยชื่อของตัวเอง หรือใช้ตัวแปร POD จากขั้นที่ 1 ต่อได้เลย
kubectl -n shop exec $POD -- sh -c "echo \"web v1 from \$(hostname)\" > /usr/share/nginx/html/index.html"; date +%T; kubectl -n shop wait --for=condition=Ready $POD --timeout=30s; date +%T
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
kubectl -n shop exec client -- wget -qO- http://10.244.1.5
```

```text
09:01:16
pod/web-gsgss condition met
09:01:17
10.244.1.4 web-mgz49 ready=true
10.244.2.6 web-k2nk5 ready=true
10.244.1.5 web-gsgss ready=true
web v1 from web-gsgss
```

ใส่ไฟล์คืนแล้วกลับมา Ready ในราว 1 วินาที และ `ready=true` อีกครั้งโดยไม่ต้องทำอะไรกับ Service

### สิ่งที่เห็น

- บูธที่ readiness ล้มยังอยู่ใน EndpointSlice แต่ `ready=false` จึงไม่ได้ลูกค้า (Pod ไม่ถูก restart)
- คอลัมน์ ENDPOINTS ไม่บอกเรื่อง ready ต้องดู jsonpath หรือ `describe endpointslice`
- เมื่อ probe ผ่าน บูธกลับมารับลูกค้าเอง

**คำถามชวนคิด**

1. ถ้าลบ `index.html` ของ **ทุก** บูธ ลูกค้าที่เรียก `http://web` จะเห็นข้อความอะไร (เทียบกับ LAB 7)
2. ถ้าเปลี่ยน probe นี้เป็น livenessProbe แทน ผลของการลบ `index.html` จะต่างไปอย่างไร

---

## LAB 7: debug Service

{{FIG:L09}}

**เป้าหมาย:** ไล่ debug Service ที่ตั้งใจตั้งค่าผิด 3 แบบ: selector ผิด, targetPort ผิด และชื่อ DNS ผิด แล้วแก้ให้ใช้ได้

**ต้องมีจาก LAB 6:** ReplicaSet `web` 3 บูธที่ ready ทั้งหมด และ Pod `client`

ไฟล์ใน `labs/lab07-debug/`

```yaml
# LAB 7 (ตั้งใจผิด #1): selector พิมพ์ผิด app=wbe → ไม่มี Pod ไหนตรง → ไม่มี endpoint
apiVersion: v1
kind: Service
metadata:
  name: web-typo
  namespace: shop
spec:
  selector:
    app: wbe               # ← พิมพ์ผิด (ที่ถูกคือ web)
  ports:
    - port: 80
      targetPort: http
---
# LAB 7 (ตั้งใจผิด #2): selector ถูก แต่ targetPort 8080 — nginx ฟังที่ 80
apiVersion: v1
kind: Service
metadata:
  name: web-badport
  namespace: shop
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080     # ← ผิด: ใน Pod ไม่มีอะไรฟัง 8080
```

(ในโฟลเดอร์แยกเป็น 2 ไฟล์ `web-typo-svc.yaml` และ `web-badport-svc.yaml` ด้านบนรวมมาให้อ่านต่อกัน)

### ขั้นที่ 1: selector พิมพ์ผิด

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab07-debug/
sleep 2; kubectl -n shop exec client -- wget -qO- -T 3 http://web-typo; echo "exit=$?"
```

```text
service/web-badport created
service/web-typo created
wget: can't connect to remote host (10.96.237.174): Connection refused
command terminated with exit code 1
exit=1
```

DNS หาชื่อเจอ (ได้ ClusterIP `10.96.237.174`) แต่ถูกปฏิเสธ ไล่ตามบันไดในทฤษฎีหัวข้อ 13: ดู endpoint → ดู selector → เทียบ label

```bash
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-typo
kubectl -n shop describe svc web-typo | grep -E "Selector|Endpoints"
kubectl -n shop get pods --show-labels
```

```text
NAME             ADDRESSTYPE   PORTS     ENDPOINTS   AGE
web-typo-rsdpj   IPv4          <unset>   <unset>     4s

Selector:                 app=wbe
Endpoints:                

NAME        READY   STATUS    RESTARTS   AGE     LABELS
client      1/1     Running   0          5m13s   role=client
client2     1/1     Running   0          2m20s   role=client
web-gsgss   1/1     Running   0          3m47s   app=web
web-k2nk5   1/1     Running   0          4m44s   app=web
web-mgz49   1/1     Running   0          5m13s   app=web
```

EndpointSlice ว่าง (`<unset>`) เพราะไม่มี Pod ไหนมี label `app=wbe` เมื่อ Service ไม่มี endpoint kube-proxy ตอบปฏิเสธทันที (`Connection refused`) แก้ selector ได้เลย (selector ของ Service แก้ได้ ต่างจาก ReplicaSet)

```bash
kubectl -n shop patch svc web-typo -p '{"spec":{"selector":{"app":"web"}}}'
sleep 2; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-typo
kubectl -n shop exec client -- wget -qO- -T 3 http://web-typo
```

```text
service/web-typo patched
NAME             ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-typo-rsdpj   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5   6s
web v1 from web-k2nk5
```

### ขั้นที่ 2: targetPort ผิด

```bash
time kubectl -n shop exec client -- wget -qO- -T 3 http://web-badport; echo "exit=$?"
kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-badport
kubectl -n shop describe svc web-badport | grep -E "TargetPort|Endpoints"
```

```text
wget: can't connect to remote host (10.96.234.49): Connection refused
command terminated with exit code 1

real	0m0.061s
user	0m0.040s
sys	0m0.018s
exit=1
NAME                ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-badport-cqhnf   IPv4          8080    10.244.1.5,10.244.1.4,10.244.2.6   22s
TargetPort:               8080/TCP
Endpoints:                10.244.1.5:8080,10.244.1.4:8080,10.244.2.6:8080
```

ข้อความเหมือนขั้นที่ 1 (`Connection refused` ภายใน 0.06 วินาที) แต่สาเหตุต่างกัน คราวนี้ **มี endpoint ครบ 3 ตัว** แต่ PORTS เป็น `8080` ซึ่งไม่มีโปรแกรมฟังใน Pod ตัว Pod จึงปฏิเสธ แก้ targetPort เป็นชื่อพอร์ต `http`

```bash
kubectl -n shop patch svc web-badport -p '{"spec":{"ports":[{"port":80,"targetPort":"http"}]}}'
sleep 2; kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-badport
kubectl -n shop exec client -- wget -qO- -T 3 http://web-badport
```

```text
service/web-badport patched
NAME                ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-badport-cqhnf   IPv4          80      10.244.1.5,10.244.1.4,10.244.2.6   25s
web v1 from web-mgz49
```

### ขั้นที่ 3: ชื่อ DNS ผิด

```bash
kubectl -n shop exec client -- wget -qO- -T 3 http://wbe; echo "exit=$?"
```

```text
wget: bad address 'wbe'
command terminated with exit code 1
exit=1
```

`bad address` แปลว่า DNS หาชื่อไม่เจอ ยังไม่ถึงขั้น Service เลย ตรวจการสะกดชื่อและ namespace

### ขั้นที่ 4: เก็บกวาด LAB 7

```bash
kubectl delete -f labs/lab07-debug/
```

```text
service "web-badport" deleted from shop namespace
service "web-typo" deleted from shop namespace
```

### สิ่งที่เห็น

| อาการ | สาเหตุ | หลักฐาน |
|---|---|---|
| `Connection refused` + ENDPOINTS `<unset>` | selector ไม่ตรง label ของ Pod | `describe svc` → `Selector: app=wbe`, `Endpoints:` ว่าง |
| `Connection refused` + มี endpoint ครบ | targetPort ไม่ตรงพอร์ตที่แอปฟัง | PORTS `8080`, `Endpoints: ...:8080` |
| `bad address` | ชื่อ DNS ผิด/ไม่มี | ยังไม่ถึง Service |

**คำถามชวนคิด**

1. ถ้า selector ถูกแต่ทุกบูธ readiness ล้ม (LAB 6 ทำกับทุกตัว) ลูกค้าจะเห็นข้อความเหมือนกรณีไหนในตาราง และจะแยกด้วยคำสั่งอะไร
2. ทำไม `web-badport` จึงได้ `Connection refused` ทันที แต่เรียก `web-alt` พอร์ต 80 ใน LAB 3 กลับ `timed out`

---

## LAB 8: NodePort 30080, LoadBalancer และ keep-alive

{{FIG:L10}}

**เป้าหมาย:** เปิดร้าน `web` จาก browser บนเครื่องนักศึกษาด้วย `http://localhost:30080` ดูว่าทุก Node ตอบ ลองกติกาของ NodePort และ LoadBalancer และเข้าใจว่าทำไม browser มักเห็น Pod เดิม

**ต้องมีจาก LAB 7:** ReplicaSet `web` 3 บูธใน `shop` และ NodePort 30080 ว่าง (LAB 0)

### ขั้นที่ 1: สร้าง NodePort 30080

ไฟล์ `labs/lab08-nodeport/web-nodeport.yaml`

```yaml
# LAB 8: NodePort 30080 → เปิดประตูหมายเลข 30080 บน "ทุก Node"
# kind ของ k8s-lab map พอร์ต 30080 ของเครื่องนักศึกษา → lab-control-plane:30080 (extraPortMappings บท 001)
# → เปิด http://localhost:30080 จาก browser ได้เลย
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
  namespace: shop
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80             # ClusterIP:80 (ภายในคลัสเตอร์)
      targetPort: http     # → Pod:80
      nodePort: 30080      # ทุก Node:30080 (ช่วงที่ใช้ได้ 30000–32767)
```

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl apply -f labs/lab08-nodeport/web-nodeport.yaml
kubectl -n shop get svc web-nodeport
sleep 1; curl -s localhost:30080
```

```text
service/web-nodeport created
NAME           TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-nodeport   NodePort   10.96.39.125   <none>        80:30080/TCP   0s
web v1 from web-k2nk5
```

`PORT(S)` อ่านว่า "พอร์ต 80 ของ ClusterIP และพอร์ต 30080 ของทุก Node" ใน k8s-lab `localhost:30080` ไปถึง `lab-control-plane:30080` ผ่าน extraPortMappings (LAB 0 ขั้นที่ 6)

### ขั้นที่ 2: ประตู 30080 เปิดบนทุก Node

```bash
for n in lab-control-plane lab-worker lab-worker2; do echo -n "$n: "; curl -s http://$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $n):30080; done
```

```text
lab-control-plane: web v1 from web-k2nk5
lab-worker: web v1 from web-k2nk5
lab-worker2: web v1 from web-mgz49
```

`docker inspect` อ่าน IP ของ container ที่เป็น Node แต่ละลำ ทั้ง 3 Node ตอบที่ 30080 รวม `lab-control-plane` ที่ไม่มี Pod `web` เลย (kube-proxy บนเรือลำนั้นส่งต่อข้ามเรือให้)

### ขั้นที่ 3: เปิดจาก browser บนเครื่องนักศึกษา

🌐 **browser บนเครื่องนักศึกษา** เปิด **http://localhost:30080** จะเห็นข้อความบรรทัดเดียว `web v1 from web-xxxxx` ไม่ต้องใช้ `kubectl port-forward` หรือ `ssh -L` เหมือนบทก่อน ๆ

{{FIG:L11}}

ลองกด refresh (F5) หลายครั้ง ส่วนใหญ่จะเห็น **ชื่อ Pod เดิมทุกครั้ง** ผลจริงเมื่อทดลองด้วย Chromium จากนอก container ผ่านเส้นทางเดียวกับ `localhost:30080` ของนักศึกษา

| การทดลองใน browser | ผล |
|---|---|
| เปิดหน้า + reload 9 ครั้ง (รวม 10) | `web v1 from web-k2nk5` ทั้ง 10 ครั้ง |
| `fetch()` 10 ครั้งในหน้าเดิม | Pod เดียวทั้ง 10 ครั้ง |
| เปิด browser context ใหม่ทุกครั้ง (คล้ายหน้าต่าง Incognito ใหม่) 5 ครั้ง | 2 ชื่อ (3 + 2) |

สาเหตุคือ **keep-alive**: browser เปิด connection เดียวแล้วใช้ส่งหลาย request ส่วน kube-proxy เลือก Pod **ตอนเปิด connection** เท่านั้น ถ้าอยากเห็นชื่อเปลี่ยน ให้ปิดหน้าต่างทั้งหมดแล้วรอสักครู่ หรือเปิดหน้าต่าง Incognito ใหม่ (ก็ยังสุ่มอยู่ดี) **การที่ refresh แล้วเห็นชื่อเดิมไม่ได้แปลว่ามี Pod เดียว**

### ขั้นที่ 4: ดูการกระจายด้วย curl วน

🐧 **ใน SSH session ของ k8s-lab** `curl` แยกคำสั่งเปิด connection ใหม่ทุกครั้ง

```bash
for i in $(seq 30); do curl -s localhost:30080; done | sort | uniq -c
```

```text
     12 web v1 from web-gsgss
      9 web v1 from web-k2nk5
      9 web v1 from web-mgz49
```

🖥️ **บนเครื่องนักศึกษา (ทางเลือก)** ยิงจากเครื่องตัวเองผ่าน `localhost:30080` ได้เช่นกัน ผลจริงเมื่อยิง 30 ครั้งจากนอก container ได้ `7 web-gsgss / 8 web-k2nk5 / 15 web-mgz49` (กระจายครบ 3 Pod)

```bash
# macOS / Linux / Git Bash
for i in $(seq 30); do curl -s http://localhost:30080; done | sort | uniq -c
```

```powershell
# Windows PowerShell (ใช้ curl.exe ไม่ใช่ alias curl ของ PowerShell)
1..30 | ForEach-Object { curl.exe -s http://localhost:30080 } | Group-Object | Select-Object Count, Name
```

### ขั้นที่ 5: กติกาของ NodePort

ไฟล์ `labs/lab08-nodeport/web-dup-nodeport.yaml` ขอ nodePort 30080 ซ้ำ (ตั้งใจผิด) ส่วนคำสั่งแรกขอเลขนอกช่วง

```bash
kubectl -n shop create service nodeport bad --tcp=80:80 --node-port=29999; echo "exit=$?"
kubectl apply -f labs/lab08-nodeport/web-dup-nodeport.yaml; echo "exit=$?"
```

```text
error: failed to create NodePort service: Service "bad" is invalid: spec.ports[0].nodePort: Invalid value: 29999: provided port is not in the valid range. The range of valid ports is 30000-32767
exit=1
The Service "web-dup" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated
exit=1
```

- nodePort ต้องอยู่ใน **30000–32767**
- เลข **30080 ถูกจองแล้ว** โดย `web-nodeport` เลขเดียวใช้ได้ Service เดียวทั้งคลัสเตอร์ (แม้อยู่คนละ namespace ก็ไม่ได้)

### ขั้นที่ 6: LoadBalancer ใน kind

ไฟล์ `labs/lab08-nodeport/web-lb.yaml` เป็น Service `type: LoadBalancer` ที่ไม่ระบุ nodePort

```bash
kubectl apply -f labs/lab08-nodeport/web-lb.yaml
sleep 5; kubectl -n shop get svc web-lb
kubectl delete -f labs/lab08-nodeport/web-lb.yaml
```

```text
service/web-lb created
NAME     TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-lb   LoadBalancer   10.96.28.238   <pending>     80:31841/TCP   5s
service "web-lb" deleted from shop namespace
```

kind ไม่มีผู้จัดสรร IP ภายนอก `EXTERNAL-IP` จึงค้าง `<pending>` แต่ยังได้ ClusterIP และ nodePort สุ่ม (`31841` ในการทดลอง) ซึ่ง **ไม่ได้ map ออกมาที่เครื่องนักศึกษา** (map แค่ 30080–30082)

### ขั้นที่ 7: ลบ NodePort ก่อน LAB สุดท้าย (ห้ามข้าม)

```bash
kubectl delete -f labs/lab08-nodeport/web-nodeport.yaml
kubectl get svc -A | grep 30080 || echo "(ว่าง — 30080 ว่างแล้ว)"
curl -sS -m 3 localhost:30080; echo "exit=$?"
```

```text
service "web-nodeport" deleted from shop namespace
(ว่าง — 30080 ว่างแล้ว)
curl: (56) Recv failure: Connection reset by peer
exit=56
```

หลังลบ ใน k8s-lab ได้ `Connection reset by peer` ส่วนการเรียกจากนอก container ในการทดลอง ยังได้หน้าเว็บอีก 1 ครั้งในราว 1 วินาทีแรก (kube-proxy ยังไม่ลบกฎ) แล้วจึงได้ `curl: (7) Failed to connect ... Couldn't connect to server` 🌐 ลอง refresh browser ตอนนี้จะเปิดไม่ได้แล้ว

### สิ่งที่เห็น

- NodePort เปิดประตูเดียวกันบนทุก Node และ `http://localhost:30080` บนเครื่องนักศึกษาใช้ได้ทันที
- browser refresh มักเห็น Pod เดิม (keep-alive) ส่วน `curl` วนเห็นหลาย Pod
- nodePort ต้องอยู่ในช่วงและห้ามซ้ำ LoadBalancer ใน kind ค้าง `<pending>`
- ลบ `web-nodeport` แล้ว 30080 ว่างสำหรับ LAB 10

**คำถามชวนคิด**

1. ถ้าเปลี่ยน `web-nodeport` เป็น `nodePort: 31000` Service ยังใช้ได้ไหม แล้วจะเปิดจาก browser บนเครื่องนักศึกษาได้ไหม เพราะอะไร
2. ถ้าอยากให้ browser แสดงชื่อ Pod ต่างกันทุกครั้งที่ refresh ต้องเปลี่ยนที่ฝั่ง client หรือฝั่ง Service

---

## LAB 9: ข้าม namespace, headless, ExternalName และ NetworkPolicy

{{FIG:L12}}

**เป้าหมาย:** เรียก Service จาก namespace อื่น เทียบ DNS ของ Service ปกติ, headless และ ExternalName และเห็นว่า NetworkPolicy ต้องใช้พอร์ตของ Pod

**ต้องมีจาก LAB 8:** namespace `shop` ที่มี Service `web`, `web-alt`, `web-multi`, ReplicaSet `web` และ Pod `client`

### ขั้นที่ 1: ตรวจว่าไม่มี NetworkPolicy ค้าง แล้วสร้างโซนครัว

ไฟล์ `labs/lab09-cross-ns/kitchen.yaml` มี namespace `kitchen` (label `team: kitchen`) และ Pod `cook` (busybox)

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get networkpolicy -A
kubectl apply -f labs/lab09-cross-ns/kitchen.yaml
kubectl -n kitchen wait --for=condition=Ready pod/cook --timeout=60s
```

```text
No resources found
namespace/kitchen created
pod/cook created
pod/cook condition met
```

ถ้า `get networkpolicy -A` เจอ policy ค้างจากบทที่ 4 ให้ลบ namespace ของบทนั้นก่อน มิฉะนั้นผลจะเพี้ยน

### ขั้นที่ 2: เรียก Service ข้าม namespace

```bash
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web; echo "exit=$?"
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web.shop
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web.shop.svc.cluster.local
kubectl -n kitchen exec cook -- cat /etc/resolv.conf
```

```text
wget: bad address 'web'
command terminated with exit code 1
exit=1
web v1 from web-gsgss
web v1 from web-k2nk5
search kitchen.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

search domain ตัวแรกของ `cook` คือ `kitchen.svc.cluster.local` ชื่อสั้น `web` จึงถูกหาใน `kitchen` (ไม่มี) ข้ามโซนต้องใช้ `web.shop` หรือชื่อเต็ม

### ขั้นที่ 3: headless เทียบกับ Service ปกติ และ ExternalName

{{FIG:L13}}

```bash
kubectl apply -f labs/lab09-cross-ns/web-headless.yaml -f labs/lab09-cross-ns/supplier-externalname.yaml
kubectl -n kitchen exec cook -- nslookup web-headless.shop.svc.cluster.local
kubectl -n kitchen exec cook -- nslookup web.shop.svc.cluster.local
```

```text
service/web-headless created
service/supplier created
Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web-headless.shop.svc.cluster.local
Address: 10.244.1.4
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.2.6
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.1.5

Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web.shop.svc.cluster.local
Address: 10.96.55.132
```

headless (`clusterIP: None`) คืน **IP ของ Pod ทั้ง 3** ส่วน Service ปกติคืน **ClusterIP เดียว** อย่าลืมใช้ชื่อเต็มกับ `nslookup` ของ busybox ผลจริงเมื่อใช้ชื่อย่อแบบมีจุด

```bash
kubectl -n kitchen exec cook -- nslookup web-headless.shop; echo "exit=$?"
```

```text
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find web-headless.shop: NXDOMAIN

** server can't find web-headless.shop: NXDOMAIN

command terminated with exit code 1
exit=1
```

ต่อด้วย ExternalName `supplier` (CNAME ไป `example.com`)

```bash
kubectl -n kitchen exec cook -- nslookup supplier.shop.svc.cluster.local
kubectl -n shop get svc
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://supplier.shop; echo "exit=$?"
```

```text
Server:		10.96.0.10
Address:	10.96.0.10:53

supplier.shop.svc.cluster.local	canonical name = example.com
Name:	example.com
Address: 172.66.147.243
Name:	example.com
Address: 104.20.23.154
...
NAME           TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)           AGE
supplier       ExternalName   <none>          example.com   <none>            17s
web            ClusterIP      10.96.55.132    <none>        80/TCP            7m2s
web-alt        ClusterIP      10.96.141.242   <none>        8080/TCP          5m58s
web-headless   ClusterIP      None            <none>        80/TCP            17s
web-multi      ClusterIP      10.96.28.97     <none>        80/TCP,8080/TCP   5m53s
wget: server returned error: HTTP/1.1 409 Conflict
command terminated with exit code 1
exit=1
```

- `supplier` ได้ `canonical name = example.com` ตามด้วย IP ของ `example.com` (IP ในเครื่องนักศึกษาอาจต่าง และถ้าไม่มีอินเทอร์เน็ตจะเห็นแค่บรรทัด canonical name)
- `get svc`: ExternalName ไม่มี ClusterIP และ PORT(S) ส่วน headless มี CLUSTER-IP เป็น `None`
- `wget http://supplier.shop` ได้ `409 Conflict` เพราะ wget ส่ง Host header เป็น `supplier.shop` ซึ่งปลายทางไม่รู้จัก นี่คือข้อจำกัดของ ExternalName ที่เปลี่ยนแค่ DNS ไม่ได้เปลี่ยน Host header/TLS

### ขั้นที่ 4: NetworkPolicy กับพอร์ตของ Service

{{FIG:L14}}

ก่อนมีรั้ว `cook` เรียก `web-alt.shop:8080` ได้ จากนั้นสร้าง policy ที่ "อนุญาต `kitchen` ที่พอร์ต 8080" (ไฟล์ `np-kitchen-8080.yaml` ตั้งใจผิด)

```yaml
# LAB 9 (ตั้งใจผิด): อนุญาตครัวเข้า web "พอร์ต 8080" (= port ของ Service web-alt)
# NetworkPolicy ตรวจที่ Pod ปลายทาง "หลัง" kube-proxy แปลงที่อยู่แล้ว → เห็นพอร์ต 80 ของ Pod ไม่ใช่ 8080
# ผล: ครัวถูกกั้น (timed out)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-from-kitchen
  namespace: shop
spec:
  podSelector:
    matchLabels:
      app: web             # policy เลือก "Pod" ไม่ใช่ Service
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              team: kitchen
      ports:
        - port: 8080       # ← ผิด: ต้องใช้พอร์ตของ Pod (targetPort)
```

```bash
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web-alt.shop:8080
kubectl apply -f labs/lab09-cross-ns/np-kitchen-8080.yaml
sleep 2; kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web-alt.shop:8080; echo "exit=$?"
kubectl -n shop exec client -- wget -qO- -T 3 http://web; echo "exit=$?"
```

```text
web v1 from web-mgz49
networkpolicy.networking.k8s.io/web-from-kitchen created
wget: download timed out
command terminated with exit code 1
exit=1
wget: download timed out
command terminated with exit code 1
exit=1
```

- `cook` ถูกกั้น (`download timed out`) ทั้งที่ policy "อนุญาตพอร์ต 8080" เพราะ policy ตรวจที่ Pod **หลัง** kube-proxy แปลง `ClusterIP:8080` เป็น `Pod:80` แล้ว Pod เห็นพอร์ต 80 ซึ่งไม่ได้อนุญาต
- ผลข้างเคียง: `client` ใน `shop` เองก็ถูกกั้น เพราะทันทีที่มี policy เลือก Pod `app=web` Pod นั้นรับเฉพาะที่ policy อนุญาต (ต้นทางจาก `kitchen` เท่านั้น)

แก้เป็นพอร์ตของ Pod (ไฟล์ `np-kitchen-80.yaml` เหมือนเดิมทุกอย่างยกเว้น `port: 80`)

```bash
kubectl delete -f labs/lab09-cross-ns/np-kitchen-8080.yaml && kubectl apply -f labs/lab09-cross-ns/np-kitchen-80.yaml
sleep 2; kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web-alt.shop:8080
kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web.shop
kubectl -n shop exec client -- wget -qO- -T 3 http://web; echo "exit=$?"
```

```text
networkpolicy.networking.k8s.io "web-from-kitchen" deleted from shop namespace
networkpolicy.networking.k8s.io/web-from-kitchen created
web v1 from web-mgz49
web v1 from web-mgz49
wget: download timed out
command terminated with exit code 1
exit=1
```

ตอนนี้ `cook` เข้าได้ทั้งทาง `web-alt:8080` และ `web:80` (ทั้งสอง Service ส่งไปพอร์ต 80 ของ Pod) ส่วน `client` ใน `shop` ยังถูกกั้นอยู่เพราะ policy นี้อนุญาตเฉพาะ `kitchen`

### ขั้นที่ 5: เก็บกวาด LAB 1–9

```bash
time kubectl delete ns shop kitchen
kubectl get ns
```

```text
namespace "shop" deleted
namespace "kitchen" deleted

real	0m10.745s
...
NAME                 STATUS   AGE
default              Active   13m
kube-node-lease      Active   13m
kube-public          Active   13m
kube-system          Active   13m
local-path-storage   Active   13m
```

ลบ namespace แล้ว ReplicaSet, Pod, Service, EndpointSlice และ NetworkPolicy ทั้งหมดใน `shop`/`kitchen` หายไปด้วย

### สิ่งที่เห็น

- ข้ามโซนต้องใช้ `<svc>.<ns>` หรือชื่อเต็ม ชื่อสั้นได้ `bad address`
- headless คืน IP ของทุก Pod, Service ปกติคืน ClusterIP เดียว, ExternalName คืน CNAME (แต่ Host header ยังเป็นชื่อเดิม → `409 Conflict`)
- `nslookup` ของ busybox ต้องใช้ชื่อเต็ม (`web-headless.shop` ได้ NXDOMAIN)
- NetworkPolicy ต้องใช้พอร์ตของ Pod (targetPort) และเมื่อเลือก Pod แล้ว ทุกต้นทางที่ไม่ได้อนุญาตถูกกั้นหมด

**คำถามชวนคิด**

1. ถ้าต้องการให้ทั้ง `kitchen` และ Pod ใน `shop` เข้า `web` ได้ ต้องเพิ่มอะไรใน policy (ใบ้: ทฤษฎีบทที่ 4 หัวข้อ 10.3 เรื่อง OR)
2. ถ้าแอปในคลัสเตอร์ต้องเรียก API ภายนอกผ่าน HTTPS ด้วยชื่อ ExternalName ใบรับรอง TLS ของปลายทางจะตรวจผ่านไหม เพราะอะไร

---

