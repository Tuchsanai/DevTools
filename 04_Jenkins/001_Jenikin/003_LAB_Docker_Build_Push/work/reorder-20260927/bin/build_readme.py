#!/usr/bin/env python3
"""Rebuild README.md from the pre-reorder backup:
 step 2 without the Dashboard paragraph/figure 6, Credentials first (step 3), sshpass + host-key pin after it (step 4),
 incremental Jenkinsfile walkthrough (step 5), Pipeline script from SCM job (step 6), renumbered steps/figures.
Code snippets are cut from ../../Jenkinsfile by anchors, so they are always exact excerpts."""
import os, re, textwrap

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.abspath(os.path.join(W, '..', '..'))
old = open(os.path.join(W, 'evidence', 'README.before-reorder.md'), encoding='utf-8').read().split('\n')
JF = open(os.path.join(LAB, 'Jenkinsfile'), encoding='utf-8').read()
jl = JF.rstrip('\n').split('\n')


def L(a, b):
    """old README lines a..b (1-indexed, inclusive)"""
    return '\n'.join(old[a - 1:b])


def find(sub, start=0, exact=False):
    for i in range(start, len(jl)):
        if (jl[i] == sub) if exact else (sub in jl[i]):
            return i
    raise KeyError(sub)


def snip(start, end, extra=0, end_exact=False):
    s = find(start)
    e = find(end, s + 1 if end != start else s, end_exact) + extra
    block = jl[s:e + 1]
    n = len(block[0]) - len(block[0].lstrip(' '))  # indentation of the first (Groovy) line
    return '\n'.join(l[n:] if l.startswith(' ' * n) else l for l in block)


def groovy(code):
    return '```groovy\n' + code + '\n```'


def fig_shift(text):
    return re.sub(r'ภาพที่ (\d+)', lambda m: f'ภาพที่ {int(m.group(1)) + 2}' if int(m.group(1)) >= 11 else m.group(0), text)


def anchor(line):
    """line index in old README, located by content so the script fails loudly if the backup differs"""
    for i, l in enumerate(old):
        if l.startswith(line):
            return i + 1
    raise KeyError(line)


s1 = anchor('## ขั้นที่ 1 ')
s2 = anchor('## ขั้นที่ 2 ')
dash = anchor('✅ เข้า Dashboard ของ Jenkins ได้')
s3 = anchor('## ขั้นที่ 3 ')
s4 = anchor('## ขั้นที่ 4 ')
s5 = anchor('## ขั้นที่ 5 ')
s6 = anchor('## ขั้นที่ 6 ')
s7 = anchor('## ขั้นที่ 7 ')
tbl0 = anchor('| Stage | ทำอะไร')
tbl1 = anchor('Clean ทำหลัง Push สำเร็จเท่านั้น')
res0 = anchor('✅ build #1 `SUCCESS` ครบ 8 stage')
s8 = anchor('## ขั้นที่ 8 ')
s9 = anchor('## ขั้นที่ 9 ')
chk = anchor('## ✅ ตรวจปิดแล็บ')
end = len(old)

# ---------------------------------------------------------------- intro (small edits)
intro = L(1, s1 - 1)
intro = intro.replace('🧪 9 ขั้น', '🧪 8 ขั้น')
intro = intro.replace(
    '- **`jenkins`** — ควบคุม Pipeline ไม่มี Docker CLI และไม่ mount `docker.sock` (เพิ่มแค่ `sshpass`)',
    '- **`jenkins`** — ควบคุม Pipeline: อ่าน `Jenkinsfile` จาก GitHub (Pipeline script from SCM) เก็บ Credentials และส่งคำสั่งทาง SSH · ไม่มี Docker CLI และไม่ mount `docker.sock` (เพิ่มแค่ `sshpass`)')
intro = intro.replace(
    '- port `8080`, `2222`, `3000` ต้องว่าง',
    '- port `8080`, `2222`, `3000` ต้องว่าง และ Jenkins ต้องออก internet ไป `github.com` ได้ (โหลด `Jenkinsfile`) · devtools ต้องไป `github.com` และ Docker Hub ได้')
for a, b in [('หน้าสร้าง token บน Docker Hub:', None)]:
    assert a in intro

# ---------------------------------------------------------------- step 1, step 2 (drop Dashboard paragraph + figure 6)
step1 = L(s1, s2 - 1)
step2 = L(s2, dash - 1).rstrip('\n')
assert 'lab3_sib_dashboard' not in step2

