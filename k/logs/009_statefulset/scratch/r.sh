#!/usr/bin/env bash
# ใช้: r.sh <labNN> <subdir ใต้ 02_LAB หรือ .> <<'X' ...คำสั่ง... X
C=$(cat /root/workspace/DevTools/k/logs/009_statefulset/scratch/cname)
LOG=/root/workspace/DevTools/k/logs/009_statefulset/lab-run/$1.log
DIR=$2
CMD=$(cat)
{ echo "### $(date -u +%T) (cd 02_LAB/$DIR)"; echo "$CMD" | sed 's/^/$ /'; } >> $LOG
printf 'cd /workspace/009_kubernetes_statefulset/02_LAB/%s\n%s\n' "$DIR" "$CMD" | docker exec -i $C bash 2>&1 | tee -a $LOG
echo >> $LOG
