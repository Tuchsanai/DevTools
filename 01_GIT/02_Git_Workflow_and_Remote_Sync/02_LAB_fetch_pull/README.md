# LAB 02 — Two Machines, One Project · `clone` / `fetch` / `pull` (Sync จาก Remote)

> **Week 2 · Getting Started with Git** — อ้างอิงสไลด์ `02_GIT.pdf` หน้า 47, 50–62 (Cloning & Remote-Tracking Branches) และหน้า 63–76 (Git Log · Fetch and Pull) และ `git_week2.html`
> expected output ทุกจุดรันจริงบน container `tuchsanai/devtools:2569_1` (git 2.43.0) กับ GitHub จริง
> ตัวอย่างใช้ตัวตนสมมุติ `somchai-dev` — **แทน `YOUR_USERNAME` ด้วย username GitHub ของตัวเอง** และใช้ token ของตัวเองเสมอ

---

## 1) Story / Pain Point 📖

จบ [LAB 01](../01_LAB_push_to_github/README.md) สมชายมี repository อยู่บน GitHub แล้ว — เครื่องพังงานไม่หาย 🎉
แต่เช้าวันจันทร์ สมชายไปถึง**ห้องแลปมหาวิทยาลัย** นั่งลงหน้าคอมของแลป…แล้วก็นิ่งไป

เครื่องแลป**ไม่มีโปรเจกต์ของเขาเลยสักไฟล์** — งานทั้งหมดอยู่บน GitHub กับโน้ตบุ๊กที่บ้าน

**Pain Point ที่ LAB 01 ยังแก้ไม่ครบ:**

| # | ปัญหา | อาการ |
|---|-------|-------|
| 1 | เครื่องใหม่ = เริ่มจากศูนย์ | จะเอาโปรเจกต์ (พร้อม**ประวัติทุก commit**) ลงเครื่องแลปยังไง — ก๊อปไฟล์มาได้แต่ประวัติหาย |
| 2 | สองเครื่องไม่ตรงกัน | คืนนี้แก้งานที่บ้านแล้ว push — พรุ่งนี้เครื่องแลปกลายเป็น "เวอร์ชันเมื่อวาน" ทันที |
| 3 | ไม่รู้ว่า GitHub มีอะไรใหม่ | นั่งลงหน้าเครื่องแลปแล้วตอบไม่ได้ว่า "ที่นี่ล้าหลัง GitHub อยู่กี่ commit" |
| 4 | กลัวดึงงานมาทับ | อยากได้ของใหม่จาก GitHub แต่กลัวมัน "ทับ" สิ่งที่กำลังทำค้างอยู่บนเครื่อง |

**ทางแก้ = ขาดาวน์โหลดของ Git.** LAB 01 ฝึกขาขึ้น (`git push`) — LAB นี้ฝึก**ขาลง**ให้ครบวงจร:
`git clone` ยกโปรเจกต์+ประวัติทั้งหมดลงเครื่องใหม่ · `git fetch` เช็กของใหม่แบบ**ปลอดภัย** ·
`git merge` / `git pull` นำของใหม่เข้า branch ของเรา

---

## 2) สิ่งที่จะได้เรียนรู้ 🎯

- `git clone` — ประตูทางเข้าที่สอง: ได้ไฟล์ + ประวัติทุก commit + การเชื่อมต่อ remote **ฟรีในคำสั่งเดียว**
- **remote-tracking branch** (`origin/main`) — "บุ๊กมาร์ก" ที่ทำให้ `git status` รู้ว่าเรา ahead/behind
- อ่านสถานะ `ahead of` / `behind` / `up to date` ให้ออก — และรู้ว่ามันเทียบกับ**บุ๊กมาร์ก** ไม่ใช่ GitHub จริง ๆ
- `git fetch` — ดึงของใหม่มา**เก็บไว้ก่อน** โดยไม่แตะไฟล์ที่กำลังทำงาน (ปลอดภัยเสมอ)
- สูตรสำคัญ **`git pull` = `git fetch` + `git merge`** — ลองแยกทีละท่อนก่อน แล้วค่อยใช้ท่ารวบ
- โบนัส: แอบดูของที่ fetch มาด้วย `git checkout origin/main` (รู้จัก **detached HEAD** แบบไม่ต้องตกใจ)

