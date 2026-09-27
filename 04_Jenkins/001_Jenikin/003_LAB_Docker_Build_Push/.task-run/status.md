# Task status — LAB003 Jenkins Docker Build Push (worker3)
Updated: 2026-09-27T22:02:25Z

## Endpoints (for parent)
- Agent container (sshd :22, SSH tunnel entry): **172.18.0.2:22** (Docker gateway 172.18.0.1)
- Upload receiver (loopback of agent container only): **127.0.0.1:8791** — `curl -X PUT --data-binary @- http://127.0.0.1:8791/upload/<name>.png` · names `[A-Za-z0-9_-]{1,64}.png` · PNG magic required · max 20 MB · saves to `.task-run/images/` · `GET /list`, `GET /health`
- (REMOVED) Jenkins UI: Docker-host **127.0.0.1:18491** · from agent container: **172.22.0.3:8080** (login admin / admin2569)
- (REMOVED) Shop (catfood-web in devtools DinD): Docker-host **127.0.0.1:13000** · from agent: **172.22.0.2:3000**
- (REMOVED) devtools SSH: Docker-host 127.0.0.1:2223 (key Devtool_SSH/devtoolSSH or root/passwd)
- Tunnel example: `ssh -N -L 18491:172.22.0.3:8080 -L 13000:172.22.0.2:3000 -L 8791:127.0.0.1:8791 root@172.18.0.2`

## SCM
- GitHub Tuchsanai/DevTools main = a8d0c0b2f1522eff08b63f3bb4538b161f5e71b9 (ls-remote before build 1; Clone stage printed `a8d0c0b 1`)
- Local HEAD = a8d0c0b; `git diff origin/main -- Jenkinsfile` empty → local Jenkinsfile == SCM at start

## Milestones
- [x] M0 status file
- [x] M1 local files + prior worker findings (prior worker: devtools:2569_1 lacks key support; stopped before any lab resources)
- [x] M2 old lab devtools-l3nav-277caf-{jenkins,jhome,net} verified + removed (logs/old-lab-cleanup.log)
- [x] M3a fresh lab up (lab_up.sh, ledger.md); adaptation: LAB pubkey installed into isolated devtools authorized_keys; Setup Wizard skipped via init groovy (admin/admin2569); plugins via jenkins-plugin-cli
- [x] M3b credentials devtools-ssh + dockerhub, job docker-build-push (SCM, */main, lightweight)
- [x] M4 upload receiver running (pid in upload_receiver.pid)
- [!] Build #1 Build Now (SCM a8d0c0b): **FAILURE at Test** — first run exports no APP_VERSION env to sh (`APP_VERSION=` empty, grep `version:,build:1,`); Connect/Clone/Build ok; Push/Deploy skipped. logs/build1_console.log
- [x] SCM job build #2 APP_VERSION=1.0.0 (Build with Parameters): SUCCESS 6/6, pushed lab3-2 digest c7f2b86f…, deployed, health version:1.0.0,build:2 (logs/build2_console.log)
- [x] SCM job build #3 APP_VERSION=1.1.0: SUCCESS 6/6, pushed lab3-3 digest 3dd2e5a0… (still on Hub), deployed (logs/build3_console.log)
- [x] LOCAL FIX (unpublished, differs from SCM a8d0c0b): Jenkinsfile environment adds `APP_VERSION = "${params.APP_VERSION}"`. SCM job did NOT test this. Tested via job **docker-build-push-localfix** reading the local Jenkinsfile (sha256 fff6238f…) from fixture git repo git://devtools/fixture.git (commit d13ae94, fixture_scm.sh, served inside isolated devtools only); app source still cloned from GitHub a8d0c0b
  - localfix #1 Build Now (no params): SUCCESS 6/6, APP_VERSION=1.0.0 reached sh, pushed lab3-1 digest 71536f72…
  - localfix #2 APP_VERSION=1.1.0: SUCCESS 6/6, pushed lab3-2 digest a6c5def3… (overwrote SCM #2's lab3-2 on Hub), deployed
- Current shop: catfood-web = <DOCKER_USER>/catfood-shop:lab3-2 from localfix #2 → /api/health version 1.1.0 build 2 (healthy)
- Hub tags now: lab3-1 (localfix#1), lab3-2 (localfix#2), lab3-3 (SCM#3) — logs/dockerhub_tags_final.txt
- Docker Hub auth dir removed by post on devtools after every build (verified ls /root/lab3-work → only DevTools)
- [x] README 4.3 rewritten: whole Jenkinsfile in one ```groovy fence (cmp vs Jenkinsfile: BYTE-IDENTICAL apart from trailing newline, check via .task-run/fence_extract.txt) followed by Thai explanations of header comments, pipeline/agent, options, parameters, environment (4 values incl. new APP_VERSION), shared sshagent/heredoc patterns, Stage 1–6, post. Generator: build_readme_43.py + readme_43_template.md. Image 10 caption: dropped the claim "ยังไม่ได้รันจริงบน Jenkins"; images unchanged (awaiting parent screenshots)
- [x] Parent host screenshots received (.task-run/images)
- [x] FINAL (2026-09-27T22:02:25Z): 10 new real images in images/ (localfix stages, shop v1.0.0 #1 / v1.1.0 #2 full-page, 5 tour frames, lab3_shop_tour.gif 5×2 s 1440×1000); README image 10/11ก/12 replaced, step 5 bug box, step 7 overview + GIF; fence cmp identical; 51 links OK; secret scan clean (worker*.jsonl username → placeholder)
- [x] Lab cleanup done: l3e2e containers/volume/network + fixture daemon removed; unrelated container still present (logs/final-cleanup.log)
- [x] Receiver restarted (new pid in upload_receiver.pid) with read-only GET /artifact/<allow-listed name> from ../images; kill once the parent finishes preview
- [x] completion-report.md + completion-email.html (Thai, not sent; the parent sends it)

## Not published
- No git commit/push made. Local Jenkinsfile (+2 lines) and README differ from GitHub a8d0c0b. **Until pushed, a student following step 5 with the GitHub file hits the build-#1 Test failure.**

## Cleanup plan — EXECUTED (only the receiver remains)
docker rm -fv devtools-l3e2e-406430-jenkins devtools-l3e2e-406430-devtools; docker volume rm devtools-l3e2e-406430-jhome; docker network rm devtools-l3e2e-406430-net; kill $(cat .task-run/upload_receiver.pid)
