# LAB 6 — CI/CD Capstone: Push ถึง Deploy

แล็บ 45 นาทีนี้บูรณาการสิ่งที่เรียนจาก LAB 1–5 เป็นวงจรเดียว เมื่อ push โค้ด FastAPI เข้า Gitea แล้ว webhook จะสั่ง Jenkins ให้ทดสอบ สร้างและเผยแพร่ image จากนั้น deploy และ verify โดยอัตโนมัติ เมื่อจบแล็บ นักศึกษาจะพิสูจน์การเปลี่ยน dashboard จาก v1 เป็น v2 ด้วย build และ Docker Hub tag ที่สัมพันธ์กันได้

> **Prerequisite ก่อนคาบ:** ต้องมี Docker Hub repository `<DOCKER_USER>/cicd-webapp` และ `<DOCKER_USER>/ci-demo` แบบ **Public** พร้อม Access Token สิทธิ์ Read/Write ตาม [LAB 3](../003_LAB_Docker_Build_Push/README.md) หากยังไม่พร้อม ให้ดำเนินการให้ครบก่อนเริ่ม LAB 6

> **ข้อควรระวังด้านความปลอดภัย:** environment นี้เป็นแล็บ disposable ที่ใช้ privileged container และ Docker socket ซึ่งมีอำนาจใกล้เคียง root เท่านั้น ระบบ production ควรใช้ isolated agent, สิทธิ์ขั้นต่ำ และ secret manager; Access Token ควรจำกัดเป็น Read/Write และ revoke หลังคาบ

## ทฤษฎีก่อนลงมือ

วงจรของ capstone คือ `push → webhook → pytest → docker build → push Hub → deploy → verify` รายละเอียดภาพรวมดู slide ตอนที่ 6 และวิดีโอ **Pipeline flow** Jenkinsfile อยู่ใน repository เดียวกับ application จึงทำให้โค้ดและกระบวนการส่งมอบเปลี่ยนแปลงภายใต้ revision เดียวกัน

การทดสอบต้องเกิดก่อนเผยแพร่ image เพราะ artifact ที่ไม่ผ่าน quality gate ไม่ควรถูกนำไป deploy stage `Build-Test-Push` จึง build image แล้วรัน `pytest` ภายใน image ก่อนดำเนินการ push หากการทดสอบล้มเหลว pipeline จะหยุดใน stage นี้

แต่ละ build ใช้ tag `BUILD_NUMBER` เป็นตัวระบุแบบไม่เปลี่ยนความหมายภายหลัง ส่วน `latest` เป็นชื่ออ้างอิง build ล่าสุด แล็บนี้เผยแพร่ทั้งสอง tag และตรวจว่า digest ตรงกัน เพื่อป้องกันการสรุปผลจาก tag เก่าที่ไม่เกี่ยวกับ run ปัจจุบัน

ส่วน push ต้องรักษารูปแบบ canonical: ใช้ Groovy single-quoted string, ปิด shell tracing ด้วย `set +x`, login ก่อน build, ใช้ `DOCKER_CONFIG` ชั่วคราว และลบ credential ด้วย `trap` เสมอ Jenkins masking ช่วยลดโอกาสรั่วใน console แต่ไม่ใช่การรับประกัน จึงห้ามพิมพ์ token ลงคำสั่งหรือไฟล์

```groovy
withCredentials([usernamePassword(credentialsId: 'dockerhub',
    usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
  sh '''set +x
    export DOCKER_CONFIG=$(mktemp -d)
    trap 'docker logout >/dev/null 2>&1; rm -rf "$DOCKER_CONFIG"' EXIT
    echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
    docker build -t docker.io/$DOCKER_USER/cicd-webapp:$BUILD_NUMBER .
    docker run --rm docker.io/$DOCKER_USER/cicd-webapp:$BUILD_NUMBER pytest -q
    docker push docker.io/$DOCKER_USER/cicd-webapp:$BUILD_NUMBER
    docker tag docker.io/$DOCKER_USER/cicd-webapp:$BUILD_NUMBER docker.io/$DOCKER_USER/cicd-webapp:latest
    docker push docker.io/$DOCKER_USER/cicd-webapp:latest
  '''
}
```

