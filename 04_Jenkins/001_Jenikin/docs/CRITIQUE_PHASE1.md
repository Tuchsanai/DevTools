# Adversarial Critique — Phase 1

**คำตัดสิน:** ยัง freeze แผนไม่ได้

ตรวจ `docs/PLAN.md` ฉบับ SHA-256 `9c2680bfac29170397630eae8f5ec71505db32df45dd64c8267a9286d17768c6` (แก้ล่าสุด 2026-08-19 23:13:36 UTC) ตาม Critique Contract ครบ `assumption | dependency | DoD | feasibility | scope | interface`

เกณฑ์ระดับที่ใช้:

- **blocker** — เส้นทางหลักรันไม่ได้จริง หรือ contract ขัดกันจน unit ทำงานต่อไม่ได้ถ้ายังไม่แก้
- **major** — อาจทำให้ LAB ผิดผล, integration รับของผิด, ห้องเรียนกู้สถานะไม่ได้ หรือเกิด rework ข้าม unit
- **minor** — ไม่มีรายการ; ไม่เติมข้อทักท้วงเกรดต่ำเพื่อให้ดูครบ

ข้อเท็จจริงเรื่อง Jenkins `2.568.2`, compatibility ของ Generic Webhook Trigger `2.4.2`, RAM 54 GB และ 32 cores รับตามหลักฐานที่ผู้ใช้ให้มาและไม่ตรวจซ้ำ

## หลักฐานจากการรัน

ทดลองใน outer containers `devtools-critic-wizard` และ `devtools-critic-resume` เท่านั้น ทั้งสอง container และ volume ทดลองถูกลบแล้วก่อนเขียนไฟล์นี้

| id | สิ่งที่ทดลอง | ผลจริง |
|---|---|---|
| E1 | เปิด Jenkins wizard จาก host ด้วย Playwright 1.62 | Playwright unlock ได้, ถึงหน้า Customize ใน 3.5 วินาที และ suggested plugins ถึงหน้า admin form ราว 135 วินาที จึงสรุปว่า **wizard ทำผ่าน Playwright ได้** ในเครื่องนี้ แต่ `http://172.17.0.2:8080` timeout (`curl` exit 28); เส้นทางที่ใช้ได้คือ outer port ที่ publish แล้วผ่าน `http://host.docker.internal:18080` |
| E2 | mount socket ของ inner dockerd เข้า container ที่รันเป็น root | `curl --unix-socket /var/run/docker.sock http://localhost/_ping` ตอบ `OK`; กลไก socket ใน A2 ใช้ได้จริง |
| E3 | registry อยู่แค่ `cicd-net` เทียบกับ publish inner port | `docker push localhost:5000/...` ล้ม (`connect: connection refused`, exit 1) เมื่อ registry ไม่มี `-p`; หลังรัน registry ด้วย `-p 5000:5000` push สำเร็จ exit 0 ส่วนชื่อ `registry:5000` ใช้จาก dockerd ไม่ได้ เพราะ dockerd ไม่ได้อยู่ใน container DNS ของ `cicd-net` และ HTTP registry ยังต้องจัดการ insecure policy |
| E4 | Gitea 1.27.2 ส่ง test delivery ไป Jenkins | env `GITEA__webhook__ALLOWED_HOST_LIST=*` ถูกเขียนลง `app.ini` จริง และ Gitea ติดต่อ `http://jenkins:8080/...` ได้ แต่ delivery ได้ HTTP 404 พร้อม `Did not find any jobs with GenericTrigger configured!`; แปลว่า network/allow-list ผ่าน แต่ “ติด plugin + ตั้ง URL” ยังไม่ทำให้ job ถูก trigger |
| E5 | restart outer devtools container | `docker restart devtools-critic-wizard` ทำให้ inner dockerd ไม่ขึ้น: `failed to start daemon ... /var/run/docker.pid: process with PID 11 is still running`; หลังลบ pid/socket และกู้ dockerd เอง `jenkins`, `gitea`, `registry` อยู่ `Exited (255)` ทั้งหมด การเพิ่ม `--tmpfs /run` ทำให้ dockerd กลับมาหลัง outer restart และ inner container ที่ตั้ง `--restart unless-stopped` กลับมา `Up` ได้จริง |
| E6 | verify deployed sibling จาก process ใน Jenkins | จาก Jenkins, `curl http://localhost:8000` ล้ม exit 7 แม้ sibling `webapp` publish port 8000 แล้ว; `curl http://webapp:80` ผ่านการเชื่อมต่อบน `cicd-net` (HTTP 404 เพราะ probe image ไม่มี index) จึงยืนยันว่า URL verify ต้องใช้ service DNS ไม่ใช่ Jenkins-localhost |
| E7 | H.264 post-process ตามสเปก UM | `ffmpeg 8.1.1` ใน host ถูก build ด้วย `--disable-decoder=h264`, ไม่มี H.264 encoder และไม่มี `libx264`; minimal encode จบ `Unknown encoder 'libx264'`, exit 8 |
| E8 | เทียบ convention ชุด Traefik ก่อนหน้า | capstone เดิมมี executable `check.sh`, clean re-run และ acceptance ที่ตัดสินด้วย exit code; diagram เก็บทั้ง SVG และ source `.excalidraw` ใน `slides_assets/scenes/` ขณะที่แผนใหม่นี้ยังไม่มี contract สองส่วนดังกล่าว |

