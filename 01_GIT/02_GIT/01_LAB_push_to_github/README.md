# LAB 01 — Backup to the Cloud · push ขึ้น GitHub (Remote Repository)

> **Week 2 · Getting Started with Git** — อ้างอิงสไลด์ `02_GIT.pdf` หน้า 38–48 และ `git_week2.html`
> expected output ทุกจุดรันจริงบน container `tuchsanai/devtools:2569_1` (git 2.43.0) push ขึ้น GitHub จริง
> ตัวอย่างใช้ตัวตนสมมุติ `somchai-dev` — **แทน `YOUR_USERNAME` ด้วย username GitHub ของตัวเอง** และใช้ token ของตัวเองเสมอ

---

## 1) Story / Pain Point 📖

สมชายทำ [LAB 00](../00_LAB_add_commit_status/README.md) จบ — มี time machine ประจำโปรเจกต์แล้ว 🎉
แต่คืนนั้นเอง…ชาเย็นทั้งแก้วคว่ำใส่โน้ตบุ๊ก เครื่องดับ เปิดไม่ติด

ประวัติ commit ทั้งหมดอยู่ในโฟลเดอร์ `.git/` **ในเครื่องที่เพิ่งพังไปเมื่อกี้** — time machine ที่อุตส่าห์สร้าง จมน้ำชาไปพร้อมกัน

**Pain Point ที่ LAB 00 ยังแก้ไม่ได้:**

| # | ปัญหา | อาการ |
|---|-------|-------|
| 1 | เครื่องพัง = งานหาย | ทุก commit อยู่ในเครื่องเดียว ไม่มีสำเนาที่อื่น |
| 2 | ทำงานได้เครื่องเดียว | อยากทำต่อที่แลป/ที่บ้าน ต้องก๊อปใส่แฟลชไดรฟ์ |
| 3 | ไม่มีใครเห็นงานเรา | อาจารย์/เพื่อนร่วมทีมดูโค้ดเราไม่ได้เลย |

**ทางแก้ = Remote Repository.** ฝากสำเนา repository ไว้บนเซิร์ฟเวอร์ (GitHub) แล้วซิงก์ด้วย
`git push` — เครื่องพังก็แค่ clone กลับมา งานอยู่ครบทุก commit

---

## 2) สิ่งที่จะได้เรียนรู้ 🎯

- เชื่อม local repository เข้ากับ **remote** ด้วย `git remote add origin <URL>`
- ตรวจการเชื่อมต่อด้วย `git remote -v`
- เข้าใจปัญหา **master vs main** และแก้ด้วย `git branch -M main`
- push ครั้งแรกด้วย `git push -u origin main` (ตั้ง upstream)
- ฝึกวงจรทำงานจริง **แก้ไข → commit → push** ซ้ำ 3 รอบจนเป็นนิสัย

---

## 3) ทฤษฎี ①: Local ↔ Remote และ "origin"

*(สไลด์หน้า 38–42)*

```
   เครื่องเรา (LOCAL)                        GitHub (REMOTE)
 ┌──────────────────┐      git push       ┌──────────────────┐
 │  lab-git/        │  ─────────────────► │  lab-git.git     │
 │  (.git ครบทุก     │      git pull       │  (สำเนาบน cloud)  │
 │   commit)        │  ◄───────────────── │                  │
 └──────────────────┘                     └──────────────────┘
```

- **remote** = repository อีกก้อนที่อยู่บนเซิร์ฟเวอร์ (GitHub/GitLab/Bitbucket)
- `git remote -v` — ดูว่า repo เราเชื่อมกับ remote ไหนอยู่ (repo ที่ clone มาจะเห็น URL,
  repo ที่ `git init` เองจะ**ว่างเปล่า**จนกว่าจะ add)
- `git remote add origin https://url.git` — ผูก remote โดยตั้งชื่อเรียกสั้น ๆ ว่า **`origin`**
  (เป็นธรรมเนียม — ตั้งชื่ออื่นได้แต่ไม่มีใครทำ)
- เผื่ออนาคต (สไลด์หน้า 41): `git remote rename <old> <new>` และ `git remote remove <name>`
- `git push -u origin main` — push ครั้งแรกพร้อมตั้ง **upstream** (`-u`) ให้ branch local
  จับคู่กับ branch บน remote → ครั้งถัดไป Git รู้เองว่า push ไปไหน
- `git pull` = ทิศตรงข้ามของ push คือ**ดึง**การเปลี่ยนแปลงจาก remote ลงเครื่อง (สไลด์หน้า 35–36) —
  LAB นี้โฟกัสขา push ส่วน pull ฝึกต่อในหัวข้อ Fetch vs Pull ของ Week 2

