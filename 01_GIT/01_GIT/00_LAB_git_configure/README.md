# LAB 00 — Who Are You?: การตั้งค่า Git (Configure) ก่อนเริ่มใช้งานจริง

> อ้างอิงเนื้อหา `git_week1.html` หัวข้อ 8 — การตั้งค่า Git (Configure) · สไลด์หน้า 46–50
> ใช้เฉพาะคำสั่งที่เรียนแล้ว: `git config` และ `git init` เท่านั้น

## 📖 Story / Pain Point

**มายด์** นักศึกษาปี 2 เพิ่งติดตั้ง Git เสร็จ กำลังจะเริ่มโปรเจกต์แรก เพื่อนถามว่า *"ตั้งค่า Git หรือยัง?"* มายด์งง — *"ต้องตั้งอะไรด้วยเหรอ? ก็ติดตั้งเสร็จแล้วนี่"*

ลองถาม Git ดูว่ารู้จักเราไหม:

```
$ git config user.name
$                        ← เงียบ... ไม่ตอบอะไรเลย
```

> Git ยัง**ไม่รู้เลยว่าเราเป็นใคร** — และทุกงานที่ Git บันทึก จะต้องแนบ**ชื่อ + อีเมลของผู้เขียน**ติดไปด้วยเสมอ ถ้าไม่ตั้งค่า เมื่อถึงตอนบันทึกงานจริง Git จะหยุดทำงานพร้อมข้อความ `Please tell me who you are`

เพื่อนอีกคนเจอหนักกว่า — ไปใช้**เครื่องในห้อง Lab** ที่รุ่นพี่ปีที่แล้วเคยตั้งค่าไว้ ทุกงานที่บันทึกบนเครื่องนั้นจะ**ขึ้นชื่อของรุ่นพี่** แทนชื่อตัวเอง ผลงานทั้งเทอมไม่นับเป็น contribution (ช่องเขียว) ใน GitHub ของตัวเองเลย

ปัญหาทั้งสองแบบมาจากเรื่องเดียวกัน: **Git ต้องรู้ตัวตนของผู้ใช้ก่อนเริ่มงาน** — ไม่ตั้งก็ทำงานต่อไม่ได้ ตั้งผิด (หรือค้างของคนอื่น) งานก็กลายเป็นของคนอื่น

LAB นี้จะพาไปสำรวจ "เครื่องที่ Git ยังไม่รู้จักใคร" ด้วยตัวเอง แล้วตั้งค่าอย่างถูกวิธี พร้อมเข้าใจระบบ config 3 ระดับของ Git

## 🎯 สิ่งที่จะได้เรียนรู้

- วิธีเช็คว่าเครื่องนี้ Git รู้จักเราหรือยัง (`git config user.name` + exit code, ไฟล์ `~/.gitconfig`)
- ตั้งค่าด้วย `git config --global` และค่าเสริมที่ควรตั้ง (`init.defaultBranch`, `color.ui`)
- ตรวจสอบค่าด้วย `git config --list`, ดูทีละค่า และ `--show-origin` (ดูว่าค่ามาจากไฟล์ไหน)
- ระบบ config 3 ระดับ (system / global / local) และกติกา **local ชนะ global**
- แก้ปัญหาเครื่อง Lab ค้าง account เก่า ด้วย `--unset`

## 📚 ทฤษฎีก่อนลงมือ

### 1) Git ต้องรู้ว่า "ใคร" เป็นคนทำงาน

หน้าที่หลักของ Git คือบันทึกประวัติว่า**ใคร แก้อะไร เมื่อไหร่** — ดังนั้นทุกครั้งที่ Git บันทึกงาน จะแนบ `user.name` และ `user.email` ของผู้เขียนติดไป**ถาวร** ถ้ายังไม่ตั้งค่า เมื่อถึงขั้นตอนบันทึกงาน (จะได้เรียนใน LAB ถัดไป) Git จะหยุดพร้อม error:

