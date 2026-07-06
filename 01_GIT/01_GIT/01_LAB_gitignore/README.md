# LAB 00 — The Noise & The Secret: จัดระเบียบ Git ด้วย `.gitignore`

> อ้างอิงเนื้อหา Week 1 · Day 1 — Ignoring Files / `.gitignore` · `01_GIT.pdf` สไลด์หน้า 43–44
> ใช้เฉพาะสิ่งที่เรียนแล้ว: **สร้างไฟล์ + `.gitignore` + `git status`** เท่านั้น (ยังไม่แตะ `git add` / `git commit`)

## 📖 Story / Pain Point

**มายด์** ตั้งค่า Git เสร็จจากบท Configure Git แล้ว วันนี้เริ่มโปรเจกต์ AI ตัวแรก `secret-ai-project` เขียนโค้ดจริงแค่ 4 ไฟล์ (`train.py`, `model.py`, `requirements.txt`, `README.md`)

พอสร้าง virtual environment แล้วลองรันโปรแกรม Git ก็เริ่มเห็น "ผลพลอยได้" เต็มไปหมด — โฟลเดอร์ `venv/`, ไฟล์ cache `__pycache__/`, ไฟล์ log, ไฟล์ขยะของ macOS (`.DS_Store`) มายด์ลองสั่ง `git status` ดู:

```
$ git status
...
	.DS_Store
	.env          ← 🔑 ไฟล์นี้มี OpenAI API key อยู่ข้างใน!
	README.md
	__pycache__/
	debug.log
	model.py
	...
	venv/
```

เจอ **2 ปัญหาพร้อมกัน**:

1. **รก (Noise):** โค้ดจริง 4 ไฟล์ จมอยู่ในรายการยาวเหยียด 10 บรรทัด — มองแทบไม่เห็นว่าอะไรคือของที่ต้องดูแลจริง ๆ
2. **อันตราย (Secret):** ไฟล์ `.env` ที่เก็บ **API key + รหัสผ่าน** โผล่อยู่ในรายการ "รอ commit" — ถ้าเผลอเอาขึ้น GitHub เมื่อไร key รั่วทันที รุ่นพี่เตือนว่า *"key หลุดครั้งเดียว โดนคนอื่นเอาไปใช้ฟรี ค่าใช้จ่ายบานปลายเป็นหมื่น"*

> ปัญหาทั้งสองมาจากเรื่องเดียวกัน: **Git พยายามติดตามทุกไฟล์ในโฟลเดอร์** — ทั้งของที่เราต้องการและไม่ต้องการ เราต้องมีวิธี "บอก Git ว่าไฟล์ไหนให้มองข้าม" ตั้งแต่ต้น

LAB นี้จะพาไปสร้างสถานการณ์รก ๆ อันตราย ๆ แบบนี้ด้วยตัวเอง แล้วใช้ไฟล์ `.gitignore` กรองมันออกจากสายตา Git ให้ `git status` กลับมาสะอาดและปลอดภัย

## 🎯 สิ่งที่จะได้เรียนรู้

- เข้าใจว่าทำไม `git status` ถึงรก และไฟล์ประเภทไหนที่**ไม่ควรให้ Git ติดตาม** (จากสไลด์หน้า 43)
- เขียนไฟล์ `.gitignore` ด้วย **3 pattern หลัก**: ชื่อไฟล์ตรงตัว, `โฟลเดอร์/`, `*.นามสกุล` (จากสไลด์หน้า 44)
- กัน **ความลับ** (`.env`, API key) ไม่ให้หลุดเข้า Git ตั้งแต่แรก
- พิสูจน์ว่าไฟล์ถูก **"ซ่อน" ไม่ใช่ "หาย"** ด้วย `git status --ignored` (ไฟล์ยังอยู่ครบ ไม่ได้ถูกลบ)

## 📚 ทฤษฎีก่อนลงมือ

### 1) `.gitignore` คืออะไร และแก้ปัญหาอะไร

`.gitignore` คือ **ไฟล์ข้อความธรรมดา** ที่เราวางไว้ที่ root ของ repo ข้างในเขียน "pattern" บอก Git ว่า **ไฟล์/โฟลเดอร์ไหนให้มองข้าม** — Git จะไม่ติดตาม ไม่ขึ้นใน `git status` และไม่มีวันถูก commit โดยบังเอิญ

สไลด์หน้า 43 ระบุ 4 ประเภทไฟล์ที่ *"you know you NEVER want to commit"*:

