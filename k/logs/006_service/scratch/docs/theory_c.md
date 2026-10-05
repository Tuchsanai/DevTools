## 12. readinessProbe กับ endpoints

### 12.1 บูธไฟแดงยังอยู่ในรายชื่อ แต่ไม่ได้ลูกค้า

{{FIG:T27}}

**readinessProbe** (บทที่ 2) คือไฟเขียวหน้าบูธ ในบทนี้มันมีผลโดยตรงกับ Service

- Pod ที่ **ไม่ ready** (READY `0/1`) ยังอยู่ใน EndpointSlice แต่ endpoint ของมันมี `conditions.ready: false`
- kube-proxy ส่งลูกค้าไปเฉพาะ endpoint ที่ `ready: true`
- เมื่อ probe ผ่านอีกครั้ง `ready` กลับเป็น `true` และบูธได้ลูกค้าอีกโดยไม่ต้องทำอะไร

**กับดักสำคัญ:** คอลัมน์ ENDPOINTS ของ `kubectl get endpointslice` **ยังแสดง IP ของ Pod ที่ไม่ ready** ด้วย ผลจริงจาก LAB 6 หลังลบไฟล์ `index.html` ใน Pod `web-gsgss` (nginx ตอบ 403 → probe ล้ม)

```text
$ kubectl -n shop get pods
NAME        READY   STATUS    RESTARTS   AGE
...
web-gsgss   0/1     Running   0          3m7s
web-k2nk5   1/1     Running   0          4m4s
web-mgz49   1/1     Running   0          4m33s

$ kubectl -n shop get endpointslice -l kubernetes.io/service-name=web
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-5r58w   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5   3m44s

$ kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'
10.244.1.4 web-mgz49 ready=true
10.244.2.6 web-k2nk5 ready=true
10.244.1.5 web-gsgss ready=false

$ kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
     19 web v1 from web-k2nk5
     11 web v1 from web-mgz49
```

ENDPOINTS ยังมี `10.244.1.5` แต่ `ready=false` และยิง 30 ครั้งไม่ไป `web-gsgss` เลยสักครั้ง สาเหตุดูได้จาก Event ของ Pod

```text
Warning  Unhealthy  0s (x13 over 22s)  kubelet  spec.containers{nginx}: Readiness probe failed: HTTP probe failed with statuscode: 403
```

ระยะเวลาก่อนบูธถูกถอดจากการรับลูกค้าขึ้นกับ `periodSeconds × failureThreshold` ในการทดลอง (`periodSeconds: 2`, `failureThreshold` ค่าเริ่มต้น 3) `ready=false` ปรากฏหลังลบไฟล์ประมาณ **7 วินาที** และเมื่อคืนไฟล์ Pod กลับมา Ready ในราว 1 วินาที

### 12.2 endpoint ของ Pod ที่กำลังปิด

{{FIG:T28}}

เมื่อ Pod ถูกลบ (เช่น ลบด้วยมือ หรือ ReplicaSet scale ลง) endpoint ของมันไม่ได้หายทันที แต่เปลี่ยนสถานะตามเอกสารของ Kubernetes เป็น

| condition | ความหมาย | Pod ที่กำลังปิด |
|---|---|---|
| `ready` | พร้อมรับลูกค้าใหม่ | `false` |
| `serving` | ยังตอบได้อยู่ (ไม่สนว่ากำลังปิด) | `true` ถ้ายังผ่าน readinessProbe |
| `terminating` | กำลังถูกปิด | `true` |

kube-proxy หยุดส่ง connection **ใหม่** ไปที่ endpoint ที่ `ready=false` แต่ปัญหาคือขั้นตอนเกิดขึ้น **พร้อมกันหลายที่** kubelet ส่ง SIGTERM ให้ container ขณะที่ EndpointSlice controller อัปเดตรายชื่อ และ kube-proxy บนทุก Node ต้องเขียนกฎใหม่ ในช่วงสั้น ๆ ที่กฎบางเรือยังไม่อัปเดต connection ใหม่อาจยังไปถึง Pod ที่กำลังปิด ลูกค้าจึงเห็น error

ผลจริงจาก LAB 10 เมื่อลบ Pod web 1 ตัว (จาก 5 ตัว) ระหว่างยิง 100 ครั้ง: 5 รอบได้ err **1, 0, 1, 0, 0** ข้อความคือ `curl: (56) Recv failure: Connection reset by peer` และระหว่างนั้น `kubectl get pods -w` เห็น Pod Next.js ที่ถูกลบขึ้นสถานะ `Error` ชั่วครู่ก่อนหาย (process ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM ไม่ใช่ความผิดพลาดของ LAB)

หลักการแก้คือให้ Pod **รอสั้น ๆ ก่อนปิดจริง** (hook `preStop`) เพื่อให้ kube-proxy ทุกเรืออัปเดตทัน แล้วแอปค่อยปิดแบบ graceful ในการตรวจก่อนเขียนบท (ร้าน nginx ถูกเปลี่ยนรุ่นขณะยิง 5 ครั้งต่อวินาที) ไม่มี preStop เกิด error 3 จาก 150 ครั้ง เมื่อใส่ preStop รอ 5 วินาที error ลดเหลือ 1/150, 0/200 และ 0/200 **การลงมือใส่ preStop และการเปลี่ยนรุ่นแบบไม่สะดุดเป็นเนื้อหาของบทที่ 7**

### 12.3 readiness กับ liveness ไม่ควรพึ่งสิ่งเดียวกัน