---

## 3) ทฤษฎี ①: `git clone` — ประตูทางเข้าที่สอง

*(สไลด์หน้า 5–7, 47, 50–52)*

การพาโปรเจกต์มาเจอกับ GitHub มี **2 เส้นทาง**:

```
 เส้นทาง A (LAB 01): local เกิดก่อน                เส้นทาง B (LAB นี้): GitHub เกิดก่อน
 ┌─────────┐                    ┌────────┐         ┌────────┐                    ┌─────────┐
 │ git init │ ── remote add ──► │ GitHub │         │ GitHub │ ──── git clone ──► │ เครื่องเรา │
 │ (master) │    branch -M main │ (main) │         │ (main) │    ได้ main ติดมาเลย │ (main)  │
 └─────────┘    push -u        └────────┘         └────────┘                    └─────────┘
      ต้องทำเอง 3 คำสั่ง + เจอปัญหา master/main            คำสั่งเดียวจบ ✓
```

`git clone <URL>` ทำให้เราแบบครบเซ็ต:

- ดาวน์โหลด**ทุกไฟล์ + ประวัติทุก commit** ของ repo ณ ขณะนั้น (ไม่ใช่แค่ไฟล์ล่าสุด)
- ตั้ง remote `origin` ให้อัตโนมัติ (ไม่ต้อง `git remote add`)
- ได้ branch ชื่อ **`main` ตามต้นทาง** — ปัญหา Improper Reference (master ชน main, สไลด์หน้า 46)
  **ไม่เกิดเลย**ในเส้นทางนี้ (สไลด์หน้า 47)
- ผูก upstream ให้เสร็จ — `git push` / `git pull` ได้ทันทีโดยไม่ต้อง `-u`

## 3.1) ทฤษฎี ②: `origin/main` — บุ๊กมาร์กที่เลื่อนเองไม่ได้

*(สไลด์หน้า 53–59)*

หลัง clone เครื่องเราจะมีตัวชี้ **2 ตัว** ที่หน้าตาคล้ายกันแต่คนละหน้าที่:

| ตัวชี้ | ชนิด | ใครขยับมัน |
|--------|------|-----------|
| `main` | local branch ของเรา | **เราขยับเอง** — ขยับไปข้างหน้าทุกครั้งที่ commit |
| `origin/main` | **remote-tracking branch** | **เราขยับเองไม่ได้** — เป็นบุ๊กมาร์กจดว่า "เท่าที่รู้ล่าสุด main บน GitHub อยู่ตรงไหน" อัปเดตเฉพาะตอน sync (`fetch`/`pull`/`push`) |

```
 commit ในเครื่อง 2 ครั้ง:                        มีคน push ขึ้น GitHub 2 commit:
                                                 (เครื่องเรายังไม่ sync)
 ●───●───●───●            ●───●───●───●
     ▲       ▲                ▲       ▲
 origin/main main         main     origin/main  ← หลัง git fetch
 → status: "ahead by 2"   → status: "behind by 2"
```

- ดูบุ๊กมาร์กทั้งหมดที่เครื่องรู้จัก: `git branch -r`
- `git status` เทียบ `main` กับ `origin/main` แล้วรายงาน **ahead** (เรามีของที่ยังไม่ push) /
  **behind** (remote มีของที่เรายังไม่รับ) / **up to date**
- ⚠️ **กับดักสำคัญ:** `git status` **ไม่ได้ต่อเน็ตไปถาม GitHub** — มันเทียบกับบุ๊กมาร์กในเครื่องเท่านั้น
  ถ้าบุ๊กมาร์กเก่า (ยังไม่ fetch) มันจะตอบ `up to date` ทั้งที่ GitHub มีของใหม่แล้ว → เจอของจริงใน STEP 3

## 3.2) ทฤษฎี ③: Fetch vs Pull — ดึงแบบระวัง vs ดึงแบบรวบรัด

*(สไลด์หน้า 63–76)*

การนำการเปลี่ยนแปลงจาก remote ลงมามี **2 วิธี** (สไลด์หน้า 66):