## 3.1) ทฤษฎี ②: master vs main — ปัญหาชนกันที่ต้องรู้ก่อน push

*(สไลด์หน้า 43–48)*

- เดิม Git ตั้งชื่อ branch แรกว่า **`master`** — แต่ **GitHub เปลี่ยนธรรมเนียมอย่างเป็นทางการ
  เป็น `main`** repo ที่สร้างบนเว็บ GitHub ปัจจุบันจึงได้ default branch ชื่อ `main`
- เครื่องเรา `git init` ยังได้ `master` (git 2.43 ใน container นี้) → เกิดสถานการณ์ **Improper Reference**:

```
   LOCAL: master  ──✗──  GitHub: main     ← คนละชื่อ = คนละ branch, push/pull ไม่เจอกัน
```

- **สองทางแก้:**
  1. เปลี่ยนชื่อ branch ปัจจุบันทันที (ใช้ใน LAB นี้ — ตามที่หน้า repo GitHub แนะนำ):
     `git branch -M main`
  2. ตั้งถาวรทุก repo ใหม่ (ทำแล้วใน LAB Configure Week 1): `git config --global init.defaultBranch main`
- กรณี **clone** จาก GitHub มาก่อน จะไม่เจอปัญหานี้ — เพราะได้ branch `main` ติดมาตั้งแต่แรก
  ปัญหาจะเกิดเฉพาะเส้นทาง **"local folder เดิม → GitHub"** แบบที่เรากำลังทำใน LAB นี้

---

## 4) เตรียมความพร้อม ⚙️

### 4.1 Container + ตัวตน

```bash
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

```bash
git config --global user.name "somchai-dev"            # ← ใช้ชื่อของตัวเอง
git config --global user.email "somchai.dev@example.com" # ← ใช้อีเมลของตัวเอง
```

### 4.2 Personal Access Token (PAT) ของตัวเอง

GitHub ไม่รับ password ในการ push แล้ว — ต้องใช้ **token** (สร้างตามวิธีใน LAB ชุด token ของ Week 1:
GitHub → Settings → Developer settings → Personal access tokens (classic) → scope `repo`)

```bash
export GIT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   # ← token ของตัวเอง
```

> 🔐 **token = รหัสผ่าน** — ห้ามส่งให้เพื่อน ห้าม commit ลงไฟล์ ห้ามแปะในรายงาน/สไลด์
> ตัวอย่างทั้งเอกสารนี้ใช้ตัวแปร `${GIT_TOKEN}` แทนค่าจริงเสมอ

> 🆕 GitHub ปัจจุบันมี token แบบใหม่ **fine-grained** (จำกัดสิทธิ์ราย repo ได้ละเอียดกว่า) ให้เลือกด้วย —
> ใน LAB นี้ใช้แบบ classic + scope `repo` ตามที่ฝึกใน Week 1 ก็เพียงพอ

---

## 5) STEP 1 — สร้าง local repo + commit แรก (ทบทวน LAB 00)

```bash
mkdir lab-git
cd lab-git
git init
echo "Initial content for file 1" > file1.txt
echo "Initial content for file 2" > file2.txt
echo "Initial content for file 3" > file3.txt
git add file1.txt file2.txt file3.txt
git commit -m "Initial commit with three files"
git log --oneline
```

**Expected Output** (ย่อ — โครงเดียวกับ LAB 00)

```
[master (root-commit) 8f157da] Initial commit with three files
 3 files changed, 3 insertions(+)
 create mode 100644 file1.txt
 create mode 100644 file2.txt
 create mode 100644 file3.txt
