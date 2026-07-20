# PROMPT: สร้างสไลด์สอน Git Worktree

> วางข้อความด้านล่างนี้ทั้งหมดเป็น prompt เดียว

---

## บทบาท

คุณคือผู้ช่วยออกแบบสื่อการสอนวิชา Git/DevTools ระดับมหาวิทยาลัย
ภารกิจ: ออกแบบ **เนื้อหาสไลด์สอนเรื่อง Git Worktree** ภาษาไทยปน technical term ภาษาอังกฤษ

---

## 0. อ่านพื้นความรู้เดิมของนักศึกษาก่อน (บังคับ — ทำก่อนเขียนสไลด์)

**ห้ามเริ่มเขียนสไลด์จนกว่าจะอ่านไฟล์เหล่านี้ครบ** ไฟล์ `.html` ต่อไปนี้คือ *ทุกอย่างที่นักศึกษาเคยเรียนมาแล้ว* — คือ ground truth ของ prior knowledge ไม่ใช่แค่ข้อมูลอ้างอิง:

| ไฟล์ | เนื้อหาที่นักศึกษาผ่านมาแล้ว |
|---|---|
| `01_GIT/00_LAB_git_configure/README.html` | ตั้งค่า Git (config, identity) |
| `01_GIT/01_LAB_gitignore/README.html` | `.gitignore` |
| `02_GIT/git_week2.html` | สไลด์ Week 2 (ภาพรวม) |
| `02_GIT/00_LAB_add_commit_status/README.html` | add · commit · status (local workflow) |
| `02_GIT/01_LAB_push_to_github/README.html` | push ขึ้น GitHub (remote) |
| `02_GIT/02_LAB_fetch_pull/README.html` | clone / fetch / pull |

**สิ่งที่ต้องทำหลังอ่าน:**

1. สรุป (ใน 5–8 bullet ก่อนขึ้นสไลด์แรก) ว่านักศึกษา *รู้อะไรมาแล้ว* และ *ยังไม่รู้อะไร* จากไฟล์เหล่านี้
2. **สืบทอด design language และ HTML/CSS structure จากไฟล์เดิม** — ถ้า output เป็น `.html`
   ต้องใช้ theme เดียวกัน: dark GitHub palette (`--bg:#0d1117`, `--accent:#f05133`, `--accent2:#58a6ff`),
   sidebar nav แบบ sticky, hero header, section แบบมี `.sec-num`, `"Noto Sans Thai"` font stack, single-file self-contained
3. **สืบทอด pedagogy pattern เดิม** — ตั้งชื่อบทแบบมี narrative hook (เช่น "LAB 00 — The Time Machine")
   และมีโครงสร้าง LAB ที่มีเกณฑ์ตรวจสอบผลลัพธ์
4. **ห้ามสอนซ้ำ** สิ่งที่มีอยู่ในไฟล์เหล่านี้แล้ว — อ้างอิงสั้น ๆ ได้ ("จาก LAB 02 ที่เคยทำ…") แต่ไม่อธิบายใหม่

---

## 1. ระดับผู้เรียน (ข้อจำกัดเด็ดขาด)

- **รู้แล้ว:** clone, add, commit, status, push, fetch, pull, branch, merge, .gitignore
- **ยังไม่เคยเรียน:** `git stash`, `git worktree`, `git rebase`, `git reflog`
- 🚫 **ห้ามใช้ ห้ามเอ่ยถึง ห้ามเปรียบเทียบกับ `git stash` ในทุกสไลด์ ทุก speaker note และทุก code block**
  (ถ้าเจอจุดที่ "โดยธรรมชาติควรพูดถึง stash" ให้อธิบายปัญหาโดยไม่เสนอ stash เป็นทางออก)
- ถ้าจำเป็นต้องใช้คำสั่งนอกรายการ "รู้แล้ว" ต้องอธิบายคำสั่งนั้นสั้น ๆ ก่อนใช้

---

## 2. Scenario กลาง (ใช้ต่อเนื่องทุกสไลด์ — ห้ามเปลี่ยน repo กลางคัน)

