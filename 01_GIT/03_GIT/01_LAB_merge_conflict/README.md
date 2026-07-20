# LAB 01 — Merge Day ⚔️
### รวมจักรวาลกลับเป็นหนึ่ง: Fast-forward · 3-way Merge · และสงคราม Conflict

> **Week 3 · Branches and Working with Others · LAB 01**
> เนื้อหาอ้างอิงสไลด์ `03_GIT.pdf` หน้า 61–82 · ทุก expected output รันจริงบน container `tuchsanai/devtools:2569_1` (git 2.43.0)

---

## 1) Story / Pain Point 📖

จบ [LAB 00](../00_LAB_branch_switch/README.md) สมชายแตก branch คล่องแล้ว — งานทดลองไม่ทำของจริงพังอีกต่อไป แต่พอใช้ไปหนึ่งสัปดาห์ ปัญหาชุดใหม่ก็โผล่มา:

| # | ปัญหา | อาการ |
|---|--------|-------|
| 1 | **งานเสร็จแล้ว…แต่ติดอยู่ใน branch** | เมนูชาทำเสร็จใน `feature-tea` แต่ป้าเปิดดู `main` — ไม่เห็นชาสักแก้ว |
| 2 | **สองงานเสร็จพร้อมกัน** | เมนูเค้กก็เสร็จ เบอร์ติดต่อร้านก็เสร็จ — อยู่คนละ branch จะรวมยังไงไม่ให้ของหาย |
| 3 | **สองจักรวาลแก้ "บรรทัดเดียวกัน"** | สมชายเปลี่ยนเมนูพิเศษเป็นโกโก้ ป้าสั่งเปลี่ยนเป็นชาเขียว — บรรทัดเดียวกัน คนละค่า ใครชนะ? |
| 4 | **มองไม่เห็นความต่างระหว่าง branch** | ก่อนรวมอยากรู้ว่าอีก branch แก้อะไรไปบ้าง — ไล่เปิดไฟล์เทียบเองตาไม่ไหว |

**ทางแก้ = `git merge` + `git diff`.** การแตก branch เป็นแค่ครึ่งแรกของวิชา — ครึ่งหลังคือพางานกลับบ้าน: Git รวมงานให้อัตโนมัติได้เกือบทุกกรณี (สไลด์หน้า 62–82) และกรณีเดียวที่มันยอมแพ้ — **conflict** — ก็มีขั้นตอนแก้ที่เป็นระบบ ไม่ใช่เรื่องดวง

---

## 2) สิ่งที่จะได้เรียนรู้ 🎯

- **Fast-forward merge** — การรวมแบบ "เลื่อนป้ายตาม" ไม่มี commit ใหม่ (สไลด์หน้า 62–69)
- **3-way merge** — สองเส้นแยกกันจริง Git สร้าง **merge commit** ให้อัตโนมัติ พร้อมข้อความ default `Merge branch '...'` (สไลด์หน้า 70–75)
- เคสที่ Git รวมให้เองได้: ต่างคนต่างแตะคนละไฟล์/คนละส่วน — ไม่มีข้อมูลฝั่งไหนหาย (สไลด์หน้า 76–82)
- **Merge conflict**: อ่าน marker `<<<<<<<` `=======` `>>>>>>>` → แก้ → `add` → `commit` จบสงครามอย่างมีขั้นตอน
- `git diff` — ส่องความต่าง: ก่อน commit, ระหว่าง branch, และตอน conflict
- `git log --oneline --all --graph` — อ่านแผนที่ประวัติแบบเห็นเส้นแยก-เส้นรวม
- โบนัสเชื่อม LAB 00: branch ที่ merge แล้วลบด้วย `-d` ได้เงียบกริบ

---

## 3) ทฤษฎี ① — Fast-forward: การรวมที่ง่ายที่สุดในโลก

*(อ้างอิงสไลด์ 03_GIT.pdf หน้า 62–69)*

ถ้าเราแตก branch ออกไปทำงาน แล้ว **เส้นเดิม (`main`) ไม่มี commit ใหม่เลย** — ปลายทั้งสองยังอยู่บนโซ่เส้นเดียวกัน:

