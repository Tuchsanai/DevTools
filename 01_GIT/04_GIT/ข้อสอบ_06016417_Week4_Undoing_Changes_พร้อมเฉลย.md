# Q1
ในสถานะปกติ HEAD ของ Git จะชี้ไปยัง branch reference แต่เมื่อเกิดสถานะ **detached HEAD** หมายความว่าอย่างไร?

- A. HEAD ถูกลบออกจาก repository จนกว่าจะ commit ใหม่
- B. HEAD ชี้ไปยัง branch มากกว่าหนึ่ง branch พร้อมกัน
- C. HEAD ชี้ตรงไปยัง commit ใด commit หนึ่ง โดยไม่ผ่าน branch reference
- D. HEAD ชี้ไปยัง staging area แทนที่จะชี้ไปยัง repository
- E. HEAD ชี้ไปยัง remote repository แทน local repository

===ANSWER_START===
เฉลย: C
เหตุผล: detached HEAD คือสถานะที่ HEAD ชี้ตรงไปที่ commit hash โดยตรง (เช่นหลัง git checkout <hash>) แทนที่จะชี้ผ่าน branch — commit ใหม่ที่สร้างในสถานะนี้จะไม่ถูก branch ใดอ้างอิง
[verified ด้วยเหตุผล (ไม่ต้องรัน) — นิยามตรงตามสไลด์ Week 4 และ LAB01]
===ANSWER_END===

# Q2
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init travel-log
cd travel-log
echo "Day 1: Bangkok" > journal.txt
git add journal.txt
git commit -m "day1"
echo "Day 2: Chiang Mai" >> journal.txt
git commit -am "day2"
echo "Day 3: Phuket" >> journal.txt
git commit -am "day3"
echo "Day 4: Krabi" >> journal.txt
git commit -am "day4"
git checkout HEAD~2
```

หลังจากรันคำสั่งเหล่านี้ เนื้อหาของ journal.txt จะเป็นอย่างไร?

- A. มีบรรทัดเดียวคือ Day 1: Bangkok
- B. มี 2 บรรทัดคือ Day 1: Bangkok และ Day 2: Chiang Mai
- C. มี 3 บรรทัดคือ Day 1 ถึง Day 3
- D. มีครบ 4 บรรทัด เพราะ git checkout ไม่เปลี่ยนเนื้อหาไฟล์
- E. เกิด error เพราะใช้ HEAD~2 กับ git checkout ไม่ได้

===ANSWER_START===
เฉลย: B
เหตุผล: HEAD~2 นับถอยจาก commit "day4" ไป 2 ครั้ง = commit "day2" การ checkout จึงย้อนไฟล์กลับเป็นเวอร์ชันที่มี 2 บรรทัด
[verified ใน container แล้ว — output จริง: "HEAD is now at 90fee9e day2" และ cat ได้ 2 บรรทัด Day 1 / Day 2]
===ANSWER_END===

# Q3
repository หนึ่งมีประวัติ commit ดังนี้ (ใหม่สุดอยู่บนสุด, working tree clean):

```
b4dbc00 add summary section
0171668 fix typo in intro
6903f93 add conclusion
d3512e9 add methodology
8418f60 add introduction
ed8a43e initial draft
```

หลังจากรันคำสั่งต่อไปนี้:

```
git checkout d3512e9
git log --oneline
```

git log --oneline จะแสดง commit ทั้งหมดกี่รายการ?

- A. 3 รายการ
- B. 6 รายการ
- C. 4 รายการ
- D. 2 รายการ
- E. เกิด error เพราะต้องสร้าง branch ก่อนจึงจะดู log ได้

===ANSWER_START===
เฉลย: A
เหตุผล: git log แสดงเฉพาะ commit ตั้งแต่ตำแหน่ง HEAD ปัจจุบันย้อนลงไป — เมื่อ HEAD อยู่ที่ d3512e9 (add methodology) จึงเห็นเพียง 3 รายการ ส่วน commit ที่ใหม่กว่าไม่แสดงแต่ไม่ได้ถูกลบ
[verified ใน container แล้ว — สร้าง 6 commits จริง, checkout ไป commit ที่ 3, git log --oneline | wc -l = 3]
===ANSWER_END===

# Q4
นักศึกษาคนหนึ่ง checkout ไปยัง commit เก่าจนอยู่ในสถานะ detached HEAD แล้วทดลองแก้โค้ดพร้อม commit ไปแล้ว 1 ครั้ง ต้องการเก็บงานนี้ไว้เป็น branch ใหม่ชื่อ hotfix-rescue **ก่อนออกจากสถานะ detached HEAD** คำสั่งใดถูกต้อง?

- A. `git branch --keep hotfix-rescue`
- B. `git checkout --save hotfix-rescue`
- C. `git head attach hotfix-rescue`
- D. `git switch -c hotfix-rescue`
- E. `git commit --branch hotfix-rescue`

===ANSWER_START===
เฉลย: D
เหตุผล: git switch -c <branch> สร้าง branch ใหม่ที่ตำแหน่ง HEAD ปัจจุบันและ attach HEAD เข้ากับ branch นั้น (ตรงตามคำแนะนำที่ Git แสดงตอนเข้า detached HEAD) — ตัวเลือกอื่นไม่มีอยู่จริงหรือใช้ไม่ได้
[verified ใน container แล้ว — A: error: unknown option 'keep', B: error: unknown option 'save', C: git: 'head' is not a git command, E: error: pathspec 'hotfix-rescue' did not match any file(s), D: Switched to a new branch 'hotfix-rescue']
===ANSWER_END===

# Q5
repository ชื่อ api-server มี 5 commits แก้ไขไฟล์ server.py ตามลำดับ และ working tree clean จากนั้นรัน:

```
git checkout 11023f3
```

โดย 11023f3 คือ hash ของ **commit ที่ 2** (นับจากเก่าสุด) หลังจากนั้นรัน git status ผลลัพธ์จะเป็นอย่างไร?

- A. On branch master และ nothing to commit, working tree clean
- B. HEAD detached at 11023f3 และ nothing to commit, working tree clean
- C. HEAD detached at 11023f3 และ Changes not staged for commit: modified: server.py
- D. เกิด error เพราะใช้ git status ในสถานะ detached HEAD ไม่ได้
- E. On branch 11023f3 และ nothing to commit, working tree clean

===ANSWER_START===
เฉลย: B
เหตุผล: การ checkout ไป commit เก่าทำให้เข้าสถานะ detached HEAD — git status จะรายงานบรรทัดแรกว่า HEAD detached at <hash> และเนื่องจากไฟล์ตรงกับ commit นั้นพอดี working tree จึง clean
[verified ใน container แล้ว — output จริง: "HEAD detached at 11023f3" / "nothing to commit, working tree clean"]
===ANSWER_END===

# Q6
ขณะอยู่ในสถานะ detached HEAD ที่ commit เก่า (ไม่มีการแก้ไขใด ๆ ค้างอยู่) เมื่อรันคำสั่ง:

```
git checkout master
```

ข้อใดอธิบายผลลัพธ์ได้ถูกต้อง?

- A. เกิด error เพราะออกจาก detached HEAD ได้ด้วย git switch เท่านั้น
- B. HEAD ยังคง detached อยู่ แต่เนื้อหาไฟล์เปลี่ยนเป็นเวอร์ชันล่าสุด
- C. branch master ถูกย้ายมาชี้ที่ commit ที่กำลัง detached อยู่
- D. ไฟล์ใน working directory คงเดิม แต่ HEAD กลับไปชี้ master
- E. HEAD กลับไป attach กับ branch master และไฟล์กลับเป็นเวอร์ชันของ commit ล่าสุด

===ANSWER_START===
เฉลย: E
เหตุผล: git checkout master ทำให้ HEAD กลับไปชี้ branch master ซึ่งชี้ commit ล่าสุดอยู่ working directory จึงถูกอัปเดตเป็นไฟล์เวอร์ชันล่าสุด — branch pointer ไม่ถูกย้าย และ checkout ใช้ออกจาก detached ได้เช่นเดียวกับ switch
[verified ด้วยเหตุผล (ไม่ต้องรัน) — พฤติกรรมตรงตาม LAB01 ขั้นตอน "Return to the Latest Commit"]
===ANSWER_END===

# Q7
repository ชื่อ inventory มี 5 commits ข้อความ add item 1 ถึง add item 5 (แก้ไฟล์ stock.csv ตามลำดับ) จากนั้น checkout ไปยัง hash ของ commit "add item 2" แล้วรันสองคำสั่งนี้:

```
git log --oneline          # แสดง X รายการ
git log --oneline --all    # แสดง Y รายการ
```

X และ Y มีค่าเท่าใด?

- A. X = 5, Y = 5
- B. X = 2, Y = 2
- C. X = 2, Y = 5
- D. X = 3, Y = 5
- E. X = 5, Y = 2

===ANSWER_START===
เฉลย: C
เหตุผล: git log ธรรมดาแสดงเฉพาะ commit ตั้งแต่ HEAD ย้อนลงไป (item 2, item 1 → X=2) ส่วน --all แสดง commit ทุก reference ใน repository รวมที่อยู่ "ข้างหน้า" HEAD ด้วย (Y=5)
[verified ใน container แล้ว — output จริง: X=2, Y=5]
===ANSWER_END===

# Q8
ตามที่สอนในชั้นเรียน คำสั่ง git checkout เป็นคำสั่งอเนกประสงค์ที่สามารถทำงานกับ entity ใดได้บ้าง?

- A. files, commits และ branches
- B. commits และ branches เท่านั้น
- C. branches เท่านั้น
- D. files และ branches เท่านั้น
- E. remotes, tags และ stashes เท่านั้น

===ANSWER_START===
เฉลย: A
เหตุผล: สไลด์ Week 4 ระบุตรงว่า "The git checkout command can operate on three distinct entities: files, commits, and branches" — ความอเนกประสงค์นี้เป็นเหตุให้เกิดคำสั่งใหม่อย่าง git switch ขึ้นมาแทนบางหน้าที่
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ข้อเท็จจริงตรงจากสไลด์หน้า 6]
===ANSWER_END===

# Q9
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init lab-experiment
cd lab-experiment
echo "v1" > config.yml
git add . && git commit -m "C1"
echo "v2" >> config.yml && git commit -am "C2"
echo "v3" >> config.yml && git commit -am "C3"
git checkout HEAD~2
echo "experiment" >> config.yml
git commit -am "trial"
git checkout master
git log --oneline
```

หลังจากรันคำสั่งเหล่านี้ ผลลัพธ์ของ git log --oneline และชะตากรรมของ commit "trial" จะเป็นอย่างไร?

- A. log แสดง 4 commits รวม trial ด้วย เพราะ commit สำเร็จไปแล้ว
- B. เกิด error ตั้งแต่คำสั่ง commit เพราะ commit ในสถานะ detached HEAD ไม่ได้
- C. commit trial ถูกลบออกจาก repository ทันทีและกู้คืนไม่ได้
- D. log แสดง 3 commits (C3, C2, C1) — trial ไม่แสดง แต่ Git แจ้ง hash พร้อมวิธีสร้าง branch เก็บไว้
- E. คำสั่ง git checkout master ล้มเหลว เพราะมี commit ค้างอยู่ใน detached HEAD

===ANSWER_START===
เฉลย: D
เหตุผล: commit ในสถานะ detached HEAD ทำได้ปกติ แต่เมื่อสลับกลับ master โดยไม่สร้าง branch เก็บ Git จะเตือน "Warning: you are leaving 1 commit behind..." พร้อมแนะนำ git branch <new-branch-name> <hash> — commit ยังอยู่ใน object database ไม่ได้ถูกลบทันที
[verified ใน container แล้ว — output จริง: Warning + "git branch <new-branch-name> 5f544b8" และ log แสดง 3 รายการ]
===ANSWER_END===

