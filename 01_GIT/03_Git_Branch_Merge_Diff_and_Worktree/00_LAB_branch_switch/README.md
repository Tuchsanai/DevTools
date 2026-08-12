# LAB 00 — The Parallel Universe 🌌
### Branch & Switch: แตกเส้นทางงานคู่ขนาน โดยไม่ทำของจริงพัง

> **Week 3 · Branches and Working with Others · LAB 00**
> เนื้อหาอ้างอิงสไลด์ `03_GIT.pdf` หน้า 4–60 · ทุก expected output รันจริงบน container `tuchsanai/devtools:2569_1` (git 2.43.0)

---

## 1) Story / Pain Point 📖

จบ Week 2 สมชายทำงานสองเครื่องผ่าน GitHub ได้คล่องแล้ว คราวนี้เขารับงานจริงชิ้นแรก: **ระบบข้อมูลร้านกาแฟของป้า** — ไฟล์เมนู ไฟล์เวลาเปิดปิด อยู่ใน repo เรียบร้อย ป้าเปิดดูได้ทุกวัน แปลว่า **โค้ดเวอร์ชันหลักต้อง "ใช้งานได้เสมอ"**

แล้วปัญหาก็มา: ป้าอยากได้ **โปรโมชั่นวันศุกร์** เพิ่มในเมนู สมชายเริ่มแก้ไฟล์ตรง ๆ … แก้ครึ่ง ๆ กลาง ๆ อยู่ ป้าโทรมาขอเปิดดูเมนู — หน้าจอป้าเจอเมนูเวอร์ชันแหว่งที่แก้ค้างไว้ 😱

| # | ปัญหา | อาการ |
|---|--------|-------|
| 1 | **แก้งานบนของจริงโดยตรง** | ฟีเจอร์ทำค้างครึ่งทาง = ของจริงพังครึ่งทาง ลูกค้าเห็นงานแหว่ง |
| 2 | **ก๊อปโฟลเดอร์หนีปัญหา** | `shop-v2/`, `shop-final/`, `shop-final-จริงๆ/` — โฟลเดอร์ท่วมเครื่อง ประวัติขาดตอน ไม่รู้อันไหนล่าสุด |
| 3 | **ไอเดียทดลองไม่มีที่อยู่** | อยากลองไอเดียบ้า ๆ ("AI ชงกาแฟ!") แต่กลัวเลอะงานหลัก เลยไม่กล้าลองอะไรเลย |
| 4 | **ทำสองงานพร้อมกันไม่ได้** | งานโปรโมชั่นยังไม่เสร็จ แต่ต้องรีบแก้เวลาเปิดร้านด่วน — สลับงานแล้วไฟล์ตีกันเอง |

**ทางแก้ = Branch.** สไลด์หน้า 8 พูดตรงประเด็น: เราต้องการวิธี *"focus on new updates without breaking old code"* — Git ให้ "จักรวาลคู่ขนาน" ของโปรเจกต์: แตกเส้นทางใหม่ไปทดลอง ทำเสร็จค่อยกลับมา ของจริงบนเส้นหลักไม่สะเทือนแม้แต่ไบต์เดียว

---

## 2) สิ่งที่จะได้เรียนรู้ 🎯

- **Branch คืออะไรกันแน่** — ไม่ใช่การก๊อปโปรเจกต์ แต่เป็นแค่ **pointer ชี้ commit** (สไลด์หน้า 10, 24)
- **HEAD** — เข็มบอกว่า "ตอนนี้เรายืนอยู่ตรงไหน" (สไลด์หน้า 28–41)
- `git branch` — สร้าง/ดู branch · `git switch` และ `git checkout` — ย้ายจักรวาล (สไลด์หน้า 44)
- `git switch -c` — สร้าง + ย้าย ในคำสั่งเดียว
- `git branch -m` เปลี่ยนชื่อ · `git branch -d` / `-D` ลบ branch พร้อมกำแพงกันพลาด 2 ชั้น (สไลด์หน้า 52–60)
- อ่าน `git log --oneline --all` ให้เห็น "หลายจักรวาล" พร้อมกัน

