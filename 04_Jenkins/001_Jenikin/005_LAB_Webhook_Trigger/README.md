# LAB 5 — Push แล้ว Build ทันทีด้วย Webhook

แล็บ 30 นาทีนี้ศึกษาการเปลี่ยนกลไก trigger ของ `hello-ci-pipeline` จากการที่ Jenkins ตรวจ repository เป็นระยะ ไปเป็นการที่ Gitea แจ้งเหตุการณ์ `push` ทันที เมื่อสิ้นสุดแล็บ ผู้เรียนจะติดตั้ง plugin กำหนด token สร้าง webhook และตรวจสอบ delivery, payload และ build cause ได้จากหลักฐานจริง

## ทฤษฎีก่อนลงมือ

Webhook คือการแจ้งเหตุการณ์แบบ **push model** เมื่อ Gitea รับ commit ใหม่ ระบบจะส่ง HTTP POST พร้อม payload ไปยัง endpoint ของ Jenkins ทันที ผู้รับจึงไม่ต้องส่ง request เพื่อตรวจสอบ repository ซ้ำในช่วงที่ไม่มีการเปลี่ยนแปลง รายละเอียดเปรียบเทียบและวิดีโอ `polling vs webhook` อยู่ในสไลด์ตอนที่ 5

Poll SCM เป็น **pull model** ซึ่ง Jenkins ทำงานตามตารางเวลาแล้วตรวจว่า revision เปลี่ยนหรือไม่ วิธีนี้ไม่ต้องให้ระบบต้นทางเข้าถึง endpoint ของ Jenkins แต่มีความหน่วงตามรอบ polling และเกิด request แม้ repository ไม่มี commit ใหม่ LAB 4 ใช้ `* * * * *`; LAB นี้จะปิด polling และให้ Gitea เป็นผู้แจ้งเหตุการณ์แทน

Generic Webhook Trigger plugin เพิ่ม endpoint `/generic-webhook-trigger/invoke` และเลือก job ด้วย token ตามสัญญา I-05 แล็บนี้ใช้ `cicd2569-hello` เฉพาะ `hello-ci-pipeline` หากหลาย job ใช้ token เดียวกัน request หนึ่งครั้งอาจ trigger ทุก job ที่ผูก token นั้น จึงต้องแยก token ต่อ job

Gitea รันด้วย `GITEA__webhook__ALLOWED_HOST_LIST=private` ตั้งแต่ LAB 4 เพื่ออนุญาตปลายทาง private network เช่น `jenkins` บน `cicd-net` โดยไม่เปิดให้ webhook ติดต่อทุก host การกำหนด allow-list ช่วยลดความเสี่ยงที่ server จะถูกใช้เรียกปลายทางที่ไม่ได้ตั้งใจ

> **Safety:** token webhook คือรหัสเปิดประตูให้สั่ง build แล็บนี้ใช้ค่าคงที่เพื่อ copy-paste ง่าย; production ต้องสุ่มค่าแรง แยก token/credential ต่อ job จำกัด scope/เครือข่าย และเก็บด้วยระบบ secrets ส่วน `ALLOWED_HOST_LIST=private` จำกัดพื้นที่ปลายทางแทน wildcard แต่ยังควรใช้ least privilege และแยก build agent

## 🎯 ขอบเขตและผลลัพธ์การเรียนรู้

- ติดตั้ง Generic Webhook Trigger 2.4.2 และยืนยันว่า Jenkins กลับมาทำงานหลัง restart
- ปิด Poll SCM และกำหนด token เฉพาะ `hello-ci-pipeline`
- ทดสอบ endpoint โดยตรงเพื่อแยกปัญหาฝั่ง Jenkins ออกจาก Gitea
- สร้าง Gitea webhook ด้วย URL canonical และตรวจ delivery HTTP 200
- push commit จริงแล้วตรวจ build cause และ payload ของเหตุการณ์

## สภาพตั้งต้น

