# LAB 3 — work item มืออาชีพ · ทีมและสิทธิ์ · traceability · จรรยาบรรณ · token ส่วนตัว

> โฟลเดอร์ `003_LAB_Professional_Work_Items` = **LAB 3** ในสไลด์ `Plane_Agile_Slides.html` (ตอนที่ 1 · หลักการเพื่อเป็นผู้เชี่ยวชาญด้านซอฟต์แวร์ — work item · ทีมและสิทธิ์ · จรรยาบรรณ)
> (ไฟล์ของแล็บนี้ : `work_item_template.md` · `backlog_seed.md` · `ethics_cases.md` · `lint_work_items.py` · `planeapi.py` · `auth_rate_limit.sh` · `check_lab03.sh` · `requirements.txt`)
> (เวลาโดยประมาณ : 50 นาที)

## สิ่งที่จะได้เรียนรู้

- เขียน work item ที่ **ตรวจสอบได้**: บริบท · เกณฑ์การยอมรับ (checkbox) · Definition of Done · ความเสี่ยง — แล้วเทียบกับใบที่เขียนแค่ "แก้บั๊ก"
- แตกงานเป็น **sub-work items**, ระบุความสัมพันธ์ **Blocked by / Blocking**, แนบ **link** ไป commit เพื่อ traceability
- อ่าน **Activity** เป็นหลักฐานความรับผิดชอบ: ใครเปลี่ยนอะไร เมื่อไร (บันทึกโดย worker — เชื่อมกับ LAB 2)
- เพิ่มเพื่อนร่วมทีม **โดยไม่มี SMTP** ผ่านคำเชิญ + Copy link และเข้าใจบทบาท Admin (20) · Member (15) · Guest (5)
- สะท้อนคิดตาม **ACM/IEEE-CS Code of Ethics** บน Page ที่แก้พร้อมกันได้ (live)
- สร้าง **Personal Access Token** ของตัวเอง เก็บอย่างปลอดภัย แล้วใช้ `lint_work_items.py` วัดความครบถ้วนของ work item (hygiene) ทั้ง backlog

## ทฤษฎีที่เกี่ยวข้อง

- **การสื่อสารของวิศวกรคือการเขียน** — คำพูดหายไปกับอากาศ แต่ work item อ่านซ้ำได้ ตรวจย้อนหลังได้ และเป็น "หน่วยของการสื่อสาร" ระหว่างคนที่ไม่ได้อยู่ในห้องเดียวกัน (สไลด์ตอนที่ 1: กายวิภาคของ work item)
- **User story + INVEST + Acceptance Criteria** — ชื่อบอกผลลัพธ์ที่ผู้ใช้ได้ ไม่ใช่งานที่โปรแกรมเมอร์ทำ; เกณฑ์การยอมรับต้องตอบได้ว่า "ผ่าน/ไม่ผ่าน"; Definition of Done เป็นสัญญาของทีมว่า "เสร็จ" แปลว่าอะไร
- **Traceability** — โจทย์ ↔ work item ↔ commit/PR ↔ release ต้องตามกันได้ทั้งไปและกลับ; ใน Plane ใช้ Links, relations และ commit message ที่อ้าง `PLAB-N`
- **Accountability** — Activity log บันทึก actor · field · old → new ให้อัตโนมัติ (เฉพาะฟิลด์หลัก เช่น state, assignee, priority, labels, dates, estimate, comment) จึงเป็นหลักฐานที่เถียงไม่ได้
- **Least privilege** — สิทธิ์เท่าที่หน้าที่ต้องการ: Admin ตั้งค่า/เชิญคน, Member ทำงาน, Guest ดูและตอบกลับได้จำกัด; token ผูกกับคนและเพิกถอนได้ (จรรยาบรรณข้อ 2.05 · 3.09 · 5.05)
- **Code of Ethics 8 หลักการ** — Public · Client & Employer · Product · Judgment · Management · Profession · Colleagues · Self — ใช้กับ 3 กรณีในแล็บนี้ (ตัดการทดสอบ · ปกปิดบั๊ก · ข้อมูลส่วนบุคคล)

## ภาพรวมของแล็บนี้

1. **สร้าง label 4 ชนิด** (`bug` `feature` `docs` `tech-debt`) ให้ทีมใช้ร่วมกัน
2. **เขียน work item ที่ดี** ("นักศึกษาสมัครบัญชี…" — PLAB-4 ในภาพ) จากแม่แบบ และใบที่ไม่ดี ("แก้บั๊ก" — PLAB-5 ในภาพ: มีแค่ชื่อ ไม่มี AC/assignee/due/label) ไว้เทียบ
3. **แตกงาน**: sub-work items 3 ใบ · ความสัมพันธ์ Blocked by · link ไป commit
4. **Activity**: comment · เปลี่ยน state · assignee → ดูหลักฐานใน UI และ SQL
5. **ทีมโดยไม่มี SMTP**: เชิญ `dev1@example.com` → Copy link → dev1 สมัครด้วยรหัสผ่านที่ถูกปฏิเสธก่อน แล้วรับคำเชิญ → มอบหมายงาน
6. **Guest**: เชิญ `guest@example.com` เป็น Guest และเข้าใจสิทธิ์ 20/15/5
7. **จรรยาบรรณ**: Page "Code of Ethics Reflection — LAB 3" ที่ admin กับ dev1 เขียนพร้อมกัน
8. **Token ส่วนตัว** → `~/.plane_token` → `lint_work_items.py` ให้คะแนน backlog → แก้ใบ "แก้บั๊ก" ให้ครบแล้ววัดใหม่
9. **`check_lab03.sh`** พิมพ์ `PASS` บรรทัดเดียว

