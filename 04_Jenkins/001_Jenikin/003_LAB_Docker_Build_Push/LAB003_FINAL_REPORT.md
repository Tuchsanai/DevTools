# LAB 3 final report: sibling Jenkins + devtools, SSH password

Date: 2026-09-26. Scope: `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push` only. Work files and harness are in `../work/lab003-sibling-password/`.

## Result

| item | state |
|---|---|
| [`README.md`](./README.md) | Rebuilt from tested blocks and real outputs: 736 lines. 309 of those are the full Jenkinsfile, collapsed in `<details>`, so the reading flow is 421 lines (was 956 total, about 650 visible). It has 27 figures (2 diagrams, 2 reused common-context captures, 23 host captures). |
| [`Jenkinsfile`](./Jenkinsfile) | Password SSH in every remote path: `sshpass -e ssh -o StrictHostKeyChecking=yes -o PreferredAuthentications=password` inside `withCredentials([usernamePassword('devtools-ssh')])`. The `sh` strings are constant and single-quoted. Unchanged in phase 2. |
| `images/` | `lab3_sib_<key>.png` is the full capture and `lab3_sib_<key>_crop.png` is the crop shown in the README. The files are cyolo1 diagrams `lab3_diagram_sibling_*`, the PAT and GitHub captures, and nothing else. The 67 obsolete topology images are archived in `../work/lab003-sibling-password/archive_old_images/` (MANIFEST + SHA256SUMS). |
| app code, `catfood-shop/app/globals.css`, `.ipynb_checkpoints`, other labs | Not modified by this work. |

## Learner topology (as tested)

```bash
docker rm -f jenkins devtools
docker network create cicd-net
docker run -dit --name devtools --network cicd-net --privileged --tmpfs /run \
  --restart unless-stopped -p 2222:22 -p 3000:3000 tuchsanai/devtools:2569_1
docker run -d --name jenkins --network cicd-net --restart unless-stopped \
  -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
```

The later steps are:
1. Unlock and run the wizard.
2. Install `sshpass` in `jenkins` (no Docker CLI, no socket).
3. Pin devtools' ed25519 host key into `jenkins`' `known_hosts` via `docker cp`.
4. Do an interactive password SSH test.
5. Create the credentials `devtools-ssh` (Username with password, `root`/`passwd`) and `dockerhub`.
6. Run the job `docker-build-push`.

## Test run (hash `c23096`, real Docker Hub)

**Isolation.** The run used `devtools-lab003-c23096` (alias `devtools`) and `jenkins-lab003-c23096` (alias `jenkins`) on `cicd-net-lab003-c23096`, with volume `jenkins-lab003-c23096-home`. Ports were loopback-only: 18080→8080, 2223→22, 13000→3000. Every README host block ran verbatim through a name/port mapper.

**Images.**
- `tuchsanai/devtools:2569_1`: `sha256:b3e0784f66b7…`
- `jenkins/jenkins:lts-jdk21`: `sha256:66ebfe0c8828…` (Jenkins 2.568.3)

**Security setup.** Security was enabled, anonymous access got 403, and the test admin had a random password.

| check | result |
|---|---|
| Docker access from jenkins | `docker CLI = none docker.sock = none`, `sshpass = /usr/bin/sshpass` |
| SSH with empty `known_hosts` and strict checking | `Host key verification failed.`, exit 255, before any password prompt |
| host-key pin | devtools and jenkins fingerprints both `SHA256:xx0jAuPG…`. This is the key baked into the image (`root@buildkitsandbox`), so it is the same for every clone. |
| interactive password SSH | prompt, then hostname, with no yes/no question |
| #1 `1.0.0` | SUCCESS, 8/8 stages, 74 s. Push = Deploy digest `sha256:ea2559a940026b2eb8feb704f941c7b1980364e02429ac8145e1393d2a2665c8` |
| #2 `1.1.0` | SUCCESS in 30 s. The digests are equal at every step: Build manifest = Push = Pull `Digest:` = Deploy `image:` = `sha256:2b717397cbd2b05d53cc67dd5f85c90035a045b4bbcd491c399a46e844e815d4`. Clean removed the build #1 shop (`ea2559a94002`) and the local build-2 image before Pull (`Downloaded newer image`). Health reports 1.1.0 / build 2. Clean→Deploy downtime was 7 s. |
| #3 `APP_VERSION=1.2.0; id` | Negative test. FAILURE at Connect (regex check) in 3 s. Only the `post` SSH ran, and no parameter crossed SSH. |
| #4 `GIT_REF=no-such-branch` | Negative test. FAILURE at Clone (`Remote branch … not found`, exit 128). `post` cleaned up the build-4 files. |
| #5 wrong SSH password (random, never stored) | Negative test. FAILURE at Connect (`Permission denied`, `script returned exit code 5`). |
| shop after #3–#5 | still build 2, same container `2d7c4b120c21`, healthy |
| credential restored | `devtools-ssh user=root usernameSecret=false restored=true` |
| README cleanup block | It removed the lab-labelled container and images inside devtools, and `devtools`/`jenkins` stayed up. |

