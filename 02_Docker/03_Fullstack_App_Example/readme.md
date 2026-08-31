# Fullstack App Example — SkillSpace

ชุดเรียนนี้ใช้ระบบแจ้งซ่อม **SkillSpace** เพื่อเชื่อมแนวคิด Requirement, User Flow, Architecture และ Docker และต่อยอดสู่การออกแบบระบบจองนัดหมายสัตวแพทย์ใน LAB 003

## เส้นทางการเรียน

| LAB | โฟลเดอร์ | เป้าหมาย |
|---|---|---|
| 001 | [`001_LAB_PostgreSQL`](./001_LAB_PostgreSQL/readme.md) | สร้างฐานข้อมูล `skillspace`, schema 5 ตาราง, seed และเชื่อมต่อด้วย Python |
| 002 | [`002_LAB_Fullstack_Compose`](./002_LAB_Fullstack_Compose/readme.md) | เปิดระบบ `web + api + db` ด้วย Docker Compose และทดลอง Flow ระบบแจ้งซ่อมทั้งชุด |
| 003 | [`003_LAB_Pet_Clinic_Design`](./003_LAB_Pet_Clinic_Design/readme.md) | สกัด Evidence, Story และ Requirement เพื่อออกแบบ User Flow, หน้าจอ, Feature และ System Design |

```text
LAB 001                         LAB 002                              LAB 003
PostgreSQL + schema + seed  →  Browser → web → api → db + volume  →  Evidence → Flow → System Design
```

## สิ่งที่ผู้เรียนจะพิสูจน์

- สร้างใบแจ้งซ่อมและเดิน State `NEW → ASSIGNED → IN_PROGRESS → DONE`
- มอบหมายงานให้ช่างและกรองงานตามผู้รับผิดชอบ
- ป้องกันการยืมครุภัณฑ์ที่ถูกยืมหรืออยู่ระหว่างซ่อม
- เบิกอะไหล่และตรวจรายการต่ำกว่าจุดสั่งซื้อ
- เปิดระบบ 3 service ด้วยคำสั่ง Compose เดียว
- ให้ Container ติดต่อกันด้วยชื่อ `web`, `api`, `db`
- เปิดพอร์ตเฉพาะ web และเก็บข้อมูลใน named volume

## เอกสารประกอบ

| รายการ | คำอธิบาย |
|---|---|
| [`Fullstack_Slides.html`](./Fullstack_Slides.html) | เนื้อหาสอน Requirement, User Flow, Architecture และจุดเริ่มต้นของแล็บ |
| [`docs/00_story.md`](./docs/00_story.md) | เรื่องราวและปัญหาของผู้ใช้ |
| [`docs/01_requirements.md`](./docs/01_requirements.md) | Functional และ Non-functional Requirements |
| [`docs/02_contract.md`](./docs/02_contract.md) | API, State และ error contract |
| [`app/`](./app/) | reference implementation ของระบบเต็มชุด |

## เตรียมเครื่องเรียน

แต่ละแล็บรันใน Docker-in-Docker Container แยกกัน:

| LAB | Container | SSH | หน้าเว็บ |
|---|---|---:|---:|
| 001 | `devtools-fs-lab1` | `2251` | — |
| 002 | `devtools-fs-lab2` | `2252` | `8252` |

ตัวอย่าง:

```bash
docker run -dit --name devtools-fs-lab2 --privileged \
  -p 2252:22 -p 8252:3000 <LAB_IMAGE>
ssh root@localhost -p 2252
```

> `--privileged` ใช้เฉพาะ Container สำหรับเรียนแบบใช้แล้วทิ้ง ไม่ใช่ production workload

## ตรวจงาน

รันจากโฟลเดอร์ของแต่ละแล็บ:

```bash
bash verify.sh
echo "exit code = $?"
```

ผ่านครบจะพิมพ์ `ALL CHECKS PASSED` และคืน exit code `0`

## ขอบเขต

- ระบบนี้เป็นกรณีศึกษา ไม่มี login และ role-based access control
- รหัสผ่านในไฟล์เป็นค่าสำหรับห้องเรียน งานจริงต้องใช้ secret management
- named volume ช่วยให้ข้อมูลอยู่รอดจากการสร้าง Container ใหม่ แต่ไม่ใช่ backup
- ระบบทั้งหมดอยู่บนเครื่องเดียว จึงยังไม่ใช่ High Availability
- `healthcheck` และ `depends_on` ช่วยลำดับเริ่มต้น แต่ application ยังควรมี retry เมื่อ service ล้มภายหลัง

## เก็บกวาด

```bash
docker rm -f devtools-fs-lab1 devtools-fs-lab2 2>/dev/null || true
docker ps -a --filter "name=devtools-fs-lab"
```
