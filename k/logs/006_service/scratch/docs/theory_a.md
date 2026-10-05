# Service: ประภาคารที่ชื่อและที่อยู่ไม่เคยเปลี่ยน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Service — ClusterIP, selector และ EndpointSlice, Service CIDR, port/targetPort/nodePort และ named port, NodePort, LoadBalancer, ExternalName, headless Service, DNS และ env var ของ Service, kube-proxy, การกระจายโหลดและ sessionAffinity, readinessProbe กับ endpoints, การ debug Service และ NetworkPolicy กับ Service
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 5 ReplicaSet](../../005_kubernetes_replicaset/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md) · **บทถัดไป:** [บทที่ 7 Deployment](../../007_kubernetes_deployment/)

---

## บทคัดย่อ

บทที่ 5 จบลงที่ร้านอาหารแมวน้องส้มมี 3 บูธที่ **หัวหน้ากะ (ReplicaSet)** ดูแลให้ครบเสมอ แต่ลูกค้ายังหาร้านไม่เจอ บูธที่เกิดใหม่ได้ชื่อใหม่และ IP ใหม่ทุกครั้ง น้องส้มต้อง `port-forward` ทีละบูธ สายหลุดทุกครั้งที่บูธถูกแทน และแต่ละบูธมีฐานข้อมูลของตัวเองจนออเดอร์ไม่ตรงกัน บทนี้แก้ปัญหา **"ที่อยู่"** ด้วย **Service** ซึ่งเปรียบเหมือน **ประภาคารบนท่าเรือ** ที่มีป้ายชื่อและป้ายที่อยู่คงที่ คอยส่งลูกค้าไปยังบูธที่ไฟเขียว (พร้อมขาย) เท่านั้น

เนื้อหาเริ่มจากเหตุผลที่ต้องมี Service และธรรมชาติของ **ClusterIP** ที่เป็นที่อยู่เสมือน (ping ไม่ตอบแต่ต่อ TCP ได้) ต่อด้วยกลไก **selector → EndpointSlice** ที่ทำให้รายชื่อบูธอัปเดตเอง ช่วง **Service CIDR** พอร์ต 3 ชั้น (`port`, `targetPort`, `nodePort`) และ named port จากนั้นเป็นชนิดของ Service ได้แก่ **NodePort** (รวมเส้นทางจาก `http://localhost:30080` บนเครื่องนักศึกษาถึง Pod), **LoadBalancer**, **ExternalName** และ **headless** แล้วจึงเจาะลึกการหาร้านด้วยชื่อผ่าน **DNS** (search domain, `ndots`) และ env var, การทำงานของ **kube-proxy** การกระจายลูกค้าแบบสุ่มต่อ connection ผลของ **keep-alive** และ `sessionAffinity` ความสัมพันธ์ระหว่าง **readinessProbe กับ endpoints** ขั้นตอน **debug Service** ทีละขั้น และกับดักของ **NetworkPolicy** ที่ตรวจหลัง kube-proxy แปลงปลายทางแล้ว ปิดท้ายด้วยสิ่งที่ Service ยังไม่ช่วย ซึ่งนำไปสู่บทที่ 7 (Deployment)

ผลลัพธ์คำสั่งและข้อความ error ที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (kind v0.33, Kubernetes v1.37.0, kube-proxy โหมด iptables) ใน LAB ประจำบทและการตรวจสอบก่อนเขียนบท (pre-check) เมื่อ 5 ตุลาคม 2569 **เวลา, AGE, ClusterIP, Pod IP, ชื่อ Pod ที่สุ่ม และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนจะต่างจากตัวอย่าง** เป็นเรื่องปกติ

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายปัญหาของการเรียก Pod ด้วย IP โดยตรง และบอกได้ว่า Service แก้ปัญหานั้นด้วยชื่อ DNS + ClusterIP คงที่ + selector อย่างไร
2. อธิบายว่าทำไม ClusterIP จึงเป็นที่อยู่เสมือนที่ `ping` ไม่ตอบ แต่เชื่อมต่อ TCP ไปที่พอร์ตของ Service ได้
3. เขียน manifest ของ Service (`selector`, `ports`, `type`) และเทียบกับการสร้างด้วย `kubectl expose` ได้ รวมถึงบอกความต่างระหว่าง Service กับ ReplicaSet ในแง่ "ความเป็นเจ้าของ" Pod
4. อ่าน EndpointSlice (addresses, `conditions.ready/serving/terminating`, targetRef) และอธิบายบทบาทของ EndpointSlice controller และเหตุที่ v1 Endpoints ถูกประกาศเลิกใช้
5. แยก `port`, `targetPort`, `nodePort` และใช้ named port กับ Service หลายพอร์ตได้ถูกต้อง
6. อธิบายกติกาของ NodePort และเส้นทางของ `http://localhost:30080` จากเครื่องนักศึกษาผ่าน k8s-lab และ kind ถึง Pod
7. เลือกชนิดของ Service ที่เหมาะสม (ClusterIP, NodePort, LoadBalancer, ExternalName, headless, Service ไม่มี selector) พร้อมบอกข้อจำกัดของแต่ละชนิด
8. อธิบายชื่อ DNS ของ Service, search domain และ `ndots:5` และเรียก Service ข้าม namespace ได้ถูกต้อง รวมถึงข้อจำกัดของ env var ของ Service
9. อธิบายการทำงานของ kube-proxy (watch → เขียนกฎ → DNAT บน Node ต้นทาง) และโหมด iptables/nftables/ipvs
10. อธิบายการกระจายโหลดแบบสุ่มต่อ connection, ผลของ keep-alive ใน browser และ `sessionAffinity: ClientIP`
11. อธิบายความสัมพันธ์ระหว่าง readinessProbe กับ endpoint และอ่าน `ready=false` ได้ แม้คอลัมน์ ENDPOINTS ยังแสดง IP ครบ
12. ไล่ debug Service ทีละขั้น แยกอาการ `Connection refused`, `download timed out` และ `bad address` ได้ และเขียน NetworkPolicy โดยใช้พอร์ตของ Pod (targetPort) ได้ถูกต้อง