| | ประเภทไฟล์ | ตัวอย่าง | ทำไมไม่ควร commit |
|---|---|---|---|
| 🔑 | **Secrets / API keys / credentials** | `.env`, `secrets.json` | หลุดขึ้น GitHub = โดนขโมยไปใช้ เสียเงิน/เสียข้อมูล |
| 💻 | **Operating System files** | `.DS_Store` (macOS) | ไฟล์ขยะเฉพาะเครื่อง ไม่เกี่ยวกับโปรเจกต์ |
| 📄 | **Log files** | `*.log` | ไฟล์บันทึกที่งอกใหม่เรื่อย ๆ ทุกครั้งที่รัน |
| 📦 | **Dependencies & packages** | `venv/`, `node_modules/`, `__pycache__/` | ไฟล์ที่ **สร้างใหม่ได้เสมอ** จาก `requirements.txt` — ไม่ต้องเก็บ (ใหญ่และเปลืองมาก) |

### 2) 3 Pattern หลัก (จากสไลด์หน้า 44)

เขียน pattern บรรทัดละหนึ่งอันในไฟล์ `.gitignore`:

| Pattern | ความหมาย | ตัวอย่างที่โดน |
|---|---|---|
| `.DS_Store` | ละเว้น**ไฟล์ที่ชื่อตรงตัว**นี้ | `.DS_Store` |
| `folderName/` | ละเว้น**ทั้งโฟลเดอร์** (มี `/` ปิดท้าย) | `venv/`, `__pycache__/` ทั้งอัน |
| `*.log` | ละเว้น**ทุกไฟล์นามสกุล** `.log` (`*` = อะไรก็ได้) | `training.log`, `debug.log` |

ไวยากรณ์เสริมที่ควรรู้ (นอกเหนือจากสไลด์):

| Pattern | ความหมาย |
|---|---|
| `# comment` | บรรทัดที่ขึ้นต้นด้วย `#` = คอมเมนต์ (Git ข้าม) · บรรทัดว่างก็ถูกข้าม |
| `!important.log` | เครื่องหมาย `!` = **ยกเว้น** (un-ignore) ดึงไฟล์กลับมา แม้โดน pattern อื่นละเว้นไว้ — *ยกเว้นไม่ได้ถ้าโฟลเดอร์แม่ถูกละเว้นทั้งอันไปแล้ว* (เช่น มี `venv/` แล้วสั่ง `!venv/keep.txt` จะไม่ได้ผล) |
| `/config.py` | `/` นำหน้า = ยึดกับ root ของ repo เท่านั้น (ไม่ใช่ทุกโฟลเดอร์ย่อย) |

### 3) จุดที่ต้องรู้ (2 กับดักยอดฮิต)

| ⚠️ | กับดัก | สิ่งที่ต้องจำ |
|---|---|---|
| 1 | ตัว `.gitignore` เองล่ะ? | `.gitignore` **ควรถูก commit เข้า repo ด้วย** — เพื่อให้ทุกคนในทีมใช้กติกาละเว้นชุดเดียวกัน (มันจะยัง "untracked" อยู่ใน LAB นี้ ซึ่งถูกต้อง — เราตั้งใจจะเก็บมันในบทถัดไป) |
| 2 | เพิ่มชื่อไฟล์ที่ **commit ไปแล้ว** ลง `.gitignore` | **ไม่ช่วย!** `.gitignore` มีผลกับไฟล์ที่ **ยังไม่ถูก track** เท่านั้น ไฟล์ที่เข้า repo ไปแล้ว Git จะติดตามต่อไป (วิธีถอนออกจะได้เรียนใน LAB `git add` / `git commit`) — **ทางที่ดีที่สุดคือใส่ `.gitignore` ให้ครบ *ก่อน* commit ครั้งแรก** |

> 🔗 ไม่อยากเขียน `.gitignore` เองทั้งหมด? มีตัวสร้างสำเร็จรูปตามภาษา/เฟรมเวิร์ก (สไลด์หน้า 44 แนะนำไว้): <https://www.toptal.com/developers/gitignore>

---

## ⚙️ เตรียมความพร้อม

รัน container สำหรับทดลอง (บนเครื่องตัวเอง):

```bash
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
```

จากนั้น SSH เข้าไป (password: `passwd`):

```bash
ssh root@localhost -p 2222
```

> 💡 LAB นี้ต่อจากบท **Configure Git** — สมมติว่าตั้งค่า Git ไว้แล้ว ถ้ายังไม่ได้ตั้ง `init.defaultBranch` ให้รันบรรทัดนี้ก่อน เพื่อให้ผลลัพธ์ตรงกับที่แสดงในเอกสาร (branch ชื่อ `main`):
> ```bash
> git config --global init.defaultBranch main
> ```
> คำสั่งทั้งหมดตั้งแต่จุดนี้ **พิมพ์ภายใน container**