ร้านน้องส้มรุ่น 1.2 ใน LAB 10 แยก probe เป็น 2 endpoint

| probe | endpoint | ตรวจอะไร | ถ้าล้ม |
|---|---|---|---|
| readinessProbe | `/api/health` | ต่อ db ได้ไหม (`SELECT 1`) | Service ไม่ส่งลูกค้ามา (Pod ไม่ถูก restart) |
| livenessProbe | `/api/live` | process ยังตอบได้ (ไม่แตะ db) | kubelet restart container |

ถ้าให้ liveness พึ่ง db ด้วย เมื่อ db ล่มชั่วคราว web ทุก Pod จะถูก restart พร้อมกันโดยไม่จำเป็น และ `/api/health` ก็ตั้งใจ **ไม่ตรวจว่ามีตารางสินค้า** เพราะตอน db ใหม่ยังว่าง ถ้าทุก Pod not ready พร้อมกัน Service จะไม่มี endpoint ที่ ready เลย ลูกค้าจะเข้าร้านไม่ได้แม้แต่หน้าแจ้งเตือน (LAB 10 จึงเห็นหน้า 503 "ร้านกำลังเตรียมสินค้า" แทน)

---

## 13. debug Service ทีละขั้น

### 13.1 บันได 7 ขั้น

{{FIG:T29}}

เมื่อเรียก Service แล้วไม่ได้ ให้ไล่ทีละขั้นจากบนลงล่าง อย่าข้ามไปแก้แอปทันที

| ขั้น | ตรวจอะไร | คำสั่ง | ถ้าผิดจะเห็น |
|:---:|---|---|---|
| 1 | Service มีอยู่ ชนิด/พอร์ตถูกไหม | `kubectl -n <ns> get svc <svc>` / `describe svc <svc>` | `NotFound`, PORT(S) ไม่ตรงที่เรียก |
| 2 | มี endpoint ไหม | `kubectl -n <ns> get endpointslice -l kubernetes.io/service-name=<svc>` | `PORTS <unset>  ENDPOINTS <unset>` |
| 3 | selector ตรงกับ label ของ Pod ไหม | `describe svc` (บรรทัด `Selector:`) เทียบ `get pods --show-labels` | label ไม่ตรง ตัวสะกดผิด |
| 4 | targetPort ตรงพอร์ตที่แอปฟังไหม | `describe svc` (บรรทัด `TargetPort:`/`Endpoints:`) เทียบ `containerPort` | มี endpoint แต่ `Connection refused` |
| 5 | Pod ready ไหม | `get pods` (READY) และ jsonpath `conditions.ready` | `0/1`, `ready=false` |
| 6 | ชื่อ DNS ถูกไหม | `nslookup <svc>.<ns>.svc.cluster.local` | `bad address`, NXDOMAIN |
| 7 | ข้าม namespace / NetworkPolicy | ใช้ `<svc>.<ns>`, `kubectl get netpol -A` | `bad address` (ลืม namespace), `download timed out` (ถูกรั้วกั้น) |

### 13.2 selector พิมพ์ผิด

{{FIG:T30}}

ไฟล์ `labs/lab07-debug/web-typo-svc.yaml` ตั้ง `selector: {app: wbe}` (สลับตัวอักษร) ผลจริงจาก LAB 7

```text
$ kubectl -n shop exec client -- wget -qO- -T 3 http://web-typo
wget: can't connect to remote host (10.96.237.174): Connection refused
command terminated with exit code 1

$ kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-typo
NAME             ADDRESSTYPE   PORTS     ENDPOINTS   AGE
web-typo-rsdpj   IPv4          <unset>   <unset>     4s

$ kubectl -n shop describe svc web-typo | grep -E "Selector|Endpoints"
Selector:                 app=wbe
Endpoints:                
```

DNS หาเจอ (ได้ ClusterIP `10.96.237.174`) แต่ไม่มีบูธไหนตรง selector เมื่อ Service **ไม่มี endpoint** kube-proxy ใส่กฎ "ปฏิเสธ" ไว้ ลูกค้าจึงได้ `Connection refused` ทันที แก้ด้วย `kubectl -n shop patch svc web-typo -p '{"spec":{"selector":{"app":"web"}}}'` แล้ว EndpointSlice มี 3 IP ภายในไม่กี่วินาที (selector ของ Service แก้ได้ ต่างจาก ReplicaSet)

### 13.3 targetPort ผิด

{{FIG:T31}}

ไฟล์ `labs/lab07-debug/web-badport-svc.yaml` ตั้ง `targetPort: 8080` ทั้งที่ nginx ฟังพอร์ต 80 ผลจริงจาก LAB 7

```text
$ time kubectl -n shop exec client -- wget -qO- -T 3 http://web-badport
wget: can't connect to remote host (10.96.234.49): Connection refused
command terminated with exit code 1

real	0m0.061s

$ kubectl -n shop get endpointslice -l kubernetes.io/service-name=web-badport
NAME                ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-badport-cqhnf   IPv4          8080    10.244.1.5,10.244.1.4,10.244.2.6   22s

$ kubectl -n shop describe svc web-badport | grep -E "TargetPort|Endpoints"
TargetPort:               8080/TCP
Endpoints:                10.244.1.5:8080,10.244.1.4:8080,10.244.2.6:8080
```

ครั้งนี้ **มี endpoint ครบ 3 ตัว** (selector ถูก) แต่ kube-proxy ส่งไปพอร์ต 8080 ของ Pod ซึ่งไม่มีโปรแกรมฟังอยู่ Pod จึงปฏิเสธทันที (0.06 วินาที) แก้ด้วยการเปลี่ยน `targetPort` เป็น `http` (ชื่อพอร์ต) แล้ว PORTS กลับเป็น `80`