# Q10
นักศึกษา checkout ไปยัง commit กลางประวัติจนเข้าสถานะ detached HEAD แล้วพบว่า git log --oneline ไม่แสดง commit ที่ใหม่กว่าตำแหน่งปัจจุบัน สาเหตุคือข้อใด?

- A. commit ที่ใหม่กว่าถูกลบออกจาก repository ชั่วคราวจนกว่าจะกลับ branch เดิม
- B. สถานะ detached HEAD ทำให้ Git ล็อกประวัติไว้ที่ commit แรกของ repository
- C. git log แสดงเฉพาะ commit ที่อยู่ใน staging area ณ ขณะนั้น
- D. branch pointer ถูกย้ายถอยหลังมาที่ commit นี้แล้ว commit ข้างหน้าจึงหลุดจากประวัติ
- E. git log ไล่แสดงเฉพาะ commit ที่เป็นบรรพบุรุษ (ancestor) ของ HEAD ปัจจุบันเท่านั้น

===ANSWER_START===
เฉลย: E
เหตุผล: git log เดินย้อนจาก HEAD ลงไปตามสาย parent เท่านั้น commit ที่ "อยู่ข้างหน้า" HEAD จึงไม่แสดง แต่ยังอยู่ครบใน repository (ดูได้ด้วย git log --oneline --all) — ข้อ D ผิดเพราะ checkout ไม่ย้าย branch pointer (นั่นคือพฤติกรรมของ reset)
[verified ด้วยเหตุผล (ไม่ต้องรัน) — แนวคิดตาม LAB01 Tip; พฤติกรรม log/--all ยืนยันจากการรันข้อ 7]
===ANSWER_END===

# Q11
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init cafe-menu
cd cafe-menu
echo "Espresso" > menu.txt
git add . && git commit -m "C1 espresso"
echo "Latte" >> menu.txt
git commit -am "C2 latte"
echo "Mocha" >> menu.txt
git commit -am "C3 mocha"
git checkout HEAD~1 -- menu.txt
```

หลังจากรันคำสั่งเหล่านี้ สถานะของ repository จะเป็นอย่างไร?

- A. menu.txt ย้อนเป็นเวอร์ชัน C2 (2 บรรทัด) และการเปลี่ยนแปลงถูกจัดเข้า staging area ให้อัตโนมัติ
- B. menu.txt ย้อนเป็นเวอร์ชัน C2 แต่อยู่ในสถานะ modified ที่ยังไม่ staged
- C. เข้าสู่สถานะ detached HEAD ที่ commit C2
- D. เกิด error เพราะ git checkout ใช้กับไฟล์เดี่ยวไม่ได้
- E. ไฟล์ไม่เปลี่ยนแปลง เพราะการย้อนไฟล์เดี่ยวต้องใช้ git restore เท่านั้น

===ANSWER_START===
เฉลย: A
เหตุผล: git checkout <commit> -- <file> คือรูปแบบ "checkout ระดับไฟล์" — ดึงไฟล์จาก commit ที่ระบุมาทับทั้ง working directory และ staging area (HEAD ไม่ย้าย จึงไม่ detached) git status จึงแสดง "Changes to be committed: modified: menu.txt"
[verified ใน container แล้ว — cat ได้ Espresso/Latte และ status แสดง Changes to be committed]
===ANSWER_END===

# Q12
นักพัฒนาต้องการ "ย้อนเวลา" ไปดูโค้ดทั้งโปรเจกต์ ณ commit เก่าชั่วคราวเพื่อตรวจสอบเท่านั้น โดยไม่ต้องการแก้ไขประวัติหรือย้าย branch pointer ใด ๆ คำสั่งใดเหมาะสมที่สุด?

- A. `git reset --hard <hash>`
- B. `git revert <hash>`
- C. `git checkout <hash>`
- D. `git restore --staged <hash>`
- E. `git log -p <hash>`

===ANSWER_START===
เฉลย: C
เหตุผล: git checkout <hash> พาเข้า detached HEAD เพื่อสำรวจโค้ด ณ จุดนั้นโดยไม่แตะประวัติและ branch — reset --hard ตัด commit ทิ้ง, revert สร้าง commit ใหม่, restore --staged ใช้กับไฟล์ไม่ใช่การย้อนทั้งโปรเจกต์, log -p แค่แสดง diff ไม่เปลี่ยน working directory
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์ "you are simply exploring the historical commit" และพฤติกรรมที่รันยืนยันในข้อ 2, 5]
===ANSWER_END===

# Q13
นักศึกษารัน git checkout <hash> จนอยู่ในสถานะ detached HEAD (จาก branch master) จากนั้นรันคำสั่งตามที่ Git แนะนำ:

```
git switch -
```

คำสั่งนี้ให้ผลอย่างไร?

- A. สลับไปยัง commit แรกสุดของ repository
- B. กลับไปยังตำแหน่งก่อนหน้า คือ branch master
- C. สร้าง branch ใหม่ชื่อ "-"
- D. เกิด error เพราะ git switch ต้องระบุชื่อ branch เสมอ
- E. เลื่อนไปยัง commit ถัดไป (ไปข้างหน้า 1 commit)

===ANSWER_START===
เฉลย: B
เหตุผล: เครื่องหมาย - หมายถึง "ตำแหน่งก่อนหน้า" (เหมือน cd -) — Git แนะนำ git switch - ไว้ในข้อความตอนเข้า detached HEAD เพื่อ undo การ checkout กลับไปที่เดิม
[verified ใน container แล้ว — output จริง: "Previous HEAD position was d5fb85d C1" / "Switched to branch 'master'"]
===ANSWER_END===

# Q14
ข้อใดอธิบายความแตกต่างระหว่าง `git checkout feature-x` (ชื่อ branch) กับ `git checkout 3f2a91c` (commit hash) ได้ถูกต้อง?

- A. ทั้งสองแบบให้ผลเหมือนกันทุกประการ
- B. แบบแรกเปลี่ยนไฟล์ใน working directory แต่แบบหลังไม่เปลี่ยน
- C. แบบหลังจะลบ commit ที่ใหม่กว่า 3f2a91c ออกจากประวัติ
- D. แบบแรก HEAD ยัง attach กับ branch ตามปกติ แต่แบบหลัง HEAD จะ detach ไปชี้ commit โดยตรง
- E. แบบแรกใช้ได้เฉพาะกับ branch ชื่อ main หรือ master เท่านั้น

===ANSWER_START===
เฉลย: D
เหตุผล: checkout ด้วยชื่อ branch ทำให้ HEAD ชี้ผ่าน branch reference (สถานะปกติ) ส่วน checkout ด้วย hash ทำให้ HEAD ชี้ commit ตรง ๆ = detached HEAD — ทั้งสองแบบต่างก็อัปเดตไฟล์ และไม่มีแบบใดลบ commit
[verified ด้วยเหตุผล (ไม่ต้องรัน) — นิยามจากสไลด์และพฤติกรรมที่รันยืนยันแล้วในข้อ 5]
===ANSWER_END===

# Q15
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง แล้วสร้าง 5 commits โดยแต่ละ commit เติมบรรทัด "Chapter 1" ถึง "Chapter 5" ลงไฟล์ chapter.txt ทีละบรรทัด):

```
git checkout HEAD~3
git checkout master
git checkout HEAD~1
cat chapter.txt
```

หลังจากรันครบทุกคำสั่ง chapter.txt จะมีกี่บรรทัด?

- A. 2 บรรทัด
- B. 3 บรรทัด
- C. 4 บรรทัด
- D. 5 บรรทัด
- E. 1 บรรทัด

===ANSWER_START===
เฉลย: C
เหตุผล: HEAD~N วัดจากตำแหน่ง HEAD "ปัจจุบัน" เสมอ — คำสั่งแรกพาไป C2 (2 บรรทัด) คำสั่งที่สองกลับ master (C5, 5 บรรทัด) คำสั่งที่สามนับจาก C5 ถอย 1 = C4 ไฟล์จึงเหลือ 4 บรรทัด
[verified ใน container แล้ว — cat สุดท้ายได้ Chapter 1–4 และ status: HEAD detached]
===ANSWER_END===

# Q16
ขณะอยู่ในสถานะ detached HEAD ที่ commit เก่า ต้องการดูประวัติ commit แบบย่อ "ทุก commit" ใน repository รวมทั้ง commit ที่อยู่ข้างหน้า HEAD ด้วย ต้องใช้คำสั่งใด?

- A. `git log --oneline --all`
- B. `git log --oneline --full`
- C. `git history --oneline`
- D. `git show-all --oneline`
- E. `git log --oneline --head`

===ANSWER_START===
เฉลย: A
เหตุผล: --all สั่งให้ log ไล่จากทุก reference (ทุก branch) จึงเห็น commit ที่อยู่ข้างหน้า HEAD ด้วย ตรงตาม Tip ใน LAB01 — ตัวเลือกอื่นไม่มีอยู่จริง
[verified ใน container แล้ว — B: fatal: unrecognized argument: --full, C: error, D: git: 'show-all' is not a git command, E: fatal: unrecognized argument: --head; ส่วน --all ใช้ได้จริง (ข้อ 7)]
===ANSWER_END===

# Q17
คำสั่ง `git restore report.docx` (ไม่ใส่ option ใด ๆ) ทำหน้าที่อะไร?

- A. ลบไฟล์ report.docx ออกจาก repository
- B. ทิ้งการแก้ไขของ report.docx ใน working directory คืนไฟล์เป็นเวอร์ชันที่บันทึกไว้ล่าสุด
- C. สร้าง commit ใหม่ที่ย้อนการแก้ไขของ report.docx
- D. ถอนไฟล์ report.docx ออกจาก staging area
- E. ย้าย HEAD กลับไปยัง commit ก่อนหน้าของ report.docx

===ANSWER_START===
เฉลย: B
เหตุผล: git restore <file> คือ "Ctrl+Z ขั้นสุดท้าย" — เขียนทับไฟล์ใน working directory ด้วยเวอร์ชันที่บันทึกไว้ ไม่สร้าง commit ไม่แตะ staging area ของไฟล์อื่น และไม่ย้าย HEAD (การ unstage ต้องใช้ --staged)
[verified ด้วยเหตุผล (ไม่ต้องรัน) — นิยามตรงตามสไลด์และ LAB02 Task 2]
===ANSWER_END===

# Q18
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มี 3 commits ของไฟล์ post.md ซึ่งมีเนื้อหา 3 บรรทัด: post v1, post v2, post v3 และ working tree clean):

```
echo "draft idea" >> post.md
git restore post.md
```

หลังจากรันคำสั่งเหล่านี้ ผลลัพธ์จะเป็นอย่างไร?

- A. post.md ยังมี 4 บรรทัด เพราะ git restore ต้องระบุ --source เสมอ
- B. post.md เหลือ 3 บรรทัด แต่ git status ยังแสดง modified
- C. post.md เหลือ 3 บรรทัด และ git log เหลือ 2 commits
- D. เกิด error เพราะยังไม่ได้ git add ไฟล์ก่อน restore
- E. post.md เหลือ 3 บรรทัดเดิม, working tree clean และ git log ยังมี 3 commits ครบ

===ANSWER_START===
เฉลย: E
เหตุผล: git restore ดึงเวอร์ชันล่าสุดมาทับ บรรทัด "draft idea" ที่ยังไม่เคย commit จึงหายไป status กลับมา clean และประวัติ commit ไม่เปลี่ยนเพราะ restore ไม่สร้าง/ลบ commit
[verified ใน container แล้ว — cat ได้ 3 บรรทัด, "nothing to commit, working tree clean", log count = 3]
===ANSWER_END===

# Q19
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init kitchen && cd kitchen
echo "step1: prep" > recipe.txt
git add . && git commit -m "C1 recipe step1"
echo "buy eggs" > notes.txt
git add . && git commit -m "C2 notes"
echo "step2: mix" >> recipe.txt
git add . && git commit -m "C3 recipe step2"
echo "buy milk" >> notes.txt
git add . && git commit -m "C4 notes2"
echo "step3: bake" >> recipe.txt
git add . && git commit -m "C5 recipe step3"
git restore --source=HEAD~3 recipe.txt
```

