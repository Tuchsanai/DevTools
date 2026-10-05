#!/usr/bin/env bash
# ใช้: r.sh <labNN> '<คำสั่งแบบนักศึกษาพิมพ์>'  — รันใน container จาก 02_LAB แล้วต่อท้าย log
C=$(cat /root/workspace/DevTools/k/logs/007_deployment/scratch/container-name)
LOG=/root/workspace/DevTools/k/logs/007_deployment/lab-run/$1.log; shift
{ echo "### $(date -u +%H:%M:%S)"; echo "\$ $*"; } >> "$LOG"
docker exec $C bash -lc "cd /workspace/007_kubernetes_deployment/02_LAB 2>/dev/null || cd /workspace; $*" 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}; echo "[exit $rc]" >> "$LOG"; echo >> "$LOG"; return $rc 2>/dev/null || exit $rc