```
main
 ↓
 C1 ← C2 ← C3
            ↑
       new_branch
```

การ "รวม" จึงไม่ต้องรวมอะไรจริง ๆ — Git แค่**เลื่อนป้าย `main` ไปข้างหน้า**จนทันปลาย branch (`git switch main` แล้ว `git merge new_branch` — สไลด์หน้า 68–69) ไม่มี commit ใหม่เกิดขึ้น ประวัติยังเป็นเส้นตรงสวยงาม เรียกว่า **"fast-forward" merge**

## ทฤษฎี ② — 3-way merge: เมื่อสองเส้นแยกกันจริง

*(อ้างอิงสไลด์ 03_GIT.pdf หน้า 70–82)*

ถ้าระหว่างที่แยกไป **`main` เองก็มี commit ใหม่** (เช่น Commit Alpha — สไลด์หน้า 72) สองเส้นก็แยกกันจริง ๆ แล้ว เลื่อนป้ายเฉย ๆ ไม่ได้อีกต่อไป:

- Git สร้าง **commit ใหม่ให้อัตโนมัติ** (AUTO Commit — สไลด์หน้า 74) ที่มี parent สองตัว คือปลายของทั้งสองเส้น
- Git จะขอให้เราตั้งชื่อ commit นี้ โดยมีชื่อ default ว่า **`Merge branch 'branch_name'`** (สไลด์หน้า 75) — ตอนทำจริง nano จะเด้งขึ้นมาพร้อมข้อความนี้ให้กดบันทึกได้เลย
- Git รวมให้เองสำเร็จเสมอเมื่อ**ไม่มีข้อมูลของฝั่งไหนต้องถูกทิ้ง** เช่น ต่างคนต่างเพิ่มคนละไฟล์ / แก้คนละส่วนของไฟล์ (สไลด์หน้า 76–82)

## ทฤษฎี ③ — Conflict: จุดที่ Git ยกมือขอมนุษย์ตัดสิน

Git ฉลาดเรื่องรวมงาน แต่**ไม่ตัดสินใจแทนเรา**: ถ้าสอง branch แก้ **บรรทัดเดียวกันของไฟล์เดียวกัน** เป็นคนละค่า Git ไม่มีทางรู้ว่าค่าไหนถูก — มันจะหยุดกลางคัน ประกาศ `CONFLICT` แล้วเขียน **เครื่องหมายเขตสงคราม** ลงในไฟล์ให้เราเลือกเอง:

```
<<<<<<< HEAD
ของฝั่งเรา (branch ที่ยืนอยู่)
=======
ของฝั่งเขา (branch ที่ถูก merge เข้ามา)
>>>>>>> branch_name
```

ขั้นตอนดับไฟมี 3 จังหวะตายตัว: **แก้ไฟล์ให้เหลือเวอร์ชันสุดท้าย → `git add` → `git commit`** — และถ้าอยากถอยทั้งกระดาน `git status` ก็ใบ้ทางหนีไฟไว้ให้ (`git merge --abort`)

---

## 4) เตรียมความพร้อม ⚙️

ใช้ container เดิมจาก LAB 00 ได้เลย (ถ้าเปิด container ใหม่ ให้ตั้งตัวตนก่อน — ตัวอย่างใช้ตัวตนสมมุติ `somchai-dev` ให้แทนด้วยชื่อ-อีเมลของตัวเอง):

```bash
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd

git config --global user.name "somchai-dev"              # ← ใช้ชื่อของตัวเอง
git config --global user.email "somchai.dev@example.com" # ← ใช้อีเมลของตัวเอง
```

สร้างสนามทดลองใหม่ (แยกจาก repo ของ LAB 00) — เมนูหลัก + ป้ายเมนูพิเศษรายวัน:

```bash
cd ~
mkdir cafe-menu && cd cafe-menu
git init
echo "== Cafe Menu ==" > menu.txt
echo "Americano 45" >> menu.txt
echo "Latte 55" >> menu.txt
echo "Special: Croissant" > special.txt
git add .
git commit -m "Initial menu"
git branch -m master main
git branch
git log --oneline
```