ก่อนคาบต้องมีสถานะจบ LAB 4: devtools ทำงานอยู่, inner container `jenkins` และ `gitea` อยู่บน `cicd-net`, repository `student/hello-ci` มี branch `main` และ job `hello-ci-pipeline` เปิด Poll SCM หากต้องกู้สถานะ ต้องเตรียม `DOCKER_USER`/`DOCKER_TOKEN` ใน environment สำหรับ bootstrap เท่านั้น

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
```

✅ **สิ่งที่ต้องเห็น** :

```text
jenkins    Up ...
gitea      Up ...
```

> ยังไม่มี? ย้อนไปทำ [LAB 4](../004_LAB_Pipeline_From_Git/README.md) ก่อน (ใช้เวลา ~40 นาที) หรือกู้สถานะด้วย `(cd "$COURSE_ROOT" && bash tools/bootstrap/up_to_lab4.sh)`

## การทดลองที่ 1 — Jenkins รับ webhook ได้อย่างไร

**คำถาม:** plugin รุ่นใดเพิ่ม Generic Webhook Trigger ให้ job และจะยืนยันการ restart ได้อย่างไร?

Plugin ทำให้ Jenkins มี endpoint สำหรับรับ HTTP request จาก Gitea ขั้นนี้จึงติดตั้ง plugin ก่อนแก้ job เพื่อให้รายการ trigger ใหม่ปรากฏในหน้า Configure

1. เปิด `http://localhost:8080` แล้วเลือก **Manage Jenkins → Plugins → Available plugins**
2. ค้นหา `generic-webhook-trigger` เลือกผลลัพธ์ **Generic Webhook Trigger 2.4.2**
3. กด **Install** และตรวจสถานะในหน้า **Download progress**
4. เลือก **Restart Jenkins when installation is complete and no jobs are running** แล้วรอให้หน้า login กลับมา

![ผลค้น Generic Webhook Trigger ใน Available plugins](../slides_assets/lab5_s01_available_plugin.png)

*ภาพที่ 1 ผลค้น `generic-webhook-trigger` แสดงรุ่น 2.4.2 และช่องเลือกของ plugin ก่อนติดตั้ง*

![หน้า Download progress และตัวเลือก restart](../slides_assets/lab5_s02_plugin_download_restart.png)

*ภาพที่ 2 หน้า Download progress แสดงรายการติดตั้งและตัวเลือก restart Jenkins ด้านล่าง*

```bash
until curl -fsS http://localhost:8080/login >/dev/null; do sleep 2; done
```

✅ **สิ่งที่ต้องเห็น** :

```text
Generic Webhook Trigger 2.4.2    Enabled
```

> 📝 หากหน้า restart ยังไม่ตอบสนอง ให้รอผลจาก `curl` ก่อน ไม่ควรส่งคำสั่ง restart ซ้ำระหว่างที่ Jenkins กำลังโหลด plugin

ขณะนี้ Jenkins มี plugin ที่ต้องใช้แล้ว ขั้นถัดไปจะเปลี่ยน trigger ของ job โดยไม่แก้ Jenkinsfile

## การทดลองที่ 2 — จะเปลี่ยนจาก polling เป็น webhook โดยไม่แก้ Jenkinsfile อย่างไร

**คำถาม:** trigger ของ `hello-ci-pipeline` ต้องตั้งค่าอย่างไรเพื่อให้ token เลือก job นี้เพียงตัวเดียว?

Trigger เป็นคุณสมบัติของ job และมีผลหลังบันทึก configuration การปิด Poll SCM ป้องกัน build ซ้ำจากสองกลไก ส่วน token ใช้ระบุ job ที่ endpoint ต้อง trigger

1. เลือก **Jenkins → hello-ci-pipeline → Configure → Triggers**
2. เอาเครื่องหมาย **Poll SCM** ออก
3. เลือก **Generic Webhook Trigger**
4. กรอกช่อง **Token** เป็น `cicd2569-hello` แล้วกด **Save**

