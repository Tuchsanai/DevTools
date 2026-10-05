# บทที่ 6: Service — ประภาคารที่ชื่อและที่อยู่ไม่เคยเปลี่ยน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Service — ClusterIP, selector และ EndpointSlice, Service CIDR, port/targetPort/nodePort และ named port, NodePort, LoadBalancer, ExternalName, headless Service, DNS และ env var ของ Service, kube-proxy, การกระจายโหลดและ sessionAffinity, readinessProbe กับ endpoints, การ debug Service และ NetworkPolicy กับ Service
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

{{TOPFIG}}

## บทนี้เรียนอะไร

บทที่ 5 ร้านอาหารแมวน้องส้มมี **หัวหน้ากะ (ReplicaSet)** ดูแลให้ครบ 3 บูธเสมอ แต่ลูกค้ายังหาร้านไม่เจอ บูธที่เกิดใหม่ได้ชื่อและ IP ใหม่ทุกครั้ง ต้อง `port-forward` ทีละบูธจนสายหลุด และแต่ละบูธมีฐานข้อมูลของตัวเองจนออเดอร์ไม่ตรงกัน บทนี้แก้ปัญหา **"ที่อยู่"** ด้วย **Service** หรือ **ประภาคารบนท่าเรือ** ที่มีชื่อและ ClusterIP คงที่ มี **คลิปบอร์ดรายชื่อบูธ (EndpointSlice)** ที่อัปเดตเองตาม label และไฟเขียว (readinessProbe) มี **ป้ายบอกทางบนเรือทุกลำ (kube-proxy)** และเปิด **ประตูหมายเลข 30080 (NodePort)** ให้ลูกค้าเปิดร้านจาก browser ที่ `http://localhost:30080` ได้ตรง ๆ เป็นครั้งแรก ปิดท้ายด้วย **การแยกหน้าร้าน (web) ออกจากครัวกลาง (db) ครั้งแรก** ออเดอร์จากทุกบูธจึงรวมที่เดียว แต่เมื่อน้องส้มอยากเปลี่ยนร้านเป็นรุ่น 1.3 ก็ต้องรื้อบูธเองจนร้านสะดุด ซึ่งเป็นปัญหาที่บทที่ 7 จะแก้

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ทำไมต้องมี Service, ClusterIP ที่เป็นที่อยู่เสมือน, โครง manifest และ `kubectl expose`, selector → EndpointSlice (conditions, EndpointSlice controller, v1 Endpoints ที่เลิกใช้, Service ไม่มี selector), Service CIDR, port/targetPort/nodePort และ named port, NodePort และเส้นทางจาก `localhost:30080` ถึง Pod, LoadBalancer, ExternalName, headless, DNS (search domain, `ndots`) และ env var, kube-proxy และโหมดของมัน, การกระจายแบบสุ่ม keep-alive และ sessionAffinity, readinessProbe กับ endpoints, บันได debug Service, NetworkPolicy ที่ตรวจหลัง DNAT และข้อจำกัดที่ส่งต่อบทที่ 7 (36 ภาพประกอบ + คำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–10 จากง่ายไปยาก: เตรียมคลัสเตอร์และตรวจพอร์ต 30080–30082 → ปัญหาก่อนมี Service → ClusterIP และ EndpointSlice → พอร์ตและชื่อพอร์ต → DNS และ env var → การกระจายและ sessionAffinity → readiness → debug Service → NodePort/LoadBalancer/keep-alive → ข้าม namespace, headless, ExternalName และ NetworkPolicy → **LAB สุดท้าย: ร้านน้องส้มแยก web กับ db ครั้งแรก** (พร้อมภาพหน้าจอจริง) และ Troubleshooting, Checklist, ตารางเก็บกวาด | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีหัวข้อ 1–4 ก่อน** (ปัญหา, ClusterIP, EndpointSlice, Service CIDR) แล้วเริ่ม LAB 0–2 ได้
2. ก่อน LAB 3 อ่านหัวข้อ 5 (พอร์ต) ก่อน LAB 4 อ่านหัวข้อ 9 (DNS) ก่อน LAB 5–6 อ่านหัวข้อ 10–12 (kube-proxy, การกระจาย, readiness) ก่อน LAB 7 อ่านหัวข้อ 13 (debug) ก่อน LAB 8–9 อ่านหัวข้อ 6–8 และ 14 (NodePort, LoadBalancer, ExternalName/headless, NetworkPolicy) และก่อน LAB 10 อ่านหัวข้อ 15
3. ทำ LAB **ตามลำดับ** LAB 1–9 ใช้ namespace `shop` ต่อเนื่องกัน (ลบตอนท้าย LAB 9) และ **ต้องลบ NodePort 30080 ของ LAB 8 ก่อนเริ่ม LAB 10** ทำบล็อก "เก็บกวาด" ทุกครั้ง ใช้เวลารวมประมาณ 3–3.5 ชั่วโมง
4. สังเกตสัญลักษณ์ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0, 5 ตุลาคม 2569) แต่ **เวลา, ClusterIP, Pod IP, ชื่อ Pod ที่สุ่ม และจำนวนครั้งที่สุ่มได้อาจต่างจากเครื่องของนักศึกษา**
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** Pod ที่อยู่หลัง Service ทุก LAB สร้างด้วย **ReplicaSet** (บทที่ 5) เพราะ Service เลือก Pod ด้วย label ไม่สนว่าใครสร้าง การเปลี่ยนรุ่นทีละบูธอัตโนมัติ (Deployment) เป็นเนื้อหาของบทที่ 7 ส่วนการเก็บข้อมูลถาวร (PersistentVolumeClaim) และชื่อโดเมน/HTTPS (Ingress/Gateway) อยู่ในบทหลัง

