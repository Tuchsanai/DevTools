# PLAN v2 (FROZEN) — CI/CD ด้วย Jenkins บน Docker (ชุด 001_Jenikin)

> **สถานะ: FROZEN 2026-08-19** หลังผ่าน Codex critique (`docs/CRITIQUE_PHASE1.md`) และคำตัดสินครบทุกข้อ (`docs/LEDGER.md`)
> ผู้เรียน: นักศึกษาวิชา DevTools ที่ผ่าน Docker (สัปดาห์ 8–12) และ Git มาแล้ว · แบ่งสอน 2 ครั้ง: LAB 1–3 และ LAB 4–6

## 1. เป้าหมาย

สื่อการสอนภาษาไทย **CI/CD ด้วย Jenkins บน Docker** = slide HTML ไฟล์เดียว (ไม่มี CDN, ฝังวิดีโอ Remotion autoplay) + **6 LAB**
รันได้จริงใน `tuchsanai/devtools:2569_1` (DinD) เล่าเรื่องต่อเนื่องเรื่องเดียว:

**"จากกด Build เองทีละครั้ง → git push แล้วระบบ test-build-deploy ให้เองทั้งวง"**

นักศึกษาใช้ devtools container ตัวเดียวตลอด ทุก LAB ต่อสถานะกันเป็นชั้น (wizard จ่ายครั้งเดียวใน LAB 1)
คนตามไม่ทัน/เครื่องพัง → กู้ด้วย `tools/bootstrap/up_to_labN.sh`

## 2. โครงสร้างไฟล์ (deliverables)

```
001_Jenikin/
├── Jenkins_CICD_Docker_Slides.html      # deck ไฟล์เดียว self-contained
├── readme.md                            # ดัชนีชุด + system req + คำสั่งเริ่ม + กู้สถานะ + timebox
├── slides_assets/                       # screenshot .png + diagram .svg (source of truth = SVG แก้ตรง)
├── slides_assets/motion/*.mp4 + motion-manifest.json
├── tools/embed_assets.py                # ฝังภาพ+วิดีโอเป็น data URI ลง deck
├── tools/motion/                        # โปรเจกต์ Remotion (src, fonts/, package-lock.json, render.sh, validate.py)
├── tools/bootstrap/                     # up_to_lab1..5.sh + wizard.py (Playwright) — ใช้โดย agent/นักศึกษา/integration
├── tools/ui/                            # Playwright scripts ต่อ flow UI (assertion + exit code)
│                                        #   common.py + lab1_wizard.py + lab4_gitea_install.py = U0 · labN_*.py อื่น ๆ = unit N
├── docs/PLAN.md · CRITIQUE_PHASE1.md · LEDGER.md · STACK_RESOLVED.md (เจ้าของ=U0) · INTEGRATION.md
├── logs/<unit_id>.log
├── 001_LAB_Jenkins_On_Docker/README.md + check.sh
├── 002_LAB_Declarative_Pipeline/README.md + check.sh + Jenkinsfile
├── 003_LAB_Docker_Build_Push/README.md + check.sh + Dockerfile.jenkins + app/ + Jenkinsfile
├── 004_LAB_Pipeline_From_Git/README.md + check.sh + Jenkinsfile (+ src ตัวอย่าง)
├── 005_LAB_Webhook_Trigger/README.md + check.sh
└── 006_LAB_CICD_Capstone/README.md + check.sh (acceptance เต็ม) + app/ + Jenkinsfile + Dockerfile
```

## 3. Locked stack