### 13.4 แผนที่ข้อความ error

| ข้อความ (busybox wget / curl) | ความหมายที่พบใน LAB | ขั้นที่ต้องดู |
|---|---|---|
| `wget: bad address 'wbe'` | DNS หาชื่อไม่เจอ (พิมพ์ผิด หรือเรียกชื่อสั้นข้าม namespace) | 6, 7 |
| `can't connect to remote host (<ClusterIP>): Connection refused` | Service ไม่มี endpoint ที่ ready, targetPort ผิด หรือกฎเพิ่งถูกสร้าง (~1 วินาทีแรก) | 2–5 |
| `wget: download timed out` | พอร์ตที่ Service ไม่ได้ประกาศ, NetworkPolicy กั้น หรือเรียก Pod IP ที่ไม่มีแล้ว | 1, 7 |
| `curl: (56) Recv failure: Connection reset by peer` | connection ถูกตัดกลางทาง เช่น Pod ปลายทางกำลังถูกลบ หรือ NodePort เพิ่งถูกลบ | 12.2 |
| `curl: (28) Operation timed out` | ไม่ได้คำตอบภายในเวลาที่กำหนด (LAB 10 เจอตอนลบ Pod ทั้งหมดพร้อมกัน) | 12.2, 15 |
| `curl: (7) Failed to connect ... Couldn't connect to server` | ไม่มีโปรแกรมรับที่พอร์ตนั้นเลย (เช่น ลบ Service NodePort แล้ว) | 1 |

---

## 14. NetworkPolicy กับ Service

{{FIG:T32}}

บทที่ 4 เราใช้ NetworkPolicy สร้างรั้วรอบ Pod บทนี้มีกับดักเพิ่มเมื่อเรียกผ่าน Service

1. NetworkPolicy เลือก **Pod** (`podSelector`) ไม่ได้เลือก Service ไม่มีฟิลด์ไหนอ้างชื่อ Service
2. NetworkPolicy ถูกตรวจที่ Pod ปลายทาง **หลัง** kube-proxy แปลงปลายทาง (DNAT) แล้ว แพ็กเก็ตที่มาถึงจึงเป็น `<Pod IP>:<targetPort>` ไม่ใช่ `<ClusterIP>:<port>`
3. ดังนั้น `ports` ใน policy ต้องเป็น **พอร์ตของ Pod (targetPort/containerPort)** ไม่ใช่ `port` ของ Service

ตัวอย่างจาก LAB 9: Service `web-alt` รับที่ 8080 ส่งต่อไป 80 ไฟล์ `labs/lab09-cross-ns/np-kitchen-8080.yaml` (ตั้งใจผิด)

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

ผลจริง: `cook` ใน `kitchen` เรียก `http://web-alt.shop:8080` ได้ `wget: download timed out` เมื่อลบแล้วใช้ `np-kitchen-80.yaml` (เปลี่ยนเป็น `port: 80`) `web-alt.shop:8080` และ `web.shop` กลับมาใช้ได้

ผลข้างเคียงที่ต้องรู้: ทันทีที่มี NetworkPolicy เลือก Pod `app=web` Pod นั้นถูก "ปิดรั้ว" และรับเฉพาะที่ policy อนุญาต ใน LAB 9 แม้แต่ `client` ใน `shop` เอง (ซึ่งไม่ได้อยู่ใน `kitchen`) ก็เรียก `http://web` ได้ `download timed out` ด้วย ถ้าต้องการให้ Pod ในโซนเดียวกันเข้าได้ต้องเพิ่มกฎอนุญาตเอง (แบบ `allow-same-namespace` ของบทที่ 4)

> **ข้อควรระวังกับ NodePort:** ลูกค้าที่เข้ามาทาง NodePort (นโยบาย `externalTrafficPolicy: Cluster` ค่าเริ่มต้น) อาจถูกแปลง IP ต้นทางเป็น IP ของ Node ระหว่างทาง policy ที่อนุญาตด้วย `namespaceSelector` หรือ `podSelector` อย่างเดียวจึงอาจกั้นลูกค้า NodePort ไปด้วย ต้องเพิ่ม `ipBlock` ที่ครอบคลุมต้นทางเหล่านั้นเมื่อจำเป็น (ไม่มีใน LAB)

---

## 15. ข้อจำกัดที่ Service ยังไม่ช่วย

{{FIG:T33}}

LAB 10 แยกร้านน้องส้มเป็น **2 ReplicaSet + 2 Service** (`som-db` ClusterIP และ `som-web` NodePort 30080) ใน namespace `som-shop` แก้ปัญหาของบทที่ 5 ได้ครบ: ทุกบูธใช้ db กลางตัวเดียวผ่านชื่อ `som-db` ออเดอร์จึงตรงกันทุกบูธ ลบ Pod db แล้ว IP ของ db เปลี่ยน (`10.244.2.21 → 10.244.2.26`) แต่ ClusterIP ของ `som-db` ยังเป็น `10.96.93.105` เดิม web จึงต่อใหม่ได้เองโดยไม่ต้อง restart และลูกค้าเปิด `http://localhost:30080` ได้ตรง ๆ แต่ยังเหลือปัญหา 3 ข้อที่ Service ไม่ได้ออกแบบมาแก้