หลังจากรันคำสั่งเหล่านี้ เนื้อหาของ recipe.txt จะเป็นอย่างไร?

- A. มี 1 บรรทัดคือ step1: prep
- B. มี 2 บรรทัดคือ step1: prep และ step2: mix
- C. มี 3 บรรทัดครบ ไม่เปลี่ยนแปลง
- D. เกิด error เพราะ commit ที่ HEAD~3 แก้ไข notes.txt ไม่ใช่ recipe.txt
- E. recipe.txt ถูกลบออกจาก working directory

===ANSWER_START===
เฉลย: A
เหตุผล: HEAD~3 นับถอยจาก C5 ไป 3 ครั้ง = C2 ซึ่ง ณ จุดนั้น recipe.txt มีเพียงบรรทัดเดียว (step2 เพิ่มมาใน C3) — กับดักคือการเผลอนับเฉพาะ commit ที่แก้ recipe.txt ซึ่งจะได้คำตอบ B ที่ผิด
[verified ใน container แล้ว — cat ได้ "step1: prep" บรรทัดเดียว]
===ANSWER_END===

# Q20
นักพัฒนา `git add` ไฟล์ไป 3 ไฟล์ (app.js, style.css, index.html) แล้วเปลี่ยนใจ ต้องการถอนเฉพาะ app.js ออกจาก staging area โดยให้การแก้ไขในไฟล์ยังคงอยู่ คำสั่งใดถูกต้อง?

- A. `git unstage app.js`
- B. `git rm --staged app.js`
- C. `git restore app.js`
- D. `git restore --staged app.js`
- E. `git reset --hard app.js`

===ANSWER_START===
เฉลย: D
เหตุผล: git restore --staged คือคำสั่ง unstage ที่ตรงหน้าที่ (ตรงข้าม git add) — A ไม่มีจริง, B option จริงคือ --cached, C จะย้อนไฟล์ใน working directory (คนละหน้าที่), E ใช้ --hard กับ path ไม่ได้
[verified ใน container แล้ว — A: git: 'unstage' is not a git command, B: error: unknown option 'staged', E: fatal: Cannot do hard reset with paths.]
===ANSWER_END===

# Q21
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มีไฟล์ cart.js เนื้อหา "base price" ถูก commit แล้ว):

```
echo "promo code" >> cart.js
git add cart.js
git restore --staged cart.js
```

หลังจากรันคำสั่งเหล่านี้ ข้อใดถูกต้อง?

- A. บรรทัด promo code หายไปจากไฟล์ และ working tree clean
- B. ไฟล์กลับเป็นเวอร์ชันที่ commit ล่าสุดทั้งใน staging และ working directory
- C. cart.js ยังมีบรรทัด promo code อยู่ แต่สถานะเปลี่ยนเป็น modified ที่ยังไม่ staged
- D. เกิด error เพราะ restore --staged ใช้หลัง git add ไม่ได้
- E. การแก้ไขถูก commit ให้อัตโนมัติ

===ANSWER_START===
เฉลย: C
เหตุผล: git restore --staged แตะเฉพาะ staging area (รีเซ็ตให้เท่ากับ HEAD) แต่ไม่แตะ working directory — ไฟล์จึงยังมีบรรทัดใหม่อยู่ครบ เพียงย้ายจาก "Changes to be committed" กลับไป "Changes not staged for commit"
[verified ใน container แล้ว — cat ยังเห็น promo code และ status แสดง Changes not staged: modified: cart.js]
===ANSWER_END===

# Q22
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มีไฟล์ index.html ถูก commit แล้ว):

```
echo "<svg>" > banner.svg
git add banner.svg
git restore --staged banner.svg
```

banner.svg เป็นไฟล์ใหม่ที่ไม่เคย commit มาก่อน — หลังคำสั่งสุดท้าย สถานะของ banner.svg จะเป็นอย่างไร?

- A. เกิด error เพราะ --staged ใช้ได้เฉพาะไฟล์ที่เคย commit แล้ว
- B. กลับเป็นไฟล์ untracked โดยเนื้อหาไฟล์ยังอยู่ครบ
- C. ไฟล์ถูกลบออกจาก working directory
- D. ไฟล์ยังคงอยู่ใน staging area ต่อไป
- E. ไฟล์ถูก commit ให้อัตโนมัติ

===ANSWER_START===
เฉลย: B
เหตุผล: สำหรับไฟล์ใหม่ที่เพิ่ง add การ unstage คือการเอา entry ออกจาก index ไฟล์จึงกลับเป็น untracked — ตัวไฟล์ใน working directory ไม่ถูกแตะเช่นเดิม
[verified ใน container แล้ว — status เปลี่ยนจาก "new file: banner.svg" เป็น "Untracked files: banner.svg" และ ls ยังเห็นไฟล์]
===ANSWER_END===

# Q23
ใน repo หนึ่งมีไฟล์ secret.env ที่เพิ่งสร้างใหม่ ยังไม่เคยผ่าน git add หรือ commit ใด ๆ (untracked) เมื่อรัน:

```
git restore secret.env
```

ผลลัพธ์จะเป็นอย่างไร?

- A. ไฟล์ secret.env ถูกลบออกจาก working directory
- B. ไม่มีอะไรเกิดขึ้น คำสั่งจบแบบเงียบ ๆ
- C. ไฟล์ถูกเพิ่มเข้า staging area
- D. Git สร้างไฟล์เวอร์ชันว่างเปล่าขึ้นมาแทน
- E. เกิด error: pathspec 'secret.env' did not match any file(s) known to git

===ANSWER_START===
เฉลย: E
เหตุผล: git restore ทำงานได้เฉพาะไฟล์ที่ Git รู้จัก (tracked หรืออยู่ใน index) — ไฟล์ untracked ไม่มีเวอร์ชันให้ย้อน จึงเกิด error pathspec
[verified ใน container แล้ว — output จริง: error: pathspec 'secret.env' did not match any file(s) known to git]
===ANSWER_END===

# Q24
เหตุใดการแก้ไขที่ถูกทิ้งด้วย `git restore <file>` จึง "กู้คืนไม่ได้" ต่างจากการเปลี่ยนแปลงที่ถูกลบด้วยวิธีอื่นใน Git?

- A. เพราะการแก้ไขนั้นยังไม่เคยถูกบันทึกเป็น commit จึงไม่มีสำเนาเก็บอยู่ใน repository เลย
- B. เพราะ git restore เข้ารหัสไฟล์เดิมทิ้งอย่างถาวร
- C. เพราะ git restore ลบ commit ล่าสุดออกจากประวัติไปด้วย
- D. ที่จริงกู้ได้เสมอด้วยคำสั่ง git restore --undo
- E. เพราะไฟล์ถูกย้ายไปเก็บบน remote repository แทน

===ANSWER_START===
เฉลย: A
เหตุผล: Git กู้ข้อมูลได้เฉพาะสิ่งที่เคยบันทึก (commit/stage) ไว้ — การแก้ไขที่ค้างใน working directory ไม่มีสำเนาใน object database เมื่อถูกเขียนทับจึงหายถาวร (คำเตือนตรงจากสไลด์: "You can not undo a git restore command, since your changes were not committed!")
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์และคำเตือนใน LAB02]
===ANSWER_END===

# Q25
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มี 4 commits ของ poem.txt เนื้อหา verse 1 ถึง verse 4 ทีละบรรทัด, working tree clean):

```
git restore --source=HEAD~2 poem.txt
git restore --source=HEAD poem.txt
```

หลังจากรันทั้งสองคำสั่ง เนื้อหาไฟล์และสถานะจะเป็นอย่างไร?

- A. 2 บรรทัด และ git status แสดง modified
- B. 2 บรรทัด และ working tree clean
- C. 4 บรรทัดครบ แต่ git status แสดง modified
- D. 4 บรรทัดครบ และ working tree clean
- E. เกิด error เพราะใช้ --source ซ้ำสองครั้งติดกันไม่ได้

===ANSWER_START===
เฉลย: D
เหตุผล: การ restore ด้วย --source ไม่ลบ commit ใด ๆ จึงย้อนกลับมาเวอร์ชันล่าสุดได้เสมอด้วย --source=HEAD — คำสั่งที่สองดึงเวอร์ชัน 4 บรรทัดกลับมาทับ ไฟล์ตรงกับ HEAD จึง clean (ตรงตามคำอธิบาย LAB02 Task 3)
[verified ใน container แล้ว — หลังคำสั่งแรกเหลือ 2 บรรทัด, หลังคำสั่งที่สอง cat ได้ 4 บรรทัด + working tree clean]
===ANSWER_END===

# Q26
ไฟล์ report.txt มีการแก้ไขผ่านหลาย commit นักพัฒนาต้องการดึงเนื้อหา report.txt "เวอร์ชันของ commit hash a1b2c3d" มาไว้ใน working directory คำสั่งใดถูกต้อง?

- A. `git restore a1b2c3d report.txt`
- B. `git restore --source=a1b2c3d report.txt`
- C. `git restore --commit=a1b2c3d report.txt`
- D. `git revert a1b2c3d -- report.txt`
- E. `git reset a1b2c3d report.txt`

===ANSWER_START===
เฉลย: B
เหตุผล: --source= ระบุ commit ต้นทางได้ทั้งรูปแบบ HEAD~N และ hash ตรง ๆ — A ตีความ hash เป็นชื่อไฟล์ (error pathspec), C ไม่มี option นี้, D revert ใช้กับ path ไม่ได้ (fatal: bad revision), E รีเซ็ตเฉพาะ index ของไฟล์ ไม่เปลี่ยน working directory
[verified ใน container แล้ว — A: error: pathspec 'cdca83d' did not match, C: error: unknown option, D: fatal: bad revision 'report.txt', E: worktree ไม่เปลี่ยน (ยัง 3 บรรทัด), B: ได้เนื้อหาเวอร์ชัน C1 จริง]
===ANSWER_END===

# Q27
repo หนึ่งมี 6 commits ที่แก้ไขไฟล์ menu.json ต่อเนื่อง (working tree clean) หลังจากรัน:

```
git restore --source=HEAD~4 menu.json
git status
```

git status จะรายงานว่าอย่างไร?

- A. nothing to commit, working tree clean เพราะ restore ไม่เปลี่ยนสถานะไฟล์
- B. Changes to be committed: modified: menu.json
- C. Untracked files: menu.json
- D. HEAD detached at HEAD~4
- E. Changes not staged for commit: modified: menu.json

===ANSWER_START===
เฉลย: E
เหตุผล: restore --source เขียนทับเฉพาะ working directory — เมื่อเนื้อหาไฟล์ต่างจากเวอร์ชัน HEAD สถานะจึงเป็น modified ที่ยังไม่ staged (ตรงตาม LAB02: "git status reports the file as modified because it now differs from HEAD")
[verified ใน container แล้ว — output จริง: Changes not staged for commit: modified: menu.json]
===ANSWER_END===

# Q28
ข้อใดสรุปความแตกต่างระหว่าง `git restore <file>` กับ `git restore --staged <file>` ได้ถูกต้อง?

