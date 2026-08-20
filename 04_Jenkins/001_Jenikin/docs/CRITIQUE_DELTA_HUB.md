# Delta Critique — Docker Hub จริง + หลักฐานบนเว็บ

ตรวจเฉพาะ delta `USR-02` ของ `PLAN v2` และไม่รื้อคำตัดสินเดิมใน ledger  
วันที่ตรวจ: 2026-08-20

## สรุปคำตัดสิน

เส้นทางหลัก **ทำได้จริง**: Access Token แลก JWT ได้, API สร้าง public repository ได้, push ได้, manifest ของ public repo ตรวจแบบไม่ login ได้ และหน้า Docker Hub Tags เปิด/capture แบบ anonymous ได้จริง

อย่างไรก็ตาม แผนยังมี 1 blocker และ major หลายจุดที่ทำให้ห้องเรียนหยุด, secret ค้างใน filesystem หรือ DoD ผ่านแบบ false-positive ได้ โดยเฉพาะลำดับ `build → login`, tag `BUILD_NUMBER` ที่ชนกันระหว่าง U0/U3/U6/U8 และ contract `DOCKER_USER`/`DOCKER_TOKEN` ที่ยังไม่ครบทุก consumer

## หลักฐานทดลองขนาดเล็ก

- ใช้ credential จาก environment ใน memory เท่านั้น ไม่พิมพ์ token/JWT และไม่เขียนลง repo
- `POST /v2/auth/token` ด้วย Access Token → HTTP 200 และได้ JWT; `POST /v2/users/login/` → HTTP 200 เช่นกัน
- `POST /v2/namespaces/<namespace>/repositories` โดยระบุ `is_private:false` → HTTP 201; อ่านกลับได้ `is_private=false`
- push `docker.io/tuchsanai/critic-probe:probe-20260820` สำเร็จ ได้ digest `sha256:69287efec03466c657ef9e44cc0e259a481476bd3b0384193854a6cad7500437`
- `docker manifest inspect` ผ่านด้วย `DOCKER_CONFIG` ว่าง จึงเป็น anonymous verification จริง
- Playwright ใช้ browser context ใหม่เปิดหน้า Tags → HTTP 200, เห็น `probe-20260820`, เห็นปุ่ม `Sign in` และไม่มี consent/anti-bot overlay; มีเพียงปุ่ม `Cookies Settings` ที่ footer ซึ่งไม่บัง tag
- local image tag, Docker config ชั่วคราว และ screenshot ชั่วคราวถูกล้างแล้ว; ไม่มี container ทดลองค้าง; **public repo/tag บน Hub ยังอยู่** ตามขอบเขตทดลองและควรลบภายหลัง: `tuchsanai/critic-probe`

