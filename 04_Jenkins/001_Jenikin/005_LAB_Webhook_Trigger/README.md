# LAB 5 — Push แล้ว Build ทันทีด้วย Webhook

แล็บ 30 นาทีนี้ตอบคำถามว่าเราจะเปลี่ยนจาก Jenkins คอยถาม Git ทุกนาทีเป็น Gitea แจ้ง Jenkins ทันทีเมื่อมี `push` ได้อย่างไร เมื่อจบแล้ว `hello-ci-pipeline` จะ build อัตโนมัติจาก webhook พร้อมหลักฐาน delivery, payload และ build cause

## ทฤษฎีก่อนลงมือ

Webhook คือการแจ้งเหตุการณ์แบบ **push model**: เมื่อ Gitea รับ commit ใหม่ มันส่ง HTTP POST พร้อม payload ไปยัง endpoint ของ Jenkins ทันที ผู้รับไม่ต้องถามซ้ำ ๆ จึงตอบสนองเร็วและไม่มี request ตอนที่ repository เงียบ ดูภาพเปรียบเทียบและวิดีโอ `polling vs webhook` ในสไลด์ **ตอนที่ 5**

Poll SCM เป็น **pull model**: Jenkins ตั้งเวลาแล้วถาม Git ว่า revision เปลี่ยนหรือยัง ข้อดีคือไม่ต้องเปิด endpoint ให้ระบบต้นทางเรียก แต่มีช่วงหน่วงสูงสุดตามรอบ polling และเกิด request แม้ไม่มีงานใหม่ LAB 4 ใช้ `* * * * *`; LAB นี้จะปิด polling แล้วให้ Gitea เป็นฝ่ายแจ้ง

Generic Webhook Trigger plugin เพิ่ม endpoint กลาง `/generic-webhook-trigger/invoke` และเลือก job ด้วย token ตามสัญญา I-05 เราใช้ `cicd2569-hello` เฉพาะ `hello-ci-pipeline` เพราะถ้าหลาย job ใช้ token เดียวกัน การเรียกหนึ่งครั้งจะยิงโดนทุก job ที่ใช้ token นั้น ไม่ใช่การแบ่งงานตามชื่อ repository ให้อัตโนมัติ

Gitea รันด้วย `GITEA__webhook__ALLOWED_HOST_LIST=private` ตั้งแต่เริ่ม container ใน LAB 4 เพื่ออนุญาตปลายทาง private network เช่น `jenkins` บน `cicd-net` แต่ไม่เปิดกว้างทุก host การ allow-list นี้ป้องกันไม่ให้ผู้ใช้ตั้ง webhook ให้ server ไปเรียกปลายทาง arbitrary บนอินเทอร์เน็ตหรือทรัพยากรที่ไม่ตั้งใจ

> **Safety:** token webhook คือรหัสเปิดประตูให้สั่ง build แล็บนี้ใช้ค่าคงที่เพื่อ copy-paste ง่าย; production ต้องสุ่มค่าแรง แยก token/credential ต่อ job จำกัด scope/เครือข่าย และเก็บด้วยระบบ secrets ส่วน `ALLOWED_HOST_LIST=private` จำกัดพื้นที่ปลายทางแทน wildcard แต่ยังควรใช้ least privilege และแยก build agent

## 🎯 แล็บนี้ใน 30 วินาที

- ติดตั้ง Generic Webhook Trigger 2.4.2 แล้ว restart Jenkins
- ปิด Poll SCM และใส่ token เฉพาะ `hello-ci-pipeline`
- เรียก endpoint ตรงเพื่อพิสูจน์ว่า token เลือก job ถูก
- เพิ่ม Gitea webhook และอ่าน delivery HTTP 200
- push commit จริง จับเวลา และตรวจ build cause/payload
- รัน `check.sh` ตรวจสถานะจบแล็บ

## สภาพตั้งต้น

ต้องมีสถานะจบ LAB 4: devtools ยังทำงาน และ inner container `jenkins`, `gitea` อยู่บน `cicd-net`; job `hello-ci-pipeline` checkout `student/hello-ci` branch `main` สำเร็จและยังเปิด Poll SCM

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
```

✅ **สิ่งที่ต้องเห็น** :

```text
jenkins    Up ...
gitea      Up ...
```

> ยังไม่มี? ย้อนไปทำ [LAB 4](../004_LAB_Pipeline_From_Git/README.md) ก่อน (ใช้เวลา ~40 นาที) หรือกู้สถานะด้วย `bash tools/bootstrap/up_to_lab4.sh`

## การทดลองที่ 1 — Jenkins รับ webhook ได้อย่างไร

**คำถาม:** plugin รุ่นใดเพิ่ม Generic Webhook Trigger ให้ job และเรารู้ได้อย่างไรว่า restart เสร็จแล้ว?

- เปิด `http://localhost:8080` แล้วไป **Manage Jenkins → Plugins → Available plugins**
- ค้นหา **Generic Webhook Trigger** ตรวจว่าเป็นรุ่น **2.4.2** แล้วเลือก **Install**
- หน้า installation progress เลือก **Restart Jenkins when installation is complete and no jobs are running**
- รอหน้า Jenkins หายไปชั่วครู่ แล้วใช้คำสั่งนี้รอจน login page กลับมา

