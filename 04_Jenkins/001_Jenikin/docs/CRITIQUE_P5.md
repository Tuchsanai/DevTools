# CRITIQUE — PLAN Phase 5: ย้าย SCM จาก Gitea ไป GitHub

วันที่ตรวจ: 2026-08-20  
ผู้ตรวจ: Codex (builder + critic)  
สถานะคำตัดสิน: **REVISE — ยังไม่ควรเริ่ม implementation ตามแผนฉบับนี้**

## สรุปคำตัดสิน

แผนมี spike ที่พิสูจน์ happy path ของ GitHub → Smee → GWT แล้ว แต่ยังไม่ได้ล็อก semantics ที่สำคัญต่อห้องเรียนจริง ได้แก่ GitHub `ping`, ขอบเขตของ delivery status, rate limit ต่อ public IP, lifecycle แบบไม่เก็บ event ของ Smee, การใช้สอง channel อย่าง idempotent, การไม่แตะ repository เดิมของนักศึกษา และการพิสูจน์เส้นทางที่นักศึกษาคลิกจริง

| ระดับ | จำนวน |
|---|---:|
| BLOCKER | 8 |
| MAJOR | 18 |
| MINOR | 7 |
| **รวม** | **33** |

## หลักฐานที่ใช้ตัดสิน