- A. ทั้งสองแบบแก้ไขไฟล์ใน working directory เหมือนกัน
- B. --staged ทิ้งการแก้ไขในไฟล์ด้วย ส่วนแบบธรรมดาเก็บการแก้ไขไว้
- C. แบบธรรมดาเขียนทับไฟล์ใน working directory ส่วน --staged ถอนไฟล์จาก staging area โดยไม่แตะ working directory
- D. แบบธรรมดาใช้ unstage ไฟล์ ส่วน --staged ใช้ทิ้งการแก้ไข
- E. ทั้งสองแบบสร้าง commit ใหม่เพื่อบันทึกการย้อนกลับ

===ANSWER_START===
เฉลย: C
เหตุผล: สองรูปแบบนี้คือหัวใจของ LAB02 — แบบธรรมดา "ทิ้งการแก้ไขจริง ๆ" (อันตราย กู้ไม่ได้) ส่วน --staged แค่ย้ายไฟล์ออกจากคิวที่จะ commit การแก้ไขยังอยู่ครบในไฟล์
[verified ด้วยเหตุผล (ไม่ต้องรัน) — สรุปตรงตาม LAB02 Tasks 2 และ 4; พฤติกรรมจริงยืนยันแล้วในข้อ 18 และ 21]
===ANSWER_END===

# Q29
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init memo && cd memo
echo "alpha" > notes.txt
git add . && git commit -m "C1"
echo "beta" >> notes.txt
git add notes.txt
echo "gamma" >> notes.txt
git restore notes.txt
cat notes.txt
```

เนื้อหาของ notes.txt หลังคำสั่งสุดท้ายจะเป็นอย่างไร?

- A. alpha และ beta (2 บรรทัด) — gamma หายไป และการแก้ไขที่ staged ไว้ยังคงอยู่
- B. alpha บรรทัดเดียว เพราะ restore ดึงจาก commit ล่าสุด (HEAD) เสมอ
- C. alpha, beta, gamma ครบ 3 บรรทัด เพราะไฟล์ถูก staged อยู่จึง restore ไม่ได้
- D. เกิด error เพราะมีทั้งเวอร์ชัน staged และ modified พร้อมกัน
- E. ไฟล์กลายเป็น untracked

===ANSWER_START===
เฉลย: A
เหตุผล: git restore <file> (ไม่ระบุ --source) ใช้ **staging area (index)** เป็นต้นทาง ไม่ใช่ HEAD — เวอร์ชันที่ staged คือ alpha+beta จึงทับ gamma ที่ยังไม่ staged ทิ้ง ส่วน "Changes to be committed" ยังอยู่ครบ
[verified ใน container แล้ว — cat ได้ alpha/beta และ status ยังแสดง Changes to be committed: modified: notes.txt]
===ANSWER_END===

# Q30
จากพฤติกรรมของ `git restore <file>` เมื่อไม่ระบุ `--source` คำสั่งจะใช้อะไรเป็น "ต้นทาง" ของเนื้อหาที่นำมาเขียนทับ working directory?

- A. commit ล่าสุด (HEAD) เสมอ
- B. commit แรกสุดของ repository
- C. remote repository (origin)
- D. staging area (index) — ถ้ามีเวอร์ชัน staged อยู่จะได้เวอร์ชันนั้น ไม่ใช่เวอร์ชัน HEAD
- E. stash รายการล่าสุด

===ANSWER_START===
เฉลย: D
เหตุผล: ต้นทาง default ของการ restore working directory คือ index — ในกรณีทั่วไป (ไม่มีอะไร staged) index ตรงกับ HEAD จึงดูเหมือน "ย้อนเป็น commit ล่าสุด" แต่เมื่อมีเวอร์ชัน staged อยู่ ไฟล์จะกลับเป็นเวอร์ชัน staged (พิสูจน์จากข้อ 29) — ถ้าต้องการ HEAD จริง ๆ ให้ระบุ --source=HEAD
[verified ด้วยเหตุผล (ไม่ต้องรัน) — พฤติกรรมยืนยันด้วยผลรันจริงของข้อ 29 แล้ว]
===ANSWER_END===

# Q31
นักพัฒนาเผลอลบไฟล์ styles.css ทิ้งด้วยคำสั่ง `rm styles.css` ของ shell (ไฟล์นี้ถูก commit ไว้แล้ว และการลบยังไม่ได้ commit) ต้องการได้ไฟล์กลับคืนมา คำสั่งใดถูกต้อง?

- A. `git undelete styles.css`
- B. `git restore styles.css`
- C. `git revert styles.css`
- D. `git reset --soft styles.css`
- E. `git add styles.css`

===ANSWER_START===
เฉลย: B
เหตุผล: การลบไฟล์ใน working directory ก็คือ "การแก้ไขที่ยังไม่ commit" ชนิดหนึ่ง — git restore ดึงเวอร์ชันที่บันทึกไว้กลับมา ไฟล์จึงคืนมาพร้อมเนื้อหาเดิม
[verified ใน container แล้ว — หลัง rm แล้ว restore ไฟล์กลับมาพร้อมเนื้อหาเดิม + working tree clean; A: git: 'undelete' is not a git command]
===ANSWER_END===

# Q32
ไฟล์ config.ini ถูกแก้ไขและ `git add` ไปแล้ว จากนั้นถูกแก้เพิ่มอีกรอบ (มีทั้งเวอร์ชัน staged และแก้ค้างใน working directory) ต้องการล้างทั้งหมดให้ไฟล์กลับเป็นเวอร์ชัน HEAD ทั้งใน staging area และ working directory **ในคำสั่งเดียว** ต้องใช้คำสั่งใด?

- A. `git restore --all config.ini`
- B. `git restore --hard config.ini`
- C. `git undo config.ini`
- D. `git restore --full config.ini`
- E. `git restore --staged --worktree config.ini`

===ANSWER_START===
เฉลย: E
เหตุผล: git restore ระบุเป้าหมายได้สองส่วนพร้อมกัน (--staged = index, --worktree = ไฟล์จริง) เมื่อใส่คู่กัน ต้นทาง default คือ HEAD จึงล้างทั้งสองชั้นในคำสั่งเดียว — ตัวเลือกอื่นไม่มีอยู่จริง
[verified ใน container แล้ว — A/B/D: error: unknown option, C: git: 'undo' is not a git command, E: ไฟล์กลับเป็น mode=prod บรรทัดเดียว + working tree clean]
===ANSWER_END===

# Q33
repo หนึ่งมี 6 commits (C1 ถึง C6) โดยไฟล์ sauce.txt ถูกสร้างครั้งแรกใน commit C4 ขณะนี้ working tree clean เมื่อรัน:

```
git restore --source=HEAD~5 sauce.txt
```

(HEAD~5 คือ commit C1 ซึ่งยังไม่มี sauce.txt) — ผลลัพธ์จะเป็นอย่างไร?

- A. เกิด error: pathspec 'sauce.txt' did not match any file(s)
- B. ไฟล์ไม่เปลี่ยนแปลง เพราะ source ไม่มีไฟล์นี้ให้ดึง
- C. sauce.txt ถูกลบออกจาก working directory และ git status แสดง deleted: sauce.txt (ยังไม่ staged)
- D. sauce.txt กลายเป็นไฟล์ว่างเปล่า (0 byte)
- E. Git สลับเข้าสถานะ detached HEAD ที่ C1

===ANSWER_START===
เฉลย: C
เหตุผล: restore ทำให้ไฟล์ "ตรงกับสถานะใน source commit" — เมื่อ C1 ยังไม่มี sauce.txt การทำให้ตรงกันคือการลบไฟล์ออกจาก working directory คำสั่งจบด้วย exit code 0 ไม่ error และ status แสดง deleted (unstaged)
[verified ใน container แล้ว — exit=0, ls ไม่เหลือ sauce.txt, status: "deleted: sauce.txt" ใต้ Changes not staged]
===ANSWER_END===

# Q34
นักศึกษาแก้ไฟล์ utils.py จนพังโดยยังไม่ได้ commit อะไรเลย ไฟล์อื่น ๆ ในโปรเจกต์มีงานสำคัญที่แก้ค้างอยู่ ต้องการทิ้งเฉพาะการแก้ไขของ utils.py กลับเป็นเวอร์ชันล่าสุดที่ commit ไว้ ควรใช้คำสั่งใด?

- A. `git restore utils.py` — จำกัดผลเฉพาะไฟล์เดียว ไม่กระทบไฟล์อื่นและประวัติ commit
- B. `git reset --hard HEAD` — เพราะเร็วและแน่นอนกว่า
- C. `git revert HEAD` — เพราะปลอดภัยที่สุด
- D. `git checkout HEAD~1` — เพื่อกลับไปเวอร์ชันก่อนหน้า
- E. `git reset --soft HEAD~1` — เพื่อเก็บงานไว้ใน staging

===ANSWER_START===
เฉลย: A
เหตุผล: โจทย์ต้องการย้อน "ไฟล์เดียว" — restore ตอบโจทย์ตรงและปลอดภัยต่อไฟล์อื่น ส่วน reset --hard จะกวาดการแก้ไขค้างของทุกไฟล์ทิ้งหมด (งานสำคัญหาย), revert/reset ทำงานระดับ commit ไม่ใช่ระดับไฟล์, checkout HEAD~1 พาเข้า detached HEAD
[verified ด้วยเหตุผล (ไม่ต้องรัน) — เทียบขอบเขตผลของแต่ละคำสั่งตาม LAB02/LAB03]
===ANSWER_END===

# Q35
ข้อใดเปรียบเทียบ `git reset --soft <hash>` กับ `git reset --hard <hash>` ได้ถูกต้อง?

- A. --soft ไม่ตัด commit ออกจาก git log แต่ --hard ตัดออก
- B. --hard เก็บการแก้ไขไว้ใน staging area ส่วน --soft ทิ้งทั้งหมด
- C. --soft ย้อนเนื้อหาไฟล์ด้วย ส่วน --hard คงเนื้อหาไฟล์ไว้
- D. ทั้งคู่ตัด commit หลัง <hash> ออกจาก log เหมือนกัน แต่ --soft เก็บการแก้ไขไว้ (staged) ส่วน --hard ย้อนไฟล์กลับทั้งหมด
- E. ทั้งสองแบบให้ผลเหมือนกันทุกประการ

===ANSWER_START===
เฉลย: D
เหตุผล: ทั้งสอง mode ย้าย branch pointer ถอยเหมือนกัน (log สั้นลง) ต่างกันที่ชะตากรรมของการแก้ไข: --soft เก็บไว้เป็น "Changes to be committed" / --hard เคลียร์ทั้ง staging และไฟล์ (ตารางสรุป LAB03)
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามตารางสรุป LAB03; พฤติกรรมจริงยืนยันในข้อ 36–37]
===ANSWER_END===

# Q36
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง แล้วสร้าง 5 commits โดยแต่ละ commit เติมบรรทัด "Chapter 1" ถึง "Chapter 5" ลงไฟล์ chapters.md ทีละบรรทัด):

```
git reset --soft HEAD~2
```

หลังจากรันคำสั่งนี้ ข้อใดถูกต้อง?

- A. git log เหลือ 3 commits, chapters.md เหลือ 3 บรรทัด, working tree clean
- B. git log เหลือ 3 commits, chapters.md ยังมี 5 บรรทัดครบ และ git status แสดง Changes to be committed
- C. git log ยังมี 5 commits ครบ ไม่มีอะไรเปลี่ยน
- D. git log เหลือ 3 commits, chapters.md ยังครบ 5 บรรทัด และ working tree clean
- E. เกิด error เพราะ reset --soft ต้องระบุ commit hash เต็มเท่านั้น

===ANSWER_START===
เฉลย: B
เหตุผล: --soft ย้าย branch ถอย 2 commits (log เหลือ 3) แต่ไม่แตะทั้ง staging และไฟล์ — ส่วนต่างระหว่างเนื้อหาปัจจุบันกับ commit ปลายทางจึงค้างเป็น "Changes to be committed" พร้อม commit ใหม่ทันที
[verified ใน container แล้ว — log=3, cat 5 บรรทัด, status: Changes to be committed: modified: chapters.md]
===ANSWER_END===

# Q37
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init billing && cd billing
echo "bill 1" > bills.txt
git add . && git commit -m "C1"
echo "bill 2" >> bills.txt && git commit -am "C2"
echo "bill 3" >> bills.txt && git commit -am "C3"
echo "bill 4" >> bills.txt && git commit -am "C4"
git reset --hard HEAD~3
```