---

## 3) ทฤษฎี ① — สายโซ่ commit และเหตุผลที่ต้องมี branch

*(อ้างอิงสไลด์ 03_GIT.pdf หน้า 5–20)*

ทุก commit จดว่า **parent ของตัวเองคือใคร** ต่อกันเป็นโซ่เส้นเดียว:

```
started project ← added code ← more updates
```

ตราบใดที่มีเส้นเดียว ทุกการแก้ไขต้องต่อท้ายเส้นนี้ — งานทดลอง งานค้าง งานพัง ทั้งหมดปนอยู่บนเส้นเดียวกับของจริง สไลด์หน้า 11–20 เลยวาดภาพทีมที่แตกงานเป็นหลายเส้น: *New Library Version*, *New Styling*, *Performance* — ต่างคนต่างวิ่งบนเส้นของตัวเอง โดยมี **master/main** เป็นเส้นหลักที่ต้องพร้อมใช้งานเสมอ

**Branch = อิสระของเส้นทางพัฒนา** (สไลด์หน้า 9): แต่ละ branch ให้ working directory + staging area + ประวัติ เป็นของตัวเอง

## ทฤษฎี ② — Branch เป็นแค่ pointer (ของถูกที่สุดใน Git)

*(อ้างอิงสไลด์ 03_GIT.pdf หน้า 10, 24–27, 34)*

- Branch **ไม่ใช่กล่องใส่ commit** — มันคือ **ป้ายชื่อที่ชี้ไปยัง commit ปลายเส้น** (tip) หนึ่งอัน ประวัติที่เหลือไล่ตาม parent เอาเอง (สไลด์หน้า 34)
- สร้าง branch = Git สร้าง pointer ใหม่ 1 ตัว **เท่านั้น** ไม่ก๊อปไฟล์ ไม่แตะ repo ส่วนอื่นเลย (สไลด์หน้า 24) — นี่คือเหตุผลที่สร้าง branch เร็วและ "ฟรี" ต่างจากการก๊อปโฟลเดอร์ทั้งก้อน
- **master vs main** (สไลด์หน้า 21–23): `git init` สร้าง branch แรกชื่อ `master` ส่วน GitHub ใช้ชื่อ `main` — มันคือ branch ธรรมดา ๆ ที่บังเอิญเกิดก่อน เปลี่ยนชื่อได้เสมอ

## ทฤษฎี ③ — HEAD: เข็มบอกว่าเรายืนอยู่ตรงไหน

*(อ้างอิงสไลด์ 03_GIT.pdf หน้า 28–41)*

- **HEAD คือตัวชี้บอกว่าเรากำลัง "มอง" commit ไหนอยู่** — ปกติ HEAD ชี้ไปที่ *branch* แล้ว branch ชี้ไปที่ commit ต่อ: `HEAD -> main` (สไลด์หน้า 31–32)
- ไฟล์ที่เห็นในโฟลเดอร์ = snapshot ของ commit ที่ HEAD พาไปดู — **ย้าย HEAD (ด้วย switch/checkout) = ไฟล์บนโต๊ะเปลี่ยนตาม**
- commit ใหม่จะต่อจากจุดที่ HEAD ยืนอยู่ และลาก branch ปัจจุบันตามไปด้วย — ส่วน branch อื่นปักอยู่ที่เดิม (สไลด์หน้า 46–51)

---

## 4) เตรียมความพร้อม ⚙️

รัน container และ SSH เข้าไป (เหมือนทุก LAB):

