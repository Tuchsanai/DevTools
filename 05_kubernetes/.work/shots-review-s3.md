ตรวจภาพจริงครบ 14 ไฟล์แล้ว โดยคะแนนเรียงตาม: ตรงขั้นตอน / หลักฐานมองเห็น / คุณภาพ / ความสม่ำเสมอ / ความปลอดภัย

| แล็บ | ไฟล์ | คะแนน 5 หมวด | ปัญหา | ถ่ายใหม่? |
|---|---|---:|---|---|
| 015 | `03-web-api-assembled-no-db.png` | 5/5/5/5/5 | ไม่มี—web/API พร้อม, DB down ตามขั้นตอน | ไม่ |
| 015 | `04-api-service-deleted.png` | 5/5/5/5/5 | ไม่มี—API `fetch failed` และ DB `unknown` ตรงกับการลบ Service | ไม่ |
| 016 | `02-full-stack-with-data.png` | 5/5/5/5/5 | ไม่มี—WEB/API/DB พร้อมครบ | ไม่ |
| 016 | `03-data-survives.png` | 5/5/5/4/5 | เป็น full-page 1280×1595 ต่างจากภาพ 800px แต่จำเป็นเพื่อเห็นการ์ดสถานะและ ticket #9 พร้อมกัน | ไม่ |
| 017 | `03-root-via-ingress.png` | 5/5/5/5/5 | ไม่มี—ระบบครบและเข้าผ่าน `/` | ไม่ |
| 017 | `03-api-dashboard-json-via-ingress.png` | 5/4/4/4/5 | เป็น JSON ดิบและไม่มีการ์ดสถานะ แต่เป็นหลักฐานตรงของ `/api/dashboard` ผ่าน Ingress | ไม่ |
| 018 | `04-rollout-in-progress-mixed.png` | 4/4/5/5/5 | ภาพเดี่ยวเห็น request ตกที่ v1; หลักฐาน v1/v2 mixed อยู่ใน monitor/Expected output รอบข้าง และภาพถัดไปเห็น v2 emerald ชัด | ไม่ |
| 018 | `04-rollout-done-v2.png` | 5/5/5/5/5 | ไม่มี—ป้าย v2 และธีม emerald ชัดเจน | ไม่ |
| 018 | `06-after-undo-v1.png` | 5/5/5/5/5 | ไม่มี—กลับเป็น v1 และธีมน้ำเงินชัดเจน | ไม่ |
| 019* | `02-web-with-resources.png` | 5/4/5/5/5 | UI ยืนยัน Pod/v1 ยังให้บริการหลังตั้ง resources; ค่า requests/limits พิสูจน์ด้วย kubectl รอบภาพ | ไม่ |
| 020* | `05-service-fixed.png` | 5/5/5/5/5 | ไม่มี—เห็น `endpoint-web`; API/DB สีเทาเป็นสถานะที่ตั้งใจของเคสนี้ | ไม่ |
| 021 | `01-complete-system.png` | 5/5/5/5/5 | ไม่มี—WEB/API/DB เขียวครบและชื่อ Pod อ่านได้ | ไม่ |
| 021 | `02-ticket-created-trace.png` | 5/5/5/4/5 | เป็น full-page 1280×1614 เพื่อให้เห็นการ์ดสถานะและ ticket #9 ในภาพเดียว | ไม่ |
| 021 | `04-db-service-cut.png` | 5/5/5/5/5 | ไม่มี—DB แดง/down ขณะที่หน้าเว็บยังตอบได้ตรงขั้นตอน | ไม่ |

\* แล็บ 019–020 ไม่บังคับ screenshot แต่ตรวจภาพที่มีอยู่ให้ครบแล้ว

สรุป:

- ทุกภาพกว้าง 1280 px, ไม่เบลอ, ไม่มีการ์ดถูกตัด และขนาดไฟล์ 36–294 KB
- ชื่อ Pod/version/status ตรงกับ Expected output ของรอบจริง และ README กำกับค่าที่เปลี่ยนได้ไว้แล้ว
- ไม่พบชื่อจริง, email, token, `172.30.*` หรือชื่อ `devtools-k8s-lab-*`
- ไม่มีภาพใดได้ต่ำกว่า 4 จึงไม่ต้องถ่ายใหม่และไม่มีการแก้ README
- ภาพบังคับไม่มีรายการขาด
- ภาพที่ outline ระบุแบบมีเงื่อนไขแต่ไม่มีไฟล์: `016/images/05-db-scale-2-crash.png` — outline อนุญาตให้ใช้ผล `kubectl` แทน และ README ใช้หลักฐานดังกล่าวแล้ว
- ไม่ได้สร้าง container `devtools-k8s-shots-s3`; ตรวจ `docker ps -a --filter name=devtools-k8s-shots-s3` แล้วว่าง จึงยืนยันว่าไม่มี container ของงานนี้ค้างอยู่ครับ