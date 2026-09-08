ตรวจและแก้ครบทั้ง 15 ภาพแล้ว ไฟล์ SVG และ `.excalidraw` ถูกเขียนทับใน [slides_assets](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets) ตามชื่อเดิม

ลำดับคะแนน: `ความถูกต้อง / ตัวอักษร / เลย์เอาต์ / ความสวยงาม / อื่น ๆ`

| ไฟล์ | คะแนนก่อนแก้ | ปัญหาที่พบ | สิ่งที่แก้ | คะแนนหลังแก้ |
|---|---|---|---|---|
| d01-compose-vs-kubernetes.svg | 5/5/5/4/5 | เส้นคั่นหัวเรื่องเป็น arrow จึงมีหัวลูกศรแฝง | เปลี่ยนเป็น line จริง | 5/5/5/5/5 |
| d02-cluster-architecture.svg | 3/5/4/4/5 | วาด controller ติดต่อ etcd โดยตรง ซึ่งข้าม API server | เปลี่ยนเป็น API server ↔ etcd และทำช่องทาง scheduler/controller เป็นสองทิศ | 5/5/4/5/5 |
| d03-pod-vs-container.svg | 3/4/4/4/5 | ใช้ Pod IP เสมือนค่าคงที่; สื่อว่า volume แชร์อัตโนมัติ; ข้อความสรุปชิดขอบ | ตัดเลข IP; ระบุว่า container ต้อง mount volume ร่วมกัน; ขยายกรอบสรุป | 5/5/4/5/5 |
| d04-declarative-loop.svg | 2/5/3/4/5 | reconciliation loop วนกลับไป YAML ผิดทิศ | เปลี่ยนลูปเป็น actual → compare → controller → action → actual และปรับคำอธิบาย | 5/5/4/5/5 |
| d05-labels-and-selectors.svg | 3/5/4/4/5 | มี Pod `worker-x` เกินจากแล็บและขัดกับเงื่อนไขใช้เฉพาะ web | ลบ Pod ส่วนเกิน เหลือ web-a/web-b/web-c ตรงกับแล็บ | 5/5/5/5/5 |
| d06-deployment-rs-pod.svg | 5/5/4/4/5 | กล่อง “revision พร้อม rollback” ลอย ไม่เห็นความสัมพันธ์กับ RS เก่า | เพิ่มเส้นกำกับจาก RS เก่าไปยังคำอธิบาย | 5/5/4/5/5 |
| d07-rolling-vs-recreate.svg | 5/5/5/4/5 | เส้นคั่นหัวเรื่องเป็น arrow | เปลี่ยนเป็น line จริง | 5/5/5/5/5 |
| d08-learning-loop.svg | 5/5/5/4/5 | เส้นคั่นหัวเรื่องเป็น arrow | เปลี่ยนเป็น line จริง | 5/5/5/5/5 |
| lab001-architecture.svg | 3/5/4/4/5 | ภาพเดิมสื่อว่า image cache อยู่เฉพาะ worker และลูกศรชี้เพียง node เดียว | เปลี่ยนเป็นแถบ cluster-level ระบุชัดว่า `kind load` โหลดเข้า control-plane และ worker ทั้งสอง; แก้คำบรรยายเป็น node ทั้ง 3 | 5/5/4/5/5 |
| lab002-architecture.svg | 5/5/5/4/5 | เส้นคั่นหัวเรื่องเป็น arrow | เปลี่ยนเป็น line จริง | 5/5/5/5/5 |
| lab003-architecture.svg | 3/5/4/4/5 | กรอบ Worker node ครอบ Pod ทั้งหมด ทำให้เข้าใจว่าต้องอยู่ node เดียวกัน | ลบกรอบดังกล่าวและเพิ่มหมายเหตุว่าแต่ละ Pod อาจอยู่คนละ node | 5/5/4/5/5 |
| lab004-architecture.svg | 2/5/2/4/5 | กรอบ namespace ครอบ API server และ Browser ซึ่งไม่อยู่ใน namespace | ย่อกรอบให้ครอบเฉพาะ Pod และจัดเส้น API/port-forward ใหม่ | 5/5/5/5/5 |
| lab005-architecture.svg | 2/5/5/4/5 | คำสั่ง `kubectl -l ...` ไม่สมบูรณ์ | แก้เป็น `kubectl get pods -l app=web,version=v2` | 5/5/5/5/5 |
| lab006-architecture.svg | 4/5/3/4/5 | เส้น traffic ไขว้กับ owner และหัวลูกศรชี้ออกจากกลุ่ม Pod | เดินเส้นใหม่ให้ไม่ไขว้และชี้ลงเข้าสู่กลุ่มที่ Service selector จับได้ | 5/5/4/5/5 |
| lab007-architecture.svg | 5/5/5/4/5 | เส้นคั่นหัวเรื่องเป็น arrow | เปลี่ยนเป็น line จริง | 5/5/5/5/5 |

ผลตรวจรับเพิ่มเติม:

- SVG ครบ 15 ไฟล์และมีคู่ `.excalidraw` ครบ 15 คู่
- ทุก scene import กลับเข้า canvas ได้
- ทุก SVG มี `viewBox="0 0 1420 820"`
- ฟอนต์ต่ำสุด 20px และ `roughness=0`
- สีทั้งหมดอยู่ใน palette ที่กำหนด
- ไม่พบชื่อบุคคล อีเมล หรือ metadata ส่วนตัว
- ตรวจภาพหลังแก้จาก PNG 1600×900 ครบทุกภาพ
- ปิด canvas พอร์ต 8893 แล้ว และไม่ได้สร้างไฟล์รายงานเพิ่ม

ภาพที่ยังมีข้อจำกัดแก้ไม่ได้: ไม่มี ทุกหมวดได้คะแนนอย่างน้อย 4

ข้อสังเกตเชิงสไตล์สำหรับทั้ง 3 ครั้ง:

- ใช้โครงหัวเรื่อง ตำแหน่ง และเส้นคั่นแบบเดียวกัน โดยเส้นคั่นต้องเป็น `line` ไม่ใช่ arrow
- กำหนดภาษาภาพให้คงที่: Pod=`accw`, Service/traffic/Ready=`okw`, input/Ingress/config=`warnw`, failure=`critw`, namespace/node=กรอบเทาเส้นประ
- ใช้เส้นน้ำเงินแทน ownership/control และเขียวแทน traffic/healthy พร้อม legend เมื่อมีสองความหมายในภาพเดียว
- ชื่อ namespace/node ต้องเป็น free-standing text และมีช่องว่างจากเส้นประ
- ค่าที่เปลี่ยนได้ เช่น Pod IP, hash และชื่อ node ควรระบุว่าเป็น “ตัวอย่าง” หรือหลีกเลี่ยงเลขจริง
- หากนำ object ของบทถัดไปมาใช้เป็นของสำเร็จรูป ต้องติดป้ายชัดเจนเหมือน Service/Ingress ในแล็บ 006–007
- รักษารูปทรง Deployment, ReplicaSet, Pod, Service และ Ingress ให้เหมือนชุดครั้งที่ 1 นี้ตลอดทั้งหลักสูตร