ตรวจและแก้ครบทั้ง 15 ภาพแล้ว โดยดูจาก PNG ที่ render จริงทั้งก่อนและหลังแก้ ใช้ canvas เฉพาะ port 8894 และปิดเรียบร้อยแล้ว

คะแนนเรียงตาม `ความถูกต้อง / ตัวอักษร / เลย์เอาต์ / ความสวยงาม / อื่น ๆ`

| ไฟล์ | คะแนนก่อนแก้ | ปัญหาที่พบ | สิ่งที่แก้ | คะแนนหลังแก้ |
|---|---|---|---|---|
| `d01-pod-ip-changes.svg` | 5/4/3/4/5 | • ชื่อโซนซ้าย–ขวาทับเส้นประ | ย้ายชื่อโซนเข้าด้านในและเว้นระยะจากกรอบ | 5/5/5/5/5 |
| `d02-service-types.svg` | 3/4/4/4/5 | • คำว่า “เฉพาะ Pod ใน cluster” แคบเกินจริง เพราะ ClusterIP เข้าถึงได้จากภายใน cluster ไม่จำกัดเฉพาะ Pod | แก้เป็น “เฉพาะภายใน cluster” | 5/5/5/5/5 |
| `d03-config-outside-image.svg` | 3/4/2/3/5 | • ลูกศร ConfigMap พาดผ่าน Secret ทำให้ดูเหมือน ConfigMap → Secret → Deployment | แยกเส้น ConfigMap และ Secret ให้เข้า Deployment คนละเส้น พร้อม route อ้อม object | 5/5/4/4/5 |
| `d04-secret-base64.svg` | 5/4/4/4/5 | ไม่พบปัญหาชัดเจน เนื้อหา base64 และค่า `labpass` ถูกต้อง | ไม่แก้ | 5/4/4/4/5 |
| `d05-container-fs-vs-volume.svg` | 5/4/2/3/3 | • หัวข้อและข้อความสรุปเลื่อนไปนอกแนวกรอบ<br>• viewBox กว้างผิดชุดและไม่ใกล้ 16:9 | แก้ alignment ของ free text ทั้งสามคอลัมน์ และ export ใหม่เป็น `1500×840` | 5/5/5/5/5 |
| `d06-readiness-vs-liveness.svg` | 5/4/4/4/5 | ไม่พบปัญหาชัดเจน แยกผล readiness/liveness ถูกต้อง | ไม่แก้ | 5/4/4/4/5 |
| `d07-request-path-web-api-db.svg` | 5/4/3/4/5 | • ชื่อ namespace ทับเส้นประด้านบน | ย้ายชื่อ namespace เข้าด้านในกรอบ | 5/5/5/5/5 |
| `d08-learning-loop.svg` | 5/5/5/5/5 | ไม่พบปัญหา ลำดับทั้ง 6 ขั้นตรงตาม outline | ไม่แก้ | 5/5/5/5/5 |
| `lab008-architecture.svg` | 5/3/2/3/5 | • ป้าย Deployment/ReplicaSet ทับกรอบ<br>• ลูกศร fan-out พาดผ่าน Pod/ข้อความ<br>• namespace ทับเส้นประ | จัดใหม่ด้วย component มาตรฐาน แสดง web ×1, api ×2, Service DNS/Endpoints และไม่มี db อย่างชัดเจน | 5/5/5/5/5 |
| `lab009-architecture.svg` | 4/2/2/3/4 | • ขอบซ้ายดูถูกตัด<br>• ป้าย object ซ้อนกรอบ<br>• เส้น NodePort วนและความหมายไม่ชัด | แยกทางเข้า `<NodeIP>:30080` กับ `port-forward`; จัด Pod แนวตั้งเพื่อให้ fan-out ไม่ไขว้; แสดง api เป็น ClusterIP | 5/5/4/4/5 |
| `lab010-architecture.svg` | 4/3/3/3/5 | • ป้าย Deployment/ReplicaSet ซ้อนขอบ<br>• image note ชิด object และพื้นที่ไม่สมดุล | จัด chain ใหม่; แยก ConfigMap ใต้ Pod ด้วยเส้นประ; ระบุ image เดิมและ `rollout restart` | 5/5/4/4/5 |
| `lab011-architecture.svg` | 5/2/2/3/5 | • ป้าย object ซ้อนกัน<br>• ลูกศร Secret อ้อมยาวรบกวนภาพ<br>• หมายเหตุยื่นเกินพื้นหลัง | จัดระบบ 3 ชั้นใหม่; ใช้ Secret note แบบสั้น; ระบุ “ยังไม่มี PVC” โดยไม่ชนกรอบ | 5/5/4/4/5 |
| `lab012-architecture.svg` | 5/3/2/3/5 | • ปัญหาเลย์เอาต์ซ้ำจาก lab011<br>• emptyDir และข้อความข้อมูลหายชิดขอบล่าง | จัดระบบใหม่; วาง `emptyDir → ลบ Pod → ข้อมูลหาย` ภายใน namespace และแยกจากเส้น request | 5/5/4/4/5 |
| `lab013-architecture.svg` | 5/2/2/3/3 | • ชื่อภาพ/ส่วนล่างถูกตัดบางส่วน<br>• PVC/PV ชนขอบ namespace<br>• viewBox สูงผิดชุด | จัด PVC อยู่ใน namespace และ PV แบบ cluster-scoped อยู่นอกกรอบ; เว้น padding และ export ใหม่ | 5/5/4/4/5 |
| `lab014-architecture.svg` | 4/3/2/3/4 | • เส้น probes พาด Pod และข้อความ<br>• กล่อง probe ชนเส้น request<br>• หมายเหตุ readiness ทับขอบ | แยก readiness/liveness เป็นสองกล่องผลลัพธ์; จัด request path, Secret, PVC/PV ใหม่; ระบุ `Running แต่ 0/1 Ready` | 5/5/4/4/5 |