| ชิ้น | เวอร์ชัน | หมายเหตุ |
|---|---|---|
| ฐานทดลอง | `tuchsanai/devtools:2569_1` | DinD `--privileged`, SSH root/passwd |
| Jenkins | `jenkins/jenkins:lts-jdk21` (= 2.568.2 ณ 2026-08-19) | U0 บันทึก digest+เวอร์ชันจริงลง STACK_RESOLVED |
| Jenkins+Docker CLI | `jenkins-docker:2569` (build ใน LAB 3) | FROM lts-jdk21 → root → ติด docker CLI → รัน `-u root` |
| Git server | `gitea/gitea:1.27.2` | SQLite · `GITEA__webhook__ALLOWED_HOST_LIST=private` · `GITEA__server__DISABLE_SSH=true` |
| Registry ปลายทาง push | **Docker Hub จริง** (คำสั่งผู้ใช้ 2026-08-20) | นักศึกษาต้องมี account + **Access Token (Read/Write)** ก่อนเรียน · เอกสารใช้ `<DOCKER_USER>`/`<DOCKER_TOKEN>` เท่านั้น · repos: `<DOCKER_USER>/ci-demo` (LAB 3), `<DOCKER_USER>/cicd-webapp` (LAB 6) — สร้างเป็น **public** บนเว็บ Hub ก่อน push |
| App base | `python:3.12-slim` | FastAPI + uvicorn + pytest |
| Plugin เพิ่ม | Generic Webhook Trigger **2.4.2** (LAB 5) | นอกนั้น = suggested plugins (LAB 1 wizard) |
| Motion | Remotion 4.x pin exact + `package-lock.json` + `npm ci` (Node v24.18.1) | **render H.264 ตรงจาก Remotion** (`--codec=h264 --crf=28 --x264-preset=slow --muted`) — ห้ามใช้ ffmpeg เครื่องนี้ (ไม่มี H.264 — E7) · ฟอนต์ไทย OFL bundle ใน `tools/motion/fonts/` |

## 4. สถาปัตยกรรม runtime (ใน devtools)

- network: `cicd-net` · containers: `jenkins`(8080), `gitea`(3000), `webapp`(8000) — ทุกตัวรัน `--restart unless-stopped` (ไม่มี registry local — push ขึ้น Docker Hub จริง)
- volumes (inner): `jenkins_home`, `gitea_data`
- **คำสั่ง canonical เริ่มระบบ (LAB 1 / readme):**

```bash
docker run -dit --name devtools-jenkins --privileged \
  --tmpfs /run -v jenkins-dind:/var/lib/docker \
  -p 2222:22 -p 8080:8080 -p 3000:3000 -p 8000:8000 \
  tuchsanai/devtools:2569_1
```

- `--tmpfs /run` = restart แล้ว dockerd ขึ้นเอง (กัน pid ค้าง — E5) · named volume = recreate ได้โดยไม่เสีย image/volume ภายใน
- ไม่เผยแพร่ 50000 (ไม่มี inbound agent — slide อธิบาย 1 บรรทัด)
- readme มีหัวข้อ **"กู้สถานะหลัง restart/ปิดเครื่อง"**: `docker start devtools-jenkins` → รอ ~20 วิ → `docker exec devtools-jenkins docker ps` ต้องเห็น services กลับมาเอง

### URL map v2 (canonical — ทุก unit ต้องตรงนี้)

| ผู้เรียก | ปลายทาง | URL |
|---|---|---|
| เบราว์เซอร์นักศึกษา | Jenkins / Gitea / webapp | `http://localhost:8080` / `:3000` / `:8000` |
| shell ใน devtools (git) | Gitea | `http://localhost:3000/student/<repo>.git` |
| Jenkins (checkout) | Gitea | `http://gitea:3000/student/<repo>.git` |
| Gitea (webhook) | Jenkins | `http://jenkins:8080/generic-webhook-trigger/invoke?token=<token ต่อ job>` |
| **inner dockerd** (`docker push/pull`) | Docker Hub | `docker.io/<DOCKER_USER>/<repo>:<tag>` — ต้อง `docker login -u <DOCKER_USER>` ด้วย Access Token (`--password-stdin`) ก่อน |
| เบราว์เซอร์ (พิสูจน์ push) | Docker Hub | `https://hub.docker.com/r/<DOCKER_USER>/<repo>/tags` (repo public — เห็น tag ใหม่โดยไม่ login) |
| **Jenkins pipeline (verify stage)** | webapp | `http://webapp:8000` (DNS บน cicd-net — ห้าม localhost — E6) |