![กายวิภาคของ work item ที่ดี](../slides_assets/d06-work-item-anatomy.svg)

> **คำถามก่อนเริ่ม:** ไม่มี SMTP จะเพิ่มเพื่อนร่วมทีมได้ไหม? และ work item ที่เขียนว่า "แก้บั๊ก" ผิดตรงไหนบ้าง — เขียนคำตอบไว้ก่อน แล้วดูข้อ 5 และข้อ 8 ว่าหลักฐานตรงกับที่ทายไหม

### Terminal Map

| หน้าต่าง | หน้าที่ | เปิดเมื่อใด |
|---|---|---|
| **T1** | คำสั่ง SQL / curl / python ในเครื่องเรียน | ตั้งแต่เริ่ม |
| **B1** | เบราว์เซอร์ปกติ — ล็อกอินเป็น `admin@example.com` | ตั้งแต่เริ่ม |
| **B2** | หน้าต่าง private/incognito — จะกลายเป็น `dev1@example.com` | ข้อ 5 |

> ภาพหน้าจอในเอกสารนี้จับจากเครื่องทดสอบซึ่งอาจแสดง port อื่น (เช่น `localhost:8083`) — ของผู้เรียนคือ `localhost:8080`

> **เรื่องเลข PLAB-N:** ภาพและผลลัพธ์ในเอกสารนี้มาจากเครื่องที่ทำ **LAB 1 อย่างเดียว** จึงได้ **PLAB-4** (ใบดี) · **PLAB-5** (ใบไม่ดี) · **PLAB-6..8** (sub-work items) — ถ้าทำ LAB 2 มาแล้ว เลข 4–7 ถูกใช้ไปแล้วและ Plane **ไม่ใช้เลขซ้ำ** ใบเดียวกันจะเป็น **PLAB-8 · PLAB-9 · PLAB-10..12** · ให้ยึด**ชื่อ** work item และเลขที่ UI แสดงจริง — คำสั่ง SQL และ `check_lab03.sh` ในแล็บนี้ค้นด้วยชื่อ ไม่ใช่เลข

---

## 0. เตรียมเครื่องเรียน

ต้องผ่าน LAB 1 มาแล้ว (Plane รันอยู่ที่ `~/plane-selfhost`, มีคำสั่ง `pc`, โปรเจกต์ `Plane Lab` (`PLAB`) มี PLAB-1..3 — และ PLAB-4..7 ด้วยถ้าทำ LAB 2):

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 -p 8080:8080 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
pc ps --format 'table {{.Name}}\t{{.Status}}' | head -5
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/api/instances/
```

> 📝 **คำอธิบาย:** `pc` คือ `docker compose` ของสแต็ก Plane ที่ LAB 1 ติดตั้งไว้ · ถ้าเพิ่งเปิดเครื่องใหม่ให้ `pc start` แล้วรอจน `/api/instances/` ตอบ `200` (ราว 1–2 นาที) ·
> แล็บนี้ต้องการ **worker** ทำงาน เพราะ Activity และคำเชิญถูกบันทึกโดย worker (บทเรียนจาก LAB 2) — ตรวจว่า `plane-worker-1` เป็น `Up`

✅ **Expected output** — `200` และ `plane-worker-1 Up`

```
NAME                  STATUS
plane-admin-1         Up 2 hours (healthy)
plane-api-1           Up 2 hours
plane-beat-worker-1   Up 2 hours
plane-live-1          Up 2 hours
200
```

เข้าโฟลเดอร์แล็บ:

```bash
cd ~/labwork/DevTools/03_Application_Docker/Plane/003_LAB_Professional_Work_Items
ls
```

✅ **Expected output** — ไฟล์ของแล็บ 8 ไฟล์ + โฟลเดอร์ `images`:

```
auth_rate_limit.sh  backlog_seed.md  check_lab03.sh  ethics_cases.md  images  lint_work_items.py  planeapi.py  requirements.txt  work_item_template.md
```

---

## 1. สร้าง label ให้ทีมใช้ร่วมกัน

ใน B1: sidebar **Plane Lab** → ไอคอน ⚙ (หรือ **Settings → Projects → Plane Lab**) → **Labels** → **Add label** ทีละตัว: `bug` (แดง) · `feature` (เหลือง) · `docs` (เขียว) · `tech-debt` (ฟ้า)

![หน้า Labels ของโปรเจกต์หลังสร้าง 4 label](./images/ui-labels.png)

> 📝 **คำอธิบาย:** label คือ "ภาษากลาง" ของทีม — ใช้ filter, view, และ automation ได้ในทุกแล็บถัดไป · ตั้งชื่อเป็นตัวพิมพ์เล็กสั้น ๆ และตกลงความหมายกันครั้งเดียว (`tech-debt` = งานที่ไม่เพิ่มฟีเจอร์แต่ลดต้นทุนอนาคต)

ตรวจในฐานข้อมูล (T1):

```bash
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select name, color from labels where project_id=(select id from projects where identifier='PLAB') and deleted_at is null order by name;"
```

> 📝 **คำอธิบาย:** `pc exec -T … plane-db psql` รันคำสั่ง SQL ข้างใน container ของ PostgreSQL · ต้องส่ง `PGPASSWORD=plane` เพราะ container ตั้ง `PGHOST` ให้ต่อผ่าน TCP ซึ่งขอรหัสผ่าน (ค่า LAB เท่านั้น) · `deleted_at is null` กรองแถวที่ถูก soft-delete ออก (LAB 2)

✅ **Expected output** — 4 แถว ชื่อ label เรียงตามตัวอักษรพร้อมรหัสสี:

```
   name    |  color
