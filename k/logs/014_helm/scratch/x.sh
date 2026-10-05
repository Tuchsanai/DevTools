#!/usr/bin/env bash
# usage: x.sh <name> < script  — copy script into the test container and run it with bash -l
C=$(cat /root/workspace/DevTools/k/logs/014_helm/scratch/cname)
f=/root/workspace/DevTools/k/logs/014_helm/scratch/run-$1.sh
cat > $f
docker cp -q $f $C:/workspace/run-$1.sh
docker exec $C bash -l /workspace/run-$1.sh 2>&1
