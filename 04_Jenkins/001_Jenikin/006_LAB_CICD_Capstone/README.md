# LAB 6 — CI/CD Capstone: Push ถึง Deploy

แล็บ 45 นาทีนี้รวมสิ่งที่เรียนจาก LAB 1–5 ให้เป็นวงเดียว: เมื่อ push โค้ด FastAPI เข้า Gitea แล้ว webhook จะสั่ง Jenkins ให้ test, build, push image ขึ้น Docker Hub, deploy และ verify อัตโนมัติ เมื่อจบแล้วนักศึกษาจะเห็นหน้าเว็บเปลี่ยนจาก v1 เป็น v2 โดยไม่ต้องกด build เอง

> **Prerequisite ก่อนคาบ:** Docker Hub repository `<DOCKER_USER>/cicd-webapp` ต้องสร้างเป็น **Public** ไว้แล้วพร้อมกับ `ci-demo` และ Access Token Read/Write ตามกล่องเตรียมตัวใน [LAB 3](../003_LAB_Docker_Build_Push/README.md) ถ้ายังไม่มีให้สร้างก่อนเริ่ม LAB 6

## ทฤษฎีก่อนลงมือ

วงจรเต็มของแล็บนี้คือ `push → webhook → pytest → docker build → push Hub → deploy → verify` รายละเอียดภาพรวมดู slide ตอนที่ 6 และวิดีโอ **Pipeline flow** ซึ่งแสดงไฟเขียวไล่จาก commit ไปถึง deployment ปลายทาง Jenkinsfile อยู่ใน repo เดียวกับแอป จึงทำให้โค้ดกับวิธีส่งมอบเปลี่ยนไปพร้อมกัน

Test ต้องเกิด **ก่อน push** เพราะ image ที่ test ไม่ผ่านไม่ควรกลายเป็น artifact ที่คนอื่นดึงไปใช้ ใน stage `Build-Test-Push` เราจึง build image ก่อน แล้วรัน `docker run --rm <image> pytest -q`; มีเพียงผลผ่านเท่านั้นที่ไปถึงคำสั่ง push ลำดับนี้ทำให้ console บอกได้ชัดว่า failure หยุดตรงไหน

แต่ละ build ใช้ tag `BUILD_NUMBER` ซึ่งไม่เปลี่ยนความหมายภายหลัง จึงใช้อ้าง deployment และย้อนดูหลักฐานได้ ส่วน `latest` เป็นชื่อสะดวกที่ชี้ build ใหม่สุด แล็บนี้ push ทั้งสอง tag และตัวตรวจจะยืนยันว่า digest ตรงกัน ไม่ใช้เพียงชื่อ tag เป็นหลักฐาน

Deploy ใช้วิธี recreate: ลบ container `webapp` เดิมแล้วรัน image tag ใหม่บน `cicd-net` จากนั้น Verify เรียก `http://webapp:8000` ผ่าน DNS ของ Docker network ไม่ใช่ localhost ระบบ production มักลด downtime ด้วย rolling หรือ canary deployment ซึ่งเรียนแล้วในชุด Traefik; ที่นี่ใช้ recreate เพื่อให้เห็นกลไกหลักใน 45 นาที

## 🎯 แล็บนี้ใน 30 วินาที

- สร้าง public Gitea repo `student/webapp` และ push แอปตัวอย่าง v1
- สร้าง `webapp-deploy` แบบ Pipeline from SCM พร้อม GWT token เฉพาะ job
- เพิ่ม webhook แล้วเห็น test, build, push, deploy และ verify เขียวครบ
- เปิด dashboard v1 จากนั้นเปลี่ยน VERSION/THEME และ push v2
- เห็นหน้าเปลี่ยนอัตโนมัติและ Docker Hub มี build tag ใหม่พร้อม `latest`

## สภาพตั้งต้น

ต้องมีสถานะจบ LAB 5: devtools, network `cicd-net`, Jenkins ที่มี Docker CLI/credential `dockerhub`, Gitea และ Generic Webhook Trigger 2.4.2 ต้องพร้อม โดย `hello-ci-pipeline` เดิมยังใช้ token `cicd2569-hello`

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
docker exec jenkins docker version --format '{{.Client.Version}}'
```

✅ **สิ่งที่ต้องเห็น** :

```text
jenkins    Up ...
gitea      Up ...
26.1.5
```

> ยังไม่มี? ย้อนไปทำ [LAB 5](../005_LAB_Webhook_Trigger/README.md) ก่อน (ใช้เวลา ~30 นาที) หรือกู้สถานะด้วย `bash tools/bootstrap/up_to_lab5.sh`

## การทดลองที่ 1 — Repo ของแอปควรอยู่ที่ไหน?

**คำถาม:** เราสร้าง public repo `student/webapp` ที่ Jenkins checkout โดยไม่ใช้ Git credential ได้หรือไม่?

เปิด `http://localhost:3000` แล้วลงชื่อเข้าใช้ `student / student2569`:

