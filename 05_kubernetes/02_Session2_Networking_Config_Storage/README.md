# ครั้งที่ 2 — Networking, Config & Storage: การสื่อสารและการคงอยู่ของข้อมูลเมื่อ Pod เปลี่ยนแปลง

ศึกษา manifest ของ Service, ConfigMap, Secret, Volume/PVC และ Probes แยกตามแต่ละ field ได้จาก [`YAML_Guide.md`](./YAML_Guide.md)

การสอนครั้งนี้ศึกษาประเด็นสำคัญสามประการซึ่งปรากฏชัดเมื่อ Pod ไม่ใช่ทรัพยากรถาวร ได้แก่ วิธีอ้างถึงปลายทางที่ IP เปลี่ยนแปลง
วิธีเปลี่ยน config โดยไม่ build image ใหม่ และวิธีรักษาข้อมูลให้คงอยู่เมื่อมี Pod ใหม่
ช่วงท้ายจะเพิ่ม readiness/liveness เพื่อจำแนกสถานะ process ที่กำลังทำงานออกจากสถานะแอปพลิเคชันที่พร้อมรับงาน

เนื้อหาต่อยอดจากการสอนครั้งที่ 1 ซึ่งได้สร้าง Pod ผ่าน Deployment และสังเกตกลไก self-healing แล้ว
การสอนครั้งนี้จึงศึกษาผลที่เกิดขึ้นตามมา ได้แก่ Pod ที่สร้างทดแทนได้รับ IP ใหม่ container ใหม่ไม่มีข้อมูลเดิม และ Service
ต้องระบุ Pod ที่พร้อมเป็น endpoint โดยอ้างถึงแนวคิดเดิมในรูปข้อความโดยไม่ผูก path ข้ามครั้ง

## สไลด์ของครั้งนี้

สไลด์ประกอบการสอนแบบ Interactive สำหรับครั้งนี้คือ [`Kubernetes_Session2_Slides.html`](./Kubernetes_Session2_Slides.html) (88 หน้า) ซึ่งสามารถเปิดด้วยเบราว์เซอร์ผ่าน `file://` ได้โดยตรงโดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต
เมื่อเพิ่มไฟล์ตามชื่อมาตรฐานแล้ว สามารถเปิดจากโฟลเดอร์นี้ด้วยคำสั่งต่อไปนี้:

```bash
xdg-open Kubernetes_Session2_Slides.html
```

ไฟล์ควรเปิดผ่าน `file://` ได้โดยตรง ส่วนภาพรวมการเตรียมเครื่องระบุไว้ใน README ระดับชุด

| ปุ่ม | การทำงาน |
|---|---|
| `←` / `→` | สไลด์ก่อนหน้า / ถัดไป |
| `Space` | สไลด์ถัดไป |
| `PgUp` / `PgDn` | สไลด์ก่อนหน้า / ถัดไป |
| `Home` | ไปหน้าแรก |
| `End` | ไปหน้าสุดท้าย |
| `O` | เปิด overview grid |
| `F` | เปิด/ปิดเต็มจอ |
| `?` | เปิดหน้าคำแนะนำการใช้งาน |
| `Esc` | ปิด overview หรือหน้าคำแนะนำการใช้งาน |
| `Ctrl+P` | พิมพ์หรือบันทึก PDF อัตราส่วน 16:9 |

## ปฏิบัติการทั้ง 7

| ปฏิบัติการ | โฟลเดอร์ | หัวข้อหลัก | ประเด็นสำคัญ |
|---:|---|---|---|
| 008 | [`008-why-we-need-service/`](./008-why-we-need-service/) | เหตุผลที่ต้องมี Service | ฝัง (hard-code) Pod IP ไว้ฝั่ง web แล้วลบ Pod ปลายทาง ก่อนแก้ไขด้วยชื่อ DNS คงที่ของ Service |
| 009 | [`009-service-types-and-access/`](./009-service-types-and-access/) | Service types และขอบเขตการเข้าถึง | เปรียบเทียบ ClusterIP/NodePort จากภายในและภายนอก cluster พร้อม selector ที่กำหนดให้ผิดโดยเจตนา |
| 010 | [`010-configmap-separate-config/`](./010-configmap-separate-config/) | ConfigMap แยก config จาก image | ใช้ image เดิมเพื่อเปลี่ยนชื่อและธีม พร้อมสังเกตว่า env จะเปลี่ยนเมื่อสร้าง Pod ใหม่ |
| 011 | [`011-secret-and-why-not-configmap/`](./011-secret-and-why-not-configmap/) | Secret และข้อจำกัดของ base64 | เชื่อมต่อ db-api-web ด้วย secretKeyRef และยืนยันว่าสามารถ decode ค่า base64 กลับเป็นข้อความที่อ่านได้ |
| 012 | [`012-why-data-disappears/`](./012-why-data-disappears/) | อายุข้อมูลใน container และ emptyDir | สร้าง ticket แล้ว recreate Pod เพื่อพิสูจน์การสูญหายของข้อมูล |
| 013 | [`013-persistent-storage-with-pvc/`](./013-persistent-storage-with-pvc/) | Persistent storage ด้วย PVC | ลบ db Pod แล้วพิสูจน์ว่าข้อมูลยังคงอยู่บน PV เดิม |
| 014 | [`014-running-is-not-ready/`](./014-running-is-not-ready/) | Running ไม่เท่ากับ Ready | ทำให้ db ไม่พร้อมใช้งาน สังเกต readiness ถอด endpoint และให้ liveness restart process ที่ขัดข้อง |