![Build Triggers และ token ของ job](../slides_assets/lab5_s03_build_trigger_token.png)

*ภาพที่ 3 Generic Webhook Trigger ถูกเลือก และช่อง Token มีค่า `cicd2569-hello` ก่อนบันทึก*

✅ **สิ่งที่ต้องเห็น** :

```text
Poll SCM: off
Generic Webhook Trigger: on
Token: cicd2569-hello
```

> 📝 Trigger ที่ตั้งผ่าน job UI มีผลเมื่อกด Save จึงไม่ต้องกด Build Now หรือทำ seed build ก่อนทดสอบ endpoint

ขณะนี้ job พร้อมรับ request แล้ว แต่ยังไม่เกี่ยวข้องกับ Gitea ขั้นถัดไปจึงทดสอบ endpoint จาก shell เพื่อแยกขอบเขตปัญหา

## การทดลองที่ 3 — token เลือก job ถูกจริงไหม

**คำถาม:** ก่อนเชื่อม Gitea จะทดสอบ endpoint โดยตรงจาก devtools shell ได้อย่างไร?

การเรียก endpoint โดยตรงพิสูจน์ว่า plugin, token และ job configuration ทำงานครบ หากขั้นนี้ไม่ผ่าน ปัญหายังอยู่ฝั่ง Jenkins ไม่ใช่การตั้งค่า webhook ของ Gitea

```bash
curl -s 'http://localhost:8080/generic-webhook-trigger/invoke?token=cicd2569-hello'
```

✅ **สิ่งที่ต้องเห็น** :

```json
{"jobs":{"hello-ci-pipeline":{"triggered":true}},"message":"Triggered jobs."}
```

ค่าจริงมี field รายละเอียดเพิ่ม เช่น queue id แต่ต้องพบ `hello-ci-pipeline`, `triggered:true` และ `Triggered jobs.` เมื่อ endpoint ผ่านแล้วจึงกำหนดให้ Gitea เรียก URL เดียวกันผ่าน network ภายใน

## การทดลองที่ 4 — Gitea ส่ง delivery ถึง Jenkins ได้ไหม

**คำถาม:** URL ใดทำให้ Gitea container เรียก Jenkins container ผ่าน `cicd-net` ได้?

Webhook ต้องใช้ DNS ภายใน Docker network เพราะ request ถูกส่งจาก Gitea container ไม่ใช่จาก browser ของผู้เรียน URL canonical จึงใช้ชื่อ service `jenkins` แทน `localhost`

1. เปิด `http://localhost:3000` แล้วเลือก **student/hello-ci → Settings → Webhooks**
2. กด **Add Webhook → Gitea**
3. กรอก **Target URL** เป็น `http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello`
4. คง **HTTP Method = POST**, **POST Content Type = application/json**, **Active** และ **Push Events**
5. กด **Add Webhook** แล้วตรวจว่ารายการใหม่แสดง URL canonical
6. เปิด webhook ที่สร้าง กด **Test Push Event** แล้วกาง delivery ล่าสุดที่แท็บ **Response**

![แบบฟอร์ม Add Webhook ที่กรอก URL แล้ว](../slides_assets/lab5_s04_add_webhook_form.png)

*ภาพที่ 4 แบบฟอร์ม Gitea แสดง Target URL canonical พร้อม POST, application/json และ Active*

![แบบฟอร์ม webhook จากภาพชุดเดิม](../slides_assets/lab5_webhook_config.png)

*ภาพที่ 5 ภาพอ้างอิงเดิมของหน้า Add Webhook ซึ่งใช้ค่า configuration เดียวกัน*

![รายการ webhook หลังบันทึก](../slides_assets/lab5_s05_webhook_list.png)

*ภาพที่ 6 รายการ Webhooks หลังบันทึกแสดงจุดสถานะและ URL ที่ใช้ชื่อ container `jenkins`*

