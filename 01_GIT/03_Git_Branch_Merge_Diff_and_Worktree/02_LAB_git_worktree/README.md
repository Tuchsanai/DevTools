# LAB 02 — Shadow Clone 🥷
### Git Worktree: ทำงานหลาย branch พร้อมกัน โดยไม่ต้องสลับไปมา

> **Week 3 · Branches and Working with Others · LAB 02**
> เนื้อหาอ้างอิงสไลด์ `week3-Git worktree slides.pdf` (Git Worktree Slides) · ทุก expected output รันจริงบน container `tuchsanai/devtools:2569_1` (git 2.54.0)

---

## 1) Story / Pain Point 📖

จบ [LAB 01](../01_LAB_merge_conflict/README.md) สมชายแตก branch–merge–ดับ conflict ได้ครบวงจร ร้านป้าไปได้สวย… จนวันหนึ่ง:

สมชายกำลังทำ **เมนูใหม่** อยู่บน branch `feature-newmenu` — พิมพ์เมนูโกโก้ค้างอยู่ครึ่งบรรทัด ราคายังใส่ไม่เสร็จ — ป้าโทรมาเสียงสั่น: *"เวลาเปิดร้านบนหน้าเว็บผิด! ลูกค้ามารอหน้าร้านตั้งแต่ 7 โมง แต่ร้านเปิด 8 โมง แก้เดี๋ยวนี้เลยนะ!"* 🔥

งานด่วนต้องแก้บน `main` แต่สมชายยืนอยู่บน `feature-newmenu` ที่มีไฟล์แก้ค้างไม่เสร็จ — วิชา `git switch` จาก LAB 00 กลับกลายเป็นตัวปัญหาซะเอง:

| # | ปัญหา | อาการ |
|---|--------|-------|
| 1 | **switch ทั้งที่งานค้าง — Git ไม่ให้ไป** | ไฟล์แก้ครึ่งทางจะถูกเขียนทับ Git เบรกหัวทิ่ม: `would be overwritten` |
| 2 | **จำใจ commit งานครึ่งทาง (WIP commit)** | ต้อง `git commit -am "WIP: ยังไม่เสร็จ"` ทิ้งไว้ก่อน แล้วค่อยแกะกลับมาทำต่อ — ประวัติเลอะ สมาธิหลุด |
| 3 | **สลับกลับมาแล้ว…เมื่อกี้ทำถึงไหนนะ** | ทุกครั้งที่สลับ branch คือการรื้อโต๊ะทำงานทิ้งทั้งโต๊ะ แล้วจัดใหม่ — context หายเกลี้ยง |
| 4 | **โปรเจกต์ใหญ่ สลับทีเจ็บที** | dependencies / build cache ถูกเขียนทับทุกครั้งที่ checkout ข้าม branch — บางทีมรอ build เป็นสิบนาทีต่อการสลับหนึ่งครั้ง |

**ทางแก้ = `git worktree`.** ไม่ต้องสลับ — **เปิดโต๊ะทำงานตัวใหม่** ของ repo เดิมขึ้นมาข้าง ๆ กันเลย: โฟลเดอร์ใหม่ checkout branch ใหม่ ส่วนโต๊ะเดิมกับงานค้างครึ่งทาง **ไม่ถูกแตะต้องแม้แต่ไบต์เดียว** — เหมือนวิชาแยกเงา (Shadow Clone): ตัวจริงทำเมนูต่อ ตัวเงาไปดับไฟ 🥷

---

## 2) สิ่งที่จะได้เรียนรู้ 🎯

- **ต้นทุนของการสลับ branch** — ทำไม `git switch` ถึงไม่ตอบโจทย์งานขนาน (สไลด์ 01)
- **Git Worktree คืออะไร** — 1 repository → หลาย working directory: **SHARED · ISOLATED · CHEAP** (สไลด์ 02)
- **โครงสร้าง worktree** — main worktree + linked worktree ใช้ `.git` ก้อนเดียวกัน และกติกา **หนึ่ง branch ต่อหนึ่ง worktree** (สไลด์ 03)
- `git worktree add` ครบ 3 ท่า: checkout branch เดิม · `-b` สร้าง branch ใหม่ · `--detach` ย้อนดู commit เก่า (สไลด์ 04)
- `git worktree list` / `remove` / `prune` — จัดการวงจรชีวิต worktree (สไลด์ 05)
- **Workflow hotfix ด่วน** ของจริงตั้งแต่เปิดเงาจนเก็บกวาด (สไลด์ 06)
- ทวนวิชา LAB 01: Fast-forward + 3-way merge ในสถานการณ์จริง
- ข้อควรระวัง: ลบ directory ตรง ๆ ไม่ได้ · untracked files ไม่ตามไปด้วย (สไลด์ 09)

---

## 3) ทฤษฎี ① — ต้นทุนที่มองไม่เห็นของ `git switch`

*(อ้างอิงสไลด์ 01 · THE PROBLEM)*