```
*** Please tell me who you are.
```

ประโยชน์ของการตั้งให้ถูก:

| | |
|---|---|
| 🪪 ระบุตัวตนผู้เขียน | ตามได้ว่าใครแก้อะไร เมื่อไหร่ ในทีม |
| 🔗 เชื่อมกับ GitHub | ถ้าอีเมลตรงกับที่ผูกไว้ใน GitHub account — งานที่บันทึกจะโชว์รูปโปรไฟล์และ**นับเป็น contribution (ช่องเขียว)** ของเรา |
| 1️⃣ ตั้งครั้งเดียวพอ | ค่าแบบ `--global` ใช้ได้กับทุก repo บนเครื่อง |

### 2) Config มี 3 ระดับ — ระดับที่แคบกว่าชนะเสมอ

Git อ่านค่า config จาก 3 ระดับ ทับกันตามลำดับ **local > global > system**

| ระดับ | Flag | ขอบเขต | เก็บที่ไฟล์ |
|---|---|---|---|
| **System** | `--system` | ทุก user ทุก repo บนเครื่อง (แทบไม่ได้ใช้) | `/etc/gitconfig` |
| **Global** ⭐ | `--global` | ทุก repo ของ user คนนี้ — **ใช้ระดับนี้เป็นหลัก** | `~/.gitconfig` |
| **Local** | `--local` (ค่า default) | เฉพาะ repo นั้น ๆ — ใช้เมื่ออยากให้บางโปรเจกต์ใช้ตัวตนอื่น | `.git/config` ใน repo |

> ตัวอย่างการใช้จริง: ตั้ง global เป็น account ส่วนตัว แต่ repo งานบริษัทตั้ง local ทับเป็น account บริษัท — งานใน repo นั้นจะใช้ตัวตนบริษัทโดยอัตโนมัติ

### 3) ค่าเสริมที่ควรตั้ง (Optional แต่แนะนำ)

| คำสั่ง | ทำอะไร |
|---|---|
| `git config --global init.defaultBranch main` | ให้ branch แรกชื่อ `main` (แทน `master`) ตรงมาตรฐาน GitHub — และปิด hint ยาว ๆ ตอน `git init` |
| `git config --global color.ui auto` | เปิดสีในผลลัพธ์คำสั่ง Git อ่านง่ายขึ้น |
| `git config --global core.editor "code --wait"` | ใช้ VS Code เป็น editor เวลา Git ให้พิมพ์ข้อความ (บน container ที่ไม่มี VS Code ข้ามได้) |
| `git config --global credential.helper store` | จำรหัส/token ไว้ ไม่ต้องกรอกซ้ำ ⚠️ เก็บเป็น**ข้อความธรรมดา**ใน `~/.git-credentials` — ห้ามใช้บนเครื่องสาธารณะ |

### 4) คำสั่งตรวจสอบ — เครื่องมือสืบสวนเวลา config เพี้ยน

```
git config --list                 # ดูทุกค่า (ย่อ: git config -l)
git config user.name              # ดูทีละค่า
git config --list --show-origin   # ดูว่าแต่ละค่ามาจาก "ไฟล์ไหน" — ตัวชี้ขาดเวลา local ทับ global
```

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

> คำสั่งทั้งหมดตั้งแต่จุดนี้ **พิมพ์ภายใน container** (หลัง SSH เข้าไปแล้ว) — container เปล่านี้**ยังไม่เคยตั้งค่า Git เลย** เหมือนเครื่องใหม่ของมายด์พอดี

---

## STEP 1 — สำรวจเครื่องใหม่: Git รู้จักเราหรือยัง?

ถาม Git ว่ารู้จักเราไหม (จำลองสถานการณ์ของมายด์):

```bash
git config --list
echo "exit code: $?"
git config user.name
echo "exit code: $?"
```

**Expected output:**

```
exit code: 0
exit code: 1
```