```bash
until curl -fsS http://localhost:8080/login >/dev/null; do sleep 2; done
```

✅ **สิ่งที่ต้องเห็น** :

```text
Generic Webhook Trigger 2.4.2    Enabled
```

> 📝 ถ้าหน้า restart ค้าง อย่ากดซ้ำหลายครั้ง ให้รอด้วย `curl` ก่อน แล้วค่อยดูวิธีแก้ปัญหาท้ายแล็บ

## การทดลองที่ 2 — จะเปลี่ยนจาก polling เป็น webhook โดยไม่แก้ Jenkinsfile อย่างไร

**คำถาม:** trigger ของ `hello-ci-pipeline` ต้องตั้งค่าอย่างไรให้ webhook เลือก job นี้เพียงตัวเดียว?

- ไปที่ **hello-ci-pipeline → Configure → Build Triggers**
- เอาเครื่องหมาย **Poll SCM** ออก
- เลือก **Generic Webhook Trigger** แล้วใส่ **Token** = `cicd2569-hello`
- กด **Save**

✅ **สิ่งที่ต้องเห็น** :

```text
Poll SCM: off
Generic Webhook Trigger: on
Token: cicd2569-hello
```

> 📝 Trigger ที่ตั้งผ่าน job UI มีผลทันทีเมื่อ Save ไม่ต้อง Build Now หรือ seed-build ก่อนทดสอบ endpoint

## การทดลองที่ 3 — token เลือก job ถูกจริงไหม

**คำถาม:** ก่อนต่อ Gitea เราจะทดสอบ endpoint ตรงจาก devtools shell ได้อย่างไร?

```bash
curl -s 'http://localhost:8080/generic-webhook-trigger/invoke?token=cicd2569-hello'
```

✅ **สิ่งที่ต้องเห็น** :

```json
{"jobs":{"hello-ci-pipeline":{"triggered":true}},"message":"Triggered jobs."}
```

ค่าจริงมี field รายละเอียดเพิ่ม เช่น queue id แต่ต้องเห็น `hello-ci-pipeline`, `triggered:true` และ `Triggered jobs.`

## การทดลองที่ 4 — Gitea ส่ง delivery ถึง Jenkins ได้ไหม

**คำถาม:** URL ใดทำให้ Gitea container เรียก Jenkins container ผ่าน `cicd-net` ได้?

- เปิด `http://localhost:3000` แล้วไป **student/hello-ci → Settings → Webhooks → Add Webhook → Gitea**
- ใส่ Target URL: `http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello`
- คง **POST Content Type = application/json**, **Active** และ **Push Events** แล้วกด **Add Webhook**
- เปิด webhook ที่สร้าง กด **Test Push Event** แล้วคลิก delivery ล่าสุดเพื่อดูแท็บ **Response**

![หน้า Add Webhook ใน Gitea](../slides_assets/lab5_webhook_config.png)

✅ **สิ่งที่ต้องเห็น** :

```text
HTTP Status: 200
Response: ... "hello-ci-pipeline" ... "Triggered jobs."
```

![Delivery HTTP 200 และ response จาก Jenkins](../slides_assets/lab5_delivery.png)

> 📝 ใน URL นี้ `jenkins` คือ DNS ของ container บน `cicd-net`; `localhost` ใน Gitea หมายถึง Gitea เอง จึงใช้แทนกันไม่ได้

## การทดลองที่ 5 — push จริงเร็วกว่า polling แค่ไหน

**คำถาม:** เมื่อแก้ไฟล์แล้ว push Jenkins จะเห็น build ใหม่ในกี่วินาที และรู้ได้อย่างไรว่ามาจาก webhook?

```bash
LAB5_WORKDIR=$(mktemp -d) && git clone http://student:student2569@localhost:3000/student/hello-ci.git "$LAB5_WORKDIR/hello-ci"
cd "$LAB5_WORKDIR/hello-ci" && git config user.name student && git config user.email student@example.com && date -u +"webhook proof %Y-%m-%dT%H:%M:%SZ" >> webhook-proof.txt && git add webhook-proof.txt && git commit -m 'Verify immediate webhook build' && time git push origin main
```