### Fixtures (demo — ไม่ใช่ secret จริง; ledger S-01)

- Jenkins `admin / admin2569` · Gitea `student / student2569` (email `student@example.com`)
- Webhook tokens แยกต่อ job: `cicd2569-hello` (hello-ci-pipeline) · `cicd2569-webapp` (webapp-deploy)
- **Docker Hub**: Jenkins credential id `dockerhub` (Username with password = `<DOCKER_USER>` / `<DOCKER_TOKEN>` Access Token Read&Write) — สอนผ่าน Manage Jenkins → Credentials · Jenkinsfile ใช้ `withCredentials` + `docker login --password-stdin` (token ถูก mask ใน console เป็น `****` — จุดสอน)
- ในเอกสาร/สไลด์: Hub ใช้ **placeholder เท่านั้น** · ของจริง (token/email) ห้ามปรากฏในไฟล์และ log ทุกชนิด — agent รับค่าจริงผ่าน env ตอน runtime เท่านั้น · screenshot หน้า Hub public ที่เห็นชื่อบัญชีทดสอบ = ยอมรับได้ (หน้า public + ผู้ใช้สั่งให้พิสูจน์ push จริง)
- **Safety callout บังคับ** (LAB 1/3/5 + slide): privileged / socket≈root / allow-list — ท่าแล็บ disposable เท่านั้น + production ใช้อะไรแทน 1 บรรทัด · LAB 3 เพิ่ม: Access Token ให้สิทธิ์แคบ (Read/Write ไม่ใช่ Delete/Admin) และ revoke ได้ทันทีหลังคาบ

### Push-block canonical (ledger DH-01..DH-08 — ทุก Jenkinsfile/job ที่ push ต้องใช้ท่านี้)

```groovy
stage('Build & Push') {
  steps {
    withCredentials([usernamePassword(credentialsId: 'dockerhub',
        usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
      sh '''set +x
        export DOCKER_CONFIG=$(mktemp -d)
        trap 'docker logout >/dev/null 2>&1; rm -rf "$DOCKER_CONFIG"' EXIT
        echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
        docker build -t docker.io/$DOCKER_USER/<repo>:$BUILD_NUMBER .
        docker push docker.io/$DOCKER_USER/<repo>:$BUILD_NUMBER
      '''
    }
  }
}
```

- กติกา: groovy string แบบ single-quote เท่านั้น (กัน interpolation รั่ว) · `set +x` · login **ก่อน** build (ให้ pull base image attributed กับ account — กัน 429 anonymous) · `DOCKER_CONFIG` ชั่วคราว + trap ลบเสมอ (ไม่เหลือ credential ใน filesystem แม้ stage fail) · เอกสารเขียนว่า masking "ลดการหลุดใน console" ไม่ใช่การันตีสัมบูรณ์
- **การพิสูจน์ push ผูกกับ run ปัจจุบัน** (กัน false-positive จาก tag เก่า/unit อื่น): check.sh ดึง build number ล่าสุด + digest จาก console/Jenkins API แล้วเทียบกับ Hub API `/v2/namespaces/<ns>/repositories/<repo>/tags/<tag>` (anonymous): digest ตรง + `last_updated` ใหม่กว่าเวลาเริ่ม run · การ inspect ทุกครั้งใช้ `DOCKER_CONFIG=$(mktemp -d)` (บังคับ anonymous) · LAB 6: tag `BUILD_NUMBER` กับ `latest` ต้องชี้ digest เดียวกัน
- check.sh ฝั่งนักศึกษาเรียกแบบ non-secret: `DOCKER_USER=<id> bash check.sh` (token ไม่ใช่ input ของการตรวจ)
- **Prerequisite ก่อนคาบ LAB 3** (readme + กล่องหัว LAB 3): สมัคร Docker Hub + verify email + สร้าง Access Token (Read/Write) + สร้าง repo `ci-demo`, `cicd-webapp` (public) — มีขั้น preflight 2 คำสั่งตรวจว่าพร้อม · ไม่มี fallback token กลางของผู้สอน
- Troubleshooting LAB 3 ต้องแยกอาการ: `401 unauthorized` (token ผิด/หมดอายุ) · `denied: requested access` (namespace/repo ผิด หรือ token ไม่มี Write) · `429` pull-limit vs abuse-limit · หน้า tags ว่าง/404 (repo private หรือ URL ผิด)