## สารบัญ

{{TOC}}

### สารบัญรูปภาพ

{{FIGTOC}}

---

## 1. บทนำ: บูธครบ 3 แต่ลูกค้าหาไม่เจอ

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

{{FIG:T01}}

ในบทที่ 5 น้องส้มจ้าง **หัวหน้ากะ (ReplicaSet)** มานับบูธให้ครบ 3 บูธเสมอ บูธไหนหายก็ได้บูธใหม่ภายในไม่กี่วินาที ปัญหา "จำนวน" จึงหมดไป แต่ลูกค้ายังมีปัญหาเดิมอยู่ คือ **ไม่รู้ว่าจะไปซื้อที่ไหน** เพราะบูธใหม่ทุกบูธได้ **ชื่อใหม่** (`som-booth-xxxxx`) และ **IP ใหม่** ไม่มีที่อยู่กลางที่ลูกค้าจำได้

{{FIG:T02}}

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–5)

| Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| container / Pod | ตู้สินค้า / กล่องใสสี teal มีป้าย IP (บทนี้วาดเป็น "บูธร้าน" มีกันสาด) | |
| Node / Control Plane | เรือสินค้า (`lab-worker`, `lab-worker2`) / หอบังคับการ (`lab-control-plane`) | |
| Namespace | โซนทาสีบนแผนผังท่าเรือ | |
| label / ReplicaSet / Pod template | ป้ายห้อยกระเป๋าสี / หัวหน้ากะ (หุ่นยนต์ teal ถือคลิปบอร์ดนับหัว) / พิมพ์เขียว | |
| **Service** | **ประภาคาร/เคาน์เตอร์ต้อนรับ** มีป้ายชื่อและป้ายที่อยู่คงที่ ส่งลูกค้าไปบูธที่พร้อม | ✅ |
| ClusterIP | ป้ายที่อยู่ของประภาคาร เป็นภาพโฮโลแกรม ไม่มีใครอยู่ข้างในจริง (ping ไม่ตอบ) | ✅ |
| EndpointSlice | คลิปบอร์ดรายชื่อบูธที่เปิดอยู่ ติดข้างประภาคาร (ไม่เกิน 100 แถวต่อแผ่น) | ✅ |
| EndpointSlice controller | เสมียนหุ่นยนต์ในหอ ส่องกล้องดูบูธแล้วเขียนคลิปบอร์ด | ✅ |
| readinessProbe | ไฟเขียวหน้าบูธ (ไฟแดง = ไม่ได้ลูกค้า) | ✅ |
| kube-proxy | ป้ายบอกทางบนเรือทุกลำ ทาสีใหม่ตามวิทยุจากหอ | ✅ |
| NodePort | ประตูทางขึ้นเรือหมายเลข 30080 บนทุก Node | ✅ |
| LoadBalancer | เครนของผู้ให้บริการคลาวด์ที่ส่งป้ายที่อยู่สาธารณะมาให้ (ใน kind ไม่มา จึงค้าง `<pending>`) | ✅ |
| ExternalName | เสาป้ายชี้ออกทะเลไปเกาะซัพพลายเออร์ | ✅ |
| headless Service | สมุดโทรศัพท์รายชื่อบูธ ไม่มีเคาน์เตอร์กลาง | ✅ |
| sessionAffinity / keep-alive | บัตรสมาชิกที่พาลูกค้าไปบูธเดิม / เชือกเส้นเดียวผูกลูกค้ากับบูธเดียว | ✅ |
| NetworkPolicy | รั้วและยามหน้าประตูโซน (บทที่ 4) ที่ตรวจหลังป้ายบอกทางเปลี่ยนที่อยู่แล้ว | |

{{FIG:T03}}

