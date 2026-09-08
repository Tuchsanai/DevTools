สร้างครบ 30 ไฟล์แล้วใน [slides_assets](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets):

- SVG 15 ไฟล์: `d01`–`d08` และ `lab008`–`lab014`
- Excalidraw 15 ไฟล์ชื่อคู่กันใน [scenes](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets/scenes)

ตรวจทุกภาพโดย render SVG เป็น PNG ขนาด 1600×900 และเปิดดูด้วยตาแล้ว ไม่เหลือภาพที่ไม่พอใจหรือข้อจำกัดสำคัญ

ปัญหาที่พบและแก้แล้ว:

- Headless tab หลุดระหว่าง export รอบแรก
- แก้ลูกศรที่พาดผ่าน object และข้อความ
- แก้ข้อความ Browser ล้นกรอบ
- เพิ่ม Secret ให้ lab012–014 ตาม object จริง
- ย้าย PV ของ lab013/014 ออกนอก namespace
- ตรวจชื่อไฟล์ตรงรายการ, SVG/JSON อ่านได้, font ต่ำสุด 20px และ non-text elements ใช้ `roughness: 0`

ปิด canvas port 8894 เรียบร้อยแล้วครับ