หลังจากรันคำสั่งเหล่านี้ สถานะของ repository จะเป็นอย่างไร?

- A. bills.txt ยังครบ 4 บรรทัด และ git log เหลือ 1 commit
- B. bills.txt เหลือ 1 บรรทัด แต่ git log ยังมี 4 commits ครบ
- C. bills.txt ครบ 4 บรรทัด และ git log ครบ 4 commits
- D. bills.txt เหลือ 1 บรรทัด, git log เหลือ 1 commit แต่ git status แสดง Changes to be committed
- E. bills.txt เหลือบรรทัดเดียวคือ "bill 1", git log เหลือ 1 commit และ working tree clean

===ANSWER_START===
เฉลย: E
เหตุผล: --hard ย้อนทุกอย่าง: branch ถอยไป C1, staging ถูกเคลียร์, ไฟล์ถูกเขียนทับเป็นเวอร์ชัน C1 — Git ตอบ "HEAD is now at <hash> C1" และ status เป็น clean
[verified ใน container แล้ว — cat ได้ "bill 1" บรรทัดเดียว, log=1, nothing to commit, working tree clean]
===ANSWER_END===

# Q38
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มี 3 commits ของไฟล์ scores.csv เนื้อหา score 1 ถึง score 3 ทีละบรรทัด):

```
git reset HEAD~1
```

(สังเกต: ไม่ได้ใส่ทั้ง --soft และ --hard) หลังจากรันคำสั่งนี้ ข้อใดถูกต้อง?

- A. commit ล่าสุดถูกถอนออก (log เหลือ 2) ไฟล์ยังครบ 3 บรรทัด แต่การแก้ไขอยู่ในสถานะ not staged
- B. commit ล่าสุดถูกถอนออก และการแก้ไขถูกเก็บไว้ใน staging area (Changes to be committed)
- C. ไฟล์ถูกย้อนกลับเหลือ 2 บรรทัดด้วย
- D. เกิด error เพราะ git reset ต้องระบุ --soft หรือ --hard เสมอ
- E. ไม่มีอะไรเปลี่ยนแปลง git log ยังครบ 3 commits

===ANSWER_START===
เฉลย: A
เหตุผล: default mode ของ reset คือ --mixed: ย้าย branch ถอย + เคลียร์ staging แต่คงไฟล์ไว้ — Git พิมพ์ "Unstaged changes after reset: M scores.csv" การแก้ไขจึงเป็น "Changes not staged for commit" (ต่างจาก --soft ที่ staged ให้)
[verified ใน container แล้ว — log=2, status: Changes not staged: modified: scores.csv, ไฟล์ยัง 3 บรรทัด]
===ANSWER_END===

# Q39
นักพัฒนาเผลอ commit งานลง branch `master` ทั้งที่ตั้งใจจะ commit ลง branch `feature-login` (commit นี้ยังไม่ได้ push) ต้องการถอน commit ออกจาก master โดยให้การแก้ไขทั้งหมดถูกเก็บไว้ใน staging area พร้อมนำไป commit ที่ branch ที่ถูกต้องทันที ควรใช้คำสั่งใด?

- A. `git revert HEAD`
- B. `git reset --hard HEAD~1`
- C. `git reset --soft HEAD~1`
- D. `git restore --staged .`
- E. `git checkout HEAD~1`

===ANSWER_START===
เฉลย: C
เหตุผล: สไลด์ระบุ use case นี้ตรง ๆ — --soft ถอน commit ออกจาก branch โดยงานทั้งหมดค้างอยู่ใน staging พร้อม switch ไป commit ใหม่ที่ branch ถูกต้องได้ทันที ส่วน --hard ทำงานหาย, revert เพิ่ม commit ใหม่ใน master (ไม่ได้ถอน), restore --staged แค่ unstage ไม่แตะ commit
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์ "useful if you accidentally committed to the wrong branch" + พฤติกรรม --soft ยืนยันจากข้อ 36]
===ANSWER_END===

# Q40
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init writing && cd writing
echo "para 1" > draft.md
git add . && git commit -m "C1"
echo "para 2" >> draft.md && git commit -am "C2"
echo "para 3 (uncommitted)" >> draft.md
git reset --hard HEAD
```

หลังจากรันคำสั่งเหล่านี้ ข้อใดถูกต้อง?

- A. ไม่มีอะไรเปลี่ยน เพราะ reset ไปที่ HEAD คือตำแหน่งเดิมอยู่แล้ว
- B. commit C2 ถูกลบออกจากประวัติด้วย
- C. บรรทัด para 3 ยังอยู่ เพราะ reset ไม่แตะ working directory
- D. บรรทัด para 3 หายไป ไฟล์กลับเป็น 2 บรรทัด และ git log ยังมี 2 commits ครบ
- E. เกิด error เพราะ reset --hard ต้องระบุ commit hash

===ANSWER_START===
เฉลย: D
เหตุผล: reset --hard HEAD ไม่ย้าย branch (ชี้ที่เดิม) แต่ผลของ --hard คือบังคับให้ staging และ working directory ตรงกับ HEAD — การแก้ไขที่ยังไม่ commit จึงถูกกวาดทิ้ง (เทคนิคล้าง working tree ยอดนิยม) โดยประวัติไม่เปลี่ยน
[verified ใน container แล้ว — cat เหลือ para 1/para 2, log=2, working tree clean]
===ANSWER_END===

# Q41
เหตุใดการใช้ `git reset` กับ commit ที่ **push ขึ้น remote repository ไปแล้ว** จึงถือว่าอันตราย?

- A. เพราะ reset จะลบไฟล์ทั้งหมดบน remote ทันที
- B. เพราะ reset ทำให้ local repository เสียหายจนใช้งานไม่ได้
- C. เพราะ Git ห้ามใช้ reset กับ commit ที่ push แล้ว (คำสั่งจะ error)
- D. เพราะ reset ใช้เวลานานมากกับ commit บน remote
- E. เพราะเป็นการ rewrite history — เพื่อนที่ pull ไปแล้วจะมีประวัติไม่ตรงกัน และการ push ต้องใช้ --force ซึ่งเสี่ยงลบงานคนอื่น

===ANSWER_START===
เฉลย: E
เหตุผล: ตามสไลด์ Week 4 — reset ย้าย branch pointer ถอยหลังทำให้ประวัติถูกเขียนใหม่ ผู้ร่วมทีมที่มีประวัติเดิมจะ diverge และต้อง push --force ซึ่งเสี่ยงทับ/ลบงานคนอื่น หลักคิดคือ "reset ใช้ได้เฉพาะ commit ที่ยังไม่เคย push"
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์ "ทำไม reset ถึงอันตราย: เสีย shared history"]
===ANSWER_END===

# Q42
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มี 5 commits C1–C5 ของไฟล์ todo.txt เนื้อหา task 1 ถึง task 5 ทีละบรรทัด):

```
git reset --soft HEAD~3
git commit -m "combine work"
git log --oneline
```

หลังจากรันครบทุกคำสั่ง git log --oneline จะแสดงกี่ commit และไฟล์ todo.txt มีกี่บรรทัด?

- A. 5 commits / 5 บรรทัด
- B. 3 commits (C1, C2, combine work) / 5 บรรทัด
- C. 1 commit / 1 บรรทัด
- D. 4 commits / 3 บรรทัด
- E. เกิด error เพราะไม่มีอะไรให้ commit หลัง reset

===ANSWER_START===
เฉลย: B
เหตุผล: นี่คือเทคนิค "squash ด้วยมือ" ตาม use case ในสไลด์/LAB03 — --soft ถอย 3 commits โดยงานทั้งหมดค้างใน staging แล้ว commit เดียวรวบยอด ประวัติจึงเหลือ C1, C2 และ combine work ส่วนเนื้อหาไฟล์ครบ 5 บรรทัดเท่าเดิม
[verified ใน container แล้ว — log: combine work / C2 / C1, ไฟล์ 5 บรรทัด]
===ANSWER_END===

# Q43
ต้องการยกเลิก commit ล่าสุด (ยังไม่ push) โดยเก็บการแก้ไขทั้งหมดไว้ใน staging area คำสั่งใดถูกต้อง?

- A. `git reset --soft HEAD~1`
- B. `git reset --keep-staged HEAD~1`
- C. `git undo commit`
- D. `git commit --rollback`
- E. `git reset --stage HEAD~1`

===ANSWER_START===
เฉลย: A
เหตุผล: --soft คือ mode เดียวที่ถอน commit แล้วการแก้ไขค้างอยู่ใน staging — ตัวเลือกอื่นทั้งหมดเป็นคำสั่ง/option ที่ไม่มีอยู่จริง
[verified ใน container แล้ว — B: error: unknown option 'keep-staged', C: git: 'undo' is not a git command, D: error: unknown option 'rollback', E: error: unknown option 'stage']
===ANSWER_END===

# Q44
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มีไฟล์ auth.py และ db.py ถูก commit แล้ว):

```
echo "token check" >> auth.py
echo "pool size" >> db.py
git add auth.py db.py
git reset
```

คำสั่ง `git reset` (ไม่ระบุอะไรเลย) ให้ผลอย่างไร?

- A. ไฟล์ทั้งสองถูกย้อนเนื้อหากลับเป็นเวอร์ชัน HEAD
- B. เกิด error เพราะไม่ได้ระบุ commit hash
- C. ไฟล์ทั้งสองถูก unstage (กลายเป็น Changes not staged) โดยเนื้อหาที่แก้ยังอยู่ครบ และไม่มี commit ถูกลบ
- D. เฉพาะไฟล์แรก (auth.py) ถูก unstage
- E. commit ล่าสุดถูกถอนออกจากประวัติ

===ANSWER_START===
เฉลย: C
เหตุผล: git reset เฉย ๆ = git reset --mixed HEAD คือรีเซ็ต staging ให้เท่ากับ HEAD โดยไม่ย้าย branch (ไม่มี commit หาย) และไม่แตะ working directory — ใช้เป็นคำสั่ง "unstage ทุกไฟล์" ได้
[verified ใน container แล้ว — output: "Unstaged changes after reset: M auth.py M db.py", status: ทั้งคู่ modified not staged]
===ANSWER_END===

# Q45
สไลด์ Week 4 สรุปหลักคิดว่า "git reset = แกล้งทำเป็นว่าไม่เคยเกิดขึ้น" (pretend it never happened) — จากหลักคิดนี้ git reset ควรใช้เมื่อใด?

- A. ใช้ได้ทุกกรณีถ้าผู้ใช้มีสิทธิ์ admin บน repository
- B. ใช้กับ commit ที่ push แล้วได้ ถ้ารัน git pull ตามทันที
- C. ห้ามใช้ในทุกกรณี เพราะมี git revert ที่ดีกว่าเสมอ
- D. ใช้ได้เฉพาะกับ merge commit เท่านั้น
- E. ใช้กับ commit ที่ยังไม่เคย push ออกไปให้ผู้อื่นเห็นเท่านั้น

===ANSWER_START===
เฉลย: E
เหตุผล: ตราบใดที่ commit ยังอยู่แค่ในเครื่องเรา การเขียนประวัติใหม่ไม่กระทบใคร — ทันทีที่ push แล้วมีคนอื่น pull ไป ประวัติกลายเป็นของร่วม การ reset จะสร้างปัญหา diverge/force push ทันที
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์หลักคิด git reset]
===ANSWER_END===

# Q46
repo หนึ่งมี 5 commits (C1–C5) อยู่บน branch master เพียง branch เดียว หลังจากรัน:

```
git reset --hard HEAD~2
git log --oneline --all
```

git log --oneline --all จะแสดงกี่ commit?

- A. 5 commits เหมือนเดิม เพราะ --all แสดงทุก commit ใน repository เสมอ
- B. 2 commits
- C. 5 commits โดย C4, C5 มีเครื่องหมาย dangling กำกับ
- D. 3 commits — C4, C5 ไม่ปรากฏแม้ใช้ --all เพราะไม่มี reference ใดชี้ถึงอีกแล้ว
- E. เกิด error เพราะใช้ --all หลัง reset ไม่ได้

===ANSWER_START===
เฉลย: D
เหตุผล: จุดต่างสำคัญจาก detached HEAD (ข้อ 7): checkout ไม่ย้าย branch ดังนั้น --all ยังเห็น commit ข้างหน้า แต่ reset ย้าย branch pointer ถอยลงมา C4/C5 จึงไม่มี reference ชี้ → --all มองไม่เห็น (เข้าถึงได้ทาง reflog เท่านั้น ซึ่ง log --all ไม่แสดง)
[verified ใน container แล้ว — log=3 และ log --all=3]
===ANSWER_END===

# Q47
ข้อใดเปรียบเทียบ `git checkout <hash>` กับ `git reset --hard <hash>` ได้ถูกต้อง? (ทั้งคู่ชี้ไปยัง commit เก่าเดียวกัน)

- A. checkout ย้ายเฉพาะ HEAD (detached) โดย branch ยังชี้ commit ล่าสุด ส่วน reset --hard ย้าย branch pointer ถอยไปด้วย ทำให้ commit ข้างหน้าหลุดจากประวัติ
- B. ทั้งสองคำสั่งให้ผลเหมือนกันทุกประการ
- C. checkout ย้าย branch pointer ส่วน reset ย้ายเฉพาะ HEAD
- D. reset --hard ไม่เปลี่ยนเนื้อหาไฟล์ ส่วน checkout เปลี่ยน
- E. checkout ลบ commit ที่ใหม่กว่าทิ้งถาวร

===ANSWER_START===
เฉลย: A
เหตุผล: นี่คือหัวใจของ Week 4 — checkout = "ไปดู" (ย้อนกลับได้เสมอเพราะ branch ยังอยู่) / reset --hard = "ถอย branch จริง" (ประวัติสั้นลง) แม้ทั้งคู่จะทำให้ไฟล์ใน working directory เปลี่ยนเหมือนกัน
[verified ด้วยเหตุผล (ไม่ต้องรัน) — สอดคล้องผลรันจริงข้อ 7 (checkout: --all เห็น 5) กับข้อ 46 (reset: --all เห็น 3)]
===ANSWER_END===

# Q48
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก repo ที่มี 3 commits ของไฟล์ app.css เนื้อหา rule 1 ถึง rule 3 ทีละบรรทัด):

```
git reset --soft HEAD~1
git restore --staged app.css
git status
```

หลังจากรันครบทุกคำสั่ง สถานะสุดท้ายจะเป็นอย่างไร?

- A. app.css ถูกย้อนเหลือ 2 บรรทัด และ working tree clean
- B. git log เหลือ 2 commits, app.css ยังมี 3 บรรทัด และการแก้ไขอยู่ในสถานะ Changes not staged for commit
- C. การแก้ไขยังอยู่ใน staging area (Changes to be committed) ตามเดิม
- D. git log กลับมาเป็น 3 commits เพราะ restore --staged ยกเลิกการ reset
- E. เกิด error เพราะใช้ restore --staged หลัง reset --soft ไม่ได้

===ANSWER_START===
เฉลย: B
เหตุผล: reset --soft ถอน commit ล่าสุด (log=2) เก็บส่วนต่างไว้ staged จากนั้น restore --staged ก็ unstage ส่วนต่างนั้นลงมาเป็น not staged — เนื้อหาไฟล์ไม่ถูกแตะทั้งสองคำสั่ง ผลรวมเทียบเท่า git reset --mixed HEAD~1
[verified ใน container แล้ว — log=2, ไฟล์ 3 บรรทัด, status: Changes not staged: modified: app.css]
===ANSWER_END===

# Q49
นักพัฒนาทดลองไอเดียใหม่ไป 2 commits ล่าสุดบนเครื่องตัวเอง (ยังไม่ push) แล้วพบว่าแนวทางผิดทั้งหมด ไม่ต้องการทั้ง commit และเนื้อหาการแก้ไขใด ๆ เลย ควรใช้คำสั่งใด?

- A. `git reset --soft HEAD~2`
- B. `git revert HEAD~2`
- C. `git reset --hard HEAD~2`
- D. `git restore --source=HEAD~2 .`
- E. `git checkout HEAD~2`

===ANSWER_START===
เฉลย: C
เหตุผล: ต้องการล้างทั้ง commit และไฟล์ = นิยามของ --hard พอดี (ยังไม่ push จึงปลอดภัย) — --soft เหลืองานค้าง staged, revert สร้าง commit ใหม่โดยประวัติเดิมยังอยู่, restore แก้แค่ไฟล์ไม่ถอน commit, checkout ได้ detached HEAD เฉย ๆ
[verified ด้วยเหตุผล (ไม่ต้องรัน) — พฤติกรรม --hard ยืนยันจากการรันข้อ 37 แล้ว]
===ANSWER_END===

# Q50
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init assets && cd assets
echo "logo" > logo.svg
git add . && git commit -m "C1 add logo"
echo "icon" > icon.svg
git add . && git commit -m "C2 add icon"
echo "font" > font.css
git add . && git commit -m "C3 add font"
git reset --soft HEAD~2
git status
```