การ deploy ใช้วิธี recreate container `webapp` บน network `cicd-net` แล้ว stage Verify เรียก `http://webapp:8000` ผ่าน Docker DNS ไม่ใช่ `localhost` ระบบ production มักใช้ rolling หรือ canary deployment เพื่อลด downtime แต่แล็บนี้ใช้ recreate เพื่อเน้นกลไก CI/CD หลัก

## 🎯 ขอบเขตและผลลัพธ์การเรียนรู้

- สร้าง public repository `student/webapp` และจัดเก็บ application, tests, Dockerfile และ Jenkinsfile บน branch `main`
- กำหนด job `webapp-deploy` แบบ Pipeline from SCM พร้อม token `cicd2569-webapp`
- เชื่อม Gitea webhook กับ Jenkins และตรวจว่า pipeline ผ่านทุก stage
- ตรวจ dashboard v1 แล้วเปลี่ยน `VERSION` และ `THEME` เพื่อ deploy v2 อัตโนมัติ
- ยืนยัน build ล่าสุดด้วยหน้า Docker Hub public tags และ acceptance check

## สภาพตั้งต้น

ต้องมีสถานะจบ LAB 5: network `cicd-net`, Jenkins ที่มี Docker CLI และ credential `dockerhub`, Gitea และ Generic Webhook Trigger 2.4.2 ต้องพร้อม โดย `hello-ci-pipeline` เดิมยังใช้ token `cicd2569-hello`

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
docker exec jenkins docker version --format '{{.Client.Version}}'
```

✅ **สิ่งที่ต้องเห็น** :

```text
jenkins    Up ...
gitea      Up ...
29.7.2
```

> ยังไม่มี? ย้อนไปทำ [LAB 5](../005_LAB_Webhook_Trigger/README.md) ก่อน (ใช้เวลา ~30 นาที) หรือกู้สถานะด้วย `(cd "$COURSE_ROOT" && bash tools/bootstrap/up_to_lab5.sh)`

## การทดลองที่ 1 — Repository ของ application ควรอยู่ที่ใด?

**คำถาม:** สามารถสร้าง public repository `student/webapp` ที่ Jenkins checkout โดยไม่ใช้ Git credential ได้หรือไม่?

Public repository ทำให้ Jenkins อ่าน source code ผ่าน SCM URL ภายในได้โดยไม่ต้องเพิ่ม credential อีกชุด ขั้นนี้กำหนดชื่อและ branch ให้ตรงกับ contract ของ pipeline

1. เปิด `http://localhost:3000` แล้วลงชื่อเข้าใช้ด้วย `student / student2569`
2. เลือก **+ → New Repository**
3. กำหนด **Repository Name** เป็น `webapp` และไม่เลือก **Make Repository Private**
4. กำหนด **Default Branch** เป็น `main` แล้วเลือก **Create Repository**

![ฟอร์มสร้าง public repository webapp ใน Gitea](../slides_assets/lab6_s01_gitea_repo_form.png)

*ภาพที่ 1 ฟอร์ม New Repository แสดง owner `student`, ชื่อ `webapp` และไม่เลือกสถานะ private*

> **ทางเลือกอัตโนมัติ (รันจากเครื่อง host ของผู้สอน):** helper ใต้ `tools/ui` ใช้ Playwright ซึ่งไม่มีใน devtools image นักศึกษาจึงทำขั้น UI ตามรายการของแต่ละการทดลอง ส่วนผู้สอนที่ติดตั้ง Playwright และมี course tree บน host ให้กำหนด `COURSE_ROOT` บน host ก่อนใช้คำสั่งอัตโนมัติใน LAB นี้

รัน UI automation จาก host เพื่อสร้าง repository และตรวจ assertion เดียวกันได้ดังนี้

```bash
(cd "$COURSE_ROOT" && GITEA_BASE_URL=http://localhost:3000 python3 tools/ui/lab6_gitea_repo.py)
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: student/webapp repository is public
[ui]... PASS
```

> 📝 ชื่อ repository ต้องเป็น `webapp` และเป็น public เพราะ SCM URL ของ job คือ `http://gitea:3000/student/webapp.git`

ขณะนี้ Gitea มี repository ว่างพร้อม branch `main` ขั้นถัดไปจะนำ source code ของ v1 เข้า repository นี้

