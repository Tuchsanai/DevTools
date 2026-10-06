#!/usr/bin/env bash
# usage: x.sh <logname> [append] < script — รันสคริปต์ใน container ทดลอง (bash -l, set -v แสดงคำสั่ง) แล้วเก็บ log ที่ lab-run/<logname>.log
S=/root/workspace/DevTools/k/logs/014_helm/scratch
LR=/root/workspace/DevTools/k/logs/014_helm/lab-run
C=$(cat $S/cname)
f=$S/run-$1-$(date +%H%M%S).sh
{ echo 'set -v'; cat; } > $f
docker cp -q $f $C:/root/run.sh
mode=">"; [ "${2:-}" = append ] && mode=">>"
{
  echo "##### [$(date '+%F %T')] $1 — container $C"
  t0=$(date +%s)
  docker exec $C bash -l /root/run.sh 2>&1
  echo "##### [$(date '+%F %T')] จบ $1 ใช้เวลา $(( $(date +%s)-t0 )) วินาที"
} | if [ "${2:-}" = append ]; then tee -a $LR/$1.log; else tee $LR/$1.log; fi