ทบทวนปัญหาที่ค้างมาจากบทที่ 4–5 (เห็นจริงใน LAB สุดท้ายของบทที่ 5)

| ปัญหา | หลักฐานจากบทก่อน | สิ่งที่บทนี้ใช้แก้ |
|---|---|---|
| Pod ใหม่ = ชื่อใหม่ + IP ใหม่ จด IP ไว้ใช้ไม่ได้ | บูธใหม่ชื่อ/IP ใหม่ทุกครั้งที่ ReplicaSet สร้างแทน | ชื่อ Service + ClusterIP คงที่ (หัวข้อ 2–4) |
| `port-forward` ผูกกับ Pod เดียว หลุดเมื่อ Pod ถูกลบ | `error: lost connection to pod` และบูธที่ถูก scale ลงเปิดไม่ได้ | Service เลือก Pod ใหม่เองผ่าน EndpointSlice (หัวข้อ 3) และ NodePort เปิดร้านให้ browser ได้ตรง ๆ (หัวข้อ 6) |
| แต่ละบูธมีฐานข้อมูลของตัวเอง ออเดอร์ไม่ตรงกัน | บูธหนึ่งออเดอร์ 2 แต่อีกสองบูธออเดอร์ 0 บูธใหม่เริ่มจาก 0 | แยก db เป็น Pod ของตัวเอง แล้วให้ทุกบูธเรียกด้วยชื่อ Service `som-db` (LAB 10) |

เป้าหมายของบทนี้จึงมี 5 ข้อ: **(1)** ที่อยู่คงที่ **(2)** กระจายลูกค้าไปหลายบูธ **(3)** ส่งลูกค้าเฉพาะบูธที่พร้อม **(4)** เปิดร้านสู่ภายนอกคลัสเตอร์ และ **(5)** แยกหน้าร้าน (web) ออกจากครัวกลาง (db) ครั้งแรก

ในทุก LAB ของบทนี้ ตัวสร้าง Pod ที่อยู่หลัง Service ยังเป็น **ReplicaSet** ที่เรียนมาแล้ว เพราะ Service เลือก Pod ด้วย label เท่านั้น ไม่สนว่าใครเป็นผู้สร้าง Pod

---

## 2. ทำไมต้องมี Service

### 2.1 นิยาม

{{FIG:T04}}

**Service** คือ object ใน Kubernetes API (`apiVersion: v1`, `kind: Service`) ที่ให้ **ชื่อและที่อยู่คงที่** กับกลุ่มของ Pod ที่ทำหน้าที่เดียวกัน ประกอบด้วย 3 ส่วน

1. **ชื่อ** ที่กลายเป็นชื่อ DNS เช่น `web` หรือชื่อเต็ม `web.shop.svc.cluster.local` (หัวข้อ 9)
2. **ClusterIP** เป็น IP เสมือนที่ไม่เปลี่ยนตลอดอายุของ Service (หัวข้อ 2.2 และ 4)
3. **selector** เป็นเงื่อนไข label ที่ใช้เลือก Pod ปลายทาง รายชื่อ Pod ที่ตรงจะถูกเขียนลง EndpointSlice ให้อัตโนมัติ (หัวข้อ 3)

ลูกค้า (Pod อื่นหรือผู้ใช้ภายนอก) จึงจำแค่ชื่อของ Service แล้ว Kubernetes จะส่งต่อไปยัง Pod ที่พร้อมให้เอง บูธจะเกิดใหม่กี่ครั้ง ได้ IP ใหม่กี่ครั้งก็ไม่กระทบลูกค้า

ข้อเข้าใจผิดที่พบบ่อยคือคิดว่า Service เป็น "โปรแกรม load balancer ที่รันอยู่บนเครื่องใดเครื่องหนึ่ง" ความจริงคือ **Service เป็นแค่ข้อมูลใน API** (เหมือนป้ายประกาศในหอบังคับการ) ส่วนงานส่งต่อแพ็กเก็ตทำโดย **kube-proxy บนทุก Node** (หัวข้อ 10) จึงไม่มีจุดคอขวดกลางและไม่มี "เครื่องประภาคาร" ให้ล่ม

### 2.2 ClusterIP เป็นที่อยู่เสมือน

{{FIG:T05}}

ClusterIP **ไม่ได้ผูกกับ network interface ของเครื่องใด** ไม่มี Pod หรือ Node ใดถือ IP นี้จริง สิ่งที่มีคือกฎของ kube-proxy บนทุก Node ที่บอกว่า "แพ็กเก็ต TCP ที่ส่งไป `ClusterIP:port` ให้เปลี่ยนปลายทางเป็น IP ของ Pod ตัวหนึ่ง" กฎนี้จับเฉพาะ **protocol และพอร์ตที่ Service ประกาศไว้** เท่านั้น ผลที่ตามมาคือ

