# Decision Ledger — Phase 1

รูปแบบ: `id | ระดับ | คำตัดสิน | เหตุผล | หลักฐาน/ผลต่อแผน`

| id | ระดับ | คำตัดสิน | เหตุผล | ผลต่อแผน |
|---|---|---|---|---|
| A-01 | blocker | **ยอมรับ** | E5 พิสูจน์แล้วว่า restart ธรรมดาทำ dockerd + ทุก service พัง — ห้องเรียนจริงเจอแน่ | คำสั่ง canonical เพิ่ม `--tmpfs /run` + `-v jenkins-dind:/var/lib/docker` (named volume — recreate ได้ ไม่เสียสถานะ) · inner services ทุกตัวรัน `--restart unless-stopped` · readme มีหัวข้อ "กู้สถานะหลัง restart" · U8 เพิ่ม restart checkpoint |
| A-02 | major | **ยอมรับ** | E3 พิสูจน์: ไม่มี `-p 5000:5000` (ระดับ inner) → push ล้ม | คำสั่ง registry canonical ล็อกเป็น `-p 5000:5000` + URL map เพิ่มแถว dockerd→registry |
| A-03 | major | **บางส่วน** | ห้องเรียนจริง = 1 คน/1 เครื่อง โหลด ~500MB/คน เป็นเรื่องปกติของคอร์ส Docker ที่ผ่านมา — mirror/cache เกิน scope | ยอมรับ: readme ระบุ requirement (เน็ต + disk ว่าง ≥5GB) · U0 วัด/บันทึกเวลาโหลดจริง · troubleshooting มีแถว "update center ช้า" · ปฏิเสธ: local mirror (accepted risk: ถ้าเน็ตห้องเรียนล่มทั้งห้อง คอร์สนี้สอนไม่ได้อยู่แล้วทุกแล็บ) |
| D-01 | major | **ยอมรับ** | สถานะข้ามแล็บต้องเป็น artifact ที่รันได้ ไม่ใช่คำอธิบาย | เพิ่ม unit **U0 — bootstrap kit** (`tools/bootstrap/`): สคริปต์พาระบบจากศูนย์ → "จบ LAB k" (k=1..5) ใช้ทั้งโดย agent (สร้างสภาพตั้งต้น), U8 (integration checkpoint) และนักศึกษาที่ตามไม่ทัน (catch-up) · ทุก unit ปลายน้ำ consume จาก U0 เท่านั้น |
| D-02 | major | **บางส่วน** | ปฏิเสธข้อเท็จจริง "4 concurrency slots" — orchestration ของงานนี้คือ OS process อิสระ (พิสูจน์: background task หลายตัวรันพร้อมกันได้ในสภาพแวดล้อมนี้) แต่ยอมรับประเด็นการแย่ง CPU/เน็ต | Wave ใหม่: W0 = U0 + UM ขนาน → WA1 = U1,U2,U3 → WA2 = U4,U5,U6 → WB = U7 → Phase 3 = U8 · สูงสุด 3 devtools container พร้อมกัน |
| D-03 | major | **บางส่วน** | เอกสารนักศึกษาต้องใช้ tag (convention ทุกชุดก่อน + copy-paste ได้) — digest ในคำสั่งสอนคือ hostile UX · Remotion pin ได้เต็มที่ | U0 บันทึก digest + เวอร์ชันจริง + รายชื่อ plugin ลง `docs/STACK_RESOLVED.md` (เจ้าของไฟล์ = U0 คนเดียว — ตอบ I-01 ด้วย) · Remotion: pin เวอร์ชัน exact + commit `package-lock.json` + `npm ci` · ปฏิเสธ plugins.txt เป็นทางเดินนักศึกษา (wizard คือจุดสอน) แต่ bootstrap ใช้ plugin list ที่ freeze แล้วได้ |
| D-04 | major | **บางส่วน** | ยอมรับ: จำกัด `--concurrency` ตอน render + batch ละ 3 · ปฏิเสธ: ระบบ monitor threshold (เครื่อง build เครื่องเดียว log พอ) | UM spec เพิ่ม `--concurrency=8` · เวลาจริงบันทึกใน log |
| DD-01 | major | **ยอมรับ** | screenshot อย่างเดียวพิสูจน์ flow ไม่ได้ | ทุก unit ที่มีขั้น UI ต้องส่ง Playwright script ใน `tools/ui/` (มี assertion + exit code) — ส่วนใหญ่ได้จาก U0 อยู่แล้ว · log ต้องอ้างการรัน script |
| DD-02 | major | **ยอมรับ** | fresh-run อย่างเดียวไม่เจอ E5 | U8 เพิ่ม 2 checkpoint: หลังจบ LAB 3 และ LAB 5 → `docker restart devtools-…` → services กลับมาเอง + job history/repo อยู่ครบ โดยไม่ทำ wizard ซ้ำ |
| DD-03 | major | **ยอมรับ** | convention ชุด Traefik มี `check.sh` จริง (E8) | **ทุกแล็บ** มี `check.sh` ตรวจสถานะจบแล็บ (exit code) · ของ LAB 6 เป็น acceptance เต็ม: webhook 2xx → build cause → pytest → registry manifest → VERSION ใหม่บนเว็บ → push รอบสองซ้ำได้ |
| DD-04 | major | **ยอมรับ** | ตรวจ global ระหว่าง wave ขนานจะ fail ผิด ๆ | ต่อ unit: ตรวจ `^devtools-jk<N>$` ของตนเท่านั้น · global check เป็นหน้าที่ orchestrator (Claude) ท้ายแต่ละ wave และตอนจบ |
| DD-05 | major | **บางส่วน** | grep จับ dynamic request ไม่ได้ — จริง | ยอมรับ: U7 DoD เปลี่ยนเป็น Playwright offline test (abort ทุก http(s) request, ไล่ทุกหน้า, assert 0 external request + 0 console error + video เล่น/หยุดถูกหน้า) · ปฏิเสธ: runtime manifest ที่ README+slide consume ร่วม (over-engineering — Phase 3 ตรวจ consistency ด้วยมือ+สคริปต์เทียบเฉพาะจุด, accepted risk) |
| DD-06 | major | **ยอมรับ (ปรับวิธี)** | เกณฑ์ต้องรันได้จริงบนเครื่องนี้ — host decode H.264 ไม่ได้ จึงใช้ chromium (decode ได้) เป็นเครื่องตรวจแทน ffmpeg | UM ส่ง `motion-manifest.json` (duration/fps/ขนาด/codec/no-audio/bytes/sha256) + `tools/motion/validate.py`: อ่าน metadata + Playwright เปิดคลิป: assert autoplay(muted), `currentTime` เดิน, จับเฟรม t=0 กับ t=end เทียบด้วย PIL (loop เนียน = diff ต่ำ) |
| F-01 | blocker | **ยอมรับ** | E7 exit 8 — ffmpeg เครื่องนี้ไม่มี H.264 ทั้ง encode/decode | ตัดขั้น ffmpeg ทิ้ง — render ตรงจาก Remotion: `npx remotion render --codec=h264 --crf=28 --x264-preset=slow --muted` (ใช้ binary ที่ Remotion bundle มาเอง) · ขนาดเกิน cap → ปรับ crf ใน render ไม่ใช่ post-process |
| F-02 | major | **ยอมรับ** | E1: bridge IP timeout ใน environment นี้ — ต้องใช้ published port ผ่าน `host.docker.internal` (ขัด memory เก่า — สภาพแวดล้อมเปลี่ยน จะแก้ memory ด้วย) | กติกา agent: ต้อง publish shifted ports + base URL = `http://host.docker.internal:<shifted>` + preflight `curl` ก่อนเริ่ม Playwright · เอกสารนักศึกษายังใช้ `localhost` |
| F-03 | major | **ยอมรับ** | E6 พิสูจน์: localhost ใน Jenkins ≠ inner host | Jenkinsfile capstone ล็อก verify = `http://webapp:8000` (webapp อยู่บน `cicd-net`) · URL map เพิ่มแถว |
| F-04 | major | **บางส่วน** | ยอมรับ: กำหนด timebox/แล็บ + แบ่ง 2 ครั้งเรียน (LAB 1–3 / LAB 4–6) + catch-up ด้วย bootstrap (จาก D-01) · ปฏิเสธ: dry-run กับผู้เรียนจริง 2 คน — ไม่มีผู้เรียนใน build loop นี้ (accepted risk: ปรับ timebox หลังสอนรอบแรก) | readme ระบุ: LAB1 40' · LAB2 30' · LAB3 45' · LAB4 40' · LAB5 30' · LAB6 45' |
| S-01 | major | **ปฏิเสธ (บันทึก exception)** | กติกา placeholder มุ่งกัน **ของจริง** (email/token/username จริง) — `admin/admin2569` เป็น fixture ของแล็บ local ไม่ใช่ secret จริง · placeholder จะทำลาย copy-paste-ability ซึ่งเป็นกติกาเอกสารข้อบังคับ · ชุดก่อน ๆ ใช้ demo creds แบบเดียวกัน | คง demo creds · เพิ่ม (จาก S-03) callout "แล็บเท่านั้น" · ปฏิเสธ bind 127.0.0.1 (เพิ่ม noise ทุกคำสั่ง — นักศึกษารันบนเครื่องตัวเองหลัง NAT; บันทึกเป็น accepted risk) |
| S-02 | major | **ปฏิเสธ** | convention ล่าสุดของ repo นี้คือ **SVG-edit-not-reimport** (บันทึกใน memory ชุด Dockerfile 2569): SVG คือ source of truth แก้ตรง ไม่ round-trip ผ่าน .excalidraw ซึ่งเคยสร้างปัญหา — ชุด Traefik เป็น convention เก่ากว่า | U7 เขียน SVG inline ตรง (โทน/ลูกศร/ฟอนต์ตามกติกา deck เดิม) |
| S-03 | major | **ยอมรับ** | ถูก และถูกมาก — เทคนิคที่สอน (privileged, sock=root, wildcard) อันตรายถ้าเข้าใจว่าเป็น production pattern | LAB 1/3/5 + slide มี callout 1–2 บรรทัด: ทำไมเป็นท่าแล็บ + production ใช้อะไรแทน (agent/JCasC/least-privilege) — เป็นข้อบังคับใน DoD เนื้อหา |
| I-01 | major | **ยอมรับ** | scope ขัดกันจริง | เจ้าของ `docs/STACK_RESOLVED.md` = **U0** (สอดคล้อง D-03) · U1–U7 อ่านอย่างเดียว |
| I-02 | major | **ยอมรับ** | interface ต้อง executable | "สถานะจบ LAB N" ≡ `tools/bootstrap/up_to_labN.sh` (สร้าง) + `00N_LAB_*/check.sh` (ตรวจ) — สคริปต์คือ manifest |
| I-03 | major | **ยอมรับ** | E3/E6 | URL map v2 เพิ่ม: `dockerd → registry = localhost:5000 (registry ต้องรัน -p 5000:5000)` และ `Jenkins (verify) → webapp = http://webapp:8000` |
| I-04 | major | **ยอมรับ** | SCM contract ต้องล็อก | ล็อก: repo `student/hello-ci`, `student/webapp` เป็น **public** (checkout ไม่ใช้ credential — ใน scope นี้) · branch `main` (`git config --global init.defaultBranch main` อยู่ใน LAB 4) · job: `hello-ci-pipeline`, `webapp-deploy` · trigger ตั้งผ่าน **job UI** (ไม่ใช่ `triggers{}` ใน Jenkinsfile) → LAB 5 ปิด polling ได้โดยไม่แตะไฟล์ของ LAB 4 และไม่ต้องมี seed-build quirk |
| I-05 | major | **ยอมรับ** | E4 + doc upstream: token เดียวหลาย job = ยิงโดนหมด | token แยก: `cicd2569-hello` (job hello-ci-pipeline), `cicd2569-webapp` (job webapp-deploy) · trigger ผ่าน UI จึง apply ทันทีที่ save (ไม่มี seed build) — LAB 5 มีขั้น "Build Now ครั้งเดียวเพื่อยืนยัน" อยู่แล้วในเนื้อเรื่อง |
| I-06 | major | **ยอมรับ** | ค่าติดตั้ง Gitea รั่วตาม URL ที่ agent ใช้จริง | ล็อก installer: DOMAIN=`localhost` · ROOT_URL=`http://localhost:3000/` · ปิด SSH (`GITEA__server__DISABLE_SSH=true`) · allow-list ใช้ `GITEA__webhook__ALLOWED_HOST_LIST=private` (แคบกว่า `*` ตามข้อเสนอ) · agent ต้อง override ค่าใน form ให้ตรง canonical แม้ตัวเองเข้าผ่าน host.docker.internal |
| I-07 | major | **ยอมรับ** | contract สื่อกลางต้องชัด + ฟอนต์ไทยใน video ต้อง bundle | UM ส่ง `slides_assets/motion/motion-manifest.json` + ฟอนต์ไทย OFL (Noto Sans Thai/Sarabun .ttf) ใน `tools/motion/fonts/` โหลดผ่าน staticFile — ไม่โหลดจากเน็ตตอน render · U7 embed ตาม manifest เท่านั้น |

