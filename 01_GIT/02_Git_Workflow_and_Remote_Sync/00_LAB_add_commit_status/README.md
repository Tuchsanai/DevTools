# LAB 00 — The Time Machine · `add` / `commit` / `status` (Local Workflow)

> **Week 2 · Getting Started with Git** — อ้างอิงสไลด์ `02_GIT.pdf` หน้า 12–31 และ `git_week2.html`
> expected output ทุกจุดรันจริงบน container `tuchsanai/devtools:2569_1` (git 2.43.0)

---

## 1) Story / Pain Point 📖

คืนก่อนส่งงาน สมชาย (`somchai-dev`) นั่งแก้โปรเจกต์ถึงตีสอง แก้ไปแก้มา…โค้ดที่เคยรันได้**พังกว่าเดิม**
อยากย้อนกลับไป "เวอร์ชันเมื่อวานที่ยังรันได้" แต่กด Ctrl+Z ย้อนไม่ถึงแล้ว สุดท้ายโฟลเดอร์เต็มไปด้วย

```
project_final.zip
project_final_v2.zip
project_final_v2_จริงๆ.zip
project_final_v2_จริงๆ_ล่าสุด.zip
```

**Pain Point ที่เกิดขึ้น:**

| # | ปัญหา | อาการ |
|---|-------|-------|
| 1 | ย้อนเวลาไม่ได้ | แก้โค้ดพังแล้วกลับไปเวอร์ชันที่เคยรันได้ไม่ได้ |
| 2 | ไม่รู้ประวัติ | ตอบไม่ได้ว่า "แก้ไฟล์ไหน เมื่อไหร่ เพราะอะไร" |
| 3 | สำเนาท่วมเครื่อง | ก๊อปทั้งโฟลเดอร์เก็บไว้หลายชุด เปลืองที่และสับสน |
| 4 | ไม่รู้สถานะ | ไม่รู้ว่าไฟล์ไหนแก้แล้วยังไม่ได้บันทึก ไฟล์ไหนเรียบร้อยแล้ว |

**ทางแก้ = Git.** ทุกครั้งที่งานถึงจุดที่ "ดีแล้ว" เราสั่ง `git commit` เพื่อถ่ายรูป (snapshot) ทั้งโปรเจกต์เก็บไว้
อยากรู้ว่าตอนนี้มีอะไรค้างอยู่ → `git status` · อยากดูประวัติ → `git log` · อยากย้อนเวลา → ทำได้ (Week 4)

---

## 2) สิ่งที่จะได้เรียนรู้ 🎯

- วงจรพื้นฐานของ Git: **แก้ไฟล์ → `git add` → `git commit`** ทำซ้ำ 3 รอบจนเป็นนิสัย
- สามพื้นที่ของ Git: **Working Directory → Staging Area → Repository**
- สถานะของไฟล์: **untracked → staged → committed → modified**
- ใช้ `git status` เป็น "เข็มทิศ" และ `git log` เป็น "สมุดประวัติ"
- รู้จักชื่อ branch เริ่มต้น `master` และที่มาของชื่อ `main` (จะใช้จริงใน LAB 01)

---

## 3) ทฤษฎี ①: Commit = Snapshot ของทั้งโปรเจกต์

*(สไลด์หน้า 12–15, 37)*

- โปรเจกต์เดินหน้าเป็นก้อน ๆ : `Initial Project → Add Code → More Code → …`
  แต่ละก้อนที่เราบอก Git ให้จดจำ เรียกว่า **commit**
- commit **ไม่ใช่** การเซฟทีละไฟล์ — หนึ่ง commit เก็บการเปลี่ยนแปลง**ทั้ง working directory**
  (เช่นแก้ `program.py`, `index.html`, `style.css` พร้อมกันก็อยู่ใน commit เดียวได้)
- ทุก commit มี 3 อย่างเสมอ: **hash** (เลขประจำตัว เช่น `678e366…`), **message** (คำอธิบาย)
  และ **parent** (ชี้กลับไป commit ก่อนหน้า) → ต่อกันเป็นสายโซ่ประวัติ ทำให้ย้อนกลับ commit เก่าได้

## 3.1) ทฤษฎี ②: สามพื้นที่ของ Git

*(สไลด์หน้า 17–31)*

