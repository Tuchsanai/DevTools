# LAB003 Docker Build Push — completion report (2026-09-27)

## Changes (working tree only — no commit, no push)
| file | change |
|---|---|
| `Jenkinsfile` | +2 lines in `environment`: a comment plus `APP_VERSION  = "${params.APP_VERSION}"` (fixes the first Build Now build) |
| `README.md` | 4.3 has the full Jenkinsfile in one fence plus Thai explanations; note that the corrected file is not on GitHub yet; image 10 → real v1.0.0 build #1 full page; step 5 → real console expectations, first-build bug box with the 2-line fix and build numbering, new image 11ก (real Stages view); step 6 → real Deployment info (image 12); new **step 7** with a full-page overview, the tour GIF, and a feature list |
| `images/` (new, 10) | `lab3_localfix_stages_builds_1_2.png`, `lab3_localfix_shop_v100_build1_full.png`, `lab3_localfix_shop_v110_build2_full.png`, `lab3_shop_tour_01_hero … 05_deployment.png`, `lab3_shop_tour.gif` |

All new images are real host Playwright screenshots uploaded by the parent. The GIF uses exactly those 5 tour PNGs in order: 5 frames, 1440×1000, 2000 ms each, loops forever (Pillow, median-cut 256 colours, no dither), 795 KB. No frames were invented and nothing was AI-generated. Old images that are still valid were kept: setup/navigation images, console image 11 (marked as an old image), and Docker Hub tags image 13 (marked as an old image; no new Hub screenshot exists).

## Test matrix (real Jenkins, isolated lab)
| job / build | Jenkinsfile source | trigger | result |
|---|---|---|---|
| docker-build-push #1 | GitHub `main` a8d0c0b (original) | Build Now | **FAILURE at Test**: `grep -F version:,build:1,` (empty `$APP_VERSION`) |
| docker-build-push #2 | GitHub a8d0c0b | params 1.0.0 | SUCCESS 6/6 |
| docker-build-push #3 | GitHub a8d0c0b | params 1.1.0 | SUCCESS 6/6 |
| docker-build-push-localfix #1 | local corrected file (sha256 fff6238f…) through a local Git SCM fixture | Build Now | SUCCESS 6/6 + Post, v1.0.0 build #1, pushed lab3-1 |
| docker-build-push-localfix #2 | same | params 1.1.0 | SUCCESS 6/6 + Post, v1.1.0 build #2, pushed lab3-2, deployed |

Browser checks (by the parent): the wet-food filter shows 1 product; adding the tuna product makes the cart 1 item / ฿329; "All" shows 6 products again; Deployment info shows 1.1.0 / #2.

## Verification
- README 4.3 fence vs `Jenkinsfile`: `cmp` byte-identical (fence + trailing newline), 155 lines (`fence_extract.txt`)
- README local links: 51 checked, 0 missing
- GIF: 5 frames, all 1440×1000, 2000 ms each, loop=0
- Secret scan of README, Jenkinsfile and `.task-run` text: no Docker token value; no Docker Hub username outside placeholders. The prior worker transcripts `worker*.jsonl` had 41 username occurrences, replaced in place with `<DOCKER_USER>`. `admin/admin2569` is the documented course default already in the committed README. `finalize.jsonl` is the parent's live stream of this session and was not edited.
- No temporary credential files were left in the workdir. Docker Hub auth dirs on devtools were removed by `post` after every build, and the whole container is now gone.

## Cleanup (`logs/final-cleanup.log`, `logs/old-lab-cleanup.log`)
- Removed: containers `devtools-l3e2e-406430-{jenkins,devtools}`, volume `-jhome`, network `-net`; the fixture git daemon was stopped and `/srv/fixture{,.git}` removed before the container was deleted. The old `devtools-l3nav-277caf-*` was removed earlier.
- Verified: no `l3e2e` or `l3nav` containers, volumes or networks remain; the unrelated `deep_vision_5090_vllm` is still Up (healthy).
- Still present on purpose: the upload receiver `127.0.0.1:8791` (pid in `upload_receiver.pid`), with new read-only `GET /artifact/<name>` limited to an exact allow-list of the 9 final images in `../images/`. Tests: returned files are byte-identical; `../README.md`, `%2e%2e/…`, non-listed images, empty name and trailing slash all give 404; PUT to `/artifact` gives 400. Stop it with `kill $(cat .task-run/upload_receiver.pid)` once the preview is done.
- Remote leftovers (not deleted, need the owner's decision): Docker Hub tags `catfood-shop:lab3-1`, `lab3-2` (localfix) and `lab3-3` (SCM #3).

## SCM limitation
GitHub `main` still has the original Jenkinsfile (a8d0c0b). The corrected file was tested only through a local Git SCM fixture; the shop source was still cloned from GitHub. Until the change is committed and pushed, students following step 5 hit the build #1 Test failure, and their build numbers shift by one (1.0.0 = #2, 1.1.0 = #3).