LAB 00 สอนว่า switch = ย้ายจักรวาล แต่มีรายละเอียดที่เพิ่งจะกัดเราวันนี้: **ทุกจักรวาลใช้ "โต๊ะทำงาน" (working directory) ตัวเดียวกัน** การ switch คือการรื้อไฟล์บนโต๊ะทิ้งแล้ววางไฟล์ของ branch ใหม่แทน ดังนั้น:

- งานที่ยังไม่ commit **ขวางทาง switch** — Git ยอมให้ไปเฉพาะเมื่อพกงานค้างข้ามไปได้โดยไม่ทับอะไร ถ้าทับ → `error: Your local changes ... would be overwritten`
- ทางหนีแบบเดิมคือ **WIP commit**: `git commit -am "WIP: ยังไม่เสร็จ"` แล้วค่อยแกะกลับ (ด้วยวิชา reset ที่ยังไม่เรียน) — ทำได้ แต่ประวัติรก และเสี่ยงลืม
- ไฟล์ที่ Git ไม่ track (dependencies, build cache) อยู่บนโต๊ะเดียวกันด้วย — โปรเจกต์จริงสลับ branch ทีอาจต้อง build ใหม่นานหลายนาที

> 💡 **คำถามเปลี่ยนมุม:** ปัญหาไม่ใช่ "จะสลับยังไงให้เร็ว" แต่คือ **"ทำไมต้องสลับด้วยล่ะ?"** — ถ้ามีโต๊ะทำงานสองตัวพร้อมกัน ก็ไม่ต้องรื้อโต๊ะไหนเลย

## ทฤษฎี ② — Git Worktree: 1 repo → หลายโต๊ะทำงาน

*(อ้างอิงสไลด์ 02 · CONCEPT)*

**Git Worktree = 1 repository → หลาย working directory ที่ checkout branch ต่างกัน และทำงานพร้อมกันได้** คุณสมบัติ 3 ข้อที่ทำให้มันเวิร์ก:

| | ความหมาย |
|---|---|
| 🔗 **SHARED** | ทุก worktree ใช้ **object database และ refs ชุดเดียวกัน** — commit จากที่หนึ่ง เห็นได้ทันทีจากอีกที่ ไม่ต้อง push/pull หากัน |
| 🧱 **ISOLATED** | แต่ละ directory มี **ไฟล์, index และ HEAD ของตัวเอง** — แก้งานคนละ branch โดยไม่รบกวนกัน งานค้างของโต๊ะไหนอยู่โต๊ะนั้น |
| 🪶 **CHEAP** | ไม่ต้อง clone ซ้ำ — สร้างได้ในไม่กี่วินาที ใช้พื้นที่เพิ่มเฉพาะไฟล์ working copy (ไม่ก๊อป object database) |

## ทฤษฎี ③ — โครงสร้าง: main worktree + linked worktree

*(อ้างอิงสไลด์ 03 · CONCEPT)*

```
~/coffee-app            ~/hotfix                ~/time-machine
[main worktree]         [linked worktree]       [linked worktree]
 branch: feature-...     branch: hotfix-...      detached HEAD
        \                      |                      /
         \                     |                     /
          `------->  ~/coffee-app/.git  <-----------'
        object database + refs + config — ใช้ร่วมกันทุก worktree
```

- โฟลเดอร์ที่ `git init` ไว้แต่แรก = **main worktree** — เจ้าของ `.git` ตัวจริง
- โฟลเดอร์ที่เพิ่มด้วย `git worktree add` = **linked worktree** — ข้างในไม่มี `.git` เต็ม ๆ มีแค่ **ไฟล์จดที่อยู่** ชี้กลับไปหา `.git` ของ main worktree (เดี๋ยวได้เปิดดูของจริงใน STEP 5)
- **กติกาสำคัญ: หนึ่ง branch ถูก checkout ได้ในหนึ่ง worktree เท่านั้น** — กันไม่ให้สองโต๊ะแก้ branch เดียวกันซ้อนกันจนประวัติพัง (เดี๋ยวได้ชนกำแพงจริงใน STEP 6)

## ทฤษฎี ④ — Worktree เทียบกับทางเลือกอื่น

*(อ้างอิงสไลด์ 08 · COMPARISON)*

| | สลับ branch ใน directory เดียว | clone หลายชุด | **git worktree** |
|---|---|---|---|
| ทำงานหลาย branch พร้อมกัน | ไม่ได้ | ได้ | **ได้** |
| เวลา setup | ทันที | ช้า — ดาวน์โหลดทั้ง repo | **ไม่กี่วินาที** |
| disk space | น้อยที่สุด | เต็ม repo ต่อชุด | **เฉพาะ working copy** |
| branch / refs ตรงกันเสมอ | ใช่ — repo เดียว | ต้อง fetch / push เอง | **ใช่ — แชร์ refs กัน** |
| เหมาะกับ | งานเดี่ยวตามลำดับ | โปรเจกต์แยกขาดถาวร | **งานขนานใน repo เดิม** |

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

จำ hint ยาว ๆ ตอน `git init` ใน LAB 00 ได้ไหม? Git แนะนำวิธีตั้งชื่อ branch แรกให้เป็น `main` อัตโนมัติ — ได้เวลาใช้จริง จะได้ไม่ต้อง `git branch -m` ทุกรอบ:

```bash
git config --global init.defaultBranch main
```

> LAB นี้ทำงานในเครื่องล้วน ๆ — ไม่ต้องใช้ GitHub และไม่ต้องใช้ token
>
> ⚠️ `git worktree` ต้องใช้ git 2.5 ขึ้นไป — เช็กด้วย `git --version` (container นี้คือ 2.54.0 สบายมาก)

---

## 5) STEP 1 — ตั้งร้าน: repo `coffee-app` + งานฐาน 2 commit

```bash
cd ~
mkdir coffee-app && cd coffee-app
git init
```

**Expected Output**

```
Initialized empty Git repository in /root/coffee-app/.git/
```

> 📌 คราวนี้ไม่มี hint เตือนเรื่อง `master` แล้ว — เพราะเราตั้ง `init.defaultBranch main` ไว้ branch แรกเกิดมาเป็น `main` เลย

สร้างเมนูและเวลาเปิดร้าน (สังเกตว่าเวลา **ผิด** อยู่ — ระเบิดเวลาของ story นี้ 🕖):

```bash
echo "Americano 45" > menu.txt
echo "Latte 55" >> menu.txt
git add menu.txt
git commit -m "Add menu"