```
 Working Directory          Staging Area            Repository
 (โต๊ะทำงาน)                (ตะกร้าเตรียมถ่ายรูป)      (อัลบั้มถาวร)
 ┌───────────────┐  git add  ┌──────────────┐ git commit ┌──────────────┐
 │ file1.txt ✏️  │ ────────► │ file1.txt    │ ─────────► │ snapshot #1  │
 │ file2.txt ✏️  │           │ file2.txt    │            │ snapshot #2  │
 │ file3.txt ✏️  │           │ (เฉพาะที่เลือก)│            │   ...        │
 └───────────────┘           └──────────────┘            └──────────────┘
```

- **Working Directory** — โฟลเดอร์จริงที่เราแก้ไฟล์
- **Staging Area** — พื้นที่พัก "เลือกเฉพาะไฟล์" ที่จะบันทึกใน commit ถัดไป (`git add`)
  ประโยชน์: แก้ 3 ไฟล์ แต่จะ commit แค่ 2 ไฟล์ก็ได้ (ได้ลองจริงใน STEP 2)
- **Repository** (`.git/`) — ที่เก็บ snapshot ถาวรทุก commit (`git commit`)

**สถานะของไฟล์ที่ `git status` รายงาน:**

| สถานะ | ความหมาย |
|--------|-----------|
| `Untracked files` | ไฟล์ใหม่ Git ยังไม่รู้จัก |
| `Changes to be committed` | อยู่ใน staging แล้ว รอ commit |
| `Changes not staged for commit` | ไฟล์ที่เคย commit ถูกแก้ (modified) แต่ยังไม่ `git add` |
| `nothing to commit, working tree clean` | ทุกอย่างถูกบันทึกครบแล้ว |

---

## 4) เตรียมความพร้อม ⚙️

รัน container สำหรับทดลอง แล้ว SSH เข้าไป:

```bash
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

Git ต้องรู้ก่อนว่า "เราเป็นใคร" จึงจะ commit ได้ (ทำแล้วใน LAB Configure ของ Week 1 —
เครื่องใหม่ต้องตั้งใหม่ทุกครั้ง) **ใช้ชื่อ-อีเมลของตัวเอง** ในที่นี้ใช้ตัวตนสมมุติ:

```bash
git config --global user.name "somchai-dev"
git config --global user.email "somchai.dev@example.com"
git config --global --list
```

**Expected Output**

```
user.name=somchai-dev
user.email=somchai.dev@example.com
```

> ⚠️ ถ้าข้าม step นี้ `git commit` จะล้มเหลวพร้อมข้อความ `Author identity unknown`

---

## 5) STEP 1 — สร้าง repo แรก + commit แรก

สร้างโฟลเดอร์ แล้วประกาศให้ Git เริ่มจับตาดู:

```bash
mkdir git-lab
cd git-lab
git init
```

**Expected Output**

```
hint: Using 'master' as the name for the initial branch. This default branch name
hint: is subject to change. To configure the initial branch name to use in all
hint: of your new repositories, which will suppress this warning, call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
Initialized empty Git repository in /workspace/git-lab/.git/
```

### 💡 master vs main — hint นี้บอกอะไรเรา?

- branch เริ่มต้นของ Git ใช้ชื่อ **`master`** มาแต่เดิม แต่ **GitHub เปลี่ยนธรรมเนียมเป็น `main`**
  (สไลด์หน้า 43) — repo ที่สร้างบนเว็บ GitHub ทุกวันนี้จึงชื่อ `main`
- LAB นี้ทำงานใน**เครื่องตัวเองล้วน ๆ** ชื่อ branch จึงยังไม่มีผลอะไร ใช้ `master` ต่อไปได้
- แต่ LAB 01 เราจะ push ขึ้น GitHub ถ้าปล่อยให้ local เป็น `master` ส่วน GitHub เป็น `main`
  จะกลายเป็น**คนละ branch ไม่เจอกัน** → LAB 01 จะแก้ด้วย `git branch -M main`
- ถ้าเคยตั้ง `git config --global init.defaultBranch main` ไว้ (LAB Configure Week 1)
  เครื่องคุณจะ**ไม่เห็น hint นี้** และ branch จะชื่อ `main` ตั้งแต่แรก — ถูกต้องเช่นกัน

สร้างไฟล์ 3 ไฟล์ แล้วถาม "เข็มทิศ" ว่าเห็นอะไร:

```bash
echo "Content for file 1" > file1.txt
echo "Content for file 2" > file2.txt
echo "Content for file 3" > file3.txt
git status
```

**Expected Output**

```
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	file1.txt
	file2.txt
	file3.txt