**1. เปลี่ยนรุ่นต้องลบ Pod เอง และร้านสะดุด** ผลจริงจาก LAB 10

```text
$ kubectl -n som-shop set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3
replicaset.apps/som-web image updated

$ kubectl -n som-shop get pods -l app=som-web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
NAME            IMAGE
som-web-lm7jj   som-shop-web:1.2
som-web-n5vw6   som-shop-web:1.2
som-web-zr5pd   som-shop-web:1.2
```

template ของ ReplicaSet เป็น 1.3 แล้ว แต่ Pod เดิมยังเป็น 1.2 ทั้งหมด (ทบทวนบทที่ 5: ReplicaSet ดูแลแค่ "จำนวน") น้องส้มต้องลบ Pod เอง

| วิธีลบ | ผลที่ลูกค้าเห็น (ผลจริง) |
|---|---|
| ลบทีละตัว แล้วรอ Ready เอง | ลูกค้าเห็นร้าน 1.2 และ 1.3 ปนกัน เช่น `58 som-web-mtvzf 1.3` คู่กับ `62 som-web-n5vw6 1.2` err 0–1 ครั้ง ต้องพิมพ์ชื่อ Pod เองทุกตัว รอเองทุกครั้ง |
| ลบทั้งหมดในคำสั่งเดียว `kubectl delete pod -l app=som-web` | Pod ใหม่ทุกตัวยังอยู่ใน `Init` ร้านสะดุด: ยิง 200 ครั้งได้ err **4–7 ครั้ง** ในช่วง 2.3–4.3 วินาที (`Connection reset by peer` และ `Operation timed out`) และในรอบที่ถ่ายภาพหน้าจอ **ยิง 150 ครั้ง error 7 ครั้ง** |

ตัวเลขนี้มาจากเครื่องทดสอบที่เร็วมาก (Pod ใหม่ Ready ในราว 3–4 วินาที) เครื่องที่ช้ากว่าจะเห็น error มากกว่า และถ้าร้านมี 30 บูธ การลบทีละตัวด้วยมือแทบเป็นไปไม่ได้ อีกทั้งไม่มีประวัติรุ่นให้ย้อนกลับ

**2. ข้อมูลของ db หายเมื่อ Pod db เกิดใหม่** เพราะ db เก็บข้อมูลใน `emptyDir` ที่อยู่กับ Pod หลังลบ Pod db หน้าเว็บตอบ 503 "ร้านกำลังเตรียมสินค้า" และ `psql` ได้ `ERROR:  relation "orders" does not exist` เติมสินค้าใหม่ได้แต่ออเดอร์เก่าหายถาวร (แก้ด้วย PersistentVolumeClaim ในบทหลัง)

**3. ลูกค้าภายนอกยังต้องจำเลขประตู** `localhost:30080` ไม่มีชื่อโดเมน ไม่มี HTTPS (แก้ด้วย Ingress/Gateway ในบทหลัง)

---

## 16. สรุปและบทถัดไป

### 16.1 เลือกชนิดของ Service

{{FIG:T34}}

**ตารางที่ 2** เลือกชนิดของ Service

| ต้องการ | ชนิด | ตัวอย่างในบทนี้ | ข้อควรระวัง |
|---|---|---|---|
| ให้ Pod ในคลัสเตอร์เรียกกันด้วยชื่อคงที่ | **ClusterIP** (ค่าเริ่มต้น) | `web`, `som-db` | ใช้จากนอกคลัสเตอร์ไม่ได้ |
| เปิดออกนอกคลัสเตอร์แบบง่าย (LAB, on-premise ขนาดเล็ก) | **NodePort** | `web-nodeport`, `som-web` (30080) | ช่วง 30000–32767, ห้ามซ้ำทั้งคลัสเตอร์, kind ของเรา map ออกมาแค่ 30080–30082 |
| IP ภายนอกจากผู้ให้บริการคลาวด์ | **LoadBalancer** | `web-lb` | ใน kind ค้าง `<pending>` |
| ชื่อในคลัสเตอร์ที่ชี้ไปชื่อ DNS ภายนอก | **ExternalName** | `supplier` → `example.com` | ไม่มี proxy, Host header/TLS ยังเป็นชื่อเดิม |
| ต้องการ IP ของทุก Pod ให้ client เลือกเอง | **headless** (`clusterIP: None`) | `web-headless` | ไม่มีการกระจายโดย kube-proxy |
| ชื่อในคลัสเตอร์ที่ชี้ IP นอกคลัสเตอร์ | Service **ไม่มี selector** + EndpointSlice เขียนเอง | `old-db` (หัวข้อ 3.4) | ต้องดูแลรายชื่อเอง |

### 16.2 สรุปบท

{{FIG:T35}}