# ---------------------------------------------------------------- step 3 credentials (new, first after Jenkins setup)
step3 = '''## ขั้นที่ 3 — สร้าง Jenkins Credentials: `devtools-ssh` และ `dockerhub`

ก่อนเขียนหรือรัน Pipeline ให้เก็บความลับไว้ใน Jenkins ก่อน `Jenkinsfile` อ้างถึงแค่ **ID** (`devtools-ssh`, `dockerhub`) ไม่มีรหัสผ่านหรือ token อยู่ในไฟล์ และ Jenkins จะซ่อนค่าเป็น `****` ใน console ให้

| ID | ใช้ทำอะไร | ใช้ใน stage |
|---|---|---|
| `devtools-ssh` | username/password ที่ Jenkins ใช้ **SSH เข้า `devtools`** (`root` / `passwd`) ทุกครั้งที่ส่งคำสั่ง | ทุก stage (ผ่านฟังก์ชัน `onDevtools`) และ `post` |
| `dockerhub` | username + Personal Access Token ของ Docker Hub: username ใช้ตั้งชื่อ repository `docker.io/<DOCKER_USER>/catfood-shop` ส่วน token ใช้ `docker login` บน devtools เพื่อ **push** (ต้องมีสิทธิ์ Write) แล้ว **pull** กลับตาม digest (สิทธิ์ Read) ก่อน deploy | Connect (อ่าน username) · Push (login + push) · Pull (pull แล้ว logout) |

เปิด **Manage Jenkins → Credentials → System → Global credentials (unrestricted)** แล้วกด **+ Add Credentials**

[![หน้า Global credentials ก่อนเพิ่ม credential](./images/lab3_scm_01_credentials_store_crop.png)](./images/lab3_scm_01_credentials_store.png)

*ภาพที่ 6 หน้า **Global credentials (unrestricted)** ยังว่าง · กด **+ Add Credentials** ที่มุมขวาบน*

**3.1) `devtools-ssh`** — เลือกชนิด **Username with password** แล้วกรอกในหน้าต่าง **Add Username with password**:

| ช่อง | ค่า |
|---|---|
| Username | `root` |
| Treat username as secret | ไม่ติ๊ก (ถ้าติ๊ก console จะแสดง `user=****`) |
| Password | `passwd` |
| ID | `devtools-ssh` |
| Description | `SSH password: Jenkins to devtools` |

กด **Create** · `passwd` เป็นรหัสตั้งต้นของ image แล็บนี้เท่านั้น

[![ฟอร์ม credential devtools-ssh](./images/lab3_scm_02_cred_devtools_ssh_crop.png)](./images/lab3_scm_02_cred_devtools_ssh.png)

*ภาพที่ 7 ฟอร์ม **Add Username with password** ของ `devtools-ssh`: Username `root` · ไม่ติ๊ก Treat username as secret · Password ถูกซ่อน · ID `devtools-ssh`*

**3.2) `dockerhub`** — กด **+ Add Credentials** อีกครั้ง ชนิด **Username with password** เหมือนเดิม:

| ช่อง | ค่า |
|---|---|
| Username | `<DOCKER_USER>` ชื่อบัญชี Docker Hub (ตัวพิมพ์เล็ก) |
| Treat username as secret | ไม่ติ๊ก |
| Password | `<DOCKER_TOKEN>` Personal Access Token จากภาพที่ 3 (Repo **Read & Write**) ไม่ใช่รหัสผ่านบัญชี |
| ID | `dockerhub` |
| Description | `Docker Hub access token` |

[![ฟอร์ม credential dockerhub](./images/lab3_scm_03_cred_dockerhub_crop.png)](./images/lab3_scm_03_cred_dockerhub.png)

*ภาพที่ 8 ฟอร์มของ `dockerhub` · ในภาพใช้ชื่อสมมติ `demostudent` และ token สมมติ ให้ใส่บัญชีและ token ของตัวเอง*

[![รายการ credential สองตัว](./images/lab3_scm_04_credentials_list_crop.png)](./images/lab3_scm_04_credentials_list.png)

*ภาพที่ 9 Global credentials มี `devtools-ssh` (`root/******`) และ `dockerhub` (`<DOCKER_USER>/******`) · Jenkins ไม่แสดงรหัสผ่านหรือ token*

> ⚠️ วาง token ใน Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git · ID ต้องสะกดตรงตัว เพราะ `Jenkinsfile` เรียกด้วย ID นี้'''

