# PROMPT สำหรับ claude.ai/design — สไลด์สอน Git Worktree

> **วิธีใช้:** copy ทุกอย่างใต้เส้นคั่นด้านล่าง วางใน https://claude.ai/design
> (prompt นี้ self-contained — ไม่ต้องแนบไฟล์ เพราะฝัง prior knowledge ไว้ครบแล้ว)

---

สร้าง **สไลด์บรรยาย 16:9 จำนวน 15–20 สไลด์** เรื่อง **Git Worktree** สำหรับนักศึกษามหาวิทยาลัย
ภาษาไทย + technical term ภาษาอังกฤษคงรูป (worktree, branch, commit, merge — ไม่ต้องแปล)

## 1. พื้นความรู้ของผู้เรียน (สำคัญมาก — ห้ามสอนซ้ำ)

นักศึกษาผ่าน 2 สัปดาห์แรกของวิชานี้มาแล้ว **สอนซ้ำสิ่งเหล่านี้ไม่ได้ อ้างอิงสั้น ๆ ได้เท่านั้น:**

**Week 1**

- `git config` ระดับ global/local, identity, `init.defaultBranch`
- `.gitignore` — ทำให้ `git status` สะอาด, ไฟล์ถูกซ่อนไม่ใช่หาย

**Week 2**

- 3 พื้นที่ของ Git: Working Directory → Staging Area → Repository
- `git add` / `git commit` / `git status` / `git log` / `git diff`
- commit = snapshot ของทั้งโปรเจกต์, commit anatomy
- `master` vs `main`, `git branch -M main`
- `git remote add origin`, `git push -u`, PAT token
- `git clone`, `origin/main` เป็น bookmark ที่เลื่อนเองไม่ได้, ahead/behind
- `git fetch` vs `git pull`, `git merge origin/main`
- `git checkout <commit>` + detached HEAD (เคยเห็นผ่าน ๆ แล้ว)

**ยังไม่เคยเรียนเลย:** `git stash`, `git worktree`, `git rebase`, `git reflog`
รวมถึงยังไม่เคย **สร้าง branch ของตัวเองแล้ว merge กันเอง** อย่างเป็นเรื่องเป็นราว —
ถ้าใช้ `git switch -c` / `git merge <branch>` ให้อธิบายสั้น ๆ ก่อนใช้ครั้งแรก

### 🚫 ข้อห้ามเด็ดขาด

**ห้ามเอ่ยถึง `git stash` เลยแม้แต่ครั้งเดียว** — ห้ามในสไลด์ ห้ามใน code block ห้ามใน speaker notes
ห้ามแม้แต่ในประโยคเปรียบเทียบทำนอง "ต่างจาก stash ตรงที่…"
เมื่อถึงจุดที่ปัญหา uncommitted changes โผล่มา ให้อธิบาย **ตัวปัญหา** อย่างเดียว
แล้วเดินเรื่องไปสู่ worktree โดยตรง

## 2. Scenario กลาง (ใช้ตลอดทั้ง deck ห้ามเปลี่ยน repo กลางคัน)

- repo ชื่อ **`demo-worktree`** ที่ **`~/work/demo-worktree`**
- 3 branch: `main`, `dev`, `feature/login` — แต่ละ branch มีไฟล์/commit ต่างกันชัดเจน
- **local repo ล้วน — ไม่ต้องใช้ GitHub จริง**
- ทุก path, ชื่อ branch, ชื่อไฟล์ในทุกสไลด์ต้องสอดคล้องกับ scenario นี้ 100%

## 3. โครงสไลด์

