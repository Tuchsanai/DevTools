# CRITIQUE PHASE 4 — Final Adversarial Review

วันที่ตรวจ: 2026-08-20 UTC  
ฐานที่ตรวจ: commit `83c8cf7`  
กรอบวิจารณ์: `assumption | dependency | DoD | feasibility | scope | interface`

## คำตัดสิน

**NOT READY TO SHIP** — พบ 3 blocker, 5 major และ 1 minor โดย blocker ทุกข้อมีหลักฐานทำซ้ำได้บนสถานะปัจจุบัน ได้แก่ consistency gate ยัง exit 1, fresh devtools image ไม่มี course tree ที่ README สมมติว่ามี และมี credential ที่ยังใช้งานได้ค้างอยู่ในไฟล์ ignored/backup

การทดสอบแบบนักศึกษาเลือก LAB 4 และ LAB 5 เพราะเป็นจุดเปลี่ยน interface จาก shell → Gitea → Jenkins SCM → scheduler/webhook และมี state ต่อเนื่องมากที่สุด ผู้ตรวจสร้าง `devtools-critic4` จาก `tuchsanai/devtools:2569_1`, ใช้ SSH 2240 และ ports 20080/20300/20800 ตามโจทย์ จากนั้นทำ prerequisite LAB 1–3 และ LAB 4–5 ตามลำดับจริงโดย **ไม่ใช้** `up_to_labN` ค่า `DOCKER_USER`/`DOCKER_TOKEN` มาจาก environment และไม่ถูกพิมพ์ในหลักฐาน

## 1. Automated gates — DoD

