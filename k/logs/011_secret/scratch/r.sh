#!/usr/bin/env bash
# r.sh <log-name> <subdir-under-02_LAB> <cmd...>  — run like a student inside the test container, append to lab-run/<log>.log
C=$(cat /root/workspace/DevTools/k/logs/011_secret/scratch/C.txt)
LOG=/root/workspace/DevTools/k/logs/011_secret/lab-run/$1.log; D=$2; shift 2
CMD="$*"
{ echo; echo "# [$(date +%T)] (02_LAB/$D)"; echo "root@k8s-lab:/workspace/011_kubernetes_secret/02_LAB/$D# $CMD"; } >> "$LOG"
docker exec $C bash -lc "cd /workspace/011_kubernetes_secret/02_LAB/$D && $CMD" 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}; echo "[rc=$rc]" >> "$LOG"; exit $rc