- กด **+ → New Repository** ตั้ง Repository Name เป็น `webapp`
- ไม่เลือก **Make Repository Private**, ตั้ง Default Branch เป็น `main` แล้วกด **Create Repository**

สำหรับ flow automation ของบทเรียน ใช้คำสั่งเดียว:

```bash
GITEA_BASE_URL=http://localhost:3000 python3 tools/ui/lab6_gitea_repo.py
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: student/webapp repository is public
[ui]... PASS
```

> 📝 ชื่อ repo ต้องเป็น `webapp` และ public ตรงตัว เพราะ SCM URL ใน job คือ `http://gitea:3000/student/webapp.git`

## การทดลองที่ 2 — ไฟล์ใดต้องเข้า repo?

**คำถาม:** แอป, tests, Dockerfile และ Jenkinsfile ถูก commit บน branch `main` ครบหรือไม่?

```bash
mkdir -p ~/webapp && cp -r 006_LAB_CICD_Capstone/app 006_LAB_CICD_Capstone/Dockerfile 006_LAB_CICD_Capstone/Jenkinsfile ~/webapp/
cd ~/webapp && git init -b main && git config user.name student && git config user.email student@example.com && git add . && git commit -m 'Deploy dashboard v1' && git remote add origin http://student:student2569@localhost:3000/student/webapp.git && git push -u origin main
```

✅ **สิ่งที่ต้องเห็น** :

```text
[main (root-commit) ...] Deploy dashboard v1
 * [new branch]      main -> main
```

## การทดลองที่ 3 — Job รู้ทั้ง SCM และ webhook ได้อย่างไร?

**คำถาม:** `webapp-deploy` checkout Jenkinsfile จาก Gitea และมี GWT token เฉพาะ job หรือไม่?

เปิด `http://localhost:8080` แล้วลงชื่อเข้าใช้ `admin / admin2569`:

- **New Item → webapp-deploy → Pipeline**
- เลือก **Generic Webhook Trigger**, ใส่ Token `cicd2569-webapp` — คนละ token กับ `cicd2569-hello`
- Definition = **Pipeline script from SCM**, SCM = **Git**, URL = `http://gitea:3000/student/webapp.git`, Branch = `*/main`, Script Path = `Jenkinsfile` แล้ว Save

รัน flow เดียวกันแบบตรวจ assertion ได้ด้วย:

```bash
JENKINS_BASE_URL=http://localhost:8080 python3 tools/ui/lab6_job.py
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: Pipeline from SCM uses the canonical Gitea URL and main branch
[ui]... assert: Generic Webhook Trigger token is cicd2569-webapp
[ui]... PASS
```

> 📝 Token แยกต่อ job สำคัญมาก: ถ้าใช้ `cicd2569-hello` ซ้ำ push ครั้งเดียวอาจยิงหลาย job โดยไม่ตั้งใจ

## การทดลองที่ 4 — Gitea จะบอก Jenkins URL ใด?

**คำถาม:** webhook ของ repo `webapp` ส่ง push event ไปหา Jenkins ด้วย DNS ภายในได้หรือไม่?

ใน Gitea repo `webapp` ไปที่ **Settings → Webhooks → Add Webhook → Gitea**:

- Target URL = `http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp`
- Content Type = `application/json`, Trigger On = **Push Events**, Active แล้วกด **Add Webhook**

หรือรัน UI automation:

```bash
GITEA_BASE_URL=http://localhost:3000 python3 tools/ui/lab6_webhook.py
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: active webapp webhook uses the canonical Jenkins URL
[ui]... PASS
```

## การทดลองที่ 5 — Push หนึ่งครั้งเดินครบวงหรือไม่?

**คำถาม:** push หลังมี webhook ทำให้ build แรกผ่าน test, push, deploy และ verify ครบหรือไม่?

```bash
cd ~/webapp && git commit --allow-empty -m 'Trigger v1 deployment' && git push origin main
JENKINS_BASE_URL=http://localhost:8080 python3 tools/ui/lab6_pipeline.py
```

✅ **สิ่งที่ต้องเห็น** :

```text
Build-Test-Push    SUCCESS
Deploy             SUCCESS
Verify             SUCCESS
3 passed
```

![Pipeline เต็มวงเขียวครบ](../slides_assets/lab6_pipeline_full.png)

## การทดลองที่ 6 — Deployment v1 บอกเราอะไร?

**คำถาม:** container ที่เพิ่ง deploy แสดง VERSION, BUILD_NUMBER, hostname และ theme สีน้ำเงินจริงหรือไม่?

