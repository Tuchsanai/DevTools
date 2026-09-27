#!/usr/bin/env python3
"""Rewrite README step 5 (teach creating a Jenkinsfile), step 3/6 caption fixes, new GitHub/Docker Hub figures, renumber figures.
Input: evidence/README.before-teach.md. Excerpts are reused verbatim from the existing README (already exact Jenkinsfile excerpts)."""
import os, re
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LAB = os.path.abspath(os.path.join(W, '..', '..'))
R = open(f'{W}/evidence/README.before-teach.md', encoding='utf-8').read()
JF = open(f'{LAB}/Jenkinsfile', encoding='utf-8').read(); jl = [l.strip() for l in JF.split('\n')]

a = R.index('## ขั้นที่ 5 '); b = R.index('**5.7) ครบ 8 stage:**')
old5 = R[a:b]
blk = re.findall(r'```groovy\n(.*?)\n```', old5, re.S)
assert len(blk) == 11, len(blk)

def lines(code, bash=False):
    bl = [l.strip() for l in code.split('\n')]
    for i in range(len(jl)):
        if jl[i:i + len(bl)] == bl:
            return i + 1, i + len(bl)
    raise KeyError(code[:40])

def ex(code, where, bash=False):
    s, e = lines(code)
    lang = 'bash' if bash else 'groovy'
    body = code.replace('\\\\', '\\') if bash else code
    return f'📄 *ส่วนหนึ่งของ `Jenkinsfile` บรรทัด {s}–{e} · {where}*\n\n```{lang}\n{body}\n```'

SKEL = r'''```groovy
// Jenkinsfile — โครงเปล่า (skeleton) รันได้แต่ยังไม่ทำงานจริง: เติมโค้ดของแต่ละชั้นตาม 5.4–5.8

// [A] ฟังก์ชันช่วย (helper) ประกาศนอก pipeline { } ด้านบนสุดของไฟล์
def requireMatch(String name, String value, String regex, String hint) {
  // 5.4: ตรวจค่าด้วย regex
}

def onDevtools(Map vars, String body, boolean capture = false) {
  // 5.5: ส่งสคริปต์ไปรันบน devtools ผ่าน SSH
}

pipeline {                  // [B] บล็อกนอกสุด มีได้บล็อกเดียวต่อไฟล์
  agent any                 // [C] รันบน executor ใดก็ได้ของ Jenkins

  options {                 // [D] ตัวเลือกของทั้ง job
    disableConcurrentBuilds()
    skipDefaultCheckout()
  }

  parameters {              // [E] ช่องในหน้า Build with Parameters อ่านด้วย params.NAME
    string(name: 'APP_VERSION', defaultValue: '1.0.0', description: 'เวอร์ชัน X.Y.Z')
  }

  environment {             // [F] ตัวแปรที่ทุก stage อ่านได้ด้วย env.NAME
    APP_NAME = 'catfood-shop'
  }

  stages {                  // [G] รายการ stage เรียงตามลำดับที่รัน
    stage('Connect') {      // [H] หนึ่ง stage = หนึ่งช่องใน Stage View
      steps {               // [I] คำสั่งของ stage
        script {            // [J] Groovy เต็มรูปแบบ: def, if, try และเก็บค่าที่ฟังก์ชันคืน
          echo "Connect: ${env.APP_NAME} v${params.APP_VERSION}"
        }
      }
    }
    stage('Clone') {
      steps {
        script {
          echo 'Clone'
        }
      }
    }
    // stage Build, Test, Push, Clean, Pull, Deploy เขียนแบบเดียวกัน ต่อท้ายในบล็อก stages
  }

  post {                    // [K] ทำหลังทุก stage จบ ตามผลของ build
    success {
      echo 'สำเร็จ'
    }
    unsuccessful {
      echo 'ไม่สำเร็จ: เก็บกวาดของชั่วคราว'
    }
    always {
      deleteDir()
    }
  }
}
```'''

# helper requireMatch excerpt from the Jenkinsfile itself
rm = '\n'.join(JF.split('\n')[8:13])
assert rm.startswith('def requireMatch') and rm.endswith('}'), rm