-----------+---------
 bug       | #EB144C
 docs      | #00d084
 feature   | #fcb900
 tech-debt | #0693e3
(4 rows)
```

---

## 2. work item ที่ดี vs ไม่ดี

เปิด `work_item_template.md` แล้วอ่านกติกาสามข้อ: **ชื่อ = ผลลัพธ์ที่ผู้ใช้ได้ · เกณฑ์การยอมรับต้องทดสอบได้ · ฟิลด์ว่างคือคำถามที่เพื่อนต้องเสียเวลาถาม**

ใน B1: **Work items → Add work item**
- Title: `นักศึกษาสมัครบัญชีและเข้าสู่ระบบด้วยอีเมล`
- Description: คัดลอกตัวอย่างเต็มของ story ที่ 1 จาก `backlog_seed.md` (พิมพ์ `[]` ตามด้วยเว้นวรรคต้นบรรทัดจะกลายเป็น checkbox)
- Priority **High** · Label **feature** · Due date **+7 วัน** → **Save** → ได้เลขถัดไป (**PLAB-4** ในภาพ — ต่อจากนี้เอกสารจะเรียกใบนี้ว่า PLAB-4)

![ฟอร์ม Create new work item ของ PLAB-4 ที่กรอกครบ](./images/ui-create-good-item.png)

แล้วสร้างใบ "ไม่ดี" ไว้เทียบ: Title `แก้บั๊ก` โดย **ไม่กรอกอะไรเลย** นอกจากชื่อ → **PLAB-5** (ในภาพ) — ข้อ 8 จะกลับมาแก้ใบนี้ให้ครบ รวมทั้งเปลี่ยนชื่อ

![รายการ work items เทียบใบที่ดีกับใบที่ไม่ดี](./images/ui-work-items-good-vs-bad.png)

> 📝 **คำอธิบาย:** PLAB-5 ไม่ผิดที่ "สั้น" แต่ผิดที่ **ตอบคำถามไม่ได้**: ทำซ้ำอย่างไร · เสร็จแล้ววัดจากอะไร · ใครทำ · เมื่อไร — ข้อ 8 จะให้สคริปต์วัดเป็นคะแนน แล้วเราจะกลับมาแก้

เปิด PLAB-4 ดูหน้า detail:

✅ **Expected output** — checkbox 3 ข้อในส่วน "เกณฑ์การยอมรับ", properties ด้านขวาแสดง State/Priority/Label/Due date ครบ (ภาพหน้า detail เต็มอยู่ท้ายข้อ 3 หลังเพิ่ม sub-work items · relation · link)

---

## 3. แตกงาน: sub-work items · Blocked by · link

ใน PLAB-4 → ส่วน **Sub-work items → Add sub-work item → Create new** ×3:
`ออกแบบฟอร์มสมัคร/เข้าสู่ระบบ (UI)` · `API สมัครบัญชีและตรวจโดเมนอีเมล` · `เขียน test ครอบคลุมเกณฑ์การยอมรับ 3 ข้อ`

![Sub-work items 0/3 ใต้ PLAB-4](./images/ui-sub-items-0of3.png)

ย้าย sub-item ใบแรกเป็น **Done** → วงกลมความคืบหน้าเป็น 1/3:

![Sub-work items 1/3 หลังปิดงานย่อยใบแรก](./images/ui-sub-items-1of3.png)

> 📝 **คำอธิบาย:** sub-work item เป็น work item เต็มตัวที่มี `parent` — จึง **กินเลข** ไปด้วย (PLAB-6..8 ในภาพ) (ดูข้อ 8 และ LAB 2: `issue_sequences` ไม่ใช้เลขซ้ำ) · ความคืบหน้าของ parent คำนวณจากลูก แต่ parent **ไม่ Done เอง** — ทีมต้องเขียนกติกานี้ไว้ใน DoD

เปิด PLAB-5 → **Relations → Add relation → Blocked by** → เลือก PLAB-4:

![PLAB-5 แสดง Blocked by PLAB-4](./images/ui-relation-plab5.png)

กลับไป PLAB-4 → **Links → Add link** — Title `commit 3f2a9c1 feat(auth): login form`, URL `https://github.com/<YOUR_ORG>/campuseats/commit/3f2a9c1` (URL ตัวอย่างสำหรับฝึก)

> 📝 **คำอธิบาย:** Plane สร้างคู่กลับให้อัตโนมัติ (PLAB-4 จะแสดง **Blocking** PLAB-5) · link ไป commit/PR คือปลายอีกด้านของ traceability — งานจริงให้ commit message อ้าง `PLAB-4:` แล้ว GitHub/GitLab จะลิงก์กลับได้

หน้า detail ของ PLAB-4 ตอนนี้ครบทุกส่วน:

![หน้า detail ของ PLAB-4: เกณฑ์การยอมรับแบบ checkbox · Sub-work items 1/3 · Relations Blocking PLAB-5 · Links ไป commit](./images/ui-work-item-detail.png)

ตรวจด้วย SQL:

```bash
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select sequence_id, left(name,45) as name, parent_id is not null as sub, priority from issues where project_id=(select id from projects where identifier='PLAB') and deleted_at is null order by sequence_id;"
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select relation_type, (select sequence_id from issues i where i.id=r.issue_id) as issue, (select sequence_id from issues i where i.id=r.related_issue_id) as related from issue_relations r where deleted_at is null;"
```