```bash
curl -fsS http://localhost:8000/api/info
WEBAPP_BASE_URL=http://localhost:8000 EXPECTED_VERSION=1.0.0 EXPECTED_THEME=blue SCREENSHOT=slides_assets/lab6_app_v1.png python3 tools/ui/lab6_app.py
```

✅ **สิ่งที่ต้องเห็น** :

```json
{"version":"1.0.0","build_number":"1","theme":"blue","hostname":"..."}
```

![Deploy Dashboard v1 สีน้ำเงิน](../slides_assets/lab6_app_v1.png)

## การทดลองที่ 7 — Push v2 แล้วระบบทำอะไรเอง?

**คำถาม:** เมื่อเปลี่ยนสองตัวแปรแล้ว push ระบบสร้าง build ใหม่และหน้าเดิมเห็น deployment ใหม่ได้หรือไม่?

```bash
cd ~/webapp && sed -i 's/VERSION = "1.0.0"/VERSION = "2.0.0"/; s/THEME = "blue"/THEME = "green"/' app/main.py
git add app/main.py && git commit -m 'Release dashboard v2 green' && git push origin main
```

✅ **สิ่งที่ต้องเห็น** :

```text
To http://localhost:3000/student/webapp.git
   ...  main -> main
```

เปิด `http://localhost:8000` ค้างไว้: JavaScript จะถาม `/api/info` ทุก 5 วินาที เมื่อ build/deploy จบ หน้าเดิม reload แล้วแสดง v2 สีเขียวเอง

## การทดลองที่ 8 — จะปิดวงด้วยหลักฐานใด?

**คำถาม:** หน้า v2, Hub tags และ acceptance check ผูกกับ build ล่าสุดเดียวกันหรือไม่?

```bash
WEBAPP_BASE_URL=http://localhost:8000 EXPECTED_VERSION=2.0.0 EXPECTED_THEME=green SCREENSHOT=slides_assets/lab6_app_v2.png python3 tools/ui/lab6_app.py && DOCKER_USER=<id> JENKINS_BASE_URL=http://localhost:8080 python3 tools/ui/lab6_hub_tags.py
cd 006_LAB_CICD_Capstone && DOCKER_USER=<id> bash check.sh
```

✅ **สิ่งที่ต้องเห็น** :

```text
[ui]... assert: dashboard shows version 2.0.0 and green theme
[PASS] Hub build digest ตรง Jenkins, ใหม่กว่าเวลาเริ่ม build และ latest ชี้ digest เดียวกัน
[PASS] /health ตอบและ /api/info แสดง build_number ตรง build ล่าสุดผ่าน DNS webapp
ผลรวม: PASS
```

![Deploy Dashboard v2 สีเขียวและ BUILD_NUMBER ใหม่](../slides_assets/lab6_app_v2.png)

![Docker Hub Tags มี build ใหม่และ latest](../slides_assets/lab6_hub_tags.png)

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `pytest` fail แล้วไม่มี push | ตั้งใจให้ test เป็น quality gate ก่อน push | เปิด **Console Output**, หา `FAILED` แรกและชื่อ test แก้โค้ดแล้ว push ใหม่; อย่าย้าย test ไปหลัง push |
| Verify ล้มทั้งที่เปิดเว็บได้ | Pipeline ใช้ `localhost` ซึ่งหมายถึง Jenkins container | Jenkinsfile ต้องเรียก `http://webapp:8000/health` และ `/api/info` ผ่าน `cicd-net` ตาม F-03 |
| webhook ไม่ยิง | token คนละค่า, URL ใช้ localhost หรือ hook ไม่ Active | เทียบ `cicd2569-webapp`, URL canonical แล้วดู **Recent Deliveries** ต้องตอบ 2xx |
| หน้าเว็บไม่เปลี่ยน | build ยังไม่จบหรือ browser cache หน้าเดิม | รอ stage Verify เขียว; auto-refresh ตรวจทุก 5 วินาทีอยู่แล้ว หรือกด hard refresh หนึ่งครั้ง |
| `401 Unauthorized` ตอน login/push | token ผิด, หมดอายุ หรือถูก revoke | ทำตามตาราง 401 ใน [LAB 3](../003_LAB_Docker_Build_Push/README.md) และอัปเดต credential `dockerhub` |
| `denied: requested access` ตอน push | namespace/repo ผิดหรือ token ไม่มี Write | ตรวจ public repo `<DOCKER_USER>/cicd-webapp` และ PAT Read/Write ตามตาราง LAB 3 |
| restart devtools แล้ว service หาย | outer container หรือ inner service ไม่มี restart policy | `docker start devtools-jenkins`, รอ ~20 วินาที แล้ว `docker ps`; หากต้องกู้ใช้ `bash tools/bootstrap/up_to_lab5.sh` |