1. **Service** = ชื่อ DNS + ClusterIP คงที่ + selector เป็นข้อมูลใน API ไม่ใช่โปรแกรมบนเครื่องใด ไม่เป็นเจ้าของ Pod และไม่สนว่าใครสร้าง Pod
2. **ClusterIP** เป็น IP เสมือนจากช่วง Service CIDR (`10.96.0.0/16`) ping ไม่ตอบ แต่ TCP ไปพอร์ตของ Service ได้ และไม่เปลี่ยนตลอดอายุ Service
3. **EndpointSlice** (`discovery.k8s.io/v1`) เก็บรายชื่อ IP:port ของ Pod ที่ตรง selector เขียนโดย EndpointSlice controller ค้นด้วย label `kubernetes.io/service-name` ส่วน v1 Endpoints เลิกใช้แล้วตั้งแต่ v1.33
4. **พอร์ต 3 ชั้น**: `port` (Service) → `targetPort` (container, ใช้ชื่อได้) และ `nodePort` (ทุก Node) Service หลายพอร์ตต้องตั้งชื่อทุกพอร์ต
5. **NodePort** เปิดพอร์ตเดียวกันบนทุก Node ช่วง 30000–32767 ห้ามซ้ำ kind ของเรา map 30080–30082 ออกมาที่ `localhost` ของเครื่องนักศึกษาตั้งแต่บทที่ 1 **LoadBalancer** ใน kind ค้าง `<pending>` **ExternalName** เป็น CNAME **headless** คืน IP ของทุก Pod
6. **DNS**: `<svc>.<ns>.svc.cluster.local` ชื่อสั้นใช้ได้ในโซนเดียวกัน ข้ามโซนใช้ `<svc>.<ns>` (search domain + `ndots:5`) env var ของ Service มีเฉพาะ Pod ที่สร้างหลัง Service จึงควรใช้ DNS
7. **kube-proxy** (DaemonSet โหมด iptables ใน kind) watch Service + EndpointSlice แล้วเขียนกฎ DNAT บนทุก Node เลือก Pod แบบสุ่มต่อ connection browser ใช้ keep-alive จึงติด Pod เดิม `sessionAffinity: ClientIP` บังคับให้ไป Pod เดิม
8. **readinessProbe** ควบคุมว่า endpoint ได้ลูกค้าไหม (`ready=false` ยังเห็น IP ในคอลัมน์ ENDPOINTS) และ Pod ที่กำลังปิดอาจทำให้ลูกค้าเห็น error ชั่วครู่
9. **debug** ไล่ตาม: Service → EndpointSlice → selector → targetPort → ready → DNS → namespace/NetworkPolicy และแยก `refused` / `timed out` / `bad address` ให้ออก NetworkPolicy ใช้พอร์ตของ Pod
10. Service ยัง **ไม่** เปลี่ยนรุ่นให้ ไม่เก็บข้อมูล db และไม่ให้ชื่อโดเมน

**ตารางที่ 3** สรุปคำสั่งที่ใช้ในบทนี้

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl -n <ns> expose rs <rs> --port=80 --name=<svc>` | สร้าง Service จาก selector ของ ReplicaSet (targetPort เป็นเลข) |
| `kubectl apply -f <svc>.yaml` | สร้าง Service จาก YAML (แนะนำ) |
| `kubectl -n <ns> create service nodeport <svc> --tcp=80:80 --node-port=<n>` | สร้าง NodePort แบบคำสั่ง |
| `kubectl -n <ns> get svc,endpointslice` / `kubectl get svc -A` | ดู Service และรายชื่อ endpoint |
| `kubectl -n <ns> describe svc <svc>` | ดู Selector, TargetPort, Endpoints, Session Affinity |
| `kubectl -n <ns> get endpointslice -l kubernetes.io/service-name=<svc> [-o yaml]` | ดู EndpointSlice ของ Service |
| `kubectl ... get endpointslice ... -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'` | ดู IP ครบทุกตัวพร้อม ready |
| `kubectl -n <ns> describe endpointslice -l kubernetes.io/service-name=<svc>` | ดู Conditions ของแต่ละ endpoint |
| `kubectl -n <ns> patch svc <svc> -p '{"spec":{...}}'` | แก้ selector / targetPort / sessionAffinity |
| `kubectl -n <ns> exec <pod> -- wget -qO- -T 3 http://<svc>.<ns>` | ทดสอบเรียก Service จาก Pod |
| `kubectl -n <ns> exec <pod> -- nslookup <svc>.<ns>.svc.cluster.local` | ทดสอบ DNS (ใช้ชื่อเต็มกับ busybox) |
| `kubectl -n <ns> exec <pod> -- cat /etc/resolv.conf` | ดู search domain และ nameserver |
| `kubectl -n kube-system get ds kube-proxy` / `get cm kube-proxy -o yaml \| grep mode` | ดู kube-proxy และโหมด |
| `for i in $(seq 30); do curl -s localhost:30080; done \| sort \| uniq -c` | ดูการกระจายแบบ connection ใหม่ทุกครั้ง |

### 16.3 ปูทางบทที่ 7

{{FIG:T36}}

ตอนจบ LAB 10 น้องส้มเปลี่ยนร้านเป็นรุ่น 1.3 ได้สำเร็จ แต่ต้องพิมพ์ชื่อ Pod ลบเองทีละตัว หรือลบทั้งหมดแล้วยอมให้ลูกค้าเจอ error (7 ใน 150 ครั้ง) และถ้ารุ่นใหม่มีปัญหาก็ไม่มีปุ่มย้อนรุ่น สิ่งที่ร้านต้องการคือ **"ผู้จัดการร้าน"** ที่สั่งหัวหน้ากะรุ่นใหม่ให้เปิดบูธใหม่ทีละบูธ รอไฟเขียวของบูธใหม่ก่อนปิดบูธเก่า จำประวัติรุ่น และย้อนกลับได้ในคำสั่งเดียว นั่นคือ **Deployment** ในบทที่ 7 ซึ่งจะใช้ Service `som-web`/`som-db` ของบทนี้ต่อได้ทันที เพราะ Service เลือก Pod ด้วย label ไม่สนว่าใครสร้าง Pod

---

## 17. คำถามทบทวน

**1. ทำไมแอปจึงไม่ควรเก็บ IP ของ Pod ไว้ใน config แล้วเรียกตรง ๆ ยกตัวอย่างผลจริงจาก LAB 1**

