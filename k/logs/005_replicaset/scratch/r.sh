#!/bin/bash
# ใช้: r.sh <log> '<คำสั่ง>'  → รันใน container ทดลองที่ 02_LAB แล้วบันทึกคำสั่ง+output ลง lab-run/<log>.log
C=$(cat /root/workspace/DevTools/k/logs/005_replicaset/scratch/container-name)
L=/root/workspace/DevTools/k/logs/005_replicaset/lab-run/$1.log
shift
{ echo "### $(date '+%H:%M:%S')"; echo "\$ $*"; } >> $L
docker exec $C bash -c "cd /workspace/005_kubernetes_replicaset/02_LAB; $*" 2>&1 | tee -a $L
echo >> $L