git status จะแสดงผลอย่างไร?

- A. icon.svg และ font.css กลายเป็น Untracked files
- B. icon.svg และ font.css ถูกลบออกจาก working directory
- C. เฉพาะ font.css อยู่ใน Changes to be committed
- D. nothing to commit, working tree clean
- E. icon.svg และ font.css แสดงเป็น new file ใต้ Changes to be committed

===ANSWER_START===
เฉลย: E
เหตุผล: หลัง --soft branch ถอยไป C1 (ซึ่งมีแค่ logo.svg) แต่ staging ยังเก็บสถานะของ C3 ไว้ — ไฟล์สองตัวที่เกิดใน C2/C3 จึงปรากฏเป็น "new file" ที่ staged พร้อม commit ใหม่ (ไม่ใช่ untracked เพราะยังอยู่ใน index)
[verified ใน container แล้ว — status: Changes to be committed: new file: font.css / new file: icon.svg]
===ANSWER_END===

# Q51
เมื่อรัน `git reset <hash>` โดยไม่ระบุ option ใด ๆ เลย Git จะใช้ mode ใดและมีผลอย่างไร?

- A. ใช้ --soft: การแก้ไขทั้งหมดถูกเก็บไว้ใน staging area
- B. ใช้ --hard: ทุกอย่างถูกย้อนกลับรวมทั้งไฟล์
- C. เกิด error เพราะต้องระบุ mode เสมอ
- D. ใช้ --mixed (default): ตัด commit ออกจาก log และเคลียร์ staging แต่เนื้อหาไฟล์ไม่เปลี่ยน (การแก้ไขกลายเป็น not staged)
- E. แค่ย้าย HEAD ไปแบบ detached โดยไม่แตะ branch

===ANSWER_START===
เฉลย: D
เหตุผล: default ของ reset คือ --mixed ตรงตามสไลด์ ("git reset ####### — Removes commits in front of the specific hash called, files unchanged") — ไฟล์ไม่เปลี่ยนแต่การแก้ไขไม่ถูก staged ให้ (จุดต่างจาก --soft)
[verified ด้วยเหตุผล (ไม่ต้องรัน) — พฤติกรรม mixed ยืนยันจากการรันข้อ 38 และ 44 แล้ว]
===ANSWER_END===

# Q52
ต้องการลบ commit ล่าสุดทิ้งทั้ง commit และเนื้อหาการแก้ไขทั้งหมด (งานทดลองที่ยังไม่ push) คำสั่งใดถูกต้อง?

- A. `git reset --hard HEAD~1`
- B. `git delete HEAD`
- C. `git reset --force HEAD~1`
- D. `git remove-commit HEAD`
- E. `git revert --hard HEAD`

===ANSWER_START===
เฉลย: A
เหตุผล: reset --hard HEAD~1 ถอย branch 1 commit พร้อมล้างไฟล์และ staging — ตัวเลือกอื่นเป็นคำสั่ง/option ที่ไม่มีอยู่จริงทั้งหมด (revert ไม่มี --hard)
[verified ใน container แล้ว — B: git: 'delete' is not a git command, C: error: unknown option 'force', D: git: 'remove-commit' is not a git command, E: usage error; A: log เหลือ 1 จริง]
===ANSWER_END===

# Q53
คำสั่ง `git revert <hash>` ทำอะไร?

- A. ลบ commit <hash> ออกจากประวัติอย่างถาวร
- B. สร้าง commit ใหม่ที่มีการเปลี่ยนแปลง "กลับด้าน" ของ commit <hash> โดยประวัติเดิมยังอยู่ครบ
- C. ย้าย HEAD ไปที่ commit <hash> ในสถานะ detached
- D. คืนไฟล์ทุกไฟล์เป็นเวอร์ชันของ commit <hash>
- E. รวม commit <hash> เข้ากับ commit ล่าสุดเป็น commit เดียว

===ANSWER_START===
เฉลย: B
เหตุผล: revert คือ "forward-moving undo" — สร้าง commit ใหม่ที่มีเนื้อหาตรงข้ามกับ commit เป้าหมาย ประวัติจึงยาวขึ้น 1 commit โดยไม่มี commit ใดถูกลบ (ต่างจาก reset โดยสิ้นเชิง)
[verified ด้วยเหตุผล (ไม่ต้องรัน) — นิยามตรงตามสไลด์และ LAB04]
===ANSWER_END===

# Q54
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init calc-app && cd calc-app
echo "print('hello')" > app.py
git add . && git commit -m "C1: add app.py"
echo "print('feature A')" >> app.py
git commit -am "C2: add feature A"
echo "print('DEBUG')" >> app.py
git commit -am "C3: add debug code"
git revert --no-edit HEAD
```

หลังจากรันคำสั่งเหล่านี้ git log --oneline และเนื้อหา app.py จะเป็นอย่างไร?

- A. log มี 2 commits และ app.py เหลือ 2 บรรทัด
- B. log มี 4 commits แต่ app.py ยังมี 3 บรรทัดครบ
- C. log มี 4 commits (มี Revert "C3: add debug code" บนสุด และ C3 เดิมยังอยู่) ส่วน app.py เหลือ 2 บรรทัด — บรรทัด DEBUG หายไป
- D. log มี 3 commits เท่าเดิม แต่ app.py เหลือ 2 บรรทัด
- E. เกิด merge conflict ต้องแก้ไขก่อน

===ANSWER_START===
เฉลย: C
เหตุผล: revert HEAD สร้าง commit ที่ 4 ชื่อ Revert "C3: add debug code" ซึ่งลบบรรทัด DEBUG ออก — commit C3 เดิมยังอยู่ในประวัติครบ (จุดขายของ revert) และไม่มี conflict เพราะไม่มี commit หลัง C3
[verified ใน container แล้ว — log 4 รายการ มี C3 และ Revert อยู่คู่กัน, cat เหลือ hello + feature A]
===ANSWER_END===

# Q55
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init payment && cd payment
echo "init gateway" > gateway.txt
git add . && git commit -m "C1 init gateway"
echo "cfg" > settings.txt
git add . && git commit -m "C2 add settings"
echo "add api v1" >> gateway.txt
git add . && git commit -m "C3 api v1"
echo "timeout=30" >> settings.txt
git add . && git commit -m "C4 update settings"
echo "add api v2" >> gateway.txt
git add . && git commit -m "C5 api v2"
git revert <hash-ของ-C3>
```