| # | เนื้อหา |
|---|---|
| 1 | Title + สิ่งที่จะได้เรียนรู้วันนี้ |
| 2 | Story / Pain Point เปิดเรื่อง (กำลังทำ `feature/login` ค้าง แล้วหัวหน้าสั่งแก้บั๊กด่วนบน `main`) |
| 3 | **Setup** — bash script สร้าง repo ทดสอบ ครบใน code block เดียว copy-paste ได้ทันที |
| 4 | ตรวจสอบว่าพร้อม — `git branch -a`, `git log --oneline --all --graph` + expected output |
| 5–6 | **ปัญหาของวิธีเดิม** — `git switch` ขณะมี uncommitted changes: switch ไม่ได้ / ไฟล์ติดข้ามไปด้วย (อธิบายปัญหาเท่านั้น ยังไม่เฉลย) |
| 7 | **Worktree คืออะไร** — concept: 1 `.git` : หลาย working directory |
| 8 | **Diagram** — เปรียบเทียบ before/after แบบภาพ (ดู §5) |
| 9 | `git worktree add <path> <branch>` — ใช้ branch ที่มีอยู่ |
| 10 | `git worktree add -b <new-branch> <path>` — สร้าง branch ใหม่พร้อมกัน |
| 11 | `git worktree list` — อ่านผลลัพธ์ให้เป็น |
| 12 | `git worktree remove` / `git worktree prune` |
| 13–15 | **Workflow step-by-step** — แก้ hotfix บน `main` ขณะ `feature/login` ยังค้าง → merge → เก็บกวาด worktree |
| 16 | **Use case: AI coding agent** — รัน agent หลายตัว (เช่น Claude Code) คนละ worktree พร้อมกัน ไม่ชนกัน |
| 17 | **ข้อควรระวัง** — branch เดียว checkout ซ้ำไม่ได้, shared `.git`, `node_modules`/venv ต้องติดตั้งแยกต่อ worktree, ลบ folder มือเปล่าแล้วต้อง `prune` |
| 18 | **Hands-on Lab** — โจทย์ + ขั้นตอน |
| 19 | **Checklist ตรวจสอบความสำเร็จ** — เกณฑ์ที่ตรวจได้ด้วยคำสั่งจริง |
| 20 | **คำถามทบทวน 4 ข้อ + เฉลย** |

## 4. กติกาเนื้อหาต่อสไลด์

- **1 สไลด์ = 1 ประเด็น, ไม่เกิน 6 bullets**
- **ทุกคำสั่งอยู่ใน code block** และต้องมี **expected output จริง** (ไม่ใช่ `...` หรือ placeholder)
- ทุกสไลด์มี **speaker notes 2–3 บรรทัด** (สิ่งที่ผู้สอนควรพูด / จุดที่นักศึกษามักพลาด)
- Setup script ต้อง **idempotent** — ลบ directory เดิมก่อน, ใช้ `git init -b main`,
  ตั้ง `git config user.name/user.email` ระดับ local ในสคริปต์ เพื่อให้ commit ผ่านบนเครื่องเปล่า

## 5. Visual design

ใช้ธีมเดียวกับเอกสารประกอบวิชาที่ผ่านมา — **dark GitHub theme**:

- Background `#0d1117` · panel `#161b22` · border `#30363d`
- Text `#e6edf3` · muted `#8b949e`
- Accent (Git orange) `#f05133` · accent2 (link blue) `#58a6ff`
- Success `#3fb950` · warning `#d29922` · code background `#0b0f14`
- Font: `"Segoe UI", "Noto Sans Thai", sans-serif` — heading หนา, body line-height โปร่ง ~1.7
- Code block: monospace, พื้นเข้ม, border ซ้ายสีส้ม, มี prompt `$` นำหน้าคำสั่ง และ output สีเทาอ่อน
- แต่ละสไลด์มี **หมายเลขสไลด์มุมล่างขวา** และ **แถบหัวข้อสั้น ๆ มุมบนซ้าย**
- ไอคอน/emoji ใช้ได้เบา ๆ ตามสไตล์เอกสารเดิม (📖 story, 🎯 objective, ✅ checklist, ❓ คำถาม)

**Diagram สไลด์ที่ 8** ให้วาดเป็นภาพจริง (ไม่ใช่ ASCII):

- ฝั่งซ้าย "แบบเดิม": 1 กล่อง working directory เชื่อมกับ `.git` มีลูกศรวนสลับ branch ไปมา + ป้ายแดง "สลับทีต้องเคลียร์งานค้างทุกครั้ง"
- ฝั่งขวา "worktree": `.git` เดียวตรงกลาง แตกเส้นไปยัง 3 กล่อง working directory
  (`demo-worktree` = main, `demo-hotfix` = hotfix, `demo-login` = feature/login) แต่ละกล่องระบุ branch กำกับ
- ใช้สี accent ส้มสำหรับ `.git` และสีฟ้าสำหรับ working directory

## 6. ตรวจก่อนส่ง (รายงานผลเป็น checklist ท้าย output)

- [ ] คำว่า `stash` ปรากฏ **0 ครั้ง** ทั้ง deck
- [ ] Setup script รันได้จริงตั้งแต่บรรทัดแรกถึงบรรทัดสุดท้ายบนเครื่องเปล่า
- [ ] ทุก path / branch ตรงกับ scenario `~/work/demo-worktree`
- [ ] ทุก code block มี expected output
- [ ] ไม่มีสไลด์ใดเกิน 6 bullets
- [ ] ไม่สอนซ้ำหัวข้อใน §1
- [ ] จำนวนสไลด์ 15–20