เปิด **Jenkins → hello-ci-pipeline** ทันที จับเวลาจาก `git push` ถึง build ใหม่ปรากฏ แล้วเปิด build ล่าสุดดูข้อความ cause และ Console Output

✅ **สิ่งที่ต้องเห็น** :

```text
new build #6 detected 10.54s after push
build #6 = SUCCESS
cause: Generic Cause
```

ผลจริงของเครื่องทดสอบคือ 10.54 วินาที ซึ่งเกิดทันทีตาม event และไม่ต้องรอหน้าต่าง 0–60 วินาทีของ Poll SCM ใน LAB 4 เลข build และเวลาของแต่ละเครื่องอาจต่างกัน

![Build ที่เกิดอัตโนมัติและ cause จาก webhook](../slides_assets/lab5_auto_build.png)

## การทดลองที่ 6 — payload บอกเรื่อง commit อะไร

**คำถาม:** Gitea ส่งข้อมูลอะไรให้ Jenkins พร้อม push event?

- กลับไป **Gitea → hello-ci → Settings → Webhooks** แล้วเปิด webhook เดิม
- คลิก delivery ล่าสุดจากการ push จริง แล้วเลือกแท็บ **Request**
- ค้นหา `ref`, `after`, `head_commit.id`, `head_commit.message` และ `commits[].modified`

✅ **สิ่งที่ต้องเห็น** :

```text
head_commit.id: 9464fc0039bc...
head_commit.message: Verify immediate webhook build
commits[0].modified: webhook-proof.txt
```

payload จึงบอกได้ว่า branch ใดชี้ไป commit ใด ใคร push ข้อความ commit คืออะไร และไฟล์ใดเปลี่ยน แม้แล็บนี้ใช้ token เลือก job อย่างเดียว ข้อมูลเหล่านี้นำไปทำ filter หรือ audit ต่อได้

## การทดลองที่ 7 — สถานะจบ LAB 5 ครบหรือยัง

**คำถาม:** จะตรวจ plugin, trigger, webhook และ build ล่าสุดพร้อมกันได้อย่างไร?

```bash
cd 005_LAB_Webhook_Trigger
bash check.sh
```

✅ **สิ่งที่ต้องเห็น** :

```text
[PASS] Generic Webhook Trigger 2.4.2 ติดตั้งและ active
[PASS] job hello-ci-pipeline ปิด Poll SCM แล้ว
[PASS] Gitea มี active push webhook ไป canonical Jenkins URL
[PASS] build ล่าสุด #6 มี cause จาก Generic Webhook Trigger
ผลรวม: PASS — LAB 5 พร้อมใช้งาน
```

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| Delivery ได้ 404 และ `Did not find any jobs` | ยังไม่ Save trigger หรือ token ใน URL/หน้า job สะกดไม่ตรง | กลับไป Configure ตรวจ `cicd2569-hello`, กด Save แล้วเรียก endpoint ตรงซ้ำ |
| Delivery timeout | ใช้ `http://localhost:8080/...` ทำให้ Gitea เรียกตัวเอง | เปลี่ยนเป็น `http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello` |
| Delivery 200 แต่ build ที่ต้องการไม่เกิด | token ซ้ำกับ job อื่นหรือไปผูกผิด job | แยก token ต่อ job ตรวจ config ของทุก job และใช้ `cicd2569-hello` เฉพาะ `hello-ci-pipeline` |
| Plugin restart ค้าง | Jenkins ยังติดตั้ง dependency หรือ browser รอ connection เก่า | รอด้วย `until curl -fsS http://localhost:8080/login; do sleep 2; done`; ยังไม่กลับให้ดู `docker logs --tail 100 jenkins` |
| Gitea แจ้ง URL not allowed | container ไม่ได้ตั้ง webhook allow-list สำหรับ private network | recreate Gitea ตาม LAB 4 ด้วย `GITEA__webhook__ALLOWED_HOST_LIST=private` หรือกู้ด้วย `bash tools/bootstrap/up_to_lab4.sh` แล้วตั้ง webhook ใหม่ |
| ตามไม่ทันหรือสถานะไม่ตรง | ขั้น LAB 5 ทำค้างกลางทาง | รัน `bash tools/bootstrap/up_to_lab5.sh` เพื่อกู้สถานะ แล้วรัน `bash 005_LAB_Webhook_Trigger/check.sh` |