![Delivery ล่าสุดพร้อม HTTP 200 และ response](../slides_assets/lab5_s06_delivery_response.png)

*ภาพที่ 7 delivery ที่กางอยู่แสดง Response 200 และ body ซึ่งระบุ `hello-ci-pipeline` ว่าถูก trigger*

![Delivery HTTP 200 จากภาพชุดเดิม](../slides_assets/lab5_delivery.png)

*ภาพที่ 8 ภาพอ้างอิงเดิมยืนยัน HTTP 200 และข้อความ `Triggered jobs.` จาก Jenkins*

✅ **สิ่งที่ต้องเห็น** :

```text
HTTP Status: 200
Response: ... "hello-ci-pipeline" ... "Triggered jobs."
```

> 📝 ใน URL นี้ `jenkins` คือ DNS ของ container บน `cicd-net`; `localhost` ภายใน Gitea หมายถึง Gitea เอง จึงใช้แทนกันไม่ได้

เมื่อ test delivery ได้ HTTP 200 แล้ว เส้นทาง Gitea → Jenkins พร้อมใช้งาน ขั้นถัดไปจะสร้างเหตุการณ์จาก `git push` จริง

## การทดลองที่ 5 — push จริงเร็วกว่า polling แค่ไหน

**คำถาม:** เมื่อแก้ไฟล์แล้ว push Jenkins จะพบ build ใหม่ในกี่วินาที และจะพิสูจน์ build cause ได้อย่างไร?

การทดลองนี้ใช้ commit จริงเพื่อยืนยันว่าการแจ้งเตือนไม่ได้เกิดจากปุ่ม Test Push Event หลัง push ให้เปิด build ล่าสุดและตรวจทั้งผลลัพธ์, revision และข้อความ cause

```bash
LAB5_WORKDIR=$(mktemp -d) && git clone http://student:student2569@localhost:3000/student/hello-ci.git "$LAB5_WORKDIR/hello-ci"
cd "$LAB5_WORKDIR/hello-ci" && git config user.name student && git config user.email student@example.com && date -u +"webhook proof %Y-%m-%dT%H:%M:%SZ" >> webhook-proof.txt && git add webhook-proof.txt && git commit -m 'Verify immediate webhook build' && time git push origin main
```

1. เปิด **Jenkins → hello-ci-pipeline** ทันทีหลัง `git push`
2. เปิด build ใหม่ที่ปรากฏ แล้วตรวจหน้า **Status** และ **Console Output**
3. ยืนยันว่าหน้า build แสดง **Generic Cause** และ revision ตรงกับ commit ที่ push

![Build ที่เกิดจาก webhook และ Generic Cause](../slides_assets/lab5_s07_webhook_build_cause.png)

*ภาพที่ 9 build #6 สำเร็จ แสดง Generic Cause, revision `401ab4f0ded0...` และข้อความ commit ที่ใช้ทดสอบ*

![Build อัตโนมัติจากภาพชุดเดิม](../slides_assets/lab5_auto_build.png)

*ภาพที่ 10 ภาพอ้างอิงเดิมของ build อัตโนมัติ ซึ่งแสดง cause จาก Generic Webhook Trigger เช่นเดียวกัน*

✅ **สิ่งที่ต้องเห็น** :

```text
new build #6 detected 11.59s after push
build #6 = SUCCESS
cause: Generic Cause
```

ผลรอบตรวจนี้พบ build ใหม่ภายใน 11.59 วินาที จึงไม่ต้องรอหน้าต่าง 0–60 วินาทีของ Poll SCM เลข build และระยะเวลาของแต่ละเครื่องอาจต่างกัน แต่ cause ต้องมาจาก Generic Webhook Trigger

ขณะนี้มี push delivery จริงและ build ที่สัมพันธ์กันแล้ว ขั้นถัดไปจะอ่าน request payload ของ delivery ล่าสุด

## การทดลองที่ 6 — payload บอกเรื่อง commit อะไร

