# LAB003 reorder — final result (2026-09-27)

Commits on `main`, pushed without force and checked with `git ls-remote`:
- `e200b5556263c9c9837c7d488c966cc739043d22`: content change (README step 5 teaching, SCM step 6, new screenshots, Jenkinsfile `skipDefaultCheckout()`, report section)
- `667350bb975f8be5ee2795b6f87e2871b12c8986`: real post-push evidence (console excerpt, figures 14–15, report row). This is the final remote `main`.

Each commit staged only these explicit paths: `README.md`, `Jenkinsfile`, `LAB003_FINAL_REPORT.md` and `images/lab3_scm_*`. `catfood-shop/app/globals.css`, `work/`, other LABs and the other working-tree changes were not staged and not touched.

## README
- **Step 5 "สร้าง `Jenkinsfile` ทีละชั้น"**
  - Offers two options. Option ก runs the course file (no fork needed). Option ข writes your own file in your own public repo.
  - 5.1 covers the file name, the Script Path and git add/commit/push, and adds the GitHub figure.
  - 5.3 is a full skeleton with balanced braces. A table shows where helper functions, agent, options, parameters, environment, stages/stage/steps/script and post go.
  - 5.4–5.8 add the layers in order: Credentials → SSH → clone → build/test → push/pull/deploy.
  - Each block is labelled "📄 ส่วนหนึ่งของ Jenkinsfile บรรทัด a–b · ตำแหน่ง". There are 12 labelled excerpts.
  - The Test and Deploy scripts are now `bash` fences with real shell escaping (`\`), and the README explains why the Groovy source has `\\`.
  - 5.9 has the complete file. The embed is byte-identical to `Jenkinsfile`.
  - The phrase "ไม่ต้องพิมพ์หรือคัดลอกไฟล์" was removed.
- **Captions**
  - Figure 6 now says the Add Credentials button is centred in the empty store.
  - Figures 8 and 9 now say the values are the dummy `demostudent` user and a dummy token.
  - The Lightweight checkout row no longer promises that only the Jenkinsfile bytes are fetched.
  - The older-evidence note now says "same 8-stage behaviour, earlier file without skipDefaultCheckout".
- **Figures, 33 in order**
  - 10: GitHub Jenkinsfile page. It is a host-native capture showing commit `92d3888`, from before this change.
  - 13: crop of Branch and Script Path from the stitched full page.
  - 14–15: post-push Console Output and Stages, both real.
  - 30: Docker Hub tags, a host-native capture showing the 2026-09-26 `lab3-sibling-20260926r2` tags, not tags from this test.
  - Crops are plain crops made on the remote. No image was generated or annotated.

## Tests (actual)
- The skeleton and the Jenkinsfile both got "Jenkinsfile successfully validated" from the Jenkins 2.568.3 linter (`evidence/jenkins-linter-teach.txt`).
- `bin/validate.py` returned ALL PASS:
  - 61 local links, 0 missing
  - the full embed is exact
  - all 12 excerpts match their line ranges
  - skeleton braces are balanced
  - fences are balanced
  - figures 1–33 are consecutive and steps 1–8 are consecutive
  - no forbidden phrases, no secrets
- `git diff --check` was clean.
- A secret scan with the runtime values (Docker/GitHub/admin) found 0 matches in the docs and evidence.
- **Post-push build `verify-local/upstream-main` #2** read GitHub `main` at `e200b55`:
  - SUCCESS in 29 s.
  - Stages: Connect, Clone, Build, Test, Push, Clean, Pull, Deploy. **No `Declarative: Checkout SCM`.**
  - Push digest = Pull = Deploy = `sha256:a33d7870924a79f76b6e3844672ce397593ab0a8faaba34ad5453b96ed28fd5f` (tag `lab3-reorder-20260927p-2`).
  - The shop answered 1.0.0, build 2, commit `e200b5556263`.
  - Redacted console: `evidence/build-upstream-main-2.postpush.console.txt`.
- The top-level `docker-build-push` job, which has the dummy global credentials, was never built.

## Cleanup
- `bin/cleanup.sh` removed both `devtools-l3reorder-8de7f5-*` containers, the volume `-jhome` and the network `-net`.
- The helper pidfiles were stale, so the actual owned forwarders and receiver (cwd = this directory) were stopped by PID.
- Verified: 0 containers, volumes or networks matching `l3reorder`, and no listeners on 8080, 8790 or 3000.
- The temporary Jenkins admin password file was shredded. Nothing unrelated was touched.
- Docker Hub tags `lab3-reorder-20260927{l,u,p}-*` stay on Hub as test evidence.

## Status note
While it ran, the lab Jenkins UI was reachable anonymously (HTTP 200) even though an admin user existed. That was acceptable only because it was a loopback-only, disposable local environment, and it has now been deleted.