nothing added to commit but untracked files present (use "git add" to track)
```

ไฟล์ทั้งสามเป็น **untracked** — Git เห็นว่ามีไฟล์ใหม่ แต่ยังไม่จับตาดูจนกว่าจะสั่ง `git add`:

```bash
git add file1.txt file2.txt file3.txt
git status
```

**Expected Output**

```
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   file1.txt
	new file:   file2.txt
	new file:   file3.txt
```

> 💡 **ทางลัดที่ใช้บ่อยในงานจริง:** `git add .` = stage ทุกไฟล์ที่เปลี่ยนในโฟลเดอร์รวดเดียว (สไลด์หน้า 28)
> ใน LAB นี้ตั้งใจ add ทีละไฟล์ เพื่อให้เห็นชัดว่า Staging Area "เลือกได้" — พอคล่องแล้วค่อยใช้ทางลัด

ทั้งสามไฟล์ย้ายเข้า **Staging Area** แล้ว (`Changes to be committed`) — กดชัตเตอร์ถ่าย snapshot:

```bash
git commit -m "Initial commit with three files"
```

**Expected Output**

```
[master (root-commit) 678e366] Initial commit with three files
 3 files changed, 3 insertions(+)
 create mode 100644 file1.txt
 create mode 100644 file2.txt
 create mode 100644 file3.txt
```

> 📌 `678e366` คือ commit hash — **ของแต่ละคนจะไม่เหมือนกัน** (คำนวณจากเนื้อหา+ผู้เขียน+เวลา)
> `root-commit` = commit แรกสุดของ repo (ยังไม่มี parent)

ตรวจสอบผลด้วยเข็มทิศ + สมุดประวัติ:

```bash
git status
git log
```

**Expected Output**

```
On branch master
nothing to commit, working tree clean
```

```
commit 678e3667ca4fd037059c249d2f2d1bfda0e2a13e
Author: somchai-dev <somchai.dev@example.com>
Date:   Tue Jul 14 04:27:03 2026 +0700

    Initial commit with three files
```

> hash / Author / Date จะเป็นของคุณเอง ไม่ตรงกับตัวอย่าง

---

## 6) STEP 2 — แก้ 2 ไฟล์ แล้วเลือก stage เฉพาะที่ต้องการ

เพิ่มเนื้อหาต่อท้าย (`>>` = append) เฉพาะ file1 กับ file2:

```bash
echo "Additional content for file 1" >> file1.txt
echo "Additional content for file 2" >> file2.txt
git status
```

**Expected Output**

```
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   file1.txt
	modified:   file2.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

สถานะเปลี่ยนจาก `untracked` เป็น **`modified`** — Git รู้จักไฟล์แล้ว และเห็นว่ามันต่างจาก snapshot ล่าสุด
สังเกตว่า `file3.txt` ไม่ถูกพูดถึงเลย เพราะไม่ได้แก้

```bash
git add file1.txt file2.txt
git commit -m "Updated file1 and file2"
git status
git log
```

**Expected Output**

```
[master bce79d5] Updated file1 and file2
 2 files changed, 2 insertions(+)
```

```
On branch master
nothing to commit, working tree clean
```

```
commit bce79d5014174e2659bdb75c6447276af43193fd
Author: somchai-dev <somchai.dev@example.com>
Date:   Tue Jul 14 04:27:03 2026 +0700

    Updated file1 and file2

commit 678e3667ca4fd037059c249d2f2d1bfda0e2a13e
Author: somchai-dev <somchai.dev@example.com>
Date:   Tue Jul 14 04:27:03 2026 +0700

    Initial commit with three files
```

> 📌 `git log` แสดง commit **ใหม่สุดอยู่บนสุด** — ตอนนี้สายโซ่ประวัติมี 2 ข้อแล้ว

---

## 7) STEP 3 — ปิดจ๊อบ file3 + commit สุดท้าย

