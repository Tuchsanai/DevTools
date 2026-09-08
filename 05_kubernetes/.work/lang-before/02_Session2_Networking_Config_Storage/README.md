# ครั้งที่ 2 — Networking, Config & Storage: Pod เปลี่ยนได้ แล้วแอปจะคุยและจำได้อย่างไร?

อ่าน manifest ของ Service, ConfigMap, Secret, Volume/PVC และ Probes ทีละ field ได้ใน [`YAML_Guide.md`](./YAML_Guide.md)

ครั้งนี้ถามสามเรื่องที่เริ่มชัดเมื่อ Pod ไม่ใช่สิ่งถาวร: จะเรียกปลายทางที่ IP เปลี่ยนอย่างไร,
จะเปลี่ยน config โดยไม่ build image ใหม่อย่างไร และจะเก็บข้อมูลให้รอดจาก Pod ใหม่อย่างไร
ปลายครั้งจะเพิ่ม readiness/liveness เพื่อแยกคำว่า process รันอยู่ ออกจากแอปพร้อมรับงาน

เนื้อหาต่อยอดจากครั้งที่ 1 ซึ่งสร้าง Pod ผ่าน Deployment และเห็น self-healing แล้ว
ครั้งนี้จึงติดตามผลที่ตามมา: Pod ตัวแทนมี IP ใหม่, container ใหม่ไม่มีข้อมูลเดิม และ Service
ต้องรู้ว่า Pod ใดพร้อมเป็น endpoint จริง โดยอ้างถึงแนวคิดเดิมเป็นข้อความ ไม่ผูก path ข้ามครั้ง

## สไลด์ของครั้งนี้

