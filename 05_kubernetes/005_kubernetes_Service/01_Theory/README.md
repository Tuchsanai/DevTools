# บทที่ 5: Kubernetes Service — ที่อยู่เดียวของร้านน้องส้ม

> **รายวิชา:** Software Development Tools and Environments (DevTools) · **CLO-5, CLO-6**
> **บทก่อนหน้า:** [บทที่ 4 Kubernetes Deployment](../../004_kubernetes_Deployment/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

อ่านบทนี้จบแล้วควรทำได้ 4 อย่าง

1. บอกได้ว่า **Service มี 3 แบบ** (ClusterIP, NodePort, LoadBalancer) แต่ละแบบเปิดให้ใครเข้าได้ และต่างกันอย่างไร
2. แยก **ที่อยู่ 3 แบบ** (Node IP, ClusterIP, Pod IP) กับ **port 4 ตัว** (`nodePort`, `port`, `targetPort`, `containerPort`) ออกจากกันได้
3. อธิบายว่า Service หา Pod เจอจาก **ป้าย (selector)** และ **Endpoints** อย่างไร อ่าน YAML ของ Service ออกทุกบรรทัด และเรียก Service ได้ทั้งด้วยชื่อในคลัสเตอร์ (**ClusterIP + DNS**) และจากนอกคลัสเตอร์ (**NodePort**)
4. บอกได้ว่า Service ยังทำอะไร **ไม่ได้** (ดูแลค่าตั้งค่า รหัสผ่าน และข้อมูลของร้าน) ก่อนไปบทถัดไป

## สารบัญ

1. [เริ่มเรื่อง: ลูกค้าหาร้านไม่เจอ](#1-เริ่มเรื่อง-ลูกค้าหาร้านไม่เจอ)
2. [Service คืออะไร](#2-service-คืออะไร)
3. [Service มีกี่แบบ และแต่ละแบบต่างกันอย่างไร](#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร)
4. [ที่อยู่ 3 แบบ และ port 4 ตัว: ศัพท์ที่ต้องแยกให้ออก](#4-ที่อยู่-3-แบบ-และ-port-4-ตัว-ศัพท์ที่ต้องแยกให้ออก)
5. [Service ทำงานอย่างไร](#5-service-ทำงานอย่างไร)
6. [อ่าน YAML ของ Service ทีละบรรทัด](#6-อ่าน-yaml-ของ-service-ทีละบรรทัด)
7. [เรียกด้วยชื่อ: DNS ในคลัสเตอร์](#7-เรียกด้วยชื่อ-dns-ในคลัสเตอร์)
8. [Service หา Pod จากป้าย](#8-service-หา-pod-จากป้าย)
9. [กับดัก: selector พิมพ์ผิด แล้ว Endpoints ว่าง](#9-กับดัก-selector-พิมพ์ผิด-แล้ว-endpoints-ว่าง)
10. [ClusterIP: ที่อยู่ภายในคลัสเตอร์](#10-clusterip-ที่อยู่ภายในคลัสเตอร์)
11. [NodePort: ประตูบนทุก Node](#11-nodeport-ประตูบนทุก-node)
12. [Service ระหว่างเปลี่ยนรุ่น: readinessProbe และ rolling update](#12-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update)
13. [อ่าน YAML ร้านน้องส้มทั้งไฟล์](#13-อ่าน-yaml-ร้านน้องส้มทั้งไฟล์)
14. [ปูทางบทถัดไป](#14-ปูทางบทถัดไป)
15. [สรุปและคำถามทบทวน](#15-สรุปและคำถามทบทวน)

> **อ่านหัวข้อ 3–4 ให้แยกออกก่อน** สองหัวข้อนี้เป็นแผนที่ของทั้งบท หัวข้อที่ 5 เป็นต้นไปลงรายละเอียดทีละเรื่อง
> หัวข้อใหม่จะเปิดด้วย **🎯 หัวข้อนี้เรียนเพื่อ** (อ่านแล้วตอบอะไรได้) และปิดด้วย **🧪 พิสูจน์ใน LAB** ซึ่งลิงก์ไปยังขั้นของ LAB ที่ได้เห็นเรื่องนั้นจริง

---

## 1. เริ่มเรื่อง: ลูกค้าหาร้านไม่เจอ

<p align="center">
  <img src="images/01-opening-customers-lost.png" alt="ลูกค้าถือแผนที่หาร้านไม่เจอ ท่อ port-forward ขาด ป้าย IP ของ Pod เปลี่ยน" width="800">
</p>

ในบทที่ 4 ร้านอาหารแมวน้องส้มเปลี่ยนเมนูได้โดยร้านไม่ปิดแล้ว แต่ **ลูกค้ายังหาร้านไม่เจอ** ([บทที่ 4 หัวข้อ 13](../../004_kubernetes_Deployment/01_Theory/README.md#13-port-forward-ระหว่างเปลี่ยนรุ่น-และบทถัดไป))

- `kubectl port-forward` ต่อท่อเข้า **Pod เดียว** ลูกค้าทุกคนไปกองที่สาขาเดียว
- พอ Pod นั้นถูกลบหรือเปลี่ยนรุ่น **ท่อขาด** ต้องรันใหม่เอง
- จะให้ลูกค้าจด **Pod IP** ไว้ก็ไม่ได้ เพราะ Pod ใหม่ได้ IP ใหม่ทุกครั้ง ([บทที่ 2 หัวข้อ 3](../../002_kubernetes_pod/01_Theory/README.md#3-pod-อยู่ที่ไหน-และคุยกันอย่างไร))

> "ร้านเรามีหลายสาขา สาขาเปลี่ยนตลอด ส้มต้องมี **พนักงานต้อนรับหน้าท่า** ที่นั่งประจำบูธเดิม ชื่อเดิม แล้วคอยส่งลูกค้าไปสาขาที่พร้อม" — กัปตันบอก

พนักงานต้อนรับคนนี้คือ **Service** ทบทวนอุปมาท่าเรือ แล้วเพิ่มตัวละครใหม่

<p align="center">
  <img src="images/02-harbor-metaphor-service.png" alt="อุปมาท่าเรือพร้อมพนักงานต้อนรับ Service และประตู NodePort" width="800">
</p>

- **container** = ตู้สินค้า / **Pod** = กล่องห่อตู้ มีป้าย IP 1 อัน (เปลี่ยนได้)
- **Node** = เรือ (`lab-worker`, `lab-worker2`) / **Control Plane** = หอบังคับการ
- **ReplicaSet** = หัวหน้าลูกเรือ / **Deployment** = ผู้จัดการลูกเรือ (บทที่ 3–4)
- **Service** = **พนักงานต้อนรับหน้าท่า** (เสื้อกั๊กสีส้ม) ประจำ **บูธต้อนรับ** มีป้ายชื่อคงที่ (`web`) กับป้ายที่อยู่ (ClusterIP) ถือ **กระดานรายชื่อกล่องที่พร้อม** (Endpoints)
- **NodePort** = **ประตูท่าเรือหมายเลข `30080`** มีบนเรือทุกลำ เปิดออกสู่ถนนด้านนอก
- **kube-proxy** = คนเรือที่ **วางรางส่งลูกค้า** บนเรือทุกลำ / **DNS** = **สมุดรายชื่อท่า** (ชื่อ → ที่อยู่)

> **ขอบเขตบทนี้:** Service มี 3 แบบ ซึ่งจะรู้จักครบในหัวข้อ 3 แต่ LAB ลงมือแค่ 2 แบบคือ **ClusterIP** (ใช้ในคลัสเตอร์) และ **NodePort** (เปิดออกนอกคลัสเตอร์) ส่วน Ingress สำหรับเว็บหลายโดเมนอยู่ในบทที่ 8

---

## 2. Service คืออะไร

<p align="center">
  <img src="images/03-what-is-service.png" alt="เทียบไม่มี Service ต้องจำ Pod IP 3 อัน กับมี Service web ที่เรียกชื่อเดียวแล้วกระจายไป Pod ที่มี label app=web" width="800">
</p>

**Service คือ object ที่ให้ "ที่อยู่เดียวที่คงที่" กับกลุ่ม Pod ที่ติดป้ายเดียวกัน แล้วกระจายลูกค้าไปยัง Pod ที่พร้อมในกลุ่มนั้น**

- เราบอกแค่ **"ส่งไป Pod ป้ายไหน"** (`selector`) กับ **"เปิดรับ port ไหน ส่งต่อ port ไหน"** (`ports`)
- Service ได้ **ชื่อ** (`web`) และ **IP ภายในคลัสเตอร์** (ClusterIP) ที่ไม่เปลี่ยนตลอดอายุของ Service
- Pod จะถูกลบ เกิดใหม่ เปลี่ยนรุ่นกี่รอบ ลูกค้าก็เรียกที่อยู่เดิม

ตัวอย่างจริงจาก LAB 1: Pod `client` เรียก `http://web` ซ้ำ ได้คำตอบจาก Pod คนละตัว

```text
$ kubectl get svc
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP   2m32s
web          ClusterIP   10.96.169.141   <none>        80/TCP    0s

$ kubectl exec client -- wget -qO- http://web
Hello from Pod web-65b66cc75b-jmvlk
$ kubectl exec client -- wget -qO- http://web
Hello from Pod web-65b66cc75b-jmvlk
$ kubectl exec client -- wget -qO- http://web
Hello from Pod web-65b66cc75b-wrw8f
...
```

- `web` = Service ของเรา `TYPE` = `ClusterIP` (ค่าเริ่มต้น) ได้ที่อยู่ `10.96.169.141`
- `kubernetes` = Service ที่คลัสเตอร์สร้างไว้เองตั้งแต่แรก (ทางเข้า kube-apiserver) ไม่ต้องไปยุ่ง
- 6 ครั้งได้ `jmvlk` 4 ครั้ง `wrw8f` 2 ครั้ง (ตัวที่ 3 `gm2pc` ตอบตอนเรียก Pod IP ตรง ๆ ในขั้นที่ 7) Service **สุ่มเลือก Pod ทีละการเชื่อมต่อ** ไม่ได้วนตามลำดับ

เทียบกับ port-forward ที่ใช้มาตั้งแต่บทที่ 2

| | `kubectl port-forward` (บทที่ 2–4) | Service (บทนี้) |
|---|---|---|
| ส่งไปกี่ Pod | Pod เดียวที่ kubectl เลือก | ทุก Pod ที่ป้ายตรงและพร้อม |
| Pod ถูกลบ/เปลี่ยนรุ่น | ท่อขาด ต้องรันใหม่ | ไม่สะดุด Service ส่งไปตัวใหม่เอง |
| อยู่ได้นานแค่ไหน | เท่ากับ terminal ที่รันค้างไว้ | อยู่ในคลัสเตอร์จนกว่าจะลบ |
| ใครใช้ได้ | เครื่องที่รันคำสั่งเท่านั้น | Pod ทุกตัวในคลัสเตอร์ (และคนนอก ถ้าเป็น NodePort) |
| ใช้ทำอะไร | ดีบัก ส่องดู Pod ตัวเดียว | ที่อยู่จริงของแอป |

---

## 3. Service มีกี่แบบ และแต่ละแบบต่างกันอย่างไร

> 🎯 **หัวข้อนี้เรียนเพื่อ:** แยก Service ทั้ง 3 แบบให้ออกก่อนเรื่องอื่น รู้ว่าแต่ละแบบเปิดให้ **ใคร** เข้าถึงได้ และ LAB ไหนใช้แบบไหน หัวข้อหลังจากนี้ทั้งหมดพูดถึงแค่ 2 แบบแรก

<p align="center">
  <img src="images/03a-service-types-layers.png" alt="Service 3 แบบซ้อนกันเป็นชั้น ClusterIP อยู่ในสุด NodePort ครอบ ClusterIP และ LoadBalancer ครอบ NodePort" width="800">
</p>

แบบของ Service กำหนดด้วย field `type:` ใต้ `spec:` ซึ่งมี 3 ค่า

- **ทั้ง 3 แบบซ้อนกันเป็นชั้น** แบบที่อยู่ชั้นนอกมีความสามารถทุกอย่างของแบบที่อยู่ข้างใน แล้วเพิ่มช่องทางเข้าถึงจากนอกคลัสเตอร์อีก 1 ชั้น
  - **ClusterIP** มีชื่อ DNS + IP ที่ใช้ได้ภายในคลัสเตอร์
  - **NodePort** = ClusterIP + เปิด port เดียวกันบน Node ทุกตัว
  - **LoadBalancer** = NodePort + load balancer ของผู้ให้บริการคลาวด์
- ถ้าไม่ระบุ `type:` จะได้ **ClusterIP**

| แบบ (`type:`) | ได้อะไร | ใครเข้าถึงได้ | ที่อยู่ที่ใช้เรียก | เหมาะกับ | ในบทนี้ |
|---|---|---|---|---|---|
| `ClusterIP` (ค่าเริ่มต้น) | ชื่อ DNS + IP ภายในคลัสเตอร์ | Pod ในคลัสเตอร์เท่านั้น | `http://som-menu` | ระบบที่ใช้กันภายในคลัสเตอร์ เช่น ฐานข้อมูล | LAB 1–2 |
| `NodePort` | ClusterIP + `nodePort` บน Node ทุกตัว | + เครื่องนอกคลัสเตอร์ที่เข้าถึง Node ได้ | `<Node IP>:30080` | ทดลองบนเครื่อง หรือคลัสเตอร์ที่ไม่ได้อยู่บนคลาวด์ | LAB 3–4 |
| `LoadBalancer` | NodePort + load balancer ของคลาวด์ | + ผู้ใช้บนอินเทอร์เน็ต | `<EXTERNAL-IP>:80` | ระบบจริงบนคลาวด์ (AWS, GCP, Azure) | ลองดูใน LAB 3 |

ภาพสถาปัตยกรรมทั้ง 3 แบบด้านล่างใช้ Service `som-menu` ของ LAB 4 (รับที่ port 80 ส่งต่อไป port 3000 ของ Pod) เป็นตัวอย่างเดียวกัน ส่วนที่ต่างกันในภาพจึงเป็นผลของการเปลี่ยน `type:` อย่างเดียว ให้สังเกตว่า request **เข้ามาจากไหน** และ **ผ่านอะไรบ้าง**

### 3.1 ClusterIP: เข้าถึงได้เฉพาะภายในคลัสเตอร์

<p align="center">
  <img src="images/03b-arch-clusterip.png" alt="สถาปัตยกรรม ClusterIP: Pod client เรียก http://som-menu:80 Service ส่งต่อไป Pod 3 ตัวที่ port 3000 browser นอกคลัสเตอร์เข้าไม่ได้" width="800">
</p>

- Service ได้ **ชื่อ DNS** (`som-menu`) กับ **ClusterIP** 1 อัน (`10.96.187.5`) Pod ทุกตัวในคลัสเตอร์เรียก `http://som-menu` ได้ ①
- Service ส่ง request ต่อไป Pod ที่ label ตรงกับ selector และพร้อมแล้ว ที่ port 3000 ไม่ว่า Pod นั้นอยู่ Node ไหน ②
- browser บนเครื่องเรา **เรียก ClusterIP ตรง ๆ ไม่ได้** เพราะ IP ช่วง `10.96.x.x` ใช้ได้เฉพาะภายในคลัสเตอร์
- LAB 1–2 จึงสร้าง Pod `client` ไว้เป็นผู้เรียก Service จากภายในคลัสเตอร์

```yaml
  type: ClusterIP            # ค่าเริ่มต้น: ได้ IP ภายในคลัสเตอร์ 1 อันที่ไม่เปลี่ยน
```

(จาก `labs/lab01-clusterip/web-svc.yaml` รายละเอียดอยู่ในหัวข้อ 10)

### 3.2 NodePort: เปิด port เดียวกันบน Node ทุกตัว

<p align="center">
  <img src="images/03c-arch-nodeport.png" alt="สถาปัตยกรรม NodePort: browser เข้าทาง nodePort 30080 ซึ่งเปิดบน Node ทั้ง 3 ตัว แล้วส่งต่อไป Service port 80 และ Pod port 3000" width="800">
</p>

- ได้ทุกอย่างของ ClusterIP (Pod ในคลัสเตอร์ยังเรียก `http://som-menu` ได้) **แล้วเพิ่ม** `nodePort` เลขเดียวกันบน Node ทุกตัว
- เครื่องนอกคลัสเตอร์เรียก `<Node IP ตัวไหนก็ได้>:30080` ① request ถูกส่งต่อไปที่ Service port 80 ② แล้ว Service ส่งต่อไป Pod ที่ port 3000 ③
- Node ที่ไม่มี Pod ของแอปอยู่เลย (`lab-control-plane`) ก็เปิด port นี้ด้วย kube-proxy บน Node นั้นส่ง request ต่อไป Pod บน Node อื่น
- ใน k8s-lab `localhost:30080` บนเครื่องเราถูกส่งต่อไปที่ port 30080 ของ `lab-control-plane` (หัวข้อ 11)

```yaml
  type: NodePort
  ...
      nodePort: 30080        # นอกคลัสเตอร์เปิด http://localhost:30080
```

(จาก `som-menu/k8s/som-menu-svc.yaml` รายละเอียดอยู่ในหัวข้อ 11)

### 3.3 LoadBalancer: ใช้ load balancer ของผู้ให้บริการคลาวด์

<p align="center">
  <img src="images/03d-arch-loadbalancer.png" alt="สถาปัตยกรรม LoadBalancer: ผู้ใช้บนอินเทอร์เน็ตเรียก EXTERNAL-IP ของ load balancer ของคลาวด์ ซึ่งส่งต่อไปที่ nodePort ของทุก Node" width="800">
</p>

- ได้ทุกอย่างของ NodePort แล้ว **ให้ผู้ให้บริการคลาวด์** สร้าง load balancer ให้ 1 ตัว IP สาธารณะของ load balancer แสดงในคอลัมน์ `EXTERNAL-IP`
- ผู้ใช้เรียกที่อยู่เดียว ไม่ต้องรู้ว่ามี Node กี่ตัวหรือ IP อะไร ① load balancer ส่ง request ต่อไปที่ nodePort ของ Node ที่ยังทำงานอยู่ (Kubernetes สุ่มเลข nodePort ให้) หลังจากนั้นเส้นทางเหมือน NodePort ทุกอย่าง ②③
- **บน kind ใช้ได้ไม่เต็มที่** เพราะไม่มีผู้ให้บริการคลาวด์มาสร้าง load balancer ให้ คอลัมน์ `EXTERNAL-IP` จะค้างเป็น `<pending>` LAB 3 ขั้นที่ 6 ลองสร้างให้เห็น (ผลจริงอยู่ในหัวข้อ 3.4) ส่วนงานหลักของบทนี้ใช้ NodePort

### 3.4 YAML ของ 3 แบบต่างกันตรงไหน

<p align="center">
  <img src="images/03e-yaml-types-compare.png" alt="YAML ของ ClusterIP NodePort และ LoadBalancer วางเทียบกัน วงบรรทัด type และ nodePort ที่ต่างกัน ใต้แต่ละไฟล์มีผล kubectl get svc และเส้นทางของ request" width="800">
</p>

วาง YAML ของทั้ง 3 แบบเทียบกัน ทั้ง 3 ไฟล์เป็นไฟล์จริงใน LAB (`web-svc.yaml` ของ LAB 1, `web-svc-nodeport.yaml` และ `web-svc-lb.yaml` ของ LAB 3)

- **① `type:`** เป็นบรรทัดเดียวที่เลือกแบบของ Service ส่วน `selector`, `port` และ `targetPort` (พื้นเทา) เหมือนกันทุกแบบ
- **② `nodePort:`** เขียนได้เฉพาะแบบ NodePort และ LoadBalancer ถ้าไม่เขียน Kubernetes สุ่มเลขให้
- **คอลัมน์ `PORT(S)`** ของ ClusterIP มีแค่ `80/TCP` ส่วนแบบ NodePort และ LoadBalancer แสดงเป็น `port:nodePort`
- **เส้นทางของ request** (แถวล่างของภาพ) ยิ่ง Service อยู่ชั้นนอก request ยิ่งเริ่มจากที่ไกลกว่า แต่ทุกแบบผ่าน ClusterIP แล้วไปจบที่ Pod เหมือนกัน

ผลจริงเมื่อ apply ทั้ง `web-svc-nodeport.yaml` และ `web-svc-lb.yaml` ใน LAB 3

```text
$ kubectl get svc
NAME           TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes     ClusterIP      10.96.0.1      <none>        443/TCP        5m49s
web-lb         LoadBalancer   10.96.28.234   <pending>     80:31484/TCP   11s
web-nodeport   NodePort       10.96.231.50   <none>        80:30080/TCP   50s

$ curl http://172.19.0.2:31484
Hello from Pod web-65b66cc75b-z6qjn
```

- `EXTERNAL-IP <pending>` = รอผู้ให้บริการคลาวด์สร้าง load balancer ให้ ซึ่งบน kind จะไม่มีวันได้
- `80:31484/TCP` = Kubernetes สุ่ม nodePort `31484` ให้เอง และเรียก `<Node IP>:31484` ได้ทันที แม้ load balancer ยังไม่มา ส่วน NodePort ข้างในใช้ได้แล้ว

> **ประโยคเดียวที่ต้องจำ:** **ClusterIP** เข้าถึงได้เฉพาะในคลัสเตอร์ · **NodePort** = ClusterIP + port บน Node ทุกตัว · **LoadBalancer** = NodePort + load balancer ของคลาวด์ บทนี้ลงมือทำแค่ 2 แบบแรก

> 🧪 **พิสูจน์ใน LAB:** ClusterIP เรียกได้จาก Pod `client` ด้วยชื่อ → **LAB 1** ขั้นที่ [5](../02_LAB/README.md#ขั้นที่-5-เรียก-service-ด้วยชื่อ) · NodePort เรียกได้ทั้งจาก `localhost:30080` และจาก IP ของทุก Node → **LAB 3** ขั้นที่ [3](../02_LAB/README.md#ขั้นที่-3-เรียกจากนอกคลัสเตอร์ด้วย-curl), [4](../02_LAB/README.md#ขั้นที่-4-ประตูเปิดบนทุก-node) · LoadBalancer ได้ `EXTERNAL-IP <pending>` แต่ nodePort ใช้ได้ → **LAB 3** ขั้นที่ [6](../02_LAB/README.md#ขั้นที่-6-ลองแบบ-loadbalancer-บน-kind)

---

## 4. ที่อยู่ 3 แบบ และ port 4 ตัว: ศัพท์ที่ต้องแยกให้ออก

> 🎯 **หัวข้อนี้เรียนเพื่อ:** แยกศัพท์ที่สะกดคล้ายกัน (Pod / port, Node / nodePort, ClusterIP) และรู้ว่าตัวเลขแต่ละตัวในไฟล์ LAB เป็นของ object ไหน ก่อนอ่าน YAML และผลของ `kubectl get svc`

### ศัพท์ที่สะกดคล้ายกัน แต่เป็นคนละอย่าง

- **Pod** คือหน่วยที่ container ของแอปรันอยู่ ส่วน **port** คือ **หมายเลข port** ของ TCP ที่รับการเชื่อมต่อ สะกดคล้ายกันแต่ไม่เกี่ยวกัน
- **Node** คือเครื่อง (worker หรือ control-plane) ในคลัสเตอร์ ส่วน **nodePort** คือ **หมายเลข port บน Node** ที่ Service สั่งให้เปิด
- **NodePort** (N ตัวใหญ่) คือชื่อ **แบบ** ของ Service (`type: NodePort`) ส่วน **nodePort** (n ตัวเล็ก) คือ **field ตัวเลข** ใต้ `ports:` (`nodePort: 30080`)
- **ClusterIP** มี 2 ความหมาย
  - ชื่อ **แบบ** ของ Service (`type: ClusterIP`)
  - **IP ของ Service** ในคอลัมน์ `CLUSTER-IP` เช่น `10.96.187.5` Service ทุกแบบในบทนี้มี IP นี้

### ที่อยู่ 3 แบบ คู่กับ port 4 ตัว

<p align="center">
  <img src="images/04a-addresses-and-ports.png" alt="เส้นทางของ request จาก browser ผ่าน Node ไป Service ไป Pod แต่ละชั้นมี IP และ port ของตัวเอง พร้อมตารางบอกว่าเขียนไว้ไฟล์ไหน ใครใช้ และเปลี่ยนไหม" width="800">
</p>

request 1 ครั้งที่มาจากนอกคลัสเตอร์ผ่าน 3 ชั้น คือ Node → Service → Pod แต่ละชั้นมี **IP** และ **port** ของตัวเอง ตัวเลขในตารางมาจาก Service `som-menu` ใน LAB 4

| port | เปิดอยู่ที่ไหน | ใช้คู่กับ IP | ใครเรียก port นี้ | กำหนดในไฟล์ไหน | LAB 4 |
|---|---|---|---|---|---|
| `nodePort` | Node ทุกตัว (Service สั่งให้เปิด) | Node IP เช่น `172.19.0.4` | เครื่องนอกคลัสเตอร์ | Service (เฉพาะแบบ NodePort / LoadBalancer) | `30080` |
| `port` | Service | ClusterIP `10.96.187.5` หรือชื่อ `som-menu` | Pod ในคลัสเตอร์ | Service | `80` |
| `targetPort` | Pod ปลายทาง (Service ส่ง request ต่อมาที่ port นี้) | Pod IP เช่น `10.244.2.14` | Service | Service | `3000` |
| `containerPort` | container ใน Pod | Pod IP | port ที่แอปเปิดรับ | Deployment | `3000` |

- `targetPort` กับ `containerPort` หมายถึง **port เดียวกัน** (port ของแอปใน Pod) ที่เขียนไว้ 2 ไฟล์ จึงต้องเป็นเลขเดียวกันเสมอ
- `containerPort` เป็นข้อมูลประกอบเท่านั้น แอปจะรับการเชื่อมต่อที่ port ไหนขึ้นกับโค้ดของแอป (`server.js` ฟังที่ค่า `PORT=3000` ที่ตั้งไว้ใน Dockerfile)
- ถ้าไม่ระบุ `targetPort` Kubernetes ใช้เลขเดียวกับ `port` ถ้าไม่ระบุ `nodePort` Kubernetes สุ่มเลขในช่วง 30000–32767 ให้

### ไล่ตัวเลขจริงตั้งแต่ LAB 1 ถึง LAB 4

| LAB | Service (ไฟล์) | `type` | `nodePort` | `port` | `targetPort` | `containerPort` | เรียกด้วย |
|---|---|---|---|---|---|---|---|
| 1–2 | `web` (`web-svc.yaml`) | ClusterIP | – | 80 | 80 | 80 (nginx) | `wget -qO- http://web` จาก Pod `client` |
| 3 | `web-nodeport` (`web-svc-nodeport.yaml`) | NodePort | 30080 | 80 | 80 | 80 (nginx) | `curl http://localhost:30080` |
| 4 | `som-menu` (`som-menu-svc.yaml`) | NodePort | 30080 | 80 | 3000 | 3000 (Node.js) | browser `http://localhost:30080` |

- **LAB 1 มีเลข 80 อยู่ 2 ตัว** ทั้ง 2 ตัวเป็น 80 เพราะ nginx ฟังที่ port 80
  - `port: 80` คือ port ของ Service เลือก 80 เพื่อให้เรียก `http://web` ได้โดยไม่ต้องระบุ port
  - `targetPort: 80` คือ port ของ Pod ที่ Service ส่ง request ต่อไป
  - เลขเท่ากันแต่เป็น **คนละ port**: ตัวหนึ่งอยู่ที่ ClusterIP ของ Service อีกตัวอยู่ที่ Pod IP
- **LAB 3** เพิ่มแค่ `nodePort: 30080` เครื่องนอกคลัสเตอร์จึงเรียกได้
- **LAB 4** แอปฟังที่ port 3000 จึงเปลี่ยน `targetPort` เป็น 3000 ส่วน `port` ยังเป็น 80 ตัวเลขทั้ง 3 ตัวไม่ซ้ำกัน จึงเห็นชัดที่สุดว่าแต่ละตัวเป็นคนละ port

### เห็นทั้ง 3 ตัวในผลจริงของ LAB 4

```text
$ kubectl get svc
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
som-menu     NodePort    10.96.187.5     <none>        80:30080/TCP   11s     ← port:nodePort

$ kubectl describe svc som-menu
Port:                     <unset>  80/TCP
TargetPort:               3000/TCP
NodePort:                 <unset>  30080/TCP
Endpoints:                10.244.1.9:3000,10.244.2.14:3000,10.244.2.15:3000    ← ลงท้าย :3000 = targetPort
```

- คอลัมน์ `PORT(S)` แสดงเป็น **`port:nodePort`** (`80:30080`) ไม่มี targetPort ในคอลัมน์นี้ ต้องดูจาก `describe`
- `Endpoints` ลงท้ายด้วย **targetPort** เสมอ เพราะเป็น IP:port จริงของ Pod

> **เคล็ดลับ:** จำตามเส้นทางของ request จากนอกเข้าใน **nodePort → port → targetPort** (Node → Service → Pod) และ `targetPort` ต้องเท่ากับ `containerPort` ใน Deployment เสมอ

> 🧪 **พิสูจน์ใน LAB:** `describe svc` ของ `som-menu` แสดง `Port 80` → `TargetPort 3000` → `NodePort 30080` ครบ และ Endpoints ลงท้าย `:3000` → **LAB 4** ขั้นที่ [5](../02_LAB/README.md#ขั้นที่-5-เปิดร้าน) · LAB 1 ที่ `port` กับ `targetPort` เป็น 80 ทั้งคู่ → **LAB 1** ขั้นที่ [3](../02_LAB/README.md#ขั้นที่-3-service-ส่งงานให้ใคร-endpoints)

---

## 5. Service ทำงานอย่างไร

<p align="center">
  <img src="images/04-service-endpoints-kubeproxy.png" alt="selector ไปเป็น Endpoints โดย endpointslice-controller แล้ว kube-proxy วางรางบนทุก Node" width="800">
</p>

พนักงานต้อนรับไม่ได้เดินพาลูกค้าไปเอง งานแบ่งเป็น 3 ช่วง

1. **selector → รายชื่อ Pod** : **endpointslice-controller** ใน **kube-controller-manager** (หอบังคับการ) คอยดูว่า Pod ไหนติดป้ายตรง `selector` และ **พร้อม** แล้วจดเป็น **EndpointSlice** (กระดานรายชื่อ = IP:port ของ Pod)
2. **รายชื่อ → ราง** : **kube-proxy** ซึ่งมี **1 ตัวบนทุก Node** อ่าน Service กับรายชื่อนี้ แล้ววางกฎเครือข่ายบนเรือของตัวเองว่า "ใครเรียก ClusterIP:port นี้ ส่งต่อไป Pod ในรายชื่อสักตัว"
3. **ราง → Pod** : ลูกค้าเรียกที่อยู่ของ Service จากเรือลำไหนก็ได้ กฎบนเรือลำนั้นส่งต่อไป Pod ตัวหนึ่ง (อยู่เรือเดียวกันหรือคนละลำก็ได้)

kube-proxy 3 ตัว (1 ตัวต่อ Node) เห็นตั้งแต่ LAB 0

```text
$ kubectl get pods -A
NAMESPACE     NAME                                        READY   STATUS    RESTARTS   AGE
...
kube-system   kube-controller-manager-lab-control-plane   1/1     Running   0          77s
kube-system   kube-proxy-46hjr                            1/1     Running   0          67s
kube-system   kube-proxy-98vh8                            1/1     Running   0          64s
kube-system   kube-proxy-gggjh                            1/1     Running   0          64s
```

### ดูรายชื่อจริงใน LAB 1

(ตัดคอลัมน์ท้ายของ `-o wide` และบรรทัดที่ไม่เกี่ยวออก)

```text
$ kubectl get pods -o wide
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE
web-65b66cc75b-gm2pc   1/1     Running   0          0s    10.244.2.6   lab-worker
web-65b66cc75b-jmvlk   1/1     Running   0          0s    10.244.2.5   lab-worker
web-65b66cc75b-wrw8f   1/1     Running   0          0s    10.244.1.3   lab-worker2

$ kubectl describe svc web
Name:                     web
Selector:                 app=web                ← หา Pod จากป้ายนี้
Type:                     ClusterIP
IP:                       10.96.169.141          ← ที่อยู่ของ Service
Port:                     <unset>  80/TCP        ← port ของ Service
TargetPort:               80/TCP                 ← port ของ container ที่ส่งต่อไป
Endpoints:                10.244.2.6:80,10.244.1.3:80,10.244.2.5:80   ← Pod IP ทั้ง 3 ตัว
...

$ kubectl get endpointslices
NAME         ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
kubernetes   IPv4          6443    172.19.0.4                         2m33s
web-vn2gl    IPv4          80      10.244.2.6,10.244.1.3,10.244.2.5   1s
```

- บรรทัด `Endpoints:` คือ **Pod IP:targetPort** ของทั้ง 3 Pod ตรงกับคอลัมน์ `IP` ของ `get pods` เป๊ะ
- EndpointSlice `web-vn2gl` ถูกสร้างให้เอง (ชื่อ Service + ท้ายสุ่ม) เราไม่ได้เขียนไฟล์ของมันเลย
- `<unset>` หน้า `80/TCP` คือ **ชื่อของ port** ที่เราไม่ได้ตั้ง ไม่ใช่ error
- เรียก Pod IP ตรง ๆ ก็ยังได้ (`wget -qO- http://10.244.2.6` ตอบ `web-65b66cc75b-gm2pc`) แต่ IP นี้หายไปพร้อม Pod

> **ประโยคเดียวที่ต้องจำ:** Service **ไม่ได้รับลูกค้าแล้วส่งต่อเอง** มันเป็น "ที่อยู่ + รายชื่อ" ส่วนคนที่ทำให้ลูกค้าไปถึง Pod จริงคือ **kube-proxy บนทุก Node**

---

## 6. อ่าน YAML ของ Service ทีละบรรทัด

YAML ของบทนี้ใช้กฎเดิมจาก [บทที่ 2 หัวข้อ 5](../../002_kubernetes_pod/01_Theory/README.md#5-yaml-ฉบับเข้าใจง่าย) ทบทวนสั้น ๆ

- `key: value` = ค่าเดี่ยว / เยื้องเข้า = **เป็นลูก** / เยื้องเท่ากัน = **เป็นพี่น้อง**
- `- ` (ขีด + เว้นวรรค) = **เริ่มรายการใหม่ 1 ชิ้น** (`ports` เป็น list เหมือน `containers`)
- object ที่ห่อ Pod มี `metadata` / `spec` **2 ชุด** (บทที่ 3–4)

สิ่งใหม่ของ YAML บทนี้: **Service มี `metadata` / `spec` ชุดเดียว เพราะ Service ไม่มี `template` และไม่สร้าง Pod** มันแค่ชี้ไปหา Pod ที่มีอยู่แล้ว

### 6.1 วาง Deployment คู่กับ Service

<p align="center">
  <img src="images/05-yaml-service-vs-deployment.png" alt="web-deploy.yaml มี template และ matchLabels ส่วน web-svc.yaml สั้นกว่า ไม่มีแม่พิมพ์" width="800">
</p>

LAB 1 ใช้ 2 ไฟล์คู่กัน วางเทียบกัน (ตัด comment และบรรทัด `command` / `args` ออกเป็น `...`) **วงสีเดียวกัน = ค่าที่ต้องตรงกัน** ลูกศรบอกว่า Service เอาค่ามาจากตรงไหนใน Deployment

<p align="center">
  <img src="images/05a-yaml-deploy-vs-svc-map.png" alt="web-deploy.yaml กับ web-svc.yaml วางคู่กัน ลูกศรจากป้ายใน template ไป selector ของ Service และจาก containerPort ไป targetPort" width="900">
</p>

อ่านตามเลขในภาพ

- **① `apiVersion` / `kind` คนละกลุ่ม** Service อยู่กลุ่มหลัก **`v1`** (เหมือน Pod) ไม่ใช่ `apps/v1` แบบ Deployment
- **② `name` ซ้ำกันได้** เพราะเป็น object คนละชนิด ชื่อ Service คือชื่อที่ Pod อื่นใช้เรียก เช่น `http://web` (หัวข้อ 7)
- **③ ป้ายต้องตรงกัน** `selector` ของ Service จับป้ายใน **`template.metadata.labels`** ของ Deployment (= ป้ายบนตัว Pod) ไม่ใช่ป้ายของตัว Deployment และ selector ของ Service **ใส่ป้ายตรง ๆ** ไม่มี `matchLabels:` คั่น
- **④ `targetPort` ต้องตรงกับ `containerPort`** คือ port ที่แอปใน Pod ฟังอยู่จริง Service ส่งลูกค้าต่อไปที่เลขนี้
- **⑤ `port` เป็นของ Service เอง** คือ port ที่คนเรียกใช้ จะเป็นคนละเลขกับ `targetPort` ก็ได้ (หัวข้อ 4)
- **⑥ ส่วนเส้นประสีเทามีแค่ฝั่ง Deployment** Service **ไม่มี `replicas` ไม่มี `template` ไม่มี `containers`** มันไม่สร้าง Pod แค่ชี้ไปหา ลบ Service ทิ้ง Pod ก็ยังอยู่ครบ

### 6.2 ไล่ไฟล์จริงจาก LAB 1

ไฟล์ `02_LAB/labs/lab01-clusterip/web-svc.yaml`

```yaml
# LAB 1, 2: Service แรก (ClusterIP) — ที่อยู่เดียวของ Pod ทุกตัวที่ติดป้าย app=web ใช้ได้เฉพาะในคลัสเตอร์
apiVersion: v1               # Service อยู่กลุ่มหลัก v1 เหมือน Pod
kind: Service
metadata:
  name: web                  # ชื่อ Service = ชื่อที่ Pod อื่นใช้เรียก เช่น http://web
spec:
  type: ClusterIP            # ค่าเริ่มต้น: ได้ IP ภายในคลัสเตอร์ 1 อันที่ไม่เปลี่ยน
  selector:
    app: web                 # ส่งงานให้ Pod ที่มีป้ายนี้ (ไม่มี matchLabels แบบ ReplicaSet)
  ports:
    - port: 80               # port ของ Service (คนเรียกใช้ port นี้)
      targetPort: 80         # port ของ container ใน Pod ที่จะส่งต่อไป
```

ไฟล์นี้ใช้ใน LAB 1 และ LAB 2

อ่านทีละบรรทัด

| บรรทัด | ความหมาย |
|---|---|
| `apiVersion: v1` | Service อยู่กลุ่มหลัก รุ่น `v1` (เหมือน Pod) |
| `kind: Service` | ขอสร้าง **Service** |
| `metadata:` → `name: web` | Service ชื่อ `web` = **ชื่อที่ใช้เรียก** (`http://web`) และชื่อใน DNS (หัวข้อ 7) |
| `spec:` → `type: ClusterIP` | แบบของ Service ได้ IP ภายในคลัสเตอร์ (ไม่เขียนก็ได้ เพราะเป็นค่าเริ่มต้น) |
| `  selector:` → `app: web` | ส่งลูกค้าไปทุก Pod ที่ติดป้าย `app=web` |
| `  ports:` | รายการ port ที่ Service เปิดรับ (มีได้หลายชิ้น) |
| `    - port: 80` | port ของ **Service** คนเรียกใช้ `web:80` (ไม่ใส่ port ใน URL = 80) |
| `      targetPort: 80` | port ของ **container ใน Pod** ที่ส่งต่อไป ต้องตรงกับ `containerPort` |

แปลทั้งไฟล์เป็นประโยคเดียว: **"ขอ Service ชื่อ `web` แบบ ClusterIP รับลูกค้าที่ port 80 แล้วส่งต่อไป port 80 ของ Pod ทุกตัวที่ติดป้าย `app=web`"**

### 6.3 แก้บรรทัดไหน แล้วเกิดอะไร

| แก้อะไรใน `web-svc.yaml` แล้ว apply | สิ่งที่เกิด | เห็นที่ |
|---|---|---|
| `type: ClusterIP` → `NodePort` และเพิ่ม `nodePort: 30080` | ได้ประตู 30080 บนทุก Node คนนอกคลัสเตอร์เข้าได้ ClusterIP ยังอยู่ | LAB 3 (`web-svc-nodeport.yaml`) |
| `selector` จาก `app: web` เป็น `app: wbe` | apply ผ่าน แต่ **Endpoints ว่าง** เรียกแล้วได้ `Connection refused` | LAB 2 (`web-svc-typo.yaml`) หัวข้อ 9 |
| `targetPort` เป็นเลขที่แอปไม่ได้ฟัง (เช่น 8080 กับ nginx ที่ฟัง 80) | apply ผ่าน Endpoints มีครบแต่ลงท้าย `:8080` เรียกแล้วได้ `Connection refused` | LAB 2 (`web-svc-wrongport.yaml`) ขั้นที่ 6 |
| `port: 80` เป็น `8080` | Pod ในคลัสเตอร์ต้องเรียก `http://web:8080` ส่วน Pod ปลายทางไม่รู้เรื่อง | หัวข้อ 4 |

> **⚠️ กับดัก:** แถวที่ 2 กับ 3 เป็นความผิดที่ **apply ผ่านทุกครั้ง** เพราะ Kubernetes ไม่รู้ว่าเราตั้งใจส่งไป Pod ไหน หรือแอปฟัง port อะไร ต้องตรวจเองด้วย `kubectl describe svc`

---

## 7. เรียกด้วยชื่อ: DNS ในคลัสเตอร์

<p align="center">
  <img src="images/07-dns-lookup.png" alt="Pod client ถาม kube-dns ว่า web.default.svc.cluster.local คือใคร ได้ ClusterIP 10.96.169.141 แล้วชื่อเต็มแบ่งเป็นชื่อ Service namespace และ svc.cluster.local" width="800">
</p>

Pod `client` เรียก `http://web` ได้ ทั้งที่ไม่รู้ IP เพราะคลัสเตอร์มี **DNS** (สมุดรายชื่อท่า) แปลชื่อ Service เป็น ClusterIP ให้

DNS ของคลัสเตอร์ก็เป็น Service ตัวหนึ่ง ชื่อ `kube-dns` เห็นตั้งแต่ LAB 0

```text
$ kubectl get svc -A
NAMESPACE     NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  77s
kube-system   kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   76s
```

- `kube-dns` ส่งต่อให้ Pod `coredns-...` 2 ตัวใน `kube-system` (Pod ที่ทำหน้าที่สมุดรายชื่อจริง)
- Pod ทุกตัวในคลัสเตอร์ถูกตั้งให้ถาม DNS ที่ `10.96.0.10`

ถามสมุดรายชื่อเองจาก Pod `client` (LAB 1)

```text
$ kubectl exec client -- nslookup web.default.svc.cluster.local
Server:		10.96.0.10              ← ถาม kube-dns
Address:	10.96.0.10:53

Name:	web.default.svc.cluster.local
Address: 10.96.169.141           ← ได้ ClusterIP ของ Service web
```

### ชื่อสั้น และชื่อเต็ม

ชื่อเต็มของ Service คือ `<ชื่อ Service>.<namespace>.svc.cluster.local`

- `web` = ชื่อ Service
- `default` = **namespace** (ห้องที่ object อยู่) ทุกอย่างที่เราสร้างมาตั้งแต่บทที่ 2 อยู่ห้อง `default`
- `svc.cluster.local` = ท้ายชื่อของ Service ทุกตัวในคลัสเตอร์นี้

Pod ที่อยู่ namespace เดียวกันเรียกแค่ `web` ก็พอ (LAB 1 เรียกทั้ง `http://web` และ `http://web.default.svc.cluster.local` ได้ทั้งคู่) ส่วน Pod ต่างห้องต้องเรียกชื่อยาวขึ้น เช่น `web.default`

> **ประโยคเดียวที่ต้องจำ:** ในแอป **ให้เรียกชื่อ Service** (`http://web`, `http://som-menu`) ไม่ใช่ Pod IP หรือ ClusterIP เพราะชื่อไม่เปลี่ยนแม้ลบแล้วสร้าง Service ใหม่ (หัวข้อ 10)

---

## 8. Service หา Pod จากป้าย

<p align="center">
  <img src="images/08-endpoints-follow-labels.png" alt="ลบ Pod ถอดป้าย scale 5 กระดานรายชื่อของพนักงานต้อนรับเปลี่ยนตามเอง" width="800">
</p>

พนักงานต้อนรับ **ไม่ได้จำชื่อกล่อง** แต่ดูป้าย เหมือนหัวหน้าลูกเรือที่นับ Pod จากป้ายใน [บทที่ 3 หัวข้อ 8](../../003_kubernetes_Replicaset/01_Theory/README.md#8-labels-replicaset-นับ-pod-จากป้าย) รายชื่อ (Endpoints) จึง **ตาม Pod เสมอ** ใน LAB 2 ลองเปลี่ยน Pod 3 แบบ

**1) ลบ Pod → ตัวใหม่เข้ารายชื่อเอง**

```text
Endpoints:  10.244.1.4:80,10.244.2.9:80,10.244.2.10:80      ← ก่อนลบ

$ kubectl delete pod web-65b66cc75b-mtg6r
$ kubectl get pods -o wide
web-65b66cc75b-fm44v   1/1     Running   0          6s    10.244.1.5    lab-worker2   ← ตัวใหม่ IP ใหม่

Endpoints:  10.244.2.9:80,10.244.2.10:80,10.244.1.5:80      ← หลังลบ: 1.4 ออก 1.5 เข้า
```

ReplicaSet สร้าง Pod ใหม่ (บทที่ 3) ส่วน Service เห็นป้าย `app=web` บน Pod ใหม่ จึงใส่ IP ใหม่ในรายชื่อให้ **เราไม่ต้องแก้ Service เลย**

**2) ถอดป้าย → หลุดจากรายชื่อ ทั้งที่ยังรันอยู่** (ตัดบางคอลัมน์ออก)

```text
$ kubectl label pod web-65b66cc75b-fm44v app-
pod/web-65b66cc75b-fm44v unlabeled

$ kubectl get pods -o wide --show-labels
NAME                   READY   STATUS    AGE   IP            LABELS
web-65b66cc75b-fm44v   1/1     Running   11s   10.244.1.5    pod-template-hash=65b66cc75b       ← ไม่มี app=web แล้ว
web-65b66cc75b-rxwr5   1/1     Running   5s    10.244.1.6    app=web,pod-template-hash=65b66cc75b   ← ReplicaSet สร้างมาเติม
...

Endpoints:  10.244.2.9:80,10.244.2.10:80,10.244.1.6:80      ← 1.5 หายไป 1.6 เข้ามา
```

- Pod `fm44v` ยัง `Running` แต่ **ไม่มี request ถูกส่งไปอีก** (`wget http://web` 4 ครั้งได้ `r9wlj`, `wmdll`, `r9wlj`, `wmdll`)
- เกิด 2 เรื่องพร้อมกันจากป้ายเดียว: ReplicaSet นับได้ 2 จึงสร้าง `rxwr5` มาเติม และ Service ตัด `fm44v` ออกจากรายชื่อ

**3) scale เป็น 5 → รายชื่อยาวขึ้นเอง**

```text
$ kubectl scale deployment web --replicas=5
Endpoints:  10.244.2.9:80,10.244.2.10:80,10.244.1.6:80 + 2 more...
```

`+ 2 more...` = มีอีก 2 ตัว (`describe` ย่อให้เมื่อยาว) ดูครบได้ด้วย `kubectl get endpointslices`

> **เคล็ดลับ:** ถอดป้ายใช้ **แยก Pod ที่มีปัญหาออกจากหน้าร้าน** ได้ ลูกค้าไม่ถูกส่งไปตัวนั้นแล้ว แต่เรายังเข้าไป `exec` / `logs` ตรวจได้ ตรวจเสร็จแล้วลบเอง (LAB 2 ลบ `fm44v` ทิ้งในขั้นที่ 4)

---

## 9. กับดัก: selector พิมพ์ผิด แล้ว Endpoints ว่าง

<p align="center">
  <img src="images/09-selector-typo-empty.png" alt="selector app=wbe ไม่ตรงป้าย app=web กระดาน Endpoints ว่าง ลูกค้าถูกปฏิเสธ" width="800">
</p>

ไฟล์ `02_LAB/labs/lab02-selector/web-svc-typo.yaml` พิมพ์ป้ายสลับตัวอักษร

```yaml
metadata:
  name: web-typo
spec:
  selector:
    app: wbe                 # ← พิมพ์ผิด (ที่ถูกคือ web) ไม่มี Pod ไหนติดป้ายนี้
```

ผลจริงใน LAB 2: apply ผ่าน ได้ ClusterIP ด้วย ดูเหมือนปกติทุกอย่าง

```text
$ kubectl apply -f labs/lab02-selector/web-svc-typo.yaml
service/web-typo created

$ kubectl get svc
NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
web          ClusterIP   10.96.62.215   <none>        80/TCP    23s
web-typo     ClusterIP   10.96.62.39    <none>        80/TCP    0s     ← ไม่มีอะไรบอกว่าผิด
```

แต่พอดูรายชื่อ และลองเรียก

```text
$ kubectl describe svc web-typo
Selector:                 app=wbe
Endpoints:                                    ← ว่าง!

$ kubectl exec client -- wget -qO- http://web-typo
wget: can't connect to remote host (10.96.62.39): Connection refused
command terminated with exit code 1
```

- ชื่อ `web-typo` แปลเป็น IP ได้ (DNS ทำงาน) แต่ **ไม่มี Pod ในรายชื่อ** จึงไม่มีใครรับ ได้ `Connection refused`
- Pod `web` 5 ตัวรันปกติอยู่ข้าง ๆ ตลอด ปัญหาไม่ได้อยู่ที่ Pod

### ตรวจ 3 ขั้น เมื่อเรียก Service ไม่ได้

1. **`kubectl describe svc <ชื่อ>`** ดูบรรทัด `Endpoints:` ถ้า **ว่าง** = Service หา Pod ไม่เจอ ไปขั้น 2
2. **`kubectl get pods --show-labels`** เทียบป้ายของ Pod กับบรรทัด `Selector:` ทีละตัวอักษร (`wbe` ≠ `web`) หรือ Pod มีครบแต่ `READY 0/1` (ยังไม่พร้อม หัวข้อ 12)
3. ถ้า Endpoints **มีครบ** แต่ยังต่อไม่ติด → เทียบ `TargetPort` กับ `containerPort` ของ Pod (LAB 2 ขั้นที่ 6 ตั้ง `targetPort: 8080` ให้ nginx ที่ฟัง 80 ได้ Endpoints ครบ 5 ตัวแต่ลงท้าย `:8080` และได้ `Connection refused` เหมือน selector ผิด)

> **⚠️ กับดัก:** Service ที่ selector ผิด **ไม่มี error ตอน apply ไม่มี Events ไม่มี STATUS สีแดง** สิ่งเดียวที่บอกคือ `Endpoints:` ว่าง ให้ดูบรรทัดนี้เป็นอย่างแรกทุกครั้ง

---

## 10. ClusterIP: ที่อยู่ภายในคลัสเตอร์

<p align="center">
  <img src="images/10-clusterip-inside.png" alt="ClusterIP ของ Service web ใน LAB 1 คือ 10.96.169.141 ลบแล้วสร้างใหม่ใน LAB 2 ได้ 10.96.62.215 และคงที่ระหว่างลบ Pod ถอด label scale ใช้ได้เฉพาะในคลัสเตอร์" width="800">
</p>

**ClusterIP** คือแบบเริ่มต้นของ Service ได้ IP 1 อัน (ในคลัสเตอร์ kind อยู่ช่วง `10.96.x.x` ส่วน Pod อยู่ช่วง `10.244.x.x`)

**คงที่ตลอดอายุ Service** ใน LAB 2 ลบ Pod ถอดป้าย scale เป็น 5 แต่ `describe svc web` ขึ้น `IP: 10.96.62.215` ทุกครั้ง มีแต่บรรทัด `Endpoints:` ที่เปลี่ยน

**แต่ลบ Service แล้วสร้างใหม่ = ได้ IP ใหม่**

- LAB 1 Service `web` ได้ `10.96.169.141`
- ตอนท้าย LAB 1 ลบทิ้ง แล้ว LAB 2 apply ไฟล์เดิมซ้ำ ได้ `10.96.62.215`
- ชื่อ `web` เหมือนเดิม → แอปที่เรียกด้วยชื่อ (หัวข้อ 7) ไม่ต้องแก้อะไร

**ใช้ได้เฉพาะในคลัสเตอร์** ClusterIP เป็นที่อยู่ภายในคลัสเตอร์ Pod ทุกตัวเรียกได้ แต่ browser บนเครื่องเรา **เรียกตรงไม่ได้** ในอุปมาคือบูธอยู่ในรั้วท่าเรือ คนบนถนนเดินเข้าไปไม่ถึง LAB 1–2 จึงต้องใช้ Pod `client` เป็นลูกค้าในคลัสเตอร์

ไฟล์ `labs/lab01-clusterip/client-pod.yaml` เป็น Pod เดี่ยว (บทที่ 2) ที่แค่นอนรอให้เรา `exec` เข้าไป

```yaml
spec:
  containers:
    - name: busybox
      image: busybox:1.37
      command: ["sleep", "3600"]   # นอนรอ 1 ชั่วโมง (มี wget และ nslookup ให้ใช้)
```

> **เคล็ดลับ:** ClusterIP เหมาะกับของที่ **ใช้กันเองในคลัสเตอร์** เช่น ฐานข้อมูลที่หน้าเว็บเรียก คนนอกไม่ควรเข้าถึงอยู่แล้ว ส่วนหน้าร้านที่ลูกค้าต้องเปิดจาก browser ใช้ NodePort (หัวข้อ 11)

---

## 11. NodePort: ประตูบนทุก Node

<p align="center">
  <img src="images/11-nodeport-gate-every-ship.png" alt="ประตู 30080 บนหอบังคับการและเรือทุกลำ ลูกค้าจากถนนเข้าได้ทุกประตู" width="800">
</p>

**NodePort** = Service ที่ได้ **ClusterIP ทุกอย่างเหมือนเดิม** แล้วเปิด **port เดียวกันบนทุก Node** เพิ่มให้คนนอกคลัสเตอร์เข้าได้ ไฟล์ `02_LAB/labs/lab03-nodeport/web-svc-nodeport.yaml` ต่างจาก `web-svc.yaml` แค่ 2 บรรทัด

```yaml
spec:
  type: NodePort             # ← ใหม่: ได้ทั้ง ClusterIP และ port บนทุก Node
  selector:
    app: web
  ports:
    - port: 80               # port ของ Service ในคลัสเตอร์
      targetPort: 80         # port ของ container
      nodePort: 30080        # ← ใหม่: port บนทุก Node (ต้องอยู่ในช่วง 30000–32767) แล็บนี้ map ออกมาถึงเครื่องเราแล้ว
```

- `nodePort` ต้องอยู่ในช่วง **30000–32767** ถ้าไม่เขียน Kubernetes สุ่มเลขในช่วงนี้ให้
- LAB นี้ **เขียนเลขเอง** เพราะ k8s-lab ส่งออกมาถึงเครื่องเราเฉพาะ `30080`–`30082`

ผลจริงใน LAB 3

```text
$ kubectl get svc
NAME           TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-nodeport   NodePort    10.96.231.50   <none>        80:30080/TCP   5s     ← มี ClusterIP ด้วย

$ curl http://localhost:30080
Hello from Pod web-65b66cc75b-xrcb5
$ curl http://localhost:30080
Hello from Pod web-65b66cc75b-z6qjn
```

### ประตูมีบนเรือทุกลำ

ลองเรียกตรงที่ IP ของ Node แต่ละตัว (`INTERNAL-IP` จาก `kubectl get nodes -o wide`)

```text
lab-worker    172.19.0.2        lab-worker2   172.19.0.3

$ curl http://172.19.0.2:30080      ← nodePort ของ lab-worker
Hello from Pod web-65b66cc75b-xrcb5 ← Pod นี้อยู่บน lab-worker2

$ curl http://172.19.0.3:30080      ← nodePort ของ lab-worker2
Hello from Pod web-65b66cc75b-z6qjn ← Pod นี้อยู่บน lab-worker
```

เข้าประตูของเรือลำไหนก็ได้ kube-proxy บนเรือลำนั้นส่งต่อไป Pod ในรายชื่อ **ซึ่งอาจอยู่คนละลำ** (หัวข้อ 5) Node ที่ไม่มี Pod ของเราเลยก็เปิดประตูนี้เหมือนกัน

### ทำไม LAB 0 ต้องเพิ่ม `-p 30080-30082:30080-30082`

คลัสเตอร์ kind ทั้งก้อน (3 Node) อยู่ **ข้างใน container `k8s-lab`** อีกที ลูกค้าจาก browser จึงต้องผ่าน 2 ชั้น

1. `-p 30080-30082:30080-30082` ตอน `docker run` = เปิดทางจาก **เครื่องเรา** เข้า **container k8s-lab**
2. คลัสเตอร์ kind ใน k8s-lab ตั้งไว้แล้วให้ port ชุดนี้ส่งต่อเข้า **nodePort ของ Node** (`k8s-up` บอกไว้ว่า `NodePort ที่ map ออก host: 30080 30081 30082`)

ขาดชั้นแรก `curl localhost:30080` ใน SSH ของ k8s-lab ยังได้ แต่ browser บนเครื่องเราเปิดไม่ได้ และถ้าตั้ง `nodePort` เป็นเลขอื่นนอก 30080–30082 ก็เข้าได้แค่ด้วย IP ของ Node จากใน k8s-lab

> **เคล็ดลับ:** เทียบ ClusterIP กับ NodePort และแบบอื่นได้จากตารางและภาพสถาปัตยกรรมใน [หัวข้อ 3](#3-service-มีกี่แบบ-และแต่ละแบบต่างกันอย่างไร) ส่วนบนคลาวด์จริงจะใช้ `type: LoadBalancer` แทน (หัวข้อ 3.3) ซึ่งคลัสเตอร์ kind บนเครื่องเราใช้ไม่ได้ บทนี้จึงใช้ NodePort

---

## 12. Service ระหว่างเปลี่ยนรุ่น: readinessProbe และ rolling update

<p align="center">
  <img src="images/12-service-readiness-rolling.png" alt="กล่องใหม่ 0/1 ไม่อยู่ในกระดาน Endpoints กล่องที่กำลังปิดรอ 5 วินาทีหลัง SIGTERM" width="800">
</p>

ใน LAB 4 ร้านน้องส้มเปิดด้วย Service NodePort `som-menu` แล้วเปลี่ยนรุ่นด้วย Deployment แบบบทที่ 4 คราวนี้ **ไม่ต้องรัน port-forward ใหม่เลย**

### refresh แล้วเห็นหลายสาขา

```text
$ curl http://localhost:30080/api/info
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
$ curl http://localhost:30080/api/info
{"pod":"som-menu-5f5c95db8f-jfjlg","version":"1.0"}
$ curl http://localhost:30080/api/info
{"pod":"som-menu-5f5c95db8f-zq7lg","version":"1.0"}
$ curl http://localhost:30080/api/info
{"pod":"som-menu-5f5c95db8f-gqsd2","version":"1.0"}
```

ใน browser เปิด `http://localhost:30080` ครั้งแรกได้ `som-menu-5f5c95db8f-gqsd2` ครั้งที่ 2–4 ได้ `som-menu-5f5c95db8f-jfjlg` ตรงกับ `kubectl logs` ของแต่ละ Pod (`gqsd2` เสิร์ฟ 1 ครั้ง, `jfjlg` เสิร์ฟ 3 ครั้ง)

Service เลือก Pod **ต่อการเชื่อมต่อ 1 ครั้ง** ไม่ใช่ต่อการกด refresh ปกติ browser ใช้การเชื่อมต่อเดิมซ้ำ (ได้สาขาเดิมตลอด) แอปร้านน้องส้มจึงตอบหน้าร้านพร้อม `connection: close` ให้ปิดการเชื่อมต่อทุกครั้ง refresh จึงเป็นการเชื่อมต่อใหม่ที่ Service เลือกสาขาใหม่ได้

### Pod ที่ยัง 0/1 ไม่ได้รับลูกค้า

หลัง apply `som-menu-deploy-v2.yaml` 3 วินาที มี Pod รุ่น 2.0 แล้ว 1 ตัว แต่ยังไม่ผ่าน readinessProbe (`/api/health`) (ย่อป้าย `pod-template-hash` เป็น `...`)

```text
$ kubectl get pods --show-labels
NAME                        READY   STATUS    RESTARTS   AGE   LABELS
som-menu-5f5c95db8f-gqsd2   1/1     Running   0          46s   app=som-menu,...,version=1.0
som-menu-5f5c95db8f-jfjlg   1/1     Running   0          46s   app=som-menu,...,version=1.0
som-menu-5f5c95db8f-zq7lg   1/1     Running   0          46s   app=som-menu,...,version=1.0
som-menu-6bf6c9f6c5-687px   0/1     Running   0          3s    app=som-menu,...,version=2.0   ← ป้ายตรง แต่ยังไม่พร้อม
```

ช่วงนั้น curl 6 ครั้ง ได้ `version: 1.0` **ทั้ง 6 ครั้ง** ไม่มี request ถูกส่งไป `687px` เพราะ endpointslice-controller ใส่ในรายชื่อเฉพาะ Pod ที่ **ป้ายตรง และ READY** (readinessProbe จากบทที่ 2 หัวข้อ 10 ทำงานคู่กับ Service ตรงนี้)

### เปลี่ยนรุ่นเสร็จ แค่ refresh

```text
$ kubectl describe svc som-menu
IP:                       10.96.187.5                                          ← ที่อยู่เดิม
Endpoints:                10.244.1.10:3000,10.244.2.16:3000,10.244.2.17:3000   ← Pod รุ่น 2.0 ทั้ง 3 ตัว

$ curl http://localhost:30080/api/info
{"pod":"som-menu-6bf6c9f6c5-kpgxt","version":"2.0"}
```

browser ไม่ได้ทำอะไรเพิ่ม แค่ refresh ก็เห็นหน้าร้านรุ่น 2.0 สีเขียวอมฟ้า ต่างจากบทที่ 4 ที่ต้องรัน port-forward ใหม่หลังเจอ `lost connection to pod`

### rollback แล้วเห็น v1 / v2 ปนกัน

ระหว่าง `kubectl rollout undo` ยิง curl 6 ครั้ง ได้ `1.0` 3 ครั้ง (`jqbz6`, `5d9r4`) และ `2.0` 3 ครั้ง (`b58wj`) เพราะ selector ของ Service คือ `app=som-menu` อย่างเดียว ไม่สนป้าย `version` **ทุกสาขาที่พร้อมได้ลูกค้าหมด ไม่ว่ารุ่นไหน** พอ rollout เสร็จก็เหลือ `1.0` ล้วน

### Pod ที่กำลังปิด ต้องรอให้ Service ถอดชื่อก่อน

ตอน Pod ถูกลบ (เช่น Pod เก่าระหว่าง rolling update) เกิด 2 เรื่อง **พร้อมกัน** ไม่ได้รอกัน

- kubelet ส่งสัญญาณ **SIGTERM** บอกแอปใน Pod ว่า "ปิดร้านได้แล้ว" (STATUS เป็น `Terminating`)
- endpointslice-controller ถอด Pod ออกจากรายชื่อ แล้ว kube-proxy บนทุก Node ค่อยปรับรางตาม **ซึ่งใช้เวลาอีกนิด**

ถ้าแอปปิดทันทีที่ได้ SIGTERM ลูกค้าที่ยังถูกส่งมาตามรางเก่าในช่วงนั้นจะเจอประตูปิด แอปร้านน้องส้ม (`som-menu/app/server.js`) จึงรอก่อน

```js
// รอ 5 วินาทีให้ Service ถอดสาขานี้ออกจากรายชื่อ (Endpoints) ก่อน ระหว่างนั้นยังเสิร์ฟลูกค้าที่หลงมาได้ แล้วค่อยปิดร้าน
process.on("SIGTERM", () => {
  console.log(`ปิดสาขา ${POD_NAME} (รอ 5 วินาทีให้ Service หยุดส่งลูกค้ามาก่อน)`);
  setTimeout(() => {
    server.close(() => process.exit(0));
    ...
  }, 5000);
});
```

> **⚠️ กับดัก:** ตอนทดลองก่อนแก้แอป เคยเจอ `Connection reset by peer` 1 ครั้งตอน Pod เก่าปิด หลังให้แอปรอ 5 วินาทีหลัง SIGTERM ยิง curl ระหว่าง rolling update และ rollback รวม 941 ครั้ง ไม่ล้มเลย **"ร้านไม่ปิด" ต้องมีทั้ง readinessProbe ตอนเปิด และรอสักครู่ตอนปิด** (Kubernetes ให้เวลาปิดตัวได้ 30 วินาทีโดยค่าเริ่มต้น 5 วินาทีจึงพอดี)

---

## 13. อ่าน YAML ร้านน้องส้มทั้งไฟล์

<p align="center">
  <img src="images/13-som-menu-svc-yaml-skeleton.png" alt="โครงของ som-menu-svc.yaml และ selector ที่จับป้ายในแม่พิมพ์ของ som-menu-deploy.yaml" width="800">
</p>

LAB 4 ใช้ 2 ไฟล์คู่กัน: `som-menu-deploy.yaml` (สร้างสาขา บทที่ 4) และ `som-menu-svc.yaml` (ที่อยู่ของร้าน) ไฟล์ Service ยาวแค่ 14 บรรทัด ถ้าพับเหลือแค่โครง

```yaml
apiVersion: v1
kind: Service
metadata:
  name: som-menu        # ชื่อร้าน = ชื่อที่ใช้เรียกในคลัสเตอร์ http://som-menu
spec:
  type: NodePort        # เปิดประตูบนทุก Node
  selector:             # ส่งลูกค้าไปสาขาที่ติดป้ายไหน
  ports:                # รับที่ไหน ส่งต่อไปไหน
```

ไฟล์เต็ม `02_LAB/som-menu/k8s/som-menu-svc.yaml`

```yaml
# LAB 4: ที่อยู่เดียวของร้านน้องส้ม — Service แบบ NodePort กระจายลูกค้าไปทุกสาขาที่พร้อม
apiVersion: v1                 # ← หัวข้อ 6: Service อยู่กลุ่มหลัก
kind: Service
metadata:
  name: som-menu               # ← หัวข้อ 7: ชื่อใน DNS = som-menu.default.svc.cluster.local
spec:
  type: NodePort               # ← หัวข้อ 3.2, 11
  selector:
    app: som-menu            # ทุกสาขาที่ติดป้ายนี้ ไม่สนว่า version 1.0 หรือ 2.0
  ports:
    - port: 80               # ในคลัสเตอร์เรียก http://som-menu (port 80)
      targetPort: 3000       # หน้าร้าน Node.js ฟัง port 3000
      nodePort: 30080        # นอกคลัสเตอร์เปิด http://localhost:30080
```

(comment ที่มี `←` เพิ่มเพื่ออ่านคู่บทนี้ ในไฟล์จริงไม่มี)

### selector ของ Service จับป้ายในแม่พิมพ์ของ Deployment

ส่วนที่เกี่ยวกันใน `som-menu-deploy.yaml`

```yaml
  template:                      # แม่พิมพ์ของทุกสาขา
    metadata:
      labels:
        app: som-menu            # ← Service ใช้ป้ายนี้ (selector: app: som-menu)
        version: "1.0"           # ← Service ไม่ได้ใช้ จึงรับทั้ง 1.0 และ 2.0
    spec:
      containers:
        - name: web
          image: som-menu:1.0
          ...
          ports:
            - containerPort: 3000      # ← = targetPort ของ Service (หัวข้อ 4)
          readinessProbe:              # ← หัวข้อ 12: ผ่านแล้วจึงเข้ารายชื่อของ Service
            httpGet:
              path: /api/health
              port: 3000
            periodSeconds: 5
```

- 3 จุดที่ต้องตรงกันระหว่าง 2 ไฟล์: **ป้าย** (`app: som-menu`), **port** (`targetPort` = `containerPort` = 3000), และ readinessProbe ที่ตัดสินว่าสาขาไหนพร้อม
- ถ้าใส่ `version: "1.0"` ลงใน selector ของ Service ด้วย พอเปลี่ยนเป็นรุ่น 2.0 เสร็จ จะไม่มี Pod ตรงเลย กลายเป็น **Endpoints ว่าง** แบบหัวข้อ 9 ทั้งร้าน
- `som-menu-deploy-v2.yaml` ต่างแค่ 3 บรรทัด (บทที่ 4) และหัวไฟล์เขียนไว้ว่า **"Service ตัวเดิม ไม่ต้องแก้"**

แปลทั้งไฟล์เป็นประโยคเดียว: **"ขอ Service ชื่อ `som-menu` แบบ NodePort เปิดประตู 30080 บนทุก Node และ port 80 ในคลัสเตอร์ แล้วส่งลูกค้าต่อไป port 3000 ของทุกสาขาที่ติดป้าย `app=som-menu` และพร้อม ไม่ว่าจะเป็นรุ่นไหน"**

---

## 14. ปูทางบทถัดไป

<p align="center">
  <img src="images/14-next-chapter-preview.png" alt="ตัวอย่างบทหน้า มองผ่านกล้องส่องทางไกล" width="800">
</p>

ร้านมีที่อยู่เดียวแล้ว ลูกค้าเข้าได้ทุกสาขา แต่ใน LAB ยังเห็นปัญหาที่ Service ช่วยไม่ได้

- **ค่าตั้งค่าเขียนอยู่ใน YAML ของ Deployment** เช่น `SHOP_NAME: "ร้านอาหารแมวน้องส้ม"` แก้ชื่อร้านทีต้องแก้ไฟล์ Deployment แล้วเปลี่ยนรุ่นทุกสาขา
- **ค่าบางอย่างฝังใน image ตอน build** เช่น `APP_VERSION` ที่ส่งด้วย `--build-arg APP_VERSION=2.0` ใน LAB 4 จะเปลี่ยนค่าต้อง build image ใหม่
- **รหัสผ่านฐานข้อมูลยังเขียนเปิดอยู่ใน YAML** ตั้งแต่บทที่ 2 ใครเปิดไฟล์ก็เห็น
- → **ConfigMap** (ค่าตั้งค่า) และ **Secret** (รหัสผ่าน) แยกค่าพวกนี้ออกจาก YAML ของ Pod และ image **(บทที่ 6)**
- ข้อมูลใน Pod ยังหายเมื่อได้ Pod ใหม่ (rolling update สร้าง Pod ใหม่ทุกตัว) → **PersistentVolume (บทที่ 7)**

---

## 15. สรุปและคำถามทบทวน

<p align="center">
  <img src="images/15-chapter-summary.png" alt="สรุปบทที่ 5" width="800">
</p>

### สรุป

1. **Service** ให้ที่อยู่เดียวที่คงที่ (ชื่อ + ClusterIP) กับกลุ่ม Pod ที่ติดป้ายเดียวกัน และกระจายลูกค้าไปทุก Pod ที่พร้อม
2. Service มี **3 แบบ** ซ้อนกันเป็นชั้น: **ClusterIP** (ใช้ในคลัสเตอร์) ⊂ **NodePort** (+ ประตูบนทุก Node) ⊂ **LoadBalancer** (+ เครื่องกระจายโหลดของคลาวด์) บทนี้ใช้ 2 แบบแรก
3. ที่อยู่ 3 แบบ คู่กับ port: Node IP + `nodePort` (คนนอก) → ClusterIP + `port` (Pod ในคลัสเตอร์) → Pod IP + `targetPort` (= `containerPort`) และ `PORT(S)` เขียนเป็น `port:nodePort`
4. ทำงาน 3 ช่วง: `selector` → endpointslice-controller จด **Endpoints** → **kube-proxy บนทุก Node** วางกฎส่งต่อ → Pod
5. YAML ของ Service ใช้ `apiVersion: v1` มี `metadata` / `spec` ชุดเดียว **ไม่มี template ไม่สร้าง Pod** และ selector ไม่มี `matchLabels`
6. เรียกด้วยชื่อผ่าน DNS (`kube-dns` ที่ `10.96.0.10`) ชื่อสั้น `web` หรือชื่อเต็ม `web.default.svc.cluster.local`
7. Endpoints **ตามป้ายเสมอ**: ลบ Pod, ถอดป้าย, scale แล้วรายชื่อเปลี่ยนเอง ไม่ต้องแก้ Service
8. selector พิมพ์ผิด apply ผ่านแต่ **Endpoints ว่าง** → `Connection refused` ตรวจ `describe svc` → `--show-labels` → targetPort
9. **ClusterIP** คงที่ตลอดอายุ Service (ลบแล้วสร้างใหม่ได้ IP ใหม่ จึงเรียกด้วยชื่อ) ส่วน **NodePort** เปิด port 30000–32767 บนทุก Node (k8s-lab ส่งออกเฉพาะ 30080–30082)
10. Pod ที่ READY `0/1` ไม่อยู่ใน Endpoints, เปลี่ยนรุ่นแล้วแค่ refresh, Pod ที่กำลังปิดควรรอให้ถอดชื่อก่อน → บทหน้า **ConfigMap + Secret**

### คำถามทบทวน

**1. อ่าน YAML นี้แล้วตอบ: Pod อื่นในคลัสเตอร์เรียกด้วย URL อะไร คนนอกคลัสเตอร์เข้าที่ port ไหน และแอปใน Pod ต้องฟัง port อะไร**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cat-api
spec:
  type: NodePort
  selector:
    app: cat-api
  ports:
    - port: 8080
      targetPort: 5000
      nodePort: 30081
```

<details>
<summary>แนวคำตอบ</summary>

ในคลัสเตอร์เรียก `http://cat-api:8080` (port ของ Service) คนนอกเข้า `<IP ของ Node ไหนก็ได้>:30081` (บน k8s-lab คือ `http://localhost:30081`) แอปใน Pod ต้องฟัง port 5000 (targetPort = containerPort)
</details>

**2. YAML ต่อไปนี้ผิดกี่จุด อะไรบ้าง**

```text
apiVersion: apps/v1
kind: service
metadata:
  name: som-menu
spec:
  type: NodePort
  selector:
    matchLabels:
      app: som-menu
  ports:
    - port: 80
      targetPort: 3000
      nodePort: 8080
```

<details>
<summary>แนวคำตอบ</summary>

1. `apiVersion: apps/v1` ต้องเป็น `v1`
2. `kind: service` ต้องเป็น `Service`
3. selector ของ Service ไม่มี `matchLabels` ต้องเขียน `app: som-menu` ใต้ `selector:` ตรง ๆ
4. `nodePort: 8080` อยู่นอกช่วง 30000–32767 (และใน k8s-lab ควรใช้ 30080–30082)
</details>

**3. เพื่อนบอกว่า "Pod รันครบ 3 ตัว แต่เรียก `http://shop` แล้วได้ `Connection refused`" แล้วส่งผลนี้มา สาเหตุน่าจะเป็นอะไร ตรวจอะไรต่อ**

```text
$ kubectl describe svc shop
Selector:                 app=shpo
TargetPort:               80/TCP
Endpoints:
```

<details>
<summary>แนวคำตอบ</summary>

`Endpoints:` ว่าง = Service หา Pod ไม่เจอ และ selector `app=shpo` น่าจะพิมพ์ผิด (เหมือน `app: wbe` ใน LAB 2) ให้ `kubectl get pods --show-labels` เทียบป้ายจริงของ Pod แล้วแก้ selector ในไฟล์ แล้ว apply ใหม่
</details>

**4. `kubectl get svc` แสดงบรรทัดนี้ Service เป็นแบบไหน ตัวเลข 80 กับ 30080 คืออะไร และ targetPort ดูได้จากไหน**

```text
NAME       TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
som-menu   NodePort   10.96.187.5   <none>        80:30080/TCP   11s
```

<details>
<summary>แนวคำตอบ</summary>

แบบ NodePort (มี ClusterIP `10.96.187.5` ด้วย) `80` = port ของ Service ใช้ในคลัสเตอร์ `30080` = nodePort เปิดบนทุก Node targetPort ไม่อยู่ในคอลัมน์นี้ ดูจาก `kubectl describe svc som-menu` (`TargetPort: 3000/TCP` และ Endpoints ลงท้าย `:3000`)
</details>

**5. ใน LAB 2 ถอดป้าย `app` ออกจาก `web-65b66cc75b-fm44v` แล้ว Pod นั้นยัง `Running` แต่ `wget http://web` 4 ครั้งไม่เคยได้คำตอบจากมันเลย เพราะอะไร และทำไมมี Pod `rxwr5` โผล่มา**

<details>
<summary>แนวคำตอบ</summary>

Service เลือก Pod จากป้าย `app=web` พอถอดป้าย `fm44v` จึงหลุดจาก Endpoints ไม่มี request ถูกส่งไป ส่วน ReplicaSet ก็นับจากป้ายเหมือนกัน นับได้ 2 จึงสร้าง `rxwr5` มาเติมให้ครบ 3 แล้ว Service ก็ใส่ `rxwr5` ในรายชื่อเอง
</details>

**6. ใน LAB 4 หลัง apply รุ่น 2.0 มี Pod `som-menu-6bf6c9f6c5-687px   0/1   Running` ติดป้าย `app=som-menu` ตรงกับ selector แต่ curl 6 ครั้งได้รุ่น 1.0 ทั้งหมด เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

Pod ใหม่ยังไม่ผ่าน readinessProbe (`/api/health`) READY จึงเป็น `0/1` และ Service ใส่ในรายชื่อเฉพาะ Pod ที่ป้ายตรง **และพร้อม** ลูกค้าจึงถูกส่งไปแค่ Pod รุ่น 1.0 ที่พร้อมอยู่ 3 ตัว
</details>

**7. บทที่ 4 เปลี่ยนรุ่นแล้ว port-forward ขึ้น `lost connection to pod` ต้องรันใหม่ แต่ LAB 4 บทนี้แค่ refresh browser ก็เห็นรุ่น 2.0 ต่างกันตรงไหน**

<details>
<summary>แนวคำตอบ</summary>

port-forward ผูกท่อกับ Pod ตัวเดียว Pod ถูกลบท่อก็ขาด ส่วน Service ผูกกับ **ป้าย** ที่อยู่ `localhost:30080` (nodePort) ไม่เปลี่ยน Endpoints เปลี่ยนเป็น Pod รุ่นใหม่เอง refresh ใหม่ก็ถูกส่งไป Pod รุ่น 2.0
</details>

**8. ทำไมแอปร้านน้องส้มรอ 5 วินาทีหลังได้ SIGTERM แทนที่จะปิดทันที**

<details>
<summary>แนวคำตอบ</summary>

ตอนลบ Pod การส่ง SIGTERM กับการถอด Pod ออกจาก Endpoints เกิดพร้อมกัน และ kube-proxy บนทุก Node ต้องใช้เวลาปรับรางอีกนิด ถ้าปิดทันที ลูกค้าที่ยังถูกส่งมาช่วงนั้นจะต่อไม่ติด (เคยเจอ `Connection reset by peer`) รอ 5 วินาทีให้ถอดชื่อเสร็จก่อน แล้วค่อยปิด
</details>

**9. เลือกแบบของ Service ให้แต่ละงาน: (ก) ฐานข้อมูลที่หน้าเว็บในคลัสเตอร์เรียกใช้ คนนอกไม่ควรเข้าถึง (ข) เปิดหน้าร้านจาก browser บนเครื่องเรา ในคลัสเตอร์ kind (ค) เปิดเว็บจริงบนคลาวด์ให้ลูกค้าจำที่อยู่เดียว**

<details>
<summary>แนวคำตอบ</summary>

(ก) **ClusterIP** ใช้ได้เฉพาะในคลัสเตอร์ (ข) **NodePort** เปิดประตู `30080` บนทุก Node แบบ LAB 3–4 (ค) **LoadBalancer** คลาวด์ตั้งเครื่องกระจายโหลดให้ ได้ `EXTERNAL-IP` ที่เดียว
</details>

**10. ถ้าแก้ `som-menu-svc.yaml` ให้ `targetPort: 80` (แต่แอปฟัง 3000) `describe svc` จะเห็น Endpoints ไหม แล้วเรียกได้ไหม**

<details>
<summary>แนวคำตอบ</summary>

เห็น Endpoints ครบ 3 ตัว (ป้ายยังตรง และ Pod พร้อม) แต่ลงท้ายเป็น `:80` ซึ่งไม่มีแอปฟังอยู่ จึงเรียกไม่ติด เป็นขั้นที่ 3 ของการตรวจในหัวข้อ 9: Endpoints มีแต่ต่อไม่ได้ → เทียบ `targetPort` กับ `containerPort`
</details>

---

## เอกสารอ้างอิง

- Kubernetes Docs: [Service](https://kubernetes.io/docs/concepts/services-networking/service/) · [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) · [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Connecting Applications with Services](https://kubernetes.io/docs/tutorials/services/connect-applications-service/) · [Pod Lifecycle: Termination of Pods](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)

> ภาพการ์ตูนในโฟลเดอร์ [`images/`](images/) สร้างด้วย AI เพื่อการเรียนการสอน (prompt อยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md)) ส่วนภาพในหัวข้อ 2, 3, 4, 6, 7 และ 10 วาดเป็น SVG จากค่าจริงใน LAB ผลลัพธ์คำสั่งมาจาก LAB จริงบน kind v0.33.0 / Kubernetes v1.37.0 (ทดลองใหม่ทั้งบท 19 ต.ค. 2569) ชื่อ Pod, ClusterIP, Pod IP, Node IP และลำดับที่ Service เลือก Pod ในเครื่องผู้เรียนจะต่างกัน
