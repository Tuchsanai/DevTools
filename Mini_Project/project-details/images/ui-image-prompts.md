# Prompt สำหรับ Gen รูป UI ตัวอย่าง — ภาษาไทย (9 รูป)

ใช้กับ Codex / เครื่องมือ Gen รูปอื่น — รูปตรงกับตาราง "ตัวอย่างขั้นตอนการใช้งานบน UI" ใน `../README.md` §2.2 (8 หน้าจอ โดยแยกผลการจองเป็น 2 รูป: สำเร็จ / ถูกตัดหน้า)

**Style กลาง (ใส่นำหน้าทุก Prompt เพื่อให้ทั้งชุดหน้าตาเดียวกัน):**

> Flat vector UI mockup illustration on a light cream background, clean modern web app for a Thai pet clinic booking system branded "PetTech" with a dog-and-cat heart logo, teal and coral accent colors, navy text, rounded cards, subtle shadows, no photorealism, 16:9 aspect ratio. All UI text labels must be in Thai language, short, and spelled exactly as the Thai strings given in the prompt. Render Thai script carefully and legibly.

---

## รูปที่ 1 — `pettech-ui-th-01-login.png` (หน้าจอ 1: เข้าสู่ระบบ)

A login page in a browser window. Heading "เข้าสู่ระบบ", input fields labeled "อีเมล" and "รหัสผ่าน", a teal button "เข้าสู่ระบบ", a link "ลืมรหัสผ่าน?", and a small red error toast at the bottom reading "อีเมลหรือรหัสผ่านไม่ถูกต้อง". PetTech logo with a dog and cat on the left panel.

## รูปที่ 2 — `pettech-ui-th-02-dashboard.png` (หน้าจอ 2: หน้าหลัก)

A pet owner dashboard. Greeting "สวัสดี คุณสมชาย", section "สัตว์เลี้ยงของฉัน" with two pet cards: dog "ลูน่า" and cat "มิโล", a card "นัดหมายที่กำลังจะถึง" showing "24 พ.ค. 2569 • 10:00 น.", and a prominent coral button "จองนัดหมาย" at the top right. Sidebar menu: "หน้าหลัก", "สัตว์เลี้ยง", "นัดหมาย", "ตั้งค่า".

## รูปที่ 3 — `pettech-ui-th-03-select-pet-service.png` (หน้าจอ 3: เลือกสัตว์เลี้ยงและบริการ)

Booking wizard with a 3-step progress bar: "1 เลือกสัตว์และบริการ" highlighted, "2 เลือกวันเวลา", "3 ยืนยันการจอง". Left: pet selection cards "ลูน่า (สุนัข)" selected with a teal check, "มิโล (แมว)" unselected. Right: service list "ตรวจสุขภาพ", "ฉีดวัคซีน", "อาบน้ำตัดขน". The "ถัดไป" button is greyed out and disabled with a small tooltip "กรุณาเลือกสัตว์เลี้ยงและบริการก่อน".

## รูปที่ 4 — `pettech-ui-th-04-timeslot.png` (หน้าจอ 4: เลือกวันเวลา)

Booking wizard step 2 of 3: heading "เลือกวันเวลา", a weekly calendar grid of appointment time slots. Available slots are teal buttons, fully booked slots are grey with the label "เต็ม", the selected slot is highlighted coral. Legend at the bottom: "ว่าง" (teal), "เต็ม" (grey), "ที่เลือก" (coral). A side panel "สรุปการจอง" shows the chosen pet "ลูน่า" and service "ตรวจสุขภาพ", with a teal button "ถัดไป".

## รูปที่ 5 — `pettech-ui-th-05-confirm.png` (หน้าจอ 5: สรุปและยืนยัน)

Booking wizard step 3 of 3: a summary card titled "สรุปการจอง" listing rows "สัตว์เลี้ยง: ลูน่า", "บริการ: ตรวจสุขภาพ", "วันที่: 24 พ.ค. 2569", "เวลา: 10:00 น.", "สัตวแพทย์: หมอสมหญิง", with a large teal button "ยืนยันการจอง" and a back link "ย้อนกลับ".

## รูปที่ 6 — `pettech-ui-th-06-result-success.png` (หน้าจอ 6ก: ผลการจองสำเร็จ)

A booking result page with a green success banner "จองนัดหมายสำเร็จ!" and a happy dog illustration. Below: "รหัสนัดหมาย: PT-2569-1024", a green status chip "ยืนยันแล้ว", an appointment detail card repeating pet, service, date and time, and a teal button "กลับหน้าหลัก".

## รูปที่ 7 — `pettech-ui-th-07-result-conflict.png` (หน้าจอ 6ข: ช่วงเวลาถูกตัดหน้า)

A booking result page with a red alert banner "ช่วงเวลานี้เพิ่งถูกจอง" with subtitle "กรุณาเลือกช่วงเวลาใหม่" and a surprised cat illustration. Below: a section "ช่วงเวลาใกล้เคียง" with three alternative slot cards "11:00 น.", "13:00 น.", "15:00 น.", each with a coral button "เลือก".

## รูปที่ 8 — `pettech-ui-th-08-notification.png` (หน้าจอ 7: การแจ้งเตือนภายหลัง)

A smartphone mockup showing a push notification "PetTech: ยืนยันนัดหมายแล้ว — ลูน่า 24 พ.ค. 10:00 น." at the top, and below an email preview titled "แจ้งเตือนนัดหมายล่วงหน้า 1 วัน" from "PetTech" with a small calendar icon and a teal button "ดูนัดหมาย".

## รูปที่ 9 — `pettech-ui-th-09-vet-dashboard.png` (หน้าจอ 8: มุมมองสัตวแพทย์/ผู้ดูแล)

A veterinarian admin dashboard titled "ตารางนัดวันนี้" with a table: columns "สัตว์เลี้ยง", "เจ้าของ", "เวลา", "สถานะ" and action buttons "ยืนยัน" (teal), "เลื่อนนัด" (outline), "ยกเลิก" (red outline) on each row. Status chips: "รอยืนยัน" (yellow) and "ยืนยันแล้ว" (green). Header shows "หมอสมหญิง" with an avatar.

---

## Markdown ที่ใช้อ้างอิงใน README

```markdown
![UI 1 — เข้าสู่ระบบ](images/pettech-ui-th-01-login.png)

![UI 2 — หน้าหลักของเจ้าของสัตว์เลี้ยง](images/pettech-ui-th-02-dashboard.png)

![UI 3 — เลือกสัตว์เลี้ยงและบริการ](images/pettech-ui-th-03-select-pet-service.png)

![UI 4 — เลือกช่วงเวลาว่าง](images/pettech-ui-th-04-timeslot.png)

![UI 5 — สรุปและยืนยันการจอง](images/pettech-ui-th-05-confirm.png)

![UI 6 — จองสำเร็จ](images/pettech-ui-th-06-result-success.png)

![UI 7 — ช่วงเวลาถูกตัดหน้า พร้อมเวลาทดแทน](images/pettech-ui-th-07-result-conflict.png)

![UI 8 — การแจ้งเตือนบนมือถือและอีเมล](images/pettech-ui-th-08-notification.png)

![UI 9 — ตารางนัดฝั่งสัตวแพทย์](images/pettech-ui-th-09-vet-dashboard.png)
```