```bash
echo "Additional content for file 3" >> file3.txt
git status
```

**Expected Output**

```
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   file3.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

```bash
git add file3.txt
git commit -m "Final update to file3"
git status
```

**Expected Output**

```
[master 1411fe8] Final update to file3
 1 file changed, 1 insertion(+)
```

```
On branch master
nothing to commit, working tree clean
```

ดูประวัติทั้งเส้น — แบบเต็มและแบบย่อ:

```bash
git log
git log --oneline
```

**Expected Output**

```
commit 1411fe801d13e08325bad883c3d758ded7b1947e
Author: somchai-dev <somchai.dev@example.com>
Date:   Tue Jul 14 04:27:03 2026 +0700

    Final update to file3

commit bce79d5014174e2659bdb75c6447276af43193fd
Author: somchai-dev <somchai.dev@example.com>
Date:   Tue Jul 14 04:27:03 2026 +0700

    Updated file1 and file2

commit 678e3667ca4fd037059c249d2f2d1bfda0e2a13e
Author: somchai-dev <somchai.dev@example.com>
Date:   Tue Jul 14 04:27:03 2026 +0700

    Initial commit with three files
```

```
1411fe8 Final update to file3
bce79d5 Updated file1 and file2
678e366 Initial commit with three files
```

🎉 **สมชายมี time machine แล้ว** — ประวัติ 3 จุดที่ย้อนกลับได้เสมอ ไม่ต้องมี `final_v2_จริงๆ.zip` อีกต่อไป

---

## 8) สรุป + Cheat Sheet

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git init` | เริ่มให้ Git จับตาดูโฟลเดอร์นี้ (สร้าง `.git/`) |
| `git status` | เข็มทิศ: ไฟล์ไหน untracked / modified / staged |
| `git add <file>` | ย้ายไฟล์เข้า Staging Area (เลือกเป็นรายไฟล์ได้) |
| `git commit -m "msg"` | ถ่าย snapshot จาก Staging เข้า Repository |
| `git log` / `git log --oneline` | ดูประวัติ commit (ใหม่สุดอยู่บน) |

**วงจรที่ต้องจำ:** แก้ไฟล์ → `git status` → `git add` → `git commit -m` → `git status`/`git log` ✅

## 9) Checklist ก่อนไปต่อ ✅

- [ ] `git status` หลังสร้างไฟล์ใหม่ เห็น `Untracked files` ครบ 3 ไฟล์
- [ ] `git status` หลัง `git add` เห็น `Changes to be committed`
- [ ] commit สำเร็จ 3 ครั้ง และ `git status` ตอบ `working tree clean` ทุกครั้ง
- [ ] STEP 2 stage เฉพาะ file1/file2 ได้ โดย file3 ไม่ติดเข้าไปด้วย
- [ ] `git log --oneline` แสดง 3 บรรทัด เรียงใหม่ → เก่า
- [ ] อธิบายเส้นทาง Working Directory → Staging → Repository ได้

## 10) คำถามทบทวน ❓

1. ไฟล์สถานะ `untracked` กับ `modified` ต่างกันอย่างไร?
2. ทำไม Git ต้องมี Staging Area — commit ตรงจาก Working Directory ไม่ได้หรือ? ยกสถานการณ์ที่ staging ช่วยได้
3. ใน STEP 2 ถ้าเผลอสั่ง `git add file3.txt` ไปด้วย จะถอนออกจาก staging ด้วยคำสั่งอะไร (ดูใน output ของ `git status` เอง!)
4. commit hash ของเพื่อนกับของเราไม่เหมือนกันทั้งที่พิมพ์คำสั่งเดียวกันทุกตัว — เพราะอะไร?
5. hint ตอน `git init` แนะนำให้ตั้งค่าอะไร ถ้าอยากให้ branch เริ่มต้นชื่อ `main` ถาวรทุก repo?
6. ถ้าอยากรู้ว่า commit ล่าสุดแก้ไฟล์อะไรไปบ้าง ควรใช้คำสั่งไหนดู?

---

*LAB 00 — The Time Machine · DevTools Week 2 · expected output รันจริงบน `tuchsanai/devtools:2569_1` (git 2.43.0) — commit hash/วันเวลา ของแต่ละคนจะต่างจากตัวอย่าง*