## การเปลี่ยนแปลงตามคำสั่งผู้ใช้ (Phase 2)

| id | คำสั่ง | ผลต่อแผน |
|---|---|---|
| USR-01 (2026-08-19) | ฝังวิดีโอ Remotion autoplay ใน slide | เพิ่ม unit UM (ทำแล้ว — PASS) |
| USR-02 (2026-08-20) | push image ขึ้น **Docker Hub จริง** + **capture หลักฐานว่า push แล้วจริง** | ตัด `registry:2.8.3` ออกทั้งชุด (หลักฐาน E3/A-02/I-03 ส่วน registry local = superseded) · LAB 3 เพิ่มเนื้อหา Access Token + Jenkins Credentials (`dockerhub`) + push `docker.io/<DOCKER_USER>/ci-demo` · LAB 6 push `cicd-webapp:BUILD_NUMBER`+`latest` · screenshot ใหม่: `lab3_hub_tags`, `lab6_hub_tags` (หน้า Hub tags จริง) · check.sh ใช้ `docker manifest inspect` · agent รับ creds จริงผ่าน env เท่านั้น (เอกสาร = placeholder) · U0 ถูก stop กลางคันแล้ว relaunch ด้วยสเปกใหม่ (ไฟล์สคริปต์เดิมใช้ต่อ+patch) · delta-critique สั่งเพิ่ม → `docs/CRITIQUE_DELTA_HUB.md` |