## สิ่งที่ต้องผ่านก่อน

- [บทที่ 1: Kubernetes และสถาปัตยกรรม](../001_kubernetes-introduction/01_Theory/README.md) และ [LAB บทที่ 1](../001_kubernetes-introduction/02_LAB/readme.md): เข้าใจบทบาทของ Control Plane, Worker Node และมี container **`k8s-lab`** ที่สร้างตามบทที่ 1 (publish พอร์ต `2223`, `8889` และ **`30080–30082`**) ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น)
- [บทที่ 2: Kubernetes Pod](../002_kubernetes_pod/01_Theory/README.md) และ [LAB บทที่ 2](../002_kubernetes_pod/02_LAB/README.md): เขียน Pod YAML ได้ เข้าใจ labels, containerPort, probes (readiness/liveness), init container และ emptyDir
- [บทที่ 3: Node กับ Pod](../003_kubernetes_node_pod/01_Theory/README.md) และ [LAB บทที่ 3](../003_kubernetes_node_pod/02_LAB/README.md): เข้าใจ Node, kube-scheduler และ Downward API
- [บทที่ 4: Namespace](../004_kubernetes_namespace/01_Theory/README.md) และ [LAB บทที่ 4](../004_kubernetes_namespace/02_LAB/README.md): เข้าใจ namespace, DNS search domain, NetworkPolicy และ Pod Security Admission
- **[บทที่ 5: ReplicaSet](../005_kubernetes_replicaset/01_Theory/README.md) และ [LAB บทที่ 5](../005_kubernetes_replicaset/02_LAB/README.md) (ต้องผ่านก่อน):** เข้าใจ selector/template/ownerReferences/scale และเห็นปัญหาของร้าน 3 บูธที่บทนี้แก้ และ **เก็บกวาด namespace ของบทที่ 5** แล้ว
- คลัสเตอร์ kind `lab` จากบทก่อน **ใช้ต่อได้** ถ้ายังไม่มี (หรือเพิ่ง restart `k8s-lab`) LAB 0 จะสร้างใหม่ด้วย `k8s-up`
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image `nginx`, `busybox`, `postgres`, `node`) และมีหน่วยความจำว่างพอสำหรับร้าน 5 บูธ + db 1 ตัว (requests รวมราว 600m CPU / 1.2Gi)

## บทที่ 5 → 6 → 7 เป็นเรื่องต่อเนื่องกัน

บทนี้เป็นบทที่สองของชุด **workload และการเข้าถึงแอป** 3 บท ที่ใช้ร้านน้องส้มเรื่องเดียวกันต่อเนื่อง **ต้องผ่านบทที่ 5 ก่อน** และควรเรียนบทที่ 7 ต่อทันที

| บท | ตัวละครใหม่ | ปัญหาที่แก้ |
|---|---|---|
| [5 ReplicaSet](../005_kubernetes_replicaset/) | หัวหน้ากะ | บูธหายแล้วไม่มีใครสร้างแทน → มีบูธครบจำนวนเสมอ |
| **6 Service** (บทนี้) | ประภาคาร, คลิปบอร์ดรายชื่อบูธ, ป้ายบอกทาง, ประตู 30080 | ชื่อ/IP ของบูธเปลี่ยนทุกครั้งและแต่ละบูธมี db ของตัวเอง → ที่อยู่คงที่ของร้าน เปิดร้านจาก browser และแยก db กลาง |
| [7 Deployment](../007_kubernetes_deployment/) | ผู้จัดการร้าน | เปลี่ยนรุ่นต้องลบบูธเองจนร้านสะดุด → เปลี่ยนรุ่นทีละบูธอัตโนมัติและย้อนรุ่นได้ |

LAB สุดท้ายของบทนี้ตั้งใจจบด้วยปัญหาการเปลี่ยนรุ่นที่บทที่ 7 จะแก้ (ลบบูธทั้งหมดเองแล้วลูกค้าเจอ error 7 ใน 150 ครั้ง) จึงควรเก็บคลัสเตอร์และ image `som-shop-web:1.2`/`1.3` ไว้ใช้ต่อ

## โครงสร้างโฟลเดอร์

```text
006_kubernetes_service/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ 00–36 (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–10
    ├── images/                       ← ภาพประกอบ LAB 01–24 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
    ├── labs/                         ← YAML ของ LAB 1–9 (namespace shop และ kitchen)
    │   ├── lab01-before-service/
    │   ├── lab02-clusterip/
    │   ├── lab03-ports/
    │   ├── lab04-dns/
    │   ├── lab07-debug/
    │   ├── lab08-nodeport/
    │   └── lab09-cross-ns/
    └── som-shop-v2/                  ← LAB 10 ร้านน้องส้ม web + db แยกกัน
        ├── app/                      ← แอป Next.js + Dockerfile (som-shop-web:1.2 และ 1.3 จากโค้ดเดียว)
        ├── k8s/                      ← 00-namespace.yaml, 10-db.yaml, 20-web.yaml
        └── hit.sh                    ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน
```

ใน LAB 0 จะคัดลอกโฟลเดอร์ทั้งหมดนี้เข้า container ด้วย 🖥️ `docker cp 006_kubernetes_service k8s-lab:/workspace/` แล้วทำงานที่ `/workspace/006_kubernetes_service/02_LAB` ภายใน k8s-lab (แอปและ manifest ของ LAB 10 อยู่ที่ `/workspace/006_kubernetes_service/02_LAB/som-shop-v2/`) พอร์ต 30080–30082 ของ kind ถูก map ออกมาที่ `localhost` ของเครื่องนักศึกษาไว้แล้วตั้งแต่บทที่ 1 จึงเปิดร้านที่ `http://localhost:30080` ได้โดยไม่ต้อง port-forward

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)
