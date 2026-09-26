# LAB003 README screenshot readability pass (yolo3, 2026-09-26)

## Problem
The real captures are 3440×1249 / 3425×1244 ultra-wide browser screenshots. At GitHub's roughly 880 px README column they shrink to about 0.26×, so the Jenkins, Hub and GitHub text can't be read.

## Method: lossless crops of the genuine captures only
- `make_crops.py` makes pure `PIL.crop()` cuts from `host-captures/*.png`, which are byte-identical to the full-size copies in `003_LAB_Docker_Build_Push/images/`. There is no resize, no redraw and no text change. Every crop is re-opened and compared pixel-for-pixel with its source box, and the script asserts equality.
- `crop-manifest.json` records, for every crop, its source, source sha256, box (l,t,r,b), size, crop sha256 and the reason for the box.
- Boxes were chosen by viewing grid overlays (`inspect/grid-*.png`, used for inspection only and not referenced by the README) and by measuring the text rows and rightmost text pixel per row on the stage pages. Long console lines get an overlapping `_tail` crop, so no relevant text is lost.
- Widths are mostly 900–1400 px. Deliberate exceptions:
  - Modal and form crops are shown at their native size (`05` and `06` credential modals are 600 px, sign-in is 520 px, the chip is 600 px). These dialogs are that small on screen, and GitHub never upscales them, so they display 1:1 and remain readable.
  - The dashboard crop is 1540 px, to keep the Last Success column.
  - Graph strips are 1400×95.
- README: each crop is wrapped as `[![alt](crop)](full)`, so clicking opens the untouched full capture. Every affected caption now says `ภาพหน้าจอจริงแบบครอป — คลิกภาพเพื่อเปิดภาพเต็ม` and explains multi-part crops (graph/log/tail, left/right columns). The storefront figures 15 and 26 keep the full screenshot and add a chip crop under it.

## Figures changed (template numbering unchanged)
2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 16, 17, 18–25, 27, 28, 29, 30, 31 now use crops. Figures 15 and 26 show the full image plus a chip crop. **Figure 9 was replaced** (see below). Figures 1 and 4 are cyolo1 diagrams at 1672×941, which already fits a README column, so they were left untouched and not regenerated.

Caption accuracy fixes found while inspecting (content claims now match what the pixels show):
- Fig 8: "plugin กลุ่ม Pipeline" → "ส่วนต้นของหน้า Installed plugins (เรียงตามชื่อ)", because the capture shows the alphabetical A–C plugins.
- Fig 19: the Clone capture shows the commit line but not the file list, so the caption now points to the experiment-8 console for the file list.
- Fig 20: the Build capture has the ssh step collapsed and no `CACHED` lines, so the caption now points to the experiment-8 console.

## Figure 9 (Docker Hub PAT)
- Source: the host coordinator's real browser captures `readability/hub-pat-full.png` (3425×1244, sha256 4ed4e53c…) and `hub-pat-setup.png` (650×460, sha256 8057eeff…). Both hold JPEG data under a `.png` name and both are archived untouched here. `hub-pat-setup.png` is not a pixel-exact sub-region of `hub-pat-full.png` (best-match mean abs diff 6.5/255, probably a separate encode), so it was not used in the README.
- `images/lab3_hub_04_pat_setup.png` is the decoded pixels of `hub-pat-full.png` stored as a real PNG (verified identical). `images/lab3_hub_04_pat_setup_crop.png` (905×530) crops it to show the Account settings menu with *Personal access tokens* highlighted, plus the Create access token form (`jenkins-lab3`, Expiration None, **Repo Read & Write**, Generate).
- The capture was taken before Generate was pressed, so no token value appears in it.
- The old figure 9 file `images/lab3_hub_01_logged_in.png` (Repositories list) is no longer referenced. It was left in `images/` and in `host-captures/`; nothing was deleted.

## Scripts
- `edit_template.py`: a one-off, guarded template edit (crop links and caption disclosure). The figure-9, caption-accuracy and wording fixes were applied afterwards as small asserted replacements.
- `scripts/build_readme.py`: now asserts that every `./images/…` reference exists before writing README.md.
- `scripts/verify_readme.py`: additionally checks that each linked crop points to a full-size image whose name starts the crop's name, that each crop caption contains `ครอป`, and that no non-diagram screenshot is left unlinked.
- Pre-edit copies: `README.before-readability.md`, `README.tmpl.before-readability.md`, `build_readme.before-readability.py`, `verify_readme.before-readability.py`.

## Verification (run after final regeneration)
- `python3 scripts/build_readme.py` → README.md, 1361 lines.
- `python3 scripts/verify_readme.py` → exit 0: all 11 `lab3-test` blocks OK, Jenkinsfile OK, launch/setup exact, 41 linked crops, bad [], unlinked [].
- `bash -n blocks/*.sh` → all pass. Fence lines: 90 (unchanged).
- `git diff --check` on README.md, README.tmpl.md and scripts/ → clean.
- A diff of README.md against the pre-edit copy changes only image lines, figure captions and the `images/` table row. Every tested shell block and the embedded Jenkinsfile are unchanged.
- Untouched: the Jenkinsfile, all full-size images, host-captures, blocks, out3 (the pre-existing `out3/exp4-test.txt` modification is not from this pass), globals.css and `.ipynb_checkpoints`.
- The pipeline and experiments were not rerun. No git commit or push, and no email.