loads = old5[old5.index('- job แบบ **Pipeline script from SCM**'):old5.index('```groovy')].rstrip()
loads = loads.replace('จึงปิดด้วย `skipDefaultCheckout()`:', 'จึงปิดด้วย `skipDefaultCheckout()` ใน `options` (ตำแหน่ง [D] ในโครงข้อ 5.3)')

def para(prefix):  # explanatory paragraph that starts with prefix in old step 5 (up to the next blank line)
    i = old5.index(prefix); return old5[i:old5.index('\n\n', i)]

ssh_notes = old5[old5.index('- `sshpass -e` อ่านรหัส'):old5.index('stage Connect เรียก')].rstrip()

new5 = f'''## ขั้นที่ 5 — สร้าง `Jenkinsfile` ทีละชั้น

`Jenkinsfile` คือไฟล์ข้อความที่เขียน Pipeline ด้วยภาษา Groovy แล้วเก็บไว้ใน Git คู่กับซอร์ส ในขั้นที่ 6 Jenkins จะอ่านไฟล์นี้จาก Git ทุกครั้งที่ build ขั้นนี้สอนวิธีสร้างไฟล์ตั้งแต่โครงเปล่า แล้วเติมทีละชั้นตามลำดับที่ Pipeline ใช้งานจริง: **Credentials → SSH ไป devtools → git clone → Docker build/test → Docker Hub push/pull/deploy**

| ทางเลือก | ทำอะไร | ขั้นที่ 6 ตั้งค่า |
|---|---|---|
| **ก. รันแล็บด้วยไฟล์ของรายวิชา** (แนะนำสำหรับรอบแรก) | อ่านขั้นนี้เพื่อเข้าใจโครงสร้าง แล้วใช้ [`Jenkinsfile`](./Jenkinsfile) ฉบับสมบูรณ์ที่อยู่ใน repository ของรายวิชาอยู่แล้ว **ไม่ต้อง fork** | Repository URL และ Script Path ของรายวิชา (ตารางในขั้นที่ 6) |
| **ข. ฝึกเขียนเอง** | สร้างไฟล์ `Jenkinsfile` ใน repository Git **สาธารณะ** ของตัวเอง ประกอบตาม 5.3–5.8 แล้ว commit/push | Repository URL ของตัวเอง และ Script Path ที่ชี้ไปยังไฟล์นั้น |

ทั้งสองทางใช้ซอร์สร้านจาก parameter `GIT_URL`/`APP_SUBDIR` (ค่าเริ่มต้นคือ repository ของรายวิชา) จึงไม่ต้องคัดลอกโฟลเดอร์ `catfood-shop`

**5.1) ชื่อไฟล์และตำแหน่ง**

- ตั้งชื่อ `Jenkinsfile` (J ตัวใหญ่ ไม่มีนามสกุล) บันทึกเป็น UTF-8
- Jenkins หาไฟล์ตาม **Script Path** ในขั้นที่ 6 ซึ่งเป็น path แบบ relative จาก root ของ repository และต้องสะกดตรงตัวพิมพ์ ในรายวิชาไฟล์อยู่ที่ `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile`
- ทางเลือก ข: ถ้าวางไฟล์ไว้ที่ root ของ repository ของตัวเอง Script Path คือ `Jenkinsfile`:

```bash
cd <โฟลเดอร์ที่ clone repository ของตัวเองไว้>
touch Jenkinsfile               # สร้างไฟล์เปล่า แล้วเปิดด้วย editor เติมตาม 5.3–5.8
git add Jenkinsfile
git commit -m "Add LAB 3 Jenkinsfile"
git push
```

[![Jenkinsfile ของแล็บบน GitHub](./images/lab3_scm_github_jenkinsfile_crop.png)](./images/lab3_scm_github_jenkinsfile.png)

*ภาพที่ @GH@ ไฟล์ `Jenkinsfile` ของแล็บนี้บน GitHub branch `main` ของ repository รายวิชา (path `DevTools / 04_Jenkins / 001_Jenikin / 003_LAB_Docker_Build_Push / Jenkinsfile`) · ถ่ายก่อนอัปเดตรอบนี้ (commit `92d3888`) หัวไฟล์ในภาพจึงยังต่างจากฉบับปัจจุบันเล็กน้อย*

**5.2) ใครโหลดอะไร: Jenkins โหลด Pipeline ส่วน devtools clone แอป**

{loads}

**5.3) โครงของ Declarative Pipeline**

เริ่มจากโครงนี้ก่อน วงเล็บปีกกา `{{ }}` ทุกคู่ต้องปิดครบ ทุกส่วนอยู่ใน `pipeline {{ }}` ยกเว้นฟังก์ชันช่วยที่อยู่ด้านบนไฟล์:

{SKEL}

| ส่วน | อยู่ตรงไหน | ในไฟล์จริงของแล็บนี้ |
|---|---|---|
| [A] ฟังก์ชันช่วย `def ...` | นอก `pipeline {{ }}` ด้านบนสุด | `requireMatch` (5.4), `onDevtools` (5.5) |
| [C] `agent` | บรรทัดแรกใน `pipeline` | `agent any` คำสั่ง `sh` รันบน Jenkins แล้ว SSH ต่อไป devtools |
| [D] `options` | ใน `pipeline` ก่อน `stages` | `disableConcurrentBuilds()`, `skipDefaultCheckout()` |
| [E] `parameters` | ใน `pipeline` | `GIT_URL`, `GIT_REF`, `APP_SUBDIR`, `APP_VERSION`, `TAG_PREFIX` |
| [F] `environment` | ใน `pipeline` | `APP_NAME`, `DEPLOY_NAME`, `TEST_NAME`, `WORK_DIR`, `DOCKER_CFG`, `LOCAL_IMAGE` |
| [G]–[I] `stages` / `stage` / `steps` | ใน `pipeline` | 8 stage: Connect … Deploy |
| [J] `script {{ }}` | ใน `steps` | ทุก stage ใช้ เพราะมี `def`, `withCredentials` และเก็บค่าที่ `onDevtools` คืน |
| [K] `post` | ใน `pipeline` หลัง `stages` | `success` แสดง URL ร้าน · `unsuccessful` เก็บกวาด · `always` ลบ workspace |

จากนี้ไปแต่ละชั้นจะเติมโค้ดลงในโครงนี้ ทุกบล็อกที่มีป้าย 📄 เป็น**ส่วนหนึ่ง**ที่ตัดมาจากไฟล์จริงตามเลขบรรทัด ไม่ใช่ไฟล์เต็ม ให้วางตามตำแหน่งที่ป้ายบอก

**5.4) ชั้นที่ 1 — Credentials:** {para('`withCredentials` ดึงค่า')}

{ex(rm, 'แทน `requireMatch` ในส่วน [A]')}

{ex(blk[1], 'ใน `script { }` ของ `stage(\'Connect\')`')}

**5.5) ชั้นที่ 2 — SSH ไป devtools:** {para('ฟังก์ชัน `onDevtools(')}

{ex(blk[2], 'แทน `onDevtools` ในส่วน [A]')}

{ssh_notes}

stage Connect เรียก `onDevtools` ครั้งแรกเพื่อถามว่า devtools พร้อมไหม:

{ex(blk[3], 'ต่อท้ายใน `script { }` ของ `stage(\'Connect\')`')}

**5.6) ชั้นที่ 3 — git clone บน devtools:** {para('stage Clone ให้')}

{ex(blk[4], 'ใน `script { }` ของ `stage(\'Clone\')`')}

**5.7) ชั้นที่ 4 — Docker build และ test บน devtools:** {para('Build ฝังเวอร์ชัน')}

{ex(blk[5], 'ใน `script { }` ของ `stage(\'Build\')`')}

สคริปต์ที่ส่งไป devtools อยู่ใน `\'\'\'...\'\'\'` ของ Groovy ในไฟล์จึงต้องเขียน `\\` แทน `\\` หนึ่งตัวของ shell บล็อก `bash` ด้านล่างแสดงสิ่งที่ bash บน devtools ได้รับจริง (ตัด `\\` ซ้ำออกแล้ว)

ส่วนหนึ่งของสคริปต์ bash ที่ stage Test ส่งไปรันบน devtools:

{ex(blk[6], 'สคริปต์ใน `onDevtools(...)` ของ `stage(\'Test\')` แสดงแบบที่ bash ได้รับ', bash=True)}

**5.8) ชั้นที่ 5 — Docker Hub push → pull → deploy:** {para('Push ส่ง token')}

{ex(blk[7], 'ใน `withCredentials` ของ `stage(\'Push\')`')}

{ex(blk[8], 'ต่อจากบล็อกก่อนหน้าใน `stage(\'Push\')`')}

{para('Clean ลบร้านเดิม')}

{ex(blk[9], 'ใน `script { }` ของ `stage(\'Pull\')`')}

และคำสั่งหลักในสคริปต์ bash ของ stage Deploy (รันจาก `<repo>@<digest>` ไม่ใช่ tag):

{ex(blk[10], 'สคริปต์ใน `onDevtools(...)` ของ `stage(\'Deploy\')` แสดงแบบที่ bash ได้รับ', bash=True)}

'''
new5 = new5.replace("`\\'\\'\\'...\\'\\'\\'`", "`'''...'''`")
BS = chr(92)
new5 = new5.replace('ในไฟล์จึงต้องเขียน `' + BS + '` แทน `' + BS + '` หนึ่งตัวของ shell', 'ในไฟล์จึงต้องเขียน backslash สองตัว `' + BS * 2 + '` แทน `' + BS + '` หนึ่งตัวของ shell')
new5 = new5.replace('(ตัด `' + BS + '` ซ้ำออกแล้ว)', '(backslash เหลือตัวเดียวแบบ shell จริง)')
R = R[:a] + new5 + R[b:]
R = R.replace('**5.7) ครบ 8 stage:**', '**5.9) ประกอบครบ 8 stage:** เมื่อเติมทุกชั้นลงในโครงข้อ 5.3 และเพิ่ม stage Clean ระหว่าง Push กับ Pull จะได้ไฟล์ฉบับสมบูรณ์ด้านล่าง ซึ่งเป็นไฟล์เดียวกับที่ขั้นที่ 6 ให้ Jenkins อ่านจาก GitHub')

