# LAB 3 prose rewrite report (2026-09-26)

Scope: prose-only rewrite of LAB 3 Thai explanations. No Docker lab rerun, no command/Jenkinsfile/app/image/credential changes.

## Files edited

| File | Change |
|---|---|
| `README.tmpl.md` | Rewrote all prose: new "ภาพรวม" section explains the model first (two containers = two servers on `cicd-net`; Jenkins controls, devtools runs every `git clone`/Docker command; Docker Hub stores images; `catfood-web` runs in devtools' nested Docker, never Jenkins), then technical details. Removed พี่น้อง/sibling/ผู้สั่ง/ผู้ทำ shorthand, shortened sentences, split the step 4 explanation into a line-by-line list. Kept every instruction, expected result, host/Jenkins/devtools location, the troubleshooting table, credential security warnings, checklist and review questions. |
| `captures.json` | Tightened 8 screenshot captions (`caption` text only; `key`/`src`/`box`/`alt` unchanged). |
| `scripts/build_readme.py` | Reworded 3 captions in `FIG` (two diagrams, Docker Hub PAT); removed "พี่น้อง". No logic changes. |
| `../../003_LAB_Docker_Build_Push/README.md` | Regenerated with `scripts/build_readme.py` (736 → 752 lines, 27 figures). |

Baseline copies and hashes: `prose-baseline/` (`files.sha256`, `images.sha256`, `codeblocks.sha256`, `*.before.*`).

## Checks

- `scripts/verify_readme.py`: exit 0, 80/80 OK (blocks identical + `bash -n`, Jenkinsfile identical, links, images, figure numbering, secret scan, no trailing whitespace).
- Build reproducibility before editing: regenerating from the old template gave the same README hash as the committed one (`8c0afc39…`).
- Code-block parity: all 20 fenced blocks (bash, groovy snippet, full Jenkinsfile, text outputs) have the same SHA-256 hashes, in the same order, as the baseline.
- `<!-- lab3-test:* -->` markers: identical.
- Images: 52 files in `images/` match `images.sha256`. 52 image refs in the same order, and all 27 `ภาพที่ N` numbers still point to the same images.
- Non-image links unchanged: LAB 1 README, `./Jenkinsfile`, `./LAB003_FINAL_REPORT.md`, LAB 4 README.
- Remaining "sibling"/"ผู้สั่ง"/"พี่น้อง" matches in the README only occur in image filenames, the embedded Jenkinsfile comments (byte-for-byte rule) and real run tags in the output logs (`lab3-sibling-…`).

## Pending

- Docker Hub **Generate-result screenshot** is still a separate, pending task. It was not created or faked here, and the README does not reference it.
- Not done by design: no git add/commit/push (the auto-commit service handles this).

## Final editorial pass (2026-09-26)

Template only (`README.tmpl.md`); `captures.json`, `scripts/*`, Jenkinsfile, app and images untouched in this pass. README regenerated (755 lines, 27 figures).

- **Execution-location fix:** removed "ทุกคำสั่ง docker ในแล็บนี้พิมพ์ที่ host". Section 0 now says commands marked 🖥️ host are learner setup commands, while the Pipeline's application Git/Docker commands are sent by Jenkins over SSH and run inside `devtools`. No all-Docker-on-host statement remains (grep of the README for `ทุกคำสั่ง docker` / `พิมพ์ที่ host`: no matches).
- **Intro:** "two servers" is now followed by exactly two bullets (`jenkins`, `devtools`). Docker Hub (image storage) and where `catfood-web` runs are covered in one short paragraph after them.
- **Shorter prose, technical details moved out of the intro:**
  - Removed the "รายละเอียดทางเทคนิค" list from the overview.
  - Name resolution on `cicd-net` → step 1.
  - `passwd` as the image default → step 6.
  - Clean-after-Push, downtime and no-rollback → one line under the step 7 stage table.
  - `sshpass -e`/`SSHPASS`, the `sh '...'` constant string, host-key enforcement, regex parameter check, token via stdin, digest reuse, `lab3` label, `post`, `disableConcurrentBuilds()` → a new collapsible block in step 7, "Jenkins ส่งคำสั่งไป devtools อย่างไร", which also holds the groovy snippet (same position in the code-block order).
  - Step 4 line-by-line list → one flow line.
  - Also shortened: the step 3 root note, step 4 caveat, step 9(ก) parenthetical, cleanup note.
- **Kept:** security warnings (root/privileged, token handling, shared host key "ไม่ใช่ตัวตนเฉพาะเครื่อง"), 🖥️ host labels, every ✅ expected result, troubleshooting table, checklist, review questions.
- **Length (template, excluding code blocks/placeholders/images):** 13,060 → 12,493 chars (−4.3%), 1,693 → 1,648 words. Generated README prose: 18,032 → 17,415 chars. Figure captions were not changed in this pass.

### Checks (final pass)

- `scripts/verify_readme.py`: exit 0, 80/80 OK. The first run failed one check (`host key shared across clones stated`) because the caveat had been shortened too far. The phrase was restored and the rerun passes.
- Against `prose-baseline/README.before.md`: 20/20 code blocks byte-identical and in the same order, matching `codeblocks.sha256`. The 31 image/link targets are identical and in the same order, the 27 `ภาพที่ N` → image mappings are identical, and the `lab3-test` markers are identical.
- `images/`: all files match `prose-baseline/images.sha256`.
- `003_LAB_Docker_Build_Push/Jenkinsfile`: no diff vs HEAD. The `catfood-shop/app/globals.css` modification was already there before this pass and was not touched.
- No Docker runtime, no git mutations, no token generation. The Docker Hub Generate-result screenshot is **still pending**.