<details>
<summary>แนวคำตอบ</summary>

Pod เป็นหน่วยที่ตายแล้วไม่ฟื้น เมื่อถูกลบหรือ ReplicaSet สร้างแทน Pod ใหม่จะได้ชื่อและ IP ใหม่ ใน LAB 1 เรียก `http://10.244.1.3` ได้ `web v1 from web-9gngn` แต่หลังลบ Pod นั้น การเรียก IP เดิมได้ `wget: download timed out` ส่วน Pod ใหม่ `web-k2nk5` ได้ IP `10.244.2.6` ควรเรียกผ่านชื่อ Service ซึ่งมี ClusterIP คงที่และรายชื่อ endpoint อัปเดตเอง
</details>

**2. `ping 10.96.55.132` (ClusterIP ของ `web`) ได้ 100% packet loss แต่ `wget http://web` ใช้ได้ Service เสียหรือไม่ อธิบาย**

<details>
<summary>แนวคำตอบ</summary>

ไม่เสีย ClusterIP เป็น IP เสมือนที่ไม่มี interface ใดถือจริง kube-proxy (โหมด iptables) เขียนกฎเฉพาะ protocol/พอร์ตที่ Service ประกาศ (TCP 80) ICMP ของ ping จึงไม่มีใครตอบ การทดสอบ Service ต้องเชื่อมต่อไปที่พอร์ตของ Service ด้วย `wget`/`curl`
</details>

**3. Service กับ ReplicaSet ใช้ selector `app: web` เหมือนกัน ถ้าลบ Service `web` จะเกิดอะไรกับ Pod และถ้าลบ ReplicaSet `web` จะเกิดอะไรกับ Service**

<details>
<summary>แนวคำตอบ</summary>

ลบ Service: Pod ไม่กระทบเพราะ Service ไม่ได้เป็นเจ้าของ Pod (ไม่มี ownerReferences ชี้ Service) แต่ EndpointSlice ของ Service จะหายตาม (ownerReferences ชี้ Service) ลบ ReplicaSet: Pod ถูกลบตามแบบ cascade Service ยังอยู่พร้อม ClusterIP เดิม แต่ EndpointSlice จะว่าง เรียกแล้วได้ `Connection refused` จนกว่าจะมี Pod ที่ label ตรงและ ready กลับมา
</details>

**4. คอลัมน์ ENDPOINTS ของ `kubectl get endpointslice` แสดง 3 IP ครบ แต่ยิง 30 ครั้งได้แค่ 2 Pod เป็นไปได้อย่างไร และจะยืนยันด้วยคำสั่งอะไร**

<details>
<summary>แนวคำตอบ</summary>

Pod ตัวหนึ่งไม่ ready (readinessProbe ล้ม) endpoint ของมันยังอยู่ใน slice แต่ `conditions.ready=false` kube-proxy จึงไม่ส่งลูกค้าไป ยืนยันด้วย jsonpath `{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}` หรือ `kubectl describe endpointslice` (ดู `Conditions: Ready: false`) และดู Event `Readiness probe failed` ของ Pod เช่นใน LAB 6 ที่ได้ `ready=false` และ `statuscode: 403`
</details>

**5. Service `web-alt` มี `port: 8080, targetPort: http` และ containerPort ชื่อ `http` คือ 80 ลูกค้าในโซนเดียวกันต้องเรียกอย่างไร ถ้าเรียก `http://web-alt` จะเห็นอะไร เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

เรียก `http://web-alt:8080` (พอร์ตของ Service) kube-proxy แปลงเป็น `<Pod IP>:80` ให้เอง ถ้าเรียก `http://web-alt` (พอร์ต 80) จะได้ `wget: download timed out` เพราะ Service ไม่ได้ประกาศพอร์ต 80 จึงไม่มีกฎสำหรับพอร์ตนั้น และไม่มีเครื่องใดเป็นเจ้าของ ClusterIP ที่จะตอบปฏิเสธกลับมา
</details>

**6. ทำไม Service ที่มี 2 พอร์ตต้องตั้งชื่อทุกพอร์ต และชื่อพอร์ตของ Service กับชื่อพอร์ตของ container ต่างกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ชื่อใช้แยกพอร์ตใน EndpointSlice, ระเบียน SRV และ env var (`WEB_MULTI_SERVICE_PORT_HTTP`) จึงบังคับเมื่อมีหลายพอร์ต (ไม่ตั้ง → `spec.ports[1].name: Required value`) ชื่อพอร์ตของ Service (`spec.ports[].name`) เป็นของ Service เอง ส่วนชื่อพอร์ตของ container (`containerPort` + `name`) คือสิ่งที่ `targetPort: http` อ้างถึง เช่น Service `web` ใช้ `targetPort: http` ได้แม้พอร์ตของ Service เองไม่มีชื่อ (จึงไม่มี env `WEB_SERVICE_PORT_HTTP`)
</details>

**7. อธิบายเส้นทางของแพ็กเก็ตเมื่อเปิด `http://localhost:30080` บนเครื่องนักศึกษา จนถึง Pod ที่อยู่บน `lab-worker2`**

<details>
<summary>แนวคำตอบ</summary>