echo "Open daily 07:00 - 17:00" > hours.txt
git add hours.txt
git commit -m "Add opening hours"
git log --oneline
```

**Expected Output**

```
[main (root-commit) 27b9a0b] Add menu
 1 file changed, 2 insertions(+)
 create mode 100644 menu.txt

[main 51c6bbb] Add opening hours
 1 file changed, 1 insertion(+)
 create mode 100644 hours.txt

51c6bbb (HEAD -> main) Add opening hours
27b9a0b Add menu
```

> 📌 **commit hash (`27b9a0b`, `51c6bbb`) ของแต่ละคนจะไม่เหมือนตัวอย่าง** — เป็นแบบนี้ทั้งเอกสาร

---

## 6) STEP 2 — งานเมนูใหม่: ทำค้างครึ่งทางไว้ (ตั้งใจ!)

สมชายเริ่มงานเมนูใหม่ตามวิชา LAB 00 — แตก branch ก่อนเสมอ:

```bash
git switch -c feature-newmenu
echo "Matcha Latte 65" >> menu.txt
git add menu.txt
git commit -m "Add Matcha Latte"
```

**Expected Output**

```
Switched to a new branch 'feature-newmenu'

[feature-newmenu 0bb5ca5] Add Matcha Latte
 1 file changed, 1 insertion(+)
```

ต่อด้วยเมนูโกโก้ … พิมพ์ราคาไปได้ตัวเดียว (ตั้งใจจะพิมพ์ `50` แต่ได้แค่ `5`) — **อย่าเพิ่ง commit อย่าเพิ่ง add** ปล่อยค้างไว้แบบนี้:

```bash
echo "Cocoa 5" >> menu.txt
cat menu.txt
git status
```

**Expected Output**

```
Americano 45
Latte 55
Matcha Latte 65
Cocoa 5

On branch feature-newmenu
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   menu.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

> 📌 นี่คือสภาพ "งานค้างครึ่งทาง" ของจริง: `menu.txt` แก้แล้วแต่ยังไม่เสร็จ ยังไม่ add ยังไม่ commit — โต๊ะทำงานรกอยู่พอดี… และเสียงโทรศัพท์ก็ดังขึ้น 📞

---

## 7) STEP 3 — ป้าโทรมา: ลอง switch หนีงาน → Git เบรกหัวทิ่ม

เวลาเปิดร้านผิด! ต้องรีบแก้บน `main` — ลองย้ายจักรวาลแบบที่เคยทำ:

```bash
git switch main
```

**Expected Output**

```
error: Your local changes to the following files would be overwritten by checkout:
	menu.txt
Please commit your changes or stash them before you switch branches.
Aborting
```

> 🧱 **Pain Point ข้อ 1 ตัวเป็น ๆ:** `menu.txt` ของ `feature-newmenu` (มี Matcha) กับของ `main` (ไม่มี) ไม่เหมือนกัน — ถ้า Git ยอมให้ switch งานแก้ค้างจะถูกเขียนทับหาย Git เลย `Aborting` ไว้ก่อน
>
> ทางเลือกที่เหลือดูแย่ทั้งคู่: ① commit งานครึ่งทางเป็น WIP commit — ประวัติเลอะ ② ทิ้งการแก้ — งานหาย … หรือ ③ **ไม่ต้องสลับเลย** — เปิดโต๊ะใหม่ข้าง ๆ ด้วย worktree ✨

---

## 8) STEP 4 — วิชาแยกเงา: `git worktree add`

*(อ้างอิงสไลด์ 04 · COMMANDS — รูปแบบคำสั่ง: `git worktree add <path> <branch>`)*

