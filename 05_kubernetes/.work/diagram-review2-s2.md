วาดใหม่และตรวจครบทั้ง 15 คู่ใน [slides_assets](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets) แล้ว

| ไฟล์ | A/B/C/D ก่อน | กติกาที่ผิด | ดำเนินการ | A/B/C/D หลัง |
|---|---:|---|---|---:|
| `d01-pod-ip-changes.svg` | 5/2/4/4 | 1, 2, 3, 4, 6 | วาดใหม่ ใช้กรอบกลุ่ม api Pods และเส้นแนวนอน | 5/5/5/5 |
| `d02-service-types.svg` | 5/5/5/3 | 1, 6 | วาดใหม่ 4 คอลัมน์เท่ากัน ระยะลูกศร 80px | 5/5/5/5 |
| `d03-config-outside-image.svg` | 5/2/4/3 | 1, 2, 3, 6 | วาดใหม่ ใช้กรอบกลุ่ม Deployment และเส้น config แนวตั้ง | 5/5/5/5 |
| `d04-secret-base64.svg` | 5/5/4/5 | 1, 7 | วาดใหม่ ย้ายป้ายกำกับออกจากเส้นและจัด chain แนวนอน | 5/5/5/5 |
| `d05-container-fs-vs-volume.svg` | 5/5/4/2 | 1, 6, 9 | วาดใหม่ 3 panel เท่ากัน พร้อม gap 80px | 5/5/5/5 |
| `d06-readiness-vs-liveness.svg` | 5/5/5/5 | 1 | วาดใหม่บน grid 40px และจัดสอง panel สมมาตร | 5/5/5/5 |
| `d07-request-path-web-api-db.svg` | 5/2/5/4 | 1, 3, 5 | วาดใหม่เป็นเส้นทางซ้าย→ขวาแถวเดียว | 5/5/5/5 |
| `d08-learning-loop.svg` | 5/5/5/5 | 1 | วาดใหม่บน grid; คงเส้นวงจรตามข้อยกเว้นภาพทฤษฎี | 5/5/5/5 |
| `lab008-architecture.svg` | 5/2/4/2 | 1, 2, 3, 4, 6 | วาดใหม่ Service ชี้กรอบกลุ่ม api Pods เพียงเส้นเดียว | 5/5/5/5 |
| `lab009-architecture.svg` | 5/2/4/2 | 1, 2, 3, 4, 5, 6 | วาดใหม่ แยกกลุ่มทางเข้า, web Pods และ ClusterIP | 5/5/5/5 |
| `lab010-architecture.svg` | 5/4/4/2 | 1, 2, 6 | วาดใหม่ traffic แนวนอนและ ConfigMap แนวตั้ง | 5/5/5/5 |
| `lab011-architecture.svg` | 5/2/4/3 | 1, 2, 3, 5, 6 | วาดใหม่เป็นเส้นทางสามชั้นแบบขั้นบันได | 5/5/5/5 |
| `lab012-architecture.svg` | 5/2/4/2 | 1, 2, 3, 5, 6 | วาดใหม่ วาง emptyDir ใต้ Pod db ตรงกึ่งกลาง | 5/5/5/5 |
| `lab013-architecture.svg` | 5/2/3/2 | 1, 2, 3, 6 | วาดใหม่ ใช้กรอบ “ชั้นข้อมูล”; PV อยู่ใต้ PVC นอก namespace | 5/5/5/5 |
| `lab014-architecture.svg` | 5/2/4/2 | 1, 2, 3, 4, 6, 7 | วาดใหม่ ใช้กรอบ api Pods และแยกผล probe จากเส้น request | 5/5/5/5 |

ผลตรวจสุดท้าย:

- SVG และ `.excalidraw` ครบ 15 คู่ ชื่อตรงกันและ parse ได้
- ทุกภาพ `viewBox="0 0 1540 900"`
- ลูกศรทุกเส้นมี `startBinding` และ `endBinding`
- gap ต่ำสุด 80px, font ต่ำสุด 20px, เส้นหลัก 2px
- ไม่พบเส้นเฉียง ยกเว้น `d08` ซึ่งเป็นวงจรทฤษฎีตามข้อยกเว้น
- ตรวจภาพ render จริงครบทั้งชุดและสไตล์สอดคล้องกัน
- ปิด canvas port 8894 แล้ว
- ไม่มีข้อจำกัดที่ยังค้าง และไม่ได้สร้างไฟล์รายงานเพิ่ม