---

## STEP 1 — สร้างโปรเจกต์จริง แล้วดู "ความรก" ของ `git status`

สร้างโฟลเดอร์โปรเจกต์ พร้อมทั้ง **โค้ดจริง** และ **ไฟล์ขยะ** ที่มักงอกในโปรเจกต์ AI:

```bash
mkdir -p ~/gitignore_lab/secret-ai-project && cd ~/gitignore_lab/secret-ai-project

# --- โค้ดจริง (อยากให้ Git ติดตาม) ---
echo "print('training...')"  > train.py
echo "class Model: ..."       > model.py
echo "torch==2.3.0"           > requirements.txt
echo "# Secret AI Project"    > README.md

# --- ไฟล์ที่ NEVER want to commit ---
printf 'OPENAI_API_KEY=sk-proj-DO-NOT-COMMIT-9f3a2b\nDB_PASSWORD=p@ssw0rd\n' > .env   # 🔑 ความลับ
touch .DS_Store                                                                       # 💻 ขยะ macOS
echo "epoch=1 loss=0.42" > training.log                                               # 📄 log
echo "stacktrace..."     > debug.log                                                  # 📄 log
mkdir -p venv/bin && touch venv/bin/activate venv/pyvenv.cfg                           # 📦 dependency
mkdir -p __pycache__ && touch __pycache__/model.cpython-311.pyc                        # 📦 cache
```

ดูว่ามีไฟล์อะไรบนดิสก์บ้าง (`-a` = โชว์ไฟล์ซ่อนที่ขึ้นต้นด้วย `.` ด้วย):

```bash
ls -a
```

**Expected output:**

```
.  ..  .DS_Store  .env  README.md  __pycache__  debug.log  model.py  requirements.txt  train.py  training.log  venv
```

ทำให้โฟลเดอร์นี้เป็น Git repo แล้วถาม `git status`:

```bash
git init
git status
```

**Expected output:**

```
Initialized empty Git repository in /root/gitignore_lab/secret-ai-project/.git/
```
```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.DS_Store
	.env
	README.md
	__pycache__/
	debug.log
	model.py
	requirements.txt
	train.py
	training.log
	venv/

nothing added to commit but untracked files present (use "git add" to track)
```

สังเกต 3 อย่าง:

1. **โค้ดจริงจมหาย** — `train.py`, `model.py`, `requirements.txt`, `README.md` (4 ไฟล์ที่แคร์) ปนอยู่กับขยะรวม **10 รายการ**
2. **`.env` โผล่มา** — ไฟล์ที่มี API key รออยู่ในรายการ "รอ commit" พร้อมหลุดขึ้น GitHub
3. **Git ยุบโฟลเดอร์** — `venv/` และ `__pycache__/` ที่ยังไม่ถูก track จะแสดงแค่ชื่อโฟลเดอร์ + `/` (ยังไม่ไล่โชว์ทุกไฟล์ข้างใน)

ลองดูแบบ**ย่อ** ด้วย `-s` (short) — `??` แปลว่า "untracked (Git ยังไม่รู้จัก)":

```bash
git status -s
```

**Expected output:**

```
?? .DS_Store
?? .env
?? README.md
?? __pycache__/
?? debug.log
?? model.py
?? requirements.txt
?? train.py
?? training.log
?? venv/
```

> 💥 นี่คือ pain point: ทั้ง **รก** และ **อันตราย** — ถ้าเผลอ `git add .` ตอนนี้ ทุกอย่างรวมทั้ง `.env` จะถูกเตรียม commit หมด

## STEP 2 — สร้าง `.gitignore` แล้ว `git status` สะอาดขึ้นทันที

สร้างไฟล์ `.gitignore` ที่ **root ของ repo** ใส่ pattern ครอบขยะทั้ง 4 ประเภท (heredoc ด้านล่างเขียนไฟล์ให้ในทีเดียว):

```bash
cat > .gitignore <<'EOF'
# Secrets & credentials
.env

# OS files
.DS_Store

# Log files
*.log

# Dependencies & packages
venv/
__pycache__/
EOF
```

ตรวจว่าเขียนถูก:

```bash
cat .gitignore
```

**Expected output:**

```
# Secrets & credentials
.env

# OS files
.DS_Store

# Log files
*.log

# Dependencies & packages
venv/
__pycache__/
```

ทีนี้ถาม `git status` อีกครั้ง:

```bash
git status
```

**Expected output:**