✅ **Expected output** — PLAB-6..8 เป็น `sub = t` และมี relation `blocked_by` หนึ่งแถว (5 → 4)

```
 sequence_id |                name                | sub | priority 
-------------+------------------------------------+-----+----------
           1 | ตั้งค่า Plane self-host ในเครื่องเรียน   | f   | urgent
           2 | เขียน README ของ LAB ให้ผู้เรียน        | f   | high
           3 | ตรวจว่า 13 container ทำงานครบ       | f   | medium
           4 | นักศึกษาสมัครบัญชีและเข้าสู่ระบบด้วยอีเมล    | f   | high
           5 | แก้บั๊ก                               | f   | none
           6 | ออกแบบฟอร์มสมัคร/เข้าสู่ระบบ (UI)       | t   | none
           7 | API สมัครบัญชีและตรวจโดเมนอีเมล        | t   | none
           8 | เขียน test ครอบคลุมเกณฑ์การยอมรับ 3 ข้อ | t   | none
(8 rows)

 relation_type | issue | related 
---------------+-------+---------
 blocked_by    |     5 |       4
(1 row)
```

---

## 4. Activity คือหลักฐานความรับผิดชอบ

ใน PLAB-4: พิมพ์ comment `เริ่มทำ validation วันนี้` · เปลี่ยน State **Backlog → In Progress** · Assignees = ตัวเอง แล้วเปิดแท็บ **Activity**

![แท็บ Activity ของ PLAB-4 แสดง actor field old → new](./images/ui-activity-log.png)

> 📝 **คำอธิบาย:** ทุกบรรทัดมี **ใคร · ทำอะไร · เมื่อไร** และค่าเก่า → ค่าใหม่ · ถ้าไม่ปรากฏภายในไม่กี่วินาที ให้ดู `pc ps worker` — activity เขียนโดย worker ผ่านคิว `celery` (LAB 2) ไม่ใช่โดย api ทันที

ดูตารางจริง (T1):

```bash
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select field, left(old_value,20) old, left(new_value,20) new, verb from issue_activities where issue_id=(select id from issues where name like 'นักศึกษาสมัครบัญชี%' and project_id=(select id from projects where identifier='PLAB') and deleted_at is null) and deleted_at is null order by created_at;"
```

✅ **Expected output** — แถว `created`, `link`, `blocking`, `comment`, `state Backlog → In Progress`, `assignees` (ถ้าแก้ description หลัง Save จะมีแถว `description` เพิ่ม — ลำดับ/จำนวนแถวของแต่ละคนต่างกันได้ตามที่คลิกจริง):

```
   field   |   old   |         new          |  verb   
-----------+---------+----------------------+---------
           |         |                      | created
 link      |         | https://github.com/< | created
 blocking  |         | PLAB-5               | updated
 comment   |         | <p>เริ่มทำ validatio   | created
 state     | Backlog | In Progress          | updated
 assignees |         | admin                | updated
(6 rows)
```

---

## 5. ทีมโดยไม่มี SMTP — เชิญ dev1 แล้วให้สมัครเอง

ใน B1: **Workspace settings** (sidebar **More** หรือ `http://localhost:8080/devtools-lab/settings/`) → **Members → Add member** → อีเมล `dev1@example.com` role **Member** → **Send invitations**

![modal Invite people to collaborate](./images/ui-invite-modal.png)

✅ **Expected output** — toast **Invitations sent successfully** และส่วน **Pending invites 1** แสดง `dev1@example.com – Pending – Member` (ไม่มีอีเมลถูกส่งจริง — ดู `pc logs worker --tail 5` จะเห็น `Connection refused` ของ SMTP แต่คำเชิญถูกบันทึกแล้ว)

![หน้า Members มี Pending invites และปุ่ม Copy link](./images/ui-members-invite.png)

เมนู ⋯ ของแถวคำเชิญ → **Copy link** → เปิดลิงก์ใน **B2** (private window)

![toast Copied หลังกด Copy link](./images/ui-members-copy-link-toast.png)
![หน้าที่ dev1 เห็นเมื่อเปิดลิงก์เชิญ](./images/ui-invite-landing.png)

dev1 ยังไม่มีบัญชี → ไป `http://localhost:8080/sign-up` กรอก `dev1@example.com` แล้วลองรหัสผ่าน `Password123!` ก่อน:

![ฟอร์ม sign-up กรอก Password123! ก่อนกด Create account — ฝั่ง client ไม่เตือนอะไร](./images/ui-signup-weak-typed.png)
![server ตอบ PASSWORD_TOO_WEAK](./images/ui-signup-weak-password.png)

> 📝 **คำอธิบาย:** ฝั่ง client ตรวจแค่รูปแบบ (8 ตัว มีใหญ่/เล็ก/ตัวเลข/อักขระพิเศษ) แต่ **server ใช้ zxcvbn** ให้คะแนนความคาดเดายาก — `Password123!` ได้คะแนน 1 จึงถูกปฏิเสธ · ใช้ `Member-Lab-2569` (คะแนน 4) แทน — เป็นค่า LAB เท่านั้น

สมัครด้วย `Member-Lab-2569` → onboarding **Create your profile** (ชื่อ `Dev`) → หน้า **Join invites or create a workspace** ติ๊ก DevTools Lab → **Continue**