สร้าง worktree ใหม่ที่ `../hotfix` พร้อม**สร้าง branch ใหม่** `hotfix-hours` แตกจาก `main` — จบในคำสั่งเดียว **โดยไม่ต้องขยับออกจากที่ยืน**:

```bash
git worktree add ../hotfix -b hotfix-hours main
```

**Expected Output**

```
Preparing worktree (new branch 'hotfix-hours')
HEAD is now at 51c6bbb Add opening hours
```

> 📌 อ่านคำสั่งให้ครบ 3 ส่วน: `../hotfix` = **ที่อยู่โต๊ะใหม่** (โฟลเดอร์ข้าง ๆ ไม่ใช่ข้างใน repo!) · `-b hotfix-hours` = สร้าง branch ใหม่ · `main` = **ฐานที่แตกออกมา** — ตัวเงาเกิดมายืนบนปลาย `main` (`51c6bbb`) พอดี

ดูสารบัญโต๊ะทำงานทั้งหมด:

```bash
git worktree list
```

**Expected Output**

```
/root/coffee-app 0bb5ca5 [feature-newmenu]
/root/hotfix     51c6bbb [hotfix-hours]
```

> 📌 บรรทัดแรกคือ **main worktree** (โฟลเดอร์ที่ `git init`) — ยังยืนบน `feature-newmenu` งานค้างอยู่ครบ · บรรทัดสองคือ **linked worktree** เกิดใหม่บน `hotfix-hours` — สองโต๊ะ สอง branch **พร้อมกัน** โดยไม่มีใครต้อง switch

---

## 9) STEP 5 — ดับไฟในตัวเงา + พิสูจน์ SHARED / ISOLATED

### 9.1 เข้าไปสำรวจโต๊ะใหม่

```bash
cd ../hotfix
ls
git branch --show-current
cat menu.txt
```

**Expected Output**

```
hours.txt
menu.txt

hotfix-hours

Americano 45
Latte 55
```

> 📌 ไฟล์ครบเหมือน checkout `main` สด ๆ — และ `menu.txt` ที่นี่**ไม่มี** Matcha / Cocoa เพราะโต๊ะนี้แตกจาก `main` ไม่เกี่ยวกับงานค้างของอีกโต๊ะ (**ISOLATED**)

### 9.2 แอบดูไส้ใน: `.git` ของ linked worktree เป็นแค่ "ป้ายบอกทาง"

*(ทฤษฎี ③ ของจริง — เทียบกับ `cat .git/HEAD` ที่เคยแอบดูใน LAB 00)*

```bash
cat .git
```

**Expected Output**

```
gitdir: /root/coffee-app/.git/worktrees/hotfix
```

> 🤯 `.git` ที่นี่**ไม่ใช่โฟลเดอร์ แต่เป็นไฟล์ข้อความบรรทัดเดียว** — จดที่อยู่ชี้กลับไปหา `.git` ตัวจริงใน `coffee-app` นี่คือกลไกของ **SHARED**: ทุก worktree อ่าน-เขียน object database ก้อนเดียวกัน และคือเหตุผลของ **CHEAP**: สร้าง worktree ไม่ต้องก๊อปประวัติสักไบต์

เทียบกับ `.git` **ตัวจริง**ของ main worktree — อันนั้นเป็นโฟลเดอร์เต็ม ๆ:

```bash
ls ~/coffee-app/.git
```

**Expected Output**

```
COMMIT_EDITMSG
HEAD
config
description
hooks
index
info
logs
objects
refs
worktrees
```

> 📌 ครบเครื่องทั้ง `objects` (ประวัติ) `refs` (ป้าย branch) `config` — และสังเกตโฟลเดอร์ `worktrees` โผล่มาใหม่: นั่นคือที่ที่ Git เก็บ metadata ของเงาแต่ละตัว (เดี๋ยว STEP 9 จะวนกลับมาที่นี่ตอนคุยเรื่อง `prune`)

### 9.3 แก้เวลาเปิดร้าน + commit จากในเงา

```bash
echo "Open daily 08:00 - 18:00" > hours.txt
git commit -am "Fix opening hours"
git log --oneline
```

**Expected Output**

```
[hotfix-hours e6ddb4e] Fix opening hours
 1 file changed, 1 insertion(+), 1 deletion(-)

e6ddb4e (HEAD -> hotfix-hours) Fix opening hours
51c6bbb (main) Add opening hours
27b9a0b Add menu
```

### 9.4 พิสูจน์ SHARED: commit ในเงา เห็นได้จากทุกที่ทันที

ยังยืนอยู่ใน `hotfix` — ขอดู**ทุก branch** (วิชา LAB 00):

```bash
git log --oneline --all
```

**Expected Output**

```
0bb5ca5 (feature-newmenu) Add Matcha Latte
e6ddb4e (HEAD -> hotfix-hours) Fix opening hours
51c6bbb (main) Add opening hours
27b9a0b Add menu
```