แหล่งอ้างอิง upstream ที่ใช้แยก behavior ออกจากข้อสันนิษฐาน:

- [Generic Webhook Trigger — token, first run, multi-job behavior](https://github.com/jenkinsci/generic-webhook-trigger-plugin#trigger-only-specific-job)
- [Gitea — webhook delivery/test/recent deliveries](https://docs.gitea.com/usage/repository/webhooks/)
- [Gitea — `ALLOWED_HOST_LIST`](https://docs.gitea.com/administration/config-cheat-sheet/)
- [Remotion render CLI — codec, CRF, preset, bundled binaries](https://www.remotion.dev/docs/cli/render)

## 1. assumption

| ประเด็น | ระดับ (blocker/major/minor) | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| A-01 สถานะต่อเนื่องตั้งอยู่บนสมมติฐานว่า outer devtools จะไม่ถูก stop/restart เลย | **blocker** | แผนบอก “container ตัวเดียวตลอดคาบ” และห้าม recreate แต่ไม่มี resume contract; E5 พิสูจน์ว่า restart แบบปกติทำให้ dockerd ไม่ขึ้น และแม้กู้ daemon แล้ว workload ทั้งหมดไม่กลับมา `docker ps` ที่แผนใช้ตรวจยังซ่อน container ที่ `Exited` ด้วย | เพิ่ม named outer volume สำหรับ `/var/lib/docker`, `--tmpfs /run`, restart policy ให้ inner services และขั้น “resume/reset” ที่ copy ได้; หรือประกาศอย่างชัดเจนว่าเป็น one-shot session พร้อม snapshot/restore ที่ผู้สอนแจก | ทำ LAB 1–3, `docker restart devtools-jenkins`, รอ dockerd แล้ว assert Jenkins login, job history, Gitea repo และ registry catalog ยังพร้อมโดยไม่ทำ wizard/สร้างงานซ้ำ |
| A-02 A7 ถูกนิยามแค่ว่า localhost ไม่ต้องเป็น insecure registry แต่ละเลย listener ที่ inner host | **major** | E3: localhost exemption ไม่ช่วยเมื่อไม่มี process ฟัง port 5000; คำว่า registry “inner-only” ไม่บอกว่าต้อง `-p 5000:5000` ภายใน devtools | ล็อกคำสั่ง registry ให้ publish port 5000 **ภายใน outer devtools เท่านั้น** และอธิบายว่า dockerd เป็นผู้ต่อไป `localhost`; หรือเลือก registry address อื่นพร้อม daemon config ที่พิสูจน์แล้ว | cold DinD: run registry จากคำสั่ง canonical, push/pull image คนละ tag จาก Jenkins socket และตรวจ registry catalog; ต้องผ่านโดยไม่มี manual daemon edit |
| A-03 A1/A6 นับเพียง RAM/CPU และผลติดตั้งหนึ่ง instance แต่สมมติว่า update center, bandwidth และ disk ของหลาย DinD ไม่เป็นคอขวด | **major** | E1 หนึ่ง instance ใช้ suggested plugins ราว 146 MB/73 files; Jenkins image ใน inner daemonราว 290 MB และทุก DinD มี image store แยก การ fan-out และห้องเรียนจึงดาวน์โหลดซ้ำ แม้ RAM จะพอ | pre-pull/pre-warm ที่วัดได้, mirror/cache หรือ fallback image ที่มี plugin set เดียวกัน; ระบุ disk budget และ network preflight | จำลองจำนวน instance ตาม wave จริงแบบ cold cache หรืออย่างน้อยวัด total bytes/time พร้อม timeout; acceptance ต้องมี fallback ที่รันได้เมื่อ update center ช้าหรือปิด |

### สมมติฐานที่ตรวจแล้วและไม่ยกเป็นปัญหา

- A2: socket ของ inner dockerd mount เข้า Jenkins-compatible container และเรียก API ได้จริงตาม E2
- A3: env ของ Gitea มีผลจริง และ Gitea resolve/call `jenkins` ผ่าน `cicd-net` ได้ตาม E4; ควรลด allow-list จาก `*` เป็น `private` หรือ host ที่จำเป็น แต่ไม่ใช่สาเหตุที่ delivery ล้มในการทดลองนี้
- A5: Jenkins wizard ทำผ่าน Playwright ได้จริงตาม E1; ปัญหาอยู่ที่ URL/harness ของ agent ไม่ใช่ตัว wizard
- A4 และสเปกเครื่อง: รับตามหลักฐานที่ผู้ใช้ให้มา

## 2. dependency

| ประเด็น | ระดับ (blocker/major/minor) | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| D-01 Wave A ประกาศ U1–U6 ขนาน ทั้งที่ U2→U6 consume สถานะต่อกันและไม่มี bootstrap artifact | **major** | “สถานะจบ Ux” ไม่ใช่ไฟล์ที่ส่งให้ container ของอีก unit; U6 ต้องสร้าง wizard, custom Jenkins image, Gitea, repos, jobs, plugin และ webhook ใหม่เอง ขณะที่ upstream README/Jenkinsfile ยังไม่ freeze จึงทั้งซ้ำงานและเสี่ยง topology คนละชุด | ทำ runtime units เป็นลำดับ U1→U6; หรือสร้าง/freeze `tools/bootstrap/` + state manifest เป็น unit แรก แล้วให้ทุก unit consume fixture เวอร์ชันเดียวกัน | เริ่ม U6 จาก devtools เปล่าโดยใช้เฉพาะรายการ consume; ถ้าต้องเดาคำสั่งหรืออ่าน draft ของ unit ที่ยังไม่จบ แปลว่า dependency map ยังไม่ปิด |
| D-02 Wave A ต้องการ 7 units พร้อมกัน (U1–U6 + UM) แต่ execution environment มี 4 concurrency slotsรวม primary agent | **major** | เปิดพร้อมกันได้สูงสุด 3 sub-agents ไม่ใช่ 7; ตาราง wave จึงทำตามตัวอักษรไม่ได้ และ Remotion render ยังแย่ง CPU กับ DinD builds | เปลี่ยนเป็น wave ที่ไม่เกิน 3 worker เช่น gate U1 ก่อน แล้ว 2–3 units/รอบ; วาง UM ในช่วงที่ไม่ชน integration/render หนัก | dry-run scheduler แสดงทุก unit, slot และ dependency; ต้องไม่มีช่วงใด active เกิน 4 รวม orchestrator |
| D-03 “Locked stack” ยังใช้ dependency แบบ mutable | **major** | `jenkins/jenkins:lts-jdk21`, `python:3.12-slim`, suggested plugins, `Remotion 4.x ล่าสุด` และ `npx` เปลี่ยนได้; Generic Webhook Trigger ยังไม่ใส่ `2.4.2` ในตาราง การบันทึกเวอร์ชันหลัง pull ไม่ได้ทำให้ U1–U6 ที่รันขนาน resolve เหมือนกัน | freeze image digest/immutable version, `plugins.txt` พร้อม versions, Remotion exact version + `package-lock.json`; ใช้ `npm ci` แทน `npm install` ใน DoD | clean build สองรอบจาก lock/digest แล้วเปรียบเทียบ image IDs, plugin list และ `npm ls`; ต้องตรงกัน |
| D-04 resource model ไม่รวม CPU ของ Remotion และ network/disk ของ DinD | **major** | Remotion render ใช้หลาย CPU ตาม default ขณะที่ A6 ประเมินแค่ RAM; E1 แสดง download/plugin footprint ต่อ instance | ใส่ `--concurrency` ให้ render, จำกัด wave, เก็บ cold-cache size/time และกำหนด disk headroom | รัน wave ตามแผนพร้อม monitor wall time, disk และ failure; เกณฑ์ต้องระบุ threshold ไม่ใช่เพียง “ถ้าอืดลด wave” |

## 3. DoD

| ประเด็น | ระดับ (blocker/major/minor) | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| DD-01 “log มีคำสั่ง+exit code” วัด UI experiments ไม่ได้ | **major** | LAB 1, 4, 5 และ U8 มี click/wizard แต่ scope ไม่มี Playwright script/trace เป็น deliverable; screenshot ยืนยันเพียงภาพ ณ จุดหนึ่ง ไม่ยืนยัน selector, redirect, plugin failure หรือผลหลัง click | เพิ่ม script Playwright ที่ version-control ได้ต่อ flow พร้อม assertions, exit code, console/network errors และ screenshot; log อ้าง command ที่รัน script | ลบ state แล้วให้คนอื่นรัน scriptจาก README; exit 0 ต้องเกิดเมื่อ assertion ครบ และจงใจเปลี่ยน selector/HTTP response แล้วต้อง exit non-zero |
| DD-02 Integration ทดสอบเฉพาะ happy path ต่อเนื่อง ไม่ทดสอบ contract หลักเรื่อง resume | **major** | U8 fresh-run 1→6 จะไม่พบ E5 และไม่พิสูจน์ว่านักศึกษาหยุด/เปิดเครื่องแล้วเรียนต่อได้ | เพิ่ม checkpoint restart หลัง LAB 3 หรือ LAB 5 และ recovery test; ตรวจด้วย `docker ps -a` + health endpoint ไม่ใช่ `docker ps` อย่างเดียว | restart outer จริง แล้วทำ LAB ถัดไปโดยไม่ย้อน wizard/สร้าง repo ใหม่; job history และ build number ต้องต่อเนื่อง |
| DD-03 Capstone ไม่มี machine-checkable acceptance artifact | **major** | DoD ใช้ screenshot ก่อน/หลัง แต่ไม่ผูก commit → webhook → job เดียว → tests → image digest/tag → deployed version และไม่ตรวจ deploy รอบสอง/idempotency; convention เดิมมี `check.sh` ตาม E8 | ให้ U6 produce `check.sh`/Playwright+API checker และ acceptance manifest; assert build cause/number, test result, registry manifest, running container และ VERSION หลัง push สองรอบ | จงใจทำ webhook ซ้ำ, test fail, image tagผิด หรือ deploy containerค้าง แล้ว checker ต้อง fail พร้อมข้อความเฉพาะ; happy pathสองรอบต้อง exit 0 |
| DD-04 global cleanup assertion ขัดกับ parallel wave และอาจเห็น container ของ unit/session อื่น | **major** | แต่ละ agent ถูกสั่งให้แสดง `name=^devtools-` ว่าง ทั้งที่ agent อื่นใน Wave A ยังรันอยู่; แผนก็ห้ามแตะ container อื่น | ต่อ unit ตรวจ exact name ของตน เช่น `^devtools-jk3$`; global empty checkทำครั้งเดียวโดย orchestratorหลัง join และจำกัด prefixของโปรเจกต์ | รันสอง unit ซ้อนกัน ให้ unit แรกจบและผ่าน cleanup ของตัวเองแม้อีก unit ยังอยู่; global check หลังทุก unitจบต้องว่าง |
| DD-05 DoD offline/consistency ของ deck ตรวจด้วย `grep` และคำว่า “ตรง 100%” ซึ่งไม่ครอบคลุม behavior | **major** | `grep` ไม่จับ dynamic `fetch`, request จาก JS/CSS, media decode/autoplay error และไม่สร้าง canonical source สำหรับคำสั่ง/port; external reference link ยังทำให้ regex/ข้อยกเว้นกำกวม | Playwright เปิดด้วย network route ที่ abort ทุก `http(s)` request, assert zero unexpected requests/console errors; สร้าง stack/runtime manifest ให้ README และ slide consume | ทดสอบ offlineจริง, คลิกทุกหน้า/ลิงก์ LAB, เก็บ requests/console; inject `fetch()` หรือ portผิดหนึ่งจุดแล้ว test ต้อง fail |
| DD-06 DoD motion ใช้ “เฟรมแรก≈เฟรมสุดท้าย” และ screenshot autoplay ซึ่งตัดสินไม่ได้ | **major** | screenshot เฟรมกลางไม่พิสูจน์ว่าเวลาเดิน, pause เมื่อออกหน้า, loop seamless, codec/audio/pixel format หรือไฟล์เล่นครบ; A9 ก็ไม่มี performance threshold | ตรวจทุกไฟล์ด้วย metadata tool: duration/fps/codec/audio/size; วัด frame similarity ของต้น–ท้าย; Playwright assert `currentTime` เพิ่มเมื่อ active และหยุดเมื่อออกหน้า พร้อมจับ rejected `play()`/console error | รัน checker กับคลิปที่มี audio, loopกระตุก หรือ video paused; ต้อง fail แยกสาเหตุ และ deckครบ 5 คลิปต้องผ่านทั้ง offline/autoplay/pause |

## 4. feasibility

| ประเด็น | ระดับ (blocker/major/minor) | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| F-01 ขั้น post-process H.264 ของ UM รันไม่ได้ด้วย ffmpeg ที่ล็อกไว้ | **blocker** | E7 พิสูจน์ exit 8; ffmpeg 8.1.1 ตัวนี้ไม่มีทั้ง H.264 decoder และ encoder จึงอ่าน H.264 จาก Remotionแล้ว re-encode ตาม `-crf 28` ไม่ได้ | ตัด second pass และ render ตรงด้วย Remotion เช่น `--codec=h264 --crf=28 --x264-preset=slow --muted` ซึ่งใช้ bundled binaries; หรือระบุ binary H.264-capable ที่ติดตั้ง/ตรวจ license แล้ว | render คลิปแรก จากนั้น renderครบ 5 ด้วย `render.sh`; assert codec H.264, ไม่มี audio stream, ขนาด ≤ cap และเปิดใน Chromium offline ได้ |
| F-02 URL bridge IP สำหรับ agent Playwright ใช้ไม่ได้ใน execution environment นี้ | **major** | E1: direct outer bridge IP timeout แต่ published portผ่าน `host.docker.internal`; ถ้าตัด `-p` ตามแผน agent จะไม่มีทาง capture UI จาก host | agent ต้อง publish shifted ports และใช้ base URL `host.docker.internal:<port>`; student docsยังใช้ `localhost`; เพิ่ม preflight HTTP ก่อนเริ่ม Playwright | ต่อ unit curl base URL จาก process เดียวกับ Playwright แล้วต้องได้หน้า expected; ทดสอบ Jenkins และ Giteaก่อน capture |
| F-03 verify/deploy จาก Jenkins สับสน network namespace | **major** | E6: host-published 8000 ไม่ใช่ localhost ของ Jenkins; pipeline ที่ verify `localhost:8000` จะล้มแม้ browserเข้าได้ | run `webapp` บน `cicd-net` และ verifyจาก Jenkinsด้วย `http://webapp:<container-port>`; browserยังใช้ outer `localhost:8000`; แยก “caller” ให้ครบใน URL map | pipeline deployสองรุ่นและ curl service DNSจาก Jenkins; พร้อม curl outer portจาก devtools/browser side ทั้งสองต้องได้ VERSIONเดียวกัน |
| F-04 ไม่มี budget เวลาคาบ/เวลาต่อ LAB และ fallback สำหรับงาน UI/network-heavy | **major** | มี 6 stateful LAB, deck 60–80 หน้า, wizard, image/plugin downloads, Gitea installer, polling wait, plugin install และ capstoneสอง deploy; ตัวเลข wizard ~8 นาทีไม่ใช่ budgetทั้งคาบ E1 วัดเพียงเครื่องเร็วหนึ่งครั้ง | กำหนดคาบเป้าหมายและ timebox ต่อ LAB, preflight/preload, checkpoint แจกเมื่อช้ากว่า budget และแยก optional materialโดยไม่ตัด outcomeหลัก | novice dry-runแบบ cold cacheอย่างน้อย 2 คน; เก็บ p50/p90 ต่อ LAB รวมเวลาสอน/แก้ปัญหา แล้วต้องอยู่ในคาบพร้อม bufferที่ระบุ |

### สิ่งที่ตรวจแล้วและไม่เป็น feasibility blocker

- Jenkins wizard ทำผ่าน Playwright ได้จริง และ suggested plugins สำเร็จในรอบทดลอง E1
- socket path/สิทธิ์ root ทำงานจริงตาม E2
- Gitea→Jenkins DNS, allow-list และ POST ทำงานจริงตาม E4; failure อยู่ที่ job trigger configuration
- งบไฟล์ motion ตามตัวเลขล้วนมีโอกาสอยู่ใต้ 30 MB: hard cap 5×2.5 MB หลัง base64 ประมาณ 16.7 MB ก่อนรวม asset อื่น แต่ยังต้องทดสอบ decode/interaction ตาม DD-06

## 5. scope

| ประเด็น | ระดับ (blocker/major/minor) | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| S-01 concrete credentials ในเอกสารขัดกับ requirement ล่าสุดที่กำหนด placeholder-only | **major** | `xprompt1.md` ระบุห้าม email/token/username จริงและให้ใช้ placeholder แต่ PLAN กำหนด `admin`, `student`, password และ token concrete; แม้เป็น demo ก็ยังเป็นความขัดแย้งเชิง scope/DoD นอกจากนี้ outer `-p` แบบไม่ bind IP เปิด service ไป `0.0.0.0` พร้อมรหัสคงที่ | ให้ Lead ตัดสินและบันทึก exception ใน ledgerอย่างชัดเจน หรือเปลี่ยนเป็น `<JENKINS_USER>`, `<GITEA_USER>`, `<WEBHOOK_TOKEN>` พร้อมไฟล์ `.env.example`; bind student ports ที่ `127.0.0.1` | secret/identity linter ตรวจ README/slide/log; `docker port` ต้องแสดง loopback bindingถ้าเลือก concrete lab creds |
| S-02 requirement ให้ใช้ Excalidraw แต่ U7 scope มีเฉพาะ SVG ไม่มี editable scene source | **major** | xprompt กำหนด Excalidraw และ convention ก่อนหน้าเก็บ `.excalidraw` ตาม E8; ปัจจุบัน agentสามารถวาด SVGตรงโดยยังผ่าน DoD | เพิ่ม `slides_assets/scenes/*.excalidraw` ใน U7 scope/produce และ mapping scene→SVG; หรือบันทึกการยกเว้นพร้อมเหตุผล | ทุก SVG diagram ต้องมี scene sourceคู่กันและ exportซ้ำแล้ว geometry/contentหลักตรง |
| S-03 safety boundary ของเทคนิคที่สอนไม่อยู่ใน acceptance scope | **major** | แผนใช้ `--privileged`, Jenkins เป็น root, writable Docker socket, Gitea allow-all และ portเปิดทุก interface แต่ DoDไม่บังคับคำเตือน/ขอบเขต lab; ผู้เรียนอาจตีความเป็น production pattern | บังคับ calloutสั้นใน LAB 1/3/5 และ slide: disposable only, socket≈root, wildcard allow-list, loopback binding และ production alternativeหนึ่งบรรทัด | content checkหา calloutในเจ้าของหัวข้อ และ reviewว่าคำสั่ง production comparisonไม่แนะนำ socket/root/wildcardโดยไม่มีคำเตือน |

### ขอบเขตที่ตรวจแล้วและไม่พบปัญหา

- 6 LAB ไม่เกิน requirement ล่าสุดใน `xprompt1.md` ที่อนุญาตสูงสุด 7 LAB
- UM เป็น asset unit ไม่ใช่ LAB เพิ่ม จึงไม่ทำให้จำนวน LAB เกิน
- Remotion motion graphics ถูกผู้ใช้เพิ่มเป็น in-scope ใน PLAN ล่าสุด; critique นี้ไม่เสนอให้ตัดออก เพียงต้องแก้ render/test contract

## 6. interface

| ประเด็น | ระดับ (blocker/major/minor) | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| I-01 U1 ถูกห้ามแตะไฟล์นอก scope แต่ถูกสั่ง produce `docs/STACK_RESOLVED.md` | **major** | scope U1 มีเฉพาะ LAB folder, log และ screenshots ขณะที่ produce/consumer U7 พึ่งไฟล์ใน `docs/`; agentทำตามทั้งสองข้อพร้อมกันไม่ได้ | เพิ่ม `docs/STACK_RESOLVED.md` ใน scope U1 หรือย้าย ownershipให้ integration unitก่อน U7 | scope linterเทียบไฟล์ที่แก้กับ allowed paths และ U7อ่านไฟล์ที่มี ownerเดียวชัดเจน |
| I-02 “สถานะจบ LAB” ไม่ใช่ interface ที่ส่งต่อหรือ validate ได้ | **major** | mapไม่ระบุ exact run flags, restart policy, outer Docker volume, health, job/plugin state หรือ schema/version; `docker ps` หนึ่งคำสั่งไม่เห็น E5 | เพิ่ม runtime state manifest/compose/bootstrap ที่นิยาม outer flags, inner containers, volumes, network, healthchecks, plugin/job/repo state และ resume/reset transitions | validatorรันหลังทุก LABแล้วออก PASS/FAILต่อ field; สร้าง devtoolsใหม่จาก manifestและได้ preconditionเดียวกับ LABถัดไป |
| I-03 URL map ขาด actor สำคัญคือ inner dockerd และ Jenkins process→deployed app | **major** | E3/E6 แสดงว่า `localhost` หมายคนละ namespace: Docker CLI ส่ง pushให้ dockerd ซึ่งต่อ inner-host localhost แต่ `curl` ใน Jenkinsต้องใช้ `webapp` DNS | เพิ่มแถว `dockerd → registry = localhost:5000` พร้อม required inner `-p`; เพิ่ม `Jenkins process → webapp = http://webapp:<port>` และระบุ webappอยู่ `cicd-net` | connectivity matrixยิงจาก browser side, devtools shell, Jenkins container, Gitea container และ dockerd operation; ทุกช่องต้องตรง URL canonical |
| I-04 SCM contract ยังไม่ล็อก visibility/credentials/branch/job names และเจ้าของ Poll SCM | **major** | URL checkoutไม่มี credential contract; repo private/publicไม่ระบุ; default branch/credentialId/job nameไม่อยู่ map; ถ้า Poll SCMอยู่ใน Jenkinsfile U5 “ปิด polling” แล้ว buildถัดไปอาจเขียนกลับ และ U5ไม่มีสิทธิ์แก้ U4 Jenkinsfile | ล็อก repo `hello-ci`/`webapp`, visibility, `main`, Jenkins job names, credentialIdหรือ public-read, ตำแหน่ง configของ poll/trigger และ ownerที่แก้ได้ | cold setupจาก READMEแล้ว Jenkins checkoutได้; หลัง LAB5 inspect job configยืนยันไม่มี pollและ buildถัดไปไม่ทำให้ pollกลับมา |
| I-05 webhook tokenเดียวไม่ระบุ job binding/seed build และจะชนเมื่อมีหลาย job | **major** | E4 พิสูจน์ว่า endpointตอบ 404ถ้า jobยังไม่ configure; upstream pluginระบุ pipelineต้องรันหนึ่งครั้งเพื่อ apply trigger และ jobsหลายตัวที่ใช้ tokenเดียวกันจะถูกเรียกทั้งหมด PLANมี `hello-ci` กับ `webapp` แต่ tokenเดียว `cicd2569` | ใช้ tokenแยกต่อ job เช่น `cicd2569-hello`/`cicd2569-webapp` หรือ filter repo/ref; ระบุ seed build, trigger owner และปิด triggerเก่าเมื่อส่งต่อ LAB | Gitea test deliveryต้องได้ 2xxพร้อมชื่อ job; pushแต่ละ repoแล้ว build numberเพิ่มเฉพาะ jobเป้าหมายหนึ่งตัว และอีก jobไม่เปลี่ยน |
| I-06 Gitea installer fields ที่มีผลต่อ interface ไม่ถูกล็อก | **major** | ใน agent run ผ่าน shifted port ค่า default `DOMAIN`/`ROOT_URL` กลายเป็น `host.docker.internal:18080`; student runtimeต้องเป็น `localhost:3000` และ SSH clone URL defaultชี้ port 22ที่เป็น devtools SSH ไม่ใช่ Gitea | ระบุค่า installer canonical (`DOMAIN`, `ROOT_URL`, HTTP port), repo visibility และ disable Gitea SSHหรือกำหนด/publish portให้ถูก; Playwright agentต้อง overrideค่า targetเอกสาร | inspect `app.ini` หลัง install, ตรวจ clone URLsใน UI แล้ว clone/pushผ่าน URL canonicalจาก devtoolsและ checkoutจาก Jenkins |
| I-07 UM→U7 ขาด media manifest และ font contract | **major** | ชื่อ outputไม่มีนามสกุล/composition IDใน map, ไม่มี codec/pixel format/duration/hash/poster/MIME contract และ “ฟอนต์เดียวกับ deck” ทำซ้ำไม่ได้เมื่อห้ามโหลด fontจากเน็ต | ให้ UM produce exact five `.mp4`, `motion-manifest.json` และ bundled local Thai font/declared fallback; manifestมี composition ID, path, duration, fps, dimensions, codec, no-audio, bytes, SHA-256 และ poster/fallback | U7 embedจาก manifestเท่านั้น; validatorเทียบทุกไฟล์กับ manifest, ตรวจ fontไม่ออกเน็ต และ Playwrightเปิด deckบนเครื่อง cleanโดยตัวอักษรไทยไม่ล้น |

## รายการที่ต้องแก้ก่อน freeze

1. แก้ **blocker สถานะ**: outer `/run`, named Docker state, inner restart policy และ resume/reset + integration restart checkpoint
2. แก้ **blocker UM**: เลิกใช้ system ffmpeg ตัวนี้ re-encode H.264 หรือจัด binaryที่รองรับ แล้วรันคลิปจริงหนึ่งตัวก่อน
3. เปลี่ยน Wave A ให้สอดคล้อง dependency และ 4 concurrency slots; สร้าง state/bootstrap artifactหากยังต้อง parallel
4. ล็อก registry port/namespace และ app verify URL เป็น interface canonical
5. ล็อก SCM/job/credential/poll/trigger/seed build พร้อม tokenแยกต่อ job
6. เปลี่ยน DoD UI, capstone, offline deck และ motionให้เป็น executable assertions
7. ตัดสิน placeholder-vs-demo-credential และเพิ่ม Excalidraw source/safety acceptance ให้ตรง requirement

หากยังไม่แก้ข้อ 1–2 ไม่ควรเริ่ม Phase 2 เพราะเป็น failure ที่ minimal PoC แสดงแล้ว ไม่ใช่ความเสี่ยงเชิงคาดการณ์
