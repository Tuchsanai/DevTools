สร้างครบ 30 ไฟล์แล้ว: SVG 15 ไฟล์ และ Excalidraw scene 15 ไฟล์

ตำแหน่ง:

- [slides_assets](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets)
- [scenes](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets/scenes)

รายการไฟล์คู่ SVG / Excalidraw:

- `d01-compose-to-objects`
- `d02-stateless-vs-stateful`
- `d03-ingress-vs-nodeport`
- `d04-rolling-update-timeline`
- `d05-requests-limits-scheduling`
- `d06-troubleshooting-ladder`
- `d07-request-path-browser-to-postgres`
- `d08-learning-loop`
- `lab015-architecture`
- `lab016-architecture`
- `lab017-architecture`
- `lab018-architecture`
- `lab019-architecture`
- `lab020-architecture`
- `lab021-architecture`

ผลตรวจ:

- Render SVG ทุกภาพด้วย `shot.js` ขนาด 1600×900 และเปิดตรวจด้วยตาครบ
- ไม่พบภาพที่ยังไม่พอใจหรือมี element ตกขอบ
- ตัวอักษรต่ำสุด 20px, `roughness: 0` ครบ และ scene JSON เปิดอ่านได้ครบ
- ชื่อไฟล์ตรงรายการ ไม่มีไฟล์ขาดหรือเกิน
- Canvas ส่วนตัวพอร์ต 8895 ถูกปิดแล้ว

ปัญหาที่พบและแก้แล้ว:

- การจัดข้อความกึ่งกลางเคยทำให้ SVG กว้างเกินและด้านขวาถูกตัด
- เส้นบางภาพเคยตัดผ่าน object โดยเฉพาะ d08 และ lab015–018
- Excalidraw กำหนด bound-label เป็น `roughness: 1` อัตโนมัติ จึง normalize กลับเป็น 0
- Headless tab หลุดเมื่อเปลี่ยน shell จึงเปิดแท็บเฉพาะพอร์ต 8895 ใหม่ต่อการ export โดยไม่แตะ canvas พอร์ต 8892