**Expected Output** *(ตัด hint ของ `git init` ที่เห็นกันมาแล้วใน LAB 00 ออก)*

```
Initialized empty Git repository in /root/cafe-menu/.git/

[master (root-commit) ef92a02] Initial menu
 2 files changed, 4 insertions(+)
 create mode 100644 menu.txt
 create mode 100644 special.txt

* main

ef92a02 (HEAD -> main) Initial menu
```

> 📌 commit hash ของแต่ละคนจะไม่เหมือนตัวอย่าง — ทั้งเอกสารนี้

---

## 5) STEP 1 — เมนูชา: ทำงานบน branch แล้วรวมแบบ Fast-forward

ป้าอยากขายชา — แตกจักรวาลไปทำตามวิชา LAB 00 (คราวนี้ใช้ทางลัด `switch -c`):

```bash
git switch -c feature-tea
echo "Green Tea 50" >> menu.txt
git diff
```

**Expected Output**

```
Switched to a new branch 'feature-tea'

diff --git a/menu.txt b/menu.txt
index fc61276..e15df45 100644
--- a/menu.txt
+++ b/menu.txt
@@ -1,3 +1,4 @@
 == Cafe Menu ==
 Americano 45
 Latte 55
+Green Tea 50
```

> 🔍 **พบกับ `git diff`** — ยังไม่ add ไม่ commit ก็ส่องได้ว่าเราแก้อะไรไปแล้วบ้าง: บรรทัดขึ้นต้น `+` คือของที่เพิ่มเข้ามา (ถ้าลบจะเป็น `-`) — นิสัยดีก่อน commit ทุกครั้ง: diff ดูก่อนว่ากำลังจะบันทึกอะไร

commit สองระลอกให้เมนูชาครบชุด:

```bash
git add menu.txt
git commit -m "Add green tea"
echo "Thai Tea 45" >> menu.txt
git add menu.txt
git commit -m "Add thai tea"
git log --oneline
```

**Expected Output**

```
[feature-tea 4ece70b] Add green tea
 1 file changed, 1 insertion(+)

[feature-tea 977c83e] Add thai tea
 1 file changed, 1 insertion(+)

977c83e (HEAD -> feature-tea) Add thai tea
4ece70b Add green tea
ef92a02 (main) Initial menu
```

งานเสร็จ! กลับ `main` — และเจอ Pain Point ข้อ 1 เต็ม ๆ:

```bash
git switch main
cat menu.txt
git log --oneline --all --graph
```

**Expected Output**

```
Switched to branch 'main'

== Cafe Menu ==
Americano 45
Latte 55

* 977c83e (feature-tea) Add thai tea
* 4ece70b Add green tea
* ef92a02 (HEAD -> main) Initial menu
```

> 📌 บน `main` ไม่มีชาสักแก้ว — และดูแผนที่: **เส้นตรงเส้นเดียว** โดย `main` อยู่ข้างหลัง `feature-tea` เฉย ๆ ไม่มี commit สวนทาง → เข้าเงื่อนไข Fast-forward พอดี (สไลด์หน้า 63–67)

รวมงานกลับ — ยืนที่ branch ปลายทาง (`main`) แล้วดึงเข้ามา:

```bash
git merge feature-tea
cat menu.txt
git log --oneline --graph
```

**Expected Output**

```
Updating ef92a02..977c83e
Fast-forward
 menu.txt | 2 ++
 1 file changed, 2 insertions(+)

== Cafe Menu ==
Americano 45
Latte 55
Green Tea 50
Thai Tea 45

* 977c83e (HEAD -> main, feature-tea) Add thai tea
* 4ece70b Add green tea
* ef92a02 Initial menu
```

> 📌 Git ประกาศเองว่า **`Fast-forward`** — แค่เลื่อนป้าย `main` จาก `ef92a02` ไป `977c83e` · ไม่มี commit ใหม่ ประวัติยังเป็นเส้นตรง และตอนนี้ `main` กับ `feature-tea` ชี้จุดเดียวกัน