# ---- step 3 captions
R = R.replace('*ภาพที่ 6 หน้า **Global credentials (unrestricted)** ยังว่าง · กด **+ Add Credentials** ที่มุมขวาบน*',
              '*ภาพที่ 6 หน้า **Global** ของ System credentials ยังว่าง (`This credentials domain is empty`) · กดปุ่ม **+ Add Credentials** กลางกล่อง (เมื่อมี credential แล้ว ปุ่มนี้ย้ายไปอยู่มุมขวาบนของรายการ)*')
R = R.replace('*ภาพที่ 8 ฟอร์มของ `dockerhub` · ในภาพใช้ชื่อสมมติ `demostudent` และ token สมมติ ให้ใส่บัญชีและ token ของตัวเอง*',
              '*ภาพที่ 8 ฟอร์มของ `dockerhub` · ภาพนี้ถ่ายจาก Jenkins ทดสอบที่ใส่ชื่อสมมติ `demostudent` และ token สมมติ (ไม่ใช่บัญชีจริง) ให้ใส่บัญชีและ token ของตัวเอง*')
R = R.replace('*ภาพที่ 9 Global credentials มี `devtools-ssh` (`root/******`) และ `dockerhub` (`<DOCKER_USER>/******`) · Jenkins ไม่แสดงรหัสผ่านหรือ token*',
              '*ภาพที่ 9 Global credentials มี `devtools-ssh` (`root/******`) และ `dockerhub` (ในภาพเป็นชื่อสมมติ `demostudent/******` ของคุณจะเป็น `<DOCKER_USER>/******`) · Jenkins ไม่แสดงรหัสผ่านหรือ token*')

