ตรวจและแก้ครบ 15/15 ภาพแล้ว ทั้ง SVG และต้นฉบับ `.excalidraw` พร้อมปิด canvas พอร์ต 8895 เรียบร้อย

ลำดับคะแนน: ความถูกต้อง / ตัวอักษร / เลย์เอาต์ / ความสวยงาม / อื่น ๆ

| ไฟล์ | คะแนนก่อนแก้ | ปัญหาที่พบ | สิ่งที่แก้ | คะแนนหลังแก้ |
|---|---|---|---|---|
| `d01-compose-to-objects.svg` | 3/5/5/5/5 | ระบุ `namespace lab015` แต่แสดงระบบ 10 objects ซึ่งรวม database ของ Lab 016 | เปลี่ยนเป็น “ตัวอย่างระบบเต็มรูปแบบ” ไม่ผูกกับ namespace ที่ผิด | 5/5/5/5/5 |
| `d02-stateless-vs-stateful.svg` | 5/5/5/5/5 | ไม่พบปัญหา | ไม่แก้ | 5/5/5/5/5 |
| `d03-ingress-vs-nodeport.svg` | 2/5/4/4/5 | มี `Service admin` ที่ไม่มีในแล็บ • ใช้เลข NodePort สมมติซึ่งอาจถูกเข้าใจว่าเป็นค่าจริง | ตัด admin ออก • เปลี่ยนเป็นแนวคิด “NodePort แยกต่อ Service” • คงเฉพาะ web/api และ Ingress `localhost:8080` | 5/5/4/4/5 |
| `d04-rolling-update-timeline.svg` | 5/5/5/5/5 | ไม่พบปัญหา; ลำดับ maxSurge/readiness ถูกต้อง | ไม่แก้ | 5/5/5/5/5 |
| `d05-requests-limits-scheduling.svg` | 3/5/4/5/5 | ลูกศร Pod ชี้ก้ำกึ่งระหว่าง worker ทั้งที่ควรลง worker-1 | ย้ายลูกศรให้ชี้ worker-1 โดยตรง | 5/5/5/5/5 |
| `d06-troubleshooting-ladder.svg` | 5/2/2/4/5 | คำอธิบายทั้งสี่ขั้นทับขอบกล่องหลายจุด • ข้อความล่างเกือบหลุดโซน | รวมคำอธิบายเข้าในกล่องแต่ละขั้นและจัดระยะใหม่ | 5/5/5/5/5 |
| `d07-request-path-browser-to-postgres.svg` | 2/4/4/5/5 | Secret/`DB_PASSWORD` ชี้ผิดไปยัง Pod db และ Service db | เปลี่ยนเป็น Secret → Pod api ด้วยลูกศรประเลียบขอบ • เพิ่มข้อความกำกับชัดเจน | 5/5/5/5/5 |
| `d08-learning-loop.svg` | 5/5/5/5/5 | ไม่พบปัญหา | ไม่แก้ | 5/5/5/5/5 |
| `lab015-architecture.svg` | 5/5/4/5/5 | ไม่พบปัญหาที่ต้องแก้ | ไม่แก้ | 5/5/4/5/5 |
| `lab016-architecture.svg` | 2/3/3/4/5 | ชื่อภาพถูกตัดซ้าย • เส้น request ต่อ Service→Service แทน Pod→Service • Secret ชี้ Pod db ผิด | สร้าง title ใหม่ • แก้เป็น Pod web→Service api และ Pod api→Service db • คง Secret→Pod api เท่านั้น | 5/5/5/5/5 |
| `lab017-architecture.svg` | 3/4/2/3/5 | แถว database เบียดกันและลูกศรไขว้ • Secret ชี้ Pod db ผิด • path label ชิดวัตถุ | ลดรายละเอียดซ้ำเป็น callout ที่ระบุชั้นข้อมูลเดิมและการ inject ที่ถูกต้อง • ลบ label/เส้นที่รบกวน | 5/5/5/5/5 |
| `lab018-architecture.svg` | 5/3/4/4/5 | ชื่อภาพถูกตัดซ้าย • กล่องค่ากลยุทธ์ชิดข้อความ • scene เดิมมี state ทำให้ export เลื่อนพิกัด | สร้าง scene ใหม่บน canvas ว่าง • จัด timeline v1→v2, readiness และ support objects ใหม่ • คืน viewBox 1500×840 | 5/5/5/5/5 |
| `lab019-architecture.svg` | 3/5/4/5/5 | ใช้ชื่อ `worker-1/2` ไม่ตรง cluster • label ทำให้ Scheduler ดูเหมือนอยู่ใน namespace | เปลี่ยนเป็น `devtools-worker`/`devtools-worker2` • แก้ขอบเขตเป็น Kubernetes cluster และ workload namespace | 5/5/5/5/5 |
| `lab020-architecture.svg` | 4/3/2/4/5 | ชื่อภาพถูกตัดซ้าย • Service endpoints ถูกนำเสนอซ้ำ • ลูกศร diagnostics พาดผ่านข้อความ | แก้ title • เปลี่ยนกล่องซ้ายเป็นอาการผู้ใช้ 503 • เดินลูกศร diagnostics รอบ callout | 5/5/5/5/5 |
| `lab021-architecture.svg` | 2/5/4/5/5 | Secret ชี้ Pod db/Service db ผิด • PVC ไม่ระบุชื่อจริง | เดิน Secret→Pod api เลียบขอบ • เพิ่ม `DB_PASSWORD → Pod api` • ระบุ `PVC db-data` | 5/5/5/5/5 |

ผลตรวจเชิงโครงสร้าง:

- SVG ชั้นบนสุดครบ 15 ไฟล์และชื่อตรงรายการ
- มีคู่ `.excalidraw` ที่ parse/import ได้ครบ 15 ไฟล์
- ทุก SVG มี `viewBox="0 0 1500 840"`
- font ต่ำสุด 20px, `roughness: 0`, ใช้เฉพาะ palette ที่กำหนด
- ไม่พบชื่อบุคคลหรืออีเมลจริง
- PNG สำหรับตรวจภาพจริงอยู่ใน [.work/diagram-review-s3](/root/workspace/DevTools/05_kubernetes/.work/diagram-review-s3)

ภาพที่ยังมีข้อจำกัดแก้ไม่ได้: ไม่มี

ข้อสังเกตเชิงสไตล์ที่ควรใช้เหมือนกันทั้ง 3 ครั้ง:

- ใช้ Deployment/ReplicaSet/Pod เป็นสีน้ำเงิน, Service สีเขียว, Ingress/ConfigMap/Secret/PVC สีเหลือง และ error สีแดงอย่างคงที่
- ลูกศรทึบใช้กับ request/data; ลูกศรประใช้เฉพาะ config/secret injection
- ชื่อภาพ 32px, subtitle 22px, เนื้อหาไม่น้อยกว่า 20px และเว้นขอบประมาณ 40–50px
- ชื่อ namespace/node ต้องเป็นข้อความอิสระเหนือกรอบเส้นประ ไม่ bind กับกรอบ background
- ภาพทฤษฎีไม่ควรระบุ namespace หรือ port สมมติ เว้นแต่ตรงกับแล็บจริง
- ทุกครั้งที่แก้ scene ต้อง render SVG จริงซ้ำ เพราะ canvas preview อาจไม่แสดงปัญหา font metrics หรือขอบภาพเหมือน SVG export