- `git config --list` **ไม่พิมพ์อะไรเลย** — เครื่องนี้ไม่มี config สักค่า
- `git config user.name` เงียบเหมือนกัน แต่ **exit code เป็น 1** — ภาษาของ Git แปลว่า *"ค่านี้ยังไม่ถูกตั้ง"*

แล้วไฟล์เก็บ config ระดับ global ล่ะ มีไหม?

```bash
cat ~/.gitconfig
```

**Expected output:**

```
cat: /root/.gitconfig: No such file or directory
```

ไม่มีแม้แต่ไฟล์! ทีนี้ลองสร้าง repo แรกดู จะเจอ pain point เพิ่มอีกข้อ:

```bash
mkdir -p ~/config_lab/first-try && cd ~/config_lab/first-try
git init
```

**Expected output:**

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
Initialized empty Git repository in /root/config_lab/first-try/.git/
```

สรุป pain point ที่เจอบนเครื่องที่ยังไม่ตั้งค่า:

1. Git **ไม่รู้ว่าเราเป็นใคร** — พองานถูกบันทึกจริงจะติด error `Please tell me who you are` ทันที
2. `git init` **บ่น hint ยาวเหยียด**ทุกครั้ง — บรรทัดแรกของ hint บอกเองว่ากำลังใช้ชื่อ branch `master` ซึ่งไม่ตรงกับมาตรฐาน GitHub ที่ใช้ `main`

> 💡 สังเกตว่าตัว hint เองก็บอกทางแก้ให้แล้ว: `git config --global init.defaultBranch <name>` — คำสั่งตระกูลเดียวกับที่เรากำลังจะใช้

## STEP 2 — ตั้งตัวตน + ค่าเสริม (ทางแก้ที่ถูกต้อง)

ตั้งชื่อและอีเมล **ให้ตรงกับ GitHub account ของตัวเอง** (ตัวอย่างนี้ใช้ account สมมติ `somchai-dev` — **เปลี่ยนเป็นชื่อ–อีเมลของตัวเอง**):

```bash
git config --global user.name "somchai-dev"
git config --global user.email "somchai.dev@example.com"
git config --global init.defaultBranch main
git config --global color.ui auto
```

คำสั่งชุดนี้**ไม่มี output ใด ๆ ถ้าสำเร็จ** (เงียบ = ผ่าน)

> ℹ️ ใช้ username และอีเมล**เดียวกับที่สมัคร GitHub** เพื่อให้งานผูกกับ account เราอัตโนมัติ · ชื่อที่มีช่องว่างต้องครอบด้วยเครื่องหมายคำพูด เช่น `"Somchai Jaidee"`

## STEP 3 — ตรวจสอบว่าตั้งสำเร็จ

```bash
git config --list
```

**Expected output** (สองบรรทัดแรกเป็นชื่อ–อีเมลของแต่ละคน · บรรทัด `core.*` โผล่เพราะเรายืนอยู่ใน repo `first-try`):

```
user.name=somchai-dev
user.email=somchai.dev@example.com
init.defaultbranch=main
color.ui=auto
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true
```

ดูทีละค่า และดูว่าค่ามาจากไฟล์ไหน:

```bash
git config user.name
git config --list --show-origin
```

**Expected output:**

```
somchai-dev
```
```
file:/root/.gitconfig	user.name=somchai-dev
file:/root/.gitconfig	user.email=somchai.dev@example.com
file:/root/.gitconfig	init.defaultbranch=main
file:/root/.gitconfig	color.ui=auto
file:.git/config	core.repositoryformatversion=0
file:.git/config	core.filemode=true
file:.git/config	core.bare=false
file:.git/config	core.logallrefupdates=true
```

เทียบกับ STEP 1: คราวนี้ `git config user.name` **ตอบชื่อเรากลับมา** (exit code 0) และ `--show-origin` ชี้ชัดว่าค่า `--global` ทั้งหมดอยู่ในไฟล์ `/root/.gitconfig` (คือ `~/.gitconfig`) ซึ่งตอนนี้ถูกสร้างขึ้นแล้ว — เปิดดูตรง ๆ ได้เลย:

```bash
cat ~/.gitconfig
```

**Expected output:**

```
[user]
	name = somchai-dev
	email = somchai.dev@example.com