# ---- step 6
s6 = R.index('## ขั้นที่ 6 ')
R = R[:s6] + R[s6:].replace('## ขั้นที่ 6 — สร้าง job แบบ Pipeline script from SCM แล้ว Build Now\n\n',
  '## ขั้นที่ 6 — สร้าง job แบบ Pipeline script from SCM แล้ว Build Now\n\n'
  'ตารางด้านล่างใช้ `Jenkinsfile` ฉบับสมบูรณ์ของรายวิชา (ทางเลือก ก ในขั้นที่ 5) ไม่ต้อง fork · ถ้าเขียนไฟล์เอง (ทางเลือก ข) ให้เปลี่ยนเฉพาะ **Repository URL**, **Branch Specifier** และ **Script Path** เป็นของ repository ตัวเอง\n\n', 1)
R = R.replace('| Lightweight checkout | ติ๊ก (ค่าเริ่มต้น) Jenkins ดึงเฉพาะ `Jenkinsfile` มาอ่าน |',
              '| Lightweight checkout | ติ๊ก (ค่าเริ่มต้น) Jenkins อ่าน `Jenkinsfile` ผ่าน SCM โดยไม่ checkout ทั้ง repository ลง workspace ของ job (ยังอาจดึงข้อมูล Git มาเก็บเป็น cache) |')
