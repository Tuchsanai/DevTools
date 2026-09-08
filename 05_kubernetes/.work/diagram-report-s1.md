สร้างครบ 30 ไฟล์แล้วใน [slides_assets](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets):

- SVG 15 ไฟล์: `d01`–`d08` และ `lab001-architecture`–`lab007-architecture`
- Excalidraw 15 ไฟล์ชื่อเดียวกันใน [scenes](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets/scenes)

ตรวจทุก SVG โดย render เป็น PNG ขนาด 1600×900 และเปิดตรวจด้วยตาแล้ว ไม่พบข้อความทับ/ตกขอบหรือลูกศรผิดทิศทาง จึงไม่มีภาพที่ยังไม่พอใจหรือมีข้อจำกัดค้างอยู่

ปัญหาที่พบและแก้แล้ว:

- แท็บ headless ปิดตัวระหว่าง shell จึงเปลี่ยนเป็น persistent session บนพอร์ต 8893
- Excalidraw ปรับตำแหน่งข้อความกึ่งกลางเองจนล้นกรอบ จึงคำนวณตำแหน่งและตัดบรรทัดใหม่
- ปรับลูกศรและ selector boundary ใน `lab006`–`lab007` เพื่อลดเส้นพาดกัน
- ลบ `.ipynb_checkpoints` ที่สร้างสำเนา SVG อัตโนมัติ 4 ไฟล์ ตอนนี้โฟลเดอร์ส่งมอบเหลือ 30 ไฟล์ตรงรายการ
- ปิด canvas พอร์ต 8893 เรียบร้อยแล้ว