![ฟอร์ม sign-up กรอก dev1@example.com (อีเมลตามคำเชิญ) และรหัสผ่าน Member-Lab-2569 ก่อนกด Create account](./images/ui-signup-with-invite.png)
![onboarding ของ dev1 — Create your profile](./images/ui-dev1-onboarding-profile.png)
![หน้า Join invites แสดงคำเชิญของ DevTools Lab](./images/ui-join-invites.png)
![ติ๊กคำเชิญแล้วกด Continue](./images/ui-join-invites-checked.png)
![Home ของ dev1 ใน workspace DevTools Lab](./images/ui-dev1-home.png)

กลับ B1 → Members: dev1 เป็น **Member** แล้ว

![หน้า Members หลัง dev1 เข้าร่วม](./images/ui-members-dev1-joined.png)

> 📝 **คำอธิบาย:** คำเชิญค้นด้วยอีเมลจากฐานข้อมูล ไม่ต้องใช้ token ในอีเมล — เมื่อผู้ใช้อีเมลเดียวกันสมัครสำเร็จจะเห็นคำเชิญตอน onboarding (หรือที่ **Settings → Workspace invites**) · sign-up เปิดอยู่โดยปริยาย (god-mode → Authentication) แต่ถึงปิด คนที่ถูกเชิญก็ยังสมัครได้ (ดูทดลองเพิ่มเติม ก.)

ตรวจบทบาทใน SQL แล้วมอบหมาย PLAB-4 ให้ dev1 (B1: Assignees → dev1) → B2 เปิด **Your work** เห็น PLAB-4:

```bash
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select u.email, wm.role from workspace_members wm join users u on u.id=wm.member_id where wm.deleted_at is null and wm.is_active order by role desc;"
```

✅ **Expected output** — `admin@example.com 20`, `dev1@example.com 15` (ถ้าทำ LAB 8 แล้วจะมี bot user เพิ่ม)

```
        email        | role
---------------------+------
 admin@example.com   |   20
 dev1@example.com    |   15
(2 rows)
```

![มอบหมาย PLAB-4 ให้ dev1](./images/ui-assign-dev1.png)
![Your work ของ dev1 แสดง PLAB-4](./images/ui-dev1-your-work.png)

> 📝 **คำอธิบาย:** dev1 ต้องเป็นสมาชิกของ **โปรเจกต์** ด้วยจึงจะถูกมอบหมายได้ — โปรเจกต์ Public จะให้สมาชิก workspace เข้าร่วมเองได้ หรือ admin เพิ่มที่ **Project settings → Members → Add member**

![Project settings → Members → Add member](./images/ui-project-add-member.png)
![รายชื่อสมาชิกของโปรเจกต์ Plane Lab](./images/ui-project-members.png)

---

## 6. Guest — สิทธิ์เท่าที่หน้าที่ต้องการ

B1: **Members → Add member** → `guest@example.com` role **Guest** → **Send invitations** (ไม่ต้องสมัครก็ได้ — ใช้ดูว่า role 5 ถูกบันทึกอย่างไร)

![เชิญ guest@example.com เป็น Guest](./images/ui-invite-guest-modal.png)
![Pending invites มีแถว guest role Guest](./images/ui-members-guest-pending.png)

```bash
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select email, role, accepted from workspace_member_invites where deleted_at is null;"
```

✅ **Expected output** — `guest@example.com` role `5` และ `accepted = f` (ยังไม่ได้รับคำเชิญ):

```
       email       | role | accepted
-------------------+------+----------
 guest@example.com |    5 | f
(1 row)
```

> 📝 **คำอธิบาย:** ตัวเลข role คือสิทธิ์: **20 Admin** ตั้งค่า/เชิญ/ลบ · **15 Member** สร้างและแก้ work item, cycles, pages · **5 Guest** ดูและตอบกลับได้จำกัด (sidebar ไม่มี Analytics/Archives และแท็บ Cycles/Modules ถูกซ่อน) · หลัก **least privilege**: ลูกค้าหรือผู้มีส่วนได้เสียควรเป็น Guest หรือดูผ่านบอร์ดสาธารณะ (LAB 6) ไม่ใช่ Admin

---

## 7. จรรยาบรรณ — เขียนสะท้อนคิดร่วมกันบน Page

B1: **Pages → New page** ชื่อ `Code of Ethics Reflection — LAB 3` วางเนื้อหาจาก `ethics_cases.md` (3 กรณี) → B2 (dev1) เปิดหน้าเดียวกันแล้วเขียน "สิ่งที่มืออาชีพต้องทำเป็นอย่างน้อย" ขณะที่ admin เขียน "หลักการที่ถูกท้าทาย"

![Page สะท้อนคิดในมุมมอง admin](./images/ui-ethics-page-admin.png)
![Page เดียวกันในมุมมอง dev1 ขณะแก้พร้อมกัน](./images/ui-ethics-page-dev1.png)
![Page ที่เขียนครบทั้ง 3 กรณีพร้อมเลขข้อย่อย](./images/ui-ethics-page.png)

> 📝 **คำอธิบาย:** ตัวอักษรของอีกคนโผล่ทันทีเพราะ Pages ใช้ **live server** (WebSocket `/live/`, LAB 2) · เฉลยย่ออยู่ท้าย `ethics_cases.md`: A → Product 3.10 + Management 5.11 (+ Public 1.03) · B → 2.06 + 1.03 + 6.13 · C → 2.05 + 4.01 · กติกา 4 ข้อเมื่อถูกขอให้ทำสิ่งที่ขัดจรรยาบรรณ: **ปฏิเสธพร้อมเหตุผล → เสนอทางเลือก → บันทึกเป็นลายลักษณ์อักษร → รายงานตามลำดับ** — "บันทึก" ใน Plane คือ comment/Page ที่มี actor และเวลา