```
                       git fetch                    git merge origin/main
 ☁️ Remote ────────────────────► 🔖 origin/main ────────────────────► 💻 main + ไฟล์จริง
 (GitHub)   ดาวน์โหลดมาเก็บใน .git   (บุ๊กมาร์กขยับ)      นำเข้า branch เรา
            ยังไม่แตะไฟล์ที่ทำงานอยู่

 └──────────────────────────  git pull = fetch + merge ทีเดียวจบ ──────────────────────────┘
```

| ประเด็น | `git fetch` | `git pull` |
|---------|------------|-----------|
| ดึงการเปลี่ยนแปลงจาก remote | ✅ ใช่ | ✅ ใช่ |
| อัปเดตบุ๊กมาร์ก `origin/main` | ✅ อัปเดต | ✅ อัปเดต |
| merge เข้า branch ปัจจุบัน + เปลี่ยนไฟล์จริง | ❌ ไม่ทำ | ✅ ทำให้อัตโนมัติ |
| โอกาสเกิด merge conflict | ❌ ไม่เกิด (ปลอดภัย) | ✅ อาจเกิดได้ — เจาะลึก Week 3 |
| ความปลอดภัย | **ทำได้ทุกเมื่อ** — ตรวจก่อนค่อยตัดสินใจ merge เอง | สะดวก แต่ไม่แนะนำถ้ามีงานค้างยังไม่ commit |

- **สูตรที่ต้องจำ (สไลด์หน้า 74):** `git pull` = `git fetch` + `git merge`
- ระหว่างกลาง (fetch แล้วแต่ยังไม่ merge) เราใช้ `git log --oneline --all` ดูได้ว่ามี commit ใหม่อะไรรออยู่ (สไลด์หน้า 63–64)
- LAB นี้ทุก merge เป็นแบบ **Fast-forward** (เลื่อนตัวชี้ตามไปเฉย ๆ เพราะเราไม่มี commit สวนทาง) —
  กรณีต่างคนต่างแก้จน**ชนกัน (merge conflict)** เป็นเรื่องของ branch ใน Week 3

---

## 4) เตรียมความพร้อม ⚙️

### 4.1 Container + ตัวตน

```bash
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

```bash
git config --global user.name "somchai-dev"              # ← ใช้ชื่อของตัวเอง
git config --global user.email "somchai.dev@example.com" # ← ใช้อีเมลของตัวเอง
```

### 4.2 Token

ใช้ Personal Access Token ตัวเดียวกับ LAB 01 (scope `repo`):

```bash
export GIT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   # ← token ของตัวเอง
```

> 🔐 **token = รหัสผ่าน** — ห้ามส่งให้เพื่อน ห้าม commit ลงไฟล์ ห้ามแปะในรายงาน/สไลด์
> ตัวอย่างทั้งเอกสารนี้ใช้ตัวแปร `${GIT_TOKEN}` แทนค่าจริงเสมอ

### 4.3 สร้าง Remote Repository บน GitHub (ผ่านเว็บ)

1. เข้า [github.com](https://github.com) → ปุ่ม **New repository**
2. **Repository name:** `lab-sync`
3. เลือก **Private**
4. ✅ คราวนี้**ติ๊ก "Add a README file"** — ตรงข้ามกับ LAB 01!
5. กด **Create repository**

> 💡 **ทำไม LAB 01 ห้ามติ๊ก แต่ LAB นี้ต้องติ๊ก?** — LAB 01 เรามีประวัติในเครื่องอยู่แล้ว ถ้า GitHub
> สร้าง commit ให้ก่อนจะชนกัน แต่ LAB นี้เราเริ่มจาก**ศูนย์ทั้งสองเครื่อง** — ให้ GitHub สร้าง
> commit แรก (`Initial commit` + ไฟล์ `README.md`) รอไว้ แล้วเรา clone ลงมา
> นี่คือเส้นทาง **"Create Repo on GitHub → git clone"** ตามสไลด์หน้า 6–7 เป๊ะ ๆ

**บทบาทสมมุติใน LAB:** เครื่องเดียวของเราจะเล่นเป็น 2 เครื่อง โดยใช้ 2 โฟลเดอร์แทน

```
 📁 uni-pc       = คอมห้องแลปมหาวิทยาลัย
 📁 home-laptop  = โน้ตบุ๊กที่บ้าน