[init]
	defaultBranch = main
[color]
	ui = auto
```

> 💡 `git config --global ...` ก็คือการเขียนไฟล์นี้นั่นเอง — จะแก้ไฟล์ตรง ๆ ด้วย text editor หรือใช้ `git config --global --edit` ก็ได้ผลเหมือนกัน

## STEP 4 — ผลของ `init.defaultBranch`: hint หายไปแล้ว

สร้าง repo ใหม่อีกอัน แล้วเทียบผลกับ `git init` ครั้งแรกใน STEP 1:

```bash
cd ~/config_lab
mkdir my-project && cd my-project
git init
```

**Expected output:**

```
Initialized empty Git repository in /root/config_lab/my-project/.git/
```

**hint ยาว ๆ หายไปทั้งหมด** เหลือบรรทัดเดียวสั้น ๆ — เพราะ Git ไม่ต้องเดาชื่อ branch อีกแล้ว repo ใหม่นี้จะเริ่มที่ branch ชื่อ `main` ตามค่า `init.defaultBranch` ที่เราตั้งไว้ (จะได้เห็นชื่อ branch ชัด ๆ เมื่อเริ่มบันทึกงานจริงใน LAB ถัดไป)

> 🧭 ข้อควรรู้: `init.defaultBranch` มีผลเฉพาะ repo ที่**สร้างใหม่หลังตั้งค่า**เท่านั้น — repo เก่าอย่าง `first-try` ที่สร้างไว้ก่อนตั้งค่า ยังใช้ชื่อ `master` เหมือนเดิม ไม่ถูกเปลี่ยนย้อนหลัง (ตัว hint ใน STEP 1 ก็บอกไว้ว่าถ้าจะเปลี่ยนของเก่าต้องสั่งเปลี่ยนชื่อ branch เอง)

## STEP 5 — Local ทับ Global: ให้ repo เดียวใช้ตัวตนอื่น

สมมติ repo `my-project` เป็นงานบริษัท ต้องใช้ตัวตน `work-account` เฉพาะที่นี่ — รันคำสั่งเดิมแต่**ตัด `--global` ออก** (= ระดับ local เขียนลง `.git/config` ของ repo นี้):

```bash
git config user.name "work-account"
git config user.email "work@company-example.com"
git config --list --show-origin | grep user
```

**Expected output:**

```
file:/root/.gitconfig	user.name=somchai-dev
file:/root/.gitconfig	user.email=somchai.dev@example.com
file:.git/config	user.name=work-account
file:.git/config	user.email=work@company-example.com
```

มีค่า `user.name` **2 ตัวพร้อมกัน** จากคนละไฟล์! แล้ว Git จะใช้ตัวไหน? — ถามตรง ๆ เลย:

```bash
git config user.name
```

**Expected output:**

```
work-account
```

**Local ชนะ Global** — ใน repo นี้ Git จะใช้ตัวตน `work-account` ทั้งที่ global ยังเป็น `somchai-dev` อยู่ (repo อื่นบนเครื่องไม่กระทบ) ดูไฟล์ config ระดับ local ของ repo นี้ได้ที่:

```bash
cat .git/config
```

**Expected output:**

```
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[user]
	name = work-account
	email = work@company-example.com