### SCM/job contract (ledger I-04..I-06)

- Gitea installer: DOMAIN=`localhost` · ROOT_URL=`http://localhost:3000/` · SSH ปิด
- repos: `student/hello-ci`, `student/webapp` — **public** (checkout ไม่ใช้ credential) · branch `main` (LAB 4 สั่ง `git config --global init.defaultBranch main`)
- Jenkins jobs: `first-freestyle` (LAB 1) · `first-pipeline` (LAB 2) · `docker-build-push` (LAB 3) · `hello-ci-pipeline` (LAB 4–5) · `webapp-deploy` (LAB 6)
- Trigger ตั้งผ่าน **job UI เท่านั้น** (ไม่ใช้ `triggers{}` ใน Jenkinsfile): LAB 4 = Poll SCM **`* * * * *`** (ทุกนาทีจริง — ห้ามใช้ `H/1` เพราะ Jenkins hash เป็นนาทีตายตัวของชั่วโมง หลักฐาน logs/U4.log; warning "Do you really mean every minute?" ของ Jenkins ใช้เป็นจุดสอน) → LAB 5 = ปิด polling + เปิด Generic Webhook Trigger (apply ตอน save — ไม่มี seed-build quirk)

## 5. LAB architecture (6 ตอน + timebox)

| # | โฟลเดอร์ | เวลา | คำถามหลัก | สอนอะไร |
|---|---|---|---|---|
| 1 | `001_LAB_Jenkins_On_Docker` | 40' | ยก Jenkins ใน Docker อย่างไร | canonical run + volume, unlock wizard, suggested plugins, Freestyle job แรก, restart แล้วอะไรอยู่/หาย |
| 2 | `002_LAB_Declarative_Pipeline` | 30' | เปลี่ยนคลิกเป็นโค้ดอย่างไร | Pipeline job, stages/steps/post/environment/parameters, **Pipeline Graph** (plugin `pipeline-graph-view` จาก suggested set — Stage View เก่าไม่อยู่ใน 2.568.2 แล้ว) |
| 3 | `003_LAB_Docker_Build_Push` | 45' | ให้ Jenkins build แล้ว push ขึ้น Docker Hub จริงอย่างไร | DooD vs DinD, `jenkins-docker:2569`, สลับ image โดย volume เดิม (state อยู่ใน volume), สร้าง repo `ci-demo` (public) + Access Token บนเว็บ Hub, เพิ่ม Credentials `dockerhub` ใน Jenkins, pipeline: build → smoke test → `docker login` (masked) → push `docker.io/<DOCKER_USER>/ci-demo:BUILD_NUMBER` → **เปิดเว็บ Hub เห็น tag จริง** |
| 4 | `004_LAB_Pipeline_From_Git` | 40' | Jenkinsfile ไปอยู่ใน repo อย่างไร | Gitea ขึ้นระบบ+installer, repo `hello-ci` (public), push จาก shell, Pipeline from SCM, Poll SCM — เห็นข้อเสีย polling |
| 5 | `005_LAB_Webhook_Trigger` | 30' | push แล้ว build ทันทีอย่างไร | ติดตั้ง plugin GWT 2.4.2, token ต่อ job, Gitea webhook + delivery log, ปิด polling |
| 6 | `006_LAB_CICD_Capstone` | 45' | วงเต็มหน้าตาเป็นอย่างไร | repo `webapp` (FastAPI dashboard โชว์ VERSION+BUILD_NUMBER+สี theme): push → webhook → pytest → build → push `docker.io/<DOCKER_USER>/cicd-webapp:BUILD_NUMBER` (+`latest`) → deploy → verify ผ่าน `http://webapp:8000` · แก้สี/เวอร์ชัน push ซ้ำ → หน้าเว็บเปลี่ยนเอง + tag ใหม่โผล่บน Hub · `check.sh` acceptance เต็มวง |