# ---------------------------------------------------------------- step 4: sshpass + host key pin (+ optional test)
p_sshpass = L(s3 + 1, s4 - 1).strip('\n')
p_sshpass = p_sshpass.replace(
    '**ทำไมต้องมี `sshpass`:** Pipeline ของแล็บนี้ให้ Jenkins **SSH ออกไปหา `devtools`** ด้วยรหัสผ่านโดยอัตโนมัติทุก stage แต่คำสั่ง `ssh` ปกติจะหยุดรอให้คนพิมพ์รหัส `sshpass` จึงทำหน้าที่ส่งรหัสให้แทน โดยรหัสมาจาก credential `devtools-ssh` ที่จะสร้างในขั้นที่ 6 (ไม่ได้เขียนไว้ใน Jenkinsfile)',
    '**ทำไมต้องมี `sshpass`:** Pipeline ของแล็บนี้ให้ Jenkins **SSH ออกไปหา `devtools`** ด้วยรหัสผ่านโดยอัตโนมัติทุก stage แต่คำสั่ง `ssh` ปกติจะหยุดรอให้คนพิมพ์รหัส `sshpass` จึงทำหน้าที่ส่งรหัสให้แทน โดยรหัสมาจาก credential `devtools-ssh` ที่สร้างในขั้นที่ 3 (ไม่ได้เขียนไว้ใน Jenkinsfile)')
assert 'ขั้นที่ 3 (ไม่ได้เขียน' in p_sshpass
p_pin = L(s4 + 1, s5 - 1).strip('\n')
p_test = L(s5 + 1, s6 - 1).strip('\n')
p_test = p_test.replace('ตอนกด Build (ขั้นที่ 7) แทน', 'ตอนกด Build (ขั้นที่ 6) แทน')
assert 'ขั้นที่ 6) แทน' in p_test
step4 = '\n\n'.join([
    '## ขั้นที่ 4 — เตรียม `jenkins` ให้ SSH ไป `devtools` ได้ (🖥️ host)',
    'credential `devtools-ssh` จากขั้นที่ 3 จะถูกใช้จริงเมื่อ Pipeline เริ่ม SSH ใน stage Connect ก่อนถึงตอนนั้น `jenkins` ต้องมีอีกสองอย่าง: โปรแกรม `sshpass` สำหรับส่งรหัสผ่าน และ host key ของ `devtools` ที่เชื่อถือไว้ล่วงหน้า',
    '### 4.1) ติดตั้ง `sshpass` ใน `jenkins`', p_sshpass,
    '### 4.2) pin host key ของ `devtools`', p_pin,
    '### 4.3) (ไม่บังคับ) ทดสอบ SSH ด้วยรหัสผ่าน', p_test])

S = {
    'skel': groovy(snip('pipeline {', 'skipDefaultCheckout()', extra=1)),
    'cred': groovy(snip("withCredentials([usernamePassword(credentialsId: 'dockerhub',", 'env.HUB_REPO = ', extra=1)),
    'ondev': groovy(snip('def onDevtools(', '}', end_exact=True)),
    'connect': groovy(snip("onDevtools([:], '''", "''')")),
    'clone': groovy(snip('def commit = onDevtools(', "''', true).trim()")),
    'build': groovy(snip('onDevtools([SRC:', "''')")),
    'test': groovy(snip('docker run -d --name "$NAME" --label devtools.lab=lab3 --label devtools.role=test', '[ "$STATUS" = healthy ]', end_exact=True)),
    'login': groovy(snip("sh '''set +x", "'''")),
    'digest': groovy(snip('def digest = onDevtools(', "''', true).trim()")),
    'pull': groovy(snip('onDevtools([CFG: env.DOCKER_CFG, REF:', "''')")),
    'deploy': groovy(snip('docker run -d --name "$NAME" --restart unless-stopped', 'docker run -d --name "$NAME" --restart unless-stopped', extra=1)),
}