## การทดลองที่ 2 — ไฟล์ใดต้องอยู่ใน repository?

**คำถาม:** application, tests, Dockerfile และ Jenkinsfile ถูก commit บน branch `main` ครบหรือไม่?

Pipeline from SCM ต้องอ่านทั้ง source code และคำสั่งส่งมอบจาก revision เดียวกัน จึงคัดลอกไฟล์ capstone ทั้งหมดก่อนสร้าง initial commit และ push ไปยัง Gitea

```bash
mkdir -p ~/webapp && cp -r "$COURSE_ROOT/006_LAB_CICD_Capstone/app" "$COURSE_ROOT/006_LAB_CICD_Capstone/Dockerfile" "$COURSE_ROOT/006_LAB_CICD_Capstone/Jenkinsfile" ~/webapp/
cd ~/webapp && git init -b main && git config user.name student && git config user.email student@example.com && git add . && git commit -m 'Deploy dashboard v1' && git remote add origin http://student:student2569@localhost:3000/student/webapp.git && git push -u origin main
```

✅ **สิ่งที่ต้องเห็น** :

```text
[main (root-commit) ...] Deploy dashboard v1
 * [new branch]      main -> main
```

ตรวจโครงสร้าง repository ผ่าน UI ดังนี้

1. เปิด `http://localhost:3000/student/webapp`
2. เลือกแท็บ **Code** และตรวจว่า branch เป็น `main`
3. ตรวจรายการ `app/`, `Jenkinsfile` และ `Dockerfile`

![Repository webapp หลัง push source code](../slides_assets/lab6_s02_gitea_repo_after_push.png)

*ภาพที่ 2 หน้า Code ของ `student/webapp` แสดง `app/`, `Jenkinsfile` และ `Dockerfile` บน branch `main`*

ขณะนี้ source code พร้อมให้ Jenkins checkout ขั้นถัดไปจะสร้าง job ที่อ่าน Jenkinsfile จาก repository นี้

## การทดลองที่ 3 — Job เชื่อม SCM และ webhook อย่างไร?

**คำถาม:** `webapp-deploy` checkout Jenkinsfile จาก Gitea และใช้ GWT token เฉพาะ job ได้หรือไม่?

Pipeline from SCM แยกการกำหนด job ออกจากเนื้อหา pipeline โดย Jenkins จะ checkout `Jenkinsfile` ทุกครั้ง ส่วน token เฉพาะ job ป้องกัน push เดียวกันไป trigger job อื่นโดยไม่ตั้งใจ

1. เปิด `http://localhost:8080` แล้วลงชื่อเข้าใช้ด้วย `admin / admin2569`
2. เลือก **New Item**, ระบุ `webapp-deploy`, เลือก **Pipeline** แล้วเลือก **OK**
3. ใน **Triggers** เลือก **Generic Webhook Trigger** และระบุ Token เป็น `cicd2569-webapp`
4. ใน **Pipeline** กำหนด Definition เป็น **Pipeline script from SCM** และ SCM เป็น **Git**
5. ระบุ URL `http://gitea:3000/student/webapp.git`, Branch `*/main`, Script Path `Jenkinsfile` แล้วเลือก **Save**

![SCM configuration ของ job webapp-deploy](../slides_assets/lab6_s03_job_scm.png)

*ภาพที่ 3 Pipeline from SCM แสดง Git URL canonical และ branch `*/main` โดยไม่ใช้ credential*

![Trigger token ของ job webapp-deploy](../slides_assets/lab6_s04_job_trigger.png)

*ภาพที่ 4 Generic Webhook Trigger แสดง token `cicd2569-webapp` ที่แยกจาก job ใน LAB 5*

รัน UI automation เพื่อตั้งค่าและตรวจค่าที่บันทึกได้ดังนี้

```bash
(cd "$COURSE_ROOT" && JENKINS_BASE_URL=http://localhost:8080 python3 tools/ui/lab6_job.py)
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: Pipeline from SCM uses the canonical Gitea URL and main branch
[ui]... assert: Generic Webhook Trigger token is cicd2569-webapp
[ui]... PASS
```

> 📝 Token ต้องเป็น `cicd2569-webapp` ไม่ใช่ `cicd2569-hello`; การใช้ token ซ้ำอาจทำให้ push ครั้งเดียว trigger หลาย job