ผลตรวจเชิงไฟล์รอบสุดท้าย:

- SVG 15 ไฟล์และ `.excalidraw` 15 ไฟล์ ชื่อคู่กันครบ
- ทุก scene เปิดและ parse ได้
- ทุก SVG มี `viewBox="0 0 1500 840"`
- ตัวอักษรขั้นต่ำ 20px
- เส้นและรูปทรง non-text ใช้ `roughness: 0`
- สีทั้งหมดอยู่ใน palette ที่กำหนด
- ไม่พบชื่อบุคคล อีเมล หรือข้อมูลส่วนตัว
- ไม่พบภาพที่ยังมีข้อจำกัดแก้ไม่ได้
- ไม่ได้สร้างไฟล์รายงานเพิ่ม

ข้อสังเกตเชิงสไตล์สำหรับทั้ง 3 ครั้ง:

- ใช้เฟรม `1500×840`, ตำแหน่ง title/subtitle และระยะขอบเดียวกันทุกภาพ
- กำหนดรูปแบบคงที่: Deployment/Pod น้ำเงิน, Service เขียว, Ingress/ConfigMap/Secret สีเตือน, failure สีแดง
- ชื่อ namespace/node ต้องวางด้านในกรอบโดยเว้นจากเส้นประอย่างน้อย 16px
- หลาย Pod ควรวางแนวตั้งเมื่อ Service อยู่ด้านข้าง เพื่อให้ลูกศร fan-out ไม่พาด Pod ตัวแรก
- ใช้ลูกศรเขียวสำหรับ Service routing, น้ำเงินสำหรับ application request และเส้นประสำหรับ config/dependency
- Free text ควรชิดซ้าย; การจัดกึ่งกลางด้วยกรอบข้อความกว้างอาจเลื่อนตำแหน่งเมื่อ export SVG จาก Excalidraw
- ทุกครั้งควรตรวจจาก SVG ที่ render จริงหลัง export ไม่ควรตัดสินจาก canvas หรือ JSON เพียงอย่างเดียว