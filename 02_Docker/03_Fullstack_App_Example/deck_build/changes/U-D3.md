# U-D3 — บันทึกการตัด ย้าย และแตกสไลด์

| เดิม (เด็ค 60 สไลด์) | การเปลี่ยนแปลง | ปลายทาง/แหล่งข้อมูลจริง |
|---|---|---|
| หน้า 38 · ตัวเลข `.next/standalone`, `.next/static` และ content size | แก้ `49.7 MB → 49.9 MB`, `680 kB → 668 kB`, `73.2MB → 73.3MB`, `310MB → 314MB` | `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 3–4 |
| หน้า 39 · `docker history` + การตรวจ `node_modules` สอง image | แตกเป็น 2 สไลด์: (ก) history ไม่มีบรรทัด `npm` (ข) `12` เทียบ `35` และไม่มี `typescript` | เนื้อหาทั้งสองแผ่นชี้ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 4 |
| หน้า 39 · transcript ของ base `node:22-alpine` ที่ไม่ใช่คำตอบหลัก | ย่อเป็นบรรทัด `ต่อจากนี้คือ base node:22-alpine 9 บรรทัด` | transcript เต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 4 |
| หน้า 39 · รายละเอียด exit code และคำอธิบาย toolchain | ย่อเหลือข้อสรุปว่าคำสั่งแรกออก exit code 1 เป็นคำตอบที่ถูก และ image ไม่มี compiler/devDependencies | คำอธิบายเต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 4 |
| หน้า 41 · transcript `ps` ของ exec/shell form | คงเฉพาะ PID 1, process ลูกที่จำเป็น และเวลา `0m0.244s` เทียบ `0m10.281s`; ตัดแถว process ของคำสั่ง `ps` | transcript เต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 7 |
| หน้า 41 · note ผลต่อ LAB 5 | ย่อกลไก `SIGTERM → SIGKILL` ให้เหลือข้อสรุปเดียว และเพิ่ม pointer | คำอธิบายเต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 7 |
| หน้า 42 · ขนาด CSS สองจุด | แก้ `35 kB → 21048 ไบต์` และ `35235 ไบต์ → 21048 ไบต์` | `003_LAB_Build_The_Web/readme.md` · กับดักของ Next.js 16 / การทดลองที่ 9 |
| ท้ายตอนที่ 6 · เดิมไม่มีสไลด์ปิดตอน | เพิ่ม 4 บล็อก: ทฤษฎี 3 บรรทัด, REQ-08/09/12, LAB 3 = 9 การทดลอง · 45 นาที · 22 PASS, คำสั่งไป LAB 4 | `003_LAB_Build_The_Web/readme.md` · แล็บนี้ใน 30 วินาที / ตรวจงานด้วย `verify.sh`; คำสั่งจาก `004_LAB_Connect_Them/readme.md` · เตรียมเครื่องเรียน |
| ท้ายตอนที่ 7 · เดิมไม่มีสไลด์ปิดตอน | เพิ่ม 4 บล็อก: ทฤษฎี 3 บรรทัด, NFR-3, LAB 4 = 9 การทดลอง · 45 นาที · 19 PASS, คำสั่งไป LAB 5 | `004_LAB_Connect_Them/readme.md` · แล็บนี้ใน 30 วินาที / ตรวจงานด้วย `verify.sh`; คำสั่งจาก `005_LAB_Compose_And_Ship/readme.md` · เตรียมเครื่องเรียน |

ทุกสไลด์เนื้อหาใน `s6_lab3.html` และ `s7_lab4.html` ได้เติมป้าย `ทฤษฎี` หรือ `หลักฐาน` ใน eyebrow ตามชนิดของสไลด์; ไม่มี `data-waiver` และไม่มีข้อความถูกย้ายเข้า `<svg>` เพื่อหลบการนับ