ป้ายที่งานถูกรวมแล้ว ลบได้เงียบกริบด้วย `-d` ตัวเล็ก (เทียบกับ LAB 00 ที่โดนกำแพง!):

```bash
git branch -d feature-tea
git branch
```

**Expected Output**

```
Deleted branch feature-tea (was 977c83e).

* main
```

> 💡 คราวนี้ไม่มี error เพราะงาน merge เข้า `main` ครบแล้ว — ลบป้ายชื่อทิ้ง **commit ไม่หายไปไหน** (ยังอยู่ในเส้น `main`) · วงจรชีวิต branch จบสวย: แตก → ทำ → รวม → ลบป้าย

---

## 6) STEP 2 — เค้ก vs เบอร์ติดต่อ: 3-way merge (มี AUTO Commit)

คราวนี้เจอสถานการณ์สไลด์หน้า 70–75 เต็มรูปแบบ: แตกไปทำเมนูเค้ก แต่**ระหว่างนั้น `main` ก็มีงานใหม่** (ป้าขอเบอร์ติดต่อด่วน):

```bash
git switch -c feature-cake
echo "Cheesecake 89" > cake.txt
git add cake.txt
git commit -m "Add cake menu"

git switch main
echo "Contact: 02-123-4567" > contact.txt
git add contact.txt
git commit -m "Add contact info"

git log --oneline --all --graph
```

**Expected Output**

```
Switched to a new branch 'feature-cake'
[feature-cake 46913ff] Add cake menu
 1 file changed, 1 insertion(+)
 create mode 100644 cake.txt

Switched to branch 'main'
[main 8c6e723] Add contact info
 1 file changed, 1 insertion(+)
 create mode 100644 contact.txt

* 46913ff (feature-cake) Add cake menu
| * 8c6e723 (HEAD -> main) Add contact info
|/
* 977c83e Add thai tea
* 4ece70b Add green tea
* ef92a02 Initial menu
```

> 📌 แผนที่**แตกเป็นสองง่าม**แล้ว — `main` มี commit สวนทาง (`Add contact info` = "Commit Alpha" ของสไลด์หน้า 72) เลื่อนป้ายเฉย ๆ ไม่ได้อีกแล้ว

merge เลย — คราวนี้ Git ต้องสร้าง commit ใหม่ และจะเปิด **nano** ให้ตั้งชื่อ:

```bash
git merge feature-cake
```

> ⌨️ **nano จะเด้งขึ้นมา** พร้อมข้อความ default `Merge branch 'feature-cake'` (ตรงสไลด์หน้า 75) — ไม่ต้องแก้อะไร กด **Ctrl+O → Enter** (บันทึก) แล้ว **Ctrl+X** (ออก)

**Expected Output** *(หลังออกจาก nano)*

```
Merge made by the 'ort' strategy.
 cake.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 cake.txt
```

> 📌 ไม่ใช่ `Fast-forward` แล้ว — `Merge made by the 'ort' strategy.` = Git สร้าง **merge commit** (AUTO Commit, สไลด์หน้า 74) และรวมสำเร็จอัตโนมัติเพราะสองฝั่ง**แตะคนละไฟล์** ไม่มีข้อมูลใครหาย (สไลด์หน้า 76–82)

ดูแผนที่ — จุดเด่นคือรูป **เพชร (diamond)**:

```bash
git log --oneline --graph
ls
git branch -d feature-cake
```

**Expected Output**

```
*   89f3df3 (HEAD -> main) Merge branch 'feature-cake'
|\
| * 46913ff (feature-cake) Add cake menu
* | 8c6e723 Add contact info
|/
* 977c83e Add thai tea
* 4ece70b Add green tea
* ef92a02 Initial menu

cake.txt
contact.txt
menu.txt
special.txt

Deleted branch feature-cake (was 46913ff).
```

> 📌 commit `89f3df3` มี**สองขา** (parent สองตัว) — ขาซ้ายลงไป `Add contact info` ขาขวาลงไป `Add cake menu` · ไฟล์ครบทั้งเค้กและเบอร์ติดต่อ — **Pain Point ข้อ 2 หายแล้ว**