- `ping` (ICMP) ไปที่ ClusterIP **ไม่ตอบ** เพราะไม่มีกฎสำหรับ ICMP และไม่มีใครเป็นเจ้าของ IP
- เชื่อมต่อ TCP ไปที่ **พอร์ตของ Service** ได้ตามปกติ
- เชื่อมต่อไปพอร์ต **อื่น** ของ ClusterIP จะเงียบจนหมดเวลา (timeout) เพราะไม่มีกฎรองรับ (เห็นจริงใน LAB 3)

ผลจริงจาก LAB 2 (Service `web` มี ClusterIP `10.96.55.132`)

```text
$ kubectl -n shop exec client -- wget -qO- http://web
web v1 from web-999d4

$ kubectl -n shop exec client -- ping -c 2 -W 2 10.96.55.132
PING 10.96.55.132 (10.96.55.132): 56 data bytes

--- 10.96.55.132 ping statistics ---
2 packets transmitted, 0 packets received, 100% packet loss
command terminated with exit code 1

$ kubectl -n shop exec client -- ping -c 2 -W 2 10.244.2.5
PING 10.244.2.5 (10.244.2.5): 56 data bytes
64 bytes from 10.244.2.5: seq=0 ttl=63 time=0.063 ms
64 bytes from 10.244.2.5: seq=1 ttl=63 time=0.064 ms
...
2 packets transmitted, 2 packets received, 0% packet loss
```

Pod IP (`10.244.2.5`) ping ได้เพราะเป็น IP ที่มีอยู่จริงบน network interface ของ Pod ส่วน ClusterIP ping ไม่ได้แต่ `wget http://web` ใช้ได้ **อย่าใช้ ping ทดสอบ Service** ให้ใช้ `wget`/`curl` ไปที่พอร์ตของ Service แทน

> พฤติกรรม ping ข้างต้นเป็นของโหมด iptables ที่ kind ใช้ kube-proxy บางโหมดหรือ network plugin บางตัวอาจตอบ ping ของ ClusterIP ได้ จึงไม่ควรใช้ผล ping ตัดสินว่า Service ใช้ได้หรือไม่

### 2.3 โครงสร้าง manifest ของ Service

{{FIG:T06}}

ไฟล์ `02_LAB/labs/lab02-clusterip/web-svc.yaml` ของ LAB 2

```yaml
# LAB 2: Service แรก — ClusterIP (ค่าเริ่มต้น) ชื่อ web
# ชื่อ "web" + IP เสมือน (ClusterIP) คงที่ ส่งต่อไป Pod ที่มีป้าย app=web และ Ready
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: shop
spec:
  type: ClusterIP          # ไม่ใส่ก็ได้ (ค่าเริ่มต้น)
  selector:
    app: web               # เลือก Pod ด้วย label (ไม่สนว่าใครสร้าง Pod)
  ports:
    - port: 80             # พอร์ตที่ Service รับ (http://web:80)
      targetPort: http     # พอร์ตของ container (ชื่อ http = containerPort 80)
```

| ฟิลด์ | ความหมาย | หมายเหตุ |
|---|---|---|
| `metadata.name` | ชื่อ Service = ชื่อ DNS | ต้องเป็น DNS label (ตัวพิมพ์เล็ก ตัวเลข `-`) |
| `spec.type` | ชนิดของ Service | ค่าเริ่มต้น `ClusterIP`; อื่น ๆ คือ `NodePort`, `LoadBalancer`, `ExternalName` |
| `spec.selector` | label ที่ใช้เลือก Pod | **แก้ไขได้** (ต่างจาก selector ของ ReplicaSet ที่แก้ไม่ได้) และรองรับเฉพาะแบบเท่ากับ (ไม่มี `matchExpressions`) |
| `spec.ports[].port` | พอร์ตที่ Service รับ | ลูกค้าเรียก `web:80` |
| `spec.ports[].targetPort` | พอร์ตของ container ปลายทาง | เป็นเลขหรือ **ชื่อพอร์ต** ก็ได้ ไม่ใส่ = เท่ากับ `port` |
| `spec.ports[].protocol` | `TCP` (ค่าเริ่มต้น), `UDP`, `SCTP` | |
| `spec.clusterIP` | ClusterIP ที่ระบบจัดสรรให้ | ใส่เองได้ (ไม่แนะนำ) หรือใส่ `None` เพื่อทำ headless |

ส่วน Pod ปลายทางมาจาก ReplicaSet ใน `labs/lab01-before-service/web-rs.yaml` (ตัดมาเฉพาะส่วนที่เกี่ยวกับ Service)

```yaml
  template:
    metadata:
      labels:
        app: web                   # Service จะเลือก Pod ด้วยป้ายนี้ (LAB 2)
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          ports:
            - name: http             # ตั้งชื่อพอร์ต → Service อ้าง targetPort: http ได้
              containerPort: 80
          readinessProbe:            # ไฟเขียวหน้าบูธ: ไม่ผ่าน = Service ไม่ส่งลูกค้ามา (LAB 6)
            httpGet: { path: /, port: http }
            periodSeconds: 2
```