ขณะนี้ Jenkins พร้อมรับ event แต่ Gitea ยังไม่ทราบปลายทาง ขั้นถัดไปจะเพิ่ม webhook ให้ repository `webapp`

## การทดลองที่ 4 — Gitea ต้องส่ง event ไปยัง URL ใด?

**คำถาม:** webhook ของ `webapp` ส่ง push event ไปหา Jenkins ผ่าน DNS ภายในได้หรือไม่?

Gitea และ Jenkins อยู่บน `cicd-net` จึงต้องใช้ชื่อ service `jenkins` ใน Target URL การใช้ `localhost` จะอ้างถึง Gitea container เองและไม่ถึง Jenkins

1. เปิด repository `webapp` แล้วเลือก **Settings → Webhooks → Add Webhook → Gitea**
2. ระบุ Target URL เป็น `http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp`
3. กำหนด Content Type เป็น `application/json`, Trigger On เป็น **Push Events** และเปิด **Active**
4. เลือก **Add Webhook** แล้วกลับมาตรวจรายการ webhook

![Gitea webhook ของ repository webapp](../slides_assets/lab6_s05_gitea_webhook.png)

*ภาพที่ 5 หน้า Webhooks แสดง active endpoint ของ Jenkins พร้อม token canonical*

รัน UI automation เพื่อสร้างและตรวจ webhook ได้ดังนี้

```bash
(cd "$COURSE_ROOT" && GITEA_BASE_URL=http://localhost:3000 python3 tools/ui/lab6_webhook.py)
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: active webapp webhook uses the canonical Jenkins URL
[ui]... PASS
```

ขณะนี้ repository และ job เชื่อมกันครบ ขั้นถัดไปจะสร้าง push event สำหรับ deployment v1

## การทดลองที่ 5 — Push ครั้งแรกเดินครบวงหรือไม่?

**คำถาม:** push หลังเพิ่ม webhook ทำให้ build แรกผ่าน test, push, deploy และ verify ครบหรือไม่?

Empty commit สร้าง push event โดยไม่เปลี่ยน source code ทำให้แยกการทดสอบ wiring ของ webhook ออกจากการเปลี่ยน application ได้ชัดเจน จากนั้น UI automation จะรอ build ที่เกิดจาก webhook และตรวจลำดับ stage กับ console

```bash
cd ~/webapp && git commit --allow-empty -m 'Trigger v1 deployment' && git push origin main
```

จากนั้นรอและตรวจ pipeline ด้วย helper บน host ของผู้สอน:

```bash
(cd "$COURSE_ROOT" && JENKINS_BASE_URL=http://localhost:8080 python3 tools/ui/lab6_pipeline.py)
```

✅ **สิ่งที่ต้องเห็น** :

```text
Build-Test-Push    SUCCESS
Deploy             SUCCESS
Verify             SUCCESS
3 passed, 1 warning in ...
```

ตรวจผลผ่าน Jenkins UI ดังนี้

1. เปิด `http://localhost:8080/job/webapp-deploy/lastBuild/stages/`
2. ตรวจว่า **Checkout SCM**, **Build-Test-Push**, **Deploy** และ **Verify** เป็นสีเขียว
3. เปิด **Console Output** แล้วค้นหา `3 passed` และ `http://webapp:8000/health`

![Pipeline graph ของ build แรก](../slides_assets/lab6_s06_pipeline_graph.png)

*ภาพที่ 6 Pipeline Graph ของ build #1 แสดงทุก stage สำเร็จและ Verify เรียก URL ภายในที่ถูกต้อง*

![Console ช่วง pytest ผ่าน](../slides_assets/lab6_s07_console_pytest.png)

*ภาพที่ 7 Console ของ build #1 แสดง `3 passed` ก่อนข้อความเริ่ม push image*

![Console ช่วง Verify](../slides_assets/lab6_s08_console_verify.png)

*ภาพที่ 8 Console ของ build #1 แสดง stage Verify เรียก `http://webapp:8000` และจบด้วย SUCCESS*

ขณะนี้ build #1 deploy application v1 แล้ว ขั้นถัดไปจะตรวจข้อมูลที่ container เผยแพร่จริง

## การทดลองที่ 6 — Deployment v1 แสดงข้อมูลใด?