---

## 8. Token ส่วนตัว — มืออาชีพไม่แชร์รหัสผ่าน

B1: avatar มุมขวาบน → **Settings** → **Developer → Personal Access Tokens** → **Add access token** — Title `lab`, สวิตช์ **Never expires** → **Generate token** → คัดลอก (แสดง **ครั้งเดียว**) → **Close**

![หน้า Personal Access Tokens ยังว่าง](./images/ui-pat-empty.png)
![modal Create token](./images/ui-pat-create-modal.png)
![modal Key created — token แสดงครั้งเดียว ต้องคัดลอกก่อนกด Close](./images/ui-personal-access-token.png)
![รายการ token ชื่อ lab สถานะ Active](./images/ui-pat-list.png)

เก็บ token ในไฟล์ที่อ่านได้เฉพาะเรา แล้วทดสอบ (T1):

```bash
echo '<YOUR_API_TOKEN>' > ~/.plane_token && chmod 600 ~/.plane_token
curl -si http://localhost:8080/api/v1/users/me/ -H "X-API-Key: $(cat ~/.plane_token)" | grep -iE '^HTTP|x-ratelimit'
```

> 📝 **คำอธิบาย:** token ขึ้นต้นด้วย `plane_api_` และ **ทำแทนตัวเรา** (ไม่มี scope ให้เลือก) — จึงห้ามใส่ในโค้ด/ใน readme/ใน chat · `chmod 600` ให้เจ้าของอ่านได้คนเดียว · header `X-API-Key` คือวิธียืนยันตัวของ REST API v1 · `X-RateLimit-Remaining` บอกโควตา 60 ครั้ง/นาที **ต่อ token**

✅ **Expected output** — `200 OK` และ `X-Ratelimit-Remaining: 59` (ใช้ไป 1 จาก 60 ครั้ง/นาที):

```
HTTP/1.1 200 OK
X-Ratelimit-Remaining: 59
X-Ratelimit-Reset: 1788179745
```

เตรียม Python แล้ววัดความครบถ้วนของ backlog:

```bash
python3 -m venv ~/venv-plane && source ~/venv-plane/bin/activate
pip install -r requirements.txt
python lint_work_items.py --project PLAB
```

> 📝 **คำอธิบาย:** `planeapi.py` (ใช้ร่วมกันทุกแล็บถัดไป) อ่าน token จาก `~/.plane_token`, เดิน cursor pagination ให้, และถ้าโดน 429 จะรอตาม `Retry-After` / `X-RateLimit-Reset` เอง — ไฟล์นี้เป็นสำเนาเดียวกันใน LAB 3–7 · `lint_work_items.py` ให้คะแนน 5 ข้อต่อใบ: มีเกณฑ์การยอมรับ (checkbox/หัวข้อ) · มี assignee · priority ≠ none · มี due date · มี label — sub-work item ถูกข้ามเพราะรับบริบทจาก parent

✅ **Expected output** — PLAB-4 ได้ 5/5 · PLAB-5 (`แก้บั๊ก`) ได้ 0/5 · PLAB-1..3 จาก LAB 1 ได้ 1/5 (มีแค่ priority) → ทีมได้ `8/25 (32%)`:

![ผลลัพธ์ lint_work_items.py ก่อนแก้](./images/terminal-lint.png)

```
Work-item hygiene — Plane Lab (PLAB)   token remaining: 31

ID              AC Assignee Priority      Due   Labels   คะแนน  ชื่อ
PLAB-1           ✗        ✗        ✓        ✗        ✗   1/5    ตั้งค่า Plane self-host ในเครื่องเรียน
PLAB-2           ✗        ✗        ✓        ✗        ✗   1/5    เขียน README ของ LAB ให้ผู้เรียน
PLAB-3           ✗        ✗        ✓        ✗        ✗   1/5    ตรวจว่า 13 container ทำงานครบ
PLAB-4           ✓        ✓        ✓        ✓        ✓   5/5    นักศึกษาสมัครบัญชีและเข้าสู่ระบบด้วยอีเมล
PLAB-5           ✗        ✗        ✗        ✗        ✗   0/5    แก้บั๊ก

Team hygiene score: 8/25 (32%)  (ข้าม sub-work item 3 รายการ)
เกณฑ์: AC = มี checkbox หรือหัวข้อ 'เกณฑ์การยอมรับ' ใน description · Priority ≠ none · Due = target_date · Labels ≥ 1
```

แก้ PLAB-5 ให้เป็นมืออาชีพ: เปลี่ยนชื่อจาก `แก้บั๊ก` เป็น `ตะกร้าคำนวณราคาผิดเมื่อมีโปรโมชันซ้อนกัน` · description จากแม่แบบ (ทำซ้ำอย่างไร · เกณฑ์การยอมรับ 10 กรณีทดสอบ · regression test) · Priority **Urgent** · Label **bug** · Assignee dev1 · Due +3 วัน แล้วรันซ้ำ

![PLAB-5 หลังเติมรายละเอียดครบ](./images/ui-plab5-fixed.png)

![ผลลัพธ์ lint_work_items.py หลังแก้ PLAB-5](./images/terminal-lint-after.png)