---

## 7) STEP 3 — สงครามหนึ่งบรรทัด: Merge Conflict ⚔️

วันเสาร์ สมชายแตก branch ไปเปลี่ยนเมนูพิเศษเป็น **Matcha Latte** … แต่ระหว่างนั้นป้าโทรมาสั่งเปลี่ยนหน้าร้านเป็น **Iced Cocoa** — สมชายเลยแก้บน `main` ด้วย ทั้งสองฝั่งเขียนทับ **บรรทัดเดียวกัน** ของ `special.txt`:

```bash
git switch -c feature-weekend
echo "Special: Matcha Latte" > special.txt
git add special.txt
git commit -m "Weekend special: Matcha Latte"

git switch main
echo "Special: Iced Cocoa" > special.txt
git add special.txt
git commit -m "Change special to Iced Cocoa"
```

**Expected Output**

```
Switched to a new branch 'feature-weekend'
[feature-weekend 77fa925] Weekend special: Matcha Latte
 1 file changed, 1 insertion(+), 1 deletion(-)

Switched to branch 'main'
[main acf24cc] Change special to Iced Cocoa
 1 file changed, 1 insertion(+), 1 deletion(-)
```

ก่อน merge ใช้ `git diff` เทียบสอง branch — **พยากรณ์การชนล่วงหน้าได้เลย**:

```bash
git diff main feature-weekend
git log --oneline --all --graph
```

**Expected Output**

```
diff --git a/special.txt b/special.txt
index 687f2fc..15515f7 100644
--- a/special.txt
+++ b/special.txt
@@ -1 +1 @@
-Special: Iced Cocoa
+Special: Matcha Latte

* 77fa925 (feature-weekend) Weekend special: Matcha Latte
| * acf24cc (HEAD -> main) Change special to Iced Cocoa
|/
*   89f3df3 Merge branch 'feature-cake'
|\
| * 46913ff Add cake menu
* | 8c6e723 Add contact info
|/
* 977c83e Add thai tea
* 4ece70b Add green tea
* ef92a02 Initial menu
```

> 🔍 diff บอกชัด: บรรทัดเดียวกัน ฝั่ง `main` เป็น Iced Cocoa (`-`) ฝั่ง `feature-weekend` เป็น Matcha Latte (`+`) — สองง่ามในแผนที่ก็ยืนยัน ชนแน่นอน

เดินหน้าชน:

```bash
git merge feature-weekend
```

**Expected Output**

```
Auto-merging special.txt
CONFLICT (content): Merge conflict in special.txt
Automatic merge failed; fix conflicts and then commit the result.
```

> ⚔️ Git ยกมือยอมแพ้ตามทฤษฎี ③ — **การ merge ค้างอยู่กลางคัน** รอเราตัดสิน อย่าตกใจ ทำตามขั้นตอนดับไฟ 3 จังหวะ

**จังหวะที่ 1 — สำรวจสนามรบ:**

```bash
git status
cat special.txt
```

**Expected Output**

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   special.txt

no changes added to commit (use "git add" and/or "git commit -a")

<<<<<<< HEAD
Special: Iced Cocoa
=======
Special: Matcha Latte
>>>>>>> feature-weekend
```

> 📌 `git status` ระบุคู่กรณี (`both modified: special.txt`) และแถมทางหนีไฟ: ถ้าอยากยกเลิกทั้งหมดกลับไปก่อน merge ใช้ `git merge --abort` ได้ · ในไฟล์ Git เขียนเขตสงครามให้แล้ว: บน `=======` คือฝั่งเรา (`HEAD` = `main`) ล่างคือฝั่ง `feature-weekend`
>
อยากดูเขตสงครามในรูปแบบ diff ก็ได้ (ไม่บังคับ):

```bash
git diff
```

**Expected Output** *(ถ้าลองรัน)*

```
diff --cc special.txt
index 687f2fc,15515f7..0000000
--- a/special.txt
+++ b/special.txt
@@@ -1,1 -1,1 +1,5 @@@
++<<<<<<< HEAD
 +Special: Iced Cocoa