ผลของคำสั่ง revert สุดท้ายจะเป็นอย่างไร?

- A. revert สำเร็จทันที ได้ commit ใหม่ Revert "C3 api v1"
- B. เกิด error และ Git ยกเลิกการ revert ให้เองอัตโนมัติ
- C. revert สำเร็จ แต่บรรทัด api v2 ถูกลบไปด้วย
- D. เกิด CONFLICT (content) ใน gateway.txt — การ revert หยุดค้างรอให้แก้ไขก่อน (ยังไม่มี commit ใหม่เกิดขึ้น)
- E. Git ข้าม commit C3 ไปเองโดยอัตโนมัติ

===ANSWER_START===
เฉลย: D
เหตุผล: C5 เติมบรรทัด api v2 ติดกับบรรทัด api v1 ที่ revert ต้องการลบ Git จึงไม่แน่ใจว่าจะรวมอย่างไร → "CONFLICT (content): Merge conflict in gateway.txt / error: could not revert" พร้อม hint ให้แก้แล้ว git revert --continue (ตรงตามสถานการณ์ LAB04)
[verified ใน container แล้ว — output: Auto-merging gateway.txt / CONFLICT (content) / error: could not revert 11d532f... C3 api v1]
===ANSWER_END===

# Q56
จากสถานการณ์ในข้อ 55 เมื่อเปิดไฟล์ gateway.txt จะพบเนื้อหาดังนี้:

```
init gateway
<<<<<<< HEAD
add api v1
add api v2
=======
>>>>>>> parent of 11d532f (C3 api v1)
```

ส่วนที่อยู่ระหว่าง `<<<<<<< HEAD` กับ `=======` หมายถึงอะไร?

- A. เนื้อหาปัจจุบันของเรา ณ commit ล่าสุด (HEAD) ก่อนการ revert
- B. เนื้อหาที่ Git ต้องการเปลี่ยนไปเป็น (เป้าหมายของการ revert)
- C. เนื้อหาของ commit แรกสุดใน repository
- D. เนื้อหาที่ถูกลบออกจาก repository ไปแล้ว
- E. ข้อความ commit message ของ commit ที่ถูก revert

===ANSWER_START===
เฉลย: A
เหตุผล: ตามหลักการอ่านเครื่องหมาย conflict ใน LAB04 — ส่วนบน (<<<<<<< HEAD ถึง =======) คือเนื้อหาปัจจุบันของเรา ส่วนล่าง (======= ถึง >>>>>>>) คือเนื้อหาที่ Git อยากย้อนกลับไป (สถานะก่อนมี C3 — ซึ่งในที่นี้ว่างเปล่า)
[verified ใน container แล้ว — เนื้อหาไฟล์ conflict ตรงตามที่แสดงทุกบรรทัด]
===ANSWER_END===

# Q57
ระหว่างการ revert ที่ติด conflict ค้างอยู่ นักศึกษาเปลี่ยนใจไม่ต้องการ revert แล้ว ต้องการกลับสู่สถานะเดิมก่อนสั่ง revert ทั้งหมด คำสั่งใดถูกต้อง?

- A. `git revert --cancel`
- B. `git revert --undo`
- C. `git abort`
- D. `git reset --abort`
- E. `git revert --abort`

===ANSWER_START===
เฉลย: E
เหตุผล: git revert --abort ยกเลิกการ revert ที่ค้างและคืนสถานะก่อนเริ่ม (Git บอกไว้ใน hint ตอน conflict: "To abort and get back to the state before 'git revert', run 'git revert --abort'") — ตัวเลือกอื่นไม่มีอยู่จริง
[verified ใน container แล้ว — A/B: usage error (unknown option), C: git: 'abort' is not a git command, D: error: unknown option 'abort']
===ANSWER_END===

# Q58
ต่อจากสถานการณ์ข้อ 55–56 นักศึกษาแก้ไฟล์ gateway.txt ให้เหลือเนื้อหาที่ต้องการ (init gateway และ add api v2) แล้วรัน:

```
git add .
git revert --continue
```

(บันทึกและปิด editor ตามปกติ) — ผลลัพธ์สุดท้ายจะเป็นอย่างไร?

- A. commit C3 ถูกลบออก log เหลือ 5 commits
- B. เกิด commit ใหม่ Revert "C3 api v1" — log มี 6 commits โดย C3 เดิมยังอยู่ในประวัติ
- C. log ยังมี 5 commits เพราะการ revert แก้ไข commit C3 เดิมแทนที่จะสร้างใหม่
- D. เกิด commit ใหม่ 2 รายการ (หนึ่งสำหรับ conflict หนึ่งสำหรับ revert)
- E. เกิด error เพราะต้องใช้ git commit ปิดท้ายเอง

===ANSWER_START===
เฉลย: B
เหตุผล: git revert --continue ปิดจบการ revert ที่ค้าง สร้าง commit ใหม่ 1 รายการชื่อ Revert "C3 api v1" ต่อยอดประวัติ — commit เดิมทั้ง 5 รวมทั้ง C3 ยังอยู่ครบ (จุดต่างสำคัญจาก reset ตาม LAB04)
[verified ใน container แล้ว — output: [master 428f46e] Revert "C3 api v1" และ log แสดง 6 รายการโดย C3 ยังอยู่]
===ANSWER_END===

# Q59
จาก repo ที่มีประวัติ 5 commits: C1 (แก้ catalog.txt), C2 (สร้าง register.txt), C3 (แก้ catalog.txt), C4 (แก้ register.txt), C5 (แก้ catalog.txt) — การ `git revert <hash-ของ-C4>` สำเร็จทันทีโดยไม่เกิด conflict เพราะเหตุใด?

- A. เพราะ C4 เป็น commit ล่าสุดของ repository
- B. เพราะ register.txt เป็นไฟล์ขนาดเล็ก Git จึงรวมให้อัตโนมัติ
- C. เพราะ Git จดจำวิธีแก้ conflict จากการ revert ครั้งก่อนไว้แล้ว
- D. เพราะหลังจาก C4 ไม่มี commit ใดแก้ไข register.txt อีกเลย Git จึงย้อน patch ได้โดยไม่มีการเปลี่ยนแปลงทับซ้อน
- E. เพราะการ revert commit ที่ไม่ใช่ HEAD จะไม่เกิด conflict เสมอ

===ANSWER_START===
เฉลย: D
เหตุผล: conflict เกิดเมื่อ commit หลังจากนั้นแก้ไฟล์บริเวณเดียวกัน — C5 แก้เฉพาะ catalog.txt ดังนั้นการย้อนการเปลี่ยนแปลงของ register.txt จึงไม่ชนกับใคร (ตรงตาม LAB04 Task 4: "ไม่มี commit ไหนแก้ file2.txt อีกเลย Git จึงย้อนการแก้ไขได้อย่างมั่นใจ")
[verified ใน container แล้ว — revert C4 ผ่านทันที: [master] Revert "C4 register update" และ register.txt เหลือ member 1]
===ANSWER_END===

# Q60
เหตุใด `git revert` จึงเป็นตัวเลือกที่เหมาะสมสำหรับยกเลิกการเปลี่ยนแปลงบน branch ที่ **ใช้ร่วมกับผู้อื่น (push แล้ว)**?

- A. เพราะ revert ทำงานเร็วกว่า reset มาก
- B. เพราะ revert จะลบ commit ที่ผิดออกจากเครื่องของเพื่อนร่วมทีมให้อัตโนมัติ
- C. เพราะ revert ไม่เขียนประวัติทับ — เพิ่ม commit ใหม่ต่อท้าย ทีม git pull ตามปกติได้โดยไม่ต้อง push --force
- D. เพราะ revert รับประกันว่าจะไม่เกิด merge conflict
- E. เพราะ revert เข้ารหัสประวัติเดิมไม่ให้ใครแก้ไขได้อีก

===ANSWER_START===
เฉลย: C
เหตุผล: revert เดินหน้าเพิ่ม commit ใหม่ ประวัติที่ทุกคนถืออยู่ไม่ถูกแก้ — เพื่อนแค่ pull commit ใหม่ไป และตรวจสอบย้อนหลังได้ว่าใครยกเลิกอะไร (auditable) ข้อ D ผิดเพราะ revert ก็เกิด conflict ได้ตามข้อ 55
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์ข้อดีของ revert]
===ANSWER_END===

# Q61
ต้องการ revert commit hash `f3d92c1` โดย **ไม่ให้ Git เปิด editor** มายืนยัน commit message (ใช้ message อัตโนมัติเลย) คำสั่งใดถูกต้อง?

- A. `git revert --silent f3d92c1`
- B. `git revert --no-message f3d92c1`
- C. `git revert --auto f3d92c1`
- D. `git revert --skip-editor f3d92c1`
- E. `git revert --no-edit f3d92c1`

===ANSWER_START===
เฉลย: E
เหตุผล: --no-edit คือ option จริงของ revert (ปรากฏใน usage: git revert [--[no-]edit] ...) ใช้ commit message อัตโนมัติโดยไม่เปิด editor — ตัวเลือกอื่นไม่มีอยู่จริง
[verified ใน container แล้ว — A/B/C/D: usage error ทั้งหมด, E: สร้าง commit Revert สำเร็จ]
===ANSWER_END===