| ข้อเท็จจริง | ผลต่อแผน | แหล่งอ้างอิง |
|---|---|---|
| GitHub ส่ง `ping` ทันทีเมื่อสร้าง webhook และรองรับทั้ง JSON กับ form-urlencoded | GWT แบบ token-only อาจสร้าง build ตั้งแต่ยังไม่มี push; payload ต้องล็อกเป็น JSON | [GitHub: Creating webhooks](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks) |
| GWT รับ HTTP request ทั่วไป และ filter ด้วยตัวแปร/regular expression เป็นความสามารถแบบ optional | config ปัจจุบันที่ filter ว่างไม่ได้แยก `ping` จาก `push` | [Generic Webhook Trigger plugin](https://github.com/jenkinsci/generic-webhook-trigger-plugin) และ `tools/bootstrap/jobs/hello-ci-webhook.xml:28-40` |
| GitHub REST แบบไม่ authenticate จำกัด 60 request/ชั่วโมงตาม originating IP | นักศึกษา 30 คนหลัง NAT เดียวใช้โควตาร่วมกัน | [GitHub: REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) |
| GitHub webhook delivery status คือผลตอบจาก Payload URL ซึ่งในแผนคือ Smee | HTTP 2xx จาก GitHub API ไม่ได้พิสูจน์ว่า relay POST ถึง Jenkins หรือเกิด build | [GitHub: Repository webhooks API](https://docs.github.com/en/rest/repos/webhooks) |
| Smee ส่ง event ให้ client ที่กำลังเชื่อมอยู่, ไม่เก็บ payload ฝั่ง server, หน้าเว็บเก็บเฉพาะ localStorage และ channel ไม่มี authentication | event ขณะ relay/browser หลุดหายถาวร; URL channel เป็น capability ที่ต้อง redact | [Smee.io README/FAQ](https://github.com/probot/smee.io) |
| image ที่เลือกเป็น third-party, Docker Hub ระบุว่าอัปเดตเกิน 5 ปีแล้ว และ manifest เป็น `linux/amd64` เดี่ยว | digest อย่างเดียวไม่รับรอง runtime/version/reconnect หรือ ARM compatibility | [Docker Hub: deltaprojects/smee-client](https://hub.docker.com/r/deltaprojects/smee-client/tags) |

## Findings — BLOCKER

1. **P5-B01 — [severity: BLOCKER] [assumption | interface] GWT แบบ token-only จะรับ GitHub `ping` เป็นคำขอ trigger ด้วย**  
   GitHub ส่ง `ping` อัตโนมัติหลัง Add webhook แต่ I-05v3 ล็อกเพียง token และ XML ปัจจุบันมี `genericVariables`, `genericHeaderVariables` และ regexp filter ว่างทั้งหมด การเลือกเฉพาะ “Push events” ไม่ได้ตัด `ping` เริ่มต้น ผลคือ LAB 5 อาจได้ build ที่ไม่ได้เกิดจาก push และ LAB 6 อาจเลื่อน build v1/v2 เป็น #2/#3 ทำให้ภาพ, expected output และ check ผูกผิด run
   - **แก้แบบ concrete:** เพิ่มตัวแปร GWT `ref = $.ref` และ `after = $.after`; ตั้ง `regexpFilterText=$ref`, `regexpFilterExpression=^refs/heads/main$` และ `causeString` ที่มี `$after` หรือใช้ header `X-GitHub-Event` filter เป็น `^push$` พร้อม branch filter
   - เพิ่ม acceptance: จด baseline → สร้าง hook → รอแล้ว baseline ต้องไม่เปลี่ยนจาก `ping` → push SHA เฉพาะรอบ → ต้องเกิด build ใหม่ **หนึ่ง** buildและ checkout SHA นั้น

2. **P5-B02 — [severity: BLOCKER] [interface | DoD] `/hooks/{id}/deliveries` ไม่ใช่หลักฐาน end-to-end แทน Gitea delivery เดิม**  
   GitHub POST ไป `<SMEE_URL>` ดังนั้น `status_code=200` ใน GitHub API พิสูจน์เพียง GitHub → Smee; ต่อให้ `smee-client` หยุด, Jenkins ล่ม, token ผิด หรือ GWT filter ไม่รับ GitHub ก็ยังเห็น delivery 2xx ได้ D8 และ U-P5-INT จึงเปิดช่อง false-positive
   - **แก้แบบ concrete:** DoD หนึ่ง event ต้อง correlate อย่างน้อย 4 hop ด้วย SHA/GUID เดียวกัน: GitHub delivery `event=push`, `request.payload.after=<SHA>` → relay log หลังเวลานั้นมี `POST <target> - 200` → Jenkins build cause เป็น GitHub/GWT และ checkout `<SHA>` → build `SUCCESS`
   - ห้ามใช้ “delivery ล่าสุด” อย่างเดียว; ต้องกรอง `event=push`, `ref=refs/heads/main`, repository เต็ม และ SHA ของ probe รอบนั้น

3. **P5-B03 — [severity: BLOCKER] [dependency | feasibility] สมมติฐาน anonymous API “ไม่เกิน 3 ครั้งต่อ check” ผิดในระดับห้องเรียน**  
   limit 60 ครั้ง/ชั่วโมงผูกกับ public IP ไม่ใช่นักศึกษา 1 คน นักศึกษา 30 คน × 3 request = 90 ตั้งแต่รอบแรก และการ rerun จะ fail ทั้งห้องหลัง NAT เดียวกัน
   - **แก้แบบ concrete:** ทุก `check.sh` ที่เรียก `api.github.com` ต้อง authenticate ด้วย token ของนักศึกษา รวม LAB 4 ด้วย; อ่าน response ครั้งเดียวแล้ว cache ใน temp fileเพื่อใช้หลาย assertion
   - DoD ต้องมี request budget ต่อ script, ทดสอบ burst จำลองจำนวนผู้เรียน และข้อความเฉพาะสำหรับ 403/429/`Retry-After` โดยไม่พิมพ์ token

4. **P5-B04 — [severity: BLOCKER] [scope | interface] bootstrap มีสิทธิ์เขียนทับ repository ชื่อทั่วไปที่มีอยู่ก่อน**  
   E3 พิสูจน์เพียงว่า `hello-ci`/`webapp` ว่างบนบัญชี Tuchsanai ไม่ได้พิสูจน์บัญชีนักศึกษาทุกคน D9 ระบุว่า repo มีอยู่แล้วก็ push fixtures ซึ่งอาจแก้ repository ส่วนตัว, ชน initial README, หรือ normalize งานที่ผู้เรียนทำไว้
   - **แก้แบบ concrete:** เลือกชื่อ course-specific หรือเพิ่มไฟล์ ownership marker เช่น `.jenkins-lab-2569`; ถ้า repo มีอยู่แต่ไม่มี marker/contract ที่ตรง ให้ **fail closed โดยไม่ commit/push/hook** พร้อมขั้น rename/backup ที่ชัดเจน
   - บันทึก `created_by_this_run=true/false`; ห้าม force-push และห้ามลบ repo ที่ไม่ได้สร้างโดย run นี้

5. **P5-B05 — [severity: BLOCKER] [interface | feasibility] contract ใช้สอง channel แต่มี env `SMEE_URL` เดียว และการ mint ใหม่ไม่ idempotent**  
   D3 ต้องมี hello/webapp คนละ channel ขณะที่ D9 ระบุเพียง `SMEE_URL`; rerun โดยไม่ส่ง env อาจ mint URL ใหม่ แต่ hook/container เดิมยังชี้ URL เก่า ทำให้ executable manifest I-02 แตกทันที
   - **แก้แบบ concrete:** ล็อกชื่อ `SMEE_HELLO_URL` และ `SMEE_WEBAPP_URL`; mapping ต้องเป็น 1:1 ระหว่าง repo ↔ hook id ↔ channel ↔ relay container ↔ GWT token
   - persist/recover URL จาก Docker label หรือ state fileที่ permission จำกัด; rerun ต้อง assert URL/target/image เดิมหรือ converge อย่างปลอดภัย และต้องเหลือ hook/relay ต่อ repoอย่างละหนึ่งเท่านั้น

6. **P5-B06 — [severity: BLOCKER] [assumption | dependency | DoD] แผนถือ Smee เป็นคิวที่ย้อนดู/replay ได้ ทั้งที่เป็น pass-through**  
   Smee ไม่เก็บ event ฝั่ง server และส่งเฉพาะ client ที่เชื่อมอยู่ หน้า channel จะเห็น history เฉพาะ browser tab ที่เปิดรับ event แล้วเก็บใน localStorage หากปิด tab หรือ relay disconnect ตอน push หลักฐานและ build จะหาย แม้ GitHub delivery จะยังเขียว
   - **แก้แบบ concrete:** README ต้องสั่งเปิด channel ใน tab แยก **ก่อน** Add webhook/push, รอ relay log `Connected`, แล้วจึง push; ระบุชัดว่า reconnect ไม่ replay event ที่พลาด
   - DoD ต้องทดสอบ `docker restart smee-hello` → รอ connected รอบใหม่ → push unique commit → exactly one build และมี recovery ที่ deterministic เช่น GitHub redelivery/API attempt หรือ empty commit ใหม่

7. **P5-B07 — [severity: BLOCKER] [scope | DoD] migration inventory ไม่ครอบ active Gitea surfaces จึงยังบรรลุ G1 ไม่ได้**  
   U-P5-0 ระบุ UI scripts เพียงบางไฟล์ แต่ inventory ปัจจุบันยังมี contract Gitea ใน `004.../{Jenkinsfile,hello.sh,expected.txt}`, `docs/LAB_TEMPLATE.md`, bootstrap fixtures/job XML/up_to script, `lab4_scm_job.py`, `lab4_scm_rewrite_capture.py`, `lab5_payload.py`, `lab5_push_build.py`, `lab6_job.py`, `lab6_pipeline.py`, annotation JSON, root README, integration และ slide source
   - **แก้แบบ concrete:** ทำ migration manifest ระดับไฟล์ก่อนเริ่ม unit; กำหนด owner ของทุกไฟล์และ asset ว่าจะ rewrite/delete/archive
   - เพิ่ม gate `rg` สำหรับ active deliverables ที่ต้องได้ศูนย์สำหรับ `gitea`, `localhost:3000`, `gitea_data`, `student/hello-ci`, `student/webapp` พร้อม allowlist เฉพาะ historical ledger/critique เท่านั้น

8. **P5-B08 — [severity: BLOCKER] [DoD | interface] Integration ใช้ bootstrap ข้ามเส้นทางนักศึกษา และ D5 ขัด DD-01 เดิม**  
   U-P5-INT เริ่มจาก “bootstrap lab5 → capstone” จึงไม่พิสูจน์คำสั่ง/คลิกจริงของ LAB 4–5 ขณะที่ภาพ auth-only เป็นภาพสร้างและไม่มี Playwright assertion ตาม DD-01/G2 การที่ postcondition ผ่าน API ไม่ได้พิสูจน์ว่า navigation และ field labels ในเอกสารถูกต้อง
   - **แก้แบบ concrete:** แยก integration สอง track: (A) manual student replay จากจบ LAB 3 ผ่านทุก block/UI step LAB 4–6 และ (B) bootstrap recovery/idempotency จากเครื่องใหม่
   - เพิ่ม ledger exception แบบจำกัดขอบเขตสำหรับ GitHub auth-only UI: manual click path + ภาพที่ระบุชัดว่า “ภาพจำลอง” + ลิงก์ official docs + API postcondition; Jenkins, Smee public UI และ GitHub public pages ยังต้องมี script/assertion จริง

## Findings — MAJOR

1. **P5-M01 — [severity: MAJOR] [dependency | feasibility] image relay ที่ pin เป็น dependency เก่าและไม่รู้เวอร์ชันภายใน**  
   `deltaprojects/smee-client` ถูกอัปเดตเกิน 5 ปีแล้วและมีเฉพาะ `linux/amd64`; E4 ล็อกเพียง digest แต่ไม่ล็อก Node/smee-client version หรือ behavior ของ reconnect/header forwarding
   - **แก้แบบ concrete:** สร้าง image ของชุดสอนเองจาก Node base digest + `smee-client` version exact/package lock จาก upstream แล้วบันทึก `node --version`, `smee --version`, architecture และ digest ใน STACK_RESOLVED; ถ้าคง image เดิมต้องประกาศ amd64-only และเพิ่ม reconnect/TLS/target tests เป็น accepted risk

2. **P5-M02 — [severity: MAJOR] [interface] GitHub hook contract ยังไม่ครบ field ที่มีผลต่อ payload**  
   แผนพูดเพียง smee URL แต่ GitHub UI อาจส่ง `application/x-www-form-urlencoded`; GWT JSONPath/filter ต้องการ JSON และ hook ยังมี events, active, SSL verification และ secret decision
   - **แก้แบบ concrete:** ล็อก `config.url=<channel>`, `content_type=json`, `events=[push]`, `active=true`, `insecure_ssl=0`; ระบุว่า Secret เว้นว่างเพราะ topology นี้ไม่มี signature-verifying receiver หรือเพิ่ม verifier จริง ห้ามอ้างว่า secret ถูกตรวจถ้ายังไม่มี
   - `check.sh` ต้อง assert ทุก field ไม่ใช่แค่ URL

3. **P5-M03 — [severity: MAJOR] [interface | DoD] วิธีแทนค่า username ใน Jenkins job XML ยังเสี่ยงทั้ง literal placeholder และค่าจริงหลุดเข้า tracked file**  
   ข้อความ “job XML URL template แทนค่า `$GITHUB_USER`” ไม่ระบุว่า render ที่ใด หากแก้ template in-place หลัง integration จะ commit `Tuchsanai`; หากไม่ render Jenkins จะได้ URL literal
   - **แก้แบบ concrete:** checked-in template ใช้ sentinel `__GITHUB_USER__`; validate login จาก `GET /user` และรูปแบบ username จากนั้น render ไป `mktemp`, POST จาก temp, trap ลบ และ assert `git diff --exit-code` หลัง bootstrap
   - runtime `config.xml` ต้องเทียบกับ `https://github.com/$GITHUB_USER/...`; README/deck/log ที่ส่งมอบใช้ `<GITHUB_USER>` เท่านั้น

4. **P5-M04 — [severity: MAJOR] [interface | DoD] masking ครอบคลุม username แต่ไม่ครอบ capability URL และข้อมูลผู้ commit**  
   หน้า Smee และ startup log แสดง channel URL จริงซึ่งไม่มี authentication; ผู้ที่รู้ URL สามารถส่ง payload ผ่าน relay ไปยัง GWT ได้ Payload GitHub ยังอาจมี username/email จริงจาก global Git config
   - **แก้แบบ concrete:** I-10 ต้อง mask ทั้ง `<GITHUB_USER>` และ `<SMEE_URL>`/channel id ในภาพและรายงาน; raw capture ห้าม track/เก็บเป็น pristine source
   - ตั้ง identity ระดับ repo เช่น `Jenkins Student` + `student@example.invalid`; scan `ghp_`, `gho_`, `github_pat_`, `dckr_pat_` และ `https://smee.io/<real-id>` โดยมี allowlist เฉพาะ placeholder/official base URL
   - ก่อน publish ให้ลบ GitHub hook และ relay เพื่อให้ URL ที่อาจหลุดไม่เหลือเส้นทางสั่ง build

5. **P5-M05 — [severity: MAJOR] [feasibility | interface] ขั้น `git push` ด้วย GitHub PAT ยังไม่มี workflow ที่ปลอดภัยและ copy-paste ได้**  
   GitHub ไม่รับ account password สำหรับ HTTPS Git; นักศึกษาต้องใช้ PAT เป็น password แผนยังไม่บอก prompt, credential helper หรือวิธี bootstrap ส่ง token โดยไม่ฝังใน URL/process/history
   - **แก้แบบ concrete:** manual flow ใช้ remote URL ปกติและบอกชัดว่า Username = GitHub login, Password = PAT; ห้าม `https://TOKEN@...` และห้าม `credential.helper store`
   - bootstrap ใช้ temporary `GIT_ASKPASS` ที่อ่าน token จาก env, `GIT_TERMINAL_PROMPT=0`, trap ลบ และตรวจว่า `.git/config`, shell trace, process args กับ logs ไม่มี token; รับ tokenแบบ hidden prompt เมื่อใช้โดยคนและ env เมื่อใช้ CI

6. **P5-M06 — [severity: MAJOR] [dependency | scope] prerequisite “PAT classic scope repo” กว้างเกินและยังไม่ใช่ executable preflight**  
   `repo` ให้สิทธิ์ private repositories ทั้งหมดโดยไม่จำเป็น และผู้เรียนอาจติด email verification, 2FA, managed account, token expiry หรือสิทธิ์สร้าง repo/hookในคาบ
   - **แก้แบบ concrete:** ล็อก credential profile ที่แคบและทดสอบจริง เช่น classic `public_repo` + `write:repo_hook` หรือ fine-grained PAT ที่มี Administration/Contents/Webhooks เท่าที่จำเป็น; `delete_repo` ให้เฉพาะ integration account ไม่ให้ผู้เรียน
   - prerequisite ก่อนคาบต้องมี script ตรวจ token owner, repo creation/public push/hook permission ด้วย disposable probe ที่ cleanup ได้ พร้อม expiry/revoke instruction และ fallback สำหรับบัญชีที่สร้าง public repo ไม่ได้

7. **P5-M07 — [severity: MAJOR] [DoD] check scripts ไม่มี negative matrix และยังเสี่ยงผ่านด้วยสถานะเก่า**  
   “exit 0 กับสถานะจริง” ไม่พิสูจน์ว่าตัวตรวจปฏิเสธ ping-only, delivery เก่า, manual build ล่าสุด, relay 200 เก่า, private repo หรือ hook ผิด channel
   - **แก้แบบ concrete:** ต่อ LAB ต้องมี positive + negative fixtures อย่างน้อย: wrong owner/URL, private repo, stale SHA, ping without push, stopped relay, wrong token/content type, Poll SCM ค้าง และ latest build ที่ cause ไม่ใช่ webhook
   - check ต้อง observational ไม่สร้าง hook/buildเอง และต้องผูกทุกหลักฐานกับ timestamp/SHA ของ run ที่เอกสารเพิ่งทำ

8. **P5-M08 — [severity: MAJOR] [interface | feasibility] ยังไม่มี GitHub API helper contract สำหรับ versioning, errors และ secret-safe logging**  
   การกระจาย `curl` ตรงใน bootstrap/check ทำให้ Accept/API-version/status handling และ rate budget drift ง่าย โดยเฉพาะ 401/403/404/422/429 ที่มีความหมายต่างกัน
   - **แก้แบบ concrete:** สร้าง helper เดียวที่ส่ง `Authorization`, `Accept: application/vnd.github+json`, `X-GitHub-Api-Version` ที่ล็อกไว้; คืนทั้ง status/body แบบไม่ echo header token และอ่าน `Retry-After`/rate headers
   - บันทึกจำนวน request ต่อ run และ reuse JSON เดิมสำหรับหลาย assertion

9. **P5-M09 — [severity: MAJOR] [assumption | feasibility] K3 สรุปว่า Poll SCM กับ GitHub “ไม่มีปัญหา rate” โดยไม่มีหลักฐานห้องเรียน**  
   Git smart HTTP ไม่ใช้โควตา REST 60/ชั่วโมงจริง แต่ยังเป็น outbound traffic ไป GitHub และอาจเจอ abuse/throttling/proxy ของมหาวิทยาลัย; ต่างจาก Gitea local อย่างมีนัยสำคัญ
   - **แก้แบบ concrete:** เปลี่ยนเป็น accepted risk ไม่ใช่ข้อยืนยัน; preflight `git ls-remote` จาก **Jenkins container**, วัด 30-user-equivalent poll burst/เวลาอย่างน้อยหนึ่งรอบ และเพิ่ม troubleshooting DNS/TLS/proxy/429
   - LAB 4 check ต้องยืนยัน anonymous public checkout ไม่มี `credentialsId` และ build SHA ตรง push

10. **P5-M10 — [severity: MAJOR] [DoD] restart checkpoint เดิมหายไป ทั้งที่ relay เพิ่ม state ใหม่ที่เปราะกว่าเดิม**  
    PLAN เดิมบังคับ restart หลัง LAB 5 แต่ U-P5-INT ไม่กล่าวถึง restart/reconnect ของ `smee-hello`/`smee-webapp`
    - **แก้แบบ concrete:** หลังจบ LAB 5 restart outer devtools; รอ inner Docker, Jenkins ready และ relay `Connected`; assert container source/target mappingเดิม จากนั้น push SHA ใหม่และต้องได้ exactly one webhook build โดยไม่ mint channel ใหม่
    - หลัง LAB 6 ทดสอบ relay ทั้งสองไม่ cross-trigger job อีกตัว

11. **P5-M11 — [severity: MAJOR] [scope | DoD] G5 “ไม่มี artifact ค้าง” ใช้กับ Smee channel แบบตรงตัวไม่ได้**  
    Smee ระบุว่า channel อยู่ได้ตลอดและไม่มี delete lifecycle ที่แผนควบคุมได้ D12 กล่าวถึงเพียงลบ repo จึงรับประกัน cleanup แบบเดิมไม่ได้
    - **แก้แบบ concrete:** นิยาม cleanup ใหม่เป็น “ไม่มี active route/state ที่เราควบคุมได้”: delete hooks ที่ run สร้าง, remove relay containers, deleteเฉพาะ GitHub repos ที่ `created_by_this_run`, ลบ temp workdir และ verify 404/empty inventory
    - บันทึก channel URL ว่าเป็น external inert identifier ที่ลบไม่ได้และไม่มี payload server-side; cleanup ต้องอยู่ใน trap และ fail งานถ้ายังมี hook/relay

12. **P5-M12 — [severity: MAJOR] [assumption | DoD] AI-generated GitHub UI ไม่ควรถูกนับเป็น screenshot หรือหลักฐานว่าขั้น UI รันได้**  
    เกณฑ์ “PNG ≥1280px และหน้าตรง field” ยังปล่อยให้ข้อความ/label/control ที่ไม่มีจริงผ่าน และ UI GitHub เปลี่ยนได้
    - **แก้แบบ concrete:** ทุกภาพสร้างต้องติด caption บนภาพ/ใต้ภาพว่า “ภาพจำลอง — UI อาจเปลี่ยน”, อ้าง official GitHub procedure และมี API postcondition ที่รันได้
    - สำหรับความเที่ยงตรงของข้อความ ให้ render mock จาก HTML/CSS/Playwright หรือ overlay text ด้วย code แทนให้โมเดลวาดตัวอักษร; ห้ามใช้ภาพจำลองเป็น delivery/runtime proof

13. **P5-M13 — [severity: MAJOR] [scope | DoD] ไม่มี screenshot inventory ที่พิสูจน์ G2 ว่า “ไม่ขาดช่วง”**  
    U-P5-3 ระบุภาพสร้างเพียง repo form/webhook form และ U-P5-8 ระบุสลับภาพใน deck 6 ภาพ แต่ flow ใหม่ยังมี Smee Start channel, channel URL, GitHub Settings → Webhooks, hook saved/ping, channel event, relay log, public repo result และ Jenkins evidence
    - **แก้แบบ concrete:** เพิ่ม matrix ต่อ experiment: action → filename → real/generated → marker spec → caption → assertion owner; กำหนดจำนวนและรายชื่อไฟล์ exact สำหรับ LAB 4/5/6 และ deck
    - ทุก action screenshot ต้องอยู่ใน `annotations/lab4..6.json`; evidence-only ภาพใดไม่มี markerต้องมีเหตุผลใน registry

14. **P5-M14 — [severity: MAJOR] [interface | DoD] op `mask` ยังไม่มี schema/order และ DoD หนึ่งภาพไม่พอป้องกัน identity leak**  
    `annotate_steps.py` ปัจจุบันรองรับเพียง ellipse/round_rect และ restore target ก่อนวาด หากออกแบบ mask ไม่ชัดอาจ restore กลับเป็นภาพจริง, วาด markerทับผิดลำดับ หรือเก็บ raw source ที่มี username
    - **แก้แบบ concrete:** ล็อก schema เช่น `op=mask`, `box`, `text`, `fill`; ทำ mask ก่อน leader/marker; รักษา dimensions/mode; validate bounds/text fit และ deterministic SHA เมื่อ rerun
    - unit testต้องครอบ out-of-bounds, idempotent rerun, mask+marker ในภาพเดียว, username ยาว และ assert ไม่มี unmasked source/tracked backup สำหรับ **ทุก** ภาพ GitHub/Smee

15. **P5-M15 — [severity: MAJOR] [DoD] การ “ปรับค่าคงที่ deck_offline” สามารถทำให้ gate เขียวโดยไม่รักษา topology ของ deck**  
    `deck_offline_test.py` hardcode 80 หน้า, counter 1/80–80/80, jump 70/72, SVG 8 และ screenshot 19; หากเพิ่ม/ลบหน้าแล้วแก้เลขให้ผ่าน อาจทำ overview jump ผิดตอนหรือฝังภาพเก่าครบ 19 แต่เป็น Gitea
    - **แก้แบบ concrete:** ถ้าคง 80 หน้าให้ประกาศเป็น invariant; ถ้าเปลี่ยนให้สร้าง semantic page IDs/section map แล้ว test jump ตาม ID ไม่ใช่เลขดิบ
    - assert รายชื่อ `data-embedded-from` ใหม่แบบ exact และ zero old Gitea assets ไม่ใช่เพียง count 19; ตรวจ source และ final deckทั้งคู่

16. **P5-M16 — [severity: MAJOR] [DoD] “gates exit 0” ยังไม่มี anti-vacuity และไม่ตรวจ G3/G4 จริง**  
    ผู้ implement แก้ expected constants/required stringsไปพร้อม content แล้วทำให้สาม gate ผ่านได้ ทั้งยังไม่มีตัวตรวจว่า runnable command block มี expected output จาก logจริง
    - **แก้แบบ concrete:** เพิ่ม known-bad mutation tests ให้ gate ต้อง fail เมื่อใส่ Gitea/port 3000, old SCM URL, wrong Smee target, missing image หรือ wrong page map
    - เพิ่ม README structure gate/manifest เชื่อม command block ID → log evidence → normalized expected output และรัน command inventory จาก fresh devtools

17. **P5-M17 — [severity: MAJOR] [scope | feasibility] migration กับ simplification ทั้ง 6 LAB ถูกรวมใน wave เดียวโดยไม่มี regression boundary**  
    R1 ห้าม `--format` แบบกว้างอาจทำ output อ่านยากกว่าเดิม; R2 clone ทั้ง DevTools อาจเพิ่ม bandwidth; การ append `.bashrc` ตรงๆ ไม่ idempotent และ `git clone ~/DevTools` ล้มเมื่อผู้เรียนมี checkout เดิม
    - **แก้แบบ concrete:** แยก commit/wave “SCM migration” กับ “simplification”; ใช้ golden command inventory เปรียบก่อน/หลังและคง exception สำหรับคำสั่งที่รูปแบบ outputเป็นสาระ
    - วัดขนาด/เวลาของ clone ใหม่, รองรับ `~/DevTools` ที่มีอยู่ด้วย update path ชัดเจน และไม่ append export ซ้ำ (หรือไม่ persist เลย)

18. **P5-M18 — [severity: MAJOR] [interface | DoD] fallback “เปิด Poll SCM ชั่วคราว” ขัดกับ canonical end-state ของ LAB 5/6**  
    K1 แนะนำ fallback ไป Poll SCM แต่ I-05v3 และ check กำหนด Poll off; ผู้เรียนอาจจบแล็บในสถานะที่เรื่องเล่า webhook ไม่เคยถูกพิสูจน์
    - **แก้แบบ concrete:** แยก “continuity fallback” ออกจาก acceptance ชัดเจน; canonical recovery คือรอ relay connected → update hook เมื่อเปลี่ยน channel → redeliver/pushใหม่
    - หากใช้ Poll ชั่วคราว ต้องมีขั้น revert และ `check.sh` ต้องไม่ผ่านจนมี push delivery + relay POST + webhook-caused build ที่ correlate กันจริง

## Findings — MINOR

1. **P5-m01 — [severity: MINOR] [interface] I-09 ย่อ digest เป็น `20ea24c8...` ใน contract**  
   - **แก้แบบ concrete:** ใช้ digest เต็มทุก canonical location และ STACK_RESOLVED ต้องบันทึก package/Node version, architecture, created date, command line และผล reconnect ไม่ใช่เพียงแทนแถว Gitea ด้วย digest

2. **P5-m02 — [severity: MINOR] [scope] แผน authoritative สองไฟล์ขัดกันระหว่าง `PLAN.md (FROZEN)` กับ P5 DRAFT**  
   - **แก้แบบ concrete:** หลังตัดสิน critique ให้ mark P5 เป็น frozen canonical และทำ `PLAN.md` ชี้ว่า section เดิมถูก supersede; gates/agents ต้องอ่าน source เดียว ไม่แก้ประวัติ ledger ให้ดูเหมือนไม่เคยใช้ Gitea

3. **P5-m03 — [severity: MINOR] [DoD] R3 “expected output จริง” ขัดกับ R6 เมื่อ output มี username, SHA, URL และเลข build แบบ dynamic**  
   - **แก้แบบ concrete:** ล็อก normalization policy: มาจาก logจริงแต่แทนเฉพาะ `<GITHUB_USER>`, `<SMEE_URL>`, `<SHA>`, `<BUILD_NUMBER>`, elapsed time และบอกว่า redacted; block ที่เงียบให้เขียน `(ไม่มี output)` หรือกำหนด exemptionชัดเจน

4. **P5-m04 — [severity: MINOR] [dependency | feasibility] `/new` + 307 เป็น implementation detail ที่ bootstrap ยังไม่ validate**  
   - **แก้แบบ concrete:** ใช้ HEAD, อ่าน `Location`, validate scheme/host/path, จำกัด redirect และ failชัดเมื่อไม่มี header; log เฉพาะ `<SMEE_URL>` ไม่พิมพ์ channel idจริง

5. **P5-m05 — [severity: MINOR] [scope | DoD] ไม่มีนโยบายลบ/เก็บ old Gitea screenshots และ annotation specs**  
   - **แก้แบบ concrete:** สร้าง asset reachability report จาก READMEs + `tools/slides_src.html`; ลบหรือย้าย obsolete assetsออกจาก active tree, rebuild deck แล้ว assertไม่มีชื่อ/bytesของ assetเก่าฝังอยู่ พร้อมทะเบียนภาพ generated/real/masked

6. **P5-m06 — [severity: MINOR] [interface] เอกสารปัจจุบัน hardcode build #1/#2/#6 และเวลาวินาที แต่ GitHub/ping/bootstrap ทำเลขเปลี่ยนได้**  
   - **แก้แบบ concrete:** ใช้ baseline-relative `#N`/`#N+1`, SHA และข้อความ “เวลาจริงของแต่ละเครื่องต่างกัน”; caption จาก captureจริงระบุเลขเฉพาะภาพได้แต่ contract/check ห้ามผูกเลขคงที่

7. **P5-m07 — [severity: MINOR] [feasibility] timebox LAB 5/6 ยังเท่าเดิมทั้งที่เพิ่ม Smee, สอง tab, PAT และ troubleshooting ภายนอก**  
   - **แก้แบบ concrete:** วัด student-style replay ตั้งแต่ login ไม่ใช่ bootstrap; บันทึก median/slow path และปรับ 30/45 นาทีหรือย้าย account/token/channel preflight ก่อนคาบ

## Minimum revised DoD ก่อนเริ่ม build

| Gate | ต้องพิสูจน์แบบ executable |
|---|---|
| Account/auth preflight | token owner ตรง canonical login, สิทธิ์สร้าง public repo/push/hook/delivery ครบ, token ไม่ถูกเก็บหรือ echo |
| LAB 4 | public repo ที่มี ownership marker, Jenkins ไม่มี credentialsId, Poll SCM push SHA ใหม่แล้ว build cause=SCM และ checkout SHA ตรง |
| LAB 5 ping | Add hook ส่ง ping 2xx แต่จำนวน build ไม่เพิ่ม |
| LAB 5 push | GitHub push delivery SHA → relay POST 200 → GWT build exactly one → Jenkins checkout SHA เดียวกัน; Poll off |
| Relay resilience | restart outer/relay, recover URL เดิม, wait Connected, pushใหม่ผ่าน; เอกสารยอมรับว่า event ระหว่าง disconnectไม่ replay |
| LAB 6 isolation | webapp ใช้ channel/tokenคนละชุด; push webapp ไม่ trigger hello job และกลับกัน; v1→v2 ผูกกับ SHA/build/digestเดียวกัน |
| Checks/gates | positive + known-negative, authenticated API budget, zero active Gitea references, exact deck asset/page map, README command→log evidence |
| Cleanup | hooks/relay/temp/repoที่ run สร้างเหลือศูนย์; pre-existing repo ไม่ถูกแตะ; Smee channel เหลือเพียง inert identifier ที่ไม่มี active client/hook |

## คำตัดสินสุดท้าย

ให้ architect แก้ P5-B01 ถึง P5-B08 และเพิ่ม acceptance matrix ข้างต้นเข้า PLAN ก่อน freeze จากนั้นค่อย implement โดยแยก migration ออกจาก simplification pass เพื่อให้ review และ rollback ได้เป็นส่วนๆ