✅ **Expected output** — PLAB-5 เป็น `5/5` และคะแนนทีมเพิ่มเป็น `13/25 (52%)` (PLAB-1..3 ปล่อยไว้ให้เติมในทดลองเพิ่มเติม จ.):

```
Work-item hygiene — Plane Lab (PLAB)   token remaining: 24

ID              AC Assignee Priority      Due   Labels   คะแนน  ชื่อ
PLAB-1           ✗        ✗        ✓        ✗        ✗   1/5    ตั้งค่า Plane self-host ในเครื่องเรียน
PLAB-2           ✗        ✗        ✓        ✗        ✗   1/5    เขียน README ของ LAB ให้ผู้เรียน
PLAB-3           ✗        ✗        ✓        ✗        ✗   1/5    ตรวจว่า 13 container ทำงานครบ
PLAB-4           ✓        ✓        ✓        ✓        ✓   5/5    นักศึกษาสมัครบัญชีและเข้าสู่ระบบด้วยอีเมล
PLAB-5           ✓        ✓        ✓        ✓        ✓   5/5    ตะกร้าคำนวณราคาผิดเมื่อมีโปรโมชันซ้อนกัน

Team hygiene score: 13/25 (52%)  (ข้าม sub-work item 3 รายการ)
เกณฑ์: AC = มี checkbox หรือหัวข้อ 'เกณฑ์การยอมรับ' ใน description · Priority ≠ none · Due = target_date · Labels ≥ 1
```

---

## 9. ปิดด้วย `check_lab03.sh`

```bash
bash check_lab03.sh
```

> 📝 **คำอธิบาย:** สคริปต์ตรวจจาก **ฐานข้อมูลจริง**: label 4 · sub-work items ≥ 3 · relation `blocked_by` · link ≥ 1 · activity ≥ 3 · role {20,15} · Page จรรยาบรรณ · token ใช้ได้ — พิมพ์ `PASS` บรรทัดเดียวเมื่อครบ (ผู้สอนใช้ให้คะแนนได้ใน 10 วินาที)

✅ **Expected output** — `PASS` บรรทัดเดียว พร้อมตัวเลขที่นับได้จริงจากฐานข้อมูล:

```
PASS: LAB 3 — labels 4 · sub-work items 3 · relation blocked_by 1 · links 1 · activities 9 · roles {15,20} · ethics page 1 · token OK
```

---

## ทดลองเพิ่มเติม

### ก. ปิด sign-up สาธารณะ — คำเชิญยังเปิดทางให้ได้

B1 ไป `http://localhost:8080/god-mode/authentication/` ปิดสวิตช์ **Allow anyone to sign up even without an invite** → B2 (ออกจากระบบก่อน) ลองสมัคร `nobody@example.com`

![god-mode ปิดสวิตช์ sign-up](./images/ui-godmode-signup-off.png)
![หน้า sign-up แจ้ง SIGNUP_DISABLED](./images/ui-signup-disabled.png)

✅ **Expected output** — ข้อความ **SIGNUP_DISABLED** · จากนั้น B1 เชิญ `nobody@example.com` แล้วสมัครใหม่ → ผ่าน (กติกา: ไม่มีคำเชิญ = ห้าม, มีคำเชิญ = ได้) · **เปิดสวิตช์คืน** ก่อนไปข้ออื่น

### ข. เลขงานไม่ถูกใช้ซ้ำ

ลบ work item ใบใดใบหนึ่งที่สร้างทดสอบ (เมนู ⋯ → Delete) แล้วสร้างใหม่:

![เลข work item ใหม่ข้ามเลขที่ถูกลบ](./images/ui-sequence-never-reused.png)

```bash
pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c \
 "select sequence, deleted from issue_sequences where project_id=(select id from projects where identifier='PLAB') order by sequence desc limit 4;"
```

✅ **Expected output** — แถวของเลขที่ลบมี `deleted = t` และใบใหม่ได้เลขถัดไป ไม่ย้อนกลับมาใช้เลขเดิม (audit trail ไม่หาย)

### ค. rate limit ของการ sign-in (ทางเลือก)

```bash
bash auth_rate_limit.sh
```

✅ **Expected output** — 10 ครั้งแรกถูก redirect กลับพร้อม `AUTHENTICATION_FAILED` ครั้งที่ 11 กลายเป็น **429** (`AUTHENTICATION_RATE_LIMIT=10/minute`) — ป้องกันการเดารหัสผ่าน

### ง. sub-work items เสร็จหมด แต่ parent ไม่ Done เอง

ย้าย sub-work items ทั้ง 3 ใบ (PLAB-6..8 ในภาพ) เป็น Done → PLAB-4 แสดง 3/3 (100%) แต่ state ของ PLAB-4 ยังเป็น In Progress

![Sub-work items 3/3](./images/ui-subitems-3of3.png)

> 📝 **คำอธิบาย:** Plane ไม่ปิด parent ให้ เพราะ "งานย่อยเสร็จ" ไม่เท่ากับ "เกณฑ์การยอมรับผ่าน" — ทีมต้องเขียนไว้ใน DoD ว่าใครเป็นคนปิด parent และตรวจอะไรก่อน

### จ. ทำ backlog ทั้งชุดให้ได้ 100%