## ลำดับที่ควรทำ

เส้นหลักคือ `008 → 009 → 010 → 011 → 012 → 013 → 014`

- ควรดำเนินการ 008 ก่อน 009 เพื่อศึกษาปัญหา Pod IP ก่อนจำแนกชนิด Service
- 010 แทรกระหว่าง 008 กับ 009 ได้ เพราะ ConfigMap ไม่พึ่งรายละเอียด NodePort
- ควรดำเนินการ 011 ต่อจาก 010 เพื่อเปรียบเทียบข้อมูลทั่วไปกับข้อมูลลับด้วย mental model เดียวกัน
- ควรดำเนินการ 012 และ 013 ต่อเนื่องกัน เนื่องจากต้องสังเกตการสูญหายของข้อมูลก่อนจึงจะเข้าใจปัญหาที่ PVC แก้ไข
- ควรดำเนินการ 014 เป็นลำดับสุดท้าย เนื่องจากใช้ระบบสามชั้น Service และ dependency จากปฏิบัติการก่อนหน้า

## เตรียมเฉพาะครั้งนี้

ตรวจสอบ node, image ทั้งสี่รายการ และ ingress controller ที่ปฏิบัติการช่วงหลังจะใช้งาน:

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl -n ingress-nginx get pods
kubectl get ns lab008 lab009 lab010 lab011 lab012 lab013 lab014 --ignore-not-found
```

การสอนครั้งนี้ใช้ namespace `lab008` ถึง `lab014` แยกจากกันในแต่ละปฏิบัติการ
LAB 009 ใช้ port-forward ที่ `http://localhost:3000`; สำหรับ Ingress คำสั่งในเทอร์มินัลเครื่องเรียนเรียก `http://localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องหลักเปิด `http://localhost:8080`
PVC/PV ใน LAB 013 ต้องตรวจสอบ finalizer ก่อน Cleanup เนื่องจากการลบ claim เป็นการลบข้อมูลของปฏิบัติการ

## การล้างทรัพยากรเมื่อสิ้นสุดการสอน

```bash
kubectl delete ns lab008 lab009 lab010 lab011 lab012 lab013 lab014 --ignore-not-found
kubectl get ns lab008 lab009 lab010 lab011 lab012 lab013 lab014 --ignore-not-found
```

รอให้การลบ namespace ที่มี PVC เสร็จสมบูรณ์ก่อนเริ่มดำเนินการซ้ำ และตรวจสอบว่าไม่มี port-forward เดิมค้างอยู่ใน terminal
ไม่จำเป็นต้องลบ ingress-nginx หรือ cluster เนื่องจากเป็นทรัพยากรส่วนกลางที่ใช้ต่อในการสอนครั้งถัดไป

## รายการตรวจสอบเมื่อสิ้นสุดการสอน

- [ ] อธิบายเหตุผลที่ Pod IP ไม่ใช่ contract ที่ปลอดภัย และอธิบายบทบาทของ Service ได้
- [ ] แยก ClusterIP กับ NodePort จากการพิจารณาขอบเขตของผู้ที่สามารถเข้าถึงข้อมูลได้
- [ ] อธิบายเหตุผลที่ ConfigMap ทำให้ image เดียวเปลี่ยนพฤติกรรมตาม deployment ได้
- [ ] อธิบายได้ว่า Secret แยกข้อมูลลับแต่ base64 ไม่ใช่ encryption
- [ ] เปรียบเทียบ writable layer, emptyDir และ PVC ตามอายุของข้อมูลได้
- [ ] อธิบายความสัมพันธ์ PVC, PV และ StorageClass โดยไม่เรียกสามสิ่งนี้ว่า disk เดียวกัน
- [ ] อธิบายได้ว่า readiness กับ liveness ตอบคนละคำถามและส่งผลต่างกันอย่างไร

ภาพรวมที่ควรจดจำ: **Pod เปลี่ยนแปลงได้ จึงต้องแยกชื่อคงที่ config และข้อมูลถาวรออกจาก Pod**