## Screenshot provenance

All captures are real host-Chrome screenshots taken over an SSH tunnel by the coordinator. Nothing was generated or retouched.
- Sources are in `../work/lab003-sibling-password/host-captures/`, as JPEG data under `.png` names.
- `01-unlock` comes from run 1 (`326752`), which had the same topology; the Unlock page is common UI.
- `02`–`19` come from the current run 2 (`c23096`).
- The README image is a pure rectangular crop of the decoded pixels, with no resize and no retouch. The full capture is re-encoded as real PNG with identical pixels and is linked from each crop.
- `integrate.py` asserts both of these properties.

| source | crop in README | source size | crop size |
|---|---|---|---|
| `01-unlock.png` | `lab3_sib_unlock_crop.png` | 1376×522 | 992×482 |
| `02-dashboard.png` | `lab3_sib_dashboard_crop.png` | 1370×497 | 985×104 |
| `03-ssh_credential.png` | `lab3_sib_ssh_credential_crop.png` | 1376×500 | 550×464 |
| `03-ssh_credential-id.png` | `lab3_sib_ssh_credential_id_crop.png` | 1376×500 | 550×464 |
| `04-credentials.png` | `lab3_sib_credentials_crop.png` | 1376×500 | 1120×245 |
| `05-pipeline_config.png` | `lab3_sib_pipeline_config_crop.png` | 1370×497 | 900×369 |
| `06-build1_graph.png` | `lab3_sib_build1_graph_crop.png` | 1370×497 | 1314×177 |
| `07-build1_connect.png` | `lab3_sib_build1_connect_crop.png` | 1370×497 | 990×322 |
| `07-build1_connect-ssh.png` | `lab3_sib_build1_connect_ssh_crop.png` | 1370×497 | 990×154 |
| `08-build_parameters.png` | `lab3_sib_build_parameters_crop.png` | 1370×497 | 910×325 |
| `16-build2_clone.png` | `lab3_sib_build2_clone_crop.png` | 1370×497 | 990×345 |
| `17-build2_build.png` | `lab3_sib_build2_build_crop.png` | 1370×497 | 990×420 |
| `18-build2_test.png` | `lab3_sib_build2_test_crop.png` | 1370×497 | 990×293 |
| `19-build2_push.png` | `lab3_sib_build2_push_crop.png` | 1370×497 | 990×420 |
| `09-build2_clean_pull.png` (shows Clean only) | `lab3_sib_build2_clean_crop.png` | 1370×497 | 990×298 |
| `09-build2_pull.png` | `lab3_sib_build2_pull_crop.png` | 1370×497 | 990×343 |
| `10-build2_deploy.png` | `lab3_sib_build2_deploy_crop.png` | 1370×497 | 990×374 |
| `11-app_v110.png` | `lab3_sib_app_v110_crop.png` | 1370×497 | 1240×375 |
| `11-app_deployment.png` | `lab3_sib_app_deployment_crop.png` | 1370×497 | 700×400 |
| `12-hub_tags-context.png` | `lab3_sib_hub_tags_crop.png` | 2740×995 | 932×864 |
| `13-build3.png` | `lab3_sib_build3_crop.png` | 1370×497 | 1314×394 |
| `14-build4.png` | `lab3_sib_build4_crop.png` | 1370×497 | 990×242 |
| `15-build5.png` | `lab3_sib_build5_crop.png` | 1370×497 | 990×290 |

Notes on individual captures:
- `12-hub_tags.png` is the same Tags page scrolled down. `12-hub_tags-context.png` shows the same two tag/digest rows plus the repository header, so only the context version is in the README; the other stays in `host-captures/`.
- The Jenkins Update-credential dialog has no Kind selector. The caption says Username with password only because of the Username/Password fields and the `root/******` list entry.
- The dashboard's last failure `#5` is the intended negative test.
- The build-parameters form was opened for display after all builds, and Build was not pressed.
- Reused common context:
  - `lab3_hub_04_pat_setup*.png` (Docker Hub PAT page) and `lab3_github_01_source*.png` (GitHub source), both from an earlier capture round.
  - `lab3_diagram_sibling_architecture.png` and `lab3_diagram_sibling_pipeline.png`: cyolo1 built-in imagegen, not screenshots, inspected and not regenerated.
- The public Docker Hub namespace (the same as the course image `tuchsanai/devtools`) is visible in Hub/credential screenshots. README text uses `<DOCKER_USER>`.

## Secrets

- No secret values were printed during the work.
- `scripts/secret_scan.py` found 0 hits in the 127 working-tree text files of LAB003 plus `work/lab003-sibling-password`, before cleanup. It checked:
  - known values: the Docker Hub token, the test admin password, the run 1 and run 2 initial admin passwords, and their 16-char prefixes;
  - patterns: Docker/GitHub/AWS tokens, private-key bodies, `<16 hex>•` redactions, and basic-auth URLs.
