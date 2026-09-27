# LAB003 README-only draft — remove manual SSH prep (2026-09-27)

Scope: `README.md` only. No Jenkinsfile change, no plugin install/test, no build/deploy/push/mail, no container/volume/network changes. Full diff: `readme-only.diff` (15 insertions, 85 deletions; 1181 → 1111 lines).

## Exact changes
1. **Top draft note** (after title): README review draft; manual SSH prep removed; target = Jenkins Username-with-password Credentials only; current `Jenkinsfile` still uses `sshpass`; code/screenshots/test results are of the current version; plugin migration not done/not tested, next pass.
2. **Overview** `jenkins` bullet: removed "(เพิ่มแค่ `sshpass`)".
3. **Step 1** heading → "สร้าง network และ container สองตัว (🖥️ host)"; intro now says only 1.1, no manual SSH setup in `jenkins`.
4. **Removed entirely:** 1.2 install `sshpass`, 1.3 pin host key, 1.4 optional manual SSH test (incl. `lab3-test:sshpass`, `pin-hostkey`, `ssh-test` blocks). 1.1 unchanged (container/volume/network commands preserved).
5. Transition paragraph after 1.1 rewritten: Connect uses `devtools-ssh` credential only; added 🚧 "planned, not done" note describing a Jenkins SSH plugin in beginner terms, and stating the draft cannot run end-to-end yet.
6. **4.7**: removed "(1.2–1.3)" reference; flagged code as current `Jenkinsfile` (still `sshpass` + pinned host key). Bullet "pin ในข้อ 1.3" reworded as current-code behaviour.
7. **Full Jenkinsfile `<details>`**: added note that it is the current file; its "ขั้นที่ 1" comments refer to removed prep. Code itself untouched.
8. **Step 5** Connect screenshot sentence: marked as output of current `sshpass` Jenkinsfile.
9. **Troubleshooting**: `sshpass: not found` and `Host key verification failed.` rows no longer point to 1.2/1.3; explain draft state/next pass.
10. **Review question 2** (host-key pinning) replaced with a Credentials question. Q3 (`sshpass -e`) kept — it describes existing code; revisit after migration.

## Checks
- No remaining references to 1.2/1.3/1.4 (only `1.2.0` version strings remain).
- Code fences balanced (48); no figures/images removed; figure numbering unchanged.

## Caveat
The current `Jenkinsfile` still depends on `sshpass` and a pinned `known_hosts`, whose setup steps are now gone from the README. Following this draft as-is, stage Connect will fail. Migration to Jenkins-native SSH (plugin) is NOT implemented or tested; code samples, Step 5–7 screenshots/outputs and LAB003_FINAL_REPORT reflect the old `sshpass` flow.