- repo ชื่อ **`demo-worktree`** อยู่ที่ **`~/work/demo-worktree`**
- branch: `main`, `dev`, `feature/login` — แต่ละ branch มีไฟล์/commit ต่างกัน **ชัดเจนพอที่จะเห็นความต่างเมื่อสลับ worktree**
- **local repo ล้วน ไม่ต้องใช้ GitHub จริง**
- Setup script ต้อง **รันได้จริงทั้งชุดใน code block เดียว (bash)** copy-paste ครั้งเดียวจบ
  - ต้อง idempotent: ขึ้นต้นด้วยการลบ/เตือนถ้ามี directory เดิม
  - ตั้ง `git config user.name/user.email` ระดับ local ในสคริปต์ เพื่อให้ commit ผ่านแน่นอน
  - ตั้ง `git init -b main` เพื่อไม่ให้ชนกับ default branch ของเครื่องผู้เรียน
- ทุกคำสั่งหลังจากนี้ต้องอ้างอิง path และชื่อ branch ชุดเดียวกันนี้เท่านั้น

---

## 3. โครงเนื้อหา (เรียงตามลำดับนี้)

1. **Setup** — script สร้าง repo + ตรวจสอบความพร้อม (`git branch -a`, `git log --oneline --all --graph`)
2. **ปัญหาของวิธีเดิม** — ทำไม `git checkout` / `git switch` สลับ branch ไปมาถึงไม่สะดวก
   แสดงสถานการณ์จริง: มี uncommitted changes ค้าง → switch ไม่ได้ หรือไฟล์ติดข้ามไปด้วย
   (อธิบาย *ปัญหา* เท่านั้น ยังไม่เฉลยทางแก้ และ **ห้ามพูดถึง stash**)
3. **Git Worktree คืออะไร** — concept + ASCII diagram: 1 `.git` : หลาย working directory
4. **คำสั่งหลัก** (แยกสไลด์ตามคำสั่ง) — `git worktree add` (branch เดิม / `-b` branch ใหม่),
   `git worktree list`, `git worktree remove`, `git worktree prune`
5. **Workflow step-by-step** — แก้ hotfix บน `main` ขณะที่งาน `feature/login` ยังค้างอยู่ → merge → เก็บกวาด worktree
6. **Use case กับ AI coding agent** — รัน agent หลายตัวคนละ worktree พร้อมกัน (เช่น Claude Code)
7. **ข้อควรระวัง / limitation** — branch เดียว checkout ซ้ำไม่ได้, shared `.git`, `node_modules` / venv ต่อ worktree, การลบ directory ทิ้งมือเปล่า ๆ แล้วต้อง prune
8. **Hands-on lab สั้น ๆ** — ขั้นตอน + **เกณฑ์เช็คว่าทำสำเร็จ (checklist ที่ตรวจได้ด้วยคำสั่ง)**
9. **คำถามทบทวน 3–5 ข้อ พร้อมเฉลย** (เฉลยแยกสไลด์หรือพับซ่อน)

---

## 4. Format ที่ต้องการ

- แบ่งเป็นสไลด์: `Slide N: <title>` ตามด้วย bullet points
- **1 สไลด์ = 1 ประเด็น, ไม่เกิน 6 bullets ต่อสไลด์**
- **ทุกคำสั่งอยู่ใน code block พร้อม expected output** (ใส่ output จริงที่ควรเห็น ไม่ใช่ placeholder)
- รวม **15–20 สไลด์**
- ทุกสไลด์มี **speaker notes สั้น ๆ 2–3 บรรทัด** (สิ่งที่ผู้สอนควรพูด/เน้น/ระวัง)
- ภาษาไทย + technical term ภาษาอังกฤษคงรูป (worktree, branch, commit — ไม่ต้องแปล)

---

## 5. Output

สร้างไฟล์ `03_GIT/git_worktree.html` (หรือ path ที่ระบุ) เป็น **single-file HTML self-contained**
ที่ใช้ theme และ layout เดียวกับไฟล์ใน §0 — เปิดในเบราว์เซอร์ได้ทันทีโดยไม่ต้องมี asset ภายนอก

---

## 6. Self-check ก่อนส่ง (ทำแล้วรายงานผลเป็น checklist)

- [ ] ค้นคำว่า `stash` ทั้งไฟล์ → ต้องเจอ **0 ครั้ง**
- [ ] Setup script รันได้จริงตั้งแต่บรรทัดแรกถึงบรรทัดสุดท้ายบนเครื่องเปล่า
- [ ] ทุก path/branch สอดคล้องกับ scenario `~/work/demo-worktree` ตลอดทั้งไฟล์
- [ ] ทุก code block มี expected output
- [ ] ไม่มีสไลด์ไหนเกิน 6 bullets
- [ ] ไม่มีการสอนซ้ำเนื้อหาที่อยู่ในไฟล์ `.html` ตาม §0
- [ ] จำนวนสไลด์อยู่ในช่วง 15–20