> 📌 เห็น `feature-newmenu` ของอีกโต๊ะจากที่นี่เลย ไม่ต้อง push/pull — เพราะ refs อยู่ใน `.git` ก้อนเดียวกัน (**SHARED**)

### 9.5 พิสูจน์ ISOLATED: กลับโต๊ะเดิม — งานค้างอยู่ครบทุกตัวอักษร

```bash
cd ~/coffee-app
git branch --show-current
cat menu.txt
git status --short
```

**Expected Output**

```
feature-newmenu

Americano 45
Latte 55
Matcha Latte 65
Cocoa 5

 M menu.txt
```

> 🥷 **โมเมนต์ Shadow Clone สมบูรณ์:** ตัวเงาดับไฟ–commit เสร็จไปแล้วบน `hotfix-hours` ส่วนโต๊ะนี้ยังยืนบน `feature-newmenu` เดิม `Cocoa 5` ยังพิมพ์ค้างอยู่ที่เดิม `git status` ยังเห็นไฟล์แก้ค้างเหมือนไม่มีอะไรเกิดขึ้น — **Pain Point ข้อ 2–3 หายเกลี้ยง**: ไม่มี WIP commit ไม่มี context หาย

---

## 10) STEP 6 — ชนกำแพง: หนึ่ง branch ต่อหนึ่ง worktree

*(กติกาสำคัญจากทฤษฎี ③ — ลองแหกดูให้เห็นกับตา)*

ลองเปิดเงาอีกตัวบน branch ที่**ถูกใช้อยู่แล้ว**:

```bash
git worktree add ../oops feature-newmenu
```

**Expected Output**

```
Preparing worktree (checking out 'feature-newmenu')
fatal: 'feature-newmenu' is already used by worktree at '/root/coffee-app'
```

กลับกันก็โดน — ยืนที่โต๊ะนี้แล้วขอ switch ไป branch ที่เงาใช้อยู่:

```bash
git switch hotfix-hours
```

**Expected Output**

```
fatal: 'hotfix-hours' is already used by worktree at '/root/hotfix'
```

> 🧱 ทั้งสองทิศชนกำแพงเดียวกัน: **branch หนึ่งมีโต๊ะประจำได้ตัวเดียว** — ถ้าสองโต๊ะ checkout branch เดียวกันแล้วต่าง commit ป้าย branch จะวิ่งแยกสองทางพร้อมกัน ประวัติพังทันที Git เลยห้ามตั้งแต่ต้นทาง

---

## 11) STEP 7 — ปิดจ๊อบทั้งสองงาน: ทวนวิชา merge จาก LAB 01

ไฟดับแล้ว กลับมาทำเมนูต่อให้จบ — เปิด `nano menu.txt` แก้บรรทัดสุดท้าย `Cocoa 5` → `Cocoa 50` (บันทึก: `Ctrl+O` `Enter` ออก: `Ctrl+X`) หรือใช้ `sed` แทนก็ได้:

```bash
sed -i 's/Cocoa 5$/Cocoa 50/' menu.txt
cat menu.txt
git commit -am "Add Cocoa"
```

**Expected Output**

```
Americano 45
Latte 55
Matcha Latte 65
Cocoa 50

[feature-newmenu 4e47c28] Add Cocoa
 1 file changed, 1 insertion(+)
```

งานเสร็จทั้งคู่แล้ว — พางานกลับบ้านทั้งสองทาง ตอนนี้ไม่มีไฟล์ค้าง `git switch main` ผ่านฉลุย:

```bash
git switch main
git merge hotfix-hours
```

**Expected Output**

```
Switched to branch 'main'

Updating 51c6bbb..e6ddb4e
Fast-forward
 hours.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

> 📌 **Fast-forward** (LAB 01): `main` ไม่ขยับเลยตั้งแต่แตก `hotfix-hours` — เลื่อนป้ายตามเฉย ๆ ไม่มี commit ใหม่

```bash
git merge feature-newmenu
```

**Expected Output**

```
Merge made by the 'ort' strategy.
 menu.txt | 2 ++
 1 file changed, 2 insertions(+)