```bash
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

ตั้งตัวตน (ถ้า container นี้ยังไม่เคยตั้ง) — **ใช้ชื่อ-อีเมลของตัวเอง** ตัวอย่างในเอกสารนี้ใช้ตัวตนสมมุติ `somchai-dev`:

```bash
git config --global user.name "somchai-dev"              # ← ใช้ชื่อของตัวเอง
git config --global user.email "somchai.dev@example.com" # ← ใช้อีเมลของตัวเอง
```

> LAB นี้ทำงานในเครื่องล้วน ๆ — ไม่ต้องใช้ GitHub และไม่ต้องใช้ token

---

## 5) STEP 1 — ตั้งร้าน: repo + เปลี่ยนชื่อ master → main

สร้างโปรเจกต์ร้านกาแฟของป้า และ commit แรก:

```bash
mkdir coffee-shop && cd coffee-shop
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
Initialized empty Git repository in /root/coffee-shop/.git/
```

> 📌 Git บอกเองเลยว่า branch แรกชื่อ `master` และแนะนำคำสั่งเปลี่ยนชื่อ `git branch -m` — ตรงกับสไลด์หน้า 21–23 เดี๋ยวเราใช้มันจริง ๆ ข้างล่าง

```bash
echo "Americano 45" > menu.txt
echo "Latte 55" >> menu.txt
git add menu.txt
git commit -m "Add first menu"
git branch
```

**Expected Output**

```
[master (root-commit) 41b269c] Add first menu
 1 file changed, 2 insertions(+)
 create mode 100644 menu.txt

* master
```

> 📌 `git branch` แสดง branch ทั้งหมด — ตอนนี้มีเส้นเดียวชื่อ `master` และเครื่องหมาย `*` บอกว่าเรายืนอยู่บนมัน · **commit hash (`41b269c`) ของแต่ละคนจะไม่เหมือนตัวอย่าง** — เป็นแบบนี้ทั้งเอกสาร

เปลี่ยนชื่อให้ตรงมาตรฐานที่ใช้กับ GitHub (สไลด์หน้า 23):

```bash
git branch -m master main
git branch
git log --oneline
```

**Expected Output**

```
* main

41b269c (HEAD -> main) Add first menu
```

> 📌 ใน log มีวงเล็บ `(HEAD -> main)` — นี่แหละตัวละครหลักของ LAB นี้: **HEAD ชี้ไป branch `main` และ `main` ชี้ commit นี้** (สไลด์หน้า 31)

แอบเปิดดูไส้ในสักนิด — HEAD เป็นแค่ไฟล์ข้อความจริง ๆ:

```bash
cat .git/HEAD
```

**Expected Output**

```
ref: refs/heads/main
```

เพิ่ม commit ที่สองไว้เป็นฐาน:

```bash
echo "Open daily 07:00 - 17:00" > hours.txt
git add hours.txt
git commit -m "Add opening hours"
git log --oneline
```

**Expected Output**

```
[main 4f2b390] Add opening hours
 1 file changed, 1 insertion(+)
 create mode 100644 hours.txt

4f2b390 (HEAD -> main) Add opening hours
41b269c Add first menu
```

---

## 6) STEP 2 — งานโปรโมชั่นมา: สร้าง branch (แต่ยังไม่ย้าย!)

ป้าสั่งงานโปรโมชั่นวันศุกร์ — สมชายจะไม่แตะ `main` ตรง ๆ อีกแล้ว:

```bash
git branch feature-promo
git branch
git log --oneline
```

**Expected Output**

```
  feature-promo
* main

4f2b390 (HEAD -> main, feature-promo) Add opening hours
41b269c Add first menu
```

> 📌 อ่านให้ครบ 2 จุด: ① `*` ยังอยู่ที่ `main` — **`git branch <name>` สร้าง pointer ใหม่เฉย ๆ ไม่พาเราย้ายไปไหน** ② ใน log ทั้ง `HEAD -> main` และ `feature-promo` เกาะอยู่บน **commit เดียวกัน** — branch ใหม่คือป้ายชื่ออีกป้ายบน commit เดิม ไม่มีการก๊อปไฟล์ใด ๆ (สไลด์หน้า 24–27)

---

## 7) STEP 3 — ย้ายจักรวาล: git switch แล้วทำงานบน branch

```bash
git switch feature-promo
cat .git/HEAD
git branch
```

**Expected Output**

```
Switched to branch 'feature-promo'

ref: refs/heads/feature-promo

* feature-promo
  main