++=======
+ Special: Matcha Latte
++>>>>>>> feature-weekend
```

> 🔍 หน้าตา diff ตอน conflict จะพิเศษ: `diff --cc` = **combined diff** เทียบกับสองฝั่งพร้อมกัน จึงมี 2 คอลัมน์เครื่องหมาย — `+ `/` +` บอกว่าบรรทัดนั้นมาจากฝั่งไหน ส่วน `++` คือบรรทัดที่ไม่อยู่ในฝั่งใดเลย (ก็คือ marker ที่ Git เพิ่งเขียนลงไปเอง) และหัว hunk ใช้ `@@@` สามตัว

**จังหวะที่ 2 — มนุษย์ตัดสิน + ประกาศสันติภาพ:** สมชายโทรหาป้า สรุปว่า *เอาทั้งคู่!* — เปิด `nano special.txt` ลบ marker ทั้งสามบรรทัดทิ้ง เหลือข้อความสุดท้ายบรรทัดเดียว (หรือใช้ `echo` ทับแบบด้านล่างก็ได้ผลเดียวกัน) แล้ว `git add` บอก Git ว่า "ไฟล์นี้จบแล้ว":

```bash
echo "Special: Matcha Latte and Iced Cocoa" > special.txt
git add special.txt
git status
```

**Expected Output**

```
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
	modified:   special.txt
```

**จังหวะที่ 3 — ปิดสงครามด้วย commit:**

```bash
git commit
```

> ⌨️ nano เด้งขึ้นมาพร้อมข้อความ default `Merge branch 'feature-weekend'` — กด **Ctrl+O → Enter → Ctrl+X** เหมือนเดิม

**Expected Output** *(หลังออกจาก nano)*

```
[main 078bc04] Merge branch 'feature-weekend'
```

ตรวจสนามหลังสงคราม แล้วเก็บป้าย:

```bash
git log --oneline --graph
git branch -d feature-weekend
cat special.txt
```

**Expected Output**

```
*   078bc04 (HEAD -> main) Merge branch 'feature-weekend'
|\
| * 77fa925 (feature-weekend) Weekend special: Matcha Latte
* | acf24cc Change special to Iced Cocoa
|/
*   89f3df3 Merge branch 'feature-cake'
|\
| * 46913ff Add cake menu
* | 8c6e723 Add contact info
|/
* 977c83e Add thai tea
* 4ece70b Add green tea
* ef92a02 Initial menu

Deleted branch feature-weekend (was 77fa925).

Special: Matcha Latte and Iced Cocoa
```

> 🎉 เพชรเม็ดที่สองขึ้นแผนที่ — ประวัติเล่าเรื่องครบ: ใครแยกไปทำอะไร ชนกันตรงไหน และมนุษย์ตัดสินอย่างไร · **Pain Point ครบทั้ง 4 ข้อ**: งานใน branch กลับบ้านได้ (FF) · สองงานรวมกันไม่มีของหาย (3-way) · ชนบรรทัดเดียวกันก็มีขั้นตอนแก้ (conflict) · และ `git diff` ส่องความต่างได้ทุกจังหวะ

---

## 8) สรุป + Cheat Sheet 📋

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git merge <branch>` | รวม `<branch>` เข้า branch ที่ยืนอยู่ (ยืนที่ปลายทางเสมอ!) |
| — ผล `Fast-forward` | เส้นเดิมไม่มี commit สวน → เลื่อนป้ายตาม ไม่มี commit ใหม่ |
| — ผล `Merge made by the 'ort' strategy.` | สองเส้นแยกกันจริง → Git สร้าง merge commit (ตั้งชื่อ default `Merge branch '...'`) |
| — ผล `CONFLICT (content)` | สองเส้นแก้บรรทัดเดียวกัน → หยุดรอมนุษย์: แก้ไฟล์ → `add` → `commit` |
| `git merge --abort` | ทางหนีไฟ: ยกเลิก merge ที่ค้าง กลับสภาพก่อนชน |
| `git diff` | ดูของที่แก้แล้วยังไม่ stage (และดูเขตสงครามตอน conflict) |
| `git diff <b1> <b2>` | เทียบสอง branch — พยากรณ์ conflict ก่อน merge |
| `git log --oneline --all --graph` | แผนที่ประวัติ: เห็นเส้นแยก สองง่าม และเพชร merge |
| `git branch -d <branch>` | ลบป้ายที่ merge แล้ว (ผ่านฉลุย — ต่างจาก LAB 00 ที่ต้องใช้ `-D`) |