**Service กับ ReplicaSet ใช้ selector เหมือนกันแต่คนละหน้าที่**

| | ReplicaSet (บทที่ 5) | Service (บทนี้) |
|---|---|---|
| ใช้ selector ทำอะไร | นับ Pod เพื่อสร้าง/ลบให้ครบ `replicas` | หา Pod เพื่อส่งลูกค้าไป |
| เป็นเจ้าของ Pod ไหม | ใช่ Pod มี `ownerReferences` ชี้ ReplicaSet | **ไม่ใช่** Pod ไม่มี ownerReferences ชี้ Service ลบ Service แล้ว Pod ยังอยู่ |
| สร้าง/ลบ Pod ได้ไหม | ได้ | ไม่ได้เลย |
| สนใจว่าใครสร้าง Pod ไหม | Pod ต้องตรง selector (รับเลี้ยง Pod หลงได้) | ไม่สน: Pod เดี่ยว, Pod ของ ReplicaSet หรือของ workload อื่นในบทหลัง ถ้า label ตรงและ Ready ก็ได้ลูกค้า |
| แก้ selector ได้ไหม | ไม่ได้ (`field is immutable`) | ได้ (LAB 7 แก้ selector ที่พิมพ์ผิดด้วย `kubectl patch`) |

### 2.4 สร้าง Service ได้ 2 ทาง

**ทางที่ 1: `kubectl expose`** คัดลอก selector จาก object ต้นทาง เหมาะกับการลองเร็ว ๆ

```bash
kubectl -n shop expose rs web --port=80 --name=web-quick
kubectl -n shop get svc web-quick -o yaml
```

ผลจริงจาก LAB 2 (ตัดบางส่วน)

```text
service/web-quick exposed
...
spec:
  clusterIP: 10.96.84.23
  ...
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: web
  sessionAffinity: None
  type: ClusterIP
```

สังเกตว่า `expose` คัดลอก selector `app: web` จาก ReplicaSet มาให้ แต่ใส่ **`targetPort: 80` เป็นตัวเลข** ไม่ใช่ชื่อพอร์ต `http` และ API เติมค่าเริ่มต้นอื่น ๆ ให้ (`sessionAffinity: None`, `internalTrafficPolicy: Cluster`, `ipFamilies`)

**ทางที่ 2: เขียน YAML แล้ว `kubectl apply -f`** (แนะนำ) เพราะเก็บใน Git ได้ ทบทวนได้ และใช้ named port ได้ตามต้องการ

---

## 3. selector → EndpointSlice

### 3.1 EndpointSlice คือรายชื่อบูธที่ระบบเขียนให้

{{FIG:T07}}

Service ไม่ได้เก็บรายชื่อ Pod ไว้ในตัวเอง รายชื่อ "IP:port ของ Pod ที่ตรง selector" ถูกเก็บใน object อีกชนิดคือ **EndpointSlice** (`discovery.k8s.io/v1`) ผลจริงจาก LAB 2 หลัง apply `web-svc.yaml`

```text
$ kubectl -n shop get svc,endpointslice
NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/web   ClusterIP   10.96.55.132   <none>        80/TCP    0s

NAME                                       ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
endpointslice.discovery.k8s.io/web-5r58w   IPv4          80      10.244.2.5,10.244.1.4,10.244.2.6   0s

$ kubectl -n shop get pods -o wide
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE          ...
client      1/1     Running   0          50s   10.244.2.4   lab-worker    ...
web-999d4   1/1     Running   0          50s   10.244.2.5   lab-worker    ...
web-k2nk5   1/1     Running   0          21s   10.244.2.6   lab-worker    ...
web-mgz49   1/1     Running   0          50s   10.244.1.4   lab-worker2   ...
```

ENDPOINTS 3 ตัวตรงกับ IP ของ Pod `web-*` ทั้ง 3 (ไม่มี `client` เพราะ label เป็น `role=client`) และ PORTS เป็น `80` คือพอร์ตของ **Pod** (targetPort ที่แปลงจากชื่อ `http` แล้ว) ไม่ใช่พอร์ตของ Service

### 3.2 EndpointSlice controller

{{FIG:T08}}

ผู้เขียน EndpointSlice คือ **EndpointSlice controller** ซึ่งรันอยู่ใน `kube-controller-manager` บน control plane (ที่เดียวกับ ReplicaSet controller ของบทที่ 5) มันทำงานแบบ reconciliation loop เหมือนกัน

1. **watch** Service ทุกตัวที่มี selector และ Pod ทุกตัว
2. เมื่อมีการเปลี่ยนแปลง (Pod ใหม่, Pod ถูกลบ, Pod เปลี่ยนสถานะ ready, label เปลี่ยน, Service เปลี่ยน selector) ก็คำนวณรายชื่อใหม่
3. เขียน EndpointSlice ที่ติด label `kubernetes.io/service-name=<ชื่อ Service>` และมี `ownerReferences` ชี้กลับ Service