R = R.replace('[![Branch และ Script Path](./images/lab3_scm_07_branch_script_path.png)](./images/lab3_scm_07_branch_script_path.png)',
              '[![Branch และ Script Path](./images/lab3_scm_07_branch_script_path_crop.png)](./images/lab3_scm_07_branch_script_path.png)')
R = R.replace('*ภาพที่ 12 Branch Specifier `*/main`, Script Path ของ `Jenkinsfile` แล็บนี้ และ **Lightweight checkout***',
              '*ภาพที่ 12 Branch Specifier `*/main`, Script Path `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile` และ **Lightweight checkout** ติ๊กอยู่ · ครอปจากภาพเต็มหน้าที่ต่อจากหลายช่วงเลื่อน แถบกลางภาพคือรอยต่อของภาพ (คลิกดูภาพเต็ม)*')
R = R.replace('> 📷 ภาพที่ 13–29 ถ่ายจากรอบทดสอบเดิมที่ใช้ `Jenkinsfile` เดียวกันแบบวางในช่อง Pipeline script ชื่อและลำดับ stage รวมถึง log ของแต่ละ stage เหมือนกับโหมด SCM',
              '> 📷 ภาพที่ 13–29 (ยกเว้นภาพที่ @HUB@ ที่เปิดดูภายหลัง) ถ่ายจากรอบทดสอบเดิม (2026-09-26) ที่วาง `Jenkinsfile` รุ่นก่อนหน้าในช่อง Pipeline script รุ่นนั้นยังไม่มี `skipDefaultCheckout()` แต่มี 8 stage ลำดับและพฤติกรรมเดียวกัน log ของแต่ละ stage จึงมีรูปแบบเดียวกับโหมด SCM')
# console excerpt: illustrative until the real post-push run replaces it (finalize_console.py)
old_hdr = R[R.index('✅ บรรทัดแรก ๆ ของ **Console Output**'):R.index('> build แรกอาจรอ')]
R = R.replace(old_hdr, '✅ บรรทัดแรก ๆ ของ **Console Output** บอกว่า Jenkins ดึง `Jenkinsfile` มาจาก Git แล้ว stage ถัดไปคือ **Connect** ทันที (ไม่มี `Declarative: Checkout SCM` เพราะ `skipDefaultCheckout()`) @CONSOLE@\n')
# ---- Docker Hub native screenshot after the existing tags figure
hub = R.index('🔍 **สืบย้อนได้ครบ:**')
R = R[:hub] + ('[![หน้า Tags พร้อมคำสั่ง docker pull](./images/lab3_scm_dockerhub_tags_crop.png)](./images/lab3_scm_dockerhub_tags.png)\n\n'
  '*ภาพที่ @HUB@ หน้า Tags เดียวกันเปิดภายหลังด้วย browser ของเครื่อง host: tag `lab3-sibling-20260926r2-2` digest `2b717397cbd2` และ `-1` digest `ea2559a94002` พร้อมคำสั่ง `docker pull tuchsanai/catfood-shop:<tag>` · เป็น tag ของรอบทดสอบ 2026-09-26 ไม่ใช่รอบทดสอบ SCM*\n\n') + R[hub:]
open(f'{W}/tmp/README.teach.md', 'w', encoding='utf-8').write(R)
print('ok')