(1) Docker บนเครื่องนักศึกษา publish 30080 → container `k8s-lab` (`-p 30080-30082:30080-30082` บทที่ 1) (2) Docker ใน k8s-lab publish 30080 → container `lab-control-plane` ตาม `extraPortMappings` ของ kind (3) NodePort 30080 บน control plane: kube-proxy บน control plane เลือก Pod ที่ ready แบบสุ่มแล้ว DNAT ไปที่ `<Pod IP>:<targetPort>` (4) แพ็กเก็ตเดินทางข้ามเรือไป `lab-worker2` ตามเครือข่าย Pod ปกติ control plane ไม่ต้องมี Pod ของเราเลย
</details>

**8. ทำไม LAB 8 ต้องลบ `web-nodeport` ก่อนเริ่ม LAB 10 และทำไม LAB 0 ต้องตรวจตัวอย่างของบทที่ 1**

<details>
<summary>แนวคำตอบ</summary>

เลข nodePort ใช้ได้ Service เดียวทั้งคลัสเตอร์ (ข้าม namespace ก็ไม่ได้) LAB 10 ต้องใช้ 30080 กับ `som-web` ถ้า `web-nodeport` ยังอยู่จะได้ `provided port is already allocated` ตัวอย่าง `/workspace/examples/web-deployment.yaml` ที่ `k8s-up` แนะนำในบทที่ 1 ก็สร้าง Service `web` ที่ใช้ `80:30080/TCP` ใน `default` จึงต้องลบด้วย `kubectl delete -f /workspace/examples/web-deployment.yaml` ก่อน
</details>

**9. Pod `cook` ใน namespace `kitchen` เรียก `http://web` ได้ `bad address` แต่ `http://web.shop` ได้ อธิบายด้วย resolv.conf และทำไม `nslookup web.shop` ของ busybox จึงได้ NXDOMAIN**

<details>
<summary>แนวคำตอบ</summary>

resolv.conf ของ `cook` มี `search kitchen.svc.cluster.local svc.cluster.local cluster.local` และ `ndots:5` ชื่อ `web` จึงถูกลองเป็น `web.kitchen.svc.cluster.local` ฯลฯ ซึ่งไม่มี ส่วน `web.shop` มีจุดน้อยกว่า 5 จึงถูกเติม `.svc.cluster.local` กลายเป็น `web.shop.svc.cluster.local` ที่มีอยู่จริง `nslookup` ของ busybox ไม่เติม search domain ให้ชื่อที่มีจุด จึงถามชื่อ `web.shop` ตรง ๆ และได้ NXDOMAIN ทั้งที่ `wget` ซึ่งใช้ resolver ปกติใช้ได้ ควรใช้ชื่อเต็มกับ nslookup
</details>

**10. ทำไม `client` ไม่มี `WEB_SERVICE_HOST` แต่ `client2` มี และสรุปว่าแอปควรหา Service ด้วยวิธีใด**

<details>
<summary>แนวคำตอบ</summary>

kubelet ใส่ env ของ Service ให้เฉพาะตอนสร้าง container และเฉพาะ Service ใน namespace เดียวกันที่มีอยู่ ณ ตอนนั้น `client` สร้างใน LAB 1 ก่อน Service `web` จึงไม่มี ส่วน `client2` สร้างหลัง จึงได้ `WEB_SERVICE_HOST=10.96.55.132` ฯลฯ แอปควรใช้ DNS (`web` หรือ `web.shop`) ซึ่งไม่ขึ้นกับลำดับการสร้าง
</details>

**11. นักศึกษากด refresh หน้า `localhost:30080` 10 ครั้ง เห็นชื่อ Pod เดิมทุกครั้ง จึงสรุปว่า Service ไม่กระจายโหลด ข้อสรุปนี้ผิดอย่างไร และควรทดสอบอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

browser ใช้ keep-alive ส่งหลาย request ผ่าน connection เดิม kube-proxy เลือก Pod ตอนเปิด connection เท่านั้น จึงติด Pod เดิม (ผลจริง Chromium reload 10/10 Pod เดียว) ควรทดสอบด้วยคำสั่งที่เปิด connection ใหม่ทุกครั้ง เช่น `for i in $(seq 30); do curl -s localhost:30080; done | sort | uniq -c` หรือ `./hit.sh` ของ LAB 10 ซึ่งเห็นหลาย Pod (เช่น 7/8/15)
</details>

**12. ถ้าแอปต้องการให้ลูกค้าคนเดิมไปบูธเดิม จะตั้งค่าอะไร มีข้อเสียอะไร และถ้ายิงจาก Pod 2 ตัวจะเห็นอะไร**

<details>
<summary>แนวคำตอบ</summary>

ตั้ง `sessionAffinity: ClientIP` (ค่า `timeoutSeconds` เริ่มต้น 10800) ลูกค้า IP เดียวกันไป Pod เดิมตลอด ใน LAB 5 `client` ไป `web-k2nk5` 30/30 และ `client2` ไป `web-mgz49` 30/30 (คนละ Pod ได้เพราะคนละ IP) ข้อเสียคือลูกค้าหลัง NAT เดียวกันไปกองที่บูธเดียว โหลดไม่สมดุล และ session ยังหายเมื่อบูธนั้นหายไป
</details>

**13. Service `web-typo` ได้ `Connection refused` และ `web-badport` ก็ได้ `Connection refused` สองกรณีนี้ต่างกันอย่างไร จะแยกด้วยคำสั่งอะไร**

<details>
<summary>แนวคำตอบ</summary>