# Q62
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init game && cd game
printf "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\n" > physics.js
git add . && git commit -m "C1 base"
sed -i "s/line2/line2-improved/" physics.js
git commit -am "C2 improve line2"
echo "line9" >> physics.js
git commit -am "C3 add line9"
git revert --no-edit <hash-ของ-C2>
```

หลังจากรันคำสั่งเหล่านี้ ผลลัพธ์จะเป็นอย่างไร?

- A. revert สำเร็จโดยไม่มี conflict — บรรทัดที่ 2 กลับเป็น "line2" เดิม, "line9" ยังอยู่ และ log มี 4 commits
- B. revert สำเร็จ แต่ "line9" ถูกลบออกไปด้วย
- C. เกิด conflict เพราะการ revert commit กลางประวัติทำให้ชนกันเสมอ
- D. ไฟล์ทั้งไฟล์ถูกย้อนกลับเป็นเวอร์ชัน C1
- E. เกิด error เพราะ revert ใช้กับ commit ที่แก้ไขบรรทัดเดิม (ไม่ใช่เพิ่มบรรทัดใหม่) ไม่ได้

===ANSWER_START===
เฉลย: A
เหตุผล: การแก้ของ C3 (ท้ายไฟล์ บรรทัด 9) อยู่ห่างจากบริเวณที่ revert ต้องแก้ (บรรทัด 2) เกินระยะ context ของ patch — Git จึง auto-merge ได้ ผลคือย้อนเฉพาะการเปลี่ยนแปลงของ C2 โดยงานของ C3 คงอยู่ครบ
[verified ใน container แล้ว — Auto-merging physics.js สำเร็จ, cat: line2 กลับปกติ + line9 ยังอยู่, log=4]
===ANSWER_END===

# Q63
commit กลางประวัติที่ **push ขึ้น shared repository ไปแล้ว** มีบั๊กร้ายแรง ต้องยกเลิกผลของ commit นั้นเพียง commit เดียว โดยงานทั้งหมดที่ commit หลังจากนั้นต้องอยู่ครบ ควรใช้คำสั่งใด เพราะเหตุใด?

- A. `git reset --hard <hash>` — เพราะย้อนกลับไปยัง commit นั้นได้ตรงจุดที่สุด
- B. `git revert <hash>` — เพราะเลือกย้อนผลเฉพาะ commit เดียวได้โดยไม่แตะ commit อื่น และไม่ rewrite ประวัติที่ push แล้ว
- C. `git restore --source=<hash> .` — เพราะดึงไฟล์ทุกไฟล์กลับเป็นเวอร์ชันนั้น
- D. `git checkout <hash>` — เพราะ HEAD จะย้ายไปที่ commit นั้นทันที
- E. `git reset --soft <hash>` — เพราะเก็บงานไว้ใน staging ได้

===ANSWER_START===
เฉลย: B
เหตุผล: มีเงื่อนไขบังคับสองข้อ: (1) push แล้ว → ห้าม rewrite history ตัด reset ทั้งสองแบบทิ้ง (2) ยกเลิกเฉพาะ commit กลางโดยเก็บงานหลังจากนั้น → reset ทำไม่ได้เพราะถอยทั้งสาย ส่วน restore --source ย้อนไฟล์ "ทุกอย่าง" เป็นเวอร์ชันเก่า (งานหลังจากนั้นหายจากไฟล์) — revert ตอบทั้งสองเงื่อนไข (ตารางสรุป LAB04: "ย้อนได้เฉพาะ commit ที่เลือก ✅")
[verified ด้วยเหตุผล (ไม่ต้องรัน) — คุณสมบัติ revert commit กลางยืนยันด้วยผลรันข้อ 59, 62]
===ANSWER_END===

# Q64
การ revert commit หนึ่งเกิด conflict ค้างอยู่ นักศึกษารัน:

```
git revert --skip
```

ผลลัพธ์จะเป็นอย่างไร?

- A. Git สร้าง commit ว่างเปล่า (empty commit) แทนการ revert
- B. Git ลบ commit ที่ revert ไม่สำเร็จออกจากประวัติ
- C. ไฟล์ยังค้างเครื่องหมาย conflict อยู่ ต้องลบเอง
- D. การ revert ของ commit นี้ถูกข้ามไป — ไม่มี commit ใหม่เกิดขึ้น (log เท่าเดิม), working tree กลับมา clean และเนื้อหาไฟล์เท่าก่อนสั่ง revert
- E. เกิด error เพราะ --skip ใช้ได้เฉพาะกับ git rebase

===ANSWER_START===
เฉลย: D
เหตุผล: --skip คือทางเลือกที่สามใน hint ของ Git ("You can instead skip this commit with 'git revert --skip'") — ข้ามการ revert commit ปัจจุบันทั้งหมด สถานะกลับเป็นเหมือนก่อนเริ่ม (ในกรณี revert commit เดียว ผลเหมือน --abort)
[verified ใน container แล้ว — log ยัง 3 commits, nothing to commit working tree clean, ไฟล์กลับเป็น 3 บรรทัดเดิม]
===ANSWER_END===

# Q65
เมื่อ revert สำเร็จ Git จะตั้ง commit message ของ commit ใหม่ให้อัตโนมัติในรูปแบบใด?

- A. Undo: <hash ของ commit ที่ถูก revert>
- B. Reverted changes
- C. Revert "<commit message เดิมของ commit ที่ถูก revert>"
- D. revert-<hash>
- E. ไม่มีการตั้งให้ ผู้ใช้ต้องพิมพ์ message เองเสมอ

===ANSWER_START===
เฉลย: C
เหตุผล: รูปแบบมาตรฐานคือ Revert "..." ครอบ message เดิม เช่น Revert "Update file1" ใน LAB04 — ทำให้ตรวจสอบย้อนหลังได้ทันทีว่า commit นี้ยกเลิกอะไร
[verified ด้วยเหตุผล (ไม่ต้องรัน) — เห็นจากผลรันจริงหลายข้อ เช่น ข้อ 54: Revert "C3: add debug code"]
===ANSWER_END===

# Q66
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init logs && cd logs
echo "core" > main.txt
git add . && git commit -m "C1 main"
echo "tmp data" > temp.log
git add . && git commit -m "C2 add temp.log"
echo "core v2" >> main.txt
git add . && git commit -m "C3 main update"
git revert --no-edit <hash-ของ-C2>
```

C2 เป็น commit ที่ "เพิ่มไฟล์ใหม่" temp.log — หลังจาก revert C2 ผลลัพธ์จะเป็นอย่างไร?

- A. temp.log ยังอยู่ เพราะ revert ย้อนได้เฉพาะการแก้ไขเนื้อหา ไม่ใช่การเพิ่มไฟล์
- B. temp.log กลายเป็นไฟล์ untracked
- C. เกิด error เพราะ revert ลบไฟล์ไม่ได้
- D. main.txt ถูกย้อนกลับเป็นเวอร์ชัน C1 ด้วย
- E. temp.log ถูกลบออกจาก working directory และเกิด commit ใหม่ Revert "C2 add temp.log" (log มี 4 commits)

===ANSWER_START===
เฉลย: E
เหตุผล: การกลับด้านของ "เพิ่มไฟล์" คือ "ลบไฟล์" — revert จึงสร้าง commit ที่ delete temp.log (Git รายงาน delete mode 100644 temp.log) โดยไฟล์อื่นไม่ถูกแตะ และไม่มี conflict เพราะไม่มี commit หลัง C2 ยุ่งกับ temp.log
[verified ใน container แล้ว — ls เหลือ main.txt, log=4, commit ใหม่แสดง 1 deletion + delete mode temp.log]
===ANSWER_END===

# Q67
หลังจากแก้ไข conflict ในไฟล์เรียบร้อยระหว่างการ revert ที่ค้างอยู่ ขั้นตอนที่ถูกต้องเพื่อ "จบ" การ revert คือข้อใด?

- A. รัน `git revert --resolve`
- B. รัน `git revert --finish`
- C. รัน `git merge --continue`
- D. รัน `git revert <hash>` ซ้ำอีกครั้ง
- E. รัน `git add <ไฟล์ที่แก้แล้ว>` แล้วตามด้วย `git revert --continue`

===ANSWER_START===
เฉลย: E
เหตุผล: ลำดับตาม hint ของ Git และ LAB04: mark ว่าแก้เสร็จด้วย git add ก่อน แล้วจึง git revert --continue — A/B ไม่มีจริง, C ใช้กับ merge (fatal: There is no merge in progress), D จะถูกปฏิเสธเพราะมี revert ค้างอยู่
[verified ใน container แล้ว — C: fatal: There is no merge in progress (MERGE_HEAD missing), D: error: Reverting is not possible because you have unmerged files, E: จบด้วย commit Revert สำเร็จ]
===ANSWER_END===

# Q68
พิจารณาโค้ดต่อไปนี้ (เริ่มจาก directory ว่าง):

```
git init quotes && cd quotes
echo "wisdom1" > quotes.txt
git add . && git commit -m "C1 add wisdom1"
echo "wisdom2" >> quotes.txt
git commit -am "C2 add wisdom2"
git revert --no-edit HEAD
git revert --no-edit HEAD
```

(revert สองครั้งติดกัน — ครั้งที่สองคือการ revert ตัว commit revert เอง) ผลลัพธ์สุดท้ายจะเป็นอย่างไร?

- A. quotes.txt เหลือ 1 บรรทัด และ log มี 2 commits
- B. quotes.txt กลับมามี 2 บรรทัด (wisdom1, wisdom2) และ log มี 4 commits
- C. เกิด error เพราะ revert commit ที่เป็น revert อยู่แล้วไม่ได้
- D. quotes.txt มี 2 บรรทัด แต่ log เหลือ 2 commits เพราะ revert คู่หักล้างกันหายไป
- E. quotes.txt กลายเป็นไฟล์ว่างเปล่า

===ANSWER_START===
เฉลย: B
เหตุผล: revert ครั้งแรกลบ wisdom2 (เหลือ 1 บรรทัด) ครั้งที่สอง revert ตัว revert → wisdom2 กลับมา ไฟล์ครบ 2 บรรทัดเหมือนก่อนเริ่ม แต่ประวัติบันทึกทุกย่างก้าวรวมเป็น 4 commits (Git 2.54 ตั้งชื่อ commit สุดท้ายว่า Reapply "C2 add wisdom2") — revert ไม่เคยลบประวัติ มีแต่เพิ่ม
[verified ใน container แล้ว — log 4 รายการ: Reapply / Revert / C2 / C1 และ cat ได้ wisdom1+wisdom2]
===ANSWER_END===

# Q69
สไลด์ Week 4 เปรียบเทียบการ undo ทั้งสองแบบกับ "การทำบัญชี" — ข้อใดจับคู่ได้ถูกต้อง?

- A. git reset = เขียนรายการปรับปรุงยอด / git revert = ฉีกหน้าบัญชีทิ้ง
- B. ทั้ง reset และ revert = ฉีกหน้าบัญชีทิ้งเหมือนกัน
- C. ทั้ง reset และ revert = เขียนรายการปรับปรุงยอดเหมือนกัน
- D. git reset = ฉีกหน้าบัญชีทิ้ง (รายการผิดหายไป ผู้ตรวจสอบไม่รู้ว่าเคยเกิดอะไร) / git revert = เขียนรายการปรับปรุงยอด (รายการเดิมอยู่ครบ ตรวจสอบย้อนหลังได้)
- E. การทำบัญชีเปรียบเทียบกับ git ไม่ได้ เพราะบัญชีแก้ไขย้อนหลังไม่ได้

===ANSWER_START===
เฉลย: D
เหตุผล: ตามสไลด์ — reset ทำให้สมุด "ดูสะอาด" แต่เสีย audit trail และถ้ามีคนถ่ายสำเนา (pull) ไปแล้วเล่มจะไม่ตรงกัน ส่วน revert เพิ่มรายการหักล้างโดยยอดสุทธิถูกต้องและตรวจสอบย้อนหลังได้ครบ
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามสไลด์หน้า "เปรียบเทียบให้เห็นภาพ: การทำบัญชี"]
===ANSWER_END===

# Q70
จากตารางสรุป 4 คำสั่งของ Week 4 (checkout / restore / reset / revert) ข้อใดกล่าวได้ **ถูกต้อง**?

- A. `git checkout <hash>` เขียนประวัติใหม่ จึงอันตรายกับ shared repository
- B. `git restore <file>` ลบ commit ล่าสุดออกจากประวัติ
- C. `git revert <hash>` เป็นคำสั่งเดียวในสี่คำสั่งนี้ที่เหมาะกับการยกเลิก commit ที่ push แล้ว เพราะเพิ่ม commit ใหม่แทนการแก้ประวัติ
- D. `git reset <hash>` ปลอดภัยกับ shared repository มากที่สุด
- E. ทั้งสี่คำสั่งล้วนเขียนประวัติใหม่ (rewrite history) ทั้งหมด

===ANSWER_START===
เฉลย: C
เหตุผล: ตารางสรุปสไลด์หน้า 55: checkout = แค่ดู ไม่เปลี่ยนประวัติ / restore = แก้ไฟล์ ไม่เปลี่ยนประวัติ / reset = เขียนประวัติใหม่ อันตราย / revert = เพิ่ม commit ไม่เขียนทับ — "ตัวเลือกเดียวที่ใช้ได้กับ commit ที่ push แล้ว"
[verified ด้วยเหตุผล (ไม่ต้องรัน) — ตรงตามตารางสรุปสไลด์หน้า 55]
===ANSWER_END===