- The final scan ran after cleanup, with the token and the patterns.
- The earlier `out/unlock.txt` evidence contained the first 16 characters of the initial admin password. It is now a placeholder (both runs), those fragments are redacted in `yolo-phase1.jsonl`, and the README shows no example value.
- **Already in git history (cannot be rewritten without git writes):** the user-owned auto-commit service committed the unredacted evidence before phase 2 fixed it.
  - The run 1 fragment is in `out/unlock.txt` and `yolo-phase1.jsonl` at `92d3888`/`8b38dc9`.
  - The run 2 fragment is in the phase-1 956-line `README.md` at `3cdfcba` (2026-09-26 21:29 +0700), which is on `origin/main`. That commit landed after the scrub but before the README was rebuilt.
  - Both Jenkins instances are destroyed, so the fragments no longer unlock anything. The working tree is clean, and the next auto-commit will replace the README.
  - `001_LAB_Jenkins_On_Docker/README.md` at HEAD also contains a `<16 hex>•` unlock example. That is another lab and was left as is.
- `secret_scan.py --git` after cleanup (token + patterns): the only HEAD hits are those two `<16 hex>•` README examples.

## Model and cost metadata

| step | model | usage | cost |
|---|---|---|---|
| phase 1 (yolo3: redesign, harness, runs 1–2, capture handoff) | `claude-opus-5-5` | input 170, cache write 309,837, cache read 17,159,962, output 148,749 (thinking 66,931), 91 turns, 50.5 min | USD 8.8863484 (list basis) |
| diagrams (cyolo1, built-in `image_gen` only: 2 generations + 2 corrective edits, prompts in `../work/lab003-sibling-password/diagrams/cyolo-result.txt`) | `gpt-6-astra`, effort high | input 245,283 (cached 213,376), output 4,319, reasoning 434 | not supplied |
| phase 2 (yolo3: integration, lean README, review corrections, cleanup, this report) | `claude-opus-5-5` | recorded by the caller in `yolo-phase2.jsonl` | measured by the caller |

## Cleanup

- `scripts/lab.sh cleanup` ran the README cleanup block, then `docker rm -fv` of both run containers, then removed the network and volume.
- It shredded `private/jpass` and `private/browser-auth.json`. The temporary scan-value files were shredded too.
- Result: 0 containers, networks or volumes matching `c23096`, and `private/` holds only `.gitignore`. No other container was touched.
- The temporary previews `/tmp/prev_architecture-sibling.jpg` and `/tmp/prev_pipeline-sibling.jpg` were removed. `/tmp/prev_01-unlock.jpg` is not ours and was left alone.
- Kept on purpose as test evidence: the public repo `catfood-shop` with tags `lab3-sibling-20260926-1` (run 1), `lab3-sibling-20260926r2-1` and `lab3-sibling-20260926r2-2`. Nothing on Hub was overwritten or deleted.

## Git

yolo3 made no git writes (no add, commit or push). The user-owned auto-commit service committed during this work:
- `3cdfcba` "1" at 2026-09-26 21:29:04 +0700: the images, work files and the phase-1 README.
- `e730d40` "Update yolo-phase2.jsonl" at 21:29:09.

The local `origin/main` ref equals `HEAD`, so the service also pushes. The final README and this report are still uncommitted, and the service is expected to commit and push them. `catfood-shop/app/globals.css` shows as modified; that is a pre-existing line-ending-only (CRLF) change that this work did not make or touch.

## Compatibility note: LAB 4

`004_LAB_Pipeline_From_Git` still expects `devtools-ssh` to be an **SSH private key** credential (`SSH_KEY = credentials('devtools-ssh')`) and a `--add-host devtools:host-gateway` setup. After LAB 3, `devtools-ssh` is Username with password on `cicd-net`, so LAB 4 needs a matching update before it is used with this LAB 3. LAB 4 was not modified.

## Residual limitations

- Step 1 `docker rm -f` removes an existing `devtools` together with LAB 1–2 content; the README warns about this.
- `sshpass` lives in the jenkins container layer and must be reinstalled if `jenkins` is recreated.
- The host commands assume bash/zsh (Linux, macOS, WSL).
- Clean→Deploy has a short outage and no rollback, by design.
- Pull may show `Already exists` layers from the containerd content store, even though the image refs were verifiably removed.

## Verification

```bash
cd 04_Jenkins/001_Jenikin/work/lab003-sibling-password
python3 scripts/verify_readme.py      # blocks = tested blocks, Jenkinsfile parity, links, PNG crops, no placeholders/secrets
python3 scripts/secret_scan.py        # narrow gitleaks-style scan (prints file + rule only)
git diff --check -- ../../003_LAB_Docker_Build_Push
```