เอกสารอ้างอิงหลัก: [Docker Hub API](https://docs.docker.com/reference/api/hub/latest/), [authenticate Hub API](https://docs.docker.com/docker-hub/repos/manage/export/#authenticate-with-the-docker-hub-api), [create repository](https://docs.docker.com/docker-hub/repos/create/), [Hub quickstart](https://docs.docker.com/docker-hub/quickstart/), [pull limits](https://docs.docker.com/docker-hub/usage/pulls/), [Jenkins Credentials Binding](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/)

## Assumption

| ประเด็น | ระดับ | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| ข้อความว่า `withCredentials` ทำให้ token “ถูก mask” ชวนให้เข้าใจว่าปลอดภัยเด็ดขาด | major | Jenkins mask secret ใน console แบบ best-effort เท่านั้น เอกสาร Jenkins ยังแนะนำ `set +x` และห้าม Groovy interpolation; secret ที่ถูกแปลงรูปหรือถูกโปรแกรมเขียนลงไฟล์ไม่อยู่ใต้การรับประกันนี้ ที่สำคัญ การทดลอง `docker login` แสดงคำเตือนว่าเขียน credential แบบไม่เข้ารหัสลง `config.json` ซึ่งเป็น base64 ของ `username:token` | แก้ถ้อยคำเป็น “ลด accidental disclosure ใน console” และล็อก pattern: `withCredentials` เฉพาะ push block, Groovy single-quoted shell, `set +x`, `--password-stdin`, `DOCKER_CONFIG=$(mktemp -d)`, `docker logout` + trap ลบ directory เสมอ; ห้าม `printenv`/archive Docker config | ใช้ token จริงตรวจ console/repo ด้วยตัวเปรียบเทียบที่รายงานเพียง PASS/FAIL; ตรวจทั้ง literal token และ decoded `auth` ใน Docker config โดยไม่พิมพ์ค่า แล้ว assert ไม่มี config/auth เหลือหลัง success และ forced failure |

สิ่งที่ตรวจแล้วไม่พบปัญหา:

- Docker ระบุว่า push สามารถ auto-create repository ได้ แต่เอกสาร quickstart ไม่รับประกัน visibility ของเส้นทาง auto-create; จึงไม่ควรใช้เป็น contract หลัก แผนที่บังคับสร้าง public repo ก่อน push ถูกต้อง
- API create repository ระบุ `is_private` default เป็น `false` แต่ควรส่ง `false` ชัดเจนเสมอ ผลทดลองจริงได้ public repo ตามต้องการ
- Access Token แบบ Read/Write ใช้กับ Docker CLI และแลก JWT สำหรับ Hub API ได้จริงใน account ทดลอง; ไม่ต้องเพิ่มสิทธิ์ Delete/Admin

## Dependency

| ประเด็น | ระดับ | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| account/token กลายเป็น hard gate ก่อนเรียน แต่ R5 ยังจัดการเหมือน troubleshooting ทั่วไป | blocker | ผู้เรียนที่ยังไม่สมัคร, ยังไม่ verify email, token หมดอายุ/หาย หรือไม่มี Write ทำ LAB 3 ต่อไม่ได้ และ bootstrap ก็ช่วยไม่ได้ การสร้าง account/token ระหว่าง timebox 45 นาทีพึ่ง email/2FA/บริการภายนอก | กำหนด pre-class gate อย่างน้อย 24 ชม.: login สำเร็จ, account verified, มี PAT Read/Write และสร้าง `ci-demo`/`cicd-webapp` เป็น public แล้ว; ห้าม fallback เป็น shared instructor token ให้ระบุ contingency ที่ยอมรับได้ เช่น pair/observe แล้วทำ make-up ด้วย account ตนเอง | preflight สั้นที่ไม่เก็บ token: anonymous GET หน้า repo ต้อง 200 และ login/push probe ไป tag เฉพาะผู้เรียนได้; เก็บเพียง PASS/FAIL ไม่เก็บ credential |
| ลำดับ LAB 3 เป็น `build → login → push` ทำให้ pull ของ `FROM python:3.12-slim` ยัง anonymous | major | Docker ระบุ limit 100 pulls/6h ต่อ IPv4 หรือ IPv6 /64 สำหรับ anonymous และ 200/account สำหรับ Personal; นักศึกษาหลายคนหลัง NAT เดียวและ agent หลาย daemon มีโอกาสชน 429 แม้ build ซ้ำใน daemon เดิมจะได้ประโยชน์จาก cache การ probe จาก host นี้ไม่พบ rate-limit header สำหรับ `python:3.12-slim` แต่ Docker ระบุว่าการไม่มี header อาจมาจาก publisher/network ที่ได้ unlimited จึงสรุปแทนห้องเรียนไม่ได้ | login ใน temp `DOCKER_CONFIG` **ก่อน** `docker build` เพื่อให้ base pull attributed ต่อ account, คง Docker volume/cache ระหว่างแล็บ และเพิ่ม 429/backoff เป็น preflight; ไม่จำเป็นต้องรื้อ accepted decision เรื่องไม่ทำ mirror | ก่อนสอนยิง HEAD ตามวิธี official ทั้ง anonymous/authenticated จาก network ห้องเรียนและบันทึก header เท่านั้น; dry-run พร้อมจำนวนเครื่องจริงและ cold inner daemon |
| ไม่มี owner ชัดเจนสำหรับการ provision public repos ใน automation | major | Student path ระบุสร้างผ่านเว็บ แต่ U0 DoD ต้อง chain จาก env ถึง push จริงแบบ CLI-only; env สองตัวอย่างเดียวไม่รับประกันว่า repo มีอยู่/เป็น public แม้ API path จะทำได้จริง | ล็อกหนึ่ง contract: orchestrator provision ทั้งสอง repo ก่อน W0 หรือให้ U0 idempotently GET/create ด้วย `/v2/auth/token` + `POST /v2/namespaces/.../repositories` และ assert `is_private=false`; UI creation ยังคงเป็นเนื้อหานักศึกษา ไม่ต้องสอน API | ทดสอบทั้ง fresh namespace state (404→201) และ rerun (200→no mutation) แล้ว anonymous manifest/page check |
| R5/troubleshooting ระบุเพียง 401/timeout จึงวินิจฉัย failure สำคัญผิดทาง | major | `unauthorized` มักมาจาก token ผิด/หมดอายุ; `denied: requested access` มักมาจาก namespace/repo/tag ผิดหรือไม่มี Write; pull-limit และ abuse-limit เป็น 429 คนละข้อความ; หน้า Tags 404/ว่างอาจเป็น repo private, URL/tag ผิด หรือ UI sync ช้า | เพิ่มแถวแยกอย่างน้อย: 401, denied/requested access, 429 pull-limit vs plain 429 abuse-limit, wrong `DOCKER_USER`/repo/tag, private repo/anonymous 404 และ token revoked/expired; ให้แต่ละแถวมีคำสั่งตรวจที่ไม่พิมพ์ secret | ทำ negative test ด้วย wrong namespace, token ไม่มี Write/invalid token, nonexistent tag และ private repo fixture; assert ข้อความช่วยเหลือชี้สาเหตุถูกและไม่มี secret ใน log |

## DoD

| ประเด็น | ระดับ | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| `BUILD_NUMBER` + repo กลางสองชื่อทำให้ manifest/screenshot ผ่านจาก tag เก่าหรือ push ของ unit อื่น | major | U0, U3, U6 และ U8 ใช้ Docker account เดียว แต่สร้าง Jenkins ใหม่ได้ build number ซ้ำ เช่น `1`; tag เดิมถูก overwrite หรือมีอยู่ก่อนแล้ว `manifest inspect` และภาพหน้า Tags จึงพิสูจน์เพียง “เคยมี tag นี้” ไม่ใช่ “run นี้ push สำเร็จ” | สำหรับ agent เพิ่ม run nonce ใน tag เช่น `u3-<DT_NAME>-<BUILD_NUMBER>-<nonce>`; สำหรับ flow นักศึกษาคง BUILD_NUMBER ได้ แต่ check ต้องผูก build URL/เวลา/digest ของ run ปัจจุบัน และ U6 ต้องตรวจว่า build tag กับ `latest` ชี้ digest เดียวกัน | เก็บ digest จาก push แบบไม่พึ่งข้อความอย่างเดียว แล้ว compare กับ remote manifest ของ expected unique tag; Playwright assert repo title + exact tag + last-pushed หลังเวลาเริ่ม run; rerun ต้องได้ tag ใหม่ |
| `docker manifest inspect` ใน `check.sh` ยังไม่ถูกล็อกว่า anonymous | major | คำสั่งจะใช้ credential จาก Docker config ปัจจุบันได้ ทำให้ repo ที่เผลอเป็น private ยังผ่าน แม้ requirement อาศัย public page เป็นหลักฐาน | ใน check ใช้ temporary empty `DOCKER_CONFIG` และไม่รับ `DOCKER_TOKEN`; แยกผล “remote tag exists anonymously” ออกจาก credentialed push | ทำ repo private ชั่วคราวใน fixture/negative test: authenticated inspect ต้องผ่าน แต่ check anonymous ต้อง fail; public repo ต้องผ่าน |
| DoD “token ไม่ปรากฏในไฟล์/log” ไม่มี executable proof และขัดกับ default behavior ของ `docker login` | major | Docker CLI สร้าง `config.json` ที่มี reversible base64 auth; ถ้ารันเป็น root ใน Jenkins container ไฟล์อาจค้างใน writable layer ข้าม restart แม้ console จะแสดง `****` | เปลี่ยนเกณฑ์ให้ชัดว่า “ไม่มี retained secret หลัง stage” และเพิ่ม forced-failure cleanup; สแกน repo, unit log, Jenkins console, workspace และ known Docker config paths โดยรายงานเฉพาะ count/path ที่พบ ไม่พิมพ์ match | รัน success + ทำ push ให้ fail หลัง login แล้ว assert trap ทำงาน; inspect container filesystem หลัง restart และตรวจว่าไม่มี `auths` สำหรับ Docker Hub |

สิ่งที่ตรวจแล้วไม่พบปัญหา:

- `docker manifest inspect docker.io/<user>/<repo>:<tag>` ใช้กับ public repo โดยไม่ login ได้จริง (ทดลองด้วย config ว่าง)
- หน้า `https://hub.docker.com/r/<user>/<repo>/tags` เป็นหลักฐานบนเว็บที่ใช้งานได้จริง: browser anonymous เห็น exact tag และ digest; ไม่มี banner บังจุดสำคัญในการทดลองนี้
- ข้อกำหนด screenshot U3/U6 + console push log ครอบคลุมหลักฐานสองชนิดที่เหมาะสม หากแก้ unique-tag/digest binding ข้างต้นแล้ว

## Feasibility

ไม่พบ technical blocker ของเส้นทางที่เลือก ตรวจด้วย API create จริง, push จริง, anonymous manifest inspect และ Playwright capture จริงครบแล้ว ทั้ง current auth endpoint และ legacy login endpoint ใช้ Access Token ได้ในวันที่ตรวจ

ข้อกำกับสำหรับ implementation: ใช้ endpoint ที่มีใน API reference ปัจจุบันคือ `/v2/auth/token` + Bearer JWT; legacy `/v2/users/login/` แม้ทดลองแล้วยังทำงาน ไม่ควรเป็น contract ใหม่เมื่อมี endpoint ปัจจุบันรองรับตรง ๆ และการสร้าง repo ต้องส่ง `is_private:false` ชัดเจน

## Scope

ไม่พบ scope creep ที่ควรตีกลับ: public repo, PAT, Jenkins credential, push จริง, anonymous Hub page และ screenshot เป็นงานขั้นต่ำที่ตามมาจาก USR-02 โดยตรง ส่วน API provisioning ควรอยู่เฉพาะ automation/U0 ไม่ต้องเพิ่มเป็นเนื้อหานักศึกษา

สิ่งที่ยอมรับโดยรู้ตัว: username และชื่อ repo จะปรากฏในหน้า public/screenshot และ tag ขยะจะค้างจนลบ repo; สอดคล้องกับ delta/ledger แล้ว จึงไม่เปิดประเด็นนี้ใหม่

## Interface

| ประเด็น | ระดับ | เหตุผล/หลักฐาน | ทางเลือก | วิธีพิสูจน์ |
|---|---|---|---|---|
| unit map ส่ง env creds ให้เฉพาะ U3/U6 แต่ U4/U5 consume `up_to_lab3.sh`/`up_to_lab4.sh` ซึ่งตาม U0 DoD ต้องใช้ creds | major | dependency chain ทำให้ U4 และ U5 fail-fast โดย design แม้ตารางไม่ได้ประกาศ `+ env creds`; U8 และ W0/U0 ก็เป็น consumer จริงแต่ contract กระจายอยู่คนละ section | ระบุ `requires: DOCKER_USER, DOCKER_TOKEN` ให้ U0 และทุก unit ที่เรียก bootstrap ตั้งแต่ LAB 3 ขึ้นไป (U4/U5/U6/U8); หรือแยก bootstrap state-only ออกจาก push proof ให้ consumer ที่ไม่ต้อง push ไม่ต้องรับ token | รัน dependency matrix จาก env ว่าง/มีเฉพาะ username/มีครบ และ assert unit ที่ต้องใช้ fail-fast ก่อน mutation ส่วน unit ที่ไม่ต้องใช้ไม่ขอ secret |
| mapping env → Jenkins credential → Pipeline variables ยังไม่ล็อกครบ | major | แผนล็อก credential id `dockerhub` และชื่อ env ฝั่ง orchestrator แต่ไม่ล็อก `usernameVariable`/`passwordVariable`; implementation ต่าง unit อาจใช้ชื่อคนละชุดหรือเผลอทำ Groovy interpolation | ล็อก mapping เดียว: host/agent `DOCKER_USER`,`DOCKER_TOKEN` → Jenkins Username/Password id `dockerhub` → `usernameVariable: 'DOCKER_USER'`, `passwordVariable: 'DOCKER_TOKEN'`; Pipeline ใช้ shell expansion ใน single-quoted Groovy string | static check Jenkinsfiles/config.xml + รัน job ที่ token มี shell metacharacter โดยตรวจเพียง success/absence ไม่พิมพ์ค่า |
| student → `check.sh` ขาด contract สำหรับ username และ expected tag | major | นักศึกษาเพิ่ม credential ใน Jenkins ไม่ได้แปลว่า shell ที่รัน `bash check.sh` มี `$DOCKER_USER`; ส่วน `<tag>` ของ U6 ไม่ระบุว่าจะ derive จาก last build หรือรับจาก env ทำให้ copy-paste ไม่ได้และมีโอกาสตรวจ tag เก่า | README ต้องมีคำสั่ง non-secret ชัดเจน เช่น `DOCKER_USER=<id> EXPECTED_TAG=<build-number> bash check.sh` หรือให้ check derive build number จาก Jenkins API แล้วรับเพียง username; token ต้องไม่เป็น input ของ anonymous check | เปิด shell ใหม่ที่ไม่มี Docker login/config แล้วทำตาม README verbatim; check ต้องหา exact current tag และผ่านโดยใช้เพียงข้อมูล non-secret |

ไม่ควรเพิ่ม fallback ที่ใช้ Docker password, token ในไฟล์ `.env` หรือ shared instructor token เพราะลดความปลอดภัยและทำให้หลักฐานไม่ใช่ของผู้เรียน ทาง fallback ที่สอดคล้อง requirement คือ fail-fast + pre-class remediation/make-up เท่านั้น
