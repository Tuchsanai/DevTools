# LAB003: web-first restructure + credential navigation — result (2026-09-27)

**Status: DONE.** Commit `484f287` was pushed to `origin/main`. Remote main is `484f2878c62483ef2e884428a5c4740d079c800a`, which equals local HEAD. The commit contains exactly 15 LAB paths: README.md, Jenkinsfile, LAB003_FINAL_REPORT.md, and 6 nav screenshots plus 6 crops. No force push, and nothing from `work/`, user CSS or other LABs was included.

## What changed
- **Step 1** now also installs `sshpass`, pins the host key, and has the optional SSH test (1.2–1.4). These were moved unchanged from the old step 4.
- **Step 3** gains 3.0ก–3.0ฉ (Login → gear → Security › Credentials → Stores scoped to Jenkins › System → Global → + Add Credentials). They come before the existing forms, and a note explains the "Global" vs "Global credentials (unrestricted)" labels.
- **Step 4** starts in the web UI (Dashboard → New Item → Pipeline → Configure with Pipeline script from SCM). It then covers the Jenkinsfile design (4.3–4.11) and applying the file via Git (4.12). Old steps 6/7/8 are now 5/6/7, and figures 10–13 were reordered.
- **Jenkinsfile:** only two header comments changed (step 4 → step 1). The non-comment code is identical and the file is still 311 lines. It keeps the real `git clone` on devtools and the credential IDs `devtools-ssh`/`dockerhub`.

## Checks (actual, this session)
- `/pipeline-model-converter/validate` on the preserved Jenkins: the Jenkinsfile and the README skeleton were both "successfully validated".
- The embedded Jenkinsfile is byte-identical to the file, and all 11 📄 excerpts match their line ranges.
- Fences are balanced, 82 local links resolve, and figures run 1…33 in order.
- `git diff --check` is clean, and the secret scan is clean.
- All 6 crops were checked visually.
- **No new pipeline build was run**, because the code is unchanged. The README still uses the historical build evidence from 2026-09-26 and `work/reorder-20260927`.

## Jenkins PRESERVED (not deleted)
- Container `devtools-l3nav-277caf-jenkins`, volume `devtools-l3nav-277caf-jhome` and network `devtools-l3nav-277caf-net` are all kept. Host publish is 127.0.0.1:18490.
- Plugins `workflow-aggregator`, `git` and `pipeline-graph-view` were installed with their dependencies (59, all active) into the same volume. One `safeRestart` was needed, so the container restarted in place under restart=unless-stopped; data was kept.
- A saved job `docker-build-push` uses Pipeline script from SCM (course repo, `*/main`, this Script Path, lightweight). It was **not triggered**, because no real credentials are stored.
- Access helpers are still running: forwarder 127.0.0.1:8080 (pid 408603) and receiver 127.0.0.1:8790 (pid 408601). Coordinator tunnel 7012→8080 and receiver 7013 were left untouched.
- Login is admin / admin2569. Anonymous access returns 403.

GitHub: https://github.com/Tuchsanai/DevTools/commit/484f2878c62483ef2e884428a5c4740d079c800a
README: https://github.com/Tuchsanai/DevTools/blob/main/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/README.md
