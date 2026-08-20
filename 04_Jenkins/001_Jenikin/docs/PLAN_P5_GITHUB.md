# PLAN Phase 5 (v2) — ย้าย SCM จาก Gitea → GitHub (ทั้งชุด) + Simplification pass

สถานะ: **FROZEN (canonical)** หลังตัดสิน critique 33 ข้อ (ดู LEDGER §P5) · สถาปนิก: Claude · ผู้สร้าง: Codex · 2026-08-20
ไฟล์นี้ supersede ส่วน SCM/webhook contract ของ `docs/PLAN.md` (I-04..I-06) — gates และ builder อ่านไฟล์นี้เป็นหลัก [P5-m02]

## เป้าหมาย (จาก USR)

- G1: LAB ทุกตัวใช้ **GitHub.com เท่านั้น** เป็น SCM — active tree ต้องไม่มี Gitea เหลือ (พิสูจน์ด้วย rg-zero gate)
- G2: ทุกขั้น UI มีลำดับคลิก + screenshot + marker + caption ไม่ขาดช่วง (มี screenshot matrix ต่อการทดลอง)
- G3: ตัดคำสั่งซับซ้อนที่ไม่ใช่หัวใจแล็บ · G4: expected output จริง (normalize ตาม R7) + code ตัวเต็ม
- G5: จบงาน gates exit 0 + cleanup ตามนิยาม D14

## หลักฐาน (spike 2026-08-20)

- E1: GitHub push → webhook → smee.io → `deltaprojects/smee-client` (bridge net) → HTTP 200; payload มี `ref`,`after`,`head_commit.message`,`commits[].added`
- E2: `HEAD https://smee.io/new` → `Location: https://smee.io/<channel>`
- E3: token gh (repo+delete_repo) สร้าง/ลบ repo ได้; `hello-ci`,`webapp` ว่างบนบัญชีทดสอบ
- E4: image lock `deltaprojects/smee-client@sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33` (amd64-only — accepted risk, สภาพแวดล้อมชุดสอนเป็น amd64) [P5-M01→PARTIAL]
- E5: ไม่มีทาง capture หน้า GitHub ที่ต้อง login (มีแค่ PAT/OAuth token)

## การตัดสินใจสถาปัตยกรรม (v2)

