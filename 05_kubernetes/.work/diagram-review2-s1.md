วาดใหม่ครบทั้ง 15 ภาพและเขียนทับคู่ SVG/Excalidraw ชื่อเดิมแล้วใน [slides_assets](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets) และ [scenes](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets/scenes)

คะแนนเรียง `A / B / C / D`

| ไฟล์ | ก่อน | กติกาที่ผิด | วาดใหม่/แก้จุด | หลัง |
|---|---:|---|---|---:|
| d01-compose-vs-kubernetes.svg | 5/3/5/4 | 1, 2, 6 | วาดสองฝั่งใหม่ จัดกลุ่ม Worker และผูกเส้นจากกึ่งกลางขอบ | 5/5/5/5 |
| d02-cluster-architecture.svg | 5/2/5/4 | 1, 2, 3, 6 | วาง API server เป็นศูนย์กลาง แยก control plane/worker และใช้เส้นตั้งฉาก | 5/5/5/5 |
| d03-pod-vs-container.svg | 5/3/4/3 | 1, 2, 3, 6, 7 | สร้างกรอบเปรียบเทียบใหม่ จัด container/volume เป็นแถวและกึ่งกลาง | 5/5/5/5 |
| d04-declarative-loop.svg | 5/3/5/4 | 1, 2, 6 | วาด reconciliation loop แบบเหลี่ยมบน grid และ bind ทุกช่วง | 5/5/5/5 |
| d05-labels-and-selectors.svg | 5/4/5/4 | 1, 2, 6 | ให้ selector ชี้เข้ากึ่งกลางกรอบกลุ่มแทนการ fan ไปแต่ละ Pod | 5/5/5/5 |
| d06-deployment-rs-pod.svg | 5/2/5/4 | 1, 2, 3, 4 | จัด Deployment → กลุ่ม RS → กลุ่ม Pod แนวดิ่ง ไม่มีเส้นเฉียง | 5/5/5/5 |
| d07-rolling-vs-recreate.svg | 5/4/5/5 | 1, 2 | สร้าง timeline สองแถวด้วยกล่องเท่ากันและเส้นตรงมี binding | 5/5/5/5 |
| d08-learning-loop.svg | 5/4/5/5 | 1, 2 | จัดวงจรเรียนรู้ใหม่และ bind ทุกจุด; คงเส้นเฉียงตามข้อยกเว้นวงจรทฤษฎี | 5/5/5/5 |
| lab001-architecture.svg | 5/3/5/4 | 1, 2, 3, 6 | จัด control plane เหนือ worker และแก้เส้น `kind load` เป็นเส้นตั้งฉาก | 5/5/5/5 |
| lab002-architecture.svg | 5/4/5/5 | 1, 2 | จัด namespace เป็นแถวเท่ากันและผูก kubectl เข้ากึ่งกลาง API group | 5/5/5/5 |
| lab003-architecture.svg | 5/3/5/4 | 1, 2, 6 | วาดใหม่ตาม feedback บังคับ จัด Pod ระยะเท่ากันและแยก Pod เสียชัดเจน | 5/5/5/5 |
| lab004-architecture.svg | 5/3/5/4 | 1, 2, 3 | จัด YAML → API → Pod → Browser แนวนอน และ desired ↔ actual แยกด้านล่าง | 5/5/5/5 |
| lab005-architecture.svg | 5/3/5/5 | 1, 2 | วาด selector เข้ากรอบกลุ่ม พร้อมแก้หมายเหตุสองบรรทัดไม่ให้ล้น | 5/5/5/5 |
| lab006-architecture.svg | 5/2/3/3 | 1, 2, 3, 4, 5, 7 | วาง traffic ซ้าย→ขวา, ownership บน→ล่าง และชี้เข้ากรอบ Pod | 5/5/5/5 |
| lab007-architecture.svg | 5/2/4/3 | 1, 2, 3, 4, 5, 6 | วาดใหม่ทั้งหมด: traffic แถวเดียว, Deployment/RS/Pod กึ่งกลางตรงกัน | 5/5/5/5 |

ผลตรวจสุดท้าย:

- SVG และ scene ครบ 15 คู่ ขนาดทุกภาพ `1580×900`
- ลูกศรทั้งหมดมี `startBinding`/`endBinding`; ระยะเชื่อมต่ำสุด 80px
- ไม่มีเส้นเฉียง ยกเว้น `d08` ตามข้อยกเว้นของกติกา
- ฟอนต์อย่างน้อย 20px, เส้นหลัก 2px, กรอบเส้นประ 1.5px
- ตรวจความสม่ำเสมอรวมจาก [contact-sheet.png](/root/workspace/DevTools/05_kubernetes/.work/diagram-review2-s1/contact-sheet.png)
- ปิด canvas port 8893 แล้ว และไม่ได้แตะ port 8892

ข้อจำกัดที่ยังเหลือ: ไม่มี; `d08` ใช้เส้นเฉียงโดยเจตนาตามข้อยกเว้นสำหรับวงจรเชิงทฤษฎีเท่านั้น