`web-typo` ไม่มี endpoint เลย (`PORTS <unset> ENDPOINTS <unset>`, `describe svc` บรรทัด `Endpoints:` ว่าง, `Selector: app=wbe` ไม่ตรง label ของ Pod) kube-proxy ปฏิเสธเองเพราะไม่มีปลายทาง ส่วน `web-badport` มี endpoint ครบ 3 ตัว แต่ PORTS เป็น `8080` ซึ่งไม่มีโปรแกรมฟังใน Pod ตัว Pod จึงปฏิเสธ แยกด้วย `kubectl get endpointslice -l kubernetes.io/service-name=<svc>` และ `kubectl describe svc` (Selector, TargetPort, Endpoints)
</details>

**14. NetworkPolicy ที่อนุญาต `kitchen` เข้า Pod `app=web` ที่ `port: 8080` ทำไมจึงยัง timed out เมื่อเรียก `web-alt.shop:8080` และมีผลข้างเคียงอะไรกับ Pod อื่นใน `shop`**

<details>
<summary>แนวคำตอบ</summary>

NetworkPolicy ตรวจที่ Pod ปลายทางหลัง kube-proxy DNAT แล้ว แพ็กเก็ตที่มาถึง Pod คือพอร์ต 80 (targetPort) ไม่ใช่ 8080 ของ Service จึงไม่ตรงกฎและถูกทิ้ง ต้องใช้ `port: 80` (หรือชื่อ `http`) ผลข้างเคียงคือเมื่อมี policy เลือก Pod `app=web` Pod นั้นรับเฉพาะที่อนุญาต `client` ใน `shop` เองจึงได้ `download timed out` ด้วย
</details>

**15. ใน LAB 10 หลังลบ Pod db หน้าเว็บตอบ 503 แต่ Pod web ยัง `1/1 Ready` และ `/api/health` ยังตอบ `{"ok":true,"db":"up"}` เป็นการออกแบบที่ดีหรือไม่ ถ้า readinessProbe ตรวจว่ามีตาราง `products` ด้วยจะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

เป็นการออกแบบโดยตั้งใจ readiness ตรวจแค่ "ต่อ db ได้" (`SELECT 1`) web จึงยังรับลูกค้าและแสดงหน้าเป็นมิตร "ร้านกำลังเตรียมสินค้า" (HTTP 503) ได้ ถ้า readiness ตรวจตารางด้วย ทุก Pod web จะ not ready พร้อมกันทันทีที่ db ใหม่ยังว่าง Service ไม่มี endpoint ที่ ready ลูกค้าจะได้ connection refused ทั้งร้าน และไม่มีใครเห็นข้อความแจ้ง
</details>

**16. ถ้ายังไม่มี Deployment การเปลี่ยนร้าน 3 บูธจาก 1.2 เป็น 1.3 ด้วย ReplicaSet + Service ทำได้กี่วิธี แต่ละวิธีเสียอะไร**

<details>
<summary>แนวคำตอบ</summary>

ต้อง `kubectl set image rs/som-web ...` (เปลี่ยนแค่ template Pod เดิมยัง 1.2) แล้ว (ก) ลบทีละตัวและรอ Ready เอง: ลูกค้าเห็น 1.2/1.3 ปนกัน err 0–1 ครั้ง แต่ต้องพิมพ์ชื่อ Pod และรอเองทุกตัว เสี่ยงลบผิด ทำกับหลายสิบบูธไม่ไหว (ข) ลบทั้งหมดในคำสั่งเดียว: เร็วแต่ร้านสะดุด (ผลจริง err 4–7 จาก 200 และ 7 จาก 150) ทั้งสองวิธีไม่มีประวัติรุ่นและย้อนรุ่นยาก จึงต้องใช้ Deployment ในบทที่ 7
</details>

---

## 18. เอกสารอ้างอิง

1. The Kubernetes Authors. *Service*. https://kubernetes.io/docs/concepts/services-networking/service/
2. The Kubernetes Authors. *EndpointSlices*. https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/
3. The Kubernetes Authors. *Virtual IPs and Service Proxies*. https://kubernetes.io/docs/reference/networking/virtual-ips/
4. The Kubernetes Authors. *Service ClusterIP allocation*. https://kubernetes.io/docs/concepts/services-networking/cluster-ip-allocation/
5. The Kubernetes Authors. *DNS for Services and Pods*. https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
6. The Kubernetes Authors. *Connecting Applications with Services*. https://kubernetes.io/docs/tutorials/services/connect-applications-service/
7. The Kubernetes Authors. *Debug Services*. https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/
8. The Kubernetes Authors. *Use a Service to Access an Application in a Cluster*. https://kubernetes.io/docs/tasks/access-application-cluster/service-access-application-cluster/
9. The Kubernetes Authors. *Create an External Load Balancer*. https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/
10. The Kubernetes Authors. *Service Internal Traffic Policy*. https://kubernetes.io/docs/concepts/services-networking/service-traffic-policy/
11. The Kubernetes Authors. *Network Policies*. https://kubernetes.io/docs/concepts/services-networking/network-policies/
12. The Kubernetes Authors. *Configure Liveness, Readiness and Startup Probes*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
13. The Kubernetes Authors. *Pod Lifecycle* (termination of Pods). https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
14. The Kubernetes Authors. *kubectl expose*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_expose/
15. The Kubernetes Authors. *ReplicaSet*. https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
16. The Kubernetes Authors. *Deployments* (บทถัดไป). https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
17. kind — Kubernetes IN Docker. *Configuration: Extra Port Mappings*. https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 36 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น ClusterIP, Pod IP และจำนวนครั้ง) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (Kubernetes v1.37.0) ค่าเวลา, IP, ชื่อ Pod และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างกัน
