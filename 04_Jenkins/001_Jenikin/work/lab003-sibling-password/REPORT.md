# LAB003 second redesign — sibling topology + SSH password (yolo3, 2026-09-26)

**Status: CAPTURE HANDOFF, not final.** The run environment is alive for host-browser screenshots. Waiting for `CAPTURE_DONE`, then `scripts/finalize.sh` integrates the images, rebuilds and verifies the README, and removes every owned resource. Cleanup has **not** been done yet.

## Deliverables (all under `04_Jenkins/001_Jenikin`)

| path | change |
|---|---|
| `003_LAB_Docker_Build_Push/Jenkinsfile` | Rewritten for password SSH. Every SSH path (Connect … Deploy, Push login, `post`) is `sshpass -e ssh -o StrictHostKeyChecking=yes -o PreferredAuthentications=password "$SSH_USER@devtools"` inside `withCredentials([usernamePassword('devtools-ssh' → SSH_USER/SSHPASS)])`. The `sh` scripts are constant single-quoted strings, so there is no Groovy interpolation of secrets. The validated vars are written as `NAME='value'` lines at the top of `remote.sh`. The Docker Hub token still travels over SSH stdin to `--password-stdin`. The owned-container label checks, digest push/pull, health tests and Clean-before-Pull are unchanged. No gateway, key or `devtools-gw`. |
| `003_LAB_Docker_Build_Push/README.md` | Regenerated (956 lines now; it will grow with the screenshots). It has one sequential host-shell setup (steps 1–5), the credential table, the Jenkinsfile reading, the full Jenkinsfile, and real evidence for builds #1–#5. Removed: Path A/B, gateway, key/ssh-keygen setup, SSH agent, and the gateway troubleshooting. |
| `003_LAB_Docker_Build_Push/images/` | Kept 4 topology-neutral captures (GitHub source, Docker Hub PAT). Added the cyolo1 diagrams as `lab3_diagram_sibling_*.png` and `lab3_sib_unlock.png` (coordinator capture). **67 obsolete images moved** to `work/lab003-sibling-password/archive_old_images/` (MANIFEST + SHA256SUMS). `.ipynb_checkpoints` was not touched. |
| app code, `globals.css`, `.ipynb_checkpoints` | untouched |

The work files are in `work/lab003-sibling-password/`:
- `backup_prior/`: the previous README and Jenkinsfile, with SHA256SUMS.
- `README.tmpl.md`, `blocks/*.sh`: the exact host blocks.
- `scripts/`:
  - `lab.sh`: the harness.
  - `docker-map.sh`: maps learner names to run names and refuses learner resources.
  - `pty_ssh.py`, `build_readme.py`, `verify_readme.py`, `integrate.py`, `capture_ready.py`, `finalize.sh`.
- `shots.json`, `diagram-brief.md`, `CAPTURE_READY.json`.
- `out/`: run 2 evidence.
- `out.326752/`: run 1, discarded (see below).

## Learner topology implemented

These are host-shell commands, and they are also the exact README block:

```
docker rm -f jenkins devtools
docker network create cicd-net
docker run -dit --name devtools --network cicd-net --privileged --tmpfs /run --restart unless-stopped -p 2222:22 -p 3000:3000 tuchsanai/devtools:2569_1
docker run -d --name jenkins --network cicd-net --restart unless-stopped -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
```

Then:
1. Unlock and run the wizard.
2. `docker exec -u root -e DEBIAN_FRONTEND=noninteractive jenkins sh -c "apt-get … sshpass"` (the only change to stock Jenkins; no Docker tools).
3. Pin the host key. `sed` builds the known_hosts line from devtools' own `/etc/ssh/ssh_host_ed25519_key.pub`, then `docker cp` devtools → host → jenkins:/tmp. The **jenkins** user copies it into `~/.ssh/known_hosts`, and the fingerprints are compared.
4. Interactive `docker exec -it jenkins ssh -o StrictHostKeyChecking=yes root@devtools hostname` with password `passwd`.
5. Credentials `devtools-ssh` (Username with password, root/passwd, username not secret) and `dockerhub`.

## Tests (run 2, hash c23096, real Docker Hub)

- **Isolation:** `devtools-lab003-c23096` (alias `devtools`) + `jenkins-lab003-c23096` (alias `jenkins`) on `cicd-net-lab003-c23096`, volume `jenkins-lab003-c23096-home`. Ports are loopback only: 18080→8080, 2223→22, 13000→3000. 0 other `devtools-*` containers existed (limit 7).
- **Fidelity:** every README host block was executed verbatim through `docker-map.sh`. The SSH test ran in a real pty that typed the password.
- **Security:** Jenkins 2.568.3 stock `lts-jdk21`, with HudsonPrivateSecurityRealm, anonymous access 403, and a test admin with a random password (`private/`, mode 600, git-ignored).