```

---

## 5) STEP 1 — clone ลงเครื่องแลป (`uni-pc`)

สมชายนั่งหน้าเครื่องแลป — ยกโปรเจกต์จาก GitHub ลงมาทั้งก้อนด้วยคำสั่งเดียว:

```bash
git clone https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-sync.git uni-pc
cd uni-pc
ls
```

**Expected Output**

```
Cloning into 'uni-pc'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (3/3), done.
```

```
README.md
```

> 📌 คำที่ต่อท้าย URL (`uni-pc`) = ชื่อโฟลเดอร์ปลายทาง (ถ้าไม่ใส่จะได้โฟลเดอร์ชื่อ `lab-sync`)
> จำนวน objects/ความเร็ว ของแต่ละคนอาจต่างกันเล็กน้อย

สำรวจของแถมที่ clone ให้ฟรี — branch, บุ๊กมาร์ก และ remote:

```bash
git branch
git branch -r
git remote -v
```

**Expected Output**

```
* main
```

```
  origin/HEAD -> origin/main
  origin/main
```

```
origin	https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-sync.git (fetch)
origin	https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-sync.git (push)
```

> 📌 เทียบกับ LAB 01 ชัด ๆ : ไม่ต้อง `git branch -M main` (ได้ `main` ติดมาเลย — สไลด์หน้า 47)
> ไม่ต้อง `git remote add origin` (ผูกให้แล้ว) · `git branch -r` โชว์**บุ๊กมาร์ก**ฝั่ง remote ที่เครื่องรู้จัก
> ส่วน `origin/HEAD -> origin/main` หมายถึง branch หลักของ remote คือ `main`
>
> 🔐 `git remote -v` โชว์ token เต็ม ๆ ใน URL — ระวังเวลาแชร์หน้าจอ/แคปภาพส่งรายงาน

ดูประวัติและสถานะ:

```bash
git log --oneline
git status
```

**Expected Output**

```
0a3ff6b (HEAD -> main, origin/main, origin/HEAD) Initial commit
```

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

> 📌 `(HEAD -> main, origin/main, origin/HEAD)` = ตอนนี้ `main` กับบุ๊กมาร์ก `origin/main`
> ชี้ commit เดียวกัน → `git status` จึงรายงาน `up to date` · hash ของแต่ละคนจะไม่เหมือนตัวอย่าง

---

## 6) STEP 2 — กลับบ้าน: clone เครื่องที่สอง แล้วทำงานต่อ (`home-laptop`)

ตกเย็นสมชายกลับบ้าน — โน้ตบุ๊กที่บ้านก็ยังไม่มีโปรเจกต์เหมือนกัน clone อีกรอบ (ถอยออกมาก่อนด้วย `cd ..` ให้สองโฟลเดอร์อยู่ระดับเดียวกัน):

```bash
cd ..
git clone https://YOUR_USERNAME:${GIT_TOKEN}@github.com/YOUR_USERNAME/lab-sync.git home-laptop
cd home-laptop
```

**Expected Output**

```
Cloning into 'home-laptop'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (3/3), done.
```

คืนนี้ไฟแรง — เขียนโปรแกรมแรก + จดวิธีรัน (2 commits ตามวงจรที่ฝึกใน LAB 00):

```bash
echo 'print("Hello from DevTools project")' > app.py
git add app.py
git commit -m "Add app.py"

echo "Run with: python3 app.py" > howto.txt
git add howto.txt
git commit -m "Add how-to-run notes"
```

**Expected Output**

```
[main 395d6a8] Add app.py
 1 file changed, 1 insertion(+)
 create mode 100644 app.py
```

```
[main f339d7d] Add how-to-run notes
 1 file changed, 1 insertion(+)
 create mode 100644 howto.txt
```

ก่อน push ลองถามเข็มทิศ — ทฤษฎี ② จะปรากฏตัวครั้งแรก:

```bash
git status
git log --oneline
```

**Expected Output**

```
On branch main
Your branch is ahead of 'origin/main' by 2 commits.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

