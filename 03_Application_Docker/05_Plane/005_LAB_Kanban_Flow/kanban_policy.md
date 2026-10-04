# Kanban Policies — ทีม CampusEats (โปรเจกต์ Plane Lab / PLAB)

> "Make policies explicit" — นโยบายที่ทุกคนเห็นบนบอร์ดเดียวกัน ไม่ใช่กติกาในหัวของคนใดคนหนึ่ง (Anderson, Kanban 2010)

## 1. คอลัมน์และความหมาย (State → group)

| คอลัมน์ | group ใน Plane | ความหมายในทีม |
|---|---|---|
| Backlog | backlog | ไอเดีย/คำขอที่ยังไม่ผ่านการคัดกรอง — ห้ามหยิบมาทำ |
| Todo | unstarted | ผ่าน Intake แล้ว รอเขียนรายละเอียดให้ครบตาม DoR |
| **Ready** | unstarted | ผ่าน **Definition of Ready** แล้ว — ใครว่างก็ "ดึง" (pull) ได้ทันที |
| In Progress | started | กำลังลงมือทำ นาฬิกา cycle time เริ่มเดินตั้งแต่เข้าคอลัมน์นี้ |
| **In Review** | started | code review / ทดสอบ — ยังนับเป็น WIP เพราะยังไม่ส่งมอบ |
| Done | completed | ผ่าน **Definition of Done** — Plane บันทึก `completed_at` ให้อัตโนมัติ |
| Cancelled | cancelled | เลิกทำ พร้อมเหตุผลใน comment |

## 2. Definition of Ready (DoR) — ก่อนย้ายเข้า Ready

- [ ] เขียนในรูป **ในฐานะ… ฉันต้องการ… เพื่อ…** และมี Acceptance Criteria อย่างน้อย 2 ข้อ
- [ ] มี Priority และ Label (feature / bug / docs / tech-debt)
- [ ] ประเมินขนาดแล้ว (story points) และไม่เกิน 8 points — ใหญ่กว่านั้นให้แตกเป็น sub-work item
- [ ] ไม่มีสิ่งที่ blocked อยู่ (relation *Blocked by* ต้องว่าง)

## 3. Definition of Done (DoD) — ก่อนย้ายเข้า Done

- [ ] Acceptance Criteria ทุกข้อติ๊กครบ
- [ ] ผ่าน review ในคอลัมน์ In Review โดยคนที่ **ไม่ใช่** ผู้ทำ
- [ ] มี link ไป commit/PR ในใบงาน (traceability — LAB 3)
- [ ] ไม่มี sub-work item ค้างในคอลัมน์ก่อน Done

## 4. WIP limits (บังคับด้วย `wip_guard.py` เพราะ Plane CE ไม่มี WIP limit ในบอร์ด)

| คอลัมน์ | limit | เหตุผล |
|---|---|---|
| In Progress | **3** | ทีม 2 คน + งานเร่งด่วน 1 ใบ — เกินกว่านี้คือ multitasking |
| In Review | **2** | review ค้างคือคอขวดที่พบบ่อยที่สุด |

กติกา: ถ้าคอลัมน์เต็ม **ห้ามดึงงานใหม่** ให้ไปช่วยเคลียร์คอลัมน์ขวาสุดที่เกินก่อน ("stop starting, start finishing")
`wip_guard.py` คืน exit 1 เมื่อเกิน — ใช้เป็นด่านใน CI ได้ และ `--watch 15` ใช้แขวนบนจอทีม

## 5. Expedite lane (class of service)

- ใบงาน **Priority = Urgent** คือ expedite: ข้ามคิว Ready ได้ทันที มีได้ **ครั้งละ 1 ใบ** ทั้งบอร์ด และไม่นับใน WIP limit
- ใบงาน Priority = High คือ fixed-date/standard ที่ต้องดึงก่อน Medium/Low — ดูได้จาก View **Expedite lane** (filter Urgent + High)
- ใครสั่ง expedite ต้องเขียนเหตุผลใน comment และแจ้งใน Daily kanban

## 6. Cadences

- **Daily kanban** เดินบอร์ดจากขวาไปซ้าย (Done ← In Review ← In Progress) ทุกวัน 10:00
- **Replenishment** เติม Ready จาก Todo สัปดาห์ละครั้ง (ใช้ผล `flow_metrics.py` ประกอบ)
- **Intake triage** ผู้ดูแลตัดสิน Accept / Decline / Snooze ทุกใบใน Intake ภายใน 1 วันทำการ
