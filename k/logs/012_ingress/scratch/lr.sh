#!/usr/bin/env bash
# lr.sh <log> : อ่านคำสั่งทีละบรรทัดจาก stdin รันใน container ทดลอง (bash เดียวต่อเนื่อง) พิมพ์ "$ cmd" + output ลง log
C=$(cat /root/workspace/DevTools/k/logs/012_ingress/scratch/cname-lab)
LOG=/root/workspace/DevTools/k/logs/012_ingress/lab-run/$1
gen() {
  echo 'cd ${LRDIR:-/workspace/012_kubernetes_ingress/02_LAB} 2>/dev/null; exec 2>&1'
  while IFS= read -r l; do
    [ -z "$l" ] && continue
    if [[ $l == '##'* ]]; then printf 'echo %q\n' "$l"; continue; fi
    printf 'echo %q\n' "\$ $l"
    printf '%s\n' "$l"
  done
  echo 'echo "[cwd: $(pwd)]" >/dev/null'
}
gen | docker exec -i "$C" bash -c "cat > /root/.lr.sh"
{ echo "===== $(date "+%F %T") ====="; docker exec -e LRDIR="${LRDIR:-}" "$C" bash -l /root/.lr.sh 2>&1 </dev/null; } | tee -a "$LOG"