- เอกสารตาม `docs/LAB_TEMPLATE.md` เคร่งครัด (1 การทดลอง = 1 คำถาม = 1–2 คำสั่ง = 1 สิ่งที่ต้องสังเกต · ห้ามหัวข้อ "ทำให้พัง")
- ทุกแล็บ: กล่อง "สภาพตั้งต้น" + `bash check.sh` ท้ายแล็บ + แถวกู้สถานะใน troubleshooting
- Capstone ใช้เฉพาะเทคนิคที่สอนใน LAB 1–5

## 6. Unit list + interface map

| unit | scope (แตะได้เท่านั้น) | produce | consume |
|---|---|---|---|
| **U0** | `tools/bootstrap/` + `tools/ui/common.py`,`tools/ui/lab1_wizard.py`,`tools/ui/lab4_gitea_install.py` + `docs/STACK_RESOLVED.md` + `logs/U0.log` | `up_to_lab1..5.sh` (**CLI-only รันในตัว devtools ได้ — นักศึกษาใช้กู้สถานะ**: skip-wizard + groovy init admin + jenkins-plugin-cli ตาม plugins.txt ที่ freeze + Gitea API + job จาก config.xml · idempotent · พารามิเตอร์ env `DT_NAME`) · `wizard.py`/UI scripts พื้นฐานฝั่ง host (Playwright: พิสูจน์เส้นทาง wizard ของนักศึกษา + dump plugin list → freeze `plugins.txt`) · STACK_RESOLVED (digest/เวอร์ชัน/plugin list/เวลาโหลดจริง) | PLAN นี้ |
| U1 | `001_LAB_.../` + `logs/U1.log` + `slides_assets/lab1_*.png` | README+check.sh · shots: `lab1_unlock, lab1_plugins, lab1_dashboard, lab1_first_build` | U0 (ui scripts) |
| U2 | `002_LAB_.../` + `logs/U2.log` + `slides_assets/lab2_*.png` | README+check.sh+Jenkinsfile · shots: `lab2_pipeline_graph, lab2_params` | U0 (`up_to_lab1.sh`) |
| U3 | `003_LAB_.../` + `logs/U3.log` + `slides_assets/lab3_*.png` | README+check.sh+`Dockerfile.jenkins`+app เล็ก+Jenkinsfile · shots: `lab3_pipeline_docker, lab3_push_log (console: login masked + push layers), lab3_hub_tags (หน้า Hub tags — หลักฐาน push จริง)` | U0 (`up_to_lab2.sh`) + env creds |
| U4 | `004_LAB_.../` + `logs/U4.log` + `slides_assets/lab4_*.png` | README+check.sh+Jenkinsfile · shots: `lab4_gitea_repo, lab4_jenkins_scm, lab4_poll_build` | U0 (`up_to_lab3.sh`) |
| U5 | `005_LAB_.../` + `logs/U5.log` + `slides_assets/lab5_*.png` | README+check.sh · shots: `lab5_webhook_config, lab5_delivery, lab5_auto_build` | U0 (`up_to_lab4.sh`) |
| U6 | `006_LAB_.../` + `logs/U6.log` + `slides_assets/lab6_*.png` | README+check.sh(acceptance)+app/+Jenkinsfile+Dockerfile · shots: `lab6_app_v1, lab6_app_v2, lab6_pipeline_full, lab6_hub_tags (Hub tags โชว์ BUILD ใหม่)` | U0 (`up_to_lab5.sh`) + env creds |
| UM | `tools/motion/` + `slides_assets/motion/` + `logs/UM.log` | 5 คลิป mp4 + `motion-manifest.json` + `validate.py` ผ่าน | PLAN นี้ (ไม่ใช้ container) |
| U7 | deck HTML + `tools/embed_assets.py` + `slides_assets/*.svg` + `logs/U7.log` | deck สมบูรณ์ (ตอน 0–6+สรุป, เลขหน้า, overview, SVG≥8, shots≥8, วิดีโอ 5 ฝัง data URI) | shots + motion manifest + STACK_RESOLVED + README ทุกแล็บ (อ่านอย่างเดียว) |
| U8 | `readme.md` + `docs/INTEGRATION.md` + `logs/U8.log` | integration เต็มวง + restart checkpoints + ดัชนีชุด | ทุกอย่าง |