ผลจริงจาก LAB 2 (`kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o yaml` ตัดบางส่วน)

```text
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.2.5
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: lab-worker
    targetRef:
      kind: Pod
      name: web-999d4
      namespace: shop
      ...
  ...
  kind: EndpointSlice
  metadata:
    ...
    generateName: web-
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web
    name: web-5r58w
    namespace: shop
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: web
      ...
  ports:
  - name: ""
    port: 80
    protocol: TCP
```

ข้อสังเกตสำคัญ

- **ชื่อ slice เป็น `<ชื่อ Service>-<สุ่ม 5 ตัว>`** (`web-5r58w`) จึงต้องค้นด้วย label `-l kubernetes.io/service-name=web` ไม่ใช่ด้วยชื่อ
- **ownerReferences ชี้ Service** ลบ Service แล้ว EndpointSlice หายตาม (cascade แบบเดียวกับบทที่ 5)
- แต่ละ endpoint มี `addresses`, `conditions` (`ready`, `serving`, `terminating`), `nodeName` และ `targetRef` (ชี้ Pod) ทำให้รู้ว่า IP นี้คือ Pod ตัวไหนอยู่บนเรือลำไหน
- **1 slice เก็บได้ไม่เกิน 100 endpoint** (ค่าเริ่มต้น) Service ที่มี Pod มากกว่านั้นจะมีหลาย slice ทำให้อัปเดตทีละส่วนได้โดยไม่ต้องเขียน object ก้อนใหญ่ทั้งก้อนทุกครั้งที่ Pod ตัวเดียวเปลี่ยน
- รายชื่อ **อัปเดตเอง** ทันทีที่ Pod เปลี่ยน ผลจริงจาก LAB 2 เมื่อ scale ReplicaSet เป็น 5 แล้วลบ Pod `web-999d4` (IP `10.244.2.5`) IP นั้นหายจากรายชื่อและมี IP ใหม่ `10.244.1.5` เข้ามาแทน ส่วน ClusterIP ยังเป็น `10.96.55.132` เหมือนเดิม

```text
$ kubectl -n shop scale rs web --replicas=5 ...
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-5r58w   IPv4          80      10.244.2.5,10.244.1.4,10.244.2.6 + 2 more...   39s

$ kubectl -n shop delete pod web-999d4 ...
pod "web-999d4" deleted from shop namespace
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
web-5r58w   IPv4          80      10.244.1.4,10.244.2.6,10.244.1.5 + 2 more...   41s
...
NAME   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
web    ClusterIP   10.96.55.132   <none>        80/TCP    44s
```

> **กับดัก:** คอลัมน์ ENDPOINTS ของ `kubectl get endpointslice` แสดงแค่ 3 IP แรกแล้วตามด้วย `+ 2 more...` แม้ใช้ `-o wide` ถ้าต้องการเห็นครบให้ใช้ jsonpath เช่น
> `kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'`

### 3.3 v1 Endpoints เป็นรุ่นเก่า

{{FIG:T09}}

ก่อนมี EndpointSlice Kubernetes ใช้ object ชื่อ **Endpoints** (`v1`) ที่เก็บรายชื่อทั้งหมดของ Service ไว้ใน object เดียว เมื่อ Service มี Pod นับพันตัว ทุกครั้งที่ Pod ตัวเดียวเปลี่ยน ต้องส่ง object ก้อนใหญ่ทั้งก้อนไปให้ทุก Node จึงถูกแทนด้วย EndpointSlice และ **v1 Endpoints ถูกประกาศเลิกใช้ (deprecated) ตั้งแต่ Kubernetes v1.33** ผลจริงจาก LAB 2

```text
$ kubectl -n shop get endpoints web
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
NAME   ENDPOINTS                                   AGE
web    10.244.1.4:80,10.244.2.5:80,10.244.2.6:80   1s
```

คำสั่ง `kubectl describe svc` ยังมีบรรทัด `Endpoints:` ให้ดูสรุปได้สะดวก

```text
$ kubectl -n shop describe svc web
Name:                     web
Namespace:                shop
...
Selector:                 app=web
Type:                     ClusterIP
...
IP:                       10.96.55.132
IPs:                      10.96.55.132
Port:                     <unset>  80/TCP
TargetPort:               http/TCP
Endpoints:                10.244.2.5:80,10.244.1.4:80,10.244.2.6:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
```

`Port: <unset>  80/TCP` หมายถึงพอร์ตนี้ของ Service ไม่ได้ตั้งชื่อ (ใช้ได้เพราะมีพอร์ตเดียว) ส่วน `TargetPort: http/TCP` คือชื่อพอร์ตของ container ที่อ้างถึง

### 3.4 Service ที่ไม่มี selector