**ภาพจำ:** งานเดินเส้นเดียว = Fast-forward · สองเส้นแตะคนละที่ = AUTO Commit · สองเส้นแตะที่เดียวกัน = มนุษย์ตัดสิน

---

## 9) Checklist ✅

- [ ] merge แรกเห็นคำว่า `Fast-forward` และ `git log --graph` **ไม่มี** merge commit (เส้นตรง)
- [ ] อธิบายได้ว่าทำไมเคสแรกถึง fast-forward ได้ (main ไม่มี commit สวนทาง)
- [ ] merge ที่สองเห็น `Merge made by the 'ort' strategy.` + nano เด้งพร้อมข้อความ `Merge branch 'feature-cake'`
- [ ] `git log --oneline --graph` เห็นรูปเพชร (commit ที่มี parent สองตัว)
- [ ] ใช้ `git diff main feature-weekend` พยากรณ์ conflict ได้ก่อน merge จริง
- [ ] เจอ `CONFLICT (content)` แล้วไม่ตกใจ — ชี้ได้ว่าในไฟล์ ส่วนไหนของ `HEAD` ส่วนไหนของอีก branch
- [ ] แก้ conflict ครบ 3 จังหวะ: แก้ไฟล์ → `git add` → `git commit`
- [ ] ลบ branch ที่ merge แล้วด้วย `-d` ตัวเล็กผ่านโดยไม่มี error
- [ ] จบ LAB: `git branch` เหลือ `* main` เส้นเดียว และ `special.txt` เป็นข้อความที่ตัดสินแล้ว

---

## 10) คำถามทบทวน ❓

1. เงื่อนไขอะไรทำให้ merge เป็นแบบ Fast-forward ได้ และผลลัพธ์ต่างจาก 3-way merge อย่างไรในแผนที่ `git log --graph`?
2. ก่อน merge ต้อง `git switch` ไปที่ branch ไหน — ปลายทางหรือต้นทาง? เพราะอะไร?
3. ทำไม merge ใน STEP 2 (เค้ก vs เบอร์ติดต่อ) Git ถึงรวมให้เองได้ แต่ STEP 3 (เมนูพิเศษ) ต้องให้มนุษย์ตัดสิน?
4. ข้อความ default ของ merge commit คืออะไร และมันโผล่ขึ้นมาตอนไหนบนหน้าจอ?
5. ใน conflict marker — ส่วนที่อยู่เหนือ `=======` เป็นของฝั่งไหน? `>>>>>>> feature-weekend` บอกอะไร?
6. ขั้นตอนดับไฟ conflict 3 จังหวะมีอะไรบ้าง? ถ้าอยากล้มกระดานกลับไปก่อน merge ใช้คำสั่งอะไร?
7. `git diff main feature-weekend` ช่วยอะไรเรา*ก่อน* merge — บรรทัดที่ขึ้นต้น `-` และ `+` หมายถึงฝั่งไหน?
8. ทำไม `git branch -d feature-tea` ใน LAB นี้ผ่านฉลุย ทั้งที่ LAB 00 คำสั่งเดียวกันโดน error จนต้องใช้ `-D`?

---

*LAB 01 — Merge Day · DevTools Week 3 · expected output ทุกจุดรันจริงบน `tuchsanai/devtools:2569_1` (git 2.43.0) — commit hash ของแต่ละคนจะต่างจากตัวอย่าง · ตัวอย่างใช้ตัวตนสมมุติ `somchai-dev` — ใช้ชื่อและอีเมลของตัวเองเสมอ*