สไลด์ของครั้งนี้คือ [`Kubernetes_Session2_Slides.html`](./Kubernetes_Session2_Slides.html) (87 หน้า) — ดับเบิลคลิกเปิดในเบราว์เซอร์ได้ทันที (file://) ไม่ต้องต่ออินเทอร์เน็ต
เมื่อไฟล์ถูกเพิ่มตามชื่อมาตรฐาน ให้เปิดจากโฟลเดอร์นี้ด้วย:

```bash
xdg-open Kubernetes_Session2_Slides.html
```

ไฟล์ควรเปิดผ่าน `file://` ได้ทันที; ภาพรวมการเตรียมเครื่องอยู่ใน README ระดับชุด

| ปุ่ม | การทำงาน |
|---|---|
| `←` / `→` | สไลด์ก่อนหน้า / ถัดไป |
| `Space` | สไลด์ถัดไป |
| `PgUp` / `PgDn` | สไลด์ก่อนหน้า / ถัดไป |
| `Home` | ไปหน้าแรก |
| `End` | ไปหน้าสุดท้าย |
| `O` | เปิด overview grid |
| `F` | เปิด/ปิดเต็มจอ |
| `?` | เปิดหน้าช่วยเหลือ |
| `Esc` | ปิด overview หรือหน้าช่วยเหลือ |
| `Ctrl+P` | พิมพ์หรือบันทึก PDF อัตราส่วน 16:9 |

## แล็บทั้ง 7

| แล็บ | โฟลเดอร์ | หัวข้อหลัก | ไฮไลต์ |
|---:|---|---|---|
| 008 | [`008-why-we-need-service/`](./008-why-we-need-service/) | ทำไมต้องมี Service | ฝัง Pod IP แล้วลบปลายทาง ก่อนแก้ด้วยชื่อ DNS คงที่ของ Service |
| 009 | [`009-service-types-and-access/`](./009-service-types-and-access/) | Service types และขอบเขตการเข้าถึง | เทียบ ClusterIP/NodePort จากในและนอก cluster พร้อม selector ที่จงใจผิด |
| 010 | [`010-configmap-separate-config/`](./010-configmap-separate-config/) | ConfigMap แยก config จาก image | ใช้ image เดิมเปลี่ยนชื่อ/ธีม และเห็นว่า env ต้องสร้าง Pod ใหม่จึงเปลี่ยน |
| 011 | [`011-secret-and-why-not-configmap/`](./011-secret-and-why-not-configmap/) | Secret และข้อจำกัดของ base64 | ต่อ db-api-web ด้วย secretKeyRef แล้วพิสูจน์ว่า base64 decode อ่านได้ |
| 012 | [`012-why-data-disappears/`](./012-why-data-disappears/) | อายุข้อมูลใน container และ emptyDir | สร้าง ticket แล้ว recreate Pod เพื่อเห็นข้อมูลหายจริง |
| 013 | [`013-persistent-storage-with-pvc/`](./013-persistent-storage-with-pvc/) | Persistent storage ด้วย PVC | ลบ db Pod แล้วพิสูจน์ว่าข้อมูลยังอยู่บน PV เดิม |
| 014 | [`014-running-is-not-ready/`](./014-running-is-not-ready/) | Running ไม่เท่ากับ Ready | ทำ db หาย ดู readiness ถอด endpoint และให้ liveness restart ตัวป่วย |

## ลำดับที่ควรทำ

เส้นหลักคือ `008 → 009 → 010 → 011 → 012 → 013 → 014`

- 008 ต้องมาก่อน 009 เพื่อเห็นปัญหา Pod IP ก่อนจำแนกชนิด Service
- 010 แทรกระหว่าง 008 กับ 009 ได้ เพราะ ConfigMap ไม่พึ่งรายละเอียด NodePort
- 011 ควรตาม 010 เพื่อเทียบข้อมูลทั่วไปกับข้อมูลลับด้วย mental model เดียวกัน
- 012 และ 013 ไม่ควรแยกจากกัน: ต้องเห็นข้อมูลหายก่อนจึงเข้าใจว่า PVC แก้อะไร
- 014 ควรทำท้ายครั้ง เพราะใช้ระบบสามชั้น, Service และ dependency จากแล็บก่อนหน้า

## เตรียมเฉพาะครั้งนี้

ตรวจ node, image ทั้งสี่ และ ingress controller ที่แล็บช่วงหลังจะใช้:

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl -n ingress-nginx get pods
kubectl get ns lab008 lab009 lab010 lab011 lab012 lab013 lab014 --ignore-not-found
```

ครั้งนี้ใช้ namespace `lab008` ถึง `lab014` แยกกันทุกแล็บ
LAB 009 ใช้ port-forward ที่ `http://localhost:3000`; สำหรับ Ingress คำสั่งในเทอร์มินัลเครื่องเรียนเรียก `http://localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของคุณเปิด `http://localhost:8080`
PVC/PV ใน LAB 013 ต้องสังเกต finalizer ก่อน Cleanup เพราะการลบ claim คือการลบข้อมูลของแล็บ

## เก็บกวาดเมื่อจบครั้ง

```bash
kubectl delete ns lab008 lab009 lab010 lab011 lab012 lab013 lab014 --ignore-not-found
kubectl get ns lab008 lab009 lab010 lab011 lab012 lab013 lab014 --ignore-not-found
```

รอให้ namespace ที่มี PVC ลบเสร็จก่อนเริ่มซ้ำ และตรวจว่าไม่มี port-forward เก่าค้างใน terminal
ไม่ต้องลบ ingress-nginx หรือ cluster เพราะเป็นส่วนกลางที่ครั้งถัดไปใช้ต่อ

## เช็กลิสต์ปิดท้ายครั้ง

- [ ] อธิบายได้ว่าทำไม Pod IP ไม่ใช่ contract ที่ปลอดภัย และ Service ช่วยอย่างไร
- [ ] แยก ClusterIP กับ NodePort จากคำถามว่า “ใครเข้าถึงได้” ได้
- [ ] อธิบายได้ว่าทำไม ConfigMap ทำให้ image เดียวเปลี่ยนพฤติกรรมตาม deployment
- [ ] อธิบายได้ว่า Secret แยกข้อมูลลับแต่ base64 ไม่ใช่ encryption
- [ ] เปรียบเทียบ writable layer, emptyDir และ PVC ตามอายุของข้อมูลได้
- [ ] อธิบายความสัมพันธ์ PVC, PV และ StorageClass โดยไม่เรียกสามสิ่งนี้ว่า disk เดียวกัน
- [ ] อธิบายได้ว่า readiness กับ liveness ตอบคนละคำถามและส่งผลต่างกันอย่างไร

จำภาพเดียวให้ได้: **Pod เปลี่ยนได้ จึงต้องแยกชื่อคงที่ config และข้อมูลถาวรออกจากตัว Pod**