# ---------------------------------------------------------------- step 5: build up the Jenkinsfile layer by layer
stage_table = L(tbl0, tbl1)
step5 = f'''## ขั้นที่ 5 — ทำความเข้าใจ `Jenkinsfile` ทีละชั้น

[`Jenkinsfile`](./Jenkinsfile) ของแล็บนี้อยู่ใน GitHub แล้ว ในขั้นที่ 6 Jenkins จะอ่านไฟล์นี้จาก Git เอง ขั้นนี้จึง**ไม่ต้องพิมพ์หรือคัดลอกไฟล์** ให้อ่านทีละชั้นตามลำดับที่ Pipeline ใช้งานจริง: **Credentials → SSH ไป devtools → git clone → Docker build/test → Docker Hub push/pull/deploy** (โค้ดด้านล่างตัดมาจากไฟล์จริง)

**5.1) ใครโหลดอะไร: Jenkins โหลด Pipeline ส่วน devtools clone แอป**

- job แบบ **Pipeline script from SCM** ทำให้ Jenkins (controller) ดึง `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile` จาก `https://github.com/Tuchsanai/DevTools.git` branch `main` **ก่อน** Pipeline เริ่ม นี่คือ Git ครั้งเดียวที่ Jenkins ทำเอง
- `devtools` ช่วยงานนี้ไม่ได้ เพราะ Jenkins จะรู้ว่าต้อง SSH ไปไหนและใช้ credential ตัวใด ก็ต่อเมื่ออ่าน `Jenkinsfile` แล้ว
- หลังจากนั้นทุกอย่างของแอป (`git clone` ซอร์สร้าน, `docker build`/`run`/`push`/`pull`) Jenkins ส่งผ่าน SSH ไปรันบน `devtools`
- ปกติ Declarative Pipeline จะ checkout ทั้ง repository ลง workspace ของ Jenkins อีกรอบโดยอัตโนมัติ แต่แล็บนี้ไม่ใช้ไฟล์ใน workspace นั้น (repository ของรายวิชาใหญ่ระดับ GB) จึงปิดด้วย `skipDefaultCheckout()`:

{S['skel']}

**5.2) ชั้นที่ 1 — Credentials:** `withCredentials` ดึงค่าจาก ID ที่สร้างในขั้นที่ 3 มาเป็นตัวแปรชั่วคราวเฉพาะในบล็อก ใน stage Connect ใช้แค่ username ของ `dockerhub` เพื่อตั้งชื่อ repository ปลายทาง:

{S['cred']}

**5.3) ชั้นที่ 2 — SSH ไป devtools:** ฟังก์ชัน `onDevtools(ตัวแปร, สคริปต์)` เขียนสคริปต์ของ stage เป็น `remote.sh` แล้วส่งทาง SSH โดยใช้ `devtools-ssh`, `sshpass` และ host key จากขั้นที่ 4:

{S['ondev']}

- `sshpass -e` อ่านรหัสจากตัวแปร `SSHPASS` รหัสจึงไม่โผล่ใน command line หรือ console · `sh(script: '...')` เป็นข้อความคงที่ `$SSH_USER` จึงถูกแทนค่าโดย shell ไม่ใช่ Groovy · SSH ต่อเฉพาะเมื่อ host key ตรงกับที่ pin ในขั้นที่ 4.2
- สคริปต์อยู่ใน `\'\'\'...\'\'\'` Groovy จึงไม่แทนค่า `$` เอง แล้วส่งทาง stdin ไปรันด้วย bash บน devtools
- parameter ถูกตรวจด้วย regex (ยอมเฉพาะ `A-Za-z0-9._:/@=+-`) แล้วเขียนเป็น `NAME='value'` ต้น `remote.sh` ค่าที่แฝงคำสั่ง shell จึงไปไม่ถึง devtools

stage Connect เรียก `onDevtools` ครั้งแรกเพื่อถามว่า devtools พร้อมไหม:

{S['connect']}

**5.4) ชั้นที่ 3 — git clone บน devtools:** stage Clone ให้ devtools ทำ sparse clone เฉพาะโฟลเดอร์ `catfood-shop` แล้วส่ง commit กลับมาให้ Jenkins จดไว้:

{S['clone']}

**5.5) ชั้นที่ 4 — Docker build และ test บน devtools:** Build ฝังเวอร์ชัน/build/commit ลง image แล้ว Test รัน container ชั่วคราวจนกว่าจะ `healthy`:

{S['build']}

ส่วนหนึ่งของสคริปต์ที่ stage Test ส่งไปรันบน devtools:

{S['test']}

**5.6) ชั้นที่ 5 — Docker Hub push → pull → deploy:** Push ส่ง token ทาง stdin ให้ `docker login --password-stdin` บน devtools แล้ว push และจด **digest**:

{S['login']}

{S['digest']}

Clean ลบร้านเดิมและ image ในเครื่อง (ทำ**หลัง** Push สำเร็จเท่านั้น) แล้ว Pull ดึง image กลับมาด้วย digest ตัวเดียวกัน ก่อน Deploy รันร้าน:

{S['pull']}

และคำสั่งหลักในสคริปต์ของ stage Deploy (รันจาก `<repo>@<digest>` ไม่ใช่ tag):

{S['deploy']}

**5.7) ครบ 8 stage:**

{stage_table}

- Clean ลบเฉพาะของที่มี label `devtools.lab=lab3` · `post {{ unsuccessful }}` ลบของชั่วคราวของ build ที่ล้มโดยไม่แตะร้าน · `disableConcurrentBuilds()` กันสอง build ใช้ port 3000 พร้อมกัน

<details>
<summary><b>Jenkinsfile ฉบับสมบูรณ์</b> (เหมือนไฟล์ <code>Jenkinsfile</code> ทุกตัวอักษร คลิกเพื่อเปิด)</summary>

```groovy
{JF.rstrip(chr(10))}
```

</details>'''