```

> 📌 สิ่งเดียวที่เปลี่ยนคือ **HEAD หันไปชี้ `feature-promo`** (ดูได้จากไฟล์ `.git/HEAD` ตรง ๆ) — ตรงภาพสไลด์หน้า 37–38 ที่ HEAD ย้ายไปเกาะ branch ใหม่

ทำงานโปรโมชั่นตามปกติ — วงจร edit → add → commit เดิมที่คุ้นเคย:

```bash
echo "PROMO: Friday - Latte buy 1 get 1 free" >> menu.txt
cat menu.txt
git add menu.txt
git commit -m "Add Friday promo"
git log --oneline
```

**Expected Output**

```
Americano 45
Latte 55
PROMO: Friday - Latte buy 1 get 1 free

[feature-promo 1786c2b] Add Friday promo
 1 file changed, 1 insertion(+)

1786c2b (HEAD -> feature-promo) Add Friday promo
4f2b390 (main) Add opening hours
41b269c Add first menu
```

> 📌 commit ใหม่ลาก `feature-promo` ขยับไปข้างหน้า แต่ **`(main)` ยังปักอยู่ commit เดิม** — สองป้ายแยกจากกันแล้ว (สไลด์หน้า 50)

---

## 8) STEP 4 — โมเมนต์จักรวาลคู่ขนาน: switch กลับแล้วไฟล์ "เปลี่ยนเอง"

ระหว่างนั้นป้าโทรมา: *"เดี๋ยวก่อน ขอดูเมนูจริงหน่อย โปรยังไม่ประกาศนะ!"* — กลับจักรวาลหลัก:

```bash
git switch main
cat menu.txt
git log --oneline
```

**Expected Output**

```
Switched to branch 'main'

Americano 45
Latte 55

4f2b390 (HEAD -> main) Add opening hours
41b269c Add first menu
```

> 🌌 **บรรทัดโปรโมชั่นหายไปจากไฟล์!** ไม่ใช่งานหาย — งานอยู่ครบใน `feature-promo` แต่ HEAD พาเรากลับมาดู snapshot ของ `main` ซึ่งไม่เคยมีโปรโมชั่น · ป้าเห็นเมนูจริงเนี้ยบ ๆ ส่วนงานค้างอยู่อีกจักรวาลอย่างปลอดภัย — **Pain Point ข้อ 1 หายทันที**

อยากเห็นทุกจักรวาลพร้อมกัน ใช้ `--all`:

```bash
git log --oneline --all
```

**Expected Output**

```
1786c2b (feature-promo) Add Friday promo
4f2b390 (HEAD -> main) Add opening hours
41b269c Add first menu
```

**`git checkout` — คำสั่งรุ่นพี่ที่เจอบ่อยในโลกจริง** (สไลด์หน้า 44 ให้ใช้ได้ทั้งคู่): `git checkout <branch>` ย้าย branch ได้เหมือน `git switch` ทุกประการ — ลองสลับด้วย checkout ดูบ้าง:

```bash
git checkout feature-promo
cat menu.txt
git checkout main
```

**Expected Output**

```
Switched to branch 'feature-promo'

Americano 45
Latte 55
PROMO: Friday - Latte buy 1 get 1 free

Switched to branch 'main'
```

> 💡 `switch` เป็นคำสั่งรุ่นใหม่ที่แยกงาน "ย้าย branch" ออกมาจาก `checkout` (ซึ่งทำได้สารพัดจนสับสน) — ใช้ `switch` เป็นหลักได้เลย แต่ต้องอ่าน `checkout` ให้ออกเพราะเอกสาร/เพื่อนร่วมทีมยังใช้กันทั่วไป

---

## 9) STEP 5 — ไอเดียบ้า: branch ทดลองด้วย git switch -c

สมชายอยากลองไอเดียเพี้ยน ๆ: **AI barista คุยกับลูกค้า** — ไม่แน่ใจว่าจะรอด เปิดจักรวาลทดลองใหม่ด้วยทางลัด (สร้าง + ย้าย ในคำสั่งเดียว):

```bash
git switch -c experimental
echo "TODO: AI barista that talks to customers" > idea.txt
git add idea.txt
git commit -m "Experiment: AI barista"
git log --oneline --all
```

**Expected Output**

```
Switched to a new branch 'experimental'

