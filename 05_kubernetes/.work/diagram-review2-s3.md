วาดใหม่ครบ 15/15 ภาพแล้ว ทั้ง [SVG และ scenes](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets) พร้อมตรวจภาพจริงที่ [diagram-review2-s3](/root/workspace/DevTools/05_kubernetes/.work/diagram-review2-s3)

| ไฟล์ | A B C D ก่อน | กติกาที่ผิด | วาดใหม่/แก้จุด | A B C D หลัง |
|---|---|---|---|---|
| `d01-compose-to-objects.svg` | 5 3 5 4 | 2, 6 | วาดใหม่ทั้งภาพ; ลูกศรตรงชี้กรอบกลุ่ม objects และ binding ครบ | 5 5 5 5 |
| `d02-stateless-vs-stateful.svg` | 5 4 5 5 | 2 | วาดใหม่; จัด Pod แถวตรงและเส้น Pod→PVC→PV กึ่งกลางขอบ | 5 5 5 5 |
| `d03-ingress-vs-nodeport.svg` | 5 2 5 4 | 2, 3, 4 | วาดใหม่; ใช้กล่องกลุ่มแทนเส้น fan เฉียง | 5 5 5 5 |
| `d04-rolling-update-timeline.svg` | 5 4 5 5 | 2 | วาดใหม่; timeline กล่องเท่ากันและลูกศรตรงทั้งหมด | 5 5 5 5 |
| `d05-requests-limits-scheduling.svg` | 5 3 5 4 | 2, 3, 6 | วาดใหม่; จัด Scheduler ตรงกึ่งกลางกับต้นทางและ node group | 5 5 5 5 |
| `d06-troubleshooting-ladder.svg` | 5 3 5 5 | 2, 6 | วาดใหม่; ขั้นตรวจเรียงแนวตั้ง ช่องว่าง 80px และไม่ชิดขอบ | 5 5 5 5 |
| `d07-request-path-browser-to-postgres.svg` | 5 3 4 4 | 1, 2, 3, 6 | วาดใหม่; ใช้ 6 stage groups แถวเดียว และ config injection แนวตั้ง | 5 5 5 5 |
| `d08-learning-loop.svg` | 5 3 5 5 | 2 | วาดใหม่; ลูปสี่เหลี่ยมด้วยเส้นแนวนอน/แนวตั้งที่ bind ครบ | 5 5 5 5 |
| `lab015-architecture.svg` | 5 2 5 4 | 2, 3, 5 | วาดใหม่; traffic ซ้าย→ขวา และ ownership บน→ล่าง | 5 5 5 5 |
| `lab016-architecture.svg` | 5 2 4 3 | 2, 3, 5, 6 | วาดใหม่; แยก 3 tier, PVC ใต้ DB และ Browser นอก namespace | 5 5 5 5 |
| `lab017-architecture.svg` | 5 2 5 4 | 2, 3, 4, 5 | วาดใหม่; Ingress→Services→Pods เป็นกลุ่มเรียงแถวเดียว | 5 5 5 5 |
| `lab018-architecture.svg` | 5 1 5 3 | 2, 3, 4 | วาดใหม่แน่นอน; Deployment→RS group→Pod group ไม่มี fan/เส้นโค้ง | 5 5 5 5 |
| `lab019-architecture.svg` | 5 3 5 4 | 2, 3, 5 | วาดใหม่; traffic และ ownership แยกแกน พร้อม Scheduler→node group | 5 5 5 5 |
| `lab020-architecture.svg` | 5 3 5 4 | 2, 3, 6 | วาดใหม่; อาการและ troubleshooting ladder แยกพื้นที่ชัดเจน | 5 5 5 5 |
| `lab021-architecture.svg` | 5 3 5 4 | 1, 2, 3, 6 | วาดใหม่แน่นอน; request path เป็นแถวตรงและ Secret→API แนวตั้ง | 5 5 5 5 |

ผลตรวจโครงสร้างสุดท้าย:

- ลูกศรทุกเส้นมี `startBinding` และ `endBinding`
- ไม่พบลูกศรเฉียงหรือ fan-out
- กล่องทั้งหมดลง grid 40px
- font ต่ำสุด 20px และ `roughness: 0`
- SVG ทั้งหมดขนาด `1540×878.4` อยู่ในช่วงบังคับ
- ชื่อ SVG/scene ตรงกันครบ 15 คู่
- ปิด canvas พอร์ต 8895 แล้ว
- ลบไฟล์ element/canvas ชั่วคราวแล้ว โดยเก็บ PNG ผลตรวจไว้

ภาพที่ยังมีข้อจำกัด: ไม่มี