```

```
8f157da Initial commit with three files
```

> hash ของแต่ละคนไม่เหมือนกัน — และสังเกตว่าเรายังอยู่บน `master`

---

## 6) STEP 2 — เปลี่ยน master → main (แก้ปัญหาจากทฤษฎี ②)

ดูชื่อ branch ปัจจุบัน → เปลี่ยนชื่อ → ตรวจซ้ำ:

```bash
git branch
git branch -M main
git branch
git status
```

**Expected Output**

```
* master
```

```
* main
```

```
On branch main
nothing to commit, working tree clean
```

> 📌 `-M` = ย้าย/เปลี่ยนชื่อ branch (บังคับทับถ้าชื่อซ้ำ) — commit ทั้งหมดยังอยู่ครบ แค่ป้ายชื่อเปลี่ยน
> ถ้าเครื่องคุณตั้ง `init.defaultBranch main` ไว้แล้ว `git branch` จะตอบ `* main` ตั้งแต่แรก —
> สั่ง `git branch -M main` ซ้ำก็ไม่เสียหายอะไร

---

## 7) STEP 3 — สร้าง Remote Repository บน GitHub (ผ่านเว็บ)

1. เข้า [github.com](https://github.com) → ปุ่ม **New repository**
2. **Repository name:** `lab-git`
3. เลือก **Private**
4. ⚠️ **ไม่ต้องติ๊ก** "Add a README file" และไม่เลือก .gitignore/license ใด ๆ — เราจะ push
   ประวัติจาก local ขึ้นไปเอง ถ้า GitHub สร้าง commit ให้ก่อน จะชนกับของเราแล้ว push แรกโดน **rejected**
5. กด **Create repository** — GitHub จะแสดงหน้า quick setup พร้อมคำแนะนำ

> 🆕 สังเกตบล็อก **"…or push an existing repository from the command line"** บนหน้านั้น —
> คือชุดคำสั่งเดียวกับที่เรากำลังทำเป๊ะ ๆ: `git remote add origin …` → `git branch -M main` (STEP 2 ของเรา)
> → `git push -u origin main` — จบ LAB นี้แล้วจะอ่านหน้านั้นออกทั้งหมด

---

## 8) STEP 4 — เชื่อม local เข้ากับ remote

ก่อนเชื่อม — พิสูจน์ว่า repo เรายังไม่รู้จัก remote ใดเลย:

```bash
git remote -v
```

**Expected Output** *(ว่างเปล่า — ไม่มี output ใด ๆ)*

```
```

เชื่อมด้วยชื่อ `origin` (ฝัง token ใน URL เพื่อให้ push ได้โดยไม่ต้องพิมพ์รหัสทุกครั้ง) แล้วตรวจซ้ำ:

```bash
git remote add origin https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-git.git
git remote -v
```

**Expected Output**

```
origin	https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-git.git (fetch)
origin	https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-git.git (push)
```

> 🔐 ในเครื่องจริง `git remote -v` จะแสดง **token จริงของคุณเต็ม ๆ** ใน URL —
> ระวังเวลาแชร์หน้าจอ/แคปภาพส่งรายงาน

---

## 9) STEP 5 — Push ครั้งแรก (-u = ตั้ง upstream)

```bash
git push -u origin main
```

**Expected Output**

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 32 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (5/5), 379 bytes | 379.00 KiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/lab-git.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

> 📌 บรรทัดสำคัญ: `* [new branch] main -> main` = สร้าง branch main บน GitHub สำเร็จ
> และ `branch 'main' set up to track 'origin/main'` = ผลของ `-u`
> (จำนวน threads / ความเร็ว KiB/s ขึ้นกับเครื่องแต่ละคน)

```bash
git status
```

**Expected Output**

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

> `git status` ตอนนี้รายงานเทียบกับ remote ด้วย — refresh หน้า repo บน GitHub จะเห็นไฟล์ทั้ง 3 แล้ว 🎉

---

## 10) STEP 6 — วงจรจริง: แก้ไข → commit → push × 3 รอบ

### รอบที่ 1

```bash
echo "Change 1 for file 1" >> file1.txt
echo "Change 1 for file 2" >> file2.txt
echo "Change 1 for file 3" >> file3.txt
git status
git add file1.txt file2.txt file3.txt
git commit -m "First set of changes"
git push origin main
```

**Expected Output**

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   file1.txt
	modified:   file2.txt
	modified:   file3.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

```
[main 1ed541c] First set of changes
 3 files changed, 3 insertions(+)
```

```
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 32 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (5/5), 431 bytes | 431.00 KiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/lab-git.git
   8f157da..1ed541c  main -> main
```

> 📌 คราวนี้ไม่มี `[new branch]` แล้ว — แต่เป็น `8f157da..1ed541c` = ขยับ main
> จาก commit เก่าไป commit ใหม่ · และไม่ต้องใส่ `-u` อีกเพราะตั้ง upstream ไว้แล้ว

### รอบที่ 2

```bash
echo "Change 2 for file 1" >> file1.txt
echo "Change 2 for file 2" >> file2.txt
echo "Change 2 for file 3" >> file3.txt
git add file1.txt file2.txt file3.txt
git commit -m "Second set of changes"
git push origin main
```

**Expected Output**

```
[main e81cee4] Second set of changes
 3 files changed, 3 insertions(+)
```

```
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 32 threads
Compressing objects: 100% (5/5), done.
Writing objects: 100% (5/5), 444 bytes | 444.00 KiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/lab-git.git
   1ed541c..e81cee4  main -> main
```

### รอบที่ 3

```bash
echo "Change 3 for file 1" >> file1.txt
echo "Change 3 for file 2" >> file2.txt
echo "Change 3 for file 3" >> file3.txt
git add file1.txt file2.txt file3.txt
git commit -m "Third set of changes"
git push origin main
```

**Expected Output**

```
[main 4482f52] Third set of changes
 3 files changed, 3 insertions(+)