```

ทดลองเสร็จแล้ว ลบค่า local ทิ้งให้ repo กลับไปใช้ global ตามเดิม:

```bash
git config --unset user.name
git config --unset user.email
git config user.name
```

**Expected output:**

```
somchai-dev
```

## STEP 6 — Troubleshooting: ล้างเครื่อง Lab ที่ค้าง account เก่า

จำลองสถานการณ์เพื่อนของมายด์ — สมมติเราเป็น "คนถัดไป" ที่มาใช้เครื่องนี้ และต้องล้างตัวตนของคนก่อนหน้าออกก่อน (`--unset` = ลบค่านั้นทิ้ง):

```bash
git config --global --unset user.name
git config --global --unset user.email
git config --list
```

**Expected output** (ค่า `user.*` หายไปแล้ว):

```
init.defaultbranch=main
color.ui=auto
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true
```

พิสูจน์ว่าตอนนี้เครื่อง "ไม่มีตัวตน" จริง — กลับไปสภาพเดียวกับ STEP 1:

```bash
git config user.name
echo "exit code: $?"
```

**Expected output:**

```
exit code: 1
```

ปิดจบ: ตั้งตัวตน**ของตัวเอง**กลับเข้าไปใหม่ (ครบวงจร ล้าง → ตั้งใหม่ เหมือนที่ต้องทำจริงในห้อง Lab):

```bash
git config --global user.name "somchai-dev"
git config --global user.email "somchai.dev@example.com"
git config user.name
```

**Expected output:**

```
somchai-dev
```

> 💡 การสลับไปใช้ GitHub **อีก account** แบบเต็มรูปแบบ ต้องเปลี่ยน 2 อย่าง: ตัวตนของผู้เขียน (`user.name` / `user.email` — ทำใน LAB นี้แล้ว) และตัวตนที่ใช้ login กับ GitHub (`git config --global credential.username "new-user"`) — ส่วนหลังผูกกับเรื่อง token จึง**ตั้งใจแยกไปฝึกใน LAB ชุด token** ของสัปดาห์นี้ · ถ้าเครื่องค้าง credential ของคนเก่า ให้ล้างด้วย `git config --global --unset credential.username`

## ✅ Checklist ก่อนไปต่อ

- [ ] เจอกับตาตัวเองว่าเครื่องเปล่า `git config user.name` เงียบ + exit code 1 และไม่มีไฟล์ `~/.gitconfig`
- [ ] `git config --list` แสดง `user.name` / `user.email` ของตัวเอง และ `init.defaultbranch=main`
- [ ] `cat ~/.gitconfig` เห็นค่า global ที่ตั้งไว้ทั้งหมด
- [ ] `git init` ครั้งที่สอง (หลังตั้งค่า) ไม่มี hint ยาว ๆ โผล่มาอีกแล้ว
- [ ] อธิบายได้ว่าใน STEP 5 ทำไม `git config user.name` ตอบ `work-account` ทั้งที่ global เป็นอีกชื่อ
- [ ] ล้าง account เก่าด้วย `--global --unset` แล้วตั้งใหม่ได้เอง

## ❓ คำถามทบทวน

1. เครื่องที่ยังไม่ตั้งค่า — `git config user.name` ให้ผลอย่างไร และ exit code เท่าไร? ค่านี้บอกอะไรเรา
2. ค่า `--global` ถูกเก็บไว้ที่ไฟล์อะไร และค่า local ของแต่ละ repo เก็บที่ไฟล์อะไร
3. ถ้า `~/.gitconfig` ตั้ง `user.name=somchai-dev` แต่ `.git/config` ของ repo ตั้ง `user.name=work-account` — ใน repo นั้น Git จะใช้ชื่อไหน เพราะกติกาข้อใด
4. คำสั่งใดใช้ดูว่า config แต่ละค่า "มาจากไฟล์ไหน" และมีประโยชน์ตอนไหน
5. ทำไม `git init` ใน STEP 4 ถึงไม่มี hint ยาว ๆ เหมือน STEP 1 อีกแล้ว? และ repo เก่าที่สร้างไว้**ก่อน**ตั้งค่า จะถูกเปลี่ยนชื่อ branch เป็น `main` ให้อัตโนมัติหรือไม่
6. ทำไมอีเมลที่ตั้งควรตรงกับอีเมลใน GitHub account?
