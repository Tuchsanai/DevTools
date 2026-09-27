# LAB003 reorder 2026-09-27 — result

Author: yolo3 (Opus). No git commit/push. Every file this task wrote is inside `003_LAB_Docker_Build_Push/`: `README.md`, `Jenkinsfile`, `work/reorder-20260927/**`, plus screenshots saved by the receiver into `images/`.

## Completed changes

### README.md (Thai), 8 steps (previously 9)
1. **Step 1**: no change.
2. **Step 2**: removed the final "✅ เข้า Dashboard…" paragraph and figure 6 (`lab3_sib_dashboard*`) with its caption. The step now ends at figure 5ฉ.
3. **Step 3 (new position, right after Jenkins setup): Jenkins Credentials.**
   - A table explains what each credential is for:
     - `devtools-ssh` (root/passwd) is used for SSH in every stage and in `post`.
     - `dockerhub` (username + PAT) supplies the username for the repo name in Connect, the login + push in Push, and the pull by digest + logout in Pull. PAT needs Read & Write.
   - Sub-steps 3.1 and 3.2 give field tables that match the real Jenkins 2.568.3 modal ("Add Username with password").
   - Figures 6–9 are new genuine captures.
4. **Step 4: prepare `jenkins` to SSH to `devtools`.**
   - 4.1 sshpass, 4.2 host-key pin, 4.3 optional SSH test.
   - The old steps 3/4/5 are kept word-for-word (commands, test markers, expected output). Only the references to other steps changed.
   - This step now comes after Credentials and before the first real use (Connect).
5. **Step 5: understand the Jenkinsfile layer by layer.**
   - 5.1 explains who loads what. The Jenkins controller fetches the Jenkinsfile through SCM before the pipeline starts. devtools cannot do this bootstrap, because Jenkins only knows about SSH and credentials after it has read the Jenkinsfile. The app `git clone` and all docker commands then run over SSH on devtools. `skipDefaultCheckout()` is explained here.
   - Then the layers, in order: 5.2 Credentials → 5.3 SSH (`onDevtools` + Connect) → 5.4 git clone → 5.5 Docker build/test → 5.6 push → clean → pull (digest) → deploy.
   - 5.7 has the 8-stage table and the full Jenkinsfile.
   - The snippets are cut from the Jenkinsfile by a script, so they are exact excerpts (only leading indentation is removed).
6. **Step 6: job as Pipeline script from SCM.**
   - Settings: Git `https://github.com/Tuchsanai/DevTools.git`, `*/main`, Script Path `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile`, Lightweight checkout. Figures 10–12 are new genuine captures.
   - Added the expected console head and a note about the first slow fetch and the old `Declarative: Checkout SCM` stage.
   - Added a note that figures 13–29 come from the earlier Pipeline-script run. The stages are identical.
7. **Steps 7 and 8**: these were old steps 8 and 9, renumbered. Figures were shifted +2 (now 16–29).
8. **Checklist, troubleshooting, questions**:
   - Step references renumbered (4.1 and 4.2).
   - Added two SCM troubleshooting rows and review question 5.
   - The final report line now says the SCM mode was tested on 2026-09-27.
9. Figures are now numbered 1–29 with no gaps. The old credential figures (`lab3_sib_ssh_credential*`, `lab3_sib_credentials*`) and the Pipeline-script config figure (`lab3_sib_pipeline_config*`) are no longer referenced. **I did not delete their files.**

### Jenkinsfile (3-line diff vs upstream main `2a47c68`)
- Added `skipDefaultCheckout()` in `options`. The course repository's `.git` is 1.3 GB, and without this option Declarative runs a full `Checkout SCM` into the Jenkins workspace that nothing uses.
- Header comment: sshpass is now "ขั้นที่ 4", plus one line explaining the SCM loading.
- The 8 stages, push-before-clean ordering, digest pull/deploy, `post` block and parameters are all unchanged.

## Evidence

### Static checks (`bin/validate.py` → `evidence/static-validation.json`): **ALL PASS**
- 56 local links, 0 missing.
- The full Jenkinsfile embedded in the README is byte-identical to `Jenkinsfile`.
- All 12 groovy blocks are contiguous excerpts of the Jenkinsfile.
- Code fences are balanced.
- Figures are sequential with no duplicates.
- Steps 1–8 are consecutive. No reference points to a missing step or sub-step, and the header says "8 ขั้น".
- Section order and layer order are as required.
- No secrets found. The public image name `<owner>/devtools:2569_1` is the only allowed match.
- `git diff --check` is clean.

### Jenkins declarative linter (`/pipeline-model-converter/validate`, Jenkins 2.568.3)
The local and the upstream Jenkinsfile both returned "successfully validated". See `evidence/jenkins-linter.txt`.

### Real builds (not simulated)
Both builds ran on the owned Jenkins + devtools and did a real Docker Hub push and pull, using runtime-env credentials in folder scope. Consoles are redacted in `evidence/build-*.console.txt`, and the summary is in `evidence/builds-summary.json`.

| job | source of Jenkinsfile | result | stages |
|---|---|---|---|
| `verify-local/local-jenkinsfile` #1 | local bare repo holding the **modified** Jenkinsfile (never pushed) | **SUCCESS**, 76 s | Connect, Clone, Build, Test, Push, Clean, Pull, Deploy (no Checkout SCM) |
| `verify-local/upstream-main` #1 | **GitHub main** (read-only) | **SUCCESS**, 151 s | `Declarative: Checkout SCM` + the same 8 stages |

- The upstream Jenkinsfile is compatible with SCM mode. It is only slower because of the full checkout.
- Tags pushed to the Docker Hub repo `catfood-shop` from the runtime-env account: `lab3-reorder-20260927l-1` and `lab3-reorder-20260927u-1`.
- Composite in README: the README console-head block uses the real GitHub `Obtained … from git https://github.com/…` line from the upstream run, followed by the stage lines from the modified run. The workspace path shown is the student job's path. **The exact post-push console has not been observed**, because the change is not pushed to GitHub.

### Screenshots
- Received from the coordinator through the receiver: shots 01–07, full images only. Receipts with sha256 are in `evidence/receiver-receipts.jsonl`.
- I reviewed them and they match the captions. Shot 07 is a stitched full-page capture.
- No `_crop` images were received, so the README links the full images. If crops arrive later, `bin/build_readme.py` relinks them automatically.
- I did not create any image.

## Remaining work / notes
1. **Push is needed** (not authorized here). Until the updated Jenkinsfile is on GitHub main, a student job will still show `Declarative: Checkout SCM` and do the 1.3 GB clone. It still works (proven by the upstream run above).
2. Deferred shot 08 (console after the push) is optional and not referenced in the README.
3. Two images appeared in `images/` **outside the receiver** (no receipt, not in the allowlist): `lab3_scm_dockerhub_tags.png` and `lab3_scm_github_jenkinsfile.png`, at 01:56. I did not reference, inspect or delete them. The coordinator should confirm where they came from.
4. The environment is still up. Cleanup: `work/reorder-20260927/bin/cleanup.sh`. It removes only `devtools-l3reorder-8de7f5-*` plus the forwarders and receiver. It has not been run yet.
5. `catfood-shop/app/globals.css` and the other files in `work/` were not touched.