| # | การตัดสินใจ | อ้าง critique |
|---|---|---|
| D1 | LAB 4: repo public `<GITHUB_USER>/hello-ci`; Jenkins checkout `https://github.com/<GITHUB_USER>/hello-ci.git` ไม่มี credentialsId; Poll SCM `* * * * *`; build ต้อง checkout SHA ตรงกับ push | B02 |
| D2 | LAB 5: GWT ต้องตั้ง **Post content parameter** `ref=$.ref`, `after=$.after` + **Optional filter** text=`$ref` expression=`^refs/heads/main$` + causeString `GitHub push $after` — เพื่อกัน `ping` และ branch อื่น; acceptance: สร้าง hook แล้ว build count ต้องไม่เพิ่ม, push แล้วเกิด exactly one build | **B01** |
| D3 | สอง relay แยกขาด: env `SMEE_HELLO_URL`/`SMEE_WEBAPP_URL` · mapping 1:1 repo↔hook↔channel↔container(`smee-hello`/`smee-webapp`)↔token · URL persist ใน docker args (recover ด้วย `docker inspect`) · rerun ต้อง converge ไม่ mint ใหม่ | **B05** |
| D4 | หลักฐาน payload = หน้า smee channel (เปิด tab **ก่อน** Add webhook) + `docker logs smee-*` + Jenkins build; ลำดับบังคับ: เปิด tab → รัน relay → รอ `Connected` → Add webhook → push; เอกสารระบุชัด: smee ไม่ replay event ที่พลาด — recovery คือ push commit ใหม่ | **B06** |
| D5v2 (USR 2026-08-20) | ภาพ GitHub UI ใช้**ของจริงทั้งหมด**: ผู้ใช้ให้ session cookie → capture หน้า auth จริง (New repo, Add webhook, Recent Deliveries) แบบ mask username/URL ตอน capture; cookie ใช้ local เท่านั้น ห้ามเขียนลงไฟล์/log/repo; mock ที่ทำไว้เป็น fallback ชั่วคราวจนกว่า capture จริงครบ | (แทน D5 เดิม) |
| D5-เดิม | ภาพหน้า GitHub auth-only: **HTML/CSS mock render ผ่าน Playwright** (ตัวหนังสือคมและตรงค่า contract) เป็นวิธีหลัก, codex-gen เป็น fallback; ทุกภาพติด caption "ภาพจำลอง — UI จริงอาจต่างเล็กน้อย" + ลิงก์ GitHub Docs + มี API postcondition; ห้ามใช้เป็นหลักฐาน runtime | **B08, M12** |
| D6 | masking ทำ **ตอน capture** (ไฟล์ที่ commit ต้อง mask แล้ว): `<GITHUB_USER>` และ `<SMEE_URL>`/channel id; annotate_steps เพิ่ม op `mask` (schema: `type:"mask"`, `box`, `text`, `fill`; วาดก่อน marker; idempotent) + unit test; git identity ในแล็บใช้ระดับ repo `Student <student@example.invalid>` | M04, M14 |
| D7 | Prereq ก่อนคาบ: บัญชี GitHub + PAT classic scope **`public_repo` + `admin:repo_hook`** (แคบกว่า `repo`); preflight script ตรวจ `GET /user` + `X-OAuth-Scopes` header — ไม่สร้าง probe repo | M06 |
| D8 | check.sh: ทุกการเรียก `api.github.com` ต้อง **authenticated** (`GITHUB_USER`/`GITHUB_TOKEN` จำเป็นทั้ง LAB 4/5/6); ดึง response ครั้งเดียว cache ลง temp; หลักฐาน webhook ต้อง correlate ≥4 hop ด้วย SHA เดียวกัน: GitHub delivery(`event=push`,`payload.after=SHA`) → relay log `POST … 200` หลัง timestamp → Jenkins cause GWT + checkout SHA → build SUCCESS; hook assert ครบ field (`content_type=json`,`events=[push]`,`active`,`insecure_ssl=0`, secret ว่าง+เหตุผลใน README) | **B02, B03**, M02 |
| D9 | bootstrap: ต้องมี `GITHUB_USER`/`GITHUB_TOKEN`; repo ที่สร้างต้องมี **ownership marker** `.course-cicd2569`; ถ้า repo มีอยู่แต่ไม่มี marker → **fail closed** (ไม่ push/hook/แก้ใดๆ) พร้อมคำแนะนำ rename; บันทึก `created_by_this_run`; ห้าม force-push/ลบ repo ที่ไม่ได้สร้างเอง; push ใช้ temp `GIT_ASKPASS` + `GIT_TERMINAL_PROMPT=0` + trap ลบ — ห้าม token ใน URL/`.git/config`/log; job XML ใช้ sentinel `__GITHUB_USER__` render ลง mktemp แล้ว POST, จบด้วย `git diff --exit-code` | **B04**, M03, M05 |
| D10 | ตัด `-p 3000:3000` จาก canonical run; URL ผู้เรียน = Jenkins 8080, Webapp 8000 | — |
| D11 | GitHub API ทุกจุดผ่าน helper เดียว (`gh_api` ใน common.sh; check.sh ฝัง copy สั้นจาก source เดียว): ส่ง `Accept: application/vnd.github+json` + `X-GitHub-Api-Version: 2022-11-28`, ไม่ echo token, อ่าน `Retry-After`, นับ request ต่อ run | M08 |
| D12 | ทดสอบจริงใช้บัญชี Tuchsanai; จบ integration: ลบ hook ที่สร้าง, ลบ relay containers, ลบเฉพาะ repo ที่ `created_by_this_run`, ตรวจ 404; channel smee = inert identifier ภายนอก (ลบไม่ได้ — ไม่มี active client/hook เหลือ = สะอาด) | M11 |
| D13 | แยกงานเป็น **2 wave commit**: Wave A = SCM migration (LAB4–6+bootstrap+ui+slides+gates) · Wave B = simplification (LAB1–3+root readme) — review/rollback แยกส่วน · **USR สั่ง (2026-08-20): จบงานแล้ว push ขึ้น origin main** (หลังผ่าน INT+gates+P4 review; ตรวจ secret scan ก่อน push เสมอ) | M17 |
| D14 | manual flow push: Username=login, Password=PAT ที่ prompt; ห้าม `https://TOKEN@…`, ห้าม `credential.helper store` (ลบคำแนะนำเดิมใน LAB 4 ด้วย) | M05 |
| D15 | fallback "Poll SCM ชั่วคราว" เป็น continuity เท่านั้น อยู่ในตาราง troubleshoot พร้อมขั้น revert; check ไม่ยอมผ่านจนมี webhook chain จริง | M18 |