| check | result |
|---|---|
| jenkins has docker / docker.sock | none / none; sshpass `/usr/bin/sshpass` |
| DNS `devtools` from jenkins | resolves on cicd-net |
| SSH with empty known_hosts + strict | `Host key verification failed.` exit 255 before any password prompt |
| host-key pin | devtools and jenkins fingerprints equal `SHA256:xx0jAuPG…` |
| interactive password SSH | prompt → hostname `4dc7e37d7397`, no yes/no question |
| #1 1.0.0 | SUCCESS 8/8, 74 s. Fresh build; 5 layers Pushed. `lab3-sibling-20260926r2-1` `sha256:ea2559a9…` |
| #2 1.1.0 | SUCCESS 30 s. Clean: `ลบแอปเดิม catfood-web (ea2559a94002 …)`, then Untagged/Deleted and the assertion that the tag and digest are absent. Pull `Downloaded newer image` by digest. Push = Pull = Deploy `sha256:2b717397…`. Health 1.1.0/build 2 |
| #3 `APP_VERSION=1.2.0; id` | FAILURE at Connect in 3 s. Only the post SSH ran (no parameter crossed SSH) |
| #4 `GIT_REF=no-such-branch` | FAILURE at Clone (`Remote branch … not found`, exit 128). Post cleaned the build-4 dirs |
| #5 wrong SSH password (random, never stored) | FAILURE at Connect: `Permission denied, please try again.`, `script returned exit code 5`. Post SSH also refused and was caught |
| app after #3–#5 | still build 2, same container (`build=2`, healthy) |
| credential restored | `devtools-ssh user=root usernameSecret=false restored=true` |
| README verify (`verify_readme.py`) | exit 0. 8 blocks identical and `bash -n` clean. Embedded Jenkinsfile identical. Both SSH calls use sshpass+strict. No banned mechanisms or old images. Fences balanced, no trailing whitespace, figures sequential. The token and admin password appear in none of the 66 files. The Hub account is replaced by `<DOCKER_USER>` |
| git | the repo auto-commit (not yolo3) already committed some work files. History checked: only `private/.gitignore` and the non-secret `state.env` from `private/`/state. 0 hits for the admin password or the token |

## Issues found and fixed during the run

1. The REST-created `UsernamePasswordCredentialsImpl` without `<usernameSecret>false</usernameSecret>` masked `root` as `****` (`user=****`, `/****/lab3-work`). A learner creating it in the UI (checkbox unchecked by default) sees `root`. Run 1 (hash 326752) was fully torn down and redone as run 2 with prefix `…r2`. Run 1's pushed tag `lab3-sibling-20260926-1` was left on Hub, not overwritten. The troubleshooting table mentions the checkbox.
2. `docker cp` into jenkins created a root-owned `known_hosts`, and ssh then warned `hostfile_replace_entries … Operation not permitted` on every connection. The jenkins user now copies the file from /tmp.
3. `jenkins-plugin-cli` stalled on `plugin-versions.json` (about 14 KB/s here). The wizard stand-in now installs the same plugin set through the controller's UpdateCenter.

## Residual limitations

- **LAB 4 (and later labs) now conflict with LAB 3.** `004_LAB_Pipeline_From_Git/README.md` still requires `--add-host devtools:host-gateway` and uses credential `devtools-ssh` as an **SSH private key** (`SSH_KEY = credentials('devtools-ssh')`). LAB 1–2 still create Jenkins inside devtools. Out of scope here (LAB003 only), but LAB 4+ need a matching update.
- Step 1 `docker rm -f jenkins devtools` discards the learner's LAB 1–2 devtools (the Jenkins inside it). The README warns about this.
- sshpass lives in the jenkins container layer, so it must be reinstalled if jenkins is recreated (README says so). Host keys are baked into `tuchsanai/devtools:2569_1` (`root@buildkitsandbox`), so every learner's devtools has the same fingerprint. The pin prevents talking to a different image or host, but it is not unique per machine.
- Host commands assume bash/zsh (Linux, macOS or WSL). PowerShell and Git Bash are not supported, because of `\` continuations and `docker exec -it`.
- Pull shows `Already exists` layers. The image refs were verifiably removed, but the containerd content store keeps the blobs. The README explains this.
- Downtime Clean→Deploy was 7 s in the test; there is no rollback (unchanged design).
- The README test notes show loopback test ports. Container names in the evidence are rewritten from `*-lab003-c23096` to `devtools`/`jenkins`, and this is declared.
- 14 of 15 planned screenshots are pending coordinator capture. The README renders without them until then.
- Public Hub tags from this work: `lab3-sibling-20260926-1` (run 1), `lab3-sibling-20260926r2-1`, `-2`. Nothing else was pushed or overwritten.

## Pending (same task, next sequential run)

1. The coordinator captures the shots listed in `CAPTURE_READY.json` into `host-captures/NN-<key>.png`, then creates `CAPTURE_DONE`.
2. yolo3 runs `scripts/finalize.sh`: `integrate.py` → build+verify → `lab.sh cleanup` (the README cleanup block, then `docker rm -fv` of both containers, then network/volume rm, then shred the private files) → rebuild+verify → leftover check.
3. Optional: if cyolo1 updates `diagrams/*.png` per `diagram-brief.md`, `integrate.py` picks them up.

Still alive right now: containers `devtools-lab003-c23096` and `jenkins-lab003-c23096`, network `cicd-net-lab003-c23096`, volume `jenkins-lab003-c23096-home`, and the files `private/jpass` and `private/browser-auth.json`.