### แผนผังตอนของ slide (locked — ตรงกับที่ README แล็บอ้างอิงแล้ว)

| ตอน | ชื่อ | ครอบคลุม | LAB |
|---|---|---|---|
| 0 | Overview + แผนที่คอร์ส | เป้าหมาย, สิ่งที่จะสร้าง, prerequisite, ตาราง LAB+timebox | — |
| 1 | จากงานมือสู่ CI/CD | pain ของ deploy มือ, CI vs CD, แนวคิด pipeline | — |
| 2 | รู้จัก Jenkins | controller/job/build/workspace, plugins, jenkins_home | — |
| 3 | Jenkins บน Docker | canonical run, volume=state, restart resilience (--tmpfs /run), 8080/50000, wizard | LAB 1 |
| 4 | Declarative Pipeline | Jenkinsfile anatomy, stages/post/env/params/when, Pipeline Graph | LAB 2 |
| 5 | เชื่อมโลกภายนอก | 5.1 DooD+custom image+Credentials+push Hub จริง · 5.2 Gitea+Pipeline from SCM+polling · 5.3 Webhook+GWT token | LAB 3, 4, 5 |
| 6 | CI/CD เต็มวง | topology รวม, test-ก่อน-push, deploy+verify, capstone เดินเรื่อง v1→v2 | LAB 6 |
| สรุป | — | ตาราง LAB, safety recap (lab vs production), ไปต่อทางไหน | — |

### คลิป motion (UM)

`mo_intro` (วง CI/CD หมุน — ปก) · `mo_manual_vs_ci` · `mo_pipeline_flow` (commit→webhook→test→build→push→deploy ไฟเขียวไล่ stage) · `mo_polling_vs_webhook` · `mo_dood_socket`
สเปก: 6–14 วิ · 1280×720 · 30fps · ไม่มีเสียง · loop เนียน · ≤1.5MB เป้าหมาย (cap 2.5MB) · ข้อความไทยฟอนต์ bundle · `--concurrency=8`

### ลำดับรัน (ledger D-02)

**W0**: U0 + UM ขนาน → **WA1**: U1,U2,U3 → **WA2**: U4,U5,U6 → **WB**: U7 → **Phase 3**: U8
(สูงสุด 3 devtools container พร้อมกัน · UM ไม่ใช้ container)

## 7. กติกาการทดสอบของ agent

- ชื่อ container: `devtools-jk<N>` · SSH `2230+N` · **web ports ต้อง publish แบบ shift**: Jenkins `1<N>080`, Gitea `1<N>300`, webapp `1<N>800` (เช่น U3 → 13080/13300/13800; เลี่ยง 2242–2260)
- **เข้า UI ผ่าน `http://host.docker.internal:<shifted>` เท่านั้น** (bridge IP ใช้ไม่ได้ — E1) · preflight `curl -fsS <BASE_URL>/login` ก่อนเริ่ม Playwright
- ค่าใน form/เอกสารเป็น canonical (`localhost`) เสมอ แม้ agent เข้าผ่าน host.docker.internal (โดยเฉพาะ Gitea installer — I-06)
- รอ inner dockerd: retry `docker exec devtools-jkN docker info`
- ขั้น UI ทุกขั้นต้องรันผ่าน script ใน `tools/ui/` (assertion + exit code) แล้ว capture — ห้าม mock ภาพ
- **Docker Hub creds**: orchestrator ส่งผ่าน env `DOCKER_USER`/`DOCKER_TOKEN` ให้ **U0, U3, U4, U5, U6, U8** (ทุก unit ที่เรียก `up_to_lab3.sh` ขึ้นไป — fail-fast ถ้าไม่ตั้ง) — ห้าม hardcode/commit/echo ลงไฟล์หรือ log · เอกสารใช้ placeholder · repo provision: `up_to_lab3.sh` ensure-repo ผ่าน Hub API (`/v2/auth/token` → POST repositories `is_private:false`, idempotent) ส่วนนักศึกษาสร้างผ่านเว็บ (ทั้งสองทาง converge)
- cleanup ต่อ unit: `docker rm -f devtools-jkN` + แสดง `docker ps -a --filter name=^devtools-jk<N>$` ว่างใน log (ตรวจเฉพาะของตน — DD-04) · global check เป็นของ orchestrator ท้าย wave
- ห้ามแตะ container คนอื่น (`kafka-teach`, `deep_vision_5090_vllm`, `devtools-jk*` ของ unit อื่น)