# ---------------------------------------------------------------- step 6: job from SCM + first build (old results kept)
results = fig_shift(L(res0, s8 - 1).rstrip('\n'))
step6 = f'''## ขั้นที่ 6 — สร้าง job แบบ Pipeline script from SCM แล้ว Build Now

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → เลือก **Pipeline** → **OK**

[![หน้า New Item](./images/lab3_scm_05_new_item_crop.png)](./images/lab3_scm_05_new_item.png)

*ภาพที่ 10 หน้า **New Item**: ชื่อ `docker-build-push` และเลือกชนิด **Pipeline***

2. เลื่อนลงไปส่วน **Pipeline** แล้วตั้งค่าตามตาราง → **Save**

| ช่อง | ค่า |
|---|---|
| Definition | **Pipeline script from SCM** |
| SCM | **Git** |
| Repository URL | `https://github.com/Tuchsanai/DevTools.git` |
| Credentials | `- none -` (repository สาธารณะ) |
| Branch Specifier | `*/main` |
| Script Path | `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile` |
| Lightweight checkout | ติ๊ก (ค่าเริ่มต้น) Jenkins ดึงเฉพาะ `Jenkinsfile` มาอ่าน |

[![Definition Pipeline script from SCM](./images/lab3_scm_06_pipeline_from_scm_crop.png)](./images/lab3_scm_06_pipeline_from_scm.png)

*ภาพที่ 11 ส่วน **Pipeline** ของหน้า Configure: Definition = **Pipeline script from SCM**, SCM = **Git**, Repository URL ของรายวิชา และ Credentials = none*

[![Branch และ Script Path](./images/lab3_scm_07_branch_script_path_crop.png)](./images/lab3_scm_07_branch_script_path.png)

*ภาพที่ 12 Branch Specifier `*/main`, Script Path ของ `Jenkinsfile` แล็บนี้ และ **Lightweight checkout***

3. กด **Build Now** — job ใหม่ยังไม่มี **Build with Parameters** จนกว่าจะรันครั้งแรก build แรกจึงใช้ค่า default (`APP_VERSION=1.0.0`, tag `lab3-1`)

✅ บรรทัดแรก ๆ ของ **Console Output** บอกว่า Jenkins ดึง `Jenkinsfile` มาจาก Git แล้ว stage ถัดไปคือ **Connect** ทันที (ไม่มี `Declarative: Checkout SCM` เพราะ `skipDefaultCheckout()`):

```text
Obtained 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile from git https://github.com/Tuchsanai/DevTools.git
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/docker-build-push
[Pipeline] {{
[Pipeline] withEnv
[Pipeline] {{
[Pipeline] stage
[Pipeline] {{ (Connect)
```

> build แรกอาจรอช่วง `Obtained ... from git` นานกว่าปกติ เพราะ Jenkins ต้องดึงข้อมูล repository ครั้งแรก รอบถัดไปใช้ cache · ถ้าเห็น stage `Declarative: Checkout SCM` แปลว่า `Jenkinsfile` ที่ Jenkins ดึงมายังเป็นรุ่นก่อนเพิ่ม `skipDefaultCheckout()` จะยังทำงานได้แต่ช้ากว่า

> 📷 ภาพที่ 13–29 ถ่ายจากรอบทดสอบเดิมที่ใช้ `Jenkinsfile` เดียวกันแบบวางในช่อง Pipeline script ชื่อและลำดับ stage รวมถึง log ของแต่ละ stage เหมือนกับโหมด SCM

{results}'''

step7 = fig_shift(L(s8, s9 - 1).rstrip('\n')).replace('## ขั้นที่ 8 —', '## ขั้นที่ 7 —')
step8 = fig_shift(L(s9, chk - 1).rstrip('\n')).replace('## ขั้นที่ 9 —', '## ขั้นที่ 8 —')