| id | ระดับ | คำตัดสิน | เหตุผล | ผลต่อแผน |
|---|---|---|---|---|
| USR-03 (2026-08-20) | คำสั่งผู้ใช้ | เรียบเรียง README ทุก LAB: โทนวิชาการ (ไม่เอาแนวเพื่อน) + เพิ่ม screenshot ขั้นตอน Jenkins แบบไม่ขาดช่วง + ตรวจภาพด้วย cyolo gpt-5.6-sol/medium (ประหยัด token Claude) → spec: docs/REWRITE_SPEC.md · fan-out U1R–U6R (medium) 2 ชุด · Phase 4 adversarial review เลื่อนไปตรวจฉบับหลังเรียบเรียง |
| UM-01 | minor | **ยอมรับ** | Remotion 4.0.513 ห้าม `_` ใน Composition.id — พิสูจน์ตอน build | manifest ใช้ id แบบ dash (`mo-intro`) ชื่อไฟล์คง `mo_*.mp4` · U7 ต้องอ่านจาก manifest เท่านั้น |

## Delta critique — Docker Hub (docs/CRITIQUE_DELTA_HUB.md, 2026-08-20)

| id | ระดับ | คำตัดสิน | เหตุผล → ผลต่อแผน |
|---|---|---|---|
| DH-01 (masking wording) | major | **ยอมรับ** | ล็อก Push-block canonical ใน PLAN §4: single-quote groovy + `set +x` + temp `DOCKER_CONFIG` + trap logout/ลบ + ถ้อยคำ "ลดการหลุด" ไม่ใช่การันตี |
| DH-02 (pre-class gate) | blocker | **ยอมรับ (จัดการในสื่อ)** | readme + LAB 3 มีกล่อง prerequisite ทำล่วงหน้าก่อนคาบ (สมัคร/verify/token RW/สร้าง repo public) + preflight 2 คำสั่ง · ไม่มี shared instructor token · การบังคับ 24 ชม.เป็นเรื่อง process ของผู้สอน (นอกเหนือ build นี้) |
| DH-03 (login ก่อน build) | major | **ยอมรับ** | ลำดับใน Push-block: login → build → push (pull base attributed กับ account) |
| DH-04 (repo provisioning owner) | major | **ยอมรับ** | `up_to_lab3.sh` ensure-repo ผ่าน Hub API idempotent (`is_private:false` ชัดเจน) · นักศึกษาสร้างทางเว็บ |
| DH-05 (troubleshooting แยกอาการ) | major | **ยอมรับ** | LAB 3 ตารางต้องมี 401 / denied / 429 สองแบบ / private-404 |
| DH-06 (BUILD_NUMBER collision → false positive) | major | **ยอมรับ (วิธี digest+timestamp)** | ไม่เปลี่ยน tag scheme ที่สอน — check.sh ผูก digest ของ run ปัจจุบัน + `last_updated` จาก Hub API · LAB 6 เทียบ digest ของ tag build กับ latest · ปฏิเสธ nonce ใน tag ของ pipeline นักศึกษา (เปลี่ยนเนื้อหาที่สอนโดยไม่จำเป็น) |
| DH-07 (inspect ต้อง anonymous) | major | **ยอมรับ** | ทุกการ verify ใช้ `DOCKER_CONFIG=$(mktemp -d)` |
| DH-08 (retained secret proof) | major | **ยอมรับ** | trap ลบ config เสมอ + check สแกน pattern `dckr_pat_` ใน log/ไฟล์ (รายงานจำนวน ไม่พิมพ์ค่า) + ตรวจไม่มี `auths` ค้างใน jenkins container |
| DH-09 (env contract U4/U5/U8) | major | **ยอมรับ** | PLAN §7 ระบุ U0,U3–U6,U8 ต้องได้รับ env creds |
| DH-10 (lock variable mapping) | major | **ยอมรับ** | `usernameVariable:'DOCKER_USER'` / `passwordVariable:'DOCKER_TOKEN'` ตายตัวใน Push-block canonical |
| DH-11 (student check contract) | major | **ยอมรับ** | `DOCKER_USER=<id> bash check.sh` — token ไม่ใช่ input |