```

> 📌 คราวนี้สองเส้นแยกกันจริง (main มี hotfix แล้ว) → **3-way merge**: nano จะเด้งขึ้นมาพร้อมข้อความ default `Merge branch 'feature-newmenu'` — บันทึกออกตามเดิม (`Ctrl+O` `Enter` `Ctrl+X`) แล้วจะเห็นบรรทัด `ort` ตามตัวอย่าง · ไม่มี conflict เพราะสองงานแตะคนละไฟล์

ดูแผนที่รวมพล:

```bash
git log --oneline --all --graph
```

**Expected Output**

```
*   e4a2b04 (HEAD -> main) Merge branch 'feature-newmenu'
|\  
| * 4e47c28 (feature-newmenu) Add Cocoa
| * 0bb5ca5 Add Matcha Latte
* | e6ddb4e (hotfix-hours) Fix opening hours
|/  
* 51c6bbb Add opening hours
* 27b9a0b Add menu
```

> 📌 รูปเพชรเหมือน LAB 01 เป๊ะ — ต่างแค่ครั้งนี้**สองเส้นถูกสร้างจากคนละโต๊ะพร้อมกัน** งานด่วนไม่เคยต้องรอเมนู เมนูไม่เคยต้องหลบงานด่วน

---

## 12) STEP 8 — โบนัส: `--detach` ไทม์แมชชีนดูอดีต

*(อ้างอิงสไลด์ 04 — `git worktree add --detach`)*

ป้าถามว่า *"เมนูรุ่นแรกสุดของร้านมีอะไรบ้างนะ?"* — ไม่ต้อง switch ไม่ต้องกลัวกระทบงาน เปิดเงาชั่วคราวส่องอดีต (`HEAD~3` = ถอยจาก merge commit ไป 3 ก้าวตามเส้นหลัก = commit แรกสุด):

```bash
git worktree add --detach ../time-machine HEAD~3
cat ../time-machine/menu.txt
ls ../time-machine
```

**Expected Output**

```
Preparing worktree (detached HEAD 27b9a0b)
HEAD is now at 27b9a0b Add menu

Americano 45
Latte 55

menu.txt
```

> 📌 `--detach` = ไม่เกาะ branch ไหนเลย (detached HEAD — ยืนบน commit ตรง ๆ) เหมาะกับส่องของเก่า/ทดสอบชั่วคราว · สังเกตว่าในนั้นยังไม่มี `hours.txt` ด้วยซ้ำ — โลกของ commit แรกจริง ๆ

```bash
git worktree list
```

**Expected Output**

```
/root/coffee-app   e4a2b04 [main]
/root/hotfix       e6ddb4e [hotfix-hours]
/root/time-machine 27b9a0b (detached HEAD)
```

> 📌 3 โต๊ะ 3 สถานะ: branch หลัก · branch hotfix · detached HEAD — คอลัมน์ท้ายบอกชัดว่าใครยืนบนอะไร

---

## 13) STEP 9 — เก็บกวาดให้เป็น: remove / prune + กำแพงกันพลาด

*(อ้างอิงสไลด์ 05 · COMMANDS และสไลด์ 09 · CAVEATS)*

### 13.1 ปริศนาจาก LAB 00 เฉลยที่นี่

งานจบแล้ว ลบ branch `hotfix-hours` ทิ้ง (merge แล้ว `-d` ตัวเล็กต้องผ่าน…?):

```bash
git branch -d hotfix-hours
```

**Expected Output**

```
error: cannot delete branch 'hotfix-hours' used by worktree at '/root/hotfix'
```

> 💡 **จำ error ประหลาดตอนลบ branch ที่ตัวเองยืนอยู่ใน LAB 00 ได้ไหม? — ข้อความเดียวกันเป๊ะ!** เพราะโฟลเดอร์ที่เรายืน `git init` ก็คือ worktree ตัวหนึ่ง (main worktree) ในสายตา Git มาตลอด การยืนบน branch = branch นั้น "ถูกใช้โดย worktree" — วันนี้วงจรความรู้ครบแล้ว: **ลบ branch ที่มีโต๊ะใช้งานอยู่ไม่ได้ ต้องเก็บโต๊ะก่อน**

### 13.2 เก็บโต๊ะด้วย `git worktree remove` — เจอกำแพงของแท้

สมมุติสมชายเคยจดโน้ตค้างไว้ในเงา (ไฟล์ untracked):

```bash
echo "remember to tell auntie" > ../hotfix/note.txt
git worktree remove ../hotfix
```

**Expected Output**

```
fatal: '../hotfix' contains modified or untracked files, use --force to delete it
```

> 🧱 Git เช็กก่อนลบเสมอ — มีไฟล์แก้ค้าง/untracked จะไม่ยอมลบเงียบ ๆ กันงานหายโดยไม่รู้ตัว · โน้ตไม่เอาแล้วจริง ๆ ก็ยืนยันด้วย `--force`:

```bash
git worktree remove --force ../hotfix
git worktree list
git branch -d hotfix-hours
git branch -d feature-newmenu
git branch
```

**Expected Output**

```
/root/coffee-app   e4a2b04 [main]
/root/time-machine 27b9a0b (detached HEAD)

Deleted branch hotfix-hours (was e6ddb4e).
Deleted branch feature-newmenu (was 4e47c28).