```

```
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 32 threads
Compressing objects: 100% (5/5), done.
Writing objects: 100% (5/5), 453 bytes | 453.00 KiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/lab-git.git
   e81cee4..4482f52  main -> main
```

---

## 11) STEP 7 — ตรวจผลสุดท้าย

```bash
git log --oneline
git status
cat file1.txt
```

**Expected Output**

```
4482f52 Third set of changes
e81cee4 Second set of changes
1ed541c First set of changes
8f157da Initial commit with three files
```

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

```
Initial content for file 1
Change 1 for file 1
Change 2 for file 1
Change 3 for file 1
```

**ตรวจบนเว็บ GitHub:** เปิดหน้า repo `lab-git` → เห็นไฟล์ 3 ไฟล์ + ข้อความ commit ล่าสุด
"Third set of changes" → กดตัวเลข **4 Commits** เพื่อไล่ดูประวัติทั้งหมดบน cloud ☁️

🎉 ตอนนี้ต่อให้โน้ตบุ๊กจมชาเย็นทั้งแก้ว งานของสมชายก็ยังอยู่ครบทุก commit บน GitHub

---

## 12) สรุป + Cheat Sheet

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git branch -M main` | เปลี่ยนชื่อ branch ปัจจุบันเป็น main (ธรรมเนียม GitHub) |
| `git remote -v` | ดู remote ที่เชื่อมอยู่ (ว่าง = ยังไม่เชื่อม) |
| `git remote add origin <URL>` | ผูก remote ชื่อ origin |
| `git push -u origin main` | push ครั้งแรก + ตั้ง upstream |
| `git push origin main` | push รอบถัดไป (มี upstream แล้ว ใช้ `git push` เฉย ๆ ก็ได้) |
| `git remote rename/remove` | เปลี่ยนชื่อ/ถอด remote (เผื่ออนาคต) |
| `git pull` | ดึง commit ใหม่จาก remote ลงเครื่อง (คู่ตรงข้ามของ push — ฝึกในหัวข้อ Fetch vs Pull) |

**วงจรที่ต้องจำ:** แก้ไข → `git add` → `git commit -m` → `git push` ✅

## 13) Checklist ก่อนไปต่อ ✅

- [ ] `git branch` ตอบ `* main` ก่อน push ครั้งแรก
- [ ] `git remote -v` ก่อน add ว่างเปล่า / หลัง add เห็น origin 2 บรรทัด (fetch, push)
- [ ] push แรกเห็น `* [new branch] main -> main` และ `set up to track`
- [ ] push รอบ 2–4 เห็นรูปแบบ `<hash เก่า>..<hash ใหม่>  main -> main`
- [ ] `git log --oneline` มี 4 commits และหน้าเว็บ GitHub แสดง "4 Commits" ตรงกัน
- [ ] ตอบได้ว่าถ้าเครื่องพังตอนนี้ งานหายไหม เพราะอะไร

## 14) คำถามทบทวน ❓

1. `origin` คืออะไร — เป็นคำสงวนของ Git หรือแค่ธรรมเนียม? ใช้ชื่ออื่นได้ไหม
2. ทำไมต้องสั่ง `git branch -M main` ก่อน push? ถ้าไม่ทำแล้ว push `master` ขึ้นไป repo GitHub ที่ default เป็น `main` จะเกิดอะไรขึ้น
3. `-u` ใน `git push -u origin main` ทำอะไร และเห็นผลที่บรรทัดไหนของ output?
4. ตอนสร้าง repo บนเว็บ ทำไม LAB นี้ห้ามติ๊ก "Add a README file"?
5. `git remote -v` หลัง STEP 4 มีอะไรซ่อนอยู่ใน URL ที่ไม่ควรให้คนอื่นเห็น? ควรระวังตอนไหน
6. push รอบ 2 ขึ้นไป output ไม่มีคำว่า `[new branch]` แล้ว — บรรทัด `8f157da..1ed541c main -> main` อ่านว่าอย่างไร
7. สถานการณ์ไหนที่เราจะ**ไม่เจอ**ปัญหา master vs main เลยตั้งแต่ต้น? (คำใบ้: สไลด์หน้า 47 — clone)

---

*LAB 01 — Backup to the Cloud · DevTools Week 2 · expected output รันจริงบน `tuchsanai/devtools:2569_1` (git 2.43.0) push ขึ้น GitHub จริง — commit hash / จำนวน threads / ความเร็ว ของแต่ละคนจะต่างจากตัวอย่าง*