```
f339d7d (HEAD -> main) Add how-to-run notes
395d6a8 Add app.py
0a3ff6b (origin/main, origin/HEAD) Initial commit
```

> 📌 **`ahead of 'origin/main' by 2 commits`** (สไลด์หน้า 56–59): เรา commit ไป 2 ครั้ง →
> ตัวชี้ `main` ขยับ 2 ก้าว แต่บุ๊กมาร์ก `origin/main` ยังปักอยู่ที่ `Initial commit`
> ดูใน `git log` ก็เห็นตรงกัน: `(HEAD -> main)` อยู่บนสุด ส่วน `(origin/main)` ค้างอยู่ล่างสุด

ส่งขึ้น GitHub — สังเกตว่า**ไม่ต้องใส่ `-u origin main`** เพราะ clone ผูก upstream ให้แล้ว:

```bash
git push
git status
```

**Expected Output**

```
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 32 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (6/6), 557 bytes | 557.00 KiB/s, done.
Total 6 (delta 1), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (1/1), done.
To https://github.com/YOUR_USERNAME/lab-sync.git
   0a3ff6b..f339d7d  main -> main
```

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

> 📌 `main -> main` = local main ไปอัปเดต main บน GitHub · push แล้วบุ๊กมาร์กขยับตาม →
> กลับมา `up to date` (จำนวน threads/ความเร็ว ขึ้นกับเครื่องแต่ละคน)

---

## 7) STEP 3 — เช้าวันใหม่ที่แลป: `git status` โกหก?! → `git fetch`

เช้าวันอังคาร สมชายกลับมานั่งเครื่องแลป (`uni-pc`) — เครื่องนี้**ยังไม่รู้อะไรเลย**เกี่ยวกับงานเมื่อคืน
ลองถามเข็มทิศดูก่อน:

```bash
cd ../uni-pc
git status
git log --oneline
```

**Expected Output**

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

```
0a3ff6b (HEAD -> main, origin/main, origin/HEAD) Initial commit
```

> ⚠️ **`up to date` ทั้งที่ GitHub มีของใหม่ 2 commits!** — ไม่ใช่ bug: `git status`
> เทียบกับ**บุ๊กมาร์ก `origin/main` ในเครื่อง**ซึ่งยังปักอยู่ที่ `Initial commit` ตั้งแต่ตอน clone เมื่อวาน
> มัน**ไม่เคยต่อเน็ตไปถาม GitHub เอง** — เราต้องสั่งอัปเดตบุ๊กมาร์กด้วย `git fetch`

อัปเดตบุ๊กมาร์กแบบปลอดภัย:

```bash
git fetch
```

**Expected Output**

```
remote: Enumerating objects: 7, done.
remote: Counting objects: 100% (7/7), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 6 (delta 1), reused 6 (delta 1), pack-reused 0 (from 0)
Unpacking objects: 100% (6/6), 537 bytes | 268.00 KiB/s, done.
From https://github.com/YOUR_USERNAME/lab-sync
   0a3ff6b..f339d7d  main       -> origin/main
```

> 📌 บรรทัดสำคัญ: **`main -> origin/main`** = ดาวน์โหลดของใหม่แล้วเลื่อน**บุ๊กมาร์ก** —
> เทียบกับตอน push ที่ขึ้นว่า `main -> main` (อัปเดต branch จริงบน GitHub) คนละทิศ คนละความหมาย

คราวนี้ถามเข็มทิศอีกรอบ + ส่องดูว่ามีอะไรรออยู่:

```bash
git status
git log --oneline --all
ls
```

**Expected Output**

```
On branch main
Your branch is behind 'origin/main' by 2 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)

nothing to commit, working tree clean
```

```
f339d7d (origin/main, origin/HEAD) Add how-to-run notes
395d6a8 Add app.py
0a3ff6b (HEAD -> main) Initial commit
```

```
README.md
```

