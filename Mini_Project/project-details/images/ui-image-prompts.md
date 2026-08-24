# Prompt สำหรับ Gen รูป UI ตัวอย่าง (5 รูป)

ใช้กับ Codex / ChatGPT / เครื่องมือ Gen รูปอื่น — รูปตรงกับตาราง "ตัวอย่างขั้นตอนการใช้งานบน UI" ใน `../README.md` §2.2 (8 หน้าจอ ยุบเป็น 5 รูป)

**Style กลาง (ใส่นำหน้าทุก Prompt เพื่อให้ทั้งชุดหน้าตาเดียวกัน):**

> Flat vector UI mockup illustration on a light cream background, clean modern web app for a pet clinic booking system, teal and coral accent colors, navy text, rounded cards, subtle shadows, no photorealism, minimal short English labels only, 16:9 aspect ratio.

---

## รูปที่ 1 — `pettech-ui-01-login-dashboard.png` (หน้าจอ 1–2)

Two browser-window mockups side by side. Left: login page with email and password fields, a sign-in button, and a small error toast reading "Invalid email or password". Right: pet owner dashboard showing a list of pets with dog and cat avatars, an upcoming appointment card, and a prominent "Book Appointment" button.

## รูปที่ 2 — `pettech-ui-02-select-pet-service.png` (หน้าจอ 3)

A booking wizard screen with a 3-step progress bar, step 1 highlighted. Selection cards for a pet (dog "Luna", cat "Milo") and a service list: Health Check, Vaccination, Grooming. The "Next" button is disabled and greyed out, with a small hint tooltip "Select a pet and service first".

## รูปที่ 3 — `pettech-ui-03-timeslot-calendar.png` (หน้าจอ 4)

Booking wizard step 2 of 3: a weekly calendar grid of appointment time slots. Available slots are teal clickable buttons, fully booked slots are grey and disabled with a "Full" label, and the selected slot is highlighted in coral. A side panel summarizes the chosen pet and service.

## รูปที่ 4 — `pettech-ui-04-confirm-result.png` (หน้าจอ 5–6)

Booking wizard step 3 of 3: left panel shows a confirmation summary card with pet, service, date, time, and veterinarian, plus a "Confirm Booking" button. Right side shows two stacked outcome states: a green success banner with a booking ID and status "Confirmed", and a red conflict banner reading "This slot was just taken" with three suggested alternative time slots.

## รูปที่ 5 — `pettech-ui-05-vet-dashboard-notification.png` (หน้าจอ 7–8)

Left: veterinarian admin dashboard with today's appointment schedule table, each row showing pet, owner, time, and status, with Confirm, Reschedule, and Cancel buttons. Right: a smartphone mockup showing a push notification and an email reminder "Appointment confirmed — Luna, May 20, 10:00".

---

## Markdown สำหรับแปะกลับเข้า README

เมื่อได้รูปครบแล้ว วางไฟล์ทั้ง 5 ลงโฟลเดอร์นี้ (`project-details/images/`) ตามชื่อด้านบน แล้วแปะบล็อกนี้ใน `../README.md` §2.2 ต่อท้ายตาราง UI (ก่อนย่อหน้า "ตารางนี้เป็นตัวอย่างระดับความละเอียด...")

```markdown
![UI 1 — เข้าสู่ระบบและ Dashboard](images/pettech-ui-01-login-dashboard.png)

![UI 2 — เลือกสัตว์เลี้ยงและบริการ](images/pettech-ui-02-select-pet-service.png)

![UI 3 — เลือกช่วงเวลาว่าง](images/pettech-ui-03-timeslot-calendar.png)

![UI 4 — ยืนยันการจองและผลลัพธ์ทั้งสำเร็จ/ถูกตัดหน้า](images/pettech-ui-04-confirm-result.png)

![UI 5 — มุมมองสัตวแพทย์และการแจ้งเตือน](images/pettech-ui-05-vet-dashboard-notification.png)
```