## ตรวจรับ Phase 2

| unit | คำตัดสิน | หมายเหตุ |
|---|---|---|
| UM | **PASS** | ตรวจไขว้เองแล้ว: sha256 ตรง manifest, h264 720p30 ไม่มีเสียง, 5 คลิปรวม ~740KB · UM-01 ยอมรับ |
| U4 | **PASS** | ทุก DoD ผ่าน + negative check · critique U4-01 **ยอมรับ**: `H/1 * * * *` ถูก Jenkins hash เป็นนาทีตายตัว (หลักฐาน polling log) → canonical เปลี่ยนเป็น `* * * * *` (แก้ PLAN แล้ว, U-PATCH แก้ README/check ของ LAB 4 + bootstrap) · critique U4-02 **ยอมรับ**: fixture hello-ci ของ U0 ต้อง sync กับของจริง LAB 4 (4 stages + hello.sh + expected.txt) → U-PATCH |
| U-PATCH | **PASS** | drift ทุกจุดแก้แล้ว + เจอและแก้ drift LAB 1/2 เพิ่มเอง · fresh chain + **check.sh ไขว้ครบ 5 ชั้น exit 0 ทุกตัว** (ปิดเงื่อนไข U0 DoD ข้อ 1) · idempotent ✓ token ✓ cleanup ✓ · เศษ `H/1` เหลือ 2 ไฟล์นอก scope → U-PATCH2 (micro) |
| U-FIX3 | **PASS** | U3-01: credential first-run exit 0 (ทดสอบซ้ำสด) · VER-01: Docker CLI 29.7.2 ตรงทั้ง bootstrap/STACK/LAB6/deck (rebuild + tests ผ่าน) · +micro-fix int_consistency.py → 12/12 PASS |
| U1R | **PASS** | README LAB 1 ฉบับวิชาการ 279 บรรทัด + ภาพขั้นตอนใหม่ 6 (vision-verified โดย agent) · check.sh ผ่าน · hash คำสั่งเดิมตรง · สุ่มตรวจโทน: 0 คำ casual |
| U2R | **PASS** | README LAB 2 วิชาการ 383 บรรทัด + ภาพขั้นตอน 9 (s01 New Item → s09 prod graph, vision-verified) · check.sh #7 SUCCESS 4 stages · Jenkinsfile/check ไม่ถูกแตะ · โทน clean |
| U3R | **PASS** | README LAB 3 วิชาการ 310 บรรทัด + ภาพ 8 (เส้นทางเมนู Credentials ครบ, console login masked/digest, hub public tag) · token/auth ค้าง = 0 · ภาพเดิม SHA ไม่เปลี่ยน · check.sh ผ่าน |
| U4R | **PASS** | README LAB 4 วิชาการ 306 บรรทัด + ภาพ 10 (installer→repo→SCM config→Poll→SCM change) · anchor `* * * * *`/ห้ามใช้ H/1 คงอยู่ · check.sh ผ่าน · โทน clean |
| U5R | **PASS** | README LAB 5 วิชาการ 252 บรรทัด + ภาพ 8 (plugin→trigger token→webhook form→delivery 200→cause) · check.sh ผ่าน · leakage 0 · โทน clean |
| U6R | **PASS** | README LAB 6 วิชาการ 333 บรรทัด + ภาพ 11 (s01–s11 ครบวง v1→v2 รวม console pytest/verify) · anchors ครบ · check.sh acceptance ผ่าน · ภาพเดิม hash เดิม · leakage 0 |
| UA2 | **PASS** | LAB 3–4 annotate ครบ (vision-verified, deck files เดิมไม่ถูกแตะ) |
| U-FINAL | **PASS → SHIP** | ปิด P4-01..06, 08, 09 ครบ: clone+COURSE_ROOT convention พิสูจน์จาก fresh devtools · student replay LAB 4–6 ผ่านทุกบล็อก · payload=added · gates 3 ตัว exit 0 (int 12/12 — orchestrator รันซ้ำยืนยันเอง) · critic-probe บน Hub = 404 · containers/volumes ทดสอบ = 0 · **คงเหลือ P4-07 (action ผู้ใช้): rotate DOCKER_TOKEN+GIT_TOKEN และลบสำเนาใน backup/** |
| UA1 | **PASS** | เครื่องมือ annotate + LAB 1–2 (idempotent ยืนยัน SHA) · ผมตรวจตัวอย่างเอง: marker 3 จุด+เลขลำดับ+ป้ายไทยตรงเป้า · commit 8d66902 |
| UA3 | **PASS** | LAB 5–6: annotate 5 ภาพ action, เว้นภาพหลักฐาน 8 พร้อมเหตุผลราย ภาพ (vision-verified) |
| U8 | **FAIL → FIX เฉพาะจุด** | ผ่าน: chain 1→6 + check.sh ทุกแล็บ + restart checkpoint ×2 + capstone e2e + consistency 12/12 + cleanup global · Findings: **U3-01** (lab3_credential.py แพ้ race รอบแรก) และ **VER-01** (Docker CLI 26.1.5 Debian repo ใน bootstrap vs 29.7.2 official repo ใน LAB 3 → STACK/LAB6/deck คัดค่าเก่า) · คำตัดสิน: canonical = official Docker repo · แก้โดย U-FIX3 + re-proof เฉพาะจุด (ไม่ re-run เต็มเพราะ findings จำกัดวง มีหลักฐาน chain ส่วนอื่นครบแล้ว) |
| U7 | **PASS** | ตรวจไขว้ภาพหลักฐาน: ปก+overview grid+D8 topology ถูกต้องสวยงาม · 80 หน้า 6.0MiB · offline test 0 external req/0 error · วิดีโอ 5 เล่น/หยุดตามหน้า · consistency 17 code blocks ผ่าน + guard กัน H/1 ถดถอย · polish item (Phase 4, minor): ป้ายลูกศร push/verify ใน D8 ทับกันเล็กน้อย |
| U-PATCH2 | **PASS** | เศษ `H/1` ในโค้ดหมดแล้ว (เหลือเฉพาะบรรทัดสอน/guard ที่ตั้งใจ) · py_compile ผ่าน |
| **U-PATCH (แผนเดิม)** | — | รวมแก้ drift ทั้งหมดใน bootstrap: job xml docker-build-push ให้ตรง LAB 3 (จาก U3) · hook cause/field normalize (จาก U5) · fixture hello-ci + poll spec (จาก U4) · แล้วพิสูจน์ fresh chain up_to_lab4/5 + รัน check.sh ของ LAB 1–5 ไขว้ (ปิดเงื่อนไข U0 DoD ข้อ 1 ไปในตัว) |
| U5 | **PASS** | push→build อัตโนมัติใน 10.5 วิ (cause Generic Cause) · delivery HTTP 200 · check.sh positive+negative · drift เล็กของ U0 (ข้อความ cause + field XML ของ plugin) → รวมเข้า **U0.2** (check.sh รองรับสองแบบแล้ว ไม่ block) |
| U6 | **PASS** | ตรวจไขว้ภาพ: dashboard v1 (blue, BUILD #1, 01:22:46) → v2 (green, BUILD #2, 01:24:25, hostname ใหม่) = วง push→webhook→test→build→push Hub→deploy จบใน ~100 วิ · Push-block canonical ตรง + pytest-ก่อน-push + latest digest ตรง build · check.sh acceptance ผ่าน positive+negative · หมายเหตุ: ตัวตรวจ delivery อ่านตาราง hook_task ของ Gitea 1.27.2 (ไม่มี REST endpoint) — จดเป็นข้อจำกัดเวอร์ชัน |
| U3 | **PASS** | ตรวจไขว้: `lab3_hub_tags.png` = หน้า Hub จริงแบบ anonymous เห็น tags 1–5 เพิ่ง push + digest (หลักฐานตาม USR-02) · Jenkinsfile ตรง Push-block canonical · token scan 0 · check.sh มี negative case · critique drift ของ bootstrap job xml (แอป/ลำดับ smoke ไม่ตรง LAB 3) = **ยอมรับ → คิวงาน U0.2** หลัง Wave A2 (ไม่กระทบ U4–U6 เพราะไม่ได้ใช้ job นี้) |
| U2 v2 | **PASS** | ตรวจไขว้: Pipeline Graph จริง (build #7, 4 stages + post เขียว, Jenkins 2.568.2) · README 274 บรรทัด 7 การทดลอง · check.sh ใช้ core API + `/stages/tree` ของ pipeline-graph-view (บันทึกเหตุผลในไฟล์) · เงื่อนไข: check ตรวจ build ล่าสุดต้องเป็นรอบ APP_ENV=prod (ตรง flow เอกสาร) · container สะอาด |
| U1 | **PASS** | ตรวจไขว้: README 225 บรรทัด ตรง template + canonical + safety callout · screenshot 4 รูปเป็น Jenkins 2.568.2 จริง · check.sh พิสูจน์ทั้ง exit 0 และ negative case · container สะอาด |
| U2 (รอบแรก) | **BLOCKED → ตัดสินแล้ว relaunch** | critique U2-01 **ยอมรับ**: suggested set ของ 2.568.2 ไม่มี pipeline-stage-view/wfapi — มี `pipeline-graph-view` แทน (หลักฐาน: plugin API ใน logs/U2.log) · เลือกสอน Pipeline Graph ของ stock (ปฏิเสธการเพิ่ม plugin legacy — ขัด D-03 และ UI เก่า deprecated) · screenshot เปลี่ยนชื่อเป็น `lab2_pipeline_graph.png` · check.sh ให้ใช้ API ที่มีจริง (pipeline-graph-view หรือ Jenkins core API) — U2 v2 เลือกและบันทึก |
| U0.1 | **PASS** | job xml ตรง Push-block canonical แล้ว (ตรวจไขว้ยืนยัน) · chain ถึง LAB 3 ผ่าน · เงื่อนไขของ U0 ปิดแล้ว · ⚠️ พบ token จริงค้างใน `prompt1md`/`xprompt1.md`/.ipynb_checkpoints (ไฟล์ผู้ใช้ นอก scope) — **ต้องกันออกจาก commit + แจ้งผู้ใช้ตอนปิดงาน** |
| U0 | **PASS (มีเงื่อนไข)** | chain 0→LAB5 ผ่านจริง (push Hub + webhook), idempotent, token scan = 0 · DoD ข้อ 1 แก้ถ้อยคำ (ไขว้ check.sh → U8, dependency cycle จริงตามที่ U0 ชี้) · เงื่อนไข: **U0.1** patch jobs/docker-build-push.xml ให้ตรง Push-block canonical (ตอนนี้ใช้ USER/PASS, ไม่มี set +x/temp DOCKER_CONFIG — เขียนก่อน canonical ถูก freeze) + พิสูจน์ซ้ำถึง lab3 · critique ของ U0 เรื่อง LAB_TEMPLATE ตกค้าง registry/token เก่า = ยอมรับ แก้แล้ว |

หมายเหตุ cleanup: critique สร้าง repo ทดลอง `tuchsanai/critic-probe` ค้างบน Hub — **ต้องลบใน Phase 4/cleanup สุดท้าย** (repos `ci-demo`/`cicd-webapp` เก็บไว้เป็นหลักฐานจริงตามที่ผู้ใช้ขอ)

## Phase 4 Final Review (docs/CRITIQUE_PHASE4.md @83c8cf7) — คำตัดสิน

| id | ระดับ | คำตัดสิน | การจัดการ |
|---|---|---|---|
| P4-01 consistency gate exit 1 | blocker | **ยอมรับ (ทาง ก)** | LAB 3 README เพิ่มบรรทัด artifact canonical `docker.io/<DOCKER_USER>/ci-demo:<BUILD_NUMBER>` (สอน naming contract ไปในตัว) → gate ต้อง 12/12 |
| P4-02 fresh devtools ไม่มี course tree | blocker | **ยอมรับ** | canonical ใหม่: หลัง SSH ให้ clone repo สาธารณะแบบ sparse/depth-1 → `COURSE_ROOT=~/DevTools/04_Jenkins/001_Jenikin` (readme + LAB 1) + preflight ตรวจ course root |
| P4-03 cwd drift ทำ helper/check พัง | major | **ยอมรับ** | ใช้ `COURSE_ROOT` + รูปแบบ subshell `(cd "$COURSE_ROOT/..." && bash check.sh)` ทุกจุดใน LAB 4/5/6 |
| P4-04 LAB 5 modified vs added | major | **ยอมรับ** | แก้ README/expected/helper เป็น `added` (ตรง delivery จริง+ภาพ) |
| P4-05 LAB 1 expected แต่งรูปแบบ + ไม่มี readiness wait | major | **ยอมรับ** | expected เป็นรูปแบบ redacted ของ output จริง + เพิ่ม loop รอ Jenkins พร้อมหลัง restart ก่อน check |
| P4-06 INTEGRATION.md ขัดสถานะจริง | major | **ยอมรับ** | เพิ่มส่วน "Final status (superseded)" อ้าง U-FIX3/UPATCH + เวอร์ชัน 29.7.2 + gate ปัจจุบัน |
| P4-07 token จริงใน backup/ (3 สำเนา) | blocker | **บางส่วน** | ตรวจแล้ว: `backup/` ถูก ignore + ไม่เคยเข้า git history (0 tracked) → ไม่มี exposure ทาง repo · ไฟล์เป็นของผู้ใช้ — ไม่ลบเอง · **action ผู้ใช้: rotate DOCKER_TOKEN + GIT_TOKEN และลบสำเนา backup หลังจบงาน** (แจ้งในสรุปปิดงาน) |
| P4-08 ป้าย D8 ทับกัน | minor | **ยอมรับ** | แก้ตำแหน่ง label ใน slides_src + rebuild + gates |
| P4-09 volume/junk ค้าง + INTEGRATION กล่าวเกิน | major | **ยอมรับ** | orchestrator ลบ lab volumes 18 ลูก + junk dirs แล้ว (เหลือ 0) · INTEGRATION ส่วน Final ใส่ inventory จริง |

## Accepted risks (สรุป)

1. เน็ตห้องเรียนล่มทั้งห้อง → คอร์สนี้เดินไม่ได้ (เหมือนทุกแล็บ Docker ก่อนหน้า) — ไม่ทำ mirror
2. Timebox ต่อแล็บมาจากการประเมิน + การรันของ agent ไม่ใช่ผู้เรียนจริง — ปรับหลังสอนรอบแรก
3. Consistency slide↔README ใช้การตรวจ Phase 3/4 (สคริปต์เทียบจุดสำคัญ + อ่านทาน) ไม่สร้าง shared manifest
4. Demo credentials คงที่ + publish 0.0.0.0 — ยอมรับสำหรับแล็บ disposable บนเครื่องนักศึกษา มี callout กำกับ