[experimental fa1fc4b] Experiment: AI barista
 1 file changed, 1 insertion(+)
 create mode 100644 idea.txt

fa1fc4b (HEAD -> experimental) Experiment: AI barista
1786c2b (feature-promo) Add Friday promo
4f2b390 (main) Add opening hours
41b269c Add first menu
```

> 📌 ตอนนี้มี 3 จักรวาล: `main` (ของจริง) · `feature-promo` (งานป้า) · `experimental` (ไอเดียบ้า) — ตรงภาพสไลด์หน้า 53 เป๊ะ และ **Pain Point ข้อ 3–4 หายแล้ว**: ทดลองได้ ทำหลายงานสลับได้ ไม่มีอะไรตีกัน

---

## 10) STEP 6 — ไอเดียแป้ก: เปลี่ยนชื่อ แล้วลบทิ้งให้เป็น

หนึ่งสัปดาห์ผ่านไป… AI barista ไปไม่รอด 😅 สมชายตั้งชื่อ branch ใหม่ให้สมศักดิ์ศรีก่อนลบ (ตามสไลด์หน้า 55 เป๊ะ ๆ) — `git branch -m <ชื่อใหม่>` ที่ไม่ใส่ชื่อเก่า = เปลี่ยนชื่อ **branch ที่ยืนอยู่**:

```bash
git branch -m please_delete
git branch
```

**Expected Output**

```
  feature-promo
  main
* please_delete
```

ลองลบทั้งที่ยังยืนอยู่บนมัน — **กำแพงชั้นที่ 1**:

```bash
git branch -d please_delete
```

**Expected Output**

```
error: cannot delete branch 'please_delete' used by worktree at '/root/coffee-shop'
```

> 🧱 สไลด์หน้า 58: *"You can not delete a branch you are checked out at"* — ลบพื้นที่ตัวเองยืนอยู่ไม่ได้ ต้องถอยออกก่อน

ถอยไป `main` แล้วลองใหม่ — **กำแพงชั้นที่ 2**:

```bash
git switch main
git branch -d please_delete
```

**Expected Output**

```
Switched to branch 'main'

error: the branch 'please_delete' is not fully merged.
If you are sure you want to delete it, run 'git branch -D please_delete'
```

> 🧱 งานใน branch นี้**ยังไม่เคยถูกรวมกลับ** (not fully merged) — ลบแล้วงานหายถาวรนะ Git เลยขอใบยืนยัน: ต้องใช้ `-D` ตัวใหญ่ (สไลด์หน้า 57–58)

สมชายมั่นใจ — ไอเดียนี้ไม่เอาแล้วจริง ๆ:

```bash
git branch -D please_delete
git branch
git log --oneline --all
ls
```

**Expected Output**

```
Deleted branch please_delete (was fa1fc4b).

  feature-promo
* main

1786c2b (feature-promo) Add Friday promo
4f2b390 (HEAD -> main) Add opening hours
41b269c Add first menu

hours.txt
menu.txt
```

> 📌 commit `fa1fc4b` หายไปจาก log และ `idea.txt` ไม่อยู่ในโฟลเดอร์ — จักรวาลทดลองถูกพับเก็บสะอาดหมดจด ส่วน `main` และ `feature-promo` ไม่สะเทือนเลย
>
> ⏭️ สังเกตว่า `feature-promo` (งานโปรโมชั่นที่**เสร็จแล้ว**) ยังค้างอยู่ — จะเอากลับเข้า `main` ยังไง? นั่นคือเรื่องของ **LAB 01: Merge Day**

---

## 11) สรุป + Cheat Sheet 📋

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git branch` | ดู branch ทั้งหมด (`*` = จุดที่ยืนอยู่) |
| `git branch <name>` | สร้าง branch ใหม่ (pointer ใหม่ — **ไม่ย้ายตัวเราไป**) |
| `git switch <name>` | ย้ายไป branch นั้น (HEAD ย้าย + ไฟล์บนโต๊ะเปลี่ยนตาม) |
| `git switch -c <name>` | สร้าง + ย้าย ในคำสั่งเดียว |
| `git checkout <name>` | ย้าย branch แบบคำสั่งรุ่นพี่ — ผลเหมือน `switch` |
| `git branch -m <old> <new>` / `git branch -m <new>` | เปลี่ยนชื่อ branch (แบบหลัง = เปลี่ยนชื่อ branch ปัจจุบัน) |
| `git branch -d <name>` | ลบ branch (ยอมลบเฉพาะที่ merge แล้ว + ต้องไม่ยืนอยู่บนมัน) |
| `git branch -D <name>` | บังคับลบทั้งที่ยังไม่ merge — งานใน branch หายถาวร |
| `git log --oneline --all` | ดูทุก branch พร้อมกัน + ตำแหน่ง `(HEAD -> ...)` |
| `cat .git/HEAD` | แอบดูว่า HEAD ชี้ branch ไหน (ไฟล์ข้อความธรรมดา) |

