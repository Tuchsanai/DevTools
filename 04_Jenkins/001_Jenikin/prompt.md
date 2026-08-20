# Prompt: สื่อการสอน CI/CD Jenkins บน Docker (HTML Slide + LAB)

## เป้าหมาย
สื่อการสอนภาษาไทย **CI/CD ด้วย Jenkins บน Docker** = HTML slide 1 ไฟล์ + LAB ไม่เกิน 7 ที่รันได้จริง

## Setup (ค่าจริงใช้ตอนรันเท่านั้น — ห้ามปรากฏในไฟล์/เอกสาร/log)
```
git config user.name/user.email · export GIT_TOKEN=<GIT_TOKEN>
echo "<DOCKER_TOKEN>" | docker login -u <DOCKER_USER> --password-stdin
```

## Slide
- ไฟล์เดียว, CSS/JS inline, **ห้าม CDN** · ภาษาไทยกระชับ แบ่งเป็นตอน เชื่อมกับ LAB
- หน้า overview + เลขหน้า + diagram (inline SVG) + code snippet
- ฝัง**วิดีโอ Remotion** เป็น data URI, autoplay(muted) เฉพาะหน้าที่แสดง

## LAB (`001_LAB_...` → สูงสุด `007_LAB_...`)
- รันจริงบน `tuchsanai/devtools:2569_1` (--privileged, ssh root/passwd) · ทุกแล็บมี `README.md` + `check.sh` (exit code)
- **push image ขึ้น Docker Hub จริง + capture หน้า Hub เป็นหลักฐาน**
- LAB ที่มี web UI → ออกแบบให้ **Wow**
- 1 Codex agent / 1 LAB (รวม ≤7 container ชื่อ `devtools-<ชื่อ>` แยกพอร์ตไม่ชนกัน) · **ลบ container ตัวเองก่อนส่งงาน**

## มาตรฐานเอกสาร LAB
- **โทนวิชาการ** (ไม่ใช้ภาษาแนวเพื่อน) · 1 การทดลอง = 1 คำถาม = 1–2 คำสั่ง = 1 สิ่งที่ต้องสังเกต (`✅` จากผลรันจริง)
- ทุกขั้น UI: ลำดับคลิก + **screenshot จริง + marker** (กรอบแดงล้อมจุดคลิก + เลขลำดับ + ป้ายไทยสั้น) + caption — ขั้นตอนห้ามขาดช่วง
- placeholder เท่านั้น (`<DOCKER_USER>` `<DOCKER_TOKEN>`) — ห้าม email/ชื่อ/token จริง
- ห้ามหัวข้อ "ทำให้พัง" — error ไว้ในตาราง "แก้ปัญหาที่พบบ่อย"

## Collaborative Workflow
**Claude = Lead Architect** (ออกแบบ/แบ่ง unit/กำหนด interface+DoD/ตัดสิน — ไม่เขียนโค้ดเอง) · **Codex = Builder+Critic** (สร้าง+รันจริง+critique — ห้ามเปลี่ยน scope เอง)

**การแบ่งงานตาม token:** Claude ตรวจเฉพาะ **text** (เอกสาร/โค้ด/log ช่วงสั้น) — งานที่ต้องเข้าใจ**รูปภาพ/วิดีโอ** หรืองานอ่านหนักที่กิน token เยอะ (log ยาว, ไฟล์ใหญ่, ไล่ดูภาพหลายไฟล์) ให้มอบ `cyolo` (gpt-5.6-sol / medium — ยกระดับ effort เฉพาะงานยาก) แล้ว Claude อ่านเฉพาะรายงานสรุป

1. **Plan** — Claude (xhigh) ร่าง architecture+interface map+DoD → Codex `/cyolo` (max) critique: `assumption|dependency|scope|interface|feasibility|DoD` → Claude ตัดสินทีละข้อ `ACCEPT|PARTIAL|REJECT` ลง ledger → freeze
2. **Build & Test** — Codex (high) fan-out ต่อ unit · log เต็มที่ `logs/<unit_id>.log` · ห้าม PASS โดยไม่รันจริง · Return: `status | unit_id | งานที่ทำ | files | command+exit code | DoD | risk | pending`
3. **Integrate** — รัน chain จริงทั้งชุด + ตรวจ naming/links/ports/Slide↔LAB · รอยต่อพัง → ตีกลับเฉพาะ unit พร้อมหลักฐาน
4. **Review & Fix** — Claude ตรวจ DoD+สุ่ม verify log → Codex (max) adversarial review → Claude ตัดสิน `PASS|FIX|REPLAN` → Codex (high) แก้+re-run (วนได้ ≤3 รอบ; ผิดเชิงโครงสร้าง → กลับข้อ 1)

## Rules
Evidence > Opinion · `PASS` ต้องมี exit code + log + DoD ครบ · 1 LAB/1 agent scope ไม่ซ้อน · Claude ต้องตอบทุก blocker critique · ห้ามข้าม Integration Test · จบงานต้องไม่มี container/volume/test artifact ค้าง