ถ้าไม่ใส่ `selector` EndpointSlice controller จะไม่เขียนรายชื่อให้ ผู้ดูแลต้องสร้าง EndpointSlice เอง ใช้กับปลายทางที่ **อยู่นอกคลัสเตอร์** เช่น ฐานข้อมูลเดิมของบริษัทที่ยังไม่ได้ย้ายเข้า Kubernetes แต่อยากให้แอปเรียกด้วยชื่อ Service เหมือนของในคลัสเตอร์ ตัวอย่างแนวคิด (ไม่มีใน LAB ของบทนี้ IP `192.168.10.50` เป็นค่าสมมุติ)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: old-db
  namespace: som-shop
spec:                      # ไม่มี selector → ระบบไม่เขียน EndpointSlice ให้
  ports:
    - name: postgres
      port: 5432
      targetPort: 5432
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: old-db-1
  namespace: som-shop
  labels:
    kubernetes.io/service-name: old-db                   # ผูกกับ Service ด้วย label นี้
    endpointslice.kubernetes.io/managed-by: staff.example.com   # บอกว่าคนเขียนเอง ไม่ใช่ controller
addressType: IPv4
ports:
  - name: postgres         # ต้องตรงกับชื่อพอร์ตของ Service
    port: 5432
    protocol: TCP
endpoints:
  - addresses: ["192.168.10.50"]
    conditions:
      ready: true
```

แอปใน `som-shop` จะเรียก `old-db:5432` ได้เหมือน Service ปกติ และเมื่อย้าย db เข้าคลัสเตอร์แล้ว ก็แค่เปลี่ยน Service ให้มี selector โดยไม่ต้องแก้แอป

---

## 4. ClusterIP และ Service CIDR

{{FIG:T10}}

ClusterIP ทุกตัวมาจาก **Service CIDR** ซึ่งเป็นช่วง IP ที่กำหนดตอนสร้างคลัสเตอร์และ **แยกจาก Pod CIDR** ในคลัสเตอร์ kind ของเรา ผลจริงจาก LAB 0

```text
$ docker exec lab-control-plane cat /kind/kubeadm.conf | grep -i serviceSubnet
  serviceSubnet: 10.96.0.0/16

$ kubectl get svc -A
NAMESPACE     NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  4m57s
kube-system   kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   4m56s
```

| ช่วง | ใช้กับ | ตัวอย่างในคลัสเตอร์ของเรา |
|---|---|---|
| Service CIDR `10.96.0.0/16` | ClusterIP ของ Service | `web` = `10.96.55.132`, `som-db` = `10.96.93.105` |
| Pod CIDR `10.244.0.0/16` | IP ของ Pod (แต่ละ Node ได้ช่วงย่อย `/24`) | `10.244.1.x` บน `lab-worker2`, `10.244.2.x` บน `lab-worker` |

Service 2 ตัวที่มีอยู่ตั้งแต่สร้างคลัสเตอร์

- **`kubernetes`** (namespace `default`) = `10.96.0.1:443` เป็นทางเข้า API server สำหรับโปรแกรมที่รันใน Pod (ทุก Pod ได้ env `KUBERNETES_SERVICE_HOST=10.96.0.1`)
- **`kube-dns`** (namespace `kube-system`) = `10.96.0.10` พอร์ต 53 UDP/TCP เป็น DNS ของคลัสเตอร์ (CoreDNS) และพอร์ต 9153 สำหรับ metrics ทุก Pod ใช้ IP นี้เป็น `nameserver` (หัวข้อ 9)

กติกาที่ควรรู้

- ClusterIP **ไม่เปลี่ยนตลอดอายุของ Service** แต่ถ้าลบ Service แล้วสร้างใหม่ชื่อเดิม จะได้ ClusterIP ใหม่ (ชื่อ DNS ยังเหมือนเดิม จึงควรเรียกด้วยชื่อเสมอ)
- กำหนด `spec.clusterIP` เองได้ถ้าอยู่ในช่วง Service CIDR และยังว่าง แต่ไม่แนะนำ เพราะชนกับ Service อื่นได้ง่าย
- `spec.clusterIP: None` ไม่ใช่ "ไม่มี IP แบบผิดพลาด" แต่เป็นการขอ **headless Service** (หัวข้อ 8.2)

---

## 5. พอร์ต: port, targetPort, nodePort และชื่อพอร์ต

### 5.1 พอร์ต 3 ชั้น

{{FIG:T11}}

| ฟิลด์ | อยู่ที่ไหน | ใครใช้ | ค่าเริ่มต้น |
|---|---|---|---|
| `port` | Service | ลูกค้าในคลัสเตอร์ เรียก `<ชื่อ Service>:<port>` หรือ `<ClusterIP>:<port>` | ต้องระบุ |
| `targetPort` | container ใน Pod | kube-proxy ส่งต่อไปที่ `<Pod IP>:<targetPort>` | เท่ากับ `port` |
| `nodePort` | ทุก Node | ลูกค้านอกคลัสเตอร์ เรียก `<Node IP>:<nodePort>` (เฉพาะ `NodePort` และ `LoadBalancer`) | สุ่มในช่วง 30000–32767 |
| `protocol` | ทั้งสามชั้น | | `TCP` (หรือ `UDP`, `SCTP`) |

ตัวอย่างจาก LAB 3 ไฟล์ `labs/lab03-ports/web-alt-svc.yaml` รับที่พอร์ต 8080 แต่ส่งต่อไปพอร์ต 80 ของ Pod

```yaml
# LAB 3: Service รับที่พอร์ต 8080 แต่ส่งต่อไปพอร์ต 80 (ชื่อ http) ของ Pod
apiVersion: v1
kind: Service
metadata:
  name: web-alt
  namespace: shop