> 📌 อ่านผลให้ครบ 3 ชั้น:
> ① `behind by 2, can be fast-forwarded` — ตอนนี้เครื่องรู้แล้วว่าตัวเองล้าหลัง 2 commits
> ② `git log --oneline --all` (สไลด์หน้า 63–64) — `(origin/main)` วิ่งขึ้นไปบนสุดแล้ว
> แต่ `(HEAD -> main)` ของเรายังอยู่ล่าง — commit ใหม่**อยู่ในเครื่องแล้ว** (ใน `.git`)
> ③ แต่ `ls` ยังไม่มี `app.py` / `howto.txt` — **fetch ไม่แตะไฟล์ที่เราทำงานอยู่** นี่แหละความปลอดภัยของมัน

---

## 8) STEP 4 (โบนัส) — แอบดูของที่ fetch มา ด้วย detached HEAD 👀

*(สไลด์หน้า 60–61)*

ยังไม่อยาก merge แต่อยากเห็นหน้าตางานเมื่อคืนก่อน? checkout ไปที่บุ๊กมาร์กได้เลย:

```bash
git checkout origin/main
ls
```

**Expected Output**

```
Note: switching to 'origin/main'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at f339d7d Add how-to-run notes
```

```
README.md  app.py  howto.txt
```

> 😌 **detached HEAD ไม่ใช่ error!** แค่แปลว่า HEAD ไปเกาะ commit ตรง ๆ (ไม่ได้เกาะปลาย branch)
> "มองดูได้ ทดลองได้" — ไฟล์งานเมื่อคืนโผล่ครบ พิสูจน์ว่า fetch ดาวน์โหลดมาจริง แค่เก็บไว้ใน `.git`
> จะเจาะลึก checkout / detached HEAD กันจริงจังใน Week 4

ดูเสร็จแล้ว กลับบ้าน (branch `main`) — ไฟล์ก็หายไปเหมือนเดิม:

```bash
git checkout main
ls
```

**Expected Output**

```
Previous HEAD position was f339d7d Add how-to-run notes
Switched to branch 'main'
Your branch is behind 'origin/main' by 2 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)
```

```
README.md
```

---

## 9) STEP 5 — `git merge origin/main`: นำของใหม่เข้า branch เรา

ตรวจสอบแล้ว ปลอดภัย — merge จากบุ๊กมาร์กเข้า `main` ของเครื่องแลป:

```bash
git merge origin/main
ls
cat howto.txt
```

**Expected Output**

```
Updating 0a3ff6b..f339d7d
Fast-forward
 app.py    | 1 +
 howto.txt | 1 +
 2 files changed, 2 insertions(+)
 create mode 100644 app.py
 create mode 100644 howto.txt
```

```
README.md  app.py  howto.txt
```

```
Run with: python3 app.py
```

> 📌 **`Fast-forward`** = `main` ของเราไม่มี commit สวนทาง Git เลยแค่ "เลื่อนตัวชี้ตามไป"
> ไม่ต้องสร้าง commit ใหม่ — ไฟล์จริงบนโต๊ะทำงานถูกอัปเดตในจังหวะนี้เอง (ไม่ใช่ตอน fetch)

```bash
git status
git log --oneline
```

**Expected Output**

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

```
f339d7d (HEAD -> main, origin/main, origin/HEAD) Add how-to-run notes
395d6a8 Add app.py
0a3ff6b Initial commit
```

> 🎉 `main` กับ `origin/main` กลับมาชี้จุดเดียวกัน — เครื่องแลปตามทัน GitHub แล้ว
> และเราเพิ่งทำ **`git fetch` + `git merge` = สิ่งที่ `git pull` ทำ** แบบแยกท่อนครบถ้วน

---

## 10) STEP 6 — รอบสอง: ใช้ท่ารวบ `git pull` ทีเดียวจบ

คืนวันอังคาร สมชายแก้งานที่บ้านอีกรอบแล้ว push (ทำฝั่ง `home-laptop`):

```bash
cd ../home-laptop
echo 'print("Hello again from the home laptop")' >> app.py
git add app.py
git commit -m "Update app.py from home laptop"
git push
```

**Expected Output**

```
[main 7aab544] Update app.py from home laptop
 1 file changed, 1 insertion(+)
```

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 32 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 387 bytes | 387.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/lab-sync.git
   f339d7d..7aab544  main -> main