* main
```

> 📌 พอโต๊ะถูกเก็บ `branch -d` ก็ผ่านแบบ LAB 01 (merge แล้วลบได้เงียบกริบ) — **ลบ worktree ≠ ลบ branch**: ตอน remove โต๊ะ commit ทั้งหมดยังอยู่ครบ เพิ่งหายตอนเราสั่งลบป้ายเอง

### 13.3 บาปของการ `rm -rf` + ไม้กวาด `prune`

เพื่อนร่วมทีมไม่รู้เรื่อง ลบโฟลเดอร์ time-machine ตรง ๆ แบบโฟลเดอร์ธรรมดา:

```bash
rm -rf ../time-machine
git worktree list
```

**Expected Output**

```
/root/coffee-app   e4a2b04 [main]
/root/time-machine 27b9a0b (detached HEAD) prunable
```

> ⚠️ โฟลเดอร์หายไปแล้ว แต่ Git **ยังจำ** อยู่ — metadata ค้างใน `.git/worktrees/` สถานะ `prunable` = "ศพที่รอเก็บ" · นี่คือเหตุผลที่สไลด์ 09 เตือน**อย่าลบ directory ตรง ๆ** — ใช้ `git worktree remove` เสมอ ถ้าพลาดไปแล้วก็เก็บกวาดด้วย:

```bash
git worktree prune
git worktree list
```

**Expected Output**

```
/root/coffee-app e4a2b04 [main]
```

> ✅ สะอาดเอี่ยม — เหลือ main worktree ตัวเดียว (ซึ่งไม่มีวันถูก remove/prune — มันคือตัวจริง ไม่ใช่เงา)

---

## 14) Use case ระดับโปร: รัน AI coding agent หลายตัวพร้อมกัน 🤖

*(อ้างอิงสไลด์ 07 · USE CASE — อ่านเฉย ๆ ไม่ต้องรัน)*

ทีมยุคใหม่ใช้ AI agent ช่วยเขียนโค้ด — ปัญหาคือถ้า agent หลายตัวเขียนไฟล์ในโฟลเดอร์เดียวกันมันจะทับกันเอง ทางแก้คือแพตเทิร์นเดียวกับ LAB นี้เป๊ะ: **หนึ่ง agent → หนึ่ง worktree → หนึ่ง branch**

```
~/agent-auth              ~/agent-search             ~/agent-tests
[agent/auth]              [agent/search]             [agent/tests]
$ claude "แก้ระบบ OAuth"   $ claude "เพิ่ม fuzzy search"  $ claude "เขียน test ให้ครบ"
```

```bash
git worktree add ../agent-auth -b agent/auth main
# ทำซ้ำต่อ agent หนึ่งตัว — แต่ละตัวทำงานขนานกันโดยไม่แย่งเขียนไฟล์
# เสร็จแล้ว review และ merge ทีละ branch (วิชา LAB 01) แล้วเก็บกวาด (STEP 9)
```

สังเกตว่าทั้งหมดคือคำสั่งที่เพิ่งใช้มาแล้วใน LAB นี้ทุกตัว — สเกลจาก "สมชาย + เงา 1 ตัว" เป็น "agent N ตัว" ได้ตรง ๆ

---

## 15) ข้อควรระวังและข้อจำกัด ⚠️

*(อ้างอิงสไลด์ 09 · CAVEATS — สองข้อแรกเจอตัวเป็น ๆ ไปแล้ว)*

| ข้อควรระวัง | รายละเอียด | เจอใน |
|---|---|---|
| **หนึ่ง branch ต่อหนึ่ง worktree** | checkout branch ที่ถูกใช้อยู่ในโต๊ะอื่น → `fatal: ... already used by worktree` | STEP 6 |
| **อย่าลบ directory ตรง ๆ** | `rm -rf` ทิ้ง metadata ค้าง — ใช้ `git worktree remove` หรือตามเก็บด้วย `prune` เสมอ | STEP 9 |
| **untracked files ไม่ตามไปด้วย** | worktree ใหม่ได้เฉพาะไฟล์ที่ Git track — `node_modules`, `.env`, config ต้อง setup ใหม่ในแต่ละโต๊ะ เผื่อเวลา install ด้วย | (สังเกต STEP 5.1: ไม่มีไฟล์ untracked ตามมา) |
| **submodules รองรับได้จำกัด** | repo ที่พึ่งพา submodule หนัก ๆ ควรทดสอบ workflow ก่อนใช้จริง | — |

---

## 16) สรุป + Cheat Sheet 📋

*(อ้างอิงสไลด์ 10 · SUMMARY)*

**ครั้งหน้าที่มีงานด่วนแทรก — สร้าง worktree แทนการสลับ branch แล้วงานเดิมจะอยู่ตรงที่เราทิ้งไว้เสมอ**

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git worktree add <path> <branch>` | เปิดโต๊ะใหม่ checkout branch ที่มีอยู่แล้ว |
| `git worktree add <path> -b <new> <base>` | เปิดโต๊ะใหม่ + สร้าง branch ใหม่จากฐานที่กำหนด (ท่าหลักของ LAB นี้) |
| `git worktree add --detach <path> <commit>` | เปิดโต๊ะชั่วคราวแบบ detached HEAD — ส่องอดีต/ทดลอง |
| `git worktree list` | ดูโต๊ะทั้งหมด: path · commit · branch (+ `prunable` ถ้ามีศพรอเก็บ) |
| `git worktree remove <path>` | เก็บโต๊ะอย่างถูกวิธี (มีไฟล์ค้างต้อง `--force`) |
| `git worktree prune` | เก็บกวาด metadata ของโต๊ะที่โฟลเดอร์ถูกลบไปแล้ว |