```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore
	README.md
	model.py
	requirements.txt
	train.py

nothing added to commit but untracked files present (use "git add" to track)
```

```bash
git status -s
```

**Expected output:**

```
?? .gitignore
?? README.md
?? model.py
?? requirements.txt
?? train.py
```

🎉 จาก **10 รายการ เหลือ 5** — ขยะทั้งหมด (`​.env`, `.DS_Store`, `*.log`, `venv/`, `__pycache__/`) **หายจากสายตา Git** แล้ว เหลือแต่โค้ดจริง 4 ไฟล์ บวกกับ `.gitignore` เอง

> 🧭 ทำไม `.gitignore` ถึงยังโผล่ในรายการ untracked? — เพราะเรา **อยากให้มันอยู่ใน repo** เพื่อนในทีมจะได้ใช้กติกาละเว้นชุดเดียวกัน (`.gitignore` ไม่ละเว้นตัวมันเอง) — มันจะถูก commit ในบทถัดไป

## STEP 3 — พิสูจน์ว่าไฟล์ถูก "ซ่อน" ไม่ใช่ "หาย" (`git status --ignored`)

`.gitignore` **ไม่ได้ลบไฟล์** — แค่บอก Git ให้มองข้าม ไฟล์ยังอยู่บนดิสก์ครบ เติม flag `--ignored` เพื่อให้ Git โชว์รายการที่มัน "จงใจซ่อน":

```bash
git status --ignored
```

**Expected output:**

```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore
	README.md
	model.py
	requirements.txt
	train.py

Ignored files:
  (use "git add -f <file>..." to include in what will be committed)
	.DS_Store
	.env
	__pycache__/
	debug.log
	training.log
	venv/

nothing added to commit but untracked files present (use "git add" to track)
```

มีหัวข้อ **`Ignored files:`** โผล่ขึ้นมา แสดงขยะทั้ง 6 รายการที่เราตั้งใจซ่อน — ยืนยันว่าไฟล์ **ยังอยู่ครบ** (ลอง `ls -a` ดูอีกทีก็ยังเห็น) Git แค่ไม่เอามันมายุ่งด้วยเท่านั้น

> ✅ ตอบคำถามยอดฮิต "ใส่ `.gitignore` แล้วไฟล์หายไหม?" — **ไม่หาย** ไฟล์อยู่บนเครื่องเหมือนเดิมทุกประการ

> ⚠️ **อย่าลืมกับดักข้อ 2:** `.gitignore` ได้ผลกับไฟล์ที่ **ยังไม่ถูก track** เท่านั้น ดังนั้นควรวาง `.gitignore` ให้ครบ **ก่อน** `git add` / `git commit` ครั้งแรกเสมอ (จะได้ลงมือ commit จริงใน LAB ถัดไป)

## ✅ Checklist ก่อนไปต่อ

- [ ] เห็นกับตาว่า `git status` ก่อนมี `.gitignore` โชว์ทั้ง 10 รายการ รวมถึง `.env` ที่มีความลับ
- [ ] สร้างไฟล์ `.gitignore` ที่ root และ `cat` ดูเนื้อหาได้ถูกต้อง
- [ ] `git status` หลังมี `.gitignore` เหลือแค่ 5 รายการ (โค้ดจริง 4 + `.gitignore`)
- [ ] อธิบายได้ว่าทำไม `.gitignore` ตัวเองถึงยังขึ้นเป็น untracked
- [ ] `git status --ignored` โชว์หัวข้อ `Ignored files:` และไฟล์ขยะยังอยู่ครบบนดิสก์

## ❓ คำถามทบทวน

1. ไฟล์ 4 ประเภทที่สไลด์บอกว่า "NEVER want to commit" มีอะไรบ้าง และทำไมไฟล์ `.env` ถึงอันตรายที่สุด?
2. Pattern 3 แบบต่อไปนี้ต่างกันอย่างไร: `secret.key` , `logs/` , `*.tmp` ?
3. หลังใส่ `.gitignore` แล้ว `git status` ก็ยังโชว์ `.gitignore` เป็น untracked อยู่ดี — เพราะอะไร และเป็นเรื่องปกติหรือไม่?
4. ใส่ไฟล์ลง `.gitignore` แล้ว "ไฟล์นั้นหายไปจากเครื่อง" จริงหรือไม่? ใช้คำสั่งใดพิสูจน์?
5. ถ้าเผลอ `commit` ไฟล์ `.env` ไปแล้ว ค่อยมาเพิ่มชื่อมันใน `.gitignore` ทีหลัง จะช่วยให้ Git เลิกติดตามไหม? เพราะกติกาข้อใด?
