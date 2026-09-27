# Ownership ledger (owner: worker3 of this task, LAB003)
| resource | kind | created by this task | status |
|---|---|---|---|
| devtools-l3nav-277caf-jenkins / -jhome / -net | old LAB003 nav Jenkins | no (prior LAB003 task) | REMOVED 2026-09-27T21:40Z (logs/old-lab-cleanup.log) |
| upload_receiver.py pid file upload_receiver.pid, 127.0.0.1:8791 | process in agent container | yes | running (restarted with /artifact allow-list; kill after the parent previews) |
| devtools-l3e2e-406430-net | docker network | yes | REMOVED 2026-09-27T22:02:25Z |
| devtools-l3e2e-406430-jhome | docker volume | yes | REMOVED 2026-09-27T22:02:25Z |
| devtools-l3e2e-406430-devtools | container devtools:2569_1 (b3e0784f66b7) | yes | REMOVED 2026-09-27T22:02:25Z |
| devtools-l3e2e-406430-jenkins | container jenkins/jenkins:lts-jdk21 (66ebfe0c8828) | yes | REMOVED 2026-09-27T22:02:25Z |
| Docker Hub <DOCKER_USER>/catfood-shop:lab3-1, lab3-2, lab3-3 | remote tags (pushed by Jenkins) | yes | present (see logs/dockerhub_tags_final.txt) |
| Jenkins jobs docker-build-push (SCM GitHub) + docker-build-push-localfix (fixture SCM) | in jhome volume | yes | REMOVED with volume |
| /srv/fixture{,.git} + git daemon :9418 | inside isolated devtools container | yes | daemon stopped, repos deleted, container REMOVED |
| README images/ lab3_localfix_* , lab3_shop_tour_* , lab3_shop_tour.gif (10 files) | repo files | yes | present (uncommitted) |
| deep_vision_5090_vllm | unrelated container | no | untouched, Up |