spec:
  selector:
    app: web
  ports:
    - port: 8080           # ลูกค้าเรียก http://web-alt:8080
      targetPort: http     # → containerPort ชื่อ http (80)
```

ผลจริง: `web-alt:8080` ได้หน้าเว็บ แต่ `web-alt` (พอร์ต 80 ที่ Service นี้ไม่ได้ประกาศ) **เงียบจนหมดเวลา** ไม่ใช่ถูกปฏิเสธ เพราะไม่มีกฎของ kube-proxy สำหรับพอร์ตนั้น และไม่มีเครื่องใดเป็นเจ้าของ ClusterIP ที่จะตอบปฏิเสธกลับมา

```text
$ kubectl -n shop get svc web-alt
NAME      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
web-alt   ClusterIP   10.96.141.242   <none>        8080/TCP   0s

$ kubectl -n shop exec client -- wget -qO- http://web-alt:8080
web v1 from web-gsgss

$ time kubectl -n shop exec client -- wget -qO- -T 3 http://web-alt
wget: download timed out
command terminated with exit code 1

real	0m3.060s
```

### 5.2 ชื่อพอร์ต (named port) และ Service หลายพอร์ต

{{FIG:T12}}

**named port** คือการตั้งชื่อให้ `containerPort` ใน Pod (`ports: [{name: http, containerPort: 80}]`) แล้วให้ Service อ้างด้วยชื่อ (`targetPort: http`) ข้อดีคือ

- เปลี่ยนเลขพอร์ตใน Pod ได้โดย **ไม่ต้องแก้ Service** (เช่น รุ่นใหม่ของแอปย้ายไปฟังพอร์ต 8080 แต่ยังตั้งชื่อ `http`)
- Pod แต่ละตัวที่ Service เลือกใช้เลขพอร์ตต่างกันได้ ถ้าชื่อเหมือนกัน (EndpointSlice เก็บเลขจริงต่อกลุ่ม)
- อ่าน manifest แล้วเข้าใจง่ายกว่าเลขลอย ๆ

Service ที่มี **มากกว่า 1 พอร์ตต้องตั้ง `name` ให้ทุกพอร์ต** ไฟล์ `labs/lab03-ports/web-multi-svc.yaml`

```yaml
# LAB 3: Service หลายพอร์ต — ต้องตั้ง name ให้ทุกพอร์ต
apiVersion: v1
kind: Service
metadata:
  name: web-multi
  namespace: shop
spec:
  selector:
    app: web
  ports:
    - name: http
      port: 80
      targetPort: http
    - name: alt
      port: 8080
      targetPort: http     # สองพอร์ตของ Service ชี้ไปพอร์ตเดียวกันของ Pod ได้
```

ผลจริง: `PORT(S)` เป็น `80/TCP,8080/TCP` ส่วน EndpointSlice มี PORTS `80,80` (ทั้งพอร์ต `alt` และ `http` ชี้ไปพอร์ต 80 ของ Pod)

```text
NAME        TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)           AGE
web-multi   ClusterIP   10.96.28.97   <none>        80/TCP,8080/TCP   0s
NAME              ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-multi-4gzd9   IPv4          80,80   10.244.1.5,10.244.1.4,10.244.2.6   0s
```

ถ้าพอร์ตที่สองไม่มีชื่อ (ไฟล์ `labs/lab03-ports/web-multi-noname.yaml`) API ปฏิเสธทันที

```text
The Service "web-noname" is invalid: spec.ports[1].name: Required value
```

(ถ้าไม่ตั้งชื่อทั้งสองพอร์ต จะได้ 2 บรรทัด `* spec.ports[0].name: Required value` และ `* spec.ports[1].name: Required value`)

> **ข้อควรรู้:** ใน LAB 3 การเรียก `web-multi` ครั้งแรกหลังสร้างเสร็จราว 1 วินาทีได้ `wget: can't connect to remote host (10.96.28.97): Connection refused` แล้วครั้งถัดไปใช้ได้ปกติ เพราะ kube-proxy ยังเขียนกฎไม่เสร็จ Service ที่เพิ่งสร้างจึงอาจต้องรอสักครู่

---