เติม PLAB-1..3 ตามแม่แบบ แล้ว `python lint_work_items.py --project PLAB` จนคะแนนทีม 25/25 — เป็น "Definition of Ready" ที่ LAB 5 จะใช้

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| Activity ไม่ขึ้นหลังเปลี่ยน state | worker ไม่ทำงาน — activity เขียนผ่านคิว `celery` | `pc ps worker` ต้อง Up; `pc start worker` แล้วรอ 10 วินาที (LAB 2) |
| เปิดลิงก์เชิญแล้วเจอหน้า sign-in / "not for you" | อีเมลที่ล็อกอินไม่ตรงกับคำเชิญ หรือยังไม่มีบัญชี | สมัครด้วยอีเมลเดียวกับคำเชิญก่อน แล้วรับที่หน้า Join invites หรือ Settings → Workspace invites |
| B2 กลายเป็น admin | ไม่ได้ใช้ private window จึงใช้ cookie ร่วมกับ B1 | เปิด private/incognito หรือใช้โปรไฟล์เบราว์เซอร์แยก |
| `Password123!` ผ่านฝั่ง client แต่ server ปฏิเสธ | zxcvbn ให้คะแนน 1 (< 3) | ใช้รหัสผ่านที่คาดเดายาก เช่น `Member-Lab-2569` (ค่า LAB) |
| `curl … users/me/` ตอบ **401** | ไม่ได้ส่ง header `X-API-Key` (ชื่อ header ผิด/ค่าว่าง) | ใช้ `-H "X-API-Key: $(cat ~/.plane_token)"` และตรวจว่าไฟล์ไม่ว่าง |
| `curl … users/me/` ตอบ **403** `Given API token is not valid` | token พิมพ์ผิด/หมดอายุ/ถูกปิด | สร้าง token ใหม่แล้วเขียนทับ `~/.plane_token` (LAB 2 ใช้พฤติกรรม 403 นี้พิสูจน์ว่า DB ตอบ) |
| `ModuleNotFoundError: requests` | ยังไม่ activate venv | `source ~/venv-plane/bin/activate` ทุก terminal ใหม่ |
| `psql: fe_sendauth: no password supplied` | ลืม `-e PGPASSWORD=plane` | ใช้คำสั่งตามเอกสาร (`pc exec -T -e PGPASSWORD=plane plane-db psql …`) |
| มอบหมาย dev1 ไม่ได้ | dev1 ยังไม่เป็นสมาชิกโปรเจกต์ | Project settings → Members → Add member |

---

## เก็บกวาด (Cleanup)

แล็บนี้ **ไม่ลบอะไร** — label, ใบดี/ใบไม่ดีที่แก้แล้ว (PLAB-4/5 ในภาพ), dev1, Page และ token ถูกใช้ต่อใน LAB 4–9 · ปิด B2 ได้ · ถ้าจบวัน: `pc stop` (ข้อมูลอยู่ใน volume) และ **Stop Forwarding Port** 8080

```bash
pc ps --format 'table {{.Name}}\t{{.Status}}' | grep -c Up
```

✅ **Expected output** — `12` (Plane ยังรันครบสำหรับแล็บถัดไป)

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -c "…"` | สอบถามฐานข้อมูลของ Plane โดยตรง (labels, issues, issue_relations, issue_activities, workspace_members) |
| `echo '<YOUR_API_TOKEN>' > ~/.plane_token && chmod 600 ~/.plane_token` | เก็บ Personal Access Token อย่างปลอดภัย |
| `curl -si …/api/v1/users/me/ -H "X-API-Key: $(cat ~/.plane_token)"` | ทดสอบ token และดู rate-limit header |
| `python lint_work_items.py --project PLAB` | ให้คะแนนความครบถ้วน (hygiene) ของ work item ทั้งโปรเจกต์ |
| `bash auth_rate_limit.sh` | สาธิต AUTHENTICATION_RATE_LIMIT (10/นาที) |
| `bash check_lab03.sh` | ด่านหลักฐานของแล็บ — ต้องได้ `PASS` |

> **จำให้ขึ้นใจ:** ชื่อ = ผลลัพธ์ที่ผู้ใช้ได้ · เกณฑ์การยอมรับต้องทดสอบได้ · ฟิลด์ว่างคือคำถามที่เพื่อนต้องเสียเวลาถาม · token คือตัวเรา ห้ามแชร์

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] label `bug` `feature` `docs` `tech-debt` ครบ 4 ใน SQL
- [ ] PLAB-4 มีเกณฑ์การยอมรับแบบ checkbox · priority · label · due date · assignee
- [ ] sub-work items 3 ใบ และวงกลมความคืบหน้าเปลี่ยนเมื่อปิดงานย่อย
- [ ] PLAB-5 **Blocked by** PLAB-4 และ PLAB-4 แสดง **Blocking**
- [ ] link ไป commit อยู่ใน Links ของ PLAB-4
- [ ] Activity แสดง state · assignees · comment พร้อม actor
- [ ] dev1 เข้าร่วมผ่าน Copy link + Join invites โดยไม่มีอีเมล และเป็น role 15
- [ ] เห็น `PASSWORD_TOO_WEAK` จาก `Password123!`
- [ ] guest@example.com ถูกบันทึกเป็น role 5 ใน `workspace_member_invites`
- [ ] Page สะท้อนคิดตอบครบ 3 กรณีพร้อมเลขข้อย่อย และเห็นการแก้พร้อมกัน
- [ ] `~/.plane_token` มีสิทธิ์ 600 และ `users/me/` ตอบ 200 พร้อม `X-RateLimit-Remaining`
- [ ] `lint_work_items.py` — ใบ "แก้บั๊ก" จาก 0/5 เป็น 5/5 หลังแก้
- [ ] `bash check_lab03.sh` ได้ `PASS`

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` (Plane v1.4.2) เมื่อ 31 ส.ค. 2026*