**คำถาม:** container ที่ deploy แล้วแสดง VERSION, BUILD_NUMBER, hostname และ theme สีน้ำเงินตรงกับ build แรกหรือไม่?

Endpoint `/api/info` เป็นหลักฐานแบบ machine-readable ส่วน dashboard ทำให้ผู้ใช้เห็น version, build และ theme ในบริบทเดียวกัน การตรวจทั้งสองรูปแบบช่วยยืนยันว่า service ที่ port 8000 คือ deployment ล่าสุด

```bash
curl -fsS http://localhost:8000/api/info
```

ตรวจ dashboard ผ่าน browser automation บน host ของผู้สอน:

```bash
(cd "$COURSE_ROOT" && WEBAPP_BASE_URL=http://localhost:8000 EXPECTED_VERSION=1.0.0 EXPECTED_THEME=blue SCREENSHOT=slides_assets/lab6_s09_dashboard_v1.png python3 tools/ui/lab6_app.py)
```

✅ **สิ่งที่ต้องเห็น** :

```json
{"version":"1.0.0","build_number":"1","theme":"blue","hostname":"..."}
```

1. เปิด `http://localhost:8000`
2. ตรวจหัวข้อ `v1.0.0`, ค่า `BUILD #1`, theme `blue` และ container hostname
3. เปิดหน้านี้ค้างไว้เพื่อสังเกต auto-refresh ในการทดลองถัดไป

![Deploy Dashboard v1 สีน้ำเงิน](../slides_assets/lab6_s09_dashboard_v1.png)

*ภาพที่ 9 Dashboard v1 แสดง VERSION `1.0.0`, BUILD `#1`, theme `blue` และ hostname ของ container*

ขณะนี้ browser แสดง v1 และตรวจ `/api/info` ทุก 5 วินาที ขั้นถัดไปจะเปลี่ยน source code แล้วสังเกต deployment ใหม่บนหน้าเดิม

## การทดลองที่ 7 — Push v2 เปลี่ยน deployment อัตโนมัติหรือไม่?

**คำถาม:** เมื่อเปลี่ยน `VERSION` และ `THEME` แล้ว push ระบบสร้าง build ใหม่และหน้าเดิมแสดง deployment v2 ได้หรือไม่?

การเปลี่ยนสองค่าทำให้ผลของ revision ใหม่สังเกตได้ชัด เมื่อ push แล้ว webhook จะเริ่ม pipeline โดยไม่ต้องกด Build Now และ JavaScript บนหน้าเดิมจะ reload เมื่อ `/api/info` รายงาน version ใหม่

```bash
cd ~/webapp && sed -i 's/VERSION = "1.0.0"/VERSION = "2.0.0"/; s/THEME = "blue"/THEME = "green"/' app/main.py
git add app/main.py && git commit -m 'Release dashboard v2 green' && git push origin main
```

✅ **สิ่งที่ต้องเห็น** :

```text
To http://localhost:3000/student/webapp.git
   ...  main -> main
```

1. กลับไปยัง browser ที่เปิด `http://localhost:8000` ค้างไว้
2. รอ pipeline จบโดยไม่ refresh เอง; หน้าเดิมจะเปลี่ยนภายในรอบตรวจ 5 วินาที
3. ตรวจหัวข้อ `v2.0.0`, ค่า `BUILD #2` และ theme `green`

![Deploy Dashboard v2 หลัง push](../slides_assets/lab6_s10_dashboard_v2.png)

*ภาพที่ 10 หน้า browser เดิมหลัง auto-refresh แสดง VERSION `2.0.0`, BUILD `#2` และ theme `green`*

ขณะนี้ deployment v2 ทำงานแล้ว ขั้นสุดท้ายจะผูกหน้าเว็บกับ tag ที่เผยแพร่จาก build เดียวกัน

## การทดลองที่ 8 — หลักฐานใดปิดวง CI/CD ได้ครบ?

**คำถาม:** Docker Hub public tags และ acceptance check ยืนยัน build ล่าสุดเดียวกับ deployment v2 ได้หรือไม่?

หน้า public tags แสดงผล push โดยไม่เปิดเผยสถานะ login ส่วน acceptance check เปรียบเทียบ Jenkins digest, เวลาอัปเดต Hub, tag `2` กับ `latest`, webhook delivery และข้อมูลจาก `http://webapp:8000`