tail = L(chk, end)
reps = [
    ('- [ ] Credentials มี `devtools-ssh` (`root`) และ `dockerhub`',
     '- [ ] Credentials มี `devtools-ssh` (`root`) และ `dockerhub` · job `docker-build-push` เป็น **Pipeline script from SCM** ชี้ไปที่ Script Path ของแล็บนี้'),
    ('- [ ] build ในขั้นที่ 9 ล้มตามที่คาด', '- [ ] build ในขั้นที่ 8 ล้มตามที่คาด'),
    ('| `sshpass: not found` ใน Connect | รันขั้นที่ 3 อีกครั้ง (เกิดเมื่อสร้าง `jenkins` ใหม่) |',
     '| `sshpass: not found` ใน Connect | รันขั้นที่ 4.1 อีกครั้ง (เกิดเมื่อสร้าง `jenkins` ใหม่) |'),
    ('→ รันขั้นที่ 4 อีกครั้ง |', '→ รันขั้นที่ 4.2 อีกครั้ง |'),
    ('| `Could not find credentials entry with ID ...` | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ให้ตรงตัว |',
     '| `Could not find credentials entry with ID ...` | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ให้ตรงตัว (ขั้นที่ 3) |\n'
     '| `Unable to find 04_Jenkins/.../Jenkinsfile from git` / `Couldn\'t find any revision to build` | ตรวจ Repository URL, Branch Specifier `*/main` และ Script Path ในขั้นที่ 6 ให้ตรงตัว (ตัวพิมพ์เล็ก-ใหญ่มีผล) |\n'
     '| `Failed to connect to repository` ตอน Save หรือ build ค้างที่ `Obtained ...` | `jenkins` ต้องออก internet ไป `github.com` ได้ · build แรกดึงข้อมูลนานกว่าปกติ |'),
    ('| เปิด `localhost:3000` ไม่ได้ทั้งที่ Deploy เขียว | `docker port devtools` ถ้าไม่มี 3000 ให้ทำขั้นที่ 1 ใหม่ |',
     '| เปิด `localhost:3000` ไม่ได้ทั้งที่ Deploy เขียว | `docker port devtools` ถ้าไม่มี 3000 ให้ทำขั้นที่ 1 ใหม่ |'),
    ('4. ทำไม Clean ต้องเกิด **หลัง** Push สำเร็จ และทำไม Pull/Deploy ใช้ `repository@sha256:...` แทน `repository:tag`',
     '4. ทำไม Clean ต้องเกิด **หลัง** Push สำเร็จ และทำไม Pull/Deploy ใช้ `repository@sha256:...` แทน `repository:tag`\n'
     '5. ในโหมด Pipeline script from SCM ทำไม Jenkins ต้องดึง `Jenkinsfile` เองแทนที่จะให้ devtools clone ให้ และ `skipDefaultCheckout()` ช่วยอะไร'),
    ('เอกสารนี้ทดสอบจริงครบทุกขั้นแล้ว ดู [รายงานผลทดสอบ](./LAB003_FINAL_REPORT.md)',
     'ผลทดสอบรอบ Pipeline script ดู [รายงานผลทดสอบ](./LAB003_FINAL_REPORT.md) · โหมด Pipeline script from SCM ทดสอบเพิ่มเมื่อ 2026-09-27 (build จริงครบ 8 stage)'),
]
for a, b in reps:
    assert tail.count(a) == 1, a
    tail = tail.replace(a, b)

def crop_or_full(text):
    """use images/X_crop.png only if the coordinator delivered it, else show the full capture"""
    def f(m):
        alt, name = m.group(1), m.group(2)
        crop = f'{name}_crop.png'
        img = crop if os.path.exists(os.path.join(LAB, 'images', crop)) else f'{name}.png'
        return f'[![{alt}](./images/{img})](./images/{name}.png)'
    return re.sub(r'\[!\[([^\]]*)\]\(\./images/(lab3_scm_[0-9a-z_]+?)_crop\.png\)\]\(\./images/\2\.png\)', f, text)


step3, step6 = crop_or_full(step3), crop_or_full(step6)
out = '\n\n'.join(x.strip('\n') for x in [intro, step1, step2, step3, step4, step5, step6, step7, step8, tail]) + '\n'
open(os.path.join(LAB, 'README.md'), 'w', encoding='utf-8').write(out)
print('README.md written', len(out.split('\n')), 'lines')