**คำถาม:** Gitea ส่งข้อมูลใดให้ Jenkins พร้อม push event?

Payload เป็นหลักฐานระดับเหตุการณ์ที่ใช้ตรวจ branch, commit และไฟล์ที่เปลี่ยน แม้แล็บนี้ใช้ token เลือก job เพียงอย่างเดียว ข้อมูลเดียวกันสามารถนำไปกำหนด filter หรือใช้ audit ได้

1. กลับไป **Gitea → hello-ci → Settings → Webhooks** แล้วเปิด webhook เดิม
2. กาง delivery ล่าสุดจากการ push จริง
3. เลือกแท็บ **Request** แล้วตรวจ Headers และ Content
4. ค้นหา `ref`, `after`, `head_commit.id`, `head_commit.message` และ `commits[].added`

![Request payload ของ push delivery ล่าสุด](../slides_assets/lab5_s08_delivery_request.png)

*ภาพที่ 11 delivery จาก push จริงแสดง request URL, event type, `refs/heads/main`, commit `401ab4f0ded0...` และข้อความ `Verify immediate webhook build`*

✅ **สิ่งที่ต้องเห็น** :

```text
head_commit.id: 401ab4f0ded0...
head_commit.message: Verify immediate webhook build
commits[0].added: webhook-proof.txt
```

Payload จึงระบุได้ว่า branch ใดชี้ไป commit ใด ผู้ใด push ข้อความ commit คืออะไร และไฟล์ใดเปลี่ยน เมื่อหลักฐานครบแล้วจึงตรวจสถานะรวมด้วยสคริปต์ของแล็บ

> **ทางเลือกอัตโนมัติ (รันจากเครื่อง host ของผู้สอน):** helper นี้ใช้ Playwright ซึ่งไม่มีใน devtools image ให้ผู้สอนกำหนด `COURSE_ROOT` บน host แล้วตรวจว่า delivery ล่าสุดมี `webhook-proof.txt` อยู่ใน `commits[].added`; นักศึกษาตรวจผ่านแท็บ Request ตามขั้นด้านบนได้โดยไม่ต้องใช้ helper

```bash
(cd "$COURSE_ROOT" && GITEA_BASE_URL=http://localhost:3000 DT_NAME=devtools-jenkins python3 tools/ui/lab5_payload.py)
```

## การทดลองที่ 7 — สถานะจบ LAB 5 ครบหรือยัง

**คำถาม:** จะตรวจ plugin, trigger, webhook และ build ล่าสุดพร้อมกันได้อย่างไร?

```bash
(cd "$COURSE_ROOT/005_LAB_Webhook_Trigger" && bash check.sh)
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
| Delivery 200 แต่ build ที่ต้องการไม่เกิด | token ซ้ำกับ job อื่นหรือผูกผิด job | แยก token ต่อ job และใช้ `cicd2569-hello` เฉพาะ `hello-ci-pipeline` |
| Plugin restart ค้าง | Jenkins ยังติดตั้ง dependency หรือ browser รอ connection เดิม | รอด้วย `until curl -fsS http://localhost:8080/login; do sleep 2; done`; หากยังไม่กลับให้ดู `docker logs --tail 100 jenkins` |
| Gitea แจ้ง URL not allowed | container ไม่ได้อนุญาต webhook ไป private network | recreate Gitea ตาม LAB 4 ด้วย `GITEA__webhook__ALLOWED_HOST_LIST=private` หรือกู้ด้วย `(cd "$COURSE_ROOT" && bash tools/bootstrap/up_to_lab4.sh)` |
| ตามไม่ทันหรือสถานะไม่ตรง | ขั้น LAB 5 ค้างกลางทาง | รัน `(cd "$COURSE_ROOT" && bash tools/bootstrap/up_to_lab5.sh)` แล้วตรวจด้วย `(cd "$COURSE_ROOT/005_LAB_Webhook_Trigger" && bash check.sh)` |