```

เช้าวันพุธที่แลป — คราวนี้มั่นใจแล้วว่าไม่มีงานค้าง ใช้ `git pull` คำสั่งเดียว:

```bash
cd ../uni-pc
git pull
```

**Expected Output**

```
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 3 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (3/3), 367 bytes | 367.00 KiB/s, done.
From https://github.com/YOUR_USERNAME/lab-sync
   f339d7d..7aab544  main       -> origin/main
Updating f339d7d..7aab544
Fast-forward
 app.py | 1 +
 1 file changed, 1 insertion(+)
```

> 📌 อ่าน output แล้วจะเห็น**สูตรทั้งสูตรในคำสั่งเดียว**:
> ท่อนบนคือหน้าตาของ `git fetch` (จบที่ `main -> origin/main`)
> ท่อนล่างคือหน้าตาของ `git merge` (`Updating … Fast-forward`) — `pull = fetch + merge` จริงตามสไลด์หน้า 74

```bash
cat app.py
git log --oneline
```

**Expected Output**

```
print("Hello from DevTools project")
print("Hello again from the home laptop")
```

```
7aab544 (HEAD -> main, origin/main, origin/HEAD) Update app.py from home laptop
f339d7d Add how-to-run notes
395d6a8 Add app.py
0a3ff6b Initial commit
```

---

## 11) STEP 7 — สลับขา: แลปเป็นฝ่ายส่งบ้าง แล้วปิดลูป

ที่แลป สมชายจดโน้ตสรุปบทเรียน (อยู่ที่ `uni-pc` ต่อ) — คราวนี้เครื่องแลปเป็นฝ่าย **ahead** บ้าง:

```bash
echo "git pull = git fetch + git merge" > notes.txt
git add notes.txt
git commit -m "Add lab notes at university"
git status
```

**Expected Output**

```
[main 2d83061] Add lab notes at university
 1 file changed, 1 insertion(+)
 create mode 100644 notes.txt
```

```
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

> 📌 ครบทั้งสองทิศแล้ว: **behind → แก้ด้วย `pull`** (STEP 3–6) · **ahead → แก้ด้วย `push`** (ตอนนี้)

```bash
git push
git status
```

**Expected Output**

```
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 32 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 309 bytes | 309.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
To https://github.com/YOUR_USERNAME/lab-sync.git
   7aab544..2d83061  main -> main
```

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

ปิดลูป: ฝั่งบ้านดึงโน้ตกลับไปด้วย `git pull` — สองเครื่องจะเห็นประวัติเดียวกันเป๊ะ:

```bash
cd ../home-laptop
git pull
git log --oneline
ls
```

**Expected Output**

```
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (1/1), done.
remote: Total 3 (delta 1), reused 3 (delta 1), pack-reused 0 (from 0)
Unpacking objects: 100% (3/3), 289 bytes | 289.00 KiB/s, done.
From https://github.com/YOUR_USERNAME/lab-sync
   7aab544..2d83061  main       -> origin/main
Updating 7aab544..2d83061
Fast-forward
 notes.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 notes.txt
```

```
2d83061 (HEAD -> main, origin/main, origin/HEAD) Add lab notes at university
7aab544 Update app.py from home laptop
f339d7d Add how-to-run notes
395d6a8 Add app.py
0a3ff6b Initial commit
```

```
README.md  app.py  howto.txt  notes.txt
```

**ตรวจบนเว็บ GitHub:** เปิดหน้า repo `lab-sync` → เห็นไฟล์ 4 ไฟล์ และตัวเลข **5 Commits**
ตรงกับ `git log --oneline` ทั้งสองเครื่อง ☁️

🎉 **สมชายทำงานสองเครื่องได้ลื่นไหลแล้ว** — เช้า pull เย็น push งานวิ่งตามตัวไปทุกที่ ไม่ต้องพก
แฟลชไดรฟ์ และรู้เสมอว่าตัวเองล้ำหน้า/ล้าหลัง GitHub อยู่กี่ก้าว

---