## กฎเรียบเรียงเอกสาร (R1–R7)

- R1: ห้าม `--format`/`--filter`/pipe ซับซ้อนที่ไม่ใช่หัวใจแล็บ; ข้อยกเว้นได้เมื่อ format คือสาระ (บันทึกเหตุผล) [M17]
- R2: เตรียมชุดสอน: วัดขนาด clone `--depth 1` เต็ม repo ก่อน — ถ้า ≤300MB ใช้ `git clone --depth 1` ธรรมดา, ถ้าเกินคง sparse พร้อมกล่องอธิบายสั้น; `COURSE_ROOT` persist ด้วย `echo 'export …' > /etc/profile.d/course.sh` (idempotent, ไม่มี grep); รองรับกรณี `~/DevTools` มีอยู่แล้ว (`git -C ~/DevTools pull`) [M17]
- R3: ทุก code block รันได้ ตามด้วย ✅ expected output จาก log จริง
- R4: ไฟล์ที่ต้องใช้ให้ตัวเต็มหรือ `cp` จาก `$COURSE_ROOT`
- R5: ไม่มีหัวข้อ "ทำให้พัง"; error อยู่ตาราง troubleshoot
- R6: placeholder เท่านั้น: `<GITHUB_USER>` `<GITHUB_TOKEN>` `<DOCKER_USER>` `<DOCKER_TOKEN>` `<SMEE_HELLO_URL>` `<SMEE_WEBAPP_URL>`
- R8 (USR 2026-08-20): **ห้ามอัดหลายคำสั่งต่อกันด้วย `&&` ในบรรทัดเดียว** — code block ให้เขียนทีละคำสั่งทีละบรรทัด (คำสั่งเดียวที่ยาวใช้ `\` ต่อบรรทัดได้) แบ่งกลุ่มตามขั้นตอนเชิงตรรกะ · ใช้กับทุก LAB
- R7: normalization ของ expected output: มาจาก log จริง แทนเฉพาะ `<GITHUB_USER>`,`<SMEE_*_URL>`,`<SHA>`,`<BUILD_NUMBER>`, เวลา; เลข build ในเนื้อความใช้แบบ baseline-relative (`#N`,`#N+1`) — caption ของภาพจริงคงเลขจริงได้ [m03, m06]

## Contract (interface map v3)

- **I-04v3 (SCM)**: repo public `<GITHUB_USER>/hello-ci`, `<GITHUB_USER>/webapp` branch `main` + marker `.course-cicd2569`; Jenkins URL `https://github.com/<GITHUB_USER>/<repo>.git` ไม่มี credentialsId; job `hello-ci-pipeline`, `webapp-deploy`; trigger ผ่าน job UI เท่านั้น
- **I-05v4 (trigger)**: GWT 2.4.2 token `cicd2569-hello`/`cicd2569-webapp` + post-content param `ref=$.ref`,`after=$.after` + filter `$ref` ~ `^refs/heads/main$` + causeString `GitHub push $after`; GitHub hook: url=`<SMEE_*_URL>`, content_type=json, events=[push], active, insecure_ssl=0, secret ว่าง (เหตุผล: ไม่มี receiver ที่ verify signature ใน topology นี้ — ระบุใน README)
- **I-08 (GitHub prereq)**: PAT classic `public_repo`+`admin:repo_hook`; preflight `tools/bootstrap/github_preflight.sh` (ตรวจ /user + scopes header, ไม่เก็บ/ไม่พิมพ์ token)
- **I-09 (relay)**: `deltaprojects/smee-client@sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33`; container `smee-hello`,`smee-webapp` บน `cicd-net`, `--restart unless-stopped`; STACK_RESOLVED บันทึก node/smee version จริง + architecture + reconnect test result
- **I-10 (masking)**: mask ตอน capture; ครอบ `<GITHUB_USER>` + `<SMEE_URL>`; raw ที่ไม่ mask ห้ามเข้า git; secret scan: `ghp_`,`gho_`,`github_pat_`,`dckr_pat_`,`https://smee.io/<id จริง>` = 0 (allowlist: placeholder)
- **I-11 (gen image)**: HTML mock → Playwright render เป็นหลัก; ทะเบียนภาพ (real/mock/masked) ใน docs/INTEGRATION.md; caption "ภาพจำลอง" บังคับ
- **I-12 (API helper)**: `gh_api` contract ตาม D11
- I-01, I-02, I-03, I-07 คงเดิม · I-06 ยกเลิก

## หน่วยงาน + ลำดับ + DoD

| unit | งาน | ขึ้นกับ | DoD หลัก |
|---|---|---|---|
| U-P5-0 | tooling: mask op ใน annotate_steps.py (+unit test synthetic image: bounds/idempotent/mask+marker) · แทน/ลบ ui scripts ที่ผูก Gitea ตาม **migration manifest** (ทำ manifest ก่อน: rg `gitea|localhost:3000|gitea_data|student/hello-ci|student/webapp` ระดับไฟล์ ระบุ rewrite/delete/archive ทุกไฟล์) · `github_preflight.sh` | — | py_compile ครบ; unit test ผ่าน; manifest ครอบ 100% ของ rg hits ใน active tree |
| U-P5-1 | bootstrap: common.sh (gh_api, ensure_github_repo แบบ fail-closed+marker, GIT_ASKPASS, ensure_smee_channel/relay ด้วย env D3, ensure_github_hook ครบ field, GWT job XML sentinel+render+filter I-05v4) · fixtures `Hello from GitHub` · up_to_lab4/5.sh | U-P5-0 | up_to_lab4/5 exit 0 บน devtools ใหม่ **สองรอบ** (idempotent converge); `git diff --exit-code`; token ไม่โผล่ใน log/config |
| U-P5-2 | check.sh LAB4/5/6 ตาม D8 (+ mutation negative set รันตอน integration: stopped relay, wrong token, ping-only, stale SHA) | U-P5-1 | exit 0 กับสถานะจริง; negative set fail ทุกตัว; ไม่มี gitea; API ทุกจุด authenticated |
| U-P5-3 | mock images (HTML render): ฟอร์ม New repository ×2, Add webhook ×2 + ภาพ PAT ถ้าจำเป็น | — (ขนาน) | ค่าตรง contract ทุก field; caption ภาพจำลอง; ทะเบียนใน INTEGRATION.md |
| U-P5-4 | LAB 4 README + รันจริง + capture (mask ตอน capture) + annotations | U-P5-1,2,3 | student-path จริงทุก block; check exit 0; screenshot matrix ครบ; SHA correlate |
| U-P5-5 | LAB 5 README (smee+GWT filter flow ตาม D2/D4) + รันจริง + capture + **ping acceptance** (hook สร้างแล้ว build ไม่เพิ่ม) + restart/reconnect test | U-P5-4 | B01/B02/B06 acceptance ผ่านครบ; matrix ครบ |
| U-P5-6 | LAB 6 README + รันจริง v1→v2 + Hub จริง + **isolation test** (push webapp ไม่ trigger hello และกลับกัน) | U-P5-5 | check exit 0; isolation+digest correlate; matrix ครบ |
| U-P5-7 | Wave B: LAB1–3 + root readme simplification (R1–R7, R2 วัดขนาด clone ก่อน) | — (ขนาน, commit แยก wave) | คำสั่งที่แก้รันจริงทั้งหมด; golden inventory before/after |
| U-P5-8 | slides: ตอน 5.2/5.3 + หน้าที่แตะ Gitea; SVG d7/d8; screenshot ฝังชุดใหม่; **คง 80 หน้า (invariant)**; deck_offline assert รายชื่อ embedded asset แบบ exact + zero gitea assets | U-P5-4..6 | deck_offline exit 0; ไม่มี asset เก่าฝัง |
| U-P5-9 | gates+docs: deck_consistency/int_consistency contracts v3 + **rg-zero gate** (allowlist: docs/LEDGER*, docs/CRITIQUE*, logs/, backup/) + **mutation self-test** (`--self-test` ใส่ bad fixture ต้อง fail) · STACK_RESOLVED · PLAN.md pointer · LEDGER append · INTEGRATION.md (ทะเบียนภาพ+ทะเบียน asset ลบ) | U-P5-8 | gates 3 ตัว exit 0 + self-test fail-on-bad ผ่าน |
| U-P5-INT | **Track A**: student replay จากจบ LAB 3 → ทำ LAB4–6 ตาม README ทุก block/UI step + จับเวลา (ปรับ timebox) · **Track B**: bootstrap recovery บนเครื่องใหม่ + restart outer devtools หลัง LAB 5 (relay reconnect + push ใหม่ = exactly one build) · secret scan I-10 · cleanup D12 | ทั้งหมด | acceptance matrix ล่างครบทุกแถว; logs ครบ |

## Acceptance matrix (จาก critique — บังคับก่อดปิดงาน)

| Gate | พิสูจน์แบบ executable |
|---|---|
| Preflight | token owner ตรง login; scopes ครบ; token ไม่ถูกเก็บ/echo |
| LAB 4 | repo public + marker; ไม่มี credentialsId; push SHA ใหม่ → build cause SCM + checkout SHA ตรง |
| LAB 5 ping | Add hook → ping 2xx แต่ build count ไม่เพิ่ม |
| LAB 5 push | delivery SHA → relay POST 200 → exactly one GWT build → checkout SHA เดียวกัน; Poll off |
| Relay resilience | restart แล้ว recover URL เดิม + Connected + push ใหม่ผ่าน; docs ระบุ no-replay |
| LAB 6 isolation | channel/token แยก; ไม่ cross-trigger; v1→v2 ผูก SHA/build/digest เดียวกัน |
| Checks/gates | positive+negative; authenticated budget; zero gitea (active tree); exact asset map |
| Cleanup | hooks/relay/temp/repo ที่สร้าง = 0; repo เดิมไม่ถูกแตะ; channel เหลือแบบ inert |

## ความเสี่ยงคงเหลือ (accepted)

- K1: smee.io ไม่มี SLA — troubleshoot: สร้าง channel ใหม่ + update hook + push ใหม่ (canonical) / Poll ชั่วคราวแบบมีขั้น revert [D15]
- K2: image relay เก่า (amd64, Node เก่า) — บันทึก version จริงใน STACK_RESOLVED; ถ้า reconnect test ล้ม → build image เองจาก Node base (fallback ที่วางไว้)
- K3: Poll ทุกนาทีเป็น outbound จริงไป GitHub — accepted risk + preflight `git ls-remote` จากใน Jenkins container + troubleshoot DNS/TLS/proxy/429
- K4: mock image อาจ drift จาก GitHub UI จริง — caption + ลิงก์ docs + reviewer vision ก่อนรับ
