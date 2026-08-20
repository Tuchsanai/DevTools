# Prompt: สื่อการสอน CI/CD Jenkins บน Docker (HTML Slide + LAB)

## เป้าหมาย
สื่อการสอนภาษาไทย **CI/CD ด้วย Jenkins บน Docker** = HTML slide 1 ไฟล์ + LAB ไม่เกิน 7 ที่รันได้จริง
**Phase 5 (ปัจจุบัน): ย้าย SCM ทั้งชุดจาก Gitea → GitHub.com เท่านั้น** — แผน/contract อยู่ที่ `docs/PLAN_P5_GITHUB.md`

## Setup (ค่าจริงใช้ตอนรันเท่านั้น — ห้ามปรากฏในไฟล์/เอกสาร/log/commit)
```
git config user.name/user.email · export GIT_TOKEN=<GITHUB_TOKEN>
echo "<DOCKER_TOKEN>" | docker login -u <DOCKER_USER> --password-stdin
```
ค่าจริงเก็บนอก git เท่านั้น (เช่น `backup/xprompt1.md` ซึ่งถูก ignore) — `prompt.md` ไฟล์นี้ถูก track จึงต้องเป็น placeholder ล้วนเสมอ

## การจำลองและทดสอบ LAB
ตั้งชื่อ container `devtools-<ชื่อการทดลอง>` และแยก port ต่อการทดลอง (2222, 2223, …)

```bash
docker rm -f devtools-<ชื่อการทดลอง> 2>/dev/null                 # 1. ลบของเดิม
docker run -dit --name devtools-<ชื่อการทดลอง> --privileged \
  --tmpfs /run -v <ชื่อ>-dind:/var/lib/docker \
  -p 2222:22 tuchsanai/devtools:2569_1                            # 2. รัน (DinD ต้องมี --tmpfs /run + volume)
ssh root@localhost -p 2222                                        # 3. เข้าใช้ (password: passwd)
docker rm -f devtools-<ชื่อการทดลอง>                              # 4. จบแล้วลบทุกครั้ง
```

ตรวจไม่ให้มี container ค้าง: `docker ps -a --filter "name=^devtools-"` ต้องว่าง
รวมกันทุก agent **ไม่เกิน 7 container** · แต่ละ agent **ลบ container ของตัวเองก่อนส่งงาน**

## เครื่องมือ
- **Excalidraw MCP** — วาด diagram ประกอบการสอน
- **Playwright CLI** (host, `/opt/venv`) — ขับ UI จริง + capture screenshot
- **ffmpeg** — ตัดเฟรม ครอป ย่อ · **ChatGPT vision (Codex)** — งานภาพ/gen รูปที่จำเป็น
- **Remotion Agent Skills** — สร้างวิดีโอสอน render ด้วย `npx remotion render`

## Goal Phase 5 (Gitea → GitHub)
- LAB 4–6 ใช้ **GitHub.com เท่านั้น**: repo public `<GITHUB_USER>/hello-ci`, `<GITHUB_USER>/webapp` · Jenkins checkout ผ่าน `https://github.com/...` ไม่ใช้ credential · PAT (scope `repo`) เป็น prerequisite ก่อนคาบ
- **Webhook ข้าม NAT ด้วย smee.io** (พิสูจน์แล้ว 2026-08-20): GitHub → `<SMEE_URL>` → container `smee-hello`/`smee-webapp` (image lock `deltaprojects/smee-client@sha256:20ea24c8...`) → `http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-*`
- ทุกขั้น UI: ลำดับคลิก + **screenshot จริง + marker** (กรอบแดง + เลขลำดับ + ป้ายไทยสั้น) + caption — ห้ามขาดช่วง
  - หน้า GitHub ที่ต้อง login (ฟอร์ม New repo / Add webhook) capture จริงไม่ได้ (ไม่มี web session) → ใช้ **Codex gen รูป** ตามค่าจริงทุก field และขึ้นทะเบียนใน `docs/INTEGRATION.md`
  - screenshot จริงที่ติด username จริง → **mask เป็น `<GITHUB_USER>`** ด้วย annotation pipeline
- **คำสั่งในเอกสารต้องเรียบง่าย**: ห้าม `--format`/`--filter`/pipe ซับซ้อนที่ไม่ใช่หัวใจแล็บ · clone แบบ `git clone --depth 1` ธรรมดา (เลิก sparse-checkout, เลิก `grep -qxF`) · ทุก command block ตามด้วย ✅ expected output จากผลรันจริง · code ให้ตัวเต็ม copy-paste ได้
- จบงาน: gates ทั้งสาม (deck_offline / deck_consistency / int_consistency) exit 0 · ไม่มี container/volume/repo ทดสอบค้าง (repo ทดสอบบนบัญชีจริงต้องลบ ยกเว้นมีอยู่ก่อนแล้ว)

## Slide
- ไฟล์เดียว, CSS/JS inline, **ห้าม CDN** · ภาษาไทยกระชับ แบ่งเป็นตอน เชื่อมกับ LAB
- หน้า overview + เลขหน้า + diagram (inline SVG) + code snippet
- ฝัง**วิดีโอ Remotion** เป็น data URI, autoplay(muted) เฉพาะหน้าที่แสดง
- Phase 5: แก้ตอน 5.2/5.3 (Gitea→GitHub+smee), SVG d7/d8, สลับ screenshot ฝัง แล้วปรับค่าคงที่ deck_offline ให้ตรง

## LAB (`001_LAB_...` → สูงสุด `007_LAB_...`)
- รันจริงบน `tuchsanai/devtools:2569_1` (--privileged, ssh root/passwd) · ทุกแล็บมี `README.md` + `check.sh` (exit code)
- **push image ขึ้น Docker Hub จริง + capture หน้า Hub (public/anonymous) เป็นหลักฐาน**
- **ทดลองกับ GitHub จริง + capture หน้าเป็นหลักฐาน** (mask username จริงเสมอ)
- LAB ที่มี web UI → ออกแบบให้ **Wow**
- 1 Codex agent / 1 LAB (รวม ≤7 container ชื่อ `devtools-<ชื่อ>` แยกพอร์ตไม่ชนกัน) · **ลบ container ตัวเองก่อนส่งงาน**

## มาตรฐานเอกสาร LAB
- **โทนวิชาการ** (ไม่ใช้ภาษาแนวเพื่อน) · 1 การทดลอง = 1 คำถาม = 1–2 คำสั่ง = 1 สิ่งที่ต้องสังเกต (`✅` จากผลรันจริง)
- ทุกขั้น UI: ลำดับคลิก + **screenshot จริง + marker** + caption — ขั้นตอนห้ามขาดช่วง
- placeholder เท่านั้น (`<DOCKER_USER>` `<DOCKER_TOKEN>` `<GITHUB_USER>` `<GITHUB_TOKEN>` `<SMEE_URL>`) — ห้าม email/ชื่อ/token จริง
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