## 8. DoD

### U0
1. `up_to_labN.sh` (N=1..5) รันจากศูนย์บน devtools เปล่าแล้วผ่าน assertion ภายในของ bootstrap ครบ (chain ต่อเนื่อง 1 รอบ + log exit code) — การไขว้ตรวจกับ `check.sh` ของแล็บเป็นหน้าที่ U8 (แก้ dependency cycle ตาม critique U0)
2. script ทุกตัว idempotent (รันซ้ำบนสถานะที่ถึงแล้ว → exit 0 ไม่พัง)
3. STACK_RESOLVED.md: digest ทุก image, Jenkins ver, plugin list+เวอร์ชัน, เวลาโหลดจริง
4. ใช้ค่า canonical ทั้งหมด (creds/ชื่อ/พอร์ต ตาม §4)
5. `up_to_lab3.sh` ขึ้นไป: รับ `DOCKER_USER`/`DOCKER_TOKEN` จาก env (fail-fast พร้อมข้อความชัดถ้าไม่ตั้ง) · seed Jenkins credential id `dockerhub` · push จริงขึ้น Hub สำเร็จใน chain proof · ค่า token ไม่ปรากฏในไฟล์/log

### ต่อ LAB (U1–U6)
1. README ตาม template · `> 📝` ≤250 ตัวอักษร · safety callout ตามที่ ledger S-03 กำหนด (แล็บ 1/3/5)
2. รันจริงครบทุกการทดลอง — log มีคำสั่ง+exit code · ขั้น UI มี script `tools/ui/` + exit code
3. `check.sh` ตรวจสถานะจบแล็บ (exit 0/1) — ของ U6 คือ acceptance เต็มวง (webhook 2xx → build cause=webhook → pytest pass → **tag ใหม่บน Docker Hub**: `docker manifest inspect docker.io/$DOCKER_USER/cicd-webapp:<tag>` exit 0 → เว็บโชว์ VERSION ใหม่ → push รอบสอง idempotent)
3.1 U3/U6 เพิ่ม: **หลักฐาน push จริง** — screenshot หน้า `hub.docker.com/r/<user>/<repo>/tags` ที่เห็น tag ที่เพิ่ง push (`lab3_hub_tags`, `lab6_hub_tags`) + console log ช่วง push ใน log unit
4. Screenshot ครบตามชื่อใน interface map (ของจริง)
5. ไฟล์ประกอบตรงกับ README ทุกบรรทัด · ไม่มีของจริง (email/token) · fixtures ตาม §4
6. cleanup ของตนพิสูจน์ใน log

### UM
1. คลิปครบ 5 + manifest ครบ field (composition, duration, fps, dim, codec=h264, no-audio, bytes, sha256)
2. `cd tools/motion && npm ci && ./render.sh` ทำซ้ำได้จากศูนย์ · `validate.py` ผ่าน: metadata + Playwright (autoplay muted, currentTime เดิน, เฟรม t=0≈t=end ด้วย PIL diff)
3. ไม่มี asset/ฟอนต์จากเน็ตตอน render