1. เปิด `https://hub.docker.com/r/<DOCKER_USER>/cicd-webapp/tags` ในหน้าต่างที่ไม่ได้ login
2. ตรวจชื่อ repository และ tag `2` กับ `latest`
3. ห้าม capture หน้า Docker Hub ที่ login แล้วหรือหน้าสร้าง Access Token

![Docker Hub public tags ของ build ล่าสุด](../slides_assets/lab6_s11_hub_public_tags.png)

*ภาพที่ 11 หน้า public tags แบบ anonymous แสดง tag `2` และ `latest` ซึ่งมี digest เดียวกัน*

รัน automation สำหรับหน้า public tags จาก host ของผู้สอน:

```bash
(cd "$COURSE_ROOT" && DOCKER_USER='<DOCKER_USER>' JENKINS_BASE_URL=http://localhost:8080 python3 tools/ui/lab6_hub_tags.py)
```

จากนั้นปิดวงด้วย acceptance check ภายใน devtools:

```bash
(cd "$COURSE_ROOT/006_LAB_CICD_Capstone" && DOCKER_USER='<DOCKER_USER>' bash check.sh)
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: new build tag 2
[PASS] Hub build digest ตรง Jenkins, ใหม่กว่าเวลาเริ่ม build และ latest ชี้ digest เดียวกัน
[PASS] /health ตอบและ /api/info แสดง build_number ตรง build ล่าสุดผ่าน DNS webapp
ผลรวม: PASS
```

> 📝 คำสั่งตรวจใช้เฉพาะ `<DOCKER_USER>` และไม่รับ token; หน้า Hub ต้องเป็น public tags แบบ anonymous เท่านั้น

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `pytest` fail แล้วไม่มี push | Test ทำหน้าที่เป็น quality gate ก่อนเผยแพร่ image | เปิด **Console Output**, หา `FAILED` แรกและชื่อ test แก้ source code แล้ว push ใหม่ โดยไม่ย้าย test ไปหลัง push |
| Verify ล้มทั้งที่เปิดเว็บได้ | Pipeline ใช้ `localhost` ซึ่งหมายถึง Jenkins container | Jenkinsfile ต้องเรียก `http://webapp:8000/health` และ `/api/info` ผ่าน `cicd-net` |
| webhook ไม่ trigger | token ไม่ตรง, URL ใช้ localhost หรือ webhook ไม่ Active | ตรวจ `cicd2569-webapp`, URL canonical และ **Recent Deliveries** ซึ่งต้องตอบ 2xx |
| หน้าเว็บไม่เปลี่ยน | build ยังไม่จบหรือ browser ไม่ได้ตรวจข้อมูลใหม่ | รอ stage Verify เป็นสีเขียว แล้วตรวจว่า auto-refresh ทำงานทุก 5 วินาที หรือ hard refresh หนึ่งครั้ง |
| `401 Unauthorized` ตอน login หรือ push | token ผิด หมดอายุ หรือถูก revoke | ทำตามตาราง 401 ใน [LAB 3](../003_LAB_Docker_Build_Push/README.md) และอัปเดต credential `dockerhub` |
| `denied: requested access` ตอน push | namespace/repository ผิดหรือ token ไม่มี Write | ตรวจ public repository `<DOCKER_USER>/cicd-webapp` และ Access Token สิทธิ์ Read/Write |
| `429` จาก Docker Hub | ถึง pull limit หรือ abuse limit | ตรวจข้อความตอบกลับ แยกชนิด limit แล้วรอตามเวลาที่ Hub ระบุ; canonical push block ต้อง login ก่อน build |
| หน้า tags ว่างหรือ 404 | repository เป็น private หรือ URL ผิด | ตรวจว่า `<DOCKER_USER>/cicd-webapp` เป็น public และเปิด path `/tags` แบบไม่ login |
| restart devtools แล้ว service หาย | outer container หรือ inner service ไม่กลับมาทำงาน | `docker start devtools-jenkins`, รอประมาณ 20 วินาทีแล้วรัน `docker ps`; หากต้องกู้สถานะใช้ `(cd "$COURSE_ROOT" && bash tools/bootstrap/up_to_lab5.sh)` |