| ประเด็น | ระดับ blocker/major/minor | หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| **P4-01 [DoD] consistency gate ปัจจุบันไม่ผ่าน** | **blocker** | `python3 tools/ui/int_consistency.py` exit **1**, สรุป `FINDING (11/12)` ที่ `003_LAB_Docker_Build_Push`: ขาด literal `docker.io/<DOCKER_USER>/ci-demo` ตาม contract ใน [`tools/ui/int_consistency.py:42`](../tools/ui/int_consistency.py#L42) ขณะที่ runnable Groovy ใช้ `docker.io/$DOCKER_USER/ci-demo` ที่ [`README.md:37`](../003_LAB_Docker_Build_Push/README.md#L37) และหน้า Hub ใช้รูป URL คนละตำแหน่ง จึงไม่ตรงตัวตรวจหลัง rewrite | (ก) เพิ่ม artifact notation แบบ placeholder ที่ canonical ลงใน LAB 3 โดยคง shell variable ในบล็อกรันจริง หรือ (ข) หากยอมรับสอง representation ให้แก้ตัวตรวจให้ normalize placeholder กับ shell variable อย่างชัดเจน | รัน test ทั้งสามจาก clean checkout; ต้องได้ exit 0 ทั้งหมด และ `int_consistency.py` ต้องสรุป `PASS (12/12)` |

ส่วนที่ไม่พบปัญหา:

- `python3 tools/ui/deck_offline_test.py` exit 0: 80 pages, external requests 0, console/page errors 0, embedded screenshots 19, inline SVG 8 และวิดีโอ 5 รายการเล่น/หยุดได้
- `python3 tools/ui/deck_consistency_test.py` exit 0: code blocks 17 รายการ, canonical URL/job/token/version, media hash, placeholder และ Poll SCM guards ผ่าน
- การเพิ่มไฟล์ critique ไม่เปลี่ยน input ของ gate; ผล rerun ปิดงานบันทึกไว้ในหัวข้อ “หลักฐานปิด environment” ด้านล่าง

## 2. การโจมตี LAB 4 และ LAB 5 — assumption, feasibility, interface

| ประเด็น | ระดับ blocker/major/minor | หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| **P4-02 [assumption/feasibility] fresh devtools ไม่มีชุดสอนที่คำสั่ง canonical ต้องใช้** | **blocker** | คำสั่งเริ่มระบบใน [`readme.md:29`](../readme.md#L29) รันเฉพาะ image และ mount `jenkins-dind`; ไม่มี bind mount, copy หรือ clone course tree หลัง SSH เข้า container ใหม่ `test -d /workspace/001_Jenikin` ให้ผลว่าไม่มี directory แต่ LAB 1 ระบุว่าผู้สอนเตรียม directory นี้ไว้ที่ [`README.md:240`](../001_LAB_Jenkins_On_Docker/README.md#L240) ผู้ตรวจจึงต้องทำ reviewer-only `docker cp` เพื่อให้ตรวจขั้นถัดไปได้ นักศึกษาที่ทำตามหน้าแรกเพียงอย่างเดียวจะใช้ `check.sh`, helper และไฟล์ LAB 4/6 ไม่ได้ | บรรจุ course tree ใน image ที่ประกาศใช้ หรือเพิ่มขั้น clone/bind mount แบบ canonical พร้อม preflight ที่หยุดทันทีเมื่อหา course root ไม่พบ | สร้าง container จาก image ใหม่ด้วยคำสั่งหน้าแรกเพียงอย่างเดียว, SSH เข้าไป และยืนยันว่า README, `tools/ui/` และ `001...006/check.sh` อ่านได้โดยไม่ inject ไฟล์นอกเอกสาร |
| **P4-03 [feasibility/interface] working directory ที่ README เปลี่ยนไว้ทำให้ helper/check ท้าย LAB หาไฟล์ไม่พบ** | **major** | LAB 4 เปลี่ยน cwd เป็น `/root/hello-ci` ที่ [`README.md:128`](../004_LAB_Pipeline_From_Git/README.md#L128); การรัน helper ที่ [`README.md:177`](../004_LAB_Pipeline_From_Git/README.md#L177) ตามลำดับจริงจึง exit 2 ด้วย `can't open file '/root/hello-ci/tools/ui/lab4_scm_job.py'` และ `cd 004_LAB_Pipeline_From_Git` ที่บรรทัด 291 exit 1 ส่วน LAB 5 เปลี่ยน cwd เป็น temp clone ที่ [`README.md:172`](../005_LAB_Webhook_Trigger/README.md#L172), ทำให้ `cd 005_LAB_Webhook_Trigger` ที่บรรทัด 229 exit 1 เช่นกัน เมื่อใช้ absolute course path ทั้งสอง `check.sh` exit 0 รูปแบบเดียวกันมีใน LAB 6: `cd ~/webapp` บรรทัด 104 ก่อนเรียก relative helper บรรทัด 149 และ final check บรรทัด 307 | กำหนด `COURSE_ROOT` ครั้งเดียวและอ้าง absolute path ทุก helper/check หรือครอบคำสั่งที่ต้อง `cd` ด้วย subshell `(cd ... && ...)` เพื่อไม่เปลี่ยน cwd ของบทเรียน | เริ่ม shell ใหม่ที่ course root แล้ว copy/paste ทุก code block ตามลำดับโดยไม่แทรก `cd` แก้เอง; บันทึก `pwd` ก่อน helper/check และยืนยันทุกคำสั่ง exit 0 ใน LAB 4–6 |
| **P4-04 [DoD/interface] LAB 5 บอกให้หา `modified` แต่ fresh commit สร้างไฟล์ใหม่จึงอยู่ใน `added`** | **major** | คำสั่ง [`README.md:172`](../005_LAB_Webhook_Trigger/README.md#L172) append ไปยัง `webhook-proof.txt` ที่ยังไม่มีและ Git รายงาน `create mode 100644` ข้อมูล `hook_task.payload_content` ของ Gitea 1.27.2 จาก delivery จริงให้ `commits[0].added` ยาว 1, `modified` ยาว 0 แต่ README สั่งค้น `commits[].modified` ที่บรรทัด 208 และ expected block บรรทัด 219 ระบุ `commits[0].modified: webhook-proof.txt` ภาพ `lab5_s08_delivery_request.png` เองเริ่มแสดง key `added` ด้านล่าง ขณะที่ [`lab5_payload.py:54`](../tools/ui/lab5_payload.py#L54) ตรวจเพียง `head_commit`, SHA และ message จึง PASS โดยไม่จับ contradiction นี้ | เลือก contract เดียว: เปลี่ยน README/expected/helper เป็น `added` สำหรับ fresh run หรือสร้างไฟล์นี้ใน LAB 4 ก่อนแล้ว LAB 5 จึงแก้ไฟล์เดิมเพื่อให้เป็น `modified` | ใช้ repo ใหม่ ทำคำสั่ง LAB 5 เพียงครั้งแรก แล้ว parse delivery ล่าสุด; assertion ต้องตรวจ array และชื่อไฟล์ตาม contract เดียวกับข้อความและภาพ |

สิ่งที่รันได้จริงเมื่อแก้เฉพาะ path เพื่อเดินหน้าตรวจ:

- LAB 4: ติดตั้ง Gitea ผ่าน UI, register `student`, สร้าง public `student/hello-ci`, push `main`, สร้าง Pipeline from SCM, manual build สำเร็จ, เปิด Poll SCM `* * * * *`, push commit และได้ build #2 จาก SCM timer; `check.sh` ผ่าน 6 จุด
- LAB 5: ติดตั้ง Generic Webhook Trigger ผ่านหน้า Available plugins และ restart Jenkins, ปิด Poll SCM, เปิด token ของ job, direct invoke สำเร็จ, Gitea test delivery HTTP 200, real push สร้าง SUCCESS build ด้วย Generic Cause; `check.sh` ผ่านเมื่อเรียกด้วย course path ที่ถูกต้อง
- prerequisite ที่ทำเองให้ runtime เดียวกัน: LAB 1 wizard + freestyle, LAB 2 builds #1–#7 และ LAB 3 negative CLI → build `jenkins-docker:2569` → credential/UI → push Hub → smoke test ล้วนสำเร็จ ไม่มีการเรียก bootstrap

## 3. README ทั้ง 6 และความน่าเชื่อถือของหลักฐาน — DoD, interface

| ประเด็น | ระดับ blocker/major/minor | หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| **P4-05 [DoD] LAB 1 มี expected output ที่คำสั่งไม่สามารถผลิต และไม่มี readiness wait ก่อน acceptance** | **major** | คำสั่ง [`README.md:68`](../001_LAB_Jenkins_On_Docker/README.md#L68) คือ `cat` ไฟล์ password จึงคืนค่า raw 32 ตัวอักษร แต่ expected block บรรทัด 74 เติมข้อความ `initialAdminPassword=... (length=32)` ซึ่งไม่ได้มาจากคำสั่งจริง; การพิสูจน์รอบนี้ได้ length 32 แต่ไม่มี prefix นอกจากนี้ขั้น restart รอเพียง inner Docker/container ที่บรรทัด 225 แล้วให้รัน check ที่บรรทัด 243 ทั้งที่ [`logs/U1R.log:36`](../logs/U1R.log#L36) บันทึกว่ารอบแรก exit 1 เพราะ Jenkins HTTP/API ยังไม่พร้อม และผ่านหลังรอ API เท่านั้น | เปลี่ยนคำสั่งให้ผลิตผลแบบ redacted/length ที่ expected อ้างจริง หรือแสดงเพียง `<32-character secret>` โดยไม่อ้าง prefix; หลัง restart เพิ่ม loop รอ Jenkins login/API ก่อนให้ SSH กลับและรัน check | fresh run อย่างน้อย 3 รอบ: diff stdout shape กับ expected โดยไม่เก็บ secret และรัน `check.sh` ทันทีหลัง readiness command; ทุกครั้งต้อง exit 0 |

ส่วนที่ไม่พบปัญหา:

- อ่าน README ทั้ง 6 ครบทั้งไฟล์และตรวจด้วยสคริปต์: reference ภาพ 61 จุด โดยเป็นภาพขั้นตอนชุด `sNN` ใหม่ 52 ภาพ; target มีจริงทุกจุดและทุกภาพตามด้วย caption
- ลำดับภาพใหม่เป็น LAB1 `s01–s06`, LAB2 `s01–s09`, LAB3 `s01–s08`, LAB4 `s01–s10`, LAB5 `s01–s08`, LAB6 `s01–s11` ไม่มีช่องว่าง ตรวจ vision แบบเจาะจงกับฟอร์ม Gitea LAB4/LAB6, webhook request/cause LAB5 และ topology D8; caption ตรงองค์ประกอบ ยกเว้นความอ่านง่ายของ D8 ที่แยกเป็น P4-08
- relative links 69 จุด resolve เป็นไฟล์จริงทั้งหมด; note `> 📝` ยาวสุด 137 ตัวอักษร จึงไม่เกิน 250; ไม่พบหัวข้อต้องห้ามหรือสำนวนสนทนาตาม `REWRITE_SPEC`
- เทียบ expected blocks กับ `logs/U1R.log`–`logs/U6R.log`, ภาพ และ runtime รอบนี้ พบ contradiction ที่พิสูจน์ได้เฉพาะ P4-04/P4-05 ข้างต้น ไม่ยัดข้อสังเกตด้านสำนวนที่ไม่มีผลต่อการเรียนเป็น finding

## 4. ความถูกต้องทางเทคนิคและ deck — dependency, interface

| ประเด็น | ระดับ blocker/major/minor | หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| **P4-06 [dependency/DoD] เอกสาร integration ทางการยังประกาศ FAIL และ version เก่า ขัดกับ resolved state** | **major** | [`docs/INTEGRATION.md:4`](./INTEGRATION.md#L4) ระบุสถานะรวม FAIL; บรรทัด 70 ระบุ Docker CLI 26.1.5 และบรรทัด 73/80 ยังเปิด VER-01 ขณะที่ [`STACK_RESOLVED.md:20`](./STACK_RESOLVED.md#L20) ล็อก Jenkins 2.568.2, Gitea 1.27.2, Docker CLI 29.7.2, GWT 2.4.2 และ [`LEDGER.md:70`](./LEDGER.md#L70) ระบุ U-FIX3 PASS เอกสารสองชิ้นจึงให้คำตอบตรงข้ามแก่ผู้อนุมัติ ship | อัปเดต integration report จาก rerun ปัจจุบัน หรือเก็บเอกสารเดิมเป็น historical report แต่ติดป้าย superseded พร้อมลิงก์ไป final integration result ที่มีสถานะเดียวกับ ledger/stack | scan version/status ข้าม README, stack, integration, ledger และ deck ต้องเหลือ canonical ชุดเดียว; rerun full/corrected gate และให้ final report อ้าง exit code ปัจจุบัน |
| **P4-08 [interface] ป้ายลูกศรใน topology D8 ทับกัน** | **minor** | เปิดดู [`logs/U7_diagram.png`](../logs/U7_diagram.png) ด้วย vision พบข้อความ `push docker.io/…` กับ `verify webapp:8000` เบียด/ทับบริเวณเส้นทาง Jenkins → Hub/webapp ทำให้อ่านความสัมพันธ์ของสอง flow ช้าลง; [`LEDGER.md:80`](./LEDGER.md#L80) ก็จด polish item เดียวกันไว้ | ย้าย label คนละด้านของเส้นหรือเปลี่ยน routing ของลูกศร แล้ว rebuild deck | render หน้า D8 ที่ resolution เดิมและตรวจ vision ว่าข้อความไม่ชนเส้น/ข้อความอื่น โดย offline/consistency tests ยัง exit 0 |

ส่วนที่ไม่พบปัญหา:

- runtime จากการทำจริงตรง `STACK_RESOLVED`: Jenkins **2.568.2**, Gitea **1.27.2**, Docker CLI ใน Jenkins **29.7.2**, Generic Webhook Trigger **2.4.2 active**; deck consistency อ่านค่าชุดเดียวกัน
- คำอธิบาย DooD ถูกต้อง: การ mount `/var/run/docker.sock` ให้สิทธิ์ใกล้เคียง root ของ Docker host ชั้นใน และ `-u root` เพิ่มผลกระทบ เอกสารจำกัดไว้ที่ disposable lab
- คำอธิบาย volume ถูกต้องกับ restart/recreate ที่รันจริง: `jenkins_home` รักษา config/build history และ outer `jenkins-dind` รักษา inner Docker state
- URL ตามผู้เรียกถูกต้องและพิสูจน์ด้วย delivery จริง: shell ใช้ `localhost:3000`, Jenkins ใช้ `gitea:3000`, Gitea ใช้ `jenkins:8080`; webhook test ได้ HTTP 200
- credential masking ไม่กล่าวเกินจริง: single-quoted Groovy, `set +x`, temporary `DOCKER_CONFIG`, `trap logout/remove` ลดการหลุดแต่ไม่ได้รับประกัน; runtime scan ไม่พบ auth ค้าง คำอธิบาย `H/1` ก็ถูกต้องกับ Jenkins 2.568.2 (`H/1` เลือกหนึ่ง hashed minute ต่อชั่วโมง ไม่เท่ากับทุกนาที)

## 5. ความปลอดภัยและความสะอาด — scope, DoD

| ประเด็น | ระดับ blocker/major/minor | หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| **P4-07 [scope/security] credential จริงที่ยังใช้ได้ค้างใน ignored backup 3 สำเนา** | **blocker** | scan แบบไม่พิมพ์ค่า ครอบคลุม working tree ทั้ง tracked/untracked/ignored (ยกเว้น `.git`) พบ exact current `DOCKER_TOKEN` และ Docker-token pattern ใน `backup/prompt1md`, `backup/xprompt1.md`, `backup/.ipynb_checkpoints/xprompt1-checkpoint.md` อย่างละหนึ่ง; token เดียวกันใช้ push LAB 3 สำเร็จในรอบนี้ จึงไม่ใช่เพียง fixture ทั้งสามไฟล์ยังมี GitHub-PAT-like candidate ซึ่งไม่ได้ทดสอบ validity เพื่อไม่ขยายความเสี่ยง [`LEDGER.md:89`](./LEDGER.md#L89) เคยรายงาน leak นี้แล้วแต่ยังคงอยู่ | revoke/rotate credential ที่เกี่ยวข้องทันที, นำไฟล์สำรองออกจาก workspace/ship artifact และตรวจว่าไม่เคยเข้า Git history; ห้ามแก้ด้วยการ ignore เพิ่มเพียงอย่างเดียว | หลัง revoke ให้ old credential authenticate ไม่สำเร็จโดยไม่พิมพ์ค่า; rerun exact-value + token-pattern scan ทั้ง working tree/history/ship artifact และ OCR ภาพ ต้องได้ 0 ทุกประเภท |
| **P4-09 [scope/DoD] สถานะ cleanup ที่เอกสารรับรองไม่ตรง workspace/host ปัจจุบัน** | **major** | [`INTEGRATION.md:96`](./INTEGRATION.md#L96) ระบุ `.ipynb_checkpoints` final count 0 และไม่มี `__pycache__`/`.pyc` แต่ปัจจุบันมี ignored `.ipynb_checkpoints/`, `backup/`, `tools/motion/__pycache__/`, `tools/ui/__pycache__/` (รวมถึง checkpoint ใต้ LAB/assets) ก่อนลบของผู้ตรวจมี lab-related volumes 19; หลังลบ `critic4-dind` ยังเหลือ pre-existing 18 volumes เช่น `jenkins-dind-*`, `u*r-jk*-dind` จึงยังกล่าวว่า host สะอาดไม่ได้ | ระบุ cleanup scope/allowlist ให้ชัด แล้วให้เจ้าของยืนยัน ownership ก่อนลบ volume เก่า; ลบ cache/checkpoint/backup ที่ไม่ใช่ deliverable และป้องกันการสร้างซ้ำ | `find` สำหรับ checkpoint/cache/temp/backup ต้องว่างตาม allowlist, `docker volume ls` ต้องเหลือเฉพาะรายการที่ประกาศคงไว้ และ final integration report ต้องบันทึก inventory จริงแทนคำว่า global cleanup แบบกว้าง |

ส่วนที่ไม่พบปัญหาและสถานะภายนอก:

- scan ไฟล์ส่งมอบ 219 ไฟล์ไม่พบ exact runtime token, Docker/GitHub PAT หรือ JWT candidate; scan working tree ทั้งหมดพบเฉพาะสามไฟล์ใน P4-07
- OCR ภาพ raster **115 ไฟล์ทั้งหมด** รวม ignored images: exact current token 0 และ token-pattern candidate 0
- ก่อน cleanup สแกนไฟล์ใน `jenkins_home`, `gitea_data` และ container logs 3,012 ไฟล์: exact token 0, Docker-token pattern 0; ไม่พบ Docker `config.json` ที่มี auth ค้าง
- Docker Hub repository `<DOCKER_USER>/critic-probe` **ยังอยู่และเป็น public** การตรวจครั้งนี้รายงานสถานะเท่านั้นและไม่ได้ลบ ตามคำสั่งว่าการลบเป็นงานถัดไป

## หลักฐานปิด environment ของผู้ตรวจ

ผล rerun บน working tree หลังสร้าง critique:

```text
tools/ui/deck_offline_test.py     -> exit 0, RESULT: PASS
tools/ui/deck_consistency_test.py -> exit 0, RESULT: PASS
tools/ui/int_consistency.py       -> exit 1, FINDING (11/12), missing LAB 3 canonical literal
```

ดำเนินการลบเฉพาะทรัพยากรที่สร้างใน Phase 4 รอบนี้:

```text
docker rm -f devtools-critic4       -> exit 0
docker volume rm critic4-dind       -> exit 0
exact container filter count       -> 0
exact critic volume filter count   -> 0
reviewer /tmp filter count         -> 0
remaining pre-existing lab volumes -> 18
```

filter ที่ใช้ยืนยัน container ว่าง:

```bash
docker ps -a --filter 'name=^/devtools-critic4$' --format 'container={{.Names}} status={{.Status}}'
```

stdout ว่าง และการนับด้วย `-q | wc -l` ได้ `0` ไม่มี container/volume ของ `devtools-critic4` เหลืออยู่

## เกณฑ์สำหรับประกาศปิดงานรอบถัดไป

1. ปิด P4-01, P4-02 และ P4-07 ก่อนทุกข้อ แล้ว rerun security scan และ test gates จาก clean checkout
2. แก้ path continuity P4-03 และ payload/evidence P4-04/P4-05 แล้วทำ student replay LAB 4–6 โดยไม่ bootstrap และไม่แทรกคำสั่งนอก README
3. ทำให้ `INTEGRATION`, `LEDGER`, `STACK_RESOLVED`, README และ deck ให้สถานะ/version เดียวกัน พร้อม inventory cleanup ที่ตรวจซ้ำได้
4. เกณฑ์ ship ขั้นต่ำคือ test ทั้งสาม exit 0, student replay/check ทุก LAB exit 0, secret scan/OCR เป็นศูนย์ และไม่มี blocker/major เปิดอยู่