**ภาพจำ:** commit = ข้อต่อโซ่ · branch = ป้ายชื่อชี้ปลายโซ่ · HEAD = เข็มบอกว่าเรายืนป้ายไหน · switch = ย้ายเข็ม (ไฟล์เปลี่ยนตาม)

---

## 12) Checklist ✅

- [ ] อธิบายได้ว่า branch คือ pointer — สร้างแล้ว `git log` เห็น 2 ป้ายบน commit เดียว (STEP 2)
- [ ] เห็นว่า `git branch <name>` ไม่ย้ายตัวเรา (`*` ค้างที่ `main`)
- [ ] `cat .git/HEAD` แล้วชี้ได้ว่า HEAD เปลี่ยนตอน switch
- [ ] เห็นโมเมนต์ไฟล์ "หาย/โผล่" ตอน switch ไป-กลับ และอธิบายได้ว่าทำไม (STEP 4)
- [ ] ใช้ได้ทั้ง `git switch` และ `git checkout` และรู้ว่าคู่นี้แทนกันได้
- [ ] เจอกำแพง 2 ชั้นตอนลบ branch: ยืนอยู่บนมัน / ยังไม่ merge — และผ่านมันด้วย `git switch` + `-D`
- [ ] จบ LAB เหลือ 2 branch: `main` และ `feature-promo` (เก็บไว้ต่อ LAB 01)

---

## 13) คำถามทบทวน ❓

1. Branch ใน Git คืออะไรกันแน่ — ทำไมการสร้าง branch ถึงเร็วกว่าก๊อปโฟลเดอร์โปรเจกต์มหาศาล?
2. `git branch feature-x` กับ `git switch -c feature-x` ให้ผลต่างกันอย่างไร?
3. HEAD คืออะไร และตอน `git switch` เกิดอะไรขึ้นกับ HEAD / ไฟล์ในโฟลเดอร์?
4. ตอนอยู่บน `feature-promo` แล้ว commit — ทำไม `(main)` ใน log ไม่ขยับตาม?
5. STEP 4 บรรทัดโปรโมชั่น "หายไป" จาก `menu.txt` — งานหายจริงไหม? อยู่ที่ไหน?
6. กำแพง 2 ชั้นของ `git branch -d` มีอะไรบ้าง แต่ละชั้นป้องกันความผิดพลาดแบบไหน?
7. หลัง `git branch -D please_delete` แล้ว commit `fa1fc4b` ไปไหน? ถ้าเป็น branch ที่ merge แล้ว การลบป้ายชื่อทำให้งานหายไหม?
8. ทำไม `git init` ถึงได้ branch ชื่อ `master` แต่ GitHub ใช้ `main` — และเราแก้ให้ตรงกันด้วยคำสั่งอะไร?

---

*LAB 00 — The Parallel Universe · DevTools Week 3 · expected output ทุกจุดรันจริงบน `tuchsanai/devtools:2569_1` (git 2.43.0) — commit hash ของแต่ละคนจะต่างจากตัวอย่าง · ตัวอย่างใช้ตัวตนสมมุติ `somchai-dev` — ใช้ชื่อและอีเมลของตัวเองเสมอ*