## 12) สรุป + Cheat Sheet

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git clone <URL> [folder]` | ยก repo+ประวัติทั้งหมดลงเครื่อง พร้อมผูก origin/upstream ให้ฟรี |
| `git branch -r` | ดู remote-tracking branches (บุ๊กมาร์ก) ที่เครื่องรู้จัก |
| `git status` | รายงาน ahead/behind — **เทียบกับบุ๊กมาร์ก ไม่ใช่ GitHub สด ๆ** |
| `git fetch` | อัปเดตบุ๊กมาร์ก `origin/main` — ไม่แตะไฟล์งาน ปลอดภัยเสมอ |
| `git log --oneline --all` | ส่องว่า `origin/main` ล้ำหน้า `main` อยู่กี่ commit หลัง fetch |
| `git merge origin/main` | นำของจากบุ๊กมาร์กเข้า branch เรา (LAB นี้เป็น Fast-forward) |
| `git pull` | ท่ารวบ = `git fetch` + `git merge` |
| `git checkout origin/main` | แอบดูสถานะที่บุ๊กมาร์ก (detached HEAD — ดูได้ กลับด้วย `git checkout main`) |

**วงจรทำงานหลายเครื่องที่ต้องจำ:** นั่งลง → `git pull` → ทำงาน → `git add` → `git commit` → `git push` ก่อนลุก ✅

## 13) Checklist ก่อนไปต่อ ✅

- [ ] clone แล้ว `git branch` ตอบ `* main` และ `git remote -v` มี origin ครบ โดย**ไม่ได้ตั้งค่าเอง**สักคำสั่ง
- [ ] เห็น `git status` ตอบ `ahead of 'origin/main' by 2 commits` ก่อน push (ฝั่ง home-laptop)
- [ ] เห็น `git status` ตอบ `up to date` ทั้งที่ GitHub มีของใหม่ (ฝั่ง uni-pc ก่อน fetch) และอธิบายได้ว่าทำไม
- [ ] หลัง `git fetch`: status เปลี่ยนเป็น `behind by 2` แต่ `ls` ยังไม่เห็นไฟล์ใหม่
- [ ] หลัง `git merge origin/main`: เห็น `Fast-forward` และไฟล์ใหม่โผล่ครบ
- [ ] อ่าน output ของ `git pull` แล้วชี้ได้ว่าท่อนไหนคือ fetch ท่อนไหนคือ merge
- [ ] `git log --oneline` ของทั้งสองโฟลเดอร์ และเลข Commits บนเว็บ GitHub ตรงกัน (5 commits)

## 14) คำถามทบทวน ❓

1. `git clone` ให้อะไรมาบ้างที่ LAB 01 ต้องทำเองถึง 3 คำสั่ง (`remote add` / `branch -M` / `push -u`)?
2. `main` กับ `origin/main` ต่างกันอย่างไร ใครเป็นคนขยับตัวชี้แต่ละตัว?
3. ทำไม `git status` ที่เครื่องแลป (STEP 3) ถึงตอบ `up to date` ทั้งที่ GitHub มีของใหม่แล้ว 2 commits?
4. output ของ `git fetch` มีบรรทัด `main -> origin/main` ส่วนของ `git push` เป็น `main -> main` — สองบรรทัดนี้ต่างกันอย่างไร?
5. ถ้ามีงานค้างยังไม่ commit อยู่ในเครื่อง ระหว่าง `git fetch` กับ `git pull` ควรใช้อะไร เพราะอะไร?
6. คำว่า `Fast-forward` ใน output ของ merge/pull แปลว่าอะไร และสถานการณ์แบบไหนที่จะ**ไม่**เป็น Fast-forward? (คำใบ้: Week 3)
7. ตอน detached HEAD (STEP 4) ไฟล์ `app.py` โผล่มา แต่พอ `git checkout main` มันหายไป — ไฟล์นั้นหายไปไหน แล้วทำไม fetch แล้วไฟล์ไม่มาเลยตั้งแต่แรก?
8. ทำไม LAB นี้ตอนสร้าง repo บนเว็บถึง**ต้องติ๊ก** "Add a README file" ทั้งที่ LAB 01 ห้ามติ๊ก?

---

*LAB 02 — Two Machines, One Project · DevTools Week 2 · expected output รันจริงบน `tuchsanai/devtools:2569_1` (git 2.43.0) กับ GitHub จริง — commit hash / จำนวน objects / ความเร็ว ของแต่ละคนจะต่างจากตัวอย่าง*
