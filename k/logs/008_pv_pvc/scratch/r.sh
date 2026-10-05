#!/bin/bash
# ใช้: LOG=labNN.log D=<subdir ใต้ 02_LAB> r.sh 'คำสั่ง'  — รันใน container ทดลองแล้วเก็บคำสั่ง+output ลง lab-run/$LOG
C=$(cat /root/workspace/DevTools/k/logs/008_pv_pvc/scratch/container-name)
W=/workspace/008_kubernetes_pv_pvc/02_LAB/${D}
L=/root/workspace/DevTools/k/logs/008_pv_pvc/lab-run/${LOG:-misc.log}
{ echo "### $(date -u +%T) (cd 02_LAB/${D})"; echo "\$ $1"; timeout ${TO:-600} docker exec $C bash -c "cd $W && $1" 2>&1; echo; } | tee -a "$L"