### U7 (deck)
1. Playwright offline test: abort ทุก http(s) → ไล่ครบทุกหน้า → 0 external request, 0 console error
2. โครง: ปก → overview/สารบัญคลิกได้ → ตอน 0–6 → สรุป+ตาราง LAB · เลขหน้า n/N + progress bar + คีย์ ←/→
3. SVG inline ≥8 (โทนสว่าง, แก้ตรงใน HTML/ไฟล์ svg — ไม่มี .excalidraw ตาม ledger S-02) + shots ≥8 (crop ไม่ย่อเบลอ)
4. วิดีโอ 5 ตัวฝัง data URI จาก manifest · `<video autoplay muted loop playsinline>` · JS play เมื่อเข้าหน้า/pause เมื่อออก (Playwright assert currentTime)
5. ขนาดรวม < 30MB · เปิดลื่นใน chromium
6. ทุกตอนจบลิงก์ "→ LAB N" ชื่อตรงโฟลเดอร์จริง · คำสั่ง/พอร์ต/ชื่อ ตรง URL map + STACK_RESOLVED
7. safety callout 1 หน้า (production vs ท่าแล็บ)

### U8 (integration)
1. devtools ใหม่ 1 ตัว ไล่ LAB 1→6 ตาม README ทีละการทดลอง (UI ผ่าน tools/ui) — ทุก "✅ สิ่งที่ต้องเห็น" ตรง · ไม่ตรง = ตีกลับ unit พร้อม log
2. **restart checkpoint ×2**: หลังจบ LAB 3 และ LAB 5 → `docker restart` → services กลับเอง + job history/repo ครบ ไม่ทำ wizard ซ้ำ (ตรวจด้วย `docker ps -a` + check.sh ของแล็บล่าสุด)
3. capstone end-to-end: แก้โค้ด → push → auto build → เว็บเวอร์ชันใหม่ (shots ก่อน/หลัง) + tag ใหม่บน Docker Hub (capture หน้า tags) + `006.../check.sh` exit 0
4. cross-check: ชื่อ/พอร์ต/creds ทุกแล็บ + slide ↔ โฟลเดอร์/URL map (สคริปต์เทียบ + อ่านทาน)
5. จบ: `docker ps -a --filter name=^devtools-` ว่าง (global) · ไม่มีไฟล์ขยะ (.ipynb_checkpoints, ไฟล์ tmp)

## 9. ความเสี่ยงคงเหลือ (หลัง critique)

| id | เรื่อง | การจัดการ |
|---|---|---|
| R1 | update center ช้า/ล่มระหว่างเรียน | ตาราง troubleshooting + retry · accepted risk (ledger A-03) |
| R2 | เวลาแล็บจริงของผู้เรียนต่างจาก timebox | ปรับหลังสอนรอบแรก + bootstrap catch-up (ledger F-04) |
| R3 | deck+วิดีโอเปิดช้าบนเครื่องอ่อน | วิดีโอ decode เฉพาะหน้า active (play/pause JS) · วัดจริงใน U7 |
| R4 | slide↔README consistency ด้วยมือ | Phase 3 สคริปต์เทียบจุดสำคัญ + Phase 4 adversarial review |
| R5 | พึ่ง Docker Hub จริง: เน็ต/rate limit/นักศึกษาไม่มี account หรือลืม token | readme+LAB 3 มีกล่อง prerequisite (สมัคร+สร้าง token ก่อนเรียน) · troubleshooting มีแถว push ล้ม (401/timeout) · tag ขยะสะสมบน repo ทดสอบ = ยอมรับ (ลบทีหลังได้) |

## 10. Scope guard

- ✅ Remotion motion graphics ใน deck (คำสั่งผู้ใช้ 2026-08-19) — 5 คลิปตามสเปก ไม่ทำวิดีโอยาว/มีเสียง/standalone
- ❌ Jenkins distributed agents / Kubernetes / Blue Ocean / Multibranch / shared library / credentials binding ขั้นสูง — slide "ไปต่อทางไหน" 1 หน้า
- ❌ GitHub จริง + token จริง — Gitea local แทน (slide เทียบ 1 หน้า; ชุดเก่า 02_Jenkins ครอบคลุม GitHub แล้ว)
