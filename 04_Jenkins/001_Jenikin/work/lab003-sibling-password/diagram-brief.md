# LAB 3 diagram brief (for cyolo1) — sibling topology + SSH password

Two illustrative diagrams for `003_LAB_Docker_Build_Push/README.md`. They are captioned in the README as "แผนภาพประกอบ ไม่ใช่ภาพหน้าจอ". English labels, large type, white opaque background, navy/teal/blue/orange palette. Fit a ~880 px GitHub README column, so no text smaller than about 22 px at 1254 px width.

Deliver to `work/lab003-sibling-password/diagrams/`:

| file | README target (copied by `scripts/integrate.py`) |
|---|---|
| `architecture-sibling.png` | `images/lab3_diagram_sibling_architecture.png` |
| `pipeline-sibling.png` | `images/lab3_diagram_sibling_pipeline.png` |

## Status of the 13:33 versions already in `diagrams/`

Both match the implemented design and are used as they are. The optional refinements below are small. If you skip them, nothing in the README is wrong.

- Architecture: add a third host port, `host:2222 → devtools:22`, labelled "student SSH (optional)", on the devtools bottom border beside `host:3000`. Add "sshpass" under "SSH client" in the jenkins box. Add a small "pinned host key" tag on the SSH arrow.
- Pipeline: under the "SSH devtools:22" arrow, add a small line "sshpass -e · StrictHostKeyChecking=yes".

## 1. Architecture (`LAB 3 | System Architecture`)

Containment, outer to inner:

1. **Student Docker host**, meaning the learner's machine with Docker.
2. **cicd-net**, a user-defined bridge network created on the host.
3. Two **sibling** boxes side by side inside cicd-net. Neither box is inside the other:
   - **jenkins :8080**, the stock image `jenkins/jenkins:lts-jdk21`. Lines: "Pipeline controller", "SSH client + sshpass", "Password from Jenkins Credentials (devtools-ssh)", "No Docker CLI · no docker.sock".
   - **devtools :22**, a privileged container with its own Docker daemon (DinD). Lines: "Git clone workspace", "Docker CLI + daemon".
     - Nested inside devtools only: **catfood-web :3000**, the shop. Optionally a dashed **catfood-test-N**, a temporary test container.

Arrows:

- jenkins → devtools: "SSH devtools:22 (password, pinned host key)". This is the only control path.
- GitHub → devtools: "git clone" (Clone stage).
- devtools → Docker Hub: "Push image".
- Docker Hub → devtools: "Pull by digest". Draw this as a separate arrow, single-headed.
- Student browser → `host:8080` → jenkins.
- Student browser → `host:3000` → `devtools:3000` → catfood-web:3000.
- Optional: Student terminal → `host:2222` → `devtools:22`.

Must NOT appear:

- Jenkins inside devtools.
- A gateway or `devtools-gw`.
- SSH keys, ssh-agent, or authorized_keys.
- A Docker socket mount.
- catfood-web outside devtools.
- Any real username, token, or password value. `passwd` is fine only as "learner image default" if you mention it at all. Leave it out.

## 2. Pipeline (`LAB 3 | Pipeline`)

A portrait layout:

- Top box, outside the execution boundary: **Jenkins controls**, "Password from Jenkins Credentials".
- Down arrow: **SSH devtools:22**.
- Boundary box: **devtools executes**, containing eight stage cards in exact order, joined by down arrows:

1. Connect: Password SSH (validate parameters first)
2. Clone: GitHub to devtools
3. Build: Docker image
4. Test: Temporary container + health
5. Push: Docker Hub + save digest
6. Clean: Remove old LAB app and local image
7. Pull: Same digest from Docker Hub
8. Deploy: catfood-web on devtools + health

Keep two orange annotations: "Only after Push succeeds" between 5 and 6, and "Pull before Deploy" between 7 and 8.

Optional small side note: "failures before Clean keep the running shop".