**ภาพจำ:** repo = คลังกลาง (`.git` เดียว) · worktree = โต๊ะทำงานหลายตัวหน้าคลัง · หนึ่งโต๊ะหนึ่ง branch · เลิกใช้เก็บโต๊ะด้วย `remove` ไม่ใช่ `rm`

---

## 17) Checklist ✅

- [ ] อธิบายได้ว่าทำไม `git switch` ตอนมีงานค้างถึงโดน `would be overwritten` (STEP 3)
- [ ] สร้าง worktree ใหม่พร้อม branch ใหม่ได้ในคำสั่งเดียว และชี้ได้ว่า path / branch ใหม่ / ฐาน คือส่วนไหนของคำสั่ง (STEP 4)
- [ ] `cat .git` ใน linked worktree แล้วอธิบายได้ว่ามันพิสูจน์ SHARED + CHEAP ยังไง (STEP 5.2)
- [ ] commit จากในเงาแล้วเห็นจาก `git log --oneline --all` ของโต๊ะไหนก็ได้ (STEP 5.4)
- [ ] กลับโต๊ะเดิมแล้ว `Cocoa 5` ยังค้างอยู่ — ชี้ได้ว่านี่คือ ISOLATED (STEP 5.5)
- [ ] ชนกำแพง "หนึ่ง branch ต่อหนึ่ง worktree" ครบทั้งสองทิศ (STEP 6)
- [ ] merge กลับ `main` ครบสองงาน: Fast-forward หนึ่ง + `ort` หนึ่ง แล้วเห็นรูปเพชรใน `--graph` (STEP 7)
- [ ] ใช้ `--detach` เปิดไทม์แมชชีน และอ่าน `(detached HEAD)` ใน `worktree list` ออก (STEP 8)
- [ ] เฉลยปริศนา LAB 00 ได้: ทำไม error ลบ branch ถึงพูดถึง "worktree" (STEP 9.1)
- [ ] เจอครบ: remove โดนกำแพง untracked → `--force` → `rm -rf` เกิด `prunable` → `prune` เก็บกวาด (STEP 9)
- [ ] จบ LAB: `git worktree list` เหลือบรรทัดเดียว และ `git branch` เหลือ `* main`

---

## 18) คำถามทบทวน ❓

1. ทำไม `git switch main` ใน STEP 3 ถึงโดนปฏิเสธ — Git กลัวอะไรหาย? แล้วทำไม `git switch main` ใน STEP 7 ถึงผ่าน?
2. worktree แก้ Pain Point "WIP commit" ได้อย่างไร — ต่างจากการ commit งานครึ่งทางแล้วค่อยแกะกลับตรงไหน?
3. SHARED / ISOLATED / CHEAP — แต่ละคำหมายถึงอะไร และใน LAB นี้พิสูจน์แต่ละข้อด้วยการทดลองไหน?
4. `cat .git` ใน linked worktree ได้ไฟล์ข้อความบรรทัดเดียว — มันชี้ไปไหน และต่างจาก `.git` ของ main worktree อย่างไร?
5. ในคำสั่ง `git worktree add ../hotfix -b hotfix-hours main` — สามส่วน `../hotfix` / `hotfix-hours` / `main` แต่ละส่วนคืออะไร?
6. ทำไม Git ถึงห้ามสอง worktree checkout branch เดียวกัน — ถ้ายอมให้ทำ จะเกิดอะไรขึ้นกับป้าย branch?
7. commit ที่ทำจากใน `../hotfix` ไปเก็บอยู่ที่ไหน — ทำไมโต๊ะอื่นเห็นทันทีโดยไม่ต้อง push?
8. `git worktree add --detach` ต่างจากแบบปกติอย่างไร และสถานการณ์ไหนควรใช้?
9. error `cannot delete branch ... used by worktree` เคยเจอใน LAB 00 ตอนไหน — ความรู้ LAB นี้อธิบายมันว่าอย่างไร?
10. ลบ worktree ด้วย `git worktree remove` กับ `rm -rf` ต่างกันอย่างไร — ถ้าเผลอ `rm -rf` ไปแล้วต้องตามด้วยคำสั่งอะไร?
11. `git worktree remove ../hotfix` ครั้งแรกโดนปฏิเสธเพราะอะไร — กำแพงนี้ป้องกันความผิดพลาดแบบไหน?
12. "ลบ worktree ≠ ลบ branch" — หลัง `remove --force ../hotfix` แล้ว commit `Fix opening hours` ยังอยู่ไหม? รู้ได้อย่างไร?

---

*LAB 02 — Shadow Clone · DevTools Week 3 · expected output ทุกจุดรันจริงบน `tuchsanai/devtools:2569_1` (git 2.54.0) — commit hash ของแต่ละคนจะต่างจากตัวอย่าง · ตัวอย่างใช้ตัวตนสมมุติ `somchai-dev` — ใช้ชื่อและอีเมลของตัวเองเสมอ*
